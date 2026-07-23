# Abstractions playbook (internal — not served)

How to use `ABSTRACTIONS.md` (the glossary) when de-referencing an entry so it satisfies the governing
interpretability rule (CLAUDE.md §"Core principle: this repo must be interpretable by an independent
Claude"). This file is process guidance for whoever migrates the remaining families; it is excluded from
`catalog.py build` (see `NOSERVE` in `catalog.py`).

## What problem this solves

Entries were written citing the parent system's unshipped filenames (`components.py`, `repo-query.py`,
the `lint-*.py` fleet) and bare project-rule numbers (`#33`, `#42`). Both are meaningless to a reader who
has only this repo. `ABSTRACTIONS.md` is the single, in-repo place where each concrete artifact is named
by its **role and shape** and grounded (once) in the real filename — so an entry can *cite the
abstraction* and stay standalone.

## The decision procedure (per filename/rule you hit)

1. **Bare rule number (`#NN`, "Part B rule #NN")** → NEVER a glossary entry. Rewrite it inline to the
   rule's *content*: `#33` → "a lint that reads the meta-file is preferred over codegen, over a
   hand-rolled copy". Rule numbers are unstable and unhelpful as terms (user decision).

2. **A backticked filename** → decide glossary vs inline prose:
   - **Inline prose** when de-`.py`-ing the name already yields a self-describing noun phrase:
     `supported_filetypes.py` → "the supported-filetypes registry"; `lint-public-api-drift.py` → "the
     public-API drift lint". No glossary entry — just describe it. (Recurrence alone does not force a
     glossary entry if the prose form is short and stable.)
   - **Glossary entry** when the role is *not* obvious from the name, **and** the artifact recurs across
     entries: `components.py`, `mediators.py`, `repo-query.py`, `state_mutator_registry.py`. Add it to
     `ABSTRACTIONS.md` (if not present) and cite it `[[slug]]`.

3. **A definitional page** (the mechanism *about* that artifact, e.g. `query-surface.md` for the query
   tool) → naming the artifact once here for grounding is sanctioned. Strip the extension
   (`repo-query.py` → `repo-query`) rather than citing the abstraction that points back to this very
   page (avoid the self-referential loop).

4. **Type / field / constant / dialect tokens defined in context** (`SyncLock`, `focus_dirs`,
   `kind: Component | API | System`, `fcntl.flock`) → leave as-is. They describe *shape* and are
   self-contained; they are not dangling references.

5. **External tools** (`dotnet test`, `flock`, `veraPDF`) → leave as-is. They're public, not unshipped
   parent artifacts.

## Authoring a glossary entry (`ABSTRACTIONS.md`)

Strict per-entry shape the parser reads (`parse_abstractions()` in `catalog.py`):

```
## <Headword — the abstract role, Title Case>
<!-- slug: kebab-case-slug -->
<one definition paragraph: role + shape, tooltip-friendly. This becomes the hover text.>

**Grounds** — <the real artifact, named ONCE> (`filename.py`). **See** — [mechanism](role/family/mechanism.md).
```

- **Headword = the abstract role**, never the filename ("Component registry", not `components.py`). The
  page is keyed on concepts so it stands alone.
- **slug** is the citation key; keep it stable even if the headword is reworded.
- **Grounds** is the *only* place a raw parent filename may appear in the whole served site.
- **See** points to the mechanism that governs the artifact (validated as a live link).

## Citing from an entry

- `[[slug]]` renders the headword; `[[slug|your words]]` renders custom display text. Hover shows the
  definition. Write the sentence so it **still reads if you strip the citation** — the abstraction is
  grounding, not a load-bearing click. Good: "the [[component-registry]] is a typed dataclass set". Bad:
  "[[component-registry]] does the mapping" (leans on the link to be understood).

## The gate (what `catalog.py validate` enforces — now global)

- Every `[[slug]]` across all catalogue markdown resolves to an `ABSTRACTIONS.md` entry.
- **Every** entry: no backticked *unshipped* filename (basename absent from this repo — so `catalog.py`
  is allowed, `components.py` is not) and no bare `#NN` rule citation. (This was scoped by a
  now-removed `ABBR_MIGRATED_DIRS` while the sweep was in progress; the ban is global by construction
  now that all three roles are migrated, so a *new* entry is forward-policed automatically.)

## Adding a new entry (the ongoing rule)

Author it clean from the start: run every filename / rule-number through the decision procedure above,
citing `[[slug]]` (adding a glossary entry if the artifact is non-obvious and recurs) or writing
self-describing prose. `python3 catalog.py validate` will reject an entry that reintroduces a raw
filename or a bare rule number.

Migration is **complete**: all 53 entries across `agent/`, `models-bridge/`, and `product/` are on the
glossary (18 glossary entries). The single-machine-contention rephrasing in [`TODO.md`](TODO.md) is the
one deferred follow-up.
