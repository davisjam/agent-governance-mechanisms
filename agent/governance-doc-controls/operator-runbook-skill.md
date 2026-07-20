# Operator runbook skill (positive map first, symptom index fallback)

**Intent** — A loadable skill that gives an operating agent the *positive* map of how the operational
substrate works — its lifecycles and healthy baselines — **first**, and a *symptom → resolving-doc*
catalog as the fallback when something breaks. Generate its content from a typed source-of-truth so a
reference-validity lint (not tests — it executes nothing) keeps every pointer honest, and type each
recovery step by how automatable it is (our instance: an `operate-ada-tool-repo` skill over the
agent-fleet substrate, rendered from two typed YAML sources — a pointer catalog and a runbook catalog).

| | |
|---|---|
| Summary | Positive substrate map + symptom→doc routing, generated from typed YAML, ref-lint-checked. |
| Target | Agent · **Governance-doc controls** |
| Form | `agent-output` |
| Enforcement | **Soft·Hard** — the skill *routes*, it cannot execute or block; its correctness is a hard reference-validity lint that resolves every pointer's file *and* heading anchor against disk (a non-executable index earns trust from a ref-check, not tests) |

## Motivation — the failure it kills

An operator — a human or an orchestrator agent — running a complex substrate must know two things: how it
*works* when healthy, and what to do when it *breaks*. Both live scattered across a house-rules doc, a
docs index, and incident memories that a fresh or post-compaction operator does not reliably hold. So the
operator **re-derives the substrate's shape from scratch** under load, and during an incident re-derives —
badly, under time pressure — a recovery a doc already spells out. And the routing itself **rots**: a doc
moves, the pointer dangles, the next operator is sent on a chase. The failure is *re-derivation of known
operations* plus *silent pointer rot*, and it recurs every session and every incident.

Underneath is a stance: **the fleet is cattle, not pets.** You operate an agent fleet with *repeatable
runbooks*, not by re-reasoning each incident from scratch or *chatting* the orchestrator toward a goal —
that is the pet stance ("sysadmin-ing a pet server"), and it is a category error at fleet scale. This
mechanism is the cattle stance made concrete for repo operations: a routed, lint-kept index of typed
operations, so an operator runs the herd instead of nursing it.

## Why it's not just "a folder of runbooks" (or the docs index)

A runbook collection answers "what do I do when X breaks" — but only the *failure* half, and only if you
already know which runbook. A docs index answers "what docs exist" — *doc-keyed*, not operator-keyed.
This skill does three things neither does. It **leads with the positive map** — the substrate's lifecycles
and healthy baselines — so the operator knows *normal* before hunting a break (most of the time the system
is healthy, and you cannot spot a fault without the baseline). It is **symptom-keyed** — you start from
what you *observe*, not the doc you'd have to already know. And it is **generated from a typed
source-of-truth**, so a **reference-validity lint** resolves every pointer's file *and* heading anchor on
every build — a moved doc or renamed section is a build error, not a dangling chase. The distinction is
*an operator-keyed, positive-first, lint-kept map* versus *a doc-keyed pile you must already know your way
around*.

## Mechanism

The skill has two halves. A **portable stance** — how to operate, how to RCA observability-first, the
standing freedom to propose governance improvements — and a **project-specific catalog generated from
typed YAML**: the positive lifecycle map, the symptom→doc rows, and the runbooks. Each runbook decomposes
into **typed step-kinds** — *runnable* (a command), *carried-brief* (a dispatchable judgment step),
*surface-to-user* (needs a human decision) — so the judgment-automatable middle is a first-class, lintable
resource rather than under-specified prose. Two controls keep it honest: the **reference-validity lint**
resolves every pointer's file and anchor; and the skill **partners with a failure-interpretation skill** —
after a failure recurs, it routes to *classify the class → register an Epic → design the control*, never a
DIY inline fix (a control is architecture and earns a design pass). Part of that design is choosing the
control's **placement by semantic level** — the *semantic gap*: a syntactic check at a commit hook, a
judgment check at a reasoning hook or the whole-worktree final commit, an intent-level check at the Epic's
definition-of-done. Putting a check *below* the semantics it must apply is the classic gap that leaves the
policy unenforceable, so the level is chosen to match the decision, not the convenience.

## Prerequisites

- **A typed source-of-truth** the skill renders from — hand-authored markdown drifts from the docs it
  points at; the YAML is single-sourced and lint-checkable.
- **A reference-validity lint that resolves file *and* anchor** — file-exists alone lets a renamed section
  dangle.
- **Typed step-kinds** on runbook steps, so "which of these is runnable vs needs judgment" is declared,
  not guessed by the operator mid-incident.
- **A partner failure-interpretation path**, so a recurring failure becomes a *designed* control rather
  than an inline patch.

## Consequences & costs

- **The skill is soft.** It routes an operator to the right doc; it cannot execute or block. Its value is
  being loaded and heeded.
- **Coverage is soft; validity is the hard half.** The lint guarantees every *listed* pointer resolves; it
  cannot guarantee every *real* symptom is listed. Completeness rots unless new incidents are appended
  (the second-time-not-the-third discipline).
- **Anchor-resolution is a maintenance tax.** Resolving heading anchors (not only files) catches more rot
  but fires on every heading rename — the price of the higher fidelity.
- **Generation adds a build step.** The YAML→markdown render must run, or the served skill drifts from its
  source.

## Known uses

- A skill leading with the substrate's lifecycles + healthy baselines, then a symptom→resolving-doc
  catalog for breaks.
- Runbooks with typed step-kinds (runnable / carried-brief / surface-to-user), making the
  judgment-automatable middle a lintable resource.
- The reference-validity lint resolving every pointer's file and heading anchor from a typed YAML
  source-of-truth.
- The handoff to a failure-interpretation skill: recurring failure → classify → Epic → designed control.

## Related mechanisms

- **Counterpart** — [operational-playbooks](operational-playbooks.md): those are the situation-keyed
  runbooks themselves (the failure half); this skill is the operator-keyed *map over* them —
  positive-lifecycle-first, symptom-indexed, lint-kept. The named axis is *the runbooks* versus *the
  indexed, generated map into them*.
- **See also** — [claude-md-rule-index](claude-md-rule-index.md): both treat a governance *document* as
  enforced infrastructure held honest by a lint; this one adds the operator-index shape and generation
  from a typed source.
- **Enabler** — the reference-validity lint is the same "every pointer ↔ a real target" discipline as the
  models' [drift-parity gates](../../models-bridge/system-models/drift-parity-gates.md), applied to a
  doc-skill instead of a typed model.
