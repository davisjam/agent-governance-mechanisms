# READY-TO-DISPATCH BRIEF — PHASE 2c: opening/closing refactor (Opus, prose judgment)

Dispatch after Phase 2 (2a+2b) — DONE, live `02bf052`, single-writer confirmed. Model **opus**. run_in_background. Live tree, branch main, NO worktree, single writer. commit-early-often (per chapter or small group). Deploy at end. Record to the results-log.

## Brief text (paste into Agent prompt)

You are editing the MAGE book in the governance-catalog repo (LIVE checkout at `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). Work **slow and correct**, **commit early and often** (per chapter or small group). This is NOT the parent ada-tool product — book workflow = edit → `catalog.py validate` → `book/build_book_html.py` → `catalog.py deploy github`. `book/_design/*.md` are working drafts; don't fret their tracked/untracked state.

**Your task = PHASE 2c** — refactor the failing chapter openings/closings that Phase 2a+2b flagged. This is prose judgment work; get each fix RIGHT.

**READ FIRST:**
- `book/_design/editorial-run-results-260802.md` § **"PHASE 2 (2a+2b) — chapter opening/closing analysis"** — the FLAG LIST with per-chapter diagnosis, the 2c sizing notes, and the exemplars worth imitating.
- `book-models/chapter-shape.json` — the `flags` block (the queryable worklist) + each chapter's `opening`/`closing` assessment + the `anchors` (first/last 12 prose words each assessment was made against).
- `book/_design/book-editorial-discipline-directive-260802.md` § "Task 2 — Restructure the evidence" — the discipline: every OPENING identifies (failure/question · answer · which thesis it advances); every ENDING gives (a concrete consequence · a transition to the next unresolved problem · a concise synthesis) and does NOT merely re-announce the thesis.

**THE 9 FIXES:**
1. **Openings missing a thesis-link (ONE pattern) — `3.2-the-logical-view`, `3.3-the-process-view`, `3.5-the-physical-view`, `3.6-the-scenarios-view`:** add ONE sentence to each opening saying how that view advances a thesis, matching THAT chapter's spine labels in `book-models/argument-spine.json` (do NOT invent a thesis the spine doesn't carry). `3.4-the-development-view` is the exemplar of the shape ("the view the people and agents who build the system reason through"). Keep each opening tight.
2. **`1.1-the-printer` opening (heaviest):** it has NO untitled lead — it opens mid-taxonomy. Write a real chapter lead that names the failure/question AND the thesis-link; the printer frame + fault-lies-in-instructions currently arrive only in the closing — pull the framing up front (don't merely duplicate; restructure so the lead frames and the body develops).
3. **`4.2-the-skills` opening:** add a motivating failure/question (currently pure inventory: "a book of method ought to ship with batteries"). What failure does the skills library answer?
4. **`2.4-lifecycles-and-runbooks` closing:** currently stops mid-taxonomy at the pre-canned brief + a Learn-more link. Add a chapter-level close — a consequence, a transition to the next unresolved problem, or a concise synthesis that re-collects lifecycles→runbooks→split.
5. **`3.1-the-executable-zoo` closing:** currently ends on insets + a navigation note (apparatus tail). Give it a real close.
6. **`5.4-the-road-to-mage` thesis-spine MISMATCH (judgment):** the opening explicitly claims the Modeling Thesis ("each step induces one more model… the models accrete"), but the spine labels 5.4 `[oversight-does-not-scale, seat-moves, grounded-in-one-case]` (at focus-cap 3, no modeling-thesis). DECIDE + DOCUMENT: either (a) relabel the spine — swap one claim for modeling-thesis (update `argument_spine_declared.json` + regen + keep the spine reconciliation invariants happy) — if the chapter genuinely advances modeling-thesis; or (b) reweight the opening so it leads with the claims the chapter actually advances. Pick the one that's TRUE to what 5.4 does; record the call.

**MODELS-FIRST DISCIPLINE (critical — CS5 anchor-freshness guard):** after you rewrite any opening/closing, **RE-ASSESS that chapter in `book-models/chapter-shape.json`** (its declared source `chapter_shape_declared.json` → regen) — update the `opening`/`closing` assessment AND **refresh the `anchors`** to the new first/last 12 prose words. CS5 reddens a chapter whose prose changed until its anchors are refreshed; drive `check_chapter_shape` back to 0 findings. The `flags` block should shrink to empty (or only the deliberately-deferred, documented). If you relabel the spine for 5.4, keep `check_argument_spine` green too.

**House style:** this repo's CLAUDE.md "Writing style" (Hemingway; active voice; short sentences; cut qualifiers; vary rhetorical figures, cap em-dash density). Exemplars to imitate: `4.6` (opening names both theses + maps them), `1.4`/`1.5`, `3.4`'s thesis-clause. Keep book coverage ⊇ site framings. Honor the C7 watch-phrase discipline on any strong claim.

**GATES (before deploy):** `catalog.py validate` (0) · `book/build_book_html.py` (green) · `catalog.py deploy github`; foreground-poll the Deploy Pages CI to success; curl landing + the touched chapters for 200 + content spot-checks. Confirm `check_chapter_shape` + `check_argument_spine` at 0 findings.

**RECORD (do not relay):** append a `## PHASE 2c — opening/closing refactor` block to `book/_design/editorial-run-results-260802.md`: each fix (chapter → what changed), the 5.4 reconciliation decision + rationale, the model re-assessments + anchor refreshes, the CUTS RECORD (likely ~0 cuts — this is sharpening, not cutting), gates, live SHA(s).

Thorough over fast. On a load-bearing ambiguity, make the most defensible call, DOCUMENT it in the results-log, continue.
