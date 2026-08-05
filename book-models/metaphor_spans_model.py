"""The METAPHOR-SPANS view — a typed model of every sustained metaphor the book runs, carrying WHERE each is
introduced and (for local metaphors) where it pays off, so the author's own editorial rule is MEASURABLE:
never introduce a second metaphor until the first has paid off. A sibling of the other declared -> generated
book models (metrics-dashboard / flagship-stack / lit-positioning): the hand-authored source of truth is
`book-models/metaphor-spans.json`; this module projects the inventory and computes the overlap metric,
wired into `catalog.py validate`.

WHY A MODEL, NOT A HEADCOUNT.  "One metaphor at a time" is an editorial discipline you can only audit if the
spans are written down. The model splits metaphors into two kinds — `core` (established book vocabulary that
is always live, exempt from the rule) and `local` (raised for one point, expected to pay off before the next
local starts) — because the rule is meaningless without that split: the Printer and the loop recur on nearly
every page by design. Only locals participate in the overlap metric.

STABLE ANCHORS, NOT LINE NUMBERS.  Each span keys on a chapter `page_slug` plus a heading/index-def/point
`anchor` slug, so the model survives prose edits that shift line numbers. The overlap metric resolves an
anchor to a linear position by walking the chapter's anchors in document order.

TWO KINDS OF FINDING.
  * `structural_findings()` (C1-C7) — the schema + resolution invariants. BLOCKING in `catalog.py validate`
    (the model must be well-formed).
  * `overlap_findings()` + `vehicle_collision_findings()` — the editorial metric and a softer secondary
    check. AUDIT-ONLY-first: surfaced, non-gating, until a clean session promotes overlap to blocking.

Run `python3 book-models/metaphor_spans_model.py verify` to drift-check; `... table` to print the inventory
table; `... show` to list every metaphor with its kind + span; `... anchors <page_slug>` to dump a chapter's
resolvable anchors in order.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

from _book_pages import book_page_slugs, chapter_md_path  # shared page-slug resolver (extract-on-2nd-site)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DECLARED = os.path.join(_HERE, "metaphor-spans.json")

#: The ratified split — encode the author's set so a silent add/reclassify reddens (C6).
EXPECT_CORE = 7
EXPECT_LOCAL = 9
EXPECT_OVERLAPS = 0

_REQUIRED_FIELDS = ("name", "slug", "kind", "vehicle", "introduced_at", "payoff", "overlap_ok", "overlap_rationale", "notes")
_KINDS = ("core", "local")

#: The projected inventory table header (CLI `table`).
_TABLE_HEADER = "| Metaphor | Kind | Introduced | Pays off | Payoff |"
_TABLE_RULE = "|---|---|---|---|---|"

#: Tokens dropped from the vehicle-collision comparison (articles / connectives / generic figure words).
_STOP_TOKENS = frozenset({
    "the", "a", "an", "and", "or", "of", "is", "not", "as", "to", "for", "on", "in", "at", "by",
    "two", "one", "into", "over", "with", "from", "you", "your", "it", "its", "that", "this",
})


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class Metaphor:
    """One sustained metaphor the book runs. `kind` drives the overlap exemption: `core` vocabulary is always
    live (no `pays_off_at`); a `local` metaphor carries a `pays_off_at` and is the only kind the overlap
    metric ranges over. `overlap_ok` + `overlap_rationale` record a DELIBERATE overlap (a ratified exception),
    so 'exceptional' is a written decision, not an unaudited pass."""
    name: str
    slug: str
    kind: str
    vehicle: str
    introduced_at: dict
    payoff: str
    overlap_ok: bool
    overlap_rationale: str
    notes: str
    pays_off_at: "dict | None" = None
    stretch: str = ""

    def stretch_key(self) -> str:
        """The collision unit — the explicit `stretch`, else the intro chapter page_slug."""
        return self.stretch or (self.introduced_at or {}).get("page_slug", "")


@dataclass
class MetaphorModel:
    overlap_rule: str
    ratified_counts: dict
    metaphors: "list[Metaphor]"

    def core(self) -> "list[Metaphor]":
        return [m for m in self.metaphors if m.kind == "core"]

    def local(self) -> "list[Metaphor]":
        return [m for m in self.metaphors if m.kind == "local"]


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def derive_model() -> MetaphorModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and
    the checks share."""
    raw = _load_declared()
    metaphors = [
        Metaphor(
            name=m["name"], slug=m["slug"], kind=m["kind"], vehicle=m["vehicle"],
            introduced_at=m["introduced_at"], payoff=m["payoff"],
            overlap_ok=bool(m.get("overlap_ok", False)), overlap_rationale=m.get("overlap_rationale", ""),
            notes=m.get("notes", ""), pays_off_at=m.get("pays_off_at"), stretch=m.get("stretch", ""),
        )
        for m in raw["metaphors"]
    ]
    return MetaphorModel(
        overlap_rule=raw.get("overlap_rule", ""),
        ratified_counts=raw.get("ratified_counts", {}),
        metaphors=metaphors,
    )


