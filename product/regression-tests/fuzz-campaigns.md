# Fuzz campaigns (+ auto-coverage)

**Intent** — Campaigns that feed malformed and adversarial inputs to the tool to find crashes and
corruption, with coverage collected automatically, plus an RCA discipline that fixes to the *spec*, not
the failing seed.

| | |
|---|---|
| Summary | Malformed-input campaigns; fix to the spec, not the seed. |
| Target | Product · **Regression tests** |
| Form | `regression` |
| Enforcement | **Hard** (deterministic) — a repeatable campaign body; coverage tracked against a baseline |

## Motivation — the failure it kills

Real-world documents are malformed in ways no hand-written test anticipates: a truncated stream, an odd
encoding, a structure right at the edge of what the spec allows. A fuzzer finds the crash or corruption on inputs you would never think
to write. The failure is *crashes / corruption on adversarial or spec-edge inputs*, and it hides across
an input space far too large to enumerate.

## Why it's not just "property tests" (or "more example inputs")

Property tests check invariants over *structured, generated* inputs; fuzzing throws **malformed,
adversarial bytes** to find crashes and spec-edge failures the structured generators don't reach. And
the payoff is multiplied by an **RCA discipline**: fix to the *stable point in the format spec*, not to
the failing seed, so the fix passes *every* spec-allowed input, not just the one that crashed.
Structured generation is a good tool, and it does find bugs, until the corruption lives in bytes no
generator would produce. Adversarial campaigns reach that space, and fixing to the spec closes the whole
class the seed exposed rather than the one seed. Auto-coverage tracks what the campaign actually reached
so gains are measurable, not assumed.

## Mechanism

`*Fuzz*` / `*Campaign*` harnesses run the tool against generated malformed inputs. The test-serializer
auto-appends coverage collection when the filter contains `Fuzz`/`Campaign`, aggregated against a
baseline. On a finding, the RCA discipline mandates RCA to the stable spec point rather than patching the seed.

## Prerequisites

- **Fuzz harnesses** and a corpus/generator of malformed inputs.
- **A coverage collector + aggregator + baseline** so reach is measurable.
- **RCA discipline** (fix to the spec, not the seed) — without it, fuzzing devolves into seed whack-a-mole.

## Consequences & costs

- **Compute-heavy.** Campaigns cost real time; coverage is tracked to know when they've
  saturated.
- **Baseline maintenance.** The coverage baseline must be re-based only on intentional coverage-shape
  changes.
- **Seed-fixing is the anti-pattern** the RCA discipline exists to prevent — fixing only the failing
  input leaves the spec-class open.

## Known uses

- The `*Fuzz*` / `*Campaign*` harnesses + auto-coverage collection and aggregation.
- The fix-to-the-stable-spec-point RCA discipline.

## Related mechanisms

- *See also (sibling)* — [property-tests](property-tests.md) (structured generation),
  [test-onion-tiers](test-onion-tiers.md) (example tiers).
- **Counterpart** — the coverage baseline tracks what the campaign reached, keeping "we fuzzed it"
  honest.
