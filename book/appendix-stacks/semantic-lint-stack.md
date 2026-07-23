### Concept

Move a recurring judgment out of review and into a deterministic check that fires at commit time.
The stack is what turns "an agent keeps re-introducing this class of mistake" into "the class is now
impossible to commit." It has two parts that must travel together: the check itself, and the
discipline of writing the check at the *level where the invariant actually lives* — not one level too
shallow, where it fires on syntax and misses meaning.

### Mandatory members

- **role:semantic-lints** — a blocking check that reads structure and rejects a violation, not a
  regex over surface text. This is the enforcement muscle: without it the invariant is only a
  convention, and conventions decay under a fleet.
- **role:semantic-level-enforcement** — the discipline of enforcing at the right semantic level. A
  lint aimed one level too low passes on a spec-legal variation it should have caught and fires on a
  legal one it should have allowed. The check is only as good as the level it targets, so choosing
  the level is not optional polish — it is what makes the check correct.

### Complementary members

- **role:claude-md-rule-index** — a terse index of the standing rules the lints enforce, so an agent
  can find the rule behind a red check. Aids comprehension; the check blocks with or without the
  index.
- **role:dynamic-context-injection** — inject the relevant rule text into an agent's context before
  it writes the code, so it avoids the violation in the first place. This layers *prevention* on top
  of the *detection* the lint provides — a strict addition, never a replacement for the blocking
  check.