# ---- anchor resolution ------------------------------------------------------------------------------

_ANCHOR_HEADING_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
_ANCHOR_INDEXDEF_RE = re.compile(r"<!--\s*index-def:\s*([A-Za-z0-9_-]+)")
_ANCHOR_POINT_RE = re.compile(r"<!--\s*point:\s*([A-Za-z0-9_-]+)")


def chapter_anchors(page_slug: str) -> "list[str]":
    """Every resolvable anchor slug in a chapter, in document order — the union of `{#slug}` heading anchors,
    `<!-- index-def: slug -->` markers, and `<!-- point: slug -->` drain decorators. These are exactly the
    ids the book build emits, so 'the anchor resolves to a real heading in the built book' is checkable, and
    the overlap metric can turn an anchor into a linear position (its index in this list)."""
    path = chapter_md_path(page_slug)
    if path is None:
        return []
    anchors: "list[str]" = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            for rx in (_ANCHOR_HEADING_RE, _ANCHOR_INDEXDEF_RE, _ANCHOR_POINT_RE):
                m = rx.search(line)
                if m:
                    anchors.append(m.group(1))
    return anchors


def _anchor_position(page_slug: str, anchor: str) -> "int | None":
    """The linear position of an anchor within its chapter (its index in `chapter_anchors`), or None if the
    anchor is empty or does not resolve."""
    if not anchor:
        return None
    order = chapter_anchors(page_slug)
    try:
        return order.index(anchor)
    except ValueError:
        return None


# ---- invariants (C1-C7; the STRUCTURAL checks catalog.py validate walks — BLOCKING) -----------------

