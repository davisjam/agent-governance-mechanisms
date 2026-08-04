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

### STEP 3

- **D17 · Density pass → PILOT on Part 3 before committing to the full 6-wave per-Part pass.** Rationale
  (A.3 hyper-experimentation, pilot-before-sweep): the book is already tight (local-repetition + naming-
  compression both found little), so before spending ~6 sequential opus waves I measure the REAL yield of
  the thesis-reconnection lever on the highest-gain Part (Part 3 — the reader's flagship "why models matter"
  re-derivation example, large established-vocabulary per the manifest). If Part 3 compresses meaningfully →
  run the full per-Part pass; if it too is near-floor → lighter touch, accept the honest word count. The
  pilot's yield verdict is the decision input; I'll log the outcome.
- **D-plan · Section numbering (S1, b6d0d42) shipped clean** — build-derived `1.1.x` on body `<h2>` only,
  display-prefix (never the slug), 1207 anchor links 0 broken, TOC unchanged, front/back-matter/appendix
  skipped, full suite 32/32. No fragile-anchor case (so no Fable consult needed). `###` left unnumbered per
  the 3-level decision (3.1/3.6 flagged as the only 4-level candidates, not actioned).

- **D18 · SELF-GOVERNANCE: pre-commit-vs-full-suite gap recurred 2× → durable control (book-repo, not Epic).**
  Class: a wave passes its per-wave gates (validate+build+tier-1) but leaves a DEPLOY-SCOPE-ONLY full-suite
  gate RED, caught only at deploy → a follow-up fix wave. Instances: D14 (float-ref, after FAST-1 figures) +
  D16 (html-validate unique-landmark, after FAST-2a nav). RIGHT-SIZED CONTROL (A.22, smallest that closes
  the class): (a) extend the book `hooks/pre-commit` to run the CHEAP deterministic deploy-scope checks
  (float-ref — fast Python; the derived-view FRESHNESS regen too) so figure/model-touching waves catch them
  at commit; (b) the SLOW external checks (html-validate/axe T2) stay deploy-time, protected by the standing
  "full `catalog_tests.py` before every deploy" discipline (D15); (c) brief convention added to upcoming
  build/figure/HTML-touching waves: run the relevant full-suite check before the final commit. FOLDED into
  the queued auto-regen-views control wave (same hook). Book-repo control — NOT ada-tool pointers.yaml/Epic.

- **D19 · Density-pass pilot (Part 3) verdict → ~0 yield; book already dense on this lever. One more probe
  (4.5, narrative) before deciding.** The Part-3 pilot (f096195) removed **~0 words**: the view chapters are
  already authored in the invoke-don't-re-explain style (one-clause thesis-invocations, grep-confirmed); the
  sole real re-derivation (3.1 flagship) compressed rhetorically (bullets→clauses) but shed no words (the 3
  legs are load-bearing ideas — "never remove an idea" + departure-a keeps the maintenance forward-pointer).
  This CONFIRMS the accumulating evidence (local-repetition ~60-130w/part, naming-compression ~30-90w, now
  density ~0 on model-pages): **the book is at its honest floor; the 87-89K target is not reachable via any
  editing lever without content-rewrites the author prohibited.** DECISION: do NOT run the full 6-wave sweep
  on model-page Parts. Run ONE cheap probe on a NARRATIVE-register chapter (4.5-lessons-learned, 126
  established) — the pilot's hypothesis that prose re-explanation, if it survives anywhere, is in narrative
  not template chapters. If 4.5 also ~0 → ABANDON the density sweep, accept honest tightness, the
  density-principle style rule (voice.md/directive) governs FUTURE writing only; pivot to the ADDITIVE
  STEP-3 value (operational-density, appendix curation, part-synthesis) which improve the book regardless of
  word count. If 4.5 yields real paragraphs → target only the narrative chapters that have it.

- **D20 · 4.5 narrative probe → ALSO ~0 (0 words). Running the FINAL probe (5.3 retrospective) then closing
  the density sweep.** 4.5-lessons-learned (the strongest hypothesis candidate: 126 established, pure
  narrative) removed 0 words — structural reason: a Lessons-Learned chapter is a DEFINITION site (14 own
  index-defs), its aphorisms ARE the canonical intros; backward refs already one-clause invocations
  (churn/gov-conversion/Modeling-Thesis all dense, grep-verified); forward refs are clean hand-offs. Two
  registers now ~0 (model-page + lessons-narrative). Per the probe's recommendation, running ONE final
  probe on 5.3-the-built-system (the RETROSPECTIVE register, 0 new defs — the one distinct untested shape
  that could re-narrate/re-explain a built mechanism). This is the LAST probe — after it the density-sweep
  question closes regardless (2-3 ~0 probes + structural reasoning = the book is already progressive-density
  by construction; abandon the multi-Part sweep; the style rule governs future writing). Then pivot to the
  ADDITIVE high-value STEP-3 work (operational-density, appendix curation, part-synthesis).

