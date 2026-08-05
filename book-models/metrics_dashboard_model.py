"""The METRICS-DASHBOARD view — a typed model of the metrics the book steers by or certifies with, carrying
the author's INCLUSION CRITERION so a future metric is testable against it, not sorted by taste. A sibling of
the other declared -> generated book models (claims / outline / flagship-stack): the hand-authored source of
truth is `book-models/metrics-dashboard.json`; this module projects ALL nine metrics into the Operator's
Dashboard page (Appendix D.1, Operator's Reference), grouped by MODE, and holds that page's table equal to
the model with a parity check.

FORMATIVE vs SUMMATIVE.  Every metric the book names is on the dashboard now — an engineering reference wants
the whole set — but each carries a MODE that says WHEN you read it. A `formative` metric is measured DURING
the work and feeds back to steer the next step. A `summative` metric is measured at MATURITY and delivers a
verdict on what was achieved. A `both` metric is a trajectory: watched formatively as it forms, reported
summatively at maturity. The criterion (verbatim from the author): a metric belongs iff it is one you STEER
BY while the work is in flight (formative) or one you CERTIFY THE RESULT with at maturity (summative) —
measured to guide or to judge engineering with MAGE, not merely reported.

TWO PROJECTIONS, ONE SOURCE.
  * `render_table_md()` — the markdown table the Operator's Dashboard page shows: all nine metrics in two mode bands
    (a Formative band, a divider/band-label row, then a Summative band that carries the summative + both
    metrics). Author it into the page from `... table`; the page and the model cannot then diverge without
    the parity check reddening.
  * `structural_findings()` / `parity_findings()` — the invariants (schema + defined-in resolution + the
    ratified mode counts) and the page-parity check. Wired into `catalog.py validate`.

Run `python3 book-models/metrics_dashboard_model.py verify` to drift-check (structural + parity);
`... table` to print the markdown table for the page; `... show` to list every metric and its mode.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

from _book_pages import book_page_slugs as _book_page_slugs  # shared page-slug resolver (extract-on-2nd-site)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DECLARED = os.path.join(_HERE, "metrics-dashboard.json")
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_BOOK = os.path.join(_ROOT, "book")

#: The page the mode-banded table is authored into (parity target). The Operator's Dashboard moved from a
#: back-matter chapter to Appendix D.1 (Operator's Reference); the model projects into and holds equal its new
#: appendix-card home.
_PAGE_REL = os.path.join("appendix-operators-reference", "operators-dashboard.md")

#: The valid MODE values — the formative/summative axis, plus `both` for a trajectory metric.
_VALID_MODES = ("formative", "summative", "both")

#: The ratified mode split — encode the author's set so a silent add/drop/reclassify reddens (C5).
EXPECT_TOTAL = 9
EXPECT_FORMATIVE = 6
EXPECT_SUMMATIVE = 1
EXPECT_BOTH = 2

#: The dashboard columns (the header the projection emits and the page carries; parity is exact).
_COLUMNS = ("Metric", "Mode", "What it counts", "When to watch", "Healthy direction", "Defined in")
_TABLE_HEADER = "| " + " | ".join(_COLUMNS) + " |"
_TABLE_RULE = "|" + "---|" * len(_COLUMNS)

_REQUIRED_FIELDS = ("name", "slug", "counts", "informs", "healthy_direction", "defined_in", "mode", "rationale")


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class Metric:
    """One metric the book names. `mode` is the formative/summative verdict against the inclusion criterion;
    `rationale` records WHY it lands in that band (so the call is auditable, not silent). `defined_in` cites
    the chapter and heading anchor where the metric lives — the load-bearing 'reference index' column."""
    name: str
    slug: str
    counts: str
    informs: str
    healthy_direction: str
    defined_in: dict
    mode: str
    rationale: str


@dataclass
class DashboardModel:
    inclusion_criterion: str
    mode_bands: dict
    metrics: "list[Metric]"

    def formative(self) -> "list[Metric]":
        """The formative band — metrics you steer by while the work is in flight, in declared order."""
        return [m for m in self.metrics if m.mode == "formative"]

    def summative_band(self) -> "list[Metric]":
        """The summative band — the summative verdict metric plus the `both` trajectory metrics (whose
        reference number is the mature verdict), in declared order."""
        return [m for m in self.metrics if m.mode in ("summative", "both")]

    def by_mode(self, mode: str) -> "list[Metric]":
        return [m for m in self.metrics if m.mode == mode]


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
            mode=str(m["mode"]), rationale=m["rationale"],
        )
        for m in raw["metrics"]
    ]
    return DashboardModel(
        inclusion_criterion=raw["inclusion_criterion"],
        mode_bands=raw.get("_mode_bands", {}),
        metrics=metrics,
    )


# ---- book-chapter resolution ------------------------------------------------------------------------
# The page-slug resolve set for each metric's `defined_in.page_slug` (C4) is the shared `_book_pages`
# derivation (imported as `_book_page_slugs` above), so a chapter add/rename updates every model at once.


# ---- invariants (C1-C5; the structural checks catalog.py validate walks) ----------------------------

def structural_findings(model: "DashboardModel | None" = None) -> "list[str]":
    """The STRUCTURAL / SCHEMA invariants. Each finding is a defect the fast gate should catch.

    C1 — a non-empty inclusion criterion (the model without its rule is just a list).
    C2 — every metric carries all required fields, non-empty (defined_in is a dict with chapter+page_slug).
    C3 — slugs are unique and kebab-case; `mode` is one of the valid formative/summative/both values.
    C4 — every `defined_in.page_slug` resolves to a real book chapter page.
    C5 — the mode split matches the ratified set (all nine present; 6 formative, 1 summative, 2 both).
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
            elif f != "defined_in" and not str(rawm[f]).strip():
                findings.append(f"C2 metric {m.slug!r} has empty field {f!r}")
        if not isinstance(m.defined_in, dict) or not m.defined_in.get("chapter") or not m.defined_in.get("page_slug"):
            findings.append(f"C2 metric {m.slug!r} defined_in lacks chapter/page_slug")

        # C3 — slug shape + uniqueness + valid mode.
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", m.slug):
            findings.append(f"C3 metric {m.slug!r} slug is not kebab-case")
        if m.slug in seen:
            findings.append(f"C3 duplicate metric slug {m.slug!r}")
        seen.add(m.slug)
        if m.mode not in _VALID_MODES:
            findings.append(f"C3 metric {m.slug!r} mode {m.mode!r} is not one of {_VALID_MODES}")

        # C4 — defined_in resolves to a real chapter page.
        page = (m.defined_in or {}).get("page_slug", "")
        if page and page not in page_slugs:
            findings.append(f"C4 metric {m.slug!r} defined_in page {page!r} resolves to no book chapter")

    # C5 — the ratified mode split (all nine present; the mode-classified counts).
    total = len(model.metrics)
    if total != EXPECT_TOTAL:
        findings.append(f"C5 {total} metrics, expected {EXPECT_TOTAL} (a metric was added or removed)")
    nf, ns, nb = len(model.by_mode("formative")), len(model.by_mode("summative")), len(model.by_mode("both"))
    if nf != EXPECT_FORMATIVE:
        findings.append(f"C5 {nf} formative metrics, expected {EXPECT_FORMATIVE} (a metric was reclassified)")
    if ns != EXPECT_SUMMATIVE:
        findings.append(f"C5 {ns} summative metrics, expected {EXPECT_SUMMATIVE} (a metric was reclassified)")
    if nb != EXPECT_BOTH:
        findings.append(f"C5 {nb} both-mode metrics, expected {EXPECT_BOTH} (a metric was reclassified)")

    return findings


