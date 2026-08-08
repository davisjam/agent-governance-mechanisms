<!-- doc-format: epic-v2 -->
<!-- epic-format-version: 2 -->
# Epic: master-skill-starter-upstream-260807 — Upstream ada-tool's mature EPIC/design-template richness (§Models "what models touched/missing", §9 type-system posture, rule-#57 verification-tier as the static/dynamic-analysis framing) + the stabilized MAGE book vocabulary + the govern/operate/communicate trio shells into the bundled `claude-starter` family; resolve the 3-copy starter source-of-truth drift.

**Home (canonical).** This Epic lives in the **governance-catalog submodule** at
`docs/epics/master-skill-starter-upstream-260807/main.md`. It was **re-homed here (260807)** from the
parent ada-tool repo's `docs/epics/`, where it had been mistakenly registered (confusing ada-tool's Epic
tracking). The skills it upstreams live in THIS repo (`plugin/mage/skills/`) and the entire write surface
is this submodule, so this is its real home. The parent ada-tool repo no longer tracks it. This submodule
has no knowledge of the parent — treat the Epic as standalone; the ada-tool paths it cites (below) are the
*upstream-FROM* source it ports content out of, not self-references into a shipped tree.

**Status:** 🔵 queued — Phase 1 founding design LANDED (re-homed into the submodule); Phase 1b (independent
2nd-Opus review + **plug-convention design**) PENDING, to run **here in the submodule**; Phases 2+ gated on
Phase-1b RATIFY + book v2 publish.
**Dispatch posture:** P1b (independent 2nd-Opus review, per the parent method's double-Opus rule) is
dispatch-ready and runs in this submodule; ALL impl phases (P2–P6) gated on "book v2 published +
governance-catalog single-writer lock free" AND on the §G Fork rulings (now RATIFIED — see below).
**Owner:** orchestrator
**Created:** 260808 · **Re-homed into submodule:** 260807
**Closed:** —

> **RATIFIED §G fork rulings (author, 260807).** The four §G forks below are RESOLVED. The full 5-field
> framing of each stays in §G verbatim (the options + this doc's original recommendation); these are the
> authoritative rulings the impl phases execute against:
>
> - **F1 — source of truth / mirror → INSTALL + LOCAL-ADAPTER.** The starter ships as an *installable*
>   SSOT; an adopter's local deltas live in a companion **file `*.local.md` + directory `local/`** (NOT an
>   in-file section, NOT a hand-synced third copy). Phase 1b designs the **plug convention** — how the
>   installed SSOT and the `*.local.md` / `local/` local-adapter overlay compose.
> - **F2 — static/dynamic-analysis framing → ALSO-ENHANCE.** Merge the consolidated "Static & Dynamic
>   Analyses" best-practice **into the skill/source**, not port-only.
> - **F3 — trio scope → BOTH shells now.** P4 ships `operate-starter.md` AND `communicate-starter.md`.
> - **F4 — vocabulary depth → SHIP THE GLOSSARY FILE.** P3 ships the Tier-1 + Tier-3 `method-language`
>   glossary file (not aliases-only).
>
> Phase 1b remains REQUIRED before any impl dispatch: it re-derives independently, ratifies the load-bearing
> premises in §1.3C, folds any REVISEs, and produces the plug-convention design that F1 now calls for.

> Source proposal: `scratchpad/claude-starter-upstream-proposal-260807.md` (ranked A/B/C/D).
> This founding design operationalizes that proposal into phases, invariants, an enforcement→test
> map, and the §G forks (now ratified above). **Design-only** — no starter file was written.

---

## §1 Rationale

**What is missing today.** The bundled `claude-starter` — the portable starter templates shipped inside
the **self-governance** skill's `reference/downloads/` — is mature on *method* (Part A is already
re-clustered into a governance view) but has three gaps:

1. **It teaches one of three master-skills.** ada-tool runs a partner trio — **govern** (self-governance:
   convert failures into controls), **operate** (run the substrate: positive-first lifecycle map +
   symptom→doc catalog + typed runbooks), **communicate** (write the prose + diagrams the other two
   produce). The starter bundles only the governance leg's reference. The *operate* and *communicate*
   legs and the trio-routing framing are absent.
2. **It lacks the book's now-stable conceptual vocabulary.** The starter speaks in
   "architecture / control / soft / hard / convert-a-failure" — correct but unnamed. The MAGE book has
   stabilized a coherent field vocabulary (Governance = "judgment, as code"; the Governed Engineering
   Environment as the *object* the method builds; the Modeling / Alignment Theses; Governance Conversion;
   Engineering Capital / Churn; Constraint / Sensor as the crisp names for architecture / control). The
   starter has **no noun for the thing being built** and no shared lexicon its legs speak in.
