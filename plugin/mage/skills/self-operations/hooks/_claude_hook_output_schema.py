"""_claude_hook_output_schema.py — the vendored Claude Code hook-output schema.

PORTABLE. Stdlib-only. Zero project coupling. This module vendors the **valid
output surface per hook event** from the Claude Code hooks contract, so that "what
a hook is allowed to emit" is a machine-checkable fact rather than a comment that
rots. It is the SINGLE SOURCE OF TRUTH the hook registry (the emitter) and the
conformance test (`test_hook_output_schema_conformance.py`) both validate against,
so a field-drift in ANY hook fails a test instead of silently failing at runtime.

WHY THIS EXISTS (the failure class it kills). A hook can be built on an output
capability that does not exist — for example, trying to steer the summarizer from
a PreCompact hook, which is a block/allow veto only and carries NO
``hookSpecificOutput`` surface. If the hook's own test asserts its self-declared
(impossible) shape, the suite stays green while production is broken. This vendored
schema makes "SubagentStop is block-only, cannot inject" (and every sibling claim)
an ENFORCEABLE predicate: the conformance control drives each hook end-to-end and
validates the JSON it actually prints against this table.

THE VALID OUTPUT SURFACE (the Claude Code hook contract, transcribed):

  Common top-level fields (allowed for EVERY hook event):
    - ``continue``         (bool)  — whether Claude continues after the hook.
    - ``stopReason``       (str)   — message shown when ``continue`` is false.
    - ``suppressOutput``   (bool)  — hide stdout from the transcript.
    - ``systemMessage``    (str)   — warning surfaced to the user.
    - ``decision``         (str)   — "block" (Stop / PreCompact / … veto).
    - ``reason``           (str)   — companion to ``decision:"block"``.
    - ``terminalSequence`` (str)   — advanced terminal-control field.

  Per-event ``hookSpecificOutput`` sub-shapes (the ONLY events that support one):
    - PreToolUse       → ``permissionDecision`` ("allow"|"deny"|"ask") + optional
                         ``permissionDecisionReason``.
    - SessionStart     → ``additionalContext`` (str).
    - UserPromptSubmit → ``additionalContext`` (str).
    - PostToolUse      → ``additionalContext`` (str).

  Events with NO ``hookSpecificOutput`` (top-level fields only — block/allow veto):
    - PreCompact    → block/allow veto ONLY. There is no output surface to steer
                      the summarizer. Minimal valid no-op = exit 0 with empty
                      stdout (or ``{}``).
    - Stop          → block/allow veto (``decision:"block"`` + ``reason``).
    - SubagentStop  → same as Stop.
    - Notification  → top-level only.

An echoed ``hookEventName`` key inside ``hookSpecificOutput`` is always allowed
(hooks may echo it back for provenance) and, when present, MUST match the event.

PUBLIC INTERFACE (kept stable — imported by the registry + the conformance test):
  - ``KNOWN_EVENTS: frozenset[str]``
  - ``hook_specific_output_allowed(hook_event_name: str) -> bool``
  - ``events_supporting_hook_specific_keys(sub_keys: frozenset[str]) -> list[str]``
  - ``validate_hook_output(hook_event_name, payload) -> list[str]``
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# The vendored per-event allow-tables.
# ---------------------------------------------------------------------------

# Top-level fields allowed for EVERY hook event (the "Common JSON fields").
_COMMON_TOP_LEVEL: Final[frozenset[str]] = frozenset(
    {
        "continue",
        "stopReason",
        "suppressOutput",
        "systemMessage",
        "decision",
        "reason",
        "terminalSequence",
        "hookSpecificOutput",  # gated separately by _HOOK_SPECIFIC_FIELDS below
    }
)

# Per-event allowed ``hookSpecificOutput`` sub-keys. An event ABSENT from this
# table supports NO ``hookSpecificOutput`` at all (PreCompact / Stop / …).
# ``hookEventName`` is implicitly allowed for every event that supports a
# hookSpecificOutput block (it is echoed back for provenance).
_HOOK_SPECIFIC_FIELDS: Final[dict[str, frozenset[str]]] = {
    "PreToolUse": frozenset({"permissionDecision", "permissionDecisionReason"}),
    "SessionStart": frozenset({"additionalContext"}),
    "UserPromptSubmit": frozenset({"additionalContext"}),
    "PostToolUse": frozenset({"additionalContext"}),
}

# The events that support NO ``hookSpecificOutput`` (top-level fields only).
# Listed explicitly so an unknown event is distinguishable from a known-but-
# hookSpecificOutput-less one. This is the field that catches the "steer the
# summarizer from PreCompact" bug: PreCompact is here, so any hookSpecificOutput
# on it is a violation.
_TOP_LEVEL_ONLY_EVENTS: Final[frozenset[str]] = frozenset(
    {"PreCompact", "Stop", "SubagentStop", "Notification"}
)

# Allowed values for PreToolUse ``permissionDecision``.
_PERMISSION_DECISION_VALUES: Final[frozenset[str]] = frozenset({"allow", "deny", "ask"})

# All events the vendored schema knows about (for the "unknown event" check).
KNOWN_EVENTS: Final[frozenset[str]] = (
    frozenset(_HOOK_SPECIFIC_FIELDS) | _TOP_LEVEL_ONLY_EVENTS
)


def hook_specific_output_allowed(hook_event_name: str) -> bool:
    """True iff ``hook_event_name`` may carry a ``hookSpecificOutput`` block."""
    return hook_event_name in _HOOK_SPECIFIC_FIELDS


def events_supporting_hook_specific_keys(sub_keys: frozenset[str]) -> list[str]:
    """Return the events whose ``hookSpecificOutput`` schema supports ALL ``sub_keys``.

    ``hookEventName`` is ignored (it is an echo key allowed on every hSO event).
    Used to infer which event(s) a ``hookSpecificOutput`` block *could* belong to
    when no ``hookEventName`` is echoed — a bare ``additionalContext`` is legal for
    several inject-capable events, so a caller can treat a payload as valid if it
    conforms to at least one candidate. A key that no event supports yields an
    EMPTY list. Derives from the same ``_HOOK_SPECIFIC_FIELDS`` source of truth as
    ``validate_hook_output`` — no second copy to drift.
    """
    meaningful = frozenset(k for k in sub_keys if k != "hookEventName")
    return [
        event
        for event, allowed in _HOOK_SPECIFIC_FIELDS.items()
        if meaningful <= allowed
    ]


def validate_hook_output(
    hook_event_name: str, payload: dict[str, object] | None
) -> list[str]:
    """Validate a hook's emitted JSON payload against the vendored Claude Code schema.

    Returns a list of human-readable violation strings; an EMPTY list means the
    payload is a valid output shape for ``hook_event_name``. A ``None`` payload
    (the no-op / empty-stdout case) is always valid — exit 0 with no stdout is the
    universally-legal no-op.

    Checks:
      1. ``hook_event_name`` is a known Claude Code event.
      2. Every top-level key is in the common-allowed set.
      3. ``hookSpecificOutput`` is present ONLY for events that support it
         (PreCompact / Stop / … must NOT emit one).
      4. Every ``hookSpecificOutput`` sub-key is allowed for that event.
      5. An echoed ``hookEventName`` (inside hookSpecificOutput) matches the event.
      6. PreToolUse ``permissionDecision`` is one of allow/deny/ask.

    The validator is intentionally strict (unknown keys are violations, not
    warnings) — an unrecognized key is exactly the drift class this control exists
    to surface. It never raises on a well-typed dict.
    """
    if payload is None:
        return []

    violations: list[str] = []

    if hook_event_name not in KNOWN_EVENTS:
        violations.append(
            f"unknown hook event {hook_event_name!r} "
            f"(known: {', '.join(sorted(KNOWN_EVENTS))})"
        )
        # Continue anyway — surface any structural issues too.

    # (2) Top-level keys.
    for key in payload:
        if key not in _COMMON_TOP_LEVEL:
            violations.append(
                f"{hook_event_name}: unknown top-level output key {key!r} "
                f"(allowed: {', '.join(sorted(_COMMON_TOP_LEVEL))})"
            )

    # (3)/(4)/(5) hookSpecificOutput handling.
    hso = payload.get("hookSpecificOutput")
    if hso is not None:
        if hook_event_name in _TOP_LEVEL_ONLY_EVENTS:
            violations.append(
                f"{hook_event_name}: emits a hookSpecificOutput block, but "
                f"{hook_event_name} supports NO hookSpecificOutput — it is a "
                f"top-level-only (block/allow veto) event. "
                f"Emit top-level fields only, or a no-op."
            )
        elif hook_event_name not in _HOOK_SPECIFIC_FIELDS:
            violations.append(
                f"{hook_event_name}: emits a hookSpecificOutput block, but this "
                f"event is not known to support one."
            )
        elif not isinstance(hso, dict):
            violations.append(
                f"{hook_event_name}: hookSpecificOutput must be an object, "
                f"got {type(hso).__name__}."
            )
        else:
            allowed_sub = _HOOK_SPECIFIC_FIELDS[hook_event_name]
            for sub_key, sub_val in hso.items():
                if sub_key == "hookEventName":
                    if sub_val != hook_event_name:
                        violations.append(
                            f"{hook_event_name}: hookSpecificOutput.hookEventName "
                            f"is {sub_val!r}, expected {hook_event_name!r}."
                        )
                    continue
                if sub_key not in allowed_sub:
                    violations.append(
                        f"{hook_event_name}: unknown hookSpecificOutput key "
                        f"{sub_key!r} (allowed: {', '.join(sorted(allowed_sub))})."
                    )
                elif (
                    hook_event_name == "PreToolUse"
                    and sub_key == "permissionDecision"
                    and sub_val not in _PERMISSION_DECISION_VALUES
                ):
                    violations.append(
                        f"PreToolUse: permissionDecision {sub_val!r} is not one of "
                        f"{', '.join(sorted(_PERMISSION_DECISION_VALUES))}."
                    )

    return violations


__all__ = [
    "KNOWN_EVENTS",
    "events_supporting_hook_specific_keys",
    "hook_specific_output_allowed",
    "validate_hook_output",
]
