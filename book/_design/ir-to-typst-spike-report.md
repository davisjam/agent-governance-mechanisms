# IR → Typst → PDF — spike report

**Status:** SPIKE (de-risking proof-of-concept). Emitter: [`book/book_typst.py`](../book_typst.py). Output
is gitignored (`/book/_typst/`). The production HTML + Paged.js PDF path is untouched.

**Question this spike answers.** The book's PDF is HTML → Paged.js (headless browser) → PDF, which brings
browser artifacts, bloat, and a browser dependency. Now that we have a typed book IR
([`book/book_ir.py`](../book_ir.py)), can we emit `IR → Typst → PDF` as a print-native sibling? Two sub-
questions, both answered with evidence below: (1) is the Typst PDF good — faithful, small, fast? and (2) can
Typst carry ALL our model annotations (the feasibility study for a possible future Typst-as-source
migration)?

**Verdict:** yes to both. Typst is **~12× faster** and **~30% smaller** than Paged.js at full fidelity for
the block content, and it carries every model annotation as a native, tool-queryable construct — a **146/146
round-trip** of our index/point annotations through `typst query`. Recommendation: build out the full Typst
PDF path. It also **de-risks** a future Typst-as-source migration: only the display-equation syntax needs
real authoring work; everything else maps clean.

---

## 1. The annotation → Typst mapping table (the feasibility verdict)

Every directive walked by the IR, mapped to a Typst-native construct and exercised on real chapters. The
emitter reuses the IR's `classify_render_block` and `Block` taxonomy — it is a `render_typst(block)` sibling
to `Block.render_html()`, not a second parser.

| Our directive | Typst construct | Status | Evidence |
|---|---|---|---|
| `<!-- label: k -->` + `[ref:k]` | `#figure(…) <k>` + `@k` | **clean** | 2.5: `@metric-spectrum`→"Figure 1", `@metrics-table`→"Table 1", both **linked** in the PDF |
| `<!-- figure: path \| cap -->` | `#figure(image("/…"), caption: […])` | **clean** | 3.1: `trunk-and-views.svg` renders as numbered "Figure 1" with caption |
| standalone ` ```mermaid ` | `#figure(image(<cached SVG>), caption)` | **clean, one caveat** | 2.5/3.1/appendix diagrams render; **caveat: mermaid SVGs carry `<foreignObject>`** — Typst warns "might render incorrectly" (83 warnings whole-book) but they DID render correctly in every page inspected |
| pipe table | `#figure(table(…), kind: table) <k>` | **clean** | 2.5: numbered "Table 1", booktabs 3-rule style, right-align on `---:` columns |
| ` ```lang ` fenced code | `#raw(…, block: true, lang: …)` | **clean** | code blocks render with the fence body escaped safely (a `$` or ``` inside never breaks) |
| heading `#`..`####` | `=`..`====` | **clean** | `{#slug}` anchor stripped; `## [role: X]` kicker → emphasised lead |
| unordered / ordered list | `- item` / `+ item` | **clean** | wrapped-line continuations fold into one item, matching the HTML renderer |
| blockquote `>` | `#quote(block: true)[…]` (recursive) | **clean** | concept insets / theses render; inner markdown recursed |
| `<!-- inset: T -->` + fence | bordered `#block` + bold title + body | **clean** | titled code/mermaid inset boxes |
| `<!-- eq: … -->` | `$ … $` block math | **awkward** | our equations are unicode prose (`P(wrong) = 1 − (1 − p)ⁿ`), not Typst math; a best-effort bridge quotes multi-letter words and maps operators. Renders correctly (`𝑃(wrong)=1−(1−𝑝)ⁿ`) but a real migration would author math in Typst's language |
| `{{token}}` metric | value substitution | **clean (upstream)** | done in the IR text via `build_book_html._apply_metrics`; the emitter sees resolved prose (`data/metrics.json`) |
| `<!-- index-def: slug -->` | `#metadata((slug, kind:"index-def")) <…>` | **clean** | 3.1: 13 tags → 13 `#metadata` nodes, all `typst query`-extractable |
| `<!-- index-example: slug -->` | `#metadata((slug, kind:"index-example"))` | **clean** | round-trips with its kind |
| `<!-- point: slug \| text -->` (planned) | `#metadata((slug, kind:"point", text)) <…>` | **clean** | synthetic round-trip: `typst query` returns `{slug, kind:"point", text:"…"}` — the payload survives |

**The crux — `#metadata` + `typst query`.** Typst's purpose-built mechanism for embedded, tool-queryable
data is `#metadata(value) <label>` plus `typst query <doc> metadata`. Our HTML build stamps index anchors on
the DOM for a harvester to read; Typst holds the same annotations as first-class document values an external
tool extracts. **Whole-book result: 146 index/point annotations in the IR → 146 `#metadata` nodes extracted
by `typst query`.** An exact round-trip. This is the decisive evidence that Typst can hold the whole model,
not just render it.

```
$ typst query --root <repo> _typst/whole-book.typ metadata --field value
[{"slug":"model-as-map","kind":"index-example"},{"slug":"model-zoo","kind":"index-def"}, … 146 total]
```

(`typst query` is deprecated in 0.15 in favour of `typst eval 'query(metadata)…'`; both work today.)

---

