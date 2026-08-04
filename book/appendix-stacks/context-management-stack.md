*A two-page synthesis of the context-management stack. Five patterns get the right policy and context to an
agent at the moment a decision is due — so it acts on the relevant slice, not the whole corpus and not its
memory. This is the book's explicit durable-versus-2026-transient exemplar: each part is marked for whether
it is infrastructure that endures or a crutch a stronger model eases.*

## The capability

**Deliver the policy an agent needs at the grain and moment it needs it — the task's constraints into the
brief, the standing rules into the boot, an omitted step off the runtime lifecycle, a soft discipline as a
rate-limited nudge.** The stack makes one capability: *manage work, state, and resources*, on its context
face. Five delivery surfaces at four grains, so a bounded-context agent acts on the slice that matters
rather than re-reading a whole rulebook or trusting its memory. Read against the years the parts split: some
are infrastructure a larger window does not retire, some are 2026-era crutches whose pressure eases as
models improve.

## Failure classes it covers

- **The unread rulebook.** An agent is handed a task and a whole rulebook; it reads none of it or the wrong
  part, and violates a constraint it would have honored had the constraint been in front of it.
- **The missing boilerplate.** A brief ships without a piece of safety boilerplate; the agent drifts its
  working directory, skips the commit cadence, or misses a submodule, and the omission surfaces downstream.
- **The unloaded standing policy.** The standing rules live in a document no one loads; an agent boots
  without them and re-derives conventions it should have inherited, inconsistently.
- **The forgotten step.** A step that must happen at a specific moment — a checkpoint before compaction, a
  check before a tool call — depends on someone remembering it, and the moment it is forgotten the state it
  protected is lost.
- **The wall of nudges.** Several soft reminders each fire on their own cadence; together they become noise
  the operator learns to ignore, and the alarm fatigue kills all of them at once.

## Composition

<!-- label: context-management-stack -->
<!-- figure: assets/context-management-stack.svg | The context-management stack in one picture. Five parts run left to right, coloured by durability. INJECT (accent, 2026-transient) maps files-about-to-be-touched to their governing constraints and injects the slice into the brief. SNIPPET (blue, mixed) is the registry of mandatory brief snippets asserted at dispatch — transient delivery, durable enforcement. INDEX (green, durable) loads the numbered rule index into every boot context. HOOK (green, durable) binds a script to the runtime lifecycle so an omitted step fires deterministically. NUDGE (accent, 2026-transient) emits at most one tempo-gated reflection per window. The durable parts are infrastructure regardless of model; the transient parts ease as context windows grow. -->

Four parts deliver *policy* at four grains — task-specific, per-brief mandatory, always-on standing, soft
reminder; one delivers an *action* at a runtime moment. Each seam names what the part before it hands over.

## The constituent patterns

- **INJECT — role:dynamic-context-injection.** Map the files an agent is about to touch to the exact
  constraints that govern them — lints, conventions, boundaries, tests — and inject that slice into the brief
  before it writes code, moving detection left of the cheapest CI gate. The just-in-time face of delivery.
- **SNIPPET — role:mandatory-snippet-table.** A typed registry of the mandatory brief snippets — PATH export,
  commit cadence, worktree discovery, submodule check — with a dispatch-time lint asserting each required one
  is present, so every brief carries its safety boilerplate by construction.
- **INDEX — role:claude-md-rule-index.** The numbered, stable-numbered governance rule index loaded into
  every agent's boot context — the always-on baseline every agent shares, held honest by a cap lint and a
  conformance lint.
- **HOOK — role:lifecycle-hooks.** Bind a script to the runtime's lifecycle events — turn-stop,
  pre-compaction, session-start, before-a-tool-call — so a step the operator keeps omitting fires
  deterministically. It delivers an *action* at the moment it is due, not a reminder to take it.
- **NUDGE — role:reflection-facet-substrate.** Tempo-gated policy nudges: a registry of reflection facets,
  each reflecting the running context against one policy dimension, the whole family emitting at most one
  reflection per window — so soft reminders cannot compound into fatigue.

## A DocAble example, end to end

A DocAble agent is dispatched to change PDF tag-tree code. **INJECT** resolves the files it is about to touch
to the constraints that govern them — the typed-seam rule, the ban-lint on raw library calls, the tests that
pin the format — and drops that slice into the brief, so the agent sees exactly the rules its files invoke
before it writes a line. **SNIPPET** asserts the brief also carries the invariant safety boilerplate: PATH
export, commit cadence, worktree discovery, the submodule check. **INDEX** is already present — the numbered
rule index loaded at boot gives the agent the always-on baseline the other deliveries specialize. Mid-run,
**HOOK** fires a checkpoint before the context compacts, saving state the agent would otherwise lose to a
forgotten step. And **NUDGE**, at most once per window, reflects the running work against one standing
discipline — a soft reminder that aims without becoming the wall of alarms the operator tunes out.

## Tradeoffs and adoption order

This stack is where the book makes the durable-versus-transient call explicit, part by part.

1. **INDEX and HOOK are durable.** An enforced rule index and a deterministic lifecycle binding lean on no
   model capability; they are infrastructure a larger window does not retire. Adopt them first.
2. **SNIPPET is mixed.** Its delivery half is 2026-transient — a model that reliably held every convention
   would need fewer pasted snippets — but its assert-at-dispatch enforcement half is durable, since a
   required snippet's absence is a deterministic check.
3. **INJECT and NUDGE are 2026-transient in degree.** Pre-selecting the relevant slice and nudging a
   forgotten discipline both compensate for a 2026 limit — a small window, a model losing track over a long
   run. Their pressure eases as windows grow, though relevance-focusing and fatigue-prevention never fall to
   zero.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
INDEX's govern-itself facet lives in the
[governance-of-governance stack](appendix-d-governance-of-governance-stack.html); the stack shares one
machine among many agents with the [resource-mediation stack](appendix-d-resource-mediation-stack.html). The
full 83-mechanism catalogue is online in the web edition.
