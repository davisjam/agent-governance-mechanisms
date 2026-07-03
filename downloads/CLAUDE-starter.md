<!-- Redacted starter mirror of a real, mature CLAUDE.md — the governance-rules half
     (everything before the project's "## CLI Commands" section). Product identity is redacted;
     doc/tool paths are kept as illustrative structure. This is a MENU, not a drop-in: adopt the
     rules that fit your repo, adapt the rest, delete what doesn't apply. Companion to the
     agent-governance-mechanisms catalogue — each rule here maps to a control writeup there. -->

# CLAUDE.md — <Project>

This is a **redacted starter** — the governance-rules half of a real, mature CLAUDE.md from an
**agent-team-as-team** codebase (most code is written by dispatched AI agents; the discipline below
exists to make that safe at scale). Product-specific details are stripped; adapt the rest to your repo.

This file has two parts:

- **Part A — Davis AI-First Engineering Method.** Portable principles for AI-collaborative engineering.
  Apply on every touch; they are about *how to make choices that fit an agent-collaborative codebase*,
  independent of any domain.
- **Part B — Project Reference.** Everything project-specific: conversation conventions, the numbered
  development rules (cited by number across the codebase), CLI commands, deploy, architecture, library
  discipline, testing, and the orchestrator / agent-launch machinery.

**Reading order:** Part A is the durable, portable front-matter (Tier-1 read for orchestrators + code
agents). Part B is the reference you consult per-task.

---

# Part A — Davis AI-First Engineering Method

**Copyright © 2026 James C. Davis, PhD (davisjam@purdue.edu).**
*Licensed under the MIT License — free to use, modify, and redistribute
(including commercially), provided this copyright and permission notice are
retained. Full terms in the LICENSE file distributed with this catalogue.*

Portable principles for AI-collaborative software engineering, carried
across the author's repos. They are about *how to make choices that fit
an agent-collaborative codebase*, independent of this project's domain.
Each principle below is the crisp statement + the WHY; the full treatise —
with worked examples, canonical commits, and anti-patterns — is
[`docs/dev/AI-FIRST-ENGINEERING.md`](docs/dev/AI-FIRST-ENGINEERING.md).
Where a principle is also enforced as a numbered rule, the Part B rule
number is cited; the rule text itself lives in Part B, unchanged.

## A.1. Autonomy — carry work through; surface only load-bearing decisions

When the user invites autonomy: make good judgments, don't round-trip on
every decision, carry agreed work through to a sensible stopping point, and
surface doubts at the end of a work block rather than at each step. **Rework
is cheaper than waiting.** Make calls inline when they're judgment ("which of
two reasonable shapes?"); surface the decision when it is genuinely
architectural and load-bearing ("should this whole subsystem be reshaped?").
**When uncertain about a load-bearing call — scope, a naming seam, a design
axis — ask the user; do NOT defer the call to a sub-agent.** A fuzzy brief
lets the agent silently answer a narrower question than intended. Autonomy
never lifts the quality gates — speed comes from fewer round-trips, not from
skipping checks. Full discipline: `docs/dev/AI-FIRST-ENGINEERING.md` §3 +
§4.12c.

## A.2. Implementation is cheap; architecture is expensive

Prefer the right design over the faster-but-compromised one. Implementation
is a one-time cost; compromised architecture compounds in maintenance,
agent-confusion, and drift. In an agent-collaborative codebase this asymmetry
is sharper than usual: a bad shape confuses every future agent that reads it,
and substantial refactoring is nearly free (dispatch an agent), so there is
almost never a reason to enshrine a compromise. Corollary: **substantial
refactoring is "free" and drives a recurring audit cadence** —
`docs/dev/AI-FIRST-ENGINEERING.md` §2 + §2.3.

## A.3. Hyper-experimentation — pilot, compare, measure; the prototypes throw away, the learning stays

Ground decisions in data, because in the agentic era data is cheap. Run pilot
studies before wider sweeps; surface 2–3 alternatives before picking; measure
rather than argue — a pilot beats a debate. The discipline that keeps this
from becoming flailing: experiments must be **falsifiable** and grounded in
**ground truth**, **negative results are wins** (a cheap pilot that kills a
bad path saved an expensive build), and you must be willing to be wrong and
**correct the record when the data contradicts you**. The prototype is
disposable; the learning it produces is what you keep. Full principle:
`docs/dev/AI-FIRST-ENGINEERING.md` §2.4.

## A.4. Types are how you name shapes; type-in-place before decomposing

Architecture is a structure of shapes; types are how you name them. Types
reveal architecture that primitive-passing leaves anonymous. When decomposing:
(1) annotate the types in-place; (2) let the types become the cross-module
contract; (3) THEN move the typed cluster. Don't decompose what you haven't
yet typed — the types reveal the seam. New Python lands strict-typed; new
frontend lands as TypeScript (Part B rule #24). Full principle:
`docs/dev/AI-FIRST-ENGINEERING.md` §2.5.

## A.5. Explicit models, states, and policies over implicit ones

Name the thing, encode it in types, write a test that walks the encoded
structure. State machines beat scattered counter increments; typed enums beat
magic strings; declared coverage tiers beat binary "covered" claims. Implicit
invariants are invisible to future auditors (human or agent) and rot silently
when surrounding code shifts. This is why job lifecycles use explicit
`JobStateMachine` transition tables rather than ad-hoc increments (Part B
"Architecture rules"). Full principle: `docs/dev/AI-FIRST-ENGINEERING.md` §2
+ §4.5.

## A.6. Unify for defect-class consolidation, not just capability

Fix-once-benefits-all is the load-bearing affordance — capability parity is
sufficient justification to unify two parallel implementations; you do not
need the merged path to be *more* capable. When two sites share logic, extract
a shared helper — **on the second site, not the third** (DRY-drift hazard).
When unification also unlocks new capability, split the commit: consolidation
(correctness) separate from capability (feature). Full principle:
`docs/dev/AI-FIRST-ENGINEERING.md` §2 + `docs/dev/CODE-STYLE.md` §3; Part B
rule #11.

## A.7. Update call sites; don't preserve legacy shims

When a refactor exposes a cleaner surface, migrate ALL call sites in the same
change. No delegating shim "for backwards compatibility" — compatibility shims
compound into a permanent two-paths tax that every future agent must reason
about. Full rationale: `docs/dev/AI-FIRST-ENGINEERING.md` §2.3.

## A.8. Enforce structure with the compiler / static analysis — do not defer

Author the lint or type-check *now*, even when it has zero findings today;
forward-policing IS the value. Code review is not a substitute for static
analysis. **Move audits to lints** whenever the signal is mechanically
detectable — audit signals are expensive, deferrable, and post-hoc; lint
signals are cheap, at-PR, and deterministic. Today's audit finding should
become tomorrow's lint: if a bug is in N>1 files, the right fix shape is "fix
N sites + add a lint," not "fix N sites and wait for the next audit." For a
class-level failure, propose a `[LINT]` in addition to the `[FIX]` (Part B
rule #23). Full discussion: `docs/dev/AI-FIRST-ENGINEERING.md` §4.2 + §4.11.

## A.9. Genre check before invent; single source of truth

Before proposing a new abstraction, schema, or tool: (1) what is the genre?
(2) who is the canonical best-in-class? (3) can we adopt their schema even if
we skip their runtime? **Adopt the schema even when the runtime is overkill**
— you inherit hard-won constraints at naming-convention cost. And prefer a
single source of truth wherever possible: a stable lint that reads meta-files
at lint-time beats codegen-from-spec beats N hand-rolled lints (each step
loses a drift hazard). Full principles: `docs/dev/AI-FIRST-ENGINEERING.md`
§4.3, §4.3a, §4.16; Part B rules #22, #33.

## A.10. Class-vs-module shape; extract on the second site

The decomposition default is a module of free functions only for *stateless*
clusters. For a state-bearing cluster (≥2 mutable module-private vars shared
across exported functions, a state machine, or a long-lived cache/handle),
extract a **class** — state wants an owner. And extract the shared helper on
the **second** site, not the third; two files with the same logic in one PR is
the extract-now signal. Full rule: `docs/dev/CODE-STYLE.md` §1a + §3; Part B
rules #11, #11a.

## A.11. Reason about second-order effects and dynamics

A first-order design ("when X happens, do Y") is often correct in isolation
but produces pathological dynamics under repetition, concurrency, or stale
state. Always walk through: what happens at tick T+1, T+10, T+100? What if N
components do this simultaneously? What if state drifts between dispatch and
consumption? For any new substrate with repetition, concurrency, or
time-delayed consumption, write an explicit "second-order dynamics" section in
the design doc. **Dynamics-aimed tests find the real defects** — distributed
bugs live in driving-conditions and cross-component dynamics, not in static
structure; a strong-but-static unit suite will miss them. Full principle +
worked examples: `docs/dev/AI-FIRST-ENGINEERING.md` §4.17; Part B rule #45.

## A.12. Quality gates — grade on the commodity-lint floor

Every commit should pass the project's standing gates (type-check, tests,
lint, behavior-identity smoke). Gates that catch defects at commit time
prevent ones that surface at review or production time, both of which cost the
user more attention than the gate cost the agent. **Grade the codebase on its
commodity-lint floor** (ruff / eslint / tsc / pyright / Roslyn analyzers), not
on the count of bespoke custom lints — the floor is what a fresh reader can
trust. **Dependency manifests must be complete (SBOM discipline):** every
third-party package the code or the gates use MUST be declared in the matching
manifest, and any out-of-band `pip install` / `npm install` an agent runs MUST
be persisted in the same change — an undeclared tool is invisible to SBOM
retrieval and breaks a fresh checkout's gates. Full discussion:
`docs/dev/AI-FIRST-ENGINEERING.md` §4.13; `docs/dev/DEPENDENCIES.md`.

## A.13. Regex policy — parser-first

Regex is acceptable for genuinely simple string matching (literal patterns,
fixed prefixes/suffixes, enum values). For anything that parses semantic
structure, reach for the real parser / walker — PDF content streams, JSON from
LLM output, C# source, and Office/PDF tree traversal each have a canonical
parser (see Part B "Library and dependency discipline"). Catastrophic
backtracking and "regex that was subtly wrong for months" are the motivators.
Full audit: `docs/design/regex-usage-audit-260425.md`.

## A.14. Never silent-catch

Every `except` / `catch` must log, re-throw, convert to a domain error, OR
carry an inline comment justifying the swallow. A silent catch turns a
fail-loud bug into a fail-quiet one — the worst failure mode for a pipeline
where "ran successfully but produced garbage" is invisible. This composes with
the **fail-fast / GenAI-first** posture: when a dependency is unreachable,
fail loudly rather than degrade silently. Full rule + examples:
`docs/dev/CODE-STYLE.md` §4; Part B rule #8.

## A.15. Comments and commits earn their place

**Comments** default to none; a comment justifies its existence by explaining
*why* (a non-obvious invariant, a chosen trade-off, a footgun), not by
restating *what* the code does. **Commits** land in reasonable, self-contained
sets with messages that state the intent; agents commit per meaningful step
(never accumulate) and carry the co-author trailer. Full rule:
`docs/dev/CODE-STYLE.md` §2; Part B rule #13. Commit trailer:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

## A.16. Verify factual claims; trust nothing stale

A 30-second `grep` / `wc` / `ls` before quoting a number, a filename, or a
schema fact prevents stale-claim drift — verify brief premises before
dispatching. When reviewing "done" work, **trust nothing at HEAD**: re-run the
gates, pin-tests, and lints yourself; markers and counts rot when sibling
sweeps break the substrate. Agent reports describe *intent*, not *reality* —
verify. This is the load-bearing discipline of the Final Opus DoD review. Full
principle: `docs/dev/AI-FIRST-ENGINEERING.md` §4.9; Part B "Final Opus DoD
discipline."

## A.17. Destructive-op care

`rm -rf`, overwrite-in-place, force-push, history rewrite: in-repo / scratch
(`/tmp`) is fine without asking; anything outside the repo working tree gets an
explicit ask first, **every time**. Always look before deleting — never remove
a path you did not create or whose contents contradict how it was described.
Destructive `git` on `main` (`reset --hard`, reset to older refs, force-push)
requires explicit user approval — the orchestrator's inline shell has no
worktree backstop, so a flailing reset destroys work permanently. Undo a
landed commit with `revert`, never `reset`. Full rule: Part B rules #21, #36.

## A.18. Documentation — the invariants-driven pattern

Subsystem / architecture docs (the `docs/arch/` arch-vN family) earn their
keep through four load-bearing elements; a doc without them is prose that rots:
(1) **a section per real part** — one section/row per source, stage, module,
or entity, mirroring the actual structure; (2) **invariants with stable IDs** —
each invariant a tagged, testable predicate with a `file:line` cite, and the
ID is the join key that tests and audits cite; (3) **as-built vs design,
⚠️-marked** — call out where code diverges from design, because the ⚠️ gaps are
where the next work is; (4) **enforcement: invariants → tests** — map each
invariant ID to the test that pins it, or mark it UNTESTED, so the doc *drives*
the test backlog. Design docs encode invariants, not just rationale. Full
principle: `docs/dev/AI-FIRST-ENGINEERING.md` §4.5; `docs/arch/DESIGN.md`.

## A.19. Uniformity over fit — one codebase-wide pattern beats a locally-better bespoke one

Prefer a single consistent approach applied everywhere over a cleverer solution
tuned to one site. In an agent-fleet codebase this trades a small local-optimum
loss for a large system-wide win: a uniform pattern an agent has already seen
200× is applied correctly on reflex, while a bespoke one — however elegant — must
be re-derived from scratch by every future agent that meets it, and each
re-derivation is a chance to get it subtly wrong. Uniformity lowers
agent-confusion and defect *variance* more than local optimization raises
capability. This is the principle behind the canonical-lib mandate, the
sole-seam discipline, and the one-canonical-walker rule (Part B "Library and
dependency discipline"; rules #15, #16, #52): the win is not that iText or
`PdfModel` is the best conceivable tool, but that there is exactly *one* of them,
so a fix or a constraint applied once holds everywhere. Deviate only when a site
has a genuine, named reason the uniform pattern cannot serve — not merely because
a bespoke shape would be marginally nicer here. Full principle:
`docs/dev/AI-FIRST-ENGINEERING.md` §2.

## A.20. Essence vs. accident — attack accidental complexity; budget for essential

Brooks' distinction in "No Silver Bullet" is the sharpest triage tool we have.
*Essential* complexity is inherent to the problem — accessibility remediation
across PPTX / DOCX / XLSX / PDF, each with its own tag model, reading-order
semantics, and conformance spec, genuinely *is* hard, and no tool erases that.
*Accidental* complexity is the complexity our own tooling and choices introduce:
parallel implementations, primitive-passing that hides shapes, hand-built argv,
scattered state, drift between a doc and the code it describes. Spend effort
attacking the accidental kind — that is the complexity our substrate keeps
removing (unification for defect-class consolidation, typed seams, single
sources of truth), and every removal is a permanent reduction. Accept and
*budget* for the essential kind rather than pretending a cleverer abstraction
will make it vanish; mis-labeling essential complexity as accidental produces
leaky abstractions that cost more than the complexity they hid. The test before
any big refactor: is this reducing accidental complexity, or just relocating
essential complexity behind a prettier name? Full principle:
`docs/dev/AI-FIRST-ENGINEERING.md` §2.

## A.21. Governance as a method — three complementary control targets

Governance is not one thing. A **control** is a discrete, named artifact that
fires on a violation — a lint, a quality gate, a validator, a regression /
property / fuzz test, a conformance check, an observability assertion — and its
organizing move is always the same: *convert a recurring failure into a control
rather than re-inspect for it*, so a failure caught once is enforced on every
subsequent agent without re-inspection. What makes governance a *method* rather
than a pile of checks is that every control governs one of **three complementary
targets**, and a mature system covers all three:

- **(a) Agent** — the fleet and the substrate that *produces* work: briefs and
  brief-linting, role-typed dispatch, worktree isolation, the pre-commit /
  sentinel / merge-train / staged-deploy gate staircase, host-compute mediators,
  lifecycle + observability (agent-registry, event bus, tombstones, the
  cron-alerts gate), and governance-doc controls (this rule index and its
  cap/conformance lints, the mandatory-snippet table, the Epic DoD).
- **(b) Models-bridge** — the typed MBSE models the fleet reasons *through* and
  the codebase is generated / governed *from*: the component & zone model, the
  synchronization / mediator contracts, the service-flow model, the deployment
  topology, the domain registries — plus the drift / parity gates and query
  surface over them. This is the interface through which a context-*bounded*
  agent operates a context-*exceeding* codebase; meta-sync keeps the map equal to
  the territory, or the bridge would lie.
- **(c) Product** — the shipped artifact: the canonical typed models & sole seams
  (held in place by ban-lints on the raw alternative), content-fidelity
  validation and the WCAG / conformance rule engine, the regression-test onion,
  provenance & attribution (per-mutator stamps, the F10 wiring lint, the `a11y_`
  prefix), and the bounded repair vocabulary (closed remediation-verb sets, typed
  violation categories).

Each target is governed the same way — as a design pattern that holds the *cost
of a failure within bounds* — and the axis that most clarifies any single control
is soft (probabilistic — aims an agent, cannot block) vs. hard (deterministic —
holds the line regardless of agent cooperation); guidance *aims*, machinery
*holds*. The worked census — every control by role, family, form, novelty, and
enforcement — is the governance catalog (`talks-and-notes/governance-catalog/`
README + INDEX). Full principle: `docs/dev/AI-FIRST-ENGINEERING.md` §4.

## A.22. Right-size the fix — architecture-first, defense-in-depth, neither over- nor under-engineered

Every fix is bounded by two symmetric failures: **over-engineering** (a sweeping
redesign for a one-off) and **under-engineering** (a hacky patch over a structural
flaw). Aim for the middle — close the structural issue with the smallest sound
change, and when a larger scheme is genuinely warranted, *float it as an option*
rather than reflexively building it: offer both the local fix and the elaborate one,
bias toward the local, and let the cost of the failure justify the elaborate. Prefer
**architecture** (make the error impossible by construction) over a **control** (catch
it after the fact) as the first reach; where prevention isn't possible, add the
control; where a failure is costly, do **both** — belt-and-suspenders defense-in-depth
is a feature, not redundancy. The test before any fix: is it proportionate to the
failure it prevents, and does it close the *class* or merely the instance? Full
discussion: `docs/dev/AI-FIRST-ENGINEERING.md` §2 + §4.

*Attribution: Part A distills principles from the author's <Project> and
tenure-packet-generator repos; it is a portable method, reusable across
projects, governed by the copyright notice at the head of Part A. The full,
canonical treatise for <Project> lives at
[`docs/dev/AI-FIRST-ENGINEERING.md`](docs/dev/AI-FIRST-ENGINEERING.md).*

---

# Part B — Project Reference

Everything project-specific to <Project>. **The numbered rules below (`#1–#52`,
including sub-rules `11a`, `29a`) are cited by number across the codebase —
their numbers and text are immutable. Rule numbers are stable, not sequential;
new rules are appended, never renumbered (a few out-of-order pairs reflect
insertion history).**

## Conversation conventions

The user prefixes messages with a mode tag:

- **`S:`** — Synchronous discussion. Respond conversationally, don't
  launch agents or do heavy work unless asked.
- **`A:`** or **`Agents:`** — Asynchronous task. Dispatch the heavy
  work (long test suites, multi-file refactors, builds, anything >2
  min wall-clock) to one or more worktree agents. **Inline reads,
  greps, `git` commands, brief-drafting, cherry-picks, and parent
  coordination stay in the main thread** — they sharpen the brief
  and don't burn wall-clock. The failure mode is running a full
  test suite or doing a multi-file refactor inline; not dispatching
  at all is also a failure. Bundling several related findings into
  one agent is fine; splitting is also fine.
- **`SR:` or `R:`** — Status report request. Give a concise summary of
  all in-flight work, recent completions, and blockers.

When the user says "fire up an agent" or "queue this", treat it as `A:`.
When the user asks "how's it going" or "status", treat it as `SR:`.

**Epic status report shape** (user-ratified 2026-06-01): when the user asks
"show me Epic status" or "status of all open Epics," deliver a per-Epic
table with these four columns: **codename | description + value-add for
product | Opus-or-Sonnet gated | estimated remaining dispatches**.
Group by bucket (active / near-term / long-term / held). Full discipline
+ per-column rules: `docs/dev/AGENT-ORCHESTRATION.md` §"Epic status report
— canonical shape."

**Surfacing Phase-1-design questions to user for ratification** (user-ratified 2026-06-18): when an Opus Phase-1 design returns with §G open Qs, surface them in the canonical 5-field framing per question, preceded by an Epic-codename + 1-3 paragraph design-summary briefing. Full template + anti-patterns: [`docs/dev/orchestrator-surfacing-design-questions.md`](docs/dev/orchestrator-surfacing-design-questions.md).
**Immediate-dispatch + triage cadence** (2026-06-19): ≤10 LoC + single-file + no design judgment → IMMEDIATE-DISPATCH; otherwise backlog Epic. Decision tree: [`docs/dev/backlog-epic-triage-cadence.md`](docs/dev/backlog-epic-triage-cadence.md).
**Work-item tags in todos and follow-up queues.** Categorize every
pending work item with one of the five tags below so future-self
(human or agent) can tell at a glance whether the item adds structural
defense, patches a specific site, requires architectural thinking,
verifies a claim, or improves the workflow. Mixed-category items get
two tags joined with `+` or `→` (e.g. `[AUDIT]→[FIX]` if a verification
gates a downstream fix). If every item ends up multi-tagged, the
categories aren't earning their keep — split the work into discrete
items instead.

- **[LINT]** `tag-definition` — produces a new lint or extends an existing one. Structural
  defense; prevents re-introduction of the class.
- **[FIX]** `tag-definition` — one-off code change to a specific site. No new enforcement;
  the next instance of the same anti-pattern stays catch-only-by-audit
  unless paired with a `[LINT]`.
- **[DESIGN]** `tag-definition` — design doc or architectural decision. Often gates later
  `[LINT]` / `[FIX]` items but produces no code itself.
- **[AUDIT]** `tag-definition` — verification, investigation, empirical check, or
  reconciliation between conflicting findings. No fix; surfaces facts.
- **[PROCESS]** `tag-definition` — workflow / discipline improvement (e.g., verify briefs
  against design docs before dispatch, refine the cherry-pick protocol).

Apply the same tags to resume-plan checklists. The point is to make the
"lint will prevent re-introduction" vs "we patched one site" distinction
legible without re-deriving it on every read. **`[TAG]` is the ACTION axis; the
orthogonal DOMAIN axis (infra/controls/product/pre-epic/other) is the backlog
router's key** -- boyscout follow-ups emit a `<!-- followup-domain: <D> -->`
guess beside the `[TAG]` (a lint/gate is always `controls`). Design:
[`backlog-taxonomy-domain-based-260627`](docs/design/backlog-taxonomy-domain-based-260627.md).

**Always use `file://` absolute URLs when referencing local HTML / PDF /
image artifacts the user is meant to open** (mockups, generated reports,
screenshots, design-doc HTML, etc.). The VSCode extension renders
`file:///path/to/your-repo/...` links as clickable; relative
markdown paths render broken or open in a code pane, not the browser/preview
pane the user wants. Repo-relative `[name](path/to/file.html)` is right for
*source code* references; `file://` for *artifacts to view* (when in doubt, `file://`).

**"Quiesce" / "save and stop"** — the parent relays via `SendMessage` to every
in-flight agent. The agent must stop new work, commit whatever is in-flight (even
partial) with a verbose hand-off log, and exit cleanly — do not arm a monitor or
iterate. Full 4-step protocol: `docs/dev/AGENT-ORCHESTRATION.md` §"Quiesce protocol".

**When uncertain, ask the user for judgment — do not defer the call to
a sub-agent** (260518 font-WALK-vs-EMBED seam incident). (→ A.1.)

## Before making changes

1. Read `docs/arch/DESIGN.md` to understand the current architecture.
2. Check existing tests for the area you're changing:
   - Pre-deploy (.NET): `backend/test/<Project>.Cli.Tests/`
   - E2e: `test/e2e/e2e-test.mjs`

## When making changes

> **Rule numbers are stable, not sequential** — cited by number across the codebase, so
> new rules are appended, never renumbered (a few out-of-order pairs reflect insertion
> history). Next unused: #53.

1. **Update docs** — update `docs/arch/DESIGN.md` or the relevant sub-file in
   `docs/design/` if you change architecture, add services, or modify
   how components communicate.

2. **Add or update tests** — pre-deploy (.NET) tests for internal logic,
   e2e tests for user-visible behavior. See `docs/dev/TESTING.md`.

3. **Add timing/diagnostic logs** to new server or worker code paths.
   - Python: `log.info("v%s ...", VERSION, ...)`
   - C#: `logger.Log(2, "...")` — never use `Console.WriteLine` for
     diagnostics. `SimpleLogger` is the only diagnostic channel.

6. **Tool/script log and output file naming:** Any tool or script that
   writes output files or log files to disk MUST embed a `YYMMDD.HHMMSS`
   timestamp in the filename (e.g., `bench-260423.143015.log`,
   `grid-report-260423.143015.md`). Without timestamps, successive runs
   silently overwrite earlier results. Apply this to `tools/` scripts,
   `deploy/` scripts, and any new C# or Python diagnostic writers.

4. **Prefer config system over env vars.** Runtime-toggleable settings
   should go through the config system (`POST /api/admin/config` →
   `_CONFIGURABLE_ATTRS` in `server.py`, or `AltTextGenerationConfig`
   in C#), not raw `os.environ` / `Environment.GetEnvironmentVariable`.
   Env vars require redeployment; config overrides are instant.

5. **Config field discipline:** Every new field in `AltTextGenerationConfig` (or
   any JSON-deserialized config record) MUST also appear in `assets/genai-config.sample.json`.
   `System.Text.Json` uses CLR defaults (`false`/`0`/`null`) for missing fields —
   a missing batch-size field silently collapses batching to single-call in prod.
   Enforced by `ConfigDeserialization_AllBoolFieldsExplicit` and
   `ConfigDeserialization_AllBatchSizeFieldsExplicit`.

7. **GenAI batch-size + `validateAltText` fields are hot-configurable via
   `POST /api/admin/config`.** Don't re-bake them via env vars or redeploys.
   See `docs/genai/genai-config-hot-overrides.md`.

8. **Never silent-catch.** Every `catch` must log / re-throw / convert to a domain exception, OR carry an inline comment justifying the swallow. (→ A.14.) `docs/dev/CODE-STYLE.md` §4.

9. **Banned APIs in production code.** `tools/lint/lint-banned-apis.py` (runs on every deploy) is the source of truth — `BANS` table has rationale, scope, pattern. Add new bans there, not here. Escape: `# noqa: <ban-name> — <reason>` (Python) / `// noqa: <ban-name> — <reason>` (C#).

10. **`a11y_` prefix convention for inserted artifacts.** Invisible-to-author
    insertions MUST start with `a11y_`; user-visible insertions MUST NOT;
    spec-mandated names keep their spec name. Policy + per-site corollaries:
    `docs/design/inserted-content-placement-audit-260425.md` §"a11y_ prefix convention".

11. **DRY-drift hazard: extract on the second site, not the third.** (→ A.10.) Full rule + incidents: `docs/dev/CODE-STYLE.md` §3.

11a. **Class-vs-module shape: prefer class when state exists** (≥2 mutable module-private vars / SM / long-lived cache-handle → class). (→ A.10.) Full rule + per-language form: `docs/dev/CODE-STYLE.md` §1a.

13. **Comments earn their place by doing one of three jobs; default to no comment.** (→ A.15.) See `docs/dev/CODE-STYLE.md` §2 for the rule + DELETE/KEEP patterns + canonical motivating commits (`f7b30e4a` + `0dd2ca73`).

12. **`Console.SetOut`/`Console.SetError` are process-wide singletons — use `TextWriter` DI instead.** Accept `TextWriter` as a constructor parameter; tests inject a per-test `StringWriter`. Lint: `console-singleton-mutation` (BANS rationale in `tools/lint/lint-banned-apis.py`).

14. **Python subprocess scripts signal status via exit codes, not magic stdout strings.** Convention: `0` = success, `1` = runtime error, `2` = missing dependency. Full rationale + script template: `docs/dev/LIBRARY-GUIDE.md` §"Python subprocess error semantics — exit-code convention".

15. **All PDF I/O goes through `PdfModel`** (→ A.19). Read via `PdfModel.Read(path)`; write via typed mutators in `<Project>.PdfModel/Primitives/`. Banned: raw iText constructors, `tagPointer.AddTag`, `dict.Put`, `structRoot.AddKid`. Lint: `itext-direct-access` + `helpers-no-itext`. Primer: `docs/pdf/pdf-architecture-and-pdfmodel.md`.

16. **Office analogue of rule #15: Office remediation goes through the Office Model (`<Project>.{Slides,Docs,Sheets}Model/`, `<Project>.OpenXmlCommon/`), not raw `DocumentFormat.OpenXml.*`** (→ A.19). Same applies to `<Project>.Checking/` — route through `RuleWalkers/`. Lint: `openxml-direct-access` + `no-raw-xml-string-match`. Primer: `docs/arch/masked-pass-architecture.md`. Migration plan: `docs/office/office-model-material-inventory.md`.

17. **Served-page smoke gates: post-condition, not pre-condition.** Every served HTML page must register a smoke phase asserting NO fallback strings appear AND at least one expected content shape is present; the fallback-string set is a **closed, monotonically-growing tuple** (→ A.5). Full rule + per-fixture detail: `docs/dev/TESTING.md` §2.5 and `docs/design/examples-served-page-smoke-gate-260512.md`.

18. **Fuzz-exposed bugs: RCA to the stable point in the format spec, not
    to the producer variation.** Fix to the stable spec point so the fix passes
    every spec-allowed input, not just the failing seed. Full discipline:
    `docs/tests/fuzz-rca-discipline.md`.

19. **`*.ResetForTesting()` calls from test code are banned.** Process-wide static mutation races with concurrent tests. Alternative: AsyncLocal-scoped `UseScope()` (see `RealGenAiClientGuard.UseScope()` as reference). Lint: `no-test-reset-for-testing` (BANS rationale in `lint-banned-apis.py`).

20. **Logging discipline: see `docs/dev/LOGGING.md`** for the canonical cross-language reference (C# `SimpleLogger` + `DebugTrace`; Python `log = logging.getLogger(...)`; JS `window.<project>.log`). RCA-class work: use `DebugTrace.Emit` with typed topic constants; ponder keep-vs-remove after investigation (§"RCA Discipline").

21. **Destructive filesystem ops — in-repo/scratch OK, outside ASK FIRST.** (→ A.17.) Irreversible mutations (`rm`, overwrite, `mv`-over-existing) run WITHOUT asking ONLY when every target path is under the repo working tree (`/path/to/your-repo/**`), `/tmp/**`, or the project memory dir. For ANY target outside that set — `$HOME`, system paths, other repos, `~/.claude/**` beyond the project memory dir — **STOP and ask first**, every time. `bypassPermissions` is in effect; this rule is the only seatbelt.

22. **Genre check before invent** — identify genre + canonical best-in-class + adopt-their-schema option before proposing a new abstraction/schema/tool. (→ A.9.) Full rule + example: `docs/dev/AI-FIRST-ENGINEERING.md` §4.3a.

23. **Class-level failures get [LINT] proposals, not just [FIX]es** (OTHER files likely share the bug → `[FIX]+[LINT]`; one-offs don't; default: propose). (→ A.8.) Full discipline: `docs/dev/TESTING.md` §"Lints — quality-gate discipline". Snippet: `docs/agent-snippets/lint-first-for-class-issues.md`.

24. **New code lands typed.** New Python files land in both `[tool.pyright].include`
    AND `[tool.pyright].strict` (gated by `tools/lint/lint-pyright-gate.py`).
    New frontend code lands as TypeScript (`.ts` under `web/static/spa/`,
    `web/static/editor/`, etc.). `.ts` is canonical; tsc emits a sibling `.js`
    delivery artifact that is **gitignored** (NOT committed) and rebuilt in-image —
    do not track it. Rare exception: a `.js` needed at type-resolution time by a
    cross-tree build stage stays tracked + documented in `.gitignore` (e.g.
    `web/static/spa/backend-mirror.js`).
    Drift defense: pyright-gate enforces Python; `lint-ts-checkjs.py` +
    `lint-ts-js-artifact-fresh.py` enforce TS.

25. **New lints declare `COMPONENT_TAGS` + docstring.** Every lint MUST declare
    (in order after `from __future__ import annotations`): `COMPONENT_TAGS`,
    `SEVERITY`, and a verb-of-checking docstring — all three BLOCKING (enforced by
    `lint-component-tags-declared.py`). Class D lints also declare `CONSUMES_REGISTRIES`;
    Class E lints declare `EXEMPT` (mutually exclusive with D). `main()` returns
    `1 if count else 0`. Full spec: `docs/design/lint-component-scoped-modes-260523.md` §2-§3;
    EXEMPT: `docs/design/lint-exempt-field-260610.md`.

26. **Install-class operations belong only in setup/bootstrap contexts — not in
    deploy phases, lint scripts, test helpers, or service code.** (`npm install`,
    `pip install`, etc. outside setup creates parallel-phase package-manager races.)
    Approved contexts: `setup.py`, `tools/dev/install_dev_deps.py`,
    `tools/fuzz/*/setup.py`, `deploy/Dockerfile.*`, `services/*/Dockerfile`.
    Escape: `# noqa: no-installs-outside-setup — <justification>`.
    Lint: `lint-no-installs-outside-setup.py` (NON-BLOCKING during migration).
    Full rule: `docs/ops/setup-phase-discipline.md`.

27. **No shell scripts.** `*.sh`, bash/sh shebang, `subprocess.run(..., shell=True)`,
    `os.system(...)` banned codebase-wide — use Python instead. Approved exemptions:
    vendored scripts (`services/*/vendor/`), `setup.sh` per
    `docs/design/no-shell-policy-260526.md`. Escape: `# noqa: no-shell-scripts —
    <justification ≥ 8 chars>`. Lint: `lint-no-shell-scripts.py` (AUDIT-ONLY
    during migration; BLOCKING after Phase 4). Policy: `docs/dev/DEVELOP.md` §"No shell".

28. **Codemod-first for large mechanical lint backlogs.** For N ≳ 50 findings with a
    deterministic fix shape, **author an AST-level transformer** — don't dispatch N
    Sonnets. Use Sonnet-by-Sonnet only when each site requires per-site judgment.
    Full discipline + genre cues + when-Sonnet-still-wins:
    `docs/dev/AI-FIRST-ENGINEERING.md` §4.14.

29. **Agent CWD-drift defense — `isolation: "worktree"` in the brief is BLOCKING.** Every code-writing brief MUST carry `isolation: "worktree"` (lint-verified by `agent_prompt_lint.py`); the orchestrator MUST call `dispatch_agent.prepare()` and embed `dispatch-id: agent-<id>` (check #9 verifies the token AND that `.claude/active-agents/agent-<id>.json` exists at lint-time). Bypass: `<PROJECT>_BYPASS_AGENT_FENCE=1`. Full design: `docs/design/agent-cwd-drift-defense-260527.md` + `docs/design/dispatch-wrapper-convention-to-required-260528.md`.

29a. **Agent() call discipline — orchestrator-side companion to #29.** The orchestrator's `Agent({...})` invocation MUST ALSO include `isolation: "worktree"` (the harness only creates the worktree when the param is present at the call site), and MUST instruct the agent to discover its worktree via `$(pwd)` — NEVER prescribe `.claude/worktrees/agent-<dispatch-id>/` (SBL-8: harness allocates a different worktree-id than the dispatch-id). Exception: `--role commit-slave` operates on main directly — MUST omit `isolation`. Field note: `docs/field-notes/worktree-isolation-r2-260607.md`; pin test `tools/agents/test_dispatch_isolation_field.py`; SBL-8: `docs/design/dispatch-vs-runtime-worktree-arch-260529.md` §5.2.

30. **No inline imports — declare every dependency at module scope.** Deferring an import into a function body is an ERROR (user directive 260625): module-scope imports make the dep set knowable for auto-derived docker images; boot-time fail-loud beats request-time fail-quiet. Runtime-only deps absent from the dev venv go in a module-top `try/except ImportError` that fails-loud-in-prod. BANNED hoist markers + transitional circular-guard markers + enforcers (`lint-no-inline-imports-in-functions.py`, `lint-prod-dep-import-fail-loud.py`, `lint-lazy-load-justified.py`, codemod `hoist_inline_imports.py`): [`docs/design/no-inline-imports-drain-260625.md`](docs/design/no-inline-imports-drain-260625.md).
31. **Codemod-class commits may opt out of pre-commit checks with `# pre-commit-skip: <reason>` in the commit body.** Reserved for rule-#28 codemod-first waves (marker MUST carry a `<reason>` token); `--no-verify` is BANNED (skips CWD-drift fences). Lint stanza skipped; unit-tier still runs. Agent briefs MUST include `docs/agent-snippets/codemod-skip-precommit.md`. Unit-tier bypass + LIFT-#11 per-check kill switch (`<PROJECT>_SKIP_PRECOMMIT_CHECKS`, humans only) + audit log: `docs/design/pre-commit-unit-tier-tests-260602.md`.

32. **Tools we build do their work AND report on plans/results clearly enough for agents to spot behavior problems.** Every agent-callable tool MUST emit (a) a planned-actions preamble before execution ("Deploy Plan" / dry-run / DAG) AND (b) measurable results after execution (durations, counts, exit-record signaling) in a mechanically parseable format. (→ A.21.) Full discipline + canonical incident (260528 lint-no-shell-scripts 73.9s blind spot): `docs/dev/AI-FIRST-ENGINEERING.md` §4.15.

33. **Prefer stable-lint-reads-meta-files over codegen over hand-rolled.** For N invariants across N meta-files: (a) BEST — one stable lint reads meta-files at lint-time; (b) MIDDLE — codegen from shared spec; (c) WORST — N hand-rolled lints. (→ A.9.) Full discipline: `docs/dev/AI-FIRST-ENGINEERING.md` §4.16.

35. **Auto-generated files must carry a provenance header — hand-edits will be overwritten.**
    Any git-tracked file emitted by a tool MUST carry a comment in its first 5 non-blank
    lines declaring the emitter and regen discipline path. The emitter MUST re-emit the
    marker on every regen run. Register new auto-gen targets in `_AUTOGEN_TARGETS` in
    `tools/lint/lint-autogen-files-have-provenance-header.py`.
    Lint: `lint-autogen-files-have-provenance-header.py` (BLOCKING).

34. **Do not launch deploy when it will predictably fail — lints green, flaky-tests killed.**
    Before dispatching ANY deploy attempt, confirm: (a) all BLOCKING lints exit 0;
    (b) no known flaky test class surfaced since last green
    (`docs/design/flake-inventory-and-elimination-plan-260531.md`); (c) `lint-all.py
    --changed-since main` exits 0. Speculative deploys (verifying "did substrate-X heal
    the failing phase") are OK — document the speculation in the brief's Headline.
    Telemetry: `lint-all.py` mutex bypass writes to `.claude/lint-all-mutex-overrides.jsonl`.

36. **Destructive `git` on `main` from the orchestrator's inline shell requires explicit user approval, every time.** (→ A.17.) Banned without per-op approval: `git reset --hard`, reset to older refs, `git push --force` to main, `git cherry-pick --abort` on a partly-landed chain. Reflexes: undo landed cherry-pick → `git revert <sha>` (never `git reset`); escape in-progress cherry-pick → `git cherry-pick --quit`. Canonical cherry-pick: `tools/agents/auto_cherrypick.py apply` (enforces `--quit`; C6 gate refuses bare `git cherry-pick`). Snippet `docs/agent-snippets/cherrypick-via-auto-tool.md`; field note `docs/field-notes/destructive-git-on-main-260603.md`; design `docs/design/auto-cherrypick-method-260604.md` §3.

37. **Orchestrator does not run `git commit` or `git cherry-pick` directly on main.** Dispatch a commit-slave Sonnet for every commit via `tools/agents/dispatch.py --role commit-slave` (operates on main directly — NOT `isolation: worktree` — via `agent_commit.py --of 1/1` so the hook fires). Bypass-prefix subjects (`sentinel:`/`tombstone:`/`chore(worktree):`/`quiesce:`) may commit inline; undo a landed commit via `git revert` (never `git reset`). Break-glass `<PROJECT>_BYPASS_ORCHESTRATOR_CHECK=1` (audit-logged). Workflow: [`docs/dev/orchestrator-commit-delegation.md`](docs/dev/orchestrator-commit-delegation.md); snippet [`docs/agent-snippets/role-commit-slave.md`](docs/agent-snippets/role-commit-slave.md).

38. **Orchestrator MUST close Epics via `tools/dev/epic_close.py close --commits <sha-list>`
    or `--override '<reason>'`; inline `**Status:**` line edit for closure is BANNED.**
    The tool enforces: (a) every commit reachable from main via ancestry OR patch-id match;
    (b) missing commits require `--override '<reason ≥30 chars>'` logged to
    `.claude/epic-close-overrides.jsonl`; (c) Status + Closed: rewritten atomically,
    file moved to `docs/epics/closed/`, INDEX.md regenerated. Phase-completion notes
    still allowed inline or via `epic_close.py update-phase`.
    Field note: `docs/field-notes/epic-close-tool-mandate-c60-260603.md`.

39. **Mass-tombstone Sonnets MUST receive an explicit ID list — runtime
    enumeration of `.claude/worktrees/agent-*` is BANNED for tombstone
    targeting.** Substrate guard: `tombstone_commit.py` + `worktree.py clean`
    refuse to operate on any agent-id whose `.claude/active-agents/<id>.json`
    marker file exists. Override flags (audit-logged to
    `.claude/tombstone-overrides.jsonl` / `.claude/worktree-clean-overrides.jsonl`)
    reserved for verifiably stale markers. Every mass-tombstone brief MUST
    pass `--id-file <path>` — never `ls .claude/worktrees/agent-*`.
    Design: [`docs/epics/closed/mass-tombstone-live-worktree-guard-260603.md`](docs/epics/closed/mass-tombstone-live-worktree-guard-260603.md).

40. **Brief authoring declares `subagent_type` per *expected output shape*, not per work shape.** Every brief carries `<!-- subagent-type: <Plan|Explore|code-reviewer|general-purpose> -->`. Deciding axis: does the brief expect a file artifact? Produces a file (design/DoD/RCA/code/lint/snippet — anything mutating disk) → `general-purpose` (Plan agents are harness-READ-ONLY, so pick general-purpose even for read-heavy artifact briefs); inline analysis only → `Plan`; code-review of landed diffs → `code-reviewer`; pure search → `Explore`. Full corrected matrix (INVERTED 260614): `docs/agent-snippets/brief-subagent-shape.md`.

41. **Tombstone substrate — dedup-via-registry.**
    (a) **Dedup**: `tombstoning_started` event deduplicates concurrent tombstone procs (exits 78);
    bypass: `<PROJECT>_TOMBSTONE_FORCE=1` (audit-logged).
    (b) ~~**Tier A predicate** (REMOVED 260618 — `docs/epics/active/tier-a-removal-260618.md`)~~:
    inverted the validation hierarchy; removed entirely. Every tombstone
    now runs the full CI gate unless the human escape (`<PROJECT>_TOMBSTONE_CI_GATE_BYPASS`) is set.
    Forward-policing: `tools/lint/lint-no-tier-a-predicate-reintroduction.py` (BLOCKING).
    Design: [`docs/design/tombstone-dedup-via-registry-260609.md`](docs/design/tombstone-dedup-via-registry-260609.md).
    Telemetry: `.claude/agent-registry.jsonl`. Observability: [`event-bus-playbook`](docs/dev/event-bus-playbook.md) §Q9.

42. **Tests must look up substrate values, not hardcode them.** If a test value is expressible as a lookup against an in-repo source-of-truth (registry, enum, schema constant, typed set), the test MUST perform the lookup — never embed a snapshot copy. (→ A.5, A.16.) A mechanical forward-policing lint (C87, `lint-test-hardcodes-queryable-value.py`) was **assessed infeasible** (`docs/design/c87-c88-lint-feasibility-260702.md`) — the queryable-vs-legitimate signal is not deterministic; enforcement is this rule + Final-Opus-DoD audit + per-site structural bounds. Full discipline + worked examples: `docs/dev/TESTING.md` §"Tests must look up substrate values, not hardcode them".

44. **Aggregate compute discipline — one `lint-all` instance per host; one `lint-all`-triggering Agent in flight per orchestrator.** `lint-all.py` flocks `/tmp/<project>-lint-all-instance.lock` at entry (hard cap 1800s; bypass `<PROJECT>_LINT_ALL_NO_MUTEX=1`, audit-logged). Every code-writing brief declares `<!-- compute-class: lint-all-on-commit | lint-all-explicit | read-only -->`; only ONE `lint-all-on-commit`/`lint-all-explicit` brief in flight at a time. Merge-train staging fast-path + conflicting-signal defense + all host locks: [`docs/epics/closed/aggregate-compute-protection-260611.md`](docs/epics/closed/aggregate-compute-protection-260611.md) + [`docs/dev/dev-mediators.md`](docs/dev/dev-mediators.md) §"Synchronization & locks inventory". Observability: [`docs/dev/event-bus-playbook.md`](docs/dev/event-bus-playbook.md) §Q1+§Q2+§Q3.

43. **Infra-class substrate work earns a deterministic check at sentinel commit** — **land a check at sentinel that runs the substrate end-to-end against the actual brief** (constraint extractors, mediators, dispatch tools, hook stanzas, registries). (→ A.11, A.21.) AUDIT-ONLY initially → BLOCKING after 1 session of clean events. Full discipline: `docs/dev/AI-FIRST-ENGINEERING.md` §"Production-path validation at sentinel commit". Companion snippets: `assert-canonical-dispatch.md`, `dispatch-id-confirm.md`. Forward-policing: C88 (`lint-substrate-has-sentinel-check.py`) — **queued, NOT yet built**.

45. **When designing infrastructure, reason about second-order effects and dynamics.** For any new substrate with repetition, concurrency, or time-delayed consumption, write an explicit "second-order dynamics" section in the design doc. (→ A.11.) Canonical worked examples: [`docs/design/merge-train-bisect-attribution-and-fix-in-batch-260612.md`](docs/design/merge-train-bisect-attribution-and-fix-in-batch-260612.md) §4.8 (cron-retry) + §4.9 (stale-base).

46. **Substrates emitting event-bus topics own their observability end-to-end.** Every design doc introducing a new event-bus topic MUST carry a `## §N. Observability / event-bus` block (topics + baseline-healthy + what-looks-wrong + target playbook entry); missing [`docs/dev/event-bus-playbook.md`](docs/dev/event-bus-playbook.md) §Q-N entry = incomplete substrate design. Lint: `lint-substrate-emits-have-playbook-entry.py` (AUDIT-ONLY → BLOCKING). Template + full doctrine: [`docs/dev/OBSERVABILITY.md`](docs/dev/OBSERVABILITY.md) §6.

47. **Orchestrator monitors cron + merge-train + tombstone substrate via event-bus.** Check at session-start + after cherry-pick waves (anomaly triggers: yields >3 in a row, `discard_lint`, `outcome=no_op` >30 min with tombstones queued). **Session start (MANDATORY):** read `.claude/cron-alerts.jsonl` for unconsumed alerts since `last_seen_ts`; surface proactively if severity ≥ MEDIUM. Full doctrine + how-to-check recipes: [`docs/dev/OBSERVABILITY.md`](docs/dev/OBSERVABILITY.md) §1+§7 + [`docs/dev/event-bus-playbook.md`](docs/dev/event-bus-playbook.md) §Q3/§Q5+. Alert-channel: [`docs/dev/cron-alerts-discipline.md`](docs/dev/cron-alerts-discipline.md) + [`docs/agent-snippets/cron-alerts-poll.md`](docs/agent-snippets/cron-alerts-poll.md). Cron-broken recovery (chicken-and-egg): [`docs/dev/cron-recovery-playbook.md`](docs/dev/cron-recovery-playbook.md).

48. **Unresolved HIGH-severity cron alerts BLOCK new orchestrator-side work-dispatch — ack or resolve first.** When `.claude/cron-alerts.jsonl` carries a HIGH alert whose latest `.claude/cron-alerts-acks.jsonl` row is NOT `ACK`/`RESOLVE`/`BYPASS_AUDIT`, the gate refuses `dispatch.py` (new sonnet-active/opus), `worktree.py create`, `merge_train.py run|stage|attest`, and `brief-template.py new`. Canonical resolution: `dispatch.py --resolves-alert <id> <brief>` (auto-acks + dispatches fix). Gate status: BLOCKING. EXEMPT tools + full resolution paths + deadlock-freedom: `docs/design/cron-orchestrator-comms-substrate-260615.md` §8.4; recovery: `docs/dev/cron-alerts-gate-recovery-playbook.md`; producer: `docs/dev/cron-alerts-discipline.md`; observability: `docs/dev/event-bus-playbook.md` §Q17.

49. **Never end a turn by arming a Monitor — commit synchronously.** The
    "I'll arm a Monitor and finish" pattern is the single most common stub-
    completion failure: the parent reads your final output + commits, NOT your
    monitor, so a turn ending with an unfired monitor lands ZERO work. If you
    need to wait on a long process, run it synchronously (Bash + timeout, or
    `await_baseline_output.py`), then `git commit` AS YOUR LAST ACTION. Full
    discipline + incident log: `docs/agent-snippets/worktree-path.md`
    §"The 'I'll arm a Monitor and finish' trap" + `commit-cadence.md`.

50. **MIS-aware composition for cron throughput.** Cron's merge_train.py batches
    NON-CONFLICTING worktrees per tick (Maximum Independent Set). To maximize
    pool→cron throughput, dispatch waves with DISJOINT file footprints. Hot-spot
    files (merge_train.py, pyproject.toml, CLAUDE.md, .githooks/) become MIS
    bottlenecks — 8 concurrent agents touching the same file = MIS size 1.
    Full discipline + 8-pool recipe: [`docs/dev/work-scheduling.md`](docs/dev/work-scheduling.md).

51. **Doc-derived tests carry a pin-trailer; regenerate on cited-source edits.**
    Every DDT test file (`*_doc_derived.py`) MUST carry a `# DDT-audited:` +
    `# DDT-source:` + `# DDT-pins:` trailer block immediately after the module
    docstring (full schema: [`docs/design/ddt-pin-trailer-phase1-260618.md`](docs/design/ddt-pin-trailer-phase1-260618.md) §A).
    When you edit a Python source file (or docs file) that has a DDT test pinning
    it, regenerate the trailer via `python3 tools/dev/regen-ddt-trailer.py <test-file>`
    in the same commit. Lints: `lint-ddt-trailer-present.py` (BLOCKING after Phase 3
    stabilizes), `lint-ddt-trailer-fresh.py` (WARNING; never BLOCKING — staleness is
    informational). Snippet: `docs/agent-snippets/ddt-test-trailer.md`.

52. **Every external CLI is reached through its tool's typed invoker — never a hand-built argv** (→ A.19). Prod AND tools reach external command-line tools (`verapdf`, `pdftoppm`, `soffice`, `tesseract`, `<project>`) only via that tool's typed argv-builder; hand-built argv silently drops rules / fails / corrupts. Peer to #15/#16; per-tool sole-seam ban-lints enforce it. Table + detail: `docs/dev/LIBRARY-GUIDE.md` §"External-CLI argv discipline".

