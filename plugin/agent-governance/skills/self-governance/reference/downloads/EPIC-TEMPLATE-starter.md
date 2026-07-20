<!--
  Epic template — STARTER (adopt & adapt)

  A distilled, portable version of the Epic template from a production system built by
  frontier coding agents. An "Epic" is a multi-dispatch effort — anything too large for one
  agent run, planned once and executed over several dispatches. This file ships the *shape*
  and the definition-of-done; strip nothing load-bearing, add what your substrate needs, and
  replace the bracketed placeholders. Nothing here is framework-specific — it is a section
  contract for a planning artifact.

  It pairs with the "Epic & design-doc templates" mechanism in the catalogue (the WHY) and the
  design-doc starter (its sibling artifact).
-->

# Epic: <name> — <one-line scope>

**Status:** queued | active | blocked-user | blocked-<other-epic> | paused | ✅ DONE
**Dispatch posture:** dispatch-ready | gated on <epic/phase> | dispatch-after-<event>
**Owner:** <who>
**Created:** <date>
**Closed:** <date — only when Status = ✅ DONE>

> Status tokens: `queued` = designed, not dispatched · `active` = a phase in flight or recently
> landed · `blocked-*` = needs a decision or a sibling milestone · `paused` = deferred (cite why) ·
> `✅ DONE` = definition-of-done all green **and** the final independent review signed off.
> An `active` Epic with some phases done keeps a qualifier ("Phases 1–3 done; 4–5 dispatchable") so
> "intermediate" is never confused with "terminal."

## §1 Rationale (the WHY)

The reader must be able to re-derive "is this worth funding?" from this section alone. Answer:

1. **What invariant or capability is missing today?**
2. **What is the cost of NOT doing it?** (A real bug class? A maintenance tax? Audit overhead? Risk to a specific contract/customer/SLO?)
3. **Why now?** What changed to make this load-bearing now rather than three months ago?
4. **What's the leverage?** One-fix-vs-one-class? Does it unblock N downstream efforts? Does it gate a release stage?
5. **What would tell us we picked the wrong shape?** — a failure mode you can detect early.
6. **Empirical check recipe.** The concrete, runnable verification for this Epic's invariants, written *now* so the final reviewer doesn't have to invent it. E.g. "`grep -E <pattern>` across `<dir>` returns 0"; "`<lint>` exits 0"; "`<test>` pins the invariant — run it."

## §2 Cost calibration

