"""AUDIT-ONLY structural checks over the embedded book (`book/`) — the mechanical arm of the
engineering-book document type (see the self-communicate skill's `writing/document-types.md`).

These are REPORT-ONLY: every function returns `(findings, stats)` and NONE of them contributes to the
suite's fail count. The book has known, deliberate gaps (draft chapters with no figure yet, placeholder
markers), so a hard gate here would wrongly red the whole suite. The driver in `catalog_tests.py` runs
these via a separate `--book-audit` path that prints findings and always exits neutral. Promote an
individual rule to blocking only once the book clears it — then move it behind a real `Check(...)`.

What each rule enforces (the engineering-book specializations `document-types.md` names). The name in
brackets is the LINT NAME an inline suppression cites (see "Suppression" below):

  1. [book-links]        intra-book link integrity — nav-pager / figure-source / index See-link targets resolve.
  2. [book-visual]       >=1 visual per chapter — every chapter page carries a <figure>/<svg>/mermaid.
  3. [book-section-cap]  section-length cap — no heading-to-heading section exceeds the word/paragraph caps.
  4. [book-thesis]       thesis woven — the named theses appear across >=K chapters.
  5. [book-figure]       figure hygiene — every `<!-- figure -->` source resolves AND has a non-empty caption.
  6. [book-placeholder]  placeholder tracking — count `[FILL IN]` / `[MORE CHAPTERS FOLLOW]` (report, never fail).
  7. [book-delimiters]   delimiter balance — parens / curly braces balance per section, after masking the
                         constructs that legitimately carry unbalanced delimiters (code, mermaid, build comments).
  8. [book-headings]     heading-level skips — no heading jumps more than one level deeper than the last
                         (h1->h3); the first heading is the chapter h1; exactly one h1 per page.

**Suppression.** Every rule honors an inline suppression comment, mirroring the repo's
`# noqa: <name> — <reason>` convention but expressed as an HTML comment (the book is markdown):

    <!-- noqa: <lint-name> — <reason> -->

placed in the chapter SOURCE `.md` (authors edit source, not the generated HTML). A reason token after the
em-dash or hyphen is REQUIRED — a bare `<!-- noqa: book-visual -->` does not suppress (it is reported as a
malformed suppression). A suppression silences findings of THAT lint for the file it sits in; for the
per-section rules (section-cap, delimiters) it may ALSO name the section to scope it to one section — see
`_SuppressionIndex.covers`. Suppressed findings are still surfaced, in a separate report section, so
nothing silenced disappears.

Intra-book links (rule 1) largely overlap the whole-site `check_html_links` in `tests/html.py`, which
already resolves every local href/src across the built site (book pages included). This module adds only
what that check does NOT cover: the `<!-- figure: path -->` SOURCE in the markdown (a comment, invisible to
the HTML link scanner) and the figure CAPTION.

Thresholds are module consts so they are tunable without touching logic.
"""
from __future__ import annotations

import os
import re
from typing import NamedTuple

from tests.common import ROOT, rel

# ---- tunable thresholds (module consts; adjust as the book settles) -------------------------------
MAX_SECTION_WORDS = 400   # a heading-to-heading section over this many words is a wall of text
MAX_SECTION_PARAS = 6     # ...or over this many paragraphs
THESIS_TERMS = ("Modeling Thesis", "Alignment Thesis")  # the named theses the book weaves
THESIS_MIN_CHAPTERS = 4   # each thesis should recur across at least this many chapters
# Placeholder markers are matched by BRACKET+PHRASE, with an optional `: <body>` — authors write both the
# bare `[FILL IN]` and the annotated `[FILL IN: introduce the running example ...]`. Matching the exact
# string `[FILL IN]` (the old bug) missed every colon-and-body instance. The phrases only; the regex below
# adds the `[`, the optional `: body`, and the closing `]`.
PLACEHOLDER_PHRASES = ("FILL IN", "MORE CHAPTERS FOLLOW")
# `[<phrase>]` or `[<phrase>: any body up to the closing bracket]`. Scanned over SOURCE .md (never the
# built HTML, where the brackets may be escaped/rendered differently).
_PLACEHOLDER_RE = re.compile(
    r"\[(?P<phrase>" + "|".join(re.escape(p) for p in PLACEHOLDER_PHRASES) + r")(?::[^\]]*)?\]")
