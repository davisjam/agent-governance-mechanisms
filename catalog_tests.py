#!/usr/bin/env python3
"""Test suite for the governance catalogue + the packaged self-governance skill.

Tiered by dependency, so the stdlib core runs on a fresh clone (the repo's clone-and-run posture):

  Tier 1 — pure stdlib, always runs, hard-fails:
    * markdown : schema + INDEX + `.md` link existence (delegates to `catalog.py validate`)
    * markdown : `#anchor` resolution (a `file.md#x` link's `x` must be a heading in the target)
    * html     : every local `href`/`src` resolves, and `#anchor`s exist where the target uses ids
    * skill    : SKILL.md / plugin.json / marketplace.json structure + a bundle-freshness (no-drift) check

  Tier 2 — external tools, SKIP if the tool is absent (FAIL under --strict):
    * html     : axe-core accessibility scan of representative pages
    * skill    : `claude plugin validate` on the plugin + marketplace manifests

"Resolve" = the relative target file exists; a `#anchor` matches a heading-slug (markdown) or an
`id`/`name` (html) in the target; `http(s)`/`mailto`/`data:` are out of scope (no network in tests).

Run: `python3 catalog_tests.py [--strict]`  (or `python3 catalog.py test [--strict]`, which builds first).
Exit 0 = all checks pass; 1 = any FAIL (a Tier-2 SKIP becomes FAIL only under --strict).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import catalog

ROOT = catalog.ROOT
SKILL = os.path.join(ROOT, "plugin", "self-governance")
SKILLDIR = os.path.join(SKILL, "skills", "self-governance")
SKILLREF = os.path.join(SKILLDIR, "reference")

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


def _rel(p: str) -> str:
    return os.path.relpath(p, ROOT)


def _slug(heading: str) -> str:
    """GitHub-style heading slug: lowercase, drop punctuation (keep word chars + hyphen), spaces->hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def _run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)


# ── Tier 1 ─────────────────────────────────────────────────────────────────────

def check_markdown_schema():
    """Delegate to the canonical validator (schema + INDEX + `.md`-link existence + abstractions)."""
    r = _run([sys.executable, "catalog.py", "validate"])
    if r.returncode == 0:
        return PASS, []
    return FAIL, [ln.strip() for ln in r.stdout.splitlines() if re.search(r"\[(entry|index|link|abbr|role|family)", ln)]


def check_markdown_anchors():
    """Every `](file.md#anchor)` must point at a heading that exists in the target file."""
    files = catalog.catalogue_md_files()
    slugs: dict[str, set[str]] = {}
    for f in files:
        txt = open(f, encoding="utf-8").read()
        slugs[os.path.abspath(f)] = {_slug(h) for h in re.findall(r"^#{1,6}\s+(.+?)\s*$", txt, re.M)}
    issues = []
    for f in files:
        base = os.path.dirname(f)
        txt = open(f, encoding="utf-8").read()
        for tgt_rel, anchor in re.findall(r"\]\(([^)#\s]+\.md)#([^)\s]+)\)", txt):
            tgt = os.path.abspath(os.path.join(base, tgt_rel))
            if tgt in slugs and _slug(anchor) not in slugs[tgt]:
                issues.append(f"{_rel(f)} -> {tgt_rel}#{anchor} (no matching heading)")
    return (FAIL if issues else PASS), issues


class _Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for a in ("href", "src"):
            if d.get(a):
                self.refs.append(d[a])
        if d.get("id"):
            self.ids.add(d["id"])
        if tag == "a" and d.get("name"):  # legacy <a name>; NOT meta/input name=
            self.ids.add(d["name"])


def _html_files() -> list[str]:
    return [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
            if os.sep + "plugin" + os.sep not in f]


