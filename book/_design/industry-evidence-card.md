# Industry Evidence Card — the pre-encoding worksheet

A worksheet the author fills once per candidate practitioner report **before** deciding whether it earns book
space. It is not built and not shipped — it lives under `_design/` as the authoring altitude of an
`industry_case` record. Fill the card, then encode the record in
`book-models/industry_cases_declared.json`; the fields map one-to-one so the card is a pre-encoding of the
model, not a second source of truth.

The gate is **field 14**: if "This case matters to MAGE because ___" is weak or redundant with a case already
in the roster, the report does not earn a writeup — cite it as corroboration and move on. The selection rule
is **orthogonality, not agreement**: run `python3 book-models/industry_cases_model.py only-docable` first and
prefer a source that fills an empty column over another good story that re-tells one already covered.

| # | Card field | → model field |
|---|---|---|
| 1 | Source & independence — who wrote it, in what role | `source.{citation_key, source_type, independence, author_role}` |
| 2 | Account type & evidence horizon — retrospective vs aspirational; days vs years | `source.{account_type, evidence_horizon}` |
| 3 | Setting — scale, brownfield?, the quantified scale facts that make it *evidence* | `setting.{scale, brownfield, scale_facts}` |
| 4 | Autonomous work — what the agents actually do, and where their authority stops | `autonomous_work`, `agent_authority` |
| 5 | Object territory — what is engineered/acted upon | `object_territory[]` (closed vocab) |
| 6 | Representation — what they made explicit (rules? system? both?) | `representations[]` (closed vocab) |
| 7 | Traceability — how a claim/requirement keeps its identity across edits | `traceability` |
| 8 | Context strategy — how the representation reaches the agent at the point of work | `context_strategy` |
| 9 | Mechanism — the environmental machinery installed | `mechanisms[]` (closed vocab) |
| 10 | Where judgment lives — the load-bearing three cells | `judgment.{policy_authoring, semantic_compliance, mechanically_checkable_compliance}` |
| 11 | Feedback & org memory — how the environment evolves; what durable knowledge it banks | `feedback_adaptation`, `org_memory` |
| 12 | Implicit theory — the site's OWN competing description, in one paragraph | `implicit_theory` |
| 13 | MAGE correspondence — the matrix row: a strength per construct + a per-cell note (the book's reading) | `mage_constructs[]` (strength ∈ the correspondence set) |
| 14 | Hypothesis linkage — which theory H-ids this case bears on | `hypotheses[]` (join to the theory model) |
| 15 | What MAGE adds — the connective account the site does not supply | `mage_explains_implicit` |
| 16 | What the case adds to MAGE — reciprocity | `adds_to_mage[]` |
| 17 | Boundary / non-evidence — what this case explicitly does NOT show | `limitations[]` |
| 18 | One-sentence result — "This case matters to MAGE because ___" | `result_sentence` |

## The correspondence vocabulary (field 13)

Rate each construct with exactly one value from the closed set — never a checkmark:

- **strong** — the source's behavior maps cleanly onto the construct (not proof).
- **partial** — instantiated in part; a named piece is missing.
- **not-described** — the source is silent. **Absence from a report is NOT evidence the company lacks it.**
- **tension** — MAGE's vocabulary fits only with contortion, but the site does not disconfirm it.
- **counterexample** — the source describes behavior that runs *against* the construct (genuine disconfirming
  evidence).

Every cell carries a **note** framing the reading as the book's, not the site's claim about MAGE.

## Framing discipline

- **Source-facts vs the book's reading.** Encode the site's reported facts (scale numbers, lifecycle states,
  mechanism names) as facts; frame every MAGE-construct correspondence as the book's interpretation. A cell
  note reads "the book reads this as…", never "the site instantiates MAGE."
- **Verbs.** Use *substantiated* / *corroborating* / *convergent* — never *validated* / *confirmed*.
- **One site, one record.** A company's coordinated first-party posts are one site, not several independent
  witnesses. Reconcile with any existing citation of the same organization so it is not double-counted.
