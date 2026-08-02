# Bibliography & Citation Subsystem — Design + Feasibility (260801)

**Status:** DESIGN + FEASIBILITY. No implementation landed. Awaiting author ratification of the
feasibility verdict (§2) and the renderer decision (§3) before any build phase.

**Scope:** a real citation subsystem for the MAGE book. One BibTeX `.bib` file is the single source
of truth; Chicago-style renderings are *projected* from it onto both surfaces — the HTML web book
(`book/build_book_html.py`) and the Typst PDF (`book/book_typst.py`). Three projections: in-text
footnote→sidebar citations, an end-of-chapter numeric **Works Cited**, and an end-of-book
alphabetical **Bibliography**. Plus Google Scholar crawlability via highwire meta tags.

**Path note:** written to `docs/design/` per the dispatch brief. The book's own design docs live under
`book/_design/`; if the author prefers, this belongs there (`book/_design/bibliography-subsystem-260801.md`).

---

## §1. The problem, and the one risk that matters

The book cites ~15 scholarly works today (§7), all as loose prose — "Winters, Manshreck, and
Wright, 2020," "the Gang of Four," "Brooks in *No Silver Bullet*." Nothing is a structured citation.
There is no Works Cited, no bibliography, no machine-readable reference metadata for Scholar.

A `.bib` SSOT fixes the *data* drift by construction: author, title, year live once. The residual
risk is **formatting drift across the two surfaces**. If the HTML book renders Chicago with one
engine and the PDF renders it with another, "Winters, Titus, Tom Manshreck, and Hyrum Wright" on one
surface can become "Winters, T., T. Manshreck and H. Wright" on the other — same data, same style
name, different strings. The whole design turns on removing that risk.

**This is not hypothetical.** The feasibility spike (§2) rendered the *same* `chicago-author-date`
CSL against the *same* two-entry `.bib` with two engines and got two different strings — one of them
carrying an actual rendering bug. Two native renderers drift. The architecture must render Chicago
**once**.

---

## §2. Feasibility verdict (grounded in spikes)

Every claim below was run on 2026-08-01 against the CI-pinned toolchain (Typst 0.15.1, the exact
version `.github/workflows/pages.yml` installs) and Python 3.14 in a throwaway venv.

### 2.1. Typst native Chicago — CONFIRMED, zero new dependency

Typst 0.15.1 ships Chicago natively. `#bibliography("refs.bib", style: "chicago-author-date")` and
`style: "chicago-notes"` both compile clean; the `-bibliography`-suffixed names are invalid. Extracted
PDF text:

> Cited (Winters et al. 2020) and (Gamma et al. 1994).
> Works Cited
> Gamma, Erich, Richard Helm, Ralph Johnson, and John Vlissides. 1994. *Design Patterns…*. Addison-Wesley.
> Winters, Titus, Tom Manshreck, and Hyrum Wright. 2020. *Software Engineering at Google*. O'Reilly Media.

Typst is **already a required build binary** for the PDF (a downloaded release, not a pip package),
so using it costs nothing against the clone-and-run rule.

### 2.2. citeproc-py for HTML — installs, but drifts and needs a compiled dep

- **Install:** `pip install citeproc-py` succeeds; it pulls **`lxml`** (a compiled C-extension wheel).
  On the Ubuntu CI runner `lxml` has a manylinux wheel, so it installs without `apt` — but it is a
  binary dependency, not pure Python.
- **Chicago is not bundled.** citeproc-py ships exactly one style (`harvard-cite-them-right.csl`).
  Chicago requires either the extra **`citeproc-py-styles`** package (a *second* dependency) or a
  **vendored CSL file**. Passing a local `chicago-author-date.csl` path works.
- **It drifts from Typst, and it is buggy.** Same CSL, same data, citeproc-py 0.10.3 emitted:
  > Winters, T., T. Manshreck**and** H. Wright. 1994…
  Initials instead of full given names, and a missing space/comma ("Manshreckand"). This is the
  weaker engine.

**Verdict on citeproc-py:** rejected as a *second* live renderer. It would add a compiled dependency
to the build path AND reintroduce exactly the drift the `.bib` SSOT exists to kill.

### 2.3. Can we extract Typst's strings for HTML? — partially, two routes

To make Typst the *single* engine, the HTML surface must consume Typst-rendered strings. Two routes,
tested:

- **`typst query bibliography`** → returns `[]` (the rendered reference strings are not exposed as
  queryable fields; `ref` elements give only citation *targets*). Not usable directly.
- **`typst compile --features html`** of a minimal bibliography-only document → **produced the
  correct Chicago strings as HTML** ("Winters, Titus, Tom Manshreck, and Hyrum Wright…"). Typst flags
  HTML export "experimental — do not rely on for production," but for a *tiny, author-controlled*
  input (only the reference list, no prose) the surface area is small and the output was correct.

### 2.4. Recommendation — ONE renderer, the Typst/Hayagriva engine, both surfaces consume it

Render Chicago **once**, through Typst's own bibliography engine (**Hayagriva**), and feed both
surfaces from that one output. Rationale:

1. **Drift-proof by construction** — the HTML strings *are* the PDF strings; they cannot differ.
2. **No new pip dependency** — Typst is already required; the clone-and-run rule for `catalog.py`
   stays intact (the HTML build reads a committed/generated JSON with stdlib `json`, §11).
3. **Best quality** — Typst's output is clean; citeproc-py's is not.

**Extraction mechanism** (Phase 1 confirms the primary; the fallback is already proven):
- **Primary — the Hayagriva CLI.** Hayagriva is the Rust library Typst embeds; its standalone CLI
  renders references/citations in a CSL style, byte-identical to `#bibliography`. It is a downloaded
  binary like Typst (no pip). *Not installed in the spike env (no cargo); confirm availability and
  output shape in Phase 1.*
- **Fallback — Typst experimental HTML export** of a generated `_citations.typ` manifest (§3.2),
  harvested into `citations.json`. Proven in 2.3.

If neither route hardens acceptably, the fallback-of-last-resort is citeproc-py generating the
committed JSON that **both** surfaces consume (Typst then renders from strings, not `@key`), so the
two surfaces still match — accepting citeproc-py's lower quality on *both*. This is explicitly the
least-preferred option and is recorded only for completeness.

---

## §3. Architecture — bib SSOT → single renderer → three projections × two surfaces

```
book/references.bib   ← single source of truth (all scholarly works)
        │
        ▼
 render_citations.py  ← Phase-1 tool: runs the Typst/Hayagriva engine ONCE
        │                (Hayagriva CLI, or a generated _citations.typ + HTML export)
        ▼
 book/data/citations.json   ← generated artifact: per-key rendered strings + metadata
   { "<key>": {
       "note_html":  "…",   // Chicago note form (for the sidebar citation)
       "works_cited_html": "…",  // numbered end-of-chapter entry body
       "bib_html":   "…",   // alphabetical end-of-book entry body
       "csl": { "title":…, "author":[…], "year":…, "container":…, "url":… }  // → Scholar meta
   }, … }
        │                                   │
        ▼                                   ▼
build_book_html.py                     book_typst.py
  reads citations.json (stdlib json)     reads citations.json (or renders @key natively —
  → numeric sidebar notes                  see §3.3 note)
  → per-chapter Works Cited
  → end-of-book Bibliography page
  → highwire <meta> in <head>
```

### 3.1. The SSOT file — `book/references.bib`

A standard BibTeX file, one entry per scholarly work, keyed `authorYEAR` (e.g. `winters2020`,
`gof1994`, `brooks1995`). This is the *only* place a reference's data lives. Wikipedia glossary links
(SysML, timed automata, MDA) are **not** scholarly citations and stay as ordinary inline links —
§7 draws the line.

### 3.2. The renderer — `book/render_citations.py` (single authority)

A dev/CI-time tool (not on the clone-and-run path). It reads `references.bib`, drives the
Typst/Hayagriva engine once, and writes `book/data/citations.json`. In CI it can regenerate fresh on
every push (Typst is installed there — the same pattern the PDF and the mermaid SVGs already use);
locally the JSON is a committed cache refreshed on demand, guarded by a freshness gate (§9). The tool
obeys the tool-output-naming discipline (a planned-actions preamble + a machine-parseable result
summary; timestamped log if it writes one).

### 3.3. The two surfaces

- **HTML (`build_book_html.py`)** reads `citations.json` and emits the three projections plus the
  `<head>` meta. The `page()` head is minimal today (§10) and must grow a meta-block parameter.
