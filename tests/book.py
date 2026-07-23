"""AUDIT-ONLY structural checks over the embedded book (`book/`) — the mechanical arm of the
engineering-book document type (see the self-communicate skill's `writing/document-types.md`).

These are REPORT-ONLY: every function returns `(findings, stats)` and NONE of them contributes to the
suite's fail count. The book has known, deliberate gaps (draft chapters with no figure yet, placeholder
markers), so a hard gate here would wrongly red the whole suite. The driver in `catalog_tests.py` runs
these via a separate `--book-audit` path that prints findings and always exits neutral. Promote an
individual rule to blocking only once the book clears it — then move it behind a real `Check(...)`.

What each rule enforces (the engineering-book specializations `document-types.md` names):
  1. intra-book link integrity — nav-pager / figure-source / index See-link targets resolve.
  2. >=1 visual per chapter — every chapter page carries a <figure>/<svg>/mermaid.
  3. section-length cap — no heading-to-heading section exceeds the word/paragraph caps.
  4. thesis woven — the named theses appear across >=K chapters.
  5. figure hygiene — every `<!-- figure -->` source resolves AND has a non-empty caption.
  6. placeholder tracking — count `[FILL IN]` / `[MORE CHAPTERS FOLLOW]` (report, never fail).
  7. delimiter balance — parens / curly braces balance per section, after masking the constructs that
     legitimately carry unbalanced delimiters (code, mermaid, `{#anchor}`, `{{token}}`, build comments).
  8. heading-level skips — no heading jumps more than one level deeper than the last (h1->h3); the first
     heading is the chapter h1; exactly one h1 per page. Runs ~0 across the book — a promote-now candidate.

Intra-book links (rule 1) largely overlap the whole-site `check_html_links` in `tests/html.py`, which
already resolves every local href/src across the built site (book pages included). This module adds only
what that check does NOT cover: the `<!-- figure: path -->` SOURCE in the markdown (a comment, invisible to
the HTML link scanner) and the figure CAPTION. The nav-pager and index See-links are hrefs, so the site
scanner covers them; rule 1 re-reports them scoped to book/ for a single book-focused verdict.

Thresholds are module consts so they are tunable without touching logic.
"""
from __future__ import annotations

import os
import re

from tests.common import ROOT, rel

# ---- tunable thresholds (module consts; adjust as the book settles) -------------------------------
MAX_SECTION_WORDS = 400   # a heading-to-heading section over this many words is a wall of text
MAX_SECTION_PARAS = 6     # ...or over this many paragraphs
THESIS_TERMS = ("Modeling Thesis", "Alignment Thesis")  # the named theses the book weaves
THESIS_MIN_CHAPTERS = 4   # each thesis should recur across at least this many chapters
PLACEHOLDER_MARKERS = ("[FILL IN]", "[MORE CHAPTERS FOLLOW]")
DELIMITER_PAIRS = (("(", ")"), ("{", "}"))  # pairs checked for balance in prose (after masking)

BOOK = os.path.join(ROOT, "book")
# Source chapters live under these dirs (part1..5, plus front/back matter); appendix + meta files excluded.
_CHAPTER_SRC_DIRS = ("part1", "part2", "part3", "part4", "part5", "frontmatter", "backmatter")

# ---- source + built-page discovery ---------------------------------------------------------------


def _chapter_src_files() -> list[str]:
    """Every chapter SOURCE .md (part dirs + front/back matter). Appendix fills, README, AGENTS,
    index-terms, manuscript-cleaned are NOT chapters."""
    out: list[str] = []
    for d in _CHAPTER_SRC_DIRS:
        dp = os.path.join(BOOK, d)
        if not os.path.isdir(dp):
            continue
        out.extend(os.path.join(dp, fn) for fn in sorted(os.listdir(dp)) if fn.endswith(".md"))
    return out


# A real chapter page is `book/<N>.<M>-<slug>.html` (part chapters + front/back matter number as 0.x / 6.x).
# Appendix, index, and stack pages also carry `<header class="chap">` but are NOT chapters — exclude them
# so "a visual per chapter" and the section cap grade only the narrative body, not a reference appendix.
_CHAPTER_HTML_RE = re.compile(r"^\d+\.\d+-.+\.html$")


