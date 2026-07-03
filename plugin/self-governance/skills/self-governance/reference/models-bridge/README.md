# The models-bridge — the MBSE substrate between agents and codebase

<!-- summary: Typed models between agents and codebase — the MBSE substrate that makes scaling possible. -->

*The third role in the [catalogue](../README.md). Not "agent" and not "product," but the layer that
**couples** them: typed models of the system that agents **read** to reason about the codebase, and
that the codebase is **generated and governed from**. This is the interface through which a
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

## Why this is the crux

**1 · Executable documentation that cannot drift.** These models are not prose — they are *data that
tools, lints, and deploy scripts read on every run, and that generate real artifacts* (NetworkPolicy,
service wiring, API docs, docker). Because they are continuously *used* and *validated*, they can't go
stale: the build fails the moment a model diverges from the code (that is what [meta-sync /
drift-parity-gates](system-models/drift-parity-gates.md) enforces). Prose docs drift because nothing
forces them true; executable models can't, because something *breaks* when they lie.

**2 · The barrier was always human.** Model-Based Systems Engineering — modelling your system as typed
source-of-truth — has been *possible* and rarely *done*, because maintaining the models and satisfying
the drift gates is **tedious**, and humans resent the nagging. So it stays aspirational.

**3 · Agents dissolve the barrier.** Maintaining the model, running the parity gates, regenerating
artifacts is exactly the disciplined, repetitive upkeep agents do without complaint. So agentic
engineering is what finally makes MBSE *practical* — and since the same models are what let agents
operate a large codebase at all, the conclusion is strong: **every project doing serious agentic
engineering should adopt the model bridge.**

The single load-bearing control is **[meta-sync](system-models/synchronization-model.md)**'s cousin,
the [drift & parity gates](system-models/drift-parity-gates.md): a bridge is only useful if the map
equals the territory. Without bidirectional drift enforcement the bridge *lies*, and a lying map is
worse than none.

## The eleven controls (one family: `system-models/`)

**Six models** — each a typed source-of-truth for one slice of the system:

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

**Five mechanisms** over the models:

7. [Executable source-of-truth](system-models/executable-source-of-truth.md) ★ — the pattern itself:
   data-not-code, read every run, generated-from, can't drift.
8. [Drift & parity gates](system-models/drift-parity-gates.md) — bidirectional model↔reality
   enforcement (the counterpart that makes "can't drift" true).
9. [Model-driven codegen](system-models/model-driven-codegen.md) — generate artifacts *from* the
   models, provenance-headed.
10. [Query surface](system-models/query-surface.md) — `repo-query`, the agent-facing read API.
11. [Read-don't-hardcode consumption](system-models/meta-model-consumption.md) — consume by query,
    never by copied snapshot.

## The bridge relationship

Every model here carries a **bridge** edge — the one relationship that crosses the agent↔product
boundary. The agent side *consumes* the model to reason; the model *governs or generates* the product;
the drift gate keeps the two faces equal. See the umbrella [README](../README.md#relationships-between-controls).

Naming note: per the catalogue's reference policy, these entries name the `system-models/` substrate and
its files directly — that directory is their subject.
