# DESIGN — Part-6 v2 review, divvied and reconciled (READ-ONLY, 260807)

Apply-ready decomposition of the editor's **Part-6 v2 review** (`~/Downloads/part6-v2.md`: 13 numbered
comments + a philosophical observation + a `====` closing-line rewrite). This feeds a **serial main-lane
prose-apply pass**, not a rewrite.

**The reconciliation problem.** The v2 review was written against the PDF of the **pre-revision,
pre-migration** Part 6. Two changes it cannot see already reshape its targets:

- **(R) The Part-6 revision** (`part6-revision/WORK-ORDERS.md`, drafts assembled under
  `part6-revision/assembled/`). Already split Part 6 into **six-ish files** — `6.1` theory · `6.2`
  implications · `6.3` empirical regime (PROMOTED) · `6.4` limitations · `6.5` conclusion — and landed the
  commodity-intelligence restructure + the round-2 conclusion pass on `main`. The assembled drafts carry the
  near-final revised text; several v2 asks are **already satisfied** there.
- **(M) The on-the-shelf migration** (`on-the-shelf-migration-DESIGN-260806.md`). Inserts a NEW chapter
  **6.5 `where-mage-fits`** immediately before the Conclusion, which slides to **6.6**. It also **trims the
  Conclusion** (cuts the three-book re-derivation) and specs an **ending-fix** for the "finally become the
  discipline it always claimed to be" line.

**The final Part-6 structure this design targets (post-R, post-M):**

| # | Chapter | v2 items that land here |
|---|---|---|
| 6.1 | `toward-a-theory-of-mage` | #1, #2, #3, #4, #5, #11 |
| 6.2 | `implications-for-se` (*What Changes in Software Engineering*) | #12 |
| 6.3 | `a-new-empirical-regime` (null result) | #6, #7 |
| 6.4 | `limitations` | — |
| **6.5** | **`where-mage-fits` — NEW (migration)** | **#10 (Royce/Brooks/Parnas body)** |
| 6.6 | `conclusion` (was 6.5) | #8, #9, #10 (ending-fix), #13, `====` |

The v2 review's own section numbers are approximate (it read a rendered PDF); receipts below are pinned to
the **assembled revision drafts** (`part6-revision/assembled/*.md`), which are the text the apply pass edits.

---

## A. Divvy table (one row per v2 item)

Line cites are into `book/_design/drafts/part6-revision/assembled/<chapter>.md` unless noted.

### #1 — State/box the theory one page earlier ("Theory of MAGE (informal)")
- **RECEIPT:** 6.1, opening + `## The dynamic model`. Anchor: *"Velocity amplifies the fit between the
  fleet and the engineering environment it runs in."* (6.1:16–17).
- **VERDICT:** APPLY-MODIFIED (+ AUTHOR-DECISION on box style; optional [INFRA]).
- **CHANGE:** The theory sentence already appears early (6.1:16). Add the **boxed informal statement** the
  reviewer wants, right after the opening scope paragraph, verbatim from the review:
  > **Theory of MAGE (informal).** Agentic velocity does not create engineering progress. It amplifies
  > whatever governed engineering environment surrounds it.
  Render it as a **concept-inset** (existing infra: `> ### Theory of MAGE (informal)` + the two sentences →
  lavender boxed primer). No new environment required for this route. If the author prefers the **green
  thesis-box** weight (semantically apt — this is 6.1's load-bearing claim), that needs the optional
  thesis-box matcher relax (INFRA-2 below), since the classifier keys on a lead ending in the literal word
  `Thesis.`.
- **LANDS:** 6.1, before `## The dynamic model`. No migration conflict (6.1 unmoved). No WO conflict — WO-6.1
  tightened the dynamic-model prose but never boxed the informal statement.

### #2 — Elevate the adaptation loop to a shaded "The MAGE adaptation cycle" box
- **RECEIPT:** 6.1, `### The green path: governance adaptation`. Anchor: the five-move list
  *"**Represent** … **Convert** … **Strengthen** … **Reconcile** … **Retire**"* (6.1:147–152) and the
  causal sequence velocity→churn→conversion→improved environment→durable velocity.
- **VERDICT:** APPLY (existing infra).
- **CHANGE:** Lift the adaptation cycle into a **concept-inset** titled *The MAGE adaptation cycle*
  (`> ### The MAGE adaptation cycle` + the loop stated as a compact causal chain). Maps cleanly to the
  existing lavender concept-inset box — no new environment. Keep the surrounding prose; the box is the
  "readers most likely to remember" unit.
- **LANDS:** 6.1, `### The green path`. No migration conflict. Coordinate with WO-6.1's TM-2 rename (the five
  moves are already `Represent/Convert/Strengthen/Reconcile/Retire` in the assembled draft — box that form).

