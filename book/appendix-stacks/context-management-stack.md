*A flagship deep-dive: the context-management stack, walked part by part. A context-bounded agent cannot
hold the whole corpus, so the substrate delivers the right slice at the right moment — the task's
constraints into the brief, the standing policy into the boot, the omitted step off the runtime lifecycle,
a soft discipline as a rate-limited nudge. This is the book's explicit durable-versus-transient exemplar:
each part is marked for whether it is infrastructure that endures or a crutch a stronger model eases.*

## The goal

**Get the right policy and context to an agent at the moment a decision is due — so it acts on the relevant
slice, not the whole corpus and not its memory.** Five delivery surfaces, at four grains: the task-specific
constraints injected into the brief, the mandatory boilerplate pasted at dispatch, the standing rule index
loaded at boot, an action fired off the runtime lifecycle, and a soft reminder nudged at a gated cadence.
Read against the years, they split: some are infrastructure a larger context window and a stronger model do
not retire, and some are 2026-era crutches whose pressure eases as models improve.

<!-- label: context-management-stack -->
<!-- figure: assets/context-management-stack.svg | The context-management stack in one picture. Five parts run left to right, coloured by durability. INJECT (accent, 2026-transient) maps files-about-to-be-touched to their governing constraints and injects the slice into the brief. SNIPPET (blue, mixed) is the registry of mandatory brief snippets asserted at dispatch — transient delivery, durable enforcement. INDEX (green, durable) loads the numbered rule index into every boot context. HOOK (green, durable) binds a script to the runtime lifecycle so an omitted step fires deterministically. NUDGE (accent, 2026-transient) emits at most one tempo-gated reflection per window. The durable parts are infrastructure regardless of model; the transient parts ease as context windows grow. -->

## How the parts interlock

The stack delivers policy at four grains and one runtime moment. **INJECT** delivers the slice specific to
*this* task — the constraints its files invoke. **SNIPPET** delivers the invariant safety boilerplate every
brief needs, asserted at dispatch. **INDEX** delivers the always-on baseline every agent shares at boot.
**HOOK** shifts from delivering *policy* to firing an *action* at a runtime moment the operator keeps
forgetting. **NUDGE** is the lowest-pressure delivery — a soft reminder of a standing discipline, rate-limited
so it aims without overwhelming. Read the parts in that order; each seam names what the part before it hands
over.

## Durable versus 2026-transient

This stack is where the book makes the durable-versus-transient call explicit, part by part:

- **Durable infrastructure** — INDEX and HOOK. An enforced, numbered rule index and a deterministic
  lifecycle binding do not depend on model capability; they are infrastructure a larger window does not
  retire.
- **2026-transient crutches** — INJECT and NUDGE. Pre-selecting the relevant slice and nudging a forgotten
  discipline both compensate for a 2026 limit — a small context window, a model losing track over a long run.
  Their pressure eases as windows grow and models hold their disciplines, though neither falls to zero.
- **Mixed** — SNIPPET. Its *delivery* half is transient (a model that reliably held every convention would
  need fewer pasted snippets); its *assert-at-dispatch enforcement* half is durable.

## The parts

### 1. INJECT — the task-specific constraint slice

- **Part** — role:dynamic-context-injection
- **Role in the stack** — Map the files an agent is about to touch to the exact constraints that govern them
  — lints, conventions, boundaries, tests — and inject that slice into the brief before it writes code.
- **Failure it retires** — An agent is handed a task and a whole rulebook; it either reads none of it or the
  wrong part, and violates a constraint it would have honored had the constraint been in front of it.
- **Mechanism** — Resolve the files-about-to-be-touched to the constraints that govern them and inject that
  subset into the brief, moving detection *left* of the cheapest CI gate — prevention before the first
  commit.
- **The seam** — Opens the stack. It is the just-in-time face of context delivery: where the snippet table
  and the rule index deliver *standing* policy, injection delivers the slice specific to *this* task, so the
  agent sees exactly the constraints its files invoke.
- **Limits / durability** — **2026-transient in degree** — the smaller the context window, the more injection
  earns its keep; as windows grow, the pressure to pre-select the slice eases, though relevance-focusing
  never fully disappears. It fails where the file-to-constraint map is incomplete, which widens rather than
  breaks it.

### 2. SNIPPET — mandatory boilerplate at dispatch

