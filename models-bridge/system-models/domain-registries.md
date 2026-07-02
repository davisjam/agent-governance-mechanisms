# Domain registries

**Intent** — A set of frozen, typed registries for the system's *domain facts* — the supported
filetypes, the WCAG coverage gaps, the periodic-GC cron entries, the UX write-authority surfaces, the
competitor set, the CLAUDE.md rule metadata — each the single source of truth for its slice.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `typed-ir` |
| Novelty | standard |
| Real artifact | `supported_filetypes.py` · `wcag_coverage_gaps.py` · `cron_entries.py` · `ux_surfaces.py` · `competitors/` · `claude-md-rules.py` |
| Governing rule(s) | Each registry's charter; consumed by dispatch, checkers, generators, and their parity lints |
| Enforcement | **Hard** (deterministic) — typed registries *held true* by their coverage/parity lints |

## Motivation — the failure it kills

Domain facts — "which four filetypes do we support," "which WCAG SCs are coverage-gaps," "which cron
entries run," "who may write UX surface X," "who are our competitors," "what metadata does each
CLAUDE.md rule carry" — get restated in code, docs, and dashboards. Restated, they drift: a filetype
list diverges, a rule's metadata goes stale, a competitor doc is out of date. Each is a small
correctness or a stale-doc failure, multiplied across many domain slices.

## Why it's not just "hardcode each list where it's used"

A hardcoded domain list is a snapshot that drifts and can't be queried as a set. Each registry is the
**frozen typed source of truth** for its slice, read by the tools that need it and *generated into* the
docs that present it (the competitor catalog → competitive-analysis doc; the rule metadata → rule
index). A coverage/parity lint keeps each honest. The distinction is *one typed registry per domain
fact, consumed and validated* versus *scattered hardcoded snapshots*.

## Mechanism

Each is a small typed model: `supported_filetypes.py` (the frozen four), `wcag_coverage_gaps.py` (the
gap registry, feeding the WCAG-scope status), `cron_entries.py` (periodic-GC — distinct from the
per-minute merge-train), `ux_surfaces.py` (frontend write-authority), `competitors/` (Backstage-style
Competitor dialect → competitive-analysis doc), `claude-md-rules.py` (rule metadata extracted from
inline `<!-- rule-meta: -->` blocks, feeding the [rule-index](../../agent/governance-doc-controls/claude-md-rule-index.md)).
Each has a coverage/parity lint + a doc-derived pin.

## Prerequisites

- **A typed registry per domain fact** with the fields its consumers need.
- **Consumers that read it** (dispatch/checkers/generators) rather than hardcoding.
- **A coverage/parity lint + a doc-derived pin** per registry.

## Consequences & costs

- **Many small registries to maintain** — the cost is breadth, not depth; each is simple but each is a
  surface.
- **Frozen sets resist expedient edits** — changing "the supported four" is a deliberate model change.

## Known uses

- `supported_filetypes` · `wcag_coverage_gaps` · `cron_entries` · `ux_surfaces` · `competitors/` ·
  `claude-md-rules`.
- Their generators (e.g. competitor catalog → `gen-competitive-analysis.py`) and coverage/parity lints.

## Related controls

- **Bridge** — agents/checkers *read* these facts (agent side) ◀──▶ they *govern & generate* product
  surfaces (WCAG scope, competitor docs, cron behaviour) (product side).
- **Consumer** — `claude-md-rules` feeds the
  [rule-index](../../agent/governance-doc-controls/claude-md-rule-index.md); `wcag_coverage_gaps` feeds
  the [standards rule-engine](../../product/validation-and-conformance/standards-rule-engine.md).
- **Counterpart** — [drift-parity-gates](drift-parity-gates.md): each registry's coverage/parity lint.
