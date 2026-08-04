*A two-page synthesis of the provenance + fidelity stack. Five patterns make one guarantee: reconstruct a
remediated document's mutation history from the artifact itself, and catch any damage done through the
sanctioned door. Who and why for every change, and nothing silently lost.*

## The capability

**Reconstruct the full mutation history of a shipped artifact from the artifact alone — and prove nothing
the author wrote was dropped on the way out.** The stack builds two capabilities: *track provenance and
trace causes*, and *preserve product semantics*. It assumes every change already flows through one
sanctioned door; on that door it builds attribution you can read back and a fidelity check you cannot skip.
The evidence lives inside the file, so it survives copy, download, and re-open — no side log to trust or
lose.

## Failure classes it covers

- **The unattributable change.** A pass mutates a document but leaves no durable trace of who changed it or
  why; once the file leaves the pipeline the history is gone.
- **The indistinguishable insert.** A tool-inserted artifact looks exactly like authored content, so nothing
  can tell what the tool added — and a validator cannot cover what it cannot name.
- **The silent hole.** A new mutator lands without attribution wiring; "we record every change" quietly stops
  being true, one commit at a time.
- **The unread evidence.** Stamps sit in the artifact with no consumer, so "auditable" is a claim no one can
  exercise.
- **The silent loss.** A pass drops a table, a note, a paragraph; the file looks fixed but shipped damaged,
  and no one sees the hole until a reader hits it.

## Composition

<!-- label: provenance-fidelity-stack -->
<!-- figure: assets/provenance-fidelity-stack.svg | The provenance + fidelity stack in one picture. A document flows left to right through two lanes. The sanctioned door (fleet blue): MARK names every insertion so it is registry-covered; EMIT writes an attribution stamp for every mutation into the artifact. The guarantee (governed green): COVER's wiring lint holds the closed verb set at zero gaps; READ reconstructs the history from the embedded stamps; GATE asserts the input's content survives the output and names the pass that dropped it otherwise. Below the row, the artifact strip carries the stamps EMIT drops and READ and GATE read back. Mark it, cover the marking, read it back, and gate what leaves — provenance you can reconstruct from the artifact itself. -->

The five parts run as a chain: mark every insertion, stamp every mutation, prove the stamping complete, read
the history back, gate what leaves against what came in. Each part hands the next a stronger guarantee.

## The constituent patterns

- **MARK — role:a11y-prefix.** Name every insertion so it is distinguishable from authored content and
  registry-covered by construction: an invisible insert takes a reserved prefix, a user-visible one keeps an
  ordinary name, a spec-mandated name keeps its spec name — every inserter records into one registry. Opens
  the chain with a closed, complete population of insertions to attribute.
- **EMIT — role:mutator-stamps.** Every sanctioned mutation embeds an attribution stamp — its pass, its
  visibility — into the artifact itself, written through one stamp-writer per format with the raw mutation
  ban-linted away. Each change becomes embedded evidence.
- **COVER — role:f10-wiring-lint.** A blocking lint scans every mutator verb and fails on any that skips the
  stamp wiring, so completeness is a guarantee, not an aspiration. It reads the same closed verb set the
  writer serves and proves the writer is called across all of it.
- **READ — role:derive-changelog.** A command reconstructs a human-legible changelog from the embedded stamp
  registry, each entry a mutation attributed to its pass — history projected from the artifact, never a
  trusted external log.
- **GATE — role:content-validator.** The fidelity gate extracts the input's content, asserts input is a
  subset of output, and fails the job when meaning was dropped; a per-pass staging variant names which pass
  dropped it. Where the first four attribute what the tool *added*, this catches what a pass silently
  *removed*.

## A DocAble example, end to end

DocAble remediates a slide deck for accessibility. A pass writes alt text onto an untagged image. **MARK**
gives that description a reserved prefix and records it in the insertion registry, so it reads as tool-added,
not author-written. **EMIT** stamps the mutation into the file — this pass, invisible insertion — through
the one sanctioned stamp-writer for the format. **COVER** has already proven, at build time, that the
alt-text verb wires that stamp; a version of the verb that forgot to would have reddened the gate before it
shipped. Weeks later a customer asks what the tool changed: **READ** reconstructs the changelog straight
from the deck's embedded stamps, no pipeline access needed. And when a different pass quietly drops a
speaker-notes paragraph, **GATE** catches it — input content is not a subset of output — fails the job, and
names the pass that lost it, instead of shipping a deck that looks fixed but is not.

## Tradeoffs and adoption order

Adopt in chain order, because each part presumes the one before it.

1. **MARK first.** Until insertions are named and registered, nothing downstream has a complete population to
   attribute. A naming convention costs nothing at runtime.
2. **EMIT, then COVER.** Stamp through one writer, then add the wiring lint that holds the closed verb set at
   zero gaps. The stamps cost one write per mutation; the lint is deterministic and does not decay.
3. **READ** is a read-only projection — cheap, and it makes the stored provenance finally usable.
4. **GATE** last, and independently valuable: a set-containment check over extracted content, run in
   production. Its per-pass diagnostic variant stays staging-only to keep the production path fast.

The chain's guarantee is only as strong as the one door it presumes — every mutation must route through the
sanctioned surface, held by a separate ban-lint. Extraction that under-reads a format weakens the gate;
bound it to the canonical reader.

## The full treatment

Every constituent above links to its full Gang-of-Four pattern — in this appendix for the flagship members,
online for the rest. The stack composes with the
[model-coherence stack](appendix-d-model-coherence-stack.html) — the sanctioned door it stamps is that
stack's typed seam — and the
[specification + verification stack](appendix-d-specification-verification-stack.html). The complete
83-mechanism catalogue, each pattern with its Motivation, Applicability, and Known uses, is online in the
web edition.
