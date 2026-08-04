# Chapter section numbering — STEP 3 item (author 260804)

## Requirement (author)
Number chapter sections **part.chapter.section**, e.g. `1.1.1`, `1.1.2` — PRESENT WITHIN chapters for
reference/navigation. NOT in the table of contents at that granularity (TOC stays chapter-level).

## Intended design (my call — build-derived, not hand-numbered; drift-proof)
- **Auto-number in the build** (`build_book_html.py`), NOT by editing headings by hand. The build already
  knows each chapter's part+chapter number (from `_discover_chapters` / the filename `<part>.<ch>-slug`),
  so it derives the 3rd number by counting the chapter's `##` (section) headings in order → `1.1.1`,
  `1.1.2`, … Derived = it can't drift and needs zero prose edits.
- **Depth = section level (`##`) → the 3-part number** `part.chapter.section` (matches the author's "1.1.1").
  `###` subsections: default LEAVE unnumbered (the author asked for 3 levels); reconsider only if a chapter
  clearly needs 4-level refs — decide per evidence, log if so.
- **TOC-exempt:** the chapter-list / pager / `book-index` render at chapter granularity — do NOT inject the
  section number there. Only the in-chapter rendered `<h2>` gets its `1.1.x` prefix.
- **Anchor/cross-ref safety (the load-bearing constraint):** existing `{#anchor}` heading ids, `[ref:]`
  targets, `<!-- index-def: -->`/`<!-- label: -->` anchors, and the glossary→expansion-site pointer-wiring
  (FAST-2) must NOT break. The number is a DISPLAY prefix on the heading text; it must not change the slug
  anchor. Verify the reachability gate + all `[ref:]`/index-def links still resolve after.
- Front-matter (preface, glossary, acknowledgments) + back-matter: these are `apparatus`/unnumbered parts
  — likely SKIP numbering (they have no part.chapter number). Number only the body chapters (Parts 1-5).
  Appendix entries: separate scheme (they use A-1/B-2 locators already) — do not disturb.

## Execution (STEP 3)
A focused build wave (or a short ponder first, given the anchor-interaction risk — treat as a candidate
"real pickle" → an independent-Opus check if the anchor/ref interaction looks fragile on inspection).
Verify: build green, reachability green, every `[ref:]`/index-def/glossary-pointer resolves, TOC unchanged,
`<h2>`s show `1.1.x`, front/back-matter unnumbered. Log the depth + front-matter decisions in the
autonomous-decisions log.
