"""Drift checks for the book's typed 4+1 view-models (`book-models/`).

The book preaches (Part 3) that every view is a typed model held equal to the source by a build-time drift
check — derived, never snapshotted. This module dogfoods that on the book itself: it re-derives each
view-model from the book via `book-models/` (over `book_ir`) and fails on divergence.

CURRENTLY IMPLEMENTED — the OUTLINE view (the PoC; DESIGN §2.1):
  - O1 (drift): the materialized `book-models/outline.json` equals a fresh derivation from the book. A
    heading added / removed / renumbered / re-anchored without regenerating the artifact is a finding.
  - O2/O3/O4 (invariants): every section has a topic sentence; section ids are unique per chapter; heading
    nesting is well-formed. Walked by `outline_model.invariant_findings`.

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
