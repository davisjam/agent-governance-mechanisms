"""Shared helpers + constants for the test suite. Imported by every test-kind module.

`resolve` semantics (used across the checks): a relative target file must exist; a `#anchor` matches a
heading-slug (markdown) or an `id`/`name` (html) in the target; `http(s)`/`mailto`/`data:` links are out
of scope (the suite does no network).
"""
from __future__ import annotations

import glob
import os
import re
import socket
import subprocess

import catalog  # the catalogue's shared model (ROOT, all_entries, catalogue_md_files, ...)

ROOT = catalog.ROOT
SKILL = os.path.join(ROOT, "plugin", "self-governance")
SKILLDIR = os.path.join(SKILL, "skills", "self-governance")
SKILLREF = os.path.join(SKILLDIR, "reference")

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


def rel(p: str) -> str:
    return os.path.relpath(p, ROOT)


def slug(heading: str) -> str:
    """GitHub-style heading slug: lowercase, drop punctuation (keep word chars + hyphen), spaces->hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def changed_vs_origin() -> frozenset[str] | None:
    """Repo-relative paths that differ from `origin/main` — committed-but-unpushed + uncommitted +
    new-untracked — used to skip a check whose declared inputs didn't change (see `needs_run`).

    Returns None when no baseline is available (missing `origin/main` ref, or not a git tree); callers
    then run every check. This is fail-SAFE, never fail-open: a stale baseline over-includes (runs more
    checks), and a missing one runs all — neither can skip a check whose input really changed.
    """
    if run(["git", "rev-parse", "--verify", "--quiet", "origin/main"]).returncode != 0:
        return None
    diff = run(["git", "diff", "--name-only", "origin/main"])
    if diff.returncode != 0:
        return None
    names = set(diff.stdout.splitlines())
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"])  # new files absent from origin
    if untracked.returncode == 0:
        names |= set(untracked.stdout.splitlines())
    return frozenset(n for n in names if n)


def html_files() -> list[str]:
    """Every built page, minus the plugin bundle (which is markdown, not a served site)."""
    return [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
            if os.sep + "plugin" + os.sep not in f]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