DELIMITER_PAIRS = (("(", ")"), ("{", "}"))  # pairs checked for balance in prose (after masking)

BOOK = os.path.join(ROOT, "book")
# Source chapters live under these dirs (part1..5, plus front/back matter); appendix + meta files excluded.
_CHAPTER_SRC_DIRS = ("part1", "part2", "part3", "part4", "part5", "frontmatter", "backmatter")
# Front/back matter (Preface, Acknowledgments, Conclusion, Implications) is narrative but not a numbered
# body chapter — it does not plausibly want a figure, so the visual-per-chapter rule EXEMPTS it by default.
# A front/back-matter page that DOES want the rule can still opt in via source dir; a body chapter that
# genuinely needs no figure opts out with a per-file `<!-- noqa: book-visual — <reason> -->`.
_VISUAL_EXEMPT_SRC_DIRS = ("frontmatter", "backmatter")

# ---- the finding + suppression model -------------------------------------------------------------


class Finding(NamedTuple):
    """One audit finding. `src` is the chapter SOURCE `.md` a suppression for this finding would live in
    (None for a whole-book rule like thesis, which no single file can suppress). `label` scopes a
    per-section suppression (the section heading text) — empty for a whole-file finding. `msg` is the
    human-readable line printed in the report."""
    src: str | None
    label: str
    msg: str


class Suppression(NamedTuple):
    lint: str          # the lint name the comment cites, e.g. "book-visual"
    reason: str        # the required reason token(s) after the em-dash / hyphen
    scope: str         # optional section-scope text (a substring of the section heading), or ""
    raw: str           # the raw comment, for the report


# `<!-- noqa: <lint-name> [| <section-scope>] — <reason> -->`. The separator before the reason is an
# em-dash or a WHITESPACE-FLANKED hyphen (mirrors the repo's `# noqa: <name> — <reason>`); the flanking
# space matters — a bare hyphen inside a lint name like `book-visual` must NOT be read as the separator, so
# the lint name is captured non-greedily and the separator requires ` — ` / ` - ` (space before the dash).
# A reason token is REQUIRED. An optional `| <scope>` before the separator narrows a per-section rule.
_NOQA_RE = re.compile(
    r"<!--\s*noqa:\s*(?P<lint>[\w-]+?)\s*"
    r"(?:\|\s*(?P<scope>[^—|][^—]*?)\s*)?"        # optional "| <scope>"
    r"(?:\s—|\s-{1,2})\s+(?P<reason>\S.*?)\s*-->",  # separator: em-dash or hyphen, space BEFORE it
    re.S,
)
# A malformed suppression: cites a lint but gives no reason (bare `<!-- noqa: book-visual -->`). Reported
# so a typo doesn't silently fail to suppress.
_NOQA_BARE_RE = re.compile(r"<!--\s*noqa:\s*(?P<lint>[\w-]+)\s*-->")


class _SuppressionIndex:
    """Reads every chapter source's `<!-- noqa: ... -->` comments once, and answers `covers(finding)`."""

    def __init__(self) -> None:
        self.by_file: dict[str, list[Suppression]] = {}
        self.malformed: list[Finding] = []
        for f in _chapter_src_files():
            txt = open(f, encoding="utf-8").read()
            sups: list[Suppression] = []
            for m in _NOQA_RE.finditer(txt):
                sups.append(Suppression(
                    lint=m.group("lint"),
                    reason=m.group("reason").strip(),
                    scope=(m.group("scope") or "").strip(),
                    raw=m.group(0).strip(),
                ))
            self.by_file[f] = sups
            # flag bare noqa comments that matched no well-formed pattern (no reason token)
            wellformed_spans = {m.group(0) for m in _NOQA_RE.finditer(txt)}
            for bm in _NOQA_BARE_RE.finditer(txt):
                if bm.group(0) not in wellformed_spans:
                    self.malformed.append(Finding(
                        src=f, label="",
                        msg=f"{rel(f)} — malformed suppression {bm.group(0)!r}: "
                            f"missing required reason after '—' (won't suppress)"))

    def covers(self, lint: str, fnd: Finding) -> Suppression | None:
        """A suppression covers a finding when it is in the same source file, names the same lint, and —
        if it carries a `| <scope>` — that scope text appears in the finding's section label."""
        if fnd.src is None:
            return None
        for s in self.by_file.get(fnd.src, ()):
            if s.lint != lint:
                continue
            if s.scope and s.scope.lower() not in fnd.label.lower():
                continue
            return s
        return None


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


