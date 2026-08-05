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
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))

# Design-token SSOT projection — the CSS :root{--…} block and the web-font <link>, both derived from
# book-models/design-tokens.json by the stdlib-only projector. Inlined once per page (via FONT_CSS, which
# every page carries), so every literal in the style blocks resolves to a var(--…). Keeps clone-and-run:
# design_tokens.py is stdlib-only too.
sys.path.insert(0, os.path.join(ROOT, "book-models"))
import design_tokens as _dtokens  # noqa: E402 — the design-token projector (stdlib-only)

CSS_ROOT_BLOCK = _dtokens.css_root_block()
FONTS_LINK = _dtokens.google_fonts_link()

# Single source of truth for the book's cover identity (title/subtitle/kicker/author). Also read by
# book/build_book_html.py (print cover + web front page) — edit book/book-manifest.json once, all follow.
BOOK_MANIFEST = json.loads(open(os.path.join(ROOT, "book", "book-manifest.json"), encoding="utf-8").read())
_PDF_HREF = "book/" + BOOK_MANIFEST["pdf_filename"]  # root-relative href to the published PDF (single source: the manifest)

# Repo-metadata SSOT — owner/repo/URLs read once from book-models/repo-metadata.json (stdlib-read, the
# design-tokens.json pattern). The GitHub repo link in the chrome (footer, top nav, landing nav grid) and
# the deploy "watch the Actions run" line all resolve from HERE, so a repo rename touches one file, not four.
_REPO_META = json.loads(open(os.path.join(ROOT, "book-models", "repo-metadata.json"), encoding="utf-8").read())
_REPO_OWNER = _REPO_META["owner"]
_REPO_NAME = _REPO_META["repo"]
_REPO_URL = f"https://github.com/{_REPO_OWNER}/{_REPO_NAME}"          # <site>/<owner>/<repo>
_REPO_ACTIONS_URL = _REPO_META.get("actions_url", f"{_REPO_URL}/actions")
_SITE_URL = _REPO_META["site_url"]                                    # the author's Pages root


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
MOVE_ORDER = ["constraint", "sensor", "package"]        # Alignment-Thesis display order for the By-move view: prevent → detect → both (set == MOVE_CLASSES; parity checked in check_views_move)
MODEL_CLASSES = {"is-a-model", "governs-a-model", "—"}  # a typed model · gates/generates/queries one · neither
DERIVATION_CLASSES = {"model-from-code", "model-to-code", "both"}
# `Governs` is the join key: an optional trailing row on `governs-a-model` entries naming the model(s) it
# governs — either `all-models` (the whole zoo; the method trunk) or a ` · `-separated list of is-a-model
# entry slugs (file stems). Exact precedent: the `Derivation` row (optional, one Model class only, NOT
# mirrored in INDEX → zero INDEX churn). Referential integrity (each slug resolves) is a cross-entry check
# in `check_governs`; the per-row format check lives in Entry._parse.
GOVERNS_ALL = "all-models"
META_ORDER = ["Summary", "Target", "Form", "Move", "Model", "Enforcement"]  # + optional trailing Derivation|Governs
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

