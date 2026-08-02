# The book's claims / key-distinctions as a typed model — design

**Status:** DESIGN ONLY — nothing built. This doc recommends a new sibling model in the
governance-catalogue's `book-models/` directory (a git submodule under
`talks-and-notes/governance-catalog/`), so the MAGE book becomes **auditable against its own stated
positions**. It follows the repo design-doc shape: invariants with stable IDs, as-built-vs-design
(⚠️ where code diverges — here, everything is design), and enforcement → gate mapping. The author
ratifies before any build.

All paths below are relative to `talks-and-notes/governance-catalog/`.

---

## 0. The motivating failure — one real datum

The book's stance on its modeling lineage is **direction-agnostic**: MAGE's claim is about
*maintenance* (model and code stay equal under drift gates), **not** authoring *direction*. The
preface's Lineage touchstone states it plainly (`book/frontmatter/0.1-preface.md`):

> Classical model-driven engineering prescribes an authoring direction (write the model, generate the
> code from it) … MAGE needs neither. Its claim is about maintenance, not authorship: model and code
> must stay equal … whichever artifact came first — model authored and code derived, model induced
> from existing code, or the two co-evolved.

A Scope-box line in `book/part3/3.1-the-executable-zoo.md` had **drifted to contradict it**. It read:

> keep the model **derived from the code**, not drawn alongside it.

