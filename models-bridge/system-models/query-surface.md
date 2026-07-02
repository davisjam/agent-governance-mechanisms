# Model query surface (`repo-query`)

**Intent** — One canonical, self-describing query API over all the models — `repo-query.py` with
deterministic `--json` subcommands — so an agent reads the system's compressed truth *through a tool*
rather than parsing raw files, and the tool itself documents how the models load.

| | |
|---|---|
| Target | Bridge · **System models** |
| Form | `agent-output` |
| Novelty | notable |
| Real artifact | `repo-query.py` (self-describing `models` command + ~15 subcommands, `--json`) |
| Governing rule(s) | The `repo-query` charter ("lives here so the tool documents how the models are loaded"); the `repo-query` skill |
| Enforcement | **Soft** (probabilistic) — the canonical *read convenience* agents/orchestration use; it emits structured `--json` (deterministic) but doesn't block raw reads |
| Summary | repo-query — the agent-facing read API over the models. |

## Motivation — the failure it kills

The models are the agent's compressed map of the codebase — but only if the agent can *read them
cheaply and correctly*. Left to `cat`/`grep` the model files, an agent (or a tool) re-implements
loading + traversal, gets the dialect subtly wrong, and produces brittle one-offs. The failure is
*ad-hoc, error-prone model access* — which undermines the whole point of having a queryable map.

## Why it's not just "import the model / cat the file"

Direct import works for Python tools, but agents and the orchestrator need a **stable, self-describing
query interface** — not to re-derive how services or components load each time. `repo-query.py` is that
surface: deterministic subcommands (`component`, `service-flow`, `frontend-flow`, `design`, `callers`,
`xrefs`, `epic`, `task`, …) with a `--json` contract, and it *lives in* `system-models/` so its
top-of-file import pattern is the documented canonical example of loading the models. The distinction is
*a self-describing, structured query API an agent acts on* versus *each consumer re-implementing model
access*.

## Mechanism

`repo-query.py` exposes a `models` meta-command (self-describing) plus ~15 subcommands over the model
set, each with atomic writes where relevant and a `--json` mode so downstream agents consume structure,
not prose (an `agent-output` contract). It is the read half of the bridge — the agent-facing surface
over the models the codebase is governed by.

## Prerequisites

- **The models exist and load cleanly** (the substance being queried).
- **A stable subcommand + `--json` contract** so agents can act on the output.
- **The loader pattern documented** (here, by co-locating the tool with the models).

## Consequences & costs

- **Not a sole seam** — Python tools still import models directly; `repo-query` is the *canonical*
  read/query path for agents + orchestration, not a lint-banned monopoly. So it's a Soft convenience,
  not a Hard gate.
- **Subcommand surface to maintain** as models are added.

## Known uses

- `repo-query.py` — `models` / `component` / `service-flow` / `frontend-flow` / `design` / `callers` /
  `xrefs` / `epic` / `task` / `web-api` / `config` subcommands (`--json`).
- The `repo-query` skill (orchestrator-facing).

## Related controls

- **Bridge** — this is the *agent-facing* face of the models: how a bounded agent reads the unbounded
  codebase's compressed truth.
- **Consumer** — reads every model here; e.g. [component-zone](component-zone-model.md),
  [service-flow](service-flow-model.md).
- *See also* — [meta-model-consumption](meta-model-consumption.md): the discipline of reading the model
  (not a hardcoded copy) — `repo-query` is the canonical way to do it.
