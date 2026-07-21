#!/usr/bin/env python3
"""hook_reflection_turn_end.py — the shared ON_TURN_END reflection emitter (a Stop hook).

PORTABLE. Stdlib-only. This is the runnable Claude Code **Stop** hook: register it
in ``.claude/settings.json`` (see settings.snippet.json). It drives ALL
``ON_TURN_END`` reflection facets through ONE shared tempo window, emitting **at
most one reflection per window** across the facets (round-robin), each keeping
disarm-first / default-silence.

This is the substrate's answer to the load-bearing constraint: *N facets each
firing separately → alarm fatigue → WORSE outcomes.* Adding a facet does NOT raise
the reflection RATE (the window caps it); it only changes WHICH dimension a given
window's single reflection covers. So the facet count is YAGNI-safe on fatigue.

TURN-TRAP SAFETY (every blocking Stop hook must have all three):
  (a) dedupe within a window — the shared flag file makes the block fire ≤1×/window;
  (b) an exit condition that becomes false — the window closes immediately after a
      fire, so the next Stop is a no-op until the window reopens;
  (c) a kill switch — the substrate env var below suppresses the whole family.

FAIL-OPEN. Every read/write/parse path is swallowed → emit nothing (allow stop). A
Stop must NEVER be blocked by a hook error.

ENV VARS:
  REFLECTION_TURN_END_OFF=1        — kill switch: suppress the whole ON_TURN_END
                                     substrate.
  REFLECTION_TURN_END_WINDOW_S     — shared dedupe window in seconds (default 1800 =
                                     30 min).
  REFLECTION_STATE_DIR             — where the window flag + telemetry live (default
                                     the dir this script sits in).
  Per-facet kill switches (each facet declares its own, e.g.
    REFLECTION_FAILURE_CONTROL_OFF) — a killed facet is skipped in the round-robin.

TELEMETRY (the measured leash):
  reflection-turn-end-telemetry.jsonl         — one line per FIRING.
  reflection-turn-end-silence-telemetry.jsonl — one line per Stop that produced NO
    reflection (a default-silence no-op), with a reason + the attributed facet.
  Query both with reflection_turn_end_query.py.

INPUT CONTRACT (Claude Code Stop): JSON via stdin — {"session_id": "...", ...}.
OUTPUT CONTRACT: exit 0 always. ``{"decision":"block","reason":…}`` on a fire;
  nothing otherwise.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

# Make the sibling modules importable when Claude Code exec's this script directly
# (the script's own dir is not on sys.path by default).
_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _hook_harness import HookDecision, HookInput, parse_stdin  # noqa: E402
from reflection_facet import (  # noqa: E402
    REFLECTION_FACETS,
    FacetKey,
    ReflectionFacet,
    ReflectionTempo,
)

# Import the facet modules so they self-register into REFLECTION_FACETS at import.
# Import ORDER = ON_TURN_END round-robin order (facets_for_tempo is registration-
# order). Add your own facet imports here.
import reflection_facet_recurrence as _recurrence  # noqa: E402
import reflection_facet_memory_routing as _memory_routing  # noqa: E402

# Pin the self-registering facets as used + document the set. The ON_TURN_END subset
# competes for THIS emitter's window; the memory-routing facet is ON_MEMORY_WRITE
# (imported for registry completeness only — never selected here).
_REGISTERED_FACETS: tuple[ReflectionFacet, ...] = (
    _recurrence.RECURRENCE_FACET,
    _memory_routing.MEMORY_ROUTING_FACET,
)

# Per-facet kill-switch env vars, keyed by FacetKey (each facet declares its own).
_PER_FACET_KILL_SWITCH: dict[FacetKey, str] = {
    FacetKey.FAILURE_CONTROL: _recurrence.ENV_NUDGE_OFF,
}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_TURN_END_OFF = "REFLECTION_TURN_END_OFF"
ENV_WINDOW_S = "REFLECTION_TURN_END_WINDOW_S"
ENV_STATE_DIR = "REFLECTION_STATE_DIR"
DEFAULT_WINDOW_S = 1800  # 30 minutes.


def _state_dir() -> Path:
    """Where the window flag + telemetry live (env override or the hooks dir)."""
    raw = os.environ.get(ENV_STATE_DIR, "").strip()
    return Path(raw) if raw else _HOOKS_DIR


def _flag_path() -> Path:
    return _state_dir() / ".reflection-turn-end-flag.json"


def telemetry_path() -> Path:
    """The FIRING sink (one JSON line per reflection that emitted a payload)."""
    return _state_dir() / "reflection-turn-end-telemetry.jsonl"


def silence_telemetry_path() -> Path:
    """The SILENCE sink (one JSON line per Stop that produced no reflection)."""
    return _state_dir() / "reflection-turn-end-silence-telemetry.jsonl"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class SilenceReason(str, Enum):
    """WHY a Stop produced no reflection (the silence-telemetry axis)."""

    WINDOW_CLOSED = "window_closed"          # a reflection already fired this window.
    ALL_FACETS_KILLED = "all_facets_killed"  # every ON_TURN_END facet is killed / none registered.
    FACET_DECLINED = "facet_declined"        # a facet was selected but returned silent.


@dataclass(frozen=True)
class TurnEndSnapshot:
    """The read step's output — the facet selected to reflect this window, or None + why.

    ``selected is None`` ⇒ no fire. ``silence`` names WHY (when this Stop WAS a
    reflection opportunity — i.e. the substrate is on and the window was considered);
    ``silence_facet_key`` attributes the silence to a facet where meaningful.
    """

    selected: ReflectionFacet | None
    session_id: str
    silence: SilenceReason | None = None
    silence_facet_key: str = ""


# ---------------------------------------------------------------------------
# The shared window (dedupe + round-robin)
# ---------------------------------------------------------------------------


def _window_s() -> int:
    """The shared dedupe window in seconds (env override or default)."""
    try:
        return int(os.environ.get(ENV_WINDOW_S, DEFAULT_WINDOW_S))
    except ValueError:
        return DEFAULT_WINDOW_S


def _read_flag(path: Path) -> tuple[float, str] | None:
    """Read the (ts, last_facet_key) of the last reflection, or None. NEVER raises."""
    try:
        loaded: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(loaded, dict):
        return None
    data = cast("dict[str, Any]", loaded)
    ts = data.get("ts")
    last = data.get("last_facet_key")
    if not isinstance(ts, (int, float)):
        return None
    return (float(ts), last if isinstance(last, str) else "")


def _write_flag(now: float, facet_key: str, path: Path) -> None:
    """Record (now, facet_key) as the last-reflection flag; best-effort, NEVER raises."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"ts": now, "last_facet_key": facet_key}), encoding="utf-8"
        )
    except OSError:
        # A failed write only weakens the window (the next Stop may re-fire) — safe.
        pass


