#!/usr/bin/env python3
"""Driver for the governance-catalogue + skill test suite.

Registers the per-kind checks (see the `tests/` package: markdown / html / skill / external) and runs
them tiered:

  Tier 1 — pure stdlib, always runs, hard-fails: markdown schema + anchors, html well-formedness + link
           resolution, skill structure + bundle freshness + bundle link integrity.
  Tier 2 — external tools, run ONLY if Tier 1 is clean (fail-fast — don't pay for the ~88s browser pass
           on already-broken output): axe-core a11y, `claude plugin validate`. SKIP if the tool is absent
           (FAIL under --strict).

Adding a check = a function in the right `tests/<kind>.py` module + one `Check(...)` line in CHECKS below.
Run: `python3 catalog_tests.py [--strict]` (or `python3 catalog.py test`, which builds first).
Exit 0 = all pass; 1 = any FAIL (a Tier-2 SKIP becomes FAIL only under --strict).

**Incremental gating (`needs_run`).** A check may declare `needs_run(changed) -> bool` — a predicate over
the set of paths changed since `origin/main`. When it returns False the check SKIPs ("inputs unchanged"),
because its verdict is a pure function of those inputs. Only the expensive Tier-2 checks bother (axe's ~88s
browser pass, `claude plugin validate`); Tier-1 is sub-second, so it leaves `needs_run=None` (always run).
No baseline (missing `origin/main`) → everything runs — fail-safe.
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable, NamedTuple

from tests.common import FAIL, PASS, SKIP, changed_vs_origin
from tests.external import check_axe, check_claude_validate
from tests.html import check_html_links, check_html_valid
from tests.markdown import check_markdown_anchors, check_markdown_schema
from tests.skill import check_bundle_links, check_skill_drift, check_skill_structure


class Check(NamedTuple):
    label: str
    tier: int  # 1 = stdlib always; 2 = external, fail-fast-gated
    run: Callable[[bool], tuple]  # (strict) -> (status, issues)
    needs_run: Callable[[frozenset[str]], bool] | None = None  # None => always run


def _html_changed(changed: frozenset[str]) -> bool:
    """axe scans the served pages; the plugin bundle's HTML is gitignored, so a bare `.html` test only
    matches served output."""
    return any(f.endswith(".html") for f in changed)


def _plugin_changed(changed: frozenset[str]) -> bool:
    """`claude plugin validate` reads the plugin dir + its manifests."""
    return any(f.startswith("plugin/") or f.startswith(".claude-plugin/") for f in changed)


CHECKS = [
    Check("markdown: schema + md-link existence", 1, lambda strict: check_markdown_schema()),
    Check("markdown: #anchor resolution", 1, lambda strict: check_markdown_anchors()),
    Check("html: well-formed (balanced containers)", 1, lambda strict: check_html_valid()),
    Check("html: link + anchor resolution", 1, lambda strict: check_html_links()),
    Check("skill: structure + manifests", 1, lambda strict: check_skill_structure()),
    Check("skill: bundle freshness (no drift)", 1, lambda strict: check_skill_drift()),
    Check("skill: bundle link integrity", 1, lambda strict: check_bundle_links()),
    Check("html: axe-core accessibility", 2, check_axe, needs_run=_html_changed),
    Check("skill: claude plugin validate", 2, check_claude_validate, needs_run=_plugin_changed),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance-catalogue + skill test suite.")
    ap.add_argument("--strict", action="store_true", help="treat a Tier-2 SKIP (missing tool) as failure")
    args = ap.parse_args()

    changed = changed_vs_origin()  # None => no baseline => run everything (fail-safe)
    base = "no origin/main baseline — running all" if changed is None else f"{len(changed)} path(s) changed vs origin/main"
    print(f"== Test plan: {len(CHECKS)} checks (Tier 1 stdlib first; Tier 2 external — axe/claude — run "
          f"only if Tier 1 is clean; {'strict' if args.strict else 'skip-if-absent'}); {base} ==")
    failed = skipped = 0

    def _emit(c: Check):
        nonlocal failed, skipped
        if changed is not None and c.needs_run and not c.needs_run(changed):
            status, issues = SKIP, ["inputs unchanged since origin/main"]
        else:
            status, issues = c.run(args.strict)
        mark = {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[status]
        print(f"  [{mark}] (T{c.tier}) {c.label}")
        for it in issues:
            for line in str(it).splitlines():
                print(f"          {line}")
        failed += status == FAIL
        skipped += status == SKIP

    for c in CHECKS:  # Tier 1: cheap, stdlib
        if c.tier == 1:
            _emit(c)
    tier2 = [c for c in CHECKS if c.tier == 2]
    if failed:  # fail-fast: skip the expensive external passes if a cheap check already failed
        for c in tier2:
            print(f"  [skip] (T{c.tier}) {c.label} — skipped: fix the failed Tier-1 check(s) first")
        skipped += len(tier2)
    else:
        for c in tier2:
            _emit(c)
    print(f"== {len(CHECKS)} checks: {len(CHECKS) - failed - skipped} passed, {failed} failed, {skipped} skipped ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