# ── The By-model node map (the "By model" view's grouping) ──
# The substrate audit's assignment of every entry to the organizing model it plugs into or serves. TWO
# organizing spines — the fleet's self-operate LIFECYCLE models and the product's 4+1 VIEWS — over one
# METHOD TRUNK, with the 43-mechanism perimeter grouped under the lifecycle/view each mechanism serves.
# Slugs are entry file stems. Per node: `models` = the is-a-model entries HOMED here; `cross` = a model
# shown here but homed on another node (a shared-by-projection cross-link, rendered dashed, never a second
# home); `perim` = the perimeter mechanisms filed under this node (for the trunk node, its method
# mechanisms). Every entry is a home exactly once — `check_model_map` fails the build otherwise, so the map
# can't silently fall out of sync when an entry is added. Presentation only: no files move, no prose changes.
FLEET_ANCHOR_SLUG = "lifecycle-model"  # the is-a-model that anchors the whole fleet spine (not one node)
MODEL_NODES = [
    {"k": "l1", "spine": "fleet", "title": "manage-agents",
     "sub": "Dispatch → registry → worktree isolation → the gate staircase → tombstone and clean.",
     "models": ["agent-orchestration-model", "concurrency-contracts"],
     "cross": ["required-config-per-role-manifest"],
     "perim": ["role-typed-dispatch", "brief-linting", "agent-registry", "tombstone-commits",
               "typed-event-bus", "caused-by-provenance"]},
    {"k": "l2", "spine": "fleet", "title": "manage-context",
     "sub": "Banking, compaction, and session-start reconstruction of the agent's working context.",
     "models": [], "cross": [],
     "perim": ["dynamic-context-injection", "docs-hierarchy", "lifecycle-hooks", "reflection-facet-substrate"]},
    {"k": "l3", "spine": "fleet", "title": "manage-git-repo",
     "sub": "Main as the deploy tip; cherry-pick and merge-train reachability; the commit gate.",
     "models": [], "cross": [],
     "perim": ["pre-commit-hook", "sentinel-first-commit", "merge-train-mis-batching"]},
    {"k": "l4", "spine": "fleet", "title": "manage-deploy",
     "sub": "The local → staging → prod staircase, its canaries, heartbeats, and topology.",
     "models": ["deployment-topology-model"], "cross": [],
     "perim": ["staged-deploy-gates", "deploy-heartbeats"]},
    {"k": "l5", "spine": "fleet", "title": "manage-dev-machine",
     "sub": "Host compute rationed across concurrent worktrees; the locks that keep them from colliding.",
     "models": ["synchronization-model"], "cross": [],
     "perim": ["test-serializer", "build-serializer", "aggregate-compute-protection", "resource-pressure-gating"]},
    {"k": "lcron", "spine": "fleet", "title": "gc-cron plane",
     "sub": "The periodic garbage-collection crons and their typed alert stream.",
     "models": [], "cross": [], "perim": ["cron-alerts-gate"]},
    {"k": "lorch", "spine": "fleet", "title": "orchestrator-hooks",
     "sub": "The orchestrator session's own hook machinery and the governance-document mechanisms.",
     "models": ["governance-graph"], "cross": [],
     "perim": ["claude-md-rule-index", "mandatory-snippet-table", "epic-definition-of-done",
               "doc-hygiene-lints", "operational-playbooks", "operator-runbook-skill",
               "epic-and-design-templates", "self-governance"]},
    {"k": "logical", "spine": "product", "title": "Logical",
     "sub": "The system's functional decomposition — including the product's own document models, which "
            "carry the artifact-side mechanisms.",
     "models": ["service-flow-model", "domain-registries", "pdf-model", "office-models", "canonical-walkers",
                "typed-contract-surfaces"],
     "cross": [],
     "perim": ["content-validator", "standards-rule-engine", "semantic-lints", "coherence-lints",
               "mutator-stamps", "derive-changelog", "a11y-prefix", "test-onion-tiers", "property-tests",
               "fuzz-campaigns", "ddt-pin-trailers", "typed-categories", "remediation-verbs",
               "codemod-first", "service-client", "raw-redis-seam"]},
    {"k": "process", "spine": "product", "title": "Process",
     "sub": "What runs at once and where it can collide.",
     "models": ["composed-state-machine-model", "process-view", "timeout-budget-ordering-model"],
     "cross": ["synchronization-model", "concurrency-contracts"], "perim": []},
    {"k": "dev", "spine": "product", "title": "Development",
     "sub": "How the codebase is zoned and layered.",
     "models": ["component-zone-model", "rule-metadata-registry"], "cross": [], "perim": []},
    {"k": "phys", "spine": "product", "title": "Physical",
     "sub": "Where things run and what depends on what.",
     "models": ["control-substrate-dependency", "data-flow-model", "required-config-per-role-manifest",
                "telemetry-collection-provenance"],
     "cross": ["deployment-topology-model"], "perim": []},
    {"k": "scen", "spine": "product", "title": "Scenarios",
     "sub": "The journeys that tie the views together.",
     "models": ["user-journey-model"], "cross": ["agent-orchestration-model"], "perim": []},
    {"k": "trunk", "spine": "trunk", "title": "The method trunk",
     "sub": "What holds ANY model true, regardless of subject — governs every model in both spines.",
     "models": ["symbol-anchored-traceability-graph"], "cross": [],
     "perim": ["executable-source-of-truth", "drift-parity-gates", "agent-first-mbse-harness",
               "formal-invariant-verification", "coverage-model-mapping", "query-surface",
               "meta-model-consumption", "model-driven-codegen", "model-graded-finding-severity",
               "invariant-dag-execution-policy", "semantic-level-enforcement",
               "journey-criticality-test-placement", "journey-task-closure", "f10-wiring-lint",
               "model-derived-test-obligation-census", "control-coverage-census"]},
]

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

        # Recognized metadata labels = the six required (META_ORDER) + one optional trailing row, which is
        # `Derivation` (is-a-model only) OR `Governs` (governs-a-model only) — never both (their Model
        # classes are disjoint).
        META_LABELS = META_ORDER + ["Derivation", "Governs"]
        rows = re.findall(r"^\| ([^|]+?) \| (.+?) \|$", t, re.M)
        self.meta = {k.strip(): v.strip() for k, v in rows if k.strip() in META_LABELS}
        labels = [k.strip() for k, _ in rows if k.strip() in META_LABELS]
        # The six required rows must appear in order; a single optional row (Derivation|Governs) may trail.
        if labels[:len(META_ORDER)] != META_ORDER or labels[len(META_ORDER):] not in ([], ["Derivation"], ["Governs"]):
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

        # Governs (optional): allowed ONLY on governs-a-model entries. The value leads with a ` · `-separated
        # list of backticked slugs (an is-a-model file stem, or the sentinel `all-models`), optionally
        # followed by ` — gloss`. Per-row format lives here; slug referential integrity is `check_governs`.
        self.governs: list[str] | None = None
        if "Governs" in self.meta:
            head = self.meta["Governs"].split(" — ", 1)[0]  # slugs precede the em-dash gloss
            self.governs = re.findall(r"`([a-z][a-z0-9-]*)`", head)
            if not self.governs:
                self.issues.append(f"Governs row has no backticked model slug(s): {self.meta['Governs']!r}")
            if self.model != "governs-a-model":
                self.issues.append("Governs row present but Model is not `governs-a-model` "
                                   "(Governs is only for governs-a-model entries)")
            if GOVERNS_ALL in self.governs and len(self.governs) != 1:
                self.issues.append(f"Governs `all-models` must stand alone, not mixed with slugs: "
                                   f"{self.governs}")

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

    @property
    def slug(self) -> str:
        """The entry's stable slug — its file stem (`service-flow-model`). The Governs join key resolves to
        these; the By-model node map groups by them."""
        return os.path.splitext(os.path.basename(self.path))[0]

    def as_dict(self) -> dict:
        return {
            "path": self.path, "role": self.role, "family": self.family,
            "form": self.form, "move": self.move, "model": self.model,
            "derivation": self.derivation, "governs": self.governs, "slug": self.slug,
            "enforcement": self.enf, "summary": self.summary,
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


def check_governs(entries: list[Entry]) -> list[str]:
    """Referential integrity for the `Governs` join key: every slug a governs-a-model entry names must be
    `all-models` or resolve to a real is-a-model entry. The reverse "Governed by" blocks are derived from
    exactly these edges, so a dangling slug would render a broken back-link — fail it at validate time."""
    model_slugs = {e.slug for e in entries if e.model == "is-a-model"}
    problems = []
    for e in entries:
        for slug in e.governs or []:
            if slug == GOVERNS_ALL:
                continue
            if slug not in model_slugs:
                problems.append(f"Governs slug `{slug}` in {e.path} resolves to no is-a-model entry")
    return problems


def check_model_map(entries: list[Entry]) -> list[str]:
    """Completeness of the By-model node map: every entry must be homed under exactly one node (as a model
    or a perimeter mechanism) or be the fleet anchor, every cross-link must resolve to a real home, and no
    homed slug may be a phantom. This makes the presentation grouping a checked projection over the entry
    set — add an entry without placing it and the build fails loudly (no silently-dropped mechanism)."""
    slugs = {e.slug for e in entries}
    homes: dict[str, str] = {}
    problems: list[str] = []

    def claim(slug: str, where: str) -> None:
        if slug in homes:
            problems.append(f"model-map: '{slug}' homed twice ({homes[slug]} + {where})")
        else:
            homes[slug] = where

    for n in MODEL_NODES:
        for s in n["models"]:
            claim(s, f"{n['k']}.model")
        for s in n["perim"]:
            claim(s, f"{n['k']}.perim")
    claim(FLEET_ANCHOR_SLUG, "fleet-anchor")
    for n in MODEL_NODES:
        for s in n["cross"]:
            if s not in homes:
                problems.append(f"model-map: cross-link '{s}' in {n['k']} homes on no node")
    for s in sorted(homes):
        if s not in slugs:
            problems.append(f"model-map: homed slug '{s}' ({homes[s]}) is not a real entry")
    for e in entries:
        if e.slug not in homes:
            problems.append(f"model-map: entry '{e.slug}' has no node home (place it in MODEL_NODES)")
    return problems


def check_views_move(entries: list[Entry]) -> list[str]:
    """Completeness/drift guard for the codegen'd 'By move' card-grid view — the sibling of check_model_map
    for the Alignment-Thesis Move axis. The axis is a closed set (MOVE_CLASSES) and the view groups every
    entry under it, so the build fails if: (a) MOVE_ORDER drifts from MOVE_CLASSES; (b) some Move class has
    no entry (an empty bucket / axis value uncovered); or (c) the VIEWS_JS 'move' view's declared bucket
    order drifts from MOVE_ORDER (a class added without teaching the view about it). This ties the JS view
    declaration to the Python source of truth, so the presentation grouping stays a checked projection over
    the closed axis — a new Move class can't silently rot the view."""
    problems: list[str] = []
    if set(MOVE_ORDER) != MOVE_CLASSES:
        problems.append(f"move-view: MOVE_ORDER {MOVE_ORDER} ≠ MOVE_CLASSES {sorted(MOVE_CLASSES)}")
    seen = {e.move for e in entries}
    for cls in MOVE_ORDER:
        if cls not in seen:
            problems.append(f"move-view: no entry carries Move `{cls}` — the '{cls}' bucket would render empty")
    m = re.search(r'id:"move",.*?order:\[([^\]]*)\]', VIEWS_JS, re.S)
    if not m:
        problems.append('move-view: no {id:"move", …, order:[…]} card-grid view found in VIEWS_JS')
    else:
        declared = re.findall(r'"([^"]+)"', m.group(1))
        if declared != MOVE_ORDER:
            problems.append(f"move-view: VIEWS_JS 'move' bucket order {declared} ≠ MOVE_ORDER {MOVE_ORDER}")
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


# The [gh:] marker regex — kept in sync with book/build_book_html.py:_GH_MARKER_RE. Simple enough that a
# 2nd copy is acceptable; importing build_book_html here would pull its heavier module-load (manifest reads).
_GH_MARKER_RE = re.compile(r"\[gh:\s*([^\]|]+?)\s*(?:\|[^\]]*?)?\]")


def check_gh_refs() -> list[str]:
    """Every `[gh:<repo-relative-path>]` in the book prose must resolve to a real file in the working tree.
    Deterministic + offline (no network) — a rotted source reference must fail the build, not ship a 404
    'view the source' link. Path-exists twin of the build-time resolver in book/build_book_html.py."""
    problems: list[str] = []
    for md in sorted(glob.glob(os.path.join(ROOT, "book", "**", "*.md"), recursive=True)):
        text = open(md, encoding="utf-8").read()
        for path in _GH_MARKER_RE.findall(text):
            path = path.strip()
            if not os.path.exists(os.path.join(ROOT, os.path.normpath(path))):
                rel = os.path.relpath(md, ROOT)
                problems.append(f"{rel}: [gh:{path}] -> no such file in the working tree")
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


def _landing_id_scan() -> "set[str] | None":
    """Every `id="…"` on the BUILT landing (index.html), or None when the site is not built yet. The
    id-set the model→site projection-drift join runs against."""
    idx = os.path.join(ROOT, "index.html")
    if not os.path.isfile(idx):
        return None
    return set(re.findall(r'\bid="([a-z0-9][a-z0-9-]*)"', open(idx, encoding="utf-8").read()))


def projection_drift(records: dict, landing_ids: "set[str] | None", id_of) -> "list[tuple[str, str]]":
    """The shared model→SITE projection-drift core (rule #11 second-site DRY — extracted from
    check_big_ideas + the definitions site check, which both projected a model file then asserted every
    record's id resolved on the built landing). Given a model's `records`, the set of ids on the built
    landing, and a per-record extractor `id_of(slug, rec) -> projected_id`, return the (slug, projected_id)
    pairs whose id is modeled but does NOT resolve on the landing — "modeled but not projected".
    `landing_ids is None` (site not built yet) returns [] so the join stays best-effort; each caller
    formats its own domain finding string."""
    if landing_ids is None:
        return []
    missing: list[tuple[str, str]] = []
    for slug, rec in records.items():
        pid = id_of(slug, rec)
        if pid and pid not in landing_ids:
            missing.append((slug, pid))
    return missing


def check_big_ideas() -> list[str]:
    """The BIG-IDEAS projection drift catch. book-models/landing-big-ideas.json is the model; the landing's
    Big-Ideas argument (index.html) is its projection. Mirrors the definitions drift check. Asserts:
      (a) BOOK HOME — `book_home` (minus any `#anchor`) resolves to a real chapter/page on disk (the
          "site is a preview; book coverage ⊇ site framings" rule made mechanical).
      (b) FIGURE — `figure` exists under book/assets/. Every asset's palette conformance is enforced
          separately + audit-only by the design-token drift lint, so a real asset is palette-governed;
          this check does not re-gate palette (it would redden validate on the existing audit-only drift).
      (c) WORD CAP — `claim` is within the model's declared `_word_cap`.
      (d) MODEL→SITE — when index.html is present, each SIX-idea record's `id` resolves to an id on the
          built landing (via the shared `projection_drift`). The `gateway` record is EXCLUDED: the landing
          closes on the conclusion + three ways-in buttons and no longer renders the F1-gateway band, so
          its id is intentionally not projected — the six ideas ARE.
    Returns a list of problem strings (empty = clean)."""
    path = os.path.join(ROOT, "book-models", "landing-big-ideas.json")
    if not os.path.isfile(path):
        return []
    raw = json.load(open(path, encoding="utf-8"))
    cap = raw.get("_word_cap", 26)
    recs = {k: v for k, v in raw.items() if not k.startswith("_")}
    problems: list[str] = []
    for slug in raw.get("_order", []):
        if slug not in recs:
            problems.append(f"_order references {slug!r} with no record")
    for slug, rec in recs.items():
        bh = (rec.get("book_home") or "").split("#")[0]
        if not bh or not os.path.exists(os.path.join(ROOT, bh)):
            problems.append(f"big-ideas: {slug!r} book_home {rec.get('book_home')!r} does not resolve "
                            f"to a real chapter/page on disk")
        fig = rec.get("figure", "")
        if not fig or not os.path.exists(os.path.join(ROOT, "book", "assets", fig)):
            problems.append(f"big-ideas: {slug!r} figure {fig!r} not found under book/assets/")
        n = len((rec.get("claim") or "").split())
        if n > cap:
            problems.append(f"big-ideas: {slug!r} claim is {n} words (cap {cap}): {rec.get('claim')!r}")
    # (d) MODEL→SITE via the shared helper — the six ideas only (gateway excluded, see docstring).
    projected = {k: v for k, v in recs.items() if k != "gateway"}
    for slug, rid in projection_drift(projected, _landing_id_scan(), lambda s, r: r.get("id", "")):
        problems.append(f"big-ideas: {slug!r} id {rid!r} does not resolve on the landing "
                        f"(index.html) — modeled but not projected (rebuild, or fix the renderer)")
    return problems


def _big_ideas_palette_audit() -> list[str]:
    """AUDIT-ONLY companion to check_big_ideas: which referenced figures carry a hex outside the SVG
    palette allow-list. Reported (never gated) so a committer sees palette state without reddening
    validate on pre-existing, audit-only design-token drift."""
    path = os.path.join(ROOT, "book-models", "landing-big-ideas.json")
    if not os.path.isfile(path):
        return []
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    try:
        import design_tokens as dtk  # noqa: E402 — palette source of truth
        palette = dtk.svg_palette()
    except Exception:
        return []
    raw = json.load(open(path, encoding="utf-8"))
    hex_re = re.compile(r'#[0-9a-fA-F]{3,8}\b')
    out: list[str] = []
    for slug, rec in ((k, v) for k, v in raw.items() if not k.startswith("_")):
        fp = os.path.join(ROOT, "book", "assets", rec.get("figure", ""))
        if not os.path.isfile(fp):
            continue
        bad = sorted({h.lower() for h in hex_re.findall(open(fp, encoding="utf-8").read())
                      if h.lower() not in palette})
        if bad:
            out.append(f"{rec.get('figure')}: {len(bad)} hex outside palette ({', '.join(bad[:4])}…)")
    return out


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
    for msg in check_governs(entries):
        print(f"  [governs] {msg}")
        n_issues += 1
    for msg in check_model_map(entries):
        print(f"  [modelmap] {msg}")
        n_issues += 1
    for msg in check_views_move(entries):
        print(f"  [moveview] {msg}")
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
    for msg in check_gh_refs():
        print(f"  [gh]    {msg}")
        n_issues += 1
    for msg in check_big_ideas():
        print(f"  [bigidea] {msg}")
        n_issues += 1
    bi_palette = _big_ideas_palette_audit()
    if bi_palette:
        print(f"  [bigidea] AUDIT-ONLY: {len(bi_palette)} Big-Ideas figure(s) carry a hex outside the "
              f"SVG palette (governed audit-only by lint_design_token_drift; does not gate):")
        for msg in bi_palette:
            print(f"            {msg}")
    for msg in check_banned_terms():
        print(f"  [banned] {msg}")
        n_issues += 1
    # CANONICAL-VOCABULARY — BLOCKING. The book's house term for its central artifact is a "structured
    # model" (structured data), not a "typed model" (typed data). This lint holds the settled term in the
    # narrative body chapters via a DEPRECATED->CANONICAL map. A fix-wave drove the tree to 0 before the
    # flip, so it lands BLOCKING (repo blocking-lint discipline). See book-models/lint_canonical_vocab.py.
    bm_vocab = os.path.join(ROOT, "book-models")
    if bm_vocab not in sys.path:
        sys.path.insert(0, bm_vocab)
    import lint_canonical_vocab as lcv  # noqa: E402 — blocking canonical-vocabulary lint
    for msg in lcv.findings():
        print(f"  [vocab] {msg}")
        n_issues += 1
    # NOTE-JUDGMENTS — the R7 invariant over book-models/note-judgments.json: every Appendix-B flagship note
    # teaches one distinct engineering judgment. Completeness (every note has a well-formed judgment record)
    # + curated distinct_from SHAPE are BLOCKING — deterministic, cannot false-positive on well-formed data;
    # the model ships clean, so they gate. The lexical-overlap SUGGESTion + foundational-ceiling warning are
    # AUDIT-ONLY (heuristics over prose + editorial weight) — they PRINT but do NOT increment n_issues. See
    # book-models/lint_note_judgments.py.
    import lint_note_judgments as lnj  # noqa: E402 — blocking (completeness + curation shape)
    for msg in lnj.blocking_findings():
        print(f"  [judgment] {msg}")
        n_issues += 1
    nj_audit = lnj.audit_findings()
    if nj_audit:
        print(f"  [judgment] AUDIT-ONLY: {len(nj_audit)} suggestion(s) — "
              f"run `python3 book-models/lint_note_judgments.py` (does not gate):")
        for msg in nj_audit:
            print(f"            {msg}")
    for msg in check_summary_counts(entries):
        print(f"  [census] {msg}")
        n_issues += 1
    for msg in check_no_raw_stats(entries):
        print(f"  [stat]  {msg}")
        n_issues += 1
    for msg in check_census_tokens(entries):
        print(f"  [census] {msg}")
        n_issues += 1
    for msg in check_leaked_markers():
        print(f"  [marker] {msg}")
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
    # DESIGN-TOKEN DRIFT — AUDIT-ONLY. The one-token / three-surface style gate (raw literals / off-scale
    # sizes / SVG-palette membership / mermaid freshness / anchor-hue pins). Lands audit-only per the repo's
    # blocking-lint discipline: it PRINTS its finding count here (so a committer sees the migration worklist)
    # but does NOT increment n_issues, so validate stays green until the migration drains it and a follow-up
    # flips it blocking. See book-models/lint_design_token_drift.py.
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    import lint_design_token_drift as ldtd  # noqa: E402 — audit-only drift gate
    drift = ldtd.findings()
    if drift:
        print(f"  [tokens] AUDIT-ONLY: {len(drift)} design-token-drift finding(s) — "
              f"run `python3 book-models/lint_design_token_drift.py` (does not gate)")
    # FIGURE OVERFLOW — the text-fits-its-box sensor over book/assets/*.svg. It landed AUDIT-ONLY-first per
    # the repo's blocking-lint discipline; a fix-wave has now drained its offenders to zero, so it is
    # FLIPPED BLOCKING: any label that overruns its padded box increments n_issues and reddens validate,
    # exactly like the sibling banned/census/stat checks. See book-models/lint_figure_overflow.py.
    import lint_figure_overflow as lfo  # noqa: E402 — blocking overflow sensor
    overflow = lfo.findings()
    if overflow:
        print(f"  [overflow] {lfo.summary_line(overflow)} — "
              f"run `python3 book-models/lint_figure_overflow.py`")
        n_issues += len(overflow)
    # FIGURE MIN-FONT — the figure-text-not-smaller-than-body sensor over book/assets/*.svg (the legibility
    # complement to the overflow sensor above). AUDIT-ONLY: a strict body-size floor surfaces every figure
    # whose labels normalize below body, which the design system's small label roles do corpus-wide — so it
    # PRINTS that backlog (a committer sees the enlarge worklist) but does NOT increment n_issues. The two
    # author-named figures are enlarged now; a follow-up flips it blocking once a re-layout wave drains the
    # rest (audit->lint, fix-then-flip). See book-models/lint_figure_min_font.py.
    import lint_figure_min_font as lfmf  # noqa: E402 — audit-only legibility sensor
    minfont = lfmf.findings()
    if minfont:
        print(f"  [minfont] AUDIT-ONLY: {lfmf.summary_line(minfont)} — "
              f"run `python3 book-models/lint_figure_min_font.py` (does not gate)")
    # BRICK FITNESS — the Appendix-C §13.4 sensor: a brick whose Structure diagram scores SIMPLIFY/GLYPH under
    # the thumbnail-fitness rubric but carries NO verdict in book-models/brick-fitness.json (the model the grid
    # renderer reads to pick diagram-vs-glyph). AUDIT-ONLY-first per the repo's blocking-lint discipline: all 83
    # verdicts are recorded, so it reports zero today; it exists to catch the NEXT unrecorded dense diagram. It
    # PRINTS any finding but does NOT increment n_issues. See book-models/lint_brick_fitness.py.
    import lint_brick_fitness as lbf  # noqa: E402 — audit-only brick-fitness sensor
    brick_unscored = lbf.findings()
    if brick_unscored:
        print(f"  [brick]  AUDIT-ONLY: {lbf.summary_line(brick_unscored)} — "
              f"run `python3 book-models/lint_brick_fitness.py` (does not gate)")
    # APPENDIX-B NOTE WORD-CAP — the EARLY sensor over the authored Flagship-Mechanism notes
    # (`book/appendix-notes/*.md`): a note whose prose outgrows its declared `note-spread` budget. AUDIT-ONLY
    # per the repo's blocking-lint discipline — it PRINTS its finding count (so an author sees a note that has
    # bloated past its page) but does NOT increment n_issues. The REAL invariant is the keep-together renderer's
    # rendered-height assertion in the PDF build; this word count is the cheap early warning. See
    # book-models/lint_appendix_b_note_word_cap.py.
    import lint_appendix_b_note_word_cap as labnw  # noqa: E402 — audit-only note word-cap sensor
    note_over = labnw.findings()
    if note_over:
        print(f"  [bnote]  AUDIT-ONLY: {len(note_over)} Appendix-B note(s) over the spread word budget — "
              f"run `python3 book-models/lint_appendix_b_note_word_cap.py` (does not gate)")
    # CAPTION LENGTH — every authored figure/table caption ≤3 sentences AND ≤50 words. HARD cap, NO noqa
    # escape (author instruction). A trim-wave drove the tree to 0, so it lands BLOCKING: an over-long
    # caption increments n_issues and reddens validate. See book-models/lint_caption_length.py.
    import lint_caption_length as lcl  # noqa: E402 — blocking caption-length cap (hard, no dispensation)
    long_caps = lcl.findings()
    if long_caps:
        print(f"  [caption] {lcl.summary_line(long_caps)} — "
              f"run `python3 book-models/lint_caption_length.py`")
        n_issues += len(long_caps)
    # NO-HARDCODED-REF — a cross-reference in the narrative prose names its target by a SYMBOLIC marker
    # (`{{part:N}}` / `[ref:<label>]` / `[appendix:<slug>]`), never a literal letter/number typed into the
    # sentence. The three "Appendix E" literals were converted to `[appendix: …]`, driving the tree to 0, so
    # it lands BLOCKING: a hardcoded reference increments n_issues. See book-models/lint_no_hardcoded_ref.py.
    import lint_no_hardcoded_ref as lnhr  # noqa: E402 — blocking symbolic-cross-reference lint
    hard_refs = lnhr.findings()
    if hard_refs:
        print(f"  [xref]  {lnhr.summary_line(hard_refs)} — "
              f"run `python3 book-models/lint_no_hardcoded_ref.py`")
        for f in hard_refs:
            print(f"          {f.file}:{f.line}: [{f.kind}] literal {f.text!r} — {f.remedy}")
        n_issues += len(hard_refs)
    # BRICK-METADATA — every catalogue mechanism carries a curated Appendix-C applicability AND primary-concern
    # call, and the two curated models (brick-applicability.json + brick-metadata.json) agree with the census.
    # Both models were authored complete (all 83 slugs), so the tree is green from birth → lands BLOCKING: a new
    # entry that omits either call, or a mismatched slug, increments n_issues. See book-models/lint_brick_metadata.py.
    import lint_brick_metadata as lbm  # noqa: E402 — blocking applicability+concern completeness lint
    brick_meta_findings = lbm.findings()
    if brick_meta_findings:
        print(f"  [brickmeta] {lbm.summary_line(brick_meta_findings)}:")
        for f in brick_meta_findings:
            print(f"          {f.slug}: {f.problem}")
        n_issues += len(brick_meta_findings)
    # FLAGSHIP-STACK CONFORMANCE (FS1–FS5) — AUDIT-ONLY. The deep-dive TEMPLATE check over the flagship
    # PACKAGE model (book-models/flagship-stack.json): join integrity, page shape, figure house-rules,
    # freshness. Lands audit-only-first (repo blocking-lint discipline) while the model carries fewer than
    # the full seven stacks — it PRINTS its findings + the deferred coverage note here (so a committer sees
    # the worklist) but does NOT increment n_issues. A follow-up flips it blocking once the seven land and a
    # clean session confirms the drain. See book-models/flagship_stack_model.py + tests/book_models.py.
    import flagship_stack_model as fsm  # noqa: E402 — audit-only conformance model
    fs_findings = fsm.structural_findings()
    print(f"  [flagship] AUDIT-ONLY: {fsm.coverage_note()}")
    if fs_findings:
        print(f"  [flagship] AUDIT-ONLY: {len(fs_findings)} FS conformance finding(s) — "
              f"run `python3 book-models/flagship_stack_model.py regenerate` (does not gate):")
        for f in fs_findings:
            print(f"             {f}")
    # LITERATURE-POSITIONING CONFORMANCE (LP1–LP6) — AUDIT-ONLY. The Literature-Positioning Pass model
    # (book-models/lit-positioning.json): every X→Y→Z intervention's frame is present, its citations nest
    # under the argument spine (backs_claims resolve), landed records' cites resolve in references.bib AND
    # appear in a target chapter, and the planned-vs-landed burndown is surfaced. Lands audit-only-first
    # (repo blocking-lint discipline) while the LPP prose waves are still landing — it PRINTS its findings +
    # the burndown here (so a committer sees the worklist) but does NOT increment n_issues. A follow-up flips
    # it blocking once the waves land and a clean session confirms the drain. See book-models/
    # lit_positioning_model.py + tests/book_models.py.
    import lit_positioning_model as lpm  # noqa: E402 — audit-only conformance model
    lp_findings = lpm.structural_findings()
    print(f"  [litpos] AUDIT-ONLY: {lpm.coverage_note()}")
    if lp_findings:
        print(f"  [litpos] AUDIT-ONLY: {len(lp_findings)} LP conformance finding(s) — "
              f"run `python3 book-models/lit_positioning_model.py regenerate` (does not gate):")
        for f in lp_findings:
            print(f"           {f}")
    # METRICS-DASHBOARD CONFORMANCE — BLOCKING. The back-matter "Operator's Dashboard" page is a projection
    # of a declared model (book-models/metrics-dashboard.json): the model carries the author's inclusion
    # criterion + every metric's formative/summative mode, and metrics_dashboard_model.py holds the page's
    # two-band table equal to that projection. Green from birth (the table is authored from the projection),
    # so it lands BLOCKING: a schema break, a broken defined-in cite, a changed mode count, or page-vs-model
    # drift reddens validate. See book-models/metrics_dashboard_model.py.
    import metrics_dashboard_model as mdm  # noqa: E402 — blocking dashboard-parity model
    md_findings = mdm.all_findings()
    if md_findings:
        print(f"  [dashboard] {len(md_findings)} metrics-dashboard finding(s) — "
              f"run `python3 book-models/metrics_dashboard_model.py verify`:")
        for f in md_findings:
            print(f"              {f}")
        n_issues += len(md_findings)
    # METAPHOR-SPANS CONFORMANCE — STRUCTURAL BLOCKING + OVERLAP AUDIT-ONLY. The book's sustained metaphors
    # are a declared model (book-models/metaphor-spans.json): each metaphor's span (introduced -> pays off)
    # plus its kind (core = always live / local = must pay off before the next local), so the author's rule
    # "never introduce a second metaphor until the first has paid off" is MEASURABLE. Two halves, two
    # landings: (1) the STRUCTURAL / schema invariants (C1-C7 — well-formedness, page + anchor resolution,
    # local-has-payoff, the ratified core/local split) land BLOCKING (green from birth; a malformed row
    # reddens validate); (2) the OVERLAP metric + the softer vehicle-collision check land AUDIT-ONLY-first
    # (repo blocking-lint discipline) — they PRINT here so a committer sees them, but do NOT increment
    # n_issues. Today's overlap count is 0, so the audit-only phase catches a newly-authored overlap before a
    # follow-up flips it blocking. See book-models/metaphor_spans_model.py + tests/book_models.py.
    import metaphor_spans_model as msm  # noqa: E402 — structural-blocking + overlap-audit-only model
    mp_structural = msm.structural_findings()
    if mp_structural:
        print(f"  [metaphor] {len(mp_structural)} STRUCTURAL finding(s) — "
              f"run `python3 book-models/metaphor_spans_model.py verify`:")
        for f in mp_structural:
            print(f"             {f}")
        n_issues += len(mp_structural)
    print(f"  [metaphor] AUDIT-ONLY: {msm.coverage_note()}")
    for f in msm.overlap_findings() + msm.vehicle_collision_findings():
        print(f"  [metaphor] AUDIT-ONLY: {f}")
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

# Three centered lines: (1) © + affiliation, (2) GitHub repo + read-the-book, (3) the NSF funding
# acknowledgement. Each rides its own block-level `.foot-line`; the footer is `text-align:center`.
SITE_FOOTER = (f'<footer class="site-foot">'
               f'<span class="foot-line foot-copy">© <a href="{_SITE_URL}">James C. Davis</a>, '
               f'2026–present &nbsp;·&nbsp; Assistant Professor, ECE @ Purdue</span>'
               f'<span class="foot-line foot-links">'
               f'<a class="gh" href="{_REPO_URL}">{GITHUB_SVG} {_REPO_NAME}</a>'
               f'&nbsp;·&nbsp; <a class="book-foot" href="{{book_prefix}}book/index.html">'
               f'Read the book →</a></span>'
               f'<span class="foot-line foot-nsf">This work was supported by the U.S. National Science '
               f'Foundation under grants #2541917 and #2452533.</span></footer>')

TOPNAV = (f'<div class="topnav"><a href="{_SITE_URL}">James C. Davis, Purdue University</a>'
          f'<a class="gh" href="{_REPO_URL}">'
          f'{GITHUB_SVG} GitHub</a></div>')

# Landing top-right 3×2 nav grid — bigger, higher-contrast tap targets than the old topnav link pair.
# Layout:  Author | GitHub | Quick Start   (top row, 3 cells)
#          Book | Book (PDF)                (bottom row, 2 cells centered under the 3-col track)
NAV_GRID = (
    '<nav class="nav-grid" aria-label="Primary">'
    f'<a class="ng-cell" href="{_SITE_URL}">'
    '<span class="ng-t">Author</span><span class="ng-s">James C. Davis · Purdue</span></a>'
    f'<a class="ng-cell" href="{_REPO_URL}">'
    f'<span class="ng-t">{GITHUB_SVG} GitHub</span><span class="ng-s">the source repository</span></a>'
    '<a class="ng-cell" href="quick-start.html">'
    '<span class="ng-t">Quick Start</span><span class="ng-s">adopt it in your repo</span></a>'
    '<a class="ng-cell ng-book ng-bottom" href="book/index.html">'
    '<span class="ng-t">Book</span><span class="ng-s">read the web book</span></a>'
    f'<a class="ng-cell ng-book ng-bottom" href="{_PDF_HREF}">'
    f'<span class="ng-t">{PDF_SVG} Book (PDF)</span><span class="ng-s">download offline</span></a>'
    '</nav>')


# FONT_CSS carries the design-token :root block (inlined once — it is present on every page) plus the
# family bindings and the shared footer/topnav chrome, all token-referenced. Display = Fraunces, body =
# Source Sans 3, mono = IBM Plex Mono (the Umber Monograph faces).
FONT_CSS = (CSS_ROOT_BLOCK +
            '  body { font-family:var(--font-body); }\n'
            '  h1,h2,h3,h4,.walk-h,.section-h { font-family:var(--font-display); font-weight:var(--display-weight); }\n'
            '  .site-foot { max-width:1320px; margin:var(--space-5) auto 0; padding:var(--space-2) 26px var(--space-4);'
            ' border-top:var(--border-hairline) solid var(--rule);'
            ' font-size:var(--fs-micro); color:var(--muted); text-align:center; }\n'
            '  .site-foot a { color:var(--accent); text-decoration:underline; } .site-foot a:hover { text-decoration:none; }\n'
            '  .site-foot .gh { white-space:nowrap; }\n'
            '  .site-foot .foot-line { display:block; }\n'
            '  .site-foot .foot-line + .foot-line { margin-top:var(--space-1); }\n'
            '  .site-foot .foot-nsf { color:var(--muted); }\n'
            '  .topnav { position:absolute; top:14px; right:20px; font-size:var(--fs-micro); display:flex; gap:var(--space-2); }\n'
            '  .topnav a { color:var(--muted); text-decoration:none; white-space:nowrap; } .topnav a:hover { color:var(--accent); }\n'
            '  @media (max-width:640px){ .topnav { position:static; justify-content:flex-end; margin:0 0 var(--space-1); } }\n')

PAGE_CSS = """
  /* Legacy var aliases → design tokens: --line/--link predate the token model and are referenced across
     the landing + views CSS; alias them so every site rule resolves to the Umber-Monograph tokens without
     touching hundreds of call sites. The token :root (inlined via FONT_CSS) defines --ink/--muted/--accent. */
  :root { --line: var(--rule); --link: var(--accent); }
  * { box-sizing: border-box; }
  body { margin:0; font-family:var(--font-body);
         color:var(--ink); background:var(--paper); line-height:var(--lh-body); font-size:var(--fs-body); }
  main { width: 94vw; max-width: 1320px; margin: 0 auto; padding: 32px 26px 80px; }
  /* The landing is a figure-prose BOARD — a controlled ceiling so wide-screen scan-lines stay comfortable
     (was 2100); entry/prose pages keep the 1320 reading width. */
  body.landing main { max-width: 1600px; }
  body.landing .site-foot { max-width: 1600px; }
  nav.crumb { font-size: var(--fs-meta); color: var(--muted); margin: 0 0 18px; letter-spacing:.01em; }
  nav.crumb a { color: var(--link); text-decoration: underline; text-underline-offset: 2px; }
  nav.crumb a:hover { text-decoration: underline; }
  h1 { font-size: var(--fs-thesis-title); margin: 6px 0 4px; letter-spacing:var(--display-tracking); line-height:1.12; }
  h2 { font-size: var(--fs-section); margin: 30px 0 8px; padding-top: 6px; border-top:var(--border-hairline) solid var(--line); }
  h3 { font-size: var(--fs-card-title); margin: 22px 0 6px; }
  h4 { font-size: var(--fs-card-body); margin: 16px 0 4px; color:var(--ink); }
  p, li { font-size: var(--fs-body); }
  a { color: var(--link); }
  code { background:var(--code-bg); padding:1px 5px; border-radius:var(--radius-chip); font-size:.9em;
         font-family:var(--font-mono); }
  pre { background:var(--code-bg); padding:12px 14px; border-radius:var(--radius-code); overflow:auto; }
  pre code { background:none; padding:0; }
  table { border-collapse: collapse; margin: 12px 0; font-size: var(--fs-meta); width:100%; }
  th, td { border:var(--border-hairline) solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; }
  th { background:var(--panel); font-weight:700; }
  hr { border:none; border-top:var(--border-hairline) solid var(--line); margin: 22px 0; }
  .subtitle { font-size: var(--fs-meta); color:var(--muted); font-style: italic; margin: 0 0 6px; }
  a.abbr { color:var(--ink); text-decoration:none; border-bottom:var(--border-hairline) dotted var(--accent);
           cursor:help; }
  a.abbr:hover { color:var(--accent); border-bottom-style:solid; }
  section.abbr-entry { scroll-margin-top:14px; }
  section.abbr-entry h2 code.slug { font-size:var(--fs-micro); font-weight:400; color:var(--accent);
           background:var(--accent-tint); vertical-align:middle; margin-left:8px; }
  p.abbr-grounds { font-size:var(--fs-meta); color:var(--muted); margin:4px 0 2px; }
  /* Derived "Governed by" block — appended to is-a-model entry pages (reverse of the Governs join). */
  .govby { margin-top:28px; border-top:var(--border-accent-bar) solid var(--accent); padding-top:6px; }
  .govby h2 { border-top:none; padding-top:0; margin-top:8px; }
  .gb-note { font-size:var(--fs-meta); color:var(--muted); font-style:italic; margin:2px 0 8px; }
  .gb-list { margin:0; padding-left:20px; }
  .gb-list li { font-size:var(--fs-meta); margin:4px 0; }
  .gb-list li a { font-weight:600; text-decoration:none; }
  .gb-list li a:hover { text-decoration:underline; color:var(--accent); }
  .gb-all { font-size:var(--fs-micro); color:var(--muted); background:var(--panel); border:var(--border-hairline) solid var(--rule);
            border-radius:var(--radius-chip); padding:0 6px; margin-left:5px; white-space:nowrap; }
  .tag { color: var(--accent); font-weight: 700; font-size: var(--fs-micro); letter-spacing:.08em; text-transform:uppercase; }
  .census h3.role-h { color:var(--accent); border-top:var(--border-accent-bar) solid var(--line); padding-top:14px; margin-top:26px; }
  .census .role-note { font-size:var(--fs-micro); color:var(--muted); background:var(--accent-tint); border-left:var(--border-accent-bar) solid var(--accent);
                       padding:7px 12px; border-radius:0 var(--radius-code) var(--radius-code) 0; margin:2px 0 10px; }
  /* Census tables read as the card language: no full cell-grid — row hairlines only, header a stronger
     bottom rule, warm-panel header fill. */
  table.census-t th, table.census-t td { border:none; border-bottom:var(--border-hairline) solid var(--line); }
  table.census-t thead th { border-bottom:2px solid var(--rule); background:var(--panel); }
  table.census-t td.c-name a { font-weight:600; text-decoration:none; }
  table.census-t td.c-name a:hover { text-decoration:underline; }
  table.census-t td.c-sum { font-size:var(--fs-meta); color:var(--muted); }
  table.census-t td.c-enf { white-space:nowrap; color:var(--ink); }
  table.census-t th, table.census-t td { vertical-align:top; }
  table.census-t tr:hover { background:var(--panel); }
  .fam-lede { font-size:var(--fs-meta); color:var(--muted); font-style:italic; margin:2px 0 6px; }
  .foot { font-size: var(--fs-micro); color: var(--muted); border-top:var(--border-hairline) solid var(--line); padding-top:14px; margin-top: 34px; }
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
    # Consume the remaining build-time markdown directives BEFORE block parsing, so a stray `<!-- … -->`
    # never reaches the paragraph path (which would ESCAPE it into visible text — the `constructing-the-gee`
    # `--census` / `-- summary` leak the browser showed). ALL served pages funnel through here, so the
    # standalone prose pages (constructing-the-gee, the role READMEs, README) now get the same consumption
    # the census/summary machinery always assumed: unwrap `<!--census:KEY-->V<!--/census-->` to its
    # build-filled value V (kept visible), and strip the invisible `<!-- summary: … -->` metadata line and
    # the `<!-- prior-art: … -->` provenance notes outright. Keyed to each named directive (not a blanket
    # comment-strip) so a comment inside a code span stays intact.
    md = _CENSUS_TOKEN.sub(lambda m: m.group(4), md)
    md = re.sub(r"<!--\s*summary:.*?-->", "", md, flags=re.DOTALL)
    md = re.sub(r"<!--\s*prior-art:.*?-->", "", md, flags=re.DOTALL)
    lines = md.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        st = lines[i].strip()
        if re.match(r'^<a id="[a-z0-9-]+"></a>$', st):
            out.append(st); i += 1; continue  # bare in-page anchor target — pass through raw (not escaped)
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
  /* ============================================================================================
     THE BIG-IDEAS LANDING — a projection of book-models/landing-big-ideas.json (Option 3, "the
     argument"). Every colour/size references a design token (the Umber-Monograph :root, inlined via
     FONT_CSS). Landing-only styles; the census + prose pages use PAGE_CSS. --line aliases --rule. */

  /* ---- shared chrome: title, nav pills, lead prose, dividers -------------------------------- */
  .book-h1 { margin:6px 0 2px; }
  .book-sub { color:var(--accent); font-weight:700; font-size:var(--fs-body); letter-spacing:.01em; margin:0 0 12px; }
  .nav-grid { display:flex; flex-wrap:wrap; justify-content:center; gap:9px; margin:0 0 22px; }
  .nav-grid .ng-cell { display:flex; flex-direction:column; justify-content:center; gap:1px;
              border:1.6px solid var(--rule); border-radius:10px; padding:7px 13px; background:var(--paper);
              text-decoration:none; color:var(--ink); transition:border-color .12s, background .12s; }
  .nav-grid .ng-cell:hover { border-color:var(--accent); background:var(--accent-tint); }
  .nav-grid .ng-t { font-size:var(--fs-meta); font-weight:700; color:var(--link); letter-spacing:-.01em; }
  .nav-grid .ng-t svg { fill:currentColor; }
  .nav-grid .ng-s { font-size:var(--fs-micro); color:var(--muted); line-height:1.25; }
  .nav-grid .ng-book { border-color:var(--accent); background:var(--accent-tint); }
  .nav-grid .ng-book .ng-t { color:var(--accent); }
  .site-foot .book-foot { white-space:nowrap; font-weight:600; }
  .lead, .m-lead { max-width:74ch; font-size:var(--fs-body); color:var(--ink); line-height:1.66; margin:0 0 13px; }
  .m-lead .term, .lead .term { font-weight:700; }
  .hero-cta { color:var(--accent); font-weight:600; text-decoration:none; }
  .hero-cta:hover { text-decoration:underline; }
  hr.sep { border:none; border-top:1px solid var(--line); margin:30px 0 24px; }
  hr.i-sep { border:none; border-top:1px solid var(--rule); margin:34px 0; }
  figure { margin:0; min-width:0; }
  .m-cap { display:block; font-size:var(--fs-meta); color:var(--muted); line-height:1.55; margin:11px 2px 0; text-align:center; }
  .m-cap b { color:var(--muted); }

  /* ---- HERO band: a prose-led lead that flows straight into the Big Idea 1 churn flowchart ---- */
  .hero-band { margin:8px 0 6px; }
  .hero-lead { max-width:1000px; margin:0 auto; text-align:center; }
  .hero-lead .book-h1 { margin-top:0; }
  .hero-lead .book-sub { margin-left:auto; margin-right:auto; }
  /* A wider, larger lead paragraph — a comfortable reading measure that better matches the full-width
     lead figure beneath it (author feedback: the intro read too narrow + too small on a wide display). */
  .hero-lead .m-lead { max-width:82ch; font-size:20px; line-height:1.6; margin-left:auto; margin-right:auto; }

  /* ---- the Big-Ideas argument ---------------------------------------------------------------- */
  .big-ideas { margin:20px 0 4px; }
  .s-kick { font-size:var(--fs-micro); text-transform:uppercase; letter-spacing:.08em; font-weight:800;
            color:var(--accent); margin:0 0 3px; }
  .s-title { font-family:var(--font-display); font-size:var(--fs-card-title); font-weight:var(--display-weight);
             letter-spacing:-.01em; line-height:1.22; margin:0 0 8px; border-top:none; padding-top:0; }
  .s-claim { font-size:var(--fs-body); color:var(--muted); line-height:1.62; margin:0 0 10px; max-width:66ch; }
  .s-claim b, .s-claim .term { color:var(--ink); }
  .s-fig svg { display:block; width:100%; height:auto; }

  /* Big Idea 1 - the landing's lead visual: the churn flowchart full-width beneath the hero lead. */
  .idea-hero { margin:22px 0 0; }
  .idea-hero .ih-fig svg { display:block; width:100%; height:auto; max-width:1080px; margin:0 auto; }
  .idea-hero .ih-words { max-width:84ch; margin:16px auto 0; text-align:center; }
  .idea-hero .ih-words .s-claim { max-width:84ch; margin-left:auto; margin-right:auto; }

  /* A Big-Idea band: figure beside words, sides alternate for rhythm. */
  .slot { display:grid; grid-template-columns:minmax(0,1.2fr) minmax(0,1fr); gap:16px 42px; align-items:center; }
  .slot.figright .s-fig { order:2; }
  .slot .s-words { min-width:0; }

  /* Big Ideas 5 & 6 — enlarged figures (author feedback: too small to read beside the words). Reuse the
     idea-hero full-width idiom: the figure spans the content column, the words center beneath it, so a
     wide diagram is legible without zooming. */
  .slot.slot-bigfig { display:block; }
  .slot.slot-bigfig .s-fig { margin:0 0 18px; }
  .slot.slot-bigfig .s-fig svg { max-width:1080px; margin:0 auto; }
  .slot.slot-bigfig .s-words { max-width:80ch; margin:0 auto; text-align:center; }
  .slot.slot-bigfig .s-claim { max-width:74ch; margin-left:auto; margin-right:auto; }
  .slot.slot-bigfig .s-more-text { margin-left:auto; margin-right:auto; }
  .slot.slot-bigfig button.s-expand { margin-left:auto; margin-right:auto; text-align:center; }

  /* The matched thesis PAIR - two half-width cells, figure above words. */
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:30px; }
  .pair .p-cell { border-top:3px solid var(--box-thesis-rule); padding-top:14px; scroll-margin-top:16px; }
  .pair .p-cell .s-kick { color:var(--box-thesis-rule); }
  .pair .p-cell .s-fig { margin:0 0 12px; }

  /* The LIGHT "expand to learn more" disclosure. The button is INJECTED by EXPAND_JS; with JS off the
     .s-more-text block simply shows (no broken control). */
  .s-more-text { font-size:var(--fs-card-body); color:var(--muted); line-height:1.6; margin:0 0 10px; max-width:64ch; }
  .idea-hero .s-more-text { margin-left:auto; margin-right:auto; }
  button.s-expand { display:block; font:inherit; font-size:var(--fs-meta); font-weight:700;
             color:var(--accent); background:none; border:none; padding:0; margin:0 0 10px; cursor:pointer;
             letter-spacing:.01em; text-align:left; }
  button.s-expand::before { content:"\\203A\\00a0"; }
  button.s-expand:hover { text-decoration:underline; }
  button.s-expand:focus-visible { outline:2px solid var(--accent); outline-offset:2px; border-radius:3px; }
  .idea-hero button.s-expand { margin:0 auto 10px; text-align:center; }
  .s-read { display:inline-block; font-size:var(--fs-meta); font-weight:700; color:var(--accent);
            text-decoration:none; }
  .s-read:hover { text-decoration:underline; }

  /* ---- the closing: conclusion + four ways in ----------------------------------------------- */
  /* A wide, fluid footer block (author feedback: the closing read too narrow on a wide display). It uses
     the top-text measure and flows to more of the page; the four ways-in buttons ride a 1×4 grid on wide
     screens and collapse to 2-up then a single stacked column as the viewport narrows. */
  .closing { max-width:1200px; margin:8px auto 8px; text-align:center; }
  .close-lead { font-size:var(--fs-body); line-height:var(--lh-body); color:var(--ink); margin:0 auto 20px; max-width:82ch; }
  .close-ways { display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:12px; align-items:stretch; }
  .close-btn { display:block; border:1.6px solid var(--rule); border-top:4px solid var(--accent); border-radius:12px;
               background:var(--paper); padding:14px 20px; text-decoration:none; color:var(--ink); min-width:0;
               transition:border-color .12s, background .12s; }
  .close-btn:hover { border-color:var(--accent); background:var(--accent-tint); }
  .close-btn .cb-t { display:block; font-family:var(--font-display); font-size:var(--fs-card-title); font-weight:600; }
  .close-btn .cb-s { display:block; font-size:var(--fs-micro); color:var(--muted); margin-top:3px; }

  /* ---- the quiet back-matter vocabulary/definitions/outcomes reference strip ----------------- */
  .reference { margin:26px 0 6px; }
  .deep-h { font-family:var(--font-display); font-size:var(--fs-section); margin:0 0 4px; border-top:none; padding-top:0; letter-spacing:-.01em; }
  .deep-note { font-size:var(--fs-meta); color:var(--muted); font-style:italic; margin:0 0 14px; max-width:74ch; }
  .deep-grp { margin:0 0 14px; }
  .deep-lbl { display:block; font-size:var(--fs-micro); text-transform:uppercase; letter-spacing:.06em;
              font-weight:800; color:var(--muted); margin:0 0 7px; }
  .deep-row { display:flex; flex-wrap:wrap; gap:9px; }
  .deep-item { display:block; border:1.4px solid var(--rule); border-radius:9px; background:var(--panel);
               padding:8px 13px; text-decoration:none; color:var(--ink); font-size:var(--fs-meta); line-height:1.3;
               scroll-margin-top:16px; }
  .deep-item b { display:block; font-size:var(--fs-meta); font-weight:700; color:var(--ink); }
  .deep-item span { display:block; color:var(--muted); font-size:var(--fs-micro); margin-top:1px; }
  .deep-item:hover { border-color:var(--accent); background:var(--accent-tint); }
  /* the `structured` adjective, held out of the four peers as a rider — blue def-box tint ties it to §2.1 */
  .def-rider-lead { display:block; width:100%; font-size:var(--fs-micro); font-style:italic; color:var(--muted); margin:8px 0 0; }
  .deep-item.def-rider { border-style:dashed; border-color:var(--box-def-rule); }

  /* The learning-outcomes list (projected from book-models/outcomes.json), tiered Program → Module. */
  .oc-tier { margin:0 0 4px; }
  .oc-tier-h { font-size:var(--fs-micro); text-transform:uppercase; letter-spacing:.05em; font-weight:800;
               color:var(--muted); margin:10px 0 1px; }
  .oc-unit small { display:block; font-weight:600; text-transform:none; letter-spacing:0; color:var(--muted); }
  ul.oc-list { margin:4px 0 4px; padding:0; list-style:none; }
  ul.oc-list li.oc-row { display:grid; grid-template-columns:auto auto 1fr auto; gap:10px; align-items:baseline;
                   font-size:var(--fs-meta); color:var(--ink); line-height:1.5; padding:7px 0;
                   border-top:1px solid var(--line); scroll-margin-top:16px; }
  ul.oc-list li.oc-row:first-child { border-top:none; }
  .oc-row .oc-unit { font-weight:800; color:var(--accent); white-space:nowrap; font-size:var(--fs-micro); }
  .oc-row .oc-bloom { font-size:var(--fs-micro); text-transform:uppercase; letter-spacing:.05em; font-weight:800;
                   color:var(--paper); background:var(--accent); border-radius:4px; padding:1px 6px; white-space:nowrap; }
  .oc-row .oc-stmt { color:var(--ink); }
  .oc-row .oc-more { color:var(--link); white-space:nowrap; font-size:var(--fs-micro); text-decoration:none; }

  /* ---- the bottom book CTA ------------------------------------------------------------------- */
  .book-cta { text-align:center; margin:20px 0 30px; }
  .book-cta a { color:var(--accent); font-size:var(--fs-body); text-decoration:none; }
  .book-cta a:hover { text-decoration:underline; }
  .book-cta-pdf { display:inline-block; margin-left:14px; }
  .book-cta-pdf a { font-size:var(--fs-meta); font-weight:600; color:var(--accent); text-decoration:none;
                    padding:3px 10px; border:1px solid var(--rule); border-radius:6px; }
  .book-cta-pdf a:hover { border-color:var(--accent); background:var(--panel); text-decoration:none; }

  /* ---- responsive: stack every two-column primitive at <= 900px ----------------------------- */
  @media (max-width:900px){
    .slot { grid-template-columns:1fr; gap:14px; }
    .slot.figright .s-fig { order:0; }
    .slot .s-fig { max-width:640px; margin:0 auto; }
    .pair { grid-template-columns:1fr; gap:22px; }
    .close-ways { grid-template-columns:1fr 1fr; }
  }
  @media (max-width:640px){
    ul.oc-list li.oc-row { grid-template-columns:1fr; gap:3px; }
    .close-ways { grid-template-columns:1fr; }
  }
"""

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


def _def_strip_link(rec: dict, cls: str) -> str:
    """One anchored definition link — `<a id="def-<slug>">` carries the record's `site_home` (the drift
    check's join key) and points at the definition's book home (the fuller treatment)."""
    slug = rec["_slug"]
    site_home = rec.get("site_home", f"def-{slug}")
    term = _esc(rec.get("term", slug))
    box = _esc(rec.get("box", ""))
    frame = box.split(" — ")[0].split(". ")[0].rstrip(".") if box else ""
    href = _esc(rec.get("book_home", "book/2.1-the-agent-stack.html"))
    return (f'<a class="{cls}" id="{_esc(site_home)}" href="{href}">'
            f'<b>{term}</b><span>{frame}</span></a>')


def _landing_definitions() -> str:
    """The FOUR core-term definitions projected COMPACTLY from book/data/definitions.json as a strip of
    anchored links, then the adjective every one of them rides on — `structured` — as a RIDER after the
    four, NOT a fifth peer (the '2.1 rider, not a fifth term' shape, on the landing). Site element ⟵ model
    element: each link's id is `def-<slug>` = the record's `site_home`, the join key the definitions drift
    check asserts resolves on the landing (the rider keeps `def-structured` present, so the projection
    still resolves both directions). Each link goes to its book home, honoring `site previews; book ⊇ site`."""
    peers: list[str] = []
    rider: dict | None = None
    for rec in _load_definitions():
        if rec.get("site_home") == "N/A":
            continue             # book-only definition (core-construct inset) — never projected to the site
        if rec["_slug"] == "structured":
            rider = rec          # the adjective — held out of the peer strip, appended as a rider
        else:
            peers.append(_def_strip_link(rec, "deep-item"))
    strip = "\n      ".join(peers)
    if rider is not None:
        strip += ('\n      <span class="def-rider-lead">— and the adjective every one of them rides on:</span>'
                  f'\n      {_def_strip_link(rider, "deep-item def-rider")}')
    return strip


def _outcome_index_by_id() -> dict:
    """{outcome_id: record} over book-models/outcomes.json — the derived outcomes view the site projects
    a slice of. Read-only: the site is a projection OF this model, never an edit to it."""
    path = os.path.join(ROOT, "book-models", "outcomes.json")
    if not os.path.isfile(path):
        return {}
    raw = json.load(open(path, encoding="utf-8"))
    return {o["outcome_id"]: o for o in raw.get("outcomes", []) if o.get("outcome_id")}


def _outcomes_hierarchy() -> dict:
    """The Module → Lesson → outcome hierarchy block from book-models/outcomes.json (derived by the
    outcomes model). Read-only; the site projects a slice of it. Empty dict if absent (thin-fallback)."""
    path = os.path.join(ROOT, "book-models", "outcomes.json")
    if not os.path.isfile(path):
        return {}
    return json.load(open(path, encoding="utf-8")).get("hierarchy", {})


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
    book-models/outcomes.json filtered by book/data/outcomes-site.json's selection, tiered as a
    Module → Lesson → outcome course structure (Module = Part, Lesson = chapter). The site surfaces two
    tiers: the whole-book PROGRAM outcomes, then one row per MODULE (each carrying its Part-level outcome
    and a count of the Lessons it contains — the finer Lesson/section outcomes stay book-only). Each row
    renders the outcome's `statement` STRAIGHT FROM the model (no copy), a bloom-verb tag, and a link to
    its book home. Re-running the outcomes drain re-syncs this section (row ids stay `outcome-<slug>`)."""
    site = _load_outcomes_site()
    if not site:
        return ""
    by_id = _outcome_index_by_id()
    home_map = site.get("_book_home_map", {})
    lessons_by_module = {m.get("module"): len(m.get("lessons", []))
                         for m in _outcomes_hierarchy().get("modules", [])}
    selected = [by_id[oid] for oid in site.get("projected", []) if oid in by_id]

    def _row(o: dict, label: str, sub: str = "") -> str:
        oid = o["outcome_id"]
        home = home_map.get(o.get("primary_unit", ""), "book/index.html")
        sub_html = f"<small>{_esc(sub)}</small>" if sub else ""
        return (
            f'<li id="{_outcome_row_id(oid)}" class="oc-row">'
            f'<span class="oc-unit">{_esc(label)}{sub_html}</span>'
            f'<span class="oc-bloom">{_esc(o.get("bloom", ""))}</span>'
            f'<span class="oc-stmt">{_esc(o.get("statement", ""))}</span>'
            f'<a class="oc-more" href="{_esc(home)}">read →</a></li>')

    program = [o for o in selected if o.get("granularity") == "book"]
    modules = sorted((o for o in selected if o.get("granularity") == "part"),
                     key=lambda o: o.get("primary_unit", ""))
    blocks = []
    if program:
        rows = "".join(_row(o, "The book") for o in program)
        blocks.append('<div class="oc-tier"><p class="oc-tier-h">Across the whole program</p>'
                      f'<ul class="oc-list">{rows}</ul></div>')
    if modules:
        rows = []
        for o in modules:
            unit = o.get("primary_unit", "")
            n = lessons_by_module.get(unit, 0)
            rows.append(_row(o, unit.replace("part-", "Module "),
                             sub=f"{n} lesson{'s' if n != 1 else ''}"))
        blocks.append('<div class="oc-tier"><p class="oc-tier-h">Module by module</p>'
                      f'<ul class="oc-list">{"".join(rows)}</ul></div>')
    return "".join(blocks)


# ── The Big-Ideas model — the landing AS A PROJECTION of the book's argument ─────────────────────
# book-models/landing-big-ideas.json is the SSOT: six Big Ideas in the book's own order + a gateway,
# each rendered as one slot (figure · concise claim · a light "expand to learn more" · "Read in the
# book →"). Nothing on the landing's Big-Ideas argument is hand-authored in HTML — a build iterates
# the model. The drift check (`check_big_ideas`) keeps the projection faithful. See book-models/SITE-VIEW.md.

def _load_big_ideas() -> dict:
    """Read book-models/landing-big-ideas.json → the raw record dict (meta `_`-keys kept for the loader
    to read `_order` / `_word_cap`). The landing's Big-Ideas argument is a projection of this model."""
    path = os.path.join(ROOT, "book-models", "landing-big-ideas.json")
    if not os.path.isfile(path):
        return {}
    return json.load(open(path, encoding="utf-8"))


def _big_ideas_ordered() -> list[dict]:
    """The six Big-Idea records in `_order`, each tagged with its slug (`_slug`). The gateway is NOT in
    `_order` — it renders separately as the census gateway, so it is excluded here."""
    raw = _load_big_ideas()
    order = raw.get("_order", [])
    return [raw[k] | {"_slug": k} for k in order if k in raw]


def _read_link(book_home: str, label: str = "Read in the book →") -> str:
    """The uniform per-slot book link — one consistent verb+destination across every Big Idea."""
    return f'<a class="s-read" href="{_attr(book_home)}">{_esc(label)}</a>'


def _more_block(rec_id: str, more: str) -> str:
    """The LIGHT disclosure body. Rendered VISIBLE by default (no `hidden` attribute) so with JS off the
    text simply shows — no broken control. The end-of-page script (EXPAND_JS) progressively enhances it:
    it injects a keyboard-operable toggle button, collapses this block, and wires aria-expanded — CSP-safe
    (addEventListener, no inline handler)."""
    return f'<div class="s-more-text" id="more-{_attr(rec_id)}" data-more>{_esc(more)}</div>'


def _idea_figure(rec: dict) -> str:
    """The slot's figure, spliced inline with its internal ids namespaced per-slot (so no two figures — or
    a figure reused — collide on element ids). Falls back to empty if the asset is missing."""
    svg = _inline_svg("assets/" + rec.get("figure", ""))
    return _ns_svg_ids(svg, "bi-" + rec.get("_slug", rec.get("id", "x")))


def _big_idea_band(rec: dict, figright: bool = False, bigfig: bool = False) -> str:
    """One Big Idea as a full-width band: figure beside words (sides alternate for rhythm), one clean
    block — no card, no thumbnail, no peek. Divider handled by the caller. `bigfig` renders the band
    stacked full-width (figure above centred words) for ideas whose figure needs the whole column to
    stay legible; it supersedes `figright` (side is moot when the figure spans the column)."""
    cls = "slot slot-bigfig" if bigfig else ("slot figright" if figright else "slot")
    return (
        f'<div class="{cls}" id="{_attr(rec.get("id", ""))}">\n'
        f'  <figure class="s-fig">{_idea_figure(rec)}</figure>\n'
        f'  <div class="s-words">\n'
        f'    <p class="s-kick">{_esc(rec.get("kicker", ""))}</p>\n'
        f'    <h2 class="s-title">{_esc(rec.get("title", ""))}</h2>\n'
        f'    <p class="s-claim">{_esc(rec.get("claim", ""))}</p>\n'
        f'    {_more_block(rec.get("id", ""), rec.get("more", ""))}\n'
        f'    {_read_link(rec.get("book_home", ""))}\n'
        f'  </div>\n'
        f'</div>')


def _thesis_cell(rec: dict, concept_id: str) -> str:
    """One half of the matched thesis PAIR. Carries `id="<concept_id>"` (card-thesis-modeling /
    card-thesis-alignment) so the thesis concepts' `site_home` resolves on the landing — the slot IS the
    concept's site realization (the concept drift check joins on this id)."""
    return (
        f'<div class="p-cell" id="{_attr(concept_id)}">\n'
        f'  <figure class="s-fig" id="{_attr(rec.get("id", ""))}">{_idea_figure(rec)}</figure>\n'
        f'  <p class="s-kick">{_esc(rec.get("kicker", ""))}</p>\n'
        f'  <h2 class="s-title">{_esc(rec.get("title", ""))}</h2>\n'
        f'  <p class="s-claim">{_esc(rec.get("claim", ""))}</p>\n'
        f'  {_more_block(rec.get("id", ""), rec.get("more", ""))}\n'
        f'  {_read_link(rec.get("book_home", ""))}\n'
        f'</div>')


def _landing_big_ideas() -> str:
    """The six Big Ideas, rendered from the model in the book's argument order: idea 1 (the problem)
    fused as the full-width churn-flowchart band directly under the hero; the stance as one band; the two
    theses as a matched PAIR (Thesis 1 / Thesis 2); then practice and seat as alternating bands. The
    thesis pair cells carry the thesis concepts' site ids."""
    by_slug = {r["_slug"]: r for r in _big_ideas_ordered()}
    parts: list[str] = []
    # Idea 1 — the problem — the full-width churn flowchart, the hero-void fix, with Big-Idea framing.
    p1 = by_slug["churn"]
    parts.append(
        f'<div class="idea-hero" id="{_attr(p1.get("id", ""))}">\n'
        f'  <figure class="ih-fig">{_idea_figure(p1)}</figure>\n'
        '  <div class="ih-words">\n'
        f'    <p class="s-kick">{_esc(p1.get("kicker", ""))}</p>\n'
        f'    <h2 class="s-title">{_esc(p1.get("title", ""))}</h2>\n'
        f'    <p class="s-claim">{_esc(p1.get("claim", ""))}</p>\n'
        f'    {_more_block(p1.get("id", ""), p1.get("more", ""))}\n'
        f'    {_read_link(p1.get("book_home", ""))}\n'
        '  </div>\n'
        '</div>')
    parts.append('<hr class="i-sep" />')
    # Idea 2 — the stance — one band.
    parts.append(_big_idea_band(by_slug["governance-centric"], figright=True))
    parts.append('<hr class="i-sep" />')
    # Ideas 3 & 4 — the two theses — a matched pair (the concepts' site homes).
    parts.append(
        '<div class="pair">\n'
        + _thesis_cell(by_slug["modeling-thesis"], "card-thesis-modeling") + "\n"
        + _thesis_cell(by_slug["alignment-thesis"], "card-thesis-alignment") + "\n"
        + '</div>')
    parts.append('<hr class="i-sep" />')
    # Ideas 5 & 6 — practice, then seat — enlarged full-width figures (legible without zooming).
    parts.append(_big_idea_band(by_slug["convert-failures"], bigfig=True))
    parts.append('<hr class="i-sep" />')
    parts.append(_big_idea_band(by_slug["seat-moves"], bigfig=True))
    return "\n\n  ".join(parts)


def _landing_closing() -> str:
    """The page's conclusion — the argument's sign-off, drawn from the book's own closing chapter — then
    the three ways in: the full catalogue, the book, and the Claude quickstart. This CLOSES the landing
    after Big Idea 6; it replaces the old F1-gateway band, so the reader leaves on the conclusion and a
    choice of entry rather than a mid-page gateway."""
    ways = [
        ("The construction kit", "constructing-the-gee.html",
         "the architecture: 9 capabilities · 25 canonical mechanisms · 8 compositions"),
        ("Full catalogue", "catalogue-views.html", "every mechanism, by role · model · enforcement"),
        ("Book", "book/index.html", "the full treatment of the method"),
        ("Claude quickstart", "quick-start.html", "install the skills in your repo"),
    ]
    buttons = "\n    ".join(
        f'<a class="close-btn" href="{_attr(h)}"><span class="cb-t">{_esc(t)}</span>'
        f'<span class="cb-s">{_esc(s)}</span></a>'
        for t, h, s in ways)
    return (
        '<section class="closing" aria-label="In closing">\n'
        '  <p class="close-lead">The code got cheap; the judgment got expensive. Govern the conditions '
        'under which fast code can be trusted — the machine can search faster than any of us, but it cannot '
        'tell us what is worth searching for. So start with one recurring failure your agents keep handing '
        'you, and convert it: one type, one lint, one gate. The method grows from there; below are four '
        'ways in.</p>\n'
        f'  <div class="close-ways">\n    {buttons}\n  </div>\n'
        '</section>')


# The remaining site-eligible concepts whose `card-<slug>` id must resolve on the landing (the thesis
# concepts land on the pair cells above; these five are the alignment/modeling vocabulary). Each renders
# as an anchored link in the back-matter reference strip → its book home. (title, id, book_home)
_DEEP_CONCEPTS = [
    ("Models as the universal language", "card-universal-language", "book/6.0-implications-for-se.html"),
    ("Constraint", "card-constraint", "book/2.3-the-governed-environment.html"),
    ("Sensor", "card-sensor", "book/2.3-the-governed-environment.html"),
    ("The residual", "card-residual", "book/2.3-the-governed-environment.html"),
    ("Generative validation", "card-generate-to-falsify", "book/4.6-generative-validation.html"),
]


def _landing_reference() -> str:
    """The quiet back-matter reference strip — trimmed from the old 'Deeper in the book' masonry to the
    rows the site still OWES the reader and the projection-drift gates require: the four definitions + the
    adjective they ride on, the alignment/modeling vocabulary, and the learning outcomes. It keeps the
    `def-<slug>`, `card-<slug>`, and `outcome-<…>` ids the projection-drift gates (definitions, concepts
    L2/L3, outcomes) join against, so the model→site projection stays checkable. The F1-gateway band and
    the duplicate 'More' nav row are DROPPED — the top nav-grid and the closing's three buttons carry
    navigation now; the book claims and expands every framing (site previews; book ⊇ site)."""
    concept_items = "\n      ".join(
        f'<a class="deep-item" id="{_attr(cid)}" href="{_attr(home)}"><b>{_esc(title)}</b></a>'
        for title, cid, home in _DEEP_CONCEPTS)
    # The two method-view pages the landing is the sole entry point for — kept linked so the reachability
    # gate stays green (the rest of the old "More" row is reachable from the top nav-grid + the book index).
    more_links = "\n      ".join(
        f'<a class="deep-item" href="{_attr(h)}"><b>{_esc(t)}</b></a>'
        for t, h in [
            ("Browse the book models", "book-models/models-view.html"),
            ("The development process, as a figure", "development-workflow.html"),
        ])
    return (
        '<section class="reference" aria-labelledby="reference-h">\n'
        '  <h2 id="reference-h" class="deep-h">The vocabulary, in brief</h2>\n'
        '  <p class="deep-note">The site previews; the book claims and expands every framing. Each row '
        'is an entry point into the fuller treatment.</p>\n'
        '  <div class="deep-grp">\n'
        '    <span class="deep-lbl">The four definitions — the vocabulary the theses ride on</span>\n'
        f'    <div class="deep-row">\n      {_landing_definitions()}\n    </div>\n'
        '  </div>\n'
        '  <div class="deep-grp">\n'
        '    <span class="deep-lbl">The alignment &amp; modeling vocabulary</span>\n'
        f'    <div class="deep-row">\n      {concept_items}\n    </div>\n'
        '  </div>\n'
        '  <div class="deep-grp">\n'
        '    <span class="deep-lbl">What you\'ll be able to do — the learning outcomes</span>\n'
        f'    {_landing_outcomes()}\n'
        '  </div>\n'
        '  <div class="deep-grp">\n'
        '    <span class="deep-lbl">More views of the method</span>\n'
        f'    <div class="deep-row">\n      {more_links}\n    </div>\n'
        '  </div>\n'
        '</section>')


# End-of-body progressive-enhancement script for the LIGHT per-slot disclosure. Each `.s-more-text` block
# ships VISIBLE (so with JS off the text is readable — no broken control). This injects a keyboard-operable
# toggle button before each block, collapses it, and keeps `aria-expanded` in sync. CSP-safe: it uses
# addEventListener and DOM APIs only — no inline event handlers, no eval.
EXPAND_JS = """<script>
(function(){
  var blocks = document.querySelectorAll('.s-more-text[data-more]');
  Array.prototype.forEach.call(blocks, function(m){
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 's-expand';
    btn.setAttribute('aria-controls', m.id);
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = 'Expand to learn more';
    m.parentNode.insertBefore(btn, m);
    m.setAttribute('hidden', '');
    btn.addEventListener('click', function(){
      var willOpen = m.hasAttribute('hidden');
      if (willOpen) { m.removeAttribute('hidden'); } else { m.setAttribute('hidden', ''); }
      btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      btn.textContent = willOpen ? 'Show less' : 'Expand to learn more';
    });
  });
})();
</script>"""

LANDING_INTRO = """  <!-- ===================== HERO + BIG IDEA 1 =====================
       The landing is a PROJECTION of the Big-Ideas model (book-models/landing-big-ideas.json), laid out
       as the book's own argument in the book's own order (Option 3 "the argument"). The hero is a
       prose-led lead — the title + the framing paragraph — that flows straight into Big Idea 1, whose
       churn flowchart renders full-width beneath it as the landing's LEAD VISUAL. Then the stance (one
       band), the two theses (a matched pair), practice and seat (alternating bands), and the CLOSING —
       the conclusion + three ways in (full catalogue · book · quickstart). The census and the quiet
       vocabulary/definitions/outcomes reference strip follow as back-matter (appended in cmd_build). Each
       Big-Idea slot = figure · concise claim · a light "expand to learn more" · "Read in the book →". No
       card masonry, no <details> peeks — a build renders every slot from the model. -->
  <div class="hero-band">
    <div class="hero-lead">
      {book_title_block}
      <p class="m-lead">Generative AI is shifting software engineering from a practice built around scarce
      implementation toward one built around abundant, low-cost code. The hard part stops being writing
      code and becomes <span class="term">governing the conditions under which fast code can be
      trusted</span>. This site describes a method for doing that. The method is called <span class="term">Model-Based
      Agentic Software Engineering (MAGE)</span>. MAGE has six big ideas described below. To learn more,
      <a class="hero-cta" href="book/index.html"><strong>the book provides the full treatment.</strong></a></p>
      <p class="m-lead"><a class="hero-cta" href="quick-start.html"><strong>QuickStart: Bootstrap MAGE in
      your own project by installing the Skills for Claude.</strong></a></p>
    </div>
  </div>

  <div class="big-ideas">
  {big_ideas}
  </div>

  <hr class="sep" />

  {closing}
"""


VIEWS_CSS = """
  /* The views page carries FONT_CSS's token :root too. Role top-bars keep a 3-way coding, all sourced
     from the token palette (agent=accent umber · bridge=fleet navy · product=thesis green) — this page
     has no thesis/def boxes, so the reuse never collides on-surface. --line aliases --rule. */
  :root { --line: var(--rule); --a: var(--accent); --p: var(--box-thesis-rule); --b: var(--diagram-fleet); }
  * { box-sizing:border-box; }
  body { margin:0; padding:26px 20px 70px; color:var(--ink); background:var(--paper); line-height:1.4;
         font-family:var(--font-body); }
  h1 { font-size:var(--fs-card-title); max-width:1080px; margin:0 auto 4px; }
  .sub { max-width:1080px; margin:0 auto 14px; font-size:var(--fs-micro); color:var(--muted); }
  .sub a { color:var(--accent); }
  #tabs { max-width:1080px; margin:0 auto 6px; display:flex; flex-wrap:wrap; gap:6px; }
  .tab { font:inherit; font-size:var(--fs-micro); font-weight:600; cursor:pointer; border:var(--border-hairline) solid var(--line);
         background:var(--panel); color:var(--muted); border-radius:var(--radius-code); padding:5px 11px; }
  .tab.on { background:var(--ink); color:var(--paper); border-color:var(--ink); }
  #stage { max-width:1080px; margin:10px auto 0; }
  .blurb { font-size:var(--fs-micro); color:var(--muted); font-style:italic; margin:0 0 12px; }
  .grp { margin:0 0 16px; }
  .grp h2 { font-size:var(--fs-meta); margin:0 0 7px; padding-bottom:3px; border-bottom:var(--border-hairline) solid var(--line); }
  .grp h2 .cnt { color:var(--muted); font-weight:500; font-size:var(--fs-micro); }
  .grp h2 .gloss { color:var(--muted); font-weight:400; font-size:var(--fs-micro); font-style:italic; }
  .rt-a{color:var(--a);font-weight:800;} .rt-b{color:var(--b);font-weight:800;} .rt-p{color:var(--p);font-weight:800;}
  .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:8px; }
  .card { display:block; text-decoration:none; color:var(--ink); border:var(--border-hairline) solid var(--rule);
          border-radius:var(--radius-chip); padding:7px 9px; background:var(--paper); transition:border-color .12s, background .12s; }
  .card:hover { border-color:var(--accent); background:var(--accent-tint); }
  .card.r-a { border-top:var(--border-accent-bar) solid var(--a); } .card.r-p { border-top:var(--border-accent-bar) solid var(--p); }
  .card.r-b { border-top:var(--border-accent-bar) solid var(--b); }
  .card.e-s  { border-style:dashed; }
  .card.e-sh { border-left:var(--border-box-rule) solid var(--box-def-rule); }
  .card .c-t { display:block; font-size:var(--fs-micro); font-weight:700; letter-spacing:-.01em; }
  .card .c-m { display:block; font-size:var(--fs-micro); color:var(--muted); margin-top:2px; }
  .card .c-m code { background:var(--code-bg); padding:0 3px; border-radius:3px; }
  .card .star { color:var(--accent); }
  /* ── "By model" map-first view (Option C): F1 as the nav + a detail rail + a no-JS static hierarchy ── */
  #view-model .blurb { max-width:1080px; margin:0 auto 8px; }
  .mapfig { display:block; width:100%; height:auto; max-width:960px; margin:4px auto 2px; }
  .mapfig .node { cursor:pointer; }
  .mapfig .node rect { transition:stroke-width .1s; }
  .mapfig .node:hover rect, .mapfig .node.sel rect { stroke-width:3; }
  .mapfig .node:focus { outline:none; }
  .mapfig .node:focus-visible rect { stroke-width:3.4; }
  .detail-rail { max-width:1080px; margin:12px auto 0; border:var(--border-hairline) solid var(--rule);
                 background:var(--panel); border-radius:var(--radius-code); padding:12px 15px; min-height:92px; }
  .detail-rail .dr-k { font-family:var(--font-mono); font-size:var(--fs-micro); letter-spacing:.1em;
                       text-transform:uppercase; color:var(--muted); }
  .detail-rail .dr-t { font-size:var(--fs-card-body); font-weight:700; margin:1px 0 2px; }
  .detail-rail .dr-b { font-size:var(--fs-micro); color:var(--muted); margin:0 0 6px; max-width:92ch; }
  .mrow { display:flex; flex-wrap:wrap; gap:5px; margin:2px 0 4px; }
  .mcard { display:inline-block; text-decoration:none; color:var(--ink); border:var(--border-hairline) solid var(--rule);
           border-radius:var(--radius-chip); padding:5px 9px; background:var(--paper); font-size:var(--fs-micro); }
  .mcard:hover { border-color:var(--accent); background:var(--accent-tint); }
  .mcard.model { border-top:var(--border-accent-bar) solid var(--box-def-rule); }
  .mcard.xlink { border-style:dashed; color:var(--muted); background:var(--panel); }
  .mcard .star { color:var(--accent); font-weight:700; }
  a.chip { display:inline-block; font-size:var(--fs-micro); color:var(--ink); text-decoration:none; background:var(--panel);
           border:var(--border-hairline) solid var(--rule); border-radius:var(--radius-code); padding:3px 8px; }
  a.chip:hover { border-color:var(--accent); color:var(--accent); background:var(--accent-tint); }
  .chip-label { display:block; font-size:var(--fs-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:8px 0 2px; }
  #model-static { max-width:1080px; margin:16px auto 0; }
  #model-static .spine-sec { margin:16px 0 0; }
  #model-static h2 { font-size:var(--fs-section); margin:14px 0 4px; padding-bottom:3px; border-bottom:var(--border-hairline) solid var(--line); }
  #model-static h2 .sh-sub { font-weight:400; font-size:var(--fs-micro); color:var(--muted); }
  #model-static h3 { font-size:var(--fs-card-body); margin:12px 0 2px; }
  #model-static .node-sec { border-left:var(--border-accent-bar) solid var(--rule); padding-left:12px; margin:8px 0; }
  #model-static .n-sub { font-size:var(--fs-meta); color:var(--muted); margin:1px 0 2px; }
  #model-static .lbl { font-size:var(--fs-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:6px 0 0; }
  #model-static ul { margin:2px 0 6px; padding-left:20px; }
  #model-static li { font-size:var(--fs-meta); margin:2px 0; }
  #model-static .spine-anchor { font-size:var(--fs-meta); color:var(--muted); margin:2px 0 6px; }
  #model-static .star { color:var(--accent); }
  #model-static .xtag { font-size:var(--fs-micro); color:var(--muted); font-style:italic; }
  .spine-sec.fleet h2 { color:var(--b); } .spine-sec.product h2 { color:var(--p); } .spine-sec.trunk h2 { color:var(--accent); }
"""

VIEWS_JS = r"""
const ROLE_ORDER = ["Agent","Bridge","Product"];
const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
// The By-move headings pair each Move bucket with its one-line Alignment-Thesis gloss (prevent / detect / both).
const MOVE_DESC = {
  "constraint":"prevents the class, costs no iteration",
  "sensor":"detects after the fact, costs an iteration",
  "package":"both, bundled",
};
const moveHeading = k => esc(k)+' <span class="gloss">— '+esc(MOVE_DESC[k]||"n/a")+'</span>';
// The card-grid views (rendered into #stage). "By model" (id:"model") is handled specially below —
// its content is the F1 map + a detail rail + a static hierarchy, already present in #view-model.
const VIEWS = [
  { id:"family",  label:"By role & family", blurb:"The logical view — the structural inventory, grouped as it ships.", key:c=>c.role+" · "+c.family, order:null },
  { id:"enf",     label:"By enforcement",   blurb:"soft (probabilistic, cannot block) → soft·hard → hard (deterministic).", key:c=>c.enforcement, order:["Soft","Soft·Hard","Hard"] },
  { id:"move",    label:"By move",          blurb:"The Alignment-Thesis axis — how a control holds its goal: constraint (prevent) → sensor (detect) → package (both, bundled).", key:c=>c.move, order:["constraint","sensor","package"], heading:moveHeading },
  { id:"form",    label:"By form",          blurb:"The nine recurring shapes a control takes.", key:c=>c.form, order:null },
];
const roleCls = c => c.role==="Agent"?"r-a":c.role==="Product"?"r-p":"r-b";
const enfCls  = c => c.enforcement==="Hard"?"e-h":c.enforcement==="Soft"?"e-s":"e-sh";
const attr = s => (s||"").replace(/&/g,"&amp;").replace(/"/g,"&quot;");
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
      '<section class="grp"><h2>'+(v.heading?v.heading(k):label(k))+' <span class="cnt">('+cs.length+')</span></h2>'
      + '<div class="cards">'+cs.map(renderForView).join("")+'</div></section>').join("");
}
// ── the "By model" detail rail — driven by the F1 map's nodes ──
const rail = document.getElementById("model-rail");
function modelCard(m){
  const lead = m.cross ? '⇆ ' : (m.star ? '<span class="star">★</span> ' : '');
  return '<a class="mcard '+(m.cross?"xlink":"model")+'" href="'+attr(m.href)+'">'
       + '<span class="t">'+lead+esc(m.t)+'</span></a>';
}
function showModelGroup(k){
  const g = MODEL_GROUPS[k]; if(!g || !rail) return;
  document.querySelectorAll("#modelmap .node").forEach(n=>{
    const on = n.dataset.k===k;
    n.classList.toggle("sel", on);
    n.setAttribute("aria-pressed", on ? "true" : "false");
  });
  const models = g.models.map(modelCard).join("");
  const mechs  = g.mechs.map(m=>'<a class="chip" href="'+attr(m.href)+'">'+esc(m.t)+'</a>').join("");
  const mechLbl = g.trunk ? (g.mechs.length+" method mechanisms — govern every model")
                          : (g.mechs.length+" mechanisms filed here");
  rail.innerHTML =
      '<div class="dr-k">'+esc(g.kick)+'</div>'
    + '<div class="dr-t">'+esc(g.t)+'</div>'
    + '<div class="dr-b">'+esc(g.b)+'</div>'
    + (models ? '<div class="chip-label">Models plugged in</div><div class="mrow">'+models+'</div>' : '')
    + (mechs  ? '<div class="chip-label">'+mechLbl+'</div><div class="mrow">'+mechs+'</div>' : '');
}
function setView(id){
  document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on", t.dataset.v===id));
  const vm = document.getElementById("view-model"), st = document.getElementById("stage");
  if(id==="model"){ vm.hidden=false; st.hidden=true; }
  else { vm.hidden=true; st.hidden=false; renderView(VIEWS.find(v=>v.id===id)); }
}
document.querySelectorAll(".tab").forEach(t=>t.addEventListener("click", ()=>setView(t.dataset.v)));
// Progressive enhancement: upgrade the decorative F1 map into an interactive, keyboard-operable nav.
// (Without JS the SVG stays aria-hidden and #model-static carries the accessible hierarchy.)
(function(){
  const svg = document.getElementById("modelmap");
  const stat = document.getElementById("model-static");
  if(!svg){ return; }
  svg.removeAttribute("aria-hidden");
  svg.setAttribute("role","group");
  svg.setAttribute("aria-label","Model map — activate a lifecycle, a view, or the method trunk to see the models and mechanisms grouped under it");
  if(rail) rail.hidden = false;
  if(stat) stat.hidden = true;
  svg.querySelectorAll(".node").forEach(n=>{
    const g = MODEL_GROUPS[n.dataset.k]; if(!g) return;
    n.setAttribute("role","button");
    n.setAttribute("tabindex","0");
    n.setAttribute("aria-pressed","false");
    n.setAttribute("aria-label", g.t+" — "+g.b);
    n.addEventListener("click", ()=>showModelGroup(n.dataset.k));
    n.addEventListener("keydown", e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); showModelGroup(n.dataset.k); } });
  });
  showModelGroup("l1");
})();
setView("model");
"""


def _governed_by_block(e: Entry, entries: list[Entry], rel_root: str) -> str:
    """The derived "Governed by" block appended to an is-a-model entry page. Inverts the `Governs` join:
    every governs-a-model entry whose `Governs` names this model's slug (a direct governor) or `all-models`
    (a trunk mechanism that governs every model). Rendered at build time from the metadata — never a
    hand-maintained back-link, so it cannot drift from the forward edges."""
    if e.model != "is-a-model":
        return ""
    direct, trunk = [], []
    for g in entries:
        if not g.governs:
            continue
        if e.slug in g.governs:
            direct.append(g)
        elif GOVERNS_ALL in g.governs:
            trunk.append(g)
    if not direct and not trunk:
        return ""

    def li(g: Entry, all_models: bool) -> str:
        href = _attr(rel_root + _md_link_rewrite(g.path))
        badge = ' <span class="gb-all">governs every model</span>' if all_models else ""
        summ = f" — {_esc(g.summary)}" if g.summary else ""
        return f'<li><a href="{href}">{_esc(g.title_only())}</a>{summ}{badge}</li>'

    rows = "".join(li(g, False) for g in sorted(direct, key=lambda x: x.title_only()))
    rows += "".join(li(g, True) for g in sorted(trunk, key=lambda x: x.title_only()))
    note = ("The mechanisms that hold this model true — inverted from their <code>Governs</code> edges at "
            "build time, never hand-written. A direct governor names this model; a trunk mechanism governs "
            "every model.")
    return ('\n<section class="govby" aria-labelledby="gb-h">\n'
            '<h2 id="gb-h">Governed by</h2>\n'
            f'<p class="gb-note">{note}</p>\n'
            f'<ul class="gb-list">{rows}</ul>\n</section>\n')


_SPINE_KICK = {"fleet": "Fleet spine · lifecycle model", "product": "Product spine · 4+1 view",
               "trunk": "Tier 2 · the method trunk"}
_SPINE_HEAD = {
    "fleet": ("The fleet", "the self-operate lifecycle models — Part 2's spine"),
    "product": ("The product", "the 4+1 views of the shipped system — Part 3's spine"),
    "trunk": ("The method trunk", "governs every model in both spines"),
}


def _model_view(entries: list[Entry]) -> tuple[str, str]:
    """Build the "By model" view: the F1 map's detail-rail data (JS) + the no-JS static hierarchy (HTML).
    Both project over the real entries via the NODE_MAP grouping — titles/summaries/links come from the
    entries, only the grouping is the audit's map. Returns (static_hierarchy_html, model_groups_json)."""
    by_slug = {e.slug: e for e in entries}

    def resolve(slug: str, cross: bool = False) -> dict | None:
        e = by_slug.get(slug)
        if e is None:
            return None
        return {"t": e.title_only(), "href": _md_link_rewrite(e.path), "sum": e.summary,
                "star": e.model == "is-a-model", "cross": cross}

    # (1) the rail groups (consumed by showModelGroup in VIEWS_JS)
    groups: dict[str, dict] = {}
    for n in MODEL_NODES:
        models = [r for r in (resolve(s) for s in n["models"]) if r]
        models += [r for r in (resolve(s, cross=True) for s in n["cross"]) if r]
        mechs = [r for r in (resolve(s) for s in n["perim"]) if r]
        groups[n["k"]] = {"kick": _SPINE_KICK[n["spine"]], "t": n["title"], "b": n["sub"],
                          "models": models, "mechs": mechs, "trunk": n["spine"] == "trunk"}

    # (2) the static hierarchy — the accessible, no-JS fallback (headings + link lists)
    def li_model(r: dict) -> str:
        lead = "⇆ " if r["cross"] else ('<span class="star">★</span> ' if r["star"] else "")
        tail = ' <span class="xtag">shared by projection</span>' if r["cross"] else ""
        summ = f" — {_esc(r['sum'])}" if r["sum"] else ""
        return f'<li>{lead}<a href="{_attr(r["href"])}">{_esc(r["t"])}</a>{tail}{summ}</li>'

    def li_mech(r: dict) -> str:
        summ = f" — {_esc(r['sum'])}" if r["sum"] else ""
        return f'<li><a href="{_attr(r["href"])}">{_esc(r["t"])}</a>{summ}</li>'

    def node_block(n: dict) -> str:
        g = groups[n["k"]]
        parts = [f'<section class="node-sec"><h3>{_esc(n["title"])}</h3>'
                 f'<p class="n-sub">{_esc(n["sub"])}</p>']
        if g["models"]:
            parts.append('<p class="lbl">Models plugged in</p><ul>'
                         + "".join(li_model(r) for r in g["models"]) + "</ul>")
        if g["mechs"]:
            lbl = "The method mechanisms — govern every model" if n["spine"] == "trunk" \
                else "Perimeter — filed under this " + ("view" if n["spine"] == "product" else "lifecycle")
            parts.append(f'<p class="lbl">{lbl}</p><ul>'
                         + "".join(li_mech(r) for r in g["mechs"]) + "</ul>")
        parts.append("</section>")
        return "".join(parts)

    static_parts = []
    for spine in ("fleet", "product", "trunk"):
        h, sub = _SPINE_HEAD[spine]
        static_parts.append(f'<section class="spine-sec {spine}"><h2>{_esc(h)} '
                            f'<span class="sh-sub">— {_esc(sub)}</span></h2>')
        if spine == "fleet":
            anchor = resolve(FLEET_ANCHOR_SLUG)
            if anchor:
                static_parts.append(
                    f'<p class="spine-anchor">Anchored by <span class="star">★</span> '
                    f'<a href="{_attr(anchor["href"])}">{_esc(anchor["t"])}</a> — {_esc(anchor["sum"])}</p>')
        for n in MODEL_NODES:
            if n["spine"] == spine:
                static_parts.append(node_block(n))
        static_parts.append("</section>")
    static_html = '<div id="model-static">\n' + "\n".join(static_parts) + "\n</div>"
    return static_html, json.dumps(groups, ensure_ascii=False)


def build_views_page(entries: list[Entry]) -> str:
    stars = {os.path.normpath(r["path"]) for fam in parse_census() for r in fam["rows"] if r["star"]}
    cards = []
    for e in entries:
        d = e.as_dict()
        cards.append({
            "title": d["title"], "html": _md_link_rewrite(e.path),
            "role": d["role"], "family": d["family"], "form": d["form"],
            "move": d["move"], "enforcement": d["enforcement"],
            "summary": d["summary"], "star": e.path in stars,
        })
    static_html, groups_json = _model_view(entries)
    mapfig = _inline_svg("assets/model-map.svg")
    head = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>Governance catalogue — codegen'd views</title>\n{FONTS_LINK}\n"
            f"<style>{VIEWS_CSS}{FONT_CSS}</style>\n</head>\n<body>\n")
    # Tabs are rendered server-side (so they exist without JS); "By model" is the default. The card-based
    # views (family/enf/form) render into #stage on demand; the model view lives in #view-model.
    tabs = ('<button type="button" class="tab on" data-v="model">By model</button>'
            '<button type="button" class="tab" data-v="family">By role &amp; family</button>'
            '<button type="button" class="tab" data-v="enf">By enforcement</button>'
            '<button type="button" class="tab" data-v="move">By move</button>'
            '<button type="button" class="tab" data-v="form">By form</button>')
    model_blurb = ('Two organizing spines over one method trunk: the fleet\'s <b>lifecycle models</b> and the '
                   'product\'s <b>4+1 views</b>, with the sub-models that plug into each and the perimeter '
                   'grouped under the model it serves. Activate a node on the map — or read the full hierarchy '
                   'below. ★ = an is-a-model entry; ⇆ = a model shared across spines by projection.')
    body = ("<h1>Governance catalogue — codegen'd views</h1>\n"
            f'<p class="sub">The same {len(entries)} mechanisms, re-grouped live from card metadata. Every card is emitted by '
            '<code>renderForView(card)</code>; a view is just a grouping key + order, so <b>adding a mechanism or a '
            'view is data, not layout</b>. Click a card for its writeup; hover for its one-line summary. '
            '&nbsp;·&nbsp; <a href="catalogue-figure.html">the governance map</a> '
            '&nbsp;·&nbsp; <a href="book-models/models-view.html">the book models</a> '
            '&nbsp;·&nbsp; <a href="development-workflow.html">the development process</a> '
            '&nbsp;·&nbsp; <a href="index.html">home</a></p>\n'
            f'<div id="tabs">{tabs}</div>\n'
            '<section id="view-model" aria-label="By model">\n'
            f'<p class="blurb">{model_blurb}</p>\n'
            f'{mapfig}\n'
            '<div id="model-rail" class="detail-rail" aria-live="polite" hidden></div>\n'
            f'{static_html}\n'
            '</section>\n'
            '<div id="stage" hidden></div>\n')
    script = ("<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n"
              + "const MODEL_GROUPS = " + groups_json + ";\n" + VIEWS_JS + "</script>\n")
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
_MD_CENSUS_FILES = ("README.md", "INDEX.md", "CLAUDE.md", os.path.join("models-bridge", "README.md"),
                    "constructing-the-gee.md")
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