def _chapter_html_pages() -> list[str]:
    """Every BUILT narrative chapter page: a top-level `book/<N>.<M>-<slug>.html` carrying
    `<header class="chap">`. Appendix / index / stack pages are excluded by the numbered-slug pattern."""
    out: list[str] = []
    if not os.path.isdir(BOOK):
        return out
    for fn in sorted(os.listdir(BOOK)):
        if not _CHAPTER_HTML_RE.match(fn):
            continue
        p = os.path.join(BOOK, fn)
        try:
            txt = open(p, encoding="utf-8").read()
        except OSError:
            continue
        if '<header class="chap">' in txt:
            out.append(p)
    return out


def _main_body(html: str) -> str:
    """The <main>...</main> content of a chapter page (the chapter's own prose, minus the nav sidebar)."""
    m = re.search(r"<main\b.*?</main>", html, re.S)
    return m.group(0) if m else html


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s)


def _words(s: str) -> int:
    return len(_strip_tags(s).split())


# ---- rule 1: intra-book link integrity (figure-source + caption + hrefs, scoped to book/) --------


def check_intra_book_links() -> tuple[list[str], dict]:
    """Book-scoped link integrity. The whole-site `check_html_links` already resolves nav-pager and index
    See-link hrefs; here we add the coverage IT misses — the `<!-- figure: path -->` SOURCE in the
    markdown — and re-report any book href that fails to resolve, for a single book verdict."""
    findings: list[str] = []
    checked = 0
    # figure sources (markdown comments — invisible to the HTML link scanner). The build emits flat pages
    # at the book root, so a figure's `assets/...` path is relative to book/, NOT to the chapter's part-dir.
    for f in _chapter_src_files():
        txt = open(f, encoding="utf-8").read()
        for src in re.findall(r"<!--\s*figure:\s*([^|>]+?)\s*(?:\||-->)", txt):
            checked += 1
            tgt = os.path.normpath(os.path.join(BOOK, src.strip()))
            if not os.path.exists(tgt):
                findings.append(f"{rel(f)} -> figure source {src.strip()} (missing asset)")
    # built-page hrefs/srcs, scoped to book/ (dedup of the site scanner, book-focused)
    for p in _chapter_html_pages():
        base = os.path.dirname(p)
        body = open(p, encoding="utf-8").read()
        for ref in re.findall(r'(?:href|src)="([^"]+)"', body):
            if ref.startswith(("http://", "https://", "mailto:", "data:", "//", "#")):
                continue
            checked += 1
            tgt_rel = ref.split("#", 1)[0]
            if not tgt_rel:
                continue
            tgt = os.path.normpath(os.path.join(base, tgt_rel))
            if not os.path.exists(tgt):
                findings.append(f"{rel(p)} -> {ref} (missing target)")
    return findings, {"links_checked": checked, "broken": len(findings)}


# ---- rule 2: >=1 visual per chapter --------------------------------------------------------------


def check_visual_per_chapter() -> tuple[list[str], dict]:
    """Every built chapter page carries at least one visual: a <figure>, a bare <svg>, or a mermaid block."""
    findings: list[str] = []
    pages = _chapter_html_pages()
    without = 0
    for p in pages:
        body = _main_body(open(p, encoding="utf-8").read())
        has_visual = bool(re.search(r"<figure\b|<svg\b|class=\"mermaid\"|pre class=\"mermaid\"", body))
        if not has_visual:
            without += 1
            findings.append(f"{rel(p)} — no <figure>/<svg>/mermaid in chapter body")
    return findings, {"chapters": len(pages), "without_visual": without}


# ---- rule 3: section-length cap ------------------------------------------------------------------


def check_section_length() -> tuple[list[str], dict]:
    """No heading-to-heading section (split on h1/h2/h3) exceeds MAX_SECTION_WORDS or MAX_SECTION_PARAS.
    A section past the cap with no subheading/list/figure is a wall of text."""
    findings: list[str] = []
    over = 0
    total_sections = 0
    for p in _chapter_html_pages():
        body = _main_body(open(p, encoding="utf-8").read())
        # split into segments at each heading; keep the heading text as the segment label
        parts = re.split(r"(<h[123]\b[^>]*>.*?</h[123]>)", body, flags=re.S)
        # parts alternates: [pre, heading, content, heading, content, ...]
        i = 1
        while i < len(parts):
            heading = _strip_tags(parts[i]).strip()
            content = parts[i + 1] if i + 1 < len(parts) else ""
            total_sections += 1
            words = _words(content)
            paras = len(re.findall(r"<p\b", content))
            if words > MAX_SECTION_WORDS or paras > MAX_SECTION_PARAS:
                over += 1
                findings.append(
                    f"{rel(p)} § {heading!r}: {words} words / {paras} paras "
                    f"(cap {MAX_SECTION_WORDS} words / {MAX_SECTION_PARAS} paras)"
                )
            i += 2
    return findings, {"sections": total_sections, "over_cap": over}


