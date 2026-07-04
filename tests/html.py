"""HTML checks over the built site: link and in-page anchor resolution (stdlib `html.parser`, no browser).
Full HTML validity is NOT hand-rolled here — it's delegated to the canonical `html-validate` (Tier-2,
`tests/external.py`), configured by `.htmlvalidate.json`."""
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
