# 3D Printing Production Software — dictated manuscript (cleaned)

*Lightly-cleaned assembly of the 12 dictation clips, in order. The raw
`NN-X-transcript.txt` files (verbatim Whisper output) are preserved alongside;
re-runnable from the `.m4a` source any time. Cleaning applied: removed the car-GPS
navigation interjections that bled into the audio, collapsed ASR stutter-repeats,
and fixed predictable mishears (Kruchten, Diátaxis, provenance, invariants, Claude
/ Claude Code, governed engineering environment, ex-ante, Ruff/Pylint/ESLint,
em-dash, fingers, PNGs, bill-of-materials). The author's wording, phrasing, jokes,
and digressions are kept intact — this is de-noised, not rewritten. ~17,220 words.*

---

## 1 — The printer (metaphor)

The entire book is driven by the metaphor of a 3D printer. A 3D printer is a
machine that allows you to produce arbitrary products, so long as they can be
created using the filaments — or whatever materials you print with. What's magic
about a 3D printer is that it is unbounded, except by your own creativity. There
are the limits of the filament, of this engineering substrate you're working with,
of course — but beyond that, the only thing that keeps you from building stuff is
your own ability to imagine it, and to imagine how to create it.

Now, this is the key part: to engineer software with a 3D printer, with a model.
Everybody can imagine a software thing. Software we're all familiar with — taking
in data and doing something with it. And we've seen all these magic demos: Google
Maps, Google Docs, spreadsheets, all these things we use to manipulate data in our
everyday lives. We can all sketch the concept. But, like a 3D printer, just
sketching the concept is not really enough. You also need a way to explain how to
create it.

If you have a 3D printer and you give it a picture of what you want to make, this
will not be enough to make the thing you're trying to produce. You also need to
provide instructions. These instructions are the CAD model that shows not just the
picture but the internal structure — how the pieces fit together. And then you also
have notes about how you're supposed to print the thing. So realizing it, reifying
it, requires also separate instructions about how to go about printing it. You
typically slice it into layers, and then you need to think about how the layers
compose, and what's going to happen as it prints. Different materials you're
printing with have different minimum thicknesses; they have different strengths;
they can be fit together in certain joints and not other joints. There are all
these different ways that you can misdo the work.

As you work with agents to do software development, you cannot only give them the
picture. You must also give them — or figure out how to give them — the detailed
instructions on how to make it work. Good instructions, it works great. Bad
instructions, not a hope in the world.

Now, if you use a stapler and the staple doesn't staple, it's really the staple's
fault. It's not your fault. But when you're working with software agents, because
it's more like a 3D printer, if it doesn't work — perhaps it's your fault. This
book is about teaching you how to get the most out of the agents that you work
with. And in my experience, every single time the agent has not produced what I
want, it was always my fault. The state-of-the-art models are capable of building
anything we can envision with software, as far as I can tell, so long as you can
figure out how to explain it to them. This book will teach you how to do that.

---

## 2 — Loops and models

The core premise of this book requires you to understand two distinct things.

The first thing is that all agent work can be understood as a loop. There are
inputs to the loop. There are actions that the agent takes based on that input in
its operating environment. It produces results. And then those results feed back
into the next round of the agent's work as part of the input. So the input is
success metrics and the current problem; it does reasoning; and then it produces
the next round of outputs. Everything that we're talking about can be thought of in
terms of that concept. It's called **loop engineering**.

To engineer loops well, you need to figure out what metrics to provide. The agent
does not magically know about your operating environment, your goals, etc. You need
to figure out how to make its progress deterministic — via quantitative results —
or measurable, via rubrics over qualitative results. If you don't tell it what
success looks like, it does not know, and it will just search and search and
search.

You also need to figure out how to articulate those inputs — the results of its
previous run. So this is the second piece. You need to give it a model of the
world. And that's in a broad sense — I don't mean a "world model." But you need to
give it a sense of the operating environment it's working in: when it pulls which
lever, what happens? And what is it allowed to do as it operates? These can be
understood as an input. And if you provide it with models, it will be able to know
what kind of reasoning it ought to perform. Period.

*Footnote.* Of course, as of 2022, these things were not reasoning. But the
model-probe, Othello-type work has shown us very clearly that these models do
reason. So don't think that you're going crazy and wasting your time writing
documentation. It does read it, and it does reason. *End of footnote.*

Okay, so those are the two pieces. You need to think about it as a loop, and you
need to think about the models that it's working with. Now, why do we need to do
this? Well, we need to understand how the foundation model works. And very loosely,
it is a probabilistic reasoning machine. Probabilistic reasoning machines can
reason — great. And they're probabilistic, meaning that they don't necessarily do
exactly what you want. They can also be understood as searching over an extremely
large search space for the solution to the task that you set them.

So when you structure your loop — when you give it models — what you're doing is
you are conditioning the probability distribution of its behavior, such that it
will be more likely to search in the space that you're interested in. I like to
think of it as the set of all possible places we can look for the answer; the set
of all possible configuration parameters we can try; the set of all possible
functions that implement the desired functionality. That's a big set, right? Well,
within that search space, where should we look? And the way you structure your
loops, and the way you structure your governed engineering environment, profoundly
impacts how effective the model is at completing the tasks. It may take it from
being unable to complete them to completing them. And if it is already completing
your tasks, it will make it so much faster. It will use fewer tokens and complete
the work more quickly, so you can get back to doing the interesting parts of your
job.

---

## 3 — The agent stack and conditioning

Now, the next thing we need to understand is what opportunity we have to govern the
model's behavior. You should understand the model stack as having four parts.

**First, the foundation model at the bottom of the stack.** This is typically given
to us by either a commercial model vendor — think OpenAI or Anthropic — or by an
open-weight model that we've downloaded off the internet (thank you, people who do
that). These models can be conditioned. They are general language manipulators and
reasoners, and they can induce an understanding of the operating environment. But
that induction is very costly. So what we want to do over and over again is
eliminate their need to perform reasoning — by telling them either deterministically
through actual executable programs, or through soft modes of governance: written-down
pseudocode for the algorithm it's supposed to follow, the playbook for root-cause
analysis, or a hybrid. We want to repeatedly tell them exactly where to look, and
this will allow them to make progress. So that's how we control the base model.

**Now on top of that is an agentic harness** — think Claude Code, OpenCode. These
sit on top of the model; they take our prompts and feed them to the model. And they
are in charge of managing a couple of things. One thing they manage is the language
model's context window — how many tokens it's getting fed. It's a fixed amount of
tokens, based on your hardware and the model's capacity. And if you exceed that, the
harness needs to figure out how to compact it, so it retains some sense of what's
been going on. But of course, it's a lossy compression.

That agentic coding harness has places where we can plug in controls. One place is
called a **skill**. A skill is a soft control. It has criteria that trigger its
operating behavior. For example: if you are going to interact with a PDF, call this
skill. And when you interact with the PDF, the agentic harness realizes we're about
to interact with the PDF; it enters the skill; the skill has text descriptions of
what you should do to do things on a PDF. These text descriptions may be entirely
prompts — like "be very careful manipulating PDFs" — or they may be a mix of prompts
and code. There may be a library that you can call, or a command-line interface.
These are called **tools**. And these tools allow the model to deterministically
take actions — like add a page or delete a page from the PDF, modify words, whatever
you want. It's a way to programmatically interact with them. So those are skills.

The other thing the agentic harness gives us is called **hooks**. As the harness
interacts with the model — doing things like passing along a prompt, or preparing to
dispatch an agent, or exercising another skill, or interacting with a tool — before
and after those actions, you can execute a deterministic program. And that
deterministic program can say: *don't do that.* And it can authoritatively say,
you're not allowed to take this action. For example, it might look at a network I/O
and say, that's not allowed. Or, I'm about to send an email via a tool — don't send
that email, it's got typos in it, or it's disclosing sensitive government
information. You can also run these *after* an action is taken. For example, you
might log the fact that the action occurred, the result that happened, etc. So you
can apply hooks onto the agent harness, and this also allows you to control the
agent's behavior.

**Now the next layer above that is the engineering environment.** Think: we use Jira
to store bug tickets. We use Git to store the code. This is the name of the
deployment server. This is the name of the node that we use as the head node for the
compute cluster, if you're running your simulation there. These things can all be
written down. I mean, they're often known by engineers in their head, but they can
be written down. And this engineering environment probably has processes that one is
supposed to follow. For example, your team might have a standard operating
procedure — an SOP — related to how you handle a bug report: we open the bug report,
we check if there's a reproducible claim in there; if there's not, we try to do a
root-cause analysis and localize it ourselves; after we have a minimal reproducing
test case, this is the next step; eventually we make a fix; when we have a fix, we
write tests. That's the SOP for how you handle Jira tickets. Now, you might have a
separate SOP for new feature development. You might have a design review. You might
have a requirement that there be provable invariants, or proof. There's all kinds of
things you can require when you're doing new feature development. You might have
rules to follow when there is an incident: how do we perform incident review? How do
we triage it? Who do we route it to? All these things are SOPs in the engineering
environment. And you can control this environment.

