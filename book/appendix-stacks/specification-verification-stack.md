*A flagship deep-dive: the specification + verification stack, walked part by part. A concurrent system is
correct only against a spec you can name and check. This stack writes the spec as composed state machines,
derives every obligation from it, and discharges each at graduated rigor — an exhaustive proof where the
invariant is hairy, a deterministic lint where it is linear. This page folds in what used to be the
separate semantic-lint stack, as the deterministic-verification tier.*

## The goal

**Turn a concurrent behavioral spec into checked assurance.** Model the lifecycle as composed state
machines, derive from it every test obligation, discharge each obligation at the rigor its shape demands,
then map coverage back onto the model so an unexercised invariant is a visible gap, not a guess. Two rigor
tiers do the discharging: an exhaustive proof for a safety or liveness invariant, a deterministic lint for
a linear one — and a discipline that keeps each check aimed at the level its property actually lives at.

<!-- label: specification-verification-stack -->
<!-- figure: assets/specification-verification-stack.svg | The specification + verification stack in one picture. Six parts run left to right. The spec (violet): SPEC models the lifecycle as composed state machines and names the cross-machine invariants; CENSUS derives every obligation owed. The rigor tiers: PROVE (green) discharges the hairy invariants with an exhaustive check routed by each invariant's temporal form; LINT (blue) discharges the linear ones with a blocking semantic check at commit, and LEVEL (blue) aims each check at the granularity where its property first becomes legible. COVER (accent) projects coverage back onto the model's nodes, so a verified-in-principle invariant with no live test is a visible gap. -->

## How the parts interlock

The chain runs from a named spec to a checked one. **SPEC** models the concurrent lifecycle and names the
predicates that must hold across it. **CENSUS** reads those invariants and seams and derives the obligation
set — what is *owed* a test. **PROVE** discharges the hairy invariants: an exhaustive state-space or
temporal check, routed by each invariant's temporal form. **LINT** discharges the linear ones: a blocking
semantic check at commit. **LEVEL** is what makes LINT *correct* — a check aimed one level too low passes
on the violation it should catch. **COVER** closes the loop, projecting coverage back onto the model so a
verified-in-principle invariant with no live test becomes a named gap. Read the parts in that order; each
seam names what the part before it hands over.

## The parts

### 1. SPEC — the composed state-machine model

- **Part** — role:composed-state-machine-model
- **Role in the stack** — Model a concurrent lifecycle as a set of typed state machines running at once,
  and name the predicates that must hold *across* them as first-class invariants.
- **Failure it retires** — Concurrency correctness lives as scattered ad-hoc guards; the invariants that
  must hold across components are never named, so no one can say what "correct" even means, let alone check
  it.
- **Mechanism** — Model the lifecycle as composed state machines, name each cross-machine predicate as an
  invariant, and derive each invariant's verification obligation from its shape — a safety predicate earns
  an exhaustive state-space check, a liveness one a temporal check, a linear one a property test.
- **The seam** — Opens the stack. It is the spec every later part discharges: the census reads its
  invariants to build the obligation set, the prover reads their temporal form to pick a checker, the
  coverage map projects tests back onto these same nodes.
- **Limits / durability** — Durable — a typed state-machine model is the standard way to make concurrency
  legible, and it leans on no 2026 model capability. Its cost is authoring the machines and the invariants;
  it is only as honest as the parity gate that keeps the model equal to the running code.

### 2. CENSUS — the model-derived obligation set

- **Part** — role:model-derived-test-obligation-census
- **Role in the stack** — Derive the set of things that *should* be tested from the models: every external
  seam to fuzz, every failure edge to inject, every invariant to check.
- **Failure it retires** — Coverage is a percentage over the lines someone happened to write a test for; an
  entire untested seam or failure edge is invisible because nothing knows it was owed a test.
- **Mechanism** — Walk the models to derive the obligation set — the seams, edges, and invariants that
  demand a test — and lint the *gap* between that derived set and the tests that actually exist.
- **The seam** — Reads the SPEC's invariants and seams and turns them into a work-list. It hands the prover
  and the lints a *named* backlog of obligations, so "what still needs verifying" is a query over the
  model, not a memory.
- **Limits / durability** — Durable — deriving obligations from a typed model is deterministic and re-runs
  on every change. Its cost is the derivation rules; it fails only where an obligation kind is not yet
  modeled, which widens the census rather than breaking it.

