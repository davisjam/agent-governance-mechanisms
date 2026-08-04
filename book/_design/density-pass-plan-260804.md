# Progressive-density pass — plan + the refined principle (260804)

Supersedes the "reconnection-compression" framing in `reconnection-compression-plan-260804.md` with the
author's cleaner articulation (260804). The take-for-granted-5 data + my 3 departures from that doc still hold.

## THE PRINCIPLE (author, verbatim intent — promote to the book's writing style)

**Make the explanations shorter, not the ideas.** Two axes that were being conflated:
- **Abstraction stays HIGH.** Don't dumb the book down. The ideas keep their full altitude.
- **Exposition SHRINKS** as the reader learns the vocabulary.

So later chapters become **denser, not simpler** — the discourse gets *more* abstract because it assumes
internalized concepts. This is *Design Patterns*' own progression: early on Gamma et al. explain what a
pattern IS; by chapter 5 they write "Use Strategy here" and move on. **Exploit the reader's accumulated
knowledge:** as the book progresses, increasingly rely on previously-introduced terminology instead of
re-explaining it. It is less about cutting words than about **letting the book's language do more work over time.**

Example: Part 1 spends two pages introducing the Printer — appropriate (first introduction). A Part-4
chapter that reopens with another two-page meditation on why agents are printers is waste; it should just
say "the Printer tells us to suspect the instructions before the model" and move — which is *more*
abstract, because it assumes the concept is held. (Note: the book's term is "the Printer," capital P — no
"Principle" coinage, per the author's earlier ruling. The invocation is dense, not cute.)

**This REPLACES round-1 recommendation #4 (anticipatory-reference cap)** — that was a symptom; this is the
disease. (The anticipatory-cap still applies as a minor sub-case.)

## WHERE IT LANDS (author: "update writing style")
- Primary: the self-communicate writing SSOT (`plugin/mage/skills/self-communicate/writing/voice.md`) —
  a general "progressive density" principle (applies to any long-form technical text).
- Book-specific operationalization: `book/_design/book-editorial-discipline-directive-260802.md` — the
  take-for-granted-5 + the per-chapter "what came before" method below.

## THE SYSTEMATIC PER-CHAPTER REVIEW (author: "have writing agents systematically review each Chapter
based on the models and glossary so they know what came before")

The enabling move: each chapter's editing agent is given **the accumulated vocabulary established BEFORE
that chapter**, computed from the models, so it can tell a *first introduction* (keep full) from a
*re-explanation* (compress to a dense invocation).

**"What came before" = DERIVED FROM THE MODELS (not guessed):**
- For chapter N in reading order, the established set = every concept whose `<!-- index-def: slug -->`
  canonical site is in a chapter BEFORE N, PLUS the front glossary (which front-loads the core terms), PLUS
  the take-for-granted-5 (assumed after Part 1).
- Precompute a per-chapter manifest: `chapter → [concepts already introduced]`. This is a read-only pass
  over the index-def ordering (run AFTER the glossary wave lands, so the canon incl. the slug-rename +
  Validator + glossary is final).

**Each per-chapter review agent gets:** (a) its chapter, (b) its "established-before" concept list, (c) the
front glossary, (d) the density principle. It then, for each place the chapter explains a concept:
- **First introduction of a NEW concept** (its index-def is HERE) → keep the full exposition. Altitude high.
- **Re-explanation of an ALREADY-established concept** → compress to a one-sentence dense invocation that
  ASSUMES the reader holds it. Never re-derive. Keep the new APPLICATION/argument the chapter makes with it.
- Preserve every idea, incident, number, citation, real-world detail, and voice. When unsure first-vs-re,
  check the index-def: if the canonical site is elsewhere-earlier, it's a re-explanation → compress.

**Order:** reading order (fm → part1 → … → backmatter), because "what came before" only accumulates
correctly forward. Part 1 chapters change least (they DO the first introductions); density gains grow
toward Parts 3-5 (the reader holds the most by then) — matching the reader's own observation that Part 3+
is where the compression lives.

**Bounded, middle-path (my departures still hold):** high-abstraction not research-paper density; the
reader must NOT need to flip to the glossary (invocation works because the term is genuinely internalized);
no vocabulary proliferation (no new coinages — the ~5 core + the existing index-def set); Part-4 gets one
decision TABLE not scattered heuristics; keep Kruchten/pedagogy.

## SEQUENCING
1. Glossary wave (in flight) — establishes the canon + front glossary the pass depends on.
2. Diagrams wire (SVGs prepped + fit-clean: `governance-conversion-loop.svg`, `printer-loop.svg`) + nav impl.
3. **Style update** — the density principle → voice.md + the editorial directive (step 1 of the density pass, committed).
4. **Compute the per-chapter established-vocabulary manifest** (read-only, from index-def ordering, post-glossary).
5. **The density pass** — reading-order, per-chapter (or per-Part) review agents, each armed with its
   established-before set + glossary + the principle. Opus (judgment-heavy). This is the main body edit;
   honest word delta reported (the real ~10-20 pages, concentrated in Parts 3-5).
6. F1.1 4.1-recharacterization · part-synthesis · appendix curation · REPUBLISH.