An example of this is Git. Git is a place where you do version control. And in a Git
repo, like the agent harness, Git has hooks. You can register deterministic programs
that execute before a commit and after a commit, before you pull, after you pull,
before you push, after you push. Every Git command, you can hook. A great common
application of this is to have a Git hook on pre-commit, which runs tests or some
sort of lightweight check on the quality of a commit prior to it actually being
permitted into the tree. This moves feedback as far left as possible. And it
prevents bad things from entering the tree. You separately probably have power to
deploy integration tests, and a continuous-integration pipeline, and a series of
stages that it has to go through. This is also a point where you can inject controls
on the system.

**Now above that is your application.** And of course, the application has a bunch
of product code. And that product code can also contain some kind of governance or
controls. You can have models that describe how things are supposed to work. You can
have static analyses that check for out-of-bounds memory accesses, or for the lack
of comments on a file, or for a lack of documentation, or code that has no test tag
associated with it.

So those are basically all the points where you can plug in some sort of governance
mechanism. Our goal with all of these governance mechanisms is, at every point, to
prevent the agent from making bad choices, and to constrain its search space so that
we are conditioning it toward the kinds of actions we want it to take. Every step
you can take along this stack, every place you can inject governance and control, is
intended to steer the agent toward the behavior you want.

In a software system — or any real engineered system — this is incredibly important,
because the context window that an agent has is too small to contain any non-trivial
thing in it, whether that's the U.S. tax code or a web application. It's too
complicated for the model to make sense of. If you don't give the model any controls
or guidance or hierarchical representation of knowledge, the model has no choice but
to induce that representation as it goes along — and its context window is only so
big. So it will spend most of its time trying to figure out the rules of the road.

---

## 4 — The agent stack, continued

So all these layers of controls. Your agent pre-commit. Your agent harness that
says, "oh, we're running out of context window — please take a reliable output of
the current state and the plans, instead of waiting for a lossy best-effort
compression to happen." That's an opportunity to help the model reconstruct less
state after a compacted window.

If you have a pre-commit hook, that's an opportunity to help the model avoid
introducing defects into the codebase — but you're also steering it toward correct
behavior. Instead of it having to figure out the correct behavior from a failed test
case three context-window compressions later, it gets the feedback right away, while
everything it's done is fresh in its window. And if above that you have a CI
pipeline, and the CI pipeline produces a failure, it's still surfacing it to the
agent and allowing the agent to know where to go. So you're always trying to
condition it toward the behavior that you want.

---

## 5 — Semantic gaps and model synchronization

All right, now to the thesis of modeling in this book. I have said that what we're
trying to do over and over is push the model toward making the correct choices. And
I have said over and over that if the model doesn't have good guidance about what to
do next, it will not know what to do — you will not have constrained its search
space, you will not have conditioned its behavior.

So the basic opportunity for control is the prompt you give it — the words that you
say — because it's a language model. You communicate with words. But words are soft.
And words are imprecise; they're ambiguous. The less ambiguity you can have — in
other words, the more precision you can have in talking to the language model — the
happier you'll be. And you can write documentation for the model to describe how the
world works within this context: the governed engineering environment, the product,
its goals, the policies. You can describe all this in words. And if you're operating
an engineering *organization*, that's about all you need to do, because humans
aren't dumb — they can remember stuff, they know what information is important, they
know where to go look it up, and they know they'll get fired if they misbehave.

You need to treat agents as very intelligent reasoning things that need to know what
to reason over. And if all they have is documents, the documents are not precise
enough. Now, code is incredibly precise. Code is exactly what's going to happen. But
the trouble with code is that it is too verbose. What we need is a sweet spot. We
need something that is accurate and unambiguous, and yet not verbose. And the word
for this is a **model**.

Now, you're probably familiar with mathematical models — like *F = ma* from Newton,
or *y = mx + b* to describe a line. These are models. They often show up in physics
to describe how the real world works. And they're not quite right. *F* doesn't quite
equal *ma*. *y* is not always equal to *mx + b* in the real world; sometimes there's
a little bit of error, or some noise. And when you model something as a line — when
you model the distribution as a line — you're looking for the best fit you can. You
do some kind of minimization of the mean squared error. Fine. But it's not reality.
It's just a representation of reality. But it's a much cheaper representation to
reason over than the full dataset representing empirical conditions. It's much
cheaper to think about than the fluid equations — maybe a Navier–Stokes equation —
that are a bit of a nightmare. There are much simpler models that work pretty well. A
derivative. You can model a circle as a series of tangents to a curve. Is it
perfect? No. But it's pretty good. It's good enough — in the sense that you can make
accurate approximations of reality that are much cheaper.

Software has models. You've probably heard of UML, the Unified Modeling Language.
Never really took off. It came out of the '90s. People thought it was going to be
the future. And the problem was: the models are the map, and the code is the
territory. You make the map, you can then implement the code based on the map, and
then the territory — the code — has this habit of drifting. And it's very expensive
to keep the code in sync with the models. It's also really hard to represent all the
things you want to represent in a single model. So people would try to stack every
distinct kind of attribute you might care about on a codebase into one mega-model,
and then nobody could make sense of it. Or they'd try to slice all these different
aspects into different views of the model — but now you've got a proliferation of
models that people can't make sense of, and when you make a change to the code, you
have to go update ten models. It's a big pain. So people basically make box
diagrams. And that's what they do in practice.

Now, if you're working on super-high-criticality software, they keep the models up
to date. So Rolls-Royce, Boeing — these folks know that if they screw up, it's real
bad. And so they're willing to pay the cost of doing the modeling and keeping the
models up to date. But most other people are more interested in agility, because they
realize that whatever software they make, most of the context is going to need to
change six months from now — maybe a week from now. And so they'd rather not pay the
cost of keeping the models up to date, because they know the model is always going to
drift. So they rely on the code instead.

Now here's the trouble: the coding agents cannot reason over the code. There's too
much of it. They *can* reason over models. So if you can identify models that give
you a useful approximation of reality, and keep those models in sync, your coding
agents will be able to know exactly where to go. They'll walk through the docs.
They'll eventually hit the pointer to the model. That might be a data-flow diagram.
It might be a performance model. It might be an inheritance model. It might be a user
journey. There's all kinds of models — UML has 20-odd, and there's a bunch more after
that. If the agent finds the model, and the model is linked to the relevant parts of
the code, the agent can change the code. It knows where to go, and it can hold
everything inside its context window and make good choices, because it has a map, and
that map tells it where the territory is. And when they go to the territory, they
know the semantics and the terminology to worry about.

The model also lets them check their work. You can encode test cases for code, but
over a model, you can encode the invariants you actually care about. There are, in
fact, special languages for this purpose — we'll talk about those later in the book.
The model knows not just that the test suite passes; if there is a model, it knows
what needs to be true *beyond* the tests, without worrying about actually finding the
integration test (although I hope it does). It can see what is supposed to be the
case.

If you have models, you avoid lots and lots of issues of the form "the model decayed
the architecture of my codebase" — because the agent finds the architectural model,
and it knows to follow it. Because it knows to follow it, and because it has the
model, when it's making its change, it can check that it's followed the model. And if
it's changed the model, it can update the model. If the territory changes — it's
changed the code substantially — it can go back and retrofit the change into the
model, so that the model is in sync again. This is beautiful.

But, of course, we talked about how there's this stack of places to inject controls
or governance. One of these places is probably the pre-commit hook. And it would be
nice if you could say: "ah, the agent has committed a change that substantially
modified the actual call graph, and yet it did not update the underlying, the
overlaid model — we should reject this commit." This is a cool idea. But at the level
of commits, you may not be able to enforce the properties you want, because an agent
is usually making multiple commits and carrying out a broader goal. You could call
this adding a feature, or undertaking a ticket. A ticket usually has multiple steps
and moving parts. So if you try to do governance at the level of a commit for this
notion of model drift, you're barking up the wrong tree. You'll have to somehow
figure out that the model is done with its task within the level of the commit hook.

