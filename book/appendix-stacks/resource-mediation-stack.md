*A flagship deep-dive: the resource-mediation stack, walked part by part. Dozens of agent worktrees share
one machine. Left ungoverned they saturate its I/O, thrash its cores, and drive it into swap. This stack
declares which work must be serialized and which may run in parallel, holds each declaration with a
host-level mediator, and governs the whole with a live pressure signal.*

## The goal

**Share one machine among dozens of concurrent worktrees without letting them trample each other or drown
the host.** Two kinds of contention need two kinds of answer: a resource that cannot be shared takes a
single-writer lock; a resource that can be shared takes a counting one, up to the host's capacity. And
because a correctly-shared fleet can still overload the box, a live pressure signal sits above both mediators
— refusing new heavy work before it starts and shedding running work when the machine spikes.

<!-- label: resource-mediation-stack -->
<!-- figure: assets/resource-mediation-stack.svg | The resource-mediation stack in one picture. Four parts run left to right. DECLARE (violet) is the typed registry of concurrency contracts — what is serialized, what is single-writer. SERIALIZE (blue) is the host-level flock that admits one run of the heaviest tool at a time (N=1). SEMAPHORE (green) is the counting lock that admits up to eight concurrent runs of the adjacent heavy tools (M=8). SHED (accent) governs a saturable resource with a live pressure signal at two layers — an admission gate that refuses heavy work before dispatch and an execution shed that stops running work on a spike. The contract says how many; the mediators hold that many; the pressure gate decides whether they run at all. -->

## How the parts interlock

The stack runs from a declaration to an adaptive gate. **DECLARE** turns "how many at once" from folklore
into typed data. **SERIALIZE** enforces the strictest contract — the N=1 monopoly — with an exclusive flock.
**SEMAPHORE** enforces the contracts that permit bounded sharing — the M>1 tier — with a counting lock; same
registry, different cardinality. **SHED** closes the stack: where the mediators bound *how many* run, the
pressure gate bounds *whether they run at all* given the host's live state. Read the parts in that order;
each seam names what the part before it hands over.

## The parts

### 1. DECLARE — the concurrency contracts

- **Part** — role:concurrency-contracts
- **Role in the stack** — Typed registries of the system's concurrency contracts: which subprocess
  invocations are serialized, and which state-mutating functions are single-writer.
- **Failure it retires** — Who may run a thing, and how many at once, lives as folklore in scattered wrapper
  scripts; nothing declares it, so a new call site oversubscribes a resource no one knew was contended.
- **Mechanism** — A typed registry names each concurrency contract — this invocation is serialized by that
  mediator, this mutation is single-writer — so "how many at once" is declared data a check can enforce, not
  a convention.
- **The seam** — Opens the stack. It is the model side the mediators enforce: the serializer and the
  semaphore read these declarations to know what to serialize and to what degree, and a drift gate can hold
  each mediator to its declared contract.
- **Limits / durability** — Durable — a typed contract registry is model-independent and outlives any one
  mediator. Its cost is authoring the contracts; it fails only where a contended invocation is left
  undeclared, which the mediators' own coverage check surfaces.

### 2. SERIALIZE — the single-writer flock

- **Part** — role:test-serializer
- **Role in the stack** — A host-level wrapper that serializes the heaviest tool to a *single* writer via an
  exclusive flock.
- **Failure it retires** — Two worktrees run the heavy test suite at once on one machine; they saturate I/O
  and interfere with each other's runs, and both come back slow and flaky.
- **Mechanism** — An exclusive flock admits one run of the tool at a time (N=1); the second caller waits, so
  concurrent worktrees serialize on the contended resource instead of colliding on it.
- **The seam** — Enforces the strictest DECLARE contract — the N=1 monopoly. It sits beside the semaphore:
  the resource that cannot share takes the flock, the resources that can share take the counting lock, and
  both read their cardinality from the same contract registry.
- **Limits / durability** — Durable — an OS flock is a deterministic correctness net regardless of agent
  count. Its cost is the serialization latency on the monopoly resource; it fails only if a caller bypasses
  the wrapper, which a mediator-enforcement guard refuses.

### 3. SEMAPHORE — the counting lock

- **Part** — role:build-serializer
- **Role in the stack** — A host-level counting semaphore (M=8) over the adjacent heavy-compute tools, so
  worktrees get parallelism up to the machine's capacity without oversubscribing it.
- **Failure it retires** — Heavy builds and type-checks either run one-at-a-time (wasting a capable machine)
  or all-at-once (thrashing it); neither matches the host's actual capacity.
- **Mechanism** — A counting semaphore admits up to M concurrent runs of the adjacent heavy tools; the
  M+1-th waits, so parallelism rises to capacity and stops there.
- **The seam** — Enforces the DECLARE contracts that permit bounded sharing — the M>1 tier beside the
  serializer's N=1 monopoly. Same registry, different cardinality: the contract says how many, the semaphore
  holds that many.
- **Limits / durability** — Durable — a byte-range semaphore is deterministic and model-independent. Its
  cost is a tuned M per machine; it degrades gracefully — too low wastes capacity, too high thrashes — and
  the pressure gate above it catches the thrash.

### 4. SHED — the adaptive pressure gate

- **Part** — role:resource-pressure-gating
- **Role in the stack** — Govern a saturable host resource with a live pressure signal read at two layers:
  an admission gate that refuses heavy work before dispatch, and an execution shed that stops running work
  when pressure spikes.
- **Failure it retires** — Even a correctly-serialized fleet can drive the host into swap: work admitted
  while the machine was healthy keeps running as pressure climbs, and the box wedges under its own load.
- **Mechanism** — One live pressure signal drives two layers — refuse or defer heavy work before it is
  dispatched, and shed heavy work already running when pressure spikes — and the same signal is callable for
  the operator's own judgment.
- **The seam** — Closes the stack. Where DECLARE, SERIALIZE, and SEMAPHORE bound *how many* run, this bounds
  *whether they should run at all* given the host's live state — the admission-and-shedding layer over the
  fixed-cardinality mediators beneath it.
- **Limits / durability** — Durable — a live-signal gate adapts where a fixed cap cannot, and it is
  model-independent. Its cost is a reliable pressure signal; it fails if the signal lags the real pressure,
  bounded by how directly it reads the saturating resource.
