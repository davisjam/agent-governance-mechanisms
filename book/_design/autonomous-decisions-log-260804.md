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

## Part-4 hierarchy + naming round (author, 260804) — D45–D47 → PART-4 ponder then apply

**D45 — Part 4 needs hierarchy: cluster the lessons into a few named groups.** The Part-4
lessons currently read as a flat list; group them under headings. Author's example (Fable
may improve): "Engineering with abundance" {refactoring is free · cost estimation is broken
· scope creep is inevitable}; "Engineering with unreliable workers" {done is a claim ·
explicitness is essential · tests must survive agent failure}; "Engineering with leverage"
{governance spectrum · AI is an autonomy amplifier · who owns governance conversion}. →
Fable ponder proposes cluster names + membership grounded in the REAL part4 chapters, then
apply wave adds the section hierarchy.

**D46 — rename the "Generative Validation" (4.6) pattern more articulately.** The pattern is
"turning generators into adversaries." Author: can it be named more articulately? → ponder
proposes a sharper name + rationale; author/I pick. (Interacts with the naming wave's 4.6-2
"The Coin Is the Model" figure name — keep chapter-name vs figure-name distinct.)

**D47 — elevate + name the SUPPORT-RATIO heuristic ("Timeline and the work" chapter).** The
support-ratio concept is a reusable management heuristic but arrives as a single observation.
Give it a NAME and make it more prominent; at minimum connect it to the Governed Engineering
Environment concept. → ponder proposes name + prominence treatment (no chapter expansion).

**D48 — add a named "Putting it into practice" METRICS table (author, 260804).** Capture
and NAME all the metrics a practitioner can use for their loops, in one consolidated table
somewhere (likely Part 4 "method in practice", or a back-matter reference). Inventory every
metric the book already names/uses — support ratio (D47), the missing-model metric/drain,
velocity, churn, control-growth — name any unnamed ones, and give each a one-line "what it
tells you / when to watch it." Grounded in metrics the book ACTUALLY uses (don't invent
metrics). → folded into the PART-4 ponder (scope + home + shape), then apply wave builds
the table.

## D49 — orchestration mishap + lesson (260804): premature commit of a still-live agent's work

**What happened.** I mis-diagnosed the front-matter agent (afbd3e7d) as dead — proc-grep by
agentId showed nothing and its edits sat in the working tree, so I concluded it had died in its
final gate step, committed its work myself as baad0e1, and dispatched the naming wave (ae91987b).
The agent was in fact STILL ALIVE; it completed later and reported it had (correctly) declined to
commit into a contested tree. Net: a brief single-live-writer violation (I committed a live agent's
work + started a 2nd writer over it).

**Consequences (contained).** The restructure landed correctly (agent confirmed HEAD is right). But
my commit ran only the FAST gate (`catalog.py validate`, 0 issues) — which does NOT include the
claims/spine/chapter-shape drift checks — so it shipped a BLOCKING full-suite regression: claim
`grounding-case-not-proof` still homed at the now-removed `a-map-of-the-book` outline unit
(C1 claims-drift FAIL under `catalog_tests.py`). The naming wave then defensively isolated its 47
files and RESTORED the front-matter agent's known-good reconcile fix into the working tree.

**Two lessons (both recurrences of prior classes):**
1. **Agent liveness: trust the completion NOTIFICATION, never proc-grep / working-tree inference.**
   Same misdiagnosis class as D27 (STEP-4 deploy agent judged not-pushed via a fetch timing race).
   ≥2× now. Discipline: an agent is done ONLY when its task-notification fires; do not commit its
   work or start a successor before then.
2. **Book restructure/model changes must be verified by the FULL suite (`catalog_tests.py`), not
   `catalog.py validate`.** The model-drift gates (claims/spine/chapter-shape) live only in the full
   suite — the D14/D16/D18 fast-gate-vs-full-suite gap, recurring. For book-models-touching commits,
   run the full suite (orchestrator detached bg bash) before committing.

**Not founding an Epic:** the fixes are discipline corrections (wait-for-notification; full-suite for
model changes), not lint-able substrate in this stdlib-only book repo. Captured here for STEP-4. If a
3rd liveness-misdiagnosis or fast-gate-miss occurs, revisit as a control.

## Part-4 apply decisions (author-steered + my judgment, 260804) — D50–D52

**D50 — metrics table (D48 resolved): inclusion RULE + the 5 rows + encode-in-model.** Author's
inclusion rule (260804): "a metric belongs iff it is a useful AGENT-LOOP metric or an ORG-level
TARGET for engineering with MAGE" — not every number the book measures. Author: "encode it in the
model associated with the table, use your judgment." Applied:
- IN (5): support ratio (org target — build env first, ~3x), Missing-Model Metric + drain (loop
  target — drain to <=10%), velocity (org target — sustain linear productivity), control growth
  (trajectory target — accrete controls), churn (useful loop signal — phase indicator; the
  borderline one, flagged to author as first-to-pull if targets-only).
- OUT (4): MBSE navigation token-savings (author's explicit example — model-payoff diagnostic, not a
  target), model-sync efficacy (gate/invariant health-check), grammar coverage + model-claim coverage
  (technique-local generative-validation oracles → belong with the coverage family at 2.5).
- HOME: back-matter reference **"The Operator's Dashboard"** (ponder rec; program-level twin of 2.5's
  in-loop table). Columns: Metric | What it counts | The call it informs (when to watch) | Healthy
  direction | Defined in.
- ENCODE THE RULE IN THE MODEL: new declared book-models SSOT (e.g. metrics-dashboard.json) carrying
  the inclusion CRITERION text + every candidate with qualifies:true/false + rationale + cite; the
  back-matter table is GENERATED/validated from it (declared→generated idiom). So a future metric is
  testable against the rule, and the excluded ones are recorded with WHY (not silently dropped).

**D51 — Part-4 lesson clusters (D45 resolved, my judgment per ponder).** Group the 12 `##` lessons
INSIDE 4.5-lessons-learned.md under a new `##` cluster layer (lessons demote to `###`), causal spine
cheap→unreliable→govern: **Engineering with abundance** · **Engineering with an unreliable workforce**
· **Engineering as governance** (framing sections — three-ways + fastest-road-to-hell — stay outside
the clusters). Chose "as governance" over the author's original "leverage" for the third (names the
actual content). Membership per the ponder's mapping. Reversible; surfaced to author for veto.

**D52 — rename 4.6 (D46 resolved, my judgment per ponder): "Generative Validation" → "Generative
Falsification."** The chapter subtitle is already "Generate to Falsify"; the move is Popperian
(generate to BREAK a spec). Sharper + truer than "Validation." Rename the chapter title + chase all
refs/links + the index term (ponder flagged the index-term rename cost). Reversible; surfaced to
author for veto.

**CORRECTION (author, 260804):** D48 HOME confirmed = back-matter "The Operator's Dashboard"
(author: "back-matter or the Brownfield part" — chose back-matter as the reference home; Brownfield/4.1
is topical method, not a lookup surface). D45 (clusters) and D46 (4.6 rename) — author RECLAIMED these
as their own calls ("surface for my judgment"). So D51/D52 above are now my RECOMMENDATIONS pending the
author's decision, NOT decided — the Part-4-chapter wave (4.5 clusters + 4.6 rename) is HELD until the
author rules. D50 metrics (rule + 5 rows + back-matter + encode-in-model) proceeds now — independent of
D45/D46.

## D53 — Part-4-chapter decisions FINALIZED (author, 260804) + PUBLISH authorized

**D45 FINAL (author chose option C, tweaked):** cluster the 12 `##` lessons in 4.5-lessons-learned.md
under three `##` headings (lessons → `###`), framing sections (three-ways, fastest-road-to-hell) stay
OUTSIDE the clusters:
- **The new economics** — refactoring-is-free, cost-estimator-broken
- **The failure modes** — done-is-a-claim, tests-survive-agent-failure, vibe-coding, explicitness,
  optionality-is-poison
- **The MAGE discipline** — soft/hard, autonomy-amplifier, what-this-means, who-converts
(Applying agent VERIFIES the real 12 headings and maps them; ponder membership is the guide.)

**D46 FINAL (author rejected "Generative Falsification" as too nominalization-y):** rename chapter 4.6
title "Generative Validation" → **"Validation with Agents"** (author's suggestion — plain, verb-friendly,
agentic frame). KEEP the subtitle **"Generate to Falsify"** so the Popperian generate-to-break essence
stays. Chase all refs/links + the index term for the title change.

