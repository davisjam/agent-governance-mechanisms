<!-- Provenance: REPAIRED from book/transcripts/Definitions 1.txt (whisper.cpp large-v3-turbo, 5.4 min).
De-noised + aligned to plugin/mage/skills/self-communicate/writing/lexicon.md. whisper
stutters/repeats removed, mis-hearings fixed; the author's exact words, jokes, and meaning PRESERVED —
de-noising, not rewriting. A garbled ~15-word tail (whisper noise as the memo trailed off mid-thought on
"model") was dropped; the "model" definition continues in Definitions 2. The RAW .txt is the source of record. -->

# Definitions 1 — engineering, agent (raw note)

The book needs to define the key terms. I think these terms are **model**, **agent**, and
**engineering** — and, specifically, **software engineering**. We have a standard definition for agent, and
a standard definition for engineering; software engineering is a specialization. I think one distinctive
perspective of the book is that the notion of a *model* is somewhat different between conventional
model-based software engineering and agentic approaches. Maybe it's been discussed in the modeling
literature — I guess it must have been — but perhaps the emphasis is different for this project.

I would say our working definition of **engineering** is a discipline concerned with the development of
solutions to problems amenable to (primarily) technological means — the development of operable
technological artifacts to address those problems. And engineering is also a discipline concerned with the
analytical identification and assessment of competing means of obtaining those solutions, with distinct
trade-offs. If you cannot articulate the trade-offs, then you are not engineering; you are a technician. An
engineer can model and predict the outcomes of the decisions they are going to make — based on the
architectures and designs they propose — *prior* to building them.

There is therefore a distinction between **software development**, which produces a functioning artifact,
and **software engineering**, which predictively *selects* a software artifact according to desired
properties. So much for engineering and software engineering, the discipline that does that.

Next we have to consider **agents**. This is not a book about human management, and therefore we must
identify a specific actor intended to be undertaking the implementation work and participating in the
design. An agent is a **controllable intelligence capable of independent reasoning** over a knowledge base.
There are many interesting aspects to this definition.

First, *intelligence*. This is outside the scope of the book, of course, but a working definition might be
that it can, given a set of constraints and a goal, devise a means of satisfying the goal without violating
the constraints. You might think of a raven placing pebbles into a jar to raise the water level high enough
that it can drink. The goal: get a drink. The constraint: the beak is too big to reach the bottom of the
cup. The means: some pebbles. And thus we have a raven Archimedes. Eureka.

Then, *controllable*. So we have an intelligence — it needs to be controllable. Controllable means that you
can change its environment and the knowledge available to it, and it will do different things, and it will
generally follow orders. Controllable is maybe a different word from *controlled*: controlled means you
have perfect guarantees of its behavior; controllable means you have *probabilistic* guarantees of its
behavior.

[memo trails off here beginning the definition of **model** — continued in Definitions 2.]
