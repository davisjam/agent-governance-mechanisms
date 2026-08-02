# The plain-text citation model — how to cite in the book's markup

**Mode: reference.** This is the spec an author or agent consults *before writing a citation or
note* in any `book/**.md` chapter body. It documents the inline bracket-marker family as the
parser actually implements it (`build_book_html.py`), not as one might wish it worked. The
subsystem design rationale lives in
[`bibliography-subsystem-260801.md`](bibliography-subsystem-260801.md); this doc is the
author-facing contract.

## The marker family at a glance

| Marker | Job | Renders as | Resolved against |
|---|---|---|---|
| `[cite: key]` | Scholarly citation | Numeric superscript `¹` + right-gutter Chicago note (first use) | `references.bib` → `data/citations.json` |
| `[note: text]` | Editorial sidenote | Symbolic superscript `* † ‡ § ‖ ¶` + right-gutter editorial note | Nothing — body is the content |
| `[ref: key]` | Float cross-reference | Linked "Figure N" / "Table N" | A float's `<!-- label: key -->` |
| `[data: slug]` | Data-claim cross-reference | Inline text link into the data chapter | `data/data-claims.json` |
| `[[slug\|text]]` / `[[slug]]` | Abstraction citation | Link into the catalogue glossary | `../ABSTRACTIONS.html` anchors |

All five fail the build loud on an unresolvable key/slug — a dead reference never ships as
literal bracket text.

## `[cite:]` — syntax and semantics

Grammar (SSOT regex: `_CITE_MARKER_RE = r"\[cite:\s*([^\]]+?)\s*\]"`; payload split by
`parse_cite_spec`):

- **Single work:** `[cite: winters2020]`
- **With locator** (page/chapter, anything after the first comma): `[cite: winters2020, 42]`,
  `[cite: brambilla2017, ch. 2]` — the locator renders appended to the gutter note (", 42").
- **Multiple works, one marker:** `;`-separated — `[cite: gof1994; brooks1995, 7]` renders two
  superscripts.
- The payload may not contain `]` (the regex stops at the first one).

Semantics: per chapter, each **distinct** key takes the next integer in first-reference order; a
repeat reuses its number. The superscript links to the chapter's **Works Cited** entry of the
same number (invariant BIB-4, the mirror). The gutter citation note (Chicago note form) is
emitted **only on the key's first occurrence** in the chapter.

Where it renders — three surfaces, one data source:

1. **In prose:** `<sup class="cite-ref">` numeric superscript + (first use) a
   `span.cite-note` right-gutter note.
2. **Per-chapter Works Cited:** numbered `<ol>`, first-reference order, appended to the chapter.
3. **End-of-book Bibliography:** the alphabetical union (by author surname) of every key cited
   anywhere. Also feeds the per-chapter Google Scholar `citation_reference` head meta.

A key must exist in `references.bib` AND in the committed render `data/citations.json` (produced
by `render_citations.py`; never hand-edited). New key workflow: add the BibTeX entry to
`references.bib`, run `python3 book/render_citations.py`, commit both.

## `[note:]` — syntax and semantics

Grammar: `_NOTE_MARKER_RE = r"\[note:\s*(.+?)\s*\]"` (DOTALL). The body runs to the **first**
`]` in the source.

- **Form:** `[note: One or more plain sentences.]`
- **Symbology:** the per-chapter note counter walks `* † ‡ § ‖ ¶`, then doubles (`** ††` …) —
  disjoint from the numeric citation glyphs by construction (gate CITE-SYMBOLOGY).
- **Renders:** `<sup class="note-ref" role="doc-noteref">` symbolic superscript (aria-label
  "note N" — the DPUB-ARIA role is what makes the label valid on a `<sup>`) + a
  `span.editorial-note` in the right gutter. Notes and citations number independently.
- **Placement:** immediately after the sentence it annotates, superscript-style (after the
  period). Fine inside list items — wrapped continuation lines fold into one string before the
  inline pass, so the marker may span source lines.

### The note body is strictly plain text

Three hard rules, all consequences of how `inline()` scans:

1. **No `]` anywhere in the body.** The non-greedy regex stops at the first `]` — a bracketed
   aside or markdown link truncates the note and leaks the tail into the prose.
2. **No markdown.** The note renders before the link/bold/italic passes and its output is
   shielded from them, so `*italic*`, `**bold**`, and `[text](url)` inside a body stay literal
   (or truncate, per rule 1). Parenthetical attribution is the sanctioned form:
   `(Brambilla, Cabot, and Wimmer, ch. 2)`.
3. **No stashed constructs: no `` `code` ``, no `[+…+]`, and no `[cite:]`** — see the nesting
   rule below.

## The nesting rule: `[cite:]` does NOT nest inside `[note:]`

**Determined empirically (260802) against `inline()` — do not retry it; the failure is silent
until the page renders garbage.**

Why, mechanically: `inline()` shields rendered fragments behind `\x00…\x00` placeholders and
restores each family in a **single, non-recursive** `re.sub` pass at the end. The cite pass runs
*before* the note pass, so for `[note: … [cite: key] …]`:

1. The inner cite renders fine and is stashed as `\x00CITE0\x00` — the note body now contains
   the placeholder instead of the marker (so the note is *not* truncated at the cite's `]`;
   that is what makes the failure sneaky).
2. The note renders around it and is stashed as `\x00CITE1\x00`.
3. The final restore expands `\x00CITE1\x00` in the page string — but replacement text is never
   rescanned, so the inner `\x00CITE0\x00` ships **literally** inside the editorial note.

Test that confirms it: `inline("[note: a [cite: brambilla2017] b]")` →
`…<span class="editorial-note">… a \x00CITE0\x00 b</span>` (NUL placeholder in output). The same
single-pass restore bites `` `code` `` and `[+…+]` inside a note body.

Even if the restore looped, the render would still be wrong: the cite's gutter note would nest
inside the editorial note's gutter span. A citation and an editorial note are two independent
gutter artifacts; the model keeps them siblings, never parent/child.

**The sanctioned forms when a note needs a source:**

- **Prose attribution inside the note** (no marker):
  `[note: … The MDSE text (Brambilla, Cabot, and Wimmer, ch. 2) draws the tower in full.]`
- **Sibling markers** when the numeric citation must appear: close the note, then cite —
  `… tower.] [cite: brambilla2017, ch. 2]` — two superscripts, two gutter entries.

Live example of the first form: the M0–M3 metamodel sidenote in
`part3/3.1-the-executable-zoo.md` ("How to read a model page", field (b)).

## The sibling markers (for disambiguation)

- **`[ref: key]`** — cross-reference to a captioned float. Resolved in a **post-render pass over
  the HTML** (not in `inline()`) against the label map built from `<!-- label: key -->` float
  comments; a dangling key fails the build. Emits a linked "Figure N" / "Table N".
- **`[data: slug]`** — resolved at **chapter-assembly time** (before `inline()`) against
  `data/data-claims.json`; unknown slug fails the build. Emits an inline "For the data, see …"
  link, not a superscript.
- **`[[slug|text]]` / `[[slug]]`** — abstraction citation into the catalogue glossary; runs
  before the cite/note passes inside `inline()`.

None of these three participate in the citation numbering or the Works Cited / Bibliography.

## Escaping and shielding rules

- **Backticks shield everything:** `` `[cite: x]` `` renders as literal code, never as a
  citation — code spans are stashed before any marker pass runs. Use this to *mention* a marker
  (as this doc's source does) rather than *use* it.
- Marker payloads are matched **after** HTML-escaping, so `&`, `<`, `>` in a note body are safe.
- There is no escape character for a literal `[cite:` in prose outside code spans — wrap it in
  backticks.

## Processing order in `inline()` (the whole model in one list)

1. `[+…+]` intra-word emphasis — stashed (pre-escape)
2. HTML-escape
3. `` `code` `` spans — stashed
4. `[[slug|text]]` → glossary links
5. `[cite:]` → rendered + stashed
6. `[note:]` → rendered + stashed
7. `[text](url)` markdown links
8. `**bold**`, then `*italic*`
9. Restore CODE, EM, CITE/NOTE stashes — each a single non-recursive pass (⇒ the nesting rule)

(`[data:]` runs before this pipeline at chapter level; `[ref:]` after it, over the HTML.)

## Gates that hold the model

All run in `catalog.py validate` / `tests/citations.py` (invariant IDs from the design doc §8):

| Gate | Invariant | Holds |
|---|---|---|
| CITE-RESOLVE | BIB-2 | Every `[cite:]` key exists in `references.bib`; markers parse. Imports the SSOT regexes from the build module — the gate cannot drift from the parser. |
| CITE-FRESH | BIB-6 | `citations.json` stamp-hash matches `references.bib` + the cited-key set; stale → "run render_citations.py". |
| CITE-MIRROR | BIB-4 | In built HTML, superscript N links to Works Cited entry N. |
| CITE-SYMBOLOGY | BIB-7 | Citation glyphs (digits) and note glyphs (`*†‡§‖¶`) stay disjoint. |
| CITE-PARITY | BIB-5 | Both surfaces read the one `.bib` / JSON. |
| SCHOLAR-META | BIB-8 | Chapter `<head>` carries `citation_*` tags + one `citation_reference` per cited work. |
| CITE-ORPHANS | — | A `.bib` entry never cited is an audit finding (non-fatal). |

An unresolvable `[cite:]` or `[data:]` also fails the **build itself** (`SystemExit`), before any
gate runs.

## Gotchas checklist (read before writing a citation)

- [ ] Cite key exists in `references.bib` AND `data/citations.json` is regenerated (CITE-FRESH).
- [ ] Note body: no `]`, no markdown, no backticks, no `[cite:]`, no `[+…+]`.
- [ ] Need a source in a note? Prose attribution in parentheses, or a sibling `[cite:]` after
  the closing `]`.
- [ ] Locator goes after the first comma: `[cite: key, 42]`; multiple works use `;`.
- [ ] Mentioning (not using) a marker? Wrap it in backticks.
- [ ] Markers may wrap across source lines inside a paragraph or list item; keep the whole
  marker within one block.
