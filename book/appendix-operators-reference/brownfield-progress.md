*Where is governance weakest, and where should the next conversion happen?*

Watch the ungoverned surface shrink as the migration runs its four stages, and aim the next stage at the
biggest remaining ungoverned cluster. Weakest is wherever the map still floats beside the code; the next
conversion goes where the largest unmodelled region meets the highest value.

Most readers do not start clean — they start with a legacy codebase and a drifted wiki. The card shows the
migration as a trajectory: ungoverned today, governed over adoption, with the four stages as the track and
one number reading the drain.

Healthy direction: the ungoverned surface drains as subsystems get modeled, and the next stage aims at the
biggest remaining cluster.
*DocAble reference:* 56% → 7.89% over nine passes — one observed run.

### What to read

- **Ungoverned vs governed.** The Missing-Model surface — the fraction of tests whose exercised code traces
  to no model claim — drains as subsystems get modeled. It falls toward an explicitly chosen floor as the
  model loop covers each biggest orphan cluster in turn. The before-and-after bar is this drain.
- **Stage position.** Which of the four stages the migration has reached — Audit, Synchronize, Govern,
  Extend — each a useful stopping point that already pays.
- **Tribal knowledge.** What still lives only in one person's head — the invariants known by reputation. No
  declared measure; an operator glance.

```
  BROWNFIELD PROGRESS         "Where should the next conversion happen?"
  ──────────────────────────────────────────────────────────────────────
  early    Ungoverned ██████████   Governed ██
  now      Ungoverned ██           Governed ████████   (Missing-Model draining)
  ──────────────────────────────────────────────────────────────────────
  Audit ──▶ Synchronize ──▶ [ Govern ] ──▶ Extend        stage track
  Next conversion → biggest remaining ungoverned cluster
  Still tribal: invariants living in one head            convert these
  example reading — the before/after bars show the drain's shape, not your counts
```

### The soft-gap read

**Tribal knowledge** — invariants that live only in one head — has no declared measure. Read it green /
yellow / red: green when the load-bearing invariants are modeled and linked, red when the system is still
known by reputation. No fabricated count.

### What this projects

The Brownfield chapter's four stages, each a useful stopping point ([Chapter 4.1](4.1-brownfield.html)); the
Missing-Model Metric (the ungoverned-vs-governed drain); the shipped From-Drifted-Wiki-to-Trusted-Model
operator card; and the chapter's Sizing Matrix, which picks the next mechanism by cost times frequency.
"Where next" is the Missing-Model's own steering rule: aim the next model-loop effort at the biggest orphan
cluster it surfaces.
