"""The SUBSTANTIATION aggregator — nests the DATA ledger and the LITERATURE positioning UNDER the argument
spine and, per claim, surfaces what backs it. The query the author asked for: "where we cite in the text,
back those cites in the model (ref, claims-from-it), nested under the spine, so we can query for
under-substantiated-or-situated claims about reality."

It reads THREE meta-files at query time (rule-#33 best form — stable, no codegen, no snapshot):
  - book-models/argument_spine_declared.json — the spine claims + their `quantifiable` / `reality_claim`
    flags (a claim that asserts something about reality, vs a definitional or normative one).
  - book/data/data-claims.json — the metric->claim ledger (each datum's `spine_claim`/`spine_claims` +
    observable + data_source + limitation). This is the DATA half.
  - book-models/lit-positioning.json — the literature-positioning citations, each `{key, backs_claims,
    relation}`. This is the LITERATURE half. Robust to its absence (data-only + a note), so W-LEDGER does
    not hard-depend on the LPP-MODEL ordering.

Per spine claim it aggregates `data_backing` (the data-claims bound to it) + `literature_backing` (the
citations whose `backs_claims` include it), then computes two reports:
  - DL3 UNDERQUANTIFIED — a `quantifiable:true` claim with ZERO data_backing (the author's "which
    quantifiable claims are underquantified" surface — seeds future collection).
  - UNDER-SUBSTANTIATED-OR-SITUATED — a `reality_claim:true` claim with ZERO data_backing AND ZERO
    literature_backing (an empirical/positioned claim with no evidence of any kind — the broader gap).
Both REPORT, never gate.

Run `python3 book-models/substantiation.py` to print the per-claim backing + the two reports; `... json`
for the machine form. Also the engine behind `catalog.py substantiation`.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_SPINE_DECLARED = os.path.join(_HERE, "argument_spine_declared.json")
_LIT_POSITIONING = os.path.join(_HERE, "lit-positioning.json")
_DATA_CLAIMS = os.path.join(_ROOT, "book", "data", "data-claims.json")


# ---- typed rows ------------------------------------------------------------------------------------

@dataclass
class DataBacking:
    slug: str
    status: str
    observable: str
    data_source: str
    limitation: str


@dataclass
class LiteratureBacking:
    key: str
    relation: str
    section: str


@dataclass
class ClaimSubstantiation:
    id: str
    statement: str
    quantifiable: bool
    reality_claim: bool
    data_backing: list[DataBacking] = field(default_factory=list)
    literature_backing: list[LiteratureBacking] = field(default_factory=list)

    @property
    def underquantified(self) -> bool:
        """DL3 — a quantifiable claim no metric yet bears weight for."""
        return self.quantifiable and not self.data_backing

    @property
    def under_substantiated(self) -> bool:
        """A reality-claim with neither data nor literature behind it — the broader gap."""
        return self.reality_claim and not self.data_backing and not self.literature_backing


# ---- load the three meta-files ---------------------------------------------------------------------

def _load(path: str) -> "dict | None":
    return json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else None


def _spine_claims() -> "list[dict]":
    data = _load(_SPINE_DECLARED) or {}
    return data.get("spine", [])


def _data_bindings() -> "dict[str, list[DataBacking]]":
    """claim id -> the data-claims bound to it. A datum binds via `spine_claim` (str) or `spine_claims`
    (list); both are read and unioned so a datum bearing weight for several claims reaches each."""
    raw = _load(_DATA_CLAIMS) or {}
    out: "dict[str, list[DataBacking]]" = {}
    for slug, e in raw.items():
        if slug.startswith("_") or not isinstance(e, dict):
            continue
        ids: "list[str]" = []
        if e.get("spine_claim"):
            ids.append(e["spine_claim"])
        ids.extend(e.get("spine_claims", []) or [])
        for cid in dict.fromkeys(ids):  # de-dup, keep order
            out.setdefault(cid, []).append(DataBacking(
                slug=slug, status=e.get("status", "?"),
                observable=e.get("observable", ""), data_source=e.get("data_source", ""),
                limitation=e.get("limitation", ""),
            ))
    return out


def _lit_bindings() -> "tuple[dict[str, list[LiteratureBacking]], bool]":
    """(claim id -> the citations that back it, lit_present). Reads lit-positioning.json; robust to its
    absence — returns ({}, False) so the aggregator degrades to data-only with a note."""
    art = _load(_LIT_POSITIONING)
    if art is None:
        return {}, False
    out: "dict[str, list[LiteratureBacking]]" = {}
    for iv in art.get("interventions", []):
        section = iv.get("section", "")
        for c in iv.get("citations", []):
            for cid in c.get("backs_claims", []):
                out.setdefault(cid, []).append(LiteratureBacking(
                    key=c.get("key", ""), relation=c.get("relation", ""), section=section,
                ))
    return out, True


# ---- aggregate -------------------------------------------------------------------------------------

def aggregate() -> "tuple[list[ClaimSubstantiation], bool]":
    """(per-claim substantiation in spine order, lit_present). The nest-under-the-spine query surface."""
    data_by_claim = _data_bindings()
    lit_by_claim, lit_present = _lit_bindings()
    rows: "list[ClaimSubstantiation]" = []
    for c in sorted(_spine_claims(), key=lambda d: d.get("order", 0)):
        rows.append(ClaimSubstantiation(
            id=c["id"], statement=c.get("statement", ""),
            quantifiable=bool(c.get("quantifiable", False)),
            reality_claim=bool(c.get("reality_claim", False)),
            data_backing=data_by_claim.get(c["id"], []),
            literature_backing=lit_by_claim.get(c["id"], []),
        ))
    return rows, lit_present


def dl_findings() -> "list[str]":
    """DL1 (join-integrity) + DL2 (four-fields-present) over the data-claims — the structural half the
    extended check_data_claims surfaces. DL1: every datum's spine_claim(s) resolve to a real spine claim.
    DL2: every datum carries non-empty observable + data_source + limitation. Deterministic; audit-only."""
    spine_ids = {c["id"] for c in _spine_claims()}
    raw = _load(_DATA_CLAIMS) or {}
    findings: "list[str]" = []
    for slug, e in raw.items():
        if slug.startswith("_") or not isinstance(e, dict):
            continue
        ids: "list[str]" = ([e["spine_claim"]] if e.get("spine_claim") else []) + list(e.get("spine_claims", []) or [])
        if not ids:
            findings.append(f"DL1 data-claim {slug!r} binds to no spine_claim (add spine_claim or spine_claims)")
        for cid in ids:
            if cid not in spine_ids:
                findings.append(f"DL1 data-claim {slug!r} spine_claim {cid!r} resolves to no spine claim")
        for f_name in ("observable", "data_source", "limitation"):
            if not str(e.get(f_name, "")).strip():
                findings.append(f"DL2 data-claim {slug!r} has an empty {f_name!r} field")
    return findings


def underquantified() -> "list[ClaimSubstantiation]":
    rows, _ = aggregate()
    return [r for r in rows if r.underquantified]


def under_substantiated() -> "list[ClaimSubstantiation]":
    rows, _ = aggregate()
    return [r for r in rows if r.under_substantiated]


# ---- CLI -------------------------------------------------------------------------------------------

def _flag_tag(r: "ClaimSubstantiation") -> str:
    tags = []
    if r.under_substantiated:
        tags.append("UNDER-SUBSTANTIATED-OR-SITUATED")
    elif r.underquantified:
        tags.append("UNDERQUANTIFIED")
    if r.reality_claim:
        tags.append("reality")
    if r.quantifiable:
        tags.append("quantifiable")
    return f"  [{'; '.join(tags)}]" if tags else ""


def _to_jsonable() -> dict:
    rows, lit_present = aggregate()
    from dataclasses import asdict
    return {
        "_note": ("Substantiation aggregate — data-claims + lit-positioning citations nested under each "
                  "argument-spine claim. UNDERQUANTIFIED = quantifiable claim with no data; "
                  "UNDER-SUBSTANTIATED-OR-SITUATED = reality-claim with neither data nor literature. Reports."),
        "lit_positioning_present": lit_present,
        "claims": [{**asdict(r), "underquantified": r.underquantified,
                    "under_substantiated": r.under_substantiated} for r in rows],
        "underquantified": [r.id for r in rows if r.underquantified],
        "under_substantiated_or_situated": [r.id for r in rows if r.under_substantiated],
    }


def render(as_json: bool = False) -> int:
    rows, lit_present = aggregate()
    if as_json:
        print(json.dumps(_to_jsonable(), ensure_ascii=False, indent=2))
        return 0
    print("== substantiation — data + literature nested under the argument spine ==")
    if not lit_present:
        print("  (note: book-models/lit-positioning.json absent — literature half empty; run the "
              "lit_positioning model's regenerate)")
    for r in rows:
        print(f"\n{r.id}{_flag_tag(r)}")
        print(f"  {r.statement}")
        if r.data_backing:
            for d in r.data_backing:
                print(f"  data: {d.slug} [{d.status}] — {d.observable}")
        else:
            print("  data: — none")
        if r.literature_backing:
            keys = ", ".join(f"{l.key}({l.relation})" for l in r.literature_backing)
            print(f"  lit:  {keys}")
        else:
            print("  lit:  — none")
    uq = [r for r in rows if r.underquantified]
    us = [r for r in rows if r.under_substantiated]
    print("\n== DL3 UNDERQUANTIFIED (quantifiable claim, no data yet — seeds future collection) ==")
    print("  " + (", ".join(r.id for r in uq) if uq else "none — every quantifiable claim has bound data"))
    print("== UNDER-SUBSTANTIATED-OR-SITUATED (reality-claim with neither data nor literature) ==")
    print("  " + (", ".join(r.id for r in us) if us
                  else "none — every reality-claim has data or literature behind it"))
    return 0


def main(argv: "list[str]") -> int:
    if len(argv) > 1 and argv[1] == "json":
        return render(as_json=True)
    return render(as_json=False)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