### 3. PROVE — the exhaustive-verification tier

- **Part** — role:formal-invariant-verification
- **Role in the stack** — Give each invariant a temporal form — safety (`[]P`, always) or liveness
  (`P ~> Q`, eventually) — and let that form route *which* exhaustive checker verifies it.
- **Failure it retires** — A concurrency invariant is "tested" by a sampled unit test that walks a handful
  of interleavings; the one interleaving that violates it is never sampled, and the bug ships
  proven-absent.
- **Mechanism** — Tag each invariant with its temporal-logic form and make the form the routing input: a
  safety predicate is discharged by an exhaustive state-space model-check, a liveness one by a temporal
  checker — proven by the method its shape demands, not by a sample.
- **The seam** — Consumes the SPEC's invariants and the CENSUS's obligation set. It is the heavy-rigor
  tier: the invariants whose shape is *hairy* get an exhaustive proof here, leaving the linear ones for the
  deterministic lints beside it.
- **Limits / durability** — Durable — an exhaustive check over a bounded state space does not decay, though
  its cost grows with the space. It fails where the model abstracts away the detail that carried the bug,
  bounded by how faithfully the SPEC mirrors the code.

### 4. LINT — the deterministic-verification tier (folded from the semantic-lint stack)

- **Part** — role:semantic-lints
- **Role in the stack** — A fleet of blocking semantic checks over the tool's own source (banned APIs,
  silent-catch bans, typed-seam violations) that fail the build on invariant violations the compiler and
  review miss.
- **Failure it retires** — A recurring class of mistake keeps re-entering through review; a convention says
  "don't do that," but a convention decays under a fleet and the class re-appears one commit at a time.
- **Mechanism** — A blocking check reads *structure* — not a regex over surface text — and rejects the
  violation at commit time, moving a recurring judgment out of review and into a deterministic gate.
- **The seam** — The linear-rigor tier beside the prover. Where PROVE discharges the hairy invariants
  exhaustively, LINT discharges the linear ones deterministically at commit — the two together cover the
  obligation set the CENSUS derived, each at the rigor its invariant's shape demands.
- **Limits / durability** — Durable — a deterministic structural check does not decay and fires on every
  commit. Its guarantee is only as good as the level it targets, which the next part holds.

### 5. LEVEL — enforce at the level the invariant lives at (folded from the semantic-lint stack)

- **Part** — role:semantic-level-enforcement
- **Role in the stack** — Place each check at the granularity where the property it guards first becomes
  legible, not at the cheapest or earliest point.
- **Failure it retires** — A lint aimed one level too low passes on a spec-legal variation it should have
  caught and fires on a legal one it should have allowed — the check is present but wrong.
- **Mechanism** — Choose the scope where the invariant is actually observable — for instance, check
  model-to-code drift when an agent *returns* from a multi-commit task, never at a per-commit hook where
  the model is legitimately mid-flight.
- **The seam** — Sits over LINT. It is what makes the deterministic tier *correct* rather than merely
  present: the check the CENSUS demanded is only trustworthy once it fires at the level its invariant lives
  at.
- **Limits / durability** — Durable — a level, once chosen right, does not decay. Its cost is the judgment
  of choosing it; it fails silently when a check is placed a level off, which reads as a false pass rather
  than a red gate — the most expensive failure mode to notice.

### 6. COVER — coverage projected onto the model

- **Part** — role:coverage-model-mapping
- **Role in the stack** — Project test coverage onto the model's own nodes — its states, seams, and
  invariants — so "is this invariant tested?" is a queried fact, not a guess from a line-coverage
  percentage.
- **Failure it retires** — Line coverage says 80% and everyone relaxes; a critical invariant node sits at
  zero covering tests, invisible because the percentage averages it away.
- **Mechanism** — Map each test to the model nodes it exercises, turning the model into a work-list: an
  invariant node with no covering test is a visible gap that drives the next test.
- **The seam** — Closes the stack. It reads the SPEC's nodes and asks, of everything the CENSUS owed and
  PROVE and LINT discharged, which is actually *exercised* — so a verified-in-principle invariant with no
  live test becomes a named gap, not a comfortable average.
- **Limits / durability** — Durable — a projection of coverage onto model nodes is a query, not a runtime
  dependency. Its cost is maintaining the test-to-node map; it is exactly as complete as the SPEC's node
  set, which the census keeps honest.
