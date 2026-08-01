# Example runbook — query the caused-by mix

*A worked runbook. Keep the shape: a **problem statement** (universal), then **typed steps** (RUNNABLE /
JUDGMENT-AUTOMATABLE / JUDGMENT-IRREDUCIBLE). Swap the illustrative commands for this repo's tools.*

**Lifecycle:** (cross-cuts every lifecycle) — the operating half of caused-by provenance.

## Problem (universal)

Every agent change is stamped with the reason that caused it — a typed `caused-by` cause carried on the
change (the `caused-by-provenance` mechanism). That trace is only worth its cost if you *read* it: now decide
whether a given control or reflection facet is earning its keep — a facet that fires but changes nothing is
noise you should pull. The trap is turning a health signal into a target and gaming it. Read the mix; never
optimize it.

## Steps (typed)

- **[RUNNABLE] Query the mix and the yield.** Pull the caused-by distribution per cause-class, and the yield
  — how often a control's firing actually *preceded* the change it aimed for. Keep a deterministic cause-key
  join separate from a `_proxy`-labeled inference: a proxy cause is a guess, and mixing the two hides which
  numbers you can trust.
  `<your caused-by mix query, per cause-class, with yield and proxy-vs-exact split>`
- **[JUDGMENT-AUTOMATABLE] Decide which facets to pull.** A carried brief that reads the mix and flags any
  control or reflection facet that fires but never *precedes* a real downstream action — noise, by definition.
  Its recommendation is concrete: set that facet's kill switch and remove it.
  Carried brief: *"Given this caused-by mix, name each facet whose firing never preceded the change it aimed
  for; recommend its kill switch, and separate exact-join evidence from `_proxy`-labeled inference."*
- **[JUDGMENT-IRREDUCIBLE] Honor the no-reward discipline.** The mix is a health signal you *read*, never a
  rate you optimize — this is the mechanism's own guard against gaming (*no reward for a rate*, held by the
  measured-leash on the trace). A rising or falling number is neither good nor bad on its own; investigate
  the cause, don't chase the number. A facet whose only value would be moving this metric is exactly the
  facet to pull.

## Second-order note

The two guards on the trace are what keep this query honest: *no reward for a rate* (so the mix stays a
diagnostic, not a scoreboard) and the `_proxy` suffix on an inferred cause (so a guessed cause never
masquerades as a measured one). Read against both — trust the exact-join yield, discount the proxy share, and
treat any pressure to *improve the mix* as the smell it is.
