#!/usr/bin/env python3
"""Part-B generator + ref-lint starter for a self-operations skill (adopt & adapt).

One file, two jobs (subcommands `gen` and `lint`), over the two typed SSOTs
`pointers-starter.yaml` + `runbooks-starter.yaml`:

  gen   — render the Part B markdown (lifecycle map + docs index + symptom catalog
          + typed-step runbooks) between provenance markers in your SKILL.md,
          idempotently (regen twice = no diff). `--check` exits non-zero on drift.
  lint  — prove the index is EXECUTABLE, not decorative:
            * template completeness — each row carries its required fields;
            * ref resolution — every `ref` path exists, and a `#anchor` resolves
              to a real slugified heading in the target (code refs carry none);
            * carried-brief existence — each JUDGMENT_AUTOMATABLE step's brief exists;
            * no-hardcoded-derived-counts — a count quoted in SKILL.md prose
              ("N lifecycles") must equal the count DERIVED from the SSOT. Counts
              are derived, never quoted — a hand-typed number drifts silently.

This is the SSOT→generator→ref-lint triangle the catalogue teaches: one source of
truth, a derived doc, a lint that keeps them honest.

PyYAML is the one non-stdlib dependency (`pip install pyyaml`), declared here so a
fresh checkout knows to install it — mirrors this repo's other loader starters.

Exit codes (subprocess convention): 0 = success, 1 = runtime error OR lint
findings, 2 = missing dependency (PyYAML), 3 = `gen --check` found drift.

Fill every `# TODO(adapt)` — the paths below are placeholders.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:  # runtime-only dep absent — fail loud, not at first use
    print("MISSING-DEP: PyYAML required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

# ── Adopt-and-adapt paths ─────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_HERE, ".."))       # TODO(adapt)
_POINTERS = os.path.join(_HERE, "pointers-starter.yaml")        # TODO(adapt): your SSOT
_RUNBOOKS = os.path.join(_HERE, "runbooks-starter.yaml")        # TODO(adapt): your SSOT
_SKILL_MD = os.path.join(_HERE, "SKILL.md")                     # TODO(adapt): render target

# Region delimiters in SKILL.md — everything between (exclusive) is regenerated.
_BEGIN = "<!-- BEGIN GENERATED PART B — do not edit; regen via gen-and-lint-partb-starter.py -->"
_END = "<!-- END GENERATED PART B -->"
_PROVENANCE = "<!-- AUTO-GENERATED from pointers-starter.yaml + runbooks-starter.yaml. Hand-edits are overwritten. -->"

_STEP_REQUIRED = {  # kind -> the field the lint requires
    "RUNNABLE": "command",
    "JUDGMENT_AUTOMATABLE": "carried_brief",
    "JUDGMENT_IRREDUCIBLE": "prose",
}
_STEP_LABEL = {
    "RUNNABLE": "RUNNABLE",
    "JUDGMENT_AUTOMATABLE": "JUDGMENT (dispatch a carried brief)",
    "JUDGMENT_IRREDUCIBLE": "JUDGMENT (surface to user)",
}


# ── helpers ───────────────────────────────────────────────────────────────────
def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {path} did not parse to a mapping")
    return data


def _collapse(v: object) -> str:
    return " ".join(str(v).split())


def _rows(data: dict, key: str) -> list[dict]:
    return [r for r in (data.get(key) or []) if isinstance(r, dict)]


def _slug(heading: str) -> str:
    """GitHub-style heading slug: lowercase, drop non-word/space/hyphen, spaces→hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s]+", "-", s)


