*A flagship deep-dive: the observe → react loop, walked part by part. The worst failure mode of an agent
fleet is a pipeline that runs but produces garbage — invisible until much later. This stack makes live
state legible and every bad state actionable, so an operator drives from typed signals plus written
responses rather than from scraped logs and memory. This page folds in what used to be the separate
observability and self-operations stacks — the signal side and the self-operate component.*

## The goal

**Make the fleet's live state legible and every bad state actionable.** Emitting signals is only half of
it: a signal nobody knows how to answer is noise, and a procedure with no signal to trigger it never runs.
So the loop pairs a typed signal surface with a liveness channel, a written response per signal, a gate
that stops new work while a serious signal is unresolved, and a positive map of the substrate that makes
the signals interpretable. An operator — human or agent — then reacts to structure, not to text.

<!-- label: observe-react-stack -->
<!-- figure: assets/observe-react-stack.svg | The observe → react loop in one picture. Five parts run left to right. Observe (fleet blue): WATCH is the typed event bus every substrate emits onto; BEAT is the liveness channel that tells a hung process from a slow one. React (green): RESPOND is a written playbook per signal. Block (churn red): BLOCK refuses new work-dispatch while a high-severity alert is unresolved. Self-operate (accent): OPERATE is the positive map of how the substrate works. The bus says what happened; the playbook says what to do; the gate refuses to proceed until it is cleared; the map makes every signal interpretable. -->

## How the parts interlock

The loop runs from a signal to a cleared state. **WATCH** is the one surface every substrate emits onto, so
health is read, not scraped. **BEAT** rides that bus as its liveness channel — the difference between "still
working" and "wedged." **RESPOND** is the counterpart to WATCH: the bus says *what happened*, the playbook
says *what to do*. **BLOCK** raises the cost of ignoring a serious signal from zero to blocking, refusing new
work until the alert is cleared. **OPERATE** gives the operator the standing map that makes all of it
interpretable — self-operation from a model of the substrate, not from memory. Read the parts in that order;
each seam names what the part before it hands over.

## The parts

### 1. WATCH — the typed event bus

- **Part** — role:typed-event-bus
- **Role in the stack** — A typed event bus with a closed topic registry that every substrate emits its
  lifecycle and health facts onto, turning the orchestrator into a reactor over one signal surface.
- **Failure it retires** — Fleet state is scraped from a dozen logs in different shapes; the operator learns
  of a bad state late, by reading, and reacts to text rather than to structure.
- **Mechanism** — Every substrate emits named events onto one typed bus with a const-string topic registry,
  so health is read from a queryable, self-documenting surface and each event dispatches on structure, not
  scraped text.
- **The seam** — Opens the loop. It is the single surface the rest of the stack reads: the heartbeat rides
  it, the playbook is keyed to its topics, the alerts-gate blocks on its high-severity events. Everything
  downstream reacts to what the bus says.
- **Limits / durability** — Durable — a typed signal bus is standard operational infrastructure, and the
  closed topic registry keeps a typo from silently disabling a signal. Its cost is one emit per lifecycle
  fact; it is only as legible as the topics substrates remember to emit.

### 2. BEAT — the liveness channel (folded from the observability stack)

- **Part** — role:deploy-heartbeats
- **Role in the stack** — Periodic liveness emissions from long-running work, plus a stale-worker sweep, so
  a *hung* process is distinguishable from a merely *slow* one.
- **Failure it retires** — A long deploy goes silent; the operator cannot tell a wedged process from one
  grinding through a slow phase, so a hang is discovered only by a timeout much later.
- **Mechanism** — A long-running process emits a periodic heartbeat carrying its phase and elapsed time, and
  a sweep flags a worker that has stopped beating — silence becomes a signal, not an ambiguity.
- **The seam** — Rides the WATCH bus as its liveness channel. It sharpens the observed picture the playbook
  responds to: the difference between "still working" and "wedged" is exactly what tells the operator
  whether to wait or to act.
- **Limits / durability** — Durable — a periodic beat is cheap and model-independent. It is complementary,
  not load-bearing: the see-and-respond loop functions without per-phase beats, but a long pipeline is far
  more legible with them.

### 3. RESPOND — a playbook per signal

- **Part** — role:operational-playbooks
- **Role in the stack** — A written decision procedure per situation the signals surface: symptom → steps in
  order.
- **Failure it retires** — A signal fires a red state but says nothing about what to do; the operator
  re-reasons the response from scratch each time, inconsistently, under incident pressure.
- **Mechanism** — A library of documented, incident-tested procedures — when situation X arises, take these
  steps in this order — that agents and orchestrators consult instead of reasoning from zero.
- **The seam** — The counterpart to WATCH. The bus says *what happened*; the playbook says *what to do* —
  neither half is useful alone. A signal keyed to no playbook is unactioned noise; a playbook with no signal
  to trigger it never runs.
- **Limits / durability** — Durable — a pre-reasoned procedure is model-independent and gets better each
  incident. Its cost is writing and maintaining the procedures; it decays only where a signal's playbook is
  never written, leaving that signal at noticing without acting.

### 4. BLOCK — the alerts gate

- **Part** — role:cron-alerts-gate
- **Role in the stack** — While an unresolved HIGH-severity alert stands, refuse new orchestrator
  work-dispatch until it is acknowledged or resolved.
- **Failure it retires** — A high-severity alert fires and the operator keeps piling new work onto a
  possibly-broken substrate, compounding the failure it should have stopped to fix.
- **Mechanism** — A gate reads the bus's unresolved high-severity alerts and blocks the dispatch,
  worktree-create, and merge tools until the alert carries a matching ack or resolve.
- **The seam** — Raises the cost of ignoring a WATCH signal from zero to blocking. It sits over the bus and
  the playbook: the alert names the problem, the playbook says how to clear it, and the gate refuses to let
  the fleet proceed until one or the other is done.
- **Limits / durability** — Durable — a deterministic gate over unresolved alerts does not decay. Its cost
  is the discipline of ack-or-resolve; it is designed deadlock-free so a broken substrate can always be
  cleared, and it degrades to noise only if alerts are acked without being fixed.

### 5. OPERATE — the positive substrate map (folded from the self-operations stack)

- **Part** — role:operator-runbook-skill
- **Role in the stack** — A loadable skill giving an operating agent the *positive* map of how the substrate
  works first, and a symptom → resolving-doc catalog as the fallback.
- **Failure it retires** — An operating agent knows the symptom index but not how the substrate is *supposed*
  to work, so it treats symptoms without a model and mis-operates the fleet it is meant to run.
- **Mechanism** — A skill that leads with the substrate's lifecycles and healthy baselines and falls back to
  a symptom → doc catalog, generated from a typed source-of-truth so a reference-validity lint keeps every
  pointer honest.
- **The seam** — Closes the loop. Where WATCH and BEAT show state and RESPOND and BLOCK handle each bad one,
  this gives the operator the standing map that makes the signals *interpretable* — self-operation from a
  model of the substrate, not from memory.
- **Limits / durability** — Durable — a positive operating map is model-independent and its pointers are
  lint-checked against the source of truth. Its cost is generating and maintaining the skill; it speeds
  recovery, but the react-and-follow loop still functions without it.
