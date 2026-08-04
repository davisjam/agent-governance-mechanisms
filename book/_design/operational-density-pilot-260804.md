# Operational-density pilot — does the book deliver a concept OR an artifact per chapter?

**Status:** PILOT (go/no-go). READ-ONLY analysis + design. No model edited.
**Date:** 2026-08-04
**Question (author):** A chapter earns its place when it delivers something the reader can DO
tomorrow — an **operational artifact** — *or* a genuine theoretical **concept**. Bake a per-chapter
`delivers` field into the models so we can find chapters that deliver **neither**, and chapters that
are **all-prose where an artifact would clearly sharpen them**. Framing is **concept OR artifact** —
a conceptual chapter is NOT a gap; do not force an artifact into every chapter.

**Typed artifact vocabulary (pilot closed set):** decision-tree · checklist · pattern · commandment ·
litmus-test · anti-pattern · smell · review-question. Candidate additions surfaced below:
**framework/table** and **worked-example** (and **evidence-table**) — see §5.

**Bottom line up front:** the book is **denser than the hypothesis feared.** Of ~34 content chapters,
**0 deliver neither**. 26 already carry a typed operational artifact; 4 are legitimately concept-only;
**2 are the real finding — operational chapters that describe their artifacts in prose instead of
showing them.** The field is worth adding to the model *as a coverage lens and a latent-artifact
finder*, not as a gap alarm — because the alarm would fire ~0 times. Go, but scoped small. Details in §5.

---

## 1. Genre-check: where the `delivers` field belongs

**Recommendation: extend `chapter_shape` (the declared→generated per-chapter model).** Do NOT invent a
new sibling model, and do NOT overload `outcomes`.

### Why not a new model
The book already runs a **7-sibling declared→generated model family** under `book-models/`
(outline / outcomes / concepts / big-ideas / claims / argument-spine / chapter-shape), each with the
same shape: a hand-authored `*_declared.json`, a generator that joins it against the book IR and the
spine, a materialized `*.json` artifact, structural invariants, and a `catalog.py` view. The homing
rule the repo already applies (`chapter_shape_model.py` docstring): *a new model earns its own file
only for distinctive fields that belong to no sibling.* `delivers` is **per-chapter**, so it belongs on
the existing per-chapter model — `chapter_shape` — not a ninth file.

### Why `chapter_shape`, not `outcomes`
They look adjacent but are distinct, and the `outcomes` model's own docstring already draws the line:

| Model | Answers | Grain |
|---|---|---|
| `outcomes` | what the reader can **DO** after the unit (action-verb + object, Bloom-tagged) | pedagogical |
| `chapter_shape` | **HOW** the chapter opens and closes (rhetorical: failure/answer/thesis · consequence/transition/synthesis) | rhetorical |
| **`delivers` (new)** | **WHAT the chapter hands over** — the concept(s) and/or the operational artifact(s) | deliverable |

`delivers` is the *payload*; `outcomes` is the *capability the payload confers*; `chapter_shape` is the
*prose frame around it*. Two chapters can share an outcome ("size a transformation") while delivering
different payloads (a concept vs. a decision-tree). `chapter_shape` is already the per-chapter,
hand-assessed, spine-joined home; `delivers` is a fourth block beside `opening` / `closing` / `note`.

### The exact declared → generated shape

Add to each record in `chapter_shape_declared.json` (hand-authored):

```json
{
  "slug": "2.4-lifecycles-and-runbooks",
  "opening": { "...": "..." },
  "closing": { "kind": "..." },
  "delivers": {
    "concepts": ["lifecycle", "failure-mode-effects-analysis", "runbook", "rubric", "pre-canned-brief"],
    "artifacts": [
      { "type": "framework", "name": "config-optimization runbook figure", "anchor": "runbook-split" }
    ]
  },
  "note": "..."
}
```

- **`concepts`** — a list of concept slugs. **Do NOT re-key by hand.** Derive/validate against the
  `index-def:` tags harvested from the chapter's own prose (the join `build_book_html._harvest_concept_tags`
  already computes; `concepts.json` uses it as SSOT). A declared concept that is not an `index-def` site
  in that chapter is a finding (DV2 below). This makes `concepts` a *cheap join*, not a second copy.
- **`artifacts`** — hand-authored list of `{type, name, anchor?}`. `type ∈ ARTIFACT_TYPES` (the closed
  set). `anchor` optionally points at an existing `<!-- label: … -->` so a drift check can confirm the
  named figure/table still exists (mirrors `chapter_shape`'s existing `opening_anchor`/`closing_anchor`
  staleness guard, CS5).

