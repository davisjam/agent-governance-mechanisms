# STYLE-RHETORIC.md — a rhetoric toolkit for technical prose

This is an **agent-facing** style doc — a resource of the `self-communicate` skill, not a catalogue entry.
It is not rendered to HTML or served.

## Why this file exists

The so-called "LLM tells" — the em-dash everywhere, the rule of three, the reflexive "not X, but Y" —
are not defects. They are **classical rhetorical devices** that have worked for two thousand years. The
problem is never the device. The problem is **mechanical overuse and sameness**: the same three figures on
repeat, at the same cadence, until the prose reads as a machine running one loop.

The fix is not to ban the figures. The fix is a **broad toolkit used with variety and taste**. A tricolon
lands when it is the *only* tricolon on the page; it becomes a tic when every paragraph has one. So:

- **Variety and fit are the craft.** Reach for the figure that fits the sentence, and don't reach for the
  same one twice in a row.
- **Any single figure on repeat is the tell.** Count your em-dashes. Count your rule-of-threes. If one
  device recurs on a fixed beat, that recurrence — not the device — is what a reader clocks as artificial.
- **Match the house voice.** See [`STYLE-VOICE.md`](STYLE-VOICE.md) for how the house author actually
  deploys these. He uses many of them; he varies constantly; he leans on the period and the plain word as
  often as the dash.

Below: the toolkit, grouped by what the device *does*. For each — **name · definition · a
technical-writing example · a "use tastefully" note** (when it lands, when it becomes a tic).

---

## Group 1 — Balance & parallelism

- **Tricolon (the rule of three)** · three parallel phrases or clauses in a row. · *"It fails fast, it
  logs the cause, and it surfaces a typed error."* · **Tastefully:** one strong tricolon per section is
  memorable; three tricolons on one page is the single most recognizable LLM cadence. Vary the count —
  sometimes list two, sometimes four.
- **Isocolon** · successive clauses of equal length and matching structure. · *"Guidance aims; machinery
  holds."* · **Tastefully:** the symmetry is the point — use it when the two halves genuinely balance.
  Forcing equal length on unequal ideas reads as sing-song.
- **Antithesis** · two contrasting ideas set in parallel structure. · *"A wrong remediation is worse than
  a slow one."* · **Tastefully:** superb for a sharp contrast. But a whole document written in
  antithesis-cadence (every sentence a this-versus-that) flattens into monotony — let some sentences just
  assert.
- **Parallelism** · matching grammatical shape across successive clauses. · *"Read via the model, write via
  the model, validate via the model."* · **Tastefully:** parallel structure aids scanning. Break it
  deliberately when you want one item to stand out.
- **Chiasmus** · two parallel phrases with the second reversing the order of the first (ABBA). · *"We test
  what we ship and ship what we test."* · **Tastefully:** striking once; precious if overused. Save it for
  a claim you want quoted.
- **Antimetabole** · chiasmus done at the word level — the same words reversed for contrast. · *"The map
  equals the territory, or the territory has outrun the map."* · **Tastefully:** the most quotable figure
  and the most easily overcooked. One per document, at most.
- **Climax (gradatio)** · phrases arranged in rising order of force. · *"It slows the build, then breaks
  the gate, then blocks the release."* · **Tastefully:** builds momentum toward a payoff. Needs a genuine
  escalation, or it feels padded.

## Group 2 — The "not X, but Y" family (correction & contrast)

These are the figures behind the reflexive "not X, but Y" tell. Named precisely, they are three different
moves — and knowing which one you mean is how you stop defaulting to the same phrasing.

- **Correctio** · retract a first framing and replace it with a sharper one. · *"The gate isn't slow — it
  is thorough, which costs a few seconds."* · **Tastefully:** use it to *redefine*, so the two halves
  carry different content. If Y merely restates X in nicer words, cut the setup and just say Y.
- **Antithesis (as "not X, but Y")** · the contrastive form: reject X, affirm the opposing Y. · *"Not a
  faster path, but a correct one."* · **Tastefully:** the canonical LLM cadence. It is fine occasionally
  and deadly on repeat. When you catch a third "not X, but Y" in a page, rewrite two of them as plain
  claims.
- **Metanoia** · qualify or walk back a statement you just made, mid-stride. · *"It catches every case —
  or every case we've named a test for."* · **Tastefully:** honest and human when the qualification is
  real. A crutch if every claim gets one; sometimes a claim should stand unqualified.

## Group 3 — Omission & addition

