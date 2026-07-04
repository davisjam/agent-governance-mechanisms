# Model-driven codegen

**Intent** — Generate real artifacts **from** the models — NetworkPolicy, service catalog, env wiring,
public-API docs, competitor catalog, wire-contract types, docker — each carrying a provenance header, so
the model *drives the system* (not merely describes it) and hand-edits are caught.

| | |
|---|---|
| Summary | Generate real artifacts from the models, provenance-headed. |
| Target | Bridge · **System models** |
| Form | `validation` |
| Enforcement | **Hard** (deterministic) — generated artifacts carry a re-emitted provenance marker + a freshness/drift lint |

## Motivation — the failure it kills

If the models only *described* the system, they would be optional — nice docs, easy to ignore, quick to
drift. The failure this addresses is **a model nothing depends on**: nothing breaks if it's wrong,
so nothing keeps it right. And separately: a *generated* artifact that someone hand-edits loses the edit
on the next regen, silently.

## Why it's not just "hand-write the config / docs"

Hand-writing NetworkPolicy, the service catalog, the API docs, or the competitor analysis means the same
facts live in two places (model + artifact) and diverge. Generating them **from** the model makes the
model authoritative — change the artifact by changing the model — and a **provenance header**
on each generated file, re-emitted every run, plus a freshness lint, ensures a hand-edit is caught and a
stale artifact fails the build. The distinction is *one model, N generated-and-provenance-checked
consumers* versus *hand-maintained artifacts that drift from the model and swallow edits*.

## Mechanism

A family of generators read the models and emit artifacts: a NetworkPolicy generator (from the
service-flow model), the service-catalog and env generators, the web-API entity and public-API-doc
generators (from the web-API model), a competitor-catalog generator (from the competitor registry), the
wire-contract generators (from the wire-contract schemas), and a docker generator. Each emitted file
carries a provenance marker (emitter + regen path), enforced by a provenance-header lint.

## Prerequisites

- **Models rich enough to generate from** (the source-of-truth must contain what the artifact needs).
- **Generators** that re-emit the provenance marker every run.
- **A provenance + freshness lint** so hand-edits and stale artifacts are caught.

## Consequences & costs

- **A generator per artifact class** to author + keep current with the model schema.
- **Generated files must not be hand-edited** — a real constraint (the provenance lint enforces it).
- **Regen discipline** — the artifact must be regenerated when the model changes (the freshness lint
  catches misses).

## Known uses

- The NetworkPolicy, service-catalog, web-API-entity, public-API-doc, competitor-catalog,
  wire-contract, and docker generators.
- The provenance-header requirement + its enforcing lint.

## Related mechanisms

- **Enabler** — the models ([service-flow](service-flow-model.md),
  [domain-registries](domain-registries.md), [deployment-topology](deployment-topology-model.md)) are
  what it generates from; without them there is nothing to generate.
- **Bridge** — this is the *product-facing* face of the models: they don't just inform agents, they
  *build* the codebase's config and docs.
- *See also (cross-target)* — the product [provenance & attribution](https://davisjam.github.io/agent-governance-mechanisms/product/provenance-and-attribution/mutator-stamps.html)
  family: provenance headers here, mutation stamps there — both "the tool records what it produced."
