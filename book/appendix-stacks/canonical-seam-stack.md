### Concept

Route every mutation of a format through one typed model, and stamp every mutation so it can be
explained and reversed. The stack is what makes a remediation *auditable*: one place where change
happens, and a durable record of each change made there. A typed model with no attribution can still
corrupt trust silently; attribution with no single seam has too many un-covered doors to stamp.

### Mandatory members

- **role:pdf-model** — the sole sanctioned mutation surface for a format, held in place by a ban-lint
  on the raw library (the instance here is a PDF model; the pattern applies per format). One door
  means one place to enforce every invariant. (The office-format and traversal analogues —
  role:office-models, role:canonical-walkers — instantiate the same member for their trees.)
- **role:mutator-stamps** — every mutating verb records what it changed, in a durable per-mutation
  stamp. This is what turns an opaque edit into an explainable, reversible one; the single seam exists
  precisely so this stamping has a bounded set of sites to cover.
- **role:f10-wiring-lint** — a cross-cutting lint that fails if any mutator verb ships without its
  stamp wiring. It is the guarantee that the stamping is *complete*, not merely present on the verbs
  someone remembered. Drop it and coverage rots one new verb at a time.

### Complementary members

- **role:content-validator** — a fidelity gate asserting the input content survives into the output
  (input ⊆ output). It catches a mutation that dropped authored content; strong insurance layered on
  top of the seam, not part of what makes the seam auditable.
- **role:derive-changelog** — reconstruct the human-readable list of mutations from the stamps. A
  consumer of the attribution record, valuable for the reader; the stack records provenance with or
  without the rendered changelog.
