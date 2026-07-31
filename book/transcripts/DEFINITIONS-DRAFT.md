# Definitions — green-box drafts (from the "Definitions 1/2" + "Controllability" notes)

Integration draft for the book's core-term definitions, in the **green definition-box + per-aspect
elaboration** shape the author asked for. Each term gets a short **box** (the concise definition) followed by
**elaboration prose on each adjective/aspect** — most of which the author verbalized in the audio notes.

**Two follow-ups gate the final landing (not blockers for drafting):**
1. **Renderer feature — the green definition box.** Proposed directive `<!-- def: <term> -->` heading a
   blockquote → `<aside class="definition-box">` with green accent (a sibling of the concept-inset box).
   It needs `build_book_html.py`, currently owned by the C→A IR migration; it drops in as ONE directive-
   registry row + a CSS rule once that lands. Spec it there.
2. **Chapter home.** The author's audio says these belong "in the definitions, in Part 2" (and some framing
   early in Part 1). Likely a new **"Definitions" section** early in Part 2 (or a Part-1 §), cross-linked
   from the lexicon and the concept-model (`book/data/concepts.json`).

---

## Engineering

> 🟢 **Engineering** — the discipline of developing operable technological artifacts to solve problems,
> *and* of analytically identifying and assessing the competing means to those solutions, each with distinct
> trade-offs.

**On "develops operable artifacts."** Engineering produces something that *works* — a technological artifact,
with human operators, that addresses a real problem.

**On "analytical assessment of competing means / trade-offs."** This is the part that separates the engineer
from the technician: *if you cannot articulate the trade-offs, you are not engineering — you are a
technician.* An engineer weighs competing architectures and designs against desired properties.

**On "predictive."** An engineer can **model and predict** the outcomes of the decisions they are about to
make — from the architecture and design they propose — *prior to building.* Prediction-before-construction is
the engineering move.

## Software engineering

> 🟢 **Software development** produces a functioning artifact. **Software engineering** *predictively selects*
> a software artifact according to its desired properties.

**On the development-vs-engineering distinction.** Development asks "does it function and meet requirements?"
Engineering asks "of the artifacts that would function, which one should we build, given the properties we
want?" — and answers *before* building it. (This is why the book is about software *engineering*, not
software development.)

## Agent

> 🟢 **Agent** — a **controllable intelligence capable of independent reasoning** over a knowledge base.

**On "intelligence."** Out of scope to define fully, but a working sense: given a set of **constraints** and a
**goal**, it can devise a *means* of satisfying the goal without violating the constraints. Picture a raven
dropping pebbles into a jar to raise the water high enough to drink — goal: a drink; constraint: the beak
can't reach the bottom; means: pebbles. A raven Archimedes. *Eureka.*

**On "controllable" (not *controlled*).** You can change its environment and the knowledge available to it,
and it will do different things, and it will generally follow orders. **Controllable ≠ controlled:**
*controlled* means **perfect** guarantees of behavior; *controllable* means **probabilistic** guarantees.
This one adjective is why **governance is a major part of this book** — if agents were *controlled*, we would
not need governance at all.

**On "independent reasoning."** It genuinely reasons in response to a query — it is not merely retrieving or
pattern-matching stored answers.

**On "over a knowledge base."** The thing it reasons *over*. For this book, the **models are that knowledge
base** — which is what ties the agent definition to the model definition.

## Model

> 🟢 **Model** — a description that approximates a phenomenon usefully enough to make **predictions** about it.

**On "approximation."** Imperfect but useful. *f = ma* neglects friction, and is nevertheless useful. Models
come in kinds: **mathematical** (a quantitative variable relationship), **qualitative** (this goes up, that
goes up — strength unknown; supply and demand), **relational** (every one of these comes with two of those),
and **data-flow** (the transformations applied to data as it moves through a system).

**On "useful" — in the eye of the application.** To know roughly what a system does, "it processes
information serially" may suffice; to reason about **security or privacy**, you need a far higher-fidelity
model, one much closer to the real system.

**On "fidelity."** Closeness to the thing signified. As fidelity rises the model's utility rises; pushed high
enough, the model *becomes* the thing signified (for good or ill). And a coarser model is **cheaper to
analyze** but yields **error bars** around the analysis — the fidelity/cost trade-off.

**On "implies constraints."** A model is not just descriptive — it **constrains**. A system built on a model
cannot take *any* form; it must take roughly the form the model describes. It may **elaborate** on the model,
but it cannot **diverge** from it. This is the hinge to the agent: the model an agent is given serves as both
a **constraint** (bounding what it may build) and a **blueprint** (telling it what to build) — and, because
agents reason over knowledge bases, the model *is* the knowledge base for the artifact under construction.

---

*The relationship between the four is "the whole book in a nutshell" (the author's phrase): engineers love
models because they can assess trade-offs without excess cost; agents are controllable reasoners; and a model
handed to an agent is at once its constraint, its blueprint, and its knowledge base — so the book's job is to
describe the models useful to agents, show how agents interact with them, keep them consistent with the
artifact as it is built, and teach engineers to construct/assess/use them to predict before building.*
