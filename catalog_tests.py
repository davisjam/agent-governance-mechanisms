#!/usr/bin/env python3
"""Driver for the governance-catalogue + skill test suite.

Registers the per-kind checks (see the `tests/` package: markdown / html / skill / external) and runs
them tiered:

  Tier 1 — pure stdlib, always runs, hard-fails: markdown schema + anchors, html well-formedness + link
           resolution, skill structure + bundle freshness + bundle link integrity.
  Tier 2 — external tools, run ONLY if Tier 1 is clean (fail-fast — don't pay for the ~88s browser pass
           on already-broken output): axe-core a11y, `claude plugin validate`. SKIP if the tool is absent
           (FAIL under --strict).

Adding a check = a function in the right `tests/<kind>.py` module + one line in CHECKS below.
Run: `python3 catalog_tests.py [--strict]` (or `python3 catalog.py test`, which builds first).
Exit 0 = all pass; 1 = any FAIL (a Tier-2 SKIP becomes FAIL only under --strict).
"""
from __future__ import annotations

import argparse
import sys

from tests.common import FAIL, PASS, SKIP
from tests.external import check_axe, check_claude_validate
from tests.html import check_html_links, check_html_valid
from tests.markdown import check_markdown_anchors, check_markdown_schema
from tests.skill import check_bundle_links, check_skill_drift, check_skill_structure

# (label, tier, fn(strict) -> (status, issues)). Tier 1 = stdlib always; Tier 2 = external, fail-fast-gated.
CHECKS = [
    ("markdown: schema + md-link existence", 1, lambda strict: check_markdown_schema()),
    ("markdown: #anchor resolution", 1, lambda strict: check_markdown_anchors()),
    ("html: well-formed (balanced containers)", 1, lambda strict: check_html_valid()),
    ("html: link + anchor resolution", 1, lambda strict: check_html_links()),
    ("skill: structure + manifests", 1, lambda strict: check_skill_structure()),
    ("skill: bundle freshness (no drift)", 1, lambda strict: check_skill_drift()),
    ("skill: bundle link integrity", 1, lambda strict: check_bundle_links()),
    ("html: axe-core accessibility", 2, check_axe),
    ("skill: claude plugin validate", 2, check_claude_validate),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance-catalogue + skill test suite.")
    ap.add_argument("--strict", action="store_true", help="treat a Tier-2 SKIP (missing tool) as failure")
    args = ap.parse_args()

    print(f"== Test plan: {len(CHECKS)} checks (Tier 1 stdlib first; Tier 2 external — axe/claude — run "
          f"only if Tier 1 is clean; {'strict' if args.strict else 'skip-if-absent'}) ==")
    failed = skipped = 0

    def _emit(name, tier, fn):
        nonlocal failed, skipped
        status, issues = fn(args.strict)
        mark = {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[status]
        print(f"  [{mark}] (T{tier}) {name}")
        for it in issues:
            for line in str(it).splitlines():
                print(f"          {line}")
        failed += status == FAIL
        skipped += status == SKIP

    for name, tier, fn in CHECKS:  # Tier 1: cheap, stdlib
        if tier == 1:
            _emit(name, tier, fn)
    tier2 = [c for c in CHECKS if c[1] == 2]
    if failed:  # fail-fast: skip the expensive external passes if a cheap check already failed
        for name, tier, fn in tier2:
            print(f"  [skip] (T{tier}) {name} — skipped: fix the failed Tier-1 check(s) first")
        skipped += len(tier2)
    else:
        for name, tier, fn in tier2:
            _emit(name, tier, fn)
    print(f"== {len(CHECKS)} checks: {len(CHECKS) - failed - skipped} passed, {failed} failed, {skipped} skipped ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