- **Typst (`book_typst.py`)** *may* consume the same JSON strings, OR use native `#cite(<key>)` +
  `#bibliography(style:"chicago-notes")` directly. **Because Typst *is* the reference engine, its
  native output equals the JSON strings** — so either is drift-free. Native `@key` is simpler and
  gives real intra-PDF links; recommended for the PDF, with the JSON reserved for the HTML side. The
  one shared input — `references.bib` — guarantees the surfaces agree.

---

## §4. Citation & note syntax — two symbologies, distinct at a glance

### 4.1. What the book renders today (grep-confirmed)

The current sidenote/footnote family is **anchorless**. Asides render as right-gutter Tufte
blockquotes (`blockquote.aside-sidenote`) with **no in-text reference marker** — no superscript,
no counter, no symbol. Kinds: a plain aside, an em-led "footnote" (`> *A footnote…*`), and a
term-labeled definition sidenote (`> **Term.** …`). The `[data: slug]` marker renders an *inline
text link* ("For the data, see …"), not a marker. `[ref:key]` cross-refs floats; `[[slug|text]]`
links the abstractions glossary. **No numeric or symbolic marker sequence exists to collide with.**

That is the opening the author's steer needs: the two new marker families start on a clean field.

### 4.2. The two-symbology scheme

- **Citations → numeric superscript** (`¹ ² ³ …`). A new inline marker **`[cite: <key>]`** (locator
  optional: `[cite: winters2020, 42]`; multiple: `[cite: gof1994; brooks1995]`). It joins the
  existing inline bracket-marker family (`[ref:]`, `[data:]`, `[[…]]`) so it fits the book's
  conventions by construction. Renders a numeric superscript in prose, linked to a right-gutter
  **citation note** carrying the Chicago note string. The number equals the citation's Works-Cited
  entry number (§5).
- **Explanatory notes → symbolic superscript** (`* † ‡ § ‖ ¶`, then doubled `** †† …`). A new inline
  marker **`[note: <text>]`** renders a symbolic superscript linked to a right-gutter **editorial
  note**. This gives genuine footnotes an in-text anchor on a sequence visibly distinct from
  citations.
- **Existing definition/aside sidenotes are untouched.** `> **Term.** …` and plain `> *…*` asides
  keep their current anchorless, label-led rendering — already a third, visually distinct class. This
  honors "least disrupt the existing look": the rework is *additive*, not a migration of what works.

**Why symbols for notes, numbers for citations** (not the reverse): citations must carry a *stable
ordinal* that mirrors the numbered Works Cited (§5) — numbers are the natural fit. Notes have no such
mirror; a symbolic run keeps them unmistakably not-a-citation.

### 4.3. Rendering on both surfaces

- **HTML:** `[cite:]` → `<sup class="cite-ref"><a href="#cite-c<lang>-N">N</a></sup>` + a
  `blockquote.cite-note` (a new sibling class beside `aside-sidenote`, same gutter geometry).
  `[note:]` → `<sup class="note-ref">†</sup>` + `blockquote.editorial-note`. Both reuse the existing
  Tufte gutter CSS so the look matches; only the marker glyph is new.
- **Typst:** `[cite:]` → `#cite(<key>)` (numbered, via `chicago-notes`) rendered into the margin with
  the book's existing sidenote mechanism; `[note:]` → a symbolic-marked margin note. Typst numbers
  citation notes natively; the symbolic sequence for `[note:]` is a small counter in the template.

---

## §5. Numbering & mirroring mechanics

- **Per-chapter numeric citation run.** Within a chapter, each *distinct* `[cite: key]` takes the next
  integer in first-reference order. A repeat of the same key reuses its number (standard). The run
  resets at each chapter.
- **Sidebar number == Works-Cited number.** The end-of-chapter **Works Cited** lists the chapter's
  cited works numbered `1..K` in that same first-reference order. So citation ³ in the prose is entry
  3 in that chapter's Works Cited — the mirror the author asked for. The sidebar note and the Works
  Cited entry render from the *same* `citations.json` strings.
- **End-of-book Bibliography — alphabetical union.** A new back-matter page joins every cited key
  across all chapters, deduplicates, and renders the standard Chicago **alphabetical** bibliography
  (by author surname), unnumbered. Built from the same JSON; ordering is the only difference from
  Works Cited.
- **Notes run independently.** The symbolic `[note:]` sequence has its own per-chapter counter and
  never shares numbering with citations.

---

## §6. Google Scholar crawlability — highwire meta tags

