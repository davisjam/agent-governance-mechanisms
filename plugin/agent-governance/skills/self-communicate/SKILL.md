---
name: self-communicate
description: >-
  Write and diagram engineer-facing documentation well — the third partner skill
  in the govern / operate / communicate trio. Use when authoring or auditing any
  prose an engineer or a coding agent reads: a control's description, a mechanism
  entry, a design doc, a runbook, a handoff, a README, a tutorial, an ADR, an API
  reference. Two legs. PROSE — the rhetoric toolkit (classical figures, used with
  variety so the prose doesn't read as machine-uniform), the Diátaxis engineering
  register (tutorial / how-to / reference / explanation), a house lexicon that
  names concepts consistently, the target voice, and an audit procedure that grades
  a passage and emits concrete fixes. VISUALIZATION — technical-diagram types,
  Mermaid-first, with a narrow hand-authored-SVG escape hatch. Also bootstraps a
  house vocabulary by walking a codebase and keeps it living. Use whenever prose
  quality, doc structure, term consistency, LLM-tell density, or a technical diagram
  is in hand.
---

# self-communicate — write and diagram engineer-facing docs well

You are communicating **the way the work is explained** in this repository — the prose and diagrams an
engineer or a coding agent reads to understand it. This is the *communicate* leg of a trio: **govern /
operate / communicate.** [`self-governance`](../self-governance/SKILL.md) is the *harden* leg (the census
of controls and the engine that mints new ones); [`self-operations`](../self-operations/SKILL.md) is the
*operate* leg (running the substrate those controls govern). This skill makes the writing those two
produce — control descriptions, design docs, mechanism entries, runbooks, handoffs — clear, consistent,
and readable.

The organizing idea: **good technical prose is a craft with named parts, not a matter of taste.** Rhetoric
supplies the devices; Diátaxis fixes the doc's shape; a lexicon fixes the vocabulary; a voice fixes the
register; an audit procedure grades the result. Diagrams are the same craft for shapes prose can't carry.
None of this is invented per document — you reach into a toolkit and apply it.

## The two legs

- **Prose** — the argument, carried in sentences. Five resources, applied in order.
- **Visualization** — the shape, carried in a diagram. One resource, Mermaid-first.

### Prose — the five resources, in order

1. **Rhetoric (the basis).** [`STYLE-RHETORIC.md`](STYLE-RHETORIC.md) — the device toolkit. The
   "LLM tells" (the universal em-dash, the mechanical tricolon, the reflexive "not X, but Y") are
   classical figures, not defects; the tell is *sameness and density*, the same figure on a fixed beat.
   Draw variety from the toolkit so no one figure recurs every beat.
2. **Engineering discourse / Diátaxis (the shape).** [`STYLE-ENGINEERING.md`](STYLE-ENGINEERING.md) —
   fixes the *shape* of a doc via the four Diátaxis modes (tutorial / how-to / reference / explanation).
   Decide the mode first; a how-to written as an explanation confuses the reader. The
   [`STYLE-DIAGRAMS.md`](STYLE-DIAGRAMS.md) leg pairs a diagram type to each mode.
3. **Lexicon (the vocabulary).** [`STYLE-LEXICON.md`](STYLE-LEXICON.md) — the house vocabulary of
   engineering terms-of-art, so the prose names an established idea and links it rather than re-describing
   it each time. Pick one word per concept and say it everywhere.
4. **Voice (the sensibility).** [`STYLE-VOICE.md`](STYLE-VOICE.md) — the target register with verbatim
   exemplars. Voice says what the prose should *sound* like; the engineering register says what *shape*
   it should take.
5. **Audit (the procedure).** [`STYLE-AUDIT.md`](STYLE-AUDIT.md) — a run-in-order procedure that grades a
   passage against all of the above and emits concrete fixes. Run it last, over the drafted prose.

### Visualization — Mermaid-first

[`STYLE-DIAGRAMS.md`](STYLE-DIAGRAMS.md) — the standard technical-diagram types, when to reach for each,
and how to realize one. **Default to Mermaid** (it is text, it renders in Markdown, it diffs like code);
drop to hand-authored SVG only for a geometry Mermaid can't lay out, and justify the escape. Prose carries
the argument; a diagram carries the *shape* — a structure, a flow, a lifecycle, a schema. When the thing
you are explaining has a shape, draw it.

## How to use this skill

1. **Name the genre and the mode first.** What kind of doc is this — tutorial, how-to, reference,
   explanation, ADR, runbook, mechanism entry? The mode ([`STYLE-ENGINEERING.md`](STYLE-ENGINEERING.md))
   decides the shape before you write a sentence.
2. **Draft in the house voice, with varied devices.** Apply [`STYLE-VOICE.md`](STYLE-VOICE.md); reach into
   [`STYLE-RHETORIC.md`](STYLE-RHETORIC.md) for figures, and vary them so nothing recurs on a fixed beat.
3. **Name concepts from the lexicon.** Use [`STYLE-LEXICON.md`](STYLE-LEXICON.md) — one established term
   per idea, linked; don't coin a synonym for a concept that already has a name.
4. **Draw the shape where there is one.** If the content is a structure, flow, lifecycle, or schema, add a
   diagram per [`STYLE-DIAGRAMS.md`](STYLE-DIAGRAMS.md) — Mermaid unless the geometry forces SVG.
5. **Audit before you ship.** Run [`STYLE-AUDIT.md`](STYLE-AUDIT.md) over the draft and apply its fixes.

## Bootstrap the lexicon from a codebase walk — then keep it living

The lexicon ships a **portable base** (terms with an established name in the wider discipline). Your repo
also has a **house dialect** — its own coinages and the terms it reuses. You do not invent that table; you
*mine* it, then keep it current.

1. **Bootstrap by walking the codebase.** Follow the bootstrap recipe in
   [`STYLE-LEXICON.md`](STYLE-LEXICON.md) (§"Bootstrap recipe — walk your codebase"): sample your sources
   (the house-rules doc, a handful of design docs, your typed enums / registries / schema constants),
   extract every term you use with a specific meaning more than once, classify each as **portable** (link
   the established name) or **house** (note the standard concept it renames), and draft the table.
2. **Confirm with the maintainer.** The maintainer ratifies the preferred term and the definition — a
   lexicon nobody agreed to won't be used.
3. **Keep it living.** Re-walk periodically and whenever vocabulary drifts: a new coinage, or two words for
   one idea, is the signal to add or fix a row. **self-communicate owns the lexicon** — update it when you
   coin a term or notice drift. Keep the portable base shared; keep the house dialect local (an outside
   adopter who copies your coinages inherits terms that mean nothing in their repo).

## Notes

- **Partner to self-governance and self-operations — the prose those two produce is this skill's work.**
  The controls, mechanism entries, and design docs [`self-governance`](../self-governance/SKILL.md) writes
  are prose; write them in the engineering register. The runbooks, handoffs, and banking docs
  [`self-operations`](../self-operations/SKILL.md) writes are prose too. The lexicon's **Governance &
  controls** and **Operations** clusters are the shared vocabulary all three skills reason in — keep those
  terms consistent across the trio.
- **This skill is soft.** It aims the writer at a craft; it does not itself block. The one hard control it
  suggests is running the audit procedure as a gate over prose before it ships.
- **Grade the prose, not the writer.** The audit procedure grades a passage and emits fixes. It is a
  checklist an agent runs, not a verdict on the author.
