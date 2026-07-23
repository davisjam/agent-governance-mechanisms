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

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent  # the catalogue root — the appendix reads the entry .md files from here
ACCENT = "#1a4a7a"
COPYRIGHT = "© James C. Davis, 2026–present"

# Mermaid runtime (CDN) — pulled in so the appendix's ```mermaid placeholder blocks render as diagrams.
MERMAID_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
    "<script>mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });</script>"
)

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
    1: "The Context",
    2: "The Mindset",
    3: "The Governed Engineering Environment",
    4: "The Model Zoo",
    5: "Putting It to Work",
    6: "Back Matter",
}

# Per-Part epigraph rendered at the opener of the first chapter in each numbered Part. Each is a
# (quote, attribution) pair. The two literary quotations (Macbeth, Ecclesiastes) are verbatim from
# the source memoir; the Context and Governed-Environment openers use a regulatory line and the
# book's own thesis, respectively (candidates a human editor may swap).
_PART_EPIGRAPHS: dict[int, tuple[str, str]] = {
    1: (
        "Just as stairs can exclude people who use wheelchairs, inaccessible web content "
        "and mobile apps can exclude people with disabilities.",
        "U.S. Department of Justice, Title II Final Rule, 2024",
    ),
    2: (
        "It is a tale told by an idiot, full of sound and fury, signifying nothing.",
        "William Shakespeare, Macbeth",
    ),
    3: (
        "Govern the conditions under which fast code can be trusted.",
        "the thesis of this book",
    ),
    4: (
        "All models are wrong, but some are useful.",
        "George E. P. Box",
    ),
    5: (
        "I applied mine heart to know, and to search, and to seek out wisdom, and the "
        "reason of things.",
        "King Solomon (Ecclesiastes 7:25)",
    ),
}

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


def parse_chapter(path: pathlib.Path, part: int, chapter: int, metrics: dict[str, str]) -> dict:
    text = _apply_metrics(path.read_text(encoding="utf-8"), metrics)
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
        "body_md": "\n".join(lines).strip(),
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
    return found


def _abbr_cite(m: "re.Match[str]") -> str:
    """A `[[slug|text]]` / `[[slug]]` abstraction citation from a catalogue entry → a link into the
    catalogue's rendered abstractions glossary (one level up from book/)."""
    slug = m.group(1).strip()
    text = (m.group(2) or slug).strip()
    return f'<a href="../ABSTRACTIONS.html#{html.escape(slug, quote=True)}">{html.escape(text, quote=False)}</a>'


def inline(s: str) -> str:
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
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    # Restore the stashed code spans as <code> (their content is already HTML-escaped).
    s = re.sub(r"\x00CODE(\d+)\x00", lambda m: f"<code>{code_spans[int(m.group(1))]}</code>", s)
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
    cap_html = f"<figcaption>{inline(caption)}</figcaption>" if caption else ""
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
    alt = html.escape(caption or asset.stem, quote=True)
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
           f'<a href="{src}">Open the full interactive map ›</a></figcaption>') if caption else ""
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


