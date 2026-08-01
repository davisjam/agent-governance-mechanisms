# Example lifecycle model — L6 · govern-your-own-loop

*A worked lifecycle model. Keep the shape (purpose · healthy baseline · symptom classes · owned runbooks),
swap in this repo's tools. One repo's illustrative instantiation.*

## Purpose

The operator's own decision loop is a substrate you manage too. Some judgments you *mean* to make every
session — "did this failure recur, so should I harden it?", "does this lesson belong in durable memory or
in a runbook?" — are exactly the ones thin attention skips when they matter most. L6 covers **interposing
hooks on your own loop**: turning an ambient judgment you keep meaning to make into a deterministic nudge
at the moment it is due, biased hard toward silence so it aims without nagging. It is the seam where
*operate* hands a recurring break to *harden* (partner with self-governance).

## Healthy baseline

- An ambient operator judgment that keeps getting skipped is backed by a hook that fires the reflex at its
  decision point — not left to memory-under-load.
- Each such hook is **soft and fail-open** (it aims, never bricks the loop), fires **at most once per long
  window**, and carries a **kill switch**.
- Each hook is **telemetered** — you can watch it fire and correlate its firings against the thing it was
  meant to provoke, so a dead or over-firing hook is visible rather than silent (the measured leash).

## Symptom classes → resolving docs (Part B fills the doc column)

Two example hooks — illustrations of the pattern, not a fixed set; adapt them to your own recurring
skipped-judgments:

| Symptom class (what you observe) | Resolving hook (yours) |
|---|---|
| A failure class recurs across the session but you keep re-patching the instance, never converting the *class* into a control | a **turn-end reflection nudge** — at most once per window, "did the same failure recur ≥2×? consider handing the class to your hardening discipline" (→ self-governance) |
| A durable lesson is about to be written to the wrong store — stashed as a one-off memory when it belongs in a runbook/playbook, or the reverse | a **pre-write routing nudge** on the memory file — "a true contextual one-off, or should this update an associated runbook/playbook/pointer instead?" |

## Owned runbooks

- **add-a-loop-hook** — name the recurring skipped-judgment; write a fail-open, kill-switched,
  once-per-window hook that fires the reflex at its decision point; bias the payload toward silence.
- **put-the-hook-on-a-leash** — ship per-firing telemetry + a yield query, and set a written pull
  condition (it over-fires, or shows near-zero yield across sessions → pull it).

## Observability surface

Each loop-hook's own firing log plus a yield query that correlates its firings against the action they
were meant to provoke — a reflection nudge against a real hardening invocation, a routing nudge against a
lesson landing in the right store. A soft hook you cannot watch fire is indistinguishable from a dead one,
so the telemetry is what tells *working quietly* from *silently dead*, and the yield is the keep-or-pull
signal.
