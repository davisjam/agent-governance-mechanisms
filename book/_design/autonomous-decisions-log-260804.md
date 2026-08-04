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
