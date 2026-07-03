# CLAUDE.md — agent-governance-mechanisms

This repo is a **pattern catalogue**: 53 governance controls that keep a fleet of autonomous coding
agents productive while bounding their failures, each written as a Gang-of-Four-style design pattern.
It is published as a static GitHub Pages site and embedded in a parent repo as a git submodule.

`catalog.py` is the one tool — **stdlib-only, no dependencies** (so `python3 catalog.py …` runs on a
fresh checkout with nothing installed). Do not add pip dependencies; keep it clone-and-run.

## Core principle: this repo must be interpretable by an independent Claude

**Every mechanism description must stand on its own to an agent that has no access to the parent
repo** — not its source, its docs, its tools, or its `CLAUDE.md` rule numbers. This is the
governing rule for all content here:

- **Describe artifacts by role and shape, not by unshipped filename.** "A host-level flock wrapper that
  serializes the test runner," not `` `test-serializer.py` ``. "A stable lint that reads the model at
  build time," not `` `lint-service-flow-model.py` ``.
- **Explain a governing rule's *content*; never cite a bare rule number.** "A project rule that a new
  event-bus topic must ship an observability entry," not "rule #46". A number like `#46` is meaningless
  outside the parent repo.
- **No dangling paths** into trees this repo does not ship (`services/…`, `deploy/…`, `docs/…`,
  `talks-and-notes/…`). Intra-catalogue links (`../<role>/<family>/<control>.md`) are fine — they ship.
- **Prefer the conceptual statement over the concrete DocAble artifact** that happens to implement
  it. `Known uses` may name a real artifact *once* for grounding, but the mechanism must be understandable
  without it. The `product/` role is the catalogue's flagged project-specific exception; keep it
  self-contained too.

The test: *could a Claude that has only this repo read an entry and understand the mechanism well enough
to adapt it?* If it depends on a file, path, or rule number it can't see, the entry fails this rule.

## Writing style

An entry is read by a busy engineer and a coding agent. Write for both: plain, direct, no padding. Aim
for Hemingway — short sentences, strong verbs, few qualifiers.

- **Active voice; name the actor.** "The reclaim trusts the record," not "the record's correctness is
  what the reclaim trusts." Prefer "X does Y" to "Y is what X does."
- **Short, declarative sentences — one idea each.** Break a clause-stacked sentence into two.
- **Say it once.** State the point and move on. No "One line:", no "the heart of it", no closing
  sentence that restates the paragraph. If you summarized your own paragraph, cut one of the two.
- **Concrete words, not reflex labels.** Reach for the precise term — *central*, *authoritative*, *the
  weak point*, *essential*. Use "load-bearing" very sparingly, if at all.
- **Cut qualifiers.** Drop *very, quite, essentially, arguably, precisely*. Bold one or two phrases per
  section, not by habit.
- **Describe, don't sell.** Give the mechanism and the failure it kills. Don't tell the reader every
  project should adopt it — that's their call.
- **Instance entries lead with the portable pattern.** When an entry instantiates a general pattern,
  open its Intent with the transferable claim, then name the project instance in parentheses —
  *"…route all mutation of a format through one typed model with a ban-lint on the raw library (our
  instance: `PdfModel`)."* A reader who doesn't share the domain still gets the idea.

## The content model

- **Entries** live at `<role>/<family>/<control>.md` — roles are `agent/`, `models-bridge/`, `product/`.
  Every entry follows the template documented in [`README.md`](README.md): a title, an `**Intent** —`
  line, a 4-row metadata card (`Summary · Target · Form · Enforcement`), then the sections
  (`Motivation` … `Related controls`).
- **[`INDEX.md`](INDEX.md)** is the census — one row per entry, grouped by family. The `Form`, `Novelty`,
  and `Enf.` columns MUST match the entry's metadata card (the validator enforces this).
- Cross-cuts: 9 **forms**, **soft/hard** enforcement, 5 **relationships** — all defined in `README.md`.
- **One entry, or two, for a construction + its enforcement?** By enforcement scope. A **dedicated**
  (one-to-one) enforcement — a ban-lint guarding *this one* seam — is **bundled into the construction
  entry** (the typed model + its ban-lint is one control). A **cross-cutting** (one-to-many) enforcement
  that governs *many* constructions earns **its own entry** (`drift-parity-gates` governs every model;
  `f10-wiring-lint` governs every mutator verb). Don't split a dedicated pair; don't bundle a cross-cutting
  one.

**When you add or edit a control:** update both the entry and its `INDEX.md` row in the same change,
then `python3 catalog.py validate` (must be 0 issues). The schema, INDEX-consistency, link-integrity,
and hover-summary checks all live there.

## Build & deploy

The site is generated from the markdown — **never hand-edit the `.html`** (it carries a
`GENERATED by catalog.py build` banner and is overwritten on every build).

| Command | What it does |
|---|---|
| `python3 catalog.py validate` | schema + INDEX + link + summary checks; exit 1 on any violation |
| `python3 catalog.py build` | render every `.md` → sibling `.html` + regenerate `index.html` (census) + `catalogue-views.html` |
| `python3 catalog.py deploy local` | validate → build → serve at `http://127.0.0.1:8137/` (`--port` to change; **not** 8080) |
| `python3 catalog.py deploy github` | validate → build → commit changes → `git push origin main` (GitHub Actions then deploys Pages) |
| `python3 catalog.py install-hooks` | one-time: `core.hooksPath=hooks` so `pre-commit` auto-runs validate+build+stage |

**Two deploy modes, one command:**
- **`deploy local`** — preview in a browser. Blocks while serving; Ctrl-C to stop.
- **`deploy github`** — publish. Commits any pending changes and pushes; the
  [`.github/workflows/pages.yml`](.github/workflows/pages.yml) workflow rebuilds and deploys to Pages.
  (Requires Settings → Pages → Source = "GitHub Actions".)

Both modes **always validate + build first**, so a broken schema can never be served or published.

## Serving model

GitHub Pages serves the committed HTML (deploy path = the Actions workflow, which re-runs
`catalog.py build` in CI — the "executable, can't-drift" build). The tracked `hooks/pre-commit` keeps
the committed HTML in sync locally; CI is the source of truth on push. `.nojekyll` disables Jekyll so
files are served as-is.

## Submodule relationship

This repo is embedded in a parent repo as a submodule. Edits happen **here** (commit + push to this
repo's `origin/main`); the parent then bumps its gitlink pointer separately. This repo has no knowledge
of the parent — treat it as standalone.

## Standalone posture

The catalogue is distilled from a real product (DocAble, live at scholaccess.com) — referencing it and the paper is fine. The
real constraint is that every entry stays **standalone and interpretable**: no absolute paths, and no
dangling internal file or rule-number references an outside reader can't resolve (the abstractions
glossary exists for exactly this — see the interpretability principle above). `scholaccess.com` and the
paper are the deliberate outward links.
