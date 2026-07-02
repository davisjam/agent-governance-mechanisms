# Sole raw-Redis seam (the dispatch module)

**Intent** — Confine *all* raw-Redis access to one module, with every queue key declared there — so the
queue's atomicity and schema invariants live in exactly one lint-enforced place.

| | |
|---|---|
| Summary | All raw Redis in one seam; queue atomicity encoded once. |
| Target | Product · **Canonical models & seams** |
| Form | `bounded-service` |
| Enforcement | **Hard** (deterministic) · *blocking* — the sole-seam lint bans raw Redis outside the dispatch module |

## Motivation — the failure it kills

Raw Redis calls scattered across the codebase break two invariants at once. **Atomicity**: a
pop-and-move done as `ZPOPMIN` + `LPUSH` (two commands) **silently loses a job** if the worker crashes
between them. **Schema**: key names drift from the declared set, so a metric that reads queue depth
misses a structure. Both recur wherever someone reaches for the raw client.

## Why it's not just "call Redis where you need it"

Scattered raw Redis lets the **atomicity bug class recur** — every non-atomic pop-and-move is a
silent-job-loss waiting for a crash — and lets key names drift from the schema until a depth metric
reads the wrong structures. The dispatch module is the **sole raw-Redis seam**: all keys are declared
there, atomic pop-and-move is encoded once (Lua `EVAL` for sorted sets, `RPOPLPUSH` for lists), and a
lint bans raw Redis elsewhere. The distinction is *a bounded seam that encodes atomicity and schema
once* versus *scattered raw calls that each re-risk the silent-loss bug*. Centralizing is also what
makes "a queue-depth metric must query *all* queue structures" enforceable at all.

## Mechanism

The dispatch module is the one raw-Redis surface; all queue keys are declared in its schema (a flat
re-export name exists as a transitional shim). Pop-and-move is atomic — Lua for ZSETs, `RPOPLPUSH` for
lists — never `ZPOPMIN` + `LPUSH` as two commands. A sole-seam lint bans raw Redis outside the module.

## Prerequisites

- **A single module owning Redis** and a **declared key schema** it is the source of truth for.
- **Atomic operation primitives** (Lua / `RPOPLPUSH`) so pop-and-move can't be two commands.
- **A sole-seam lint** banning the raw client elsewhere.

## Consequences & costs

- **All Redis funnels through one seam** — a coupling point that must cover every queue operation.
- **Transitional debt.** The flat re-export shim for the key schema is a name to eventually retire.
- **The seam must keep pace** with new queue structures, or callers are tempted back to raw access.

## Known uses

- The dispatch module (sole raw-Redis seam) + the queue-key schema.
- Atomic pop-and-move (Lua `EVAL` for ZSETs, `RPOPLPUSH` for lists).
- The sole-raw-Redis-seam lint.

## Related controls

- *See also (sibling)* — [service-client](service-client.md): the same `bounded-service` pattern for
  the cross-service-HTTP boundary — one lint-enforced seam owning a dangerous class of raw calls.
- **Counterpart** — the sole-seam lint (hard) that bans raw Redis outside the dispatch module.
