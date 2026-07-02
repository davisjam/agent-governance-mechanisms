# PdfModel (sole PDF mutation surface)

**Intent** — Route *all* PDF reads and writes through one typed model, with raw iText access banned by
a lint — so PDF structure is compiler-checked and every mutation passes through a surface that encodes
the format's invariants.

| | |
|---|---|
| Target | Product · **Canonical models & seams** |
| Form | `typed-ir` |
| Novelty | notable |
| Real artifact | `PdfModel` + its typed `Primitives/` mutators; the `itext-direct-access` ban-lint |
| Governing rule(s) | **#15** (all PDF I/O goes through `PdfModel`; raw iText banned) |
| Enforcement | **Hard** (deterministic) · *blocking* — `itext-direct-access` + `helpers-no-itext` fail the build on raw iText; the typed model is *construction*, the ban-lint is the counted control |

## Motivation — the failure it kills

Raw iText is a minefield of silent, invisible-at-the-call-site failures. Forget `SetModified()` on an
indirect object and the write is **silently dropped** on save. Call `tagPointer.AddTag` or `dict.Put`
directly and you can corrupt the `/StructTreeRoot` — the exact class that produced the v172 corruption.
There is no single place to enforce these invariants, so scattered raw calls make the *same* PDF bug
class recur at every call site.

## Why it's not just "use iText carefully" (or "code-review the PDF calls")

iText's sharp edges are invisible where they're used — a missing `SetModified()` looks like correct
code, and reviewers miss it reliably because nothing in the diff flags it. `PdfModel` makes the raw
API **unreachable**: typed mutators encode the invariants (they can't forget `SetModified()`), and the
`itext-direct-access` ban-lint fails the build on any raw constructor, `AddTag`, `dict.Put`, or
`structRoot.AddKid`. The distinction is *a typed sole-seam whose raw alternative is lint-banned* versus
*disciplined use of a raw API*. The typed model is **construction** — the bug becomes unrepresentable;
the ban-lint is the **counted detection control** that keeps every call site on the seam.

## Mechanism

Read via `PdfModel.Read(path)`; write via the typed mutators in `Primitives/`. The `itext-direct-access`
and `helpers-no-itext` lints ban raw iText constructors, `tagPointer.AddTag`, `dict.Put`, and
`structRoot.AddKid`. Each typed mutator wires the `SetModified()` discipline and stamp emission so a new
verb cannot land un-wired.

## Prerequisites

- **A typed model covering the domain surface** — every operation callers need must exist as a typed
  mutator, or they're forced back to the raw API.
- **A ban-lint on the raw API** (the counted control) plus a migration of *all* existing call sites.
- **A pinned library version** — iText minor bumps can silently change auto-tagging, so the seam pins
  it and gates upgrades behind a regression suite.

## Consequences & costs

- **The model must cover everything.** A missing operation forces either a `noqa` escape (a hole) or a
  model extension (the right fix, but friction) — the seam's completeness is load-bearing.
- **Version lock-in.** Pinning iText for tag-tree stability means upgrades are deliberate, gated work.
- **Maintenance surface.** The typed mutators + the ban-lint are code to keep current as the format
  needs grow.

## Known uses

- `PdfModel.Read` + the typed `Primitives/` mutators (each wiring `SetModified()` + stamp emission).
- `itext-direct-access` + `helpers-no-itext` ban-lints.
- The v172 `/StructTreeRoot` corruption — the defect class this seam eliminates.

## Related controls

- **Counterpart** — the `itext-direct-access` ban-lint (hard) is what holds this construction-mode seam
  in place; without it, "route through PdfModel" is an unenforced convention.
- *See also (sibling)* — [office-models](office-models.md): the same typed-model + ban-lint pattern for
  the OpenXML formats — the pair is the *defect-class consolidation* of raw-library corruption across
  all four document formats.
- *See also* — [canonical-walkers](canonical-walkers.md): how traversal over this typed model is done.
