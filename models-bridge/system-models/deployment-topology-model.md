# Deployment & tier topology

**Intent** — Typed models of *where things run and how they layer* — the managed-deployment topology,
each service's tier class, and the agent-substrate's layer boundaries — so deploy scripts and layering
lints reason about a declared topology, not scattered constants.

| | |
|---|---|
| Summary | Typed models of where things run and how they layer. |
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) — typed models *held true* by the deploy-parity + layer-boundary lints |

## Motivation — the failure it kills

Deployment facts — which layer a service is in, its tier, what may depend on what — end up hardcoded in
deploy scripts and import checks. Hardcoded, they drift from the real topology: a service moves tier, a
layer boundary is quietly crossed, and the deploy or an architectural invariant breaks. And an agent
reasoning about "can layer X import layer Y?" needs the boundary declared, not inferred.

## Why it's not just "encode the topology in the deploy scripts"

Topology in the deploy scripts is a *copy* — it drifts from the real service set and from the layering
the code actually has. These typed models **declare** the topology once (managed-deployment L3 loader,
tier classification, layer-boundary contracts), and parity lints check the declaration against reality
(deploy phase tables, import-layer checks). The distinction is *a declared topology validated against
the system* versus *deploy-time constants that drift*.

## Mechanism

`deployment_topology.py` is the typed L3 loader for the managed-deployment topology; `service_tiers.py`
classifies each service-flow Component's tier; `agent_substrate_layering.py` declares the
layer-boundary contracts for the agent substrate. Deploy scripts and layering lints
(`lint-deploy-phase-table-parity`, the import-layer checks) read them and gate on divergence.

## Prerequisites

- **A typed topology + tier + layering schema**.
- **Deploy scripts + layering lints that read it** rather than hardcoding.
- **Parity lints** against the real deploy tables and import graph.

## Consequences & costs

- **Topology changes are model edits** — a moved tier or new layer boundary means a model edit or a
  parity failure.
- **Layering contracts constrain the code** — a declared boundary blocks a cross-layer import
  (deliberately; a real cost to expedient shortcuts).

## Known uses

- `deployment_topology.py` (L3) · `service_tiers.py` · `agent_substrate_layering.py`.
- `lint-deploy-phase-table-parity.py` + the import-layer boundary lints.

## Related controls

- **Bridge** — agents reason about layering/tiers *through* these models (agent side) ◀──▶ they
  *govern* the real deployment + import structure of the codebase (product side).
- **Enabler** — feeds [model-driven-codegen](model-driven-codegen.md) (deploy/env generation).
- **Counterpart** — [drift-parity-gates](drift-parity-gates.md): the deploy-parity + layer lints.
