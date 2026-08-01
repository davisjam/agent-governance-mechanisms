<!--
  Design-doc template — STARTER (adopt & adapt)

  A distilled, portable version of the design-doc conventions from a production system built by
  frontier coding agents. A design doc is the Phase-1 artifact of an Epic (see the Epic starter): it
  is where you encode the DESIGN and its INVARIANTS before any implementation dispatches — so the doc
  *drives* the work and later *drives the test backlog*, rather than being written after the fact.

  The load-bearing idea: a design doc earns its keep through four elements — (1) a section per real
  part, (2) invariants with stable IDs, (3) as-built-vs-design marks, (4) an enforcement map from
  invariants to tests. A doc without them is prose that rots. Replace the bracketed placeholders;
  keep the section contract.
-->

# Design: <subsystem / change> — <one-line intent>

**Status:** draft | ratified | as-built | DECISION-RECORD | ✅ <verdict>
**Author:** <who> · **Created:** <date> · **Epic:** <link, if any>

> Keep the Status line honest through the whole lifecycle. When the change lands, restamp: replace
> "draft / NOT SAFE / deferred" language with the landing outcome (`as-built` or `DECISION-RECORD`),
> preserving the original reasoning as clearly-flagged history. A design doc that still says "pending"
> weeks after it shipped is the single most common doc-rot failure.

## §1 Context & the failure it kills

The problem in one paragraph, then: what breaks today (or will), how often, and how expensive each
occurrence is. State the **essential** complexity (inherent to the problem) separately from the
**accidental** complexity (introduced by current tooling/choices) — the design should attack the
accidental kind and *budget* for the essential kind, not pretend a cleverer abstraction erases it.

## §2 Genre check (before you invent)

Before proposing a new abstraction / schema / tool: (1) what **genre** is this? (2) who is the
canonical best-in-class? (3) can you **adopt their schema** even if you skip their runtime? Prefer a
single source of truth: a stable check that reads a meta-file at build time beats codegen-from-spec
beats N hand-rolled copies. Record the alternatives you considered and why you rejected them — a
design doc with no rejected alternatives usually didn't look for them.

When two candidates clear the genre check, weigh **training-data density** as a tiebreaker: agents
produce more reliable output for a widely-adopted mainstream tool than for a niche one, which is
out-of-distribution and gets re-derived (and mis-derived) by every future agent. A heuristic, not a
mandate — record it as one factor among capability, fit, licensing, and uniformity.

## §3 The design

One subsection **per real part** — one heading (or table row) per source, stage, module, service, or
entity, mirroring the actual structure of the thing. Name shapes with types: types reveal the
architecture that primitive-passing leaves anonymous. Prefer one canonical seam per concern (a single
sanctioned way to do X), and make illegal states unrepresentable where you can (a typed model beats a
runtime guard).

## §4 Invariants (the join key)

Each invariant is a **tagged, testable predicate** with a stable ID and a `file:line` (or module)
cite. The ID is what tests and audits cite back — it is the join key between the doc and the code.

| ID | Invariant (a predicate that is true or false) | Where it lives (`file:line`) |
|----|-----------------------------------------------|------------------------------|
| INV-1 | <e.g. every job transition goes through the state machine — no ad-hoc status writes> | `<cite>` |
| INV-2 | <e.g. every emitted file carries a provenance header> | `<cite>` |

## §5 Second-order effects & dynamics

**Mandatory for any substrate with repetition, concurrency, or time-delayed consumption.** A
first-order design ("when X happens, do Y") is often right in isolation but pathological under
repetition or contention. Walk the dynamics explicitly:

- **Over time** — what happens at tick T+1, T+10, T+100? Does anything accumulate, starve, or oscillate?
- **Under concurrency** — what if N components do this simultaneously? Is there a race, a deadlock (an inverted lock-acquisition order), a thundering herd?
- **Under stale state** — what if state drifts between when it's produced and when it's consumed (a stale base, a retried cron tick, a cached snapshot)?

Dynamics-aimed tests find the real defects; a strong-but-static unit suite will miss driving-condition
bugs. Name the dynamics you're relying on, and the ones you're ruling out.

## §6 Observability

**Required for any substrate that emits events / topics.** For each signal: the topic name, what
"baseline healthy" looks like, what "something's wrong" looks like, and where the operator goes when it
fires (the playbook entry). A substrate you can't observe end-to-end is an incomplete design.

## §7 As-built vs. design (⚠️ the gaps are the next work)

Call out, with ⚠️, every place the shipped code diverges from this design — a deferred invariant, a
stubbed path, a "for now" shortcut. The ⚠️ marks are where the next work lives; an as-built doc with
none is usually hiding drift, not free of it.

## §8 Enforcement — invariants → tests/lints

Map **each invariant ID** to the test or lint that pins it, or mark it `UNTESTED`. This table *is* the
test backlog the doc drives.

| Invariant | Enforced by | Kind | Status |
|-----------|-------------|------|--------|
| INV-1 | `<test/lint>` | pin / property / lint | ✅ / UNTESTED |
| INV-2 | `<test/lint>` | lint | ✅ / UNTESTED |

Prefer converting a recurring manual audit into a **lint** whenever the signal is mechanically
detectable: audit signals are expensive, deferrable, and post-hoc; lint signals are cheap, at-commit,
and deterministic. Today's audit finding is tomorrow's lint.

## §9 (Optional) Open questions for the user

Park unresolved judgment-class decisions here for ratification before implementation dispatches — the
load-bearing calls (a naming seam, a scope boundary, a design axis) belong to the user, not to a
sub-agent that would silently answer a narrower question.
