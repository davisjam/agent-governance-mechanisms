# Empirical Study Design — Evidence for the MAGE Book's Quantifiable Claims

**Pre-registration of record · v2 · 260803.**

**Status: v2 — the author's red-pen rulings of 260803 folded into the v1 draft. Nothing in this
document has been measured or collected. It is a pre-registration artifact: it states, before
collection, what each measurement is, against what baseline it becomes evidence, and what result
would confirm vs. complicate each claim. The commitments bind in both directions — a complicating
result is reported, not shelved.**

**v1 → v2 changes (author rulings, 260803):**
- Window periodization is **four windows**, not three (the author's lived periodization splits the
  draft's "governed steady-state" into *hardening* and *loop-management & autonomy*).
- The measurement matrix is **pruned to the kept set** — the study leans on already-collected
  longitudinal data (the MMM drain series, git-history churn) scoped to where the author actually
  worked (`web/` + the remediate pipeline), plus cheap counts (census, real-bug yield,
  support-ratio, seat-composition). Cut rows are retained below, marked **CUT** with the author's
  reason — the record of *why* is part of the pre-registration.
- The **contrastive intra-repo baseline is dropped** (author-attention bias; see §4.2). The study's
  comparative spine is longitudinal-only, plus the one pending external point (MBSE, §3e).
- v1's MMM feasibility assessment is **corrected**: the tracer exists and drove the dispatch drain
  56% → 20.9%; MMM here means *publish the already-collected series*, not build a tool (§3c).

Grounding sources read for this design:
- Spine: `talks-and-notes/governance-catalog/book-models/argument-spine.json` (14 claims)
- Claims model: `talks-and-notes/governance-catalog/book-models/claims.json` (18 stances)
- Existing data: `talks-and-notes/governance-catalog/book/data/metrics.json` + `book/data/data-claims.json`
- Instruments: `tools/dev/run-cloc.py`, `talks-and-notes/history-mining/repo-activity-histogram.py`,
  the missing-model-metric Epic (`docs/epics/closed/missing-model-metric-260724/`),
  `system-models/missing_control_metric.py`, `system-models/governance_graph.py`,
  `talks-and-notes/history-mining/` (control catalog, emergence timeline, episodes, codebook),
  the Epic corpus (`docs/epics/`, 239 closed) and field notes (`docs/field-notes/`, 47 files),
  and the catalogue's control-coverage-census mechanism
  (`talks-and-notes/governance-catalog/models-bridge/system-models/control-coverage-census.md`).
- Author rulings: the 260803 red-pen (Q1–Q10 dispositions; recorded in §5).

---

## 1. Framing — description vs. evidence, and the pre-registration commitment

### 1.1 The methodological crux

Every number the book currently holds is a **description of ada-tool**: 22,024 commits in 19 weeks,
2.59M lines in tree, a 2.9 support ratio, a 56% orphan rate on first MMM run. A description of one
system, however precise, supports only the spine's claim 14 (`grounded-in-one-case`) and the
`single-case-humility` caveat. A measurement becomes **evidence** for a causal or comparative claim
only when it is read against a **baseline** — something the number can differ *from*:

- **Longitudinal intra-repo** — early-ada-tool vs. late-ada-tool, from git history, cut at the four
  author-ratified windows (§4.1). Did churn fall, coverage rise, the support ratio grow *as the
  governance estate matured*? This is the spine of the study (author-confirmed): the repo's own past
  is the control condition, and the controls-emergence timeline
  (`history-mining/controls-emergence-timeline.md`) dates when each treatment arrived.
- **Contrastive intra-repo** — heavily-governed vs. lightly-governed subsystems at the *same* point
  in time. **Dropped by author ruling (260803):** in a solo-author-directed repo the cut is
  hopelessly confounded with author attention — an un-drained subsystem is *not-yet-worked-on*, not
  differently-governed. Recorded in §4.2; no matrix row uses it.
- **External** — another project or a published benchmark. Scarce by construction: the one candidate
  is the author's MBSE benchmark (§3e, pending the author's artifact). Everything else external
  (industry velocity numbers, other agent-fleet reports) is not measured on comparable definitions;
  the design does not lean on it.

The honest posture, already encoded in the claims model (`grounding-case-not-proof`,
`single-case-humility`): even with baselines, this remains a **single-case field report with
within-case contrasts**. The contrasts upgrade "here is what one system looks like" to "here is what
changed inside one system when governance/modeling arrived" — hypothesis-motivating, never a proof.

### 1.2 The pre-registration commitment

For each measurement, this document states **before collection**: the datum, the instrument, the
baseline, and the interpretation rule — *result R confirms claim C; result R′ complicates it*. The
commitments bind in both directions:

1. **A complicating result is reported, not shelved.** The book already has form here (the PDL-260726
   negative result is recorded in the MMM Epic as a finding). A churn ratio that *rose* over the
   window, or an orphan rate flat across governance maturity, goes into the book's limitations, not
   into a drawer.
