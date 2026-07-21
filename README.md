# Agent Governance Mechanisms

<!-- summary: A pattern catalogue of the mechanisms for governable agentic software engineering — 62 across three roles. -->

*A catalogue of the **governance mechanisms** that keep a fleet of AI coding agents productive while
holding the cost of their failures within bounds — distilled from a 12-week case study of building a
production system with frontier coding agents. Each mechanism is written like a design pattern: the
recurring failure it kills, and why it is **not** just the cheaper thing everyone already does.*

## Between two schools of thought

Two common ways to build with agents sit at opposite poles. This catalogue is about the **midway**.

| Vibe coding | · Governance-centric · — **the midway** | Oversight-centric |
|:---|:---:|:---|
| Prompt, accept what looks right, iterate by feel. Fast — but the same failures keep recurring and human review becomes the bottleneck. | Let velocity **expose** failures, and **convert** each recurring one into a durable guardrail. The guardrails grow from real failures, so code stays fast **and** trustworthy. This is **governance conversion**. | Check *everything* before you trust it — a human reviewing every change, or a formal spec verified against (spec-driven development is this). Rigorous — but checking is the bottleneck, and neither humans nor specs anticipate what only breaks at velocity. |
| *all velocity — no guardrails* | *velocity + guardrails grown from failure* | *all oversight — everything checked* |
| e.g. [Karpathy](https://x.com/karpathy/status/1886192184808149383) · [Gas Town](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04) | | e.g. [Meyer, CACM](https://dl.acm.org/doi/full/10.1145/3773295) · [vibe-OS / vibe-tools](https://homes.cs.washington.edu/~oskin/vibeos/vibetools.html) |

**Both poles pay the *pet tax.*** Each gives per-change human attention — *coaxing* the output (left) or
*inspecting* it (right) — and that attention scales linearly with the herd, so it becomes the bottleneck.
The midway is **cattle, not pets**: you build the fences and chutes once, and the *guardrails* ride each
change, not a person. One pole pets the fleet out of affection, the other out of anxiety; only the middle
runs the herd.

This middle column isn't new. It's the agentic-era instantiation of quality practices long standard in
regulated industry — documented process, requirements traceability, verification tiers scaled to
criticality, corrective-and-preventive action. What's new is the **substrate**. Those programs run on
manually-maintained dead documents — Word, Excel, DOORS — that drift the moment they're written and need
dedicated staff to keep. Here the same process runs on **executable, agent-maintained models that can't
drift**: the traceability matrix is a queried model behind a drift gate, the process rules are enforced
infrastructure, the verification records are machine-checked against the code rather than filed in a
spreadsheet. The contribution isn't the assurance discipline — it's making it *live*, and tractable for a
team of one.

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

## Why you might NOT want to use this

Governance has a cost — every mechanism taxes every future change and every agent's context budget. The
failure mode of adopting it wholesale is a **tower of governance nobody wants** — mechanisms manufactured
faster than they earn their keep, until the overhead outweighs the failures they were meant to prevent
(and there's an adverse selection: the people most drawn to a governance catalogue are the ones most at
risk of over-building it).

So it's **descriptive, not prescriptive** — a menu to tailor to your needs, not a bar to clear. If you
can't name the failure a mechanism prevents in *your* system, you might not need it yet.

## Read the catalogue

- **[The catalogue — interactive web view](https://davisjam.github.io/agent-governance-mechanisms/)** —
  the best way to read it: the governance map, a clickable census, and a full writeup per mechanism.
- **[The paper](https://arxiv.org/pdf/2607.01087)** — *Cheap Code, Costly Judgment: A Case Study on
  Governable Agentic Software Engineering* — the theory, evidence, and testable propositions.
- **[Quick start](quick-start.md)** — adopt these in your own repo.
- **The live system** these mechanisms govern: **DocAble** ([scholaccess.com](https://scholaccess.com)).

## The two skills

The catalogue also ships as **two partner Claude skills** (one plugin, `agent-governance`):

- **self-governance** — *harden.* Audit your repo for missing guardrails, or convert a recurring failure
  into a durable control. Carries the AI-First Engineering Method as its operating stance, plus the
  agent + models-bridge control census as on-demand reference.
- **self-operations** — *operate.* Run the agent-fleet substrate day to day: the positive lifecycle map
  (agents, context, git, deploy, dev-env, cron) plus a symptom → resolving-doc catalog when something
  breaks. It bootstraps to your repo by inspection.

They partner: **operate routes a break to its fix; when a failure recurs, it hands the class to
self-governance to convert into a control.** Install both from the [quick start](quick-start.md).

They're **two lenses on one substrate, not competitors.** self-governance is the *census of controls* and
the engine that mints new ones — the **design-time** view (what controls exist, which you're missing, how
to add one). self-operations *runs the substrate those controls govern* — the **run-time** view (the
lifecycle you operate, the runbook you follow, the hook you wire). The same mechanism appears in
self-governance's census *and* is operated day-to-day through self-operations — one substrate seen
design-time vs run-time, not two copies. The loop closes between them: operate surfaces a recurring break →
harden mints the control → it joins the census *and* the running substrate.

## Using this repo

**To read it yourself, use the [web view](https://davisjam.github.io/agent-governance-mechanisms/)** —
that's the pretty version, with the governance map, a clickable census, and a full writeup per
mechanism. This raw repo is what you **hand to your coding agent**: vendor it (or the
[starter `CLAUDE.md`](downloads/CLAUDE-starter.md)) into your project, point your agent at it, and ask it
to produce a plan to adopt / adapt / apply the mechanisms in your context — see the
[quick start](quick-start.md).

**Already have a `CLAUDE.md`?** Don't start fresh — fold the *method* (the AI-First Engineering stance in
[`downloads/CLAUDE-starter.md`](downloads/CLAUDE-starter.md)) into your existing doc, adopt / adapt / skip
per principle. The [quick start](quick-start.md) has ready prompts for before *or* after you install the
skill.

The source is organized by role — [`agent/`](agent/) · [`models-bridge/`](models-bridge/) ·
[`product/`](product/) — with the full census in [`INDEX.md`](INDEX.md). `catalog.py` validates the
schema and builds the web view (`catalog.py validate` · `build` · `deploy local|github`; see
[`CLAUDE.md`](https://github.com/davisjam/agent-governance-mechanisms/blob/main/CLAUDE.md)).

## Start small, and make it yours

Start with the highest-leverage, lowest-cost mechanisms for the failures your agents *actually* make — a
governance doc, a gate or two — and add mechanisms only as velocity surfaces the failures they prevent.
Growing guardrails from real failure **is** the method (*governance conversion*).

**Adapt the mechanisms to your environment** — your language, your agents, your CI; they are patterns, not
a stack. But keep the part that travels furthest: most of the value lands **on the developer's own
machine, before CI ever runs**. Every developer already works locally; this method makes that local loop
unusually productive — the agent fails fast against the same gates a reviewer would apply, so defects are
caught and fixed *before the push*, and CI becomes confirmation rather than the first line of defense.
Whatever your stack, that "trustworthy locally, not just in CI" property is the part most worth porting.

---

To learn more about the experience behind this repository, see the
[*Cheap Code, Costly Judgment*](https://arxiv.org/pdf/2607.01087) paper.
