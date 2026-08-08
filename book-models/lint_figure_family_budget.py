"""LINT `figure-family-budget` — the figure colour-LANGUAGE consistency gate (a coarse projection of INV-SEM).

The figures have quietly grown a colour vocabulary: green = modeling, rust = governance, blue = agent,
gray = neutral, red = failure (the `figure_semantics` block in design-tokens.json). Readers start reading
the colours as meaning, so the colours must stay relentlessly consistent — a governance-rust element must
never leak into an all-green modeling figure.

A lint cannot check "this rect, which DEPICTS a model, is green" — an SVG `<rect fill="#1f7a4d"/>` carries
no role, so intent is unreadable. But it CAN check the coarser, still-real guarantee: which colour FAMILIES
a whole figure is allowed to use, declared once in a header marker the author writes:

    <!-- semantic-families: modeling, neutral -->

The lint then asserts every family-owned hex in that SVG belongs to a DECLARED family — i.e.
`family_of_hex(hex) ∈ declared ∪ {None}`. Supporting neutrals (ink/paper/rule) and non-family colours map
to None and are ignored here (the sibling design-token-drift lint holds palette MEMBERSHIP). So an accidental
agent-blue leaking into the all-green Representation Ladder is caught deterministically, at one comment per
figure — the "relentless consistency" cost is a single declaration, not a per-element annotation.

Findings (per SVG):
  1. UNDECLARED — the figure uses a family hex but declares NO `semantic-families` header at all (so nothing
     scopes its palette). Every figure that uses a role colour should declare its budget.
  2. OUT-OF-BUDGET — a family hex whose family is not in the figure's declared set (the leak this exists to
     catch).
  3. BAD-FAMILY — the header names a token that is not one of the five families (a typo guard).

LANDS AUDIT-ONLY-FIRST (the repo's blocking-lint landing discipline): the corpus predates the header
convention, so most figures are UNDECLARED today. It PRINTS its findings and exits 0, so it never reddens an
in-flight commit; a figure-wiring wave adds the `semantic-families` headers, drains this to 0, and a follow-up
flips `--strict` (exit 1 on any finding) — the audit->drain->promote move.

Scan root: book/assets/*.svg (the same root the design-token-drift lint scans). The 8 redrawn figures live
in book/_design/drafts/figures-redraw/ until the wiring wave promotes them; widen SCAN_DIRS then if needed.

Run `python3 book-models/lint_figure_family_budget.py` to see the findings (audit-only, exit 0).
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_tokens as dtk  # noqa: E402 — the projector owns the family model this lint reads

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "book" / "assets"

_HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
# `<!-- semantic-families: modeling, neutral -->` — comma/space separated family names.
_HEADER_RE = re.compile(r"<!--\s*semantic-families:\s*(?P<list>[^>]*?)\s*-->")


def _declared_families(text: str) -> frozenset[str] | None:
    """The family set declared in the SVG's `semantic-families` header, or None if no header is present.
    None (undeclared) is distinct from an empty set (`<!-- semantic-families: -->`, declared-but-none)."""
    m = _HEADER_RE.search(text)
    if m is None:
        return None
    names = [p.strip() for p in re.split(r"[,\s]+", m.group("list")) if p.strip()]
    return frozenset(names)


def findings() -> list[str]:
    out: list[str] = []
    valid = dtk.semantic_families()
    for svg in sorted(ASSETS.glob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        declared = _declared_families(text)
        # Which families does the figure actually use (by hex)?
        used = {fam for hx in _HEX_RE.findall(text) if (fam := dtk.family_of_hex(hx)) is not None}
        if not used:
            continue  # a figure with no role colours needs no budget
        if declared is None:
            out.append(f"UNDECLARED {svg.name} — uses families {sorted(used)} but declares no "
                       f"'<!-- semantic-families: … -->' header")
            continue
        for bad in sorted(declared - valid):
            out.append(f"BAD-FAMILY {svg.name} — header names {bad!r}, not one of {sorted(valid)}")
        for leaked in sorted(used - declared):
            out.append(f"OUT-OF-BUDGET {svg.name} — uses {leaked!r} colour but only declares "
                       f"{sorted(declared)} (declare it, or re-colour the element)")
    return out


def summary_line(fs: list[str]) -> str:
    return f"{len(fs)} figure-family-budget finding(s)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding (the post-drain flip)")
    args = ap.parse_args(argv)
    fs = findings()
    mode = "STRICT (exit 1 on any finding)" if args.strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== figure-family-budget — declared colour families ⊇ used families per figure [{mode}] ==")
    if not fs:
        print("  clean — every figure using role colours declares them, and uses only declared families")
        return 0
    print(f"  {len(fs)} finding(s):")
    for f in fs:
        print(f"    {f}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