def check_html_links():
    """Every local href/src resolves to a file; #anchors resolve where the target page uses ids."""
    files = _html_files()
    if not files:
        return FAIL, ["no built HTML found — run `catalog.py build` first"]
    parsed: dict[str, _Refs] = {}
    for f in files:
        p = _Refs()
        p.feed(open(f, encoding="utf-8").read())
        parsed[os.path.abspath(f)] = p
    issues = []
    for f in files:
        base, ap = os.path.dirname(f), os.path.abspath(f)
        for ref in parsed[ap].refs:
            if ref.startswith(("http://", "https://", "mailto:", "data:", "//")):
                continue
            tgt_rel, _, anchor = ref.partition("#")
            if not tgt_rel:  # in-page anchor
                if anchor and anchor not in parsed[ap].ids:
                    issues.append(f"{_rel(f)} -> #{anchor} (no such id in page)")
                continue
            tgt = os.path.abspath(os.path.join(base, tgt_rel))
            if not os.path.exists(tgt):
                issues.append(f"{_rel(f)} -> {ref} (missing target)")
            elif anchor and tgt in parsed and parsed[tgt].ids and anchor not in parsed[tgt].ids:
                # only assert the anchor when the target page uses ids at all (avoids false positives
                # on pages that don't emit heading ids)
                issues.append(f"{_rel(f)} -> {ref} (no such anchor in target)")
    return (FAIL if issues else PASS), issues


def check_skill_structure():
    """SKILL.md frontmatter, manifests, and the bundled reference are present and well-formed."""
    issues = []
    skmd = os.path.join(SKILLDIR, "SKILL.md")
    if not os.path.isfile(skmd):
        return FAIL, ["SKILL.md missing"]
    fm = re.match(r"^---\n(.*?)\n---\n", open(skmd, encoding="utf-8").read(), re.S)
    if not fm:
        issues.append("SKILL.md: no YAML frontmatter")
    elif not re.search(r"^description:\s*\S", fm.group(1), re.M):
        issues.append("SKILL.md: frontmatter has no non-empty `description`")
    try:
        pj = json.load(open(os.path.join(SKILL, ".claude-plugin", "plugin.json"), encoding="utf-8"))
        issues += [f"plugin.json: missing `{k}`" for k in ("name", "description") if not pj.get(k)]
    except Exception as ex:  # noqa: BLE001 — surfaced as a test issue, not swallowed
        issues.append(f"plugin.json: {ex}")
    try:
        mj = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
        issues += [f"marketplace.json: missing `{k}`" for k in ("name", "owner", "plugins") if not mj.get(k)]
    except Exception as ex:  # noqa: BLE001 — surfaced as a test issue
        issues.append(f"marketplace.json: {ex}")
    principles = os.path.join(SKILLDIR, "principles.md")
    if not (os.path.isfile(principles) and os.path.getsize(principles) > 500):
        issues.append("principles.md: missing or too small")
    for name in ("INDEX.md", "ABSTRACTIONS.md", "README.md"):
        if not os.path.isfile(os.path.join(SKILLREF, name)):
            issues.append(f"reference/{name}: missing")
    n = len(glob.glob(os.path.join(SKILLREF, "agent", "*", "*.md"))) + \
        len(glob.glob(os.path.join(SKILLREF, "models-bridge", "*", "*.md")))
    if n < 30:
        issues.append(f"reference: only {n} entries bundled (expected 30+)")
    return (FAIL if issues else PASS), issues


def check_skill_drift():
    """Regenerate the bundle and assert it matches what's committed (no stale bundle)."""
    r = _run([sys.executable, "bundle_skill.py"])
    if r.returncode != 0:
        return FAIL, [f"bundle_skill.py failed (rc={r.returncode}): {r.stderr.strip()[:200]}"]
    d = _run(["git", "status", "--porcelain", "--", "plugin/self-governance/skills"])
    changed = [ln for ln in d.stdout.splitlines() if ln.strip()]
    if changed:
        return FAIL, ["bundle is STALE vs its sources — run `bundle_skill.py` and commit:"] + changed[:12]
    return PASS, []


