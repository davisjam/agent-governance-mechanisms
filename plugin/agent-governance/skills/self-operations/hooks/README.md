# The reflection-hook library — a runnable, portable substrate

*A self-contained, stdlib-only Claude Code hook library. Copy this whole `hooks/`
directory into your `.claude/`, wire the Stop hook, and adapt the example facets.
This is the runnable complement to the catalogue's
[reflection-facet-substrate](../../../../../agent/lifecycle-and-observability/reflection-facet-substrate.md)
mechanism and the [L6 · govern-your-own-loop](../examples/lifecycle-L6-govern-your-own-loop.md)
lifecycle model.*

## The pattern

Some judgments you *mean* to make every session — "did this failure recur, so should
I harden the class?", "does this lesson belong in durable memory or in a runbook?" —
are exactly the ones thin attention skips when they matter most. The fix is a **hook
that fires the skipped reflex at its moment**, biased hard toward silence so it aims
without nagging.

The trouble starts at the *second* such hook. N independent nudges a turn is noise;
the operator tunes them all out, and every nudge dies together. So this library
consolidates them into ONE tempo-gated substrate:

- **A `ReflectionFacet` Template-Method base** (`reflection_facet.py`) fixes the
  reflect algorithm — `classify → snapshot → check_policy_material → build_payload →
  route_followup` — and each facet overrides only the virtual steps. A facet cannot
  re-implement or bypass the shared machinery (a closed surface).
- **A typed facet registry** — one place says which facets exist (`FacetKey`, an
  enum, not free strings).
- **A shared emitter** (`hook_reflection_turn_end.py`) drives all facets of a tempo
  class through **one window**, round-robins among them, and emits **at most one
  reflection per window**. Adding a facet does not raise the reflection *rate* — it
  only changes which dimension a given window's single reflection covers.

Two example facets ship, both generic:

- **`reflection_facet_recurrence.py`** — the `failure_control` facet. On a turn-end,
  "did the same failure surface ≥2× this session? convert the *class* into a control
  (lint / gate / typed seam / test), don't just re-patch the instance."
- **`reflection_facet_memory_routing.py`** — the `knowledge_routing` facet. On a
  memory-file write, "is this a true one-off, or durable know-how that belongs in a
  shared runbook / design doc instead?"

## Files

| File | Role |
|---|---|
| `reflection_facet.py` | The Template-Method base + typed registry + the types (`FacetKey`, `ReflectionTempo`, `RoutedFollowup`, `MaterialPointer`, `ReflectionResult`). The core — port this faithfully. |
| `hook_reflection_turn_end.py` | The runnable **Stop** hook (the ON_TURN_END emitter): the ≤1-per-window round-robin gate + dedupe flag + telemetry. |
| `reflection_facet_recurrence.py` | Example facet: failure→control (ON_TURN_END). |
| `reflection_facet_memory_routing.py` | Example facet: memory-vs-runbook routing (ON_MEMORY_WRITE). |
| `reflection_turn_end_query.py` | The measured-leash query (per-facet firing + silence counts). |
| `_hook_harness.py` | Minimal self-contained Claude Code hook harness (stdin parse + decision emit). No project coupling. |
| `settings.snippet.json` | How to register the Stop hook + set the kill-switch / window env vars. |

## How to wire it

1. **Copy** this `hooks/` directory into your project's `.claude/` (say
   `.claude/hooks/reflection/`).
2. **Register the Stop hook.** Merge the `hooks` block from `settings.snippet.json`
   into `.claude/settings.json`, fixing the `command` path. The Stop hook drives the
   ON_TURN_END facets — the failure→control nudge works with no further config.
3. **(Optional) wire the memory-routing facet.** It fires on the `ON_MEMORY_WRITE`
   tempo — a `PostToolUse` `Write|Edit` into your private-memory store. Set
   `REFLECTION_MEMORY_DIRS` to your store's absolute path(s) (os.pathsep-joined), and
   add a sibling `PostToolUse` emitter that drives the `ON_MEMORY_WRITE` facet the
   way `hook_reflection_turn_end.py` drives the ON_TURN_END ones (per-path dedupe
   instead of a shared window). Until you point it at a store it is a safe no-op.