def md_to_html(md: str, anchor_map: dict[tuple[str, str, int], str] | None = None) -> str:
    """Convert the markdown subset the chapters use into HTML.

    `anchor_map` (optional) maps `(concept-slug, "def"|"ex", occurrence-on-this-page)` → the anchor id the
    curated index links to. When a `<!-- index-def: … -->` / `<!-- index-example: … -->` tag is met, its
    anchor is attached to the FOLLOWING rendered block (per book/AGENTS.md §6). Occurrences are counted
    per (slug, kind) in reading order to match `_harvest_concept_tags`."""
    out: list[str] = []
    blocks = _split_blocks(md)
    pending_anchor: str | None = None       # anchor id to inject onto the next content block
    occ: dict[tuple[str, str], int] = {}    # per-page (slug, kind) → next occurrence index

    def _emit(block_html: str) -> None:
        nonlocal pending_anchor
        if pending_anchor is not None:
            block_html = _inject_anchor_id(block_html, pending_anchor)
            pending_anchor = None
        out.append(block_html)

    def _consume_index_tag(line: str) -> bool:
        """If `line` is a lone index-def / index-example tag, arm the pending anchor for the next block
        and return True. A tag may sit on its own line at the head of a block that ALSO holds the block it
        annotates (no blank line between), so this is called both on a standalone comment block and on the
        first line of a multi-line block."""
        nonlocal pending_anchor
        s = line.strip()
        _md, _me = INDEX_DEF_RE.match(s), INDEX_EXAMPLE_RE.match(s)
        if not (_md or _me):
            return False
        slug = (_md or _me).group(1)
        kind = "def" if _md else "ex"
        n = occ.get((slug, kind), 0)
        occ[(slug, kind)] = n + 1
        if anchor_map is not None:
            got = anchor_map.get((slug, kind, n))
            if got is not None:
                pending_anchor = got
        return True

    for block in blocks:
        block = block.strip("\n")
        if not block.strip():
            continue
        # Peel a leading index tag off the block. The tag attaches its anchor to the block it heads (the
        # renderer arms `pending_anchor` and injects it on the next emitted content). A block may be JUST
        # the tag (blank line follows) or the tag PLUS its annotated block (no blank line) — handle both.
        blk_lines = block.splitlines()
        while blk_lines and _consume_index_tag(blk_lines[0]):
            blk_lines = blk_lines[1:]
        if not blk_lines:
            continue  # the block was nothing but tag comment(s)
        block = "\n".join(blk_lines)
        stripped = block.strip()
        # Fenced code — a ```mermaid block renders as <pre class="mermaid"> (the mermaid runtime
        # transforms it into a diagram); any other fenced block renders as a plain <pre><code>.
        if stripped.startswith("```"):
            lines = block.splitlines()
            lang = lines[0].strip()[3:].strip().lower()
            inner_lines = lines[1:]
            if inner_lines and inner_lines[-1].strip() == "```":
                inner_lines = inner_lines[:-1]
            inner = "\n".join(inner_lines)
            if lang == "mermaid":
                _emit(f'<pre class="mermaid">{html.escape(inner, quote=False)}</pre>')
            else:
                _emit(f"<pre><code>{html.escape(inner, quote=False)}</code></pre>")
            continue
        # Gap-marker callouts.
        if stripped.startswith("[FILL IN:") or stripped.startswith("[MORE CHAPTERS FOLLOW:"):
            kind = "fill" if stripped.startswith("[FILL IN:") else "more"
            label = "FILL IN" if kind == "fill" else "MORE CHAPTERS FOLLOW"
            inner = stripped[stripped.index(":") + 1:].rstrip("]").strip()
            # A plain <div> (not <aside>): <aside> is a `complementary` landmark, and two markers on one
            # page trip html-validate's unique-landmark rule (each landmark needs a unique accessible name).
            _emit(
                f'<div class="marker marker-{kind}">'
                f'<span class="marker-tag">{label}</span> {inline(inner)}</div>'
            )
            continue
        # Figure directive: `<!-- figure: <path> | <caption> -->` → a <figure> with inline SVG
        # (or <img> for a raster) + <figcaption>. Checked BEFORE the generic-comment passthrough
        # so a figure comment is rendered, not emitted raw.
        if stripped.startswith("<!--") and stripped.endswith("-->") \
                and stripped.count("<!--") == 1 \
                and stripped[4:].lstrip().startswith("figure:"):
            _emit(_figure_block(stripped))
            continue
        # Figure-iframe directive: `<!-- figure-iframe: <path> | <caption> | <a11y-title> -->` → a
        # <figure><iframe> preview of a self-contained figure page (the rewired mechanism map), never
        # inlined. Checked before the generic-comment passthrough for the same reason.
        if stripped.startswith("<!--") and stripped.endswith("-->") \
                and stripped.count("<!--") == 1 \
                and stripped[4:].lstrip().startswith("figure-iframe:"):
            _emit(_figure_iframe_block(stripped))
            continue
        # A standalone HTML comment (e.g. the TODO markers) — emit it raw so it stays an invisible
        # comment in the source rather than escaped visible text.
        if stripped.startswith("<!--") and stripped.endswith("-->") and stripped.count("<!--") == 1:
            out.append(stripped)
            continue
        # Headings. A trailing `{#slug}` sets the heading's id anchor (used by the appendix so the
        # rewired mechanism-map figure can deep-link each pattern); it is stripped from the visible text.
        if stripped.startswith("### "):
            txt, anc = _heading_anchor(stripped[4:])
            _emit(f"<h3{anc}>{inline(txt)}</h3>")
            continue
        if stripped.startswith("## "):
            txt, anc = _heading_anchor(stripped[3:])
            _emit(f"<h2{anc}>{inline(txt)}</h2>")
            continue
        if stripped.startswith("# "):
            txt, anc = _heading_anchor(stripped[2:])
            _emit(f"<h1{anc}>{inline(txt)}</h1>")
            continue
        # Blockquote (all lines start with >). Its inner content is itself markdown — a `> ###`
        # heading, `> ` prose paragraphs, a `> ```mermaid ``` fence — so strip the `>` prefix and
        # render the inner content recursively. This is what makes a boxed concept-primer inset
        # (a heading + prose + a diagram) render as structured content, not one flattened line.
        if all(ln.strip().startswith(">") for ln in block.splitlines()):
            inner_md = "\n".join(_strip_blockquote_prefix(ln) for ln in block.splitlines())
            inner_html = md_to_html(inner_md)
            # An inset's `### Title` is a callout LABEL, not a document-outline heading. Rendering it as
            # <hN> makes axe flag a heading-order skip when an inset sits right after the chapter <h1>.
            # Demote any heading inside a blockquote to a styled paragraph, preserving its {#id} anchor.
            inner_html = re.sub(r"<h[1-6]([^>]*)>(.*?)</h[1-6]>", r'<p class="inset-title"\1>\2</p>', inner_html, flags=re.S)
            _emit(f"<blockquote>{inner_html}</blockquote>")
            continue
        # Pipe table (a header row, a `|---|---|` separator, then body rows). GitHub-flavored
        # markdown tables — the invariant/checker tables in the model pages depend on this.
        if _is_pipe_table(block):
            _emit(_render_pipe_table(block))
            continue
        # Unordered list (all lines start with - ).
        if all(ln.strip().startswith("- ") for ln in block.splitlines()):
            items = "".join(f"<li>{inline(ln.strip()[2:])}</li>" for ln in block.splitlines())
            _emit(f"<ul>{items}</ul>")
            continue
        # Paragraph (join wrapped lines).
        _emit(f"<p>{inline(' '.join(ln.strip() for ln in block.splitlines()))}</p>")
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