# CLOSED, monotonically-growing tuple of build-time markdown-directive fragments that must NEVER survive
# into a served page. `render_md` consumes each — it strips the `<!-- summary: … -->` metadata line and the
# `<!-- prior-art: … -->` provenance notes, unwraps `<!--census:KEY-->V<!--/census-->` to its value V, and
# drops the adoption sentinels — so a served page carries none of them. Both the raw `<!--x` and the
# HTML-escaped `&lt;!--x` forms are listed because a stray comment that reaches block parsing is ESCAPED into
# visible text, not passed through (the `constructing-the-gee.html` `--census` / `--summary` leak this gate
# exists to make impossible). GROW this tuple whenever a new build-time directive is added; never shrink it.
_LEAKED_MARKER_FRAGMENTS: tuple[str, ...] = (
    "<!--census", "&lt;!--census",
    "<!--/census", "&lt;!--/census",
    "<!-- summary:", "&lt;!-- summary:",
    "<!-- prior-art:", "&lt;!-- prior-art:",
    "<!--adoption-source", "&lt;!--adoption-source",
    "<!--adoption-auto", "&lt;!--adoption-auto",
    "<!--adoption-interactive", "&lt;!--adoption-interactive",
)


def check_leaked_markers() -> list[str]:
    """Served-page post-condition sensor: no build-time markdown directive may survive into a built page.
    Walk every served `.html` (catalogue entries, the standalone prose pages, and the book) and flag any
    fragment from the closed `_LEAKED_MARKER_FRAGMENTS` tuple. `render_md` consumes each directive, so a hit
    means one leaked un-rendered — the `constructing-the-gee.html` `--census` / `--summary` class. Twin of
    `check_census_tokens`, which guards the source counts; this guards the rendered output. Rule-#17 shape:
    a served-page invariant asserted as a mechanical closed-tuple check, not re-inspected by eye."""
    prune = site_prune_dirs()
    problems: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in prune]
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            txt = open(path, encoding="utf-8").read()
            for frag in _LEAKED_MARKER_FRAGMENTS:
                if frag in txt:
                    problems.append(f"{rel}: un-rendered marker {frag!r} leaked into the served page "
                                    f"— render_md must consume it (run `catalog.py build`)")
    return sorted(problems)


