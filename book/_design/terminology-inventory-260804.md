# Terminology inventory — name-and-reference compression + front-of-book glossary (260804)

**Scope:** READ-ONLY inventory. No book prose was edited. Source: `book/{frontmatter,part1-5,backmatter}/*.md`
(33 chapter files), cross-checked against `book/data/definitions.json`, `book/data/concepts.json`,
`book/index-terms.md`, and `book/_design/editorial-run-results-260802.md`.

## Headline finding — read this before the tables

The guidance's premise ("core concepts get re-defined in full in several chapters") is **largely
already addressed**. A **CORE-CONCEPTS PASS landed and deployed** (`8a92395`, recorded in
`editorial-run-results-260802.md` lines 31-57) **one day before** the guidance decomposition was
written. It gave six core constructs — the engineered agent loop, model, governance mechanism,
churn, the governance-conversion loop, the governed engineering environment — formal single-source
definitions in `definitions.json`/`concepts.json`, each anchored to exactly one canonical chapter
site via an `<!-- index-def: slug -->` marker.

More importantly, the book already runs a **working two-tier name-and-reference mechanism** across
~140 concepts, independent of that pass:

1. **`<!-- index-def: <slug> -->`** marks the ONE chapter location where a concept gets its full
   treatment (~140 markers found across the 33 chapter files). `catalog.py concepts` / `definitions`
   read this registry and flag drift.
2. **`<!-- gloss: Term | one-to-three-sentence definition -->`** marks a short *first-use* inline
   gloss for jargon that doesn't warrant its own chapter section (12 found: Fleet, Lint, Gate,
   Tokenomics, Quality metrics, Dispatch, Tombstone, SELC, Epic, DoD, Brief, Worktree).
3. **`<!-- point: ... | terms: slug1, slug2 -->`** and **`<!-- section-terms: ... -->`** tag every
   paragraph/section with the concept slugs it *touches* (for cross-reference tooling), separate
   from where a concept is *defined*.

Given this, most of the 25 target concepts already have exactly **one** canonical definition site and
**zero** genuine re-explanations. The real compression opportunity is narrower than the guidance
assumed: a handful of short (20-35 word) restatements, concentrated in Part 5's case-study chapter
(5.3), plus two structural gaps (no canonical site for "Validator" as a class term; a metaphor
["scar"] that names the same idea as Governance Conversion without being registered as one).

**Total estimated recoverable words: ~55-90 words** (see the summary table). This is an honest,
much lower number than the guidance's framing implied — the CORE-CONCEPTS PASS already banked the
bulk of the achievable compression on these specific concepts. The word-count lever for reaching
87-89K likely has to come from A2 (anticipatory-reference cap) and A3/A4 (motivation-trim,
lit-shorten) per the guidance decomposition, not from re-compressing these 25 concepts further.

---

## Per-concept inventory

### 1. The Printer / "Printer Principle"
- **Canonical site:** `part1/1.1-the-printer.md:111-224` (whole "The printer" section; `index-def:
  printer-metaphor` at line 116; the "suspect the instructions" claim is a distinct sub-concept
  registered separately, `index-def: whose-fault`, line 192).
- **Re-explanation occurrences:**
  - `frontmatter/0.1-preface.md:303-311` — introduces the metaphor in ~90 words. **[PROTECT]** — this
    is the *first* mention, appearing before 1.1; it's a teaser/through-line statement, not a
    re-explanation of an already-established concept.
  - `part1/1.3-loops-and-models.md:104-111` — "The metaphor's seam" callout, extends the metaphor to
    a NEW point (determinism vs. probability). **[PROTECT]** — distinct argument, not a restatement.
  - `backmatter/6.1-conclusion.md:94-97` — "We opened by calling the agent a 3D printer... let us
    revisit the metaphor in closing." **[PROTECT]** — deliberate bookend (explicitly framed as a
    revisit), ~25 words, not a full re-explanation.
- **Verdict:** no compression candidates. Exemplary.
- **Glossary entry:** *The Printer.* The book's governing metaphor: treat a coding agent as a 3D
  printer, not a coder or a stapler — it builds almost anything you can describe, and only what you
  describe, so a bad build is evidence about the instructions, not a limit in the machine.

