"""LINT `figure-font-band` — figure text must render inside a legibility BAND, not too small AND not too big.

The overflow sensor (`lint_figure_overflow`) catches text that runs PAST its box. This one catches the two
mistakes the constraint half does not prevent — text too SMALL to read (smaller than the book body copy, so
a reader who can read the prose cannot read the figure) AND text too BIG (a figure label louder than a
section heading, which the narrow-viewBox loop figures hit at ~44px). Both ends share ONE root cause: the
house SVGs author font-sizes in ABSOLUTE user units against viewBoxes that span 380 → 1300 (a ~3.4× spread),
so identical role intent renders up to 3× different — some figures shrink their text below body, others
inflate it past a heading. A single floor can only see half of a scale-inconsistency problem; the band sees
both.

How it measures (no browser, no font metrics — pure geometry against the design-token SSOT):

  * **The band — floor + ceiling.** Both come from the design tokens (`figure_styles.font.band_px`), the
    same SSOT the figures are authored against: FLOOR (a label may not render below it — a below-floor
    label is roughly half its size again in the PDF, where the page column is ~0.55× the reference width)
    and CEILING (the type scale's section/H2 step — figure text may not out-shout a heading). The band is a
    knob in the SSOT, not a constant in this file.
  * **Reference-width normalization.** A hand-authored SVG carries no absolute size — it scales to fit its
    column. Its font-sizes are quoted at the design system's figure reference width
    (`figure_styles.canvas.reference_width_px`), per the token block's own note. So the size a label
    RENDERS at, when the figure is shown at that reference width, is `font_size · reference_width /
    viewBox_width`. That normalized size is what the check compares to the band — a 12u label in a 980u
    viewBox renders ~12.2px at the 1000px reference, below a 16px floor, so it flags TOO_SMALL; a 15u label
    in a 380u viewBox renders ~39px, above a 28px ceiling, so it flags TOO_BIG.
  * **Font-size resolution.** Each `<text>`'s size resolves from its own `font-size` attribute, an
    inherited one from an ancestor `<g>`/`<svg>`, or a CSS `<style>` class — reusing the parsing in the
    sibling text-fit check (`tests/svg_fit.py`) so a class-styled label resolves the same as an
    attribute-styled one.

Excluded: `cover*` (decorative tracked-caps cover art) and `velocity-*` (data charts, no prose labels) —
the same out-of-scope set the overflow sensor carries.

LANDING: this check lands AUDIT-ONLY. The band, at any real floor, finds >0 at HEAD (the corpus predates
the shared band, so many figures sit below the floor and a handful above the ceiling). It PRINTS that
backlog (so an author sees every out-of-band figure, each end labelled) but does not gate; a re-scale wave
(`tools/rescale_figure_fonts.py`) drives each figure's fonts into the band at its own viewBox, and a
follow-up flips this blocking once the tree reads clean (the repo's audit->lint, fix-then-flip discipline).

    python3 book-models/lint_figure_font_band.py            # print findings (audit-only, exit 0)
    python3 book-models/lint_figure_font_band.py --strict   # exit 1 on any finding (the blocking flip)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_tokens as dtk  # noqa: E402 — the band + reference-width SSOT lives in the projector

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

# Float-boundary tolerance (px). A label re-scaled to render exactly AT the floor lands at 15.9999… under
# the `size · (ref/vb)` accumulation, which is not meaningfully too-small; this epsilon absorbs that noise
# without masking a genuine violation (the corpus's real sub-floor labels sit ≥0.3px under the floor).
_EPS = 0.05

TOO_SMALL = "TOO_SMALL"
TOO_BIG = "TOO_BIG"


def _band() -> tuple[float, float]:
    """The (floor, ceiling) px band figure text must render within — the design-token SSOT."""
    floor, ceiling = dtk.load().figure_band_px()
    return float(floor), float(ceiling)


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
    end: str                  # TOO_SMALL or TOO_BIG


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


def analyze(path: pathlib.Path, floor_px: float, ceiling_px: float, ref_w: float) -> list[Finding]:
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
                if rendered < floor_px - _EPS:
                    out.append(Finding(path.name, text, size, rendered, vb_w, TOO_SMALL))
                elif rendered > ceiling_px + _EPS:
                    out.append(Finding(path.name, text, size, rendered, vb_w, TOO_BIG))
        for child in el:
            walk(child, cur)

    walk(root, None)
    return out


def _in_scope(name: str) -> bool:
    return not name.startswith(EXCLUDE_PREFIXES)


def findings() -> list[Finding]:
    floor_px, ceiling_px = _band()
    ref_w = _reference_width()
    out: list[Finding] = []
    for svg in sorted(ASSETS.glob("*.svg")):
        if _in_scope(svg.name):
            try:
                out.extend(analyze(svg, floor_px, ceiling_px, ref_w))
            except ET.ParseError:
                continue  # the text-fit sensor already reports parse errors
    return out


def summary_line(fs: list[Finding]) -> str:
    floor_px, ceiling_px = _band()
    small = [f for f in fs if f.end == TOO_SMALL]
    big = [f for f in fs if f.end == TOO_BIG]
    figs = len({f.svg for f in fs})
    smallest = min((f.rendered_px for f in small), default=0.0)
    biggest = max((f.rendered_px for f in big), default=0.0)
    return (f"{len(fs)} out-of-band label(s) across {figs} figure(s) "
            f"[band {floor_px:.0f}-{ceiling_px:.0f}px at reference width {_reference_width():.0f}px]: "
            f"{len(small)} too-small (smallest {smallest:.1f}px), "
            f"{len(big)} too-big (biggest {biggest:.1f}px)")


def _per_figure(fs: list[Finding]) -> list[tuple[str, float, float, int, int]]:
    """(svg, smallest-rendered, biggest-rendered, too-small-count, too-big-count) per figure, worst-first."""
    by: dict[str, list[Finding]] = {}
    for f in fs:
        by.setdefault(f.svg, []).append(f)
    rows: list[tuple[str, float, float, int, int]] = []
    for svg, items in by.items():
        small = [x for x in items if x.end == TOO_SMALL]
        big = [x for x in items if x.end == TOO_BIG]
        smallest = min((x.rendered_px for x in small), default=0.0)
        biggest = max((x.rendered_px for x in big), default=0.0)
        rows.append((svg, smallest, biggest, len(small), len(big)))
    # Worst first: a too-big figure by how far over the ceiling, else a too-small figure by how far under.
    ceiling = _band()[1]
    return sorted(rows, key=lambda r: (-(r[2] - ceiling) if r[4] else (r[1] - 1e6)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding (the blocking flip)")
    args = ap.parse_args(argv)
    fs = findings()
    floor_px, ceiling_px = _band()
    mode = "STRICT (exit 1 on any finding)" if args.strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== figure-font-band — figure text vs [{floor_px:.0f}, {ceiling_px:.0f}]px band over "
          f"book/assets/*.svg [{mode}] ==")
    print(f"  band: {floor_px:.0f}-{ceiling_px:.0f}px · normalized at reference width "
          f"{_reference_width():.0f}px · excluded: {', '.join(EXCLUDE_PREFIXES)}*")
    if not fs:
        print("  clean — every figure label renders inside the band")
        return 0
    print(f"  {summary_line(fs)}:")
    for svg, smallest, biggest, n_small, n_big in _per_figure(fs):
        bits = []
        if n_big:
            bits.append(f"{n_big:2d} too-big (max {biggest:5.1f}px)")
        if n_small:
            bits.append(f"{n_small:2d} too-small (min {smallest:5.1f}px)")
        print(f"    [{' · '.join(bits)}] {svg}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
