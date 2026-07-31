#!/usr/bin/env python3
"""Validate and query the governance-catalogue metadata schema.

Self-contained (stdlib only) so it runs from the catalogue root whether embedded in a
parent repo or checked out standalone. Subcommands:

    catalog.py validate            # schema + INDEX-consistency + link-integrity; exit 1 on any violation
    catalog.py query [filters]     # list/filter entries; --json for structured output

Exit codes (per the subprocess convention): 0 = success, 1 = validation failure / bad usage.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Single source of truth for the book's cover identity (title/subtitle/kicker/author). Also read by
# book/build_book_html.py (print cover + web front page) — edit book/book-manifest.json once, all follow.
BOOK_MANIFEST = json.loads(open(os.path.join(ROOT, "book", "book-manifest.json"), encoding="utf-8").read())
_PDF_HREF = "book/" + BOOK_MANIFEST["pdf_filename"]  # root-relative href to the published PDF (single source: the manifest)


def _book_title_block() -> str:
    """The site-landing hero title + optional subtitle, from BOOK_MANIFEST (single source of truth)."""
    sub = BOOK_MANIFEST.get("subtitle", "")
    h1 = f'<h1 class="book-h1">{html.escape(BOOK_MANIFEST["title"])}</h1>'
    return h1 + (f'\n      <div class="book-sub">{html.escape(sub)}</div>' if sub else "")

# Directories that hold .html but are never part of the served/deployed site — the gitignored scratch
# tree (`_drafts/`), the skill bundle (markdown, not a site), the dev-only axe tree, and the serve dirs.
# CI never checks these out, so they must be excluded from every local walk (orphan gate, axe,
# html-validate) or the local build/test diverges from CI. `_drafts/` is the canonical case: gitignored
# design-stage HTML that the orphan gate would otherwise flag as unreachable, breaking `catalog.py build`
# locally while CI (which lacks the dir) stays green.
NON_SITE_DIRS = ("plugin", "node_modules", "site", "_site", ".git", "__pycache__", "hooks", "_drafts", "_print")


def gitignored_top_dirs() -> frozenset[str]:
    """Top-level directory names under ROOT that git ignores. Used to prune the site walks so a
    gitignored scratch tree (absent from a fresh CI checkout) can't perturb a local build/test. Empty
    when not a git tree (fail-safe: prune nothing extra — the static NON_SITE_DIRS list still applies)."""
    try:
        dirs = [e.name for e in os.scandir(ROOT) if e.is_dir() and e.name != ".git"]
    except OSError:
        return frozenset()
    if not dirs:
        return frozenset()
    try:
        r = subprocess.run(["git", "-C", ROOT, "check-ignore", *dirs],
                           capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    # check-ignore exits 0 (some ignored), 1 (none ignored), 128 (not a git repo) — read stdout regardless.
    return frozenset(ln.strip("/").strip() for ln in r.stdout.splitlines() if ln.strip())


def site_prune_dirs() -> frozenset[str]:
    """The full set of directory names to prune from a site walk: the static non-site dirs plus every
    gitignored top-level dir (catches `_drafts/` and any future gitignored scratch dir)."""
    return frozenset(NON_SITE_DIRS) | gitignored_top_dirs()


FORMS = {
    "typed-ir", "validation", "repair-vocab", "agent-output", "bounded-service",
    "regression", "quality-gate", "observability", "audit-trail",
}
ROLES = {"Agent", "Bridge", "Product"}
ENF_CLASSES = {"Hard", "Soft", "Soft·Hard"}
# The metadata card carries two book-thesis cross-cuts beside soft/hard enforcement:
#   Move  (Alignment Thesis, book part 2.3) — how the mechanism holds a quality goal.
#   Model (Modeling Thesis, book part 2.2)  — its relation to a typed model.
# Both independent of soft/hard: a `constraint` can be soft or hard; an `is-a-model` can be any Move.
# `Derivation` is optional and appears ONLY on is-a-model entries (book part 3.1 Beat 2).
MOVE_CLASSES = {"constraint", "sensor", "package"}      # prevent · detect · both-bundled
MODEL_CLASSES = {"is-a-model", "governs-a-model", "—"}  # a typed model · gates/generates/queries one · neither
DERIVATION_CLASSES = {"model-from-code", "model-to-code", "both"}
META_ORDER = ["Summary", "Target", "Form", "Move", "Model", "Enforcement"]  # + optional trailing "Derivation"
SUMMARY_MAX = 100  # chars — a tooltip-friendly gloss, deliberately shorter than Intent
SECTION_ORDER = [
    "Motivation", "Why it's not just", "Mechanism", "Prerequisites",
    "Consequences & costs", "Known uses", "Related mechanisms",
]
# Canonical relationship vocabulary — a tight, UML-informed set (owner-ruled: the off-canonical variants
# in the corpus were prior-LLM tagging drift, not authorial nuance; consolidate direction-variants into
# one direction-neutral tag each). Every Related-mechanisms bullet's lead tag (minus any trailing
# "(qualifier)") MUST be one of these; the validator enforces membership.
#   Counterpart    — a paired opposite / twin: two mechanisms that mirror each other (incl. a temporal twin).
#   Generalization — an is-a / kind-of relation, direction-neutral: one is a special case, instance, or
#                    realization of a more general pattern (folds Specializes / Specialized-by / Instance-of /
#                    Realizes / Kin — the whole taxonomic family, either direction).
#   Enabler        — one makes the other possible (the "how" or precondition of the other).
#   Consumer       — one reads / uses / is fed by the other (the supplier↔consumer relation, incl. "ground truth").
#   Layer          — one is built atop the other (a stacking / composition relation).
#   Bridge         — couples across two roles (the models-bridge's defining cross-role relation).
#   Sibling        — the same pattern or method applied to a different subject (a peer, not a parent/child).
#   See also       — a looser association; the qualified form "See also (qualifier)" carries a flavour word.
REL_TAGS = ("Counterpart", "Generalization", "Enabler", "Consumer", "Layer", "Bridge", "Sibling", "See also")
ROLE_DIRS = ["agent", "models-bridge", "product"]

# ── Abstractions glossary (the interpretability de-referencer) ──
# Entries cite concrete artifacts as [[slug]] / [[slug|text]] rather than by unshipped filename.
ABBR_SRC = "ABSTRACTIONS.md"
ABBR_CITE_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
# An "unshipped" reference = a backticked path with one of these extensions whose basename is NOT present
# anywhere in this repo (so `catalog.py` — which ships here — is allowed; `components.py` is not).
RAW_FILE_RE = re.compile(r"`([^`]+?\.(?:py|cs|jsonl|ya?ml))`")
RULE_CITE_RE = re.compile(r"(?<![\w.])#\d{1,2}\b")  # bare project-rule citation (meaningless outside the parent)
# Not served / not link-checked: internal continuity docs (the abstractions playbook is process, not content).
NOSERVE = ("HANDOFF.md", "HANDOFF-catalogue-agent.md", "abstractions-playbook.md", "TODO.md",
           "WRITING-BACKLOG.md", "SUBMISSION.md", "PRIVACY.md", "DEVELOP.md", "CLAUDE.md")

# Declared stats — the facts not derivable from the entries (LOC, case-study length). Everything else in
# _stats() is computed from the catalogue itself. Edit a number here, once.
# Scale figures derive from the book's canonical data feed (book/data/metrics.json) — the SAME source
# the book prose reads — so the catalogue and the book never disagree (was hard-coded 430/12, which had
# drifted from the manuscript's 490K / 19-week figures).
_BOOK_METRICS = json.loads(open(os.path.join(ROOT, "book", "data", "metrics.json"), encoding="utf-8").read())
DECLARED_STATS = {
    "loc_kloc": round(int(_BOOK_METRICS["prod_loc"].replace(",", "")) / 1000),
    "case_study_weeks": int(_BOOK_METRICS["study_weeks"]),
}


class Entry:
    """A parsed catalogue entry with its metadata card and section structure."""

    def __init__(self, path: str) -> None:
        self.path = os.path.relpath(path, ROOT)
        self.text = open(path, encoding="utf-8").read()
        self.issues: list[str] = []
        self.meta: dict[str, str] = {}
        self._parse()

    def _parse(self) -> None:
        t = self.text
        if not re.search(r"^# \S", t, re.M):
            self.issues.append("missing '# ' title")
        if not re.search(r"^\*\*Intent\*\* —", t, re.M):
            self.issues.append("missing '**Intent** —' line")
        if "🚧" in t:
            self.issues.append("carries a 🚧 stub banner")

        # Recognized metadata labels = the six required (META_ORDER) + the optional trailing Derivation.
        META_LABELS = META_ORDER + ["Derivation"]
        rows = re.findall(r"^\| ([^|]+?) \| (.+?) \|$", t, re.M)
        self.meta = {k.strip(): v.strip() for k, v in rows if k.strip() in META_LABELS}
        labels = [k.strip() for k, _ in rows if k.strip() in META_LABELS]
        # The six required rows must appear in order; Derivation, if present, must trail them.
        if labels[:len(META_ORDER)] != META_ORDER or labels[len(META_ORDER):] not in ([], ["Derivation"]):
            self.issues.append(f"metadata rows/order = {labels or '(none)'}")

        self.form = None
        m = re.search(r"`([a-z-]+)`", self.meta.get("Form", ""))
        self.form = m.group(1) if m else None
        if self.form not in FORMS:
            self.issues.append(f"bad Form: {self.meta.get('Form', '(missing)')!r}")

        tgt = self.meta.get("Target", "")
        m = re.match(r"(Agent|Bridge|Product) · \*?\*?(.+?)\*?\*?$", tgt)
        self.role = m.group(1) if m else None
        self.family = re.sub(r"\*", "", m.group(2)).strip() if m else None
        if self.role not in ROLES:
            self.issues.append(f"bad Target role: {tgt!r}")

        # Move (Alignment-Thesis axis): the value is the `code`-spanned token in the row.
        self.move = None
        m = re.search(r"`([a-z-]+)`", self.meta.get("Move", ""))
        self.move = m.group(1) if m else None
        if self.move not in MOVE_CLASSES:
            self.issues.append(f"bad Move: {self.meta.get('Move', '(missing)')!r} "
                               f"(∈ {sorted(MOVE_CLASSES)})")

        # Model (Modeling-Thesis axis): a `code`-spanned value, one of is-a-model / governs-a-model / —.
        self.model = None
        m = re.search(r"`(is-a-model|governs-a-model|—)`", self.meta.get("Model", ""))
        if m is None and self.meta.get("Model", "").strip() == "—":
            self.model = "—"  # allow a bare em-dash (no code span) for the 'neither' value
        else:
            self.model = m.group(1) if m else None
        if self.model not in MODEL_CLASSES:
            self.issues.append(f"bad Model: {self.meta.get('Model', '(missing)')!r} "
                               f"(∈ {sorted(MODEL_CLASSES)})")

        # Derivation (optional): allowed ONLY on is-a-model entries; value ∈ model-from-code/model-to-code/both.
        self.derivation = None
        if "Derivation" in self.meta:
            m = re.search(r"`([a-z-]+)`", self.meta["Derivation"])
            self.derivation = m.group(1) if m else self.meta["Derivation"].strip()
            if self.derivation not in DERIVATION_CLASSES:
                self.issues.append(f"bad Derivation: {self.meta['Derivation']!r} "
                                   f"(∈ {sorted(DERIVATION_CLASSES)})")
            if self.model != "is-a-model":
                self.issues.append("Derivation row present but Model is not `is-a-model` "
                                   "(Derivation is only for is-a-model entries)")

        m = re.search(r"\*\*(Soft·Hard|Hard|Soft)\*\*", self.meta.get("Enforcement", ""))
        self.enf = m.group(1) if m else None
        if self.enf not in ENF_CLASSES:
            self.issues.append(f"Enforcement has no soft/hard class: {self.meta.get('Enforcement', '')[:50]!r}")

        self.summary = self.meta.get("Summary", "").strip()
        if not self.summary:
            self.issues.append("missing Summary row (needed for hover tooltips)")
        elif len(self.summary) > SUMMARY_MAX:
            self.issues.append(f"Summary too long ({len(self.summary)} > {SUMMARY_MAX} chars): tighten for tooltip")

        secs = [ln[3:].strip() for ln in t.splitlines() if ln.startswith("## ")]
        idxs: list[int] = []
        for canon in SECTION_ORDER:
            hits = [i for i, s in enumerate(secs) if s.startswith(canon)]
            if len(hits) != 1:
                self.issues.append(f"section '{canon}' appears x{len(hits)}")
            else:
                idxs.append(hits[0])
        if idxs != sorted(idxs):
            self.issues.append(f"sections out of order: {secs}")

        rel = t.split("## Related mechanisms")[-1] if "## Related mechanisms" in t else ""
        bullets = re.findall(r"^- (.+)$", rel, re.M)
        if not bullets:
            self.issues.append("no Related-mechanisms bullets")
        else:
            # Membership check: every top-level Related bullet must LEAD with a bold/italic relationship
            # tag drawn from the canonical REL_TAGS set. The lead tag, minus any trailing "(qualifier)",
            # must be ∈ REL_TAGS — the vocabulary is a closed, principled set (owner-ruled; the prior
            # off-canonical variants were tagging drift, not authorial nuance). A malformed/untagged bullet
            # or an off-canonical tag is a finding.
            for b in bullets:
                m = re.match(r"\*\*(.+?)\*\*|\*(.+?)\*", b.strip())
                if not m:
                    self.issues.append(f"Related-mechanisms: bullet without a relationship-tag lead: {b[:45]!r}")
                    continue
                lead = (m.group(1) or m.group(2)).strip()
                base = re.sub(r"\s*\(.*\)\s*$", "", lead).strip()  # drop a trailing "(qualifier)"
                base = base.rstrip(":")                            # tolerate a trailing colon lead
                if base not in REL_TAGS:
                    self.issues.append(
                        f"Related-mechanisms: off-canonical relationship tag {lead!r} "
                        f"(∈ {list(REL_TAGS)})")

    def title_only(self) -> str:
        m = re.search(r"^# (.+)$", self.text, re.M)
        return m.group(1).strip() if m else self.path

    def as_dict(self) -> dict:
        return {
            "path": self.path, "role": self.role, "family": self.family,
            "form": self.form, "move": self.move, "model": self.model,
            "derivation": self.derivation, "enforcement": self.enf, "summary": self.summary,
            "title": (re.search(r"^# (.+)$", self.text, re.M) or [None, self.path])[1],
        }


def all_entries() -> list[Entry]:
    paths = sorted(
        p for d in ROLE_DIRS for p in glob.glob(os.path.join(ROOT, d, "*", "*.md"))
    )
    return [Entry(p) for p in paths]


def catalogue_md_files() -> list[str]:
    """Every markdown file that IS the catalogue: root-level docs + the role trees.

    Deliberately excludes non-catalogue trees under ROOT (e.g. an untracked packaged-skill copy in
    `plugin/`) and the raw-asset / internal-continuity files, so the tooling never processes a mirror.
    """
    out = []
    for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        top = rel.split(os.sep)[0]
        if os.sep in rel and top not in ROLE_DIRS:
            continue  # nested under a non-catalogue dir (packaged copy, downloads, etc.)
        if os.path.basename(f) in NOSERVE:
            continue  # internal continuity docs: not rendered/served
        if os.path.basename(f).startswith("HANDOFF"):
            continue  # gitignored per-run handoff records (/HANDOFF*.md) — never rendered/served
        if os.path.basename(f).startswith("BOOK-PROPOSAL"):
            continue  # gitignored local book-proposal drafts (/BOOK-PROPOSAL*.md) — never rendered/served
        if ".local." in os.path.basename(f):
            continue  # local scratch (gitignored `*.local.md` convention) — never rendered/served
        out.append(f)
    return out


def check_links() -> list[str]:
    dead = []
    for f in catalogue_md_files():
        base = os.path.dirname(f)
        body = open(f, encoding="utf-8").read()
        for m in re.finditer(r"\]\(([^)]+\.md)(#[^)]*)?\)", body):
            if m.group(1).startswith(("http://", "https://")):
                continue  # external URL (e.g. a GitHub blob link) — not a local path to resolve
            tgt = os.path.normpath(os.path.join(base, m.group(1)))
            if not os.path.exists(tgt):
                dead.append(f"{os.path.relpath(f, ROOT)} -> {m.group(1)}")
    return dead


def check_index(entries: list[Entry]) -> list[str]:
    idx_path = os.path.join(ROOT, "INDEX.md")
    if not os.path.exists(idx_path):
        return ["INDEX.md missing"]
    idx = open(idx_path, encoding="utf-8").read()
    by_path = {e.path: e for e in entries}
    # INDEX row now carries Move + Model columns between Form and Enf:
    #   | ✓ | Mechanism | `form` | `move` | `model` | Enf. | [entry](path) |
    rows = re.findall(
        r"^\| (?:✅|☐)[^|]*\| ([^|]+?) \| `([a-z-]+)` \| `([a-z-]+)` \| (`[a-z-]+`|—) \| "
        r"([^|]+?) \| \[[^\]]+\]\(([^)]+)\) \|$",
        idx, re.M,
    )
    problems = []
    for _ctrl, iform, imove, imodel_raw, ienf, path in rows:
        imodel = imodel_raw.strip("`")  # bare em-dash stays "—"; `is-a-model` → is-a-model
        e = by_path.get(os.path.normpath(path))
        if e is None:
            problems.append(f"INDEX row links unknown entry: {path}")
            continue
        ienf_base = re.sub(r"\*|\(.*", "", ienf).strip()
        if e.form != iform:
            problems.append(f"FORM mismatch {path}: INDEX=`{iform}` entry=`{e.form}`")
        if e.move != imove:
            problems.append(f"MOVE mismatch {path}: INDEX=`{imove}` entry=`{e.move}`")
        if e.model != imodel:
            problems.append(f"MODEL mismatch {path}: INDEX=`{imodel}` entry=`{e.model}`")
        if e.enf != ienf_base:
            problems.append(f"ENF mismatch {path}: INDEX={ienf_base} entry={e.enf}")
    if len(rows) != len(entries):
        problems.append(f"INDEX rows ({len(rows)}) != entry files ({len(entries)})")
    return problems


ROLE_READMES = ["README.md", "agent/README.md", "models-bridge/README.md", "product/README.md"]


def role_summaries() -> dict:
    """<!-- summary: … --> from each tiered README (umbrella + the three roles)."""
    out = {}
    for rel in ROLE_READMES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            m = re.search(r"<!-- summary: (.+?) -->", open(p, encoding="utf-8").read())
            out[rel] = (m.group(1).strip() if m else "")
    return out


def family_summaries() -> dict:
    """Family → the italic one-liner under its INDEX ## header (reused as the family tooltip)."""
    idx = os.path.join(ROOT, "INDEX.md")
    if not os.path.exists(idx):
        return {}
    text = open(idx, encoding="utf-8").read()
    return {m.group(1).strip(): m.group(2).strip()
            for m in re.finditer(r"^## \d+\. (.+?)\n\n\*(.+?)\*", text, re.M)}


def parse_abstractions() -> dict:
    """Parse ABSTRACTIONS.md → {slug: {headword, definition, tail(md), raw}}.

    Entry shape: `## Headword` · `<!-- slug: x -->` · a definition paragraph · a `**Grounds** … **See** …`
    tail. The definition (plain-texted) is the hover tooltip; the tail names the real artifact once.
    """
    p = os.path.join(ROOT, ABBR_SRC)
    if not os.path.exists(p):
        return {}
    text = open(p, encoding="utf-8").read()
    out: dict = {}
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = block.splitlines()
        headword = lines[0].strip()
        m = re.search(r"<!-- slug: (\S+) -->", block)
        if not m:
            continue
        slug = m.group(1)
        body = [ln for ln in lines[1:] if not ln.strip().startswith("<!-- slug:")]
        defn, tail = [], []
        for ln in body:
            (tail if ln.strip().startswith("**Grounds**") or tail else defn).append(ln)
        out[slug] = {
            "headword": headword,
            "definition": " ".join(l.strip() for l in defn if l.strip()),
            "tail": " ".join(l.strip() for l in tail if l.strip()),
        }
    return out


