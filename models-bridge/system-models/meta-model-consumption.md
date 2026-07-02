# Meta-model consumption discipline (read, don't hardcode)

**Intent** — Consume the models *by querying them at runtime*, never by embedding a hardcoded snapshot —
so a lint, test, or brief always reasons from the live model, and a copied-out value can't drift behind
the model it was copied from.

| | |
|---|---|
| Summary | Read the model at runtime; never hardcode a snapshot. |
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) · *blocking* — rule #42's forward-policing lint fails on embedded snapshots (verify the named lint is built before relying on it as a live gate) |

## Motivation — the failure it kills

The models are only a bridge if consumers *read* them. The moment a consumer **hardcodes a snapshot** —
"our packages are [A, B, C]" pasted into a lint or test — that copy drifts the instant the model
changes, and the consumer keeps passing while reasoning about a stale world. This is the single most
common **substrate-drift** recurrence vector: the model migrates, the copy is left behind, the check
now verifies the wrong thing. It recurs at every consumer that reaches for a quick literal instead of a
query.

## Why it's not just "hardcode the list" (or "grep for it")

A hardcoded list is a *snapshot*; a queried model is a *source of truth*. With a snapshot, the answer's
authority is duplicated into every consumer and each copy is a future drift bug; with a query, there is
one authoritative answer and consumers *derive* it — so a model change updates every consumer at once.
Grepping the source is no better: it re-implements a fragile parser and couples the consumer to
file layout. The rule is **read the meta-model, never embed a copy** — itself lint-enforced (#42),
because the temptation to snapshot is constant. The distinction is *consume-by-query* versus
*consume-by-copy*.

## Mechanism

Consumers read the models at run/lint-time — via [`repo-query`](query-surface.md) for agents and
orchestration, via direct import for Python tools — rather than embedding values. Rule #33 codifies the
preference (a lint that *reads* the meta-file beats codegen beats a hand-rolled copy); rule #42's
forward-policing lint fails a test that embeds a snapshot of a queryable value; rule #25 has lints
declare their `COMPONENT_TAGS` against the component model rather than hardcoding scope.

## Prerequisites

- **The models are queryable** (they exist and have a read path — the [query surface](query-surface.md)).
- **A lint that bans re-hardcoding** the queryable value, or snapshots creep back in.
- **A consumer culture of deriving, not copying.**

## Consequences & costs

- **Slightly more ceremony per consumer** — a query call instead of a literal (the intended trade).
- **Runtime/lint-time coupling** — the consumer depends on the model being loadable when it runs.
- **The ban-lint's accuracy** — it must recognise a "queryable value" to flag its snapshot (verify it
  is built).

## Known uses

- `components.py` / `repo-query.py` read at runtime by the lint fleet + dispatch.
- Rule #42 (`lint-test-hardcodes-queryable-value.py`, per CLAUDE.md); rule #33; rule #25.

## Related controls

- **Bridge** — this is the *consumption* face: agent controls
  ([dynamic-context-injection](../../agent/context-and-dispatch/dynamic-context-injection.md),
  [docs-hierarchy](../../agent/context-and-dispatch/docs-hierarchy.md)) and product lints
  ([coherence-lints](../../product/validation-and-conformance/coherence-lints.md),
  [doc-hygiene-lints](../../agent/governance-doc-controls/doc-hygiene-lints.md)) all read the models
  through this discipline rather than copying them.
- **Consumer** — [dynamic-context-injection](../../agent/context-and-dispatch/dynamic-context-injection.md)'s
  forward slicer reads the [component-zone model](component-zone-model.md) this way.
- *See also* — [query-surface](query-surface.md): the canonical query path this discipline uses.
