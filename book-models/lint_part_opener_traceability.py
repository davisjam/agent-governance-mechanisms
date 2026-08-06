"""LINT `part-opener-traceability` — every claim a Part opener foreshadows must trace to the book's spine.

THE CLASS.  A Part opener is a promise: "here is the argument this Part will convince you of." That promise
is prose, so today nothing checks that the Part actually keeps it — an opener can foreshadow a claim no
chapter advances, or a claim that connects to none of the book's Big Ideas, and the drift is invisible until
a reader notices the Part never delivered. This lint makes the promise mechanically traceable.

THE DECLARATION.  Each `book/part<N>/00-part-intro.md` carries a `<!-- part-foreshadows: <spine-id>, … -->`
decorator naming the argument-spine claim ids the opener foreshadows. The ids are the join key: they resolve
in the spine, the chapters advance them, and the spine reconciles them to the Big Ideas.

THE CHECK — the loop must CLOSE for every declared id:
  (a) RESOLVES — the id is a real node in `argument_spine_declared.json` `spine[]`.
  (b) ADVANCED-IN-PART — at least one chapter WITHIN that same Part advances it (intersect the chapter's
      `spine_advances` from `chapter-shape.json` with the Part's chapter slugs, keyed by the `N.` prefix).
  (c) TRACES-TO-A-BIG-IDEA — the spine node reconciles to at least one Big Idea via its
      `reconciles.big_ideas` (each slug resolving in `landing-big-ideas.json`). There is no transitive
      claim→big-idea path in the models, so this is the direct spine→big-idea join.

A declared id that fails any leg is a finding, reported as `part<N>: <id> — <which leg failed>`. The lint
reads the three models at lint-time (the stable-lint-reads-the-SSOT discipline); a spine or chapter-shape
edit re-derives the answer with no second copy to maintain. Stdlib-only, matching `catalog.py`'s
clone-and-run posture.

Run `python3 book-models/lint_part_opener_traceability.py` (audit-only, exit 0) or `--strict` (exit 1 on any
finding). Lands audit-only while any opener foreshadows a spine premise not yet reconciled to a Big Idea;
promotes to blocking once the loop closes for every declared id.
"""
from __future__ import annotations

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_BOOK_DIR = os.path.join(_ROOT, "book")

#: One `<!-- part-foreshadows: a, b, c -->` decorator on its own line (the traceability notation).
_FORESHADOWS_RE = re.compile(r"<!--\s*part-foreshadows:\s*(?P<ids>.*?)\s*-->", re.S)
#: A chapter slug's Part number is its leading `N.` prefix (`5.3-the-built-system` → part 5).
_PART_PREFIX_RE = re.compile(r"^(?P<part>\d+)\.")


def _load(name: str) -> dict:
    with open(os.path.join(_HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def _opener_declarations() -> "dict[int, list[str]]":
    """Map each Part number to the spine ids its `book/part<N>/00-part-intro.md` declares. A Part with no
    decorator (or no opener file) is absent from the map — the loop cannot fail on ids that were not made."""
    out: "dict[int, list[str]]" = {}
    for entry in sorted(os.listdir(_BOOK_DIR)):
        m = re.fullmatch(r"part(\d+)", entry)
        if not m:
            continue
        opener = os.path.join(_BOOK_DIR, entry, "00-part-intro.md")
        if not os.path.isfile(opener):
            continue
        with open(opener, encoding="utf-8") as fh:
            text = fh.read()
        dm = _FORESHADOWS_RE.search(text)
        if not dm:
            continue
        ids = [s.strip() for s in dm.group("ids").split(",") if s.strip()]
        out[int(m.group(1))] = ids
    return out


def _part_of(slug: str) -> "int | None":
    m = _PART_PREFIX_RE.match(slug)
    return int(m.group("part")) if m else None


def findings() -> "list[str]":
    """Every declared foreshadow id whose traceability loop does not close, as `part<N>: <id> — <reason>`."""
    spine_model = _load("argument_spine_declared.json")
    spine_by_id = {n["id"]: n for n in spine_model["spine"]}
    big_ideas = _load("landing-big-ideas.json")
    big_idea_slugs = set(big_ideas.get("_order", []))

    # spine id -> the set of Part numbers whose chapters advance it (from chapter-shape's spine_advances).
    shape = _load("chapter-shape.json")
    advanced_in_part: "dict[str, set[int]]" = {}
    for ch in shape.get("chapters", []):
        part = _part_of(ch.get("slug", ""))
        if part is None:
            continue
        for sid in ch.get("spine_advances", []):
            advanced_in_part.setdefault(sid, set()).add(part)

    out: "list[str]" = []
    for part, ids in sorted(_opener_declarations().items()):
        for sid in ids:
            node = spine_by_id.get(sid)
            if node is None:
                out.append(f"part{part}: {sid} — (a) UNRESOLVED: not a node in argument_spine_declared.json")
                continue
            if part not in advanced_in_part.get(sid, set()):
                out.append(f"part{part}: {sid} — (b) NOT-ADVANCED-IN-PART: no part-{part} chapter advances it")
            bis = [b for b in node.get("reconciles", {}).get("big_ideas", []) if b in big_idea_slugs]
            if not bis:
                out.append(f"part{part}: {sid} — (c) NO-BIG-IDEA: spine node reconciles to no Big Idea")
    return out


def main(argv: "list[str]") -> int:
    strict = "--strict" in argv[1:]
    fs = findings()
    mode = "STRICT (exit 1 on any finding)" if strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== part-opener-traceability — every foreshadowed spine id must resolve, be advanced in its Part, "
          f"and trace to a Big Idea [{mode}] ==")
    if not fs:
        print("  clean — every declared foreshadow id closes the loop (spine ✓ chapter ✓ big-idea ✓)")
        return 0
    print(f"  {len(fs)} finding(s):")
    for f in fs:
        print(f"    {f}")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