"Derived *from* the code" is a one-directional, code-first claim — exactly the authoring-direction
opinion the book says MAGE refuses. Commit `6641b8a` ("third touchstone — MDSE as the lineage; 3.1
direction-agnostic fix") corrected it to:

> keep the model ***bound to* the code — derived in either direction, gated either way** — not drawn
> alongside it.

Nothing in the book's models caught this. The concept model knows `thesis-modeling` *exists* and has
a home; the outcomes model knows §3.1 *teaches* something; neither holds the **proposition** "MAGE is
direction-agnostic" as a checkable object, and none carries the field that would have flagged the slip:
*what prose would contradict this stance*. That missing object is what this design adds.

---

## 1. New model vs. extend an existing one — recommendation

**Recommendation: a NEW sibling model — `claims.json` + `claims_model.py` — not an extension of
concepts, definitions, outcomes, or big-ideas.** The book-models directory already holds four typed
models, each answering one quality question; a claim is a fifth kind of object none of them represents.

| Existing model | Object it holds | Quality question | Why a claim is not this |
|---|---|---|---|
| `concepts.json` (`book/data/`) | a **term/concept** (noun): `thesis-modeling`, `constraint`, `churn`; `kind ∈ {thesis, axis, family, mechanism-class, caveat}` | Does every concept have a definition and a home (book↔site)? | A claim is a **proposition about** concepts ("MAGE is direction-agnostic"), not a concept. It has a truth-stance the book asserts and can betray; a concept has a *home*, not a *stance*. |
| `definitions.json` (`book/data/`) | the 4 green-box **definitions** (model, agent, engineering, software-engineering) | Does each site definition trace to a model record? | A definition fixes what a *word* means; a claim asserts what is *true* of the system. Different object, no contradiction predicate. |
| `outcomes.json` (`book-models/`) | a **learning outcome** (verb + object per unit): "distinguish a constraint from a sensor" | Does every teaching unit declare what a reader can DO after it? | An outcome is about the **reader's** capability; a claim is about the **book's** asserted position. "The reader can distinguish X from Y" ≠ "the book asserts X is not Y." |
| `landing-big-ideas.json` (`book-models/`) | the **6 Big Ideas** as the ordered landing argument, each with a `claim` string, `figure`, `book_home` | Is the landing the book's argument in the book's own order? | Closest cousin — Big Ideas *do* carry a `claim` field. But they are a **fixed set of 6 ordered slots** built to render one page, positive framings only, single `book_home` each, **and no contradiction predicate**. Claims are an open set of N stances, each asserted at *multiple* sites, each carrying the "what would contradict it" the audit needs. |

**The load-bearing reason it is a new model: the contradiction predicate.** The author's ask — "an
audit that CATCHES prose contradicting a stated distinction" — requires every claim to carry a typed
field naming *what would negate it*. No existing model has this field, and bolting it onto (say)
big-ideas would (a) force the claim set into 6 ordered render-slots it does not fit, and (b) overload
a model whose job is landing layout. A separate `claims.json` keeps each model answering one question
(the directory's governing discipline) and lets claims **join into** the others rather than absorb
them.

**But reuse the join keys, do not re-model.** A claim does not re-declare concepts or units. It
*links* to them: `relates_to` points at `concepts.json` slugs and `definitions.json` terms; its
assertion sites are `outline`/reverse-index keys (section-id, chapter slug, `point:` slug). So the
claims model is a thin **relational layer over** the existing four, exactly as the reverse index is a
projection over the built views. New object, reused keys.

---

## 2. The candidate claims inventory (the seed set)

Grounded in `book/frontmatter/0.1-preface.md`, the Part-2 chapters, and `book/part3/3.1`. Each is a
**load-bearing proposition or distinction** — the kind of stance a prose edit could silently betray.
The author ratifies, trims, or extends this seed; ~16 is a starting corpus, not a target count.

Dominant shape: **the "X, not Y" distinction** (a claim with two named poles). For these, the
contradiction predicate is largely *derivable from the poles* — "prose that collapses pole A into pole
B, or asserts the book holds pole B." That regularity is a schema affordance (§3, `distinguishes`).

| id | kind | statement (canonical) | asserted at | what would CONTRADICT it (audit predicate) |
|---|---|---|---|---|
| `direction-agnostic` | distinction | MAGE's claim is about **maintenance** (model=code equality under drift gates), not authoring **direction**; whichever artifact came first. | 0.1 Lineage; 3.1 scope box | Prose stating MAGE prescribes model→code (or code→model) as *its own* authoring direction — the very drift `6641b8a` fixed. |
| `derived-not-snapshotted` | distinction | A model is **bound to the code and re-derived/gated on every change**; a representation drawn *alongside* is a snapshot that drifts. | 3.1 scope box; 0.1 (map kept "in sync for cents") | Endorsing a model maintained as a separately hand-updated artifact, or "draw the model beside the code." |
| `double-win` | causal | A model **earns its keep twice**: it solves the agent's context problem *and* it holds quality. | 0.1 Lineage; landing gateway; 3.1 | Framing models as *only* a context-savings, or *only* a quality tool. |
| `churn-is-symptom` | distinction | **Churn is the symptom**; its causes are the three not-knowings; every technique attacks a cause, not the symptom. | 0.1 premise | Treating churn as the root problem to fix directly, or a technique aimed at the symptom. |
| `scaling-limit-is-context-window` | distinction | The agent-fleet scaling limit is the **context window** (churn), not Brooks's-Law N² communication overhead. | 0.1 premise | Attributing agent-fleet velocity decay to coordination/communication overhead. |
| `three-not-knowings` | structural | Churn's causes are exactly three: not knowing **what** to build, **how** to realize it, how to change **without breaking**. | 0.1 premise | Enumerating a different count or set of causes. |
| `theses-divide-the-not-knowings` | mapping | The **Modeling Thesis** treats the first two not-knowings; the **Alignment Thesis** treats the third. | 0.1 premise | Assigning them differently (e.g. Alignment attacks "what to build"). |
| `governance-not-on-the-dial` | distinction | Governance is **not a point** on the velocity↔oversight axis; it changes what reliability is *made of* — pay per-class-of-failure, not per-change. | 0.1 "Three ways"; Big Idea 2 | Prose placing governance as a *midpoint/balance* on the speed-safety dial. ⚠️ See §2a — a live internal tension worth surfacing. |
| `mechanize-not-remember` | premise | Engineering discipline must be **mechanized, not remembered** — pushed into tooling so correctness never depends on holding a rule in mind. | 0.1 premise (SE@Google) | Relying on an agent/human *remembering* or *being careful* as the enforcement. |
| `constraint-prevents-sensor-detects` | distinction | A quality goal splits into a **constraint** (prevents the error) and a **sensor** (detects it after); costly failures earn both. | 0.1 Alignment Thesis; 2.3; Big Idea 4 | Conflating the two; calling a detector a constraint or a preventer a sensor. |
| `convert-failures-to-controls` | practice | **Velocity exposes** the unforeseeable failure; **judgment converts** each recurring one into a mechanism (convert judgment into infrastructure). | 0.1 "Three ways" close; Big Idea 5 | Prescribing up-front enumeration of *all* obligations as the method, or per-instance patching without retiring the class. |
| `soft-to-hard-spectrum` | distinction | Mechanisms sit on a **soft→hard** spectrum; push a recurring failure as far toward hard enforcement as it goes (2nd failure of a soft rule → move it right). | Big Idea 5; 2.3/2.6 | Treating a convention/brief as equivalent to a lint/gate, or claiming a convention "holds the line." |
| `models-are-universal-language` | master thesis | Models are the **universal language of engineering**; software could not afford them until agents removed the sync cost. | 0.1 universal-language; back matter | Framing models as a nice-to-have or a software-specific trick. |
| `printer-not-coder` | metaphor | Building with an agent is **running a printer, not managing a coder**: it builds anything you can explain; a bad output means bad instructions, not a bad machine. | 0.1 through-line; 1.1 | Locating the fault in the agent's *capability* rather than the instructions/model. |
| `seat-moves-not-lifecycle` | distinction | **SDLC → SELC**: the lifecycle stays intact; only the developer's seat moves to the fleet; the human keeps requirements/spec/design/validation. | 1.3; Big Idea 6 | Claiming agents replace the whole lifecycle, or that the lifecycle itself changes. |
| `single-case-humility` | caveat | This is a **single-case field report**; numbers are observations from one system, not measured laws; the contribution is *mechanism* (how/why). | 0.1 caution | Stating a number as a general/measured law across systems. |

### 2a. A live internal tension the model would surface on day one

`governance-not-on-the-dial` is asserted in the preface ("Governance is **not a point on that line**").
But `landing-big-ideas.json` titles the same idea "**Governance-centric — the midway between two
schools**." "Midway" reads as *a point between the poles* — the precise thing the claim denies. The
figure reconciles it (governance sits *beneath* as a synthesis, not *between* on the line), so this is
arguably consistent — **but it is exactly the judgment call the claims model exists to route to a
human.** A `direction-agnostic`-class slip in slow motion. Cited here as proof the model earns its keep
before it is even built.

---

## 3. The schema

A claim is a typed record. Hand-authored declarations live in `claims_declared.json` (the author's
editable surface, mirroring `outcomes_declared.json`); the materialized, provenance-headed
`claims.json` is generated from it.

```
Claim(
  id,                # kebab slug — the join key + reverse-index symbol (e.g. "direction-agnostic")
  kind,              # closed taxonomy: distinction | thesis | stance | causal | mapping |
                     #                  scope-boundary | metaphor | caveat | practice
  statement,        # the canonical proposition — a short declarative sentence (word-capped, §3.1)
  distinguishes,    # [pole_a, pole_b] — REQUIRED iff kind == "distinction"; the two poles held apart
  home,             # the primary site where the claim is chiefly argued (one outline key)
  asserted_at,      # [site, ...] — every site that states it (outline keys: section-id | chapter-slug
                    #               | part-N | book | "point:<slug>"); MULTI-site is the point
  contradicted_by,  # the AUDIT PREDICATE — a short statement of what prose would negate the claim
  watch_phrases,    # optional [str, ...] — literal candidate phrases that MAY signal a contradiction;
                    #                        feeds the soft surfacing lint (§4, C7). High-false-positive
                    #                        by design; a hit is a review candidate, never a verdict.
  relates_to,       # [typed-link, ...] — "concept:<slug>" | "definition:<term>" | "thesis:<slug>" |
                    #                      "big-idea:<slug>" | "outcome:<id>"; each resolves into a
                    #                      sibling model (join, not re-model)
  provenance,       # stated | implicit — honest labeling (§3.2)
  anchor,           # for a stated claim: the prose it rests on; for implicit: why the book only implies it
)
```

### 3.1 The statement word-cap — a point is a claim, not a paraphrase

`statement` is capped (proposed **≤ 18 words**, higher than the point-decorator's ≤10 because a claim
states a full proposition, not a paragraph point) and counted deterministically
(`statement.split()`), mirroring the existing `point-claim-word-cap` lint. The cap forces the claim to
its irreducible proposition, so the claim set reads as a spine of stances, not a second copy of the
prose. Ratify the number.

### 3.2 Provenance — the two-way honesty split

Mirrors the outcomes model's honesty discipline, at two tiers (claims need only two, not three — a
claim is a stance the book *takes*, so there is no "gap-recommended" analogue):

- **`stated`** — the book asserts it explicitly; `anchor` cites the sentence(s). The audited set.
- **`implicit`** — a load-bearing stance the book *relies on* but only implies; `anchor` says why it
  is not stated outright. This is the author's **worklist**: an implicit claim is either owed an
  explicit statement or is a genuine unstated assumption. Never masqueraded as `stated`.

### 3.3 Notation decision — model-file only, no inline markdown symbol

Same call the outcomes view made, for the same reasons (`book-models/DESIGN.md` §3.4):

- **The renderer stays uncoupled.** A model-file declaration needs no `MARKER_KEYWORDS` row and no
  renderer change — zero risk of the notation-leak an unknown inline keyword causes, and no
  reconciliation dependency on the concurrent C→A migration.
- **A `contradicted_by` predicate has no home in the prose by definition.** It describes prose that
  *should not exist*; there is no sentence to hang an inline marker on.
- **The declarations ARE the author's editable surface.** One queryable file lets the author read the
  whole stance-set at once — the reason to model it at all.

An inline `<!-- claim: <id> -->` marker beside a claim's home sentence remains a *possible later
upgrade* (it would let the model join on the marker instead of re-resolving `asserted_at` keys), added
deliberately with one `MARKER_KEYWORDS` row per the directory's §3.3 rule — explicitly **not** wired
here.

---

## 4. Invariants → enforcement (the gate mapping)

Every invariant carries a stable ID (the join key tests cite) and a severity. Following the directory's
**audit-only-first** landing discipline: the drift check lands non-blocking, a fix-wave drains the seed
findings, then a follow-up promotes the deterministic ones to blocking. Split by **mechanizability** —
the crux of the author's question.

### 4.1 Deterministic → a lint (structural + schema)

| ID | Invariant | Check |
|---|---|---|
| **C1** | Every claim's `home` and every `asserted_at` site resolves to a real outline unit (section-id / chapter / `part-N` / `book` / `point:<slug>`). | Re-resolve against the outline view + reverse index — one walk (same walk the reverse-index structural audit already does). |
| **C2** | Every `relates_to` link resolves — a `concept:` slug in `concepts.json`, a `definition:` term, a `thesis:`/`big-idea:` slug. | Join against the sibling models' key sets. A dangling link reddens. |
| **C3** | Every claim carries a **non-empty `contradicted_by`** predicate. | Schema completeness — the *honest-labeling* rule made mechanical: a claim with no contradiction predicate is not auditable, so it is a finding. |
| **C4** | `kind` ∈ the closed taxonomy; **a `distinction` claim names both poles** (`distinguishes` has exactly 2 entries). | Enum + shape check. |
| **C5** | Every claim is `asserted_at` ≥1 site **or** flagged `provenance: implicit` with an `anchor` note. | Coverage — a claim nothing in the book states is either drift or an aspirational gap; force the honest label. |
| **C6** | `statement` is within the word cap (§3.1). | `statement.split()` count — the `point-claim-word-cap` pattern. |
| **C7-drift** | `claims.json` equals a fresh regen from `claims_declared.json`. | Freshness / auto-gen provenance discipline — a stale artifact is a finding. |
| **RI** | The reverse index gains a **`claim` symbol kind**: each `asserted_at` site → a `claim-assertion` edge. | So `reverse_index.py deps <section>` answers "edit section X → which claims are asserted here?" — the drain guardrail extends to claims for free. |

These are as mechanical as the outline's O1–O4 and the outcomes' U1–U7. They catch **structural** and
**referential** drift: a claim whose site was renamed, a `relates_to` whose concept was retired, a
distinction missing a pole, a stale artifact. They do **not** read prose meaning.

### 4.2 Non-deterministic → a judgment-audit (the contradiction itself)

The `direction-agnostic` slip is **semantic**: the prose kept a valid *shape* (a grammatical sentence
citing "derived" and "the code") while **negating the stance**. No deterministic check separates "keep
the model derived from the code" (a contradiction) from "a derived model exists to kill drift" (a
correct use of the same words) — both sit in the *same scope box*. So:

