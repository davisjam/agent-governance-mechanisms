# Operational-density gap-fills — ada-tool grounding pointers (260804)

Author fidelity directive: "study the real materials from ada-tool repo, don't just make stuff up." The
pilot (`operational-density-pilot-260804.md`) drafted the 2 gap-fills from the BOOK's own prose only. The
STEP-3 fill wave MUST re-ground them in the REAL ada-tool practice below, and must READ the book's actual
2.4 / 4.1 chapters + these sources before drafting. If the real practice differs from the pilot's draft,
the real practice wins (don't ship an invented artifact).

## 2.4-lifecycles-and-runbooks — the real artifacts (NOT a generic FMEA)
The pilot proposed an "FMEA failure-grid + runbook-authoring checklist." The REAL ada-tool operational
practice for lifecycles/runbooks is the **operate-repo skill**, and the artifact must reflect IT:
- **Typed-step runbooks** (`.claude/skills/operate-ada-tool-repo/runbooks.yaml`): every runbook step is
  typed **RUNNABLE** (a deterministic tool line) / **JUDGMENT_AUTOMATABLE** (carries a dispatchable Opus
  brief) / **JUDGMENT_IRREDUCIBLE** (surface to the human). A `command` on a non-RUNNABLE step or a
  `carried_brief` on a non-JUDGMENT_AUTOMATABLE step is a lint finding (typed-shape enforcement).
- **Symptom→doc catalog** (`pointers.yaml`): symptom CLASS → canonical doc, matched on class not the `e.g.`.
- **The five lifecycles** (L1 manage-agents … L5 manage-dev-machine + L-cron + L-orch) each with a healthy
  baseline.
GAP-FILL GUIDANCE: the 2.4 operational artifact should be a **runbook-authoring checklist / the typed-step
taxonomy table** grounded in the RUNNABLE/JUDGMENT_AUTOMATABLE/JUDGMENT_IRREDUCIBLE structure + the
symptom→class routing — the book's own DocAble runbook practice. Only tabulate an "FMEA" if the book's 2.4
prose genuinely describes a failure-mode analysis that maps to a REAL ada-tool artifact; otherwise reflect
the typed-runbook/symptom-catalog reality. Fill wave READS: the book's `book/part2/2.4-*.md` +
`.claude/skills/operate-ada-tool-repo/{runbooks.yaml,pointers.yaml,SKILL.md}`.

## 4.1-brownfield — the real governance-sizing heuristic (A.22 right-size-the-fix)
The pilot proposed a "cost×frequency governance-sizing decision-matrix + a stop-adding-governance
litmus-test." The REAL heuristic is CLAUDE.md **A.22 "Right-size the fix — architecture-first,
defense-in-depth"** (CLAUDE.md:~329):
- "the **smallest sound change that closes the *class***, proportionate to the failure";
- "**float larger schemes, don't reflexively build them** (bias local, let cost justify)";
- "**architecture before controls** — make the error impossible before catching it (→ A.8)";
- "costly failures earn **both**" (architecture AND a control);
- pairs with the **computed control blast-radius** (compute what a control's failure takes down).
GAP-FILL GUIDANCE: the 4.1 decision-matrix + litmus should encode A.22's real axes — proportionality
(failure cost/frequency → smallest-sound-change), architecture-before-controls, "float don't reflexively
build," costly-failures-earn-both — NOT an invented sizing formula. Fill wave READS: the book's
`book/part4/4.1-brownfield.md` + CLAUDE.md A.22 + `docs/dev/AI-FIRST-ENGINEERING.md` §right-size.

## Standing constraint
Both artifacts stay within the book's fidelity principle: reflect what ada-tool ACTUALLY does. If the real
practice can't support the pilot's exact artifact shape, adapt the artifact to the real practice + note the
adaptation. The `chapter_shape.delivers{}` model field + the `catalog.py delivers` view + the
framework/table + worked-example type additions proceed as the pilot recommended (that part is uncontested).
