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
ROLES = {"Agent", "Bridge", "Product"}
ENF_CLASSES = {"Hard", "Soft", "Soft·Hard"}
META_ORDER = ["Summary", "Target", "Form", "Enforcement"]  # Summary first; novelty/artifact/rule dropped
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
            "form": self.form, "enforcement": self.enf, "summary": self.summary,
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
        r"^\| (?:✅|☐)[^|]*\| ([^|]+?) \| `([a-z-]+)` \| ([^|]+?) \| \[[^\]]+\]\(([^)]+)\) \|$",
        idx, re.M,
    )
    problems = []
    for _ctrl, iform, ienf, path in rows:
        e = by_path.get(os.path.normpath(path))
        if e is None:
            problems.append(f"INDEX row links unknown entry: {path}")
            continue
        ienf_base = re.sub(r"\*|\(.*", "", ienf).strip()
        if e.form != iform:
            problems.append(f"FORM mismatch {path}: INDEX=`{iform}` entry=`{e.form}`")
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
    for key in ("role", "family", "form"):
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

SITE_FOOTER = (f'<footer class="site-foot">© <a href="https://davisjam.github.io">James C. Davis</a>, '
               f'Assistant Professor, ECE @ Purdue &nbsp;·&nbsp; '
               f'<a class="gh" href="https://github.com/davisjam/agent-governance-mechanisms">'
               f'{GITHUB_SVG} agent-governance-mechanisms</a></footer>')

TOPNAV = ('<div class="topnav"><a href="https://davisjam.github.io">James C. Davis, Purdue University</a>'
          '<a class="gh" href="https://github.com/davisjam/agent-governance-mechanisms">'
          f'{GITHUB_SVG} GitHub</a></div>')

FONT_CSS = ('  body { font-family:"Source Sans 3",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }\n'
            '  h1,h2,h3,h4,.walk-h,.section-h { font-family:"Source Serif 4",Georgia,"Times New Roman",serif; }\n'
            '  .site-foot { max-width:1040px; margin:40px auto 0; padding:16px 22px 30px; border-top:1px solid #e2e8f0;'
            ' font-size:12.5px; color:#666; text-align:center; }\n'
            '  .site-foot a { color:#0b5cad; text-decoration:none; } .site-foot a:hover { text-decoration:underline; }\n'
            '  .site-foot .gh { white-space:nowrap; }\n'
            '  .topnav { position:absolute; top:14px; right:20px; font-size:12px; display:flex; gap:16px; }\n'
            '  .topnav a { color:#555; text-decoration:none; white-space:nowrap; } .topnav a:hover { color:#0b5cad; }\n'
            '  @media (max-width:640px){ .topnav { position:static; justify-content:flex-end; margin:0 0 8px; } }\n')