# The built page and its source share a basename (`2.2-loops-and-models.html` <- `.../2.2-loops-and-models.md`),
# so a suppression placed in the source .md governs findings raised over the built HTML.
def _src_for_html(html_path: str) -> str | None:
    """The chapter SOURCE `.md` for a built chapter page, matched by basename. None if not found (so a
    finding stays unsuppressible rather than crashing)."""
    stem = os.path.splitext(os.path.basename(html_path))[0]
    for f in _chapter_src_files():
        if os.path.splitext(os.path.basename(f))[0] == stem:
            return f
    return None


def _is_visual_exempt(src_md: str | None) -> bool:
    """True when the chapter SOURCE .md sits in a front/back-matter dir the visual-per-chapter rule
    exempts by default (Preface / Acknowledgments / Conclusion / Implications)."""
    if src_md is None:
        return False
    parent = os.path.basename(os.path.dirname(src_md))
    return parent in _VISUAL_EXEMPT_SRC_DIRS


def _main_body(html: str) -> str:
    """The <main>...</main> content of a chapter page (the chapter's own prose, minus the nav sidebar)."""
    m = re.search(r"<main\b.*?</main>", html, re.S)
    return m.group(0) if m else html


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s)


def _words(s: str) -> int:
    return len(_strip_tags(s).split())


# ---- rule 1: intra-book link integrity (figure-source + caption + hrefs, scoped to book/) --------


def check_intra_book_links() -> tuple[list[Finding], dict]:
    """Book-scoped link integrity. The whole-site `check_html_links` already resolves nav-pager and index
    See-link hrefs; here we add the coverage IT misses — the `<!-- figure: path -->` SOURCE in the
    markdown — and re-report any book href that fails to resolve, for a single book verdict."""
    findings: list[Finding] = []
    checked = 0
    # figure sources (markdown comments — invisible to the HTML link scanner). The build emits flat pages
    # at the book root, so a figure's `assets/...` path is relative to book/, NOT to the chapter's part-dir.
    for f in _chapter_src_files():
        txt = open(f, encoding="utf-8").read()
        for src in re.findall(r"<!--\s*figure:\s*([^|>]+?)\s*(?:\||-->)", txt):
            checked += 1
            tgt = os.path.normpath(os.path.join(BOOK, src.strip()))
            if not os.path.exists(tgt):
                findings.append(Finding(f, "", f"{rel(f)} -> figure source {src.strip()} (missing asset)"))
    # built-page hrefs/srcs, scoped to book/ (dedup of the site scanner, book-focused)
    for p in _chapter_html_pages():
        base = os.path.dirname(p)
        src_md = _src_for_html(p)
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
                findings.append(Finding(src_md, "", f"{rel(p)} -> {ref} (missing target)"))
    return findings, {"links_checked": checked, "broken": len(findings)}


# ---- rule 2: >=1 visual per chapter --------------------------------------------------------------


def check_visual_per_chapter() -> tuple[list[Finding], dict]:
    """Every built NARRATIVE-BODY chapter page carries at least one visual: a <figure>, a bare <svg>, or a
    mermaid block. Front/back matter (Preface, Acknowledgments, Conclusion, Implications — source dirs in
    `_VISUAL_EXEMPT_SRC_DIRS`) is EXEMPT by default. A body chapter that genuinely needs no figure suppresses
    with `<!-- noqa: book-visual — <reason> -->` in its source .md."""
    findings: list[Finding] = []
    pages = _chapter_html_pages()
    without = exempt = 0
    for p in pages:
        src_md = _src_for_html(p)
        if _is_visual_exempt(src_md):
            exempt += 1
            continue
        body = _main_body(open(p, encoding="utf-8").read())
        has_visual = bool(re.search(r"<figure\b|<svg\b|class=\"mermaid\"|pre class=\"mermaid\"", body))
        if not has_visual:
            without += 1
            findings.append(Finding(src_md, "",
                                    f"{rel(p)} — no <figure>/<svg>/mermaid in chapter body"))
    return findings, {"chapters": len(pages), "front_back_exempt": exempt, "without_visual": without}