## 2. Head-to-head: Typst vs Paged.js (whole book, real numbers)

Measured on the full 111-chapter book (incl. appendices), same machine, warm mermaid cache.

| Path | Pages | Size | Build time | Tagged (a11y) |
|---|---|---|---|---|
| **Paged.js (current)** | 381 | **7.10 MB** | **22.6 s** (Puppeteer layout + qpdf) | yes |
| **Typst (spike)** | 386 | **4.98 MB** | **1.9 s** (0.7 s emit + 1.2 s compile) | yes |

- **Speed: ~12× faster.** 1.9 s vs 22.6 s. No headless browser — a single native binary lays out the whole
  book in ~1 s. This alone is a strong reason to prefer it in CI.
- **Size: ~30% smaller.** 4.98 MB vs 7.10 MB (both figure-heavy; the delta is Typst's tighter PDF output, not
  fewer figures).
- **Accessibility parity.** Both emit a tagged PDF (struct tree present) — Typst does not regress a11y.
- **Word count:** 127,560 (Typst) vs 133,686 (Paged.js), ~95%. The delta is the generated front-matter the
  HTML build inserts that this spike does not yet emit (List of Figures, auto-glossary) plus the catalogue-
  iframe figures (web-only; correctly dropped in print).

**Fidelity — what looked better/worse.** Typography is clean and print-native (justified, proper hyphenation,
Georgia serif). Tables render in the book's booktabs 3-rule style. Cross-references are live links. The one
worse spot is the mermaid `<foreignObject>` warning — see below.

---

## 3. What mapped cleanly vs awkwardly

**Clean (most of it).** Labels/refs, figure directives, tables, code, headings, lists, blockquotes,
metrics, and — the crux — the `#metadata` annotations. The `[ref:k]` → `@k` mapping is a genuine upgrade:
Typst resolves and numbers cross-references natively, where the HTML build hand-rolls a numbering pre-pass +
a `data-label` map + a `[ref:]` regex resolver.

**Awkward — three named spots:**

1. **Mermaid SVG inclusion.** Mermaid renders labels inside `<foreignObject>` (embedded XHTML). Typst
   supports `image()` for SVG but flags foreign objects as possibly-mis-rendering (83 warnings whole-book,
   one per diagram). In every page inspected they rendered correctly, but this is the fidelity risk to watch.
   *Mitigation for a full build:* render mermaid to PDF/PNG (via `mmdc`'s PDF output or a rasterize step) so
   no `<foreignObject>` reaches Typst — trading vector crispness for guaranteed fidelity. The emitter already
   reuses the HTML build's content-hashed SVG cache, so switching the cached artifact's format is localized.

2. **The `<!-- eq: … -->` equations.** Our equations are unicode-prose strings, not math markup. The bridge
   (`_math_ish`) quotes multi-letter words and maps a handful of operators; it renders correctly but is
   best-effort. A Typst-as-source migration would author these in Typst's math language directly.

3. **`{{token}}` metrics — not the emitter's job.** Substitution happens upstream in the IR text
   (`_apply_metrics`), so the emitter sees resolved prose. Clean by construction, but worth noting the token
   layer lives in the shared tokenizer, not in either projection.

**A bug the full-corpus run caught** (bug-finding affordance): the inline converter's placeholder-stash
scheme collided across recursion (a code-span nested in bold restored against the wrong stash → `IndexError`
on ~5 chapters). Fixed by threading one shared stash through the recursion. A second whole-book finding: a
bare multi-letter word in an `<!-- eq: -->` (`P(wrong)`) is an undefined Typst math variable → compile error;
fixed in `_math_ish`. Both were invisible on the 3 sample chapters and only surfaced at book scale — evidence
that the whole-book compile is the right stress test.

---

## 4. Recommendation

**Build out the full Typst PDF path.** The evidence is decisive: ~12× faster, ~30% smaller, tagged, and
faithful to the book's typography and booktabs tables — with no headless browser in the loop. The remaining
work to reach parity with the current PDF is bounded and known: emit the generated front-matter (List of
Figures, auto-glossary), decide the mermaid-fidelity approach (rasterize vs. keep-SVG-and-accept-the-
warning), and add the book cover / TOC / running heads. None of it is architectural — the IR already holds
everything.

**Does the mapping de-risk a future Typst-as-SOURCE migration?** Substantially, yes. Every model annotation
survives to a native, queryable construct — the `#metadata`/`query` round-trip is complete (146/146), so the
index-and-point layer that today rides HTML comments would carry over cleanly. The only annotation that does
NOT map effortlessly is the display equation (`<!-- eq: -->`), which would need real Typst-math authoring
rather than a prose bridge — a small, localized cost. Labels/refs, figures, tables, and metadata all map to
things Typst does *better* natively than our bespoke stack. The source-migration blockers named in
`IR-DESIGN.md` remain (clone-and-run, Typst's HTML-export maturity, GitHub source-degradation) — this spike
touches none of those — but on the annotation-fidelity axis it clears the bar.

**How to reproduce.**

```bash
brew install typst
cd book
python3 book_typst.py 3.1-the-executable-zoo --out _typst/3.1.typ
typst compile --root .. _typst/3.1.typ _typst/3.1.pdf
typst query --root .. _typst/3.1.typ metadata --field value   # extract the model annotations
```
