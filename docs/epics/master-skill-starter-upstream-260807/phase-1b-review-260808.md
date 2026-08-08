<!-- phase-1b-review · master-skill-starter-upstream-260807 · reviewer: fresh Opus (≠ P1 author) -->
# Phase-1b Independent Design Review — master-skill-starter-upstream-260807

**Reviewer:** Fresh Opus, independent of the Phase-1 author (rule #58 double-Opus discipline).
**Posture:** READ-ONLY. Written to scratchpad; the orchestrator places it into the submodule.
**Scope:** re-derive the load-bearing claims from code; confirm/refine the four RATIFIED §G forks (rulings
STAND — not re-opened); design the F1 local-adapter plug convention; reshape §3.

**PHASE-1B VERDICT: REVISE (3 items)** — the core design RATIFIES (SSOT→bundle topology, the F1 plug
convention, the invariant frame are sound and the §1.3C premises verify), but an independent re-derivation
from the *actual* plugin tree shows the design's §1 gap-analysis and Fork-3/Phase-4 scoping are **stale**:
the operate *and* communicate legs already ship as plugin skills, and `self-operations-starter.md` already
exists. The three REVISEs correct the scoping and add the plug-convention's own controls. In autonomous
mode these fold and impl proceeds (reviewer wins).

---

## 1. Re-derivation check — load-bearing claims

I re-derived every premise the design rests on, from the files, not from the design's assertions.

### 1.1 The 3-copy SSOT → bundle → stale-mirror topology — CONFIRMED, with a correction

| Claim (design) | Independent finding | Verdict |
|---|---|---|
| `governance-catalog/downloads/CLAUDE-starter.md` is the authored SSOT (49 533 B) | `downloads/CLAUDE-starter.md` = **49533 B** (`ls`) | ✅ |
| plugin `reference/downloads/CLAUDE-starter.md` is byte-identical, generated | `diff -q` = **IDENTICAL**; `bundle_skill.py` docstring L5-6 "single writer of the generated half of the plugin" | ✅ |
| ada-tool `.claude/skills/self-governance/reference/downloads/CLAUDE-starter.md` is a 3rd, stale copy (35 388 B, ~14 KB behind) | mirror = **35388 B** at `.claude/skills/self-governance/reference/downloads/` | ✅ |
| `downloads/` is a superset SSOT; the bundle vendors a curated subset | SSOT dir has 18 files incl. `component-zone-model-starter.py`, `deployment-topology-starter.py`; plugin `reference/downloads/` ships only 5 | ✅ |

The topology is real and correctly characterized. `bundle_skill.py` is registry-driven (`SPECS`,
`SkillSpec`) and is the single writer of the generated bundle — verified at `bundle_skill.py:5-7, 38-45,
189-208` (`_vendor_referenced_downloads`) and `211-226` (`_vendor_explicit_downloads`). The generated
files carry the `GEN_NOTE` provenance banner (L35). **INV-1 (SSOT single-writer) and INV-4 (bundle
freshness) are grounded in code that exists.** No stronger-model bias here — the design does not invent a
generator, it turns on the one already shipping.

### 1.2 ★ Correction — the "operate + communicate legs are absent" claim is STALE

The design's §1 gap 1 states: *"The starter bundles only the governance leg's reference. The operate and
communicate legs and the trio-routing framing are absent."* This is **wrong against the current tree**:

- `plugin/mage/skills/` ships **three** skills today: `self-governance`, `self-operations`,
  `self-communicate` (`ls plugin/mage/skills/`).
- **self-operations is fully present and bundle-wired.** `bundle_skill.py:82-107` declares a
  `SELF_OPERATIONS` SkillSpec; `downloads/self-operations-starter.md` (6823 B) is its Part-A source; the
  skill ships `principles.md` (generated), a hand-authored `SKILL.md`, `examples/` (14 runbook/lifecycle
  files), `hooks/`, and `templates/`.
- **self-communicate is present but hand-authored** — NOT in `bundle_skill.py`'s `SPECS`
  (`SPECS = [SELF_GOVERNANCE, SELF_OPERATIONS]`, L109). It ships `SKILL.md` + `writing/` + `drawing/`,
  including its own `writing/lexicon.md` (the F1 precedent).

So the genuine gaps are **narrower and different** from what §1 claims:
1. The **trio-routing framing** inside `CLAUDE-starter.md` is indeed absent — that part of §1 stands.
2. `operate-starter.md` (Phase 4 / Fork 3) is **redundant** with the existing `self-operations-starter.md`.
3. `self-communicate` is **outside the SSOT→bundle managed set** — and its `.claude/skills/` copy DIFFERS
   from its `plugin/` copy (`diff -q` = DIFFER). That is a **second instance of the exact mirror-drift the
   Epic exists to kill**, un-named in §1.2B's join enumeration.

This is a genuine re-derivation win — the design was drafted against a tree state where the trio had not
yet all landed in the plugin, and the founding author reasoned from the proposal rather than the live
`plugin/mage/skills/` dir. It does not sink the Epic; it re-scopes Phase 4 and enlarges the F1 plug
convention's coverage. Routed as REVISE-1 and REVISE-3.

### 1.3 Book Tier-1/Tier-3 vocabulary — CONFIRMED verbatim

Every term the design imports exists in `book/frontmatter/0.3-the-books-language.md` with the claimed
definition: **Governance** = "*Judgment, as code*" (L21), **Governance Conversion** (L31), **Compounding**
(L34) / **Engineering capital** = "*Judgment that compounds*" (L36), **"Judgment is the scarce resource"**
(L40), **Governed Engineering Environment** (L76), **Constraint** = "*Prevent the mistake*" (L82),
**Sensor** = "*Detect the mistake*" (L84), **Modeling Thesis** (L27), **Alignment Thesis** (L29),
**Support ratio** (L78). F4's glossary lift is a clean verbatim extraction — no fabrication risk.

### 1.4 INV-set completeness — sound for a static-shape model, but under-covers the plug convention

The four invariants (INV-1 SSOT single-writer, INV-2 portability, INV-3 interpretability, INV-4 bundle
freshness) are individually well-formed, each carries a rule-#57 verification tier (all `LINEAR_PROPERTY`,
correct for build-time file predicates), and the retrodictive table in §1.1 maps each known failure to an
invariant. For the *porting* work the set is complete. But **F1 introduces a new subsystem — the
install/refresh tool + the local-adapter overlay — and that subsystem owns invariants the current INV set
does not name** (plug-partition disjointness; refresh-preserves-local). The design correctly defers "the
plug convention" to Phase 1b; this review supplies those invariants (INV-5/INV-6, §3 below). Routed as
REVISE-2.