- **D21 · Density sweep CLOSED — abandoned after 3 convergent ~0 probes + structural verification.** 5.3
  (retrospective re-walk, the last distinct register) → 0 words: its two heaviest expositions are its OWN
  first developments (1.2/4.3 explicitly defer to it), and every earlier-canonical back-reference is already
  a one-sentence invocation with a back-link. All 3 structurally-distinct registers (model-page / lessons-
  narrative / retrospective) return ~0. CONCLUSION: the book is ALREADY written in progressive-density
  style; there is no body to compress. The full per-Part sweep is NOT run (would yield ~0). This is a
  VALIDATION of the book's editorial quality, not a shortfall — and it means the 87-89K word target is
  unreachable via any editing lever short of content-rewrites the author excluded; the book sits at its
  honest floor (~95K narrative body). The density-principle style rule (voice.md + directive) governs FUTURE
  writing. Pivoting all remaining STEP-3 effort to ADDITIVE value: operational-density, appendix curation,
  part-synthesis, the D18 control. Density-pilot artifacts (f096195 Part-3 rhetorical tidy) kept; the 3 probe
  chapters (4.5, 5.3) unedited.

- **D22 · 2.4 gap-fill adapted FMEA→typed-step runbook table (fidelity win).** The pilot proposed a generic
  FMEA grid + `- [ ]` checklist for 2.4; the fill wave correctly ADAPTED to the real ada-tool practice
  (`.claude/skills/operate-ada-tool-repo/runbooks.yaml` typed-step grammar RUNNABLE/JUDGMENT_AUTOMATABLE/
  JUDGMENT_IRREDUCIBLE + pointers.yaml symptom→doc-class routing) — no invented FMEA — AND because the book
  renderer has no task-list-checkbox support. Every row traces to a real repo artifact. This is the author's
  "don't make stuff up" directive working as intended (real practice wins over the pilot's book-only draft).
  4.1 → A.22 cost×frequency matrix + stop-litmus, all 4 axes grounded. `delivers` field: concepts DERIVED
  from index-def (join-SSOT, 0-drift by construction), artifacts hand-authored, `all_prose_would_benefit`
  authored-not-derived (anti-filler wired into the model). audit-only-first (rule #55).
- **D23 · Additive-work order: control wave BEFORE appendix curation.** Doing the D18 pre-commit hardening +
  auto-regen-views + clearing the accumulated outline/reverse_index FRESHNESS FIRST, so the build-heavy
  appendix-curation waves (which rewire figures) inherit the float-ref catch + can't accrue view staleness.

- **D24 · Appendix AC-1 (47fb746/8b3c1f7): projection mechanism, 29 flagship, PDF 450→335pp.** Judgment calls
  the wave made (all sound): (1) my brief's "add claude-md-rule-index to appendix_exclude" contradicted the
  design §1b default 29 — the wave kept the **29 default** (claude-md-rule-index stays flagship; the 28 dial
  documented but not pulled), following the design + all gates; correct. (2) design §1c had ~100-line drift
  (mapped by name) + omitted 3 build-breaking integration points the wave ADDED: 54 narrative cross-refs to
  dropped pages → build-time redirect, stale tracked HTML git-rm, `for_print` threading through IR/Typst/verify.
  Faithful completion of an incomplete design. Structural win banked: 29 flagship + all-83 web-index + 0 orphans.

- **D25 · Appendix compression RIGHT-SIZED — skip the aggressive flagship prose rewrite; do stacks + intro +
  print-sample-code-drop.** Measurement: the catalogue entries average ~981 words (terse Hemingway house
  style), NOT the ~1900 the design §6 assumed. So AC-1's structural win (83→29 flagship, PDF 450→335pp) IS
  the lever; the design's "compress each flagship 1900→740" premise doesn't hold (they're already ~half
  that). Aggressively rewriting 29 well-written GoF pattern entries to 740w would risk losing pattern nuance
  for a marginal, print/web-DIVERGING gain — declined (consistent with the density-sweep finding: the book's
  prose is already tight). INSTEAD (A.22 right-size): AC-2 stack pages → the 2-page 7-section synthesis
  (real FORMAT value, scannable), AC-4 appendix intro (L1 principle + 9-capability map) + AppE pointer, and
  a LOW-RISK flagship compression = drop the Sample Code blocks from PRINT only (via the `for_print` path
  AC-1 threaded; kept full on web) — the least-useful print content, no prose-nuance loss. The 29 flagship
  PATTERN PROSE ships at full (good) length in print. Net: a curated, scannable print appendix without
  gutting well-written entries. Surface at STEP 4 for author ratification of the skip.

- **D26 · STEP 3 COMPLETE.** Landed: section-numbering (b6d0d42) · density sweep CLOSED (piloted 3 registers,
  ~0, book at honest floor — D19-D21) · operational-density (delivers field+view + 2.4/4.1 grounded gap-fills
  — D22) · D18 control (pre-commit float-ref-blocks + view auto-regen, verified) · appendix curation (AC-1
  47fb746 29-flagship projection + AC-completion cbfc52c/ff61a24/383c0cd stacks+intro+AppE+print-sample-drop;
  PDF ~450→315pp; D24/D25) · part-synthesis (227f7b0/e957b40/180cb49; Parts 1&5 left, 2-4 voice-matched
  closes). Open editorial (audit-only, non-gating, for author): CS5 chapter-shape re-assess flags on 3.8/4.1/
  4.6 (the rewritten open/closings) — a human may want to re-grade those anchors in chapter_shape_declared.
  Pre-existing SVG stroke-through-glyph advisories on cover/model-map/provenance-fidelity-stack (not mine).

### STEP 4

- **D27 · STEP-4 deploy agent (aced728a) full-suite PASSED but did NOT push — likely stream-silence-killed
  during the silent `deploy github`.** The agent verified 31/0 green then ran `catalog.py deploy github`; the
  process ended with origin still at 720dc1c (STEP-3 unpushed) and no agent completion — the deploy runs
  mostly-silently for minutes, tripping the 600s stream-silence watchdog. HEAD stayed at the track-docs
  commit (no partial deploy commit) → re-run is clean. FIX (memory feedback_agents_die_on_stream_silence):
  run the long silent deploy in the ORCHESTRATOR's detached background Bash (no watchdog, notifies on exit),
  not a sub-agent. Taking over now.

- **D27-CORRECTION · FALSE ALARM — the deploy agent DID complete + push successfully.** My "not pushed"
  reads were a timing race (fetched just before the push completed / before the completion notification).
  Actual: `720dc1c..cd7c4b2 main -> main`, origin==local confirmed, PDF 315pp/3.6MB, full suite 31/0. No
  takeover was launched (only the intent was logged). STEP 4 deploy SUCCEEDED at cd7c4b2. Standing lesson
  still holds (long silent deploy → orchestrator bg bash), but it wasn't needed here.

### Post-publish editorial (author, 260804 — after cd7c4b2)

- **D28 · Front-matter restructure (afbd3e7d, running).** New order per author: cover → copyright → "The MAGE
  Method at a Glance" (NEW figure page, mage-method.svg authored+fit-clean) → glossary → preface (trim
  anticipatory refs to ~2; extract "How to read this book" to its own ≤1-page section so the preface ends
  thematically) → acknowledgments → Part 1. Delicate (renumber front-matter; core concepts index-def'd in
  preface — drift-proof glossary pointer-wiring auto-follows; exhaustive cross-ref verify required).
- **D29 · Figure/table snappy-NAMES — Fable (indep-Opus) ponder dispatched (a1a2f48, read-only).** Author
  wants "Figure X: The Task Classification Heuristic. <desc>" — a memorable name prefix where it sharpens.
  Ponder proposes per figure/table (NAME vs LEAVE, conservative) → I review → apply wave. → book/_design/
  figure-table-names-ponder-260804.md.
- **D30 · "Printer Commandments" boxed capstone — PONDERED (mine), verdict YES.** A boxed 5-rule operational
  artifact at the END of Part 1 (after 1.5): suspect-instructions / one-shot-simple / supervise-reasoning /
  recurring-failures→opportunities / judgment→infrastructure = Part 1's method distilled. It's a named
  operational artifact (not a stock takeaways box → consistent with the no-generic-boxes stance), memorable,
  earns its place. Keep terse imperatives so "Commandments" reads self-aware not preachy; fallback name "The
  Printer, in five rules" if too cute in context. GROUND the 5 rules in Part 1's actual content, don't invent.
- **D31 · "This book…" repetition — QUEUED for a prose-polish wave (after front-matter wave frees the preface).**
  22 in preface + 9 in 1.1 + a few elsewhere. Vary with "MAGE …" / "The MAGE methodology …" / "MAGE teaches"
  where repetitive. Batched with D30 (Printer Commandments) into one prose-polish wave to avoid the preface
  write-conflict with the running front-matter wave.
