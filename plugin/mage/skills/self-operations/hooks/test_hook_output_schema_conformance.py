#!/usr/bin/env python3
"""test_hook_output_schema_conformance.py — the conformance control (the class-killer).

PORTABLE. Stdlib ``unittest`` (no pytest dependency). Runnable directly:
``python3 test_hook_output_schema_conformance.py``.

Drives EVERY hook wired in ``settings.snippet.json`` end-to-end (as a subprocess,
real JSON on stdin) and validates the JSON it ACTUALLY prints — the same JSON the
Claude Code harness would receive — against the vendored hook-output schema
(:mod:`_claude_hook_output_schema`). A field-drift in ANY hook fails THIS test
instead of silently failing at runtime.

WHY THIS EXISTS (the failure class it kills). A hook can be built on an output
capability that does not exist (e.g. trying to inject from a block-only Stop /
SubagentStop event). If the hook's own test asserts its self-declared (impossible)
shape, the suite stays green while production is broken — the test validated the
hook against ITS contract, never against the harness schema. This conformance
control closes that class: it makes ``_claude_hook_output_schema`` LOAD-BEARING by
checking every wired hook's real output against it.

Two assertions:

  1. For every (hook, stdin) fixture: the hook exits 0 or 2 (the only sanctioned
     hook exit codes — 0 allow/proceed, 2 deny), and its stdout, if non-empty,
     parses as JSON and passes ``validate_hook_output(<event>, payload)`` with ZERO
     violations.
  2. Coverage: every hook wired in ``settings.snippet.json`` has a case. A new hook
     added to the snippet without a conformance case fails THIS test — no silent
     gap. (Extra cases for hooks not yet in the snippet are allowed, so a case can
     land before its wiring.)

Table-driven: adding a hook is one ``HookCase`` row. Each case declares the hook
script (basename), the Claude Code event it is wired to, and representative stdin
payloads exercising its decision branches.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _claude_hook_output_schema import validate_hook_output  # noqa: E402 — sibling module

SETTINGS_SNIPPET = _HOOKS_DIR / "settings.snippet.json"

# The sanctioned hook exit codes (Claude Code hooks spec): 0 = allow / proceed,
# 2 = deny (PreToolUse). Any other code is itself a conformance failure.
_ALLOWED_EXIT_CODES = frozenset({0, 2})


@dataclass(frozen=True)
class HookCase:
    """One wired hook + the Claude Code event it is wired to + stdin fixtures."""

    script: str  # basename of the hook script (colocated in this hooks/ dir)
    event: str  # the Claude Code event (must be a vendored KNOWN_EVENTS value)
    stdins: tuple[str, ...]  # representative stdin JSON payloads exercising branches
    # Env overrides applied when running the subprocess (e.g. neutralize a kill
    # switch, or force a deterministic no-op path).
    env: dict[str, str] = field(default_factory=dict)


# Representative stdin fixtures per hook. The goal is to exercise EACH decision
# branch that can emit a payload — the schema is validated on whatever is printed.
_CASES: tuple[HookCase, ...] = (
    # Stop reflection-turn-end emitter. Fires ≤1 reflection per shared window,
    # emitting {"decision":"block","reason":"..."} — a schema-valid Stop
    # top-level-only payload. The kill switch forces the no-fire (no-op) path so a
    # test run does not trip the window / write real telemetry; the block shape is
    # itself a valid Stop payload (validate_hook_output covers both).
    HookCase(
        script="hook_reflection_turn_end.py",
        event="Stop",
        stdins=(
            '{"session_id":"s1","transcript_path":"/tmp/does-not-exist.jsonl"}',
            "",  # malformed → noop (fail-open)
        ),
        env={"REFLECTION_TURN_END_OFF": "1"},
    ),
    # PreToolUse skill-usage telemetry: telemetry-only hook — writes to a .jsonl
    # sink, emits NO decision JSON (always exit 0 with empty stdout → universally-
    # valid no-op). The kill switch suppresses the file write so the test env is
    # left clean; the schema conformance being tested is "emits nothing → valid".
    # The matcher fires only on Skill; non-Skill tool calls are silently ignored.
    HookCase(
        script="hook_skill_usage_telemetry.py",
        event="PreToolUse",
        stdins=(
            '{"tool_name":"Skill","tool_input":{"skill":"self-governance","args":"interpret-failure"},"session_id":"s1"}',
            '{"tool_name":"Skill","tool_input":{"skill":"repo-query"},"session_id":"s2"}',
            '{"tool_name":"Bash","tool_input":{"command":"echo hi"}}',  # non-Skill → noop
            "",  # malformed → noop
        ),
        env={"SELFOPS_SKILL_TELEMETRY_OFF": "1"},
    ),
)


def _run_hook(case: HookCase, stdin: str) -> tuple[int, str]:
    """Execute the hook script (from this hooks/ dir) as a subprocess.

    Returns (exit_code, stdout). Runs with a scratch ``CLAUDE_PROJECT_DIR`` so any
    fail-open sink write (should the kill switch not catch it) lands in /tmp, never
    in the repo.
    """
    env = dict(os.environ)
    env.setdefault("CLAUDE_PROJECT_DIR", "/tmp")
    env.update(case.env)
    proc = subprocess.run(
        [sys.executable, str(_HOOKS_DIR / case.script)],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=str(_HOOKS_DIR),
        env=env,
        timeout=30,
        check=False,
    )
    return proc.returncode, proc.stdout


def _wired_scripts() -> set[str]:
    """The set of hook-script basenames wired in ``settings.snippet.json``.

    Parses the ``hooks`` block, splits each ``command`` on whitespace, and takes the
    basename of any ``.py`` token. Robust to the ``$CLAUDE_PROJECT_DIR`` prefix and
    to quoting in the command string.
    """
    settings = json.loads(SETTINGS_SNIPPET.read_text(encoding="utf-8"))
    wired: set[str] = set()
    for matchers in settings.get("hooks", {}).values():
        for matcher in matchers:
            for hook in matcher.get("hooks", []):
                cmd = hook.get("command", "")
                for token in cmd.replace('"', " ").split():
                    if token.endswith(".py"):
                        wired.add(Path(token).name)
    return wired


class TestHookOutputSchemaConformance(unittest.TestCase):
    def test_every_wired_hook_emits_a_schema_valid_payload(self) -> None:
        for case in _CASES:
            for stdin in case.stdins:
                with self.subTest(script=case.script, stdin=stdin[:40]):
                    rc, stdout = _run_hook(case, stdin)
                    self.assertIn(
                        rc,
                        _ALLOWED_EXIT_CODES,
                        f"{case.script} exited {rc} (allowed: {sorted(_ALLOWED_EXIT_CODES)})",
                    )
                    text = stdout.strip()
                    if not text:
                        continue  # empty stdout is the universally-valid no-op
                    try:
                        payload = json.loads(text)
                    except json.JSONDecodeError as exc:
                        self.fail(
                            f"{case.script} emitted non-JSON stdout: {text!r} ({exc})"
                        )
                    self.assertIsInstance(
                        payload, dict, f"{case.script} emitted non-object JSON: {text!r}"
                    )
                    violations = validate_hook_output(case.event, payload)
                    self.assertEqual(
                        violations,
                        [],
                        f"{case.script} ({case.event}) emitted a schema-INVALID payload "
                        f"for stdin {stdin!r}:\n  {json.dumps(payload)}\n"
                        f"violations:\n  - " + "\n  - ".join(violations),
                    )

    def test_case_table_covers_every_wired_hook(self) -> None:
        """Every hook wired in settings.snippet.json MUST have a conformance case.

        A new hook added to the snippet without a case fails THIS test — the drift
        the class-killer prevents. Extra cases (a case ahead of its wiring) are OK.
        """
        wired = _wired_scripts()
        covered = {c.script for c in _CASES}
        missing = wired - covered
        self.assertEqual(
            missing,
            set(),
            f"wired hooks with no conformance case (add a HookCase row): {sorted(missing)}",
        )


if __name__ == "__main__":
    unittest.main()
