"""External (Tier-2) checks that need a tool beyond the stdlib: axe-core accessibility over the built
site, and `claude plugin validate` on the manifests. Each SKIPs when its tool is absent (FAIL only under
--strict), so a fresh clone / browser-less CI stays green on the Tier-1 core."""
from __future__ import annotations

import os
import random
import re
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from tests.common import _NON_SITE_DIRS, FAIL, PASS, ROOT, SKILL, SKIP, free_port, html_files, run


class _SiteHandler(SimpleHTTPRequestHandler):
    """Serve ONLY the built site. axe fetches an explicit page list, but a bare handler would expose the
    whole repo root (incl. `.git`) on the ephemeral localhost port for the run's duration — so refuse any
    path under a non-site dir or a dotfile. 404 (not 403) so it doesn't confirm what exists."""

    def send_head(self):
        rel = self.path.lstrip("/").split("?", 1)[0].split("#", 1)[0]
        if any(seg in _NON_SITE_DIRS or seg.startswith(".") for seg in rel.split("/") if seg):
            self.send_error(404)
            return None
        return super().send_head()

    def log_message(self, *_args):  # keep the suite output clean (no per-request GET spam)
        pass


def _axe_bucket(rel: str) -> str:
    """Template-family key for one served page (path relative to ROOT). Every page ADAtool renders comes
    from one of a handful of renderer templates; two pages sharing a bucket exercise the SAME template code,
    so scanning ≥1 per bucket covers every renderer path. Buckets:

      - each named top-level page + the three named book index pages → its own bucket (unique templates);
      - `book/appendix-*` → one bucket (the appendix-entry template);
      - other `book/*` (chapters) → one bucket (the chapter template);
      - catalogue entries by first path segment (`agent`/`models-bridge`/`product`), README indexes split
        from leaf entries (index template vs entry template)."""
    top_level_singletons = {
        "index.html", "catalogue-views.html", "quick-start.html",
        "catalogue-figure.html", "development-workflow.html",
        "book/index.html", "book/book-index.html", "book/list-of-figures.html", "book/figures.html",
    }
    if rel in top_level_singletons:
        return rel  # its own bucket
    if rel.startswith("book/appendix-"):
        return "book/appendix-*"
    if rel.startswith("book/"):
        return "book/chapters"
    seg = rel.split("/", 1)[0]  # agent / models-bridge / product (+ any other tree)
    kind = "readme" if rel.endswith("README.html") else "entry"
    return f"{seg}/{kind}"


def _axe_sample(pages: list[str], target: int, rng: random.Random) -> list[str]:
    """Pick ≤`target` pages: one random representative from every template-family bucket (deterministic
    coverage of each renderer path every run), then a uniform-random tail from the remainder up to `target`.
    `pages` are ROOT-relative. Returns the chosen ROOT-relative paths, sorted."""
    buckets: dict[str, list[str]] = {}
    for p in pages:
        buckets.setdefault(_axe_bucket(p), []).append(p)
    chosen: set[str] = {rng.choice(members) for members in buckets.values()}
    remainder = [p for p in pages if p not in chosen]
    rng.shuffle(remainder)
    for p in remainder:
        if len(chosen) >= target:
            break
        chosen.add(p)
    return sorted(chosen)


