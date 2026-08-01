# charts.md — the house style for data charts

This is an **agent-facing** style doc (the drawing leg of the `self-communicate` skill, beside
[`diagrams.md`](diagrams.md) and [`tables.md`](tables.md)), not a catalogue entry. It is not rendered to
HTML or served. `diagrams.md` draws the *shape* of a system — a structure, a flow, a lifecycle. A **data
chart** draws a *measurement* — a count, a rate, a distribution over time. When the content is a number the
reader should see rather than read, chart it; when it is a structure, draw the diagram.

Read it alongside [`../writing/voice.md`](../writing/voice.md) (§"Economy — less is more"), whose prose
economy this doc is the visual twin of, and [`diagrams.md`](diagrams.md), whose data-ink and font rules it
inherits. The discipline below is Edward Tufte's, ported to the figures the book and the papers ship.

---

## What a house chart is

A house chart is a bar or line figure drawn to one restrained style so a reader who has seen one has seen
them all. It carries a measurement and nothing else. The defaults below make a chart right by default, the
way the shared style source in [`diagrams.md`](diagrams.md) (§"One style source for a figure-set") makes a
diagram right — so a figure that reaches for none of them still clears the bar.

- **Reach for a chart when:** the content is a quantity the reader should *see* — a trend over weeks, a
  count across categories, a before/after saving. The picture carries the shape of the number faster than a
  sentence does.
- **Not when:** the content is four numbers a reader looks up one at a time. That is a table (see
  [`tables.md`](tables.md)) — a chart of four values is chartjunk dressed as data.

---

## The defaults

### Type — serif, sized for the page

Set every chart in a **serif** face, matching the book's body type; a chart is a figure inline in serif
prose, not a slide. Size for the tiers in [`diagrams.md`](diagrams.md) (§"Annotation — three tiers"): the
tick labels are **in-figure labels** and are never smaller than the body text around them. **The prevailing
chart fonts are too small — recalibrate up**, for a fifty-year-old's eyes on an ordinary screen. If you have
to lean in to read a tick, the font lost.

### Ticks — three round ones, human-formatted

- **Exactly ~3 y-axis ticks.** Three round ticks self-explain the scale; a ladder of eight is chartjunk. Pick
  a **"nice" step** — a `1`, `2`, `2.5`, or `5` times a power of ten (`… 100, 200, 250, 500, 1000 …`) — so
  the ticks land on round numbers, not `0, 337, 674`.
- **Human-format the tick text.** `12K`, not `12000`; `1.5M`, not `1500000`. A reader parses `50K` at a
  glance and `50000` by counting zeros.
- **Large tick labels.** Per the font rule above — a tick a reader must zoom to read is no tick.

### No title, no axis labels

**A chart carries no title and no axis labels.** The figure's **caption** names it (the book's `figure:`
directive and `tables.md`'s caption-above both do this), and the ticks self-explain the units. A "Commits per
week" title above a chart whose caption already says "commits per week" is the number stated twice; a
"weeks →" label under an axis of week ticks is a label for a thing the ticks already name. Strip both — the
caption identifies the figure, the ticks carry the scale.

### Palette — two colors, restrained

Two series is the working case, and two colors carry it: a **calm blue `#4C72B0`** and a **muted red
`#C44E52`**. They are chosen to read on both light and print backgrounds and to survive a grayscale print as
two distinct tones. Do not reach past two — a third series is usually a second chart. **Never a legend for one
series:** when a chart has one color, a caption naming it beats a legend box (a legend for one thing is
chartjunk, per [`diagrams.md`](diagrams.md) §"Less is more").

### Bars, grid, and a callout

- **Thin black bar edges.** A hairline black stroke on each bar separates adjacent bars without a gap and
  reads crisply in print. No fill gradient, no drop shadow, no 3-D — a bar is a flat rectangle.
- **A faint dotted y-grid.** Light dotted horizontal rules at the three ticks help the eye carry a bar's
  height to its value. Faint and dotted so the grid recedes behind the data; never a heavy solid grid, and
  never vertical gridlines (the bars already mark the x positions).
- **An optional rounded annotation box** for a single stat callout — a `<rect rx>` (the native rounded box,
  per [`diagrams.md`](diagrams.md) §"Use the native construct") holding one number the figure exists to make.
  One callout at most; a chart peppered with boxes is a chart that does not trust its data to speak.

---

## Data-ink — strip the chartjunk

Tufte's data-ink ratio names the discipline: every mark on the figure should carry part of the measurement;
strip the marks that only decorate. This is the visual twin of the prose rule "cut the fluffy adjective"
([`../writing/voice.md`](../writing/voice.md) §"Economy") — there, cut the word that adds heat but no
information; here, cut the mark that adds ink but no data.

- **No gradients, no 3-D, no drop shadows.** Ornament that dresses a bar up without saying anything about the
  number it stands for.
- **No legend when one series.** Name the single series in the caption; a one-entry legend is a box that
  carries no distinction.
- **No redundant gridlines, no boxed plot area, no background fill.** The three dotted grid rules are the
  whole grid; a full box around the plot is chartjunk.

The `svg-audit.py` shipped beside these docs checks a chart's SVG for the label-fit and stroke-through-glyph
defects the same way it checks a diagram; the data-ink cuts above are by eye.

---

## Emit both formats — one figure per idea

Draw the chart once and emit it for both pipelines:

- **SVG** for the web and book figure pipeline. The book's `figure:` directive inlines an `.svg` so its own
  `<title>`/`<desc>`/`aria-*` survive and no external request can 404 — an SVG chart drops straight into a
  chapter the way a hand-authored diagram does.
- **PDF** for a paper. A vector PDF is what a LaTeX `\includegraphics` wants; emitting it beside the SVG lets
  the same measurement serve the book and the paper without a redraw.

And **one figure per idea.** A chart that carries two unrelated measurements is two charts sharing an axis by
accident. Split it; each idea gets its own figure and its own caption.

---

## Charts are drawn from committed data — never mocked

**A chart is a projection of a measurement the repo holds, not a picture an author eyeballed.** Every figure
is regenerated from its source — a committed CSV, the book's `data/metrics.json`, a pilot's result table — so
a reader can trace the picture back to the number, and the figure cannot drift from the data the way a
hand-tuned mock does.

- **Cite the source.** A chart's generating script names the file it reads; a reader who doubts the picture
  can open the data. A chart with no traceable source is decoration wearing a data costume.
- **Regenerate, don't retouch.** When the measurement changes, re-run the generator; never hand-edit the SVG
  to nudge a bar. A retouched figure is a second copy of the fact that drifts the moment the data moves — the
  same drift the diagrams doc kills by generating a diagram from its model
  ([`diagrams.md`](diagrams.md) §"Generate the diagram from the model").
- **A mocked chart is a lie the reader cannot check.** The book's own velocity figure is the discipline in
  practice: it is drawn from the project's commit history, one bar per week, so the curve is the record, not
  an impression of it.

This is the chart leg of the fidelity rule the whole method turns on: do not manufacture a datum the
measurement never produced. A mocked bar is a manufactured datum.

---

## The short version

Chart a measurement when the reader should see its shape, not when four numbers want a table. Set it in
serif, sized up for older eyes; give it three round human-formatted ticks and no title, no axis labels — the
caption names it, the ticks self-explain. Two colors at most (calm blue, muted red), thin black bar edges, a
faint dotted grid, one optional rounded callout. Strip every mark that carries no data. Emit SVG for the book
and PDF for the paper, one figure per idea. And draw it from committed data, regenerated from its source, so
the reader can always trace the picture back to the number — never mocked.
