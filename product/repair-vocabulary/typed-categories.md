# Typed `ViolationCategory` / `FailureCategory` enums

**Intent** — Replace free-form failure strings with typed enums, so the categorical move-space is a
closed, enumerable set that the compiler and lints can check for exhaustive handling.

| | |
|---|---|
| Target | Product · **Repair vocabulary** |
| Form | `repair-vocab` |
| Novelty | notable |
| Real artifact | the `ViolationCategory` / `FailureCategory` enums (replacing bare failure strings) |
| Governing rule(s) | The CLAUDE.md regex/naming discipline — *failure-category strings → `FailureCategory` enum values*, not bare strings |
| Enforcement | **Hard** (deterministic) — a typed closed set; the compiler + exhaustiveness checks enforce it |

## Motivation — the failure it kills

Bare failure strings — `"timeout"`, `"corrupt"`, `"rate_limit"` — are typo-prone, un-enumerable, and let
a `switch` silently miss a case. A typo compiles and mis-routes; a new category isn't forced into every
handler; and you can't even ask "are all categories handled?" The failure is *an unhandled or
mistyped category → silent misbehaviour*, recurring at every place a category is produced or consumed.

## Why it's not just "use descriptive strings"

Strings are an *open* set: nothing makes them exhaustive, a typo is a runtime bug rather than a compile
error, and adding a case doesn't force the existing handlers to deal with it. A **typed enum** makes the
set *closed* and its handling *exhaustively checkable* — add a case and the non-exhaustive `switch`
lights up. The distinction is *a closed, typed vocabulary* versus *open free-form strings*. This is
"explicit models over implicit," and "types are how you name shapes," applied to the failure/violation
space — the enum *names* the categorical shape the strings left anonymous.

## Mechanism

`ViolationCategory` and `FailureCategory` enums replace bare strings across the code; category
comparisons use enum values, not regex-against-strings; external strings are mapped to the enum at the
boundary. Exhaustive-match discipline (and the compiler's non-exhaustiveness signal) forces every
handler to cover every case.

## Prerequisites

- **A closed, identifiable category set** — the space must actually be enumerable.
- **The enums**, and callers switched from strings to enum values.
- **Boundary mapping** from external/serialized strings into the enum.

## Consequences & costs

- **Adding a category touches every handler** — which is the point (it forces handling), but it is real
  work.
- **Boundary translation.** External strings (LLM output, wire formats) still arrive as strings and must
  be mapped in — a controlled seam, but a seam.

## Known uses

- `ViolationCategory` / `FailureCategory` enums in place of bare failure strings.
- Enum-value comparison instead of regex-on-strings (the regex-usage discipline).

## Related controls

- *See also (sibling)* — [remediation-verbs](remediation-verbs.md), [codemod-first](codemod-first.md):
  the other bounded-move-space controls.
- *See also (cross-target)* — the agent side's const-string topic registry
  ([typed-event-bus](../../agent/lifecycle-and-observability/typed-event-bus.md)) is the same "typed namespace
  over free-form strings" move for event topics.
