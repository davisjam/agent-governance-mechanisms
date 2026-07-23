<!-- part: 3 -->
<!-- part-title: Putting It to Work -->
<!-- chapter: 11 -->
<!-- chapter-title: Training Data and the Novelty Axis -->

# Chapter 11 · Training Data and the Novelty Axis

There is one last property of a coding agent you have to reason about, and it decides how much
of this book you will actually need: its training data. Everything in these chapters is about
conditioning a probability distribution — telling the agent the path through its search space.
But that distribution did not start neutral. It was shaped by what the model was trained on, and
that shape determines where the discipline is optional and where it is the only thing that will
save you. This chapter is about that axis, from the common case to the hard one.

## The model is biased toward what it has seen

Treat the training data as the whole internet and every book ever written, and treat the model as
biased toward whatever it saw a lot of. Read one book with one position and a hundred with the
opposite, and it leans to the hundred. Except where trainers worked hard to force a particular
behavior, it simply weights the common over the rare. This has a moral dimension the labs fight
with reinforcement learning from human feedback — you teach it not to lie, and they lie anyway;
not to steal, and they steal; not to break into other people's computers, and they will, given
the chance. Training data has its limits. But the same bias has an engineering consequence that
is more useful to us: the kinds of systems the model has seen a great deal of, it can build a
variation on almost effortlessly; the kinds it has never seen, it struggles with.

That divides the world of software neatly. If you are building your own version of something
standard, the model has read the documentation and watched the walkthroughs of a hundred
competing products and can reproduce the class in its sleep. (One caution: building a competitor
this way can infringe a *patent* even though you copied no *code* — a patent covers the concept,
not the text — so tread carefully.) A to-do list, a recipe tracker, a fitness app — GitHub holds
a million of each, and the agent knows them cold. Any "typical web application" — a form-driven
UI, a backend storing to a database, a compute layer producing outputs over it — it can build
without breaking a sweat, because you are asking it to regurgitate a class it has seen a thousand
times and then specialize it. This is exactly why a lab can credibly claim it built a whole C
compiler in a week, or ported one runtime to another language in three days: the training data is
full of compilers, and in the porting case, full of the very code being ported. Impressive, and
entirely unsurprising.

## Where MBSE shines: the novelty axis

The other half of the world is where this book earns its keep. Build a genuinely new kind of
application — a new class of software, something hard nobody has done, or a research setting like
high-performance computing — and the bias runs *against* you. There is very little open-source HPC
code. The model has read the OpenMP, Open MPI, and CUDA docs and seen a pile of ML kernels, but it
has not seen your climate simulation unless your organization open-sourced it, and even then it is
a drop in an ocean of everything else. So the foundation model is biased *away* from the code you
need. Left alone, it will map the architecture it *does* know onto your problem and make the wrong
choices — the right moves for the wrong class of software.

This is precisely where model-based software engineering shines: the model lacks the bias you
need, so it is your job to impose that bias and state it explicitly. And you can, because code is
cheap — you just have to tell the agent to do it, with the full rigor of the earlier chapters. The
companion catalogue's whole models-bridge exists for this: it is the substrate through which you
hand the agent the priors its training never gave it, so the invariants you care about are written
down where it will read them instead of guessed at from the wrong reference class. On a standard
class of software you still model, but you can lean on the model's built-in bias; on a novel one,
the up-front modeling is not optional, and you coach the agent step by step.

I hold this through an analogy to the diffusion models that draw pictures. Ask one for an exact
copy of a famous painting and it delivers, because it has seen that painting endlessly. Ask it for
a scene no one has ever painted — a genuinely new combination, or just a complicated one — and it
struggles, because it is working from pictures of reality rather than reality itself. The labs have
pushed these models to reason one step deeper than the prompt — enough to know a hand has five
fingers, so we stop getting humans with seventeen — but they always run up against the gap between
what they have seen of the world and how the world actually is. Engineering a system is the same.
A system it has seen a thousand times, like Starry Night, it builds without trouble. A novel system
for your startup — whose entire point is to be a new thing that does not yet exist — it has not
seen, and cannot. Say "draw an alien" and it invents seventeen fingers and two heads, because no
one knows what an alien looks like, so there is no reality to map to.

So think of it this way: the agent will hand you a working prototype, but look under the hood of a
novel system and you find a Rube Goldberg machine of hilarious extent. It runs — and a skilled
engineer is still needed to turn that crude, working prototype into something reliable across the
full breadth of inputs and quality attributes you care about. For the standard parts, the model has
seen the engine room and gets the internals right; for the novel parts, or the ones shaped by
context it never trained on — a powerful but obscure library used commercially rather than in the
open — it can read the library but has never watched anyone use it well, so it fabricates something
that passes your examples and fails in general. The engine room of a vibe-coded novel system is not
correct. It is demoable; it is not productizable — not yet, not without an engineer. That is the
job. The more standard the part, the bigger the leap you can trust and the more code you can let the
agent produce unattended. The more obscure, sensitive, or context-bound the part, the more oversight
you give, the shorter the reasoning you allow between checks, and the more you condition the
distribution yourself — narrowing the search by hand, with model-based software engineering.

[MORE CHAPTERS FOLLOW: governing an untrusted agent. This chapter notes in passing that agents lie,
steal, and break into machines given the chance, and that a hook can block a network call — but the
security thread deserves its own treatment: prompt injection, exfiltration through the very tools you
granted, and supply-chain exposure. Consolidate it rather than leaving it scattered.]
