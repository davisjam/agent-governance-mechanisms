### Concept

Make the fleet's live state legible and make each bad state actionable. The stack is the surface that
turns a running-but-wrong pipeline — the worst failure mode, because it is invisible — into a named
signal an operator can see and a procedure they can follow. Emitting signals is only half of it: a
signal nobody knows how to answer is noise, and a procedure with no signal to trigger it never runs.

### Mandatory members

- **role:typed-event-bus** — the typed stream every substrate emits its lifecycle facts onto. It is
  the single place the operator watches, so state is legible from one surface instead of scraped from
  many logs.
- **role:operational-playbooks** — a written response per signal the bus can raise. Observability that
  surfaces a red state without saying what to do about it stops at *noticing*; the playbook is what
  makes the notice actionable. The two are counterparts — neither is useful alone.

### Complementary members

- **role:deploy-heartbeats** — periodic liveness beats plus stale-worker detection, so a silent hang
  is distinguishable from slow progress. High-value on a long-running pipeline; the core see-and-act
  loop functions without per-phase beats.
- **role:cron-alerts-gate** — let an unresolved high-severity alert block new work until it is
  acknowledged. Raises the cost of ignoring a signal; a layer on top of the bus, not a precondition
  for observing state.
- **role:caused-by-provenance** — trace a change back to the agent that made it, so an incident has a
  starting point. Sharpens diagnosis; the observe-and-respond loop runs without the back-trace.