# ---- rule 4: thesis woven across chapters --------------------------------------------------------


def check_thesis_woven() -> tuple[list[str], dict]:
    """Each named thesis appears across at least THESIS_MIN_CHAPTERS chapter SOURCE files."""
    findings: list[str] = []
    files = _chapter_src_files()
    per_thesis: dict[str, int] = {}
    for term in THESIS_TERMS:
        hits = [f for f in files if term in open(f, encoding="utf-8").read()]
        per_thesis[term] = len(hits)
        if len(hits) < THESIS_MIN_CHAPTERS:
            findings.append(
                f"thesis {term!r} appears in {len(hits)} chapter(s) "
                f"(want >= {THESIS_MIN_CHAPTERS}): {', '.join(rel(h) for h in hits) or '(none)'}"
            )
    return findings, {"chapters_scanned": len(files), **{f"'{k}'_chapters": v for k, v in per_thesis.items()}}


# ---- rule 5: figure hygiene (source resolves AND caption non-empty) ------------------------------


def check_figure_hygiene() -> tuple[list[str], dict]:
    """Every `<!-- figure: path | caption -->` resolves to an asset AND carries a non-empty caption."""
    findings: list[str] = []
    figures = 0
    for f in _chapter_src_files():
        txt = open(f, encoding="utf-8").read()
        for m in re.finditer(r"<!--\s*figure:\s*(.*?)\s*-->", txt, re.S):
            figures += 1
            inner = m.group(1)
            src, sep, caption = inner.partition("|")
            src = src.strip()
            caption = caption.strip()
            # figure paths are book-root-relative (flat page emission), not chapter-dir-relative.
            tgt = os.path.normpath(os.path.join(BOOK, src)) if src else ""
            if not src or not os.path.exists(tgt):
                findings.append(f"{rel(f)} — figure source {src or '(empty)'} does not resolve")
            if not sep or not caption:
                findings.append(f"{rel(f)} — figure {src or '(?)'} has an empty caption")
    return findings, {"figures": figures, "issues": len(findings)}


# ---- rule 6: placeholder tracking (report only, never a finding to fix) --------------------------


def check_placeholders() -> tuple[list[str], dict]:
    """Count placeholder markers across chapter sources. Reported for visibility; never a fail signal —
    a draft book carries these on purpose."""
    findings: list[str] = []
    counts: dict[str, int] = {mk: 0 for mk in PLACEHOLDER_MARKERS}
    for f in _chapter_src_files():
        txt = open(f, encoding="utf-8").read()
        for mk in PLACEHOLDER_MARKERS:
            n = txt.count(mk)
            if n:
                counts[mk] += n
                findings.append(f"{rel(f)} — {n}x {mk}")
    return findings, {"total": sum(counts.values()), **counts}


# ---- rule 7: delimiter balance (after masking the legitimate carriers) ---------------------------


def _mask_markdown_noise(txt: str) -> str:
    """Blank out the constructs that legitimately carry unbalanced delimiters, so the balance check sees
    only prose: fenced code blocks, inline-code spans, mermaid blocks, `{#anchor}` heading ids,
    `{{token}}` metric placeholders, and `<!-- ... -->` build directives (figure/index-def/part-title/...).
    Replace each with spaces (preserving length so an approximate line locator stays meaningful)."""
    def _blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    # order matters: strip fenced/mermaid blocks and comments before inline spans
    txt = re.sub(r"```.*?```", _blank, txt, flags=re.S)          # fenced code (incl. ```mermaid)
    txt = re.sub(r"<!--.*?-->", _blank, txt, flags=re.S)          # build directives / HTML comments
    txt = re.sub(r"`[^`\n]*`", _blank, txt)                        # inline-code spans
    txt = re.sub(r"\{\{[^}]*\}\}", _blank, txt)                    # {{token}} metric placeholders
    txt = re.sub(r"\{#[^}]*\}", _blank, txt)                        # {#anchor} heading-id syntax
    return txt


