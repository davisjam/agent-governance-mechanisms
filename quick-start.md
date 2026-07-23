# Quick start — walk Claude through adopting these mechanisms

Governance-centric agentic software engineering is a **methodology**: you adapt these patterns to your
stack, your agents, and your failure modes. It is not a framework you drop in unchanged. The self-* skills
aid the mindset. You install and run them, but they carry a stance to apply, not a black box to adopt.

Claude reads the catalogue and turns it on your own repo. This page hands you the whole adoption sequence as
**paste-ready prompts** — each asks Claude to examine a shipped starter and adapt it to your repo. You run
the same sequence one of two ways:

- **Auto mode** — paste one block. Claude runs the sequence end to end, pausing for your approval at each write.
- **Interactive mode** — walk it step by step. Each prompt pairs with what it does and where to read more.

You also choose how to *bring* the mechanisms in, a choice orthogonal to the two run modes:

- **Skill (Path A)** — installable, auto-triggers, runs the loop for you.
- **DIY (Path B)** — read the patterns and adapt them by hand. Take this route when you can't run a plugin.

The prompts below mark **(Path A)** or **(Path B)** where the two diverge. Do step 0 first; the rest is the
same sequence either way.

## Step 0 — bring the mechanisms in

**Path A — install the skill (batteries included).** The whole loop installs as a Claude skill that
auto-triggers — no prompt to paste. Know what you install: a **third-party plugin that reads your repo and,
on your approval, writes it**. It is source-visible, MIT-licensed, and does no network I/O; *audit* only
advises, and *interpret-failure* acts only on your greenlight. In Claude Code:

```
/plugin marketplace add davisjam/agent-governance-mechanisms
/plugin install agent-governance@agent-governance-mechanisms
```

The `agent-governance` plugin ships **three partner skills**: **self-governance** (*harden* — audit for
missing guardrails, or convert a recurring failure into a durable mechanism), **self-operations**
(*operate* — run the agent-fleet substrate day-to-day), and **self-communicate** (*communicate* — write
and diagram engineer-facing docs well: the rhetoric toolkit, the Diátaxis register, a house lexicon, and a
prose-plus-diagram audit). All three install with the one plugin; start a new session and they load. Pull a
later release with `/plugin marketplace update agent-governance-mechanisms`. No marketplace? Vendor the
folder: copy `plugin/agent-governance/skills/` into `~/.claude/skills/` (all projects) or `.claude/skills/`
(one repo), then start a fresh session.

**Path B — DIY (installs nothing).** The conservative choice, for a company or anyone who can't run a
third-party plugin. Nothing runs in your agent loop that you didn't write. Vendor a copy of the catalogue
into your repo (or hand your agent the URL), and have your coding agent read the [`README`](README.md), the
[`INDEX`](INDEX.md), and the role folders ([`agent/`](agent/README.md) · [`models-bridge/`](models-bridge/README.md) ·
[`product/`](product/README.md)) before you start the sequence.

The two paths are **not exclusive**: install the skill on a personal project, and go DIY org-wide.

<!--adoption-source
  SINGLE SOURCE OF TRUTH for the adoption sequence. Author each STEP once here; the build
  (`_sync_adoption_sequence` in catalog.py) derives BOTH the Auto-mode block and the Interactive-mode
  section below from it, so the two forms can never drift. This block is an HTML comment: invisible on
  GitHub's own markdown render, and stripped by `render_md` so it never reaches the site HTML.

  Format — steps separated by a line of exactly `===`. Per step, `@KEY: value` fields, then a `@PROMPT:`
  field whose value is every line until the next `===` or end (verbatim, emitted into both modes):
    @TITLE:   short step title (plain text)
    @PATH:    A | B | both      (interactive mode tags the step; auto mode inlines the tag as a comment)
    @EXPLAIN: one paragraph for interactive mode (markdown links OK; omitted from auto mode)
    @LINKS:   markdown links joined by ` · ` for interactive mode (optional; omitted from auto mode)
    @PROMPT:  the verbatim paste-prompt, shared by both modes