# ── Leaked-inline-markdown sensor ────────────────────────────────────────────────────────────────────
# A render path that emits authored text WITHOUT its inline-markdown pass (the book's `inline` / Typst's
# `inline_typst`) ships the raw `*em*` / `**strong**` / `` `code` `` / `[t](url)` syntax as literal glyphs
# in reader-visible text — the "why are there asterisks on my page" leak. The 260804 instance was the
# Appendix-C brick summaries + the code-span-in-title contexts (page `<h1>`, nav TOC, stack legend). The
# rendered inline pass turns each form into an element, so its DELIMITERS vanish from the text nodes; a
# surviving delimiter in a reader-visible text node means the pass was skipped for that render path.
#
# Elements whose text is NOT prose (so a bare `*`/backtick there is legitimate, not a leak) are skipped:
# a `<code>`/`<pre>` holds literal source, an `<svg>` holds diagram internals, `<script>`/`<style>` hold
# code, and `<title>`/`<head>` hold the tab/meta text the renderer PLAIN-strips (no markup allowed there).
_LEAK_SKIP_TAGS = frozenset({"code", "pre", "script", "style", "svg", "title", "head", "noscript"})

# The four inline forms, detected with the SAME shape the book's `inline` converts — a match in already-
# rendered text is syntax the pass would have consumed, so it leaked. The italic pattern keeps `inline`'s
# word-boundary guards so a lone `*` or an `a * b` arithmetic run is NOT flagged (no false positive).
_LEAK_MD_PATTERNS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("strong (**…**)", re.compile(r"\*\*(?=\S).+?(?<=\S)\*\*")),
    ("code (`…`)", re.compile(r"`[^`]+`")),
    ("link ([text](url))", re.compile(r"\[[^\]]+\]\([^)]+\)")),
    ("emphasis (*…*)", re.compile(r"(?<![\w*])\*(?!\s)[^*]+?(?<!\s)\*(?![\w*])")),
)


