# Executable source-of-truth models

**Intent** — Model the system as **typed data that tools read on every run and generate real artifacts
from** — so the model is *executable documentation that cannot drift*, and the codebase becomes
operable by a context-bounded agent.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Novelty | novel |
| Real artifact | `system-models/` (typed YAML/JSON + Python loaders); consumed by lints, deploy, dispatch |
| Governing rule(s) | The `system-models/` charter ("declarative source-of-truth catalog … data, not code; tools read from here"); **#33** (stable-lint-reads-meta-files) |
| Enforcement | **Hard** (deterministic) — the models are *construction* (typed IR); the counted controls are the [drift/parity gates](drift-parity-gates.md) that fail the build when a model diverges from reality |
| Summary | Typed models read every run and generated from — can't drift. |

> **★ The bridge.** This is the flagship of the third role: the model layer is the **interface through
> which a context-bounded agent operates a context-exceeding codebase.** It faces both ways — agents
> read it to reason; the codebase is generated and governed from it. The other bridge entries are its
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

**Why now, and why every project should:** MBSE — modelling your system as typed source-of-truth — has
always been *possible* and rarely *done*, because maintaining the models and satisfying the drift gates
is **tedious**, and humans resent the nagging, so it stays aspirational. Agents dissolve that barrier:
maintaining the model, running the parity gates, regenerating artifacts is exactly the disciplined,
repetitive upkeep they do without complaint. So agentic engineering is what finally makes MBSE
*practical* — and since the same models are what let agents scale to a large codebase, the model bridge
is not optional infrastructure, it is *the* enabling substrate.

## Mechanism

`system-models/` holds typed models (Backstage-dialect YAML for services, typed Python loaders for the
rest) that **import nothing** — pure data. Consumers read them at run/lint-time (rule #33: a lint that
reads the meta-file beats codegen beats a hand-rolled copy). Every model is (a) *pinned* by a
doc-derived characterization test, (b) *held true* by a drift/parity gate, and (c) frequently *read* or
*generated-from* — so it is exercised constantly.

## Prerequisites

- **Typed models that import nothing** — data, not code, so anything can read them cheaply.
- **Continuous consumption** — the model must be read on real runs, or it is just another doc.
- **A drift gate per model** ([drift-parity-gates](drift-parity-gates.md)) — without enforcement the
  "cannot drift" claim is a hope.

## Consequences & costs

- **Upkeep is real** — the models must be maintained and the drift gates satisfied on every change;
  this is exactly the tedium that stops humans, and the reason it needs agents.
- **A wrong model is worse than none** — an authoritative-looking model that has drifted misleads
  everything downstream; hence the drift gates are load-bearing, not optional.
- **Modelling discipline up front** — deciding what to model, and in what dialect, is design work.

## Known uses

- The `system-models/` catalog (typed YAML/JSON + Python loaders; imports nothing).
- Rule #33's stable-lint-reads-meta-files preference order.
- Each model's `test__*_doc_derived.py` characterization pin.

## Related controls

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
