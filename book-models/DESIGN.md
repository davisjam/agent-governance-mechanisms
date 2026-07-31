# The book as a typed 4+1 model — design

**Dogfooding "everything is a model."** Part 3 of the book preaches that a system is best understood
through Kruchten's 4+1 views, each a **typed, drift-checked model the fleet reasons through, derived from
the source and never snapshotted**. This directory turns that lens on the book itself: it models the book
as a small set of typed view-models that reference symbols *inside* the markdown, each held equal to the
prose by a build-time drift check.

The move is the same one Part 3 teaches applied one level up. There, the models are derived from the
*product* code. Here, the models are derived from the *book* — the `book_ir` typed IR is our "code," and
each view is a `model-from-code` projection over it, reconciled on every build.

This doc names the full view set, specifies the markdown symbol scheme each view rides, and states the
drift check that keeps each honest. One view — the **outline view** — is implemented here as a working
proof of concept; the rest are specified for the author to ratify before the full build.

---

## 1. Why model the book at all — the failure it kills

A book of this size has the same failure MBSE was invented for: **structure that lives in the author's
head and drifts silently.** Concrete failures the models catch:

- **A cross-reference goes stale.** A `[ref:key]` or `[text](chapter.html)` points at a section that was
  renamed or retired; the link still renders, but lands nowhere useful. Nothing re-checks it against the
  current heading tree.
- **A reading path breaks.** The preface promises three routes through the book ("read straight through,"
  "do it Monday," "be convinced first"), each naming specific parts in order. A part gets renumbered and
  the promised route now mis-describes the book. No model ties the promise to the parts.
- **A concept loses its home.** The concept model (`book/data/concepts.json`) already catches this for the
  *conceptual* surface — but it has no sibling for the *structural* surface (the heading tree) or the
  *navigational* surface (the journeys).
- **A section loses its point.** A subsection's topic sentence — the one-sentence claim the section
  argues — is the unit an outline is built from. When a section is edited so its opening no longer states
  its point, an outline built by hand rots; an outline *derived* from the prose surfaces the gap.

Each failure is invisible from any single chapter. It shows only when you hold the whole structure at
once — which is exactly what a typed model is for.

The precedent is already in the repo: `book/data/concepts.json` is a typed model of the book's core
concepts, joined book↔site by slug, with `book_home` **derived** at check time from the `<!-- index-def:
slug -->` anchors (never stored, so it cannot drift) and four drift lints (L1–L4 in `tests/html.py`). The
view-models here extend that exact pattern to the book's structure and navigation.

---

## 2. The view set

The author named three views to start and invited more. Recommended set: **the three named views plus
two more** (a cross-reference graph and a thesis-weave model), for five total. Each is a typed model that
answers one quality question, built from named md symbols, held true by a drift check.

| # | View | Kruchten analogue | Quality question it answers | Status |
|---|------|-------------------|-----------------------------|--------|
| 1 | **Outline** | Development (how the source is organized) | *Is every section's structure and point accounted for — heading tree complete, each with a topic sentence?* | **PoC built here** |
| 2 | **Conceptual** | Logical (what the system is) | *Does every concept have a definition and a home, and do the chapter links and floats connect the concepts they claim to?* | Specified (partly exists as `concepts.json`) |
| 3 | **User-journeys** | Scenarios (+1, the paths that validate the rest) | *Does each promised reading path still traverse real parts in the promised order?* | Specified |
| 4 | **Cross-reference graph** | Process (what connects to what) | *Does every `[ref:]` / inter-chapter link / float reference resolve, and is the reference graph acyclic-where-it-should-be?* | Specified (recommended) |
| 5 | **Thesis-weave** | (a book-specific invariant view) | *Are the two theses (Modeling, Alignment) actually woven through the parts that claim to develop them?* | Specified (recommended) |

Below, each view gets its quality question, typed schema, and the md symbols it references.

### 2.1 Outline view (built)

- **Quality question.** Is the book's heading tree complete and coherent — every section down to
  sub-subsection level accounted for, in the right nesting order, each carrying a **topic sentence** that
  states its point?
