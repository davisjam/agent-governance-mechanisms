#!/usr/bin/env python3
"""hook_skill_usage_telemetry.py — PreToolUse hook: Skill-usage telemetry.

PORTABLE. Stdlib-only. Zero project coupling. Fires on every ``Skill`` tool call
from the Claude Code harness (orchestrator AND sub-agent contexts) and appends one
JSON line describing the invocation to ``.claude/skill-usage-telemetry.jsonl``.
This is the **measured leash** for a plain question your custom skills otherwise
can only answer anecdotally: *are they even firing this session?* Skill use is then
queryable directly rather than only incidentally recoverable from a noisy transcript.

**Fires in ALL contexts — deliberately NOT gated on any orchestrator check.**
Sub-agent skill use is exactly what this telemetry wants to capture, so there is no
worktree no-op. The sink is a single append-only log under the project's ``.claude/``.

**FAIL-OPEN, ALWAYS.** A Skill call must NEVER be blocked or delayed by a telemetry
error. Every failure path — a malformed payload, an unwritable sink, a permission
error — is swallowed and the hook exits 0 (allow). A telemetry error propagating
into a guardrail is the exact catastrophic outcome the design forbids.

SINK ROOT. The project root is ``$CLAUDE_PROJECT_DIR`` (set by Claude Code) or the
current working directory as a fallback; the sink is ``<root>/.claude/
skill-usage-telemetry.jsonl``. Portable — no hardcoded path.

INPUT CONTRACT (Claude Code PreToolUse):
  JSON via stdin — {"tool_name": "Skill", "tool_input": {"skill": "...",
  "args": "..."}, "session_id": "...", ...}. The ``tool_input`` sub-keys are read
  defensively (``skill`` / ``name`` for the skill; ``args`` / ``arguments`` /
  ``input`` for the args summary).

OUTPUT CONTRACT: Exit 0 — always allow (this hook never denies a Skill call, and
  emits no decision JSON: empty stdout is the universally-valid PreToolUse no-op).

ENV VARS:
  SELFOPS_SKILL_TELEMETRY_OFF=1 — kill switch: suppress the append (for a noisy
                                  debugging session); the hook still exits 0.

SETTINGS.JSON WIRING (merge into .claude/settings.json; fix the path to where you
copied this hooks/ directory):

    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Skill",
          "hooks": [
            {
              "type": "command",
              "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hook_skill_usage_telemetry.py\""
            }
          ]
        }
      ]
    }
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# _hook_harness lives beside this file; insert so the bare import resolves when
# this script is exec'd directly by the harness (no hooks dir on sys.path).
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)
from _hook_harness import parse_stdin  # noqa: E402 — sibling module after sys.path insert

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Kill switch — suppress the append without touching the hook's exit code.
ENV_TELEMETRY_OFF = "SELFOPS_SKILL_TELEMETRY_OFF"

# Max chars retained for the args summary (args can be long free text; the
# telemetry is for "which skill, roughly what", not verbatim reconstruction).
_ARGS_SUMMARY_MAX = 200


def _project_root() -> Path:
    """The project root: ``$CLAUDE_PROJECT_DIR`` (set by Claude Code) or cwd.

    Portable — no hardcoded path. When Claude Code runs the hook it sets
    ``CLAUDE_PROJECT_DIR`` to the project root; the cwd fallback keeps the hook
    runnable standalone (e.g. from a shell for a smoke test).
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def telemetry_path() -> Path:
    """The single append-only sink under the project ``.claude/`` dir.

    Computed at call time (not a module constant) so a monkeypatched
    ``CLAUDE_PROJECT_DIR`` / cwd is honored, and so the query tool and this
    emitter agree on the path by construction.
    """
    return _project_root() / ".claude" / "skill-usage-telemetry.jsonl"


def _extract_skill(tool_input: dict[str, Any]) -> str:
    """Extract the skill name from the Skill tool input, coerced to str.

    The Skill tool input carries the skill under ``skill``; fall back to ``name``
    for robustness against a schema rename. Empty string if absent.
    """
    for key in ("skill", "name"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def _extract_args_summary(tool_input: dict[str, Any]) -> str:
    """Extract a truncated args summary from the Skill tool input.

    The args live under ``args`` (canonical), with ``arguments`` / ``input`` as
    fallbacks. Whitespace is collapsed and the result truncated to keep the
    telemetry line small.
    """
    raw: Any = None
    for key in ("args", "arguments", "input"):
        if key in tool_input:
            raw = tool_input[key]
            break
    if raw is None:
        return ""
    text = raw if isinstance(raw, str) else json.dumps(raw, default=str)
    summary = " ".join(text.split())  # collapse whitespace/newlines
    if len(summary) > _ARGS_SUMMARY_MAX:
        summary = summary[: _ARGS_SUMMARY_MAX - 1].rstrip() + "…"
    return summary


def build_record(raw_stdin: str | None = None) -> dict[str, Any] | None:
    """Build the telemetry record from the hook stdin JSON, or None to skip.

    Returns None when the payload is malformed, is not a Skill call, or carries no
    skill name — in every such case the hook appends nothing (fail-open). Exposed
    (not inlined) so a unit test can pin the parse without touching disk.

    The ``ts`` field uses a ``YYMMDD.HHMMSS`` local-time convention so a reader can
    eyeball the time; ``session_id`` ties a firing to its session (the join key the
    cross-log query uses to correlate a reflection nudge with a later skill call).
    """
    hook_input = parse_stdin(raw_stdin)
    if not hook_input.ok:
        return None
    if hook_input.tool_name and hook_input.tool_name != "Skill":
        # A matcher mis-fire (or a manual invocation with the wrong tool_name):
        # record nothing. An ABSENT tool_name (empty) is tolerated — some harness
        # payloads omit it — so we only skip on an explicit non-Skill name.
        return None
    skill = _extract_skill(hook_input.tool_input)
    if not skill:
        return None
    session_id = hook_input.raw.get("session_id")
    return {
        "skill": skill,
        "ts": time.strftime("%y%m%d.%H%M%S"),  # local time
        "session_id": session_id if isinstance(session_id, str) else "",
        "args_summary": _extract_args_summary(hook_input.tool_input),
    }


def append_record(record: dict[str, Any], path: Path | None = None) -> bool:
    """Append one JSON line to the telemetry sink. NEVER raises (fail-open).

    Returns True iff the line was written, False on any swallowed failure or when
    telemetry is switched off. The boolean is for a unit test — the hook ignores it
    (a write failure must not change the exit code). ``path`` defaults to
    :func:`telemetry_path` computed at call time.
    """
    if os.environ.get(ENV_TELEMETRY_OFF) == "1":
        return False
    if path is None:
        path = telemetry_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return True
    except Exception:  # noqa: BLE001 — FAIL-OPEN: telemetry must NEVER block/delay a Skill call. Every write failure (unwritable sink, permission error, disk-full) is swallowed so the hook exits 0 regardless.
        return False


def main() -> int:
    """Append the Skill-usage telemetry record; always return 0 (allow).

    FAIL-OPEN: the record build and the append both swallow all failures, so this
    hook can never block a Skill call — it emits no decision JSON and exits 0
    unconditionally.
    """
    try:
        record = build_record()
        if record is not None:
            append_record(record)
    except Exception:  # noqa: BLE001 — FAIL-OPEN belt-and-suspenders: even an unexpected error in build/append must not block the Skill call. build_record + append_record are already defensive; this outer guard makes the exit-0 guarantee total.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