**The contradiction check is a JUDGMENT-AUDIT (an agent audit at a review gate), not a blocking lint.**
This is the honest answer to the author's question. It is the semantic-drift kind the directory already
names (`book-models/DESIGN.md` §8.2 #3): "does the prose still deliver the point it claims?" — a
question you keep asking, owned by the review gate, not the pre-commit hook.

**But the model makes that audit cheap — the audit→lint spectrum applied.** Two soft aides turn a
whole-book re-read into a bounded check:

- **C7 (watch-phrase surfacing lint, AUDIT-ONLY forever).** For each claim carrying `watch_phrases`,
  grep its `asserted_at` chapters; a hit is a **candidate contradiction** surfaced for review. On the
  motivating case, `direction-agnostic`'s watch-phrase `"derived from the code"` would have surfaced
  the 3.1 sentence for a human/agent to judge. It **also** would have surfaced the two *legitimate*
  uses in the same box — that is expected. The lint narrows the judgment-audit's search from 50k words
  to ~3 sentences; it never renders a verdict, so it stays audit-only permanently (promoting it to
  blocking would redden correct prose).
- **The pre-edit consult (soft, aims the agent).** `python3 catalog.py claims <chapter>` prints the
  claims a chapter asserts and their `contradicted_by` predicates. A fresh agent editing that chapter's
  prose consults it *before* editing — the model's forward-facing use. A brief snippet ("before editing
  book prose, run `catalog.py claims <chapter>` and confirm your edit does not negate a listed stance")
  wires it into the editing workflow.

### 4.3 The reflexive payoff — the book dogfoods its own Alignment Thesis

The two aides are a **constraint** (the pre-edit consult aims the agent away from the drift) and a
**sensor** (the watch-phrase lint + judgment-audit catch it after the fact) — `constraint-prevents,
sensor-detects` applied to the book's own prose. The claims model does not just *record* the Alignment
Thesis; it *instantiates* it on the manuscript. Worth stating in the model's `_note`.

---

## 5. Where the files live

```
book-models/
  claims_declared.json   # HAND-AUTHORED source: the stance set, keyed by claim id
  claims_model.py        # types + kind taxonomy + merge/derive + regenerate/verify/consult CLI
  claims.json            # materialized model (provenance-headed, TRACKED, diffable in PRs)
  lint_claim_watch_phrases.py  # the AUDIT-ONLY surfacing lint (C7) — grep watch_phrases in cited chapters
tests/
  book_models.py         # add check_claims_model (structural C1–C6 + freshness C7-drift), registered
                         # AUDIT-ONLY in catalog_tests.py alongside check_outline_model / check_outcomes_model
reverse_index.py         # add the `claim` symbol kind + claim-assertion edges (RI)
catalog.py               # add the `claims [chapter]` query subcommand (the pre-edit consult)
```

Mirrors the outcomes view's file set exactly (declared-source → generated-artifact → model module →
audit-only check), so a reader who knows one knows the other — the directory's uniformity discipline.