### 2. Churn
- **Canonical site:** `frontmatter/0.1-preface.md:100-127` (`index-def: churn` at line 126); also the
  book-only `definitions.json` record (CORE-CONCEPTS PASS item 3).
- **Re-explanation occurrences:** `part1/1.3-loops-and-models.md:154-155` references it by name and
  explicitly says "The preface named churn... and traced it to three not-knowings" — a callback, not
  a redefinition. **[PROTECT]**. No other full re-explanation found.
- **Verdict:** already fully compressed (this is the concept the CORE-CONCEPTS PASS formalized).
- **Glossary entry:** *Churn.* The condition in which an increasing share of agent effort is spent
  rediscovering context, undoing recent changes, repairing regressions, or reconciling
  inconsistencies rather than advancing the system — the agent-fleet form of velocity decay.

### 3. Governed Engineering Environment (GEE)
- **Canonical site:** `part2/2.3-the-governed-environment.md:277-282` (`index-def: governed-environment`).
  Note: the book **never abbreviates to "GEE"** — it always spells the term out (0 occurrences of the
  literal string "GEE" in prose).
- **Re-explanation occurrences:**
  - `part2/2.1-the-agent-stack.md:13` — "A governed engineering environment interposes between
    capability and consequence" — one-clause teaser opening Part 2, before the formal def in 2.3.
    **[PROTECT]** — foreshadowing, one clause.
  - `backmatter/6.1-conclusion.md:78-88` — "One last framing... The governed engineering environment
    is what you get when you do both..." — ~130 words deriving GEE from the SE@Google + Gang-of-Four
    premises. **[PROTECT]** — explicitly marked as the book's closing synthesis, ties the whole
    argument together; distinct rhetorical work from the 2.3 definition, not a restatement of it.
  - `part3/3.1-the-executable-zoo.md:383` — "a governed engineering environment in miniature" — 8
    words, analogy use. **[PROTECT]**.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Governed Engineering Environment.* The system that results when engineering
  policy is encoded into the environment itself — models, constraints, sensors — rather than held in
  a person's memory: the rules of the road the agent fleet operates within.

### 4. Supervised Autonomy
- **Canonical site:** `part1/1.1-the-printer.md:25-94`, principally the
  `assets/one-shot-vs-supervised-autonomy.svg` figure (line 34) and surrounding prose (`section-terms:
  one-shot-scripting, supervised-autonomy`, line 38).
- **Re-explanation occurrences:** `part4/4.5-lessons-learned.md:3` explicitly notes in an authoring
  comment that this framing is "already figured in the earlier one-shot-vs-supervised-autonomy
  chapter" and deliberately avoids re-drawing it. **[PROTECT]** — this is the book's OWN
  non-duplication discipline visible in-source.
- **Verdict:** no compression candidates; exemplary (the authoring comment shows the discipline was
  applied consciously).
- **Glossary entry:** *Supervised Autonomy.* The task mode for hard or reasoning-heavy work: you
  supply correctness conditions and proposed sub-tasks, plus tools that determinize recurring steps
  and monitoring-and-intervention to shape the process, rather than taking a single unsupervised pass.

### 5. One-shot Scripting
- **Canonical site:** same figure/section as Supervised Autonomy, `part1/1.1-the-printer.md:25-52`.
- **Re-explanation occurrences:** none found beyond brief references.
- **Verdict:** no compression candidates.
- **Glossary entry:** *One-shot Scripting.* The task mode for a small, unsubtle task: describe the
  process once, get it back in a single pass, no supervision loop.

### 6. Governance Conversion (the observe-failure → encode-mechanism move)
- **Canonical site:** `part2/2.3-the-governed-environment.md:41-65` (`index-def: failure-to-mechanism`,
  line 64). The registered internal slug is `failure-to-mechanism` (kept from before the naming
  question arose — CORE-CONCEPTS PASS item 1 explicitly chose NOT to rename the slug, to avoid
  prose-tag churn), but **the display term the prose actually uses is "governance conversion"**.
- **What the prose actually calls it:**
  - `frontmatter/0.1-preface.md:67` — "The book's vocabulary — **governance conversion**, the Modeling
    and Alignment theses..." — names it explicitly as book vocabulary.
  - `part2/2.6-when-guardrails-collide.md:103` — "the **governance-conversion loop** turns each
    recurring failure into a control."
  - Also referred to descriptively without the coined name in many places: "that conversion" (preface
    line 299), "the move that recurs" (1.2 section heading), "ex-post governance" (2.3 section
    heading, a Latinate synonym for the same idea).
