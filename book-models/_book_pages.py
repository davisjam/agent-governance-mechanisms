"""Shared book-page resolver for the declared book-models validators.

The book's chapter pages live under `book/<subdir>/<N>.<M>-slug.md`. Two declared models resolve a
`page_slug` against that set — the metrics dashboard (`defined_in.page_slug`) and the metaphor-spans
model (`introduced_at`/`pays_off_at.page_slug`). This module is the single derivation both consume, per
the extract-on-the-second-site rule: the page-slug set lives in ONE place, so a chapter added or renamed
updates every model at once.

`book_page_slugs()` — every chapter page slug the book currently defines.
`chapter_md_path(page_slug)` — the on-disk `.md` for a slug (or None), for the anchor walk.
`book_dir()` — the `book/` root.
"""
from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # the governance-catalog repo root (book-models/ is one level down)
_BOOK = os.path.join(_ROOT, "book")

#: The chapter-bearing subdirectories, in reading order. Part 6 (Reflections) and Part 7 (Back Matter
#: apparatus) replaced the old single `backmatter/` when the closing chapters were promoted to a named Part.
_SUBDIRS = ("frontmatter", "part1", "part2", "part3", "part4", "part5", "part6", "part7")

#: A chapter file name is `<N>.<M>-slug.md`.
_CHAPTER_RE = re.compile(r"\d+\.\d+-")


def book_dir() -> str:
    return _BOOK


def book_page_slugs() -> "set[str]":
    """Every chapter page slug the book currently defines (part dirs + front/back matter) — the resolve set
    a declared model's `page_slug` fields must land in."""
    slugs: "set[str]" = set()
    for sub in _SUBDIRS:
        d = os.path.join(_BOOK, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith(".md") and _CHAPTER_RE.match(fn):
                slugs.add(fn[:-3])
    return slugs


def chapter_md_path(page_slug: str) -> "str | None":
    """The on-disk `.md` path for a chapter page slug, searched across the chapter subdirs, or None if the
    slug names no chapter. Used to walk a chapter's anchors."""
    for sub in _SUBDIRS:
        p = os.path.join(_BOOK, sub, f"{page_slug}.md")
        if os.path.isfile(p):
            return p
    return None
