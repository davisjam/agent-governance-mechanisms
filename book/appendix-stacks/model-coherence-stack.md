*A flagship deep-dive: the model-based-engineering stack, walked part by part. A context-bounded agent
cannot read a whole codebase, so it reasons through a typed map of the system. The map earns that trust
only while it stays equal to the territory — so the models and the machinery that pins them to reality
travel as one package. This page folds in what used to be the separate MBSE and canonical-seam stacks.*

## The goal

**Let an agent reason through a typed map of the system instead of the whole territory — and keep the map
equal to the territory, so what the agent queries is what is true.** Adopt the models without the drift
control and you ship a map the fleet will trust while it quietly lies. Six parts make the map executable,
read live, held equal to the code, derived where a derived edge cannot drift, generated back into the
system, and — on the product side — the single sanctioned door through which a shipped format is mutated.

<!-- label: model-coherence-stack -->
<!-- figure: assets/model-coherence-stack.svg | The model-coherence stack in one picture. Six parts run left to right in two capability lanes. Authoritative knowledge (fleet blue): DATA models the system as executable typed data; CONSUME reads it live and never snapshots; EMIT generates artifacts back from the model. Equal to reality (governed green): PARITY fails the build when a model and reality disagree either way; DERIVE anchors every model-to-code edge on a resolvable symbol a lint re-checks, so a derived edge cannot drift. SEAL (accent) routes all mutation of a shipped format through one typed model held sole by a ban-lint. The map is executable, read live, held equal to the territory, and generated back into it. -->

## How the parts interlock

Each part is weak alone; coherence emerges from the chain. **DATA** makes the system's structure
machine-readable so a program can act on it. **CONSUME** keeps that structure authoritative by reading it
live — one value, never a copy. **PARITY** is the keystone: it fails the build when the map and the
territory disagree, turning "probably right" into "right or red." **DERIVE** is the highest rung of parity
— anchor an edge on a resolvable symbol and the join is *derived*, so it cannot drift. **EMIT** turns the
model from a thing that is read into a thing that produces the territory. **SEAL** applies the same
one-canonical-representation discipline to a shipped format: one typed door, held sole by a ban-lint. Read
the parts in that order; each seam names what the part before it hands over.

## The parts

### 1. DATA — the executable source of truth

- **Part** — role:executable-source-of-truth
- **Role in the stack** — Model the system as typed data the tools import and execute on every run, not
  prose that narrates a diagram.
- **Failure it retires** — The system's structure lives only in prose and diagrams; a program cannot read
  it, so it drifts from the code the moment the code moves and no one notices.
- **Mechanism** — Each model is machine-readable typed data a tool loads on every run and generates real
  artifacts from — executable documentation a query returns live where a stale sentence cannot.
- **The seam** — Opens the stack. It hands every part below it a typed object to stand on: the consumer
  queries it, the parity gate checks it against reality, the codegen emits from it, the traceability graph
  anchors its edges to it.
- **Limits / durability** — Durable — typed data outlives any one model runtime and any 2026 context
  limit; its cost is the discipline of keeping structure as data, not prose. It is worth nothing without
  the parity gate that holds it equal to reality.

### 2. CONSUME — read the model, don't copy it

- **Part** — role:meta-model-consumption
- **Role in the stack** — Read the model by querying it at runtime; never embed a hardcoded snapshot of
  what it says.
- **Failure it retires** — A consumer copies a fact out of the model into its own code; the copy and the
  model diverge silently, and the consumer acts on a value the model no longer holds.
- **Mechanism** — Every consumer resolves the fact it needs by querying the live model, so there is one
  authoritative value and no second copy to fall out of date.
- **The seam** — Sits on the DATA. It is what makes "source of truth" true in practice — the model is
  authoritative only because its consumers read it live rather than snapshotting it, so the parity gate
  downstream has one value to check, not many copies to reconcile.
- **Limits / durability** — Durable — read-don't-copy is a discipline, not a model capability, and it costs
  a query in place of a constant. It fails only where a consumer smuggles a snapshot, which a
  copy-detecting lint catches.

### 3. PARITY — the drift gate that keeps the map honest

