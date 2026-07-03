# Staged deploy gates (canary → smoke → promote)

**Intent** — A deploy pipeline that escalates **canary → smoke → promote**, blocking promotion to
production until each cheaper stage passes on a traffic-free revision — so a bad build is caught before
users see it, not after.

| | |
|---|---|
| Summary | Canary → smoke → promote; gate before users see it. |
| Target | Agent · **Gates & merge-train** |
| Form | `quality-gate` |
| Enforcement | **Hard** (deterministic) · *blocking* — promotion is refused until the smoke stage passes |

## Motivation — the failure it kills

Shipping a build straight to production means a regression lands on users; the failure *is* the
incident. This is standard practice everywhere, but it is load-bearing at agentic velocity precisely
because deploys are frequent and agent-initiated — the more often you ship, the more often an
un-gated bad build reaches users.

## Why it's not just "deploy and roll back if it breaks"

Rollback is *reactive and user-visible*: by the time you roll back, users have already hit the break.
Staged gates are *proactive* — a **canary** revision is deployed taking **no production traffic**,
**smoke**-tested against its own URL, and **promoted** only on green. The distinction is
*gate-before-users* versus *detect-after-users*. A pre-launch rule pushes the gate even earlier: don't even
*launch* a deploy that will predictably fail — confirm lints are green, no known flaky class is live,
and `--changed-since main` is green *before* paying for build minutes. (Being a standard practice, its
"why not" is thinner than the novel controls' — the value is defense-in-depth, not novelty.)

## Mechanism

Version bump → build → tag a canary revision (traffic-free) → smoke against the canary URL → promote
to production → GC old revisions. The pre-launch predicate gates the whole thing on
cheaper signals so a doomed deploy is never started. Heartbeats emit liveness during the long phases.

## Prerequisites

- **Canary capability** — the ability to deploy a revision that takes no production traffic.
- **A smoke suite** that meaningfully exercises the canary URL (real dependencies, not stubs).
- **Promotion + rollback primitives** and revision GC.
- **A pre-launch green signal** (lints / changed-since-main / flaky-class check) as the pre-launch predicate.

## Consequences & costs

- **Staging costs real build minutes.** The gate is not free; the pre-launch predicate exists to avoid
  spending them on a deploy that was never going to pass.
- **Smoke ≠ full coverage.** A thin smoke suite lets real breaks through the gate — the canary is only
  as good as what the smoke actually checks.
- **The gate infrastructure itself can drift.** Validating via the deploy pipeline assumes the pipeline
  is sound; a drifted canary/smoke path gives false confidence (don't validate via untested infra).
- **Deploy latency.** Each stage adds wall-clock before users get the change.

## Known uses

- The staged deploy driver (canary tag → smoke → promote → revision GC).
- The pre-deploy predicate (lints green · no flaky class · changed-since-main green).
- Per-phase deploy heartbeats (see Lifecycle & observability).

## Related controls

- **Layer** — the *last* stair of the staircase, downstream of [merge-train-mis-batching](merge-train-mis-batching.md);
  the most expensive gate, reached only after the cheap ones passed.
- *See also (complement)* — the product-target per-pass validators and conformance checks run *inside*
  the shipped artifact; these staged gates wrap the deploy *of* that artifact.
