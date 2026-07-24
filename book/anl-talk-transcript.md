<!-- Provenance: transcript of James C. Davis's ANL talk "Cheap Code, Costly Judgment - Using Software Agents for High-Quality Software Engineering" (~72 min). Auto-transcribed 2026-07-24 with whisper base.en over 5 parallel ~14.4-min chunks, stitched in order. RAW source material for the book's writing work - not cleaned, not shipped as book content. Absolute minute M falls in chunk floor(M/14.43); per-chunk timestamps live in book/anl-talk-transcript.srt (e.g. the quality-metrics passage near minutes 4-6 is in chunk0). -->

# ANL talk transcript - "Cheap Code, Costly Judgment"

Okay. I wonder if she knows the elevator lady.
They're probably friends.
Okay. All right. Hello everyone and welcome.
Also welcome to our virtual people. I'm Nick and this is James Davis.
He's my PhD advisor, but he's also an assistant professor at Purdue.
And his lab studies essentially how to operate operationalize.
Time to writing software for various engineering computing disciplines.
So, essentially, how do you create software in a principal way?
How do we avoid failures in production systems?
And I think that's all I have to say. I think Jamie's ready to tell us something interesting.
I hope it's interesting.
I have about 45 minutes in the Q&A or discourse.
You can do it however you like.
I just interrupt and throw things, but I'll be like, you know, we had a dialogue.
And the online people too, so free to turn it.
You can look at the online people and then time interjections for me, okay?
Okay, got it.
All right. So, hi, I'm Jamie Davis. Thank you, Nick, for the introduction.
I'm here to tell you about my perspective on 3D printing production grade software
using coding agents, which is the question of the age.
I have only one social media platform left that I use.
It's LinkedIn.
And in between the GPT slop that constitutes about half of my feed,
people with like a emoji saying they're delighted to announce whatever.
The other half are engineers of the junior senior staff principal,
director level, who say, either.
I just have Claude write everything and it's great and miracle has happened.
And that's why you should the junior engineers.
And then the principal engineers and the directors are saying, you cannot do these things.
It doesn't work. You have to check everything it's doing.
And I agree with the principals that you can't just like tell Claude to write stuff
and hope for the best.
But I am also dissatisfied with the notion that what we need to do is check
every step that our agents take.
I think there's got to be a better way.
So this talk is about what I think about a step better way.
It might be wrong, but I'm happy to share my perspective and I hope it helps
some of you think about it.
This talk was hard for me to figure out how to organize and so as a result
that is slightly disorganized.
It's hard to think about how to organize it because I am tempted to tell you
about a methodology and a perspective on doing software engineering with agents.
And this is not a formula and it's not an algorithm to follow.
So there's a rough structure and I hope it's helpful, but also there's just
kind of nuggets everywhere and interrupt and ask questions as well.
Okay. All right. Let's do it.
So the general thesis of this talk is that implementation is now free.
You can ask your coding agent to build pretty much anything and get back
a facsimile of the thing you want.
Too sweet. How lovely.
But having implementation be free by itself does not mean that you can
produce production-grade software.
And by this, I mean software that has quality metrics that you can measure
and describe and audit for self-production-grade means.
In addition to saying, wow, on this input it does in fact make a picture of a cat.
You can also talk about why it's doing that and whether it's working
correctly and what changes you'd make to it to make it better and estimate how
much it would cost to make changes like that.
That's production-grade, right? That's engineering.
So we have to figure out how to move from writing code which used to be the expensive
part of software development. You make a whiteboard design in five minutes
and then spend a year implementing that stupid design.
And the design, you know, this is hard to write code. Okay, we get it.
It's no longer hard to write code. So now we need to figure out how to govern
the very, very fast software production that we can achieve.
So the theme here is we've got a fast-code fabricator and we need to figure
how to turn that into a production line.
This talk is grounded in my own experience.
I spent the last 16 weeks building a tool called Docable, which exists to make
Word, PowerPoint, Excel, and PDF documents accessible according to the Americans
of Disabilities Act. That is a very weird context to be doing this in
and it's probably not something that's of interest to HPC.
So that's fine. I'll tell you a little bit about what it's doing.
Well, I've been using that as a testbed for the ideas that we're going to talk about.
And I hope that the ideas and the method are of great interest to anybody building software.
The website's live if you want to try it out.
If you happen to need to make a document friendly to blind people.
It costs me money, so, you know, I can get coffee or something.
So, generative AI is a tool.
I think that we've all tried hope enough.
Hey, Claude, do this for me.
Hey, Opus, do that for me to figure out that it's not like a miracle.
It doesn't get things right.
So it's a tool that we need to learn how to wield wealth.
And it's not a tool like a stapler where it's just like, you know, you insert the paper,
cut chunk, my three-year-old knows how to work a stapler.
No problem.
I think it is much better understood as a fabrication device, like a 3D printer.
3D printers have this wonderful property that they can do anything you can dream up,
as long as you can figure out how to make it happen within the constraints of the fabrication system.
So you have arbitrary instructions.
You give a CAD.
It can make stuff.
If you give it bad instructions, you'll get bad results.
And if you give it really good instructions, you'll get really good results.
And a skilled operator of a 3D printer knows how to give it really good instructions.
And an unskilled one does not.
Now, by instructions, I do not mean prompting.
This is not a talk about prompting.
Prompting is the very first thing that you need to do.
But if that is all you do, then you will never be able to fabricate production-grade software.
Please don't stop at prompting.
It's very important.
So with CAD modeling, you have to have your CAD file, but then you have all these other things you need to do
and I don't know much about 3D printing.
I'm going to be honest, the metaphor is about to break down.
But you can't just say, here's the CAD drawing printed.
And you have to say, here are the layers in which to print it.
And here's how long you need to wait in between prints so that the material, whatever subtract you're using
will harden.
Here's how, which material we need to use at this point.
Here's how much it costs to do this part, which one should we do?
All these things are instructions that a skilled operator will provide and an unskilled operator will stop with.
Here's the CAD model, I guess we're good.
With this in mind, you should understand any work you do with coding agents in generative AI as it's a 3D printer
and I need to figure out how to use it well.
It is not a stakeholder.
So if you just try to do the obvious thing, it's not going to work.
Not a stakeholder.
I have a basic decision tree that I follow when I work with generative AI.
So I said it's not a stakeholder.
Well, sometimes it is a stakeholder.
So it's kind of a basic decision tree that I follow in my head.
If there is something that might affect my reputation who involves essential judgment, I use an interactive mode.
This is careful prompting.
I use it as a source of information.
I use it to do a little research to guide my decision making, but I do not let plot papers for me.
It assists me in writing papers, but when your reputation is on the line, you should aim for the best work you can do.
On the computational side, you have to describe the IO behavior that you're looking for.
And that IO behavior allows you to think about how to use generative AI to either build or be the process you're trying to achieve.
So when I say to be the process you're trying to achieve, you've probably pasted into generative AI at CSV and said make me a bar chart out of this.
And it probably didn't, right?
So that's a computational test small enough that it can fit inside the model, and it'll just do it correctly.
Great.
It can be the whole process you want on this input, make this output.
But lots of times, what you're trying to know is too complicated, the process you're trying to achieve is too complex.
You need to ask it to help you construct that process rather than to just replace the process.
So having specified the IO behavior, if it's simple enough, hey, Claude, just do this for me.
If it's more complicated, you might have a relatively simple computational task.
Hey, one shot making me a Python program to matplotlib this chart.
If you prompt it with that sort of task, it'll just work.
It takes, I don't know, a hundred lines of Python, a thousand lines of R or whatever.
It can just do it.
Good.
If you have something that's actually complicated, either it's mathematically dense or a very large expected code base, then I would not recommend you try to one shot it because it's not going to work.
You'll need to instead break it into parts and undertake what I think of as a supervised autonomy.
So you're going to need to govern that thing as it operates.
And some of the things you'll need to govern are the design of the system.
So what are the conditions under which we'll call this thing correct?
What might the subtasks or components of the system be?
We have these modules.
We might need to break up the architecture of a coding code base.
And the other kind of thing you might need to govern is the development process.
You might say, hey, instead of me talking to you, why don't I talk to a fleet of agents to do this work for me?
Or why don't I tell you to manage 50 agents on my behalf?
Great.
So you'll need to think about how to govern that process so that it will proceed in the way that you think is acceptable, and then you'll need to watch it burn and then try to fix it.
I assume that the good people of Argonne National Labs are occasionally one shot scripting stuff, but mostly trying to figure out how to build reasonably complicated stuff.
So most of the talks about this thing.
Is there something in the chat now?
No, not yet.
So there are three ways that people talk about supervising these agents.
Two of them are in my LinkedIn feed, and the third one is in a couple archives papers, a couple keynotes, and stuff I've been doing.
So in the upper left, we've got what I call the velocity-centric approach.
This one says, hey, Claude, what the whole system for me thinks I'm going for coffee.
And people will try to get a little smarter about this.
There's a famous work by Steve Dege called the Gas Town.
Have any of you read about Gas Town?
Nice.
The rest of you should give it a Google.
There is a medium post.
It's a blog post that's sort of like the guy was on acid, which I think he was very Steve Deprived.
Because I read a post kind of like it while Steve Deprived, and it was like, oh, wow, I sound exactly like Steve Dege.
Anyway, Gas Town says, hey, we can build arbitrarily complex software.
What we need is a description of what it's supposed to be, that process model.
And then we need to tell the agents, you're the developer, you're the planner, you're the tester, you're the security analyst,
you're the project manager, and we'll give them a town hall to talk in.
Gas Town, right?
It runs on gas somehow, and it's a town.
There's a bunch of different agents with personas.
And the biggest thesis was, hey, if we just give the agents the right personas and the right prompts,
they will be able to realize the whole vision without any supervision.
That's a content, right?
So if you do it this way, you get extraordinary velocity.
That's the idea.
You'll be able to produce the thing quickly.
But what you're going to get has very little in terms of control on the process.
You're just hoping the agents take their personas and apply them up.
Okay, so on the right, we've got one of the nicola, is the nicola nicola nicolas?
Not you, you.
It's the oversight centric model.
You don't trust the agent as far as you can throw it.
And so you say, hey, do this for me.
And it gives you back a code snippet or a suggestion and you study it very carefully.
And if you trust it, you say it's good.
You paste it into your code.
And you do it again.
And so you're basically bound by the speed at which you can type and audit stuff.
So in the upper left, we've got a very fast process with no controls.
And in the upper right, you've got a very slow process with a great deal of controls.
Neither of these sounds good to me.
No offense.
You end up with either a hunk of junk, right?
Or you're not done yet and you're going to chip sober.
You'll believe.
And the bottom left is where I think we should go.
It's what I call governance centric.
And here we've got our nice human that's me.
And the human describes policies about how the engineering work should proceed.
I'll show you a fancier figure of this that's expanded a bit.
And those policies produced a governed engineering environment.
Those are the rules of the road that these software agents can operate with.
And they're much fancier than it sounds like.
So this is not just personas where there's a prompt that says you're the tester.
There's way more you could do.
Okay.
So that's the third one.
If you have this, you've got your policies, they become controls and they, in principle,
should give you higher velocity because the agents are operating independently.
But better confidence in the quality of the result because you've embedded those controls
as executable, deterministic constraints.
Okay.
So that's our goal.
We want to get down here.
My LinkedIn is full of the people in the upper left and the upper right.
And that of them is where we want.
So I want to be down here in the bottom.
Okay.
Do you also want to be in the bottom left?
I would like that.
Okay.
So this is my expanded version of that governance-centric approach.
So the papers that exist about stuff, about agenda governance generally say, well, you've
got your policies that your organization needs to comply with, like security controls.
Just tell the agents not to go outside the network.
And you'll be fine and tell them not to be mean to each other and have access to policies
in place.
And they're sort of hoping that that's going to be good enough.
I don't think it's enough.
So the government engineering environment that I think you need in the governance approach
includes agenda governance.
So that's up here in the left.
And there's a bunch of examples.
When you're launching agents, you need to make sure that the instructions are giving them
are good.
That's the brief.
You can have a checklist of all the things that are supposed to be in a brief.
Make sure you check your work.
Right?