class _VisibleProseExtractor(HTMLParser):
    """Collect the reader-visible PROSE text of an HTML page — every text node NOT inside a
    `_LEAK_SKIP_TAGS` element. A single depth counter suppresses text while any skip element is open
    (nesting-safe: it counts every skip-tag open/close, so a `<title>` inside an `<svg>` still balances)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in _LEAK_SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _LEAK_SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self.chunks.append(data)


def check_leaked_inline_markdown() -> list[str]:
    """Served-page post-condition sensor (book surface): no inline-markdown syntax may survive un-rendered
    into reader-visible prose. Parse every built `book/*.html`, extract the prose text nodes (skipping code /
    diagram / head contexts), and flag any `*em*` / `**strong**` / `` `code` `` / `[t](url)` the inline pass
    should have consumed. A hit means a render path emitted authored text without `inline` / `inline_typst`
    (the 260804 brick-summary + code-span-title class). Twin of `check_leaked_markers` (build-directive leaks)
    — this guards inline-markup leaks. Returns one problem string per (file, form, snippet)."""
    problems: list[str] = []
    for path in sorted(glob.glob(os.path.join(ROOT, "book", "*.html"))):
        rel = os.path.relpath(path, ROOT)
        parser = _VisibleProseExtractor()
        parser.feed(open(path, encoding="utf-8").read())
        seen: set[tuple[str, str]] = set()
        for chunk in parser.chunks:
            for form, pat in _LEAK_MD_PATTERNS:
                m = pat.search(chunk)
                if m and (form, m.group(0)) not in seen:
                    seen.add((form, m.group(0)))
                    snippet = " ".join(chunk.split())[:80]
                    problems.append(f"{rel}: un-rendered {form} in reader-visible prose "
                                    f"{m.group(0)!r} — route this text through `inline` / `inline_typst` "
                                    f"(context: {snippet!r})")
    return sorted(problems)


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
            body = render_md(md) + _governed_by_block(e, entries, rel_root)
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
    # landing index.html = a projection of the Big-Ideas model (hero + six slots + the closing conclusion +
    # three ways-in buttons), then the census and the quiet vocabulary/definitions/outcomes reference strip
    # then the end-of-body progressive-enhancement script. Every Big-Idea slot is rendered from
    # book-models/landing-big-ideas.json; figures splice as bare responsive <svg> with their internal
    # ids namespaced per slot (_ns_svg_ids) so no two figures collide (check_no_duplicate_ids).
    # The landing ENDS at the closing CTA + the three ways-in cards — no on-landing census enumeration
    # and no back-matter reference strip. The entries' inbound links (for the reachability gate) come from
    # catalogue-views.html (the "Full catalogue" card target), which enumerates every entry.
    # The hero carries NO cover figure — the Big Idea 1 churn flowchart is the landing's lead visual now.
    landing_body = (NAV_GRID + "\n" + LANDING_INTRO.format(
        book_title_block=_book_title_block(),
        big_ideas=_landing_big_ideas(),
        closing=_landing_closing(),
    ) + "\n" + EXPAND_JS)
    landing = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
               f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
               f"<title>Agent Governance Mechanisms</title>\n{FONTS_LINK}\n"
               f"<style>{PAGE_CSS}{LANDING_CSS}{FONT_CSS}</style>\n</head>\n"
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
    # Un-rendered-marker gate (BLOCKING): a build-time directive that survived into a served page (the
    # `constructing-the-gee.html` `--census` / `--summary` leak). Scans the freshly-written HTML (catalogue +
    # book), so it can't drift. Twin of the source-side check_census_tokens; wired here AND in validate.
    leaked = check_leaked_markers()
    if leaked:
        print(f"LEAKED MARKERS ({len(leaked)}) — a build-time directive survived into a served page:",
              file=sys.stderr)
        for m in leaked:
            print(f"  - {m}", file=sys.stderr)
        print("  Fix: ensure render_md consumes the directive (strip/unwrap it before block parsing).",
              file=sys.stderr)
        return 1
    # Leaked-inline-markdown gate (BLOCKING): a render path that emitted authored text without its inline
    # pass ships literal `*em*` / `` `code` `` / `[t](url)` into reader-visible book prose (the 260804
    # brick-summary + code-span-title class). Scans the freshly-built book HTML, so it can't drift.
    leaked_md = check_leaked_inline_markdown()
    if leaked_md:
        print(f"LEAKED INLINE MARKDOWN ({len(leaked_md)}) — authored text reached a page without its "
              f"inline pass:", file=sys.stderr)
        for m in leaked_md:
            print(f"  - {m}", file=sys.stderr)
        print("  Fix: route the offending render path's text through `inline` (HTML) / `inline_typst` "
              "(PDF), or `_plain` for a `<title>`/aria attribute.", file=sys.stderr)
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


def cmd_claims(args) -> int:
    """The PRE-EDIT CONSULT — print the claims a chapter asserts and their contradiction predicates, so an
    agent editing that chapter's prose can confirm its edit negates no listed stance (the claims model's
    forward-facing use; book/_design/book-claims-model-260801.md §4.2). Reads the claims model
    (book-models/claims.json via claims_model). `--json` dumps the resolved claim records."""
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    import claims_model as clm  # noqa: E402 — book-model package (carries its own book_ir path setup)
    hits = clm.claims_for_chapter(args.chapter)
    if args.json:
        from dataclasses import asdict  # noqa: E402 — local dump only
        print(json.dumps([asdict(c) for c in hits], ensure_ascii=False, indent=2))
        return 0
    return clm.consult(args.chapter)


def _spine_health(s: dict) -> str:
    """A compact per-claim health suffix for the spine listing — the depth + overmapping + freshness sensors
    surfaced from the generated artifact's derived fields. Empty when the claim is healthy."""
    tags = []
    if s.get("exempt"):
        tags.append(f"exempt:{s['exempt']}")
    elif not s.get("advanced_by"):
        tags.append("GAP")
    elif s.get("front_loaded"):
        tags.append("front-loaded")
    if s.get("overmapped"):
        tags.append("OVERMAPPED")
    if s.get("fresh") is False:
        tags.append("STALE")
    return f"  [{'; '.join(tags)}]" if tags else ""


