<!-- part: 2 -->
<!-- part-title: The Governed Engineering Environment -->
<!-- chapter: 7 -->
<!-- chapter-title: Lifecycles and Runbooks -->

# Chapter 7 · Lifecycles and Runbooks

You know what to do when the disk fills up, when two branches conflict, when an incident
pages you at 2 a.m. You know it so well you barely notice you know it. The agent knows
none of it. It has no operating context and no sense of "how we do things around here,"
and so a governed environment for real work has to write that knowledge down — as
lifecycles and as the runbooks that ride on top of them. This chapter is about capturing
the operational judgment you carry in your head so an agent can act on it.

## Lifecycles first, then the failure map

Start with the lifecycles, because everything else hangs off them. A lifecycle is the
correct operation of one recurring activity: how a bug report moves from filed to fixed,
how a feature moves from design to shipped. Write the healthy path first. Then, from each
node on that path, map the failure states — the ways this step can go wrong — and for
each failure, the action to take. Think of it as a grid: every node crossed with every
symptom, and in each cell, what to do.

The formal name for building that grid is **failure mode and effects analysis**. You
enumerate what can go wrong, then the consequence of each, and then — the part people
skip — how to get *out* of it again. You know how to get out. If two branches conflict,
you read both sides, work out what each was trying to accomplish, and reconcile them. If
the disk fills, you find the fat part of the system — the cache, usually — and wipe it.
The agent knows none of this. It does not know where to find each commit's intent during
a merge conflict, and it does not know where your system's fat points are — and it may,
just maybe, decide the fix for a full disk is `rm -rf /`. You think I am joking. Read
Twitter; agents do it all the time. So you coach it: where the hot points are, and, in
every failure path, what is *not allowed*. Encode the prohibition as a control at the
right level where you can — a Git hook, an agent hook — and where you cannot, at least
tell the agent plainly.

> *A footnote on the pink elephant.* Telling an agent not to do something raises an
> honest question: does naming the forbidden act make it more likely? A human cannot help
> picturing a pink elephant once told not to — though without the telling, the thought
> would never have come. The apostle Paul said the law taught him what sin was, and that
> without the law he would not have known. It is genuinely useful to name the sin. It is
> also true you may never have considered an act until someone forbade it. Worth holding
> in mind; then back to the SOPs.

## Runbooks: split the deterministic from the judgment

Once the healthy path and the failure map are written, the thing you hand the agent is a
**runbook** (or playbook): the steps to take, whether recovering from a failure or
working a fresh ticket. The one discipline that makes a runbook work is to split it into
two kinds of step, because they are governed completely differently.

**The deterministic parts get tools.** Anything that has a single correct outcome should
be an executable script the agent runs, not a procedure it improvises. Leave it to
improvisation and it will get it right most of the time — and you will wish you had
automated it the one time it does not.

**The judgment parts get the roughest algorithm that still fits.** For a well-constrained
decision, write the algorithm down and let the agent do the glue. For an open-ended one —
a cyber threat hunt, where the whole point is that the attacker did something you never
anticipated — do not over-constrain: give heuristics and strategies to explore, and stop
there. Remember you are conditioning a probability distribution; steer it down the wrong
path and it will never reach the place you wanted. So if you do not know how to do it,
do not write confidently — give hints. If you truly do not know, say "solve this
open-endedly," and accept that the looser the guidance, the more tokens it spends and the
less likely it is to land.

When a judgment step is really a *measurement*, give it a **rubric**. You cannot write a
checker for "is this painting good" or "is this student essay good," but you can
operationalize it: how are the topic sentences, how is the technique, are there
grammatical errors, are there blotches from bad storage? The agent will not deliver a
final verdict on taste, but with a rubric it gives feedback good enough to act on.

The strongest form of this is the **pre-canned brief**. When an orchestrator agent has to
hand work to a sub-agent, you do not want it inventing, each time, how to explain the
task. You want a template it adapts — the work already articulated in writing. The
companion repository leans on exactly this: every dispatch is composed from a template
that pre-places the required instructions, and a brief-linter checks the template is
intact before the agent launches. Templates constrain how work is described to agents,
which is the whole business of this book, applied to the act of delegation itself.