### #3 — Precede the H-table with "these are not rhetorical hypotheses / research agenda"
- **RECEIPT:** 6.1, `## Principal predictions`. Anchor: *"Here is where the model sticks its neck out."*
  (6.1:325) and `[ref:mage-hypotheses]` (6.1:336).
- **VERDICT:** APPLY-MODIFIED (largely ALREADY-COVERED).
- **CHANGE:** The revision already frames the table hard ("sticks its neck out"; "None of the seven receives
  an independent, population-level test … Every row is stated so a larger study can confirm or falsify it")
  and adds a `## Research agenda` section. Add **one declarative sentence** before the table to convert
  "future work" → "research agenda", in the reviewer's register:
  > These are not rhetorical hypotheses. They are the empirical program the theory implies — if the field
  > wishes to falsify MAGE, these are the experiments to run.
- **LANDS:** 6.1:325, immediately before `[ref:mage-hypotheses]`. No conflict.

### #4 — Promote H6 (oversight amortization); give it another paragraph
- **RECEIPT:** 6.1, `## Outcomes and observables` (6.1:300–302 "The theory predicts amortization…") and
  H6 row (6.1:345) + `### The compounding-governance proposition`.
- **VERDICT:** APPLY-MODIFIED (the promotion is largely DONE by the revision; add the framing).
- **CHANGE:** The revision already promotes H6 well beyond one row (the whole **Compounding-Governance
  Proposition** section is its expansion). What's missing is the reviewer's exact framing. Add one sentence
  naming H6 as the economic case, at the close of `### The compounding-governance proposition`:
  > This is the economic justification for governance: as classes convert, human attention per unit of
  > durable output falls, so the apparatus pays for itself in reclaimed judgment rather than merely catching
  > defects.
- **LANDS:** 6.1, end of the Compounding-Governance Proposition section (~6.1:425). No conflict.

### #5 — Reframe H7 as "engineering preconditions for learning," not org design
- **RECEIPT:** 6.1, H7 row (6.1:346) + the authority discussion (6.1:239–247). Anchor:
  *"the capability to diagnose structure and the authority to change the environment are colocated…"*
- **VERDICT:** APPLY-MODIFIED (light prose).
- **CHANGE:** Keep the H7 statement; add a framing clause where H7 is discussed (after 6.1:241) so it reads
  as a general engineering principle, not an org observation:
  > Stated generally, H7 names the engineering preconditions for learning: a discipline only improves where
  > the authority to diagnose structure and the authority to change the environment can reach each other.
- **LANDS:** 6.1, after the authority paragraph (~6.1:241). No conflict. (Note: WO-6.1's TM-6 already renamed
  the moderator to *diagnostic capability-fit*; use that term.)

### #6 — Lean into the null result ("a useful theory predicts null results")
- **RECEIPT:** 6.3, `## The beautiful garden: why per-task ablation cannot price a governed environment`.
  Anchor: *"**The null.** After correcting a broken first instrument…"* (6.3:121).
- **VERDICT:** APPLY.
- **CHANGE:** End the garden-null argument with the reviewer's line (adapted to house voice), turning the
  null from a detour into science:
  > A useful theory predicts null results as well as positive ones. This one was forced by the theory —
  > a garden-governed repository is exactly where a per-task recall strip must come back empty — so the
  > empty cell is evidence for the account, not against it.
- **LANDS:** 6.3, close of the garden-null section (before `## The methodology of deep single-case
  evidence`, ~6.3:250). No conflict (6.3 unmoved by migration).

### #7 — The null currently reads too defensively; soften the tone
- **RECEIPT:** 6.3, same section — the ceiling-effect / instrument-defect / pilot-scale / repeats
  enumeration (6.3:121–247). Anchor: *"an instrument defect, not evidence about the model"* (6.3:122).
- **VERDICT:** APPLY-MODIFIED (tone pass, not a cut).
- **CHANGE:** Keep every caveat (they are load-bearing), but re-cast the framing sentence from
  "please-don't-reject-this" to "this survived its first failed prediction." One reframing sentence at the
  section head or the null paragraph:
  > Read this not as a rescue but as a first stress test: the hypothesis met a prediction it could have
  > failed, and the reason it did not discriminate is a property of the instrument-meets-garden, not a crack
  > in the claim.
  Then trim any hedge that repeats a caveat already made (do not add words; the tone shift is net-neutral).
- **LANDS:** 6.3, garden-null section. No conflict. Pairs with #6 (same section — apply together).

### #8 — The conclusion is strongest when it returns to engineering
- **RECEIPT:** 6.6 (was 6.5) `The part that stays yours` → close. Anchor: *"As implementation becomes
  abundant, engineering moves to what stays scarce — judgment, models, and the governed environments…"*
  (6.5:122–124).
- **VERDICT:** ALREADY-COVERED-BY-REVISION (no-op; affirm).
- **CHANGE:** None. The round-2 conclusion pass already lands the *implementation-abundant → judgment-scarce
  → still software engineering* progression; the closing-alignment review RATIFIED it. Confirm the arc
  survives the migration trim (migration §3 keeps 99–124). No edit owed.

### #9 — Box the pull quote: "That is not the residue of a job the machines took. It is the job now."
- **RECEIPT:** 6.6 (was 6.5), close. Anchor verbatim: *"That is not the residue of a job the machines took.
  It is the job now."* (6.5:124).
- **VERDICT:** APPLY — **GATED on [INFRA-1] + AUTHOR-DECISION (`====`)**.
- **CHANGE:** Wrap the memorable sentence in a **pull-quote** box (large, offset, no label). This is the one
  construct the callout taxonomy does **not** have (thesis-box needs the word `Thesis.`; def-box needs an
  index-def; concept-inset needs a title; plain-sidenote renders as a light margin float, not a prominent
  pull quote). See **[INFRA-1]**. The exact sentence boxed depends on the `====` decision below (short line
  vs longer variant).
- **LANDS:** 6.6 close. Migration keeps line 124 in its KEEP set, so the target survives — but sequence the
  box **after** the migration renumbers/trims the Conclusion, to avoid editing a file mid-migration.

### #10 — "Classical SE was right" — sharpen; connect to Royce, Brooks, Parnas
- **RECEIPT:** 6.6, operationalization paragraphs. Anchor: *"Software engineering has not become a
  different discipline. It has finally become the discipline it always claimed to be."* (6.5:144–145).
- **VERDICT:** SUPERSEDED-BY-MIGRATION (body) + APPLY-MODIFIED (ending-fix).
- **CHANGE:** The reviewer's "connect back to Royce, Brooks, Parnas / the goals never changed, only the
  dominant scarcity changed" is **exactly** the migration's new **6.5 `where-mage-fits` §5 "Older
  aspirations, new economics"** (which names Royce/Brooks/Parnas) plus the landed operationalization thesis.
  Do **not** re-derive it in the Conclusion. In 6.6 apply only the migration's specced **ending-fix**
  (`on-the-shelf-migration-DESIGN §4`): reframe 144–145 so the emphasis is *changed economics enabling a
  standing aspiration*, not a "return to original job":
  > The discipline's aim never changed. What changed is that we can finally afford to pursue it — the models
  > kept honest for cents, the judgment freed for the essential work the older engineers always named and
  > rarely could reach.
- **LANDS:** substance → 6.5 §5 (migration owns it); ending-fix → 6.6:144–145. **Must land after the
  migration.** Reviewer's #10 line "The discipline's goals never changed. Only the dominant scarcity
  changed." may be used verbatim as the 6.5 §5 spine sentence.

### #11 — One-page synthesis causal-chain diagram ("the figure people reproduce in talks")
- **RECEIPT:** Part-6-wide. Anchor (review): *"I wanted the entire causal chain on one page."* Node list
  proposed: Cheap implementation → Reasoning bottleneck → Modeling Thesis / Alignment Thesis → Governed
  environment → Governance conversion → Engineering capital → Compounding → Trustworthy software.
- **VERDICT:** AUTHOR-DECISION (BUILD or not) — new SVG asset.
- **CHANGE:** This is **not** the existing `mage-dynamic-model` (that is a system-dynamics *loop* diagram of
  6.1's four dynamics; the reviewer explicitly wants "not another process figure — a synthesis"). It is a
  **linear top-to-bottom causal spine spanning the whole book's argument**. See §B-3 for the node sketch and
  placement options. If built, it needs a hand-authored SVG (coordinate-authored per the rejected
  node-anchor pilot; follow the self-communicate SVG guidance — Mermaid-first is inadequate for a
  talk-reproducible spine, so the narrow hand-authored-SVG escape hatch applies).
- **LANDS:** if built, either 6.1 close (as the chapter's synthesizing frame) or 6.6 (whole-book capstone).
  Recommend **6.1 close** — it synthesizes the theory the chapter builds, and keeps the Conclusion prose-only.

### #12 — Reorganize 6.2's implications explicitly by audience
- **RECEIPT:** 6.2, whole chapter. Anchor headings: `## What migrates into the environment` /
  `## Representation engineering` / `## Governance discovery and mechanization` / `## The engineer's role and
  organizational conditions` / `## Consequences for software engineering`.
- **VERDICT:** AUTHOR-DECISION (recommend APPLY-MODIFIED, not wholesale reorg).
- **CHANGE:** WO-6.2 **deliberately** landed a *thematic* structure organized around the "what migrates into
  the environment" center — that was the review-1 Priority-2 fix ("don't let the four centers compete"). A
  wholesale reorg into *researchers / practitioners / educators / organizations* would re-fragment the just
  -unified chapter. Recommend keeping the thematic spine and adding **light audience signposting**: the
  existing `### What this changes for measurement, quality investment, and education` already clusters
  practitioner/educator implications; add one-line audience lead-ins where implications cluster, rather than
  four new top-level sections. See §B-4. Surface as a structural call for the author.
- **LANDS:** 6.2 (unmoved). Conflict with WO-6.2 is the reason this is a decision, not an apply.

### #13 — The final paragraph lands beautifully
- **RECEIPT:** 6.6 close (the maturation blockquote 6.5:126–127 + the operationalization paragraphs).
- **VERDICT:** ALREADY-COVERED-BY-REVISION (affirmation; no-op).
- **CHANGE:** None. Confirms the current ending works. No edit owed — but note it interacts with #9/`====`:
  if the closing line is rewritten, preserve the *implementation-abundant → judgment-scarce → engineering
  matured* landing the reviewer praises.

### Philosophical observation — "a theory paper embedded in a book; promote, don't add"
- **RECEIPT:** review tail: *"my goal would … not be to add more ideas … make the existing ones impossible
  to miss."*
- **VERDICT:** ALREADY-EMBRACED (editorial stance, not an edit).
- **CHANGE:** None as a discrete edit. It is the **operating standard for this whole apply pass** — every row
  above is *promotion* (typography, framing, one boxed statement), not new argument. Record it as the
  acceptance test: an apply that adds a new idea has overstepped.

### `====` — the closing-line rewrite (author already prefers the LONGER variant)
- **RECEIPT:** 6.6 close, line *"It is the job now."* (6.5:124). Author intent (verbatim): *"the point is
  that it's what the job was always supposed to be, and never was because the code kept having to be
  maintained."*
- **VERDICT:** AUTHOR-DECISION (strong author intent — the longer variant; ratify exact wording).
- **CHANGE:** See §B-1. The reconciliation is non-trivial: the author's longer variant restates the
  operationalization-thesis paragraphs that **already follow** at 6.6:129–142. Two ways to compose without
  doubling; recommendation and exact wording in §B-1.
- **LANDS:** 6.6 close. Land after the migration. Couples with #9 (what gets boxed) and #10 (the ending-fix).

---

## B. AUTHOR-DECISION list (surface, do not decide)

### B-1. `====` / #9 — the exact closing wording, reconciled (TOP decision)
The author prefers the longer variant. But the v2 longer variant and the **landed operationalization thesis**
(6.6:129–142: *"Classical definitions … remain substantially correct … engineering re-centers on judgment,
modeling, validation, architecture, and governance — the systematic activities the discipline always claimed
as its own"*) are **the same argument**. Dropping the long variant at line 124 makes the book say it twice.

Two clean shapes — pick one:

- **Option 1 (RECOMMENDED) — keep the crisp line, box it; let the operationalization paragraphs carry the
  long argument.** Line 124 stays *"That is not the residue of a job the machines took. It is the job now."*
  as the **boxed pull quote** (#9). The author's longer intent is **already realized** by the paragraphs at
  129–142 that immediately follow. Result: a memorable, talk-reproducible pull quote + the full historical
  argument, no redundancy. The pull quote is short enough to box (Option 2's long form is not).
- **Option 2 — inline the longer variant at 124, trim the operationalization paragraph.** Replace 124 with:
  > That is not the residue of a job the machines took. It is the work software engineering has always been
  > reaching toward. Implementation scarcity kept pulling the discipline downward into code production. As
  > implementation becomes abundant, the profession recenters on the judgment, modeling, architecture, and
  > governance that were always its highest-leverage work.
  Then cut the near-duplicate sentence at 133–135 so the point isn't made twice. Cost: the closing line is no
  longer boxable as a pull quote (too long), so #9 becomes moot.

**Recommendation: Option 1** — it satisfies both the reviewer (a boxed pull quote) and the author (the longer
argument is present, in the operationalization paragraphs) without doubling, and it keeps the *"finally become
the discipline it always claimed to be"* destination the round-2 pass and the migration ending-fix both aim
at. Confirm.

### B-2. #1 — box style for the informal theory statement
- **Concept-inset** (lavender, titled) — works with existing infra, no INFRA task. Slightly off-genre (concept
  -insets are primers), but acceptable.
- **Thesis-box** (green, prominent) — semantically ideal (this IS 6.1's load-bearing claim), but needs
  **[INFRA-2]** (relax the thesis-box matcher to accept a `Theory of MAGE (informal).` lead, or a small
  allowlist). Recommend concept-inset unless the author wants the green thesis weight.

### B-3. #11 — build the one-page synthesis diagram? (+ node list + placement)
Build-or-not is the author's call. If **build**, proposed spine (vertical, single column, hand-authored SVG):

```
Cheap implementation
      ↓
Reasoning bottleneck  (long-horizon reasoning; finite horizon)
      ↓
Modeling Thesis  ·  Alignment Thesis   (two parallel nodes feeding one)
      ↓
Governed engineering environment
      ↓
Governance conversion   (failure class → durable mechanism)
      ↓
Engineering capital  →  Compounding
      ↓
Trustworthy software
```

- **Placement:** recommend **6.1 close** (synthesizes the theory; keeps the Conclusion prose-only). Alt: 6.6.
- **Asset:** new `assets/mage-synthesis-spine.svg`, **coordinate-authored** (explicit x/y per node, not
  auto-anchored — the node-anchor pilot was rejected). Follow self-communicate's hand-authored-SVG escape
  hatch; grayscale-survivable; caption ties each node to its home chapter.
- **Risk:** must not restate the `mage-dynamic-model` loop figure — this is the *linear whole-book* spine, a
  different object. If the author judges the two too close, SKIP (the reviewer flags it as a want, not a gap).

### B-4. #12 — audience reorg of 6.2: adopt / modify / skip
- **Adopt (four audience sections):** conflicts with the just-landed thematic WO-6.2; re-fragments the
  Priority-2 unification. Not recommended.
- **Modify (RECOMMENDED):** keep the thematic spine; add one-line audience lead-ins where implications
  cluster (researchers at the empirical/measurement bullets, practitioners at "the judgment moved… toward
  you," educators at the teaching bullet, organizations at "managing the workforce is not governing the
  environment"). Low-risk, honours both reviews.
- **Skip:** the chapter is coherent as landed; do nothing.

### B-5. #10 ending-fix wording (rides the migration)
The migration already specs the ending-fix (avoid "return to original job"; credit the traditions; attribute
the shift to economics). Confirm the writer uses the migration §4 wording (or B-1/§4-consistent voice), and
that the Royce/Brooks/Parnas connection lives in **6.5 §5**, not re-derived in 6.6.

---

## C. INFRA prerequisites (flag; do not build here)

### [INFRA-1] Add a **pull-quote** callout to the render path — prerequisite for #9 (BLOCKING for that item)
The `>`-blockquote taxonomy (`book/_design/callout-typography.md`) has four constructs — THESIS box,
DEFINITION aside, CONCEPT-INSET box, PLAIN-SIDENOTE — and **no pull-quote**. Grep confirms zero `pull-quote`
occurrences in `build_book_html.py` and `book_typst.py`. A prominent, label-less, large-type memorable line
has no home:
- **Web** (`build_book_html.py`): a new class, e.g. `blockquote.pull-quote` (large display type, centered or
  offset, no fill/label), routed by a new authored shape — recommend a fenced marker (e.g.
  `<!-- pullquote -->` glued to a `>` line) so it is not confused with THESIS/DEFINITION (both are bold-lead
  blockquotes) or PLAIN-SIDENOTE (which floats to the gutter, the opposite of a centered pull quote).
- **Print** (`book_typst.py`): a sibling display block (large text, vertical breathing room, `breakable:
  false`), drawing colours from the shared `dt` tokens like the other boxes.
- Update `callout-typography.md` (the taxonomy source of truth) to five constructs, and mind the BLOCKING
  caption-length / define-before-use lints at assembly.
- **Tag:** `[INFRA]` `followup-domain: controls` (a render-path construct).

### [INFRA-2] (OPTIONAL) Relax the thesis-box matcher — only if #1 wants the green box
Only needed if the author picks the thesis-box (not concept-inset) for #1 (B-2). Extend the classifier's lead
match from the literal `The <…> Thesis.` to also accept `Theory of MAGE (informal).` (or a tiny allowlist).
Small; skip entirely if #1 uses concept-inset.

---

## D. Sequencing (for the serial main-lane apply pass)

**Lane 1 — pure prose, no infra / no author gate / no migration dependency (fold into the main-lane apply
tail now, against the current 6.1 / 6.3):**
- #2 (adaptation-cycle concept-inset), #1 (informal-theory concept-inset — if the concept-inset route is
  taken), #3, #4, #5 → **6.1**.
- #6, #7 → **6.3** (apply together; same garden-null section).
- #8, #13, philosophical → **no-op** (affirm the arc survives).

**Lane 2 — INFRA-gated:**
- **[INFRA-1] pull-quote environment** must land before #9's box. **[INFRA-2]** only if B-2 picks the green
  thesis-box for #1.

**Lane 3 — author-decision-gated (park until ratified):**
- `====` / #9 exact wording (B-1), #11 build-or-not + placement (B-3), #12 reorg shape (B-4), #1 box style
  (B-2).

**Lane 4 — MUST land AFTER the migration reshapes Part 6 (6.5 `where-mage-fits` + 6.6 `conclusion`):**
- #10 substance → **6.5 §5** (migration owns it); #10 ending-fix → **6.6:144–145**.
- #9 pull-quote box + the ratified closing wording → **6.6** (editing the Conclusion mid-migration would
  churn; do it once the file is renumbered/trimmed).
- #11 synthesis diagram if placed in 6.6 (recommend 6.1 instead, which needs no migration wait).

**Single-writer discipline (submodule):** one writer at a time on `main`; the pre-commit hook force-stages
regenerated `.html` + `book-models/*`; never `git add -A`; run the full suite between writers. INFRA-1 (render
path) is a serialized infrastructure step, not a parallel-draft edit.

---

## E. Counts (for the orchestrator report)

- **APPLY / APPLY-MODIFIED (actionable prose):** 8 — #1, #2, #3, #4, #5, #6, #7, #10(ending-fix).
- **ALREADY-COVERED / no-op:** 3 — #8, #13, philosophical.
- **SUPERSEDED-BY-MIGRATION:** 1 — #10 (body → 6.5 §5).
- **AUTHOR-DECISION:** 4 — #9 (+`====`) closing line/box wording, #11 synthesis diagram, #12 audience reorg,
  #1 box style.
- **INFRA:** 1 blocking ([INFRA-1] pull-quote environment) + 1 optional ([INFRA-2] thesis-box matcher relax).

### Top 3 reconciliation conflicts resolved
1. **`====` closing line vs the operationalization thesis (doubling).** The author's longer closing variant
   restates the operationalization paragraphs that already follow. Resolved: **Option 1** — keep the crisp
   "It is the job now." as the boxed pull quote; the longer argument is already carried by 6.6:129–142. No
   redundancy; the reviewer gets a pull quote, the author gets the long argument.
2. **#10 (connect to Royce/Brooks/Parnas) vs the migration.** The migration's NEW **6.5 `where-mage-fits`
   §5 "Older aspirations, new economics"** IS that connection, and migration §4 already specs the Conclusion
   ending-fix. Resolved: route #10's substance to 6.5 §5; in 6.6 apply **only** the ending-fix — do not
   re-derive the traditions in the Conclusion.
3. **#12 (audience reorg of 6.2) vs the landed thematic WO-6.2.** The just-unified thematic chapter would be
   re-fragmented by four audience sections. Resolved: recommend **MODIFY** (keep the thematic spine, add light
   audience signposting), surfaced as an author structural call rather than an apply.