Generated block in `chapter-shape.json`, and DERIVED flags (never authored, mirroring the existing
`flags` worklist):

```json
"delivers_flags": {
  "delivers_neither": [ /* non-exempt chapter with empty concepts AND empty artifacts */ ],
  "all_prose_would_benefit": [ /* AUTHOR-marked: artifacts empty but chapter is operational-register */ ]
}
```

`delivers_neither` is **fully derivable** (empty ∧ empty ∧ non-exempt) → a real gap alarm.
`all_prose_would_benefit` is **judgment**, so it is an authored boolean (`"artifact_would_help": true`)
surfaced into the worklist — the model *carries* the author's flag, it does not invent it.

### Invariants (mirror the existing CS1–CS5 / DL1–DL3 style)

- **DV1 (enum):** every `artifacts[].type ∈ ARTIFACT_TYPES`.
- **DV2 (concept join-integrity):** every `delivers.concepts` slug is an `index-def` site in *that*
  chapter (join against the harvested tags) — catches a hand-keyed concept that drifted.
- **DV3 (artifact-anchor freshness):** every `artifacts[].anchor` resolves to a live `<!-- label: … -->`
  in the chapter (a renamed/deleted figure reddens — same discipline as CS5).
- **DV4 (coverage):** every non-exempt chapter has a `delivers` block (exhaustive, like CS2).

### The `catalog.py` view

Add `cmd_delivers` → `catalog.py delivers`, modeled exactly on `cmd_substantiation` / `cmd_views_audit`:

- prints the **coverage map** (one row per chapter: concepts | artifacts[type] | verdict);
- prints the two reports — `DELIVERS-NEITHER` (derived) and `ALL-PROSE-WOULD-BENEFIT` (author-flagged);
- `--json` for the machine form;
- fold the DV1–DV4 findings into the existing `views-audit` surface (audit-only-first, exits 0 unless
  `--strict`) so committers see delivers-drift in the one place they already look.

This is the rule-#33 "stable lint reads meta-files at query time" form the repo prefers — no codegen,
no snapshot.

---

## 2. Whole-book coverage map (34 assessed content chapters)

Verdict legend: **A** = has-artifact (delivers a typed operational artifact) · **C** = concept-only-OK
(delivers a real concept; prose is fine) · **P** = all-prose-would-benefit (delivers a concept but an
artifact would clearly sharpen it) · **N** = GAP-neither · **apx** = apparatus (no deliverable expected).

