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
import subprocess
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

    def title_only(self) -> str:
        m = re.search(r"^# (.+)$", self.text, re.M)
        return m.group(1).strip() if m else self.path

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
        if os.sep + "downloads" + os.sep in f:
            continue  # raw download assets (redacted CLAUDE mirror): illustrative links, not rendered
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


# ─────────────────────────── Phase 3: md → html codegen ───────────────────────────
# Dependency-free (stdlib only): a compact renderer for exactly the markdown constructs
# the catalogue uses (headers, tables, bullets, code spans/fences, bold/italic, links).
# `.md` links are rewritten to `.html` so the generated site is self-contained.

GENERATED_BANNER = ("<!-- GENERATED by catalog.py build — DO NOT EDIT. "
                    "Edit the sibling .md and re-run `catalog.py build`. -->")

PAGE_CSS = """
  :root { --ink:#1a1a1a; --muted:#555; --accent:#b45309; --line:#e2e8f0; --link:#0b5cad; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Avenir Next",Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:var(--ink); background:#fff; line-height:1.55; }
  main { max-width: 820px; margin: 0 auto; padding: 32px 22px 80px; }
  nav.crumb { font-size: 12.5px; color: var(--muted); margin: 0 0 18px; letter-spacing:.01em; }
  nav.crumb a { color: var(--link); text-decoration: none; }
  nav.crumb a:hover { text-decoration: underline; }
  h1 { font-size: 27px; margin: 6px 0 4px; letter-spacing:-0.02em; }
  h2 { font-size: 19px; margin: 30px 0 8px; padding-top: 6px; border-top:1px solid var(--line); }
  h3 { font-size: 16px; margin: 22px 0 6px; }
  h4 { font-size: 14.5px; margin: 16px 0 4px; color:#333; }
  p, li { font-size: 14.5px; }
  a { color: var(--link); }
  code { background:#f6f8fa; padding:1px 5px; border-radius:4px; font-size:.9em;
         font-family:"SF Mono",Menlo,Consolas,monospace; }
  pre { background:#f6f8fa; padding:12px 14px; border-radius:7px; overflow:auto; }
  pre code { background:none; padding:0; }
  table { border-collapse: collapse; margin: 12px 0; font-size: 13.5px; width:100%; }
  th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; }
  th { background:#f8fafc; font-weight:700; }
  hr { border:none; border-top:1px solid var(--line); margin: 22px 0; }
  .subtitle { font-size: 15px; color:#444; font-style: italic; margin: 0 0 6px; }
  .tag { color: var(--accent); font-weight: 700; font-size: 12px; letter-spacing:.08em; text-transform:uppercase; }
  .census h3.role-h { color:#c2410c; border-top:2px solid var(--line); padding-top:14px; margin-top:26px; }
  table.census-t td.c-name a { font-weight:600; text-decoration:none; }
  table.census-t td.c-name a:hover { text-decoration:underline; }
  table.census-t tr:hover { background:#fafcff; }
  .fam-lede { font-size:13px; color:var(--muted); font-style:italic; margin:2px 0 6px; }
  .foot { font-size: 12.5px; color: var(--muted); border-top:1px solid var(--line); padding-top:14px; margin-top: 34px; }
"""

ROLE_DISPLAY = {"agent": "Agent", "models-bridge": "Models-bridge", "product": "Product"}


def _md_link_rewrite(url: str) -> str:
    if url.startswith(("http://", "https://", "#", "mailto:")):
        return url
    if url.endswith(".md"):
        return url[:-3] + ".html"
    return url.replace(".md#", ".html#")


