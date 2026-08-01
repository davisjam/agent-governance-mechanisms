#!/usr/bin/env python3
"""reflection_turn_end_query.py — the measured-leash query over the reflection telemetry.

PORTABLE. Stdlib-only. Read the ON_TURN_END reflection substrate's two sinks so it
lives on a leash per facet:

  - reflection-turn-end-telemetry.jsonl         — one line per FIRING (a reflection
    that emitted a payload), tagged with the ``facet_key`` that fired.
  - reflection-turn-end-silence-telemetry.jsonl — one line per Stop that produced NO
    reflection (a default-silence no-op), tagged with a ``reason`` + the attributed
    ``facet_key``.

Per facet you can measure: how often it FIRES, how often the substrate is SILENT
(and why). That is the keep-or-pull signal: a facet that fires a lot but never
precedes a real action is noise; one that reliably precedes one earns its keep.
**Pull (kill-switch) a facet on near-zero yield.** The correlation with a real
downstream action is inherently project-specific — wire it to whatever signals your
"the operator acted on this" (e.g. a hardening-skill invocation log); this portable
tool reports the firing/silence leash and leaves the action-join to you.

Usage:
  python3 reflection_turn_end_query.py                 # per-facet firing + silence counts
  python3 reflection_turn_end_query.py --since 260721  # on/after date (ts YYMMDD prefix)
  python3 reflection_turn_end_query.py --facet failure_control  # one facet only
  python3 reflection_turn_end_query.py --json          # machine-readable output

Exit codes: 0 = success, 1 = runtime error.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, cast

# Import the sink paths from the emitter so each path is defined ONCE — the query and
# the emitter can never drift on the file name.
_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from hook_reflection_turn_end import (  # noqa: E402
    silence_telemetry_path,
    telemetry_path,
)


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


def _facet_key(record: dict[str, Any]) -> str:
    val = record.get("facet_key")
    return val if isinstance(val, str) else ""


def _reason(record: dict[str, Any]) -> str:
    val = record.get("reason")
    return val if isinstance(val, str) else ""


def summarize_by_facet(
    fired: list[dict[str, Any]],
    silent: list[dict[str, Any]],
    facet: str | None,
) -> dict[str, dict[str, Any]]:
    """Per-facet {firings, silences, silence_by_reason} roll-up (the leash report).

    The union of facet keys seen across BOTH sinks is reported — a facet that is
    all-silent (never fired) is itself the signal.
    """
    fired_by_facet: Counter[str] = Counter(_facet_key(r) for r in fired)
    silent_by_facet: Counter[str] = Counter(_facet_key(r) for r in silent)
    reason_by_facet: dict[str, Counter[str]] = {}
    for r in silent:
        reason_by_facet.setdefault(_facet_key(r), Counter())[_reason(r)] += 1

    keys = set(fired_by_facet) | set(silent_by_facet)
    if facet is not None:
        keys = {facet}
    return {
        key: {
            "firings": fired_by_facet.get(key, 0),
            "silences": silent_by_facet.get(key, 0),
            "silence_by_reason": dict(reason_by_facet.get(key, Counter())),
        }
        for key in sorted(keys)
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="reflection_turn_end_query.py",
        description="ON_TURN_END reflection firing + silence counts, per facet (the measured leash).",
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
        help="Restrict to one facet key (e.g. failure_control).",
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
        fired = filter_since(load_records(telemetry_path()), args.since)
        silent = filter_since(load_records(silence_telemetry_path()), args.since)
    except OSError as exc:
        print(f"reflection_turn_end_query: ERROR reading telemetry log: {exc}", file=sys.stderr)
        return 1

    by_facet = summarize_by_facet(fired, silent, args.facet)
    total_firings = sum(v["firings"] for v in by_facet.values())
    total_silences = sum(v["silences"] for v in by_facet.values())
    if args.json:
        print(
            json.dumps(
                {
                    "since": args.since,
                    "facet": args.facet,
                    "total_firings": total_firings,
                    "total_silences": total_silences,
                    "by_facet": by_facet,
                }
            )
        )
        return 0

    window = f" since {args.since}" if args.since else ""
    print(
        f"ON_TURN_END reflection telemetry{window}: {total_firings} firing(s), "
        f"{total_silences} silent no-op(s)"
    )
    if not by_facet:
        print("  (no records)")
        return 0
    for key in sorted(by_facet):
        row = by_facet[key]
        reasons = row["silence_by_reason"]
        reason_str = (
            " [" + ", ".join(f"{k}={v}" for k, v in sorted(reasons.items())) + "]"
            if reasons
            else ""
        )
        print(
            f"  {key}: {row['firings']} firing(s), {row['silences']} silence(s){reason_str}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
