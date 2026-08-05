<!-- part-title: Back Matter -->
<!-- chapter-title: A Theory of MAGE -->


This book argued from one case. A theory is what lets one case speak past itself. It names the parts,
draws the arrows between them, and states what you would have to observe to prove it wrong. That last
move is the point: a framework earns the word *theory* only when it sticks its neck out far enough to be
refuted. What follows is the argument of the book compressed into a causal model and a list of
predictions — each one a claim a larger study could test, and each one paired with the observation that
would sink it.

Read this the way you would read a load diagram, not a proof. The evidence under every arrow is a single
repository built over roughly twenty weeks, so the model generalizes the way a deep case generalizes:
it offers a *mechanism* and the *conditions* under which the mechanism should hold, and it invites you to
check whether those conditions hold in your own setting. The predictions are directional, not measured
laws. I fit no coefficients — one case cannot support them, and pretending otherwise is the failure mode
this appendix exists to avoid. Where *Accelerate* had thousands of survey responses and could estimate
the strength of each path, this has one system seen in depth. The shapes are the same; the claims are
weaker on purpose.

## 1. What the theory is for

Every mature engineering discipline reasons about the thing it builds through a model. This appendix
turns that habit on MAGE itself. The book's prose gives you the mechanism; the model gives you the
mechanism's *skeleton* — few enough boxes to hold in your head, drawn so the load-bearing relation is
obvious at a glance.

The relation to test is a single moderation. A fleet of coding agents produces change at a rate no human
reader can keep up with, and that rate does two opposite things depending on the environment it runs in.
In a poorly governed environment, velocity produces **churn** — effort spent undoing and reconciling as
the work outgrows what the fleet can hold in view. In a well-governed one, the same velocity produces
**durable throughput**. Velocity is not good or bad. It is a multiplier whose sign is set by the
environment. Everything else in the model exists to explain that sign.

## 2. The model

[ref:mage-causal-model] draws it. One driver on the left, two capabilities it feeds, one intermediate they
compose into, three outcomes on the right, and two conditions that gate the whole thing.

<!-- label: mage-causal-model -->
<!-- figure: assets/mage-causal-model.svg | *The MAGE Causal Model.* Agentic velocity drives two capabilities — modeling investment and governance conversion — that load onto governed environment quality E, which yields three outcomes: sustained throughput, falling defect-escape, bounded oversight cost. A dashed moderation edge sets the sign of velocity's effect by E: churn when E is low, durable throughput when E is high. -->


Take the parts in the order the method runs them.

**Agentic velocity is the driver, and its first product is not code — it is perception.** The fleet
produces change fast enough that related failures cluster in time. A gap in your abstractions, a boundary
you drew wrong, an oracle you never wrote: at human pace these arrive quarters apart and read as unrelated
mishaps; at fleet pace they arrive in an afternoon, close enough that you can see the structure they
share. Velocity exposes failure. What you build with that exposure is the rest of the model.

**Two capabilities turn exposure into an asset.** *Modeling investment* — the Modeling Thesis — binds
intent to implementation with a typed model the agent reasons over, held equal to the code by a gate, so
the work fits the context window before it churns. *Governance conversion* — the Alignment Thesis — takes
each failure class the velocity exposes and converts it, once, into a durable mechanism the environment
enforces on every later agent. One shrinks what the agent must hold; the other makes a policy decided once
hold against every change after.

**The two capabilities compose into one intermediate: governed environment quality.** Call it *E*. It
stands in the model where *Accelerate* puts "software delivery performance" — the thing capabilities
produce and outcomes flow from. E has two halves that match the two capabilities: the map equals the
territory (models carry the system and stay true), and the failure classes are mechanized (held by hard
controls, not merely watched by review). A high-E environment is one where a fresh agent finds the policy
already in the environment and cannot easily violate it.

**E produces three outcomes**, and they are the three dimensions the productivity literature already names
— velocity, quality, and sustainability — corrected for a fleet. *Sustained throughput*: durable progress
stays roughly linear as the system scales, because the churn wall stays out of reach. *Falling
defect-escape*: fewer confidently-wrong changes reach production as mechanized coverage climbs. *Bounded
oversight cost*: attention moves from changes to classes of change, so per-change review never becomes the
bottleneck the velocity was meant to remove.

