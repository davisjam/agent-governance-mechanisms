"""IR → Typst emitter — the print-native projection of the book (the PRODUCTION PDF path).

WHAT THIS IS.  A print-native projection of the book's typed IR (`book/book_ir.py`): it walks the same
`Document → Chapter → Block` model the HTML build walks and emits **Typst** markup instead of HTML. The
Typst binary then compiles that to PDF. This is the "one model, many projections" the book preaches —
HTML (the web book) and Typst (the PDF) are two emitters over one IR, neither derived from the other.

WHY (the decision this settled).  The PDF used to be HTML → Paged.js (headless browser) → PDF, which
inherited browser artifacts, bloat, imperfect print typography, and a headless-browser dependency.
`IR → Typst → PDF` is the print-native path now in production (recorded in `book/IR-DESIGN.md`
§"PDF generation"): the Typst binary lays out the whole book in ~2 s and emits a small, tagged PDF with no
browser in the loop. The whole-book render is driven by `build_book_html.build_pdf` (the `--pdf` flag).

DISCIPLINE — OUTPUT ONLY.  This module is stdlib (it emits text) and READS `build_book_html` / `book_ir`
for the tokenizer, the IR, mermaid-SVG rendering, figure-asset resolution, and metrics — it does NOT modify
either. The web `build()` path is untouched: this emitter is the SECOND projection, invoked only by `--pdf`.

ANNOTATION MAPPING (the crux).  Each of our HTML-comment directives maps to a Typst native construct:

    our directive                       Typst construct
    ----------------------------------  --------------------------------------------------
    <!-- label: k --> + [ref:k]         #figure(...) <k>   +   @k   (a linked "Figure N")
    <!-- figure: path | cap -->         #figure(image(path), caption: [...])
    standalone ```mermaid ```           #figure(image(<cached SVG>), caption: [...])
    pipe table                          #figure(table(...), caption: [...])   (numbered "Table N")
    ``` fenced code ```                 ```lang ... ``` raw block
    heading / list / ordered / quote    =/==, list.item, enum.item, #quote
    <!-- eq: … -->                      $ … $  (block equation)
    {{token}} metric                    value substitution (data/metrics.json)  — done in the IR text
    <!-- index-def: slug -->            #metadata((slug, kind: "index-def")) + typst query
    <!-- point: … -->  (planned)        #metadata((slug, kind: "point", text)) + typst query

The `#metadata` + `typst query` pair is Typst's purpose-built mechanism for embedded, tool-queryable data —
so mapping our two model-annotation directives to it proves Typst can hold the whole model, queryable by an
external tool exactly as our HTML anchors are.
"""
from __future__ import annotations

import hashlib
import html as _htmlmod
import pathlib
import re

import build_book_html as bb
import book_ir as ir
import design_tokens as _dtokens  # bb already put book-models on sys.path — the design-token projector

HERE = pathlib.Path(__file__).resolve().parent

# The Typst projection of the design-token SSOT (Umber Monograph): a `#let dt = (…)` preamble prepended
# to every compiled document so the header + box renderers look up dt.ink / dt.box-thesis-rule / dt.fs-*
# instead of literal hexes and grey values. One typed model, three surfaces (site / web book / PDF).
_TOKENS = _dtokens.load()
_TYPST_PREAMBLE = _dtokens.typst_preamble(_TOKENS)
_DEF_SLUGS = frozenset({"model", "agent", "engineering", "software-engineering"})
_MERMAID_CACHE = HERE / ".mermaid-svg-cache"
_MERMAID_CONFIG = HERE / "assets" / "mermaid-config.json"


# ── Inline markdown → Typst inline ─────────────────────────────────────────────────────────────────
# The HTML renderer's `inline()` handles: `code`, **bold**, *italic*, [+intra-word+], [text](href),
# [[abbr|text]] abstraction cites, [ref:key] cross-refs. We mirror it, emitting Typst inline markup.
# `[ref:key]` is handled specially — it becomes a Typst `@key` reference, the whole point of the mapping.

# Characters Typst treats as markup that must be escaped in body text.
_TYPST_ESCAPE = {
    "\\": "\\\\", "#": "\\#", "$": "\\$", "*": "\\*", "_": "\\_", "`": "\\`",
    "@": "\\@", "<": "\\<", ">": "\\>", "[": "\\[", "]": "\\]", "~": "\\~",
}


def _esc(text: str) -> str:
    """Escape Typst markup metacharacters in a run of plain body text."""
    return "".join(_TYPST_ESCAPE.get(ch, ch) for ch in text)