def _plain(s: str) -> str:
    """Strip the inline markdown a tooltip attribute can't carry (links/code/bold/italic)."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[`*]", "", s)
    return s.strip()


_REPO_BASENAMES: set | None = None


def _repo_basenames() -> set:
    """Every filename present in this repo (basename), so a backticked ref to one is 'shipped' (allowed)."""
    global _REPO_BASENAMES
    if _REPO_BASENAMES is None:
        _REPO_BASENAMES = set()
        for dp, dns, fns in os.walk(ROOT):
            dns[:] = [d for d in dns if d != ".git"]
            _REPO_BASENAMES.update(fns)
    return _REPO_BASENAMES


def check_abstractions(entries: list[Entry], abbrs: dict) -> list[str]:
    """(1) every [[slug]] citation resolves; (2) no entry cites an unshipped filename or a bare rule number."""
    problems: list[str] = []
    shipped = _repo_basenames()
    for f in catalogue_md_files():
        rel = os.path.relpath(f, ROOT)
        if rel == ABBR_SRC:
            continue
        body = open(f, encoding="utf-8").read()
        for m in ABBR_CITE_RE.finditer(body):
            if m.group(1) not in abbrs:
                problems.append(f"{rel}: [[{m.group(1)}]] — no such abstraction slug")
    for e in entries:
        for m in RAW_FILE_RE.finditer(e.text):
            if os.path.basename(m.group(1)) not in shipped:
                problems.append(f"{e.path}: unshipped filename `{m.group(1)}` — route through an abstraction")
        for m in RULE_CITE_RE.finditer(e.text):
            problems.append(f"{e.path}: bare rule citation '{m.group(0)}' — state the rule's content instead")
    return problems


FIGURE_FILE = "catalogue-figure.html"  # the hand-authored governance-map figure


def check_figure(entries: list[Entry]) -> list[str]:
    """Governance-map figure invariants: every mechanism is clickable, every link resolves, and no
    clickable-styled node ('chip' / 'lat-node') is a slug without a link.

    Deterministic backstop for the figure — it is hand-authored (build never regenerates it), so a
    control added to the catalogue but forgotten in the figure, or a node styled clickable but left as
    plain text, would silently ship without this gate.
    """
    p = os.path.join(ROOT, FIGURE_FILE)
    if not os.path.exists(p):
        return []
    problems: list[str] = []
    lines = open(p, encoding="utf-8").read().splitlines()
    hrefs = re.findall(r'href="([^"]+\.html)"', "\n".join(lines))
    local = {h for h in hrefs if not h.startswith(("http://", "https://", "#", "mailto:"))}

    # (1) link integrity — every relative .html link resolves on disk.
    for h in sorted(local):
        if not os.path.exists(os.path.join(ROOT, os.path.normpath(h))):
            problems.append(f"dead link -> {h}")

    # (2) coverage — every mechanism is linked at least once (no slug clickable nowhere in the figure).
    for e in entries:
        html = (e.path[:-3] + ".html").replace(os.sep, "/")
        if html not in local:
            problems.append(f"mechanism not linked anywhere -> {html} (a slug without a link)")

    # (3) no orphan node — a chip / lat-node element must carry a link.
    for i, ln in enumerate(lines, 1):
        if re.search(r'class="[^"]*\b(?:chip|lat-node)\b', ln) and "href=" not in ln:
            problems.append(f"line {i}: clickable-styled node has no link -> {ln.strip()[:80]}")

    # (4) legend usage — every encoding the legend declares must actually be used in the diagram body,
    # or the legend over-promises. Split the explanatory blocks (legend + compare-note) from the body.
    full = "\n".join(lines)
    explain = "".join(re.findall(r'<div class="(?:legend|compare-note)">.*?</div>', full, flags=re.S))
    body = re.sub(r'<div class="(?:legend|compare-note)">.*?</div>', "", full, flags=re.S)
    rels = {"cp": "counterpart", "en": "enabler", "co": "consumer", "ly": "layer"}
    for cls, name in rels.items():
        if re.search(rf"\blg-rel {cls}\b", explain) and not re.search(rf'class="(?:rel )?{cls}[" ]', body):
            problems.append(f"legend declares the '{name}' relationship but nothing in the figure uses it")
    if "◀▶" in explain and "◀▶" not in body:  # bridge relationship
        problems.append("legend declares the 'bridge' relationship (◀▶) but nothing in the figure uses it")
    for cls, name in {"soft": "Soft", "sh": "Soft·Hard"}.items():
        if re.search(rf"badge b-s{'h' if cls == 'sh' else ''}\b", explain) and \
                not re.search(rf'class="chip[^"]*\b{cls}\b', body):
            problems.append(f"legend declares enforcement '{name}' but no node in the figure carries it")
    return problems


BANNED_TERMS = {
    # A named term that must not appear + the phrasing to use instead. The canonical PDF library is under
    # licensing review, so the catalogue must not name it — describe it by role.
    "itext": "the canonical PDF library",
}


def check_banned_terms() -> list[str]:
    """Fail if a banned term is named anywhere in the catalogue SOURCES — entries, docs, downloads, and the
    hand-authored figures. Scans sources, not generated HTML (which derives from them and is rebuilt after
    validate), and skips the bundled plugin (regenerated from the entries)."""
    problems: list[str] = []
    figures = ["catalogue-figure.html", "development-workflow.html"]
    sources = [f for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
               if os.sep + "plugin" + os.sep not in f]
    sources += [os.path.join(ROOT, f) for f in figures]
    for f in sources:
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, ROOT)
        for i, ln in enumerate(open(f, encoding="utf-8").read().splitlines(), 1):
            low = ln.lower()
            for term, instead in BANNED_TERMS.items():
                if term in low:
                    problems.append(f"{rel}:{i}: banned term {term!r} — say {instead!r} instead")
    return problems


def check_summary_counts(entries: list[Entry]) -> list[str]:
    """Drift guard: the INDEX prose role-totals + grand total must equal the parsed entries.
    Rule #33 shape — a stable lint reads the meta (the entries) and asserts the hand-written summary
    numbers, rather than codegen writing them back into the source. Catches the 'Agent (20)' class of rot
    the row-count check (check_index) can't see because it only compares rows, not the prose footer."""
    problems: list[str] = []
    by_role = {r: sum(e.role == r for e in entries) for r in ROLES}
    idx = open(os.path.join(ROOT, "INDEX.md"), encoding="utf-8").read()
    for role, label in (("Agent", "Agent"), ("Bridge", "Models-bridge"), ("Product", "Product")):
        m = re.search(rf"\*\*{re.escape(label)} \((\d+)\)", idx)
        if not m:
            problems.append(f"no '**{label} (N)**' role total in the INDEX summary")
        elif int(m.group(1)) != by_role[role]:
            problems.append(f"{label} ({m.group(1)}) != actual {by_role[role]} — update the INDEX summary")
    m = re.search(r"(\d+) mechanisms across \d+ families", idx)
    if m and int(m.group(1)) != len(entries):
        problems.append(f"'{m.group(1)} controls' != actual {len(entries)} — update the INDEX summary")
    return problems


_ALLOWED_LINK_SCHEMES = ("http://", "https://", "mailto:")


def check_link_schemes() -> list[str]:
    """Every markdown link resolves to an allowed scheme (http/https/mailto), an anchor (#…), or a
    relative path. The renderer neutralizes anything else to `#` (so an unsafe href is impossible on the
    built site); this flags it loudly so the author fixes the *source* rather than shipping a dead link."""
    problems: list[str] = []
    for f in catalogue_md_files():
        for i, ln in enumerate(open(f, encoding="utf-8"), 1):
            for m in re.finditer(r"\]\(\s*([^)]+?)\s*\)", ln):
                u = m.group(1).strip()
                if u.startswith(_ALLOWED_LINK_SCHEMES) or u.startswith("#"):
                    continue
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.\-]*:", u):  # a scheme, and not an allowed one
                    problems.append(f"{os.path.relpath(f, ROOT)}:{i}: disallowed link scheme -> {u[:60]}")
    return problems


def check_escape_seam() -> list[str]:
    """HTML escaping goes through `_esc` (the stdlib `html.escape`) — NEVER a hand-rolled replace-chain,
    the class the abbr-display XSS + the stray-`&` came from. Forbid the chain anywhere in the source."""
    src = open(os.path.join(ROOT, "catalog.py"), encoding="utf-8").read().splitlines()
    needle = '.replace("&", "&amp;")' + '.replace("<", "&lt;")'  # concat so THIS line can't self-match
    return [f"catalog.py:{i + 1}: hand-rolled HTML-escape chain — use `_esc` (html.escape) instead"
            for i, ln in enumerate(src) if needle in ln]


def cmd_validate(_args) -> int:
    entries = all_entries()
    n_issues = 0
    for msg in check_link_schemes():
        print(f"  [scheme] {msg}")
        n_issues += 1
    for msg in check_escape_seam():
        print(f"  [seam]  {msg}")
        n_issues += 1
    for e in entries:
        for msg in e.issues:
            print(f"  [entry] {e.path}: {msg}")
            n_issues += 1
    for msg in check_index(entries):
        print(f"  [index] {msg}")
        n_issues += 1
    for msg in check_links():
        print(f"  [link]  DEAD {msg}")
        n_issues += 1
    abbrs = parse_abstractions()
    for msg in check_abstractions(entries, abbrs):
        print(f"  [abbr]  {msg}")
        n_issues += 1
    for msg in check_figure(entries):
        print(f"  [figure] {msg}")
        n_issues += 1
    for msg in check_banned_terms():
        print(f"  [banned] {msg}")
        n_issues += 1
    for msg in check_summary_counts(entries):
        print(f"  [census] {msg}")
        n_issues += 1
    for msg in check_no_raw_stats(entries):
        print(f"  [stat]  {msg}")
        n_issues += 1
    for msg in check_census_tokens(entries):
        print(f"  [census] {msg}")
        n_issues += 1
    for msg in check_adoption_sequence():
        print(f"  [adopt] {msg}")
        n_issues += 1
    for rel, summ in role_summaries().items():
        if not summ:
            print(f"  [role]  {rel}: missing '<!-- summary: … -->' comment")
            n_issues += 1
    fams = family_summaries()
    for fam in sorted({e.family for e in entries if e.family}):
        if fam not in fams:
            print(f"  [family] '{fam}': no italic one-liner under its INDEX header")
            n_issues += 1
    by_role = {r: sum(e.role == r for e in entries) for r in ROLES}
    print(f"validated {len(entries)} entries "
          f"(agent {by_role['Agent']} · bridge {by_role['Bridge']} · product {by_role['Product']}) "
          f"— {n_issues} issue(s)")
    return 1 if n_issues else 0


def cmd_query(args) -> int:
    rows = [e.as_dict() for e in all_entries()]
    for key in ("role", "family", "form", "move", "model"):
        val = getattr(args, key, None)
        if val:
            rows = [r for r in rows if (r[key] or "").lower() == val.lower()]
    if args.enf:
        rows = [r for r in rows if (r["enforcement"] or "").lower() == args.enf.lower()]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{r['role']:8} · {r['family']:28} · {r['form']:14} · "
                  f"{r['enforcement']:9} · {r['path']}")
        print(f"— {len(rows)} entr{'y' if len(rows) == 1 else 'ies'}")
    return 0


def cmd_summaries(args) -> int:
    """Dump the three tiers of summaries (roles · families · entries) — the codegen's tooltip source."""
    data = {
        "roles": role_summaries(),
        "families": family_summaries(),
        "entries": {e.path: e.summary for e in all_entries()},
    }
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for tier in ("roles", "families", "entries"):
            print(f"# {tier} ({len(data[tier])})")
            for k, v in data[tier].items():
                print(f"  {k}: {v}")
    return 0


# ─────────────────────────── Phase 3: md → html codegen ───────────────────────────
# Dependency-free (stdlib only): a compact renderer for exactly the markdown constructs
# the catalogue uses (headers, tables, bullets, code spans/fences, bold/italic, links).
# `.md` links are rewritten to `.html` so the generated site is self-contained.

GENERATED_BANNER = ("<!-- GENERATED by catalog.py build — DO NOT EDIT. "
                    "Edit the sibling .md and re-run `catalog.py build`. -->")

# Source Serif 4 (headings) + Source Sans 3 (body) — a professional technical-docs pairing.
FONTS_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              '<link href="https://fonts.googleapis.com/css2?'
              'family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&'
              'family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap" rel="stylesheet">')

GITHUB_SVG = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" '
              'style="vertical-align:-2px;fill:currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
              '2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94'
              '-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 '
              '2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02'
              '.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82'
              '.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 '
              '1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>')

PDF_SVG = ('<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" '
           'style="vertical-align:-2px;fill:currentColor"><path d="M4 0a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h9a1 1 '
           '0 0 0 1-1V4.5L9.5 0H4zm5 1.5L12.5 5H9V1.5zM4.9 8.2h1c.5 0 .9.4.9.9s-.4.9-.9.9h-.4v1.1h-.6V8.2zm.6.5'
           'v.8h.3c.2 0 .3-.1.3-.4s-.1-.4-.3-.4h-.3zm2 .0h.9c.6 0 1 .5 1 1.4s-.4 1.5-1 1.5h-.9V8.7zm.6.5v1.8h.2'
           'c.3 0 .5-.3.5-.9s-.2-.9-.5-.9h-.2zm2.3-.5h1.7v.5h-1.1v.6h1v.5h-1v1.2h-.6V8.7z"></path></svg>')

SITE_FOOTER = (f'<footer class="site-foot">© <a href="https://davisjam.github.io">James C. Davis</a>, '
               f'2026–present &nbsp;·&nbsp; Assistant Professor, ECE @ Purdue &nbsp;·&nbsp; '
               f'<a class="gh" href="https://github.com/davisjam/agent-governance-mechanisms">'
               f'{GITHUB_SVG} agent-governance-mechanisms</a>'
               f'&nbsp;·&nbsp; <a class="book-foot" href="{{book_prefix}}book/index.html">'
               f'Read the book →</a></footer>')

TOPNAV = ('<div class="topnav"><a href="https://davisjam.github.io">James C. Davis, Purdue University</a>'
          '<a class="gh" href="https://github.com/davisjam/agent-governance-mechanisms">'
          f'{GITHUB_SVG} GitHub</a></div>')

# Landing top-right 3×2 nav grid — bigger, higher-contrast tap targets than the old topnav link pair.
# Layout:  Author | GitHub | Quick Start   (top row, 3 cells)
#          Book | Book (PDF)                (bottom row, 2 cells centered under the 3-col track)
NAV_GRID = (
    '<nav class="nav-grid" aria-label="Primary">'
    '<a class="ng-cell" href="https://davisjam.github.io">'
    '<span class="ng-t">Author</span><span class="ng-s">James C. Davis · Purdue</span></a>'
    '<a class="ng-cell" href="https://github.com/davisjam/agent-governance-mechanisms">'
    f'<span class="ng-t">{GITHUB_SVG} GitHub</span><span class="ng-s">the source repository</span></a>'
    '<a class="ng-cell" href="quick-start.html">'
    '<span class="ng-t">Quick Start</span><span class="ng-s">adopt it in your repo</span></a>'
    '<a class="ng-cell ng-book ng-bottom" href="book/index.html">'
    '<span class="ng-t">Book</span><span class="ng-s">read the web book</span></a>'
    f'<a class="ng-cell ng-book ng-bottom" href="{_PDF_HREF}">'
    f'<span class="ng-t">{PDF_SVG} Book (PDF)</span><span class="ng-s">download offline</span></a>'
    '</nav>')


FONT_CSS = ('  body { font-family:"Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }\n'
            '  h1,h2,h3,h4,.walk-h,.section-h { font-family:"Source Serif 4",Georgia,"Times New Roman",serif; }\n'
            '  .site-foot { max-width:1320px; margin:40px auto 0; padding:16px 26px 30px; border-top:1px solid #e2e8f0;'
            ' font-size:12.5px; color:#666; text-align:center; }\n'
            '  .site-foot a { color:#0b5cad; text-decoration:underline; } .site-foot a:hover { text-decoration:none; }\n'
            '  .site-foot .gh { white-space:nowrap; }\n'
            '  .topnav { position:absolute; top:14px; right:20px; font-size:12px; display:flex; gap:16px; }\n'
            '  .topnav a { color:#555; text-decoration:none; white-space:nowrap; } .topnav a:hover { color:#0b5cad; }\n'
            '  @media (max-width:640px){ .topnav { position:static; justify-content:flex-end; margin:0 0 8px; } }\n')

PAGE_CSS = """
  :root { --ink:#1a1a1a; --muted:#555; --accent:#b45309; --line:#e2e8f0; --link:#0b5cad; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Avenir Next",Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:var(--ink); background:#fff; line-height:1.62; font-size:18.5px; }
  main { width: 94vw; max-width: 1320px; margin: 0 auto; padding: 32px 26px 80px; }
  /* The landing is a figure-prose BOARD — it spreads to a generous ceiling to use wide screens;
     entry/prose pages keep the 1320 reading width (their prose has no 70ch cap of its own). */
  body.landing main { max-width: 2100px; }
  body.landing .site-foot { max-width: 2100px; }
  nav.crumb { font-size: 13px; color: var(--muted); margin: 0 0 18px; letter-spacing:.01em; }
  nav.crumb a { color: var(--link); text-decoration: underline; text-underline-offset: 2px; }
  nav.crumb a:hover { text-decoration: underline; }
  h1 { font-size: 37px; margin: 6px 0 4px; letter-spacing:-0.02em; }
  h2 { font-size: 25px; margin: 30px 0 8px; padding-top: 6px; border-top:1px solid var(--line); }
  h3 { font-size: 20px; margin: 22px 0 6px; }
  h4 { font-size: 16.5px; margin: 16px 0 4px; color:#333; }
  p, li { font-size: 19px; }
  a { color: var(--link); }
  code { background:#f6f8fa; padding:1px 5px; border-radius:4px; font-size:.9em;
         font-family:"SF Mono",Menlo,Consolas,monospace; }
  pre { background:#f6f8fa; padding:12px 14px; border-radius:7px; overflow:auto; }
  pre code { background:none; padding:0; }
  table { border-collapse: collapse; margin: 12px 0; font-size: 14.5px; width:100%; }
  th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; }
  th { background:#f8fafc; font-weight:700; }
  hr { border:none; border-top:1px solid var(--line); margin: 22px 0; }
  .subtitle { font-size: 15px; color:#444; font-style: italic; margin: 0 0 6px; }
  a.abbr { color:var(--ink); text-decoration:none; border-bottom:1px dotted var(--accent);
           cursor:help; }
  a.abbr:hover { color:var(--accent); border-bottom-style:solid; }
  section.abbr-entry { scroll-margin-top:14px; }
  section.abbr-entry h2 code.slug { font-size:12.5px; font-weight:400; color:var(--accent);
           background:#fff8f0; vertical-align:middle; margin-left:8px; }
  p.abbr-grounds { font-size:13px; color:var(--muted); margin:4px 0 2px; }
  .tag { color: var(--accent); font-weight: 700; font-size: 12px; letter-spacing:.08em; text-transform:uppercase; }
  .census h3.role-h { color:#c2410c; border-top:2px solid var(--line); padding-top:14px; margin-top:26px; }
  .census .role-note { font-size:12.5px; color:#8a5320; background:#fff8f0; border-left:3px solid var(--accent);
                       padding:7px 12px; border-radius:0 6px 6px 0; margin:2px 0 10px; }
  table.census-t td.c-name a { font-weight:600; text-decoration:none; }
  table.census-t td.c-name a:hover { text-decoration:underline; }
  table.census-t td.c-sum { font-size:13.5px; color:#444; }
  table.census-t td.c-enf { white-space:nowrap; color:#333; }
  table.census-t th, table.census-t td { vertical-align:top; }
  table.census-t tr:hover { background:#fafcff; }
  .fam-lede { font-size:13px; color:var(--muted); font-style:italic; margin:2px 0 6px; }
  .foot { font-size: 12.5px; color: var(--muted); border-top:1px solid var(--line); padding-top:14px; margin-top: 34px; }
"""

ROLE_DISPLAY = {"agent": "Agent", "models-bridge": "Models-bridge", "product": "Product"}


def _md_link_rewrite(url: str) -> str:
    u = url.strip()
    if u.startswith(("http://", "https://", "mailto:", "#")):
        return url
    if re.match(r"[a-zA-Z][a-zA-Z0-9+.\-]*:", u):
        # Any OTHER scheme (javascript:/data:/vbscript:/file:…) — neutralize. An unsafe href is impossible
        # by construction here; `check_link_schemes` (validate) also fails loudly so the author sees it.
        return "#"
    if "downloads/" in url:
        return url  # raw asset (CLAUDE starter) — shipped as .md, not rendered
    if url.endswith(".md"):
        return url[:-3] + ".html"
    return url.replace(".md#", ".html#")


def _esc(s: str) -> str:
    """The ONE text->HTML escaper — the stdlib canonical `html.escape` (NOT a hand-rolled replace-chain).
    All rendered text routes through here — body, code, abbr display, and `_attr` for attribute values —
    so 'unescaped output' has a single owner. `check_escape_seam` (validate) forbids the hand-rolled chain
    anywhere in the source."""
    return html.escape(s, quote=False)  # & < >  (quote handled by _attr for attribute contexts)


def _attr(s: str) -> str:
    return html.escape(s, quote=True)  # & < > " '  — full attribute-safe escaping


# Render context for [[slug]] abstraction citations, set per-file in cmd_build (map + relative path to root).
_ABBR_MAP: dict = {}
_ABBR_PREFIX = ""


def _abbr_link(slug: str, text: str | None) -> str:
    a = _ABBR_MAP.get(slug)
    disp = _esc(text if text else (a["headword"] if a else slug))  # display text is user-supplied — escape it
    if not a:
        return disp  # unresolved — validate flags it; render the (escaped) words so the page still reads
    return (f'<a class="abbr" href="{_ABBR_PREFIX}{ABBR_SRC[:-3]}.html#{_attr(slug)}" '
            f'title="{_attr(_plain(a["definition"]))}">{disp}</a>')


def _inline(s: str) -> str:
    """Inline markdown → HTML: code spans, [[abstraction]] cites, links, bold, italic. Order-sensitive."""
    spans: list[str] = []
    raw: list[str] = []
    s = re.sub(r"`([^`]+)`", lambda m: spans.append(m.group(1)) or f"\x00{len(spans)-1}\x00", s)
    s = ABBR_CITE_RE.sub(
        lambda m: raw.append(_abbr_link(m.group(1), m.group(2))) or f"\x01{len(raw)-1}\x01", s)
    s = _esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: f'<a href="{_attr(_md_link_rewrite(m.group(2)))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00",
               lambda m: "<code>{}</code>".format(_esc(spans[int(m.group(1))])), s)
    s = re.sub(r"\x01(\d+)\x01", lambda m: raw[int(m.group(1))], s)
    return s