- **Part** — role:drift-parity-gates
- **Role in the stack** — Fail the build when a model and the reality it mirrors disagree, in either
  direction.
- **Failure it retires** — The map drifts from the territory: a model row points at a thing that no longer
  exists, or a real thing on disk has no model row, and the fleet reasons through a map that quietly lies.
- **Mechanism** — A fleet of deterministic lints enforces bidirectional parity — every model row resolves
  to a real thing, and every real thing has its row — plus a meta-sync contract naming, per model, what
  reality it mirrors and when it must be re-derived.
- **The seam** — The keystone. It converts "the model is probably right" into "the model is right or the
  gate is red," so the executable data, its live consumers, and the emitted artifacts above it can all be
  trusted. Drop it and each degrades into optimistic documentation.
- **Limits / durability** — Durable — a deterministic check over declared pairs does not decay. Its cost is
  a gate per model; its reach is exactly the parity rules authored, which the traceability graph raises by
  deriving edges the gate would otherwise assert by hand.

### 4. DERIVE — traceability edges that cannot drift

- **Part** — role:symbol-anchored-traceability-graph
- **Role in the stack** — Link every model to its lint, its code entry-point, its proof, and its related
  models as a typed graph whose every edge a lint re-checks.
- **Failure it retires** — The connections between a model and the code it governs live in someone's head;
  when the code moves, the model-to-code link breaks invisibly and no gate fires.
- **Mechanism** — Each edge terminates on a resolvable symbol, never a line number, and is a derived
  obligation a lint re-checks at scan time — so a moved symbol that breaks an edge becomes mechanically
  visible.
- **The seam** — The highest rung of parity. Where the gate *asserts* a model matches reality, the graph
  *derives* the join so parity is unnecessary for those edges — a derived edge cannot drift, because moving
  the code either keeps the symbol resolvable or reddens the scan.
- **Limits / durability** — Durable — symbol-anchored edges survive refactors that line numbers would not.
  Its cost is authoring the edges once; it fails only where an edge is declared but never re-checked, which
  the graph's own lint forbids.

### 5. EMIT — the model drives the system

- **Part** — role:model-driven-codegen
- **Role in the stack** — Generate real artifacts from the model — policy, wiring, catalogs, contract types
  — each carrying a provenance header.
- **Failure it retires** — The boilerplate the model implies is written by hand beside the model; the two
  fall out of step, and the generated-looking file is silently stale or hand-edited.
- **Mechanism** — A generator emits each artifact *from* the model with a provenance header declaring its
  emitter, so the model drives the system rather than merely describing it and a hand-edit is caught on
  regen.
- **The seam** — Consumes the DATA the way a compiler consumes a source file. It turns the model from a
  thing that is read into a thing that *produces* the territory, which is what lets the parity gate treat
  the generated artifact as derived, not as a second source to reconcile.
- **Limits / durability** — Durable — codegen from a typed model is standard practice; its cost is the
  generator plus the provenance-header discipline. It fails where an emitted file is hand-edited, which the
  header's regen lint reverts.

### 6. SEAL — one typed door for the product (folded from the canonical-seam stack)

- **Part** — role:pdf-model
- **Role in the stack** — Route all reads and writes of a complex file format through one structured model,
  with raw library access ban-linted away.
- **Failure it retires** — Mutation of a format happens through many raw library calls; there is no single
  place to encode the format's invariants, so a malformed write can land from any of a hundred sites.
- **Mechanism** — One typed model is the sole mutation surface for the format and a ban-lint forbids the raw
  library, so the structure is compiler-checked and every change passes a surface that encodes the format's
  invariants (our instance: a PDF model over the canonical PDF library).
- **The seam** — Closes the stack on the product side. It is model-coherence applied to a shipped artifact:
  one canonical typed representation, held sole by a ban-lint, so a fix to an invariant holds everywhere at
  once — and it is the single door the provenance stack's stamp-writer needs to cover.
- **Limits / durability** — Durable and model-independent — a typed seam plus a ban-lint is deterministic
  infrastructure. Its cost is building the model and migrating every call site; it weakens only where a raw
  call escapes the ban, which the lint is there to catch.
