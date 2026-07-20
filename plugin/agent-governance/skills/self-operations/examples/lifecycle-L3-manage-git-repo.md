# Example lifecycle model — L3 · manage-git-repo

*A worked lifecycle model. Keep the shape; swap in this repo's tools. One repo's illustrative instantiation.*

## Purpose

The git substrate is the resource that gets agent work *onto the mainline*. L3 covers landing ready
worktrees, cherry-picking/merging, tombstoning landed worktrees, branch hygiene, and recovering a mainline
that has become un-releasable.

## Healthy baseline

- Ready worktrees land onto the mainline promptly; the mainline stays **releasable** (its deploy gate is
  green).
- Landed worktrees are tombstoned and cleaned; stale branches are reaped, their tips preserved first.
- No wrong or half-landed commit sits on the mainline; undo is by *revert*, never a history rewrite.

## Symptom classes → resolving docs (Part B fills the doc column)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| A ready worktree won't cherry-pick / land onto the mainline | *your* canonical cherry-pick tool (never a bare `git cherry-pick`); on conflict, quit not abort |
| The mainline is un-releasable — the deploy gate is red with no baseline | *your* drain-to-green procedure (see `runbook-drain-unreleasable-mainline.md`) |
| A landed commit is wrong and must be undone | `git revert <sha>` — never `git reset` on a shared mainline |
| Stale worktrees have accreted | *your* bulk cleanup (dry-run then apply; preserve tips) |

## Owned runbooks

- **land-ready-worktrees** — cherry-pick / merge a ready worktree onto the mainline.
- **tombstone-worktrees** — tombstone + clean a landed/abandoned worktree (with a live-marker guard).
- **recover-un-releasable-mainline** — drain the deploy-gate backlog to green (see the runbook).

## Observability surface

`git reflog` + a patch-id reachability check (did the worktree's commits actually reach the mainline?), and
the deploy gate's own output for "is the mainline releasable right now?"
