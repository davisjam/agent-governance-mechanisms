<!-- doc-format: assessment -->
# Assessment — is the control-census / governance-target-coverage work a NEW catalogue mechanism?

**Author:** Opus analyst, 260802. **Posture:** READ-ONLY assessment. No Epic, book, or
catalogue file was edited.
**Ground truth read:** `docs/epics/active/control-census-governance-graph-260801/{main,phase-1a-260801,phase-1b-review-260801}.md`;
`docs/epics/active/governance-graph-260724/{main,phase-3-control-target-axis-260801,phase-4-modelsbridge-census-260801}.md`;
`system-models/governance_graph.py`, `system-models/control_family.py`;
`talks-and-notes/governance-catalog/{CLAUDE.md,INDEX.md}` + the two nearest entries
(`control-substrate-dependency.md`, `model-derived-test-obligation-census.md`).

---

## §0. Verdict — **NEW entry** (a distinct meta-governance sensor), with one honest caveat

The work is a **new mechanism** worth its own catalogue entry. It is the first mechanism in
the catalogue that turns the "a mature system covers all N complementary control targets"
completeness claim — today only a *principle* (the role structure), not a mechanism — into a
**queryable coverage sensor over the control portfolio itself**. It clears all three bars.

The honest caveat: it shares its *shape* — "derive a should-exist set from a model, lint the
gap to what exists" — with **model-derived-test-obligation-census**. It stays distinct because
it varies a named axis: the object censused is the **control portfolio** (not the test corpus),
the subject is the **governance system reflexively** (meta-governance), and the denominator is a
**closed complementary-targets taxonomy** (the "cover all N" claim), not a per-element obligation
set. That variation is at least as large as the lock-cardinality axis the mediators family
already accepts as distinctness. **New entry, in `models-bridge/system-models/`.**

---

## §1. The mechanism, stated portably

> **Model every governance control as a node in a typed graph, classified by a
> governance-TARGET axis — which of the system's N complementary control targets it governs —
> derived from the control's code anchor, never hand-authored. A per-target roll-up query then
> reports each target's control count and its soft/hard enforcement shape. A target with zero
> controls (or all-soft-no-hard) is a first-class, re-derived GAP finding: "this whole target
> is un-watched." Coverage of the governance estate stops being a vibe and becomes a map.**

- **The failure class it kills.** A governance portfolio grows organically — toward wherever
  the last painful failure was felt. Effort piles onto one target while another sits
  structurally un-watched, and **nobody notices the blind spot until it fails**, because no
  artifact ever asks "is the SET of controls balanced across the things that need governing?"
  A per-control lint checks each control is well-formed; it never poses the portfolio question.
  An un-audited portfolio silently under-covers a whole class.
- **The concrete instance.** Running the roll-up at HEAD returned **AGENT = 10 controls,
  MODELS_BRIDGE = 0, PRODUCT = 0** — two of three complementary targets entirely un-modeled,
  invisible until the census made it queryable. The empty cell *was itself* the finding, and it
  drove the next work (filling MODELS_BRIDGE from 0 → 12). PRODUCT is still honestly 0, named as
  such rather than silently absent.
- **What keeps it honest.** The target is DERIVED from the anchor path and **fails loud** on an
  unclassifiable control (never a silent default-bucket), so the coverage map can't quietly
  mis-credit a control to the wrong target. The projection is **instrument-only** (never blocks
  a commit) — it aims the next control, it does not hold a gate.

---

## §2. The recommendation it realized (cited)

The brief's hypothesis is **confirmed** by the ground truth, with one refinement on the exact
origin.

- **The principle.** The catalogue's three-control-targets framing (agent / models-bridge /
  product — the A.21 principle, which the catalogue reifies as its three **role** families)
  carries the standing implication that *"a mature system covers all three."* That claim was
  prose-only: there was no sensor that measured it.
- **The stated origin of the work.** The founding design
  (`phase-1a-260801.md` §0) was prompted by a build/skip pitch
  (`_drafts/governance-graph-proposal-for-ada-tool.md`) to design a read-only control census so
  *"do we have a control for that? / where does nothing watch?"* becomes a query. The design's
  load-bearing finding: the coverage half was ~75% already built (`governance_graph.py` types
  each control as a node; `repo-query governance coverage` already emits a read-only gap
  decomposition by control-FAMILY), and the **one genuinely-missing type** was the A.21
  three-TARGET axis — verified absent everywhere in `system-models/` (Phase-1b §1(c),
  CONFIRMED against the code).
- **How the work realized it.** Per the reviewer's G2 ruling (retire the stand-alone Epic; fold
  the delta onto the active conflict-model Epic to avoid a two-systems tax), the delta landed as
  `governance-graph-260724` **Phase 3**: a typed `ControlTarget {AGENT, MODELS_BRIDGE, PRODUCT}`
  enum + `derive_target(anchor)` + a `target_coverage()` read-through projection +
  `repo-query governance coverage --by-target`. USER greenlit it explicitly: *"let us identify
  gaps and do preemptive targeting"* (Phase 3 §1). The roll-up surfaced the AGENT=10 /
  MODELS_BRIDGE=0 / PRODUCT=0 gap. **Phase 4** then filled the empty MODELS_BRIDGE cell 0 → 12
  (the drift/parity/verification LINT family), cluster ② which the USER tagged *"straightforward
  win — Epic this one."*

