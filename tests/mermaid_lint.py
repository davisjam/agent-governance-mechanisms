"""Mermaid edge-label footgun lint.

Mermaid parses `[` / `]` as node-shape syntax, and `~>` is not a valid arrow; either one
placed INSIDE an edge-label pipe (`A -->|label| B`) breaks the diagram at render time with a
cryptic parser error rather than a clear "bad label" message. This check catches the footgun
at lint time with a precise file:line and the offending label.

Governance conversion (author 260804): the FILL-IN Structure-diagram wave hit this on a
mermaid diagram; rather than fix only the instance, the class is converted to a control here.
"""
from __future__ import annotations

import glob
import os
import re
import sys

from tests.common import FAIL, PASS, ROOT, rel

# Pipe-delimited segments on a line; in a mermaid flowchart these are edge labels.
_PIPE = re.compile(r"\|([^|]*)\|")
# The three render-breaking tokens the author named.
_BANNED = ("[", "]", "~>")


def check_mermaid_edge_labels():
    """Fail if any mermaid edge-label pipe contains `[`, `]`, or `~>` (mermaid render footguns)."""
    findings = []
    for md in sorted(glob.glob(os.path.join(ROOT, "book", "**", "*.md"), recursive=True)):
        # Skip design/draft docs — they are not shipped and may carry example fences.
        if "/_design/" in md:
            continue
        with open(md, encoding="utf-8") as fh:
            text = fh.read()
        in_mermaid = False
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("```mermaid"):
                in_mermaid = True
                continue
            if in_mermaid and stripped.startswith("```"):
                in_mermaid = False
                continue
            if not in_mermaid:
                continue
            for seg in _PIPE.findall(line):
                hit = [b for b in _BANNED if b in seg]
                if hit:
                    toks = ", ".join(repr(h) for h in hit)
                    findings.append(
                        f"{rel(md)}:{lineno}: mermaid edge-label |{seg.strip()}| contains {toks} "
                        f"— breaks the parser; keep [ ] and ~> out of edge-label pipes "
                        f"(use a plain word, or &rarr; for an arrow)"
                    )
    return (FAIL if findings else PASS), findings


if __name__ == "__main__":
    status, out = check_mermaid_edge_labels()
    for f in out:
        print(f)
    print(f"{status}: {len(out)} mermaid edge-label finding(s)")
    sys.exit(1 if out else 0)
