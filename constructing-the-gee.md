<!-- summary: The construction kit for a Governed Engineering Environment — 8 principles, 9 capabilities, 25 canonical mechanisms, 8 compositions, and the variants and known uses that fold under them. -->

# Constructing the Governed Engineering Environment

*A catalogue of models, controls, compositions, and known uses.*

The entries in this catalogue are not seventy independent design patterns. They are the concrete
machinery of a **governed engineering environment**: the models an agent fleet reasons through, the
surfaces it acts through, the evidence its work must produce, and the loops that convert a failure into a
control. This page is the map of that machinery. It names what the environment must be able to **do**, the
canonical mechanisms that give it those capabilities, the stacks that are strong together, and the
concrete variants each mechanism was built from.

## The two theses, built

The book develops two claims. The **Modeling Thesis** says an agent works coherently when intent and
system structure are bound into a compact, checkable representation it can reason through. The **Alignment
Thesis** says implementation stays trustworthy when the environment mechanically holds it to those
representations and the policies they express. The catalogue is what those two theses look like once you
build them. Every capability below serves one thesis or the other, and most serve both.

## The claim this catalogue makes

The DocAble case produced <!--census:controls-->82<!--/census--> concrete governance mechanisms.
Comparative analysis reduced them to **25 canonical mechanisms** under **9 capabilities**. The rest are
retained, not discarded: **54 variants and known uses** fold under a parent mechanism, **2 pairs merge**
into one, and **1 entry rises** to a principle that explains where the others sit. The reduction is the
finding. Where several entries solve the same problem through the same structure, they are one idea worn
several ways, and the catalogue says so instead of counting each dress as a concept.

The merge rule was strict. Two mechanisms collapse only when they share the same failure, obligation,
structure, guarantee, semantic level, and tradeoffs, differing only in where they were used. They stay
distinct when the **relation** they model or enforce differs, even when both are "a lint" or both are "a
model." All lints are not one pattern. All models are not one executable model. That guard is what keeps
the 25 honest.

## Four levels, not one

The entries do not sit at a single altitude, so the catalogue reads them at four levels.

- **Capabilities** — what the environment must accomplish. Nine of them. They **organize** the catalogue;
  they are not themselves entries.
- **Canonical mechanisms** — the reusable structure that supplies a capability. Twenty-five. This is the
  intellectual core: an executable source of truth, a drift gate, a sanctioned mutation surface, a
  re-derived completion gate.
- **Compositions** — mechanisms that are stronger stacked than alone. Eight named stacks.
- **Variants and known uses** — the concrete realizations that give the case its texture: a PDF mutation
  model, an `N=1` test lock, per-mutator stamps. They preserve how it was actually built without earning
  separate conceptual status.

## Not the Gang of Four's subject

The closest predecessor in form is *Design Patterns*, but the subject has moved. The Gang of Four
catalogued recurring structures **inside** an object-oriented program: how objects collaborate. This
catalogue describes recurring structures in the **environment that produces and maintains** a system with
agents. Its questions are different ones. What state is authoritative? Where may an agent act? What
evidence does a change owe? Which properties must stay invariant? How does a failure that happened once
become a control that fires on every change after it? The commonality among the entries is functional, not
formal: each supplies a capability the environment requires.

---

<a id="principles"></a>
# The eight principles

The principles are the deep claims that explain the catalogue. They are not entries you install; they are
the reasons the mechanisms take the shapes they do. One entry, the placement judgment, was lifted out of
the mechanism set to sit here as a principle in its own right.

