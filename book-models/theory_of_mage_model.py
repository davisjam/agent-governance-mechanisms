"""The THEORY-OF-MAGE projection model — the chapter's Seven-Hypotheses table PROJECTED from the declared
theory source, so the page and the model cannot drift. A sibling of the other declared -> generated book
models (metrics-dashboard / claims / spine): the hand-authored source of truth is
`book-models/theory_of_mage_declared.json`; this module derives a typed model over it, projects the
hypotheses table into the 'Toward a Theory of MAGE' chapter, and holds that page's table byte-equal to the
projection with a parity check.

ONE SOURCE, TWO CONSUMERS.
  - `render_hypotheses_table_md()` — the 3-column markdown table (`ID | Hypothesis | Key falsifier`) the
    chapter shows: one row per top-level hypothesis, and for a hypothesis that DECOMPOSES into
    `sub_hypotheses` (H4 -> H4a/H4b) the Hypothesis and Key-falsifier cells are composed from the sub-rows
    with a fixed, deterministic fold (so the two-sub-hypothesis cell reaches byte parity). Author the table
    into the page from `... hypotheses-table`; the page and the model cannot then diverge without the parity
    check reddening.
  - `all_findings()` — structural + parity + the ratified-count guard. The STRUCTURAL half delegates to the
    existing `theory_model_check.check()` (extract-on-second-site: do not re-implement the internal
    well-formedness invariants TM1-TM7). The PARITY half reuses the dashboard's contiguous-`|`-run extractor
    idiom. The COUNT guard (`EXPECT_HYPOTHESES` / `EXPECT_SUBHYP`) reddens on a silent add/drop/reclassify of
    a hypothesis or sub-hypothesis — the exact H-table drift the chapter fears.

Reads the meta-file at check-time (rule-#33 best form — stable, no codegen, no snapshot). AUDIT-ONLY: the
model itself never gates; `catalog.py validate` prints its `[theory]` findings without incrementing the
issue count until a follow-up flips it BLOCKING once a clean session confirms parity holds (the repo's
blocking-lint landing discipline).

Run `python3 book-models/theory_of_mage_model.py verify` to drift-check (structural + parity + count);
`... hypotheses-table` to print the markdown table for the page; `... show` to list every hypothesis.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

import theory_model_check as _tmc  # sibling in book-models/; the internal well-formedness check (TM1-TM7)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_BOOK = os.path.join(_ROOT, "book")
_DECLARED = os.path.join(_HERE, "theory_of_mage_declared.json")

#: The page the hypotheses table is authored into (parity target).
_PAGE_REL = os.path.join("backmatter", "6.0-toward-a-theory-of-mage.md")

#: The ratified counts — encode the author's set so a silent add/drop/reclassify reddens (the dashboard
#: model's C5-analogue: the count guard is the backstop against silent H-table drift).
EXPECT_HYPOTHESES = 7
EXPECT_SUBHYP = 2

#: The hypotheses-table columns (the header the projection emits and the page carries; parity is exact).
_COLUMNS = ("ID", "Hypothesis", "Key falsifier")
_TABLE_HEADER = "| " + " | ".join(_COLUMNS) + " |"
_TABLE_RULE = "|" + "---|" * len(_COLUMNS)

_EMDASH = "—"  # the chapter renders `**H1 — name**` with a real em-dash, spaced; reproduce it exactly


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class SubHypothesis:
    """A named hypothesis a parent decomposes into (H4a/H4b under H4)."""
    id: str
    name: str
    statement: str
    falsifier: str

    @property
    def short(self) -> str:
        return _short_id(self.id)


@dataclass
class Hypothesis:
    """One top-level falsifiable hypothesis. `sub_hypotheses` is non-empty only for a decomposed hypothesis
    (H4), whose Hypothesis/Key-falsifier cells are composed from the sub-rows rather than its own body."""
    id: str
    name: str
    statement: str
    falsifier: str
    sub_hypotheses: "list[SubHypothesis]"

    @property
    def short(self) -> str:
        return _short_id(self.id)


@dataclass
class TheoryModel:
    hypotheses: "list[Hypothesis]"

    def sub_count(self) -> int:
        return sum(len(h.sub_hypotheses) for h in self.hypotheses)


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def _short_id(full_id: str) -> str:
    """The short form the chapter uses — the leading token of the JSON id up to the first `-`
    (`H4-representation-leverage` -> `H4`, `H4a-representation-efficiency` -> `H4a`). Derived, never re-keyed."""
    return str(full_id).split("-", 1)[0]


def derive_model(raw: "dict | None" = None) -> TheoryModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and
    the checks share."""
    if raw is None:
        raw = _load_declared()
    hyps: "list[Hypothesis]" = []
    for h in raw.get("hypotheses", []):
        subs = [
            SubHypothesis(
                id=sh.get("id", ""), name=sh.get("name", ""),
                statement=sh.get("statement", ""), falsifier=sh.get("falsifier", ""),
            )
            for sh in (h.get("sub_hypotheses", []) or [])
        ]
        hyps.append(Hypothesis(
            id=h.get("id", ""), name=h.get("name", ""),
            statement=h.get("statement", ""), falsifier=h.get("falsifier", ""),
            sub_hypotheses=subs,
        ))
    return TheoryModel(hypotheses=hyps)


