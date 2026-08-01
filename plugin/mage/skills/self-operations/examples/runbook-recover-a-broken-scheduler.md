# Example runbook — recover a broken scheduler

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's scheduler + tools.*

**Lifecycle:** (L-cron) · scheduled automation.

## Problem (universal)

A cron / scheduler that runs the fleet's background automation (the batcher, the alert sweeper, the
housekeeping tick) has stalled — or worse, broke while running its own fix and is now emitting alerts that
block new work. The queue it drains is backing up. Detect it from its alerts, quiesce it so it stops making
things worse, recover the queue by hand, then re-arm — in that order.

## Steps (typed)

- **[RUNNABLE] Detect from the alert stream, not from a hunch.** Read the scheduler's own alerts — the
  unconsumed ones since you last looked, ranked by severity. A high-severity unresolved alert is often what's
  *blocking* new dispatch, so it's both the symptom and the gate.
  `<your alert query> --unconsumed --min-severity high`
- **[JUDGMENT-AUTOMATABLE] Classify what broke.** A carried brief that reads the alerts + the scheduler's
  last run state and bins the fault — *stalled* (didn't fire), *wedged* (fired but hung mid-run), *self-broke*
  (its own maintenance step left the queue inconsistent), or *cascading* (alerts blocking the work that would
  clear them). The class decides whether you quiesce, drain, or hand-repair first.
  Carried brief: *"Given these alerts + the last scheduler run, classify the fault (stalled / wedged /
  self-broke / cascading) and name the safe recovery order (quiesce → recover-queue → re-arm), flagging any
  step that needs a human."*
- **[RUNNABLE] Quiesce the scheduler.** Stop it firing new ticks before you touch the queue — a tick landing
  mid-repair re-corrupts what you're fixing. Pause the schedule (don't delete it) and let any in-flight tick
  finish or time out.
  `<your scheduler pause>`
- **[JUDGMENT-IRREDUCIBLE] Surface a queue that's inconsistent in a way you can't safely auto-repair** — a
  half-processed batch, an item in two states at once, a lock with no owner. A hand-repair of durable state
  is a human call; surface it with the evidence, don't guess.
- **[RUNNABLE] Recover the queue** — clear the stuck/duplicate items to a consistent state, then acknowledge
  or resolve the alerts that were blocking new work (so dispatch unblocks).
  `<your queue repair>` · `<your alert resolve> <id>`
- **[RUNNABLE] Re-arm and verify one clean tick.** Un-pause the schedule and watch a single tick run
  end-to-end — confirm it drains the queue and emits no new alert before you walk away.
  `<your scheduler resume>` · `<your alert query> --since now`

## Second-order note

Order is the whole game: **quiesce before you repair** (a live tick re-breaks the fix), and **recover the
queue before you re-arm** (re-arming onto an inconsistent queue just re-triggers the fault). Resolve
work-blocking alerts as part of recovery, not after — an unresolved high-severity alert can refuse the very
dispatch that would clear it (a deadlock). If the scheduler broke its own fix, that's a recurrence: hand the
class to the partner self-governance skill to design a guard (an idempotent, re-runnable maintenance step;
a dedup that stops concurrent ticks trampling each other) so the next tick can't re-corrupt the queue.
