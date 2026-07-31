# Bundled print fonts

The web book loads Fraunces / Source Sans 3 / IBM Plex Mono from Google Fonts (see
`google_fonts_link()` in `book-models/design_tokens.py`). The print PDF is built by `typst compile`,
which has no network access and no system-font access to those faces — neither this machine nor the
CI runner has them installed. Without a bundle, Typst silently substitutes its own default serif and
the PDF diverges visually from the web book.

These are the **static TTFs** `typst compile --font-path book/fonts` reads instead, matching exactly
the weights/styles the Typst emitter (`book/book_typst.py`) actually requests. All three are
OFL-licensed (SIL Open Font License 1.1), so bundling the binaries in-repo is license-clean; each
family's `LICENSE`/`OFL.txt` travels with it below.

| Family | Files | Weights/styles used | Source |
|---|---|---|---|
| Fraunces | `Fraunces/Fraunces9pt-Bold.ttf`, `Fraunces/Fraunces9pt-BoldItalic.ttf` | Headings render at weight "bold" always (`#show heading: set text(weight: "bold")`); a heading's kicker lead adds italic on top of that inherited bold. No non-bold Fraunces use exists in the Typst path, so only these two ship. | [github.com/undercasetype/Fraunces](https://github.com/undercasetype/Fraunces), `fonts/ttf/` — OFL 1.1 |
| Source Sans 3 | `SourceSans3/SourceSans3-Regular.ttf`, `SourceSans3/SourceSans3-Bold.ttf`, `SourceSans3/SourceSans3-It.ttf`, `SourceSans3/SourceSans3-BoldIt.ttf` | Document body default; `**bold**` → Bold, `*italic*` → Italic, a bold+italic run → BoldIt, table header row + cover/part-divider titles → Bold. | [github.com/adobe-fonts/source-sans](https://github.com/adobe-fonts/source-sans), `TTF/` (release branch) — OFL 1.1 |
| IBM Plex Mono | `IBMPlexMono/IBMPlexMono-Regular.ttf` | Inline code / code blocks (`raw`). | [github.com/IBM/plex](https://github.com/IBM/plex), `packages/plex-mono/fonts/complete/ttf/` — OFL 1.1 |

## Family-name reconciliation (Fraunces)

Typst matches fonts by the name baked into each file's `name` table, not by filename. The Fraunces
project ships its static instances per **optical size** (`Fraunces9pt-*`, `Fraunces72pt-*`,
`Fraunces144pt-*`, …), and each instance's internal family name is `"Fraunces <size>pt"` — e.g. the
files here report family `"Fraunces 9pt"`, not `"Fraunces"`. (Verified via `fontTools`: `TTFont(...)
['name']` nameID 1/16 → `Fraunces 9pt`.) Requesting literal `"Fraunces"` from Typst would silently miss
these files and fall back to the default serif — the exact bug this bundle fixes.

Rather than hand-editing the vendor binary's name table, `book-models/design-tokens.json`'s
`type.display.typst-stack` was changed from `["Fraunces", "Georgia", "New Computer Modern"]` to
`["Fraunces 9pt", "Georgia", "New Computer Modern"]` — the **Typst-only** projection of the family name.
The CSS projection (`css-stack`, used by the web surfaces via the Google Fonts link) is untouched and
still says `"Fraunces"`, since that's the literal family name the Google Fonts API serves. The 9pt
optical size was chosen (over 72pt/144pt) because the Typst preamble only ever sets Fraunces at heading
sizes of 1.2–1.5× an 11pt body (≈13–16.5pt) — well inside Fraunces's 9pt optical-size design range, not
the large-display range 72pt/144pt are drawn for.

Source Sans 3 and IBM Plex Mono ship a single un-suffixed static family per style already (family name
`"Source Sans 3"` / `"IBM Plex Mono"` exactly, confirmed the same way), so no reconciliation was needed
for those two.
