# Print-Appendix Curation — design (260803, RE-MATERIALIZED post-crash from orchestrator context)

> This file was reconstructed after a disk-full crash purged the scratchpad. Content is faithful to the
> original a66b4e9d design (read verbatim into orchestrator context before the crash). The load-bearing
> facts (manifest shape, build changes, 29-flagship list, execution order) are preserved.

Target: project a curated **29 flagship patterns + 7 compressed stacks** into the *print* appendix
(~28–36K words); the full 83-entry catalogue stays complete + untouched on the **web** (SSOT).

**The load-bearing find:** the repo already contains the curation signal — `book-models/catalogue-classification.json`
`dispositions`: a MECE partition of all 83 → **24 `keep-as-L2` canonical** (print flagships) + **55
`demote-to-L3-under <parent>`** (web-only, each names its canonical parent) + **2 `merge-into`** + **1
`lift-to-L1`** (semantic-level-enforcement → intro principle) + **1 `move-to-book-case`**
(standards-rule-engine → Part-5 case). Plus `gee_capabilities` groups the 24 under 9 capabilities.
So the print set is DERIVED from an existing model, not invented. Genre-check (A.9) satisfied.

## 1. Projection mechanism (build_book_html.py + thin manifest)

Web catalogue (`catalog.py`) is NOT touched. Only the book/print projection changes.

### 1b. Declared manifest — `book-models/print-appendix-manifest.json` (deviations only):
```json
{
  "_provenance": "Declared print-appendix projection scope. Base flagship set is DERIVED at build time from catalogue-classification.json (disposition == keep-as-L2). This file declares ONLY the deviations.",
  "print_promotions": ["dynamic-context-injection","resource-pressure-gating","coverage-model-mapping","formal-invariant-verification","synchronization-model"],
  "intro_l1_principles": ["semantic-level-enforcement"],
  "appendix_exclude": ["standards-rule-engine"],
  "appendix_e": "pointer",
  "stack_compression": {"target_words":1250,"sections":["capability","failure-classes","composition-diagram","constituent-flagships","docable-example","tradeoffs-adoption-order","web-links"]}
}
```
`flagship_slugs = {keep-as-L2 slugs} ∪ print_promotions − appendix_exclude` = **24 + 5 = 29**.
NOTE: also web-only `claude-md-rule-index` (a keep-as-L2 the editorial assessment sends web-only; add to `appendix_exclude` OR represent inside intro capability map) — this is a §2c dial; default keeps print at 29 without it.

### 1c. Exact build changes in `book/build_book_html.py`:
1. **New loaders** (near `_FILLS_DIR` ~L1908): `_load_classification()` → `{slug: disposition_head}` + `{canonical: [child_slug,…]}` inversion (fail-loud if missing, like `_resolve_stack_members`); `_load_print_manifest()` (validate every listed slug is a real entry, fail-loud on typo); `_flagship_slugs()` → the 29.
2. **`_appendix_entries()` (L2017) UNCHANGED** — still reads ALL 83 (needed for web-index + stack member resolution). Filter at emission, not read.
3. **`build_appendix_chapters()` (L2599) — core change:** after `ordered = sorted(...)`, `flag = _flagship_slugs()`; `flagship = [r for r in ordered if r["slug"] in flag]`; per-letter running number (`appendix_num` L2624-2630) assigned over flagship-only (locators A-1…A-12, B-1…B-11, C-1…C-6, gap-free); emit one page per flagship (the `for rec in ordered` loop at L2676 iterates `flagship`); `page_by_slug` (L2700) still built from ALL ordered (every entry keeps `catalogue_html`; flagship also carry `page_slug`); opening page `_appendix_contents_md(...)` fed ALL 83 → becomes the complete web-index (flagship→in-book link, non-flagship→web catalogue link).
4. **`_resolve_stack_members()` (L2330) — link branch:** flagship member → in-book link `appendix-x-slug.html`; non-flagship member → web link `[Name (online)](../<rel>.html)`. Delete the `SystemExit` ONLY for not-a-flagship-but-valid-entry; keep it for genuinely-unknown slug. (Stacks still name ALL members.)
5. **`_appendix_anchor_map()` (L2752) / `_emit_rewired_figure()`:** flagship slug → in-book; non-flagship → web. Clickable mechanism map sends flagship chips into print, rest to web.
6. **`_appendix_counts()` (L2495):** `mechanism_count` keeps reading census total (83 — a catalogue fact); ADD derived `flagship_count`(29) + `web_only_count` for intro "in print / online" framing. `stack_count` stays 7.
7. **Appendix E** — see §5.

