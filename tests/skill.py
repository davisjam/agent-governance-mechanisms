"""Skill checks over the packaged plugin: manifest + structure, bundle freshness (no drift vs sources),
and bundle link integrity (nothing dangles once the plugin is copied to a cache and installed)."""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from tests.common import FAIL, PASS, ROOT, SKILL, SKILLDIR, SKILLREF, run


def check_skill_structure():
    """SKILL.md frontmatter, manifests, and the bundled reference are present and well-formed."""
    issues = []
    skmd = os.path.join(SKILLDIR, "SKILL.md")
    if not os.path.isfile(skmd):
        return FAIL, ["SKILL.md missing"]
    fm = re.match(r"^---\n(.*?)\n---\n", open(skmd, encoding="utf-8").read(), re.S)
    if not fm:
        issues.append("SKILL.md: no YAML frontmatter")
    elif not re.search(r"^description:\s*\S", fm.group(1), re.M):
        issues.append("SKILL.md: frontmatter has no non-empty `description`")
    try:
        pj = json.load(open(os.path.join(SKILL, ".claude-plugin", "plugin.json"), encoding="utf-8"))
        issues += [f"plugin.json: missing `{k}`" for k in ("name", "description") if not pj.get(k)]
    except Exception as ex:  # noqa: BLE001 — surfaced as a test issue, not swallowed
        issues.append(f"plugin.json: {ex}")
    try:
        mj = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
        issues += [f"marketplace.json: missing `{k}`" for k in ("name", "owner", "plugins") if not mj.get(k)]
    except Exception as ex:  # noqa: BLE001 — surfaced as a test issue
        issues.append(f"marketplace.json: {ex}")
    principles = os.path.join(SKILLDIR, "principles.md")
    if not (os.path.isfile(principles) and os.path.getsize(principles) > 500):
        issues.append("principles.md: missing or too small")
    for name in ("INDEX.md", "ABSTRACTIONS.md", "README.md"):
        if not os.path.isfile(os.path.join(SKILLREF, name)):
            issues.append(f"reference/{name}: missing")
    n = len(glob.glob(os.path.join(SKILLREF, "agent", "*", "*.md"))) + \
        len(glob.glob(os.path.join(SKILLREF, "models-bridge", "*", "*.md")))
    if n < 30:
        issues.append(f"reference: only {n} entries bundled (expected 30+)")
    return (FAIL if issues else PASS), issues


def check_skill_drift():
    """Regenerate the bundle and assert it matches what's committed (no stale bundle)."""
    r = run([sys.executable, "bundle_skill.py"])
    if r.returncode != 0:
        return FAIL, [f"bundle_skill.py failed (rc={r.returncode}): {r.stderr.strip()[:200]}"]
    d = run(["git", "status", "--porcelain", "--", "plugin/agent-governance/skills"])
    changed = [ln for ln in d.stdout.splitlines() if ln.strip()]
    if changed:
        return FAIL, ["bundle is STALE vs its sources — run `bundle_skill.py` and commit:"] + changed[:12]
    return PASS, []


def check_bundle_links():
    """Every relative link inside the installed skill must resolve. A plugin is copied to a cache and
    can't reach outside its own dir, so a dangling `../../downloads/...` handoff (an entry citing a
    template the bundler didn't vendor) would break once installed. External / anchor-only links are
    out of scope (same as the markdown checks)."""
    issues = []
    for f in glob.glob(os.path.join(SKILLDIR, "**", "*.md"), recursive=True):
        base = os.path.dirname(f)
        for m in re.findall(r"\]\(([^)]+)\)", open(f, encoding="utf-8").read()):
            if m.startswith(("http://", "https://", "mailto:", "#", "//")):
                continue
            tgt = m.split("#", 1)[0]
            if tgt and not os.path.exists(os.path.normpath(os.path.join(base, tgt))):
                issues.append(f"{os.path.relpath(f, SKILLDIR)} -> {m} (missing in bundle)")
    return (FAIL if issues else PASS), issues
