"""HTML checks over the built site: cheap well-formedness (balanced/nested containers) + link and
in-page anchor resolution. Both parse with the stdlib `html.parser` (no browser)."""
from __future__ import annotations

import os
from html.parser import HTMLParser

from tests.common import FAIL, PASS, html_files, rel


class _Refs(HTMLParser):
    """Collects local href/src references and the id/anchor targets a page defines."""

    def __init__(self):
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for a in ("href", "src"):
            if d.get(a):
                self.refs.append(d[a])
        if d.get("id"):
            self.ids.add(d["id"])
        if tag == "a" and d.get("name"):  # legacy <a name>; NOT meta/input name=
            self.ids.add(d["name"])


def check_html_links():
    """Every local href/src resolves to a file; #anchors resolve where the target page uses ids."""
    files = html_files()
    if not files:
        return FAIL, ["no built HTML found — run `catalog.py build` first"]
    parsed: dict[str, _Refs] = {}
    for f in files:
        p = _Refs()
        p.feed(open(f, encoding="utf-8").read())
        parsed[os.path.abspath(f)] = p
    issues = []
    for f in files:
        base, ap = os.path.dirname(f), os.path.abspath(f)
        for ref in parsed[ap].refs:
            if ref.startswith(("http://", "https://", "mailto:", "data:", "//")):
                continue
            tgt_rel, _, anchor = ref.partition("#")
            if not tgt_rel:  # in-page anchor
                if anchor and anchor not in parsed[ap].ids:
                    issues.append(f"{rel(f)} -> #{anchor} (no such id in page)")
                continue
            tgt = os.path.abspath(os.path.join(base, tgt_rel))
            if not os.path.exists(tgt):
                issues.append(f"{rel(f)} -> {ref} (missing target)")
            elif anchor and tgt in parsed and parsed[tgt].ids and anchor not in parsed[tgt].ids:
                # only assert the anchor when the target page uses ids at all (avoids false positives
                # on pages that don't emit heading ids)
                issues.append(f"{rel(f)} -> {ref} (no such anchor in target)")
    return (FAIL if issues else PASS), issues


_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
         "source", "track", "wbr"}
# strict containers that must balance + nest properly. Optional-close elements (p / li / tr / td …) are
# deliberately NOT tracked, so lenient-but-valid HTML doesn't false-positive.
_CONTAINERS = {"html", "head", "body", "main", "div", "section", "article", "aside", "header", "footer",
               "nav", "figure", "figcaption", "table", "pre", "ul", "ol", "style", "script", "svg",
               "iframe", "blockquote", "form"}


class _Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in _CONTAINERS and tag not in _VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag not in _CONTAINERS:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:  # closing across a still-open container = misnest
                self.errors.append(f"</{tag}> closes across still-open <{self.stack.pop()}>")
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"stray </{tag}> (no matching open)")


def check_html_valid():
    """Cheap, stdlib well-formedness gate that runs BEFORE the expensive axe browser pass: every built
    page's container tags (div/section/main/figure/table/pre/script/svg/...) must balance and nest.
    A browser silently auto-corrects malformed HTML, so axe alone wouldn't necessarily catch a renderer
    bug that drops a close tag; this does, in milliseconds."""
    issues = []
    for f in html_files():
        p = _Balance()
        p.feed(open(f, encoding="utf-8").read())
        p.close()
        issues += [f"{rel(f)}: {e}" for e in p.errors[:5]]
        if p.stack:
            issues.append(f"{rel(f)}: unclosed at EOF -> {p.stack[:5]}")
    return (FAIL if issues else PASS), issues
