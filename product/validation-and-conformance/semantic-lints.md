# Blocking semantic lints

**Intent** — A fleet of blocking semantic lints over the tool's *own source* — banned APIs, silent-catch
bans, config-field discipline, sole-seam violations — that fail the build on domain-invariant
violations the compiler and review can't catch.

| | |
|---|---|
| Target | Product · **Validation & conformance** |
| Form | `validation` |
| Novelty | standard |
| Real artifact | the `lint-*` semantic-lint fleet (e.g. `lint-banned-apis`, `no-silent-catch`, config-field lints) |
| Governing rule(s) | Many — **#8** (never silent-catch) · **#9** (banned APIs) · **#5** (config field in sample) · **#25** (lints declare `COMPONENT_TAGS`/`SEVERITY`), … |
| Enforcement | **Hard** (deterministic) · *blocking* — each BLOCKING lint fails the build; escape is a scoped `noqa` with a reason |
| Summary | The blocking semantic-lint fleet over the tool's own source. |

> **This entry represents the fleet, not each lint.** Per the README scope note, the ~500+ individual
> custom lints are a *magnitude reported in prose*; this is the one entry for the pattern.

## Motivation — the failure it kills

The codebase carries hundreds of structural invariants — no silent `catch`, no banned API in prod, every
config field present in the sample JSON, every cross-boundary call through its seam. Code review cannot
reliably enforce hundreds of invariants, and the compiler enforces none of them (a silent catch, a
banned API, a missing config field all compile fine). The failure is *structural drift that quietly
reintroduces a defect class*, and it recurs continuously as code is written.

## Why it's not just "code review" (or "rely on the compiler")

The compiler checks *types*, not *domain invariants*: a `catch {}` that swallows an error, a
`Console.WriteLine` in prod, a config field missing from the sample (which then silently defaults to
`false` and collapses batching) all type-check. Review misses them because they look normal. Semantic
lints **encode the domain invariant** and fail the build. The distinction is *domain-invariant
enforcement* versus *the compiler (types only) plus review (unreliable)* — this is the "move audits to
lints" and "enforce structure with analysis when available" discipline made concrete.

## Mechanism

The lint fleet runs at commit and deploy. Each lint declares its `COMPONENT_TAGS`, `SEVERITY`, and a
verb-of-checking docstring (#25); BLOCKING ones fail the build, AUDIT-ONLY ones surface. Escapes are
scoped `# noqa: <ban-name> — <reason>` comments. The fleet sits atop a maxed-out commodity floor
(Roslyn analysis, pyright strict, ruff) rather than replacing it.

## Prerequisites

- **A lint framework** with per-lint scope + severity declaration (#25).
- **The invariants made mechanically detectable** — a rule you can't express as a check can't join.
- **A runner wired into the gates**, and a scoped escape hatch for legitimate exceptions.

## Consequences & costs

- **A large maintenance surface.** Hundreds of lints are hundreds of things to keep current; this is
  the very "500+ lints" magnitude that the support-apparatus ratio counts.
- **False positives need escapes.** A too-strict lint blocks legitimate code until a `noqa` is added —
  a small, audited hole.
- **Floor vs fleet.** The custom fleet only earns its keep atop the commodity analysis floor; without
  that floor the grade rests on the wrong thing.

## Known uses

- `lint-banned-apis`, `no-silent-catch`, the config-field-in-sample lints, the sole-seam ban-lints.
- Rule #25's declaration discipline; the scoped `noqa` escape convention.

## Related controls

- *See also (sibling)* — [coherence-lints](coherence-lints.md): relational lints across sources;
  [content-validator](content-validator.md) / [standards-rule-engine](standards-rule-engine.md): the
  other artifact validators.
- **Counterpart** — the ban-lints in [canonical-models-and-seams](../canonical-models-and-seams/pdf-model.md)
  are members of this fleet doing the "hold a construction seam in place" job.