def structural_findings(model: "MetaphorModel | None" = None) -> "list[str]":
    """The STRUCTURAL / SCHEMA invariants — each a defect the fast gate should catch.

    C1 — a non-empty `overlap_rule` (the model without its rule is just a list).
    C2 — every metaphor carries the required fields, non-empty; `introduced_at`/`pays_off_at` are dicts
         with chapter + page_slug.
    C3 — slugs unique + kebab-case; `kind` in {core, local}; `overlap_ok` a real JSON bool.
    C4 — every `page_slug` (intro + pays-off) resolves to a real book chapter page.
    C5 — a `local` metaphor MUST carry `pays_off_at`; a `core` metaphor must NOT (core never ends).
    C6 — the `ratified_counts` split matches reality (core, local, and computed overlaps counts).
    C7 — every NON-EMPTY anchor (intro + pays-off) resolves to a real anchor in its chapter's built page.
    """
    if model is None:
        model = derive_model()
    findings: "list[str]" = []

    if not model.overlap_rule.strip():
        findings.append("C1 the model carries no overlap_rule")

    page_slugs = book_page_slugs()
    seen: "set[str]" = set()
    raw = _load_declared()["metaphors"]
    for m, rawm in zip(model.metaphors, raw):
        # C2 — required fields present + non-empty.
        for f in _REQUIRED_FIELDS:
            if f not in rawm:
                findings.append(f"C2 metaphor {m.slug!r} is missing field {f!r}")
            elif f not in ("overlap_ok", "introduced_at", "overlap_rationale", "notes") and not str(rawm[f]).strip():
                findings.append(f"C2 metaphor {m.slug!r} has empty field {f!r}")
        if not isinstance(m.introduced_at, dict) or not m.introduced_at.get("chapter") or not m.introduced_at.get("page_slug"):
            findings.append(f"C2 metaphor {m.slug!r} introduced_at lacks chapter/page_slug")
        if m.pays_off_at is not None and (not isinstance(m.pays_off_at, dict) or not m.pays_off_at.get("chapter") or not m.pays_off_at.get("page_slug")):
            findings.append(f"C2 metaphor {m.slug!r} pays_off_at lacks chapter/page_slug")

        # C3 — slug shape + uniqueness; kind enum; real bool.
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", m.slug):
            findings.append(f"C3 metaphor {m.slug!r} slug is not kebab-case")
        if m.slug in seen:
            findings.append(f"C3 duplicate metaphor slug {m.slug!r}")
        seen.add(m.slug)
        if m.kind not in _KINDS:
            findings.append(f"C3 metaphor {m.slug!r} kind {m.kind!r} is not one of {_KINDS}")
        if not isinstance(rawm.get("overlap_ok"), bool):
            findings.append(f"C3 metaphor {m.slug!r} overlap_ok is not a JSON bool")

        # C4 — every page_slug resolves to a real chapter page.
        for where, site in (("introduced_at", m.introduced_at), ("pays_off_at", m.pays_off_at)):
            if not isinstance(site, dict):
                continue
            page = site.get("page_slug", "")
            if page and page not in page_slugs:
                findings.append(f"C4 metaphor {m.slug!r} {where} page {page!r} resolves to no book chapter")

        # C5 — local has pays_off_at; core does not.
        if m.kind == "local" and not m.pays_off_at:
            findings.append(f"C5 local metaphor {m.slug!r} is missing pays_off_at (a local must pay off)")
        if m.kind == "core" and m.pays_off_at:
            findings.append(f"C5 core metaphor {m.slug!r} carries pays_off_at (core vocabulary never ends)")

        # C7 — non-empty anchors resolve to a real anchor in the built chapter.
        for where, site in (("introduced_at", m.introduced_at), ("pays_off_at", m.pays_off_at)):
            if not isinstance(site, dict):
                continue
            page, anchor = site.get("page_slug", ""), site.get("anchor", "")
            if anchor and page in page_slugs and _anchor_position(page, anchor) is None:
                findings.append(f"C7 metaphor {m.slug!r} {where} anchor {anchor!r} resolves to no heading/index-def/point in {page!r}")

    # C6 — the ratified split (structural half: core/local; the overlap count is checked against the metric).
    nc, nl = len(model.core()), len(model.local())
    if nc != EXPECT_CORE:
        findings.append(f"C6 {nc} core metaphors, expected {EXPECT_CORE} (a metaphor was added or reclassified)")
    if nl != EXPECT_LOCAL:
        findings.append(f"C6 {nl} local metaphors, expected {EXPECT_LOCAL} (a metaphor was added or reclassified)")
    rc = model.ratified_counts or {}
    if rc.get("core") != EXPECT_CORE or rc.get("local") != EXPECT_LOCAL or rc.get("overlaps") != EXPECT_OVERLAPS:
        findings.append(f"C6 ratified_counts {rc} disagrees with the ratified set "
                        f"(core {EXPECT_CORE}, local {EXPECT_LOCAL}, overlaps {EXPECT_OVERLAPS})")

    return findings


