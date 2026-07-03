# ContentValidator (input ⊆ output fidelity)

**Intent** — A deterministic gate asserting that every piece of the user's original content survives
remediation — *input content ⊆ output content* — run in production, with a per-pass variant in staging
that pinpoints which pass dropped content.

| | |
|---|---|
| Summary | Assert input content survives remediation — a fidelity gate. |
| Target | Product · **Validation & conformance** |
| Form | `validation` |
| Enforcement | **Hard** (deterministic) · *blocking* — fails the job in prod on a fidelity violation; the per-pass variant emits `##PASS_FIDELITY##` + exit 3 in staging |

## Motivation — the failure it kills

Remediation *mutates* the document across many passes and four formats. A bug in any pass could
**silently drop or alter user content** — delete a paragraph, mangle a table, lose a caption. For a
fidelity-critical tool that is the worst possible outcome: the output looks fine and quietly isn't what
the author wrote. The failure recurs on every remediation pass.

## Why it's not just "trust the remediation code" (or "spot-check outputs")

"Trust the code" is exactly what fails when a mutator has a bug, and spot-checking outputs misses
*silent* drops — you don't notice the paragraph that's gone. `ContentValidator` makes fidelity a
**deterministic post-condition**: the input's content must be a subset of the output's, checked
mechanically, on every production job. The distinction is *a fidelity post-condition gate that fails
the job* versus *hoping mutators preserve content*. The staging per-pass variant adds localization —
it tells you *which* pass violated the subset, turning "content was lost somewhere" into "pass N lost
it."

## Mechanism

`ContentValidator` extracts the input's content and asserts it is a subset of the output's; it runs in
production and fails the job on violation. A staging-only per-pass variant (gated by an env label)
emits `##PASS_FIDELITY##` and exit 3 so the offending pass is identified before delivery.

## Prerequisites

- **A content extraction comparable across input and output** — the subset check is only as good as
  what "content" is defined to be.
- **A subset predicate** that tolerates legitimate reformatting/reordering without false positives.
- **A run point** post-remediation and pre-delivery, plus a per-pass hook for localization.

## Consequences & costs

- **Everything rests on the extractor.** A lossy or over-eager content extractor produces false positives
  (blocks good output) or false negatives (misses a real drop).
- **Subset semantics are subtle.** Reordering, whitespace, and reformatting must be normalized or the
  gate cries wolf.
- **It runs on every job** — a real but accepted cost for a fidelity guarantee.

## Known uses

- `ContentValidator` — the production input-⊆-output fidelity gate.
- The `##PASS_FIDELITY##` staging per-pass variant (localizes the offending pass).
- The accessibility-remediation policy it enforces (never drop content the user wrote).

## Related controls

- **Layer** — with [standards-rule-engine](standards-rule-engine.md): both are product gates over the
  artifact — fidelity (nothing lost) and conformance (standards met).
- **Counterpart** — the per-pass staging variant localizes what the prod gate only detects.
- *See also (sibling)* — [coherence-lints](coherence-lints.md): the other deterministic checks in this
  family.
