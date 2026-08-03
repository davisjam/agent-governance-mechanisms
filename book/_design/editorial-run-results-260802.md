# Editorial-run results log (260802) — for the ONE final report-out

Author directive: "don't bring me things, just record results for later report-out, and keep going." So each phase's outcome is RECORDED here (not relayed); one consolidated report-out at the very end. Autonomous · models-first-then-prose · 1-agent-max serial · monitor health · commit-early-often · keep the CUTS RECORD.

---

## MAGE-by-Example teaser — ✅ DONE + LIVE (`b55013a`)
- **Structural:** NEW chapter **1.2 "MAGE by Example"** (chapter-sized — a section would've tripped the 400-word cap). Renumber = file move `1.2-loops-and-models→1.3`, `1.3-the-engineers-seat→1.4`; 7 cross-refs updated (2.3, 4.1, 4.2×2, landing-big-ideas×2, an outcomes anchor). Models declared first: chapter outcome (`describe`/`understand`) + terminology stance as claims entry **`grounding-case-not-proof`** (C7 watch-phrases `is the proof`/`proves the method`) + outline skeleton.
- **Figure:** new `book/assets/docable-pipeline.svg` (working half front-door→dispatcher→core descending into a dashed **"the trust half — nothing ships unchecked"** band → checker→fidelity-validator→provenance). ICSE'27 `oversight-modes` was already in use (preface three-ways).
- **Draft:** 7 sections (Two birds one stone · What the user sees · The shape of the machine · One human a fleet · Two scars · The move that recurs · Where the map leads). Two REAL scars (the library that lied = silent structure-tree drop → shipped less-accessible-than-input; the lever that lost work), each → ban-lint / prohibition+sanctioned-escape. Two-birds motive honest. "Part 5 is the grounding case, not proof."
- **Terminology sweep:** 2 over-claiming sites fixed (preface 0.1; book-map.svg label); all legit "proof" uses preserved.
- **Gates:** validate 0 · build green (126 chapter pages) · PDF 4.6 MB · CI 30781742772 SUCCESS · live-verified (1.2/1.3/1.4 200, docable-pipeline renders, preface "grounding case", nav works).
- ⚠️ Went output-silent ~20 min mid-run (long tool call + GitHub API rate-limit backoff) → self-recovered, was NOT dead. Commit-early discipline validated (5 commits banked before the quiet).

## Phase 1 — argument spine + per-chapter claim labels (models-first) — ✅ DONE + deployed (`aa62095`; CI 30783018936 finishing, backstop monitor `b454mwhq3`)
- **Argument-spine model** (`book-models/argument-spine.json` + `argument_spine_declared.json` + `_model.py`): the book's linear argument as **14 ordered claims**, reconciled from the 10 author-seed + 6 Big-Ideas + 16 claims (→ 17 reconciled-claims, 6 big-ideas mapped). Taxonomy + provenance + drift gate.
- **30 chapters labeled** by the spine claims they advance (+ 6 exempt; 84 advancement edges).
- **FLAGS — the book is well-focused:** **0 zero-claim suspects**; **1 over-cap** = `1.2-mage-by-example` (advances 5 — the grounding teaser, broad BY DESIGN; accepted as an overview-exception). ⇒ **Phase-1 focus refactor = NO-OP.**
- **Folded a core-concepts item early:** broadened the spine's **Modeling-Thesis** step per the punch-list (`34e2a65`).
- Added **AS1–AS7 spine drift + structural check** (audit-only-first, rule #55). Committed the punch-list addendum doc (`abc5e44`).
- 5 commits `c1a79ed`..`aa62095`; models-view live 200. Gates: validate 0 (82 entries) · build green · 28/0/3 + 9 audit-only · PDF PASS 4.4 MB (402pp) · CI 30783018936 SUCCESS · live (landing/pdf/1.2 all 200).
- **Homing:** NEW `argument-spine` model (6th sibling; reconciles-not-restates — links each step's claim-ids + big-idea slugs, invariants hold reconciliation complete BOTH ways: all 17 claims + 6 Big-Ideas + 10 author-seeds covered). Drift gate `check_argument_spine` (AS1–AS7) audit-only-first; **promotion-to-blocking after a clean session = queued follow-up.**
- **The 14 spine claims (ordered):** abundant-implementation → fault-lies-in-instructions → oversight-does-not-scale → churn-is-the-limit → three-not-knowings-cause-churn → govern-the-environment → modeling-thesis(broadened) → alignment-thesis → theses-treat-the-causes → failures-become-machinery → sync-cost-removed → mage-becomes-practical → seat-moves → grounded-in-one-case.
- **FLAGS + MY RATIFICATION DECISIONS (made autonomously, inside the ratified program):**
  - **0 zero-claim suspects.**
  - **1 over-cap = `1.2-mage-by-example` (advances 1,3,6,10,14).** → **RATIFIED as `overview`-exempt** (the whole-book teaser; breadth is its job, not a focus defect — agent's diagnosis correct). Encode the `overview` exemption in the spine model = folded into the core-concepts pass (touches the spine anyway). NOT trimming its label.
  - **Judgment-call exemptions the agent encoded → all RATIFIED:** `4.5-lessons-learned`=discussion, `3.7-scope-of-modeling`=end-of-part-synthesis, `0.2-acknowledgments`=apparatus. (0.1/6.0/6.1 = directive's own exempt kinds.)
  - **Coverage observation (real, folded into core-concepts):** spine claims **5 (three-not-knowings)** + **9 (theses-divide-the-not-knowings)** are advanced ONLY in the exempt preface — no BODY chapter develops them by name. → the core-concepts pass (which formalizes churn + the theses) will ensure a body chapter (1.3 loops-and-models or 2.3 governed-environment) carries one explicitly.
- ⇒ NEXT (serial): CORE-CONCEPTS PASS — brief ready at [core-concepts-brief-260803.md](core-concepts-brief-260803.md); reconciles with this spine, ratifies 1.2-overview, closes the 5+9 body-coverage gap. Then Task 6 · Phase 2 · Phase 3.

## CORE-CONCEPTS PASS — ✅ DONE + LIVE (`8a92395`, CI 30785297658 SUCCESS)
Six items + two folded Phase-1 follow-ups, models-first per-item commits (`967b138`→`8a92395`; brief [core-concepts-brief-260803.md](core-concepts-brief-260803.md)).

- **Item 1 — CONCEPT MODEL (capstone), `967b138`.** `concepts.json` gains (a) a `_hierarchy` meta block — six ordered levels (premise → churn → theses-as-relations → governance-conversion loop → governed engineering environment → construction repertoire), each cross-ref'd to argument-spine claim ids (same object, two grains: containment vs argument order — orders differ by design, documented in the block); (b) six `core-construct` records (NEW kind, enum extended in `tests/html.py`): `engineered-agent-loop` · `model` · `governance-mechanism` · `churn` · `failure-to-mechanism` · `governed-environment`, theses as the RELATIONS (Modeling joins model↔loop-lever-1; Alignment joins mechanism↔levers-2-4); (c) NEW audit-only **L5 check** (`check_concepts_hierarchy`) holding every hierarchy cross-ref against records + spine. New records without prose tags landed `status: planned` (L1 is gating) and flipped to `book-only` as their index-defs landed. Registry: `churn`, `engineered-agent-loop`, `governance-mechanism` added to `index-terms.md`. **Defensible call:** the governance-conversion-loop construct keeps the pre-existing concept slug `failure-to-mechanism` (renaming would churn prose tags); the mapping is documented in `_hierarchy.core_constructs._note`.
- **Item 2 — formal Model def, `7a354e1`.** `definitions.json` `model.box` ← directive phrasing verbatim; intuition (approximation/blueprint + prose/code/middle) KEPT as the first aspect; new "five load-bearing terms" aspect. Prose: 2.1's intuitive inset demoted to "**Model, first pass.**" (light def-inset); the formal definition lands as the canonical blue def-box AFTER *structured* supplies its last ingredient — the `index-def: model` anchor moved with it (same page → stored `book_home` unchanged) — plus a five-clauses unpacking paragraph. 3.1: stated as the zoo's admission test. 3.7: the through-line closes on it. 2.2's sweet-spot intuition intact (KEEP directive).
- **Item 3 — Churn def, `c2496af`.** NEW **book-only definitions class**: records with `site_home: "N/A"` are never projected (`_landing_definitions` filters; `check_definitions_site` skips model→site), so the landing keeps its four-definitions + rider framing. `churn` is the first such record (directive box verbatim + symptom/scaling-wall aspects); the preface inset mirrors it + takes `index-def: churn`. **Consistency fix caught:** the `bi-churn` Big-Idea "more" said "**two** causes" — contradicting the `three-not-knowings` claim ("exactly three"); rewritten to the three not-knowings + theses-divide.
- **Item 4 — engineered agent LOOP + figure, `f3a27b1`.** `definitions.json` `engineered-agent-loop` record (directive def verbatim; aspects: four levers · levers↔theses · not-a-generic-control-loop). 1.3 gains a closing section "**The four levers of an engineered loop**": def inset (index-def) + the four levers as a bulleted list (state exposed · action surface · success criterion · admission rule) + levers→theses paragraph + levers→not-knowings paragraph. **`loop-engineering.svg` REDRAWN:** no longer the generic input→reason→output arc — the admission gate now sits ON the feedback path with a pass/fail split (pass → the next turn's input; fail → dashed "run again" into reasoning), and the four levers are numbered disk callouts at their stations, color-split Modeling (fleet blue #2f5169) vs Alignment (governed green #1f7a4d), bottom strip naming the split. Figure moved from the loop-shape section into the levers section (both [ref:]s precede it). `lint_figure_overflow` + `lint_design_token_drift` clean; verified rendered in web + PDF (p.22). Scoped `book-section-cap` noqa added (`02b00db`) — the inlined figure's accessible description dominates the section's word count.
- **Item 5 — governance mechanism + 4 classes, `7cb6057`.** `definitions.json` `governance-mechanism` record (directive def verbatim; aspects: four classes · model-not-mechanism · why-repeatable). 2.3's constraints-and-sensors section split with two new H3s: "**Four classes, one bounded term**" (def inset + prevention·detection·evidence·admission relating to the catalogue's constraint/sensor/package Move axis — evidence + admission EXTEND it at the loop's far edge) and "**What it adds up to**" (the existing governed-environment closing, now its own subsection; "That closing line" flow into The-residual preserved). 2.3's gloss-only line updated to the bounded def. NEW claims-model entry **`model-not-mechanism-until-enforced`** (scope-boundary, ≤18 words, `contradicted_by` + watch-phrase per C7 — lint clean), reconciled into the spine's `alignment-thesis` step (AS4 complete both ways; claims 17→18).
- **Item 6 — "primitive" → core-construct rename: ALL LIVE SITES KEPT.** Grep of live book prose + catalogue/appendix confirmed every occurrence is the RESERVED implementation-level sense: `2.5-metrics` (`anchor_exercised`, a measurement primitive) — KEEP; `3.3-the-process-view` ("one OS primitive", SyncLock) — KEEP; `4.1-brownfield` (dense-primitive-region cluster, the sense the region DEPENDS on) — KEEP; `5.2` ("anonymous primitives" = ints/strings) — KEEP; `index-terms.md` `dense-primitive-region` — KEEP; appendix/catalogue hits (single-hook, counting-semaphore, promotion/rollback, atomic-op, mutator-primitive-layer) — all code-level — KEEP. **No conceptual-unit use of "primitive" exists in live prose**; the conceptual vocabulary ("core construct") is now encoded in `concepts.json` `_hierarchy.core_constructs` with the reservation stated in its `_note`, and the new prose uses it. Zero renames needed — the sweep's product is the verified reservation.
- **Follow-up A — 1.2 overview-exempt RATIFIED, `83a80c7`.** `chapter_exemptions["1.2-mage-by-example"] = "overview"` (the enum's ratify-before-use reason); spine regenerated → **flags now 0 zero-claim / 0 over-cap**.
- **Follow-up B — claims-5+9 body-coverage gap CLOSED, `83a80c7`.** 1.3's four-levers prose develops claim 5 (three-not-knowings as churn's causes, by name) AND claim 9 (theses divide them, via the levers) in a BODY chapter. 1.3's labels → `[three-not-knowings-cause-churn, modeling-thesis, theses-treat-the-causes]` (3 = at cap): claim 5 SUBSUMES the old `churn-is-the-limit` label (1.1 keeps that claim's body home); the levers' alignment-thesis advancement left UNLABELED deliberately (Part 2 develops it; labeling would over-cap 1.3).
- **Also propagated (`83a80c7`):** the preface Modeling-Thesis inset takes the broadened canonical phrasing (models-first spine broadening `34e2a65` was already landed; context-window stays the immediate mechanism in the following paragraph). 2.6's census paragraph re-attributed "convert each recurring failure into a control" from "the Alignment Thesis" to **the governance-conversion loop** (concept-model reconciliation).
- **Gates:** `catalog.py validate` 0 issues at every commit · build green (126 chapter pages) · `catalog_tests.py` 28/0/3 + 10 audit-only (L5 new) · C7 watch-phrases clean · point-claim caps clean · figure lints clean · PDF 406pp content-integrity PASS · spine/claims `verify` in sync · derived artifacts (outline/outcomes/reverse_index) regenerated.
- **Deploy:** pushed `8a92395` → **Deploy Pages CI 30785297658 SUCCESS** → live-verified: landing + 1.3/2.1/2.3/0.1/3.1 + mage-book.pdf all 200; content spot-checks (engineered-loop inset on 1.3, "deliberately reduced" def-box on 2.1, `idx-def-governance-mechanism` on 2.3, canonical churn phrasing on 0.1) all present.
- **CUTS/MERGES:** nothing cut. One MERGE-class decision: the "governance-conversion loop" construct is realized by the existing `failure-to-mechanism` concept rather than a duplicate new concept (one object, one record). Pre-existing audit-only findings left as-is (the 5 original definitions' `def-*` landing homes + outcomes rows — the landing strip was removed by an earlier design decision; that reconciliation is a separate ratification, flagged here for the report-out).

## TASK 6 — MAGE follows from the machine — ✅ DONE + LIVE (`9090eb5`, CI 30787518868 SUCCESS)
Five commits, models-first per-item (`81adc44` model → `a2c0b6e` chapter+renumber → `c0f0290` reverse-index freshness → `cfdb9de` 6.2+6.3 → `9090eb5` voice trim; brief [task6-brief-260803.md](task6-brief-260803.md)). Core stance held: properties + mechanisms, zero fallible-teammate analogies (the one analogy used is a MATERIALS one — reinforced concrete — aimed at "a method is read off its material"); N=1 humility explicit in the chapter close ("a grounding case," implication-not-proof).

- **MODEL (the derivation), `81adc44`.** `concepts.json` `_hierarchy` gains a `substrate_derivation` block — chosen over a sibling model because the derivation IS the *why* under the hierarchy's theses level (one object, one file): **8 properties** (foundation-model: broad-semantic-reasoning · probabilistic-execution · bounded-reconstructed-context · cheap-repeated-cognition; harness: tool-mediated-action · interposition · lifecycle-visibility · parallel-execution) → **8 consequences** (agents-use-models, models-compact-structured, deterministic-envelopes, enforced-at-authority-boundaries, continuous-maintenance, oversight-saturates, policy-in-environment, + `locally-plausible-failure` added in `a2c0b6e` to back the table's 9th row) → **3 derives** (thesis-modeling ← broad+bounded+cheap; thesis-alignment ← probabilistic+mediated+parallel; governed-environment ← combines both theses). Every edge carries `spine_claims` reconciling to the argument spine (modeling-thesis, alignment-thesis, govern-the-environment, oversight-does-not-scale, sync-cost-removed). **L5 extended** (audit-only, consistent with rule-#55 discipline): unique property ids, closed groups, every consequence/derives id resolving against records + spine — PASS at every commit. Registry: `engineering-substrate` concept added to `index-terms.md`.
- **6.1 — NEW chapter `1.4-why-mage-follows-from-the-machine` ("Why MAGE Follows from the Machine"), `a2c0b6e`.** Chapter-sized per the section-word-cap discipline (the 1.2 precedent — 4–6pp can't be one section). Placement: immediately AFTER the theses land in 1.3's four-levers close (the directive's "as their derivation… or immediately after"), before the engineer's-seat chapter. Structure: opening = **6.5's author passage adapted to house voice** (para 1 → the substrate frame + `index-def: engineering-substrate`; para 2's theses-follow content moved to the closing section to keep say-it-once) with the reinforced-concrete concrete-anchor-first opening; then `The reasoner's properties` (4 bullets + promise-vs-catch tension), `What the harness adds` (4 bullets + read-as-control-points), `The engineering that follows` (the 7 consequences as prose + **the 6.4 9-row TABLE, caption VERBATIM**, `[short:]` split, `[ref:substrate-table]`-introduced, clean markdown table — overflow-safe by construction), `The theses follow` (Modeling ← broad+bounded+cheap · Alignment ← probabilistic+mediated+throughput · GEE = what the combination requires; scoped section-cap noqa for the inlined figure description).
- **Figure:** new hand-SVG `book/assets/substrate-derivation.svg` (design-token palette: fleet/governed/thesis/accent; two property panels → labeled derivation arrows → two thesis boxes → GEE box). `lint_figure_overflow` + `lint_design_token_drift` clean; the svg-fit heuristic's two initial findings (GEE-box width, label-on-arrow stroke-through) fixed before commit.
- **RENUMBER:** `1.4-the-engineers-seat` → `1.5-the-engineers-seat` (git mv); cross-refs updated: `4.2-the-skills` link, `2.3-the-governed-environment` footnote link, `landing-big-ideas.json` seat-moves `book_home`, stale `book/1.4-the-engineers-seat.html` git-rm'd. **Spine:** declared gains `1.4-why-mage…: [modeling-thesis, alignment-thesis, govern-the-environment]` (focus-cap 3; oversight-does-not-scale advancement left unlabeled deliberately — the preface + 6.0 own it); regen → 31 chapters, 88 edges, **0 zero-claim / 0 over-cap**. **Outcomes:** declared chapter outcome (verb `derive`) — the new chapter is a lesson PRIMARY, U3 gap closed for it (1.5's pre-existing U3 gap unchanged, pre-existing).
- **6.3 — Part-2 opening (2.1), `cfdb9de`.** 2.1 now opens on the directive's interposition frame ("A language model alone gives probabilistic recommendations. A harness turns some of them into actions. A governed engineering environment interposes between capability and consequence…"), back-linked to the 1.4 derivation, then the three governance materials (**soft conditioning · hard authority · feedback**) closing on the PROMOTED one-liner ("soft guidance goes in, deterministic guardrails constrain the actions, a deterministic envelope governs what gets admitted out" — promoted from its buried 6.0 site, which keeps its discursive twin). Scoped section-cap noqa (stack-figure description dominates; prose is 3 short paragraphs).
- **6.2 — Part-3 opening (3.1), `cfdb9de`.** New section `Why models are newly central`: the **three-way economic argument** (agents NEED models · CAN maintain them · harnesses can ENFORCE them) as bold-lead bullets, the **four-roles claim** (reasoning interface · architectural specification · derivation source · assurance surface), and the **executable source-of-truth PROMOTED into main-chapter prose** (agents read it · generators consume it · drift gates block divergence — "every view in this Part is that one architecture, worn five ways"); its `index-def` moved to the new defining paragraph, the trunk bullet now points back to it. The CAN-maintain bullet defers pricing to the existing MBSE-upkeep section (no restating). Spine labels for 2.1/3.1 unchanged (already carry the advanced claims).
- **Voice pass, `9090eb5`:** dash-density trim (2 sites) + a say-it-once fix ("not a proof" twice → once) in 1.4's close.
- **Gates:** `catalog.py validate` 0 issues at every commit · build green (127 chapter pages, 108 figures) · `catalog_tests.py` **30/0/1** (the one skip = plugin-validate inputs-unchanged; orphan-tracking + models-view link failures during the renumber fixed in-commit) · point-claim caps clean · term-tags clean · stray-comments clean · C7 watch-phrases clean · figure lints clean · PDF **410pp** content-integrity PASS (was 406).
- **Deploy:** pushed `9090eb5` → **Deploy Pages CI 30787518868 SUCCESS** (foreground-polled to conclusion) → live-verified: landing + 1.4 + 1.5 + 2.1 + 3.1 + book TOC + mage-book.pdf all **200**; content spot-checks (engineering-substrate def + verbatim table caption + derivation figure on 1.4, "interposes between capability and consequence" on 2.1, "Why models are newly central" on 3.1) all present.
- **DEFENSIBLE CALLS (made autonomously):** (1) derivation modeled INSIDE `_hierarchy` (not a sibling `substrate-properties` model) — same object, avoids a second SSOT for the same concepts; (2) new chapter placed at 1.4 (after 1.3's theses, before the seat chapter) — the derivation reads best right after the theses land, and the seat chapter's "map of the rest of the book" close stays the Part's exit; (3) the model gets an 8th consequence `locally-plausible-failure` so the verbatim table's 9th row (a composed hazard, not a raw property) has a model edge; (4) the 6.5 passage's second paragraph realized in the CLOSING section rather than the opening (say-it-once — the chapter derives, then collects); (5) new-chapter spine label capped at 3 claims, oversight-does-not-scale left to its existing owners.
- **CUTS/MERGES:** nothing cut. Pre-existing audit-only findings (5 definitions `def-*` landing homes, 9 outcomes-site rows, 2 O2 topic-sentences, 1.5+3.7 U3 gaps, 114 token-drift) left as-is — same set flagged in the core-concepts block for report-out.

## PHASE 2 (2a+2b) — chapter opening/closing analysis — ✅ DONE (analysis + model + audit-only check + FLAG LIST; NO prose refactored, per brief)
Models-first per the directive Part B Phase 2; brief [phase2-brief-260803.md](phase2-brief-260803.md). Commits `b6641e1` (model) + `8794909` (check) + this record. **2c refactor NOT performed** — the flag list below sizes it for the orchestrator's Opus follow-up.

- **2b — MODEL: NEW 7th sibling `chapter-shape`** (`chapter_shape_declared.json` → `chapter-shape.json` via `chapter_shape_model.py`, mirroring the spine's declared→generated shape). **Homing call (defensible, made autonomously):** a NEW sibling, not a field on outline/outcomes — the outline is derived-from-the-book on every run (no hand-authored home for an editorial judgment) and outcomes is pedagogical; the spine holds WHAT a chapter advances, this model holds HOW its first/last prose carries it. Schema per chapter: `opening{failure_question, answer, thesis_link}` each ∈ {explicit, implicit, absent} + `thesis_target` ∈ {modeling, alignment, both, argument-step, none}; `closing{kind}` ∈ {consequence, transition, synthesis | apparatus, mid-taxonomy, re-announcement}; evidence `note`; **anchors** (first/last 12 prose words). Joins: exemptions + per-chapter advances read LIVE from `argument_spine_declared.json` (never restated). **FLAGS DERIVED, never authored** (spine precedent): failing openings (any element `absent`), failing closings (kind ∈ bad set), thesis-spine mismatches (opening claims a thesis the spine labels don't carry). Exempt chapters assessed but never flagged (softer treatment per brief).
- **2b — CHECK: `check_chapter_shape` (CS1–CS5), AUDIT-ONLY first landing** (rule-#55 discipline, the spine/claims landing path; registered in `catalog_tests.py`; promotion after a clean session = queued follow-up). CS1 artifact drift · CS2 coverage exactly the outline's 32 chapters both ways · CS3 enums + uniqueness · CS4 `none`-iff-`absent` coherence · **CS5 anchor freshness — the 2c-dynamics guard:** anchors freeze the prose each assessment was made against; a rewritten opening/closing reddens that chapter until re-assessed (verified live: simulated rewrite of 2.4's closing → exactly 1 CS5 finding; restored). Regeneration never refreshes anchors — only editing the declared file does. **0 findings at HEAD.**
- **2a — every chapter's opening + ending read in full** (32 outline chapters; 6.2-glossary/6.3-about-the-author are outside the outline = apparatus, untracked). Opening scope = the untitled lead after the H1 (fallback: first section's prose when no lead exists — the 1.1 case); closing scope = the last section's prose, `Learn more` boilerplate excluded. **Grading call (defensible):** `implicit` (element carried by content, not stated) PASSES with a note; only `absent` flags — keeps the 2c worklist at real failures, with the 9 implicit-thesis chapters queryable in the model for optional one-clause sharpening. **Thesis-link reading:** chapters whose spine labels carry neither thesis-claim may satisfy element (3) via their argument step (`argument-step`), per the spine's claim taxonomy; a hard mismatch (opening claims a thesis the spine label lacks) flags separately.

**FLAG LIST (derived `flags` block of `chapter-shape.json`; = the 2c worklist, 9 items):**
- **Failing OPENINGS (6):**
  - `1.1-the-printer` — missing **failure/question + thesis-link** (no untitled lead AT ALL; opens mid-taxonomy into one-shot-vs-supervised-autonomy; the printer frame + fault-lies-in-instructions arrive only in the closing section). The heaviest single fix.
  - `3.2-the-logical-view` — missing **thesis-link** (view-chapter class: question + answer present; nothing says how the view advances a thesis — the frame rides at Part level in 3.1).
  - `3.3-the-process-view` — missing **thesis-link** (same class).
  - `3.5-the-physical-view` — missing **thesis-link** (same class).
  - `3.6-the-scenarios-view` — missing **thesis-link** (same class).
  - `4.2-the-skills` — missing **failure/question** (pure inventory framing: "a book of method ought to ship with batteries"; no failure/question motivates the chapter).
  - *2c sizing note:* 3.2/3.3/3.5/3.6 are ONE pattern — a one-sentence thesis clause per opening, matching each chapter's spine labels (3.4 shows the shape: "the view the people and agents who build the system reason through"). 1.1 needs a real chapter lead; 4.2 needs a motivating failure/question sentence.
- **Failing CLOSINGS (2):**
  - `2.4-lifecycles-and-runbooks` — **mid-taxonomy** (stops inside the runbook taxonomy at the pre-canned brief + a Learn-more link; no chapter-level consequence/transition/synthesis re-collecting lifecycles→runbooks→split).
  - `3.1-the-executable-zoo` — **apparatus** (ends on insets I1/I8/I9 + a where-the-remaining-insets-live navigation note; reference-matter tail, no close).
- **Thesis-spine MISMATCH (1):**
  - `5.4-the-road-to-mage` — opening explicitly claims the Modeling Thesis ("each step induces one more model… the models accrete"), but the spine labels 5.4 `[oversight-does-not-scale, seat-moves, grounded-in-one-case]` (at focus-cap, no modeling-thesis). 2c decides: relabel the spine (swap one claim) or reweight the opening. A REAL reconciliation item, left red-in-model deliberately.
- **NOT flagged (recorded as notes, queryable):** 9 non-exempt chapters carry an **implicit** thesis-link only (2.2, 2.3, 2.4, 2.5, 2.6, 3.4, 4.1, 4.3, 4.4) — pass-with-note; optional one-clause sharpenings if 2c wants them. `2.1`'s closing borders thesis-re-announcement but earns `transition` (hands off to the two thesis chapters + 2.6). Exempt-kind chapters all read cleanly for their kinds (0.1 preface, 0.2 apparatus, 1.2 overview, 3.7 end-of-part-synthesis, 4.5/6.0 discussion, 6.1 conclusion) — noted, not failed. **Exemplars worth imitating in 2c:** 4.6 (opening names both theses + maps them), 1.4/1.5/5.1–5.4 openings; the Part-3 `---`-kicker transitions + 3.6/5.3 closings.
- **Counts:** 32 assessed (7 exempt) · openings: 19 pass / 6 flagged (of 25 non-exempt) · closings: 23 pass / 2 flagged · 1 mismatch · implicit thesis-link: 10 non-exempt (the 9 pass-with-note above + 4.2, which is already flagged on the other element; artifact counter `openings_implicit_thesis`).
- **Gates:** `catalog.py validate` 0 issues · build green (127 chapter pages) · `catalog_tests.py` **28/0/3 + 11 audit-only** (chapter-shape new, 0 findings) · chapter-shape `verify` in sync · pre-existing audit-only set (18 views-audit findings: 2 O2, 2 U3, 5 def-*, 9 outcomes-site) unchanged, same set flagged since the core-concepts block.
- **Deploy:** pushed `55d47d5` → Deploy Pages CI run `30789120763` — the unauthenticated Actions API rate-limited mid-poll (20s polling burned the 60/hr IP budget; lesson: poll ≥60s or hit the live-site marker), so success was verified by the deploy's own observable: `/book-models/chapter-shape.json` flipped 404→**200** at 02:19 (an artifact only this push ships) + live curls all **200** (landing · models-view · 1.3 · 2.4 · 3.1 · mage-book.pdf) + the live artifact's `_counts` matching HEAD (32/7/6/2/1). Trailing docs-only record commit pushed after.
- ⇒ **NEXT (orchestrator, serial): 2c refactor (Opus)** — sized by the 9-item flag list above (4 of the 6 opening flags are one mechanical class); CS5 anchors will redden each rewritten chapter until its declared assessment is refreshed, which is the intended re-assessment forcing function. Promotion of CS1–CS5 to blocking after a clean session = queued follow-up (with AS-series).

## PHASE 2c — opening/closing refactor — ✅ DONE (all 9 flags → 0; models-first, per-group commits)
Opus prose-judgment follow-up to Phase 2. Brief [phase2c-brief-260803.md](phase2c-brief-260803.md). Five commits, models re-assessed + anchors refreshed after every prose change, `check_chapter_shape` driven to **0 flags** (0 failing openings / 0 failing closings / 0 thesis mismatches) and `check_argument_spine` kept green. Each fix appended a tight clause/lead/close in house voice — sharpening, not cutting.

- **FIX 1 — view-chapter thesis clauses (3.2/3.3/3.5/3.6), `b7a93fa`.** Each of the four view openings gained ONE sentence naming how the view advances a thesis, matching its spine labels (all four advance `[modeling-thesis, alignment-thesis]`), and VARIED so the four don't read as one template (house-style anti-uniformity): **3.2 Logical → Modeling** ("the representation the fleet reasons through to know what the system is: the Modeling Thesis at the grain of one view"); **3.3 Process → Alignment** ("a checker holds the running system to [the invariants], so a race cannot reach production unseen — the Alignment Thesis, read at the grain of concurrency"); **3.5 Physical → Modeling** ("written down as a placement model the fleet can read, that *where* becomes something an agent reasons over before it deploys"); **3.6 Scenarios → Alignment** ("the walk re-checks the other four against a real goal, [so] the scenario is where the models are held honest"). 3.4 was the exemplar of the shape (unchanged). Each appended mid-lead → opening anchors unchanged; `thesis_link` absent→explicit, `thesis_target` none→modeling/alignment (need ⊆ spine_advances, no mismatch). **openings-failing 6→2.**
- **FIX 2 — 1.1-the-printer real chapter lead, `561488a`.** 1.1 had NO untitled lead (opened straight into `## What this book is about`, mid-taxonomy on one-shot-vs-supervised). Added a two-paragraph lead that pulls the printer frame + fault-lies-in-instructions UP FRONT: para 1 names the failure (implementation abundant but individually unreliable); para 2 poses the question ("when an agent builds the wrong thing, whose fault is it?"), gives the answer ("treat the agent as a *printer*, not a coder … a bad build indicts the instructions and the environment, not the worker"), and states the argument role ("the premise everything after this chapter rests on"). Restructured, not duplicated: the lead FRAMES, the body sections ("The printer", "Whose fault is it?") DEVELOP the 3D-printer metaphor in full. Bonus: the following section's "Of course, not every programming task needs the machinery…" now reads as a concession to the lead instead of opening cold. `failure_question`/`thesis_link` absent→explicit; opening anchor refreshed.
- **FIX 3 — 4.2-the-skills motivating failure, `561488a`.** Opening was pure inventory ("a book of method ought to ship with batteries"). Prepended the failure the skills answer: "A method only helps while someone remembers to apply it. Left as prose in a book, it has to be re-taught to every fresh agent and every new project by hand, and a discipline that lives in memory rather than in the environment is the first thing velocity drops." (Truthful to 4.2's spine label `govern-the-environment` — policy in the environment, not remembered.) `failure_question` absent→explicit; anchor refreshed.
- **FIX 4 — 2.4-lifecycles-and-runbooks chapter close, `3c3c070`.** Closing stopped mid-taxonomy at the pre-canned-brief + a Learn-more link. Added a synthesis close re-collecting **lifecycle → runbook → pre-canned-brief** as "one instruction wearing three shapes," with the consequence that operating judgment "stops living in your head and becomes something the environment holds" — closing on a "who happens to be awake at 2 a.m." callback to the opening's 2 a.m. page. `closing.kind` mid-taxonomy→synthesis; anchor refreshed.
- **FIX 5 — 3.1-the-executable-zoo chapter close, `3c3c070`.** Closing ended on the boxed reference insets (I1/I8/I9) + a navigation note (apparatus tail). Added a real close AFTER the insets (the mechanical requirement — the model's closing = the last prose block; the boxed insets stay as trailing reference matter): "That is the trunk. The rest of this Part is the branches" — re-collects the shared machinery (executable source of truth, drift gate, derived edges, admission test, five-field template) and hands off to the five views, the Logical view first. `closing.kind` apparatus→transition; anchor refreshed.
- **FIX 6 — 5.4-the-road-to-mage thesis/spine mismatch, DECISION + reweight, `9186a1e` (+ `<this commit>` voice tweak).** The opening headlined a Modeling-Thesis claim ("each step induces one more model of the system, and the models accrete until the codebase can be reasoned about entirely through them") the spine labels `[oversight-does-not-scale, seat-moves, grounded-in-one-case]` (focus-cap 3, no modeling-thesis) do not carry. **DECISION: option (b) — reweight the opening — NOT (a) relabel the spine.** **Rationale:** all three current spine claims are genuinely 5.4's distinctive contribution (the job-title staircase co-coder→architect = **seat-moves**; the governance hinge "safe only because a control caught what delegation dropped" = **oversight-does-not-scale**/attention-per-class; the whole DocAble narrative = **grounded-in-one-case**). None can be dropped without weakening the spine's accuracy, and modeling-thesis is Part 3's job — advanced across 18 chapters — so 5.4's model-accretion line is a secondary strand, not its headline. Option (a) would have to SWAP OUT a genuinely-advanced claim to insert a secondary one: a net loss of spine truth. So I reweighted: the staircase thread now foregrounds "the seat climbs only because each step first minted the model or the control the next rung would need," and demotes model-accretion to an explicit supporting observation ("The models did accrete along the way. But the road this chapter walks is the climb of the seat, and the governance that made each rung safe to let go" — teeing up the governance inset that follows). Edited mid-lead → opening anchor unchanged; spine labels UNCHANGED so `check_argument_spine` stayed green; `thesis_target` modeling→argument-step cleared the CS mismatch.
- **MODELS-FIRST / CS5 discipline:** after every prose change, re-assessed the chapter in `chapter_shape_declared.json` (opening/closing grades + `thesis_target` + evidence note) and refreshed the frozen anchors via `chapter_shape_model.py anchors <slug>` → `regenerate` → `verify` (CS1 in sync). Mid-lead/mid-close appends (the view clauses, 4.2 prepend excepted, 5.4) left the first/last-12-word anchors unchanged; the new-first-word cases (1.1 lead, 4.2 prepend) and new-last-block cases (2.4, 3.1 closes) got refreshed anchors. **Final: `check_chapter_shape` 0 flags (0+0+0), `check_argument_spine` in sync (14 claims, 88 edges).**
- **CUTS RECORD:** ~0 cuts — this phase was sharpening, not cutting. One DEMOTION (not a cut): 5.4's model-accretion flourish moved from headline thread to supporting observation (content retained, emphasis moved). No chapters split/merged/removed.
- **Gates:** `catalog.py validate` **0 issues** at every commit (82 entries) · `book/build_book_html.py` green (127 chapter pages, 108 figures) · `chapter_shape verify` in sync · `argument_spine verify` in sync. Pre-existing audit-only set unchanged (114 token-drift; the 9 outcomes-site landing-row findings — the removed landing strip, flagged for report-out since the core-concepts block; 5 def-* homes; 2 O2; 2 U3).
- **Deploy + live SHA(s):** _(recorded on deploy below)_

## Phase 3 — catalogue → "Constructing the Governed Engineering Environment" (GEE 4-level) — 3a+3b+3c ✅ DONE

## PHASE 3 · 3a — catalogue cards

**Artifact:** [`book-models/catalogue-cards.json`](../../book-models/catalogue-cards.json) — declared→generated per the repo idiom: the hand-authored 9-field analysis lives in `book-models/catalogue_cards_declared.json`; `book-models/catalogue_cards_model.py` (`regenerate` / `verify` / `status`) JOINS each card with the entry's live INDEX.md census metadata (title · role · family · Form/Move/Model/Enf.) at generation time — the census is never restated by hand. `_provenance` header + `_note` (the 3a substrate for 3b) + `_counts` (coverage, per-role, family-guess distribution) included.

**Schema per entry** (keyed by entry id `role/family/mechanism`): `title`, `role`, `family`, `index_metadata{form,move,model,enf}`, `card{failure_class, engineering_obligation, solution_structure, guarantee, semantic_level, forces_tradeoffs, dependencies, known_uses, likely_parent_family [, abstract_name, note]}`. `semantic_level` records the RELATION modeled/enforced (per BEWARE FALSE MERGERS), never the enforcement technology; `abstract_name` supplied where the entry title is implementation-biased; `note` flags carding ambiguities for 3b.

**Count carded:** **82/82** (agent 28 · models-bridge 34 · product 20); `catalogue_cards_model.py verify` green, `catalog.py validate` 0 issues (entries untouched — READ-ONLY analysis), `book/build_book_html.py` green. Landed across 5 batch commits (recoverability discipline).

**Entries that resisted clean carding / flagged for 3b** (each also carries a card `note` or an inline flag in `likely_parent_family`):
- **`semantic-level-enforcement`** — an L1 PRINCIPLE candidate (a placement judgment that explains where other mechanisms sit), not a peer pattern; consider lifting out of the pattern set entirely.
- **`claude-md-rule-index` + `docs-hierarchy`** — deliberately two lenses on ONE artifact; 3b should treat as one mechanism with two views.
- **`pdf-model` + `office-models`** — fold as two known-uses of one One-Door pattern (the entries themselves frame it as defect-class consolidation).
- **`canonical-walkers`** — self-declared low novelty; demote to a component of the sanctioned-surface pattern.
- **`property-tests` + `fuzz-campaigns`** — the entries themselves say "two sides of one coin"; merge candidate into one generative-validation pattern with two poles (the fuzz entry's producer-dialect corpus + model-as-oracle synthesis is the distinctive canonical content).
- **`resource-pressure-gating`** — the directive flags the mediator family may SPLIT by forces/guarantees (fixed-capacity mediation vs adaptive pressure admission+shedding); this card is the adaptive pole. Also carries a ⚠️ as-built gap (load-pressure admission gate is a flagged extension).
- **`merge-train-mis-batching`** — the directive's own exemplar of exclusion criterion 10 (clever-but-distracts); the durable idea is "independence proved before integration," MIS one implementation.
- **`staged-deploy-gates`, `test-onion-tiers`** — standard practice with thin agentic delta (exclusion criterion 2 territory); breadth entries, likely L3/sidebar.
- **`symbol-anchored-traceability-graph`** — carded under drift/parity but is a strong CANONICAL-pattern candidate in its own right ("Derived Traceability"; unusually strong evidence discipline — designed from observed drift, validated on an independent drift set).
- **`codemod-first`** — a soft process discipline sitting uneasily in the product role; flag for placement.
- **`invariant-dag-execution-policy` + `control-substrate-dependency`** — same typed-edge-metadata reflex on different graphs; possible shared parent ("typed-edge semantics over modeled graphs").

**First-pass family-guess distribution (rolled up from `_counts.likely_parent_family_distribution`):** Executable-model zoo (the 18 is-a-model genres, each kept semantically distinct per BEWARE FALSE MERGERS) 18 · Executable source of truth (canonical + harness + read face + generation face) 4 · Model-derived assurance coverage 5 · Drift/parity gate (+ variants: cross-source, doc-corpus, test↔source, derived-traceability) 5 · One Door Enforced 5 · Complete mutation provenance 4 · Governance-of-governance 4 · Mediated resource admission 4 · Closed action vocabulary 3 (+ codemod-first adjacent) · Point-of-action policy delivery 3 · Staged admission gates 3 · Validated dispatch 2 · Authoritative lifecycle state 2 · Encoded operational judgment 2 · Fleet observability surfaces 2 · Generative validation 2 · singletons: Preservation invariant · Re-derived definition of done · Read-the-model-don't-copy-it · Caused-by provenance · Machine-enforced semantic policy · Conformance-to-external-spec · Health-conditioned admission · Fail-fast environment validation · Model-computed enforcement policy · Typed-edge semantics · Schema-governed planning artifacts · Governed knowledge base · Cost-stratified regression body · Bounded change-execution · 1 L1-principle candidate. Rough shape: **~20–24 candidate families/patterns before 3b's merge rule is applied** — consistent with the directive's expectation that the ~82 concrete mechanisms reduce to a materially smaller canonical set.
## PHASE 3 · 3b — cluster + classify — ✅ DONE (models-first, per-group commits; READ-ONLY wrt entries)

**Artifact:** [`book-models/catalogue-classification.json`](../../book-models/catalogue-classification.json) — the GEE 4-level classification of the 82 cards. Hand-authored analysis (not a declared→generated model file); `catalog.py validate` stays **0 issues** (entries untouched — a book-models analysis artifact only). Landed across 5 per-group commits (skeleton → CAP-KNOW → CAP-SYNC/COMPLETE/GOVERN-models → product → agent+finalize) for recoverability. A self-consistency check passes: every disposition resolves to an existing L2/L1, every L2's `canonical_card`/`merged_cards` are real card ids, each L2 has exactly one `keep-as-L2`, and all 82 appear exactly once.

**THE CLAIM (recorded):** the DocAble case produced **82** concrete governance mechanisms; comparative analysis by the card+cluster rule (merge iff the first six card fields substantially coincide and only known-uses differ; keep separate iff obligation OR guarantee differs even under identical impl tech) reduces them to **25 canonical pattern families** organized under **9 capabilities**, with the remainder retained as **56 variants / components / known-uses** and **1 lifted principle** — implementation count is not conceptual contribution.

**Demotion tally: 82 → 25 L2 (keep) + 2 merged-in + 54 demoted-to-L3 + 1 lifted-to-L1.**

**L1 principles (8) — the explanatory claims, not entries:** P1 Bind intent to structured models · P2 Reconcile models with reality · P3 Constrain action through sanctioned surfaces · P4 Re-derive evidence rather than trust reports · P5 Convert recurring failures into enforced controls · P6 Preserve provenance and accountability · P7 Model the governance environment itself · **P8 Enforce at the right semantic level** (the one entry LIFTED out of the pattern set — `semantic-level-enforcement` is a placement judgment that explains where every other mechanism sits, per 3a).

**GEE capabilities (9) — these ORGANIZE the catalogue, they are not entries:** CAP-KNOW maintain authoritative system knowledge · CAP-SYNC keep representations = reality · CAP-CONSTRAIN constrain where/how agents act · CAP-ADMIT admit or reject changes · CAP-COMPLETE establish completion on re-derived evidence · CAP-PRESERVE preserve product semantics · CAP-PROVENANCE track provenance + trace causes · CAP-MANAGE manage work/state/resources · CAP-GOVERN govern the control estate itself.

**L2 canonical patterns (25) discovered — name · rubric total · capability · override:**
- Executable Source of Truth · 20 · CAP-KNOW · Foundational (holds the 18-model "zoo" as subject-variants)
- Caused-By Provenance · 20 · CAP-PROVENANCE · Foundational + Awesome (5 components: mark/emit/cover/read + agent-side)
- Model-Derived Assurance Coverage · 19 · CAP-COMPLETE · Awesome (5 distinct obligation-variants)
- Derived Traceability · 19 · CAP-SYNC · Awesome (3a-elevated; the rung above parity — derive the edge so it can't drift)
- One Door Enforced · 19 · CAP-CONSTRAIN · Foundational (5 known-uses: pdf/office/redis/service-client/walkers)
- Drift / Parity Gate · 18 · CAP-SYNC · Foundational
- Read the Model, Don't Copy It · 17 · CAP-KNOW · Foundational
- Governance Graph · 17 · CAP-GOVERN · Coverage
- Computed Control Blast Radius · 17 · CAP-GOVERN · Awesome
- Re-Derived Definition of Done · 17 · CAP-COMPLETE · Foundational
- Validated Dispatch · 17 · CAP-ADMIT · Foundational
- Composed State-Machine Model · 16 · CAP-KNOW · Awesome
- Closed Action Vocabulary · 16 · CAP-CONSTRAIN · Foundational
- Machine-Enforced Semantic Policy · 16 · CAP-CONSTRAIN · Foundational (the operational face of P5)
- Preservation Invariant · 16 · CAP-PRESERVE · Coverage/Case
- Authoritative Lifecycle State · 16 · CAP-MANAGE · Foundational (the live-worktree-destruction scar)
- Mediated Resource Admission · 15 · CAP-MANAGE · Foundational (crit-1 exemplar; 3 cardinality variants)
- Staged Admission Gates · 14 · CAP-ADMIT · Foundational (5 rungs, incl. the evidence-bound commit gate)
- Generative Validation · 14 · CAP-COMPLETE · Awesome facet (fuzz+property merged; model-as-oracle is the content)
- Fleet Observability Surface · 14 · CAP-MANAGE · Coverage
- Governed Knowledge Base · 13 · CAP-GOVERN · Foundational (claude-md + docs-hierarchy merged — two lenses, one artifact)
- Conformance-to-External-Spec Engine · 12 · CAP-PRESERVE · Case/Coverage
- Encoded Operational Judgment · 12 · CAP-GOVERN · Coverage
- Adaptive Resource-Pressure Admission · 11 · CAP-MANAGE · Coverage (the split-out adaptive pole; sidebar-territory score, kept L2 for the family split)
- Point-of-Action Policy Delivery · 11 · CAP-MANAGE · Historical/Case (durable core = interposition; feed-forward/feed-back variants partly transient per exclusion crit 3)

Scores are diagnostic, not a cutoff: the 11–14 band (Adaptive Pressure, Point-of-Action, Encoded Operational Judgment, Conformance, Fleet Observability, Generative Validation, Staged Gates) are the print-if-breadth / sidebar candidates the overrides keep in for coverage or case value; 3c and the editor decide print-vs-online.

**Compositions / strong stacks (8):** model-coherence (Executable Source of Truth + Drift-Parity + Read-the-Model) · provenance+fidelity (One Door + Caused-By Provenance + Preservation Invariant) · specification+verification (Composed SM Model + Model-Derived Assurance) · safe-launch (Validated Dispatch + Closed Action Vocabulary) · evidence-staircase (Staged Admission Gates + Re-Derived DoD) · observe→react loop (Fleet Observability + Encoded Operational Judgment + Staged Gates) · resource-mediation pair (Mediated + Adaptive Resource Admission) · governance-of-governance (Governance Graph + Computed Blast Radius + Governed Knowledge Base).

**Hard calls / REFUSED false-mergers (the load-bearing guard):**
- **All "lints" NOT one pattern.** Machine-Enforced Semantic Policy (implementation ⊨ semantic policy), Drift/Parity Gate (model ⟷ reality), Caused-By Provenance's wiring lint (every verb → provenance, a coverage relation), and the mediator ban-lints (every call → the authorized seam) share the lint TECHNOLOGY but enforce four DIFFERENT relations — kept as four separate patterns.
- **All "models" NOT one executable model.** Executable Source of Truth holds the ~18 subject models as VARIANTS (each preserving its distinct relation in its disposition), but Composed State-Machine Model (temporal cross-machine legality), Governance Graph (control×control conflict), Computed Control Blast Radius (control→substrate), and Derived Traceability (join-web by derivation) were elevated to their own L2 because each expresses a distinct MECHANISM, not just a distinct subject.
- **Mediator family SPLIT by forces+guarantees** (directive-mandated): fixed-capacity Mediated Resource Admission (gate on COUNT; N=1/M=8/whole-sweep as cardinality variants) vs Adaptive Resource-Pressure Admission (gate on live CONDITION + shed-during) — NOT merged as "both control compute."
- **Model-Derived Assurance Coverage kept as ONE L2 with five DISTINCT obligation-variants** (denominator census / tier placement / assertion strength / per-node exercise / verification method) — the meta-move is shared; the obligations differ, so they are variants, not merges, and not five inventions.
- **Two deliberate merges honored:** property-tests ⇒ Generative Validation (self-framed "two sides of one coin"); docs-hierarchy ⇒ Governed Knowledge Base (two lenses on one artifact). Both per 3a.
- **Kept the vivid texture per "generalize the idea not the evidence":** every L2 record carries a `vivid_failure` + `concrete_impl` pointer (e.g. One Door ← the v172 tag-tree corruption ← PdfModel; Authoritative Lifecycle State ← the destroyed live worktree ← the agent registry) so 3c can preserve the scar + the DocAble implementation.
- **merge-train MIS batching** demoted (directive's own "clever-but-distracts" exemplar) — the durable idea "independence proved before integration" folds under Staged Admission Gates, MIS as one implementation. **canonical-walkers** demoted to a component of One Door (self-declared low novelty). **codemod-first** placed as the execution-mode face of Closed Action Vocabulary (resolving its uneasy product-role placement).

## PHASE 3 · 3c — GEE restructure executed — ✅ DONE + LIVE (`5810375`)

Opus flagship execution of the 3b classification. Internally staged, batch-emit, resumable. All commits
kept `catalog.py validate` at 0 and `catalog.py build` + `book/build_book_html.py` green.

**STAGE 1 — SCAFFOLD (`f99f65c`; anchor fix `59ef2ac`).** New root organizing page
[`constructing-the-gee.md`](../../constructing-the-gee.md) — the catalogue reframed as the **construction
kit for the Governed Engineering Environment**, titled *"Constructing the Governed Engineering
Environment"* · subtitle *"A catalogue of models, controls, compositions, and known uses."* It carries: the
SUPPLEMENT-2 opening passage adapted to house voice (Hemingway, capped em-dash density); the **reframed
claim** (82 concrete mechanisms → 25 canonical mechanisms under 9 capabilities, remainder as variants/known
uses); the **4-level ontology** explainer + the GoF contrast; the **8 L1 principles** (P1–P8, P8 =
`semantic-level-enforcement` lifted); the **9 capabilities** (KNOW·SYNC·CONSTRAIN·ADMIT·COMPLETE·PRESERVE·
PROVENANCE·MANAGE·GOVERN), each with its canonical L2 mechanism(s) written in compact pattern form (intent
· vivid failure/scar · concrete DocAble impl) and the folded variants/known-uses linked beneath it; the
**two borderline folds** as a named `#folds` sub-section; and the **8 compositions** (stacks) with joins +
why. Linked from the landing (a **4th way-in** card, `catalog.py`), README, and INDEX so the reachability
gate stays green. Entries left intact this stage.
- *As-built decision:* the GEE page IS the capability-organized view of the whole catalogue (canonical-vs-
  variant clearly marked, every entry grouped under its capability). INDEX.md keeps its role/family census
  tables (the strict `parse_census` regex + `build_census` depend on the role→family headings; capabilities
  cut across roles, so re-cutting the census by capability would be a high-risk rewrite for no gate gain).
  INDEX gains a "Read this as a construction kit" callout + link at the top. Defensible per the brief's
  explicit "choose the file-level approach that keeps validate 0 + reachability green."
- *Fix folded in (`59ef2ac`):* `render_md` escaped bare `<a id="…"></a>` anchor lines to visible text,
  which would have broken every intra-page `#cap-*` link (capability cross-links + compositions). Added a
  surgical `render_md` branch passing a bare-anchor line through raw. No existing catalogue content uses
  that line shape.

**STAGE 2 — CONSOLIDATE (10 commits, per capability + a folds commit).** Every one of the 82 entries now
carries a one-line **"Its place in the environment"** placement, inserted after its metadata card (schema-
safe; renders as `<p><em>…</em></p>` with a live link to the construction kit). L2 canonical entries name
themselves the canonical mechanism for their capability; L3 entries are reframed as a **variant / known-use
of `<parent L2>`** under their capability, preserved, subordinated. Driven by a deterministic stdlib script
carrying the full 3b disposition map (idempotent; `--check` audit).
- Per-capability counts (canonical L2 · variants demoted): **KNOW** 3·21 (`551edb6`) · **SYNC** 2·3
  (`d7cfcf8`) · **CONSTRAIN** 3·7 (`903f19a`) · **ADMIT** 2·7 (`a93822c`) · **COMPLETE** 3·4 (`0a6fde5`) ·
  **PRESERVE** 2·0 (`dd660cc`) · **PROVENANCE** 1·4 (`43119e3`) · **MANAGE** 5·6 (`c6af573`) · **GOVERN**
  4·2 (`9ef9962`). Totals: **25 L2 · 54 L3**.
- **Folds commit (`4fc99d2`):** the 2 merges + 1 lift. `property-tests` → **merged into Generative
  Validation** ("two sides of one coin"); `docs-hierarchy` → **merged into Governed Knowledge Base** ("two
  lenses on one artifact"); `semantic-level-enforcement` → **lifted to principle P8**. All 82 entries verified
  carrying the placement sentinel.

**THE TWO BORDERLINE FOLDS — distinction preserved.** `formal-invariant-verification` folds under
**Model-Derived Assurance Coverage** as the *proof* pole against the census's *exercise* pole (routes each
invariant to the checker its temporal shape demands; composes with the Composed State-Machine Model).
`model-graded-finding-severity` folds under **Read the Model, Don't Copy It** as a model-consuming gate
(severity = f(finding, change), computed once against the live component model). Both surfaced as a named
`#folds` sub-section on the construction-kit page, and each entry's placement line names its parent.

**CENSUS / MODELS — decisions (all consistent, gates green).**
- **Census marker unchanged at 82.** `catalog.py` derives `controls = len(entries)` and
  `check_census_tokens` enforces it; the restructure PRESERVED all 82 entries (nothing deleted), so the
  tree still holds 82 concrete mechanisms and the marker correctly reads 82. The "25 canonical / 9
  capabilities" reduction is an analytical framing carried in prose (GEE page · INDEX callout · README), not
  the entry count. Setting the marker to 25 would require deleting entries and would break the derived-count
  check — the wrong move. The census counts what is in the tree.
- **MODEL_NODES unchanged.** It organizes entries on the orthogonal governance-map axis (fleet/product/
  trunk spines); no entry was renamed, moved between roles, or deleted, so every slug still resolves and
  validate's model-map check ("every entry has a node home") stays green. No edit owed.
- **catalogue-views / reachability / INDEX** all regenerate green: `catalogue-views.html` reads the intact
  role/family census; the reachability gate passes (the new page is reached from the landing + README +
  INDEX); `check_index` passes.

**CUTS / MERGES RECORD.** This run **cut nothing** — it consolidated. Merge record: **2 merges** (property-
tests → Generative Validation; docs-hierarchy → Governed Knowledge Base) · **54 demotions** to variant/
known-use under a parent L2 · **1 lift** (semantic-level-enforcement → P8). All 82 entries preserved on
disk and in the census; the consolidation is expressed as the 4-level GEE structure over them, not by
deletion.

**PRINT-VS-ONLINE (noted for the author's later pass, NOT cut here).** All 25 L2 remain in the printed
catalogue. The rubric-11–14 band kept on Coverage/Case/Historical overrides — the print-vs-online refinement
is the author's editorial call: **Adaptive Resource-Pressure Admission** (11) · **Point-of-Action Policy
Delivery** (11) · **Encoded Operational Judgment** (12) · **Conformance-to-External-Spec Engine** (12) ·
**Governed Knowledge Base** (13) · **Fleet Observability Surface** (14) · **Generative Validation** (14) ·
**Staged Admission Gates** (14). These are the sidebar/online candidates a later pass may relegate.

**GATES (every commit).** `catalog.py validate` **0 issues** (82 entries: agent 28 · bridge 34 · product
20) · `catalog.py build` **0** (incl. the BLOCKING reachability/orphan gate) · `book/build_book_html.py`
**0** (127 chapter pages + appendix). Pre-existing AUDIT-ONLY set unchanged (114 token-drift; the 22 views-
audit findings — outline/reverse_index freshness, 2 O2, 2 U3, 5 def-*, 9 outcomes-site, 2 CLAIM-TOO-LONG —
the same set flagged since the core-concepts block; all non-gating).

**DEPLOY + live SHA.** Pushed **`5810375`** → **Deploy Pages CI SUCCESS** (foreground-polled to
completion; the deploy's own `catalog.py test` Tier-1 gate green 28/0, PDF content-integrity + size gate
green, CI's Tier-2 `--full` html-validate + axe + plugin-validate green). Live-verified on the published
site: landing · `constructing-the-gee.html` · `catalogue-views.html` · executable-source-of-truth ·
pdf-model · office-models all **200**; content spot-checks all present — the GEE title + adapted opening
passage + working `#cap-know` anchor + the "canonical mechanism for KNOW" L2 line + "The eight
compositions" on the construction-kit page, "The construction kit" 4th way-in on the landing, pdf-model
carrying its "canonical mechanism for CONSTRAIN" placement, and office-models carrying its "variant /
known-use of One Door Enforced" reframe.

**REMAINING — 3c follow-ups (deliberately scoped out; documented for a later deliberate pass):**
1. **Fuller L2 prose rewrite.** Stage 2 gave every entry its GEE placement + the GEE page gives each L2 a
   compact pattern statement (intent · vivid failure · concrete impl). The brief's richer per-L2 target —
   *one diagram · one model/code fragment · ≥1 alternative · clear limits* inline in each L2 entry — was NOT
   applied entry-by-entry (the entries were already written to good depth in prior phases; a full author-
   grade rewrite of 25 long entries is a deliberate editorial task, and it interacts with the print-vs-
   online cut above). The GEE page carries the vivid failure + concrete impl for each L2 today.
2. **Book-appendix GEE reframe (site⊇book reconciliation).** The construction-kit framing is a NEW site
   framing; the book (`book/`) already develops the GEE concept (2.3, the concept model, Part 3), but the
   book's **appendix** (`appendix-a/b/c/d/e`) still renders the flat catalogue. For strict "book coverage ⊇
   site framings," the appendix front-matter should adopt the same 4-level GEE ontology + capability
   grouping. Book build stays green today; this is an additive follow-up, not a regression.
3. **Promote the capability grouping into `catalogue-views.html`** (an optional second capability lens
   beside the role/model/enforcement lenses) if the author wants it in the interactive view as well as the
   GEE page.

## TASK 4 — durability modeling (obligation vs 2026-implementation) — CAPTURED for NEXT SESSION (directive Task 4); NOT acted this run.
## TASK 7 — harness / Agent-OS references (bibliography enrichment + VERIFY-FIRST) — CAPTURED post-deploy ([harness-references-capture-260802.md](harness-references-capture-260802.md)). 7 refs + cite the Gill LinkedIn pointer. Must confirm each arXiv ID/paper exists before citing (LinkedIn-sourced → hallucination risk); feeds Task 6 harness-derivation thread + §2.1. Do AFTER the run's final deploy.

## TASK 7 — harness references — ✅ DONE + LIVE (`95ead22`)
Executed 260803 per [task7-brief-260803.md](task7-brief-260803.md). All 7 refs VERIFIED (metadata corrected in the brief); benchmark figures handled per the guardrails.

- **8 entries added to `references.bib` SSOT** (new "Harness / Agent-OS engineering literature" section), re-rendered via `render_citations.py` (Typst/Hayagriva chicago-notes → 31 entries in `citations.json`):
  - `zhong-zhu2026` (@misc, arXiv:2605.13357) · `lee-metaharness2026` (@misc, arXiv:2603.28052) · `hanlee-harness2026` · `reganti2026` · `young-anthropic2025` · `zaharia-omnigent2026` · `tan-thinharness2026` · `gill-agent-os2026` (the surfacing LinkedIn pointer).
  - **Metadata corrections applied:** Han Lee title = "Hidden Technical Debt of AI Systems: Agent Harness"; Gill date = **July 15, 2026** (not Jul 14). Full ISO `date` on every web source, so Chicago renders the day (Han Lee "May 8, 2026", Young "November 26, 2025", Zaharia "June 13, 2026", Gill "July 15, 2026"); the two arXiv @misc render year-only (house idiom).
- **Weave (light, durable principles only):**
  - **1.4 § "What the harness adds"** — one grounding paragraph (new point `the-substrate-framing-is-an-emerging-consensus`): the model–harness–environment framing MAGE derives is now an emerging research+industry consensus. Cites `zhong-zhu2026` (triad: capability is a system property, not the model alone), `lee-metaharness2026` (the harness as a designed/optimizable variable), `young-anthropic2025` (**subtraction principle** — a harness component encodes an assumption about what the model can't yet do, and expires as models improve; pairs with the durability thread), `tan-thinharness2026` (**thin harness, fat skills**). Keeps MAGE's distinct contribution explicit: "MAGE stands on this literature and supplies what it leaves open: the engineering method the substrate implies, once the environment … is itself governed."
  - **2.1 § "The four layers"** — one grounding paragraph (new point `the-harness-layer-has-a-named-taxonomy`): the **framework / harness / agent-OS taxonomy** (`gill-agent-os2026; reganti2026`), the **harness-as-OS analogy** (`hanlee-harness2026`), and the **meta-harness** (`zaharia-omnigent2026`). Closes: "This book says *harness* for the runtime layer throughout, and treats the agent OS as the same idea drawn wider."
  - All 8 keys are cited, so all 8 appear in the end-of-book **Bibliography** (union of cited keys). `book coverage ⊇ site framings` respected (no new site framing introduced).
- **⚠️ BENCHMARK-CLAIM DECISIONS (all volatile 2026 figures OMITTED — durable principle woven instead):**
  - **"LangGraph → Top-5 on TerminalBench 2.0 by changing only the harness" — OMITTED.** Real attribution is LangChain's `deepagents-cli` (52.8%→66.5%, same model), not LangGraph; rather than repeat a mis-attributed figure, wove the *principle* (harness as a tunable variable) with no number.
  - **"76.4% on TBench-2 / 4× fewer tokens" — OMITTED.** The line conflates two different Meta-Harness experiments (76.4% = Opus 4.6 on TBench-2; 4× tokens = a separate text-classification benchmark). Cited `lee-metaharness2026` for the qualitative claim (a harness that optimizes itself) with no figure.
  - **"Haiku outranked Opus with a better harness" — OMITTED.** No pinned primary source; not stated.
- **Gates:** `render_citations.py` 31 entries OK · `catalog.py validate` 0 (82 entries) · `book/build_book_html.py` green (127 chapter pages) · 7 CITE-* gates **PASS** (resolve/fresh/mirror/symbology/parity/scholar-meta/orphans — 0 orphans) · point-claim-word-cap: both new points ≤10 words · term-tags clean · deploy-github pre-push 28/0/3 gates.
- **Commits:** `ee42b86` (bib + citations.json) · `95ead22` (weave + rebuilt 1.4/2.1/bibliography HTML). **Live SHA `95ead22`.**
- **CI + live verify:** Deploy Pages run **30801234153** deployed `95ead22` (the live Pages site now serves it — definitive). Live-verified: `1.4-why-mage-follows-from-the-machine.html`, `2.1-the-agent-stack.html`, `bibliography.html` all **HTTP 200**; all **8 new entries present** in the live end-of-book Bibliography; citation notes render (e.g. live 2.1 shows the Gill note "Gurbinder Gill, 'The Rise of the Agent OS: …,' LinkedIn, July 15, 2026" beside the framework/harness/agent-OS taxonomy sentence); Scholar `citation_reference` head-meta live for the new keys (BIB-8). (Console-error + Tier-2 axe/html-validate gates made the Pages run ~20 min; healthy, not hung.)

## CUTS RECORD (all phases) — running
- **Phases 1, 2c, Task 6, core-concepts:** nothing cut — sharpening + additions only (see each block; one
  DEMOTION, 5.4's model-accretion flourish moved from headline to supporting observation).
- **Phase 3 · 3c (catalogue → GEE construction kit):** **nothing cut.** The restructure CONSOLIDATED 82
  concrete mechanisms into 25 canonical mechanisms under 9 capabilities via **2 merges + 54 demotions-to-
  variant + 1 lift-to-principle** — every entry preserved on disk and in the census (still 82). Details in
  the "PHASE 3 · 3c" block above.

---

## SPINE-TUNE + SYNC — ✅ DONE (pre-deploy; live SHA below)

Brief: `book/_design/spine-tune-and-sync-brief-260803.md`. Models-first: tune 6 over-claiming spine statements → propagate to the exact `advanced_by` chapters. Commit-per-group.

### STEP 1 — the 6 statement edits (`argument_spine_declared.json`, regen `argument-spine.json`)
1. **`fault-lies-in-instructions`** → "Treat a bad output first as evidence about the instructions, representation, task boundary, or environment — not automatically as a fixed capability ceiling." (23 w)
2. **`churn-is-the-limit`** → "Ungoverned, the project decays into churn: an increasing share of effort goes to rediscovering context, undoing recent work, and reconciling inconsistencies rather than advancing the system." (26 w — matches the Churn definition shape.)
3. **`alignment-thesis`** → "Enforced mechanisms hold implementation to declared intent across later changes; where possible, constrain the action space so the wrong move is unavailable, and where prevention is incomplete, install sensors that detect divergence." (32 w — see word-cap decision.)
4. **`sync-cost-reduced`** (RENAMED from `sync-cost-removed`) → "The sync economics changed. Agents sharply reduce the recurring labor of keeping models and implementation reconciled." (16 w)
5. **`mage-becomes-practical`** → "This makes serious model-based software engineering practical: models can become the working language through which agents reason and engineers specify, predict, and govern." (23 w — universal-language NOT asserted as settled; it stays the larger discursive thesis.)
6. **`seat-moves`** → "The engineering lifecycle remains; the allocation of work changes. Agents occupy much of implementation, while human effort concentrates on intent, architecture, model authorship, validation, and judgment." (26 w)

### ID RENAME `sync-cost-removed` → `sync-cost-reduced` (author-confirmed) — every join-key updated
- `argument_spine_declared.json`: spine entry id + `chapter_advances` (0.1-preface, 2.2, 3.1).
- `book-models/chapter-shape.json` `spine_advances` (3 sites) — via `chapter_shape_model.py regenerate` (join-derived).
- `book/data/concepts.json` `spine_claims` (2 sites: `_hierarchy` resulting-system row + `continuous-maintenance` construct).
- `book-models/argument-spine.json` regenerated. Grep for old id across repo = 0 (excl. brief + this log).

### WORD-CAP DECISION
`argument_spine_model.py` `WORD_CAP` **26 → 32**. Only `alignment-thesis` (32 w) exceeded 26; its thesis-plus-two-hierarchical-moves (constrain-first; sense-where-prevention-incomplete) is the whole correction and does not survive compression. Per the brief's escape hatch, raised the cap minimally to hold the author-exact wording rather than mangle the claim; comment updated to note alignment-thesis sets the cap. All other 5 statements ≤ 26. (Also fixed a stale `<=24` in the declared `_note` → `<=32`.)

### STEP 2 — `catalog.py spine [<claim-id>|<chapter-slug>]` subcommand
Mirrors the `claims`/`concepts`/`definitions` siblings; reads the generated `argument-spine.json`; stdlib-only. No arg → the 14 claims in order with advance-counts; a claim-id → statement + its `advanced_by` chapters; a chapter-slug or number prefix (e.g. `2.3`) → the claims that chapter advances. `--json` for each. Subparser + dispatch wired. `validate` stays 0.

### STEP 3 — surgical book-sync per claim (via `advanced_by`)
- **A · fault-lies-in-instructions** (0.1, 1.1, 4.5, 6.1): dropped the printer *absolutism* — 1.1 opening frame ("not the worker") + whose-fault section ("every single time… my fault", "build essentially anything") and the preface through-line ("the fault is in the instructions, not the machine", "build essentially anything"). Now: a bad build is FIRST evidence about instructions/representation/task-boundary/environment, not by reflex a fixed ceiling; printer metaphor kept. **4.5 + 6.1: no fault-absolutism prose (grep clean; 6.1's printer lines are the metaphor identity — kept).** Model reconcile: claims-model `printer-not-coder` statement + `contradicted_by` softened to the same posture (regen `claims.json`).
- **B · churn-is-the-limit** (0.1, 1.1): preface premise no longer collapses churn to context-window overflow — churn = decay into rework (per the Churn definition), context named the *sharpest driver*, not the definition. **1.1: no context-overflow-churn prose (nothing to tighten).**
- **C · alignment-thesis** (0.1, 1.4, 2.2, 2.3, 2.5, 3.2–3.6, 4.3, 4.5, 4.6): **chapters already hierarchical** — 2.3 ("you do not reach for a sensor first" + the residual-as-remainder), preface thesis blockquote ("prevented, OR made visible"), 1.4 (mechanisms hold work to intent). No chapter edit. Over-claim lived on model surfaces: spine statement (STEP 1) + concepts.json `thesis-alignment` note (retuned off "a quality goal splits into constraint+sensor" → hierarchical) + **landing Big-Idea 4** (`landing-big-ideas.json`) retuned: title "A quality goal splits into a constraint and a sensor" → "Hold intent with a mechanism: prevent first, sense the rest"; claim/more to the hierarchical form (claim within the 26-w cap).
- **D · sync-cost-reduced** (0.1, 2.2, 3.1): tightened "cost removed / for free": preface "Agents remove that cost" → "cut that recurring cost sharply" + added "someone still authors the model and the gate"; 2.2 "the thing agents just removed" → "just made cheap" and "Agents removed that cost" → "cut that recurring cost sharply"; 3.1 heading "the one a fleet pays for free" → "now pays cheaply" + added "someone still authors the model, the reconciliation rule, and the gate — what shrank is the standing maintenance, not the design."
- **E · mage-becomes-practical** (0.1, 3.7, 4.4, 6.0, 6.1): **no chapter edit** — the universal-language claim is legitimately EARNED discursively (6.0 §"Models as the universal language", 6.1 scoped "thin evidence… I keep the claim scoped") and stated as thesis in the preface; the brief protects the discursive argument. Model reconcile: claims-model `models-are-universal-language` "software could not afford them until agents **removed** the sync cost" → "**cut the recurring** sync cost" (sync-cost consistency); the universal-language assertion itself kept as the larger book thesis (regen `claims.json`).
- **F · seat-moves** (1.5, 4.5, 5.4, 6.0, 6.1): **no edit** — every site already NAMES the allocation: 1.5 (SDLC→SELC, "developer's seat reassigned to the fleet; engineer keeps requirements/spec/design/validation"), 5.4 (the staircase — co-coder→architect; agents take tactics, human keeps strategy), 6.0 §"The judgment moved, and it moved toward you" (framing/abstraction/architecture/governance), 4.5 + 6.1 ("judgment is the scarce resource / the part that stays yours"). Model surfaces (claims `seat-moves-not-lifecycle`, landing Big-Idea seat-moves) already the named SELC form. The opaque compact version lived only in the spine claim (fixed STEP 1).

### RECONCILE ledger (tuned claims ↔ concept/definition model)
- claim 4 ↔ **Churn def** (`definitions.json`): now same shape (increasing share of effort → rediscovering context / undoing / reconciling rather than advancing). ✅
- claim 8 ↔ **Alignment-Thesis + Governance-mechanism defs**: concepts.json `thesis-alignment` note retuned to hierarchical; Governance-mechanism def (four classes, prevention/detection = the move axis) already consistent — untouched. ✅
- claim (mage) ↔ **universal-language** master thesis: kept as the larger book claim; only the "removed sync cost" wording reconciled. ✅

### GATES (pre-deploy, all green)
`catalog.py validate` **0 issues** · `check_argument_spine` (AS1–AS7) **PASS** · `check_chapter_shape` (CS1–CS5, anchors fresh — edits all in chapter bodies, not the anchored lead/closing) **PASS** · `check_concepts_hierarchy` **PASS** · `check_claims_model` (C1–C7) **PASS** · `book/build_book_html.py` **exit 0** (127 chapter pages).
- **Coordination note:** `book-models/outline.json` + `reverse_index.json` (book-prose-derived) left un-regenerated — their views-audit freshness finding is **audit-only / non-gating**, was already stale on `main` from the concurrent chapter-restructure work (new ch 1.4 + renumber), and is owned by the prose-model agent; regenerating would sweep nothing from worktrees but risks colliding with that agent's own regen commit. The published models-view reads `argument-spine.json` (freshly regenerated), so the tuned spine statements publish correctly.

### Commits (per group)
`2e6ab22` STEP 1 (6 statements + rename + cap) · `5c9fffa` STEP 2 (spine subcommand) · `1cd04f0` STEP 3 A+B (fault + churn prose + claims reconcile) · `0eaee21` STEP 3 C (landing alignment slot) · `7c9cfc9` STEP 3 D (sync-cost prose) · `fa296ad` STEP 3 E (universal-language claim reconcile).

### Live SHA
`91f59bf` — pushed to origin/main; Deploy Pages CI **success**; touched pages + models-view all HTTP **200**; live content verified (3.1 "now pays cheaply", 1.1 "not, by reflex, as a fixed ceiling", landing Big-Idea "prevent first, sense the rest", published `argument-spine.json` carries `sync-cost-reduced` + the tuned alignment statement).

---

## CLAIM-HEALTH SENSORS — ✅ DONE (models-first, audit-only-first; overmapping audit = PROPOSALS for author sign-off)

The spine↔book map was bidirectional (AS5 coverage + AS1 drift) but had no DYNAMIC sensors. Added three, all audit-only-first (0 structural findings at seed, mirroring AS1–AS7 / CS1–CS5). The depth + overmapping surfacing signals are REPORTS in the artifact `flags` block (never gate); AS8 freshness + AS9 exemptions are audit-only structural findings (a follow-up promotes after a clean session). No label changes or prose rewrites applied — the overmapping audit is PROPOSALS only.

### Sensor 1 — UNDERmapping (claim-depth), report flags
- **`thin_claim_gaps`**: a non-exempt claim advanced by **0 chapters** (a real gap). **None at seed.**
- **`thin_claims_front_loaded`**: a non-exempt claim advanced **only within Part 0/1** (`body_depth == 0`) — stated up front, never re-advanced in the body.
- **`claim_exemptions`** (closed enum `CLAIM_EXEMPT_REASONS = front-loaded-by-design | bridge`; validated by **AS9**) — the claim-side analogue of `chapter_exemptions`. Seeded with the two genuine premises the brief named: **`abundant-implementation`** + **`fault-lies-in-instructions`** → `front-loaded-by-design` (both actually span to Parts 4–6, so they don't currently flag; the exemption arms the mechanism + records intent).

**THIN-CLAIMS list (for the author):** three claims are front-loaded (Part 0/1 only, body-depth 0):
1. **`churn-is-the-limit`** (claim 4) — `0.1-preface, 1.1-the-printer`. The brief's known case.
2. **`three-not-knowings-cause-churn`** (claim 5) — `0.1-preface, 1.3-loops-and-models`.
3. **`theses-treat-the-causes`** (claim 9) — `0.1-preface, 1.3-loops-and-models`.

All three are the churn-diagnosis / thesis-bridging steps: stated in the front-matter + the motivating Part-1 chapters, then assumed by the body rather than re-advanced. Author's call whether each is (a) genuinely front-loaded-by-design → add to `claim_exemptions`, or (b) a real thin spot that wants a body chapter to re-advance it. `theses-treat-the-causes` is a candidate for the `bridge` reason (it divides the not-knowings across the two theses rather than earning its own chapters).

### Sensor 2 — OVERmapping flag + AUDIT (the load-bearing judgment)
**Flag** (`overmapped_claims`, `OVERMAP_CAP = 10`; claim-side symmetry of the chapter >3 over-cap): flags **`modeling-thesis` (18)**, **`alignment-thesis` (13)**, **`govern-the-environment` (11)** — a clean gap to the next-broadest claim at 7. The flag never gates; it names the claims whose breadth is worth re-examining chapter by chapter.

**AUDIT of `alignment-thesis`'s view chapters 3.2–3.6** (the brief's target), applying the author's discriminator — *introducing a representation → Modeling (claim 7); explaining how correspondence/policy is mechanically MAINTAINED → Alignment (claim 8); a chapter that presents a model and merely MENTIONS its drift gate advances Modeling, not Alignment.* A sharpening emerged: a model's **(d)-slot drift/parity lints keep the MODEL equal to the code** — that is Modeling's own drift-checking, NOT runtime Alignment. Alignment is a chapter whose teaching is holding the running SYSTEM to intent (constrain the action space / install divergence sensors).

Key finding on the **Phase-2c thesis-clauses**: the brief asked whether the added clauses now OVER-claim Alignment. They do **not** — the clauses are honest. In **3.2** and **3.5** the Phase-2c clause itself says **Modeling** ("the Modeling Thesis at the grain of one view" / "…reaching the one view the others cannot see"); it is the **[modeling, alignment] LABEL** — applied uniformly to all five view chapters — that over-reaches. So the correction is to the label, not the prose.

**Label-correction PROPOSALS (for author sign-off — NOT applied):**

| Chapter | Label now | Phase-2c clause | Verdict | Proposal | Confidence |
|---|---|---|---|---|---|
| **3.2 Logical** | modeling + alignment | **Modeling** ("Modeling Thesis at the grain of one view") | Introduces the service-flow model + domain registries (representations); the (d)-slot parity lints keep the model↔code honest; the generated access policy is one line. Frame = "what the system **is**." | **Drop alignment → Modeling-only.** Prose clause already says Modeling; the label is the over-claim (no prose change needed). | HIGH |
| **3.3 Process** | modeling + alignment | **Alignment** ("Alignment Thesis…at the grain of concurrency") | Core teaching **is** runtime enforcement — checkers hold the running system to invariants under interleaving (formal invariant verification, the deadlock ordering lint, single-writer coverage as a finding) — AND it introduces the state-machine + sync model. | **Keep both.** Clause matches; both theses genuinely carried. | — |
| **3.4 Development** | modeling + alignment | *(no Phase-2c clause)* | Frame = "how the source is **organized**" (the map = Modeling). Checks = reverse-mapping (model↔reality drift = Modeling's own check) + boundary lint + rule-index freshness. The one alignment thread is boundary-soundness (a real constraint on what a file may touch). | **Drop alignment → Modeling-only** (Modeling-primary). Author may keep both for the boundary-lint constraint. | MEDIUM |
| **3.5 Physical** | modeling + alignment | **Modeling** ("Modeling Thesis reaching the one view the others cannot see") | Introduces the deployment-topology + invariant-DAG + substrate-dependency models; checks = deploy parity (model↔code) + layer/load-edge lints (the model's own invariants). Frame = "where the parts **live**." | **Drop alignment → Modeling-only.** Prose clause already says Modeling; the label over-claims. | HIGH |
| **3.6 Scenarios** | modeling + alignment | **Alignment** ("Alignment Thesis turned back on the views themselves") | Core teaching = validation / holding-the-views-honest (journey task-closure's teeth — a flow-only closure on a major journey is a build finding; the coverage-floor gate; call-site drift lints) — AND it introduces 5 models + the flagship join. | **Keep both.** Clause matches; both theses carried. | — |

**Payoff if the author accepts 3.2 + 3.5 (+ optionally 3.4):** `alignment-thesis` advance count drops 13 → 11 (→ 10 with 3.4), which clears its own overmapping flag. `modeling-thesis` (18) and `govern-the-environment` (11) remain flagged for a future overmapping pass — noted, not audited here.

### Sensor 3 — FRESHNESS (AS8, the CS5 analogue)
Each declared claim carries a **`reviewed_hash`** — the 12-hex SHA-256 of the `statement` wording its chapter labels were reviewed against. **AS8** re-hashes the current statement and reddens a claim whose wording changed since review (its advancing-chapter labels may no longer hold); a re-review updates the hash (editing the declared file), and regenerating the artifact never refreshes it. **Seeded at the current post-sync state → 0 stale.** `argument_spine_model.py hashes` prints each claim's current hash for re-seeding.

### Wiring
- Model: `argument_spine_declared.json` (+`claim_exemptions`, per-claim `reviewed_hash`), `argument_spine_model.py` (constants `OVERMAP_CAP`/`FRONT_PARTS`/`CLAIM_EXEMPT_REASONS`; derived `body_depth`/`front_loaded`/`overmapped`/`fresh`/`statement_hash`; `flags()` claim-side keys; `structural_findings` AS8+AS9; `_counts`+`taxonomy`; CLI `hashes` + health in `spine`/`flags`). Regenerated `argument-spine.json`.
- Tests: `tests/book_models.py check_argument_spine` docstring → AS2–AS9 (still `audit_only=True`).
- `catalog.py spine` surfaces the per-claim health suffix (`[front-loaded]` / `[OVERMAPPED]` / `[exempt:…]` / `[STALE]`) + body-depth.

### GATES (all green)
`catalog.py validate` **0 issues** · `check_argument_spine` (AS1–AS9, 0 structural findings at seed; 3 front-loaded + 3 overmapped are report flags) **PASS** · `check_chapter_shape` (CS1–CS5) **PASS** · `check_concepts_hierarchy` **PASS** · `check_claims_model` (C1–C7) **PASS** · `book/build_book_html.py` **exit 0** (127 chapter pages).
- **Coordination note:** `book-models/outline.json` + `reverse_index.json` show an **audit-only / non-gating** freshness finding owned by the prose-model pass (pre-existing on `main`); left un-regenerated per the brief. The published models-view reads the freshly-regenerated `argument-spine.json`.

### Commits (per group)
`2136290` SENSORS (declared + model + artifact + tests + catalog spine health).

### Live SHA
`5eb21f1` — pushed to origin/main (deploy gate 28/28 passed, 0 failed); GitHub Actions building Pages (not blocked on per author directive). Deployed tip carries the sensors (`2136290`) + this record (`5eb21f1`); the published models-view reads the freshly-regenerated `argument-spine.json`. (This SHA-fill is a doc-only follow-up.)

## LoC/VELOCITY REFRESH — ✅ DONE (repo-derived headline numbers, 2026-07-23 → 2026-08-03)

Refreshed `book/data/metrics.json`'s repo-derived fields from FRESH runs of the sanctioned tools on the
parent repo at HEAD `ce0bde110fbb` (2026-08-03): `tools/dev/run-cloc.py --json` (categorized LoC) +
`talks-and-notes/history-mining/repo-activity-histogram.py --metric both` (commits/week). No measurement
reinvented; AUTHORED figures (cost model, corpus, per-course, vendor, model/mechanism counts,
missing-model pilot) untouched.

### Old → new field table (tool-output field each maps to)

| field | old (2026-07-23) | new (2026-08-03) | tool field |
|---|---|---|---|
| `prod_loc` | 490,231 | **501,094** | `purpose_rollup["Production Code"].code` |
| `support_loc` | 1,420,335 | **1,505,737** | `ratio_table.support_apparatus.code` (= tests + lints + load-bearing docs + agent-infra + tools) |
| `iac_loc` | 8,446 | **35,323** | `purpose_rollup["Infrastructure as Code"].code` ⚠️ see note |
| `system_model_loc` | 7,380 | **28,507** | `purpose_rollup["System-model meta-files"].code` ⚠️ see note |
| `total_loc` | 2,593,580 | **2,824,878** | `system_total_raw.SUM.code` (whole-tree RAW — verified: the old 2.59M is the raw figure; the tool's `system_total_semantic_code` (2,083,089, excludes snapshot docs) is a DIFFERENT definition, noted in provenance but not adopted) |
| `support_ratio` | 2.9 | **3.0** | `ratio_table.support_apparatus.x_prod` |
| `commits_total` | 22,024 | **23,215** | histogram total (20 full weeks) |
| `study_weeks` | 19 | **20** | histogram window (2026-03-12 → 2026-07-23 week-starts, through 07-29) |
| `study_window` | March–July 2026 | March–July 2026 (unchanged — last full week still ends in July) | — |
| `commits_per_week` | 1,000 | 1,000 (kept — sustained-rate figure; fresh 20-wk mean 1,161/wk sits inside the stated ~1,000–1,400 band) | — |
| `commits_per_day` | 200 | 200 (kept — sustained-rate figure, unchanged by fresh data) | — |
| `peak_week_commits` | 3,329 | 3,329 (unchanged — same peak week, 2026-05-21) | — |

**Sanity notes.** prod_loc +2.2% and commits_total +1,191 over ~11 days: plausible organic growth. The
`iac_loc`/`system_model_loc` ~4× jumps are NOT organic: a category re-partition landed in `run-cloc.py`
(commit `3070f2f0b6`, 2026-07-23 19:18, AFTER the baseline run) that carved previously-UNCOUNTED
`deploy/**` production source + top-level `system-models/*.py` modules into those two categories — a
coverage fix in the tool. Recorded in the refreshed `_loc_provenance` note. The old `_loc_provenance`
gloss "support = everything except production" was inaccurate (raw−prod ≠ 1,420,335); corrected to the
tool's actual rollup definition.

**Provenance bumps.** `_loc_provenance` + `_commit_provenance` dates 2026-07-23 → 2026-08-03; embedded
numbers refreshed; parent tree SHA `ce0bde110fbb` added to both.

**data-claims.** No `holds` entry pins any refreshed number (`velocity` holds is empty) — no update needed.

**Chart-regen disposition: ⚠️ FLAGGED — numbers-only refresh; `velocity-commits-per-week.svg` NOT regenerated.**
The SVG landed as a one-off matplotlib export (`92c0130`, 2026-07-25) and was then post-processed twice
(a11y `<title>/<desc>/role` in `eb21dd8`; palette re-token per the figure-fix wave). No committed
generator reproduces the current style — the histogram tool's `--plot` emits differently-styled PDFs
(`#4C72B0`, no a11y metadata, no book palette), so a regen from it would ship a restyled/mismatched
figure. The chart now lags the data by one week (through 2026-07-16 vs 2026-07-23); "velocity regen" is
already queued in the deferred figure-fix wave (HANDOFF-skill-agent-260731 NEXT-PUBLISH notes) — fold the
data bump into that pass.

**Gates.** `catalog.py validate` **0 issues** · parent `tools/lint/lint-metric-provenance-resolves.py`
**0 findings** · `book/build_book_html.py` **exit 0** (127 chapter pages; token consumers 1.2 / 5.2 / 5.3
re-rendered).

### Live SHA
`64f3dbf` — pushed to origin/main (deploy gate green: validate 0 + build + test suite + PDF integrity gate all passed); GitHub Actions building Pages (not blocked-on per brief). Live curl 200 at push time (still serving the prior build mid-CI — the refreshed numbers land when the Actions run completes). Untracked sibling briefs left unstaged by design.

## STUDY-DESIGN v2

The empirical study-design doc is committed as the **pre-registration of record** at
`book/_design/evidence-study-design-260803.md` (v2, 260803 — the author's red-pen rulings folded
into the v1 draft; nothing measured yet). Key deltas from v1: window periodization is now FOUR
windows (prototype Mar 12–Apr 9 / mechanization Apr 10–May 31 / hardening Jun 1–Jun 30 /
loop-management & autonomy Jul 1–present); the measurement matrix is pruned to the kept set — MMM
drain series (publish the already-collected 56%→20.9% dispatch-scoped series; v1's "production tool
deferred / HIGH" corrected), churn rescoped to `web/`+remediate, control-coverage census at HEAD,
support-ratio 4-point trend, real-bug yield, seat-composition (late-window only) — with cut rows
retained as CUT records (contrastive-subsystems: author-attention bias; failure→control recurrence:
"not reliably measurable"; repo-wide re-touch; sync cost; promotion recurrence). Four quantifiable
claims (spine 8, spine 11, `soft-to-hard-spectrum`, `mechanize-not-remember`) deliberately remain
unquantified as recorded accepted limitations. MBSE external-baseline row held PENDING the author's
artifact. Remaining open items: churn path-set, re-touch N/exclusions, provenance-fraction coding
rule, MBSE artifact, per-row status ceilings (§5 of the doc).
