# lexicon.local.md — this catalogue's house dialect (the adopter overlay)

<!-- Adopter-owned local overlay. Composed APPEND-only over `lexicon.md` at read time; a
`bundle_skill.py --refresh` never reads, writes, or deletes this file. Declared in the self-communicate
SKILL.md `## Local adapter` block as the overlay for `writing/lexicon.md`. -->

This is the filled **Your house vocabulary** table for this catalogue (and its parent product, DocAble),
mined by the bootstrap recipe in [`lexicon.md`](lexicon.md) (§"Bootstrap recipe — walk your codebase"). Read
it as an **APPEND** to that file's `## Your house vocabulary` section — the portable base rows stay upstream
in `lexicon.md`; these house-dialect rows are the adopter layer. It doubles as a worked example of a filled
table. The **agent-vs-model** row is governed by the
[disambiguation rule](lexicon.md#the-one-disambiguation-rule--agent-vs-model) near the top of the base file.

| Term | What it means in the house dialect | PORTABLE rename? |
|---|---|---|
| **models-bridge** | The third catalogue role: the typed MBSE substrate that *couples* the agent fleet and the codebase — models the fleet reads to reason and that govern/generate the product. Its **teaching handle** in prose is *"the model bridge"* (the [canonical-term-plus-teaching-handle](lexicon.md#canonical-term-and-teaching-handle-may-coexist) rule): keep `models-bridge` hyphenated in tables/checks/cross-refs, and use "the model bridge" as the recurring memorable phrase. | coinage (renames "MBSE substrate / model layer") |
| **the agent** / **the fleet** | The coding actor(s); the set of concurrent agents the orchestrator dispatches. | coinage over "the LLM / the worker pool" — see the disambiguation rule above |
| **orchestrator** | The main-thread session that composes briefs, dispatches agents, lands their work, and refills slots. | renames "scheduler / coordinator" (portable: *dispatch*, *worker pool* — already in base) |
| **worktree** | An isolated git working directory one agent edits, so concurrent agents don't trample each other. | **already portable-base** (link `git-worktree`) — house usage is identical |
| **dispatch** | Hand a scoped unit of work to an agent to execute. | **already portable-base** — house usage is identical |
| **Epic** | A multi-phase effort tracked as one unit, with a Definition-of-Done. | **already portable-base** (Scrum §Epic) |
| **sentinel** (first-commit early-abort) | The gate that runs the full check suite on an agent's *first* commit, aborting a doomed worktree before it accrues more work. | coinage; renames "fail-fast on first commit" (portable stance: *shift-left*) |
| **merge-train** | The batched-landing mechanism that lands non-conflicting worktrees per tick via MIS batching. | coinage; renames "merge queue / batched integration" (portable: *MIS*, already in base) |
| **tombstone** (commit) | A lifecycle-close record committed at a worktree's tip declaring its disposition (cherry-picked / skipped). | coinage; renames "lifecycle close record" |
| **quiesce** | Bring the fleet to a drained, idle stop — finish in-flight work, accept none new, then stop. | **already portable-base** (link *quiesce*); house usage adds the fleet-wide protocol |
| **reflection-facet** (substrate) | A tempo-gated policy-nudge surface — a registry of soft nudges fired on a cadence at the orchestrator. | coinage; always hyphenated, never "reflection facet" |
| **cron-alerts gate** | A blocking gate that refuses new dispatch while an unresolved HIGH-severity cron alert is open. | coinage (a *gate* keyed on an alert registry) |
| **caused-by provenance** | Agent-side change traceability: every landed change carries who/what dispatched it. | coinage; renames "change provenance / traceability matrix" (portable: *blast radius* neighbours it) |
| **ban-lint** | A lint whose sole job is to make a raw alternative to a sanctioned seam impossible (fails the build on any raw call). | coinage; a specialization of *lint* (portable-base) held against one seam |
| **typed seam** / **sole seam** | The one sanctioned wrapper for a boundary, whose signature makes a bug class unrepresentable. | **already portable-base** (*Typed seam*); house adds "sole" = exactly one, ban-lint-held |
| **canonical walker** | The one sanctioned traversal per tree (PDF/Office struct tree), so a fix applied once holds everywhere. | coinage; renames "single traversal / visitor" (GoF Visitor is the neighbour) |
| **masked pass** | The unified rule-engine architecture: a pass runs over a Model with a verb registry and a mask selecting what it may touch. | coinage (product-internal); renames "scoped transform pass" |
| **drift-parity gates** | Bidirectional model↔reality enforcement: the build fails when a model diverges from the code it describes. | coinage; renames "drift check / consistency gate" (portable: *drift*, already in base). Hyphenate; never "drift/parity". |
| **meta-sync** | The synchronization model: the OS-lock / flock registry + acquisition ordering that serializes the fleet's shared-resource access. | coinage; renames "lock registry + lock ordering" (portable: *flock*, *lock ordering* — in base) |
| **DDT** (doc-derived test) + **pin-trailer** | A test generated from a doc/source, carrying a trailer that pins the cited sources so it regenerates on their edit. | coinage; a specialization of *characterization test* (portable-base) tied to a doc source |
| **test-onion** (tiers) | The layered test suite: Smoke / Lite / targeted / full, each a wider ring run at a different gate. | coinage; renames "test tiers" (portable neighbour: *test pyramid*, *smoke test* — in base) |
| **census** | The one-row-per-mechanism catalogue count, auto-derived and drift-checked (never hand-typed). | coinage (catalogue-internal); a *single source of truth* applied to the entry count |
| **`a11y_` prefix** | The convention that every invisible-to-author inserted artifact starts `a11y_`, so it is enumerable and strippable. | coinage (product-internal) |
| **mutator stamp** | A per-mutator provenance record written into the artifact by each remediation verb. | coinage; a specialization of *provenance / audit trail* |
| **repair vocabulary** / **remediation verbs** | The closed, typed set of moves the remediator may make (closed verb set + `ViolationCategory` enums). | coinage; renames "bounded action space" (portable neighbour: *marker interface* enumerates the set) |
| **soft / hard enforcement** | Soft = probabilistic, aims an agent, can't block; hard = deterministic, holds the line. | **already portable-base** (*Soft vs. hard enforcement*). House writes it **`Soft·Hard`** (middle dot) for the mixed case in metadata cards. |
| **blast radius** | The scope of static-analysis impact if a control's substrate assumption changes — computed, not grepped. | **already portable-base** (*Blast radius*); house sharpens to "computed query" |
