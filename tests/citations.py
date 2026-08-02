"""Citation-subsystem gates — the enforcement half of the bibliography design
(book/_design/bibliography-subsystem-260801.md §8-§9). Each gate pins one invariant (BIB-N) and reads the
build's OWN single sources of truth (the cite-marker regexes, references.bib, citations.json) so it cannot
drift from what the build parses/renders.

The gates:
  CITE-RESOLVE  (BIB-2, BLOCKING) — every `[cite: key]` resolves to a references.bib entry.
  CITE-FRESH    (BIB-6, BLOCKING) — citations.json is in sync with references.bib (stamp hash) and covers
                                    every key (no partial render).
  CITE-ORPHAN   (decision #4, AUDIT-ONLY) — a .bib entry nothing cites is a warning, never fatal.
  CITE-MIRROR   (BIB-4, BLOCKING) — in built HTML, each citation superscript links to a Works-Cited entry
                                    that exists, and a chapter's entries are numbered 1..K contiguously.
  CITE-SYMBOLOGY(BIB-7, BLOCKING) — citation markers render as digits, editorial notes as symbols; the
                                    two glyph sets are disjoint.
  SCHOLAR-META  (BIB-8, BLOCKING) — every chapter page's <head> carries the required highwire citation_*
                                    tags.
"""
from __future__ import annotations

import glob
import hashlib
import os
import re
import sys as _sys

from tests.common import FAIL, PASS, ROOT, rel

_BOOK = os.path.join(ROOT, "book")
if _BOOK not in _sys.path:
    _sys.path.insert(0, _BOOK)
import build_book_html as bb  # noqa: E402 — the build owns the cite-marker vocabulary + slug discovery
import render_citations as rc  # noqa: E402 — the renderer owns the BibTeX parse + freshness hash

_REFERENCES_BIB = os.path.join(_BOOK, "references.bib")
_CITATIONS_JSON = os.path.join(_BOOK, "data", "citations.json")
# The generated (non-chapter) book pages — excluded from the chapter-scoped Scholar-meta gate.
_GENERATED = {"index", "book-index", "catalogue-figure", "figures", "bibliography", "list-of-figures"}


def _all_book_md_files() -> list[str]:
    """Every book chapter-source markdown — front matter, the five parts, AND back matter. (The data-claims
    lint's helper globs only `part*`; citations also live in the preface, the conclusion, and 6.0, so this
    covers all seven chapter dirs.)"""
    out: list[str] = []
    for sub in ("frontmatter", "part1", "part2", "part3", "part4", "part5", "backmatter"):
        out += glob.glob(os.path.join(_BOOK, sub, "*.md"))
    return sorted(out)


def _bib_keys() -> set[str]:
    if not os.path.isfile(_REFERENCES_BIB):
        return set()
    text = open(_REFERENCES_BIB, encoding="utf-8").read()
    return {e["key"] for e in rc.parse_bib(text)}


def _built_chapter_pages() -> list[str]:
    """Every built book chapter/appendix HTML page (the pages that carry citation markers + Scholar meta) —
    the build's own slug discovery minus the generated index/figure/bibliography pages."""
    try:
        slugs = bb.expected_page_slugs() - _GENERATED
    except Exception:  # noqa: BLE001 — discovery needs the tree; a bare checkout returns nothing to scan
        return []
    return [os.path.join(_BOOK, f"{s}.html") for s in sorted(slugs)
            if os.path.isfile(os.path.join(_BOOK, f"{s}.html"))]


def check_cite_resolve():
    """BIB-2 (BLOCKING). Every `[cite: key]` across all chapter sources names a key present in
    references.bib. An unknown key fails the build loud (the pattern the `[data:]` / `{{token}}` resolvers
    use) — a rotted citation must stop the build, not ship a dead reference. (The build itself also fails
    loud at render time; this is the source-side backstop that also covers keys behind a not-yet-rendered
    surface.)"""
    keys = _bib_keys()
    if not keys:
        return PASS, ["no references.bib — nothing to resolve"]
    issues: list[str] = []
    for f in _all_book_md_files():
        text = open(f, encoding="utf-8").read()
        for k in bb.iter_cite_keys(text):
            if k not in keys:
                issues.append(f"{rel(f)}: [cite: {k}] names no entry in references.bib")
    return (FAIL if issues else PASS), issues


def check_cite_fresh():
    """BIB-6 (BLOCKING). citations.json is in sync with references.bib: its stored stamp hash equals a
    fresh sha256 of the .bib, AND every .bib key is present (no partial render). A mismatch means someone
    edited references.bib without re-running the renderer — fail with the regenerate instruction, mirroring
    the committed-HTML / mermaid-cache freshness discipline."""
    if not os.path.isfile(_REFERENCES_BIB):
        return PASS, ["no references.bib — nothing to check"]
    if not os.path.isfile(_CITATIONS_JSON):
        return FAIL, ["book/data/citations.json missing — run `python3 book/render_citations.py`"]
    import json
    bib_text = open(_REFERENCES_BIB, encoding="utf-8").read()
    fresh = hashlib.sha256(bib_text.encode("utf-8")).hexdigest()
    payload = json.load(open(_CITATIONS_JSON, encoding="utf-8"))
    stored = payload.get("_stamp", {}).get("bib_sha256")
    issues: list[str] = []
    if stored != fresh:
        issues.append(f"citations.json is STALE (stamp {str(stored)[:12]}… != references.bib "
                      f"{fresh[:12]}…) — run `python3 book/render_citations.py`")
    rendered = set(payload.get("citations", {}))
    missing = _bib_keys() - rendered
    for k in sorted(missing):
        issues.append(f"citations.json is missing rendered strings for {k!r} (partial render — re-run "
                      f"render_citations.py)")
    return (FAIL if issues else PASS), issues


