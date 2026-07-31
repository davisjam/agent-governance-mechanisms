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
| 6 | **Learning outcomes** | (a book-specific pedagogical view) | *Does every teaching unit declare what a reader can DO after it, does that outcome map to a real unit, and does the Part→chapter→section outcome tree decompose without gaps?* | **PoC built here** |

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

### 2.6 Learning-outcomes view (built)

The book is a textbook, so it is modeled as one: this view names what a reader should be able to **DO or
KNOW** after each unit, and maps each outcome to the unit that teaches it. It has no Kruchten analogue — it
is a book-specific pedagogical view, the direct answer to the author's ask ("learning outcomes … another
view, perhaps partially derived or annotative").

- **Quality question.** Does every teaching unit — the book, each Part, each chapter, and the sampled
  sections — declare what a reader can do after it; does each outcome map to a real outline unit; and does
  the Part→chapter→section outcome tree decompose without a pedagogy gap?
- **Typed schema.**
  ```
  OutcomeModel
   └─ Outcome(outcome_id, granularity, unit_id, verb, obj, statement, bloom, provenance, anchor, gap_note)
  ```
  - `granularity` ∈ {`book`, `part`, `chapter`, `section`} — the four tiers the outcome tree decomposes
    through. Book-level outcomes decompose *down* into Part → chapter → section outcomes.
  - `unit_id` — the **join key into the outline view**: a `section_id` (section), a chapter `slug`
    (chapter), `part-<N>` (part), or `book`. This is what ties the pedagogy to the structure — an outcome
    whose `unit_id` no longer resolves is the finding.
  - `verb` + `obj` — an outcome is an **action verb + object** ("distinguish · a constraint from a
    sensor"). `verb` comes from a closed **Bloom-level taxonomy** (below); `bloom` is derived from it.
  - `provenance` — the honesty tag (below): `derived` | `declared` | `gap-recommended`.
  - `anchor` / `gap_note` — the grounding: for a `derived`/`declared` outcome, the topic sentence or heading
    it rests on; for a `gap-recommended` one, why the unit falls short.
- **The verb taxonomy.** A closed set of teaching verbs grouped by the six Bloom (2001-revision) cognitive
  levels — **know** (recall/recognize/define…), **understand** (explain/describe/distinguish…),
  **apply** (apply/use/compute/write…), **analyze** (classify/map/trace/situate…), **evaluate**
  (evaluate/judge/size/choose…), **create** (design/construct/author/model…). The set is tuned to *this*
  book's pedagogy — outcomes run from "recognize a mechanism" up to "design a control." An outcome's verb
  must be in the set, so the Bloom level is derivable from the verb alone and the vocabulary stays uniform
  (checked as invariant U2).
- **Derived, declared, or gap-recommended (the honesty split).** Mirroring the outline's derive-what-you-can
  / annotate-the-residual move, one level up — but with a **three-way** tag, because the author wants the
  induction honest *and* wants gap recommendations:
  - **`derived`** — grounded in what the unit teaches **as written**, traceable to an anchor. Some are
    *lifted mechanically* from a topic sentence whose first word is a teaching verb ("Name both ends before
    you move." → *know · name both ends*); the rest are hand-authored but tightly anchored to a real heading
    or topic sentence. The derivation is kept **high-precision on purpose**: navigational imperatives
    ("Start at the decision on the left", "Read the stack as …") are *refused*, because lifting them would
    manufacture a garbled outcome masquerading as taught content.
  - **`declared`** — a real outcome the existing (sometimes thin) prose roughly supports, made explicit by
    the author. The chapter / Part / book outcomes are declared — each synthesized across the unit's section
    titles and arc, and citing that arc as its anchor.
  - **`gap-recommended`** — the outcome a **missing or inadequately-delivered** unit *ought* to deliver;
    content that does not yet exist. Never masqueraded as derived. The two sections whose heading promises a
    teaching point but whose opening block is a non-paragraph (the outline's O2 findings) are the cleanest
    examples — the heading names an outcome the prose does not state.

  The `declared` + `gap-recommended` sets are exactly the **author's rearrange/fill worklist**; the
  `derived` set is what the book teaches today.
- **How it maps onto the outline.** The outcome model is a *projection over the outline view*. Every
  `unit_id` is an outline key; the coverage check re-derives the outline and joins. A chapter is "covered"
  if it carries a chapter outcome *or* owns a section that carries one. The mechanical derivation reads the
  outline's topic sentences directly. So the two views share one structural source — the outline is the
  outcomes view's substrate, not a parallel parse.
- **Invariants (checked by the drift check).**
  - *drift* — `outcomes.json` equals a fresh derivation (declared outcomes merged with derived candidates).
  - *U1 — every outcome's `unit_id` resolves* to a real section id / chapter slug / `part-N` / `book`.
  - *U2 — every verb is in the taxonomy* and `bloom` equals the verb's level.
  - *U3 / U4 / U5 — every chapter, every Part, and the book carry ≥1 outcome* (a bare unit is a pedagogy
    gap the author fills).
  - *U6 — every provenance tag cites its grounding* (a `derived`/`declared` outcome names an anchor; a
    `gap-recommended` one names why the unit falls short) — the honest-labeling discipline, enforced.
  - *(informational, not gated)* — the **uncovered-section list**: sections that teach something but carry
    no outcome yet. This is the fill worklist for the author's next phase, printed by
    `python3 book-models/outcomes_model.py gaps`, not a gate finding (this PoC covers a representative
    sample of sections, not all 164).

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

### 3.4 Notation decision for the outcomes view — model-file declarations, no inline marker

The outcomes view carries facts the prose does not fully state (a synthesized chapter outcome, a
gap-recommended outcome for content that does not yet exist). Two places those could live:

- **In the model file** — an `outcomes_declared.json` keyed by the outline's unit ids, hand-authored, that
  the model merges with the mechanically-derived candidates.
- **Inline in the markdown** — an `<!-- outcome: verb | object -->` marker beside each heading.

**This PoC chose the model file, and recommends it stand.** Three reasons:

- **Renderer stays uncoupled.** A model-file declaration needs no `MARKER_KEYWORDS` row and no renderer
  change — so the outcomes view ships with zero risk of the notation-leak an unknown inline keyword causes,
  and with no reconciliation dependency on the renderer.
- **Gap-recommended outcomes have no home in the prose by definition.** A `gap-recommended` outcome names
  content that does not exist yet; there is no heading to hang an inline marker on. The worklist has to live
  outside the prose it is a worklist *for*.
- **The declarations ARE the author's editable surface.** `outcomes_declared.json` is the one file the
  author hand-edits; `outcomes.json` and the reviewable `outcomes-draft.md` digest are generated from it.
  Keeping the declarations in one queryable file (not scattered across 28 chapter files) is what lets the
  author read the whole pedagogy at once — the reason to model it at all.

An inline `<!-- outcome: … -->` marker remains a *possible later upgrade* for the `derived` outcomes (it
would let a section state its own outcome next to its heading, and the model would join on it instead of
re-deriving). If pursued, it follows the §3.3 rule — HTML-comment, `|`-delimited, one `MARKER_KEYWORDS` row
added deliberately as a documented reconciliation step, never a silent PoC edit. It is explicitly **not**
wired here.

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

The outline view's and the outcomes view's drift checks are both implemented in `tests/book_models.py` and
registered in `catalog_tests.py` as **audit-only** (`check_outline_model`, `check_outcomes_model`).

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
  book_symbols.py           # THIN helper over book_ir (heading ids, topic sentences) — read-only over book_ir
  outline_model.py          # the Outline view: types + derive_outline() + regenerate/verify
  outline.json              # the materialized outline (provenance-headed, TRACKED)
  outcomes_model.py         # the Outcomes view: types + verb taxonomy + derive_model() + regenerate/verify/gaps
  outcomes_declared.json    # HAND-AUTHORED source: declared + gap-recommended outcomes, keyed by unit id
  outcomes.json             # the materialized outcomes model (provenance-headed, TRACKED)
  outcomes-draft.md         # GENERATED reviewable digest — the actual outcome statements, book->part->chapter->section
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

The thin helper `book_symbols.py` computes two things `book_ir` does not yet expose (a third, B1, was a
defect and is now fixed — see below). Once the C→A migration lands, fold these into `book_ir` so there is
one typed layer, not two:

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

**Bug B1 — FIXED (found while building the outline PoC; fixed while building the outcomes view).**
`book_ir.Block.heading_level` read **0 for a real H2/H3** when a marker comment was glued to the head of
the heading's block (e.g. `<!-- index-def: refactoring-is-free -->` on the line above `## …` with no blank
line). Cause: `_parse_chapter` computed `heading_level` from the block's ORIGINAL `first = lines[0]`, but
that first line was the peeled marker, not the `#` line, so `len(first) - len(first.lstrip("#"))` was 0. It
reproduced on **5** headings in `4.5-lessons-learned.md`. **Fix (landed):** compute `heading_level` from the
*remaining* heading line after marker-peeling, not the original `first`. The HTML render was never affected
(the renderer computes its own heading depth), so the fix is byte-identical. With B1 fixed, the helper's
former `heading_level()` workaround was dropped — `book_symbols` now reads `Block.heading_level` directly.

None of the remaining extensions blocks the PoC — the helper computes both today. They are the
*unification* targets once the C→A work is fully in; B1 is now off the list.

---

## 7. Ratification — settled defaults, and the open calls for the outcomes view

The author has **ratified the build-forward defaults**: the view set is GO (build the views out); model
files live in top-level `book-models/`; drift checks land **audit-only-first** (rule-#55 discipline); the
JSON artifacts are **tracked** (provenance-headed, diffable in PRs). Those four earlier questions are
answered — the outline and outcomes PoCs both follow them.

What remains open is specific to the outcomes view and to the still-unbuilt views:

1. **Verb taxonomy.** Approve the six-level Bloom-grouped closed set (§2.6) as the outcome vocabulary? It is
   tuned to this book; adding a verb is a one-row edit to `BLOOM_VERBS`. A reader who prefers a
   coarser/finer scale (e.g. a three-tier know/apply/create) would change this table.
2. **Section-coverage scope.** This PoC declares outcomes for the book, all 6 Parts, all 24 taught
   chapters, and a **representative ~18-section sample** — not all 164 sections. Confirm the next phase
   fills the rest (the `gaps` worklist), and confirm section outcomes stay *informational* (no U-invariant
   forces every section to carry one — the author decides which sections earn their own outcome).
3. **Gap-recommended review.** The three `gap-recommended` outcomes (§2.6) are *proposals* for content that
   does not exist — the author confirms, rewrites, or rejects each. Are three the right seed, or should the
   PoC surface more of the O2 / thin-opener sections as gap recommendations?
4. **Inline outcome marker (later).** Adopt the model-file-only notation now (§3.4), and treat an inline
   `<!-- outcome: verb | object -->` marker as a *deferred* upgrade for `derived` outcomes — added
   deliberately with one `MARKER_KEYWORDS` row when/if the author wants a section to state its own outcome
   in place?
5. **Promotion to blocking (both views).** When the seed findings are drained (the outline's 2 O2 findings;
   the outcomes view's section-coverage backlog, once the author decides the coverage bar), flip both
   audit-only checks to blocking — the same drain-then-gate path `concepts.json` took.