Scholar indexes pages that expose **highwire_press** `<meta>` tags in `<head>`. The `.bib` metadata
feeds them directly. Emit, per chapter page (the book is the scholarly work; each chapter page is a
crawlable unit):

- `citation_title` — the chapter title (or book title on the landing).
- `citation_author` — the book's author (repeatable).
- `citation_publication_date` / `citation_online_date` — the book's date.
- `citation_book_title` — the book title (marks chapters as book sections).
- `citation_fulltext_html_url` — the chapter's canonical Pages URL.
- `citation_pdf_url` — `…/book/mage-book.pdf` (the print edition).
- `citation_reference` — **one per cited work on that page**, in Scholar's compressed form
  (`citation_title=…;citation_author=…;citation_publication_date=…`). This is what lets Scholar build
  the citation graph *out* of the book. Generated straight from `citations.json`'s `csl` block for
  the keys cited on the page.

The end-of-book Bibliography page additionally emits a `citation_reference` for every entry, giving
Scholar one page with the whole reference list. (Optional hardening: COinS `<span class="Z3988">`
spans on each bibliography entry for Zotero/COinS harvesters — low cost, additive.)

`page()`'s `<head>` builder must take an optional meta-block string (§10).

---

## §7. Existing references to migrate into `references.bib`

Grep-confirmed inline citations (scholarly works → `.bib` + `[cite:]`):

