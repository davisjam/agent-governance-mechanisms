<!-- point: a-skill-is-the-smallest-unit-of-method-you-install | A skill is the smallest unit of method you can install. | terms: skill-soft-control -->
A skill is the smallest unit of method you can install. Package a capability or a discipline once, and
every fresh agent picks it up without being re-taught. This appendix is the how-to: the anatomy every
skill shares, the two kinds a skill can be, the steps to write each, and the ways they fail. The three
skills that ship with this book — self-operate, self-governance, self-communicate — are the worked
examples throughout.

> ### Foreword — the vendor's guidance
>
> Anthropic publishes a best-practices guide for skill authoring, and it is worth reading before this
> appendix. Its core moves, quoted from *Skill authoring best practices* (Claude platform documentation):
>
> - **The context window is a public good.** "Your Skill shares the context window with everything else
>   Claude needs to know." So *concise is key*: "Only add context Claude doesn't already have." The
>   default assumption is that "Claude is already very smart" — challenge every paragraph to justify its
>   token cost.
> - **Progressive disclosure.** At startup only each skill's `name` and `description` are pre-loaded;
>   Claude reads `SKILL.md` when the skill becomes relevant, and reads bundled files only as needed. "Keep
>   SKILL.md body under 500 lines"; push anything not needed on every invocation into a reference file, and
>   keep references "one level deep from SKILL.md."
> - **The description does the discovery.** It "should include both what the Skill does and when to use
>   it," must be written "in third person," and is capped at 1,024 characters. "Claude uses it to choose
>   the right Skill from potentially 100+ available Skills."
> - **Set appropriate degrees of freedom.** A fragile, must-run-in-sequence task is "a narrow bridge with
>   cliffs on both sides" — give exact steps. An open-ended one is "an open field with no hazards" — give
>   direction and trust the model.
> - **Build evaluations first.** "Create evaluations BEFORE writing extensive documentation." Test the
>   skill against real past tasks, across every model you plan to run it on.
>
> *— Anthropic, "Skill authoring best practices," retrieved 2026-08-04. Follow it for the mechanics; this
> appendix adds the shape the vendor guidance does not name.*

## Anthropic's take, in brief

The foreword summarizes it faithfully, so hold onto the shape of it. Anthropic answers one question well:
how do you *package* a capability so an agent discovers it and follows it cheaply? The answers are
procedural and file-structural — a `SKILL.md` with a triggering description, progressive disclosure across
bundled files, degrees of freedom matched to the task, evaluations built first. The unit of thought is one
task behind one interface: extract the PDF, fill the form, write the commit message. Read as a manual for
building a callable, it is complete and correct, and you should follow it to the letter.

## Our take: a skill is a layer of models the fleet reasons through

<!-- point: a-mastery-skill-encodes-judgment-as-a-model-reasoned-through | A mastery-skill encodes judgment as a model the agent reasons through. | terms: mastery-skill, skill-soft-control -->
Here the book parts from the vendor guidance — not to correct it, but to go a layer deeper. Start with what
the two takes **share**, because it is most of the mechanics. Both structure a skill as a `SKILL.md` an
agent discovers by its description and loads on demand. Both lean on progressive disclosure to keep the
context window honest. Both know a skill is written *for an agent to read and act on*. On the anatomy, we
and Anthropic agree, and this appendix's "anatomy" section is straight vendor practice.

The **difference** is what a skill *is*. Anthropic treats a skill as a packaged capability — a thing the
agent **invokes**. This book treats the deeper kind of skill as a **layer of models the fleet reasons
through** — a thing that shapes how the agent works even when nothing calls it by name. That is the book's
Modeling-Thesis reading of a skill, and it splits skills cleanly into the two kinds:

- **A tool-skill packages a capability the agent *invokes*.** It is a callable. The agent recognizes the
  task, reaches for the skill, makes the call, and moves on. Its governance move is *package*: it bundles an
  interface so the call is correct and cheap. Anthropic's guide is the complete manual for this kind, and
  nothing here improves on it.