---

## 6. Phased build plan

1. **Phase 1 — this design + ratify.** (This doc.) Author approves: new-model call, seed inventory,
   schema, word-cap number, the judgment-audit-not-blocking-lint boundary.
2. **Phase 2 — PoC model.** `claims_declared.json` seeded with the §2 set; `claims_model.py` (types +
   `regenerate`/`verify`); `claims.json` artifact; `check_claims_model` registered **audit-only**
   (structural C1–C6 + freshness). Reverse-index `claim` symbol kind (RI). No prose edits, no renderer
   edits.
3. **Phase 3 — the audit surface.** `lint_claim_watch_phrases.py` (C7, audit-only); the
   `catalog.py claims <chapter>` consult query; the prose-editing brief snippet. Run C7 once and record
   what it surfaces (the §2a tension is the first expected hit).
4. **Phase 4 — judgment-audit + promote.** Wire the semantic-contradiction check into the review-gate
   agent audit (the §4.2 pass). Drain the seed structural findings (dangling sites, missing predicates).
   Promote C1–C6 + freshness to **blocking** — the same drain-then-gate path `concepts.json` and the
   outline/outcomes checks took. C7 stays audit-only forever.

---

## 7. As-built vs. design

⚠️ **Nothing is built.** The entire model is design. The one real datum is the motivating case (§0):
the `6641b8a` direction-agnostic fix, which the model would have surfaced (C7 watch-phrase → judgment
audit) and whose stance it would hold as `direction-agnostic`. The §2a governance-"midway" tension is a
second real, currently-live candidate the model would surface on its first run. Every invariant ID above
is UNTESTED until Phase 2 lands its check.

