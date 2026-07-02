# Mandatory snippet-table enforcement

**Intent** — A registry of mandatory agent-brief snippets (PATH export, commit-cadence, worktree
discovery, submodule check, …) whose presence is asserted at dispatch by brief-linting, so every
dispatched brief carries the safety and context boilerplate it needs.

| | |
|---|---|
| Target | Agent · **Governance-doc controls** |
| Form | `validation` |
| Novelty | notable |
| Real artifact | the agent-snippet include-table; `agent_prompt_lint.py` |
| Governing rule(s) | The CLAUDE.md *Agent brief snippets — mandatory include table* section |
| Enforcement | **Hard** (deterministic) · *blocking via brief-linting* — a brief missing a required snippet marker fails the pre-dispatch lint |

## Motivation — the failure it kills

Every dispatch needs certain boilerplate to be safe: the PATH export (or 65+ PDF tests fail for lack
of a binary), the commit-cadence discipline, worktree discovery via `$(pwd)`, the submodule check. An
author who forgets one ships an agent that trips exactly that sharp edge 20 minutes in. Without a
*registry* of what's mandatory, "which snippets does this brief need" is tribal knowledge that drifts
as snippets are added — and the failure recurs on every hand-authored brief.

## Why it's not just "tell authors to include the snippets" (a checklist in the docs)

A docs checklist is **advisory and unenforced** — authors skim it and forget, and nothing catches the
omission until the agent fails. The mandatory-snippet **table is a registry that brief-linting reads
and asserts**: each required snippet's marker string must be present in the brief, or the pre-dispatch
lint fails. The distinction is *an enforced registry consumed by a hard lint* versus *an advisory
checklist*. It is the *universal-snippet* analogue of what [dynamic context injection](../context-and-dispatch/dynamic-context-injection.md)
does for file-scoped rules: the table answers "which snippets every brief must carry," DCI answers
"which rules *these files* need."

## Mechanism

The include-table lists each snippet with its include-when condition and its grep-able marker string;
verbatim snippet blocks live in the snippets directory. `agent_prompt_lint.py` greps the brief for the
required markers and exits non-zero on any absence. Some snippets are always-include (worktree-path,
rebase-first); others are conditional on the brief's shape (touches tests, brings up a stack, …).

## Prerequisites

- **A snippet registry with grep-able marker strings** — the lint asserts marker *presence*, so each
  snippet needs a stable marker.
- **The snippet bodies** themselves, kept verbatim so briefs include the current text.
- **An include-when spec** so conditional snippets are required only where they apply.
- **Brief-linting** to do the asserting — this table is inert without its consumer.

## Consequences & costs

- **Verbatim-include means propagation drift.** A snippet updated in the registry must be re-pasted
  into briefs; the marker catches *absence*, not *staleness* of the pasted body.
- **The table is a maintenance surface.** Every new mandatory snippet is a registry row + a lint marker
  + a template thread — drift among them produces false rejections (shared with brief-linting).
- **Over-inclusion bloats briefs.** Requiring a snippet where it doesn't apply adds noise the author
  routes around.

## Known uses

- The agent-snippet include-table (snippet → include-when → marker).
- `agent_prompt_lint.py`'s marker-presence assertions.
- Always-include snippets (worktree-path, rebase-first) vs conditional ones.

## Related controls

- **Consumer** — [brief-linting](../context-and-dispatch/brief-linting.md) reads this table and asserts
  each snippet's marker; this registry is brief-linting's **enabler** (it must exist before the lint can
  check for its markers).
- *See also (sibling)* — [claude-md-rule-index](claude-md-rule-index.md): another governance document
  held honest by a hard counterpart — this one via brief-linting rather than a bloat lint.
- *See also (family)* — [doc-hygiene-lints](doc-hygiene-lints.md): the broader "documentation enforced
  by a lint" family.
