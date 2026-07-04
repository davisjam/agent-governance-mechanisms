# Executable source-of-truth models

**Intent** — Model the system as **typed data that tools read on every run and generate real artifacts
from** — so the model is *executable documentation that cannot drift*, and the codebase becomes
operable by a context-bounded agent.

| | |
|---|---|
| Summary | Typed models read every run and generated from — can't drift. |
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) — the models are *construction* (typed IR); the counted controls are the [drift/parity gates](drift-parity-gates.md) that fail the build when a model diverges from reality |

> **★ The bridge.** This is the flagship of the third role: the model layer is the **interface through
> which a context-bounded agent operates a context-exceeding codebase.** It faces both ways — agents
> read it to reason; the codebase is governed from it (a limited slice — config, docs, IPC contracts — is generated from it too). The other bridge entries are its
> models and mechanisms.

## Motivation — the failure it kills

A large codebase **exceeds any agent's context window** — no agent can hold 280 KLOC. Left to read the
raw code, an agent gets lost, re-derives the architecture (badly), and drifts. Meanwhile the
architecture itself lives only implicitly, scattered across the code, so *humans* re-derive it too. The
failure is *no shared, authoritative, compact representation of the system* — which caps how large a
codebase agents can operate on at all.

## Why it's not just "write architecture docs"

Prose architecture docs **drift**, because nothing forces them true — they are read by humans
occasionally and validated never. These models are **executable**: they are *data that tools, lints,
and deploy scripts read on every run*, and that *generate* real artifacts (NetworkPolicy, service
wiring, API docs). Because they are continuously *used* and *validated*, they **cannot** go stale — the
build fails the moment a model diverges from the code. The distinction is *executable, continuously-
exercised source-of-truth* versus *prose that is trusted and rots*.

**Why now:** MBSE — modelling your system as typed source-of-truth — has long been *possible* and
rarely *done*: maintaining the models and satisfying the drift gates is tedious, and humans resent the
nagging. Agents dissolve that barrier — regenerating artifacts and running the parity gates is exactly
the disciplined, repetitive upkeep they do without complaint. So agentic engineering finally makes MBSE
practical, and the same models let an agent operate a codebase larger than its context.

## Mechanism

The model catalog holds typed models (Backstage-dialect YAML for services, typed loaders for the rest)
that **import nothing** — pure data. Consumers read them at run/lint-time (a lint that *reads* the
meta-file is preferred over codegen, which is preferred over a hand-rolled copy). Every model is (a)
*pinned* by a doc-derived characterization test, (b) *held true* by a drift/parity gate, and (c)
frequently *read* or *generated-from* — so it is exercised constantly.

## Prerequisites

- **Typed models that import nothing** — data, not code, so anything can read them cheaply.
- **Continuous consumption** — the model must be read on real runs, or it is just another doc.
- **A drift gate per model** ([drift-parity-gates](drift-parity-gates.md)) — without enforcement the
  "cannot drift" claim is a hope.

## Consequences & costs

- **Upkeep is real** — the models must be maintained and the drift gates satisfied on every change;
  this is exactly the tedium that stops humans, and the reason it needs agents.
- **A wrong model is worse than none** — an authoritative-looking model that has drifted misleads
  everything downstream; hence the drift gates are not optional.
- **Modelling discipline up front** — deciding what to model, and in what dialect, is design work.

## Known uses

- The model catalog (typed YAML/JSON + loaders; imports nothing).
- The preference order: a stable lint that reads the meta-file, over codegen, over a hand-rolled copy.
- Each model's doc-derived characterization pin.

## Related mechanisms

- **Bridge** — every model here couples an agent-side use (query/inject) to a product-side use
  (govern/generate); see the individual models below.
- **Counterpart** — [drift-parity-gates](drift-parity-gates.md): the hard control that makes "cannot
  drift" true.
- *See also* — the six models: [component-zone](component-zone-model.md) ·
  [synchronization](synchronization-model.md) · [concurrency-contracts](concurrency-contracts.md) ·
  [service-flow](service-flow-model.md) · [deployment-topology](deployment-topology-model.md) ·
  [domain-registries](domain-registries.md); and the mechanisms
  [codegen](model-driven-codegen.md) · [query-surface](query-surface.md) ·
  [consumption](meta-model-consumption.md).
