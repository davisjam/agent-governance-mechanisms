# READY-TO-DISPATCH BRIEF — PHASE 3 · 3c: EXECUTE the GEE restructure (Opus; the flagship execution)

Dispatch after 3b (DONE — classification at `book-models/catalogue-classification.json`, HEAD `7590fe4`). Model **opus**. run_in_background. Live tree, branch main, NO worktree, single writer. This is the BIGGEST task in the run. **Internally STAGED + BATCH-EMIT + RESUMABLE** (see below) — a prior sibling died from stream-silence; you must stay tool-active and commit per stage/capability.

## Brief text (paste into Agent prompt)

You are executing the catalogue restructure for the MAGE book (LIVE checkout at `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). This is Phase 3 · step 3c: turn the flat 82-entry catalogue into the **Governed Engineering Environment construction kit** per the 3b classification. Work **slow and correct**; the classification is your deterministic guide.

**⚠️ ANTI-DEATH / BATCH-EMIT / RESUMABLE (MANDATORY):** Do NOT do long silent thinks. Commit frequently (per stage, and within stage 2 per capability). Never go more than a few minutes without a tool call. Keep EVERY commit valid: `catalog.py validate` = 0 AND `book/build_book_html.py` green (the reachability + INDEX-consistency gates must pass at each commit — sequence your edits so the tree is never left inconsistent). If you approach context/time limits, COMMIT progress and append a precise **"3c REMAINING"** checklist to `book/_design/editorial-run-results-260802.md` (which capabilities/entries are done vs pending) so a continuation resumes cleanly.

**READ FIRST:**
- `book-models/catalogue-classification.json` — YOUR SPEC. `L1_principles` (8), `gee_capabilities` (9: KNOW·SYNC·CONSTRAIN·ADMIT·COMPLETE·PRESERVE·PROVENANCE·MANAGE·GOVERN), `L2_patterns` (25, each with parent_capability, rubric score, canonical_card, merged_cards, vivid_failure + concrete_impl pointers), `compositions` (8 named stacks), `dispositions` (all 82: keep-as-L2 / merge-into / demote-to-L3-under / lift-to-L1).
- `book/_design/book-editorial-discipline-directive-260802.md` §§ "Task 3", "Task 3 SUPPLEMENT" (3-level + generalize-idea-not-evidence), "Task 3 SUPPLEMENT 2" (the **title "Constructing the Governed Engineering Environment"**, subtitle *"A catalogue of models, controls, compositions, and known uses"*, and the verbatim **opening passage** — adapt to house voice).
- `book/_design/editorial-run-results-260802.md` § "PHASE 3 · 3b" — the rationale + the TWO borderline folds to preserve (see below).
- This repo's `README.md` (entry template + INDEX contract) + `INDEX.md` + `catalog.py` (validate/build; the census marker `<!--census:controls-->N<!--/census-->` in CLAUDE.md; MODEL_NODES; catalogue-views; the reachability gate). Understand the entry/INDEX/model machinery BEFORE restructuring — keep it all consistent.

**STAGE 1 — SCAFFOLD (commit; deployable-valid):**
- Retitle the catalogue section to **"Constructing the Governed Engineering Environment"** + the subtitle. Write the **GEE opening passage** (adapt SUPPLEMENT-2's passage to house voice — don't paste raw).
- Write the **8 L1 principles** (the deep claims that EXPLAIN the catalogue — where they best live: a principles preamble to the section / a short L1 page each; your call, keep it coherent + reachable).
- Establish the **9 GEE capabilities** as the organizing structure of INDEX/catalogue-views (capabilities ORGANIZE, they are not entries). Group the existing entries under their capability (from each entry's disposition→L2→capability). Name the **8 compositions** (the stacks) somewhere coherent.
- Reframe the catalogue's own CLAIM: not "we discovered 82 mechanisms" but *"the case produced ~82 concrete mechanisms; comparative analysis reduced them to 25 canonical patterns under 9 capabilities, the remainder retained as variants and known uses."*
- Keep all 82 entries intact in this stage (frame over existing entries). validate 0, build green, COMMIT.

**STAGE 2 — CONSOLIDATE, capability by capability (commit PER capability):** for each of the 9 capabilities:
- **(Re)write its L2 canonical patterns** to the fuller pattern form, retaining empirical texture — **one vivid failure · one concrete DocAble impl · one diagram · one model/code fragment · ≥1 alternative · clear limits** (use each L2's `vivid_failure`/`concrete_impl` pointers; NAME AFTER ABSTRACTION — the L2's abstract name, not the impl-biased title). Absorb `merged_cards` content.
- **Demote its L3 entries** to variants / known-uses / sidebars / examples UNDER their parent L2 (per each disposition). L3 is PRESERVED, never deleted — it stays as a variant/known-use (subordinated in INDEX under its parent, reframed with a "variant/known-use of <L2>" framing). Choose the file-level approach that keeps validate 0 + reachability green.
- COMMIT after each capability (e.g. `3c: consolidate CAP-PROVENANCE — 1 L2 + N known-uses`). ~9 commits here.

**STAGE 3 — FINALIZE (commit + deploy):**
- Update the **census** marker to the new count (decide what the census counts now — L2 patterns, or total entries — and make CLAUDE.md's marker + any census lint consistent). Update **MODEL_NODES**, **catalogue-views**, the **reachability gate**, and INDEX so everything is consistent and 0-orphan.
- Write the **CUTS/MERGES RECORD** (this run cut ~nothing — it CONSOLIDATED; record the 2 merges + 54 demotions + 1 lift as the merge record, and any genuine cuts).
- `catalog.py validate` 0 · `book/build_book_html.py` green · `catalog.py deploy github`; foreground-poll Deploy Pages CI to success; curl the landing + the new catalogue section + a few L2 pages for 200 + spot-checks (title, opening passage, a capability grouping, an L2 pattern with its known-uses).

**TWO BORDERLINE FOLDS — preserve the distinction (from 3b's flag):** `formal-invariant-verification` is folded under **Model-Derived Assurance Coverage** (proof-vs-exercise) and `model-graded-finding-severity` under **Read-the-Model** (severity=f(finding,change)). Do NOT lose these distinctions — surface each as a clearly-named variant/sub-section inside its parent L2 entry.

**PRINT-VS-ONLINE (leave for the author):** keep ALL 25 L2 patterns in the printed catalogue. The lower-scored band (rubric 11–14: Adaptive Pressure, Point-of-Action, Encoded Operational Judgment, Conformance, Governed KB, Fleet Observability, Generative Validation, Staged Gates) are kept on Coverage/Case/Historical overrides — the print-vs-online refinement is a later AUTHOR editorial call, NOT yours to cut here. Just note them in the results-log for that later pass.

**DISCIPLINE:** house style (CLAUDE.md "Writing style"; Hemingway; vary figures; cap em-dash density); generalize the IDEA but keep the EVIDENCE (every L2 keeps its concrete DocAble texture); every entry stays standalone/interpretable (no dangling parent-repo paths/rule-numbers); C7 watch-phrase discipline on strong claims; book coverage ⊇ site framings.

**RECORD (do not relay):** append a `## PHASE 3 · 3c — GEE restructure executed` block to `book/_design/editorial-run-results-260802.md`: the retitle + L1 + capability structure, the per-capability L2/L3 consolidation (counts), the census/models updates, the CUTS/MERGES record, the 2 borderline folds' treatment, gates, live SHA(s), and (if you had to stop early) the precise "3c REMAINING" checklist.

Thorough over fast — this is the culmination of the whole editorial program. Keep every commit valid + commit often. On a load-bearing ambiguity, make the most defensible call, DOCUMENT it, continue — do not stall.