def _render_pipe_table(block: str) -> str:
    """Render a GitHub-flavored pipe table into an HTML <table> with a <thead> and <tbody>. The
    separator row (line 2) is consumed for structure, not rendered."""
    lines = block.splitlines()
    header = _split_table_row(lines[0])
    body_rows = [_split_table_row(ln) for ln in lines[2:] if ln.strip()]
    thead = "".join(f"<th>{inline(c)}</th>" for c in header)
    trs = []
    for row in body_rows:
        tds = "".join(f"<td>{inline(c)}</td>" for c in row)
        trs.append(f"<tr>{tds}</tr>")
    return (
        '<table class="book-table"><thead><tr>'
        f"{thead}</tr></thead><tbody>{''.join(trs)}</tbody></table>"
    )


CSS = f"""
:root {{ --accent: {ACCENT}; }}
* {{ box-sizing: border-box; }}
body {{ font: 17px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
       color: #1a1a1a; margin: 0; background: #fdfdfc; }}
.wrap {{ max-width: 52rem; margin: 0 auto; padding: 0 1.4rem 4rem; }}
nav.toc {{ background: #f4f3f0; border-bottom: 1px solid #e2e0da; padding: 0.9rem 1.4rem; font-size: 14px; }}
nav.toc .toc-inner {{ max-width: 52rem; margin: 0 auto; }}
nav.toc details {{ margin: 0; }}
nav.toc summary {{ cursor: pointer; font-weight: 600; color: var(--accent); list-style: none; }}
nav.toc summary::-webkit-details-marker {{ display: none; }}
nav.toc ol {{ list-style: none; padding: 0.6rem 0 0; margin: 0; }}
nav.toc .part {{ font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 0.04em;
                 font-size: 12px; margin: 0.7rem 0 0.25rem; }}
nav.toc a {{ color: #333; text-decoration: none; display: block; padding: 2px 0 2px 1rem; }}
nav.toc a:hover {{ color: var(--accent); }}
nav.toc a.current {{ color: var(--accent); font-weight: 600; border-left: 2px solid var(--accent);
                     padding-left: calc(1rem - 2px); }}
header.chap {{ padding: 2.6rem 0 1.2rem; border-bottom: 1px solid #eee; margin-bottom: 1.6rem; }}
header.chap .kicker {{ color: var(--accent); font-weight: 700; font-size: 13px; letter-spacing: 0.06em;
                       text-transform: uppercase; }}
header.chap h1 {{ font-size: 2rem; line-height: 1.15; margin: 0.35rem 0 0; }}
.part-epigraph {{ margin: 1.6rem 0 0; padding: 0.8rem 0 0.2rem 1.1rem; border-left: 3px solid #d8d5cc;
                  color: #555; font-style: italic; }}
.part-epigraph .attr {{ display: block; margin-top: 0.5rem; font-style: normal; font-size: 14px;
                        color: #6a6a6a; }}
h2 {{ font-size: 1.32rem; margin: 2.2rem 0 0.6rem; }}
h3 {{ font-size: 1.08rem; margin: 1.6rem 0 0.4rem; }}
p {{ margin: 0 0 1rem; }}
ul {{ margin: 0 0 1rem; padding-left: 1.3rem; }}
li {{ margin: 0.3rem 0; }}
blockquote {{ margin: 1.2rem 0; padding: 0.6rem 1.1rem; border-left: 3px solid #d8d5cc;
              color: #555; font-style: italic; background: #faf9f6; }}
code {{ background: #f0efeb; padding: 0.1em 0.35em; border-radius: 3px; font-size: 0.9em; }}
a {{ color: var(--accent); }}
table.book-table {{ border-collapse: collapse; width: 100%; margin: 1.2rem 0; font-size: 15px; }}
table.book-table th, table.book-table td {{ border: 1px solid #e2e0da; padding: 0.45rem 0.6rem;
                                             text-align: left; vertical-align: top; line-height: 1.45; }}
table.book-table thead th {{ background: #f4f3f0; font-weight: 600; }}
table.book-table tbody tr:nth-child(even) {{ background: #faf9f6; }}
blockquote table.book-table {{ background: #fff; }}
blockquote .inset-title {{ font-style: normal; font-weight: 700; margin: 0 0 0.4rem; }}
blockquote pre.mermaid {{ font-style: normal; }}
figure.book-figure {{ margin: 1.8rem 0; text-align: center; }}
figure.book-figure svg,
figure.book-figure img {{ max-width: 100%; height: auto; }}
figure.book-figure figcaption {{ font-size: 14px; color: #666; margin-top: 0.6rem;
                                text-align: left; line-height: 1.5; }}
.marker {{ margin: 1.3rem 0; padding: 0.75rem 1rem; border-radius: 5px; font-size: 15px; }}
.marker-fill {{ background: #fff6e5; border: 1px dashed #d8a23a; }}
.marker-more {{ background: #eef3f7; border: 1px dashed #7aa0bd; }}
.marker-tag {{ display: inline-block; font-weight: 700; font-size: 11px; letter-spacing: 0.05em;
               padding: 1px 6px; border-radius: 3px; margin-right: 0.5rem; vertical-align: 1px; }}
.marker-fill .marker-tag {{ background: #a06a12; color: #fff; }}
.marker-more .marker-tag {{ background: #4a6f8c; color: #fff; }}
.pager {{ display: flex; justify-content: space-between; align-items: stretch; gap: 1rem;
          margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid #eee; }}
.pager a, .pager .disabled {{ text-decoration: none; color: #333; flex: 1; padding: 0.7rem 0.9rem;
            border: 1px solid #e2e0da; border-radius: 6px; background: #fff; }}
.pager a:hover {{ border-color: var(--accent); }}
.pager .dir {{ display: block; font-size: 12px; color: #5f5f5f; text-transform: uppercase; letter-spacing: 0.05em; }}
.pager .ttl {{ color: var(--accent); font-weight: 600; }}
.pager .next {{ text-align: right; }}
.pager .disabled {{ visibility: hidden; }}
.pager .home {{ flex: 0 0 auto; align-self: center; }}
.book-foot {{ margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid #eee; color: #6a6a6a;
              font-size: 13px; text-align: center; }}
/* index page */
.book-title {{ padding: 3rem 0 0.5rem; }}
.book-title h1 {{ font-size: 2.4rem; margin: 0; }}
.book-title .sub {{ color: #666; margin-top: 0.4rem; }}
.idx .part {{ font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em;
             font-size: 13px; margin: 2rem 0 0.5rem; }}
.idx ol {{ list-style: none; padding: 0; margin: 0; }}
.idx li {{ margin: 0.35rem 0; }}
.idx a {{ text-decoration: none; }}
.idx .cnum {{ color: #6a6a6a; font-variant-numeric: tabular-nums; margin-right: 0.5rem; }}
/* term index page */
.idx-terms ul {{ list-style: none; padding: 0; margin: 0 0 1rem; }}
.idx-terms li {{ margin: 0.3rem 0; }}
.idx-terms .idx-term {{ font-weight: 600; }}
.idx-terms .idx-refs {{ color: #5f5f5f; font-size: 14px; }}
.idx-terms .idx-refs a {{ margin-left: 0.15rem; }}
/* curated concept entry: a definition-of / examples-of sub-block under the concept name */
.idx-terms li.idx-concept {{ margin: 0.55rem 0; }}
.idx-concept .idx-subs {{ display: block; margin: 0.15rem 0 0 1rem; }}
.idx-concept .idx-sub {{ display: block; font-size: 14px; color: #444; line-height: 1.6; }}
.idx-concept .idx-sub-lead {{ color: #595959; font-style: italic; margin-right: 0.35rem; }}
/* Underline the locators so a link is distinguished from the "definition of:" lead text without relying
   on color alone (axe link-in-text-block). */
.idx-concept .idx-sub a {{ margin-right: 0.4rem; text-decoration: underline; }}
/* iframe figure embed (the rewired mechanism map) */
figure.book-figure.catalogue-embed iframe {{ width: 100%; height: 600px; border: 1px solid #e2e0da;
                                             border-radius: 6px; background: #fff; }}
/* jump controls — top nav + bottom pager: next PART / next CHAPTER / END / INDEX */
.jump {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }}
.jump a {{ display: inline-block; font-size: 12px; letter-spacing: 0.03em; text-transform: uppercase;
           font-weight: 600; color: var(--accent); text-decoration: none; padding: 3px 9px;
           border: 1px solid #d8d5cc; border-radius: 4px; background: #fff; }}
.jump a:hover {{ border-color: var(--accent); background: #f4f3f0; }}
nav.toc .jump {{ margin-top: 0.7rem; }}
.pager-jump {{ margin-top: 1.2rem; }}
.pager-jump .jump {{ justify-content: center; margin-top: 0; }}
"""


