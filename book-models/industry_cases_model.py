"""The INDUSTRY-CASES model — the book's external-evidence base as a queryable, drift-gated MODEL rather than
prose accumulated ad hoc. A sibling of the other declared -> generated book models (theory-of-mage /
metrics-dashboard): the hand-authored source of truth is `book-models/industry_cases_declared.json`; this
module derives a typed model over it, projects the DocAble+authored correspondence MATRIX, exposes the live
queries the volume unlocks, and holds the joins IC1-IC6 (status-aware).

ONE SOURCE, MANY CONSUMERS.
  - `render_matrix_md()` — the projected correspondence matrix: a fixed DocAble ROW 0 (the book's own case,
    hand-declared `strong` across the construct universe it induced) followed by `status == authored` rows
    only (Cloudflare now). Columns are the DECLARED, ORDERED construct universe (REVISE-3), so a new CASE is
    append-a-row and never widens the grid. A stub never renders as a blank matrix row — stubs live in the
    roster and surface through the coverage / only-docable / roster queries.
  - The live queries — `constructs` (invert the matrix: per construct, the external cases observing it and at
    what strength) · `bears-on <H>` (authored cases whose hypotheses[] contains the H-id) · `only-docable`
    (the GAP query: constructs / hypotheses with no EXTERNAL case at strength >= partial — this names the
    empty columns and drives which pending site to write first) · `coverage` (the burndown: N authored vs N
    roster, distinct constructs with >=1 external observation, the independence/scale/domain spread) ·
    `roster` (the declared six-site intent + status).
  - `all_findings()` — the joins IC1-IC6 + the audit-only IC7 scale-fact presence. STATUS-AWARE: a stub
    (`status == pending-writeup`) is checked only for id/organization/domain/distinctive_starting_point; an
    authored record is checked fully (citation join, enums, correspondence + descriptive vocabs). IC5 matrix
    parity is VACUOUS this wave — the matrix is not yet authored into any chapter page (the prose wave places
    it), so there is nothing to hold byte-equal.

LANDING: the whole model lands AUDIT-ONLY-first (rule-#55 blocking-lint discipline) — the `[industry]` band
in `catalog.py validate` PRINTS its findings + the coverage note but does NOT increment the issue count; a
follow-up flips IC1-IC6 to BLOCKING once a clean session confirms the drain, the path every book model took.
NO materialized `industry-cases.json` (REVISE-2): the queries and the matrix compute live from the declared
source at CLI time — page-parity + compute-at-CLI only.

Run `python3 book-models/industry_cases_model.py verify` to drift-check; `... matrix` to print the matrix for
a page; `... constructs` / `... bears-on H3-mechanized-assurance` / `... only-docable` / `... coverage` /
`... roster` for the live queries; `... show` to list every case.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_BOOK = os.path.join(_ROOT, "book")
_DECLARED = os.path.join(_HERE, "industry_cases_declared.json")
_REFERENCES_BIB = os.path.join(_BOOK, "references.bib")
_CITATIONS_JSON = os.path.join(_BOOK, "data", "citations.json")
_THEORY_DECLARED = os.path.join(_HERE, "theory_of_mage_declared.json")

#: The status enum. A `pending-writeup` stub carries only the roster fields; `authored` records are checked
#: fully (the status-aware schema split, IC1).
_STATUS_AUTHORED = "authored"
_STATUS_PENDING = "pending-writeup"
_VALID_STATUS = (_STATUS_AUTHORED, _STATUS_PENDING)

#: The correspondence strengths at or above `partial` — the coverage threshold the gap query (`only-docable`)
#: reads: a construct/hypothesis is "still only DocAble" when no EXTERNAL case rates it here.
_AT_LEAST_PARTIAL = ("strong", "partial")

#: The roster fields a stub (and a roster entry) carries — the status-aware minimum (IC1).
_ROSTER_FIELDS = ("id", "organization", "domain", "distinctive_starting_point", "status")

#: The matrix header stem (the Case column, then the declared construct-universe labels appended in order).
_CASE_COL = "Case"


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class ConstructCell:
    """One correspondence cell on a case's matrix row — a construct id + its strength + the per-cell note
    (the book's reading, so the cell is auditable, not silent)."""
    construct: str
    strength: str
    note: str


@dataclass
class Column:
    """One declared construct-universe column — the stable, ordered projection axis (REVISE-3)."""
    id: str
    label: str
    provenance: str


@dataclass
class RosterEntry:
    """One declared roster site — the intent block the count guard (IC6) derives from."""
    id: str
    organization: str
    domain: str
    distinctive_starting_point: str
    status: str


@dataclass
class IndustryCase:
    """One case record. A `pending-writeup` stub carries only the roster fields (the rest default empty); an
    `authored` record carries the full source / setting / descriptive / correspondence payload."""
    id: str
    organization: str
    domain: str
    distinctive_starting_point: str
    status: str
    source: dict = field(default_factory=dict)
    setting: dict = field(default_factory=dict)
    representations: "list[str]" = field(default_factory=list)
    object_territory: "list[str]" = field(default_factory=list)
    mechanisms: "list[str]" = field(default_factory=list)
    judgment: dict = field(default_factory=dict)
    mage_constructs: "list[ConstructCell]" = field(default_factory=list)
    hypotheses: "list[str]" = field(default_factory=list)
    scale_facts: "list[str]" = field(default_factory=list)
    result_sentence: str = ""

    @property
    def authored(self) -> bool:
        return self.status == _STATUS_AUTHORED

    def strength_of(self, construct_id: str) -> "str | None":
        for c in self.mage_constructs:
            if c.construct == construct_id:
                return c.strength
        return None


@dataclass
class IndustryCasesModel:
    columns: "list[Column]"
    docable_cells: "dict[str, str]"
    docable_org: str
    roster: "list[RosterEntry]"
    cases: "list[IndustryCase]"

    def authored(self) -> "list[IndustryCase]":
        """External authored cases in declared order (excludes DocAble, which is the fixed row 0, and stubs)."""
        return [c for c in self.cases if c.authored]

    def column_ids(self) -> "list[str]":
        return [col.id for col in self.columns]


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def derive_model(raw: "dict | None" = None) -> IndustryCasesModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and
    the checks and the queries share."""
    if raw is None:
        raw = _load_declared()
    columns = [
        Column(id=c.get("id", ""), label=c.get("label", ""), provenance=c.get("provenance", ""))
        for c in raw.get("construct_universe", {}).get("columns", [])
    ]
    docable = raw.get("docable_row", {})
    roster = [
        RosterEntry(
            id=s.get("id", ""), organization=s.get("organization", ""), domain=s.get("domain", ""),
            distinctive_starting_point=s.get("distinctive_starting_point", ""), status=s.get("status", ""),
        )
        for s in raw.get("roster", {}).get("sites", [])
    ]
    cases: "list[IndustryCase]" = []
    for c in raw.get("industry_cases", []):
        cells = [
            ConstructCell(construct=mc.get("construct", ""), strength=mc.get("strength", ""),
                          note=mc.get("note", ""))
            for mc in c.get("mage_constructs", [])
        ]
        cases.append(IndustryCase(
            id=c.get("id", ""), organization=c.get("organization", ""), domain=c.get("domain", ""),
            distinctive_starting_point=c.get("distinctive_starting_point", ""), status=c.get("status", ""),
            source=c.get("source", {}) or {}, setting=c.get("setting", {}) or {},
            representations=list(c.get("representations", []) or []),
            object_territory=list(c.get("object_territory", []) or []),
            mechanisms=list(c.get("mechanisms", []) or []), judgment=c.get("judgment", {}) or {},
            mage_constructs=cells, hypotheses=list(c.get("hypotheses", []) or []),
            scale_facts=list((c.get("setting", {}) or {}).get("scale_facts", []) or []),
            result_sentence=c.get("result_sentence", ""),
        ))
    return IndustryCasesModel(
        columns=columns, docable_cells=dict(docable.get("cells", {})),
        docable_org=docable.get("organization", "DocAble"), roster=roster, cases=cases,
    )


# ---- external join sources --------------------------------------------------------------------------

def _bib_keys() -> "set[str]":
    """The citation keys declared in references.bib — a `@type{key,` scan (the print bib is the source of
    truth the citations.json mirror is generated from)."""
    if not os.path.exists(_REFERENCES_BIB):
        return set()
    with open(_REFERENCES_BIB, encoding="utf-8") as fh:
        text = fh.read()
    return set(re.findall(r"@\w+\{\s*([^,\s]+)\s*,", text))


def _citation_keys() -> "set[str]":
    """The keys in the generated web citation mirror (book/data/citations.json)."""
    if not os.path.exists(_CITATIONS_JSON):
        return set()
    with open(_CITATIONS_JSON, encoding="utf-8") as fh:
        data = json.load(fh)
    return set(data.get("citations", {}).keys())


def _hypothesis_ids() -> "set[str]":
    """Every hypothesis id (top-level + sub) declared in the theory model — the IC4 join universe."""
    if not os.path.exists(_THEORY_DECLARED):
        return set()
    with open(_THEORY_DECLARED, encoding="utf-8") as fh:
        raw = json.load(fh)
    ids: "set[str]" = set()
    for h in raw.get("hypotheses", []):
        if h.get("id"):
            ids.add(h["id"])
        for sh in h.get("sub_hypotheses", []) or []:
            if sh.get("id"):
                ids.add(sh["id"])
    return ids


# ---- projection: the correspondence matrix ----------------------------------------------------------

def _header_line(model: IndustryCasesModel) -> str:
    return "| " + " | ".join([_CASE_COL, *[c.label for c in model.columns]]) + " |"


def _matrix_cell(strength: "str | None") -> str:
    """A matrix cell — the correspondence strength where the case lists the construct, else an em-dash."""
    return strength if strength else "—"


def render_matrix_rows(model: "IndustryCasesModel | None" = None) -> "list[str]":
    """The DocAble row 0 + one row per `status == authored` external case, projected against the fixed,
    ordered construct-universe columns (no header)."""
    if model is None:
        model = derive_model()
    col_ids = model.column_ids()

    def render(org: str, cell_for) -> str:
        return "| " + " | ".join([f"**{org}**", *[_matrix_cell(cell_for(cid)) for cid in col_ids]]) + " |"

    rows = [render(model.docable_org, lambda cid: model.docable_cells.get(cid))]
    for case in model.authored():
        rows.append(render(case.organization, case.strength_of))
    return rows


def render_matrix_md(model: "IndustryCasesModel | None" = None) -> str:
    """The full markdown matrix (header + rule + DocAble row 0 + authored rows) — the page carries exactly
    these when the prose wave authors it into a chapter."""
    if model is None:
        model = derive_model()
    header = _header_line(model)
    rule = "|" + "---|" * (len(model.columns) + 1)
    return "\n".join([header, rule, *render_matrix_rows(model)])


# ---- live queries ----------------------------------------------------------------------------------

def query_constructs(model: "IndustryCasesModel | None" = None) -> "dict[str, list[tuple[str, str]]]":
    """Invert the matrix across authored EXTERNAL cases: per construct id (in column order), the list of
    (organization, strength) observing it. Answers 'which constructs have external observation.'"""
    if model is None:
        model = derive_model()
    out: "dict[str, list[tuple[str, str]]]" = {cid: [] for cid in model.column_ids()}
    for case in model.authored():
        for cell in case.mage_constructs:
            if cell.construct in out:
                out[cell.construct].append((case.organization, cell.strength))
    return out


def query_bears_on(h_id: str, model: "IndustryCasesModel | None" = None) -> "list[str]":
    """Authored external cases whose hypotheses[] contains the H-id (read-only join to the theory model)."""
    if model is None:
        model = derive_model()
    return [c.organization for c in model.authored() if h_id in c.hypotheses]


def query_only_docable(model: "IndustryCasesModel | None" = None) -> "dict[str, list[str]]":
    """The GAP query. Returns the construct ids and the hypothesis ids for which NO external authored case
    reaches strength >= partial — the columns still resting on DocAble alone. This names the empty columns and
    drives which pending site to write first."""
    if model is None:
        model = derive_model()
    inverted = query_constructs(model)
    empty_constructs = [
        cid for cid in model.column_ids()
        if not any(strength in _AT_LEAST_PARTIAL for _org, strength in inverted.get(cid, []))
    ]
    covered_h = {h for c in model.authored() for h in c.hypotheses}
    empty_hyps = sorted(_hypothesis_ids() - covered_h)
    return {"constructs": empty_constructs, "hypotheses": empty_hyps}


def query_coverage(model: "IndustryCasesModel | None" = None) -> dict:
    """The burndown: N authored vs N roster, distinct constructs with >=1 external observation at any
    strength, and the independence / scale / domain spread (so an eventual synthesis can honestly gauge
    heterogeneity)."""
    if model is None:
        model = derive_model()
    inverted = query_constructs(model)
    observed = [cid for cid in model.column_ids() if inverted.get(cid)]
    authored = model.authored()
    return {
        "authored": len(authored),
        "roster": len(model.roster),
        "constructs_observed": len(observed),
        "constructs_total": len(model.columns),
        "independence_spread": sorted({c.source.get("independence", "?") for c in authored}),
        "scale_spread": sorted({c.setting.get("scale", "?") for c in authored}),
        "domain_spread": sorted({c.domain for c in authored}),
    }


# ---- invariants (IC1-IC7; status-aware) -------------------------------------------------------------

def structural_findings(model: "IndustryCasesModel | None" = None) -> "list[str]":
    """The joins IC1-IC4 + IC6 (status-aware) and the audit-only IC7. Each finding is a defect the gate
    should catch once this band is promoted to BLOCKING.

    IC1 schema/traceability — kebab-unique id; non-empty organization/domain; a `pending-writeup` stub needs
        ONLY id/organization/domain/distinctive_starting_point; an `authored` record additionally carries
        source.citation_key, in-range enums, every mage_constructs[].strength in the correspondence set, and
        every descriptive-vocab value in its closed set.
    IC2 citation join — an authored record's source.citation_key resolves in references.bib AND
        citations.json (stubs exempt).
    IC3 construct join — every mage_constructs[].construct resolves against the declared construct universe.
    IC4 hypothesis join — every hypotheses[] id resolves to a real theory hypothesis id.
    IC6 roster guard — the record id-set equals the roster id-set, and shared roster fields agree between the
        roster entry and the record.
    IC7 (audit-only) scale-fact presence — an authored scale-bearing case carries >=1 scale_facts.
    """
    if model is None:
        model = derive_model()
    raw = _load_declared()
    taxonomy = raw.get("_taxonomy", {})
    corr_set = {v["value"] for v in taxonomy.get("correspondence", [])}
    col_ids = set(model.column_ids())
    bib, cites, hyp_ids = _bib_keys(), _citation_keys(), _hypothesis_ids()

    findings: "list[str]" = []
    seen: "set[str]" = set()

    for case in model.cases:
        cid = case.id or "<empty-id>"
        # IC1 — id shape + uniqueness (every status).
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", case.id or ""):
            findings.append(f"IC1 case {cid!r} id is not kebab-case")
        if case.id in seen:
            findings.append(f"IC1 duplicate case id {case.id!r}")
        seen.add(case.id)
        if case.status not in _VALID_STATUS:
            findings.append(f"IC1 case {cid!r} status {case.status!r} is not one of {_VALID_STATUS}")
        for f_name, val in (("organization", case.organization), ("domain", case.domain),
                            ("distinctive_starting_point", case.distinctive_starting_point)):
            if not str(val).strip():
                findings.append(f"IC1 case {cid!r} has empty roster field {f_name!r}")

        if not case.authored:
            continue  # stubs are checked only for the roster minimum

        # IC2 — citation join (authored only).
        key = case.source.get("citation_key", "")
        if not key:
            findings.append(f"IC2 authored case {cid!r} has no source.citation_key")
        else:
            if key not in bib:
                findings.append(f"IC2 authored case {cid!r} citation_key {key!r} resolves in no references.bib entry")
            if key not in cites:
                findings.append(f"IC2 authored case {cid!r} citation_key {key!r} absent from citations.json (regen the mirror)")

        # IC1 — authored enums in range.
        for f_name, vocab_key in (("source_type", "source_type"), ("independence", "independence"),
                                  ("account_type", "account_type"), ("evidence_horizon", "evidence_horizon")):
            val = case.source.get(f_name, "")
            vocab = taxonomy.get(vocab_key, [])
            if val and vocab and val not in vocab:
                findings.append(f"IC1 authored case {cid!r} source.{f_name} {val!r} not in taxonomy {vocab_key}")
        scale = case.setting.get("scale", "")
        if scale and scale not in taxonomy.get("scale", []):
            findings.append(f"IC1 authored case {cid!r} setting.scale {scale!r} not in taxonomy scale")
        for cell_name, val in (case.judgment or {}).items():
            if val and val not in taxonomy.get("judgment_cell", []):
                findings.append(f"IC1 authored case {cid!r} judgment.{cell_name} {val!r} not in taxonomy judgment_cell")
        for vocab_key, values in (("representations", case.representations),
                                  ("mechanisms", case.mechanisms), ("object_territory", case.object_territory)):
            vocab = taxonomy.get(vocab_key, [])
            for v in values:
                if vocab and v not in vocab:
                    findings.append(f"IC1 authored case {cid!r} {vocab_key} value {v!r} not in taxonomy {vocab_key}")

        # IC1/IC3 — correspondence cells.
        for cell in case.mage_constructs:
            if corr_set and cell.strength not in corr_set:
                findings.append(f"IC1 authored case {cid!r} construct {cell.construct!r} strength {cell.strength!r} not in correspondence set")
            if cell.construct not in col_ids:
                findings.append(f"IC3 authored case {cid!r} construct {cell.construct!r} resolves against no declared construct-universe column")
            if not cell.note.strip():
                findings.append(f"IC1 authored case {cid!r} construct {cell.construct!r} carries no note (a cell must be auditable)")

        # IC4 — hypothesis join.
        for h in case.hypotheses:
            if hyp_ids and h not in hyp_ids:
                findings.append(f"IC4 authored case {cid!r} hypothesis {h!r} resolves to no theory hypothesis id")

        # IC7 (audit-only) — scale-fact presence.
        if scale and not case.scale_facts:
            findings.append(f"IC7 (audit-only) authored case {cid!r} is scale-bearing ({scale}) but carries no scale_facts")

    findings.extend(_roster_guard_findings(model, raw))
    return findings


def _roster_guard_findings(model: IndustryCasesModel, raw: dict) -> "list[str]":
    """IC6 — the record id-set equals the roster id-set (a silently added/dropped case reddens), and shared
    roster fields agree between the roster entry and its record (the declared-intent/record join)."""
    findings: "list[str]" = []
    roster_by_id = {r.id: r for r in model.roster}
    record_ids = {c.id for c in model.cases}
    roster_ids = set(roster_by_id)
    for missing in sorted(roster_ids - record_ids):
        findings.append(f"IC6 roster site {missing!r} has no matching case record")
    for extra in sorted(record_ids - roster_ids):
        findings.append(f"IC6 case record {extra!r} is not in the declared roster")
    for case in model.cases:
        r = roster_by_id.get(case.id)
        if not r:
            continue
        for f_name, rec_val, ros_val in (
            ("organization", case.organization, r.organization),
            ("domain", case.domain, r.domain),
            ("distinctive_starting_point", case.distinctive_starting_point, r.distinctive_starting_point),
            ("status", case.status, r.status),
        ):
            if rec_val != ros_val:
                findings.append(f"IC6 case {case.id!r} {f_name} disagrees with roster ({rec_val!r} != {ros_val!r})")
    return findings


def parity_findings(model: "IndustryCasesModel | None" = None) -> "list[str]":
    """IC5 matrix parity — VACUOUS this wave. The projected matrix is not yet authored into any chapter page
    (the prose wave places it), so there is nothing to hold byte-equal. When the matrix lands on a page, wire
    `page_block_parity(page, header_line, render_matrix_md().splitlines())` here, exactly as the theory and
    dashboard models do."""
    return []


def all_findings(model: "IndustryCasesModel | None" = None) -> "list[str]":
    """Structural (IC1-IC4 + IC6 + audit-only IC7) + parity (IC5, vacuous this wave). This whole band is wired
    AUDIT-ONLY-first (rule-#55): a follow-up promotes it to BLOCKING once a clean session confirms the drain."""
    if model is None:
        model = derive_model()
    return structural_findings(model) + parity_findings(model)


def coverage_note(model: "IndustryCasesModel | None" = None) -> str:
    """A one-line burndown for the validate band — N authored vs roster, constructs with external observation,
    and the still-only-DocAble gap count (the surface the volume unlocks)."""
    if model is None:
        model = derive_model()
    cov = query_coverage(model)
    gaps = query_only_docable(model)
    return (f"{cov['authored']}/{cov['roster']} sites authored · "
            f"{cov['constructs_observed']}/{cov['constructs_total']} constructs externally observed · "
            f"{len(gaps['constructs'])} construct(s) + {len(gaps['hypotheses'])} hypothesis(es) still only-DocAble")


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_matrix() -> int:
    print(render_matrix_md())
    return 0


def _cmd_constructs() -> int:
    model = derive_model()
    labels = {c.id: c.label for c in model.columns}
    for cid in model.column_ids():
        obs = query_constructs(model)[cid]
        rendered = ", ".join(f"{org} ({strength})" for org, strength in obs) if obs else "— (only DocAble)"
        print(f"{labels[cid]:<22} {rendered}")
    return 0


def _cmd_bears_on(h_id: str) -> int:
    orgs = query_bears_on(h_id)
    print(f"{h_id}: {', '.join(orgs) if orgs else '(no authored external case bears on this hypothesis)'}")
    return 0


def _cmd_only_docable() -> int:
    model = derive_model()
    gaps = query_only_docable(model)
    labels = {c.id: c.label for c in model.columns}
    print("only-DocAble constructs (no external case at strength >= partial — the columns to fill next):")
    if gaps["constructs"]:
        for cid in gaps["constructs"]:
            print(f"  {labels.get(cid, cid)}  ({cid})")
    else:
        print("  (none — every construct has external observation at >= partial)")
    print("only-DocAble hypotheses (no external case bears on them):")
    if gaps["hypotheses"]:
        for h in gaps["hypotheses"]:
            print(f"  {h}")
    else:
        print("  (none)")
    return 0


def _cmd_coverage() -> int:
    cov = query_coverage()
    print(coverage_note())
    print(f"  independence spread: {', '.join(cov['independence_spread']) or '—'}")
    print(f"  scale spread:        {', '.join(cov['scale_spread']) or '—'}")
    print(f"  domain spread:       {', '.join(cov['domain_spread']) or '—'}")
    return 0


def _cmd_roster() -> int:
    model = derive_model()
    for r in model.roster:
        print(f"[{r.status:>15}] {r.id:<16} {r.organization:<12} {r.domain}")
    print(f"\n{len(model.authored())}/{len(model.roster)} authored")
    return 0


def _cmd_show() -> int:
    model = derive_model()
    for c in model.cases:
        print(f"[{c.status:>15}] {c.id}  ({c.organization} — {c.domain})")
        if c.authored:
            for cell in c.mage_constructs:
                print(f"                  {cell.construct}: {cell.strength}")
    print(f"\n{len(model.cases)} records · {len(model.authored())} authored · {len(model.roster)} roster")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    print(f"industry-cases: {coverage_note(model)}")
    if findings:
        print(f"industry-cases: {len(findings)} finding(s) (AUDIT-ONLY this wave — does not gate validate):")
        for f in findings:
            print(f"  {f}")
        return 1
    print("industry-cases: schema + joins clean (IC1-IC4 + IC6; IC5 parity vacuous — matrix not yet on a page)")
    return 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "matrix":
        return _cmd_matrix()
    if cmd == "constructs":
        return _cmd_constructs()
    if cmd == "bears-on":
        if len(argv) < 3:
            print("usage: industry_cases_model.py bears-on <hypothesis-id>")
            return 2
        return _cmd_bears_on(argv[2])
    if cmd == "only-docable":
        return _cmd_only_docable()
    if cmd == "coverage":
        return _cmd_coverage()
    if cmd == "roster":
        return _cmd_roster()
    if cmd == "show":
        return _cmd_show()
    print(f"usage: {argv[0]} [verify|matrix|constructs|bears-on <H>|only-docable|coverage|roster|show]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
