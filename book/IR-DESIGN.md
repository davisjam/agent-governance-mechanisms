# The book IR — design and migration plan

## Why

`build_book_html.py` parses the book **several times over** — float numbering, concept-tag harvest,
glossary, the notation-leak gate, and every structural check in `tests/book.py` — each pass with its own
regexes, each able to drift from the others. That is the classic pre-IR smell: **N walkers, each
re-deriving structure.** `book/book_ir.py` is the one typed model those walks share. The book is ~50K
words; the whole IR fits in memory on a bare CI runner.

The move is the book's own thesis turned inward: a **canonical walker over a typed model** instead of
scattered bespoke parses.

## Foundation — a directive registry on our *own* stdlib parser

The genre-correct engine for pluggable markdown is a token-stream parser + a standard directive syntax
(`markdown-it-py` / MyST `:::name` blocks, `{role}` inlines). We do **not** adopt it, for two reasons:

1. **Clone-and-run is load-bearing.** `catalog.py` is stdlib-only so `python3 catalog.py` builds the book
   on a bare runner with nothing installed. A third-party engine means *vendoring* a markdown engine — a
   posture change, not `pip install`.
2. **Our HTML-comment notation degrades gracefully.** `<!-- figure: … -->` is invisible in a plain MD
   viewer (GitHub renders the source cleanly); `:::figure` renders as literal junk.

So we adopt the **schema** of a pluggable engine — a registry of `directive name → typed node` — while
keeping our own runtime and notation. This is the "adopt the schema, skip the runtime" move. Adding
notation is **one registry row** (`_DIRECTIVES` / `_EMITS` / `_ARMS` in `book_ir.py`, plus the render-side
twin `MARKER_KEYWORDS` in `build_book_html.py` that the notation-leak gate reads).

It is on the path to a real engine, not off it — see "If clone-and-run is ever relaxed" below.

## The model (`book/book_ir.py`)

```
Document
 └─ Chapter(slug, part, title, blocks[])
     └─ Block(kind, raw, index, label?, caption?, heading_level, directive?, refs[])
         refs: Ref(key, chapter_slug, block_index)
```

`BlockKind` ∈ {heading, para, list, table, figure, mermaid, code, code-inset, blockquote, eq, directive,
other}. The three **float** kinds (`figure`, `table`, `mermaid`) are what the build numbers "Figure N." /
"Table N." and what an author cross-references.

**Tokenizer SSOT.** Block splitting, chapter discovery, and the marker regexes are imported from
`build_book_html` — there is exactly ONE tokenizer; the IR is a typed layer over it, never a copy. This is
what makes the IR safe (no second-parser drift, the failure mode that sinks a "read-only analysis parser").

**A-ready rule (do not break).** Every `Block` carries its **raw source slice**, and the block taxonomy
mirrors the renderer's own block handling 1:1. So the IR is never lossy, and the renderer can later emit
*from* it without re-adding detail.

## What it enables (walks, not regexes)

- **`book-float-ref`** (live, `tests/book.py` rule 12) — every float is introduced by a `[ref:]` before it;
  dangling `[ref:]` is a finding. *First consumer of the IR.*
- Float-without-caption, heading-order, mid-block-marker placement, the terseness "float-without-cue"
  heuristic, the cross-reference graph, concept-tag coverage, asset existence — each becomes a short walk.

## Migration to A (renderer emits from the IR)

C (this doc) is a deliberate, low-risk **on-ramp** to A, not a detour. Three behavior-preserving moves:

1. **C (done):** shared tokenizer; typed read-only IR; lints walk it; the renderer still emits HTML from
   the shared token stream.
2. **Enrich (additive):** hang the render-relevant payload on the IR nodes (caption HTML, asset path, then
   inline spans). Each addition is behavior-preserving and changes nothing about the analyses.
3. **A:** flip the renderer's emit loop from "walk raw blocks" to "walk IR blocks," then delete its private
   block-walk. One parser now feeds both rendering and analysis.

**Safety net:** the built HTML is deterministic, so a golden-snapshot test ("build is byte-identical across
this refactor") makes step 3 a refactor-with-a-net rather than a leap. The two rules that keep C→A clean
are already in force: **one shared tokenizer** (no drift) and **raw slice on every node** (never lossy).

## If clone-and-run is ever relaxed

A `markdown-it-py` token stream is *also* just typed nodes, so "vendor the engine, turn each `_DIRECTIVES`
row into a markdown-it plugin, map its tokens onto `Block`" is a clean **further** step: C → A → real
engine. Building the registry now is the first stone on that path. The cost to weigh at that point: a
vendored engine + its transitive deps, a full render-pass rewrite (mermaid→SVG, `{{token}}`, anchors, and
the float/gloss passes all become plugins), and the loss of graceful degradation in a plain MD viewer.

## Adding a directive (today, Foundation 1)

1. Add the render behavior in `build_book_html.py` (`_consume_leading_marker` / the block loop) and the
   keyword to `MARKER_KEYWORDS` (the notation-leak gate reads it).
2. Add the classification to `book_ir.py` (`_ARMS` / `_EMITS`, or a `DIRECTIVE` fall-through).
3. Document it in `AGENTS.md` §3 and, if it carries a rule, add a `tests/book.py` walk over the IR.