And if you just let the system run, those instructions are probabilistically excluded
because Claude is not reliable.
So you'll be like, make sure the briefs always follow this template and it'll be like, sure
boss, but it won't reliably do it, not all the time because it's a probability flip.
But you can determineize that and say, no, no, before we launch the agent, check that
all the things that are supposed to be there are present.
Okay.
That's a brief one.
That's a way to govern the agentic process that happens as they write code.
Another thing that you might want to take is called a docs hierarchy.
So we all know that coding agents have a context window.
That's the amount of information they can hold in their brains at once, more or less.
If they don't know where to find information, they might read the docs, right?
If the docs are an 800-page PDF with no index, I mean, you've all opened a textbook
before incoming index to be lacking and thought, when do I find the information?
Okay.
You flip through it.
Now, index, this is terrible.
I guess I'll have to read it in 100 pages.
If your docs are like that, the agent itself will have to go read it in 100 pages.
It'll blow up its context window and it won't be able to make a progress.
If you structure your docs hierarchically with indices and references and so on like a wiki
page, it'll have no trouble finding exactly the information it wants efficiently.
So that's another form of governance you can put in your system.
The docs should be hierarchical.
Each doc that we have should be no longer than whatever.
The docs they could be linked together.
Very nice.
Right.
So this is the thing that you can do to the agent environment that your agent's operating.
In the middle here, we've got the orchestrator.
So this is the thing in the middle that says, hey, I checked the orchestrator and said launch
an agent for this and launch an agent for that and it supervises the agents that are
happening.
So you can tell that orchestrator for this kind of work, use a cheat model for that kind
of work, use an expensive model for this other kind of work, use a super expensive model and
give it some opportunity to make judgments about that.
So that's the way to work with Orca to put governance into the orchestrator's environment.
Over here in the product governance, whatever thing you're building, you can just have code
or you can have coded tests.
That's good, right?
But we can push the level of rigor a little further.
You can also have code and dynamic tests and static analyses.
Turns out, if you ask Claude, hey, we're going to lend for this, we're going to lend for
it.
That's great.
And how many of you know what UML is, Unified Modeling Language?
Okay.
How many of you use UML every day?
Okay.
Why don't you use UML?
Do you have a time sync?
Okay.
Great.
Why don't you say it's a time sync?
Well, there's the initial time invested in actually building the diagram.
But after that, it's great.
You can reference it, but it's often hard when you're pressured for velocity to sit
down and create those documents.
And once you've already created a process, then you just have like some cost fallacy
of, oh, if I go back and do this now, I'm wasting time on this, I can't make myself do
this.
Okay.
So with software modeling, you've said there's enough for cost to building the model.
Totally true, right?
UML requires that I write down my boxes.
I never use some language to do it in, and I've got a nice picture which can help me
do the implementation.
And when people use UML in industry, they generally find that after a couple releases,
the UML diagram no longer matches the territory, right?
It's a map, but it's an out of date map.
And so I have a different problem.
New person joins the team, looks at the map, looks at the territory, it doesn't know what's
true.
They don't know if the difference is because the document is out of date, or the difference
is because there is a defect in the system that's been built.
Usually you should assume the docs out of date.
But you don't actually know it, so they have to go ask the senior, hey, senior, hey,
Solomon, is it supposed to work like this or not?
I don't know.
And Solomon has to go look at the UML and be like, oh, I made this in 2015, I had the
intern do it.
And it's been a couple of years, I guess, and it's 2026 already, wow.
And then maybe they'll update the UML model, maybe they won't, right?
But it becomes maybe useful, but not great.
Well, it turns out that Claude knows how to write UML models.
And if you would like to operate product development or large companies development
scale, you yourself should probably learn the language of models and talk to Claude
in that language.
Or, oh, sorry, I've just been using Claude for months like a drunkard.
So I'm going to say Claude a lot.
But insert whatever model you prefer, right?
It knows how to work with these things.
You can say, hey, here's a rough sketch.
Can you make a model for me in visual lives that use mermaid?
That's a drawing library.
About a bit about a boom, you have a visual to talk about.
And then you can say, hey, why don't you represent that in code for me?
And hey, it'll do that.
And then you can say, cool, well, let's implement it now.
And in the model file we've made, why don't we have a pointer that this component is implemented
in this tree of the file system.
And this component's implemented in that tree.
And well, we have tests too, right?
Well, why don't we have a pointer over to the tests?
So the tests for this component are here.
And the tests for that component are there.
And we have these static analyses too.
Let's link them all together, right?
This is the thing that's super annoying for humans to do.
And so generally, only shops like Rolls Royce and Boeing are doing this sort of thing.
This is called Model-based software engineering.
It's where you make elaborate models and then you keep them in sync through an elaborate
process.
And it's very expensive.
So planes and gas turbines are really expensive.
It's really valuable for actually making sure the system is working right.
And everybody can do it now, right?
You just have to say to Claude, let's do that.
And then it'll do it.
And you have to give it the right words, and it'll have to do some infrastructure development.
But it will work.
And when you're done, you get incredible velocity out of it.
I think I have a slight explaining why.
Yeah.
If you do the things I'm talking about, you can land a thousand plus commits a week for
months.
And you can change half a million lines of code a week for months.
So I do sleep.
I also sleep.
But this is the data from my repo.
The repo does not have a hundred billion lines of code in it, although the chart makes
it look like it does.
It has about four million lines of code in it.
That's about half a million lines of product code.
So that's the thing that actually modifies the document.
And it's got two and a half million lines, three, I don't know, a bunch of million, I
think two million lines of what I call the governed engineering environment.
So that's all the tests, all the static analyses, all the associated models, and all the documentation.
All these things go into the governed engineering environment.
So that's a hilarious ratio, right?
We're happy with a one-to-one ratio of code to tests, and I've got a one-to-four ratio.
So a lot of that is changing these things.
And then some of this vlogs, it is also me saying, ah, having tried this out, I now see
the design needs to be different, based on experience, based on this feedback from some
users.
Let's change it as soon as we go back and optimize things to modify the behavior.
But I have written none of this code, and yet it's producing hilarious volumes of progress.
And because I have models upon models upon models, I am very confident that the data
that the system has high quality.
I'm confident of this because I can run queries that say, hey, how is our test coverage?
And instead of, I mean, I have unit tests, right?
So the unit test will tell me this line is covered, and this line is covered, and that
tells you something.
But you also want to know, when a user interacts with this system, do we have tests that exercise
this reasonable sequence that the administrator might need to take, or that the auditor might
need to take, or that a user who is trying to remediate a batch of documents might need
to take?
I have a model for this.
That model is linked to the relevant parts of the code that do it, and it's linked to
the associated tests.
And so I can say, not just line coverage, but also for these different flows through the
system, how well is the flow covered?
And if the flow is not covered well, that's going to be a problem, because you've probably
had modules that work, but they're not being validated in the right sequence, and so there's
defects that are exposed when you have these interactions.
If you have a model, you can query it, and then have cloud continue to improve test coverage
against the flow that it's supposed to be doing, just the lines of code.
That is one example of what models can do for you, but because I've got all these different
things, I can now say with much greater confidence, the resulting system is of high quality because
I've got the models that encode the different aspects of the system quality I care about,
and their links to the code, and so I can audit whether or not these things are being
done.
Does this make sense?
Okay.
To get this to work, you need to figure out how to make this loop work.
Everything when you work with coding agents is the same loop, and you might have heard
about prompt engineering and loop engineering and kind of gets all the same loop, right?
They're just making up new terms to try to sell more tokens.
The loop is we've got some input and an ocean of a success metric.
We've got the agent does some reasoning, and then the agent produces some output, which
feeds back into the loop, and we score that output, it becomes maybe with some transformation
in the input, the agent reasons again, and we do some problems.
So the hard problem of working with agents is defining the success criterion, and my general
answer to this is two things.
First, we learned from John asked us to help, who wrote a famous CACM article called Measure
1 Level Deeper, that the metrics we get need to be at least one level deeper than what
the human facing metric usually is, otherwise it can't make informed decisions about why
the metric is the way it is, to know why the total compute, CPU cycles used on this job
were X, we probably need to know the things that feed into that metric.
So you need at least that level of measurement, if you were to optimize it, and the agents
not magic, it also needs that level of insight, so that's why, metrics metrics metrics.
The second thing is models, models, models.
If you don't give the agent some sense of what happens when it produces this output,
like what is happening over here, it will not be able to make progress.
I mean, it will, given enough time and taxpayer-fueled tokens, it will make progress, but it will
be searching over a very large space, and it will be trying to figure out what happens
when I turn this knob, but the thing is, you usually know what happens when you turn that
knob, so just tell it, and if you tell it what happens when you turn this knob, what
you're doing is building a model, so if you tell it, the models that let it guess at what
will happen when the knobs get turned, and perhaps the models on how to interpret this
input that's coming into the system, what does cycles mean, and how does it relate to
this other thing in the context of this system, well you can hope that it guesses, but why
just tell it, tell it programmatically, you can tell it with a prompt, but don't tell
it with code also, so this is another way to interpret this notion is, it's loop engineering,
but you need to figure out the metrics and the models that will help it reason over those.
Alright, so why have I been doing this, this is a very brief history of what I've been
up to, so the Americans with Disabilities Act is the reason that we have wheelchair ramps
in all of our buildings in America, the general thesis of America is everybody should have
the opportunity to succeed on their merit, the ADA part is about the opportunity, it
says, even if you have some disability, you should be able to access the same resources
that everybody else can, such that if you're meritorious, you'll be able to use those
resources better than the other people and have, I think, all the money in America, so
go get all the money, excellent, and we measure success here, in 2024 the US Department of
Justice said, well, in addition to wheelchair ramps in the modern era, it seems like being
able to interact with digital content in an accessible way also seems important, so if
you're blind, it will be hard for you to make sense of PowerPoint decks unless someone
has gone to the trouble of making them accessible, that means all the pictures have screen reader
content attached to them, the rendering order of the slide should be encoded properly, so
that when they click through it and the screen reader reads it, it's not in a random order,
all the stuff is now an obligation that any public entity has, including Purdue University,
and in particular, any learning materials that we give to students need to be accessible,
whether or not there is currently a blind student in our class, here at Argonne, I'm
sure it's a giant government entity that you also have to deal with this in some way,
maybe you're ill shielded from it, I don't know, but if you happen to need to remediate
a document, let me know, so remediation is super expensive, I time myself doing it, we're
talking about hours per document, I have hundreds of documents from my classes, I don't have
hundreds of hours to remediate documents, I do have hundreds of hours to play with
cloth and figure out how to do this well, so that's what I'm doing instead, I'm trying
to build an automated system for it, and you can try to pay TAs, but we tried that and
they don't do a good job, so I'm not going to do that, okay, so that's the problem, and
what I've been doing is building an automated system for this purpose, again, it's half
a million lines of production code, plus several million lines of government engineering
environment, I started with a feasibility probe like any good engineer, you know, iteratively
developed stuff, I mean, it worked for PowerPoint, my colleagues, they've made it PDF support
as well, I think of amounts of cookie, he wants PDF support as well, like expanded formats,
I started hosting it on the web software, the service, and then I went and actually
read the standards, because I was basing it first on what PowerPoint says,