_XREF_RE = bb._XREF_RE                                   # SSOT: the same [ref:key] regex the HTML build uses
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])")
_INTRAWORD_RE = re.compile(r"\[\+(.+?)\+\]")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_ABBR_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")


def inline_typst(s: str) -> str:
    """Convert one run of the book's inline-markdown subset to Typst inline markup. Mirrors the branch order
    of `build_book_html.inline` (code spans stashed first so no bold/italic runs inside them), but the
    `[ref:key]` token becomes a Typst `@key` reference rather than an <a>. Everything else that is plain body
    text is escaped so a stray `#`/`*`/`@`/`_` in prose does not trigger Typst markup."""
    return _inline(s, [])


def _inline(s: str, stash: list[str]) -> str:
    """The worker for `inline_typst`. A SINGLE `stash` list is threaded through every recursion (bold/italic
    whose content itself holds a stashed code-span or link), so a placeholder index is globally unique and a
    nested run never restores against a shorter inner stash — the full-corpus bug a per-call stash caused."""
    def _hold(frag: str) -> str:
        stash.append(frag)
        return f"\x00S{len(stash) - 1}\x00"

    # 1. Cross-references FIRST — `[ref:key]` → a Typst `@key`. Held so later escaping leaves the `@` alone.
    s = _XREF_RE.sub(lambda m: _hold(f"@{m.group(1)}"), s)
    # 2. Intra-word emphasis `[+X+]` → emphasised run.
    s = _INTRAWORD_RE.sub(lambda m: _hold(f"#emph[{_esc(m.group(1))}]"), s)
    # 3. Code spans `` `x` `` → raw inline; content is literal, no further passes run inside it.
    s = _CODE_SPAN_RE.sub(lambda m: _hold(f"#raw({_typst_str(m.group(1))})"), s)
    # 4. Abstraction cites `[[slug|text]]` → a link into the rendered abstractions glossary (one dir up).
    def _abbr(m: "re.Match[str]") -> str:
        slug = m.group(1).strip()
        text = (m.group(2) or slug).strip()
        return _hold(f'#link("../ABSTRACTIONS.html#{slug}")[{_esc(text)}]')
    s = _ABBR_RE.sub(_abbr, s)
    # 5. Markdown links `[text](href)` → `#link(href)[text]`.
    s = _LINK_RE.sub(lambda m: _hold(f"#link({_typst_str(m.group(2))})[{_esc(m.group(1))}]"), s)
    # 6. Bold / italic → strong / emph. Non-greedy bold so an inner *italic* survives. The recursion threads
    #    the SAME stash so an already-held placeholder inside the span is never re-restored out of range.
    s = _BOLD_RE.sub(lambda m: _hold(f"#strong[{_inline(m.group(1), stash)}]"), s)
    s = _ITALIC_RE.sub(lambda m: _hold(f"#emph[{_inline(m.group(1), stash)}]"), s)
    # 7. Escape everything still plain, then restore the held Typst fragments (repeatedly — a held fragment
    #    may itself contain a placeholder from a later-numbered hold, e.g. a link nested in bold).
    s = _esc(s)
    while "\x00S" in s:
        s = re.sub(r"\x00S(\d+)\x00", lambda m: stash[int(m.group(1))], s)
    return s


