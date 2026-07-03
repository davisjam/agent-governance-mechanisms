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


def html_files() -> list[str]:
    """Every built page, minus the plugin bundle (which is markdown, not a served site)."""
    return [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
            if os.sep + "plugin" + os.sep not in f]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