===
@TITLE: Fold the method into your CLAUDE.md
@PATH: both
@EXPLAIN: The mechanisms are the *what*; the method is the *how* — the AI-First Engineering stance plus the rule-index discipline that decides what earns a spot in a governance doc. Put it in your own house-rules file so it shapes how your agents reason on every boot, not only when a skill fires. Already have a `CLAUDE.md`? Integrate; don't start fresh.
@LINKS: [CLAUDE-starter (the method)](downloads/CLAUDE-starter.md) · [claude-md-rule-index](agent/governance-doc-controls/claude-md-rule-index.md)
@PROMPT:
Read the AI-First Engineering Method in downloads/CLAUDE-starter.md (Part A) and my existing
CLAUDE.md (or create one if I have none). Propose edits that fold the method into my doc —
adopt / adapt / skip per principle, preserving my current rules. For the rule index, apply the
"earns a spot" test from the claude-md-rule-index mechanism: regression-preventing,
non-derivable-from-local-code, non-local. Show me a diff before writing anything.
===
@TITLE: Survey the repo for missing guardrails
@PATH: both
@EXPLAIN: Before adopting any single mechanism, get the map: which mechanisms your repo needs, already has, or would benefit from. Path A runs this as the skill's **audit** mode (advises, changes nothing). Path B asks the same of a plain agent pointed at the catalogue.
@LINKS: [INDEX (the census)](INDEX.md) · [catalogue views](catalogue-views.html)
@PROMPT:
(Path A) self-governance: run audit mode against my repo. Survey it against the catalogue and produce a
prioritized adopt / adapt / skip plan — highest-leverage, lowest-cost first — and name the one mechanism
you'd build first. Advise only; change nothing.
(Path B) Read the governance-mechanisms catalogue (README, INDEX, and the agent/ models-bridge/ product/
role folders). For each mechanism, judge whether my repo needs it, already has it, or would benefit.
Produce a prioritized adopt / adapt / skip plan, start with the highest-leverage lowest-cost mechanisms,
and tell me the one you'd build first. Advise only; change nothing.
===
@TITLE: Adopt the model-based-engineering kit
@PATH: both
@EXPLAIN: The scaling unlock for agents that keep breaking things that "looked unrelated": model your system as typed data that tools read on every run — a state-machine view, a component/zone view, a service-flow view, a deployment-topology view. The starter kit ships fill-in scaffolds for each; the mechanism entry explains why an *executable* model that governs the code beats prose that drifts.
@LINKS: [system-models starter kit](downloads/system-models-starter-kit.md) · [executable source of truth](models-bridge/system-models/executable-source-of-truth.md) · [models-bridge role](models-bridge/README.md)
@PROMPT:
Read the model-based-engineering starter kit in downloads/system-models-starter-kit.md and the
executable-source-of-truth mechanism under models-bridge/. Then look at my repo — its services,
state machines, cross-service seams, and deploy topology. Tell me which model views (state-machine,
component/zone, service-flow, deployment-topology) would earn their keep for MY system and which to
skip. For the ones worth it, draft the first view from the matching scaffold, citing real files.
State your assumptions so I correct rather than supply, and confirm the model before you emit anything.
===
@TITLE: Adapt the agent-brief validator
@PATH: both
@EXPLAIN: If you run more than one agent at a time, a brief-linting gate pays off immediately: it statically checks a task brief *before* the agent spawns and refuses to launch a malformed one. Start from the brief template, then adapt the genre-aware validator to the fields your dispatch actually uses.
@LINKS: [agent-brief starter](downloads/agent-brief-starter.md) · [brief-linting](agent/context-and-dispatch/brief-linting.md) · [role-typed dispatch](agent/context-and-dispatch/role-typed-dispatch.md)
@PROMPT:
Read the agent-brief starter in downloads/agent-brief-starter.md and the brief-linting mechanism under
agent/context-and-dispatch/. Look at how I dispatch agents today — what a brief contains, where it lives,
what a bad one looks like. Adapt the brief template to my fields, then draft a brief-linting check that
refuses to launch a brief missing the required markers. Show me the template and the check before writing.
===
@TITLE: Wire the operator-loop hooks (reflection + banking)
@PATH: A
@EXPLAIN: The self-operations skill ships a runnable hook library: a turn-end reflection nudge, a memory-routing nudge, and a context-banking check, all gated behind one typed hook substrate so they fire on tempo instead of every turn. Have the skill inspect your runtime and propose which hooks are worth wiring, then adapt the shipped library to your repo.
@LINKS: [self-operations starter](downloads/self-operations-starter.md) · [lifecycle hooks](agent/lifecycle-and-observability/lifecycle-hooks.md) · [reflection-facet substrate](agent/lifecycle-and-observability/reflection-facet-substrate.md)
@PROMPT:
(Path A) self-operations: read your SKILL.md and the shipped hook library (the reflection, memory-routing,
and banking hooks behind the typed hook substrate). Inspect my repo — how agents run, where a turn ends,
where context is banked. Propose which operator-loop hooks are worth wiring for me, adapt the shipped hook
library and its settings snippet to my repo, and show me the wiring before enabling anything.
===
@TITLE: Adopt the Epic / design-doc / handoff templates
@PATH: both
@EXPLAIN: The three planning artifacts an orchestrator authors — the Epic (the effort, with its Definition-of-Done), the design doc (the plan), and the machine-generated handoff (the context carried across sessions). Adopt the templates so your plans *drive* the work instead of being written after the fact.
@LINKS: [Epic template](downloads/EPIC-TEMPLATE-starter.md) · [design-doc template](downloads/design-doc-template-starter.md) · [handoff generator](downloads/emit-handoff-starter.py) · [epic-and-design-templates](agent/governance-doc-controls/epic-and-design-templates.md)
@PROMPT:
Read the Epic template (downloads/EPIC-TEMPLATE-starter.md), the design-doc template
(downloads/design-doc-template-starter.md), and the handoff scaffold (downloads/emit-handoff-starter.py),
plus the epic-and-design-templates mechanism under agent/governance-doc-controls/. Compare against how I
plan and track multi-step work today. Adapt the three artifacts to my repo — keep the required sections
and the Definition-of-Done — and wire the handoff generator to my session-boundary. Show me the drafts first.
===
@TITLE: Adopt an operational playbook for one substrate
@PATH: B
@EXPLAIN: A playbook is a situation-keyed operating manual for a substrate: for each thing that can go wrong, the symptom, the cause, and the fix. Start with the substrate that breaks most, and let the operator-runbook discipline turn tribal knowledge into a doc your agent can follow.
@LINKS: [op-playbook starter](downloads/op-playbook-starter.md) · [operational playbooks](agent/governance-doc-controls/operational-playbooks.md) · [operator-runbook skill](agent/governance-doc-controls/operator-runbook-skill.md)
@PROMPT:
Read the operational-playbook starter (downloads/op-playbook-starter.md) and the operational-playbooks
mechanism under agent/governance-doc-controls/. Pick the substrate in my repo that breaks most often (deploy,
the queue, the host VM, cron — your call, tell me why). Draft a situation-keyed playbook for it: per failure,
the symptom, the cause, and the fix, citing real files. Show me the draft before writing it.
===
@TITLE: Bootstrap your house lexicon, then write and audit prose with the skill
@PATH: both
@EXPLAIN: The mechanisms, design docs, runbooks, and handoffs you adopt above are all *prose* — and prose an engineer or agent must read cleanly. The self-communicate skill supplies the craft: a house lexicon (so a term means the same thing everywhere), the Diátaxis register (so a doc has the right shape), and an audit that grades a passage and emits fixes. Bootstrap the lexicon first by walking your codebase and confirming the terms with the maintainer; then write and audit prose against the skill.
@PROMPT:
(Path A) self-communicate: bootstrap my house lexicon — walk my codebase (sample my house-rules doc, a
handful of design docs, and my typed enums / registries / schema constants), extract every term I use with a
specific meaning more than once, classify each as portable (link the established name) or house (note the
concept it renames), and draft the lexicon table. Confirm the terms with me before you commit them. Then,
when I write a mechanism description, a design doc, a runbook, or a handoff, apply the engineering register and
run the audit procedure over the draft and show me the fixes.
(Path B) Read the self-communicate skill resources (its SKILL.md plus the writing/lexicon.md, writing/engineering.md,
writing/rhetoric.md, writing/voice.md, writing/audit.md, and drawing/diagrams.md files under the skills/self-communicate folder).
Bootstrap my house lexicon by walking my codebase per the lexicon's bootstrap recipe, confirm the terms with
me, then use the engineering register to write my docs and the audit procedure to grade them.
-->