PAGE_CSS = """
  :root { --ink:#1a1a1a; --muted:#555; --accent:#b45309; --line:#e2e8f0; --link:#0b5cad; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Avenir Next",Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:var(--ink); background:#fff; line-height:1.55; }
  main { width: 92vw; max-width: 1040px; margin: 0 auto; padding: 32px 22px 80px; }
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
    if "downloads/" in url:
        return url  # raw asset (CLAUDE starter) — shipped as .md, not rendered
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
            f"<title>{_attr(title)}</title>\n{FONTS_LINK}\n<style>{PAGE_CSS}{FONT_CSS}</style>\n</head>\n<body>\n"
            f"<main>\n{crumb}\n{sub}{body}\n{SITE_FOOTER}\n</main>\n</body>\n</html>\n")


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
        r"^\| (?:✅|☐)\s*(★)?\s*\| ([^|]+?) \| `([a-z-]+)` \| ([^|]+?) \| "
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
                                "form": r.group(3), "enf": r.group(4).strip(),
                                "path": r.group(5).strip()})
    return fams


CENSUS_LEGEND = (
    '<p class="census-legend"><b>Form</b> is the shape a control takes (one of nine — a typed IR, a '
    'validation check, a quality gate, an audit trail, …). <b>Enf.</b> is how it enforces: '
    '<b>Hard</b> is deterministic (blocks, audits, or signals regardless of agent cooperation), '
    '<b>Soft</b> is probabilistic (aims an agent but cannot block), and <b>Soft·Hard</b> is soft '
    'guidance with a hard counterpart. Hover a row for its summary; click a name for the full writeup.</p>')

ROLE_HEADINGS = {
    "Agent": "Governance: Agents",
    "Models-bridge": "Governance: Models — a bridge between agents and product",
    "Bridge": "Governance: Models — a bridge between agents and product",
    "Product": "Governance: Product",
}


def build_census(entries: list[Entry]) -> str:
    summ = {e.path: e.summary for e in entries}
    out = ['<section class="census">', '<h2>The catalogue — every control</h2>', CENSUS_LEGEND]
    last = None
    for fam in parse_census():
        if fam["role"] != last:
            heading = ROLE_HEADINGS.get(fam["role"] or "", f'Governance: {fam["role"]}')
            out.append(f'<h3 class="role-h">{_attr(heading)}</h3>'); last = fam["role"]
        out.append(f'<h4>{_attr(fam["family"])}</h4>')
        if fam["oneliner"]:
            out.append(f'<p class="fam-lede">{_inline(fam["oneliner"])}</p>')
        out.append('<table class="census-t"><thead><tr><th>Control</th><th>Form</th>'
                   "<th>Enf.</th></tr></thead><tbody>")
        for r in fam["rows"]:
            href = _md_link_rewrite(r["path"])
            tip = _attr(summ.get(os.path.normpath(r["path"]), ""))
            enf = _inline(r["enf"].replace("**", ""))   # no random bolding of Soft/Hard
            out.append(
                f'<tr title="{tip}"><td class="c-name"><a href="{href}">{_inline(r["control"])}</a></td>'
                f'<td><code>{r["form"]}</code></td><td>{enf}</td></tr>')
        out.append("</tbody></table>")
    out.append("</section>")
    return "\n".join(out)


LANDING_CSS = """
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
  .mustache { display:block; width:100%; height:44px; margin:2px 0 0; }
  .loop-outcome { text-align:center; margin:10px 0 2px; font-size:13px; color:#333; }
  .loop-outcome b { color:var(--accent); }
  .loop .tail { margin:14px 0 0; font-size:12.5px; color:#444; line-height:1.55; text-align:center; }
  .refs { margin:0 0 24px; }
  .refs .r { border-left:3px solid var(--accent); padding:3px 0 3px 12px; margin:0 0 7px; font-size:13px; color:#444; }
  .refs .r b { color:#333; font-weight:700; }
  .cards-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(232px,1fr)); gap:11px; margin:0 0 26px; }
  .lcard { display:block; text-decoration:none; border:1.4px solid var(--line); border-radius:10px;
           padding:13px 15px; background:#fff; transition:box-shadow .12s, border-color .12s; }
  .lcard:hover { box-shadow:0 3px 12px rgba(0,0,0,.09); border-color:#cbd5e1; }
  .lcard b { display:block; font-size:16px; color:var(--link); letter-spacing:-.01em; margin-bottom:3px; }
  .lcard span { display:block; font-size:12px; color:var(--muted); line-height:1.4; }
  .lead, .subtitle, .walk-sub, .section-sub, .census-legend { max-width:840px; }
  .lead { font-size:14.5px; color:#2a2a2a; line-height:1.62; margin:0 0 13px; }
  .lead .term { font-weight:700; }
  .wf { position:relative; left:50%; transform:translateX(-50%); width:min(1180px,96vw); margin:14px 0 6px; }
  .wf-frame { width:100%; overflow:hidden; }
  .wf-frame iframe { display:block; border:none; background:#fff; }
  .wf figcaption { font-size:12px; color:var(--muted); margin-top:8px; text-align:center; }
  hr.sep { border:none; border-top:1px solid var(--line); margin:26px 0 20px; }
  .walk-h { font-size:18px; margin:0 0 4px; letter-spacing:-.01em; }
  .walk-sub { font-size:13px; color:var(--muted); margin:0 0 14px; }
  .section-h { font-size:17px; margin:24px 0 3px; letter-spacing:-.01em; }
  .section-sub { font-size:12.5px; color:var(--muted); margin:0 0 12px; }
  .section-sub a { color:var(--link); }
  .spectrum { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin:4px 0 6px; align-items:stretch; }
  .school { border:1.4px solid var(--line); border-radius:10px; padding:12px 13px; background:#fff; display:flex; flex-direction:column; }
  .school.mid { border:2px solid var(--accent); background:#fffaf3; }
  .school h3 { margin:0 0 5px; font-size:14.5px; }
  .school.mid h3 { color:var(--accent); }
  .school p { margin:0 0 9px; font-size:12.5px; color:#444; line-height:1.5; }
  .school .srefs { font-size:11px; color:var(--muted); margin:0 0 10px; }
  .school .srefs .lbl { font-weight:700; color:#444; }
  .school .srefs ul { margin:3px 0 0; padding-left:16px; }
  .school .srefs li { margin:0 0 2px; line-height:1.4; }
  .school .srefs a { color:var(--link); }
  .school .pole { margin-top:auto; font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:800; }
  .spectrum-axis { text-align:center; font-size:11px; color:var(--muted); letter-spacing:.03em; margin:0 0 20px; }
  .cols3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:4px 0 8px; }
  .col h3 { margin:0 0 8px; font-size:14px; padding-bottom:5px; border-bottom:2px solid var(--accent); }
  .col ul { margin:0; padding:0; list-style:none; }
  .col li { font-size:12.3px; color:#3a3a3a; line-height:1.42; margin:0 0 9px; padding-left:15px; position:relative; }
  .col li::before { content:"→"; position:absolute; left:0; color:var(--accent); font-weight:700; }
  .ways-note { font-size:11.5px; color:var(--muted); margin:2px 0 22px; }
  .mechanisms { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:4px 0 8px; }
  .mech { border:1.4px solid var(--line); border-left:4px solid var(--accent); border-radius:10px; padding:12px 15px; background:#fff; }
  .mech h4 { margin:0 0 5px; font-size:14px; }
  .mech p { margin:0; font-size:12.8px; color:#444; line-height:1.5; }
  @media (max-width:720px){ .spectrum, .cols3, .mechanisms { grid-template-columns:1fr; } }
"""

# (title, subtitle, href, extra-attrs) for the landing action cards
LANDING_CARDS = [
    ("The control-map figure", "the whole catalogue at a glance — four views, controls clickable", "catalogue-figure.html", ""),
    ("Interactive views", "every control, re-grouped live from metadata", "catalogue-views.html", ""),
    ("Quick start", "adopt these in your own repo", "quick-start.html", ""),
    ("Starter CLAUDE.md", "a real, mature one — redacted; a menu to adapt", "downloads/CLAUDE-starter.md", " download"),
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


def _landing_flow() -> str:
    steps = []
    for i, (title, detail) in enumerate(_FLOW, 1):
        steps.append(f'<div class="fstep"><span class="fn">{i}</span><b>{title}</b><span>{detail}</span></div>')
        if i < len(_FLOW):
            steps.append('<div class="farrow">→</div>')
    row = '<div class="flow">\n    ' + "\n    ".join(steps) + '\n    </div>'
    mustache = ('<svg class="mustache" viewBox="0 0 1000 58" preserveAspectRatio="none" aria-hidden="true">'
                '<path d="M980 6 C 980 52, 560 55, 500 55 C 440 55, 20 52, 20 6" fill="none" '
                'stroke="#94a3b8" stroke-width="2.5" vector-effect="non-scaling-stroke"/>'
                '<path d="M20 6 l 13 -3 M20 6 l 9 10" fill="none" stroke="#94a3b8" stroke-width="2.5" '
                'stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')
    outcome = f'<p class="loop-outcome"><b>{_FLOW_OUTCOME[0]}.</b> {_FLOW_OUTCOME[1]}</p>'
    return row + "\n    " + mustache + "\n    " + outcome


def _landing_cards() -> str:
    return "\n  ".join(
        f'<a class="lcard" href="{href}"{extra}><b>{t}</b><span>{sub}</span></a>'
        for t, sub, href, extra in LANDING_CARDS)


# The two schools + the midway (title, blurb, pole-label, is-midway, [(ref-label, url), ...])
SCHOOLS = [
    ("Vibe coding",
     "Prompt an agent, accept what looks right, iterate by feel. Fast and fluid — but quality rests on "
     "the model and your eye. At scale the same failures keep recurring, and human review becomes the "
     "bottleneck.", "all velocity — no durable guardrails", False,
     [("Karpathy — coined “vibe coding”", "https://x.com/karpathy/status/1886192184808149383"),
      ("Steve Yegge’s Gas Town", "https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04")]),
    ("Governance-centric",
     "The midway. Velocity <b>exposes</b> failures; you <b>convert</b> each recurring one into a guardrail "
     "— a type, a lint, a gate. The guardrails grow out of real failures, so code stays fast <i>and</i> "
     "stays trustworthy.", "velocity + guardrails grown from failure", True, []),
    ("Oversight-centric",
     "Check <i>everything</i> before you trust it — whether a human reviews every change or a formal "
     "specification is verified against. Rigorous and safe, but checking becomes the bottleneck: all of it "
     "must be vetted, and neither humans nor specs anticipate the failures that only appear at velocity. "
     "(Spec-driven development is this, with the spec as the checker.)",
     "all oversight — everything checked", False,
     [("Meyer, CACM — “From Probable to Provable”", "https://dl.acm.org/doi/full/10.1145/3773295"),
      ("vibe-OS / vibe-tools (formal tooling for AI)", "https://homes.cs.washington.edu/~oskin/vibeos/vibetools.html")]),
]

# The three-column "way of thinking" — the AI-First Engineering Method (A.1–A.21), engineering-oriented
WAYS = [
    ("Architect deliberately", [
        "Implementation is cheap; architecture compounds — buy the right design, not the fast one.",
        "Name shapes with types; primitive-passing leaves the architecture anonymous.",
        "Make models, state, and policy explicit — state machines over scattered counters, enums over magic strings.",
        "One canonical way beats many clever ones — agents will apply patterns they see 200× with no debate.",
        "Attack accidental complexity; budget for the essential kind.",
    ]),
    ("Convert failure into machinery", [
        "When a failure recurs, encode it — a lint, type, gate, or schema — instead of re-inspecting for it.",
        "Move audits to lints: cheap, at-commit, deterministic beats expensive and post-hoc.",
        "Let the compiler and gates hold the line — review is not a substitute for static analysis.",
        "Never fail quiet — every caught error logs, re-throws, or is justified in a comment.",
        "No compatibility shims — migrate every call site in the same change.",
    ]),
    ("Keep judgment scarce & central", [
        "Carry work autonomously; surface only the load-bearing, architectural calls.",
        "Hyper-experimentation — pilot, compare, measure; a cheap experiment beats a debate, and negative results are wins.",
        "Verify claims and trust nothing stale — re-run the gates yourself, because markers rot.",
        "Reason about second-order dynamics — what happens at T+100, or under concurrency?",
        "Documentation encodes invariants that drive tests, not prose that rots.",
    ]),
]


def _landing_schools() -> str:
    out = []
    for title, blurb, pole, mid, refs in SCHOOLS:
        cls = "school mid" if mid else "school"
        rhtml = ""
        if refs:
            lis = "".join(f'<li><a href="{u}">{lbl}</a></li>' for lbl, u in refs)
            rhtml = f'<div class="srefs"><span class="lbl">Examples:</span><ul>{lis}</ul></div>'
        out.append(f'<div class="{cls}"><h3>{title}</h3><p>{blurb}</p>{rhtml}'
                   f'<span class="pole">{pole}</span></div>')
    return "\n  ".join(out)


def _landing_ways() -> str:
    out = []
    for title, items in WAYS:
        lis = "".join(f"<li>{it}</li>" for it in items)
        out.append(f'<div class="col"><h3>{title}</h3><ul>{lis}</ul></div>')
    return "\n  ".join(out)


LANDING_INTRO = """  <div class="tag">Governance-centric agentic software engineering</div>
  <h1>Agent Governance Mechanisms</h1>

  <p class="lead">Generative AI is shifting software engineering from a practice built around scarce
  implementation toward one built around <span class="term">abundant, low-cost code</span>. The hard part
  stops being writing code and becomes <span class="term">governing the conditions under which fast code
  can be trusted</span> — keeping it inspectable, correctable, and maintainable at speed.</p>

  <h2 class="section-h">Between two schools of thought</h2>
  <p class="section-sub">Two common ways to build with agents sit at opposite poles. This site is about
  the midway.</p>
  <div class="spectrum">
  {schools}
  </div>
  <p class="spectrum-axis">← all velocity &nbsp;&nbsp;•&nbsp;&nbsp; all oversight →</p>

  <p class="lead">The midway has a name — <span class="term">governance conversion</span> — and a working
  rule: <b>don't specify everything up front, and don't trust the vibes; let velocity surface the
  failures, and convert each recurring one into a durable guardrail.</b> The result is <b>{n} governance
  mechanisms across three roles</b>, each written like a design pattern — the recurring failure it kills,
  and why it is <i>not</i> just the cheaper thing everyone already does.</p>

  <h2 class="section-h">Governance has two mechanisms</h2>
  <p class="section-sub">A guardrail is one of two kinds — prevent the error, or catch it.</p>
  <div class="mechanisms">
    <div class="mech"><h4>Architecture</h4><p>Make the error <b>impossible by construction</b>: a typed
    model with one sanctioned seam, a state that cannot be represented wrongly. Software
    <a href="https://en.wikipedia.org/wiki/Poka-yoke">poka-yoke</a> — error-<i>proofing</i>, so the bad
    move can’t happen in the first place.</p></div>
    <div class="mech"><h4>Control</h4><p>Where you can’t prevent it, <b>observe and guard</b> the behavior:
    a lint, a gate, a validator, an audit that fires on a violation and holds the line. Error-<i>catching</i>,
    deterministically, before the failure escapes.</p></div>
  </div>

  <h2 class="section-h">The way of thinking</h2>
  <p class="section-sub">Three stances that make the midway work — distilled from the AI-First Engineering
  Method (21 principles); the full set ships in the
  <a href="downloads/CLAUDE-starter.md" download>starter CLAUDE.md</a>.</p>
  <div class="cols3">
  {ways}
  </div>

  <div class="refs">
    <div class="r"><b>Case study:</b> <a href="https://arxiv.org/pdf/2607.01087"><i>Cheap Code, Costly
    Judgment: A Case Study on Governable Agentic Software Engineering</i></a></div>
    <div class="r"><b>Live system it governs:</b> <a href="https://scholaccess.com">scholaccess.com</a></div>
  </div>

  <figure class="wf">
    <div class="wf-frame"><iframe id="wf-frame" src="development-workflow.html"
      title="The development-process figure" scrolling="no" onload="fitFig(this)"></iframe></div>
    <figcaption>The development process — the control substrate wrapped around the human-directs-agents
    loop. <a href="development-workflow.html">Open the figure full-screen ↗</a></figcaption>
  </figure>
  <script>
  function fitFig(f){{
    try{{
      var d=f.contentWindow.document, w=d.documentElement.scrollWidth||1040, h=d.documentElement.scrollHeight||600;
      var avail=f.parentElement.clientWidth, s=Math.min(1, avail/w);
      f.style.width=w+'px'; f.style.height=h+'px';
      f.style.transformOrigin='top left'; f.style.transform='scale('+s+')';
      f.parentElement.style.height=(h*s)+'px';
    }}catch(e){{}}
  }}
  window.addEventListener('resize', function(){{ var f=document.getElementById('wf-frame'); if(f) fitFig(f); }});
  </script>

  <hr class="sep" />

  <h2 class="walk-h">Walking through the loop</h2>
  <p class="walk-sub">Governance conversion is a non-terminating loop: higher velocity keeps surfacing
  failure classes that earlier governance didn't address.</p>
  <div class="loop">
    {flow}
    <p class="tail">Implementation is cheap; the judgment that decides <i>which governance should
    exist</i> is the costly, human part. Two dual theses hold it together: governance makes velocity
    sustainable, and judgment determines which governance should exist.</p>
  </div>

  <hr class="sep" />

  <h2 class="section-h">Explore the catalogue</h2>
  <p class="section-sub">{n} governance mechanisms — the repertoire this loop produced in one real
  production system.</p>
  <div class="cards-grid">
  {cards}
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
            "enforcement": d["enforcement"],
            "summary": d["summary"], "star": e.path in stars,
        })
    head = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
            f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"<title>Governance catalogue — codegen'd views</title>\n{FONTS_LINK}\n"
            f"<style>{VIEWS_CSS}{FONT_CSS}</style>\n</head>\n<body>\n")
    body = ("<h1>Governance catalogue — codegen'd views</h1>\n"
            '<p class="sub">The same 51 controls, re-grouped live from card metadata. Every card is emitted by '
            '<code>renderForView(card)</code>; a view is just a grouping key + order, so <b>adding a control or a '
            'view is data, not layout</b>. Click a card for its writeup; hover for its one-line summary. '
            '&nbsp;·&nbsp; <a href="catalogue-figure.html">the control-map figure</a> '
            '&nbsp;·&nbsp; <a href="index.html">catalogue</a></p>\n'
            '<div id="tabs"></div>\n<div id="stage"></div>\n')
    script = "<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n" + VIEWS_JS + "</script>\n"
    return head + body + script + SITE_FOOTER + "\n</body>\n</html>\n"


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
    landing_body = TOPNAV + "\n" + LANDING_INTRO.format(
        n=len(entries), flow=_landing_flow(), cards=_landing_cards(),
        schools=_landing_schools(), ways=_landing_ways()) + "\n" + build_census(entries)
    landing = (f"<!doctype html>\n<html lang=\"en\">\n{GENERATED_BANNER}\n<head>\n"
               f'<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
               f"<title>Agent Governance Mechanisms</title>\n{FONTS_LINK}\n"
               f"<style>{PAGE_CSS}{LANDING_CSS}{FONT_CSS}</style>\n</head>\n"
               f"<body>\n<main>\n{landing_body}\n{SITE_FOOTER}\n</main>\n</body>\n</html>\n")
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
