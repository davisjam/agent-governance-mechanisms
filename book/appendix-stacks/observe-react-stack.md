*A two-page synthesis of the observe → react loop. Five patterns make the fleet's live state legible and
every bad state actionable, so an operator — human or agent — drives from typed signals plus written
responses instead of scraping logs and reasoning from memory.*

## The capability

**Turn a running-but-wrong pipeline — the worst failure because it is invisible — into a named signal and a
procedure that answers it.** The stack makes two capabilities: *manage work, state, and resources*, and
*govern the control estate itself*. Every substrate emits its health onto one typed surface; a written
procedure answers each signal; a gate refuses new work while a serious one stands unresolved; and a standing
map makes every signal interpretable. The operator reacts to structure, not to scraped text.

## Failure classes it covers

- **The scraped state.** Fleet health lives in a dozen logs in different shapes; the operator learns of a bad
  state late, by reading, and reacts to text rather than to structure.
- **The silent long-runner.** A deploy goes quiet; nothing distinguishes a wedged process from one grinding
  through a slow phase, so a hang is found only by a timeout much later.
- **The signal with no response.** A red state fires but says nothing about what to do; the operator
  re-reasons the response from scratch each time, inconsistently, under incident pressure.
- **The ignored alarm.** A high-severity alert fires and the operator keeps piling new work onto a
  possibly-broken substrate, compounding the failure it should have stopped to fix.
- **The symptom without a model.** An operating agent knows the symptom index but not how the substrate is
  *supposed* to work, so it treats symptoms without a model and mis-operates the fleet.

## Composition

<!-- label: observe-react-stack -->
<!-- figure: assets/observe-react-stack.svg | The observe → react loop in one picture. Five parts run left to right. Observe (fleet blue): WATCH is the typed event bus every substrate emits onto; BEAT is the liveness channel that tells a hung process from a slow one. React (green): RESPOND is a written playbook per signal. Block (churn red): BLOCK refuses new work-dispatch while a high-severity alert is unresolved. Self-operate (accent): OPERATE is the positive map of how the substrate works. The bus says what happened; the playbook says what to do; the gate refuses to proceed until it is cleared; the map makes every signal interpretable. -->

Two parts observe, two react, one gives the operator the standing map. The bus is the single surface the
rest of the loop reads.

## The constituent patterns

- **WATCH — role:typed-event-bus.** A typed event bus with a closed topic registry that every substrate
  emits its lifecycle and health facts onto, so health is read from a queryable, self-documenting surface and
  each event dispatches on structure, not scraped text. Opens the loop; everything downstream reacts to what
  it says.
- **BEAT — role:deploy-heartbeats.** Periodic liveness emissions from long-running work, plus a stale-worker
  sweep, so a hung process is distinguishable from a merely slow one. Silence becomes a signal, not an
  ambiguity.
- **RESPOND — role:operational-playbooks.** A written decision procedure per situation the signals surface:
  symptom → steps in order. The counterpart to WATCH — the bus says *what happened*, the playbook says *what
  to do*.
- **BLOCK — role:cron-alerts-gate.** While an unresolved high-severity alert stands, refuse new orchestrator
  work-dispatch until it is acknowledged or resolved. It raises the cost of ignoring a signal from zero to
  blocking, and is designed deadlock-free so a broken substrate can always be cleared.
- **OPERATE — role:operator-runbook-skill.** A loadable skill that leads with the substrate's lifecycles and
  healthy baselines — the *positive* map — and falls back to a symptom → doc catalog, its pointers held
  honest by a reference-validity lint. It makes the signals interpretable.

## A DocAble example, end to end

A DocAble deploy runs long. Historically it would go silent and an operator could not tell a wedged build
from a slow one. Now every substrate — deploy, cron, merge-train — emits onto **WATCH**, the one typed bus,
and the long-running deploy emits a **BEAT** every interval carrying its phase and elapsed time; a sweep
flags a worker that stops beating. When a merge-train tick fails, the event is not a log line to grep but a
typed alert on the bus, keyed to a **RESPOND** playbook that names the recovery steps in order. If that
alert is high-severity, **BLOCK** refuses the next dispatch, worktree-create, and merge until someone acks or
resolves it — so the fleet cannot pile new work onto a broken substrate. And an agent asked to operate the
repo loads **OPERATE** first: it reads how the substrate is supposed to work before it touches a symptom, so
it drives from a model of the fleet rather than from memory.

## Tradeoffs and adoption order

1. **WATCH is the floor.** Without one typed signal surface the rest of the loop has nothing to read. Its
   cost is one emit per lifecycle fact; the closed topic registry keeps a typo from silently disabling a
   signal.
2. **RESPOND pairs with it.** Neither half is useful alone — a signal keyed to no playbook is unactioned
   noise, a playbook with no signal never runs. Adopt them together.
3. **BLOCK when ignoring a signal is expensive.** A deterministic gate over unresolved alerts; it degrades to
   noise only if alerts are acked without being fixed.
4. **BEAT and OPERATE are complementary.** The loop functions without per-phase heartbeats or the operating
   map, but a long pipeline is far more legible with beats, and recovery is faster with the map. Add them
   where the substrate is long-running or agent-operated.

## The full treatment

Each constituent links to its full pattern — in this appendix for the flagship members, online for the rest.
The loop consumes the [specification + verification stack](appendix-d-specification-verification-stack.html)
(a proven invariant still needs a live signal when it breaks) and feeds the
[governance-of-governance stack](appendix-d-governance-of-governance-stack.html) (the estate that governs the
controls themselves). The full 83-mechanism catalogue is online in the web edition.
