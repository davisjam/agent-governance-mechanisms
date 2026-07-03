# Quick start — two ways to adopt these mechanisms

Governance-centric agentic software engineering is an engineering **methodology**, not something you
install and run. The mechanisms in this catalogue are patterns — you *adapt* them to your stack, your
agents, and your failure modes.

However, Claude is capable of assisting you through **self-governance**: reading the catalogue and turning
it on your own repository. There are **two on-ramps to the same destination** — pick by how much you want
automated versus how much you want to keep in your own hands.

## Path A — DIY with the catalogue (installs nothing)

The **safe default**, and the right choice for a company — or anyone who can't or won't run a third-party
plugin. Nothing executes in your agent loop that you didn't write: you read the patterns and adapt them
by hand. The fastest way is to let your coding agent read the catalogue and propose a plan grounded in
**your** codebase.

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

## Path B — the self-governance skill (batteries included)

The **same loop, packaged as an installable Claude skill** that auto-triggers and runs it for you — no
prompt to paste. Convenient, but understand what you're installing: a **third-party agentic plugin that
reads, and on your approval writes, your repo**. It is source-visible (read its `SKILL.md`,
`principles.md`, and `reference/` before you trust a line), MIT-licensed, **gated** (its *audit* mode only
advises; its *interpret-failure* mode proposes and acts only on your greenlight), and does no network
I/O. Still: vet it before enterprise use, and check it clears your org's plugin policy — Path A exists
precisely for teams where installing it isn't an option.

Install it directly — copy-paste these (you or Claude can run them); no marketplace needed:

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

Start a new Claude session and the skill loads. *(Want team-wide install with auto-updates? The repo also
ships as a plugin marketplace — `/plugin marketplace add davisjam/agent-governance-mechanisms` — once you
enable that route.)*

Two modes:

- **audit** — survey your repo against the catalogue → a prioritized adopt / adapt / skip plan (advises;
  changes nothing).
- **interpret-failure** — a failure just recurred → classify it and convert the *class* into a durable
  control; proposes first, writes the lint/test/gate only on your go-ahead.

It also carries the AI-First Engineering Method as an ambient operating stance, so the agent reasons the
way the catalogue was built. The skill covers the **agent** and **models-bridge** roles — the "self" a
coding agent governs; the **product** role stays in the full catalogue.

## Which path?

|  | Path A — catalogue (DIY) | Path B — self-governance skill |
|---|---|---|
| **Installs** | nothing | a Claude plugin |
| **Runs in your loop** | only what you write | the skill (gated; greenlight to write) |
| **Effort** | adapt by hand | auto-triggers, runs the loop |
| **Best for** | companies, the security-conservative, full control | individuals / teams who want it automated |

They're **not exclusive** — DIY org-wide, and use the skill on a personal project.

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

The system that this catalogue was distilled from is live at **[scholaccess.com](https://scholaccess.com)**;
the case study is the [paper](https://arxiv.org/pdf/2607.01087).