## Run the sequence — Auto mode

Paste this once. Claude runs the whole adoption sequence, pausing for your approval before each write. Replace
the `(Path A)` / `(Path B)` forks with the line that matches how you brought the mechanisms in (Step 0).

<!--adoption-auto-->
```
Read this whole block, then work through the steps in order. For each step, propose
before you write, and wait for my approval.

# Step 1 — Fold the method into your CLAUDE.md  [either path]
Read the AI-First Engineering Method in downloads/CLAUDE-starter.md (Part A) and my existing
CLAUDE.md (or create one if I have none). Propose edits that fold the method into my doc —
adopt / adapt / skip per principle, preserving my current rules. For the rule index, apply the
"earns a spot" test from the claude-md-rule-index mechanism: regression-preventing,
non-derivable-from-local-code, non-local. Show me a diff before writing anything.

# Step 2 — Survey the repo for missing guardrails  [either path]
(Path A) self-governance: run audit mode against my repo. Survey it against the catalogue and produce a
prioritized adopt / adapt / skip plan — highest-leverage, lowest-cost first — and name the one mechanism
you'd build first. Advise only; change nothing.
(Path B) Read the governance-mechanisms catalogue (README, INDEX, and the agent/ models-bridge/ product/
role folders). For each mechanism, judge whether my repo needs it, already has it, or would benefit.
Produce a prioritized adopt / adapt / skip plan, start with the highest-leverage lowest-cost mechanisms,
and tell me the one you'd build first. Advise only; change nothing.

# Step 3 — Adopt the model-based-engineering kit  [either path]
Read the model-based-engineering starter kit in downloads/system-models-starter-kit.md and the
executable-source-of-truth mechanism under models-bridge/. Then look at my repo — its services,
state machines, cross-service seams, and deploy topology. Tell me which model views (state-machine,
component/zone, service-flow, deployment-topology) would earn their keep for MY system and which to
skip. For the ones worth it, draft the first view from the matching scaffold, citing real files.
State your assumptions so I correct rather than supply, and confirm the model before you emit anything.

# Step 4 — Adapt the agent-brief validator  [either path]
Read the agent-brief starter in downloads/agent-brief-starter.md and the brief-linting mechanism under
agent/context-and-dispatch/. Look at how I dispatch agents today — what a brief contains, where it lives,
what a bad one looks like. Adapt the brief template to my fields, then draft a brief-linting check that
refuses to launch a brief missing the required markers. Show me the template and the check before writing.

# Step 5 — Wire the operator-loop hooks (reflection + banking)  [Path A]
(Path A) self-operations: read your SKILL.md and the shipped hook library (the reflection, memory-routing,
and banking hooks behind the typed hook substrate). Inspect my repo — how agents run, where a turn ends,
where context is banked. Propose which operator-loop hooks are worth wiring for me, adapt the shipped hook
library and its settings snippet to my repo, and show me the wiring before enabling anything.

# Step 6 — Adopt the Epic / design-doc / handoff templates  [either path]
Read the Epic template (downloads/EPIC-TEMPLATE-starter.md), the design-doc template
(downloads/design-doc-template-starter.md), and the handoff scaffold (downloads/emit-handoff-starter.py),
plus the epic-and-design-templates mechanism under agent/governance-doc-controls/. Compare against how I
plan and track multi-step work today. Adapt the three artifacts to my repo — keep the required sections
and the Definition-of-Done — and wire the handoff generator to my session-boundary. Show me the drafts first.

# Step 7 — Adopt an operational playbook for one substrate  [Path B]
Read the operational-playbook starter (downloads/op-playbook-starter.md) and the operational-playbooks
mechanism under agent/governance-doc-controls/. Pick the substrate in my repo that breaks most often (deploy,
the queue, the host VM, cron — your call, tell me why). Draft a situation-keyed playbook for it: per failure,
the symptom, the cause, and the fix, citing real files. Show me the draft before writing it.

# Step 8 — Bootstrap your house lexicon, then write and audit prose with the skill  [either path]
(Path A) self-communicate: bootstrap my house lexicon — walk my codebase (sample my house-rules doc, a
handful of design docs, and my typed enums / registries / schema constants), extract every term I use with a
specific meaning more than once, classify each as portable (link the established name) or house (note the
concept it renames), and draft the lexicon table. Confirm the terms with me before you commit them. Then,
when I write a mechanism description, a design doc, a runbook, or a handoff, apply the engineering register and
run the audit procedure over the draft and show me the fixes.
(Path B) Read the self-communicate skill resources (its SKILL.md plus the writing/lexicon.md, writing/engineering.md,
writing/rhetoric.md, writing/voice.md, writing/audit.md, and drawing/diagrams.md files under the skills/self-communicate folder).
Bootstrap my house lexicon by walking my codebase per the lexicon's bootstrap recipe, confirm the terms with
me, then use the engineering register to write my docs and the audit procedure to grade them.
```
<!--/adoption-auto-->

