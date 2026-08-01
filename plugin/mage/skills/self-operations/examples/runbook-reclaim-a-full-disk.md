# Example runbook — reclaim a full disk

*A worked runbook. Keep the shape: **problem statement** (universal) then **typed steps**. Swap the
illustrative commands for this repo's host + tools.*

**Lifecycle:** L5 · manage-dev-env.

## Problem (universal)

Dispatch (or a build) is refused on a low-disk floor — the host's dev machine has run out of headroom, so
new heavy work can't start. Reclaim disk *before* pruning anything valuable, because the fastest reclaim is
often the least destructive.

## Steps (typed)

- **[RUNNABLE] Confirm the pressure and where it is.** Read the host's disk on the sites that actually fill
  (the container-runtime VM, the build cache, the worktree/log dirs).
  `<your host-disk check>` · `du -sh <the 2–3 sites that grow>`
- **[RUNNABLE] Reclaim the cheap way first.** For a container-runtime VM, the un-TRIMmed VM is the usual
  culprit — reclaim freed-but-unTRIMmed blocks before deleting real data:
  `<vm> ssh -- sudo fstrim -av`   *(this alone often reclaims tens of GiB; do it FIRST)*
- **[JUDGMENT-AUTOMATABLE] If TRIM isn't enough, decide what to prune** — a carried brief that ranks the
  reclaimable sets (stale worktrees already landed, old logs, build caches) by size × safety and proposes a
  prune order. *Report the plan; don't auto-delete outside scratch.*
- **[RUNNABLE] Prune the ratified sets** — stale/landed worktrees via the safe cleanup tool (dry-run then
  apply), rotated logs, expendable caches.
- **[JUDGMENT-IRREDUCIBLE] If still low after safe reclaim,** surface to the human — resizing the VM or
  deleting anything outside the repo/scratch is a human decision.
- **[RUNNABLE] Re-dispatch** the work that was refused.

## Second-order note

Order matters: **TRIM/reclaim before prune** (cheap + non-destructive first). Never delete a path you did
not create or whose contents contradict how it was described; anything outside the repo/scratch gets an
explicit ask.
