<!-- Internal working doc — NOT served (see NOSERVE in catalog.py). -->

# Writing backlog — distinctness / utility / drift

Working plan for the catalogue-improvement pass that came out of the 260703 critical read
(distinctness + general utility). Four items, ordered. Check items off as they land.

Governing style: the CLAUDE.md **Writing style** section. Every prose change obeys it.

---

## B1 — Templated summary counts (drift-proof) ✅ DONE (4a3f3ea)

**Problem.** `INDEX.md` footer (L152–157) had stale hand-maintained numbers — "Agent (20)" and
"Governance-doc controls (4)" while the tables hold 22 / 6. The row-count validator passes (rows are
right); only the prose summary rotted.

**Design — reuse the figure mechanism, extend it to markdown.**
The figures already fill `<span data-census="controls">53</span>` from the parsed entries
(`_sync_figure_census`, "single source of truth = the catalogue"). Markdown can't use inline spans —
`render_md` escapes `<`/`>`. So:

1. **`render_md` strips HTML-comment lines** (`^\s*<!--…-->\s*$`). Generic fix: also removes the
   pre-existing leak (agent/README.html renders an escaped `<!-- summary -->`). Lets comment delimiters
   be invisible in the rendered page.
2. **`_census_counts(entries)`** — the single source: `controls`, `families`, per-role
   (`agent`/`bridge`/`product`), per-family (from `parse_census()`, which is already ordered 1–11).
3. **`_sync_census_counts`** (rename of `_sync_figure_census`) — fills the figure spans (as now) AND
   regenerates the `INDEX.md` footer block between `<!-- BEGIN census-summary … -->` /
   `<!-- END census-summary -->` markers from `_census_counts`. Provenance per rule #35 (the emitter +
   "generated — do not edit" in the marker).
4. **`check_summary_counts`** (validate) — belt-and-suspenders: assert the coarse prose totals elsewhere
   (README "53 across three roles", INDEX header "All 53 entries") equal the computed total.

**Done when:** build regenerates the footer with 22/6; validate 0; the stale numbers can't recur
(change an entry → build → footer updates).

## B2 — Intent leads with the portable pattern ✅ DONE

Audit: most instance entries already led with the pattern (the 6 system-models, content-validator). Only
**4 were DocAble-first** — rewritten portable-first + "(our instance: …)": `pdf-model`, `office-models`,
`standards-rule-engine`, `a11y-prefix`. Rule lives in CLAUDE Writing style.

**Problem.** Instance entries lead their `**Intent**` with the DocAble specific, so a reader who doesn't
process PDFs/Office/WCAG misses the transferable idea.

**Style rule (add to CLAUDE Writing style):** *Instance entries lead with the portable pattern, then the
project instance.* "Intent — Route all mutation of a document format through one typed model with a
ban-lint on the raw library (our instance: `PdfModel` over the canonical PDF library)."

**Targets (~12):** the 6 system-models, pdf-model, office-models, standards-rule-engine, a11y-prefix,
content-validator, domain-registries. Some already lead with the pattern — audit each Intent, only tweak
the DocAble-first ones.

## B3 — Family-level "pattern → instances" signal ✅ DONE (presentation signed off)

Swept: **mediators** (resource-mediator ×3 cardinalities) + **system-models** (executable-source-of-truth
×6 domains) INDEX descriptors carry the pattern→instances line. Left the distinct-pattern families and
**canonical-seams** (descriptor already signals "one sanctioned seam per concern, held by a ban-lint").
Entries stay self-aware via their existing "Why it's not just…" sibling sections — no per-entry boilerplate.

**Problem.** ~15 of 53 are same-pattern instances (mediators ×3 cardinalities; canonical-seams ×2
patterns; system-models ×6 domains; gov-doc-lints ×3). Each defends its seam via "Why it's not just…",
so they're distinct — but a reader learns the pattern once; instances 2..N should read as *variations*.

