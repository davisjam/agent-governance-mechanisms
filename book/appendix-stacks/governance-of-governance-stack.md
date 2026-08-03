*A flagship deep-dive: the governance-of-governance stack, walked part by part. A fleet accumulates
controls — lints, gates, mediators, registries — and the control estate itself becomes a system that can
drift, collide, and rot. This stack turns the governance system into its own subject of governance.*

## The goal

**Govern the control estate as its own subject.** Model the controls as a graph so two guardrails cannot
silently collide; census which targets are covered and which are blind; compute the blast radius of a
substrate change before making it; convert each recurring failure into a proportionate new control so the
estate grows by design; and hold the governing document itself as enforced, queryable infrastructure rather
than prose that rots. Six parts make the estate legible to itself, questionable for its own blind spots and
change-safety, self-repairing when a failure recurs, and deliverable to every agent.

<!-- label: governance-of-governance-stack -->
<!-- figure: assets/governance-of-governance-stack.svg | The governance-of-governance stack in one picture. Six parts run left to right. Model the estate (violet): GRAPH represents each control as a node tagged by trigger and resource footprint, with a conflict edge where two controls contend; REGISTRY attaches machine-readable metadata to each governance rule. Query the estate (green): CENSUS classifies each control by the target it guards, so a bare target is a re-derived gap; RADIUS makes each control declare its substrate assumption, so a change's blast radius is a computed query. Grow the estate (green): INTERPRET converts a recurring failure into a proportionate new control, fired on a cadence. Deliver it (accent): INDEX holds the governance document as a numbered, enforced, capped rule index in every agent's boot context. -->

## How the parts interlock

The stack turns governance into a governed model. **GRAPH** maps the controls and derives a conflict edge
wherever two contend over one resource — collisions caught at model time, not in production. **CENSUS** rolls
those nodes up per target and surfaces the bare ones. **RADIUS** walks the graph's substrate edges to answer
"what will my change break." **INTERPRET** turns a recurring failure — or a gap the census surfaced — into a
proportionate new control, fired on a cadence so the estate grows by design and not by memory. **REGISTRY**
makes the governing prose itself a queryable model. **INDEX** is
the delivery surface: the governance the graph maps, the census covers, and the blast-radius query protects
reaches every agent only because this enforced, capped index puts it in front of them. Read the parts in
that order; each seam names what the part before it hands over.

## The parts

### 1. GRAPH — the controls as a typed graph

- **Part** — role:governance-graph
- **Role in the stack** — Model the fleet's process-governance mechanisms as a typed graph: each mechanism a
  node tagged by the event it fires on and the resources it reads, writes, or locks; each edge a conflict
  over a shared resource.
- **Failure it retires** — Two guardrails contend over one resource — a lock, a file, a queue — and the
  collision is discovered only when they trip each other in production, because nothing modeled that they
  touch the same thing.
- **Mechanism** — Represent each control as a node carrying its trigger and its resource footprint, and
  derive a conflict edge wherever two nodes contend over one resource — so a collision is caught by
  construction, at model time.
- **The seam** — Opens the stack. It is the map of the estate the rest of the parts read: the census rolls
  its nodes up per target, the blast-radius query walks its substrate edges, and a new control is placed by
  where it lands in the graph.
- **Limits / durability** — Durable — a typed graph of the controls is model-independent and re-derives on
  every change. Its cost is tagging each control's trigger and footprint; it is only as complete as the
  controls that remember to register their nodes.

### 2. CENSUS — coverage over the control targets

- **Part** — role:control-coverage-census
- **Role in the stack** — Classify every control by which complementary control-target it guards — derived
  from the control's own code anchor, never hand-declared — and roll the set up per target.
- **Failure it retires** — The estate has blind spots no one can see: a target guarded only by soft aims and
  no hard hold, or by nothing at all, discovered the day it fails rather than the day the gap opened.
- **Mechanism** — Derive each control's target from its code anchor and aggregate per target, so a target
  with zero controls — or only soft ones — is a re-derived coverage gap surfaced as a queryable map.
- **The seam** — Reads the GRAPH's nodes and asks the coverage question of them: which targets are held,
  which are only aimed at, which are bare. It hands the estate a map of its own blind spots instead of a
  surprise.
- **Limits / durability** — Durable — a census derived from code anchors does not drift the way a hand-kept
  list would. Its cost is the classification rules; it is exactly as honest as the anchors, which move with
  the code they cite.

### 3. RADIUS — the computed blast radius

