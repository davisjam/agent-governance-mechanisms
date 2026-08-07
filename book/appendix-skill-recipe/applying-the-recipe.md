<!-- point: the-recipe-generalizes-across-three-independent-domains | The recipe generalizes across three independent domains. | terms: self-communicate, self-governance, self-operate -->
The recipe is only worth stating if it generalizes. This chapter runs it three times — on
self-communicate, self-governance, and self-operate — three independent domains factored the same way.
Each case answers the identical seven questions in the same order, so you can read the three line for line
and watch the same skeleton surface in each. The third, self-operate, is the payoff: operations looks least
like something you can model, yet it factors as cleanly as the other two.

## self-communicate

### What problem is this skill solving?

The fleet and its operator produce prose and diagrams constantly — control descriptions, design docs,
mechanism entries, runbooks, handoffs, and the orchestrator's own status reports and tradeoff explanations
to the human. Ungoverned, it drifts: inconsistent terms, the wrong doc shape, LLM-tell density,
hand-generated bad PNGs. The agent *can* write, but writes *inconsistently against a standard*. Install the
craft so every document comes out terse, consistent, and correctly shaped.

### Identify the base model.

**Rhetoric** — good technical prose is a craft with named parts, not a matter of taste. See prose as
classical figures applied with variety, and the register, lexicon, voice, and audit all attach to that one
frame. The second leg, visualization, rests on the same claim: a diagram is that craft for the shapes prose
cannot carry.

### Identify the orthogonal models.

One file per facet.

- **Rhetoric** (`writing/rhetoric.md`) — the device toolkit; sentence shape.
- **Diátaxis engineering register** (`writing/engineering.md`) — the doc's shape: tutorial, how-to,
  reference, explanation.
- **Lexicon** (`writing/lexicon.md`) — one concept, one word.
- **Voice** (`writing/voice.md`) — the register and sound.
- **Audit** (`writing/audit.md`) — the grading procedure.
- **Visualization** (`drawing/diagrams.md`, Mermaid-first, with `drawing/charts.md` and `drawing/tables.md`
  for data figures) — the shapes prose cannot carry.

### Explain why these are orthogonal.

Each cuts an independent axis of a document. A doc's *shape* (Diátaxis) is independent of its *vocabulary*
(lexicon), which is independent of its *register* (voice), which is independent of its *sentence devices*
(rhetoric): change the mode without touching the terms, fix a term without re-shaping the doc. The top
split is prose versus drawing — argument versus shape. Audit is the meta-facet that grades them all. No two
facets half-say the same thing.

### Show the governing `SKILL.md` principle.

