# Drift & parity gates

**Intent** — The fleet of lints and tests that enforce **bidirectional parity between each model and
reality** — every model row ↔ a real thing on disk, and every real thing ↔ a model row — so the models
*cannot drift*.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `validation` |
| Novelty | notable |
| Real artifact | `lint-*-drift` / `lint-*-parity` (service-flow, public-api, call-graph, deploy-phase, k8s, …) + reverse-mapping tests |
| Governing rule(s) | The per-model charters' drift-gate clauses; **#33** (stable-lint-reads-meta-files) |
| Enforcement | **Hard** (deterministic) · *blocking* — a model that diverges from reality fails the build |

## Motivation — the failure it kills

An [executable model](executable-source-of-truth.md) is only trustworthy if it stays true. The failure
this kills is **silent model drift**: the model says one thing, the code does another, and everything
downstream — dispatch, codegen, deploy — reasons from a lie. Because the model *looks* authoritative,
drift is worse than absence. It recurs whenever code changes without the model, or the model changes
without the code.

## Why it's not just "regenerate the model from the code" (or "trust people to update it)"

Regenerating the model from the code makes the code the source of truth — but the whole point is that
the *model* is the source of truth that *generates* parts of the code (NetworkPolicy, wiring). One-way
regeneration can't express that. Trusting people to update both sides is exactly what fails. Parity
gates instead enforce the invariant **in both directions**: every frontend tree ↔ a matching entity
*and* every entity ↔ a real tree; every handler ↔ its spec; every `flock` ↔ a declared lock; every
component row ↔ a real zone. The distinction is *bidirectional model↔reality parity, build-blocking* —
neither side may drift unilaterally.

## Mechanism

A family of drift/parity checks, one (or a pair) per model: `lint-service-flow-model.py`
(tree↔yaml, both ways), `lint-public-api-drift.py` (handler↔spec), `lint-service-call-graph-drift.py`,
`lint-deploy-phase-table-parity.py`, the k8s parity lints, the sync-coverage lint, and the
`test_*_reverse_mapping.py` tests. Each reads the model at lint-time (rule #33) and fails on divergence.

## Prerequisites

- **A machine-readable model + a machine-readable reality** to compare (the code, the deploy tables,
  the real trees, the `flock` sites).
- **A bidirectional predicate** — both "model ⊆ reality" and "reality ⊆ model" — or one side drifts.
- **Blocking placement** in the gates, or drift is merely reported.

## Consequences & costs

- **A gate per model to author + maintain** — real breadth of enforcement surface.
- **Bidirectional is stricter** — it catches more, and also fails more often on legitimate transitions
  (which is the point: the transition must update both sides).
- **A wrong parity predicate** produces false drift or false confidence.

## Known uses

- `lint-service-flow-model.py`, `lint-public-api-drift.py`, `lint-service-call-graph-drift.py`,
  `lint-deploy-phase-table-parity.py`, k8s parity lints, the sync-coverage lint.
- The `test_*_reverse_mapping.py` model↔tree parity tests.

## Related controls

- **Counterpart** — of every model here: [component-zone](component-zone-model.md) ·
  [synchronization](synchronization-model.md) · [service-flow](service-flow-model.md) · … each typed
  model (construction) is *held true* by its drift gate (the counted control). This is the family's
  pervasive construction-held-by-detection pairing.
- *See also (sibling)* — the product [coherence-lints](../../product/validation-and-conformance/coherence-lints.md):
  the same relational-invariant idea, there across product sources, here across model↔reality.