- Per-phase estimate (agent-hours/days) + total.
- Confidence band (a wide band means Phase 1's design must narrow it).
- Risk factors that could blow the estimate (rebase contention, schema drift, vendor-flag interactions…).
- **If the estimate exceeds a few agent-days, it needs sub-phases and a checkpoint after Phase 1.**

## §3 Phases

**Phase 1 is ALWAYS planning/design** — read-only investigation + a design doc (see the design-doc
starter) + user ratification of judgment-class questions. Never dispatch implementation speculatively;
restructuring after a wrong design costs multiples of re-running Phase 1.

**Phase 1 MUST explicitly consider tooling** before planning any per-site agent sweep. Ask: would a
**one-off codemod** (an AST transformer that rewrites N≳50 sites mechanically, then is deleted — the
lint that prevents recurrence is the lasting defense) or a **permanent tool** (a mediator / generator /
enforcer the codebase keeps running) make this faster, deterministic, and easier to verify? If neither
— per-site judgment, small count, or semantic-not-syntactic change — an agent sweep is correct. If you
pick a tool: build it self-documenting (`--help` + verbose "found / changed / skipped-why"), validate it
on ≥2 real files before adopting it, ship it as part of Phase 1, and make Phase 2 "run the tool," not a
batch dispatch.

Per phase:

```
- [ ] Phase N — <name> (~<estimate>). <one-paragraph scope>.
      Acceptance: <the specific, testable criterion that means done>.
      Prereqs: <preceding phases / user gates / sibling milestones>.
```

**Canary-until-quiet** (for "new substrate + N adopters" efforts): don't plan the parallel migration
wave as the step after the first canary. Migrate one consumer that exercises facet A; fix the substrate
for what it surfaced; migrate a *deliberately different* facet B; loop. Gate the parallel wave on
"the most-recent canary surfaced 0 new design findings" — not on a fixed canary count. Each canary must
probe a different region of the risk surface; a repeated canary yields no new information.

## §4 Definition of done (DoD)

An Epic does **not** close until every criterion is green — even if "the code works."

1. **Functional invariants in place.** The capability/invariant is shipped, tested, and verifiable.
1b. **Numeric claims re-verified.** Every number in the Epic ("N sites migrated," "K→L delta," "P bugs caught") is re-counted at close; drift is documented or the claims corrected.
2. **Docs updated.** Every doc the Epic produced or invalidated is committed; stale docs are updated or deleted; the doc index reflects new docs.
2c. **Higher-layer models/registries updated.** Any new code surface is reflected in the maps orchestrators and reviewers navigate by (component/ownership registry, service/flow model, etc.) — not only the doc index. Decline only with an explicit "no map drift — <reason>."
3. **Lints authored/extended for class-level invariants — RUN FRESH at close.** If the Epic encoded a structural rule (X relates to Y), a lint defends it forward; if no lint is feasible, the review says why. **Run the lint(s) fresh (exit 0) — do not merely confirm the file exists and is wired in.** A gate can go red silently hours after it ships clean.
3a. **ALL blocking gates green at close — not just the Epic's own.** Run the full gate sweep end-to-end; a sibling change can have introduced a regression the gate correctly catches that no one ran.
4. **Tests cover the invariants.** Seam tests (module boundaries the Epic moved), pin tests (the specific behavior the invariants imply — a state-machine table, a lint's findings on synthetic fixtures), and property-based tests where an invariant quantifies over an input space. Quality is "would this catch the bug class the Epic exists to prevent?" — not test count.
5. **Final independent review (the closer).** A read-only review agent (a strong model — trust nothing at HEAD) checks criteria 1–4, reads the design doc + recent commits, and grep/re-runs to verify the invariant holds in current code. It posts a verdict and **routes every regression it surfaces with a tag** ([FIX] / [LINT] / [DESIGN]) to a queue — "list regressions" without routing is half a review. Only then does Status flip to ✅ DONE.
5a. **Routing-completeness audit.** The reviewer enumerates every tagged follow-up across the Epic's agent reports and confirms each was routed or resolved — nothing dropped on the floor.

## §5 Cross-references · §6 Dispatch posture · §7 (optional) open user questions · §8 (optional) reconcile log

Link the design doc, parent/sibling Epics, and the lints/tests this Epic ships. Record the dispatch
dependency order (which phase unblocks which). Park unresolved judgment-class questions for the user in §7.

## Anti-patterns (what an Epic must NOT look like)

- **No rationale** — "we're doing X" without "because Y, leveraging Z." Future-self can't re-derive the funding call.
- **No Phase 1** — jumping straight to "implement." Even a one-day Epic earns 30 minutes of read-only investigation + a verdict.
- **DoD missing the lint criterion** — most Epics encode *some* invariant; "we didn't think to add a lint" is usually wrong. Default to proposing one.
- **DoD missing the independent sign-off** — self-marking ✅ DONE is how silent regressions slip through. The review is cheap and catches "we forgot the related test" / "the lint isn't scanning the dir it claims."
- **Phases without acceptance criteria** — "clean up X" is fuzzy; "clean up X; acceptance: `grep … | wc -l` returns 0" is testable.
- **Referencing a doc that isn't authored yet** — make "Phase 1 authors `<design-doc>`" the acceptance instead.

## Worked example (genericised)

> **Epic: inline-script extraction — make one page's logic lint-scannable.**
> Status=queued · gated on the layout refactor · Created=<date>.
> **§1** A page carries ~1,200 LoC of inline `<script>` outside the layer-boundary lint's scan tree, so
> the architecture lint can't fire on it. Cost of not doing: a permanent two-mental-model tax + the lint
> stays advisory. **§2** ~3 agent-days, ±1. **§3** P1 design + user Qs → P2 skeleton → P3 model → P4 view
> → P5 controller → P6 finalize → P7 promote the lint to blocking. **§4 DoD** inline `<script>` ≤ 20 LoC;
> the page classified under the model/view/controller seams; the lint blocking and green; seam tests pass;
> independent review signed off.
