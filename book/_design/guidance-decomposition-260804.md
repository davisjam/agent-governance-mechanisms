# guidance.md decomposition + independent judgment (260804)

Source: `~/Downloads/guidance.md` — "Editorial Recommendations: Structural Compression and Reader Guidance."
Author asked: PTAL, judge independently, break into additions to apply.

## The load-bearing reframe (why this matters more than the current copyedit)

Body-Wave-1 found the book already tight (~133 words of *local within-chapter* repetition in preface+Part1) and concluded 87-89K might need content-rewrites. **This guidance identifies the slack I was missing:** it's not local repetition, it's **cross-chapter RE-EXPLANATION of named concepts** (churn, the printer, GEE, governance-conversion get re-defined in full in several chapters). The fix — define once, name, then REFERENCE — is pure verbiage compression, not content loss. So this **makes 87-89K reachable without the rewrites I was worried about**, AND it's a more principled lever (the book earns its own vocabulary). This should REDIRECT the remaining copyedit.

## Independent judgment — not blanket adoption

Strong endorsement of the core thesis (compression through terminology). Nuances / mild pushback noted per item.

### CATEGORY A — Compression levers (verbiage; fold into the redirected copyedit; authorized under "run through, verbiage not content")

- **A1 = Rec #1 (name-and-reference) — THE lever, highest yield.** Define each core concept once at a canonical site, name it, and thereafter REFERENCE not re-explain. Concepts: the Printer (→ reference "the Printer" / "a Printer failure"), Churn, Governed Engineering Environment (GEE — already the catalogue's real term), Supervised Autonomy, One-shot Scripting, **Governance Conversion** (genuine MAGE contribution — name it). Requires a terminology CANON first (name + single definition site each) → needs author blessing of the vocabulary (see DECISIONS).
- **A2 = Rec #4 (anticipatory-reference cap) — clean, pure verbiage.** Delete "we'll return to…/Part 5 explains…/this will become important" except in Preface/Part-1/roadmap; cap ~4 in the whole remainder. Adopt as a book-wide copyedit rule. Zero risk.
- **A3 = Rec #8 (motivation→method, 20/80).** After ch2 the reader accepts code-is-cheap / oversight-doesn't-scale / models-matter; trim RE-motivation that restates accepted premises, keep genuine new argument. JUDGMENT: "trim re-motivation" borders on content — cut only restated-accepted-premise, never a new argument. Careful, not mechanical.
- **A4 = Rec #3 (shorten literature prose to ~1-2pp).** CAUTION: I just ran the LPP (X→Y→Z positioning). Keep the POSITIONING (where MAGE sits) + citations; cut the verbose lit TOUR prose only. Do NOT gut the LPP's positioning beats. Selective.
- **A5 = Rec #2 (story→pattern-reference).** Later stories reference the named pattern rather than re-teaching the lesson. The compression half is verbiage (adopt); the pattern-NAMING half is additive (→ B, overlaps A1).

### CATEGORY B — Content/structure additions (authoring; author-gated; propose then ratify)

- **B1 = Rec #9 (front-of-book glossary) — AUTHOR-CONFIRMED 260804: place AFTER the Preface, BEFORE Part 1 (Option A).** DUPLICATE (not move) — appendix reference stays. Supports the whole naming thesis (reader internalizes vocabulary early). Build change (a new front-matter glossary page rendered after preface) + it's the SSOT for the A1 terminology canon. ADOPTED.
- **B2 = Rec #6 (diagrams replacing prose): Governance Conversion lifecycle + Printer Loop feedback diagram.** A diagram replacing several prose pages both compresses AND clarifies — double win. Hand-SVG via self-communicate (like §3.8). RECOMMEND the 2 named ones; heed the guidance's own "avoid diagram inflation."
- **B3 = Rec #5 (explicit frameworks): Task Classification (one-shot vs supervised), Governance Conversion lifecycle, Model-or-Mechanism decision.** JUDGMENT: the guidance itself warns "avoid inventing frameworks unnecessarily; 3 strong > 10 weak." Governance-Conversion lifecycle = yes (central, pairs with B2). Task Classification may already exist as prose → elevate only. Model-or-Mechanism = genuinely recurring, worth a decision figure. Authoring — author input on framework content.
- **B4 = Rec #7 (open/close each Part with synthesis).** MILD PUSHBACK: a rigid generic "Takeaways box" per part risks flattening the book's distinct voice into textbook-feel. Adopt the ONE-SENTENCE opening (clean, skimmable); on the closing box, make it match the house voice, not a stock bullet list — or make it optional per part. Adds a little word count (paid for by A-compression).

## Sequencing
1. FINISH the in-flight local-repetition waves (still valid; don't waste them).
2. **Establish the terminology CANON** (A1 linchpin): a decision doc naming ~10-14 core concepts + their single definition site. Author blesses the vocabulary + the front-glossary (B1) decision. This gates A1 + A5 + B1.
3. **Redirected copyedit pass** book-wide: A1 (reference-not-re-explain) + A2 (anticipatory cap) + A3 (motivation→method) + A4 (lit-shorten) — THIS is where the real word reduction lands (likely gets to 87-89K honestly).
4. **Content additions** (author-ratified): B1 front glossary, B2 two diagrams, B3 frameworks (start with Governance Conversion), B4 part-synthesis.

## DECISIONS NEEDED FROM AUTHOR
1. **Bless the vocabulary + names** (A1): the terminology canon — e.g. "Printer Principle" vs "The Printer"; is "Governance Conversion" the canonical name for the observe-failure→encode-mechanism move? I'll draft the canon list from guidance for a quick yes/adjust.
2. **Front glossary (B1):** duplicate to after-Preface (Option A, guidance's pref) — adopt?
3. **Frameworks/diagrams scope (B2/B3):** all three frameworks + both diagrams, or start with Governance Conversion (the clear central one) and add others only if they earn it? (I lean: start with Governance Conversion lifecycle diagram+framework, judge the rest.)
4. **Part-synthesis (B4):** opening sentence yes; closing box — voice-matched prose vs a stock bullet takeaways box?
