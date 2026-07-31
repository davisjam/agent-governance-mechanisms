"""A typed intermediate representation of the book — a stdlib parse into typed blocks that analyses
*walk*, instead of every lint re-deriving structure with its own regexes (the N-walkers smell).

WHY THIS EXISTS.  `build_book_html` parses the book several times over — float numbering, concept-tag
harvest, glossary, the notation-leak gate, and every structural check in `tests/book.py` — each pass with
its own regexes and each able to drift. This module is the one typed model those walks share. See
`book/IR-DESIGN.md` for the design and the C→A migration plan.

FOUNDATION — directive registry on our OWN stdlib parser (not a third-party engine).  `catalog.py` is
clone-and-run stdlib-only, so we cannot pull in `markdown-it-py` / MyST. Instead we adopt the *schema* of a
pluggable-markdown engine — a registry of `directive name → typed node` — while keeping our own runtime and
our degradation-friendly HTML-comment notation (`<!-- figure: … -->` is invisible in a plain MD viewer;
`:::figure` is not). Adding notation = one `_DIRECTIVES` row. This is the A.9 "adopt the schema, skip the
runtime" move, and it is on the path to a real engine later, not off it (IR-DESIGN.md §"If clone-and-run
is ever relaxed").

A-READY RULE (do not break).  Every `Block` carries its raw source slice, so the IR is never lossy and the
renderer can later emit *from* it (the C→A step) without re-adding detail. The block taxonomy mirrors the
renderer's own block handling 1:1 for the same reason.

TOKENIZER SSOT.  Block splitting, chapter discovery, and the marker regexes are imported from
`build_book_html` — there is exactly ONE tokenizer; this module is a typed layer over it, never a copy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

import build_book_html as bb  # SSOT: _split_blocks, _discover_chapters, _load_metrics, _is_pipe_table, _XREF_RE, _INSET_RE


class BlockKind(Enum):
    HEADING = "heading"
    PARA = "para"
    LIST = "list"              # unordered `- ` list
    TABLE = "table"            # a numbered float
    FIGURE = "figure"          # <!-- figure: … --> SVG/img — a numbered float
    MERMAID = "mermaid"        # a standalone ```mermaid fence — a numbered float
    CODE = "code"              # any other standalone fenced block
    CODE_INSET = "code-inset"  # <!-- inset: … --> + fence — NOT numbered
    BLOCKQUOTE = "blockquote"  # concept insets live here; their inner mermaid is NOT numbered
    ORDERED_LIST = "ordered-list"  # `N. ` list — a distinct render kind (<ol> vs <ul>)
    EQ = "eq"
    DIRECTIVE = "directive"    # a lone marker comment (label / index / gloss / noqa …) — renders no structure
    OTHER = "other"            # figure-iframe (catalogue embed) and anything unmatched


#: The three block kinds the build numbers as "Figure N." / "Table N." — the floats an author cross-refs.
FLOAT_KINDS = frozenset({BlockKind.FIGURE, BlockKind.TABLE, BlockKind.MERMAID})

#: One marker comment on its own line: `<!-- keyword: arg -->` or `<!-- keyword -->`.
_MARKER_LINE = re.compile(r"^<!--\s*([a-z0-9-]+)\s*(?::\s*(.*?))?\s*-->$", re.I)

#: The directive registry — the pluggable-notation SSOT. `arms` directives set state for the NEXT float
#: (label, caption); `emits` directives produce a block of the named kind; the rest are inert markers the
#: IR records as DIRECTIVE. `build_book_html.MARKER_KEYWORDS` is the render-side twin; the notation-leak
#: gate reads that. Keep the two in step when adding notation (IR-DESIGN.md §"Adding a directive").
_ARMS = {"label", "table"}                       # arm state consumed by the next float
_EMITS = {"figure": BlockKind.FIGURE, "figure-iframe": BlockKind.OTHER, "eq": BlockKind.EQ}


@dataclass
class Ref:
    """A `[ref:key]` cross-reference found in prose, with where it sits (for the before-its-float rule)."""
    key: str
    chapter_slug: str
    block_index: int


@dataclass
class Block:
    kind: BlockKind
    raw: str                                   # the raw source slice — A-ready, never lossy
    index: int                                 # position within the chapter's flat block list
    label: str | None = None                   # a float's cross-ref key (from a <!-- label: … --> arming it)
    caption: str | None = None                 # a float's caption text, if any
    heading_level: int = 0                     # 1..6 for HEADING
    directive: str | None = None               # for DIRECTIVE/OTHER: the marker keyword
    refs: list[Ref] = field(default_factory=list)  # [ref:key] tokens in this block's prose

    @property
    def is_float(self) -> bool:
        return self.kind in FLOAT_KINDS

    #: Block kinds this node can render from its raw slice with NO cross-block or arming state — the
    #: render-complete subset (the C→A enrich step). The stateful kinds a full flip must still thread
    #: through the renderer's arming loop are excluded: MERMAID (a following italic paragraph may fold in
    #: as its caption), FIGURE / EQ / OTHER / DIRECTIVE (emitted by an arming marker, may carry a
    #: `data-label`), and TABLE (a `<!-- table: -->` caption / label may arm it). See `render_html`.
    _RENDER_COMPLETE = frozenset({
        BlockKind.HEADING, BlockKind.PARA, BlockKind.LIST, BlockKind.ORDERED_LIST,
        BlockKind.CODE, BlockKind.CODE_INSET, BlockKind.BLOCKQUOTE,
    })

    @property
    def is_render_complete(self) -> bool:
        """True when `render_html()` can produce this block's HTML from its raw slice alone — no arming
        marker (label/caption/anchor) and no cross-block fold participates. The C→A enrich step made the IR
        render-complete for this subset; a full flip renders these from the node and threads only the rest."""
        return self.kind in Block._RENDER_COMPLETE

    def render_html(self) -> str:
        """Render this block's HTML from its raw slice — byte-identical to `md_to_html`'s emit for the
        render-complete kinds (the enrich step's proof that the IR node holds enough to render). Delegates
        to the renderer's extracted per-kind primitives (the ONE renderer, never a copy). Raises for a kind
        that needs the renderer's arming/fold state, so a caller cannot silently drop a float's label."""
        if not self.is_render_complete:
            raise ValueError(
                f"{self.kind.value} is not render-complete: it needs the renderer's arming/fold state "
                f"(label / caption / anchor / mermaid-caption fold); render it through md_to_html")
        import build_book_html as _bb
        k = self.kind
        if k is BlockKind.HEADING:
            return _bb._render_heading(self.raw)
        if k is BlockKind.PARA:
            # A standalone HTML comment (an authoring TODO not in the notation vocabulary — so not peeled as
            # a DIRECTIVE) renders RAW, not wrapped in <p>. `classify_render_block` reports it PARA because
            # it is prose-shaped; the renderer keeps a lone-comment passthrough just ahead of prose, and this
            # mirrors it so `render_html` on such a block equals the emit.
            s = self.raw.strip()
            if s.startswith("<!--") and s.endswith("-->") and s.count("<!--") == 1:
                return s
            return _bb._render_paragraph(self.raw)
        if k is BlockKind.LIST:
            return _bb._render_unordered_list(self.raw)
        if k is BlockKind.ORDERED_LIST:
            return _bb._render_ordered_list(self.raw)
        if k is BlockKind.CODE:
            return _bb._render_code(self.raw)
        if k is BlockKind.CODE_INSET:
            return _bb._render_inset(self.raw)
        return _bb._render_blockquote(self.raw)  # BLOCKQUOTE


@dataclass
class Chapter:
    slug: str
    part: int
    title: str
    blocks: list[Block]

    def floats(self) -> list[Block]:
        return [b for b in self.blocks if b.is_float]

    def refs(self) -> list[Ref]:
        return [r for b in self.blocks for r in b.refs]


@dataclass
class Document:
    chapters: list[Chapter]

    def floats(self) -> "list[tuple[Chapter, Block]]":
        return [(c, b) for c in self.chapters for b in c.floats()]

    def refs(self) -> list[Ref]:
        return [r for c in self.chapters for r in c.refs()]

    def labels(self) -> "dict[str, tuple[Chapter, Block]]":
        """key → (chapter, float) for every labelled float — the resolve target set for `[ref:]`."""
        return {b.label: (c, b) for c in self.chapters for b in c.floats() if b.label}


def _fig_caption(arg: str) -> "str | None":
    """The caption of a `<!-- figure: <src> | <caption> -->` directive (the part after `|`), or None."""
    return arg.split("|", 1)[1].strip() if "|" in arg else None


def _classify_prose(text: str) -> BlockKind:
    """Classify a block's non-marker remainder. Mirrors the renderer's block dispatch order so the IR block
    taxonomy equals what gets rendered (the A-migration 1:1 rule)."""
    s = text.lstrip()
    if s.startswith("```"):
        lang = s[3:].split("\n", 1)[0].strip().lower()
        return BlockKind.MERMAID if lang == "mermaid" else BlockKind.CODE
    if bb._is_pipe_table(text):
        return BlockKind.TABLE
    if s.startswith("#"):
        return BlockKind.HEADING
    if s.startswith(">"):
        return BlockKind.BLOCKQUOTE  # concept insets; an inner `> ```mermaid` is NOT a standalone float
    if s.startswith("- "):
        return BlockKind.LIST
    if re.match(r"^\d+\.\s", s):
        return BlockKind.ORDERED_LIST  # `N. ` list → <ol> (distinct from the `- ` unordered <ul>)
    return BlockKind.PARA


def classify_render_block(block: str) -> BlockKind:
    """Classify one whole render block EXACTLY as `build_book_html.md_to_html`'s emit loop dispatches it —
    the single classifier the renderer's content dispatch now calls, so one parse feeds both render and
    analysis (the C→A flip). Mirrors the renderer's precise branch order and tests (a space-delimited
    heading, an all-lines `>` blockquote, a `_is_pipe_table` table), NOT the looser `_classify_prose` shape
    tests. Returns CODE_INSET / MERMAID / CODE / HEADING / BLOCKQUOTE / TABLE / LIST / ORDERED_LIST / PARA.

    Two shapes render-loop-inline that this reports as PARA (they are prose-shaped and the renderer keeps a
    literal test for them just ahead of prose): a `[FILL IN: …]` / `[MORE CHAPTERS FOLLOW: …]` gap marker,
    and a standalone HTML comment. The renderer's own conditionals catch those before falling through to the
    PARA renderer; the classifier need not distinguish them."""
    stripped = block.strip()
    lines = stripped.splitlines()
    first = lines[0].strip() if lines else ""
    # Inset: `<!-- inset: <title> -->` glued to the head of a fenced code block.
    if bb._INSET_RE.match(first) and len(lines) > 1 and lines[1].strip().startswith("```"):
        return BlockKind.CODE_INSET
    # Fenced code — a ```mermaid fence is a numbered figure; any other fence is a plain code block.
    if first.startswith("```"):
        lang = first[3:].strip().lower()
        return BlockKind.MERMAID if lang == "mermaid" else BlockKind.CODE
    # Heading (space-delimited `# ` … `#### `).
    if any(stripped.startswith(h) for h in ("#### ", "### ", "## ", "# ")):
        return BlockKind.HEADING
    # Blockquote — EVERY line starts with `>` (matches the renderer's `all(...)` test).
    if lines and all(ln.strip().startswith(">") for ln in block.splitlines()):
        return BlockKind.BLOCKQUOTE
    # Pipe table.
    if bb._is_pipe_table(block):
        return BlockKind.TABLE
    # Unordered / ordered list (keyed on the first line, as the renderer does).
    if first.startswith("- "):
        return BlockKind.LIST
    if re.match(r"^\d+\.\s", first):
        return BlockKind.ORDERED_LIST
    return BlockKind.PARA


def _find_refs(text: str, slug: str, index: int) -> list[Ref]:
    return [Ref(m.group(1), slug, index) for m in bb._XREF_RE.finditer(text)]


def _parse_chapter(rec: dict) -> Chapter:
    slug = rec["slug"]
    blocks: list[Block] = []
    pending_label: "str | None" = None      # a <!-- label: --> waiting for its float
    pending_caption: "str | None" = None    # a <!-- table: --> caption waiting for its table

    for raw in bb._split_blocks(rec["body_md"]):
        raw = raw.strip("\n")
        if not raw.strip():
            continue
        lines = raw.splitlines()
        first = lines[0].strip()

        # A titled inset (`<!-- inset: … -->` glued to a fence) is a set-apart box, NOT a numbered float —
        # detect it BEFORE peeling so its inner mermaid never counts as a "Figure N".
        if bb._INSET_RE.match(first) and len(lines) > 1 and lines[1].strip().startswith("```"):
            blocks.append(Block(BlockKind.CODE_INSET, raw, len(blocks), directive="inset"))
            continue

        # Peel leading marker comments (placement-robust — a marker may sit glued to the prose/float it
        # heads). `label`/`table` arm the next float; `figure`/`eq` emit; the rest are inert DIRECTIVEs.
        while lines:
            m = _MARKER_LINE.match(lines[0].strip())
            if not m:
                break
            kw, arg = m.group(1).lower(), (m.group(2) or "").strip()
            if kw == "label":
                pending_label = arg
            elif kw == "table":
                pending_caption = arg
            elif kw == "figure":
                blocks.append(Block(BlockKind.FIGURE, lines[0].strip(), len(blocks),
                                    label=pending_label, caption=_fig_caption(arg)))
                pending_label = None
            elif kw in _EMITS:
                blocks.append(Block(_EMITS[kw], lines[0].strip(), len(blocks), directive=kw))
            else:
                blocks.append(Block(BlockKind.DIRECTIVE, lines[0].strip(), len(blocks), directive=kw))
            lines = lines[1:]

        remaining = "\n".join(lines).strip("\n")
        if not remaining.strip():
            continue  # block was nothing but marker comment(s)

        kind = _classify_prose(remaining)
        idx = len(blocks)
        b = Block(kind, remaining, idx)
        if kind in (BlockKind.MERMAID, BlockKind.TABLE):   # a float armed by the pending state
            b.label, pending_label = pending_label, None
            if kind is BlockKind.TABLE:
                b.caption, pending_caption = pending_caption, None
        elif kind is BlockKind.HEADING:
            # B1 fix: compute the depth from the REMAINING heading line (after leading markers were peeled),
            # not the block's original `first` line. When a marker comment is glued above the heading (e.g.
            # `<!-- index-def: … -->` on the line before `## …`), `first` is the peeled marker and its `#`
            # run is 0 — so the level must come from the surviving heading text.
            head = remaining.lstrip()
            b.heading_level = len(head) - len(head.lstrip("#"))
        else:  # prose — the only place a [ref:] introduces a float
            b.refs = _find_refs(remaining, slug, idx)
        blocks.append(b)

    return Chapter(slug=slug, part=rec["part"],
                   title=rec.get("chapter_title") or rec.get("part_title", ""), blocks=blocks)


def parse_book(include_appendices: bool = False) -> Document:
    """Parse the main-narrative chapters (front / parts 1–5 / back) into the typed IR. Appendices are
    reference entries with their own float conventions; opt in with `include_appendices=True`."""
    metrics = bb._load_metrics()
    chapters = bb._discover_chapters(metrics)
    if include_appendices:
        chapters = chapters + bb.build_appendix_chapters(next_part=max(c["part"] for c in chapters) + 1)
    return Document([_parse_chapter(c) for c in chapters])
