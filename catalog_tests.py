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

**Book audit (`--book-audit`).** A separate AUDIT-ONLY report path over the embedded book (`tests/book.py`):
intra-book link integrity, a visual per chapter, section-length cap, thesis-woven, figure hygiene,
placeholder count. It prints findings and ALWAYS exits 0 — the book has deliberate draft gaps, so it must
never contribute to the suite's fail count. It runs disjoint from the pass/fail CHECKS above: `--book-audit`
runs only the report and returns; a normal run leaves the book untouched. Promote a book rule to blocking
only once the book clears it.
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable, NamedTuple

from tests.book import run_book_audit
from tests.common import FAIL, PASS, SKIP, changed_vs_origin
from tests.external import check_axe, check_claude_validate, check_html_valid
from tests.html import (
    check_book_html_tracking,
    check_concepts_book_home,
    check_concepts_drift,
    check_concepts_reverse_coverage,
    check_concepts_site_home,
    check_data_claims,
    check_html_links,
    check_no_duplicate_ids,
    check_no_empty_table_header,
    check_no_notation_leak,
    check_summary_no_flow_content,
)
from tests.markdown import check_markdown_anchors, check_markdown_schema, check_render_safety
from tests.skill import check_bundle_links, check_skill_drift, check_skill_structure
from tests.svg_fit import check_svg_drawing_hygiene, check_svg_text_fit


class Check(NamedTuple):
    label: str
    tier: int  # 1 = stdlib always; 2 = external, fail-fast-gated
    run: Callable[[bool], tuple]  # (strict) -> (status, issues)
    needs_run: Callable[[frozenset[str]], bool] | None = None  # None => always run
    audit_only: bool = False  # True => reports candidates but never contributes to the fail count (a
    #                            heuristic still being tuned; promote to a real gate once its FP rate is
    #                            low enough). Kept out of the "N real checks" total in the plan/summary.


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
    Check("render: XSS neutralization (escape seam + link scheme)", 1, lambda strict: check_render_safety()),
    Check("html: link + anchor resolution", 1, lambda strict: check_html_links()),
    Check("html: no duplicate element ids (stdlib twin of T2 no-dup-id)", 1, lambda strict: check_no_duplicate_ids()),
    Check("html: no flow content under <summary> (stdlib twin of T2 element-permitted-content)", 1, lambda strict: check_summary_no_flow_content()),
    Check("html: no empty <th> (stdlib twin of T2 empty-table-header)", 1, lambda strict: check_no_empty_table_header()),
    Check("html: no book notation leaks (whole-vocabulary; marker / {{token}} / [+emph+])", 1, lambda strict: check_no_notation_leak()),
    Check("html: book/*.html <-> build outputs (no orphans, present + non-empty)", 1, lambda strict: check_book_html_tracking()),
    # AUDIT-ONLY (rule #55: audit-first for a new lint while wiring is partial): governed data
    # cross-references — every [data:X] resolves, each manifest source+anchor still exists, each `holds`
    # number still appears in the source (loose match), uncited entries warned. Keyed off data-claims.json.
    Check("book: data-claims manifest integrity (marker/anchor/holds/uncited)", 1,
          lambda strict: check_data_claims(), audit_only=True),
    # The concept model (book/data/concepts.json) drift lints — a typed model of the book's core concepts
    # joined book<->site by slug. L1 book-home presence + enum pre-check; L2 site-home card resolves on the
    # landing; L3 the DRIFT catch (book expands it, site has no card). Phase 2 drained the seed worklist to
    # zero, so L1/L2/L3 are now GATING (rule #55: audit-only-first → drain → promote to blocking). L4
    # (reverse coverage) stays a WARN — narrative/adoption cards legitimately back no concept; the honest
    # residual warns are informational, never gating.
    Check("concepts: L1 book-home presence + kind/status enum (concepts.json)", 1,
          lambda strict: check_concepts_book_home(), audit_only=False),
    Check("concepts: L2 site-home card resolves on landing (concepts.json)", 1,
          lambda strict: check_concepts_site_home(), audit_only=False),
    Check("concepts: L3 DRIFT catch — site-eligible+both must have a real card (concepts.json)", 1,
          lambda strict: check_concepts_drift(), audit_only=False),
    Check("concepts: L4 reverse coverage — landing card has a backing concept (warn)", 1,
          lambda strict: check_concepts_reverse_coverage(), audit_only=True),
    Check("skill: structure + manifests", 1, lambda strict: check_skill_structure()),
    Check("skill: bundle freshness (no drift)", 1, lambda strict: check_skill_drift()),
    Check("skill: bundle link integrity", 1, lambda strict: check_bundle_links()),
    Check("html: validity (html-validate)", 2, check_html_valid, needs_run=_html_changed),
    Check("html: axe-core accessibility", 2, check_axe, needs_run=_html_changed),
    Check("skill: claude plugin validate", 2, check_claude_validate, needs_run=_plugin_changed),
    # BLOCKING: estimates whether a hand-authored figure's text overflows its box or the canvas. Promoted
    # from audit-only after the figure backlog was driven to 0 (audit->lint; fix-then-flip). See tests/svg_fit.py.
    Check("svg: text-fit (box/canvas overflow)", 1,
          lambda strict: check_svg_text_fit()),
    # BLOCKING: native-construct discipline — a <marker orient=auto> arrowhead not drawn in the +x
    # convention (lands off-axis), a hand-stitched arrowhead outside a marker, or a <line> stroke running
    # through a <text> glyph box. Promoted from audit-only after the backlog hit 0 (audit->lint; fix-then-flip).
    Check("svg: drawing hygiene (marker +x / stitched arrowhead / stroke-through-glyph)", 1,
          lambda strict: check_svg_drawing_hygiene()),
]

