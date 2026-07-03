<!-- Internal continuity doc — NOT served (see NOSERVE in catalog.py). -->

# HANDOFF — catalogue-agent

Continuity doc for the **catalogue-agent**: the agent that owns the catalogue's **content, the `catalog.py`
tooling, the validate gates, and the hand-authored figure**. Assume the reader has only this repo.

> **Two agents work this repo — don't confuse them.**
> - **catalogue-agent (this doc)** — catalogue entries, `ABSTRACTIONS.md`, the `downloads/` starters,
>   `catalog.py` (schema + content gates), `README`/`quick-start`/`CLAUDE.md` prose, and the *content* of
>   the hand-authored figures.
> - **skill-agent** — the installable `self-governance` Claude skill (`bundle_skill.py`, `plugin/`,
>   `.claude-plugin/`), the **a11y / axe** compliance of the served pages, and the **`tests/` package**.
>
> **Shared surfaces (coordinate):** `catalogue-figure.html` (I edit content; skill-agent edits a11y),
> `README.md`, `catalog.py`, `hooks/pre-commit`. When touching a shared file, prefer small commits and
> `git status` first — both agents have been landing here interleaved. The a11y agent made the figures
> **axe-green**; when you edit a figure, imitate the existing patterns (link text + `title`; decorative
> symbols as plain spans; no new aria) so you don't regress axe.

Companion docs: [`HANDOFF.md`](HANDOFF.md) (the general catalogue handoff), [`CLAUDE.md`](CLAUDE.md)
(the governing rules), [`abstractions-playbook.md`](abstractions-playbook.md) (how to use the glossary),
[`TODO.md`](TODO.md) (deferred work).

---

## 1. Current state (verify, don't trust)

- **53 entries · 3 roles** (agent 22 · models-bridge 11 · product 20 · 11 families). **18 abstractions**
  in `ABSTRACTIONS.md`.
- Verify: `python3 catalog.py validate` → must print `… — 0 issue(s)`; `python3 catalog.py build` →
  `built 62 entry/index pages …`.
- **~42 commits ahead of `origin/main` — NOTHING IS PUBLISHED.** The live GitHub-Pages site + the pinned
  parent submodule are stale. Publish with `python3 catalog.py deploy github` (validate → build → commit →
  push → Pages CI). The parent-pointer bump is a separate step (see `HANDOFF.md` §6).
- Local preview server may be running at `http://127.0.0.1:8137/` (`catalog.py deploy local`).

## 2. What the catalogue-agent built this run (the systems)

### 2a. The abstractions glossary — the interpretability de-referencer
The catalogue must be **standalone**: readable by an agent with only this repo, with no dangling
references into the private source project. Entries used to cite unshipped filenames (`components.py`,
`test-serializer.py`, …) and bare project-rule numbers (`#46`). Both are now removed.

- **`ABSTRACTIONS.md`** — a single-page glossary. Each entry: `## Headword` (the abstract role) +
  `<!-- slug: … -->` + a definition + a `**Grounds** — …` line naming the real artifact **once** + a
  `**See** — [control](…)` link. Entries cite it as **`[[slug]]`** or `[[slug|display text]]` (renders a
  tooltip'd link to `ABSTRACTIONS.html#slug`).
- **Decision rule** (full version in `abstractions-playbook.md`): a filename → a glossary entry only if
  its role isn't obvious from the name **and** it recurs; otherwise de-`.py` it to self-describing prose.
  Rule numbers → always inline their *content*, never a glossary term. A control's *own* page uses prose
  (no self-citation).
- Enforced by `check_abstractions` (see §3): every `[[slug]]` resolves; **no** entry may carry a
  backticked *unshipped* filename (basename absent from this repo) or a bare `#NN` rule cite. This is
  **global** now — a new entry that reintroduces either fails validate.

### 2b. The `downloads/` starters (adopt-and-adapt artifacts)
Portable, distilled-from-the-real-system files an adopter drops into their own repo:
`CLAUDE-starter.md` (Part A method verbatim + Part B stripped to its *shape* + the "what earns a spot"
test), `EPIC-TEMPLATE-starter.md`, `design-doc-template-starter.md`, `agent-brief-starter.md`,
`op-playbook-starter.md`, and a **runnable** `governance-lint-example.py` (the real
regex-against-structured-formats lint, self-contained). Each is linked from the mechanism it instantiates
("Adopt it →") and from quick-start Path A. **These are NOT catalogue mechanisms** — no new entry; the
count stayed 53.

### 2c. The hand-authored figure (`catalogue-figure.html`) — "the governance map"
Four views (census / staircase / soft↔hard lattice / model-bridge). **Build never regenerates it** — edit
the HTML directly. Invariants now enforced by `check_figure` (§3):
- **Every control is clickable** somewhere (coverage); **every `chip`/`lat-node` carries a link** (no
  orphan clickable-looking nodes); **every relative `.html` link resolves**.
- **Every legend element is used** in the diagram body (counterpart/enabler/consumer/layer/bridge +
  Soft/Soft·Hard).
- View 3's "wiring by relationship" is grouped per-relationship (taller, with the definition pulled into
  each header) and its control slugs are links (informal counterparts like `cap-lint` stay text).