def check_delimiter_balance() -> tuple[list[str], dict]:
    """Per chapter source, per heading-to-heading section, count each delimiter pair after masking the
    legitimate carriers; report any section with an unequal open/close count. Audit-only by nature — prose
    smileys and lone parens produce false positives, so this surfaces candidates for a human to eyeball, it
    does not fail the gate."""
    findings: list[str] = []
    imbalanced = 0
    sections_scanned = 0
    for f in _chapter_src_files():
        masked = _mask_markdown_noise(open(f, encoding="utf-8").read())
        # split into sections at markdown ATX headings; keep a label for each
        parts = re.split(r"(?m)^(#{1,6}\s+.*)$", masked)
        # parts: [pre, heading, body, heading, body, ...]; a leading pre-body counts as its own section
        segments: list[tuple[str, str]] = []
        if parts[0].strip():
            segments.append(("(preamble)", parts[0]))
        i = 1
        while i < len(parts):
            label = re.sub(r"^#{1,6}\s+", "", parts[i]).strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            segments.append((label, body))
            i += 2
        for label, body in segments:
            sections_scanned += 1
            for op, cl in DELIMITER_PAIRS:
                no, nc = body.count(op), body.count(cl)
                if no != nc:
                    imbalanced += 1
                    # approximate location: first line in the body carrying either delimiter
                    loc = "?"
                    for ln_no, ln in enumerate(body.splitlines(), 1):
                        if op in ln or cl in ln:
                            loc = f"~body-line {ln_no}"
                            break
                    findings.append(
                        f"{rel(f)} § {label!r}: {op}{cl} imbalance ({no} open / {nc} close), {loc}"
                    )
    return findings, {"sections": sections_scanned, "imbalanced": imbalanced}


# ---- rule 8: heading-level skips (deterministic sibling of the axe heading-order check) -----------


def check_heading_levels() -> tuple[list[str], dict]:
    """Per chapter source, over the markdown ATX headings: flag a jump of more than one level deeper than
    the previous heading (h1->h3), a first heading that is not the chapter h1, or more than one h1. This is
    the deterministic sibling of axe's heading-order check. It runs ~0 across the book — a candidate to
    PROMOTE TO BLOCKING immediately, unlike the draft-gap rules above."""
    findings: list[str] = []
    files = _chapter_src_files()
    for f in files:
        masked = _mask_markdown_noise(open(f, encoding="utf-8").read())  # ignore `#` inside code fences
        levels = [(len(m.group(1)), m.group(2).strip())
                  for m in re.finditer(r"(?m)^(#{1,6})\s+(.*)$", masked)]
        if not levels:
            continue
        h1_count = sum(1 for lvl, _ in levels if lvl == 1)
        if levels[0][0] != 1:
            findings.append(f"{rel(f)}: first heading is h{levels[0][0]} ({levels[0][1]!r}), not the chapter h1")
        if h1_count != 1:
            findings.append(f"{rel(f)}: {h1_count} h1 headings (want exactly 1)")
        prev = levels[0][0]
        for lvl, text in levels[1:]:
            if lvl > prev + 1:
                findings.append(f"{rel(f)}: heading jumps h{prev}->h{lvl} at {text!r} (skips a level)")
            prev = lvl
    return findings, {"chapters_scanned": len(files), "issues": len(findings)}


# ---- driver: run every rule and print a report; ALWAYS exit-neutral ------------------------------

_RULES = [
    ("1. intra-book link integrity", check_intra_book_links),
    ("2. >=1 visual per chapter", check_visual_per_chapter),
    ("3. section-length cap", check_section_length),
    ("4. thesis woven across chapters", check_thesis_woven),
    ("5. figure hygiene (source + caption)", check_figure_hygiene),
    ("6. placeholder tracking", check_placeholders),
    ("7. delimiter balance (parens / braces)", check_delimiter_balance),
    ("8. heading-level skips (PROMOTE-candidate)", check_heading_levels),
]


def run_book_audit() -> int:
    """Run every book rule and print a per-rule report. AUDIT-ONLY: returns 0 regardless of findings, so
    the book's known draft gaps never red the suite. The report IS the deliverable."""
    pages = _chapter_html_pages()
    srcs = _chapter_src_files()
    print(f"== Book audit (AUDIT-ONLY — never fails the gate): "
          f"{len(pages)} built chapter page(s), {len(srcs)} source chapter(s) ==")
    if not pages:
        print("  (no built chapter pages found — run `catalog.py build` first; report is empty)")
    grand = 0
    for label, fn in _RULES:
        findings, stats = fn()
        grand += len(findings)
        statline = " · ".join(f"{k}={v}" for k, v in stats.items())
        print(f"  [audit] {label}: {len(findings)} finding(s) — {statline}")
        for it in findings:
            print(f"          {it}")
    print(f"== Book audit: {grand} finding(s) across {len(_RULES)} rules (exit-neutral) ==")
    return 0
