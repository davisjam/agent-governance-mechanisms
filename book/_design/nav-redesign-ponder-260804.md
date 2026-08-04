# Web-view per-page navigation — redesign ponder (260804)

**Status:** design only (READ-ONLY ponder). No code changed. Implementer wave applies §4.

**Problem (author):** "the navigation pane on the web view is pretty weird." The
per-page nav renders as three cluttered, redundant tiers. Prev/next chapter shows
twice; whole-book "Beginning/End" jumps aren't locally useful; there's no clean
left→right logic; the current chapter isn't named.

**Desired shape (author):** one logical left→right sequence —
`« Table of contents   « Beginning of part   « Previous chapter   [ THIS CHAPTER ]   Next chapter »   Next part »   Index »`
— backward-nav on the left, the current chapter name centered and emphasized
(non-link), forward-nav on the right. This replaces book-level Beginning/End with
per-**part** Beginning-of-part / Next-part, and drops End.

---

## 1. Current implementation (as-built)

All per-page nav lives in **`book/build_book_html.py`** and is **web-HTML-only**
(confirmed §5 — `book_typst.py` / `book_ir.py` never reference it).

### 1.1 The three tiers the author sees

Assembled per chapter in the main render loop, `build_book_html.py:4037-4043`:

```
main = header + body + pager + pager_jump + foot   # line 4042
```

- **Top nav** (`toc_html`, `:1796-1813`) — a `<nav class="toc">` with a `☰ Contents`
  `<details>` disclosure (full chapter list, current chapter highlighted) **plus a
  duplicate jump row** (`nav.toc .jump`, injected via the `jump=` arg, `:4043`).
- **Tier 1 — the pager** (`:4020-4037`): `‹ Previous / <prev title>` | `Contents`
  (→ `index.html`) | `Next › / <next title>`. Disabled ends render as
  `visibility:hidden` spans (`:4028`, `:4036`; CSS `:1645`).
- **Tier 2+3 — the jump row** (`.pager-jump` wrapping `_jump_html`, `:4039-4040`):
  a single flex row of pills that **wraps**, so the author's "row 2" (Previous part,
  Next part, Next chapter, Beginning, End) and "row 3" (Index) are one `.jump` row
  broken across two visual lines.

The **redundancy**: the jump row's `Next chapter ›` duplicates the pager's
`Next › / <title>`; the backward-part pill overlaps the pager's `‹ Previous`. The
same jump row is rendered **twice** (top nav + bottom).

### 1.2 The ordering / part model it walks

- `_discover_chapters` (`:690-718`) walks `part<N>/` dirs → an ordered `chapters`
  list, sorted by `(part, chapter)`. `_PART_DIRS` (`:277`) maps part → dir;
  `_PART_TITLES` (`:289`) names parts.
- **Part numbers are contiguous integers**: `0` frontmatter, `1-5` body,
  `6` backmatter, `7+` each appendix letter (A–E) is its own part
  (`build_appendix_chapters`, `:2663-2694`). Matter carries `is_matter=True`
  (`part in (0,6)`, `:683`); appendices `is_appendix=True`.
- So **every page has a part number**, and prev/next-part logic works uniformly
  across front-matter, body, back-matter, and appendices — no special-casing.
- `seq` (`:714-718`) is the body chapter number (1..N); matter/appendix get none.

### 1.3 Every nav target it computes today (`_jump_targets`, `:1724-1775`)

Given `chapters[idx]`:

| Target | Rule | Line |
|---|---|---|
| Backward-part (position-aware) | if `cur` **is** first-of-part → `⇐ Previous part` (prev part's first chapter); else `⇐ Beginning of this part` (current part's first chapter) | 1742-1757 |
| `Next part ⇒` | first later chapter whose `part` differs | 1758-1761 |
| `Next chapter ›` | `chapters[idx+1]`, when it isn't already the next-part jump | 1762-1766 |
| `⇤ Beginning` | `chapters[0]` (preface), unless already there | 1767-1769 |
| `End ⇥` | `chapters[-1]` (colophon), unless already there | 1770-1772 |
| `Index` | always → `book-index.html` | 1773-1774 |

