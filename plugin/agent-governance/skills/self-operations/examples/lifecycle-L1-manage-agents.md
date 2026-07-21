# Example lifecycle model — L1 · manage-agents

*A worked lifecycle model. Adapt it: keep the shape (purpose · healthy baseline · symptom classes · owned
runbooks), swap in this repo's tools and docs. This is one repo's illustrative instantiation.*

## Purpose

The fleet is the resource that *produces* work through sub-agents. L1 manages its whole arc:
**dispatch → monitor → land → tombstone → recover**. Everything that launches, watches, lands, or reclaims
an agent lives here.

## Healthy baseline

State yours concretely — the operator should be able to check it in one glance:

- Agents in flight ≤ the pool cap; no idle slots while ratified work is queued.
- Every in-flight agent has a live record in the authoritative registry.
- Landed work is cherry-picked to the mainline and its worktree cleaned up (tombstoned); no orphaned
  worktrees accreting.
- No agent has committed onto the mainline branch instead of its own worktree branch.
- Every dispatch clears a **brief validator** before launch — the structural markers present, *and* the
  content checks gated by the brief's declared genre so the lint doesn't false-fire and get tuned out — so
  a malformed brief *can't* launch (the dispatch path calls the validator; there is no un-validated door).

## Symptom classes → resolving docs (Part B fills the doc column for your repo)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| An agent died mid-flight (crash / watchdog kill); its worktree is orphaned with un-landed work | *your* recover-the-fleet runbook (see `runbook-recover-the-fleet.md`) |
| Dispatch refused on a resource floor (disk / load) | *your* dev-env reclaim procedure (→ L5) |
| An agent committed to the mainline instead of its worktree branch | *your* CWD-drift recovery (rebase the misplaced commits back) |
| A worktree needs reclaiming but must not touch a live agent | *your* tombstone/clean procedure with a live-marker guard |

## Owned runbooks

- **recover-the-fleet** — reconstruct fleet state after a crash and resolve each orphan (land / tombstone /
  surface). See `runbook-recover-the-fleet.md`.
- **dispatch-a-wave** — compose N disjoint-footprint briefs and launch them (mostly runnable already).
- **keep-the-pool-hot** — refill a freed slot in the same turn from the backlog.

## Observability surface (where you look to see L1's health)

The authoritative "who's in flight" record (a registry, not a filesystem scan), plus the fleet's
lifecycle event stream (dispatch / land / tombstone). If you can't tell live from stale from the signal you
have, *that gap is the first finding* — add the record before you act.
