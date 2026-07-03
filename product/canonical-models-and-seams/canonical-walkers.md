# Canonical walkers (one traversal per tree)

**Intent** — One canonical walker per tree (`PdfStructTreeWalker`, the `RuleWalkers`,
`DocxTopLevelPartWalker`, …) that all traversal must route through, instead of ad hoc recursion — so a
tree's traversal invariants live in exactly one place.

| | |
|---|---|
| Summary | One canonical traversal per tree, not ad hoc recursion. |
| Target | Product · **Canonical models & seams** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) · *blocking* — routed via the model ban-lints; raw recursion / regex-into-tree is banned alongside raw library access |

## Motivation — the failure it kills

Ad hoc tree recursion re-implements traversal at every site, and each copy is subtly wrong in its own
way — one misses a node type, another visits in the wrong order, a third forgets link annotations. The
same traversal bug recurs per site, and because each is hand-rolled, a fix to one never reaches the
others.

## Why it's not just "recurse the tree where you need it"

Hand-rolled recursion **duplicates the traversal logic**, and duplicated logic drifts: the invariants
(visit every node type, in the right order, resolving indirect references) get re-derived — badly — at
each site. A canonical walker **centralizes** the traversal so those invariants are fixed once and
inherited everywhere. The distinction is *a single canonical traversal* versus *N ad hoc recursions
that each re-introduce the same class of omission*. (A standard DRY-plus-walker-discipline move that
keeps the typed models usable without re-opening the raw-access door.)

## Mechanism

Each tree type has one canonical walker (`PdfStructTreeWalker` for the PDF struct tree, `RuleWalkers`
for the checking pass, `DocxTopLevelPartWalker` for DOCX parts, …). The canonical-walker discipline
routes all traversal through them; regexing into the tree or hand-recursing is banned together with raw
library access.

## Prerequisites

- **A walker per tree type**, exposing the traversal shape callers actually need.
- **A discipline (and lint coverage) that routes traversal through it**, closing the raw-recursion and
  regex-into-tree escapes.

## Consequences & costs

- **The walker must expose what callers need.** A missing traversal shape pushes a caller back to raw
  recursion — coverage matters here, same as the models.
- **Low novelty.** This is a well-understood pattern; its value is DRY + invariant-centralization, not
  invention.

## Known uses

- `PdfStructTreeWalker`, the `RuleWalkers`, `DocxTopLevelPartWalker`, and the other per-tree walkers.
- The canonical-walker discipline (traversal routed through the walker, raw recursion banned).

## Related controls

- *See also* — [pdf-model](pdf-model.md), [office-models](office-models.md): walkers are *how you
  traverse* those typed models; they are part of the same sole-seam discipline.
- **Enabler** — a canonical walker makes routing traversal through the typed models practical;
  without it, callers reach for raw recursion and re-open the ban-lint's door.