The pager (`:4020-4037`) separately computes prev/next **chapter** (adjacent in
reading order) with their titles. Home → `index.html`.

**Key as-built cleverness worth preserving:** the backward control is
*position-aware* — it means "beginning of this part" mid-part and "previous part"
at a part boundary. The author's 7-slot layout wants these as **two separate fixed
slots** instead (§2).

---

## 2. The 7-item layout — adopted, sharpened, edge cases resolved

**Adopt the author's sequence.** Sharpen it into **three flex zones** so the center
name stays dead-center regardless of how many side items are present:

```
[ backward zone → hugs center ]   [ CHAPTER NAME ]   [ ← forward zone hugs center ]
  Contents · Beg-of-part · Prev-ch      (non-link)       Next-ch · Next-part · Index
```

**Final nav item list (left → right):**

| # | Item | Links to | Availability rule |
|---|---|---|---|
| 1 | **Table of contents** | `index.html` | **Always** (structural chapter-list page) |
| 2 | **« Beginning of part** | first chapter of current part | Shown **only when not already the part's first page** (else self → omit) |
| 3 | **« Previous chapter** | `chapters[idx-1]` | Shown when `idx>0`; **may cross a part boundary** (it's strict reading-order predecessor) |
| 4 | **[ Chapter name ]** | — (non-link) | **Always**; centered, emphasized |
| 5 | **Next chapter »** | `chapters[idx+1]` | Shown when `idx<len-1`; may cross a part boundary |
| 6 | **Next part »** | first later chapter with a different part | Shown when a later part exists |
| 7 | **Index »** | `book-index.html` | **Always** (alphabetized term index) |

### 2.1 Edge cases — each resolved

- **First page of book** (preface, part 0, first chapter): items 2 (self), 3
  (none) omitted. Left zone = just *Table of contents*. Right zone full. Name
  centered.
- **Last page of book** (colophon, last appendix part, last chapter): items 5, 6
  omitted. Right zone = just *Index*. Left zone full.
- **First chapter of a (non-first) part** — e.g. `2.1`: item 2 "Beginning of part"
  = self → **omit**. Item 3 "Previous chapter" = last chapter of the *previous*
  part → **shown and allowed** (crossing the boundary is the correct reading-order
  predecessor; this is the natural way to step back into the prior part). This is a
  deliberate departure from the as-built position-aware fold: the author's fixed
  slots read more predictably than a shape-shifting pill.
- **Front-matter / back-matter / appendices**: they carry real part numbers, so
  items 2/6 work **with no special-casing**. On `0.2 The Book's Language`
  (front-matter part 0): Beginning-of-part → `0.1 preface`; Next part → `1.1`
  (first body chapter). On an appendix page: Beginning-of-part → that appendix
  letter's first page; Next part → the next appendix letter. This uniformity is a
  virtue — the same code path covers every page.
- **Unavailable targets → OMIT, not disable.** Justification: (a) it matches the
  established codebase convention ("a control appears only when it can go
  somewhere", `_jump_targets` docstring `:1728`); (b) with 7 slots and frequent
  edge omissions, greyed placeholders would clutter more than they'd orient; (c)
  the **three-zone flex keeps the center anchored** and the **outer anchors of each
  zone are always present** (Table of contents / Index never omit), so positions
  stay legible without disabled stand-ins. The only items that come and go are the
  *inner* ones (Beg-of-part, Prev/Next-chapter, Next-part) — the skeleton is
  stable.
- **Current-chapter name styling**: non-link `<span>`, `font-weight:600`, accent
  color, prefixed with the reference for numbered chapters (reuse `_pager_label`,
  `:1713` — e.g. `2.1 · The Agent Stack`; matter/appendix get bare title). Long
  titles (up to ~55 chars, e.g. *Keeping the Models in Sync with the Code — A
  Measurement*): `title=` attr carries full text; CSS 2-line clamp with ellipsis on
  desktop so it never blows out the row (§3).
- **Contents vs Index — both warranted, both exist.** `index.html` = structural
  chapter list (the landing/Contents). `book-index.html` = alphabetized **term**
  index (`build_index_page`, `<h1>Index</h1>`, `:3110`). Distinct pages, distinct
  jobs — keep both.

### 2.2 Refinement I'd make to the author's layout

**One material change + two small ones:**

1. **Split the position-aware backward pill into two fixed slots** (Beginning-of-part
   *and* Previous-chapter), per the author's sequence — but note that on a part's
   first page only *Previous chapter* survives, and it crosses into the prior part.
   This is the biggest judgment (§ Return).
2. **Keep the `☰ Contents` disclosure at the top; drop the top jump row.** The top
   `nav.toc` keeps only the always-visible expandable chapter list (with
   current-chapter highlight). The 7-item sequence bar renders at the **bottom
   only**. This kills the top/bottom duplication the author flagged, and puts the
   "where next?" sequence exactly where a reader finishes a chapter. (Item 1 "Table
   of contents" in the bottom bar links `index.html`; the top disclosure is the
   in-place quick-jump. No redundancy — one is a page link, one is an inline
   expander.)
3. **Directional glyphs**: use `«` / `»` (or keep the existing `‹ › ⇐ ⇒`) but give
   each pill an `aria-label` naming the destination (the glyph reads poorly aloud —
   extend the existing `_JUMP_ARIA` map, `:1780`).

---

## 3. Responsive behavior

Book is **mobile-first**; the two-column enhancements sit behind
`@media (min-width: 60rem)` (`:1439`, `:1462`). Content wrap is `52rem` (`:1395`).
Follow the same idiom: **base = stacked; enhance to a row.**

- **Base (mobile, < 60rem)** — `flex-direction: column`, `align-items: stretch`.
  DOM order (and thus reading order) is: backward pills (wrapped, one group) →
  **chapter name** (own row, centered, larger: `card-title` role, accent) →
  forward pills (wrapped). Each zone `flex-wrap: wrap`, centered. The name stays
  prominent because it gets its own full-width centered row.
- **≥ 60rem** — `flex-direction: row`; three zones: left `flex:1;
  justify-content:flex-end`, center `flex:0 0 auto` (name, centered), right
  `flex:1; justify-content:flex-start`. Pills `white-space:nowrap`. Name capped
  with `max-width: 22rem; -webkit-line-clamp:2` + ellipsis (`title=` full text).
- **No new tokens.** Reuse: `var(--rule)`, `var(--paper)`, `var(--panel)`,
  `var(--accent)`, `var(--ink)`, `var(--muted)`, the pill geometry already in
  `.jump a` (`:1685-1688`), radius `6px`, the `12px` uppercase pill type. The
  center name uses the existing display/accent treatment (`_pager_label` + accent),
  no invented color/font.

---

## 4. Implementation spec (`build_book_html.py`)

Scope: **one file, HTML-only.** Touch four functions + the CSS block.

### 4.1 Replace `_jump_targets` (`:1724-1775`) with a structured, zone-aware builder

Return a small typed record instead of a flat list, so the renderer can place
zones and the center name. Suggested shape:

```python
def _chapter_nav(chapters: list[dict], idx: int) -> dict:
    cur = chapters[idx]
    first_of_part = next((c for c in chapters if c["part"] == cur["part"]), cur)
    back, fwd = [], []
    # 1. Table of contents — always
    back.append(("« Table of contents", "index.html", "Table of contents"))
    # 2. Beginning of part — only when not already the part's first page
    if first_of_part["slug"] != cur["slug"]:
        back.append(("« Beginning of part", f'{first_of_part["slug"]}.html',
                     f'Beginning of {_part_label(cur)}'))
    # 3. Previous chapter — strict reading-order predecessor (may cross a part)
    if idx > 0:
        back.append(("« Previous chapter", f'{chapters[idx-1]["slug"]}.html',
                     f'Previous chapter — {_pager_label(chapters[idx-1])}'))
    # 5. Next chapter
    if idx + 1 < len(chapters):
        fwd.append(("Next chapter »", f'{chapters[idx+1]["slug"]}.html',
                    f'Next chapter — {_pager_label(chapters[idx+1])}'))
    # 6. Next part
    nxt_part = next((c for c in chapters[idx+1:] if c["part"] != cur["part"]), None)
    if nxt_part:
        fwd.append(("Next part »", f'{nxt_part["slug"]}.html',
                    f'Next part — {_part_label(nxt_part)}'))
    # 7. Index — always
    fwd.append(("Index »", f"{BOOK_INDEX_SLUG}.html", "Index of terms"))
    return {"back": back, "name": _pager_label(cur), "fwd": fwd}
```

Each pill tuple is `(visible_label, href, aria_label)` — the `aria_label` supersedes
the `_JUMP_ARIA` lookup (which can be **retired**, `:1780-1783`).

Availability rules restated: TOC/Index always; Beginning-of-part iff not first-of-part;
Prev/Next-chapter by index bounds; Next-part iff a later part exists. **End and
whole-book Beginning are dropped entirely.**

### 4.2 Replace `_jump_html` (`:1786-1793`) with a zone renderer

```python
def _chapter_nav_html(chapters: list[dict], idx: int) -> str:
    nav = _chapter_nav(chapters, idx)
    def pill(label, href, aria):
        return (f'<a href="{html.escape(href, quote=True)}" '
                f'aria-label="{html.escape(aria, quote=True)}">{html.escape(label)}</a>')
    back = "".join(pill(*t) for t in nav["back"])
    fwd  = "".join(pill(*t) for t in nav["fwd"])
    name = (f'<span class="chapnav-here" title="{html.escape(nav["name"], quote=True)}">'
            f'{html.escape(nav["name"])}</span>')
    return (f'<nav class="chapnav" aria-label="Chapter navigation">'
            f'<div class="chapnav-back">{back}</div>{name}'
            f'<div class="chapnav-fwd">{fwd}</div></nav>')
```

### 4.3 Main render loop (`:4020-4043`)

- **Delete** the `prev_html` / `home_html` / `next_html` / `pager` block
  (`:4020-4037`) and the `pager_jump` block (`:4039-4040`).
- Set `nav_bar = _chapter_nav_html(chapters, i)` and
  `main = header + body + nav_bar + foot` (`:4042`).
- **Top nav:** call `toc_html(chapters, c["slug"])` **without** a `jump=` arg
  (`:4043`) — top keeps only the `☰ Contents` disclosure.

### 4.4 `toc_html` (`:1796-1813`)

Drop the `jump` parameter (or default it to `""` and stop passing it). Remove the
`{jump}` interpolation (`:1812`). No other change — the disclosure `<ol>` still
links every chapter (**this is what keeps the reachability gate green**, §5).

### 4.5 Other callers of the old jump row — the generated pages

`_jump_html` / `pager-jump` are also used by the **term-index page**
(`:3122-3131`) and the **figures/bibliography** pages (`:3534-3540`, `:653-660`).
Give each the same `_chapter_nav_html` treatment **or** a minimal fixed bar
(Table of contents · Index). Simplest: synthesize an `idx` for these generated
pages in the `chapters` order (they already appear in it, `:3555-3557`) and call
`_chapter_nav_html`. Verify no page loses its sole inbound link (§5).

### 4.6 CSS — replace the `.pager` + `.jump` + `.pager-jump` blocks (`:1637-1646`, `:1681-1699`)

Retire `.pager`, `.pager .dir/.ttl/.next/.disabled/.home`, `.pager-jump`, and the
`nav.toc .jump` rule. Add (mobile-first, tokens only):

```css
.chapnav { display:flex; flex-direction:column; gap:0.8rem; align-items:stretch;
           margin-top:3rem; padding-top:1.4rem; border-top:1px solid var(--rule); }
.chapnav-back, .chapnav-fwd { display:flex; flex-wrap:wrap; gap:0.6rem;
           justify-content:center; }
.chapnav-here { text-align:center; font-weight:600; color:var(--accent);
           font-size:18px; padding:0.2rem 0; }          /* card-title role */
.chapnav a { font-size:12px; letter-spacing:0.03em; text-transform:uppercase;
           font-weight:600; color:var(--accent); text-decoration:none;
           padding:0.5rem 0.85rem; line-height:1.1; border:1px solid var(--rule);
           border-radius:6px; background:var(--paper); }
.chapnav a:hover { border-color:var(--accent); background:var(--panel); }
@media (min-width:60rem) {
  .chapnav { flex-direction:row; align-items:center; }
  .chapnav-back { flex:1; justify-content:flex-end; }
  .chapnav-fwd  { flex:1; justify-content:flex-start; }
  .chapnav a { white-space:nowrap; }
  .chapnav-here { flex:0 0 auto; max-width:22rem; overflow:hidden;
                  text-overflow:ellipsis; display:-webkit-box;
                  -webkit-line-clamp:2; -webkit-box-orient:vertical; }
}
```

CSS classes to **retire**: `.pager*`, `.pager-jump`, `.jump` (+ `nav.toc .jump`,
`nav.toc details[open]` can stay). Reuse everything else via tokens.

---

## 5. Mechanical-check awareness

- **PDF / Typst path — UNAFFECTED (web-HTML-only).** Confirmed: `_jump_targets`,
  `_jump_html`, `toc_html`, `_kicker_html`, `pager`, `pager-jump` are referenced
  **only** in `build_book_html.py` — `grep` across `book_typst.py` / `book_ir.py`
  finds none. The PDF is paginated by Typst and carries no HTML pager. The change
  is HTML-only. **No flag needed.**
- **Reachability gate stays green** (`catalog.py:check_orphan_pages`, `:2659`). It's
  a static inbound-`href` scan. Every chapter page is linked from the `☰ Contents`
  disclosure `<ol>` (`toc_html`, present on every book page) → dropping the pager
  and Beginning/End orphans nothing (those were chapter pages the TOC already
  links). `book-index.html` keeps its inbound link via the always-present **Index**
  pill (and the landing). Figures/bibliography/list-of-figures never got links from
  the jump row, so they're unaffected — but §4.5 must confirm the generated pages
  still emit *some* inbound-linking bar so none becomes an orphan.
- **Tier-1 / html-validate:** the disabled pager `visibility:hidden` empty spans go
  away (they existed to dodge the "anchor must have text" rule, `:4026-4028`) —
  every `.chapnav a` now carries visible text, so no wcag/h30 risk. The non-link
  name is a `<span>`, not an empty `<a>`. Keep `aria-label` on every glyph pill.
- **Build determinism:** no new inputs; pure render change. `python3 catalog.py
  build` must still exit 0 (reachability) and `validate` is unaffected (nav isn't
  schema).

---

## 6. Return summary

- **Design path:** `build_book_html.py:4037-4043` (assembly) → `_jump_targets`
  `:1724`, `_jump_html` `:1786`, `toc_html` `:1796`, pager `:4020-4037`, CSS
  `:1637-1699`; part model `_discover_chapters` `:690`, `_PART_TITLES` `:289`;
  reachability `catalog.py:2659`; tokens `book-models/design-tokens.json`.
- **Web-HTML-only — PDF unaffected**, confirmed by grep (nav functions absent from
  `book_typst.py` / `book_ir.py`).
- **Biggest judgment:** (a) **split the as-built position-aware backward pill into
  two fixed slots** (Beginning-of-part + Previous-chapter) per the author's
  sequence — predictable fixed positions beat a shape-shifting pill; and (b)
  **omit-not-disable** for unavailable targets, safe because the three-zone flex
  anchors the center name and the zone-edge items (Contents/Index) never omit.
- **Refinements to the author's layout:** keep the top `☰ Contents` disclosure but
  **drop the duplicated top jump row** and render the 7-item bar **bottom-only**
  (kills the redundancy the author flagged); front/back-matter and appendices need
  **no special-casing** (contiguous part numbers make Beginning-of-part / Next-part
  meaningful everywhere); on a part's first page only *Previous chapter* survives
  and it correctly crosses into the prior part.