So: the three-target *principle* implied "cover all three"; an axis built to test that principle
against the live control set **surfaced a gap (a whole target at ~0)**, which then got filled —
exactly the mechanism the brief hypothesized. The refinement: the immediate prompt was the
build/skip pitch, and the A.21 completeness claim is the *doctrine the pitch operationalized*,
not a separately-worded recommendation.

---

## §3. Novelty verdict — the explicit 3-bar check

### Bar 1 — kills a failure class (not a one-off bug)? **PASS**
The recurring failure: a governance portfolio under-covers a whole complementary target because
effort accretes where pain was felt, and no artifact measures the portfolio's balance. The
AGENT=10 / MODELS_BRIDGE=0 / PRODUCT=0 result is one instance; the class is "structural blind
spot in the control estate, invisible until it bites." Nameable, recurring, real.

### Bar 2 — distinct (survives "Why it's not just [X]")? **PASS**
- **Not just a per-control lint.** A lint validates each control in isolation. This asks a
  question no per-artifact check poses: is the SET balanced across the targets? An empty cell is
  a property of the *portfolio*, not of any one control.
- **Not just a one-off audit.** An audit answers "are we covered?" once, in prose, and rots the
  day a control lands or a cell empties. The census **re-derives from the live node-set every
  query**, so a newly-added target reopens the gap and a filled cell closes it — automatically.
