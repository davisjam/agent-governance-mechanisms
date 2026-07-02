# Service-flow / API model

**Intent** — A Backstage-dialect model of the service-oriented architecture — every service, its APIs,
inter-service auth, URL wiring, and frontend trees — that is the **source of truth** the deployment,
NetworkPolicy, and API docs are *generated from* and validated against.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Novelty | notable |
| Real artifact | `system-models/services/*.yaml` (Backstage `Component`/`API`/`System`) + `web-api/` (OpenAPI) + `wire-contracts/` + `config/` |
| Governing rule(s) | The service-flow-model charter; drift gates `lint-service-flow-model.py`, `lint-public-api-drift.py`, `lint-service-call-graph-drift.py` |
| Enforcement | **Hard** (deterministic) — a typed model *held true* by bidirectional parity gates (tree↔yaml, handler↔spec, call-graph↔model) |

## Motivation — the failure it kills

A service-oriented deployment has many moving parts that must agree: inter-service auth headers, URL env
vars, NetworkPolicy, the `SOA_SERVICES` deploy table, the public-API contract, the frontend trees. Kept
in sync *by hand* across code + YAML + deploy scripts, they drift — a service gains an endpoint the
NetworkPolicy doesn't allow, a handler diverges from its spec, a frontend tree exists with no entity.
Each drift is a production-shaped bug, and there are many surfaces to drift.

## Why it's not just "configure each piece where it's needed"

Per-piece configuration means the same fact (a service's auth, its URL, its APIs) is restated in code,
in deploy YAML, in NetworkPolicy — and restated facts diverge. The service-flow model is the **single
Backstage-dialect source of truth**: NetworkPolicy, service catalog, and env wiring are *generated from
it*, and **bidirectional drift gates** enforce it (every frontend tree ↔ a matching entity *and* every
entity ↔ a real tree; every handler ↔ its OpenAPI spec; the call-graph ↔ the declared model). The
distinction is *one generated-and-validated source of truth* versus *N hand-synced restatements that
drift*.

## Mechanism

`services/*.yaml` uses the Backstage entity dialect (`kind: Component | API | System`) with
`<org>.dev/*` annotations for SOA fields; `web-api/` holds OpenAPI fragments; `wire-contracts/` and
`config/` model the inter-service wire schemas and config. Generators emit NetworkPolicy, the service
catalog, env, and public-API docs *from* these (see [model-driven-codegen](model-driven-codegen.md)).
The drift lints enforce parity in both directions.

## Prerequisites

- **A service-architecture dialect** (here Backstage) expressive enough for the SOA fields.
- **Generators** that emit the real artifacts from the model.
- **Bidirectional parity gates** so neither the model nor reality can drift unilaterally.

## Consequences & costs

- **A new service/endpoint/tree ⇒ a model edit** or a parity-gate failure (deliberately).
- **Dialect lock-in** — adopting Backstage's schema inherits its conventions (a deliberate rule-#22
  "adopt the canonical schema" trade).
- **Generator + gate maintenance** across several surfaces.

## Known uses

- `services/*.yaml` (Backstage) — source of truth for inter-service auth, URLs, NetworkPolicy, SOA table.
- `web-api/` OpenAPI + `wire-contracts/` + `config/` schemas.
- Drift gates: `lint-service-flow-model.py` (tree↔yaml parity), `lint-public-api-drift.py` (handler↔spec).

## Related controls

- **Bridge** — agents *query* it ([query-surface](query-surface.md) `service-flow`/`web-api`) to reason
  about the SOA (agent side) ◀──▶ it *generates & governs* the deployed system — NetworkPolicy, wiring,
  API docs (product side). The clearest bridge: one model, both faces.
- **Enabler** — feeds [model-driven-codegen](model-driven-codegen.md).
- **Counterpart** — [drift-parity-gates](drift-parity-gates.md): the bidirectional parity lints.