def _render_table(rows: list[str]) -> str:
    def cells(r: str) -> list[str]:
        return [c.strip() for c in r.strip().strip("|").split("|")]
    header = cells(rows[0])
    body_start = 1
    if len(rows) > 1 and set(rows[1].replace("|", "").replace(":", "").replace("-", "").strip()) == set():
        body_start = 2
    out = ["<table>"]
    if any(header):
        out.append("<thead><tr>" + "".join(f"<th>{_inline(h)}</th>" for h in header) + "</tr></thead>")
    out.append("<tbody>")
    for r in rows[body_start:]:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells(r)) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_md(md: str) -> str:
    """Block-level markdown → HTML for the catalogue's regular subset."""
    # Strip ONLY the quick-start dual-emit scaffolding before block parsing, so it never renders as escaped
    # paragraphs: the `<!--adoption-source ... -->` single-source block and the bare `<!--adoption-auto-->` /
    # `<!--/adoption-auto-->` / `-interactive` sentinel markers around the generated regions. Kept narrow on
    # purpose — a blanket comment-strip would also eat a comment inside a code span (e.g. `` `<!-- x -->` ``),
    # which is legitimate visible content elsewhere in the catalogue.
    md = re.sub(r"<!--adoption-source.*?-->", "", md, flags=re.DOTALL)
    md = re.sub(r"<!--/?adoption-(?:auto|interactive)-->", "", md)
    lines = md.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        st = lines[i].strip()
        if st.startswith("```"):
            i += 1
            code: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            esc = _esc("\n".join(code))
            out.append(f'<pre tabindex="0"><code>{esc}</code></pre>'); continue  # tabindex: scrollable code blocks must be keyboard-focusable (axe scrollable-region-focusable)
        if st.startswith("|"):
            tbl: list[str] = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip()); i += 1
            out.append(_render_table(tbl)); continue
        m = re.match(r"^(#{1,4})\s+(.+)$", st)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if st == "---":
            out.append("<hr />"); i += 1; continue
        if st.startswith("- "):
            items: list[str] = []
            while i < n:
                s2 = lines[i].strip()
                if s2.startswith("- "):
                    items.append(s2[2:]); i += 1
                elif s2 == "" or s2.startswith(("#", "|", "---", "```")):
                    break
                elif items:
                    items[-1] += " " + s2; i += 1
                else:
                    break
            out.append("<ul>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ul>"); continue
        if st == "":
            i += 1; continue
        buf: list[str] = []
        while i < n:
            s2 = lines[i].strip()
            if s2 == "" or s2.startswith(("#", "|", "- ", "```", "---")):
                break
            buf.append(s2); i += 1
        if buf:
            out.append("<p>" + _inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def _site_footer(rel_root: str = "") -> str:
    """The shared page footer with a book link, its `book/index.html` href resolved for the page's depth
    (rel_root is the `../`-string from the page back to the catalogue root)."""
    return SITE_FOOTER.replace("{book_prefix}", rel_root)


def _page(title: str, crumb: str, body: str, subtitle: str = "", rel_root: str = "") -> str:
    sub = f'<p class="subtitle">{_inline(subtitle)}</p>\n' if subtitle else ""
    return (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>{_attr(title)}</title>\n{FONTS_LINK}\n<style>{PAGE_CSS}{FONT_CSS}</style>\n</head>\n<body>\n"
            f"<main>\n{crumb}\n{sub}{body}\n{_site_footer(rel_root)}\n</main>\n</body>\n</html>\n")


def _crumb(rel_root: str, trail: list[tuple[str, str]]) -> str:
    parts = [f'<a href="{rel_root}index.html">Home</a>']
    for label, href in trail:
        parts.append(f'<a href="{href}">{_attr(label)}</a>' if href else _attr(label))
    return '<nav class="crumb">' + " &nbsp;/&nbsp; ".join(parts) + "</nav>"


def parse_census() -> list[dict]:
    """Ordered families from INDEX.md with their control rows (role, one-liner, rows)."""
    idx = open(os.path.join(ROOT, "INDEX.md"), encoding="utf-8").read()
    fams: list[dict] = []
    role = None
    cur: dict | None = None
    # Row carries Move + Model columns between Form and Enf (groups 4 + 5); census table below shows
    # Mechanism / Summary / Enforcement, so Move/Model are parsed but not displayed here.
    row_re = re.compile(
        r"^\| (?:✅|☐)\s*(★)?\s*\| ([^|]+?) \| `([a-z-]+)` \| `([a-z-]+)` \| (?:`([a-z-]+)`|—) \| "
        r"([^|]+?) \| \[[^\]]+\]\(([^)]+)\) \|$")
    for ln in idx.split("\n"):
        rm = re.match(r"^# (.+?)(?: target)?$", ln)
        if rm and not ln.startswith("## "):
            role = rm.group(1).strip(); continue
        fm = re.match(r"^## \d+\.\s+(.+)$", ln)
        if fm:
            cur = {"role": role, "family": fm.group(1).strip(), "oneliner": "", "rows": []}
            fams.append(cur); continue
        if cur is not None and not cur["oneliner"]:
            om = re.match(r"^\*(.+?)\*", ln)
            if om:
                cur["oneliner"] = om.group(1).strip()
        r = row_re.match(ln)
        if r and cur is not None:
            cur["rows"].append({"star": bool(r.group(1)), "control": r.group(2).strip(),
                                "form": r.group(3), "move": r.group(4), "model": r.group(5) or "—",
                                "enf": r.group(6).strip(), "path": r.group(7).strip()})
    return fams


CENSUS_LEGEND = (
    '<p class="census-legend">A <b>representative</b> selection — mechanism <i>patterns</i>, not an '
    'exhaustive list of every lint and gate in the system. Each row is one mechanism with its one-line '
    '<b>Summary</b> and how it <b>Enforces</b>: <b>Hard</b> is deterministic (blocks, audits, or signals '
    'regardless of agent cooperation), <b>Soft</b> is probabilistic (aims an agent but cannot block), and '
    '<b>Soft·Hard</b> is soft guidance with a hard counterpart. Click a name for the full writeup.</p>')

ROLE_HEADINGS = {
    "Agent": "Governance: Agents",
    "Models-bridge": "Governance: Models — a bridge between agents and product",
    "Bridge": "Governance: Models — a bridge between agents and product",
    "Product": "Governance: Product",
}

ROLE_NOTES = {
    "Product": "This is the part that's specific to the DocAble project — you'll need your own for "
               "your project.",
}


def build_census(entries: list[Entry]) -> str:
    summ = {e.path: e.summary for e in entries}
    out = ['<section class="census">', '<h2>The catalogue</h2>', CENSUS_LEGEND]
    last = None
    for fam in parse_census():
        if fam["role"] != last:
            heading = ROLE_HEADINGS.get(fam["role"] or "", f'Governance: {fam["role"]}')
            out.append(f'<h3 class="role-h">{_attr(heading)}</h3>')
            note = ROLE_NOTES.get(fam["role"] or "")
            if note:
                out.append(f'<p class="role-note">{_attr(note)}</p>')
            last = fam["role"]
        out.append(f'<h4>{_attr(fam["family"])}</h4>')
        if fam["oneliner"]:
            out.append(f'<p class="fam-lede">{_inline(fam["oneliner"])}</p>')
        out.append('<table class="census-t"><thead><tr><th>Mechanism</th><th>Summary</th>'
                   "<th>Enforcement</th></tr></thead><tbody>")
        for r in fam["rows"]:
            href = _md_link_rewrite(r["path"])
            summary = _inline(summ.get(os.path.normpath(r["path"]), ""))
            enf = _inline(r["enf"].replace("**", ""))   # no random bolding of Soft/Hard
            out.append(
                f'<tr><td class="c-name"><a href="{href}">{_inline(r["control"])}</a></td>'
                f'<td class="c-sum">{summary}</td><td class="c-enf">{enf}</td></tr>')
        out.append("</tbody></table>")
    out.append("</section>")
    return "\n".join(out)


LANDING_CSS = """
  .book-h1 { margin:6px 0 2px; }
  .book-sub { color:var(--accent); font-weight:700; font-size:17px; letter-spacing:.01em;
              margin:0 0 16px; }
  .nav-grid { position:absolute; top:16px; right:20px; display:grid; grid-template-columns:repeat(6,1fr);
              gap:9px; width:min(480px,64vw); z-index:5; }
  /* Top row: three cells, each spanning 2 of the 6 tracks. */
  .nav-grid .ng-cell { grid-column:span 2; }
  /* Bottom row: two cells, centered under the three above — each spans 2 tracks, offset by 1 so the
     pair (4 tracks) is centered in the 6-track grid (1 empty track on each side). */
  .nav-grid .ng-bottom:nth-of-type(4) { grid-column:2 / span 2; }
  .nav-grid .ng-bottom:nth-of-type(5) { grid-column:4 / span 2; }
  .nav-grid .ng-cell { display:flex; flex-direction:column; justify-content:center; gap:2px;
              border:1.6px solid #cbd5e1; border-radius:10px; padding:9px 12px; background:#fff;
              text-decoration:none; color:var(--ink); min-height:52px; transition:box-shadow .12s, border-color .12s, background .12s; }
  .nav-grid .ng-cell:hover { border-color:var(--accent); box-shadow:0 3px 12px rgba(0,0,0,.10); background:#fffaf3; }
  .nav-grid .ng-t { font-size:15px; font-weight:700; color:var(--link); letter-spacing:-.01em; }
  .nav-grid .ng-t svg { fill:currentColor; }
  .nav-grid .ng-s { font-size:11px; color:var(--muted); line-height:1.25; }
  .nav-grid .ng-book { border-color:var(--accent); background:#fff8f0; }
  .nav-grid .ng-book .ng-t { color:var(--accent); }
  @media (max-width:820px){ .nav-grid { position:static; width:100%; margin:0 0 14px; }
              .nav-grid .ng-cell, .nav-grid .ng-bottom:nth-of-type(4), .nav-grid .ng-bottom:nth-of-type(5) { grid-column:span 3; } }
.site-foot .book-foot { white-space:nowrap; font-weight:600; }
  .loop { border:1px solid var(--line); border-radius:11px; padding:16px 17px 15px; margin:4px 0 20px; background:#fbfcfd; }
  .loop .hd { margin:0 0 12px; font-size:14px; color:#222; }
  .flow { display:flex; flex-wrap:wrap; align-items:stretch; gap:8px; }
  .fstep { flex:1 1 150px; min-width:140px; border:1.4px solid #e2e8f0; border-top:3px solid var(--accent);
           border-radius:9px; padding:9px 11px; background:#fff; position:relative; }
  .fstep .fn { display:inline-flex; align-items:center; justify-content:center; width:19px; height:19px;
               border-radius:50%; background:var(--accent); color:#fff; font-size:11px; font-weight:800; margin-bottom:5px; }
  .fstep b { display:block; font-size:12.5px; line-height:1.25; margin-bottom:3px; }
  .fstep span { font-size:11px; color:var(--muted); line-height:1.35; }
  .farrow { align-self:center; color:#94a3b8; font-size:18px; font-weight:700; }
  @media (max-width:720px){ .farrow{ transform:rotate(90deg); width:100%; text-align:center; } .fstep{ flex-basis:100%; } }
  .mustache { display:block; width:100%; height:auto; margin:0; }
  .loop-outcome { text-align:center; margin:10px 0 2px; font-size:13px; color:#333; }
  .loop-outcome b { color:var(--accent); }
  .loop .tail { margin:14px 0 0; font-size:12.5px; color:#444; line-height:1.55; text-align:center; }
  .tail-pair { max-width:760px; margin:8px auto 0; padding-left:20px; }
  .tail-pair li { font-size:12.5px; color:#444; line-height:1.5; margin:0 0 6px; }
  .refs { margin:0 0 24px; }
  .refs .r { border-left:3px solid var(--accent); padding:3px 0 3px 12px; margin:0 0 7px; font-size:13px; color:#444; }
  .refs .r b { color:#333; font-weight:700; }
  .cards-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:11px; margin:0 0 26px; }
  .lcard { display:block; text-decoration:none; border:1.4px solid var(--line); border-radius:10px;
           padding:13px 15px; background:#fff; transition:box-shadow .12s, border-color .12s; }
  .lcard:hover { box-shadow:0 3px 12px rgba(0,0,0,.09); border-color:#cbd5e1; }
  .lcard b { display:block; font-size:17px; color:var(--link); letter-spacing:-.01em; margin-bottom:3px; }
  .lcard span { display:block; font-size:14.5px; color:var(--muted); line-height:1.4; }
  .lead, .subtitle, .walk-sub, .section-sub, .census-legend { max-width:70ch; }
  .lead { font-size:19px; color:#2a2a2a; line-height:1.66; margin:0 0 13px; }
  .lead .term { font-weight:700; }
  .wf { position:relative; left:50%; transform:translateX(-50%); width:min(1400px,96vw); margin:14px 0 6px; }
  .wf-frame { width:100%; overflow:hidden; }
  .wf-frame iframe { display:block; border:none; background:#fff; }
  .wf figcaption { font-size:13px; color:var(--muted); margin:10px auto 0; text-align:center;
                   max-width:780px; line-height:1.55; }
  hr.sep { border:none; border-top:1px solid var(--line); margin:26px 0 20px; }
  .walk-h { font-size:21px; margin:0 0 4px; letter-spacing:-.01em; }
  .walk-sub { font-size:16.5px; color:var(--muted); margin:0 0 14px; }
  .section-h { font-size:20.5px; margin:24px 0 3px; letter-spacing:-.01em; }
  .section-sub { font-size:16.5px; color:var(--muted); margin:0 0 12px; }
  .section-sub a { color:var(--link); }
  .spectrum { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin:4px 0 6px; align-items:stretch; }
  .school { border:1.4px solid var(--line); border-radius:10px; padding:12px 13px; background:#fff; display:flex; flex-direction:column; }
  .school.mid { border:2px solid var(--accent); background:#fffaf3; }
  .school h3 { margin:0 0 5px; font-size:17px; }
  .school.mid h3 { color:var(--accent); }
  .school p { margin:0 0 9px; font-size:16.5px; color:#444; line-height:1.55; }
  .school .srefs { font-size:12px; color:var(--muted); margin:0 0 10px; }
  .school .srefs .lbl { font-weight:700; color:#444; }
  .school .srefs ul { margin:3px 0 0; padding-left:16px; }
  .school .srefs li { margin:0 0 2px; line-height:1.4; }
  .school .srefs a { color:var(--link); }
  .school .pole { margin-top:auto; font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:800; }
  .spectrum-axis { text-align:center; font-size:11px; color:var(--muted); letter-spacing:.03em; margin:0 0 20px; }
  .cols3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:4px 0 8px; }
  .col h3 { margin:0 0 8px; font-size:16.5px; padding-bottom:5px; border-bottom:2px solid var(--accent); }
  .col ul { margin:0; padding:0; list-style:none; }
  .col li { font-size:16px; color:#3a3a3a; line-height:1.5; margin:0 0 9px; padding-left:15px; position:relative; }
  .col li::before { content:"→"; position:absolute; left:0; color:var(--accent); font-weight:700; }
  .ways-note { font-size:11.5px; color:var(--muted); margin:2px 0 22px; }
  .mechanisms { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:4px 0 8px; }
  .mech { border:1.4px solid var(--line); border-left:4px solid var(--accent); border-radius:10px; padding:12px 15px; background:#fff; }
  .mech.right { border-left:1.4px solid var(--line); border-right:4px solid var(--accent); text-align:right; }
  .mech h3 { margin:0 0 5px; font-size:16.5px; }
  .mech p { margin:0; font-size:16.5px; color:#444; line-height:1.55; }
  @media (max-width:900px){ .cols3 { grid-template-columns:1fr 1fr; } }
  @media (max-width:720px){ .spectrum, .cols3, .mechanisms { grid-template-columns:1fr; } }
  /* Figures align to the text column's left edge (text is max-width:840, margin:0),
     so each figure sits directly under its prose rather than auto-centering in the wider
     content box (which read as a rightward offset). The SVG scales within the figure. */
  .lfig, .hero-fig { margin:14px 0 18px; max-width:840px; }
  .hero-fig { max-width:920px; margin:18px 0 22px; }
  .lfig svg, .hero-fig svg { display:block; width:100%; height:auto; margin:0 auto; }
  .lfig figcaption, .hero-fig figcaption { font-size:14.5px; color:var(--muted); line-height:1.55;
                   margin:9px auto 0; max-width:70ch; text-align:center; }
  .lfig figcaption b, .hero-fig figcaption b { color:#333; }
  .book-cta { text-align:center; margin:6px 0 28px; }
  .book-cta a { color:var(--accent); font-size:17.5px; text-decoration:none; }
  .book-cta a:hover { text-decoration:underline; }
  .book-cta-pdf { display:inline-block; margin-left:14px; }
  .book-cta-pdf a { font-size:14px; font-weight:600; color:var(--accent); text-decoration:none;
                    padding:3px 10px; border:1px solid #d8d5cc; border-radius:6px; }
  .book-cta-pdf a:hover { border-color:var(--accent); background:#f4f3f0; text-decoration:none; }

  /* ---- Responsive figure-prose board -------------------------------------
     The one-page summary lays out as a board of bordered boxes on a grid:
     three tracks on a wide viewport, collapsing to one column on mobile. Each
     box pairs a figure or a bolded lead with a few lines of prose so the page
     is scannable at a glance instead of a long scroll. Boxes opt into a wider
     span with .span2 / .spanfull; the hero MAGE figure is a full-span lead. */
  .board { display:grid; grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); gap:16px; align-items:stretch;
           margin:6px 0 10px; }
  .box { border:1.4px solid var(--line); border-radius:11px; padding:16px 18px; background:#fff;
         display:flex; flex-direction:column; transition:box-shadow .12s, border-color .12s; }
  .box:hover { box-shadow:0 3px 14px rgba(0,0,0,.07); border-color:#cbd5e1; }
  .box > :first-child { margin-top:0; }
  .box > :last-child { margin-bottom:0; }
  .box.span2 { grid-column:span 2; }
  .box.spanfull { grid-column:1 / -1; }
  .box.accent { border-top:3px solid var(--accent); }
  .box.tint { background:#fffaf3; border-color:#f0dcc0; }
  .box .bx-h { font-family:"Source Serif 4",Georgia,serif; font-size:19px; margin:0 0 7px;
               letter-spacing:-.01em; }
  .box .bx-h.accent-t { color:var(--accent); }
  .box .bx-eyebrow { font-size:11.5px; text-transform:uppercase; letter-spacing:.06em; font-weight:800;
                     color:var(--accent); margin:0 0 4px; }
  .box p { font-size:16.5px; color:#3a3a3a; line-height:1.58; margin:0 0 10px; }
  .box p:last-child { margin-bottom:0; }
  .box .term { font-weight:700; color:#222; }
  /* A figure-prose lead box: the SVG sits beside (wide) or above (narrow) its prose. */
  .fp { display:grid; grid-template-columns:minmax(0,1.05fr) minmax(0,1fr); gap:20px 26px;
        align-items:center; }
  .fp .fp-fig { margin:0; }
  .fp .fp-fig svg { display:block; width:100%; height:auto; }
  .fp .fp-fig figcaption { display:none; }
  .fp .fp-body > :first-child { margin-top:0; }
  .fp .fp-body > :last-child { margin-bottom:0; }
  .fp .fp-body ul.theses { margin:8px 0 11px; padding-left:20px; }
  .fp .fp-body ul.theses li { margin:0 0 7px; line-height:1.55; }
  /* A figure that sits at the top of a box, prose beneath it (used inside thesis boxes). */
  .box .bx-fig { margin:2px 0 12px; }
  .box .bx-fig svg { display:block; width:100%; height:auto; }
  .box .bx-fig figcaption { display:none; }
  /* Nested constraint/sensor pair inside a thesis box, side by side then stacked. */
  .duo { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:10px 0 0; }
  .duo .mech { margin:0; }
  @media (max-width:900px){
    .board { grid-template-columns:repeat(2, 1fr); }
    .box.span2 { grid-column:1 / -1; }
    .fp { grid-template-columns:1fr; gap:16px; }
    .fp .fp-fig { max-width:560px; margin:0 auto; }
  }
  @media (max-width:720px){
    .board { grid-template-columns:1fr; gap:14px; }
    .box.span2, .box.spanfull { grid-column:auto; }
    .duo { grid-template-columns:1fr; }
  }

  /* ---- The pair of theses (two-up on wide, stacked on narrow) --------------------------------
     The two theses are a matched pair and must read as a grouped unit, and the top spine must use
     the full page width. So they sit side-by-side in a two-track grid that spans the whole 2100px
     spine (was: two lonely 70ch left columns that wasted the right half). Each thesis is a bordered
     card; its figure fills the card's column, so at 2560px each figure renders ≈1000px wide — far
     more legible than the old fixed 920px pinned in a narrow column. */
  .theses-pair { display:grid; grid-template-columns:1fr 1fr; gap:22px; margin:22px 0 8px;
                 align-items:stretch; }
  .thesis { border:1.4px solid var(--line); border-radius:12px; padding:20px 24px 22px; background:#fff;
            display:flex; flex-direction:column; }
  .thesis.accent { border-top:3px solid var(--accent); }
  .thesis .th-eyebrow { font-size:12px; text-transform:uppercase; letter-spacing:.07em; font-weight:800;
                        color:var(--accent); margin:0 0 6px; }
  .thesis .th-h { font-size:22px; margin:0 0 8px; letter-spacing:-.01em; line-height:1.25;
                  font-family:"Source Serif 4",Georgia,serif; }
  .thesis .th-sub { font-size:16.5px; color:#3a3a3a; margin:0 0 6px; line-height:1.62; max-width:none; }
  .thesis .th-fig { margin:auto 0 0; padding-top:14px; }
  .thesis .th-fig svg { display:block; width:100%; height:auto; }
  .thesis .th-fig figcaption { font-size:14px; color:var(--muted); line-height:1.55;
                               margin:11px 0 0; text-align:center; max-width:none; }
  .thesis .th-fig figcaption b { color:#333; }
  /* Below 960px the pair can't hold two legible columns; stack it and keep each figure full-width. */
  @media (max-width:960px){
    .theses-pair { grid-template-columns:1fr; gap:16px; }
  }

  /* ---- Cheat-sheet MASONRY (below the prose spine) -----------------------------------------
     Everything under the two theses tiles into a Pinterest-style pack: CSS multi-column with
     break-inside:avoid on each self-contained card, so varying-height cards float up and fill
     the width instead of leaving the right half of a wide screen empty. `column-width` lets the
     column COUNT grow with the viewport (≈4 tracks at 2100px, 1 track ≤720px) with no media
     queries for the count. A handful of intrinsically-wide cards (the horizontal flow strip, the
     dev-workflow figure) opt out with `.wide { column-span:all }` and punctuate the pack full-bleed. */
  /* The card families lay out as a responsive GRID (was CSS multi-column): with only a handful of
     cards per family, multi-column filled column 1 then column 2 and left the right half of a wide
     screen empty, whereas grid `auto-fill, minmax(320px,1fr)` spreads the cards ACROSS the full width
     (≈5-6 tracks at 2560px, 1 at ≤720px). A `.card.wide` spans every track. An open <details> just
     grows its own grid cell's row — cleaner than a multi-column reflow. */
  .masonry { display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr));
             gap:16px; align-items:start; margin: 4px 0 8px; }
  @media (max-width:720px){ .masonry { grid-template-columns:1fr; } }
  .tile { break-inside: avoid; -webkit-column-break-inside: avoid; page-break-inside: avoid;
          display: inline-block; width: 100%; margin: 0 0 16px;
          border:1.4px solid var(--line); border-radius:11px; padding:15px 17px; background:#fff;
          transition:box-shadow .12s, border-color .12s; }
  .tile:hover { box-shadow:0 3px 14px rgba(0,0,0,.07); border-color:#cbd5e1; }
  .tile > :first-child { margin-top:0; }
  .tile > :last-child { margin-bottom:0; }
  .tile.accent { border-top:3px solid var(--accent); }
  .tile.tint { background:#fffaf3; border-color:#f0dcc0; }
  .tile.mid { border:2px solid var(--accent); background:#fffaf3; }
  /* Lightweight card headers/kickers — the demoted band H2s become these, no full-width heading rows. */
  .tile .tl-kicker { font-size:11px; text-transform:uppercase; letter-spacing:.07em; font-weight:800;
                     color:var(--accent); margin:0 0 4px; }
  .tile .tl-h { font-family:"Source Serif 4",Georgia,serif; font-size:18px; margin:0 0 6px;
                letter-spacing:-.01em; color:var(--ink); }
  .tile .tl-h.accent-t { color:var(--accent); }
  .tile p { font-size:16px; color:#3a3a3a; line-height:1.56; margin:0 0 9px; }
  .tile p:last-child { margin-bottom:0; }
  .tile .bx-fig { margin:2px 0 11px; }
  .tile .bx-fig svg { display:block; width:100%; height:auto; }
  .tile .bx-fig figcaption { display:none; }
  .tile .term { font-weight:700; color:#222; }
  .tile .pole { display:block; margin-top:8px; font-size:10px; text-transform:uppercase;
                letter-spacing:.05em; color:var(--muted); font-weight:800; }
  .tile .srefs { font-size:12px; color:var(--muted); margin:8px 0 0; }
  .tile .srefs .lbl { font-weight:700; color:#444; }
  .tile .srefs ul { margin:3px 0 0; padding-left:16px; }
  .tile .srefs li { margin:0 0 2px; line-height:1.4; }
  .tile.axis { text-align:center; font-size:11px; color:var(--muted); letter-spacing:.03em;
               padding:9px 12px; background:#f8fafc; }
  /* A stance/skill card whose body is an arrow-bulleted list. */
  .tile ul.tl-list { margin:0; padding:0; list-style:none; }
  .tile ul.tl-list li { font-size:15px; color:#3a3a3a; line-height:1.5; margin:0 0 8px;
                        padding-left:15px; position:relative; }
  .tile ul.tl-list li:last-child { margin-bottom:0; }
  .tile ul.tl-list li::before { content:"→"; position:absolute; left:0; color:var(--accent); font-weight:700; }
  /* An action card that is itself a link (the catalogue-explore cards). */
  a.tile { text-decoration:none; color:var(--ink); }
  a.tile b { display:block; font-size:16px; color:var(--link); letter-spacing:-.01em; margin-bottom:3px; }
  a.tile span { display:block; font-size:14px; color:var(--muted); line-height:1.4; }
  /* Refs as a compact card. */
  .tile .r { border-left:3px solid var(--accent); padding:2px 0 2px 11px; margin:0 0 7px;
             font-size:13px; color:#444; }
  .tile .r:last-child { margin-bottom:0; }
  .tile .r b { color:#333; font-weight:700; }
  /* CTA card. */
  .tile.cta { text-align:center; }
  .tile.cta .book-cta { margin:0; }
  /* Intrinsically-wide cards span every column and punctuate the pack full-bleed. */
  .tile.wide { column-span: all; -webkit-column-span: all; width:auto; display:block; }
  .tile.wide .loop { border:none; background:none; padding:0; margin:0; }
  /* Inside a full-bleed tile the .wf figure no longer needs the 50%-viewport centering trick it
     used in the old full-width main; reset it to a normal centered block so the iframe fits the tile. */
  .tile.wide .wf { position:static; left:auto; transform:none; width:100%; max-width:1400px;
                   margin:8px auto 0; }
  /* The midway-discipline figure sits beside its prose in a full-bleed tile: the SVG gets a generous
     column so its three-panel labels are legible, prose reads alongside on wide screens. */
  .tile.wide .midway-fp { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);
                          gap:20px 30px; align-items:center; margin-top:4px; }
  .tile.wide .midway-fp .bx-fig { margin:0; }
  .tile.wide .midway-fp .bx-fig svg { display:block; width:100%; height:auto; }
  .tile.wide .midway-body > :first-child { margin-top:0; }
  .tile.wide .midway-body > :last-child { margin-bottom:0; }
  @media (max-width:820px){
    .tile.wide .midway-fp { grid-template-columns:1fr; gap:14px; }
  }
  @media (max-width:720px){
    .masonry { columns: 1; }
  }

  /* ---- HERO 2-up ---------------------------------------------------------------------------
     The opening is a real two-column spine: the lead prose on the left, the MAGE-method overview
     figure pulled up beside it on the right, so the top uses the full page width and "one picture"
     lands immediately (was: a ~70ch left column with the entire top-right empty, and the method
     figure marooned in a full-width box below). Collapses to a single stacked column ≤900px. */
  .hero { display:grid; grid-template-columns:minmax(0,0.92fr) minmax(0,1.08fr); gap:26px 40px;
          align-items:center; margin:8px 0 6px; }
  .hero-lead { min-width:0; }
  .hero-lead .lead { max-width:56ch; }
  .hero-lead .book-h1 { margin-top:0; }
  .hero-fig-2up { margin:0; min-width:0; }
  .hero-fig-2up figure { margin:0; }
  .hero-fig-2up svg { display:block; width:100%; height:auto; }
  .hero-fig-2up figcaption { font-size:14px; color:var(--muted); line-height:1.55;
                             margin:11px 2px 0; text-align:center; }
  .hero-fig-2up figcaption b { color:#333; }
  @media (max-width:900px){
    .hero { grid-template-columns:1fr; gap:18px; }
    .hero-lead .lead { max-width:70ch; }
    .hero-fig-2up { max-width:640px; margin:0 auto; }
  }

  /* ---- The uniform clickable CARD (a native <details>) --------------------------------------
     Every landing unit is the same primitive: a <details class="card"> whose <summary> is the
     always-visible header (kicker + title + one-line frame, and a figure thumbnail when the card
     has a figure). Expanding reveals the figure large-and-legible and/or the fuller summary
     INLINE (the "peek"), then a "read the full treatment →" link-through to the book/entry page.
     Native <details> keeps it accessible and JS-free — no custom modal/accordion. The whole card
     carries id="card-<slug>" so it is deep-linkable (index.html#card-tombstone-commits). */
  .card { border:1.4px solid var(--line); border-radius:11px; background:#fff; overflow:hidden;
          width:100%; margin:0; align-self:start;
          transition:box-shadow .12s, border-color .12s; scroll-margin-top:16px; }
  .card:hover { box-shadow:0 3px 14px rgba(0,0,0,.08); border-color:#cbd5e1; }
  .card[open] { box-shadow:0 4px 18px rgba(0,0,0,.09); border-color:#cbd5e1; }
  .card.accent { border-top:3px solid var(--accent); }
  .card.tint { background:#fffaf3; border-color:#f0dcc0; }
  .card.mid { border:2px solid var(--accent); background:#fffaf3; }
  /* The summary IS the card header — no default disclosure triangle; we draw our own affordance. */
  .card > summary { list-style:none; cursor:pointer; padding:15px 17px; display:grid;
                    grid-template-columns:1fr auto; gap:4px 12px; align-items:start; position:relative; }
  .card > summary::-webkit-details-marker { display:none; }
  .card > summary:focus-visible { outline:2px solid var(--accent); outline-offset:-2px; }
  .cd-kicker { grid-column:1; font-size:11px; text-transform:uppercase; letter-spacing:.07em;
               font-weight:800; color:var(--accent); margin:0 0 4px; }
  .cd-title { grid-column:1; font-family:"Source Serif 4",Georgia,serif; font-size:18px;
              letter-spacing:-.01em; color:var(--ink); line-height:1.25; margin:0; }
  .card.mid .cd-title, .card.accent .cd-title.accent-t { color:var(--accent); }
  .cd-frame { grid-column:1; font-size:14px; color:var(--muted); line-height:1.5; margin:5px 0 0; }
  /* Figure thumbnail on the summary — a small, cropped preview so a figure-bearing card reads as one. */
  .cd-thumb { grid-column:2; grid-row:1 / span 3; width:96px; height:64px; border-radius:7px;
              border:1px solid var(--line); background:#fbfcfd; overflow:hidden; display:flex;
              align-items:center; justify-content:center; }
  .cd-thumb svg { width:100%; height:100%; object-fit:contain; }
  /* A figure card opens by default so its figure is never lost behind a peek; the summary thumbnail is
     then redundant with the large figure below it, so hide it while open (the peek/close chip stays). */
  .card[open] .cd-thumb { display:none; }
  /* The open/closed affordance — a "peek ▸ / close ▾" chip bottom-right of the summary. */
  .cd-toggle { grid-column:2; align-self:end; font-size:11px; font-weight:700; color:var(--accent);
               letter-spacing:.02em; white-space:nowrap; margin-top:6px; }
  .card[open] .cd-toggle::after { content:"Close ▾"; }
  .card:not([open]) .cd-toggle::after { content:"Peek ▸"; }
  /* When a card has a thumb, the toggle sits under it (row 4); else it shares column 2 row 1. */
  .cd-body { padding:0 17px 16px; border-top:1px solid var(--line); margin-top:2px; }
  .cd-body > :first-child { margin-top:12px; }
  .cd-body p { font-size:16px; color:#3a3a3a; line-height:1.56; margin:0 0 10px; }
  .cd-body p:last-of-type { margin-bottom:10px; }
  .cd-body .term { font-weight:700; color:#222; }
  .cd-body .cd-fig { margin:12px 0 12px; }
  .cd-body .cd-fig svg { display:block; width:100%; height:auto; }
  .cd-body .cd-fig figcaption { font-size:13.5px; color:var(--muted); line-height:1.5;
                                margin:9px 2px 0; text-align:center; }
  .cd-body .cd-fig figcaption b { color:#333; }
  /* The link-through — always the last thing in an expanded card. */
  .cd-more { display:inline-block; margin-top:4px; font-size:14.5px; font-weight:700;
             color:var(--accent); text-decoration:none; }
  .cd-more:hover { text-decoration:underline; }
  /* Arrow-bulleted lists inside a card body (the "way of thinking" skill cards). */
  .cd-body ul.cd-list { margin:0 0 12px; padding:0; list-style:none; }
  .cd-body ul.cd-list li { font-size:15px; color:#3a3a3a; line-height:1.5; margin:0 0 8px;
                           padding-left:15px; position:relative; }
  .cd-body ul.cd-list li::before { content:"→"; position:absolute; left:0; color:var(--accent); font-weight:700; }
  .cd-body .srefs { font-size:12.5px; color:var(--muted); margin:8px 0 0; }
  .cd-body .srefs .lbl { font-weight:700; color:#444; }
  .cd-body .srefs ul { margin:3px 0 0; padding-left:16px; }
  .cd-body .srefs li { margin:0 0 3px; line-height:1.4; }
  .cd-body .srefs a { color:var(--link); }
  .cd-body .pole { display:block; margin:10px 0 0; font-size:10px; text-transform:uppercase;
                   letter-spacing:.05em; color:var(--muted); font-weight:800; }

  /* ---- The four definitions (projected from book/data/definitions.json) --------------------- */
  .cd-body blockquote.def-box { margin:0 0 12px; padding:10px 14px; background:#f0fdf4;
                   border-left:4px solid #15803d; border-radius:0 7px 7px 0; font-size:15px;
                   line-height:1.55; color:#1a1a1a; }
  .cd-body ul.def-aspects li { font-size:14px; color:#3a3a3a; }
  .cd-body .def-trace { font-size:12px; color:var(--muted); margin:8px 0 0; }
  .cd-body .def-trace a { color:var(--link); }
  .cd-body .def-owed { color:#b45309; font-style:italic; }

  /* ---- The learning-outcomes view (projected from book-models/outcomes.json) --------------- */
  .cd-body ul.oc-list { margin:4px 0 12px; padding:0; list-style:none; }
  .cd-body ul.oc-list li.oc-row { display:grid; grid-template-columns:auto auto 1fr auto; gap:10px;
                   align-items:baseline; font-size:14.5px; color:#2a2a2a; line-height:1.5;
                   padding:7px 0; border-top:1px solid var(--line); }
  .cd-body ul.oc-list li.oc-row:first-child { border-top:none; }
  .oc-row .oc-unit { font-weight:800; color:#15803d; white-space:nowrap; font-size:12.5px; }
  .oc-row .oc-bloom { font-size:10px; text-transform:uppercase; letter-spacing:.05em; font-weight:800;
                   color:#fff; background:#b45309; border-radius:4px; padding:1px 6px; white-space:nowrap; }
  .oc-row .oc-stmt { color:#2a2a2a; }
  .oc-row .oc-more { color:var(--link); white-space:nowrap; font-size:12.5px; }
  @media (max-width:640px){ .cd-body ul.oc-list li.oc-row { grid-template-columns:1fr; gap:3px; } }

  /* ---- The two theses as a matched PAIR of cards -------------------------------------------
     The theses stay a grouped, adjacent pair ("Thesis I of II" / "Thesis II of II") but are now
     the same <details class="card"> primitive, sitting two-up in their own grid so they read
     together and each figure renders at ~half the page width. Stacks ≤900px. */
  .theses-cards { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:20px 0 8px;
                  align-items:start; }
  .theses-cards .card { margin:0; }
  @media (max-width:900px){ .theses-cards { grid-template-columns:1fr; gap:16px; } }

  /* A card-family block: a light kicker heading over a masonry pack of its cards. */
  .fam { margin:0 0 6px; }
  .fam-h { font-size:13px; text-transform:uppercase; letter-spacing:.06em; font-weight:800;
           color:#556072; margin:20px 0 12px; padding-bottom:6px; border-bottom:1px solid var(--line); }
  /* Full-bleed cards inside a family grid (the midway strip, the workflow figure, the alignment-grows
     strip) span every track. */
  .card.wide { grid-column:1 / -1; }
  .card.wide .loop { border:none; background:none; padding:0; margin:8px 0 0; }
  .card.wide .wf { position:static; left:auto; transform:none; width:100%; max-width:1400px;
                   margin:8px auto 0; }
  .card.wide .midway-fp { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);
                          gap:20px 30px; align-items:center; margin-top:4px; }
  .card.wide .midway-fp .cd-fig { margin:0; }
  @media (max-width:820px){ .card.wide .midway-fp { grid-template-columns:1fr; gap:14px; } }
"""

# (title, subtitle, href, extra-attrs) for the landing action cards
LANDING_CARDS = [
    ("Views of the governance catalogue", "the whole catalogue at a glance — four views, mechanisms clickable", "catalogue-figure.html", ""),
    ("Abstractions glossary", "the artifacts the mechanisms are built from — named by role, not filename", "ABSTRACTIONS.html", ""),
    ("Quick start", "two ways to adopt — DIY the catalogue, or install the self-governance skill", "quick-start.html", ""),
    ("Starter CLAUDE.md", "a mature one — have Claude fold it into your CLAUDE.md (see Quick start)", "downloads/CLAUDE-starter.md", " download"),
    ("Epic template", "the section shape + Definition-of-Done, portable", "downloads/EPIC-TEMPLATE-starter.md", " download"),
    ("Design-doc template", "invariants-driven; dynamics + observability blocks", "downloads/design-doc-template-starter.md", " download"),
    ("Agent-brief template", "the dispatch — scope, context, acceptance, hand-back", "downloads/agent-brief-starter.md", " download"),
    ("Op-playbook template", "situation → inspect → healthy → what-to-do", "downloads/op-playbook-starter.md", " download"),
    ("Governance-lint example", "a real, runnable lint — copy the shape, change the check", "downloads/governance-lint-example.py", " download"),
    ("Download the catalogue", "all writeups as a markdown ZIP", "https://github.com/davisjam/agent-governance-mechanisms/archive/refs/heads/main.zip", ""),
]

_FLOW = [
    ("Velocity exposes failure", "Agent changes surface ambiguity, drift, and weak boundaries — fast."),
    ("Monitoring intelligence classifies it", "Local defect, or a recurring structural weakness?"),
    ("Convert to governance", "Encode it: a type, a lint, a schema, a gate, or a harness rule."),
    ("Action space narrows", "Every later agent inherits a smaller, more explicit space."),
]
# The outcome of the loop — a centered fact, not a numbered step.
_FLOW_OUTCOME = ("Governability compounds",
                 "The environment absorbs more agent work, so velocity stays sustainable.")


def _inline_svg_figure(rel_path: str, caption: str, cls: str = "lfig") -> str:
    """Splice a book SVG asset inline as a <figure>, mirroring the book's figure directive.

    Reads the .svg under book/, strips any XML prolog / leading comment so only <svg>…</svg>
    remains, and neutralizes the intrinsic width/height so the viewBox drives responsive
    scaling (CSS caps the max width). Falls back to an empty string if the asset is missing.
    """
    path = os.path.join(ROOT, "book", rel_path)
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return ""
    m = re.search(r"<svg\b.*</svg>", raw, re.S)
    if not m:
        return ""
    svg = m.group(0)
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r"\1", svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r"\1", svg, count=1)
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="{cls}">{svg}{cap}</figure>'


