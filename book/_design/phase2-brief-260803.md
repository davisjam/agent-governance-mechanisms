# READY-TO-DISPATCH BRIEF — PHASE 2 (2a+2b): chapter opening/closing discipline (Fable, models-first)

Dispatch after Task 6 (DONE, live). Model **fable-5**. run_in_background. Live tree, branch main, NO worktree, single writer. commit-early-often. This pass = **analysis + model + FLAG** (2a+2b); the 2c refactor is a separate Opus follow-up the orchestrator gates on the flag count. Record to the results-log.

## Brief text (paste into Agent prompt)

You are editing the MAGE book in the governance-catalog repo (LIVE checkout at `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). Work **models-first**, **slow and correct**, **commit early and often**. This is NOT the parent ada-tool product — book workflow = edit → `catalog.py validate` → `book/build_book_html.py` → `catalog.py deploy github`. Note: `book/_design/*.md` are TRACKED coordination docs (the book build skips `_design`, so they never orphan) — commit your results-log edits normally.

**Your task = PHASE 2 sub-steps 2a + 2b**, spec'd in `book/_design/book-editorial-discipline-directive-260802.md`:
- **§ "Task 2 — Restructure the evidence (chapter openings + endings)"** (Part A) — the discipline, verbatim.
- **§ "PHASE 2 — Chapter opening/closing discipline"** (Part B) — the 2a/2b/2c sub-sequence.

**THE DISCIPLINE (what you inspect against):**
- Every chapter **OPENING** should identify: (1) the failure or question the chapter addresses · (2) the chapter's answer · (3) how it advances one of the two theses (Modeling / Alignment).
- Every chapter **ENDING** should give ONE of: a concrete consequence · a transition to the next unresolved problem · a concise synthesis. It must NOT merely re-announce the chapter's thesis.

**DO (this pass = analysis + model + flag; NO prose refactor):**
1. **2a — inspect EVERY chapter's opening + ending** against the discipline. Read the actual chapter prose (the openings/closings), not just topic sentences. For each chapter record: does the opening carry all three elements (failure/question · answer · thesis-link)? does the ending do one of the three good things and avoid thesis-re-announcement? Leverage the landed models: the argument-spine already labels each chapter's advanced thesis-claims (`book-models/argument-spine.json`) and the concept model carries the two theses — an opening's "which thesis" should match the chapter's spine labels; flag mismatches too.
2. **2b — MODEL the opening/closing shape (models-first).** Add per-chapter `opening_shape` + `closing_shape` assessment to the model — a field on the outline or outcomes model if it fits (the author expects the models already mostly support this), else a small new `chapter-shape` model sibling. Encode the checkable predicates (opening has failure/answer/thesis; ending is consequence|transition|synthesis AND not-mere-re-announcement). Add an **audit-only** check (consistent with the existing L-series checks in `tests/`, **audit-only-first** per the repo's blocking-lint-landing discipline — land it non-gating; promotion is a later step). Regenerate reverse_index/outline if touched.
3. **FLAG** every failing opening and every failing ending — chapter + which element is missing/weak (like Phase 1's flag list). Exempt kinds mirror the spine's (preface / acknowledgments / conclusion / discussion / end-of-part synthesis) — an exempt chapter's opening/closing discipline is softer; note but don't flag those as failures.
4. **DO NOT rewrite prose openings/endings in this pass.** Produce the analysis + the model + the flag list. The refactor (2c) is the orchestrator's next serial step (Opus), gated on how many real failures you surface.

**GATES + deploy:** `catalog.py validate` (0) · `book/build_book_html.py` (green) · `catalog.py deploy github`; foreground-poll the Deploy Pages CI to success; curl landing + models-view + a couple pages for 200. (The model + audit-only check are the deployable change; no prose changes expected.)

**RECORD (do not relay):** append a `## PHASE 2 (2a+2b) — chapter opening/closing analysis` block to `book/_design/editorial-run-results-260802.md`: the model/field added + the audit-only check, and the **FLAG LIST** (failing openings + failing endings, per chapter, with the missing element) so the orchestrator can size the 2c refactor. Keep house style; C7 discipline on any new claim/definition.

Thorough over fast. On a load-bearing ambiguity, make the most defensible call, DOCUMENT it in the results-log, continue.