def _attr(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def _inline(s: str) -> str:
    """Inline markdown → HTML: code spans, links, bold, italic. Order-sensitive."""
    spans: list[str] = []
    s = re.sub(r"`([^`]+)`", lambda m: spans.append(m.group(1)) or f"\x00{len(spans)-1}\x00", s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: f'<a href="{_attr(_md_link_rewrite(m.group(2)))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00",
               lambda m: "<code>{}</code>".format(
                   spans[int(m.group(1))].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")), s)
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
            esc = "\n".join(code).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f"<pre><code>{esc}</code></pre>"); continue
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


def _page(title: str, crumb: str, body: str, subtitle: str = "", rel: str = "") -> str:
    sub = f'<p class="subtitle">{_inline(subtitle)}</p>\n' if subtitle else ""
    return (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>{_attr(title)}</title>\n<style>{PAGE_CSS}</style>\n</head>\n<body>\n"
            f"<main>\n{crumb}\n{sub}{body}\n</main>\n</body>\n</html>\n")


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
    row_re = re.compile(
        r"^\| (?:✅|☐)\s*(★)?\s*\| ([^|]+?) \| `([a-z-]+)` \| (\w+) \| ([^|]+?) \| "
        r"\[[^\]]+\]\(([^)]+)\) \|$")
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
                                "form": r.group(3), "nov": r.group(4), "enf": r.group(5).strip(),
                                "path": r.group(6).strip()})
    return fams


def build_census(entries: list[Entry]) -> str:
    summ = {e.path: e.summary for e in entries}
    out = ['<section class="census">', "<h2>The catalogue — every control</h2>"]
    last = None
    for fam in parse_census():
        if fam["role"] != last:
            out.append(f'<h3 class="role-h">{_attr(fam["role"] or "")}</h3>'); last = fam["role"]
        out.append(f'<h4>{_attr(fam["family"])}</h4>')
        if fam["oneliner"]:
            out.append(f'<p class="fam-lede">{_inline(fam["oneliner"])}</p>')
        out.append('<table class="census-t"><thead><tr><th>Control</th><th>Form</th>'
                   "<th>Novelty</th><th>Enf.</th></tr></thead><tbody>")
        for r in fam["rows"]:
            href = _md_link_rewrite(r["path"])
            star = " ★" if r["star"] else ""
            tip = _attr(summ.get(os.path.normpath(r["path"]), ""))
            out.append(
                f'<tr title="{tip}"><td class="c-name"><a href="{href}">'
                f'{_inline(r["control"])}{star}</a></td>'
                f'<td><code>{r["form"]}</code></td><td>{r["nov"]}</td>'
                f'<td>{_inline(r["enf"])}</td></tr>')
        out.append("</tbody></table>")
    out.append("</section>")
    return "\n".join(out)


