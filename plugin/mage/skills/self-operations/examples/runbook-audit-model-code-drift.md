# Example runbook — audit a typed model against the code it claims

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's model + tools.*

**Lifecycle:** L3 · manage-git-repo — the definition-of-done reading the model to know what drifted.
(Cross-cuts the models-bridge: the model is the thing being audited.)

## Problem (universal)

You govern a context-exceeding codebase *through* a typed model — a set of claims about the code (an
invariant names the routine that enforces it, a state machine names its implementing function, a model
element names the registry it reconciles against). The model is only worth its cost while it equals the
territory. But a closed piece of work can pass a green definition-of-done and still leave the model
**silently drifted**: the code moved and the claim now points at a ghost, or a replacement was built and
the "which one is live" pointer never got repointed. The trap is auditing this by hand under load — you
either re-read the whole model from scratch (slow, and you miss the stale edges) or trust the last green
DoD (which is exactly what let the drift through). The move is to **mechanize the enumeration and the
diff, and reserve human judgment for the one question a machine can't answer: is this a real divergence,
or an intended as-built gap?**

The drift falls into a small, typed set of **layers** — name them so the audit can classify each finding:

- **L1 · anchor-broke** — the claim points at a symbol that no longer resolves (deleted, renamed, moved).
  Purely mechanical to detect.
- **L2 · role-currency** — the symbol still resolves, but no longer plays the role the claim says (a
  checker made stricter than the producer it now rejects; a subsystem retired from the code but still
  present-tense in the model). Detectable by a keyword / present-tense scan; the *verdict* is judgment.
- **L3 · semantic-correctness** — everything resolves and reads current, but does the code actually
  *satisfy* the claim? Irreducibly judgment — **except** for a claim carrying a formal anchor (a
  model-check, a property test), where re-running the checker *is* the L3 verdict.

## Steps (typed)

- **[RUNNABLE] Enumerate the model's claims.** Walk the typed model and pull every claim that points at
  code — invariant → routine, state machine → function, model element → registry — as a flat list of
  `(claim, anchor)` pairs. This is the audit's work-list; do it off the model, never from memory.
  `<your model-element enumeration>` — one row per claim, each carrying its code anchor.
- **[RUNNABLE] Diff each anchor against the code it points at — L1 first.** For every anchor, resolve the
  symbol with a language-aware static resolver (not a line-number lookup — line numbers churn). A symbol
  that fails to resolve is an **L1 anchor-broke** finding, flagged mechanically. Anchor to symbol
  *definitions*, so a claim survives edits above it.
  `<your symbol-resolve over each anchor>` — collect the non-resolving set as L1.
- **[RUNNABLE] Scan the resolving set for L2 role-currency.** For anchors that resolve, run the cheap
  present-tense / keyword pass that flags a claim describing a role the code may no longer play — a
  "retired" subsystem still named present-tense, a stricter-than-producer mismatch. This narrows the
  judgment queue; it does not decide.
  `<your role-currency keyword scan over the resolving set>`
- **[RUNNABLE] Batch-re-run the model's own owned checks.** Re-run every lint / gate the model declares it
  owns and flag any that went **red since the work closed** — a claim the DoD asserted green that has since
  fallen. A red-since-close check is a drift the last green DoD is actively lying about.
  `<your owned-check batch re-run>` — flag each red-since-close.
- **[JUDGMENT-AUTOMATABLE] Classify each surviving finding by layer, and route it.** A carried brief that
  reads the L1 set, the L2 candidates, and the red-since-close set, assigns each a layer, and proposes the
  disposition — *repoint the anchor* (L1), *update the claim's tense/role or the code* (L2), *escalate for
  a semantic call* (L3). It separates a mechanically-certain finding from an inferred one, so the human
  reviews only what actually needs a verdict.
  Carried brief: *"Given these non-resolving anchors, role-currency candidates, and red-since-close checks,
  assign each a drift layer (L1 anchor-broke / L2 role-currency / L3 semantic), propose a disposition, and
  separate mechanically-certain findings from inferred ones."*
- **[JUDGMENT-IRREDUCIBLE] Judge each L3: real divergence, or intended as-built gap?** This is the one step
  a machine can't take. For each claim that resolves and reads current, decide whether the code *satisfies*
  it — and, critically, whether a mismatch is a genuine drift to fix or a **deliberate as-built gap** the
  model should record with a `⚠️` marker rather than treat as an error. A design that never shipped the way
  the model describes is not a bug in the code; it is a note the model owes its readers. Give this your
  strongest model; it is the residual the whole runbook exists to isolate.
- **[RUNNABLE] For a formally-anchored claim, mechanize the L3 — re-run the checker.** Where a claim
  carries a formal anchor (a bounded model-check, an exhaustive state-space search, a property test),
  the semantic verdict is not a human call: re-run the checker and read its result. For that slice, L3
  joins the mechanized zone; everything else stays sample-judged above.
  `<your model-checker / property-test re-run for the formally-anchored claims>`

## Second-order note

The load-bearing lesson is **derived defends; snapshotted drifts.** Every mechanical step above works only
because it *re-reads the territory at audit time* — resolving a live symbol, re-running a live check. The
moment a step reconciles against a hand-maintained list (a frozen trace matrix, a snapshotted enum) instead
of the code, a territory move slips past it silently — which is the exact failure the audit exists to catch,
now hiding *inside* the audit. So when you find drift the audit missed, the fix is not a better hand-list:
convert that check to one that derives its answer from the code. And watch for **pointer drift** as its own
class — a replacement built but the surfaces naming *which implementation is live* left aimed at the retired
one (code routing, the runbook, the agent-context doc, the operator skill, a canonical-command example all
drift together). A cutover must repoint every surface atomically, or it leaves a loaded gun. If this audit
keeps surfacing the same drift class, that recurrence is a self-governance signal: hand the class to the
partner skill and design the derived control (this DoD drift-audit is one such runbook, minted from a real
audit that harvested roughly two dozen drift instances at near-one signal-to-noise across recently-closed
work). Governance is design, not an inline patch.
