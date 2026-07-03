# Orchestrator-as-reactor over an event bus

**Intent** — A typed event bus with a closed, const-string topic registry and a companion **playbook**,
over which substrate emits lifecycle/health events — turning the orchestrator into a **reactor** over the
fleet: it reads health from a *queryable, self-documenting* signal surface and *reacts* to each event
with a playbook-prescribed response, which is what keeps a fleet of agents productive over long-running
sessions rather than drifting into silent breakage.

| | |
|---|---|
| Summary | The orchestrator reacts to typed fleet events via a per-topic playbook. |
| Target | Agent · **Lifecycle & observability** |
| Form | `observability` |
| Enforcement | **Hard** (deterministic) · *signal* — emission is mechanical; the bus itself does not block (the derived alerts gate does) |

## Motivation — the failure it kills

A fleet's health — is cron running, is the merge-train yielding, are tombstones stuck — is **invisible
without a signal surface**, so degradation accretes silently (cron broken for hours before anyone
notices). Worse, without a reaction loop the orchestrator is a passive observer: it can only steer the
fleet if it *reacts* to what the substrate reports. The failure is *silent substrate degradation and an
un-reacting orchestrator*, and it recurs continuously across a long session — the fleet slowly stops
being productive while each dispatch still looks locally fine.

## Why it's not just "log it and grep the logs"

Free-form logs are a **pull** model: you have to know to look, and then parse prose. A **typed** event
bus gives a *queryable* surface, and its topics are a **closed const-string namespace** (a typed
registry, lint-enforced) — so a typo can't silently create a dead topic that disables a signal. Most
important, every topic carries a **playbook entry**: baseline-healthy, what-looks-wrong, and a target
§Q lookup (a substrate-observability rule makes a missing playbook entry an *incomplete substrate design*). The distinction
is *a typed, queryable, self-documenting signal with an owned playbook* versus *unstructured logs you
must remember to grep and know how to read*.

## Mechanism

Emitters call the event bus with a topic drawn from the const-string registry. The playbook maps each
topic → healthy / wrong / §Q entry. A substrate-observability rule requires any design doc that
introduces a topic to carry an Observability block (lint AUDIT-ONLY → BLOCKING). A monitoring-cadence
rule sets the *consumption* cadence: the
orchestrator polls at session start and after cherry-pick waves, with named anomaly triggers (yields
>3 in a row, `discard_lint`, `no_op` >30 min with tombstones queued). Together these are the **reactor
loop**: emit → the orchestrator reads the queryable surface → matches the event to its playbook entry →
takes the prescribed action (dispatch a fix, open a recovery playbook, hold new work). The playbook is
the load-bearing half — it is what turns a raw signal into a *reaction* rather than a passive read.

## Prerequisites

- **A typed topic registry** (const strings + a lint) so topics are enumerable and typo-proof.
- **Emit points wired into the substrate** at the events that matter.
- **A playbook keyed by topic** — the signal is only actionable if each topic says what healthy and
  broken look like.
- **An orchestrator that actually polls it** on a defined cadence.

## Consequences & costs

- **Only as useful as playbook coverage.** A topic without a §Q entry is emitted but not
  interpretable — the substrate-observability rule exists because that gap is the common failure.
- **Consumption is discipline.** The bus is Hard emission, but *acting* on it depends on the
  orchestrator honoring the poll cadence — the signal can be perfect and still ignored.
- **Registry + emit-point maintenance.** New topics need registry rows, emit wiring, and playbook
  entries kept in sync.

## Known uses

- The event bus + its const-string topic registry.
- The event-bus playbook (topic → healthy / wrong / §Q); the Observability-block requirement for any
  topic-introducing design doc.
- The session-start + post-cherry-pick monitoring cadence.

## Related controls

- **Consumer** — the *reaction* half is an
  [operational playbook](../governance-doc-controls/operational-playbooks.md): each topic's playbook
  entry is the situation-keyed procedure the orchestrator runs when the event fires.
- **Enabler** — [cron-alerts-gate](cron-alerts-gate.md): alerts are *derived events* on this bus,
  promoted into a blocking gate.
- **Counterpart** — the Observability-block lint keeps every emitting substrate's topics
  documented (the playbook honest).
- *See also (sibling)* — [agent-registry](agent-registry.md), [deploy-heartbeats](deploy-heartbeats.md):
  the fleet's other signal surfaces.