Concept column = `index-def` canonical sites (the chapter *is* that concept's home). Artifact column =
the operational artifact(s) actually present, by type.

| Chapter | Delivers concept(s) | Delivers artifact(s) [type] | Verdict |
|---|---|---|---|
| 0.1-preface | churn, thesis-modeling, thesis-alignment, universal-language | book-map fig; one-move epigraph [pattern] | A (exempt) |
| 0.2-the-books-language | — | the front-of-book glossary itself [reference] | apx |
| 0.3-acknowledgments | — | — | apx |
| 1.1-the-printer | printer-metaphor, picture-vs-model, whose-fault | llm-as-function-call fig [pattern] | C→A (metaphor is the payload) |
| 1.2-mage-by-example | — | docable-pipeline fig; the running example [worked-example] | A (exempt overview) |
| 1.3-loops-and-models | loop-engineering, engineered-agent-loop, success-metric, search-space | loop-engineering fig (4 levers) [framework] | A |
| 1.4-why-mage-follows | engineering-substrate | substrate-derivation: 8-property/7-consequence table [framework] | A |
| 1.5-the-engineers-seat | engineers-seat, selc, lifecycle-phases | oversight-modes fig (one-shot vs supervised) [decision-tree]; sdlc-to-selc | A |
| 2.1-the-agent-stack | agent-stack (+13: skill/hook/tool, injection-point, …) | agent-stack-layers fig (4-layer injection model) [framework] | A |
| 2.2-models-and-semantic-gap | semantic-gap, model-as-map, right-level-of-enforcement, … | documentation-hierarchy + semantic-gap-levels figs; context-bank-hook [worked-example] | A |
| 2.3-the-governed-environment | governance-mechanism, constraint, sensor, governance-package, residual, … | constraint-vs-sensor fig; "four classes" [framework]; control-substrate table [evidence] | A |
| **2.4-lifecycles-and-runbooks** | lifecycle, FMEA, runbook, det-vs-judgment-split, rubric, pre-canned-brief | config-optimization-runbook fig only | **P (#1)** |
| 2.5-metrics | measure-one-level-deeper | "governance metrics at a glance" table (metric→decision→axis) [decision-rule]; metric-spectrum fig | A |
| 2.6-when-guardrails-collide | (gloss) governance-graph | collision-edge fig; 4-value collision taxonomy in prose [framework, latent] | A (P secondary) |
| 3.1-the-executable-zoo | executable-source-of-truth, four-plus-one-views, drift-gate, … (12) | 4+1 framework; per-model template [pattern]; token-cost table [evidence] | A |
| 3.2-the-logical-view | logical-view, data-flow-diagram | data-flow figs + structure table [framework/worked-example] | A |
| 3.3-the-process-view | process-view, state-machine, safety/liveness, bounded-model-checking, … (10) | process fig + verification-tier table [framework] | A |
| 3.4-the-development-view | development-view, bill-of-materials, component-zone-model, … | component-model fig + BoM table [framework] | A |
| 3.5-the-physical-view | physical-view, deployment-topology, invariant-dag-policy, … (6) | deployment + dag-policy figs + 2 tables [framework] | A |
| 3.6-the-scenarios-view | scenarios-view, user-journey-model, node-coverage, … (9) | journey fig + coverage-mapping table [framework] | A |
| 3.7-the-scope-of-modeling | scope-of-modeling, digital-twin | — (short synthesis prose) | C (exempt synthesis) |
| 3.8-keeping-models-in-sync | — | two-layer-net fig; 2 evidence tables; two-failure-modes [framework]; "derived defends, snapshotted drifts" [commandment] | A |
| **4.1-brownfield** | brownfield-migration, lint-cover-induce, fitness-function, make-lint-blocking, … | squash-zero-promote fig; three-approaches + cost×freq rule in prose [decision-rule, latent] | **P (#2)** |
| 4.2-the-skills | self-operate, self-governance, self-communicate, lexicon, teetering-tower | three-skills + recipe figs; 3 by-construction-layer tables [framework] | A |
| 4.3-transformations | transformation, sizing-the-leap, compounding-failure-probability | transformations-pipeline fig | C (P-mild: sizing litmus latent) |
| 4.4-training-data | novelty-axis, reference-class, diffusion-analogy, demoable-vs-productizable, … | novelty-axis fig (3-knob decision aid) [decision-tree] | A |
| 4.5-lessons-learned | 14 maxims (optionality-is-poison, refactoring-is-free, done-is-a-claim, …) | "lessons as quotable lines + the move each demands" table [commandment/anti-pattern set] | A (exempt discussion) |
| 4.6-generative-validation | generative-validation, property-test-models-output, producer-dialect-corpus | example-vs-generative + generative-loop figs; "When to reach for which" [decision-rule] | A |
| 5.1-the-ada-context | — | context table [worked-example] | A (case study) |
| 5.2-timeline-and-work | — | phased-timeline, velocity, churn-per-path figs; 2 tables [worked-example/evidence] | A |
| 5.3-built-system | — | frontend-mvc, dsl-remediation, services-reactive figs [worked-example] | A |
| 5.4-road-to-mage | — | mage-staircase fig [worked-example/pattern] | A |
| 6.0-implications-for-se | — | 2 tables + fig [framework] | A (exempt discussion) |
| 6.1-conclusion | judgment-is-scarce, governance-as-design-patterns | — | C (exempt conclusion) |

(Pure apparatus set aside: 6.2-glossary, 6.3-about-author, 6.4-colophon.)

### Coverage summary

| Verdict | Count | Chapters |
|---|---|---|
| **A** — has-artifact | **26** | most of Parts 1–5 + 6.0 |
| **C** — concept-only-OK | **4** | 1.1, 3.7, 4.3, 6.1 |
| **P** — all-prose-would-benefit | **2** | 2.4, 4.1 (secondary: 2.6, 4.3) |
| **N** — GAP-neither | **0** | — |
| apparatus (N/A) | 2 in-set (0.2, 0.3) + 3 back | — |

**0 chapters deliver neither.** Every non-apparatus chapter is a concept's canonical site, an
artifact-bearer, or both. This is the headline finding and it directly answers the pilot's primary
worry: the "chapter that doesn't earn its place" does not exist in this book.

---

## 3. The gap list (conservative, ranked)

Per the author's framing, concept-only is fine, so this list holds only *all-prose-where-an-artifact-
would-clearly-help* — and it is short.

1. **2.4-lifecycles-and-runbooks — STRONGEST.** The most purely operational chapter in the book, and
   it delivers its operational forms *as prose descriptions of artifacts it never shows*. It says to
   build "a grid: every node crossed with every symptom, and in each cell, what to do" — and shows no
   grid. It names the **rubric** as the way to operationalize a measurement-judgment — and gives no
   rubric. It names the **runbook split** (deterministic → tool, judgment → roughest algorithm) — and
   leaves it as prose. A reader cannot lift a template from it. Highest value, lowest risk (the chapter
   is *about* these artifact forms, so an artifact is on-genre, not bolted on).

2. **4.1-brownfield — MODERATE.** "How much governance is enough" answers with an explicit multiply
   rule — *failure cost × frequency → mechanism hardness* — stated in a paragraph. That is a
   decision-matrix hiding in prose. The three migration approaches (top-down / bottom-up / lint-cover-
   induce) also read as a decision the reader must make with no decision-aid drawn. Delivers plenty of
   concepts, so not a gap — but a 2×2 and a one-line litmus would convert judgment into something the
   reader applies.

**Secondary / watch (do not force):**
- **2.6-when-guardrails-collide** — the 4-value collision taxonomy and the "before you ship a control,
  ask…" payoff are latent review-questions; it already has a strong concept + figure, so this is a
  *nice-to-have*, not a gap.
- **4.3-transformations** — "size the leap" invites a litmus, but the pipeline figure already carries
  the load; leave concept-only unless the author wants the litmus.

---

## 4. Depth — two drafted gap-fills (real content from the chapters)

### 4.1 — Draft for 2.4 (artifact types: **checklist** + **framework/table**)

**(a) The FMEA failure-grid the chapter describes but doesn't show — a `framework` table.**
Drawn from the chapter's own examples (merge conflict, full disk):

| Lifecycle node | Failure mode | Way out (sanctioned) | Prohibited (the pink elephant) | Encode at |
|---|---|---|---|---|
| Merge two branches | Branches conflict | Read both sides, recover each side's intent, reconcile | Reset the branch (silently drops applied work) | agent hook + named escape |
| Disk check | Disk fills | Find the fat point (the cache), wipe it | `rm -rf /` or wiping non-cache state | git/agent hook |
| Deploy | Gate fails mid-run | Read the gate output, fix the flagged cause, re-run | Bypass the gate to "make it green" | blocking gate |

**(b) The runbook-authoring `checklist` — the split the chapter argues, made liftable:**

- [ ] Written the **healthy path** for this activity, node by node?
- [ ] From each node, mapped the **failure modes** and, for each, the **way out** (not just the block)?
- [ ] Split every step into **deterministic** vs **judgment**?
- [ ] Deterministic steps → an **executable tool**, not a prose procedure the agent improvises?
- [ ] Determinized steps → do they **log a trace** (for the next loop turn AND a second checker)?
- [ ] Judgment steps → the **roughest algorithm that still fits** (heuristics if open-ended, an
      algorithm if well-constrained — never over-constrained)?
- [ ] Measurement-judgments → given a **rubric** (the dimensions to score), not a verdict demand?
- [ ] Delegated work → a **pre-canned brief template** with a linter that checks it before launch?
- [ ] Every prohibition **paired with its sanctioned escape** ("not that lever, this one")?

Effort to add: ~1 table + 1 checklist, both grounded in text already present. No new claims.

### 4.2 — Draft for 4.1 (artifact type: **decision-tree** / decision-matrix + **litmus-test**)

**The governance-sizing matrix — the cost×frequency rule made a 2×2:**

| | **Rare failure** | **Frequent failure** |
|---|---|---|
| **Cheap** | Leave to judgment. A mechanism here is the first brick in the teetering tower. | Cheap script or lint — it stumbles agents often; token cost is real cost. |
| **Costly** | Runbook + named escape; a lint if the shape is decidable. | **Hard mechanism** — blocking gate, or a typed model that makes the mistake impossible. |

**And the one-line litmus (when to STOP adding governance):**
> *Would this control guard a failure that is both rare and cheap? Then don't build it — its upkeep
> costs more attention than the failure ever will.*

Effort to add: 1 small table + 1 pull-quote, both verbatim-faithful to the existing paragraph.

---

## 5. Pilot verdict, cost, and risk

### Honest read: **GO — but scope it as a coverage lens + latent-artifact finder, not a gap alarm.**

The hypothesis had two hopes: (a) find chapters that earn no place, and (b) find all-prose chapters an
artifact would sharpen. On this book, **(a) yields zero** and **(b) yields two solid finds plus two
watch-items.** So the field's value is NOT the `delivers_neither` alarm (it will read 0 for the
foreseeable life of the book) — it is:

1. **A durable coverage map** — the one place that answers "what does each chapter hand the reader?"
   in a queryable form, which is genuinely missing today (you had to reconstruct it by hand, as this
   pilot did).
2. **A latent-artifact finder** — the `all_prose_would_benefit` author-flag surfaces the 2–4 chapters
   where an operational form is *described* but not *shown*. That is a real, actionable editorial
   worklist (§4 is it, drafted).
3. **A regression guard** — once an artifact is added (say the 2.4 checklist), the anchor freshness
   check (DV3) keeps the model honest that it still exists.

### How many real gaps? **0 deliver-neither; 2 all-prose (2.4, 4.1); ~2 watch (2.6, 4.3).**
The book is denser than expected. This is itself a publishable finding for the author: the
concept-OR-artifact discipline is *already met*, largely unconsciously, because the book leans on
figures, tables, and typed frameworks throughout.

### Rough effort
- **(a) Model field + view:** ~half a day. Extend `chapter_shape_declared.json` (34 records get a
  `delivers` block — concepts are a mechanical join from `index-def`, so only `artifacts` is authored),
  add the derive + DV1–DV4 to `chapter_shape_model.py`, add `cmd_delivers` + fold findings into
  `views-audit`. All patterns already exist in the sibling models — this is copy-the-shape work.
- **(b) Fill the 2 real gaps:** ~1–2 hours. Both drafts in §4 are ready; they need figure/table
  rendering into the chapter's marker vocabulary (`<!-- table: … -->` / a checklist block) and an
  anchor label. No new research, no new claims.

### The risk, and how the framing mitigates it
The named risk is **formulaic filler** — a `delivers.artifacts` field pressures every chapter toward a
box-ticking decision-tree, and the book's voice (Hemingway, "say it once", "describe don't sell") would
rot into listicle. **The concept-OR-artifact framing is the mitigation, and it must be load-bearing in
the model, not just the intent:**
- `concepts` non-empty **satisfies** `delivers` alone. A conceptual chapter (1.1's printer metaphor,
  6.1's conclusion) is green with zero artifacts. The model must never flag a concept-only chapter.
- `all_prose_would_benefit` is an **authored judgment flag**, never derived from "artifacts is empty."
  The model reports the author's call; it does not manufacture a gap from absence. This is the single
  most important design constraint — invert it (auto-flag empty-artifacts) and you rebuild the filler
  pressure the framing exists to prevent.
- Keep `ARTIFACT_TYPES` a **closed set**, and recognize **worked-example / evidence-table / framework**
  as first-class types (§below) — otherwise Part 5 and the model-zoo chapters look artifact-poor when
  they are the opposite, and the pressure to bolt a decision-tree onto a case study returns.

### Recommended vocabulary additions (answer to the author's candidate question)
- **ADD `framework` (a.k.a. table):** the model-zoo (3.x), the agent-stack, the four-classes,
  the by-construction-layer tables are the book's most common artifact. Without this type the densest
  chapters mis-read as gaps. **Strongly recommend.**
- **ADD `worked-example`:** all of Part 5 and the 2.2 bank-hook deliver via a traced real case, not a
  concept and not a decision-tree. Without it the entire case study looks like a gap. **Strongly
  recommend.**
- **ADD `evidence-table` (or fold into framework):** the measurement chapters (3.8, 2.3 substrate,
  3.1 token-cost) deliver data. Optional; can fold under framework if you want a tighter set.
- Keep the original 8; they map cleanly (commandment ← 4.5 maxims + "derived defends" lines;
  decision-rule ← 2.5/4.6; decision-tree ← 1.5/4.4; the latent checklist/litmus/review-question types
  are exactly the §4 fills).

**Net: go, small, and wire the concept-OR-artifact asymmetry into the model itself — the field pays for
itself as a coverage map and a 2-item editorial worklist, and the framing keeps it from breeding
filler.**
