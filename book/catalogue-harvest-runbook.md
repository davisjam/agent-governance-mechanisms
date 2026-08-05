# Runbook — harvesting the source project's practice into catalogue/book material

The MAGE catalogue and book are fed partly by the *real* engineering practice of the source project
(**ada-tool**, the parent repo this submodule lives under). This runbook is the recurring sequence for
mining that practice for candidate new **mechanisms**, **models**, **insights**, and **highlights**.

It is **draft-only by construction.** Every run produces DRAFTS for the author to review. It **lands
nothing** in `book/`, in the catalogue (`agent/` · `models-bridge/` · `product/` entries), or in
`book-models/` without explicit author approval. Approved candidates become their own separate landing
waves — never a side effect of the harvest.

Sibling runbook: [`book/transcript-runbook.md`](transcript-runbook.md) (audio → book material). This one
is practice → catalogue/book material.

## The three sources

1. **Field notes** — `docs/field-notes/` in ada-tool. Completed-but-unprocessed RCA writeups / dated
   incident notes not yet mined into the catalogue or the field-note evidence data.
2. **Self-operate skill + runbooks** — the `operate-ada-tool-repo` skill (`pointers.yaml`,
   `runbooks.yaml`, the positive-lifecycle map, the carried briefs). Mine for shareable operational
   concepts + possible mechanisms.
3. **Recent Epics** — ada-tool Epics closed or active in a trailing window (default **240 h / 10 days**;
   `docs/epics/`, the epic ledger / `reconcile-epics.py`). Scan for missed field-note opportunities,
   new models/mechanisms, and "awesome" material worth highlighting.

## Where things live

- **Sources** → the ada-tool parent repo: `docs/field-notes/`, `.claude/skills/operate-ada-tool-repo/`,
  `docs/epics/`. Read-only during harvest.
- **Copied-in field notes** → `book/_design/harvest/field-notes/` (this repo) — the working copy; the
  original note in ada-tool stays the source of record (copy, never move).
- **Field-note evidence data** → `book-models/` (the field-note source in the substantiation model —
  `FieldNoteBacking`; see the round-2 evidentiary-basis work). Registering a note here is data-update,
  not book content.
- **Drafts / review packets** → `book/_design/harvest/<source>-<YYMMDD>/` — candidate additions, gitignored
  draft space, **never** promoted to `book/` or the catalogue by the harvest itself.

## The discipline (non-negotiable)

- **Draft-only. Land nothing.** The harvest reviews, analyzes, and drafts. The author decides what lands.
- **Fidelity.** A candidate mechanism must be a *real recurring* pattern in the practice, not a one-off. A
  candidate insight must be genuinely *transferable* beyond ada-tool.
- **Genre-check before proposing a new catalogue entry** (→ the book's own A.9 discipline): does it
  already exist as a mechanism / variant / **technique**? Is it an *instance* of an existing technique
  (→ an "advanced example," not a new top-level entry)? Prefer surfacing over inventing.
- **Deliver a review packet**, not scattered files: what was found, why it qualifies, where it would go
  (new mechanism / technique instance / new insight / book highlight / field-note-to-formalize), and the
  proposed draft.

## The sequence

### A. Field notes

> **✅ Priority input, now available (landed 260805 — ada-tool commit `4b426bd956`).** The field note
> `fieldnote-loops-completeness-mode-assembled-260805.001658.md` (in `docs/field-notes/`) carries **metrics**
> — notably **Epics closed in a period** — to draw into the **book's empirical data**, augmenting the
> existing data mining: the metrics dashboard / substantiation numbers, and the Theory chapter's
> velocity/throughput hypotheses. Ponder folding its metrics into the book's data, not just the catalogue.

1. Enumerate `docs/field-notes/` in ada-tool; identify the completed-but-unprocessed set (not yet mined
   into the catalogue or registered in the field-note evidence data).
2. Copy each into `book/_design/harvest/field-notes/` (working copy).
3. Analyze each: what recurring failure or transferable insight does it capture? Map it to an existing
   catalogue mechanism/technique, or flag it as new.
4. Update the field-note **data** (register in the `FieldNoteBacking` substantiation source: id, location,
   the judgment/insight it grounds, its limitation).
5. Draft candidates: a new mechanism? a new technique *instance* (advanced example)? an insight/highlight
   for the book? a field note worth formalizing as an evidence citation?

### B. Self-operate skill + runbooks
1. Read `operate-ada-tool-repo` (`pointers.yaml`, `runbooks.yaml`, the five-lifecycle map, carried briefs).
2. Identify **shareable** concepts (e.g. the positive-lifecycle-first framing; the symptom → doc catalog;
   the typed runbook-step kinds RUNNABLE / JUDGMENT_AUTOMATABLE / JUDGMENT_IRREDUCIBLE; the audit → lint →
   control staircase) — separate the genuinely transferable MAGE patterns from the ada-tool-specific.
3. Genre-check against the existing catalogue (`operational-playbooks`, `self-governance`,
   `operator-runbook-skill` may already cover it).
4. Draft candidates: new catalogue mechanism(s), or a new insight/highlight for the book (governing the
   operator's *own* practice as a MAGE application).

### C. Recent Epics (trailing window, default 240 h)
1. Query ada-tool Epics closed/active in the window (`docs/epics/`, the ledger, `reconcile-epics.py`).
2. For each substantive Epic ask: **(a) missed field-note opportunity** — did something happen worth a
   field note that was never captured? **(b) new model/mechanism** — did it produce a catalogable pattern?
   **(c) awesome** — a demonstration or insight worth highlighting in the book/catalogue?
3. Draft candidates + explicitly flag the missed-field-note opportunities (so they can be written
   retroactively into `docs/field-notes/` — a separate, author-approved action).

## Output

One **review packet** per run at `book/_design/harvest/<YYMMDD>/README.md` — a summary plus per-candidate
draft files. Nothing staged or committed to `book/` or the catalogue. The author reviews; approved
candidates become their own separate landing waves (a new catalogue entry, a technique instance, a book
highlight, or a formalized field note), each following the normal single-live-writer + gate discipline.