- **A mastery-skill encodes judgment as a model the agent reasons *through*.** It is not a callable but a
  **governed layer**. The agent does not invoke it once and return; it *thinks in it* while doing the work —
  the way an expert carries a mental model that colors every decision. Its governance move is to shape
  behavior: it installs the base model and the orthogonal models of a craft, so the whole class of work
  comes out the way you want. This is the layer the vendor guidance does not name, and the one this book
  gives a construction recipe.

Three claims carry the framing, each in the book's own vocabulary.

- **A skill is a soft mechanism; a mastery-skill is a governed *layer* of them.** A skill can aim a
  probabilistic agent, never force one — soft, in the book's soft/hard axis (see
  [The Skills](4.2-the-skills.html)). A tool-skill aims a single call. A mastery-skill aims the *judgment*
  behind a whole task, which is why it is built as a stack of models rather than a snippet of instructions:
  a base model of the domain, orthogonal models cutting it along independent axes, and a `SKILL.md` that
  ties them. That stack *is* the layer the fleet reasons through — the same layered-models discipline the
  rest of the book applies to code, turned on the skill itself.
- **The layer turns on one base model, or it is a pile of tips.** A capability you can package thinly; a
  discipline you cannot. What separates a mastery-skill from a heap of advice is whether its resources hang
  off a single fundamental abstraction the agent can reason *from*. Miss the base model and "concise,
  well-structured, tested" still yields disconnected tips — a manual, not a model.
- **Installing judgment is governance, not documentation — judgment as infrastructure.** A mastery-skill
  encodes how you want the work done, which is to say it biases the agent's search toward your standards.
  That is a governance act, the same move as a project rule in the fleet's boot-context `CLAUDE.md` or a
  lint, one rung softer on the enforcement axis. A tool-skill is a tool; a mastery-skill is *governed
  judgment made part of the environment the fleet runs in*.

The punchline sets the two takes side by side. **Anthropic tells you how to package a capability so an agent
can call it. MAGE tells you how a skill becomes a governed layer of models that shapes how the fleet
works** — deeper because it is about judgment-as-infrastructure, not file structure. One rung softer than a
rule or a lint, but the same kind of thing: a model the fleet reasons through, installed once and inherited
by every agent after.

<!-- point: the-industry-is-converging-from-rules-to-judgment | The industry is converging from rule lists toward installed judgment. | terms: judgment-into-infrastructure, mastery-skill -->
This is not a quarrel with Anthropic; it is a reading of where Anthropic itself is heading. Its guidance for
`CLAUDE.md` and `SKILL.md` has been moving *away* from long lists of specific prohibitions — enumerate every
forbidden command, name each thing the agent must never do — and *toward* the language of taste and
delegated autonomy: describe the goal and the standard, trust the model's judgment, delete the brittle
specifics. That is a good move, and the right one; a rule list is a soft mechanism that rots the moment the
world shifts under it, and a capable model does better with the intent than with a hundred edge-case bans.
MAGE's mastery-skill *is* that move, given a name and a structure. Where the newer guidance says "use taste,
delegate autonomy," this book says what taste-you-can-install actually is: **encoded judgment as a governed
layer of models the fleet reasons through** — judgment as infrastructure, not a rule list. The industry is
converging on a shift from rules to judgment. The layered-models-plus-governance vocabulary here is the
articulated form of that convergence, and a step ahead of it, because it says *how* judgment
becomes infrastructure — a base model, orthogonal facets, a tying principle, fired by a hook — rather than
only "trust the agent more."

