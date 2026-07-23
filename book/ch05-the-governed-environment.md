<!-- part: 2 -->
<!-- part-title: The Governed Engineering Environment -->
<!-- chapter: 5 -->
<!-- chapter-title: The Governed Environment: Ex-Ante and Ex-Post -->

# Chapter 5 · The Governed Environment: Ex-Ante and Ex-Post

Everything so far assumes you know, in advance, what should be true about your software.
If you do, the path is easy: write it all into a specification up front and hold the
agent to it. But real software engineering rarely works that way — you discover what you
are building by building part of it. So a governed environment has two halves: what you
can decide *before* you start, and what you can only learn *along the way*. This chapter
is about both halves, and about the two forms every governance mechanism finally takes.

## Ex-ante: everything you can decide up front

Some things you genuinely know from the beginning, and you should write every one of
them down. This is specification-driven development, and where you can do it, you should.
A coding style guide is the everyday example — Google has one, Airbnb has one — full of
rules like "every function carries a comment" or "we never call `exec` outside this one
approved place." Give the agent those rules, and then write *deterministic checks* for
them. If a program's output has a required format, write the checker that confirms it —
or, better, have the agent write the checker. Determinizing what you know up front gives
you a much stronger starting point, and it costs you almost nothing, because the checks
are cheap and the agent writes them.

## Ex-post: everything you learn by building

But you will not know everything, and pretending otherwise is the mistake. You will
discover that performance is a problem and you have no performance model. You will
discover that a particular model version has a tic — every LLM's fondness for the
em-dash is the running joke — and that the tics move when you upgrade. So you will build
governance *ex-post*: after the fact, iteratively, strapping on new controls as the
failures reveal themselves and as the software's real properties emerge. You define what
you can up front, and you stay willing to discover the rest — the mistakes you are
making, the mistakes the model is making, the gap between what you thought the customer
wanted and what they did, between how you thought the code would perform and how it did.

The engine of the whole discipline is what you do with those recurring mistakes: **you
convert each one into a mechanism.** This is the organizing move of the companion
catalogue — a failure seen twice becomes a control, so it is enforced on every agent
thereafter instead of re-caught by inspection. A mistake caught in yesterday's manual
audit becomes today's automatic check. There are two forms that conversion can take, and
the difference between them is the difference between a smoke detector and a firewall.

## Controls and architecture

**A control is a sensor.** It detects that a mistake has happened and surfaces it in
time to stop the damage. Your test suite in CI is a control: it would be better if the
model never wrote the bug, but if it does, the control catches it before the code ships.
Controls observe and prevent; they are the sensors wired through the stack.

**Architecture is a wall.** Instead of detecting the mistake, architecture makes the
whole *class* of mistake impossible. The cleanest example is types. Models are, by
default, careless with types — and a compiler exists precisely to confirm that functions
are called with the right arguments. Suppose the agent has represented a state with bare
strings. Because it is a language model, it will cheerfully reach for a synonym next
time, and the synonym silently fails to match. Tell it to use an enumeration instead,
and the whole failure mode evaporates: it can no longer invent an unlisted value, and if
it tries, the compiler rejects it immediately, rather than the test suite crashing much
later. Choosing the enum over the string is not a control that watches for the bug — it
is an architecture that forbids it. This is why the catalogue leans so hard on typed
models and closed enumerations over free-form strings: the wall is cheaper to live
behind than the sensor is to keep reading.

You will place some of each up front, from what you know about the domain, and add more
of both as you go. That combination — determinize what you can, then convert every
recurring surprise into a control or a wall — *is* the governed engineering environment.