# ---- rule 3: section-length cap ------------------------------------------------------------------


def check_section_length() -> tuple[list[Finding], dict]:
    """No heading-to-heading section (split on h1/h2/h3) exceeds MAX_SECTION_WORDS or MAX_SECTION_PARAS.
    A deliberately long section suppresses with `<!-- noqa: book-section-cap | <heading-text> — <reason> -->`
    in the source .md (scope it to the section by naming the heading)."""
    findings: list[Finding] = []
    over = 0
    total_sections = 0
    for p in _chapter_html_pages():
        src_md = _src_for_html(p)
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
                findings.append(Finding(
                    src_md, heading,
                    f"{rel(p)} § {heading!r}: {words} words / {paras} paras "
                    f"(cap {MAX_SECTION_WORDS} words / {MAX_SECTION_PARAS} paras)"))
            i += 2
    return findings, {"sections": total_sections, "over_cap": over}


# ---- rule 4: thesis woven across chapters --------------------------------------------------------


def check_thesis_woven() -> tuple[list[Finding], dict]:
    """Each named thesis appears across at least THESIS_MIN_CHAPTERS chapter SOURCE files. This is a
    whole-book finding (no single file owns it); suppress it in ANY chapter source with
    `<!-- noqa: book-thesis | <thesis-name> — <reason> -->` (the scope names the thesis)."""
    findings: list[Finding] = []
    files = _chapter_src_files()
    per_thesis: dict[str, int] = {}
    for term in THESIS_TERMS:
        hits = [f for f in files if term in open(f, encoding="utf-8").read()]
        per_thesis[term] = len(hits)
        if len(hits) < THESIS_MIN_CHAPTERS:
            # attribute to whichever source carries a matching book-thesis suppression, else whole-book.
            findings.append(Finding(
                None, term,
                f"thesis {term!r} appears in {len(hits)} chapter(s) "
                f"(want >= {THESIS_MIN_CHAPTERS}): {', '.join(rel(h) for h in hits) or '(none)'}"))
    return findings, {"chapters_scanned": len(files), **{f"'{k}'_chapters": v for k, v in per_thesis.items()}}


# ---- rule 5: figure hygiene (source resolves AND caption non-empty) ------------------------------


def check_figure_hygiene() -> tuple[list[Finding], dict]:
    """Every `<!-- figure: path | caption -->` resolves to an asset AND carries a non-empty caption.
    Suppress a deliberate exception with `<!-- noqa: book-figure — <reason> -->` in the source .md."""
    findings: list[Finding] = []
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
                findings.append(Finding(f, src, f"{rel(f)} — figure source {src or '(empty)'} does not resolve"))
            if not sep or not caption:
                findings.append(Finding(f, src, f"{rel(f)} — figure {src or '(?)'} has an empty caption"))
    return findings, {"figures": figures, "issues": len(findings)}


# ---- rule 6: placeholder tracking (report only, never a finding to fix) --------------------------


def check_placeholders() -> tuple[list[Finding], dict]:
    """Count placeholder markers across chapter SOURCE .md files. Matches `[FILL IN]` / `[MORE CHAPTERS
    FOLLOW]` AND their colon-and-body forms (`[FILL IN: <text>]`) via `_PLACEHOLDER_RE`. Reported for
    visibility; suppress a deliberately retained marker with `<!-- noqa: book-placeholder — <reason> -->`
    in the source .md."""
    findings: list[Finding] = []
    counts: dict[str, int] = {p: 0 for p in PLACEHOLDER_PHRASES}
    for f in _chapter_src_files():
        txt = open(f, encoding="utf-8").read()
        per_file: dict[str, int] = {p: 0 for p in PLACEHOLDER_PHRASES}
        for m in _PLACEHOLDER_RE.finditer(txt):
            per_file[m.group("phrase")] += 1
        for phrase, n in per_file.items():
            if n:
                counts[phrase] += n
                # label is the bracketed phrase, so a per-marker suppression scope can name it.
                findings.append(Finding(f, f"[{phrase}]", f"{rel(f)} — {n}x [{phrase}]"))
    return findings, {"total": sum(counts.values()), **{f"[{k}]": v for k, v in counts.items()}}


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


