# User-journey model (product-goal → implementation bridge)

**Intent** — A typed model of the product's user journeys — each journey a sequence of user goals, joined
to the endpoints, tests, and resources it exercises — so the path from *what the product is for* to *what
the code must provide* is a queryable model, not tribal knowledge (our instance: a UML-esque journey
model over the remediation product's flows).

| | |
|---|---|
| Summary | A typed model of user journeys — product goals joined to the endpoints and tests each exercises. |
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) — a typed source-of-truth held true by parity audits (every journey ↔ a covering test; every endpoint ↔ some journey) |

## Motivation — the failure it kills

The path from a product goal — *a user signs up, uploads a document, has it remediated, downloads it* —
to the code that serves it lives in people's heads. Nothing ties a journey to the endpoints it hits, the
tests that cover it, or the resources it needs. So journeys go untested without anyone noticing;
endpoints accrete that no journey needs and no one dares delete; and the backend is sized for a blurred
average of all traffic rather than the journey actually underway. Each is a quiet failure — a coverage
hole, dead surface, mis-sized capacity — and none is visible from the code alone, **because the journey
is the one thing the code never names.**

## Why it's not just "the service-flow model" (or a list of pages)

The service-flow model is *structural* — which services and endpoints exist, how they are authed and
wired. It says nothing about *why* an endpoint exists or *who* traverses it. A flat registry of UX
surfaces enumerates the pages but not the paths through them. The journey model is **behavioral and
goal-anchored**: it names each journey as a traversal and joins it to the endpoints, tests, and resources
that journey exercises. The join is the point — this is the one model anchored at *product goals* rather
than *implementation*, so it bridges **down** to the code where the other models bridge **across** it.
The distinction is *a goal-anchored traversal you can query* versus *a structural map that can't tell you
which paths are real*.

## Mechanism

Each journey is a typed record — an ordered sequence of user-facing steps — with edges to the endpoints
it calls, the tests that exercise it, and the backend tier it loads. The model is data, read every run
(the executable-source-of-truth pattern), so the same drift/parity machinery that holds the other models
true applies here. Two parity audits, dedicated to this model, ride on that machinery:

- **Undertested-journey audit** — journey ⋈ tests: a journey with no covering test is a coverage hole
  that a flat test count hides.
- **Dead-endpoint audit** — endpoints ∖ (⋃ journeys): an endpoint no journey reaches is dead surface —
  dead code plus needless attack surface — safe to retire.

Both are the existing drift/parity mechanism instantiated on this model: the model is the new thing, the
audits come from machinery that already exists.

## Prerequisites

- **Journeys named as data**, not implied by UI code — the model only exists once someone writes the
  journeys down (the disciplined upkeep agents make cheap).
- **Stable identifiers for endpoints and tests** the journey can join against — the audits are only as
  true as the join keys.
- **The parity machinery** that holds the other models true, pointed at this one.

## Consequences & costs

- **A new journey or endpoint ⇒ a model edit**, or a parity failure — deliberately; that is the gate
  working.
- **The join keys can rot.** Rename an endpoint without updating the model and the dead-endpoint audit
  either false-alarms or misses; the audit inherits the identifiers' truthfulness.
- **Journey granularity is a modeling choice.** Drawn too coarse the audits are toothless; too fine the
  model is noise. The model makes that granularity explicit rather than leaving it implicit — which is
  the point, and the cost.

## Capability beyond governance — differential scale-up

Past the audits, the same model unlocks a runtime capability. Because it maps each journey to the backend
tier it loads, an orchestrator can **scale tiers differentially by the journey actually underway** on the
frontend — provisioning for the active path instead of a blurred average of all traffic. This is an
optimization the model *enables*, not a failure it *kills*; it is noted because it shows the model
reaching into live operations, not only into audits — but it is not the mechanism's governance claim.

## Known uses

- The typed journey model — each journey a sequence of user goals with edges to endpoints, tests, and
  resources.
- The undertested-journey parity audit (journey ↔ test) and the dead-endpoint audit (endpoint ↔ journey).
- Differential backend scale-up keyed to the active journey (the capability, beyond governance).

## Related mechanisms

- **Bridge** — agents *query* it to reason about which paths are real (agent side) ◀──▶ it *governs* the
  codebase, driving coverage and endpoint-retirement, and optionally live tier-scaling (product side).
  Like every model here: one model, both faces.
- **Counterpart** — [service-flow-model](service-flow-model.md): the *structural* SOA map this model's
  journeys traverse. Journey = the goal-anchored path; service-flow = the endpoints and wiring beneath
  it. The named axis is *product-goal traversal* versus *service topology*.
- *See also* — [drift-parity-gates](drift-parity-gates.md): the undertested-journey and dead-endpoint
  audits are that parity mechanism applied to this model.
- **Enabler** — [executable-source-of-truth](executable-source-of-truth.md): the pattern this
  instantiates — data-not-code, read every run, can't drift.