def _chap_ref(c: dict) -> str:
    """The 'N.M' reference for a numbered chapter, or '' for front/back matter."""
    return "" if c.get("is_matter") or c.get("is_appendix") else f'{c["part"]}.{c["chapter"]}'


def _toc_prefix(c: dict) -> str:
    ref = _chap_ref(c)
    return f"{ref}&nbsp; " if ref else ""


def _pager_label(c: dict) -> str:
    ref = _chap_ref(c)
    prefix = f"{ref} · " if ref else ""
    return f'{prefix}{c["chapter_title"]}'


BOOK_INDEX_SLUG = "book-index"  # the autogenerated term index page (see build_index_page)


def _jump_targets(chapters: list[dict], idx: int) -> list[tuple[str, str]]:
    """The jump-control targets for the chapter at position `idx`: next PART, next CHAPTER, END, INDEX.
    Returns an ordered list of (label, href) pairs; a target with no destination (e.g. next-part from the
    last part) is dropped, so a control appears only when it can go somewhere."""
    cur = chapters[idx]
    out: list[tuple[str, str]] = []
    # Next PART — the first chapter whose part number differs from the current part.
    nxt_part = next((c for c in chapters[idx + 1:] if c["part"] != cur["part"]), None)
    if nxt_part:
        out.append(("Next part ⇒", f'{nxt_part["slug"]}.html'))
    # Next CHAPTER — the immediately following chapter, when it exists and isn't already the next-part jump.
    if idx + 1 < len(chapters):
        nxt = chapters[idx + 1]
        if not nxt_part or nxt["slug"] != nxt_part["slug"]:
            out.append(("Next chapter ›", f'{nxt["slug"]}.html'))
    # END — the last chapter, unless we are already on it.
    if idx != len(chapters) - 1:
        out.append(("End ⇥", f'{chapters[-1]["slug"]}.html'))
    # INDEX — always available (the term index sits after the appendix).
    out.append(("Index", f"{BOOK_INDEX_SLUG}.html"))
    return out