and the accessibility tool, but then I read the law,
and the Microsoft is not attempting to comply with the law,
and so you have to do actually a lot more
than to comply with the law,
so I don't actually conform with the law,
but I know what I don't do, which is better than Microsoft.
They just tell you that it's fine.
And then I spent a while hardening it,
so that I would not suck.
And now I've recently switched over
to function as a service instead of software as a service.
So I moved from deploying a Kubernetes cluster
over to deploying a server listening.
While I've been doing this,
I peaked at maxing out four-clawed max plans every week,
so those are the $200 a month plans.
Thank you for paying your taxes,
but I can build the NSF for this experiment.
I'm down to 2.2 at this point.
So one other thing that's interesting
about the techniques I'm trying to tell you about
is if you used them, your token consumption
will drop dramatically.
And the reason for this is that when you tell the agent
the context in which it's working,
and then use that word generically,
but there's a bunch of really specific things
you could do like make models for your code
of all the different views that might be available.
So performance consideration.
What's the security consideration?
What's the data flow?
What's the component?
How do the services talk to each other?
All these different models you could make.
Instead of having to look at half a million lines
of production code every time the agent tries
to build a feature,
you can instead look at 500 lines of a model
and know the territory.
And as long as that map that it's looking at
is modeled, as long as it's consistent with the territory,
it will be able to make really fast progress.
Just do that again for us.
A whole module.
It will know exactly where to go.
This will link from the model right to where it is to go.
So we'll stop burning tokens.
And we'll use tokens because you'll get
more and more velocity here.
So you're ambition and grow,
but it will stop wasting time looking around
for things exploding in its context.
I don't have any compact like that.
That part just stops happening.
It's happening.
So I picked it four.
That was before this hardening step.
And a lot of this hardening consisted of me
putting models and models and models into place.
And as I did this,
I saw that it's token consumption went down and down and down.
So now I max out two a week instead of four a week.
This is progress.
Okay, so that's what I've been up to.
So firstly, go ahead to any questions.
Anything on the chat, anything from the room.
Good.
So if you're gonna work with an agent,
you need to understand what levers are available to you.
And so this is the starting point for everything.
You are working on some application.
Robert wants to know if I'll give an example, right?
Okay, Robert, I'll get to an example.
You're working on some application.
It might be some benchmark system you're developing.
It might be a simulation.
It might be in my case, a document, a mediation system.
It might be a cool app to show the public
all the good stuff that are gone.
I don't know, whatever you're building.
On top of that, you're working in some canonical
engineering environment, we're working on Git
and we push to this Git every bow or this Git every bow.
And these are the rules for pushing to the Git every bow.
Underneath that, you are probably,
instead of typing yourself,
you're probably talking to some agentic harness.
So you're typically not loading model weights
and invoking them directly.
That's down here, the gen AI model part.
You're usually talking to some harness,
most commonly open claw or plug co or something like this.
This harness talks to the gen AI model.
You give prompts to that harness.
So this is what we have to work with.
All right, so we're trying to engineer stuff.
So now we know what's available.
We know the territory.
So what can we do with it?
Well, each of these levels has distinct places
where we can do control.
So at the very top, we have an application
and we can define what correctness means.
What are the policies by which we can merge code
in the code base that is typically measured
by some combination of static and dynamic analysis.
We run the tests, we run the CI training.
Okay, so that's a thing that you can control.
You can say to Claude, hey, write tests for it.
Hey, revisit the CI, fine.
Below that, we have the engineering environment
and this is, is everybody using Git?
It's 2026, well, you can get, great.
Okay, if you're using Git,
then you probably know about Git commit
and Git pull and Git push, right?
How many of you know what a Git hook is?
Okay, how many of you don't know what a Git hook is?
Okay, all right.
A Git hook is a thing that you can register.
It's a script and a Git command line interface.
When invoked, if you say Git commit,
you can configure Git so that it invokes a script
or a program before the commit and after the commit.
So often it's called a pre-commit hook
or a post-commit hook.
For every single Git command, there is,
you can register a pre-hook and a post-hook.
Most commonly, people will use the pre-hook
to do some access control check or some quality check.
So before the commit comes in,
let's run the compiler on it.
Just, you can't even commit stuff if it doesn't compile, right?
The reason you might do this is,
instead of waiting until I push,
or I open the pull request and it triggers the CI train
and then I learn that my code doesn't compile,
well, that's silly, I should check that before.
And instead of me typing GCC blah, blah, blah,
I'm so lazy, just as a Git pre-commit hook run make
and if make fails, Git will refuse the commit
and it'll say, it's a program,
it'll print out whatever, so you could say,
exit code one, it's refuse,
and print out make fails, try that again.
If you register hooks like this,
then you will, whatever other operator
of the repository there is,
will be constrained in their behavior.
So you can register a Git pre-commit hook
that would hit Claude, every time Claude
has to make a commit and run automated checks
on the things that Claude is trying to commit.
And if they fail at that point,
Claude will say, oh, they're figgling
and then it will try to fix it.
We hope, otherwise it'll try to hack around it
or maybe break into hugging face and force, you know,
whatever, but it will at least be given a signal
that what it's done is not correct
and then it will have to choose what to do next.
Okay, so that's Git hooks.
Now below that, you're working with some coding harness
and these coding harnesses also have places
that you can plug in and control.
So there's two places.
One is a place that affects the reasoning process
that the model takes.
And the other is a deterministic control
over what it's allowed to do.
So let's talk about the deterministic control.
First, these are the hooks.
They work the same as Git hooks.
There are stages in the life cycle
or the loop that the agent is taking
that the harness defines.
These stages are things like before launching
a sub-agent or after a sub-agent finishes
or before when I'm planning to come to a stop,
should I do something?
Or right before we compact the context window,
should I do something?
Or right after we compact the context window,
should I do something?
So there are all these moving parts
that you experience when you're working
with a model into the hood.
That model has a limited capacity
and then the harness itself can talk to agents
and all these other things.
And so you can register exactly the same thing.
It's a program that is forcibly executed
at these different stages of the loop
that the harness is giving you.
So you can, for example, before compact,
say, oh, I'm about to compact.
Maybe I should write out the current things I'm working on
so that after compact, I remember what I was doing.
And then after compact, maybe I should go look
at the document, I just wrote out the handoff document
and say, oh, I'm back from compact.
Where was I again?
And so this way you get automatically a sense of
where you were.
I mean, if it just hits the compact automatically,
it will sort of remember what I was doing.
But it doesn't know what's important to keep around.
And so it's just like a best effort,
compaction, like some language compression algorithm
like strip out half the words from the context, right?
Okay, well, that's maybe it's better than nothing,
but we could do a lot better if we said,
here's our to-do list.
Okay, well, when I come back,
I don't want to happen to-do list.
I want the whole thing,
and I don't care about what I was doing four hours ago.
So you're basically giving it a policy about what to keep.
And any policy you give it is a whole lot better
than the default one.
That's a precompact hook, a postcompact hook,
you can say, hey, I'm back.
This is where we put that externalized record
of our memory.
Please go look at it, oh, on that,
and then it functions properly.
These are hooks you can put in the lifecycle.
So these are heart controls.
The claw can't cheat, it has to run it.
When it runs it, you can modify the external system,
and you can also print stuff to claw it
as though you were prompting it.
So an example of the kind of thing you can print to claw it
as though you were prompting it is,
hey, write out the record of what we're doing,
or if it's about to come to a stop,
I, for the first month, would come back to my laptop
and claw it would have said,
well, I think I'm going to rest for a bit.
And then it would stop working,
and I'm like, this is a to-do list.
Why have you stopped working?
So I would just, right, keep going,
and then it would keep going.
It's like, why don't we stop?
It just has some random decision to make a stop.
But I had to write, keep going.
Well, you don't have to write, keep going.
You can register a pre-stop hook,
and the pre-stop hook can literally just print,
keep going, and it will be as though you typed that
into the console.
Okay, well, now the lot has received the message,
keep going, and it will print out,
oh, I guess I'll keep going, and it will just pick up.
And why does it come to a stop?
Nobody knows.
It's a probabilistic machine.
It has random decisions.
It read enough forums for people
said, I'm tired, I'm going to bed.
That sometimes it says, I'm tired, I'm going to bed.
And you're like, you're a machine,
you don't know about bed.
That's just a phrase you made up,
but it stops anyway.
So that's stupid.
You can just tell it, keep going,
and it'll just keep going.
Now you should probably tell it
if something were sophisticated, then keep going.
Like, please consult your to-do list,
and choose from the next high priority task
and dispatch an agent for that,
so that it knows what it should do
when it keeps going.
But even just saying, keep going,
it's much better than nothing.
Progress, right?
You want the thing to make progress.
Okay, so then you have cloud skills.
So cloud hooks are a thing it has to do.
Cloud skills are a thing it can choose to do.
So cloud skill is the markdown, right?
It's a bunch of text files that you can register as a skill.
Each skill that you register comes
with a description of when to invoke it.
And when it gets invoked,
what that means is that the cloud,
or whatever harness you're using,
will go look in that directory,
give it its current context,
and it will see what's inside the skill
and make use of it, and this is all rather fuzzy.
But what people will do is they'll say,
if you're going to interact with a PowerPoint deck,
or a PDF, or this kind of file produced by this benchmark,
here is the structure of that file.
Here's the library that you should use to open
this PowerPoint deck.
Here is how to talk to this web server that we're running.
You define the interface,
there might be a tool that's allowed to call,
so you can use this document.
We have this tool that works here's the man page,
call it, and then a cloud will,
instead of making up how to open a PowerPoint deck,
or making up how to talk to your GRS server,
it will know exactly how to do it,
and will mostly do what it's adding.
So that's a skill.
You can't force it to use the skill,
but if it happens to trigger the skill,
it is very good for you,
because instead of honoring aimlessly
through the large space of how to talk to a GRS server,
it will know very specifically how to get
the right authentication to open and talk to it.
You might have heard about MCP.
Hooks often integrate with MCPs.
They say, here's the hook,
this is how to talk to that server.
But they can be more general than that.
So I have a hook called self-communicate,
and this hooks triggering is,
you were trying to write a document,
or draw a technical drawing.
And inside I have the rules about the kinds of documents
you might be writing, the writing style to use,
examples of my own writing.
If it's trying to do a drawing,
it will, I'll say the thing we used to draw
is called mermaid,
which is a text-based visualization library.
If you really can't use mermaid,
please use SVG or HTML.
But don't try to draw,
don't try to make a PNG by hand.
It will do that if you don't tell it.
If you say draw a picture,
it will attempt to make you a PNG.
It doesn't work at all, but it'll try.
But the skill that says,
hey, we're about to draw a picture.
If I say make a model of this thing that I can visualize,
you will say, oh, I need to draw a picture,
and then it'll hit my hook, self-communicate,
and then it will say, oh, the drawing,
here's how we draw around here.
Or you've all read writing from these models
and they're full of M-dashes.
And it's not X, it's Y, right?
There are all these things that LMs do well.
The skill that I would, you can install it if you want.
It says, here are the rules of writing.
And here are the 15 different ways
that you can say it's not X, it's Y,
and you can use M-dashes,
but you can all use colons or parentheses
or all kinds of things.
And it's just a bunch of different ways
that it can write better.
And there's also a lot of fun to go read your writing
and see if it can go right.
This is all stuff you can insert in a skill.
You can't force it to use it,
but if you write the triggering condition pretty well,
it will, most of the time, trigger it,
so that's the soft kind of control.
Okay, let me talk a lot.
I have three skills that I would recommend that you try out.
Here is a QR code, and here's a link,
and this talk is recorded, so I've done my duty.
There's one called self-governance,
there's one called self-operate,
and there's one called self-communicate.
Self-communicate, I already explained,
it's about writing and drawing.
Self-operate is about how one should operate
within an engineering environment.
So it knows out of the box how to get commit.
Rick, it doesn't know out of the box.
Hey, I wanted to design a new feature
for this code by some working on.
How should I do that?
Well, you can tell it, in the skill I have told it,
here's the text.

