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
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FORMS = {
    "typed-ir", "validation", "repair-vocab", "agent-output", "bounded-service",
    "regression", "quality-gate", "observability", "audit-trail",
}
NOVELTY = {"novel", "notable", "standard"}
ROLES = {"Agent", "Bridge", "Product"}
ENF_CLASSES = {"Hard", "Soft", "Soft·Hard"}
META_ORDER = ["Target", "Form", "Novelty", "Real artifact", "Governing rule(s)", "Enforcement", "Summary"]
SUMMARY_MAX = 100  # chars — a tooltip-friendly gloss, deliberately shorter than Intent
SECTION_ORDER = [
    "Motivation", "Why it's not just", "Mechanism", "Prerequisites",
    "Consequences & costs", "Known uses", "Related controls",
]
REL_TAGS = ("Counterpart", "Enabler", "Layer", "Consumer", "Bridge", "See also")
ROLE_DIRS = ["agent", "models-bridge", "product"]


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

        rows = re.findall(r"^\| ([^|]+?) \| (.+?) \|$", t, re.M)
        self.meta = {k.strip(): v.strip() for k, v in rows if k.strip() in META_ORDER}
        labels = [k.strip() for k, _ in rows if k.strip() in META_ORDER]
        if labels != META_ORDER:
            self.issues.append(f"metadata rows/order = {labels or '(none)'}")

        self.form = None
        m = re.search(r"`([a-z-]+)`", self.meta.get("Form", ""))
        self.form = m.group(1) if m else None
        if self.form not in FORMS:
            self.issues.append(f"bad Form: {self.meta.get('Form', '(missing)')!r}")

        nov = self.meta.get("Novelty", "").strip("` ").split()
        self.novelty = nov[0] if nov else None
        if self.novelty not in NOVELTY:
            self.issues.append(f"bad Novelty: {self.meta.get('Novelty', '(missing)')!r}")

        tgt = self.meta.get("Target", "")
        m = re.match(r"(Agent|Bridge|Product) · \*?\*?(.+?)\*?\*?$", tgt)
        self.role = m.group(1) if m else None
        self.family = re.sub(r"\*", "", m.group(2)).strip() if m else None
        if self.role not in ROLES:
            self.issues.append(f"bad Target role: {tgt!r}")

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

        rel = t.split("## Related controls")[-1] if "## Related controls" in t else ""
        bullets = re.findall(r"^- (.+)$", rel, re.M)
        if not bullets:
            self.issues.append("no Related-controls bullets")
        elif not any(any(tag in b for tag in REL_TAGS) for b in bullets):
            self.issues.append("Related-controls: no relationship tags")

    def as_dict(self) -> dict:
        return {
            "path": self.path, "role": self.role, "family": self.family,
            "form": self.form, "novelty": self.novelty, "enforcement": self.enf,
            "summary": self.summary,
            "title": (re.search(r"^# (.+)$", self.text, re.M) or [None, self.path])[1],
        }


def all_entries() -> list[Entry]:
    paths = sorted(
        p for d in ROLE_DIRS for p in glob.glob(os.path.join(ROOT, d, "*", "*.md"))
    )
    return [Entry(p) for p in paths]


def check_links() -> list[str]:
    dead = []
    for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
        base = os.path.dirname(f)
        body = open(f, encoding="utf-8").read()
        for m in re.finditer(r"\]\(([^)]+\.md)(#[^)]*)?\)", body):
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
    rows = re.findall(
        r"^\| (?:✅|☐)[^|]*\| ([^|]+?) \| `([a-z-]+)` \| (\w+) \| ([^|]+?) \| \[[^\]]+\]\(([^)]+)\) \|$",
        idx, re.M,
    )
    problems = []
    for _ctrl, iform, inov, ienf, path in rows:
        e = by_path.get(os.path.normpath(path))
        if e is None:
            problems.append(f"INDEX row links unknown entry: {path}")
            continue
        ienf_base = re.sub(r"\*|\(.*", "", ienf).strip()
        if e.form != iform:
            problems.append(f"FORM mismatch {path}: INDEX=`{iform}` entry=`{e.form}`")
        if e.novelty != inov:
            problems.append(f"NOVELTY mismatch {path}: INDEX={inov} entry={e.novelty}")
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


def cmd_validate(_args) -> int:
    entries = all_entries()
    n_issues = 0
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
    for key in ("role", "family", "form", "novelty"):
        val = getattr(args, key)
        if val:
            rows = [r for r in rows if (r[key] or "").lower() == val.lower()]
    if args.enf:
        rows = [r for r in rows if (r["enforcement"] or "").lower() == args.enf.lower()]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{r['role']:8} · {r['family']:28} · {r['form']:14} · "
                  f"{r['novelty']:8} · {r['enforcement']:9} · {r['path']}")
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


def main() -> int:
    p = argparse.ArgumentParser(description="Validate + query the governance-catalogue schema.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="schema + INDEX + link + summary checks; exit 1 on any violation")
    q = sub.add_parser("query", help="filter/list entries")
    q.add_argument("--role", help="Agent | Bridge | Product")
    q.add_argument("--family")
    q.add_argument("--form", help="one of the nine forms")
    q.add_argument("--novelty", help="novel | notable | standard")
    q.add_argument("--enf", help="Hard | Soft | Soft·Hard")
    q.add_argument("--json", action="store_true")
    s = sub.add_parser("summaries", help="dump role/family/entry summaries (tooltip source)")
    s.add_argument("--json", action="store_true")
    args = p.parse_args()
    return {"validate": cmd_validate, "query": cmd_query, "summaries": cmd_summaries}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
