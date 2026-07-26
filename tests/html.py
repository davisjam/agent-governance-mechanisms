"""HTML checks over the built site: link and in-page anchor resolution (stdlib `html.parser`, no browser).
Full HTML validity is NOT hand-rolled here — it's delegated to the canonical `html-validate` (Tier-2,
`tests/external.py`), configured by `.htmlvalidate.json`."""
from __future__ import annotations

import os
import re
import sys as _sys
from html.parser import HTMLParser

from tests.common import FAIL, PASS, ROOT, html_files, rel


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


def _book_md_files() -> list[str]:
    """Every book chapter-source markdown file (book/part<N>/<N>.<M>-*.md). The `[data:]` markers and the
    `{#anchor}` heading ids live in the SOURCE markdown, not the rendered HTML, so the data-claims lint
    reads the source of truth directly."""
    import glob
    return sorted(glob.glob(os.path.join(ROOT, "book", "part*", "*.md")))


_NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
_NUM_SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000}


def _words_to_int(phrase: str) -> int | None:
    """Convert a spelled-out English cardinal ("fifty-eight", "five thousand") to an int, so the loose
    `holds` match treats "58"/"fifty-eight" as the SAME number (a spelling change is fine) while a real
    number change still fails. Returns None when the phrase is not a number phrase."""
    tokens = re.split(r"[\s-]+", phrase.strip().lower())
    if not tokens or not all(t in _NUM_WORDS or t in _NUM_SCALES for t in tokens):
        return None
    total = 0
    current = 0
    for t in tokens:
        if t in _NUM_WORDS:
            current += _NUM_WORDS[t]
        elif t == "hundred":
            current = (current or 1) * 100
        else:  # thousand / million / billion
            total += (current or 1) * _NUM_SCALES[t]
            current = 0
    return total + current


_DATA_MARKER_RE = re.compile(r"\[data:\s*([a-z0-9-]+)\s*\]")
_HEADING_ANCHOR_RE = re.compile(r"^#{1,6}\s+.*\{#([A-Za-z0-9_-]+)\}\s*$", re.M)
# A run of digits (with optional thousands separators / decimal) followed by an optional unit word — the
# LOOSE token the holds-still-present check compares on. "58 files" and "fifty-eight files" differ in
# spelling (fine), but "58 files" -> "40 files" differs in the digit run (a real number change → fail).
_NUM_UNIT_RE = re.compile(r"[-−+]?\d[\d,\.]*\s*%?\s*[A-Za-z]*")


def _norm_num_unit(s: str) -> str:
    """Normalize a `holds` string to its comparable core: digits + a trailing unit word, lowercased,
    thousands-separators and whitespace stripped, and the unicode minus folded to ASCII. So "5,000 lines"
    and "5000 lines" match, "-20%"/"−20%" match, but "58 files"/"40 files" do NOT."""
    s = s.strip().lower().replace("−", "-").replace(",", "")
    m = re.match(r"([-+]?\d[\d\.]*\s*%?)\s*([a-z]*)", s)
    if not m:
        return re.sub(r"\s+", "", s)
    num = re.sub(r"\s+", "", m.group(1))
    unit = m.group(2)
    return num + unit


def check_data_claims():
    """AUDIT-ONLY governed data-cross-reference lint, keyed off `book/data/data-claims.json` (the SSOT):
      (a) every `[data: <slug>]` marker in a book chapter resolves to a manifest entry;
      (b) each entry's `source` chapter file exists AND still contains a heading carrying `{#<anchor>}`;
      (c) each `holds` string still appears in the source chapter under a LOOSE digit+unit match (a
          number change fails; a digit->word spelling change does not);
      (d) a manifest entry that nothing cites is WARNed (wiring may be partial — not a hard fail).
    Modelled on the book's `{{token}}`->metrics.json fail-loud mechanism; the build already fails loud on an
    unknown slug, so (a) is a belt-and-suspenders backstop. Non-gating during wiring (rule #55 audit-first)."""
    import json
    manifest_path = os.path.join(ROOT, "book", "data", "data-claims.json")
    if not os.path.isfile(manifest_path):
        return PASS, ["no book/data/data-claims.json — nothing to check"]
    raw = json.load(open(manifest_path, encoding="utf-8"))
    claims = {k: v for k, v in raw.items() if not k.startswith("_")}
    md_files = _book_md_files()
    # Map source-slug -> its markdown text + the anchor ids it defines.
    by_slug: dict[str, tuple[str, set[str]]] = {}
    cited: set[str] = set()
    issues: list[str] = []
    for f in md_files:
        text = open(f, encoding="utf-8").read()
        stem = os.path.splitext(os.path.basename(f))[0]
        by_slug[stem] = (text, set(_HEADING_ANCHOR_RE.findall(text)))
        for m in _DATA_MARKER_RE.finditer(text):  # (a) every marker resolves
            slug = m.group(1)
            cited.add(slug)
            if slug not in claims:
                issues.append(f"{rel(f)}: [data: {slug}] has no entry in data-claims.json")
    for slug, entry in claims.items():
        src = entry.get("source", "")
        anchor = entry.get("anchor", "")
        if src not in by_slug:  # (b) source chapter exists
            issues.append(f"data-claims: {slug!r} source {src!r} is not a book chapter file")
            continue
        text, anchors = by_slug[src]
        if anchor and anchor not in anchors:  # (b) source still carries the anchor heading
            issues.append(f"data-claims: {slug!r} anchor {{#{anchor}}} not found as a heading id in {src}")
        norm_text = _norm_num_unit_haystack(text)
        for hold in entry.get("holds", []):  # (c) each holds string still present (loose)
            if _norm_num_unit(hold) not in norm_text:
                issues.append(f"data-claims: {slug!r} holds {hold!r} no longer appears in {src} "
                              f"(number may have changed — re-check the source)")
    for slug in sorted(set(claims) - cited):  # (d) uncited entry → warn (not a hard fail)
        issues.append(f"data-claims: WARN {slug!r} is in the manifest but nothing cites [data: {slug}] yet")
    return (FAIL if issues else PASS), issues