that we used to fill out a document with all the designs
that are going to be needed to implement the feature.
Here's a template to fill out for the planning
and the roadmap for implementing that feature.
The first phase should look like this.
The second phase should look like that.
The third phase should look like this.
And that planning document also says the first phase
maybe have a fable grade model do that.
I really expensive one.
The second phase, it's all just make work, have a sonna do this one.
The third phase is a little tricky.
Maybe an hopeless will have to do it.
And so that's all things that you can tell it to do.
They won't do it naturally because it's called code by nature.
It's just a happy thing that knows generally how people can
stuff like GitHub-ish, but it's not enough.
And so the self-operate scale explains
the different life cycles that are in an engineered environment
and how to annotate them.
Hey, we run out of disk space.
Here is what to do when we run out of disk space.
OK, it's not going to know that in your context unless you
tell it.
That's going to include instructions for my context.
But of course, you have your own.
Then there's a third one called self-governance.
This skill is about what to do when
you encounter the same failure more than once
or the same repeated thing more than once.
And so it's a very large catalog of, I don't know,
it keeps growing, I keep putting stuff in.
60 plus different moves that I've made
to deal with a returning failure.
And those moves are generally not patched and move on.
Those moves are generally either change
the architecture of the system so that this kind of failure
can never happen again.
Like, oh, we keep picking the wrong string value.
OK, well, maybe we should use an anoom instead.
And if you just tell Cloud to fix it,
it will usually just change the string value
to the right value.
But the right move is to make it an anoom, something
that's tight so that it can't make that mistake.
And so the self-governance skill says, oh, I've
seen this sort of thing before.
The right move is probably going to do it.
Great.
That's just a bunch of these moves that it can reference.
Recurring failure, that's a triggering condition.
Here are big catalog of things to do.
Usually, the catalog is enough, but in your context,
it might not be enough.
Even the act of thinking and recurring failure,
what should I do generally causes it to step back
and think about what to do?
So we'll either introduce an architectural change for controls.
These are things that are like sensors.
They'll have the text that a failure is happening,
at least so that you'll know that it's happening.
We'll just determine, recurring failures
into things that will automatically be prevented,
or at least detect it, so that you
can go back to drinking coffee while cloud works.
All right, I'm probably at time.
The website has this.
I have a nice view of who's a screech up from my website.
So this website has a pretty birdie clause.
Talk about this.
OK, so here's one worked example for agent briefing.
So when you say to cloud, hey, do this task.
If usually is going to dispatch an agent for that purpose,
you keep chatting with it, and it will in the background
be running something to do it.
So the agent in dispatches needs to know what to do.
That task is called its briefing.
It's briefing, so it's set of instructions.
So when I launch an agent, I say to the orchestrator,
hey, do a thing like this.
And the orchestra converts that into a briefing,
and that briefing follows a structured style
and when it's done, well, there's
a tool it calls to produce the structured style,
and then it fills it in, and then it calls dispatch.
And when it calls dispatch, dispatch
looks at the file and checks that all the things that
are supposed to be there are present.
One of the things that is supposed to be there
is what documents should I read so that the agent as it starts
up knows where to start in the Docs hierarchy.
And it might know, oh, where does this come from?
Well, here's a point of that.
If that reference is section is missing,
the orchestrator can't dispatch the agent until it fixes.
It's just an automatic gate that says,
don't run the agent until you've told the context.
When the agent boots up, I then have another technique
that I call dynamic context injection.
So if the agent is going to touch a set of files,
I have all these models, and these models
connects the components of the system we're
interacting with to the associated validation
and the associated static analyses
and the associated invariance that are present
and maybe the associated PLA specification that proves
that everything's correct, like you name it,
I've got it in there.
All these connections are there.
These connections can be articulated to the agent
if you know how to query your models.
And so the static context injection
is your job is to implement this feature
and hear the references.
And the dynamic context injection says,
you're about to touch these three files
and these two components.
Great, let's go look up from within the code.
The models that govern these files
and then use those to dynamically populate the life,
oh, when you edit a Python code,
you're not allowed to do inline imports of packages.
You can't, you have to put them at the top.
So it up front knows the rules of its operating environment.
When it tries to commit later on, on the other end of this,
I've got, of course, a pre-commit hook
and the pre-commit hook does cheap checks
on whether the file's okay
and it also includes running the linter, the type checker.
And then all those rules,
I tell it about upfront or automatically checked in general.
And so if those rules are broken,
we discover at this point,
but we really like to just not make the mistake
in the first place
because every time we screw up, it costs us tokens.
So that's why we do it upfront as well.
We give it some soft guidance upfront about what to do
and then at the back end, we check its work
and if it fails, it has to do it again.
We're going to avoid that looping.
All right, and then talk about this, yeah, fine.
So here, I'll stop at this one.
Here's an example of what a way to help cloud reason
through a problem is.
And I've taken this from,
I'm trying to automatically optimize something,
which many people I talk to at Argonne
say that what they do is try to automatically optimize stuff.
So if you're trying to automatically optimize things by hand,
you generally have a set of knobs you can tune.
Maybe you can change the code,
but often you just have 6,000 config parameters.
Great, which one should I pick?
I don't know, that's a big search space.
So you figure out some kind of a grid search, I guess,
if you're super computer to pick it up,
but often you're following some
heuristic search through the space
or some algorithm that gradient descent through it or something.
So here we have this loop that you're trying to optimize
and you need to figure out how to get an agent
to undertake the loop.
So in my repo and what I would encourage you to do, right?
So this is a standard step that you might need to take.
And if there's a standard step,
you might need to take,
you should write down the process that you're following.
And you should think about how to divide that process
into deterministic,
computable stuff,
needing a standard CPU and things that entail judgment.
To the extent that the thing can be made deterministic,
always do that,
do not ask cloud to figure it out.
Even if it does, you'll have paid thousands of tokens
for to figure it out.
If you could just run a Python program,
just do that.
And cloud can figure out how to write the Python program
and test it.
And then you're not,
it never needs to pay reasoning for that again.
So eliminate the need for reasoning if you can.
When you need to reason,
you should tell it what to reason about it
and how to reason about it.
So if you have some metrics that are coming off
of your loops as it's trying to figure out what knobs to turn,
you might have metrics come out,
you might have raw performance counters.
And you should be able to say,
hey, here's a model for what we expect
the performance counters to look like.
And if there is a substantial anomaly, that's a clue.
So the model for what they should look like
and the measurement of an anomaly,
that's, that is a deterministic computation
that you can undertake and you should give it a tool to say,
is this an anomalous reading?
Or did we get a big win on this one?
Otherwise it won't know to give it a tool.
But then you also need to compliment that with reasoning.
Like, if you see this kind of anomaly,
here's what that might mean.
And this is an incomplete list of heuristics and suggestions,
but at least you're guiding its judgment
to not making it all up.
The more that you constrain that judgment,
the faster the loop will be.
And the hazard is, if you over-constraint it,
it may not discover the optimal solution
because you're not as smart as a exhausted grid search, right?
But you're probably a lot smarter than a dumb grid search.
If you can figure out how to cook up something
in the happy medium, that'll be helpful.
Even like heuristic strategy that might follow
it might be very helpful.
So as you're building this loop, you need to figure out
the things you can make deterministic,
like what's the data space look like?
Good to give it structure for reasoning.
And then I would also suggest that you
determineize the next step.
So you're gonna somehow have to give a change
to the system that's gonna be performed.
And you can tell Claude to change the system directly,
but I would not recommend you do so.
I would instead recommend that you have Claude produce
a set of changes.
And then some deterministic program
map those into your environment,
hopefully also logging what it's done with the rationale
so that you have some traceability on the process.
If it logs what it's done in the rationale,
and you tell it in the judgment step,
hey, the history of all your changes are over here
because we deterministically logged them
before applying them,
that also will help in the judgment process.
So you have to determineize the steps
that are taken as a result of the output as well.
If that needs to do substantial reasoning,
like, oh, I'm gonna go look over here
and I'll look over there
and I'll think about how these two things relate,
it may dispatch agents to do that.
And you can pre-can briefs for those agents
as part of your playbook for this process.
You can say, if you need to do this kind of thing,
here is a good starting brief
that you can just copy and modify.
And this will prevent it from having to automatically
spend a whole lot of tokens thinking
about how to articulate to a sub-agent,
how to do this well,
which it will get right in 90% of the time
when the other 10% just waste your tokens again.
So you may not be able to fully determineize
the sub-agents work,
but you can at least give it structure
so that it will make faster progress.
Agents don't, they're not magic,
they can't just solve the problems,
but you can figure out how to model the operating environment,
measure the operating environment,
and give the agent constraints
so that it can make forward progress.
If you do too much of this,
then you'll end up in trouble.
You'll end up with so much code governing
and constraining the behavior
that you call it a tower of governance, right?
Still a five minute.
You can go too far on this.
So you need to find the sweet spot.
The problem with going too far
is that the agents then spend so much of its time
patching stuff and fixing this.
I don't know if there was a mistake there,
and it just ends up like,
and it's a little loom kind of optimize your guard rails
instead of actually doing the work you're trying to do.
And so part of your judgment
as the operator or such machines
is as you construct the government engineering environment
is using your judgment
and your observational powers to figure out,
are we having high velocity in the direction that we want,
or do we end up side-questing off here
trying to optimize the linters behavior
instead of over here actually building what we want?
So this is your judgment.
The code is free, the judgment is expensive,
wisdom takes time.
But if you don't try it, that also will work.
Okay, so thanks for coming.
I again have here these things
and this website that explains everything I've talked about.
Some of these things apply very directly to HPC code.
Other things don't,
because I have not been writing HPC code.
I hope that the method and the mindset does apply.
And then if you discover the kinds of things
you need to do here, please open up pull request.
I'd be very happy to merge with them
so that the skills will extend both to conventional web,
CPU-driven software,
and also to cluster type software,
which I have not been trying to do with this method.
Okay, thank you.
Thank you.
Thank you.
If there were some questions online that can you speak them?
There's that one earlier from Robert,
who just wanted, he said,
could we see an example of one of these models?
I've just been typing in chat,
I gave them the ones I like, but.
Robert, do you feel satisfied with the example I gave
about producing a structured playbook
for how to handle a thing
and working through an optimization task,
or do you want me to talk more about this, Robert?
I know you've got plenty of stuff to work on now.
Thanks.
Great.
Any other questions online or in the room?
Yeah, I wanna just quickly look at your metric
for velocity was changes.
Are you at all looking at the differentiation
between code, churn, and new features?
Because in my experience working with agents,
you end up in situations where you build technical debt.
And you get really,
one of the worst ones I've ever seen
is a Python function called safe text
that takes a string in, checks if the string exists,
and then returns the string.
For whatever reason,
the model that term into something like that
was required, and then it became like
the single biggest dependency across the code base.
But that's kind of like,
when I think of changes as a metric is pretty
low resolution.
And so what I've seen is there's a lot of like
going back and re-fixing this problem.
One of my favorite games on Steam right now
is a game called Data Center, who's made with AI agents.
And in the change logs,
just like how Herobrine used to get removed
from Minecraft, every change log,
they had this little thing that said,
oh, finally fixed motion blur.
Fixed motion blur, the final solution
really would be the 110 percent.
There are a lot of different ways to squash
the kind of problem that you're describing.
And it's very hard to give you a general, a specific.

