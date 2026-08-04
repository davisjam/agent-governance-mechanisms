*A two-page synthesis of the model-coherence stack. Six patterns let a context-bounded agent reason through
a typed map of the system instead of the whole territory — and keep the map equal to the territory, so what
the agent queries is what is true.*

## The capability

**Give a bounded-context agent a typed map it can reason through, and hold that map equal to the code so the
map never lies.** The stack makes two capabilities: *maintain authoritative system knowledge*, and *keep
representations equal to reality*. The models are executable data, not prose — read live, checked against
reality by a gate, derived where a derived edge cannot drift, and generated back into the system. An agent
that cannot hold the whole codebase queries the map instead, and the map is trustworthy because machinery,
not hope, keeps it current.

## Failure classes it covers

- **The prose that drifts.** Structure lives only in diagrams and sentences; a program cannot read it, so it
  falls out of step the moment the code moves and no one notices.
- **The stale snapshot.** A consumer copies a fact out of the model into its own code; the copy and the model
  diverge silently, and the consumer acts on a value the model no longer holds.
- **The map that lies.** A model row points at a thing that no longer exists, or a real thing on disk has no
  row, and the fleet reasons through a map that quietly disagrees with the code.
- **The broken join.** The link between a model and the code it governs lives in someone's head; the code
  moves, the link breaks invisibly, and no gate fires.
- **The hand-edited generated file.** Boilerplate the model implies is written by hand beside it; the two
  fall out of step and the generated-looking file is silently stale.
- **The hundred raw writes.** Mutation of a format happens through many raw library calls, so a malformed
  write can land from any of a hundred sites with nowhere to encode the format's invariants.

## Composition

<!-- label: model-coherence-stack -->
<!-- figure: assets/model-coherence-stack.svg | The model-coherence stack in one picture. Six parts run left to right in two capability lanes. Authoritative knowledge (fleet blue): DATA models the system as executable typed data; CONSUME reads it live and never snapshots; EMIT generates artifacts back from the model. Equal to reality (governed green): PARITY fails the build when a model and reality disagree either way; DERIVE anchors every model-to-code edge on a resolvable symbol a lint re-checks, so a derived edge cannot drift. SEAL (accent) routes all mutation of a shipped format through one typed model held sole by a ban-lint. The map is executable, read live, held equal to the territory, and generated back into it. -->

The stack has two lanes. Three parts make the map authoritative — model it as data, read it live, generate
from it. Two parts hold it equal to reality — a parity gate and derived edges. One part seals the same
discipline onto a shipped product format.

## The constituent patterns

- **DATA — role:executable-source-of-truth.** Model the system as typed data the tools import and execute on
  every run, not prose that narrates a diagram. It hands every part below it a typed object to stand on.
- **CONSUME — role:meta-model-consumption.** Read the model by querying it at runtime; never embed a
  hardcoded snapshot of what it says. This is what makes "source of truth" true in practice — one
  authoritative value, no second copy to age.
- **PARITY — role:drift-parity-gates.** Fail the build when a model and the reality it mirrors disagree, in
  either direction. The keystone: it converts "the model is probably right" into "the model is right or the
  gate is red."
- **DERIVE — role:symbol-anchored-traceability-graph.** Link every model to its lint, its code entry-point,
  its proof, and its related models as a typed graph whose every edge terminates on a resolvable symbol a
  lint re-checks. A derived edge cannot drift — moving the code either keeps the symbol resolvable or reddens
  the scan.
- **EMIT — role:model-driven-codegen.** Generate real artifacts from the model — policy, wiring, catalogs,
  contract types — each carrying a provenance header, so the model *produces* the territory rather than
  merely describing it and a hand-edit is caught on regen.
- **SEAL — role:pdf-model.** Route all reads and writes of a complex file format through one structured
  model, with raw library access ban-linted away (our instance: a typed model over the canonical PDF
  library). Model-coherence applied to a shipped artifact — one canonical representation, so a fix to an
  invariant holds everywhere at once.

## A DocAble example, end to end

DocAble's PDF remediation is where SEAL earns its place. Every tag-tree read and write routes through one
typed PDF model; a ban-lint forbids raw calls to the underlying library, so the format's invariants live in
exactly one place and a fix holds across every call site at once. The surrounding lanes govern the wider
system. The component-and-zone model, the job-lifecycle machines, the domain registries are all **DATA** —
executable, not prose. Tools **CONSUME** them live: a check resolves "which service owns this seam" by
querying the model, never by a copied constant. **PARITY** gates fail the build if a model row names a
service that no longer exists, or a service ships with no row. **DERIVE** anchors each model-to-code edge on
a symbol, so a refactor that moves the code reddens the scan instead of silently breaking the link. And
**EMIT** regenerates catalogs and wiring from the models with provenance headers, so the generated files
cannot quietly fall behind their source.

## Tradeoffs and adoption order

1. **DATA and CONSUME are the floor.** Typed data plus read-don't-copy costs a query in place of a constant.
   Without them there is no model to keep honest.
2. **PARITY is mandatory, not optional.** The executable data is worth nothing without the gate that holds it
   equal to reality; drop it and every model degrades into optimistic documentation. Its cost is a gate per
   model.
3. **DERIVE raises the ceiling.** Where the gate *asserts* a match, derived edges make parity unnecessary for
   those joins — symbol-anchored edges survive refactors that line numbers would not.
4. **EMIT and SEAL are targeted.** Codegen pays off where the model implies boilerplate; the sealed format
   model pays off on a complex shipped format, at the cost of building the model and migrating every call
   site.

The whole stack leans on one presumption: consumers read live and mutations route through the sanctioned
surface. A smuggled snapshot or an escaped raw call is where it weakens — each held by its own lint.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
The stack is the substrate under the
[provenance + fidelity stack](appendix-d-provenance-fidelity-stack.html) (its sanctioned door is this
stack's sealed seam) and the
[specification + verification stack](appendix-d-specification-verification-stack.html) (whose state machines
are DATA this stack keeps honest). The full 83-mechanism catalogue is online in the web edition.