def cmd_spine(args) -> int:
    """Query the argument-spine model (book-models/argument-spine.json) — the book's linear argument as an
    ordered run of claims, each labeled with the chapters that advance it. Three modes, mirroring the
    claims/concepts siblings: no arg lists the 14 claims in order with advance-counts; a CLAIM-ID prints
    that claim's statement and the chapters that advance it (`advanced_by`); a CHAPTER-SLUG (or number
    prefix, e.g. 3.1) prints that chapter and the claims it advances. Reads the GENERATED artifact — run
    `python3 book-models/argument_spine_model.py regenerate` if it is stale. `--json` dumps the raw match."""
    art = _load_json_or_none(os.path.join(ROOT, "book-models", "argument-spine.json"))
    if art is None:
        print("no book-models/argument-spine.json — run "
              "`python3 book-models/argument_spine_model.py regenerate`")
        return 0
    spine = art.get("spine", [])
    chapters = art.get("chapters", [])
    by_id = {s["id"]: s for s in spine}

    target = getattr(args, "target", None)
    if not target:
        if args.json:
            print(json.dumps(spine, ensure_ascii=False, indent=2))
            return 0
        print("== the argument spine (14 claims in order) ==")
        for s in sorted(spine, key=lambda s: s["order"]):
            n = len(s.get("advanced_by", []))
            print(f"{s['order']:>3}. {s['id']:34} advanced by {n:>2} chapter(s){_spine_health(s)}")
            print(f"       {s['statement']}")
        return 0

    # A claim id wins over a chapter slug (ids are kebab, slugs are number-prefixed — no collision).
    if target in by_id:
        s = by_id[target]
        if args.json:
            print(json.dumps(s, ensure_ascii=False, indent=2))
            return 0
        seeds = f" [seeds {','.join(map(str, s.get('seeds', [])))}]" if s.get("seeds") else ""
        print(f"claim {s['order']}. {s['id']}{seeds}{_spine_health(s)}")
        print(f"  {s['statement']}")
        adv = s.get("advanced_by", [])
        print(f"  advanced by ({len(adv)}, body-depth {s.get('body_depth', 0)}): "
              f"{', '.join(adv) if adv else '— none'}")
        return 0

    # Chapter slug — exact, or a unique number/slug prefix (3.1 -> 3.1-the-executable-zoo).
    matches = [c for c in chapters if c["slug"] == target] or \
              [c for c in chapters if c["slug"].startswith(target)]
    if len(matches) == 1:
        c = matches[0]
        if args.json:
            print(json.dumps(c, ensure_ascii=False, indent=2))
            return 0
        exempt = f"  (exempt: {c['exempt']})" if c.get("exempt") else ""
        print(f"chapter {c['slug']}{exempt}")
        adv = c.get("advances", [])
        if not adv:
            print("  advances no spine claim")
            return 0
        print(f"  advances ({len(adv)}):")
        for sid in adv:
            stmt = by_id.get(sid, {}).get("statement", "?")
            print(f"    {sid} — {stmt}")
        return 0
    if len(matches) > 1:
        print(f"'{target}' matches {len(matches)} chapters: {', '.join(c['slug'] for c in matches)}")
        return 1
    print(f"'{target}' is neither a spine claim id nor a chapter slug. "
          f"Run `python3 catalog.py spine` to list the claims.")
    return 1


