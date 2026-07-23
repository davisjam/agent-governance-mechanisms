<!-- part: 2 -->
<!-- part-title: The Governed Engineering Environment -->
<!-- chapter: 4 -->
<!-- chapter-title: Models and the Semantic Gap -->

# Chapter 4 · Models and the Semantic Gap

The last chapter gave you four places to inject control. This one is about the single
most valuable thing you can put there — a *model* — and about a trap that catches
people the moment they try to enforce one: pushing on the model at the wrong level, and
watching it slip. Models are the sweet spot between prose that is too vague and code
that is too verbose. But a model only helps if you check it where checking makes sense.

## Words are soft, code is verbose, a model is the sweet spot

Your first instrument of control is the prompt, because the agent is a language model
and words are how you talk to it. But words are soft. They are ambiguous, and the more
ambiguity you leave in, the less happy you will be. You can push ambiguity down by
writing documentation — describing the environment, the product, its goals, its
policies — and if you were briefing a *human* team, that would be enough. Humans are not
dumb; they remember, they know what matters, they know where to look it up, and they
know they will be fired if they misbehave. Agents are different: brilliant reasoners
who need to be told exactly what to reason over, and for whom loose documents are simply
not precise enough.

Code is the opposite failure. Code is perfectly precise — it is exactly what will
happen — but it is far too verbose to reason over in bulk. What you want sits between
the two: something accurate and unambiguous, yet compact. The word for that thing is a
**model**.

You already know models from physics. *F = ma*. *y = mx + b*. They are not reality —
*F* does not quite equal *ma*, and real data scatters around the line — but they are a
cheap, honest approximation you can actually reason over, instead of wrestling the full
empirical dataset or a nightmare of fluid equations. A circle approximated by tangents
is not a circle, but it is good enough to compute with. Software has its own such
models. UML was the famous attempt: a whole language of them, out of the 1990s,
expected to be the future. It never took off, and the reason is the reason this whole
chapter exists.

## Why the models drifted — and why that changes now

The models are the map; the code is the territory. You draw the map, you build the
territory from it — and then the territory *drifts*. Code changes constantly, and
keeping the map in sync is expensive. Worse, no single model captures everything, so
teams either piled every concern into one unreadable mega-model, or split them into so
many views that a single code change meant updating ten diagrams. So people gave up and
drew box diagrams instead. Only the industries where a mistake is catastrophic —
Rolls-Royce, Boeing — kept their models honest, because they could justify the cost.
Everyone else chose agility and leaned on the code.

Agents flip this calculation, because agents cannot reason over the code — there is too
much of it — but they *can* reason over models. So if you can find the models that
usefully approximate your system and keep them in sync, your agents will always know
where to go. They walk the docs, hit a pointer to the model — a data-flow diagram, a
performance model, an inheritance hierarchy, a user journey — and if that model is
linked to the relevant code, they can make the change with the whole picture held in a
single window. The model also lets them *check their work*: a test says the suite
passed, but an invariant over a model says what must be true beyond the tests. This is
how you stop architecture from decaying — the agent finds the architectural model,
follows it, verifies against it, and when the territory genuinely moves, retrofits the
map so the two stay equal. The companion catalogue's **drift-and-parity gates** are the
mechanism that makes "the map equals the territory" a checked property rather than a
hope: they fail the build the moment a model and the code it describes disagree.

## The semantic gap

Now the trap. Say you want to enforce "if the agent substantially changed the call
graph but did not update the overlaid model, reject it." It sounds like a pre-commit
hook. It is not — and seeing why is worth more than the rule itself. An agent carrying
out a real task makes *many* commits toward one goal; the model may be legitimately out
of sync in the middle and correct again by the end. Enforce at the commit and you are
checking a sentence for grammar before the paragraph is written.

This is the **semantic gap**: the failure you get whenever you enforce a property at the
wrong level of abstraction. Operating-system security lives with it constantly — the OS
sees individual system calls, but "this program is exfiltrating data" is a *pattern
across* calls, invisible in any single one; you have to stitch ten network calls
together before the leak is legible. Model drift is the same shape. The commit is the
wrong granularity.

The fix is to find the level where the property is actually legible, and enforce there.
For model drift, that level is the *agent returning from its task*, because at that
moment the entire feature and its plan are visible. You can see whether the work changed
the model, and whether the body of commits includes the tests, the documentation, and
everything else the task was supposed to carry. This is exactly where the companion
repository places its definition-of-done audit: a check that runs when an agent
finishes an Epic, over the whole unit of work, rather than at any single commit inside
it. "Correct" is a hard word — you cannot fully prove the model is right — but you *can*
check that it was updated and that the surrounding work is complete, and that is the
right semantic level to do it.

[FILL IN: cash the promissory note this chapter opens. A "special language" for
invariants over models was promised — deliver a taste of it: a property-based test, an
invariant written over a model, and a first look at where a model checker (BMC, a
temporal-logic checker) earns its keep. This is the reader's biggest unanswered
question after this chapter.]

[MORE CHAPTERS FOLLOW: a dedicated chapter on how you actually *author* a model in a
repo — is it a typed record, a diagram, a lint, a schema file? The reader now believes
models matter but cannot yet build one.]
