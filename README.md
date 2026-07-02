# Governance Catalog — a pattern language of agentic-engineering controls

*A catalog of the **controls** used to keep a fleet of autonomous coding agents productive while
holding the cost of their failures within bounds. Each entry is written like a design pattern: it
names a recurring failure, the control that kills it, and — most importantly — why the control is
**not** just the cheaper thing everyone already does. The controls here are real artifacts from a
sustained agentic-engineering effort; identities are kept out so the writeups are forwardable.*

This catalogue covers **three roles** a control can play, authored the same way, each a top-level
folder with its own README:

- **[`agent/`](agent/)** — govern the *fleet and the substrate that produces work* (briefs, dispatch,
  gates, mediators, lifecycle, governance docs).
- **[`models-bridge/`](models-bridge/)** — the **MBSE bridge**: typed models of the system that agents
  read and the codebase is generated/governed from. *This is the interface through which a
  context-bounded agent operates a context-exceeding codebase* — the thing that lets agentic
  engineering scale past a toy.
- **[`product/`](product/)** — govern the *shipped artifact* (its models, validators, tests,
  provenance, repair vocabulary).

The [INDEX](INDEX.md) is a single census across all three.

---

## What a "control" is here

A **control** is a *discrete, named artifact that fires on a violation*: a lint, a quality gate, a
validator, a regression/property/fuzz test, an audit agent, a conformance check, an observability
assertion. Controls are enumerable precisely because each is a concrete check with a pass/fail
outcome. The organizing move behind every one of them is the same:

> **Convert a recurring failure into a control rather than re-inspect for it.** A failure caught
> once becomes a mechanism enforced on every subsequent agent, without re-inspection.

**What this catalog deliberately does *not* enumerate: architecture.** A control *detects* a failure
after an agent acts; *architecture* (typed models, single sanctioned seams, explicit state machines)
eliminates a failure class **by construction** — making it unrepresentable, with no discrete check to
count. The two are a spectrum, not a partition: a typed seam is usually *held in place* by a ban-lint,
and it is the lint we catalog. Architecture is shown only **by example**, never counted. Everything in
this catalog is a detection-mode control.
>
> This is exactly how the product half's **Canonical models & seams** family is handled: the typed
> document model or sole seam is the *construction* mechanism (shown by example), and the entry's
> counted, enforced control is the **ban-lint that holds it in place** (`itext-direct-access`,
> `openxml-direct-access`, …). The entry documents both; the Enforcement row is the lint.

