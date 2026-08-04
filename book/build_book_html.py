#!/usr/bin/env python3
"""Render the polished book chapters to a small static HTML site.

AUTO-GENERATED OUTPUT: this script emits *.html in this folder; do not hand-edit
the .html (re-run `python3 build_book_html.py` to regenerate). Stdlib-only.

The book source is a Part/Chapter filesystem hierarchy — the directory tree encodes
the ordering so PART.CHAPTER is explicit in the path:

    book/frontmatter/0.1-preface.md            -> Front matter, order 0.1
    book/part1/1.1-the-ada-context.md          -> Part 1, Chapter 1
    book/part1/1.2-the-timeline-and-the-work.md-> Part 1, Chapter 2
    book/part2/2.1-the-printer.md              -> Part 2, Chapter 1
    …
    book/backmatter/5.1-conclusion.md          -> Back matter, order 5.1

The build WALKS this hierarchy, derives the part number and chapter number from each
file's `part<N>/` dir and `<N>.<M>-slug.md` name, and reads the human-readable
`<!-- part-title: … --> <!-- chapter-title: … -->` metadata from the file. It emits one
flat `<slug>.html` per chapter (Part/Chapter TOC nav on top, prev/next at the bottom),
an `index.html` landing page, and — appended after the back matter — a Gang-of-Four
appendix projected from the sibling catalogue entries.

Front matter (part 0) and back matter (part 6) render without a "Chapter N" kicker; the
first chapter of each numbered Part opens with a verbatim epigraph. Chapter prose may
reference the shared metrics file (`data/metrics.json`) through `{{token}}` placeholders,
substituted at build time so the headline numbers live in one place.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent

# Single source of truth for the book's cover identity — book-manifest.json (also read by catalog.py).
_BOOK_MANIFEST = json.loads((HERE / "book-manifest.json").read_text(encoding="utf-8"))
_PDF_FILENAME = _BOOK_MANIFEST["pdf_filename"]  # single source: the manifest


def _cover_sub(cls: str) -> str:
    """Optional subtitle div for a cover site, from the manifest; empty when the subtitle is blank."""
    s = _BOOK_MANIFEST.get("subtitle", "")
    return f'<div class="{cls}">{html.escape(s)}</div>' if s else ""
ROOT = HERE.parent  # the catalogue root — the appendix reads the entry .md files from here

# Design-token SSOT projection (Umber Monograph) — the CSS :root block + web-font link, both derived from
# book-models/design-tokens.json by the stdlib-only projector, so the web book and the site share one
# typed token model. Inlined into the book CSS below.
sys.path.insert(0, str(ROOT / "book-models"))
import design_tokens as _dtokens  # noqa: E402 — the design-token projector (stdlib-only)

_TOKENS = _dtokens.load()
CSS_ROOT_BLOCK = _dtokens.css_root_block(_TOKENS)
FONTS_LINK = _dtokens.google_fonts_link(_TOKENS)
# Mermaid label sizes — the SAME token that drives the mermaid LAYOUT config (`mermaid_theme`) so the
# CSS that DISPLAYS the labels below can never render bigger than the boxes mermaid laid out (the
# config==CSS invariant that stops label overflow). Do not hardcode these px; they follow the tokens.
_MERMAID_LABEL_PX = _dtokens.mermaid_label_px(_TOKENS)
ACCENT = _TOKENS.palette["accent"]  # umber — kept for the few Python-side consumers (cover / mermaid)
COPYRIGHT = f"© {_BOOK_MANIFEST['author']}, {_BOOK_MANIFEST['copyright_years']}"
# Cover "last updated" date. A STABLE constant, bumped intentionally — a per-build/per-commit date would
# churn the tracked book HTML and break the `check_book_html_tracking` freshness gate.
LAST_UPDATED = _BOOK_MANIFEST["last_updated"]

# Mermaid diagrams are rendered to STATIC INLINE SVG at BUILD time (see `render_mermaid_svg` below),
# NOT via a client-side runtime. This is why BOTH the web book AND the Typst PDF ship a real vector
# diagram: a PDF pipeline that never ran/awaited a client-side `mermaid.run()` would ship the raw
# ```mermaid source as code text. Build-time SVG kills that whole class (no JS-timing fragility) and is
# consistent with how every other figure in the book is inlined as SVG. The mermaid config forces SVG
# `<text>` labels (htmlLabels:false) so the SVGs carry no `<foreignObject>`, which Typst cannot draw.
# `MERMAID_CDN` is retained as an EMPTY string so the `mermaid=` chapter flag / `runtime` plumbing stays
# wired without pulling any client-side script (diagrams are already baked into the HTML as SVG).
MERMAID_CDN = ""

# Raw-mermaid-source markers — the control the author asked for. If ANY of these literal substrings
# appears in the rendered PDF text OR in a generated book/*.html code-box body, an un-rendered ```mermaid
# fence shipped (build-time SVG conversion silently failed / was bypassed). These are mermaid DIAGRAM-TYPE
# HEADER keywords + `subgraph`: a mermaid diagram ALWAYS opens with a type header (`flowchart`, `graph`,
# `erDiagram`, …), and these tokens do NOT survive into a rendered diagram's extracted TEXT (a rendered
# SVG carries the NODE LABELS, never the source syntax). Kept as one tuple so the PDF assert and the web
# book-lint share the exact same class.
#   Deliberately NOT included: the edge operator `-->`. It is ambiguous — it appears in legitimate escaped
#   prose and (as `<!-- … -->`) in HTML-comment syntax that can leak into extracted text — so it would
#   false-positive. Every un-rendered diagram still trips a header keyword above, so no detection is lost.
#   Markers are diagram-specific tokens unlikely to occur in running prose. Bare common English words
#   that happen to be mermaid headers (`pie`, `journey`, `gantt`) are omitted — the book uses none of
#   those diagram types, and including them would risk a prose false-positive in the PDF full-text scan.
# Markers of RAW mermaid source (an un-rendered ```mermaid fence leaking into the PDF text). Each must be
# diagram syntax that never occurs in English prose — so `flowchart` carries its direction, because the
# bare word "flowchart" appears legitimately in captions ("Below is a flowchart to guide…") and the loose
# "flowchart " marker false-failed the gate on prose.
MERMAID_SOURCE_MARKERS: tuple[str, ...] = (
    "flowchart TD", "flowchart LR", "flowchart TB", "flowchart RL", "flowchart BT",
    "graph TD", "graph LR", "graph TB", "graph RL", "graph BT",
    "subgraph ", "sequenceDiagram", "stateDiagram", "erDiagram", "classDiagram",
)

# SINGLE SOURCE OF TRUTH for mermaid styling: `assets/mermaid-config.json`, passed to `mmdc -c`. It
# mirrors the former `mermaid.initialize` config (Georgia serif, 20px labels, flowchart/sequence spacing)
# so every diagram renders through one config and all diagrams change together. GOTCHA: sequence diagrams
# IGNORE themeVariables.fontSize, so actor/message/note sizes are set explicitly under `sequence`.
_MERMAID_CONFIG = HERE / "assets" / "mermaid-config.json"
_MERMAID_CACHE = HERE / ".mermaid-svg-cache"   # content-hash → rendered SVG; gitignored build cache
_MMDC = HERE / "node_modules" / ".bin" / "mmdc"
# Puppeteer launch options for mmdc: the GitHub Actions Ubuntu runner (23.10+) has no usable Chromium
# sandbox, so mmdc's headless Chrome must launch with --no-sandbox or the build fails. Harmless locally.
_MMDC_PUPPETEER = HERE / "assets" / "mmdc-puppeteer.json"


def render_mermaid_svg(source: str) -> str:
    """Render a ```mermaid fence body to a self-contained inline `<svg>…</svg>` at BUILD time via
    mermaid-cli (`mmdc`, which drives the Puppeteer toolchain). Result is cached by a content hash of
    (source + config) so a rebuild that didn't touch a diagram is instant. Fails LOUD if mmdc is missing
    or a diagram fails to render — a broken diagram must never silently fall back to shipping raw source
    (the whole point of this change is that raw mermaid syntax ships NOWHERE). The returned SVG is width/
    height-stripped (like the other inline figures) so the CSS `pre.mermaid svg { max-width:100% }` rule
    still bounds it, and wrapped in `<pre class="mermaid">` so existing print/screen CSS applies unchanged.
    """
    src = source.strip()
    key = hashlib.sha256(
        (src + "\x00" + _MERMAID_CONFIG.read_text(encoding="utf-8") + "\x00idscheme-v1").encode("utf-8")
    ).hexdigest()
    # Give each rendered SVG a UNIQUE root id from its content hash. mmdc defaults to a fixed id="my-svg"
    # (+ chart-title-my-svg / chart-desc-my-svg), so two diagrams on one page collide (duplicate-ID →
    # html-validate FAILs). A per-diagram svgId namespaces the SVG's ids. (The "idscheme-v1" marker in the
    # cache key above invalidates SVGs cached under the old fixed-id scheme; bump it if the scheme changes.)
    svg_id = f"mermaid-{key[:16]}"
    cached = _MERMAID_CACHE / f"{key}.svg"
    if cached.exists():
        svg = cached.read_text(encoding="utf-8")
    else:
        if not _MMDC.exists():
            raise SystemExit(
                f"mermaid-cli (mmdc) not found at {_MMDC} — run `npm install` in book/ "
                "(mermaid fences are rendered to inline SVG at build time)")
        _MERMAID_CACHE.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            inp = pathlib.Path(td) / "diagram.mmd"
            outp = pathlib.Path(td) / "diagram.svg"
            inp.write_text(src + "\n", encoding="utf-8")
            r = subprocess.run(
                [str(_MMDC), "-i", str(inp), "-o", str(outp),
                 "-c", str(_MERMAID_CONFIG), "-p", str(_MMDC_PUPPETEER),
                 "--svgId", svg_id, "-b", "transparent", "--quiet"],
                capture_output=True, text=True,
                env={**_mermaid_env()},
            )
            if r.returncode != 0 or not outp.exists():
                raise SystemExit(
                    f"mmdc failed to render a mermaid diagram (rc={r.returncode}):\n"
                    f"{r.stderr}\n--- source ---\n{src}")
            svg = outp.read_text(encoding="utf-8")
        cached.write_text(svg, encoding="utf-8")

    # Splice only the <svg>…</svg> (drop any XML prolog / doctype), matching the inline-figure pattern.
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, flags=re.I)
    m = re.search(r"<svg\b.*</svg>", svg, re.S)
    if m:
        svg = m.group(0)
    # Drop the fixed width/height so the CSS max-width rule governs sizing (same as other inline SVGs).
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r"\1", svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r"\1", svg, count=1)
    return f'<pre class="mermaid">{svg}</pre>'


def _mermaid_env() -> dict[str, str]:
    """Environment for the `mmdc` subprocess: inherit the parent env plus a Puppeteer executable-path
    hint if one is set (mmdc's headless Chrome honors PUPPETEER_EXECUTABLE_PATH / CHROME_PATH)."""
    env = dict(os.environ)
    exe = env.get("PUPPETEER_EXECUTABLE_PATH") or env.get("CHROME_PATH")
    if exe:
        env["PUPPETEER_EXECUTABLE_PATH"] = exe
    return env

# Chapter metadata comments — ONLY the two title keys. Scoped to these keys (not a generic `[a-z-]+`)
# so the metadata strip never swallows a same-shaped directive comment that belongs in the body: a
# `<!-- figure: … -->`, an `<!-- index-def: … -->`, or an `<!-- index-example: … -->`. A generic key
# pattern here would delete those from `body_md` before the renderer ever saw them.
META_RE = re.compile(r"<!--\s*(part-title|chapter-title):\s*(.*?)\s*-->")

# Curated-index annotation tags (book/AGENTS.md §6). Placed on their own line at (or just before) the
# concept's defining / exemplifying block. The renderer turns each into a stable anchor on the FOLLOWING
# block; the index generator harvests them into curated concept entries.
INDEX_DEF_RE = re.compile(r"^<!--\s*index-def:\s*([a-z0-9-]+)\s*-->$")
INDEX_EXAMPLE_RE = re.compile(r"^<!--\s*index-example:\s*([a-z0-9-]+)\s*-->$")

# Glossary annotation — like LaTeX `\caption[SHORT]{LONG}`: a term's SHORT definition is pinned at its
# DEFINITION SITE, and the build derives BOTH the first-reference sidenote AND the generated back-Glossary
# (a `<!-- glossary-auto -->` directive) from it, so the two can never drift. `gloss:` emits a sidenote at
# the marker AND feeds the glossary; `gloss-only:` feeds the glossary WITHOUT a sidenote (for a term the
# running prose already defines in full). Single source of truth: the marker.
_GLOSS_RE = re.compile(r"^<!--\s*gloss:\s*(?P<term>.+?)\s*\|\s*(?P<def>.+?)\s*-->$")
_GLOSS_ONLY_RE = re.compile(r"^<!--\s*gloss-only:\s*(?P<term>.+?)\s*\|\s*(?P<def>.+?)\s*-->$")
_GLOSSARY: dict[str, str] = {}  # term -> short def; populated by _collect_glossary before the render loop

# Front-glossary → expansion-site wiring. The glossary page (frontmatter/0.2) is hand-authored `**Term.**`
# prose; this joins each bold term to the concept slug whose canonical `<!-- index-def: -->` anchor the build
# harvested, so the term renders as a link to where the book defines it in full. The (page, anchor) TARGET is
# taken from the harvested concept registry — never hand-written — so it CANNOT drift when a definition site
# moves; only this term→slug join is authored (the glossary's display names differ from the concept slugs,
# e.g. "The Printer"→printer-metaphor, "Skill"→skill-soft-control). A term absent here, or whose slug the book
# never index-def-tagged, stays un-linked (no fabricated target). WEB-ONLY: `_link_glossary_sites` runs on the
# rendered glossary HTML in `build()`, never on `body_md`, so the print/Typst projection is untouched.
GLOSSARY_CHAPTER_SLUG = "0.2-the-books-language"
_GLOSS_TERM_SLUGS = {
    "Model": "model",
    "Map and territory": "map-and-territory",
    "Modeling Thesis": "thesis-modeling",
    "Alignment Thesis": "thesis-alignment",
    "Governance Conversion": "governance-conversion",
    "The Printer": "printer-metaphor",
    "Churn": "churn",
    "Context Window": "context-window",
    "Foundation model": "foundation-model",
    "Agentic harness": "agentic-harness",
    "Skill": "skill-soft-control",
    "Tool": "tool-deterministic-action",
    "Fleet": "fleet",
    "One-shot Scripting": "one-shot-scripting",
    "Supervised Autonomy": "supervised-autonomy",
    "Loop engineering": "loop-engineering",
    "Governed Engineering Environment": "governed-environment",
    "Governance Mechanism": "governance-mechanism",
    "Constraint": "constraint",
    "Sensor": "sensor",
    "Validator": "validator",
    "Gate": "gate",
    "Lint": "lint",
    "Hook": "hook-hard-control",
    "Invariant": "invariant",
    "Model drift": "model-drift",
    "Drift Gate": "drift-gate",
    "Structured (model)": "structured",
    "Executable source-of-truth": "executable-source-of-truth",
    "Traceability": "traceability",
    "Pattern": "pattern",
    "The Model Zoo": "model-zoo",
    "Fidelity Validator": "fidelity-validator",
    "Provenance Layer": "provenance-layer",
}
# A rendered glossary entry: `<p><strong>Term.</strong> …`. Capture the bold lead (term text + its trailing
# period) so the whole label becomes the link, leaving `<strong>` outside the `<a>`.
_GLOSS_ENTRY_RE = re.compile(r"(<p><strong>)([^<]+?)(\.)(</strong>)")


def _link_glossary_sites(body_html: str, gloss_link_map: "dict[str, tuple[str, str]]") -> str:
    """Wrap each front-glossary bold term in a link to its canonical `index-def` anchor. `gloss_link_map` is
    {slug: (page_slug, anchor_id)} harvested from the book's `index-def` tags (never authored → drift-proof).
    A term with no map entry (unregistered slug, or no `index-def` in prose) is left un-linked. WEB-ONLY."""
    def _wrap(m: "re.Match[str]") -> str:
        term = m.group(2).strip()
        slug = _GLOSS_TERM_SLUGS.get(term)
        site = gloss_link_map.get(slug) if slug else None
        if site is None:
            return m.group(0)  # no registered expansion site — never fabricate a target
        page_slug, anchor = site
        href = html.escape(f"{page_slug}.html#{anchor}", quote=True)
        return (f'{m.group(1)}<a class="gloss-site" href="{href}">'
                f'{m.group(2)}{m.group(3)}</a>{m.group(4)}')
    return _GLOSS_ENTRY_RE.sub(_wrap, body_html)

# SINGLE SOURCE OF TRUTH for the build-time notation vocabulary — every marker-comment keyword the build
# consumes and MUST strip from the reader-visible output. The consuming regexes above/below key their
# keyword off this tuple, AND the notation-leak gate (tests/html.py: check_no_notation_leak) reads it so a
# new notation auto-extends the gate — the two can never drift (CLAUDE.md rule #33: stable-check-reads-SSOT).
# `glossary-auto` is the arg-less generated-glossary directive; the rest take a `:`-delimited argument.
MARKER_KEYWORDS = (
    "part-title", "chapter-title", "figure", "figure-iframe",
    "gloss", "gloss-only", "glossary-auto", "eq", "index-def", "index-example",
    "inset", "data", "label", "table", "point", "section-terms", "web-only",
)
# `<!-- web-only: <inline markdown> -->` — a line that belongs in the WEB book but NOT the print PDF (e.g.
# a "download the PDF" call-to-action, which would be absurd inside the PDF itself). The HTML build renders
# its argument as an ordinary paragraph; the Typst emitter drops it (the IR records it as an inert DIRECTIVE,
# so the print projection never sees it). One authored line, web-only by construction — no per-slug special
# casing. The mirror-image `<!-- print-only -->` is not needed yet; add it here if a print-only line appears.
_WEB_ONLY_RE = re.compile(r"^<!--\s*web-only:\s*(?P<content>.+?)\s*-->$")
# A comment whose first token is one of the vocabulary keywords — used to peel a marker glued to the head
# of a prose block (placement-robust stripping: an author need not remember a blank line) and, in the gate,
# to recognise a leaked marker regardless of whether it shipped escaped or raw. The trailing boundary
# (`:` or `-->` or end) keeps `glossary-auto` matchable while not matching a prose word that merely starts
# with a keyword. NOTE the `part-title`/`chapter-title` metadata is stripped earlier by META_RE; it is in
# the vocabulary so the gate still treats a leaked one as a leak.
_MARKER_KEYWORD_ALT = "|".join(re.escape(k) for k in MARKER_KEYWORDS)
_MARKER_COMMENT_RE = re.compile(rf"^<!--\s*(?:{_MARKER_KEYWORD_ALT})(?:\s*:|\s*-->)")
# `<!-- inset: <title> -->` heads a fenced code block and lifts it into a titled inset box (a real
# artifact from the system, visually set apart). It is NOT a standalone directive like `figure:` — it
# needs the fence that follows it, so it sits GLUED to the fence (no blank line) inside the same block
# and is peeled by the fenced-code branch, not by `_consume_leading_marker`. In the vocabulary SSOT so
# the notation-leak gate still treats any un-consumed / mis-placed one as a leak.
_INSET_RE = re.compile(r"^<!--\s*inset:\s*(?P<title>.+?)\s*-->$")
# A `<!-- point: <slug> | <text> -->` drain decorator (the induced canonical point of the paragraph it
# heads). Its text is AUTHORED MODEL-METADATA — invisible to the reader, consumed only by the outline
# model — so any body_md scan that reflects READER-VISIBLE prose (the occurrence index) must strip it, or a
# term that appears only in a decorator would spawn a phantom index reference. `_strip_point_decorators`
# below removes them; the outline model reads the point from the IR, never from this scrubbed prose.
_POINT_COMMENT_RE = re.compile(r"^\s*<!--\s*(?:point|section-terms):.*?-->\s*$", re.M)
# ANY HTML comment. After the block-head marker peel has consumed every recognized notation directive
# (figure / label / table / gloss / point / …), a comment still sitting in a prose-like render block is a
# STRAY authoring TODO/note — its leading token is not in the notation vocabulary. Left in, it leaks: raw
# (an invisible HTML comment) into the web page, and as VISIBLE prose into the Typst/PDF projection (which
# has no lone-comment passthrough). Both render paths strip it just before rendering. Non-greedy + DOTALL so
# a MULTI-line authoring note is matched whole. The `stray-book-comment` source lint keeps `.md` clean, so
# after a clean tree this strip has nothing to do — it is the render-time backstop, the lint the front line.
_STRAY_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _strip_point_decorators(body_md: str) -> str:
    """Remove every `<!-- point: … -->` and `<!-- section-terms: … -->` decorator line from a chapter's
    markdown. Used by the reader-visible prose scans (the occurrence index) so an authored canonical-point or
    section-terms tag never leaks into reader-facing output. Both are AUTHORED MODEL-METADATA (invisible to
    the reader, consumed only by the view-models). The renderer's block loop strips them separately (they
    render nothing); this is the text-scan twin. The name is kept for compatibility — it strips both markers."""
    return _POINT_COMMENT_RE.sub("", body_md)


def _collect_glossary(chapters: list[dict]) -> None:
    """Harvest every `gloss:` / `gloss-only:` marker across all chapter bodies into `_GLOSSARY`. Fails
    loud on a duplicate term (one definition site per term — that IS the single-source-of-truth rule)."""
    _GLOSSARY.clear()
    for c in chapters:
        for line in c["body_md"].splitlines():
            m = _GLOSS_RE.match(line.strip()) or _GLOSS_ONLY_RE.match(line.strip())
            if m:
                term = m.group("term").strip()
                if term in _GLOSSARY:
                    raise SystemExit(f"duplicate glossary definition for '{term}' — one gloss marker per term")
                _GLOSSARY[term] = m.group("def").strip()

# Part number → the source subdirectory that holds its chapters. Front matter is part 0, the
# five numbered parts are 1–5 (Part 4 is the Model Zoo), back matter is part 6. Appendix parts follow.
_PART_DIRS = {
    0: "frontmatter",
    1: "part1",
    2: "part2",
    3: "part3",
    4: "part4",
    5: "part5",
    6: "backmatter",
}

# Part number → its display title (mirrors the `part-title` metadata; kept here so a part with no
# chapters still names correctly, and so the TOC/index label is authoritative from one place).
_PART_TITLES = {
    0: "Front Matter",
    1: "The Mindset",
    2: "The Governed Engineering Environment",
    3: "The Model Zoo",
    4: "Putting It to Work",
    5: "A MAGE Case Study",
    6: "Back Matter",
}

# Per-Part epigraph rendered at the opener of the first chapter in each numbered Part. Each is a
# (quote, attribution) pair. The Macbeth line is verbatim from the source memoir; the Context and
# Governed-Environment openers use a regulatory line and the book's own thesis, and the Putting-It-
# to-Work opener the working method of that part (candidates a human editor may swap). The
# Ecclesiastes line that once opened Part 5 now lands only in the conclusion, where it sets up the
# closing "machines search, not wisdom" — kept to one appearance to avoid the reader meeting it twice.
# The book carries ONE epigraph — the Ecclesiastes verse at the opening of the Conclusion, placed
# inline there. The per-Part opener epigraphs were removed (author's call); this map stays empty so
# `_epigraph_html` is a no-op for every Part.
_PART_EPIGRAPHS: dict[int, tuple[str, str]] = {}

_PART_CHAP_RE = re.compile(r"^(\d+)\.(\d+)-")


def _load_metrics() -> dict[str, str]:
    """Read `data/metrics.json` (the single source for the book's headline numbers). Keys prefixed
    with `_` are notes, not tokens; everything else is a `{{key}}` substitution."""
    path = HERE / "data" / "metrics.json"
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {k: str(v) for k, v in raw.items() if not k.startswith("_")}


def _apply_metrics(md: str, metrics: dict[str, str]) -> str:
    """Substitute every `{{token}}` in the chapter prose with its metrics value. An unknown token
    fails loud — a mistyped placeholder should stop the build, not ship `{{typo}}` to the reader."""
    def repl(m: "re.Match[str]") -> str:
        key = m.group(1).strip()
        if key not in metrics:
            raise SystemExit(f"metrics token {{{{{key}}}}} has no value in data/metrics.json")
        return metrics[key]
    return re.sub(r"\{\{\s*([a-z0-9_]+)\s*\}\}", repl, md)


def _load_data_claims() -> dict[str, dict]:
    """Read `data/data-claims.json` — the single source of truth for the book's governed data
    cross-references. Keys prefixed with `_` are notes, not claims. Each claim maps a slug to
    {source, anchor, holds, status, gloss}. Modelled on `_load_metrics` / `data/metrics.json`: the
    `[data: <slug>]` marker resolves against this manifest, and an unknown slug fails the build loud."""
    path = HERE / "data" / "data-claims.json"
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def _apply_data_claims(md: str, claims: dict[str, dict], chapter_titles: dict[str, str]) -> str:
    """Substitute every `[data: <slug>]` marker with a footnote-style cross-ref into the chapter that
    reports the datum: "For the data, see [<Chapter Title> →](<source>.html#<anchor>)" — appending
    " (preliminary)" when the claim's status is preliminary or partial. An unknown slug fails the build
    LOUD (like an unknown `{{token}}`) — a rotted reference must stop the build, not ship a dead cross-ref.
    The `chapter_titles` map (slug -> title) is the build's own discovery, so the link text can never
    drift from the source chapter's real title. Emits a markdown link that `inline()` then renders to <a>."""
    def repl(m: "re.Match[str]") -> str:
        slug = m.group(1).strip()
        if slug not in claims:
            raise SystemExit(f"data marker [data: {slug}] has no entry in data/data-claims.json")
        entry = claims[slug]
        source = entry["source"]
        anchor = entry.get("anchor", "")
        title = chapter_titles.get(source, source)
        href = f"{source}.html" + (f"#{anchor}" if anchor else "")
        prelim = " (preliminary)" if entry.get("status") in ("preliminary", "partial") else ""
        return f"For the data, see [{title} →]({href}){prelim}"
    return re.sub(r"\[data:\s*([a-z0-9-]+)\s*\]", repl, md)


def _apply_part_refs(md: str) -> str:
    """Substitute `{{part:N}}` → `Part N (<title>)`, the title read from `_PART_TITLES` at build time. A
    prose reference to a Part stays in sync with its title: rename the Part once in `_PART_TITLES` and
    every `{{part:N}}` updates, so a rename can never strand a stale "(The Old Title)". Fails loud on a
    bad N (a reference to a Part that does not exist)."""
    def repl(m: "re.Match[str]") -> str:
        n = int(m.group(1))
        if n not in _PART_TITLES:
            raise SystemExit(f"{{{{part:{n}}}}} references a Part not in _PART_TITLES")
        return f"Part {n} ({_PART_TITLES[n]})"
    return re.sub(r"\{\{\s*part:(\d+)\s*\}\}", repl, md)


# `{{dt:<key>}}` — derive a design-system NAME from the token SSOT so the colophon's prose (faces, accent)
# follows book-models/design-tokens.json instead of hardcoding "Fraunces"/"burnt umber". Colon-namespaced
# like {{part:N}}, so _apply_metrics (which matches [a-z0-9_]+ only, no colon) never touches it. Unknown
# key fails loud — a mistyped face stops the build, never ships {{dt:typo}} to the reader.
_DT_TOKEN_RE = re.compile(r"\{\{\s*dt:([a-z0-9_]+)\s*\}\}")


def _apply_design_tokens(md: str) -> str:
    resolvers = {
        "font_display": lambda: _TOKENS.type["display"]["family"],
        "font_body":    lambda: _TOKENS.type["body"]["family"],
        "font_mono":    lambda: _TOKENS.type["mono"]["family"],
        "accent_name":  lambda: _TOKENS.accent_name,
    }

    def repl(m: "re.Match[str]") -> str:
        key = m.group(1)
        if key not in resolvers:
            raise SystemExit(f"design-token marker {{{{dt:{key}}}}} — unknown key "
                             f"(known: {', '.join(sorted(resolvers))})")
        return resolvers[key]()
    return _DT_TOKEN_RE.sub(repl, md)


# `[gh:<repo-relative-path>]` or `[gh:<path>|<label>]` → a link to the file on GitHub, deriving owner/repo/
# branch from repo-metadata.json (the same SSOT catalog.py + the citation Scholar-meta read). Label defaults
# to the path. Emits a markdown link string that inline() renders to <a>; the offline path-exists guarantee
# is the check_gh_refs gate in catalog.py validate, so this stays a pure string transform (fail-loud on a
# rotted path lives in ONE place — the gate — not duplicated here).
_REPO_META = json.loads(
    (ROOT / "book-models" / "repo-metadata.json").read_text(encoding="utf-8"))
_GH_BLOB_BASE = (f"https://github.com/{_REPO_META['owner']}/{_REPO_META['repo']}"
                 f"/blob/{_REPO_META.get('default_branch', 'main')}")
_GH_MARKER_RE = re.compile(r"\[gh:\s*([^\]|]+?)\s*(?:\|\s*([^\]]*?)\s*)?\]")


def _apply_gh_refs(md: str) -> str:
    def repl(m: "re.Match[str]") -> str:
        path = m.group(1)
        label = (m.group(2) or path).strip()
        return f"[{label}]({_GH_BLOB_BASE}/{path})"
    return _GH_MARKER_RE.sub(repl, md)


# ─────────────────────────── Bibliography & citations (references.bib → citations.json → two surfaces) ──
# The bib is the single source of truth; Chicago is rendered ONCE by render_citations.py through Typst and
# committed to book/data/citations.json, which BOTH surfaces consume so they cannot drift. Design:
# book/_design/bibliography-subsystem-260801.md. This module holds the SSOT marker vocabulary (the
# CITE-RESOLVE / CITE-FRESH gates import these), the chapter-scoped numbering pre-pass, and the HTML
# projections (numeric sidebar citations, symbolic editorial notes, per-chapter Works Cited).

# Deployed Pages root — read from the same repo-metadata SSOT catalog.py uses, so the Scholar meta URLs
# (citation_fulltext_html_url / citation_pdf_url) can never drift from the site's real address.
_PAGES_URL = json.loads(
    (ROOT / "book-models" / "repo-metadata.json").read_text(encoding="utf-8"))["pages_url"].rstrip("/")
_PUB_YEAR = (re.match(r"\d{4}", _BOOK_MANIFEST.get("copyright_years", "")) or [""])[0] or "2026"

# The inline citation + note markers — they join the existing inline bracket family (`[ref:]`, `[data:]`,
# `[[…]]`). SSOT for the renderer AND the CITE-RESOLVE gate (which imports these), so the gate can never
# drift from what the build parses. A `[note:]` body must not contain a `]` (the non-greedy stop).
_CITE_MARKER_RE = re.compile(r"\[cite:\s*([^\]]+?)\s*\]")
_NOTE_MARKER_RE = re.compile(r"\[note:\s*(.+?)\s*\]", re.S)
# Editorial-note glyph cycle: `* † ‡ § ‖ ¶`, then doubled (`** †† …`). DISJOINT from the citation glyph set
# (digits) by construction — the CITE-SYMBOLOGY gate asserts it. `_note_glyph(i)` is 0-indexed.
_NOTE_GLYPHS = ("*", "†", "‡", "§", "‖", "¶")

# The rendered Chicago strings (per key: note_html / works_cited_html / bib_html / csl), loaded once from
# the committed citations.json. Empty until _load_citations() runs (start of build()).
_CITATIONS: dict[str, dict] = {}
# Per-chapter citation state, set by _number_citations() before a chapter renders and read inside inline()
# — the same module-global pattern the glossary (`_GLOSSARY`) uses to thread chapter state into inline().
_CITE_STATE: dict = {"ns": "", "numbers": {}, "order": [], "notes_emitted": set(), "note_i": 0}


def _load_citations() -> dict[str, dict]:
    """Read book/data/citations.json (the committed render of references.bib) into `_CITATIONS`. Stdlib
    json only — this keeps catalog.py's clone-and-run promise (the Typst render is a dev/CI-time step; the
    build only ever reads the JSON). A missing file leaves the map empty (a tree with no citations still
    builds); the CITE-FRESH gate is what fails loud on a STALE file."""
    path = HERE / "data" / "citations.json"
    _CITATIONS.clear()
    if path.is_file():
        _CITATIONS.update(json.loads(path.read_text(encoding="utf-8")).get("citations", {}))
    return _CITATIONS


def parse_cite_spec(spec: str) -> list[tuple[str, str | None]]:
    """A `[cite: …]` payload → [(key, locator|None), …]. Multiple works are `;`-separated; an optional
    locator follows a key after the first `,`: `winters2020, 42; gof1994` → [('winters2020','42'),
    ('gof1994', None)]."""
    out: list[tuple[str, str | None]] = []
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        if "," in part:
            key, loc = part.split(",", 1)
            out.append((key.strip(), loc.strip()))
        else:
            out.append((part, None))
    return out


def iter_cite_keys(text: str) -> list[str]:
    """Every cite key in `text`, in first-appearance document order (repeats included). The SSOT scan the
    numbering pre-pass, the end-of-book Bibliography union, and the CITE-RESOLVE gate all share."""
    keys: list[str] = []
    for m in _CITE_MARKER_RE.finditer(text):
        keys.extend(key for key, _loc in parse_cite_spec(m.group(1)))
    return keys


def _cite_ns(slug: str) -> str:
    """A slug → a citation id namespace (`wc-<ns>-N`), sanitised to the `[a-z0-9-]` an HTML id / CSS
    selector accepts (the chapter slug carries dots: `0.1-preface` → `0-1-preface`)."""
    return re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")


def _number_citations(slug: str, body_md: str) -> None:
    """Set `_CITE_STATE` for one chapter: assign each DISTINCT cite key the next integer in first-reference
    order (a repeat reuses its number), and reset the editorial-note counter. Runs before md_to_html so
    inline() can look the numbers up. This is what makes the sidebar number equal the Works-Cited entry
    number (BIB-4 mirror) — both read this one ordering."""
    numbers: dict[str, int] = {}
    order: list[str] = []
    for key in iter_cite_keys(body_md):
        if key not in numbers:
            numbers[key] = len(order) + 1
            order.append(key)
    _CITE_STATE.clear()
    _CITE_STATE.update({"ns": _cite_ns(slug), "numbers": numbers, "order": order,
                        "notes_emitted": set(), "note_i": 0})


def _note_glyph(i: int) -> str:
    """The i-th editorial-note glyph (0-indexed): `* † ‡ § ‖ ¶`, doubled after six (`** †† …`)."""
    return _NOTE_GLYPHS[i % len(_NOTE_GLYPHS)] * (i // len(_NOTE_GLYPHS) + 1)


def _ensure_citations() -> None:
    """Populate `_CITATIONS` if empty — so ANY render path (a per-body float/word-count pass, the IR
    render-fidelity check, a direct md_to_html/inline call) resolves cite markers, not only build(), which
    loads them explicitly. Idempotent; a missing citations.json leaves it empty (CITE-FRESH fails loud)."""
    if not _CITATIONS:
        _load_citations()


def _render_cite_marker(spec: str) -> str:
    """Render one `[cite: …]` payload → numeric superscript(s) linked to the chapter's Works Cited, each
    followed (first occurrence of the key only) by a right-gutter citation NOTE carrying the Chicago
    note-form string. Fails loud on a key absent from citations.json OR unnumbered (a cite outside a
    numbered chapter) — a dead citation must stop the build, like an unknown `{{token}}` / `[data:]`."""
    _ensure_citations()
    ns = _CITE_STATE["ns"]
    numbers = _CITE_STATE["numbers"]
    emitted = _CITE_STATE["notes_emitted"]
    out: list[str] = []
    for key, loc in parse_cite_spec(spec):
        if key not in _CITATIONS:
            raise SystemExit(f"[cite: {key}] names no entry in references.bib / citations.json")
        if key not in numbers:
            # The main chapter loop pre-numbers every key via _number_citations, so this only fires in an
            # AUXILIARY render pass (float collection / word count) whose HTML is discarded — number on
            # demand so those passes never crash. A genuinely unknown key already failed above.
            numbers[key] = len(_CITE_STATE["order"]) + 1
            _CITE_STATE["order"].append(key)
        n = numbers[key]
        label = html.escape(f"citation {n}", quote=True)
        sup = f'<sup class="cite-ref"><a href="#wc-{ns}-{n}" aria-label="{label}">{n}</a></sup>'
        note = ""
        if key not in emitted:
            emitted.add(key)
            loc_txt = f", {html.escape(loc)}" if loc else ""
            note = (f'<span class="cite-note"><span class="cn-mark">{n}.</span> '
                    f'{_CITATIONS[key]["note_html"]}{loc_txt}</span>')
        out.append(sup + note)
    return "".join(out)


def _render_note_marker(escaped_text: str) -> str:
    """Render one `[note: …]` → a symbolic superscript (`*†‡§…`) + a right-gutter editorial note. `escaped_text`
    is already HTML-escaped by inline() (a note body is plain editorial text, no inner markdown). The sup
    carries an aria-label so a screen reader announces "note N", not a bare symbol (decision #3)."""
    i = _CITE_STATE["note_i"]
    _CITE_STATE["note_i"] = i + 1
    glyph = html.escape(_note_glyph(i))
    label = html.escape(f"note {i + 1}", quote=True)
    # role="doc-noteref" (DPUB-ARIA: a mark referencing a note) — a bare <sup> is generic, and
    # html-validate rejects aria-label on a generic element (aria-label-misuse); the role both
    # legitimizes the name AND says what the mark is.
    return (f'<sup class="note-ref" role="doc-noteref" aria-label="{label}">{glyph}</sup>'
            f'<span class="editorial-note"><span class="cn-mark">{glyph}</span> {escaped_text}</span>')


def works_cited_section() -> str:
    """The current chapter's Works Cited — a numbered list (Chicago notes; decision #1) in first-reference
    order, so entry N is the work cited by superscript N (BIB-4). Empty string when the chapter cites
    nothing. The `<ol>` numbering equals the entry ids (`wc-<ns>-N`) the superscripts link to."""
    order = _CITE_STATE.get("order", [])
    if not order:
        return ""
    ns = _CITE_STATE["ns"]
    items = "".join(
        f'<li id="wc-{ns}-{n}">{_CITATIONS[key]["works_cited_html"]}</li>'
        for n, key in enumerate(order, 1)
    )
    return (f'<section class="works-cited" aria-labelledby="wc-{ns}-h">'
            f'<h2 id="wc-{ns}-h" class="wc-h">Works Cited</h2>'
            f'<ol class="wc-list">{items}</ol></section>')


def _highwire_reference(csl: dict) -> str:
    """One cited work → Google Scholar's compressed `citation_reference` form
    (`citation_title=…;citation_author=…;citation_publication_date=…`), a repeated `citation_author=` per
    author. Built straight from the key's CSL block — this is what lets Scholar build the citation graph OUT
    of the book (§6, BIB-8)."""
    parts = [f"citation_title={csl.get('title', '')}"]
    for a in csl.get("author", []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            parts.append(f"citation_author={name}")
    if csl.get("year"):
        parts.append(f"citation_publication_date={csl['year']}")
    return ";".join(parts)


def _chapter_head_meta(chapter: dict, cited_keys: list[str]) -> str:
    """The highwire_press `<meta>` block for a chapter page's <head> (§6, BIB-8): the chapter as a book
    section (citation_book_title marks it), the book author + date, the canonical HTML + PDF URLs, and one
    `citation_reference` per work cited on the page. Every content attribute is escaped."""
    def meta(name: str, content: str) -> str:
        return f'<meta name="{name}" content="{html.escape(content, quote=True)}">'
    tags = [
        meta("citation_title", chapter["chapter_title"]),
        meta("citation_author", _BOOK_MANIFEST["author"]),
        meta("citation_book_title", _BOOK_MANIFEST["title"]),
        meta("citation_publication_date", _PUB_YEAR),
        meta("citation_fulltext_html_url", f"{_PAGES_URL}/book/{chapter['slug']}.html"),
        meta("citation_pdf_url", f"{_PAGES_URL}/book/{_PDF_FILENAME}"),
    ]
    tags += [meta("citation_reference", _highwire_reference(_CITATIONS[k]["csl"])) for k in cited_keys]
    return "".join(tags)


def _bib_sort_key(key: str) -> tuple[str, str]:
    """Alphabetical bibliography order: by first author's surname, then title (Chicago). A corporate/no-
    author work sorts by title."""
    csl = _CITATIONS[key]["csl"]
    authors = csl.get("author", [])
    fam = (authors[0].get("family", "") if authors else csl.get("title", "")).lower()
    return (fam, csl.get("title", "").lower())


def build_bibliography_page(chapters: list[dict], nav_last: str) -> str:
    """The end-of-book Bibliography — the alphabetical union (by author surname) of every work cited across
    all chapters, deduplicated, rendered from the same citations.json strings as the per-chapter Works
    Cited; ordering is the only difference (§5). Also emits one `citation_reference` per entry so Scholar
    gets the whole reference list on one page (§6). Always produced (a tree with no cites yields the
    'no works cited yet' note) so the tracked-HTML gate's expected set stays stable."""
    all_keys = sorted({k for c in chapters for k in iter_cite_keys(c["body_md"])}, key=_bib_sort_key)
    if all_keys:
        items = "".join(f'<li id="bib-{k}">{_CITATIONS[k]["bib_html"]}</li>' for k in all_keys)
        body = f'<ul class="bib-list">{items}</ul>'
    else:
        body = '<p class="bib-empty">No works are cited yet.</p>'
    head_meta = "".join(
        f'<meta name="citation_reference" content="{html.escape(_highwire_reference(_CITATIONS[k]["csl"]), quote=True)}">'
        for k in all_keys)
    provenance = "<!-- GENERATED by book/build_book_html.py (build_bibliography_page) — DO NOT EDIT. -->"
    header = ('<header class="chap"><div class="kicker">Back Matter</div>'
              '<h1>Bibliography</h1></header>')
    intro = ('<p>Every work cited in this book, in one alphabetical list. Each chapter also carries its own '
             'numbered <em>Works Cited</em>; this is their union.</p>')
    nav_bar = _static_nav_html(
        "Bibliography",
        back_extra=[("« Previous chapter", f"{nav_last}.html", "Previous chapter — back matter")],
    )
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    main = header + intro + f'<section class="bibliography" aria-label="Bibliography">{body}</section>' + nav_bar + foot
    toc = toc_html(chapters, None)
    return page("Bibliography · Model-Based Agentic Software Engineering", toc, main,
                provenance=provenance, head_meta=head_meta)


def parse_chapter(path: pathlib.Path, part: int, chapter: int, metrics: dict[str, str]) -> dict:
    text = _apply_gh_refs(_apply_design_tokens(
        _apply_part_refs(_apply_metrics(path.read_text(encoding="utf-8"), metrics))))
    meta = {k: v for k, v in META_RE.findall(text)}
    body = META_RE.sub("", text).strip()
    # Drop the leading H1 (# Chapter …) — we render it from metadata in the header.
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
    return {
        "slug": path.stem,
        "part": part,
        "part_title": meta.get("part-title", _PART_TITLES.get(part, "")),
        "chapter": chapter,
        "chapter_title": meta.get("chapter-title", path.stem),
        # Redirect any authored link to a now-dropped (non-flagship) appendix page to the live web entry, so
        # a main-narrative cross-reference to a mechanism the print appendix omits stays resolvable.
        "body_md": _redirect_dropped_appendix_links("\n".join(lines).strip()),
        "is_matter": part in (0, 6),  # front / back matter — no "Chapter N" kicker
        # Pull the Mermaid runtime onto this page only if the chapter carries a ```mermaid fence
        # (the Model Zoo chapters reuse the appendix Structure diagrams; other chapters do not).
        "mermaid": "```mermaid" in body,
    }


