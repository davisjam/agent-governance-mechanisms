# Example runbook — recover the fleet after a crash

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's tools.*

**Lifecycle:** L1 · manage-agents.

## Problem (universal)

A network outage or a host crash killed agents mid-flight. On restart the operator faces N worktrees in
unknown states — the moment of *most* ad-hoc judgment (each orphan is in an unknown state) and *least*
context (often a fresh session). Recover the fleet: for each orphan, decide land / tombstone / surface.

## Steps (typed)

- **[RUNNABLE] Enumerate the registered agents** from the authoritative registry — *not* a filesystem scan
  of worktree dirs (that races with any survivor still running).
  `<your registry query> --list-in-flight`
- **[RUNNABLE] Classify each orphan** by whether its commits reached the mainline:
  `<your reachability check> <branch>` → LANDABLE (un-landed real commits) · ALREADY-LANDED · EMPTY ·
  AMBIGUOUS (dirty tree / conflict).
- **[JUDGMENT-AUTOMATABLE] Draft the disposition table** — a carried brief that reads the classification and
  proposes, per orphan, `land | tombstone | surface`, with the reason. *Report first; never auto-destroy.*
  Carried brief: *"Given this registry + reachability output, produce a disposition table (orphan-id →
  disposition → action → reason); mark anything dirty/conflicting as SURFACE."*
- **[RUNNABLE] Act on the unambiguous dispositions:** land the LANDABLE (cherry-pick, or finalize-then-land
  if it died before its final commit), tombstone + clean the ALREADY-LANDED / EMPTY.
  `<your cherry-pick tool> apply <commit>` · `<your tombstone tool> --disposition clean`
- **[JUDGMENT-IRREDUCIBLE] Surface the AMBIGUOUS ones** to the human — a dirty tree or a mid-rebase conflict
  is a judgment call the driver must not guess.
- **[RUNNABLE] Reconcile state** after landing — refresh the Epic/backlog record so it matches the mainline.

## Second-order note

Make the driver **idempotent** (re-runnable after a partial recovery — it re-reads current state each run)
and honor the **live-marker guard** (never tombstone an agent whose marker is live; a crash-survivor may
still be running). REPORT-then-ACT — the destructive steps run only on an explicit `--apply`.
