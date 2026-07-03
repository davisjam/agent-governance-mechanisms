# Epic Definition-of-Done (Final-Opus trust-nothing re-run)

**Intent** — An Epic-close gate mandating a "trust nothing" Final-Opus review that re-runs every owned
pin test and lint *at HEAD* — rather than trusting phase markers or prior claims — so an Epic cannot
close on stale or rotted assertions.

| | |
|---|---|
| Summary | Close an Epic only after re-running its checks at HEAD. |
| Target | Agent · **Governance-doc controls** |
| Form | `quality-gate` |
| Enforcement | **Hard** (deterministic) · *blocking close* — reachability/patch-id checks must pass, or a logged `--override` is required |

## Motivation — the failure it kills

An Epic spanning many dispatches accumulates *claims* — phase markers, "lints pass," pin-test counts —
and those claims **rot** as sibling Epic sweeps churn the substrate underneath them. Close on the stale
claims and you ship an Epic whose defenses no longer actually hold (empirically: 7/7 back-catalogue
Epics self-marked DONE had quality-of-defense gaps). The failure is *a premature/false close*, and it
recurs at every Epic boundary.

## Why it's not just "trust the phase markers" (or "the agent said it's done")

Phase markers and self-reports are **exactly what rots**: a sibling sweep can break your lint while your
marker still reads green, and a self-marked-DONE is not verification. The DoD mandates **re-running
every owned pin test and lint at HEAD** and comparing against the claims, plus scanning the Epic's
design docs for dropped `[DESIGN]`/`[LINT]` follow-ups and doc rot. The distinction is *trust-nothing
re-verification at HEAD* versus *trusting recorded claims*. It is the **audit counterpart** to the rule
index: the index's lints keep its *form* honest; this re-run keeps an Epic's *claims* honest.

## Mechanism

An Epic-close tool enforces that every cited commit is reachable from main by ancestry or patch-id (a
missing one requires a logged `--override '<reason ≥30 chars>'`); it rewrites Status + Closed
atomically, moves the file to `closed/`, and regenerates the index. The §4 DoD carries 11 mandatory
criteria — including the Final-Opus re-run of owned pins/lints at HEAD, docs + index updates, the tag
routing-audit, and design-doc follow-up filing.

## Prerequisites

- **A machine-checkable close** (reachability / patch-id over the cited commits).
- **A well-defined "owned" set** of pin tests and lints per Epic to re-run.
- **A Final-Opus reviewer** with the judgment to re-verify rather than rubber-stamp.
- **A follow-up routing mechanism** so what the re-run surfaces becomes filed work, not a footnote.

## Consequences & costs

- **The re-run is expensive.** Opus time plus a full pass of owned pins/lints at close — deliberately
  heavyweight, because a false close is worse.
- **`--override` is a hole.** It exists for legitimately-unreachable commits, logged — but it is a way
  past the reachability check.
- **"Owned" must be accurate.** An Epic that under-declares what it owns re-runs too little and can
  still close on a rotted-but-unlisted defense.

## Known uses

- `epic_close.py close --commits …` / `--override` (reachability-gated close).
- The Epic template §4 11-criterion DoD; the Final-Opus "trust nothing" re-run.
- The tag routing-audit + design-doc follow-up filing at close.

## Related controls

- **Counterpart (audit)** — [claude-md-rule-index](claude-md-rule-index.md): the index's cap/conformance
  lints keep its *form* honest; this re-run keeps *claims* honest (presence ≠ obedience). Together they
  are the "keep the enforced documents honest" pair.
- **Consumer** — reads each Epic's owned pin tests and lints (and the repo meta-models behind them) to
  re-verify at HEAD.