### 1.5 Bias scan

- **Stronger-model bias:** none detected — the design reuses `bundle_skill.py` and `catalog.py validate`
  rather than proposing a bespoke engine.
- **Strangler-fig / over-engineering bias:** the design resists it well (REUSE verdicts in §1.2B, the
  A22 right-sizing is implicit). The one place over-engineering could creep in is the F1 tool: the ruling
  explicitly forbids a 3-way merge, and the disjoint-set partition (below) keeps it a pure overwrite —
  I confirm that is the minimal sound shape, not a compromise.
- **Under-derivation bias (the real one):** the design reasoned from the proposal, not the live tree,
  which is how the trio-legs-already-exist finding slipped. This is precisely what the independent
  re-derivation is for.

---

## 2. Fork soundness (rulings STAND — not re-opened)

**F1 — INSTALL + LOCAL-ADAPTER.** Sound and implementable. Install-from-SSOT + an adopter overlay is the
correct generalization of the rejected "hand-synced mirror." The file/dir granularity ruling (`*.local.md`
+ `local/`, NOT section-level) is the load-bearing call, and it is *right*: a section-level plug forces a
3-way merge on refresh (the lexicon's `## Your house vocabulary` section would need merging every time
upstream edits `lexicon.md`), whereas file/dir granularity makes the upstream and adopter file sets
**disjoint**, so refresh is a clean overwrite of the upstream set with the adopter set untouched. Risk to
note (not re-opening): the adopter must accept that a *section within* an upstream file cannot be locally
overridden — only whole-file append (`foo.local.md`) or a new standalone file (`local/**`). That is the
intended trade and the plug design below makes it explicit.

**F2 — ALSO-ENHANCE.** Sound. Consolidating the scattered static/dynamic-analysis surface into one
checklist and dogfooding it in the parent's `EPIC-TEMPLATE.md` is defensible; the design correctly gates it
as its own ratified phase (P6 sub-item) because it edits a hot-spot boot-context doc every agent reads.
The NON-goal that forbids editing `EPIC-TEMPLATE.md` *now* is the right seatbelt. No re-open.

