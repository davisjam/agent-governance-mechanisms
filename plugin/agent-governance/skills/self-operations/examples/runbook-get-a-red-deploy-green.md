# Example runbook — get a red deploy green

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's gate + tools.*

**Lifecycle:** L4 · manage-deploy.

## Problem (universal)

A deploy failed or is blocked: a gate went red. You can't just re-run it — a green result you don't
understand is worse than a red one. Read the gate output, classify the failure class, fix-or-revert to the
class, and re-gate — never redeploy-to-diagnose.

## Steps (typed)

- **[RUNNABLE] Read the actual gate output** — the failing phase and its message, exactly as the deploy ran
  it (the *same* scope the deploy uses, not a friendlier local subset). The first job is to *see* what
  blocked shipping, not to guess.
  `<your deploy log>` · `<your gate> --as-deploy-runs-it`
- **[JUDGMENT-AUTOMATABLE] Classify the failure class.** A carried brief that reads the gate output and bins
  the failure — *code defect* (a real regression in this change), *flaky* (non-deterministic, unrelated to
  the change), *infra* (build host / registry / network), or *pre-existing* (the gate was already red before
  this change). The class decides the fix, so classify before touching anything.
  Carried brief: *"Given this gate output, classify the failure (code-defect / flaky / infra / pre-existing),
  cite the evidence for the call, and name the smallest fix-or-revert that addresses the CLASS."*
- **[RUNNABLE] Fix-or-revert to the class.** A code defect → fix the class and re-gate (or, if a prod fire,
  revert the offending change rather than ship HEAD). A flaky → quarantine/kill the flake, don't paper over
  it. Infra → retry only after confirming the infra recovered. Pre-existing → drain it as its own backlog,
  not under deploy pressure.
  `<your revert>` · `<your fix + re-gate>`
- **[RUNNABLE] Reproduce at the cheapest tier before any re-deploy.** For a deterministic failure, reproduce
  locally first — a failure to reproduce locally *is* a clue (environment/config drift). Never redeploy just
  to see the failure again.
  `<your local run of the failing case>`
- **[JUDGMENT-IRREDUCIBLE] Surface the ambiguous call.** "Is this a real regression or a false positive?"
  and "revert vs forward-fix under a live prod fire" are human decisions — surface them, don't guess.
- **[RUNNABLE] Re-gate and confirm green** — run the same gate at the same scope; only a clean pass is
  green. Then promote.

## Second-order note

Never ship HEAD to fix production — hotfix from the deployed revision, not the tip, or you carry unrelated
in-flight changes into the fire. And if the *same* deploy failure class recurs across sessions, it has
graduated from an incident to a pattern: hand it to your hardening discipline (the partner self-governance
skill) to convert into a control — a pre-deploy check that catches the class before the gate does.
