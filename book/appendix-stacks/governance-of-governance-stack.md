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

## The constituent parts

Six parts answer as a set: map the controls as a graph so a collision is caught at model time, census which
targets are held and which are bare, compute what a substrate change will break before you make it, convert
each recurring failure into a proportionate new control, extract the governing rules into a queryable model,
and hold the top-level document itself as enforced, capped infrastructure.

### GRAPH — the control-interaction graph {#a-6-governance-graph}

**GRAPH opens the stack.** It models the fleet's governance mechanisms as a typed graph: each control a node
tagged by the event it fires on and the resources it reads, writes, or locks; each edge a conflict where two
controls contend over one shared resource.

**Receives** — the fleet's existing guardrails: turn-end hooks, pre-commit checks, dispatch gates,
host-level lock mediators. Nothing precedes it; this is the map the rest of the stack reads.

**Guarantees** — collisions caught at model time, not in production. Two controls can place contradictory
demands on one commit-set, or contend for one turn-end slot, and neither one's own code shows it — the
failure lives in the interaction. A conflict edge over a typed, closed resource vocabulary makes that
interaction visible, and a consistency check decides the mechanically-decidable conflicts before a new
control is even wired.

**Hands to CENSUS and RADIUS** — one map, two queries. Because every control is a node with a typed
footprint, the census can roll the nodes up per target and the blast-radius query can walk the substrate
edges. Both read this graph rather than re-deriving the estate from scratch.

→ **Deeper treatment:** role:governance-graph.

### CENSUS — the per-target coverage census {#a-6-control-coverage-census}

**CENSUS asks the coverage question of the map.** It classifies every control by which governance target it
guards — derived from the control's own code anchor, never hand-declared — and rolls the set up per target.

**Receives** — the graph's control nodes. It reads the same typed node-set GRAPH drew, now asking not how
two controls collide but how many guard each target.

**Guarantees** — a re-derived map of the estate's own blind spots. A control portfolio grows toward the last
painful failure, so effort piles onto the target that just hurt while another accretes nothing, and the
imbalance stays invisible because no artifact ever asks whether coverage is balanced. Here a target with
zero controls, or with only soft aims and no hard hold, is a first-class finding. A fail-loud classifier
refuses any control it cannot place, so the map can never silently mis-credit a control to the wrong target.

**Hands to INTERPRET** — a named gap to fill. Where the census surfaces an under-watched target, the
conversion loop downstream turns that gap into an actual new control rather than a noted absence.

→ **Deeper treatment:** role:control-coverage-census.

### RADIUS — the computed substrate blast-radius {#a-6-control-substrate-dependency}

**RADIUS computes what a change will break before you make it.** Each control declares the substrate
assumption it bakes in as typed metadata, so "which controls depend on this part of the substrate, and what
breaks if I change it" becomes a query, not a grep-and-read.

**Receives** — the same controls the graph holds as nodes, now read through their substrate edges. It reads
each control's declared stance toward the substrate it checks against.

**Guarantees** — a computed blast radius. A control usually buries an assumption about its substrate (a
service is a deployment under this directory; the manifest carries this field), invisible until a migration
lands and the fleet fails two silent ways: a false FAIL that blocks every release, or a false PASS where a
migrated thing drops out of every check. Lifting the assumption into a typed declaration makes the importer
and its stance one joinable fact, and a declaration lint refuses any substrate-reading control that leaves it
undeclared.

**Hands to INTERPRET** — bounded change safety. Where the census answers whether a target is covered, the
radius answers what a substrate change will break, so the estate reasons about its own change before
committing to it.

→ **Deeper treatment:** role:control-substrate-dependency.

### INTERPRET — the failure-to-control conversion loop {#a-6-self-governance}

**INTERPRET makes the estate grow by design.** When a failure recurs, it names the failure class and adds
the smallest durable guardrail that kills it (a constraint where one can be built, a sensor otherwise),
firing that conversion on a cadence, not on whoever remembers.

**Receives** — a coverage gap from CENSUS or a bounded risk from RADIUS, plus any failure that recurred this
session. It keys on the recurrence signal: the second occurrence, never the first.

**Guarantees** — a class converted once, proportionately. Re-patching an instance leaves the class alive to
bite the next agent; this closes the class, preferring a constraint that makes the wrong move unrepresentable
over a sensor that merely detects it. Two halves carry it. The conversion judgment is soft: it proposes and
scaffolds, it does not install. A time-aware reflection hook is hard, firing the loop at most once per window
so it aims without decaying into fatigue.

**Hands to REGISTRY and INDEX** — a new control that needs a home. A converted failure becomes a rule or a
check; it must land in the enforced, bounded document below, or the estate grows unindexed and the next
conversion cannot see what exists.

→ **Deeper treatment:** role:self-governance.

### REGISTRY — the queryable rule-metadata registry {#a-6-rule-metadata-registry}

**REGISTRY turns the governing prose into a model.** It attaches a machine-readable block to each rule in
the governance document (identifier, scope, severity, enforcing check, canonical detail location) and
extracts those blocks into a typed registry the tooling can query.

**Receives** — the knowledge the graph and census hold only implicitly, plus every rule the conversion loop
lands. A rule is human prose until its block makes it extractable.

**Guarantees** — governance you can query instead of grep. As long as the rules are only paragraphs, every
aggregate question — which rules have an automated enforcer, which govern this subtree, which are blocking —
is a manual read that rots as the document grows. The metadata block is the bridge: once extracted, a rule
citing an enforcer that no longer exists, or a detail pointer that dangles, is a build finding, so the
document's claims stay reconciled with the system that enforces them.

**Hands to INDEX** — a machine-readable spine. The registry gives the index below it the queryable model
that lets the governing document be checked against its own rules, not merely read by a human.

→ **Deeper treatment:** role:rule-metadata-registry.

### INDEX — the enforced rule index {#a-6-claude-md-rule-index}

**INDEX closes the stack.** It treats the top-level governance document as enforced infrastructure: a
numbered, stable-numbered rule index loaded into every agent's boot context, held honest by its own
enforcement counterpart.

**Receives** — everything the registry models and the conversion loop produces: the rules the estate has
learned, each now a short boot-context statement cross-referenced to the canonical doc that carries it in
full.

**Guarantees** — a governing document that cannot silently rot. The document that carries every other
mechanism fails two ways: it bloats until nothing in it is read, or its rules drift from the canonical docs
they summarize, and both tax every agent, because every agent boots it. A cap lint fails the build when the
index outgrows its scannable budget; a conformance lint fails when a rule stops citing its canonical doc;
and an admission test governs what may enter, so the cap stays satisfiable without evicting real rules.

**Hands off** — the estate's delivery surface. This is why the whole stack matters in practice: the
governance the graph maps, the census covers, and the radius protects is acted on only because the index
puts it in front of every agent — enforced, capped, and conformance-checked.

→ **Deeper treatment:** role:claude-md-rule-index.

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