def _inline_svg(rel_path: str) -> str:
    """Return just the responsive <svg>…</svg> for a book asset, no <figure>/caption wrapper.

    Used by the landing board, where a figure is composed inside a box (its caption
    text folded into the box's prose) rather than rendered as a standalone <figure>.
    Falls back to an empty string if the asset is missing.
    """
    fig = _inline_svg_figure(rel_path, "", cls="")
    m = re.search(r"<svg\b.*</svg>", fig, re.S)
    return m.group(0) if m else ""


def _landing_flow() -> str:
    steps = []
    for i, (title, detail) in enumerate(_FLOW, 1):
        steps.append(f'<div class="fstep"><span class="fn">{i}</span><b>{title}</b><span>{detail}</span></div>')
        if i < len(_FLOW):
            steps.append('<div class="farrow">→</div>')
    row = '<div class="flow">\n    ' + "\n    ".join(steps) + '\n    </div>'
    # orthogonal return loop: down from box 4 (x≈885), left across, then a clean VERTICAL run up into
    # box 1 (x≈115) so the arrowhead attaches square to the line. Rounded corners (Q) keep it from looking
    # harsh; the final `V17` segment is straight vertical into the arrowhead base at y=17.
    mustache = ('<svg class="mustache" viewBox="0 0 1000 76" aria-hidden="true">'
                '<path d="M885 10 V52 Q885 62 875 62 H125 Q115 62 115 52 V17" '
                'fill="none" stroke="#9aa4b2" stroke-width="2.5" stroke-linejoin="round"/>'
                '<polygon points="115,3 107,17 123,17" fill="#9aa4b2"/></svg>')
    outcome = f'<p class="loop-outcome"><b>{_FLOW_OUTCOME[0]}.</b> {_FLOW_OUTCOME[1]}</p>'
    return row + "\n    " + mustache + "\n    " + outcome


def _card(slug: str, kicker: str, title: str, frame: str, body: str,
          more_href: str = "", more_label: str = "read the full treatment →",
          fig_asset: str = "", cls: str = "", title_accent: bool = False,
          more_download: bool = False) -> str:
    """Build one uniform clickable landing card as a native <details>.

    The <summary> is the always-visible header (kicker + title + one-line `frame`, plus a small
    figure thumbnail when `fig_asset` is given). Expanding reveals `body` (the inline "peek" — a
    short summary and, when `fig_asset` is set, the same figure rendered large + legible) followed
    by a "read the full treatment →" link-through to `more_href`. The whole card carries
    id="card-<slug>" so it is deep-linkable; the slug must be unique across the page.

    A figure appears TWICE — as the summary thumbnail and (large) in the body — so both the summary
    and the peek are figure-forward. To keep element-ids unique (check_no_duplicate_ids), any ids
    inside the inlined SVG are namespaced per placement, so the thumb copy and the body copy never
    collide with each other or with another card's figure.
    """
    fig_svg = _inline_svg(fig_asset) if fig_asset else ""
    thumb = ""
    fig_block = ""
    if fig_svg:
        thumb = f'<span class="cd-thumb" aria-hidden="true">{_ns_svg_ids(fig_svg, f"{slug}-th")}</span>'
        fig_block = f'<figure class="cd-fig">{_ns_svg_ids(fig_svg, f"{slug}-fig")}</figure>'
    tcls = "cd-title accent-t" if title_accent else "cd-title"
    kick = f'<span class="cd-kicker">{kicker}</span>' if kicker else ""
    frm = f'<span class="cd-frame">{frame}</span>' if frame else ""
    dl = " download" if more_download else ""
    more = (f'<a class="cd-more" href="{more_href}"{dl}>{more_label}</a>'
            if more_href else "")
    ccls = ("card " + cls).strip()
    return (
        f'<details class="{ccls}" id="card-{slug}">\n'
        f'  <summary>{kick}<span class="{tcls}">{title}</span>{frm}'
        f'<span class="cd-toggle" aria-hidden="true"></span>{thumb}</summary>\n'
        f'  <div class="cd-body">{fig_block}{body}{more}</div>\n'
        f'</details>')