This is called the **semantic gap**, and it shows up any time you're trying to
enforce behavior at the wrong semantic level — the wrong level of abstraction. This
happens all the time in operating systems. You try to have security controls, but the
operating system can only see the system calls an application performs. It's hard to
figure out if the application is misbehaving based on one thing it does. So often you
need to stitch together a sequence of things it does, and then realize that it's done
a naughty thing — it sent sensitive information in a funny pattern through ten
network calls, and you have to stitch together all the network calls and figure out
what it did in order to see that the bad information leaked. Very hard.

So if you want to enforce governance, you need to find the right level at which to do
so. In the case of model drift, you should not try to do this at the pre-commit hook,
because the commit is the wrong granularity. But you can do it at the level of an
agent returning from completing a coding task — because you know the whole feature
and its whole plan. You know from that feature whether or not what it was doing
substantially changed the model — the map — causing the map to become out of date.
And so at the time the agent returns, it's got its whole statement of work that it's
completed, and you can check that for whether it correctly updated the model. Now,
"correct" is a hard word — but you can at least check that it's updated the model, and
that the body of commits associated with the work includes tests, and includes
documentation changes, and anything else that is supposed to have been done as part
of the work. That's the right semantic level for enforcement. This is what models are
good for, and it's also how you keep the models up to date. You need to find the right
level of abstraction, the right level of semantics, at which to do the enforcement.

---

## 6 — The governed engineering environment (ex-ante and ex-post)

So all this talk of models is very beautiful — *if* you know in advance all the
things that are supposed to be true about your software; *if* you know in advance all
the moving parts; *if* you know in advance all the policies that are supposed to be
upheld. Then you can, up front, ex-ante — that means from the beginning — write down
all of them into a specification, and then tell the agent it needs to honor all of
them. Congratulations. This is called specification-driven development. If you can do
it, you can be a happy boy.

However, here in the real world, most of the time — especially in software
engineering — people don't know what they're trying to build until they've built part
of it. And then after they've built part of it, they get a better sense of what it was
supposed to do, and they modify their goals, they modify the properties that are
supposed to be true across the codebase, and they have to change stuff. They also
change the model that they were expected to uphold. They may also discover new things
that they have to do, and they will need to construct new ways of enforcement.

So I talked about a governed engineering environment, and this environment has both
parts. It's got all the up-front stuff that you can conclude ex-ante, before you
begin. That might be something like a coding style guide. You know, Google has one,
Airbnb has one — all these organizations have coding style guides. All these style
guides say things like "every function should have comments," and "we don't use the
exec function anywhere in the codebase except in this approved part." All these things
you can write down up front, and you should. If you're working with agents, you
should give the agents the rules, and you should write deterministic checks on all
these rules. Wonderful. If you're writing a thing that has a check on the output —
that it's the correct format, that it has all the pieces it's supposed to have — you
should write it. Write the checker. I mean, have Claude write the checker. But
determinize all this stuff up front. That gives you a much stronger starting point.

But you're going to discover things along the way. You're going to discover that
performance is a problem, and you didn't have a performance model up front — you're
going to need to build a performance model. You're going to discover that the
particular versions of the underlying foundation models have a predilection for
certain behaviors, and these behaviors are a moving target — if you upgrade the
model, it might have different weird tics. In writing, a standard one is the use of
the em-dash, which LLMs — all of them — love to use. Nobody really knows why. It's not
like the data has em-dashes everywhere, but they all love em-dashes.

So you will need to construct ex-post governance mechanisms. That means: after the
fact, as you go along, you'll need to iteratively continue to strap on more and more
controls of governance, to make sure the models behave the way you want — based on
the failure points you've observed and the evolving properties of the software you're
trying to construct. So you define as much as you can up front in the spec, but you
also need to be able and willing to iteratively discover the mistakes that you're
making, or the mistakes the model is making, or the mismatch between what you thought
customers wanted and what they actually wanted, or the mismatch between how you
thought the code would perform and how it actually performed.

And you need to iteratively take all those recurring mistakes and convert them into
one of two things, to improve your governed engineering environment.

**First, controls.** A control is a way to automatically detect that a mistake has
occurred and surface it, to prevent the model from making the mistake again. Here's
an example: you should have tests, and you should run the tests, and if the tests
fail you should prevent the model from committing its code or shipping the code. We
all have test suites in CI. These are controls. Now, it'd be great if the model
didn't make the mistake — but if it does, you want to be able to catch it. So those
are controls. They're **sensors**. They're ways to observe and prevent bad behavior.

**The other kind of governance mechanism is architecture.** You can think of that as
a specific form of software architecture — but in general, when I say architecture,
what I mean is a means of preventing the model from making the *class* of mistake in
the first place. An example, a simple one: models will not, by default, do a very
good job at types. And types are how a compiler can confirm that people are calling
the right functions with the right arguments — is it a string? Is it a vector, a
stack, a hash, a person record? Is it an optional person record? Models are not, by
default, very good at this. If the model has used strings to represent state instead
of an enumeration, you can tell it: hey, use an enumeration here. And then afterward,
the model will never be able to make a string type error. Say it's a language model
and it picks synonyms for the strings — this is a problem, because the synonym
doesn't work. If you change it to an enumeration, it will simply not pick hallucinated
enum values; or if it does, the compiler will check it automatically, instead of you
having to wait until the test suite crashes to find out that you put a funny string
in there. So that's an architectural change.

These are the two kinds of governance mechanisms you put in place. Again, you'll put
some of them in up front, based on what you know about the problem and the domain and
your engineering environment at the beginning. And then others you'll need to keep
adding along the way.

---

## 7 — MBSE and Kruchten

Now, even if you got a degree in computing, you might not know about models. Models
in software are a fabulous idea that had a lot of trouble starting out. They were big
in the '70s and '80s, when people in general were building very expensive things —
think big government projects, think the Space Shuttle. They were very interested in
high assurance. That was partly also because the cost of computers was so high that
they couldn't afford to waste compute cycles. But with the advent of the personal
computer and Moore's Law, compute has gotten cheaper and cheaper. And with the
development of lots and lots of people who know how to do software development
globally, it's become cheaper and cheaper to get engineers to write software and to
change it. So the industry shifted away from careful up-front modeling and toward
ad-hoc agile methods, where we assume things are going to change all the time.

And this has probably, in many engineering and computer-science departments, produced
gaps in student knowledge. Because although models are a thing that are in the
textbooks, the faculty and the curricula often de-emphasize them, because they're
less industry-relevant. And of course, if you teach them, the students who've gone on
internships will say "nobody uses this" — and they're right. Nobody does use it.

The time for models has come. And so it's important that you understand the variety
of models that exist that you can use. Models are valuable because they give you an
abstract representation of computation. That is what they do. And the other thing
they let you do is give an abstract model of how data flows through a system. That's
the whole story of computers: computation over data. Different models give you
different views of computation over data.

Maybe you only care about the computation itself — you might be doing performance
engineering. And so here, what you care about is: how much compute does it cost to do
something? And when I'm doing that compute, if I have to send data across a network,
how much does it cost to do the data send? Should I do the compute locally? Should I
do it remotely? Am I going to need to interact with this data more than once — should
I cache it? Am I going to need to perform this computation more than once — should I
memoize it? There's all kinds of things you might need to model.

So we have a lot of canonical models. We have **data-flow diagrams** — super useful
for cybersecurity, for privacy, for checking where the data is going and who's
allowed to access it. We have **user journeys** or user stories — this represents the
set of interfaces that a user might interact with, and the actions they might take in
each of those interfaces to complete a task that adds business value. We have, in
object-oriented programming, **hierarchical inheritance diagrams**, that show which
specializations exist of an abstract concept that you could use or further
specialize. We have **bills of materials** — models of the dependencies a project
has, possibly direct, possibly transitive. We have **automata diagrams** — these
represent computation in an abstract manner by showing the states a system might be
in. A microwave might be on; it might have the door open; it might have the door
closed; somebody might be entering numbers on the keypad; if you're entering a
kitchen timer, it might be in a state for that; if you're changing the power level,
it might be in a state for this. These are called **state-machine diagrams**.

For each of these kinds of models, you're getting a different perspective on the
data. There's this really important work by **Philippe Kruchten** that articulates
what models are doing in the context of software — although it's a general property
of models. He talks about the **4+1 views** of software. It's true of software, but
it's true effectively of any complicated system. It's the whole field of systems
engineering that loves these models.

If you have the right model, you can write a policy over what should be true. And
that policy can be natural text — and it often is, in business documents — but it can
be written in a formal, unambiguous manner. So for a state machine, you can model the
flow of data or steps through the state machine, and you can describe what it means
to be in an unsafe state. In the case of a microwave, that might mean the magnetron
is powered on — it's cooking — while the door is open. That is not safe. And if you
have a policy like "never does that happen — never is it cooking while the door is
open," then you can apply that policy over the state machine, and assess whether
there's any path that leads us to a state where it's cooking plus the door is open.
Ideally, you have some kind of circuit breaker, where when the door opens, it shuts
off the magnetron. But if the circuit breaker is tripped, and then there's a path
back to powered-on, you've got a problem. You've got to cook yourself.