**F3 — BOTH SHELLS NOW.** The ruling (ship both legs' framing now) STANDS, but its **implementation is
mis-scoped** by the stale §1 (see §1.2). The trio-routing paragraph in `CLAUDE-starter.md` should ship now;
`operate-starter.md` should be **reconciled with the existing `self-operations-starter.md`, not created
fresh**; and the communicate leg's Part-A source is the genuinely-new artifact. The *intent* of F3 (the
trio framing exists to route to all three legs) is fully served — the correction is about *which files
already exist*. Routed as REVISE-1.

**F4 — SHIP THE GLOSSARY FILE.** Sound and cheapest of the four (verbatim lift from a verified source, §1.3).
`method-language-starter.md` as a Tier-1+Tier-3 file, wired into a `vendor_downloads`, is the right shape.
No risk beyond keeping the definitions verbatim (INV-2 portability lint + a "matches book" check cover it).
No re-open.

---

## 3. ★ The concrete local-adapter plug convention (the F1 design artifact)

The install-with-adapter model has three parts: **how a skill declares its plug points**, **how the
overlay composes at read time**, and **what the install/refresh tool does**. Design goal: an adopter can
`refresh` from upstream at any time and *never* lose local tinkering, with **no merge** — because upstream
files and adopter files are disjoint by naming convention.

### 3.1 The partition — the one idea the whole convention rests on

Every file in an installed skill is owned by exactly one side:

- **Upstream-owned** — any file NOT matching `*.local.md` and NOT under a `local/` directory. The
  install/refresh tool **overwrites** these on every refresh. The adopter must not edit them (edits are
  lost on refresh — same contract as `bundle_skill.py`'s `GEN_NOTE` banner).
- **Adopter-owned** — any `*.local.md` file, or any file under `local/`. The tool **never reads, writes,
  or deletes** these. The adopter tinkers here freely.

`upstream-owned ∩ adopter-owned = ∅` by construction. **Refresh is therefore a pure overwrite-preserve:
overwrite the upstream set, touch nothing else.** No 3-way merge exists to get wrong (the F1 ruling's
central requirement). This is the "adopt the schema, skip the runtime" move applied to package managers —
it is exactly how `apt`/`dpkg` treat a config-file `.dpkg-new` split, minus the merge prompt.

### 3.2 How SKILL.md DECLARES plug points

SKILL.md gains a single declarative block — enumerable, so a lint can walk it (typed-namespaces-over-strings):

```markdown
## Local adapter (plug points)

This skill is installed from upstream and refreshed in place. Your local additions live in files
the refresh never touches:

- **File overlays** — for any upstream file listed below, create a sibling `*.local.md`; the agent
  reads it as an APPEND after the upstream file. Declared overlays:
  - `writing/lexicon.md` → `writing/lexicon.local.md`  (your house vocabulary rows)
- **Directory drop-in** — any file you place under `local/` is discovered and read on the topic it
  names. Upstream never ships into `local/`.
```

Two plug kinds, both declared in one place:
- **File overlay** — a named upstream file that accepts a sibling `.local.md`. The declaration is the
  *allow-list*: an orphan `*.local.md` with no declared base, or no corresponding upstream file, is a lint
  finding (INV-5).
- **Directory drop-in** — the `local/` dir, always available, no per-file declaration; for adopter-authored
  standalone material (a new runbook, a house-specific note) that upstream does not own.

### 3.3 The composition (routing) contract — APPEND only, resolved at read time

Skills are read by the agent, not compiled, so composition is a **reading convention SKILL.md states**, not
a build step:

- **`foo.local.md` composes as APPEND over `foo.md`.** When the agent consults `foo.md`, it also reads
  `foo.local.md` if present and treats it as adopter additions to the upstream content. This matches the
  lexicon precedent exactly: the portable base rows stay in `lexicon.md`; the adopter's house rows are the
  append. **No OVERRIDE mode** — override is what forking the whole file would be, and it defeats refresh;
  if an adopter needs to replace upstream wholesale, that is a fork, out of scope for the adapter. Keeping
  the model append-only is the A19 uniformity win: one composition rule an agent applies on reflex.
- **`local/**` files are standalone** — discovered by "read anything under `local/`," not composed over a
  base. They are the adopter's own topics.

The "plug = trigger + SKILL.md routing" model from the self-communicate precedent holds: the trigger is
"agent consulting this topic," the routing is the SKILL.md instruction to also read the overlay. Nothing
new in the harness; the composition is prose the agent follows, exactly like self-communicate's SKILL.md
routes to its `writing/` siblings today.

### 3.4 The install/refresh tool semantics

A new tool (or a `bundle_skill.py --install <skill> <dest>` / `--refresh` mode — prefer extending
`bundle_skill.py` since it already owns the upstream-side generation and is stdlib-only, A9 single-source):

- **install** — copy every upstream-owned file of the skill into the adopter's skill dir. If a
  `*.local.md` / `local/` already exists at the dest, leave it. Emit a manifest (`.upstream-manifest`)
  listing every upstream-owned file written.
- **refresh** — recompute the upstream file set, **overwrite exactly the manifest files**, add any new
  upstream files, and delete upstream files that vanished upstream (tracked via the old manifest). **Never**
  enumerate or touch `*.local.md` / `local/**`. Re-emit the manifest.
- **Guard (assert, fail-loud):** no upstream-owned file may be named `*.local.md` or sit under `local/`
  (else the tool would clobber an adopter file) — this is a hard precondition, checked before any write.

No 3-way merge, no diff prompt, no backup-and-restore dance. The disjoint partition makes overwrite safe.

### 3.5 First adopter — migrate the lexicon's section-plug to file/dir form

The lexicon's `## Your house vocabulary` section (`writing/lexicon.md:231-263`) is today a section-level
plug — a designated empty table + a bootstrap recipe the adopter fills *in place*. Migrate:

- **Keep upstream-owned in `lexicon.md`:** the portable base (all the standard-SE domain tables) AND the
  `## Your house vocabulary` heading, the empty-table template, and the bootstrap recipe (they are
  *guidance*, portable, upstream's to maintain).
- **Move adopter rows to `writing/lexicon.local.md`:** the actual house-dialect rows an adopter fills in.
  SKILL.md declares the `lexicon.md → lexicon.local.md` overlay; the recipe's step 4 ("Propose the table")
  now says "write the rows into `lexicon.local.md`."
- **Result:** upstream can edit the portable base and refresh cleanly; the adopter's house vocabulary
  survives every refresh untouched. This is the concrete proof the convention works, and it is the second
  site of the "adopter tinkers on a portable base" pattern (self-governance's `CLAUDE-starter.md` Part-B
  stub is the first) — extract-on-second-site justifies building the convention now.

### 3.6 Invariants + the drift/wiring lint (extends the design's INV set)

- **INV-5 (plug-partition wiring)** — every declared file overlay in SKILL.md names a real upstream file;
  every `*.local.md` present has a corresponding upstream base and a declaration; no upstream-owned file is
  named `*.local.md` or lives under `local/`. *Tier:* `LINEAR_PROPERTY` → a **plug-wiring lint** that walks
  the SKILL.md `## Local adapter` block and the skill tree. *Posture target:* A. Proof-of-fire: an orphan
  `foo.local.md` with no `foo.md`, or an upstream file placed under `local/`, goes RED.
- **INV-6 (refresh preserves local)** — the install/refresh manifest excludes all `*.local.md`/`local/**`;
  a refresh preserves every adopter file byte-for-byte. *Tier:* `LINEAR_PROPERTY` → a **failure-injection
  test** (memory `feedback_failure_injection_over_real_defects`): install, write a synthetic
  `lexicon.local.md` + a `local/x.md`, run refresh, assert both survive unchanged and the upstream file was
  overwritten. *Posture target:* A.

These two extend the design's INV-1 (which reshapes to "the upstream side is single-writer; the adopter
side is disjoint and preserved") rather than replacing it. They are the controls the F1 subsystem owns
(rule #46 — a substrate owns its observability/enforcement end-to-end).

### 3.7 Coverage note — bring self-communicate under the managed set (REVISE-3)

self-communicate today has two hand-maintained copies (`.claude/skills/` vs `plugin/`, verified DIFFERENT)
and is not in `bundle_skill.py`'s `SPECS`. That is the **second instance** of the mirror-drift the Epic
kills. The install/refresh tool should govern self-communicate too: either add a `SELF_COMMUNICATE`
SkillSpec (if any part is generated) or, since it is hand-authored, register it as install/refresh-managed
so the SSOT→installed flow (and the lexicon overlay) applies. Name this in §1.2B's join enumeration.

---

## 4. Phase-plan impact (how the ratifications reshape §3)

- **Phase 4 (Fork 3) — RE-SCOPE (REVISE-1).** Not "add `operate-starter.md` AND `communicate-starter.md`."
  Instead: (a) ship the trio-routing paragraph in `CLAUDE-starter.md` (unchanged, still needed); (b)
  **reconcile** the operate framing with the *existing* `self-operations-starter.md` + `self-operations`
  skill — do NOT create a redundant `operate-starter.md`; (c) author the genuinely-new communicate Part-A
  source and decide its bundle status (self-communicate is hand-authored today; either add a
  `SELF_COMMUNICATE` SkillSpec or leave authored and just wire routing). Acceptance updates accordingly.

- **Phase 6 (Fork 1) — REPLACE the thin "source-of-truth resolution" with the full plug-convention build
  (REVISE-2).** The old phase said "implement the plug convention P1b designs." Concretely, Phase 6 now =
  (a) extend `bundle_skill.py` with `install`/`refresh` modes + manifest (§3.4); (b) add the
  `## Local adapter` declaration to each managed skill's SKILL.md (§3.2); (c) migrate the lexicon
  section-plug to `lexicon.local.md` (§3.5); (d) author the INV-5 plug-wiring lint + the INV-6
  refresh-preserves-local failure-injection test (§3.6); (e) bring self-communicate under the managed set
  (§3.7); (f) resolve the stale ada-tool `CLAUDE-starter.md` mirror via install-from-SSOT; (g) the Fork-2
  ALSO-ENHANCE parent-doc edit stays its own ratified sub-item. This is ~1.5–2 agent-days, up from the
  design's ~0.5–1 — the plug convention is a small subsystem, not a one-file fix. Update §2 cost.

- **Phases 2, 3, 5 — UNCHANGED.** The template-richness port, the glossary file, and the DoD-criterion
  additions are unaffected by the trio-existence correction. They remain gated on P1b RATIFY (this review,
  after REVISEs fold), book v2 published, single-writer free.

- **DoD §5 — add INV-5/INV-6 to criteria (1), (3), (4).** The portability lint and drift check the DoD
  already names now sit alongside the plug-wiring lint and the refresh-preserves-local test.

---

## 5. Verdict + routed REVISEs

**PHASE-1B VERDICT: REVISE (3 items).** The core design RATIFIES: the SSOT→bundle→stale-mirror topology is
real and correctly characterized, `bundle_skill.py` is the single writer, the four §G rulings stand and are
implementable, the §1.3C premises all verified, and the book vocabulary lifts are verbatim-safe. The plug
convention (§3) is delivered. The REVISEs correct a stale gap-analysis and supply the plug subsystem's own
controls; in autonomous mode they fold and impl proceeds (reviewer wins, per rule #58).

- **REVISE-1** `[AUDIT]→[DESIGN]` <!-- followup-domain: pre-epic --> — Correct §1 gap-1, Fork 3, and
  Phase 4. The operate leg is NOT absent: `self-operations` ships as a bundle-wired plugin skill with
  `downloads/self-operations-starter.md`, and self-communicate ships hand-authored. Re-scope Phase 4 to
  *reconcile* with the existing operate starter (no redundant `operate-starter.md`) + ship trio-routing +
  author only the genuinely-new communicate source. Verified: `ls plugin/mage/skills/`,
  `bundle_skill.py:82-109`, `downloads/self-operations-starter.md`.

- **REVISE-2** `[DESIGN]+[LINT]` <!-- followup-domain: controls --> — Adopt the §3 plug convention as the
  Phase-6 build, and add its two invariants: **INV-5** (plug-partition wiring lint) and **INV-6**
  (refresh-preserves-local failure-injection test). Extend the install/refresh tool as a `bundle_skill.py`
  mode (overwrite upstream-owned, never touch `*.local.md`/`local/**`, no 3-way merge). Update §2 cost
  (Phase 6 ~1.5–2 agent-days) and §5 DoD criteria (1)/(3)/(4).

- **REVISE-3** `[AUDIT]→[FIX]` <!-- followup-domain: controls --> — Name self-communicate's un-managed
  double copy (`.claude/skills/` vs `plugin/`, verified DIFFERENT; not in `bundle_skill.py` SPECS) in
  §1.2B's join enumeration as the *second site* of the mirror-drift, and bring it under the install/refresh
  managed set in Phase 6. Verified: `diff -q` = DIFFER; `SPECS = [SELF_GOVERNANCE, SELF_OPERATIONS]`.

**Impl gating (confirmed):** design-only P1b is not book-gated; all impl phases (P2–P6) remain gated on
book v2 published (DONE per the header) + the governance-catalog single-live-writer lock free + this
RATIFY (REVISEs folded). The submodule single-writer constraint (§1.3A risk 1) is real — serialize every
impl phase.

PHASE-1B VERDICT: REVISE (3 items)
