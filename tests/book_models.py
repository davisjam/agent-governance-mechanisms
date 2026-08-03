"""Drift checks for the book's typed 4+1 view-models (`book-models/`).

The book preaches (Part 3) that every view is a typed model held equal to the source by a build-time drift
check — derived, never snapshotted. This module dogfoods that on the book itself: it re-derives each
view-model from the book via `book-models/` (over `book_ir`) and fails on divergence.

CURRENTLY IMPLEMENTED:

OUTLINE view (the PoC; DESIGN §2.1):
  - O1 (drift): the materialized `book-models/outline.json` equals a fresh derivation from the book. A
    heading added / removed / renumbered / re-anchored without regenerating the artifact is a finding.
  - O2/O3/O4 (invariants): every section has a topic sentence; section ids are unique per chapter; heading
    nesting is well-formed. Walked by `outline_model.invariant_findings`.

OUTCOMES view (DESIGN §2.6):
  - drift: `book-models/outcomes.json` equals a fresh derivation (declared outcomes + derived candidates).
  - U1–U7 (coverage / honesty): each outcome has a PRIMARY unit (chiefly teaches it — drives coverage) plus
    elaborative SECONDARY units (reinforce it — do NOT drive coverage). Primary drives coverage: every
    chapter / Part / the book must be the PRIMARY of ≥1 outcome (an elaborative-only unit is still a GAP);
    every primary/secondary unit resolves; every verb is in the taxonomy; every provenance tag (derived |
    declared | gap-recommended) cites its grounding. Walked by `outcomes_model.coverage_findings`. The
    no-primary-section list (`section_gap_findings`) is the author's fill worklist — informational, not gated.

REVERSE INDEX (the drift layer's substrate; DESIGN §8):
  - freshness: `book-models/reverse_index.json` equals a fresh inversion of the built views' forward refs.
  - structural: every view->md reference resolves against the current source (no dangling section id /
    chapter / part / concept / label). One walk over the inverted edges. Walked by
    `reverse_index.structural_findings`. This is the STRUCTURAL + FRESHNESS half of the two-kind drift
    split — mechanical, a lint; the SEMANTIC half is a review-gate agent audit (DESIGN §8), not here.

LANDS AUDIT-ONLY (repo rule-#55 discipline). The book carries deliberate draft gaps, and the outline seed
surfaces 2 real O2 findings today; landing this blocking-red would break the gate. So it registers
`audit_only=True` in catalog_tests.py, reports its findings, and never contributes to the fail count. A
follow-up promotes it to blocking once the O2 findings are drained (a topic sentence added to the two
sections, or the check refined to accept an epigraph/list-led section). This mirrors exactly how the
concept model's L1–L3 landed (audit-only → drain → gate).
"""
from __future__ import annotations

import os
import sys

from tests.common import FAIL, PASS, ROOT, rel

_BOOK_MODELS = os.path.join(ROOT, "book-models")
if _BOOK_MODELS not in sys.path:
    sys.path.insert(0, _BOOK_MODELS)


def check_outline_model():
    """The outline view's drift + invariant check (audit-only). Re-derives the outline from the book and
    reports: O1 the on-disk artifact matches a fresh derivation; O2/O3/O4 the outline's own invariants.
    Keyed off `book-models/outline.json` + the book prose (via book_ir)."""
    import outline_model as om  # noqa: E402 — path set above; the book-model package

    issues: list[str] = []

    # O1 — drift: the stored artifact equals a fresh derivation.
    outline = om.derive_outline()
    fresh = om.to_jsonable(outline)
    stored = om.load_artifact()
    if stored is None:
        issues.append(f"{rel(om._ARTIFACT)} missing — run `python3 book-models/outline_model.py regenerate`")
    elif stored.get("chapters") != fresh["chapters"] or stored.get("_counts") != fresh["_counts"]:
        issues.append(f"O1 DRIFT: {rel(om._ARTIFACT)} disagrees with a fresh derivation from the book — "
                      f"regenerate with `python3 book-models/outline_model.py regenerate`")

    # O2/O3/O4 — the outline's structural invariants.
    issues.extend(om.invariant_findings(outline))

    # Audit-only: the caller (catalog_tests.py Check(audit_only=True)) renders these as [audt] and excludes
    # them from the fail tally, so returning FAIL-with-issues surfaces them without gating. Kept explicit
    # here so a future promotion to blocking is a one-line flip in catalog_tests.py, not a rewrite.
    return (FAIL if issues else PASS), issues