<!-- point: a-governed-layer-sits-passive-until-a-hook-fires-it | A governed layer sits passive until a hook fires it. | terms: skill-soft-control, reflection-hook -->
A last practical consequence, because a governed layer has a failure the vendor frame does not surface. A
skill sits **passive** until something invokes it, and an agent heads-down in the work will not stop to
invoke it. The fix is a **hook** — a timer or event that fires the skill without waiting for a human to
notice. Guidance aims; the hook makes the aiming happen. The failure-modes section returns to this.

## The anatomy every skill shares

<!-- point: progressive-disclosure-is-the-anatomys-load-bearing-property | Progressive disclosure keeps the shared context window honest. | terms: context-window -->
Both kinds wear the same shell. A skill is a directory with one required file and optional bundled
resources.

- **`SKILL.md`** — a Markdown file with two parts. **YAML frontmatter** carries `name` (lowercase letters,
  numbers, hyphens; gerund form reads well — `processing-pdfs`, `writing-documentation`) and `description`
  (third person, what-it-does *and* when-to-use-it, under 1,024 characters). The **body** holds the
  instructions. Keep it under ~500 lines; it competes with conversation history once loaded.
- **Bundled resources** — reference files, examples, datasets, and scripts the body points to. These cost
  nothing until read. A script the agent *runs* costs only its output; a reference the agent *reads* costs
  its tokens, but only when the task needs it. Link every reference directly from `SKILL.md` — one level
  deep — so the agent reads whole files rather than previewing fragments of a nested chain.

Progressive disclosure is the load-bearing property of this shell. The `name` and `description` are the
first level — enough for the agent to decide the skill is relevant. `SKILL.md` is the second. The bundled
files are the third, pulled only on demand. Author for that ladder: put triggering in the description, the
governing shape in the body, and the bulk in resources.

## Two kinds of skill

<!-- point: choose-the-kind-of-skill-before-writing-it | Choosing the kind of skill is the first authoring decision. | terms: mastery-skill, skill-soft-control -->
The choice of kind is the first authoring decision, because it sets everything after it.

> **Tool-skill.** Teaches an *interface* — the calls, flags, and shapes for operating one tool: an MCP
> server, a CLI, an API. Its content is a capability. It takes a paragraph to describe, and the vendor
> checklist covers it end to end.
>
> **Mastery-skill.** Installs a *knowledge-base and the judgment* for doing a task well, independent of any
> single tool. Its content is a way of working. It takes a chapter to walk, because it teaches seeing, not
> calling.

Choose by asking what you are installing. A capability the agent lacks an interface to → tool-skill. A
discipline the agent could technically perform but performs *inconsistently* without your standards →
mastery-skill. This book's three skills are all mastery-skills: none of them wraps a tool; each installs a
craft — hardening the fleet, running it, explaining it.

## Writing a tool-skill

The short path. Follow the vendor guidance directly; there is little to add.

1. **Scope it to one capability.** One tool, one clear job. Resist bundling three tools into one skill —
   split them.
2. **Write the description for discovery.** What it does and when to reach for it, in the user's words and
   the key terms they will type. This is what gets it triggered from a crowded shelf.
3. **Set the degrees of freedom to match the task's fragility.** Fragile and sequential → exact commands,
   "do not modify." Open-ended → direction and a default. Offer one default with an escape hatch, not a menu
   of options.
4. **Push the bulk into references.** API surface, exhaustive examples, large schemas → separate files,
   linked one level deep.
5. **Prefer a script to generated code** for any deterministic, fragile, or repeated operation. It is more
   reliable, costs no context, and cannot drift between runs. Handle errors inside the script rather than
   deferring them back to the agent.

## Writing a mastery-skill

<!-- point: name-the-fundamental-model-before-writing-a-resource | Name the domain's fundamental model before writing a resource. | terms: mastery-skill -->
The long path, and the one this book exists to teach. A mastery-skill is built in three layers, top idea
first, and the order matters: you cannot layer facets onto a model you have not found, and you cannot write
the tying principles before the facets exist.