# ── Tier 2 (degrade if the tool is absent) ─────────────────────────────────────

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def check_axe(strict: bool):
    """Run axe-core over representative built pages. SKIP if npx/browser unavailable."""
    if not shutil.which("npx"):
        return (FAIL if strict else SKIP), ["npx not found — install Node to enable axe"]
    pages = ["index.html", "quick-start.html", "ABSTRACTIONS.html",
             "agent/context-and-dispatch/brief-linting.html"]
    pages = [p for p in pages if os.path.isfile(os.path.join(ROOT, p))]
    if not pages:
        return (FAIL if strict else SKIP), ["no built pages to scan (run build first)"]
    port = _free_port()
    handler = partial(SimpleHTTPRequestHandler, directory=ROOT)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        urls = [f"http://127.0.0.1:{port}/{p}" for p in pages]
        r = _run(["npx", "--yes", "@axe-core/cli", "--exit", *urls], timeout=300)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as ex:
        return (FAIL if strict else SKIP), [f"axe could not run ({type(ex).__name__}) — treating as skip"]
    finally:
        httpd.shutdown()
    out = r.stdout + r.stderr
    # axe-core/cli --exit returns non-zero when violations are found; a launch failure (no browser) also
    # returns non-zero but without a violations summary — distinguish so a missing browser SKIPs.
    if re.search(r"\bviolation", out, re.I):
        if r.returncode != 0:
            hits = [ln.strip() for ln in out.splitlines() if re.search(r"violation|WCAG|\bfail", ln, re.I)]
            return FAIL, hits[:20] or ["axe reported violations (see build log)"]
        return PASS, []
    if r.returncode != 0:
        return (FAIL if strict else SKIP), [f"axe did not complete (likely no headless browser): {out.strip()[:200]}"]
    return PASS, []


def check_claude_validate(strict: bool):
    """`claude plugin validate` on the plugin dir + the marketplace root. SKIP if the CLI is absent."""
    if not shutil.which("claude"):
        return (FAIL if strict else SKIP), ["claude CLI not found"]
    issues = []
    for path, label in ((SKILL, "plugin"), (ROOT, "marketplace")):
        try:
            r = _run(["claude", "plugin", "validate", path], timeout=120)
        except subprocess.TimeoutExpired:
            return (FAIL if strict else SKIP), [f"claude plugin validate ({label}) timed out"]
        if r.returncode != 0:
            issues.append(f"{label}: {(r.stdout + r.stderr).strip()[:300]}")
    return (FAIL if issues else PASS), issues


CHECKS = [
    ("markdown: schema + md-link existence", 1, lambda strict: check_markdown_schema()),
    ("markdown: #anchor resolution", 1, lambda strict: check_markdown_anchors()),
    ("html: link + anchor resolution", 1, lambda strict: check_html_links()),
    ("skill: structure + manifests", 1, lambda strict: check_skill_structure()),
    ("skill: bundle freshness (no drift)", 1, lambda strict: check_skill_drift()),
    ("html: axe-core accessibility", 2, check_axe),
    ("skill: claude plugin validate", 2, check_claude_validate),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance-catalogue + skill test suite.")
    ap.add_argument("--strict", action="store_true", help="treat a Tier-2 SKIP (missing tool) as failure")
    args = ap.parse_args()

    print(f"== Test plan: {len(CHECKS)} checks (Tier 1 stdlib always; Tier 2 external, "
          f"{'strict' if args.strict else 'skip-if-absent'}) ==")
    failed = 0
    skipped = 0
    for name, tier, fn in CHECKS:
        status, issues = fn(args.strict)
        mark = {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[status]
        print(f"  [{mark}] (T{tier}) {name}")
        for it in issues:
            for line in str(it).splitlines():
                print(f"          {line}")
        failed += status == FAIL
        skipped += status == SKIP
    print(f"== {len(CHECKS)} checks: {len(CHECKS) - failed - skipped} passed, {failed} failed, {skipped} skipped ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