**Two conditions gate the whole model.** *Capability-fit*: the agents must be matched to judgment good
enough to read a failure as a missing abstraction rather than a one-off bug. *Authority*: the person who
sees the recurring failure must be able to change the environment. Split either and the machine stalls —
a capable fleet in unfit hands is motion without direction, and a clear failure signal under split
authority yields a local patch instead of a shared mechanism, so the class never dies.

## 3. The measurement model

A causal model earns its keep only if its constructs can be observed. Each one here ties to a metric on
the Operator's Dashboard, so the theory is not free-floating — it reads out of numbers the build already
kept. [ref:mage-construct-crosswalk] is the crosswalk.

<!-- label: mage-construct-crosswalk -->
<!-- table: *The Measurement Model.* Each construct in the causal model, its role, the dashboard observable that reads it, and what a healthy value looks like. [short: Construct → dashboard observable crosswalk] -->
| Construct | Role | Dashboard observable | Healthy signature |
|---|---|---|---|
| Agentic velocity | Driver | Velocity; Churn | ~500 commits/week sustained; churn present but converting |
| Modeling investment | Capability | Missing-model metric; Model-sync efficacy | Orphan rate drains (56% → 7.89%); gates stay green |
| Governance conversion | Capability | Control growth | Lints 0 → 747, gates 0 → 102; accretes one class at a time |
| Governed environment quality (E) | Intermediate | Support ratio; Missing-model metric | Support apparatus leads production (~3×); orphans low |
| Sustained throughput | Outcome | Velocity; Churn | Roughly linear; deletions collapse as base stabilizes |
| Falling defect-escape | Outcome | Control growth; Model-claim coverage; Grammar coverage | Escape rate falls as mechanized coverage rises |
| Bounded oversight cost | Outcome | Support ratio | Apparatus stands in for per-diff review at fleet volume |
| Capability-fit; Authority | Scope conditions | (weakly observable) | Conversions land as shared controls, not local patches |

The support ratio appears twice on purpose — once as an input to E (the apparatus you build) and once as a
summary of it (the apparatus you have). It is both the spend and the balance.

Some predictions below ride constructs the dashboard does not yet carry. Four borrow *Accelerate*'s
delivery metrics — time to restore service, deployment frequency, change fail rate, delivery lead time —
and its deployment-pain survey; one borrows the interruption / context-switch cost from the productivity
literature. None has an in-repo observable on this build, so I state those predictions as
awaiting-instrumentation: the mechanism is stated, the metric is named, and the honest note is that
measuring it here would need an observable this dashboard has not added.

## 4. The predictions

Here is where the model sticks its neck out. Each prediction names a mechanism, the observable that would
show it, and the observation that would refute it. None is *tested* by this case — one repository cannot
test a claim about a population, and every row below is offered so a larger study can. [ref:mage-predictions]
collects all fifteen; the prose then walks them grouped by the governance target each one reads — the fleet
(**agent**), the typed maps (**models-bridge**), and the shipped artifact (**product**).

