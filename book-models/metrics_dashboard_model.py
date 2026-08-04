"""The METRICS-DASHBOARD view — a typed model of the metrics the book steers by, carrying the author's
INCLUSION CRITERION so a future metric is testable against it, not sorted by taste. A sibling of the other
declared -> generated book models (claims / outline / flagship-stack): the hand-authored source of truth is
`book-models/metrics-dashboard.json`; this module projects the QUALIFYING subset into the back-matter page
"The Operator's Dashboard" and holds that page's table equal to the model with a parity check.

WHY A MODEL, NOT A HAND-BUILT TABLE.  The book measures many numbers; only some are metrics you STEER BY.
The inclusion criterion draws that line once, in one place, so every row on the dashboard passes the same
test and every exclusion is recorded WITH its reason instead of silently dropped. The criterion (verbatim
from the author): a metric belongs iff it is a useful agent-loop metric OR an org-level target for
engineering with MAGE — not merely a number the book measures. Diagnostics and payoff-measurements you
don't steer by are out.

TWO PROJECTIONS, ONE SOURCE.
  * `render_table_md()` — the markdown table the back-matter page shows (qualifying rows only). Author it
    into the page from `... table`; the page and the model cannot then diverge without the parity check
    reddening.
  * `structural_findings()` / `parity_findings()` — the invariants (schema + defined-in resolution + the
    ratified qualifying count) and the page-parity check. Wired into `catalog.py validate`.

Run `python3 book-models/metrics_dashboard_model.py verify` to drift-check (structural + parity);
`... table` to print the markdown table for the page; `... show` to list every metric and its verdict.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

_HERE = os.path.dirname(os.path.abspath(__file__))
_DECLARED = os.path.join(_HERE, "metrics-dashboard.json")
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_BOOK = os.path.join(_ROOT, "book")

#: The back-matter page the qualifying table is authored into (parity target).
_PAGE_REL = os.path.join("backmatter", "6.5-the-operators-dashboard.md")

#: The ratified verdict counts — encode the author's set so a silent add/drop reddens (C5).
EXPECT_QUALIFY = 5
EXPECT_EXCLUDE = 4

#: The table header the projection emits and the page carries (parity is exact).
_TABLE_HEADER = "| Metric | What it counts | The call it informs (when to watch) | Healthy direction | Defined in |"
_TABLE_RULE = "|---|---|---|---|---|"

_REQUIRED_FIELDS = ("name", "slug", "counts", "informs", "healthy_direction", "defined_in", "qualifies", "rationale")


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class Metric:
    """One metric the book names. `qualifies` is the verdict against the inclusion criterion; `rationale`
    records WHY it passes or fails (so an exclusion is auditable, not silent). `defined_in` cites the
    chapter and heading anchor where the metric lives — the load-bearing 'reference index' column."""
    name: str
    slug: str
    counts: str
    informs: str
    healthy_direction: str
    defined_in: dict
    qualifies: bool
    rationale: str


@dataclass
class DashboardModel:
    inclusion_criterion: str
    metrics: "list[Metric]"

    def qualifying(self) -> "list[Metric]":
        """The dashboard rows — metrics that pass the inclusion criterion, in declared order."""
        return [m for m in self.metrics if m.qualifies]

    def excluded(self) -> "list[Metric]":
        return [m for m in self.metrics if not m.qualifies]


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def derive_model() -> DashboardModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and
    the checks share."""
    raw = _load_declared()
    metrics = [
        Metric(
            name=m["name"], slug=m["slug"], counts=m["counts"], informs=m["informs"],
            healthy_direction=m["healthy_direction"], defined_in=m["defined_in"],
            qualifies=bool(m["qualifies"]), rationale=m["rationale"],
        )
        for m in raw["metrics"]
    ]
    return DashboardModel(inclusion_criterion=raw["inclusion_criterion"], metrics=metrics)


# ---- book-chapter resolution ------------------------------------------------------------------------

