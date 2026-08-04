*A two-page synthesis of the governance-of-governance stack. Six patterns treat the governance system as its
own subject: model the controls as a graph, census which targets are covered, compute a change's blast
radius before making it, convert each recurring failure into a proportionate new control, and hold the
governing document itself as enforced, queryable infrastructure.*

## The capability

**Govern the control estate the way you govern the product — model it, measure its coverage, bound its
changes, and grow it by design.** The stack makes one capability: *govern the control estate itself*. A
fleet accumulates lints, gates, mediators, and registries until the estate is a system in its own right,
with its own failure modes: controls that collide, targets no one guards, substrate changes with unknown
blast radius, and a governing document that rots. The stack turns each of those into a modeled, queryable,
self-repairing fact.

## Failure classes it covers

- **The colliding guardrail.** Two controls contend over one resource — a lock, a file, a queue — and the
  collision surfaces only when they trip each other in production, because nothing modeled that they touch
  the same thing.
- **The blind spot.** A target guarded only by soft aims, or by nothing at all, is discovered the day it
  fails rather than the day the gap opened.
- **The unbounded change.** A cross-cutting substrate change lands blind; a control that silently assumed the
  old shape breaks, and the blast radius was a grep no one ran completely.
- **The re-patched class.** The same failure is fixed locally each time it recurs, so the class survives to
  bite the next agent — and even a team that means to convert it forgets on a long autonomous run.
- **The rotting document.** The doc that carries every other mechanism silently decays — a rule renumbered,
  bloated past what fits in context, or drifted from the check it names — and every agent boots on a lie.

## Composition

<!-- label: governance-of-governance-stack -->
<!-- figure: assets/governance-of-governance-stack.svg | The governance-of-governance stack in one picture. Six parts run left to right. Model the estate (violet): GRAPH represents each control as a node tagged by trigger and resource footprint, with a conflict edge where two controls contend; REGISTRY attaches machine-readable metadata to each governance rule. Query the estate (green): CENSUS classifies each control by the target it guards, so a bare target is a re-derived gap; RADIUS makes each control declare its substrate assumption, so a change's blast radius is a computed query. Grow the estate (green): INTERPRET converts a recurring failure into a proportionate new control, fired on a cadence. Deliver it (accent): INDEX holds the governance document as a numbered, enforced, capped rule index in every agent's boot context. -->

Two parts model the estate, two query it, one grows it, one delivers it. The graph and the registry are the
map the rest of the stack reads.

## The constituent patterns

- **GRAPH — role:governance-graph.** Model the fleet's process-governance mechanisms as a typed graph: each
  control a node tagged by its trigger and its resource footprint, each edge a conflict where two contend
  over one resource — so a collision is caught by construction, at model time.
- **CENSUS — role:control-coverage-census.** Classify every control by which control-target it guards —
  derived from the control's own code anchor, never hand-declared — and roll up per target, so a target with
  zero controls, or only soft ones, is a re-derived coverage gap.
- **RADIUS — role:control-substrate-dependency.** Make each control declare, as typed metadata, the substrate
  assumption it bakes in, so "which controls depend on this part of the substrate, and what breaks if I
  change it" is a computed query run before the change.
- **INTERPRET — role:self-governance.** Convert a recurring failure class into the smallest durable guardrail
  that kills it — a constraint where one can be built, else a sensor — fired by a time-aware hook (at most
  once per window) so the estate grows by design, not by whoever remembers. The skill proposes and scaffolds;
  it does not install.
- **REGISTRY — role:rule-metadata-registry.** Attach machine-readable metadata to each rule in the governing
  document — id, scope, severity, enforcing check, canonical detail location — and extract those blocks into
  a typed registry, so the prose becomes a model the tooling can query.
- **INDEX — role:claude-md-rule-index.** Treat the top-level governance document as enforced infrastructure:
  a numbered, stable-numbered rule index loaded into every agent's boot context, held honest by a bloat/cap
  lint and a rule-conformance lint. The delivery surface for everything the registry models.

## A DocAble example, end to end

DocAble's fleet runs on scores of controls. **GRAPH** models each as a node carrying its trigger and its
resource footprint; when two mediators both take the same host lock, the graph derives a conflict edge and
the collision is caught at model time, not in a production deadlock. **CENSUS** classifies each control by
the target it guards, derived from its code anchor, and rolls up per target — so a target held only by a
soft nudge, with no hard gate, shows up as a bare spot on a queryable coverage map. **RADIUS** has each
control declare the substrate it reads, so before a cross-cutting change to the event bus an engineer queries
exactly which controls depend on it. When a cherry-pick keeps false-rejecting a second time in one session,
**INTERPRET** names the class and scaffolds a proportionate new control instead of re-patching the instance,
fired on a cadence so the conversion is not left to memory. **REGISTRY** carries each governance rule's
metadata as a queryable block, and **INDEX** delivers the whole numbered rule index into every agent's boot
context, capped and conformance-checked so the governing document cannot silently rot.

## Tradeoffs and adoption order

1. **GRAPH and REGISTRY first — model the estate.** Tag each control's trigger and footprint; embed each
   rule's metadata. The graph is only as complete as the controls that register their nodes; the registry as
   honest as the rules that ship their block, held by a presence lint.
2. **CENSUS and RADIUS next — query it.** Both derive from anchors and declarations that move with the code,
   so they do not drift the way a hand-kept list would.
3. **INTERPRET grows it.** Its hard half — the recurrence trigger and the periodic hook — is deterministic;
   its soft half, the taste to keep a new control proportionate, is aided but not replaced by a stronger
   model.
4. **INDEX delivers it, and is durable infrastructure regardless of model.** Its cost is the discipline of
   stable numbering and the cap; a rule added without its enforcement counterpart is the gap, which the
   conformance lint refuses.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
The stack reads the [observe → react loop](appendix-d-observe-react-stack.html) (a recurring alert is a
recurrence INTERPRET converts) and shares its delivery surface with the
[context-management stack](appendix-d-context-management-stack.html) (the rule index is loaded into every
boot there). The full 83-mechanism catalogue is online in the web edition.
