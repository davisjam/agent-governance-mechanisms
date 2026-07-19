# Mechanism census

Every mechanism, by **role** and family. `form` (the shape it takes) and `Enf.` (soft/hard) are the
cross-cuts (see [README](README.md)). Families **1–5** = the **agent** role
(the fleet + work-producing substrate); family **6** = the **models-bridge** (the MBSE substrate between
the two); families **7–11** = the **product** role (the shipped artifact). All 58 entries are fully
written (**✅**).

**`Enf.` = soft/hard** (see README *Governance has two mechanisms*): **`Hard`** = deterministic
(blocking / audit / signal); **`Soft`** = probabilistic (influences, cannot block); **`Soft·Hard`** =
soft guidance with a hard counterpart.

# Agent target

## 1. Context & dispatch substrate

*What an agent knows and how it is launched.* — [family folder](agent/context-and-dispatch/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Brief-linting | `validation` | Hard | [brief-linting.md](agent/context-and-dispatch/brief-linting.md) |
| ✅ | Docs hierarchy + governance index | `validation` | Soft·Hard | [docs-hierarchy.md](agent/context-and-dispatch/docs-hierarchy.md) |
| ✅ | Dynamic context injection | `agent-output` | Soft | [dynamic-context-injection.md](agent/context-and-dispatch/dynamic-context-injection.md) |
| ✅ | Role-typed dispatch | `quality-gate` | Hard | [role-typed-dispatch.md](agent/context-and-dispatch/role-typed-dispatch.md) |

## 2. Gates & merge-train

*The path-to-production staircase for agent work.* — [family folder](agent/gates-and-merge-train/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Pre-commit hook (3-stanza, tree-sha markers) | `quality-gate` | Hard | [pre-commit-hook.md](agent/gates-and-merge-train/pre-commit-hook.md) |
| ✅ | Sentinel first-commit early-abort | `quality-gate` | Hard | [sentinel-first-commit.md](agent/gates-and-merge-train/sentinel-first-commit.md) |
| ✅ | Merge-train MIS batching | `quality-gate` | Hard | [merge-train-mis-batching.md](agent/gates-and-merge-train/merge-train-mis-batching.md) |
| ✅ | Staged deploy gates (canary → smoke → promote) | `quality-gate` | Hard | [staged-deploy-gates.md](agent/gates-and-merge-train/staged-deploy-gates.md) |

## 3. Mediators & resource locks

*Host-level wrappers that ration shared compute across concurrent worktrees. Three cap by **cardinality** — one resource-mediator pattern at three lock cardinalities (exclusive `N=1` · bounded `M=8` · a global mutex); the fourth caps by **live pressure** instead of count (an admit-before / shed-during gate on a GREEN/YELLOW/RED signal).* — [family folder](agent/mediators-and-resource-locks/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Test-serializer (N=1 flock on `dotnet test`) | `regression` | Hard | [test-serializer.md](agent/mediators-and-resource-locks/test-serializer.md) |
| ✅ | Build-serializer (M=8 semaphore) | `validation` | Hard | [build-serializer.md](agent/mediators-and-resource-locks/build-serializer.md) |
| ✅ | Aggregate-compute protection (`lint-all` host mutex) | `validation` | Hard | [aggregate-compute-protection.md](agent/mediators-and-resource-locks/aggregate-compute-protection.md) |
| ✅ | Resource-pressure gating (admit before, shed during) | `quality-gate` | Hard | [resource-pressure-gating.md](agent/mediators-and-resource-locks/resource-pressure-gating.md) |

## 4. Lifecycle & observability

*Live signal surfaces over the fleet.* — [family folder](agent/lifecycle-and-observability/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Agent-registry (`agent-registry.jsonl` + marker cache) | `observability` | Hard (signal) | [agent-registry.md](agent/lifecycle-and-observability/agent-registry.md) |
| ✅ | Orchestrator-as-reactor over an event bus | `observability` | Hard (signal) | [typed-event-bus.md](agent/lifecycle-and-observability/typed-event-bus.md) |
| ✅ | Deploy heartbeats + stale-worker detection | `observability` | Hard (signal) | [deploy-heartbeats.md](agent/lifecycle-and-observability/deploy-heartbeats.md) |
| ✅ | Tombstone commits (lifecycle close records) | `audit-trail` | Hard (audit) | [tombstone-commits.md](agent/lifecycle-and-observability/tombstone-commits.md) |
| ✅ | Cron-alerts gate | `observability` | Hard (blocking) | [cron-alerts-gate.md](agent/lifecycle-and-observability/cron-alerts-gate.md) |
| ✅ | Lifecycle hooks (turn-stop / compaction / session-start / pre-action) | `quality-gate` | Soft·Hard | [lifecycle-hooks.md](agent/lifecycle-and-observability/lifecycle-hooks.md) |

## 5. Governance-doc controls

*Documentation treated as enforced infrastructure.* — [family folder](agent/governance-doc-controls/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | CLAUDE.md rule index + cap lint | `validation` | Soft·Hard | [claude-md-rule-index.md](agent/governance-doc-controls/claude-md-rule-index.md) |
| ✅ | Mandatory snippet-table enforcement | `validation` | Hard | [mandatory-snippet-table.md](agent/governance-doc-controls/mandatory-snippet-table.md) |
| ✅ | Epic Definition-of-Done (Final-Opus trust-nothing re-run) | `quality-gate` | Hard | [epic-definition-of-done.md](agent/governance-doc-controls/epic-definition-of-done.md) |
| ✅ | Doc-hygiene lints (index coverage, autogen provenance) | `validation` | Hard | [doc-hygiene-lints.md](agent/governance-doc-controls/doc-hygiene-lints.md) |
| ✅ | Operational playbooks (situation-keyed devops procedures) | `agent-output` | Soft | [operational-playbooks.md](agent/governance-doc-controls/operational-playbooks.md) |
| ✅ | Operator runbook skill (positive map + symptom index, ref-lint-kept) | `agent-output` | Soft·Hard | [operator-runbook-skill.md](agent/governance-doc-controls/operator-runbook-skill.md) |
| ✅ | Epic & design-doc templates | `agent-output` | Soft·Hard | [epic-and-design-templates.md](agent/governance-doc-controls/epic-and-design-templates.md) |

# Models-bridge

## 6. System models

*One MBSE **method** (the trunk — six subject-agnostic mechanisms) reified toward the two subjects the bridge couples: the **product** it ships and the **orchestration** that builds it (a **Y**). Seven models split product-facing (service-flow, user-journey, domain-registries) · orchestration-facing (synchronization) · shared-spine (component-zone, concurrency, deployment — both faces); the six method-mechanisms — including formal, temporal-logic invariant verification — hold them all true. Rows below are grouped trunk → product → orchestration → shared.* — [family folder](models-bridge/system-models/) · [role README](models-bridge/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Executable source-of-truth (data-not-code, can't drift) — *trunk / method* | `typed-ir` | Hard | [executable-source-of-truth.md](models-bridge/system-models/executable-source-of-truth.md) |
| ✅ | Drift & parity gates (model↔reality) — *trunk / method* | `validation` | Hard | [drift-parity-gates.md](models-bridge/system-models/drift-parity-gates.md) |
| ✅ | Formal invariant verification (temporal form → model check) — *trunk / method* | `validation` | Hard | [formal-invariant-verification.md](models-bridge/system-models/formal-invariant-verification.md) |
| ✅ | Model-driven codegen — *trunk / method* | `validation` | Hard | [model-driven-codegen.md](models-bridge/system-models/model-driven-codegen.md) |
| ✅ | Model query surface (`repo-query`) — *trunk / method* | `agent-output` | Soft | [query-surface.md](models-bridge/system-models/query-surface.md) |
| ✅ | Meta-model consumption (read, don't hardcode) — *trunk / method* | `typed-ir` | Hard | [meta-model-consumption.md](models-bridge/system-models/meta-model-consumption.md) |
| ✅ | Service-flow / API model — *product-facing* | `typed-ir` | Hard | [service-flow-model.md](models-bridge/system-models/service-flow-model.md) |
| ✅ | User-journey model (product-goal → implementation) — *product-facing* | `typed-ir` | Hard | [user-journey-model.md](models-bridge/system-models/user-journey-model.md) |
| ✅ | Domain registries — *product-facing* | `typed-ir` | Hard | [domain-registries.md](models-bridge/system-models/domain-registries.md) |
| ✅ | Synchronization model (meta-sync) — *orchestration-facing* | `typed-ir` | Hard | [synchronization-model.md](models-bridge/system-models/synchronization-model.md) |
| ✅ | Component & zone model — *shared spine* | `typed-ir` | Hard | [component-zone-model.md](models-bridge/system-models/component-zone-model.md) |
| ✅ | Mediator & single-writer contracts — *shared spine* | `typed-ir` | Hard | [concurrency-contracts.md](models-bridge/system-models/concurrency-contracts.md) |
| ✅ | Deployment & tier topology — *shared spine* | `typed-ir` | Hard | [deployment-topology-model.md](models-bridge/system-models/deployment-topology-model.md) |

# Product target

## 7. Canonical models & seams

*The one sanctioned typed model or seam per concern, each held in place by a ban-lint.* — [family folder](product/canonical-models-and-seams/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | PdfModel (sole PDF mutation surface) | `typed-ir` | Hard | [pdf-model.md](product/canonical-models-and-seams/pdf-model.md) |
| ✅ | Office Models ({Slides,Docs,Sheets}Model) | `typed-ir` | Hard | [office-models.md](product/canonical-models-and-seams/office-models.md) |
| ✅ | ServiceClient (typed cross-service seam) | `bounded-service` | Hard | [service-client.md](product/canonical-models-and-seams/service-client.md) |
| ✅ | Canonical walkers (one traversal per tree) | `typed-ir` | Hard | [canonical-walkers.md](product/canonical-models-and-seams/canonical-walkers.md) |
| ✅ | Sole raw-Redis seam (the dispatch module) | `bounded-service` | Hard | [raw-redis-seam.md](product/canonical-models-and-seams/raw-redis-seam.md) |

## 8. Validation & conformance

*Deterministic pass/fail checks over the artifact.* — [family folder](product/validation-and-conformance/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | ContentValidator (input ⊆ output fidelity) | `validation` | Hard | [content-validator.md](product/validation-and-conformance/content-validator.md) |
| ✅ | Blocking semantic lints | `validation` | Hard | [semantic-lints.md](product/validation-and-conformance/semantic-lints.md) |
| ✅ | Standards / WCAG rule engine | `validation` | Hard | [standards-rule-engine.md](product/validation-and-conformance/standards-rule-engine.md) |
| ✅ | Cross-source coherence lints | `validation` | Hard | [coherence-lints.md](product/validation-and-conformance/coherence-lints.md) |

## 9. Regression tests

*Repeatable behaviour-pinning bodies.* — [family folder](product/regression-tests/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Test-onion tiers (Smoke / Lite / targeted / full) | `regression` | Hard | [test-onion-tiers.md](product/regression-tests/test-onion-tiers.md) |
| ✅ | FsCheck property tests | `regression` | Hard | [property-tests.md](product/regression-tests/property-tests.md) |
| ✅ | Fuzz campaigns (+ auto-coverage) | `regression` | Hard | [fuzz-campaigns.md](product/regression-tests/fuzz-campaigns.md) |
| ✅ | DDT pin-trailers | `regression` | Hard | [ddt-pin-trailers.md](product/regression-tests/ddt-pin-trailers.md) |

## 10. Provenance & attribution

*Durable records of what the tool changed.* — [family folder](product/provenance-and-attribution/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Per-mutator attribution stamps | `audit-trail` | Hard (audit) | [mutator-stamps.md](product/provenance-and-attribution/mutator-stamps.md) |
| ✅ | F10 mutator-stamp-wiring lint | `validation` | Hard | [f10-wiring-lint.md](product/provenance-and-attribution/f10-wiring-lint.md) |
| ✅ | `derive-changelog` (reconstruct mutations) | `audit-trail` | Hard (audit) | [derive-changelog.md](product/provenance-and-attribution/derive-changelog.md) |
| ✅ | `a11y_` prefix convention | `repair-vocab` | Hard | [a11y-prefix.md](product/provenance-and-attribution/a11y-prefix.md) |

## 11. Repair vocabulary

*The bounded move-space of the remediator.* — [family folder](product/repair-vocabulary/)

| ✓ | Mechanism | Form | Enf. | Entry |
|---|---|---|---|---|
| ✅ | Typed `ViolationCategory` / `FailureCategory` enums | `repair-vocab` | Hard | [typed-categories.md](product/repair-vocabulary/typed-categories.md) |
| ✅ | Closed remediation-verb sets | `repair-vocab` | Hard | [remediation-verbs.md](product/repair-vocabulary/remediation-verbs.md) |
| ✅ | Codemod-first threshold (N≳50 → AST transformer) | `repair-vocab` | Soft | [codemod-first.md](product/repair-vocabulary/codemod-first.md) |

---

**Three roles complete — 58 mechanisms across 11 families, all fully developed.**
**Agent (25):** Context & dispatch (4) · Gates & merge-train (4) · Mediators & resource locks (4) ·
Lifecycle & observability (6) · Governance-doc controls (7, incl. the **CLAUDE.md rule index**
meta-mechanism).
**Models-bridge (13):** the MBSE **method** (6 subject-agnostic mechanisms, incl. **formal temporal-logic invariant verification**) reified as a **Y** over 7 models — product-facing 3 (service-flow · user-journey · domain-registries) · orchestration-facing 1 (synchronization) · shared-spine 3 (component-zone · concurrency · deployment, both faces);
the MBSE substrate through which a bounded agent operates an unbounded codebase.
**Product (20):** Canonical models & seams (5) · Validation & conformance (4) · Regression tests (4) ·
Provenance & attribution (4) · Repair vocabulary (3).