- **Typed schema.**
  ```
  Outline
   └─ OutlineChapter(slug, part, title, sections[])
       └─ Section(id, level, heading_text, topic_sentence, id_source)
  ```
  - `id` — a **stable section id**: the explicit `{#slug}` anchor when present, else a slug derived from
    the heading text. `id_source` records which (`explicit` | `derived`) so the model shows how many
    sections still want a curated anchor.
  - `topic_sentence` — the first sentence of the first paragraph block that follows the heading (derived,
    not annotated — see §3).
  - `level` — 2–4 (H1 is the chapter title, rendered separately by the build).
- **Md symbols referenced.** `{#slug}` heading anchors (existing, 22 sites) for stable ids; heading text +
  the following paragraph (structural, no new symbol) for the topic sentence.
- **Invariants (checked by the drift check).**
  - *O1 — every heading is in the model.* The model's section set re-derived from the book equals the
    stored set. (`model-from-code` reconcile; a heading added/removed/renumbered without regenerating the
    model is a finding.)
  - *O2 — every section has a topic sentence.* A heading with no following paragraph is a finding
    (surfaces a section that opens on a float/list with no stated point).
  - *O3 — section ids are unique.* Two sections resolving to the same id collide the outline's join key.
  - *O4 — heading nesting is well-formed.* No jump from H2 to H4 without an intervening H3 (an outline hole).

### 2.2 Conceptual view (specified)

- **Quality question.** Does every core concept have a definition and a home, and do the inter-chapter
  links and the floats (figures/tables) actually connect the concepts they claim to?
- **Typed schema.**
  ```
  ConceptModel
   └─ Concept(slug, name, kind, book_home, site_home, status, defined_in, referenced_by[])
   └─ ChapterLink(from_chapter, to_chapter, anchor_text)      # [text](chapter.html) edges
   └─ Float(label, kind, chapter, caption, introduced_by_ref) # figure/table/mermaid, joined to its [ref:]
  ```
  `Concept` is the *existing* `book/data/concepts.json` shape (reuse it verbatim — this view formalizes it
  as one of the 4+1 and adds the link/float layers around it).
- **Md symbols referenced.** `<!-- index-def: slug -->` (126×, concept anchors), `<!-- index-example: slug
  -->` (12×), `<!-- label: key -->` (43×, float labels), `[ref:key]` cross-refs, `[text](chapter.html)`
  inter-chapter links. **All existing** — the conceptual view needs no new symbol; it composes symbols
  already in use.
- **Invariants.** Every concept's `book_home` resolves to a real `index-def` (already L1). Every float has
  a caption and is introduced by a `[ref:]` before it (already the `book-float-ref` gate). New: every
  concept referenced in prose (`[ref:]` to a concept anchor) resolves to a defined concept; the
  chapter-link graph has no dangling target.

### 2.3 User-journeys view (specified)

- **Quality question.** Does each "how to read this book" path still traverse real parts in the promised
  order? This is the direct analogue of the product's `user-journey-model` — an *actor* pursuing a *goal*
  through *ordered steps*, each step joined to the structural element it visits.
- **Typed schema.**
  ```
  JourneyModel
   └─ Journey(id, actor, goal, steps[])
       └─ Step(order, target_part_or_chapter, description)   # each step joins to a real part/chapter slug
  ```
  The three journeys already worked out in the preface's "A map of the book" section
  (`{#...}` home, float `[ref:book-map]`):
  - **`read-straight-through`** — actor: first-time reader; goal: follow the argument in order; steps: Part
    1 → 2 → 3 → 4 → 5 → back matter.
  - **`do-it-monday`** — actor: practitioner; goal: apply this now; steps: Part 1 → Part 4 → dip into Parts
    2–3 as a technique needs its foundation.
  - **`be-convinced-first`** — actor: skeptic; goal: see the method survive a real system before learning
    the how; steps: Part 1 → Part 5 → back for the how.
- **Md symbols referenced.** The `[ref:book-map]` float (existing) as the journeys' home; **one new
  symbol** to mark each journey and its steps in the prose so the model joins to the exact sentence that
  promises the path (see §3 — `journey` / `journey-step`).
