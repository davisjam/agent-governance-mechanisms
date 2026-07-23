# Callout typography — the `>`-blockquote taxonomy

The book authors four distinct constructs as markdown blockquotes (`>` lines). They
share one syntax but carry different jobs, so `build_book_html.py`'s blockquote
classifier routes each to a different rendering. This note is the source of truth for
that taxonomy: what each construct is, how it renders, and why.

## The four constructs

| Construct | Authored as | Renders as | Why |
|---|---|---|---|
| **THESIS** | `> **The <Name> Thesis.** <statement>` | **Box** — light lavender panel (`thesis-box`) | A thesis is the load-bearing claim of a chapter. It must stop the eye and read as a distinct, quotable unit — a prominent box. |
| **DEFINITION** | `> **<Term>.** <definition>` | **Footnote/aside** — lighter margin treatment (`aside-sidenote`) | A definition is a glossary aside — it pins a term the surrounding prose uses. The author called the churn definition a "footnote": it supports the reading, it does not interrupt it. Lighter, not boxed. |
| **CONCEPT-INSET** | `> ### Title` + prose (+ optional diagram) | **Box** — boxed primer (`concept-inset`) | A concept inset is a self-contained primer with a titled label. It already reads as a box (its label sets it apart); unchanged from prior behavior. |
| **PLAIN-SIDENOTE** | plain `> <prose>` (no bold lead, no heading) | **Sidenote** — Tufte-style margin float (`aside-sidenote`) | A short editorial remark that belongs beside the column, not in it. Unchanged from prior behavior. |

## Boxes vs footnotes/sidenotes — the deciding axis

The split is **prominence**, and prominence tracks **structural weight**:

- **Box** (THESIS, CONCEPT-INSET) — the callout carries a claim or a primer the reader
  is meant to *stop on*. It earns a filled panel, a border, and padding that lift it out
  of the reading column.
- **Footnote / sidenote** (DEFINITION, PLAIN-SIDENOTE) — the callout *supports* the
  reading without arresting it. It stays light: no fill on narrow screens, and on wide
  screens it floats into the right gutter as a Tufte sidenote.

A THESIS and a DEFINITION are both bold-lead blockquotes, so the classifier
distinguishes them by the **lead token**: a bold lead matching `The <…> Thesis.`
(ending in the literal word `Thesis.`) is a thesis; any other `> **Term.**` lead is a
definition. This keeps the author's syntax natural — no special fence, just the words.

## The THESIS box — lavender spec

- **Background** — light lavender `#f2effb` (a calm, distinct tint; not the warm
  parchment of the default blockquote, not the orange/blue of the gap markers).
- **Border** — a subtle `1px` solid lavender-grey `#d9d2ef`, plus a slightly heavier
  left rule in the accent-lavender `#7c6bb0` to echo the blockquote family without the
  italic aside styling.
- **Padding** — generous (`1rem 1.3rem`) so the claim breathes.
- **Text** — dark ink `#241f33` on the `#f2effb` panel. Contrast ≈ 13.8:1, well past
  the 4.5:1 WCAG AA floor the accessibility gate checks. The bold `The <Name> Thesis.`
  lead stays dark and un-italic (a thesis is a statement, not an aside), while the
  default blockquote's italic is dropped for this class.

## Does any other construct need a box?

No. The gap markers (`[FILL IN: …]` / `[MORE CHAPTERS FOLLOW: …]`) already render as
their own bordered panels through a separate path, and pipe tables and figures carry
their own framing. Among the `>`-blockquote family, only THESIS and CONCEPT-INSET earn
boxes; DEFINITION and PLAIN-SIDENOTE stay light. Adding a box to the definition would
undercut the author's intent — a definition is a footnote, and a footnote that shouts
is no longer a footnote.
