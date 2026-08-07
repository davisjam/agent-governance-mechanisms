"""Shared projection-parity primitives for the declared -> generated book/site models.

Three-plus consumers now share the "project a declared model, then check the projection against the
world" idiom (`metrics_dashboard_model` and `theory_of_mage_model` project a table into an authored
page; `landing_big_ideas_model` projects a Concept-Card page per idea and resolves a hand-declared
edge). Rather than copy the page-table extractor a third time and hand-roll a fresh catalogue-slug
resolver, the reused primitives live here once, per the extract-on-the-third-site rule.

This module holds ONLY the reused primitives — no reverse-edge derivation, no bidirectional join
engine (that machinery waits for a consumer that renders a reverse direction):

  * `page_block_parity(page_path, header_line, want_lines)` — the authored-page table-parity check: the
    contiguous run of `|`-rows starting at `header_line` must equal `want_lines`, row for row. Relocates
    the byte-identical `_page_table_lines` + row-diff both existing table models carried.
  * `resolve_edges(records, edge_field, target_set, label)` — every slug in `record[edge_field]` resolves
    in `target_set`; the generic hand-declared-edge resolution check.
  * `require_fields(records, required, label)` — every record carries each `required` field, non-empty.
  * `catalogue_entry_slugs()` / `catalogue_entry_paths()` — the entry-slug resolve set and the
    slug -> `<role>/<family>/<slug>.html` href map, scanned from the role trees (`agent/`,
    `models-bridge/`, `product/`). The sibling of `_book_pages.book_page_slugs()` for chapters; the
    resolve set the `Concept -> mechanism` edge joins against. Reads the trees at check time, so a
    consumer's `verify` runs standalone (no catalog import).

Stdlib-only, like the rest of `book-models/` — clone-and-run.
"""
from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)

#: The catalogue's three role trees; entry `.md` files live at `<role>/<family>/<slug>.md`. A role-level
#: `README.md` (depth 1) is NOT an entry and is excluded — only `<role>/<family>/*.md` counts.
_ROLE_TREES = ("agent", "models-bridge", "product")

_MISSING = object()


# ---- record-field access (dataclass OR dict) --------------------------------------------------------

def _field(rec: object, name: str, default: object = _MISSING) -> object:
    """Read `name` off a record that may be a dataclass/object (attribute) or a dict (key)."""
    if isinstance(rec, dict):
        return rec.get(name, default)
    return getattr(rec, name, default)


def _ident(rec: object) -> str:
    """A record's identifier for finding messages — its `slug`, else `id`, else `repr`."""
    for key in ("slug", "id"):
        val = _field(rec, key, None)
        if val:
            return str(val)
    return repr(rec)


# ---- page-table parity ------------------------------------------------------------------------------

def _contiguous_pipe_run(page_md: str, header_line: str, occurrence: int = 0) -> "list[str]":
    """The contiguous run of `|`-rows starting at the model's exact `header_line` — the table (header +
    rule + body, incl. band-label divider rows, which also begin with `|`). Comments/captions sit above
    the header, so they are not swept in. `occurrence` selects WHICH match to anchor on when two placed
    tables share an identical header line (e.g. two convergence tables on one page, distinguished only by
    their rows) — `occurrence=0` (the default) preserves the single-table behaviour. Returns [] if the
    header line's `occurrence`-th match is not present."""
    lines = [ln.rstrip() for ln in page_md.splitlines()]
    matches = [i for i, ln in enumerate(lines) if ln == header_line]
    if occurrence >= len(matches):
        return []
    start = matches[occurrence]
    out: "list[str]" = []
    for ln in lines[start:]:
        if ln.startswith("|"):
            out.append(ln)
        else:
            break
    return out


def page_block_parity(page_path: str, header_line: str, want_lines: "list[str]", *,
                      display: "str | None" = None, label: str = "table",
                      regen_hint: str = "", occurrence: int = 0) -> "list[str]":
    """The authored page's `label` block must equal the model's projection. Extract the contiguous
    `|`-row run beginning at `header_line`; compare it to `want_lines` row for row. A mismatch means the
    page drifted from the model — regenerate the block. `occurrence` disambiguates two placed tables that
    share an identical header line (default 0 = the first/only match). Returns [] when the page carries
    exactly the projection (or is absent — a caller that treats a missing page as a hard finding checks
    first)."""
    name = display or os.path.basename(page_path)
    if not os.path.isfile(page_path):
        return [f"parity: {label} page {name} does not exist"]
    page_md = open(page_path, encoding="utf-8").read()
    got = _contiguous_pipe_run(page_md, header_line, occurrence)
    if not got:
        return [f"parity: no {label} found in {name} (expected the model's header line)"]
    if got != want_lines:
        hint = f" with `{regen_hint}`" if regen_hint else ""
        findings = [f"parity: {name} {label} differs from the model projection — regenerate{hint}"]
        for i in range(max(len(got), len(want_lines))):
            g = got[i] if i < len(got) else "<missing>"
            w = want_lines[i] if i < len(want_lines) else "<missing>"
            if g != w:
                findings.append(f"  row {i}: page {g!r} != model {w!r}")
        return findings
    return []


# ---- hand-declared-edge + schema checks -------------------------------------------------------------

def resolve_edges(records: "list", edge_field: str, target_set: "set[str]", label: str) -> "list[str]":
    """Every slug in each record's `edge_field` list must resolve in `target_set`. The generic
    hand-declared-edge resolution check — a declared edge cannot silently point at nothing."""
    findings: "list[str]" = []
    for rec in records:
        edges = _field(rec, edge_field, None) or []
        for slug in edges:
            if slug not in target_set:
                findings.append(f"{label}: {_ident(rec)!r} references {slug!r}, which resolves to no target")
    return findings


def require_fields(records: "list", required: "tuple[str, ...] | list[str]", label: str) -> "list[str]":
    """Every record carries each `required` field, present and (for strings) non-empty."""
    findings: "list[str]" = []
    for rec in records:
        ident = _ident(rec)
        for f in required:
            val = _field(rec, f, _MISSING)
            if val is _MISSING or val is None:
                findings.append(f"{label}: {ident!r} is missing field {f!r}")
            elif isinstance(val, str) and not val.strip():
                findings.append(f"{label}: {ident!r} has empty field {f!r}")
    return findings


# ---- catalogue-entry resolve set --------------------------------------------------------------------

def catalogue_entry_paths() -> "dict[str, str]":
    """`{slug: '<role>/<family>/<slug>.html'}` for every catalogue entry — the href map a root-level page
    links a mechanism edge through. Scans `<role>/<family>/*.md`; role-level READMEs are excluded."""
    paths: "dict[str, str]" = {}
    for role in _ROLE_TREES:
        base = os.path.join(_ROOT, role)
        if not os.path.isdir(base):
            continue
        for family in sorted(os.listdir(base)):
            fam_dir = os.path.join(base, family)
            if not os.path.isdir(fam_dir):
                continue
            for fn in sorted(os.listdir(fam_dir)):
                if fn.endswith(".md"):
                    slug = fn[:-3]
                    paths[slug] = f"{role}/{family}/{slug}.html"
    return paths


def catalogue_entry_slugs() -> "set[str]":
    """Every catalogue entry slug — the resolve set the `Concept -> mechanism` edge joins against."""
    return set(catalogue_entry_paths())
