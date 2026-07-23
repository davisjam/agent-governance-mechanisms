# Figure text-fit runbook — a label spills its box or the canvas

The build runs an AUDIT-ONLY check (`tests/svg_fit.py`, driven by `catalog_tests.py`) over every
`book/assets/*.svg`. It estimates each `<text>`'s rendered width and flags two failures:

- **Box overflow** — a label sits inside a `<rect>` box but its estimated width runs past the box's
  inner edge. The text spills its box, often over a neighboring shape.
- **Canvas overflow** — a label's estimated horizontal extent runs past the figure's `viewBox` width.
  The text spills off the whole figure.

The estimate is a heuristic — `len(text) × font-size × ~0.55` (`~0.6` bold), an average glyph ratio — so
it produces false positives, which is why it is audit-only and does not block the build. When it flags a
figure, open the SVG, look at the named text, and confirm the spill by eye. If it is real, fix it in the
order below. If it is a false alarm (a wide-but-fitting label, an intentional full-bleed note), leave the
figure and note the miss when the check is tuned.

This runbook is the fix procedure the check points every finding at.

## Confirm before you fix

The heuristic over-estimates for narrow-glyph strings (lots of `i`/`l`/`.`/spaces) and for condensed
fonts. Before editing, verify the spill is real: render the SVG (open it in a browser, or `catalog.py
deploy local` and view the book page) and look at the flagged label. A label that clears its box by eye
is a false positive — skip it.

When the spill is real, work the fixes in order. Each earlier fix preserves more of the author's intent
than the next; drop to the later ones only when the earlier one can't serve.

## The fixes, in order

### (a) Enlarge the box — first choice

**Widen or heighten the `<rect>` so the label fits, and shift its neighbors to make room.** The label is
right; the box is too small. Grow the box's `width` (and `x` if it should stay centered), then nudge any
adjacent rects, arrows, and labels so nothing collides. This keeps the label at full size and full
wording — the reader loses nothing.

Reach for this when the figure has slack around the box, or can be rebalanced to create it. Most box
overflows are a box drawn a little too tight, and widening it is the honest fix.

### (b) Add space into the diagram — when the whole figure is cramped

**Grow the `viewBox` and re-space the elements so nothing is packed edge to edge.** When several labels
overflow at once, or a canvas overflow shows text running off the figure, the figure is trying to hold
more than its current dimensions allow. Widen the `viewBox` (and the `width`/`height` if set), then spread
the shapes into the new room. A wider `viewBox` renders every label smaller at book width, so pair this
with a font bump if the labels were already near the floor (see the legibility floor below).

Reach for this when the crowding is the figure's, not one box's — the picture needs more canvas, not a
single wider rect.

### (c) Shorten or wrap the label — when the words can give

**Cut the wording to the shortest phrasing that carries the idea, or split one long `<text>` into two
stacked lines.** A caption that reads `translates the gesture into one typed edit operation` might become
`translates a gesture into` / `one typed edit operation` on two lines, or just `translates to a typed
op`. Wrapping trades vertical space for horizontal; shortening trades words for fit. Both keep the font
size.

Reach for this when the box and canvas are fixed for a reason (a panel that must stay a set size, a grid
that must align) and the text is the thing that can yield. Prefer a genuine shortening over cramming —
a label the reader can't parse is worse than one that wrapped.

### (d) Reduce the font size for that figure — last resort

**Shrink the font size, for the one figure, only after (a)–(c) can't fit the text — and never below the
legibility floor.** Smaller type is the last lever because it costs the reader: a label sized for the
author's monitor is a non-label for a reader presenting to a room or reading at book width. Drop the size
only when the box can't grow, the canvas can't grow, and the words can't shorten.

The floor is the drawing-skill minimum (see the annotation-tier table in the drawing style doc,
`plugin/agent-governance/skills/self-communicate/drawing/diagrams.md` — its "Annotation — three tiers"
section). Sized to a ~500-unit viewBox, a primary label wants ~15–17 user units and a heading ~20–24;
scale up for a wider viewBox (multiply by ~1.9 for a 960-wide one). A primary label is never smaller than
the body text it sits beside. If reducing the font would push a label under that floor, the fix is wrong —
go back to (a) or (b) and make room instead.

## Why this order

The order runs from *most* faithful to the author's intent to *least*. Enlarging a box or the canvas
keeps the words and the size — the reader sees exactly what the author meant, with more room. Shortening
gives up some words but keeps legibility. Shrinking the font keeps the words but costs the reader's
eyes, so it comes last and is fenced by the floor. Try the cheap, lossless moves first; spend legibility
only when nothing else fits.

## The check's known limits

- **It is a width heuristic, not a renderer.** It estimates from character count and font size, so it
  over-flags narrow-glyph strings and under-flags wide-glyph ones. Confirm by eye.
- **Vertical overflow is out of scope.** It checks horizontal fit only. A label taller than its box (a
  multi-line `<text>` with many `<tspan>` lines) is not caught.
- **Label-over-arrow overlap is a known gap.** Precise overlap between a label and a line or arrow needs
  real geometry the heuristic doesn't compute. Box and canvas overflow are the priority; watch for
  label-on-arrow collisions by eye when you render the figure.
- **`dx`/`dy`-positioned and `<tspan>`-driven text is skipped.** The check anchors on a `<text>`'s `x`/`y`;
  text positioned by relative offsets isn't measured.

These limits are why the check is audit-only. Once its false-positive rate is low enough on the real
corpus — after the ratio and padding are tuned against confirmed spills — a follow-up can promote it to a
blocking gate.
