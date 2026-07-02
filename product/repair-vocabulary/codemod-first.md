# Codemod-first threshold (N≳50 → AST transformer)

**Intent** — For a large mechanical backlog (N≳50 sites with a deterministic fix shape), author *one
AST-level transformer* instead of dispatching N agents — bounding *how* large mechanical changes are
made.

| | |
|---|---|
| Target | Product · **Repair vocabulary** |
| Form | `repair-vocab` |
| Novelty | notable |
| Real artifact | the codemod-first threshold; AST transformers (e.g. `hoist_inline_imports.py`) |
| Governing rule(s) | **#28** (codemod-first for large mechanical lint backlogs — N≳50 + deterministic shape → AST transformer) · **#31** (codemod-class commits may skip the pre-commit lint stanza with a reason) |
| Enforcement | **Soft** (probabilistic) — a discipline/threshold guiding *how* a mechanical backlog is fixed; nothing blocks N per-site edits, though the transform it produces is itself deterministic |

## Motivation — the failure it kills

A large mechanical lint backlog — say 200 sites all needing the same deterministic edit — tempts one of
two bad responses: dispatch N agents (expensive, and each introduces per-site drift) or hand-edit them
(slow and inconsistent). The failure is *N inconsistent hand/agent fixes for a change that is actually a
single deterministic transform*, and it recurs at every large mechanical backlog.

## Why it's not just "dispatch an agent per site" (or "fix them by hand")

N agents on a *deterministic* fix is wasteful and yields per-site drift — each agent re-derives the same
edit slightly differently, and 200 of them is 200 chances to diverge. A **single AST transformer**
applies the *exact same* transform everywhere, deterministically, in one reviewable artifact. Rule #28
sets the threshold: N≳50 + deterministic shape → codemod; genuine per-site *judgment* → Sonnet. The
distinction is *one deterministic AST transform* versus *N judgment-free agent edits*. Codemods are kept
as **deprecated reference exemplars** so the next backlog starts from a working pattern.

## Mechanism

Rule #28 triggers a codemod when N≳50 sites share a deterministic shape; the transformer operates at the
AST level (e.g. `hoist_inline_imports.py`). Rule #31 lets a codemod-class commit skip the pre-commit
*lint* stanza (with a `pre-commit-skip: <reason>` marker; unit-tier still runs), since the transform is
mechanical. Finished codemods are marked deprecated and cross-referenced as paste-ready exemplars.

## Prerequisites

- **An AST toolkit** for the language and a **deterministic fix shape**.
- **The threshold judgment** (N≳50, deterministic vs per-site judgment).
- **The pre-commit-skip protocol** for codemod waves (#31).

## Consequences & costs

- **Writing the transformer is upfront cost** — it pays off only at scale, which is what the threshold
  encodes.
- **Only for deterministic shapes.** A backlog needing per-site judgment still goes to Sonnet, not a
  codemod.
- **Skipping the lint stanza (#31) is a scoped hole** — justified by the transform's mechanical nature,
  marker-audited.

## Known uses

- Rule #28's N≳50 threshold; AST transformers such as `hoist_inline_imports.py`.
- Rule #31's `pre-commit-skip` for codemod-class waves; codemods retained as deprecated exemplars.

## Related controls

- *See also (sibling)* — [typed-categories](typed-categories.md), [remediation-verbs](remediation-verbs.md):
  the other bounded-move controls; this one bounds *how a mechanical change is executed*.
- *See also (cross-target)* — this is the product-side face of the same codemod-first discipline the
  agent fleet uses for its own mechanical lint backlogs.