4. **Verify it runs** (no Claude Code needed):
   ```
   echo '{"session_id":"demo"}' | python3 hook_reflection_turn_end.py
   ```
   The first call emits `{"decision":"block","reason":"🛠 FAILURE→CONTROL …"}`; a
   second call within the window emits nothing (the dedupe). A firing line lands in
   `reflection-turn-end-telemetry.jsonl`.

The Claude Code Stop contract: the event JSON arrives on **stdin**; a
`{"decision":"block","reason":…}` on **stdout** re-prompts the assistant with
`reason` as an injected message (the nudge). Emitting nothing lets the turn end. Full
contract is documented at the top of `_hook_harness.py`.

## The measured-leash discipline

A soft hook you cannot watch fire is indistinguishable from a dead one. So every
firing writes a line to `reflection-turn-end-telemetry.jsonl`, and every silent Stop
that *was* a reflection opportunity writes a line to
`reflection-turn-end-silence-telemetry.jsonl` (with a reason). Read the leash:

```
python3 reflection_turn_end_query.py                 # per-facet firing + silence counts
python3 reflection_turn_end_query.py --facet failure_control
python3 reflection_turn_end_query.py --json
```

**Pull a facet on near-zero yield.** The keep-or-pull rule: a facet that fires but
never precedes a real downstream action is noise — set its kill switch and remove it.
Correlating a firing against "the operator actually acted" is project-specific (join
the firing log against whatever records your hardening-skill invocation); this
portable query reports the firing/silence leash and leaves that join to you.

Kill switches: `REFLECTION_TURN_END_OFF=1` suppresses the whole family; each facet
declares its own (`REFLECTION_FAILURE_CONTROL_OFF=1`,
`REFLECTION_KNOWLEDGE_ROUTING_OFF=1`).

## How to add a facet

1. **Add its key** to the `FacetKey` enum in `reflection_facet.py` (the typed
   namespace — a new dimension is a new key, never a free string).
2. **Subclass `ReflectionFacet`** in a new `reflection_facet_<name>.py` and implement:
   - the four **declaration properties** — `key` (your new `FacetKey`), `tempo`
     (`ON_TURN_END` or `ON_MEMORY_WRITE`), `policy_material` (a tuple of
     `MaterialPointer`s into YOUR canonical policy docs — *reference*, don't copy),
     and `followup_vocabulary` (the closed set of `RoutedFollowup`s it may emit);
   - the four **virtual Algorithm hooks** — `classify` (eligible on this event?),
     `snapshot` (freeze the substrate, I/O here), `check_policy_material` (the policy
     branch, biased hard toward `PROCEED`), and `build_payload` (word the
     conservative nudge — this is the core design work: disarm-open, concrete, with
     an explicit escape, anti-manufacture).
   - **Do not** override `reflect` or `route_followup` — the base owns the control
     flow. Emitting a follow-up outside your declared vocabulary fails loud.
3. **Register it** at the bottom of the module:
   `MY_FACET = REFLECTION_FACETS.register(MyFacet())`.
4. **Import it** in the emitter (`hook_reflection_turn_end.py`) so it self-registers;
   for an ON_TURN_END facet, add its per-facet kill switch to `_PER_FACET_KILL_SWITCH`.
   Import order = round-robin order.

**Hold the discipline:** fail-open (a hook error never blocks a turn), once-per-window
dedupe (never trap the turn in a re-prompt loop), a kill switch, a default-silent /
bias-away payload, and per-firing telemetry. That discipline — not the specific
policy dimension — is the whole value.

**Recommended hard controls** (author these as lints over your facet registry — see
the `reflection-facet-substrate` mechanism's "held hard" note):

- a **closed-surface lint** — every facet implements exactly the sanctioned virtuals
  and overrides nothing else;
- a **pointer-resolve lint** — every facet's `policy_material` pointer resolves
  (`MaterialPointer.resolves(repo_root)`), so a moved policy doc trips a check rather
  than rotting inside a hook string.

Start with ONE facet if that's all you need — the registry and the shared window are
overhead until the *second*. This substrate earns its keep at facet two.