def _book_page_slugs() -> "set[str]":
    """Every chapter page slug the book currently defines (part dirs + front/back matter) — the resolve set
    for each metric's `defined_in.page_slug` (C4)."""
    slugs: "set[str]" = set()
    for sub in ("frontmatter", "part1", "part2", "part3", "part4", "part5", "backmatter"):
        d = os.path.join(_BOOK, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith(".md") and re.match(r"\d+\.\d+-", fn):
                slugs.add(fn[:-3])
    return slugs


# ---- invariants (C1-C5; the structural checks catalog.py validate walks) ----------------------------

def structural_findings(model: "DashboardModel | None" = None) -> "list[str]":
    """The STRUCTURAL / SCHEMA invariants. Each finding is a defect the fast gate should catch.

    C1 — a non-empty inclusion criterion (the model without its rule is just a list).
    C2 — every metric carries all required fields, non-empty (defined_in is a dict with chapter+page_slug).
    C3 — slugs are unique and kebab-case; `qualifies` is a real bool.
    C4 — every `defined_in.page_slug` resolves to a real book chapter page.
    C5 — the verdict split matches the ratified set (EXPECT_QUALIFY qualify, EXPECT_EXCLUDE do not).
    """
    if model is None:
        model = derive_model()
    findings: "list[str]" = []

    if not model.inclusion_criterion.strip():
        findings.append("C1 the model carries no inclusion_criterion")

    page_slugs = _book_page_slugs()
    seen: "set[str]" = set()
    raw = _load_declared()["metrics"]
    for m, rawm in zip(model.metrics, raw):
        # C2 — required fields present + non-empty.
        for f in _REQUIRED_FIELDS:
            if f not in rawm:
                findings.append(f"C2 metric {m.slug!r} is missing field {f!r}")
            elif f not in ("qualifies", "defined_in") and not str(rawm[f]).strip():
                findings.append(f"C2 metric {m.slug!r} has empty field {f!r}")
        if not isinstance(m.defined_in, dict) or not m.defined_in.get("chapter") or not m.defined_in.get("page_slug"):
            findings.append(f"C2 metric {m.slug!r} defined_in lacks chapter/page_slug")

        # C3 — slug shape + uniqueness + real bool.
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", m.slug):
            findings.append(f"C3 metric {m.slug!r} slug is not kebab-case")
        if m.slug in seen:
            findings.append(f"C3 duplicate metric slug {m.slug!r}")
        seen.add(m.slug)
        if not isinstance(rawm.get("qualifies"), bool):
            findings.append(f"C3 metric {m.slug!r} qualifies is not a JSON bool")

        # C4 — defined_in resolves to a real chapter page.
        page = (m.defined_in or {}).get("page_slug", "")
        if page and page not in page_slugs:
            findings.append(f"C4 metric {m.slug!r} defined_in page {page!r} resolves to no book chapter")

    # C5 — the ratified verdict split.
    nq, nx = len(model.qualifying()), len(model.excluded())
    if nq != EXPECT_QUALIFY:
        findings.append(f"C5 {nq} metrics qualify, expected {EXPECT_QUALIFY} (a metric was added or reclassified)")
    if nx != EXPECT_EXCLUDE:
        findings.append(f"C5 {nx} metrics excluded, expected {EXPECT_EXCLUDE} (a metric was added or reclassified)")

    return findings


# ---- projection: the markdown table -----------------------------------------------------------------

def _defined_in_cell(d: dict) -> str:
    """Render the `Defined in` cell as a book cross-chapter link — `[N.M](slug.html#anchor)`."""
    chapter, page, anchor = d["chapter"], d["page_slug"], d.get("anchor", "")
    href = f"{page}.html#{anchor}" if anchor else f"{page}.html"
    return f"[{chapter}]({href})"


def render_table_rows(model: "DashboardModel | None" = None) -> "list[str]":
    """The qualifying rows as markdown table lines (no header) — the page carries exactly these."""
    if model is None:
        model = derive_model()
    rows: "list[str]" = []
    for m in model.qualifying():
        rows.append(
            f"| **{m.name}** | {m.counts} | {m.informs} | {m.healthy_direction} | {_defined_in_cell(m.defined_in)} |"
        )
    return rows


def render_table_md(model: "DashboardModel | None" = None) -> str:
    """The full markdown table (header + rule + qualifying rows) the back-matter page shows."""
    return "\n".join([_TABLE_HEADER, _TABLE_RULE, *render_table_rows(model)])


# ---- parity: the page carries the projection --------------------------------------------------------

def _page_table_lines(page_md: str) -> "list[str]":
    """Extract the dashboard table from the page — the contiguous run of `|`-rows that starts at the model's
    exact header line. Returns [] if the header is not found."""
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


def parity_findings(model: "DashboardModel | None" = None) -> "list[str]":
    """The page's table must equal the model's projection — the authored-content + parity-validator idiom.
    A mismatch means the page and the model have drifted; regenerate the table from `... table`."""
    if model is None:
        model = derive_model()
    page_path = os.path.join(_BOOK, _PAGE_REL)
    if not os.path.isfile(page_path):
        return [f"parity: back-matter page {_PAGE_REL} does not exist"]
    page_md = open(page_path, encoding="utf-8").read()
    got = _page_table_lines(page_md)
    want = render_table_md(model).splitlines()
    if not got:
        return [f"parity: no dashboard table found in {_PAGE_REL} (expected the model's header line)"]
    if got != want:
        findings = [f"parity: {_PAGE_REL} table differs from the model projection — regenerate with `table`"]
        for i in range(max(len(got), len(want))):
            g = got[i] if i < len(got) else "<missing>"
            w = want[i] if i < len(want) else "<missing>"
            if g != w:
                findings.append(f"  row {i}: page {g!r} != model {w!r}")
        return findings
    return findings_ok()


def findings_ok() -> "list[str]":
    return []


def all_findings(model: "DashboardModel | None" = None) -> "list[str]":
    """Structural + parity — the full check catalog.py validate runs."""
    if model is None:
        model = derive_model()
    return structural_findings(model) + parity_findings(model)


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_table() -> int:
    print(render_table_md())
    return 0


def _cmd_show() -> int:
    model = derive_model()
    print(f"inclusion criterion:\n  {model.inclusion_criterion}\n")
    for m in model.metrics:
        verdict = "DASHBOARD" if m.qualifies else "excluded "
        print(f"[{verdict}] {m.name}  (defined in {m.defined_in['chapter']})")
        print(f"             {m.rationale}")
    print(f"\n{len(model.qualifying())} qualify · {len(model.excluded())} excluded")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    if findings:
        print(f"metrics-dashboard: {len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"metrics-dashboard is in sync ({len(model.qualifying())} dashboard rows, "
          f"{len(model.excluded())} excluded; page table matches the model)")
    return 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "table":
        return _cmd_table()
    if cmd == "show":
        return _cmd_show()
    print(f"usage: {argv[0]} [verify|table|show]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