**Presentation options (pick one, then canary the mediators family):**
- (a) **Family note in `INDEX.md`** descriptor — one authored line per family: "*One pattern — a
  resource-mediator — at three lock cardinalities (N=1 · M=8 · global mutex); the entries vary the
  cardinality, not the idea.*" Cheap, single place, but only in the census.
- (b) **A one-line italic "pattern" note under each instance entry's metadata card** — self-contained
  for a standalone reader; naming the shared pattern + the axis that varies + sibling links. Costs a line
  per entry; strongest for the "reads as a variation" goal.
- (c) Lean on the existing `*See also (sibling)*` Related-control relationship — already there, just
  make it consistent + name the varying axis.

**Lean:** (a) + (c) — author the pattern line once per family in INDEX, and standardise the sibling
Related-control to name the varying axis. Avoids a schema change; keeps entries standalone via the
sibling link they already carry. Canary on mediators, get sign-off, then sweep.

**✳ CANARY LANDED (mediators INDEX descriptor):** "*One pattern — a resource-mediator — at three lock
cardinalities (exclusive `N=1` · bounded `M=8` · a global mutex); the three entries vary the cardinality,
not the idea.*" Shows under the INDEX header + as the census tooltip. **Awaiting presentation sign-off**
before sweeping system-models (6 = executable-source-of-truth ×6 domains) and confirming canonical-seams
(family descriptor already signals "one sanctioned seam per concern, held by a ban-lint").

## B4 — Construction+enforcement pair consistency ✅ DONE (principle stated; audit clean)

Principle added to CLAUDE content model: *dedicated (one-to-one) enforcement bundles into the construction
entry; cross-cutting (one-to-many) enforcement earns its own entry.* Audit: all pairs already obey it —
seams bundle their dedicated ban-lints; `f10-wiring-lint` (all mutators) and `drift-parity-gates` (all
models) are cross-cutting → correctly separate. **No merges needed** (earlier "merge f10" take retracted).

--- original note ---

**Apparent problem.** Seams bundle construction+ban-lint into ONE entry; provenance splits
mutator-stamps + f10-wiring-lint into TWO; executable-source-of-truth + drift-parity-gates are TWO.

**Careful thought (recalibration — the split is mostly principled).** The deciding axis is *enforcement
scope*:
- **Dedicated (one-to-one)** enforcement → bundle into the construction entry. A seam's ban-lint guards
  that ONE seam (raw-PDF ban ↔ PdfModel). ✓ bundled, correct.
- **Cross-cutting (one-to-many)** enforcement → its own entry. `drift-parity-gates` governs ALL six
  models; `f10-wiring-lint` governs ALL mutator verbs across pdf/office. Both are one-to-many → separate
  is correct, and consistent with each other.

So there is **likely no real inconsistency** — the rule is just implicit. **Action:** (1) state the rule
explicitly (CLAUDE content-model or a short convention note), (2) quick audit that every pair obeys it
(no dedicated pair split; no cross-cutting enforcement bundled). Correct the earlier "merge f10" take —
f10 is cross-cutting, so it stays its own entry.

## B5 — Stats meta-file + HTML fill + no-raw-stats guard ✅ DONE

`stats.json` (declared facts: LOC 430, weeks 12) + `_stats(entries)` (merges declared + derived:
controls/families/roles/enforcement split) → `data-census` spans filled by build → `check_no_raw_stats`
forbids a stat literal (KLOC/controls/families/weeks) outside a span in the figure. Migrated the figure's
hardcoded `53/46/4/3` + `280 KLOC` (→430) into spans. Verified: validate 0, build idempotent (2nd build
empty diff), guard catches an injected `999 controls`. Prose numbers (N=8) exempt by vocabulary.

**Split recap:** markdown counts → lint-check (B1, rule #33); HTML stats → fill + guard (B5). One source
(entries + stats.json), two enforcement shapes matched to the medium.

## Bonus / follow-ups
- The INDEX footer census-summary was the drift; B1 fixes the class.
- `TODO.md` single-machine-contention rephrasing overlaps B3 (mediators) — fold in.
