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

## The twelve mechanisms (one family: `system-models/`)

**Seven models** — each a typed source-of-truth for one slice of the system:

1. [Component & zone model](system-models/component-zone-model.md) — the code-zone / boundary / seam map.
2. [Synchronization model (meta-sync)](system-models/synchronization-model.md) — the OS-lock / `flock`
   registry + acquisition ordering.
3. [Mediator & single-writer contracts](system-models/concurrency-contracts.md) — subprocess
   serialization + single-writer state contracts.
4. [Service-flow / API model](system-models/service-flow-model.md) — the Backstage-dialect SOA model
   (auth, wiring, NetworkPolicy, API contract).
5. [Deployment & tier topology](system-models/deployment-topology-model.md) — where things run and how
   they layer.
6. [Domain registries](system-models/domain-registries.md) — filetypes, WCAG gaps, cron, UX surfaces,
   competitors, rule metadata.
7. [User-journey model](system-models/user-journey-model.md) — the product-goal→implementation bridge:
   journeys (actor / goal / ordered steps) joined to the endpoints and tests they exercise, hosted as a
   `Journey` kind in the service-flow dialect (the one *goal-anchored* model).

**Five mechanisms** over the models:

8. [Executable source-of-truth](system-models/executable-source-of-truth.md) ★ — the pattern itself:
   data-not-code, read every run, generated-from, can't drift.
9. [Drift & parity gates](system-models/drift-parity-gates.md) — bidirectional model↔reality
   enforcement (the counterpart that makes "can't drift" true).
10. [Model-driven codegen](system-models/model-driven-codegen.md) — generate artifacts *from* the
    models, provenance-headed.
11. [Query surface](system-models/query-surface.md) — `repo-query`, the agent-facing read API.
12. [Read-don't-hardcode consumption](system-models/meta-model-consumption.md) — consume by query,
    never by copied snapshot.

## The bridge relationship

Every model here carries a **bridge** edge — the one relationship that crosses the agent↔product
boundary. The agent side *consumes* the model to reason; the model *governs or generates* the product;
the drift gate keeps the two faces equal — the one cross-role edge in the catalogue.

Naming note: per the catalogue's reference policy, these entries name the `system-models/` substrate and
its files directly — that directory is their subject.
