<!-- Starter mirror of a real, mature CLAUDE.md — the portable engineering method (Part A) plus the
     SHAPE of a project rule index (Part B), with the source project's specific rules stripped out. This
     is a MENU: adopt the Part A principles as-is, then write your own Part B. Companion to the
     agent-governance-mechanisms catalogue — many principles map to a control writeup there. -->

# CLAUDE.md — <Project>

This is a **starter** — the governance half of a real, mature CLAUDE.md from an **agent-team-as-team**
codebase (most code is written by dispatched AI agents; the discipline below exists to make that safe at
scale). It's a menu: adopt the Part A principles as-is, then fill Part B with your own project rules.

This file has two parts:

- **Part A — Davis AI-First Engineering Method.** Portable principles for AI-collaborative engineering.
  Apply on every touch; they are about *how to make choices that fit an agent-collaborative codebase*,
  independent of any domain. Adopt these as-is.
- **Part B — Project Reference (write your own).** In the source project this is a stable, numbered index
  of project-specific rules plus the concrete reference (CLI, deploy, architecture, testing). None of it
  transfers — here Part B is stripped to its *shape* + the test for what earns a spot + one worked
  example. Fill it with your own rules.

**Reading order:** Part A is the durable, portable front-matter (Tier-1 read for orchestrators + code
agents). Part B is the reference you build up per-project.

---

# Part A — Davis AI-First Engineering Method

**Copyright © 2026 James C. Davis, PhD (davisjam@purdue.edu).**
*Licensed under the MIT License — free to use, modify, and redistribute
(including commercially), provided this copyright and permission notice are
retained. Full terms in the LICENSE file distributed with this catalogue.*

The portable **method** behind this catalogue: principles for AI-collaborative software engineering,
independent of any domain.

They map onto the governance view the catalogue teaches — every mechanism is either an **architecture**
that makes a failure impossible by construction, or a **control** that observes and guards against one it
can't prevent. The standard engineering playbook (types, tests, DRY, state machines, lints, docs) appears
here *as* those mechanisms, not re-taught.

Four groups:

- **[The governance view](#a1--the-governance-view) (A.1)** — frames the method.
- **[Architecture](#a2--architecture-make-the-failure-impossible-by-construction) (A.2)** and
  **[Controls](#a3--controls-observe-and-guard-what-you-cant-prevent) (A.3)** — the two mechanism kinds.
- **[Operating the method](#a4--operating-the-method) (A.4)** — the working discipline that wields them.

Each principle is the crisp statement + the WHY. Many are also enforced, in the source project, as a
numbered rule plus a lint or gate — adopt the principle, and wire your own enforcement.

## A.1 — The governance view

The frame the rest of the method hangs on: what governance is, how the standard playbook maps into it, and
how to choose and size mechanisms.

### A.1.1. Governance as a method — three complementary targets

Governance is not one thing. A governance **mechanism** is either an *architecture* that makes a failure
impossible by construction, or a *control* that fires on a violation — a lint, gate, validator, regression
/ property / fuzz test, conformance check, or observability assertion. Either way the organizing move is
the same: *convert a recurring failure into a mechanism rather than re-inspect for it*, so a failure
caught once is prevented on every later agent without re-inspection. What makes governance a *method*
rather than a pile of checks is that every mechanism governs one of **three complementary targets**, and a
mature system covers all three:

- **(a) Agent** — the fleet and the substrate that *produces* work. *e.g.* brief-linting, role-typed
  dispatch, the pre-commit → merge-train gate staircase, agent-registry + lifecycle observability.
- **(b) Models-bridge** — the typed models the fleet reasons *through* and governs the codebase *from*
  (a limited slice — config, docs, IPC contracts — is generated from them too). *e.g.* a component/zone
  model, a service-flow model, drift/parity gates. This is how a
  context-*bounded* agent operates a context-*exceeding* codebase — meta-sync keeps the map equal to the
  territory, or the bridge lies.
- **(c) Product** — the shipped artifact. *e.g.* canonical typed models held by ban-lints,
  content-fidelity validation, a regression-test onion, per-mutator provenance stamps, a bounded repair
  vocabulary.

Each target is governed the same way — as a design pattern that holds the *cost of a failure within
bounds*. The axis that most clarifies any single mechanism is **soft** (probabilistic — aims an agent,
can't block) vs. **hard** (deterministic — holds the line regardless of agent cooperation): guidance
*aims*, machinery *holds*.

The worked census — every mechanism by target, family, form, and enforcement, with a full writeup per
concept named above — is this catalogue: **https://davisjam.github.io/agent-governance-mechanisms/**

### A.1.2. Complement competence — map the playbook to the failures it governs

Assume the engineer — human or agent — already knows the craft: how to write a test, factor a module, cut
a duplication, pick a data structure. This method does not re-teach that playbook; it shows **how each
familiar practice fits the governance view** — as an *architecture* that makes a failure impossible or a
*control* that catches it. The value is the map from failure mode to mechanism, not the practice itself.
When a failure recurs, name the class and point to the mechanism that governs it; skip the lecture the
reader could give you. A few standing maps:

- **Flakiness** → nondeterminism (a race, shared state, real I/O behind a fake): a *control* —
  dynamics-aimed tests (→ A.3.4, A.2.10) — never a blanket retry.
- **Duplication that drifts** → an *architecture*: extract on the second site (→ A.2.5).
- **Tangled responsibility** → an *architecture*: decompose along the types (→ A.2.2, A.2.4).
- **Reinventing a solved problem** → reach for a canonical exemplar (→ A.2.8).
- **Silent degradation** → a *control*: never-silent-catch, fail loud (→ A.3.3).

The catalogue entries are this map at scale — each names the failure it kills and whether it *prevents*
(architecture) or *catches* (control). Add to the map when a failure *recurs*, not when a practice is
merely worth teaching.

### A.1.3. Right-size the fix — architecture-first, defense-in-depth

Over- and under-engineering are symmetric failures: a sweeping redesign for a one-off
is as wrong as a hacky patch over a structural flaw. Aim for the middle.

- **Smallest sound change** that closes the *class*, not just the instance —
  proportionate to the failure it prevents.
- **Float larger schemes**, don't reflexively build them — offer the local fix and the
  elaborate one, bias local, let the failure's cost justify the elaborate.
- **Architecture before controls** — prefer making the error impossible to catching it;
  where prevention can't reach, add the control.
- **Belt-and-suspenders** where a failure is costly: do both. Defense-in-depth is a
  feature, not redundancy.

### A.1.4. Proportion governance to the operation — the catalogue is a menu, not a mandate

Governance has a cost: every control taxes every future change and every agent's context budget. The
right amount is not "all of it" — it is the least that holds *your* recurring failures. This method and
its catalogue were distilled from a high-intensity operation (many parallel agents, hundreds of commits a
day); most repos need less than that — though a larger fleet or a higher-stakes domain may need more.
Calibrate to your scale, and treat the catalogue as descriptive — adapt it to fit:

- **Match intensity to pain.** Adopt a control only against a failure you have seen recur — not because
  the catalogue lists it. Default to *skip*; the burden of proof is on adding, not omitting.
- **Small operation → light touch.** One agent or a small team rarely needs the mediators, registries, or
  merge-train machinery; a house-rules doc and a couple of lints may be the whole right answer.
- **Remove what stops earning.** A control that was "fix-once-benefits-all" at scale becomes a
  tax-on-every-change below it; re-audit and delete controls whose failure no longer bites.

The failure mode this guards against is a **tower of governance nobody wants** — controls manufactured
faster than they earn their keep, until the repo is slower and more confusing than the failures it
feared. Grandiosity is a smell; the people most drawn to a governance catalogue are the ones most at risk
of over-building it. (→ A.2.11, A.1.3)

### A.1.5. Reach proactively on the predictive smells — design-time governance

Most governance is failure-driven (A.1.4): default to skip; convert a failure once it *recurs*. But a few
structural traits make a failure class near-certain *before* you've felt it — and for those, reaching for
the mechanism at design time is cheap insurance, not premature. **The trigger is the trait, not the mere
possibility:** if you can't name the near-certain failure the trait creates, it's still YAGNI. Reach when
you see:

- **Concurrency, shared mutable state, or a multi-step mutation that can tear** → a lock/mediator, or make
  the step atomic (transaction / CAS / Lua); walk the T+1…T+N dynamics (→ A.2.10).
- **A stateful lifecycle** (states + transitions) → an explicit state machine, not scattered flags (→ A.2.3).
- **The second copy of the same logic** → unify now, on the second site (→ A.2.5).
- **A raw seam to a powerful resource** (a query language, a subprocess, the filesystem, a format library)
  → one typed seam + a ban-lint on the raw path; a typed signature can make the bug class *unrepresentable*
  (→ A.2.7).
- **The same fact re-derived or hardcoded in more than one place → model it.** Name it once as a typed
  source of truth the tools query, instead of restating it. Two things are worth modeling: **the world**
  (domain state, config, statuses, entities hardcoded across files) and **the codebase itself** (its own
  structure — ownership, zones, seams — re-analyzed by each tool). Model whichever you keep repeating.
- **Retried / queued / time-delayed consumption** → design the second-order dynamics up front (→ A.2.10).
- **A decision point that changes state on a timer or threshold and emits no structured record of what it
  decided** → emit the signal (inputs, computed value, decision, reason) at design time; a silent
  decision core is a near-certain future un-pinnable RCA (→ A.3.6).
- **A trust boundary** — untrusted input, user content, a cross-service call, a secret, or a broad
  capability → validate / escape at the boundary, externalize secrets, grant least privilege.
- **An irreversible op** (delete, overwrite, migrate, force-push) → a guard, a dry-run, or a backup.
- **An invariant that lives only in prose or a head** → encode it + a test that walks it (→ A.3.5).
- **A hot path doing per-item what a bulk, cached, or incremental op could do** (N+1, unbounded fan-out,
  recompute-what-you-could-reuse) → batch it, bound it, make it incremental.
- **An advisory "remember to…"** → make it a hard gate; guidance you must remember rots (→ A.3.1).

These are the *named exceptions* to default-skip — not a license to govern everything. Everything not on
this list stays failure-driven; this is the design-time complement to A.1.2 (which maps a failure to its
mechanism *after* it recurs).

## A.2 — Architecture: make the failure impossible by construction

The first-choice mechanism. Shape the system so the failure class cannot be represented — a typed model
with one sanctioned seam, a state that can't be written wrongly. Prefer these to any control that merely
catches the failure after it happens (→ A.1.3).

### A.2.1. Implementation is cheap; architecture is expensive

Prefer the right design over the faster-but-compromised one. Implementation
is a one-time cost; compromised architecture compounds in maintenance,
agent-confusion, and drift. In an agent-collaborative codebase this asymmetry
is sharper than usual: a bad shape confuses every future agent that reads it,
and substantial refactoring is nearly free (dispatch an agent), so there is
almost never a reason to enshrine a compromise. Corollary: **substantial
refactoring is "free" and drives a recurring audit cadence.**

### A.2.2. Types are how you name shapes; type-in-place before decomposing

Architecture is a structure of shapes; types are how you name them. Types
reveal architecture that primitive-passing leaves anonymous. When decomposing:
(1) annotate the types in-place; (2) let the types become the cross-module
contract; (3) THEN move the typed cluster. Don't decompose what you haven't
yet typed — the types reveal the seam. New Python lands strict-typed; new
frontend lands as TypeScript.

### A.2.3. Explicit models, states, and policies over implicit ones

Name the thing, encode it in types, write a test that walks the encoded
structure. State machines beat scattered counter increments; typed enums beat
magic strings; declared coverage tiers beat binary "covered" claims. Implicit
invariants are invisible to future auditors (human or agent) and rot silently
when surrounding code shifts. This is why job lifecycles are better modelled as
explicit state-machine transition tables than as ad-hoc status increments.

### A.2.4. Class-vs-module shape; single responsibility; extract on the second site

The decomposition default is a module of free functions only for *stateless*
clusters. For a state-bearing cluster (≥2 mutable module-private vars shared
across exported functions, a state machine, or a long-lived cache/handle),
extract a **class** — state wants an owner. Give each unit **one responsibility**:
a module or class that owns two unrelated jobs is two seams wearing one name, and
every future agent has to re-discover the split before it can touch either. And
extract the shared helper on the **second** site, not the third; two files with
the same logic in one PR is the extract-now signal.

### A.2.5. Unify for defect-class consolidation, not just capability

Fix-once-benefits-all is the core affordance — capability parity is
sufficient justification to unify two parallel implementations; you do not
need the merged path to be *more* capable. When two sites share logic, extract
a shared helper — **on the second site, not the third** (DRY-drift hazard).
When unification also unlocks new capability, split the commit: consolidation
(correctness) separate from capability (feature).

### A.2.6. Update call sites; don't preserve legacy shims

When a refactor exposes a cleaner surface, migrate ALL call sites in the same
change. No delegating shim "for backwards compatibility" — compatibility shims
compound into an ongoing two-paths tax that every future agent must reason
about.

### A.2.7. Uniformity over fit — one codebase-wide pattern beats a locally-better bespoke one

Prefer a single consistent approach applied everywhere over a cleverer solution
tuned to one site. In an agent-fleet codebase this trades a small local-optimum
loss for a large system-wide win: a uniform pattern an agent has already seen
200× is applied correctly on reflex, while a bespoke one — however elegant — must
be re-derived from scratch by every future agent that meets it, and each
re-derivation is a chance to get it subtly wrong. Uniformity lowers
agent-confusion and defect *variance* more than local optimization raises
capability. This is the principle behind single-canonical-library, sole-seam, and
one-walker-per-tree disciplines: the win is not that any
one library or model is the best conceivable tool, but that there is exactly
*one* of them, so a fix or a constraint applied once holds everywhere. Deviate
only when a site has a genuine, named reason the uniform pattern cannot serve —
not merely because a bespoke shape would be marginally nicer here.

### A.2.8. Genre check before invent; reach for canonical exemplars

Before proposing a new abstraction, schema, or tool: (1) what is the genre?
(2) who is the canonical best-in-class? (3) can we adopt their schema even if
we skip their runtime? **Adopt the schema even when the runtime is overkill**
— you inherit hard-won constraints at naming-convention cost. And prefer a
single source of truth wherever possible: a stable lint that reads meta-files
at lint-time beats codegen-from-spec beats N hand-rolled lints (each step
loses a drift hazard).

To answer "who is best-in-class," recall the field's most-scrutinized production
systems — for a coding agent the name *is* the retrieval key ("how does Kafka
partition?" recalls more than "how should I shard a queue?"). Reservoirs to jog
memory (not exhaustive): the Apache Software Foundation, the Linux Foundation /
CNCF, Eclipse, GNU; and by genre — streaming/queues:
Kafka, RabbitMQ · orchestration: Kubernetes · relational DBs: PostgreSQL, SQLite
· caches/KV: Redis · web servers/proxies: nginx, Envoy · version control: Git ·
build: Bazel · search: Lucene / Elasticsearch · observability: Prometheus,
OpenTelemetry. Treat these as prior art to adapt, not designs to reinvent.

### A.2.9. Regex policy — parser-first

Regex is acceptable for genuinely simple string matching (literal patterns,
fixed prefixes/suffixes, enum values). For anything that parses semantic
structure, reach for the real parser / walker — content streams, JSON from
LLM output, source code, and document tree traversal each have a canonical
parser. Catastrophic backtracking and "regex that was subtly wrong for months"
are the motivators. (The catalogue ships a runnable example lint for this — see
the governance-lint example.)

### A.2.10. Reason about second-order effects and dynamics

A first-order design ("when X happens, do Y") is often correct in isolation
but produces pathological dynamics under repetition, concurrency, or stale
state. Always walk through: what happens at tick T+1, T+10, T+100? What if N
components do this simultaneously? What if state drifts between dispatch and
consumption? For any new substrate with repetition, concurrency, or
time-delayed consumption, write an explicit "second-order dynamics" section in
the design doc. **Dynamics-aimed tests find the real defects** — distributed
bugs live in driving-conditions and cross-component dynamics, not in static
structure; a strong-but-static unit suite will miss them.

### A.2.11. Essence vs. accident — attack accidental complexity; budget for essential

Two kinds of complexity, handled oppositely (Brooks' "No Silver Bullet"):

- **Essential** — the irreducible complexity of the problem and the structures that solve it: the domain
  rules you're paid to get right, *plus* the inherent difficulty of the abstractions, state, and
  interfaces themselves (a consensus protocol has trivial "requirements" yet enormous essential
  complexity). No tool erases it. **Budget** for it — don't pretend a cleverer abstraction makes it
  vanish; mis-labeling it as accidental produces leaky abstractions that cost more than the complexity
  they hid.
- **Accidental** — introduced by our own tooling and choices: parallel implementations, primitive-passing
  that hides shapes, hand-built argv, scattered state, doc↔code drift. **Attack** it — this is the
  complexity the substrate keeps removing (unification for defect-class consolidation, typed seams, single
  sources of truth). A removal *stays* gone only once a control pins it; otherwise it re-accretes through
  drift — which is why a removal graduates into a lint.

The test before any big refactor: are you *reducing* accidental complexity, or just *relocating*
essential complexity behind a prettier name?

## A.3 — Controls: observe and guard what you can't prevent

Where architecture can't make a failure impossible, catch it: a lint, a gate, a test, a validator that
fires on violation and holds the line. The organizing move — *convert a recurring failure into a control
rather than re-inspect for it* (→ A.1.1).

### A.3.1. Enforce structure with the compiler / static analysis — do not defer

Author the lint or type-check *now*, even when it has zero findings today;
forward-policing IS the value. Code review is not a substitute for static
analysis. **Move audits to lints** whenever the signal is mechanically
detectable — audit signals are expensive, deferrable, and post-hoc; lint
signals are cheap, at-PR, and deterministic. Today's audit finding should
become tomorrow's lint: if a bug is in N>1 files, the right fix shape is "fix
N sites + add a lint," not "fix N sites and wait for the next audit." For a
class-level failure, propose a lint that prevents the class — not just a one-off fix.

### A.3.2. Quality gates — grade on the commodity-lint floor

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
retrieval and breaks a fresh checkout's gates.

### A.3.3. Never silent-catch

Every `except` / `catch` must log, re-throw, convert to a domain error, OR
carry an inline comment justifying the swallow. A silent catch turns a
fail-loud bug into a fail-quiet one — the worst failure mode for a pipeline
where "ran successfully but produced garbage" is invisible. This composes with
a **fail-fast** posture: when a dependency is unreachable, fail loudly rather
than degrade silently.

### A.3.4. Testing strategies — reach for the kind that fits the failure

A specific test is a control; the *strategy* is the general means of building one that catches the
*class*, not just the example in front of you. Match strategy to failure mode — all fair game:

- **Property-based** — invariants over generated inputs.
- **Doc-driven** — pin a doc's claims to the code so the two can't drift.
- **Schema-driven** — structural conformance to a typed shape / registry.
- **Fuzz** — adversarial inputs against a stable point in the spec.
- **State-machine coverage** — walk the declared transitions; catch the illegal ones.
- **User-journey** — end-to-end flows over real driving conditions.
- **Dynamics-aimed** — repetition / concurrency / stale-state, where distributed bugs live (→ A.2.10).

Reach for the right *kind*, not one canonical suite; a strong-but-static unit suite misses the dynamics
ones every time.

### A.3.5. Documentation — the invariants-driven pattern

Subsystem / architecture docs earn their keep through four essential
elements; a doc without them is prose that rots: (1) **a section per real
part** — one section/row per source, stage, module, or entity, mirroring the
actual structure; (2) **invariants with stable IDs** — each invariant a
tagged, testable predicate with a `file:line` cite, and the ID is the join key
that tests and audits cite; (3) **as-built vs design, ⚠️-marked** — call out
where code diverges from design, because the ⚠️ gaps are where the next work
is; (4) **enforcement: invariants → tests** — map each invariant ID to the
test that pins it, or mark it UNTESTED, so the doc *drives* the test backlog.
Design docs encode invariants, not just rationale. (The catalogue ships a
design-doc template starter built on this pattern.)

### A.3.6. Diagnosability-driven observability — an un-pinnable diagnosis is a finding about the signal

When a root-cause analysis **cannot pin the cause from the signal you already have** (logs, events,
traces), treat that inability as a finding in its own right — not a dead end. Add the observability that
*would* have pinned it, so this failure and the ones like it are diagnosable next time **without a
re-run**. This is the runtime analogue of A.3.1's audit→lint reflex: **today's un-pinnable diagnosis
becomes tomorrow's standing signal.** It composes with the fix — close the bug *and* the signal gap —
and never replaces it.

The shape that pays off: a decision point that changes system state — a scaler, a retry, a router, a
gate — emits a **structured, per-decision record** of its inputs, the value it computed, the decision it
took, and why. A later anomaly is then reconstructable from the record alone. Guidance *aims* ("look for
the missing signal"); the emitted signal holds — and a substrate that emits a signal owns it end to end:
whatever emits it also says what healthy looks like and where to look when it isn't.

## A.4 — Operating the method

How the agent works the loop day to day: the stance that keeps velocity honest without lifting the gates.

### A.4.1. Autonomy — carry work through; surface only load-bearing decisions

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
skipping checks.

### A.4.2. Hyper-experimentation — pilot, compare, measure; the prototypes throw away, the learning stays

Ground decisions in data, because in the agentic era data is cheap. Run pilot
studies before wider sweeps; surface 2–3 alternatives before picking; measure
rather than argue — a pilot beats a debate. The discipline that keeps this
from becoming flailing: experiments must be **falsifiable** and grounded in
**ground truth**, **negative results are wins** (a cheap pilot that kills a
bad path saved an expensive build), and you must be willing to be wrong and
**correct the record when the data contradicts you**. The prototype is
disposable; the learning it produces is what you keep.

### A.4.3. Verify factual claims; trust nothing stale

A 30-second `grep` / `wc` / `ls` before quoting a number, a filename, or a
schema fact prevents stale-claim drift — verify brief premises before
dispatching. When reviewing "done" work, **trust nothing at HEAD**: re-run the
gates, pin-tests, and lints yourself; markers and counts rot when sibling
sweeps break the substrate. Agent reports describe *intent*, not *reality* —
verify. This is the central discipline of the final, independent
"trust-nothing" definition-of-done review.

### A.4.4. Destructive-op care

`rm -rf`, overwrite-in-place, force-push, history rewrite: in-repo / scratch
(`/tmp`) is fine without asking; anything outside the repo working tree gets an
explicit ask first, **every time**. Always look before deleting — never remove
a path you did not create or whose contents contradict how it was described.
Destructive `git` on `main` (`reset --hard`, reset to older refs, force-push)
requires explicit user approval — the orchestrator's inline shell has no
worktree backstop, so a flailing reset destroys work permanently. Undo a
landed commit with `revert`, never `reset`.

### A.4.5. Comments and commits earn their place

**Comments** default to none; a comment justifies its existence by explaining
*why* (a non-obvious invariant, a chosen trade-off, a footgun), not by
restating *what* the code does. **Commits** land in reasonable, self-contained
sets with messages that state the intent; agents commit per meaningful step
(never accumulate) and carry a co-author trailer, e.g.
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

*Attribution: Part A is a portable engineering method, reusable across projects, governed by the MIT
license at the head of Part A.*

---

# Part B — Project Reference (write your own)

Part B is where the portable method (Part A) meets **your** codebase. In the source project it is a
stable, numbered index of project-specific rules — each cited by number across the code, never
renumbered — followed by the concrete reference (CLI commands, deploy, architecture, library discipline,
testing, the agent-dispatch machinery). None of that content transfers; you write your own. What *does*
transfer is the **shape**, below.

## What earns a spot in this file

CLAUDE.md is loaded into every agent's context, so every rule pays a per-invocation cost. A rule earns
its place only if **all three** hold:

1. **Regression-preventing** — an agent who didn't know the rule, touching code that doesn't look
   related, could accidentally violate it.
2. **Non-derivable from the immediate code** — reading the file being edited wouldn't surface it.
3. **Non-local** — it crosses files / subsystems. A pattern specific to one class belongs as a
   doc-comment on that class, not here.

If a rule fails any of these, route it out: to a subsystem doc, a class doc-comment, or an inline
`WHY:` comment. Every rule here should cross-reference the doc that explains it in full — CLAUDE.md
carries the minimum agent boot context; the referenced doc carries the complete rationale.

## The shape of a rule (one worked example)

**Number your rules and never renumber them** — the number becomes a citable namespace ("rule #15")
across the codebase. Each rule is a crisp imperative + the WHY + a pointer to where it's *enforced* (a
lint or gate) or explained in full. For example:

> **1. All `<format>` I/O goes through the typed model, never the raw library.** Read via the model's
> reader; write via its typed mutators. Raw-library constructors are banned — a single sanctioned seam
> means a fix or a constraint applied once holds everywhere (→ A.2.7). Enforced by a sole-seam ban-lint
> on the raw alternative. See the *canonical models & seams* control in the catalogue.

Note the moves: an arrow to the Part A principle it instantiates (`→ A.2.7`), a named enforcement
mechanism (the ban-lint), and a link to the catalogue control that generalises it. A rule without an
enforcement pointer is a hope, not a gate.

## Insert your project's rules here

Add rules as your agents surface recurring failures — each new rule is ideally paired with a lint that
prevents the class from recurring (Part A.3.1 + A.1.1: *convert a recurring failure into a control*).
Common sections a mature Part B also carries, all project-specific: conversation conventions, CLI
commands, deploy discipline, architecture overview, library / dependency discipline, testing tiers, and
the agent-dispatch / orchestration machinery. Grow it deliberately — the "what earns a spot" test above
is what keeps it from bloating into noise every agent has to page through.