So each model has its own strengths and weaknesses, and the models ought to be
**orthogonal** — that's a fancy word that means they should be complementary, and
they should not be repeating themselves. Often they're interlocking. So you'll have
one kind of model for perspective A, like security, and a different kind of model for
user behaviors and user journeys. And you might want to write policies or invariants
or rules that span multiple models. So it's important that there not be repetition,
because if there is, you're kind of screwed — you have to keep things in sync. You'd
much rather have a body of models over which you can write policies, for each model
or for combinations or joins over the models.

This book is going to teach you about all these different model types, give you
examples of representing them in real code on a real project, examples of the kinds
of invariants you can write and articulate, and then how you can make sure that your
codebase does not drift from its models.

---

## 8 — Engineering lifecycles and SOPs

One of the crucial things you need to do in the engineering environment is have your
standard operating procedures — SOPs. These might be something you do intuitively
yourself. Congratulations, you're an intelligent human. Agents are not intelligent
humans. Agents do not have the operating context, and they do not know "how we do
things around here." And so, to work with agents on a substantial project, your
governed engineering environment needs to include **playbooks**. It also needs to
include **lifecycles**. You need to have a statement of: if we run out of storage on
the production server, here's what we do. If there's an incident, here's what we do.
If there's a this, here's what we do. If there's a that, here's what we do.

Now, you want to have the lifecycles first, the correct operation of the lifecycle
second, and then a map from "we've gone to the failure mode, the failure state, from
this node in the lifecycle — what do we do?" You might have some symptoms, and then
for each symptom you should have a description of what action you might take. Think of
this as a big grid. A way to think about this is called **failure mode and effects
analysis**. You think about all the things that could go wrong in the operation of
your project; you think about what the consequences of that are; and then — here's the
trick — you think about how to get out of it again.

Now, you know how to get out of it. You're not dumb. You know if there's a merge
conflict, you need to look at part A and part B and think about what was trying to be
accomplished and figure out how to deal with it. You know that if you run out of disk
space, you need to look at the typical fat parts of your system — for example, the
cache — and wipe it. The agent does not know all those things. The agent does not know,
if there's a merge conflict, where to look for each commit's background information —
but it should be written down somewhere, right? You need to tell it. It doesn't know
where the typical fat points of your system are, and it maybe, just maybe, will decide
that it should just nuke `rm -rf /` — that'll free up space. You think I'm kidding?
Read Twitter. Agents do it all the time.

So you've got to coach it. You've got to tell it where the typical hot points are, and
during resolution of failures in these lifecycles, your SOPs need to explain what is
*not* allowed. Ideally, you encode that via the appropriate semantic-level control —
think Git hooks, think agent hooks. But even if you can't encode it, you can tell the
agent not to do it.

Now, there is something I need to follow up on here. *Footnote. Pink-elephant
syndrome.* If you tell an agent not to do something, does it make it more likely that
it will actually do that? Humans can't *not* think about pink elephants if you tell
them not to — although, without the prompt, they would never have thought about it.
The apostle Paul says that the law taught him what it meant to sin, and without the
law, he would not have known what sin was. And this is true. It's helpful to know
what sin is — but it's also true that you might not have ever considered an action
until someone tells you not to do it. Maybe you would anyway, but it's a good
question. Anyway — back to the regularly scheduled programming. Where was I? Ah, your
SOPs.

So, once you've defined what should happen, you need to define what to do in the event
that something bad has happened. Or, in the positive sense: if there's a new ticket,
you need to describe the right steps to take. And I call the thing to do **playbooks**
or **runbooks**. These need to be divided into deterministic parts and reasoning parts
— parts that involve judgment. You need to help the agent with the deterministic parts
by giving it tools: executable scripts or programs it can run to always correctly get
the results — the deterministic parts. If you don't, it's going to wing it, and it'll
get it right some of the time, or most of the time, but not perfectly. And you're
going to be really glad you automated it instead.

Then, for the judgment-laden parts, you need to give it the rough algorithm, or kinds
of reasoning it might perform. For sufficiently constrained things, you can write down
the algorithm — and it might still need to do some of the glue work that agents are
really good at. You might not be able to fully encode it deterministically, but you
can still give it the rough algorithm. For open-ended things — think cyber threat
hunt, where the whole point is that the attackers figured out some clever thing you
never thought of — you can instead give it heuristics or strategies it might explore,
but not constrain it too much beyond that. Remember, you're conditioning the
probabilistic behavior of the model, and if you condition it down the wrong path, it
will just never get to the place you're trying to go. So if you don't know how to do
it, don't write confidently — just give it some hints. If you truly don't know what to
do, just tell it to solve the problem open-endedly. But remember: the less constraint,
the more tokens it spends, and the less likely it is to actually succeed.

Okay. Having distinguished the deterministic parts from the judgment-laden parts: for
the judgment-laden parts, if it's a measurement, give it a **rubric**. Tell it how to
operationalize qualitative stuff so that it can at least sort of quantify it, or
reason about whether something is good or bad. These models are clever. You just need
to tell it what the rules are. You might not be able to automatically detect if a
painting is good, or if student writing is good — but you can say: how are the topic
sentences? How is the artist's technique? Are there grammatical errors? Are there
weird blotches resulting from bad storage of the artwork? There's all these things you
can articulate. It's not going to tell you ultimately if it's good style — but agents
are pretty clever if you tell them the rubric to follow. It'll be good enough to give
it feedback, instead of you having to deal with the mess it makes.

Ideally, you may be able to articulate the judgment-laden parts through what I think
of as **pre-canned briefs**. The agent is going to need to take some steps, and you
want to articulate that in writing, so that the orchestrator agent you've got doesn't
need to guess how to explain the work to a sub-agent. It's got already pre-canned
instructions to adapt. This is a template. Templates are great, because they, again,
constrain how to talk about things to agents and how to do work. So this is how to
operationalize those SOPs in a way that will help your agents make progress.

---

## 9 — Brownfield guidance

All this sounds good if you did greenfield work. You've got a new rough sketch, you
can use agents to vibe-code a first prototype, and then you can work your way down to
an increasingly governed engineering environment. And it doesn't sound too bad — if
you know up front it's a new thing, you can avoid all the mistakes you made from prior
projects. That's the ex-ante governance we talked about. If you can do that, things
are good.

But you say: "I'm working on a legacy codebase. We started it before agents came
around. We even tried agents, and it added a hundred thousand lines of code that
nobody can read. How do I take these ideas and apply them to an existing codebase?"

Well, the answer is: step by step. There are a lot of different ways to attack this
target. We know what the starting point probably looks like: a bit of spaghetti, some
under-documentation, invariants and properties that only exist in somebody's head —
and you hope that person never retires. We also know what we want the endpoint to look
like: we want models necessary to express all the views of the system that are
pertinent to the quality properties we care about — that might be performance,
correctness, security, privacy, you name it. You need models that articulate it. We
want code that reflects those models — the map should equal the territory. The
territory should be refinements or elaborations on the map, but it should not be a
different place. When you zoom in on a map, what you should see is the county lines;
you shouldn't see that Switzerland's in the middle of it, by surprise.

We want the code representing it, and we want those models to have traceability for
our quality case. Whatever you're claiming is your quality property, you want to be
able to automatically make a case for it. How do you do that? You need to be able to
point to the code that implements the quality property; you need to be able to point
to the static analyses that enforce it; you need to be able to point to the protocols
you're model-checking against, if you're doing that for correctness; you need to be
able to point to the dynamic analyses — the tests — that confirm that, on all the
inputs you try, the properties hold. You need to be able to point to all these things.
And then you need to have records showing that every change that was made over time,
and why it was made.

