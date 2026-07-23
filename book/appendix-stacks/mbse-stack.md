### Concept

Model-based systems engineering for an agent fleet: a context-bounded agent operates a
context-exceeding codebase by reasoning *through* a typed map of the system rather than by reading
the whole territory. The map only earns that trust while it stays equal to the territory — so the
models and the machinery that pins them to reality travel as one package. Adopt the models without
the drift control and you have ship a lie the fleet will act on.

### Mandatory members

- **role:executable-source-of-truth** — the models are plain typed data the tools import and execute,
  not prose that narrates a diagram. A query returns the live shape; a stale sentence cannot.
- **role:synchronization-model** — a meta-sync contract that names, for each model, what reality it
  mirrors and when it must be re-derived. Without it the map drifts silently the first time the code
  moves underneath it.
- **role:drift-parity-gates** — the deterministic check that fails the build when a model and its
  subject disagree. This is the member that makes the map trustworthy: it converts "the model is
  probably right" into "the model is right or the gate is red." Drop it and every other member
  degrades into optimistic documentation.

### Complementary members

- **role:query-surface** — a typed query CLI over the models. It makes the map *convenient* to
  consult, which raises how often agents actually reason through it, but the stack is correct without
  it.
- **role:model-driven-codegen** — generate the boilerplate the model implies. Value on top, not a
  precondition; a model can be a source of truth that is read, not one that emits code.
- **role:coverage-model-mapping** — map which model invariants are actually exercised by a test, so
  an untested invariant is visible. Sharpens the map's honesty; layers on rather than holds it up.
