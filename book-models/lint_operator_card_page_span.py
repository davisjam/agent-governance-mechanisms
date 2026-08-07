"""LINT lint_operator_card_page_span — the post-render ONE-PAGE-FIT sensor for the Appendix-D operator cards.

Each operator card is one page. A card fits iff its rendered title and the NEXT card's title land on
adjacent pdftotext pages (gap of one). A gap greater than one means the earlier card overflowed onto a
continuation page. Iterates the DECLARED card set (operator-cards.json), NOT a hardcoded list — the
stable-lint-reads-the-SSOT posture the caption lint uses.

Coverage note: this sensor is the backstop for LANDSCAPE cards, which render breakable and can overflow
silently. PORTRAIT cards get the compile-time keep-together assert (operator_cards_model.HARD_PAGE_ASSERT)
at the Phase-3 flip; the last card in the deck is portrait, so its overflow is caught at compile time, not
here (this sensor bounds a card by the NEXT card's page, which the last card lacks).

LANDING: AUDIT-ONLY-first (the repo's blocking-lint discipline). It PRINTS its worklist without gating; a
fit-pass drains offenders; a follow-up flips BLOCKING = True AND turns on
operator_cards_model.HARD_PAGE_ASSERT (the ordering guard couples the two). Needs a compiled PDF, so it is a
no-op when book/mage-book.pdf is absent (returns []).

    python3 book-models/lint_operator_card_page_span.py           # print worklist (exit 0, audit-only)
    python3 book-models/lint_operator_card_page_span.py --strict  # exit 1 on any span>1 (Phase-3 mode)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_SOURCE = os.path.join(HERE, "operator-cards.json")
_DEFAULT_PDF = os.path.join(ROOT, "book", "mage-book.pdf")

#: Phase-3 flip flag — the single source of truth the model's _ordering_guard reads. OFF during the audit
#: window; set True at the BLOCKING commit (paired with operator_cards_model.HARD_PAGE_ASSERT).
BLOCKING = False


def _declared_cards() -> "list[tuple[str, str, str]]":
    """(card-id, title, operator_question) in declared deck order."""
    with open(_SOURCE, encoding="utf-8") as fh:
        data = json.load(fh)
    return [(c["card-id"], c.get("title", c["card-id"]), c.get("operator_question", ""))
            for c in data["cards"]]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _per_page_text(pdf_path: str) -> "list[str]":
    """Per-page normalized text via pdftotext (form-feed split). Mirrors the book's orphan-heading sensor
    without importing the heavy builder module."""
    out = subprocess.run(["pdftotext", "-layout", pdf_path, "-"],
                         capture_output=True, text=True, check=True).stdout
    return [_norm(page) for page in out.split("\x0c")]


#: A card page opens with its title heading (title within the first N chars) AND carries the card's unique
#: operator question in its opening line. Requiring BOTH pins each card to exactly its page — a title phrase
#: that recurs as a body-chapter heading elsewhere lacks the operator question, so it never false-matches.
_HEADING_WINDOW = 80


def _card_page(pages: "list[str]", title: str, question: str) -> "int | None":
    """1-indexed page that is this card's page: the title is heading-anchored (within the first
    _HEADING_WINDOW chars) AND the card's operator question appears on the same page. None if not found."""
    t, q = _norm(title), _norm(question)
    if not t:
        return None
    for i, txt in enumerate(pages, 1):
        pos = txt.find(t)
        if pos != -1 and pos < _HEADING_WINDOW and (not q or q in txt):
            return i
    return None


def findings(pdf_path: "str | None" = None) -> "list[tuple[str, int, int]]":
    """(card-id, start_page, end_page) for every card whose rendered span exceeds one page. A card's span
    ends one page before the NEXT card's title page; the last card is bounded by the compile-time assert,
    not here. Empty when the PDF is absent (nothing to sense)."""
    pdf = pdf_path or _DEFAULT_PDF
    if not os.path.isfile(pdf):
        return []
    pages = _per_page_text(pdf)
    cards = _declared_cards()
    located = [(cid, _card_page(pages, title, q)) for cid, title, q in cards]
    out: "list[tuple[str, int, int]]" = []
    for idx, (cid, start) in enumerate(located):
        if start is None:
            continue
        # bound by the NEXT located card's title page
        nxt = next((p for _, p in located[idx + 1:] if p is not None), None)
        if nxt is None:
            continue  # last located card — compile-time assert owns portrait overflow
        end = nxt - 1
        if end > start:
            out.append((cid, start, end))
    return out


def orphan_rows() -> "list[str]":
    """Reverse join: a declared card whose title never appears in the rendered PDF (a projection drift).
    Empty when the PDF is absent."""
    if not os.path.isfile(_DEFAULT_PDF):
        return []
    pages = _per_page_text(_DEFAULT_PDF)
    return [f"card {cid!r} page not found in the rendered PDF"
            for cid, title, q in _declared_cards() if _card_page(pages, title, q) is None]


def summary_line(fs: "list[tuple[str, int, int]]") -> str:
    if not fs:
        return "every operator card fits one page"
    return (f"{len(fs)} operator card(s) span >1 page: "
            + ", ".join(f"{c}(p{s}->p{e})" for c, s, e in fs))


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any card spanning >1 page")
    args = ap.parse_args(argv)
    print("== operator-card page-span — post-render one-page-fit sensor "
          f"[{'BLOCKING' if BLOCKING else 'AUDIT-ONLY'}] ==")
    if not os.path.isfile(_DEFAULT_PDF):
        print("  no compiled PDF (book/mage-book.pdf) — render with `catalog.py deploy local --pdf`; nothing to sense")
        return 0
    fs = findings()
    orphans = orphan_rows()
    print(f"  {summary_line(fs)}")
    for cid, s, e in fs:
        print(f"    {cid}: title on p{s}, content continues to p{e}")
    for o in orphans:
        print(f"    {o}")
    return 1 if (fs and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
