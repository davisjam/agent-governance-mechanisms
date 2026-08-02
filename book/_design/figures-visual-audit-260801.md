# Figures visual audit — book proper (260801)

A visual quality pass over every book-proper figure in `book/figures.html`: front matter
(`fig-0-*`), Parts 1–5, back matter (`fig-6-*`). **Scope excludes the cover art (`cover-*.svg`)
and all Appendix figures (`fig-7-*`, the mermaid-rendered pattern pages) — do not touch either.**
Every figure was rendered to PNG at 2× (`rsvg-convert`) and judged by eye, then cross-checked
against its SVG source (coordinates, markers, fonts, tokens). This is a remediation *plan* —
minor polish, not a redesign. Fix guidance follows `book/_design/figure-text-fit-runbook.md`
(enlarge box → add canvas → shorten/wrap → shrink font, in that order) and the drawing stance in
`plugin/mage/skills/self-communicate/drawing/diagrams.md`.

**Census:** 38 book-proper figures. 37 are hand-authored SVGs in `book/assets/` (spliced inline
by `build_book_html.py:_figure_block`); 1 is a photo (`fig-6-3-1`, `assets/author-headshot.jpg`).
No book-proper figure is mermaid-rendered — the mermaid cache serves appendix pages only, so the
`mermaid_label_px` token and the mermaid label-overflow sensor do not apply here.

**Verdict in one line:** the corpus is in good shape — 13 of 38 figures are fully clean and most
of the rest carry only polish items. The real findings concentrate in (a) five label-collision
defects, (b) the three slide-import figures whose style and spacing drifted from the house look,
and (c) a handful of mechanical consistency gaps (a11y metadata, background tone, quote glyphs, a
legibility floor) that are exactly the deterministically checkable classes.

**Severity counts:** 22 finding rows — distracting 4 · notable 7 · polish 11 (two polish rows are
multi-figure sweeps: the 3-figure background-tone row and the 9-figure quote row). 25 figures
carry at least one row; 13 are clean.

---

## 1. Per-figure findings

Clean — no findings (13): fig-0-1-3 `book-map` · fig-1-2-1 `loop-engineering` · fig-2-2-1
`documentation-hierarchy` · fig-2-3-1 `constraint-vs-sensor` · fig-3-2-1 `dataflow-inset` ·
fig-3-2-2 `service-model-structure` · fig-3-3-1 `sync-model-structure` · fig-3-4-1
`component-model-structure` · fig-3-5-2 `dag-policy-structure` · fig-4-2-1 `three-skills` ·
fig-4-2-2 `skill-recipe` · fig-4-6-1 `example-vs-generative` · fig-6-3-1 (photo; alt + caption
fine). A further five — fig-2-2-2, fig-2-6-1, fig-3-1-1, fig-3-1-2, fig-4-4-1 — appear only in
the mechanical quote-sweep row at the bottom of the table.

Findings (severity: **D** distracting · **N** notable · **P** polish):

