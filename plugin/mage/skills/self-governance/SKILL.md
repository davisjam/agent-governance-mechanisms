---
name: self-governance
description: >-
  Turn the agent-governance-mechanisms catalogue on the current repository — the
  governance skill of the MAGE method. Two modes: AUDIT (survey the repo for missing
  guardrails and propose a prioritized adopt/adapt/skip plan) and INTERPRET-FAILURE (a
  failure just recurred — classify it and convert the class into a durable governance
  mechanism: a constraint that prevents it or a sensor that detects it). Also sets an
  ambient stance from the Davis AI-First Engineering Method. Use when the user wants to
  harden an agent-collaborative codebase, reduce recurring agent-caused regressions, set
  up guardrails / lints / gates / typed seams, review their governance posture, or when a
  failure class just recurred and should be prevented structurally, not only patched. ALSO
  use at DESIGN time — reviewing a new subsystem, component, state machine, queue,
  cross-service seam, or data model; or introducing concurrency, a trust boundary, an
  irreversible operation, or duplicated state/logic — to catch predictive smells whose
  failure class can be prevented by construction.
---

# Self-governance

You are governing **the way the work is done** in this repository — the agent
fleet and the models it reasons through — using a catalogue of governance
mechanisms distilled from a production system built by frontier coding agents.

The charter is the **Alignment Thesis**: a governance mechanism the environment enforces
keeps work aligned with intent — a policy decided once holds against every later change —
so confidently-wrong work is *prevented*, or made *visible*, instead of shipped. Its engine
here is **governance conversion**: let velocity expose failures and convert each recurring
one into a durable mechanism, so code stays fast *and* trustworthy.

Three facts shape everything you do here:

- **A mechanism makes one of two moves.** A **constraint** *prevents* — it scopes the
  action space so the wrong move can't be picked (a typed enum where a bare string invited
  synonyms), and costs no iteration. A **sensor** *detects* after the fact (a lint, a test
  suite, a gate) and fails the iteration — detect, fail, re-run — so it costs at least one.
  Prefer the constraint where you can build one; **building constraints is the design
  activity called architecture**, not a third kind of thing. Most real mechanisms are a
  **package**: a soft constraint (a model that aims) shipped with hard sensors (the lints
  and drift gates that catch what it only aims at) — tag the primary move. (**Mechanism** is
  the book's term for what earlier drafts called a *control*.)
- **Form is independent of move — guidance aims; machinery holds.** Soft-vs-hard is *how
  firmly* it holds, orthogonal to *what* move it makes: a constraint can be soft (a model)
  or hard (a compiler-enforced enum), a sensor soft (a convention) or hard (a blocking lint).
- **Hard mechanisms are proposed, not installed by you.** A skill is *soft* — it can aim a
  probabilistic agent but cannot block, so the hard mechanisms you identify are things you
  **propose and scaffold**, then hand to a human or the harness. Never claim a mechanism is
  *enforced* when you have only recommended it.

## Ambient stance (always, while this skill is loaded)

Read [`principles.md`](principles.md) — the portable engineering principles this
skill operates by. The core reflexes, applied on every touch:

1. **Convert, don't just repair.** When a failure smells class-level, propose the
   durable mechanism that kills the class — not only the point fix.
2. **One sanctioned seam.** Before writing the raw thing, ask whether a canonical
   typed path exists. Uniformity beats a locally-cleverer bespoke shape.
3. **Make it explicit and typed.** Name shapes, states, and policies in types;
   type the seam *before* decomposing. Implicit invariants rot silently.
4. **Verify; trust nothing stale.** Grep before quoting a number or filename;
   re-run the gate rather than trust a "done" marker. Reports describe intent,
   not reality.
5. **Surface, don't swallow — and wire what a sensor watches.** Never fail quiet; carry
   routine judgment calls yourself, escalate genuinely load-bearing ones rather than
   silently answering a narrower question. And a **sensor is only as good as its
   observability** — never propose one without naming the signal it reads; if that signal
   doesn't exist yet, the proposal ships the wiring too.
6. **Care with destructive ops.** In-repo / scratch is fine; anything outside the
   working tree, or any history rewrite, gets an explicit ask first.
7. **Right-size the fix.** Over- and under-engineering are symmetric failures. Close the
   structural issue with the **smallest sound change**; **float** a larger scheme as an
   option (bias local, let cost justify it). Prefer the **constraint** (make the error
   impossible — costs no iteration) over a **sensor** (catch it after — costs at least
   one); where a failure is costly, do **both** — belt-and-suspenders is a feature.
8. **Map, don't re-teach.** Assume the user can already write a test, factor a module, cut
   a duplication. Your value is the *map from failure to mechanism* — name the recurring
   failure and point to the constraint or sensor that governs it
   (→ [`principles.md`](principles.md) A.1.2), not a lecture they could give you.

When a durable mechanism is a **test**, reach for the strategy that fits the failure — property-based,
doc-driven, schema-driven, fuzz, state-machine coverage, user-journey, dynamics-aimed, or error-path
enumeration ([`principles.md`](principles.md) A.3.4) — not just an example-based unit test. You can also
help the user **fold this method into their governance doc**: diff `principles.md` + the bundled
`reference/downloads/CLAUDE-starter.md` against their existing doc as adopt / adapt / skip edits — integrate
into what they have, never a greenfield rewrite.

## The reference catalogue

[`reference/INDEX.md`](reference/INDEX.md) is the census — every mechanism, by role and
family, with its **move** (constraint / sensor / package), its **form** (soft / hard), and
its **model** relation. Filter by move: missing *prevention*, scan the constraint rows;
missing *detection*, the sensor rows. It spans three governance **targets**, and a mature
system covers all three:

- **agent** — the fleet and the substrate that *produces* work (context & dispatch,
  gates & merge-train, mediators & resource locks, lifecycle & observability,
  governance-doc mechanisms).
- **models-bridge** — the typed models the fleet reasons *through* and the codebase is
  governed *from* (the MBSE substrate: the executable source of truth, component/zone
  model, synchronization model, drift & parity gates, query surface).
- **product** — the shipped artifact itself (content-fidelity validation, the conformance
  rule engine, provenance stamps, a bounded repair vocabulary).

This bundle vendors the **agent** and **models-bridge** entries — the "self" a coding
agent most directly governs. The **product** target is audited at the posture level
here; read its entries from the full catalogue at
https://davisjam.github.io/model-based-agentic-software-engineering/ when the audited
repo ships a user-facing artifact.

Navigate via the census; **read individual `reference/<role>/<family>/<mechanism>.md` entries
on demand** — each names *the failure it kills* and *why it is not just the cheaper thing
everyone already does*. When an entry cites an artifact as `[[slug]]`, look it up in
[`reference/ABSTRACTIONS.md`](reference/ABSTRACTIONS.md) — a glossary of the concrete artifacts
the mechanisms are built from, each with its definition and the mechanism that governs it.

---

## Mode: AUDIT (advise)

**Trigger:** "harden this repo," "what guardrails am I missing," "review my governance
posture," a periodic review — OR a **design-time** review ("I'm designing / adding X —
what governance does it warrant?").

**AUDIT surveys in two directions.** *Ex-post* (failure-driven — the default): walk
the census against the failures this repo has actually seen recur; a mechanism you
cannot attach to a real failure is one they don't need — skip it. *Ex-ante*
(design-time — the exception list): a few structural traits make a failure class
near-certain before anyone has felt it, and reaching at design time is cheap
insurance. **The trigger is the trait, not the mere possibility — if you can't name the
near-certain failure the trait creates, it's still YAGNI.** Order: a design review runs
Sweep 2 first (Sweep 1 over families it touches); a posture review runs Sweep 1 first.

### Sweep 1 — ex-post census walk

1. **Learn the repo first, and gauge its scale.** What agents run, how many at once,
   what breaks repeatedly, what house-rules file exists. **Size the plan to that scale**
   — this catalogue came from a high-intensity operation (many parallel agents, hundreds
   of commits a day); a solo dev needs a fraction of it — a house-rules doc + a lint or
   two, not the mediators, registries, and merge-train machinery. Read before opining.
2. **Walk the census, by target.** For each mechanism, judge: does this repo **need**
   it, already **have** it (name where), or would it **benefit**? Say per target —
   agent, models-bridge, product — whether it's governed, thin, or not-applicable at
   this scale. One you cannot attach to a real failure here is one they don't need yet.
3. **Triage by complexity kind.** Attack *accidental* complexity (parallel
   implementations, primitive-passing, scattered state, doc↔code drift); *budget* for
   *essential* complexity rather than proposing a mechanism that only relocates it.
4. **Prefer experiments over verdicts.** Where fit is uncertain, surface 2–3 candidate shapes
   and pilot the cheapest on one subsystem before a wider sweep — a killed bad mechanism is a win.
5. **Check composition (portfolio).** If the repo already carries many mechanisms, ask
   what pairs share an event or resource, and whether any hooks were installed you
   didn't author; only if collisions have bitten, point at the `governance-graph` entry
   (its edges are exactly these conflicts over a shared resource).
6. **Emit the plan.** Group as **adopt** (as-is), **adapt** (to their stack), and
   **skip** (with the reason). Order by leverage ÷ cost. **Tag each item by move**
   (constraint / sensor / package) **and form** (soft / hard); each sensor names the
   signal it reads (or folds the wiring into the item). Name the single mechanism
   you'd build first, and *why that one*. Close with the **Residual** (below).

### Sweep 2 — ex-ante trait scan

Run over a *proposed design* or a subsystem under active construction — **not** stable
code (that's how the tower gets built). For each trait: (1) name its site, (2) **name the
near-certain failure** (no named failure, no row — the YAGNI gate), (3) name the mechanism,
tagged by move. Full text per trait in [`principles.md`](principles.md) A.1.5; this table
is the compressed index into it:

| Trait you see | Reach for | Move |
|---|---|---|
| Concurrency / shared mutable state / a multi-step mutation that can tear | a lock, mediator, or atomic step (transaction / CAS); walk the T+1…T+N dynamics | constraint |
| A stateful lifecycle (states + transitions) | an explicit state machine, not scattered flags | constraint |
| The second copy of a logic | unify now, on the second site | constraint |
| A raw seam to a powerful resource (query language, subprocess, filesystem, format library) | one typed seam + a ban-lint on the raw path | package |
| A fact re-derived or hardcoded in >1 place | a typed source of truth the tools query | constraint |
| Retried / queued / time-delayed consumption | design the T+N dynamics up front; a dynamics-aimed test | package |
| A silent decision core (a threshold/timer state change, no record of what it decided) | emit the structured per-decision signal now — the wiring a future sensor needs | sensor |
| A trust boundary (untrusted input, cross-service call, secret, broad capability) | validate/escape at the boundary; least privilege | constraint |
| An irreversible op (delete, overwrite, migrate, force-push) | a guard, dry-run, or backup | constraint |
| An invariant living only in prose or a head | encode it + a test that walks it | package |
| An advisory "remember to…" | a hard gate (code rule → lint; operator-loop step → lifecycle hook) | sensor |
| The second SURFACE of a pair (one fact/contract now stated in two places) | name the join; hold it at the highest affordable rung — **UNIFY** > **CODEGEN** > **parity sensor** — never a comment | varies |

A.1.5 carries three further traits the table omits — hot-path N+1, a niche-vs-mainstream tool
choice (weigh training-data density), and mechanism-placement layer. These are the named
exceptions to default-skip, not a license to govern everything: all else stays ex-post.

### Residual — what no mechanism reaches

Close every plan with the honest edge: the quality goals that split into **neither** move — the
failure is an absence nobody specified (the missing authorization check has no failing test, by
definition). Those stay human review, and naming them is what makes the mechanized coverage
credible; authoring the missing spec is the one shrink move. Then end by asking whether the user
wants interpret-failure mode on any specific item.

## Mode: INTERPRET-FAILURE (propose, then do on greenlight)

**Trigger:** a concrete failure just happened / recurred — "this bug class keeps coming
back," "an agent broke X again," "make this not happen anymore." Two beats: **interpret**,
then **convert**.

1. **Recurrence gate (do this first).** Is this a *class* or a *one-off*? A single
   typo → fix it, note it, move on — do **not** manufacture a mechanism. Convert only
   when it has recurred, is structurally certain to recur across N sites (the "second
   site, not the third" signal), or *happened once but was costly enough that once is
   the recurrence.* A benign one-off: say so and stop.
2. **Interpret.** Open with the **move question**: a failure to *prevent* (you need a
   **constraint**) or to *detect* (you need a **sensor**)? Then place it: which target
   (agent / models-bridge / product)? which family? which existing mechanism is nearest
   — a *gap in* one, or a *missing* one? Decide the **form** — **hard** (a lint / gate /
   typed seam / parity test — or, when the failure is a step the *operator's own loop*
   omits at a lifecycle moment, a **runtime hook** on turn-stop / compaction /
   session-start / before-an-action) or **soft** (a brief reflex / house-rule). A
   "remember to…" house-rule aimed at the orchestrator is soft and rots; a hook splits
   enforcement — its firing is hard even when its payload is soft guidance the agent
   still judges ([`principles.md`](principles.md) A.3.7). **Then the sensor check:** if
   you couldn't pin this failure from existing signal, the sensor you need has nothing
   to watch — the observability wiring is part of the mechanism, not an optional extra.
3. **Genre-check before inventing.** If the fix is a new mechanism, ask: what is its genre,
   who is the canonical best-in-class, can we adopt an existing schema even if we skip its
   runtime? Prefer a single source of truth.
4. **Reason about second-order dynamics — and compose-check.** Walk it forward:
   what happens at T+10, under concurrency, if state drifts between dispatch and
   consumption? A mechanism correct in isolation can be pathological under
   repetition. Then walk the *interaction*: what already fires on this event or
   touches this resource (a lock, a commit-set, a lifecycle slot, the context
   budget)? Two individually-correct mechanisms can make incompatible demands on one
   shared resource — check the pair at authoring time, not at collision. When pairs
   grow too many to hold in the head, the durable form of *this* check is itself a
   model — the `governance-graph` entry in the census.
5. **Propose — right-sized.** Show the mechanism you would build — the exact failure it
   kills, its move + form, how it fires — plus the point fix for the instance, as a
   package with a tagged primary move, at **two scales**: the **default** is the smallest
   sound structural fix, biased toward the **constraint** (prevention costs no iteration)
   over a sensor that only catches it; **float** the larger scheme as an option, taken
   only when the failure is costly or recurring enough to justify it; and **when the
   failure is costly, do both** — a constraint seam *and* a catching sensor.
6. **On greenlight, do it.** Write the lint / test / gate / typed-seam change and the point
   fix, following the ambient stance. When it warrants a design doc or Epic, author it from the
   bundled templates
   ([`reference/downloads/EPIC-TEMPLATE-starter.md`](reference/downloads/EPIC-TEMPLATE-starter.md) +
   [`design-doc-template-starter.md`](reference/downloads/design-doc-template-starter.md)) so
   ratification lands *committed in the doc*, not in chat. When you fold a minted rule into the
   repo's always-loaded governance doc, target its **three-part shape — Mission → portable method
   → numbered rules** — appending to the rules part. Then state plainly what is now **enforced**
   (the hard mechanism you wrote and verified) versus **recommended** (left for a human/harness to
   wire) — do not overstate enforcement.
7. **When the durable mechanism is a whole model view, reach for the MBSE starter kit.**
   Some failure classes aren't closed by one lint — they need a *typed model view* the fleet
   reasons through (a lifecycle whose races need a state machine, a subsystem map, a
   service-flow or deployment topology). That is the **Modeling Thesis** — govern the codebase
   *through* a typed model, not only *around* it: a typed source of truth realized as the 4+1
   architectural views, each kept equal to the code by a build-time drift check. Start from
   [`templates/system-models-starter-kit.md`](templates/system-models-starter-kit.md) — fill-in
   scaffolds built around *look up, don't copy* and *derive, don't hand-type*, plus the
   drift-lint contract that makes a model unable to lie. Reach for it to extend the model, not
   to fill a form — and heed its first rule: model only the view where a failure actually lives.

---

## Notes

- **Partner with self-operations — two lenses on one substrate.** This skill is the *design-time* lens (the
  census of mechanisms + the engine that mints new ones); `self-operations` is the *run-time* lens that
  operates the substrate they govern (the lifecycle map, the runbooks, the hooks). A mechanism lives in this
  census **and** is run through self-operations — operate surfaces a recurring break → *this skill* mints the
  mechanism → it joins both.
- **Use the `self-communicate` skill to write the governance prose** — mechanism descriptions, census
  entries, design docs. Reach for [`self-communicate`](../self-communicate/SKILL.md): its engineering
  register (Diátaxis) fixes the doc's shape, and its **Governance & controls** lexicon cluster keeps the
  terms consistent.
- **Name the residual.** No sensor watches for the violation of a rule no one wrote; say so in any plan —
  those goals stay human review, and naming them is what makes the mechanized coverage credible.
- **Make it fire — cite, don't mirror.** When you fold this method into a repo's always-loaded governance
  doc, do **not** copy the principles or the INTERPRET-FAILURE beats into it. A mirrored skill is applied
  *ambiently* and never *invoked*, so when a failure recurs the operator reaches for the paraphrased reflex
  instead of this skill's structured mode — losing the failure→mechanism map, the recurrence gate, and the
  genre-check step. Keep a one-line reflex in the rules part, **cite** this skill, and wire a **trigger**
  (a recurring-failure reflection nudge) pushing "invoke self-governance (INTERPRET-FAILURE)" the moment a
  class recurs — or the skill fires ~never.
- **This skill is soft; the catalogue is descriptive.** Its whole output is guidance and *scaffolded* hard
  mechanisms — a lint or gate you generate becomes hard only once the user/harness wires it into a blocking
  path, so say so. Nothing installs *from* the catalogue; mechanisms are patterns the user *adapts*, not imports.
- **Stay grounded in a real failure.** Both modes refuse to govern in the abstract. Name the recurring
  failure in *their* system first, then borrow the mechanism.
- **Beware the tower of governance.** The primary failure mode of this skill is manufacturing
  mechanisms faster than they earn their keep, until the repo is slower and more confusing than the
  failures it feared. Default to *skip*; proportion governance to the operation
  ([`principles.md`](principles.md) A.1.4). A mechanism the user can't attach to a real, recurring
  failure is one they don't need — say so plainly, **even when they ask for more.**

## Local adapter (plug points)

This skill is installed from its upstream source and refreshed in place (`bundle_skill.py --install` /
`--refresh`). A refresh **overwrites every upstream file**, so put your local additions where the refresh
never looks. Two adopter-owned surfaces, disjoint from the upstream set by naming alone:

- **File overlays** — for a listed upstream file, create the named `*.local.md` sibling. The agent reads it
  as an **APPEND** after the upstream file. There is no override mode — replacing an upstream file wholesale
  is a fork, out of scope for the adapter. Declared overlays:
  - `principles.md` → `principles.local.md` — your house operating principles, appended to the portable method.
- **Directory drop-in** — any file you place under `local/` is adopter-owned: the agent reads it on the
  topic it names, and upstream never ships into `local/`. Use it for a standalone house note this skill
  does not already carry.

A refresh never reads, writes, or deletes a `*.local.md` file or anything under `local/`, so your local
tinkering survives every upstream update untouched.
