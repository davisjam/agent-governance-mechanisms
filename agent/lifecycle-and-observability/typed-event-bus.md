# Typed event bus + playbook

**Intent** — A typed event bus with a closed, const-string topic registry and a companion playbook,
over which substrate emits lifecycle/health events — so the orchestrator observes fleet health from a
*queryable, self-documenting* signal surface rather than by grepping prose logs.

| | |
|---|---|
| Target | Agent · **Lifecycle & observability** |
| Form | `observability` |
| Novelty | notable |
| Real artifact | `event-bus.py`; the event-bus playbook (topic → baseline-healthy / what-looks-wrong) |
| Governing rule(s) | **#46** (substrates emitting topics own observability end-to-end) · **#47** (monitor cron / merge-train / tombstone via the bus) |
| Enforcement | **Hard** (deterministic) · *signal* — emission is mechanical; the bus itself does not block (the derived alerts gate does) |
| Summary | Typed topics plus a playbook surface fleet health live. |

## Motivation — the failure it kills

A fleet's health — is cron running, is the merge-train yielding, are tombstones stuck — is **invisible
without a signal surface**, so degradation accretes silently (cron broken for hours before anyone
notices). The failure is *silent substrate degradation*, and it recurs continuously: the orchestrator
flies blind between the moment something breaks and the moment its downstream effect becomes obvious.

## Why it's not just "log it and grep the logs"

Free-form logs are a **pull** model: you have to know to look, and then parse prose. A **typed** event
bus gives a *queryable* surface, and its topics are a **closed const-string namespace** (a typed
registry, lint-enforced) — so a typo can't silently create a dead topic that disables a signal. Most
important, every topic carries a **playbook entry**: baseline-healthy, what-looks-wrong, and a target
§Q lookup (rule #46 makes a missing playbook entry an *incomplete substrate design*). The distinction
is *a typed, queryable, self-documenting signal with an owned playbook* versus *unstructured logs you
must remember to grep and know how to read*.

## Mechanism

Emitters call `event-bus.py` with a topic drawn from the const-string registry. The playbook maps each
topic → healthy / wrong / §Q entry. Rule #46 requires any design doc that introduces a topic to carry
an Observability block (lint AUDIT-ONLY → BLOCKING). Rule #47 sets the *consumption* cadence: the
orchestrator polls at session start and after cherry-pick waves, with named anomaly triggers (yields
>3 in a row, `discard_lint`, `no_op` >30 min with tombstones queued).

## Prerequisites

- **A typed topic registry** (const strings + a lint) so topics are enumerable and typo-proof.
- **Emit points wired into the substrate** at the events that matter.
- **A playbook keyed by topic** — the signal is only actionable if each topic says what healthy and
  broken look like.
- **An orchestrator that actually polls it** on a defined cadence.

## Consequences & costs

- **Only as useful as playbook coverage.** A topic without a §Q entry is emitted but not
  interpretable — rule #46 exists because that gap is the common failure.
- **Consumption is discipline.** The bus is Hard emission, but *acting* on it depends on the
  orchestrator honoring the poll cadence — the signal can be perfect and still ignored.
- **Registry + emit-point maintenance.** New topics need registry rows, emit wiring, and playbook
  entries kept in sync.

## Known uses

- `event-bus.py` + the const-string topic registry.
- The event-bus playbook (topic → healthy / wrong / §Q); rule #46's Observability-block requirement.
- Rule #47's session-start + post-cherry-pick monitoring cadence.

## Related controls

- **Enabler** — [cron-alerts-gate](cron-alerts-gate.md): alerts are *derived events* on this bus,
  promoted into a blocking gate.
- **Counterpart** — the rule-#46 Observability-block lint keeps every emitting substrate's topics
  documented (the playbook honest).
- *See also (sibling)* — [agent-registry](agent-registry.md), [deploy-heartbeats](deploy-heartbeats.md):
  the fleet's other signal surfaces.
