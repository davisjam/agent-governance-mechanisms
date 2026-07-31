<!-- Provenance: REPAIRED from book/transcripts/Definitions 2.txt (whisper.cpp large-v3-turbo, 7.0 min).
De-noised + aligned to the house lexicon. whisper broke this into one-phrase-per-line; reflowed into
paragraphs. The author's exact words and meaning PRESERVED — de-noising, not rewriting. The RAW .txt is the
source of record. -->

# Definitions 2 — model (raw note)

Now we have **model**. Model is a very broad word. It is a description that approximates the phenomenon it
is trying to capture, in a way that is useful for making predictions about that phenomenon.

Sometimes models are **mathematical**: they describe a quantitative relationship between variables — perhaps
imperfect but useful. Think *f = ma*, which may neglect the effect of friction in a simpler model but is
nevertheless useful. Another kind of model is **qualitative** — think supply and demand in economics. You
can predict a relationship between things but not necessarily the strength of that relationship: if this one
goes up, that one's going to go up, but we don't know exactly how much. Models can also describe the
relationship between things quantitatively — these are **relational models**: every time I get one of these,
I get two of those. The point is that these things go together. And you can describe the **flow of
information** through a system with a model: here are the set of transformations applied to data as it goes
through a system. This too is a model, a useful approximation of reality. There may be other things that
happen to that data — side effects that result from processing it — but you needn't include them for the
model to be useful, e.g. for someone auditing the mathematical outcome, or auditing who can access that
data.

On the other hand, the model's **fidelity** may influence your ability to use it. A model needs to be an
approximation that is *useful*, and useful is in the eye of the application. To understand roughly what kind
of system you're working with, it might suffice to say that it does information processing in a serial
manner. But if you're trying to understand cybersecurity or privacy considerations, you need a much
higher-fidelity model — one much closer to the real system, not a coarse approximation. So this notion of
fidelity is also crucial for understanding the idea of a model.

Now for the purpose of this text, that is what a model is. We must also talk about what a model *implies*. A
model implies **constraints** on the system or phenomenon being modeled. For the model to be useful it must
be an accurate approximation, and so a system constructed on the basis of such models cannot take *any*
form — it must take roughly the form described by the model. It can *elaborate* on the model, but it cannot
*diverge* from it. To the extent that the model diverges from the real thing — the thing signified — its
utility diminishes. Conversely, to the extent that the model maps exactly, its utility increases; and to the
extent that the model's fidelity is high, it *becomes* the thing signified, with good or bad results. The
thing signified itself is very difficult to understand because of its complexity; a model is simpler to
understand. So the more coarse the model, the cheaper it is to analyze the properties — and yet the less
accurate the analysis may become. So you get error bars around your analysis, shall we say.

All right. So these are the core definitions and terms. Please note the relationship between them. For the
purpose of this text: a model allows you to make predictions because it provides a useful perspective on the
functioning or behavior of a phenomenon. Therefore engineers love models — they can, without excess cost,
assess the trade-offs of different approaches to a problem. That's their bread and butter.

Now, an agent works with a knowledge base to satisfy constraints and produce a functioning artifact. Well, a
model sounds pretty good for them too, doesn't it? The model, which approximates the thing being described,
thus serves as a **constraint and a blueprint**. The agent is allowed to elaborate on those models but it
cannot diverge from them. And because agents are capable of reasoning over knowledge bases, the models serve
as the knowledge base of interest for the artifact being constructed.

These definitions and the relationship between them tell you the whole book in a nutshell. Our goal is to
describe the kinds of models that are of use to agents; to show how agents can interact with them, and
whether it benefits those agents; how to keep the models consistent with the artifact as the artifact is
constructed; and finally, to help engineers understand how to construct these models, how to assess them,
and how to use them to make predictions *prior to* the construction of a system.

We also discussed the implications of software agents making implementations free. In the olden days we
offered software development in an agile manner, figuring that building anything that functioned and met
requirements is better than not. Now we can build more than one — and, in the words of Fred Brooks, we can
build one to throw away. We can make models, we can assess our trade-offs, we can build a prototype in light
of that, and we can afford to do it more than once, to the extent that the model didn't work. This is all
very desirable.