| Figure | Source (`book/assets/`) | Class | Issue | Suggested fix | Sev |
|---|---|---|---|---|---|
| fig-5-3-1 | `llm-as-function-call.svg` | spacing/overlap | Edge labels "typed input contract" / "typed output contract" (anchor=middle at x=262 / x=542, 18u italic) are wider than the 80u inter-box gaps — both run under the flanking box borders; rendered text is visibly clipped to "typed inpu…" / "typed outpu…". | Runbook order (a): widen the gaps (shift Model box right, validator right, grow viewBox 1040→~1150) so the two-line labels clear; or place each label *above* its arrow with clearance. Keep wording. | D |
| fig-4-3-1 | `transformations-pipeline.svg` | spacing/overlap | The input spine (`<path>` at x=70) runs vertically *through* all three lane labels — "self-communicate", "self-operate", "self-governance" are `text-anchor=middle` at x=70, so the stroke strikes the glyphs. | Move the spine left (x≈36) and left-align labels in the freed band, or right-align labels ending at x≈62. Break-the-line-at-text is the fallback. | D |
| fig-4-1-1 | `squash-zero-promote.svg` | spacing/overlap | Transition label "at zero" (anchor=middle x=666, ends ≈x=697) runs under the Blocking box (x=690); the sibling "land" (ends ≈x=408) clears its box by only ~2u. | Shift both labels to sit fully in their gaps (e.g. "at zero" → x≈650) or raise them above the arrows; the 280u box pitch has room. | D |
| fig-0-1-2 | `oversight-modes.svg` | spacing/overlap | Panel (a): the four ring arcs terminate *on* the role words — arrowheads strike "Planner", "Tester", "Reviewer", "Security" glyphs. Panel (c): the italic "policies" label (x=480) tucks under the governed-environment box's left border. | Shorten each arc's angular extent so heads stop ~8u short of the words; nudge "policies" left of the box edge. | D |
| fig-2-4-1 | `config-optimization-runbook.svg` | spacing/overlap | The outer lifecycle arc passes through the label "A lifecycle the runbook is anchored to"; on the right the same arc crowds the Determinize/Decision-trace boxes. One short connector (trace box → "(a)" box) has no arrowhead while the figure's other 8 edges do. | Nudge the label below the arc (or break the arc under it); add the missing `marker-end`. | N |
| fig-2-1-1 | `agent-stack-layers.svg` | spacing/consistency | Slide-import style (see Batch C). Specific collisions: the "via harness" chip overlaps both the Harness and GenAI boxes with a stitched-glyph caret (▲) instead of a marker arrow; "claude-hooks"/"claude-skills" boxes touch with no gap; the rotated right-panel label reads bottom-up as "governance / Methodology +" — line order inverts the intended "Methodology + governance". | Separate the chip from both boxes and give its arrow a real `<marker>`; add ~10u gap between hook boxes; swap the two rotated text lines. | N |
| fig-3-6-1 | `join-composite.svg` | spacing/overlap | "local + staging" and "staging only" boxes share an edge (no gap). The dashed node-join edge passes through the Journey panel's text band (the drawing-hygiene sensor flags this at x36–184, y418–436). | Insert a ~12u gap between the two boxes; reroute the dashed edge around the "endpoint" label. | N |
| fig-5-3-4 | `dsl-remediation-function.svg` | spacing/arrowheads | The purple "Shared edit language" box overlaps the orange task-to-edit function box's top-right corner (borders collide, reads as sloppy rather than layered); the function → Document model edge has no arrowhead while sibling edges do. | Lift the purple box ~20u; add `marker-end` to the edge. | N |
| fig-1-1-1 | `one-shot-vs-supervised-autonomy.svg` | consistency/arrowheads | Slide-import style (Batch C). The four fan lines from "Supervised autonomy" to the leaf boxes carry no arrowheads while the figure's other edges do (`csp-ah` used on only 3 of 7+ edges). | Either add `marker-end="url(#csp-ah)"` to the fan lines or accept fan-out-as-tree; pick one convention within the figure. | N |
| fig-5-2-1 | `velocity-commits-per-week.svg` | consistency/a11y | Generated (matplotlib) chart: the only book-proper SVG with **no `<title>`, no `<desc>`, no `role`**; serif chart typography and inset "Commit size (LOC)" stat box sit inside the plot area crowding the tall May bars; no y-axis unit on the SVG itself (caption carries it). | Post-process (or re-emit) with `<title>`/`<desc>`/`role="img"`; optionally nudge the inset box fully clear of the bars. Font/style: leave — the serif matches the book body. | N |
| fig-0-1-1 | `mage-overview.svg` | legibility/a11y | Smallest text is 10.5u on a 1080-wide viewBox (≈7px at column width — the "MAGE is the governed path…" note and box sublabels at 13–13.5u ≈ 8.5px). Root `<svg>` lacks the `role` attribute its siblings carry. | Bump the note + sublabels ~2u each (room exists); add `role="group"` with the existing title/desc ids in `aria-labelledby`. | N |
| fig-1-3-1 | `sdlc-to-selc.svg` | legibility | Densest text in the corpus: 11–12.5u on a 940-wide viewBox (≈8–9px at column width). Fits and reads at 2×, but at book width the row sublabels ("authored as models", "gates, not reading") are at the floor. | Optional: grow viewBox height + font ~1.5u across; the layout has slack. Do not shorten wording. | P |
| fig-5-4-1 | `mage-staircase.svg` | legibility/arrowheads | Body text 14–15.5u on 1180 viewBox (≈9px). The stage→shortcoming horizontal connectors are thin light-gray lines with small heads — nearly invisible next to the red "forces" arrows. | Darken connectors to the muted token and/or +0.5 stroke; optional +1u font pass. | P |
| fig-6-0-1 | `soft-hard-spectrum.svg` | wording/legibility | The last tick label wraps as "quality / drift / deploy gate / · marker file the tool reads" — a leading interpunct opens the second line. Body labels 13.5u on 1000 viewBox (≈9.5px). | Rewrap so the "·" stays with the preceding item (break after "gate ·"); optional font bump. | P |
| fig-2-5-1 | `metric-spectrum.svg` | legibility | Card sublabels 15–15.5u on a 1200-wide viewBox (≈9px at column width). The text-fit sensor flags 3 of the 4 card titles as box-overflow; by eye they fit but are snug (≤8u side padding). | If touched at all: widen the three flagged cards ~15u each (runbook (a)); otherwise record as sensor false-positives when tuning. | P |
| fig-5-2-2 | `phased-timeline.svg` | wording | May 5 entry: the italic punchline convention breaks — the roman text ends mid-sentence ("… My graduate") and the italics begin mid-sentence ("is at the next table…"). Every other entry switches at a sentence boundary. | Rebreak the three lines so the roman/italic split lands on the sentence boundary ("Its owner is at a retreat, not watching the chat." / *"My graduate is at the next table. She walks over and taps him in."*). | P |
| fig-3-5-1 | `deployment-model-structure.svg` | wording (caption/figure fit) | The caption promises three things — build host, runtime cluster, *and a parity lint holding declaration to reality* — but the figure draws only the first two; no parity element appears. Also generous empty space in the Runtime-cluster panel. | Either add a small parity-gate diamond (matching fig-3-2-2's) fed by both panels, or trim the caption's parity clause to "…deploys it; the parity lint (§text) holds the declaration honest." Author's call — flag, don't force. | P |
| fig-5-3-2 | `services-reactive-view.svg` | spacing | Edge labels "enqueue" / "hands off" / "publishes" end flush against the boxes they point into (0–2u clearance). Reads fine; snug. | Optional 4–6u nudge left each. | P |
| fig-5-3-3 | `frontend-mvc-editor-dsl.svg` | spacing | The "One model, one way to change it." annotation abuts the dashed re-render line (the dashes graze the text's left edge). | Nudge the annotation right ~8u or the dashed line left. | P |
| fig-4-6-2 | `generative-loop.svg` | spacing | The bottom-left caption "model-claim coverage — the metrics chapter owns it" floats far from the dashed curve it annotates; association is weak. Arrow crossings in the center are inherent to the content — leave them. | Move the caption to sit along the dashed curve's midpoint. | P |
| 3 figures | `llm-as-function-call.svg`, `frontend-mvc-editor-dsl.svg`, `dsl-remediation-function.svg` | consistency (tokens) | Each paints a full-canvas `<rect fill="#ffffff">` background — pure white slabs on the `#fdfcf9` paper page (all other figures use paper/panel tones or no background). | Change the three background rects to the paper token or delete them (transparent inherits the page). | P |
| 9 figures | `sdlc-to-selc`, `semantic-gap-levels`, `collision-edge`, `trunk-and-views`, `projection-axes`, `novelty-axis`, `phased-timeline`, `llm-as-function-call`, `frontend-mvc-editor-dsl` | wording (typography) | Straight apostrophes/quotes in labels (`it's`, `node's`, `"function"`) while e.g. fig-1-1-1 uses proper curly quotes ("One-shot scripting") and the book body sets typographic quotes throughout. | Mechanical sweep: `'` → `’` and `"…"` → `“…”` in `<text>` content only (never in ids/attrs). | P |

Non-findings verified and dropped: the faint vertical divider in fig-1-1-1 is the rule token
`#e4e0d8` (intentional, correct); the "hairline" under fig-0-1-1 is the gallery's `<hr>`, not the
SVG; fig-6-0-1's varying tick colors track the soft→hard gradient (intentional); all 37 SVGs pass
the design-token palette allow-list (`lint_design_token_drift.py` — its only SVG-COLOR findings
are cover art, out of scope).

---

## 2. Opus work-batches

Every batch touches **only `book/assets/*.svg`** (plus, where stated, one chapter `.md` caption).
Common DON'T-touch boundary for all batches: never edit `book/figures.html` or any generated
`.html` (build artifacts); never touch `cover-*.svg`; never touch `book/.mermaid-svg-cache/`,
`mermaid-config.json`, or the `mermaid_label_px` token; no build-pipeline edits except where
Batch F says so. After each batch: re-render the touched figures at 2× and re-check by eye;
`python3 catalog.py validate && python3 catalog.py build` must stay green.

**Batch A — label-collision fixes (mechanical; the 4 distracting + 3 notable overlap rows).**
Files: `llm-as-function-call.svg`, `transformations-pipeline.svg`, `squash-zero-promote.svg`,
`oversight-modes.svg`, `config-optimization-runbook.svg`, `join-composite.svg`,
`dsl-remediation-function.svg`. Each fix is a coordinate shift / gap insertion / added
`marker-end` per the table; wording unchanged; runbook order (a)/(b) only. One dispatch.

**Batch B — mechanical consistency sweep (mechanical).**
(1) a11y metadata: add `<title>`/`<desc>`/`role="img"` to `velocity-commits-per-week.svg`
(post-process the matplotlib output; if an emitter script exists, fix the emitter too) and
`role="group"` to `mage-overview.svg`. (2) The three `#ffffff` background rects → paper token.
(3) The curly-quote sweep across the 9 listed figures (`<text>` content only). One dispatch;
zero layout changes, so visually diff-safe.

**Batch C — slide-import harmonization (judgment).**
Files: `one-shot-vs-supervised-autonomy.svg`, `agent-stack-layers.svg`,
`config-optimization-runbook.svg` (its style half; its collision half lands in Batch A). These
three came in with a slide-deck look — heavy Helvetica bold, saturated navy slabs — that reads as
a different hand from the 34 house-style figures. **This batch is deliberately scoped to
harmonization, not redesign:** fix the listed collisions (agent-stack chip/boxes/rotated-label
order; one-shot arrowhead convention), set `font-family` to the body token stack, and rebalance
the worst empty regions (agent-stack bottom-left; one-shot top-clearance of the "Simple task"
edge label). Whether to go further — re-drawing them fully in house style — is an author decision
this plan surfaces but does not make. DON'T: change their information content or layout topology.

**Batch D — legibility floor pass (judgment-lite, optional).**
Files: `mage-overview.svg` (do — it is the worst, 10.5u/1080), `sdlc-to-selc.svg`,
`mage-staircase.svg` (+ its gray connector darkening — do), `soft-hard-spectrum.svg`,
`metric-spectrum.svg`. Normalized floor: a label should render ≥ ~12px at a 700px column, i.e.
`font-size ≥ viewBox-width / 58`. Each bump needs a per-figure re-space check, so this is one
careful dispatch, not a sed. The two "do" items are worth it; the other three are defensible
as-is — apply only if the fix stays lossless (runbook (a)/(b)).

**Batch E — caption/wording touch-ups (judgment; SVG text + one chapter caption).**
(1) The May-5 rebreak lives in `phased-timeline.svg` — the timeline prose is SVG `<text>`, not
chapter markdown; rebreak the three lines there. (2)
fig-3-5-1 caption-vs-figure parity: decide add-glyph vs trim-clause (the figure directive's
caption sits in `book/part3/3.5-the-physical-view.md`). (3) `soft-hard-spectrum.svg` tick-label
rewrap. House voice per `plugin/mage/skills/self-communicate/writing/voice.md`: plain, active,
no new qualifiers; keep the caption's claim-then-scope cadence.

**Batch F — mechanical checks (see §3; lands in `tests/svg_fit.py` + `catalog_tests.py`).**
Independent of A–E; can run in parallel with them but must re-baseline after A–C land (the
fix batches change exactly the geometry the new checks measure).

Suggested order: A → B (parallel-safe with A: disjoint edits, but same files in 3 cases — run B
after A to avoid conflicts) → C → E; D and F whenever slots allow. A, B are mechanical; C, D, E
judgment.

---

## 3. Mechanical-check (lint) candidates

Existing sensors, for orientation — all audit-only today:
- `tests/svg_fit.py::check_svg_text_fit` — box/canvas **horizontal** text overflow over
  `book/assets/*.svg` (glyph-ratio heuristic). Current book-proper findings: `book-map` ×1,
  `metric-spectrum` ×3, `services-reactive-view` ×1 — all verified snug-but-fitting by eye
  (false positives to feed back into its ratio/padding tuning).
- `tests/svg_fit.py::check_svg_drawing_hygiene` — stitched-primitive arrowheads and
  **`<line>`-through-glyph**. Real book-proper hit: `join-composite` (the Batch A/6 dashed edge).
- `book-models/lint_design_token_drift.py` — SVG fill/stroke hex ∈ `svg_palette()` (book-proper
  figures currently pass), off-scale CSS sizes, anchor hues.
- Mermaid label-overflow sensor + the `mermaid_label_px` token — appendix figures only; no
  book-proper coverage needed.

New candidates, ranked by (determinism × observed hit-rate). "Gate" = can block `catalog.py
build`; per house discipline every new check lands audit-only first and promotes after a clean
pass.

1. **SVG a11y metadata** — every `book/assets/*.svg` referenced by a `figure:` directive carries
   `<title>` + `<desc>` and a `role` on the root, with `aria-labelledby` naming the two ids.
   *How:* ElementTree walk; join against the chapter directives (parse `<!-- figure: … -->`).
   *Today's hits:* `velocity-commits-per-week` (all three missing), `mage-overview` (role).
   Zero-heuristic → **build-time gate** after the Batch B fix.
2. **Marker integrity** — (a) every `marker-start/-end` URL resolves to a `<marker>` defined in
   the same file; (b) every defined marker is referenced (unused = drift); (c) the marker's child
   fill matches the referencing path's stroke (or an allow-map). *How:* regex/ET enumeration —
   the same join the audit ran. (a)+(b) deterministic → **gate**; (c) audit-only.
3. **Label-overlaps-foreign-box** — a `<text>`'s estimated extent intersects a `<rect>` that does
   *not* contain its anchor. Extension of `check_svg_text_fit` (which only tests the containing
   box and the canvas). *Today's hits:* `llm-as-function-call` ×2, `squash-zero-promote` ×1,
   `oversight-modes` ×1 — i.e. every Batch A label-clip. Same glyph-ratio heuristic → audit-only.
4. **Stroke-through-glyph for `<path>`** — extend `check_svg_drawing_hygiene`'s line-through-text
   test to straight `<path>` segments (`M…L…` polylines). *Today's hit:* `transformations-pipeline`
   (its spine is a `<path>`, so the current `<line>`-only check misses the worst collision in the
   corpus). Audit-only.
5. **Box-touch/overlap** — two sibling `<rect>`s intersect with neither containing the other
   (gap < ~4u counts as touch). *Today's hits:* `join-composite`, `agent-stack-layers`,
   `dsl-remediation-function`. Pure geometry, but panels-with-children need a containment
   exemption → audit-only.
6. **Background-tone conformance** — a rect covering ≥95% of the viewBox must use the paper or
   panel token (tightens palette *membership* to per-role placement; `#ffffff` is the case it
   kills). Deterministic → **gate** after Batch B.
7. **Typographic-quote check** — no `\w'\w` and no straight `"` inside `<text>`/`<tspan>` content.
   *Today's hits:* the 9-figure straight-apostrophe list. Deterministic on text nodes →
   **gate** after the Batch B sweep (allow-list escape for a deliberate code literal).
8. **Normalized font floor** — `min(font-size) ≥ viewBox-width / 58` (≈12px at a 700px column),
   flagging per figure with the offending text. *Today's hits:* `mage-overview`, `sdlc-to-selc`,
   `mage-staircase`, `soft-hard-spectrum`, `join-composite`, `metric-spectrum`. The floor
   constant needs calibration against figures the author accepts as-is → audit-only, with the
   drawing-skill annotation tiers as the reference scale.
9. **Vertical canvas overflow / edge margin** — y-extent of text and shapes vs the viewBox with a
   small margin (`check_svg_text_fit` is horizontal-only; `squash-zero-promote`'s terminal bar and
   `oversight-modes`' bottom caption run within ~10u of the edge). Audit-only.

Not proposed: arrow-direction semantics, crossing-count, whitespace-balance — judgment classes
where a checker would mostly emit noise; the visual pass stays the control for those.

---

*Audit basis: 37/37 SVGs rendered and read at 2× into `/tmp/figaudit/`; sensors re-run at HEAD
(`svg_fit` both checks, `lint_design_token_drift`). No figure, book file, or build file was
modified; this document is the audit's only artifact.*