---

## 8. Open calls for the author (ratify before build)

1. **New model, not an extension?** Confirm `claims.json` as a fifth sibling (§1) rather than folding
   into big-ideas or concepts. (Recommendation: new model — the contradiction predicate has no home in
   the others.)
2. **Seed inventory.** Is the §2 set of ~16 right — trim, extend, re-word any statement? In particular:
   keep `derived-not-snapshotted` and `direction-agnostic` as *separate* claims (different axes:
   snapshot-vs-derived vs. authoring-direction), or merge?
3. **`kind` taxonomy.** Approve the closed set `{distinction, thesis, stance, causal, mapping,
   scope-boundary, metaphor, caveat, practice}`? A coarser set (e.g. just distinction/stance/caveat)
   would change the schema's `kind` enum.
4. **Word cap.** ≤18 words for `statement` (§3.1) — right, or looser/tighter?
5. **The judgment-audit boundary.** Confirm the §4.2 call: the **contradiction check stays a
   judgment-audit** (agent audit at a review gate), the watch-phrase lint stays **audit-only forever**
   (surfacing aid, never a verdict), and only the structural/schema checks (C1–C6, freshness) ever go
   blocking. This is the load-bearing decision — it says what is mechanizable *now* and what stays human.
6. **Notation.** Adopt model-file-only now (§3.3); treat an inline `<!-- claim: <id> -->` marker as a
   deferred upgrade?
