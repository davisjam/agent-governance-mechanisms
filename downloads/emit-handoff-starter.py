#!/usr/bin/env python3
"""emit-handoff-starter.py — machine-generated handoff SCAFFOLD (adopt & adapt).

A distilled, portable version of a handoff generator from a production system built by
frontier coding agents. It pairs with the L2 · manage-context lifecycle model: the
handoff is the artifact a fresh session reads to reconstruct in-flight state after a
compaction/restart. This starter machine-generates the RECONSTRUCTABLE half of that
handoff from live git state, and leaves clearly-marked placeholders for the narrative
half that only human/agent judgment can fill.

Why generate the reconstructable half: re-banking must be CHEAP enough to do often
(automated compaction fires without warning). If every section is hand-retyped, you
save it once at session-end and lose the delta. Machine-generate the parts that ARE a
query — HEAD sha, worktrees, status, recent commits — so re-banking is a narrative
diff, not a rewrite.

WHAT TO FILL IN (this is a STARTER):
  - Replace the `# TODO(adapt):` blocks with YOUR project's queryable sources. The git
    sections below are generic and work in any git repo. If your project has a queue, an
    epic/task store, or a brief backlog, add a machine section that reads IT (the way the
    git helpers read git) — do NOT hand-type what you can query.
  - Keep the `<!-- TODO: narrative -->` placeholders for the judgment sections. Those are
    the point of a handoff — the machine can't know what's blocked on a user decision.

THE INVARIANT (do not remove): when `--output` is given, a successful run MUST advance
the destination file's mtime. If the write appears to succeed but mtime does not move,
the tool exits non-zero. This guards the silent-no-write class — a handoff that looks
banked but wasn't is worse than a loud failure, because a resume trusts it.

Stdlib-only. Exit codes: 0 = emitted; 1 = runtime error / mtime-did-not-advance.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections.abc import Sequence

# The sentinel a shape-check (or your eye) greps for unfilled narrative sections.
TODO_PLACEHOLDER = "<!-- TODO: narrative -->"


# ── git helpers (generic — work in any git repo) ─────────────────────────────


def _run(cmd: list[str]) -> tuple[str, int]:
    """Run a command, return (stdout, returncode). Never raises (fail-open)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except Exception as exc:  # noqa: BLE001 — a git helper must never crash the handoff; any error becomes a visible "[error]" marker in the section rather than an exception (justified swallow, documented).
        return f"[error: {exc}]", 1


def _head_sha() -> str:
    out, rc = _run(["git", "rev-parse", "HEAD"])
    return out if rc == 0 else "[unknown]"


def _current_branch() -> str:
    out, rc = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out if rc == 0 else "[unknown]"


def _git_status_short() -> str:
    out, rc = _run(["git", "status", "--short"])
    return out if rc == 0 else "[error]"


def _worktree_list() -> str:
    out, rc = _run(["git", "worktree", "list"])
    return out if rc == 0 else "[error]"


def _recent_commits(session_start: datetime) -> str:
    """One-line commits since ``session_start`` (the "what landed this session" section)."""
    since = session_start.strftime("%Y-%m-%d %H:%M:%S")
    out, rc = _run(["git", "log", "--oneline", "--since", since, "--format=%h %s"])
    if rc != 0 or not out:
        return "  (none since session start — verify the --session-start window)"
    return "\n".join(f"  - {line}" for line in out.splitlines()[:40])


def _main_repo_root() -> Path:
    """The MAIN checkout root (first entry of ``git worktree list --porcelain``).

    WHY not ``git rev-parse --show-toplevel``: from inside a linked worktree that returns
    the WORKTREE dir, so a relative --output would land in the worktree subtree instead of
    the main checkout — the silent-wrong-location bug. The porcelain list's first entry is
    always the main worktree, regardless of CWD.
    """
    out, rc = _run(["git", "worktree", "list", "--porcelain"])
    if rc == 0 and out:
        for line in out.splitlines():
            if line.startswith("worktree "):
                return Path(line[len("worktree "):].strip())
    return Path.cwd()  # fallback: best-effort.


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%y%m%d.%H%M%S")