*Less is more — the representation must not distract from the idea* (Hemingway, Tufte, Picasso's *Bull*),
plus the order of application: name the genre and mode first, draft in the house voice with varied devices,
name concepts from the lexicon, draw the shape where there is one, and audit before you ship. A second
stance runs underneath: *name the concept, then use the name.*

### Show the resulting directory layout.

```
self-communicate/
  SKILL.md
  writing/   rhetoric.md  engineering.md  lexicon.md  voice.md  audit.md
  drawing/   diagrams.md  charts.md  tables.md  svg-audit.py
```

One directory per leg, one file per facet — the tree *is* the orthogonal-model set.

### Lessons learned.

The base model, rhetoric-as-craft, is what turns a pile of style tips into a skill. Facets map one-to-one
to files, so progressive disclosure loads only the one the task touches. It **composes**: it owns the prose
the other two skills produce — governance entries and runbooks are written in its register — cited by base
model rather than copied. A facet can be **mined, not only authored**: the lexicon is bootstrapped from a
codebase walk and kept living. It is a **soft** skill; the one hard control it suggests is running the audit
as a gate.

## self-governance

### What problem is this skill solving?

A fleet at velocity keeps producing recurring failures — the same bug class, a lint that mis-fires, a
manual step redone by hand, an agent regression. Patching instances never stops the class. Convert each
recurring failure into a **durable mechanism**, and at design time recognize which structural traits
warrant a mechanism by construction.

### Identify the base model.

**Two kinds of governance move.** A mechanism either **prevents** — a *constraint* that scopes the action
space so the wrong move cannot be picked, the architecture — or **detects** — a *sensor* that fires after
the fact, a lint, gate, or test. That single distinction decides, for any failure, what you build.

### Identify the orthogonal models.

- **The mechanism census** (`reference/INDEX.md` plus `reference/<role>/<family>/<mechanism>.md`, the
  catalogue of patterns you draw from).
- **Soft-vs-hard enforcement** — the form.
- **The target axis** — agent, models-bridge, product.
- **The form taxonomy** — the nine forms.
- **Ambient principles** (`principles.md`) — the reflexes applied on every touch.
- **The two modes** — AUDIT and INTERPRET-FAILURE — plus the **MBSE starter kit** (`templates/`).

### Explain why these are orthogonal.

This is the case's headline: why governance splits into a catalogue with cross-cutting columns rather than
one huge reference doc. **Move** (constraint, sensor, package) is independent of **form** (soft, hard): a
constraint can be soft (a model that aims) or hard (a compiler-enforced enum); a sensor can be soft (a
convention) or hard (a blocking lint). Both are independent of **target** and of the **form taxonomy**.
Because the axes are orthogonal, any mechanism is a *point* in that space — which is why the census is a
queryable table ("missing prevention? scan the constraint rows"), not a flat list. The principles are a
separate ambient layer that deliberately does not live in the census.

### Show the governing `SKILL.md` principle.

*Convert recurring failures into durable guardrails; guidance aims, machinery holds.* Plus three reflexes:
**architecture before sensors** (prefer the constraint that makes the error impossible), **right-size the
fix** (the smallest sound change; float the larger scheme), and **propose, don't install** — a skill is
soft, so hard mechanisms are scaffolded and handed to a human or harness; never claim *enforced* when you
have only *recommended*.

### Show the resulting directory layout.

```
self-governance/
  SKILL.md
  principles.md                       # the ambient-stance facet
  reference/  INDEX.md  ABSTRACTIONS.md  README.md  <role>/<family>/<mechanism>.md   # the census facet
  templates/  system-models-starter-kit.md  state-machine-model-starter.py
              component-zone-model-starter.py  service-flow-*  deployment-topology-starter.py  # scaffolds
```

The tree mirrors the split: census (`reference/`), principles (`principles.md`), scaffolds (`templates/`).

### Lessons learned.

The base model, prevent versus detect, is the cut every other axis hangs off. Orthogonal axes make the
catalogue something you **query**, not read top to bottom. A skill **cannot install hard mechanisms** — it
proposes them, so honesty about enforced-versus-recommended is part of the craft. The primary failure is
the **teetering tower**: default to *skip*, and proportion governance to the operation. It **composes**: it
mints the mechanisms self-operate runs and self-communicate documents. *Cite, don't mirror* — a mirrored
skill fires almost never.

## self-operate

<!-- point: operations-factors-as-cleanly-as-any-recurring-domain | Operations, the least modelable domain, factors as cleanly as the rest. | terms: self-operate, lifecycle -->
The strongest case. Operations is *less* obviously modelable than communication or governance, yet it
factors the same way — which is the evidence that almost any recurring engineering domain factors into a
base model plus orthogonal overlays.

### What problem is this skill solving?

Running an agent-fleet repo is a sprawl of ad-hoc operations — dispatch and recover agents, keep the
mainline deployable, reclaim disk, weather colima and host-tool trouble, watch cron health, RCA an
ambiguous signal. Met cold, each break is a fresh fire, and it looks *least* like something you can model:
"it's just ops." Give it a positive lifecycle map so every symptom routes to a class, and typed runbooks so
each fix is repeatable.

### Identify the base model.

**The engineering lifecycles.** A fleet repo runs the same few: manage-agents, manage-context,
manage-git-repo, manage-deploy, manage-dev-env, plus cron and govern-your-own-loop. Every symptom belongs
to one lifecycle, so every break routes to a *class* instead of being met cold. The insight the case turns
on: ops *is* modelable — the lifecycles are the base model hiding in the sprawl.

### Identify the orthogonal models.

- **The lifecycle map / symptom→doc catalog** — the routing table.
- **Typed runbooks** (`examples/runbook-*.md`) — steps typed RUNNABLE, JUDGMENT-AUTOMATABLE, or
  JUDGMENT-IRREDUCIBLE; the procedures a symptom routes to.
- **The runnable hook library** (`hooks/`) — reflection substrate, typed hook substrate, banking substrate;
  the machinery that fires a skipped reflex at its moment.
- **Build and handoff templates** (`templates/`) — for when operating spills into building.

### Explain why these are orthogonal.

They cut operations along three independent axes: **where** (the lifecycle class — which resource broke),
**what-to-do** (the runbook's typed steps), and **when-it-fires** (the hook). One routing table, many
runbooks, a separate firing layer: a symptom's class does not change its runbook's steps, and a hook fires
regardless of which lifecycle owns the break. That a domain which looks like undifferentiated "ops" factors
this cleanly is the demonstration the whole appendix is building toward.

### Show the governing `SKILL.md` principle.

*Orient positive first, then route a break to its class.* Know the healthy baseline before you hunt; meet
every symptom as a member of a lifecycle; when a failure **recurs**, hand it to self-governance — the
operate-govern bridge. Supporting reflexes: *determinize the runnable, brief the judgment*, and *the
lifecycle is a state machine, not a habit.*

### Show the resulting directory layout.

```
self-operations/
  SKILL.md
  principles.md
  examples/   lifecycle-L1..L6-*.md   runbook-*.md          # lifecycle models + typed runbooks
  hooks/      reflection_facet*.py  hook_*.py  _hook_*.py  README.md  ...   # the runnable hook library
  templates/  pointers-starter.yaml  runbooks-starter.yaml
              gen-and-lint-partb-starter.py  EPIC-TEMPLATE-starter.md  design-doc-template-starter.md
```

### Lessons learned.

The headline: operations is less obviously modelable than prose or governance, yet it factors the same way
— evidence the recipe **generalizes** to almost any recurring engineering domain. The base model, the
lifecycles, was **discovered, not obvious**; naming it converted firefighting into routing. Runbooks are
**typed**, so the model itself says what to automate, what to brief, and what to escalate. The repo-specific
bindings are generated and ref-linted — a non-executable index earns trust from a ref-check, not from
tests. It **composes**: it runs the mechanisms self-governance mints, hands recurrences back to it, and
writes its runbooks in self-communicate's register.
