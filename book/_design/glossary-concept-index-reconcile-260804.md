# Glossary ⇄ concept-index reconciliation (260804)

**Scope:** READ-ONLY analysis. No prose or data edited. Reconciles the front glossary
(`frontmatter/0.2-the-books-language.md`, 24 entries) against the concept-index registry
(`index-terms.md` + the 145 `<!-- index-def: -->` markers across the chapter prose + their
`terms:`/`section-terms:` reference tags). Author's model: the front glossary should BE the curated
concept-index — the terms that are planted as concepts and expanded at a canonical site, with every
"good" (core, reused-across-the-book) concept present and incidental one-site terms absent.

## Headline numbers

| Measure | Count |
|---|---|
| `index-def` concepts (canonical expansion sites, chapter prose) | **145** |
| Front-glossary entries | **24** |
| Glossary entries backed by a matching `index-def` anchor | **15** (16 counting Pattern's loose match) |
| Glossary entries with NO `index-def` site (gloss / figure / gap) | **9** |
| ADD list — good concepts missing from the glossary (primary) | **8** |
| ADD list — secondary "consider" candidates | **5** |
| DEMOTE flags (clear one-site outliers) | **1** (Trust Half) |
| Take-for-granted-5 present in glossary | **5 / 5** ✓ |

The reuse signal below counts **distinct Parts** that reference a concept via `terms:`/`section-terms:`
tags (the "reused-across-the-book" measure), and total tag occurrences as a tiebreak.

---

## 1. Concept-index inventory (the 145, by reuse)

Full per-slug table with canonical site, Part-reuse count, and glossary membership. Sorted by
Parts-referencing (the reuse signal), then occurrences. **G** = currently in front glossary.

### Multi-Part concepts (reused across ≥3 Parts) — the "good ones" by reuse

| Slug | Canonical site (Part) | #Parts | #refs | In glossary? |
|---|---|---:|---:|:--:|
| thesis-modeling | frontmatter/0.1-preface | 5 | 28 | **G** |
| model-drift | part3/3.1-executable-zoo | 4 | 25 | — ADD |
| context-window | part2/2.1-agent-stack | 4 | 21 | **G** |
| governance-conversion | part2/2.3-governed-env | 4 | 18 | **G** |
| thesis-alignment | frontmatter/0.1-preface | 4 | 16 | **G** |
| model-zoo | part3/3.1-executable-zoo | 4 | 14 | **G** |
| invariant | part3/3.1-executable-zoo | 4 | 7 | — ADD |
| judgment-is-the-scarce-resource | backmatter/6.1-conclusion | 4 | 6 | — consider |
| drift-gate | part3/3.1-executable-zoo | 3 | 29 | **G** |
| executable-source-of-truth | part3/3.1-executable-zoo | 3 | 23 | **G** |
| traceability | part3/3.1-executable-zoo | 3 | 18 | — ADD |
| model | part2/2.1-agent-stack | 3 | 16 | — ADD |
| sensor | part2/2.3-governed-env | 3 | 15 | **G** |
| coverage-model-mapping | part3/3.6-scenarios-view | 3 | 14 | — hold (Part-3) |
| constraints-and-sensors | part2/2.3-governed-env | 3 | 13 | — (both members G) |
| hook-hard-control | part2/2.1-agent-stack | 3 | 13 | — ADD |
| model-as-map | part2/2.2-semantic-gap | 3 | 13 | — ADD (fold w/ map-and-territory) |
| component-zone-model | part3/3.4-development-view | 3 | 12 | — hold (Part-3) |
| foundation-model | part2/2.1-agent-stack | 3 | 11 | — ADD |
| map-and-territory | part2/2.2-semantic-gap | 3 | 11 | — ADD (fold w/ model-as-map) |
| velocity-exposes-the-danger | part4/4.5-lessons | 3 | 10 | — consider |
| conditioning-the-search | part4/4.4-training-data | 3 | 8 | — hold |
| deployment-topology-model | part3/3.5-physical-view | 3 | 8 | — hold (Part-3) |
| loop-engineering | part1/1.3-loops-and-models | 3 | 8 | — ADD |
| sizing-the-leap | part4/4.3-transformations | 3 | 8 | — hold |
| governed-environment | part2/2.3-governed-env | 3 | 7 | **G** |
| lifecycle | part2/2.4-lifecycles | 3 | 7 | — consider |
| training-data-bias | part4/4.4-training-data | 3 | 7 | — hold |
| agent-orchestration-model | part3/3.6-scenarios-view | 3 | 5 | — hold (Part-3) |

### Two-Part concepts (selected — reuse ≥ moderate)

`four-plus-one-views` (14), `right-level-of-enforcement` (14), `semantic-gap` (14), `model-from-code`
(13), `soft-vs-hard-governance` (13), `measure-one-level-deeper` (12), **`constraint` (11, G)**,
`model-to-code` (11), `injection-point` (10), `agentic-harness` (9, consider), `transformation` (9),
`demoable-vs-productizable` (8), `residual` (8), `deterministic-vs-judgment-split` (7),
`per-model-template` (7), `teetering-tower` (7), `audits-into-lints` (6), `brownfield-migration` (6),
`runbook` (6), `vibe-coding-vs-engineering` (6), `ex-ante-governance` (5), `node-coverage` (5),
`refactoring-is-free` (5), **`skill-soft-control` (5, consider)**, `model-only-where-a-failure-lives`
(4), `search-space` (4), `compounding-failure-probability` (3), `engineering-environment` (3),
`rubric` (3), **`churn` (2, G)**, `tool-deterministic-action` (2, consider).

### One-Part concepts (~115) — the concept-index tail

Everything else is single-Part-dominant: the Part-3 model machinery (`logical-view`, `process-view`,
`physical-view`, `scenarios-view`, `state-machine`, `data-flow-diagram`, `safety-property`,
`liveness-property`, `bounded-model-checking`, `temporal-logic`, `mediator-registry`,
`single-writer-registry`, `rule-metadata-registry`, `bill-of-materials`, `performance-cost-model`,
`derive-and-join`, `derivation-direction`, `journey-*`, …), the Part-4 maxims
(`optionality-is-poison`, `done-is-a-claim`, `broken-cost-estimator`, `explicitness-is-essential`,
`governance-centric`, `autonomy-amplifier`, `three-ways-to-run-an-agent`, …), the Part-4 skills
(`self-operate`, `self-governance`, `self-communicate`, `governance-catalogue`, `lexicon`), and the
definitional singletons (`agent`, `engineering`, `software-engineering`, `governance-mechanism` (G),
`ex-post-governance`, `structured` (G), `lint` (G), `whose-fault`, `printer-metaphor` (G), …).
These are correctly concept-index-only: defined once, in situ, not front-glossary material.

Two `index-def` markers carry **zero** `terms:` references (`universal-language`,
`governance-as-design-patterns`) — they are defined but never tagged as used; not glossary candidates.

---

## 2. Reconcile — the three buckets

### 2a. IN glossary + earns it — CONFIRM (13 of 24)

All strongly reused; keep:

- **thesis-modeling** (5 Parts) · **context-window** (4) · **governance-conversion** (4) ·
  **thesis-alignment** (4) · **model-zoo** (4) · **drift-gate** (3, 29 refs) ·
  **executable-source-of-truth** (3) · **sensor** (3) · **governed-environment** (3) ·
  **constraint** (2, 11) · **structured** (1, but the foundational adjective the Modeling Thesis
  rests on) · **governance-mechanism** (1, but the definitional class term) · **printer-metaphor**
  (1, but the governing metaphor / take-for-granted-5).

Low-reuse-but-load-bearing keeps: **churn** (2 Parts / 2 refs), **printer-metaphor**,
**governance-mechanism**, **structured**, **lint** — each earns its place by role in the argument,
not by tag count. Do NOT demote these.

Glossary entries with no `index-def` slug but justified as vocabulary: **Fleet**, **Gate**, **Lint**
(gloss + index-def), **One-shot Scripting** / **Supervised Autonomy** (the named task-mode dichotomy;
figure site), **Validator** (a real structural gap — see §3), **Pattern**, **Fidelity Validator**,
**Provenance Layer**. Keep, but see §3 for their wiring problem.

### 2b. NOT in glossary but SHOULD BE — the ADD list (the author's main ask)

**Primary (8) — high reuse, conspicuous gaps given what is already in:**

| Concept | Group | #Parts/refs | Canonical site (anchor) | Proposed one-line entry |
|---|---|---|---|---|
| **Model drift** (`model-drift`) | The GEE | 4 / 25 | part3/3.1 `#idx-def-model-drift` | The divergence a drift gate exists to catch: when a model and the code it describes stop agreeing. (Drift Gate is glossed; the thing it catches is not.) |
| **Model** (`model`) | Core ideas | 3 / 16 | part2/2.1 `#idx-def-model` | A cheaper, structured approximation of a system that an agent can reason through and an engineer can specify on — the base term the Modeling Thesis turns on. |
| **Traceability** (`traceability`) | The GEE | 3 / 18 | part3/3.1 `#idx-def-traceability` | The round-trip join between a model and the code it governs, so every model node maps to the code it constrains and back. |
| **Map and territory** (`map-and-territory` / `model-as-map`) | Core ideas | 3 / 11–13 | part2/2.2 `#idx-def-map-and-territory` | A model is a map, not the territory: useful precisely because it drops detail, and never a substitute for the running system. |
| **Foundation model** (`foundation-model`) | How coding agents work | 3 / 11 | part2/2.1 `#idx-def-foundation-model` | The bottom layer of the agent stack — the trained model whose choice fixes the context window and the reasoning ceiling. |
| **Loop engineering** (`loop-engineering`) | How coding agents work | 3 / 8 | part1/1.3 `#idx-def-loop-engineering` | Shaping the agent's generate-check-correct loop — the correctness conditions, tools, and monitoring — rather than steering a single pass. |
| **Hook** (`hook-hard-control`) | The GEE | 3 / 13 | part2/2.1 `#idx-def-hook-hard-control` | A hard mechanism the harness fires deterministically at an injection point — the enforcement primitive under lints and gates. |
| **Invariant** (`invariant`) | The GEE | 4 / 7 | part3/3.1 `#idx-def-invariant` | A predicate over a model that must always hold — the testable claim a gate or a model-checker enforces. |

**Secondary (5) — "consider," author's call; each is a real concept but risks glossary bloat or is a near-sibling of an existing entry:**

- **Agentic harness** (`agentic-harness`, 2 Parts / 9) — completes the agent stack with foundation-model
  and skill/hook/tool; add if the "How coding agents work" group is meant to name the whole stack.
- **Skill (soft) + Tool (deterministic)** (`skill-soft-control` 5, `tool-deterministic-action` 2) — the
  soft and deterministic siblings of Hook. If Hook is added, symmetry argues for the whole
  skill/hook/tool trio; reuse of the other two is thinner.
- **Judgment is the scarce resource** (`judgment-is-the-scarce-resource`, 4 Parts / 6) — a
  load-bearing thesis-grade maxim (backmatter climax); fits "Core ideas" if the author wants the
  book's governing maxims glossed, but it reads as a claim more than a term.
- **Lifecycle** (`lifecycle`, 3 Parts / 7) — the SOP/runbook substrate term; moderate reuse.
- **Velocity exposes the danger** (`velocity-exposes-the-danger`, 3 Parts / 10) — Part-4 maxim tying
  churn to velocity; thematic, not strictly a defined term.

**Explicitly NOT ADD (hold as concept-index-only):** the Part-3 model machinery
(`component-zone-model`, `deployment-topology-model`, `coverage-model-mapping`,
`agent-orchestration-model`, the four view slugs, the property/checking slugs) and the Part-4 maxims
(`sizing-the-leap`, `conditioning-the-search`, `training-data-bias`, `optionality-is-poison`, …).
These are reused *within one Part* or are in-situ maxims — the curated `book-index.html` is their
correct home, not the front glossary.

### 2c. In glossary but marginal — DEMOTE flag (be conservative)

- **Trust Half** — the one clear one-site outlier. The prior terminology inventory
  (`terminology-inventory-260804.md` §10) found it appears **exactly twice, both in
  part1/1.2**, names one half of a single pipeline figure, and is never picked up again; it
  recommended NOT front-glossary-ing it "unless the author intends broader use." No `index-def`, no
  cross-Part reuse. **Flag for DEMOTE to concept-index-only** (or drop), unless the author plans to
  lean on the working-half/trust-half framing more widely.

Everything else in the glossary either reuses across Parts or is load-bearing to the argument at a
single canonical site (Printer, Churn, Governance Mechanism, Structured, Lint) — keep. **One-shot
Scripting** has low cross-Part reuse but is half of a named dichotomy with Supervised Autonomy;
keep the pair intact.

---

## 3. Pointer wiring — glossary → canonical `index-def` site

**Anchor format (from the build):** each `<!-- index-def: <slug> -->` attaches a stable
`id="idx-def-<slug>"` to the block that follows it, on the page `<chapter-slug>.html`. So the
navigable link for a glossed term is `<chapter-slug>.html#idx-def-<slug>`.

**Is it auto-derivable or manual? — Auto-derivable in principle; manual today.**

- The front glossary (`0.2-the-books-language.md`) is **fully hand-authored prose** — bold `**Term.**`
  entries, no directive, no links. It does **not** currently link any entry to its `index-def` anchor.
- The build already computes the exact mapping: `_harvest_concept_tags()` builds a registry
  `{slug: {"def": (page, "idx-def-<slug>"), …}}` and emits a separate autogenerated **concept-index
  page** (`book-index.html`) with those deep links. The data a glossary→site link needs already exists.
- So two paths for the refinement wave:
  1. **Manual per-entry links** — add `[canonical site →](<chapter>.html#idx-def-<slug>)` to each
     glossary entry by hand. Simple, immediate, but drifts if a concept's site moves.
  2. **A build feature (preferred, drift-proof)** — key the front glossary entries by slug (a
     directive analogous to the existing `glossary-auto`, or a `<!-- gloss-site: <slug> -->` per
     entry) and let the build inject the `#idx-def-<slug>` link from the harvested registry. This
     reuses the single source of truth and cannot go stale, matching the repo's
     stable-lint-reads-the-model discipline.

**Per-entry wiring status (which entries even HAVE an anchor to point to):**

- **15 wire cleanly** to `#idx-def-<slug>`: Modeling Thesis, Alignment Thesis, Governance Conversion,
  The Printer (`printer-metaphor`), Churn, Context Window, Governed Engineering Environment
  (`governed-environment`), Governance Mechanism, Constraint, Sensor, Lint, Drift Gate, Structured,
  Executable source-of-truth, The Model Zoo (`model-zoo`).
- **9 have NO `index-def` anchor** and cannot be auto-wired as-is:
  - **Fleet, Gate** — only a `<!-- gloss: -->` marker (could link to the gloss sidenote anchor, or
    promote to a registered concept + `index-def`).
  - **One-shot Scripting, Supervised Autonomy** — registered as *terms* (section-tier), canonical
    site is the part1/1.1 figure; no `index-def`. Would need an `index-def` tag at the figure prose.
  - **Validator** — the genuine structural gap flagged in the terminology inventory: used constantly,
    never given a canonical definition site, not in the concept registry. Needs a registered concept +
    an `index-def` (natural home: part2/2.3, tied to the evidence/admission classes).
  - **Pattern** — loose match to `governance-as-design-patterns` (backmatter/6.1); could point there,
    or register a `pattern` concept at the preface GoF discussion.
  - **Fidelity Validator, Provenance Layer, Trust Half** — DocAble specifics, canonical site
    part1/1.2 (prose + `docable-pipeline.svg` caption); none tagged `index-def` and none in the
    concept registry. Would each need registering + an `index-def` at 1.2.

So making the glossary a true navigational concept-index requires, alongside the wiring, **registering
~7 concepts** (Validator, Fleet, Gate, Pattern, One-shot Scripting/Supervised Autonomy if promoted
from term to concept, and the three DocAble terms) and adding their `index-def` markers — otherwise
those 9 entries stay dead-ends.

---

## 4. Take-for-granted-5 — CONFIRMED 5/5

All five are in the glossary:

| Concept | Glossary group | Slug / status |
|---|---|---|
| Modeling Thesis | Core ideas | `thesis-modeling` ✓ |
| Alignment Thesis | Core ideas | `thesis-alignment` ✓ |
| The Printer | Core ideas | `printer-metaphor` ✓ |
| Governance Conversion | Core ideas | `governance-conversion` ✓ |
| Churn | How coding agents work | `churn` ✓ |

Note: four of the five sit in "Core ideas"; **Churn** sits in "How coding agents work (and fail)" —
present and correct, just grouped by topic rather than under the core-ideas banner. No action needed.

---

## Biggest judgment call

**Whether to add the agent-stack cluster whole or piecemeal.** The "How coding agents work (and
fail)" group names Fleet, Context Window, and the two task modes, but omits the actual stack it rests
on — `foundation-model`, `agentic-harness`, and the `skill`/`hook`/`tool` mechanism trio. Hook alone
clears the reuse bar cleanly (3 Parts, 13 refs); foundation-model does too (3/11); the others are
thinner (skill 5, tool 2, harness 9-but-2-Part). Adding only the high-reuse ones (Hook, Foundation
model) is defensible by the numbers but leaves the stack half-named in the glossary; adding the whole
stack is more coherent but pulls in two low-reuse siblings and grows the group from 5 to ~9. This is
the one place where "reused across ≥2-3 Parts" and "coherent named set" pull in different directions —
recommend the author rule on stack-whole vs. stack-by-reuse before the ADD list is finalized.
