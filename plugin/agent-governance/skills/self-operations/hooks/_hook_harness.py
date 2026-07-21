"""_hook_harness.py — a minimal, self-contained Claude Code hook harness.

PORTABLE. Stdlib-only. Copy this whole ``hooks/`` directory into your ``.claude/``
and adapt. This file has NO project coupling — it implements just enough of the
Claude Code hook contract for the reflection substrate to run.

────────────────────────────────────────────────────────────────────────────────
THE CLAUDE CODE HOOK CONTRACT (the part this harness realizes)

A hook is a script Claude Code runs at a lifecycle event. The event's JSON payload
arrives on **stdin**; the hook's decision goes out on **stdout** as JSON; the exit
code is (almost) always 0.

This substrate uses the **Stop** event (fires when the assistant finishes a turn).
A Stop hook may:

  - emit nothing (exit 0)                     → allow the turn to end (the no-op).
  - emit ``{"decision":"block","reason":…}``  → re-prompt the assistant with
                                                ``reason`` as an injected message
                                                (the "nudge"). Stop is BLOCK-only —
                                                there is no separate "inject" verb,
                                                so a nudge IS a block whose reason
                                                is the nudge text.

It also uses **PostToolUse** (fires after a tool call) for the memory-write facet;
that payload carries ``tool_name`` and ``tool_input.file_path``.

TURN-TRAP SAFETY. A Stop hook that blocks unconditionally would trap the turn in an
infinite re-prompt loop. So EVERY blocking Stop hook here MUST: (a) dedupe within a
window (fire ≤1×/window), (b) have an exit condition that becomes false, and (c)
carry a kill switch. The emitter enforces all three.

FAIL-OPEN. A hook error must NEVER block a turn. Every parse/read/write path here
swallows its exception and falls back to "allow" (emit nothing). A broken hook is
silent, not fatal.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, cast


@dataclass
class HookInput:
    """The parsed hook stdin payload (a subset of the Claude Code hook JSON).

    ``raw`` retains the whole dict; typed accessors surface the fields the facets
    read. A malformed / empty / non-object stdin yields ``ok=False`` with empty
    defaults — callers treat that as "fail-open, allow".
    """

    raw: dict[str, Any] = field(default_factory=dict)
    ok: bool = True  # False ⇒ stdin was malformed / empty / not a JSON object.

    @property
    def tool_name(self) -> str:
        """PostToolUse ``tool_name`` (e.g. "Write" / "Edit"), coerced to str."""
        val = self.raw.get("tool_name")
        return val if isinstance(val, str) else ""

    @property
    def tool_input(self) -> dict[str, Any]:
        val = self.raw.get("tool_input")
        return cast("dict[str, Any]", val) if isinstance(val, dict) else {}

    @property
    def file_path(self) -> str:
        """PostToolUse ``tool_input.file_path`` (the path a Write/Edit touched)."""
        val = self.tool_input.get("file_path")
        return val if isinstance(val, str) else ""

    @property
    def session_id(self) -> str:
        """The Claude Code session id (used to correlate telemetry)."""
        val = self.raw.get("session_id")
        return val if isinstance(val, str) else ""


def parse_stdin(raw: str | None = None) -> HookInput:
    """Parse the hook stdin JSON defensively; NEVER raises (fail-open).

    Returns ``HookInput(ok=False)`` with empty fields if stdin is empty,
    unparseable, or not a JSON object. Pass ``raw`` in tests to avoid touching
    ``sys.stdin``.
    """
    if raw is None:
        try:
            raw = sys.stdin.read()
        except OSError:
            return HookInput(ok=False)
    if not raw or not raw.strip():
        return HookInput(ok=False)
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return HookInput(ok=False)
    if not isinstance(payload, dict):
        return HookInput(ok=False)
    return HookInput(raw=cast("dict[str, Any]", payload), ok=True)


@dataclass(frozen=True)
class HookDecision:
    """A hook's decision, rendered as Claude Code hook JSON on stdout.

    Two shapes only, matching the Stop contract:
      - ``noop()``            → emit nothing, exit 0 (allow the turn to end).
      - ``block(reason)``     → ``{"decision":"block","reason":…}``, exit 0
                                (re-prompt with ``reason`` — the nudge).
    """

    decision: str | None = None  # "block" or None.
    reason: str | None = None

    @classmethod
    def noop(cls) -> HookDecision:
        """Emit nothing — allow the turn to end (the default-silence common case)."""
        return cls()

    @classmethod
    def block(cls, reason: str) -> HookDecision:
        """Re-prompt the assistant with ``reason`` as an injected message."""
        return cls(decision="block", reason=reason)

    def emit(self) -> int:
        """Print the decision JSON (if any) to stdout; return the exit code (always 0).

        A no-op prints nothing. Fail-open: a print failure is swallowed so a hook
        error can never propagate into a blocked turn.
        """
        if self.decision == "block":
            try:
                sys.stdout.write(
                    json.dumps({"decision": "block", "reason": self.reason or ""})
                )
            except OSError:
                pass
        return 0