- **Invariants.** Every step's `target_part_or_chapter` resolves to a real part number / chapter slug in
  the book (join against the outline view). Every journey named in the model is described in the prose and
  vice versa (two-way coverage, mirroring the concept model's L3/L4).

### 2.4 Cross-reference graph (specified, recommended)

- **Quality question.** Does every cross-reference resolve, and does the reference structure hold where it
  should (a float is introduced before it appears; a `[ref:]` names a real label)?
- **Typed schema.** `Edge(kind, from_chapter, from_block, target, resolves)` over three edge kinds:
  `ref` (`[ref:key]` → a `<!-- label: key -->` float), `chapter-link` (`[text](x.html)` → a real
  chapter), `concept-ref` (prose → an `index-def`). This is a thin projection over `book_ir`'s existing
  `Document.refs()` and `Document.labels()` — most of it is *already computed by the IR*, so this view is
  cheap.
- **Md symbols referenced.** `[ref:key]`, `<!-- label: key -->`, `[text](chapter.html)` — all existing.
- **Invariants.** Every `ref` edge resolves to a label (already the `book-float-ref` gate covers the
  before-its-float rule; this generalizes to *all* refs). No chapter-link points at a non-existent page.

### 2.5 Thesis-weave view (specified, recommended)

- **Quality question.** The book rests on two theses (the Modeling Thesis, the Alignment Thesis). Part 2
  claims to develop one and Part 3 the other. Are the theses actually *woven* through the parts that claim
  them, or only asserted in the preface?
- **Typed schema.** `ThesisWeave(thesis_slug, claimed_parts[], woven_at[])` where `woven_at` is the set of
  chapters that carry a `<!-- thesis: modeling|alignment -->` marker. `tests/book.py` already runs a
  "thesis-woven" audit; this view formalizes its result as a queryable model.
- **Md symbols referenced.** The concept anchors for `thesis-modeling` / `thesis-alignment` (existing);
  **one new symbol** — a `<!-- thesis: slug -->` marker an author drops in a chapter that develops a
  thesis, so the weave is explicit rather than heuristic.
- **Invariants.** Every claimed part has ≥1 `woven_at` chapter. No thesis is claimed by a part it never
  touches.

---

## 3. The symbol scheme

The models reference symbols in the markdown. The governing constraint: **the notation-leak gate and the
renderer share one vocabulary SSOT (`MARKER_KEYWORDS` in `build_book_html.py`), and that file is owned by
the concurrent C→A migration — this design must not require editing it for the PoC.** A new marker keyword
that the renderer does not know how to consume ships as escaped visible text (`&lt;!-- sec: … --&gt;`), an
ugly leak. So the scheme is layered:

### 3.1 Existing symbols reused (no new work)

| Symbol | Count | Views that use it |
|--------|------:|-------------------|
| `{#slug}` heading anchor | 22 | Outline (stable section id) |
| `<!-- index-def: slug -->` | 126 | Conceptual (concept definition anchor) |
| `<!-- index-example: slug -->` | 12 | Conceptual (concept example anchor) |
| `<!-- label: key -->` | 43 | Conceptual, Cross-ref (float labels) |
| `[ref:key]` | — | Conceptual, Cross-ref, Journeys (float refs; book-map home) |
| `[text](chapter.html)` | — | Conceptual, Cross-ref (inter-chapter links) |

### 3.2 Structural derivation — symbols the model computes, not the author annotates

Two facts the outline needs are **derived structurally**, so they need *no* symbol at all:

- **Topic sentence** = the first sentence of the first paragraph block following a heading. `book_ir`
  already gives the block sequence; the model walks it. (162 of 164 headings are followed by a paragraph;
  the 2 that are not are exactly the O2 findings the view should surface.)
- **Derived section id** = a slug of the heading text, used when no explicit `{#slug}` exists. So the
  outline is *complete on day one* with zero md edits — explicit `{#slug}` anchors upgrade a derived id to
  a curated one incrementally, and the model reports the `derived` count as the "sections still wanting a
  stable anchor" backlog.

**This is the key design choice for the PoC: the outline view is 100% derivable from the current book with
no new markdown symbol.** It rides `{#slug}` where present and derives the rest.

### 3.3 New symbols proposed (for the author to ratify, needed by later views)

Two views want a symbol the vocabulary does not yet have. Both are **HTML-comment style, degradation-
friendly** (invisible in a plain MD viewer), consistent with the existing directives — and both require
one `MARKER_KEYWORDS` row, which is a **reconciliation item with the C→A agent** (§6), not a PoC edit.

| New symbol | Notation | Purpose | Est. md sites |
|------------|----------|---------|---------------|
| `<!-- journey: id \| actor \| goal -->` + `<!-- journey-step: id \| order \| target -->` | HTML comment, arg-delimited by `\|` (matches `figure:`'s `src \| caption` convention) | Anchors each reading path and its steps to the exact prose that promises it (User-journeys view) | ~3 journeys × ~4 steps ≈ 15 markers, all in the preface's "A map of the book" section |
| `<!-- thesis: modeling\|alignment -->` | HTML comment, enum arg | Marks a chapter that develops a thesis (Thesis-weave view) | ~6–8 (the Part 2 / Part 3 chapters) |

**Recommended notation rule for all new book-model symbols:** an arg-bearing marker uses `keyword: arg`
with `|`-delimited fields (the established `figure:` / `table:` convention), lives on its own line, and
degrades to an invisible comment in any plain markdown viewer. This keeps the scheme uniform with what the
book already teaches and what `book_ir`'s `_MARKER_LINE` already parses.

Until the C→A agent adds these keywords to `MARKER_KEYWORDS`, the journeys and thesis-weave views can
still be authored **derived-from-existing-prose** (the journeys are already fully described in the preface;
the thesis-weave audit already runs heuristically) — the new markers make the join *exact and stable*
rather than heuristic, which is the upgrade, not the enabler.

---

## 4. How each model stays honest — the drift check

Every view ships with a **drift check that re-derives the model from the source and fails on divergence** —
the book's own `derived-not-snapshotted` discipline, dogfooded. The contract (identical to the starter
kit's drift-lint contract and the `concepts.json` L1–L4 precedent):

1. **Load the stored model** (its declared sections / journeys / concepts) from the `book-models/*.json`
   sidecar.
2. **Re-derive the model from the book** via `book_ir` + the thin helper, the same call sequence the build
   uses.
3. **Set-diff the two.** An element in the derived set but not the stored one (a section added without
   regenerating), or the reverse (a stored section the book no longer has), is a finding.
4. **Re-run every derived field** (topic sentence, id_source) and assert it equals the stored value.
5. **Exit non-zero on a finding** — but land **audit-only first** (repo rule-#55 discipline): the check
   contributes zero to the fail count until a fix-wave drains the seed findings, then a follow-up promotes
   it to blocking. This is exactly how `concepts.json`'s L1–L3 landed (audit-only → drain → gate).

The outline view's drift check is implemented in `tests/book_models.py` and registered in
`catalog_tests.py` as **audit-only**.

**Derived-not-stored, taken further.** The purest form (what the outline PoC does) stores *nothing* and
re-derives the whole model on every run, so there is no sidecar to drift at all — the "stored model" is
regenerated into `book-models/outline.json` as a queryable artifact carrying a provenance header, and the
drift check asserts the on-disk artifact equals a fresh derivation (a hand-edit or a stale regen is the
finding). This matches the repo's auto-generated-file provenance discipline.

---

## 5. Where the model files live

```
book-models/
  DESIGN.md                 # this doc
  book_symbols.py           # THIN helper over book_ir (heading ids, topic sentences, journeys) — my code,
                            #   read-only over book_ir; the reconciliation target for book_ir extensions
  outline_model.py          # the Outline view: types + derive_outline() + regenerate/verify
  outline.json              # the materialized outline (provenance-headed, regenerated, gitignored-or-tracked TBD)
tests/
  book_models.py            # the drift check(s), registered audit-only in catalog_tests.py
```

Rationale: a top-level `book-models/` dir mirrors the product's `models-bridge/system-models/` genre (typed
model files next to a design doc), keeps the book-about-the-models cleanly separated from the book prose
under `book/`, and gives the future multi-view build one obvious home. The thin helper stays *out* of
`book/book_ir.py` (owned by the C→A agent) as a separate module, with its wanted `book_ir` extensions
written down for reconciliation (§6).

---

## 6. `book_ir` extensions wanted (reconciliation with the C→A migration)

The thin helper `book_symbols.py` computes three things `book_ir` does not yet expose. Once the C→A
migration lands, fold these into `book_ir` so there is one typed layer, not two:

1. **Heading `{#slug}` id extraction.** `book_ir`'s `Block` for a heading carries the raw `## Text {#slug}`
   but does not split the `{#slug}` id off. Wanted: `Block.heading_id: str | None` (parsed with the
   renderer's own `_HEADING_ANCHOR_RE`, the SSOT) and `Block.heading_text` (the id stripped). Today the
   helper re-runs that regex; the reconciled form imports the renderer's regex so there is no second copy.
2. **`index-def` / `index-example` concept anchors as typed refs.** `book_ir` records a lone
   `<!-- index-def: slug -->` as a `DIRECTIVE` block with `directive="index-def"` but does not expose the
   slug as a first-class field. Wanted: a `ConceptAnchor(slug, kind, chapter, block_index)` accessor on
   `Document`, so the conceptual + cross-ref views join on it without re-parsing.
3. **Topic-sentence accessor.** Wanted: `Chapter.section_topic_sentences() -> list[(heading_block,
   first_para_block)]`, the heading→following-paragraph pairing the outline derives, so every view that
   needs "the paragraph that follows this heading" shares one implementation.

**Bug B1 (found while building the PoC — a real `book_ir` defect, not just an extension).**
`book_ir.Block.heading_level` reads **0 for a real H2/H3** when a marker comment is glued to the head of
the heading's block (e.g. `<!-- index-def: refactoring-is-free -->` on the line above `## …` with no blank
line). Cause: `_parse_chapter` computes `heading_level` from the block's ORIGINAL `first = lines[0]`, but
that first line is the peeled marker, not the `#` line, so `len(first) - len(first.lstrip("#"))` is 0.
Reproduces on ≥3 headings in `4.5-lessons-learned.md`. The helper works around it by re-deriving the level
from the heading line the IR leaves in `raw` (`book_symbols.heading_level`). The fix in `book_ir`: compute
`heading_level` from the *remaining* heading line after marker-peeling, not the original `first`. Hand this
to the C→A agent; until fixed, any consumer trusting `Block.heading_level` mis-reads these headings.

None of the three extensions blocks the PoC — the helper computes all three today. B1 is a defect the C→A
agent should absorb; the extensions are the *unification* targets once both agents' work is in.

---

## 7. Ratification questions for the author

Before the full multi-view build, four calls:

1. **View set.** Ship the three named views plus the two recommended (cross-reference graph,
   thesis-weave), for five? Or hold the two extras until a failure demands them (the starter kit's "model
   only where a failure lives" rule argues for holding)?
2. **New-symbol notation.** Approve `<!-- journey: id | actor | goal -->` / `<!-- journey-step: ... -->`
   and `<!-- thesis: slug -->` as HTML-comment, `|`-delimited markers (uniform with `figure:`)? And is the
   `MARKER_KEYWORDS` addition a reconciliation item to hand to the C→A agent, or should the journeys view
   stay derived-from-prose (no new marker) to keep zero coupling?
3. **Where model files live.** Confirm top-level `book-models/` (mirrors `models-bridge/system-models/`),
   vs. under `book/` (next to `book_ir`), vs. under `tests/` (next to the drift checks)?
4. **Drift-check severity + artifact tracking.** Confirm audit-only-first landing (rule #55), and: is
   `book-models/outline.json` a **tracked** provenance-headed artifact (queryable, diffable in PRs) or
   **gitignored** and regenerated on demand (like the PDF)?
