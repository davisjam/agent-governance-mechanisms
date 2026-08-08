# Vision-review on figure change — geometry cannot see text-on-text

**A figure change gets a vision pass: render it, then look.** The deterministic figure lints guard the
classes geometry can measure. One legibility class they structurally cannot reach is text crowding text —
and that class is common enough to earn a standing review step.

## Why geometry goes blind

The figure lints over `book/assets/*.svg` each read coordinates:

- **overflow** — a label runs past its own box.
- **font-band** — a label renders too small or too big for the legibility band.
- **label-collision** — a connector stroke runs through the readable core of a free-floating label.

All three test a stroke or a box against a text's bounds. None can see **one glyph crowding another**. An
inline arrow glyph "→" jammed against the next word, two labels whose boxes overlap, a caption kerned into
its neighbour — these are text against text, with no stroke element to test. The model-ladder figure hit
exactly this: its top spectrum band packed an arrow glyph so tight against "follow it" the two smeared, and
the arrow glyph is a *character*, not a `<path>` or `<line>`, so the stroke-vs-text checker never saw it.

A vision model does. Render the figure and look, and the crowding is obvious in a glance.

## The process

On any change to a figure under `book/assets/*.svg`:

1. **Render it.** `rsvg-convert book/assets/<fig>.svg -o /tmp/<fig>.png` (or the book's `pdftoppm` route).
2. **Look, with three questions.** Does any stroke cross a label's readable core? Is any label cramped,
   overlapped, or text-on-text? Does anything sit off-canvas?
3. **Fix and re-verify by looking again** — geometry cannot confirm a text-on-text fix, only the eye can.

Figures change rarely, so this runs **on figure-file change, not every build**. The cost is one render plus
one look per changed figure.

## Division of labor — VLM is the catch-all, the lint is the cheap complement

- **The vision pass is the general solution.** It caught the model-ladder text-on-text cramp that geometry
  is blind to, and it adjudicates every borderline the deterministic checks raise. When in doubt, the render
  is ground truth.
- **The geometric `label-collision` lint is a deterministic complement, not a replacement.** It guards the
  exact stroke-through-a-free-label class — cheap, dependency-free, and it forward-polices reintroduction:
  land it once and every future figure edit is checked without a human in the loop. It lands audit-only, so
  it informs rather than blocks. It will never see text-on-text or low-contrast crowding — that stays the
  vision pass's job.

The two compose: the lint holds the line it can measure on every commit; the vision pass covers everything
the lint cannot, on the rare occasions a figure changes.

## Provenance

A figure-QA pilot (260807) validated both halves. It rendered all 87 hand-authored figures and looked,
confirming a vision pass reliably catches intra-figure defects — including the model-ladder text-on-text
cramp and the research-arc feedback edge drawn through its "the theory changed" label. It also built and
refined the geometric detector now shipping as `book-models/lint_figure_label_collision.py`, taking it from
~4% precision to clean-on-the-current-tree while it still flags the research-arc defect if reintroduced. The
pilot's verdict: build both, staged — the vision pass as the catch-all, the lint as the fast deterministic
pre-filter.
