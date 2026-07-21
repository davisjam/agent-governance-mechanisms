"""Skill checks over the packaged plugin: manifest + structure, bundle freshness (no drift vs sources),
and bundle link integrity (nothing dangles once the plugin is copied to a cache and installed)."""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from tests.common import BUNDLED_SKILLS, FAIL, PASS, ROOT, SKILL, SKILLS, run


def check_skill_structure():
    """For every shipped skill: SKILL.md frontmatter. Bundled skills (generated from catalogue sources)
    also ship a bundler-emitted `principles.md`; a mirror-carrying skill ships its reference tree. An
    authored skill ships neither — its resources live in its own dir. Plus the plugin + marketplace
    manifests (once, at plugin level)."""
    issues = []
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
    for name, sdir, has_ref in SKILLS:
        skmd = os.path.join(sdir, "SKILL.md")
        if not os.path.isfile(skmd):
            issues.append(f"{name}: SKILL.md missing")
            continue
        fm = re.match(r"^---\n(.*?)\n---\n", open(skmd, encoding="utf-8").read(), re.S)
        if not fm:
            issues.append(f"{name}: SKILL.md has no YAML frontmatter")
        elif not re.search(r"^description:\s*\S", fm.group(1), re.M):
            issues.append(f"{name}: SKILL.md frontmatter has no non-empty `description`")
        if name in BUNDLED_SKILLS:  # only generated skills carry a bundler-emitted principles.md
            principles = os.path.join(sdir, "principles.md")
            if not (os.path.isfile(principles) and os.path.getsize(principles) > 500):
                issues.append(f"{name}: principles.md missing or too small")
        if has_ref:
            ref = os.path.join(sdir, "reference")
            for fn in ("INDEX.md", "ABSTRACTIONS.md", "README.md"):
                if not os.path.isfile(os.path.join(ref, fn)):
                    issues.append(f"{name}: reference/{fn} missing")
            n = len(glob.glob(os.path.join(ref, "agent", "*", "*.md"))) + \
                len(glob.glob(os.path.join(ref, "models-bridge", "*", "*.md")))
            if n < 30:
                issues.append(f"{name}: reference has only {n} entries (expected 30+)")
    return (FAIL if issues else PASS), issues


def check_skill_drift():
    """Regenerate the bundle and assert it matches what's committed (no stale bundle). Scoped to the
    GENERATED skill dirs — an authored skill (`bundle_skill.py` never emits it) must not read as drift."""
    r = run([sys.executable, "bundle_skill.py"])
    if r.returncode != 0:
        return FAIL, [f"bundle_skill.py failed (rc={r.returncode}): {r.stderr.strip()[:200]}"]
    pathspecs = [f"plugin/agent-governance/skills/{n}" for n in sorted(BUNDLED_SKILLS)]
    d = run(["git", "status", "--porcelain", "--"] + pathspecs)
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
    for name, sdir, _ in SKILLS:
        for f in glob.glob(os.path.join(sdir, "**", "*.md"), recursive=True):
            base = os.path.dirname(f)
            for m in re.findall(r"\]\(([^)]+)\)", open(f, encoding="utf-8").read()):
                if m.startswith(("http://", "https://", "mailto:", "#", "//")):
                    continue
                tgt = m.split("#", 1)[0]
                if tgt and not os.path.exists(os.path.normpath(os.path.join(base, tgt))):
                    issues.append(f"{name}/{os.path.relpath(f, sdir)} -> {m} (missing in bundle)")
    return (FAIL if issues else PASS), issues