## Run the sequence — Interactive mode

Walk it one step at a time. Each step pairs its prompt with what it does and where to read more. `(Path A)` /
`(Path B)` tags mark the steps that differ by how you installed; unmarked steps are the same either way.

<!--adoption-interactive-->
### Step 1 — Fold the method into your CLAUDE.md

The mechanisms are the *what*; the method is the *how* — the AI-First Engineering stance plus the rule-index discipline that decides what earns a spot in a governance doc. Put it in your own house-rules file so it shapes how your agents reason on every boot, not only when a skill fires. Already have a `CLAUDE.md`? Integrate; don't start fresh.

```
Read the AI-First Engineering Method in downloads/CLAUDE-starter.md (Part A) and my existing
CLAUDE.md (or create one if I have none). Propose edits that fold the method into my doc —
adopt / adapt / skip per principle, preserving my current rules. For the rule index, apply the
"earns a spot" test from the claude-md-rule-index mechanism: regression-preventing,
non-derivable-from-local-code, non-local. Show me a diff before writing anything.
```

**Read more:** [CLAUDE-starter (the method)](downloads/CLAUDE-starter.md) · [claude-md-rule-index](agent/governance-doc-controls/claude-md-rule-index.md)

### Step 2 — Survey the repo for missing guardrails

Before adopting any single mechanism, get the map: which mechanisms your repo needs, already has, or would benefit from. Path A runs this as the skill's **audit** mode (advises, changes nothing). Path B asks the same of a plain agent pointed at the catalogue.

