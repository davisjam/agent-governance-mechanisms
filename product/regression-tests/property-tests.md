# FsCheck property tests

**Intent** — Property-based tests that assert *invariants* (round-trip, combinatorial) over
machine-*generated* inputs, catching bugs in the input space that example-based tests never reach.

| | |
|---|---|
| Target | Product · **Regression tests** |
| Form | `regression` |
| Novelty | notable |
| Real artifact | FsCheck.Xunit property tests (round-trip / combinatorial invariants) across the test projects |
| Governing rule(s) | The CLAUDE.md property-based-testing pilot + triage — FsCheck.Xunit is the canonical property-test library; add when a class has property-shaped invariants |
| Enforcement | **Hard** (deterministic) — a repeatable regression body; shrinks to a minimal counterexample |

## Motivation — the failure it kills

Example-based tests only check the cases you *thought of*. Invariants — read∘write = identity, a
combinatorial property that must hold for all inputs — fail on inputs you never imagined and never
wrote a test for. The failure is *a bug living in the untested input space*, and it recurs for any
invariant-shaped contract that hand-picked examples under-cover.

## Why it's not just "write more example tests"

Examples check *points*; you cannot enumerate a document's input space by hand, and the bug is almost
always in the case you didn't write. A property test asserts an **invariant over generated inputs**
(FsCheck synthesizes them) and, on failure, **shrinks** to a minimal counterexample you can debug. The
distinction is *an invariant checked over generated inputs* versus *a finite set of hand-picked
examples*. It is the highest-leverage tool for the bug-finding-affordance goal — a good property surfaces
latent bugs a hundred examples would miss.

## Mechanism

FsCheck.Xunit properties (round-trip and combinatorial invariants) live across the test projects; you
add them when a class has a property-shaped contract. FsCheck generates inputs, checks the property, and
shrinks any failure to the smallest input that still breaks it.

## Prerequisites

- **FsCheck** and **generators** for the domain types.
- **Identified invariants** — a class whose contract is expressible as a property (round-trip, idempotence, a combinatorial law).
- Determinism in the property, or it flakes.

## Consequences & costs

- **Generators are real work** to write for rich domain types.
- **The property must be stated correctly** — a wrong invariant yields false failures or, worse, false
  confidence.
- **Nondeterministic properties flake** — the invariant must be a true function of the input.

## Known uses

- FsCheck.Xunit properties across the test projects (round-trip / combinatorial invariants).
- Added per-class when a property-shaped invariant exists (the pilot + triage discipline).

## Related controls

- *See also (sibling)* — [test-onion-tiers](test-onion-tiers.md), [fuzz-campaigns](fuzz-campaigns.md):
  examples-in-tiers and adversarial-fuzzing complement invariant-checking.
- **Consumer** — properties are asserted over the typed models
  ([pdf-model](../canonical-models-and-seams/pdf-model.md) et al.): round-trip properties over a model
  are how you pin its read/write invariants.
