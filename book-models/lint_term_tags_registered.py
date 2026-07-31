"""LINT `term-tags-registered` — every tagged term must resolve to a registered term, AND a section-terms
slug must carry the tier its role demands.

THE TWO-TIER TAGGING.  The drain tags concepts at two tiers: a `point`'s `terms:` segment names tier-2 LOCAL
terms a paragraph deploys; a `<!-- section-terms: <t1>, <t2> -->` marker names the tier-1 SECTION concepts a
section develops. The lint checks two things:

  1. REGISTRATION — every tagged slug (a point `terms:` entry OR a `section-terms:` entry) resolves to a
     REGISTERED term in the two-tier registry (`index-terms.md` §"Term tiers"), which carries the term's
     `tier` ∈ {section, local}. A tagged slug the registry does not know has no tier, so it is a finding.
  2. ROLE↔TIER — a slug in a `section-terms:` marker plays the tier-1 role, so it must resolve to tier
     `section`. A `local`-registered slug used there is a tier-role mismatch (`reverse_index.role_tier_findings`).
     Paragraph `terms:` slugs are unconstrained — a section concept may be reused at paragraph tier, and a
     local is expected there.

THE REGISTRY.  Reuses `index-terms.md` as the single term SSOT (no parallel registry): the 135 existing
`- concept:` slugs default to `tier: section`; an explicit `- term: <slug> | <tier>` row registers a new
local term or overrides a concept's default. The membership test lives in `reverse_index.term_findings()`
(the drift substrate); this script is its CLI face.

LANDS AUDIT-ONLY-FIRST.  It PRINTS findings and exits 0 (audit-only). Once the reform tags every point +
section against registered terms and any new local terms are added to the registry, a follow-up promotes it
to blocking.

Run `python3 book-models/lint_term_tags_registered.py` (audit-only, exit 0).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reverse_index as ri  # noqa: E402 — the term-tag drift substrate (term_findings) lives here


def findings() -> "list[str]":
    """Registration findings (a tagged slug not in the registry) PLUS role↔tier findings (a `section-terms:`
    slug registered `local`). Delegates to `reverse_index.term_findings()` + `reverse_index.role_tier_findings()`
    so both rules have ONE home (the drift substrate); this script is their CLI face."""
    return ri.term_findings() + ri.role_tier_findings()


def main(argv: "list[str]") -> int:
    strict = "--strict" in argv[1:]
    fs = findings()
    mode = "STRICT (exit 1 on any finding)" if strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== term-tags-registered — every tagged term registered; every section-terms slug tier `section` [{mode}] ==")
    if not fs:
        print("  clean — every tagged term is registered, and every section-terms slug carries tier `section`")
        return 0
    print(f"  {len(fs)} finding(s):")
    for f in fs:
        print(f"    {f}")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