def _ns_svg_ids(svg: str, ns: str) -> str:
    """Namespace every id="…" (and its #id references) inside an inlined SVG with a `ns-` prefix, so
    the same figure spliced twice (summary thumb + body) — or the same asset reused across cards —
    never yields a duplicate element id (check_no_duplicate_ids fails on any repeat). Rewrites
    id="x" → id="ns-x", url(#x) → url(#ns-x), href="#x" → href="#ns-x", and xlink:href likewise."""
    ids = set(re.findall(r'\bid="([^"]+)"', svg))
    if not ids:
        return svg
    for i in sorted(ids, key=len, reverse=True):
        esc = re.escape(i)
        svg = re.sub(rf'\bid="{esc}"', f'id="{ns}-{i}"', svg)
        svg = re.sub(rf'url\(#{esc}\)', f'url(#{ns}-{i})', svg)
        svg = re.sub(rf'(xlink:href|href)="#{esc}"', rf'\1="#{ns}-{i}"', svg)
    return svg


def _landing_cards() -> str:
    """The catalogue-explore action cards, each a uniform clickable card (summary = title + frame;
    the peek repeats the frame and the link-through IS the card's destination)."""
    out = []
    for t, sub, href, extra in LANDING_CARDS:
        slug = _slug(t)
        dl = "download" in extra
        label = ("download →" if dl else "open →")
        body = f'<p>{sub}</p>'
        out.append(_card(slug, "Explore the catalogue", t, sub, body,
                         more_href=href, more_label=label, more_download=dl))
    return "\n  ".join(out)


def _slug(text: str) -> str:
    """A stable, url-safe slug from a card title (lowercased, non-alnum → single hyphens)."""
    s = re.sub(r"<[^>]+>", "", text)               # drop any inline tags
    s = re.sub(r"&[a-z]+;", " ", s)                # drop entities (&amp; etc.)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "card"


# The two schools + the midway (title, blurb, pole-label, is-midway, [(ref-label, url), ...])
SCHOOLS = [
    ("Vibe coding",
     "Prompt an agent, accept what looks right, iterate by feel. Fast and fluid, but quality rests on "
     "the model and your eye. At scale the same failures keep recurring, and human review becomes the "
     "bottleneck.", "all velocity — no durable guardrails", False,
     [("Karpathy — coined “vibe coding”", "https://x.com/karpathy/status/1886192184808149383"),
      ("Steve Yegge’s Gas Town", "https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04")]),
    ("Governance-centric",
     "The midway. Velocity <b>exposes</b> failures; you <b>convert</b> each recurring one into a guardrail: "
     "a type, a lint, a gate. The guardrails grow out of real failures, so code stays fast <i>and</i> "
     "stays trustworthy.", "velocity + guardrails grown from failure", True, []),
    ("Oversight-centric",
     "Check <i>everything</i> before you trust it, whether a human reviews every change or a formal "
     "specification is verified against. Rigorous and safe, but checking becomes the bottleneck: all of it "
     "must be vetted, and neither humans nor specs anticipate the failures that only appear at velocity. "
     "(Spec-driven development is this, with the spec as the checker.)",
     "all oversight — everything checked", False,
     [("Meyer, CACM — “From Probable to Provable”", "https://dl.acm.org/doi/full/10.1145/3773295"),
      ("vibe-OS / vibe-tools (formal tooling for AI)", "https://homes.cs.washington.edu/~oskin/vibeos/vibetools.html")]),
]

# The three-column "way of thinking" — the AI-First Engineering Method (A.1–A.4 groups), engineering-oriented
WAYS = [
    ("Architect deliberately", [
        "Implementation is cheap; architecture compounds. Buy the right design, not the fast one.",
        "Name shapes with types; primitive-passing leaves the architecture anonymous.",
        "Make models, state, and policy explicit: state machines over scattered counters, enums over magic strings.",
        "One canonical way beats many clever ones. Agents will apply patterns they see 200× with no debate.",
        "Attack accidental complexity; budget for the essential kind.",
    ]),
    ("Convert failure into machinery", [
        "When a failure recurs, encode it (a lint, type, gate, or schema) instead of re-inspecting for it.",
        "Move audits to lints: cheap, at-commit, deterministic beats expensive and post-hoc.",
        "Let the compiler and gates hold the line; review is not a substitute for static analysis.",
        "Never fail quiet: every caught error logs, re-throws, or is justified in a comment.",
        "No compatibility shims. Migrate every call site in the same change.",
    ]),
    ("Keep judgment scarce &amp; central", [
        "Carry work autonomously; surface only the architectural calls.",
        "Hyper-experimentation: pilot, compare, measure; a cheap experiment beats a debate, and negative results are wins.",
        "Verify claims and trust nothing stale. Re-run the gates yourself, because markers rot.",
        "Reason about second-order dynamics: what happens at T+100, or under concurrency?",
        "Documentation encodes invariants that drive tests, not prose that rots.",
    ]),
]


def _landing_schools() -> str:
    """The two schools + the midway, each a uniform clickable card (the summary carries a one-line
    frame; the peek reveals the fuller blurb, examples, and the pole label)."""
    out = []
    for title, blurb, pole, mid, refs in SCHOOLS:
        cls = "mid" if mid else ""
        rhtml = ""
        if refs:
            lis = "".join(f'<li><a href="{u}">{lbl}</a></li>' for lbl, u in refs)
            rhtml = f'<div class="srefs"><span class="lbl">Examples:</span><ul>{lis}</ul></div>'
        kicker = "The midway" if mid else "Between two schools"
        frame = pole
        body = f'<p>{blurb}</p>{rhtml}<span class="pole">{pole}</span>'
        more = ("book/2.3-the-governed-environment.html" if mid else "book/1.1-the-printer.html")
        out.append(_card(_slug("school-" + title), kicker, title, frame, body,
                         more_href=more, cls=cls))
    return "\n  ".join(out)


_WAY_FRAME = {
    "Architect deliberately": "buy the right design; name shapes with types",
    "Convert failure into machinery": "encode each recurring failure as a lint, type, or gate",
    "Keep judgment scarce &amp; central": "carry work autonomously; spend human judgment where it counts",
}


def _landing_ways() -> str:
    """The three "way of thinking" stances, each a uniform clickable card (the peek reveals the
    stance's bullet list; the link-through goes to the lessons chapter)."""
    out = []
    for title, items in WAYS:
        lis = "".join(f'<li>{it}</li>' for it in items)
        body = f'<ul class="cd-list">{lis}</ul>'
        frame = _WAY_FRAME.get(title, "")
        out.append(_card(_slug("way-" + title), "Way of thinking", title, frame, body,
                         more_href="book/4.5-lessons-learned.html"))
    return "\n  ".join(out)


# ── The site AS A PROJECTION of the book's typed models ──────────────────────────────────────────
# The definitions section and the outcomes section are DERIVED VIEWS: their content is read straight
# from the model files at build time (book/data/definitions.json, book-models/outcomes.json filtered by
# book/data/outcomes-site.json), never hand-authored in the landing HTML. A build renders them; the
# drift checks (check_definitions_* / check_outcomes_site_* in tests/html.py) keep the projection
# faithful. This is the concept-model precedent (concepts.json ↔ the concept cards) extended to the
# definitions and the core learning-outcomes view. See book-models/SITE-VIEW.md.

def _load_definitions() -> list[dict]:
    """Read book/data/definitions.json → the ordered list of definition records (meta `_`-keys stripped,
    ordered by the `_order` meta list). The site's Definitions section is a projection of this model."""
    path = os.path.join(ROOT, "book", "data", "definitions.json")
    if not os.path.isfile(path):
        return []
    raw = json.load(open(path, encoding="utf-8"))
    order = raw.get("_order", [])
    recs = {k: v for k, v in raw.items() if not k.startswith("_")}
    ordered = [recs[k] | {"_slug": k} for k in order if k in recs]
    ordered += [v | {"_slug": k} for k, v in recs.items() if k not in order]  # any un-ordered, appended
    return ordered


def _landing_definitions() -> str:
    """The four core-term definitions, each a uniform clickable card projected from
    book/data/definitions.json. The summary carries the term + a one-line frame (the box's opening
    clause); the peek renders the full green-box definition, the per-aspect elaboration, and the
    traceability line (owed book home + lexicon + concept model). Site element ⟵ model element: the
    card id is `def-<slug>` = the record's `site_home`, the join key the drift check asserts."""
    out = []
    for rec in _load_definitions():
        slug = rec["_slug"]
        site_home = rec.get("site_home", f"def-{slug}")
        card_slug = site_home[len("card-"):] if site_home.startswith("card-") else site_home
        term = _esc(rec.get("term", slug))
        box = _esc(rec.get("box", ""))
        frame = box.split(" — ")[0].split(". ")[0].rstrip(".") + "…" if box else ""
        aspects = "".join(
            f'<li><b>{_esc(a.get("lead", ""))}</b> {_esc(a.get("text", ""))}</li>'
            for a in rec.get("aspects", []))
        owed = rec.get("book_home_owed", {}) or {}
        owed_status = owed.get("status", "owed")
        section = _esc(owed.get("section", "the book"))
        if owed_status == "landed" and rec.get("book_home"):
            home = f'<a href="{_esc(rec["book_home"])}">{section}</a>'
        else:
            home = f'<span class="def-owed">{section} (owed — drafted, not yet landed)</span>'
        trace = (f'<p class="def-trace"><b>Book home:</b> {home} · '
                 f'<a href="book/6.2-glossary.html">lexicon</a> · '
                 f'projected from the definitions model.</p>')
        body = (f'<blockquote class="def-box">🟢 <b>{term}</b> — {box}</blockquote>'
                f'<ul class="cd-list def-aspects">{aspects}</ul>{trace}')
        # The card id becomes `card-<card_slug>`; site_home stores the FULL id, so we pass card_slug so
        # _card emits id="{site_home}". When site_home is `def-<slug>`, card_slug == site_home minus no
        # prefix — so we build the details manually to honor the exact declared id.
        out.append(
            f'<details class="card def-card" id="{_esc(site_home)}">\n'
            f'  <summary><span class="cd-kicker">Definition</span>'
            f'<span class="cd-title">{term}</span>'
            f'<span class="cd-frame">{frame}</span>'
            f'<span class="cd-toggle" aria-hidden="true"></span></summary>\n'
            f'  <div class="cd-body">{body}</div>\n'
            f'</details>')
    return "\n  ".join(out)


def _outcome_index_by_id() -> dict:
    """{outcome_id: record} over book-models/outcomes.json — the derived outcomes view the site projects
    a slice of. Read-only: the site is a projection OF this model, never an edit to it."""
    path = os.path.join(ROOT, "book-models", "outcomes.json")
    if not os.path.isfile(path):
        return {}
    raw = json.load(open(path, encoding="utf-8"))
    return {o["outcome_id"]: o for o in raw.get("outcomes", []) if o.get("outcome_id")}


def _load_outcomes_site() -> dict:
    """Read book/data/outcomes-site.json — the SELECTION + traceability sidecar (which outcomes the site
    surfaces, and each one's book-home link). Thin by design: outcome prose is read from outcomes.json."""
    path = os.path.join(ROOT, "book", "data", "outcomes-site.json")
    if not os.path.isfile(path):
        return {}
    return json.load(open(path, encoding="utf-8"))


def _outcome_row_id(outcome_id: str) -> str:
    """A stable per-row landing id from an outcome_id (id='outcome-<safe-slug>'), so each projected
    outcome is deep-linkable and the drift check can join site→model per row."""
    return "outcome-" + re.sub(r"[^a-z0-9]+", "-", outcome_id.lower()).strip("-")


_BLOOM_ORDER = ["know", "understand", "apply", "analyze", "evaluate", "create"]


def _landing_outcomes() -> str:
    """The core learning-outcomes view — 'what you'll be able to do' — projected from
    book-models/outcomes.json filtered by book/data/outcomes-site.json's selection. Book-level outcomes
    first, then Part-level; each row renders the outcome's `statement` STRAIGHT FROM the model (no copy),
    a bloom-verb tag, and a link to its book home. Re-running the outcomes drain re-syncs this section."""
    site = _load_outcomes_site()
    if not site:
        return ""
    by_id = _outcome_index_by_id()
    home_map = site.get("_book_home_map", {})
    selected = [by_id[oid] for oid in site.get("projected", []) if oid in by_id]
    # book-level rows first, then part-level; within a granularity, keep declared order.
    selected.sort(key=lambda o: 0 if o.get("granularity") == "book" else 1)
    rows = []
    for o in selected:
        oid = o["outcome_id"]
        gran = o.get("granularity", "")
        unit = o.get("primary_unit", "")
        label = "The book" if gran == "book" else unit.replace("part-", "Part ")
        home = home_map.get(unit, "book/index.html")
        bloom = _esc(o.get("bloom", ""))
        stmt = _esc(o.get("statement", ""))
        rows.append(
            f'<li id="{_outcome_row_id(oid)}" class="oc-row">'
            f'<span class="oc-unit">{_esc(label)}</span>'
            f'<span class="oc-bloom">{bloom}</span>'
            f'<span class="oc-stmt">{stmt}</span>'
            f'<a class="oc-more" href="{_esc(home)}">read →</a></li>')
    body = ('<p>Each promise below is a learning outcome projected from the book\'s outcomes model — '
            'the "after this Part, the reader can…" spine, derived from the prose and kept in sync by a '
            'drift check. The book-level goals come first, then one per Part.</p>'
            f'<ul class="oc-list">{"".join(rows)}</ul>')
    return (
        '<details class="card wide accent" id="outcomes-view" open>\n'
        '  <summary><span class="cd-kicker">What you\'ll be able to do</span>'
        '<span class="cd-title accent-t">The learning outcomes, book and Part</span>'
        '<span class="cd-frame">The book\'s and each Part\'s "you\'ll be able to…", projected from the outcomes model.</span>'
        '<span class="cd-toggle" aria-hidden="true"></span></summary>\n'
        f'  <div class="cd-body">{body}'
        '<a class="cd-more" href="book/index.html">read the book →</a></div>\n'
        '</details>')


# Defined in <head> so the workflow-figure iframe's `onload="fitFig(this)"` can never fire before the
# function exists (a fast/cached iframe load previously raced the later inline <script> → "fitFig is
# not defined"). Doubled braces so it survives `LANDING_INTRO.format(...)` — but LANDING_INTRO is the
# only thing .format()'d; this constant is spliced into the head literal, so it needs single braces.
LANDING_HEAD_SCRIPT = """<script>
function fitFig(f){
  try{
    var d=f.contentWindow.document, w=d.documentElement.scrollWidth||1040, h=d.documentElement.scrollHeight||600;
    var frame=f.parentElement, wf=frame.parentElement;
    var avail=wf.clientWidth, s=Math.min(1, avail/w);
    f.style.width=w+'px'; f.style.height=h+'px';
    f.style.transformOrigin='top left'; f.style.transform='scale('+s+')';
    // size the frame to the SCALED figure and center it, so a figure narrower than the
    // column isn't pinned left by the top-left transform origin
    frame.style.width=(w*s)+'px'; frame.style.height=(h*s)+'px'; frame.style.margin='0 auto';
  }catch(e){}
}
</script>
"""