- **Asyndeton** · drop the conjunctions. · *"It builds, tests, lints, ships."* · **Tastefully:** speeds a
  list and adds urgency. Overused it reads clipped and breathless.
- **Polysyndeton** · pile the conjunctions on. · *"The worker crashes and the job stalls and the queue
  backs up and nothing surfaces."* · **Tastefully:** conveys accumulation or dread. A rare tool — one use
  per document lands; more feels mannered.
- **Zeugma** · one verb governs two objects in different senses. · *"The lint caught the bug and the
  reviewer's eye."* · **Tastefully:** a clever grace note. Deploy at most once, where the double meaning is
  actually apt; a strained zeugma is worse than none.
- **Hendiadys** · express one idea with two nouns joined by "and". · *"the noise and confusion of an
  undocumented seam."* · **Tastefully:** adds texture. In terse technical prose it often just doubles a
  word — prefer one precise noun unless the pair earns its keep.

## Group 4 — Repetition for structure

- **Anaphora** · successive sentences open with the same words. · *"It must fail loud. It must log the
  cause. It must leave a typed error."* · **Tastefully:** powerful for a deliberate build. Two or three
  repetitions land; a fourth tips into oratory that clashes with plain technical prose.
- **Epistrophe** · successive clauses *end* with the same words. · *"The lint enforces it. The gate
  enforces it. The reviewer trusts that both enforce it."* · **Tastefully:** rarer and quieter than
  anaphora — use when the repeated tail is the point.
- **Symploce** · anaphora and epistrophe together (same start and end). · *"We govern the agent, we govern
  the model, we govern the product."* · **Tastefully:** strong closing figure; one per document.
- **Epizeuxis** · repeat a single word for emphasis. · *"This path is slow, slow enough to notice."* ·
  **Tastefully:** a spotlight. Once, on the word that matters.
- **Anadiplosis** · begin a clause with the word that ended the last. · *"The gate blocks the merge; the
  merge that would have shipped the regression."* · **Tastefully:** chains ideas smoothly. A whole
  paragraph of it becomes a gimmick.

## Group 5 — Objection-handling (the "they say / I say" moves)

- **Hypophora** · pose the question the reader is forming, then answer it. · *"Why not just review for it?
  Because review is post-hoc and the lint is at-commit."* · **Tastefully:** excellent for pacing an
  argument. Overused it turns every point into a mock-Socratic dialogue.
- **Procatalepsis / prolepsis** · raise and rebut an objection before the reader can. · *"You might say
  this is over-engineered. It isn't: the failure it prevents cost us a release."* · **Tastefully:** the
  strongest tool for a contested claim. Deploy on the two or three objections that actually bite, not on
  every claim.
- **Praeteritio (paralipsis)** · mention a thing by declining to dwell on it. · *"I'll set aside the
  obvious cost argument and focus on correctness."* · **Tastefully:** useful to acknowledge-and-move-on.
  Reads as coy if you "decline" to discuss what you clearly want to.
- **Aporia** · a stated (often feigned) doubt, for rhetorical setup. · *"It's not obvious which failure
  this even is."* · **Tastefully:** honest when the doubt is real and you then resolve it. Skip the feigned
  version in technical writing — it wastes the reader's time.

## Group 6 — Understatement, emphasis & substitution

- **Litotes** · affirm by negating the opposite; understatement. · *"This is not a cheap check to run."* ·
  **Tastefully:** dry emphasis. A page of double negatives is hard to parse — use sparingly and never
  stack two litotes in one sentence.
- **Metonymy** · name a thing by something closely associated with it. · *"the merge train" for the batched
  landing pipeline.* · **Tastefully:** natural and compact when the association is shared. Obscure metonymy
  confuses a reader who lacks the reference — the interpretability rule bites here.
- **Rhetorical question** · a question posed for effect, not an answer (often paired with hypophora). ·
  *"What good is a gate that never fires?"* · **Tastefully:** sharpens a point. A cluster of them reads as
  padding; convert most to plain assertions.
- **Direct address** · speak to the reader as "you". · *"You'll hit this the first time two agents share a
  worktree."* · **Tastefully:** warms the prose and matches the house voice. Keep it occasional — constant
  second-person turns instructional prose preachy.

---

## The one rule that governs all of them

Every figure above is legitimate. The tell is never a single use — it is **sameness and density**: the
same figure on a fixed beat, or a paragraph so dense with figures that the argument disappears under the
ornament. Write the point plainly first. Then reach for *one* figure where it genuinely sharpens the
sentence, and reach for a *different* one next time.
