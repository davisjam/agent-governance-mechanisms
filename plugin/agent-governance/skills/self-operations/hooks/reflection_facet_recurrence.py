"""reflection_facet_recurrence.py — the ``failure_control`` reflection facet.

PORTABLE example facet. Reflection dimension: *failure → control*.

On a turn-end (when it is this facet's round-robin turn in the shared ON_TURN_END
window) it emits a conservative reminder: if the SAME failure has surfaced ≥2× this
session, stop re-patching the instance and convert the CLASS into a durable control
(a lint / gate / typed seam / test). The facet cannot itself detect a recurrence —
that is model judgment over the session's work — so it always emits the SAME
reminder; the "only on CLEAR evidence, otherwise say nothing" gate lives in the
payload WORDING, delegated to the operator's judgment.

The split of concerns:

  - **The facet** (this file) owns the POLICY: "when it is my turn, emit the
    failure→control self-check." Its ``check_policy_material`` returns ``NUDGE``
    unconditionally because the facet always has the same thing to say.
  - **The emitter** (hook_reflection_turn_end.py) owns the TEMPO: orchestrator
    context, the ≤1-per-window dedupe, the kill switch, telemetry — shared across
    all ON_TURN_END facets so a busy session still sees ≤1 reflection per window.

To adapt: change the ``policy_material`` pointers to YOUR hardening-discipline doc,
and re-word ``NUDGE_TEXT`` for your control vocabulary.
"""

from __future__ import annotations

from reflection_facet import (
    REFLECTION_FACETS,
    FacetKey,
    MaterialPointer,
    ReflectionFacet,
    ReflectionTempo,
    RoutedFollowup,
)

# WORDING IS THE CORE DESIGN WORK. Disarm-open ("soft; usually a no-op"), concrete
# (name the ≥2× trigger + the control kinds), explicit-escape ("if it hasn't
# recurred, proceed"), anti-manufacture ("don't invent a recurrence to justify
# acting"). Re-word this for your own hardening discipline.
NUDGE_TEXT = (
    "🛠  FAILURE→CONTROL SELF-CHECK (soft; usually a no-op — proceed by default). "
    "Before you finish: did the SAME failure surface twice or more this session — "
    "the same bug re-fixed, the same lint mis-firing, the same manual step re-done "
    "by hand? If so, the instance-level patch you just made won't stop the NEXT "
    "instance. Consider converting the CLASS into a durable control instead of only "
    "re-patching: a lint or gate that fires on the pattern, a typed seam that makes "
    "the mistake unrepresentable, a regression/property test that pins it, or a "
    "runtime guard. Hand the class to your hardening discipline (the partner "
    "self-governance skill's interpret-failure mode) — a designed, registered "
    "control, not an inline hack. If the failure has NOT recurred, proceed — this "
    "is usually the case, and manufacturing a control for a one-off is worse than "
    "missing one. Do NOT invent a recurrence to justify acting."
)

# Per-facet kill switch (an env var → "1" suppresses just this facet in the
# round-robin). The emitter reads it; name it whatever fits your convention.
ENV_NUDGE_OFF = "REFLECTION_FAILURE_CONTROL_OFF"


class RecurrenceNudgeFacet(ReflectionFacet):
    """The ``failure_control`` facet — reflect on whether a failure class recurred ≥2×."""

    @property
    def key(self) -> FacetKey:
        return FacetKey.FAILURE_CONTROL

    @property
    def tempo(self) -> ReflectionTempo:
        return ReflectionTempo.ON_TURN_END

    @property
    def policy_material(self) -> tuple[MaterialPointer, ...]:
        # Point at YOUR canonical hardening-discipline material (the "convert a
        # recurrence into a control" method + the skill that names the hand-off).
        # These illustrative refs resolve inside this catalogue; swap for yours.
        return (
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/principles.md",
                anchor="a6-you-have-the-freedom-and-duty-to-improve-the-substrate",
            ),
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/SKILL.md"
            ),
        )

    @property
    def followup_vocabulary(self) -> frozenset[RoutedFollowup]:
        # A self-check nudge — no user-surface / backlog hand-off.
        return frozenset({RoutedFollowup.NUDGE})

    # ---- The four virtual Algorithm hooks ----

    def classify(self, hook_input: object) -> object | None:
        """Eligible on EVERY turn-end (the tempo-gate decides IF this turn fires).

        There is no per-event predicate — a turn-end is always a candidate moment
        for the failure-control self-check. Returns a sentinel so the Algorithm
        proceeds; the emitter's window-gate + round-robin decide whether this facet
        actually reflects THIS turn.
        """
        _ = hook_input
        return True

    def snapshot(self, hook_input: object, classification: object) -> object:
        """No substrate to read — the payload is a static reminder.

        The facet cannot detect a recurrence, so the snapshot is empty. Kept as an
        explicit no-op to honor the fixed Algorithm shape uniformly.
        """
        _ = (hook_input, classification)
        return None

    def check_policy_material(self, snapshot: object) -> RoutedFollowup:
        """Always NUDGE when it is this facet's turn (the CLEAR-evidence gate is in the payload)."""
        _ = snapshot
        return RoutedFollowup.NUDGE

    def build_payload(self, snapshot: object, followup: RoutedFollowup) -> str | None:
        """Return the conservative ``NUDGE_TEXT``."""
        _ = (snapshot, followup)
        return NUDGE_TEXT


# Self-register at import.
RECURRENCE_FACET: ReflectionFacet = REFLECTION_FACETS.register(RecurrenceNudgeFacet())


__all__ = [
    "ENV_NUDGE_OFF",
    "NUDGE_TEXT",
    "RECURRENCE_FACET",
    "RecurrenceNudgeFacet",
]