3. **Its EPIC / design templates lack ada-tool's models / type-system / analysis richness.** The
   ada-tool `EPIC-TEMPLATE.md` carries a §Models "which typed models does this touch / what's missing"
   entry, a §9 six-facet **type-system posture** section, and a rule-#57 **verification-tier**
   framing (SAFETY_BFS / LIVENESS_TLC / LINEAR_PROPERTY) that is the codebase's answer to "what
   *dynamic* analyses does this design commit to." The starter templates carry none of this.

**Cost of not doing it.** An adopter who installs the starter inherits a governance-only,
vocabulary-thin scaffold: they get the *method* but not the *object* (the GEE) it produces, not the
operate/communicate legs, and an Epic/design template that never prompts "what models does this touch,
what's their type-quality bar, and what static + dynamic analyses hold the invariants." Those omissions
are the exact gaps that make a governed environment shallow — a pile of guidance with no named target
and no analysis-completeness check.

**Why now.** The book vocabulary has stabilized (the `0.3-the-books-language.md` glossary + the
`theory_of_mage_declared.json` hypotheses are coherent), the trio of master-skills now exists in
ada-tool (`self-governance`, `operate-ada-tool-repo`, `self-communicate`), and a read-only skills-review
(agent afd168e0) produced a ranked upstream proposal the user ratified ("fire it up"). The material to
port is stable; the port is additive.

**Leverage.** Purely additive, portable content — new bundled shells + a glossary file + a handful of
Part-A header aliases and template sections. No restructure of the already-good Part A. Fix-once benefits
every future adopter of the starter.

**What would tell us we picked the wrong shape.** If a ported section still leaks ada-tool nouns
(`system-models/`, `rule #57`, `pyright`, `merge_train.py`) it is not portable — an adopter can't resolve
the reference. The portability lint (INV-2) is the early detector.

**Empirical check recipe (for the Final DoD reviewer, written now).**
- Portability: `grep -nE 'system-models/|rule #[0-9]|pyright|merge_train|colima|PdfModel' <ported-starter-files>` returns 0.
- Source-of-truth: the SSOT copy (`governance-catalog/downloads/CLAUDE-starter.md`) and the generated
  plugin copy (`plugin/mage/skills/self-governance/reference/downloads/CLAUDE-starter.md`) are byte-identical
  after `bundle_skill.py` runs; any third mirror is either deleted or drift-lint-clean.
- Interpretability: the submodule's own `python3 catalog.py validate` exits 0 (no dangling paths / bare
  rule numbers introduced).

## §1.1 Models & Invariants

**No ada-tool system-model touched** — every write surface of this Epic is a *documentation template* in
the `governance-catalog` submodule (a separate repo), not ada-tool code, `system-models/`, or a state
machine. The honest escape applies to the ada-tool side. But this Epic reasons *through* several models,
and the design **dogfoods** a model-completeness question, so the section is filled substantively.

**A. Models reasoned through — STUDY / UPDATE / ADD** (all in the governance-catalog submodule):

- **STUDIES** — (a) the **starter-template family** (`CLAUDE-starter.md`, `EPIC-TEMPLATE-starter.md`,
  `design-doc-template-starter.md`, `op-playbook-starter.md`, `agent-brief-starter.md`) — the shape to
  extend; (b) the **book glossary model** (`book/frontmatter/0.3-the-books-language.md` +
  `book-models/theory_of_mage_declared.json`) — the source of the Tier-1/Tier-3 term definitions; (c) the
  **`bundle_skill.py` generator model** — "the single writer of the generated" skill bundle; it copies
  `downloads/*` → `plugin/.../reference/downloads/*` and lifts Part A into `principles.md`. This is the
  SSOT+regen machine that Fork 1 turns on.
- **UPDATES** — the starter templates (content added). These are submodule docs, not ada-tool models —
  no ada-tool model↔code drift is introduced.
- **ADDS** — three new bundled artifacts in the submodule: `method-language-starter.md` (portable
  glossary subset), `operate-starter.md`, `communicate-starter.md`. Each must be wired into
  `bundle_skill.py`'s `vendor_downloads` so the generator ships them (else they never reach the bundle).

**The design's own dogfood (the model-completeness angle the brief calls out).** The templates ARE the
"model" of how an Epic / design is shaped. The user's ask — "if the template doesn't include an explicit
*what static analyses / what dynamic analyses* framing, it should" — is a **model-invariant-completeness**
question applied to the templates themselves: is the template's section-set complete over the full
analysis surface? Today the substance exists but is scattered — **static** analyses live in the
design-doc-starter §8 (enforcement→lints) and the (to-be-ported) type-system posture; **dynamic**
analyses live in §5 (second-order dynamics) and the (to-be-ported) verification-tier framing. The port
consolidates them into one explicit "Static & Dynamic Analyses" checklist so the completeness is visible,
not inferred. (Fork 2 — RATIFIED ALSO-ENHANCE — rules that ada-tool's OWN source template gains the same
consolidation, as a separate ratified phase.)

**B. Invariants — named, testable, with rule-#57 tier + A/B/C/D posture target.**

