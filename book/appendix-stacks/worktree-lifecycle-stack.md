### Concept

Every agent works in its own isolated checkout, and every checkout has a birth, a life, and a clean
death. The stack is the set of records and gates that keep dozens of concurrent worktrees from
trampling each other and from leaking half-finished state into the trunk. Skip the close records and
the isolation still *starts* correctly — but it never ends cleanly, and stale worktrees accumulate
until a reclaim guesses wrong and destroys live work.

### Mandatory members

- **role:agent-registry** — an append-only log of who is in flight, with a marker-file cache. It is
  the authoritative answer to "is this worktree still alive?" A reclaim that trusts anything else
  eventually races a running agent.
- **role:tombstone-commits** — the lifecycle close record: a commit that marks a worktree finished
  and safe to reclaim. Without it, cleanup cannot tell a done worktree from an abandoned one, so it
  either leaks disk or deletes work.
- **role:pre-commit-hook** — the gate every commit passes on its way out of a worktree. It is what
  keeps an isolated agent from landing a broken tree; the isolation is only safe because the exit is
  guarded.

### Complementary members

- **role:sentinel-first-commit** — an early-abort first commit that fails fast when a worktree is
  mis-configured, before real work accumulates on top of the mistake. Saves wasted effort; the
  lifecycle is still correct if the mistake surfaces later at the pre-commit gate instead.
- **role:merge-train-mis-batching** — batch non-conflicting worktrees so the trunk absorbs many at
  once. A throughput optimization layered on the lifecycle; each worktree can also land one at a
  time.
- **role:build-serializer** — ration shared heavy compute across the concurrent worktrees. Protects
  the host; the lifecycle of any single worktree is correct without it.