```
(Path A) self-governance: run audit mode against my repo. Survey it against the catalogue and produce a
prioritized adopt / adapt / skip plan — highest-leverage, lowest-cost first — and name the one mechanism
you'd build first. Advise only; change nothing.
(Path B) Read the governance-mechanisms catalogue (README, INDEX, and the agent/ models-bridge/ product/
role folders). For each mechanism, judge whether my repo needs it, already has it, or would benefit.
Produce a prioritized adopt / adapt / skip plan, start with the highest-leverage lowest-cost mechanisms,
and tell me the one you'd build first. Advise only; change nothing.
```

**Read more:** [INDEX (the census)](INDEX.md) · [catalogue views](catalogue-views.html)

### Step 3 — Adopt the model-based-engineering kit

The scaling unlock for agents that keep breaking things that "looked unrelated": model your system as typed data that tools read on every run — a state-machine view, a component/zone view, a service-flow view, a deployment-topology view. The starter kit ships fill-in scaffolds for each; the mechanism entry explains why an *executable* model that governs the code beats prose that drifts.

```
Read the model-based-engineering starter kit in downloads/system-models-starter-kit.md and the
executable-source-of-truth mechanism under models-bridge/. Then look at my repo — its services,
state machines, cross-service seams, and deploy topology. Tell me which model views (state-machine,
component/zone, service-flow, deployment-topology) would earn their keep for MY system and which to
skip. For the ones worth it, draft the first view from the matching scaffold, citing real files.
State your assumptions so I correct rather than supply, and confirm the model before you emit anything.
```

