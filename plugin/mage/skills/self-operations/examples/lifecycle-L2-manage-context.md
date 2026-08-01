# Example lifecycle model — L2 · manage-context

*A worked lifecycle model. Keep the shape (purpose · healthy baseline · symptom classes · owned runbooks),
swap in this repo's tools. One repo's illustrative instantiation.*

## Purpose

The operator's own context window (and, secondarily, agents') is a finite resource that must be *managed*,
not just consumed. L2 covers banking in-flight state before compaction, reconstructing it after, and
keeping-going near the limit so compaction fires on activity rather than stranding you idle.

## Healthy baseline

- In-flight state (the plan, the queue, the open threads) is banked to a durable place a fresh session can
  read — not held only in the live window.
- After a compaction/restart, the operator can reconstruct what was in flight from a small, fixed set of
  queries.
- The pool isn't sitting idle near the context limit; the way out of a deep context is *forward* (keep
  dispatching), not rest.
- The *reconstructable* half of what's banked is **machine-generated from a queryable source-of-truth**
  (the queue, the epic/task state, the in-flight work) — not hand-retyped — so re-banking is a cheap diff
  of the narrative, not a rewrite.
- The banked state is re-banked **as it goes stale** (a bounded staleness window — say ~15 min of drift),
  not saved once at session-end: automated compaction fires without warning, so a save-at-the-end habit
  loses the delta.

## Symptom classes → resolving docs (Part B fills the doc column)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| Approaching compaction with unsaved in-flight state | *your* bank-before-compaction procedure (write the handoff + strategy) |
| Fresh / post-compaction session — must rebuild the picture | *your* session-start reconstruction (the fixed recovery queries) |
| Idle capacity while ratified work is queued near the limit | keep-going: refill slots so compaction fires on activity |
| The banked state has drifted from reality mid-session (a stale handoff / strategy) | *your* re-bank-the-delta step — regenerate the machine sections + diff the narrative, *before* it's needed |

## Owned runbooks

- **emit-the-handoff** — a tool that machine-generates the handoff's reconstructable sections (queue /
  epic / in-flight state) from the queryable source-of-truth, so banking is a narrative diff, not a hand
  rewrite. The machinery is what makes re-banking cheap enough to actually do often.
- **bank-before-compaction** — atomically write the handoff + strategy with fresh stamps.
- **re-bank-the-delta** — when the banked state is past its staleness window, re-bank *now*; don't wait
  for the compaction or interruption that won't announce itself first.
- **resume-post-compact** — read the handoff + run the reconstruction queries.
- **keep-going-near-compaction** — don't rest at high context; keep the pool full.

## Observability surface

The handoff/strategy artifacts + a fixed set of session-start queries that reconstruct in-flight work. If
the picture can't be rebuilt from what's banked, the *banking* is the gap — bank more, earlier. And if the
reconstructable sections are all hand-typed, *that* is the gap — generate them from the queryable source,
so re-banking stays cheap enough to keep current.
