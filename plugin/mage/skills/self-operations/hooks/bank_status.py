"""bank_status.py — the atomic dual-write banking substrate (both-or-nothing).

PORTABLE. Stdlib-only. This is the runnable HARD machinery under the L2
manage-context lifecycle's "bank-before-compaction" runbook step: it writes a SET
of status artifacts (a strategy file, a handoff file, whatever pair a project banks)
so a fresh session can reconstruct in-flight state after a compaction/restart.

────────────────────────────────────────────────────────────────────────────────
THE ATOMICITY INVARIANT (state it plainly)

A bank is **both-or-nothing across the whole artifact set.** The banker first
RENDERS every artifact into memory; only if EVERY render succeeds does it write ANY
of them. If any render raises, NOTHING is written — the on-disk set is left exactly
as it was. Each individual write is itself atomic (temp-file + ``os.replace``, an
atomic rename on POSIX), so a reader never sees a half-written file either.

Why this matters: the failure this kills is the **inconsistent bank** — artifact A
written with fresh state, artifact B left stale (or half-written) because the run
died between the two writes. A resume that reads the pair then gets a torn picture:
a strategy that references a plan the handoff never mentions. Making the two writes
all-or-nothing makes that torn state unrepresentable in the happy path.

PARAMETERIZED. This substrate is NOT hardcoded to any project's two files. The
caller supplies the artifact set as ``StatusArtifact`` records — each a (name, path,
render-callable) triple — so the same engine banks one artifact, two, or five. The
render callable owns HOW an artifact's text is produced (read-modify-write, template
fill, machine-generate — the banker doesn't care); the banker owns the atomic WHEN.

Optional prior-edition snapshot: before overwriting an artifact the banker can copy
the current on-disk version to a ``.bak`` sibling, so a bad bank is one ``mv`` from
recovery. No elaborate retention/GC — one ``.bak`` per artifact, overwritten each run.

State-bearing (it owns the artifact set + the snapshot flag across its methods), so
``StatusBanker`` is a class, not a module of free functions.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# The machine-readable banked-at stamp format (YYMMDD.HHMMSS) — a precise stamp so
# successive banks don't collide and a staleness check can read the age. The render
# callable receives it so an artifact MAY embed it; the banker does not require it.
BANKED_AT_FMT = "%y%m%d.%H%M%S"


# ---------------------------------------------------------------------------
# Types (named before decomposition)
# ---------------------------------------------------------------------------


class BankStatusError(RuntimeError):
    """Raised on a mis-shaped bank request or a render failure (fail-loud).

    The one place both-or-nothing is enforced on the render side: a render callable
    that raises is wrapped in this error BEFORE any write happens, so the whole bank
    aborts with nothing written rather than one-siding the set.
    """


@dataclass(frozen=True)
class StatusArtifact:
    """One artifact in the banked set — a (name, path, render) triple.

    - ``name`` — a short logical id (used for the ``.bak`` naming + the RESULT lines).
    - ``path`` — where the artifact lives on disk.
    - ``render`` — a callable ``(banked_at: str) -> str`` returning the artifact's
      FULL new text. It owns the artifact's content strategy (read-modify-write,
      template, machine-generate); the banker only calls it and writes the result.
      It receives the shared ``banked_at`` stamp so every artifact in one bank can
      carry the SAME stamp (so their mtimes/stamps agree — the consistency signal).
    """

    name: str
    path: Path
    render: Callable[[str], str]


@dataclass(frozen=True)
class ArtifactBankResult:
    """The per-artifact outcome of one bank (part of the RESULT envelope)."""

    name: str
    path: str
    bytes_written: int
    snapshotted: bool  # True iff a prior .bak was written before overwrite.


@dataclass(frozen=True)
class BankResult:
    """The whole-bank outcome — every artifact, since a bank is all-or-nothing."""

    banked_at: str  # the shared YYMMDD.HHMMSS stamp passed to every render.
    artifacts: tuple[ArtifactBankResult, ...]


# ---------------------------------------------------------------------------
# The banker (state-bearing → a class)
# ---------------------------------------------------------------------------


class StatusBanker:
    """Atomic dual-write banker for an arbitrary SET of status artifacts.

    Owns the artifact set + the snapshot flag across ``bank`` / snapshot / write
    methods (state → class). Renders ALL artifacts first, then — only if every render
    succeeded — writes each via temp-file + ``os.replace``. A render failure aborts
    the whole bank with nothing written (the both-or-nothing invariant).
    """

    def __init__(
        self,
        artifacts: list[StatusArtifact],
        *,
        keep_snapshot: bool = True,
    ) -> None:
        if not artifacts:
            raise BankStatusError(
                "a bank needs at least one artifact — pass the (name, path, render) "
                "set this project banks together."
            )
        self.artifacts = tuple(artifacts)
        self.keep_snapshot = keep_snapshot

    # -- atomic single-file write ------------------------------------------

    @staticmethod
    def _atomic_write(path: Path, text: str) -> int:
        """Write ``text`` to ``path`` via temp-file + ``os.replace`` (atomic on POSIX).

        Returns bytes written. The temp file sits in the SAME directory so the
        replace is a same-filesystem rename (atomic); a cross-dir temp would degrade
        to a non-atomic copy+unlink. A reader thus never sees a half-written file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode("utf-8")
        tmp = path.parent / f".{path.name}.bank-tmp-{os.getpid()}"
        tmp.write_bytes(data)
        os.replace(tmp, path)
        return len(data)

    def _snapshot_prior(self, artifact: StatusArtifact) -> bool:
        """Copy the current on-disk artifact to a ``.bak`` sibling before overwrite.

        Returns True iff a snapshot was written. A missing file (nothing to snapshot)
        or a disabled ``keep_snapshot`` returns False. Best-effort recovery aid, not a
        retention system — one ``.bak`` per artifact, overwritten each run.
        """
        if not self.keep_snapshot or not artifact.path.exists():
            return False
        bak = artifact.path.with_name(artifact.path.name + ".bak")
        bak.write_bytes(artifact.path.read_bytes())
        return True

    # -- the one banking call (both-or-nothing) ----------------------------

    def bank(self, *, now: datetime | None = None) -> BankResult:
        """Atomically bank the WHOLE artifact set (both-or-nothing).

        Two phases, in order:
          1. **Render all.** Call every artifact's ``render(banked_at)`` into memory.
             A render that raises aborts here — NOTHING has been written yet, so the
             on-disk set is untouched (the atomicity invariant's load-bearing half).
          2. **Write all.** Snapshot each prior edition (optional ``.bak``), then write
             each via ``_atomic_write``. Every artifact carries the SAME ``banked_at``
             stamp so a reader can confirm the set was banked together.

        Returns a ``BankResult`` describing every write (for the RESULT envelope).
        """
        stamp = (now or datetime.now(timezone.utc)).strftime(BANKED_AT_FMT)

        # Phase 1 — render EVERYTHING first (nothing on disk changes yet).
        rendered: list[tuple[StatusArtifact, str]] = []
        for artifact in self.artifacts:
            try:
                text = artifact.render(stamp)
            except Exception as exc:  # noqa: BLE001 — re-raise as a domain error; the point is to abort the WHOLE bank before any write, so a torn set is impossible. Justified swallow-and-convert (never a silent catch).
                raise BankStatusError(
                    f"render failed for artifact {artifact.name!r} ({artifact.path}); "
                    f"aborting the whole bank with NOTHING written (both-or-nothing): {exc}"
                ) from exc
            if not isinstance(text, str):
                raise BankStatusError(
                    f"render for artifact {artifact.name!r} returned "
                    f"{type(text).__name__}, not str — aborting the bank."
                )
            rendered.append((artifact, text))

        # Phase 2 — every render succeeded: now write them all.
        results: list[ArtifactBankResult] = []
        for artifact, text in rendered:
            snapped = self._snapshot_prior(artifact)
            n = self._atomic_write(artifact.path, text)
            results.append(
                ArtifactBankResult(
                    name=artifact.name,
                    path=str(artifact.path),
                    bytes_written=n,
                    snapshotted=snapped,
                )
            )
        return BankResult(banked_at=stamp, artifacts=tuple(results))


