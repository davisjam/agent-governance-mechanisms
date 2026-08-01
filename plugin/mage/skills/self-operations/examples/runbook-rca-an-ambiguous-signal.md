# Example runbook — RCA an ambiguous signal

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's tools.*

**Lifecycle:** (cross-cuts every lifecycle) — the observability-first RCA spine.

## Problem (universal)

Something failed, and the signal you have can't pin the cause — the log says "failed" but not *why*, or the
symptom is consistent with three different faults. The reflex is to hypothesize and go hunting. Resist it:
when the signal can't pin the cause, the **missing signal is itself the first finding**. Assess observability
first, instrument for the decision the fix must drive, and reproduce at the cheapest tier — no goose chases.

## Steps (typed)

- **[RUNNABLE] State the symptom precisely — what was *observed*, not the suspected cause.** Pull the reliably
  *distinct* signal (the one that means exactly one thing), not a plausible-looking one that's consistent
  with several faults.
  `<your log/metric read>` — capture the exact failing observation.
- **[JUDGMENT-IRREDUCIBLE] Assess observability first: can you pin this with what you have?** If not — *stop
  hypothesizing.* The absence of the pinning signal is the **first finding**. Do not proceed to guess a cause
  you cannot yet distinguish from its neighbours.
- **[JUDGMENT-AUTOMATABLE] Add the signal — and measure one level *deeper*.** Instrument for the *decision*
  the reading must drive, one level *below* the surface symptom, so the reading points at the fix rather than
  merely reporting the fault. A reading that only reports is a level too shallow the moment its job is to
  change something.
  Carried brief: *"Given this symptom, name the one distinct signal that would pin the cause AND drive the
  fix decision; specify where to instrument it (one level below the surface symptom) and what value would
  point at which fix."*
- **[RUNNABLE] Reproduce at the cheapest tier.** Reproduce locally before anything remote — a failure to
  reproduce locally *is* a clue (environment/config drift). Never redeploy-to-diagnose.
  `<your local repro of the instrumented case>`
- **[JUDGMENT-IRREDUCIBLE] Ground the hypothesis in the new evidence — only once the signal exists.** Root
  cause is judgment-heavy; give it your strongest model, reasoning from the reading, not from the guess.
- **[RUNNABLE] Fix to the stable point, not the failing seed** — fix the *class* so the fix holds for every
  input the class admits, not just the one case that failed.

## Second-order note

An un-pinnable diagnosis is a gap in the signal's *presence*; an un-actionable reading is a gap in its
*depth* — treat both as findings about the observability, not just the bug. If the failure recurred, the
control you add is *the signal you just wished you'd had*: convert the RCA into observability the next
occurrence pins itself with (hand it to the partner self-governance skill — governance is design, not an
inline hack). The RCA's real output is often the missing signal, not the one fix.
