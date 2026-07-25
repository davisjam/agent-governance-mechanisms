"""HTML checks over the built site: link and in-page anchor resolution (stdlib `html.parser`, no browser).
Full HTML validity is NOT hand-rolled here — it's delegated to the canonical `html-validate` (Tier-2,
`tests/external.py`), configured by `.htmlvalidate.json`."""
from __future__ import annotations

import os
from html.parser import HTMLParser

from tests.common import FAIL, PASS, html_files, rel


class _Refs(HTMLParser):
    """Collects local href/src references and the id/anchor targets a page defines."""

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


# Artifacts built by the Pages CI (gitignored locally, present on the deployed site) — a link to one
# is valid on the live site, but its target does not exist at check-time, so don't flag it as missing.
_CI_BUILT_ARTIFACTS = ("mage-book.pdf",)


def check_html_links():
    """Every local href/src resolves to a file; #anchors resolve where the target page uses ids."""
    files = html_files()
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
            if tgt_rel and os.path.basename(tgt_rel) in _CI_BUILT_ARTIFACTS:
                continue  # CI-built download artifact — present on the deployed site, not on disk here
            if not tgt_rel:  # in-page anchor
                if anchor and anchor not in parsed[ap].ids:
                    issues.append(f"{rel(f)} -> #{anchor} (no such id in page)")
                continue
            tgt = os.path.abspath(os.path.join(base, tgt_rel))
            if not os.path.exists(tgt):
                issues.append(f"{rel(f)} -> {ref} (missing target)")
            elif anchor and tgt in parsed and parsed[tgt].ids and anchor not in parsed[tgt].ids:
                # only assert the anchor when the target page uses ids at all (avoids false positives
                # on pages that don't emit heading ids)
                issues.append(f"{rel(f)} -> {ref} (no such anchor in target)")
    return (FAIL if issues else PASS), issues


def check_book_html_tracking():
    """Every tracked book/*.html is a page the current build produces (no stale orphans), present and
    non-empty. Blocks the renumber-orphan class (a chapter renumber leaves the old-numbered HTML tracked
    with no source): the expected set is the build's OWN discovery — `_discover_chapters` +
    `build_appendix_chapters` — plus the two index pages and the hand-authored figure copy, so it can't
    drift from what the build writes."""
    import subprocess
    import sys as _sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    book_dir = os.path.join(root, "book")
    if book_dir not in _sys.path:
        _sys.path.insert(0, book_dir)
    import build_book_html as bb  # noqa: E402 — path set above; build's discovery is the source of truth
    chapters = bb._discover_chapters(bb._load_metrics())
    chapters = chapters + bb.build_appendix_chapters(next_part=max(c["part"] for c in chapters) + 1)
    real = {c["slug"] + ".html" for c in chapters}
    real |= {"index.html", "book-index.html", "catalogue-figure.html"}  # index pages + hand-authored figure
    tracked_paths = subprocess.run(
        ["git", "ls-files", "book/*.html"], cwd=root, capture_output=True, text=True
    ).stdout.split()
    tracked = {os.path.basename(p) for p in tracked_paths}
    issues = []
    for o in sorted(tracked - real):
        issues.append(f"book/{o}: tracked but the build does not produce it (stale orphan — git rm it)")
    for m in sorted(real - tracked):
        issues.append(f"book/{m}: a build output but not tracked (run `catalog.py build` and commit it)")
    for p in tracked_paths:
        ap = os.path.join(root, p)
        if not os.path.exists(ap):
            issues.append(f"{p}: tracked but missing on disk")
        elif os.path.getsize(ap) == 0:
            issues.append(f"{p}: tracked but empty")
    return (FAIL if issues else PASS), issues


class _IdCollector(HTMLParser):
    """Collects every element id (WITH repeats) so within-page duplicates can be found."""

    def __init__(self):
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v:
                self.ids.append(v)


def check_no_duplicate_ids():
    """No built HTML page repeats an element id. Duplicate ids break in-page anchors, getElementById, and
    accessibility, and fail html-validate's `no-dup-id`. The usual source is inlined SVGs (mermaid or
    hand-authored) that carry a fixed id, so two figures on one page collide. This is the stdlib (Tier-1)
    twin of that CI-only Tier-2 check: it catches a collision LOCALLY, keeping every figure's ids a clean
    unique namespace."""
    from collections import Counter
    files = html_files()
    if not files:
        return FAIL, ["no built HTML found — run `catalog.py build` first"]
    issues = []
    for f in files:
        c = _IdCollector()
        c.feed(open(f, encoding="utf-8").read())
        counts = Counter(c.ids)
        for dup in sorted(i for i, n in counts.items() if n > 1):
            issues.append(f"{rel(f)}: duplicate element id {dup!r} ({counts[dup]}x)")
    return (FAIL if issues else PASS), issues