def _headings(md_path: str) -> set[str]:
    slugs: set[str] = set()
    with open(md_path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^#{1,6}\s+(.*)$", line)
            if m:
                slugs.add(_slug(m.group(1)))
    return slugs


# ── gen ───────────────────────────────────────────────────────────────────────
def _render(pointers: dict, runbooks: dict) -> str:
    out: list[str] = [_PROVENANCE, ""]

    out.append("### Part B.1 — Lifecycles (how things work)")
    out.append("")
    for m in _rows(pointers, "lifecycle_models"):
        out += [f"#### {m['id']} — {m['name']}", "", _collapse(m.get("summary", "")), ""]
        out += [f"**Healthy:** {_collapse(m.get('healthy', ''))}", ""]
        refs = ", ".join(f"[`{r}`]({r})" for r in (m.get("refs") or []))
        out += [f"**Refs:** {refs}", ""]

    out += ["### Part B.2 — The map: canonical docs + tools", "", "| What | Doc/tool | Why |", "|---|---|---|"]
    for d in _rows(pointers, "canonical_docs"):
        out.append(f"| {d['name']} | [`{d['ref']}`]({d['ref']}) | {d.get('why', '')} |")
    out.append("")

    out += ["### Part B.3 — Symptom → doc catalog", "",
            "| ID | Lifecycle | Symptom (class + e.g.) | Action | Refs | See also | Status |",
            "|---|---|---|---|---|---|---|"]
    for r in _rows(pointers, "catalog"):
        refs = "<br>".join(f"[`{x}`]({x})" for x in (r.get("refs") or []))
        see = ", ".join(r.get("see_also") or []) or "—"
        action = _collapse(r.get("action", ""))
        if r.get("carried_brief"):
            action += f" **Carried brief (JUDGMENT):** `{r['carried_brief']}`."
        out.append(f"| {r['id']} | {r['lifecycle']} | {_collapse(r.get('symptom',''))} | "
                   f"{action} | {refs} | {see} | {r.get('status','')} |")
    out.append("")

    out += ["### Part B.4 — Runbooks (typed steps)", ""]
    for rb in _rows(runbooks, "runbooks"):
        out += [f"#### {rb['id']} — {rb['title']}", "", _collapse(rb.get("summary", "")), ""]
        out += [f"**Lifecycle:** {rb['lifecycle']} · **Symptom row:** {rb['catalog_row']}", ""]
        out += ["| # | Kind | Step | Runnable / brief |", "|---|---|---|---|"]
        for i, step in enumerate(rb.get("steps") or [], start=1):
            kind = str(step.get("kind", ""))
            detail = (f"`{_collapse(step['command'])}`" if step.get("command")
                      else f"dispatch `{step['carried_brief']}`" if step.get("carried_brief")
                      else "surface to user")
            out.append(f"| {i} | {_STEP_LABEL.get(kind, kind)} | {_collapse(step.get('do',''))} | {detail} |")
        out.append("")

    return "\n".join(out)


def _splice(skill_text: str, generated: str) -> str:
    if _BEGIN not in skill_text or _END not in skill_text:
        raise SystemExit(f"ERROR: SKILL.md missing region markers ({_BEGIN} … {_END})")
    pre, rest = skill_text.split(_BEGIN, 1)
    _, post = rest.split(_END, 1)
    return f"{pre}{_BEGIN}\n{generated}\n{_END}{post}"


def cmd_gen(check: bool) -> int:
    pointers, runbooks = _load(_POINTERS), _load(_RUNBOOKS)
    with open(_SKILL_MD, encoding="utf-8") as fh:
        skill_text = fh.read()
    new_text = _splice(skill_text, _render(pointers, runbooks))
    if new_text == skill_text:
        print("OK: Part B up to date.")
        return 0
    if check:
        print("DRIFT: SKILL.md Part B is out of date — run `gen`.", file=sys.stderr)
        return 3
    with open(_SKILL_MD, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print("OK: rewrote generated Part B.")
    return 0


# ── lint ──────────────────────────────────────────────────────────────────────
def _check_ref(ref: str, findings: list[str]) -> None:
    path, _, anchor = ref.partition("#")
    abspath = os.path.join(_REPO_ROOT, path)
    if not os.path.exists(abspath):
        findings.append(f"ref missing file: {ref}")
        return
    if anchor:
        if not path.endswith(".md"):
            findings.append(f"code ref must not carry an anchor: {ref}")
        elif anchor not in _headings(abspath):
            findings.append(f"ref anchor does not resolve to a heading: {ref}")


def cmd_lint() -> int:
    pointers, runbooks = _load(_POINTERS), _load(_RUNBOOKS)
    findings: list[str] = []

    for m in _rows(pointers, "lifecycle_models"):
        for req in ("summary", "healthy", "refs"):
            if not m.get(req):
                findings.append(f"lifecycle {m.get('id','?')}: missing `{req}`")
        for r in m.get("refs") or []:
            _check_ref(str(r), findings)
    for d in _rows(pointers, "canonical_docs"):
        _check_ref(str(d.get("ref", "")), findings)
    for r in _rows(pointers, "catalog"):
        for req in ("symptom", "action", "refs", "status"):
            if not r.get(req):
                findings.append(f"catalog {r.get('id','?')}: missing `{req}`")
        for x in r.get("refs") or []:
            _check_ref(str(x), findings)
        if r.get("carried_brief"):
            _check_ref(str(r["carried_brief"]), findings)

    for rb in _rows(runbooks, "runbooks"):
        for step in rb.get("steps") or []:
            kind = str(step.get("kind", ""))
            req = _STEP_REQUIRED.get(kind)
            if req is None:
                findings.append(f"runbook {rb.get('id','?')}: unknown step kind `{kind}`")
                continue
            if not step.get(req):
                findings.append(f"runbook {rb.get('id','?')}: {kind} step missing `{req}`")
            for other in set(_STEP_REQUIRED.values()) - {req}:  # typed-shape: no cross-kind field
                if step.get(other):
                    findings.append(f"runbook {rb.get('id','?')}: {kind} step carries `{other}`")
        for r in rb.get("refs") or []:
            _check_ref(str(r), findings)
        for r in rb.get("resources") or []:
            _check_ref(str(r), findings)

    # no-hardcoded-derived-counts: a count quoted in SKILL.md must match the SSOT.
    derived = {
        "lifecycle": len(_rows(pointers, "lifecycle_models")),
        "symptom": len(_rows(pointers, "catalog")),
        "runbook": len(_rows(runbooks, "runbooks")),
    }
    if os.path.isfile(_SKILL_MD):
        text = open(_SKILL_MD, encoding="utf-8").read()
        for noun, n in derived.items():
            for m in re.finditer(rf"(\d+)\s+{noun}s?\b", text):
                if int(m.group(1)) != n:
                    findings.append(f"hardcoded count '{m.group(0)}' disagrees with derived {noun} count {n} "
                                    f"— derive it, don't quote it")

    if findings:
        print(f"LINT: {len(findings)} finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("OK: Part B lint clean.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen", help="render Part B into SKILL.md")
    g.add_argument("--check", action="store_true", help="exit 3 on drift, do not rewrite")
    sub.add_parser("lint", help="template + ref + count checks")
    args = ap.parse_args(argv)
    return cmd_gen(args.check) if args.cmd == "gen" else cmd_lint()


if __name__ == "__main__":
    sys.exit(main())