So that's what we want as our output. It sounds like a dream — and as I've discussed
elsewhere in this text, if you have that, you can enforce it through soft and hard
governance mechanisms. You can force the agents to comply with it and keep it up to
date. A miracle. So how do we get from spaghetti over to a strong model-based
software-engineering environment? Well, it's not going to happen overnight. It will
require engineering rigor. And in particular, it is going to require that you and your
team pause to write down all the quality you care about, and for each quality aspect
you care about, you're going to need to build the models that encode the way in which
your system operates pertinent to that quality attribute. And then you're going to
need to build the connections between that model and the code, and you'll need to show
the model itself is correct (assuming it's implemented right), and then you'll need to
show the connections.

**Approach one — top-down.** You should start with a very coarse model, and you can
refine it yourself. You're going to start with something like: "on this input, the
test suite passes and we get the right output." You should be able to do that. Now,
that's a very coarse model — but from there you can say, well, what are the steps of
computation that are performed in between "insert file" and "output score" or "output
spreadsheet," or whatever your program is: "insert picture, and get out — where are
the cats and antelopes?" You can iteratively refine this model until it captures the
coarse abstractions and increasingly fine-grained abstractions. And at some point you
get diminishing returns — at some point the territory is the territory. You don't need
the map to *be* the territory, but you need it refined enough that you can show the
connection, for the level of quality assurance you're trying to achieve.

You can get this model in a lot of different ways. You can start with a whiteboard
diagram: take a picture, give the picture to Claude, and tell Claude, "I want you to
make a data-flow diagram; here's the starting picture, and code it in whatever
representation you like." In the self-governance skill, there is a description of many
kinds of models you might need, and the benefit of each. It'll know how to visualize
them — the self-communicate skill knows how to visualize things pretty well using
Mermaid. And then you can say, "Hey, look at the code and help me iteratively refine
this model — what nodes am I missing? What flows am I missing? What am I missing?" And
it will help you discover those things. As you improve the model, you can write
improved policies over that model, and enforce stronger and stronger assertions over
what is supposed to happen — statically, like "we never call exec," and dynamically,
as you integrate these different modules together. For an individual module: what
should be true? What are the invariants? What are the assumed inputs and outputs, the
preconditions and post-conditions? Can I automatically enforce all those things, and
map them back to an abstraction? And then you'll be able to talk about the interaction
*between* modules — when these modules interact, here's what should be preserved
across the interactions, or here's what the output should be, depending on which
specializations it's calling into.

As you do this, you will discover either flaws in your model or flaws in your
codebase. You'll discover places where the model doesn't match — the map doesn't match
the territory. Each mismatch means one of three things: the model's wrong and needs to
be refined; the model's at the wrong level of abstraction from what you're checking
(so maybe make a different model, or it's not able to enforce the property you're
looking for — use a different kind of model); or it means there's actually a
legitimate bug in the code — and the process of modeling and enforcing invariants
suitable to the level and perspective of the model is working.

Note also that you will almost certainly find a lot of defects if you're working on a
legacy codebase that did not follow this process. Of course you will. If you're
shifting from "best-effort, the tests pass" over to stronger guarantees about all
possible behaviors, of course you'll find defects. Now, it could be those defects are
not a problem, and you might say "working as designed — fix the model." Or you might
say "not worth dealing with," in which case you fix the invariant you're asserting
over the model. If it crashes only on some weird input, you could exclude that as an
input criterion to the model — you could say, "we assume all inputs are well-formed."
With that assumption, your validation criteria will no longer need to worry about
malformed inputs, and then you'll be fine. So you can build this from your own expert
knowledge.

**Approach two — bottom-up induction.** A second approach is to induce the model from
scratch. You could say, "Hey Claude, I want you to look at the codebase and help me
inductively develop the model." The first approach is kind of top-down — you're
starting with the coarsest abstraction you can, based on your understanding, on the
whiteboard, and refining it downward toward the code, toward the territory. The second
approach is starting from the code. Here, it's like: I'm standing on a street, and I'm
flying a drone up in the air, and as it goes up and up, I can see more and more — the
local things become less pertinent, and I can see how the streets are laid out, and
above that where the highways are, and above that where the cities are. As you fly up,
you discover levels of abstraction. And whether you're going top-down or bottom-up,
you'll hopefully meet in the middle, at the right abstraction — the right model for the
quality properties you're trying to enforce and the level of assurance you're trying
to achieve.

There's a cost-benefit trade-off here. If you're looking for a pretty low level of
assurance, then just run the tests — the coarsest model is "on this input, I get this
kind of output, and we check it dynamically." Fine. But if you want stronger
guarantees, you'll need a refined model, and you'll be able to write stronger
assertions over it. If you want the strongest guarantees, you need extremely elaborate
analyses on the control-flow graph, on the input and output of every function. You can
do it. It's really expensive — expensive to write down all the properties, and
expensive to run the checker, because the checker's having to deal with the full
monte, doing a grid search in every acre of the whole county. Whereas what you might
need for the level of quality assurance you're going for is just some checkboxes over
"the modules talk to each other and don't cheat on the boundaries." So — the answer is,
of course, it depends. Both of these paths depend on finding the right level of
abstraction for the properties you're trying to enforce.

Either way, you should probably start by writing down what it means to be correct. If
you can write that down, it will help you figure out the right level of abstraction to
represent that correctness property. If you're trying to achieve memory safety, you
need an extremely fine-grained representation, because you need to know about every
single memory access — fine, if you want memory safety, you're going to pay for it. If
you're trying to assert semantic correctness, you might need a much coarser model,
depending on the semantic.

So let's say you're trying to make modifications to a spreadsheet automatically, and
you're trying to keep a record of all the changes that are made. Your correctness
property might be: every modification is stamped, so that we have an audit trail. You're
an accountant; you need to be sure the books haven't been cooked. How do you assure
that? Everybody who interacts with the master budget spreadsheet has to sign off on
having made a change. To enforce that, you don't need to observe every person doing
everything — you just need to check the people going into the room with the
spreadsheet, and have a ledger of the person going in and the person coming out. If
you're trying to enforce that at the code level — let's say the code is automatically
modifying the ledger — you just need to say: every code path that modifies the ledger
has, on the way out, a call to the stamp function that collects provenance. That is way
cheaper to model and represent, because you're not trying to capture every aspect of
the code; you're just tracking a particular order of events. If there is a modification
action, then it is followed in the control-flow graph by a call to this other routine
that records provenance. You don't need to know what the functions *do* — you just need
to know that they are called in this order, by guarantee. That's a higher level of
abstraction, and it's therefore cheaper to enforce.

Now, if you want to *prove* that the stamping function works right, you need a much
finer-grained model. Fine. But if you just want to know that it's being called — and
you're going to use some other method to assure the provenance routine works right (a
human inspects it, you have test cases for it) — then a coarse model will be
sufficient. So it's very important that you define what correctness *means*. That's an
abstract notion: for security, correctness means something; for semantics, correctness
means something; for privacy, correctness means something. You need to know what your
**fitness function** is, and then you need to choose a level of abstraction that lets
you enforce it. It's going to vary by every codebase. It's your job as the engineer to
know and think about it. You might not know off the top of your head — it's your job to
figure out how to do this. That's the new job.

Okay, so that's an inductive approach — that's fine for modeling. Now let's say you're
trying to make things cheaper, so you can build these models. You can have all the
models you want, but if the codebase itself is a mess, it'll still be expensive to work
on. So how do we make it cheaper to work on the code? I'll give you a hint: models read
code like humans do. Humans like well-documented code, with comments that give the
rationale; humans like variables whose names reflect their purpose; humans don't like
deeply nested conditional statements, because it's hard to make sense of them. And
agents don't like them either — because as they operate, they need to somehow represent
that nested structure in their working memory, their context, and that's not free.
They'll have to pay for it.

So you can also inductively improve the *quality* of your code, prior to or concurrent
with the model-extraction process. And I would strongly encourage you to do some
up-front refactoring before trying to extract models — because otherwise building the
model is going to be very costly, since you won't be able to make sense of the code.
The agent won't be able to make sense of the code. Nobody will know what the code is
doing, because it's just a mess.

**Approach three — lint, cover, then induce.** So how do we make it less of a mess?
Remember, I talked about loops. We define a loop; we need to measure; we need to define
the inputs; we need to define the judgment or reasoning task; we need to define the
output — so it can control the system it's working in — and we need metrics to measure
how well it's doing. So how do we measure whether a type system is present, or if it's
just all ints and strings? You can define a static analysis that parses the AST
associated with the code and counts the density of primitives — ints and strings — and
if there's a high density of primitives, that is probably a problem. If there's a high
density of if-statements and nesting, that's probably a problem. In software
engineering, these are called **smells**. Smells mean this code might work, but it is
going to be very fragile when changed, because nobody will be able to reason over its
behavior. So I strongly urge you to make use of smell detectors. There are a lot of
them. These smell detectors are traditionally called **lints** — think dryer lint, or
belly-button lint, things you want to pull out to make things look nice. The lints are
cheap static analyses that do simple, local reasoning over an AST. And they're
generally generic: in no codebase should you have a function that is 2,000 lines long;
in no codebase should there be a module that is imported in every other file; in no
codebase should there be a switch statement that has 400 cases that are all strings; in
no codebase should there be structs that contain anonymous structs that contain
anonymous structs; in no codebase should you return unnamed, many-element tuples. Don't
do that. It's just bad. It might work, but it's bad.