# ---------------------------------------------------------------------------
# A tiny CLI (a demonstration harness — bank two files from --set NAME=PATH pairs)
# ---------------------------------------------------------------------------

_PLAN_MARKER = "=== bank-status PLAN v1 ==="
_RESULT_MARKER = "=== bank-status RESULT v1 ==="


def _read_or_empty(path: Path) -> str:
    """Read a file's text, or '' if it does not exist (the read side of RMW)."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _stamp_render(path: Path, stamp_line_prefix: str) -> Callable[[str], str]:
    """A simple read-modify-write render: re-stamp the first line, keep the body.

    The default CLI render — a stand-in for a project's real content strategy. It
    replaces (or prepends) a ``<prefix> <stamp>`` first line and preserves the rest of
    the current file verbatim (the previous edition IS the template). Swap this for
    your own render callable when you wire ``StatusBanker`` into a hook or tool.
    """

    def render(banked_at: str) -> str:
        current = _read_or_empty(path)
        stamp_line = f"{stamp_line_prefix} {banked_at}"
        lines = current.splitlines()
        if lines and lines[0].startswith(stamp_line_prefix):
            lines[0] = stamp_line
        else:
            lines.insert(0, stamp_line)
        return "\n".join(lines) + "\n"

    return render


def _emit_plan(banker: StatusBanker) -> None:
    """Emit the planned-actions preamble to stderr (a tool must announce its plan)."""
    lines = [
        _PLAN_MARKER,
        "invariant: both-or-nothing atomic dual-write (render-all-then-write-all)",
        "planned_writes:",
        *(f"  - {a.name}: {a.path}" for a in banker.artifacts),
        f"keep_snapshot: {banker.keep_snapshot} (one .bak per artifact)",
        "=== END PLAN ===",
    ]
    print("\n".join(lines), file=sys.stderr)


def _emit_result(result: BankResult) -> None:
    """Emit the measurable RESULT envelope to stderr (a tool must report results)."""
    lines = [
        _RESULT_MARKER,
        "status: success",
        f"banked_at: {result.banked_at}",
        "artifacts:",
    ]
    for a in result.artifacts:
        lines.append(f"  - {a.name}: {a.path}")
        lines.append(f"      bytes_written: {a.bytes_written}")
        lines.append(f"      snapshotted: {a.snapshotted}")
    lines.append("=== END RESULT ===")
    print("\n".join(lines), file=sys.stderr)


def _parse_set(spec: str) -> StatusArtifact:
    """Parse a ``NAME=PATH`` CLI pair into a ``StatusArtifact`` with the default render."""
    if "=" not in spec:
        raise BankStatusError(
            f"--set expects NAME=PATH, got {spec!r} (e.g. --set strategy=STRATEGY.md)."
        )
    name, _, raw_path = spec.partition("=")
    name = name.strip()
    path = Path(raw_path.strip())
    return StatusArtifact(
        name=name,
        path=path,
        render=_stamp_render(path, stamp_line_prefix=f"<!-- banked_at:{name} -->"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bank_status.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--set",
        metavar="NAME=PATH",
        action="append",
        default=[],
        help="An artifact to bank as NAME=PATH. Repeat for each file in the set "
        "(a bank writes them all-or-nothing). At least one required.",
    )
    parser.add_argument(
        "--no-snapshot",
        action="store_true",
        help="Skip the prior-edition .bak snapshot before overwrite.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Exit codes: 0 = banked; 1 = runtime error / mis-shaped request."""
    args = build_parser().parse_args(argv)
    try:
        artifacts = [_parse_set(spec) for spec in args.set]
        banker = StatusBanker(artifacts, keep_snapshot=not args.no_snapshot)
        _emit_plan(banker)
        result = banker.bank()
    except (BankStatusError, OSError) as exc:
        print(f"bank-status: ERROR — {exc}", file=sys.stderr)
        return 1
    _emit_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BANKED_AT_FMT",
    "ArtifactBankResult",
    "BankResult",
    "BankStatusError",
    "StatusArtifact",
    "StatusBanker",
]