LANDING_INTRO = """  <div class="tag">Pattern catalogue</div>
  <h1>Agent Governance Mechanisms</h1>
  <p class="subtitle">The controls that keep a fleet of autonomous coding agents productive while holding
  the cost of their failures within bounds — {n} controls across three roles, each written like a design
  pattern: the recurring failure it kills, and why it is <i>not</i> just the cheaper thing everyone does.</p>
  <p style="font-size:13.5px;color:#555;border-left:3px solid #b45309;padding:4px 0 4px 12px;margin:14px 0 22px;">
  Distilled from the case study in <a href="https://arxiv.org/pdf/2607.01087"><i>Cheap Code, Costly
  Judgment: A Case Study on Governable Agentic Software Engineering</i></a>.</p>
  <ul style="list-style:none;padding:0;margin:0 0 18px;font-size:14px;">
  <li style="margin-bottom:8px;"><a href="catalogue-figure.html"><b>▸ The control-map figure</b></a>
    <span style="color:#555;">— the whole catalogue at a glance: four hand-drawn views (census · staircase · lattice · model-bridge)</span></li>
  <li style="margin-bottom:8px;"><a href="catalogue-views.html">▸ Interactive views</a>
    <span style="color:#555;">— every control clickable + hover-summaries, re-grouped live from metadata; adding one is data, not layout</span></li>
  <li style="margin-bottom:8px;"><a href="quick-start.html">▸ Quick start — adopt these in your repo</a>
    <span style="color:#555;">— install a governance doc, point your agent here, ask for an adopt/adapt plan</span></li>
  <li style="margin-bottom:8px;"><a href="https://github.com/davisjam/agent-governance-mechanisms">▸ Browse the source on GitHub</a>
    <span style="color:#555;">— README · INDEX · every control as a full writeup</span></li>
  <li style="margin-bottom:8px;"><a href="downloads/CLAUDE-starter.md" download>▸ Download a starter <code>CLAUDE.md</code></a>
    <span style="color:#555;">— the governance-rules half of a real, mature one (identity redacted); a menu to adapt</span></li>
  <li><a href="https://github.com/davisjam/agent-governance-mechanisms/archive/refs/heads/main.zip">▸ Download the catalogue</a>
    <span style="color:#555;">— the full set of markdown writeups as a ZIP</span></li>
  </ul>
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
  .grp h3 { font-size:13.5px; margin:0 0 7px; padding-bottom:3px; border-bottom:1px solid var(--line); }
  .grp h3 .cnt { color:var(--muted); font-weight:500; font-size:11px; }
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
  { id:"novelty", label:"By novelty",       blurb:"How new the mechanism is: novel · notable · standard-applied-well.", key:c=>c.novelty, order:["novel","notable","standard"] },
];
const roleCls = c => c.role==="Agent"?"r-a":c.role==="Product"?"r-p":"r-b";
const enfCls  = c => c.enforcement==="Hard"?"e-h":c.enforcement==="Soft"?"e-s":"e-sh";
function renderForView(card){                       // one card ← its metadata; clickable + tooltipped
  const star = card.star ? ' <span class="star">★</span>' : '';
  const tip = (card.summary||"").replace(/"/g,'&quot;');
  return '<a class="card '+roleCls(card)+' '+enfCls(card)+'" href="'+card.html+'" title="'+tip+'">'
       + '<span class="c-t">'+card.title+star+'</span>'
       + '<span class="c-m"><code>'+card.form+'</code> · '+card.novelty+' · '+card.enforcement+'</span></a>';
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
      '<section class="grp"><h3>'+label(k)+' <span class="cnt">('+cs.length+')</span></h3>'
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
            "novelty": d["novelty"], "enforcement": d["enforcement"],
            "summary": d["summary"], "star": e.path in stars,
        })
    head = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>Governance catalogue — codegen'd views</title>\n<style>{VIEWS_CSS}</style>\n</head>\n<body>\n")
    body = ("<h1>Governance catalogue — codegen'd views</h1>\n"
            '<p class="sub">The same 51 controls, re-grouped live from card metadata. Every card is emitted by '
            '<code>renderForView(card)</code>; a view is just a grouping key + order, so <b>adding a control or a '
            'view is data, not layout</b>. Click a card for its writeup; hover for its one-line summary. '
            '&nbsp;·&nbsp; <a href="catalogue-figure.html">the hand-drawn figure</a> '
            '&nbsp;·&nbsp; <a href="index.html">catalogue</a></p>\n'
            '<div id="tabs"></div>\n<div id="stage"></div>\n')
    script = "<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n" + VIEWS_JS + "</script>\n"
    return head + body + script + "</body>\n</html>\n"


def cmd_build(_args) -> int:
    entries = all_entries()
    written = 0
    md_files = sorted(f for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
                      if os.sep + "downloads" + os.sep not in f)  # raw assets, shipped as-is
    by_path = {e.path: e for e in entries}
    for f in md_files:
        rel = os.path.relpath(f, ROOT)
        depth = rel.count(os.sep)
        rel_root = "../" * depth
        md = open(f, encoding="utf-8").read()
        e = by_path.get(rel)
        title = (re.search(r"^# (.+)$", md, re.M) or [None, rel])[1]
        if e:  # a control entry
            seg0 = rel.split(os.sep)[0]
            trail = [(ROLE_DISPLAY.get(seg0, e.role or ""), f"{rel_root}{seg0}/README.html"),
                     (e.family or "", ""), (e.title_only(), "")]  # family has no page → plain text
            body = render_md(md)
            html = _page(e.title_only(), _crumb(rel_root, trail), body, subtitle=e.summary)
        else:  # README / INDEX
            trail = []
            if depth >= 1:
                seg0 = rel.split(os.sep)[0]
                trail.append((ROLE_DISPLAY.get(seg0, seg0), f"{rel_root}{seg0}/README.html" if depth == 2 else ""))
            if os.path.basename(rel) != "README.md" or depth == 0:
                trail.append((title, ""))
            body = render_md(md)
            html = _page(title, _crumb(rel_root, trail), body)
        out_path = f[:-3] + ".html"
        open(out_path, "w", encoding="utf-8").write(html)
        written += 1
    # landing index.html = intro + census (overwrites the hand-authored placeholder)
    landing_body = LANDING_INTRO.format(n=len(entries)) + "\n" + build_census(entries) + \
        '\n  <p class="foot">Built from the markdown by <code>catalog.py build</code>. '\
        'Hover a control for its one-line summary; click to open its writeup.</p>'
    landing = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
               f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
               f"<title>Agent Governance Mechanisms</title>\n<style>{PAGE_CSS}</style>\n</head>\n"
               f"<body>\n<main>\n{landing_body}\n</main>\n</body>\n</html>\n")
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(landing)
    open(os.path.join(ROOT, "catalogue-views.html"), "w", encoding="utf-8").write(build_views_page(entries))
    print(f"built {written} entry/index pages + landing index.html + catalogue-views.html "
          f"({len(entries)} controls in census)")
    return 0


def cmd_install_hooks(_args) -> int:
    """Point git at the tracked hooks/ dir so validate+build run on every commit."""
    r = subprocess.run(["git", "config", "core.hooksPath", "hooks"], cwd=ROOT)
    if r.returncode == 0:
        print("core.hooksPath → hooks (pre-commit will validate + build + stage HTML)")
    return r.returncode


DEFAULT_PORT = 8137  # deliberately not 8080/8000 (common collisions)


def _git(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, text=True,
                          capture_output=capture)


def cmd_deploy(args) -> int:
    """Build the site, then serve it locally (--local) or publish it to GitHub (--github)."""
    print(f"== Deploy plan: target={args.target} ==")
    print("  1. validate schema   2. build HTML   "
          + ("3. serve on localhost" if args.target == "local"
             else "3. commit + push to origin main (CI deploys)"))
    if cmd_validate(None) != 0:
        print("ABORT: schema invalid — fix before deploying.")
        return 1
    cmd_build(None)

    if args.target == "local":
        url = f"http://127.0.0.1:{args.port}/"
        print(f"\n== Serving {url}  (Ctrl-C to stop) ==")
        try:
            subprocess.run([sys.executable, "-m", "http.server", str(args.port),
                            "--bind", "127.0.0.1"], cwd=ROOT)
        except KeyboardInterrupt:
            print("\nstopped.")
        return 0

    # --github: commit whatever changed, then push (the Actions workflow deploys on push)
    _git("add", "-A")
    dirty = _git("status", "--porcelain", capture=True).stdout.strip()
    if dirty:
        cp = _git("commit", "-m", args.message)
        if cp.returncode:
            print("ABORT: commit failed (see hook output above).")
            return cp.returncode
    else:
        print("  (nothing to commit — pushing current HEAD)")
    if _git("push", "origin", "main").returncode:
        print("ABORT: push failed.")
        return 1
    head = _git("rev-parse", "--short", "HEAD", capture=True).stdout.strip()
    print(f"\n== Pushed {head} to origin/main. GitHub Actions will build + deploy Pages. ==")
    print("   Watch: https://github.com/davisjam/agent-governance-mechanisms/actions")
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
    sub.add_parser("build", help="render every .md → .html + regenerate the landing census")
    sub.add_parser("install-hooks", help="git config core.hooksPath hooks (auto-regen on commit)")
    d = sub.add_parser("deploy", help="build, then serve locally (local) or publish to GitHub (github)")
    d.add_argument("target", choices=["local", "github"], help="local = serve on localhost; github = commit + push (CI deploys)")
    d.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"localhost port for --local (default {DEFAULT_PORT})")
    d.add_argument("-m", "--message", default="deploy: rebuild site", help="commit message for github mode")
    args = p.parse_args()
    return {"validate": cmd_validate, "query": cmd_query, "summaries": cmd_summaries,
            "build": cmd_build, "install-hooks": cmd_install_hooks, "deploy": cmd_deploy}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