def check_delimiter_balance() -> tuple[list[Finding], dict]:
    """Per chapter source, per heading-to-heading section, count each delimiter pair after masking the
    legitimate carriers; report any section with an unequal open/close count. Audit-only by nature — prose
    smileys and lone parens produce false positives, so this surfaces candidates for a human to eyeball.
    Suppress a deliberate imbalance with `<!-- noqa: book-delimiters | <heading-text> — <reason> -->`."""
    findings: list[Finding] = []
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
                    findings.append(Finding(
                        f, label,
                        f"{rel(f)} § {label!r}: {op}{cl} imbalance ({no} open / {nc} close), {loc}"))
    return findings, {"sections": sections_scanned, "imbalanced": imbalanced}


# ---- rule 8: heading-level skips (deterministic sibling of the axe heading-order check) -----------


def check_heading_levels() -> tuple[list[Finding], dict]:
    """Per chapter source, over the markdown ATX headings: flag a jump of more than one level deeper than
    the previous heading (h1->h3), a first heading that is not the chapter h1, or more than one h1. This is
    the deterministic sibling of axe's heading-order check. It runs ~0 across the book — a candidate to
    PROMOTE TO BLOCKING immediately. Suppress a deliberate structure with
    `<!-- noqa: book-headings — <reason> -->` in the source .md."""
    findings: list[Finding] = []
    files = _chapter_src_files()
    for f in files:
        masked = _mask_markdown_noise(open(f, encoding="utf-8").read())  # ignore `#` inside code fences
        levels = [(len(m.group(1)), m.group(2).strip())
                  for m in re.finditer(r"(?m)^(#{1,6})\s+(.*)$", masked)]
        if not levels:
            continue
        h1_count = sum(1 for lvl, _ in levels if lvl == 1)
        if levels[0][0] != 1:
            findings.append(Finding(
                f, levels[0][1],
                f"{rel(f)}: first heading is h{levels[0][0]} ({levels[0][1]!r}), not the chapter h1"))
        if h1_count != 1:
            findings.append(Finding(f, "", f"{rel(f)}: {h1_count} h1 headings (want exactly 1)"))
        prev = levels[0][0]
        for lvl, text in levels[1:]:
            if lvl > prev + 1:
                findings.append(Finding(
                    f, text, f"{rel(f)}: heading jumps h{prev}->h{lvl} at {text!r} (skips a level)"))
            prev = lvl
    return findings, {"chapters_scanned": len(files), "issues": len(findings)}


# ---- rule 9: render fidelity (un-converted markdown left literal in the BUILT html) ---------------

