<!-- part: 3 -->
<!-- part-title: Putting It to Work -->
<!-- chapter: 9 -->
<!-- chapter-title: The Skills -->

# Chapter 9 · The Skills

This book is not only a methodology — it ships with batteries. There is a repository
that goes with it, and it contains three Claude skills you can install and use today:
**self-operate**, **self-governance**, and **self-communicate**. Each is the methodology
of the preceding chapters, packaged as something an agent triggers and follows. This
chapter walks all three.

## Self-operate: the lifecycles, made runnable

Self-operate is the starting point, because it holds the lifecycles of running a repo —
everything an engineering team actually does. Pull a ticket and build a feature. Pull a
ticket and fix a bug. Optimize the codebase. Handle resource exhaustion. Each of those is
written down as a model — I did say models everywhere, and I meant it — because that is how
you constrain the agent's search and bias it toward doing the work the way you want.

On top of the models sit the playbooks, and there is a playbook for everything, each with
briefs for its judgment steps. This is what lets an orchestrator agent — itself running as a
reactive loop — know how to respond when an event arrives. An agent finished? Reach for the
next step: *agent landed*. Is the feature done? Open the Epic file, which lists the launches
needed to complete it, and check. Not done — launch the next item. Done — run the
definition-of-done audit over the whole Epic, the one that asks, among other things, whether
the model drifted from the code. Passes — mark it done and move it to the closed pile.
Still active — record the status and the commit that made progress, and launch the next
agent from the Epic's list. The playbook keeps the loop turning on inputs from the
environment, which is precisely the *dispatch → work → land → tombstone* lifecycle from
Chapter 2, now written down for the operator to run.

## Self-governance: the catalogue and the posture

The second skill, self-governance, triggers on a simple signal: a bad thing happened more
than once — sometimes just once, if it was bad enough. Recurrence is the clue that you are
either failing to *detect* the problem (you need a control, a sensor) or failing to *prevent*
it (you need architecture, a wall). You have not put the wall in the right spot, or you have
not put a badge reader on the door.

At its center is a catalogue of governance mechanisms and worked examples — around sixty-six
at last count, and still growing as new failures surface new mechanisms. I did not know these
were the controls I would need until I started building and kept hitting failures; as velocity
rose, more failures and new *kinds* of failure appeared, and each mechanism I invented to kill
one went into the catalogue. The hope is that this becomes ex-ante governance for *you*: the
mistakes I made and solved, you inherit for free — install it and say "audit my codebase and
help me find room for governance." But you will find your own failures too, because you run a
different model, different constraints, different customers, different operators, and all of it
shapes your agent's behavior. So the skill ships not just the catalogue but a **posture** — the
heuristics for minting new mechanisms well.

The first heuristic is to **avoid a teetering tower of governance.** Ask how detailed the check
should really be. Is this generic or specific — do you need a lint for "never type the word X"?
Almost certainly the wrong level, but a lint that blocks typing anything is worse. Decide
whether false positives or false negatives hurt you more, because that governs which control
fits. And when you say "this must *never* happen," you are choosing architecture — a wall — and
every wall constrains the model. A well-placed wall is pure gain. A wall across the only fire
exit is a disaster the day there is a fire and no one can get to work. Because of this, the
skill will not silently enforce a mechanism without checking with you — you are the engineer who
knows the context. Its own trigger is a control at the right semantic level: a hook that fires
every thirty minutes or so in the orchestrator loop and asks, "since I last checked, did we hit
any recurring failure, or solve one problem several different ways?" Solving it several ways is a
don't-repeat-yourself smell in the code; hitting the same *process* wall repeatedly — "I failed
to create a VM," again — is a process smell. At agentic velocity you cover enormous ground in
thirty minutes, so a repeat inside that window is the signal that a mechanism is owed.

## Self-communicate: how the agent writes and draws

The third skill, self-communicate, governs how the agent explains itself — to you and to other
people. Docs are a soft control for an agent, but they are a genuine tool for humans, so the
skill carries guidance on the kinds of technical documentation, crediting the Diátaxis project
for enumerating them and the Apache Foundation for the exemplars it learns style and voice from.
It targets prose that avoids imprecise claims and the grating verbal tics, and that is as terse
as it can be without losing the reader. When the agent writes, it turns here; when it needs a
drawing, the skill says "use me," and teaches drawing in Mermaid — dropping to HTML or SVG only
when Mermaid cannot express the shape — which keeps the agent from trying to hand-generate raw
PNGs, a thing it will attempt and be bad at.

Self-communicate also owns a **lexicon**: the house vocabulary for your repo, so one concept gets
one word, used consistently. You can bootstrap it — point the skill at existing material and have
it walk the repository, surface the terms you use with specific meaning, and write down the
working definitions. That walk tends to catch two failures at once: different words for the same
concept, and the same word for different concepts. Both confuse any reader, human or agent, and
finding them may show you mistakes in your own thinking. "There are actually two concepts here —
help me name them." Now they have names, and you can retrofit structure onto the writing — which
is, exactly, the code problem from Chapter 8, wearing different clothes. Those are the three
skills that ship with the book. I hope they are of use.

[MORE CHAPTERS FOLLOW: the team dimension. Everything here is written as "you and your agents,"
but production software is built by teams. How do shared models become team artifacts rather than
one person's? How does review work when an agent wrote the change, and who owns the model when it
drifts? This is the chapter an O'Reilly production-software audience will look for.]
