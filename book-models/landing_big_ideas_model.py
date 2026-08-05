"""The CONCEPT-CARD projection model — one Concept Card page per Big Idea, projected from the declared
landing model so the card cannot drift from the model.

MODULE-NAME NOTE. The file mirrors its declared source `landing-big-ideas.json` (the repo's
`X.json <-> X_model.py` pairing), so the module keeps the "big-ideas" name even though the RENDERED
vocabulary is "Concept" — the six ideas are the site's Concepts section, rebranded from "Big Ideas."
A sibling of `metrics_dashboard_model.py` / `theory_of_mage_model.py`: the hand-authored source of truth
is `book-models/landing-big-ideas.json`; this module derives a typed model over the six idea records
(the `gateway` is not a concept), renders a Concept Card page body per idea, and reports the card
concerns with a non-overlapping drift check.

TWO CONCERNS, ONE SOURCE.
  - `render_concept_cards(svg_render=...)` — the ordered ConceptCardView list `catalog.py:cmd_build`
    writes as `concept-<slug>.html`. Each view carries the card BODY HTML (the six rendered sections;
    the "supporting examples" section is dropped permanently per the author, and Applications waits for
    Phase 3) plus the resolved outbound links. The model owns data->body; `catalog.py` owns the page
    chrome, the write, and the landing band link — so the model imports no catalog symbol (no circular
    import); the figure splice is injected as `svg_render(figure, ns)`.
  - `all_findings()` — the card drift check (CC1-CC4). It owns ONLY the NEW concerns (the two new-field
    schema, the Concept->mechanism edge, concept-page existence + landing linkage); `check_big_ideas` in
    catalog.py keeps owning band drift (book_home / figure / word-cap / id-on-landing) unchanged, so the
    two checks are non-overlapping.

Reads the meta-file at check time (no codegen, no snapshot). AUDIT-ONLY-first landing: `catalog.py
validate` prints the CC findings under an AUDIT-ONLY banner without gating; a follow-up flips them
BLOCKING once a clean session confirms the drain (the repo's blocking-lint landing discipline). The
thin `mechanisms: []` default keeps CC2 trivially green from day one.

Run `python3 book-models/landing_big_ideas_model.py verify` to drift-check (CC1-CC4, audit-only);
`... show` to list every concept and its declared mechanism edge.
"""
from __future__ import annotations

import html
import json
import os
import sys
from dataclasses import dataclass, field

