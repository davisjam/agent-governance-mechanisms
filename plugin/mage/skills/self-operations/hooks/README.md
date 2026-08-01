# The hook library — a runnable, portable substrate

*A self-contained, stdlib-only Claude Code hook library. Copy this whole `hooks/`
directory into your `.claude/`, wire the hooks, and adapt the example facets. This is
the runnable complement to the catalogue's
[reflection-facet-substrate](../../../../../agent/lifecycle-and-observability/reflection-facet-substrate.md)
mechanism and the [L6 · govern-your-own-loop](../examples/lifecycle-L6-govern-your-own-loop.md)
lifecycle model.*

It ships three layers you adopt independently:

1. **The reflection substrate** — tempo-gated, default-silent nudges that fire a
   skipped reflex at its moment (the bulk of this README).
2. **The typed hook substrate** — a machine-checkable Claude Code hook-output schema
   + a typed hook registry that catches an "inject on a block-only event" bug *at
   construction*, not in production (see [The typed hook substrate](#the-typed-hook-substrate)).
3. **The banking substrate** — the runnable half of L2 (manage-context): an atomic
   dual-write status banker + a paired-artifact consistency facet + a
   machine-generated handoff scaffold (see [The banking substrate](#the-banking-substrate)).

**Every hook here holds the same five-part discipline** — the value is the discipline,
not any one hook:

- **(a) fail-open** — a hook error never blocks a turn (it falls back to silence);
- **(b) kill-switched** — every hook honours an env-var off switch;
- **(c) context-guarded** — a hook meant for the operator no-ops inside a sub-agent
  session (guard on your fleet's worktree/agent marker);
- **(d) telemetered** — every firing (and every was-eligible-but-silent) writes a line
  to a jsonl leash you can read;
- **(e) capability-derived** — a hook's allowed output shape is *derived from the
  vendored schema*, never hand-declared (so a block-only event can't claim to inject).

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

Three example facets ship, all generic:

- **`reflection_facet_recurrence.py`** — the `failure_control` facet. On a turn-end,
  "did the same failure surface ≥2× this session? convert the *class* into a control
  (lint / gate / typed seam / test), don't just re-patch the instance."
- **`reflection_facet_memory_routing.py`** — the `knowledge_routing` facet. On a
  memory-file write, "is this a true one-off, or durable know-how that belongs in a
  shared runbook / design doc instead?"
- **`reflection_facet_bank_consistency.py`** — the `bank_consistency` facet. On a write
  to one member of a paired status set (e.g. a strategy doc + a handoff doc), "you
  updated one; the other is now stale — bank the pair before you end the turn." The
  facet shape the other two don't cover: *paired-artifact freshness*.

## Files

| File | Role |
|---|---|
| `reflection_facet.py` | The Template-Method base + typed registry + the types (`FacetKey`, `ReflectionTempo`, `RoutedFollowup`, `MaterialPointer`, `ReflectionResult`). The core — port this faithfully. |
| `hook_reflection_turn_end.py` | The runnable **Stop** hook (the ON_TURN_END emitter): the ≤1-per-window round-robin gate + dedupe flag + telemetry. |
| `reflection_facet_recurrence.py` | Example facet: failure→control (ON_TURN_END). |
| `reflection_facet_memory_routing.py` | Example facet: memory-vs-runbook routing (ON_MEMORY_WRITE). |
| `reflection_facet_bank_consistency.py` | Example facet: paired-status-artifact freshness (ON_MEMORY_WRITE). |
| `reflection_turn_end_query.py` | The measured-leash query (per-facet firing + silence counts). |
| `_hook_harness.py` | Minimal self-contained Claude Code hook harness (stdin parse + decision emit). No project coupling. |
| `_claude_hook_output_schema.py` | The vendored, machine-checkable Claude Code hook-output contract (which events may inject; the block-only set). No project coupling. |
| `_hook_registry.py` | The typed hook registry — declares what each hook may output (INJECT/BLOCK derived from the schema); catches inject-on-block-only at construction. |
| `test_hook_output_schema_conformance.py` | The conformance control — drives every wired hook and validates its real output against the schema; asserts no wired hook is untested. |
| `hook_skill_usage_telemetry.py` | PreToolUse hook: logs every `Skill` invocation to the measured leash (are your skills firing at all?). |
| `skill_usage_query.py` | Cross-log query: did a reflection nudge precede an actual skill invocation in the same session? |
| `bank_status.py` | The atomic dual-write status banker (both-or-nothing write of a parameterized status-artifact set). |
| `settings.snippet.json` | How to register the Stop + PreToolUse hooks and set the kill-switch / window / bank-pair env vars. |

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

## The typed hook substrate

A Claude Code hook may emit different output shapes at different events — and a
`Stop` / `SubagentStop` / `PreCompact` / `Notification` hook may emit **no**
`hookSpecificOutput` at all (it is block-only). A hook that tries to *inject* context
on one of those events fails silently in production: the output is ignored and the
hook looks dead. This layer makes that a *construction-time* error instead.

- **`_claude_hook_output_schema.py`** vendors the contract: `KNOWN_EVENTS`,
  `hook_specific_output_allowed(event)`, and `validate_hook_output(event, payload)`
  (returns the list of violations; `[]` = valid). It is pure Claude-Code knowledge —
  zero project coupling — so it is the one file to copy near-verbatim and keep current
  with the hooks docs.
- **`_hook_registry.py`** builds on it: a frozen `OrchestratorHook` declares its event,
  and its allowed `HookOutputKind` (INJECT / BLOCK) is **derived from the schema**, not
  hand-set. Declaring INJECT on a block-only event raises `HookCapabilityError` when the
  hook object is *constructed* — the (e) discipline made mechanical. A `HookRegistry.run`
  driver owns kill-switch honouring + fail-open in one place.
- **`test_hook_output_schema_conformance.py`** is the hard control that makes the schema
  load-bearing: it reads the hooks wired in `settings.snippet.json`, drives each
  end-to-end with a representative payload, validates the *actual* stdout against the
  schema, and asserts every wired hook has a test case (no silent gaps). Run it with
  `python3 test_hook_output_schema_conformance.py`.

**Recommended:** wire the conformance test into your pre-commit / CI alongside the
closed-surface and pointer-resolve lints above — it is the third standing control over
the hook substrate.

## The banking substrate

Some judgments recur every session at the substrate's *edges*: bank the in-flight
state before a context window compacts; keep a strategy doc and its handoff in sync;
know whether your own skills are even firing. This layer ships the runnable half of the
[L2 · manage-context](../examples/lifecycle-L2-manage-context.md) lifecycle — the part
the model only described in prose.

- **`bank_status.py`** — the atomic dual-write status banker. You hand it a
  parameterized set of `StatusArtifact` records (name, path, render-callable); it
  renders them all into memory, then writes each via temp-file + `os.replace`. A render
  failure aborts the whole bank with **nothing written** — both-or-nothing, so a
  compaction can never catch a half-updated pair. Runs 1, 2, or N artifacts; nothing is
  hardcoded. `python3 bank_status.py --set STRATEGY=path --set HANDOFF=path`.
- **`reflection_facet_bank_consistency.py`** — the soft complement (an `ON_MEMORY_WRITE`
  reflection facet): write one member of the paired set and, if the other is now stale,
  it nudges FINISH-THE-BANK. Point it at the pair with `REFLECTION_BANK_PAIR` (two
  `os.pathsep`-joined absolute paths); silent no-op until you do.
- **`hook_skill_usage_telemetry.py`** + **`skill_usage_query.py`** — the measured leash
  for the skills themselves. The PreToolUse hook logs every `Skill` invocation; the
  query joins that log against the reflection-firing log by `session_id` to answer *"did
  a nudge ever precede an actual skill invocation?"* — the keep-or-pull evidence the
  reflection query alone can't produce.
- **`emit-handoff-starter.py`** (shipped in [`../templates/`](../templates/), not here)
  — a fill-in scaffold that machine-generates the *reconstructable* handoff sections
  from live git state (HEAD, worktrees, status, recent commits) and leaves
  `<!-- TODO: narrative -->` for judgment. Banking becomes a narrative diff, not a
  rewrite — which is what makes frequent re-banking actually happen. Adapt its
  `# TODO(adapt)` seam to your own queryable sources.

The `ON_MEMORY_WRITE` facet needs the same optional `PostToolUse` emitter as the
memory-routing facet (see step 3 of *How to wire it*); `bank_status.py`,
`hook_skill_usage_telemetry.py`, and the query run standalone.
