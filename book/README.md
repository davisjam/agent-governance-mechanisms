# *3D Printing Production Software* — the book

Draft chapters, polished from the dictated manuscript and the author's field notes using the
**self-communicate** skill. The book renders to a small static HTML site by
`build_book_html.py` (wired into `catalog.py build`).

## Part/Chapter filesystem hierarchy

The source tree **encodes the hierarchy**: a chapter lives at `part<N>/<N>.<M>-<slug>.md`, so the
part number and chapter number are explicit in the path. `build_book_html.py` walks the tree,
derives PART.CHAPTER from the path, and reads the `<!-- part-title --> <!-- chapter-title -->`
metadata from each file. It emits one flat `<slug>.html` per chapter plus `index.html`, and appends
a Gang-of-Four appendix projected from the sibling catalogue entries.

```
book/
  frontmatter/0.1-preface.md
  part1/  (Part 1 — The Context)
    1.1-the-ada-context.md
    1.2-the-timeline-and-the-work.md
  part2/  (Part 2 — The Mindset)
    2.1-the-printer.md
    2.2-loops-and-models.md
  part3/  (Part 3 — The Governed Engineering Environment)
    3.1-the-agent-stack.md
    3.2-models-and-the-semantic-gap.md
    3.3-the-governed-environment.md
    3.4-the-model-zoo.md
    3.5-lifecycles-and-runbooks.md
  part4/  (Part 4 — Putting It to Work)
    4.1-brownfield.md
    4.2-the-skills.md
    4.3-transformations.md
    4.4-training-data.md
    4.5-lessons-learned.md
  backmatter/5.1-conclusion.md
  data/metrics.json      # headline numbers, referenced from prose via {{token}}
  assets/                # figure assets (inline SVGs)
```

Front matter (Preface) renders before Part 1; the Conclusion renders after Part 4. The appendix
pages (`appendix-a/b/c-*.html`) are generated from the catalogue entries and render last.

## Authoring notes

- **Metadata.** Each chapter carries two comments: `<!-- part-title: … -->` and
  `<!-- chapter-title: … -->`. The leading `# …` H1 is dropped on render (the header comes from
  metadata), so keep or change it freely.
- **Metrics tokens.** Numbers that recur (weeks, LoC, costs) live in `data/metrics.json`. Reference
  them from prose with `{{token}}`; the build substitutes them and **fails loud** on an unknown token.
  Edit the number in the JSON, never in the prose. A later pass refreshes the repo-derived figures
  from history-mining; the cost-model and policy figures are the book's canonical estimates.
- **Epigraphs.** The first chapter of each numbered Part opens with an epigraph, defined in
  `_PART_EPIGRAPHS` in `build_book_html.py`. The Macbeth (Part 2) and Ecclesiastes (Part 4) quotations
  are verbatim from the source memoir; the Context and Governed-Environment openers are candidates a
  human editor may swap.
- **Figures.** Insert a figure with a directive comment: `<!-- figure: assets/<file> | <caption> -->`.
  An `.svg` is inlined (its own `<title>`/`<desc>`/`aria-*` survive); any other extension is wrapped in
  `<img>`. A missing asset fails the build.
- **Copyright.** Every page footer carries `© James C. Davis, 2026–present`.

## Build

Run `python3 build_book_html.py` (stdlib-only) or, from the catalogue root,
`python3 catalog.py build` (builds the book as part of the site and runs the orphan-reachability gate
over the book pages too). Never hand-edit the `.html`.

The book's appendix references catalogue-root figures. Run `catalog.py build` (regenerates
`catalogue-views.html`) before or alongside `build_book_html.py`, and commit both, so any deployed
cross-references resolve.
