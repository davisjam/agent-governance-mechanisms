# Autonomous decisions log — for author review at end of STEP 4 (260804)

Author granted full autonomy 260804: "make all judgments yourself, consult a Fable for real pickles, save
the decision + rationale, surface them all later for my review at the end of STEP 4." This is that log.
Each entry: DECISION · context · options · CHOICE · rationale · (Fable-consulted? verdict). Append-only.

Note: "Fable" is not harness-dispatchable (Agent model enum = opus/sonnet/haiku); a "Fable consult" is an
INDEPENDENT fresh-context Opus second opinion. Logged honestly as such.

---

## Already-made calls (this session, pre-autonomy-grant — logged for completeness)

- **D1 · M-in-MAGE flagship dial → DEFAULT 29** (not the wider ~31 modeling footprint). Rationale: 29 =
  the repo's OWN `catalogue-classification.json` (24 keep-as-L2 + 5 model-tagged showpieces) — the
  least-inventive, most-defensible choice; the 18 modeling "faces" stay complete on the web; trivially
  widened via a one-line manifest edit if you want more print modeling. STILL YOUR CALL at STEP 4.
- **D2 · Density-pass departures from the outside reader** (3): (a) NO "Maintenance Economics Principle"
  coinage — invoke the Modeling Thesis instead (avoids a 6th proper noun against the middle path); (b)
  Part-4 gets ONE decision TABLE, not scattered named heuristics; (c) keep the Kruchten 4+1 exposition in
  full, trim only the repeated "one model isn't enough." Rationale: the author's "middle path, pedagogical
  not research-paper" steer.
- **D3 · "the Printer" not "Printer Principle"** — author-confirmed (not autonomous), logged for the record.
- **D4 · Glossary agent-stack = WHOLE STACK** — author-confirmed (not autonomous).
- **D5 · Trust Half → DEMOTE from front glossary** (concept-index-only). Rationale: genuinely one-site
  (appears only in 1.2's pipeline figure), per the reconcile audit; the one clear outlier.
- **D6 · 2.5-metrics representation → raw 7.89% + "0% genuine once glue excluded, target crossed"** rather
  than a naive 14.9→7.89 swap. Rationale: faithful to the real Epic (raw vs glue-excluded is the honest
  nuance); shows the loop reached its target — a live demonstration of the book's own thesis.
- **D7 · FILL-IN diagrams → all 16 drawn uniquely (mermaid), L3-merge deferred to the curation.** Rationale:
  the 16 are mostly canonical/standalone + all lack any diagram; the merge (variants→parent figure) is a
  curation-time projection optimization, cleaner applied there.
- **D8 · Mermaid footgun → a lint (`tests/mermaid_lint.py`), not just a fix.** Author-requested; logged as
  the governance-conversion instance.
- **D9 · Nav redesign → adopt the ponder's refinements** (drop the duplicate top jump-row = the redundancy
  source; omit-not-disable unavailable items; cross-part prev/next allowed). Rationale: faithful to the
  author's layout + kills the flagged clutter; no genuine fork needed author input.

---

## STEP 1-4 autonomous calls (append as made)

### FAST set (STEP 1)

- **D10 · Concept canonical-site picks (glossary pointer-wiring, FAST-2b).** 8 previously-unwired glossary
  terms needed an `index-def` site chosen. Picks: `validator` + `gate` → 2.3 (the four-classes /
  determinize-into-a-gate paragraphs — that content IS the glossary entry); `fidelity-validator` +
  `provenance-layer` → 1.2 (the trust-half pipeline); `fleet` + `pattern` → preface (SE@Google fleet
  sentence / GoF Design-Patterns paragraph); `one-shot-scripting` + `supervised-autonomy` → 1.1. Rationale:
  each anchored at the site where the concept is most-fully introduced; NO prose written or relocated. Low
  risk (display-only index-def markers).
- **D11 · concepts.json enum scope (FAST-2b) — did NOT force the schema.** `concepts.json` has a closed
  `kind` enum {thesis, axis, family, mechanism-class, caveat, core-construct}. Only the 4 that fit cleanly
  (validator/gate/fidelity-validator/provenance-layer = mechanism-class, siblings of constraint/sensor) got
  a concepts.json record; fleet/pattern/one-shot-scripting/supervised-autonomy fit NO enum kind, so they
  were registered in `index-terms.md` + `index-def` only (all the pointer-wiring needs), leaving
  concepts.json 0-drift. Rationale: forcing the enum would violate the schema + risk the pre-check; the
  wiring doesn't require a concepts.json record.
- **D12 · Glossary pointer-wiring mechanism (FAST-2b) → web-only post-render build directive**
  (`_link_glossary_sites`), registry-derived href (drift-proof), over per-entry content markers. Rationale:
  zero `body_md` change → zero Typst/PDF/IR/notation-gate risk; the only authored join is term→slug
  (unavoidable — display names differ from slugs, e.g. "The Printer"→`printer-metaphor`), and the link
  TARGET can't go stale (derived from the concept-tag registry).
- **D13 · Split FAST-2 into 2a (nav+lint+style) + 2b (float-ref+glossary).** Orchestration call: the
  glossary refinement (concept registration + pointer-wiring) was big + judgment-heavy enough to warrant a
  focused wave separate from the nav build-code. Cost ~one extra wave; bought cleaner commits + lower
  stream-death risk. (Tactical, logged for completeness.)
- **D14 · book-float-ref gate red after FAST-1 (process).** FAST-1's figure-wiring placed the 2 loop
  figures but omitted the required `[ref:]` intro, so the full-suite `check_float_ref_gate` went red
  (pre-commit runs validate+build only, not the full suite, so it wasn't caught at commit). Fixed in FAST-2b
  Group-0. STANDING FIX: run the full `catalog_tests.py` before every deploy, not just pre-commit.

### STEP 2

- **D15 · STEP-2 deploy agent stub-completed (armed-monitor trap) → re-dispatched SYNCHRONOUS.** The first
  deploy agent (sonnet) ran the pre-deploy chore (`b35e70b`: regen views + track decisions-log/section-
  numbering) but then "armed a Monitor and ended" before running `deploy github` — so NOTHING pushed
  (origin/main stayed `5b4cf90`, local 54 ahead). Detected by verifying origin/main vs local (trust-nothing).
  FIX: re-dispatched with strict "FOREGROUND-synchronous, no Monitor, don't end until the push is confirmed"
  discipline. STANDING LESSON: book deploy agents must run `catalog_tests.py` + `catalog.py deploy github`
  in the FOREGROUND and wait — never background+monitor for a deploy (the classic stub-completion class).

- **D16 · Nav redesign (FAST-2a) introduced a `unique-landmark` a11y regression → fix = label the toc nav.**
  The single-bar nav left two `<nav>` landmarks per page — `chapnav` (aria-labeled) + `nav.toc` (unlabeled);
  html-validate's `unique-landmark` rule then failed on 135 pages (T2 deploy-scope gate, not in FAST-2a's
  gate set — same pre-commit-vs-full-suite gap as D14). Caught by the synchronous full-suite-before-deploy
  (D15's discipline working). FIX: add `aria-label="Table of contents"` to `nav.toc` in build_book_html.py
  (distinct from chapnav's "Chapter navigation" → both landmarks uniquely named). Book-a11y is
  self-consistent with the product's own accessibility thesis, so this is a correctness fix, not cosmetic.
