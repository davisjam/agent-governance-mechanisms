# Body-to-catalogue linking policy

**Purpose.** The book is the *argument*; the appendix (the rendered catalogue entries) is the
*reference*. When the body names or exemplifies a governance mechanism that has a catalogue
entry, the reader should be able to jump from "here is an example" to "here is the full pattern."
Today the body carries **zero** such links, so this is a first, deliberate pass — not a retrofit.

The bar is **tasteful**: links are affordances, not footnote clutter. A paragraph must not become
a sea of blue. Fewer, higher-value links beat exhaustive cross-referencing.

## When to link

1. **Link a mechanism, not a mention.** Add a link where the body (a) **names** a specific
   catalogue mechanism, or (b) gives a concrete **example that instantiates** one. A passing,
   generic reference is not a link site.
2. **First substantive mention per chapter.** Link the first place *in a chapter* where the
   mechanism is discussed enough that the full writeup would help. Do **not** re-link the same
   mechanism later in the same chapter. A different chapter may link it again (first-per-chapter,
   not once-per-book).
3. **Precision — the example must be an instance of *that* entry.** Only link when the body's
   example is genuinely a case of the mechanism you are linking, never a sibling. This mirrors the
   catalogue's own rule that an entry's examples must instantiate *it*. If no single entry clearly
   fits, do **not** force a link.
4. **Prefer the high-value sites.** Strong candidates: a named mechanism in prose ("the
   drift-and-parity gates," "role-typed dispatch," "the one typed model under every format"); a
   concrete DocAble example that maps to an entry (the ban-lint that routes all format mutation
   through one typed model → the canonical-typed-model entry); a "the companion catalogue" /
   "in the appendix" gesture that points at a *specific* entry or role. Weak/no candidates: a
   generic noun, a concept with no single entry, a hand-wave at the catalogue as a whole.
5. **Density cap.** Link the meaningful mechanisms a chapter actually exemplifies — roughly a
   handful per chapter at most, not every glancing mention. When in doubt, link fewer.

## What to link to

Each mechanism's **appendix page**, which is the same writeup as the catalogue entry, rendered into
the book. The page name is derived from the entry:

- `agent/<family>/<slug>.md`         → `appendix-a-<slug>.html`
- `models-bridge/<family>/<slug>.md` → `appendix-b-<slug>.html`
- `product/<family>/<slug>.md`       → `appendix-c-<slug>.html`

(Role → letter: agent → **a**, models-bridge → **b**, product → **c**; the slug is the entry's
filename stem.) The full target list is `ls book/appendix-[a-c]-*.html`; the mechanism → role/slug
map is `INDEX.md`. **Every link must resolve to a real appendix page** — the intra-book-link lint
fails the build on a dangling target, so verify each one exists before writing it.

## Link form — a margin sidenote, never an inline wrap

The body prose must read **identically with the links removed**. So a catalogue link is NOT an
inline-wrapped phrase — it is a **margin sidenote** placed just after the paragraph that names or
exemplifies the mechanism. In the book's Tufte-style renderer, a plain blockquote floats into the
right gutter as a light sidenote (and collapses inline on a narrow screen):

```
…and the automated pipeline emits ops into that same closed edit language.

> Learn more about this governance mechanism: [remediation verbs](appendix-c-remediation-verbs.html).
```

- The **body sentence keeps the plain phrase** — nothing is wrapped in a link, so the prose is
  unchanged.
- The **sidenote** leads with a consistent "Learn more about this governance mechanism:" and links
  the mechanism's name to its appendix page.
- Place the sidenote **immediately after the paragraph** with the mention, so it floats beside the
  relevant text.
- The density and first-per-chapter rules above still hold — one sidenote per mechanism per chapter,
  a handful per chapter at most.

## Anti-patterns

- Linking every occurrence of a mechanism (link spam).
- Linking a generic word or a concept that has no single entry.
- Linking to a *sibling* entry because it is "close enough."
- Forcing a link where no entry cleanly fits.
- Turning a paragraph into a link farm — if three links land in one sentence, keep the best.

## Scope

Body → appendix only. Appendix → body backlinks are out of scope for this policy. Chapter numbers
and appendix slugs are filesystem-derived; never hand-type a chapter number, and always take the
appendix slug from the real page, not from memory.
