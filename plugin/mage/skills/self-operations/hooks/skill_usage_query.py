#!/usr/bin/env python3
"""skill_usage_query.py — the cross-log correlation query (the reflection→action join).

PORTABLE. Stdlib-only. Zero project coupling. This is the join that the sibling
``reflection_turn_end_query.py`` explicitly punts on: correlating a reflection
FIRING against a real downstream action. Here the "action" is a custom-skill
invocation, and the two sinks are:

  - skill-usage-telemetry.jsonl        — one line per Skill tool call
    (``hook_skill_usage_telemetry.py``'s sink), tagged with ``skill`` + ``session_id``.
  - reflection-turn-end-telemetry.jsonl — one line per reflection FIRING
    (the ON_TURN_END emitter's sink), tagged with ``facet_key`` + ``session_id``.

Joined BY ``session_id``, they answer the keep-or-pull question a soft nudge lives
or dies on: *did a reflection nudge ever precede an actual skill invocation in the
same session?* A facet that fires but never precedes a skill call is noise — pull
it. One that reliably precedes one earns its keep.

The join is deliberately coarse — same-session co-occurrence, NOT strict temporal
"the nudge came first" (the ``ts`` is a ``YYMMDD.HHMMSS`` string, comparable, but a
firing and an invocation in the same session is already the signal you want; a
matched pair means "in this session, a nudge fired AND a skill was later invoked").
Optionally restrict the invocation side to one skill with ``--skill``.

Usage:
  python3 skill_usage_query.py                          # firings, invocations, matched pairs
  python3 skill_usage_query.py --skill self-governance  # only count invocations of one skill
  python3 skill_usage_query.py --facet failure_control  # only count firings of one facet
  python3 skill_usage_query.py --since 260721           # on/after date (ts YYMMDD prefix)
  python3 skill_usage_query.py --json                   # machine-readable output

Exit codes: 0 = success, 1 = runtime error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

# Import the sink paths from the two emitters so each path is defined ONCE — the
# query and the emitters can never drift on a file name.
_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from hook_skill_usage_telemetry import telemetry_path as skill_usage_path  # noqa: E402
from reflection_turn_end_query import telemetry_path as reflection_firing_path  # noqa: E402


def load_records(path: Path) -> list[dict[str, Any]]:
    """Load JSONL records from a telemetry sink (malformed lines skipped; [] if absent).

    A partial write from a fail-open hook must not crash the reader.
    """
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            obj: Any = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict):
            records.append(cast("dict[str, Any]", obj))
    return records


def _ts_date_prefix(record: dict[str, Any]) -> str:
    """The ``YYMMDD`` date prefix of a record's ``ts`` (empty if malformed)."""
    ts = record.get("ts")
    if not isinstance(ts, str):
        return ""
    return ts.split(".", 1)[0]


def filter_since(
    records: list[dict[str, Any]], since: str | None
) -> list[dict[str, Any]]:
    """Filter records by ``--since`` (YYMMDD date-prefix ≥)."""
    if not since:
        return records
    return [r for r in records if _ts_date_prefix(r) >= since]


def _str_field(record: dict[str, Any], key: str) -> str:
    val = record.get(key)
    return val if isinstance(val, str) else ""


def correlate(
    firings: list[dict[str, Any]],
    invocations: list[dict[str, Any]],
    facet: str | None,
    skill: str | None,
) -> dict[str, Any]:
    """Join reflection firings against skill invocations by ``session_id``.

    Optionally restrict firings to one ``facet`` and invocations to one ``skill``.
    A "matched pair" session is one that has BOTH ≥1 firing AND ≥1 invocation.
    Returns the counts + the matched session ids (the keep-or-pull evidence).
    """
    if facet is not None:
        firings = [r for r in firings if _str_field(r, "facet_key") == facet]
    if skill is not None:
        invocations = [r for r in invocations if _str_field(r, "skill") == skill]

    firing_sessions = {
        s for r in firings if (s := _str_field(r, "session_id"))
    }
    invocation_sessions = {
        s for r in invocations if (s := _str_field(r, "session_id"))
    }
    matched = firing_sessions & invocation_sessions
    return {
        "firings": len(firings),
        "invocations": len(invocations),
        "firing_sessions": len(firing_sessions),
        "invocation_sessions": len(invocation_sessions),
        "matched_sessions": sorted(matched),
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="skill_usage_query.py",
        description=(
            "Reflection-firing ↔ skill-invocation correlation, joined by session_id "
            "(the keep-or-pull leash the reflection query punts on)."
        ),
    )
    parser.add_argument(
        "--since",
        metavar="YYMMDD",
        default=None,
        help="Only count records on/after this date (compared to the ts YYMMDD prefix).",
    )
    parser.add_argument(
        "--facet",
        metavar="KEY",
        default=None,
        help="Restrict reflection firings to one facet key (e.g. failure_control).",
    )
    parser.add_argument(
        "--skill",
        metavar="NAME",
        default=None,
        help="Restrict invocations to one skill name (e.g. self-governance).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a table.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        firings = filter_since(load_records(reflection_firing_path()), args.since)
        invocations = filter_since(load_records(skill_usage_path()), args.since)
    except OSError as exc:
        print(f"skill_usage_query: ERROR reading telemetry log: {exc}", file=sys.stderr)
        return 1

    result = correlate(firings, invocations, args.facet, args.skill)
    if args.json:
        print(
            json.dumps(
                {
                    "since": args.since,
                    "facet": args.facet,
                    "skill": args.skill,
                    **result,
                }
            )
        )
        return 0

    window = f" since {args.since}" if args.since else ""
    facet_str = f" facet={args.facet}" if args.facet else ""
    skill_str = f" skill={args.skill}" if args.skill else ""
    print(
        f"reflection↔skill correlation{window}{facet_str}{skill_str}: "
        f"{result['firings']} reflection firing(s), "
        f"{result['invocations']} skill invocation(s)"
    )
    print(
        f"  sessions: {result['firing_sessions']} with a firing, "
        f"{result['invocation_sessions']} with an invocation, "
        f"{len(result['matched_sessions'])} with BOTH (matched pairs)"
    )
    if result["matched_sessions"]:
        for sid in result["matched_sessions"]:
            print(f"    matched session: {sid}")
    elif result["firings"] and result["invocations"]:
        print("  (no session had both — a firing never preceded an invocation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
