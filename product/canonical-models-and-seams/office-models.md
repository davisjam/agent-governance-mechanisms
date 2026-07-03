# Office Models ({Slides,Docs,Sheets}Model)

**Intent** — The same typed-model-plus-ban-lint pattern as [pdf-model](pdf-model.md), applied to a second
object model: all remediation of a format family routes through one typed model, with raw library access —
and raw string-matching into the serialized form — banned by lint (our instance: `{Slides,Docs,Sheets}Model`
for PPTX/DOCX/XLSX over `DocumentFormat.OpenXml`).

| | |
|---|---|
| Summary | All OOXML through typed models; raw SDK access banned. |
| Target | Product · **Canonical models & seams** |
| Form | `typed-ir` |
| Enforcement | **Hard** (deterministic) · *blocking* — the two lints fail the build on raw OpenXml / raw-XML string-match; the typed models are *construction*, the lints are the counted controls |

## Motivation — the failure it kills

Raw OpenXML SDK access, and the sneakier path of *regexing into the XML*, are the Office equivalent of
the raw-PDF-library minefield: brittle, corruption-prone, and with no single point to enforce structural
invariants. Left ad hoc, the same raw-library corruption class recurs across three separate document
formats.

## Why it's not just "PdfModel already solves this" (or "handle Office ad hoc")

Office is a *different object model* (the OpenXML SDK), so `PdfModel` cannot cover it — but the **same
defect class** (raw-library corruption) applies. The Office Models are the parallel sole-seam, and
routing all three formats through the same typed-model + ban-lint pattern is **defect-class
consolidation**: a fix to the pattern benefits all four formats at once, which is sufficient
justification on its own — capability parity, not new capability. The distinction is *the same
construction + ban-lint pattern applied per object-model* versus *per-format ad hoc handling that lets
the corruption class recur three more times*. The `no-raw-xml-string-match` lint closes the sneaky
regex-into-XML escape that a plain "no raw SDK" rule would miss.

## Mechanism

Route through `SlidesModel` / `DocsModel` / `SheetsModel` and the shared `OpenXmlCommon`; the
Checking layer routes through `RuleWalkers/`. `openxml-direct-access` bans raw
`DocumentFormat.OpenXml.*`; `no-raw-xml-string-match` bans regexing the serialized XML.

## Prerequisites

- **A typed model per Office format** plus a shared common layer for cross-format primitives.
- **Two ban-lints** — one on the raw SDK, one on raw-XML string-matching (the sneaky path).
- **Call-site migration** across all three formats.

## Consequences & costs

- **Three models plus a shared layer to maintain** — more surface than the single PdfModel.
- **Coverage gaps per format** force a `noqa` or a model extension, same as PdfModel.
- **The string-match ban can false-positive** on a legitimate string operation over document text,
  needing an escape.

## Known uses

- `SlidesModel` / `DocsModel` / `SheetsModel` + `OpenXmlCommon`; `RuleWalkers/` for the checking path.
- `openxml-direct-access` + `no-raw-xml-string-match` ban-lints.

## Related controls

- *See also (sibling)* — [pdf-model](pdf-model.md): the PDF half of the unified "typed model + ban-lint"
  pattern; together they consolidate the raw-library corruption defect class across all four formats.
- **Counterpart** — the `openxml-direct-access` + `no-raw-xml-string-match` lints (hard) hold these
  construction-mode seams in place.
- *See also* — [canonical-walkers](canonical-walkers.md): traversal over the Office models' trees.
