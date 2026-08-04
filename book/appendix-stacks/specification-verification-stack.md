*A two-page synthesis of the specification + verification stack. Six patterns turn a concurrent behavioral
spec into checked assurance: model the lifecycle as composed state machines, derive every obligation from it,
discharge each at the rigor its shape demands, then map coverage back onto the model so an unexercised
invariant is a visible gap, not a guess.*

## The capability

**Say what "correct" means for a concurrent system, derive every check that correctness owes, and prove each
one at the right rigor.** The stack makes two capabilities: *establish completion on re-derived evidence*,
and *constrain where and how agents act*. It models the lifecycle as state machines running at once, names
the predicates that must hold across them, and routes each to a checker by its shape — an exhaustive proof
for a hairy safety or liveness invariant, a deterministic lint for a linear one. Then it projects coverage
back onto the model, so a verified-in-principle invariant with no live test is a named hole.

## Failure classes it covers

- **The unnamed invariant.** Concurrency correctness lives as scattered ad-hoc guards; the predicates that
  must hold across components are never named, so no one can say what "correct" even means.
- **The invisible obligation.** Coverage is a percentage over the lines someone happened to test; a whole
  untested seam or failure edge is invisible because nothing knows it was owed a test.
- **The unsampled interleaving.** A concurrency invariant is "tested" by a unit test that walks a handful of
  interleavings; the one that violates it is never sampled, and the bug ships proven-absent.
- **The convention that decays.** A recurring mistake keeps re-entering through review; a convention says
  "don't do that," but a convention decays under a fleet and the class re-appears one commit at a time.
- **The check aimed wrong.** A lint one level too low passes a spec-legal variation it should catch and fires
  on a legal one it should allow — present but wrong.
- **The comfortable average.** Line coverage reads 80% and everyone relaxes; a critical invariant sits at
  zero covering tests, invisible because the percentage averages it away.

## Composition

<!-- label: specification-verification-stack -->
<!-- figure: assets/specification-verification-stack.svg | The specification + verification stack in one picture. Six parts run left to right. The spec (violet): SPEC models the lifecycle as composed state machines and names the cross-machine invariants; CENSUS derives every obligation owed. The rigor tiers: PROVE (green) discharges the hairy invariants with an exhaustive check routed by each invariant's temporal form; LINT (blue) discharges the linear ones with a blocking semantic check at commit, and LEVEL (blue) aims each check at the granularity where its property first becomes legible. COVER (accent) projects coverage back onto the model's nodes, so a verified-in-principle invariant with no live test is a visible gap. -->

Two parts build and read the spec; three discharge the obligations at graded rigor; one maps coverage back.
The spec is the single source every later part reads.

## The constituent patterns

- **SPEC — role:composed-state-machine-model.** Model a concurrent lifecycle as a set of typed state machines
  running at once, and name the predicates that must hold *across* them as first-class invariants. The spec
  every later part discharges.
- **CENSUS — role:model-derived-test-obligation-census.** Derive from the models what *should* be tested —
  every external seam to fuzz, every failure edge to inject, every invariant to check — and lint the gap
  between that derived set and the tests that exist.
- **PROVE — role:formal-invariant-verification.** Give each invariant a temporal form — safety (always) or
  liveness (eventually) — and let the form route which exhaustive checker verifies it. The heavy-rigor tier
  for the hairy invariants.
- **LINT — role:semantic-lints.** A fleet of blocking structural checks over the tool's own source rejects
  the linear-invariant violation at commit, moving a recurring judgment out of review into a deterministic
  gate.
- **LEVEL — role:semantic-level-enforcement.** Place each check at the granularity where its property first
  becomes legible, not at the cheapest or earliest point — what makes the deterministic tier *correct* rather
  than merely present. (This member is a design-time placement principle, so it lives online, not as a
  print page.)
- **COVER — role:coverage-model-mapping.** Project test coverage onto the model's own nodes — states, seams,
  invariants — so "is this invariant tested?" is a queried fact, not a guess from a line-coverage percentage.

## A DocAble example, end to end

DocAble's job pipeline is concurrent: a parent job fans out into chunks, each chunk walks its own lifecycle,
and results fan back in. **SPEC** models the parent and chunk lifecycles as composed state machines and names
the cross-machine predicates — for instance, *the fallback file is uploaded to storage before the job row is
marked complete*. **CENSUS** walks those machines and derives the obligation set: the seams to fuzz, the
failure edges to inject, the invariants to check. **PROVE** takes the hairy safety invariant — no crash
interleaving leaves a job marked done with no artifact — and discharges it with an exhaustive state-space
check, not a sampled unit test. **LINT** discharges the linear ones deterministically at commit: a banned
raw call, a silent catch, a mutation that skips the typed seam. **LEVEL** keeps those lints honest — a
model-to-code drift check fires when an agent *returns* from a multi-commit task, never at a per-commit hook
where the model is legitimately mid-flight. **COVER** then asks, of every obligation CENSUS owed and PROVE
and LINT discharged, which is actually exercised — so an invariant verified in principle but with no live
test surfaces as a gap.

## Tradeoffs and adoption order

1. **SPEC first, and it is only as honest as the parity gate that keeps it equal to the running code.**
   Author the machines and the invariants; without them nothing downstream has a spec to read.
2. **CENSUS turns the spec into a work-list.** Cheap, deterministic, re-runs on every change; it makes "what
   still needs verifying" a query, not a memory.
3. **PROVE and LINT split by shape.** Route the hairy invariants to exhaustive proof — its cost grows with
   the state space — and the linear ones to commit-time lints, which are cheap and fire on every commit.
   LEVEL is the judgment that keeps each lint aimed right; misplacement fails silently as a false pass, the
   most expensive failure to notice.
4. **COVER last.** A projection, not a runtime dependency; it keeps the discharged set honest against the
   spec's nodes.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
The stack sits on the [model-coherence stack](appendix-d-model-coherence-stack.html) (its state machines are
that stack's executable data) and feeds the
[observe → react loop](appendix-d-observe-react-stack.html) (a verified invariant still needs a live signal
when it breaks). The full 83-mechanism catalogue is online in the web edition.