- **INV-1 (SSOT single-writer).** Every starter file has exactly ONE authored source
  (`governance-catalog/downloads/`); the plugin `reference/downloads/` copy is *generated* from it by
  `bundle_skill.py` and carries a provenance marker; no un-wired third copy diverges. *Verification tier:*
  `LINEAR_PROPERTY` (content-equality predicate) → a drift lint / property check. *Posture target:* **A**
  (ENFORCED-PROVEN — a drift check that goes RED when SSOT ≠ generated; the stale 14 KB ada-tool mirror is
  the pinned known-finding at HEAD that earns the A). *Fork-1 ruling (INSTALL + LOCAL-ADAPTER) reshapes the
  mirror side: the SSOT is installed, not hand-mirrored, and adopter deltas live in `*.local.md` / `local/`.*
- **INV-2 (portability).** No ada-tool-specific noun leaks into ported starter content (banned set:
  `system-models/`, `rule #<n>`, `pyright`, `merge_train.py`, `colima`, `PdfModel`, `.claude/…`). *Tier:*
  `LINEAR_PROPERTY` → grep-lint over the starter files. *Posture:* **A** (a portability ban-lint;
  proof-of-fire = a synthetic fixture containing a banned noun goes RED).
- **INV-3 (interpretability).** Every ported entry stands alone to an outside reader — no dangling paths
  into unshipped trees, no bare rule numbers (the submodule CLAUDE.md's governing rule). *Tier:*
  `LINEAR_PROPERTY` → the submodule's existing `catalog.py validate` (link-integrity + summary checks).
  *Posture:* **A** (existing gate; SENSOR already wired).
- **INV-4 (bundle freshness).** After any `downloads/` edit, `bundle_skill.py` was re-run and the
  generated plugin copy matches the SSOT. *Tier:* `LINEAR_PROPERTY` → the submodule's pre-commit hook
  (which force-stages regenerated files) + a bundle-drift check. *Posture:* **B→A** (the hook enforces on
  the single-writer path; a standalone drift check would raise it to A).

**Completeness (Axis-1).** These models are `STATIC-SHAPE` (documentation templates + a deterministic
generator) — no stall-capable lifecycle, so no liveness ◇ is owed. The retrodictive table: every known
failure mode (a copy drifts → INV-1; a noun leaks → INV-2; a dangling ref → INV-3; a stale bundle →
INV-4) maps to an invariant. The set is complete for a static-shape model.

**SENSOR vs CONSTRAINT.** All four invariants are build/commit-time properties of committed files, so a
CONSTRAINT/SENSOR *lint* is the right kind of control — there is no live runtime state to observe.

## §1.2 Closest Related Functionality & Models

**A. Nearest existing things.**
- **`bundle_skill.py`** (submodule) — the existing SSOT+regen generator. The three ADDed artifacts REUSE
  its `vendor_downloads` mechanism rather than inventing a new packaging path.
- **The existing closing "trust-nothing" independent review** in `EPIC-TEMPLATE-starter.md` §4 criterion
  5 — P5 adds its symmetric *opening* partner (the Phase-1b independent design review), so this is a
  DISTINCT-but-paired addition, not a duplicate.
- **The ada-tool `EPIC-TEMPLATE.md` §Models / §9 / rule-#57 blocks** — the source content P2 ports FROM;
  the port strips ada-tool nouns (REUSE-the-idea, not the text).
- **The submodule's `catalog.py validate`** — the interpretability gate INV-3 REUSES.

**B. DRY verdict.** REUSE `bundle_skill.py` (do not add a parallel packaging path). REUSE `catalog.py
validate` for interpretability. The one **join** introduced: the starter content now exists as an
authored SSOT (`downloads/`) AND a generated bundle (`plugin/.../reference/downloads/`) AND, today, a
stale ada-tool mirror — a fact-in-three-surfaces. Held at the **CODEGEN** rung by `bundle_skill.py` for
the SSOT→bundle pair (correct); the third mirror is the **below-affordable-rung** drop that Fork 1
resolves — the RATIFIED ruling is INSTALL + LOCAL-ADAPTER (install the SSOT, adopter deltas in
`*.local.md` / `local/`), which Phase 1b turns into the plug-convention design. Named here so P1b and
criterion 14 can audit it.

**C. Reference exemplar.** The ada-tool `operate-ada-tool-repo` skill's SSOT+regen+drift-gate discipline
(edit `pointers.yaml`/`runbooks.yaml`, regenerate the projection, a drift gate blocks the build on
divergence) is the pattern this Epic COPIES for Fork 1's resolution — and, fittingly, is one
of the disciplines the proposal (A2) upstreams. The Epic dogfoods what it ships.

## §1.3 Greatest Risks & Blast-Radius

**A. Greatest risks (ranked).**
1. **Submodule single-writer collision (highest likelihood).** The `governance-catalog` pre-commit hook
   rebuilds the site and force-stages generated `.html` + `book-models/*` on every commit, so two agents
   committing concurrently collide. Detection: a merge-conflict or a force-staged-file surprise at commit
   time. Mitigation: ALL impl phases serialize on the single-writer lock and run one-at-a-time, after the
   book v2 publish frees the lock (see §Sequencing).
2. **Portability leak (medium).** A ported section keeps an ada-tool noun and becomes unresolvable for an
   adopter. Detection: the INV-2 portability lint. Mitigation: author the lint in P2 alongside the port.
3. **Bundle desync (medium).** An editor touches `downloads/` but forgets `bundle_skill.py` regen, so the
   shipped bundle is stale. Detection: INV-4 bundle-drift check + the submodule hook. Mitigation: make
   "run `bundle_skill.py` + commit the regenerated bundle" a step in every impl phase's acceptance.
4. **Over-porting (low).** Dragging ada-tool's pyright/verification-tier *specifics* into the portable
   type-system facets instead of the portable type-QUALITY-bar idea. Detection: P1b review. Mitigation:
   the brief's "portable subset, strip the nouns" rule is explicit in each phase acceptance.

**B. Blast-radius.**
- **Subsystems / services** — none in ada-tool. The write surface is entirely the governance-catalog
  submodule's `downloads/` + generated bundle + `bundle_skill.py`.
- **Data** — none. No persisted state, billing, or customer artifact touched.
- **Agents / substrate** — the *published starter* is consumed by outside adopters and by ada-tool agents
  who read the self-governance skill's bundled reference. A wrong port degrades guidance quality but wires
  no gate that could break an in-flight agent. The ONE ada-tool-substrate question is the mirror (Fork 1):
  if ada-tool agents load `.claude/skills/self-governance/reference/downloads/`, that copy being stale is
  a live guidance-drift; the INSTALL + LOCAL-ADAPTER ruling resolves it (install the SSOT, keep local
  deltas in the overlay).
- **Deploy / runtime** — none in ada-tool. The submodule's own Pages deploy re-runs `catalog.py build` in
  CI; a broken schema can never be served (its build gate blocks it).

**C. Load-bearing premises (state so P1b can refute).**
- **PREMISE:** `governance-catalog/downloads/` is the authored SSOT and `bundle_skill.py` generates the
  plugin `reference/downloads/` copy from it. *Check:* `grep -n "downloads" bundle_skill.py` shows it
  reads `downloads/*` and writes the reference bundle (VERIFIED at design time: `bundle_skill.py` docstring
  "the single writer of the generated…", `_vendor_referenced_downloads` copies into `reference/downloads/`).
- **PREMISE:** the ada-tool mirror is stale, not canonical. *Check:* `wc -c` shows the mirror at 35 388 B
  vs the submodule copies at 49 533 B; `diff` shows they differ (VERIFIED at design time).
- **PREMISE:** the two submodule copies (`plugin/.../reference/downloads/` and `downloads/`) are kept
  in sync for `CLAUDE-starter.md`. *Check:* `diff` = identical (VERIFIED); NOTE the `downloads/` dir also
  holds files the plugin bundle does not vendor (`component-zone-model-starter.py`,
  `deployment-topology-starter.py`) — so `downloads/` is the superset SSOT, the bundle is a curated subset.
- **PREMISE:** the book Tier-1 terms the proposal names exist with crisp one-line definitions. *Check:*
  VERIFIED at design time in `0.3-the-books-language.md` — Governance ("Judgment, as code"), Governance
  Conversion, Compounding/Engineering capital, "Judgment is the scarce resource," Governed Engineering
  Environment, Constraint ("Prevent the mistake"), Sensor ("Detect the mistake"), Modeling Thesis,
  Alignment Thesis, Support ratio all present verbatim.

## §2 Cost calibration

- **P1 (founding design):** landed (this doc).
- **P1b (independent 2nd-Opus review + plug-convention design):** ~0.5 Opus-agent-day (read-only re-derive
  from the starter + book + proposal, rule on the §G forks — now ratified — and design the F1 plug convention).
- **P2 (template-richness port):** ~1 agent-day (two starter files + the INV-2 portability lint + regen).
- **P3 (book Tier-1 vocabulary + glossary file):** ~0.5–1 agent-day.
- **P4 (trio shells + "three partner skills" paragraph + bundle wiring):** ~1 agent-day.
- **P5 (Phase-1b DoD criterion into EPIC-starter):** ~0.25 agent-day.
- **P6 (Fork-1 install/local-adapter resolution + Fork-2 also-enhance ada-tool-source):** ~0.5–1 agent-day,
  scope set by the (now ratified) fork rulings.
- **Total:** ~3.5–5 agent-days, confidence ±1 day. **Confidence band is dominated by the plug-convention
  design (P1b/P6 scope) and the single-writer serialization overhead, not by the porting itself (mechanical).**

## §3 Phases

Phase 1 is planning/design (this doc). Every impl phase writes files in the `governance-catalog`
submodule and therefore (a) serializes on the single-live-writer lock and (b) is gated behind the book v2
publish (book-first is ratified). Each phase's acceptance includes "run `bundle_skill.py`, commit the
regenerated bundle, `catalog.py validate` exits 0." Each phase = a new `phase-<N>-260808.md` file
(agents never edit `main.md` after founding).

- [x] **Phase 1 — Opus founding design** (this `main.md`). Acceptance: valid EPIC-TEMPLATE v2 doc with
      §1/§1.1/§1.2/§1.3, phase plan, §4 DoD, §Models, and a §G forks section (≥4 forks in 5-field form).
      *Re-homed into the submodule 260807; §G forks now RATIFIED (see header).*

- [ ] **Phase 1b — Independent 2nd-Opus design review + plug-convention design** (per the parent method's
      double-Opus discipline, REQUIRED before any impl). A FRESH Opus (≠ this author) re-derives from the
      starter + book + `bundle_skill.py`, checks the load-bearing premises in §1.3C, confirms/refines the
      RATIFIED §G rulings, **designs the F1 plug convention** (installable SSOT + `*.local.md` / `local/`
      local-adapter overlay), returns RATIFY/REVISE, emits `phase-1b-review-260808.md` **in this submodule**.
      Acceptance: a landed RATIFY (REVISEs folded) + the plug-convention design before P2 dispatch.
      Prereqs: P1. **Not gated on the book publish** (design-only).

- [ ] **Phase 2 — Template-richness port.** Into `EPIC-TEMPLATE-starter.md` + `design-doc-template-starter.md`
      (SSOT copies under `governance-catalog/downloads/`): (a) a portable **§Models "what models does this
      touch / what's missing"** entry (STUDY/UPDATE/ADD phrasing; strip ada-tool nouns); (b) a portable
      **type-system posture** block (the type-QUALITY-bar idea + the six facets restated language-agnostically
      — NOT ada-tool's pyright/tsc specifics); (c) an explicit **"Static & Dynamic Analyses"** consolidated
      checklist (static = types + lints; dynamic = tests + property + state-machine/BFS + liveness). Author
      the **INV-2 portability lint** in the same phase. Acceptance: the three sections present + portable
      (INV-2 lint exit 0); `catalog.py validate` exit 0; bundle regenerated. Write surface: **SSOT
      `downloads/` → regen plugin bundle**. Prereqs: P1b RATIFY; book v2 published; single-writer free;
      Fork 2 RATIFIED ALSO-ENHANCE (adds a P6 sub-item).

- [ ] **Phase 3 — Book Tier-1 + Tier-3 vocabulary (Fork 4 RATIFIED: ship the glossary file).** Ship
      `method-language-starter.md` (a portable glossary subset: Tier-1 + Tier-3 terms, one line each, lifted
      from `0.3-the-books-language.md`) and wire the Tier-1 aliases into `CLAUDE-starter.md`'s Part-A headers
      + opening premise (Governance = "judgment, as code"; "Judgment is the scarce resource" as the opening
      premise; the Governed Engineering Environment as the named object; Modeling/Alignment Theses as the two
      backbones; Governance Conversion named; Engineering Capital/Churn as a pair; Constraint/Sensor aliased
      onto the architecture/control headers). Acceptance: the glossary file ships in the bundle (wired into
      `vendor_downloads`); the header aliases present; terms match the book verbatim; `catalog.py validate`
      exit 0. Write surface: **SSOT `downloads/` + `bundle_skill.py`**. Prereqs: P1b RATIFY; book publish;
      single-writer free.

- [ ] **Phase 4 — Trio shells (Fork 3 RATIFIED: both now).** Add `operate-starter.md` (Part-A DevOps
      mindset: positive-first lifecycle map, RCA-observability-first, symptom→class routing + typed runbook
      step-kinds RUNNABLE / JUDGMENT_AUTOMATABLE / JUDGMENT_IRREDUCIBLE) and `communicate-starter.md` (prose
      craft: name-the-genre/Diátaxis-mode first, house lexicon, less-is-more, run-the-audit-before-ship),
      plus a one-paragraph **"The three partner skills"** section in `CLAUDE-starter.md` naming the trio and
      how they route. Wire both shells into `bundle_skill.py`'s `vendor_downloads`. Acceptance: both shells
      ship in the bundle; the trio paragraph present; Part-A-only (no ada-tool Part-B content); `catalog.py
      validate` exit 0. Write surface: **SSOT `downloads/` + `bundle_skill.py`**. Prereqs: P1b RATIFY; book
      publish; single-writer free.

- [ ] **Phase 5 — Phase-1b independent-review criterion into the EPIC-starter DoD.** Add to
      `EPIC-TEMPLATE-starter.md` §4 a criterion: "a founding design earns a second, independent strong-model
      review before implementation dispatches; the reviewer re-derives from code and rules on the open
      forks (reviewer wins conflicts); returns RATIFY/REVISE." Acceptance: the criterion present + portable;
      `catalog.py validate` exit 0. Write surface: **SSOT `downloads/`**. Prereqs: P1b RATIFY; book publish;
      single-writer free.

- [ ] **Phase 6 — Source-of-truth resolution (Fork 1 RATIFIED INSTALL+LOCAL-ADAPTER; Fork 2 RATIFIED
      ALSO-ENHANCE).** Per Fork 1: implement the plug convention P1b designs — install the SSOT and route
      adopter deltas through a companion `*.local.md` file + `local/` directory (NOT a hand-synced mirror);
      the stale ada-tool copy resolves via install-from-SSOT + a drift check (INV-1 raised to A). Per Fork 2:
      add the consolidated Static & Dynamic Analyses subsection to the ada-tool `EPIC-TEMPLATE.md` /
      design-doc template (a SEPARATE, ratified change in the parent repo — a hot-spot doc every agent reads).
      Acceptance: the mirror is resolved (installed + drift-clean); the ada-tool template change lands green.
      Prereqs: P1b plug-convention design; Fork rulings (ratified).

- [ ] **Final Opus DoD review** — the 12-criterion §4 checklist, trust-nothing at HEAD.

## §4 Phase completion notes (thin index)

- **Phase 1 (260808):** founding design landed. Source-of-truth topology mapped (SSOT =
  `governance-catalog/downloads/`; plugin copy generated by `bundle_skill.py`; ada-tool `.claude/skills`
  mirror stale by 14 KB). Four §G forks surfaced.
- **Re-home (260807):** Epic re-homed from parent ada-tool `docs/epics/` into this submodule at
  `docs/epics/master-skill-starter-upstream-260807/main.md`; §G forks RATIFIED (F1 install+local-adapter;
  F2 also-enhance; F3 both shells; F4 glossary file); Phase-1b (review + plug-convention design) PENDING here.
- Phases 1b–6: one line each once they land.

## §5 Definition of Done

Per the parent ada-tool repo's method template (`docs/dev/EPIC-TEMPLATE.md`) §2 (MANDATORY criteria).
Adapted for a submodule-documentation Epic:

```
### Definition of done

- [ ] (1) Functional invariants — INV-1..INV-4 hold. Verified by the INV-2 portability lint (exit 0),
      the INV-1 bundle/mirror drift check, and `catalog.py validate` (INV-3) exit 0.
- [ ] (1b) Narrative numeric claims verified — every "N files / K→L KB / M terms" claim re-counted at close.
- [ ] (2) Docs updated — every starter file touched listed; the submodule INDEX/census reflects new bundled files.
- [ ] (2c) Higher-layer models updated — no ada-tool `system-models/` drift (no ada-tool code shipped);
      `bundle_skill.py` `vendor_downloads` updated for every ADDed artifact (method-language / operate /
      communicate shells) — else they never ship. Decline the ada-tool-model half with "no ada-tool model touched".
- [ ] (3) Lints authored — RUN FRESH at close — the INV-2 portability lint (and INV-1 drift lint per the
      Fork-1 install/local-adapter resolution) exit 0 on the ported files. Interpretability via `catalog.py validate` exit 0.
- [ ] (3a) ALL blocking gates green at close — submodule `catalog.py validate` + `catalog_tests.py` green end-to-end.
- [ ] (4) Tests cover the invariants — the portability lint's synthetic-fixture proof-of-fire (banned noun → RED);
      a bundle-drift fixture for INV-1/INV-4.
- [ ] (5) Final independent review (closer) — read-only Opus, trust-nothing at HEAD; routes every regression with a tag.
- [ ] (5a) Routing-completeness audit — every [FIX]/[LINT]/[DESIGN]/[AUDIT]/[PROCESS] across agent reports routed; "not addressed" = 0.
- [ ] (11) Phase-1b independent 2nd-Opus review + plug-convention design landed + REVISEs applied —
      `phase-1b-review-260808.md` (in this submodule) with a RATIFY/REVISE from a FRESH Opus; every §G fork
      RULED (ratified); the F1 plug convention designed; impl dispatched only after RATIFY.
- [ ] (7) Pin tests RE-RUN at close — every lint the Epic owns re-executed at HEAD; actual pass/fail recorded.
- [ ] (8) Design-doc review + follow-ups scheduled — the ported starters + this main.md scanned for [DESIGN]/[LINT]/doc-rot; each routed.
- [ ] (12) Field note authored OR [NO-FIELD-NOTE] justified.
- [ ] (13) Whole-Epic token cost recorded at close.
- [ ] (9) Type-system posture — **no type-system surface — this Epic ships documentation templates + a
      stdlib-only generator wiring, no typed application code.** (The ported *content* teaches type-system
      posture; the Epic itself ships no compiled types.)
- [ ] (10) Docs + models traceability — the SSOT→bundle→(install/local-adapter) join held at the highest
      affordable rung (CODEGEN via bundle_skill.py for SSOT→bundle; mirror per Fork 1 install+local-adapter); no drift.
- [ ] (10a) DoD drift-audit runbook run (submodule analogue: `catalog.py validate` + bundle-drift check).
- [ ] (14) Joins held at the highest AFFORDABLE rung — the 3-copy starter join enumerated + held (CODEGEN + Fork-1 install/local-adapter resolution).
- [ ] (15) Design-context triad present + substantive — §1.1 / §1.2 / §1.3 all filled (this doc).
- [ ] (16) Model-invariant-completeness re-audit — "No ada-tool system-models touched"; the submodule
      template/glossary "models" re-audited (static-shape class; retrodictive table in §1.1 complete).
```

## §6 Open questions

The judgment-class forks live in **§G — Open forks for the user** below and are now **RATIFIED** (see the
header). §6 holds no additional open questions beyond those forks and the plug-convention design deferred
to Phase 1b.

## §G — Open forks for the user (5-field form) — RATIFIED

> **All four forks are RATIFIED (author, 260807).** The ruling for each is stated in the header and repeated
> at the top of each fork below; the full 5-field framing (options + this doc's original recommendation) is
> retained verbatim as the design record.

### Fork 1 — Source of truth for the starter files (3 divergent copies, no ada-tool-side sync)

**RATIFIED: INSTALL + LOCAL-ADAPTER** — install the SSOT; adopter deltas live in a companion file
`*.local.md` + directory `local/` (NOT an in-file section, NOT a hand-synced third copy). Phase 1b designs
the plug convention.

- **Question.** Which copy is canonical, and how is the ada-tool mirror kept honest?
- **Why it matters.** There are THREE copies of the starter set. **Finding (verified at design time):**
  (1) `governance-catalog/downloads/` (49 533 B `CLAUDE-starter.md`) is the **authored SSOT** — it also
  holds files the bundle doesn't vendor, so it is the superset source; (2)
  `governance-catalog/plugin/mage/skills/self-governance/reference/downloads/` (49 533 B, **byte-identical**)
  is **generated** from #1 by `bundle_skill.py` ("the single writer of the generated" bundle); (3) the
  ada-tool `.claude/skills/self-governance/reference/downloads/` mirror (35 388 B) is a **third, un-wired,
  14 KB-stale copy** with no regen path. Editing the wrong copy, or shipping the stale mirror to ada-tool
  agents, silently drifts the guidance.
- **Options.** **(a)** Declare `governance-catalog/downloads/` canonical (it already is); keep the plugin
  copy generated by `bundle_skill.py` (already correct); **delete the ada-tool `.claude/skills` mirror**
  and have ada-tool agents consume the self-governance skill from the submodule/plugin (UNIFY-by-removal —
  strongest, if the harness can load from there). **(b)** Keep the mirror but declare it
  *generated-from-submodule*: add a provenance header + a **drift lint** that fails when it diverges from
  the SSOT (the `operate-ada-tool-repo` SSOT+regen+drift-gate pattern — the exemplar in §1.2C). **(c)** Do
  nothing (status quo — the mirror keeps drifting). Rejected on its face; named only for completeness.
- **Recommendation (original).** **(a) if** ada-tool's skill loader can read the submodule/plugin copy
  (verify how the harness resolves `self-governance`); **else (b)**. Both make the SSOT the single writer;
  (a) removes a copy, (b) controls it. NOT (c). *→ Superseded by the RATIFIED install + local-adapter
  ruling, which generalizes (a)/(b): install the SSOT and overlay adopter deltas via `*.local.md` / `local/`.*
- **Blast-radius.** Small + submodule-local for the content; the one ada-tool-substrate touch is the
  mirror deletion/lint (a `controls`-domain change). No product/deploy impact.

### Fork 2 — Static/dynamic-analysis framing: port-only, or also enhance the ada-tool source?

**RATIFIED: ALSO-ENHANCE** — merge the consolidated "Static & Dynamic Analyses" best-practice into the
skill/source, not port-only (staged as P6, a separate ratified change to the parent hot-spot doc).

- **Question.** Do we ONLY port a consolidated "Static & Dynamic Analyses" checklist into the *starter*
  templates, or ALSO add it to ada-tool's own `EPIC-TEMPLATE.md` / design-doc template?
- **Why it matters.** The user said "if it doesn't include it, it should." The substance exists in
  ada-tool but is **scattered**: static analyses live in the design-doc §8 (enforcement→lints) + §9
  type-system posture; dynamic analyses live in §5 second-order-dynamics + the rule-#57 verification-tier
  (BFS/TLC/property). There is no single "here is the static + dynamic analysis surface this design
  commits to" checklist. Porting a *consolidated* version to the starter is in-scope; enhancing the
  ada-tool source is a separate change to a hot-spot doc.
- **Options.** **(a)** Port-only — add the consolidated checklist to the starters; leave the ada-tool
  source as-is (its substance is present, just distributed). **(b)** Also-enhance — add the same
  consolidated subsection to ada-tool's `EPIC-TEMPLATE.md` §Models + design-doc template, as a separate
  ratified P6 sub-item.
- **Recommendation.** **(b) also-enhance, staged as P6** — the consolidation is genuinely useful in-house
  (it makes analysis-completeness a visible checklist item, not something inferred across four sections),
  and dogfooding it in the source keeps source and starter aligned. But it edits a doc every agent reads,
  so it earns its own ratified phase, NOT a silent fold into P2. (The brief's NON-goal correctly forbids
  editing `EPIC-TEMPLATE.md` *now* — this fork is the ratification gate.) *→ RATIFIED as recommended.*
- **Blast-radius.** (a) submodule-only. (b) adds one hot-spot ada-tool doc edit (`docs/dev/EPIC-TEMPLATE.md`)
  — no code, but every agent reads it; a poor edit adds boot-context cost. Contained by making it a
  reviewed standalone phase.

### Fork 3 — Trio scope: ship both operate + communicate shells now, or stage communicate later?

**RATIFIED: BOTH NOW** — P4 ships both `operate-starter.md` and `communicate-starter.md`.

- **Question.** Does P4 ship both `operate-starter.md` and `communicate-starter.md`, or only operate now
  with communicate deferred?
- **Why it matters.** Both are Part-A-only shells (portable mindset, no ada-tool Part-B content), so both
  are low-risk and additive. The trio framing in `CLAUDE-starter.md` reads cleaner if both legs exist to
  route to. Staging communicate later leaves the trio paragraph pointing at one missing leg.
- **Options.** **(a)** Ship both shells in P4. **(b)** Ship operate in P4; defer communicate to a later
  phase; the trio paragraph names communicate as "coming."
- **Recommendation.** **(a) both now** — they are cheap, additive, and the trio framing is incomplete
  without the third leg. Defer only the *deeper* content (the full SSOT+regen A2 discipline, the full
  typed-runbook A3 catalog) if scope pressure appears, not the shells themselves. *→ RATIFIED as recommended.*
- **Blast-radius.** Submodule-only; two new bundled files + `bundle_skill.py` wiring. No product impact.

### Fork 4 — Vocabulary depth: Tier-1 aliases only, or a Tier-1 + Tier-3 glossary file?

**RATIFIED: SHIP THE GLOSSARY FILE** — P3 ships `method-language-starter.md` (Tier-1 + Tier-3) AND wires
the Tier-1 aliases.

- **Question.** Does P3 ship a full `method-language-starter.md` glossary (Tier-1 + Tier-3 terms), or only
  wire the Tier-1 header aliases into `CLAUDE-starter.md`?
- **Why it matters.** The one-line definitions are cheap to lift (they exist verbatim in the book
  glossary). A dedicated glossary file is the *shared lexicon* the trio (Fork 3) speaks in — it pays off
  across all three legs. Aliases-only leaves the terms defined inline but with no single lookup surface.
- **Options.** **(a)** Ship `method-language-starter.md` with Tier-1 + Tier-3 (one line each) AND wire the
  Tier-1 aliases. **(b)** Tier-1 aliases only (no separate glossary file); add Tier-3 later if demanded.
- **Recommendation.** **(a) Tier-1 + Tier-3 glossary file** — near-zero cost (verbatim lift), and it
  establishes the lexicon every later upstream (the trio shells) references. This is the proposal's
  "smallest first step," and it is the highest-leverage single artifact. *→ RATIFIED as recommended.*
- **Blast-radius.** Submodule-only; one new bundled file + a few header touches. No product impact.

## §7 Cross-references

> These reference the parent ada-tool repo (the *upstream-FROM* source) and this submodule (the
> *upstream-TO* target). This submodule ships standalone; the ada-tool paths below are the porting source,
> not links into a tree this repo serves.

- Source proposal: `scratchpad/claude-starter-upstream-proposal-260807.md` (ranked A/B/C/D).
- Upstream-FROM source (parent ada-tool repo): `docs/dev/EPIC-TEMPLATE.md` §1.1 Models (~L255),
  §9 Type-system posture (~L1148), rule-#57 verification-tier (~L281), DoD criteria (9)/(16) (~L1236/L1241).
- Upstream-TO targets (this submodule, read-only until impl): `downloads/*` (SSOT),
  `plugin/mage/skills/self-governance/reference/downloads/*` (generated bundle).
- Generator: `bundle_skill.py` (SSOT+regen single-writer).
- Book vocabulary: `book/frontmatter/0.3-the-books-language.md`, `book-models/theory_of_mage_declared.json`.
- Submodule discipline: this submodule's `CLAUDE.md` (single-live-writer + interpretability + standalone posture).
- Related ada-tool skills upstreamed as the trio: `self-governance`, `operate-ada-tool-repo`, `self-communicate`.

## §8 Tag

`[DESIGN]` <!-- followup-domain: pre-epic --> — founding design. Impl phases re-tag: P2/P5 `[DESIGN]`→`[FIX]`
+ `[LINT]` (INV-2 portability lint) <!-- followup-domain: controls -->; P3/P4 `[FIX]`
<!-- followup-domain: other --> (submodule docs); Fork-1 install/local-adapter drift lint `[LINT]`
<!-- followup-domain: controls -->.