So run the lints on your codebase, and instruct Claude to fix them in a
behavior-preserving way. Now, I hope you have tests. If you don't have tests, perhaps
you should consider starting with, "Hey Claude, please write tests to achieve code
coverage — line-based coverage, or conditional coverage — on this codebase, module by
module." Achieving line coverage lets you refactor safely — safely-ish — lets you
modify in safe, behavior-preserving ways, using the tests as your success metric, and
using the lints as your other success metric. And so you can drive iterative
improvement of the codebase through a combination of lints and code-covering tests.

Having done this enough, you will have a starting point for model induction. Claude
will have done its best to insert some kinds of abstractions, some kind of better
structure, and those structures will give clues to the model-induction process to
reason about what is actually happening. Because you'll have introduced classes and
subclasses; you'll have introduced enums with some kind of name, based on old docs
that are at least sort of explaining what's happening; you'll have introduced some
kinds of types; you'll have introduced names of things that go together as a struct —
you can name it, and at least that name of the things that get carried around together
will show any model-induction process the structure that's inherent, that's missing
from spaghetti code (that's smells; that's very linty).

So that's the third approach: if you have a sufficiently spaghetti codebase, the
strategy is — have Claude develop tests that cover the modules, and run lints, and then
fix all the lints, and don't allow the lint fix to pass until all the tests pass. And
then make that lint blocking — that means don't allow any regression in that lint
again. So now the test becomes "all the tests pass, and that lint still passes." There
are no longer unnamed return tuples; there are no longer random imports in the middle
of functions. As you squash each lint, you make it blocking again, and so you end up
with smells that get removed and never return. And when you're done with this process,
you've got cleaned-up spaghetti that might have some shape and structure to it — and
that allows you to induce the models.

Now, you'll probably need a combination of all of these techniques. It's not magic. It
takes hard work, and it takes judgment. But if you use these techniques in conjunction,
depending on the quality of your starting point, you will end up with that goal we're
trying to achieve: the right models to encode the right views or properties on the
codebase, with the right correctness criteria, with traceability to the places where
those criteria are implemented — audited statically, or dynamically, or through a model
check. So that's the recipe for application to brownfield engineering.

Now, how do I know this? I know this because when I built my application, I vibe-coded
a heck of a lot of it. I vibe-coded a couple hundred thousand lines of production code,
and it worked — but I had not attempted to impose much control over it. Parts of it I
had exerted a substantial amount of control over, because I pushed for a strong
architecture — I knew those were the very sensitive parts. The other parts, they're
like "there's a web layer here" and the front end — I sort of hoped Claude would just
get it right. Spoiler: it did not get it right. And so those parts became extremely
crufty. I had told it to use Python, and it did — but it didn't use types. Then I told
it to retrofit types, use Python 3 with types, and it did — but it turns out that when
I said "use types," what it heard was "turn on the type checker, and then make
everything strings or ints." It didn't actually build in the type abstractions I
wanted.

The same thing happened when I moved from JavaScript to TypeScript, by the way — it was
in the same week. I ported 100,000 lines of Python to "typed" Python (in quotes), and
150,000 lines of JavaScript to TypeScript. And in both cases it did the exact same
thing — which was the cheapest way to get the port over. Because, of course, it didn't
have a model. It didn't know the names of things. And so when I said "go through this
file and make it typed," it did — it just didn't have the ability to impose the right
names to things. It didn't know what to do. And it's probably better it didn't. So I
ended up with 150,000 lines of quote-unquote typed code that was not what I wanted.

I wanted to move that code toward a well-architected user experience, using
model-view-controller architectures. I wanted to move the web stack to reactive,
loop-based things, so it would be friendly for auto-scaling. And to do that, I had to
retrofit models onto this — I mean, it wasn't a million lines of code, but it was over
a hundred thousand lines of code I had to retrofit. And so I did the exact same process
in both cases: I turned on every lint from Ruff, and Pylint, and ESLint — hundreds of
commodity lints that enforced general smell checks — and then, for several weeks, I
blew four Claude Max subscriptions squashing every lint. And as each lint went away, I
made it blocking, so it could never emerge again. And I knew the architecture, the
coarse model I wanted; I said "pursue this model," but I had to iteratively get there,
by telling it, "okay, find dense primitive regions and induce some kind of structure
there, so that we can get toward porting to the right MVC architecture." After a bit, it
worked. And now I've got the models, the architecture, the code implementing the
architecture, and it's all linked together and held in place by enforcement when code
changes are made.

---

## 10 — Introduction to the skills

Okay, this brings me to the skills. This book is not just a methodology — although I
hope the methodology is of use to you. This book has batteries included. There is a
GitHub repo associated with this book, and it contains three Claude skills. One is
called **self-governance**. The second is called **self-operate**. And the third is
called **self-communicate**. Let me explain each of these skills.

**Self-operate** is probably the starting point. The self-operate skill says: here are
the lifecycles in operating this repo. That means all the things a software engineer,
or an engineering team, does — they pull tickets and implement new features; they pull
tickets and fix bugs; they optimize the codebase; they deal with resource exhaustion.
There are all these distinct kinds of things they have to do. Each of these lifecycles
is written down in a model. Right — I said model-based software engineering, and I'm
not kidding: models everywhere. You need to constrain the model's search space; you
need to condition its probability distribution, so that the agent you're working with
does what you want, and is biased toward working on things the way you want.

So, having written down the models, it also contains **playbooks**. I talked about
playbooks earlier — it's got them out the wazoo. There's playbook upon playbook upon
playbook. There's accompanying **briefs** for each step: when it's a judgment step,
there's a brief explaining what to do. And this allows the orchestrator — the one
running this skill — to know how to respond when events occur. Did an agent finish?
Great — reach for the next step in the development-process lifecycle, which is "agent
landed." Check if the feature's done yet. Go look at the epic file, which encodes what
the distinct launches are that need to happen to complete the epic — that might be
fixing a bug, it might be landing a new feature. Look at whether it's done or not. If
it's not done, launch the next thing out of the epic. If it is done, run the
definition-of-done check — that's an audit over the whole epic, that includes things
like "did the model drift from the code?" If that's all landed, mark it done, move it
off the pile to the done-epics folder. If it's still active, update the epic with the
latest status and the commit that made progress, and then launch the next agent out of
the epic's to-do list. There's a playbook for all of this, so it keeps the orchestrator
— which is running as a reactive loop itself — knowing, based on these inputs from the
environment, what it should do. Okay, so that's the self-operate skill.

**The second skill is self-governance.** This skill — its triggering criterion is: a
bad thing has happened more than once. Sometimes even just once, if it was bad enough.
If the bad thing happens more than once, this is a clue that we are failing to detect
it — that's a control, or a sensor — or that we are failing to architecturally prevent
it from happening. We have not put a wall in the right spot. We need a wall there. Or
we haven't detected people entering the building unauthorized — we need a badge checker
there, a control, or an architectural checker.

Self-governance has a catalog of a ton — a *ton* — of distinct governance mechanisms
and examples. It's about 65 at last count, although it keeps growing as I invent new
things. All the things I discovered were exposed from my perspective: I didn't know
they were kinds of controls I would need until I started building, and I kept getting
new failures as I went. As the velocity increased, more failures can occur, or
different kinds of failures get exposed. As I found new failures, I invented new
controls, new governance mechanisms, new architectures — and each of them ends up in
the catalog. I hope this turns into ex-ante governance for you, because all these
mistakes that I've made and discovered mechanisms for, you get for free. Just install,
and tell Claude: "Hey, audit my codebase and help me find room for governance."
Congratulations.

But in your operating environment, you will find your own failures. You'll be using a
different coding model than I am. You're going to be working with different
constraints, different kinds of customers, different human operators — all these
environmental factors affect the behavior of your coding agent, and so you're going to
need to introduce your own governance mechanisms. The self-governance skill includes a
posture, and a set of heuristics and strategies, for developing controls. For example:
**avoid a teetering tower of governance.** Check with the user exactly how detailed the
check should be. Is this a generic thing — how generic should the control be? Is it a
very specific thing? Do we need a lint for "never type the word X"? Obviously, that's
probably the wrong level of abstraction — but we also don't need a lint that blocks
ever typing anything. You need to figure out the right level of enforcement. You want
to avoid false positives or false negatives — which one is more important to you may
govern which controls you put in place. You might also say, "we need this to never
happen." That's called architecture — you put up a wall that prevents things from
happening. Every wall you put up constrains the behavior of the model. That can be good
and bad. If the wall is chosen well, it's only good. But if you put up a wall in front
of the only door — the main entrance or exit — you're going to have a problem if
there's a fire, and people won't be able to get to work.

