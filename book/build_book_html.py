#!/usr/bin/env python3
"""Render the polished book chapters (ch*.md) to a small static HTML site.

AUTO-GENERATED OUTPUT: this script emits *.html in this folder; do not hand-edit
the .html (re-run `python3 build_book_html.py` to regenerate). Stdlib-only.

Each chapter .md carries metadata comments:
    <!-- part: N --> <!-- part-title: ... --> <!-- chapter: N --> <!-- chapter-title: ... -->
The build derives part grouping + reading order from those, emits one .html per
chapter (Part::Chapter table-of-contents nav on top, prev/next at bottom), and an
index.html landing page.
"""
from __future__ import annotations

import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent  # the catalogue root — the appendix reads the entry .md files from here
ACCENT = "#1a4a7a"

# Mermaid runtime (CDN) — pulled in so the appendix's ```mermaid placeholder blocks render as diagrams.
MERMAID_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
    "<script>mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });</script>"
)

META_RE = re.compile(r"<!--\s*([a-z-]+):\s*(.*?)\s*-->")


def parse_chapter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta = {k: v for k, v in META_RE.findall(text)}
    body = META_RE.sub("", text).strip()
    # Drop the leading H1 (# Chapter ...) — we render it from metadata in the header.
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
    return {
        "slug": path.stem,
        "part": int(meta.get("part", "0")),
        "part_title": meta.get("part-title", ""),
        "chapter": int(meta.get("chapter", "0")),
        "chapter_title": meta.get("chapter-title", path.stem),
        "body_md": "\n".join(lines).strip(),
    }


