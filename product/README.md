# Product controls — governing the shipped artifact

<!-- summary: Controls that govern the shipped accessibility-remediation artifact. -->

*One of three roles in the [catalogue](../README.md). Product controls govern the **shipped
accessibility-remediation artifact**: how the document is modelled and accessed, how the remediation is
validated and conformance-checked, how behaviour is regression-pinned, how mutations are made auditable,
and how the repair move-space is bounded. (The artifact is *produced by* the [agent](../agent/) fleet,
*through* the [models-bridge](../models-bridge/).)*

## The five families

1. **[Canonical models & seams](canonical-models-and-seams/)** — the one sanctioned typed model or seam
   per concern (document models, walkers, the cross-service client, the sole raw-Redis seam).
2. **[Validation & conformance](validation-and-conformance/)** — deterministic pass/fail checks over the
   artifact: content-fidelity, semantic lints, the standards/WCAG rule engine, cross-source coherence.
3. **[Regression tests](regression-tests/)** — repeatable behaviour-pinning: the test-onion tiers,
   FsCheck property tests, fuzz campaigns, doc-derived-test pin-trailers.
4. **[Provenance & attribution](provenance-and-attribution/)** — durable records of what the tool
   changed: per-mutator stamps, the F10 wiring lint, changelog derivation, the `a11y_` prefix.
5. **[Repair vocabulary](repair-vocabulary/)** — the bounded move-space of the remediator: closed
   remediation-verb sets, typed violation/failure categories, the codemod-first threshold.

## The reconciliation that lives here

**Construction, held by a ban-lint.** The *Canonical models & seams* family is *typed models and seams*
— which the catalogue elsewhere says it "shows by example, never counts" (that is *construction*, not
detection). The reconciliation is the catalogue's own rule: the typed model/seam is the construction
mechanism (shown by example), and the entry's **counted, enforced control is the ban-lint that holds it
in place** (the [raw-PDF-library ban-lint](canonical-models-and-seams/pdf-model.md),
the [raw-OpenXML ban-lint](canonical-models-and-seams/office-models.md), the sole-seam lints). Each entry
documents both; the Enforcement row is the lint. This is the same construction-held-by-detection
pairing the [models-bridge](../models-bridge/) uses for its models and drift gates.

The census, forms, soft/hard axis, relationships, and entry template are documented once in the
[umbrella README](../README.md).