because the answer is kind of, it depends on your operating environment.
But the general method that I've been following has been to say,
all right, here are all the things that I know should remain true about the code base.
And here are all the kinds of models I know I'm going to need.
Like I said, those all up, they're all automatically enforced.
On an agent attempt to commit a change, I have all these checks on it.
A lot of those checks includes, did I make a change that should have caused those
that might drift from the models?
If so, reject the commit until the model is self-updated, right?
So you can force it to keep in sync with all the stuff that you're interested in.
And then as new, funny things have done in your context, with your history,
with whatever model you're using as those things come up,
it's part of your job is to figure out what kind of constraints can I put into the system
so that it doesn't do that again, and this class of failure doesn't occur again.
So the self-governance skill, that's one of the three skills that are up,
is up there, basically says, it's in a hook.
The hook fires every 30 minutes.
It fires much more frequently than that, but it's got a timer on it.
So it says, if I haven't operated in the last 30 minutes, I'll write it again.
And it spits out one of these types of prompts.
And the type of prompts is, have you run into any recurring issue in the last 30 minutes
or any architectural anti-pattern like repeating the same code or concept in multiple places?
In the last 30 minutes, if you have, please call the self-governance skill.
And the self-governance skill triggers and has this giant catalog of all the ways
you might try to deal with this kind of thing.
And then it looks at it and, well, it fixes it usually.
Or it says, hey, I ran into this.
I see that we're repeating this failure.
Here are two ideas.
What should I try?
And then it'll try.
You have to tell it.
It's your job to have judgment.
Or you could just say, you know, do your best work.
Go for it.
So that's a way to automatically try to get the prevention of this sort of thing.
Is it perfect?
No.
But it's a whole lot better than what you have.
The way that you can try to automatically prevent that is very concrete control for this situation
of there is some utility that is included everywhere.
Because you can have a metric.
You compute over your code base.
That metric is, are there any substantial outlier modules that are being imported everywhere?
That's calculatable for a pretty cheap static analysis that we import statements.
If there is an outlier, fail the commit until the outliers result.
Or fail the CI until the outliers result.
So where you compute it, that's kind of a semantic question.
At what point in the engineering process ought we to compute and enforce this property?
That's up to you to decide you're the engineer who owns the whole stack.
But you need to figure out the right level of semantic.
Is this a journey to fine tune the model?
Please don't.
Do I need to put in hooks or skills?
Do I need to put in git hooks?
Do I need to put this at the level of the CI or the test?
You have to decide that for yourself.
Then you need to put it in and you can say, maybe it's CI time.
Super outlier, heavily imported modules are probably an anti-pattern.
We should just not do that around here.
And then it will never happen again.
So the context for this was a project made by one of my non-software engineer friends.
And it wasn't on git.
And he didn't know how to code.
And even using an agent with a harness.
Yeah, I was just pointing it out as an example of potential sources for code churn of the model
spending.
Something got here because you asked how much of what I'm showing there is churn.
Yes.
So the answer to your friend's specific issue is you need to figure out the right place
to put that control.
And what it is grab as they import outlier would prevent that from ever happening.
And I would probably put it in CI because maybe the pre-commits too low level for that assessment.
In my code base on Monday, I said to Claude, hey, I'm spending too much money on Google
Cloud hosting things that no one calls in this community's cluster.
I think we should go serverless.
One was Monday, two days ago, right?
Monday morning, I said that.
Last night, my production deployment is serverless.
This involved about 400 commits that touched the huge number of files that did a whole
bunch of rewiring.
But it was not churn in the sense that it was fixing its own technical debt and running
in circles.
It was an architectural change that I structured.
There were about 27.
I think it was 27 distinct phases that Claude said, well, bring it into 27 phases.
Fine, Claude, it's great.
Just do careful design.
Each of the designs it did, it surfaced because it was following the design template that
I asked it to fill out.
One of the things in the template is judgment calls.
What are the places you're uncertain about this back or the plan?
And are there things that maybe in your broader context of the whole architecture of the system,
I should know about.
It'll surface between one and about a judgment call questions, depending on its uncertainty.
So I looked at each of them and gave it a whole lot of answers.
It's 27 different sets of these questions and answers.
And then I said, go.
And then it's now serverless.
So that's sort of the experience that I have.
Before I put the models in eight roles, there was a lot more churn in technical debt.
And as I started to construct this thing with models everywhere and models for the models
and controls over the agents and the definition of the life cycle to follow and the runbooks
that you can apply.
And on the product side, what do we measure?
Where do we measure it?
At what point do the semantic levels do it?
After I started to do all of that, my token consumption went down and the churn went down
as well.
And I started to be able to say, do this and it would just happen.
And on simple applications, we can all do that.
But on complicated applications, mostly you can't do that.
But this technique allows me to do that.
So then that's your question.
Yeah.
And I've been a pretty significant hold out on agentic software for a while.
I'm going to set the Kool-Aid a little bit when I get back to school this fall and play
with this.
Your internship over?
I'm sorry.
When is your internship over?
August 7th.
Come on, man.
She has two weeks here.
Well, I'm talking a different project.
My project.
Yeah, but the tokens here are free.
Yeah.
I can get free tokens at home.
I'm going to make the university pay for it.
We just bought a $4 million compute cluster.
So I was probably just going to do an open cloth with an agent hosted on.
I'm in the pictures of building the cluster.
They love me.
They love me.
I hope.
Any other questions?
I'm sure somebody's going to come and yell at me in my office later.
In the context of a lot of the scientific software developers, people don't always do best practices
because they're like, say, best case, they're really limited on time.
So there's a lot of bootstrapping that probably has to happen to get to this kind of a loop.
Do you have any whatever sticks or insight on?
A good way to tackle that beyond just like general education.
Well, we are.
We have shifted from an era where it took so much time to write the code and get it to work
that we didn't have time to do the best practices to an era where the code is now free.
And I know that for HPC, the code is very complicated and the code is not quite free
because Cloud does not know how to do HPC.
I've tried it on the benchmarks.
It's not super good.
But if you give it hypothetically, if you give it a model of your cluster and your cluster's
resources and your cluster's performance characteristics and the IO bandwidth between dies on the same note
and cross-node communication and multi-clustered community, if you give it that kind of model,
it will be able to make much better decisions about what it's doing.
Because all this stuff in OpenMP and OpenAPI involves saying do this communication over there
and if Cloud knows the performance implications of doing that, it'll do a lot better.
So that's like a general statement.
If you have a performance model and then you try to write OpenMP code,
it will work better, I promise.
I have not tested it, but I have done enough other things with this that I can tell you that will work.
What you have is 10 million lines are 100 million, whatever.
Some horrible number of lines of things built by very well-meaning people for the last 50 years, right?
Self-governance, one of the skills, has an audit mode.
And you can say, please audit this module and think through how we could put a little more structure in here.
Now, one kind of tool that I have used kind of new tools for retrofit, better stuff,
because again, I started with I needed MVP to see if this is possible.
And what I got was a really chanky root Goldberg machine that worked, but it was a root Goldberg machine.
And I had told it, I wanted to use typed Python, Python 3 with types, and it did.
It specifically used to type string.
That was the type I used.
And so it was typed Python, but it wasn't typed, it was not stringly typed, meaning there were,
it's actually no type safety that the compiler was giving you the way that you might like.
So I tried saying put types in, and that didn't work.
And so what I tried doing instead was I had to write two things.
First, I modified the design template that is followed every time I order work.
And the design template now has a section title, types, type system.
And in the design part, the open string table model that's doing the planning says,
there are going to be these three types and here's how they're going to interact,
and we'll have some specialization off of this general type.
And then when it implements it, it actually has the type system.
So that's great for the new thing.
Now for the old thing, you can retrofit and you can say, here is a file and the associated document.
Things are a bit out of date.
Can you induce a design document following the template again?
The templates are awesome in these skills.
So induce a design doc following the self governance design template.
And then let's work through the migration.
Another thing you can do, and I have one of these two, it is a lint, the static analysis,
a really cheap one.
And all it does is it counts the density of primitives.
This is, again, part of my typing example, right?
So it counts how often the string type is used in a class.
And if the answer is too much, it just flags it and says, this is a problem.
Someone needs to go in here and put some types in.
And so you have kind of a top down, but you have an upfront, let's design the types in advance.
If you're building a new thing.
If you have an existing thing that's got decent documentation and you want to keep it around,
you can try to induce a better type system based on the documentation.
And if you really don't know what you've got and nobody wants to touch it, but it exists
as a documentation, you can also write automated measurements that give Claude a success criterion
to say, this seems to be better now.
And you can measure that in terms of the presence of primitives.
You can measure that in terms of how much coupling there is.
You can measure that.
A very simple thing that works pretty well is how many lines of code are in this file?
If it's more than 500, that's a problem.
We need to plan out a decomposition and the act of that planning.
Usually, I mean, it's a retrofit process, but you say make a design doc for what you want
based on what we've got and then plan out the mapping and then having done those things,
implement it, and now what you've got is an actual design that's present as a result
of looking at it a couple of times.
But if what you just say to Claude is, hey, make this better, it doesn't know what to do
because you haven't given it the deterministic parts that you can.
You haven't given it a description of what better would look like in a brief,
a description like a judgment-laden thing.
And you also haven't given it the loop that it can implement.
But you could do those things.
It'll cost a lot of tokens, but if you don't, you pay more time and energy servicing that
technical debt, then it would cost you a front to fix it once.
And so we have the tools.
You can fix it at this point.
You just need to walk it through the right process.
Does that make sense?
No, yes, that completely.
Again, I'm saying this is possible because I did it because in April,
I had 300,000 lines of code that were very crafty.
And so I spent a month saying, well, let's try retrofitting all these ideas onto the code base.
And when I was done, I had 200,000 lines of code that were not crafty.
And I said, oh, this is much better.
Excellent.
And so going forward, things have been way better, but you can, with an existing system
and enough thought, you can retrofit a design onto it.
So this is also real.
I'm going to try that.
I have my main project is very complicated microservice architecture with a lot of moving
parts that has no documentation.
I'm the documentation.
And so I'm going to give it a shot when I get back at creating the models and the procedures,
and then see what I can throw at it.
I don't think it'll be clogged.
But if it's something that can be hosted on a GPU that my university has,
they'll probably go for it.
So what I've been saying this whole time has been do software engineering, right?
So like, of course, do software engineering.
That's nice.
But I've been trying to discover the specific aspects of software engineering
that seem to be very effective in this process and how to map them onto this new technology,
this new kind of hardware we've got.
And I think it works very well.
So I think it works very well.
Okay.
All right.
I think that's all.
I think we're over time.
Just a little bit.
I really appreciate your time.
Thank you.
