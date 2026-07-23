## The recipe

Three steps build a skill. Each names one thing, and the order matters: you cannot layer facets onto a
model you have not found, and you cannot write the tying principles before the facets exist. Work top to
bottom.

### Step 1 — Identify the domain's fundamental model

Find the one abstraction the whole skill reasons through. It is the first thing you would teach a new
hire — the frame that makes every later rule land, the mental model an expert in the domain already
carries. Name it before you write a resource. If you cannot name it, you do not yet understand the domain
well enough to write the skill, and the resources you write will be a pile of tips instead of a way of
seeing.

The book's three self-* skills each turn on such a model:

- **The prose skill reasons through rhetoric.** Good technical writing is a craft with named parts, not a
  matter of taste. Once you see prose as classical figures applied with variety, the register, the
  lexicon, the voice, and the audit all attach to that one frame.
- **The governance skill reasons through two kinds of governance.** Every guardrail is either an
  *architecture* that makes a failure impossible by construction or a *sensor* that fires on a violation.
  That single distinction decides, for any failure, what you build.
- **The operations skill reasons through the engineering lifecycles.** A fleet repo manages the same few
  lifecycles — the agents, the context, the git repo, the deploy, the machine. Every symptom belongs to
  one of them, so every break routes to a class instead of being met cold.

### Step 2 — Layer orthogonal models on it

Cover the domain with facets, each an independent model in its own resource. Orthogonality is the test:
two facets that overlap are one facet split badly, and a facet you cannot name is a gap in the coverage.
Aim for a set that spans the domain without seams and without doubles.

Each self-* skill layers a different set of facets on its fundamental model:

- **The prose skill** layers the engineering register (the four Diátaxis modes), a house lexicon, a target
  voice, an audit procedure, and a diagram toolkit — one facet for the doc's shape, one for its
  vocabulary, one for its register, one for its grading, one for the shapes prose cannot carry.
- **The governance skill** layers the census of mechanisms, the two enforcement modes (soft aims, hard
  holds), and a set of ambient principles — the catalogue you draw from, the axis you place a mechanism on,
  and the reflexes that run while the skill is loaded.
- **The operations skill** layers a symptom-to-doc catalog, a set of typed runbooks, and a runnable hook
  library — the routing table, the procedures it routes to, and the substrate that fires a skipped reflex
  at its moment.

### Step 3 — Write the top-level SKILL.md as the tying principles

The front matter is not a table of contents that lists the resources. It is the governing principle that
makes the facets cohere, plus the order to apply them. State what all the layers are *for*, then say which
to reach for first. A reader who absorbs the top page should already know how to use the skill; the
resources fill in the how, not the why.

Each self-* skill's SKILL.md carries such a principle:

- **The prose skill** — *less is more*: name the genre, draft in the voice, name concepts from the
  lexicon, draw the shape where there is one, and audit before you ship. The economy stance ties the five
  resources into one craft.
- **The governance skill** — *convert recurring failures into durable guardrails; guidance aims,
  machinery holds*. That sentence tells you both what to do with a failure and how to weigh the fix.
- **The operations skill** — *orient positive first, then route a break to its class*. Know the healthy
  baseline before you hunt, and meet every symptom as a member of a lifecycle.

## The three steps across the three skills

The table reads the recipe down its rows and the three worked skills across its columns. Each cell is that
skill's answer to that step.

| Step | self-communicate | self-governance | self-operations |
|---|---|---|---|
| **1 · Fundamental model** | Rhetoric — prose is a craft with named parts | Two kinds of governance — architecture vs sensor | The engineering lifecycles — agents, context, repo, deploy, machine |
| **2 · Orthogonal facets** | Register (Diátaxis), lexicon, voice, audit, diagrams | The mechanism census, soft/hard enforcement, ambient principles | Symptom→doc catalog, typed runbooks, the hook library |
| **3 · Tying principle** | Less is more — name genre, draft in voice, name concepts, draw the shape, audit | Convert failures to guardrails; guidance aims, machinery holds | Orient positive first; route a break to its class |

## What the recipe buys you

A skill built this way gains two properties for free, both second-order — they come from the shape, not
from any one resource.

- **It composes.** Because each skill turns on a clean fundamental model, another skill can cite it by that
  model instead of duplicating its content. The three self-* skills do exactly this: the prose skill owns
  the writing that the other two produce, governance mints the mechanism that operations surfaces, and
  operations runs the substrate governance designs. Three skills, one substrate, cross-cited — no copy
  drifts because each names the others rather than mirroring them.
- **It adopts in layers.** A reader can take the fundamental model alone and get most of the value, then
  add facets as the need arises. The recipe degrades gracefully: the model without its facets still
  teaches a way of seeing, and a facet without the tying principle still solves its slice. You do not have
  to swallow a skill whole to start using it.