# ---- the overlap metric (AUDIT-ONLY) ----------------------------------------------------------------

def overlap_findings(model: "MetaphorModel | None" = None) -> "list[str]":
    """The editorial metric: two LOCAL metaphors live simultaneously within one stretch. Group locals by
    stretch; within a stretch, order by intro position; a collision is any pair (A, B) where B is introduced
    at or before A's pays_off_at (their spans intersect). CORE is exempt. A ratified overlap (overlap_ok on
    either party) is excluded — so 'exceptional' is a recorded decision, not an unaudited pass."""
    if model is None:
        model = derive_model()
    findings: "list[str]" = []

    by_stretch: "dict[str, list[Metaphor]]" = {}
    for m in model.local():
        by_stretch.setdefault(m.stretch_key(), []).append(m)

    for stretch, locals_ in sorted(by_stretch.items()):
        # Order by intro position; unresolved positions sort last but stably.
        def intro_pos(mm: Metaphor) -> int:
            p = _anchor_position(mm.introduced_at.get("page_slug", ""), mm.introduced_at.get("anchor", ""))
            return p if p is not None else 1 << 30
        ordered = sorted(locals_, key=intro_pos)
        for i, a in enumerate(ordered):
            a_payoff = _anchor_position((a.pays_off_at or {}).get("page_slug", ""), (a.pays_off_at or {}).get("anchor", ""))
            for b in ordered[i + 1:]:
                b_intro = intro_pos(b)
                # B introduced within A's still-open span (A has not yet paid off).
                if a_payoff is not None and b_intro <= a_payoff:
                    if not (a.overlap_ok or b.overlap_ok):
                        findings.append(
                            f"OVERLAP in stretch {stretch!r}: {b.slug!r} (intro @{b.introduced_at.get('anchor','')}) "
                            f"opens before {a.slug!r} pays off (@{(a.pays_off_at or {}).get('anchor','')}). "
                            f"Fix: DEFER {b.slug!r} past {a.slug!r}'s payoff, PAY OFF {a.slug!r} first, or DELETE the weaker image."
                        )
    return findings


def compute_overlap_count(model: "MetaphorModel | None" = None) -> int:
    return len(overlap_findings(model))


# ---- the secondary vehicle-collision check (AUDIT-ONLY) ---------------------------------------------

def _image_tokens(m: Metaphor) -> "set[str]":
    """The distinctive image words of a metaphor — tokens of its name + slug, minus articles/connectives and
    tokens under four characters. The identifying image (e.g. 'staircase') lives here, so a shared token
    across different stretches is a diluted vehicle."""
    words = re.split(r"[^a-z0-9]+", f"{m.name} {m.slug}".lower())
    return {w for w in words if len(w) >= 4 and w not in _STOP_TOKENS}


def vehicle_collision_findings(model: "MetaphorModel | None" = None) -> "list[str]":
    """A softer, secondary finding, distinct from overlap: two metaphors in DIFFERENT stretches sharing an
    image word (e.g. 'staircase'). Legal under the overlap rule — non-simultaneous — but a reader meets the
    same vehicle twice meaning two things. Surfaced so the author can rename one or accept the echo."""
    if model is None:
        model = derive_model()
    tokens: "dict[str, list[Metaphor]]" = {}
    for m in model.metaphors:
        for t in _image_tokens(m):
            tokens.setdefault(t, []).append(m)

    findings: "list[str]" = []
    for token, group in sorted(tokens.items()):
        stretches = {g.stretch_key() for g in group}
        if len(group) >= 2 and len(stretches) >= 2:
            names = ", ".join(f"{g.slug!r} ({g.stretch_key()})" for g in group)
            findings.append(f"VEHICLE-COLLISION: the image word {token!r} carries {len(group)} metaphors across "
                            f"different stretches — {names}. Rename one or accept the echo.")
    return findings


