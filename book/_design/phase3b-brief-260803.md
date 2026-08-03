# READY-TO-DISPATCH BRIEF — PHASE 3 · 3b: CLUSTER + CLASSIFY (Opus, judgment; read-only wrt entries)

Dispatch after 3a (DONE — cards at `book-models/catalogue-cards.json`). Model **opus**. run_in_background. Live tree, branch main, NO worktree, single writer. This is the load-bearing INTELLECTUAL step: it decides the L1/L2/L3 architecture from the 82 cards. READ-ONLY wrt entries — 3b DECIDES, 3c EXECUTES. Emit a classification artifact + rationale; commit (no deploy — intermediate for 3c). The orchestrator will sanity-check the classification before dispatching 3c.

## Brief text (paste into Agent prompt)

You are classifying the MAGE governance catalogue (LIVE checkout at `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). Work **slow and correct**; commit the classification artifact when done. NOT the parent ada-tool product. This is **Phase 3 · step 3b — CLUSTER + CLASSIFY only**; do NOT rewrite any entry (that is 3c).

**READ FIRST:**
- `book-models/catalogue-cards.json` — the 82 nine-field cards from 3a (Failure class · Engineering obligation · Solution structure · Guarantee · Semantic level · Forces/tradeoffs · Dependencies · Known uses · Likely parent family + `abstract_name`/`note`). Each card's `note`/`likely_parent_family` carries 3a's first-pass merge/demote/lift flags — weigh them, don't rubber-stamp them.
- `book/_design/book-editorial-discipline-directive-260802.md` §§ "Task 3" (the 12 inclusion / 10 exclusion criteria + the 10-dim 0/1/2 rubric + overrides + governing principle), "Task 3 SUPPLEMENT" (3-level architecture; FAMILY vs PATTERN vs INSTANCE; **BEWARE FALSE MERGERS**; the card+cluster merge rule; **NAME AFTER ABSTRACTION**; the claim to make; generalize-idea-not-evidence), "Task 3 SUPPLEMENT 2" (the **4-level GEE ontology**: Capabilities / Canonical mechanisms / Compositions / Variants+known-uses; the title "Constructing the Governed Engineering Environment"; the opening passage).
- `book/_design/editorial-run-results-260802.md` § "PHASE 3 · 3a" — 3a's findings-for-3b.

**⚠️ ANTI-SILENCE / BATCH-EMIT DISCIPLINE (MANDATORY — a prior attempt died here).** Do NOT do one giant silent think across all 82 cards then emit at the end — a long tool-silent reasoning stretch (>~10 min without a tool call) trips the stream-silence watchdog and kills you, losing all work. Instead work INCREMENTALLY and keep tool activity flowing:
1. FIRST, write a **skeleton** `book-models/catalogue-classification.json` (the L1/capabilities scaffold + an empty/first-pass disposition map) and **commit it** early.
2. Then process the cards **capability-by-capability (or family-by-family)** — for each group: read the relevant cards, make the merge/keep/demote calls, write that group's L2 patterns + L3 dispositions into the artifact, and **COMMIT after each group** (descriptive message, e.g. `3b: classify <capability> — N cards → M patterns`). ~8–12 commits total is healthy.
3. Never go more than a few minutes without a Read/Write/Bash tool call. Frequent commits ALSO make any death recoverable (the next attempt resumes from your last committed group).
This keeps the reasoning quality (you still apply the full merge rule + false-merger guard per group) while staying alive.

**DO — cluster, classify, score, name:**
1. **CLUSTER** the 82 cards by the directive's rule: **merge** two cards iff their first SIX fields (failure/obligation/structure/guarantee/semantic-level/forces) are substantially the same AND only known-uses differ; **keep separate** iff obligation OR guarantee differs even when the impl tech is identical. ⚠️ **GUARD FALSE MERGERS** — preserve the RELATION modeled/enforced, not the impl mechanism (all "lints" are not one pattern; all "models" are not "executable model" — they enforce/model DIFFERENT relations). This is the single most important guard.
2. **NAME AFTER ABSTRACTION** — before deciding component-vs-variant, rename each impl-biased title to its pattern-level abstract name (use each card's `abstract_name`; refine). Sort items into the named abstraction's components/variants/examples.
3. **ASSIGN the 4-level GEE ontology** (SUPPLEMENT 2, which enriches SUPPLEMENT 1's 3 levels): **Capabilities** (what the GEE must DO — these ORGANIZE the catalogue, they are not entries) · **Canonical mechanisms** (the L2 intellectual core — reusable structures providing a capability) · **Compositions/stacks** (mechanisms powerful together — name the strong stacks) · **Variants/known-uses** (L3 — concrete DocAble realizations folded under their mechanism). Also mark the **L1 Principles** (the few deep claims that EXPLAIN the catalogue — e.g. 3a flags `semantic-level-enforcement` as one; the directive lists ~7 candidate principles).
4. **SCORE** each surviving candidate mechanism against the 10-dim rubric (Novelty · Agentic-significance · Durability · Generality · Thesis-relevance · Architectural-depth · Evidence · Tradeoffs · Compositional-value · Wow-factor; 0/1/2), record the total, and note any OVERRIDE applied (Foundational / Awesome / Coverage / Case / Historical). No target count — the L2 set is DISCOVERED (expect ~20–27).

**EMIT a classification artifact** — `book-models/catalogue-classification.json` (declared→generated if it fits the idiom; else structured JSON with a `_provenance` header + `_note`): 
- the **L1 principle set** (each: name + the claim it makes + which entries express it);
- the **GEE Capability list** (each capability + the canonical mechanisms under it);
- the **L2 canonical-pattern set** (each: abstract name + one-line intent + rubric score + override + the cards that MERGE into it + its parent capability);
- the **Compositions/stacks** (each: name + the mechanisms it joins);
- the **L3 demotions** — every entry not surviving as L2, mapped to `{disposition: demote-to-L3-under <pattern> | merge-into <pattern> | lift-to-L1 <principle> | keep-as-L2}` with a one-line reason;
- a `_coverage` check: every one of the 82 entries appears exactly once in a disposition.
Plus a short **rationale** section in the results-log (the hard calls, the false-mergers you REFUSED, the splits you made by forces/guarantees).

**DISCIPLINE:**
- READ-ONLY wrt entries. `catalog.py validate` stays 0 (you add a model file only). NO deploy (intermediate for 3c) — validate (0) + build (green) + commit.
- Generalize the IDEA, not the EVIDENCE — every L2 pattern must retain, in your classification note, the pointer to its one vivid failure + one concrete DocAble impl (so 3c can keep the texture).
- The CLAIM to make (record it): not "we discovered 70 mechanisms" but "the case produced ~82 concrete mechanisms; comparative analysis reduced them to N pattern families + canonical patterns, the remainder retained as variants/known-uses."

**RECORD (do not relay):** append a `## PHASE 3 · 3b — cluster + classify` block to `book/_design/editorial-run-results-260802.md`: the artifact path, the L1 set, the GEE capabilities, the L2 discovered count + list with scores, the compositions, the demotion tally (82 → N L2 + M L3 + P L1), the hard calls / refused-mergers rationale. Commit it.

Thorough over fast. This decides the book's catalogue architecture — the false-merger guard and the obligation/relation fidelity matter most. On a genuinely balanced call, make the defensible choice, DOCUMENT the rationale, continue.