def _abbr_cite(m: "re.Match[str]") -> str:
    """A `[[slug|text]]` / `[[slug]]` abstraction citation from a catalogue entry → a link into the
    catalogue's rendered abstractions glossary (one level up from book/)."""
    slug = m.group(1).strip()
    text = (m.group(2) or slug).strip()
    return f'<a href="../ABSTRACTIONS.html#{html.escape(slug, quote=True)}">{html.escape(text, quote=False)}</a>'


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    # Abstraction citations (`[[slug|text]]`) → links into the catalogue glossary. After escaping (the
    # brackets survive escaping); before the markdown-link pass so the emitted <a> is left intact.
    s = re.sub(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]", _abbr_cite, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def md_to_html(md: str) -> str:
    """Convert the markdown subset the chapters use into HTML."""
    out: list[str] = []
    blocks = re.split(r"\n\s*\n", md)
    for block in blocks:
        block = block.strip("\n")
        if not block.strip():
            continue
        stripped = block.strip()
        # Fenced code — a ```mermaid block renders as <pre class="mermaid"> (the mermaid runtime
        # transforms it into a diagram); any other fenced block renders as a plain <pre><code>.
        if stripped.startswith("```"):
            lines = block.splitlines()
            lang = lines[0].strip()[3:].strip().lower()
            inner_lines = lines[1:]
            if inner_lines and inner_lines[-1].strip() == "```":
                inner_lines = inner_lines[:-1]
            inner = "\n".join(inner_lines)
            if lang == "mermaid":
                out.append(f'<pre class="mermaid">{html.escape(inner, quote=False)}</pre>')
            else:
                out.append(f"<pre><code>{html.escape(inner, quote=False)}</code></pre>")
            continue
        # Gap-marker callouts.
        if stripped.startswith("[FILL IN:") or stripped.startswith("[MORE CHAPTERS FOLLOW:"):
            kind = "fill" if stripped.startswith("[FILL IN:") else "more"
            label = "FILL IN" if kind == "fill" else "MORE CHAPTERS FOLLOW"
            inner = stripped[stripped.index(":") + 1:].rstrip("]").strip()
            # A plain <div> (not <aside>): <aside> is a `complementary` landmark, and two markers on one
            # page trip html-validate's unique-landmark rule (each landmark needs a unique accessible name).
            out.append(
                f'<div class="marker marker-{kind}">'
                f'<span class="marker-tag">{label}</span> {inline(inner)}</div>'
            )
            continue
        # A standalone HTML comment (e.g. the TODO markers) — emit it raw so it stays an invisible
        # comment in the source rather than escaped visible text.
        if stripped.startswith("<!--") and stripped.endswith("-->") and stripped.count("<!--") == 1:
            out.append(stripped)
            continue
        # Headings.
        if stripped.startswith("### "):
            out.append(f"<h3>{inline(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            out.append(f"<h2>{inline(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            out.append(f"<h1>{inline(stripped[2:])}</h1>")
            continue
        # Blockquote (all lines start with >).
        if all(ln.strip().startswith(">") for ln in block.splitlines()):
            inner = " ".join(ln.strip().lstrip(">").strip() for ln in block.splitlines())
            out.append(f"<blockquote>{inline(inner)}</blockquote>")
            continue
        # Unordered list (all lines start with - ).
        if all(ln.strip().startswith("- ") for ln in block.splitlines()):
            items = "".join(f"<li>{inline(ln.strip()[2:])}</li>" for ln in block.splitlines())
            out.append(f"<ul>{items}</ul>")
            continue
        # Paragraph (join wrapped lines).
        out.append(f"<p>{inline(' '.join(ln.strip() for ln in block.splitlines()))}</p>")
    return "\n".join(out)


CSS = f"""
:root {{ --accent: {ACCENT}; }}
* {{ box-sizing: border-box; }}
body {{ font: 17px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
       color: #1a1a1a; margin: 0; background: #fdfdfc; }}
.wrap {{ max-width: 44rem; margin: 0 auto; padding: 0 1.4rem 4rem; }}
nav.toc {{ background: #f4f3f0; border-bottom: 1px solid #e2e0da; padding: 0.9rem 1.4rem; font-size: 14px; }}
nav.toc .toc-inner {{ max-width: 44rem; margin: 0 auto; }}
nav.toc details {{ margin: 0; }}
nav.toc summary {{ cursor: pointer; font-weight: 600; color: var(--accent); list-style: none; }}
nav.toc summary::-webkit-details-marker {{ display: none; }}
nav.toc ol {{ list-style: none; padding: 0.6rem 0 0; margin: 0; }}
nav.toc .part {{ font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 0.04em;
                 font-size: 12px; margin: 0.7rem 0 0.25rem; }}
nav.toc a {{ color: #333; text-decoration: none; display: block; padding: 2px 0 2px 1rem; }}
nav.toc a:hover {{ color: var(--accent); }}
nav.toc a.current {{ color: var(--accent); font-weight: 600; border-left: 2px solid var(--accent);
                     padding-left: calc(1rem - 2px); }}
header.chap {{ padding: 2.6rem 0 1.2rem; border-bottom: 1px solid #eee; margin-bottom: 1.6rem; }}
header.chap .kicker {{ color: var(--accent); font-weight: 700; font-size: 13px; letter-spacing: 0.06em;
                       text-transform: uppercase; }}
header.chap h1 {{ font-size: 2rem; line-height: 1.15; margin: 0.35rem 0 0; }}
h2 {{ font-size: 1.32rem; margin: 2.2rem 0 0.6rem; }}
h3 {{ font-size: 1.08rem; margin: 1.6rem 0 0.4rem; }}
p {{ margin: 0 0 1rem; }}
ul {{ margin: 0 0 1rem; padding-left: 1.3rem; }}
li {{ margin: 0.3rem 0; }}
blockquote {{ margin: 1.2rem 0; padding: 0.6rem 1.1rem; border-left: 3px solid #d8d5cc;
              color: #555; font-style: italic; background: #faf9f6; }}
code {{ background: #f0efeb; padding: 0.1em 0.35em; border-radius: 3px; font-size: 0.9em; }}
a {{ color: var(--accent); }}
.marker {{ margin: 1.3rem 0; padding: 0.75rem 1rem; border-radius: 5px; font-size: 15px; }}
.marker-fill {{ background: #fff6e5; border: 1px dashed #d8a23a; }}
.marker-more {{ background: #eef3f7; border: 1px dashed #7aa0bd; }}
.marker-tag {{ display: inline-block; font-weight: 700; font-size: 11px; letter-spacing: 0.05em;
               padding: 1px 6px; border-radius: 3px; margin-right: 0.5rem; vertical-align: 1px; }}
.marker-fill .marker-tag {{ background: #a06a12; color: #fff; }}
.marker-more .marker-tag {{ background: #4a6f8c; color: #fff; }}
.pager {{ display: flex; justify-content: space-between; align-items: stretch; gap: 1rem;
          margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid #eee; }}
.pager a, .pager .disabled {{ text-decoration: none; color: #333; flex: 1; padding: 0.7rem 0.9rem;
            border: 1px solid #e2e0da; border-radius: 6px; background: #fff; }}
.pager a:hover {{ border-color: var(--accent); }}
.pager .dir {{ display: block; font-size: 12px; color: #5f5f5f; text-transform: uppercase; letter-spacing: 0.05em; }}
.pager .ttl {{ color: var(--accent); font-weight: 600; }}
.pager .next {{ text-align: right; }}
.pager .disabled {{ visibility: hidden; }}
.pager .home {{ flex: 0 0 auto; align-self: center; }}
/* index page */
.book-title {{ padding: 3rem 0 0.5rem; }}
.book-title h1 {{ font-size: 2.4rem; margin: 0; }}
.book-title .sub {{ color: #666; margin-top: 0.4rem; }}
.idx .part {{ font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em;
             font-size: 13px; margin: 2rem 0 0.5rem; }}
.idx ol {{ list-style: none; padding: 0; margin: 0; }}
.idx li {{ margin: 0.35rem 0; }}
.idx a {{ text-decoration: none; }}
.idx .cnum {{ color: #767676; font-variant-numeric: tabular-nums; margin-right: 0.5rem; }}
"""


def _toc_prefix(c: dict) -> str:
    return "" if c.get("is_appendix") else f'Ch {c["chapter"]} · '


def _pager_label(c: dict) -> str:
    prefix = "" if c.get("is_appendix") else f'Ch {c["chapter"]} · '
    return f'{prefix}{c["chapter_title"]}'


def toc_html(chapters: list[dict], current_slug: str | None) -> str:
    rows = []
    last_part = None
    for c in chapters:
        if c["part"] != last_part:
            rows.append(f'<li class="part">Part {c["part"]} — {html.escape(c["part_title"])}</li>')
            last_part = c["part"]
        cls = "current" if c["slug"] == current_slug else ""
        rows.append(
            f'<li><a class="{cls}" href="{c["slug"]}.html">'
            f'{_toc_prefix(c)}{html.escape(c["chapter_title"])}</a></li>'
        )
    inner = "\n".join(rows)
    return (
        '<nav class="toc"><div class="toc-inner"><details>'
        "<summary>☰&nbsp; Contents</summary>"
        f'<ol>{inner}</ol></details></div></nav>'
    )


def page(title: str, toc: str, main: str, mermaid: bool = False) -> str:
    runtime = MERMAID_CDN if mermaid else ""
    # <main> landmark so the content is a single main region (axe landmark-one-main / region).
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
        f"{toc}<main class=\"wrap\">{main}</main>{runtime}</body></html>\n"
    )


# ─────────────────────────── Appendix A — the pattern catalogue (GoF format) ───────────────────────────
# Generated at build time from the catalogue entry .md files, so the appendix stays in sync with the
# catalogue rather than duplicating its text. Each entry is re-projected into the classic Gang-of-Four
# Design-Patterns layout: Intent · Motivation · Applicability · Structure · Consequences · Known Uses ·
# Related Patterns. Structure is a PLACEHOLDER mermaid diagram (a real diagram is TODO per pattern).

# role dir -> (display group name, ordering key). Mirrors INDEX.md's role grouping.
_APPENDIX_ROLES = [
    ("agent", "Agent"),
    ("models-bridge", "Models-bridge"),
    ("product", "Product"),
]

# GoF section label -> the catalogue section header prefix it is drawn from.
_SECTION_SOURCES = [
    ("Motivation", "Motivation"),
    ("Applicability", "Prerequisites"),
    ("Consequences", "Consequences"),
    ("Known Uses", "Known uses"),
    ("Related Patterns", "Related mechanisms"),
]


def _entry_title(text: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def _entry_intent(text: str) -> str:
    """The `**Intent** — …` line (may wrap across lines up to the metadata card)."""
    m = re.search(r"\*\*Intent\*\* —\s*(.+?)(?:\n\n|\n\|)", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def _fold_wrapped_bullets(md: str) -> str:
    """Join a bullet's wrapped continuation lines onto the bullet line, so the book's simple list parser
    (which requires every line of a list block to start with `- `) sees one line per bullet. The catalogue
    entries wrap long bullets across lines; without folding they render as a paragraph."""
    out: list[str] = []
    for ln in md.splitlines():
        stripped = ln.strip()
        if out and stripped and not stripped.startswith(("- ", "#", "|", ">", "```")) \
                and out[-1].strip().startswith("- "):
            out[-1] = out[-1].rstrip() + " " + stripped
        else:
            out.append(ln)
    return "\n".join(out)


def _entry_section(text: str, prefix: str) -> str:
    """The markdown body of the `## <prefix>…` section (through the next `## `), stripped. Wrapped bullet
    continuation lines are folded so the book's list parser renders them as list items, not a paragraph."""
    lines = text.splitlines()
    body: list[str] = []
    capturing = False
    for ln in lines:
        if ln.startswith("## "):
            if capturing:
                break
            capturing = ln[3:].strip().startswith(prefix)
            continue
        if capturing:
            body.append(ln)
    return _fold_wrapped_bullets("\n".join(body).strip())


_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _rewrite_entry_links(md: str, entry_dir: pathlib.Path) -> str:
    """Rewrite relative `.md` links from a catalogue entry so they resolve from `book/*.html`. An
    entry-relative `foo.md` / `../fam/bar.md` becomes `../<repo-relative>.html`; absolute URLs and
    anchors are left alone. Keeps the appendix's cross-references live on the built site."""
    def repl(m: "re.Match[str]") -> str:
        label, url = m.group(1), m.group(2).strip()
        if url.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor
        if not url.endswith(".md"):
            return m.group(0)
        try:
            target = (entry_dir / url).resolve().relative_to(ROOT.resolve())
        except ValueError:
            return m.group(0)  # points outside the repo — leave as-is
        tgt = target.as_posix()
        # `downloads/*.md` are raw assets shipped as `.md` (NOT rendered to `.html`) — keep the `.md`
        # extension, matching catalog.py's own link-rewrite rule; everything else points at rendered HTML.
        if "downloads/" in tgt:
            return f"[{label}](../{tgt}{anchor})"
        return f"[{label}](../{tgt[:-3]}.html{anchor})"
    return _MD_LINK_RE.sub(repl, md)


def _appendix_entries() -> list[dict]:
    """Read every catalogue entry .md → an ordered list of GoF-projected pattern records, grouped by role."""
    out: list[dict] = []
    for role_dir, group in _APPENDIX_ROLES:
        role_root = ROOT / role_dir
        if not role_root.is_dir():
            continue
        paths = sorted(role_root.glob("*/*.md"))
        for p in paths:
            text = p.read_text(encoding="utf-8")
            rel = p.relative_to(ROOT).as_posix()
            family = p.parent.name
            sections = {label: _rewrite_entry_links(_entry_section(text, src), p.parent)
                        for label, src in _SECTION_SOURCES}
            out.append({
                "group": group,
                "family": family,
                "rel_md": rel,
                # link back to the rendered catalogue entry (two levels up from book/appendix-*.html to root)
                "catalogue_html": "../" + rel[:-3] + ".html",
                "name": _entry_title(text, p.stem),
                "intent": _rewrite_entry_links(_entry_intent(text), p.parent),
                "sections": sections,
            })
    return out


def _appendix_pattern_md(rec: dict) -> str:
    """One pattern rendered in GoF layout as markdown the book's md_to_html understands. The Structure
    section is a PLACEHOLDER mermaid stub — a real structure diagram is TODO per pattern."""
    parts: list[str] = [f"## {rec['name']}", ""]
    if rec["intent"]:
        parts += ["**Intent** — " + rec["intent"], ""]
    src_note = (f'*Projected from the catalogue entry [{rec["family"]} / {rec["name"]}]'
                f'({rec["catalogue_html"]}). Regenerated from its `.md` at build time.*')
    parts += [src_note, ""]

    if rec["sections"].get("Motivation"):
        parts += ["### Motivation", "", rec["sections"]["Motivation"], ""]
    if rec["sections"].get("Applicability"):
        parts += ["### Applicability", "", rec["sections"]["Applicability"], ""]

    # STRUCTURE — placeholder mermaid stub + a TODO marker. Real diagram is future work.
    safe = rec["name"].replace('"', "'")
    parts += [
        "### Structure",
        "",
        "<!-- TODO: real structure diagram -->",
        "",
        "```mermaid",
        f'graph TD; TODO["TODO: structure diagram — {safe}"]',
        "```",
        "",
    ]

    # SAMPLE CODE — placeholder stub + a TODO marker. Real sample is future work.
    parts += [
        "### Sample Code",
        "",
        "<!-- TODO: sample code -->",
        "",
        "```",
        f"# TODO: sample code — {safe}",
        "```",
        "",
    ]

    if rec["sections"].get("Consequences"):
        parts += ["### Consequences", "", rec["sections"]["Consequences"], ""]
    if rec["sections"].get("Known Uses"):
        parts += ["### Known Uses", "", rec["sections"]["Known Uses"], ""]
    if rec["sections"].get("Related Patterns"):
        parts += ["### Related Patterns", "", rec["sections"]["Related Patterns"], ""]
    return "\n".join(parts).strip()


def build_appendix_chapters(next_part: int) -> list[dict]:
    """Build appendix 'chapter' records (one per role group) mirroring the chapter dict shape, so the
    existing pager/TOC/index machinery renders them. Returns [] if no entries are found."""
    entries = _appendix_entries()
    if not entries:
        return []
    chapters: list[dict] = []
    # one appendix page per role group (Agent / Models-bridge / Product), in INDEX order
    for i, (_role_dir, group) in enumerate(_APPENDIX_ROLES):
        recs = [e for e in entries if e["group"] == group]
        if not recs:
            continue
        letter = chr(ord("A") + len(chapters))  # A, B, C …
        # group patterns by family for readability
        body_parts = [
            f"Appendix {letter} re-projects the **{group}** governance mechanisms from the catalogue into "
            "the classic Gang-of-Four design-pattern layout — Intent, Motivation, Applicability, Structure, "
            "Sample Code, Consequences, Known Uses, Related Patterns. These pages are generated from the "
            "catalogue entry sources at build time, so they cannot drift from the catalogue. Each "
            "**Structure** and **Sample Code** section is a placeholder; a real diagram and sample are "
            "future work.",
            "",
        ]
        last_family = None
        for rec in recs:
            if rec["family"] != last_family:
                body_parts += [f"# {rec['family']}", ""]
                last_family = rec["family"]
            body_parts += [_appendix_pattern_md(rec), ""]
        chapters.append({
            "slug": f"appendix-{letter.lower()}-{_role_dir_slug(group)}",
            "part": next_part,
            "part_title": "Appendix A — The Pattern Catalogue",
            "chapter": 100 + i,  # sort after all real chapters
            "chapter_title": f"Appendix {letter} — {group} patterns",
            "body_md": "\n".join(body_parts).strip(),
            "is_appendix": True,
            "mermaid": True,
        })
    return chapters


def _role_dir_slug(group: str) -> str:
    return group.lower().replace(" ", "-")


def build() -> int:
    chapters = sorted(
        (parse_chapter(p) for p in HERE.glob("ch*.md")),
        key=lambda c: c["chapter"],
    )
    if not chapters:
        print("no chapter files (ch*.md) found", file=sys.stderr)
        return 1

    # Appendix A — the pattern catalogue, projected from the catalogue entries into GoF format.
    max_part = max(c["part"] for c in chapters)
    appendix = build_appendix_chapters(next_part=max_part + 1)
    chapters = chapters + appendix

    # Per-chapter pages.
    for i, c in enumerate(chapters):
        prev_c = chapters[i - 1] if i > 0 else None
        next_c = chapters[i + 1] if i < len(chapters) - 1 else None
        num_label = "Appendix" if c.get("is_appendix") else f"Chapter {c['chapter']}"
        header = (
            f'<header class="chap"><div class="kicker">Part {c["part"]} · {html.escape(c["part_title"])} '
            f'&nbsp;::&nbsp; {num_label}</div>'
            f'<h1>{html.escape(c["chapter_title"])}</h1></header>'
        )
        body = md_to_html(c["body_md"])
        if prev_c:
            prev_html = (
                f'<a class="prev" href="{prev_c["slug"]}.html"><span class="dir">‹ Previous</span>'
                f'<span class="ttl">{html.escape(_pager_label(prev_c))}</span></a>'
            )
        else:
            # A disabled pager is not a link — render an empty <span> (an empty <a href="#"> trips
            # html-validate's wcag/h30 "anchor must have text" rule).
            prev_html = '<span class="prev disabled" aria-hidden="true"></span>'
        home_html = '<a class="home" href="index.html">Contents</a>'
        if next_c:
            next_html = (
                f'<a class="next" href="{next_c["slug"]}.html"><span class="dir">Next ›</span>'
                f'<span class="ttl">{html.escape(_pager_label(next_c))}</span></a>'
            )
        else:
            next_html = '<span class="next disabled" aria-hidden="true"></span>'
        pager = f'<div class="pager">{prev_html}{home_html}{next_html}</div>'
        main = header + body + pager
        toc = toc_html(chapters, c["slug"])
        out = HERE / f'{c["slug"]}.html'
        out.write_text(
            page(f'{num_label} · {c["chapter_title"]}', toc, main, mermaid=c.get("mermaid", False)),
            encoding="utf-8",
        )

    # Index / landing page.
    idx_rows = []
    last_part = None
    for c in chapters:
        if c["part"] != last_part:
            idx_rows.append(f'<div class="part">Part {c["part"]} — {html.escape(c["part_title"])}</div>')
            idx_rows.append("<ol>")
            if last_part is not None:
                idx_rows[-2] = "</ol>" + idx_rows[-2]
            last_part = c["part"]
        idx_rows.append(
            f'<li><a href="{c["slug"]}.html">'
            f'<span class="cnum">{c["chapter"]:>2}</span>{html.escape(c["chapter_title"])}</a></li>'
        )
    idx_rows.append("</ol>")
    title_block = (
        '<div class="book-title"><h1>3D Printing Production Software</h1>'
        '<div class="sub">Engineering production software with coding agents — a governed, model-based method. '
        "<em>Draft chapters, polished from dictation.</em></div></div>"
    )
    main = title_block + '<div class="idx">' + "\n".join(idx_rows) + "</div>"
    (HERE / "index.html").write_text(
        page("3D Printing Production Software — Contents", "", main), encoding="utf-8"
    )

    print(f"built {len(chapters)} chapter pages + index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
