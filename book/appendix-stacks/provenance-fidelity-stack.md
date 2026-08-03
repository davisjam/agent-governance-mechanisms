*A flagship deep-dive walks a stack part by part: a goal, an overview figure, and one six-field entry per
member (role · failure · mechanism · seam · durability). Each seam names what the part before it hands
over, so the page reads as one interlocking chain rather than a list of parts.*

## The goal

**Reconstruct a remediated document's mutation history from the artifact itself, and catch any damage done
through the sanctioned door.** Two promises in one: *provenance* — who changed what, and why, for every
change; and *fidelity* — nothing the author wrote goes silently missing. A remediation tool earns trust
only when both hold, and neither holds from a single mechanism. This stack is how five parts make them
hold together.

<!-- label: provenance-fidelity-stack -->
<!-- figure: assets/provenance-fidelity-stack.svg | The provenance + fidelity stack in one picture. A document flows left to right through two lanes. The sanctioned door (fleet blue): MARK names every insertion so it is registry-covered; EMIT writes an attribution stamp for every mutation into the artifact. The guarantee (governed green): COVER's wiring lint holds the closed verb set at zero gaps; READ reconstructs the history from the embedded stamps; GATE asserts the input's content survives the output and names the pass that dropped it otherwise. Below the row, the artifact strip carries the stamps EMIT drops and READ and GATE read back. Mark it, cover the marking, read it back, and gate what leaves — provenance you can reconstruct from the artifact itself. -->

## How the parts interlock

Each part is weak alone; the guarantee emerges only from the chain. **MARK** makes every insertion
registry-covered by construction. **EMIT** stamps each sanctioned mutation into the file. **COVER** — the
wiring lint — turns "we attribute mutations" from an aspiration into a checked property over a closed set
of mutator verbs. **READ** reconstructs a legible history from the embedded stamps, so the provenance has a
consumer. **GATE** catches damage done *through* the sanctioned door: when a pass drops content, "something
was lost" becomes "pass N lost it." Read the parts in that order; each seam names what the part before it
hands over.

## The parts

### 1. MARK — the reserved-prefix naming rule

- **Part** — role:a11y-prefix
- **Role in the stack** — Name every insertion so it is distinguishable from authored content and
  registry-covered by construction.
- **Failure it retires** — An inserted artifact is indistinguishable from what the author wrote, so nothing
  can tell what the tool added — and a validator cannot cover what it cannot name.
- **Mechanism** — A three-way naming rule: an invisible insert takes a reserved prefix, a user-visible
  insert keeps an ordinary name, a spec-mandated name keeps its spec name. Every inserter records into one
  registry.
- **The seam** — Opens the chain. It hands the next part a closed, registry-covered population of
  insertions to attribute; nothing enters the artifact unmarked, so the stamp-writer downstream has a
  complete set to stamp.
- **Limits / durability** — Durable and model-independent — a naming convention costs nothing at runtime
  and leans on no 2026 model capability. It fails only if an inserter bypasses the registry, which the
  fidelity gate then catches.

### 2. EMIT — one stamp-writer per format

- **Part** — role:mutator-stamps
- **Role in the stack** — Embed an attribution stamp — its pass and its visibility — into the artifact for
  every sanctioned mutation.
- **Failure it retires** — A change is made but leaves no durable trace of who made it or why; once the
  file leaves the pipeline the mutation history is unrecoverable.
- **Mechanism** — One sanctioned stamp-writer per format, with the raw stamp mutation ban-linted away, so
  every mutator verb writes its stamp through a single surface.
- **The seam** — Takes the marked, registry-covered inserts from MARK and turns each sanctioned mutation
  into embedded evidence. It hands the wiring lint a closed verb set to prove complete, and the changelog
  an embedded registry to read back.
- **Limits / durability** — Durable — evidence embedded in the artifact, not a side log, survives copy,
  download, and re-open. Cost is one stamp per mutation; it fails only where a mutation skips the
  sanctioned writer, which the next part forbids.

### 3. COVER — the wiring lint over the verb set

- **Part** — role:f10-wiring-lint
- **Role in the stack** — Assert every mutator verb wires the stamp, so completeness is a guarantee, not an
  aspiration.
- **Failure it retires** — A new mutator lands without stamp wiring; provenance quietly develops a hole and
  "we attribute every change" silently stops being true.
- **Mechanism** — A build-time lint scans every mutator verb in the model primitives and fails on any
  unwired one — the closed verb set held at zero open gaps.
- **The seam** — Sits over EMIT. It reads the same closed verb set the stamp-writer serves and proves the
  writer is called across all of it, so the READ downstream can trust the stamped population is complete.
- **Limits / durability** — Durable — a deterministic lint over a closed set does not decay. Its guarantee
  is only as strong as the one door it presumes: mutations must route through the sanctioned primitives,
  held by a separate ban-lint.

### 4. READ — reconstruct the changelog

- **Part** — role:derive-changelog
- **Role in the stack** — Reconstruct a human-legible ChangeLog from the embedded stamp registry, each
  entry a mutation attributed to its pass.
- **Failure it retires** — The provenance is present but unusable — stamps sit in the artifact with no
  consumer, so "auditable" is a claim no one can exercise.
- **Mechanism** — A command reads the embedded stamps and projects them into an attributed history — the
  mutation record reconstructed from the artifact itself, never a trusted external log.
- **The seam** — Consumes what EMIT wrote and COVER proved complete. It turns the embedded evidence into
  the reconstructable history the goal promises — provenance that finally has a reader.
- **Limits / durability** — Durable — a read-only projection of embedded data, with no runtime dependency.
  It reconstructs history from any conformant artifact and is exactly as complete as the stamps the wiring
  lint guarantees.

### 5. GATE — the fidelity check at the exit

- **Part** — role:content-validator
- **Role in the stack** — Extract the input's content, assert input is a subset of output, and fail the job
  when meaning was dropped.
- **Failure it retires** — A remediation pass silently drops the user's content — the file looks fixed but
  lost a table, a note, a paragraph — and the damage ships invisibly.
- **Mechanism** — A deterministic gate extracts input content and asserts it survives into the output,
  failing the job in production; a per-pass staging variant names which pass dropped it.
- **The seam** — Closes the chain. Where MARK, EMIT, COVER, and READ attribute what the tool *added*, the
  validator catches what a sanctioned pass silently *removed* — damage done through the same door
  provenance covers. "Content was lost somewhere" becomes "pass N lost it."
- **Limits / durability** — Durable and model-independent — a set-containment assertion over extracted
  content. Cost is one extract-and-compare per job; the per-pass variant is staging-only. It weakens only
  if extraction under-reads the format, bounded by the canonical reader.
