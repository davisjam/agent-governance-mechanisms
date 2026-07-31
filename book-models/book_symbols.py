"""A THIN helper over the book IR — the symbol-extraction the view-models need but `book/book_ir.py` does
not yet expose. Read-only over `book_ir`; a separate module by design (book_ir.py is owned by the C→A
migration and must not be edited here). The three accessors below are the `book_ir` extensions wanted for
reconciliation once that migration lands — see `book-models/DESIGN.md` §6.

WHAT IT COMPUTES (that book_ir does not, today):
  1. Heading `{#slug}` id + id-stripped text, parsed with the renderer's OWN `_HEADING_ANCHOR_RE` SSOT.
  2. The topic-sentence pairing: a heading → the first paragraph block that follows it.
  3. A stable section id: the explicit `{#slug}` when present, else a slug derived from the heading text.

TOKENIZER SSOT.  Heading-anchor parsing imports the renderer's `_HEADING_ANCHOR_RE` rather than re-typing
it, so there is exactly one heading-anchor grammar in the repo (the same discipline book_ir uses for its
block tokenizer). Slugification is the only local rule (no renderer counterpart exists to borrow).
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field

_BOOK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "book")
if _BOOK_DIR not in sys.path:
    sys.path.insert(0, _BOOK_DIR)

import book_ir  # noqa: E402 — path set above; the book IR is the read-only data source
import build_book_html as bb  # noqa: E402 — the SSOT for the heading-anchor grammar (_HEADING_ANCHOR_RE)

#: The renderer's own heading-anchor grammar — imported, never re-typed (tokenizer SSOT).
_HEADING_ANCHOR_RE = bb._HEADING_ANCHOR_RE
#: One sentence terminator run — a `.`/`?`/`!` followed by whitespace or end. Kept simple on purpose:
#: a topic sentence is a coarse signal (does this section open on a stated point?), not a parse target.
_SENTENCE_END = re.compile(r"(?<=[.?!])\s")
_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """A stable, lowercase, hyphen-joined slug of heading text — the derived section id when a heading
    carries no explicit `{#slug}`. Deterministic so the same heading always yields the same id."""
    return _SLUG_STRIP.sub("-", text.lower()).strip("-")


def heading_level(block: "book_ir.Block") -> int:
    """The heading depth (2–4), derived from the raw `#` run rather than trusting `book_ir.Block.heading_level`.

    WHY not the IR field: `book_ir` computes `heading_level` from the block's ORIGINAL first line, but when a
    marker comment (e.g. `<!-- index-def: … -->`) is glued to the head of the same block, that first line is
    the marker, so the IR field reads 0 for a real H2. We re-derive from the heading line the IR left in
    `raw`. This is `book_ir` bug B1 in DESIGN §6 — fold the fix into book_ir on reconciliation."""
    line = block.raw.strip()
    return len(line) - len(line.lstrip("#"))


def heading_id_and_text(block: "book_ir.Block") -> "tuple[str | None, str]":
    """Split a heading block's raw `## Title {#slug}` into (explicit_id_or_None, visible_text). Uses the
    renderer's `_HEADING_ANCHOR_RE` SSOT to peel the `{#slug}`, then strips the leading `#`s. This is the
    `book_ir.Block.heading_id` / `.heading_text` extension wanted for reconciliation (DESIGN §6.1)."""
    raw = block.raw.strip()
    body = raw.lstrip("#").strip()  # drop the `##`/`###` prefix; heading_level() carries the depth
    m = _HEADING_ANCHOR_RE.search(body)
    if m:
        return m.group(1), body[: m.start()].rstrip()
    return None, body


def first_sentence(text: str) -> str:
    """The first sentence of a paragraph block — the topic sentence. A coarse split on `.?!`-then-space;
    a paragraph with no terminator returns whole (a one-clause topic sentence)."""
    flat = " ".join(text.split())
    parts = _SENTENCE_END.split(flat, maxsplit=1)
    return parts[0].strip()


@dataclass
class HeadingRow:
    """A heading joined to its stable id, visible text, and the topic sentence that follows it."""
    chapter_slug: str
    part: int
    level: int
    heading_text: str
    section_id: str                    # explicit {#slug} if present, else slugify(heading_text)
    id_source: str                     # "explicit" | "derived"
    topic_sentence: str | None         # first sentence of the following paragraph, or None (an O2 finding)
    block_index: int


def _following_topic_sentence(blocks: "list[book_ir.Block]", i: int) -> "str | None":
    """The topic sentence for the heading at blocks[i]: the first sentence of the first PARA block after it,
    skipping inert DIRECTIVE markers (a `<!-- index-def -->` glued under a heading). None if the heading is
    followed by a float/list/code/heading with no intervening paragraph — the O2 finding."""
    j = i + 1
    while j < len(blocks) and blocks[j].kind is book_ir.BlockKind.DIRECTIVE:
        j += 1
    if j < len(blocks) and blocks[j].kind is book_ir.BlockKind.PARA:
        return first_sentence(blocks[j].raw)
    return None


def heading_rows(include_appendices: bool = False) -> list[HeadingRow]:
    """Every narrative heading (H2–H4; the H1 chapter title is rendered separately by the build and is not a
    block) as a typed row with its stable id, id-source, and topic sentence. The outline view's raw material.
    Derived fresh from `book_ir.parse_book()` on every call — never snapshotted (DESIGN §4)."""
    doc = book_ir.parse_book(include_appendices=include_appendices)
    rows: list[HeadingRow] = []
    for c in doc.chapters:
        for i, b in enumerate(c.blocks):
            if b.kind is not book_ir.BlockKind.HEADING:
                continue
            explicit_id, text = heading_id_and_text(b)
            rows.append(HeadingRow(
                chapter_slug=c.slug,
                part=c.part,
                level=heading_level(b),  # re-derived; the IR field is 0 for a marker-glued heading (bug B1)
                heading_text=text,
                section_id=explicit_id or slugify(text),
                id_source="explicit" if explicit_id else "derived",
                topic_sentence=_following_topic_sentence(c.blocks, i),
                block_index=b.index,
            ))
    return rows