So the self-governance skill is very sensitive to this. It has these strategies and
heuristics, and it will generally not make governance mechanisms enforced without
consulting with you — because you're the engineer, you know the context and
environment. But the governed engineering environment triggers this skill. There is a
hook. Remember, we need to pick the right level of semantics. From my perspective, the
right semantic point at which to trigger this skill is every 30 minutes or so in the
orchestrator loop: the hook spits out, "Hey, it's been 30 minutes — since I last
checked, have we encountered any recurring failures, or any repeated problems we solved
in different ways?" Maybe when you solve the same problem a couple of ways, you probably
end up with a don't-repeat-yourself (DRY) problem — that's a code problem. When you hit
the same *process* issue repeatedly — like "I failed to create a virtual machine"
repeatedly — well, that's some kind of process issue. When you encounter the same
problem, or solve the same problem, many times within a window at agentic velocity —
it's usually a lot of ground you're covering in that window — that's a clue that you
need a governance mechanism that should prevent the failure from occurring
(architecture) or make it detectable (controls, or sensors). So that self-governance
skill is automatically triggered, if you register the associated hook attached to it.

**Now the third skill is self-communicate.** This skill is about how Claude articulates
itself, to you and to other people. Although docs are a soft means of control for an
agent, they are a very useful tool for humans. And so there is guidance on how to write
different kinds of technical documentation. Credit to the **Diátaxis** project for
enumerating these kinds of documentation and giving rules. Also, thanks to the Apache
Foundation for providing great examples of such documents, that the skill leverages to
get the style and voice. You want to avoid imprecise claims. You want to avoid really
annoying verbal tics. All this stuff is baked into self-communicate. You want it to be
as terse as necessary, but no terser than that, to communicate well with other people
and agents. That's baked into the skill too. So when Claude needs to do writing, it
will turn to that skill. When it needs to make a drawing, that skill also says: "fire
me if you're going to do a drawing." And it teaches the skill how to make drawings in
Mermaid. It says: use Mermaid to do your drawing work; if Mermaid is not expressive
enough, use HTML or SVG. But that guidance keeps Claude from trying to generate raw
PNGs — which it tries to do, if it's not told otherwise, and it kind of sucks at it.

And you can add refinements to the skill — any of the skills, you can refine. The
self-communicate also has a list of jargon: the **lexicon** that it utters in the
context of your repo, or your project. If you're writing a paper or a technical report,
you want to use one term to refer to a concept. That lexicon file — you can bootstrap
it if you have existing material. And if you don't, you can say, "Hey, here's the
vocabulary we're going to use as we write," and it will keep that glossary or lexicon
and use those terms consistently as it writes. If you already have a repository —
maybe it's code, maybe it's a technical paper you're writing, maybe it's a user
manual — you can say to Claude (and there are instructions in the skill): "Please
bootstrap the lexicon." And it will walk through the repository, look at the materials,
and identify the different kinds of vocabulary and concepts that are present, and write
them down in its working definition. You can audit that. It will, in this process,
probably discover different words being used for the same construct, or the same word
being used to mean different constructs. Either of those is a problem for any human
reader — and it's also a problem for an agent that you've got to do writing or edit
writing for you. So you need to have that lexicon, and that bootstrap process may help
you discover mistakes in your own writing. And you can say, "Oh, that's a mistake —
there are actually these two concepts. Help me name them." Great, now we have a name.
"Now that we have these distinct concepts, please help me retrofit structure onto the
writing." Hey — it's exactly the same problem as we had for code. It's the same problem
because... well, let's talk about that in the next chat.

So those are the three skills that ship with the repo — the ship, and the agentic
governance mechanisms. Plug. I hope that they're of use to you.

---

## 11 — Everything is a series of transformations (Pólya)

When you work with any large language model — any machine intelligence, but especially
large language models, based on their underlying architecture, which is a transformer —
it is extremely helpful if you think about your task as a series of steps that need to
be taken, that transform an input into an output. Large language models are extremely
good at transformation. Given an input, and examples of the transform, or a description
of both, they are very good at undertaking the transformation on a new thing —
assuming the new thing is sufficiently close to the examples, or the transformation
rule is sufficiently precise.

The stronger the model, the bigger the leaps of transformation it can make with a high
likelihood of success. An extremely strong model can take pretty abstract instructions
and produce working code. Amazing. A weak model can take high-level instructions and
produce a dumpster fire, or nothing, or it won't compile — it just won't be able to do
it. So you need to tailor the level of abstraction you're using, and the kinds of
transformation — the size of the transformative leaps you're requesting — to the skill
of the model, and also, of course, to the degree of guarantee you want. If you want
high guarantees, then you want smaller leaps, and you want the ability to check the
result of each transformation as it occurs. If you want faster performance, there's
also a sweet spot. If you demand that it make tiny changes, it'll take a lot of changes,
and you'll pay a lot of tokens for that. On the other end, if you want huge leaps, it'll
take a lot of reasoning to make the leap, and you'll pay a lot for that.

Depending on the model, and the task complexity, and the transformation you're trying to
perform, there's a sweet spot — where the transformation is big enough that you're
leveraging the full power of the model, but not so big that it needs to do intensive
reasoning, or a very long chain of thought. So that's kind of the measurement you can
take: how many reasoning steps are needed? If it's zero or one, you're probably wasting
the model's capacity. But if it's more than a couple, you're going to end up with
probabilistic problems — because every step of reasoning it takes, there's a possibility
it's going to deviate, or make a funny choice. And those probabilities compound. You
don't want too many. With a 1% probability of failure in a couple of steps, that's still
quite low; with a 1% probability of failure at each of 100 steps, that's a quite large
probability that at some point a failure occurred. So you need to size the
transformations, based on the complexity and also based on the model scale.

So you should think about everything you do with an agent or an LLM as a series of
transformations, on some input, into some output. This means that the self-governance
skill, and the self-operate skill, and the self-communicate skill are all built on the
same underlying structure. So how do they work? Each of them has a set of models that
the agent needs to reason over. And it indicates the kinds of steps it should take —
and it's up to you, as the actual user, to break it down into (in your context) writing
the playbooks and the runbooks for the steps you need to take, or iteratively doing it
through context.

So the communicating skill, for example, is built on a foundation of the model's
original weights — which is all language — and on top of that it layers all forms of
rhetoric, out of, essentially, the Wikipedia entry on rhetoric: all the different ways
the Greeks invented to talk about things. And that includes "it's not X, it's Y" — but
it also includes many other kinds of discourse, kinds of articulation, depending on the
context and what you're trying to say. On top of that, there is the genre of writing
you're trying to perform — and there are a couple of different genres, coming from the
Diátaxis project. On top of that, there's the vocabulary set — the lexicon that should
be used to convey the points you're trying to make in that context. And on top of that,
it's up to you to plug in: who's the audience of this thing, and what do they know? I
don't know. The skill doesn't know. You have to tell it.

The self-operate skill has models at the base. The models are the lifecycle it's
supposed to be following. And when an event comes in — how to map that event to the
kind of activity being performed. Is this a development activity, a bug-fixing
activity, a resource-management activity, a deploy activity? What is it? And then it
maps those models onto playbooks, which are the steps it should take — the
transformations it should take on the input (which is the event) to the next step
(which is some characterization of a defect, or some design document associated with a
feature request). From a design document, we need to break that into the steps we take
— that's the next transformation. From those steps, we need to map those onto distinct
agent launches, and there are associated briefs. Each of these can be understood as a
transformation of some input into some output, toward a goal.

The self-governance skill has, again, the same thing. There's a model of what
governance looks like. There's a notion of architecture, and controls or sensors.
There's a notion of properties that ought to be true of any codebase — like
"don't repeat yourself," as a rule for architectural quality. There are kinds of
controls you can put in place: static analysis, or lints; dynamic analysis, or tests.
There are invariants you might write over models. There are ways of articulating those
invariants using different languages, like TLA. There are ways of validating those
invariants using things like bounded model checking. Each of these is a distinct
representation of the property you're trying to enforce over a codebase. And each entry
in the self-governance catalog describes how you get from the symptom you're
experiencing — the kind of recurring failure you're having — to the governance
mechanism, or mechanisms, that you're trying to put in place.

So each of the skills follows that same approach: take a general reasoning task, and
break it into a series of transformations over inputs into outputs, with steps that the
model can follow. That's how each of the skills works. And if you think about working
with agents using that same perspective, you will find yourself a very happy engineer.

