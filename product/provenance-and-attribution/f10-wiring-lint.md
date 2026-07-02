# F10 mutator-stamp-wiring lint

**Intent** — A lint that fails the build if *any* mutator verb in the Model `Primitives` lacks stamp
wiring — so a new mutator cannot land producing unattributable mutations.

| | |
|---|---|
| Summary | Fail the build if any mutator verb lacks a stamp. |
| Target | Product · **Provenance & attribution** |
| Form | `validation` |
| Enforcement | **Hard** (deterministic) · *blocking* — scans every mutator verb; fails the build on an unwired one (0 open gaps) |

## Motivation — the failure it kills

[Attribution stamps](mutator-stamps.md) only work if **every** mutator stamps. Add one new verb without
wiring and it silently produces unattributable mutations — a hole in the audit trail that no one sees
until an RCA hits it and finds no stamp. The failure is *an unstamped mutator (an attribution gap)*, and
it recurs precisely when a new verb is added — usually under time pressure, when "remember to stamp" is
most likely to be forgotten.

## Why it's not just "remember to add the stamp" (or "review new mutators")

"Remember" fails exactly when a new verb is added in a hurry, and review reliably misses a *missing*
call (nothing in the diff shouts "no stamp here"). The F10 lint **mechanically checks that every mutator
verb** in the `Primitives` directories calls stamp wiring, and fails the build on a gap — HIGH-severity,
held at 0 open gaps. The distinction is *a mechanical completeness check over all verbs* versus *a
per-author reminder*. This is the counterpart that turns "we attribute mutations" from an aspiration
into a guarantee.

## Mechanism

`lint-mutator-stamp-wiring.py` scans the `{Pdf,Slides,Docs,Sheets}Model` `Primitives` directories for
mutator verbs and asserts each calls the stamp wiring. It is BLOCKING; a new verb without wiring is a
HIGH-severity finding. The invariant has been held at 0 open gaps.

## Prerequisites

- **A detectable "mutator verb" pattern** in the `Primitives` layer.
- **A detectable stamp-wiring call** so the lint can tell wired from unwired.
- **A lint over the Primitives directories** run in the gates.

## Consequences & costs

- **The verb-detection heuristic is load-bearing.** Miss a verb shape and a real gap passes; over-match
  and legitimate code fails.
- **Coupled to the Primitives structure** — a reorganization of the mutator layer needs the lint updated
  in step.

## Known uses

- `lint-mutator-stamp-wiring.py` (F10, BLOCKING, 0 open gaps).

## Related controls

- **Counterpart** — of [mutator-stamps](mutator-stamps.md): the stamps are the *construction* (the audit
  record), this lint is the *counted control* that guarantees they're complete. The canonical
  construction-held-by-detection pairing on the product side.
- *See also (sibling)* — [semantic-lints](../validation-and-conformance/semantic-lints.md): the F10 lint
  is a member of that fleet doing a completeness-over-verbs job.
