"""LINT `brick-metadata` — every catalogue mechanism carries a curated Appendix-C applicability AND
primary-concern call, and the two curated models agree with the census.

The Appendix-C brick chip line (`Family · Primary-concern · Enforcement · Applicability`) spends two of its
four facets on CURATED judgment: `applicability` (essential / specialized, in `brick-applicability.json`) and
`primary_concern` (the cross-cutting organizer, in `brick-metadata.json`). Family and enforcement are DERIVED
(the entry path + the INDEX Enf. column), so they cannot go missing; the two curated facets can. A new
catalogue entry that ships without an applicability or a concern call would render a `—` chip and quietly lose
its place in the reader's mental organization.

This sensor makes that mechanical. It reads the census — every entry under `agent/` · `models-bridge/` ·
`product/` — and asserts each slug appears in BOTH curated models, and that neither model names a slug the
census does not (a typo, or an entry that was renamed). It also holds the design invariant that keeps the
technique/instance overlay clean: `domain_specific ⊂ specialized` — a document-accessibility instance is
domain-triggered by definition, so it can never be marked essential.

LANDING: BLOCKING in `catalog.py validate`. Both models were authored complete (all 83 slugs), so the tree is
green from birth; a new entry that omits either call, or a mismatched slug, reddens validate.

    python3 book-models/lint_brick_metadata.py            # print findings (exit 1 on any)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
_ROLE_DIRS = ("agent", "models-bridge", "product")
_APPLICABILITY = HERE / "brick-applicability.json"
_METADATA = HERE / "brick-metadata.json"
_VALID_APPLICABILITY = ("essential", "specialized")


@dataclass(frozen=True)
class Finding:
    slug: str
    problem: str


def _census_slugs() -> set[str]:
    """Every catalogue entry slug — one per `<role>/<family>/<slug>.md`, excluding the family READMEs."""
    out: set[str] = set()
    for role in _ROLE_DIRS:
        for p in (ROOT / role).glob("*/*.md"):
            if p.name == "README.md":
                continue
            out.add(p.stem)
    return out


def _applicability() -> dict[str, str]:
    if not _APPLICABILITY.is_file():
        return {}
    data = json.loads(_APPLICABILITY.read_text(encoding="utf-8"))
    return {s: (r or {}).get("applicability", "") for s, r in data.get("applicability", {}).items()}


def _metadata() -> dict:
    if not _METADATA.is_file():
        return {}
    return json.loads(_METADATA.read_text(encoding="utf-8"))


def findings() -> list[Finding]:
    census = _census_slugs()
    applic = _applicability()
    meta = _metadata()
    concern = meta.get("primary_concern", {})
    domain_specific = set(meta.get("domain_specific", []))
    out: list[Finding] = []

    for slug in sorted(census):
        if slug not in applic:
            out.append(Finding(slug, "no applicability call in brick-applicability.json"))
        if slug not in concern:
            out.append(Finding(slug, "no primary_concern call in brick-metadata.json"))
    for slug in sorted(set(applic) - census):
        out.append(Finding(slug, "in brick-applicability.json but names no catalogue entry"))
    for slug in sorted(set(concern) - census):
        out.append(Finding(slug, "in brick-metadata.json primary_concern but names no catalogue entry"))
    for slug in sorted(applic):
        if applic[slug] not in _VALID_APPLICABILITY:
            out.append(Finding(slug, f"applicability {applic[slug]!r} not in {_VALID_APPLICABILITY}"))
    # The design invariant: domain_specific ⊂ specialized (never essential; never a phantom slug).
    for slug in sorted(domain_specific):
        if slug not in census:
            out.append(Finding(slug, "in domain_specific but names no catalogue entry"))
        elif applic.get(slug) != "specialized":
            out.append(Finding(slug, "marked domain_specific but is not specialized (invariant: "
                                     "domain_specific ⊂ specialized)"))
    return out


def summary_line(fs: list[Finding]) -> str:
    return f"{len(fs)} brick-metadata finding(s) — every mechanism needs an applicability + concern call"


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    fs = findings()
    print("== brick-metadata — applicability + primary-concern completeness/agreement [BLOCKING] ==")
    if not fs:
        print("  clean — every catalogue mechanism carries an applicability + concern call; models agree")
        return 0
    print(f"  {summary_line(fs)}:")
    for f in sorted(fs, key=lambda x: (x.slug, x.problem)):
        print(f"    {f.slug}: {f.problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