# ---- projection: the markdown table -----------------------------------------------------------------

def _hypothesis_cell(h: Hypothesis) -> str:
    """The Hypothesis cell. A plain hypothesis renders its statement; a decomposed one folds its sub-rows as
    `**H4a — <name>.** <statement> **H4b — <name>.** <statement>` (fixed separator + bold pattern, so the
    two-sub fold is deterministic and reaches byte parity)."""
    if not h.sub_hypotheses:
        return h.statement
    return " ".join(
        f"**{s.short} {_EMDASH} {s.name}.** {s.statement}" for s in h.sub_hypotheses
    )


def _falsifier_cell(h: Hypothesis) -> str:
    """The Key-falsifier cell. A plain hypothesis renders its falsifier; a decomposed one folds its sub-rows
    as `**H4a:** <falsifier> **H4b:** <falsifier>`."""
    if not h.sub_hypotheses:
        return h.falsifier
    return " ".join(f"**{s.short}:** {s.falsifier}" for s in h.sub_hypotheses)


def _hypothesis_row(h: Hypothesis) -> str:
    """One top-level hypothesis as a markdown table row — `| **H1 — name** | <hyp> | <falsifier> |`."""
    lead = f"**{h.short} {_EMDASH} {h.name}**"
    return f"| {lead} | {_hypothesis_cell(h)} | {_falsifier_cell(h)} |"


def render_table_rows(model: "TheoryModel | None" = None) -> "list[str]":
    """The hypotheses as markdown table lines (no header) — the page carries exactly these."""
    if model is None:
        model = derive_model()
    return [_hypothesis_row(h) for h in model.hypotheses]


def render_hypotheses_table_md(model: "TheoryModel | None" = None) -> str:
    """The full markdown table (header + rule + one row per top-level hypothesis) the chapter shows."""
    return "\n".join([_TABLE_HEADER, _TABLE_RULE, *render_table_rows(model)])


# ---- parity: the page carries the projection --------------------------------------------------------

def _page_table_lines(page_md: str) -> "list[str]":
    """Extract the hypotheses table from the page — the contiguous run of `|`-rows that starts at the model's
    exact header line (the dashboard extractor idiom). The `<!-- label -->` / caption comments sit ABOVE the
    header, so they are not swept in. Returns [] if the header is not found."""
    lines = [ln.rstrip() for ln in page_md.splitlines()]
    try:
        start = lines.index(_TABLE_HEADER)
    except ValueError:
        return []
    out: "list[str]" = []
    for ln in lines[start:]:
        if ln.startswith("|"):
            out.append(ln)
        else:
            break
    return out