def _discover_chapters(metrics: dict[str, str]) -> list[dict]:
    """Walk the Part/Chapter filesystem hierarchy → an ordered list of chapter records. Part number
    and chapter number come from the PATH (the `part<N>/` dir and the `<N>.<M>-slug.md` name); the
    titles come from each file's metadata. Ordered by (part, chapter)."""
    found: list[dict] = []
    for part, subdir in _PART_DIRS.items():
        d = HERE / subdir
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            m = _PART_CHAP_RE.match(p.name)
            if not m:
                continue  # not a chapter file (e.g. a stray README)
            file_part, chapter = int(m.group(1)), int(m.group(2))
            # The filename's leading part digit must match its directory's part (catch a misfiled chapter).
            if file_part != part:
                raise SystemExit(
                    f"chapter {p} names part {file_part} but sits in {subdir} (part {part})")
            found.append(parse_chapter(p, part, chapter, metrics))
    found.sort(key=lambda c: (c["part"], c["chapter"]))
    # Derive the sequential chapter number — single source of truth is the filesystem order over the
    # numbered body Parts (1-5). Front/back matter (is_matter) is unnumbered and skipped. This replaces
    # the old hand-typed "# Chapter N ·" H1 (which the build drops anyway), so a chapter number can never
    # drift again: renumbering is just moving a file.
    seq = 0
    for c in found:
        if not c.get("is_matter"):
            seq += 1
            c["seq"] = seq
    # Resolve `[data: <slug>]` cross-ref markers now that every chapter's title is known — the link text
    # is the SOURCE chapter's real title (the build's own discovery), so a cross-ref can never carry a
    # stale title. Runs after discovery (not in parse_chapter) because it needs the whole slug->title map.
    claims = _load_data_claims()
    if claims:
        titles = {c["slug"]: c["chapter_title"] for c in found}
        for c in found:
            c["body_md"] = _apply_data_claims(c["body_md"], claims, titles)
    return found


def _abbr_cite(m: "re.Match[str]") -> str:
    """A `[[slug|text]]` / `[[slug]]` abstraction citation from a catalogue entry → a link into the
    catalogue's rendered abstractions glossary (one level up from book/)."""
    slug = m.group(1).strip()
    text = (m.group(2) or slug).strip()
    return f'<a href="../ABSTRACTIONS.html#{html.escape(slug, quote=True)}">{html.escape(text, quote=False)}</a>'


def inline(s: str) -> str:
    # Intra-word emphasis: `[+X+]` → <em>X</em>. Stashed BEFORE escaping so the emitted <em> survives.
    # The italic `*…*` pass below is word-boundary-only by design and cannot emphasize letters *inside*
    # a word — e.g. the acronym-deriving M / Ag / E in "Model-Based Agentic Software Engineering" (MAGE).
    em_spans: list[str] = []

    def _stash_em(m: "re.Match[str]") -> str:
        em_spans.append(html.escape(m.group(1), quote=False))
        return f"\x00EM{len(em_spans) - 1}\x00"

    s = re.sub(r"\[\+(.+?)\+\]", _stash_em, s)
    s = html.escape(s, quote=False)
    # Inline code spans (`text`) first — their content is code, so no bold/italic/link pass should
    # run inside them. Stash each span behind a placeholder, run the markdown passes, then restore.
    # This is what lets `MAJOR`, `[]P`, and `Service` render as <code> instead of literal backticks.
    code_spans: list[str] = []

    def _stash(m: "re.Match[str]") -> str:
        code_spans.append(m.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    s = re.sub(r"`([^`]+)`", _stash, s)
    # Abstraction citations (`[[slug|text]]`) → links into the catalogue glossary. After escaping (the
    # brackets survive escaping); before the markdown-link pass so the emitted <a> is left intact.
    s = re.sub(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]", _abbr_cite, s)
    # Inline citation / editorial-note markers render to raw HTML (superscript + gutter note) that the
    # bold/italic passes below must not touch, so stash each behind a placeholder and restore at the end —
    # the same shield the code spans use. Both read the chapter-scoped `_CITE_STATE` set before this block.
    cite_spans: list[str] = []

    def _stash_cite(frag: str) -> str:
        cite_spans.append(frag)
        return f"\x00CITE{len(cite_spans) - 1}\x00"

    s = _CITE_MARKER_RE.sub(lambda m: _stash_cite(_render_cite_marker(m.group(1))), s)
    s = _NOTE_MARKER_RE.sub(lambda m: _stash_cite(_render_note_marker(m.group(1).strip())), s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # Bold: non-greedy so an inner *italic* span survives (e.g. `**a typed *derived* edge**`); the
    # italic pass below then converts the inner single-asterisk pair. (`[^*]+` used to fail whenever a
    # bold span wrapped an italic one, leaking a literal `**` into the page.)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    # Restore the stashed code spans as <code> (their content is already HTML-escaped).
    s = re.sub(r"\x00CODE(\d+)\x00", lambda m: f"<code>{code_spans[int(m.group(1))]}</code>", s)
    # Restore the stashed intra-word emphasis spans (content already HTML-escaped).
    s = re.sub(r"\x00EM(\d+)\x00", lambda m: f"<em>{em_spans[int(m.group(1))]}</em>", s)
    # Restore the stashed citation / editorial-note HTML (raw superscript + gutter note, shielded above).
    s = re.sub(r"\x00CITE(\d+)\x00", lambda m: cite_spans[int(m.group(1))], s)
    return s


def _figure_block(comment: str) -> str:
    """Render a `<!-- figure: <path> | <caption> -->` directive into a <figure>.

    <path> is relative to book/ (this dir). A `.svg` asset is INLINED (its own <title>/<desc>/
    aria-* survive, and there is no external request that can 404); any other extension is
    wrapped in <img alt="<caption>">. Fails loud if the asset is missing — a broken figure
    directive should stop the build, not ship a silent gap.
    """
    inner = comment[len("<!--"):-len("-->")].strip()
    spec = inner[len("figure:"):].strip()
    if "|" in spec:
        rel, caption = (s.strip() for s in spec.split("|", 1))
    else:
        rel, caption = spec, ""
    asset = HERE / rel
    if not asset.is_file():
        raise SystemExit(f"figure directive: asset not found: {asset}")
    cap_html = _caption_el("figcaption", caption) if caption else ""
    if asset.suffix.lower() == ".svg":
        svg = asset.read_text(encoding="utf-8")
        # Strip an XML prolog / leading comment so only the <svg>…</svg> is spliced inline.
        svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
        m = re.search(r"<svg\b.*</svg>", svg, re.S)
        svg = m.group(0) if m else svg
        # Neutralize the intrinsic width/height so the viewBox drives responsive scaling; CSS caps it.
        svg = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r"\1", svg, count=1)
        svg = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r"\1", svg, count=1)
        return f'<figure class="book-figure">{svg}{cap_html}</figure>'
    alt = html.escape((_split_caption_md(caption)[0] if caption else "") or asset.stem, quote=True)
    src = html.escape(rel, quote=True)
    return f'<figure class="book-figure"><img src="{src}" alt="{alt}">{cap_html}</figure>'


def _figure_iframe_block(comment: str) -> str:
    """Render a `<!-- figure-iframe: <path> | <caption> | <a11y-title> -->` directive into a <figure> with
    an <iframe> preview and a through-link. Used to surface a self-contained catalogue figure page (whose
    internal links are book-relative) live and interactive, without inlining its markup — inlining would
    splice another document's styles/scripts and its links resolve only when loaded as its own document.
    The iframe loads the figure from `book/`, so the figure's book-relative links resolve inside it. The
    <iframe> carries a required `title` for accessibility; the caption repeats it visibly with a link out.
    Fails loud if the target page is missing so a mistyped path stops the build."""
    inner = comment[len("<!--"):-len("-->")].strip()
    spec = inner[len("figure-iframe:"):].strip()
    fields = [s.strip() for s in spec.split("|")]
    rel = fields[0] if fields else ""
    caption = fields[1] if len(fields) > 1 else ""
    a11y_title = fields[2] if len(fields) > 2 else caption
    target = HERE / rel
    if not target.is_file():
        raise SystemExit(f"figure-iframe directive: page not found: {target}")
    src = html.escape(rel, quote=True)
    title = html.escape(a11y_title or "Embedded figure", quote=True)
    cap = (f'<figcaption>{inline(caption)} '
           f'<a href="{src}">Open the full-size map ›</a></figcaption>') if caption else ""
    return (
        '<figure class="book-figure catalogue-embed">'
        f'<iframe src="{src}" title="{title}" loading="lazy"></iframe>'
        f"{cap}</figure>"
    )


_HEADING_ANCHOR_RE = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")


def _heading_anchor(text: str) -> tuple[str, str]:
    """Split a trailing `{#slug}` id-anchor off a heading's text. Returns (visible_text, id_attr) where
    id_attr is ` id="slug"` (already escaped) or "". The appendix uses this so its per-pattern `<h2>`
    carries a stable id the rewired mechanism-map figure deep-links to."""
    m = _HEADING_ANCHOR_RE.search(text)
    if not m:
        return text, ""
    slug = m.group(1)
    return text[: m.start()].rstrip(), f' id="{html.escape(slug, quote=True)}"'


_ROLE_KICKER_RE = re.compile(r"^\s*\[role:\s*([^\]]+?)\s*\]\s*")


def _role_kicker(text: str) -> tuple[str, str]:
    """Split a leading `[role: Name]` kicker off a step heading. Returns (kicker_html, rest) where
    kicker_html is a styled accent `<span class="role-kick">` (or "" if none). The 5.4 staircase uses
    this so each step heading carries the engineer's climbing title — co-coder, QA, HR, org designer,
    architect, director — in the same small-caps accent register as the chapter kicker."""
    m = _ROLE_KICKER_RE.match(text)
    if not m:
        return "", text
    label = html.escape(m.group(1), quote=False)
    return f'<span class="role-kick">{label}</span> ', text[m.end():]


def _split_blocks(md: str) -> list[str]:
    """Split markdown into blank-line-delimited blocks, but keep a fenced code block (```` ``` ````…```` ``` ````)
    intact even when it contains blank lines. A naive blank-line split shatters a code block that has an
    internal blank line, so its later lines get parsed as prose (and e.g. `[x](y)` in the code turns into a
    stray link). This scanner tracks fence state so a fence's blank lines never break the block."""
    blocks: list[str] = []
    cur: list[str] = []
    in_fence = False
    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            cur.append(line)
            in_fence = not in_fence
            continue
        if not in_fence and not stripped:
            if cur:
                blocks.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def _inject_anchor_id(block_html: str, anchor_id: str) -> str:
    """Add `id="<anchor_id>"` to the first HTML tag of a rendered block, so a curated-index tag deep-links
    the concept's defining / exemplifying block. If the tag already carries an id (a heading with a
    `{#slug}` anchor), prepend an empty `<span id=…>` marker instead of clobbering the existing id."""
    m = re.match(r"\s*<([a-zA-Z0-9]+)((?:\s[^>]*)?)>", block_html)
    if m and " id=" not in m.group(2):
        idx = m.end(1)
        return block_html[:idx] + f' id="{html.escape(anchor_id, quote=True)}"' + block_html[idx:]
    # First tag already has an id (or no leading tag) — front the block with an anchor-only span.
    return f'<span id="{html.escape(anchor_id, quote=True)}"></span>' + block_html


# A THESIS blockquote leads with a bold `The <Name> Thesis.` label — authored as
# `> **The <Name> Thesis.** <statement>`, rendered into `<p><strong>The … Thesis.</strong> …`. Matched on
# the rendered inner HTML (a leading `<p>` whose first `<strong>` ends in the literal word `Thesis.`), so it
# is told apart from an ordinary `> **Term.**` definition callout (which stays a light sidenote).
_IS_THESIS_LEAD_RE = re.compile(r"^\s*<p>\s*<strong>\s*The\b.*?\bThesis\.\s*</strong>", re.S)

# A DEFINITION blockquote leads with a bold `<Term>.` label (`> **Model.** …`) and is armed by an
# immediately-preceding `<!-- index-def: <slug> -->` for one of the four core terms — the vocabulary the
# theses ride on — plus `structured`, the adjective riding on the model definition. Rendered into the blue
# `def-box` (mirrors the thesis-box mechanism). The index-def context is the discriminator; this regex
# confirms the bold-lead shape.
_DEF_SLUGS = frozenset({"model", "agent", "engineering", "software-engineering", "structured"})
_IS_DEF_LEAD_RE = re.compile(r"^\s*<p>\s*<strong>", re.S)

# A DEFINITION sidenote is the light (non-core-term) cousin: a `> **Term.** …` aside whose bold lead ENDS
# in a period (`> **Churn.** …`, `> **Lint.** …`), authored into `<p><strong>Churn.</strong> …`. It carries
# a `def-inset` modifier so its definition body italicises while the bold Term stays upright. The trailing
# period inside the bold is the discriminator: it tells a `**Term.**` glossary/aside label apart from an
# em-led footnote (`> *A footnote…*`, no <strong> lead) and a plain sidenote (no bold lead), both of which
# keep their as-authored rendering. Theses and core-term def-boxes are classified earlier, so never reach it.
_IS_DEFN_SIDENOTE_LEAD_RE = re.compile(r"^\s*<p>\s*<strong>[^<]*\.\s*</strong>", re.S)


_BOOK_IR_MOD = None  # cached `book_ir` module handle (lazy — book_ir imports THIS module as its tokenizer SSOT)


def _book_ir():
    """Return the `book_ir` module, imported lazily to break the SSOT import cycle (book_ir imports this
    module for the shared tokenizer, so this module must NOT import book_ir at module load). The renderer's
    block-classification dispatch is single-sourced through it — one classifier feeds both render and analysis."""
    global _BOOK_IR_MOD
    if _BOOK_IR_MOD is None:
        import book_ir
        _BOOK_IR_MOD = book_ir
    return _BOOK_IR_MOD


