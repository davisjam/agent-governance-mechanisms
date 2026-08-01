# Example runbook — keep the tree clean

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's tools.*

**Lifecycle:** L3 · manage-git-repo.

## Problem (universal)

The mainline's working tree isn't green — untracked run-artifacts have piled up: measurement outputs, logs,
session flags. Left there, a stray `commit -a` sweeps them into one mislabeled commit — often right after the
operator's shell drifts into the wrong repo and a reflex "commit everything" fires. You need the tree clean,
and (the sharp case) to un-bundle a sweep that already landed without rewriting shared history.

## Steps (typed)

- **[RUNNABLE] Snapshot the untracked set with sizes.** List what's untracked and how big each path is;
  large files are almost always transient outputs, and the size ranking tells you where the accretion lives.
  `<your untracked-file listing with sizes>`
- **[JUDGMENT-AUTOMATABLE] Triage each path.** A carried brief that bins every untracked path into **WIPE**
  (transient artifacts), **COMMIT** (authored content), **LEAVE** (untracked-by-design — e.g. installed-skill
  mirrors), or **DEFER** (another agent's in-flight work). Conservative default: *when uncertain, COMMIT —
  never wipe authored content.* The brief emits a manifest — each path, its disposition, and the rationale (a
  look-before-delete audit trail) — and proposes ignore-rules for the recurring transient patterns.
  Carried brief: *"Given this untracked set, bin each path (WIPE / COMMIT / LEAVE / DEFER) with a one-line
  rationale; default to COMMIT when uncertain; propose ignore-rules for the recurring transient patterns."*
- **[RUNNABLE] Execute the manifest.** Remove the WIPE set, stage the COMMIT set, land the manifest plus the
  new ignore-rules; leave the LEAVE set alone and don't touch the DEFER set.
  `<your remove of the wipe-set>` · `<your stage + commit of the commit-set + manifest + ignore-rules>`
- **[JUDGMENT-IRREDUCIBLE] If a sweep already landed, un-bundle forward-only.** Land a new commit that
  unstages the swept blobs — restoring them to untracked — so the mislabeled commit is corrected by adding
  history, not rewriting it. A history rewrite is destructive on a shared mainline and needs explicit human
  approval every time: surface the rewrite option, don't take it. (Cite the **care-with-destructive-ops**
  principle in the partner [`self-governance`](../../self-governance/SKILL.md) skill — don't restate it.)

## Second-order note

The ignore-rule addition is what keeps this from recurring — convert the recurring artifact pattern to an
ignore-rule in the *same* pass. A manual step you keep repeating (re-cleaning the same transient outputs) is
a self-governance signal: hand the class to the partner skill so the next run never accretes it.