<!-- figure: assets/skill-recipe.svg | *The Skill Skeleton.* A mastery-skill has three layers: a base model of the domain, orthogonal models cutting it along independent axes, and a SKILL.md of principles that ties them into a working skill. -->

### Step 1 — Find the domain's fundamental model

Name the one abstraction the whole skill reasons through — the first thing you would teach a new hire, the
frame that makes every later rule land. Name it before you write a single resource. If you cannot name it,
you do not yet understand the domain well enough to write the skill, and what you write will be a pile of
tips instead of a way of seeing.

The three self-* skills each turn on such a model:

- **self-communicate reasons through rhetoric.** Good technical writing is a craft with named parts, not a
  matter of taste. Once you see prose as classical figures applied with variety, the register, the lexicon,
  the voice, and the audit all attach to that one frame.
- **self-governance reasons through two kinds of governance.** Every guardrail is either an *architecture*
  that makes a failure impossible by construction or a *sensor* that fires on a violation. That single
  distinction decides, for any failure, what you build.
- **self-operate reasons through the engineering lifecycles.** A fleet repo runs the same few lifecycles —
  the agents, the context, the git repo, the deploy, the machine. Every symptom belongs to one of them, so
  every break routes to a class instead of being met cold.

### Step 2 — Layer orthogonal models on it

Cover the domain with facets, each an independent model in its own resource. Orthogonality is the test: two
facets that overlap are one facet split badly, and a facet you cannot name is a gap in the coverage. Aim for
a set that spans the domain with neither doubles nor holes. This is where progressive disclosure earns its
keep — each facet is a file the agent loads only when the task touches it.

Each self-* skill layers a different set:

- **self-communicate** layers the Diátaxis register (the four doc shapes), a house lexicon, a target voice,
  an audit procedure, and a diagram toolkit — one facet for the doc's shape, one for its vocabulary, one for
  its register, one for its grading, one for the shapes prose cannot carry.
- **self-governance** layers the census of mechanisms, the two enforcement modes (soft aims, hard holds),
  and a set of ambient principles — the catalogue you draw from,
  the axis you place a mechanism on, and the reflexes that run while the skill is loaded.
- **self-operate** layers a symptom-to-doc catalog, a set of typed runbooks, and a runnable hook library —
  the routing table, the procedures it routes to, and the machinery that fires a skipped reflex at its
  moment.

### Step 3 — Write `SKILL.md` as the tying principle

The front matter is not a table of contents that lists the resources. It is the governing principle that
makes the facets cohere, plus the order to apply them. State what all the layers are *for*, then say which
to reach for first. A reader who absorbs the top page should already know how to use the skill; the
resources supply the how.

Each self-* skill's `SKILL.md` carries such a principle:

- **self-communicate** — *less is more*: name the genre, draft in the voice, name concepts from the
  lexicon, draw the shape where there is one, audit before you ship.
- **self-governance** — *convert recurring failures into durable guardrails; guidance aims, machinery
  holds.* That sentence tells you both what to do with a failure and how to weigh the fix.
- **self-operate** — *orient positive first, then route a break to its class.* Know the healthy baseline
  before you hunt, and meet every symptom as a member of a lifecycle.

<!-- table: The mastery-skill recipe across the three worked skills — each step answered for self-communicate, self-governance, and self-operate. [short: The mastery-skill recipe, step by step] -->
| Step | self-communicate | self-governance | self-operate |
|---|---|---|---|
| **1 · Fundamental model** | Rhetoric — prose is a craft with named parts | Two kinds of governance — architecture vs sensor | The engineering lifecycles — agents, context, repo, deploy, machine |
| **2 · Orthogonal facets** | Register, lexicon, voice, audit, diagrams | The mechanism census, soft/hard enforcement, ambient principles | Symptom→doc catalog, typed runbooks, the hook library |
| **3 · Tying principle** | Less is more | Convert failures to guardrails; guidance aims, machinery holds | Orient positive first; route a break to its class |

### What the recipe buys you