def md_to_html(md: str, anchor_map: dict[tuple[str, str, int], str] | None = None,
               section_prefix: str | None = None) -> str:
    """Convert the markdown subset the chapters use into HTML.

    `anchor_map` (optional) maps `(concept-slug, "def"|"ex", occurrence-on-this-page)` → the anchor id the
    curated index links to. When a `<!-- index-def: … -->` / `<!-- index-example: … -->` tag is met, its
    anchor is attached to the FOLLOWING rendered block (per book/AGENTS.md §6). Occurrences are counted
    per (slug, kind) in reading order to match `_harvest_concept_tags`.

    `section_prefix` (optional, e.g. "1.1") is the body chapter's `part.chapter` id. When set, each `## `
    (section) heading's visible text is stamped with a DISPLAY-ONLY `part.chapter.N` number (N = the
    section's 1-based order within the chapter). `None` (the default) leaves headings unnumbered — the
    blockquote recursion, floats pass, and word-count all call unprefixed, so only the per-chapter body
    build numbers. The number never alters a heading's `{#slug}` id anchor (see `_render_heading`)."""
    _ir = _book_ir()                        # the typed IR — the single classifier for the content dispatch
    out: list[str] = []
    blocks = _split_blocks(md)
    pending_anchors: list[str] = []         # anchor id(s) to attach to the next content block
    pending_table_caption: list[str] = []   # a `<!-- table: … -->` caption armed for the next table
    pending_label: list[str] = []           # a `<!-- label: … -->` cross-ref key armed for the next float
    pending_def: list[str] = []             # a core-term `index-def` armed for the next block (→ def-box)
    occ: dict[tuple[str, str], int] = {}    # per-page (slug, kind) → next occurrence index

    def _with_label(frag: str) -> str:
        """Attach an armed `<!-- label: key -->` as `data-label` on the float's opening tag, so the
        numbering pre-pass can build the key→"Figure N" map the `[ref:key]` cross-reference resolves
        against. Consumes the pending label; a float with no armed label renders unchanged."""
        if pending_label:
            key = html.escape(pending_label.pop(0), quote=True)
            # Inject at the END of the opening tag (before `>`), NOT right after `<figure`: the float
            # regex and the numbering pass both key on `class="book-figure"` sitting immediately after
            # `<figure `, so a `data-label` wedged in front of `class` would make the float unmatchable.
            frag = re.sub(r"(<(?:figure|table)\b[^>]*?)>", rf'\1 data-label="{key}">', frag, count=1)
        return frag

    def _emit(block_html: str) -> None:
        # Attach every pending anchor. The first goes onto the block's own opening tag; extras (two tags
        # heading one block — a concept defined and another exemplified at the same paragraph) front the
        # block as empty anchor spans so each deep-link resolves.
        if pending_anchors:
            for extra in pending_anchors[1:]:
                block_html = f'<span id="{html.escape(extra, quote=True)}"></span>' + block_html
            block_html = _inject_anchor_id(block_html, pending_anchors[0])
            pending_anchors.clear()
        out.append(block_html)

    def _consume_index_tag(line: str) -> bool:
        """If `line` is a lone index-def / index-example tag, arm its anchor for the next block and return
        True. A tag may sit on its own line at the head of a block that ALSO holds the block it annotates
        (no blank line between), so this runs both on a standalone comment block and on a block's first
        line(s). Several tags may stack on one block."""
        s = line.strip()
        _md, _me = INDEX_DEF_RE.match(s), INDEX_EXAMPLE_RE.match(s)
        if not (_md or _me):
            return False
        slug = (_md or _me).group(1)
        kind = "def" if _md else "ex"
        if _md and slug in _DEF_SLUGS:
            pending_def.append(slug)   # arm the blue def-box for the term's defining blockquote
        n = occ.get((slug, kind), 0)
        occ[(slug, kind)] = n + 1
        if anchor_map is not None:
            got = anchor_map.get((slug, kind, n))
            if got is not None:
                pending_anchors.append(got)
        return True

    def _consume_leading_marker(line: str) -> bool:
        """Placement-robust marker strip. If `line` (the head of a block) is a whole marker comment the
        build consumes — an index tag, a `gloss:`/`gloss-only:`, or a bare `<!-- glossary-auto -->` — act on
        it and return True so the caller peels it off the block. This is what lets a marker sit glued to the
        prose it annotates (NO blank line between), matching META_RE's already-placement-robust behaviour:
        the author need not remember a blank line, and a glued marker leaks NOWHERE (the twice-shipped
        gloss-only-glued-to-prose bug). Each keyword acts as it would as a standalone block — `gloss:` emits
        its first-reference sidenote, `figure`/`figure-iframe`/`eq` render their display element, `gloss-only`
        / `glossary-auto` harvest/render — then is peeled. This covers the WHOLE argument-taking vocabulary
        uniformly (part-title/chapter-title are stripped earlier by META_RE, before block splitting)."""
        s = line.strip()
        if _consume_index_tag(s):
            return True
        _gm = _GLOSS_RE.match(s)
        if _gm:
            # A gloss first-reference sidenote is itself a `**Term.**` definition inset, so it carries the
            # `def-inset` modifier (italic body, upright bold Term) like an authored `> **Term.**` blockquote.
            _emit(f'<blockquote class="aside-sidenote def-inset"><p><strong>{inline(_gm.group("term"))}.</strong> '
                  f'{inline(_gm.group("def"))}</p></blockquote>')
            return True
        if _GLOSS_ONLY_RE.match(s):
            return True  # glossary-only: harvested by _collect_glossary; renders nothing inline
        _wo = _WEB_ONLY_RE.match(s)
        if _wo:
            # Web-only line — render its inline markdown as a paragraph (the PDF projection drops the marker).
            _emit(f"<p>{inline(_wo.group('content'))}</p>")
            return True
        if s == "<!-- glossary-auto -->":
            items = "".join(f"<li><strong>{inline(t)}</strong> — {inline(d)}</li>"
                            for t, d in sorted(_GLOSSARY.items(), key=lambda kv: kv[0].lower()))
            _emit(f'<ul class="glossary">{items}</ul>')
            return True
        # Single-comment display directives (figure / figure-iframe / eq): render whichever it is, then peel.
        if s.startswith("<!--") and s.endswith("-->") and s.count("<!--") == 1:
            inner = s[4:].lstrip()
            if inner.startswith("figure-iframe:"):
                _emit(_figure_iframe_block(s))
                return True
            if inner.startswith("figure:"):
                _emit(_with_label(_figure_block(s)))
                return True
            if inner.startswith("label:"):
                # A cross-ref key for the NEXT float: `<!-- label: <key> -->`. Armed here, consumed by
                # `_with_label` when the figure/mermaid/table emits, which stamps it as `data-label`.
                pending_label.append(s[len("<!--"):-len("-->")].strip()[len("label:"):].strip())
                return True
            if inner.startswith("table:"):
                # A caption for the NEXT table: `<!-- table: <full caption> [short: <short>] -->`. Armed
                # here, consumed when the pipe table renders (which wraps it in a <caption>). All tables are
                # numbered "Table N" regardless; a directive is only needed to give one a caption + a list
                # of floats entry.
                pending_table_caption.append(
                    s[len("<!--"):-len("-->")].strip()[len("table:"):].strip())
                return True
            if inner.startswith("eq:"):
                _emit(f'<p class="book-eq">{inline(s[len("<!--"):-len("-->")].strip()[len("eq:"):].strip())}</p>')
                return True
            if inner.startswith("point:"):
                # `<!-- point: <slug> | <claim> [| terms: …] -->` — the induced canonical point of the
                # paragraph it heads (the drain notation). An INERT decorator: consumed and stripped, renders
                # NOTHING (the outline model reads it from the IR, not the HTML). Peeled here so it never
                # reaches the lone-comment passthrough and leaks; degradation-friendly and byte-identical.
                return True
            if inner.startswith("section-terms:"):
                # `<!-- section-terms: <t1>, <t2> -->` — the tier-1 sibling of `point`: names the major
                # concepts a section develops (the drain notation). Equally INERT — consumed, stripped,
                # renders NOTHING (the reverse index reads it from the IR). Same byte-identical guarantee.
                return True
        return False

    skip_blocks: set[int] = set()   # blocks already consumed as a figure caption (folded into the <figure>)
    section_no = 0                   # per-chapter `## ` section counter (only used when section_prefix is set)
    for _bi, block in enumerate(blocks):
        if _bi in skip_blocks:
            continue
        block = block.strip("\n")
        if not block.strip():
            continue
        # Peel every leading marker comment off the block (placement-robust — a marker may sit glued to the
        # prose it heads, NO blank line between). `_consume_leading_marker` acts on each (index tag → arm
        # anchor; gloss → emit sidenote; gloss-only / glossary-auto → harvest/render) and returns True so it
        # is stripped from the block. A block may be JUST markers (blank line follows) or markers PLUS the
        # prose they head (no blank line) — this handles both, so a glued marker leaks NOWHERE.
        blk_lines = block.splitlines()
        while blk_lines and _consume_leading_marker(blk_lines[0]):
            blk_lines = blk_lines[1:]
        if not blk_lines:
            continue  # the block was nothing but marker comment(s)
        # A marker heads the block it annotates — a MID-block marker (prose above it in the same block) would
        # silently leak into the rendered <p>. Fail loud so the author moves it to the block boundary rather
        # than shipping a raw comment. (The head case above already consumed leading markers.)
        for _ln in blk_lines[1:]:
            if _MARKER_COMMENT_RE.match(_ln.strip()):
                raise SystemExit(
                    f"notation marker must head its block (blank line before it, or move above the prose): "
                    f"mid-block marker {_ln.strip()!r}")
        block = "\n".join(blk_lines)
        # A core-term index-def arms the blue def-box for the block it heads (this content block). Capture
        # and clear here so it applies to exactly the next content block, never leaking further.
        def_armed = bool(pending_def)
        pending_def.clear()
        stripped = block.strip()
        # ── The A-flip: one classifier, one renderer per node kind. ────────────────────────────────
        # Classification is single-sourced through the typed IR (`book_ir.classify_render_block`, which
        # wraps the IR's `_classify_prose`), and each kind renders through the extracted `_render_*`
        # primitive. The marker-arming state above (pending label / caption / anchors, gloss sidenotes)
        # stays in this loop — it is the placement-robust arming layer the content dispatch consumes.
        # This replaces the old inline prefix-testing cascade; the emit is byte-identical.
        kind = _ir.classify_render_block(block)

        if kind is _ir.BlockKind.CODE_INSET:
            _emit(_render_inset(block))
            continue
        if kind is _ir.BlockKind.MERMAID:
            # A standalone diagram is a numbered figure; fold an immediately-following one-line italic
            # paragraph (`*…*`) in as its <figcaption>, and skip that block. `_with_label` stamps any
            # armed `<!-- label: -->` so the numbering pass can key the `[ref:]` cross-reference.
            caption_md = None
            if _bi + 1 < len(blocks):
                _nb = blocks[_bi + 1].strip()
                if (_nb.startswith("*") and not _nb.startswith("**")
                        and _nb.endswith("*") and "```" not in _nb and "\n\n" not in _nb):
                    caption_md = _nb.strip("*").strip()
                    skip_blocks.add(_bi + 1)
            _emit(_with_label(_render_mermaid_figure(block, caption_md)))
            continue
        if kind is _ir.BlockKind.CODE:
            _emit(_render_code(block))
            continue
        # A blockquote renders its inner content recursively (its own `md_to_html` pass over the
        # prefix-stripped body handles any inner directive AND strips any inner stray comment), so it MUST
        # be dispatched with the block INTACT — before the prose-block stray-comment strip below. Left to
        # that strip, a legitimate directive living inside the quote (an inline `> <!-- figure: … -->` inset
        # diagram) is deleted as if it were a stray authoring comment, silently dropping the figure.
        if kind is _ir.BlockKind.BLOCKQUOTE:
            _emit(_render_blockquote(block, is_def=def_armed))
            continue
        # Gap-marker callouts (`[FILL IN: …]` / `[MORE CHAPTERS FOLLOW: …]`) — the IR classifies these as
        # PARA (they are prose-shaped), so the renderer keeps the shape test for them just ahead of prose.
        if stripped.startswith("[FILL IN:") or stripped.startswith("[MORE CHAPTERS FOLLOW:"):
            _emit(_render_gap_marker(block))
            continue
        # Strip any HTML comment still in this (prose-like) block. Every recognized display/arming directive
        # was already consumed + peeled by `_consume_leading_marker` in the block-head pass; a comment that
        # survives to here is a STRAY authoring TODO/note (its leading token is not in the notation
        # vocabulary — the `stray-book-comment` lint guards the source). Left in, it leaks: raw here (an
        # invisible HTML comment) and as VISIBLE text in the Typst/PDF projection. Drop it. Code / mermaid /
        # inset blocks (which may hold a literal `<!-- … -->`) were emitted and `continue`d above, so this
        # only ever touches prose. A block that was nothing but a stray comment strips to empty and is skipped.
        if "<!--" in block:
            block = _STRAY_COMMENT_RE.sub("", block).strip("\n")
            stripped = block.strip()
            if not stripped:
                continue
        if kind is _ir.BlockKind.HEADING:
            # Section-level (`## `) headings in a body chapter carry a `part.chapter.N` display prefix.
            # N counts `## ` headings in reading order; `###`/`####` subsections stay unnumbered (3-level
            # scheme). Deeper levels don't advance the counter, so the section number is stable.
            heading_no = None
            if section_prefix is not None and block.strip().startswith("## "):
                section_no += 1
                heading_no = f"{section_prefix}.{section_no}"
            _emit(_render_heading(block, heading_no))
            continue
        if kind is _ir.BlockKind.TABLE:
            tbl = _render_pipe_table(block)
            if pending_table_caption:
                cap_el = _caption_el("caption", pending_table_caption.pop(0))
                tbl = re.sub(r"(<table\b[^>]*>)", lambda mm: mm.group(1) + cap_el, tbl, count=1)
            _emit(_with_label(tbl))
            continue
        if kind is _ir.BlockKind.LIST:
            _emit(_render_unordered_list(block))
            continue
        if kind is _ir.BlockKind.ORDERED_LIST:
            _emit(_render_ordered_list(block))
            continue
        # Paragraph (the IR's PARA fall-through).
        _emit(_render_paragraph(block))
    return "\n".join(out)


def _strip_blockquote_prefix(line: str) -> str:
    """Drop a leading `> ` (or bare `>`) from one blockquote line, so the inner content can be
    re-rendered as markdown. A `>` with nothing after it becomes a blank line (a paragraph break
    inside the quote)."""
    s = line.strip()
    if s.startswith("> "):
        return s[2:]
    if s == ">":
        return ""
    return s.lstrip(">")


_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _is_pipe_table(block: str) -> bool:
    """A block is a pipe table when it has at least two lines, every line contains a `|`, and the
    second line is a `|---|---|` separator row."""
    lines = block.splitlines()
    if len(lines) < 2 or "|" not in lines[0]:
        return False
    return bool(_TABLE_SEP_RE.match(lines[1]))


def _split_table_row(row: str) -> list[str]:
    """Split one `| a | b | c |` row into its cells, dropping the outer empties from the leading and
    trailing pipe."""
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return cells


def _col_alignments(sep_row: str) -> list[str]:
    """Read GFM per-column alignment off the separator row (line 2): a trailing colon (`---:`) marks a
    right-aligned column, which the booktabs style renders with the `.num` class (numbers right-align so a
    reader compares magnitudes down the column). A leading+trailing colon (`:-:`) is center; a bare `---`
    or leading-colon is the left default. Returns a class string ("" left, " class=\"num\"" right) per column."""
    out: list[str] = []
    for spec in _split_table_row(sep_row):
        s = spec.strip()
        right = s.endswith(":") and not s.startswith(":")  # `---:` only → numeric right-align
        out.append(' class="num"' if right else "")
    return out


def _render_pipe_table(block: str) -> str:
    """Render a GitHub-flavored pipe table into an HTML <table> with a <thead> and <tbody>. The
    separator row (line 2) is consumed for structure (and per-column alignment), not rendered. A column
    whose separator ends in a colon (`---:`) right-aligns via `.num` for the booktabs style (drawing/tables.md)."""
    lines = block.splitlines()
    header = _split_table_row(lines[0])
    aligns = _col_alignments(lines[1]) if len(lines) > 1 else []

    def _cls(i: int) -> str:
        return aligns[i] if i < len(aligns) else ""

    body_rows = [_split_table_row(ln) for ln in lines[2:] if ln.strip()]
    thead = "".join(f"<th{_cls(i)}>{inline(c)}</th>" for i, c in enumerate(header))
    trs = []
    for row in body_rows:
        tds = "".join(f"<td{_cls(i)}>{inline(c)}</td>" for i, c in enumerate(row))
        trs.append(f"<tr>{tds}</tr>")
    return (
        '<table class="book-table"><thead><tr>'
        f"{thead}</tr></thead><tbody>{''.join(trs)}</tbody></table>"
    )


# ── Per-block-kind content renderers ──────────────────────────────────────────────────────────────
# Extracted verbatim from `md_to_html`'s block loop so a single dispatch table maps each IR `BlockKind`
# to its HTML. These are the "render each node kind to HTML" primitives of the C→A migration: the emit
# loop below walks the block segmentation and calls the one that matches, rather than re-testing string
# prefixes inline. Each returns the SAME HTML the old inline branch produced (byte-identical build).

def _render_inset(block: str) -> str:
    """A titled INSET — `<!-- inset: <title> -->` glued to the head of a fenced code block — lifted into a
    set-apart box (a `<figure class="code-inset">` with a demoted `inset-title` label, NOT an <hN>, so no
    heading-order break). A mermaid fence renders to a static inline SVG; any other fence to <pre><code>."""
    lines = block.strip().splitlines()
    title = _INSET_RE.match(lines[0].strip()).group("title")
    lines = lines[1:]  # drop the inset marker; the rest is the fence
    lang = lines[0].strip()[3:].strip().lower()
    inner_lines = lines[1:]
    if inner_lines and inner_lines[-1].strip() == "```":
        inner_lines = inner_lines[:-1]
    inner = "\n".join(inner_lines)
    body = (render_mermaid_svg(inner) if lang == "mermaid"
            else f"<pre><code>{html.escape(inner, quote=False)}</code></pre>")
    return f'<figure class="code-inset"><p class="inset-title">{inline(title)}</p>{body}</figure>'


def _render_code(block: str) -> str:
    """A non-mermaid fenced block → a plain <pre><code>."""
    lines = block.splitlines()
    inner_lines = lines[1:]
    if inner_lines and inner_lines[-1].strip() == "```":
        inner_lines = inner_lines[:-1]
    inner = "\n".join(inner_lines)
    return f"<pre><code>{html.escape(inner, quote=False)}</code></pre>"


def _render_mermaid_figure(block: str, caption_md: str | None) -> str:
    """A standalone ```mermaid fence → a numbered `<figure class="book-figure diagram-figure">` holding the
    static inline SVG, with an optional folded italic-paragraph <figcaption>. `caption_md` is the folded
    following-paragraph caption text (already stripped of its `*…*`), or None."""
    lines = block.splitlines()
    inner_lines = lines[1:]
    if inner_lines and inner_lines[-1].strip() == "```":
        inner_lines = inner_lines[:-1]
    inner = "\n".join(inner_lines)
    svg = render_mermaid_svg(inner)
    cap_html = _caption_el("figcaption", caption_md) if caption_md is not None else ""
    return f'<figure class="book-figure diagram-figure">{svg}{cap_html}</figure>'


def _render_gap_marker(block: str) -> str:
    """A `[FILL IN: …]` / `[MORE CHAPTERS FOLLOW: …]` gap-marker callout → a plain <div> (not <aside>: two
    markers on one page would trip the unique-landmark accessibility rule)."""
    stripped = block.strip()
    kind = "fill" if stripped.startswith("[FILL IN:") else "more"
    label = "FILL IN" if kind == "fill" else "MORE CHAPTERS FOLLOW"
    inner = stripped[stripped.index(":") + 1:].rstrip("]").strip()
    return (f'<div class="marker marker-{kind}">'
            f'<span class="marker-tag">{label}</span> {inline(inner)}</div>')


def _render_heading(block: str, section_no: str | None = None) -> str:
    """A `#`..`####` heading → the matching <hN>. A trailing `{#slug}` sets the id anchor (stripped from the
    visible text); an `## ` may carry a leading `[role: Name]` kicker.

    `section_no` (e.g. "1.1.3") is a DISPLAY-ONLY `part.chapter.section` prefix stamped on a `## ` (section)
    heading's visible text for in-chapter reference. It is prose, not structure: it never touches the `{#slug}`
    id anchor (the anchor is peeled off first by `_heading_anchor`), so every cross-ref, index-def, and
    glossary pointer keeps resolving. Passed only for body chapters (Parts 1-5) by the per-chapter build;
    `None` (the default) — front/back-matter, appendix, blockquotes, floats, word-count — renders unnumbered."""
    stripped = block.strip()
    if stripped.startswith("#### "):
        txt, anc = _heading_anchor(stripped[5:])
        return f"<h4{anc}>{inline(txt)}</h4>"
    if stripped.startswith("### "):
        txt, anc = _heading_anchor(stripped[4:])
        return f"<h3{anc}>{inline(txt)}</h3>"
    if stripped.startswith("## "):
        txt, anc = _heading_anchor(stripped[3:])
        kick, txt = _role_kicker(txt)
        num = f'<span class="sec-num">{html.escape(section_no)}</span> ' if section_no else ""
        return f"<h2{anc}>{num}{kick}{inline(txt)}</h2>"
    txt, anc = _heading_anchor(stripped[2:])
    return f"<h1{anc}>{inline(txt)}</h1>"


def _render_blockquote(block: str, is_def: bool = False) -> str:
    """A blockquote (every line starts with `>`) → a classified `<blockquote>`. Its inner content is itself
    markdown (heading + prose + a `> ```mermaid ``` fence), rendered recursively; an inner heading is demoted
    to a styled `inset-title` paragraph (no document-outline break). The class is picked by shape: a demoted
    label → `concept-inset`; a `**The … Thesis.**` lead → `thesis-box`; a `**Term.**` lead armed by a
    core-term `index-def` (`is_def`) → the blue `def-box`; else a light `aside-sidenote`."""
    inner_md = "\n".join(_strip_blockquote_prefix(ln) for ln in block.splitlines())
    inner_html = md_to_html(inner_md)
    inner_html = re.sub(r"<h[1-6]([^>]*)>(.*?)</h[1-6]>", r'<p class="inset-title"\1>\2</p>', inner_html, flags=re.S)
    if 'class="inset-title"' in inner_html:
        klass = "concept-inset"
    elif _IS_THESIS_LEAD_RE.search(inner_html):
        klass = "thesis-box"
    elif is_def and _IS_DEF_LEAD_RE.search(inner_html):
        klass = "def-box"
    elif _IS_DEFN_SIDENOTE_LEAD_RE.search(inner_html):
        klass = "aside-sidenote def-inset"
    else:
        klass = "aside-sidenote"
    return f'<blockquote class="{klass}">{inner_html}</blockquote>'


def _render_unordered_list(block: str) -> str:
    """An unordered list — items open with `- `; a following non-`- ` line is a wrapped continuation folded
    into the current item so a wrapped bullet stays one <li>."""
    li_texts: list[str] = []
    for ln in block.splitlines():
        s = ln.strip()
        if s.startswith("- "):
            li_texts.append(s[2:])
        elif li_texts:
            li_texts[-1] += " " + s
        else:
            li_texts.append(s)
    items = "".join(f"<li>{inline(t)}</li>" for t in li_texts)
    return f"<ul>{items}</ul>"


def _render_ordered_list(block: str) -> str:
    """An ordered list — items open with `N. `; wrapped continuations fold into the current item (same as
    the unordered case)."""
    oli: list[str] = []
    for ln in block.splitlines():
        s = ln.strip()
        if re.match(r"^\d+\.\s", s):
            oli.append(re.sub(r"^\d+\.\s+", "", s))
        elif oli:
            oli[-1] += " " + s
        else:
            oli.append(s)
    items = "".join(f"<li>{inline(t)}</li>" for t in oli)
    return f"<ol>{items}</ol>"


def _render_paragraph(block: str) -> str:
    """A paragraph — wrapped source lines joined into one <p>."""
    return f"<p>{inline(' '.join(ln.strip() for ln in block.splitlines()))}</p>"