def cmd_litpos(args) -> int:
    """Query the literature-positioning model (book-models/lit-positioning.json) — the Literature-Positioning
    Pass as an ordered set of X→Y→Z interventions, each with its citations nested under the argument spine.
    No arg lists the interventions + the planned-vs-landed burndown; an INTERVENTION-ID or §N prints that
    intervention's X/Y/Z frame + its citations (key · relation · backed spine claims). Reads the GENERATED
    artifact — run `python3 book-models/lit_positioning_model.py regenerate` if it is stale. `--json` dumps
    the raw matched record(s)."""
    art = _load_json_or_none(os.path.join(ROOT, "book-models", "lit-positioning.json"))
    if art is None:
        print("no book-models/lit-positioning.json — run "
              "`python3 book-models/lit_positioning_model.py regenerate`")
        return 0
    ivs = art.get("interventions", [])
    target = getattr(args, "target", None)
    if not target:
        if args.json:
            print(json.dumps(ivs, ensure_ascii=False, indent=2))
            return 0
        landed = [iv for iv in ivs if iv.get("status") == "landed"]
        print(f"== literature-positioning ({len(ivs)} interventions, {len(landed)} landed) ==")
        for iv in ivs:
            fold = f"; fold:{iv['fold_target']}" if iv.get("fold_target") else ""
            pend = sum(1 for c in iv.get("citations", []) if not c.get("resolves_bib"))
            print(f"{iv.get('section',''):4} {iv['id']:34} [{iv.get('status','?')}{fold}] "
                  f"{len(iv.get('citations', []))} cite(s) ({pend} pending bib)")
            print(f"       advances {', '.join(iv.get('advances_theses', []))}")
        return 0
    match = next((iv for iv in ivs if iv["id"] == target or iv.get("section") == target), None)
    if match is None:
        print(f"'{target}' is neither an intervention id nor a §N section. "
              f"Run `python3 catalog.py litpos` to list them.")
        return 1
    if args.json:
        print(json.dumps(match, ensure_ascii=False, indent=2))
        return 0
    fold = f"; fold:{match['fold_target']}" if match.get("fold_target") else ""
    print(f"== {match.get('title','')} ({match['id']}, {match.get('section','')}) "
          f"[{match.get('status','?')}{fold}] ==")
    print(f"  X (lineage):   {match.get('x','')}")
    print(f"  Y (frontier):  {match.get('y','')}")
    print(f"  Z (MAGE move): {match.get('z','')}")
    print(f"  advances theses: {', '.join(match.get('advances_theses', []))}")
    print(f"  target locations: {', '.join(match.get('target_locations', []))}")
    print("  citations (nested under the spine):")
    for c in match.get("citations", []):
        bibtag = "" if c.get("resolves_bib") else "  [PENDING in references.bib]"
        print(f"    · {c['key']}  [{c.get('relation','?')}]{bibtag}")
        print(f"        backs: {', '.join(c.get('backs_claims', []))}")
    return 0


