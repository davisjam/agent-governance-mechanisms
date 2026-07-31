# Draining the sections into the views — the plan

**Goal.** Take the 6 book views from PoC/sample to **complete at paragraph granularity**, and emit the
rearrange/gap-fill worklist. "Drain a section" = walk it, deepen the outline to each paragraph's *canonical
point*, populate every view for it, and record the gaps. Guarded by the reverse-index + drift audit that
already landed (structural + freshness pre-commit lints; semantic = a review-gate agent audit).

## The unit of work — one section

For each of the ~139 sections (the `outcomes_model.py gaps` / outline worklist):

1. **Walk it** — read the section as written.
2. **Deepen the outline — canonical points, INDUCED not lifted.** For each paragraph, author its **canonical
   point** — *"if a machine wrote this, what's the sentence"* — the normalized statement of the idea, NOT the
   prose sentence (which carries segues/rhetoric). Record it as an inline **`<!-- point: <canonical> -->`
   decorator** above the paragraph. This makes the outline **model-from-decorator** (the model derives from
   the decorators; the prose is checked against them). Honesty rule: the point is a *faithful normalization*
   of what the paragraph ACTUALLY says — a paragraph with no clear point is a **gap**, not an invented point.
3. **Populate the views** for the section:
   - **Outline** — section + paragraph points (from the decorators).
   - **Outcomes** — the outcome(s) this section serves, as **primary** (chiefly delivered here) or
     **secondary/elaborative** (reinforced here); provenance derived / declared / gap-recommended.
   - **Conceptual** — concepts this section **defines** (`<!-- index-def -->`) vs merely **uses**; the
     chapter links it makes; the role of each float/table it carries.
   - **Cross-reference** — every `[ref:]`, chapter link, concept ref resolves (the reverse index covers it).
   - **Thesis-weave** — which thesis (if any) this section develops.
4. **Emit gaps** — the **union across views**: a paragraph with no clean canonical point; a section that is no
   outcome's primary; a promised concept never defined; a dangling reference; a thin thesis touch. Two
   paragraphs that induce the **same** canonical point = a **redundancy** (the machine version of the
   terseness audit — it would have caught the 3.1 triple-telling).

## Prerequisite (do first)

Add the **`<!-- point: <text> -->` directive**: a `MARKER_KEYWORDS` row in `build_book_html.py` + IR
classification in `book_ir.py` (a DIRECTIVE/arming marker, stripped from HTML — degradation-friendly, does
not leak, byte-identical build). Land it **after the Typst spike reports** (both read/edit `book_ir` /
`build_book_html`; avoid concurrent edits). Extend the reverse index + structural audit to cover the new
`point` symbol kind (it's an authored reference — the drift-prone kind).

## Roll-out — pilot, refine, then parallelize

1. **Pilot on ONE Part** (recommend **Part 1** — smallest, 2 chapters — or **Part 2**). Do the full per-section
   procedure by hand/one-agent. Land audit-only.
2. **Refine the plan** from what the pilot teaches: canonical-point *voice* (how terse/abstract), *granularity*
   (every paragraph, or only idea-bearing ones — skip pure segues/transitions), gap-precision, decorator
   ergonomics. Update this doc.
3. **Pilot again** on a second, different-shaped Part (e.g. a Part-3 model chapter — reference-style prose).
   Refine again.
4. **Scale: 3 parallel Opuses, disjoint per-chapter scopes.** Each drains its chapters end-to-end (decorators +
   views + gaps), commits local, does NOT push. **Concurrency discipline:** disjoint chapter *files* (no two
   Opuses in one `.md`); model-file writes serialize or partition by chapter (append-only per chapter, or each
   emits a per-chapter fragment merged after); the reverse-index/drift audit is the guardrail; run a
   `book-models` consolidation check afterward (did any re-implement `book_symbols`?).

## Honesty + provenance (non-negotiable)

- **Derived** = grounded in the prose as written (canonical point / primary outcome traceable to the text).
- **Declared** = a real point/outcome thin prose roughly supports, made explicit.
- **Gap-recommended** = the point/outcome a MISSING or inadequate unit *ought* to deliver — a recommendation
  for content that does not exist yet. Never let declared/gap masquerade as derived.
- The derived set = "what the book teaches as written"; declared + gap = the author's rearrange/fill worklist.

## Gates + discipline

- After each step: `catalog.py build` clean + **byte-identical HTML** (`git diff` on `book/*.html` empty —
  the decorators must strip cleanly), `catalog.py validate` 0, `catalog_tests.py --tier1` 0-failed,
  `catalog.py views-audit` exits 0. Keep all view checks **audit-only** during the drain.
- **Promotion:** once a view is drained to clean, flip its audit-only check to **blocking** (rule #55).
- Commit per section/chapter, co-author trailer, **do NOT push** (publish is the last step of the forward plan).

## After the drain

Rearrange content + fill the gaps (write the missing openers, define the promised concepts, add the
should-exist outcomes), then promote the view checks to blocking, then the semantic review-gate agent audit
runs over the `(point, paragraph)` pairs. Then: full Typst PDF (`book-typst.pdf`, local-only) → website sync
(site as a projection of the models) → publish.