2. **No post-hoc re-cutting.** Window boundaries, scopes, and definitions (what is a "re-touch",
   what counts as a provenanced control) are fixed by the author's red-pen — now folded into this v2
   — *before* any collection. The four windows of §4.1 and the `web/`+remediate churn scope are
   fixed here. If a definition must change after first contact with the data, the change and its
   reason are recorded (the same correct-the-record discipline as `commits_per_day` 500→200 in
   `metrics.json` `_commit_provenance`).
3. **Provenance travels with every number.** Results land in `book/data/metrics.json` with a
   `_provenance` note (tool + flags + tree SHA + date), and load-bearing numbers get a
   `data-claims.json` entry so the `holds` lint pins them — the book's own governed-data machinery.
   (Author-ratified, Q9 — including committing this document itself as the pre-registration of
   record, so the "stated before collected" claim is auditable.)
4. **Status ceiling (author-ratified, Q10).** Any single-run or judgment-coded result caps at
   data-claims `status: preliminary` for the first edition. This binds at least the
   provenance-fraction count (§3b) and the real-bug yield (§3i); per-row `final` assignments for
   the mechanical measurements remain an open item (§5).

### 1.3 Reflexivity

This design makes the book practice its own principles on itself. Pre-registered interpretation is
the claims model's `contradicted_by` audit predicate applied to data; the provenance-pinned
`data-claims.json` entry is the alignment thesis (a sensor holding the number to the prose); the
falsifiability commitment is Part A's A.3 ("experiments must be falsifiable… correct the record when
the data contradicts you"). A study section that *couldn't* come out against the book would itself
contradict `grounding-case-not-proof`. The v1 → v2 prune is the same discipline applied to the
study itself: measurements the author judged unreliable ("not reliably measurable", attention-biased)
were cut *before* collection, and the cut is recorded rather than silently absorbed.

---

## 2. Claim inventory

Tags: **[Q]** quantifiable · **[C]** conceptual (definition / distinction / stance — argued, not
measured). Quantifiable claims are sub-tagged **quantified** (a number already exists in
`metrics.json` / `data-claims.json` and covers the claim), **partial** (some numbers exist; the
load-bearing comparison does not), **under-quantified** (essentially no number yet).
Matrix column = which §3 measurement(s) feed it — updated for the v2 prune; where a claim's planned
feed was CUT, the entry says so rather than silently narrowing the claim's evidence base.

### 2.1 Spine claims (argument-spine.json, 14)

