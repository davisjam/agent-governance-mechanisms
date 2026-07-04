"""External (Tier-2) checks that need a tool beyond the stdlib: axe-core accessibility over the built
site, and `claude plugin validate` on the manifests. Each SKIPs when its tool is absent (FAIL only under
--strict), so a fresh clone / browser-less CI stays green on the Tier-1 core."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from tests.common import FAIL, PASS, ROOT, SKILL, SKIP, free_port, html_files, run


def check_axe(strict: bool):
    """Run axe-core over EVERY built page (the whole site, minus the plugin bundle). SKIP if
    npx/browser/the locally-installed axe are unavailable. `--load-delay` lets async content (the figure
    iframes) settle so the scan is deterministic — without it a heavy page can be scanned before it
    finishes loading and return a silent partial result.

    We invoke axe via `npx --no-install`, so it runs ONLY the version installed into `node_modules` by
    `npm ci`/`setup.sh` (pinned exactly by `package-lock.json`). It never fetches from the npm registry at
    run time — a `--yes` runtime fetch would pull an unpinned tree into a process that, in CI, shares the
    job. Absent a local install, `--no-install` errors and we treat it as a skip (same as no browser)."""
    if not shutil.which("npx"):
        return (FAIL if strict else SKIP), ["npx not found — run ./setup.sh (installs the pinned @axe-core/cli)"]
    pages = sorted(html_files())  # the served site only (excludes plugin/ + node_modules/)
    if not pages:
        return (FAIL if strict else SKIP), ["no built pages to scan (run `catalog.py build` first)"]
    port = free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(SimpleHTTPRequestHandler, directory=ROOT))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        urls = [f"http://127.0.0.1:{port}/{os.path.relpath(p, ROOT)}" for p in pages]
        r = run(["npx", "--no-install", "@axe-core/cli", "--exit", "--load-delay", "1000",
                 "--timeout", "120", *urls], timeout=900)
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


def check_claude_validate(strict: bool):
    """`claude plugin validate` on the plugin dir + the marketplace root. SKIP if the CLI is absent."""
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