REAL_CHECKS = [c for c in CHECKS if not c.audit_only]  # the gate — the count the summary reports


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance-catalogue + skill test suite.")
    ap.add_argument("--strict", action="store_true", help="treat a Tier-2 SKIP (missing tool) as failure")
    ap.add_argument("--full", action="store_true", help="run every check regardless of needs_run — the "
                    "authoritative pass. CI MUST use this: post-push, HEAD == origin/main, so incremental "
                    "gating would skip everything. Local predeploy stays incremental and trusts CI's green.")
    ap.add_argument("--tier1", action="store_true", help="run ALL Tier-1 deterministic checks (force, not "
                    "incremental) and SKIP the slow Tier-2 external passes — the fast pre-push gate")
    ap.add_argument("--book-audit", action="store_true", help="run the AUDIT-ONLY book structural report "
                    "(visual-per-chapter, section-length, thesis-woven, figure hygiene, placeholders) and "
                    "exit 0 — never contributes to the fail count. Disjoint from the pass/fail CHECKS.")
    args = ap.parse_args()

    if args.book_audit:
        return run_book_audit()

    # --full and --tier1 both force run-everything for the checks they DO run (reusing the no-baseline
    # fail-safe). --tier1 additionally skips every Tier-2 external pass (fast deterministic pre-push gate);
    # --full runs both tiers; otherwise incremental.
    changed = None if (args.full or args.tier1) else changed_vs_origin()
    base = ("Tier-1 only (--tier1; Tier-2 external passes skipped)" if args.tier1 else
            "full scan (--full)" if args.full else
            "no origin/main baseline — running all" if changed is None else
            f"{len(changed)} path(s) changed vs origin/main")
    print(f"== Test plan: {len(REAL_CHECKS)} gate checks + {len(CHECKS) - len(REAL_CHECKS)} audit-only "
          f"(Tier 1 stdlib first; Tier 2 external — axe/claude — run only if Tier 1 is clean; "
          f"{'strict' if args.strict else 'skip-if-absent'}); {base} ==")
    failed = skipped = 0

    def _emit(c: Check):
        nonlocal failed, skipped
        if changed is not None and c.needs_run and not c.needs_run(changed):
            status, issues = SKIP, ["inputs unchanged since origin/main"]
        else:
            status, issues = c.run(args.strict)
        # An audit-only check reports candidates but never counts — render it [audit], not [ok]/[FAIL].
        mark = "audt" if c.audit_only else {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[status]
        print(f"  [{mark}] (T{c.tier}) {c.label}")
        for it in issues:
            for line in str(it).splitlines():
                print(f"          {line}")
        if not c.audit_only:
            failed += status == FAIL
            skipped += status == SKIP

    for c in CHECKS:  # Tier 1: cheap, stdlib
        if c.tier == 1:
            _emit(c)
    tier2 = [c for c in CHECKS if c.tier == 2]
    if args.tier1:  # fast pre-push gate: run every Tier-1 check, skip the slow external passes entirely
        for c in tier2:
            print(f"  [skip] (T{c.tier}) {c.label} — skipped: --tier1 gate (Tier-2 runs in CI's --full)")
        skipped += len(tier2)
    elif failed:  # fail-fast: skip the expensive external passes if a cheap check already failed
        for c in tier2:
            print(f"  [skip] (T{c.tier}) {c.label} — skipped: fix the failed Tier-1 check(s) first")
        skipped += len(tier2)
    else:
        for c in tier2:
            _emit(c)
    n = len(REAL_CHECKS)  # audit-only checks are reported but excluded from the pass/fail tally
    print(f"== {n} gate checks: {n - failed - skipped} passed, {failed} failed, {skipped} skipped "
          f"(+ {len(CHECKS) - n} audit-only, non-gating) ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
