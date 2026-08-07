"""The SUPPORTING-SOURCES model — the book's Tier-2 corroboration corpus (engineering reports that reinforce
ONE observation somewhere in the manuscript) as a queryable, drift-gated MODEL rather than footnotes sprinkled
by hand. A SIBLING of the Tier-1 deep-case model (`industry_cases_declared.json` / `industry_cases_model.py`):
the hand-authored source of truth is `book-models/supporting_sources_declared.json`; this module derives a
typed model over it, projects the deterministic 3-channel render routing, exposes the live queries the corpus
unlocks, and holds the joins SS1-SS7 (destination-anchor / closed-vocab / citation / id / render-gate / caution
/ construct / channel-parity).

WHAT THIS TIER IS. A supporting source carries ONE extractable claim + a destination anchor + a caution. It
does NOT carry the Tier-1 apparatus (no rated construct matrix, no hypotheses[], no reciprocity). The two tiers
share the citation-key namespace and nothing else — that asymmetry is why this is a sibling model, not a `tier`
flag on `industry_cases`.

ONE SOURCE, MANY CONSUMERS.
  - `render_channel(source)` — the DETERMINISTIC 3-channel projection (body-known-use / footnote / bibliography),
    a pure function of (tier, role, corroboration_verdict); the encoded `channel` field is held equal to it by
    SS7, so a channel cannot drift from the record.
  - The live queries — `by-destination [<chapter>]` (every source landing in a chapter, grouped — the insertion
    worklist) · `by-role <role>` (all corroborate / challenge / illustrate / extend) · `channels` (the render
    projection over the whole corpus, segmented by channel) · `coverage` (N sources, N confirmed, the
    role/source_type/independence spread, and which MAGE constructs have external SUPPORTING observation via
    reinforces_construct) · `unverified` (every source at pending/unverifiable/contradicted — the fetch
    worklist).
  - `all_findings()` — the joins SS1-SS7. SS1 destination resolves (no dangling insertion); SS2 closed-vocab +
    citation join; SS3 id shape/uniqueness; SS4 render-gate coherence; SS5 caution presence for vendor sources;
    SS6 construct pointer resolves against the Tier-1 construct universe; SS7 encoded channel == derived channel.

LANDING: the whole band lands AUDIT-ONLY-first (rule-#55 blocking-lint discipline) — the `[supporting]` band in
`catalog.py validate` PRINTS its findings + the coverage note but does NOT increment the issue count; a follow-up
flips SS1-SS4 to BLOCKING once a clean session confirms the drain, the path every book model took. On first
landing the citation keys are all TO-ADD (none in references.bib / citations.json yet), so SS2b prints one
audit-only finding per record — EXPECTED; adding the bib entries is a separate single-writer batch.

Run `python3 book-models/supporting_sources_model.py verify` to drift-check; `... channels` for the render
projection; `... by-destination the-agent-stack` / `... by-role corroborate` / `... coverage` / `... unverified`
for the live queries; `... show` to list every source.
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
_DECLARED = os.path.join(_HERE, "supporting_sources_declared.json")
_REFERENCES_BIB = os.path.join(_BOOK, "references.bib")
_CITATIONS_JSON = os.path.join(_BOOK, "data", "citations.json")
_INDUSTRY_DECLARED = os.path.join(_HERE, "industry_cases_declared.json")

#: The render-channel enum (the deterministic §C projection). body-known-use is an inline SENTENCE; footnote an
#: elaboration; bibliography a terse bib line (Tier-3 academic only).
_CH_BODY = "body-known-use"
_CH_FOOTNOTE = "footnote"
_CH_BIB = "bibliography"

#: The verdicts that permit a body-known-use render (SS4). An unverified corroboration may not become an inline
#: claim — it degrades to a hedged footnote.
_BODY_OK_VERDICTS = ("confirmed", "adjusted")

#: The verdicts that force a footnote regardless of role (the §C projection's first gate).
_DEGRADE_VERDICTS = ("unverifiable", "pending")

#: The roles that route to the body when verified (convergence AND disconfirmation both surface, never buried).
_BODY_ROLES = ("corroborate", "challenge")

#: The source_type / independence values that MUST carry a non-empty caution (SS5 — the vendor honesty valve).
_VENDOR_SOURCE_TYPE = "vendor-product"
_VENDOR_INDEPENDENCE = "vendor-aligned"


# ---- typed model ------------------------------------------------------------------------------------

@dataclass
class Destination:
    """The manuscript anchor a source sits beside — a chapter label (or appendix stem) plus an OPTIONAL finer
    anchor (a heading slug or point slug walked in that chapter). `anchor is None` = chapter-level targeting,
    robust to in-chapter edits."""
    chapter: str
    anchor: "str | None"


@dataclass
class SupportingSource:
    """One Tier-2 source record — one extractable claim, a destination, a role, a caution, a verdict, and the
    drafted insertion `text` the prose wave consumes. `reinforces_construct` (nullable) is the narrow OPTIONAL
    single-construct pointer that resolves against the Tier-1 construct universe (SS6)."""
    id: str
    organization: str
    source_type: str
    url: str
    citation_key: str
    extractable_claims: "list[str]"
    destination: Destination
    role: str
    tier: str
    independence: str
    strength: str
    corroboration_verdict: str
    channel: str
    text: str
    caution: str
    reinforces_construct: "str | None" = None
    note: str = ""

    @property
    def is_vendor(self) -> bool:
        """A vendor-product genre OR a vendor-aligned independence — the SS5 caution-required set."""
        return self.source_type == _VENDOR_SOURCE_TYPE or self.independence == _VENDOR_INDEPENDENCE


@dataclass
class SupportingSourcesModel:
    sources: "list[SupportingSource]"

    def by_role(self, role: str) -> "list[SupportingSource]":
        return [s for s in self.sources if s.role == role]

    def by_channel(self, channel: str) -> "list[SupportingSource]":
        """Sources whose DERIVED render channel equals `channel` (the projection, not the stored field)."""
        return [s for s in self.sources if render_channel(s) == channel]

    def source_ids(self) -> "set[str]":
        return {s.id for s in self.sources}


# ---- load + build -----------------------------------------------------------------------------------

def _load_declared() -> dict:
    with open(_DECLARED, encoding="utf-8") as fh:
        return json.load(fh)


def derive_model(raw: "dict | None" = None) -> SupportingSourcesModel:
    """Build the typed model from the hand-authored declarations — the single derivation the projection and the
    checks and the queries share."""
    if raw is None:
        raw = _load_declared()
    sources: "list[SupportingSource]" = []
    for s in raw.get("supporting_sources", []):
        dest = s.get("destination", {}) or {}
        sources.append(SupportingSource(
            id=s.get("id", ""), organization=s.get("organization", ""),
            source_type=s.get("source_type", ""), url=s.get("url", ""),
            citation_key=s.get("citation_key", ""),
            extractable_claims=list(s.get("extractable_claims", []) or []),
            destination=Destination(chapter=dest.get("chapter", ""), anchor=dest.get("anchor")),
            role=s.get("role", ""), tier=s.get("tier", ""), independence=s.get("independence", ""),
            strength=s.get("strength", ""), corroboration_verdict=s.get("corroboration_verdict", ""),
            channel=s.get("channel", ""), text=s.get("text", ""), caution=s.get("caution", ""),
            reinforces_construct=s.get("reinforces_construct"), note=s.get("note", ""),
        ))
    return SupportingSourcesModel(sources=sources)


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


def _construct_universe() -> "set[str]":
    """The Tier-1 construct-universe column ids — the SS6 join target. Read from the sibling industry-cases
    declared source (the two models share the construct namespace; this is a read-only join, like
    industry_cases.hypotheses[] reads the theory H-ids)."""
    if not os.path.exists(_INDUSTRY_DECLARED):
        return set()
    with open(_INDUSTRY_DECLARED, encoding="utf-8") as fh:
        raw = json.load(fh)
    return {c.get("id", "") for c in raw.get("construct_universe", {}).get("columns", []) if c.get("id")}


def _appendix_stems() -> "set[str]":
    """The appendix-stem resolve set (the SS1 destination alternative to a chapter label). Collects every `.md`
    stem under the book's appendix subdirs — both the bare stem (`applying-the-recipe`) AND the subdir-qualified
    form (`appendix-skill-recipe/applying-the-recipe`) — plus the top-level built-appendix stems
    (`appendix-d-governance-conversion`), so both anchor forms the design names resolve."""
    stems: "set[str]" = set()
    if not os.path.isdir(_BOOK):
        return stems
    for entry in os.listdir(_BOOK):
        full = os.path.join(_BOOK, entry)
        if os.path.isdir(full) and entry.startswith("appendix-"):
            for fn in os.listdir(full):
                if fn.endswith(".md"):
                    stem = fn[:-3]
                    stems.add(stem)
                    stems.add(f"{entry}/{stem}")
        elif entry.startswith("appendix-") and entry.endswith(".html"):
            stems.add(entry[:-5])
    return stems


def _chapter_labels() -> "set[str]":
    """The number-free canonical chapter-label set (the SS1 primary destination resolve target)."""
    import chapter_identity_model as chapter_identity  # noqa: E402 — sibling book-model
    return chapter_identity.labels()


def _chapter_md_path(chapter: str) -> "str | None":
    import _book_pages  # noqa: E402 — shared book-page resolver
    return _book_pages.chapter_md_path(chapter)


# ---- projection: the deterministic 3-channel render routing ----------------------------------------

def render_channel(source: SupportingSource) -> str:
    """The house-style render channel for a source — a PURE function of (tier, role, corroboration_verdict),
    never hand-authored, so a channel cannot drift from the record (§C). SS7 holds the encoded `channel` equal
    to this.

      1. unverifiable / pending  -> footnote      (cannot make an unverified claim a body known-use)
      2. academic / paper        -> bibliography   (terse; research earns a citation, not a sentence)
      3. corroborate / challenge -> body-known-use (convergence AND disconfirmation both surface, never buried)
      4. illustrate / extend     -> footnote       (elaboration without independently establishing the claim)
    """
    if source.corroboration_verdict in _DEGRADE_VERDICTS:
        return _CH_FOOTNOTE
    if source.tier == "academic" or source.source_type == "paper":
        return _CH_BIB
    if source.role in _BODY_ROLES:
        return _CH_BODY
    return _CH_FOOTNOTE  # illustrate / extend (and any conservative default)


# ---- live queries ----------------------------------------------------------------------------------

def query_by_destination(chapter: "str | None" = None,
                         model: "SupportingSourcesModel | None" = None) -> "dict[str, list[SupportingSource]]":
    """Every supporting source grouped by destination chapter (optionally filtered to one chapter). Answers
    'what corroboration sits in Brownfield / the-agent-stack / §6.3' — drives the insertion pass."""
    if model is None:
        model = derive_model()
    out: "dict[str, list[SupportingSource]]" = {}
    for s in model.sources:
        if chapter is not None and s.destination.chapter != chapter:
            continue
        out.setdefault(s.destination.chapter, []).append(s)
    return out


def query_channels(model: "SupportingSourcesModel | None" = None) -> "dict[str, list[SupportingSource]]":
    """The render-channel projection over the whole corpus — the insertion worklist segmented by channel
    (body-known-use / footnote / bibliography)."""
    if model is None:
        model = derive_model()
    out: "dict[str, list[SupportingSource]]" = {_CH_BODY: [], _CH_FOOTNOTE: [], _CH_BIB: []}
    for s in model.sources:
        out.setdefault(render_channel(s), []).append(s)
    return out


def query_coverage(model: "SupportingSourcesModel | None" = None) -> dict:
    """The burndown: N sources, N confirmed/adjusted (renderable), the role / source_type / independence /
    channel spread, and (via reinforces_construct) which MAGE constructs have external SUPPORTING observation —
    complementary to the Tier-1 only-docable gap query."""
    if model is None:
        model = derive_model()
    srcs = model.sources
    renderable = [s for s in srcs if s.corroboration_verdict in _BODY_OK_VERDICTS]
    constructs = sorted({s.reinforces_construct for s in srcs if s.reinforces_construct})
    channels = query_channels(model)

    def spread(attr) -> "list[str]":
        return sorted({getattr(s, attr) for s in srcs})

    return {
        "sources": len(srcs),
        "renderable": len(renderable),
        "constructs_supported": constructs,
        "role_spread": spread("role"),
        "source_type_spread": spread("source_type"),
        "independence_spread": spread("independence"),
        "channel_counts": {ch: len(v) for ch, v in channels.items()},
    }


def query_unverified(model: "SupportingSourcesModel | None" = None) -> "list[SupportingSource]":
    """Every source at pending / unverifiable / contradicted — the corroboration-pass worklist (what still needs
    a fetch, what failed)."""
    if model is None:
        model = derive_model()
    return [s for s in model.sources
            if s.corroboration_verdict in ("pending", "unverifiable", "contradicted")]


# ---- invariants (SS1-SS7) ---------------------------------------------------------------------------

def all_findings(model: "SupportingSourcesModel | None" = None) -> "list[str]":
    """The joins SS1-SS7. Each finding is a defect the gate should catch once this band is promoted to BLOCKING.
    This whole band is wired AUDIT-ONLY-first (rule-#55): a follow-up promotes SS1-SS4 to BLOCKING once a clean
    session confirms the drain (SS5-SS7 stay audit-only longer while early records churn).

    SS1 destination resolves — every destination.chapter is a real chapter label OR appendix stem (no dangling
        insertion); a non-null destination.anchor resolves as a heading/point slug inside that chapter.
    SS2 closed-vocab membership — role / tier / source_type / independence / strength / corroboration_verdict /
        channel each in their declared set; SS2b citation join — citation_key resolves in references.bib AND
        appears in citations.json (a source with no bib entry cannot carry a [cite:] marker).
    SS3 id shape + uniqueness — kebab, unique (the reverse-index symbol).
    SS4 render-gate coherence — a source whose DERIVED channel is body-known-use must have verdict in
        {confirmed, adjusted} (an unverified corroboration may not become an inline claim).
    SS5 caution presence — a vendor-product / vendor-aligned source with an empty caution reddens.
    SS6 construct join — a non-null reinforces_construct resolves against the Tier-1 construct universe.
    SS7 channel parity — the encoded `channel` equals the deterministic render_channel projection (the stored
        field the prose wave consumes cannot drift from the projection).
    """
    if model is None:
        model = derive_model()
    raw = _load_declared()
    taxonomy = raw.get("_taxonomy", {})

    chapter_labels = _chapter_labels()
    appendix_stems = _appendix_stems()
    bib, cites = _bib_keys(), _citation_keys()
    constructs = _construct_universe()

    findings: "list[str]" = []
    seen: "set[str]" = set()

    for s in model.sources:
        sid = s.id or "<empty-id>"

        # SS3 — id shape + uniqueness.
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s.id or ""):
            findings.append(f"SS3 source {sid!r} id is not kebab-case")
        if s.id in seen:
            findings.append(f"SS3 duplicate source id {s.id!r}")
        seen.add(s.id)

        # SS1 — destination resolves (chapter, then optional anchor).
        chapter = s.destination.chapter
        if chapter not in chapter_labels and chapter not in appendix_stems:
            findings.append(f"SS1 source {sid!r} destination.chapter {chapter!r} resolves to no chapter label "
                            f"or appendix stem (dangling insertion)")
        elif s.destination.anchor:
            findings.extend(_anchor_findings(sid, chapter, s.destination.anchor))

        # SS2 — closed-vocab membership.
        for f_name, val in (("role", s.role), ("tier", s.tier), ("source_type", s.source_type),
                            ("independence", s.independence), ("strength", s.strength),
                            ("corroboration_verdict", s.corroboration_verdict), ("channel", s.channel)):
            vocab = taxonomy.get(f_name, [])
            if val and vocab and val not in vocab:
                findings.append(f"SS2 source {sid!r} {f_name} {val!r} not in taxonomy {f_name}")

        # SS2b — citation join (one finding per record; keys are model-side proposals until the bib batch lands).
        key = s.citation_key
        if not key:
            findings.append(f"SS2b source {sid!r} has no citation_key")
        else:
            missing = [t for t, present in (("references.bib", key in bib), ("citations.json", key in cites))
                       if not present]
            if missing:
                findings.append(f"SS2b source {sid!r} citation_key {key!r} is TO-ADD "
                                f"(absent from {' + '.join(missing)})")

        # SS4 — render-gate coherence (a body known-use must be verified).
        if render_channel(s) == _CH_BODY and s.corroboration_verdict not in _BODY_OK_VERDICTS:
            findings.append(f"SS4 source {sid!r} derives channel body-known-use but verdict "
                            f"{s.corroboration_verdict!r} is not in {_BODY_OK_VERDICTS}")

        # SS5 — caution presence for vendor sources.
        if s.is_vendor and not s.caution.strip():
            findings.append(f"SS5 vendor source {sid!r} ({s.source_type}/{s.independence}) has an empty caution")

        # SS6 — construct pointer resolves against the Tier-1 construct universe.
        if s.reinforces_construct is not None:
            if constructs and s.reinforces_construct not in constructs:
                findings.append(f"SS6 source {sid!r} reinforces_construct {s.reinforces_construct!r} resolves "
                                f"against no Tier-1 construct-universe column")

        # SS7 — encoded channel == derived channel.
        derived = render_channel(s)
        if s.channel and s.channel != derived:
            findings.append(f"SS7 source {sid!r} encoded channel {s.channel!r} != derived channel {derived!r} "
                            f"(role {s.role!r}, verdict {s.corroboration_verdict!r})")

    return findings


def _anchor_findings(sid: str, chapter: str, anchor: str) -> "list[str]":
    """SS1 anchor resolution — a non-null destination.anchor must match a `## Heading` slug (title -> kebab) OR
    a `<!-- point: <slug> ... -->` marker slug in the chapter's markdown."""
    path = _chapter_md_path(chapter)
    if not path or not os.path.isfile(path):
        return [f"SS1 source {sid!r} anchor {anchor!r}: chapter {chapter!r} has no readable markdown to walk"]
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    heading_slugs = {_slugify(m) for m in re.findall(r"^##+\s+(.*)$", text, flags=re.MULTILINE)}
    point_slugs = set(re.findall(r"<!--\s*point:\s*([a-z0-9][a-z0-9-]*)", text))
    if anchor in heading_slugs or anchor in point_slugs:
        return []
    return [f"SS1 source {sid!r} anchor {anchor!r} resolves to no `## Heading` slug or `<!-- point: -->` "
            f"marker in {chapter!r}"]


def _slugify(heading: str) -> str:
    """A `## Heading Text` -> `heading-text` kebab slug (lowercase, non-alnum -> hyphen, collapsed/trimmed)."""
    s = re.sub(r"[^a-z0-9]+", "-", heading.strip().lower())
    return s.strip("-")


def coverage_note(model: "SupportingSourcesModel | None" = None) -> str:
    """A one-line burndown for the validate band — N sources, N renderable, the channel split, and how many MAGE
    constructs have external supporting observation."""
    if model is None:
        model = derive_model()
    cov = query_coverage(model)
    cc = cov["channel_counts"]
    return (f"{cov['sources']} supporting sources · {cov['renderable']} renderable (confirmed/adjusted) · "
            f"channels: {cc.get(_CH_BODY, 0)} body-known-use / {cc.get(_CH_FOOTNOTE, 0)} footnote / "
            f"{cc.get(_CH_BIB, 0)} bibliography · "
            f"{len(cov['constructs_supported'])} MAGE construct(s) with external supporting observation")


# ---- CLI --------------------------------------------------------------------------------------------

def _cmd_by_destination(chapter: "str | None") -> int:
    model = derive_model()
    groups = query_by_destination(chapter, model)
    if not groups:
        print(f"(no supporting source lands in {chapter!r})" if chapter else "(no supporting sources)")
        return 0
    for chap in sorted(groups):
        print(f"{chap}:")
        for s in groups[chap]:
            print(f"  [{render_channel(s):<14}] {s.id:<32} {s.role:<12} {s.organization}")
    return 0


def _cmd_by_role(role: str) -> int:
    model = derive_model()
    srcs = model.by_role(role)
    if not srcs:
        print(f"(no supporting source with role {role!r})")
        return 0
    for s in srcs:
        print(f"[{render_channel(s):<14}] {s.id:<32} {s.destination.chapter:<32} {s.organization}")
    return 0


def _cmd_channels() -> int:
    model = derive_model()
    channels = query_channels(model)
    for ch in (_CH_BODY, _CH_FOOTNOTE, _CH_BIB):
        srcs = channels.get(ch, [])
        print(f"{ch} ({len(srcs)}):")
        for s in srcs:
            print(f"  {s.id:<32} {s.role:<12} {s.destination.chapter:<32} {s.organization}")
    return 0


def _cmd_coverage() -> int:
    model = derive_model()
    cov = query_coverage(model)
    print(coverage_note(model))
    print(f"  role spread:         {', '.join(cov['role_spread']) or '—'}")
    print(f"  source_type spread:  {', '.join(cov['source_type_spread']) or '—'}")
    print(f"  independence spread: {', '.join(cov['independence_spread']) or '—'}")
    print(f"  constructs supported: {', '.join(cov['constructs_supported']) or '—'}")
    return 0


def _cmd_unverified() -> int:
    model = derive_model()
    srcs = query_unverified(model)
    if not srcs:
        print("(no unverified source — every source is confirmed or adjusted)")
        return 0
    for s in srcs:
        print(f"[{s.corroboration_verdict:<13}] {s.id:<32} {s.url}")
    return 0


def _cmd_show() -> int:
    model = derive_model()
    for s in model.sources:
        cons = f" -> {s.reinforces_construct}" if s.reinforces_construct else ""
        print(f"[{render_channel(s):<14}] {s.id:<32} {s.role:<12} {s.corroboration_verdict:<10} "
              f"{s.destination.chapter}{cons}")
    print(f"\n{len(model.sources)} supporting sources")
    return 0


def _cmd_verify() -> int:
    model = derive_model()
    findings = all_findings(model)
    print(f"supporting-sources: {coverage_note(model)}")
    if findings:
        print(f"supporting-sources: {len(findings)} finding(s) (AUDIT-ONLY this wave — does not gate validate):")
        for f in findings:
            print(f"  {f}")
        return 1
    print("supporting-sources: schema + joins clean (SS1-SS7)")
    return 0


def main(argv: "list[str]") -> int:
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd == "verify":
        return _cmd_verify()
    if cmd == "by-destination":
        return _cmd_by_destination(argv[2] if len(argv) > 2 else None)
    if cmd == "by-role":
        if len(argv) < 3:
            print("usage: supporting_sources_model.py by-role <corroborate|illustrate|challenge|extend>")
            return 2
        return _cmd_by_role(argv[2])
    if cmd == "channels":
        return _cmd_channels()
    if cmd == "coverage":
        return _cmd_coverage()
    if cmd == "unverified":
        return _cmd_unverified()
    if cmd == "show":
        return _cmd_show()
    print(f"usage: {argv[0]} [verify|by-destination [<chapter>]|by-role <role>|channels|coverage|unverified|show]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