def _jump_html(chapters: list[dict], idx: int) -> str:
    """Render the jump controls as a small row of links, for the top nav and the bottom pager alike."""
    links = "".join(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href in _jump_targets(chapters, idx)
    )
    return f'<div class="jump">{links}</div>'


def toc_html(chapters: list[dict], current_slug: str | None, jump: str = "") -> str:
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
        '<nav class="toc"><div class="toc-inner"><details>'
        "<summary>☰&nbsp; Contents</summary>"
        f'<ol>{inner}</ol></details>{jump}</div></nav>'
    )


def _part_label(c: dict) -> str:
    """The heading a Part gets in the TOC / index. Front and back matter and the appendix name
    themselves; numbered Parts get 'Part N — Title'."""
    if c.get("is_appendix"):
        return c["part_title"]
    if c["part"] in (0, 6):
        return c["part_title"]
    return f'Part {c["part"]} — {c["part_title"]}'


def page(title: str, toc: str, main: str, mermaid: bool = False) -> str:
    runtime = MERMAID_CDN if mermaid else ""
    # <main> landmark so the content is a single main region (axe landmark-one-main / region). It carries
    # an aria-label of the page title so it stays a UNIQUELY-NAMED main landmark even when a page embeds the
    # mechanism-map figure in an <iframe> — axe flattens the iframe, and the figure has its own <main>; two
    # unnamed main landmarks would trip landmark-unique, so name this one.
    label = html.escape(title, quote=True)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
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
                "sections": sections,
                "fill": _load_fill(role_dir, slug),
            })
    return out


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


