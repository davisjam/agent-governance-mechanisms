"""LINT `caption-length` — every figure/table caption is sized to its argumentative TIER, not one flat cap.

A caption's length should match the job the figure does. An anchor figure that introduces or summarizes a
major idea earns a rich caption a reader can learn the idea from; a reference visual earns one identifying
sentence. The retired uniform cap (<=3 sentences AND <=50 words for every caption) squeezed the book's
central method diagram and its author photo to the same budget. This check replaces that one ceiling with
**per-tier bands**, read from the declared registry `book-models/figure-caption-tiers.json`:

  * **A — Anchor**     4-8 sentences / 60-120 words. Carries a FLOOR: an under-written anchor is a finding.
  * **B — Supporting** 2-4 sentences / 25-70 words.
  * **C — Reference**  1-2 sentences / <=30 words.

Band semantics (symmetric with the retired cap's AND-ceiling):
  * CEILING violated when words > max OR sentences > max  (a caption must be under BOTH maxima).
  * FLOOR violated when words < min AND sentences < min  (a caption must meet at least ONE minimum) —
    so a 4-sentence-but-terse caption still satisfies an A/B floor. C has no meaningful floor.

HARD, no dispensation. Like the retired cap, this lint has **no `noqa` escape** — an off-band caption is a
finding, always, by author instruction. The remedy is to resize the caption to its band, never to suppress.
A caption whose id is absent from the registry is itself a finding (drift defense — a new figure/table must
declare its tier, mirroring brick-fitness's "dense diagram with no verdict").

Scope — the captions an author writes in a chapter source `.md`:
  * `<!-- figure: <path> | <caption> -->`   — keyed on the asset path (`<path>`).
  * `<!-- table: <caption> [short: <short>] -->` — keyed on `<chapter-file>::<short>` (the `[short: ...]`
    print-index name; the display caption is counted, the `[short: ...]` tail stripped before counting).
Generated appendix/catalogue captions are rendered elsewhere and are out of scope here.

Counting (after stripping markdown emphasis and reducing `[text](url)` links to their text):
  * **words** — whitespace-separated tokens.
  * **sentences** — runs terminated by `.`/`!`/`?` followed by whitespace or end-of-string, so a decimal
    inside a number (`7.89%`) or a mid-token dot does not split. A bold lead-in title (`*The Net.*`) counts
    as one sentence, which is the intent.

    python3 book-models/lint_caption_length.py            # print findings, exit 1 if any

LANDING: AUDIT-ONLY first (rule #55). The tree carried every caption at the retired <=3/<=50 cap, so all
A-tier captions are under-length on day one. `catalog.py validate` invokes this as a NON-gating sensor; the
Phase-3 caption-rewrite wave drains the findings to zero, then a follow-up promotes it to blocking. See
book/_design/drafts/caption-tier-model-260806.md.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
REGISTRY = HERE / "figure-caption-tiers.json"

# Chapter source dirs — front/back matter + the five parts. Appendix fills / README / manifests are not
# authored-caption chapters, matching the book suite's own chapter-source scope.
CHAPTER_DIRS = ("frontmatter", "part1", "part2", "part3", "part4", "part5", "part6", "part7")

#: Per-tier band as (min_sentences, max_sentences, min_words, max_words). §2.1 of the caption-tier design.
#: Floor uses the minima (satisfied by meeting EITHER dimension); ceiling uses the maxima (must be under
#: BOTH). C's minima are 1/0 — a non-empty caption always clears them, so C is effectively ceiling-only.
BANDS: dict[str, tuple[int, int, int, int]] = {
    "A": (4, 8, 60, 120),
    "B": (2, 4, 25, 70),
    "C": (1, 2, 0, 30),
}

_FIGURE_RE = re.compile(r"<!--\s*figure:\s*(.*?)\s*-->", re.S)
_TABLE_RE = re.compile(r"<!--\s*table:\s*(.*?)\s*-->", re.S)
_SHORT_VALUE_RE = re.compile(r"\[short:\s*(.*?)\s*\]", re.I | re.S)
_SHORT_STRIP_RE = re.compile(r"\s*\[short:.*?\]\s*$", re.I | re.S)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_EMPH_RE = re.compile(r"[*_`]")
_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")


@dataclass(frozen=True)
class Finding:
    file: str
    kind: str          # "figure" | "table"
    ref: str           # the figure asset, or the table short name
    tier: str          # "A" | "B" | "C" | "?" (untiered)
    reason: str        # "OVER" | "UNDER" | "UNTIERED"
    words: int
    sentences: int
    caption: str


def _plain(caption: str) -> str:
    """Strip markdown emphasis and reduce links to their visible text — the countable prose."""
    return _EMPH_RE.sub("", _LINK_RE.sub(r"\1", caption)).strip()


def count_words(caption: str) -> int:
    return len([w for w in re.split(r"\s+", _plain(caption)) if w])


def count_sentences(caption: str) -> int:
    return len([s for s in _SENTENCE_SPLIT.split(_plain(caption)) if s.strip()])


def _load_tiers() -> dict[str, str]:
    """Return the caption-id -> tier map from the declared registry (the stable-lint-reads-the-SSOT
    discipline; the builder and this lint share the one file, no hardcoded list)."""
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {key: row["tier"] for key, row in data["tiers"].items()}


def _src_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for d in CHAPTER_DIRS:
        dp = BOOK / d
        if dp.is_dir():
            out.extend(sorted(dp.glob("*.md")))
    return out


def _band_finding(f: pathlib.Path, kind: str, ref: str, cap_id: str, caption: str,
                  tiers: dict[str, str]) -> Finding | None:
    """One caption vs its tier band. Untiered id -> UNTIERED finding; else OVER (ceiling) / UNDER (floor)."""
    caption = caption.strip()
    if not caption:
        return None
    rel = os.path.relpath(f, BOOK.parent)
    tier = tiers.get(cap_id)
    w, s = count_words(caption), count_sentences(caption)
    if tier is None:
        return Finding(rel, kind, ref, "?", "UNTIERED", w, s, caption)
    min_s, max_s, min_w, max_w = BANDS[tier]
    if w > max_w or s > max_s:
        return Finding(rel, kind, ref, tier, "OVER", w, s, caption)
    if w < min_w and s < min_s:
        return Finding(rel, kind, ref, tier, "UNDER", w, s, caption)
    return None


def findings() -> list[Finding]:
    tiers = _load_tiers()
    out: list[Finding] = []
    for f in _src_files():
        rel_to_book = os.path.relpath(f, BOOK)
        txt = f.read_text(encoding="utf-8")
        for m in _FIGURE_RE.finditer(txt):
            src, _sep, caption = m.group(1).partition("|")
            asset = src.strip()
            fnd = _band_finding(f, "figure", asset, asset, caption, tiers)
            if fnd:
                out.append(fnd)
        for m in _TABLE_RE.finditer(txt):
            body = m.group(1)
            sm = _SHORT_VALUE_RE.search(body)
            short = sm.group(1).strip() if sm else ""
            caption = _SHORT_STRIP_RE.sub("", body)
            cap_id = f"{rel_to_book}::{short}" if short else ""
            fnd = _band_finding(f, "table", short, cap_id, caption, tiers)
            if fnd:
                out.append(fnd)
    return out


def summary_line(fs: list[Finding]) -> str:
    over = sum(1 for f in fs if f.reason == "OVER")
    under = sum(1 for f in fs if f.reason == "UNDER")
    untiered = sum(1 for f in fs if f.reason == "UNTIERED")
    return (f"{len(fs)} caption(s) off their tier band "
            f"({over} over-ceiling, {under} under-floor, {untiered} untiered; "
            f"A 4-8s/60-120w · B 2-4s/25-70w · C 1-2s/<=30w; hard, no dispensation)")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    fs = findings()
    print("== caption-length — every figure/table caption sized to its tier band "
          "(A anchor / B supporting / C reference; HARD, no noqa) ==")
    if not fs:
        print("  clean — every caption sits within its tier band")
        return 0
    print(f"  {summary_line(fs)}:")
    for f in sorted(fs, key=lambda x: (x.tier, x.reason, -x.words)):
        tag = f"{f.kind} {f.ref}".strip()
        print(f"    [{f.tier} {f.reason:8s} {f.words:3d}w {f.sentences}s] {f.file} — {tag}")
        print(f"        {f.caption[:110]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
