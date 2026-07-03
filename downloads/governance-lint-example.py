#!/usr/bin/env python3
"""A CONCRETE, RUNNABLE example of a governance lint — the artifact that turns a
recurring failure into a control.

This is the real "regex-against-structured-formats" lint from a production system,
made self-contained so you can run it as-is:

    python3 governance-lint-example.py [PATH ...]     # defaults to the current dir

It flags `re.compile(...)` patterns that are being used to *parse structured data*
(HTML comments, YAML, JSON, XML) — where the right tool is a parser, not a regex.
Copy the SHAPE for your own invariants; the specific check is illustrative.

────────────────────────────────────────────────────────────────────────────────
WHY THIS EXISTS (abridged field note — "Regexes considered harmful, again")

A project's own regex-based lint once hung the deploy gate for 5+ minutes at 100%
CPU. The pattern had nested unbounded quantifiers inside an optional group; on
generic-typed signatures like `IReadOnlyList<Dictionary<string, List<int>>>` the
engine explored every way to partition the input — exponential (catastrophic)
backtracking. The lint was BLOCKING, so the deploy gate was effectively broken,
and the hang was masked for months behind an unrelated crash upstream.

The response was NOT "lint for catastrophic backtracking." It was: **eliminate the
surface** — stop using regex where you needed a parser. Every replacement (a real
code-parser, a tree walker with a cycle guard, a content-stream scanner, a JSON
loader, a typed enum) also fixed edge cases the regex had silently dropped: the
defect-delta of porting an old regex to a parser is rarely zero, even when the
regex "looked correct" in the working case.

The parser-first rule isn't arbitrary: the author wrote his PhD
(https://vtechworks.lib.vt.edu/server/api/core/bitstreams/53fece6d-7f32-4b58-a29a-2f9f1095b52e/content)
about regular expressions. The feature set most engineers reach for — capture
groups, lookarounds, nested unbounded quantifiers — is the wrong tool for nearly
every job it gets used for, because the failure mode is silent and catastrophic.
Treat a non-trivial regex as a smell, not a tool.

────────────────────────────────────────────────────────────────────────────────
HOW TO USE THIS AS A SCAFFOLD (the portable governance-lint shape)

  1. A self-describing DECLARATION block (COMPONENT_TAGS = where it scans;
     SEVERITY = whether it blocks) so the lint can be centrally scheduled and a
     reader knows its scope + teeth at a glance.
  2. A `find_violations()` that returns one human-readable finding per problem —
     walk files / the AST / your meta-model; prefer reading a registry to
     hardcoding paths, or the lint drifts when a directory moves.
  3. A `main()` that prints findings and returns an EXIT CODE (non-zero fails the
     gate). This one is AUDIT-ONLY (always exits 0) — ship a new lint advisory
     first, watch it stay green under real traffic, then flip SEVERITY to
     "BLOCKING" so it never wedges the team on day one.
  4. An ESCAPE HATCH: `# noqa: <lint-name> — <reason>` makes a legitimate
     exception explicit and greppable instead of a silent suppression.

The workflow it belongs to: an audit finds the same defect in N>1 places → fix the
N sites AND drop in a lint like this so the class can't come back. Today's audit
finding is tomorrow's lint.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

# ── Declaration block (self-describing; a reader/scheduler sees scope + teeth) ──
COMPONENT_TAGS: list[str] = ["ALL_PY"]          # WHERE it scans (read from your
                                                # component model, don't hardcode)
SEVERITY: str = "AUDIT-ONLY"                     # "AUDIT-ONLY" advises; "BLOCKING"
                                                # fails the gate. Migrate up once green.
_NOQA_TOKEN = "regex-against-structured-formats"  # the escape-hatch name

# Substrings inside a compiled pattern that suggest it is parsing structured data
# rather than doing simple string matching. Conservative — tuned to minimize
# false positives (simple header/bullet/slug patterns are NOT flagged).
_SUSPICIOUS_SUBSTRINGS: tuple[str, ...] = (
    "<!--",       # HTML comment delimiter inside a regex
    "-->",        # HTML comment close inside a regex
    r":\s*\[",    # YAML/JSON list value prefix (key: [...])
    r":\s*\{",    # YAML/JSON dict value prefix (key: {...})
    r"\\\{",      # escaped curly brace (object literal in the pattern)
    r"\\\}",      # escaped curly brace close
)


def _pattern_is_suspicious(pattern_str: str) -> str | None:
    """Return the first structured-data indicator found in the pattern, or None."""
    for indicator in _SUSPICIOUS_SUBSTRINGS:
        if indicator in pattern_str:
            return indicator
    return None


def scan_file(path: Path) -> list[str]:
    """Return one finding string per suspicious `re.compile(...)` in *path*."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return []

    lines = source.splitlines()
    findings: list[str] = []

    for node in ast.walk(tree):
        # Match re.compile(...) calls.
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "compile"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "re"
                and node.args):
            continue

        # The first positional arg must be a plain string literal (skip f-strings).
        first = node.args[0]
        if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
            continue
        pattern_str = first.value

        indicator = _pattern_is_suspicious(pattern_str)
        if indicator is None:
            continue

        # Honour an inline escape on any line of the call expression.
        start = max(0, node.lineno - 1)
        end = min(len(lines), getattr(node, "end_lineno", node.lineno))
        if any(_NOQA_TOKEN in ln for ln in lines[start:end]):
            continue

        excerpt = pattern_str[:80] + ("…" if len(pattern_str) > 80 else "")
        findings.append(
            f"{path}:{node.lineno}: re.compile() looks like it is parsing "
            f"structured data (indicator {indicator!r}) — use a parser "
            f"(yaml.safe_load / json.loads / html.parser). Pattern: {excerpt!r}"
        )
    return findings


def find_violations(roots: list[Path]) -> list[str]:
    """Walk *roots* for Python files and collect all findings."""
    findings: list[str] = []
    for root in roots:
        py_files = [root] if root.is_file() else sorted(root.rglob("*.py"))
        for py in py_files:
            findings.extend(scan_file(py))
    return findings


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    roots = [Path(a) for a in argv] or [Path.cwd()]

    findings = find_violations(roots)
    for f in findings:
        print(f"  [{_NOQA_TOKEN}] {f}")
    print(f"{_NOQA_TOKEN}: {len(findings)} finding(s)", file=sys.stderr)

    # AUDIT-ONLY: always exit 0. For a BLOCKING lint: `return 1 if findings else 0`.
    return 0


if __name__ == "__main__":
    sys.exit(main())
