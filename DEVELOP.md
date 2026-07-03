# Developing the catalogue

How to extend the catalogue, work with the packaged skill, and run/write the tests.
`catalog.py` is the one tool; it is **stdlib-only** so a fresh clone runs with nothing installed.

## Quick reference

| Command | What it does |
|---|---|
| `python3 catalog.py validate` | schema + INDEX + `.md`-link + summary checks (exit 1 on any violation) |
| `python3 catalog.py build` | render every `.md` → `.html`, regenerate the landing census, **and** the skill bundle |
| `python3 catalog.py test [--strict]` | build, then run the full test suite (see the **Tests** section) |
| `python3 catalog.py deploy local` | validate → build → test → serve at `http://127.0.0.1:8137/` |
| `python3 catalog.py deploy github` | validate → build → test → commit + push (CI deploys Pages) |
| `./setup.sh` | install the OPTIONAL Node dep (`@axe-core/cli`) for the accessibility test tier |

## Adding or extending a mechanism

1. **Create the entry** at `<role>/<family>/<control>.md` (`role` ∈ `agent`, `models-bridge`, `product`).
   Follow the template in an existing sibling: a `# Title`, an `**Intent** —` line, the 4-row metadata
   card (`Summary · Target · Form · Enforcement`), then the sections `Motivation` … `Related controls`.
2. **Add its `INDEX.md` row** in the same change — `Form` and `Enf.` MUST match the entry's metadata card
   (the validator enforces this).
3. **Cite artifacts by their glossary slug** (the double-bracket citation syntax; see `ABSTRACTIONS.md`),
   not by raw filename — add new slugs to the glossary. This keeps every entry understandable to a reader
   who has only this repo.
4. **Run `python3 catalog.py validate`** (must be 0 issues), then `build`.

The self-containment rule (see [`CLAUDE.md`](CLAUDE.md)): every entry must stand on its own to an agent
that has only this repo — describe artifacts by role and shape, never cite an external rule number or a
path into a tree this repo doesn't ship.

## The packaged skill

The `plugin/self-governance/` skill is **generated** from the catalogue by `bundle_skill.py`, which
`catalog.py build` runs automatically — so it can't drift from the entries. It mirrors the `agent` +
`models-bridge` roles into `reference/` (the `product` role is intentionally excluded) and lifts Part A of
`downloads/CLAUDE-starter.md` into `principles.md`. **Never hand-edit** `principles.md` or anything under
`reference/`; edit the catalogue sources and rebuild. The hand-authored parts are `SKILL.md` and the
manifests (`plugin.json`, `.claude-plugin/marketplace.json`).

## Tests

`catalog_tests.py` is a **tiered** suite (run it via `python3 catalog.py test`, which builds first):

**Tier 1 — pure stdlib, always runs, hard-fails.** No external tools; safe on a fresh clone.
- *markdown: schema + `.md`-link existence* — delegates to `catalog.py validate`.
- *markdown: `#anchor` resolution* — a `file.md#x` link's `x` must match a heading in the target file.
- *html: link + anchor resolution* — every local `href`/`src` in the built HTML resolves; `#anchor`s exist
  where the target page uses ids.
- *skill: structure + manifests* — `SKILL.md` frontmatter has a `description`; `plugin.json` /
  `marketplace.json` are valid with required fields; the bundle is present and non-trivial.
- *skill: bundle freshness* — regenerates the bundle and asserts it matches what's committed (no drift).

**Tier 2 — external tools; SKIP if absent, or FAIL under `--strict`.**
- *html: axe-core accessibility* — serves the site and runs `@axe-core/cli` over representative pages.
  Needs Node (`./setup.sh`) + a Chrome/Chromium browser.
- *skill: `claude plugin validate`* — validates the plugin + marketplace manifests. Needs the `claude` CLI.

**"Resolve"** = the relative target file exists; a `#anchor` matches a heading-slug (markdown) or an
`id`/`name` (html) in the target. `http(s)`/`mailto`/`data:` links are out of scope (no network in tests).

**Adding a check:** write a function returning `(status, issues)` where `status` ∈ `PASS`/`FAIL`/`SKIP`
and `issues` is a list of strings; add it to the `CHECKS` table with its tier. Tier-2 checks take a
`strict` bool and should return `SKIP` (not `FAIL`) when their tool is missing unless `strict`.

**Where they run:** `catalog.py deploy` runs the suite before serving/publishing (axe runs here if
installed), and the Pages CI runs it on every push. Both are **blocking** (the suite is green): a failure
aborts the deploy / fails CI. Tier-2 checks (axe, `claude plugin validate`) auto-**skip** when their tool
is absent — so a browser-less CI enforces the Tier-1 stdlib checks and skips axe, while a local deploy
(with Node + a browser) enforces axe too.

## Dependencies

| Layer | Needs | Notes |
|---|---|---|
| Catalogue tool + Tier-1 tests | **Python 3 stdlib only** | zero install; `git clone` and go |
| Tier-2 axe (a11y) | Node.js + `@axe-core/cli` + a Chrome/Chromium browser | `./setup.sh` installs the npm dep; `node_modules/` is gitignored |
| Tier-2 manifest validation | the `claude` CLI | ships with Claude Code |

The core tool stays dependency-free on purpose; the Node dep exists **only** for the optional a11y tier
and never blocks a fresh clone.

## Deploy & serving

The site is GitHub Pages, built in CI from the `.md` on every push (the "executable, can't-drift" build).
The tracked `hooks/pre-commit` keeps the committed HTML + skill bundle in sync locally
(`python3 catalog.py install-hooks` to enable). Never hand-edit `.html` — it's regenerated and overwritten.