CSS = f"""
{CSS_ROOT_BLOCK}
* {{ box-sizing: border-box; }}
body {{ font-family: var(--font-body); font-size: 17px; line-height: 1.65;
       color: var(--ink); margin: 0; background: var(--paper); }}
h1, h2, h3, h4, header.chap h1 {{ font-family: var(--font-display); font-weight: var(--display-weight); }}
.wrap {{ max-width: 52rem; margin: 0 auto; padding: 0 1.4rem 4rem; }}
nav.toc {{ background: var(--panel); border-bottom: 1px solid var(--rule); padding: 0.9rem 1.4rem; font-size: 14px; }}
nav.toc .toc-inner {{ max-width: 52rem; margin: 0 auto; }}
nav.toc details {{ margin: 0; }}
nav.toc summary {{ cursor: pointer; font-weight: 600; color: var(--accent); list-style: none; }}
nav.toc summary::-webkit-details-marker {{ display: none; }}
nav.toc ol {{ list-style: none; padding: 0.6rem 0 0; margin: 0; }}
nav.toc .part {{ font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em;
                 font-size: 12px; margin: 0.7rem 0 0.25rem; }}
nav.toc a {{ color: var(--ink); text-decoration: none; display: block; padding: 2px 0 2px 1rem; }}
nav.toc a:hover {{ color: var(--accent); }}
nav.toc a.current {{ color: var(--accent); font-weight: 600; border-left: 2px solid var(--accent);
                     padding-left: calc(1rem - 2px); }}
header.chap {{ padding: 2.6rem 0 1.2rem; border-bottom: 1px solid var(--rule); margin-bottom: 1.6rem; }}
header.chap .kicker {{ color: var(--accent); font-weight: 700; font-size: 13px; letter-spacing: 0.06em;
                       text-transform: uppercase; }}
/* The kicker halves are links but must stay understated — inherit the small-caps accent colour, no default
   underline; reveal the underline only on hover/focus so the affordance is discoverable without shouting. */
header.chap .kicker a {{ color: inherit; text-decoration: none; }}
header.chap .kicker a:hover, header.chap .kicker a:focus {{ text-decoration: underline; }}
header.chap h1 {{ font-size: 2rem; line-height: 1.15; margin: 0.35rem 0 0; }}
.part-epigraph {{ margin: 1.6rem 0 0; padding: 0.8rem 0 0.2rem 1.1rem; border-left: 3px solid var(--rule);
                  color: var(--muted); font-style: italic; }}
.part-epigraph .attr {{ display: block; margin-top: 0.5rem; font-style: normal; font-size: 14px;
                        color: var(--muted); }}
h2 {{ font-size: 1.32rem; margin: 2.2rem 0 0.6rem; }}
/* `part.chapter.section` display number stamped on a body-chapter section heading (build-derived, not
   authored). Muted + tabular so it reads as a reference locator, not part of the title; it is display-only
   and carries no id, so the heading's own anchor, cross-refs, and the index all still resolve. */
h2 .sec-num {{ color: var(--muted); font-weight: 600; font-variant-numeric: tabular-nums; margin-right: 0.15em; }}
/* Role kicker on a step heading (`## [role: Architect] …`) — the engineer's climbing title, rendered in
   the same small-caps accent register as the chapter kicker (`header.chap .kicker`) but inline before the
   heading text. It rides the accent colour so the ladder reads at a glance down the chapter. */
h2 .role-kick {{ color: var(--accent); font-weight: 700; font-style: italic; font-size: 0.62em; letter-spacing: 0.07em;
                 text-transform: uppercase; margin-right: 0.5em; vertical-align: 0.12em; }}
h3 {{ font-size: 1.08rem; margin: 1.6rem 0 0.4rem; }}
h4 {{ font-size: 0.98rem; margin: 1.15rem 0 0.3rem; color: var(--ink); }}
p {{ margin: 0 0 1rem; }}
ul {{ margin: 0 0 1rem; padding-left: 1.3rem; }}
ol {{ margin: 0 0 1rem; padding-left: 1.5rem; list-style: decimal; }}
li {{ margin: 0.3rem 0; }}
blockquote {{ margin: 1.2rem 0; padding: 0.6rem 1.1rem; border-left: 3px solid var(--rule);
              color: var(--muted); font-style: italic; background: var(--panel); }}
/* Plain editorial asides render as Tufte-style sidenotes. On a NARROW screen they collapse to a normal
   inline blockquote (the default above). On a WIDE screen the media query below floats them into the
   right gutter — smaller, ragged, unboxed — so the aside sits beside the text it comments on without
   breaking the reading column. Concept insets (`.concept-inset`, boxed primers) keep the default box. */
blockquote.aside-sidenote {{ background: transparent; }}
@media (min-width: 60rem) {{
  blockquote.aside-sidenote {{
    float: right; clear: right; width: 13rem; margin: 0.3rem -15rem 1rem 0;
    padding: 0 0 0 0.9rem; border-left: 2px solid var(--box-inset-rule); background: transparent;
    font-size: 14px; line-height: 1.5; color: var(--muted);
  }}
}}
/* CITATIONS & EDITORIAL NOTES (bibliography subsystem). Two visibly-distinct in-text marker families:
   `[cite:]` → a NUMERIC superscript linked to the chapter's numbered Works Cited; `[note:]` → a SYMBOLIC
   superscript (* † ‡ § …). Each is followed by a right-gutter note (an inline <span>, valid inside a <p>,
   styled to reuse the same Tufte gutter geometry as `.aside-sidenote`). The number/symbol sets are
   disjoint by construction (a check asserts it). */
sup.cite-ref, sup.note-ref {{ line-height: 0; font-size: 0.72em; }}
sup.cite-ref a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
sup.cite-ref a:hover {{ text-decoration: underline; }}
sup.note-ref {{ color: var(--muted); font-weight: 600; padding-left: 0.05em; }}
.cite-note, .editorial-note {{
  display: block; margin: 0.3rem 0 1rem; padding: 0 0 0 0.9rem;
  border-left: 2px solid var(--box-inset-rule); font-size: 14px; line-height: 1.5;
  color: var(--muted); font-style: normal;
}}
.cite-note .cn-mark, .editorial-note .cn-mark {{ color: var(--accent); font-weight: 600; margin-right: 0.15em; }}
.cite-note a, .editorial-note a {{ color: var(--accent); word-break: break-word; }}
@media (min-width: 60rem) {{
  .cite-note, .editorial-note {{
    float: right; clear: right; width: 13rem; margin: 0.2rem -15rem 0.9rem 0;
  }}
}}
/* Per-chapter Works Cited — a numbered list set off from the body by a top rule; the <ol> numbering
   equals each entry's id, so citation superscript N links to entry N (the mirror). */
section.works-cited {{ margin: 2.4rem 0 1rem; padding-top: 1rem; border-top: 1px solid var(--rule); clear: both; }}
section.works-cited .wc-h {{ font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em;
                             color: var(--muted); margin: 0 0 0.6rem; }}
ol.wc-list {{ font-size: 15px; line-height: 1.5; }}
ol.wc-list li {{ margin: 0.35rem 0; padding-left: 0.2rem; }}
ol.wc-list li em, ul.bib-list li em {{ font-style: italic; }}
/* End-of-book Bibliography — a hanging-indent alphabetical list (unnumbered). */
section.bibliography ul.bib-list {{ list-style: none; padding-left: 0; font-size: 15px; line-height: 1.55; }}
section.bibliography ul.bib-list li {{ margin: 0 0 0.7rem; padding-left: 1.4rem; text-indent: -1.4rem; }}
section.bibliography .bib-empty {{ color: var(--muted); font-style: italic; }}
code {{ background: var(--code-bg); padding: 0.1em 0.35em; border-radius: 3px; font-size: 0.9em; }}
a {{ color: var(--accent); }}
/* Booktabs table style (drawing/tables.md): exactly three horizontal rules — a heavy top rule, a light
   rule under the header, a heavy bottom rule — and NO vertical rules or cell borders. Whitespace separates
   columns/rows; rules only group. No zebra striping (row padding does the separating). Numbers
   right-aligned via `.num`. WHY: vertical rules and boxed cells are chartjunk (Tufte / booktabs). */
table.book-table {{ border-collapse: collapse; width: 100%; margin: 1.2rem 0; font-size: 15px;
                    border-top: 2px solid var(--ink); border-bottom: 2px solid var(--ink); }}
table.book-table th, table.book-table td {{ border: none; padding: 0.6rem 0.7rem;
                                             text-align: left; vertical-align: top; line-height: 1.45; }}
table.book-table thead th {{ background: transparent; font-weight: 600;
                             border-bottom: 1px solid var(--muted); }}
table.book-table th.num, table.book-table td.num {{ text-align: right; }}
blockquote table.book-table {{ background: transparent; }}
blockquote .inset-title {{ font-style: normal; font-weight: 700; margin: 0 0 0.4rem; }}
blockquote pre.mermaid {{ font-style: normal; }}
/* Mermaid label DISPLAY size — driven from the SAME design token as the mermaid LAYOUT config
   (assets/mermaid-config.json, emitted by the token projector). Mermaid sizes each node box at the
   config font-size; these rules render the text at that identical px, so a label can never overflow the
   box mermaid drew for it (the config==CSS invariant). Do not hardcode a literal here — it would drift
   from the config and re-introduce the overflow class. */
pre.mermaid .nodeLabel, pre.mermaid .label text {{ font-size: {_MERMAID_LABEL_PX['node']}px; }}
pre.mermaid text.messageText {{ font-size: {_MERMAID_LABEL_PX['message']}px; }}
/* CONCEPT INSET — a textbook-style primer sidebar (a `> ### Inset N — Title` block). It is NOT a plain
   quote: it is a deliberately designed aside that teaches a background concept beside the main argument
   (e.g. "What is an automaton?"). So it drops the base blockquote's grey border + italic run and gets its
   own visual language: a tinted panel, a strong left accent rule, a labelled header band, and a ROMAN
   (non-italic) body a reader can actually read at length.

   ── SWAP POINT ─────────────────────────────────────────────────────────────────────────────────────
   Every knob is a CSS custom property on `.concept-inset`, so this "screen representation of the book" can
   be re-skinned in ONE place — change these vars to retarget a print stylesheet, a dark theme, or an
   alternate house style without touching any rule below. Add e.g. a `@media print` or `:root[data-theme=…]`
   block that only re-declares these variables and the whole sidebar follows. */
blockquote.concept-inset {{
  --inset-bg: var(--panel);           /* panel fill — warm off-white, distinct from the page's var(--panel) */
  --inset-accent: var(--box-inset-rule);       /* the lavender left accent rule + ::before square — a BORDER, no contrast rule */
  --inset-header: var(--ink);       /* header title + strong TEXT ink — near-black, ~13:1 on the lavender band/panel (WCAG-AA). The lavender box-inset-rule stays the accent RULE only; used as text ink it was 4.03:1, under AA. */
  --inset-header-bg: var(--box-inset-fill);    /* header band fill — a shade deeper than the panel so the label reads */
  --inset-body: var(--ink);         /* body ink — near-black warm grey, comfortable roman reading colour */
  --inset-accent-width: 5px;     /* thickness of the left accent rule */
  --inset-radius: 6px;
  --inset-pad-x: 1.35rem;
  --inset-pad-y: 1rem;
  --inset-max: 34rem;            /* keep the primer to a readable measure, not the full column width */

  background: var(--inset-bg);
  border: 1px solid var(--rule);
  border-left: var(--inset-accent-width) solid var(--inset-accent);
  border-radius: var(--inset-radius);
  color: var(--inset-body);
  font-style: normal;            /* KEY: kill the base blockquote italic — a primer reads as roman prose */
  padding: 0 var(--inset-pad-x) var(--inset-pad-y);
  margin: 1.7rem 0;
  max-width: var(--inset-max);
}}
/* Header treatment — the "Inset N — Title" label sits in its own tinted band, flush to the panel edges,
   set in small-caps-ish tracked type so it reads as a sidebar HEADER, not a run-in paragraph. It stays a
   demoted callout label (`p.inset-title`, not an <hN>) so no heading-order break and its id anchor is
   preserved. */
blockquote.concept-inset .inset-title {{
  font-style: normal; font-weight: 700; color: var(--inset-header);
  background: var(--inset-header-bg);
  margin: 0 calc(-1 * var(--inset-pad-x)) var(--inset-pad-y);
  padding: 0.6rem var(--inset-pad-x);
  border-radius: var(--inset-radius) var(--inset-radius) 0 0;
  border-bottom: 1px solid var(--rule);
  font-size: 0.9rem; letter-spacing: 0.02em; line-height: 1.35;
}}
blockquote.concept-inset .inset-title::before {{
  content: ""; display: inline-block; width: 0.55rem; height: 0.55rem; margin-right: 0.5rem;
  background: var(--inset-accent); border-radius: 2px; vertical-align: middle;
}}
blockquote.concept-inset p {{ margin: 0 0 0.7rem; line-height: 1.6; }}
blockquote.concept-inset p:last-child {{ margin-bottom: 0; }}
blockquote.concept-inset strong {{ color: var(--inset-header); }}
blockquote.concept-inset em {{ font-style: italic; }}  /* inline emphasis still italicizes inside roman body */
/* CODE INSET — a fenced code listing lifted into a titled box: "here is a real artifact from the system."
   It shares the concept-inset's amber header-band label typography (the sidebar HEADER, `p.inset-title`,
   demoted so no heading-order break), but its body is a monospace listing, not roman prose. The header
   sits flush to the panel edges; the <pre> keeps the page's usual code styling, un-boxed inside the panel
   so the box's own border is the only frame. */
figure.code-inset {{
  --inset-bg: var(--panel); --inset-accent: var(--box-inset-rule); --inset-header: var(--ink); --inset-header-bg: var(--box-inset-fill);
  --inset-radius: 6px; --inset-pad-x: 1.35rem;
  background: var(--inset-bg); border: 1px solid var(--rule);
  border-left: 5px solid var(--inset-accent); border-radius: var(--inset-radius);
  margin: 1.7rem 0; max-width: 40rem; overflow: hidden;
}}
figure.code-inset .inset-title {{
  font-family: "Source Sans 3", sans-serif; font-style: normal; font-weight: 700;
  color: var(--inset-header); background: var(--inset-header-bg);
  margin: 0; padding: 0.55rem var(--inset-pad-x);
  border-bottom: 1px solid var(--rule);
  font-size: 0.9rem; letter-spacing: 0.02em; line-height: 1.35;
}}
figure.code-inset .inset-title::before {{
  content: ""; display: inline-block; width: 0.55rem; height: 0.55rem; margin-right: 0.5rem;
  background: var(--inset-accent); border-radius: 2px; vertical-align: middle;
}}
figure.code-inset pre {{ margin: 0; padding: 0.9rem var(--inset-pad-x); background: transparent; border: 0; }}
/* THESIS box — a chapter's load-bearing claim, lifted out of the reading column as a light lavender panel.
   Un-italic (a thesis is a statement, not an aside); dark ink var(--ink) on var(--box-thesis-fill) clears WCAG AA (~13.8:1).
   Taxonomy + spec: book/_design/callout-typography.md. */
blockquote.thesis-box {{ background: var(--box-thesis-fill); border: 1px solid var(--rule); border-left: 4px solid var(--box-thesis-rule);
                         color: var(--ink); font-style: normal; padding: 1rem 1.3rem; margin: 1.6rem 0;
                         border-radius: 5px; }}
blockquote.thesis-box p {{ margin: 0 0 0.6rem; }}
blockquote.thesis-box p:last-child {{ margin-bottom: 0; }}
blockquote.thesis-box strong {{ color: var(--box-thesis-rule); }}
/* DEFINITION box — a core-term definition (an index-def marker on a bold-lead Term blockquote), lifted
   into a blue panel that mirrors the thesis box's shape but carries the definition-azure anchor. Blue on
   every surface, distinct from the umber chrome accent and the green thesis claim. */
blockquote.def-box {{ background: var(--box-def-fill); border: 1px solid var(--rule);
                      border-left: var(--border-box-rule) solid var(--box-def-rule);
                      color: var(--ink); font-style: italic; padding: 1rem 1.3rem; margin: 1.6rem 0;
                      border-radius: 5px; }}
blockquote.def-box p {{ margin: 0 0 0.6rem; }}
blockquote.def-box p:last-child {{ margin-bottom: 0; }}
blockquote.def-box strong {{ color: var(--box-def-rule); }}
/* DEFINITION body typography — the definition prose reads in italics (it is an aside on a term), while the
   bold Term LEAD stays upright (a label, not emphasis). Applies to both the light `> **Term.**` sidenote
   (`def-inset`) and the boxed core-term definition (`def-box`). Only the FIRST paragraph's leading <strong>
   is uprighted, so the term label reads as a label; any later inline bold keeps the surrounding italic.
   Footnotes (em-led), plain sidenotes, primers, and theses are untouched. Taxonomy: _design/callout-typography.md. */
blockquote.def-inset {{ font-style: italic; }}
blockquote.def-inset > p:first-child > strong:first-child,
blockquote.def-box > p:first-child > strong:first-child {{ font-style: normal; }}
.book-eq {{ text-align: center; font-family: Georgia, "Times New Roman", serif; font-style: italic;
           font-size: 1.2em; color: var(--ink); margin: 1.3rem 0; letter-spacing: 0.02em; }}
figure.book-figure {{ margin: 1.8rem 0; text-align: center; }}
figure.book-figure svg,
figure.book-figure img {{ max-width: 100%; height: auto; }}
figure.book-figure figcaption {{ font-size: 14px; color: var(--muted); margin-top: 0.6rem;
                                text-align: left; line-height: 1.5; }}
figure.book-figure figcaption.fig-label-only {{ text-align: center; }}
.fig-label, .tbl-label {{ font-weight: 700; color: var(--ink); }}
table caption {{ caption-side: top; text-align: left; font-size: 14px; color: var(--muted);
                 margin-bottom: 0.45rem; line-height: 1.5; }}
ul.list-of-floats-links {{ list-style: none; padding-left: 0; }}
ul.list-of-floats-links li {{ margin: 0.15rem 0; }}
/* Front-glossary term linked to its canonical definition site (idx-def anchor). Keeps the bold term's ink
   colour; a dotted underline marks it as a jump-to-definition without the heavy accent of an inline link. */
a.gloss-site {{ color: inherit; text-decoration: none; border-bottom: 1px dotted var(--muted); }}
a.gloss-site:hover, a.gloss-site:focus {{ color: var(--accent); border-bottom-color: var(--accent); }}
/* Figures Gallery (figures.html) — every figure verbatim (same rendered fragment the chapters ship),
   `<hr>`-separated, each followed by a small "from <chapter>" back-link. */
.gallery-item {{ margin: 0; }}
.gallery-item .book-figure {{ margin-top: 0; }}
.gallery-source {{ font-size: 13px; color: var(--muted); text-align: center; margin: 0.5rem 0 0; }}
.gallery-source a {{ color: var(--accent); text-decoration: underline; }}
.gallery hr {{ border: none; border-top: 1px solid var(--rule); margin: 2.4rem 0; }}
.gallery-group {{ margin: 0 0 2.4rem; }}
.gallery-group > h2 {{ margin: 2.6rem 0 0.2rem; padding-bottom: 0.3rem; border-bottom: 2px solid var(--rule); }}
.gallery-group-note {{ font-size: 14px; color: var(--muted); margin: 0 0 1.6rem; }}
.marker {{ margin: 1.3rem 0; padding: 0.75rem 1rem; border-radius: 5px; font-size: 15px; }}
.marker-fill {{ background: var(--accent-tint); border: 1px dashed var(--accent); }}
.marker-more {{ background: var(--box-def-fill); border: 1px dashed var(--box-def-rule); }}
.marker-tag {{ display: inline-block; font-weight: 700; font-size: 11px; letter-spacing: 0.05em;
               padding: 1px 6px; border-radius: 3px; margin-right: 0.5rem; vertical-align: 1px; }}
.marker-fill .marker-tag {{ background: var(--accent); color: var(--paper); }}
.marker-more .marker-tag {{ background: var(--box-def-rule); color: var(--paper); }}
/* Per-page chapter navigation — one left→right sequence bar (Table of contents « … │ THIS CHAPTER │ … »
   Index), bottom-only. Mobile-first: stacked column (backward pills → centred name → forward pills);
   enhanced to a three-zone row at >=60rem so the name stays dead-centre. Tokens only. */
.chapnav {{ display: flex; flex-direction: column; gap: 0.8rem; align-items: stretch;
            margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid var(--rule); }}
.chapnav-back, .chapnav-fwd {{ display: flex; flex-wrap: wrap; gap: 0.6rem; justify-content: center; }}
.chapnav-here {{ text-align: center; font-weight: 600; color: var(--accent); font-size: 18px; padding: 0.2rem 0; }}
.chapnav a {{ font-size: 12px; letter-spacing: 0.03em; text-transform: uppercase; font-weight: 600;
              color: var(--accent); text-decoration: none; padding: 0.5rem 0.85rem; line-height: 1.1;
              border: 1px solid var(--rule); border-radius: 6px; background: var(--paper); }}
.chapnav a:hover {{ border-color: var(--accent); background: var(--panel); }}
@media (min-width: 60rem) {{
  .chapnav {{ flex-direction: row; align-items: center; }}
  .chapnav-back {{ flex: 1; justify-content: flex-end; }}
  .chapnav-fwd {{ flex: 1; justify-content: flex-start; }}
  .chapnav a {{ white-space: nowrap; }}
  .chapnav-here {{ flex: 0 0 auto; max-width: 22rem; overflow: hidden; text-overflow: ellipsis;
                   display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
}}
.book-foot {{ margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--rule); color: var(--muted);
              font-size: 13px; text-align: center; }}
/* index page */
.book-title {{ padding: 3rem 0 0.5rem; }}
.book-title h1 {{ font-size: 2.4rem; margin: 0; }}
.book-title .sub {{ color: var(--muted); margin-top: 0.4rem; }}
.book-download {{ margin-top: 0.9rem; }}
.book-download a {{ display: inline-block; font-size: 14px; font-weight: 600; color: var(--accent);
                    text-decoration: none; padding: 0.45rem 0.9rem; border: 1px solid var(--rule);
                    border-radius: 6px; background: var(--paper); }}
.book-download a:hover {{ border-color: var(--accent); background: var(--panel); }}
.idx .part {{ font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em;
             font-size: 13px; margin: 2rem 0 0.5rem; }}
.idx ol {{ list-style: none; padding: 0; margin: 0; }}
.idx li {{ margin: 0.35rem 0; }}
.idx a {{ text-decoration: none; }}
.idx .cnum {{ color: var(--muted); font-variant-numeric: tabular-nums; margin-right: 0.5rem; }}
/* term index page */
.idx-terms ul {{ list-style: none; padding: 0; margin: 0 0 1rem; }}
.idx-terms li {{ margin: 0.3rem 0; }}
.idx-terms .idx-term {{ font-weight: 600; }}
.idx-terms .idx-refs {{ color: var(--muted); font-size: 14px; }}
.idx-terms .idx-refs a {{ margin-left: 0.15rem; }}
/* curated concept entry: a definition-of / examples-of sub-block under the concept name */
.idx-terms li.idx-concept {{ margin: 0.55rem 0; }}
.idx-concept .idx-subs {{ display: block; margin: 0.15rem 0 0 1rem; }}
.idx-concept .idx-sub {{ display: block; font-size: 14px; color: var(--muted); line-height: 1.6; }}
.idx-concept .idx-sub-lead {{ color: var(--muted); font-style: italic; margin-right: 0.35rem; }}
/* Underline the locators so a link is distinguished from the "definition of:" lead text without relying
   on color alone (axe link-in-text-block). */
.idx-concept .idx-sub a {{ margin-right: 0.4rem; text-decoration: underline; }}
/* iframe figure embed (the rewired mechanism map) */
figure.book-figure.catalogue-embed iframe {{ width: 100%; height: 600px; border: 1px solid var(--rule);
                                             border-radius: 6px; background: var(--paper); }}
/* TOP nav bar — the ☰ Contents disclosure only (the per-page sequence bar lives at the bottom now). */
nav.toc .toc-inner {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
                      gap: 0.7rem 1.4rem; }}
nav.toc details {{ flex: 0 0 auto; }}
/* When the reader opens the Contents disclosure, let it claim the full row so the chapter list flows at
   full width under the summary. */
nav.toc details[open] {{ flex: 1 1 100%; }}
"""


def _chap_ref(c: dict) -> str:
    """The 'N.M' reference for a numbered chapter, or '' for front/back matter."""
    return "" if c.get("is_matter") or c.get("is_appendix") else str(c["seq"])


def _toc_prefix(c: dict) -> str:
    ref = _chap_ref(c)
    return f"{ref}&nbsp; " if ref else ""


def _pager_label(c: dict) -> str:
    ref = _chap_ref(c)
    prefix = f"{ref} · " if ref else ""
    return f'{prefix}{c["chapter_title"]}'


BOOK_INDEX_SLUG = "book-index"  # the autogenerated term index page (see build_index_page)
_FIGURES_GALLERY_SLUG = "figures"  # the autogenerated figures-only page (see build_figures_page)
_BIBLIOGRAPHY_SLUG = "bibliography"  # the end-of-book alphabetical bibliography (see build_bibliography_page)


def _chapter_nav(chapters: list[dict], idx: int) -> dict:
    """The per-page navigation for the chapter at `idx`, as a single left→right sequence:

        Table of contents « Beginning of part « Previous chapter │ THIS CHAPTER │ Next chapter » Next part » Index

    Backward controls fill the left zone, forward controls the right, the current chapter names the centre
    (a non-link). An unavailable target is OMITTED, not disabled — Table of contents and Index anchor the
    zone edges and never drop, so the skeleton stays stable while the inner pills (Beginning-of-part,
    Prev/Next-chapter, Next-part) come and go. Every page carries a real part number, so the same code path
    covers front-matter, body, back-matter, and appendices with no special-casing.

    Returns `{"back": [(label, href, aria)], "name": str, "fwd": [(label, href, aria)]}`.
    """
    cur = chapters[idx]
    first_of_part = next((c for c in chapters if c["part"] == cur["part"]), cur)
    back: list[tuple[str, str, str]] = []
    fwd: list[tuple[str, str, str]] = []
    # 1. Table of contents — always (the structural chapter-list landing).
    back.append(("« Table of contents", "index.html", "Table of contents"))
    # 2. Beginning of part — only when not already on the part's first page (else it would self-link).
    if first_of_part["slug"] != cur["slug"]:
        back.append(("« Beginning of part", f'{first_of_part["slug"]}.html',
                     f'Beginning of {_part_label(cur)}'))
    # 3. Previous chapter — the strict reading-order predecessor (may cross a part boundary).
    if idx > 0:
        back.append(("« Previous chapter", f'{chapters[idx - 1]["slug"]}.html',
                     f'Previous chapter — {_pager_label(chapters[idx - 1])}'))
    # 5. Next chapter — the strict reading-order successor (may cross a part boundary).
    if idx + 1 < len(chapters):
        fwd.append(("Next chapter »", f'{chapters[idx + 1]["slug"]}.html',
                    f'Next chapter — {_pager_label(chapters[idx + 1])}'))
    # 6. Next part — the first later chapter whose part number differs.
    nxt_part = next((c for c in chapters[idx + 1:] if c["part"] != cur["part"]), None)
    if nxt_part:
        fwd.append(("Next part »", f'{nxt_part["slug"]}.html',
                    f'Next part — {_part_label(nxt_part)}'))
    # 7. Index — always (the alphabetised term index sits after the appendix).
    fwd.append(("Index »", f"{BOOK_INDEX_SLUG}.html", "Index of terms"))
    return {"back": back, "name": _pager_label(cur), "fwd": fwd}


def _render_chapnav(back: list[tuple[str, str, str]], name: str,
                    fwd: list[tuple[str, str, str]]) -> str:
    """Render one chapter-nav bar: a backward zone, the centred current-page name (a non-link `<span>`, so
    no empty-anchor html-validate risk), a forward zone. Shared by the in-order chapter pages and the
    generated pages (term index, figures gallery, bibliography). Each pill carries an explicit aria-label
    because the `«`/`»` glyphs read poorly aloud."""
    def pill(label: str, href: str, aria: str) -> str:
        return (f'<a href="{html.escape(href, quote=True)}" '
                f'aria-label="{html.escape(aria, quote=True)}">{html.escape(label)}</a>')
    back_html = "".join(pill(*t) for t in back)
    fwd_html = "".join(pill(*t) for t in fwd)
    name_html = (f'<span class="chapnav-here" title="{html.escape(name, quote=True)}">'
                 f'{html.escape(name)}</span>')
    return (f'<nav class="chapnav" aria-label="Chapter navigation">'
            f'<div class="chapnav-back">{back_html}</div>{name_html}'
            f'<div class="chapnav-fwd">{fwd_html}</div></nav>')


def _chapter_nav_html(chapters: list[dict], idx: int) -> str:
    nav = _chapter_nav(chapters, idx)
    return _render_chapnav(nav["back"], nav["name"], nav["fwd"])


def _static_nav_html(name: str, back_extra: list[tuple[str, str, str]] | None = None,
                     fwd_extra: list[tuple[str, str, str]] | None = None) -> str:
    """A fixed chapter-nav bar for the generated pages that sit outside the chapter reading order (term
    index, figures gallery, bibliography). Table of contents anchors the left, the page name centres, Index
    anchors the right; callers pass any page-specific extra pills."""
    back: list[tuple[str, str, str]] = [("« Table of contents", "index.html", "Table of contents")]
    back += back_extra or []
    fwd: list[tuple[str, str, str]] = list(fwd_extra or [])
    fwd.append(("Index »", f"{BOOK_INDEX_SLUG}.html", "Index of terms"))
    return _render_chapnav(back, name, fwd)


def toc_html(chapters: list[dict], current_slug: str | None) -> str:
    """The top-of-page navigation: a `☰ Contents` disclosure listing every chapter (current highlighted).
    This disclosure is the sole quick-jump at the top; the left→right sequence bar (`_chapter_nav_html`)
    renders bottom-only, killing the old top/bottom duplication. The `<ol>` links every chapter, which is
    what keeps the reachability gate green."""
    rows = []
    last_part = None
    for c in chapters:
        if c["part"] != last_part:
            rows.append(f'<li class="part">{html.escape(_part_label(c))}</li>')
            last_part = c["part"]
        cls = "current" if c["slug"] == current_slug else ""
        rows.append(
            f'<li><a class="{cls}" href="{c["slug"]}.html">'
            f'{_toc_prefix(c)}{html.escape(c["chapter_title"])}</a></li>'
        )
    inner = "\n".join(rows)
    return (
        '<nav class="toc" aria-label="Table of contents"><div class="toc-inner"><details>'
        "<summary>☰&nbsp; Contents</summary>"
        f'<ol>{inner}</ol></details></div></nav>'
    )


def _part_label(c: dict) -> str:
    """The heading a Part gets in the TOC / index. Front and back matter and the appendix name
    themselves; numbered Parts get 'Part N — Title'."""
    if c.get("is_appendix"):
        return c["part_title"]
    if c["part"] in (0, 6):
        return c["part_title"]
    return f'Part {c["part"]} — {c["part_title"]}'


def _kicker_html(chapters: list[dict], idx: int, num_label: str) -> str:
    """The chapter-header kicker with both halves as navigation links: the 'Part N — Title' half jumps to
    that Part's FIRST chapter (its beginning in reading order); the 'Chapter N.M' half jumps to the book
    Contents. The links keep the kicker's understated small-caps look (accent colour, underline on hover
    only — see the `.kicker a` CSS). Front/back matter and appendix pages carry only the part half."""
    c = chapters[idx]
    part_first = next((p for p in chapters if p["part"] == c["part"]), c)
    part_text = html.escape(_part_label(c))
    part_link = (
        f'<a href="{part_first["slug"]}.html" '
        f'aria-label="Beginning of {html.escape(_part_label(c), quote=True)}">{part_text}</a>'
    )
    if c.get("is_appendix") or c.get("is_matter"):
        return part_link
    # Numbered chapter — the second half links to the whole-book Contents (chapter list).
    chap_link = (
        f'<a href="index.html" aria-label="Book contents — jump to the chapter list">'
        f'{html.escape(num_label)}</a>'
    )
    return f'{part_link} &nbsp;::&nbsp; {chap_link}'


def page(title: str, toc: str, main: str, mermaid: bool = False, provenance: str = "",
         head_meta: str = "") -> str:
    runtime = MERMAID_CDN if mermaid else ""
    # <main> landmark so the content is a single main region (axe landmark-one-main / region). It carries
    # an aria-label of the page title so it stays a UNIQUELY-NAMED main landmark even when a page embeds the
    # mechanism-map figure in an <iframe> — axe flattens the iframe, and the figure has its own <main>; two
    # unnamed main landmarks would trip landmark-unique, so name this one.
    label = html.escape(title, quote=True)
    # `provenance` is an optional HTML comment sat right after `<html>`, mirroring catalog.py's own
    # "GENERATED by ... — DO NOT EDIT" banner placement on its rendered pages. Most book pages render from
    # tracked markdown (the markdown source itself is the record — see book/AGENTS.md), so this stays "" by
    # default; a page with NO markdown source of its own (an assembled projection like the figures gallery)
    # passes one so a reader who opens the raw HTML still finds the regen path.
    return (
        f'<!DOCTYPE html>\n<html lang="en">{provenance}<head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'{head_meta}'
        f"<title>{html.escape(title)}</title>{FONTS_LINK}<style>{CSS}</style></head><body>"
        f'{toc}<main class="wrap" aria-label="{label}">{main}</main>{runtime}</body></html>\n'
    )


def _epigraph_html(part: int) -> str:
    """The Part-opener epigraph block for the first chapter of a numbered Part, or '' if none."""
    epi = _PART_EPIGRAPHS.get(part)
    if not epi:
        return ""
    quote, attr = epi
    return (
        f'<div class="part-epigraph">{inline(quote)}'
        f'<span class="attr">— {inline(attr)}</span></div>'
    )


# ─────────────────────────── Appendix — the pattern catalogue (GoF format) ───────────────────────────
# Generated at build time from the catalogue entry .md files, so the appendix stays in sync with the
# catalogue rather than duplicating its text. Each entry is re-projected into the classic Gang-of-Four
# Design-Patterns layout: Intent · Motivation · Applicability · Structure · Sample Code · Consequences ·
# Known Uses · Related Patterns. The Structure (a Mermaid diagram) and Sample Code slots are injected from
# a per-entry "fill" markdown under `appendix-fills/<role>/<slug>.md`, keyed by the catalogue entry slug;
# an entry with no fill falls back to a visible TODO note.

# role dir -> (display group name, ordering key). Mirrors INDEX.md's role grouping.
_APPENDIX_ROLES = [
    ("agent", "Agent"),
    ("models-bridge", "Models-bridge"),
    ("product", "Product"),
]

# GoF section label -> the catalogue section header prefix it is drawn from.
_SECTION_SOURCES = [
    ("Motivation", "Motivation"),
    ("Applicability", "Prerequisites"),
    ("Consequences", "Consequences"),
    ("Known Uses", "Known uses"),
    ("Related Patterns", "Related mechanisms"),
]

# Where the per-entry Structure + Sample Code fills live (tracked, so the CI build sees them). One file per
# catalogue entry, keyed by the entry's SLUG (the fill's filename stem matches the catalogue entry stem).
_FILLS_DIR = HERE / "appendix-fills"