# ---- coverage note (the audit-only one-liner catalog.py prints) -------------------------------------

def coverage_note(model: "MetaphorModel | None" = None) -> str:
    if model is None:
        model = derive_model()
    return (f"metaphor spans: {len(model.core())} core + {len(model.local())} local; "
            f"{compute_overlap_count(model)} overlap(s), {len(vehicle_collision_findings(model))} vehicle-collision(s) "
            f"(overlap non-gating until a clean session promotes it)")


# ---- projection: the inventory table ----------------------------------------------------------------

def _site_cell(site: "dict | None") -> str:
    if not isinstance(site, dict):
        return "—"
    chapter, page, anchor = site.get("chapter", ""), site.get("page_slug", ""), site.get("anchor", "")
    href = f"{page}.html#{anchor}" if anchor else f"{page}.html"
    return f"[{chapter}]({href})"


def render_table_rows(model: "MetaphorModel | None" = None) -> "list[str]":
    if model is None:
        model = derive_model()
    rows: "list[str]" = []
    for m in model.metaphors:
        rows.append(
            f"| **{m.name}** | {m.kind} | {_site_cell(m.introduced_at)} | "
            f"{_site_cell(m.pays_off_at) if m.kind == 'local' else '*always live*'} | {m.payoff} |"
        )
    return rows


def render_table_md(model: "MetaphorModel | None" = None) -> str:
    """The full markdown inventory table (header + rule + one row per metaphor)."""
    return "\n".join([_TABLE_HEADER, _TABLE_RULE, *render_table_rows(model)])


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_table() -> int:
    print(render_table_md())
    return 0


def _cmd_show() -> int:
    model = derive_model()
    print(f"overlap rule:\n  {model.overlap_rule}\n")
    for m in model.metaphors:
        intro = m.introduced_at
        span = f"intro {intro.get('chapter','?')}#{intro.get('anchor','') or '(page)'}"
        if m.kind == "local" and m.pays_off_at:
            span += f" -> pays off {m.pays_off_at.get('chapter','?')}#{m.pays_off_at.get('anchor','') or '(page)'}"
        else:
            span += " -> always live"
        print(f"[{m.kind:5}] {m.name}  ({span})")
    print(f"\n{len(model.core())} core · {len(model.local())} local · "
          f"{compute_overlap_count(model)} overlap(s) · {len(vehicle_collision_findings(model))} vehicle-collision(s)")
    return 0


def _cmd_anchors(argv: "list[str]") -> int:
    if len(argv) < 3:
        print(f"usage: {argv[0]} anchors <page_slug>")
        return 2
    page = argv[2]
    order = chapter_anchors(page)
    if not order:
        print(f"no anchors (or no such chapter): {page!r}")
        return 1
    for i, a in enumerate(order):
        print(f"{i:3}  {a}")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    structural = structural_findings(model)
    overlaps = overlap_findings(model)
    collisions = vehicle_collision_findings(model)
    if structural:
        print(f"metaphor-spans: {len(structural)} STRUCTURAL finding(s) (blocking):")
        for f in structural:
            print(f"  {f}")
    else:
        print(f"metaphor-spans structural checks pass ({len(model.core())} core, {len(model.local())} local).")
    print(f"metaphor-spans overlaps: {len(overlaps)} (audit-only; ratified {EXPECT_OVERLAPS})")
    for f in overlaps:
        print(f"  {f}")
    print(f"metaphor-spans vehicle-collisions: {len(collisions)} (audit-only, secondary)")
    for f in collisions:
        print(f"  {f}")
    # In sync iff structural clean AND overlaps within the ratified set.
    return 1 if (structural or len(overlaps) != EXPECT_OVERLAPS) else 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "table":
        return _cmd_table()
    if cmd == "show":
        return _cmd_show()
    if cmd == "anchors":
        return _cmd_anchors(argv)
    print(f"usage: {argv[0]} [verify|table|show|anchors <page_slug>]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
