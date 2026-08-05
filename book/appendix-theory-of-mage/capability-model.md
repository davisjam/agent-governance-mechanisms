<!-- part-title: Back Matter -->
<!-- chapter-title: A Capability Model, Not a Maturity Model -->


MAGE is a capability model, not a maturity model, and the distinction is worth stating plainly because
the field has been here before. The dominant frame for "how good is your engineering" for two decades
was the staged maturity model: the CMM and its CMMI successor from the Software Engineering Institute,
which ranked an organization on a five-rung ladder from Initial to Optimizing and told it to climb. That
ladder was a real advance for its era. It named process discipline as something you could assess and
improve, and for organizations with none it gave a direction to move. *Accelerate* rejects the frame
anyway, and its reasons carry straight over to a fleet. A staged ladder imposes one linear progression on
every organization regardless of where its actual constraint sits; it grades process conformance in place
of the outcomes the process was meant to produce; and, worst under pressure, it decays into box-ticking,
where "we reached Level 3" comes to stand in for shipping better software. The complaint is not that
structure is bad. It is that a *staged ladder* changes behaviour — it makes the rung the goal.

By that test MAGE is already a capability model, and it was built as one before it had the label. The
catalogue is a set of controls, not a sequence of levels. A team adopts the ones that answer its own
bottleneck — the failure class actually costing it — in whatever order its constraints dictate, and it
reads its progress off outcomes rather than off a stage it has attained. The measurement model of the
previous chapter is the scorecard [ref: mage-construct-crosswalk]: durable throughput, defect-escape, and
oversight cost, each an observable on the [operator's dashboard](6.5-the-operators-dashboard.html), each a thing
the controls are supposed to move. The capability packages of the stacks appendix [appendix: appendix-stacks] are
the closest MAGE comes to a ladder, and they are careful about it. Each stack names an interlock and a
sensible adoption order for the controls inside it, because some controls presume others; but that order
is a dependency, not a rank. You adopt a package because you have its problem, not because you have
cleared the package below it.

The honest reason MAGE offers no levels is the reason it offers no fitted coefficients: it is one case. A
maturity ladder implies a progression validated across many organizations — that Level 4 reliably follows
Level 3, that the rungs mean the same thing everywhere. One repository over roughly twenty weeks cannot
support that, and printing a five-level scale off a single system would be exactly the over-reach this
appendix exists to avoid. This is also why the continuous term `m` in the churn-wall relation
[ref: mage-trajectories] is not a maturity level wearing a disguise. In `V_durable = V_raw·(1 − c(m))`,
`m` is a theoretical latent construct — how governed the environment is, how much of the system the maps
have made tractable — that the model reasons *with*. It is not a number a reader scores a team against. It
runs continuously because governance is a matter of degree, and it stays inside the theory because a
single case cannot calibrate it into a public scale. Read it as a variable in an argument, not a rung on
a wall.

What replaces "what level am I" is a plainer question with a more useful answer: which controls do you
have, and what does each one buy? A capability inventory sorted by the three governance targets — the
fleet that produces the work, the structured maps it reasons through, and the artifact it ships — lets a
team see its own coverage without ranking itself on a scale. When escapes are climbing, you reach for the
product-side controls; when the agents churn against a surface they cannot hold, you invest in the maps;
when recovery keeps pulling a human back in, you harden the fleet's substrate. The bottleneck in front of
you picks the next control, and there is no next rung waiting above it. That is what a capability model
gives that a maturity model withholds: a way to be deliberate about what you build next without pretending
every team must build it in the same order.
