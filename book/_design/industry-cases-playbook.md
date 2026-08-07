# Industry-cases playbook — the add-a-case flow

How to fold a new practitioner report into the book's external-evidence base. The design goal is that each new
case is a **declared-JSON record plus a batched regen**, never a hand-edit the author will forget. The model
lives at `book-models/industry_cases_declared.json`; the reader/projection/queries at
`book-models/industry_cases_model.py`.

## The flow

```
read the source
  → fill the Industry Evidence Card (book/_design/industry-evidence-card.md — the ~18-field worksheet)
  → run `python3 book-models/industry_cases_model.py only-docable` : does this source fill an empty column?
       (the coverage gate — card field 18; orthogonality beats agreement)
  → encode an industry_case record in industry_cases_declared.json
       (flip its roster entry status: pending-writeup → authored; the record carries the full payload)
  → add the citation to book/references.bib, then regenerate the web mirror:
       `python3 book/render_citations.py`   (authored records only; a stub carries no cite)
  → [BATCHED, single writer] regenerate the matrix into its chapter page:
       `python3 book-models/industry_cases_model.py matrix`   (author the block verbatim into the page)
       write prose analysis IF the case fills a gap; otherwise it is a corroboration cite, not two pages
  → validate: `python3 catalog.py validate`   (schema + joins green; matrix page-parity green once wired)
  → adjust the Preface posture ONLY if the overall evidence posture materially changes
       (thresholds: 1–2 corroborating anecdotes → 3 emerging pattern → 5 comparative synthesis)
```

## The two rules that keep this scaling

- **The only per-case edit is the declared-JSON record.** The matrix regen and the page re-author are a
  **batched infrastructure step** one writer runs to fold in a wave of records — not a per-drafter page edit.
  This keeps parallel case-drafting from serializing on the single Chapter-6 matrix page (the one shared
  hot-spot). There is no count guard to hand-bump: the roster is the declared intent, and the roster guard
  (IC6) checks the record-set equals the roster set, so adding a case is a roster edit plus a record, never a
  magic integer.
- **No blank matrix rows.** `render_matrix_md()` projects the fixed DocAble row 0 plus `status == authored`
  rows only. A `pending-writeup` stub lives in the roster and surfaces through the `coverage` / `only-docable`
  / `roster` queries — it never renders as a blank row in the live book. When a stub flips to `authored`, it
  becomes a matrix row: the append-a-row property.

## Selection rule — maximize orthogonality, not agreement

"Does this source increase coverage?" beats "is this another good story?" The `only-docable` query names the
columns still resting on DocAble alone; those gaps drive which pending site to write first. Cloudflare leaves
one construct column empty — **governance-conversion** (Conversion): its incident reviewer surfaces gaps but
the source describes no failure→new-obligation loop. So the first pending sites to write are the ones whose
reports show a **failure → durable-control conversion** loop, plus the sites that fill the wider gaps a
single policy-first case cannot reach — system-modeling / specs-as-reasoning-substrate (Siemens), high-autonomy
fleets and churn (Spotify / Docker), and brownfield knowledge recovery.

## The column contract

The matrix columns are a **declared, ordered construct universe** (`construct_universe` in the declared JSON),
not the union of whatever constructs cases happen to touch. A new *case* renders against this fixed set
(append-a-row); a new *construct* is the rare, deliberate event that widens the grid. Rate a construct a case
does not touch as an explicit `not-described`, or leave it off the record and let the projection emit `—`.

## Reconciliation obligations

- **Vocabulary membership stays audit-only longer** than the joins: early cases legitimately want new
  descriptive-vocab terms (a new mechanism name), so a blocking membership gate would stall a reasonable
  case-add. Extend the closed vocab deliberately; promote membership to blocking once it stops churning.
- **Watch the overlap with existing citations.** A new case may already appear as a build-report cite
  elsewhere in the book; the two must agree on the shared source, and the same organization is one site, not
  two independent witnesses. Cloudflare is the worked example: a build report and a governance report, two
  evidence forms, two epistemic jobs, one site.