## 2. The 29 flagship selection (24 keep-as-L2 + 5 promotions). Balance: Agent 12 / Models-bridge 11 / Product 6. All 7 stacks ≥2 anchors.
**Agent (12):** self-governance, brief-linting, staged-deploy-gates, pre-commit-hook(as sub-section of Staged Admission, not standalone), lifecycle-hooks, dynamic-context-injection[P], typed-event-bus, agent-registry, test-serializer, resource-pressure-gating[P], epic-definition-of-done, operational-playbooks.
**Models-bridge (11):** executable-source-of-truth, read-the-model(meta-model-consumption), composed-state-machine-model, drift-parity-gates, synchronization-model[P], symbol-anchored-traceability, model-derived-assurance-coverage, coverage-model-mapping[P], formal-invariant-verification[P], computed-control-blast-radius, governance-graph.
**Product (6):** one-door-enforced(PdfModel+sole-seams), closed-action-vocabulary, machine-enforced-semantic-policy, preservation-invariant(ContentValidator), caused-by-provenance(mutator-stamps), generative-validation(fuzz+property).
**Not pages but represented:** semantic-level-enforcement → L1 intro principle; standards-rule-engine → Part-5 case.
**52 web-only** grouped by disposition reason (18 Executable-Source-of-Truth faces, admission-rungs, mediation-cardinality-variants, provenance-arms, one-door-instances, closed-vocab-instances, drift-instances, lifecycle-variants, gov-doc-plumbing, property-tests-merged).

### 2c. THE ONE AUTHOR DIAL (M-in-MAGE): default keeps 11 models-bridge (aggressive one-canonical reduction, 18 model faces online); editorial reviewer wanted ~18 in print ("the M in MAGE"). +2 dial = promote component-zone-model + agent-first-mbse-harness (+service-flow) → wider modeling footprint, ~31, touches 36K ceiling (needs ~1.5K trimmed from stacks). DEFAULT = 29. Surfaced to user; adjustable via manifest one-liner.

## 3. Stack compression (7 → ~2pp each, ~8.75K total)
Currently AUTHORED not projected: `build_stack_chapters()` (L2348) reads `book/appendix-stacks/<stem>.md` verbatim (~26pp today). `flagship_stack_declared.json` already has `goal`,`capabilities`,`overview_figure`, per-`parts`{role,failure,mechanism,seam,durability}.
**Wave A (interim, recommended first):** rewrite the 7 `appendix-stacks/*.md` to the 7-section template (capability / failure-classes / composition-diagram=existing overview_figure SVG / constituent-flagships[flagship→in-book, else→web(online)] / one-DocAble-example / tradeoffs+adoption-order / web-links), ~1,250 words each.
**Wave B (target SSOT, optional later):** `_render_stack_page(stack_record)` projects from the model; needs `docable_example` + `adoption_order` added to flagship_stack_declared.json.

## 4. Web-index (all 83) — source from opening page `_appendix_contents_md()` (L2565): feed all 83, flagship→in-book(A-N locator), non-flagship→web(online marker), optional "· under <Canonical>" tag from disposition. ~1,600 words / 2-4pp. Header states the split + URL.

## 5. Appendix E → pointer: `build_skill_recipe_chapters()` (L2422) already emits front-door + full recipe page. Honor `manifest.appendix_e=="pointer"`: emit ONLY front-door + a one-paragraph "full recipe online at <URL>"; skip the-recipe content page in print/PDF. Web keeps full. ~600 words.

## 6. Word budget: 29 flagship @~740 (compressed GoF) = 21,460 + 7 stacks @~1,250 = 8,750 + intro ~2,500 + web-index ~1,600 + AppE ~600 = **~34,910** (inside 28-36K). Down from ~76K today, zero content lost.

## 7. EXECUTION ORDER (dependency-ordered writer waves):
1. **[BUILD]** projection mechanism (build_book_html.py §1c 1-7) + manifest §1b. No prose. Verify: build emits 29 pages, A/B/C gap-free, every stack token resolves (flagship→in-book else→web), no orphan/broken-link gate fail. BLOCKS 2-6.
2. **[MANIFEST]** author print-appendix-manifest.json (can land with task 1).
3. **[WRITE]** compress 7 stack pages (§3 Wave A).
4. **[WRITE]** compress 29 flagship pages to ~740-word GoF + "represents online:" line. Split by role (12/11/6) if needed.
5. **[WRITE]** appendix intro (frame + semantic-level-enforcement L1 principle + 9-capability map from gee_capabilities + interlock + web-index header).
6. **[WRITE]** Appendix E pointer paragraph.
7. **[GATE]** build + content-integrity gate; confirm word count ∈28-36K, every omitted pattern has live web page, every book cross-ref to a demoted pattern → web, no dup prose body/appendix.
**Optional hardening lint:** assert flagship_slugs ⊆ catalogue entries AND every keep-as-L2-but-web-only override is manifest-listed (print/web split can't drift from classification.json).