---

## 12 — The role of training data in sizing transformations

There's another aspect of coding agents — software agents in general — that we need to
think about when we use them: their **training data**. The coding agent, we talked
about how it is a probabilistic model, and how what we're trying to do with this
engineering methodology is constrain its behavior, condition its probabilities — or, a
different way of saying this, tell it the path through the search space, or narrow the
search space it's searching over for solutions to the task. That search space, and its
baseline probabilities, are the result of training. And the training data the model has
received should be understood as the full contents of the internet, and all books that
have ever been written. And the model is biased toward things it sees a lot. So if it
reads one book about anything, with one position on a topic, and 100 books with the
opposite position, it will be biased toward thinking about the opposite position as
being true. It does not — except in special cases, where the model trainers have tried
hard to make it think a certain way — do anything other than weight the kinds of things
it sees a lot over the kinds of things it sees rarely.

Now, there's this reinforcement learning with human feedback, where you teach it not to
be bad or evil — you teach it morals or ethics in some way, and it's gonna try. You
teach it not to lie, but they lie all the time. You try to teach it not to steal, but
they steal all the time. You try to teach it not to hack other people's computers, but
boy, do they hack other people's computers if you let them. So all that training data
has its limitations.

It also includes, remember, the whole context of the internet. And that means that the
kinds of engineered systems it's seen a lot of, it will know how to implement your
variation on. And if it's never seen anything like what you're doing before, it's gonna
have some trouble. Now, this means that if you're a small-business owner, for example,
and you're trying to build your own version of some really standard thing — great. You
can build it yourself, and you won't need to license it. Because the thing you're trying
to license — if there's a bunch of people who have competing products, they probably
have documentation for those products, they probably have videos explaining enough about
how the products work, that the LLM can build its own. (You might be violating some
patents when you do this. *Warning.* You might be violating some patents. You violate a
patent when you use a concept, not when you take the code — so you're not violating
copyright, but you might violate a patent. If you're caught doing this, you will face
quite a lawsuit. So please be very careful about doing that.) But it'll be pretty good
at it. So if you're trying to make a to-do-list app — well, open-source software has a
thousand thousand to-do lists, written by undergrads and hobbyists and people who wanted
a to-do list. If you're trying to make a recipe tracker, or a fitness app — there's a
million fitness apps on GitHub, there's a million recipe trackers. Claude knows how to
do them in its sleep.

In general, if the application you're trying to build is a "typical web application" —
where there's a user interface with some buttons to enter a form, a backend that stores
that data in a database, some kind of compute engine over the database that produces
outputs — it's going to be able to do it in its sleep, because it's seen so many
versions of it. When you say, "I want a thing like this genre, this class of software,
and here are my specific details," it's going to be able to regurgitate the whole class
and then specialize it. This is why you see Anthropic able to claim it can make an
entire C compiler in a week. Amazing. Or, "we can make a port of Bun to Rust in three
days." Okay, fine, it's cool that it can do that — but it's also not surprising, because
its training data is full of examples of that class of software (a compiler), or, in
the case of the Bun port, the actual code that it's trying to port. It's not terribly
surprising that, given a codebase, it can convert it to another language. I mean, it's
cool, it's amazing — but given the capabilities we know about, of course it can. These
are tasks well within its training data, so it's good on them.

On the other hand — with respect to the transformations conversation — that means you
can ask it to make bigger leaps, because its training data has biased its probability
distribution toward the right moves: the right software architecture, the right
communication pathways for that class of software. It's seen it before.

But if you're building a new kind of application that no one has built before — if it's
a new class of software, if it's doing something hard that no one has done, or if you're
working in a research setting on high-performance computing — there's just not that much
open-source high-performance-computing code. Claude has read the docs for OpenMP and
Open MPI and CUDA. It's seen a bunch of ML-model CUDA code, but it hasn't seen a bunch of
climate-simulation modeling code, unless your organization has open-sourced it. And even
then, it's just a tiny drop in the comprehensive ocean of code. So the foundation models
are biased *away* from the kind of code you're trying to write. It just hasn't seen much
of it. It will therefore potentially impose the wrong architecture on the code you're
trying to build, the wrong working model — because it's going to try to map the things
it's biased toward onto your project, and then it's going to make the wrong choices.

**This is where model-based software engineering really shines.** It's where the
foundation model does not have the existing bias you need, and so it's your job as an
engineer to impose those biases, and articulate them explicitly. Now, if you're trying
to get good quality assurance, even on a standard class of software, you're going to
need the same level of rigor with the models. And again — code is cheap, and so this is
not actually that hard to achieve. You just need to tell Claude to do it. But if you're
trying to do it on a kind of software no one has built before, then it's just going to
have no clue, and you're going to need to really coach it step by step to get it right.
The up-front modeling will be more necessary for that kind of project than the
retroactive modeling you might do if you're standing up a vibe-coded web app.

I like to think about this through an analogy — the analogy to the **diffusion models**
that produce art, or pictures of things. If you ask it to reproduce an exact copy of a
famous painting, it will have no trouble doing so, because it's seen that painting
before, over and over. But if you ask it to draw a scene it's never seen — if you will,
a kind of art no one's ever made, art that combines things in a way no one's ever done
before, or just a complicated scenario — it's going to have trouble doing it, because
it's going off the pictures of reality, but not the real reality. Now, these
vision-generator models have improved substantially in the last couple of years, because
the companies that want better demos to attract capital have been trying desperately to
teach the models how to reason about the actual world — or at least more of the world,
one step deeper than the user's asking about, so that it knows how many fingers a human
should have. That way we don't have humans with 17 fingers, or two fingers. But
ultimately, these models always run up against the gap between what they know about the
world and how the world actually is.

The same thing happens when you try to engineer a system. If you try to engineer a
system it's seen many times before — like the picture of Starry Night — it's going to
have no trouble building that system. But if you're trying to engineer a novel system for
your startup, it will not have seen — I mean, I hope not; the whole point of your startup
is that it's building a new thing that doesn't exist, so you can compete in a marketplace
and be highly profitable. In that setting, the agent will not be able to produce useful
stuff for you. It's going to make a picture of what you're trying to build, but it has no
idea — the picture will be crappy. It'll have 17 fingers and two heads, because when you
say "draw an alien," it doesn't know what aliens are like. No one knows what aliens are
like. It's not going to map the reality.

So I like to think of this as: it'll build you a functioning prototype. But if you look
under the hood, it's a Rube Goldberg machine of hilarious extent. And a skilled engineer
is needed to turn that crude prototype — which probably works, by the way — into
something that will reliably work on the full breadth of inputs, and the full breadth of
quality attributes, that you're pursuing. If it has seen a million versions of the thing
— the to-do list, the CRUD-type web app — then what it produces beneath the picture,
beneath the I/O interface, is going to have the right parts; it's seen the engine room of
those things. But if it's never seen one of these before, or just one or two, it's going
to have no idea what to do. If it's never seen anybody actually use this very powerful but
obscure library that is not used by open-source folks — it's used commercially, or maybe
Microsoft or Google open-sourced the library, like Chrome or V8 — it can see the library,
but it hasn't seen people using the library well, and so it doesn't know how to use it.
And so it'll do something bad, something that works on the examples you've given it, but
will not work in general, because it doesn't know what to do; it hasn't seen it.

So if you look inside the engine room of the mock-up — the vibe-coded result, for a
complicated, novel class of software — it is not going to be correct. It'll be
demoable, but it won't be productizable. Not yet. Not without an engineer.

So that's a different way that I understand how to work with these agents. Part of the
engineer's job is to think about what parts of the system are standard — fair, the model
will have no trouble producing a reasonably correct thing; that's a bigger reasoning
leap you can trust it to make, you can ask it to make bigger transformations, produce
larger swaths of code and expect it to work. And the more obscure the thing you're
working on is, or the more sensitive it is because of contextual factors that aren't in
play in the training examples the foundation model has seen — the more obscure, or the
more contextually dictated the approach, the architecture, the implementation — the more
oversight you need to give the model, and the shorter the amount of reasoning steps you
can permit between the transformations you're undertaking. And the more you need to
condition the probability distribution yourself, to narrow the search space yourself,
using model-based software engineering.

---

*End of dictated material. ~17,220 words = roughly 3.5–4 chapters / a quarter-to-third
of a short technical book. Spine: metaphor → loop → stack → models → semantic gap →
ex-ante/ex-post governance → MBSE/Kruchten → lifecycles/SOPs → brownfield recipe →
the three skills → transformations/Pólya → training-data/novelty axis.*