**Read more:** [system-models starter kit](downloads/system-models-starter-kit.md) · [executable source of truth](models-bridge/system-models/executable-source-of-truth.md) · [models-bridge role](models-bridge/README.md)

### Step 4 — Adapt the agent-brief validator

If you run more than one agent at a time, a brief-linting gate pays off immediately: it statically checks a task brief *before* the agent spawns and refuses to launch a malformed one. Start from the brief template, then adapt the genre-aware validator to the fields your dispatch actually uses.

```
Read the agent-brief starter in downloads/agent-brief-starter.md and the brief-linting mechanism under
agent/context-and-dispatch/. Look at how I dispatch agents today — what a brief contains, where it lives,
what a bad one looks like. Adapt the brief template to my fields, then draft a brief-linting check that
refuses to launch a brief missing the required markers. Show me the template and the check before writing.
```

**Read more:** [agent-brief starter](downloads/agent-brief-starter.md) · [brief-linting](agent/context-and-dispatch/brief-linting.md) · [role-typed dispatch](agent/context-and-dispatch/role-typed-dispatch.md)

### Step 5 — Wire the operator-loop hooks (reflection + banking) *(Path A)*

The self-operations skill ships a runnable hook library: a turn-end reflection nudge, a memory-routing nudge, and a context-banking check, all gated behind one typed hook substrate so they fire on tempo instead of every turn. Have the skill inspect your runtime and propose which hooks are worth wiring, then adapt the shipped library to your repo.

```
(Path A) self-operations: read your SKILL.md and the shipped hook library (the reflection, memory-routing,
and banking hooks behind the typed hook substrate). Inspect my repo — how agents run, where a turn ends,
where context is banked. Propose which operator-loop hooks are worth wiring for me, adapt the shipped hook
library and its settings snippet to my repo, and show me the wiring before enabling anything.
```

**Read more:** [self-operations starter](downloads/self-operations-starter.md) · [lifecycle hooks](agent/lifecycle-and-observability/lifecycle-hooks.md) · [reflection-facet substrate](agent/lifecycle-and-observability/reflection-facet-substrate.md)

### Step 6 — Adopt the Epic / design-doc / handoff templates

The three planning artifacts an orchestrator authors — the Epic (the effort, with its Definition-of-Done), the design doc (the plan), and the machine-generated handoff (the context carried across sessions). Adopt the templates so your plans *drive* the work instead of being written after the fact.

```
Read the Epic template (downloads/EPIC-TEMPLATE-starter.md), the design-doc template
(downloads/design-doc-template-starter.md), and the handoff scaffold (downloads/emit-handoff-starter.py),
plus the epic-and-design-templates mechanism under agent/governance-doc-controls/. Compare against how I
plan and track multi-step work today. Adapt the three artifacts to my repo — keep the required sections
and the Definition-of-Done — and wire the handoff generator to my session-boundary. Show me the drafts first.
```

**Read more:** [Epic template](downloads/EPIC-TEMPLATE-starter.md) · [design-doc template](downloads/design-doc-template-starter.md) · [handoff generator](downloads/emit-handoff-starter.py) · [epic-and-design-templates](agent/governance-doc-controls/epic-and-design-templates.md)