def check_outcomes_model():
    """The outcomes view's drift + coverage check (audit-only). Re-derives the outcome model from the book
    (declared outcomes + derived candidates) and reports: drift against the on-disk artifact; U1–U7 the
    coverage / honesty invariants (primary drives coverage — every chapter/Part/book is the PRIMARY of an
    outcome; every primary/secondary unit resolves; verb+bloom consistent; every provenance tag cites its
    grounding). Keyed off `book-models/outcomes.json` + `outcomes_declared.json` + the book prose (via
    book_ir)."""
    import outcomes_model as ocm  # noqa: E402 — path set above; the book-model package

    issues: list[str] = []

    # Drift — the stored artifact equals a fresh derivation.
    model = ocm.derive_model()
    fresh = ocm.to_jsonable(model)
    stored = ocm.load_artifact()
    if stored is None:
        issues.append(f"{rel(ocm._ARTIFACT)} missing — run "
                      f"`python3 book-models/outcomes_model.py regenerate`")
    elif stored.get("outcomes") != fresh["outcomes"] or stored.get("_counts") != fresh["_counts"]:
        issues.append(f"DRIFT: {rel(ocm._ARTIFACT)} disagrees with a fresh derivation from the book — "
                      f"regenerate with `python3 book-models/outcomes_model.py regenerate`")

    # U1–U7 — coverage (primary-driven) + honesty invariants (unit resolution, verb+bloom, provenance,
    # elaborative-unit resolution).
    issues.extend(ocm.coverage_findings(model))

    # Audit-only: same non-gating contract as check_outline_model — surfaced as [audt], excluded from the
    # fail tally. The uncovered-section list is deliberately NOT included here (it is the expected PoC
    # backlog, not a defect); `python3 book-models/outcomes_model.py gaps` prints it for the author.
    return (FAIL if issues else PASS), issues


def check_claims_model():
    """The claims view's drift + structural check (audit-only). Re-derives the claim model from the
    hand-authored `claims_declared.json` and reports: C7-drift against the on-disk artifact; C1-C6 the
    structural / schema invariants (every home + asserted_at site resolves; every relates_to link resolves;
    every claim carries a contradiction predicate; kind ∈ taxonomy + a distinction names two poles; every
    claim is asserted at ≥1 site or flagged implicit; statement within the word cap). The SEMANTIC
    contradiction check is a review-gate judgment-audit, NOT walked here (DESIGN §4.2). Keyed off
    `book-models/claims.json` + `claims_declared.json` + the outline + sibling models."""
    import claims_model as clm  # noqa: E402 — path set above; the book-model package

    issues: list[str] = []

    # C7-drift — the stored artifact equals a fresh derivation.
    fresh = clm.to_jsonable()
    stored = clm.load_artifact()
    if stored is None:
        issues.append(f"{rel(clm._ARTIFACT)} missing — run "
                      f"`python3 book-models/claims_model.py regenerate`")
    elif stored.get("claims") != fresh["claims"] or stored.get("_counts") != fresh["_counts"]:
        issues.append(f"DRIFT: {rel(clm._ARTIFACT)} disagrees with a fresh derivation — regenerate "
                      f"with `python3 book-models/claims_model.py regenerate`")

    # C1-C6 — structural / schema invariants (site + link resolution, contradiction predicate, kind + pole
    # shape, assertion coverage, word cap).
    issues.extend(clm.structural_findings())

    # Audit-only: same non-gating contract as the sibling view checks — surfaced as [audt], excluded from
    # the fail tally. A follow-up promotes C1-C6 + freshness to blocking once a clean session confirms the
    # seed drains to 0; the watch-phrase lint (C7) stays audit-only forever (DESIGN §4.2).
    return (FAIL if issues else PASS), issues


