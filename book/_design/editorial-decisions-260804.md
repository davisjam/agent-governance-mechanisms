# Editorial decisions — author-ratified 260804 (execute in the post-crash copyedit sequence)

Two content calls the author ruled on. Both are book-tree writes → queue behind the single live writer.

## DECISION 1 — F1.1: recharacterize the 4.1 "300k→200k" headline number (author: option (b) + "churn was yielding models")

**Ruling:** the "300,000 janky lines in, 200,000 clean lines out, one month" figure (`book/part4/4.1-brownfield.md:280-297`) is an April **recollection/estimate**, not a measurement. GROUND it in the measured `churn` data, and — the author's sharpening — make explicit that **the churn was PRODUCTIVE: it was yielding models / typed structure**, not line-thrashing. The compression came from replacing janky code with *modeled* structure (the book's own thesis, lived).

**Execute:**
1. In `book/part4/4.1-brownfield.md` (the 300k→200k passage), reframe the round numbers as the author's estimate of the episode, **corroborated by the measured churn**, and add the productive-churn point: the add/delete wasn't waste — it was janky code being replaced by models/typed structure, which is *why* the system got smaller as it got better. Do NOT delete the lived-experience narrative or the point-marker; recharacterize the epistemic status of the numbers.
2. Cross-reference / bind the measured **`churn`** data-claim (source `5.2-the-timeline-and-the-work`; holds `371,855 / 941,120 / 286,378 / 3,767` = per-window web/+backend/ add+delete; observable = "mechanization is the churn peak, then deletions collapse and later windows go net-additive"). Use a `[data:]`/`[ref:]` link if the 4.1 site supports it, or an explicit "the measured churn (§5.2) shows this shape" sentence.
3. Honesty guardrail: KEEP the churn limitation (add/delete includes generated/bundle/vendored → a churn signal, not hand-authored SLOC), so "300k→200k clean SLOC" reads as the author's estimate the churn corroborates, NOT a reconstructed measurement. Invent NO numbers; the only hard figures are the measured churn values.
4. Optional: update the `churn` data-claim gloss/observable in `book/data/data-claims.json` to note the churn was model-yielding (productive), if it sharpens the tie to 4.1 — but the 4.1 prose is the primary edit.
**Gate:** validate 0 · build green · tier-1 PASS. This is a Part-4 edit → FOLD INTO Body-Wave-4 (Part 4) so 4.1 is touched once (repetition-cut + this recharacterization in one pass), OR do as a focused edit before W4. Do NOT touch other real-world numbers.

## DECISION 2 — F3.1: drop the 3.3/3.6 alignment-thesis over-mapping (author: (A) fix-model)

**Ruling:** fix-model — the process view and scenarios view do modeling work, not alignment work; drop the unbacked label.

**Execute:**
1. In `book-models/argument_spine_declared.json` → `chapter_advances`: remove `alignment-thesis` from **`3.3-the-process-view`** and **`3.6-the-scenarios-view`** (leave `modeling-thesis`; match sibling `3.2-the-logical-view` which is modeling-only).
2. Regenerate the derived spine artifact (`argument-spine.json` via the spine model's regenerate path) in the same commit.
**Gate:** `catalog.py spine` + `catalog.py validate` 0; confirm `alignment-thesis` chapter count 11→9 and its OVERMAPPED flag reduced/cleared. Mechanical model edit → BATCH with the other small fixes (velocity SVG seven-week→20-week, `_MODEL_NOTE` §3/§4→11/11 staleness) in one "data/model correctness" wave.