def _extract_fill_slot(text: str, heading: str) -> str | None:
    """Return the markdown body of the fill's `### <heading>` section (through the next `### ` or EOF),
    stripped, or None if the section is absent. Preserves fenced blocks verbatim — the Structure fill is a
    ```mermaid block plus an accessible-description line; the Sample Code fill is framing prose plus a code
    block (or, for a policy control, a prose "no sample code" note with no fence)."""
    m = re.search(rf"^###\s+{re.escape(heading)}\s*$(.*?)(?=^###\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else None


def _load_fill(role_dir: str, slug: str) -> dict[str, str | None]:
    """Load the Structure + Sample Code slots for one catalogue entry from its fill file, keyed by slug.
    Missing file or missing slot → None for that slot (the generator renders a TODO fallback)."""
    path = _FILLS_DIR / role_dir / f"{slug}.md"
    if not path.is_file():
        return {"structure": None, "sample": None}
    text = path.read_text(encoding="utf-8")
    return {
        "structure": _extract_fill_slot(text, "Structure"),
        "sample": _extract_fill_slot(text, "Sample Code"),
    }


def _entry_title(text: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def _entry_intent(text: str) -> str:
    """The `**Intent** — …` line (may wrap across lines up to the metadata card)."""
    m = re.search(r"\*\*Intent\*\* —\s*(.+?)(?:\n\n|\n\|)", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def _entry_move(text: str) -> str | None:
    """The Move value (`constraint`/`sensor`/`package`) parsed from the entry's metadata card `| Move | … |`
    row — the `code`-spanned token, the same source the census reads. Returns None if the row is absent or
    carries no `code`-spanned value (so a mechanism with no Move simply gets no `package` marker)."""
    m = re.search(r"^\|\s*Move\s*\|(.+)$", text, re.M)
    if not m:
        return None
    token = re.search(r"`([a-z-]+)`", m.group(1))
    return token.group(1) if token else None


def _fold_wrapped_bullets(md: str) -> str:
    """Join a bullet's wrapped continuation lines onto the bullet line, so the book's simple list parser
    (which requires every line of a list block to start with `- `) sees one line per bullet. The catalogue
    entries wrap long bullets across lines; without folding they render as a paragraph."""
    out: list[str] = []
    for ln in md.splitlines():
        stripped = ln.strip()
        if out and stripped and not stripped.startswith(("- ", "#", "|", ">", "```")) \
                and out[-1].strip().startswith("- "):
            out[-1] = out[-1].rstrip() + " " + stripped
        else:
            out.append(ln)
    return "\n".join(out)


def _entry_section(text: str, prefix: str) -> str:
    """The markdown body of the `## <prefix>…` section (through the next `## `), stripped. Wrapped bullet
    continuation lines are folded so the book's list parser renders them as list items, not a paragraph."""
    lines = text.splitlines()
    body: list[str] = []
    capturing = False
    for ln in lines:
        if ln.startswith("## "):
            if capturing:
                break
            capturing = ln[3:].strip().startswith(prefix)
            continue
        if capturing:
            body.append(ln)
    return _fold_wrapped_bullets("\n".join(body).strip())


_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _rewrite_entry_links(md: str, entry_dir: pathlib.Path) -> str:
    """Rewrite relative `.md` links from a catalogue entry so they resolve from `book/*.html`. An
    entry-relative `foo.md` / `../fam/bar.md` becomes `../<repo-relative>.html`; absolute URLs and
    anchors are left alone. Keeps the appendix's cross-references live on the built site."""
    def repl(m: "re.Match[str]") -> str:
        label, url = m.group(1), m.group(2).strip()
        if url.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor
        if not url.endswith(".md"):
            return m.group(0)
        try:
            target = (entry_dir / url).resolve().relative_to(ROOT.resolve())
        except ValueError:
            return m.group(0)  # points outside the repo — leave as-is
        tgt = target.as_posix()
        # `downloads/*.md` are raw assets shipped as `.md` (NOT rendered to `.html`) — keep the `.md`
        # extension, matching catalog.py's own link-rewrite rule; everything else points at rendered HTML.
        if "downloads/" in tgt:
            return f"[{label}](../{tgt}{anchor})"
        return f"[{label}](../{tgt[:-3]}.html{anchor})"
    return _MD_LINK_RE.sub(repl, md)


def _appendix_entries() -> list[dict]:
    """Read every catalogue entry .md → an ordered list of GoF-projected pattern records, grouped by role."""
    out: list[dict] = []
    for role_dir, group in _APPENDIX_ROLES:
        role_root = ROOT / role_dir
        if not role_root.is_dir():
            continue
        paths = sorted(role_root.glob("*/*.md"))
        for p in paths:
            text = p.read_text(encoding="utf-8")
            rel = p.relative_to(ROOT).as_posix()
            family = p.parent.name
            slug = p.stem
            sections = {label: _rewrite_entry_links(_entry_section(text, src), p.parent)
                        for label, src in _SECTION_SOURCES}
            out.append({
                "group": group,
                "role_dir": role_dir,
                "family": family,
                "slug": slug,           # the anchor id + the fill-lookup key
                "rel_md": rel,
                # link back to the rendered catalogue entry (two levels up from book/appendix-*.html to root)
                "catalogue_html": "../" + rel[:-3] + ".html",
                "name": _entry_title(text, p.stem),
                "intent": _rewrite_entry_links(_entry_intent(text), p.parent),
                "move": _entry_move(text),      # constraint | sensor | package | None — for the package marker
                "sections": sections,
                "fill": _load_fill(role_dir, slug),
            })
    return out


# ─────────────────────────── Print-appendix projection: the flagship subset ───────────────────────────
# The PRINT appendix projects only the ~29 FLAGSHIP mechanisms; the WEB catalogue keeps all 83. The flagship
# set is DERIVED at build time from the curation signal already in the repo — catalogue-classification.json's
# `dispositions` (the keep-as-L2 canonical set) — plus a thin manifest that declares the deviations (a few
# print promotions, the entries represented in the intro/Part-5 instead of as pages). Nothing is deleted:
# every omitted pattern stays live on the web and reachable from the appendix's complete web-index.
_CLASSIFICATION_PATH = ROOT / "book-models" / "catalogue-classification.json"
_PRINT_MANIFEST_PATH = ROOT / "book-models" / "print-appendix-manifest.json"


def _load_classification() -> dict[str, dict[str, str]]:
    """Read catalogue-classification.json's `dispositions` → `{bare-slug: {"head": <token>, "parent": <name>}}`.
    `head` is the leading disposition token (`keep-as-L2` / `demote-to-L3-under` / `merge-into` / `lift-to-L1`
    / `move-to-book-case`); `parent` is the canonical pattern name the rest of the disposition names (the L2 a
    demoted/merged entry folds under — used for the web-index '· under <Canonical>' tag). Keyed by the bare
    entry slug (the path's last segment), the same key `build_appendix_chapters` filters on. Fail-loud if the
    file is missing (a projection with no curation signal is a bug, not a soft degrade — same contract as
    `_resolve_stack_members`)."""
    if not _CLASSIFICATION_PATH.is_file():
        raise SystemExit(f"print-appendix projection needs {_CLASSIFICATION_PATH} — it is missing")
    data = json.loads(_CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for full_slug, rec in data.get("dispositions", {}).items():
        disposition = (rec.get("disposition") or "").strip()
        head, _, rest = disposition.partition(" ")
        bare = full_slug.rsplit("/", 1)[-1]
        out[bare] = {"head": head, "parent": rest.strip()}
    return out


def _load_print_manifest(cls: dict[str, dict[str, str]] | None = None) -> dict:
    """Read print-appendix-manifest.json → the declared print-projection deviations (`print_promotions`,
    `intro_l1_principles`, `appendix_exclude`, `appendix_e`, `stack_compression`). Validate every slug it
    lists names a real catalogue entry, so a typo fails the build loud rather than silently dropping or
    inventing a flagship. Fail-loud if the file is missing."""
    if not _PRINT_MANIFEST_PATH.is_file():
        raise SystemExit(f"print-appendix projection needs {_PRINT_MANIFEST_PATH} — it is missing")
    if cls is None:
        cls = _load_classification()
    data = json.loads(_PRINT_MANIFEST_PATH.read_text(encoding="utf-8"))
    for field in ("print_promotions", "intro_l1_principles", "appendix_exclude"):
        for slug in data.get(field, []):
            if slug not in cls:
                raise SystemExit(
                    f"print-appendix-manifest.json {field!r} lists {slug!r} — it matches no catalogue entry "
                    f"under agent/ · models-bridge/ · product/ (typo, or the entry was renamed)")
    return data


def _flagship_slugs() -> set[str]:
    """The bare slugs the PRINT appendix emits a page for: the keep-as-L2 canonical set (from the
    classification) UNION the manifest's `print_promotions`, MINUS its `appendix_exclude`. The default
    manifest yields 24 keep-as-L2 + 5 promotions = 29 (the excludes name entries already outside keep-as-L2,
    so they subtract nothing — they are a drift guard, not a reduction)."""
    cls = _load_classification()
    manifest = _load_print_manifest(cls)
    keep_as_l2 = {slug for slug, rec in cls.items() if rec["head"] == "keep-as-L2"}
    promotions = set(manifest.get("print_promotions", []))
    exclude = set(manifest.get("appendix_exclude", []))
    return (keep_as_l2 | promotions) - exclude


# Authored chapter links to an appendix pattern page: `](appendix-<a|b|c>-<slug>.html[#frag])`. The main
# narrative cross-references mechanisms by their in-book page; when a mechanism is non-flagship (its page is
# dropped from the print projection), the link is redirected to the live WEB catalogue entry — the SAME
# flagship→in-book / non-flagship→web rule the stack links and the web-index follow (uniformity, not a
# special case). A flagship target is left untouched.
_APPENDIX_BODY_LINK_RE = re.compile(r"\(appendix-[abc]-([a-z0-9-]+)\.html(?:#[^)]*)?\)")
_WEB_REDIRECT_CACHE: dict[str, str] | None = None


def _web_redirect_map() -> dict[str, str]:
    """`{slug: web-catalogue-URL}` for every NON-FLAGSHIP mechanism (the ones the print appendix omits).
    Computed once from the entry records + the flagship set, then cached — the redirect below consults it per
    authored link."""
    global _WEB_REDIRECT_CACHE
    if _WEB_REDIRECT_CACHE is None:
        flag = _flagship_slugs()
        _WEB_REDIRECT_CACHE = {rec["slug"]: rec["catalogue_html"]
                               for rec in _appendix_entries() if rec["slug"] not in flag}
    return _WEB_REDIRECT_CACHE


def _redirect_dropped_appendix_links(md: str) -> str:
    """Rewrite an authored `](appendix-<letter>-<slug>.html)` cross-reference to the WEB catalogue entry when
    `<slug>` is a non-flagship mechanism the print appendix no longer emits a page for; a flagship link (its
    page still exists) is left as-is. Any `#fragment` is dropped — the web entry carries its own anchors —
    so a chapter's 'learn more about this mechanism' link stays live after the print projection dropped the
    in-book page, instead of dangling as a missing target."""
    redirect = _web_redirect_map()
    def repl(m: "re.Match[str]") -> str:
        web = redirect.get(m.group(1))
        return f"({web})" if web is not None else m.group(0)
    return _APPENDIX_BODY_LINK_RE.sub(repl, md)


# The eight GoF pattern elements, in canonical reading order. Structure's diagram leads the page (visual
# first); its `## Structure` heading still appears in canonical position, linking up to the diagram. The
# element TOC lists only the elements actually present on a given page.
_GOF_ELEMENTS = [
    "Intent",
    "Motivation",
    "Applicability",
    "Structure",
    "Sample Code",
    "Consequences",
    "Known Uses",
    "Related Patterns",
]


def _element_anchor(name: str) -> str:
    """The `{#el-<name>}` anchor slug for a GoF element heading, for the in-page element TOC to link to."""
    return "el-" + name.lower().replace(" ", "-")


# Per-page DISPLAY labels for GoF element headings that differ from the internal element key. The book has
# exactly one live system (DocAble), so the classic GoF "Known Uses" element reads as "Example use within
# DocAble" on the appendix pattern pages. The internal key stays "Known Uses" (it keys `_GOF_ELEMENTS`, the
# `sections` dict, and the `el-known-uses` anchor); only the rendered heading + element-TOC label change.
# The STANDALONE catalogue entry .md keeps "Known uses" — "within DocAble" would dangle there — so this
# remap lives ONLY in the book-appendix rendering.
_ELEMENT_DISPLAY = {
    "Known Uses": "Example use within DocAble",
}


def _element_label(el: str) -> str:
    """The reader-facing heading/TOC label for a GoF element on a book-appendix pattern page."""
    return _ELEMENT_DISPLAY.get(el, el)


def _pattern_elements_present(rec: dict) -> list[str]:
    """Which of the eight GoF elements this pattern page renders. Intent, Structure, and Sample Code are
    always present (Structure/Sample Code fall back to a visible TODO); the five catalogue-sourced slots
    appear only when the entry carries that section."""
    present: list[str] = []
    for el in _GOF_ELEMENTS:
        if el == "Intent":
            if rec["intent"]:
                present.append(el)
        elif el in ("Structure", "Sample Code"):
            present.append(el)  # always shown (diagram/code fill or a TODO fallback)
        elif rec["sections"].get(el):
            present.append(el)
    return present


def _appendix_pattern_page_md(rec: dict, stack_membership: dict[str, list[tuple[str, str]]] | None = None) -> str:
    """One pattern rendered as a WHOLE PAGE of GoF-layout markdown. The pattern NAME is the page `<h1>`
    (from the chapter dict's `chapter_title`), so this body emits no leading `#`/`##` name heading — it
    leads with the Structure diagram (visual first), then an in-page table of contents of the elements
    present, then the eight elements as `## ` (h2) headings in canonical order. External `#<slug>` links
    still resolve: the slug anchor rides on the projection note. The Structure diagram is rendered at the
    top; its `## Structure` heading sits in canonical position and links back up to the diagram.

    When `stack_membership` maps this mechanism's slug to one or more stacks, a derived 'Part of these
    stacks: …' line is emitted under the projection note (member→stack back-links, single-sourced from the
    same `role:<slug>` tokens as the forward links). A mechanism in no stack gets no such line."""
    fill = rec.get("fill") or {}
    safe = rec["name"].replace('"', "'")
    present = _pattern_elements_present(rec)
    parts: list[str] = []

    # 1. VISUAL FIRST — the Structure diagram (or its TODO fallback) leads the page, under the header. The
    #    canonical `## Structure` heading (below, in element order) carries the `#el-structure` anchor both
    #    the element TOC and the reader use to return here.
    parts += [f"*The Structure of {safe} — its shape at a glance:*", ""]
    if fill.get("structure"):
        parts += [fill["structure"], ""]
    else:
        parts += [f"[FILL IN: a Structure diagram for *{safe}* is not yet authored.]", ""]

    # 2. PROJECTION NOTE — provenance link back to the live catalogue entry.
    src_note = (f'*Projected from the catalogue entry [{rec["family"]} / {rec["name"]}]'
                f'({rec["catalogue_html"]}).*')
    parts += [src_note, ""]

    # 2b. STACK BACK-LINKS — if this mechanism is a member of one or more stacks, tell the reader so and
    #     link into each stack's Appendix-D page. Derived from the same `role:<slug>` tokens as the forward
    #     links (single-sourced); a mechanism in no stack gets no line (absence reads as 'stands alone').
    memberships = (stack_membership or {}).get(rec["slug"], [])
    if memberships:
        links = ", ".join(f"[{title}]({page_slug}.html)" for title, page_slug in memberships)
        parts += [f"**Part of these stacks:** {links}", ""]

    # The FIRST present element's heading carries the pattern's page-level `{#slug}` anchor (so external
    # `#<slug>` deep-links and any old figure fragments still land on this page); every other element gets
    # its `#el-<name>` anchor. The element TOC links to whichever id each element's heading actually bears.
    anchor_for = {}
    for i, el in enumerate(present):
        anchor_for[el] = rec["slug"] if i == 0 else _element_anchor(el)

    # 3. ELEMENT TOC — a short in-page list linking each element heading present on the page.
    toc_items = " · ".join(f"[{_element_label(el)}](#{anchor_for[el]})" for el in present)
    parts += [f"**On this page:** {toc_items}", ""]

    # 4. THE ELEMENTS — canonical order, each an `## ` (h2) heading carrying its TOC/legacy anchor.
    for el in _GOF_ELEMENTS:
        if el not in present:
            continue
        head = f"## {_element_label(el)} {{#{anchor_for[el]}}}"
        if el == "Intent":
            parts += [head, "", "**Intent** — " + rec["intent"], ""]
        elif el == "Structure":
            parts += [head, "", "The Structure diagram appears at the top of this page.", ""]
        elif el == "Sample Code":
            parts += [head, ""]
            if fill.get("sample"):
                parts += [fill["sample"], ""]
            else:
                parts += [f"[FILL IN: a Sample Code snippet for *{safe}* is not yet authored.]", ""]
        else:
            parts += [head, "", rec["sections"][el], ""]
    return "\n".join(parts).strip()


# The rewired mechanism-map figure lives beside the book pages so its chip links resolve at book depth.
_BOOK_FIGURE_NAME = "catalogue-figure.html"

# The opening page's fixed slug — the "front door" of the GoF appendix (see the opening-page layout).
_APPENDIX_OPENING_SLUG = "appendix-patterns"

# One-line human display name per family DIRECTORY, for the opening-page contents headings. Falls back to a
# title-cased dir name for a family not listed here (so a new family folder still renders, un-prettified).
_FAMILY_DISPLAY = {
    "context-and-dispatch": "Context & dispatch substrate",
    "gates-and-merge-train": "Gates & merge-train",
    "mediators-and-resource-locks": "Mediators & resource locks",
    "lifecycle-and-observability": "Lifecycle & observability",
    "governance-doc-controls": "Governance-doc controls",
    "system-models": "System models",
    "canonical-models-and-seams": "Canonical models & seams",
    "validation-and-conformance": "Validation & conformance",
    "regression-tests": "Regression tests",
    "provenance-and-attribution": "Provenance & attribution",
    "repair-vocabulary": "Repair vocabulary",
}

# The GoF4 opening prose for the front-door page — book voice, NO build-process confession. This frames the
# appendix as the catalogue rendered as a pattern language and names the eight pattern elements. The
# census-map figure and the contents list are appended after it by the opening-page builder.
_APPENDIX_OPENING_PROSE = """\
**The catalogue as a pattern language**

This appendix is the governance catalogue rendered as a pattern language. It borrows the style of \
[*Design Patterns*](https://en.wikipedia.org/wiki/Design_Patterns) by Gamma, Helm, Johnson, and Vlissides \
(the \"Gang of Four\"), which named and described a canonical set of reusable software-design patterns and \
wrote each one to a fixed template. Here each governance mechanism becomes one pattern, written the same way.

Every pattern follows the same template:

- **Intent** — the failure class this mechanism kills, and the shape that kills it.
- **Motivation** — the recurring failure told as a scenario, and why the naive fix does not hold.
- **Applicability** — the conditions under which reaching for this pattern pays off.
- **Structure** — a diagram of the moving parts and how they connect, drawn as a lighter reference \
schematic than the hand-drawn figures in the chapters.
- **Sample Code** — a concrete instance of the pattern.
- **Consequences** — what adopting it costs and buys, and the second-order effects to watch.
- **Example use within DocAble** — where the mechanism runs in DocAble.
- **Related Patterns** — the neighbours it composes with.

## These patterns interlock

**These patterns interlock; the unit of adoption is the package, not the lone pattern.** The Gang of \
Four wrote patterns that mostly stand alone — reach for a Visitor or an Adapter, drop it in beside code \
that knows nothing of the rest of the book. The mechanisms here do not work that way, because the method \
underneath them is model-based. A typed model is the core, and on its own it is inert; it earns its keep \
only welded to the governance that keeps it honest: the drift gate that holds it equal to the code, the \
ban-lint that routes every change through it. That welding is what the catalogue calls a **package**: \
{{package_count}} of the {{mechanism_count}} mechanisms carry one, most of them a model shipped with its \
own sensors. Above the single mechanism sits the **stack** — {{stack_count}} of them, each a handful of \
models, gates, and vocabularies that together make one governed capability. So this appendix leads with \
the compositional units. You meet the stacks and the packaged models first, because that is the grain at \
which a reader adopts a method rather than a trick; the single-mechanism pages wait underneath, one per \
pattern, for when you need to look one up.

**How this appendix is organized.** The catalogue is split into four lettered appendices, each a \
different view of the same mechanisms:

<!-- index-def: governance-target-agent -->
<!-- index-def: governance-target-models-bridge -->
<!-- index-def: governance-target-product -->
- **Appendix A — Agent patterns** — the mechanisms that govern the *fleet that produces the work*: how \
agents are dispatched, isolated, gated, and observed.
- **Appendix B — Models-bridge patterns** — the mechanisms built around the *typed models the fleet \
reasons through*: the shared map a bounded agent uses to operate a codebase larger than its context.
- **Appendix C — Product patterns** — the mechanisms that govern the *shipped artifact itself*: its \
canonical seams, its validation, and its conformance controls.
- **Appendix D — Mechanism Stacks** — packages of patterns that travel together, each attached to a \
concept you want to adopt whole.

Read a single page to adopt one mechanism. Read a family in order to see how a cluster of them reinforce \
each other. The map below is clickable: each mechanism links to its pattern page."""


# ─────────────────────────── Appendix D — Mechanism Stacks ───────────────────────────
# A "stack" is a package of mechanisms that travel together, attached to a concept (the MBSE stack, the
# self-operations stack, …). Each stack is authored as a markdown file under `appendix-stacks/`, holding a
# `### Concept` frame, a `### Mandatory members` list, and a `### Complementary members` list. Member
# bullets reference a catalogue mechanism by a `role:<entry-slug>` token, which the builder resolves to a
# live link into that mechanism's Appendix A/B/C pattern page (with its numbered locator prepended).

_STACKS_DIR = HERE / "appendix-stacks"

# The slug that heads Appendix D's Part — the stacks front-door page.
_APPENDIX_STACKS_OPENING_SLUG = "appendix-stacks"

# Stack files in reading order → (page-slug stem, display title). Each becomes one D.N page; the opening
# front-door page (D's chapter 0) precedes them. A file listed here but absent on disk is skipped.
_STACKS: list[tuple[str, str]] = [
    # The seven finalized flagship deep-dives (reframe 260803). Each walks its stack part by part — a goal,
    # an overview figure, and one six-field entry per member (role · failure · mechanism · seam ·
    # durability). The thin two-tier precursor pages were superseded and folded into these seven.
    ("provenance-fidelity-stack", "The provenance + fidelity stack"),
    ("model-coherence-stack", "The model-coherence stack"),
    ("specification-verification-stack", "The specification + verification stack"),
    ("observe-react-stack", "The observe → react loop"),
    ("resource-mediation-stack", "The resource-mediation stack"),
    ("governance-of-governance-stack", "The governance-of-governance stack"),
    ("context-management-stack", "The context-management stack"),
]

_APPENDIX_STACKS_OPENING_PROSE = """\
**Stacks: mechanisms that travel together**

A single pattern in the preceding appendices kills one failure class. In practice, though, mechanisms \
arrive in *clusters* — a concept you want to adopt (model-based engineering, a self-operating \
orchestrator, an auditable format seam) is not one mechanism but several that reinforce each other. \
This appendix names those clusters. Each **stack** attaches to a concept, lists the mechanisms that make \
it up, and says which of them you can leave out.

A stack composes at a different grain than a `package` move. A **package** is composition *inside* one \
mechanism — a constraint shipped already welded to its own dedicated sensors, still one catalogue entry. \
A **stack** is composition *across* several distinct mechanisms — many entries that together make one \
governed capability. Both travel together; the package is the intra-mechanism weld, the stack the \
inter-mechanism cluster.

Every stack sorts its members into two kinds:

- **Mandatory** — the stack *fails* without this member. Model-based engineering needs both the typed \
models AND the drift control that keeps them equal to the code; adopt the models alone and you ship a \
map the fleet will trust while it quietly lies. A self-operating orchestrator needs its work-templates. \
These are the members you cannot skip without breaking the concept.
- **Complementary** — layers on top for extra value, not required for correctness. Dynamic \
context-injection can sit on top of a semantic-lint stack to *prevent* the violation the lint already \
*catches*; heartbeats sharpen an observability stack that already sees and responds. Worth adopting, \
but the stack stands without them.

Each member links to its own pattern page in the earlier appendices. Read a stack to see which \
mechanisms you must adopt as a set, and which you can add later."""

_STACK_MEMBER_RE = re.compile(r"\brole:([a-z0-9-]+)\b")


def _stack_membership_index() -> dict[str, list[tuple[str, str]]]:
    """Invert the stack membership relation: `{member-slug: [(stack-title, stack-page-slug), …]}`. Derived
    from the same `role:<slug>` tokens `_resolve_stack_members` resolves — the ONE source of stack
    membership — so the forward links (stack→member) and these back-links (member→stack) can never disagree.
    Only stack files present on disk contribute; a member appearing in no stack simply gets no entry (the
    caller then emits no 'Part of these stacks' line, which reads as 'stands alone')."""
    index: dict[str, list[tuple[str, str]]] = {}
    for stem, title in _STACKS:
        path = _STACKS_DIR / f"{stem}.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        seen: set[str] = set()
        for m in _STACK_MEMBER_RE.finditer(text):
            slug = m.group(1)
            if slug in seen:               # a member listed twice in one stack counts once for that stack
                continue
            seen.add(slug)
            index.setdefault(slug, []).append((title, f"appendix-d-{stem}"))
    return index


def _resolve_stack_members(md: str, page_by_slug: dict[str, dict]) -> str:
    """Replace each `role:<entry-slug>` token in a stack file with a live link to that mechanism. A stack
    still names ALL of its members; the link's DESTINATION follows the print/web split:

    - **A FLAGSHIP member** (a mechanism with a page in this print appendix) links IN-BOOK, prefixed by its
      numbered locator — `role:pdf-model` → `[Appendix C - 3. PdfModel](appendix-c-pdf-model.html)`.
    - **A NON-FLAGSHIP member** (a valid entry the print appendix omits) links to its WEB catalogue page,
      marked `(online)` — `role:office-models` → `[Office Models (online)](../product/…/office-models.html)`.

    An unknown slug (matching NO catalogue entry) stays a build-loud error — it catches a typo before it
    ships a bare `role:foo` string. `page_by_slug` maps entry slug → the ordered pattern record for ALL 83
    entries; a flagship record carries `page_slug` / `appendix_letter` / `appendix_num`, a non-flagship one
    carries only `name` / `catalogue_html`, so the record's shape IS the flagship signal."""
    def repl(m: "re.Match[str]") -> str:
        slug = m.group(1)
        rec = page_by_slug.get(slug)
        if rec is None:
            raise SystemExit(
                f"appendix stack references unknown mechanism slug 'role:{slug}' — it matches no "
                f"catalogue entry under agent/ · models-bridge/ · product/")
        if "appendix_num" in rec:  # flagship — an in-book pattern page exists
            label = f"Appendix {rec['appendix_letter']} - {rec['appendix_num']}. {rec['name']}"
            return f"[{label}]({rec['page_slug']}.html)"
        # non-flagship but valid — link to the live web catalogue entry, marked (online)
        return f"[{rec['name']} (online)]({rec['catalogue_html']})"
    return _STACK_MEMBER_RE.sub(repl, md)


def build_stack_chapters(part: int, page_by_slug: dict[str, dict]) -> list[dict]:
    """Build the Appendix D chapter records: one opening front-door page (chapter 0), then one page per
    stack (D.1, D.2, …). Mirrors the role-appendix page shape — same Part, pager chain, and index locator
    machinery — so the book's TOC/pager/index render it with no special-casing. `page_by_slug` resolves each
    stack's `role:<slug>` member tokens to links into the role-appendix pages. Returns [] if no stack files
    are present."""
    stack_files = [(stem, title) for stem, title in _STACKS if (_STACKS_DIR / f"{stem}.md").is_file()]
    if not stack_files:
        return []

    chapters: list[dict] = []
    part_title = "Appendix D — Mechanism Stacks"

    # OPENING FRONT-DOOR PAGE — heads Appendix D (chapter 0, sorts before every stack).
    chapters.append({
        "slug": _APPENDIX_STACKS_OPENING_SLUG,
        "part": part,
        "part_title": part_title,
        "chapter": 0,
        "chapter_title": "Appendix D — Mechanism Stacks",
        "body_md": _APPENDIX_STACKS_OPENING_PROSE.strip(),
        "is_appendix": True,
        "mermaid": False,
    })

    # ONE PAGE PER STACK — D.1, D.2, … in the authored order.
    for i, (stem, title) in enumerate(stack_files, start=1):
        raw = (_STACKS_DIR / f"{stem}.md").read_text(encoding="utf-8")
        body = _resolve_stack_members(_fold_wrapped_bullets(raw.strip()), page_by_slug)
        chapters.append({
            "slug": f"appendix-d-{stem}",
            "part": part,
            "part_title": part_title,
            "chapter": i,                       # sorts after the opening page's chapter 0
            "chapter_title": f"Appendix D - {i}. {title}",
            "body_md": body,
            "is_appendix": True,
            "mermaid": False,
        })
    return chapters


# APPENDIX E — How to Write a Skill. Hand-authored, like the stacks Part (Appendix D): a front-door page
# whose prose lives here, then one authored markdown page under `appendix-skill-recipe/`. No catalogue
# projection — the recipe is a reference the author wrote, not a mechanism map.
_SKILL_RECIPE_DIR = HERE / "appendix-skill-recipe"

# The slug that heads Appendix E — the recipe front-door page.
_APPENDIX_SKILL_RECIPE_OPENING_SLUG = "appendix-skill-recipe"

# The single authored content page under the front-door → (page-slug stem, display title). Absent-on-disk
# files are skipped, so the front-door alone still renders if the content file is missing.
_SKILL_RECIPE_PAGES: list[tuple[str, str]] = [
    ("the-recipe", "The recipe — three steps"),
]

_APPENDIX_SKILL_RECIPE_OPENING_PROSE = """\
**A skill is a model of a domain an agent triggers into**

A skill is not a prompt, and it is not a checklist. It is a *model of a domain* — the frame an agent \
loads when a task in that domain arrives, so it reasons through the domain's own abstractions instead of \
from scratch. You met three of them earlier in this book: the skills that let the fleet write its prose, \
harden its own substrate, and operate itself. Here is how they were made.

All three were built the same way. A skill is not a bag of instructions that grew by accretion. Each of \
the book's skills started from one abstraction, layered independent facets on it, and tied them together \
with a governing principle. That construction is itself a reusable pattern: name it and you can write the \
next skill deliberately instead of by feel.

This appendix names that pattern as a three-step recipe and grounds each step in the three self-* skills \
you already met. Read the [Skills chapter](4.2-the-skills.html) for what those skills *do*; read on here \
for how they were *built*."""


def _recipe_web_url() -> str:
    """The absolute web URL of the full recipe page in the published web edition — for the print pointer.
    Built from repo-metadata.json's `pages_url` (the governed Pages identity); falls back to a bare page
    reference if the metadata is absent."""
    meta_path = ROOT / "book-models" / "repo-metadata.json"
    stem = _SKILL_RECIPE_PAGES[0][0] if _SKILL_RECIPE_PAGES else "the-recipe"
    page_ref = f"appendix-e-{stem}.html"
    if meta_path.is_file():
        pages_url = (json.loads(meta_path.read_text(encoding="utf-8")).get("pages_url") or "").rstrip("/")
        if pages_url:
            return f"{pages_url}/book/{page_ref}"
    return page_ref


def build_skill_recipe_chapters(part: int, for_print: bool = False) -> list[dict]:
    """Build the Appendix E chapter records: one front-door page (chapter 0) whose prose is authored inline,
    then one page per authored content file under `appendix-skill-recipe/` (E.1, …). Mirrors the stacks Part
    (Appendix D): a hand-authored appendix Part, rendered by the existing pager/TOC/index machinery with no
    catalogue projection. Every record carries `is_appendix: True`, so it renders with no special-casing.
    Returns [] if no content files are present (the front-door alone is not emitted without its content).

    When the print manifest sets `appendix_e == "pointer"` AND this is the print/PDF projection
    (`for_print=True`), Appendix E collapses to the front-door alone plus a one-paragraph pointer to the full
    recipe online — the content page is dropped from print. The WEB build (`for_print=False`) always keeps
    the full recipe, so the pointer's target stays live."""
    pages = [(stem, title) for stem, title in _SKILL_RECIPE_PAGES
             if (_SKILL_RECIPE_DIR / f"{stem}.md").is_file()]
    if not pages:
        return []

    pointer_mode = for_print and _load_print_manifest().get("appendix_e") == "pointer"

    chapters: list[dict] = []
    part_title = "Appendix E — How to Write a Skill"

    # FRONT-DOOR PAGE — heads Appendix E (chapter 0, sorts before the recipe). In pointer mode it carries the
    # one-paragraph online pointer (the content page below is dropped from print).
    front_body = _APPENDIX_SKILL_RECIPE_OPENING_PROSE.strip()
    if pointer_mode:
        front_body += (
            "\n\n**The full recipe — its three steps grounded in the three self-\\* skills — lives in the "
            f"web edition of this book:** [{pages[0][1]}]({_recipe_web_url()}). Open it there to read each "
            "step worked through in full."
        )
    chapters.append({
        "slug": _APPENDIX_SKILL_RECIPE_OPENING_SLUG,
        "part": part,
        "part_title": part_title,
        "chapter": 0,
        "chapter_title": "Appendix E — How to Write a Skill",
        "body_md": front_body,
        "is_appendix": True,
        "mermaid": False,
    })

    if pointer_mode:
        return chapters  # print stops at the front-door + pointer; web keeps the full recipe below

    # ONE PAGE PER AUTHORED FILE — E.1, E.2, … in listed order.
    for i, (stem, title) in enumerate(pages, start=1):
        raw = (_SKILL_RECIPE_DIR / f"{stem}.md").read_text(encoding="utf-8")
        chapters.append({
            "slug": f"appendix-e-{stem}",
            "part": part,
            "part_title": part_title,
            "chapter": i,                       # sorts after the front-door's chapter 0
            "chapter_title": f"Appendix E - {i}. {title}",
            "body_md": _fold_wrapped_bullets(raw.strip()),
            "is_appendix": True,
            "mermaid": False,
        })
    return chapters


def _family_order_from_index() -> dict[str, int]:
    """Read the family ordering from the census (`INDEX.md`) at build time, so the appendix order can't
    drift from it. Parses each `## <N>. <name>` census heading, then the `[family folder](<role>/<dir>/)`
    link in the section that follows, yielding `{family-dir: N}`. Falls back to an empty map (families then
    sort alphabetically) if `INDEX.md` is absent or unparseable — a soft degrade, not a build failure."""
    index_md = ROOT / "INDEX.md"
    if not index_md.is_file():
        return {}
    text = index_md.read_text(encoding="utf-8")
    order: dict[str, int] = {}
    current_n: int | None = None
    heading_re = re.compile(r"^##\s+(\d+)\.\s")
    folder_re = re.compile(r"\[family folder\]\((?:agent|models-bridge|product)/([^/)]+)/\)")
    for line in text.splitlines():
        hm = heading_re.match(line)
        if hm:
            current_n = int(hm.group(1))
            continue
        if current_n is not None:
            fm = folder_re.search(line)
            if fm:
                order.setdefault(fm.group(1), current_n)
                current_n = None
    return order


def _family_display(family_dir: str) -> str:
    """The human display name for a family directory — from the curated map, else a title-cased dir name."""
    return _FAMILY_DISPLAY.get(family_dir) or family_dir.replace("-", " ").title()


def _appendix_counts(ordered: list[dict]) -> dict[str, int]:
    """The live compositional counts the front-door framing cites — computed at build time from the same
    sources the census reads, so they cannot drift. `package_count`: entries whose Move is `package` (the
    per-card Move value, the census's own source); `mechanism_count`: the census total (the entry count);
    `stack_count`: the length of `_STACKS`. Only stack files present on disk are counted (mirrors what the
    stacks Part actually renders)."""
    present_stacks = sum(1 for stem, _t in _STACKS if (_STACKS_DIR / f"{stem}.md").is_file())
    # `flagship_count`: entries that carry an in-book pattern page (the ~29 the print appendix projects,
    # marked by `appendix_num` set in build_appendix_chapters); `web_only_count`: the census remainder that
    # stays online-only. `mechanism_count` remains the full census (a catalogue fact, not a print fact) so
    # the front-door's 'in print / online' framing can cite all three.
    flagship_count = sum(1 for rec in ordered if "appendix_num" in rec)
    return {
        "package_count": sum(1 for rec in ordered if rec.get("move") == "package"),
        "mechanism_count": len(ordered),
        "flagship_count": flagship_count,
        "web_only_count": len(ordered) - flagship_count,
        "stack_count": present_stacks,
    }


def _apply_appendix_counts(md: str, counts: dict[str, int]) -> str:
    """Substitute the front-door count tokens `{{package_count}}` / `{{mechanism_count}}` / `{{stack_count}}`
    with their live build-time values. The role-appendix front-door prose is assembled here (not routed
    through the chapter-file `_apply_metrics` pass), so it carries its own token substitution — same
    fail-loud contract: an unknown `{{token}}` stops the build rather than shipping a literal placeholder."""
    def repl(m: "re.Match[str]") -> str:
        key = m.group(1).strip()
        if key not in counts:
            raise SystemExit(f"appendix count token {{{{{key}}}}} has no computed value")
        return str(counts[key])
    return re.sub(r"\{\{\s*([a-z0-9_]+)\s*\}\}", repl, md)


def _stack_concept_first_sentence(stem: str) -> str:
    """The one-line capability summary for a stack: the first sentence of its `## Concept` section. Read at
    build time from the stack file, so the front-door bullet stays equal to the stack page's own framing.
    Returns '' if the file or its Concept section is absent (the caller then omits the sub-clause)."""
    path = _STACKS_DIR / f"{stem}.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^##\s+Concept\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return ""
    body = re.sub(r"\s+", " ", m.group(1)).strip()
    # First sentence: up to the first period that ends a sentence (followed by a space or end-of-string).
    dot = re.search(r"\.(?:\s|$)", body)
    sentence = body[: dot.start() + 1] if dot else body
    return sentence.strip()


def _appendix_stacks_summary_md() -> str:
    """The front-door 'Adopt by capability' block: one bullet per stack — its capability one-liner (the
    first sentence of the stack file's `## Concept`) plus a link to its Appendix-D page. Derived entirely
    from `_STACKS` (the single source for stack order) and the stack files themselves; no hand-maintained
    second list. Only stack files present on disk appear, matching what Appendix D renders."""
    bullets: list[str] = []
    for stem, title in _STACKS:
        if not (_STACKS_DIR / f"{stem}.md").is_file():
            continue
        concept = _stack_concept_first_sentence(stem)
        tail = f" — {concept}" if concept else ""
        bullets.append(f"- **[{title}](appendix-d-{stem}.html)**{tail}")
    if not bullets:
        return ""
    head = [
        "## Adopt by capability: the stacks",
        "",
        "A stack is a capability you adopt whole — a handful of mechanisms that reinforce each other. "
        "These are the reader's first navigable choice: pick the capability you want, then follow it into "
        "the mechanisms that make it up.",
        "",
    ]
    return "\n".join(head + bullets).strip()


def _appendix_contents_md(ordered: list[dict]) -> str:
    """The opening page's text table of contents, in census-map hierarchy: an `### ` (h3) heading per target
    (Agent / Models-bridge / Product), a `#### ` (h4) sub-heading per family, and a linked bullet list of
    the family's patterns under it. `ordered` is the already role/family-ordered pattern-record list; each
    record carries the page slug the pattern renders at, plus its per-appendix locator (`appendix_letter`,
    `appendix_num`) set by `build_appendix_chapters`, so the bullet reads `Appendix A - 1. <name>`. A
    mechanism whose Move is `package` carries a small inline `package` marker, so a reader sees which
    entries bundle their own sensors without leaving the list; a standalone atom carries no marker (absence
    reads as 'stands alone', which is correct)."""
    cls = _load_classification()
    parts: list[str] = ["## Reference: every mechanism", ""]
    last_group: str | None = None
    last_family: str | None = None
    for rec in ordered:
        if rec["group"] != last_group:
            # A blank line before each role heading (after the first) closes the previous role's last
            # bullet list, so `### <role>` starts its own block instead of merging into the last bullet.
            if last_group is not None:
                parts += [""]
            parts += [f"### {rec['group']}", ""]
            last_group, last_family = rec["group"], None
        if rec["family"] != last_family:
            # A blank line BEFORE each family sub-heading closes the previous family's bullet list, so the
            # heading starts its own block instead of lazy-continuing the last bullet (the old run-on). Each
            # family is its own `#### ` sub-heading; its mechanisms follow as a proper bulleted list.
            if last_family is not None:
                parts += [""]
            parts += [f"#### {_family_display(rec['family'])}", ""]
            last_family = rec["family"]
        marker = " `package`" if rec.get("move") == "package" else ""
        if "appendix_num" in rec:
            # FLAGSHIP — an in-book pattern page; link there, prefixed by its A-N locator.
            locator = f"Appendix {rec['appendix_letter']} - {rec['appendix_num']}."
            parts += [f"- {locator} [{rec['name']}]({rec['page_slug']}.html){marker}"]
        else:
            # NON-FLAGSHIP — omitted from print, live on the web; link to the catalogue entry, mark (online),
            # and (when known) tag the canonical L2 it folds under so the reader keeps the map's hierarchy.
            parent = cls.get(rec["slug"], {}).get("parent", "")
            under = f" · under {parent}" if parent else ""
            parts += [f"- [{rec['name']} (online)]({rec['catalogue_html']}){marker}{under}"]
    return "\n".join(parts).strip()


def build_appendix_chapters(next_part: int, for_print: bool = False) -> list[dict]:
    """Build appendix 'chapter' records — ONE PER FLAGSHIP PATTERN plus one opening front-door page — each
    mirroring the chapter dict shape so the existing pager/TOC/index machinery renders it. Ordering follows
    the census-map hierarchy: Environment → target (Agent A / Models-bridge B / Product C) → family (census
    order) → mechanism.

    The appendix is a PROJECTION: it emits a page only for the ~29 FLAGSHIP mechanisms (`_flagship_slugs()`),
    but it READS all 83 catalogue entries — the complete web-index on the opening page links every entry
    (flagship → in-book, non-flagship → web), the stacks name every member, and the mechanism-map figure
    routes every chip. Nothing is deleted; the omitted patterns stay live on the web. Returns [] if no
    entries are found. `for_print` is threaded to Appendix E (the pointer collapse is print-only)."""
    entries = _appendix_entries()
    if not entries:
        return []
    flagship = _flagship_slugs()

    family_order = _family_order_from_index()
    role_index = {group: i for i, (_r, group) in enumerate(_APPENDIX_ROLES)}
    role_letter = {group: chr(ord("A") + i) for i, (_r, group) in enumerate(_APPENDIX_ROLES)}

    # Order the records by (role, family census number, within-family slug) — the census-map hierarchy.
    def _sort_key(rec: dict) -> tuple:
        return (
            role_index.get(rec["group"], 99),
            family_order.get(rec["family"], 999),
            rec["family"],
            rec["slug"],
        )
    ordered = sorted(entries, key=_sort_key)
    # Per-appendix-letter running number (A-1, A-2, …, B-1, …) — the locator shown in the TOC, on each
    # pattern page's title, and in the book index. Assigned in reading order within each role letter, over
    # FLAGSHIP entries ONLY, so the locators are GAP-FREE (A-1…A-12, B-1…B-11, C-1…C-6) with no holes where a
    # non-flagship entry was skipped. A non-flagship record gets NO `page_slug` / `appendix_num`: the absence
    # is the flagship signal every downstream consumer (stack links, anchor map, web-index) reads.
    appendix_counter: dict[str, int] = {}
    for rec in ordered:
        if rec["slug"] not in flagship:
            continue
        letter = role_letter[rec["group"]]
        rec["page_slug"] = f"appendix-{letter.lower()}-{rec['slug']}"
        appendix_counter[letter] = appendix_counter.get(letter, 0) + 1
        rec["appendix_letter"] = letter
        rec["appendix_num"] = appendix_counter[letter]

    # Precompute the slug→pattern-page anchor map, then emit the rewired figure once (embedded on the
    # opening page only).
    anchor_map = _appendix_anchor_map(ordered)
    _emit_rewired_figure(anchor_map)

    # Live compositional counts + the member→stack membership index — both derived from the single sources
    # (per-card Move / `_STACKS` / the `role:<slug>` tokens), computed once and threaded through below.
    counts = _appendix_counts(ordered)
    stack_membership = _stack_membership_index()

    chapters: list[dict] = []

    # OPENING PAGE — heads Appendix A's Part (first appendix Part), sorts before every pattern (chapter 0).
    # Front-door narrative order (§2.3): frame → interlock → adopt-by-capability (stacks) → the whole map →
    # the atomic reference. The framing prose (frame + interlock) leads; the stack summary is the reader's
    # first navigable choice; the census map is 'every mechanism'; the reference list is the atomic lookup.
    opening_body = [
        _apply_appendix_counts(_APPENDIX_OPENING_PROSE, counts),
        "",
        _appendix_stacks_summary_md(),
        "",
        # The census map — the clickable visual index into the pattern pages, embedded here only.
        f"<!-- figure-iframe: {_BOOK_FIGURE_NAME} | The governance mechanism map — every mechanism in the "
        "catalogue, including the ones inside those stacks, organized by target zone and family. Click a "
        "mechanism to open its Gang-of-Four pattern. | The governance mechanism map: click any mechanism to "
        "open its Gang-of-Four pattern in this appendix. -->",
        "",
        _appendix_contents_md(ordered),
    ]
    chapters.append({
        "slug": _APPENDIX_OPENING_SLUG,
        "part": next_part,                     # heads the first appendix Part (Appendix A)
        "part_title": "Appendix A — Agent patterns",
        "chapter": 0,                          # sorts before every pattern in the Part
        "chapter_title": "Appendix — the pattern language",
        "body_md": "\n".join(opening_body).strip(),
        "is_appendix": True,
        "mermaid": False,                      # the map is an <iframe>, not an inline mermaid block
    })

    # ONE PAGE PER FLAGSHIP PATTERN — in census-map order; part = role's appendix Part, chapter sorts within
    # it by (family census number, within-family index) so the pager walks A→B→C family-by-family. Only
    # flagship records carry a `page_slug` / `appendix_num`, so the emission iterates the flagship subset.
    within_family_index = 0
    prev_family: str | None = None
    for rec in (r for r in ordered if r["slug"] in flagship):
        group = rec["group"]
        letter = role_letter[group]
        fam_n = family_order.get(rec["family"], 999)
        if rec["family"] != prev_family:
            within_family_index = 0
            prev_family = rec["family"]
        else:
            within_family_index += 1
        chapters.append({
            "slug": rec["page_slug"],
            "part": next_part + role_index[group],       # each role is its OWN Part (Appendix A / B / C)
            "part_title": f"Appendix {letter} — {group} patterns",
            # chapter sort key within the Part: family census number, then within-family index. +1 keeps
            # every pattern above the opening page's chapter 0 in Appendix A.
            "chapter": fam_n * 100 + within_family_index + 1,
            "chapter_title": f"Appendix {letter} - {rec['appendix_num']}. {rec['name']}",
            "body_md": _appendix_pattern_page_md(rec, stack_membership),
            "is_appendix": True,
            "mermaid": True,
        })

    # APPENDIX D — Mechanism Stacks. A NEW Part after the three role appendices (A/B/C), one opening page +
    # one page per stack. Each stack's member tokens link back into the role-appendix pages built above.
    page_by_slug = {rec["slug"]: rec for rec in ordered}
    stacks_part = next_part + len(_APPENDIX_ROLES)
    chapters += build_stack_chapters(part=stacks_part, page_by_slug=page_by_slug)

    # APPENDIX E — How to Write a Skill. A hand-authored Part after the stacks (its own front-door page +
    # the recipe page), rendered the same way — no catalogue projection, no role/family machinery. In the
    # print/PDF projection with `appendix_e == "pointer"` it collapses to the front-door + an online pointer.
    chapters += build_skill_recipe_chapters(part=stacks_part + 1, for_print=for_print)
    return chapters


def _role_dir_slug(group: str) -> str:
    return group.lower().replace(" ", "-")


_FIGURE_HREF_RE = re.compile(r'href="((?:agent|models-bridge|product)/[^"/]+/([^"/]+)\.html)"')
# Root-relative sibling pages the figure links to (census, codegen'd views, quick-start, dev-workflow) —
# these sit one dir up from book/, so re-point them with a `../` prefix in the book copy.
_FIGURE_ROOT_LINK_RE = re.compile(
    r'href="((?:index|catalogue-views|quick-start|development-workflow|ABSTRACTIONS|README)\.html)"')


def _emit_rewired_figure(anchor_map: dict[str, str]) -> None:
    """Copy the catalogue's clickable mechanism-map figure into `book/`, rewiring every mechanism chip so
    it links to that mechanism as rendered IN THIS APPENDIX (`appendix-<letter>-<role>.html#<slug>`) rather
    than to the live catalogue entry page. The figure is self-contained (inline SVG + inline styles, no
    script or CDN), so the copy stands alone at book depth; catalogue-root links (the census, the codegen'd
    views) are re-pointed one level up. Skips silently if the source figure is absent."""
    src = ROOT / "catalogue-figure.html"
    if not src.is_file():
        return
    doc = src.read_text(encoding="utf-8")

    def _mech(m: "re.Match[str]") -> str:
        slug = m.group(2)
        target = anchor_map.get(slug)
        # An unmapped mechanism (should not happen — every chip is a catalogue entry) keeps its original
        # link, re-pointed to the catalogue root so it still resolves from book depth.
        return f'href="{target}"' if target else f'href="../{m.group(1)}"'

    doc = _FIGURE_HREF_RE.sub(_mech, doc)
    # Catalogue-root pages (census, codegen'd views, dev-workflow) sit one dir up from book/.
    doc = _FIGURE_ROOT_LINK_RE.sub(lambda m: f'href="../{m.group(1)}"', doc)
    # Note in the served copy that it is generated/rewired (the source is hand-authored at the root).
    doc = doc.replace(
        "<head>",
        "<head>\n<!-- REWIRED COPY (generated by build_book_html.py): chips link into the book appendix. "
        "Edit the source at the catalogue root, not this copy. -->",
        1,
    )
    (HERE / _BOOK_FIGURE_NAME).write_text(doc, encoding="utf-8")


def _appendix_anchor_map(entries: list[dict]) -> dict[str, str]:
    """Map each catalogue entry slug → the URL the mechanism-map figure's chip should point at, following the
    print/web split. A FLAGSHIP entry (carrying `page_slug`, set by build_appendix_chapters) points at its
    in-book pattern page (`appendix-<letter>-<slug>.html`); a NON-FLAGSHIP entry points at its live WEB
    catalogue page (`../<role>/<family>/<slug>.html`, its `catalogue_html`). So the clickable map sends
    flagship chips into the print appendix and the rest to the web — nothing dangles."""
    return {e["slug"]: (f"{e['page_slug']}.html" if "page_slug" in e else e["catalogue_html"])
            for e in entries}


# ─────────────────────────── Curated concept index — index-def / index-example tags ───────────────────────────
# Two HTML-comment tags (book/AGENTS.md §6) let an author point the index at a concept's DEFINING
# paragraph and its EXAMPLE paragraphs, instead of a heading-heuristic occurrence scan. The harvest below
# walks every page in reading order, assigns each example a global anchor number, and validates the tags
# (a concept has one canonical definition; a slug must be registered; an example needs a definition).

_CONCEPT_RE = re.compile(r"-\s*concept:\s*([a-z0-9-]+)\s*\|\s*(.+?)\s*$")
#: The two-tier term registry line: `- term: <slug> | <tier>`, tier ∈ {section, local}. The tier annotation
#: that the drain's `terms:` / `section-terms:` tagging resolves against (index-terms.md §"Term tiers").
_TERM_TIER_RE = re.compile(r"-\s*term:\s*([a-z0-9-]+)\s*\|\s*(section|local)\s*$")
#: The two valid term tiers — the closed set the `term-tags-registered` lint checks membership against.
TERM_TIERS = ("section", "local")


def _load_term_tiers() -> dict[str, str]:
    """Read the two-tier term registry from `index-terms.md` → {slug: tier}. Every `- concept:` slug DEFAULTS
    to `tier: section` (seeding the 135 existing concepts as section-tier); an explicit `- term: <slug> |
    <tier>` row registers a new local term OR overrides a concept slug's default tier. This is the SSOT the
    drain's `terms:`/`section-terms:` tagging resolves against — one file, no parallel registry (index-terms.md
    §"Term tiers"). A `- term:` row for an unknown tier is a build-loud error (a typo, caught before it drops
    the term silently)."""
    tiers: dict[str, str] = {slug: "section" for slug in _load_concept_registry()}  # concepts default section
    it = HERE / _INDEX_TERMS_FILE
    if it.is_file():
        for line in it.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("- term:"):
                m = _TERM_TIER_RE.match(s)
                if not m:
                    raise SystemExit(f"index-terms.md: malformed `- term:` tier row {s!r} "
                                     f"(want `- term: <slug> | section|local`)")
                tiers[m.group(1)] = m.group(2)  # explicit row registers / overrides
    return tiers


def _load_concept_registry() -> dict[str, str]:
    """Read the `- concept: <slug> | <Display Name>` lines from `index-terms.md` → {slug: display}. A tag
    whose slug is absent from this registry is a build-loud error (catches a typo before it silently drops
    the concept). The display name is authored here once, not scraped from prose."""
    reg: dict[str, str] = {}
    it = HERE / _INDEX_TERMS_FILE
    if not it.is_file():
        return reg
    for line in it.read_text(encoding="utf-8").splitlines():
        m = _CONCEPT_RE.match(line.strip())
        if m:
            slug, display = m.group(1), m.group(2).strip()
            if slug in reg:
                raise SystemExit(f"index-terms.md: duplicate concept registration for '{slug}'")
            reg[slug] = display
    return reg


def _harvest_concept_tags(chapters: list[dict]) -> tuple[dict, dict]:
    """Walk every page's `body_md` in reading order for `index-def` / `index-example` tags. Returns
    `(registry, page_anchor_maps)`:

    - `registry` — {slug: {"display", "def": (page, anchor_id) | None, "examples": [(page, anchor_id), …]}}
      keyed by concept slug, examples in global reading order (anchor `idx-ex-<slug>-<n>`, n starting at 1).
    - `page_anchor_maps` — {page_slug: {(concept, kind, occ_on_page): anchor_id}} so the renderer can attach
      the exact anchor the index links to, matching per-page tag occurrence order.

    Fails loud on: a slug not registered in `index-terms.md`; a second `index-def` for one concept; an
    `index-example` for a concept that has no `index-def` anywhere in the book."""
    registry_names = _load_concept_registry()
    reg: dict[str, dict] = {}
    page_maps: dict[str, dict[tuple[str, str, int], str]] = {}
    ex_counter: dict[str, int] = {}

    def _slot(slug: str) -> dict:
        if slug not in registry_names:
            raise SystemExit(
                f"index tag references unregistered concept '{slug}' — add "
                f"`- concept: {slug} | <Display Name>` to {_INDEX_TERMS_FILE}")
        return reg.setdefault(
            slug, {"display": registry_names[slug], "def": None, "examples": []})

    for pg in chapters:
        pslug = pg["slug"]
        pmap = page_maps.setdefault(pslug, {})
        per_page_occ: dict[tuple[str, str], int] = {}
        for line in pg["body_md"].splitlines():
            s = line.strip()
            md = INDEX_DEF_RE.match(s)
            if md:
                slug = md.group(1)
                slot = _slot(slug)
                if slot["def"] is not None:
                    raise SystemExit(
                        f"duplicate index-def for concept '{slug}' — a concept has one canonical "
                        f"definition (already at {slot['def'][0]}, again on {pslug})")
                anchor = f"idx-def-{slug}"
                slot["def"] = (pg, anchor)
                occ = per_page_occ.get((slug, "def"), 0)
                pmap[(slug, "def", occ)] = anchor
                per_page_occ[(slug, "def")] = occ + 1
                continue
            me = INDEX_EXAMPLE_RE.match(s)
            if me:
                slug = me.group(1)
                _slot(slug)  # register / validate the slug
                n = ex_counter.get(slug, 0) + 1
                ex_counter[slug] = n
                anchor = f"idx-ex-{slug}-{n}"
                reg[slug]["examples"].append((pg, anchor))
                occ = per_page_occ.get((slug, "ex"), 0)
                pmap[(slug, "ex", occ)] = anchor
                per_page_occ[(slug, "ex")] = occ + 1

    # An example with no definition is a build-loud error.
    for slug, slot in reg.items():
        if slot["def"] is None and slot["examples"]:
            raise SystemExit(
                f"concept '{slug}' has index-example tag(s) but no index-def — mark its defining "
                f"paragraph with `<!-- index-def: {slug} -->`")
    return reg, page_maps


# ─────────────────────────── Book index — autogenerated term index ───────────────────────────
# Merge two term sources (the self-communicate LEXICON's house vocabulary + the book's own curated
# concepts/proper-nouns in `index-terms.md`), occurrence-scan every chapter + appendix page, keep the
# most significant sites per term (capped so the index reads curated, not a frequency dump), and emit a
# single alphabetized `book-index.html`. It is a soft, best-effort index: a term that never occurs in the
# prose is dropped, so the index only lists terms the reader can actually find.

_LEXICON_REL = ("..", "plugin", "mage", "skills", "self-communicate", "writing", "lexicon.md")
_INDEX_TERMS_FILE = "index-terms.md"
_MAX_REFS_PER_TERM = 4  # cap so the index reads curated, not a word-frequency dump
_MIN_TERM_LEN = 3       # skip 1–2 char "terms" (noise)


def _clean_term(raw: str) -> str:
    """Strip markdown/backticks and a trailing `@ch..` hint or a `(qualifier)` off a raw term string, for
    the display + match form. Keeps the term's core words."""
    t = raw.strip()
    t = re.sub(r"\s*@[\w-]+\s*$", "", t)               # drop the `@ch03` / `@context-a` chapter hint
    t = t.replace("`", "").replace("**", "").replace("*", "")
    # Drop a trailing parenthetical qualifier for the DISPLAY term (kept short); matching uses the head.
    return t.strip()


def _match_keys(term: str) -> list[str]:
    """The lowercase substrings to search the prose for, for one display term. Uses the term head (before a
    parenthetical) and, when a `/` alias-run is present, each alternative — so 'runbook / playbook' matches
    either word. Short/again-noisy fragments are dropped by the caller."""
    head = re.sub(r"\s*\([^)]*\)\s*", " ", term).strip()   # 'skill (soft control)' -> 'skill'
    parts = [p.strip() for p in re.split(r"\s*/\s*", head) if p.strip()]
    keys = parts or [head]
    return [k.lower() for k in keys if len(k) >= _MIN_TERM_LEN]


def _load_index_terms() -> list[str]:
    """Read the two term sources → an ordered, de-duplicated list of display terms. Source 1: the lexicon's
    bold first-column table terms (its house vocabulary). Source 2: the book's own `index-terms.md` bullets
    (concepts + proper nouns). A term appearing in both keeps its first (cleaned) form."""
    terms: list[str] = []
    seen: set[str] = set()

    def _add(raw: str) -> None:
        t = _clean_term(raw)
        if not t:
            return
        key = t.lower()
        if key not in seen:
            seen.add(key)
            terms.append(t)

    # Source 1 — the lexicon table's bold first-column terms.
    lex = HERE.joinpath(*_LEXICON_REL)
    if lex.is_file():
        for line in lex.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*\*\*(.+?)\*\*", line)
            if m:
                # A cell may hold two forms joined by ' / ' — keep the whole cell as one display term.
                _add(m.group(1))
    # Source 2 — the book's curated concepts + proper nouns (bulleted, may carry `@ch..`).
    it = HERE / _INDEX_TERMS_FILE
    if it.is_file():
        for line in it.read_text(encoding="utf-8").splitlines():
            m = re.match(r"-\s+(.+?)\s*$", line)
            if not m:
                continue
            raw = m.group(1)
            # Skip parenthetical-only meta bullets ("(timeline … — fill from context-b once drafted)").
            if raw.startswith("("):
                continue
            # Skip `concept: <slug> | <Display>` registry lines — those drive the curated concept index,
            # not the occurrence scan (their display names enter via the curated-entry path).
            if raw.startswith("concept:"):
                continue
            _add(raw)
    return terms


def _scan_term_refs(term: str, pages: list[dict]) -> list[dict]:
    """Find which pages mention `term`, ranked by significance. A page where the term appears in a heading
    (`# ` / `## ` / `### `) ranks above a body-only mention; ties break on reading order. Returns up to
    `_MAX_REFS_PER_TERM` page records."""
    keys = _match_keys(term)
    if not keys:
        return []
    scored: list[tuple[int, int, dict]] = []
    for order, pg in enumerate(pages):
        # Scan reader-visible prose only: strip the authored `<!-- point: … -->` decorators so a term that
        # appears solely inside a canonical-point never spawns a phantom occurrence reference.
        md = _strip_point_decorators(pg["body_md"])
        low = md.lower()
        if not any(k in low for k in keys):
            continue
        # Significance: does the term appear in a heading line on this page?
        in_heading = False
        for ln in md.splitlines():
            s = ln.strip()
            if s.startswith("#"):
                sl = s.lower()
                if any(k in sl for k in keys):
                    in_heading = True
                    break
        scored.append((0 if in_heading else 1, order, pg))
    scored.sort(key=lambda t: (t[0], t[1]))
    return [pg for _sig, _o, pg in scored[:_MAX_REFS_PER_TERM]]


def _index_ref_label(pg: dict) -> str:
    """The short locator shown beside an index term for one page: 'Appendix A', 'Preface', or 'Ch. N'."""
    if pg.get("is_appendix"):
        # Per-pattern titles read 'Appendix A - 1. Brief-linting' → locator 'Appendix A - 1'; a stack page
        # 'Appendix D - 1. The MBSE stack' → 'Appendix D - 1'. An opening front-door page
        # ('Appendix — the pattern language' / 'Appendix D — Mechanism Stacks', no numbered '. ') → its
        # 'Appendix …' prefix via the '—' split. Prefer the '<letter> - <n>.' numbered split.
        title = pg["chapter_title"]
        m = re.match(r"^(Appendix\s+[A-Z]\s+-\s+\d+)\.", title)
        if m:
            return m.group(1).strip()
        if "·" in title:
            return title.split("·")[0].strip()
        if "—" in title:
            return title.split("—")[0].strip()
        return title
    if pg.get("is_matter"):
        return pg["chapter_title"]
    return f'Ch. {pg["seq"]}'


def _curated_concept_entries(registry: dict[str, dict]) -> list[dict]:
    """Turn the harvested concept registry into curated index entries: one per concept that carries a
    definition, with its `definition of:` locator and ordered `examples of:` locators. Each locator links
    the specific anchor (`#idx-def-<slug>` / `#idx-ex-<slug>-<n>`)."""
    entries: list[dict] = []
    for slug, slot in registry.items():
        if slot["def"] is None:
            continue  # a concept with no definition contributes no curated entry
        def_pg, def_anchor = slot["def"]
        entries.append({
            "kind": "curated",
            "term": slot["display"],
            "def": (def_pg, def_anchor),
            "examples": list(slot["examples"]),
        })
    return entries


def build_index_entries(chapters: list[dict], concept_registry: dict[str, dict] | None = None) -> list[dict]:
    """Compute the index. Two entry kinds interleave alphabetically:

    - **Curated** — a concept carrying `index-def` / `index-example` tags, rendered as a `definition of:` /
      `examples of:` shape leading with the author-named sites.
    - **Occurrence** — a term with no curated tags, rendered as the capped, ranked page list from the scan.

    A curated concept whose display name also matches a scanned term SUPPRESSES that occurrence entry (a
    concept is not listed twice). A term that never occurs is dropped (the index lists only findable terms)."""
    concept_registry = concept_registry or {}
    entries: list[dict] = []
    seen_display: set[str] = set()

    # Curated entries first — they win over a same-named occurrence entry.
    for e in _curated_concept_entries(concept_registry):
        key = e["term"].lower()
        if key in seen_display:
            continue
        seen_display.add(key)
        entries.append(e)

    # Occurrence entries for every remaining findable term.
    for term in _load_index_terms():
        key = term.lower()
        if key in seen_display:
            continue
        refs = _scan_term_refs(term, chapters)
        if not refs:
            continue
        seen_display.add(key)
        entries.append({"kind": "occurrence", "term": term, "refs": refs})

    entries.sort(key=lambda e: e["term"].lower())
    return entries


def _anchored_locator(pg: dict, anchor: str) -> str:
    """One curated locator: a link to `<slug>.html#<anchor>` labelled by the short page locator."""
    return (f'<a href="{pg["slug"]}.html#{html.escape(anchor, quote=True)}">'
            f'{html.escape(_index_ref_label(pg))}</a>')


def build_index_page(chapters: list[dict], concept_registry: dict[str, dict] | None = None,
                     word_counts: "WordCounts | None" = None) -> str:
    """Render `book-index.html` from the computed entries — an alphabetized index (curated concept entries +
    occurrence term entries) grouped by first letter, led by an auto-generated 'Book length' table when
    `word_counts` is supplied. Returns the full page HTML."""
    entries = build_index_entries(chapters, concept_registry)
    groups: dict[str, list[dict]] = {}
    for e in entries:
        first = e["term"][0].upper()
        letter = first if first.isalpha() else "#"
        groups.setdefault(letter, []).append(e)

    rows: list[str] = []
    for letter in sorted(groups):
        rows.append(f'<div class="part">{html.escape(letter)}</div>')
        rows.append("<ul>")
        for e in groups[letter]:
            if e.get("kind") == "curated":
                def_pg, def_anchor = e["def"]
                sub: list[str] = [
                    f'<span class="idx-sub"><span class="idx-sub-lead">definition of:</span> '
                    f'{_anchored_locator(def_pg, def_anchor)}</span>'
                ]
                if e["examples"]:
                    ex_links = " ".join(_anchored_locator(pg, anc) for pg, anc in e["examples"])
                    sub.append(
                        f'<span class="idx-sub"><span class="idx-sub-lead">examples of:</span> '
                        f'{ex_links}</span>'
                    )
                rows.append(
                    f'<li class="idx-concept"><span class="idx-term">{inline(e["term"])}</span>'
                    f'<span class="idx-subs">{"".join(sub)}</span></li>'
                )
            else:
                links = ", ".join(
                    f'<a href="{pg["slug"]}.html">{html.escape(_index_ref_label(pg))}</a>'
                    for pg in e["refs"]
                )
                rows.append(
                    f'<li><span class="idx-term">{inline(e["term"])}</span> '
                    f'<span class="idx-refs">{links}</span></li>'
                )
        rows.append("</ul>")

    header = (
        '<header class="chap"><div class="kicker">Back Matter</div>'
        "<h1>Index</h1></header>"
    )
    intro = (
        "<p>A term index over the chapters and the appendix. A curated concept entry leads with the paragraph "
        "that <em>defines</em> it and the paragraphs that <em>exemplify</em> it; a plain term entry links the "
        "pages where it appears, capped so the index leads with the significant sites.</p>"
    )
    # Word counts stay a build-time report (printed to stdout), NOT shipped onto the page — a reader of the
    # published book should meet the ideas, not the manuscript's length. `word_counts` is still computed for
    # the stdout tool-report; it is deliberately not rendered here.
    body = header + intro + '<div class="idx idx-terms">' + "\n".join(rows) + "</div>"
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    # The term index gets the whole-book TOC disclosure at the top and a chapter-nav bar at the bottom.
    # It IS the Index, so no self-linking Index pill — forward to its back-matter siblings instead.
    toc = toc_html(chapters, None)
    nav_bar = _render_chapnav(
        [("« Table of contents", "index.html", "Table of contents")],
        "Index",
        [(f"{_FIGURES_GALLERY_SLUG.capitalize()} »", f"{_FIGURES_GALLERY_SLUG}.html", "Figures gallery"),
         ("Bibliography »", f"{_BIBLIOGRAPHY_SLUG}.html", "Bibliography")],
    )
    main = body + nav_bar + foot
    return page("Index · Model-Based Agentic Software Engineering", toc, main)


# ─────────────────────────── Book length — auto-computed word counts ───────────────────────────
# Count the words a READER READS, computed fresh every build from each page's RENDERED prose (so the
# published number can never drift from the text). The prose count strips, in order:
#   1. fenced code + mermaid blocks (rendered as <pre>…</pre>) — a reader doesn't "read" a diagram/listing;
#   2. figure <figcaption> and any SVG <title>/<desc> — a11y/caption text describes a figure, it isn't prose;
#   3. every remaining HTML tag — leaving the visible words, which are then whitespace-tokenized.
# The breakdown splits BODY (front matter + Parts 1–5 + back matter, per-Part subtotals) from APPENDIX (the
# A/B/C GoF pattern Parts + Appendix D stacks + Appendix E recipe, per-letter subtotals); TOTAL = body + app.

# <pre>…</pre> holds a rendered code OR mermaid fence; <figure>'s <figcaption> and an inline SVG's
# <title>/<desc> hold caption / a11y text. Drop all of them before the prose is tokenized. Non-greedy,
# DOTALL so a multi-line block is removed whole.
_PRE_BLOCK_RE = re.compile(r"<pre\b.*?</pre>", re.S | re.I)
_FIGCAPTION_RE = re.compile(r"<figcaption\b.*?</figcaption>", re.S | re.I)
_SVG_DESC_RE = re.compile(r"<(title|desc)\b.*?</\1>", re.S | re.I)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _prose_word_count(body_md: str) -> int:
    """Word count of one page's reader-facing prose. Render the markdown to HTML (same renderer the site
    ships), strip code/mermaid <pre> blocks, figure captions, and SVG a11y text, then strip the remaining
    tags and count whitespace-delimited tokens. Counts the words a reader actually reads — not code,
    diagrams, or caption/alt text."""
    rendered = md_to_html(body_md)
    rendered = _HTML_COMMENT_RE.sub(" ", rendered)
    rendered = _PRE_BLOCK_RE.sub(" ", rendered)
    rendered = _FIGCAPTION_RE.sub(" ", rendered)
    rendered = _SVG_DESC_RE.sub(" ", rendered)
    text = _HTML_TAG_RE.sub(" ", rendered)
    text = html.unescape(text)
    return len(text.split())


def _appendix_letter(pg: dict) -> str:
    """The appendix letter (A–E) a rendered appendix page belongs to, read from its `part_title`
    ('Appendix C — Product patterns' → 'C'). Falls back to '?' — should not happen for an appendix page."""
    m = re.search(r"Appendix\s+([A-Z])\b", pg.get("part_title", ""))
    return m.group(1) if m else "?"


class WordCounts(NamedTuple):
    body_parts: list[tuple[str, int]]      # (Part display label, word count) in reading order
    body_total: int
    appendix_letters: list[tuple[str, int]]  # (Appendix-letter label, word count) in reading order
    appendix_total: int
    total: int


def compute_word_counts(chapters: list[dict]) -> WordCounts:
    """Compute the BODY / APPENDIX / TOTAL word breakdown from the rendered prose of every page. BODY groups
    by Part (front matter, Parts 1–5, back matter — per-Part subtotals in reading order); APPENDIX groups by
    appendix letter (A/B/C pattern Parts, D stacks, E recipe — per-letter subtotals). Fresh every build."""
    body_by_part: dict[int, int] = {}
    body_part_order: list[int] = []
    app_by_letter: dict[str, int] = {}
    app_letter_order: list[str] = []
    for pg in chapters:
        wc = _prose_word_count(pg["body_md"])
        if pg.get("is_appendix"):
            letter = _appendix_letter(pg)
            if letter not in app_by_letter:
                app_by_letter[letter] = 0
                app_letter_order.append(letter)
            app_by_letter[letter] += wc
        else:
            part = pg["part"]
            if part not in body_by_part:
                body_by_part[part] = 0
                body_part_order.append(part)
            body_by_part[part] += wc

    body_parts = [(_PART_TITLES.get(p, f"Part {p}") if p in (0, 6)
                   else f"Part {p} — {_PART_TITLES.get(p, '')}", body_by_part[p])
                  for p in body_part_order]
    body_total = sum(body_by_part.values())
    appendix_letters = [(f"Appendix {ltr}", app_by_letter[ltr]) for ltr in app_letter_order]
    appendix_total = sum(app_by_letter.values())
    return WordCounts(
        body_parts=body_parts,
        body_total=body_total,
        appendix_letters=appendix_letters,
        appendix_total=appendix_total,
        total=body_total + appendix_total,
    )


def _print_word_counts(wc: WordCounts) -> None:
    """Print the word-count breakdown to stdout, so `catalog.py build` / the deploy REPORTS it (the repo's
    'tools report their results' discipline). A stable, greppable shape (`  BODY  <part> : <n>`)."""
    print("book word count (rendered prose; code/diagrams/captions excluded):")
    print("  BODY (narrative):")
    for label, n in wc.body_parts:
        print(f"    {label:<48} {n:>7,}")
    print(f"    {'BODY subtotal':<48} {wc.body_total:>7,}")
    print("  APPENDIX:")
    for label, n in wc.appendix_letters:
        print(f"    {label:<48} {n:>7,}")
    print(f"    {'APPENDIX subtotal':<48} {wc.appendix_total:>7,}")
    print(f"  {'TOTAL':<50} {wc.total:>7,}")


# ─────────────────────────── PDF print edition (opt-in `--pdf`) ──────────────────────────────────
# The book PDF is a SECOND, opt-in build path that projects the SAME typed book IR the web build walks —
# but to a print-native Typst document, which `typst compile` lays out to PDF. One IR, two projections
# (HTML web + Typst print), so the PDF cannot diverge from the web book. The default `build()` is the fast
# web build and stays untouched; `--pdf` (see `build_pdf`) renders the print edition. The float-numbering,
# caption, and cross-reference helpers below are shared by BOTH projections.


# A "float" is a numbered display block — a figure or a table. Figures render as `<figure
# class="book-figure…">` (an SVG `<!-- figure: -->` directive or a standalone mermaid diagram); tables
# render as `<table>`. The `catalogue-embed` iframe is EXCLUDED: it `display:none`s in print, so numbering
# it would leave a phantom gap in the printed book's figure sequence (web/print would disagree). Both get a
# monotonic label and an `id` the front-matter list of floats links to.
_FLOAT_RE = re.compile(
    r'(?P<fig><figure class="book-figure(?![^"]*catalogue-embed)[^"]*"[^>]*>.*?</figure>)'
    r'|(?P<tbl><table\b[^>]*>.*?</table>)', re.S)
_DATA_SHORT_RE = re.compile(r'data-short="([^"]*)"')
_DATA_LABEL_RE = re.compile(r'data-label="([^"]*)"')


def _split_caption_md(md: str) -> tuple[str, str | None]:
    r"""Split a caption's markdown at a trailing `[short: …]` marker into (display, short) — the LaTeX
    `\caption[short]{long}` idea in ONE authored string, so the full caption and its list-of-floats short
    form share a single source of truth. Returns short=None when the marker is absent."""
    m = re.search(r"\s*\[short:\s*(.+?)\s*\]\s*$", md, re.I | re.S)
    if m:
        return md[: m.start()].rstrip(), m.group(1).strip()
    return md, None


def _derive_short(display_md: str) -> str:
    """Fallback short caption when none is declared: the caption's first sentence/clause, length-capped."""
    plain = re.sub(r"[*_`]", "", " ".join(display_md.split())).strip()
    first = re.split(r"(?<=[.:])\s", plain, maxsplit=1)[0].strip().rstrip(".:")
    return (first[:77].rsplit(" ", 1)[0] + "…") if len(first) > 80 else first


def _caption_el(tag: str, caption_md: str, extra_class: str = "") -> str:
    """Render a <figcaption>/<caption> holding the FULL caption inline plus a `data-short` attribute (the
    declared or derived short form) that the numbering pass harvests for the list of floats."""
    display, short = _split_caption_md(" ".join(caption_md.split()))
    short = short or _derive_short(display)
    cls = f' class="{extra_class}"' if extra_class else ""
    return f'<{tag}{cls} data-short="{html.escape(short, quote=True)}">{inline(display)}</{tag}>'


def _chapter_id(c: "dict") -> str:
    """The chapter's `<part>.<chapter>` identifier (e.g. "1.3") — the reader-facing locator floats number
    against. Chapter-relative float numbers reset per chapter and carry this prefix, so a figure reads
    "Figure 1.3-1"; the id it derives (`fig-1-3-1`, dots→dashes for a selector-safe id) is unique within the
    chapter's page and, because the (part, chapter) pair is unique per chapter, across a single-document
    build too."""
    return f'{c["part"]}.{c["chapter"]}'


def _float_id(kind: str, num: str) -> str:
    """The selector-safe id/anchor for a float: `fig-1-3-1` from num `1.3-1`. The DISPLAY label keeps the
    period ("Figure 1.3-1"); the id must not (an HTML id with a `.` is not a valid CSS/querySelector token,
    which the html-validate `valid-id` rule rejects). Every id, `[ref:]` anchor, and list-of-floats href
    goes through here so the generator and the resolver share ONE dotted→dashed scheme."""
    return f"{kind}-{num.replace('.', '-')}"


def _number_floats(body: str, chapter_id: str, fig_n: int, tbl_n: int,
                   collect: "list[dict] | None" = None, slug: str | None = None,
                   label_sink: "dict[str, dict] | None" = None) -> tuple[str, int, int]:
    """Prepend a CHAPTER-RELATIVE, ctrl-f-able "Figure <chapter>-N."/"Table <chapter>-N." label to every
    figure/table caption in document order, give each an `id` (`fig-<chapter>-N`/`tbl-<chapter>-N`) the list
    of floats links to, and — when `collect` is given — record each captioned float's {kind, num, short,
    slug, html} for that list (`html` is the float's fully-numbered fragment VERBATIM — id, "Figure N."
    label, inlined SVG/img, and caption already baked in — so a consumer like the figures gallery can splice
    it in with no re-render). When `label_sink` is given, record each `data-label`-carrying float's
    key→{kind, num, slug} so `[ref:key]` cross-references resolve to "Figure <chapter>-N"/"Table
    <chapter>-N". `num` is the full chapter-relative locator STRING (e.g. "1.3-1"); `chapter_id` is the
    owning chapter's `<part>.<chapter>` identifier and `fig_n`/`tbl_n` RESET to 1 per chapter (the caller
    threads them within one chapter only). Numbers are DERIVED from reading-order position within the
    chapter, never hand-authored. Returns (numbered_body, next_fig_n, next_tbl_n)."""

    def _harvest(frag: str, kind: str, num: str) -> None:
        if collect is not None:
            ds = _DATA_SHORT_RE.search(frag)
            if ds and ds.group(1):
                collect.append({"kind": kind, "num": num, "short": ds.group(1), "slug": slug, "html": frag})
        if label_sink is not None:
            dl = _DATA_LABEL_RE.search(frag)
            if dl and dl.group(1):
                label_sink[dl.group(1)] = {"kind": kind, "num": num, "slug": slug}

    def _repl(m: "re.Match[str]") -> str:
        nonlocal fig_n, tbl_n
        if m.group("fig"):
            frag, num = m.group("fig"), f"{chapter_id}-{fig_n}"
            fig_n += 1
            frag = frag.replace("<figure ", f'<figure id="{_float_id("fig", num)}" ', 1)
            label = f'<span class="fig-label">Figure {num}.</span> '
            if "<figcaption" in frag:
                frag = re.sub(r"(<figcaption\b[^>]*>)", lambda mm: mm.group(1) + label, frag, count=1)
            else:
                frag = frag.replace(
                    "</figure>",
                    f'<figcaption class="fig-label-only"><span class="fig-label">Figure {num}.</span>'
                    "</figcaption></figure>", 1)
            _harvest(frag, "fig", num)
            return frag
        frag, num = m.group("tbl"), f"{chapter_id}-{tbl_n}"
        tbl_n += 1
        frag = frag.replace("<table", f'<table id="{_float_id("tbl", num)}"', 1)
        label = f'<span class="tbl-label">Table {num}.</span> '
        if "<caption" in frag:
            frag = re.sub(r"(<caption\b[^>]*>)", lambda mm: mm.group(1) + label, frag, count=1)
        else:
            frag = re.sub(
                r"(<table\b[^>]*>)",
                lambda mm: mm.group(1) + f'<caption class="tbl-label-only"><span class="tbl-label">'
                f"Table {num}.</span></caption>", frag, count=1)
        _harvest(frag, "tbl", num)
        return frag

    return _FLOAT_RE.sub(_repl, body), fig_n, tbl_n


_XREF_RE = re.compile(r"\[ref:\s*([a-z0-9][a-z0-9-]*)\]")


def _resolve_xrefs(body: str, ref_map: "dict[str, dict]", for_print: bool) -> str:
    """Resolve every `[ref:key]` cross-reference to a linked "Figure N"/"Table N", using the label map the
    numbering pre-pass built. Fails loud on a `[ref:]` whose key has no `<!-- label: -->` float — a dangling
    cross-reference must stop the build, not ship as literal `[ref:foo]` text."""
    def _repl(m: "re.Match[str]") -> str:
        key = m.group(1)
        e = ref_map.get(key)
        if e is None:
            raise SystemExit(
                f"[ref:{key}]: no float carries `<!-- label: {key} -->` — check the spelling or add the label")
        word = "Figure" if e["kind"] == "fig" else "Table"
        anchor = _float_id(e["kind"], e["num"])
        href = f'#{anchor}' if for_print else f'{e["slug"]}.html#{anchor}'
        return f'<a class="xref" href="{html.escape(href, quote=True)}">{word}&nbsp;{e["num"]}</a>'
    return _XREF_RE.sub(_repl, body)


def _collect_floats(chapters: list[dict], page_anchor_maps: dict) -> "tuple[list[dict], dict[str, dict]]":
    """Render every chapter once (mermaid SVG is cached) and number its floats in reading order, returning
    (ordered captioned floats for the list of figures/tables, label→{kind,num,slug} map for [ref:] xrefs).
    The per-chapter numbering in the per-chapter page build RESETS the SAME counters at each chapter over the
    SAME reading order, so a float's list number equals its printed 'Figure <chapter>-N.' / 'Table
    <chapter>-N.' and its `[ref:]` number."""
    entries: list[dict] = []
    labels: dict[str, dict] = {}
    for c in chapters:
        body = md_to_html(c["body_md"], anchor_map=page_anchor_maps.get(c["slug"]))
        # Chapter-relative: counters reset to 1 at EACH chapter; the label carries the chapter id.
        _number_floats(body, _chapter_id(c), 1, 1, collect=entries, slug=c["slug"], label_sink=labels)
    return entries, labels


def _list_of_floats_chapter(entries: list[dict], for_print: bool) -> dict:
    """Generate the front-matter "List of Figures and Tables" chapter from collected floats. Entries link
    to each float by its `id`; the visible text is the SHORT caption (the list wants scannable labels, not
    the full sentence). Web links cross to the owning chapter page; print links are same-document."""
    def _lines(kind: str, word: str) -> list[str]:
        rows = [e for e in entries if e["kind"] == kind]
        if not rows:
            return []
        out = [f"## {word}s", ""]
        for e in rows:
            anchor = _float_id(kind, e["num"])
            href = f'#{anchor}' if for_print else f'{e["slug"]}.html#{anchor}'
            out.append(f'- [{word} {e["num"]}]({href}) — {e["short"]}')
        out.append("")
        return out

    # The Figures Gallery is a WEB-ONLY generated page (no Typst/print projection); only link it from the
    # web build's intro, so the print edition (`for_print=True`) never ships a dangling `figures.html` href.
    gallery_note = (
        " Every figure, rendered in full with its caption, also lives on the "
        f"[Figures Gallery]({_FIGURES_GALLERY_SLUG}.html) — a one-page visual review of the whole book."
    ) if not for_print else ""
    body_md = "\n".join(
        [f"The figures and tables of this book, in order. Each links to where it appears.{gallery_note}", ""]
        + _lines("fig", "Figure") + _lines("tbl", "Table")
    ).strip()
    return {
        "slug": _GENERATED_PAGE_SLUGS[0], "part": 0, "part_title": _PART_TITLES.get(0, ""),
        "chapter": 99, "chapter_title": "List of Figures and Tables",
        "body_md": body_md, "is_matter": True, "mermaid": False, "list_of_floats": True,
    }


# Pages the build writes BEYOND chapter/appendix discovery. Declared once so the two build paths that
# insert them and the tracked-HTML test that expects them share ONE source of truth (an ad-hoc insertion
# that the test's discovery never saw is exactly the orphan this centralization prevents).
_GENERATED_PAGE_SLUGS = ("list-of-figures",)


def _insert_list_of_floats(chapters: list[dict], page_anchor_maps: dict,
                           for_print: bool) -> "tuple[list[dict], dict[str, dict], list[dict]]":
    """Insert the generated List of Figures and Tables just after the preface, and return the label→float
    map for `[ref:]` cross-reference resolution PLUS the raw collected float entries (so a caller building
    a further projection — e.g. the figures gallery — reuses the SAME reading-order render instead of
    walking the chapters a second time). Shared by the print and per-chapter builds so the two cannot
    drift; its float numbers come from the same reading-order pass the inline numbering uses, so the list
    number, the printed 'Figure N.', and every `[ref:]` to it all agree."""
    entries, ref_map = _collect_floats(chapters, page_anchor_maps)
    lof = _list_of_floats_chapter(entries, for_print)
    pi = next((k for k, c in enumerate(chapters) if c["slug"].endswith("preface")), -1)
    return chapters[: pi + 1] + [lof] + chapters[pi + 1:], ref_map, entries


_SVG_ID_RE = re.compile(r'\bid="([A-Za-z][\w:.-]*)"')


def _namespace_element_ids(frag: str, prefix: str) -> str:
    """Rename every `id="…"` defined in `frag` — and every reference to it (`href="#x"`, `url(#x)`,
    `aria-labelledby`, `aria-describedby`, …) — to be namespaced by `prefix`. mermaid-cli derives an SVG's
    root id (and everything under it — gradients, arrowheads, per-node ids) from a hash of the DIAGRAM
    SOURCE, so two different chapters that happen to embed the identical diagram render identical ids; that
    is harmless on their own per-chapter pages (each page only ever holds one copy) but collides the moment
    both copies land on ONE page — exactly what the figures gallery does. Replacing every id (longest first,
    so a short id is never rewritten while it is still a substring of a longer one still pending its own
    exact-match rewrite) in a single pass keeps every internal `<defs>`/`fill`/`aria-*` reference intact."""
    ids = sorted(set(_SVG_ID_RE.findall(frag)), key=len, reverse=True)
    if not ids:
        return frag
    mapping = {i: f"{prefix}-{i}" for i in ids}
    pattern = re.compile("|".join(re.escape(i) for i in ids))
    return pattern.sub(lambda m: mapping[m.group(0)], frag)


def build_figures_page(chapters: list[dict], entries: list[dict]) -> str:
    """Render `figures.html` — a standalone gallery of every FIGURE in the book, in reading order, each
    followed by its full caption and an `<hr>` divider (the quick "review every figure in one place" view).
    Each figure's markup — including its inlined SVG (title/desc intact) or `<img>`, id, "Figure N." label,
    and caption — is reused VERBATIM from `entries["html"]` (the same fully-numbered fragment `_collect_
    floats` already rendered for the List of Figures and Tables), so a figure here is byte-identical to its
    chapter rendering: no second render pass, no risk of drifting from what the chapter actually ships. Each
    figure's internal ids are namespaced (`_namespace_element_ids`) by its own float id before splicing, so
    two chapters that happen to embed the SAME diagram (identical mermaid content-hash → identical ids)
    don't collide once both land on this one page."""
    title_by_slug = {c["slug"]: c for c in chapters}
    figs = [e for e in entries if e["kind"] == "fig"]

    def _gallery_item(e: dict) -> str:
        src = title_by_slug.get(e["slug"])
        anchor = _float_id("fig", e["num"])
        fig_html = _namespace_element_ids(e["html"], anchor)
        from_label = _pager_label(src) if src else e["slug"]
        from_link = (
            f'<p class="gallery-source">From <a href="{html.escape(e["slug"], quote=True)}.html#{anchor}">'
            f'{html.escape(from_label)}</a></p>'
        )
        return f'<section class="gallery-item">{fig_html}{from_link}</section>'

    # Two REGISTERS live in one gallery: the book-proper chapter figures are hand-drawn to the house
    # palette; the appendix pattern pages carry lighter schematic diagrams. Section the gallery by the
    # source chapter's `is_appendix` flag so the two registers don't shuffle together — a reader scanning
    # the visuals sees the deliberate style shift, not an inconsistency. Every figure still appears.
    chapter_figs = [e for e in figs if not (title_by_slug.get(e["slug"]) or {}).get("is_appendix")]
    appendix_figs = [e for e in figs if (title_by_slug.get(e["slug"]) or {}).get("is_appendix")]

    def _group(heading: str, blurb: str, group: list[dict]) -> str:
        if not group:
            return ""
        inner = "<hr>".join(_gallery_item(e) for e in group)
        return (
            '<section class="gallery-group">'
            f"<h2>{html.escape(heading)}</h2>"
            f'<p class="gallery-group-note">{blurb}</p>'
            f'<div class="gallery">{inner}</div></section>'
        )

    header = (
        '<header class="chap"><div class="kicker">Front Matter</div>'
        "<h1>Figures Gallery</h1></header>"
    )
    intro = (
        f"<p>Every figure in the book — {len(figs)} in all — gathered here in reading order, each with its "
        "full caption. A quick way to review the book's visuals in one place; every figure links back to "
        "where it appears in the text. The chapter figures come first; the appendix pattern pages follow "
        "in a lighter schematic style. (See also the "
        f'<a href="{_GENERATED_PAGE_SLUGS[0]}.html">List of Figures and Tables</a> for tables, and a '
        "scannable index of short captions.)</p>"
    )
    body = (
        header + intro
        + _group("Chapter figures", "The book-proper figures, hand-drawn to the house palette.",
                 chapter_figs)
        + _group("Appendix schematics",
                 "Diagrams from the pattern-catalogue appendix, drawn in a lighter reference style.",
                 appendix_figs)
    )
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    toc = toc_html(chapters, None)
    nav_bar = _static_nav_html(
        "Figures Gallery",
        fwd_extra=[("List of Figures and Tables »", f"{_GENERATED_PAGE_SLUGS[0]}.html",
                    "List of Figures and Tables")],
    )
    main = body + nav_bar + foot
    provenance = (
        "<!-- GENERATED by book/build_book_html.py (build_figures_page) — DO NOT EDIT. Regenerate via "
        "python3 book/build_book_html.py or python3 catalog.py build. -->"
    )
    return page("Figures Gallery · Model-Based Agentic Software Engineering", toc, main, provenance=provenance)


def expected_page_slugs() -> set[str]:
    """Single source of truth for every page slug the build writes: chapter + appendix discovery, the
    generated front-matter pages (`_GENERATED_PAGE_SLUGS`), the two index pages, the hand-authored
    catalogue figure, and the figures gallery. The tracked-HTML test consumes THIS, so its expectation
    cannot drift from what the build produces — the guard against a build-writes-it-but-the-test-doesn't-
    know-it orphan."""
    chapters = _discover_chapters(_load_metrics())
    chapters += build_appendix_chapters(next_part=max(c["part"] for c in chapters) + 1)
    return ({c["slug"] for c in chapters} | set(_GENERATED_PAGE_SLUGS)
            | {"index", "book-index", "catalogue-figure", _FIGURES_GALLERY_SLUG, _BIBLIOGRAPHY_SLUG})


# The rendered PDF is gated on CONTENT INTEGRITY, not just a page count. The failure modes are a runaway
# pagination (the render explodes the book into hundreds of near-empty pages) OR a collapse / truncation
# (the render stops partway, or falls to a handful of pages). A page-count band catches the explosion; a
# text-extraction check catches the truncation — every chapter and part title from the SOURCE OF TRUTH
# (`_discover_chapters()` / `_PART_TITLES`) must appear in the extracted PDF text, plus the cover title and
# a distinctive tail from the last section. Any miss → RENDER FAILURE.
_PDF_PAGE_CEILING = 800
_PDF_PAGE_FLOOR = 50  # a real book render; under this means the render collapsed or truncated
# Shipped-size ceiling: the FINAL (post-repack) PDF must be <= 8 MiB. A dense whole-book render is ~4.3 MB;
# a full-bleed rasterized cover or an un-downsampled image blows this past 30 MB. The gate blocks such a
# bloated PDF from shipping via CI or the local push. Measured on the post-qpdf-repack file (what ships).
_PDF_MAX_BYTES = 8 * 1024 * 1024  # 8 MiB = 8388608 bytes
_BOOK_TITLE = "Model-Based Agentic Software Engineering"


def _pdf_page_count(pdf_path: pathlib.Path) -> int:
    """Count pages in a PDF. Prefers `pdfinfo` (poppler) which handles object-stream-compressed PDFs
    (qpdf --object-streams=generate packs the page tree into compressed xref streams so raw byte scans
    miss it). Falls back to raw byte scan for non-compressed PDFs when pdfinfo is absent."""
    import subprocess
    import shutil
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        r = subprocess.run([pdfinfo, str(pdf_path)], capture_output=True, text=True)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if line.startswith("Pages:"):
                    try:
                        return int(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
    # Fallback: raw byte scan (works on non-object-stream PDFs; misses pages in compressed xref streams).
    data = pdf_path.read_bytes()
    counts = re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)
    if counts:
        return max(int(c) for c in counts)
    return len(re.findall(rb"/Type\s*/Page\b", data))


def _extract_pdf_text(pdf_path: pathlib.Path) -> str:
    """Extract the PDF's text via poppler `pdftotext` (on PATH). Returns whitespace-normalized text so a
    title wrapped across two lines in the layout still matches as one run. Fails loud if pdftotext is
    absent (the integrity gate needs it)."""
    import shutil
    import subprocess
    if not shutil.which("pdftotext"):
        raise SystemExit("pdftotext (poppler) not found on PATH — required for the PDF content-integrity gate")
    r = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"pdftotext failed (rc={r.returncode}): {r.stderr}")
    # Rejoin words broken by CSS `hyphens: auto` line-breaks: poppler emits the fragment, a hyphen
    # (ASCII `-`, U+2010 `‐`, or soft-hyphen U+00AD), then a newline. Stripping the break-hyphen makes a
    # tail run like "to start using" match even when reflow hyphenated "using" at the column edge — so a
    # margin/font change cannot make the content-integrity gate false-fail on intact text.
    dehyphenated = re.sub(r"[-‐­]\n", "", r.stdout)
    return re.sub(r"\s+", " ", dehyphenated)


# ── words-per-page density check ─────────────────────────────────────────────────────────────
# The enforced typographic-density metric, at O'Reilly-class technical density. `pdftotext` writes a
# form-feed (\x0c) between pages; we split on it, apply the SAME hyphen-rejoin as `_extract_pdf_text`,
# and count words per page.
#
# The check: over the FIRST N pages (representative body — the sparse appendix tail is excluded),
# at least _DENSITY_MIN_FRACTION of them must exceed _DENSITY_WORDS_THRESHOLD words. This book is
# figure/table/code/short-chapter-heavy, so even at O'Reilly-dense type only ~68% of the first-100
# pages clear 400 words (book-wide, only ~38% of substantive pages can) — 80% is structurally
# unreachable here without cramping. The 0.50 bar clears the achieved dense build (68%, with margin)
# while decisively failing the airy trade-paperback regression (~11% at 10.25pt/6×9). Below it is bloat.
_DENSITY_FIRST_N_PAGES = 100
_DENSITY_WORDS_THRESHOLD = 400
_DENSITY_MIN_FRACTION = 0.40  # relaxed from 0.50 (author call): density is a house-style preference, not
                              # a correctness gate — figures/tables/short sections legitimately vary it


def _pdf_per_page_word_counts(pdf_path: pathlib.Path) -> list[int]:
    """Word count per page. `pdftotext` emits a form-feed (\\x0c) between pages; split on it, apply the
    same `hyphens: auto` rejoin as `_extract_pdf_text`, then count whitespace-delimited words per page."""
    import shutil
    import subprocess
    if not shutil.which("pdftotext"):
        raise SystemExit("pdftotext (poppler) not found on PATH — required for the density metric")
    r = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"pdftotext failed (rc={r.returncode}): {r.stderr}")
    pages = r.stdout.split("\x0c")
    counts: list[int] = []
    for page in pages:
        dehyphenated = re.sub(r"[-‐­]\n", "", page)
        counts.append(len(re.sub(r"\s+", " ", dehyphenated).split()))
    # Trailing split element is the empty tail after the final form-feed — drop empty trailing pages.
    while counts and counts[-1] == 0:
        counts.pop()
    return counts


def _density_report(pdf_path: pathlib.Path) -> tuple[int, list[str]]:
    """Compute + print the words-per-page density metric and gate on: over the FIRST N pages, at least
    _DENSITY_MIN_FRACTION exceed _DENSITY_WORDS_THRESHOLD words. Returns (rc, problems): rc is 0 if the
    fraction holds, 1 otherwise; problems appended to the caller's list."""
    problems: list[str] = []
    per_page = _pdf_per_page_word_counts(pdf_path)
    total_pages = len(per_page)
    total_words = sum(per_page)
    overall = (total_words / total_pages) if total_pages else 0
    substantive = sorted(c for c in per_page if c >= 100)
    median = substantive[len(substantive) // 2] if substantive else 0

    window = per_page[:_DENSITY_FIRST_N_PAGES]
    n = len(window)
    dense = sum(1 for c in window if c > _DENSITY_WORDS_THRESHOLD)
    frac = (dense / n) if n else 0.0
    need_pct = int(_DENSITY_MIN_FRACTION * 100)
    passed = frac >= _DENSITY_MIN_FRACTION

    print("PDF words-per-page density:")
    print(f"  total pages ............. {total_pages}")
    print(f"  total words ............. {total_words}")
    print(f"  overall w/pg ............ {overall:.0f}  (total/pages)")
    print(f"  median w/pg (substantive) {median}  ({len(substantive)} pages ≥ 100 words)")
    print(f"  density check: {dense}/{n} pages > {_DENSITY_WORDS_THRESHOLD} words "
          f"({frac * 100:.0f}%) — {'PASS' if passed else 'FAIL'} (need >={need_pct}%)")

    if not passed:
        problems.append(f"density check: only {dense}/{n} of first pages > {_DENSITY_WORDS_THRESHOLD} "
                        f"words ({frac * 100:.0f}%), need >={need_pct}% — too airy (below O'Reilly "
                        f"technical density)")
    return (1 if problems else 0), problems


def verify_pdf(pdf_path: pathlib.Path) -> int:
    """Content-integrity gate over the rendered PDF. Extracts the text and asserts the WHOLE book is
    present against the source of truth. Returns 0 if the PDF contains the entire book, 1 otherwise.
    Also reused by the CI step so a truncated/broken render fails the Pages build. Checks:
      1. page count within [_PDF_PAGE_FLOOR, _PDF_PAGE_CEILING] (no collapse, no runaway),
      2. cover title present,
      3. every chapter title AND every rendered Part title present (no dropped/truncated chapter),
      4. the TOC lists exactly the source chapter set (none missing, none extra),
      5. a distinctive tail from the LAST section present (render did not stop partway),
      6. words-per-page density: ≥80% of the first 100 pages exceed 400 words (O'Reilly-dense body)."""
    problems: list[str] = []

    pages = _pdf_page_count(pdf_path)
    if pages < _PDF_PAGE_FLOOR:
        problems.append(f"page count {pages} < floor {_PDF_PAGE_FLOOR} (render collapsed/truncated)")
    if pages > _PDF_PAGE_CEILING:
        problems.append(f"page count {pages} > ceiling {_PDF_PAGE_CEILING} (runaway pagination)")

    text = _extract_pdf_text(pdf_path)

    # ASSERT (author-requested control): no RAW mermaid source may ship in the PDF. A rendered diagram
    # carries only its node labels as text; the `flowchart`/`subgraph`/`-->` syntax appears ONLY if a
    # ```mermaid fence shipped un-rendered as a code box (the exact bug this change fixes). Print an
    # explicit PASS/FAIL line so the control is visible in the build log.
    mermaid_hits = [m for m in MERMAID_SOURCE_MARKERS if m in text]
    if mermaid_hits:
        print(f"PDF MERMAID ASSERT: FAIL — raw mermaid source in PDF text: {mermaid_hits}", file=sys.stderr)
        problems.append(f"raw mermaid source shipped in PDF (markers: {mermaid_hits}) — "
                        "a ```mermaid fence rendered as source text, not a diagram")
    else:
        print("PDF MERMAID ASSERT: PASS — no raw mermaid source in PDF text.")

    if _BOOK_TITLE not in text:
        problems.append(f"cover title {_BOOK_TITLE!r} not found (cover did not render)")

    # Source of truth: the discovered chapters + the projected appendix, in reading order. The PDF gate must
    # build the appendix in the SAME print projection the render used (`for_print=True`), so the expected
    # titles match what actually renders (e.g. Appendix E's dropped recipe page is not expected in the PDF).
    metrics = _load_metrics()
    chapters = _discover_chapters(metrics)
    appendix = build_appendix_chapters(next_part=max(c["part"] for c in chapters) + 1, for_print=True)
    full = chapters + appendix

    # Normalize for matching so a markup / typographic difference cannot false-fail on intact content:
    #   - drop backtick markers: the typed IR renders a `code-span` in a title as PLAIN TEXT (no ` fences),
    #     so "Aggregate-compute protection (`lint-all` host mutex)" appears without the backticks;
    #   - fold typographic quotes/dashes to ASCII: the print renderer's smart-quotes turns a straight `'`
    #     into `’` (U+2019) and `--` into an en/em dash, so a title like "the runtime's events" or
    #     "read, don't hardcode" extracts with a curly apostrophe. The CONTENT matters, not the glyph.
    def _norm(s: str) -> str:
        s = s.replace("`", "")
        s = (s.replace("’", "'").replace("‘", "'")
               .replace("“", '"').replace("”", '"')
               .replace("–", "-").replace("—", "-").replace("‐", "-"))
        return re.sub(r"\s+", " ", s.strip())

    text_norm = _norm(text)

    def _present(s: str) -> bool:
        return _norm(s) in text_norm

    # The appendix chapter heading in the print edition renders the title WITHOUT its "Appendix X - N."
    # numeric prefix (the part-divider already names the family). Match on the title portion after that
    # prefix so a present-but-un-prefixed appendix heading is not falsely reported missing.
    _APPENDIX_PREFIX = re.compile(r"^Appendix\s+[A-Z]\s*[-—]\s*\d+\.\s*")

    def _title_present(title: str) -> bool:
        if _present(title):
            return True
        stripped = _APPENDIX_PREFIX.sub("", title)
        return stripped != title and _present(stripped)

    # Every chapter title must appear.
    missing_titles = [c["chapter_title"] for c in full if not _title_present(c["chapter_title"])]
    if missing_titles:
        problems.append(f"{len(missing_titles)} chapter title(s) missing from PDF: {missing_titles[:5]}")

    # Every rendered Part title (numbered Parts 1–5 get a divider; front/back matter do not).
    rendered_parts = sorted({c["part"] for c in full if c["part"] not in (0, 6)})
    for p in rendered_parts:
        appendix_part = next((c for c in full if c["part"] == p and c.get("is_appendix")), None)
        pt = appendix_part["part_title"] if appendix_part else _PART_TITLES.get(p, "")
        if pt and not _present(pt):
            problems.append(f"Part title {pt!r} (part {p}) missing from PDF")

    # Tail: a distinctive word-run from the LAST section's rendered body must appear (not truncated).
    last = full[-1]
    tail_words = re.findall(r"[A-Za-z][A-Za-z'-]+", md_to_html(last["body_md"]))
    # take a 6-word run from near the end of the last section
    if len(tail_words) >= 12:
        tail_run = " ".join(tail_words[-8:-2])
        if tail_run and tail_run not in text:
            # fall back to a shorter run (rendering may split a hyphenated word)
            short = " ".join(tail_words[-6:-3])
            if short not in text:
                problems.append(f"tail run from last section {last['slug']!r} not found "
                                f"({short!r}) — render may be truncated")

    # Words-per-page density metric + O'Reilly-band gate (prints its own report).
    _, density_problems = _density_report(pdf_path)
    problems.extend(density_problems)

    if problems:
        print(f"PDF CONTENT-INTEGRITY FAILURES ({len(problems)}):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"PDF content-integrity OK: {pages} pages, title present, "
          f"{len(full)} chapter titles + {len(rendered_parts)} part titles present, tail present.")
    return 0


def assert_pdf_size(pdf_path: pathlib.Path) -> None:
    """Shipped-size gate. Fails loud (raises SystemExit) if the FINAL PDF exceeds `_PDF_MAX_BYTES` (8 MiB).

    Call this AFTER the qpdf repack so the number checked is the post-repack size that actually ships. A
    bloated PDF is almost always a full-bleed cover or an un-downsampled image rasterized at print DPI —
    a dense whole-book render is ~4.3 MB, so 8 MiB leaves generous headroom while still catching a 30 MB
    regression. Prints a PASS line when green so the control is visible in the build log alongside the
    content-integrity gate."""
    size = pdf_path.stat().st_size
    if size > _PDF_MAX_BYTES:
        raise SystemExit(
            f"PDF SIZE GATE: FAIL — {pdf_path.name} is {size / 1_048_576:.1f} MB "
            f"({size:,} bytes), over the {_PDF_MAX_BYTES / 1_048_576:.0f} MB "
            f"({_PDF_MAX_BYTES:,} bytes) ceiling.\n"
            "  Hint: a filter-heavy full-bleed cover rasterizes huge — pre-rasterize it to a compressed "
            "image (or downsample any oversized image) before shipping.")
    print(f"PDF SIZE GATE: PASS — {size / 1_048_576:.1f} MB "
          f"<= {_PDF_MAX_BYTES / 1_048_576:.0f} MB ceiling.")


def _pdf_is_tagged(pdf_path: pathlib.Path) -> bool:
    """Return True if the PDF is tagged (has a struct tree root).

    Strategy: use `pdfinfo` (poppler) which reports "Tagged: yes" in its output — reliable even after
    qpdf object-stream compression (which packs /StructTreeRoot inside a compressed xref stream so a raw
    byte scan would miss it). Falls back to a byte scan on the raw un-compressed input PDF only.
    `pdfinfo` is always on PATH when the build runs (it is installed for the content-integrity gate)."""
    import subprocess
    import shutil
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        r = subprocess.run([pdfinfo, str(pdf_path)], capture_output=True, text=True)
        if r.returncode == 0:
            return "Tagged:          yes" in r.stdout or "Tagged: yes" in r.stdout
    # pdfinfo absent — fall back to raw byte scan (works for non-object-stream PDFs only).
    data = pdf_path.read_bytes()
    return b"/StructTreeRoot" in data


def _book_last_modified() -> str:
    """The book's last content-modification date (YYYY-MM-DD) for the print cover footer. Prefers the last
    git commit that touched `book/` (the real content change, stable across rebuilds of the same source);
    falls back to today's date when git is unavailable (a shallow export, a non-git checkout)."""
    import subprocess
    import datetime
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=short", "--", "book"],
                           cwd=str(ROOT), capture_output=True, text=True)
    except OSError:
        r = None  # git binary absent — fall through to the build-date fallback below
    if r is not None and r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return datetime.date.today().isoformat()


def build_pdf() -> int:
    """`--pdf`: render the production print edition to `book/mage-book.pdf` via the print-native Typst
    path — emit the WHOLE-BOOK Typst source from the typed book IR, then `typst compile` it to PDF. Gates
    the result on the same content-integrity band (page floor/ceiling, every chapter + part title present,
    no raw mermaid, density) so a truncated or runaway render fails instead of shipping. Fast, opt-in —
    NOT part of `build()` (the web build is untouched).

    Typst lays out the whole book with one native binary in ~2 s and emits a small (~5 MB), tagged PDF —
    no headless browser in the loop. Its output is already compact, so there is no post-compression pass;
    the tag tree is asserted directly on the compiled file."""
    import shutil
    import subprocess

    # book_typst imports build_book_html at module scope; import it here (function-local, matching this
    # function's existing shutil/subprocess pattern) so importing build_book_html as a library never pulls
    # the emitter and its transitive book_ir graph.
    import book_typst
    import book_ir

    typst = shutil.which("typst")
    if not typst:
        print("ERROR: `typst` not found on PATH — install it (brew install typst / download the pinned "
              "release binary in CI).", file=sys.stderr)
        return 2

    pdf_out = HERE / _PDF_FILENAME
    # Emit into _typst/ (gitignored, multi-file + binary — never committed).
    typ_dir = HERE / "_typst"
    typ_dir.mkdir(exist_ok=True)
    typ_src = typ_dir / "mage-book.typ"

    # Emit the WHOLE book (front matter → parts → back matter → appendices) as one Typst document from the
    # typed IR — the same IR the web build walks, so the print edition cannot diverge from the web book. This
    # is the PRINT projection (`for_print=True`), so the slug list matches what emit_document renders (e.g.
    # Appendix E collapses to its front-door pointer, dropping the recipe content page from the PDF).
    doc = book_ir.parse_book(include_appendices=True, for_print=True)
    slugs = [c.slug for c in doc.chapters]
    typ = book_typst.emit_document(slugs, root=ROOT, with_frontmatter=True)
    typ_src.write_text(typ, encoding="utf-8")
    print(f"Typst source: {typ_src} ({len(typ):,} bytes, {len(slugs)} chapters)")

    # Compile. `--root ..` so leading-`/` image paths (figure SVGs, cached mermaid SVGs) resolve against
    # the repo root. `--font-path` points Typst at the bundled OFL statics (book/fonts/) — Fraunces /
    # Source Sans 3 / IBM Plex Mono are not installed on the host or the CI runner, so without this flag
    # Typst silently substitutes a default serif and the PDF diverges from the web book, which loads the
    # real faces via Google Fonts. Typst fails loud on any unresolved reference / bad image / math error.
    # `--input last_modified=…` feeds the cover footer the book's last content-commit date (Typst has no
    # clock, and CI has no wall-clock intent — the date must be computed here and passed in).
    last_modified = _book_last_modified()
    cmd = [typst, "compile", "--input", f"last_modified={last_modified}",
           "--root", str(ROOT), "--font-path", str(HERE / "fonts"), str(typ_src), str(pdf_out)]
    print("PDF compile plan:\n  " + " ".join(f'"{a}"' if " " in a else a for a in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0 or not pdf_out.is_file():
        print(f"ERROR: Typst compile failed (rc={r.returncode}).\n{r.stderr}", file=sys.stderr)
        return 1
    if r.stderr.strip():
        # Typst prints warnings to stderr on success; surface them (foreign-object warnings, etc.).
        print(r.stderr.strip(), file=sys.stderr)

    final_size = pdf_out.stat().st_size
    print(f"PDF: {pdf_out} ({final_size / 1_048_576:.1f} MB via typst)")

    # Post-compression repack — Typst emits every object as an uncompressed indirect object with NO object
    # streams (~20K individual objects, dominated by the accessibility struct tree's thousands of small
    # StructElem objects). qpdf's lossless repack packs those into compressed object streams and recompresses
    # the content streams, cutting the whole-book PDF by ~35% (≈ 6.7 MB → 4.3 MB) with the tag tree fully
    # preserved. Object streams are PDF-spec-standard and PDF/UA-safe. The tag assertion + content-integrity
    # gate below run on the REPACKED file, so what ships is what we validate (the verify helpers read via
    # pdfinfo/pdftotext, which see through object streams). If qpdf is absent (fresh checkout without it), the
    # uncompressed PDF still ships — larger — so clone-and-run never hard-fails on a missing optimizer.
    qpdf = shutil.which("qpdf")
    if qpdf:
        opt_tmp = pdf_out.with_suffix(".opt.pdf")
        qr = subprocess.run(
            [qpdf, "--object-streams=generate", "--compress-streams=y", "--recompress-flate",
             "--compression-level=9", str(pdf_out), str(opt_tmp)],
            capture_output=True, text=True)
        # qpdf exit 0 = clean, 3 = warnings (still wrote a valid file); accept both.
        if qr.returncode in (0, 3) and opt_tmp.is_file():
            opt_tmp.replace(pdf_out)
            new_size = pdf_out.stat().st_size
            print(f"PDF: qpdf object-stream repack {final_size / 1_048_576:.1f} MB "
                  f"-> {new_size / 1_048_576:.1f} MB")
            final_size = new_size
        else:
            opt_tmp.unlink(missing_ok=True)
            print(f"WARNING: qpdf repack failed (rc={qr.returncode}); shipping uncompressed PDF.\n"
                  f"{qr.stderr}", file=sys.stderr)
    else:
        print("WARNING: qpdf not found on PATH — shipping the uncompressed (larger) PDF. Install qpdf "
              "to enable the lossless object-stream repack.", file=sys.stderr)

    # Tag-preservation assertion — Typst emits a tagged PDF; assert it (on the repacked file) so a future
    # template/flag change — or an optimizer that strips structure — cannot silently drop the struct tree.
    if not _pdf_is_tagged(pdf_out):
        print("ERROR: Typst PDF has no struct tree — tags lost (a11y regression). "
              "Check the Typst document settings before shipping.", file=sys.stderr)
        return 1
    print("Tag preservation: struct tree present in PDF.")

    # Shipped-size gate — measured on the REPACKED file (what actually ships), so it fails loud on a
    # bloated PDF (e.g. a full-bleed rasterized cover) that content-integrity alone would pass. Raises
    # SystemExit on breach; prints its PASS line adjacent to the content-integrity gate below.
    assert_pdf_size(pdf_out)

    # Content-integrity gate — the whole book must be in the compiled PDF.
    return verify_pdf(pdf_out)


def build() -> int:
    metrics = _load_metrics()
    _load_citations()  # the committed Chicago render of references.bib — read once, consumed per chapter
    chapters = _discover_chapters(metrics)
    if not chapters:
        print("no chapter files found under the Part/Chapter hierarchy", file=sys.stderr)
        return 1

    # Appendix — the pattern catalogue, projected from the catalogue entries into GoF format. Sorts
    # after the back matter.
    max_part = max(c["part"] for c in chapters)
    appendix = build_appendix_chapters(next_part=max_part + 1)
    chapters = chapters + appendix

    # The first chapter of each Part opens with an epigraph (numbered Parts only).
    seen_parts: set[int] = set()
    for c in chapters:
        c["show_epigraph"] = c["part"] not in seen_parts and not c.get("is_appendix")
        seen_parts.add(c["part"])

    # Curated concept index — harvest the index-def / index-example tags across all pages in reading
    # order (fails loud on a duplicate def, an unregistered slug, or an example with no def). The per-page
    # anchor maps feed the renderer so each tagged block carries the anchor the index links to.
    concept_registry, page_anchor_maps = _harvest_concept_tags(chapters)
    # {slug: (page_slug, idx-def anchor)} for every concept the book gave a canonical definition site — the
    # drift-proof target set the front glossary links its terms to (see `_link_glossary_sites`).
    gloss_link_map = {
        slug: (slot["def"][0]["slug"], slot["def"][1])
        for slug, slot in concept_registry.items() if slot.get("def")
    }
    # Harvest the glossary annotations (single source of truth for the inline glosses + the back-Glossary).
    _collect_glossary(chapters)

    chapters, ref_map, float_entries = _insert_list_of_floats(chapters, page_anchor_maps, for_print=False)

    # Per-chapter pages. Float numbers are CHAPTER-RELATIVE ("Figure 1.3-1"): the counters reset to 1 at
    # each chapter, keyed to the chapter's <part>.<chapter> id, matching the label map _collect_floats built.
    for i, c in enumerate(chapters):
        if c.get("is_appendix"):
            num_label = "Appendix"
        elif c.get("is_matter"):
            num_label = c["chapter_title"]  # "Preface" / "Conclusion"
        else:
            num_label = f'Chapter {c["seq"]}'
        kicker = _kicker_html(chapters, i, num_label)
        header = (
            f'<header class="chap"><div class="kicker">{kicker}</div>'
            f'<h1>{html.escape(c["chapter_title"])}</h1>'
            + (_epigraph_html(c["part"]) if c.get("show_epigraph") else "")
            + '</header>'
        )
        # Assign this chapter's citation numbers (first-reference order) BEFORE rendering, so inline()'s
        # `[cite:]` superscripts and the Works Cited list below both read the one ordering (BIB-4 mirror).
        _number_citations(c["slug"], c["body_md"])
        cited_keys = list(_CITE_STATE["order"])
        # `part.chapter` section-numbering prefix — body chapters (Parts 1-5) only. Front/back matter and
        # the appendix (which carries its own A-1/B-2 locators) stay unnumbered → `section_prefix=None`.
        section_prefix = (None if c.get("is_matter") or c.get("is_appendix")
                          else f'{c["part"]}.{c["chapter"]}')
        body = md_to_html(c["body_md"], anchor_map=page_anchor_maps.get(c["slug"]),
                          section_prefix=section_prefix)
        body, _fig_n, _tbl_n = _number_floats(body, _chapter_id(c), 1, 1)
        body = _resolve_xrefs(body, ref_map, for_print=False)
        if c["slug"] == GLOSSARY_CHAPTER_SLUG:
            body = _link_glossary_sites(body, gloss_link_map)
        body += works_cited_section()  # per-chapter numbered Works Cited (empty when nothing is cited)
        # The single left→right sequence bar (Table of contents « … │ THIS CHAPTER │ … » Index), bottom-only.
        nav_bar = _chapter_nav_html(chapters, i)
        foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
        main = header + body + nav_bar + foot
        toc = toc_html(chapters, c["slug"])
        out = HERE / f'{c["slug"]}.html'
        out.write_text(
            page(f'{num_label} · {c["chapter_title"]}', toc, main, mermaid=c.get("mermaid", False),
                 head_meta=_chapter_head_meta(c, cited_keys)),
            encoding="utf-8",
        )

    # Index / landing page.
    idx_rows = []
    last_part = None
    for c in chapters:
        if c["part"] != last_part:
            idx_rows.append(f'<div class="part">{html.escape(_part_label(c))}</div>')
            idx_rows.append("<ol>")
            if last_part is not None:
                idx_rows[-2] = "</ol>" + idx_rows[-2]
            last_part = c["part"]
        ref = _chap_ref(c)
        if ref:
            cnum = ref
        elif c.get("is_appendix"):
            # 'Appendix B — …' → 'B' (each appendix Part carries its own letter)
            m = re.search(r"Appendix\s+([A-Z])", c["part_title"])
            cnum = m.group(1) if m else "A"
        else:
            cnum = "•"
        idx_rows.append(
            f'<li><a href="{c["slug"]}.html">'
            f'<span class="cnum">{html.escape(cnum):>2}</span>{html.escape(c["chapter_title"])}</a></li>'
        )
    idx_rows.append("</ol>")
    # Back-matter row on the landing page: the autogenerated term index + the figures gallery (both also
    # reachable from every page's INDEX nav button / the List of Figures and Tables page respectively).
    # Linking them here keeps them off the orphan-reachability list.
    idx_rows.append('<div class="part">Index</div><ol>')
    idx_rows.append(
        f'<li><a href="{BOOK_INDEX_SLUG}.html">'
        f'<span class="cnum">{"★":>2}</span>Index (terms)</a></li>'
    )
    idx_rows.append(
        f'<li><a href="{_FIGURES_GALLERY_SLUG}.html">'
        f'<span class="cnum">{"◫":>2}</span>Figures Gallery</a></li>'
    )
    idx_rows.append(
        f'<li><a href="{_BIBLIOGRAPHY_SLUG}.html">'
        f'<span class="cnum">{"❧":>2}</span>Bibliography</a></li>'
    )
    idx_rows.append("</ol>")
    title_block = (
        f'<div class="book-title"><h1>{html.escape(_BOOK_MANIFEST["title"])}</h1>'
        f'{_cover_sub("sub")}'
        # PDF edition — a CI-published artifact at book/mage-book.pdf on the deployed site (a purely-local
        # checkout without the CI render will 404 this; that is expected).
        f'<div class="book-download"><a href="{_PDF_FILENAME}">Download the PDF edition ↓</a></div>'
        '</div>'
    )
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    main = title_block + '<div class="idx">' + "\n".join(idx_rows) + "</div>" + foot
    (HERE / "index.html").write_text(
        page("Model-Based Agentic Software Engineering — Contents", "", main), encoding="utf-8"
    )

    # Book length — auto-computed from the rendered prose of every page (fresh each build, never hardcoded).
    # Printed to stdout (tools report their results) and rendered onto book-index.html as a "Book length" table.
    word_counts = compute_word_counts(chapters)
    _print_word_counts(word_counts)

    # Autogenerated term index — placed after the appendix, reachable from the INDEX nav button.
    (HERE / f"{BOOK_INDEX_SLUG}.html").write_text(
        build_index_page(chapters, concept_registry, word_counts=word_counts), encoding="utf-8")

    # Figures Gallery — every figure the book collected during the list-of-floats pass, spliced in as one
    # standalone page. Reachable from the landing page, the List of Figures and Tables, and its own pager.
    (HERE / f"{_FIGURES_GALLERY_SLUG}.html").write_text(
        build_figures_page(chapters, float_entries), encoding="utf-8")

    # End-of-book Bibliography — the alphabetical union of every cited work (always written so the
    # tracked-HTML gate's expected set stays stable). Its pager points back to the last chapter.
    (HERE / f"{_BIBLIOGRAPHY_SLUG}.html").write_text(
        build_bibliography_page(chapters, chapters[-1]["slug"]), encoding="utf-8")
    fig_count = sum(1 for e in float_entries if e["kind"] == "fig")

    print(f"built {len(chapters)} chapter pages + index.html + {BOOK_INDEX_SLUG}.html + "
          f"{_FIGURES_GALLERY_SLUG}.html ({fig_count} figures)")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    # `--pdf` is the opt-in print edition (the print-native Typst render); default is the fast web build.
    if "--pdf" in args:
        raise SystemExit(build_pdf())
    # `--verify-pdf` runs ONLY the content-integrity gate over an existing book/mage-book.pdf (CI reuses it).
    if "--verify-pdf" in args:
        pdf = HERE / _PDF_FILENAME
        if not pdf.is_file():
            print(f"ERROR: {pdf} not found — run `--pdf` first.", file=sys.stderr)
            raise SystemExit(2)
        raise SystemExit(verify_pdf(pdf))
    raise SystemExit(build())
