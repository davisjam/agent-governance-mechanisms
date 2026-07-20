# Example runbook — drain an un-releasable mainline

*A worked runbook. Keep the shape: **problem statement** (universal) then **typed steps**. Swap the
illustrative commands for this repo's gate + tools.*

**Lifecycle:** L3 · manage-git-repo.

## Problem (universal)

The mainline can't ship: its deploy gate is red, and (the sharp case) the gate has **no baseline** — it
fails on the *total* set of findings, not a delta — so pre-existing findings block every deploy until the
whole set is cleared to zero. You need to drain the backlog to green without breaking in-flight work.

## Steps (typed)

- **[RUNNABLE] See the true gate.** Run the deploy-scope gate exactly as the deploy does (no baseline, the
  full set) so you're looking at what actually blocks shipping — not a friendlier local subset.
  `<your gate> --deploy-scope`
- **[JUDGMENT-AUTOMATABLE] Partition the findings before fixing.** A carried brief that reads the gate
  output and groups the findings into homogeneous batches (by rule, by subtree, by fix-shape), so parallel
  fixers get disjoint, low-conflict work. *Partition first; don't hand a mixed pile to one fixer.*
  Carried brief: *"Given this gate output, produce homogeneous fix-batches with disjoint file footprints,
  ordered by leverage; flag any that need judgment."*
- **[RUNNABLE] Dispatch the batches** as disjoint-footprint waves (so they land without conflicting), each
  fixing its batch to zero.
- **[JUDGMENT-IRREDUCIBLE] Surface the judgment findings** — a finding that's arguably a false positive, or
  that needs an architectural call, goes to the human, not an auto-fix.
- **[RUNNABLE] Re-run the true gate** until it's zero; only then is the mainline releasable again.

## Second-order note

New-baseline gates punish *pre-existing* debt, so the drain is all-or-nothing — landing a new red finding
mid-drain resets progress. Keep new work from adding findings while draining (land fixes, not features),
and don't register a still-red check into the gate.