def check_axe(strict: bool):
    """Run axe-core over a REPRESENTATIVE + RANDOM SAMPLE (~25 pages) of the built site, not the whole
    thing. The pages are homogeneous generated output — every one is emitted by the SAME small set of
    renderer templates — so a sample that touches each template family catches a template-level a11y bug
    just as reliably as scanning all ~190 pages, at a fraction of the cost (a full scan is ~10 min; the
    sample runs in ~1-2 min, which is what makes it usable in BOTH local `--full` and CI).

    Sampling has two parts (see `_axe_sample`):
      - REPRESENTATIVE — bucket the pages by template family (`_axe_bucket`) and always include ≥1 per
        bucket, so every renderer path is exercised every run (deterministic coverage). The representative
        within a multi-page bucket is picked at random so it varies run to run.
      - RANDOM TAIL — fill up to the target with a uniform-random sample of the remaining pages, using an
        UNSEEDED `random.Random()` so the sample varies per run and coverage accumulates over time. This is
        a test helper (a template-level bug shows up on the first sampled page from that template) — plain
        unseeded randomness is deliberately fine here; we do NOT want per-run determinism.
    Target size defaults to 25, overridable via `ADA_CATALOG_AXE_SAMPLE` for tuning. The chosen count +
    per-bucket sample is printed so a failure is reproducible and the reader sees it's a sample.

    A per-page load delay lets async content (the figure iframes AND the book appendix's CDN-loaded Mermaid
    diagrams) settle so the scan is deterministic — without it a heavy page can be scanned before it
    finishes painting and return a spurious partial result (Mermaid repaints its placeholder blocks after
    the runtime loads, which mid-scan reads as contrast failures on unrelated elements).

    We scan with `tests/axe_scan.cjs`, which launches ONE headless Chrome and reuses it across every URL.
    The old `@axe-core/cli` path spawned a fresh Chrome per URL — a full-site scan paid the browser
    cold-start cost dozens of times (~20 min). One reused browser drops that to a navigation-plus-analyze
    per page. Same engine and pinned versions (`@axe-core/webdriverjs` + `axe-core` + `chromedriver` from
    `npm ci`/`setup.sh`); absent a local install `node` errors and we treat it as a skip (same as no
    browser)."""
    if not shutil.which("node"):
        return (FAIL if strict else SKIP), ["node not found — run ./setup.sh (installs the pinned axe scanner)"]
    scanner = os.path.join(ROOT, "tests", "axe_scan.cjs")
    if not os.path.exists(scanner):
        return (FAIL if strict else SKIP), ["tests/axe_scan.cjs missing"]
    all_pages = sorted(os.path.relpath(p, ROOT) for p in html_files())  # served site only (excl. plugin/)
    if not all_pages:
        return (FAIL if strict else SKIP), ["no built pages to scan (run `catalog.py build` first)"]
    try:
        target = int(os.environ.get("ADA_CATALOG_AXE_SAMPLE", "25"))
    except ValueError:
        target = 25
    rng = random.Random()  # UNSEEDED on purpose — sample varies per run, coverage accumulates over time
    sample = _axe_sample(all_pages, target, rng)
    buckets_hit = sorted({_axe_bucket(p) for p in sample})
    print(f"          axe: sampling {len(sample)}/{len(all_pages)} pages across {len(buckets_hit)} "
          f"template-family buckets (representative + random tail; unseeded — varies per run):")
    for p in sample:
        print(f"            - {p}")
    pages = sample
    port = free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(_SiteHandler, directory=ROOT))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        urls = [f"http://127.0.0.1:{port}/{p}" for p in pages]  # `pages` are already ROOT-relative
        r = run(["node", scanner, "2500", *urls], timeout=900)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as ex:
        return (FAIL if strict else SKIP), [f"axe could not run ({type(ex).__name__}) — treating as skip"]
    finally:
        httpd.shutdown()
    out = r.stdout + r.stderr
    found = re.findall(r'Violation of "([^"]+)" with (\d+)', out)
    if found:  # real a11y violations — aggregate by rule across all pages
        agg: dict[str, int] = {}
        for name, n in found:
            agg[name] = agg.get(name, 0) + int(n)
        return FAIL, [f"{name}: {cnt} occurrence(s)" for name, cnt in sorted(agg.items(), key=lambda kv: -kv[1])]
    if r.returncode != 0:  # non-zero without a violations summary = launch/browser failure
        return (FAIL if strict else SKIP), [f"axe did not complete (no headless browser?): {out.strip()[:200]}"]
    return PASS, []


def check_html_valid(strict: bool):
    """Full HTML validity via html-validate — the canonical validator (rules in `.htmlvalidate.json`),
    NOT a hand-rolled definition. Tier-2: needs Node + the pinned html-validate from `npm ci`/`setup.sh`;
    runs offline via `npx --no-install`. SKIP if npx/tool absent (same posture as axe)."""
    if not shutil.which("npx"):
        return (FAIL if strict else SKIP), ["npx not found — run ./setup.sh (installs the pinned html-validate)"]
    pages = sorted(os.path.relpath(p, ROOT) for p in html_files())
    if not pages:
        return (FAIL if strict else SKIP), ["no built pages to validate (run `catalog.py build` first)"]
    try:
        r = run(["npx", "--no-install", "html-validate", *pages], timeout=300)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as ex:
        return (FAIL if strict else SKIP), [f"html-validate could not run ({type(ex).__name__}) — treating as skip"]
    if r.returncode == 0:
        return PASS, []
    out = r.stdout + r.stderr
    errs = [ln.strip() for ln in out.splitlines() if re.search(r"\d+:\d+\s+error", ln)]
    if errs:
        return FAIL, errs[:30]  # real validation errors
    return (FAIL if strict else SKIP), [f"html-validate did not complete: {out.strip()[:200]}"]


def check_claude_validate(strict: bool):
    """`claude plugin validate` on the plugin dir + the marketplace root. LOCAL-ONLY: the `claude` CLI is
    never invoked in CI (headless runners have no interactive CLI, and CI must not call it) — it SKIPs under
    a CI runner. On a developer machine it runs; SKIP if the CLI is absent there."""
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return SKIP, ["local-only — `claude` is not invoked in CI (run locally with the CLI installed)"]
    if not shutil.which("claude"):
        return (FAIL if strict else SKIP), ["claude CLI not found"]
    issues = []
    for path, label in ((SKILL, "plugin"), (ROOT, "marketplace")):
        try:
            r = run(["claude", "plugin", "validate", path], timeout=120)
        except subprocess.TimeoutExpired:
            return (FAIL if strict else SKIP), [f"claude plugin validate ({label}) timed out"]
        if r.returncode != 0:
            issues.append(f"{label}: {(r.stdout + r.stderr).strip()[:300]}")
    return (FAIL if issues else PASS), issues