_WORD_NUM_UNIT_RE = re.compile(
    r"\b((?:(?:" + "|".join(list(_NUM_WORDS) + list(_NUM_SCALES)) + r")[\s-]*)+)([a-z]*)",
    re.I,
)


def _norm_num_unit_haystack(text: str) -> set[str]:
    """The set of normalized number+unit tokens present in a chapter's text — the haystack (c) searches.
    Captures BOTH digit-form ("5,000 lines" -> "5000lines") AND spelled-out-form ("fifty-eight files" ->
    "58files"), so a digit-form `holds` string matches spelled-out prose (spelling-agnostic) while a real
    number change still fails. Built once per source so each `holds` check is a set membership."""
    hay: set[str] = {_norm_num_unit(m.group(0)) for m in _NUM_UNIT_RE.finditer(text)}
    for m in _WORD_NUM_UNIT_RE.finditer(text):
        n = _words_to_int(m.group(1))
        if n is not None:
            unit = m.group(2).lower()
            hay.add(f"{n}{unit}")
    return hay


def _marker_keywords() -> tuple[str, ...]:
    """The build-time notation vocabulary — READ from its single source of truth in the build script
    (`build_book_html.MARKER_KEYWORDS`) so this gate can never drift from what the build defines. A new
    notation added there auto-extends this gate; there is NO second hand-maintained copy (CLAUDE.md rule
    #33: a stable check that reads the SSOT beats N hand-rolled lints)."""
    book_dir = os.path.join(ROOT, "book")
    if book_dir not in _sys.path:
        _sys.path.insert(0, book_dir)
    import build_book_html as bb  # noqa: E402 — path set above; the build owns the vocabulary
    return tuple(bb.MARKER_KEYWORDS)


def check_no_notation_leak():
    """WHOLE-VOCABULARY backstop: no build-time notation may survive into ANY served HTML page. The build
    consumes each notation and renders it to real HTML; if a marker is mis-placed (e.g. a `<!-- gloss-only …
    -->` glued to a prose paragraph with no blank line — the twice-shipped bug this gate closes), the
    markdown pass escapes it and it ships as visible `&lt;!-- … --&gt;` text. This gate fails on that class,
    keyed off the build's OWN vocabulary SSOT so it covers every marker, not just the one that leaked.

    Composes with (does NOT duplicate) `tests/book.py` rule 11 `check_no_raw_mermaid` — that guards
    un-rendered ```mermaid FENCES; this guards the marker-comment + `{{token}}` + `[+…+]` vocabulary.

    Three precise, keyword-scoped discriminators (NOT a blunt `<!--` / `{{` / `[+` scan — legitimate SVG
    structure comments, `<!-- noqa … -->`, the `GENERATED by catalog.py` banner, and any prose showing
    template syntax must NOT false-positive):
      (a) a marker-comment for a KNOWN vocabulary keyword, escaped (`&lt;!-- gloss …`) OR raw
          (`<!-- figure: …`). The keyword+boundary anchor is what excludes the banner and noqa comments.
      (b) an unresolved metric token `{{name}}` / macro `{{part:N}}` — the build fails loud on an unknown
          token, so any survivor means a token slipped a fence and shipped literally.
      (c) a leaked intra-word-emphasis span `[+X+]` — the build converts these to <em>; a survivor is a raw
          notation the reader sees.
    """
    files = html_files()
    if not files:
        return FAIL, ["no built HTML found — run `catalog.py build` first"]
    kws = _marker_keywords()
    if not kws:
        return FAIL, ["build_book_html.MARKER_KEYWORDS is empty — the vocabulary SSOT vanished"]
    kw_alt = "|".join(re.escape(k) for k in kws)
    # A marker comment for a known keyword, in EITHER shipped form: escaped (markdown-escaped visible text)
    # or raw (an un-consumed HTML comment). The trailing boundary (`:` arg-marker, or `-->`/whitespace for
    # the arg-less `glossary-auto`) keeps the match tight to the vocabulary and off same-prefixed prose.
    esc = rf"&lt;!--\s*(?:{kw_alt})(?:\s*:|\s+|&gt;|--&gt;)"
    raw = rf"<!--\s*(?:{kw_alt})(?:\s*:|\s+|-->)"
    marker_re = re.compile(f"(?:{esc})|(?:{raw})")
    token_re = re.compile(r"\{\{\s*(?:part:\d+|[a-z_][a-z0-9_]*)\s*\}\}")
    emph_re = re.compile(r"\[\+[^\]]+\+\]")
    issues = []
    for f in files:
        text = open(f, encoding="utf-8").read()
        for m in marker_re.finditer(text):
            issues.append(f"{rel(f)}: leaked notation marker {text[m.start():m.start()+60]!r}")
        for m in token_re.finditer(text):
            issues.append(f"{rel(f)}: unresolved metric token {m.group(0)!r}")
        for m in emph_re.finditer(text):
            issues.append(f"{rel(f)}: leaked intra-word emphasis {m.group(0)!r}")
    return (FAIL if issues else PASS), issues
