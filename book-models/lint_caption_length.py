"""LINT `caption-length` — a figure/table caption is capped at 3 sentences AND 50 words.

A caption names what a figure shows and states the one point it carries; the elaboration belongs in the
prose. Left ungoverned, captions grow into paragraphs — one ran to eight sentences and 126 words. This
check caps every authored figure and table caption at **3 sentences AND 50 words**.

HARD cap, no dispensation. Unlike most book lints, this one has **no `noqa` escape** — a caption over the
cap is a finding, always, by author instruction. The remedy is to trim the caption, never to suppress.

Scope — the captions an author writes in a chapter source `.md`:
  * `<!-- figure: <path> | <caption> -->` — the text after the pipe.
  * `<!-- table: <caption> [short: <short>] -->` — the display caption (the trailing `[short: …]`
    print-index variant is stripped before counting).
Generated appendix/catalogue captions are rendered elsewhere and are out of scope here.

Counting (after stripping markdown emphasis and reducing `[text](url)` links to their text):
  * **words** — whitespace-separated tokens.
  * **sentences** — runs terminated by `.`/`!`/`?` followed by whitespace or end-of-string, so a decimal
    inside a number (`7.89%`) or a mid-token dot does not split. A bold lead-in title (`*The Net.*`) counts
    as one sentence, which is the intent: title plus two sentences, or three sentences and no title.

    python3 book-models/lint_caption_length.py            # print findings, exit 1 if any (blocking)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
from dataclasses import dataclass

HERE = pathlib.Path(__file__).resolve().parent
BOOK = HERE.parent / "book"

# Chapter source dirs — front/back matter + the five parts. Appendix fills / README / manifests are not
# authored-caption chapters, matching the book suite's own chapter-source scope.
CHAPTER_DIRS = ("frontmatter", "part1", "part2", "part3", "part4", "part5", "backmatter")

MAX_SENTENCES = 3
MAX_WORDS = 50

_FIGURE_RE = re.compile(r"<!--\s*figure:\s*(.*?)\s*-->", re.S)
_TABLE_RE = re.compile(r"<!--\s*table:\s*(.*?)\s*-->", re.S)
_SHORT_RE = re.compile(r"\s*\[short:.*?\]\s*$", re.I | re.S)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_EMPH_RE = re.compile(r"[*_`]")
_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")


@dataclass(frozen=True)
class Finding:
    file: str
    kind: str          # "figure" | "table"
    ref: str           # the figure asset, or "" for a table
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


def _src_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for d in CHAPTER_DIRS:
        dp = BOOK / d
        if dp.is_dir():
            out.extend(sorted(dp.glob("*.md")))
    return out


def _check_caption(f: pathlib.Path, kind: str, ref: str, caption: str) -> Finding | None:
    caption = caption.strip()
    if not caption:
        return None
    w, s = count_words(caption), count_sentences(caption)
    if w > MAX_WORDS or s > MAX_SENTENCES:
        return Finding(os.path.relpath(f, BOOK.parent), kind, ref, w, s, caption)
    return None


def findings() -> list[Finding]:
    out: list[Finding] = []
    for f in _src_files():
        txt = f.read_text(encoding="utf-8")
        for m in _FIGURE_RE.finditer(txt):
            src, _sep, caption = m.group(1).partition("|")
            fnd = _check_caption(f, "figure", src.strip(), caption)
            if fnd:
                out.append(fnd)
        for m in _TABLE_RE.finditer(txt):
            caption = _SHORT_RE.sub("", m.group(1))
            fnd = _check_caption(f, "table", "", caption)
            if fnd:
                out.append(fnd)
    return out


def summary_line(fs: list[Finding]) -> str:
    return (f"{len(fs)} caption(s) over the cap "
            f"(≤{MAX_SENTENCES} sentences AND ≤{MAX_WORDS} words; hard, no dispensation)")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    fs = findings()
    print(f"== caption-length — figure/table captions ≤{MAX_SENTENCES} sentences AND ≤{MAX_WORDS} words "
          f"(HARD, no noqa) ==")
    if not fs:
        print("  clean — every caption is within the cap")
        return 0
    print(f"  {summary_line(fs)}:")
    for f in sorted(fs, key=lambda x: (-x.words, -x.sentences)):
        tag = f"{f.kind} {f.ref}".strip()
        print(f"    [{f.words:3d}w {f.sentences}s] {f.file} — {tag}")
        print(f"        {f.caption[:110]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
