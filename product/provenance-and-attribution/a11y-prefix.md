# `a11y_` prefix convention

**Intent** — A naming convention for inserted artifacts — invisible-to-author insertions MUST start with
`a11y_`, user-visible insertions MUST NOT — so tool-inserted content is distinguishable from authored
content and the `InsertedContentValidator` can cover it.

| | |
|---|---|
| Summary | Prefix invisible inserts so they're distinguishable and tracked. |
| Target | Product · **Provenance & attribution** |
| Form | `repair-vocab` |
| Enforcement | **Hard** (deterministic) — the `InsertedContentValidator` covers every registered insert |

## Motivation — the failure it kills

The tool *inserts* content — alt text, tags, off-canvas scaffolding. Mixing tool-inserted content with
author-written content risks two failures: presenting invisible scaffolding *as if* the user wrote it,
or an insert that isn't tracked and so isn't validated. The failure is *untracked or mislabelled
inserted content*, and it recurs per inserter and per insertion site.

## Why it's not just "name things sensibly" (or "keep a list of inserts")

An ad-hoc naming choice isn't *checkable* — nothing enforces it, and a hand-maintained list of inserts
drifts. The `a11y_` prefix is a **convention with a rule** (invisible → `a11y_`, user-visible → not,
spec-mandated → the spec name) that the `InsertedContentValidator` *relies on*, and every new inserter
calls `registry.Record(...)` so it is covered **automatically**. The distinction is *a checkable naming
convention plus auto-registration* versus *ad-hoc naming and a manual list*. It is a repair-vocabulary
control: it bounds *how inserts are named and tracked*, which makes validating them possible.

## Mechanism

Invisible inserts are prefixed `a11y_` (the invisible-insert prefix convention); user-visible inserts are not; spec-mandated names keep
their spec name. New inserters call `registry.Record(...)`, so the `InsertedContentValidator`
automatically covers them; off-canvas placement uses dynamic geometry so it never bleeds on-page.
Per-site corollaries live in the placement-audit doc.

## Prerequisites

- **The naming convention** (the three-way rule) applied at every insertion site.
- **A registry** inserters record into, and a **validator** that reads it.

## Consequences & costs

- **Adherence is partly discipline.** A mis-named or unregistered insert escapes coverage until caught.
- **Spec-mandated names are exceptions** to the prefix rule (by necessity), a small carve-out to track.
- **Every inserter must call `registry.Record`** — the auto-coverage only works if the registration
  habit holds.

## Known uses

- The `a11y_` prefix convention and its per-site corollaries.
- `registry.Record(...)` + the `InsertedContentValidator` (automatic coverage of registered inserts).

## Related controls

- **Consumer** — the `InsertedContentValidator` reads the registered inserts (naming + registration are
  what it depends on).
- *See also (sibling)* — [remediation-verbs](../repair-vocabulary/remediation-verbs.md): both bound the
  remediator's move-space; this one bounds how *inserted content* is named and tracked.
