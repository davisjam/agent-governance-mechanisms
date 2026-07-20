# The models-bridge — the MBSE substrate between agents and codebase

<!-- summary: Typed models between agents and codebase — the MBSE substrate that makes scaling possible. -->

*The third role in the [catalogue](../README.md). Not "agent" and not "product," but the layer that
**couples** them: typed models of the system that agents **read** to reason about the codebase, and
that **govern** it (a limited slice — config, docs, IPC contracts — is generated from them too). This is the interface through which a
context-bounded agent operates a context-exceeding codebase — the thing that lets agentic engineering
scale past a toy.*

```
     AGENT CONTROLS   ◀────  THE MODEL BRIDGE  ────▶   PRODUCT / CODEBASE
     (govern fleet)    read    (typed system-models)   govern & generate   (the artifact)

  brief-linting  ┐                 ┌ system-model catalog ┐               ┌ NetworkPolicy / wiring gen
  dyn-ctx-inject ┼── query/inject ─┤ meta-sync ══ drift   ├── parity/gen ─┼ deployment topology
  role-dispatch  ┘                 │ query-surface        │               └ boundary / seam lints
                                   └ codegen · read-no-copy ┘
```

## Why this matters

**1 · Executable documentation that cannot drift.** These models are not prose — they are *data that
tools, lints, and deploy scripts read on every run, and that generate real artifacts* (NetworkPolicy,
service wiring, API docs, docker). Because they are continuously *used* and *validated*, the build fails
the moment a model diverges from the code — the
[drift & parity gates](system-models/drift-parity-gates.md) enforce exactly that, the one gate the
rest here depends on: a bridge is only useful if the map equals the territory, and a lying map is worse
than none.

**2 · The barrier was always human.** Model-Based Systems Engineering — modelling your system as typed
source-of-truth — has long been *possible* and rarely *done*: maintaining the models and satisfying the
drift gates is tedious, and humans resent the nagging.

**3 · Agents dissolve the barrier.** That disciplined, repetitive upkeep is exactly what agents do
without complaint — so agentic engineering finally makes MBSE practical, and the same models let an
agent operate a codebase larger than its context in the first place.

## The fourteen mechanisms — one method, two subjects (a Y)

The role is a **Y**: one **method** (the trunk) reified toward the two subjects the bridge couples — the
**product** it ships and the **orchestration** that builds it. The seven method-mechanisms are
subject-agnostic; the seven models split by subject, with three that serve both faces (the *shared spine*).

**The method — the trunk (subject-agnostic).** The pattern, plus the machinery that holds *any* model true:

- [Executable source-of-truth](system-models/executable-source-of-truth.md) ★ — the pattern itself:
  data-not-code, read every run, generated-from, can't drift.
- [Drift & parity gates](system-models/drift-parity-gates.md) — bidirectional model↔reality enforcement
  (the counterpart that makes "can't drift" true).
- [Formal invariant verification](system-models/formal-invariant-verification.md) — each invariant carries
  a temporal-logic form (`[]P` safety / `P ~> Q` liveness) that *derives* its exhaustive checker
  (state-space BFS / a model checker) — proven across every interleaving, not sampled.
- [Coverage → model-node mapping](system-models/coverage-model-mapping.md) — project test coverage onto the
  model's nodes (states, seams, invariants) so an *untested* invariant is a visible gap, not hidden inside
  a line-coverage percentage.
- [Model-driven codegen](system-models/model-driven-codegen.md) — generate artifacts *from* the models,
  provenance-headed.
- [Query surface](system-models/query-surface.md) — `repo-query`, the agent-facing read API.
- [Read-don't-hardcode consumption](system-models/meta-model-consumption.md) — consume by query, never by
  copied snapshot.

**Product-facing models** — the method pointed at the shipped artifact:

- [Service-flow / API model](system-models/service-flow-model.md) — the Backstage-dialect SOA model
  (auth, wiring, NetworkPolicy, API contract).
- [User-journey model](system-models/user-journey-model.md) — the product-goal→implementation bridge:
  journeys (actor / goal / ordered steps) joined to the endpoints and tests they exercise (the one
  *goal-anchored* model).
- [Domain registries](system-models/domain-registries.md) — filetypes, WCAG gaps, cron, UX surfaces,
  competitors, rule metadata.

**Orchestration-facing models** — the method pointed at the agent fleet / dev substrate:

- [Synchronization model (meta-sync)](system-models/synchronization-model.md) — the OS-lock / `flock`
  registry + acquisition ordering that serializes the fleet's shared-resource access.

**Shared-spine models** — one model, both faces:

- [Component & zone model](system-models/component-zone-model.md) — the code-zone / boundary / seam map
  the product *and* the fleet reason over.
- [Mediator & single-writer contracts](system-models/concurrency-contracts.md) — subprocess serialization
  (fleet mediators) + single-writer state contracts (product lifecycles).
- [Deployment & tier topology](system-models/deployment-topology-model.md) — where the product's services
  run *and* the agent-substrate's layer boundaries.

## The bridge relationship — the Y's two exits

Every model here carries a **bridge** edge. The agent side *consumes* the model to reason; the model
*governs or generates* its subject — the **product** (SOA, journeys, WCAG facts) on the product-facing
arm, the **fleet / dev-substrate** (locks, mediators, layers) on the orchestration-facing arm — and the
drift gate keeps model and reality equal. The Y's two exits *are* these two governed subjects; the trunk
is the method they share. The shared-spine models straddle the fork — one model whose two faces govern
each subject in turn.

Naming note: per the catalogue's reference policy, these entries name the `system-models/` substrate and
its files directly — that directory is their subject.
