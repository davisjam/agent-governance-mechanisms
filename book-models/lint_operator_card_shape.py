"""LINT lint_operator_card_shape — the ~60-second-read SHAPE sensor for the Appendix-D operator cards.

The fast EDITOR-time complement to the post-render page-span sensor. It reads the declared deck
(operator-cards.json — the SSOT, like the caption lint reading its tier registry) and checks the two
shape signals a card carries in the model: the operator-question length and the evidence-field count,
each against a per-family band. A card that passes the word cap can still fail the page-span sensor;
that ordering is by design — this is the cheap early read, rendered height is the real invariant.

LANDING: AUDIT-ONLY-first (the repo's blocking-lint discipline). It prints the over-band worklist; a
tighten pass drains it; a follow-up may flip BLOCKING. No PDF needed, so it runs on every validate.

    python3 book-models/lint_operator_card_shape.py           # print worklist (exit 0, audit-only)
    python3 book-models/lint_operator_card_shape.py --strict  # exit 1 on any over-band card
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
_SOURCE = os.path.join(HERE, "operator-cards.json")

#: Phase-3 flip flag (kept for symmetry with the page-span sensor; this sensor may flip independently).
BLOCKING = False

#: Per-family bands: (max operator_question words, max evidence_refs). Seeded from the deck's own densities
#: — a checklist/synthesis card legitimately cites more sources than a single-gauge steering card. Tune here.
_BANDS: "dict[str, tuple[int, int]]" = {
    "steering":    (16, 6),
    "compounding": (16, 9),
    "shipping":    (16, 8),
    "doctrine":    (16, 6),
}
_DEFAULT_BAND = (16, 9)


@dataclass(frozen=True)
class Finding:
    card_id: str
    kind: str
    value: int
    limit: int


def _cards() -> "list[dict]":
    with open(_SOURCE, encoding="utf-8") as fh:
        return json.load(fh)["cards"]


def _words(s: str) -> int:
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def findings() -> "list[Finding]":
    out: "list[Finding]" = []
    for c in _cards():
        max_q, max_refs = _BANDS.get(c["family"], _DEFAULT_BAND)
        qw = _words(c.get("operator_question", ""))
        if qw > max_q:
            out.append(Finding(c["card-id"], "operator_question_words", qw, max_q))
        nrefs = len(c.get("evidence_refs", []))
        if nrefs > max_refs:
            out.append(Finding(c["card-id"], "evidence_refs", nrefs, max_refs))
    return out


def summary_line(fs: "list[Finding]") -> str:
    if not fs:
        return "every operator card is within its family shape band"
    return f"{len(fs)} operator-card shape finding(s) over band"


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any over-band card")
    args = ap.parse_args(argv)
    fs = findings()
    print("== operator-card shape — ~60s-read shape sensor "
          f"[{'BLOCKING' if BLOCKING else 'AUDIT-ONLY'}] ==")
    print(f"  {summary_line(fs)}")
    for f in fs:
        print(f"    {f.card_id}: {f.kind} = {f.value} (band {f.limit})")
    return 1 if (fs and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
