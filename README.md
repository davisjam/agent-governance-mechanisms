# Agent Governance Mechanisms

<!-- summary: A pattern catalogue of the controls for governable agentic software engineering — 51 across three roles. -->

*A catalogue of the **governance mechanisms** that keep a fleet of AI coding agents productive while
holding the cost of their failures within bounds — distilled from a 12-week case study of building a
production system with frontier coding agents. Each mechanism is written like a design pattern: the
recurring failure it kills, and why it is **not** just the cheaper thing everyone already does.*

## Between two schools of thought

Two common ways to build with agents sit at opposite poles; this catalogue is about the **midway**.

- **Vibe coding** — prompt, accept what looks right, iterate by feel. Fast, but the same failures keep
  recurring and human review becomes the bottleneck.
- **Oversight-centric** — check *everything* before you trust it, whether a human reviews every change or
  a formal specification is verified against (spec-driven development is this). Rigorous, but checking is
  the bottleneck, and neither humans nor specs anticipate what only breaks at velocity.
- **Governance-centric (the midway)** — let velocity *expose* failures, and *convert* each recurring one
  into a durable guardrail. The guardrails grow from real failures, so code stays fast **and**
  trustworthy. This is **governance conversion**.

## Governance has two mechanisms

A guardrail is one of two kinds:

- **Architecture** — make the error **impossible by construction**: a typed model with one sanctioned
  seam, a state that can't be represented wrongly. Software
  [poka-yoke](https://en.wikipedia.org/wiki/Poka-yoke) — error-*proofing*.
- **Control** — where you can't prevent it, **observe and guard** the behavior: a lint, a gate, a
  validator, an audit that fires on a violation and holds the line. Error-*catching*.

Every mechanism in the catalogue governs one of three **roles** — the **agent** fleet, the **models**
that bridge agents and code, or the shipped **product** — and enforces either **hard** (deterministic)
or **soft** (probabilistic) or a mix.

## Read the catalogue

- **[The catalogue — interactive web view](https://davisjam.github.io/agent-governance-mechanisms/)** —
  the best way to read it: the control-map figure, a clickable census, and a full writeup per mechanism.
- **[The paper](https://arxiv.org/pdf/2607.01087)** — *Cheap Code, Costly Judgment: A Case Study on
  Governable Agentic Software Engineering* — the theory, evidence, and testable propositions.
- **[Quick start](quick-start.md)** — adopt these in your own repo.
- **The live system** these controls govern: [scholaccess.com](https://scholaccess.com).

## Using this repo

This repo is meant to be **leveraged by your coding agent**, not browsed by hand. Vendor it (or the
[starter `CLAUDE.md`](downloads/CLAUDE-starter.md)) into your project, point your agent at it, and ask it
to produce a plan to adopt / adapt / apply the mechanisms in your context — see the
[quick start](quick-start.md).

The source is organized by role — [`agent/`](agent/) · [`models-bridge/`](models-bridge/) ·
[`product/`](product/) — with the full census in [`INDEX.md`](INDEX.md). `catalog.py` validates the
schema and builds the web view (`catalog.py validate` · `build` · `deploy local|github`; see
[`CLAUDE.md`](CLAUDE.md)).