def _appendix_pattern_page_md(rec: dict) -> str:
    """One pattern rendered as a WHOLE PAGE of GoF-layout markdown. The pattern NAME is the page `<h1>`
    (from the chapter dict's `chapter_title`), so this body emits no leading `#`/`##` name heading — it
    leads with the Structure diagram (visual first), then an in-page table of contents of the elements
    present, then the eight elements as `## ` (h2) headings in canonical order. External `#<slug>` links
    still resolve: the slug anchor rides on the projection note. The Structure diagram is rendered at the
    top; its `## Structure` heading sits in canonical position and links back up to the diagram."""
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

    # The FIRST present element's heading carries the pattern's page-level `{#slug}` anchor (so external
    # `#<slug>` deep-links and any old figure fragments still land on this page); every other element gets
    # its `#el-<name>` anchor. The element TOC links to whichever id each element's heading actually bears.
    anchor_for = {}
    for i, el in enumerate(present):
        anchor_for[el] = rec["slug"] if i == 0 else _element_anchor(el)

    # 3. ELEMENT TOC — a short in-page list linking each element heading present on the page.
    toc_items = " · ".join(f"[{el}](#{anchor_for[el]})" for el in present)
    parts += [f"**On this page:** {toc_items}", ""]

    # 4. THE ELEMENTS — canonical order, each an `## ` (h2) heading carrying its TOC/legacy anchor.
    for el in _GOF_ELEMENTS:
        if el not in present:
            continue
        head = f"## {el} {{#{anchor_for[el]}}}"
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