# ── skeleton generation ──────────────────────────────────────────────────────


def build_skeleton(session_start: datetime) -> str:
    """Build the handoff Markdown: machine sections filled, narrative sections as TODOs."""
    ts = _now_stamp()
    head = _head_sha()
    branch = _current_branch()
    status = _git_status_short() or "(clean)"
    worktrees = _worktree_list()
    commits = _recent_commits(session_start)
    todo = TODO_PLACEHOLDER

    # TODO(adapt): add machine sections for YOUR queryable sources here — a queue dump, an
    # epic/task report, a brief backlog listing. Read them the way the git helpers read git.

    return f"""# Session handoff — {ts}

<!-- AUTO-GENERATED by emit-handoff-starter.py at {ts} UTC -->
<!-- MACHINE sections: regenerated from live git state on every run. -->
<!-- NARRATIVE sections: fill in the {TODO_PLACEHOLDER} placeholders by judgment. -->

## ▶ Read first (post-compaction boot)

1. You are resuming autonomous work. Default to action.
2. Read this handoff, then re-run your session-start reconstruction queries.
3. This file is stale-by-design — regenerate it as state drifts.

---

## State at handoff

<!-- MACHINE-DERIVED -->
- **Handoff stamp:** {ts} UTC
- **HEAD sha:** `{head}`
- **Branch:** `{branch}`

### git status --short
```
{status}
```

### git worktree list
```
{worktrees}
```

---

## What landed this session

<!-- MACHINE-DERIVED (commits since --session-start) -->
{commits}

---

<!-- TODO(adapt): add your queryable machine sections here (queue / epic / brief backlog). -->

## Open decisions blocked on a human

{todo}

_What is blocked on a user/reviewer call? List each + its implication._

---

## Resume priority order

{todo}

_What to do first on resume? The next ratified action, in order._

---

## Lessons / caveats

{todo}

_Drift catches, gotchas, direction-calls made, things future-you should know._

---

*Regenerate this file as state drifts (don't save-once-at-end). Delete or archive after reading.*
"""


# ── main ─────────────────────────────────────────────────────────────────────


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Exit 0 = emitted; 1 = error / mtime did not advance."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--session-start",
        metavar="DATETIME",
        help="Approx session start (ISO, e.g. '2026-01-01 10:00'), scopes 'what landed'. "
        "Default: 6 hours ago.",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Write the handoff here (relative paths resolve against the MAIN repo root). "
        "Default: stdout.",
    )
    args = parser.parse_args(argv)

    if args.session_start:
        try:
            session_start = datetime.fromisoformat(args.session_start).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            print(
                f"emit-handoff: ERROR — cannot parse --session-start "
                f"{args.session_start!r} (expected ISO, e.g. '2026-01-01 10:00').",
                file=sys.stderr,
            )
            return 1
    else:
        session_start = datetime.now(timezone.utc) - timedelta(hours=6)

    content = build_skeleton(session_start)

    if not args.output:
        print(content)
        return 0

    # Resolve a relative --output against the MAIN repo root, not CWD (the worktree fix).
    raw = Path(args.output)
    dest = raw if raw.is_absolute() else _main_repo_root() / raw

    # INVARIANT: the write must ADVANCE the file's mtime (guards the silent-no-write class).
    mtime_before = dest.stat().st_mtime if dest.exists() else None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    except OSError as exc:
        print(f"emit-handoff: ERROR writing {dest}: {exc}", file=sys.stderr)
        return 1
    mtime_after = dest.stat().st_mtime
    if mtime_before is not None and mtime_after <= mtime_before:
        print(
            f"emit-handoff: ERROR — wrote content but mtime did not advance "
            f"(before={mtime_before:.3f}, after={mtime_after:.3f}). The handoff may be "
            f"silently unwritten; check {dest} is writable.",
            file=sys.stderr,
        )
        return 1

    print(
        f"emit-handoff: wrote {len(content.encode('utf-8'))} bytes to {dest}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
