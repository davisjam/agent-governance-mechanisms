# Churn is the scaling limit

**Claim** — An agent fleet scales until the work outgrows its context window. Then it churns: it re-derives what it already built and confidently undoes yesterday's fix.

| Concept | Big idea 1 · the problem |
| --- | --- |
| Claim | An agent fleet scales until the work outgrows its context window. Then it churns: it re-derives what it already built and confidently undoes yesterday's fix. |
| Mechanisms | — none yet |
| Related | governance-centric |
| In the book | book/1.1-the-printer.html |

## The idea

<!-- fig: 0 -->

This is the problem the rest of the concepts answer. An agent fleet is cheap and fast, so it scales — up
to a point. That point is the context window. Once the work a change requires exceeds what a single
context can hold, the fleet stops advancing the system and starts churning: it re-derives architecture
it already worked out, re-opens questions it already settled, and confidently undoes yesterday's fix.

Trace the chain end to end, because each link is a step you can point at. Long-horizon reasoning creates
working-memory pressure. Pressure forces the reasoning state to be compressed and reconstructed.
Reconstruction is lossy, and lossy reconstruction degrades the reasoning it stands in for. The
degradation surfaces as churn — effort spent rebuilding a picture the reasoner keeps losing, rather than
moving the system forward.

<!-- fig: 1 -->

Name the links concretely and the failure stops being abstract. An agent handed the raw code re-derives
the architecture, badly, because the real structure never fit its window. A second agent reverts a fix
whose reason it never saw. A decided design question comes back around because the decision lived only in
a conversation that scrolled out of context. None of these is a bad agent; each is the same finite
horizon, hit from a different side.

<!-- more -->

So churn is not one failure but a family, and the family has a shape. This entry names the problem; the
concepts that follow are the responses. No mechanism enforces churn — it is the wall the whole catalogue
exists to hold off. The two theses divide the work of holding it: the modeling thesis treats *what to
build* and *how to realize it* by giving the fleet a model to reason through; governance treats *how to
change the system safely* by moving policy into the environment. Read the rest as answers to this.

## Why it's more than a team slowing down

Brooks's Law says adding people to a late project makes it later: communication paths multiply faster
than hands, so throughput degrades. That is a slowdown — the work still moves, just at rising cost per
head. A fleet does something different. It does not slow smoothly; it hits a wall and reverses, spending
its cheap velocity re-deriving and undoing.

The limit is not coordination between workers. It is the finite reasoning horizon inside each context,
and speed does not relieve it — it reaches it faster. A team feels the pain gradually and can staff
around it; a fleet crosses the horizon in an afternoon and produces confident, plausible, subtly wrong
work at a scale no human can read. That is why the answer is not "add fewer agents" but "change what each
agent has to hold."

## The mechanisms that instantiate it

No mechanism edge is declared yet — this concept ships thin for now; the edge is enriched in a later pass.

## Related concepts

- [Governance-centric — the enabling substrate](concept-governance-centric.md)

## Read in the book →

[Read in the book →](book/1.1-the-printer.html)
