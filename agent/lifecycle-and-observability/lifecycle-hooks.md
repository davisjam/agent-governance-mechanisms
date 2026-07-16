# Lifecycle hooks (interpose on the agent runtime's events)

**Intent** — Bind a script to the agent runtime's lifecycle events — turn-stop, pre-compaction,
session-start, before-a-tool-call — so a step the operator keeps *omitting at runtime* fires
deterministically, whether or not anyone remembered it.

| | |
|---|---|
| Summary | A hook on a runtime lifecycle event so an operator's omitted step can't be forgotten. |
| Target | Agent · **Lifecycle & observability** |
| Form | `quality-gate` |
| Enforcement | **Soft·Hard** — the *firing* is hard (the runtime guarantees the hook runs at the event); the *payload* is either a hard **block** that denies the action or **soft guidance** injected back into the agent's context |

## Motivation — the failure it kills

Some recurring failures live not in the code an agent writes but in the **loop that drives it** — the
operator (a human, or an orchestrator agent) skipping a step at a predictable moment. Ending a turn with
ratified work still queued. Compacting context without first writing a hand-off. Opening a session
without reading the alert backlog. Editing outside the sanctioned worktree. A lint can't reach these:
there is no source artifact to analyze, and the omission happens at runtime, in the loop itself. A
house-rule — *"remember to…"* — only aims a probabilistic operator, and it rots, because the step gets
skipped exactly when attention is thin. The failure recurs every session.

## Why it's not just "a house-rule in the governance doc"

A governance-doc rule depends on the operator **recalling it at the right moment** — which is precisely
what fails under load. A lifecycle hook removes the recall: the runtime fires it on a named event, so
the check runs whether or not anyone remembered. It **splits the two halves of enforcement that a lint
fuses.** The *firing* is hard — guaranteed by the runtime, impossible to forget. The *payload* is
either: a hard **block** that denies the action (a pre-edit guard refusing a write outside the
worktree), or **soft guidance** injected back into the agent's own context (a turn-stop hook that
re-states *"work still queued"* and leaves the agent to judge). The reflex case — *hard delivery of soft
guidance* — is the one to understand: it does not swap judgment for machinery, it makes the **aiming
deterministic.** The same guidance the house-rule offered, fired *exactly* at the decision point, every
time.

## Mechanism

The runtime exposes named lifecycle events and a surface to register scripts against them. A hook is a
script bound to one event; the runtime invokes it at that moment and reads its result. A **blocking**
hook returns a veto and the action is denied. A **guidance** hook returns text that is re-injected into
the agent's context, aiming the next decision without compelling it. The event fires regardless of the
operator's state of mind — that is the whole point — so the two design constraints are: keep the check
cheap (it runs on *every* occurrence of the event), and make a guidance hook fail-open (a crash must not
wedge the loop; reserve fail-closed for the deliberate blocking case).

## Prerequisites

- **A runtime that exposes lifecycle events** plus a registration surface — without the seam there is
  nothing to hook.
- **A cheap check** — the hook fires on every occurrence of its event; an expensive one stalls the loop
  and creates pressure to disable it.
- **Fail-open for guidance hooks** — a bug in the hook must not brick the session; only the deliberate
  block is fail-closed.
- **A named, recurring omission** — reach for a hook once a soft reflex has demonstrably failed to hold,
  not on first sight; a hook manufactured for a one-off is pure overhead.

## Consequences & costs

- **It fires on every event, not only when needed.** A turn-stop hook runs at *every* stop, including
  the ones where nothing was owed; the check must stay cheap or the tax is constant and resented.
- **A guidance hook can be ignored.** Its payload is soft — the agent may read the re-injected text and
  proceed anyway. It aims deterministically; it does not compel. Only the blocking variant compels.
- **A buggy hook is a loop-level outage.** A blocking hook that misfires, or a guidance hook that
  crashes without fail-open, stalls the whole session — the blast radius is the loop, not one commit.
- **It can nag.** A hook that fires on a state it misreads — "work still queued" when the operator is
  legitimately blocked on a decision — produces repeated false prompts, and a signal that cries wolf
  gets tuned out.

## Known uses

- A **turn-stop hook** that refuses to let the loop rest while ratified work remains and the worker pool
  is under its cap — *hard delivery of soft guidance*: it re-prompts, the agent decides.
- A **pre-compaction hook** that writes a hand-off before context is compacted, so in-flight state
  survives the summarization.
- A **session-start hook** that runs the session-start ritual — reading the unconsumed alert backlog —
  before the first action of a resumed or compacted session.
- A **before-a-tool-call guard**: the hard-block variant denies an edit outside the sanctioned worktree;
  a guidance variant surfaces unresolved alerts before a dispatch.

## Related mechanisms

- **Counterpart** — [pre-commit-hook](../gates-and-merge-train/pre-commit-hook.md): both are hooks, but
  that one fires on a *commit* and guards what gets **written**; this one fires on a *runtime lifecycle
  event* and guards what the loop **does**. The named axis is *commit-content* vs *runtime-loop*.
- **See also** — [cron-alerts-gate](cron-alerts-gate.md): a before-a-tool-call hook is one delivery
  surface for its "an unresolved high-severity alert blocks new work" rule — the gate supplies the
  state, the hook fires the check at the moment of action.
- **Layer** — it sits at the agent runtime, upstream of the commit → cron → merge-train → deploy
  staircase; it governs the operator *driving* that staircase, not the work flowing through it.