| # | id | tag | status | already covered by | fed by (v2) |
|---|----|-----|--------|--------------------|-------------|
| 1 | `abundant-implementation` | [Q] | **partial** | commits (22,024 / 19 wk; ~200/day; peak 3,329), LoC (2.59M), refactor-cost (58 files / 5k lines / 5 h), dev cost (~$60k) — the *abundant/fast/cheap* half is well quantified. The *individually unreliable* half has no number. | (a) revert/re-touch rates on `web/`+remediate. The incident-corpus arm was CUT with (b2). |
| 2 | `fault-lies-in-instructions` | [C] | — a diagnostic stance; evidenced by episodes/RCAs qualitatively, not measurable as stated | qualitative only |
| 3 | `oversight-does-not-scale` | [Q] | **partial** | 200 commits/day exists; the comparison term (plausible human per-change review throughput) is an assumption, not a measurement | (f) support-ratio trend; arithmetic framing only |
| 4 | `churn-is-the-limit` | [Q] | **under-quantified** | 15.5M gross engineering-line churn vs 2.59M surviving is derivable from existing provenance notes but not yet a published, decomposed number; no revert rate, no re-touch rate, no trend | **(a)** — primary, scoped to `web/`+remediate |
| 5 | `three-not-knowings-cause-churn` | [C] | — a taxonomy claim ("exactly three") | — |
| 6 | `govern-the-environment` | [Q] | **partial** | mechanism census (~82) exists as a count; no coverage report, no outcome delta | **(d)** census; (f); (b) descriptive count. The (h) promotion-recurrence feed was CUT. |
| 7 | `modeling-thesis` | [Q] | **partial** | MMM pilot 56% (dispatch subsystem, 144 tests) + the model-loop's own 56%→20.9% drain; mbse-nav-token pilot (−20/−12/−82/−50%, N=4, preliminary) | **(c)** — primary (drain series, longitudinal, dispatch-scoped); (i) |
| 8 | `alignment-thesis` | [Q] | **under-quantified** | no recurrence-before/after numbers; drift-gate catch counts uncollected | **No planned measurement after the v2 prune** — both candidate feeds ((b2) recurrence, (h) promotion-recurrence) were CUT as unreliable. The claim stays argued on the episodes' qualitative evidence; recorded as an accepted limitation (§4.4). |
| 9 | `theses-treat-the-causes` | [C] | — a mapping claim | — |
| 10 | `failures-become-machinery` | [Q] | **partial** | episodes reports + emergence timeline are qualitative/chronological; the *fraction of controls with a documented originating failure* is uncounted | **(b)** — descriptive provenance-fraction only (downgraded per author ruling) |
| 11 | `sync-cost-reduced` | [Q] | **under-quantified** | "kept in sync for cents" is asserted; no measured sync cost | **No planned measurement after the v2 prune** — (g) was cut with the Q8 prune (judgment-heavy coding pass). The assertion stays an assertion; recorded as an accepted limitation (§4.4). |
| 12 | `mage-becomes-practical` | [Q] | **partial** | model-zoo census (29 named models; 7,380 model LoC), nav-token pilot; the *practicality* contrast (why it wasn't practical before) rests on the external MBSE baseline | **(e)** — pending author artifact; (c) |
| 13 | `seat-moves` | [Q] | **partial** | "six to eight agents", "four accounts" are anecdote-grade; the human-vs-agent share of authored change is measurable and unmeasured | (j) — late-window only |
| 14 | `grounded-in-one-case` | [C] | — the study's own frame; this design document is its enforcement | all (by discipline) |

### 2.2 Claims-model stances (claims.json, 18)

Most are definitions/distinctions — argued in prose, checked by the claims model's own audit
predicates, not measured. Tagged [Q] only where a measurement genuinely bears:

| id | tag | note (v2) |
|----|-----|-----------|
| `churn-is-symptom` | [C] | causal taxonomy; (a) can show churn *exists and moves*, not that its causes are exactly three |
| `constraint-prevents-sensor-detects` | [C] | definitional |
| `convert-failures-to-controls` | [Q] **partial** | same evidence base as spine 10 → **(b)** descriptive provenance-fraction only |
| `direction-agnostic` | [C] | scope claim |
| `double-win` | [Q] **partial** | context win: nav-token pilot (exists, N=4). Quality win: real-bug ledger from model-loop (3–4 confirmed bugs in Epic notes, uncounted formally) → (c), (i) |
| `fleet-scaling-bounds` | [Q] **under-quantified** | "bounded by reasoning+context, not N²": (a)'s churn trend at rising agent count is weak indirect evidence; honest tag: mostly argued, hard to measure |
| `governance-not-on-the-dial` | [C] | framing distinction |
| `grounding-case-not-proof` | [C] | methodological stance — enforced by §1.2 |
| `mechanize-not-remember` | [Q] **under-quantified** | its direct test, (h) soft→hard promotion recurrence, was CUT in the v2 prune — no planned measurement; stays argued (§4.4) |
| `model-not-mechanism-until-enforced` | [C] | definitional boundary |
| `models-are-universal-language` | [C] thesis | its testable corollary was spine 11 → (g), CUT; stays argued |
| `printer-not-coder` | [C] | metaphor |
| `seat-moves-not-lifecycle` | [Q] **partial** | → (j), late-window only |
| `single-case-humility` | [C] | enforced by §1.2 / §4.4 |
| `soft-to-hard-spectrum` | [Q] **under-quantified** | its direct test, (h), was CUT in the v2 prune — no planned measurement; stays argued (§4.4) |
| `ssot-not-snapshot` | [C] | drift incidents evidence it qualitatively; no planned measurement |
| `theses-divide-the-not-knowings` | [C] | mapping |
| `three-not-knowings` | [C] | taxonomy |

**Roll-up.** Of 32 claims: 18 conceptual, 14 quantifiable. Of the 14: **0 fully quantified**
(everything currently published is one-armed — a number without its baseline), 9 partial,
5 under-quantified. The gap is uniform in kind: the *descriptive* arm exists; the *comparative* arm
(over time, against the pending external benchmark) is what this study adds. **The v2 prune
deliberately leaves four quantifiable claims without a planned measurement** — spine 8
(alignment recurrence), spine 11 (sync cost), `mechanize-not-remember`, and `soft-to-hard-spectrum`
— because their candidate measurements were judged unreliable or disproportionately costly. Those
claims stay argued, and the book says so, rather than resting on numbers the author does not trust.

---

## 3. The measurement × baseline × interpretation matrix

One row per candidate measurement, **pruned to the author's kept set (Q8, 260803)**. Cut rows are
retained, marked **CUT**, with the author's reason — deleting them would erase the record of why
they were rejected, which is itself pre-registration content. Fields on kept rows: **datum** ·
**instrument** · **baseline** · **pre-registered interpretation** · **feasibility**.

> Feasibility grades: **LOW** = re-run an existing tool with flags; **MED** = extend an existing
> tool or write a bounded script over existing data; **HIGH** = new instrument or judgment-heavy
> coding work.

**KEPT (6):** (a) churn on `web/`+remediate · (b) provenance-fraction, descriptive · (c) MMM drain
series · (d) control-coverage census at HEAD · (f) support-ratio trend · (i) real-bug yield ·
(j) seat-composition, late-window. Plus **(e)** MBSE — pending the author's artifact.
**CUT:** contrastive-subsystems arm (was inside (c) and §4.2) · (b2) failure→control recurrence ·
repo-wide re-touch (was (a3)'s scope) · (g) sync cost · (h) soft→hard promotion recurrence.

### (a) CHURN, scoped to `web/` + the remediate pipeline — the wasteful-work slice *(seeds spine 4; reliability side of spine 1)* — KEPT, RESCOPED

**Author ruling (Q4, 260803): repo-wide churn/re-touch is attention-biased** — "we re-touch what I
see is broken" — so the repo-wide cut is OUT. The measurement is **rescoped to the sustained-work
core**: `web/` plus the remediate pipeline (the C# remediation core), where multi-month continuous
work makes the signal real rather than an artifact of where the author happened to look. The exact
path-set for "remediate pipeline" is an open definition item (§5-O1); the scope decision itself is
fixed here.

Three sub-measures, deliberately separated because they answer different objections. All three run
over the scoped path-set only; the four windows of §4.1 are the longitudinal axis.

**a1 — Gross churn ÷ surviving code, per window (scoped).**
- *Datum:* (added+deleted engineering lines in window, within scope) ÷ (surviving in-scope LoC at
  window end). The whole-history repo-wide figure (≈15.5M churned vs 2.59M surviving, ≈6:1) remains
  citable as *description*, but the evidential series is the scoped one.
- *Instrument:* `talks-and-notes/history-mining/repo-activity-histogram.py` (per-day CSV;
  `--since` for windows; vendored-line and sentinel/tombstone exclusions and the patch-id
  no-double-count verification are already built in — reuse, don't re-derive), restricted to the
  scoped paths, + `tools/dev/run-cloc.py` at historical checkouts for the denominator.
- *Baseline:* longitudinal — the ratio per window (the four §4.1 windows).
- *Interpretation:* churn-is-the-limit predicts high absolute churn *plus* a governance effect.
  **R (confirms):** the wasteful sub-slices (a2, a3 below) fall as controls come online, even if
  gross churn stays high (gross churn includes healthy refactoring — A.2 says refactoring is nearly
  free, so gross churn alone can't distinguish waste from health). **R′ (complicates):** wasteful
  slices flat or rising across governance maturity → either governance didn't bite on churn, or the
  claim's mechanism needs restating. **Pre-registered caution:** a *rising gross* ratio with
  *falling waste* slices is consistent with the book and must not be spun either way.
- *Feasibility:* a1 numerator LOW–MED (the CSV exists at `history-mining/repo-activity-by-day.csv`;
  the path-scoped re-cut is a re-run with a path filter); denominator MED (run-cloc at the four
  window boundaries; the tool reads the working tree, so this needs detached checkouts in a scratch
  clone — read-only w.r.t. the live repo).

**a2 — Revert rate (scoped).**
- *Datum:* fraction of in-scope commits per window that are reverts (`git log --grep`-class match on
  Revert-shaped subjects + `git revert`-generated bodies), and lines reverted.
- *Instrument:* small extension of the histogram's parse (it already classifies subjects for the
  sentinel/tombstone exclusion — same seam).
- *Baseline:* longitudinal per window.
- *Interpretation:* **R:** revert rate falls after the merge-train/gate staircase matures (late-May
  per the emergence timeline — the W2→W3 boundary) → supports spine 4 + the reliability half of
  spine 1 ("individually unreliable" — the environment, not the agent, ends up holding the line).
  **R′:** flat/rising → either gates catch pre-merge (so reverts were always rare — check the
  absolute level first) or governance isn't reducing undo-work. **Caution:** in this repo `revert`
  is also the *sanctioned* undo (rule #36) — a revert is sometimes the control working, not a
  failure. Report both readings.
- *Feasibility:* MED (bounded script; definitional edge cases go to §5-O2).

**a3 — Re-touch rate (the sharpest waste proxy) — scoped; repo-wide variant CUT.**
- *Datum:* fraction of in-scope file-touches that modify a file already changed within the previous
  N days by a *different* work unit (different Epic / different agent branch), per window.
  Distinguishes "planned multi-phase work" from "undoing/redoing recent work". **The repo-wide
  variant is CUT (Q4): attention bias makes the repo-wide number unmeaningful.**
- *Instrument:* new bounded script over `git log --numstat --no-merges` (no existing tool computes
  per-file touch intervals; propose it as a sibling in `talks-and-notes/history-mining/`).
- *Baseline:* longitudinal only (the contrastive governed-vs-ungoverned-subtree variant is CUT with
  §4.2).
- *Interpretation:* **R:** short-interval cross-unit re-touch falls as the estate matures →
  the most direct churn-decomposition support for spine 4. **R′:** flat → churn framing survives
  (churn was still the felt limit) but the *"governance reduced it"* implication weakens; report as
  a limitation. **Caution:** hot-spot files (e.g. within scope, `web/pipeline.py`-class files) are
  re-touched by design (rule #50); pre-register an exclusion or report with/without (§5-O2).
- *Feasibility:* MED–HIGH (script is easy; the *work-unit attribution* — same-Epic vs cross-Epic —
  needs the Commit-of/Epic-citation trailers, which exist only after the discipline landed →
  attribution is only clean in W3–W4; pre-register that asymmetry).

### (b) FAILURE→CONTROL provenance *(seeds spine 10, spine 6; `convert-failures-to-controls`)* — DOWNGRADED to a descriptive count; recurrence arm CUT

**Author ruling (Q3, 260803): the recurrence arm (v1's b2 — incident counts before vs. after a
control landed) is CUT — "not reliably measurable, smells like BS."** Incident-counting is too
detection-biased (recording discipline itself matured over the window) and too judgment-laden to
carry evidence weight. What survives is at most the plain **provenance-fraction** below, kept as a
**clearly-labelled descriptive count** — composition, not comparison, not causal evidence — and
only if it earns its place in the book.

**b1 — Fraction of controls with a documented originating failure (descriptive count only).**
- *Datum:* over the control estate, the share whose introducing Epic / field note / RCA names the
  concrete failure it retired, vs. controls installed by foresight (A.24 design-time) vs.
  unprovenanced. Three-way split, reported as composition.
- *Instrument/data:* the Epic corpus (`docs/epics/closed/`, 239 Epics with §1 Rationale sections),
  `docs/field-notes/` (47), and the already-coded history-mining corpus:
  `history-mining/control-catalog.yaml` + `coding/CONTROL-CODEBOOK.md` +
  `controls-emergence-timeline.md` + the episodes reports. Much of the *coding work is already
  done* — this is largely a counting pass over an existing codebook, extended to controls added
  since its 260626 refresh pin.
- *Denominator (author-ratified, Q7):* **the `governance_graph.py` typed control node-set for
  measurement; the catalogue's 82 mechanisms for exposition** — they are different populations (the
  catalogue is curated-for-publication; the graph is the live typed set), and the mapping between
  them is stated wherever the number appears.
- *Baseline:* none — this is a composition claim, not a comparison, and the book must present it as
  such. A large foresight-installed share is *not* a refutation (A.24 exists) but changes the
  emphasis; the book's claim is "failures become machinery", not "all machinery came from failures".
- *Interpretation:* **R:** a majority of controls trace to a named failure → grounds spine 10 as
  description ("this is in fact how most of the estate arose"). **R′:** provenance mostly
  missing/unreconstructable → the claim stands only on the episodes' qualitative evidence; say so.
  Either way the number ships labelled *descriptive*, capped at `preliminary` (judgment-coded,
  §1.2 #4).
- *Feasibility:* MED (judgment coding, but the codebook + catalog exist; needs one careful pass).
  The precise coding rule for "names an originating failure" is §5-O3.

**b2 — Incident recurrence before vs. after the control. — CUT (author, Q3).** Retained here only
as a record: v1 proposed mining incident occurrences from field notes / Epic rationales / commit
messages and counting the K weeks before vs. after each control landed. The author's reason for the
cut: detection bias is unfixable (incidents are recorded far more diligently late in the window),
the incident definition is irreducibly judgment-laden, and a number built on both would be
BS-shaped. Consequence, stated honestly: **spine 8 (alignment-thesis) loses its planned
quantitative feed and remains argued** on qualitative episode evidence (§2 roll-up, §4.4).

### (c) MISSING-MODEL COVERAGE — publish the drain series *(seeds spine 7; spine 12; `double-win` quality arm)* — KEPT, corrected + rescoped

**v1 correction (author, Q6):** v1 said "a standing production MMM tool does not exist yet" and
graded whole-tree extension HIGH on that basis. The author's correction stands: **the tracer is
present, done, and drove coverage** — it is the instrument that produced the dispatch drain
56% → 20.9%, re-run repeatedly across the model-loop with per-step provenance in the Epic. There is
no tool-building cost in the kept measurement. (A whole-tree extension would reuse the existing
`traceability` machinery — but the contrastive angle it served is dropped per Q2, so it is moot for
this study.)

**Author ruling (Q2): the contrastive extension — fresh MMM runs on 2–4 lightly-modelled
subsystems — is CUT.** Un-drained subsystems are un-drained because the author has not worked there
(admin-dashboard explicitly invalid — never worked); the contrast would measure author attention,
not modeling. **The MMM story is longitudinal-only: publish the already-collected dispatch-scoped
drain series, honestly scoped as such.**

- *Datum:* the model-loop's drain series on the dispatch subsystem —
  **56% (260724) → 39% → 32.2% → 30.1% → 20.9% (260726)** orphan rate (fraction of tests / reached
  prod code not tracing to a typed model node), with per-step provenance in
  `docs/epics/closed/missing-model-metric-260724/`.
- *Instrument:* the MMM tracer from that Epic (already run; the "measurement" is publication of the
  collected series with its provenance). Companion instruments for context:
  `tools/unit_test_all/traceability_coverage.py` (the model→code direction) and
  `system-models/coverage_ref.py`.
- *Baseline:* longitudinal — the series *is* its own baseline (the 56% start-point is pre-treatment;
  each drain step is dated). This is the single cheapest upgrade the study offers: the comparative
  arm already exists in the Epic record and has merely never been published as a series.
- *Interpretation:* **R:** the drain curve is monotone and steep relative to its dispatch cost
  (count the dispatches per cluster from the Epic — they're recorded) → supports spine 7 (models
  are load-bearing where they exist) and spine 12's cheapness arm. Bonus arm: the model-loop's
  confirmed real bugs (editor lost-update race, queue_depth drift — real-bug ledger #3, #4)
  quantify `double-win`'s quality claim → **(i)**. **R′:** publication-grade re-verification shows
  the series was measured under shifting definitions between steps → report the definitional drift
  and downgrade to a two-point before/after. **Scope honesty (pre-registered):** the series is
  dispatch-subsystem-scoped and the book must not present it as tree-wide; the claim it supports is
  "the loop drains orphans where it is run", not "the tree is 21% orphaned".
  **Caution (from the pilot itself):** the rate is a lower bound (import-reach over-counts), and
  the missing-control sibling teaches the decomposition lesson — never publish the scalar without
  the raw → test-excluded → genuine split.
- *Feasibility:* LOW (the data is collected; this is a provenance-checked write-up into
  `metrics.json` + `data-claims.json`).

### (d) CONTROL-COVERAGE CENSUS report at HEAD *(seeds spine 6)* — KEPT

- *Datum:* the live control estate rolled up per governance target (agent / models-bridge /
  product), with per-target soft/hard composition and empty-or-soft-only cells flagged as gaps;
  plus the missing-control decomposition (`system-models/missing_control_metric.py`: raw 0.914 →
  test-excluded → genuinely-ungoverned ≈12% on the fleet-lifecycle surface).
- *Instrument:* the control-coverage-census mechanism (catalogue entry #82,
  `models-bridge/system-models/control-coverage-census.md`) over
  `system-models/governance_graph.py`'s typed control node-set; `missing_control_metric.py` for the
  code→control direction. Both exist and are runnable. Denominator discipline per Q7: graph for
  measurement, catalogue for exposition, mapping stated (§3b).
- *Baseline:* weak by nature — a coverage report describes the estate; kept as a **HEAD snapshot**
  (the v1 option of re-deriving the census at historical checkouts is not pursued — the typed
  node-set likely does not resolve at old checkouts; the emergence timeline already gives the
  qualitative early-window story: 0 controls Wk 1 → a control class every few days post-Apr-10).
  The internal yardstick is the census's own closed-taxonomy claim ("every target non-empty").
- *Interpretation:* **R:** all three targets non-trivially covered, hard enforcement present in
  each, genuinely-ungoverned slice small → supports spine 6 as *achieved practice*, not aspiration.
  **R′:** a target empty or soft-only → itself a book-grade finding (the census mechanism's whole
  point is that this is a first-class gap — reporting it *demonstrates* the mechanism while
  complicating the "the environment is governed" reading). This row is unusual: either result
  serves the book if reported straight.
- *Feasibility:* LOW (run existing tools at HEAD).

### (e) MBSE BENCHMARK — the external baseline *(bears on spine 12; contextualizes spine 7)* — PENDING author artifact

**Status (author, Q5): STAY TUNED — the author is supplying the external negative-result
artifact.** The row is held open as **the one external baseline** in the study. It is **distinct
from the in-repo `mbse-nav-token` A/B pilot** in `data-claims.json` — that is a different,
*positive*, internal result (N=4 tasks, −35% median tokens-to-answer, preliminary); this row is the
author's prior *negative-result* benchmark of LLM/agent performance on classical MBSE tasks,
presumed to live in the author's academic-lab materials. Nothing below activates until the artifact
and its citable numbers arrive (§5-O4).

- *Instrument:* none to run — this is a citation of completed external work.
- *Baseline role:* **contrastive framing, not replication**: unaided LLMs perform poorly on
  classical MBSE artifacts (the negative result) *and yet* inside a governed environment with
  executable, drift-gated models the practice became routine (the case evidence: 29-model zoo, the
  sync machinery, the nav-token pilot). The gap between the two is precisely spine 12's claim —
  practicality came from the environment, not from raw model capability.
- *Pre-registered interpretation:* **R (the pairing holds):** benchmark-negative + case-positive →
  supports spine 12's mechanism ("agents cut the sync cost *within an engineered environment*").
  **R′:** if the benchmark's task set overlaps what ada-tool's models actually demand (i.e. the
  case succeeded at tasks the benchmark also scores well), the contrast evaporates — check task
  comparability before leaning on it. Also pre-register the deflationary reading: the benchmark
  may show current models *can't* do classical MBSE, which bounds spine 12 ("practical" = the
  lightweight executable-zoo styles, not SysML-grade MBSE) — arguably the book's actual position;
  confirm with the author when the artifact lands.
- *Feasibility:* LOW effort, blocked on the artifact (§5-O4).

### (f) Governance-investment share over time *(seeds spine 6; framing for spine 3)* — KEPT

- *Datum:* support_loc/prod_loc (currently 2.9 at one point, 2026-08-03 refresh) re-measured at the
  four window boundaries via `run-cloc.py --json` — a **four-point trend**, per the author's
  windows.
- *Baseline:* longitudinal (the four windows).
- *Interpretation:* **R:** the support ratio *grew* as the fleet scaled → quantifies spine 6's
  "build the environment first" as revealed preference (the system spent most of its lines on the
  environment). **R′:** flat from week 1 → the environment wasn't *built up* in response to scale;
  reframe.
- *Feasibility:* MED (same scratch-clone checkouts as a1; `system-models/components.py` category
  map may not resolve cleanly at early checkouts — degrade to coarse categories and say so).

### (g) Sync cost — CUT (Q8 prune)

Retained as a record. v1 proposed counting model-regeneration/drift-fix commits per week vs.
model-estate size as spine 11's direct test. **Cut in the author's Q8 prune: not in the kept set.**
It requires a judgment-heavy commit-coding pass (attributing commits to "sync") — new collection of
exactly the kind the leaner study avoids, with attribution ambiguity adjacent to the Q3 concern.
Consequence, stated honestly: **spine 11 ("kept in sync for cents") remains an assertion** in the
first edition, and the book's limitations say so (§2 roll-up, §4.4). *(Flag: the ruling cut this by
omission from the KEEP list rather than by named reason; the reason given here is inferred from the
prune's stated rationale.)*

### (h) Soft→hard promotion recurrence — CUT (Q8 prune)

Retained as a record. v1 proposed finding-counts before vs. after AUDIT-ONLY→BLOCKING promotions
(rule #55) for 5–8 sampled lints, as the direct test of `soft-to-hard-spectrum` +
`mechanize-not-remember`. **Cut in the author's Q8 prune: not in the kept set.** It requires
re-running lints at historical checkouts — new collection, not already-collected data — and its
finding-count-as-recurrence-proxy shares the Q3 measurability concern in milder form. Consequence:
both stances remain argued (§2.2), recorded as an accepted limitation (§4.4). *(Flag: cut by
omission from the KEEP list, as with (g); reason inferred from the prune's stated rationale.)*

### (i) Real-bug yield of modeling *(quantifies `double-win`'s quality arm; feeds spine 7)* — KEPT

- *Datum:* bugs confirmed by model-loop clusters (real-bug ledger entries #3, #4, …) per cluster
  modelled; plus SimWorld/property-check finds.
- *Instrument:* counting pass over Epic notes (the ledger entries are recorded).
- *Baseline:* none — a count, reported as a count, never a rate (N is small).
- *Interpretation:* **R:** a non-trivial count of confirmed real bugs found *by the modeling loop
  itself* → `double-win`'s quality arm has at least existence-grade evidence. **R′:** on
  re-verification some ledger entries turn out not to be model-loop-attributable → publish the
  corrected smaller count.
- *Feasibility:* LOW. Caps at `preliminary` (judgment-coded attribution, §1.2 #4).

### (j) Seat-moves composition — KEPT, late-window only *(feeds spine 13)*

- *Datum:* share of commits/lines by author class (agent-dispatched vs. orchestrator-inline vs.
  human-typed), from commit trailers (`Co-Authored-By`, `Commit-of`, role prefixes) — **W4 only
  (and W3 where trailer discipline already held)**, per the author's kept-set scoping. Early-window
  attribution is unreliable because the trailer discipline itself matured; rather than pre-register
  an asymmetry caveat (v1's approach), v2 simply does not measure the early windows.
- *Baseline:* none across windows (composition at a point, honestly scoped); the claim it feeds is
  compositional, not longitudinal.
- *Interpretation:* **R:** implementation share overwhelmingly agent-authored while
  design/ratification artifacts (Epic §G rulings, STRATEGY) stay human → seat-moves, measured (for
  the mature regime — which is the regime the claim describes). **R′:** trailers too inconsistent
  even late → report the classification-failure rate and decline the number.
- *Feasibility:* MED.

---

## 4. Baselines — the load-bearing section

### 4.1 Longitudinal intra-repo (the spine of the study) — FOUR windows (author-ratified, Q1)

The repo's own history is the control condition. The treatment — the governance estate — arrived
datably: `controls-emergence-timeline.md` records ~0 controls before Apr 10, an inflection at the
casual→conventional-commit boundary (Apr 10–14), architectural controls through May, and the
agent-substrate hardening late May–June. The window boundaries are **fixed here by the author's
lived periodization** (Q1 ruling — v1's three-window option (ii) split at its third window):

| window | span | character |
|--------|------|-----------|
| **W1 — prototype** | Mar 12 – Apr 9 | pre-governance greenfield; ~0 controls |
| **W2 — mechanization** | Apr 10 – May 31 | conventional-commit inflection; architectural controls arrive |
| **W3 — hardening** | Jun 1 – Jun 30 | agent-substrate hardening; gate staircase matures |
| **W4 — loop-management & autonomy** | Jul 1 – present | governed steady-state operated as loops; autonomy discipline |

All longitudinal rows ((a), (f)) cut at these four boundaries; no post-hoc re-cutting (§1.2 #2).

What the longitudinal design can and cannot say — pre-registered:

- **It can show co-movement:** wasteful-churn slices (a2/a3, scoped) and support-ratio (f) plotted
  against the emergence timeline, and the MMM drain series (c) as a dated within-case curve.
- **It cannot cleanly separate three confounds that all trend the same direction:** (1) model
  capability improved across the window (Claude versions, March→July); (2) the author learned;
  (3) the codebase matured (early churn is partly normal greenfield exploration, not
  governance-absence). Any "it got better over time" result is jointly caused. The book should
  claim co-movement + mechanism plausibility, no more. (v1 offered the b2 staggered before/after
  design as the sharpest escape from the global-trend confound; with b2 cut, the study accepts the
  confound and says so.)
- **Denominator discipline:** all longitudinal rates normalize by activity (commits or
  engineering-LoC from the histogram), never raw counts — activity varied 10× across weeks.

### 4.2 Contrastive intra-repo — DROPPED (author, Q2)

v1 proposed same-time cuts: heavily-modelled dispatch vs. un-drained MMM-backlog subsystems (for c),
and sole-seam vs. no-seam code (for a3/b). **The author dropped the contrastive baseline entirely:
in a repo whose work allocation is one author's attention, "lightly-governed subsystem" means
"subsystem the author has not worked on yet", not a governance difference** — the selection bias v1
flagged is not a caveat but a disqualification. Admin-dashboard, a v1 candidate, is explicitly
invalid (never worked). No kept row uses a contrastive baseline; the comparative spine of the study
is longitudinal-only (§4.1) plus the pending external point (§3e).

### 4.3 External

Scarce, and the design says so plainly. The MBSE benchmark (e) is the one usable external point —
pending the author's artifact — and it is a *framing* baseline, not a matched comparison. Published
industry agent-fleet numbers are not collected on comparable definitions (commit conventions,
exclusion rules, what counts as engineering LoC) — the study declines the comparison rather than
false-precision it. This scarcity is itself worth one honest sentence in the book's limitations:
single-case field reports are what the field has right now.

### 4.4 The honesty budget

Every kept row carries at least one pre-registered caution (sanctioned-revert semantics in a2,
scope honesty + lower-bound semantics in c, composition-not-comparison framing in b1, trailer
scoping in j). These are commitments: the caution ships next to the number, in the same
`_provenance` note.

The v2 prune adds a second class of honesty commitments — **accepted limitations**, claims the
study deliberately leaves unquantified because the candidate measurement was judged unreliable or
disproportionate:

- **spine 8 (`alignment-thesis`)** — recurrence-before/after cut (Q3); stays argued on qualitative
  episode evidence.
- **spine 11 (`sync-cost-reduced`)** — sync-cost coding pass cut (Q8); "for cents" stays an
  assertion.
- **`soft-to-hard-spectrum` / `mechanize-not-remember`** — promotion-recurrence cut (Q8); stay
  argued.

The book's limitations section names these as *chosen* gaps — measurements rejected at
pre-registration for reliability reasons — which is a stronger position than numbers the author
would not defend under hostile review.

---

## 5. Author dispositions and remaining open items

### Resolved (author red-pen, 260803)

- **Q1 — windows:** FOUR — prototype (Mar 12–Apr 9) · mechanization (Apr 10–May 31) · hardening
  (Jun 1–Jun 30) · loop-management & autonomy (Jul 1–present). Fixed in §4.1.
- **Q2 — contrastive subsystems:** DROPPED as a baseline class (author-attention bias;
  admin-dashboard invalid). §4.2.
- **Q3 — failure→control recurrence:** DROPPED ("not reliably measurable"); at most the
  provenance-fraction survives as a clearly-labelled descriptive count. §3b.
- **Q4 — churn/re-touch scope:** RESCOPED to `web/` + the remediate pipeline; repo-wide re-touch
  OUT. §3a.
- **Q6 — MMM:** v1's feasibility assessment corrected — the tracer exists and drove the 56%→20.9%
  drain; the measurement is publish-the-series (dispatch-scoped, longitudinal). §3c.
- **Q7 — control-estate denominator:** graph (`governance_graph.py`) for measurement, catalogue
  (82 mechanisms) for exposition, mapping stated wherever the number appears. §3b, §3d.
- **Q8 — row scope:** pruned to KEEP = {MMM drain series, churn-on-`web/`+remediate,
  control-coverage census at HEAD, support-ratio trend (4 windows), real-bug yield,
  seat-composition (late-window)}; (e) MBSE pending. CUT = {contrastive-subsystems,
  failure→control recurrence, repo-wide re-touch, (g) sync cost, (h) promotion recurrence}.
- **Q9 — where results land:** numbers → `metrics.json` (+`_provenance`); load-bearing →
  `data-claims.json` with `holds`; this document committed to `book/_design/` as the
  pre-registration of record.
- **Q10 — status ceiling:** ratified as a rule — single-run or judgment-coded results cap at
  `preliminary` for the first edition (binds b1, i; see O5 for per-row assignment).

### Still open

- **O1 — Exact path-set for the churn scope (a).** "`web/` + the remediate pipeline" needs a fixed
  path list before collection: presumably `web/**` plus the remediation core under
  `backend/src/AdaTool.*` (which projects exactly — Cli? the format Models? Checking?). Fix the
  list, then no post-hoc changes (§1.2 #2).
- **O2 — Re-touch window N and exclusions (a3), and revert semantics (a2).** N = 7, 14, or 30 days?
  Exclude same-Epic re-touches? Exclude in-scope hot-spot files (rule #50 class) or report
  with/without? Do sanctioned rule-#36 reverts count as churn or as the control working (recommend:
  report both readings, per §3a2)?
- **O3 — Provenance-fraction coding rule (b1).** What counts as "names an originating failure":
  field note or RCA or Epic-§1 rationale naming a concrete failure (recommended); is
  commit-message-only evidence admitted as "trace-grade" or excluded?
- **O4 — MBSE artifact (e).** Awaiting the author's negative-result artifact: where it lives, what
  it measured, which numbers are citable, and whether the deflationary reading (§3e R′) is the
  book's intended position.
- **O5 — Per-row status ceilings.** The Q10 rule is ratified; the per-row assignment is not: which
  of the mechanical measurements ((a), (c), (d), (f), (j)) may print as `final` vs `preliminary`
  in the first edition?
