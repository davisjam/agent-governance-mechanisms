# Quick start — two ways to adopt these mechanisms

Governance-centric agentic software engineering is a **methodology**, not something you install and run —
the mechanisms are patterns you *adapt* to your stack, your agents, and your failure modes.

Claude can help: it reads the catalogue and turns it on your own repo. Two ways in:

- **Skill (Path A)** — installable, auto-triggers, runs the loop for you.
- **DIY (Path B)** — read the patterns and adapt them by hand; the route when you can't run a plugin.

## Fold the method into your own `CLAUDE.md`

Both paths give you the *mechanisms*. The **method** is the AI-First Engineering stance (Part A) plus the
rule-index discipline; put it in your project's own governance doc, so it shapes how your agents reason on
every boot — not only when the skill fires. Already have a `CLAUDE.md`? Integrate; don't start fresh. Two
ways in:

- **Before you install anything** — point your agent at this repo:

  > Read the AI-First Engineering Method in `downloads/CLAUDE-starter.md` (Part A) and my existing
  > `CLAUDE.md`. Propose edits that fold the method into my doc — adopt / adapt / skip per principle,
  > preserving my current rules. Show me a diff.

- **After you install the skill** — have Claude introspect what it now carries:

  > self-governance: read your own `principles.md` and the `CLAUDE-starter` you bundle, compare against my
  > repo's `CLAUDE.md`, and propose how to integrate the method — adopt / adapt / skip per principle,
  > keeping what I already have.

## Path A — the self-governance skill (batteries included)

The whole loop as an installable Claude skill that auto-triggers — no prompt to paste. Know what you're
installing, though: a **third-party plugin that reads, and on your approval writes, your repo**.

- **Source-visible** — read its `SKILL.md`, `principles.md`, and `reference/` before you trust it.
- **MIT-licensed.**
- **Gated** — *audit* only advises; *interpret-failure* acts only on your greenlight.
- **No network I/O.**

If a plugin isn't an option for your org, use Path B.

**Quickest — install from the marketplace.** In Claude Code, two commands (the repo *is* a plugin
marketplace):

```
/plugin marketplace add davisjam/agent-governance-mechanisms
/plugin install agent-governance@agent-governance-mechanisms
```

Start a new session and the skill loads. Pull a later release with `/plugin marketplace update
agent-governance-mechanisms`.

**Or copy-paste** — no marketplace, e.g. if you'd rather vendor the folder yourself:

```bash
# clone the catalogue (or reuse a clone you already have)
git clone https://github.com/davisjam/agent-governance-mechanisms.git

# install the skill for your user, across every project …
mkdir -p ~/.claude/skills
cp -R agent-governance-mechanisms/plugin/self-governance/skills/self-governance \
      ~/.claude/skills/self-governance

# … or scope it to a single repo instead
mkdir -p .claude/skills
cp -R agent-governance-mechanisms/plugin/self-governance/skills/self-governance \
      .claude/skills/self-governance
```

Start a new Claude session and the skill loads.

Two modes:

- **audit** — survey your repo against the catalogue → a prioritized adopt / adapt / skip plan (advises;
  changes nothing).
- **interpret-failure** — a failure just recurred → classify it and convert the *class* into a durable
  control; proposes first, writes the lint/test/gate only on your go-ahead.

It also carries the AI-First Engineering Method as an ambient operating stance, so the agent reasons the
way the catalogue was built. The skill covers the **agent** and **models-bridge** roles — the "self" a
coding agent governs; the **product** role stays in the full catalogue.

## Path B — DIY with the catalogue (installs nothing)

The **conservative choice** — for a company, or anyone who can't run a third-party plugin. Nothing runs in
your agent loop that you didn't write; you adapt the patterns by hand. Fastest is to let your coding agent
read the catalogue and propose a plan grounded in **your** codebase.

1. **Install a governance doc.** Put a `CLAUDE.md` (or your agent's equivalent house-rules file) at your
   repo root — the [`claude-md-rule-index`](agent/governance-doc-controls/claude-md-rule-index.md) control
   explains what earns a spot in it (regression-preventing · non-derivable-from-local-code · non-local).
   Start small; it grows as you codify each control you adopt.

2. **Point your agent at this catalogue.** Vendor a copy of `governance-mechanisms/` into your repo (or
   just hand your agent the URL), and ask it to read the [`README`](README.md), the
   [`INDEX`](INDEX.md), and the role folders ([`agent/`](agent/) · [`models-bridge/`](models-bridge/) ·
   [`product/`](product/)).

3. **Ask for an adopt / adapt / apply plan.** A prompt that works:

   > Read the governance-mechanisms catalogue. For each control, judge whether my repo needs it, already
   > has it, or would benefit. Produce a prioritized plan: which controls to **adopt** as-is, which to
   > **adapt** to my stack, and which to **skip** (with the reason). Start with the highest-leverage,
   > lowest-cost controls, and tell me the one you'd build first.

**Ready-made starters** (adopt-and-adapt) — drop these in your repo and edit:

- a [`CLAUDE.md` starter](downloads/CLAUDE-starter.md) — the governance-doc shape;
- an [Epic template](downloads/EPIC-TEMPLATE-starter.md), a [design-doc template](downloads/design-doc-template-starter.md), and an [agent-brief template](downloads/agent-brief-starter.md) — the three artifacts an orchestrator authors;
- an [operational-playbook template](downloads/op-playbook-starter.md);
- a runnable [governance-lint example](downloads/governance-lint-example.py) — the real "regex-against-structured-formats" lint, self-contained: copy the shape, change the check.

The templates encode the required sections + Definition-of-Done so your plans *drive* the work instead of being written after the fact.

## Which path?

| Aspect | Path A — self-governance skill | Path B — catalogue (DIY) |
|---|---|---|
| **Installs** | a Claude plugin | nothing |
| **Runs in your loop** | the skill (gated; greenlight to write) | only what you write |
| **Effort** | auto-triggers, runs the loop | adapt by hand |
| **Best for** | individuals / teams who want it automated | companies, the security-conservative, full control |

They're **not exclusive** — use the skill on a personal project, and go DIY org-wide.

## What to reach for first

- If you run **more than one agent at a time**: start with the **agent** role — a
  [brief-linting](agent/context-and-dispatch/brief-linting.md) gate and a
  [pre-commit hook](agent/gates-and-merge-train/pre-commit-hook.md) pay off immediately.
- If your agents keep **breaking things that "looked unrelated"**: the **models-bridge** role — a typed
  [executable source of truth](models-bridge/system-models/executable-source-of-truth.md) that agents
  read and that the codebase is generated from — is the scaling unlock.
- If you ship a **user-facing artifact**: the **product** role — a
  [content validator](product/validation-and-conformance/content-validator.md) and a closed
  [repair vocabulary](product/repair-vocabulary/remediation-verbs.md) bound what the agent can get wrong.

## The mindset

Every control is written as *the failure it kills* and *why it is not just the cheaper thing everyone
already does*. When you adapt one, keep that framing: name the recurring failure in **your** system
first, then borrow the mechanism. A control you can't attach to a real failure is one you don't need yet.

The system that this catalogue was distilled from — **DocAble** — is live at **[scholaccess.com](https://scholaccess.com)**;
the case study is the [paper](https://arxiv.org/pdf/2607.01087).