- **Not just a list.** The census is a control inventory **partitioned by a typed
  complementary-targets taxonomy with a completeness claim attached** ("all N should be
  non-empty"), so a zero cell is a first-class finding. A flat inventory has no notion of "which
  target has none."
- **Not just the already-shipped `governance coverage` (family/granularity) metric.** That
  metric already decomposes GOVERNED / ORPHAN / OUT-OF-SURFACE by control-FAMILY over the lint +
  precommit corpus. It does **not** partition by the orthogonal governance-TARGET axis — the
  target trichotomy was verified absent. The census's distinct contribution over the existing
  coverage query is precisely that target partition (Phase-1b §4, the whole build/skip pivot).
- **Not just [control-substrate-dependency] (computed blast-radius).** That models controls as
  nodes too, and computes a query — but its question is *dependency*: which controls assume which
  substrate, so I know what a substrate change BREAKS. This census's question is *coverage
  completeness*: which target is under-watched, so I know where the next control should GO.
  Different edge, different failure (a migration misfiring controls vs. a target sitting
  un-governed).
- **Not just [model-derived-test-obligation-census].** *The nearest neighbour, same shape.* That
  census derives a should-be-TESTED set from the models (seams to fuzz, edges to inject) and
  lints the gap — governing the **product's test coverage**. This census derives a
  should-be-CONTROLLED set (every complementary target owes controls) and surfaces the gap —
  governing the **governance system's own coverage**. Named axis that varies: the **object
  censused** (control portfolio vs. test corpus) and the **reflexivity** (meta-governance: the
  control set audits itself, partitioned by the targets governance doctrine says it must cover).
  That is a larger variation than the lock-cardinality axis that already separates three mediator
  entries.
- **Not just the A.21 principle.** A.21 is *prose guidance* — "a mature system covers all three
  targets" — that the catalogue reifies only as its role STRUCTURE (the three family groupings),
  never as a mechanism entry. There is no entry that measures the claim. This census is the
  **sensor that operationalizes the principle**: it makes "covers all three" a re-derived,
  queryable fact. A principle aims; this measures. That gap — principle without an instrument —
  is the space the entry fills.

### Bar 3 — examples instantiate it? **PASS**
Every example is a real case of *this* mechanism, not a neighbour's: the AGENT=10 /
MODELS_BRIDGE=0 / PRODUCT=0 roll-up; the honest "un-censused targets: PRODUCT" line; the derived
target that fails loud on an unclassifiable anchor; the 0 → 12 fill of the empty MODELS_BRIDGE
cell; the census filing its **own** anchor-drift guard so the control set censuses its own
governor.

**Verdict: NEW ENTRY.** Not already covered; A.21 is a principle without a mechanism; the two
nearest entries answer different questions over different objects.

---

## §4. Sketched entry (genericised — no project filenames or rule numbers in the prose)

**Role dir:** `models-bridge/system-models/` — it reads the control node-set model and projects a
view; it sits beside the governance-graph, the control↔substrate-dependency model, and the
test-obligation census, all of which turn the control fleet into a modeled element.

**Proposed title:** *Control-coverage census (controls per governance target)*
(alt: *Governance-target coverage census*)

**Intent line:**

> **Intent** — Classify every governance control by which of the system's complementary control
> targets it governs — derived from the control's own anchor, not hand-declared — and roll the
> control set up per target. A target with zero controls, or with only soft aims and no hard
> hold, is a re-derived coverage GAP: the governance estate's own blind spots become a queryable
> map instead of something you notice when one bites (our instance: a `ControlTarget`
> {agent · models-bridge · product} axis over the typed control node-set, projected read-only by
> a `coverage --by-target` query).

**The 6-row metadata card:**

| | |
|---|---|
| Summary | Classify each control by the governance target it guards; roll up per target; an empty target is a gap finding. |
| Target | Bridge · **System models** (its subject is the governance system itself — meta-governance) |
| Form | `validation` |
| Move | `sensor` — it detects the under-covered target |
| Model | `governs-a-model` — it reads the control node-set to derive the target classification and projects the coverage view |
| Enforcement | **Soft·Hard** — the coverage roll-up is instrument-only (it aims the next control, never blocks a commit); a hard honesty backstop derives the target from the anchor and fails loud on an unclassifiable control, so the map cannot silently mis-credit |

**Motivation (the failure it kills).** A control portfolio grows toward the last painful failure.
Effort concentrates on one target — often the one that produces work (the agent fleet) — while
another target accretes nothing, and the imbalance is invisible because no artifact measures the
SET. Each control is well-formed; the *portfolio* is lopsided. The blind spot surfaces only when
the un-watched target fails in a way a control would have caught. The knowledge that a mature
system should cover all its complementary targets lives in doctrine, but nothing joins that claim
to the controls that exist — so the gap between "should cover all N" and "actually covers one" is
un-seen.

**The load-bearing "Why it's not just …":**

- **Not just a per-control lint** — a lint checks one control; it never asks whether the *set* is
  balanced across targets. An empty target is a portfolio property no per-artifact check sees.
- **Not just a one-off coverage audit** — an audit answers "are we covered?" once, in prose, and
  rots. This re-derives from the live control set each query: add a target and the gap reopens;
  fill a cell and it closes — no hand-maintained list.
- **Not just an inventory list** — a flat list of controls has no notion of "which target has
  none." This one is partitioned by a **closed complementary-targets taxonomy with a completeness
  claim** ("every target should be non-empty"), so a zero cell is a first-class finding.
- **Not just a test-obligation census** — that derives what should be TESTED and governs product
  test coverage. This derives what should be CONTROLLED and governs the **governance system's own
  coverage**: same derive-and-lint shape, different object (the control portfolio), and reflexive
  (the control set audits itself). The named axis is the subject of the census.
- **Not just a control↔substrate blast-radius model** — that computes what a substrate change
  breaks (dependency). This computes where governance is thin (coverage completeness). Different
  question, different failure.

**Known uses (one grounding instance, kept adaptable):** a derived `ControlTarget` axis over the
typed control node-set, projected by a read-only `coverage --by-target` roll-up that reported one
target fully populated and two at zero — the empty cells naming the estate's blind spots and
driving the next controls into the thinnest target; the classifier fails loud on any control
whose anchor it can't place, keeping the map honest as controls move.

**Related mechanisms (sketch):**
- **Sibling** — model-derived-test-obligation-census: both derive a should-exist set from a model
  and lint the gap; that one over the test corpus (product), this one over the control portfolio
  (governance, reflexive).
- **Bridge / Consumer** — the governance-graph (mechanism-interaction model): this census reads
  the same control node-set the conflict view models, projecting a coverage roll-up where the
  conflict view projects same-slot collisions.
- **See also** — control↔substrate dependency (a different query over the same control-as-node
  idea: blast radius, not coverage); the model query surface (the read-only path the roll-up
  rides); drift-parity gates (the honesty backstop family the fail-loud anchor check joins).

---

## §5. Caveats for the catalogue author (if the entry is written)

- **Genericise hard.** Keep the entry portable: "N complementary control targets," not the
  project's specific agent/models-bridge/product triad in the prose (name the instance once, in
  parentheses, per the instance-entry convention). The mechanism is the *sensor over a
  targets-taxonomy*, not the specific taxonomy.
- **Guard the merge-vs-split call.** If a reader judges the shape too close to test-obligation
  census, the deciding question is the catalogue's own rule: does a *named axis* vary? It does —
  object censused + reflexivity + a completeness-claim denominator. Document that axis in the
  "Why it's not just the test-obligation census" section so the boundary is explicit, exactly as
  the mediators family documents its cardinality axis.
- **Enforcement nuance.** The coverage roll-up is soft (instrument-only, never a gate — the
  established "never block on a coverage finding" ruling). The hard half is the anchor-derived,
  fail-loud classifier. Present it as Soft·Hard, not pure-soft, so the honesty backstop is
  visible.
- **PRODUCT still 0.** The instance is honestly partial (one target filled to 12, one still at
  0). That is a *feature* of the mechanism (honest partial coverage with a named gap), and the
  entry should present it that way — the empty cell is the finding, not an embarrassment.
