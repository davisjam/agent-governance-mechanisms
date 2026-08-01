# Example runbook — convert a recurring failure into a control

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's tools.*

**Lifecycle:** L6 · govern-your-own-loop — the seam where *operate* hands a class to *harden*.

## Problem (universal)

The same break keeps coming back. You already fixed the instance once (maybe twice), yet it recurs — a
cherry-pick that keeps false-rejecting, a lint that keeps mis-firing, a manual cleanup step you keep
re-doing. Re-patching the instance a third time is the failure this runbook exists to catch. When a failure
*recurs*, the operate skill's job is to route the **class** — not the instance — to the partner
[`self-governance`](../../self-governance/SKILL.md) skill, which classifies it and mints a durable control.
This runbook is the typed hand-off between the two.

## Steps (typed)

- **[RUNNABLE] Confirm genuine recurrence.** Pull the history of this failure class before minting anything —
  a control built for a one-off is the tower-of-governance trap. Query how many times the same class has
  surfaced (an event-bus / log query keyed on the failure signature, or your incident record).
  `<your event/history query> <failure-class>` → count + the distinct sites it hit.
- **[JUDGMENT-IRREDUCIBLE] Apply the recurrence gate.** Is this a *class* or a *one-off*? Convert only when it
  has recurred, is structurally certain to recur across N sites (the "second site, not the third" signal), or
  *happened once but was costly enough that once is the recurrence*. A benign one-off: fix it, note it, stop —
  do not manufacture a control. (This is the partner skill's gate; you are just deciding whether to invoke it.)
- **[JUDGMENT-AUTOMATABLE] Hand the class to the hardening sibling.** Dispatch a carried brief that runs the
  partner skill's INTERPRET-FAILURE beats over *this* class: the **move question** (a failure to *prevent* →
  a constraint, or to *detect* → a sensor?), the nearest existing control, the hard-vs-soft form, and a
  second-order + compose-check against what already fires on the same event/resource.
  Carried brief: *"Given this recurring failure class and its sites, classify it (constraint vs sensor;
  hard vs soft; which lifecycle/target), name the nearest existing control, and propose the smallest sound
  durable control that kills the class — plus any open design forks."*
- **[JUDGMENT-IRREDUCIBLE] Design it as a first-class artifact, not an inline hack.** A control is a design
  decision. When it warrants it, author the design/Epic from the [`templates/`](../templates/) starters so
  the ratification lands *committed in the doc*, and surface the open design forks to the human — never bury
  a load-bearing seam choice inside the fix.
- **[RUNNABLE] On greenlight, build + register it.** Write the lint / test / gate / typed-seam and the point
  fix. If your operator loop carries a hook substrate, the new control lands as a *registration* there so it
  is visible in your governance census, not wired ad-hoc.
  `<your build/verify command>` · `<register the control in your hook/lint registry>`
- **[JUDGMENT-IRREDUCIBLE] State enforced vs recommended.** Say plainly what is now **enforced** (the hard
  control you wrote and verified) versus **recommended** (anything left for a human/harness to wire — e.g.
  registering the lint in a blocking gate). Do not overstate enforcement.

## Second-order note

This runbook is where the two skills physically meet: *operate* detects the recurrence, *harden* mints the
control, and the control re-enters *this* skill's substrate as something you now run. If you find yourself
running this runbook against the *same* class more than once, the miss is upstream — the earlier control was
too soft, or watched a signal that wasn't there. That is itself a self-governance signal: a soft control with
telemetry showing repeated firings-then-recurrence is a promotion candidate (soft → hard).