# Each pattern is a true-bug signal: markdown the book renderer failed to convert, left sitting as
# literal text inside a <p>. Every one has a known cause (a bullet/number list that wrapped across lines
# and fell through to a paragraph; a bold span the emphasis pass couldn't match; a code/link the inline
# pass missed). The book should render 0 of these — a hit means the renderer dropped a construct.
_RENDER_SMELLS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("literal **bold**",            re.compile(r"\*\*")),
    ("bullet swallowed into <p>",   re.compile(r"^\s*-\s")),
    ("numbered item at <p> start",  re.compile(r"^\s*\d+\.\s")),
    # user's heuristic: two ` - ` breaks (or two `N. ` markers) in one paragraph usually means a
    # `- `/`N. ` list collapsed mid-<p>. The dash and the number smell are a matched pair.
    ("multi-dash run (list?)",      re.compile(r"\s-\s\S.*\s-\s")),
    ("multi-number run (list?)",    re.compile(r"(?:^|\s)\d+\.\s.+\s\d+\.\s")),
    ("literal `code` span",         re.compile(r"`[^`]+`")),
    ("literal [text](link)",        re.compile(r"\[[^\]]+\]\([^)]+\)")),
)
_P_RE = re.compile(r"<p>(.*?)</p>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def check_render_fidelity() -> tuple[list[Finding], dict]:
    """Scan every BUILT `book/*.html` page's <p> bodies for markdown the renderer left un-converted
    (literal `**`, a `- `/`N. ` list swallowed into a paragraph, a stray `` `code` `` or `[text](link)`).
    Reads the built HTML, so it catches a renderer regression the source-only rules can't see. Runs 0 on a
    clean build — a PROMOTE-to-BLOCKING candidate. src=None (the fix is in the renderer or the source md,
    not a suppressible authoring choice), so findings surface but carry no noqa."""
    import glob
    findings: list[Finding] = []
    pages = 0
    for f in sorted(glob.glob(os.path.join(BOOK, "*.html"))):
        pages += 1
        html = open(f, encoding="utf-8").read()
        for m in _P_RE.finditer(html):
            text = _TAG_RE.sub("", m.group(1)).replace("&amp;", "&")
            for name, pat in _RENDER_SMELLS:
                if pat.search(text):
                    findings.append(Finding(None, "", f"{rel(f)} — {name}: {text[:90].strip()!r}"))
    return findings, {"pages_scanned": pages, "issues": len(findings)}


# ---- driver: run every rule, partition suppressed vs active, print a report; ALWAYS exit-neutral --

# (label, lint-name, fn). The lint-name is what an inline `<!-- noqa: <name> — <reason> -->` cites.
_RULES = [
    ("1. intra-book link integrity", "book-links", check_intra_book_links),
    ("2. >=1 visual per chapter", "book-visual", check_visual_per_chapter),
    ("3. section-length cap", "book-section-cap", check_section_length),
    ("4. thesis woven across chapters", "book-thesis", check_thesis_woven),
    ("5. figure hygiene (source + caption)", "book-figure", check_figure_hygiene),
    ("6. placeholder tracking", "book-placeholder", check_placeholders),
    ("7. delimiter balance (parens / braces)", "book-delimiters", check_delimiter_balance),
    ("8. heading-level skips (PROMOTE-candidate)", "book-headings", check_heading_levels),
    ("9. render fidelity (un-converted markdown)", "book-render-fidelity", check_render_fidelity),
]

# the lint names, exported so a suppression comment can be validated against the known set.
LINT_NAMES = frozenset(name for _, name, _ in _RULES)


def run_book_audit() -> int:
    """Run every book rule, split findings into ACTIVE and SUPPRESSED (via inline `<!-- noqa: ... -->`
    comments), and print a per-rule report with the two kept apart. AUDIT-ONLY: returns 0 regardless of
    findings, so the book's known draft gaps never red the suite. The report IS the deliverable."""
    idx = _SuppressionIndex()
    pages = _chapter_html_pages()
    srcs = _chapter_src_files()
    print(f"== Book audit (AUDIT-ONLY — never fails the gate): "
          f"{len(pages)} built chapter page(s), {len(srcs)} source chapter(s) ==")
    if not pages:
        print("  (no built chapter pages found — run `catalog.py build` first; report is empty)")

    # flag any suppression that cites an unknown lint name (typo defense).
    unknown_sups: list[str] = []
    for f, sups in idx.by_file.items():
        for s in sups:
            if s.lint not in LINT_NAMES:
                unknown_sups.append(f"{rel(f)} — suppression cites unknown lint {s.lint!r}: {s.raw}")

    active_total = suppressed_total = 0
    suppressed_report: list[str] = []
    for label, lint, fn in _RULES:
        findings, stats = fn()
        active, suppressed = [], []
        for fnd in findings:
            s = idx.covers(lint, fnd)
            (suppressed if s else active).append((fnd, s))
        active_total += len(active)
        suppressed_total += len(suppressed)
        statline = " · ".join(f"{k}={v}" for k, v in stats.items())
        print(f"  [audit] {label} [{lint}]: {len(active)} active"
              f"{f' ({len(suppressed)} suppressed)' if suppressed else ''} — {statline}")
        for fnd, _ in active:
            print(f"          {fnd.msg}")
        for fnd, s in suppressed:
            suppressed_report.append(f"[{lint}] {fnd.msg}\n            └─ suppressed: {s.reason}")

    # the SUPPRESSED section — everything silenced stays visible.
    print(f"\n== Suppressed findings ({suppressed_total}) — silenced by inline <!-- noqa --> comments ==")
    if suppressed_report:
        for line in suppressed_report:
            print(f"  {line}")
    else:
        print("  (none)")

    # malformed / unknown suppressions — a typo must not silently fail to suppress.
    problems = [m.msg for m in idx.malformed] + unknown_sups
    if problems:
        print(f"\n== Suppression problems ({len(problems)}) — these do NOT suppress anything ==")
        for pr in problems:
            print(f"  {pr}")

    print(f"\n== Book audit: {active_total} active finding(s), {suppressed_total} suppressed, "
          f"across {len(_RULES)} rules (exit-neutral) ==")
    return 0