**PUBLISH AUTHORIZED** (author: "publish when all is done"): after D48 (metrics dashboard) + the
Part-4-chapter wave (D45+D46) land and full-suite-verify, do ONE clean `catalog.py deploy github` via
orchestrator detached bg + re-bump the ada-tool submodule locally (do NOT push parent). No further
gate needed from the author.

## Part-5 reinforcement round (author, 260804) — D54–D56 → PART-5 wave (before publish)

Overall author intent: do NOT shorten Part 5; instead continuously remind the reader WHICH MAGE idea each
chapter demonstrates, so the case study reads as "here is MAGE, under stress" (evidence for the method),
not merely chronological.

**D54 — per-chapter "This chapter illustrates" box.** At the START of every Part-5 chapter (5.1–5.4), add a
tiny box: "This chapter illustrates ✓ Modeling Thesis / ✓ Alignment Thesis / ✓ Governance Conversion" (and/or
the Printer, the Governed Engineering Environment) — whichever GENUINELY apply to that chapter (agent reads
each chapter and judges; do NOT reflexively check all). Purpose: constant reinforcement that this is evidence
for the method. Reuse the book's existing box/concept-inset mechanism; keep it tiny + consistent across the
four chapters.

**D55 — FORESHADOW the support ratio before Part 5 (do NOT move it).** The support ratio is an engineering
heuristic, not just a project stat. Add an earlier foreshadow that POSES it as a question — e.g. "What is a
suitable ratio of code to governed environment? Conventional wisdom is ~1:1 tests to production… later we'll
see" — WITHOUT spoiling the ~3× answer. RECONCILE with the D47 forward-ref already in 2.3 (which currently
gives the ~3× answer): make the earlier hook the question-poser and adjust/relocate so the two don't collide
(agent picks the cleanest placement — likely the question earlier where tests:prod / the environment is first
discussed, and 2.3's pointer stays as the "measured in Part 5" ref, de-spoiled if needed). Frames it as a
reusable heuristic.

**D56 — the ending: revisit the "MAGE Method at a Glance" frontispiece one final time.** At the END of Part 5
(end of 5.4, the last case-study chapter), conclude by walking the reader back through the page-3 frontispiece
figure (`mage-method.svg`), checking off each box now instantiated in the real DocAble system: the Printer ✓,
Modeling Thesis ✓, Alignment Thesis ✓, Governed Engineering Environment ✓, Governance Conversion ✓,
Trustworthy software ✓. Closure: the reader has now seen every box in the opening diagram instantiated in a
real system. Cross-ref the frontispiece (0.1) in the book's link style. Keep it a tight closing beat, house
voice — not a re-explanation of each box, a checklist-walk that lands the "evidence" frame.

ENDGAME now: D48 (metrics) → Part-4-chapter (D45+D46) → PART-5 wave (D54+D55+D56) → full-suite verify →
PUBLISH (authorized). Each wave serial on book main; each full-suite-verified before the next.

**D57 — colophon-ordering judgment (autonomous, 260804).** D48 placed the Operator's Dashboard at
back-matter 6.5, AFTER the colophon (6.4), which self-describes as "traditionally the last page… before
the reader closed the cover" — a self-contradiction. Options: (a) renumber dashboard before colophon
(ripples into outline/argument-spine/outcomes/reverse-index declared models + the D48 parity validator's
page path — blast-radius for a cosmetic ordering nicety); (b) keep 6.5 + soften the colophon's "last page"
line (1-line prose edit, zero structural ripple). CHOSE (b) per A.22 (smallest sound change that closes the
contradiction). Folded into the Part-4-chapter wave. Strict colophon-last would want (a) — deferred as
low-value/high-ripple; noted for author.

**D58 — vibe coding → "jugaad" framing (author draft, 260804).** Where the book discusses vibe coding
(4.5-lessons-learned, the vibe-coding lesson), add the author's jugaad connection: vibe coding produces
*jugaad* (Hindi — an ingenious improvised solution from whatever's available) — NOT trash, but not
engineering; "MAGE begins where jugaad ends: by converting successful improvisations into durable
engineering mechanisms." Author supplied draft prose + a footnote defining jugaad (जुगाड़). Adapt lightly to
the exact 4.5 context + house voice; keep the author's core sentences. Use the book's footnote mechanism if
one exists, else an inline aside/parenthetical for the jugaad definition (agent checks). FOLDED into the
Part-4-chapter wave (already editing 4.5). Ties vibe-coding→governance-conversion.

## D59 — metaphor-discipline audit + tracking model (author, 260804)

Author rule: "Never introduce a second metaphor until the first has paid off." The book's strong metaphors:
the Printer, churn, maps-vs-territory, cattle-vs-pets, the zoo (+ others: the staircase, the coin, the
engineer's seat…). Author wants a MODEL that tracks each metaphor's span (begin → pays-off/end) so OVERLAP
is measurable, and overlap should be EXCEPTIONAL. Deliverable: (1) a declared metaphor-tracking model
(book-models idiom, like metrics-dashboard.json) that records each metaphor's introduced-at / pays-off-at
span; (2) a checker that MEASURES overlap (a 2nd metaphor introduced before the 1st pays off) and flags
non-exceptional cases; (3) an AUDIT of the current book's overlaps. KEY MODELING SUBTLETY: distinguish
CORE recurring book-vocabulary metaphors (Printer/churn/zoo — always "live," never end) from LOCAL section
metaphors (introduced to make a point, must pay off before the next) — the overlap rule bites on LOCAL
metaphors piling up, not the core vocabulary. Approach: dispatch a READ-ONLY Opus design+audit ponder NOW
(concurrent with the Part-5 wave — writes only _design), then build the model+checker + fix flagged overlaps
as a follow-up wave. NOT gating the current publish unless the audit surfaces quick pre-publish overlap fixes.

## D60 — delete conversational warm-ups (author, 260804) — whole-book MICRO pass

Author flagged repeatedly: delete conversational lead-in phrases whose next sentence already states the
point — "Here is the interesting part…", "Notice something…", "It turns out…", "The important thing is…",
and kin. Delete the lead-in, keep the substance. MICRO-level (not modeling), whole-book, "a big pass, a few
agents." SEQUENCING: run as ~3 SEQUENTIAL part-grouped waves (P1-2, P3-4, P5-6) AFTER the Part-5 content
wave (so it also cleans the new Part-5 boxes/closing) — sequential because the book's global html+model regen
on commit makes parallel book-writers collide on generated artifacts (the reason single-live-writer holds).
Each wave: delete the warm-up lead-ins in its parts, preserve the substance sentence, house voice; fast-gate;
I full-suite-verify between waves. Part of the pre-publish batch (autonomous; "publish when all is done").

## D61 — shorten glossary entries + add the governing voice rule (author, 260804)

Author: glossary entries are currently Definition → Commentary → Motivation; shorten to **Definition (1
sentence) + optional 2nd sentence (why it matters).** Example — "Governance Conversion. The method by which
the environment evolves. Rising velocity surfaces a structural failure; judgment converts each recurrence
into a durable mechanism…" BECOMES "Governance Conversion. Converting a recurring failure into a durable
engineering mechanism that permanently retires that failure class." AND add the editorial RULE to the book
VOICE FILE (plugin/mage/skills/self-communicate/writing/voice.md): **"Write like an engineering textbook,
not like a conference keynote."** This rule is the UNIFYING principle behind D60 (delete conversational
warm-ups) + D61 (tighten glossary) — land it in voice.md FIRST (in the D61 wave), then the D60 waves cite it.
Scope: voice.md (add rule) + 0.2-the-books-language.md (shorten every entry to def + optional why). Keep the
term's real definition; cut commentary/motivation to at most one why-it-matters sentence.

## Endgame sequence (autonomous, all before ONE publish):
Part-5 wave (D54-56) [writer] + D59 metaphor ponder [read-only, concurrent] → D61 voice-rule+glossary
[writer] → D60 warm-ups ~3 sequential part-grouped waves [writer] → D59 model+checker build + overlap fixes
→ full-suite-verify each → ONE publish + submodule bump → post-publish STEP-4 report (D1-D61).

**Architecture note (for the D59 model BUILD wave):** metrics_dashboard_model.py (D48) is the FIRST
"declared book-models JSON + typed validator/projector wired into catalog.py validate" instance; the D59
metaphor model will be the SECOND. Per A.10 (extract on the second site, not the third), the D59 build MUST
read metrics_dashboard_model.py and EXTRACT the shared validator scaffolding (JSON load, structural/parity
findings shape, catalog.py cmd_validate wire-in) into a small shared helper rather than copy-paste a second
bespoke validator — OR justify why the two are too different to share. Don't leave two parallel hand-rolled
model-validators.

## D59 ponder OUTCOME + my judgments (260804) — audit = 0 overlaps

Ponder (book/_design/metaphor-tracking-260804.md): 6 CORE metaphors (Printer, churn, map/territory, Model
Zoo, loop, engineer's seat — overlap-exempt) + 9 LOCAL (search-space 1.3, poka-yoke 1.5, raven/pebbles 2.1,
evidence-staircase 2.3, diffusion 4.4, jugaad 4.5, the coin 4.6, MAGE-staircase 5.4, DOJ-ramp 5.1). AUDIT
HEADLINE: **0 overlaps** — the author already obeys "no 2nd metaphor before the 1st pays off." So D59 = pure
forward-policing infrastructure; NO content overlap-fixes.

My judgments (autonomous):
- **BUILD the model** metaphor-spans.json + metaphor_spans_model.py (reuse metrics_dashboard_model.py
  scaffolding per A.10) + wire AUDIT-ONLY-FIRST into catalog.py validate (rule #55 landing discipline). Use
  ANCHORS not line numbers (prose drifts). Encode kind:core|local; core has no pays_off_at; overlap measured
  over locals within a stretch; overlap_ok+rationale records deliberate overlaps.
- **cattle-vs-pets: DROP** (fidelity — author listed it but it is NOT in the manuscript; only a stray
  "cattle" writing-origins line at 1.1:134). Do NOT invent a cattle-vs-pets passage. Flagged to author to add
  deliberately if wanted.
- **staircase collision (evidence-staircase 2.3 vs MAGE-staircase 5.4): DEFER** the rename — legal, only
  dilutive, chapters far apart; not worth endgame churn. Reported.
- engineers-seat core-vs-local: keep as CORE (recurs as the SDLC→SELC frame). 
SEQUENCING: D59 model BUILD runs LAST among content waves (after Part-5 + D61 + D60) so its anchors are final.

## D62 — Operator's Dashboard rebuilt on the FORMATIVE/SUMMATIVE axis (author, 260804, post-publish)

Author reframed the metrics dashboard: distinguish **formative** (measured DURING the work, feedback to steer
the next step) from **summative** (measured at MATURITY, a verdict on what was achieved) — richer than
target/signal, and standard assessment vocabulary the audience knows. Author directions: **BROADER** (catch
all 9, not the strict 5); **a MIDRULE** to visually distinguish the two groups; **overlap/duplication is
FINE** — "this table is an engineering reference; duplication from earlier in the book is expected" (waives
the earlier keep-coverage-oracles-at-2.5 objection → include grammar + model-claim coverage too).

Classification (mode field: formative | summative | both):
- **Formative (6):** Missing-Model Metric, Velocity, Churn, Model-sync efficacy, Grammar coverage,
  Model-claim coverage.
- **Summative (3):** MBSE navigation token-savings (payoff verdict) + Support ratio + Control growth — the
  latter two are TRAJECTORY metrics = **both** (watched formatively as they form, reported summatively at
  maturity); tag them "both", seat them in the summative band since their reference number is the mature verdict.
Rebuild: all 9 in metrics-dashboard.json with `mode`; inclusion_criterion → "a metric you steer by
(formative) OR certify the result with (summative)"; 6.5 page table split into Formative | (midrule) |
Summative groups + a one-line note that some rows also appear in 2.5's in-loop table by design (expected for
a reference). Update metrics_dashboard_model.py (mode field + validator: all 9 present, mode-valid; parity)
and the ratified-count check. Then REDEPLOY + re-bump submodule.

## D63 — frontispiece figure: ground "The Printer" as a Coding-agent box (author, 260804, post-publish)

Author: "The Printer" as the top box of the opening figure (mage-method.svg, "The MAGE Method at a Glance")
reads too metaphorical. Reframe it: wrap it in a **"Coding agent"** box with **"reasoning engine + printer"
at its heart** — so the pure metaphor is grounded in the literal thing (a coding agent = a reasoning engine
+ a printer). SVG redraw of the top element only: outer label "Coding agent", inner "reasoning engine +
printer" heart; keep the Umber accent palette, keep the downstream "generates code" arrow + the rest of the
flow intact; MUST pass tests/svg_fit.py (0 overflow findings — the box needs 2 lines now, so grow/space it
and re-fit); update the caption / <desc> a11y text if they lean on "The Printer" as the top node (the desc
already says "The Printer — a coding agent — …", so it's mostly consistent). The Printer stays a CORE
metaphor in the prose (D59) — this only grounds its depiction in the frontispiece. SEQUENCING: separate wave
AFTER D62 (single-live-writer); batch into the SAME redeploy as D62 (hold redeploy until both land).

## QUIESCE (author, 260804) + next-session queue

**Answer to "is the inclusion criterion written down?":** YES, in THREE places — (1) the SSOT declared model
`book-models/metrics-dashboard.json` `inclusion_criterion` field; (2) rendered on the dashboard page opener
`book/backmatter/6.5-the-operators-dashboard.md`; (3) this log (D50, D62).

**Quiesce state:** book main local HEAD = **1411850** (D62 formative/summative dashboard rebuild), origin/main
= 812a85a (the earlier publish). So D62 is COMMITTED LOCAL, **NOT deployed** — deliberately held so next
session's font-fit lands in the SAME redeploy. Tree clean outside _design/. No in-flight writer agents at
quiesce (D62 done; D63 never dispatched). Full-suite verify of 1411850 came back GREEN (32/32) just after quiesce — known-good.

**D64 — NEXT SESSION (author directive): reduce the dashboard FONT so the 9×6 table fits ONE landscape page.**
Current committed state (1411850) is a clean 2-landscape-page breakable reference (agent verified it genuinely
overruns one page; column-width squeezing clipped/scrambled, so it kept 2 pages rather than drop content).
Author's call: next session REDUCE FONT SIZE on the dashboard table (in book_typst.py, scoped to the apparatus
landscape page) to fit one page — a font reduction, not content/column drops.

**NEXT-SESSION QUEUE (do in order, then ONE redeploy + submodule bump):**
1. 1411850 ALREADY green (32/32) — skip re-verify.
2. D64: reduce dashboard table font → one landscape page (verify --pdf fit).
3. D63: redraw mage-method.svg top box → "Coding agent" box with "reasoning engine + printer" heart
   (ground the Printer metaphor); pass tests/svg_fit.py; update caption/desc; keep flow + Umber palette.
4. REDEPLOY: catalog.py deploy github via orchestrator detached bg + re-bump ada-tool submodule locally
   (do NOT push parent).

## D65 — invariants-triangle articulation: ponder verdict PARTIAL → insert (author, 260804)

Ponder (book/_design/invariants-earn-keep-ponder-260804.md) checked book-models first, then prose/figures.
VERDICT: PARTIAL. Present: "model isn't a mechanism until enforced" (claims.json:240 model-not-mechanism-
until-enforced) + prose-that-rots (2.3:280, 3.1:69/97-105, Inset I1) + invariants-as-checked-predicates
(3.1:586-589 per-model-template field (d): invariant·temporal-shape·how-checked; SysML borrow 3.1:109).
ABSENT: (a) the three nodes named as ONE triangle model→invariants→coherence-gate (currently a 5-field
template + a 6-part model-coherence stack DATA/CONSUME/EMIT/PARITY/DERIVE/SEAL — no invariants node); (b) the
"invariants map 1:1 onto failures" proof (declared nowhere). No figure carries the triangle.

MY JUDGMENTS (autonomous; author flagged 2 calls):
- INSERT one short prose beat + one new FIGURE in §3.1 right after the per-model-template (~3.1:598): name
  the triangle (model[typed edges] → invariants[predicates w/ stable IDs] → coherence-gate[enforces at
  deploy/lint]), tie to the SysML borrow, state earn-keep on the INVARIANT axis (a model earns its keep
  through the invariants it lets you enforce, not the schema). Figure = domain-neutral 3-node triangle; the
  CLOSING edge (gate→model) carries the failures point (what the stack figure can't say). Domain-neutral
  labels (the book's free/leased/done example — NOT InterServiceCall; that was the author's ada-tool example,
  not book content).
- SOFTEN piece 4: NOT a universal "1:1" (the book's single-case-humility claim won't support it). State it
  DIRECTIONALLY + ground in Part 5's failure→mechanism record (5.2:247): "in the case study, the gaps the
  model caught were violated-but-unstated invariants." Evidence-grounded, humble.
- ADD a claims.json entry for the principle so the book's OWN coherence gate tracks it (reflexive/dogfood) —
  e.g. `model-earns-keep-via-invariants` or `the-coherence-triangle`. Insert wave writes it + regenerates.
SEQUENCING: INSERT wave is a book writer (3.1 md + new assets/*.svg + claims.json + regen) → queue behind the
live SITE wave; runs after the frontispiece+seat wave. Batched into the one redeploy.

## D66 — glossary (0.2) author direct-edit + slug rename + a 6.2 collision (author, 260804)

Author hand-edited book/frontmatter/0.2-the-books-language.md: title "# The Book's Language" → "# Glossary";
rewrote the intro to frame agentic-SE's naming chaos + the book articulating coherent vocabulary, and to
name the FOUR parts. Verified: the four parts match the actual four `##` groups exactly (The core ideas / How
coding agents work (and fail) / The Governed Engineering Environment / DocAble specifics) — internally
consistent. Edit is GOOD (plainer name matches the D61 textbook-voice rule; clearer intro). Author: "if you
like it, update the slug to match" → rename slug 0.2-the-books-language → 0.2-glossary.
**COLLISION surfaced to author (NOT auto-resolved):** back-matter `6.2-glossary.md` is ALREADY titled
"Glossary" — the AUTO-GENERATED full reference glossary (`<!-- glossary-auto -->`, all terms), vs 0.2 = the
CURATED front-matter primer (4 thematic groups, read up front). Two "Glossary" pages = confusing. Fork for
author: (A) 0.2="Glossary" (primer) + rename 6.2 → "Complete Glossary"/"Term Reference" [my lean]; (B) 0.2
keeps a distinct name; (C) other. Rename ripple surface (small): README.md, AGENTS.md, 3.3-the-process-view.md
link 0.2 by slug/title. Committing the author's 0.2.md edit + the rename waits for a CLEAN tree (after site
wave) + the author's fork answer. The site wave was told (SendMessage) to leave 0.2.md/0.2.html unstaged.

## D67 — heading typesetting: number #/## + italicize a bold sub-level (author, 260804)
(a) Author wants `#` (chapter/H1) AND `##` (section/H2) headings to carry NUMBERS in the typeset output — as
an editor it's hard to reference sections with no numbers. (Earlier section-numbering-260804 added 1.1.x to
`##` in the build — investigate current state: is it web-only / not on the PDF / is `#` unnumbered? The
author perceives "no numbers", so re-check both projections + number the chapter H1 too, e.g. "1.1 The
Printer" + "1.1.1 <section>".) (b) In 0.3-preface "Where this book sits on the shelf" → "Three books frame…"
→ "The premise: mechanize discipline": "The premise" is a boldfaced heading level; author wants THIS heading
level ITALICIZED instead of bold. Identify the level (likely a `###`/`####` or bold-lead) and change its
render bold→italic in build_book_html.py + book_typst.py. → typesetting wave (build renderer).

## D68 — insets: drop exposed numbers (title-only) + de-self-reference (author Pic 1, 260804)
Author (3.3/3.6 inset screenshot): (1) the meta-text is "weirdly self-referential" ("Two insets a reader
needs for this view's model pages:" + "The four models … get a paragraph each here …") → reword to not
narrate the page furniture. (2) "Insets don't deserve exposing the numbers, just the title" — render inset
heading as TITLE ONLY, drop the "Inset I<N> —" prefix. (3) out-of-order (I10 before I7) — MOOT once numbers
are undisplayed. FINDING: insets ARE cross-referenced by number in prose (3.2 refs I5; 3.6 refs I10,I7; 3.3
defines I1,I2,I3,I4,I6; 3.1 I1) — so de-numbering the DISPLAY requires rewording those ~8 prose "Inset I<N>"
refs to title/descriptive form ("the coverage inset" / "the protocols inset"), else they dangle. Inset render
= `inset-title` <p> in build_book_html.py (the "Inset I<N> —" prefix is in the md title text or the render;
locate + drop). → wave: title-only inset render + reword prose refs + de-self-reference 3.3/3.6 meta-text.

## D69 — Table 3.6-1 temporal-shape column: DROP it (answer: liveness lives in 3.3) (author Pic 2, 260804)
Author: the "Temporal shape" column is all "□P (safety)" → if no non-safety props, not worth the column; and
"are there liveness properties we should show?" ANSWER (investigated): the book DOES have liveness (◇)
properties — but they belong to the **Process view (3.3)**, the temporal/TLA+/concurrency view (3.3 is full
of liveness + ◇). The **Scenarios-view join (Table 3.6-1)** is structural coverage/derivation invariants
(every part has a test, deps match, endpoint exercised, tier is pure, no LOAD edge, staging⊇local) — these
are GENUINELY all-safety (□). So: DROP the temporal-shape column from 3.6-1 (uniform → redundant); liveness
is correctly shown in 3.3 where the column earns its place (verify 3.3's table shows the safety+liveness mix).
→ wave: drop the 3.6-1 temporal-shape column; confirm 3.3 carries the liveness properties.

## D70 — figure min-fontsize: mechanical lint + fix 3.8-1 & 4.2-1 (author, 260804)
Author: Figure 3.8-1 (model-sync-two-layer-net) AND Figure 4.2-1 are too small + their text is SMALLER THAN
BODY TEXT, violating the "figure text not smaller than book body text" rule; widen them (column space
available) + raise font ≥ body. AND: "the fontsize issue can be detected MECHANICALLY -- do so" → extend
tests/svg_fit.py with a check that flags any figure whose text font-size < the book body-text size (A.8
audit→lint). Land the check AUDIT-ONLY-first (rule #55 — it will likely find >0), reveal ALL violators, then
a fix wave widens/enlarges each (3.8-1, 4.2-1, + whatever else it catches). Need the canonical body-text px
size to compare against (from design-tokens / the render). → wave: (a) svg min-font check audit-only; (b) fix
the flagged figures.

## D71 — Typst layout: keep-with-next intro lines + text↔table spacing (author, 260804)
Author (Table 4.2-1/4.2-2 screenshot, 2 notes): (1) need a NON-BREAKING notion so a sentence INTRODUCING a
figure/table ("… in Table 4.2-1.") is not split across a page break from the fig/table it introduces —
LaTeX's `~` is a light version; TYPST can do better (a keep-with-next: wrap the intro line + the following
float in a `block(breakable: false)`, or a show-rule that binds a table/figure to its preceding paragraph).
(2) NOT enough vertical space between body text and tables — add systematic spacing. FIX SYSTEMATICALLY in
book_typst.py (a general rule for ALL figure/table intros + block spacing), NOT one-off. → typesetting wave.

## D72 — transformer sentence + "Attention is all you need" footnote (author, 260804)
Author: change "A large language model is a transformer, and it is extraordinarily good at one thing: turning
an input into an output" → "…turning an input into an output **according to a simple-up-to-pretty-complex
mapping function that it learns from its training data**." AND add a FOOTNOTE citing the "Attention Is All You
Need" paper (Vaswani et al. 2017, the Transformer) that explains this for a non-technical reader who's made it
this far. Use the book's footnote mechanism + add the citation to references.bib if not present. → book content
wave (locate the sentence — grep result above).

## D66 RESOLVED (author, 260804): delete empty 6.2, one glossary up front, rename 0.2 slug
Author saw back-matter 6.2-glossary renders EMPTY (the `<!-- glossary-auto -->` harvester produced nothing —
the book's 11 term defs are inline `gloss:` SIDENOTES, not harvested to the back page). Author decision: the
back-matter glossary is "not needed — the opening glossary (0.2) should be all we need, and if there are
other terms we should be putting them UP FRONT." So the fork is resolved by ELIMINATION:
- DELETE `book/backmatter/6.2-glossary.md` (+ its .html, nav/pager entry, list-of-figures if any). The
  `glossary-auto` directive/mechanism in build_book_html.py can stay dormant (or note it unused).
- RENUMBER back-matter to close the 6.2 gap: 6.3-about-the-author→6.2, 6.4-colophon→6.3,
  6.5-the-operators-dashboard→6.4 — cross-ref-safe rename (fix all refs incl. the D48 dashboard slug in
  metrics_dashboard_model.py + the apparatus-oneager title set + any 6.x links; regen outline/argument-spine/
  reverse-index). (Or, if renumber ripple is too deep, leave the gap — but author just asked for MORE numbering
  [D67], so a 6.2 gap is bad → renumber.)
- RENAME 0.2 slug: 0.2-the-books-language → 0.2-glossary (now unambiguous). Fix refs (README, AGENTS, 3.3).
- CONSOLIDATE: check the 11 inline `gloss:` terms vs 0.2's four groups; add any genuinely-missing KEY term
  to the right 0.2 group (keep 0.2 CURATED, not exhaustive — the inline sidenotes stay where they are; only
  promote terms that belong in the up-front primer; surface borderline calls). Author's 0.2 CONTENT edit
  already landed (652d474); this wave does delete+renumber+slug-rename+consolidate.
→ GLOSSARY wave (Opus; cross-ref-rippling rename — handle like the front-matter restructure).

## D73 — caption cap (≤3 sentences AND ≤50 words, HARD/no-noqa) + fix a11y-leak captions (author, 260804)
Author (appendix "Figure 7.504-1: Accessible description: a turn-end …" screenshot): (1) captions are
"comically long" → CAP at ≤3 SENTENCES AND ≤50 WORDS, and MECHANIZE it (a lint) with NO noqa/dispensation
marker allowed — a HARD cap (A.8 audit→lint; but unlike most, NO escape hatch per author). (2) The
"Accessible description:" PREFIX is the SVG `<desc>` a11y text leaking into the VISIBLE caption — WRONG; the
accessible description is for screen readers, not the printed caption. Fix the caption-render path so a11y
`<desc>` never becomes/prefixes the visible caption (appendix-fill figures, the 7.x numbering path). (3) Fix
all over-long captions the lint reveals. NOTE: many book captions are currently 2-4 sentences / >50 words
(mage-method, semantic-gap, etc.) → this is a real trim-ALL-captions fix-wave. Land the lint AUDIT-ONLY-first
(rule #55), reveal all violators, TRIM every caption to the cap, then flip BLOCKING (hard, no-noqa). → folds
into the FIG mechanical-lint wave (with D70 min-font).

## D74 — Figure 6.3-1 (author headshot) smaller + WRAPFIGURE (author, 260804)
Author: Figure 6.3-1 (`assets/author-headshot.jpg`, the author portrait in 6.3-about-the-author) is "huge and
looks silly" → typeset SMALLER and as a WRAPFIGURE so the bio text FLOWS AROUND it (portrait-beside-text). A
partial wrap mechanism may already exist (book_typst.py:655/808 have "wrap"). → folds into the TYP layout wave
(with D71 keep-with-next + spacing); size + wrap the headshot; HTML can float it too.

## D75–D78 — appendix rendering + temporal notation (author, 260804)

**D75 — Related Patterns: link Bridge/Enabler (all REL_TAG bullets), like See also.** In the appendix entry
template's "Related mechanisms", the "See also —" bullets link their target mechanism but "Bridge —" /
"Enabler —" do NOT. Make EVERY REL_TAG bullet (REL_TAGS = Counterpart, Generalization, Enabler, Consumer,
Layer, Bridge, Sibling, See also — catalog.py:132) link its target mechanism the same way See-also does.
Render fix in catalog.py (the related-bullet target-parse/link path ~274/355). → APX wave.

**D76 — "See also" typesetting: ONE "See also:" then bullets.** Currently each related bullet repeats its tag
("See also — …", "See also — …"). Group consecutive same-tag bullets under a SINGLE tag label ("See also:")
with a bullet per item (applies to any tag with >1 bullet). → APX wave (catalog.py related-section render).

**D77 — appendix heading typesetting: tone down + ALL-CAPS chapters.** Appendix pattern entries should be
tight 1-pagers. (a) reduce ALL appendix heading sizes one level; (b) make the appendix CHAPTER headings
ALL CAPS so they're (1) clearly distinct from the book's chapters and (2) still stand out despite being
smaller. catalog.py heading CSS (h1/h2 fs-thesis-title/fs-section ~1181) + the Typst appendix path. → APX wave.

**D78 — proper temporal-logic symbols throughout; NO ASCII "[]" notation.** Replace ASCII temporal notation
with proper Unicode: `[]P`→□P (always/safety), `<>P`→◇P (eventually/liveness), `P ~> Q`→P ↝ Q (leads-to;
or keep ~> if the book's convention prefers it — pick one + apply consistently). Sites: 3.3-the-process-view
+ appendix-fills (composed-state-machine-model, formal-invariant-verification) + anywhere temporal logic
appears. CAREFUL: do NOT touch markdown `[](…)` links or `<…>` html/comments — target only the temporal-logic
strings. Ensure the symbols render in BOTH HTML + Typst. → folds into BC2 (Part-3 wave); also fix appendix-fills.

## D79–D80 — more appendix rendering (author, 260804) → APX wave

**D79 — delete the "Structure / The Structure diagram appears at the top of this page" template boilerplate.**
Every appendix entry emits a "Structure" section whose body is the template line "The Structure diagram
appears at the top of this page." DELETE this template entry entirely — let the figure do the talking (the
diagram is right there). catalog.py appendix-entry template. → APX.

**D80 — appendix figure numbers are hardcoded garbage (7.504-1, 8.608-1); make them DERIVED + monotonic.**
The book does not have 600 figures; "504"/"608" are hardcoded in metadata (likely a source-line or hash used
as the figure number). Appendix figure numbers MUST be derived MONOTONICALLY from the numbering system (like
the book's part.chapter-N figures), not hardcoded. Fix the appendix figure-numbering logic in catalog.py to
assign sequential numbers. (Same class as the D73 "7.504-1" observation.) → APX.

**Reassign within the appendix cluster:** D73's a11y-`<desc>`-LEAK-into-caption fix → APX (it's appendix
caption RENDERING); D73's caption-CAP lint (≤3 sentences/≤50 words, hard) + trim-all-captions stays in FIG
(book-wide mechanical). APX wave = D75 (link REL-tag bullets) + D76 (group See-also under one label) + D77
(appendix headings −1 level + ALL-CAPS chapters) + D79 (delete Structure boilerplate) + D80 (monotonic
appendix figure numbering) + D73-a11y-leak. catalog.py appendix/catalogue render — Opus.

## D81 — no emoji-as-word in prose (author, 260804)
Author: "A weak-prover fallback is a standing ⚠️." — never use emoji as a WORD in the text; write out the
meaning ("a standing hazard/liability/known-risk"). Book-wide sweep: replace inline prose-emoji (⚠️ ✓ ✗ ✅ ❌
used as words) with written-out meaning. (NOTE: ✓ checkmarks in the deliberate "This chapter illustrates ✓"
boxes + the D56 frontispiece-closure checklist are INTENTIONAL list-markers, not prose-emoji — LEAVE those;
target emoji used as a noun/adjective in a sentence.) Fold into the wave that owns the file where each occurs
(likely appendix-fills → APX, and part3 → BC2).

## D82 — BIG: appendix RESTRUCTURE into A/B/C tiers (author, 260804) — design-ponder first
Author proposes reordering the appendices by VALUE not taxonomy:
- **Appendix A: MAGE Model Stacks** — LEAD with the flagship stacks (currently Appendix D). Each A.X = overview
  + constituent parts inline (≤5 parts, one page each), with the overview figure carrying AUTOFILLED CLICKABLE
  links to each part's A.X anchor (build-time). A.1, A.2, … per stack. Opening remarks up front.
- **Appendix B: Engineering Notes** — deeper dive on ~10 flagships.
- **Appendix C: Mechanism Catalog** — the FULL list, C.1 Agent (current A) / C.2 Models-bridge (current B) /
  C.3 Product (current C). VERY TIGHT — "glossary not details": a GRAPHIC-NOVEL brick grid, each cell = the
  mechanism's figure + a 3-sentence summary.
- Opening remarks add the CLAUDE-CODE-AGNOSTIC note: "Every vendor-specific feature is an instance of a MAGE
  concept. E.g. Claude Code's hooks are an implementation of enforcement points — your framework may implement
  it differently, but the concept is portable."
MY DESIGN QUESTIONS (leans): (1) full 83 entries — WEB keeps complete, PRINT gets the tiered A/B/C (the
established print-vs-web projection; no content lost) [strong lean]; (2) which 10 flagships for B (from the
flagship set); (3) autofilled numbering = build-generated LINKED LEGEND under the overview figure (not SVG
internals); (4) bricks = CSS grid (web) + Typst grid (print). This ABSORBS the queued APX small-fixes
(D75 link REL tags, D76 See-also grouping, D77 heading sizes+ALL-CAPS, D79 Structure boilerplate, D80
monotonic fig numbering, D73 a11y-desc-leak, D81 appendix emoji) — hold APX, fold into the restructure.
APPROACH: design-ponder first (read-only, Opus, checks flagship-stack/catalogue-classification/
print-appendix-manifest models) → concrete build+migration plan → author ratifies → implement. Big lift.

## D82 RATIFIED (author, 260804) + full autonomy ("proceed without pinging me")
Author answered the 4 design Qs: (1) web keeps full GoF catalogue, print=tiered A/B/C [confirmed]; (2) B
Engineering Notes = ALL genuine flagships, DON'T pre-prune (author prunes later); binding constraint = each
note gets a 1-full-page OR 2-full-page treatment, open-book readable with NO mid-note page break (keep-together
per note); (3) autofilled linked-legend numbering — approved, "give it a try"; (4) brick grid — approved.
"Happy building" + "You are autonomous, proceed without pinging me" → NO further ratification rounds; the
restructure ponder's plan → dispatch implementation directly; drain ALL queued waves autonomously; ONE
redeploy at the end; report at close. (Relayed the 4 answers to the ponder a9e342e8 via SendMessage.)

## D82 ponder DONE + my resolutions of the §11 load-bearing calls (autonomous, 260804)
Design: book/_design/appendix-restructure-260804.md (§8 migration, §10 build touch-points w/ file:line, §12
9-step dependency-ordered exec plan). Restructure is ~fully MODEL-DERIVED (flagship_stack_model FS1-FS5 →
App A inline parts + Q3 legend; print-appendix-manifest _flagship_slugs 29-set → App B Engineering Notes;
appendix-fills (all 83) → App C bricks, no new figures; for_print projection → Q1 web-full/print-tiered).

MY RESOLUTIONS (author is autonomous, no ping — decide + report at deploy):
- §11-A (3 stacks have 6 parts > the "≤5" guide): RELAX to ≤6 — do NOT drop genuine interlocking parts to
  hit an arbitrary cap (fidelity > round number; "at most 5" was a rough guide).
- §11-B (29 Notes ≈ 30-55 print pages): PROCEED with all 29 — author explicitly said "don't pre-prune, I'll
  prune later"; within the 28-36K word ceiling; page-count is the author's later tradeoff.
- §11-C (bricks source): SHIP v1 with the FALLBACK-derived tight 3-sentence brick (from existing Intent+
  Summary), NOT a blocking 83-brick authoring wave; purpose-built `### Brick` fill slots = a FOLLOW-UP polish.
- §11 sequencing + skill-recipe E→D letter shift: follow the §12 9-step dependency-ordered plan.
IMPL: big lift → dispatch as SUB-WAVES per §12 (not one mega-agent; agents die on huge tasks). Sequence the
restructure AFTER the contained chapter waves (INS/TYP/FIG) so the risky catalog.py rework runs with an
otherwise-clear queue. Absorbs D73(a11y-leak)/D75-D81.

## D81 REVISED (260804): it's a RENDER bug, not a content sweep
The book SOURCE has no emoji-as-word (BC2 confirmed; the ~10 ⚠ files are all node_modules deps). The
"standing ⚠️" the author saw is RENDER-INJECTED: source `appendix-fills/models-bridge/symbol-anchored-
traceability-graph.md:103` says "a standing **warning**" (words) but the BUILT html renders "a standing ⚠️" —
build_book_html.py converts the word "warning" (or an admonition marker) to the ⚠️ emoji. FIX = remove that
emoji-substitution render rule so "warning" stays the word (author: never emoji-as-word). → RENDER fix, fold
into the TYP renderer wave (build_book_html.py). Content needs no sweep.

## D81 FINAL (260804): stale-html, not a real bug
Source says "standing warning" (words); catalog.py ⚠ are only its own diagnostic flags (PRELIMINARY/DRIFT/
BOOK-HOME-OWED), NOT injected into content; the .md's last commit (81865e9) authored it as "warning". The
built appendix-b html showing "⚠️" is STALE (pre-dates the wording). A rebuild regenerates it as "warning";
the deploy + the D82 restructure both rebuild the appendix, so it self-heals. No content/render change; D81
closed. (The ~10 grep-⚠ files are all node_modules deps — irrelevant.)

## D83 — un-rendered markers leak on served pages (LIVE bug) → fix + mechanical sensor (author, 260804)
LIVE: constructing-the-gee.html shows literal "--census" (line 151) + "--summary" — the marker directives
leaked un-rendered. ROOT CAUSE: `constructing-the-gee.md` is a STANDALONE served conceptual page (not a
catalogue entry); catalog.py processes `<!-- summary: … -->` (metadata, strip) + `<!--census:controls-->N
<!--/census-->` (substitute the count) for ENTRIES but NOT for these standalone served .md pages → the markers
survive into the HTML. Source `constructing-the-gee.md:1` (summary), :24 (census 82).
SENSOR GAP: `check_census_tokens(entries)` (catalog.py:945) scans ENTRIES only, not standalone served pages —
so the leak wasn't caught (rule #17 served-page smoke gate doesn't assert marker-freedom on these pages).
FIX (author "fix it and prevent in future"):
1. FIX: run the marker-processing (summary-strip + census-substitute + any other `<!-- directive -->`) on ALL
   served .md pages (constructing-the-gee, development-workflow, quick-start, etc.), not just entries. Rebuild
   → the leaks vanish.
2. PREVENT: add a MECHANICAL sensor (A.8; extend rule #17) — a build/validate check that scans EVERY served
   HTML for surviving marker syntax (`<!-- summary`, `<!--census`, leaked `--census`/`--summary`, any raw
   `<!-- <directive> -->` that should have been consumed) and FAILS. Closed monotonic marker set. Land it so
   it's impossible in future. → focused catalog.py fix-wave (D83), sequence after TYP (before FIG/RESTRUCTURE).

## D84 — coherence-triangle beat: "structured" not "typed" + schema-is-valuable reframe (author, 260804)
Author corrections to the just-landed INS beat (887f5e1):
1. TERMINOLOGY: "typed model" → "STRUCTURED model" (the book's canonical term now). Fix the 3.1 beat + the
   coherence-triangle.svg node label ("Typed model"→"Structured model") + check book-wide consistency
   (grep result above sizes whether 'typed model/data' leaked elsewhere → sweep if so).
2. REFRAME earn-keep: the schema IS valuable. Change "The schema is not what earns the model its keep. The
   invariants that get checked are." → a TWO-KINDS-OF-VALUE frame: "The model provides two kinds of value.
   First, the schema — records/edges/state machines — names the parts and gives tools something to read.
   Second, the invariants that get checked — the predicates that must hold." Value BOTH; the triangle's point
   becomes that the invariants+gate COMPLETE the model's value, not that the schema is worthless.
3. UPDATE the claim `model-earns-keep-via-invariants` (claims_declared.json): its statement "…through the
   invariants…not its schema" + contradicted-by watch now conflict with schema-is-valuable — revise to "a
   model's value is BOTH its structure and its enforced invariants" (or similar); regen claims.json.
→ focused 3.1 revision wave (prose + svg + claim); disjoint from TYP(renderer)/D83(catalog.py) but serializes.

## D84b — canonical-vocabulary lint (author, 260804): mechanize "structured model" over "typed model"
Author: "Add a regex to prevent...?" — YES. Add a lint (tests/ or catalog_tests.py gate) enforcing the book's
canonical vocabulary: flag deprecated **"typed model" / "typed data"** → canonical **"structured model/data"**.
Design: a DEPRECATED→CANONICAL map (a dict), regex per entry, so future term-shifts add a row (single source
of truth, A.9). NOT a blanket "typed" ban — "typed" is legit in "typed enum/step/language"; target only the
specific 2-word phrases. `noqa` escape for genuine exceptions (e.g. a deliberate contrast or quote). Land per
rule #55: the D84 wave FIXES the ~4 current hits (2.5:266, 3.1:58/384/402/626, 3.8:8, 4.1:286/295 — with
per-site judgment on load-bearing "typed") to ZERO, then flips the lint BLOCKING. This is the "fix + prevent"
pattern the author keeps asking for (dogfoods the book's audit→lint / mechanize-discipline thesis). Folds into
the D84 wave.

## D85 — appendix-restructure feedback INTEGRATED (author review, 260804) — reviewer wins (Phase-1b style)
Author provided a detailed critique (book/_design/appendix-feedback-260804.md). Ratifies the A/B/C VALUE
ORDER; REJECTS the current content budgets. Core correction: **A compositional, B selective, C terminally
concise** — the current plan triple-treats each flagship (1pp in A + 1-2pp in B + a brick in C = too much
duplication). REVISED PLAN (reviewer's calls WIN; supersedes my earlier D82 §11 resolutions where they
conflict):
- **Rename A → "MAGE Engineering Stacks"** ("Model Stacks" misleads = foundation-model stack). Opening ≤1-2pp
  (nine-cap map + portability note OK; don't over-theorize).
- **A contract = COMPOSITION:** each constituent part is ~150-250 WORDS (role / receives / emits-guarantees /
  pointer to its B deep-dive), NOT a full page. The STACK is the unit; constituents are not mini-essays.
  (Corrects §2.1 "one page per stack" — it was really one CHAPTER per stack.) Relax ≤5→≤6 parts BUT shorten
  the treatments (6 full-page parts was the real problem, not the number).
- **B rename → "Flagship Mechanisms"; SELECTIVE, not model-forced.** The model must ENCODE the editorial
  decision, not MAKE it (flagship_slugs≠auto-29). Prefer TWO tiers: B1 = 10-15 genuinely central (2 full pages
  MAX each) + B2 = remaining print flagships concise (½-1pp). OR all 29 but default 1pp, 2pp rare. DO NOT
  ratify 29@1-2pp without a rendered PAGE-BUDGET PROTOTYPE. "No pre-prune" = migration-only, not permanent.
  Grouped by role but numbered MONOTONICALLY.
- **C = RETRIEVAL, terminally concise:** 3 sentences + figure + metadata, no argument. **VISUAL FITNESS RULE:**
  a brick figure must be legible at final print size WITHOUT reading internal body text → 3 renderings
  (existing Structure diagram if it passes / simplified brick diagram / no diagram + a mechanism-class glyph).
  **TWO columns** in print (3 too small). Ship FALLBACK bricks first, render all 83, set the template, THEN
  curate (don't author 249 sentences blind).
- **Linked legend refinement:** link text = mechanism NAME + generated LOCATOR, e.g. "MARK — Mutator Stamps
  (§A.1.2)"; don't rely on color/abbrev alone.
- **Keep-together needs a PROTOTYPE, not confidence:** nonbreaking-1pp-block has a real failure mode (can't
  satisfy don't-split ∧ fit-page). Treat as AUTHORED LAYOUTS: `spread:1` (one indivisible block) / `spread:2`
  (two named panels + author-chosen fold); BUILD FAILURE if a panel exceeds its page budget. Word-cap = early
  sensor only; RENDERED HEIGHT is the true invariant → add a PDF-LAYOUT audit, don't trust word count.
- **Appendix D (skill recipe): KEEP FULL CONTENT in the book** (author end-note — do NOT make it a vestigial
  pointer; the tool-skill-vs-mastery-skill distinction is insightful). ENRICH: quote Anthropic's latest
  "how to write a skill" guidance as an inset/blockquote FOREWORD, then OUR take after it (ours is better).
- **MIGRATION: incremental, NOT big-bang** (the biggest de-risking). 7-step order: (1) separate stable
  semantic ID from display location — links target IDs, not letters/slugs that encode placement; (2) add
  reader-facing locator + figure-prefix fields, fix D80 independently; (3) build new A/B/C projections
  ALONGSIDE the old behind a build FLAG; (4) add HTML+Typst renderers for legends/notes/bricks; (5) run BOTH,
  compare coverage + link integrity; (6) switch print to new; (7) remove legacy + add redirects.
- §11-C: Wave-A (authored stack prose; model too terse for polished compositional prose) BUT enforce
  STRUCTURAL CORRESPONDENCE (every modeled part appears exactly once, in model order; no unmodeled part).
IMPL now follows THIS revised plan + the 7-step migration (not the original §12 big-bang). Still sequenced
after the contained chapter waves. I'll append the full revised architecture to the restructure design doc.

## D86 — C brick layout = automated constraint-driven packing (author, 260804)
Author: C bricks are variable-width (some wide); AUTOMATE layout with a brick-PACKER per section + constraints
("these two side by side", "this near that"). Integrated into the restructure design §14: shelf/row-packing
(genre A.9) + declarable `span:` widths (auto-derived from figure aspect + visual-fitness bound) + adjacency
hints (`pair_with`/`near`), build-time deterministic, HTML CSS-grid + Typst packer; 1/2-col/mixed as resolved.
V1 = shelf-pack + spans + hints, refine after rendering all 83 (fallback-first). → C sub-wave of restructure.

## D87 — parallelize appendix implementation via concurrent DRAFTING (author, 260804)
Author: "dispatch much of the implementation wave concurrent into drafts." YES — split the restructure into:
(a) SEQUENTIAL INFRASTRUCTURE (catalog.py A/B/C renderers, the C brick-packer, the 7-step migration behind a
flag) — single catalog.py, careful; (b) PARALLEL CONTENT DRAFTING (Appendix D prose, A constituent 150-250w
blurbs per stack, B Flagship-Mechanism notes) — INDEPENDENT authoring that writes to DRAFT files under
`book/_design/drafts/` (NOT book main, NOT committed, NOT built), so many run CONCURRENTLY with the book-main
drain + each other, no single-writer collision. The infrastructure wave later ASSEMBLES the drafts. Draftable
NOW: Appendix D (author flagged) + A-constituent blurbs (stack model known: FS1-FS5/7 stacks). B-notes gated
on the count decision (10-15 vs 29 — pending the reviewer's page-budget prototype); draft the safe-core after.
Appendix D content = full skill-recipe (tool-skill vs mastery-skill) + Anthropic "how-to-write-a-skill" inset
foreword + OUR take after (§13.7 / author end-note).

## D88 — persisted the parallel-drafting + single-live-writer pattern into the submodule CLAUDE.md (author, 260804)
Author: "update this repo's CLAUDE/AGENTS to explain this to yourself. You forget it." Added a "## Working on
this repo with a fleet (single-live-writer + parallel drafting)" section to the submodule-root CLAUDE.md
(governance-catalog/CLAUDE.md): (1) ONE writer at a time on main (the pre-commit hook force-stages regen
html+book-models → concurrent commits collide; two-commit/stash to isolate; --no-verify banned); (2) drafting
PARALLELIZES (drafts to book/_design/drafts/, not main) while INFRASTRUCTURE serializes (catalog.py/build_
book_html.py/book_typst.py, one writer); (3) gate discipline (full-suite between writers, never git add -A,
briefs read the submodule-ROOT CLAUDE.md — there is no book/CLAUDE.md, per the D-drafter's finding). The edit
is UNCOMMITTED (D84 live); commit it in the next clean window after D84.
Also: Appendix D draft DONE → book/_design/drafts/appendix-D-skill-recipe-draft-260804.md (fetched Anthropic
guidance + our take framed as skills-as-layers-of-models; flagged E→D letter collision + assembler TODOs).
Brief-template fix noted: stop telling agents "read book/CLAUDE.md" — it's the submodule-root CLAUDE.md.

## D89 — no hardcoded references; all xref + a sensor (author, 260804)
Author: "the book should contain NO hardcoded references, all should be xref. Mechanically prevent going
forward (sensor) and fix all violations." This IS the reviewer's migration step-1 (links target stable IDs,
not letters/slugs that encode placement) applied book-wide → the FOUNDATION for a relettering-safe restructure.
SCOPE (grep): only ~3 hardcoded "Appendix <Letter>" literals in the body; ZERO literal "Chapter N"/"Figure
N-M"/"§N" (those already use [ref:] — the book is already largely xref-clean). Existing xref machinery:
build_book_html.py _apply_part_refs(440), _apply_gh_refs(489), _chap_ref(1833), [ref:key] floats(1055).
WAVE: (1) EXTEND xref to APPENDIX cross-references (a symbolic appendix-ref resolving the letter at build, so
"Appendix E"→D relettering can't break refs); (2) FIX the 3 hardcoded "Appendix X" (+ any in appendix-fills —
though the restructure redoes those); (3) ADD a no-hardcoded-ref LINT flagging literal cross-ref patterns in
prose ("Appendix [A-Z]", "Chapter [0-9]", "(Figure|Table) N-M" not via [ref:], "§N"), noqa escape, lands ~clean
after the 3 fixes (rule #55). Sequence D89 BEFORE the restructure (its step-1). Appendix D draft COMPLETE in
drafts/ (Anthropic guidance + MAGE layer-of-models take + judgment-over-rules convergence).

## A-blurb FORMAT LOCKED (from pilot a9b476a8, 260804) → fan out remaining stacks
Pilot drafted stack 1 (provenance-and-fidelity, 5 blurbs 150-250w, structural correspondence). Format LOCKED
(pilot's calls accepted): skeleton = 1-sentence ROLE lead + bold **Receives** / **Guarantees** / **Hands to
<next>** (seam kept as its own segment — composition is A's point) + `→ Deeper treatment: [its
Flagship-Mechanism note] — *<name>* (Appendix B)` pointer; DROP the `durability` field (not compositional);
DE-JARGON part titles (role-based, no bare artifact names / rule numbers — interpretability rule); ~150-200w;
all modeled parts once, in model order, none extra. Fan out the remaining stacks as concurrent drafters into
book/_design/drafts/A-stack-<slug>-blurbs.md.

## D70-followup — enlarge the ~13 audit-only min-font figures + flip lint blocking (260804)
FIG (0cd65e1) landed lint_figure_min_font.py AUDIT-ONLY (rule #55) + fixed the 2 explicitly-flagged figures
(3.8-1 model-sync, 4.2-1 three-skills). ~13 more figures have text below body-size (audit list): skill-recipe,
substrate-derivation, deployment-model-structure, dataflow-inset, loop-engineering, novelty-axis,
coherence-triangle, squash-zero-promote, dag-policy-structure, llm-as-function-call, mage-method,
example-vs-generative, frontend-mvc-editor-dsl, dsl-remediation-function. FOLLOW-UP wave: enlarge each to ≥
body-text size (widen where column space allows), keep svg_fit + overflow clean, then FLIP lint_figure_min_font
BLOCKING. Queue as a figure-enlargement wave (can batch late in the drain, before redeploy). Note: FIG agent
hit a transient 500 mid-work; orchestrator finished + committed the audit-only-first landing.

## D90 — [FIX, low-pri, deferred] potential cmd_validate lint-registration helper
This session added several book lints (lint_canonical_vocab, lint_figure_min_font, lint_caption_length, the
D83 marker sensor, + D89 no-hardcoded-ref coming), each a distinct check in its own file (uniform
one-lint-per-file convention, A.19 — NOT logic duplication). The only repeated shape is the ~5-line
cmd_validate REGISTRATION stanza per lint (import → run → format findings → n_issues+= or audit-print). If
the count keeps growing, extract a `_run_book_lint(module, blocking=bool)` helper to DRY registration — but
FOLD it into the RESTRUCTURE's catalog.py rework (which touches cmd_validate anyway), NOT a standalone
refactor now. Explicit-per-lint registration is readable; low priority. Noted per A.10 architecture self-check.

## D91 — a THEORY OF MAGE appendix (research implications; author, 260804)
Author: articulate a THEORY of MAGE in the manner of Forsgren et al.'s *Accelerate* — offer FALSIFIABLE
PREDICTIONS from the MAGE framework, connected to the Operator's Dashboard metrics; "a beautiful summary."
Needs a MODEL then text following it (declared→generated). Mine candidate metrics from Sadowski & Zimmermann
(~/Downloads/978*.pdf) + the *Accelerate* manner (~/Downloads/Accelerate*.pdf). VERY CAREFUL thought: ~1-2
FIGURES + 1-2 TABLES + perhaps EQUATIONS. HEDGE heavily ("N=1 generalization, but here it is for posterity").
Author: "start by placing it in an Appendix, we iterate from there." APPROACH: dispatch a concurrent design-
ponder + INITIAL DRAFT (Opus) — reads both PDFs (fair-use research reference; OUR theory, not reproducing
theirs), designs the MAGE theory (constructs = the two theses + governance conversion + the metrics; causal/
predictive relations; falsifiable predictions tied to the dashboard metrics), proposes the figures/tables/
equations, drafts into book/_design/drafts/theory-of-mage-draft-260804.md for author iteration. Concurrent
(drafts only, no book-main collision). Then an appendix-placement wave after the restructure settles the
appendix scheme. Don't overdo it.

## D91 draft DONE (260804) — Theory of MAGE, awaiting author iteration
Drafter a30e19cd → book/_design/drafts/theory-of-mage-draft-260804.md (PART A design + PART B appendix draft)
+ theory-of-mage-model-260804.json (declared model, unwired pending ratify). Theory: driver=agentic velocity,
MODERATED by governed-environment-quality E (the Accelerate "delivery performance" slot); capabilities =
modeling-investment (Modeling Thesis) + governance-conversion (Alignment Thesis); outcomes = throughput/escape/
oversight (≈ Sadowski-Zimmermann Velocity/Quality/Satisfaction). 6 falsifiable predictions P1-P6 (each:
mechanism + dashboard observable + falsification). 2 eqs (churn-wall V_durable=V_raw·(1−c(m)); two-regime
escape). Fig T-1 causal model + T-2 velocity trajectories; 2 tables. Hedged N=1/analytic/directional.
AUTHOR ITERATION Qs surfaced: (1) placement — standalone vs fold into 6.0-implications (overlaps ~3 preds);
(2) formality level; (3) 6 preds vs trim to 4 (P2-P4 sharpest); (4) naming "E". → appendix-placement wave
AFTER the author's leans + the restructure settles the appendix scheme. Refs confirmed: Accelerate (Fergrson.pdf),
Sadowski-Zimmermann (978-1-4842-4221-6.pdf).

## QUIESCE (author, 260804) — mid-restructure
HEAD 0b59124 (restructure sub-wave 1: A/B/C/D projection behind ADA_APPENDIX_V2 flag, default byte-identical).
14 commits ahead of origin, batched/undeployed. No writer agents live. Restructure sub-waves 2-6 + GLOSS +
D70-followup + D91-theory-placement + redeploy remain (see handoff). Theory draft awaits author iteration
(4 Qs). Sub-wave-1 verify was mid-run — re-confirm green next session. Clean stop.

## D91 RATIFIED (author, 260804, resume) — land the Theory of MAGE
Author: "land the MAGE theory work, calls are good, prefer more predictions, naming is fine." Decisions:
- PLACEMENT: STANDALONE appendix (author's earlier "place it in an Appendix") — Appendix **E** in the v2
  scheme (A stacks / B flagships / C catalog / D skill / **E Theory of MAGE — Research Implications**). Do NOT
  fold into 6.0-implications; instead 6.0 can cross-ref E (and E can note the overlap). 
- PREDICTIONS: KEEP ALL 6 (P1-P6) — "prefer more" (add a 7th only if it's genuinely sharp + falsifiable; don't
  pad). 
- FORMALITY: directional equations (N=1 forbids a fitted SEM) — approved ("calls are good").
- NAMING: "governed-environment quality (E)" — fine, keep.
THEORY-APPENDIX wave (draws the 2 SVGs Fig T-1 causal model + T-2 velocity trajectories per the draft's specs;
writes the appendix .md from drafts/theory-of-mage-draft; wires the declared theory-of-mage-model.json into
the book-models validate; places as Appendix E in the v2 scheme). Sequence it as a restructure sub-wave BEFORE
the switch (so E is part of the v2 scheme that goes live). Hedge N=1 throughout.

## Op note — stalled book-agent diagnosis + restart (recurred 260804)
Recurring this session (FIG 500, Part-4-chapter weekly-limit, sub-wave 3 API-stall): a dispatched book agent
can hang silently. DIAGNOSTIC: transcript-output-file mtime FROZEN for minutes + NO owned build/tool proc
running (ps for catalog.py/typst) + no writes (dirty=0) + no commit = DEAD (usually API flakiness), not a slow
build. FIX: TaskStop it, confirm tree clean (HEAD unchanged, dirty=0), re-dispatch from the clean tree — split
an over-large wave into smaller ones to de-risk (the combined sub-wave 3 stalled read-only at 262KB; the split
3a completed cleanly). Book-submodule agent op (plain Agent(), not the ada-tool L1 registry) → lives here, not
the operate-repo runbook. Sub-wave-3a (8ad7500) full-suite verify pending.
