<!--
  System-models starter kit — MBSE authoring scaffolds (adopt & adapt)

  A distilled, portable version of the model-based-systems-engineering (MBSE) discipline from a
  production system built by frontier coding agents. The catalogue *documents* the system-models as
  pattern entries; this kit ships the fill-in scaffolds a fresh project uses to author its OWN model
  views. Everything here is blank + portable — replace the TODO markers, keep the disciplines.
-->

# System-models starter kit — author your typed model views

**What this is.** A set of fill-in scaffolds for building the *typed model layer* of an
agent-collaborative codebase — the layer an operating agent reasons THROUGH. It is MBSE
(model-based systems engineering) applied at the scale of an autonomous fleet: the model is the
typed **source of truth** for what the system *is*, realized as a small set of **views**, each kept
equal to the code by a build-time drift check.

You are meant to *extend the model / author a view* — not fill in a boilerplate form. The difference
matters: a boilerplate form is copied and rots; a model view is a typed surface that tools read on
every run, so it fails the build the moment it disagrees with the code.

---

## What MBSE buys you here

An agent has a bounded context window; your codebase does not fit in it. The model is the interface
that lets a context-**bounded** agent operate a context-**exceeding** codebase: instead of reading
280k lines to answer "what talks to what," the agent queries a typed model that already knows. The
model is only trustworthy if it *cannot lie* — which is the whole point of the drift check below.

The classic decomposition is the **4+1 architectural views** (Kruchten): four views onto the system
plus the scenarios that tie them together. Each view answers a different question, and each maps to a
concrete artifact you author with a scaffold in this kit.

| 4+1 view | Question it answers | The artifact you author | Scaffold |
|----------|---------------------|-------------------------|----------|
| **Logical** | What are the parts and how do they relate? | A typed component/zone catalogue | `component-zone-model-starter.py` |
| **Development** | How is the code organized into modules/owners? | The same component catalogue (focus-dirs + owner + tags) | `component-zone-model-starter.py` |
| **Process** | What runs concurrently, and what are the states/races? | A composed state-machine model (states, seams, invariants) | `state-machine-model-starter.py` |
| **Physical** | What is deployed where, and at what scale? | A deployment-topology model derived from the deploy manifest | `deployment-topology-starter.py` |
| **Scenarios (+1)** | How do the parts collaborate over a real request? | A service-flow model (Backstage entity dialect) | `service-flow-model-starter.yaml` + loader |

You do **not** need all five to start. Author the one view where a real failure lives (see the
scoping rule next), and add views only as failures demand them.

---

## The scoping rule — realize ONLY the view where a failure lives

This is the hardest-won lesson, so it leads: **do not model everything.** A model view earns its keep
only where a failure class actually lives, and a view you author "for completeness" is pure carrying
cost — every future agent must read it, and it drifts the moment nobody's failure depends on it.

The canonical discipline: a fleet models the *one concurrency view* where a data race actually lives —
the worker/queue/lease part with interleaving actors and shared mutable state — and **deliberately
refuses** to model the stateless request/response parts, which have no race to catch. There is no
spanning "model of everything"; the seams between views ARE the boundary, and each seam is reached as a
single typed edge, not modeled through.

Practically, when you reach for a scaffold, first name the failure class:

- **A concurrency race / torn multi-step mutation / stale-state read** → author the **process view**
  (state-machine model). This is the highest-leverage view: distributed bugs live in interleavings a
  static reading never surfaces.
- **"An agent keeps mis-scoping which module owns X" / cross-zone audit gaps** → author the
  **logical/development view** (component-zone model).
- **"What calls this service, with what timeout / auth / request cap?"** → author the **scenarios
  view** (service-flow model).
- **"Deploy replicas / scale drifted from the manifest"** → author the **physical view** (deployment
  topology).

If you can't name the near-certain failure a view would catch, you don't need the view yet. Refusing
to model is a first-class design act — it keeps the model layer from becoming a tower of governance
nobody can keep true.

---

## The two load-bearing disciplines (+ the drift-lint contract)

Every scaffold in this kit is built around two rules and one contract. Follow them and your model
"cannot drift"; break them and you've built a snapshot that lies within a week.

### (a) Look up, don't copy

A model's transition table, component list, or seam set is **derived from the code at build time** —
never a hand-copied snapshot. If the authoritative states live in a code enum, the model *reads that
enum* at import time and projects it; it does not re-type the state names. A hand-copied list is a
second source of truth that silently desyncs the first time someone edits one and not the other.

The scaffolds show this as a `_load_..._from_code()` stub: the model file imports the authoritative
source by path and reads its symbols, so the model surface is always a *projection* of the code, not a
parallel transcription of it.

### (b) Derive, don't hand-type

Any field that is a *function of other model data* is **computed**, not authored. The worked example:
a "verification tier" (which kind of checker an invariant needs) is derived from the invariant's own
shape — the number of concurrent lanes it touches and the shape of its temporal predicate — never
typed in by hand per invariant. A hand-typed derived field is a lie waiting to happen: someone edits
the inputs, the stored value goes stale, and now the model asserts something false. Store the derived
value for queryability if you like, but let a single derivation function own the truth, and assert the
stored value equals the derivation.

### The drift-lint contract — what makes a model "can't drift"

A model view is only trustworthy if a **stable build-time check reads both the model and the code and
fails on divergence.** This is the one gate the rest of the model layer depends on: without it, the
model is prose that rots; with it, the model is executable documentation the build keeps honest.

The contract each scaffold sketches (as a `__main__` drift-lint sketch you wire into your build):

1. Load the model's declared view (its states / components / seams).
2. Load the authoritative code source the same way the model does (rule *a*).
3. Set-diff the two. Any element in one and not the other is a finding.
4. Re-run every *derived* field's derivation (rule *b*) and assert it equals the stored value.
5. Exit non-zero on any finding, so the build blocks a divergent model.

Run this check on every build. The instant the code and the model disagree, the build breaks — which
is exactly what turns "documentation" into "a map that provably equals the territory."

---

## The scaffolds — author this view when…

| File | View | Author it when… |
|------|------|-----------------|
| [`state-machine-model-starter.py`](state-machine-model-starter.py) | Process | you have a concurrency race, a torn multi-step mutation, or a stale-state read — the highest-leverage view. Pairs with the *formal-invariant-verification* mechanism: each invariant's temporal shape derives which exhaustive checker proves it. |
| [`component-zone-model-starter.py`](component-zone-model-starter.py) | Logical / development | agents keep mis-scoping which module owns what, or you want per-zone audit sweeps. |
| [`service-flow-model-starter.yaml`](service-flow-model-starter.yaml) + [`service-flow-loader-starter.py`](service-flow-loader-starter.py) | Scenarios | you need typed inter-service contracts (callers, timeouts, auth, request caps). Adopts the Backstage entity schema — the canonical genre — while skipping its runtime. |
| [`deployment-topology-starter.py`](deployment-topology-starter.py) | Physical | deploy replicas / scale keep drifting from the manifest; derive them, don't re-annotate. |

Start with the view whose failure you can name today. Add the drift-lint the same day you add the
view — a model without its drift check is the debt, not the asset.
