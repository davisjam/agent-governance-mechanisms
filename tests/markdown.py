"""Markdown checks: schema/INDEX/link validation (delegated to the canonical validator) + heading-anchor
resolution across the catalogue markdown."""
from __future__ import annotations

import os
import re
import sys

import catalog
from tests.common import FAIL, PASS, rel, run, slug


def check_markdown_schema():
    """Delegate to the canonical validator (schema + INDEX + `.md`-link existence + abstractions)."""
    r = run([sys.executable, "catalog.py", "validate"])
    if r.returncode == 0:
        return PASS, []
    return FAIL, [ln.strip() for ln in r.stdout.splitlines()
                  if re.search(r"\[(entry|index|link|abbr|role|family|scheme|seam|census|stat|figure|banned)", ln)]


def check_render_safety():
    """Pin the renderer's XSS neutralization — regression for the abbr-display and link-scheme vectors.
    Adversarial inputs must not survive as executable HTML or a dangerous href scheme."""
    cases = [
        ("[x](javascript:alert(1))", 'href="#"', "javascript:"),
        ("[x](data:text/html,z)", 'href="#"', "data:"),
        ("[[zz|<img src=x onerror=alert(1)>]]", "&lt;img", "<img"),
        ("<script>alert(1)</script>", "&lt;script", "<script>"),
    ]
    issues = []
    for src, want, forbid in cases:
        out = catalog._inline(src)
        if forbid in out or want not in out:
            issues.append(f"unsafe render of {src!r} -> {out!r}")
    return (FAIL if issues else PASS), issues


def check_markdown_anchors():
    """Every `](file.md#anchor)` must point at a heading that exists in the target file."""
    files = catalog.catalogue_md_files()
    slugs: dict[str, set[str]] = {}
    for f in files:
        txt = open(f, encoding="utf-8").read()
        slugs[os.path.abspath(f)] = {slug(h) for h in re.findall(r"^#{1,6}\s+(.+?)\s*$", txt, re.M)}
    issues = []
    for f in files:
        base = os.path.dirname(f)
        txt = open(f, encoding="utf-8").read()
        for tgt_rel, anchor in re.findall(r"\]\(([^)#\s]+\.md)#([^)\s]+)\)", txt):
            tgt = os.path.abspath(os.path.join(base, tgt_rel))
            if tgt in slugs and slug(anchor) not in slugs[tgt]:
                issues.append(f"{rel(f)} -> {tgt_rel}#{anchor} (no matching heading)")
    return (FAIL if issues else PASS), issues