LANDING_INTRO = """  <!-- ===================== HERO 2-up =====================
       A real two-column opening: lead prose left, the MAGE-method overview figure pulled up beside it
       on the right, so the top uses the full width and "one picture" lands immediately. -->
  <div class="hero">
    <div class="hero-lead">
      {book_title_block}
      <p class="lead">Generative AI is shifting software engineering from a practice built around scarce
      implementation toward one built around <span class="term">abundant, low-cost code</span>. The hard part
      stops being writing code and becomes <span class="term">governing the conditions under which fast code
      can be trusted</span>. This catalogue serves a method for doing that:
      <span class="term">Model-Based Agentic Software Engineering</span> (MAGE) — engineering with a fleet of
      coding agents by binding intent to typed models the fleet reasons through, and governing what it builds
      with mechanisms that prevent or detect drift.</p>
      <p class="lead" style="font-size:16.5px;">MAGE is <span class="term">one method with two theses</span> —
      a <b>Modeling Thesis</b> and an <b>Alignment Thesis</b> — and this page is built around them. Every unit
      below is a clickable card: open it for a quick peek, then follow the link through to the full treatment
      in the book. <a href="quick-start.html"><em>QUICK START: install the skills for Claude →</em></a></p>
    </div>
    <div class="hero-fig-2up">
      <figure>{hero}<figcaption>A cheap agent fleet, left ungoverned, drifts into <b>churn</b> as its work
      outgrows the context window. Governed through the <b>Modeling Thesis</b> (a typed model the fleet reasons
      through) and the <b>Alignment Thesis</b> (a mechanism that keeps output aligned with intent), it converges
      on trustworthy software at velocity.</figcaption></figure>
    </div>
  </div>

  <hr class="sep" />

  <!-- ===================== THE PAIR OF THESES (matched card set) =====================
       The two theses stay a grouped, adjacent pair ("Thesis I of II" / "Thesis II of II") but are now the
       same <details class="card"> primitive as every other card. Two-up on wide, stacked ≤900px; each carries
       a unique id (card-thesis-modeling / card-thesis-alignment) and each peek surfaces its figure large. -->
  <div class="theses-cards">
    <details class="card accent" id="card-thesis-modeling" open>
      <summary>
        <span class="cd-kicker">Thesis I of II</span>
        <span class="cd-title accent-t">The Modeling Thesis</span>
        <span class="cd-frame">Documentation, taken to its limit, is a typed model.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
        <span class="cd-thumb" aria-hidden="true">{model_fig_th}</span>
      </summary>
      <div class="cd-body">
        <figure class="cd-fig">{model_fig}<figcaption>Documentation, at its limit, is a typed model — one an
        agent reasons over without error and that a build-time drift check keeps honest.</figcaption></figure>
        <p>Give agents good documentation and tests, then point them at it — the first move everyone finds on
        their own. The step the training data won't suggest is the next one: <b>documentation has a hierarchy,
        and its top is not prose. It is a typed model.</b> A context-bounded agent working on a
        context-<em>exceeding</em> system needs a <b>typed, queryable, drift-checked model</b> to reason
        through — the bridge between the agent and the codebase it cannot fit in its head. The catalogue's
        <b>models-bridge</b> role is this bridge, made concrete.</p>
        <a class="cd-more" href="book/1.2-loops-and-models.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card accent" id="card-thesis-alignment" open>
      <summary>
        <span class="cd-kicker">Thesis II of II</span>
        <span class="cd-title accent-t">The Alignment Thesis</span>
        <span class="cd-frame">A quality goal splits into a constraint that prevents and a sensor that catches.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
        <span class="cd-thumb" aria-hidden="true">{mech_fig_th}</span>
      </summary>
      <div class="cd-body">
        <figure class="cd-fig">{mech_fig}<figcaption>A quality goal splits into two moves: a constraint that
        prevents the error, and a sensor that catches it.</figcaption></figure>
        <p>A mechanism the environment enforces keeps output aligned with intent, and it takes one of two
        forms: <b>prevent</b> the error, or <b>catch</b> it. However you arrived at the goal — up front from
        the domain or in response to a failure — a <b>constraint</b> scopes the action space so the whole class
        is impossible, and a <b>sensor</b> lets the mistake happen but detects it in time, failing the loop
        iteration so the agent runs again to fix it. A third set of goals splits into <b>neither</b> — no sensor
        and no constraint reaches them, so they stay a human job; that <b>residual</b> is what the mechanisms
        leave behind.</p>
        <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
      </div>
    </details>
  </div>

  <hr class="sep" />

  <!-- ===================== THE FOUR DEFINITIONS (projected from book/data/definitions.json) =========
       The core vocabulary the two theses ride on — model, agent, engineering, software engineering.
       Each card is DERIVED from the definitions model (green box + per-aspect elaboration + traceability
       to its owed Part-2 book home); a build renders them and a drift check keeps them in sync. -->
  <div class="fam">
    <div class="fam-h">The four definitions — the vocabulary the theses ride on</div>
    <div class="masonry">
    {definitions}
    </div>
  </div>

  <hr class="sep" />

  <!-- ===================== FAMILY BLOCKS OF CARDS =====================
       Everything below groups into named families; within each family the cards pack into a CSS multi-column
       masonry (>= 3 columns wide, 1 on a phone — the check-responsive gate). Every card is the same clickable
       <details> primitive with a unique id, a peek, and a link-through. -->

  <div class="fam">
    <div class="fam-h">Two schools, and the midway between them</div>
    <div class="masonry">
    {schools}
    <details class="card" id="card-velocity-oversight-axis">
      <summary>
        <span class="cd-kicker">The spectrum</span>
        <span class="cd-title">← velocity &nbsp;•&nbsp; oversight →</span>
        <span class="cd-frame">Where each school sits on the one axis that orders them.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>The two poles trade off the same way: <b>all velocity</b> ships fast but leaves quality implicit;
        <b>all oversight</b> checks everything but makes checking the bottleneck. The <span class="term">midway</span>
        keeps velocity <i>and</i> grows guardrails from the failures velocity surfaces.</p>
        <a class="cd-more" href="book/1.1-the-printer.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card wide accent" id="card-midway-discipline" open>
      <summary>
        <span class="cd-kicker">The midway is a discipline</span>
        <span class="cd-title">Governance-centric — the synthesis</span>
        <span class="cd-frame">Three process models for agentic engineering; this site takes the third.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
        <span class="cd-thumb" aria-hidden="true">{schools_fig_th}</span>
      </summary>
      <div class="cd-body">
        <div class="midway-fp">
          <figure class="cd-fig">{schools_fig}</figure>
          <div class="midway-body">
          <p>Three process models for agentic engineering. The two poles: velocity-centric agents hand work
          around a ring of job titles with the quality mechanism left implicit; oversight-centric keeps a human
          next to each bounded piece — honest, but the human's attention does not scale with the fleet.
          <span class="term">Governance-centric</span> is the synthesis: the agents sit inside a containing
          environment of enforced mechanisms the human sets up in advance. This site takes the third.</p>
          <p>That midway means <span class="term">establishing and maintaining a governed engineering
          environment</span> — working in two directions at once: <b>up front</b> you specify what you can (the
          architecture that makes a class of error impossible, the model the fleet reasons through, the templates
          that put a change on rails); <b>in flight</b> you let velocity surface the failures you couldn't foresee
          and convert each recurring one into a durable guardrail.</p>
          <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
          </div>
        </div>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">The Modeling Thesis — why a typed model beats prose</div>
    <div class="masonry">
    <details class="card" id="card-agent-legible-precise">
      <summary>
        <span class="cd-kicker">Modeling Thesis</span>
        <span class="cd-title">Agent-legible &amp; precise</span>
        <span class="cd-frame">Abstraction shrinks the space an agent can be wrong in.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>A six-state machine with typed invariants is something an agent reasons over <b>without error</b>
        the way it cannot over 300,000 lines of prose-and-code. Abstraction shrinks the space it can be wrong
        in, not just the token count. A model is more precise than any document.</p>
        <a class="cd-more" href="book/1.2-loops-and-models.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-it-cant-lie">
      <summary>
        <span class="cd-kicker">Modeling Thesis</span>
        <span class="cd-title">It can’t lie</span>
        <span class="cd-frame">A model wired to a build-time drift check cannot rot.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>A document rots the moment the code moves; a model wired to a <b>build-time drift check cannot</b>:
        the gate stays red until the map matches the territory again. That guarantee is what prose can never
        give — though a drift gate proves the model and code <i>agree</i>, not that either is <i>right</i>: the
        model must be <b>authored</b>, not merely read off the code, or a mirror of the bug passes green (2.2).</p>
        <a class="cd-more" href="book/2.2-models-and-the-semantic-gap.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card tint" id="card-model-pays-back">
      <summary>
        <span class="cd-kicker">Modeling Thesis</span>
        <span class="cd-title">Cheap to keep, pays back</span>
        <span class="cd-frame">Agents maintain the model like docs and tests.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Because agents build and maintain the model the way they maintain docs and tests, pointing them at it
        costs almost nothing, and it pays back in <b>higher code quality, fewer tokens spent rederiving what the
        model already states, and fewer mistakes.</b></p>
        <a class="cd-more" href="book/1.2-loops-and-models.html">read the full treatment →</a>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">The Alignment Thesis — constraints and sensors</div>
    <div class="masonry">
    <details class="card accent" id="card-constraint">
      <summary>
        <span class="cd-kicker">Alignment Thesis</span>
        <span class="cd-title accent-t">Constraint</span>
        <span class="cd-frame">Make the wrong move impossible to pick.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Scope the agent's action space so the wrong move is <b>never available to pick</b>: the typed model,
        an enum instead of a free-form string, one sanctioned seam. A constraint <i>prevents</i> drift — the
        mistake costs no iteration, because the compiler rejects it on the spot.
        (<a href="https://en.wikipedia.org/wiki/Poka-yoke">Poka-yoke</a> for software; building a constraint
        is what "architecture" does.)</p>
        <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card accent" id="card-sensor">
      <summary>
        <span class="cd-kicker">Alignment Thesis</span>
        <span class="cd-title accent-t">Sensor</span>
        <span class="cd-frame">Where you can't prevent it, detect it after the fact.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Where you can't prevent it, <b>detect it after the fact</b>: a lint, a gate, a validator, a test
        suite that fires on a violation and holds the line. A sensor <i>detects</i> drift and fails the loop
        iteration, so the agent runs again to fix what it caught. It costs iterations — which is why you don't
        reach for it first.</p>
        <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-generate-to-falsify">
      <summary>
        <span class="cd-kicker">Alignment Thesis · validation</span>
        <span class="cd-title">Generate inputs to falsify a model</span>
        <span class="cd-frame">Property tests, fuzzing, and fuzz+model are one move.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>The strongest sensors don't check one example — they <b>generate</b> inputs and try to falsify a
        specification the model supplies. Property-based testing, fuzzing, and fuzzing driven by the typed model
        are one move at three richnesses of oracle: the model names the stable point in the spec, and the
        generator hunts a counterexample to it.</p>
        <a class="cd-more" href="book/4.6-generative-validation.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-constraint-vs-sensor">
      <summary>
        <span class="cd-kicker">Constraint vs. sensor</span>
        <span class="cd-title">Firewall vs. smoke detector</span>
        <span class="cd-frame">Prefer a constraint; wrap in sensors for what you can't scope away.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>A <b>sensor</b> lets the mistake happen and catches it in time — a smoke detector. A
        <b>constraint</b> makes the whole class of mistake impossible — a firewall. Prefer a constraint where
        you can build one, because a sensor still spends an iteration. But a constraint across the only exit
        blocks the people trying to leave — an over-scoped design stops legitimate work as surely as the error,
        so add a sensor for the drift you cannot scope away. Most real mechanisms are a package across both: a
        soft constraint that aims the agent, wrapped in hard sensors that catch what it only aims at.</p>
        <a class="cd-more" href="book/2.6-when-guardrails-collide.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card tint" id="card-residual">
      <summary>
        <span class="cd-kicker">The residual</span>
        <span class="cd-title">Neither move reaches it</span>
        <span class="cd-frame">Some goals have no sensor and no constraint — they stay a human job.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Not every goal splits into a constraint or a sensor. Some have <b>neither</b> — no cheap sensor can
        see the failure, no constraint can scope it away, because the failure is an absence nobody specified. A
        missing authorization check has <b>no failing test by definition</b>: a test that caught it would mean it
        was specified, and a specified check would not be missing. That goal stays a <b>human</b> job, and which
        of your goals land here sets your real throughput ceiling. This is not the soft end of a spectrum — a
        soft mechanism is still a mechanism; the residual has none. Naming it is the framework's honest edge:
        here is what the catalogue does <i>not</i> reach.</p>
        <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card wide accent" id="card-alignment-grows">
      <summary>
        <span class="cd-kicker">How the Alignment half grows</span>
        <span class="cd-title">Reading failure as a missing mechanism</span>
        <span class="cd-frame">Velocity surfaces a failure class; you convert each recurring one into a mechanism.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>You place some constraints and sensors up front, from what you know about the domain. The rest you
        learn along the way: velocity surfaces a failure class earlier governance didn't address, and you convert
        each recurring one into a mechanism. That conversion is the way of thinking inside MAGE — how the
        Alignment Thesis grows past what you could specify in advance.</p>
        <div class="loop">
        {flow}
        <p class="tail">Implementation is cheap; the judgment that decides <i>which governance should
        exist</i> is the costly, human part. Two paired concepts hold it together:</p>
        <ul class="tail-pair">
          <li><b>Governance makes velocity sustainable</b> — guardrails are what let the fleet keep shipping
          fast without drowning in its own failures.</li>
          <li><b>Judgment decides which governance to build</b> — recognizing which failures deserve a
          guardrail (and which are one-offs) is the hard, human call.</li>
        </ul>
        </div>
        <a class="cd-more" href="book/4.5-lessons-learned.html">read the full treatment →</a>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">What the engineer's job becomes</div>
    <div class="masonry">
    <details class="card wide accent" id="card-universal-language" open>
      <summary>
        <span class="cd-kicker">The engineer's job</span>
        <span class="cd-title accent-t">Models are the universal language of engineering</span>
        <span class="cd-frame">Code was the bottleneck; now the model is the work.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>For most of software's history the scarce resource was <b>implementation</b> — someone had to type
        the thing into existence, and that typing was the bottleneck everything queued behind. Agents moved
        that bottleneck: code is cheap to produce and fast to change, and a model wired to a drift check keeps
        the map in sync for free. What is <b>not</b> cheap is deciding what to build and authoring the model
        whose properties drive the tradeoffs. So the engineer's job <b>relocates up</b> — from producing code to
        <b>authoring the models</b> every other engineering discipline has always reasoned in, now finally cheap
        enough for software to speak too.</p>
        <a class="cd-more" href="book/6.0-implications-for-se.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-judgment-moved-up">
      <summary>
        <span class="cd-kicker">The engineer's job</span>
        <span class="cd-title">The judgment moved up, not away</span>
        <span class="cd-frame">You're still accountable for the code an agent typed.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>An engineer was always accountable for choices they did not hand-implement — the compiler they
        picked, the library, the algorithm. Delegating the keystrokes never delegated the accountability. The
        model level strips the <i>accidental</i> cost of holding a large system in a small window and leaves the
        <i>essential</i> difficulty in plain view, where judgment has to meet it. That essential residual does
        not yield to a tool — it moves <b>one level up</b>, from "write correct code" to "author the model that
        says what correct means."</p>
        <a class="cd-more" href="book/6.0-implications-for-se.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card tint" id="card-modelling-democratizes">
      <summary>
        <span class="cd-kicker">The engineer's job</span>
        <span class="cd-title">Modelling democratizes</span>
        <span class="cd-frame">The map used to be the architect's; now everyone can hold one.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Modelling used to be senior work — the one person who could hold the whole system in their head drew
        the map, and everyone else worked below it. Freed from the cost of <b>typing</b> and of <b>keeping the
        map in sync by hand</b>, every engineer can now reason about the system's properties and how their own
        change moves the whole. The map got cheap enough that everyone can hold one.</p>
        <a class="cd-more" href="book/6.0-implications-for-se.html">read the full treatment →</a>
      </div>
    </details>
    </div>
  </div>

  <!-- ===================== THE LEARNING OUTCOMES (projected from book-models/outcomes.json) ==========
       "What you'll be able to do" — the book- and Part-level outcomes, projected from the outcomes view
       model (filtered by book/data/outcomes-site.json's selection). Prose is read straight from the
       model; the drift check keeps the selection honest. -->
  <div class="fam">
    <div class="fam-h">What you'll be able to do — the learning outcomes</div>
    <div class="masonry">
    {outcomes}
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">The way of thinking — three stances</div>
    <div class="masonry">
    {ways}
    <details class="card tint" id="card-ways-note">
      <summary>
        <span class="cd-kicker">Way of thinking</span>
        <span class="cd-title">Where the stances come from</span>
        <span class="cd-frame">Distilled from the AI-First Engineering Method.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Three stances that make the midway work, distilled from the AI-First Engineering Method
        (architecture, controls, and the stance that wields them); the full set ships in the
        <a href="downloads/CLAUDE-starter.md" download>starter CLAUDE.md</a>.</p>
        <a class="cd-more" href="downloads/CLAUDE-starter.md" download>download the starter CLAUDE.md →</a>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">The three skills — harden · operate · communicate</div>
    <div class="masonry">
    <details class="card" id="card-skill-self-governance">
      <summary>
        <span class="cd-kicker">The three skills</span>
        <span class="cd-title">self-governance · <i>harden</i></span>
        <span class="cd-frame">The design-time lens — the census plus the engine that mints new controls.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>The <b>design-time</b> lens: the census of controls plus the engine that mints new ones — what
        exists, what you're missing, how to add one.</p>
        <a class="cd-more" href="book/4.2-the-skills.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-skill-self-operations">
      <summary>
        <span class="cd-kicker">The three skills</span>
        <span class="cd-title">self-operations · <i>operate</i></span>
        <span class="cd-frame">The run-time lens — it runs the substrate those controls govern.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>The <b>run-time</b> lens: it runs the substrate those controls govern — the lifecycle you operate,
        the runbook you follow, the hook you wire.</p>
        <a class="cd-more" href="book/4.2-the-skills.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card" id="card-skill-self-communicate">
      <summary>
        <span class="cd-kicker">The three skills</span>
        <span class="cd-title">self-communicate · <i>communicate</i></span>
        <span class="cd-frame">The prose-and-diagram craft for the docs the other two produce.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>The <b>prose-and-diagram</b> craft: a rhetoric toolkit, the Diátaxis register, a house lexicon, and
        an audit that emits fixes — for the docs the other two produce <i>and</i> the operator's own reports to
        the human.</p>
        <a class="cd-more" href="book/4.2-the-skills.html">read the full treatment →</a>
      </div>
    </details>
    <details class="card tint" id="card-skills-loop">
      <summary>
        <span class="cd-kicker">The three skills</span>
        <span class="cd-title">One substrate, seen three ways</span>
        <span class="cd-frame">The loop closes across govern, operate, and communicate.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>Govern and operate are one substrate seen two ways; communicate is the craft that keeps their output
        legible. The loop closes across all three: operate surfaces a recurring break, govern mints the control,
        communicate writes it up in the shared register.</p>
        <a class="cd-more" href="quick-start.html">install all three →</a>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">The goal, packaged, and the references</div>
    <div class="masonry">
    <details class="card tint" id="card-both-halves">
      <summary>
        <span class="cd-kicker">What this site packages</span>
        <span class="cd-title">Both halves, as three Claude skills</span>
        <span class="cd-frame">{n} governance mechanisms across three roles, each a design pattern.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <p>This site packages <b>both halves</b> — the guidance on what to fix in advance and the machinery for
        responding when something slips through — as three Claude skills with a
        <a href="quick-start.html">quick-start</a>. The catalogue itself is <b>{n} governance mechanisms across
        three roles</b>, each written like a design pattern: the recurring failure it kills, and why it is
        <i>not</i> just the cheaper thing everyone already does.</p>
        <a class="cd-more" href="quick-start.html">start here →</a>
      </div>
    </details>
    <details class="card wide" id="card-governed-environment-figure" open>
      <summary>
        <span class="cd-kicker">The goal: a governed engineering environment</span>
        <span class="cd-title">The development process, as a figure</span>
        <span class="cd-frame">From reviewing your agents' code to reviewing their failures.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <figure class="wf">
          <div class="wf-frame"><iframe id="wf-frame" src="development-workflow.html"
            title="The development-process figure" tabindex="0" onload="window.fitFig&&fitFig(this)"></iframe></div>
          <figcaption>The goal is a governed engineering environment. Some of the governance mechanisms you
          probably know up front: business requirements, security scanners you always run, etc. Others you
          need to figure out through trial and
          error, because they depend on the nature of the errors made by the models you're working with. The
          mindset shift is from reviewing your agents' code, to reviewing their failures and constraining their
          future moves as needed.</figcaption>
        </figure>
        <a class="cd-more" href="book/2.3-the-governed-environment.html">read the full treatment →</a>
        <script>
        // fitFig is DEFINED in <head> (LANDING_HEAD_SCRIPT). The iframe lives inside a <details>, so it may
        // load lazily on first-open; addEventListener('load') fires reliably even after this script runs, and
        // a 'toggle' listener refits when the card is expanded (the iframe has zero size while collapsed).
        (function(){{
          var f=document.getElementById('wf-frame');
          if(f){{ f.addEventListener('load', function(){{ window.fitFig&&fitFig(f); }}); if(window.fitFig) fitFig(f); }}
          var card=document.getElementById('card-governed-environment-figure');
          if(card) card.addEventListener('toggle', function(){{ if(card.open){{ var el=document.getElementById('wf-frame'); if(el&&window.fitFig) fitFig(el); }} }});
          window.addEventListener('resize', function(){{ var el=document.getElementById('wf-frame'); if(el&&window.fitFig) fitFig(el); }});
        }})();
        </script>
      </div>
    </details>
    <details class="card" id="card-references">
      <summary>
        <span class="cd-kicker">References</span>
        <span class="cd-title">Case study &amp; the live system</span>
        <span class="cd-frame">The paper, and the production system it governs.</span>
        <span class="cd-toggle" aria-hidden="true"></span>
      </summary>
      <div class="cd-body">
        <div class="r"><b>Case study:</b> <a href="https://arxiv.org/pdf/2607.01087"><i>Cheap Code, Costly
        Judgment: A Case Study on Governable Agentic Software Engineering</i></a></div>
        <div class="r"><b>Live system it governs:</b> <a href="https://scholaccess.com">DocAble (scholaccess.com)</a></div>
      </div>
    </details>
    </div>
  </div>

  <div class="fam">
    <div class="fam-h">Explore the catalogue — {n} governance mechanisms, the repertoire this loop produced</div>
    <div class="masonry">
    {cards}
    </div>
  </div>

  <div class="book-cta" style="margin:14px 0 28px;">
    <a href="book/index.html"><b>To learn more about the MAGE method, read the book! →</b></a>
    <span class="book-cta-pdf"><a href="{pdf_href}">Download PDF</a></span>
  </div>
"""


VIEWS_CSS = """
  :root { --ink:#1a1a1a; --muted:#555; --line:#e2e8f0;
          --a:#c2410c; --p:#15803d; --b:#b45309; }
  * { box-sizing:border-box; }
  body { margin:0; padding:26px 20px 70px; color:var(--ink); background:#fff; line-height:1.4;
         font-family:"Avenir Next",Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  h1 { font-size:21px; max-width:1080px; margin:0 auto 4px; }
  .sub { max-width:1080px; margin:0 auto 14px; font-size:12.5px; color:var(--muted); }
  .sub a { color:#0b5cad; }
  #tabs { max-width:1080px; margin:0 auto 6px; display:flex; flex-wrap:wrap; gap:6px; }
  .tab { font:inherit; font-size:12.5px; font-weight:600; cursor:pointer; border:1px solid var(--line);
         background:#f8fafc; color:#334155; border-radius:7px; padding:5px 11px; }
  .tab.on { background:#1a1a1a; color:#fff; border-color:#1a1a1a; }
  #stage { max-width:1080px; margin:10px auto 0; }
  .blurb { font-size:12px; color:var(--muted); font-style:italic; margin:0 0 12px; }
  .grp { margin:0 0 16px; }
  .grp h2 { font-size:13.5px; margin:0 0 7px; padding-bottom:3px; border-bottom:1px solid var(--line); }
  .grp h2 .cnt { color:var(--muted); font-weight:500; font-size:11px; }
  .rt-a{color:var(--a);font-weight:800;} .rt-b{color:var(--b);font-weight:800;} .rt-p{color:var(--p);font-weight:800;}
  .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:8px; }
  .card { display:block; text-decoration:none; color:var(--ink); border:1.4px solid #cbd5e1;
          border-radius:8px; padding:7px 9px; background:#fff; transition:box-shadow .1s; }
  .card:hover { box-shadow:0 2px 8px rgba(0,0,0,.10); }
  .card.r-a { border-top:3px solid var(--a); } .card.r-p { border-top:3px solid var(--p); }
  .card.r-b { border-top:3px solid var(--b); }
  .card.e-s  { border-style:dashed; }
  .card.e-sh { border-left:4px solid #38bdf8; }
  .card .c-t { display:block; font-size:12.5px; font-weight:700; letter-spacing:-.01em; }
  .card .c-m { display:block; font-size:10.5px; color:var(--muted); margin-top:2px; }
  .card .c-m code { background:#f6f8fa; padding:0 3px; border-radius:3px; }
  .card .star { color:#f59e0b; }
"""

VIEWS_JS = r"""
const ROLE_ORDER = ["Agent","Bridge","Product"];
const VIEWS = [
  { id:"family",  label:"By role & family", blurb:"The logical view — the structural inventory, grouped as it ships.", key:c=>c.role+" · "+c.family, order:null },
  { id:"enf",     label:"By enforcement",   blurb:"soft (probabilistic, cannot block) → soft·hard → hard (deterministic).", key:c=>c.enforcement, order:["Soft","Soft·Hard","Hard"] },
  { id:"form",    label:"By form",          blurb:"The nine recurring shapes a control takes.", key:c=>c.form, order:null },
];
const roleCls = c => c.role==="Agent"?"r-a":c.role==="Product"?"r-p":"r-b";
const enfCls  = c => c.enforcement==="Hard"?"e-h":c.enforcement==="Soft"?"e-s":"e-sh";
function renderForView(card){                       // one card ← its metadata; clickable + tooltipped
  const star = card.star ? ' <span class="star">★</span>' : '';
  const tip = (card.summary||"").replace(/"/g,'&quot;');
  return '<a class="card '+roleCls(card)+' '+enfCls(card)+'" href="'+card.html+'" title="'+tip+'">'
       + '<span class="c-t">'+card.title+star+'</span>'
       + '<span class="c-m"><code>'+card.form+'</code> · '+card.enforcement+'</span></a>';
}
function groupsFor(v){
  const m = new Map();
  for(const c of CARDS){ const k=v.key(c); (m.get(k)||m.set(k,[]).get(k)).push(c); }
  let keys = [...m.keys()];
  if(v.order) keys.sort((a,b)=>v.order.indexOf(a)-v.order.indexOf(b));
  else if(v.id==="family") keys.sort((a,b)=>ROLE_ORDER.indexOf(a.split(" · ")[0])-ROLE_ORDER.indexOf(b.split(" · ")[0]));
  else keys.sort();
  return keys.map(k=>[k,m.get(k)]);
}
function label(k){
  return k.replace(/^Agent · /,'<span class="rt-a">Agent</span> · ')
          .replace(/^Bridge · /,'<span class="rt-b">Models-bridge</span> · ')
          .replace(/^Product · /,'<span class="rt-p">Product</span> · ');
}
function renderView(v){
  document.getElementById("stage").innerHTML = '<p class="blurb">'+v.blurb+'</p>' +
    groupsFor(v).map(([k,cs]) =>
      '<section class="grp"><h2>'+label(k)+' <span class="cnt">('+cs.length+')</span></h2>'
      + '<div class="cards">'+cs.map(renderForView).join("")+'</div></section>').join("");
}
function setView(id){
  document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on",t.dataset.v===id));
  renderView(VIEWS.find(v=>v.id===id));
}
document.getElementById("tabs").innerHTML = VIEWS.map(v=>'<button class="tab" data-v="'+v.id+'">'+v.label+'</button>').join("");
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>setView(t.dataset.v));
setView("family");
"""


def build_views_page(entries: list[Entry]) -> str:
    stars = {os.path.normpath(r["path"]) for fam in parse_census() for r in fam["rows"] if r["star"]}
    cards = []
    for e in entries:
        d = e.as_dict()
        cards.append({
            "title": d["title"], "html": _md_link_rewrite(e.path),
            "role": d["role"], "family": d["family"], "form": d["form"],
            "enforcement": d["enforcement"],
            "summary": d["summary"], "star": e.path in stars,
        })
    head = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>Governance catalogue — codegen'd views</title>\n{FONTS_LINK}\n"
            f"<style>{VIEWS_CSS}{FONT_CSS}</style>\n</head>\n<body>\n")
    body = ("<h1>Governance catalogue — codegen'd views</h1>\n"
            f'<p class="sub">The same {len(entries)} mechanisms, re-grouped live from card metadata. Every card is emitted by '
            '<code>renderForView(card)</code>; a view is just a grouping key + order, so <b>adding a mechanism or a '
            'view is data, not layout</b>. Click a card for its writeup; hover for its one-line summary. '
            '&nbsp;·&nbsp; <a href="catalogue-figure.html">the governance map</a> '
            '&nbsp;·&nbsp; <a href="index.html">catalogue</a></p>\n'
            '<div id="tabs"></div>\n<div id="stage"></div>\n')
    script = "<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n" + VIEWS_JS + "</script>\n"
    return head + "<main>\n" + body + script + _site_footer("") + "\n</main>\n</body>\n</html>\n"


