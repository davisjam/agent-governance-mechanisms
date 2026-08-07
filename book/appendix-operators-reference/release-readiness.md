*Can I trust this release?*

Run the checklist before you ship — six items, each backed by a gate or a mechanism, not by an operator's
memory. A pilot does not certify a plane from feel; a MAGE operator does not certify a release from feel.
Every box is green, or the release waits.

This card is a checklist, deliberately. Each box reads a mechanism the earlier chapters built; the checklist
adds no policy, it gathers the gates that already exist onto one face.

### The six boxes

- **Model coverage/current.** The models regenerated against source at HEAD; the Missing-Model surface within
  its floor.
- **Model-code parity.** The drift and parity gates report the models equal to the code.
- **Validators pass.** The correctness and conformance validators, and the generative-validation coverage
  oracles, are exercised and green.
- **Fidelity acceptable.** The content survived its transformation — the output still means what the input
  meant. This catches the artifact that became more conformant and less true to the original.
- **Gates passing.** The staged-deploy gate staircase is green end to end; the release is not shipped past a
  red stage.
- **Overrides reviewed.** Every recorded escape-hatch since the last release has been read and understood,
  traced through the change-provenance record, not silently inherited.

```
  RELEASE READINESS  ·  PREFLIGHT              "Can I trust this release?"
  ═══════════════════════════════════════════════════════════════════════
  [ ]  Model coverage/current  Missing-Model within floor      (model-sync)
  [ ]  Model-code parity       parity gates report equal       (drift gates)
  [ ]  Validators pass         coverage oracles exercised      (gen-validation)
  [ ]  Fidelity acceptable     meaning survived transformation (fidelity validator)
  [ ]  Gates passing           staged staircase green          (deploy gates)
  [ ]  Overrides reviewed      every escape since last release (provenance record)
  ═══════════════════════════════════════════════════════════════════════
  All six green → cleared to ship.   Any red → the release waits.
```

Two of the six carry a number: the Missing-Model surface against its floor, and the overrides count since the
last green release. The other four are pass-or-fail gate readings.

### What this projects

The staged-deploy gates; the content validator and the *fidelity-validator* concept (meaning survived the
transformation); the drift-and-parity gates; the generative-validation coverage oracles; and the
caused-by-provenance record (the change-traceability audit trail behind "overrides reviewed"). The aviation
checklist framing is the card's identity — the one page you print and pin over the desk.