def _window_open(now: float, window_s: int, flag: tuple[float, str] | None) -> bool:
    """True iff no reflection fired within ``window_s`` seconds of ``now``."""
    if flag is None:
        return True
    prev_ts, _ = flag
    return (now - prev_ts) >= window_s


def _facet_killed(facet: ReflectionFacet) -> bool:
    """True iff this facet's per-facet kill switch is set (skip it in the round-robin)."""
    env = _PER_FACET_KILL_SWITCH.get(facet.key)
    return bool(env) and os.environ.get(env, "") == "1"


def _select_facet(
    last_facet_key: str, candidates: list[ReflectionFacet]
) -> ReflectionFacet | None:
    """Round-robin: pick the next non-killed facet AFTER ``last_facet_key``.

    Over N windows every facet gets a turn, but any single window shows ONE. The
    candidates are registration-order stable; selection starts at the slot after the
    last fire's facet (wrapping). Returns None iff no facet is eligible.
    """
    live = [f for f in candidates if not _facet_killed(f)]
    if not live:
        return None
    keys = [f.key.value for f in live]
    start = keys.index(last_facet_key) + 1 if last_facet_key in keys else 0
    return live[start % len(live)]


# ---------------------------------------------------------------------------
# Telemetry (fail-open)
# ---------------------------------------------------------------------------


def build_telemetry_record(facet_key: str, session_id: str) -> dict[str, Any]:
    """Build a FIRING record (YYMMDD.HHMMSS ts so successive runs don't collide)."""
    return {
        "event": "reflection_turn_end_fired",
        "ts": time.strftime("%y%m%d.%H%M%S"),
        "session_id": session_id,
        "facet_key": facet_key,
    }


def build_silence_record(
    facet_key: str, session_id: str, reason: SilenceReason
) -> dict[str, Any]:
    """Build a SILENCE record (the measurement-leash companion to a firing)."""
    return {
        "event": "reflection_turn_end_silent",
        "ts": time.strftime("%y%m%d.%H%M%S"),
        "session_id": session_id,
        "facet_key": facet_key,
        "reason": reason.value,
    }