- **Part** — role:control-substrate-dependency
- **Role in the stack** — Make each control *declare* the substrate assumption it bakes in as typed
  metadata, so "which controls depend on this part of the substrate, and what breaks if I change it" is a
  computed query.
- **Failure it retires** — A cross-cutting substrate change lands blind; a control that silently assumed the
  old shape breaks, and the blast radius was a grep-and-read no one ran completely.
- **Mechanism** — Each control declares the substrate it reads as typed metadata; a static-analysis query
  then rolls up the dependents of any substrate, so the blast radius of a change is known up front.
- **The seam** — Sits over the GRAPH's substrate edges. Where the census answers "is this target covered,"
  the blast radius answers "what will my change to this substrate break" — the estate reasoning about its own
  change safety before the change.
- **Limits / durability** — Durable — declared dependencies plus a static query are deterministic and
  model-independent. Its cost is the per-control declaration; it fails only where a control bakes in an
  undeclared assumption, which reads as a missing edge.

### 4. INTERPRET — a recurring failure becomes a new control

- **Part** — role:self-governance
- **Role in the stack** — Convert a recurring failure *class* into a proportionate new control, and fire that
  conversion on a cadence so the estate grows by design rather than by whoever happens to remember.
- **Failure it retires** — The same failure is re-patched locally each time it recurs, so the class survives
  to bite the next agent; and even a team that believes in converting the class forgets to do it on a long
  autonomous run, because the trigger lives only in memory.
- **Mechanism** — A loop names the recurring failure class and adds the smallest durable guardrail that kills
  it — a constraint where one can be built, else a sensor — fired by a time-aware reflection hook (at most
  once per window) so the discipline runs deterministically, not on recall. The skill proposes and scaffolds
  the control; it does not install it.
- **The seam** — Sits over the CENSUS and the blast-radius query. Where the census surfaces a coverage gap
  and the radius bounds a change, INTERPRET turns a gap or a recurrence into an actual new control that lands
  in the REGISTRY and the INDEX below it — the estate not just measuring itself but repairing itself.
- **Limits / durability** — Durable — the recurrence trigger and the periodic hook are model-independent, and
  the preference for a preventive constraint over a detective sensor does not decay. Its soft half — the
  conversion judgment, the taste to keep the control proportionate — is aided but not replaced by a stronger
  model; the hard hook that guarantees the loop fires is deterministic.

### 5. REGISTRY — the governance prose as a queryable model

- **Part** — role:rule-metadata-registry
- **Role in the stack** — Attach machine-readable metadata to each rule in the governing document — its id,
  scope, severity, enforcing check, canonical detail location — and extract those blocks into a typed
  registry.
- **Failure it retires** — A body of governance prose is an opaque wall a program can only grep; "which
  rules have an enforcing check, and which are honor-system" is a question no tool can answer.
- **Mechanism** — Embed a structured metadata block inside each rule and extract them into a typed registry,
  so the governance prose becomes a model the tooling can query — enforced rules, their checks, their
  severities.
- **The seam** — Turns the GRAPH's and CENSUS's implicit knowledge into an explicit, queryable rule model.
  It hands the index below it the machine-readable spine that lets the document be checked against its own
  rules.
- **Limits / durability** — Durable — structured metadata in the rule outlives any one tool. Its cost is the
  per-rule block; it fails only where a rule ships without its metadata, which a presence lint over the
  registry catches.

### 6. INDEX — the governing document as enforced infrastructure

- **Part** — role:claude-md-rule-index
- **Role in the stack** — Treat the top-level governance document as enforced infrastructure: a numbered,
  stable-numbered rule index loaded into every agent's boot context, held honest by its own enforcement
  counterpart.
- **Failure it retires** — The document that carries every other mechanism silently rots — a rule is
  renumbered, bloats past what fits in context, or drifts from the check it names — and every agent boots on
  a lie.
- **Mechanism** — A numbered, stable-numbered index loaded into every agent's boot context, held honest by a
  bloat/cap lint plus a rule-conformance lint, so the governing doc cannot silently decay.
- **The seam** — Closes the stack. It is the delivery surface for everything the registry models: the
  governance the graph maps, the census covers, and the blast-radius query protects is only acted on because
  this index puts it in front of every agent — enforced, capped, and conformance-checked.
- **Limits / durability** — Durable — an enforced, capped rule index is infrastructure, not a 2026
  convenience. Its cost is the discipline of stable numbering and the cap; it fails where a rule is added
  without its enforcement counterpart, which the conformance lint refuses.