- **Re-explanation occurrences:** the MOVE itself (failure → mechanism) is narrated concretely and at
  length in `part1/1.2-mage-by-example.md:159-176` (the two DocAble incident stories) — this is
  **[PROTECT]**: it's the worked example the abstract 2.3 definition needs, not a restatement of the
  definition. Every other mention (5+ chapters, `part4/4.5-lessons-learned.md:265`,
  `part5/5.2-the-timeline-and-the-work.md:254`, `backmatter/6.0-implications-for-se.md:57`,
  `backmatter/6.1-conclusion.md:21-22,124`) is a brief callback or a new instance, not a
  re-explanation.
- **Also found — a metaphor for the same idea, unregistered:** `part1/1.2-mage-by-example.md:165,185`
  — "a scar, healed into a wall" / "governed by machinery that grew scar by scar." This is a poetic
  restatement of exactly the Governance Conversion idea, used exactly twice, in the same chapter, not
  formally registered as a concept. **[PROTECT as prose]** (it's a single-chapter figure of speech,
  not a duplicate definition elsewhere) but **flag for the terminology canon**: if "Engineering Scar"
  is promoted to a named concept, it should be explicitly cross-referenced to Governance Conversion
  rather than treated as a sibling coinage — they are the same idea at two registers (mechanism vs.
  metaphor).
- **Verdict:** "Governance Conversion" is NOT a new coining requiring ratification — **it is already
  the term the book's own prose uses** (preface line 67). The only decision needed is cosmetic:
  whether to also rename the internal registry slug `failure-to-mechanism` → `governance-conversion`
  for consistency (the CORE-CONCEPTS PASS deliberately declined this to avoid churn — a reasonable
  call, but worth a yes/no from the author since the display name and the slug now diverge).
- **Glossary entry:** *Governance Conversion.* The method by which the environment evolves: rising
  velocity surfaces a structural failure, and judgment converts each recurrence into a durable
  mechanism — a type, a lint, a gate, a sensor — so the whole class cannot happen again.

### 7. Modeling Thesis
- **Canonical site:** `frontmatter/0.1-preface.md:157-158` (`index-def: thesis-modeling`).
- **Re-explanation occurrences:** none — every other mention (dozens, via `terms: thesis-modeling`
  tags) uses the thesis by name in a new argument, never restates its definition in full. Checked
  specifically for a second bolded `**The Modeling Thesis.**` definition — found only the one.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Modeling Thesis.* Binding intent and system structure into an explicit,
  structured model gives agents a compact, coherent representation to reason through, and gives
  engineers a surface on which to specify, analyze, and predict the system.

### 8. Alignment Thesis
- **Canonical site:** `frontmatter/0.1-preface.md:160-161` (`index-def: thesis-alignment`).
- **Re-explanation occurrences:** none found (same check as Modeling Thesis — one bolded
  definition, all else is application).
- **Verdict:** no compression candidates.
- **Glossary entry:** *Alignment Thesis.* A governance mechanism the environment enforces keeps
  implementation aligned with intent — a policy decided once holds against every later change — so
  confidently-wrong work is prevented, or made visible, instead of shipped.