def check_argument_spine():
    """The argument-spine view's drift + structural check (audit-only first landing). Re-derives the spine
    model from the hand-authored `argument_spine_declared.json` and reports: AS1-drift against the on-disk
    artifact; AS2–AS7 the structural / schema invariants (spine size + order + word cap; every `reconciles`
    link resolves against the claims + big-ideas siblings AND the reconciliation is complete both ways;
    chapter labeling exhaustive over the outline's chapters; every advanced id resolves; exemption reasons
    in the closed enum). The FOCUS flags (a non-exempt chapter advancing 0 or >3 spine claims) are the
    artifact's `flags` block — editorial worklist, deliberately NOT findings here. Keyed off
    `book-models/argument-spine.json` + `argument_spine_declared.json` + the outline + sibling models."""
    import argument_spine_model as asm  # noqa: E402 — path set above; the book-model package

    issues: list[str] = []

    # AS1-drift — the stored artifact equals a fresh derivation.
    fresh = asm.to_jsonable()
    stored = asm.load_artifact()
    if stored is None:
        issues.append(f"{rel(asm._ARTIFACT)} missing — run "
                      f"`python3 book-models/argument_spine_model.py regenerate`")
    elif any(stored.get(k) != fresh[k] for k in ("spine", "chapters", "flags", "_counts")):
        issues.append(f"DRIFT: {rel(asm._ARTIFACT)} disagrees with a fresh derivation — regenerate "
                      f"with `python3 book-models/argument_spine_model.py regenerate`")

    # AS2–AS7 — structural / schema invariants.
    issues.extend(asm.structural_findings())

    # Audit-only: same non-gating contract as the sibling first landings — surfaced as [audt], excluded
    # from the fail tally. A follow-up promotes AS1–AS7 to blocking after a clean session (the claims
    # model's own landing path); the focus flags never gate.
    return (FAIL if issues else PASS), issues


def check_reverse_index():
    """The reverse index's two-kind drift check (audit-only). The reverse index inverts every built view's
    forward references into `{md symbol -> [dependent view elements]}`; it re-derives from the views each
    run, so it cannot itself drift — but its two mechanical drift kinds are checked here:

      - FRESHNESS — the materialized `book-models/reverse_index.json` equals a fresh inversion. A view
        edited without regenerating the index is the finding.
      - STRUCTURAL — every view->md reference resolves against the CURRENT source. A dangling section id /
        chapter / part a view points at (that the book no longer defines) is the finding. The reverse
        index makes this one walk over the inverted edges.

    Keyed off `book-models/reverse_index.json` + the built views + the book prose (via book_ir)."""
    import reverse_index as ri  # noqa: E402 — path set above; the book-model package

    issues: list[str] = []

    # FRESHNESS — the stored artifact equals a fresh inversion.
    fresh = ri.to_jsonable()
    stored = ri.load_artifact()
    if stored is None:
        issues.append(f"{rel(ri._ARTIFACT)} missing — run "
                      f"`python3 book-models/reverse_index.py regenerate`")
    elif stored.get("index") != fresh["index"] or stored.get("_counts") != fresh["_counts"]:
        issues.append(f"DRIFT: {rel(ri._ARTIFACT)} disagrees with a fresh inversion from the views — "
                      f"regenerate with `python3 book-models/reverse_index.py regenerate`")

    # STRUCTURAL — every view->md reference resolves against the current source.
    issues.extend(ri.structural_findings())

    # Audit-only: same non-gating contract as the sibling view checks — surfaced as [audt].
    return (FAIL if issues else PASS), issues