<!-- point: a-recipe-built-skill-composes-and-adopts-in-layers | A recipe-built skill composes and adopts in layers. | terms: self-communicate, self-governance, self-operate -->
A mastery-skill built this way gains two properties for free, both from the shape rather than any one
resource.

- **It composes.** Because each skill turns on a clean fundamental model, another skill can cite it by that
  model instead of copying its content. The three self-* skills do exactly this — prose owns the writing the
  other two produce, governance mints the mechanism operations surfaces, operations runs the machinery
  governance designs — so no copy drifts.
- **It adopts in layers.** A reader can take the fundamental model alone and get most of the value, then add
  facets as the need arises. The model without its facets still teaches a way of seeing; a facet without the
  tying principle still solves its slice. You do not have to swallow the skill whole to start.

## When each kind fits

- **Reach for a tool-skill** when the agent needs an interface it does not have: a house CLI, an MCP server,
  a service API. The win is a correct call. Cheap to write, and the vendor checklist is enough.
- **Reach for a mastery-skill** when the agent already *can* do the task but does it *inconsistently*
  against your standards — when you find yourself pasting the same judgment into brief after brief. The win
  is consistent quality. Expensive to write, and worth it only when the task recurs and its quality matters.
- **Some skills are both, and should split.** If you catch a mastery-skill sprouting a tool interface,
  factor the interface into its own tool-skill and let the mastery-skill cite it. One skill, one job.

## Failure modes

The ways skills go wrong, and the fix for each.

- **The description is vague, so the skill never triggers.** "Helps with documents" loses to a rival that
  names the file types and the verbs. Fix: put the concrete triggers — formats, tool names, the words a
  user types — in the description.
- **The `SKILL.md` is a manual, not a method.** Long, exhaustive, and it re-explains what the model already
  knows. Fix: cut every paragraph the model doesn't need, and push the reference bulk into bundled files the
  agent loads on demand.
- **A mastery-skill with no fundamental model.** A pile of tips that never cohere, because Step 1 was
  skipped. Fix: name the one abstraction first; if you cannot, you are not ready to write the skill.
- **Facets that overlap.** Two resources that half-say the same thing, so the agent reads both and gets a
  muddle. Fix: they are one facet split badly — merge them, and re-cut along a genuinely independent axis.
- **The skill is passive and never fires.** A soft control that waits to be invoked, while the agent stays
  heads-down and never invokes it. Fix: pair it with a hook — a timer or event that fires it — so the
  reflection happens without a human noticing the moment.
- **Soft dressed as hard.** Claiming a skill *enforces* something. It cannot; it aims. Fix: if the rule must
  hold regardless of agent cooperation, build the hard mechanism — a lint, a gate, a typed seam — and let
  the skill point at it.
- **The teetering tower.** Enough governance skills and hooks that tending them becomes the work. Fix: this
  is the operator's judgment call, and no mechanism makes it for you — watch for the agent side-questing off
  to polish a guardrail nobody asked for, and stop minting when the tower starts to wobble.

## A checklist

Merge the vendor's checklist with this appendix's additions.

- [ ] Chosen the kind — tool-skill or mastery-skill — before writing.
- [ ] Description is third-person, specific, and names the triggers; under 1,024 characters.
- [ ] `SKILL.md` body under ~500 lines; the bulk lives in bundled files, linked one level deep.
- [ ] Degrees of freedom match the task's fragility (exact steps where fragile, direction where open).
- [ ] Scripts solve rather than defer; no magic constants; forward-slash paths.
- [ ] (Mastery-skill) A named fundamental model, orthogonal facets with no overlaps, and a tying principle
      in `SKILL.md`.
- [ ] If the skill is passive but the reflex must not be skipped, a hook fires it.
- [ ] Nothing claimed as *enforced* that the skill can only *aim*.
- [ ] At least three evaluations from real past tasks; tested across every model you will run it on.
