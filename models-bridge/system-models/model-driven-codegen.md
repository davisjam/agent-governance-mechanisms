# Model-driven codegen

**Intent** — Generate real artifacts **from** the models — NetworkPolicy, service catalog, env wiring,
public-API docs, competitor catalog, wire-contract types, docker — each carrying a provenance header, so
the model is *load-bearing* (not merely descriptive) and hand-edits are caught.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `validation` |
| Novelty | notable |
| Real artifact | `gen-*` generators (`gen-network-policies`, `gen-service-catalog`, `gen-web-api-entities`, `gen-public-api-doc`, `gen-competitive-analysis`, `gen-wire-contracts`) · `docker_codegen.py` |
| Governing rule(s) | **#35** (auto-generated files carry a provenance header; hand-edits will be overwritten) |
| Enforcement | **Hard** (deterministic) — generated artifacts carry a re-emitted provenance marker + a freshness/drift lint |

## Motivation — the failure it kills

If the models only *described* the system, they would be optional — nice docs, easy to ignore, quick to
drift. The failure this addresses is **a model that isn't load-bearing**: nothing breaks if it's wrong,
so nothing keeps it right. And separately: a *generated* artifact that someone hand-edits loses the edit
on the next regen, silently.

## Why it's not just "hand-write the config / docs"

Hand-writing NetworkPolicy, the service catalog, the API docs, or the competitor analysis means the same
facts live in two places (model + artifact) and diverge. Generating them **from** the model makes the
model load-bearing — change the artifact by changing the model — and a **provenance header** (rule #35)
on each generated file, re-emitted every run, plus a freshness lint, ensures a hand-edit is caught and a
stale artifact fails the build. The distinction is *one model, N generated-and-provenance-checked
consumers* versus *hand-maintained artifacts that drift from the model and swallow edits*.

## Mechanism

`gen-*` generators read the models and emit artifacts: `gen-network-policies` (from service-flow),
`gen-service-catalog` / `gen-service-env`, `gen-web-api-entities` + `gen-public-api-doc` (from web-api),
`gen-competitive-analysis` (from `competitors/`), `gen-wire-contracts` + the C# wire codegen (from
`wire-contracts/`), `docker_codegen`. Each emitted file carries the rule-#35 provenance marker (emitter
+ regen path), enforced by `lint-autogen-files-have-provenance-header.py`.

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

- `gen-network-policies` · `gen-service-catalog` · `gen-web-api-entities` · `gen-public-api-doc` ·
  `gen-competitive-analysis` · `gen-wire-contracts` · `docker_codegen`.
- Rule #35's provenance header + `lint-autogen-files-have-provenance-header.py`.

## Related controls

- **Enabler** — the models ([service-flow](service-flow-model.md),
  [domain-registries](domain-registries.md), [deployment-topology](deployment-topology-model.md)) are
  what it generates from; without them there is nothing to generate.
- **Bridge** — this is the *product-facing* face of the models: they don't just inform agents, they
  *build* the codebase's config and docs.
- *See also (cross-target)* — the product [provenance & attribution](../../product/provenance-and-attribution/mutator-stamps.md)
  family: provenance headers here, mutation stamps there — both "the tool records what it produced."