This appendix is the governance catalogue rendered as a pattern language, in the style Gamma, Helm, \
Johnson, and Vlissides made standard in *Design Patterns* — the [\"Gang of Four\"]\
(https://en.wikipedia.org/wiki/Design_Patterns). Each governance mechanism becomes one pattern, written \
to the same fixed elements a reader of that book already knows.

Every pattern page carries the classic slots:

- **Intent** — one line: the failure class this mechanism kills, and the shape that kills it.
- **Motivation** — the recurring failure told as a scenario, and why the naive fix does not hold.
- **Applicability** — the conditions under which reaching for this pattern pays off.
- **Structure** — a diagram of the moving parts and how they connect.
- **Sample Code** — a concrete instance: the wiring, the lint, or the typed seam that realizes it.
- **Consequences** — what adopting it costs and buys, and the second-order effects to watch.
- **Known Uses** — where the mechanism runs in a live system.
- **Related Patterns** — the neighbours it composes with, and the ones it is often confused for.

Read a single page to adopt one mechanism. Read a family in order to see how a cluster of them reinforce \
each other. The map below is the fast index: click any mechanism to open its pattern."""


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


def _appendix_contents_md(ordered: list[dict]) -> str:
    """The opening page's text table of contents, in census-map hierarchy: an `## ` (h2) heading per target
    (Agent / Models-bridge / Product), an `### ` (h3) sub-heading per family, and a linked bullet list of
    the family's patterns under it. `ordered` is the already role/family-ordered pattern-record list; each
    record carries the page slug the pattern renders at."""
    parts: list[str] = ["## Contents", ""]
    last_group: str | None = None
    last_family: str | None = None
    for rec in ordered:
        if rec["group"] != last_group:
            parts += [f"### {rec['group']}", ""]
            last_group, last_family = rec["group"], None
        if rec["family"] != last_family:
            parts += [f"**{_family_display(rec['family'])}**", ""]
            last_family = rec["family"]
        parts += [f"- [{rec['name']}]({rec['page_slug']}.html)"]
    return "\n".join(parts).strip()


def build_appendix_chapters(next_part: int) -> list[dict]:
    """Build appendix 'chapter' records — ONE PER PATTERN plus one opening front-door page — each mirroring
    the chapter dict shape so the existing pager/TOC/index machinery renders it. Ordering follows the
    census-map hierarchy: Environment → target (Agent A / Models-bridge B / Product C) → family (census
    order) → mechanism. The opening page frames the appendix GoF-style, embeds the rewired mechanism-map
    figure, and lists the whole catalogue. Returns [] if no entries are found."""
    entries = _appendix_entries()
    if not entries:
        return []

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
    for rec in ordered:
        rec["page_slug"] = f"appendix-{role_letter[rec['group']].lower()}-{rec['slug']}"

    # Precompute the slug→pattern-page anchor map, then emit the rewired figure once (embedded on the
    # opening page only).
    anchor_map = _appendix_anchor_map(ordered)
    _emit_rewired_figure(anchor_map)

    chapters: list[dict] = []

    # OPENING PAGE — heads Appendix A's Part (first appendix Part), sorts before every pattern (chapter 0).
    opening_body = [
        _APPENDIX_OPENING_PROSE,
        "",
        # The census map — the clickable visual index into the pattern pages, embedded here only.
        f"<!-- figure-iframe: {_BOOK_FIGURE_NAME} | The governance mechanism map — every mechanism in the "
        "catalogue, organized by target zone and family. Click a mechanism to open its Gang-of-Four "
        "pattern. | The governance mechanism map: click any mechanism to open its Gang-of-Four pattern "
        "in this appendix. -->",
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

    # ONE PAGE PER PATTERN — in census-map order; part = role's appendix Part, chapter sorts within it by
    # (family census number, within-family index) so the pager walks A→B→C family-by-family.
    within_family_index = 0
    prev_family: str | None = None
    for rec in ordered:
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
            "chapter_title": f"Appendix {letter} · {rec['name']}",
            "body_md": _appendix_pattern_page_md(rec),
            "is_appendix": True,
            "mermaid": True,
        })
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
    """Map each catalogue entry slug → the BARE book pattern-page URL that renders it
    (`appendix-<letter>-<slug>.html`, no fragment — one page per pattern now). The rewired mechanism-map
    figure uses this to point each chip at the pattern's own page. `entries` must carry `page_slug`
    (set by build_appendix_chapters)."""
    return {e["slug"]: f"{e['page_slug']}.html" for e in entries}


# ─────────────────────────── Curated concept index — index-def / index-example tags ───────────────────────────
# Two HTML-comment tags (book/AGENTS.md §6) let an author point the index at a concept's DEFINING
# paragraph and its EXAMPLE paragraphs, instead of a heading-heuristic occurrence scan. The harvest below
# walks every page in reading order, assigns each example a global anchor number, and validates the tags
# (a concept has one canonical definition; a slug must be registered; an example needs a definition).

_CONCEPT_RE = re.compile(r"-\s*concept:\s*([a-z0-9-]+)\s*\|\s*(.+?)\s*$")


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

_LEXICON_REL = ("..", "plugin", "agent-governance", "skills", "self-communicate", "writing", "lexicon.md")
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
        md = pg["body_md"]
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
    """The short locator shown beside an index term for one page: 'Appendix A', 'Preface', or 'N.M'."""
    if pg.get("is_appendix"):
        # 'Appendix A · Brief-linting' → 'Appendix A'; the opening 'Appendix — the pattern language'
        # (no '·') → 'Appendix'. Prefer the '·' split (per-pattern titles), then the '—' split (opening).
        title = pg["chapter_title"]
        if "·" in title:
            return title.split("·")[0].strip()
        if "—" in title:
            return title.split("—")[0].strip()
        return title
    if pg.get("is_matter"):
        return pg["chapter_title"]
    return f'{pg["part"]}.{pg["chapter"]}'


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


def build_index_page(chapters: list[dict], concept_registry: dict[str, dict] | None = None) -> str:
    """Render `book-index.html` from the computed entries — an alphabetized index (curated concept entries +
    occurrence term entries) grouped by first letter. Returns the full page HTML."""
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
    body = header + intro + '<div class="idx idx-terms">' + "\n".join(rows) + "</div>"
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    # The index gets the whole-book TOC and its own jump row (Contents + first/last chapter + itself).
    jump = (
        '<div class="jump">'
        f'<a href="{chapters[0]["slug"]}.html">Start ⇤</a>'
        f'<a href="{chapters[-1]["slug"]}.html">End ⇥</a>'
        '<a href="index.html">Contents</a>'
        "</div>"
    )
    toc = toc_html(chapters, None, jump=jump)
    pager_jump = f'<div class="pager-jump">{jump}</div>'
    main = body + pager_jump + foot
    return page("Index · 3-D Printing Production Software", toc, main)


def build() -> int:
    metrics = _load_metrics()
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

    # Per-chapter pages.
    for i, c in enumerate(chapters):
        prev_c = chapters[i - 1] if i > 0 else None
        next_c = chapters[i + 1] if i < len(chapters) - 1 else None
        if c.get("is_appendix"):
            num_label = "Appendix"
        elif c.get("is_matter"):
            num_label = c["chapter_title"]  # "Preface" / "Conclusion"
        else:
            num_label = f'Chapter {c["part"]}.{c["chapter"]}'
        kicker = html.escape(_part_label(c))
        if not (c.get("is_appendix") or c.get("is_matter")):
            kicker = f'{kicker} &nbsp;::&nbsp; {html.escape(num_label)}'
        header = (
            f'<header class="chap"><div class="kicker">{kicker}</div>'
            f'<h1>{html.escape(c["chapter_title"])}</h1>'
            + (_epigraph_html(c["part"]) if c.get("show_epigraph") else "")
            + '</header>'
        )
        body = md_to_html(c["body_md"], anchor_map=page_anchor_maps.get(c["slug"]))
        if prev_c:
            prev_html = (
                f'<a class="prev" href="{prev_c["slug"]}.html"><span class="dir">‹ Previous</span>'
                f'<span class="ttl">{html.escape(_pager_label(prev_c))}</span></a>'
            )
        else:
            # A disabled pager is not a link — render an empty <span> (an empty <a href="#"> trips
            # html-validate's wcag/h30 "anchor must have text" rule).
            prev_html = '<span class="prev disabled" aria-hidden="true"></span>'
        home_html = '<a class="home" href="index.html">Contents</a>'
        if next_c:
            next_html = (
                f'<a class="next" href="{next_c["slug"]}.html"><span class="dir">Next ›</span>'
                f'<span class="ttl">{html.escape(_pager_label(next_c))}</span></a>'
            )
        else:
            next_html = '<span class="next disabled" aria-hidden="true"></span>'
        pager = f'<div class="pager">{prev_html}{home_html}{next_html}</div>'
        # Jump controls (next PART / next CHAPTER / END / INDEX) in BOTH the top nav and the bottom pager.
        jump = _jump_html(chapters, i)
        pager_jump = f'<div class="pager-jump">{jump}</div>'
        foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
        main = header + body + pager + pager_jump + foot
        toc = toc_html(chapters, c["slug"], jump=jump)
        out = HERE / f'{c["slug"]}.html'
        out.write_text(
            page(f'{num_label} · {c["chapter_title"]}', toc, main, mermaid=c.get("mermaid", False)),
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
    # Back-matter row on the landing page: the autogenerated term index (also reachable from every page's
    # INDEX nav button). Linking it here keeps it off the orphan-reachability list.
    idx_rows.append('<div class="part">Index</div><ol>')
    idx_rows.append(
        f'<li><a href="{BOOK_INDEX_SLUG}.html">'
        f'<span class="cnum">{"★":>2}</span>Index (terms)</a></li>'
    )
    idx_rows.append("</ol>")
    title_block = (
        '<div class="book-title"><h1>3-D Printing Production Software</h1>'
        '<div class="sub">Architecture, Validation, and Control for Agentic Software Engineering</div></div>'
    )
    foot = f'<div class="book-foot">{html.escape(COPYRIGHT)}</div>'
    main = title_block + '<div class="idx">' + "\n".join(idx_rows) + "</div>" + foot
    (HERE / "index.html").write_text(
        page("3-D Printing Production Software — Contents", "", main), encoding="utf-8"
    )

    # Autogenerated term index — placed after the appendix, reachable from the INDEX nav button.
    (HERE / f"{BOOK_INDEX_SLUG}.html").write_text(
        build_index_page(chapters, concept_registry), encoding="utf-8")

    print(f"built {len(chapters)} chapter pages + index.html + {BOOK_INDEX_SLUG}.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
