# Quick start — adopt these mechanisms in your own repo

This catalogue is descriptive, not a framework. There is nothing to install. The controls are
patterns — you *adapt* them to your stack, your agents, and your failure modes. The fastest way to do
that is to let your coding agent read the catalogue and propose a plan grounded in **your** codebase.

## The three-step loop

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
