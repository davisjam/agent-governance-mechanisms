# READY-TO-DISPATCH BRIEF — PHASE 3 · 3a: catalogue CARDS (Fable, read-only analysis + emit artifact)

Dispatch after Phase 2c (DONE, live `94af0df`). Model **fable-5**. run_in_background. Live tree, branch main, NO worktree, single writer. **COMMIT EARLY per batch** (~15-20 entries/commit) — 82 entries is a long read; batch-commits make a stream-silence death recoverable. This is the empirical substrate for 3b clustering — READ-ONLY wrt the entries (do NOT modify any entry .md in 3a).

## Brief text (paste into Agent prompt)

You are analyzing the MAGE governance catalogue (LIVE checkout at `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). Work **slow and correct**; **COMMIT EARLY** (every ~15-20 cards, descriptive messages) so a long-read interruption is recoverable. NOT the parent ada-tool product — book workflow = edit → `catalog.py validate` → (no deploy needed for this step).

**Your task = PHASE 3 · step 3a** — produce a 9-field CARD for EVERY current catalogue entry, as a queryable artifact. This is the empirical substrate for the 3b clustering; it is READ-ONLY analysis — do NOT modify any entry.

**READ FIRST (the method + the target schema):**
- `book/_design/book-editorial-discipline-directive-260802.md` §§ "Task 3 — Truncate the appendix" (the 12 inclusion / 10 exclusion criteria + 10-dim rubric + overrides), "Task 3 SUPPLEMENT" (the 3-level architecture + FAMILY vs PATTERN vs INSTANCE + BEWARE FALSE MERGERS + the card+cluster method + NAME AFTER ABSTRACTION), "Task 3 SUPPLEMENT 2" (the 4-level GEE ontology + title + opening passage), and Part-B "PHASE 3" (3a/3b/3c). You are 3a only.
- `INDEX.md` — the census (one row per entry, grouped by family; the `Form`/`Move`/`Model`/`Enf.` columns). Enumerate every entry from here (and/or `python3 catalog.py` — check its subcommands).
- The entries themselves: `<role>/<family>/<mechanism>.md` (roles `agent/`, `models-bridge/`, `product/`). 82 entries total (28 agent · 34 bridge · 20 product).

**THE 9-FIELD CARD (per the directive's "PRACTICAL METHOD — card + cluster"):** for each entry, extract:
1. **Failure class** — the recurring failure it prevents.
2. **Engineering obligation** — the durable, general requirement it serves (name it abstractly — the obligation, not the impl).
3. **Solution structure** — the shape that prevents the failure.
4. **Guarantee** — what it guarantees (the guarantee boundary).
5. **Semantic level** — what RELATION it models/enforces (per BEWARE FALSE MERGERS: the relation, NOT the impl tech — e.g. "implementation ⊨ semantic policy" vs "model ⟷ reality" vs "every mutation site → provenance").
6. **Forces / tradeoffs** — competing forces, costs, where it fails, new risks.
7. **Dependencies** — what it composes with / needs.
8. **Known uses** — the concrete DocAble instances (this is where the impl texture lives).
9. **Likely parent family** — your first-pass guess at the family/pattern it belongs under (3b will finalize; give your best read).

**EMIT as a queryable artifact:** a NEW model file `book-models/catalogue-cards.json` (declared→generated if that fits the repo's model idiom, else a single well-structured JSON), keyed by entry id (role/family/mechanism), each value the 9 fields + the entry's current INDEX metadata (Form/Move/Model/Enf.) read live from INDEX/the entry card (join, don't restate by hand). Add a `_provenance` header (auto-gen discipline) + `_note` explaining it's the 3a card substrate for 3b. Keep it stdlib-parseable. If you add a generator, mirror the existing declared→generated sibling shape.

**DISCIPLINE:**
- READ-ONLY wrt entries — 3a does not rewrite/merge/rename any entry. Cards only.
- Card the ABSTRACTION honestly (esp. fields 2 + 5) — 3b's clustering quality depends on obligation + semantic-level being the real relation, not the impl. Where an entry's title is impl-biased, note the likely abstract name in field 9.
- `catalog.py validate` must stay 0 (you're only ADDING a model file + its optional generator; don't perturb entries/INDEX).
- **NO deploy needed** for 3a — the cards are intermediate substrate for 3b, not user-facing. Just `catalog.py validate` (0) + `book/build_book_html.py` (green, to be safe) + commit. (If adding the model trips the reachability/build gate, resolve minimally.)

**RECORD (do not relay):** append a `## PHASE 3 · 3a — catalogue cards` block to `book/_design/editorial-run-results-260802.md`: the artifact path + schema, entry count carded (should be 82), any entries that resisted clean carding (note them for 3b), and your first-pass family guesses' rough distribution. Commit it.

Thorough over fast. This is the foundation for the biggest phase — accuracy of the obligation + semantic-level fields matters most. On ambiguity, make the defensible call, DOCUMENT in the card's note field, continue.
