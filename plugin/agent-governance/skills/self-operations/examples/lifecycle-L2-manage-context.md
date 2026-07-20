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

## Symptom classes → resolving docs (Part B fills the doc column)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| Approaching compaction with unsaved in-flight state | *your* bank-before-compaction procedure (write the handoff + strategy) |
| Fresh / post-compaction session — must rebuild the picture | *your* session-start reconstruction (the fixed recovery queries) |
| Idle capacity while ratified work is queued near the limit | keep-going: refill slots so compaction fires on activity |

## Owned runbooks

- **bank-before-compaction** — atomically write the handoff + strategy with fresh stamps.
- **resume-post-compact** — read the handoff + run the reconstruction queries.
- **keep-going-near-compaction** — don't rest at high context; keep the pool full.

## Observability surface

The handoff/strategy artifacts + a fixed set of session-start queries that reconstruct in-flight work. If
the picture can't be rebuilt from what's banked, the *banking* is the gap — bank more, earlier.
