# Mediator & single-writer contracts

**Intent** — Typed registries of the system's *concurrency contracts* — which subprocess invocations are
serialized by a mediator, and which state-mutation functions are single-writer / monopoly — so "who may
run this, and how many at once" is declared and enforceable.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Novelty | notable |
| Real artifact | `mediators.py` (dev-mediator registry) · `state_mutator_registry.py` (single-writer / monopoly contracts) |
| Governing rule(s) | **#44** (aggregate-compute discipline) and the mediator charter; consumed by the mediator enforcers + coverage lints |
| Enforcement | **Hard** (deterministic) — typed contracts *held true* by the mediator enforcers + a registry-coverage lint |
| Summary | Declared mediator and single-writer contracts, coverage-checked. |

## Motivation — the failure it kills

Concurrent agent worktrees share a host and shared state. Two contract classes keep them from trampling
each other: **mediators** (a subprocess like `dotnet test` must run through the serializer, not raw) and
**single-writer contracts** (a state-mutation function must have exactly one writer, no concurrent
mutation). Undeclared, both silently break — a raw `dotnet test` slips the serializer; a second writer
corrupts state — and the breakage is a race, discovered late and hard.

## Why it's not just "the mediators/enforcers already handle it"

The enforcers (test-serializer, build-serializer, the role guard) *act*, but they need a **declared
contract** to act against — "which subprocesses are mediated, which functions are single-writer" — or a
newly-added subprocess/mutator is simply *not covered* and nobody notices. These registries **declare**
the contracts, so a coverage lint can flag a mediated-class call or a state mutator that isn't wired.
The distinction is *a declared concurrency contract that coverage can check* versus *enforcers that only
guard what someone remembered to route through them*.

## Mechanism

`mediators.py` is the registry of dev-time subprocess serializers (the test/build serializers, the
`lint-all` mutex, the commit-slave serializer) — what each mediates, its cap, its bypass-env.
`state_mutator_registry.py` declares single-writer / monopoly contracts for state-mutation functions.
Enforcers and coverage lints read these to refuse unmediated calls and flag uncovered mutators.

## Prerequisites

- **A mediator registry** (subprocess → serializer, cap, bypass) and a **single-writer registry**
  (function → monopoly contract).
- **Enforcers keyed on the registry** so an unmediated call is refused.
- **Coverage lints** so a new subprocess/mutator that should be contracted is flagged.

## Consequences & costs

- **New mediated subprocess / new mutator ⇒ a registry entry** or a coverage-lint failure.
- **The contract is only as good as the enforcer** — a declared-but-unenforced contract is documentation.

## Known uses

- `mediators.py` — the dev-mediator (subprocess-serializer) registry (rule #44 host locks).
- `state_mutator_registry.py` — single-writer / monopoly contracts.
- The mediator enforcers ([test-serializer](../../agent/mediators-and-resource-locks/test-serializer.md) et al.).

## Related controls

- **Bridge** — the agent [mediators & resource locks](../../agent/mediators-and-resource-locks/test-serializer.md)
  family *enforces* these contracts (agent side) ◀──▶ the model *declares* the concurrency the codebase
  must honour (product side).
- *See also* — [synchronization-model](synchronization-model.md): the OS-lock layer beneath these
  higher-level contracts.
- **Counterpart** — [drift-parity-gates](drift-parity-gates.md): the coverage lints keeping the
  registries complete.