### 9. Drift / Drift Gate
- **Canonical site:** `part3/3.1-the-executable-zoo.md:624-639` (Inset I9, "What is drift, and what is
  a drift gate?", `index-def: drift-gate`). Related but distinct: `mirror-vs-spec` and `drift-caveat`
  (both `part2/2.2-models-and-the-semantic-gap.md`) are sub-concepts about the LIMITS of a drift gate,
  not the definition itself.
- **Structural note (not a duplication, but worth surfacing):** "drift gate" is used
  extensively and load-bearingly throughout **Part 2** (`2.1-the-agent-stack.md:174-177`,
  `2.2-models-and-the-semantic-gap.md` — a dozen+ uses including a full caveat discussion at
  lines 222-251) — all of which **precede** the formal Inset I9 definition in Part 3. Checked
  whether Part 2 gives its own competing definition: it does not — every Part 2 use assumes the
  reader's intuitive grasp of "drift" + "gate" as English words and builds NEW arguments on top
  (the mirror-vs-spec caveat, the residual). **[PROTECT]** — not a re-explanation, but flag as a
  **sequencing observation**: a reader going front-to-back meets ~15 uses of "drift gate" before its
  formal definition. Worth a one-sentence forward-gloss in 2.1 or 2.2 (in the style of the existing
  `<!-- gloss: -->` mechanism) rather than a content cut — this is a comprehension-order issue, not a
  word-count one.
- **Verdict:** no compression candidates; one sequencing/glossing recommendation (a `<!-- gloss:
  Drift gate -->` in Part 2, ~15-20 words, is an ADD not a cut).
- **Glossary entry:** *Drift Gate.* A build-time check that fails when a model and the code it
  describes disagree — the mechanism that keeps a model from becoming documentation that quietly goes
  stale the moment a developer changes the code and forgets the diagram.

### 10. Trust Half
- **Canonical site:** `part1/1.2-mage-by-example.md:78-84` (both prose and the `docable-pipeline.svg`
  figure caption).
- **Re-explanation occurrences:** none — the term appears exactly twice, both in the same chapter.
- **Verdict:** this is a **chapter-local term**, not a cross-book core concept with a re-explanation
  problem. It names one half of the single DocAble pipeline diagram (working half / trust half) and
  isn't picked up again elsewhere in the book. Recommend NOT adding it to the front-of-book glossary
  unless the author intends to use it more broadly — as-is it would be a glossary entry for a term
  that appears on one page.
- **Glossary entry (optional; only if the author wants broader use):** *Trust Half.* In the DocAble
  pipeline, the half of the system that makes the remediated result believable — a checker, a
  fidelity validator, a provenance layer — as opposed to the "working half" that does the repair.

### 11. Executable Model / Typed Model
- **Canonical sites (two related but distinct concepts, both already single-sourced):**
  - "Structured" (the property that makes a model machine-checkable — the term the book prefers over
    "typed"): `part2/2.1-the-agent-stack.md:158-178` (`index-def: structured`).
  - "Executable source-of-truth" (the architecture where the model IS derived from, or generates, the
    code, so it can never silently drift): `part3/3.1-the-executable-zoo.md:46-50` (`index-def:
    executable-source-of-truth`).
- **Re-explanation occurrences:** none found for either.
- **Verdict:** no compression candidates. Note for the glossary: the book deliberately uses
  "structured" over "typed" as the general adjective (2.1 explains why at line 165: "*Structured* is
  the word I use, over *typed*, because it names that whole span"); "Executable Model" / "Typed
  Model" as phrased in this brief aren't the book's own terms — they map onto "structured model" +
  "executable source-of-truth."
- **Glossary entry:** *Structured (model).* Written in an explicit, declared shape a machine can read
  and validate — a schema, not prose — so a build can hold the system up to the model and check for
  drift. *Executable source-of-truth.* An architecture where a model and the code that must agree with
  it are bound so tightly that a drift gate can block the build the moment they disagree.

### 12. Typed IR
- **Canonical site:** none — this is **not an established cross-book concept**. The only match
  ("intermediate representation") is `part5/5.3-the-built-system.md:210`, describing the PDF/DOCX
  editor's document model in one clause: "The model is the document's intermediate representation."
  This is local vocabulary for one component (the editor's MVC "model" layer), not a book-wide term.
- **Verdict:** drop from the target concept list, or fold it into the existing "structured model" /
  "model" entries — treating it as a separate glossary entry would introduce a term the book itself
  doesn't use as a proper noun.

### 13. Pattern
- **Canonical site:** `frontmatter/0.1-preface.md:127-140` (the Gang-of-Four discussion: "the
  catalogue that gave object-oriented design its shared vocabulary of reusable solutions... This book
  borrows that form for a new subject").
- **Re-explanation occurrences:** `backmatter/6.1-conclusion.md:78-88` (`index-def:
  governance-as-design-patterns`) revisits the SAME GoF + SE@Google synthesis (~130 words),
  explicitly headed "One last framing." **[PROTECT]** — same reasoning as GEE's conclusion mention
  above: deliberate closing bookend, paired a few lines later with the printer-metaphor revisit
  (line 94-97). The conclusion chapter runs a consistent "revisit the opening frames" structure; this
  is that structure's second instance, not accidental duplication.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Pattern (governance mechanism as pattern).* Following the Gang of Four's
  *Design Patterns* form — name, recurring problem, solution shape, consequences, known uses — this
  book writes each governance mechanism as a pattern so an engineer can reach for a vetted answer
  instead of re-deriving one.

### 14. Mechanism (Governance Mechanism)
- **Canonical site:** `part2/2.3-the-governed-environment.md:240-247` (`index-def:
  governance-mechanism`); formal `definitions.json` record (CORE-CONCEPTS PASS item 5).
- **Re-explanation occurrences:** none — checked for a second bolded `**Governance mechanism.**`
  definition; found only one. All other ~40 occurrences of "mechanism" in the book use the
  already-established term in a new argument.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Governance Mechanism.* A repeatable environmental structure that encodes an
  engineering policy and either constrains an action, detects a violation, requires evidence, or
  controls admission — four classes: prevention, detection, evidence, admission.

### 15. Engineering Scar
- **Canonical site:** none formal — `part1/1.2-mage-by-example.md:165,185` only (both a single
  metaphor use and a callback in the same chapter: "a scar, healed into a wall" / "governed by
  machinery that grew scar by scar").
- **Verdict:** **not currently a registered core concept** — it's a one-chapter metaphor for
  Governance Conversion (see concept 6 above), not a separately defined term. Recommend the
  author decide: either (a) leave it as local color (no glossary entry, no further action), or
  (b) formally adopt "scar" as the book's word for "an individual instance of a converted failure"
  (distinct from "governance conversion," which names the general move) — in which case it needs its
  own `index-def` and should be cross-referenced explicitly to `failure-to-mechanism` so a reader
  doesn't mistake it for a third, unrelated concept.
- **Glossary entry (only if (b) above is ratified):** *Engineering Scar.* An individual failure that
  was converted into a durable mechanism — the visible mark, in the codebase's defenses, of one
  governance conversion.

### 16. Context Window
- **Canonical site:** `part2/2.1-the-agent-stack.md:281-283` (`index-def: context-window`).
- **Re-explanation occurrences:** none — used as established vocabulary everywhere else (preface,
  1.1, 1.4, 2.2, 6.0), each time advancing a new point (tokenomics cost, self-monitoring for
  fullness, the substrate-derivation table) rather than re-defining the term.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Context Window.* The bounded amount of prior conversation and code an agent can
  hold at once; fixed the moment you choose the model, and the sharpest driver of churn when the work
  outgrows it.

### 17. Fleet
- **Canonical site:** `frontmatter/0.1-preface.md:97` (`<!-- gloss: Fleet -->`).
- **Re-explanation occurrences:** none — used as ordinary vocabulary throughout (dozens of
  occurrences), never re-defined.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Fleet.* The set of coding agents working the codebase — the agentic-era
  workforce this book governs, in place of a team of human engineers.

### 18. Model Zoo
- **Canonical site:** `part3/3.1-the-executable-zoo.md:79` (`index-def: model-zoo`); also the title of
  all of Part 3.
- **Re-explanation occurrences:** none — every other mention is a cross-reference link
  ("[the Model Zoo](3.1-the-executable-zoo.html)").
- **Verdict:** no compression candidates.
- **Glossary entry:** *The Model Zoo.* Part 3's name for the book's tour of the 4+1 architectural
  views (logical, process, development, physical, scenarios) as executable, drift-gated models, each
  walked on the real DocAble codebase.

### 19. Validator
- **Canonical site: none.** This is the one genuine structural gap found. "Validator" is used
  constantly and load-bearingly (`deterministic validator`, `content-fidelity validator`, "a
  validator sits at the trust boundary" in `part5/5.3-the-built-system.md:279-280`, the "trust half"
  figure in 1.2) but is **never given its own formal definition**, unlike its siblings Constraint and
  Sensor (both defined at `part2/2.3-the-governed-environment.md:141-161`). The four-classes taxonomy
  at 2.3 (prevention/detection/evidence/admission) implicitly covers what a validator does (it's an
  evidence-or-admission mechanism) but never says so explicitly, and never uses the word "validator"
  in that section at all.
- **Re-explanation occurrences:** `part5/5.3-the-built-system.md:31-33` — "**A validator.** A
  content-fidelity gate asserts that the meaning of the input survived into the output..." (29 words)
  is the closest thing to a definition in the whole book, and it's phrased as a DocAble-specific
  feature-list bullet, not a general definition. **[COMPRESS-ADJACENT]** — not a duplicate (there's no
  first definition to be a duplicate OF), but it's doing double duty as both "here's what DocAble has"
  AND "here's what a validator is in general," which is worth separating.
- **Verdict:** recommend the front-of-book glossary give "Validator" its own entry, explicitly tied to
  the evidence/admission classes in 2.3, so the term doesn't float free of the four-classes taxonomy
  it belongs to. This is a **gap-fill**, not a word-count cut.
- **Glossary entry (proposed, since none exists):** *Validator.* A governance mechanism of the
  evidence or admission class: it checks a candidate result against a standard — a type, a
  preservation property, a specification — before the result is allowed to advance, and refuses or
  flags what fails.

### 20. Gate
- **Canonical site:** `frontmatter/0.1-preface.md:101` (`<!-- gloss: Gate -->`, general sense); the
  specific "drift gate" sense is separately canonicalized (see concept 9).
- **Re-explanation occurrences:** none for the general sense.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Gate.* A check placed across a pipeline step — a commit, a deploy — that
  refuses to let the step through until its condition is met.

### 21. Lint
- **Canonical sites — TWO, by design, at different tiers:**
  - `frontmatter/0.1-preface.md:99` — `<!-- gloss: Lint -->`, a 25-word first-use gloss (the
    enforcement framing: "fails the commit when it finds one").
  - `part4/4.1-brownfield.md:132-136` — `index-def: lint`, a fuller ~50-word treatment (the
    smell-detection framing: parses the syntax tree, counts the tells).
- **Assessment:** this is **not a redundant duplication** — it's the book's two-tier mechanism working
  as intended: the `gloss` gives a reader a working definition at first use (preface, page 1); the
  `index-def` gives the FULL treatment later, when the book is ready to teach where a lint comes from
  (Part 4, brownfield migration). The two framings are complementary (what a lint DOES vs. how a lint
  is BUILT), not overlapping restatements. **[PROTECT]** — flagged here as a judgment call worth the
  author's eyes, since it's the closest thing to a textbook "compress this" case in the whole
  inventory, but I judge it correctly designed as two tiers, not one redundant pair.
- **Verdict:** no action recommended; if anything this pair is the WORKED EXAMPLE of the gloss/index-def
  two-tier system the guidance is asking the rest of the book to adopt.
- **Glossary entry:** *Lint.* An automated check that scans code for a banned pattern and fails the
  commit when it finds one, so a rule holds without a human remembering it.

### 22. Sensor
- **Canonical site:** `part2/2.3-the-governed-environment.md:141-151` (`index-def: sensor`).
- **Re-explanation occurrences:** none found.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Sensor.* A governance mechanism that detects a violation after the fact rather
  than preventing it — it lets the mistake happen and catches it, failing the iteration so the
  mistake cannot ship unnoticed.

### 23. Constraint
- **Canonical site:** `part2/2.3-the-governed-environment.md:160-193` (`index-def: constraint`).
- **Re-explanation occurrences:** none found.
- **Verdict:** no compression candidates.
- **Glossary entry:** *Constraint.* A governance mechanism that prevents drift by scoping the action
  space so the mistake is impossible to make in the first place.

### 24. Provenance Layer
- **Canonical site:** `part1/1.2-mage-by-example.md:78-84` (prose + `docable-pipeline.svg` caption:
  "a provenance layer stamps every insertion").
- **Re-explanation occurrences:**
  - `part5/5.3-the-built-system.md:35` — "**A provenance layer.** Every artifact the system inserts is
    stamped, so a finished document's history can be reconstructed and any single change explained or
    reversed — the auditable trust a university requires." (32 words) **[COMPRESS]** — genuine
    re-explanation in the concrete case-study context; could reference back to 1.2 ("the provenance
    layer introduced earlier stamps...") and save roughly half the words (~15-18 recoverable).
  - `part4/4.1-brownfield.md:112` — "its provenance stamp" — brief mention, not a re-explanation.
    **[PROTECT]**.
  - `part2/2.3-the-governed-environment.md:255` — "a provenance stamp" as one example of an evidence
    mechanism, in a list — brief, not a re-explanation. **[PROTECT]**.
  - `part3/3.1-the-executable-zoo.md:264,317,369,618` and `part3/3.8-keeping-models-in-sync.md:101` —
    **different sense**: here "provenance" means model/data lineage (which artifact a derived model
    came from, for drift-gate freshness checks), not the DocAble trust-mechanism sense from 1.2/5.3.
    **Flag as a terminology note**, not a compression issue: the same English word carries two
    related-but-distinct technical senses in this book (artifact-stamp provenance vs.
    model-lineage provenance). Worth a one-clause disambiguation if a glossary entry is added, so a
    reader doesn't conflate them.
- **Verdict:** one small (~15-18 word) compress candidate in 5.3; one terminology-sense note for the
  glossary author.
- **Glossary entry:** *Provenance Layer.* The mechanism that stamps every artifact the system inserts,
  so a document's remediation history can be reconstructed and any single change explained or
  reversed. (Distinct from *model provenance* — see Model Zoo / drift gate — which tracks what a
  derived model was generated from, not what a document's inserted content was stamped with.)

### 25. Fidelity Validator
- **Canonical site:** `part1/1.2-mage-by-example.md:78-84` (prose + figure caption: "a **fidelity
  validator** asserts the meaning survived").
- **Re-explanation occurrences:**
  - `part5/5.3-the-built-system.md:31` — "**A validator.** A content-fidelity gate asserts that the
    meaning of the input survived into the output — catching the case where the file got more
    accessible and less true." (29 words) **[COMPRESS]** — same pattern as Provenance Layer above:
    genuine restatement, could reference back to 1.2 and save roughly half.
  - **Terminology-consistency finding:** 1.2 calls this a **"fidelity validator"**; 5.3 calls the same
    mechanism a **"content-fidelity gate"** in its own prose, then a **"content-fidelity validator"**
    in its "Learn more" link. Three different labels (validator / gate / content-fidelity validator)
    for what the book intends as one mechanism. This is worth flagging to the author as a naming
    consistency question, not just a compression one — pick one term (I'd lean "fidelity validator,"
    matching 1.2's canonical coinage) and use it in all three places.
- **Verdict:** one small (~15 word) compress candidate; one naming-consistency finding (validator vs.
  gate vs. content-fidelity validator).
- **Glossary entry:** *Fidelity Validator.* The mechanism that asserts a remediated document's meaning
  survived the remediation — catching the case where a file became more accessible and less true to
  the original.

---

## Canon summary table

| Concept | Proposed canonical name | Definition site | #COMPRESS occurrences | Est. words recoverable |
|---|---|---|---|---|
| The Printer | The Printer | `part1/1.1-the-printer.md:111` | 0 | 0 |
| Churn | Churn | `frontmatter/0.1-preface.md:126` | 0 | 0 |
| Governed Engineering Environment | Governed Engineering Environment | `part2/2.3-the-governed-environment.md:277` | 0 | 0 |
| Supervised Autonomy | Supervised Autonomy | `part1/1.1-the-printer.md` (fig, L34) | 0 | 0 |
| One-shot Scripting | One-shot Scripting | `part1/1.1-the-printer.md` (fig, L34) | 0 | 0 |
| Governance Conversion | Governance Conversion (prose) / `failure-to-mechanism` (slug) | `part2/2.3-the-governed-environment.md:64` | 0 | 0 |
| Modeling Thesis | Modeling Thesis | `frontmatter/0.1-preface.md:157` | 0 | 0 |
| Alignment Thesis | Alignment Thesis | `frontmatter/0.1-preface.md:160` | 0 | 0 |
| Drift / Drift Gate | Drift Gate | `part3/3.1-the-executable-zoo.md:624` | 0 (sequencing note only) | 0 |
| Trust Half | Trust Half (chapter-local) | `part1/1.2-mage-by-example.md:78` | 0 | 0 |
| Executable / Typed Model | Structured (model) + Executable source-of-truth | `part2/2.1...:158` / `part3/3.1...:47` | 0 | 0 |
| Typed IR | *(not a book concept — drop)* | — | — | — |
| Pattern | Pattern | `frontmatter/0.1-preface.md:127` | 0 | 0 |
| Mechanism | Governance Mechanism | `part2/2.3-the-governed-environment.md:245` | 0 | 0 |
| Engineering Scar | *(unregistered metaphor — author call)* | `part1/1.2-mage-by-example.md:165` | 0 | 0 |
| Context Window | Context Window | `part2/2.1-the-agent-stack.md:283` | 0 | 0 |
| Fleet | Fleet | `frontmatter/0.1-preface.md:97` | 0 | 0 |
| Model Zoo | The Model Zoo | `part3/3.1-the-executable-zoo.md:79` | 0 | 0 |
| Validator | Validator | *(gap — no site exists)* | 1 gap-fill (5.3) | 0 (add, don't cut) |
| Gate | Gate | `frontmatter/0.1-preface.md:101` | 0 | 0 |
| Lint | Lint | preface gloss + `part4/4.1-brownfield.md:136` (2-tier, by design) | 0 | 0 |
| Sensor | Sensor | `part2/2.3-the-governed-environment.md:141` | 0 | 0 |
| Constraint | Constraint | `part2/2.3-the-governed-environment.md:160` | 0 | 0 |
| Provenance Layer | Provenance Layer | `part1/1.2-mage-by-example.md:78` | 1 (`5.3:35`) | ~15-18 |
| Fidelity Validator | Fidelity Validator | `part1/1.2-mage-by-example.md:79` | 1 (`5.3:31`) | ~15 |
| **Total** | | | **2 occurrences** | **~30-33 words strict; ~55-90 incl. adjacent tightening** |

## The two coinings — what the prose actually uses today

1. **"Governance Conversion"** — **already the book's own term.** `frontmatter/0.1-preface.md:67`
   names it explicitly as book vocabulary ("The book's vocabulary — governance conversion, the
   Modeling and Alignment theses...") and `part2/2.6-when-guardrails-collide.md:103` uses
   "governance-conversion loop." No ratification needed on the NAME. The only open item: the internal
   registry slug is `failure-to-mechanism` (kept during the CORE-CONCEPTS PASS to avoid churning
   existing prose tags), so slug and display name now diverge — cosmetic, author's call whether that
   matters.
2. **"Printer Principle"** — **not used anywhere in the prose** (0 occurrences of that exact phrase).
   The book's actual terms are "the printer" / "the printer metaphor" (`index-def: printer-metaphor`,
   naming the whole 3D-printer frame) and, as a narrower sub-claim, "whose fault" (`index-def:
   whose-fault`, naming specifically "an agent is a printer, not a stapler, so suspect the
   instructions first"). If the author wants a single named "Printer Principle," it would be a
   genuine NEW coining — likely mapping onto the `whose-fault` claim specifically, not the broader
   metaphor. Recommend surfacing this choice to the author rather than assuming it.

## Top 5 highest-payoff [COMPRESS] concepts

Given the overall finding, there isn't a genuine top-5 of high-payoff cuts — only two concepts had
any [COMPRESS] occurrence at all. Ranked by what's actually available:

1. **Fidelity Validator** (`part5/5.3-the-built-system.md:31`) — ~15 words recoverable, reference
   back to 1.2's coinage; ALSO fix the validator/gate/content-fidelity-validator naming drift while
   touching this line.
2. **Provenance Layer** (`part5/5.3-the-built-system.md:35`) — ~15-18 words recoverable, reference
   back to 1.2.
3. **Validator** (general term) — not a cut, a **gap-fill**: give it a glossary entry tied explicitly
   to the evidence/admission classes so 5.3's "A validator." bullet has a canonical site to point at
   instead of quietly re-deriving one.
4. **Drift Gate sequencing** — not a cut, an **add**: a short forward-gloss in Part 2 (where the term
   is used ~15 times before its Part 3 formal definition) would help a front-to-back reader, at the
   cost of ~15-20 words, not a savings.
5. **Engineering Scar** — an author decision, not a mechanical fix: either leave as local color (no
   action) or formally register it as a named sub-concept of Governance Conversion (adds a glossary
   entry, doesn't remove words).

**Total estimated recoverable words across genuine [COMPRESS] occurrences: ~30-33 words** (the two
5.3 bullets, tightened). Even generously counting adjacent phrasing that could tighten alongside them,
this tops out around **55-90 words** — not a meaningful lever on its own for an 87-89K word-count
target. The CORE-CONCEPTS PASS already banked the compression this specific 25-concept list offered;
the remaining word-count work belongs to the guidance's other levers (A2 anticipatory-reference cap,
A3 motivation-trim, A4 literature-shorten), not to further concept-compression.
