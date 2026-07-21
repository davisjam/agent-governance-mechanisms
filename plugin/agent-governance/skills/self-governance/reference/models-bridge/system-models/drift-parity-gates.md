# Drift & parity gates

**Intent** — The fleet of lints and tests that enforce **bidirectional parity between each model and
reality** (every model row ↔ a real thing on disk, and every real thing ↔ a model row), so the models
*cannot drift*.

| | |
|---|---|
| Summary | Bidirectional model↔reality checks so models cannot drift. |
| Target | Bridge · **System models** |
| Form | `validation` |
| Enforcement | **Hard** (deterministic) · *blocking* — a model that diverges from reality fails the build |

## Motivation — the failure it kills

An [executable model](executable-source-of-truth.md) is only trustworthy if it stays true. The failure
this kills is **silent model drift**: the model says one thing, the code does another, and everything
downstream (dispatch, codegen, deploy) reasons from a lie. Because the model *looks* authoritative,
drift is worse than absence. It recurs whenever code changes without the model, or the model changes
without the code.

## Why it's not just "regenerate the model from the code" (or "trust people to update it")

Regenerating the model from the code makes the code the source of truth. But the *model* must be the
source of truth that *generates* parts of the code (NetworkPolicy, wiring). One-way
regeneration can't express that. Trusting people to update both sides is exactly what fails. Parity
gates instead enforce the invariant **in both directions**: every frontend tree ↔ a matching entity
*and* every entity ↔ a real tree; every handler ↔ its spec; every `flock` ↔ a declared lock; every
component row ↔ a real zone. The distinction is *bidirectional model↔reality parity, build-blocking* —
neither side may drift unilaterally.

## Mechanism

A family of drift/parity checks, one (or a pair) per model: a service-flow parity lint (tree↔yaml, both
ways), a public-API drift lint (handler↔spec), a service-call-graph drift lint, a deploy-phase-table
parity lint, the k8s parity lints, the sync-coverage lint, and the
[[reverse-mapping-test|model↔tree reverse-mapping tests]]. Each reads the model at lint-time (a lint
that *reads* the meta-file is preferred over codegen, which is preferred over a hand-rolled copy) and
fails on divergence.

## Prerequisites

- **A machine-readable model + a machine-readable reality** to compare (the code, the deploy tables,
  the real trees, the `flock` sites).
- **A bidirectional predicate** — both "model ⊆ reality" and "reality ⊆ model," or one side drifts.
- **Blocking placement** in the gates, or drift is merely reported.

## Consequences & costs

- **A gate per model to author + maintain** — real breadth of enforcement surface.
- **Bidirectional is stricter** — it catches more, and also fails more often on legitimate transitions
  (which is the point: the transition must update both sides).
- **A wrong parity predicate** produces false drift or false confidence.

## Known uses

- The service-flow, public-API-drift, service-call-graph-drift, and deploy-phase-table parity lints;
  the k8s parity lints; the sync-coverage lint.
- The [[reverse-mapping-test|model↔tree reverse-mapping tests]].

## Related mechanisms

- **Counterpart** — of every model here: [component-zone](component-zone-model.md) ·
  [synchronization](synchronization-model.md) · [service-flow](service-flow-model.md) · … each typed
  model (construction) is *held true* by its drift gate (the counted control). This is the family's
  pervasive construction-held-by-detection pairing.
- *See also (sibling)* — the product [coherence-lints](https://davisjam.github.io/agent-governance-mechanisms/product/validation-and-conformance/coherence-lints.html):
  the same relational-invariant idea, there across product sources, here across model↔reality.
