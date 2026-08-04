# 2.5-metrics MMM-drain correction — apply-ready spec (260804, grounded in real ada-tool figures)

The book's `part2/2.5-metrics.md` shows the Missing-Model-Metric drain ending at **14.9%** ("latest
committed point"). STALE. Real current (ada-tool `governance-metric-residue-tidy-260803`, closed today,
verified in its final-DoD): **raw orphan 7.89% (12/152) · glue-excluded 0.00% (0/140)** — the residual 12
are glue-code (web-route/seam DETAILS residue, no obvious missing model), so genuine-orphan = 0; the
**<5% target is met by GENUINE coverage** (DoD verified: real model-node additions, not exclusion-gaming).
Sibling MCM: 6.48% raw / 0% glue-excluded (only fold in if 2.5 references it — it does not today).

Do NOT naively swap 14.9→7.89. Represent faithfully — the drain CONTINUED past the earlier ≤10% target,
and the honest new nuance is raw-vs-glue-excluded.

## The 4 coordinated edits (all in `part2/2.5-metrics.md` + its curve SVG)

1. **Table (L253-262)** — ADD a 9th row after `cluster-4`:
   `| residue-tidy | web-route/seam links + control-nodes | 7.89% | 92.1% |`
   (raw 12/152. The genuine-orphan-0 point is carried in prose, not a table row, to avoid conflating raw
   vs glue-excluded in the same column.)

2. **Prose (L267-270)** — replace "took the orphan rate from 56% at the pilot to 14.9% at the latest
   committed point — code-to-model coverage rising from 44% to about 85%" with:
   "…from 56% at the pilot to **7.89% at the latest committed point** — code-to-model coverage rising from
   44% to about **92%**. And once the residual dozen orphans are set aside as glue code — web-route and
   seam wiring with no model to miss — the **genuine-orphan rate is 0%**: every test whose code could trace
   to a model now does. The loop crossed its ≤10% target and, on genuine coverage, its tighter <5% goal."
   (Keep the "metric drove the modeling" closing sentence.)

3. **Figure caption (L249)** — "falls from 56% to **7.89%** across **nine** tracer re-runs … from 44%
   toward **92%**. The dashed line marks the loop's ≤10% target — **now crossed** (and 0% once glue-code
   residue is excluded)."

4. **The curve SVG `book/assets/mmm-drain-curve.svg`** — extend the plotted series with the 9th point
   (7.89% / 92.1%), continue the orphan line down past the ≤10% dashed target line, and extend the
   code-modelled mirror line up to ~92%. Keep Umber tokens + the existing axis/ticks; re-verify `svg_fit`
   clean after. IF the SVG re-plot is fiddly, the fallback is to leave the 8-run historical curve and let
   the table+prose+caption carry the 9th point — but PREFER extending the curve so figure and table agree.

## Honesty-note check (L272-279)
The existing denominator-drift note (144→148) still holds; the new point is 12/152, so update "144 to 148"
→ "144 to 152". The "one interior point (cost-rollup) not separately enumerated" caveat stays. The
glue-excluded framing is honest (state the residual is glue, not a hidden hole).

## Provenance
All figures from `docs/epics/active/governance-metric-residue-tidy-260803/final-dod-260803.md` (raw 0.0789
(12/152); glue-excluded 0.0000 (0/140); "<5% by GENUINE coverage"). This is a book-side reflection of a
real, committed ada-tool result — the metric the book describes drove itself past its target (a live
demonstration of the book's own measure→model→improve thesis). Do NOT invent intermediate points.