### Step 7 — Adopt an operational playbook for one substrate *(Path B)*

A playbook is a situation-keyed operating manual for a substrate: for each thing that can go wrong, the symptom, the cause, and the fix. Start with the substrate that breaks most, and let the operator-runbook discipline turn tribal knowledge into a doc your agent can follow.

```
Read the operational-playbook starter (downloads/op-playbook-starter.md) and the operational-playbooks
mechanism under agent/governance-doc-controls/. Pick the substrate in my repo that breaks most often (deploy,
the queue, the host VM, cron — your call, tell me why). Draft a situation-keyed playbook for it: per failure,
the symptom, the cause, and the fix, citing real files. Show me the draft before writing it.
```

**Read more:** [op-playbook starter](downloads/op-playbook-starter.md) · [operational playbooks](agent/governance-doc-controls/operational-playbooks.md) · [operator-runbook skill](agent/governance-doc-controls/operator-runbook-skill.md)

### Step 8 — Bootstrap your house lexicon, then write and audit prose with the skill

The mechanisms, design docs, runbooks, and handoffs you adopt above are all *prose* — and prose an engineer or agent must read cleanly. The self-communicate skill supplies the craft: a house lexicon (so a term means the same thing everywhere), the Diátaxis register (so a doc has the right shape), and an audit that grades a passage and emits fixes. Bootstrap the lexicon first by walking your codebase and confirming the terms with the maintainer; then write and audit prose against the skill.

```
(Path A) self-communicate: bootstrap my house lexicon — walk my codebase (sample my house-rules doc, a
handful of design docs, and my typed enums / registries / schema constants), extract every term I use with a
specific meaning more than once, classify each as portable (link the established name) or house (note the
concept it renames), and draft the lexicon table. Confirm the terms with me before you commit them. Then,
when I write a mechanism description, a design doc, a runbook, or a handoff, apply the engineering register and
run the audit procedure over the draft and show me the fixes.
(Path B) Read the self-communicate skill resources (its SKILL.md plus the writing/lexicon.md, writing/engineering.md,
writing/rhetoric.md, writing/voice.md, writing/audit.md, and drawing/diagrams.md files under the skills/self-communicate folder).
Bootstrap my house lexicon by walking my codebase per the lexicon's bootstrap recipe, confirm the terms with
me, then use the engineering register to write my docs and the audit procedure to grade them.
```
<!--/adoption-interactive-->

## Which path?

| Aspect | Path A — self-governance skill | Path B — catalogue (DIY) |
|---|---|---|
| **Installs** | a Claude plugin | nothing |
| **Runs in your loop** | the skill (gated; greenlight to write) | only what you write |
| **Effort** | auto-triggers, runs the loop | adapt by hand |
| **Best for** | individuals / teams who want it automated | companies, the security-conservative, full control |

## What to reach for first

- **Running more than one agent at a time?** Start with the **agent** role. A
  [brief-linting](agent/context-and-dispatch/brief-linting.md) gate and a
  [pre-commit hook](agent/gates-and-merge-train/pre-commit-hook.md) pay off immediately.
- **Agents keep breaking things that "looked unrelated"?** Reach for the **models-bridge** role. A typed
  [executable source of truth](models-bridge/system-models/executable-source-of-truth.md) that agents read
  and that governs the codebase is the scaling unlock.
- **Shipping a user-facing artifact?** Reach for the **product** role. A
  [content validator](product/validation-and-conformance/content-validator.md) and a closed
  [repair vocabulary](product/repair-vocabulary/remediation-verbs.md) bound what the agent can get wrong.

## The mindset

Every mechanism is written as *the failure it kills* and *why it is not just the cheaper thing everyone
already does*. Keep that framing when you adapt one. Name the failure in **your** system — one you've hit,
or one you can see coming — then borrow the mechanism. A mechanism you can't attach to any failure, real or
anticipated, is one you don't need yet.

For one engineer's experience with this method, see the [paper](https://arxiv.org/pdf/2607.01087).