def _typst_str(s: str) -> str:
    """A Typst string literal for `s` (double-quoted, backslash/quote-escaped)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ── Asset resolution — mermaid SVG cache + figure directives ───────────────────────────────────────

def _mermaid_svg_path(source: str) -> pathlib.Path:
    """The on-disk cached SVG for a mermaid fence body — the SAME content-hash key `render_mermaid_svg`
    uses, so we reuse its cache instead of re-rendering. If the cache miss, we drive the HTML renderer's
    `render_mermaid_svg` (which renders + caches) then return the path."""
    src = source.strip()
    key = hashlib.sha256(
        (src + "\x00" + _MERMAID_CONFIG.read_text(encoding="utf-8") + "\x00idscheme-v1").encode("utf-8")
    ).hexdigest()
    cached = _MERMAID_CACHE / f"{key}.svg"
    if not cached.exists():
        bb.render_mermaid_svg(src)                       # renders + writes the cache file (fails loud if mmdc absent)
    return cached


def _root_rel(path: pathlib.Path, root: pathlib.Path) -> str:
    """A Typst root-absolute image path (`/…`) for `path` relative to the compilation `root`. Typst reads a
    leading-`/` image path relative to `--root`; a plain relative path is relative to the .typ file."""
    return "/" + str(path.resolve().relative_to(root.resolve()))


def _fence_body(block: str) -> tuple[str, str]:
    """Split a ```lang … ``` fence into (lang, inner)."""
    lines = block.splitlines()
    lang = lines[0].strip()[3:].strip()
    inner = lines[1:]
    if inner and inner[-1].strip() == "```":
        inner = inner[:-1]
    return lang, "\n".join(inner)


# ── Block-kind renderers — a `render_typst(block)` sibling to `Block.render_html()` ─────────────────

def _render_heading(raw: str) -> str:
    """`#`..`####` → Typst `=`..`====`. A trailing `{#slug}` id-anchor and an `## [role: X]` kicker are
    folded into the heading text (the kicker as an emphasised lead)."""
    stripped = raw.strip()
    level = len(stripped) - len(stripped.lstrip("#"))
    text = stripped[level:].strip()
    text, _anchor = bb._heading_anchor(text)
    kicker = ""
    if level == 2:
        kick, text = bb._role_kicker(text)
        if kick:
            m = re.search(r">([^<]+)</span>", kick)
            if m:
                kicker = f"#emph[{_esc(m.group(1).strip())}] "
    return "=" * level + " " + kicker + inline_typst(text)


def _render_paragraph(raw: str) -> str:
    # Strip any stray HTML comment (an authoring TODO/note whose keyword is not in the notation vocabulary).
    # The IR peels every RECOGNIZED marker into a DIRECTIVE (rendered as nothing); a comment that reaches a
    # PARA block is stray and would otherwise print as VISIBLE text in the PDF (the leak this closes). Removed
    # here, mirroring the web renderer's block-level strip; both share `build_book_html._STRAY_COMMENT_RE`. A
    # block that was nothing but a stray comment renders empty and is dropped by `render_chapter`'s `if frag`.
    raw = bb._STRAY_COMMENT_RE.sub("", raw)
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return ""
    return inline_typst(" ".join(lines))


def _render_unordered_list(raw: str) -> str:
    items: list[str] = []
    for ln in raw.splitlines():
        s = ln.strip()
        if s.startswith("- "):
            items.append(s[2:])
        elif items:
            items[-1] += " " + s
    return "\n".join(f"- {inline_typst(t)}" for t in items)


def _render_ordered_list(raw: str) -> str:
    items: list[str] = []
    for ln in raw.splitlines():
        s = ln.strip()
        if re.match(r"^\d+\.\s", s):
            items.append(re.sub(r"^\d+\.\s+", "", s))
        elif items:
            items[-1] += " " + s
    return "\n".join(f"+ {inline_typst(t)}" for t in items)


def _render_code(raw: str) -> str:
    """A non-mermaid fence → a Typst raw block. Language-tagged so Typst can highlight (unknown langs are
    fine — Typst falls back to plain). We emit an explicit `#raw(..., block: true)` so arbitrary body text
    (which may contain ``` sequences) never breaks the fence."""
    lang, inner = _fence_body(raw)
    lang_arg = f", lang: {_typst_str(lang)}" if lang else ""
    return f"#raw({_typst_str(inner)}, block: true{lang_arg})"


# A thesis blockquote leads with a bold `The <Name> Thesis.` label (`> **The Modeling Thesis.** …`). The
# HTML book lifts these into a coloured `thesis-box` panel; the print projection mirrors that by boxing them
# instead of typesetting them as a plain quote. Matched on the raw markdown lead (the HTML twin matches the
# rendered `<p><strong>…Thesis.</strong>`); the two stay in step by construction of the same authored shape.
_THESIS_LEAD_RE = re.compile(r"^\*\*The\b.*?\bThesis\.\*\*", re.S)

def _render_blockquote(raw: str, is_def: bool = False) -> str:
    """A `>`-prefixed blockquote → a Typst block. A thesis blockquote (`> **The … Thesis.** …`) becomes a
    GREEN boxed callout; a core-term definition blockquote (armed by a preceding index-def, `is_def`) a BLUE
    def-box; any other blockquote stays a plain `#quote(block: true)[…]`. All three mirror the web book's
    boxes and draw their colours from the shared `dt` tokens. Inner content is itself markdown; we recurse
    the whole emitter over it so an inner heading/list/mermaid renders."""
    inner_md = "\n".join(bb._strip_blockquote_prefix(ln) for ln in raw.splitlines())
    inner = _render_markdown_body(inner_md, _EmitCtx.inert())
    stripped = inner_md.strip()
    if _THESIS_LEAD_RE.match(stripped):
        return (f'#block(fill: dt.box-thesis-fill, stroke: (left: dt.border-box-rule + dt.box-thesis-rule), '
                f"inset: 12pt, radius: 4pt, width: 100%)[\n{_indent(inner)}\n]")
    if is_def:
        return (f'#block(fill: dt.box-def-fill, stroke: (left: dt.border-box-rule + dt.box-def-rule), '
                f"inset: 12pt, radius: 4pt, width: 100%)[\n{_indent(inner)}\n]")
    if stripped.startswith("#"):
        # A titled concept-inset primer (`> ### Inset N — Title`) → a LAVENDER box, mirroring the web book's
        # `concept-inset` (an inner heading heads the primer). The heading renders bold inside the panel.
        return (f'#block(fill: dt.box-inset-fill, stroke: (left: dt.border-box-rule + dt.box-inset-rule), '
                f"inset: 12pt, radius: 4pt, width: 100%)[\n{_indent(inner)}\n]")
    return f"#quote(block: true)[\n{_indent(inner)}\n]"


def _render_inset(raw: str) -> str:
    """A titled inset (`<!-- inset: T -->` glued to a fence) → a bordered block with the title as a bold
    lead and the fence body below (mermaid → the cached SVG image, else a raw code block)."""
    lines = raw.strip().splitlines()
    title = bb._INSET_RE.match(lines[0].strip()).group("title")
    lang, inner = _fence_body("\n".join(lines[1:]))
    if lang.lower() == "mermaid":
        p = _mermaid_svg_path(inner)
        body = f'#image("{_root_rel(p, _EmitCtx.root)}", width: 90%)'
    else:
        body = f"#raw({_typst_str(inner)}, block: true)"
    return (f"#block(fill: dt.box-inset-fill, inset: 10pt, "
            f"stroke: (left: dt.border-box-rule + dt.box-inset-rule), radius: 3pt, width: 100%)[\n"
            f"  #text(fill: dt.box-inset-rule)[#strong[{inline_typst(title)}]]\n\n  {body}\n]")


def _render_table(block: Block_t) -> str:
    """A pipe table → a Typst `#figure(table(...))` so it is NUMBERED "Table N" and cross-referenceable.
    A `<!-- table: caption -->` arms the caption; a `<!-- label: k -->` arms the `<k>` label for `@k`."""
    lines = block.raw.splitlines()
    header = bb._split_table_row(lines[0])
    ncol = len(header)
    body_rows = [bb._split_table_row(ln) for ln in lines[2:] if ln.strip()]
    aligns = bb._col_alignments(lines[1]) if len(lines) > 1 else []
    align_arg = ""
    if any(a for a in aligns):                           # a `---:` column right-aligns (numeric), else left
        cols = ", ".join("right" if (i < len(aligns) and aligns[i]) else "left" for i in range(ncol))
        align_arg = f"\n    align: ({cols}),"
    # Booktabs rules: heavy top, light under-header, heavy bottom — the three-rule Tufte style.
    cells = ["table.hline(stroke: 1pt)",
             "table.header(" + ", ".join(f"[{inline_typst(c)}]" for c in header) + ")",
             "table.hline(stroke: 0.5pt)"]
    for row in body_rows:
        # pad/truncate to header width so Typst's fixed column count never desyncs
        row = (row + [""] * ncol)[:ncol]
        cells.append(", ".join(f"[{inline_typst(c)}]" for c in row))
    cells.append("table.hline(stroke: 1pt)")
    tbl = f"table(\n    columns: {ncol},{align_arg}\n    " + ",\n    ".join(cells) + "\n  )"
    caption = _caption_block(block.caption)
    label = f" <{block.label}>" if block.label else ""
    return f"#figure(\n  {tbl},\n  kind: table,{caption}\n){label}"


def _render_figure(block: Block_t) -> str:
    """A `<!-- figure: path | caption -->` → `#figure(image(path), caption: […])`, numbered + labelled."""
    spec = block.raw[len("<!--"):-len("-->")].strip()[len("figure:"):].strip()
    rel = spec.split("|", 1)[0].strip()
    asset = HERE / rel
    if not asset.is_file():
        raise SystemExit(f"figure directive: asset not found: {asset}")
    caption = _caption_block(block.caption)
    label = f" <{block.label}>" if block.label else ""
    img = f'image("{_root_rel(asset, _EmitCtx.root)}", width: 85%)'
    return f"#figure(\n  {img},{caption}\n){label}"


def _render_mermaid(block: Block_t, caption_md: str | None) -> str:
    """A standalone ```mermaid fence → `#figure(image(<cached SVG>), caption)`, numbered + labelled. The SVG
    is the one the HTML build already rendered/cached — we include it, we do not re-render."""
    _lang, inner = _fence_body(block.raw)
    p = _mermaid_svg_path(inner)
    caption = _caption_block(caption_md)
    label = f" <{block.label}>" if block.label else ""
    img = f'image("{_root_rel(p, _EmitCtx.root)}", width: 78%)'
    return f"#figure(\n  {img},{caption}\n){label}"


def _render_eq(raw: str) -> str:
    """An `<!-- eq: … -->` display equation → a Typst block math `$ … $`. The body is math-ish plain text
    (our equations are simple: `P(wrong) = 1 − (1 − p)ⁿ`); we pass it through as Typst math, mapping a few
    unicode operators. Awkward by design — see the mapping report; a real migration would author math in
    Typst's own math language."""
    body = raw[len("<!--"):-len("-->")].strip()[len("eq:"):].strip()
    return f"$ {_math_ish(body)} $"


def _math_ish(s: str) -> str:
    """Best-effort map of our simple unicode-equation prose into Typst math atoms. Multi-letter alphabetic
    runs (e.g. `wrong` in `P(wrong)`) are quoted so Typst renders them as upright text rather than reading
    each as an undefined variable — the failure the whole-corpus compile surfaced. This is a best-effort
    bridge; a real migration would author equations in Typst's own math language (see the mapping report)."""
    repl = {"−": "-", "×": " times ", "·": " dot ", "≤": " <= ", "≥": " >= ", "≠": " != ", "ⁿ": "^n"}
    for k, v in repl.items():
        s = s.replace(k, v)
    # Quote multi-letter alphabetic words (2+ letters) as upright text; leave single letters as variables
    # (the usual math convention: `p`, `n`, `P` stay italic variables, `wrong` becomes text).
    return re.sub(r"[A-Za-z]{2,}", lambda m: f'"{m.group(0)}"', s)


def _caption_block(caption_md: str | None) -> str:
    """The `caption: [...]` argument for a `#figure`, or "" when there is none. Strips a trailing
    `[short: …]` marker (the list-of-floats short form has no Typst analogue in this spike)."""
    if not caption_md:
        return ""
    display, _short = bb._split_caption_md(" ".join(caption_md.split()))
    return f"\n  caption: [{inline_typst(display)}],"


# ── Metadata (index-def / point) → #metadata + query ───────────────────────────────────────────────

def _render_index_metadata(slug: str, kind: str, text: str | None = None) -> str:
    """A curated-index / point annotation → a queryable `#metadata((...))` node with a stable label. This is
    the Typst-native analogue of our HTML anchor: `typst query` (or `typst eval query(metadata)`) extracts
    every one, so an external tool reads the model annotations exactly as it reads our HTML index anchors."""
    fields = f'slug: "{slug}", kind: "{kind}"'
    if text is not None:
        fields += f", text: {_typst_str(text)}"
    return f"#metadata(({fields})) <meta-{kind}-{slug}>"


# ── The emit context + the driving walk ────────────────────────────────────────────────────────────

Block_t = ir.Block


class _EmitCtx:
    """Carries the compilation root (for image paths) and the arming state the walk threads across blocks
    (pending index-def anchors → #metadata; the mermaid caption-fold). A tiny mutable holder — the HTML
    renderer keeps the same arming state in `md_to_html`'s closure; we make it explicit."""
    root: pathlib.Path = HERE.parent           # class-level default so the pure `_render_*` helpers can read it

    def __init__(self, root: pathlib.Path):
        _EmitCtx.root = root
        self.root = root
        self.metadata_emitted = 0
        self.pending_def: list[str] = []   # a core-term index-def armed for the next block (→ blue def-box)

    @classmethod
    def inert(cls) -> "_EmitCtx":
        """A context for a recursive sub-render (blockquote inner) that reuses the current root."""
        c = cls.__new__(cls)
        c.root = cls.root
        c.metadata_emitted = 0
        c.pending_def = []
        return c


def _indent(text: str, n: int = 2) -> str:
    pad = " " * n
    return "\n".join(pad + ln if ln else ln for ln in text.split("\n"))


# The whole notation vocabulary the peel step consumes off a block head (mirrors the IR's `_parse_chapter`
# and the renderer's `_consume_leading_marker`). We recognise index-def/index-example (→ #metadata),
# point (planned → #metadata), and the display/arming directives handled by the IR parser already.
_INDEX_DEF_RE = bb.INDEX_DEF_RE
_INDEX_EXAMPLE_RE = bb.INDEX_EXAMPLE_RE
_POINT_RE = re.compile(r"^<!--\s*point:\s*(?P<slug>[a-z0-9-]+)\s*\|\s*(?P<text>.+?)\s*-->$")


def render_typst(block: Block_t, caption_md: str | None = None, is_def: bool = False) -> str:
    """Render ONE IR block to Typst markup — the sibling to `Block.render_html()`, reusing the SAME
    `book_ir.BlockKind` taxonomy and `classify_render_block` classification (the blocks arrive already
    classified from the IR parse). `caption_md` is the folded mermaid caption when the driving walk detects a
    following italic paragraph (the HTML renderer's mermaid caption-fold)."""
    k = block.kind
    K = ir.BlockKind
    if k is K.HEADING:
        return _render_heading(block.raw)
    if k is K.PARA:
        return _render_paragraph(block.raw)
    if k is K.LIST:
        return _render_unordered_list(block.raw)
    if k is K.ORDERED_LIST:
        return _render_ordered_list(block.raw)
    if k is K.CODE:
        return _render_code(block.raw)
    if k is K.CODE_INSET:
        return _render_inset(block.raw)
    if k is K.BLOCKQUOTE:
        return _render_blockquote(block.raw, is_def=is_def)
    if k is K.TABLE:
        return _render_table(block)
    if k is K.FIGURE:
        return _render_figure(block)
    if k is K.MERMAID:
        return _render_mermaid(block, caption_md)
    if k is K.EQ:
        return _render_eq(block.raw)
    if k in (K.DIRECTIVE, K.OTHER):
        return ""                                        # inert markers / catalogue iframe — no print output
    return _render_paragraph(block.raw)                  # defensive fall-through


def _render_markdown_body(md: str, ctx: _EmitCtx) -> str:
    """Render a raw markdown body (used for the blockquote recursion) by re-parsing its blocks through the
    IR's classifier and emitting each. Kept parallel to the chapter walk so nested content renders the same."""
    out: list[str] = []
    for raw in bb._split_blocks(md):
        raw = raw.strip("\n")
        if not raw.strip():
            continue
        # peel lone index/point markers → metadata; ignore other leading markers in nested context
        lines = raw.splitlines()
        while lines:
            frag = _peel_metadata_marker(lines[0].strip(), ctx)
            if frag is None:
                break
            if frag:
                out.append(frag)
            lines = lines[1:]
        rem = "\n".join(lines).strip("\n")
        if not rem.strip():
            continue
        kind = ir.classify_render_block(rem)
        out.append(render_typst(ir.Block(kind, rem, 0)))
    return "\n\n".join(x for x in out if x)


def _peel_metadata_marker(line: str, ctx: _EmitCtx) -> "str | None":
    """If `line` is an index-def / index-example / point marker, return its `#metadata(...)` emission (and
    count it); if it is any OTHER lone notation marker the IR already consumed, return "" (drop it). Return
    None when it is not a marker at all, so the caller stops peeling."""
    s = line.strip()
    md = _INDEX_DEF_RE.match(s)
    if md:
        ctx.metadata_emitted += 1
        if md.group(1) in _DEF_SLUGS:
            ctx.pending_def.append(md.group(1))   # arm the blue def-box for the term's defining blockquote
        return _render_index_metadata(md.group(1), "index-def")
    me = _INDEX_EXAMPLE_RE.match(s)
    if me:
        ctx.metadata_emitted += 1
        return _render_index_metadata(me.group(1), "index-example")
    mp = _POINT_RE.match(s)
    if mp:
        ctx.metadata_emitted += 1
        return _render_index_metadata(mp.group("slug"), "point", mp.group("text"))
    if ir._MARKER_LINE.match(s):
        return ""                                        # a consumed notation marker with no print output
    return None


def render_chapter(chapter: ir.Chapter, ctx: _EmitCtx) -> str:
    """Walk one IR chapter → its Typst body. The IR already parsed labels/captions onto floats and classified
    every block; here we (a) peel index-def/point markers off the RAW source into #metadata (the IR records
    them as DIRECTIVE, so we re-read the raw slice for the slug), (b) fold a mermaid's following italic
    caption, and (c) emit each block."""
    out: list[str] = [f"= {inline_typst(chapter.title)}", ""]
    blocks = chapter.blocks
    skip: set[int] = set()
    _title_norm = chapter.title.strip().lower()
    for i, b in enumerate(blocks):
        if i in skip:
            continue
        # Suppress a body-leading H1 that duplicates the chapter title. `parse_chapter` drops the leading
        # `# Title` for `body_md`, but a marker comment glued above it (a `<!-- noqa -->`) defeats that drop,
        # so the H1 survives into the IR. In a single-flow print doc that duplicates the chapter title we
        # already emit as the header; the HTML page carries it twice (header + body) but the print book wants
        # one. Skip only the FIRST heading, only when it matches the title, before any prose has emitted.
        if (b.kind is ir.BlockKind.HEADING and len(out) <= 2
                and b.raw.strip().lstrip("#").strip().lower() == _title_norm):
            continue
        # DIRECTIVE blocks carry index-def / index-example / point markers → #metadata.
        if b.kind is ir.BlockKind.DIRECTIVE:
            frag = _peel_metadata_marker(b.raw.strip(), ctx)
            if frag:
                out.append(frag)
            continue
        caption_md = None
        if b.kind is ir.BlockKind.MERMAID and i + 1 < len(blocks):
            nb = blocks[i + 1]
            s = nb.raw.strip()
            if (nb.kind is ir.BlockKind.PARA and s.startswith("*") and not s.startswith("**")
                    and s.endswith("*") and "```" not in s):
                caption_md = s.strip("*").strip()
                skip.add(i + 1)
        # A core-term index-def (a DIRECTIVE handled above) arms the blue def-box for the block it heads —
        # this content block. Capture and clear so it applies to exactly the next content block.
        is_def = bool(ctx.pending_def)
        ctx.pending_def.clear()
        frag = render_typst(b, caption_md, is_def=is_def)
        if frag:
            out.append(frag)
    # CHAPTER-RELATIVE float numbering (mirrors the web `_number_floats` scheme): figures/tables read
    # "<part>.<chapter>-N" and N resets to 1 per chapter. The chapter's `<part>.<chapter>` id is baked as
    # a literal into a per-chapter `#set figure(numbering: …)` closure (no state/context coupling — set
    # rules are location-scoped, so @refs and the lists of figures/tables resolve each float's number at
    # the float's own position). The image/table counters reset at the chapter boundary so the first float
    # is N=1. Image and table sequences are independent, matching the web's separate fig_n/tbl_n.
    chap_id = f"{chapter.part}.{chapter.chapter}"
    num_setup = (
        f"#set figure(numbering: (n) => [{chap_id}-#n])\n"
        "#counter(figure.where(kind: image)).update(0)\n"
        "#counter(figure.where(kind: table)).update(0)\n"
    )
    return num_setup + "\n" + "\n\n".join(out)


# ── Preamble + document assembly ───────────────────────────────────────────────────────────────────

_PREAMBLE = _TYPST_PREAMBLE + """\
// GENERATED by book/book_typst.py — the IR→Typst emitter (the production PDF path). Do not hand-edit;
// regenerate via `python3 book/build_book_html.py --pdf` (whole book) or
//   python3 book/book_typst.py <chapter-slug> [<slug> …]   (a subset).
// The compiled PDF and the emitted .typ live under book/_typst/ (gitignored — created, never committed).
// Type/colour/surface come from the design-token `dt` preamble above. Body stays at a print-native 11pt
// (the token body step is screen-sized; print density is protected here) while the faces + palette follow
// the tokens: Fraunces display headings, a quiet body face, umber accent, and the semantic-box anchors.
#set document(title: "Model-Based Agentic Software Engineering")
#set page(paper: "us-letter", margin: (x: 1.1in, y: 1in), numbering: "1", fill: dt.paper)
#set text(font: dt.font-body, size: 11pt, lang: "en", fill: dt.ink)
#set par(justify: true, leading: 0.62em, first-line-indent: 0pt, spacing: 0.9em)
#set heading(numbering: none)
#show heading: set text(font: dt.font-display, weight: "bold")
#show heading.where(level: 1): set text(size: 1.5em)
#show heading.where(level: 2): set text(size: 1.2em)
#show heading: set block(above: 1.4em, below: 0.7em)
#set figure(gap: 0.6em)
#show figure.caption: set text(size: 0.9em, style: "italic", fill: dt.muted)
#show figure.where(kind: table): set figure.caption(position: top)
// Booktabs table style (matches the HTML book's Tufte/booktabs tables): a heavy top rule, a light rule
// under the header, a heavy bottom rule — NO vertical rules or cell boxes. Whitespace separates columns.
#set table(stroke: none, inset: (x: 8pt, y: 5pt))
#show table.cell.where(y: 0): set text(weight: "bold")
#show raw.where(block: true): set block(fill: dt.code-bg, inset: 8pt, radius: 3pt, width: 100%)
#show raw: set text(font: dt.font-mono)
#set raw(tab-size: 2)
"""


def _cover_typst() -> str:
    """The cover page — the title-version cover art (`book/assets/cover.svg`), sized to the page. The art
    itself carries the title + author lockup (the same identity the web cover and the site read), so this
    page is the image, not a text setting. Its own page, no folio, but with a first-page footer carrying
    the copyright line and the book's last-modified date.

    The copyright is DERIVED from `author` + `copyright_years` (the manifest states the name once — the
    same derivation the web cover's COPYRIGHT line uses). The last-modified date is injected at compile
    time via `--input last_modified=…` (see `build_book_html.build_pdf`) and read here with `sys.inputs`,
    falling back to the manifest `last_updated` when the emitter runs standalone with no input."""
    m = bb._BOOK_MANIFEST
    copyright_txt = _esc(f'© {m["author"]}, {m["copyright_years"]}')
    default_mod = _esc(m.get("last_updated", ""))
    footer = (
        '#align(center)[#text(size: 8pt, fill: dt.muted)'
        f'[{copyright_txt} #h(0.5em) · #h(0.5em) Last modified #last_modified]]'
    )
    cover_svg = _root_rel(HERE / "assets" / "cover.svg", _EmitCtx.root)
    return (
        f'#let last_modified = sys.inputs.at("last_modified", default: "{default_mod}")\n'
        f"#page(numbering: none, footer: [{footer}])[\n"
        "  #align(center + horizon)[\n"
        f'    #image("{cover_svg}", width: 100%)\n'
        "  ]\n"
        "]"
    )


def _part_divider_typst(part: int, ch: ir.Chapter) -> "str | None":
    """A part-divider page before the first chapter of a numbered Part or an appendix Part. Front matter
    (0) and back matter (6) get no divider — they flow as chapters. Returns the Typst for the divider, or
    None when this part gets none. The part title matches the web book's `_PART_TITLES` for numbered parts;
    an appendix part reuses its own family name (e.g. "Appendix A — the pattern language")."""
    if part in (0, 6):
        return None
    part_titles = bb._PART_TITLES
    if part in part_titles and part <= 5:
        kicker, title = f"Part {part}", part_titles[part]
    else:
        # Appendix part: the chapter title carries the family (e.g. "Appendix A - 9. …" / "Appendix D — …").
        mm = re.match(r"\s*(Appendix\s+[A-Z])\b[\s—:-]*(.*)", ch.title)
        if mm:
            kicker, title = mm.group(1), (mm.group(2).split(".", 1)[-1].strip() if "." in mm.group(2) else mm.group(2).strip())
            title = title or kicker
        else:
            return None
    return (
        "#pagebreak(to: \"odd\")\n"
        "#block(breakable: false)[\n"
        f"  #v(2.4in)\n"
        f"  #text(size: 1.1em, fill: dt.muted)[{inline_typst(kicker)}]\n"
        "  #v(0.4em)\n"
        f"  #text(size: 2em, weight: \"bold\")[{inline_typst(title)}]\n"
        "  #v(0.5em) #line(length: 30%, stroke: 1pt + dt.rule)\n"
        "]"
    )


def emit_document(slugs: list[str], root: pathlib.Path | None = None, *, with_frontmatter: bool = False) -> str:
    """Emit a standalone Typst document for the named chapter slugs. When `with_frontmatter` is set (the
    whole-book production render), a title-page cover leads and a part-divider page precedes the first
    chapter of each numbered Part and each appendix Part — the same structure the web book carries, so the
    print edition does not diverge. `root` is the Typst compilation root the image paths resolve against
    (defaults to the repo dir, the parent of book/)."""
    root = root or HERE.parent
    ctx = _EmitCtx(root)
    doc = ir.parse_book(include_appendices=True)
    by_slug = {c.slug: c for c in doc.chapters}
    parts: list[str] = [_PREAMBLE]
    if with_frontmatter:
        parts.append(_cover_typst())
    seen_parts: set[int] = set()
    for n, slug in enumerate(slugs):
        if slug not in by_slug:
            raise SystemExit(f"unknown chapter slug: {slug} (have {sorted(by_slug)[:5]}…)")
        ch = by_slug[slug]
        if with_frontmatter and ch.part not in seen_parts:
            seen_parts.add(ch.part)
            divider = _part_divider_typst(ch.part, ch)
            if divider:
                parts.append(divider)
            elif n:
                parts.append("#pagebreak()")
        elif n:
            parts.append("#pagebreak()")
        parts.append(render_chapter(ch, ctx))
    return "\n\n".join(parts) + "\n"


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="IR→Typst spike emitter: emit Typst markup for book chapters.")
    ap.add_argument("slugs", nargs="+", help="chapter slug(s), e.g. 3.1-the-executable-zoo")
    ap.add_argument("--out", help="write to this .typ path (default: stdout)")
    args = ap.parse_args(argv)
    typ = emit_document(args.slugs)
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(typ, encoding="utf-8")
        print(f"wrote {p} ({len(typ)} bytes)")
    else:
        print(typ)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