> **Scope — representative, not a census.** An entry documents one control *pattern*, which is often a
> whole **family of concrete artifacts** collapsed into a single writeup (`doc-hygiene-lints` stands
> for index-coverage + autogen-provenance + cross-reference lints; `mediators` for the test/build/
> lint-all serializers). The catalog is a curated **~21-control taxonomy** — a flagship plus a few
> instances per family — deliberately *not* an enumeration of the 500+ individual custom lints. The
> lint count is a **magnitude reported in prose** (see the paper's magnitudes), never a to-do list of
> entries. A new entry earns its place by naming a *distinct pattern*, not a distinct lint; if two
> candidate controls share the same "why it's not just X," they are one entry with two examples.

## The three roles

Two targets a control can *govern* — the agent fleet, or the shipped product — and, between them, the
**bridge** that couples the two:

| Role | Governs / connects | Folder |
|---|---|---|
| **Agent** | The agent fleet and its work-producing substrate — briefs, dispatch, isolation, commit gates, host-compute mediation, fleet lifecycle, governance docs. | [`agent/`](agent/) |
| **Models-bridge** | *Neither, and both.* Typed models of the system: agents **read** them to reason about the codebase; the codebase is **generated & governed** from them. The interface through which a bounded agent operates an unbounded codebase. | [`models-bridge/`](models-bridge/) |
| **Product** | The shipped artifact — its models, validators, regression tests, provenance, repair vocabulary. | [`product/`](product/) |

## The agent-control families at a glance

Five families, roughly following the path an agent's work travels from brief to production:

1. **[Context & dispatch substrate](agent/context-and-dispatch/)** — what an agent *knows* and how it is
   *launched*: brief-linting, the rule index, dynamic file-scoped context injection, role-typed
   dispatch, queryable repo meta-models.
2. **[Gates & merge-train](agent/gates-and-merge-train/)** — the path-to-production staircase: the
   pre-commit hook, the sentinel first-commit abort, merge-train MIS batching, staged deploy gates.
3. **[Mediators & resource locks](agent/mediators-and-resource-locks/)** — host-level wrappers that ration
   shared compute across concurrent worktrees, each with an enforcer that refuses the raw call.
4. **[Lifecycle & observability](agent/lifecycle-and-observability/)** — live signal surfaces over the
   fleet: the agent-registry, the typed event bus, deploy heartbeats, tombstone records, the
   cron-alerts gate.
5. **[Governance-doc controls](agent/governance-doc-controls/)** — documentation treated as enforced
   infrastructure: the rule index and its cap/conformance lints, the mandatory snippet table, the
   Epic Definition-of-Done.

## The product-control families at a glance

Five families governing the *shipped artifact* — roughly, how it is modelled, validated, pinned,
attributed, and bounded:

1. **[Canonical models & seams](product/canonical-models-and-seams/)** — the one sanctioned typed model or
   seam per concern (document models, walkers, the cross-service client, the sole raw-Redis seam), each
   held in place by a ban-lint on the raw alternative.
2. **[Validation & conformance](product/validation-and-conformance/)** — deterministic pass/fail checks over
   the artifact: content-fidelity validation, semantic lints, the standards/WCAG rule engine,
   cross-source coherence.
3. **[Regression tests](product/regression-tests/)** — repeatable behaviour-pinning: the test-onion tiers,
   FsCheck property tests, fuzz campaigns, doc-derived-test pin-trailers.
4. **[Provenance & attribution](product/provenance-and-attribution/)** — durable records of what the tool
   changed: per-mutator stamps, the F10 wiring lint, changelog derivation, the `a11y_` prefix.
5. **[Repair vocabulary](product/repair-vocabulary/)** — the bounded move-space of the remediator: closed
   remediation-verb sets, typed violation/failure categories, the codemod-first threshold.

## The models-bridge — the MBSE substrate

One family, `system-models`, of eleven controls: the typed models the fleet reasons *through* and the
codebase is generated *from*. Six **models** —
[component & zone](models-bridge/system-models/component-zone-model.md) ·
[synchronization (meta-sync)](models-bridge/system-models/synchronization-model.md) ·
[mediator & single-writer contracts](models-bridge/system-models/concurrency-contracts.md) ·
[service-flow / API](models-bridge/system-models/service-flow-model.md) ·
[deployment & tier topology](models-bridge/system-models/deployment-topology-model.md) ·
[domain registries](models-bridge/system-models/domain-registries.md) — and five **mechanisms** over
them: [executable source-of-truth](models-bridge/system-models/executable-source-of-truth.md) ★ ·
[drift & parity gates](models-bridge/system-models/drift-parity-gates.md) ·
[model-driven codegen](models-bridge/system-models/model-driven-codegen.md) ·
[query surface](models-bridge/system-models/query-surface.md) ·
[read-don't-hardcode consumption](models-bridge/system-models/meta-model-consumption.md). Full analysis
— why executable models can't drift, and why agents finally make MBSE practical — in
[`models-bridge/README.md`](models-bridge/).

See **[INDEX.md](INDEX.md)** for the full census across all three roles (every control, its family,
form, novelty, and enforcement).

## The catalogue as a map

Two views. First, a family-level schematic of the agent and product targets and the path an agent's
work travels; then the **bridge** view — the model layer between them. Edges use the five
relationships (see *Relationships between controls*). For the full colour-coded version see the figure
page `catalogue-figure.html` (four layout options).

```
┌─ ENGINEERING ENVIRONMENT — the governed substrate ────────────────────────┐
│                                                                            │
│  AGENT TARGET · governs the fleet + the substrate that produces work       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │ Context & dispatch    brief-lint · dyn-ctx-inject(S) · role · meta  │    │
│  │       snippet-table ──▶ brief-lint     meta-models ──▶ inject       │    │
│  │       │                                                             │    │
│  │       ▼  PATH-TO-PRODUCTION STAIRCASE   (layer · defense-in-depth)  │    │
│  │  Gates & merge-train   pre-commit ▸ sentinel ▸ merge-train ▸ deploy │    │
│  │  Mediators (host tier) test-ser ═ build-ser ═ lint-all-mutex        │    │
│  │  Lifecycle & obs.      agent-registry ──▶ merge-train · alerts-gate │    │
│  │  Governance-docs       CLAUDE.md (S·H) ═ cap-lint · DoD ═ index     │    │
│  └────────────────────────────────────────┬──────────────────────────┘    │
│                                  produces  ▼                               │
│  PRODUCT TARGET · governs the shipped artifact                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │ Canonical models   PdfModel ═ itext-ban · Office ═ openxml-ban      │    │
│  │ Validation & conf. ContentValidator · WCAG-engine ═ scope-doc       │    │
│  │ Regression tests   test-onion · property · fuzz · DDT               │    │
│  │ Provenance         mutator-stamps ═ F10-lint ◀── derive-changelog   │    │
│  │ Repair vocabulary  typed-enums · verbs ──▶ (enable stamps + valid.) │    │
│  └───────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
 ═══ counterpart (soft↔hard)   ──▶ enabler   ◀── consumer   ▸ / ▼ layer
 (S) soft · (S·H) soft core + hard counterpart · unmarked = hard
```

And the **bridge** view — the model layer between the fleet and the codebase, facing both ways:

```
     AGENT CONTROLS   ◀────  THE MODEL BRIDGE  ────▶   PRODUCT / CODEBASE
     (govern fleet)    read    (typed system-models)   govern & generate   (the artifact)

  brief-linting  ┐                 ┌ system-model catalog ┐               ┌ NetworkPolicy / wiring gen
  dyn-ctx-inject ┼── query/inject ─┤ meta-sync ══ drift   ├── parity/gen ─┼ deployment topology
  role-dispatch  ┘                 │ query-surface        │               └ boundary / seam lints
                                   └ codegen · read-no-copy ┘

   ── the bridge lets a context-BOUNDED agent operate a context-EXCEEDING codebase ──
      the model is the compressed, queryable, drift-checked truth the two sides share;
      meta-sync keeps the map equal to the territory — or the bridge would lie.
```

And the five relationships on their own, each with a canonical example:

```
COUNTERPART — a soft control + the hard control that keeps its substrate honest
   ┌ rule index (soft) — guidance the agent may act on ┐
   └─────────────────────── ═══ ───────────────────────┘
         cap + conformance lint (hard) — keeps the index small & valid

ENABLER — A must exist before B             CONSUMER — B reads A at runtime
   snippet-table    ──▶ brief-lint             dyn-ctx-inject   ◀── component registry
   file-addr rules  ──▶ dyn-ctx-inject         merge-train      ◀── agent-registry
   bounded verbs    ──▶ mutator-stamps         derive-changelog ◀── mutator-stamps

LAYER — the same fight fought again downstream (defense in depth)
   brief-lint ─▶ pre-commit ─▶ sentinel ─▶ merge-train ─▶ staged-deploy ─▶ runtime
    dispatch      commit         commit        cron          deploy         prod

BRIDGE — a model facing both ways: agents consume it; the codebase is governed by it
   dyn-ctx-inject ◀──[ component model ]──▶ boundary lints · NetworkPolicy gen
   repo-query     ◀──[ service-flow    ]──▶ service catalog · deploy wiring
                    ( meta-sync keeps the two faces equal )
```

---

## How to read an entry

Every control is written to the same template. It borrows the Gang-of-Four pattern shape
(Intent / Motivation / Structure / Consequences) and adds one section GoF does not have — the
load-bearing one for this domain:

| Section | What it answers | GoF analogue |
|---|---|---|
| **Intent** (one sentence) | What the control is, in a breath. | Intent |
| **Motivation — the failure it kills** | The *recurring failure class*, why it recurs, why it *compounds* at velocity/concurrency/scale. A control is defined by the failure it kills, not by its steps. | Motivation / Applicability |
| **Why it's not just *[the naive alternative]*** | The precise distinction from the cheaper thing people already do ("it's in the docs", "just add a test", "just review it"). | *(none — added)* |
| **Mechanism** | How it actually works; prefer a crisp structural claim over a step list. | Structure / Collaborations |
| **Prerequisites** | What must already be true or built for the control to work at all — its enabling substrate. The reader's real question is *"can I do this in my system?"* | Implementation |
| **Consequences & costs** | What the control *costs* — context tax, false positives/friction, false confidence, maintenance, and above all *what it does not catch*. No control is free; this section keeps the catalog honest to the paper's "costly judgment" thesis. | Consequences |
| **Known uses** | The real artifact(s) in the case study, with rule/tool names. | Known Uses |
| **Related controls** | Links to siblings it composes with. | Related Patterns |

### The metadata block

Every entry opens with a six-row metadata table — the control's card. Each row is a cross-cut you
can sort or filter the catalog on:

| Row | What it records | Defined in full |
|---|---|---|
| **Target** | The role the control plays — **Agent** (fleet/substrate) · **Bridge** (the system-model layer between) · **Product** (shipped artifact) — followed by its **Family**. Written `Agent · <Family>` / `Bridge · System models` / `Product · <Family>`. | *The three roles* + *The families at a glance* |
| **Form** | The *kind* of mechanism it is — one of nine. Orthogonal to family. | *The Form cross-cut* |
| **Novelty** | `novel` / `notable` / `standard` — how domain-invented it is. | *Novelty ratings* |
| **Real artifact** | The concrete tool/file(s) in the case study that implement it, named (not pathed — see *Reference policy*). | *(named inline)* |
| **Governing rule(s)** | The numbered `CLAUDE.md` rule(s) the control corresponds to — the authoritative governance text the control *is*. Dispatch *substrate* with no dedicated rule number says so and cites the checklist/section that invokes it. | *(below + Provenance)* |
| **Enforcement** | The **soft/hard** class + strength + bypass: `Hard` (deterministic — *blocking* / *audit-only* / *signal*), `Soft` (probabilistic — influences, cannot block), or `Soft·Hard` (soft guidance with a hard counterpart), plus the escape (`noqa` / `ADA_TOOL_*`, who may use it). | *Enforcement: soft vs hard* |

Three of these rows have their own reference section below (Form, Novelty, Enforcement); Target and
Family are defined at the top of this README; **Governing rule(s)** is the one that grounds each entry
in `CLAUDE.md` directly rather than paraphrasing around it.

> **Reference policy — the catalogue is self-contained.** The only *links* are intra-catalogue
> (to other entries and to this README/INDEX). External artifacts are referred to by **name, never by
> path** — `agent_prompt_lint.py`, not `tools/…/agent_prompt_lint.py` — and governing rules by
> **number** (`#29`), because repository paths rot, don't survive forwarding, and are implementation
> detail. `CLAUDE.md` is named (it is the subject of its own entry); no other external file is pathed.
> **One documented exception:** the [`models-bridge/`](models-bridge/) entries name the `system-models/`
> substrate and its model files (`components.py`, `synchronization.py`, `services/`, …) directly — that
> directory *is* their subject, the way `PdfModel` is a product entry's subject, not an incidental path.

**The load-bearing section is "Why it's not just *[the naive alternative]*."** Every good control is
confused with a cheaper thing. If that section can't be written, the control probably isn't a real
contribution — it's the obvious thing. The flagship worked example is
**[dynamic context injection](agent/context-and-dispatch/dynamic-context-injection.md)**, whose distinction
("docs make a rule *knowable*; the brief makes it *governing*") is the model for the rest.

> **Note on the ★ glyph — two uses.** In the [INDEX](INDEX.md), `★` marks each *family's* canonical
> example (one per family). Additionally, two entries carry an **in-body `★` note** as *catalogue-level*
> exemplars: [dynamic context injection](agent/context-and-dispatch/dynamic-context-injection.md) (the worked
> example of the "why not just X" move) and
> [the CLAUDE.md rule index](agent/governance-doc-controls/claude-md-rule-index.md) (the meta-control). The
> in-body ★ is reserved for those two; it is not the per-family marker.

## The Form cross-cut

Orthogonal to family, every control is one of nine **forms** — the *kind of mechanism* it is:

| Form | The mechanism is… |
|---|---|
| `typed-ir` | A typed in-process model naming a domain shape, so structure is compiler-checked. |
| `validation` | A reproducible pass/fail predicate over an artifact (or a consistency relation across artifacts). |
| `repair-vocab` | A closed, named set of allowed actions/categories replacing free-form strings. |
| `agent-output` | A contract on what a tool emits (PLAN/RESULT blocks, exit codes) so a downstream agent acts on it without parsing prose. |
| `bounded-service` | A single sanctioned, typed seam every cross-boundary interaction must pass through. |
| `regression` | A body of repeatable tests that pins behavior and re-runs. |
| `quality-gate` | A staged checkpoint that blocks promotion until cheaper checks pass. |
| `observability` | A live signal surface emitted while the system runs, consumed to detect drift or health. |
| `audit-trail` | An after-the-fact durable record that reconstructs a change's history. |

## Enforcement: soft vs hard (probabilistic vs deterministic)

Beyond *what kind* of mechanism a control is (its form), each control is classed on **how it bites** —
a two-value taxonomy that is the single most clarifying axis in the catalog:

- **Hard (deterministic).** The control's verdict is a *reproducible function of its input* — same
  input, same outcome, every time, **independent of whether an agent chooses to comply.** Lints,
  quality gates, validators, exit-code contracts, mutexes, audit records. A hard control can still vary
  in *strength* — **blocking** (fails the pipeline / refuses the action), **audit-only / warning**
  (records or surfaces but does not stop), or a **signal** (emits deterministic telemetry) — but what
  makes it *hard* is that the check itself is mechanical and does not depend on agent cooperation.
- **Soft (probabilistic).** The control shifts the *probability* of correct behavior **without
  mechanically guaranteeing it** — it works only if the agent conditions on the information it was
  given. Dynamic context injection, the rule index as guidance, salience. A soft control lowers a
  failure *rate*; it never makes a failure unrepresentable, and it cannot "block."

**The two compose — soft guidance with a hard counterpart.** Several controls *deliver* soft guidance
(a document, an injected constraint) yet are kept honest by a **hard counterpart** — a deterministic
lint that enforces a property of the soft control's *own substrate* (not of the agent). The rule index
is advice to the agent (soft), but its cap and cross-reference discipline are BLOCKING lints (hard).
Classify such a control by its primary mechanism and name the counterpart (`Soft·Hard`). This
soft↔hard pairing is the first of the four control *relationships* below.

**Where the fleet's weight sits — itself a finding.** Read down the [INDEX](INDEX.md) and the fleet is
governed *overwhelmingly by hard controls*: deterministic gates, lints, mediators, records. The soft
controls are few — almost all of them *context delivery* — and each is paired with a hard counterpart.
The asymmetry is the point: **probabilistic guidance is used to *aim* agents; deterministic machinery
is what is trusted to *hold the line*.** A marquee control being soft (dynamic context injection is) is
not a weakness to hide but a fact to state — it aims, it does not guarantee.

Soft/hard is *orthogonal to the nine forms* (a `validation` form is hard; an `agent-output` injection
is soft) and is *distinct from architecture*: construction is the limit past hard — a failure
eliminated by construction has no check to run at all, because the failure is unrepresentable.

## Relationships between controls

Controls are rarely standalone. Making the catalog a *pattern language* rather than a list means
naming how they connect; each entry's **Related controls** section tags its links with one of five
relationships:

- **Counterpart (soft ↔ hard).** A soft control paired with a hard control that enforces a property
  the soft one depends on. The hard counterpart is not watching the *agent* — it enforces a property
  of the soft control's *own substrate* (e.g. the rule index stays small and its cross-refs stay
  valid). This is the `Soft·Hard` pairing from the enforcement axis, named as a relationship.
- **Enabler (A → B).** A structural precondition: B cannot work unless A already holds. Dynamic
  context injection is *enabled by* file-addressable constraints and self-documenting rules — without
  them there is nothing to slice or inject. Directional; the reverse reads "B requires A."
- **Layer (defense in depth).** Two or more controls on the *same* failure class at successive
  stages, each a backstop for what the last missed — the path-to-production staircase (commit → cron →
  merge-train → deploy) or the "deepest stack" a single dispatch passes through. Layering is *why* a
  soft control at the front (aim) plus a hard control at the back (hold) is a healthy design, not
  redundancy.
- **Consumer (B ⟵ A).** A runtime / data-flow link: B reads A's output or substrate while it runs.
  Injection *consumes* the component registry; the commit path *consumes* the role fixed at dispatch.
- **Bridge (agent ◀──[ model ]──▶ product).** The **one cross-target relationship**: a
  [models-bridge](models-bridge/) control couples an agent-side concern to a product-side one *through
  a shared model*. The agent side *consumes* the model to reason about the system; the model *governs
  or generates* the product; its drift gate keeps the two faces equal. E.g. the component model — read
  by dynamic-context-injection (agent) and enforced by the boundary lints (product). A control with
  bridge edges to *both* sides is a bridge control.

**The quick discriminator:** an **enabler** must exist *before* B is built; a **consumer** reads A
*while* B runs; a **counterpart** co-exists to keep its pair honest; a **layer** is the same fight
fought again downstream; a **bridge** is the single edge that crosses the agent↔product boundary via a
model. Links that fit none of these are left as a plain *see also*.

## Novelty ratings

Each control carries a rating of how much of it is domain-invented versus off-the-shelf:

- **novel** — invented for agentic engineering; little precedent (e.g. brief-linting, sentinel abort).
- **notable** — a known idea sharpened or repurposed for the agent-fleet setting (e.g. role-typed
  dispatch, merge-train MIS batching).
- **standard** — an established practice, listed for completeness (e.g. staged deploy gates).

---

## Provenance & redaction

- **Sources (four, each doing a different job).** (1) the history-mining control catalog
  (`control-catalog.yaml`) and its binding codebook — the family/form/novelty taxonomy;
  (2) **`CLAUDE.md`** — the numbered rule index, which supplies each control's *governing rule*;
  (3) the **repository** — the real artifact names and their actual inputs/prerequisites; (4) the
  field notes / DCI explainer — the load-bearing principle and the "why not just the naive
  alternative" distinction. Every named artifact was verified against the repository. This catalog
  develops each table row into a full pattern entry.
- **Redaction.** The system/company/product identity is kept out of these writeups so they are
  forwardable and safe to feed the paper's redaction pipeline. Tool names, rule numbers, and
  mechanism detail are engineering substance and are kept.

## Pointers

- **[INDEX.md](INDEX.md)** — the full census across all three roles.
- Per-role analysis: **[`agent/`](agent/)** (governing the fleet) · **[`models-bridge/`](models-bridge/)**
  (the MBSE bridge — why executable models can't drift, why agents make MBSE practical) ·
  **[`product/`](product/)** (governing the artifact).
- `catalogue-figure.html` — the colour-coded figure (four layout options).

*External sources (named, not linked — this catalogue keeps its own references self-contained; see*
*Reference policy):* `CLAUDE.md` (the numbered rule index each *Governing rule(s)* row cites) ·
`control-catalog.yaml` (the machine-readable table this catalog expands) ·
`dynamic-context-injection-explainer.md` (the standalone explainer that seeded the entry template).
