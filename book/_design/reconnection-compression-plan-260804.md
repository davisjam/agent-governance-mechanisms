# Reconnection-compression plan + the "take-for-granted 5" (260804)

Author guidance 260804 (Part 3/4 examples + middle-path steer). This plan is the INDEPENDENT synthesis,
deliberately NOT the reader's research-paper density. Durable per drafts discipline.

## The reframe (author's, correct): the problem is over-RECONNECTION, not over-motivation

"The manuscript is not spending too much time motivating. It's spending time reconnecting the current
chapter to the central theses... those reconnections often use three paragraphs when they could use one
sentence invoking shared vocabulary." The edit is surgical: replace 3-paragraph thesis re-derivations
with a 1-sentence invocation of a term the reader already holds. Estimated ~10-20 pages, NOT 30%.

## The "take-for-granted 5" — DERIVED FROM THE MODELS (author asked: base it on our models)

Per-Part presence of core concept slugs (`terms:`/`section-terms:`/`index-def:` tags), measured 260804:
- **thesis-modeling — 6/6 Parts (universal)**
- **thesis-alignment — 5/6**
- churn 3, failure-to-mechanism(→governance-conversion) 4, context-window 4, governed-environment 3,
  drift-gate 3, executable-source-of-truth 3, printer-metaphor 1* (*tag undercounts — the Printer is a
  prose through-line referenced without a terms: tag; same for churn).

**The 5 we assume after Part 1 (invoke, don't reintroduce):**
1. **Modeling Thesis** (6/6 — the most-relitigated; the reader's Ex1/Ex3 are exactly this)
2. **Alignment Thesis** (5/6)
3. **The Printer** (governing metaphor, through-line)
4. **Churn** (the core problem concept)
5. **Governance Conversion** (the central method move; the reader's Ex6)

These are exactly the glossary's "core ideas" group + churn. Everything ELSE (GEE, drift-gate,
executable-source-of-truth — ~3 Parts) is legitimately re-contextualized per-Part → do NOT force-compress.

## The middle path (PROMOTE TO LOCAL STYLE — author: "probably worth promoting")

Add to `book/_design/book-editorial-discipline-directive-260802.md` (the book's editorial-discipline SSOT):
> **Reconnect in one sentence, don't re-derive.** After Part 1, the 5 core terms (Modeling Thesis,
> Alignment Thesis, the Printer, Churn, Governance Conversion) are assumed. A chapter reconnecting to a
> thesis invokes it in ONE sentence ("Part 1 argued the Modeling Thesis; this Part earns it") rather than
> re-proving it across paragraphs. This is a PEDAGOGICAL text: a middle path, not research-paper density.
> The reader should NOT need to flip to the glossary — invocation works because the term is genuinely
> internalized, not because it's looked up. Do NOT proliferate named vocabulary (a book with 45 coined
> terms loses the reader); the assumed set is ~5, chosen because they recur in every Part.

## The reconnection-compression pass (the real body edit)

Part by Part, replace 3-paragraph re-derivations of the 5 with 1-sentence invocations. ONLY genuine
re-derivation; preserve every new-context APPLICATION + all pedagogy. **Part 3 is the flagship** (reader's
examples): its opening re-derives "why models matter" (already in Preface/Part 1) → compress to a
thesis-invocation ("Part 1 argued the Modeling Thesis. This Part earns it — here are the executable models
themselves and the work each performs."). Keep Kruchten 4+1 explanation; trim only the repeated "one model
isn't enough" → "As argued in Part 1, a single model can't answer every engineering question."

## MY 3 INDEPENDENT DEPARTURES FROM THE READER

1. **Do NOT coin "Maintenance Economics Principle" (reader's Ex2).** A 6th proper noun fights the middle
   path. Instead: state the maintenance-economics inversion ONCE at its best site (Part 3), and elsewhere
   invoke it as an ASPECT of the Modeling Thesis ("the maintenance-cost inversion the Modeling Thesis rests
   on") — compression without a new term. (Author already flagged the name as unsettled — this sidesteps it.)
2. **Part 4 (reader's Ex5): a single decision TABLE, not scattered named heuristics.** If the
   doc/model/gate/lint placement decision recurs, give it ONE Part-4 reference table + a sidebar that
   re-defines each row at its first subsequent mention (author's own idea) — not N new coined heuristics.
   This overlaps guidance B3 "Model-or-Mechanism" framework. Conservative: one table, not a vocabulary.
3. **Keep pedagogy intact.** The reader's "10-20 pages, feel like Design Patterns / SE@Google" is the
   right DIRECTION but overshoots. Bound the edit to the 5; when unsure whether a reconnection is
   re-derivation or genuine new application, LEAVE it (same discipline as the prior waves).

## Sequencing
1. Glossary wave (in flight) — the reference net.
2. Diagrams wave — land governance-conversion + printer-loop SVGs (author: land, don't show; pass visual+mechanical). The gov-conversion diagram makes Ex6's "we performed governance conversion" one-sentence invocations possible.
3. Style promotion — add the middle-path principle to the editorial-discipline directive (can ride with the reconnection pass).
4. Reconnection-compression pass — Part 3 first (flagship), then scan Parts 4/5/2 for thesis re-derivations of the 5. Opus (judgment-heavy).
5. Then: F1.1 4.1-recharacterization · part-synthesis · appendix curation · REPUBLISH.