# ---- projection: the markdown table -----------------------------------------------------------------

def _defined_in_cell(d: dict) -> str:
    """Render the `Defined in` cell as a book cross-chapter link — `[N.M](slug.html#anchor)`."""
    chapter, page, anchor = d["chapter"], d["page_slug"], d.get("anchor", "")
    href = f"{page}.html#{anchor}" if anchor else f"{page}.html"
    return f"[{chapter}]({href})"


def _metric_row(m: Metric) -> str:
    """One metric as a markdown table row — the six columns in header order."""
    return (
        f"| **{m.name}** | {m.mode} | {m.counts} | {m.informs} | "
        f"{m.healthy_direction} | {_defined_in_cell(m.defined_in)} |"
    )


def _band_row(label: str) -> str:
    """A band-label row — the midrule/divider between the formative and summative groups. The label sits in
    the first cell; the remaining cells are empty, so it reads as a labeled divider that renders cleanly in
    BOTH projections (an ordinary pipe-table row in HTML and Typst alike)."""
    return f"| **{label}** |" + " |" * (len(_COLUMNS) - 1)


def render_table_rows(model: "DashboardModel | None" = None) -> "list[str]":
    """All nine metrics as markdown table lines (no header), in two mode bands separated by a band-label
    divider — the page carries exactly these."""
    if model is None:
        model = derive_model()
    rows: "list[str]" = [_band_row(model.mode_bands["formative"])]
    rows += [_metric_row(m) for m in model.formative()]
    rows.append(_band_row(model.mode_bands["summative"]))
    rows += [_metric_row(m) for m in model.summative_band()]
    return rows


def render_table_md(model: "DashboardModel | None" = None) -> str:
    """The full markdown table (header + rule + the two mode bands) the Operator's Dashboard page shows."""
    return "\n".join([_TABLE_HEADER, _TABLE_RULE, *render_table_rows(model)])


# ---- parity: the page carries the projection --------------------------------------------------------

def _page_table_lines(page_md: str) -> "list[str]":
    """Extract the dashboard table from the page — the contiguous run of `|`-rows that starts at the model's
    exact header line. The band-label divider rows also begin with `|`, so the whole grouped table is one
    contiguous run. Returns [] if the header is not found."""
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
        return [f"parity: Operator's Dashboard page {_PAGE_REL} does not exist"]
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
        print(f"[{m.mode:>10}] {m.name}  (defined in {m.defined_in['chapter']})")
        print(f"             {m.rationale}")
    nf, ns, nb = len(model.by_mode("formative")), len(model.by_mode("summative")), len(model.by_mode("both"))
    print(f"\n{len(model.metrics)} metrics · {nf} formative · {ns} summative · {nb} both")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    if findings:
        print(f"metrics-dashboard: {len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    nf, ns, nb = len(model.by_mode("formative")), len(model.by_mode("summative")), len(model.by_mode("both"))
    print(f"metrics-dashboard is in sync ({len(model.metrics)} metrics: {nf} formative, {ns} summative, "
          f"{nb} both; page table matches the model)")
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
