<!-- part: 1 -->
<!-- part-title: The Mindset -->
<!-- chapter: 2 -->
<!-- chapter-title: Loops and Models -->

# Chapter 2 · Loops and Models

Two ideas carry the rest of this book, and everything else is a consequence of them.
The first is that all agent work is a *loop*. The second is that an agent steers that
loop well only when you hand it a *model* of the world it is working in. Get these two
right and the agent finds your answer fast; get them wrong and it wanders. Let me take
them in turn.

## Everything is a loop

An agent does not run in a straight line — it runs in a loop, and the loop has a fixed
shape. It takes an input: the current problem, plus some notion of what success looks
like. It reasons, and it acts in its operating environment. It produces a result. And
that result folds back into the input for the next turn. Input, reasoning, output,
fed around again. I call the practice of shaping that loop **loop engineering**, and
nearly everything in this book is an instance of it.

Engineering a loop well starts with the metric, because the metric is what the agent
steers by. The agent does not magically know your goals or your environment. You have
to make its progress *measurable* — deterministically, through a quantitative check,
or through a rubric that scores a qualitative result. Skip this, and you have told the
agent nothing about what "done" means, so it searches, and searches, and searches, and
never knows when to stop.

The orchestration layer of this book's companion repository is itself a worked example
of a loop engineered this way. The catalogue models the orchestrator — the process
that dispatches agents, waits for them to land work, and cleans up after them — as an
explicit reactive loop with a typed lifecycle: *dispatch → work → land → tombstone*,
then refill and go again. The loop is not left implicit in the code; it is written
down as a model the agent can read, which is exactly the second idea.

## Give it a model of the world

The second piece is the input the agent reasons *over*. You have to give it a sense of
the environment: when it pulls this lever, what happens, and what is it even allowed to
do? That sense of the world is itself an input, and when you supply it, the agent knows
what kind of reasoning the situation calls for.

It is worth being blunt about why this works, because it is easy to feel like you are
writing documentation into a void. A foundation model is, very loosely, a probabilistic
reasoning machine. *Probabilistic* means it does not always do exactly what you want.
*Reasoning machine* means it genuinely reasons — the interpretability work probing
world-models inside these networks settled that question — so writing the model down is
not wasted breath. It reads it, and it reasons over it.

The most useful way to hold this is as a search. The agent is searching an enormous
space: every place the answer might live, every configuration it might try, every
function that might implement what you asked. That space is far too large to sweep. So
when you structure the loop and hand over a model, what you are really doing is
**conditioning the probability distribution of the agent's behavior** — biasing it to
search where the answer actually is. Done well, this can take the agent from failing
your task to completing it. And when it was already completing the task, it now does so
in fewer tokens and less time, so you get back to the interesting parts of your job.

[FILL IN: the metaphor seam. A real 3D printer is deterministic; this one is
probabilistic. Say so explicitly, once — it is *because* the agent is a probabilistic
search that we condition it rather than merely instruct it. Naming the tension keeps a
sharp reader from feeling the metaphor and the thesis pull apart.]