from _projection_parity import (
    catalogue_entry_paths,
    catalogue_entry_slugs,
    require_fields,
    resolve_edges,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_DECLARED = os.path.join(_HERE, "landing-big-ideas.json")

#: The record that is NOT a concept — it fronts the catalogue's By-model view and gets no card
#: (consistent with check_big_ideas excluding it from projection).
_NON_CONCEPT = "gateway"

#: The existing rendered fields every Concept Card needs, non-empty (CC1). `intuition` maps to the JSON's
#: `more`; `figure`/`book_home` are resolved elsewhere (check_big_ideas owns their on-disk resolution).
_REQUIRED_RENDERED = ("title", "kicker", "claim", "figure", "book_home", "intuition")

#: A decorative single-accent "idea" glyph for the Concept chip — drawn in `currentColor` (inherits the
#: chip's `--accent`), so it carries no raw hex and needs no house SVG asset under book/assets/.
_CONCEPT_ICON = ('<svg class="cc-ico" viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
                 '<path fill="currentColor" d="M8 1.4a4.6 4.6 0 0 0-2.8 8.25c.42.33.68.72.78 1.15l.16.7h3.72'
                 'l.16-.7c.1-.43.36-.82.78-1.15A4.6 4.6 0 0 0 8 1.4Zm-1.85 11.3h3.7v1.05h-3.7V12.7Zm.62 '
                 '1.95h2.46v.35a1.23 1.23 0 0 1-2.46 0v-.35Z"/></svg>')


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class Concept:
    """One of the six Concepts. `slug` is the JSON key (== the `concept-<slug>.html` page slug), distinct
    from the existing `bi-<slug>` site id (`id`, the projection-drift join key). `intuition` is the
    existing `more` prose; `mechanisms` is the NEW hand-declared Concept->mechanism edge; `related_ideas`
    is the NEW optional Relationships override ([] => the projector uses the _order-adjacency seed)."""
    slug: str
    id: str
    title: str
    kicker: str
    claim: str
    figure: str
    intuition: str
    book_home: str
    mechanisms: "list[str]" = field(default_factory=list)
    related_ideas: "list[str]" = field(default_factory=list)


@dataclass
class ConceptModel:
    word_cap: int
    order: "list[str]"
    concepts: "list[Concept]"   # the six, in _order; gateway excluded


@dataclass
class ConceptCardView:
    """What `catalog.py:cmd_build` needs to write one `concept-<slug>.html`: the slug, the page title, the
    subtitle (the canonical claim), and the card body HTML (chrome-free — catalog.py `_page`-wraps it)."""
    slug: str
    title: str
    subtitle: str
    body_html: str


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def _concept_records(raw: "dict | None" = None) -> "list[tuple[str, dict]]":
    """The (slug, record) pairs for the six concepts in `_order` — `_`-keys and the gateway excluded."""
    if raw is None:
        raw = _load_declared()
    recs = {k: v for k, v in raw.items() if not k.startswith("_") and k != _NON_CONCEPT}
    order = raw.get("_order", [])
    return [(slug, recs[slug]) for slug in order if slug in recs]


def derive_model(raw: "dict | None" = None) -> ConceptModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and
    the checks share. Skips `_`-prefixed keys and the gateway; orders by `_order`."""
    if raw is None:
        raw = _load_declared()
    concepts = [
        Concept(
            slug=slug, id=rec.get("id", ""), title=rec.get("title", ""), kicker=rec.get("kicker", ""),
            claim=rec.get("claim", ""), figure=rec.get("figure", ""),
            intuition=rec.get("more", ""), book_home=rec.get("book_home", ""),
            mechanisms=list(rec.get("mechanisms", []) or []),
            related_ideas=list(rec.get("related_ideas", []) or []),
        )
        for slug, rec in _concept_records(raw)
    ]
    return ConceptModel(word_cap=raw.get("_word_cap", 26), order=raw.get("_order", []), concepts=concepts)


# ---- relationships seed -----------------------------------------------------------------------------

def _related_slugs(model: ConceptModel, c: Concept) -> "list[str]":
    """The Relationships targets: the curated `related_ideas` override if present, else the `_order`-
    adjacency seed (predecessor + successor; an endpoint links its one neighbour)."""
    if c.related_ideas:
        return c.related_ideas
    order = [x.slug for x in model.concepts]
    i = order.index(c.slug)
    seed = []
    if i > 0:
        seed.append(order[i - 1])
    if i < len(order) - 1:
        seed.append(order[i + 1])
    return seed


# ---- projection: the Concept Card body --------------------------------------------------------------

def _esc(s: str) -> str:
    return html.escape(str(s))


def _attr(s: str) -> str:
    return html.escape(str(s), quote=True)


def _placeholder_svg(figure: str, ns: str) -> str:
    """The default `svg_render` for standalone runs (verify/show) — the real figure splice is injected by
    catalog.py at build time; here we only need a stable stand-in that never touches the asset tree."""
    return f"<!-- figure: {figure} (ns {ns}) -->"


def _card_body(model: ConceptModel, c: Concept, svg_render) -> str:
    """The Concept Card body — the six rendered sections (examples omitted; Applications waits for Phase 3).
    The canonical claim rides in the page subtitle (catalog.py `_page`), so the body opens on the tinted
    Concepts band, then the concept title as the page's single top-level `<h1>` (the section headings stay
    `<h2>`), then the figure, engineering intuition, relationships, mechanisms, and read-more."""
    title_of = {x.slug: x.title for x in model.concepts}
    entry_href = catalogue_entry_paths()

    # 2 · Canonical figure — spliced with its ids namespaced per page (no landing/other-card id collision).
    fig_svg = svg_render(c.figure, f"cc-{c.slug}") if c.figure else ""
    fig = f'<figure class="cc-fig">{fig_svg}</figure>' if fig_svg else ""

    # 4 · Relationships — adjacency seed (or curated override), each -> its Concept Card.
    rel = _related_slugs(model, c)
    rel_items = "".join(
        f'<li><a href="concept-{_attr(s)}.html">{_esc(title_of.get(s, s))}</a></li>' for s in rel)
    rel_block = (f'<section class="cc-rel"><h2>Related concepts</h2><ul class="cc-links">{rel_items}</ul>'
                 f'</section>') if rel_items else ""

    # 5 · Mechanisms — the hand-declared Concept->mechanism edge (may be empty on a thin card).
    if c.mechanisms:
        mech_items = "".join(
            f'<li><a href="{_attr(entry_href.get(s, s + ".html"))}"><code>{_esc(s)}</code></a></li>'
            for s in c.mechanisms)
        mech_body = f'<ul class="cc-links">{mech_items}</ul>'
    else:
        mech_body = ('<p class="cc-mech-empty">No mechanism edge declared yet — this concept ships thin '
                     '(the edge is enriched in a later pass).</p>')
    mech_block = f'<section class="cc-mech"><h2>Mechanisms</h2>{mech_body}</section>'

    return (
        f'<div class="concept-band">'
        f'<span class="concept-chip">{_CONCEPT_ICON}Concept</span>'
        f'<span class="concept-kicker">{_esc(c.kicker)}</span>'
        f'</div>\n'
        f'<h1 class="cc-title">{_esc(c.title)}</h1>\n'
        f'{fig}\n'
        f'<section class="cc-intuition"><h2>Engineering intuition</h2><p>{_esc(c.intuition)}</p></section>\n'
        f'{rel_block}\n'
        f'{mech_block}\n'
        f'<section class="cc-read"><h2>Read more</h2>'
        f'<p><a class="cc-read-link" href="{_attr(c.book_home)}">Read in the book →</a></p></section>'
    )


def render_concept_cards(model: "ConceptModel | None" = None, svg_render=None) -> "list[ConceptCardView]":
    """One ConceptCardView per concept, in `_order` — the card bodies `catalog.py:cmd_build` `_page`-wraps
    and writes. `svg_render(figure, ns) -> str` splices the figure SVG (injected by catalog.py so the model
    imports no catalog symbol); it defaults to a placeholder for standalone runs."""
    if model is None:
        model = derive_model()
    if svg_render is None:
        svg_render = _placeholder_svg
    return [
        ConceptCardView(slug=c.slug, title=c.title, subtitle=c.claim,
                        body_html=_card_body(model, c, svg_render))
        for c in model.concepts
    ]


# ---- the drift check (CC1-CC4; non-overlapping with check_big_ideas) ---------------------------------

def schema_findings(model: "ConceptModel | None" = None) -> "list[str]":
    """CC1 — every concept carries the existing rendered fields non-empty AND the two new fields with the
    right type (`mechanisms` / `related_ideas` are lists of strings)."""
    if model is None:
        model = derive_model()
    findings = require_fields(model.concepts, _REQUIRED_RENDERED, "concept")
    for slug, rec in _concept_records():
        for key in ("mechanisms", "related_ideas"):
            val = rec.get(key, [])
            if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
                findings.append(f"CC1 concept {slug!r} field {key!r} must be a list of strings")
    return findings


def edge_findings(model: "ConceptModel | None" = None) -> "list[str]":
    """CC2 — every declared mechanism slug resolves to a real catalogue entry. CC3 — every related-ideas
    override slug (when used) resolves to one of the six concept slugs."""
    if model is None:
        model = derive_model()
    cc2 = resolve_edges(model.concepts, "mechanisms", catalogue_entry_slugs(), "CC2 concept→mechanism")
    concept_slugs = {c.slug for c in model.concepts}
    cc3 = resolve_edges(model.concepts, "related_ideas", concept_slugs, "CC3 concept→related-idea")
    return cc2 + cc3


def reachability_findings(model: "ConceptModel | None" = None) -> "list[str]":
    """CC4 — for each concept, `concept-<slug>.html` was written AND the landing carries a link to it
    (the model->site page-existence join). Best-effort: skips silently when the site is not built yet, so
    a pre-build `verify` does not false-fire (mirrors check_big_ideas's landing-scan best-effort)."""
    if model is None:
        model = derive_model()
    idx = os.path.join(_ROOT, "index.html")
    if not os.path.isfile(idx):
        return []
    landing = open(idx, encoding="utf-8").read()
    findings: "list[str]" = []
    for c in model.concepts:
        page = os.path.join(_ROOT, f"concept-{c.slug}.html")
        if not os.path.isfile(page):
            findings.append(f"CC4 concept {c.slug!r}: concept-{c.slug}.html was not written")
        if f'href="concept-{c.slug}.html"' not in landing:
            findings.append(f"CC4 concept {c.slug!r}: the landing carries no link to concept-{c.slug}.html")
    return findings


def all_findings(model: "ConceptModel | None" = None) -> "list[str]":
    """CC1-CC4 — the full Concept-Card drift check `catalog.py validate` runs (audit-only). Non-overlapping
    with `check_big_ideas` (which keeps band drift)."""
    if model is None:
        model = derive_model()
    return schema_findings(model) + edge_findings(model) + reachability_findings(model)


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_show() -> int:
    model = derive_model()
    for c in model.concepts:
        edge = ", ".join(c.mechanisms) if c.mechanisms else "(thin — no edge)"
        print(f"{c.slug:20} {c.title}")
        print(f"                     mechanisms: {edge}")
        print(f"                     related:    {', '.join(_related_slugs(model, c))}")
    print(f"\n{len(model.concepts)} concepts (gateway excluded)")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    if findings:
        print(f"concept-cards: {len(findings)} finding(s) "
              f"(audit-only — review candidates, not build stops):")
        for f in findings:
            print(f"  {f}")
        return 0  # audit-only: report, never gate
    print(f"concept-cards is in sync ({len(model.concepts)} concepts; schema clean; every mechanism edge "
          f"resolves; pages reachable)")
    return 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "show":
        return _cmd_show()
    print(f"usage: {argv[0]} [verify|show]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
