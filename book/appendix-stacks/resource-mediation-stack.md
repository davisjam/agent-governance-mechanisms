*A two-page synthesis of the resource-mediation stack. Four patterns share one machine among dozens of
concurrent agent worktrees without letting them trample each other or drown the host: declare what must be
serialized, hold each declaration with a host-level mediator, and govern the whole with a live pressure
signal.*

## The capability

**Run dozens of agent worktrees on one box at the right degree of parallelism — no collisions, no thrash, no
swap.** The stack makes one capability: *manage work, state, and resources*. It declares which work must be
serialized and which may run in parallel, holds each declaration with a host-level lock, and puts a live
pressure signal over the whole that refuses new heavy work before it starts and sheds running work when the
host spikes. The contract says how many; the mediators hold that many; the pressure gate decides whether they
run at all.

## Failure classes it covers

- **The undeclared contention.** Who may run a thing, and how many at once, lives as folklore in scattered
  wrapper scripts; a new call site oversubscribes a resource no one knew was contended.
- **The colliding monopoly.** Two worktrees run the heavy test suite at once on one machine; they saturate
  I/O and interfere, and both come back slow and flaky.
- **The mismatched cap.** Heavy builds and type-checks run either one-at-a-time — wasting a capable machine —
  or all-at-once, thrashing it; neither matches the host's actual capacity.
- **The self-inflicted swap.** Even a correctly-serialized fleet drives the host into swap: work admitted
  while the machine was healthy keeps running as pressure climbs, and the box wedges under its own load.

## Composition

<!-- label: resource-mediation-stack -->
<!-- figure: assets/resource-mediation-stack.svg | The resource-mediation stack in one picture. Four parts run left to right. DECLARE (violet) is the typed registry of concurrency contracts — what is serialized, what is single-writer. SERIALIZE (blue) is the host-level flock that admits one run of the heaviest tool at a time (N=1). SEMAPHORE (green) is the counting lock that admits up to eight concurrent runs of the adjacent heavy tools (M=8). SHED (accent) governs a saturable resource with a live pressure signal at two layers — an admission gate that refuses heavy work before dispatch and an execution shed that stops running work on a spike. The contract says how many; the mediators hold that many; the pressure gate decides whether they run at all. -->

One part declares the contracts; two enforce them at fixed cardinality — a strict monopoly and a bounded
pool; one adds a live signal over both.

## The constituent patterns

- **DECLARE — role:concurrency-contracts.** Typed registries of the system's concurrency contracts: which
  subprocess invocations are serialized, which state-mutating functions are single-writer. It is the model
  side the mediators enforce — "how many at once" becomes declared data a check can hold, not a convention.
- **SERIALIZE — role:test-serializer.** A host-level wrapper that serializes the heaviest tool to a single
  writer via an exclusive flock (N=1); the second caller waits. An OS flock is a deterministic correctness
  net regardless of agent count.
- **SEMAPHORE — role:build-serializer.** A host-level counting semaphore (M=8) over the adjacent
  heavy-compute tools, so worktrees get parallelism up to the machine's capacity without oversubscribing it.
  Same registry as the serializer, different cardinality.
- **SHED — role:resource-pressure-gating.** Govern a saturable host resource with a live pressure signal read
  at two layers: an admission gate that refuses heavy work before dispatch, and an execution shed that stops
  running work when pressure spikes. Where the mediators bound *how many* run, this bounds *whether they
  should run at all* given the host's live state.

## A DocAble example, end to end

DocAble's development runs six to eight agent worktrees on one shared build machine. **DECLARE** names each
contended invocation in a typed registry — the C# test runner is serialized, the build and type-check tools
share up to a fixed count, this in-memory mutation is single-writer. **SERIALIZE** holds the strictest of
those: the heavy test suite takes an exclusive flock, so when two agents reach it at once the second waits
instead of colliding on I/O — both runs come back fast and clean rather than slow and flaky. **SEMAPHORE**
holds the looser contracts: up to eight concurrent builds and type-checks run, and the ninth waits, so the
machine runs at capacity and stops there. Over all of it, **SHED** watches host pressure — when memory
climbs toward swap it refuses to admit the next heavy job, and if a running wave spikes the box it sheds
work already in flight, so a correctly-serialized fleet still cannot drive the host into the ground.

## Tradeoffs and adoption order

1. **DECLARE first.** Without the contract registry the mediators do not know what to serialize or to what
   degree. Its cost is authoring the contracts; an undeclared contended invocation is the gap, which the
   mediators' own coverage check surfaces.
2. **SERIALIZE and SEMAPHORE together.** Same registry, two cardinalities — the resource that cannot share
   takes the flock (N=1), the ones that can share take the counting lock (M>1). The serializer costs
   latency on the monopoly resource; the semaphore needs a tuned M per machine and degrades gracefully.
3. **SHED last, and it earns its place under load.** A live-signal gate adapts where a fixed cap cannot. It
   fails only if the signal lags the real pressure, so read the saturating resource as directly as possible.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
The stack pairs with the [observe → react loop](appendix-d-observe-react-stack.html) (the pressure signal
rides the same observability surface) and the
[context-management stack](appendix-d-context-management-stack.html) (both share one machine among many
agents). The full 83-mechanism catalogue is online in the web edition.