def build_abstractions_body(md: str, abbrs: dict) -> str:
    """Render ABSTRACTIONS.md with an id-anchored <section> per entry (so `#slug` targets resolve)."""
    head, *blocks = re.split(r"^## ", md, flags=re.M)
    out = [render_md(head)]
    for block in blocks:
        m = re.search(r"<!-- slug: (\S+) -->", block)
        slug = m.group(1) if m else ""
        # keep the '## Headword' heading; drop the slug comment; render the rest as normal markdown
        cleaned = re.sub(r"^<!-- slug: \S+ -->\s*$", "", block, flags=re.M)
        heading, _, rest = cleaned.partition("\n")
        body = (f'<h2>{_inline(heading.strip())} <code class="slug">[[{slug}]]</code></h2>\n'
                + render_md(rest))
        out.append(f'<section class="abbr-entry" id="{_attr(slug)}">{body}</section>')
    return "\n".join(out)


def _stats(entries: list[Entry]) -> dict[str, str]:
    """The single stat source. Derived numbers (computed from the catalogue) merged over the declared ones
    in `DECLARED_STATS` (facts not derivable from the entries, e.g. LOC). Every value a string, ready to
    drop into a `data-census` span. `_sync_figure_census` fills from this; `check_no_raw_stats` forbids a
    raw stat literal that bypasses it."""
    from collections import Counter
    rows = [r for fam in parse_census() for r in fam["rows"]]

    def enf(e: str) -> str:
        return "softhard" if "Soft·Hard" in e else ("soft" if e.strip().startswith("Soft") else "hard")

    split = Counter(enf(r["enf"]) for r in rows)
    by_role = Counter(e.role for e in entries)
    bridge_method = sum("trunk / method" in r["control"] for r in rows)  # models-bridge trunk rows carry the tag
    stats: dict[str, object] = {
        "controls": len(entries),
        "families": len({e.family for e in entries if e.family}),
        "roles": len({e.role for e in entries if e.role}),
        "enf_hard": split["hard"], "enf_soft": split["soft"], "enf_softhard": split["softhard"],
        # per-role + models-bridge trunk/models split — consumed by the markdown census tokens
        "agent": by_role.get("Agent", 0), "bridge": by_role.get("Bridge", 0),
        "product": by_role.get("Product", 0),
        "bridge_method": bridge_method, "bridge_models": by_role.get("Bridge", 0) - bridge_method,
    }
    stats.update(DECLARED_STATS)
    return {k: str(v) for k, v in stats.items()}


STAT_VOCAB = re.compile(r"\b\d[\d,]*\s*(?:KLOC|MLOC|controls|mechanisms|families|weeks?)\b")


def check_no_raw_stats(_entries: list[Entry]) -> list[str]:
    """Forbid a raw stat literal in the hand-authored figure that bypasses the `data-census` fill —
    the '280 KLOC' / '51 controls' class. A stat number MUST live in a `<span data-census="KEY">` so the
    single source (`_stats`) owns it. Prose numbers (N=8, WCAG 2.1) are outside the vocabulary."""
    problems: list[str] = []
    fig = os.path.join(ROOT, "catalogue-figure.html")
    if not os.path.isfile(fig):
        return problems
    txt = open(fig, encoding="utf-8").read()
    stripped = re.sub(r'(<span data-census="[^"]+">)[^<]*(</span>)', r"\g<1>\g<2>", txt)
    for m in STAT_VOCAB.finditer(stripped):
        line = stripped[:m.start()].count("\n") + 1
        problems.append(f"catalogue-figure.html:{line}: raw stat {m.group(0)!r} — wrap it in a "
                        '<span data-census="KEY"> so _stats owns it')
    return problems


def _sync_figure_census(entries: list[Entry]) -> None:
    """Fill `data-census` spans in the static figure pages from `_stats` (single source of truth =
    the catalogue + DECLARED_STATS), so a hand-authored figure can't drift (e.g. '51 controls' vs 53)."""
    counts = _stats(entries)
    for fig in ("catalogue-figure.html", "development-workflow.html"):
        path = os.path.join(ROOT, fig)
        if not os.path.isfile(path):
            continue
        txt = open(path, encoding="utf-8").read()
        for key, val in counts.items():
            txt = re.sub(rf'(<span data-census="{re.escape(key)}">)[^<]*(</span>)', rf"\g<1>{val}\g<2>", txt)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(txt)


# --- Markdown census tokens: the prose analogue of the figure's `data-census` spans. ---
# A hand-typed count in README/INDEX/CLAUDE/models-bridge drifts on every add (the '53 mechanisms' rot).
# A token `<!--census:KEY-->VALUE<!--/census-->` (an HTML comment, invisible on GitHub) is filled from
# `_stats` by the build precompiler, so the count is DERIVED, not maintained. `:word` fills the number-word.
_MD_CENSUS_FILES = ("README.md", "INDEX.md", "CLAUDE.md", os.path.join("models-bridge", "README.md"))
_CENSUS_TOKEN = re.compile(r"(<!--census:([a-z_]+)(:word|:Word)?-->)(.*?)(<!--/census-->)", re.DOTALL)
_NUM_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
              "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
              "nineteen", "twenty")


def _num2word(n: int) -> str:
    return _NUM_WORDS[n] if 0 <= n < len(_NUM_WORDS) else str(n)


def _census_token_value(counts: dict[str, str], key: str, mod: str | None) -> str | None:
    """The filled value for a `<!--census:KEY[:word|:Word]-->` token — digit, number-word, or Titlecased."""
    if key not in counts:
        return None
    if mod == ":word":
        return _num2word(int(counts[key]))
    if mod == ":Word":
        return _num2word(int(counts[key])).capitalize()
    return counts[key]


def _sync_markdown_census(entries: list[Entry]) -> None:
    """Fill `<!--census:KEY-->…<!--/census-->` tokens in the tracked prose from `_stats` — the markdown
    twin of `_sync_figure_census`, so a hand-typed mechanism count can't drift from the census."""
    counts = _stats(entries)

    def repl(m: "re.Match[str]") -> str:
        val = _census_token_value(counts, m.group(2), m.group(3))
        return m.group(0) if val is None else f"{m.group(1)}{val}{m.group(5)}"

    for rel in _MD_CENSUS_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        txt = open(path, encoding="utf-8").read()
        new = _CENSUS_TOKEN.sub(repl, txt)
        if new != txt:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)


def check_census_tokens(entries: list[Entry]) -> list[str]:
    """Every census token names a known key and carries the current census value (the build fills them;
    this asserts it stuck — so a stale hand-edit between builds is caught, and an unknown key is flagged)."""
    counts = _stats(entries)
    problems: list[str] = []
    for rel in _MD_CENSUS_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        txt = open(path, encoding="utf-8").read()
        for m in _CENSUS_TOKEN.finditer(txt):
            key, mod, val = m.group(2), m.group(3), m.group(4)
            want = _census_token_value(counts, key, mod)
            if want is None:
                problems.append(f"{rel}: census token unknown key {key!r}")
            elif val != want:
                problems.append(f"{rel}: census:{key} is {val!r}, census says {want!r} — run `catalog.py build`")
    # The README summary lives inside an HTML comment, so it can't hold a nested census token — assert its
    # mechanism count against the census directly (the one derived count a token can't reach).
    readme = os.path.join(ROOT, "README.md")
    if os.path.isfile(readme):
        head = open(readme, encoding="utf-8").read()[:600]
        m = re.search(r"<!--\s*summary:.*?\b(\d+)\s+across\b", head, re.DOTALL)
        if m and m.group(1) != counts["controls"]:
            problems.append(f"README.md: summary count {m.group(1)} != census {counts['controls']} — update the summary")
    return problems


# --- Adoption sequence: ONE source, TWO emitted forms (the quick-start dual-emit). ---
# The quick-start walks a reader through adopting the catalogue via paste-ready prompts. The prompt
# sequence is authored ONCE inside a `<!--adoption-source ... -->` block in `quick-start.md`; the build
# derives BOTH an Auto-mode block (one copy-paste code fence) AND an Interactive-mode section (per-step
# snippet + explanation + links) from it, so the two forms can never drift. This is the census-token
# pattern (a build-time markdown precompiler that rewrites tracked prose between sentinel markers) applied
# to a richer structure. The generated regions live between `<!--adoption-auto-->…<!--/adoption-auto-->`
# and `<!--adoption-interactive-->…<!--/adoption-interactive-->`.
_ADOPT_FILE = "quick-start.md"
_ADOPT_SRC_RE = re.compile(r"<!--adoption-source(.*?)-->", re.DOTALL)
_ADOPT_AUTO_RE = re.compile(r"(<!--adoption-auto-->)(.*?)(<!--/adoption-auto-->)", re.DOTALL)
_ADOPT_INT_RE = re.compile(r"(<!--adoption-interactive-->)(.*?)(<!--/adoption-interactive-->)", re.DOTALL)
_PATH_LABEL = {"A": "Path A", "B": "Path B", "both": "either path"}


def _parse_adoption_steps(src_body: str) -> list[dict]:
    """Parse the `<!--adoption-source-->` body into ordered step records.

    Steps are separated by a line of exactly `===`. Each step is `@KEY: value` fields, with `@PROMPT:`
    taking every remaining line of the step verbatim (so a prompt keeps its own line breaks). Everything
    before the FIRST `===` is the format-documentation preamble and is skipped."""
    steps: list[dict] = []
    parts = re.split(r"(?m)^===\s*$", src_body)
    for chunk in parts[1:]:  # drop the preamble (text before the first `===`)
        lines = chunk.splitlines()
        step: dict = {"title": "", "path": "both", "explain": "", "links": "", "prompt": ""}
        prompt_lines: list[str] = []
        in_prompt = False
        for ln in lines:
            if in_prompt:
                prompt_lines.append(ln)
                continue
            m = re.match(r"^\s*@(TITLE|PATH|EXPLAIN|LINKS|PROMPT):\s?(.*)$", ln)
            if not m:
                continue
            key, val = m.group(1).lower(), m.group(2)
            if key == "prompt":
                in_prompt = True
                if val.strip():
                    prompt_lines.append(val)
            else:
                step[key] = val.strip()
        step["prompt"] = "\n".join(prompt_lines).strip("\n")
        if step["title"] and step["prompt"]:
            steps.append(step)
    return steps


def _emit_adoption_auto(steps: list[dict]) -> str:
    """Auto mode: one fenced code block — every step's prompt, prefixed with a numbered header comment so a
    reader (and Claude) can see the sequence structure inside the single paste."""
    body: list[str] = ["Read this whole block, then work through the steps in order. For each step, propose",
                       "before you write, and wait for my approval.", ""]
    for i, s in enumerate(steps, 1):
        body.append(f"# Step {i} — {s['title']}  [{_PATH_LABEL.get(s['path'], s['path'])}]")
        body.append(s["prompt"])
        body.append("")
    fence = "```\n" + "\n".join(body).rstrip("\n") + "\n```"
    return fence


def _emit_adoption_interactive(steps: list[dict]) -> str:
    """Interactive mode: per-step heading + explanation + verbatim prompt fence + links. Plain markdown, so
    the existing renderer produces axe-clean HTML (headings, paragraphs, `<pre><code>`, link lists) — no
    custom widget, no JS."""
    out: list[str] = []
    for i, s in enumerate(steps, 1):
        tag = "" if s["path"] == "both" else f" *({_PATH_LABEL.get(s['path'], s['path'])})*"
        out.append(f"### Step {i} — {s['title']}{tag}")
        if s["explain"]:
            out.append("")
            out.append(s["explain"])
        out.append("")
        out.append("```\n" + s["prompt"] + "\n```")
        if s["links"]:
            out.append("")
            out.append(f"**Read more:** {s['links']}")
        out.append("")
    return "\n".join(out).rstrip("\n")


def _sync_adoption_sequence() -> None:
    """Fill the Auto-mode and Interactive-mode regions in `quick-start.md` from the single `adoption-source`
    block — the dual-emit. Idempotent: rewrites the tracked file only when a region's content changed."""
    path = os.path.join(ROOT, _ADOPT_FILE)
    if not os.path.isfile(path):
        return
    txt = open(path, encoding="utf-8").read()
    m = _ADOPT_SRC_RE.search(txt)
    if not m:
        return
    steps = _parse_adoption_steps(m.group(1))
    if not steps:
        return
    auto = _emit_adoption_auto(steps)
    inter = _emit_adoption_interactive(steps)
    new = _ADOPT_AUTO_RE.sub(lambda mm: f"{mm.group(1)}\n{auto}\n{mm.group(3)}", txt)
    new = _ADOPT_INT_RE.sub(lambda mm: f"{mm.group(1)}\n{inter}\n{mm.group(3)}", new)
    if new != txt:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)


def check_adoption_sequence() -> list[str]:
    """Assert the two generated regions carry the current dual-emit (the build fills them; this catches a
    stale hand-edit between builds, or a source edit that wasn't rebuilt) — twin of `check_census_tokens`."""
    path = os.path.join(ROOT, _ADOPT_FILE)
    if not os.path.isfile(path):
        return []
    txt = open(path, encoding="utf-8").read()
    m = _ADOPT_SRC_RE.search(txt)
    if not m:
        return [f"{_ADOPT_FILE}: no <!--adoption-source--> block found"]
    steps = _parse_adoption_steps(m.group(1))
    if not steps:
        return [f"{_ADOPT_FILE}: adoption-source parsed to zero steps"]
    problems: list[str] = []
    am = _ADOPT_AUTO_RE.search(txt)
    im = _ADOPT_INT_RE.search(txt)
    if not am:
        problems.append(f"{_ADOPT_FILE}: no <!--adoption-auto--> region")
    elif am.group(2).strip() != _emit_adoption_auto(steps).strip():
        problems.append(f"{_ADOPT_FILE}: Auto-mode region stale — run `catalog.py build`")
    if not im:
        problems.append(f"{_ADOPT_FILE}: no <!--adoption-interactive--> region")
    elif im.group(2).strip() != _emit_adoption_interactive(steps).strip():
        problems.append(f"{_ADOPT_FILE}: Interactive-mode region stale — run `catalog.py build`")
    return problems


def check_orphan_pages() -> list[str]:
    """Post-build reachability gate: every built `.html` must have at least one inbound `href`/`src` from
    another built page. A page nothing links to is an orphan — rendered but unreachable (the DEVELOP.html
    class: a page whose `.md` was NOSERVE'd or never linked, left stranded on the site). The root landing
    `index.html` is the entry point and is exempt. Static scan only: entry pages get their inbound links
    from `index.html`'s census (`<a href>`), so JS-built links (`catalogue-views`) need not be followed.
    The gitignored skill bundle (`plugin/`) and the serve dir (`site/`) are out of scope."""
    pages: list[str] = []
    prune = site_prune_dirs()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in prune]
        for fn in filenames:
            if fn.endswith(".html"):
                pages.append(os.path.join(dirpath, fn))
    referenced: set[str] = set()
    ref_re = re.compile(r'(?:href|src)="([^"#]+\.html)(?:#[^"]*)?"')
    for p in pages:
        base = os.path.dirname(p)
        for m in ref_re.finditer(open(p, encoding="utf-8").read()):
            tgt = m.group(1)
            if tgt.startswith(("http://", "https://")):
                continue
            referenced.add(os.path.normpath(os.path.join(base, tgt)))
    root_index = os.path.normpath(os.path.join(ROOT, "index.html"))
    orphans = [os.path.relpath(p, ROOT) for p in pages
               if os.path.normpath(p) != root_index and os.path.normpath(p) not in referenced]
    return sorted(orphans)


def cmd_build(_args) -> int:
    global _ABBR_MAP, _ABBR_PREFIX
    entries = all_entries()
    _sync_figure_census(entries)  # keep the static figures' counts equal to the census
    _sync_markdown_census(entries)  # keep the prose census tokens equal to the census (README/INDEX/CLAUDE/bridge)
    _sync_adoption_sequence()  # dual-emit: fill quick-start's Auto + Interactive regions from the one source block
    _ABBR_MAP = parse_abstractions()
    written = 0
    md_files = sorted(catalogue_md_files())
    by_path = {e.path: e for e in entries}
    for f in md_files:
        rel = os.path.relpath(f, ROOT)
        depth = rel.count(os.sep)
        rel_root = "../" * depth
        _ABBR_PREFIX = rel_root
        md = open(f, encoding="utf-8").read()
        e = by_path.get(rel)
        title = (re.search(r"^# (.+)$", md, re.M) or [None, rel])[1]
        if rel == ABBR_SRC:  # the glossary — id-anchored sections so `#slug` targets resolve
            body = build_abstractions_body(md, _ABBR_MAP)
            html = _page(title, _crumb(rel_root, [(title, "")]), body, rel_root=rel_root)
        elif e:  # a control entry
            seg0 = rel.split(os.sep)[0]
            trail = [(ROLE_DISPLAY.get(seg0, e.role or ""), f"{rel_root}{seg0}/README.html"),
                     (e.family or "", ""), (e.title_only(), "")]  # family has no page → plain text
            body = render_md(md)
            html = _page(e.title_only(), _crumb(rel_root, trail), body, subtitle=e.summary, rel_root=rel_root)
        else:  # README / INDEX
            trail = []
            if depth >= 1:
                seg0 = rel.split(os.sep)[0]
                trail.append((ROLE_DISPLAY.get(seg0, seg0), f"{rel_root}{seg0}/README.html" if depth == 2 else ""))
            if os.path.basename(rel) != "README.md" or depth == 0:
                trail.append((title, ""))
            body = render_md(md)
            html = _page(title, _crumb(rel_root, trail), body, rel_root=rel_root)
        out_path = f[:-3] + ".html"
        open(out_path, "w", encoding="utf-8").write(html)
        written += 1
    # landing index.html = intro + census (overwrites the hand-authored placeholder)
    # Figures splice as bare responsive <svg>. A figure that appears twice (a card's summary thumbnail
    # and its expanded body) gets its internal ids namespaced per placement via _ns_svg_ids, so the two
    # copies — and any asset reused across cards — never collide (check_no_duplicate_ids).
    _mage = _inline_svg("assets/mage-overview.svg")
    _oversight = _inline_svg("assets/oversight-modes.svg")
    _dochier = _inline_svg("assets/documentation-hierarchy.svg")
    _ctrlarch = _inline_svg("assets/control-vs-architecture.svg")
    landing_body = NAV_GRID + "\n" + LANDING_INTRO.format(
        n=len(entries), book_title_block=_book_title_block(), pdf_href=_PDF_HREF, flow=_landing_flow(), cards=_landing_cards(),
        schools=_landing_schools(), ways=_landing_ways(),
        definitions=_landing_definitions(), outcomes=_landing_outcomes(),
        hero=_ns_svg_ids(_mage, "hero"),
        schools_fig=_ns_svg_ids(_oversight, "midway-fig"),
        schools_fig_th=_ns_svg_ids(_oversight, "midway-th"),
        model_fig=_ns_svg_ids(_dochier, "modeling-fig"),
        model_fig_th=_ns_svg_ids(_dochier, "modeling-th"),
        mech_fig=_ns_svg_ids(_ctrlarch, "alignment-fig"),
        mech_fig_th=_ns_svg_ids(_ctrlarch, "alignment-th"),
    ) + "\n" + build_census(entries)
    landing = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
               f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
               f"<title>Agent Governance Mechanisms</title>\n{FONTS_LINK}\n"
               f"<style>{PAGE_CSS}{LANDING_CSS}{FONT_CSS}</style>\n{LANDING_HEAD_SCRIPT}</head>\n"
               f'<body class="landing">\n<main>\n{landing_body}\n{_site_footer("")}\n</main>\n</body>\n</html>\n')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(landing)
    open(os.path.join(ROOT, "catalogue-views.html"), "w", encoding="utf-8").write(build_views_page(entries))
    print(f"built {written} entry/index pages + landing index.html + catalogue-views.html "
          f"({len(entries)} mechanisms in census)")
    # Regenerate the packaged skill bundle from the same sources — same "can't drift" discipline as the
    # HTML. build is the one regeneration point (pre-commit hook, deploy, and CI all call it), so this
    # single wire-in keeps plugin/ fresh. Subprocess avoids a catalog <-> bundle_skill circular import.
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "bundle_skill.py")], cwd=ROOT).returncode
    if rc != 0:
        print(f"WARNING: skill bundle regeneration failed (rc={rc}) — plugin/ may be stale", file=sys.stderr)
    # Build the WIP book HTML as part of the same pipeline (so `deploy github` publishes it too). Its
    # standalone renderer generates the chapters + a GoF-format appendix projected from the catalogue
    # entries. Subprocess keeps `catalog.py` stdlib-only and avoids importing the book builder. The book
    # pages are subject to the reachability gate below — the landing links the book index; the book's own
    # pages link each other — so the book must build BEFORE the gate runs.
    book_builder = os.path.join(ROOT, "book", "build_book_html.py")
    if os.path.isfile(book_builder):
        rc_book = subprocess.run([sys.executable, book_builder], cwd=os.path.join(ROOT, "book")).returncode
        if rc_book != 0:
            print(f"ABORT: book build failed (rc={rc_book}).", file=sys.stderr)
            return 1
    # Reachability gate (BLOCKING): a built page nothing links to is an orphan — fail the build so it can't
    # be committed (pre-commit `_catalog("build")`) or deployed. This is the DEVELOP.html class as a control.
    orphans = check_orphan_pages()
    if orphans:
        print(f"ORPHAN PAGES ({len(orphans)}) — rendered but nothing links to them:", file=sys.stderr)
        for o in orphans:
            print(f"  - {o}", file=sys.stderr)
        print("  Fix: link the page from the site, or add its `.md` to NOSERVE and `git rm` the `.html`.",
              file=sys.stderr)
        return 1
    return 0


