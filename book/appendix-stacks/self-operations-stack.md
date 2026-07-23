## Concept

The orchestrator runs itself: it does not poll a wall of dashboards and remember what to do. It
reacts to typed signals, and each signal it can act on carries a written response. The stack is the
loop that lets an operator (human or agent) drive a fleet from events plus procedures instead of from
memory. Its templates are what keep the loop from re-deriving structure on every turn.

## Mandatory members

- **role:typed-event-bus** — the orchestrator as a reactor over a typed signal stream. Every
  lifecycle fact (an agent registered, a gate failed, a deploy stalled) arrives as a named event, so
  the operator dispatches on structure, not on scraped text. Remove it and the loop has nothing to
  react to.
- **role:operational-playbooks** — a procedure per situation the signals surface: symptom → steps.
  A signal with no playbook is unactioned noise. The pairing is the point — the bus says *what
  happened*, the playbook says *what to do* — and neither half is optional.
- **role:epic-and-design-templates** — the fixed shapes work is filed into (an Epic, a design doc)
  so the operator schedules and closes units instead of inventing a structure each time. The
  self-operating loop needs a unit of work to operate on; the template supplies it.

## Complementary members

- **role:reflection-facet-substrate** — tempo-gated policy nudges that remind the operator of a
  standing discipline at the right cadence. It raises adherence without being on the critical path;
  the loop still runs correctly if a nudge never fires.
- **role:dynamic-context-injection** — surface the right slice of guidance to the operator at the
  moment a decision is due. Convenience layered on top of the templates and playbooks, not a
  precondition for them.
- **role:operator-runbook-skill** — a positive map of how the substrate works, with a symptom index
  as fallback. Speeds recovery; the react-and-follow loop functions without it.