def check_cite_orphans():
    """Decision #4 (AUDIT-ONLY). A references.bib entry that nothing cites is a warning, not a failure — a
    bibliography may legitimately carry a work only its end-of-book list references. Reports the uncited
    keys so an author can prune a tight bib or ignore the note."""
    keys = _bib_keys()
    if not keys:
        return PASS, []
    cited: set[str] = set()
    for f in _all_book_md_files():
        cited.update(bb.iter_cite_keys(open(f, encoding="utf-8").read()))
    orphans = sorted(keys - cited)
    return (FAIL if orphans else PASS), [f"WARN {k!r} is in references.bib but nothing cites [cite: {k}]"
                                         for k in orphans]


_CITE_SUP_RE = re.compile(r'<sup class="cite-ref"><a href="#(wc-[a-z0-9-]+)"[^>]*>(\d+)</a></sup>')
_WC_ID_RE = re.compile(r'<li id="(wc-[a-z0-9-]+)">')
_NOTE_SUP_RE = re.compile(r'<sup class="note-ref"[^>]*>([^<]+)</sup>')


def check_cite_mirror():
    """BIB-4 (BLOCKING). In every built chapter page: each citation superscript links to a Works-Cited
    entry id that exists on the page, and the page's Works-Cited entries are numbered 1..K contiguously (so
    superscript N always addresses entry N). Walks the rendered HTML."""
    issues: list[str] = []
    for f in _built_chapter_pages():
        html = open(f, encoding="utf-8").read()
        entry_ids = set(_WC_ID_RE.findall(html))
        ns_nums: dict[str, set[int]] = {}
        for target, num in _CITE_SUP_RE.findall(html):
            if target not in entry_ids:
                issues.append(f"{rel(f)}: citation superscript → #{target} but no Works-Cited entry has that id")
            ns = target.rsplit("-", 1)[0]
            ns_nums.setdefault(ns, set())
            ns_nums[ns].add(int(target.rsplit("-", 1)[1]))
        # Contiguity: the entry ids present must be exactly 1..K for their namespace.
        by_ns: dict[str, set[int]] = {}
        for eid in entry_ids:
            ns, n = eid.rsplit("-", 1)
            by_ns.setdefault(ns, set()).add(int(n))
        for ns, nums in by_ns.items():
            if nums and nums != set(range(1, max(nums) + 1)):
                issues.append(f"{rel(f)}: Works-Cited entries for {ns} are not 1..K contiguous: {sorted(nums)}")
    return (FAIL if issues else PASS), issues


def check_cite_symbology():
    """BIB-7 (BLOCKING). Citation superscripts render as DIGITS; editorial-note superscripts render as
    SYMBOLS from the note glyph set (* † ‡ § ‖ ¶, possibly doubled). The two sets are disjoint — a reader
    can never confuse a citation for a note. Asserts it over the built HTML."""
    note_glyphs = set(bb._NOTE_GLYPHS)
    issues: list[str] = []
    for f in _built_chapter_pages():
        html = open(f, encoding="utf-8").read()
        for _target, num in _CITE_SUP_RE.findall(html):
            if not num.isdigit():
                issues.append(f"{rel(f)}: citation superscript {num!r} is not numeric")
        for glyph in _NOTE_SUP_RE.findall(html):
            if any(ch.isdigit() for ch in glyph) or not set(glyph) <= note_glyphs:
                issues.append(f"{rel(f)}: editorial-note superscript {glyph!r} is not a note glyph "
                              f"(must be from {''.join(bb._NOTE_GLYPHS)})")
    return (FAIL if issues else PASS), issues


_REQUIRED_META = ("citation_title", "citation_author", "citation_book_title",
                  "citation_publication_date", "citation_fulltext_html_url", "citation_pdf_url")


def check_scholar_meta():
    """BIB-8 (BLOCKING). Every built chapter page's <head> carries the required highwire_press citation_*
    tags, so Google Scholar can index the book and build its citation graph. Reads the page's <head> and
    asserts each required tag is present."""
    issues: list[str] = []
    for f in _built_chapter_pages():
        html = open(f, encoding="utf-8").read()
        head = html.split("</head>", 1)[0]
        names = set(re.findall(r'<meta name="(citation_[a-z_]+)"', head))
        for req in _REQUIRED_META:
            if req not in names:
                issues.append(f"{rel(f)}: <head> missing highwire meta {req!r}")
    return (FAIL if issues else PASS), issues