def cmd_install_hooks(_args) -> int:
    """Point git at the tracked hooks/ dir: pre-commit runs validate+build+stage on every commit, and
    pre-push runs the full test suite (the CI gate) on every push."""
    r = subprocess.run(["git", "config", "core.hooksPath", "hooks"], cwd=ROOT)
    if r.returncode == 0:
        print("core.hooksPath → hooks (pre-commit: validate + build + stage HTML; "
              "pre-push: catalog_tests.py --full, the CI gate)")
    return r.returncode


DEFAULT_PORT = 8137  # deliberately not 8080/8000 (common collisions)


def _git(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, text=True,
                          capture_output=capture)


def cmd_data_claims(args) -> int:
    """Print each governed data-claim (book/data/data-claims.json) with its status, flagging the
    preliminary/partial ones — so "which claims are preliminary?" is a query, not a grep. `--json` dumps
    the raw manifest entries."""
    path = os.path.join(ROOT, "book", "data", "data-claims.json")
    if not os.path.isfile(path):
        print("no book/data/data-claims.json")
        return 0
    raw = json.load(open(path, encoding="utf-8"))
    claims = {k: v for k, v in raw.items() if not k.startswith("_")}
    if args.json:
        print(json.dumps(claims, ensure_ascii=False, indent=2))
        return 0
    prelim = 0
    for slug in sorted(claims):
        e = claims[slug]
        status = e.get("status", "?")
        flag = "  ⚠ PRELIMINARY" if status in ("preliminary", "partial") else ""
        if flag:
            prelim += 1
        src = e.get("source", "?")
        anchor = e.get("anchor", "")
        loc = f"{src}.html" + (f"#{anchor}" if anchor else "")
        print(f"{slug:16} [{status:11}]{flag}")
        print(f"                 -> {loc}")
        if e.get("gloss"):
            print(f"                 {e['gloss']}")
    print(f"— {len(claims)} claim(s), {prelim} preliminary/partial")
    return 0


def cmd_concepts(args) -> int:
    """Print each modeled concept (book/data/concepts.json) with its kind, status, and site realization,
    flagging drift (a site-eligible `both` concept with a MISSING/N-A card) and book-expands-site-missing
    gaps — so "which concepts drift from the book to the site?" is a query, not a grep. `book_home` and
    `name` are DERIVED, not stored, so they are not shown here (query the built index / registry for them).
    `--json` dumps the raw sidecar records."""
    path = os.path.join(ROOT, "book", "data", "concepts.json")
    if not os.path.isfile(path):
        print("no book/data/concepts.json")
        return 0
    raw = json.load(open(path, encoding="utf-8"))
    records = {k: v for k, v in raw.items() if not k.startswith("_")}
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    _site_eligible = {"thesis", "axis", "family"}
    drift = gaps = 0
    for slug in sorted(records):
        e = records[slug]
        kind = e.get("kind", "?")
        status = e.get("status", "?")
        site = e.get("site_home", "?")
        flag = ""
        if kind in _site_eligible and status == "both" and not str(site).startswith("card-"):
            flag = "  ⚠ DRIFT (both but no card)"
            drift += 1
        elif status == "book-expands-site-missing":
            flag = "  ⚠ book-expands-site-missing"
            gaps += 1
        print(f"{slug:34} [{kind:15}] [{status:26}]{flag}")
        print(f"                                   site -> {site}")
        if e.get("note"):
            print(f"                                   {e['note']}")
    print(f"— {len(records)} concept(s), {drift} drift, {gaps} book-expands-site-missing gap(s)")
    return 0


def cmd_definitions(args) -> int:
    """Print each modeled definition (book/data/definitions.json) with its site realization and its OWED
    book home — so "which definitions are on the site, and where do they land in the book?" is a query,
    not a grep. The four core-term definitions are a projection of this model onto the landing. `--json`
    dumps the raw records."""
    raw = _load_json_or_none(os.path.join(ROOT, "book", "data", "definitions.json"))
    if raw is None:
        print("no book/data/definitions.json")
        return 0
    records = {k: v for k, v in raw.items() if not k.startswith("_")}
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    owed = 0
    for slug in raw.get("_order", list(records)):
        e = records.get(slug)
        if not e:
            continue
        home = e.get("book_home_owed", {}) or {}
        status = home.get("status", "owed")
        flag = "  ⚠ BOOK HOME OWED" if status != "landed" else ""
        if status != "landed":
            owed += 1
        print(f"{e.get('term', slug):24} [site: {e.get('site_home', '?')}]{flag}")
        print(f"                         book home -> {home.get('section', '?')} [{status}]")
    print(f"— {len(records)} definition(s), {owed} with an owed book home")
    return 0


def cmd_outcomes_site(args) -> int:
    """Print the site's learning-outcomes SELECTION (book/data/outcomes-site.json) resolved against the
    outcomes model (book-models/outcomes.json) — so "which outcomes does the site surface?" is a query,
    not a grep. Shows each projected outcome's unit + bloom + statement, read from the model. `--json`
    dumps the resolved selection."""
    site = _load_json_or_none(os.path.join(ROOT, "book", "data", "outcomes-site.json"))
    model = _load_json_or_none(os.path.join(ROOT, "book-models", "outcomes.json"))
    if site is None or model is None:
        print("no outcomes-site.json / outcomes.json")
        return 0
    by_id = {o["outcome_id"]: o for o in model.get("outcomes", []) if o.get("outcome_id")}
    resolved = [by_id[oid] for oid in site.get("projected", []) if oid in by_id]
    if args.json:
        print(json.dumps(resolved, ensure_ascii=False, indent=2))
        return 0
    for o in resolved:
        unit = "book" if o.get("granularity") == "book" else o.get("primary_unit", "?")
        print(f"[{unit:8}] [{o.get('bloom', '?'):10}] {o.get('statement', '')}")
    dangling = [oid for oid in site.get("projected", []) if oid not in by_id]
    print(f"— {len(resolved)} projected outcome(s)" +
          (f", {len(dangling)} DANGLING (not in model)" if dangling else ""))
    return 0


def _load_json_or_none(path: str):
    return json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else None


# ── Deploy staging manifest ──────────────────────────────────────────────────
# `deploy github` stages an EXPLICIT set of paths — never `git add -A`, which sweeps any
# stray untracked file (a screenshot helper, a scratch `.mjs`) into a publish commit. Two
# gated moves: (1) every tracked modification/deletion via `git add -u`, which by definition
# never stages an untracked file; (2) NEW publishable content under the content roots, matched
# by extension so a scratch file of an unexpected type is left alone. Anything still untracked
# is reported, not committed — explicit, not implicit.
_PUBLISHABLE_EXTS = ("md", "html", "svg", "css", "js", "json",
                     "png", "jpg", "jpeg", "gif", "webp", "ico", "woff", "woff2", "ttf")
_CONTENT_ROOTS = ("agent", "models-bridge", "product", "book", "plugin", "assets")


def _is_publishable(path: str) -> bool:
    """True if a repo-relative path is NEW content the deploy should stage: a publishable
    file type under one of the content roots. Scratch of an unexpected type (a `.mjs`
    helper, a `.log`) fails this and is left for the human to add explicitly."""
    root = path.split("/", 1)[0]
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return root in _CONTENT_ROOTS and ext in _PUBLISHABLE_EXTS


def cmd_views_audit(args) -> int:
    """The book-models DRIFT AUDIT — the fast pre-commit entry point over the typed 4+1 view-models
    (`book-models/`). Runs the two MECHANICAL kinds of drift the book's own two-kind split calls a lint
    (book part 5 §"the substrate that keeps the models honest"):

      - STRUCTURAL — every view->md reference re-resolves against the CURRENT source. A section id /
        chapter / part / concept / label a view points at must still exist; a dangling reference reddens.
        The reverse index (`book-models/reverse_index.py`) makes this one walk over the inverted edges.
      - FRESHNESS — re-derive each view artifact (outline.json, outcomes.json, reverse_index.json) from
        source and diff against the committed file. A stale artifact (source edited, artifact not
        regenerated) is a finding.

    (The THIRD, SEMANTIC kind — does a paragraph's prose still deliver the point it claims? — is NOT
    mechanical, so it is a review-gate agent audit, not this lint. See book-models/DESIGN.md §8.)

    LANDS AUDIT-ONLY-FIRST (the repo's blocking-lint landing discipline): it PRINTS findings and exits 0,
    so it never reddens an in-flight commit. `--strict` exits 1 on any finding — the flip a follow-up wires
    into the hook once the seed findings are drained. Sub-second on this book (the IR parse is fast)."""
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    # Import the view-models lazily (they carry their own book_ir path setup); keep catalog.py import-cheap.
    import outcomes_model as ocm  # noqa: E402
    import outline_model as om  # noqa: E402
    import reverse_index as ri  # noqa: E402

    findings: list[str] = []

    # --- FRESHNESS: each materialized artifact must equal a fresh derivation. -------------------------
    freshness = [
        ("outline.json", om.load_artifact(), om.to_jsonable(om.derive_outline()),
         ("chapters", "_counts")),
        ("outcomes.json", ocm.load_artifact(), ocm.to_jsonable(ocm.derive_model()),
         ("outcomes", "_counts")),
        ("reverse_index.json", ri.load_artifact(), ri.to_jsonable(), ("index", "_counts")),
    ]
    for name, stored, fresh, keys in freshness:
        if stored is None:
            findings.append(f"FRESHNESS {name} missing — regenerate the view artifact")
        elif any(stored.get(k) != fresh[k] for k in keys):
            findings.append(f"FRESHNESS {name} is STALE — source changed but the artifact was not "
                            f"regenerated (`python3 book-models/{name.replace('.json', '_model.py' if name != 'reverse_index.json' else '.py')} regenerate`)")

    # --- STRUCTURAL: every view->md reference resolves against the current source. --------------------
    findings.extend(ri.structural_findings())

    # --- Also surface the view-models' own invariant walks (outline O2-O4, outcomes U1-U7) so the audit
    # is the ONE place a committer sees every mechanical view finding. These are audit-only too.
    findings.extend(om.invariant_findings(om.derive_outline()))
    findings.extend(ocm.coverage_findings(ocm.derive_model()))

    # --- SITE-AS-PROJECTION drift: the site is a derived VIEW of the book's models, so its projection
    # drift (definitions.json ↔ the landing's def-* cards; outcomes.json/selection ↔ the outcome-* rows)
    # belongs in the same views-audit surface. See book-models/SITE-VIEW.md; checks in tests/html.py.
    from tests.html import check_definitions_site, check_outcomes_site  # noqa: E402 — audit-time only
    for _label, (_status, _issues) in (("definitions", check_definitions_site()),
                                       ("outcomes-site", check_outcomes_site())):
        findings.extend(_issues)

    strict = getattr(args, "strict", False)
    mode = "STRICT (exit 1 on any finding)" if strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== book-models views-audit — structural + freshness drift over 3 view artifacts [{mode}] ==")
    if not findings:
        print("  clean — every view reference resolves, every artifact is fresh, invariants hold")
        return 0
    print(f"  {len(findings)} finding(s):")
    for f in findings:
        print(f"    {f}")
    return 1 if strict else 0


def _stage_deploy_manifest() -> None:
    """Stage the explicit deploy manifest (see comment above). Never `git add -A`."""
    _git("add", "-u")  # all tracked modifications + deletions; never stages an untracked file
    # NEW files: only untracked-and-not-ignored ones (ls-files honors .gitignore), and only
    # publishable content under the content roots. Everything else is reported, not committed.
    others = [p for p in _git("ls-files", "--others", "--exclude-standard",
                              capture=True).stdout.splitlines() if p]
    to_add = [p for p in others if _is_publishable(p)]
    if to_add:
        _git("add", "--", *to_add)
    skipped = [p for p in others if p not in to_add]
    if skipped:
        print("  NOTE: untracked files left UNSTAGED (not published) — `git add` them explicitly if intended:")
        for p in skipped:
            print(f"    {p}")


def cmd_deploy(args) -> int:
    """Build the site, then serve it locally (--local) or publish it to GitHub (--github)."""
    want_pdf = getattr(args, "pdf", False) and args.target == "local"
    print(f"== Deploy plan: target={args.target} ==")
    print("  1. validate   2. build   3. test (BLOCKING — aborts on any failure)   "
          + ("3b. render PDF   " if want_pdf else "")
          + ("4. serve on localhost" if args.target == "local"
             else "4. commit + push to origin main (CI deploys)"))
    if getattr(args, "pdf", False) and args.target == "github":
        # The Pages workflow ALWAYS renders + publishes the PDF on push, so --pdf is redundant here.
        print("  (note: --pdf is a no-op for github — the Pages workflow always renders the PDF on push)")
    if cmd_validate(None) != 0:
        print("ABORT: schema invalid — fix before deploying.")
        return 1
    if cmd_build(None) != 0:
        print("ABORT: build failed (orphan pages / bundle) — fix before deploying.")
        return 1
    # predeploy gate — BLOCKING (the suite is green as of the a11y remediation): abort the deploy if any
    # check fails. Tier-2 (axe/claude) SKIPs when the tool is absent, so a browser-less env won't block.
    if subprocess.run([sys.executable, "catalog_tests.py"], cwd=ROOT).returncode != 0:
        print("ABORT: test suite failed — fix before deploying (run `catalog.py test` to see).")
        return 1

    # opt-in local PDF render (slow Paged.js + Puppeteer path; the default web build never touches it).
    # `--pdf` regenerates book/mage-book.pdf so the local preview's "Download PDF" link serves the CURRENT
    # book, not a stale gitignored copy. Publish (github) needs no flag — CI renders the PDF on every push.
    if want_pdf:
        print("\n== Rendering PDF (book/mage-book.pdf) — slow; content-integrity gate runs internally ==")
        pdf_build = subprocess.run([sys.executable, os.path.join("book", "build_book_html.py"), "--pdf"],
                                   cwd=ROOT)
        if pdf_build.returncode != 0:
            print("ABORT: PDF render failed (see build_book_html.py --pdf output above).")
            return 1

    if args.target == "local":
        url = f"http://127.0.0.1:{args.port}/"
        print(f"\n== Serving {url}  (Ctrl-C to stop) ==")
        try:
            subprocess.run([sys.executable, "-m", "http.server", str(args.port),
                            "--bind", "127.0.0.1"], cwd=ROOT)
        except KeyboardInterrupt:
            print("\nstopped.")
        return 0

    # --github: stage the EXPLICIT manifest (never `git add -A`), commit, push.
    _stage_deploy_manifest()
    staged = _git("diff", "--cached", "--name-only", capture=True).stdout.strip()
    if staged:
        cp = _git("commit", "-m", args.message)
        if cp.returncode:
            print("ABORT: commit failed (see hook output above).")
            return cp.returncode
    else:
        print("  (nothing staged to commit — pushing current HEAD)")
    if _git("push", "origin", "main").returncode:
        print("ABORT: push failed.")
        return 1
    head = _git("rev-parse", "--short", "HEAD", capture=True).stdout.strip()
    print(f"\n== Pushed {head} to origin/main. GitHub Actions will build + deploy Pages. ==")
    print("   Watch: https://github.com/davisjam/agent-governance-mechanisms/actions")
    return 0


def cmd_test(args) -> int:
    """Build, then run the tiered catalogue + skill test suite (see catalog_tests.py)."""
    cmd_build(None)
    cmd = [sys.executable, "catalog_tests.py"] + (["--strict"] if getattr(args, "strict", False) else [])
    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_check_responsive(_args) -> int:
    """Deploy-blocking responsive-layout gate: build the site, then drive headless Chrome to assert
    the landing `.masonry` region renders a structurally DIFFERENT layout at wide vs phone width
    (>= 3 columns wide, exactly 1 column on a phone) — the author's success metric made mechanical.

    This is NOT part of `validate` (which is stdlib-only, clone-and-run, no browser dep). Like the PDF
    density/mermaid gates it is a non-stdlib deploy-time check that needs a browser, so the measurement
    lives in `book/check_responsive.mjs` and reuses the book/ Puppeteer dep (install via `npm ci` in
    book/). Exit 0 = PASS (prints wide/phone column counts); exit non-zero = FAIL."""
    cmd_build(None)
    index_html = os.path.join(ROOT, "index.html")
    if not os.path.exists(index_html):
        print(f"ERROR: {index_html} missing after build", file=sys.stderr)
        return 1
    script = os.path.join(ROOT, "book", "check_responsive.mjs")
    if not os.path.exists(script):
        print(f"ERROR: responsive-check script missing: {script}", file=sys.stderr)
        return 1
    return subprocess.run(["node", script, index_html], cwd=ROOT).returncode


def _served_html_pages() -> list[str]:
    """Every built page that is part of the served site — the SAME walk axe/html-validate use
    (`tests.common.html_files`): walk from ROOT, pruning the non-site + gitignored dirs (the plugin
    bundle, node_modules, serve dirs, `_drafts/`). Returned as absolute paths, sorted for stable output."""
    prune = site_prune_dirs()
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in prune]
        out.extend(os.path.abspath(os.path.join(dirpath, fn))
                   for fn in filenames if fn.endswith(".html"))
    return sorted(out)


def cmd_check_console(_args) -> int:
    """Deploy-blocking console-error gate: build the site, then drive headless Chrome to load EVERY
    served HTML page and assert none produces a `pageerror` (uncaught exception / unhandled rejection)
    or a `console` message of type `error`. Catches script-ordering races (e.g. an iframe `onload`
    firing before its handler is defined → "foo is not defined"), failed fetches logged as errors, and
    missing subresources — none of which the stdlib `validate` gate or axe/html-validate can see.

    Like check-responsive it needs a browser, so the measurement lives in `book/check_console.mjs` and
    reuses the book/ Puppeteer dep. This command enumerates the served pages (same site-walk as axe) and
    passes them as argv. Exit 0 = PASS (no page errored); exit non-zero = FAIL (lists every page+error)."""
    cmd_build(None)
    script = os.path.join(ROOT, "book", "check_console.mjs")
    if not os.path.exists(script):
        print(f"ERROR: console-check script missing: {script}", file=sys.stderr)
        return 1
    pages = _served_html_pages()
    if not pages:
        print("ERROR: no served HTML pages found after build", file=sys.stderr)
        return 1
    print(f"check-console: loading {len(pages)} served page(s) in headless Chrome...")
    return subprocess.run(["node", script, *pages], cwd=ROOT).returncode


def main() -> int:
    p = argparse.ArgumentParser(description="Validate + query the governance-catalogue schema.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="schema + INDEX + link + summary checks; exit 1 on any violation")
    q = sub.add_parser("query", help="filter/list entries")
    q.add_argument("--role", help="Agent | Bridge | Product")
    q.add_argument("--family")
    q.add_argument("--form", help="one of the nine forms")
    q.add_argument("--move", help="constraint | sensor | package")
    q.add_argument("--model", help="is-a-model | governs-a-model | —")
    q.add_argument("--enf", help="Hard | Soft | Soft·Hard")
    q.add_argument("--json", action="store_true")
    s = sub.add_parser("summaries", help="dump role/family/entry summaries (tooltip source)")
    s.add_argument("--json", action="store_true")
    sub.add_parser("build", help="render every .md → .html + regenerate the landing census")
    tp = sub.add_parser("test", help="build, then run the catalogue + skill test suite (markdown/html/skill; axe + claude validate)")
    tp.add_argument("--strict", action="store_true", help="treat a Tier-2 SKIP (missing axe/claude) as failure")
    sub.add_parser("check-responsive", help="deploy-blocking gate: assert the landing masonry tiles into >=3 columns at wide width and 1 column at phone width (headless Chrome; needs book/ Puppeteer)")
    sub.add_parser("check-console", help="deploy-blocking gate: load EVERY served HTML page in headless Chrome and fail on any pageerror / console.error (headless Chrome; needs book/ Puppeteer)")
    dc = sub.add_parser("data-claims", help="list governed data-claims + their status; flag preliminary/partial ones")
    dc.add_argument("--json", action="store_true", help="dump the raw manifest entries")
    cp = sub.add_parser("concepts", help="list modeled concepts (book/data/concepts.json) + kind/status/site; flag book<->site drift")
    cp.add_argument("--json", action="store_true", help="dump the raw sidecar records")
    df = sub.add_parser("definitions", help="list modeled definitions (book/data/definitions.json) + their site realization + owed book home")
    df.add_argument("--json", action="store_true", help="dump the raw definition records")
    osub = sub.add_parser("outcomes-site", help="list the site's projected learning outcomes (book/data/outcomes-site.json resolved against outcomes.json)")
    osub.add_argument("--json", action="store_true", help="dump the resolved selection")
    va = sub.add_parser("views-audit", help="book-models drift audit: structural (every view->md reference resolves) + freshness (each view artifact equals a fresh derivation). Fast pre-commit gate; AUDIT-ONLY (prints, exits 0) unless --strict")
    va.add_argument("--strict", action="store_true", help="exit 1 on any finding (the flip a follow-up wires into the hook once seed findings are drained)")
    sub.add_parser("install-hooks", help="git config core.hooksPath hooks (auto-regen on commit)")
    d = sub.add_parser("deploy", help="build, then serve locally (local) or publish to GitHub (github)")
    d.add_argument("target", choices=["local", "github"], help="local = serve on localhost; github = commit + push (CI deploys)")
    d.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"localhost port for --local (default {DEFAULT_PORT})")
    d.add_argument("--pdf", action="store_true", help="(local only) also render book/mage-book.pdf so the local preview's Download-PDF link is current; slow. Redundant for github — CI always renders the PDF on push")
    d.add_argument("-m", "--message", default="deploy: rebuild site", help="commit message for github mode")
    args = p.parse_args()
    return {"validate": cmd_validate, "query": cmd_query, "summaries": cmd_summaries,
            "build": cmd_build, "test": cmd_test, "check-responsive": cmd_check_responsive,
            "check-console": cmd_check_console,
            "data-claims": cmd_data_claims, "concepts": cmd_concepts,
            "definitions": cmd_definitions, "outcomes-site": cmd_outcomes_site,
            "views-audit": cmd_views_audit,
            "install-hooks": cmd_install_hooks, "deploy": cmd_deploy}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