- **P1 · Bind intent to structured models.** The environment's authoritative knowledge lives in typed
  models the fleet reasons through, not in prose or scattered code. Intent and structure are represented
  so a bounded-context agent can operate a system it cannot hold in view. *Expressed by the whole
  [Maintain authoritative system knowledge](#cap-know) capability.*

- **P2 · Reconcile models with reality.** A model is trustworthy only while it equals the territory. Every
  authoritative representation owes a mechanical check that it still matches the code it describes.
  *Expressed by [Keep representations equal to reality](#cap-sync).*

- **P3 · Constrain action through sanctioned surfaces.** Bound a probabilistic actor by making the unsafe
  move impossible to represent. Route mutation through one typed surface, express authority and repair as
  closed vocabularies, and hold each with a ban-lint. *Expressed by
  [Constrain where and how agents act](#cap-constrain).*

- **P4 · Re-derive evidence rather than trust reports.** Establish completion by recomputing evidence,
  never by trusting an actor's self-report. The gate re-runs the checks itself. *Expressed by
  [Establish completion on re-derived evidence](#cap-complete).*

- **P5 · Convert recurring failures into enforced controls.** A failure that recurs is converted, once,
  into a deterministic control that fires on every later change. Audit findings become lints; the memory
  moves out of the reviewer and into the substrate. *Expressed across most of the catalogue, and directly
  by [Machine-Enforced Semantic Policy](#m-semantic-policy).*

- **P6 · Preserve provenance and accountability.** Every inserted artifact and every consequential action
  carries a durable, machine-checkable trace back to its cause, so a change can be explained, audited, and
  reversed. *Expressed by [Track provenance and trace causes](#cap-provenance).*

- **P7 · Model the governance environment itself.** Once controls proliferate, the control estate is a
  system in its own right, and it must be modeled, covered, and reasoned over. Governance of governance.
  *Expressed by [Govern the control estate itself](#cap-govern).*

- **P8 · Enforce at the right semantic level.** A control must fire where the property actually lives — a
  structural property gets a deterministic check, a semantic one gets a model or a judge — and it must be
  as legible as the failure it prevents. This is the placement judgment that explains where every other
  mechanism sits. It began as a catalogue entry,
  [Enforce at the right semantic level](agent/governance-doc-controls/semantic-level-enforcement.md), and
  was lifted to a principle.

---

# The nine capabilities

Each capability names a job the environment must do, then lists the canonical mechanisms that do it. Under
each mechanism are the variants and known uses that fold into it — preserved, subordinated, each a real
case of *this* mechanism rather than a sibling's.

<a id="cap-know"></a>
## KNOW · Maintain authoritative system knowledge

*Represent intent and structure in typed models the fleet reasons through.*

**[Executable Source of Truth](models-bridge/system-models/executable-source-of-truth.md).** Keep the
authoritative knowledge as machine-readable typed data that is continuously consumed and mechanically held
true. It is the interface through which a bounded agent operates an unbounded system. *The scar:* a stale
architecture paragraph that no longer matched the code, so agents reasoned from a lie. *Built as:* a typed
system-models bridge projected as data, not code, and held true by build-time gates.
*Known uses (subject models that share the declare-typed-data-plus-parity structure, each preserving its
own relation):*
[service-flow](models-bridge/system-models/service-flow-model.md) ·
[user-journey](models-bridge/system-models/user-journey-model.md) ·
[component & zone](models-bridge/system-models/component-zone-model.md) ·
[domain registries](models-bridge/system-models/domain-registries.md) ·
[data-flow](models-bridge/system-models/data-flow-model.md) ·
[deployment topology](models-bridge/system-models/deployment-topology-model.md) ·
[synchronization](models-bridge/system-models/synchronization-model.md) ·
[concurrency contracts](models-bridge/system-models/concurrency-contracts.md) ·
[process view](models-bridge/system-models/process-view.md) ·
[typed contract surfaces](models-bridge/system-models/typed-contract-surfaces.md) ·
[timeout-budget ordering](models-bridge/system-models/timeout-budget-ordering-model.md) ·
[required-config-per-role manifest](models-bridge/system-models/required-config-per-role-manifest.md) ·
[telemetry-collection provenance](models-bridge/system-models/telemetry-collection-provenance.md) ·
[rule-metadata registry](models-bridge/system-models/rule-metadata-registry.md) ·
[agent-orchestration model](models-bridge/system-models/agent-orchestration-model.md) ·
[lifecycle model](models-bridge/system-models/lifecycle-model.md) ·
[invariant-DAG execution policy](models-bridge/system-models/invariant-dag-execution-policy.md) ·
[model-driven codegen](models-bridge/system-models/model-driven-codegen.md) ·
[agent-first MBSE harness](models-bridge/system-models/agent-first-mbse-harness.md).

**[Read the Model, Don't Copy It](models-bridge/system-models/meta-model-consumption.md).** Consumers
derive answers from the live model at use time; the copied-out value is banned. One authoritative answer
holds, and a model change updates every consumer at once. *The scar:* a value snapshotted out of the model
drifted from it, silently disabling a check keyed on the stale copy. *Built as:* a ban-lint that flags
copied-out values on policed paths.
*Known uses:*
[model query surface](models-bridge/system-models/query-surface.md) (the ergonomic read API) ·
[model-graded finding severity](models-bridge/system-models/model-graded-finding-severity.md) (a
model-consuming gate — see the [borderline fold](#folds) below).

**[Composed State-Machine Model](models-bridge/system-models/composed-state-machine-model.md).** Author
the concurrency composition as one checkable object: which lifecycles exist, how they compose, and the
predicates that must hold across them, each predicate carrying a derived verification obligation. *The
scar:* two async lifecycles, legal alone, deadlocked when composed, and no single-machine model could see
it. *Built as:* typed lifecycle machines with cross-machine invariants — the specification a formal
verifier runs against.

<a id="cap-sync"></a>
## SYNC · Keep representations equal to reality

*Reconcile the model against the code it describes, and catch drift mechanically.*

**[Drift / Parity Gate](models-bridge/system-models/drift-parity-gates.md).** Keep the map equal to the
territory in both directions. A build-blocking parity predicate fails the moment the model or the reality
drifts alone. *The scar:* a moved directory silently staled every tool's private inference of the tree.
*Built as:* bidirectional parity lints wired into the build; divergence either way fails it.
*Known uses (the same model-versus-reality relation over different source pairs):*
[doc-hygiene lints](agent/governance-doc-controls/doc-hygiene-lints.md) (corpus versus its index) ·
[coherence lints](product/validation-and-conformance/coherence-lints.md) (cross-source relational
parity) ·
[DDT pin-trailers](product/regression-tests/ddt-pin-trailers.md) (a test versus the source it cites).

**[Derived Traceability](models-bridge/system-models/symbol-anchored-traceability-graph.md).** Make every
cross-layer join a typed edge re-proven against live reality at read time. A derived edge cannot drift; a
stored one silently can. Liveness is a property of the representation — resolution *is* the read — not a
sync job running beside a stored graph. *The scar:* a stored traceability edge went stale, claiming a join
reality had already severed. *Built as:* symbol-anchored edges that redden at scan time when the anchor no
longer resolves. This is the rung above a parity gate: remove the store, and drift has nowhere to live.

<a id="cap-constrain"></a>
## CONSTRAIN · Constrain where and how agents act

*Sanctioned mutation surfaces, closed action vocabularies, and enforced semantic policy.*

**[One Door Enforced](product/canonical-models-and-seams/pdf-model.md).** Route all mutation of a
hazardous resource through one typed surface that encodes its invariants, with the raw alternative
structurally banned. The bug is made unrepresentable, not reviewed for. *The scar:* a raw library call
bypassed a format's invariants and shipped a corrupt tag tree. *Built as:* a single sanctioned mutation
model, with a ban-lint holding every call site off the raw library.
*Known uses (the same one-door relation over different resources):*
[Office models](product/canonical-models-and-seams/office-models.md) (a second object model, so a fix
serves every format) ·
[the raw-Redis seam](product/canonical-models-and-seams/raw-redis-seam.md) (shared state plus schema) ·
[the typed service client](product/canonical-models-and-seams/service-client.md) (its signature is the
enforcement) ·
[canonical walkers](product/canonical-models-and-seams/canonical-walkers.md) (one traversal per tree).

**[Closed Action Vocabulary](product/repair-vocabulary/remediation-verbs.md).** Make the actor's
move-space a closed, named, typed set. Bounding the action space is what makes attribution, validation,
and policy tractable at all; an absent action forces a deliberate addition to the vocabulary. *The scar:*
an open-ended repair space made attribution and validation unanswerable, because anything could have
happened. *Built as:* a closed, typed set of remediation verbs — every mutation is one named verb.
*Known uses:*
[typed categories](product/repair-vocabulary/typed-categories.md) (a closed enum with exhaustiveness as
the checkable property) ·
[role-typed dispatch](agent/context-and-dispatch/role-typed-dispatch.md) (the same move applied to
authority) ·
[codemod-first](product/repair-vocabulary/codemod-first.md) (an execution-mode vocabulary for bulk
change).

<a id="m-semantic-policy"></a>
**[Machine-Enforced Semantic Policy](product/validation-and-conformance/semantic-lints.md).** Encode every
mechanically-detectable domain invariant as a blocking check with scoped, reason-bearing escapes. Audits
become lints; policy moves out of reviewer memory and into durable machinery. The agentic force is sharp
here: agents produce violations faster than a human can review them. *The scar:* a policy that lived in a
reviewer's memory was violated the moment the reviewer became a fleet — and worse, one checker became the
hazard, a runaway regex whose fix was deleting the surface, not linting the bug. *Built as:* a fleet of
blocking semantic lints with scoped, reason-bearing suppressions.

<a id="cap-admit"></a>
## ADMIT · Admit or reject changes

*Gate the work order, and gate the path to production.*

**[Validated Dispatch](agent/context-and-dispatch/brief-linting.md).** Structurally validate the
instruction packet that confers autonomy before granting it. A work order that launches an autonomous
actor is checked deterministically at the point of no return, not by probabilistic review. *The scar:* a
brief missing its isolation marker launched an agent that edited the mainline directly, and the failure
surfaced downstream, not at authoring. *Built as:* a deterministic pre-dispatch lint over the brief, wired
into the sole launch path; a failing check refuses the launch.
*Known uses:*
[the mandatory-snippet table](agent/governance-doc-controls/mandatory-snippet-table.md) (the registry the
lint reads) ·
[epic and design templates](agent/governance-doc-controls/epic-and-design-templates.md) (the same
schema-on-the-artifact move applied to planning).

**[Staged Admission Gates](agent/gates-and-merge-train/staged-deploy-gates.md).** Order verification
cheap-to-expensive along the path to production, each rung independently re-checkable, so no user meets an
unverified build and a predictably doomed run never starts. *The scar:* an unverified build reached users
because the expensive check ran only after promotion. *Built as:* a canary-to-smoke-to-promote staircase
on traffic-free surfaces.
*Known uses (the rungs, each a distinct sub-idea):*
[the pre-commit hook](agent/gates-and-merge-train/pre-commit-hook.md) (tree-sha markers make "checks ran
green on this tree" replay-proof) ·
[the sentinel first-commit](agent/gates-and-merge-train/sentinel-first-commit.md) (fail-fast at minute
one) ·
[merge-train MIS batching](agent/gates-and-merge-train/merge-train-mis-batching.md) (independence proved
before integration) ·
[the cron-alerts gate](agent/lifecycle-and-observability/cron-alerts-gate.md) (a health signal promoted to
a barrier) ·
[test-onion tiers](product/regression-tests/test-onion-tiers.md) (the cost stratification the rungs
consume).

<a id="cap-complete"></a>
## COMPLETE · Establish completion on re-derived evidence

*Recompute completion; derive the assurance obligation from the model.*

**[Re-Derived Definition of Done](agent/governance-doc-controls/epic-definition-of-done.md).** Establish
completion by independently re-derived evidence against the current state, never by a recorded assertion.
Trust nothing written down before now. *The scar:* an effort marked itself done while its owned checks had
rotted and its commits never actually landed. *Built as:* a close tool that re-runs every owned check and
verifies commit ancestry against the substrate as it stands.

**[Model-Derived Assurance Coverage](models-bridge/system-models/model-derived-test-obligation-census.md).**
Derive the assurance obligation from the model itself — the surface that should be tested, the tier, the
assertion strength, the verification method — and lint the gap, so an untested obligation is a named
finding whose set regrows with every model change. *The scar:* a green coverage percentage hid an entire
untested category of obligations. *Built as:* an obligation census that draws the owed-test denominator
from the models and lints the shortfall.
*Known uses (five distinct obligations, not one):*
[coverage-to-model-node mapping](models-bridge/system-models/coverage-model-mapping.md) (per-node
exercise) ·
[journey-criticality test placement](models-bridge/system-models/journey-criticality-test-placement.md)
(the tier) ·
[journey task-closure](models-bridge/system-models/journey-task-closure.md) (the assertion strength) ·
[formal invariant verification](models-bridge/system-models/formal-invariant-verification.md) (the
verification method — see the [borderline fold](#folds) below).

**[Generative Validation](product/regression-tests/fuzz-campaigns.md).** Falsify a specification with
machine-generated inputs at two poles: invariant-shaped properties over tame inputs, and wild adversarial
inputs fixed to the stable point in the spec. In its deepest form the structured model is the oracle,
which collapses the usual tradeoff between a rich oracle and wild inputs. *The scar:* a fix aimed at a
failing fuzz seed passed that seed and still broke every other spec-allowed input. *Built as:* fuzz
campaigns with root-cause analysis to the stable spec point, plus property tests at the tame pole.
*Merged in:* [property tests](product/regression-tests/property-tests.md) — the two entries self-framed as
two sides of one coin, so they are one mechanism with two poles.

<a id="cap-preserve"></a>
## PRESERVE · Preserve product semantics

*Guarantee the product's meaning survives mutation and conforms to spec.*

**[Preservation Invariant](product/validation-and-conformance/content-validator.md).** Make semantic
preservation a deterministic post-condition checked on every produced artifact: the input's content must
survive as a subset of the output. A per-stage variant names the stage that lost it. *The scar:* a
remediation pass silently dropped document content — it ran successfully and produced garbage. *Built as:*
a validator that checks input-subset-output on every artifact, with a staging variant that localizes the
offending pass. This is where damage done *through* the one sanctioned door is caught.

**[Conformance-to-External-Spec Engine](product/validation-and-conformance/standards-rule-engine.md).**
Make conformance a deterministic predicate in which every finding names the external-standard clause it
closes, and keep the coverage claim honest — covered, gap, or aspirational — by a same-commit discipline.
*The scar:* an opaque conformance score could not be defended clause by clause when a claim was
challenged. *Built as:* a standards rule engine where each finding cites its clause and coverage is
tracked explicitly.

<a id="cap-provenance"></a>
## PROVENANCE · Track provenance and trace causes

*Durable, complete, checkable attribution of every mutation and its cause.*

**[Caused-By Provenance](product/provenance-and-attribution/mutator-stamps.md).** Attach durable
attribution at the point of every mutation, and check that the wiring is complete over a closed verb set,
so the artifact's mutation history — who changed what, and why — reconstructs on demand. *The scar:* an
input-versus-output diff could say *what* changed but never *who* or *why*, so a remediation could not be
explained or reversed. *Built as:* per-mutator stamps embedded at the mutation site, one sanctioned writer
per format. This is a composed stack presented as one mechanism, with named components:
[the `a11y_` prefix](product/provenance-and-attribution/a11y-prefix.md) marks the insertion and
auto-registers it for validation ·
[per-mutator stamps](product/provenance-and-attribution/mutator-stamps.md) emit at the site ·
[the F10 wiring lint](product/provenance-and-attribution/f10-wiring-lint.md) covers every verb ·
[`derive-changelog`](product/provenance-and-attribution/derive-changelog.md) reads the attributed history
back ·
[caused-by provenance](agent/lifecycle-and-observability/caused-by-provenance.md) is the agent-side arm,
every commit carrying a typed cause from a closed taxonomy.

<a id="cap-manage"></a>
## MANAGE · Manage work, state, and resources

*Lifecycle records, resource mediation, and fleet observation.*

**[Authoritative Lifecycle State](agent/lifecycle-and-observability/agent-registry.md).** Make destructive
lifecycle decisions consult an authoritative recorded fact of liveness and disposition, never an inference
from side effects. The record precedes the reclaim. *The scar:* a cleanup heuristic inferred an agent was
dead from filesystem signals and destroyed a live worktree mid-run. *Built as:* an append-only registry
consulted before any reclaim; tools refuse to operate on an agent whose live marker exists.
*Known uses:*
[tombstone commits](agent/lifecycle-and-observability/tombstone-commits.md) (the close-record variant: an
irreversible reclaim justified by a durable close record with an explicit disposition).

**[Mediated Resource Admission](agent/mediators-and-resource-locks/test-serializer.md).** Mediate
shared-resource use through a single admission point at a chosen cardinality — exclusive for destructive
work, bounded for parallel-safe-heavy work — with the raw unmediated path structurally impossible and the
permitted seams declared in a model so a coverage lint detects every bypass. *The scar:* concurrent agents
ran the destructive test runner at once and corrupted each other's shared build state. *Built as:* an
`N=1` host flock on the test runner, the raw path banned, coverage checked against a declared
concurrency-contracts model.
*Known uses (cardinality variants of one relation):*
[the build-serializer](agent/mediators-and-resource-locks/build-serializer.md) (bounded `M=8`) ·
[aggregate-compute protection](agent/mediators-and-resource-locks/aggregate-compute-protection.md) (a
whole-sweep singleton).

**[Adaptive Resource-Pressure Admission](agent/mediators-and-resource-locks/resource-pressure-gating.md).**
Admit and continue heavy work only under bearable live conditions. One shared pressure signal is read both
when work is admitted and while it runs, so a red host neither starts new heavy work nor is left running
it. *The scar:* fixed concurrency slots still let heavy work pile onto a host already thrashing, because
the count was fine but the machine was not. *Built as:* one shared pressure signal read at admit and
during execution, shedding on red. This is the adaptive pole, split from the fixed-capacity mediator by
its obligation and guarantee, not merged with it.

**[Fleet Observability Surface](agent/lifecycle-and-observability/typed-event-bus.md).** Make operational
health a queryable, typed, typo-proof signal surface, and bind every signal to a prescribed response.
Emission alone is not observability; the loop is emit, interpret, react. *The scar:* operational failures
scrolled past in free-form logs that carried neither their meaning nor a response. *Built as:* an
orchestrator-as-reactor over a typed event bus, topics enumerable, each bound to a playbook.
*Known uses:*
[deploy heartbeats](agent/lifecycle-and-observability/deploy-heartbeats.md) (the progress-liveness
variant: no heartbeat for N windows reads deterministically as stale).

**[Point-of-Action Policy Delivery](agent/lifecycle-and-observability/lifecycle-hooks.md).** Deliver the
constraint that governs an action to the actor at the moment of action. A runtime lifecycle event fires
the check deterministically, converting policy from available-if-pulled to binding-because-pushed. *The
scar:* a step owed at a runtime moment depended on the actor remembering it, and was silently skipped.
*Built as:* lifecycle hooks — turn-stop, compaction, session-start, pre-action — split into guaranteed
firing and a payload that blocks or aims.
*Known uses:*
[dynamic context injection](agent/context-and-dispatch/dynamic-context-injection.md) (the feed-forward
variant: slice the meta-substrate to just the rules governing the change-target) ·
[the reflection-facet substrate](agent/lifecycle-and-observability/reflection-facet-substrate.md) (the
feed-back variant: soft nudges under one shared attention budget).

<a id="cap-govern"></a>
## GOVERN · Govern the control estate itself

*Model, cover, and encode the governance system as its own subject.*

**[Governance Graph](models-bridge/system-models/governance-graph.md).** Model the control system itself —
governance mechanisms as typed conflict edges over a closed shared-resource vocabulary — so a proposed
control's collisions are checkable at authoring, not at the tripwire. *The scar:* two controls claimed the
same slot with no ordering, colliding only when both fired in production. *Built as:* a typed interaction
model in which mechanically-decidable conflict classes are caught by construction.
*Known uses:*
[the control-coverage census](models-bridge/system-models/control-coverage-census.md) (the coverage lens
of the same governance-of-governance subject).

**[Computed Control Blast Radius](models-bridge/system-models/control-substrate-dependency.md).** Every
control declares the substrate assumption it bakes in as a typed fact, so "what breaks when I change this
substrate" is a computed query before the change, not archaeology after. *The scar:* a substrate migration
silently broke controls whose dependency on it lived only in someone's memory. *Built as:* per-control
typed substrate declarations; blast radius is a query over them.

**[Governed Knowledge Base](agent/governance-doc-controls/claude-md-rule-index.md).** Govern the document
that carries the governance. The boot-context map of the rules must itself be bounded, canonical — one
home per rule — admission-gated, and mechanically enforced. The delivery vehicle for every converted
failure is itself under mechanism. *The scar:* the governance index grew unbounded and its citations
rotted, so agents booted from a map that no longer matched the rules. *Built as:* a size-capped,
admission-gated rule index with stable citable numbering and cross-reference integrity lints.
*Merged in:* [the docs hierarchy](agent/context-and-dispatch/docs-hierarchy.md) — the boot-context lens of
the same bounded canonical index, two lenses on one artifact.

**[Encoded Operational Judgment](agent/governance-doc-controls/operational-playbooks.md).** Pre-reason each
recurring operational situation once, when nothing is burning: encode the trigger, the ordered steps, and
the reflexes to avoid. Lead with the positive model of how the substrate works healthy, generate the
runbook from a typed source of truth, and keep it honest by reference validation. *The scar:* an operator
improvised a recovery under fire and took a reflex the situation punishes, because the judgment lived in no
one's reach at the moment of need. *Built as:* situation-keyed playbooks, plus an operator runbook
generated from the lifecycle model with every pointer ref-checked.
*Known uses:*
[the operator runbook skill](agent/governance-doc-controls/operator-runbook-skill.md) (the generated,
symptom-indexed, positive-model-first variant).

<a id="folds"></a>
### Two borderline folds, kept as named variants

Two entries were folded, but their distinction is worth preserving, so each surfaces as a named variant
inside its parent.

- **Formal invariant verification** folds under **Model-Derived Assurance Coverage** as the *proof* pole
  against the census's *exercise* pole. It routes each invariant to the checker its temporal shape
  demands, proving a property across bounded interleavings or returning a counterexample. It composes with
  the Composed State-Machine Model — the model is the specification, this is the checker.
- **Model-graded finding severity** folds under **Read the Model, Don't Copy It** as a model-consuming
  gate. It computes a finding's severity as a function of the finding and the change, once, against the
  live component model — a strong instance of reading the model to grade, rather than a canonical
  mechanism of its own.

---

# The eight compositions

Some mechanisms are strong together. A composition is not a bigger pattern nor six unrelated ones; it is a
stack whose members reinforce each other.

- **The model-coherence stack** — [Executable Source of Truth](#cap-know) + [Drift / Parity
  Gate](#cap-sync) + [Read the Model, Don't Copy It](#cap-know). A model is authoritative only when it is
  read live and held equal to reality. The three together turn data-not-code into a source of truth that
  cannot silently drift. Derived Traceability is the highest rung — derive the join so parity is
  unnecessary.

- **The provenance and fidelity stack** — [One Door Enforced](#cap-constrain) + [Caused-By
  Provenance](#cap-provenance) + [Preservation Invariant](#cap-preserve). Routing every mutation through
  one door makes complete provenance feasible; stamps feed a derived changelog; the preservation invariant
  catches damage done through the sanctioned seam. Seam, stamps, wiring-lint, changelog, validator.

- **The specification and verification stack** — [Composed State-Machine Model](#cap-know) +
  [Model-Derived Assurance Coverage](#cap-complete). The composed model is the specification; formal
  invariant verification is the checker routed by the invariant's temporal shape. Spec plus prover, proven
  across interleavings or refuted by a counterexample.

- **The safe-launch stack** — [Validated Dispatch](#cap-admit) + [Closed Action Vocabulary](#cap-constrain).
  The dispatch lint validates the work order; role-typed authority fixes what the launched actor may do.
  Pre-authorization of autonomy is a well-formed order plus bounded authority.

- **The evidence staircase** — [Staged Admission Gates](#cap-admit) + [Re-Derived Definition of
  Done](#cap-complete). The pre-commit gate binds cheap checks to an exact tree so a later stage can check
  rather than trust; the re-derived Definition of Done recomputes the full evidence at close. Cheap
  evidence early, full re-derivation late, never a trusted self-report.

- **The observe-then-react loop** — [Fleet Observability Surface](#cap-manage) + [Encoded Operational
  Judgment](#cap-govern) + [Staged Admission Gates](#cap-admit). A typed event bus emits and interprets; a
  playbook binds each signal to a response; the cron-alerts gate promotes a critical signal into a barrier.
  Emit, interpret, react, gate.

- **The resource-mediation pair** — [Mediated Resource Admission](#cap-manage) + [Adaptive
  Resource-Pressure Admission](#cap-manage). Fixed-capacity mediation bounds the *count* of admitted heavy
  work; adaptive pressure gating bounds by the live *condition* of the host and sheds during. Split by
  forces and guarantees, they bound compute on both axes.

- **The governance-of-governance stack** — [Governance Graph](#cap-govern) + [Computed Control Blast
  Radius](#cap-govern) + [Governed Knowledge Base](#cap-govern). Once controls proliferate they become a
  system: the graph models their conflicts, the blast-radius model computes what a substrate change breaks
  across them, and the governed knowledge base keeps the rule index that carries every control honest.

---

# How to read the rest

No system needs every entry. This page is the repertoire; the [full census](INDEX.md) lists every
mechanism by role and family, and each links to its full writeup. Choose by the failures, risks, and
assurance obligations of the system in front of you. If you cannot name the failure a mechanism prevents in
*your* system, you may not need it yet.