def append_telemetry(record: dict[str, Any], path: Path) -> bool:
    """Append one JSON line to a telemetry sink. NEVER raises (fail-open).

    Returns True iff written; False on any swallowed failure or when the kill switch
    is set. Telemetry must never block or delay a Stop.
    """
    if os.environ.get(ENV_TURN_END_OFF) == "1":
        return False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return True
    except Exception:  # noqa: BLE001 — FAIL-OPEN: a telemetry write must never block a Stop.
        return False


# ---------------------------------------------------------------------------
# The read → nudge pair
# ---------------------------------------------------------------------------


def read_substrate(hook_input: HookInput) -> TurnEndSnapshot:
    """Select at most one ON_TURN_END facet to reflect this window.

    Fires iff (kill switch off) AND (window open) AND (≥1 non-killed ON_TURN_END
    facet). Records the window flag on a fire so the block dedupes. On a Stop that
    produces no fire but WAS a reflection opportunity, carries a ``SilenceReason``
    so ``build_nudge`` records the default-silence no-op (the measured leash).
    """
    sid = hook_input.session_id

    if os.environ.get(ENV_TURN_END_OFF) == "1":
        return TurnEndSnapshot(selected=None, session_id=sid)  # not an opportunity.

    candidates = REFLECTION_FACETS.facets_for_tempo(ReflectionTempo.ON_TURN_END)
    if not candidates:
        return TurnEndSnapshot(
            selected=None, session_id=sid, silence=SilenceReason.ALL_FACETS_KILLED
        )

    now = time.time()
    flag = _read_flag(_flag_path())
    last_key = flag[1] if flag is not None else ""

    if not _window_open(now, _window_s(), flag):
        would = _select_facet(last_key, candidates)
        return TurnEndSnapshot(
            selected=None,
            session_id=sid,
            silence=SilenceReason.WINDOW_CLOSED,
            silence_facet_key=would.key.value if would is not None else "",
        )

    selected = _select_facet(last_key, candidates)
    if selected is None:
        return TurnEndSnapshot(
            selected=None, session_id=sid, silence=SilenceReason.ALL_FACETS_KILLED
        )

    # Record the window flag FIRST (a crash after this still dedupes), then telemetry
    # happens in build_nudge only if the facet actually reflects.
    _write_flag(now, selected.key.value, _flag_path())
    return TurnEndSnapshot(selected=selected, session_id=sid)


def _record_silence(session_id: str, reason: SilenceReason, facet_key: str = "") -> None:
    """Record a default-silence no-op to the silence sink (the measurement leash)."""
    append_telemetry(
        build_silence_record(facet_key, session_id, reason), silence_telemetry_path()
    )


def build_nudge(snapshot: TurnEndSnapshot) -> HookDecision:
    """Run the selected facet's Template Method → a ``block`` or a no-op.

    A non-silent result becomes a ``decision:"block"`` re-prompt carrying the facet's
    payload + a FIRING telemetry record; a silent result (or no selection) → no-op.
    When the snapshot carries a ``SilenceReason``, a SILENCE record is written so the
    query can measure firing-rate AND silence-rate per facet.
    """
    if snapshot.selected is None:
        if snapshot.silence is not None:
            _record_silence(
                snapshot.session_id, snapshot.silence, snapshot.silence_facet_key
            )
        return HookDecision.noop()

    facet = snapshot.selected
    # ON_TURN_END facets trigger on the turn-end itself (no stdin signal needed), so a
    # synthetic empty HookInput is sufficient — their classify/check are pure of the
    # Stop payload.
    result = facet.reflect(HookInput(raw={}, ok=True))
    if result.is_silent or result.payload is None:
        # A selected facet DECLINED. read_substrate already wrote the window flag, so
        # a decline still consumes the window — the next Stop dedupes.
        _record_silence(
            snapshot.session_id, SilenceReason.FACET_DECLINED, facet.key.value
        )
        return HookDecision.noop()

    append_telemetry(
        build_telemetry_record(facet.key.value, snapshot.session_id), telemetry_path()
    )
    return HookDecision.block(result.payload)


def main() -> int:
    """Parse Stop stdin, drive the read → nudge pair, emit the decision (always exit 0).

    FAIL-OPEN: any unexpected error → emit nothing (allow the turn to end). A Stop
    must never be blocked by a hook error.
    """
    try:
        snapshot = read_substrate(parse_stdin())
        return build_nudge(snapshot).emit()
    except Exception:  # noqa: BLE001 — FAIL-OPEN: never block a Stop on a hook error.
        return 0


if __name__ == "__main__":
    sys.exit(main())