- Colour legend names all three roles: coral=agent, **blue=models-bridge**, green=product.

### 2d. Naming + licensing rules (IMPORTANT — enforced)
- **DocAble** = the product. **ScholAccess** / `scholaccess.com` = its website (the sanctioned outward
  link). **`ada-tool`** = the private parent repo's *internal codename* — do not surface it in prose (one
  labelled mention survives in `HANDOFF.md`).
- **Do NOT name the PDF vendor library** (licensing under review — name withheld even here). Say
  **"canonical PDF library"** / "raw-PDF-library ban-lint." Enforced by `check_banned_terms` (the
  `BANNED_TERMS` dict in `catalog.py`) — fails validate if the name appears anywhere in the sources. To
  ban more vendor names, add to that dict; when licensing resolves, remove the entry.
- **No "redacted" framing** anywhere — the catalogue is a standalone artifact, not a censored copy.

## 3. The validate gate inventory (`catalog.py` — runs at pre-commit AND predeploy)

`cmd_validate` runs these; any non-zero total blocks the pre-commit hook and `deploy`:

| Check | What it enforces |
|---|---|
| entry schema (`Entry._parse`) | title · `**Intent**` · the 4-row metadata card (Summary·Target·Form·Enforcement) · 7 `##` sections in order · relationship-tagged Related-controls |
| `check_index` | `INDEX.md` Form/Enforcement columns match each entry's card; row count = entry count |
| `check_links` | every `.md` link in the catalogue trees resolves (scoped by `catalogue_md_files` — ignores `plugin/` etc.) |
| `check_abstractions` | `[[slug]]` cites resolve; **no unshipped filename / bare `#NN` rule cite** in any entry |
| `check_figure` | figure: link-integrity · coverage (every control linked) · no-orphan-node · legend-usage |
| `check_banned_terms` | no banned vendor name (the PDF library, name withheld) in the sources |
| role/family summaries | each tiered README has a `<!-- summary: … -->`; each family has an INDEX italic one-liner |

**Design note:** `check_figure` / `check_banned_terms` scan **sources** (`.md` + the two hand-authored
figures), never generated HTML — validate runs *before* build, so scanning generated `.html` would flag
stale output. Generated HTML is fixed by the rebuild.

## 4. Conventions when you edit (so the gates stay green)

- **Adding a control:** author the entry to schema; add its `INDEX.md` row; add it to the figure
  (a linked chip) or `check_figure` coverage fails; run `validate`.
- **Referencing an internal artifact in an entry:** never a raw filename or `#NN` — use `[[slug]]`
  (add a glossary entry if warranted) or self-describing prose. `validate` enforces this.
- **Editing the figure:** every mechanism node must be a link; keep the legend elements all used; imitate
  the a11y patterns already there (the skill-agent made it axe-green — don't regress it).
- **Never name the PDF library**; never write "redacted"; keep DocAble/ScholAccess/ada-tool straight.
- **Commits:** the pre-commit hook runs `validate` + `build` (which also regenerates the skill bundle) and
  stages the HTML + `plugin/`. Agents in this repo have been using `git commit --no-verify` when landing
  many small commits while another agent is mid-edit on a shared file (avoids the hook re-staging the
  other agent's in-flight work) — but the hook is the safety net; prefer letting it run when the tree is
  yours alone.

## 5. Open items / next steps

- **PUBLISH** — ~42 commits are unpushed. When the human is ready: `catalog.py deploy github`, then bump
  the parent submodule pointer (commit-slave, per `HANDOFF.md` §6).
- **`TODO.md`** — the single-machine-contention rephrasing (distinguish the general "arbitrate contention"
  mechanism from our single-host `flock` instantiation) is still deferred.
- **`layer ▼` legend entry** — the thinnest (used once, only in View 3's wiring prose); left in place. If
  a reviewer finds it confusing against the diagram, it's a safe trim (drop from the legend + the wiring
  group; `check_figure` legend-usage will then pass without it).
- **Figure wiring links are hand-maintained** — the informal-slug tokens in prose aren't gate-covered
  (they don't map 1:1 to filenames). If the wiring keeps growing, a curated token→control map would let a
  check cover them; not worth it yet.
- **PDF library name** — when licensing resolves, remove the entry from `BANNED_TERMS` and (optionally)
  restore the specific name in `pdf-model.md`/`office-models.md`.

## 6. Locked decisions (don't re-litigate)

- Abstractions are **one page**, headword = abstract role (never the filename); rule numbers are always
  inlined, never glossary terms.
- The `downloads/` starters are **artifacts, not mechanisms** (no new entries).
- The figure is **hand-authored** — build never regenerates it; its invariants live in `check_figure`.
- `catalog.py` stays **stdlib-only** (clone-and-run). Same for `bundle_skill.py`.
- The gates live in **`catalog.py validate`** (schema/content) — the broader `tests/` package (axe,
  HTML well-formedness, skill-bundle) is the **skill-agent's**; both run at deploy/CI.
