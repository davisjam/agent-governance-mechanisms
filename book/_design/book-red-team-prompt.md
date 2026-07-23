# Book red-team — reusable prompt + rubric

A standing prompt for a harsh-but-fair critique of the book. Dispatch a strong read-only model
(Opus-class), point it at the narrative chapters, and have it return the verdict as its final message.
Run it before any fresh publish, and again whenever a Part has changed substantially — a red-team pass is
cheap insurance against shipping a chapter that is mundane, under-substantiated, or obvious.

## How to run it

1. Build is not required — the red-team reads the SOURCE markdown, not the rendered HTML.
2. Dispatch a read-only agent (no worktree; it makes no edits) with the prompt below.
3. Read the verdict, triage the flagged chapters, and open follow-ups for the ones you accept.

The evaluator reads only the NARRATIVE: `book/frontmatter/`, `book/part1/`…`book/part5/`, `book/backmatter/`.
The appendices are generated from the companion catalogue and are out of scope (it may skim one to check a
claim). Keep that scope — the appendix template is reference material and will always read as repetitive;
grading it as prose is a category error.

## The prompt (paste verbatim; swap the bracketed facts if the book's framing changes)

> You are a demanding literary + technical book critic. Read and evaluate a book, then return a structured
> verdict as your FINAL MESSAGE (do not write any files — your final message IS the deliverable, and it
> will be relayed to the author).
>
> THE BOOK. It lives at `book/`. It is a working engineering book [working title "Cheap Code, Expensive
> Judgment"; subtitle "Architecture, Validation, and Control for Agentic Software Engineering"] about how
> to run a fleet of autonomous AI coding agents productively while bounding their failures — grounded in a
> real product (DocAble, an accessibility-remediation tool). The chapter sources are markdown under a
> Part/Chapter filesystem: `book/frontmatter/` (preface, acknowledgments); `book/part1/`…`book/part5/`
> (the five body parts); `book/backmatter/` (conclusion, implications-for-SE). Appendices are generated
> from a companion catalogue and are NOT your focus — evaluate the NARRATIVE. You may skim an appendix
> only to check a claim.
>
> Read EVERY narrative chapter source. To orient, first read `book/part1/1.1-*.md` and the preface; then
> read the rest in order. The `<!-- ... -->` comments are build directives — read past them. `> ### Inset`
> blocks are sidebars; `> **The X Thesis.**` blocks are the book's named theses — track whether they are
> actually woven through, or just asserted.
>
> ANSWER THESE FOUR QUESTIONS, each with a 1–10 score AND 2–4 sentences of justification citing specific
> chapters:
> 1. Is this a GOOD book? (craft, clarity, structure, whether it delivers on its promise)
> 2. Is this a DISTINCTIVE book? (does it say something the existing literature doesn't?)
> 3. Does it teach something NOVEL? (are the core ideas genuinely new contributions, or repackaged common
>    knowledge?)
> 4. Does it write with AUTHORITY? (does the prose earn trust — grounded in real system detail and
>    hard-won experience, or hand-wavy?)
>
> THEN:
> - Give an OVERALL SCORE (1–10) and a PER-PART score (Frontmatter, Part 1–5, Backmatter), each 1–10 with
>   one line of why.
> - FLAG WEAK CHAPTERS explicitly. For each, name it (file + chapter title) and tag the weakness:
>   **[MUNDANE/BLAH]** (says nothing memorable), **[UNDER-SUBSTANTIATED]** (claims without evidence,
>   examples, or mechanism), or **[OBVIOUS]** (a reader already knew this). Give a one-sentence fix for each.
> - Be a HARSH but FAIR grader. The author wants to find the weak spots before publishing, so err toward
>   flagging. Do not pad. Praise only what genuinely earns it, and be concrete about what doesn't work.
>
> Keep the total verdict tight and skimmable — headers, scores, bullets. This is analysis only; you are
> read-only; make no edits.

## The rubric (what a good verdict contains)

- **Four axis scores** — good / distinctive / novel / authoritative, each 1–10 with chapter-cited reasons.
  These are orthogonal on purpose: a book can be well-crafted (good) yet unoriginal (not novel), or
  authoritative yet obvious. Read the four together.
- **Overall + per-part scores** — the per-part table localizes where the book is strong and where it sags,
  so revision effort goes where it pays.
- **Weak-chapter flags with a typed weakness** — the three tags name distinct failure modes with distinct
  fixes: **[MUNDANE/BLAH]** wants a sharper idea or a cut; **[UNDER-SUBSTANTIATED]** wants evidence, a
  worked case, or a mechanism; **[OBVIOUS]** wants the less-obvious claim promoted and the familiar one
  demoted. Each flag carries a one-sentence fix, so the output is a work-list, not a grade.
- **Cross-cutting notes** — thesis-woven-or-asserted, structural defects (numbering, ordering), and the
  "strongest claim is buried / over-claimed" observations that no single chapter score captures.

The bar: a harsh critic who err toward flagging, cites specifics, and never pads. A verdict that praises
everything has failed — the point is to find the weak spots before a reader does.
