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

## The constituent parts

Five delivery modalities answer one principle — the right policy at the right moment — each meeting the agent
at a different point: inject the constraints a task's files invoke into its brief, assert the standing safety
boilerplate is present at dispatch, load the numbered rule index into every boot, fire the omitted step off a
runtime lifecycle event, and nudge a standing discipline at a paced cadence.

### INJECT — file-scoped constraint injection {#a-7-dynamic-context-injection}

**INJECT opens the stack with just-in-time delivery.** It maps the files an agent is about to touch to the
exact constraints that govern them — lints, conventions, boundaries, tests — and injects that slice into the
brief before the agent writes code.

**Receives** — the task's target files and the fleet's addressable constraint registries. Nothing precedes
it; this is where policy first meets the specific task.

**Guarantees** — the relevant constraints made binding, not merely available. An agent handed a task and a
whole rulebook reads none of it or the wrong part, then burns rounds discovering and repairing violations it
would have honored had the rule been in front of it. Resolving the files-about-to-be-touched to the rules
that govern them, and rendering that subset into the brief, moves detection left of the cheapest CI gate:
prevention before the first commit. The relevance operator is fallible, so this shifts the odds; a
downstream gate still guarantees the rule.

**Hands to SNIPPET** — the task-specific half of one brief. Where injection delivers the constraints THIS
task's files invoke, the snippet table beside it delivers the invariant boilerplate every brief needs, and
both land in the same brief at dispatch.

→ **Deeper treatment:** role:dynamic-context-injection.

### SNIPPET — the mandatory brief-snippet table {#a-7-mandatory-snippet-table}

**SNIPPET asserts the standing boilerplate is present.** A registry names the mandatory brief snippets —
PATH export, commit cadence, worktree discovery, submodule check — and a dispatch-time lint asserts each
required one appears in the brief.

**Receives** — the brief INJECT is filling, plus the registry of what every brief of this shape must carry.

**Guarantees** — no brief ships missing its safety boilerplate. An author who forgets one — say the PATH
export, without which dozens of format tests fail for a missing binary — sends an agent that trips exactly
that sharp edge twenty minutes in. A docs checklist has no reader and rots as snippets are added; the
registry has one, a lint that greps for every required marker and refuses the dispatch on any absence. Some
snippets are always-include, others conditional on the brief's shape, so a brief carries what it needs and
nothing it does not.

**Hands to INDEX** — the per-brief half beneath the always-on baseline. Where the snippet table delivers the
boilerplate mandatory for THIS dispatch, the rule index below it delivers the standing policy every agent
shares, whatever the task.

→ **Deeper treatment:** role:mandatory-snippet-table.

### INDEX — the boot-context rule index {#a-7-claude-md-rule-index}

**INDEX delivers the always-on baseline.** The numbered, stable-numbered rule index loads into every agent's
boot context — standing policy present by construction at the start of every run, not fetched on demand.

**Receives** — the standing rules themselves, each a short boot-context statement cross-referenced to the
canonical doc that carries it in full. It sits beneath INJECT and SNIPPET as the layer neither specializes.

**Guarantees** — every agent boots on the same shared world-model. Standing rules that live in a document no
one loads leave an agent re-deriving conventions it should have inherited, inconsistently, one dispatch at a
time. Loading the index by construction makes the minimum shared policy present at boot, rather than a
reference the agent might consult. A cap lint keeps it inside a scannable budget and a conformance lint
keeps each rule citing its canonical doc, so the always-on baseline stays worth booting.

**Hands to HOOK** — the shift from context to runtime. Where INJECT, SNIPPET, and INDEX deliver POLICY into
a brief or a boot, the hook beside them delivers an ACTION at a runtime moment — the same just-in-time
principle, applied to the lifecycle rather than the context.

→ **Deeper treatment:** role:claude-md-rule-index.

### HOOK — the runtime lifecycle hook {#a-7-lifecycle-hooks}

**HOOK delivers an action at a runtime moment.** It binds a script to the agent runtime's lifecycle events —
turn-stop, pre-compaction, session-start, before-a-tool-call — so a step the operator keeps omitting fires
deterministically.

**Receives** — the runtime's named lifecycle events and a step that must happen at one of them. Where the
layers above deliver policy into context, this one reads the runtime itself.

**Guarantees** — the omitted step fires whether or not anyone remembered. Some failures live in the loop
that drives the agent, not the code it writes: ending a turn with work still queued, compacting without a
hand-off, editing outside the worktree. A lint cannot reach these: the omission happens at runtime, in the
loop itself. The hook splits enforcement's two halves. The firing is hard, guaranteed by the runtime. The
payload is either a hard block that denies the action or soft guidance re-injected into context. The reflex
case, hard delivery of soft guidance, makes the aiming deterministic: the same reminder fired exactly at the
decision point, every time.

**Hands to NUDGE** — the substrate you build on the second reflection hook. One hook re-arms one reflex; a
second soft nudge starts the fatigue the tempo-gated substrate below resolves.

→ **Deeper treatment:** role:lifecycle-hooks.

### NUDGE — the tempo-gated reflection substrate {#a-7-reflection-facet-substrate}

**NUDGE closes the stack at the lowest pressure.** It consolidates the operator's reflection nudges into one
tempo-gated substrate: a registry of facets, each reflecting the context against one policy dimension it
references, not copies, the whole family emitting at most one reflection per window.

**Receives** — the single-hook primitive from HOOK, plus more than one discipline worth nudging. It earns
its keep at the second facet, not the first.

**Guarantees** — soft reminders that cannot compound into fatigue. Fire several nudges, each on its own
cadence, and together they become a wall the operator tunes out, killing them all at once. One shared tempo
budget caps the aggregate: a class's facets round-robin for a single window's reflection. A closed surface
stops a facet re-implementing shared machinery; each facet points at its canonical policy, so a moved doc
trips a lint rather than rotting in a payload string; per-firing telemetry puts the family on a measured
leash, pulled on over-fire or near-zero yield.

**Hands off** — the stack's softest delivery. Where the other four deliver required policy and actions, the
nudge delivers a rate-limited soft reminder of a standing discipline, so it aims without overwhelming: the
gentle end of this stack's delivery spectrum.

→ **Deeper treatment:** role:reflection-facet-substrate.

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