def cmd_substantiation(args) -> int:
    """The UNIFIED SUBSTANTIATION query — data-claims + literature-positioning citations nested UNDER the
    argument spine. Per spine claim: its statement, `data_backing` (metric->claim ledger), and
    `literature_backing` (the citations whose backs_claims include it), then two reports: DL3
    UNDERQUANTIFIED (a quantifiable claim with no data) and UNDER-SUBSTANTIATED-OR-SITUATED (a reality-claim
    with neither data nor literature). Reads three meta-files at query time (argument spine + data-claims +
    lit-positioning); robust to lit-positioning not yet existing. `--json` dumps the machine form."""
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    import substantiation as sub  # noqa: E402 — book-model aggregator, reads meta-files at query time
    return sub.render(as_json=args.json)


def cmd_delivers(args) -> int:
    """The DELIVERS coverage map — what each chapter HANDS THE READER: its concept(s) (DERIVED from the
    chapter's own `index-def` tags, never re-keyed) and its operational artifact(s) (hand-authored,
    typed ∈ ARTIFACT_TYPES). Prints one row per chapter (concepts · artifact types · verdict), then the two
    reports: DELIVERS-NEITHER (derived: a non-exempt chapter with no concept AND no artifact — the real gap
    alarm) and ALL-PROSE-WOULD-BENEFIT (the AUTHORED `artifact_would_help` flag — an operational chapter that
    describes an artifact in prose instead of showing it, never manufactured from an empty artifacts list).
    Reads the chapter-shape model at query time (rule-#33 stable form). `--json` dumps the machine map."""
    bm = os.path.join(ROOT, "book-models")
    if bm not in sys.path:
        sys.path.insert(0, bm)
    import chapter_shape_model as csm  # noqa: E402 — the per-chapter deliverable view-model

    model = csm.derive_model()
    flags = model.flags()

    def _verdict(c) -> str:
        if c.exempt:
            return f"exempt ({c.exempt})"
        if c.delivers.artifacts:
            return "A (artifact)" + ("  ⚠ all-prose-would-benefit" if c.delivers.artifact_would_help else "")
        if c.delivers.concepts:
            return "C (concept-only)" + ("  ⚠ all-prose-would-benefit" if c.delivers.artifact_would_help else "")
        return "N ⚠ DELIVERS-NEITHER"

    if args.json:
        print(json.dumps(csm.to_jsonable(model), ensure_ascii=False, indent=2))
        return 0

    print("== delivers — the per-chapter deliverable coverage map (concept OR artifact) ==")
    for c in model.chapters:
        types = ", ".join(a.type for a in c.delivers.artifacts) or "—"
        print(f"{c.slug:34} concepts:{len(c.delivers.concepts):<2} artifacts[{types}]")
        print(f"{'':34} {_verdict(c)}")
    print("\n== DELIVERS-NEITHER (derived: non-exempt, no concept AND no artifact — the real gap alarm) ==")
    print("  " + (", ".join(f["chapter"] for f in flags["delivers_neither"]) if flags["delivers_neither"]
                  else "none — every non-exempt chapter hands over a concept or an artifact"))
    print("== ALL-PROSE-WOULD-BENEFIT (authored flag: an artifact would sharpen an operational chapter) ==")
    print("  " + (", ".join(f["chapter"] for f in flags["all_prose_would_benefit"])
                  if flags["all_prose_would_benefit"]
                  else "none — no chapter is flagged as prose that an artifact would sharpen"))
    c = csm.to_jsonable(model)["_counts"]
    print(f"\n— {c['chapters_assessed']} chapters ({c['chapters_exempt']} exempt); "
          f"{c['chapters_with_artifact']} with an artifact, {c['chapters_concept_only']} concept-only; "
          f"{c['delivers_neither']} deliver-neither, {c['all_prose_would_benefit']} all-prose-would-benefit")
    return 0


def _load_json_or_none(path: str):
    return json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else None


# ── Deploy staging manifest ──────────────────────────────────────────────────
# `deploy github` stages an EXPLICIT set of paths — never `git add -A`, which sweeps any
# stray untracked file (a design-doc draft, a screenshot helper, a scratch `.mjs`) into a
# publish commit. Two gated moves: (1) every tracked modification/deletion via `git add -u`,
# which by definition never stages an untracked file; (2) NEW *derived build outputs* under
# the content roots, matched by extension.
#
# The extension set is DERIVED build outputs only. The build EMITS `.html` page renders (a
# sibling per `.md`, plus the census + book pages) and generated figures/data/bundles; it
# NEVER emits `.md`. A `.md` is always hand-authored SOURCE — a chapter, a design doc, a
# stray draft — so a new `.md` is NEVER auto-staged: source is the author's to `git add`
# deliberately, with its own commit message, not swept into a "rebuild site" commit. (A new
# design draft under `book/_design/` getting swept into a `deploy: rebuild site` commit —
# then reverted — is the exact incident this exclusion kills.) A brand-new chapter's rendered
# `.html` and a new build-generated figure ARE derived outputs and still stage; the chapter's
# source `.md` is reported for the author to add. Anything unmatched is reported, not committed.
_PUBLISHABLE_EXTS = ("html", "svg", "css", "js", "json",
                     "png", "jpg", "jpeg", "gif", "webp", "ico", "woff", "woff2", "ttf")
_CONTENT_ROOTS = ("agent", "models-bridge", "product", "book", "plugin", "assets")


def _is_publishable(path: str) -> bool:
    """True if a repo-relative NEW file is a DERIVED build output the deploy should stage: a
    generated artifact type (`.html`, figures, data, bundles — never `.md` source) under a
    content root. Hand-authored source (any `.md`: chapter, design doc, draft) and scratch of
    an unexpected type (a `.mjs` helper, a `.log`) fail this and are left for the human to add
    explicitly — deploy publishes the regenerated site, it does not author-commit source."""
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
    import lint_point_claim_word_cap as lpwc  # noqa: E402 — the drain's new point-form lints (audit-only)
    import lint_term_tags_registered as lttr  # noqa: E402
    import outcomes_model as ocm  # noqa: E402
    import outline_model as om  # noqa: E402
    import reverse_index as ri  # noqa: E402

    findings: list[str] = []

    # --- FRESHNESS: each materialized artifact must equal a fresh derivation. -------------------------
    freshness = [
        ("outline.json", om.load_artifact(), om.to_jsonable(om.derive_outline()),
         ("chapters", "_counts")),
        ("outcomes.json", ocm.load_artifact(), ocm.to_jsonable(ocm.derive_model()),
         ("outcomes", "_counts", "hierarchy")),
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

    # --- The DELIVERS coverage lens (DV1-DV4): the per-chapter deliverable model's structural findings
    # (artifact-type enum, concept-join integrity, artifact-anchor freshness, coverage). Folded here so a
    # committer sees delivers-drift in the one place they already look. AUDIT-ONLY-first (rule #55).
    import chapter_shape_model as csm  # noqa: E402 — the per-chapter deliverable view-model
    findings.extend(csm.delivers_findings())

    # --- The drain's NEW point-form lints (AUDIT-ONLY, landed here before the reform drains them). The
    # word-cap reports every point whose claim exceeds 10 words (~175 today — the whole old verbose corpus,
    # the reform's fix-worklist); term-tags-registered reports any tagged term not in the two-tier registry.
    # Both PRINT into this surface and, like the rest, only redden under `--strict` once the seed is drained.
    findings.extend(lpwc.findings())
    findings.extend(lttr.findings())

    # --- SITE-AS-PROJECTION drift: the site is a derived VIEW of the book's models, so its projection
    # drift (definitions.json ↔ the landing's def-* cards; outcomes.json/selection ↔ the outcome-* rows)
    # belongs in the same views-audit surface. See book-models/SITE-VIEW.md; checks in tests/html.py.
    from tests.html import (check_definitions_site, check_models_view_site,  # noqa: E402 — audit-time only
                            check_outcomes_site)
    for _label, (_status, _issues) in (("definitions", check_definitions_site()),
                                       ("outcomes-site", check_outcomes_site()),
                                       ("models-view", check_models_view_site())):
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
    # github ALWAYS renders the PDF pre-push as a BLOCKING gate (content-integrity + shipped-size ceiling),
    # so a bloated or broken PDF aborts the push before CI ever runs — mirroring what CI enforces on push.
    github_pdf_gate = args.target == "github"
    print(f"== Deploy plan: target={args.target} ==")
    print("  1. validate   2. build   3. test (BLOCKING — aborts on any failure)   "
          + ("3b. render PDF   " if want_pdf else "")
          + ("3b. render PDF + size/integrity gate (BLOCKING)   " if github_pdf_gate else "")
          + ("4. serve on localhost" if args.target == "local"
             else "4. commit + push to origin main (CI deploys)"))
    if getattr(args, "pdf", False) and args.target == "github":
        # The github path already renders the PDF as a pre-push gate, so an explicit --pdf adds nothing.
        print("  (note: --pdf is implied for github — the PDF is always rendered pre-push as a BLOCKING gate)")
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

    # opt-in local PDF render (the print-native Typst path; the default web build never touches it).
    # `--pdf` regenerates book/mage-book.pdf so the local preview's "Download PDF" link serves the CURRENT
    # book, not a stale gitignored copy. Publish (github) needs no flag — CI renders the PDF on every push.
    if want_pdf:
        print("\n== Rendering PDF (book/mage-book.pdf) via Typst; content-integrity gate runs internally ==")
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

    # --github PRE-PUSH PDF GATE (BLOCKING): render the PDF via the same `--pdf` path CI runs, which carries
    # the content-integrity gate AND the shipped-size ceiling (<= 8 MiB, measured post-repack). This refuses
    # to push a bloated PDF (e.g. a full-bleed rasterized cover regressing to 30+ MB) — the exact failure CI
    # renders on push. Mirrors the `local --pdf` abort pattern. CI still re-renders authoritatively on push.
    print("\n== Pre-push PDF gate (book/mage-book.pdf) via Typst; content-integrity + size ceiling (8 MiB) ==")
    pdf_gate = subprocess.run([sys.executable, os.path.join("book", "build_book_html.py"), "--pdf"],
                              cwd=ROOT)
    if pdf_gate.returncode != 0:
        print("ABORT: PDF gate failed — will not push (see build_book_html.py --pdf output above; "
              "a >8 MiB PDF or a content-integrity miss blocks the push).")
        return 1

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
    print(f"   Watch: {_REPO_ACTIONS_URL}")
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
    cl = sub.add_parser("claims", help="PRE-EDIT CONSULT: list the claims a chapter asserts + their contradiction predicates (book-models/claims.json). Run before editing a chapter's prose and confirm your edit negates no listed stance")
    cl.add_argument("chapter", help="chapter slug or number prefix (e.g. 3.1 or 3.1-the-executable-zoo)")
    cl.add_argument("--json", action="store_true", help="dump the resolved claim records")
    sp = sub.add_parser("spine", help="query the argument-spine model (book-models/argument-spine.json): no arg lists the 14 claims in order with advance-counts; a CLAIM-ID prints its statement + advancing chapters; a CHAPTER-SLUG prints the claims that chapter advances")
    sp.add_argument("target", nargs="?", help="a spine claim id (e.g. alignment-thesis) or a chapter slug / number prefix (e.g. 2.3 or 2.3-the-governed-environment); omit to list the whole spine")
    sp.add_argument("--json", action="store_true", help="dump the raw matched record(s)")
    lp = sub.add_parser("litpos", help="query the literature-positioning model (book-models/lit-positioning.json): no arg lists the X→Y→Z interventions + the planned-vs-landed burndown; an INTERVENTION-ID or §N prints its X/Y/Z frame + citations nested under the spine")
    lp.add_argument("target", nargs="?", help="an intervention id (e.g. fallible-oracles-swebench) or a §N section (e.g. §9); omit to list them all")
    lp.add_argument("--json", action="store_true", help="dump the raw matched record(s)")
    su = sub.add_parser("substantiation", help="the unified substantiation query: data-claims + lit-positioning citations nested under each argument-spine claim; flags UNDERQUANTIFIED (quantifiable, no data) + UNDER-SUBSTANTIATED-OR-SITUATED (reality-claim, no data AND no literature)")
    su.add_argument("--json", action="store_true", help="dump the machine form")
    dv = sub.add_parser("delivers", help="the per-chapter deliverable coverage map (concept OR artifact): one row per chapter (concepts DERIVED from index-def tags · authored artifact types · verdict), then DELIVERS-NEITHER (derived gap alarm) + ALL-PROSE-WOULD-BENEFIT (authored flag)")
    dv.add_argument("--json", action="store_true", help="dump the machine map (the chapter-shape model)")
    va = sub.add_parser("views-audit", help="book-models drift audit: structural (every view->md reference resolves) + freshness (each view artifact equals a fresh derivation). Fast pre-commit gate; AUDIT-ONLY (prints, exits 0) unless --strict")
    va.add_argument("--strict", action="store_true", help="exit 1 on any finding (the flip a follow-up wires into the hook once seed findings are drained)")
    sub.add_parser("install-hooks", help="git config core.hooksPath hooks (auto-regen on commit)")
    d = sub.add_parser("deploy", help="build, then serve locally (local) or publish to GitHub (github)")
    d.add_argument("target", choices=["local", "github"], help="local = serve on localhost; github = commit + push (CI deploys)")
    d.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"localhost port for --local (default {DEFAULT_PORT})")
    d.add_argument("--pdf", action="store_true", help="(local only) also render book/mage-book.pdf (print-native Typst path) so the local preview's Download-PDF link is current. Implied for github — the PDF is always rendered pre-push as a BLOCKING content-integrity + size (<=8 MiB) gate")
    d.add_argument("-m", "--message", default="deploy: rebuild site", help="commit message for github mode")
    args = p.parse_args()
    return {"validate": cmd_validate, "query": cmd_query, "summaries": cmd_summaries,
            "build": cmd_build, "test": cmd_test, "check-responsive": cmd_check_responsive,
            "check-console": cmd_check_console,
            "data-claims": cmd_data_claims, "concepts": cmd_concepts,
            "definitions": cmd_definitions, "outcomes-site": cmd_outcomes_site,
            "claims": cmd_claims, "spine": cmd_spine, "litpos": cmd_litpos,
            "substantiation": cmd_substantiation,
            "delivers": cmd_delivers,
            "views-audit": cmd_views_audit,
            "install-hooks": cmd_install_hooks, "deploy": cmd_deploy}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
