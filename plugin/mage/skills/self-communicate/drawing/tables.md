# tables.md — the booktabs table style

This is an **agent-facing** style doc (the drawing leg of the `self-communicate` skill, beside
[`diagrams.md`](diagrams.md) and [`charts.md`](charts.md)), not a catalogue entry. It is not rendered to HTML
or served. A chart draws a measurement's *shape*; a **table** lays out the measurements themselves, for a
reader who looks a value up. When the content is a grid of numbers a reader reads one cell at a time, table
it — and table it in the **booktabs** style below.

Read it alongside [`charts.md`](charts.md) (chart or table? — a grid of values is a table, a trend is a chart)
and [`../writing/voice.md`](../writing/voice.md) (§"Economy — less is more"), whose prose economy this style is
the visual twin of. The style is the LaTeX [`booktabs`](https://ctan.org/pkg/booktabs) discipline — the
publishing-quality table convention — ported to HTML and print.

---

## The one rule that carries the rest: rules group, whitespace separates

A booktabs table has **horizontal rules only, and few of them**. It has **no vertical rules and no cell
borders at all**. The reason is Tufte's, and booktabs' own manual states it plainly: a vertical rule and a
boxed cell are chartjunk — ink that separates columns the eye already separates by their gap. Whitespace does
the separating; a rule is spent only where it *groups*, at the top and bottom of the table and under the
header. Every rule you add past those three is ink the reader must look past to find the number.

---

## The rules — exactly three, all horizontal

A booktabs table carries **exactly three horizontal rules**, and never a fourth kind:

- **A heavy rule at the top** — above the header row. It opens the table.
- **A light rule under the header row** — between the column names and the data. It groups the header off from
  the body.
- **A heavy rule at the bottom** — below the last data row. It closes the table.

That is the whole rule budget. **Never a vertical rule; never a cell border; never a box around the table or
any cell.** The two heavy rules bracket the table, the one light rule divides label from data, and the
columns and rows are separated by nothing but space.

(The LaTeX names are `\toprule`, `\midrule`, `\bottomrule`; the HTML analogue is a heavier `border-top` /
`border-bottom` on the `table` and a lighter `border-bottom` on the `thead`. No `border` on a `td` or `th`,
and no `border-left`/`border-right` anywhere.)

---

## Spacing, striping, and boxes

- **Generous vertical row padding.** Booktabs tables breathe — the rows sit apart, so the eye tracks along one
  without sliding into its neighbor. Increase the cell padding well past a default HTML table's cramped
  default; whitespace is the separator, so give it room to work.
- **No zebra striping.** An alternating row background is a second separator doing the job the row padding
  already does — and it is chartjunk by the same argument as the vertical rule. Rows are separated by space,
  not by color. A plain white (or plain page-color) background under every row.
- **No boxed cells, no full grid.** A cell is a number in space, not a number in a box. The failure this
  catches is the spreadsheet look — a full grid of lines around every cell, which is the maximum-chartjunk
  table and the exact thing booktabs exists to replace.

---

## Alignment and caption

- **Numbers right-aligned, text left-aligned.** A column of numbers reads down its ones, tens, hundreds when
  the digits align on the right, so a reader compares magnitudes by eye. Text columns align left, the way
  prose reads. A number column that is left-aligned makes `9` and `1000` start at the same edge and hides
  which is larger.
- **A caption sits above the table.** Unlike a figure caption (which sits below its picture), a table's caption
  sits **above** it — the reader reads the caption, then reads down into the table it introduces. The caption
  names what the table shows and any scope it carries (a sample size, a "preliminary" flag), in the same
  ≤50-word economy the prose rule demands ([`../writing/voice.md`](../writing/voice.md) §"Economy"). Like a
  figure caption, it tells the reader how to read the table and what follows from it; it must not restate the
  prose that introduces it.

---

## Why — the whole justification in one place

The style is not taste; it is data-ink. **Vertical rules and boxed cells are chartjunk** — ink that carries no
information, because the reader already sees the columns from their spacing and the rows from their padding. A
rule earns its place only where it *groups* a region off from another: the header from the body, the table
from the page above and below. That is why booktabs spends exactly three horizontal rules and no vertical ones
— **horizontal rules group, and whitespace separates.** Strip every mark that only decorates, the same
discipline as cutting a fluffy adjective from a sentence: the number is the content, and every line you draw
around it is a line the reader reads before reaching the number.

---

## The short version

Table a grid of values a reader looks up; chart a trend. Draw it booktabs: exactly three horizontal rules — a
heavy top rule, a light rule under the header, a heavy bottom rule — and **never a vertical rule or a cell
border**. Pad the rows generously, skip the zebra stripes, box nothing. Right-align numbers, left-align text,
and set the caption above the table. The whole reason is one line: vertical rules and boxes are chartjunk;
horizontal rules group, and whitespace separates.
