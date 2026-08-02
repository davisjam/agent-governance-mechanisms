"""LINT `claim-watch-phrases` (C7) — grep each claim's `watch_phrases` in the chapters it is asserted at.

THE SURFACING AID (DESIGN book/_design/book-claims-model-260801.md §4.2).  A claim's `contradicted_by`
predicate is SEMANTIC — no deterministic check separates "keep the model derived from the code" (a
contradiction of `direction-agnostic`) from "a derived model kills drift" (a correct use of the same words).
So the contradiction check is a review-gate JUDGMENT-AUDIT, not a blocking lint. This lint is the aide that
makes that audit cheap: for every claim carrying `watch_phrases`, it greps those literal phrases in the
claim's `asserted_at` chapters and surfaces each hit as a CANDIDATE contradiction for a human / agent to
judge. It narrows the audit's search from the whole book to a handful of sentences.

AUDIT-ONLY FOREVER.  A watch-phrase hit is high-false-positive BY DESIGN — the same phrase can carry a
legitimate use (the `direction-agnostic` phrase "derived from the code" is a real, correct sentence in the
mirror-vs-spec discussion). The lint NEVER renders a verdict, so it stays audit-only permanently; promoting
it to blocking would redden correct prose. It PRINTS candidates and exits 0 (`--strict` exits 1 only for a
CI probe of the surfacing itself, never wired into a gate).

Run `python3 book-models/lint_claim_watch_phrases.py` to see the candidates (audit-only, exit 0).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_symbols as bs  # noqa: E402 — read-only over book_ir (chapter prose lives in the IR blocks)
import claims_model as clm  # noqa: E402 — the claims view: each claim's watch_phrases + asserted_at
import outline_model as om  # noqa: E402 — the section→chapter map for resolving asserted_at sites


def _chapter_blocks() -> "dict[str, list[tuple[int, str]]]":
    """slug → [(block_index, raw_text)] for every chapter — the prose the watch-phrases are grepped in. Read
    from `book_ir` (the SOURCE markdown), never the generated HTML, so a fixed source is seen as fixed."""
    doc = bs.book_ir.parse_book()
    return {c.slug: [(b.index, b.raw) for b in c.blocks] for c in doc.chapters}


def _section_to_chapter() -> "dict[str, str]":
    outline = om.derive_outline()
    return {s.section_id: c.slug for c in outline.chapters for s in c.sections}


def findings() -> "list[str]":
    """Every (claim, watch-phrase, site) where the literal phrase (case-insensitive) appears in a chapter the
    claim is asserted at. Each is a CANDIDATE contradiction surfaced for the judgment-audit — never a verdict.
    A claim's `asserted_at` sites are resolved to their chapters (a section id → its chapter; a chapter slug →
    itself); part-N / book / point: sites are too broad to grep and are skipped."""
    model = clm.derive_model()
    sec_to_chap = _section_to_chapter()
    chap_blocks = _chapter_blocks()

    out: "list[str]" = []
    for cl in model.claims:
        if not cl.watch_phrases:
            continue
        chapters: "set[str]" = set()
        for site in cl.asserted_at:
            if site in sec_to_chap:
                chapters.add(sec_to_chap[site])
            elif site in chap_blocks:
                chapters.add(site)
            # part-N / book / point: — not grep-scoped; skipped.
        for chap in sorted(chapters):
            for phrase in cl.watch_phrases:
                needle = phrase.lower()
                for idx, raw in chap_blocks.get(chap, []):
                    if needle in raw.lower():
                        out.append(f"CANDIDATE claim {cl.id!r} — watch-phrase {phrase!r} appears in "
                                   f"{chap}::block-{idx}. Judge whether the prose negates the claim: "
                                   f"{cl.contradicted_by}")
    return out


def main(argv: "list[str]") -> int:
    strict = "--strict" in argv[1:]
    fs = findings()
    mode = "STRICT (exit 1 on any candidate)" if strict else "AUDIT-ONLY FOREVER (prints, exits 0)"
    print(f"== claim-watch-phrases (C7) — grep each claim's watch_phrases in its asserted_at chapters "
          f"[{mode}] ==")
    n_watched = sum(1 for c in clm.derive_model().claims if c.watch_phrases)
    if not fs:
        print(f"  clean — {n_watched} claim(s) carry watch-phrases; none surfaced a candidate in their "
              f"asserted_at chapters")
        return 0
    print(f"  {len(fs)} candidate(s) for the judgment-audit ({n_watched} claim(s) carry watch-phrases):")
    for f in fs:
        print(f"    {f}")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