- **Part** — role:mandatory-snippet-table
- **Role in the stack** — A registry of mandatory brief snippets (PATH export, commit cadence, worktree
  discovery, submodule check) whose presence is asserted at dispatch.
- **Failure it retires** — A brief ships missing a piece of safety boilerplate; the agent drifts its working
  directory, skips the commit cadence, or misses the submodule, and the omission surfaces as a failure far
  downstream.
- **Mechanism** — A typed registry of the mandatory snippets, with a dispatch-time brief-lint asserting each
  required one is present, so every brief carries the safety and context boilerplate it needs by
  construction.
- **The seam** — The point-of-action delivery member. It sits beside INJECT: injection delivers the
  task-specific constraints, the snippet table delivers the invariant safety boilerplate, and both land in
  the same brief at the moment of dispatch.
- **Limits / durability** — **Mixed** — the delivery half is 2026-transient (a model that reliably held
  every convention would need fewer pasted snippets); the assert-at-dispatch enforcement half is durable,
  since a required snippet's absence is a deterministic check regardless of model capability.

### 3. INDEX — the standing rule index at boot

- **Part** — role:claude-md-rule-index
- **Role in the stack** — The numbered, stable-numbered governance rule index loaded into every agent's boot
  context — standing policy delivered by construction at the start of every run.
- **Failure it retires** — The standing rules live in a document no one loads; an agent boots without them
  and re-derives conventions it should have inherited, inconsistently.
- **Mechanism** — A numbered, stable-numbered index loaded into every agent's boot context — held honest by a
  cap lint and a rule-conformance lint — so the standing policy is present at boot, not fetched on demand.
- **The seam** — The standing-policy delivery surface beneath INJECT and SNIPPET. Where those two deliver the
  task-specific and the mandatory-per-brief, the index delivers the always-on baseline every agent shares —
  the common ground the other deliveries specialize.
- **Limits / durability** — **Durable** — an enforced rule index is infrastructure regardless of model; only
  its boot-context delivery role is context-window-sensitive, and even a large-window model benefits from a
  stable numbered index it can cite. Its govern-itself facet lives in the governance-of-governance stack.

### 4. HOOK — an action off the runtime lifecycle

- **Part** — role:lifecycle-hooks
- **Role in the stack** — Bind a script to the agent runtime's lifecycle events — turn-stop, pre-compaction,
  session-start, before-a-tool-call — so a step the operator keeps omitting fires deterministically.
- **Failure it retires** — A step that must happen at a specific moment — a checkpoint before compaction, a
  check before a tool call — depends on someone remembering it, and the moment it is forgotten the state it
  protected is lost.
- **Mechanism** — Register a script against the runtime lifecycle event, so the step fires whether or not
  anyone remembered — deterministic delivery of an *action* at the moment it is due, not a reminder to take
  it.
- **The seam** — The runtime-event face of context delivery. Where INJECT, SNIPPET, and INDEX deliver
  *policy* into a brief or a boot, the hook delivers an *action* at a lifecycle moment — the same just-in-time
  principle applied to the runtime rather than the context.
- **Limits / durability** — **Durable** and model-independent — a deterministic lifecycle binding does not
  depend on model capability; a step that must fire regardless of memory is infrastructure, not a 2026
  crutch. It fails only where the runtime exposes no hook for the moment that matters.

### 5. NUDGE — the rate-limited reflection

- **Part** — role:reflection-facet-substrate
- **Role in the stack** — Tempo-gated policy nudges: a registry of reflection facets, each reflecting the
  running context against one policy dimension, the whole family emitting at most one reflection per window.
- **Failure it retires** — Several soft reminders each fire on their own cadence; together they become a wall
  of nudges the operator learns to ignore, and the alarm fatigue kills all of them at once.
- **Mechanism** — Consolidate the nudges into one tempo-gated substrate — each facet references a policy
  dimension rather than copying it, and the family emits at most one reflection per window — so soft
  reflections cannot compound into fatigue.
- **The seam** — Closes the stack. It is the lowest-pressure delivery: where INJECT, SNIPPET, INDEX, and HOOK
  deliver required policy and actions, the nudge delivers a *soft* reminder of a standing discipline,
  rate-limited so it aims without overwhelming.
- **Limits / durability** — **2026-transient** — tempo-gated nudges compensate for a model losing track of a
  standing discipline over a long run; a model that reliably held its disciplines would need fewer, though
  the at-most-one-per-window substrate that prevents alarm fatigue is durable.