| Key (proposed) | Work | Cited in |
|---|---|---|
| `winters2020` | Winters, Manshreck & Wright, *Software Engineering at Google* (2020, O'Reilly) | preface, conclusion, 6.0 |
| `gof1994` | Gamma, Helm, Johnson & Vlissides, *Design Patterns* (1994, Addison-Wesley) | preface, conclusion |
| `brambilla2017` | Brambilla, Cabot & Wimmer, *Model-Driven Software Engineering in Practice* (2017) | preface (0.1) |
| `brooks1995` | Brooks, *The Mythical Man-Month* (anniv. ed. 1995) | 2.1, 6.0 |
| `brooks1987` | Brooks, "No Silver Bullet — Essence and Accident…" (1987) | 2.2, 3.1, 6.0 |
| `ousterhout2018` | Ousterhout, *A Philosophy of Software Design* (2018) | 2.5 |
| `leveson2011` | Leveson, *Engineering a Safer World* (2011, MIT Press, open access) | 2.3 |
| `kruchten1995` | Kruchten, "The 4+1 View Model of Architecture," *IEEE Software* (1995) | 3.1, 3.5, 3.6, 3.7 |
| `booch-uml` | Booch, Rumbaugh & Jacobson, *The UML User Guide* | 3.7 |
| `friedenthal-sysml` | Friedenthal, Moore & Steiner, *A Practical Guide to SysML* | 3.7 |
| `bass-saip` | Bass, Clements & Kazman, *Software Architecture in Practice* | 3.7 |
| `baier-katoen2008` | Baier & Katoen, *Principles of Model Checking* (2008, MIT Press) | 3.7 |
| `lamport2002` | Lamport, *Specifying Systems* (2002) | 3.7 |
| `meyer-probable` | Meyer, "From Probable to Provable" (ACM, doi:10.1145/3773295) | preface |
| `alur-dill1994` | Alur & Dill, "A Theory of Timed Automata" (1994) | 3.1, 3.7 |
| `othello-gpt` | "Emergent world representations" (arXiv:2210.13382) | (Othello-GPT ref) |
| `arxiv-2605.10712` | arXiv:2605.10712 | (linked) |

**Kept as inline links, NOT citations** (glossary/explanatory, not scholarly claims): Wikipedia
entries for SysML, timed automata, hybrid systems, Model-Driven Architecture. Drawing this line is a
judgment call to ratify — the alternative is `@online` `.bib` entries for them too.

The **"A short shelf" list in 3.7** and the **preface's four founding books** are the natural first
adopters: convert those hand-authored lists to `[cite:]` markers so the reference data unifies.

---

## §8. Invariants (stable IDs — the join keys for tests/gates)

- **BIB-1 — single source of truth.** Every rendered citation string derives from `references.bib`.
  No reference data is authored in prose, in `citations.json` by hand, or in either renderer.
- **BIB-2 — every marker resolves.** Every `[cite: key]` names a key present in `references.bib`; an
  unknown key **fails the build loud** (the pattern the `[data:]` and `{{token}}` resolvers already
  use). ENFORCED (§9, gate CITE-RESOLVE).
- **BIB-3 — one render engine.** Chicago strings are produced by exactly one engine
  (Typst/Hayagriva). Neither surface runs a second CSL processor. ENFORCED structurally (both consume
  the one artifact / one `.bib`).
- **BIB-4 — mirror.** For any chapter, the sidebar number of a citation equals its Works-Cited entry
  number. ENFORCED (§9, gate CITE-MIRROR).
- **BIB-5 — surface parity.** A key cited on both surfaces renders the same reference data. Holds by
  construction (BIB-3); a parity assertion pins it (§9, gate CITE-PARITY).
- **BIB-6 — artifact freshness.** `citations.json` is in sync with `references.bib` + the set of
  `[cite:]` markers (content hash). Stale → build fails with a "regenerate" message, like the
  committed-HTML / mermaid-cache discipline. ENFORCED (§9, gate CITE-FRESH).
- **BIB-7 — two distinct symbologies.** Citations render numeric; editorial notes render symbolic;
  the sequences never share glyphs. ENFORCED (§9, gate CITE-SYMBOLOGY).
- **BIB-8 — Scholar metadata completeness.** Every chapter page emits the required `citation_*` head
  tags; every on-page cited key emits a `citation_reference`. ENFORCED (§9, gate SCHOLAR-META).

---

## §9. Enforcement → gates

All gates live in the existing `catalog.py validate` / `tests/book.py` structural-check path — the
same place the notation-leak, orphan-page, and glossary-duplicate gates already run.

- **CITE-RESOLVE** (BIB-2) — walk every chapter body; every `[cite: key]` / `[note:]` marker parses,
  and every cite key exists in `references.bib`. Unknown key → `SystemExit` (build-fatal), mirroring
  the `[data:]` unknown-slug failure. *This is the SSOT gate the brief asks for.*
- **CITE-FRESH** (BIB-6) — hash `references.bib` + the sorted set of cite keys; compare to a stamp in
  `citations.json`. Mismatch → fail "run `render_citations.py`."
- **CITE-MIRROR** (BIB-4) — for each chapter, assert the rendered sidebar ordinals equal the Works
  Cited ordinals (walk the IR, not the HTML).
- **CITE-PARITY** (BIB-5) — assert both surfaces read the same `references.bib` / `citations.json`;
  optionally diff Typst-native reference text against the JSON strings for cited keys (normalized
  whitespace) as a drift tripwire.
- **CITE-SYMBOLOGY** (BIB-7) — assert the citation glyph set (digits) and note glyph set
  (`*†‡§‖¶`) are disjoint in rendered output.
- **SCHOLAR-META** (BIB-8) — assert each chapter page's `<head>` carries the required `citation_*`
  tags and a `citation_reference` per on-page cite.
- **Orphan `.bib` entries** — an entry never cited is an **audit finding** (not fatal): a bibliography
  may legitimately carry "further reading." Configurable to hard-fail if the author wants a tight bib.

These follow the book's audit→gate posture: a class that can be mechanically detected becomes a
standing check, not a re-inspection.

---

## §10. As-built vs design (⚠️ — where code must change)

- ⚠️ **`page()` head is meta-blind.** `build_book_html.py:page()` emits a fixed `<head>` (charset,
  viewport, title, fonts, CSS) with no hook for `<meta>` tags. Must take an optional `head_meta` arg
  so chapter pages inject highwire tags. (§6, BIB-8)
- ⚠️ **No inline `[cite:]`/`[note:]` in the marker vocabulary.** `MARKER_KEYWORDS` and the inline
  substitution family (`_XREF_RE`, `[data:]`, `[[…]]`) have no citation marker. Both the renderer and
  `book_ir.py` (which shares the tokenizer) must learn the two new inline markers. (§4)
- ⚠️ **No sidebar *reference-marked* note class.** Current asides are anchorless
  (`blockquote.aside-sidenote`). Two new gutter classes (`cite-note`, `editorial-note`) plus the
  `<sup>` marker CSS are additive beside the existing Tufte styles. (§4.3)
- ⚠️ **No Works Cited / Bibliography assembly.** Neither surface emits an end-of-chapter or
  end-of-book reference section. New assembly passes in both renderers, fed by `citations.json`. (§5)
- ⚠️ **No `references.bib`, no `render_citations.py`, no `citations.json`.** All three are new. (§3)
- ⚠️ **CI has no citation step.** `pages.yml` installs Typst already; add a `render_citations.py`
  step (and, if the Hayagriva-CLI route wins, its binary install). (§11)

Everything the design reuses — the Tufte gutter geometry, the inline-marker family, the
`SystemExit`-on-unknown-marker discipline, the committed-artifact + freshness pattern (mermaid cache,
tracked HTML) — already exists. The subsystem is mostly *assembly of existing seams*, plus one new
SSOT file and one new render step.

---

## §11. Dependency discipline & CI wiring

- **Clone-and-run for `catalog.py` is preserved.** The HTML build reads `citations.json` with stdlib
  `json`. No pip dependency enters `catalog.py`'s path. This is the reason the single-engine choice
  routes through Typst (a binary) and a committed/generated JSON, not through a pip CSL library.
- **The render engine is a binary, declared where binaries are declared.** Typst is already pinned in
  `pages.yml`. If the **Hayagriva CLI** route wins (§2.4), pin its release the same way Typst is
  pinned (download + `install -m 0755`), in the same workflow. No `package.json` / `requirements`
  change.
- **If (and only if) the citeproc-py fallback-of-last-resort is taken:** it becomes a *dev/CI-time*
  dependency of `render_citations.py`, declared in a `book/`-scoped requirements file with the
  vendored `chicago-*.csl` committed under `book/data/csl/` — never imported by `catalog.py`. This
  keeps the clone-and-run promise even in the worst case, at the cost of citeproc-py's lower quality.
- **CI step order:** `render_citations.py` runs **before** `catalog.py build` (the HTML build reads
  its output) and before `build_book_html.py --pdf`. It slots next to the existing "install Typst" /
  "render PDF" steps.

---

## §12. Phased implementation plan

- **Phase 0 — ratify (this doc).** Author confirms: single-engine-via-Typst (§2.4); the
  scholarly-vs-inline line (§7); the two-symbology glyphs (§4.2); Works Cited style = Chicago
  *notes*, end-of-book = Chicago alphabetical.
- **Phase 1 — engine + SSOT (Opus).** Confirm the Hayagriva CLI route (else lock the Typst-HTML-export
  fallback). Author `references.bib` from the §7 inventory. Build `render_citations.py` →
  `citations.json`. Land CITE-RESOLVE + CITE-FRESH gates. *No prose touched yet.*
- **Phase 2 — HTML projections.** `page()` head-meta hook; `[cite:]`/`[note:]` inline markers in the
  renderer + `book_ir.py`; numeric sidebar citation notes + symbolic editorial notes; per-chapter
  Works Cited; end-of-book Bibliography page. Land CITE-MIRROR, CITE-SYMBOLOGY, SCHOLAR-META.
- **Phase 3 — Typst projections.** Native `#cite`/`#bibliography(style:"chicago-notes")` margin
  citations + symbolic notes + Works Cited + Bibliography, matching the HTML mirror. Land CITE-PARITY.
- **Phase 4 — migrate the corpus.** Convert the §7 inline mentions to `[cite:]` markers, starting with
  the preface's four founding books and 3.7's "short shelf." Orphan-entry audit.
- **Phase 5 — Scholar hardening (optional).** COinS spans; validate against Scholar's inclusion
  guidelines.

---

## §13. Open questions for the author

1. **Works Cited style:** Chicago **notes** (numbered, matches the numeric-marker design) for the
   per-chapter list — confirm? End-of-book stays alphabetical author-date-ordered bibliography.
2. **Scholarly-vs-inline line (§7):** keep Wikipedia/glossary links inline, or pull them into
   `references.bib` as `@online` too?
3. **Note glyph order:** `* † ‡ § ‖ ¶` then doubled — acceptable, or prefer numbered-with-a-prefix
   (e.g. "note a/b/c") for accessibility? (Superscript symbols need `aria-label`s regardless.)
4. **Orphan `.bib` entries:** hard-fail (tight bib) or audit-only (allow "further reading")?
5. **`citations.json`: committed cache or CI-only artifact?** Committed matches the mermaid-cache
   precedent and keeps local HTML-only builds working without Typst; CI-only matches the PDF's
   "created never committed." Recommend **committed cache + freshness gate**.
