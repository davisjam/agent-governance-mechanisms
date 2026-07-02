# Merge-train MIS batching

**Intent** — A merge-train that lands the largest set of *non-conflicting* agent worktrees per tick by
computing a **Maximum Independent Set** over their file footprints, so many agents' work merges in one
conflict-free pass instead of thrashing sequentially.

| | |
|---|---|
| Target | Agent · **Gates & merge-train** |
| Form | `quality-gate` |
| Novelty | notable |
| Real artifact | `merge_train.py` |
| Governing rule(s) | **#50** (MIS-aware composition for cron throughput — dispatch disjoint-footprint waves) |
| Enforcement | **Hard** (deterministic) — the batch is selected by a graph predicate, not by hope-and-retry |
| Summary | Land non-conflicting worktrees together via a maximum independent set. |

## Motivation — the failure it kills

With 6–8 agents committing concurrently, a naïve *sequential* merge serializes all of them and
conflicts thrash: each merge risks colliding with the last, and the throughput of the whole fleet
collapses toward one-at-a-time. Hot-spot files that many agents touch (the merge tool itself,
`CLAUDE.md`, shared config) become bottlenecks that stall everything behind them. The failure recurs
every merge tick and worsens as the fleet grows — more agents, more collisions.

## Why it's not just "merge them one by one" (or "let git sort the conflicts")

Sequential merge is O(n) wall-clock and conflict-prone; "let git sort it" turns every tick into a
manual conflict-resolution session. MIS batching instead builds a **conflict graph** — worktrees are
nodes, a shared file is an edge — and computes the largest set of worktrees with **disjoint file
footprints**, landing that set together. The batch is **non-conflicting by construction**: because no
two members touch the same file, they cannot collide. The distinction is *a conflict-free batch proven
by graph independence* versus *a sequence that hopes for the best and retries on failure*.

## Mechanism

Each tick: build the conflict graph from per-worktree file footprints, compute an independent set,
land that set this tick, defer the rest to the next. Throughput is maximized upstream, at dispatch:
rule #50 says to launch waves with **disjoint footprints** so the MIS is large — and warns that
hot-spot files (touched by many agents) cap the MIS to size 1 no matter how many agents are ready.
Landed commits are checked by patch-id / ancestry reachability.

## Prerequisites

- **Known per-worktree file footprints** — you must be able to say which files each worktree changed.
- **A conflict predicate** (shared file ⇒ edge) and a **(greedy) MIS routine**.
- **Reachability / patch-id checks** so a "landed" claim is verifiable.
- **Footprint discipline at dispatch** — the orchestrator has to *plan* disjoint waves for the MIS to
  pay off; the control pushes work upstream into scheduling.

## Consequences & costs

- **MIS is approximate.** The batch is a greedy independent set, not provably maximum every tick — good
  enough, but not optimal.
- **Hot-spot files hard-cap throughput.** If eight agents all touch one file, the MIS is 1 regardless
  of the algorithm — the win depends entirely on dispatch-side footprint disjointness (rule #50).
- **It moves complexity upstream.** The orchestrator must now think about footprints when composing
  waves; a mis-declared footprint can let a real conflict slip into a batch.

## Known uses

- `merge_train.py` — the conflict-graph MIS batcher.
- Rule #50's 8-pool disjoint-footprint dispatch recipe.
- Patch-id / ancestry reachability verification of landed commits.

## Related controls

- **Layer** — the cron → merge-train stair, downstream of [pre-commit-hook](pre-commit-hook.md) /
  [sentinel-first-commit](sentinel-first-commit.md) and upstream of [staged-deploy-gates](staged-deploy-gates.md).
- **Consumer** — reads the agent-registry (Lifecycle & observability family) to know which worktrees
  are ready to land.
- **Enabler** — disjoint-footprint dispatch discipline (rule #50) is what makes the batch large; the
  algorithm alone cannot beat a hot-spot file.