<!-- label: mage-predictions -->
<!-- table: *The Predictions.* Fifteen directional predictions MAGE makes, each with the metric that would track it, the governance target it reads, and the observation that would falsify it. Single-case; offered for replication, not proven. [short: MAGE's fifteen falsifiable predictions] -->
| # | Prediction | Metric | Target | Falsified if |
|---|---|---|---|---|
| P1 | Higher velocity surfaces a structural failure class *sooner* | Velocity vs. time-to-recur; conversion cadence | agent | Same-class failures surface no sooner at higher velocity |
| P2 | An apparatus that *leads* production sustains near-linear throughput; an under-invested one decays | Velocity slope vs. support ratio (→3×) + orphan drain (→7.89%); churn deletions | models-bridge | A low-support env sustains linear velocity, or a high-support one still decays |
| P3 | Defect-escape falls as mechanized coverage rises; under review-only it *rises* with velocity | Control growth (0→747) vs. escaped-defect / reopen rate | product | Escape rate is independent of mechanized coverage |
| P4 | Soft mechanisms saturate with velocity; hard ones do not | Recurrence before/after determinizing a class (marker: 3-in-5-days → 0) | agent | A soft/review regime holds violations flat as velocity rises |
| P5 | Model compression buys fewer tokens, more speed, *and* higher quality together — no trade | Token-savings at matched recall (model on vs. off) | models-bridge | The savings come at a measured cost in velocity or quality |
| P6 | The mechanism holds only under capability-fit *and* authority | Conversion rate vs. authority locus; recurrence after a local patch | agent | Split-authority settings convert classes to shared controls at the same rate |
| P7 | The substrate heals faster as it accretes controls | Time-to-restore (substrate) [DORA] vs. control growth | agent | Time-to-restore stays flat or rises while controls climb |
| P8 | Speed and stability do not trade under a fleet either | Change fail rate vs. deployment frequency [DORA] | product | Change-fail-rate rises with deployment frequency in a high-E env |
| P9 | Unmodelled surface leads churn | Missing-model metric (leading) vs. churn (lagging) | models-bridge | Orphan clusters do not predict later churn in the same subtree |
| P10 | A green model beats a green coverage number as an escape predictor | Model-sync efficacy vs. escape, benchmarked against line coverage | models-bridge | Model-sync adds no predictive power once coverage is controlled |
| P11 | The environment converts failure classes faster as its tooling matures | Delivery lead time [DORA] on conversion commits vs. project time | agent | Conversion lead time is flat or grows as the substrate matures |
| P12 | Generative (grammar) coverage, not line coverage, drives out format escapes | Grammar coverage vs. escape, contrasted with line coverage | product | Escape tracks line coverage but is flat against grammar coverage |
| P13 | A fidelity gate kills the silent-corruption class | Model-claim coverage of the fidelity validator vs. silent-corruption escape | product | Silent-corruption escapes hold steady with the gate saturated |
| P14 | Oversight moves from changes to classes, so interruption load per change falls even as velocity rises | Interruptions per landed change [SZ]; support ratio proxy | agent | Interruptions per change are flat or rising as controls accrete |
| P15 | Deployment pain stays bounded as the fleet speeds up | Deployment pain / burnout [DORA] vs. velocity | agent | Deployment pain rises with velocity even in a high-E env |

*Provenance of the metric column:* unmarked observables are slugs on the Operator's Dashboard; **[DORA]**
marks an *Accelerate* delivery metric and **[SZ]** a construct from the productivity-measurement literature.
The five external-construct rows (P7, P8, P11, P14, P15) name a metric this build does not yet record —
they are predictions awaiting instrumentation, not readings.

### 4.1 Reading the fleet (agent)

These predictions read the model on the side that *produces* the work — velocity as the exposing driver,
governance conversion as the durable answer, and the human cost of running the loop.

**P1 — velocity surfaces structure sooner.** Change fast enough and failures that would arrive quarters
apart arrive in one afternoon; proximity turns noise into a visible class. The observable is velocity
against a failure class's time-to-recur, with the paired fix-and-lint conversion cadence (208 such commits)
tracking commits per week. It is false if same-class failures surface no sooner at higher velocity — if
inter-arrival is independent of throughput. *One case can show the shape but not the slope: a single
timeline cannot separate "velocity clustered the class" from "the operator learned to look."*

**P4 — soft mechanisms saturate; hard ones do not.** A convention obeyed ninety-nine times in a hundred is
a probability flip; flip it *V* times per unit and expected violations grow as *q·V*, linear in velocity.
A constraint that removes the move costs no iteration and cannot be reworded away. The observable is the
recurrence count of a convention-guarded class before and after you determinize it — the worktree-marker
incident is the instance: three destructions in five days under prose, zero after the marker file. It is
false if a purely soft or review regime holds violation counts flat as velocity rises. *N=1: one
determinization is one data point; the general claim needs the pattern repeated where soft and hard regimes
can be toggled.*

**P6 — the mechanism holds only under capability-fit and authority.** Conversion is a judgment act followed
by an environment edit; remove either and a failure yields a patch, not a mechanism. The observable is
conversion rate and control growth against the authority locus, plus recurrence after a local patch. It is
false if split-authority or low-fit settings convert failure classes into shared, durable controls at the
same rate as single-owner high-fit ones. *This is the least measurable prediction — its observable is the
softest, and one owner-controlled repository offers no split-authority contrast to read.*

**P7 — the substrate heals faster as it accretes controls.** Each converted failure class either cannot
recur or recovers itself, so the pool of disruptions that still need a human to dig out — a clobbered
`main`, a destroyed worktree, a stuck queue — shrinks toward the newest, un-converted classes only. The
observable is time-to-restore-service [DORA], scoped to substrate disruptions, read against control growth:
mean restore time should *fall* as the lint and gate count *climbs*. It is false if restore time stays flat
or rises while controls climb. *One repository shows the shape — a marker file ended a recurring worktree
destruction — but a single case cannot separate "controls shortened recovery" from "the operator got more
practiced," and this build never recorded restore time.*

**P11 — the environment converts failure classes faster as its tooling matures.** Velocity surfaces the
class (P1); a maturing meta-substrate — codemods, lint scaffolds, brief templates, the audit-to-lint reflex
— then turns surfacing into enforcement faster each time. The observable is delivery lead time [DORA]
measured on *conversion* commits (recognition → enforced control) against project time: the lead should
*fall* as the substrate matures. It is false if conversion lead time is flat or grows — if each new control
costs as much wall-clock as the first. *A single project's learning curve confounds "the tooling improved"
with "the operator improved"; only cases with differing meta-tooling maturity at fixed operator skill
separate them.*

**P14 — oversight moves from changes to classes.** Converting a class once removes it from the per-change
review budget forever, so the operator's interruption load per landed change — the round-trips, the
decisions pulled up to a human, the context-switches — *falls* even as raw velocity rises. The observable is
interruptions-per-landed-change [SZ], with the support ratio as the dashboard proxy for the apparatus doing
the absorbing. It is false if interruptions per change stay flat or rise as controls accrete and velocity
climbs. *A single operator's interruption count is a self-observation, prone to the perceived-versus-objective
gap the productivity literature warns of; an instrumented, multi-operator study would measure it, not recall
it.*

**P15 — deployment pain stays bounded as the fleet speeds up.** The substrate absorbs the failure-recovery
load that would otherwise make faster feel worse, so operator-reported deployment pain and burnout stay
bounded as velocity rises rather than climbing with throughput. The observable is the *Accelerate*
deployment-pain survey construct [DORA] against velocity: as velocity *rises*, reported pain stays *flat*,
provided E is high. It is false if pain rises with velocity even in a demonstrably high-E environment.
*Deployment pain is a survey construct built for teams; on one operator it is a sample of one mood, offered
here as the subjective companion to P14's objective count, to be measured properly only across many
operators.*

### 4.2 Reading the maps (models-bridge)

These read the model through its typed maps — the map-equals-territory half of E, where modeling investment
keeps durable throughput linear or lets churn in.

**P2 — an apparatus that leads production sustains near-linear throughput.** Models compress the system
below the context window, so work fits before it churns; the churn wall (the fleet's Brooks's Law) moves out
of reach only when the map leads the code. The observable is the velocity-curve slope read against the
support ratio (→3×) and the missing-model drain (56% → 7.89%), with churn deletions collapsing as the
environment stabilizes. It is false if a low-support, high-orphan environment sustains linear durable
velocity as well as a high-support one, or if a high-support one still decays. *N=1: the drain and the
throughput are both observed on one timeline that cannot be untangled from a common cause — the whole
environment maturing at once.*

**P9 — unmodelled surface leads churn.** The unmodelled surface is where the fleet churns next: subtrees
carrying a high missing-model (orphan) rate predict a later churn spike in the *same* subtree, and draining
the orphans first keeps the churn that would have followed from arriving. This sharpens P2 from an aggregate
claim into a subtree-level leading indicator. The observable is the missing-model metric as the leading
signal and churn as the lagging one, correlated positive and lagged. It is false if orphan clusters do not
predict subsequent churn — if churn lands as often in well-modelled subtrees as in orphaned ones. *The drain
and the churn collapse are observed here, but on one timeline they cannot be untangled from the environment
maturing; a panel of subtrees, some drained and some not, would isolate the lead.*

**P10 — a green model beats a green coverage number as an escape predictor.** A change reasoned through a
true map escapes less often than one merely covered by tests, so whether the drift and parity gates stay
green predicts low defect-escape more strongly than line coverage does. The observable is model-sync efficacy
(gate green-rate) against escaped-defect rate, benchmarked against line coverage's own correlation with
escape: sync efficacy should carry *more* of the escape signal once both are in the model. It is false if,
with coverage controlled, model-sync efficacy adds no predictive power — or coverage dominates it. *One
repository kept its gates green throughout, so it offers no low-sync contrast window; the comparison to
coverage needs cases that vary sync efficacy and coverage independently.*

**P5 — model compression is a three-way gain, not a trade.** Working through a model that compresses the
system below the window lowers tokens-to-answer *and* speeds landing *and* lowers escapes together, because
every in-window token earns its place and the same model carries the invariants the change is checked
against. The gain lives in the representation, not in a smarter agent. The observable is MBSE navigation
token-savings (model on versus off) at *matched recall* — the near-term measurable the book's "garden null"
left open. It is false if the savings come at a measured cost in velocity or quality, or if matched-recall
efficiency shows no model advantage. *N=1, and worse: the token-savings field was null at collection, so
this is the sharpest bet the book cannot yet even partially read.*

### 4.3 Reading the artifact (product)

These read the model at the shipped artifact — the mechanized-coverage half of E and the defect-escape it
drives out.

**P3 — defect-escape falls as mechanized coverage rises; review-only escape rises with velocity.** A hard
control fires on every change regardless of throughput; per-change review coverage falls toward zero as
attention saturates, so its escape rate climbs to the raw per-change defect rate. The observable is control
growth (0 → 747 lints, 0 → 102 gates) against the escaped-defect or regression-reopen rate. It is false if
escape rate is independent of mechanized coverage, or if review-based teams hold escape flat as velocity
climbs. *One case cannot draw the review-only arm; it shows the control arm and predicts the contrast.*

**P8 — speed and stability do not trade under a fleet either.** In a high-E environment, pushing deployment
frequency up does not push the change-fail rate up: the fleet reproduces *Accelerate*'s central finding —
throughput and stability move together — rather than the intuitive trade where going faster ships more
breakage. This rides the same load-bearing moderation edge as P2 and P3, tested on the stability axis
Accelerate names. The observable is change-fail-rate against deployment frequency [DORA]: as frequency
*rises*, change-fail-rate stays *flat or falls*, provided E is high. It is false if, in a demonstrably
high-E environment, change-fail-rate rises with deployment frequency. *One case cannot draw the low-E arm;
whether a poorly-governed fleet shows the classic trade is exactly what a second case must supply.*

**P12 — generative coverage, not line coverage, drives out format escapes.** For a format handler,
post-release escapes fall as *grammar coverage* climbs toward full exercise of the input grammar, and line
coverage is a poor stand-in — the surviving defects hide in grammar productions no line number reports as
missing. The observable is grammar coverage against the handler's escape rate, contrasted with line
coverage: escape *falls* as grammar coverage *rises* and is only *weakly* related to line coverage. It is
false if escape tracks line coverage but is flat against grammar coverage. *One product's grammar is one
grammar; the general claim needs handlers for several formats measured the same way.*

**P13 — a fidelity gate kills the silent-corruption class.** A content-fidelity gate — one that asserts the
output still contains the input's content — drives *silent-corruption* escapes to near zero: the change that
passes every test yet quietly drops or garbles content, a class ordinary unit tests miss because the run
"succeeded." The observable is model-claim coverage of the fidelity validator against a silent-corruption
escape rate: as claim coverage of the fidelity invariants *rises*, the escape rate *falls* toward zero — a
fall the ordinary pass rate does not predict. It is false if silent-corruption escapes occur at the same
rate with the gate present and saturated as without it. *One product's corruption class is one class; the
general claim needs the pattern reproduced where a test suite and a fidelity gate can be toggled
independently.*

### 4.4 Where I would put money

The three founding predictions in the middle — P2, P3, P4 — are the ones I would back, because each rests on
an arithmetic that does not care about the details. Read together they say one thing: at velocity, the
environment is the variable, not the agent. Of the additions, two are the sharpest because each contradicts
a common intuition and rides a named external construct: **P8** (speed and stability do not trade under a
fleet) and **P10** (a green model beats a green coverage number). **P9** is the one most directly checkable
on the dashboard series this book already kept.

## 5. Two relations, sharpened

Two of the predictions have a form clean enough to write down. Neither is a fitted law. Each is a shape
that says which way the quantity moves, and why. The first is the model's core relation — durable velocity
as a function of how much of the environment the maps have made governable.

**The churn wall.** Durable throughput is raw velocity net of what churn eats:

> **V_durable = V_raw · (1 − c(m))**

where *c* is the churn share and *m* is how much of the system the models compress into the window. As *m*
rises, more of the relevant surface fits, so *c* falls and durable throughput tracks raw velocity. Let the
relevant surface outgrow what the fleet can hold and *c* climbs toward 1 — raw velocity keeps rising while
durable throughput collapses to near zero, the whole difference burned as rework. This is the churn wall,
and it is the fleet's version of Brooks's Law: where a human team's coordination cost grows with headcount,
a fleet's rework cost grows as the work outruns its window. The Modeling Thesis is the move that pushes the
wall back. It is the arithmetic behind P2 (and the leading-indicator sharpening in P9). [ref:mage-trajectories]
draws the two regimes.

<!-- label: mage-trajectories -->
<!-- figure: assets/mage-trajectories.svg | *Two Trajectories.* Durable throughput against cumulative work, drawn for two environments. The governed curve (high E) climbs near-linearly with a hardening dip; the under-governed curve (low E) shares the early slope, then flattens at the churn wall. The shaded gap is churn. Line A is observed, Line B predicted. -->


**Escape under two regimes.** Let *p* be the per-change probability of a defect, *r(V)* the fraction of
changes a human review still catches at velocity *V*, and *κ* the fraction of failure classes held by a
hard control. Under review-only governance the escape rate is `ε_review ≈ p·(1 − r(V))`, and because
attention is finite, *r(V)* falls toward zero as velocity rises — so `ε_review → p`, the raw defect rate,
review contributing nothing at the limit. Under control-based governance `ε_control ≈ p·(1 − κ)`, and *κ*
does not depend on velocity, because a machine applies the control on every change. The gap between the two
regimes,

> **Δε = ε_review − ε_control → p·κ**,

*widens* with velocity. That is P3 in one line: the faster the fleet runs, the more a control regime beats
a review regime, and the wider the daylight between "looked obeyed" and "was enforced". The soft-saturation
companion is simpler still — a soft convention with per-flip failure *q*, flipped *V* times, is expected to
fail *q·V* times, linear in velocity, against zero for the constraint that removes the move (that is P4, and
by the stability axis it is the arithmetic under P8 as well). The `r(V) → 0` idealization is a claim about
arithmetic, not a curve I measured; read it as the reason the gap must open, not as a fitted rate.

## 6. For posterity

I will not oversell what this is. It is a theory read off one system, offered in the spirit of the field's
better single-case work: here is the mechanism, here are the conditions I think it needs, here is what you
would have to see to prove me wrong. The value of writing it down is not that it is confirmed — it is not —
but that it is now *refutable*, and a refutable claim is a gift to whoever runs the experiment next. N=1
generalization, but here it is for posterity.

A handful of studies would turn these predictions from directional to measured, and none needs my
repository. A **multi-case comparison** across environments of differing E would test P2, P3, P8, P10, and
P12 directly — does the apparatus-leads-production signature actually predict sustained throughput, falling
escape, a decoupled speed/stability curve, and a model that out-predicts coverage? A **longitudinal
instrument** that tracks a failure class from first appearance through conversion would test P1, P6, P7, and
P11 — does velocity really shorten time-to-recur, does split authority really stall conversion, does the
substrate really heal and convert faster as it matures? An **instrumented interruption-and-pain panel**
across several operators would test P14 and P15 without leaning on one person's memory. And the
**matched-recall efficiency measurement** the book's own ablation left open would test P5 — is the three-way
gain real when recall is held equal? Each is a study the field knows how to run. This appendix is the set of
hypotheses they would test.

If code is becoming cheap and judgment the scarce thing, then the question that will matter is not whether
agents can generate — we know they can — but which environments make their generation *governable*, and how
to measure the difference. That is the empirical program this book most wants to provoke. The model here is
one entry in it, drawn as plainly as I could draw it, and left where the next person can knock it down.

> See also the prose form of these implications in [Implications for Software Engineering](6.0-implications-for-se.html),
> and the metrics behind every observable in [The Operator's Dashboard](6.4-the-operators-dashboard.html).
