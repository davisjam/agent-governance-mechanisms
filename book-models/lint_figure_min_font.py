"""LINT `figure-min-font` — figure text must not render SMALLER than the book body text.

The overflow sensor (`lint_figure_overflow`) catches text that runs PAST its box. This one catches the
opposite mistake the constraint half does not prevent: text that renders too SMALL to read — smaller than
the book's own body copy, so a reader who can read the prose cannot read the figure. Figure 3.8-1 (the
two-layer net) and Figure 4.2-1 (the three skills) are the cases the author flagged: legible-in-isolation
labels that shrink below body size once the figure sits in its column.

How it measures (no browser, no font metrics — pure geometry against the design-token SSOT):

  * **Body size — the floor.** The book body-text size comes from the design-token scale
    (`design_tokens.px("body")`), the same SSOT the web/print bodies render from. That is the floor: no
    figure text may render below it.
  * **Reference-width normalization.** A hand-authored SVG carries no absolute size — it scales to fit its
    column. Its font-sizes are quoted at the design system's figure reference width
    (`figure_styles.canvas.reference_width_px`), per the token block's own note. So the size a label
    RENDERS at, when the figure is shown at that reference width, is `font_size · reference_width /
    viewBox_width`. That normalized size is what the check compares to the body floor — a label of 12u in a
    980u viewBox renders at ~12.2px at the 1000px reference, below the 18px body, so it flags.
  * **Font-size resolution.** Each `<text>`'s size resolves from its own `font-size` attribute, an
    inherited one from an ancestor `<g>`/`<svg>`, or a CSS `<style>` class — reusing the parsing in the
    sibling text-fit check (`tests/svg_fit.py`) so a class-styled label resolves the same as an
    attribute-styled one.

Excluded: `cover*` (decorative tracked-caps cover art) and `velocity-*` (data charts, no prose labels) —
the same out-of-scope set the overflow sensor carries.

LANDING: this check lands AUDIT-ONLY. Most house figures use the design system's small label roles
(`sub_label` 12u, `label` 14u), which normalize below body, so a strict body floor surfaces a corpus-wide
backlog no single change can drain. It PRINTS that backlog (so an author sees every too-small figure) but
does not gate; the author's two named figures are enlarged now, and a follow-up flips it blocking once a
dedicated re-layout wave drains the rest (the repo's audit->lint, fix-then-flip discipline).

    python3 book-models/lint_figure_min_font.py            # print findings (audit-only, exit 0)
    python3 book-models/lint_figure_min_font.py --strict   # exit 1 on any finding (the blocking flip)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_tokens as dtk  # noqa: E402 — the body-size + reference-width SSOT lives in the projector

# Reuse the sibling text-fit check's SVG parsing (CSS-class font-size map, viewBox width, tag/text helpers)
# so a class-styled label resolves its size exactly as it does there — one parser, two checks.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tests.svg_fit import (  # noqa: E402
    _local,
    _parse_style_font_sizes,
    _text_content,
    _viewbox_width,
)

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "book" / "assets"

# Figures out of scope for a body-legibility test: decorative cover art + data charts (no prose labels).
EXCLUDE_PREFIXES = ("cover", "velocity-")


def _body_px() -> float:
    """The book body-text size (px) — the floor figure text may not render below. Design-token SSOT."""
    return float(dtk.load().px("body"))


def _reference_width() -> float:
    """The width (px) at which the house SVGs' font-sizes are quoted — the design-token figure SSOT."""
    return float(dtk.load().figure_styles["canvas"]["reference_width_px"])


@dataclass(frozen=True)
class Finding:
    svg: str
    text: str
    font_size: float          # the size as authored, in viewBox user units
    rendered_px: float        # normalized to the reference width — what it renders at
    viewbox_w: float


def _resolve_size(el: ET.Element, inherited: float | None,
                  style_classes: dict[str, tuple[float, bool]]) -> float | None:
    """Resolve a `<text>`'s font-size (user units) from its own attribute, an inherited one, or a CSS class."""
    size = inherited
    fs = el.get("font-size")
    if fs:
        num = "".join(ch for ch in fs if (ch.isdigit() or ch == "."))
        if num:
            try:
                size = float(num)
            except ValueError:
                pass
    cls_attr = el.get("class")
    if size is None and cls_attr:
        for name in cls_attr.split():
            if name in style_classes:
                size = style_classes[name][0]
                break
    return size


def analyze(path: pathlib.Path, body_px: float, ref_w: float) -> list[Finding]:
    root = ET.parse(path).getroot()
    vb_w = _viewbox_width(root)
    if not vb_w:
        return []
    style_classes = _parse_style_font_sizes(root)
    scale = ref_w / vb_w  # user unit -> px at the reference render width
    out: list[Finding] = []

    def walk(el: ET.Element, inherited: float | None) -> None:
        # font-size inherits down the tree, so carry the nearest ancestor value as the default.
        cur = inherited
        fs_attr = el.get("font-size")
        if fs_attr:
            num = "".join(ch for ch in fs_attr if (ch.isdigit() or ch == "."))
            if num:
                try:
                    cur = float(num)
                except ValueError:
                    pass
        if _local(el.tag) == "text":
            text = _text_content(el)
            size = _resolve_size(el, inherited, style_classes)
            if text and size is not None:
                rendered = size * scale
                if rendered < body_px:
                    out.append(Finding(path.name, text, size, rendered, vb_w))
        for child in el:
            walk(child, cur)

    walk(root, None)
    return out


def _in_scope(name: str) -> bool:
    return not name.startswith(EXCLUDE_PREFIXES)


def findings() -> list[Finding]:
    body_px = _body_px()
    ref_w = _reference_width()
    out: list[Finding] = []
    for svg in sorted(ASSETS.glob("*.svg")):
        if _in_scope(svg.name):
            try:
                out.extend(analyze(svg, body_px, ref_w))
            except ET.ParseError:
                continue  # the text-fit sensor already reports parse errors
    return out


def summary_line(fs: list[Finding]) -> str:
    figs = len({f.svg for f in fs})
    smallest = min((f.rendered_px for f in fs), default=0.0)
    return (f"{len(fs)} too-small label(s) across {figs} figure(s) "
            f"(body floor {_body_px():.0f}px at reference width {_reference_width():.0f}px; "
            f"smallest renders at {smallest:.1f}px)")


def _per_figure(fs: list[Finding]) -> list[tuple[str, float, int]]:
    """(svg, smallest-rendered-px, count) per figure, smallest-first — the enlarge worklist."""
    by: dict[str, list[Finding]] = {}
    for f in fs:
        by.setdefault(f.svg, []).append(f)
    rows = [(svg, min(x.rendered_px for x in items), len(items)) for svg, items in by.items()]
    return sorted(rows, key=lambda r: r[1])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding (the blocking flip)")
    args = ap.parse_args(argv)
    fs = findings()
    mode = "STRICT (exit 1 on any finding)" if args.strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== figure-min-font — figure text vs body-size floor over book/assets/*.svg [{mode}] ==")
    print(f"  floor: body {_body_px():.0f}px · normalized at reference width {_reference_width():.0f}px · "
          f"excluded: {', '.join(EXCLUDE_PREFIXES)}*")
    if not fs:
        print("  clean — every figure label renders at or above body size")
        return 0
    print(f"  {summary_line(fs)}:")
    for svg, smallest, n in _per_figure(fs):
        print(f"    [{smallest:5.1f}px min · {n:2d} label(s)] {svg}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