def parity_findings(model: "TheoryModel | None" = None) -> "list[str]":
    """The page's table must equal the model's projection — the authored-content + parity-validator idiom.
    A mismatch means the page and the model drifted; regenerate the table from `... hypotheses-table`."""
    if model is None:
        model = derive_model()
    page_path = os.path.join(_BOOK, _PAGE_REL)
    if not os.path.isfile(page_path):
        return [f"parity: theory chapter page {_PAGE_REL} does not exist"]
    page_md = open(page_path, encoding="utf-8").read()
    got = _page_table_lines(page_md)
    want = render_hypotheses_table_md(model).splitlines()
    if not got:
        return [f"parity: no hypotheses table found in {_PAGE_REL} (expected the model's header line)"]
    if got != want:
        findings = [f"parity: {_PAGE_REL} table differs from the model projection — "
                    f"regenerate with `hypotheses-table`"]
        for i in range(max(len(got), len(want))):
            g = got[i] if i < len(got) else "<missing>"
            w = want[i] if i < len(want) else "<missing>"
            if g != w:
                findings.append(f"  row {i}: page {g!r} != model {w!r}")
        return findings
    return []


# ---- structural + count guard -----------------------------------------------------------------------

def structural_findings(model: "TheoryModel | None" = None) -> "list[str]":
    """The internal well-formedness invariants (TM1-TM7) — delegated to `theory_model_check.check()` rather
    than re-implemented (extract-on-second-site). Each Finding is rendered as `[TM_] message`."""
    return [f"[{f.code}] {f.message}" for f in _tmc.check()]


def count_guard_findings(model: "TheoryModel | None" = None) -> "list[str]":
    """The ratified-count guard — a silent add/drop/reclassify of a hypothesis or sub-hypothesis reddens
    (the dashboard model's C5-analogue). This is the backstop against the exact H-table drift the chapter
    fears: the parity check holds the TEXT equal, the count guard holds the SET size equal."""
    if model is None:
        model = derive_model()
    findings: "list[str]" = []
    n_hyp = len(model.hypotheses)
    n_sub = model.sub_count()
    if n_hyp != EXPECT_HYPOTHESES:
        findings.append(f"count: {n_hyp} hypotheses, expected {EXPECT_HYPOTHESES} "
                        f"(a hypothesis was added or removed)")
    if n_sub != EXPECT_SUBHYP:
        findings.append(f"count: {n_sub} sub-hypotheses, expected {EXPECT_SUBHYP} "
                        f"(a sub-hypothesis was added or removed)")
    return findings


def all_findings(model: "TheoryModel | None" = None) -> "list[str]":
    """Structural + parity + count guard — the full check `catalog.py validate` runs (audit-only)."""
    if model is None:
        model = derive_model()
    return structural_findings(model) + parity_findings(model) + count_guard_findings(model)


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_hypotheses_table() -> int:
    print(render_hypotheses_table_md())
    return 0


def _cmd_show() -> int:
    model = derive_model()
    for h in model.hypotheses:
        print(f"{h.short:>4} {h.name}")
        print(f"       {h.statement}")
        for s in h.sub_hypotheses:
            print(f"       - {s.short} {s.name}: {s.statement}")
    print(f"\n{len(model.hypotheses)} hypotheses · {model.sub_count()} sub-hypotheses")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    if findings:
        print(f"theory-of-mage: {len(findings)} finding(s) (audit-only — review candidates, not build stops):")
        for f in findings:
            print(f"  {f}")
        return 0  # audit-only: report, never gate
    print(f"theory-of-mage is in sync ({len(model.hypotheses)} hypotheses, {model.sub_count()} "
          f"sub-hypotheses; structural clean; page table matches the model)")
    return 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "hypotheses-table":
        return _cmd_hypotheses_table()
    if cmd == "show":
        return _cmd_show()
    print(f"usage: {argv[0]} [verify|hypotheses-table|show]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
