"""SVG text-fit check (AUDIT-ONLY): does a hand-authored figure's text overflow its box or the canvas?

Some `book/assets/*.svg` figures render with a label spilling past its `<rect>` box, or past the
`viewBox` edge — the author has seen both. This check estimates each `<text>`'s rendered width from a
cheap average-glyph heuristic and flags the two priority cases:

  - **box overflow** — a `<text>` that sits inside a `<rect>` whose estimated horizontal extent exceeds
    the box's inner width (box width minus a small padding); the label likely spills its box.
  - **canvas overflow** — a `<text>` whose estimated horizontal extent runs past the `viewBox` width;
    the label likely spills the whole figure.

**This is a HEURISTIC.** Rendered glyph width varies by font, kerning, and the actual glyph mix, so an
average-ratio estimate (`len(text) * font-size * ~0.55`, `~0.6` bold) WILL produce false positives. So the
check runs **AUDIT-ONLY**: it reports candidates and returns exit-neutral (never contributes to the suite's
fail count). A follow-up promotes it to blocking once the ratio and padding are tuned against the real
corpus. Label-over-arrow overlap is a known gap (precise geometry is hard); box + canvas overflow are the
priority the author asked for.

When it flags a figure, the report points the reader at the fix runbook so an agent knows where to go.
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET

from tests.common import PASS, ROOT, rel

# Where an agent goes when a figure is flagged. Repo-relative; the check echoes it on every finding.
RUNBOOK = "book/_design/figure-text-fit-runbook.md"

# Average glyph width as a fraction of the font-size (em). A crude but serviceable mean across a
# mixed-case sans-serif label; bold runs a touch wider. Deliberately conservative-low to keep the
# audit's false-positive rate down — a too-eager ratio floods the report with non-overflows.
GLYPH_RATIO = 0.55
GLYPH_RATIO_BOLD = 0.60

# Inner-width padding: a box's text area is narrower than its rect by this fraction of the box width on
# EACH side (labels are inset from the stroke, not flush to it). 0.06 => 12% of width reserved as margin.
BOX_INNER_PAD_FRAC = 0.06

# Overflow must clear a margin before it counts, so a marginal estimation error (a glyph or two of slop in
# the average-ratio guess) doesn't flood the audit. A candidate must overflow by at least this many
# font-size ems — roughly two glyphs — OR this fraction of the reference width, whichever is larger.
MIN_OVERFLOW_EMS = 1.5
MIN_OVERFLOW_FRAC = 0.10

# A box only "holds" a label when the label's anchor sits in the box's central band, not hugging an edge.
# A caption whose baseline grazes a box's bottom stroke is an annotation BELOW the box, not text inside it;
# measuring it against that box is a false positive. Require the anchor's y to sit within this central
# fraction of the box height (0.15..0.85), and its x within the inner x-range.
BOX_CENTRAL_BAND = (0.15, 0.85)

# A rect that fills a large fraction of the canvas is a background or a PANEL — a container for other
# shapes and multi-line prose, not a label box that tightly wraps one string. Measuring a caption against
# a panel's inner width flags every intentionally-wide prose line; a panel's contents are meant to run
# near its edges. So a rect wider than this fraction of the viewBox width is treated as a container and
# skipped for box-overflow (its text is still checked against the CANVAS). Label boxes are much narrower.
PANEL_WIDTH_FRAC = 0.45

# SVG namespace — the assets declare xmlns="http://www.w3.org/2000/svg", so ET tags come back namespaced.
_SVG_NS = "http://www.w3.org/2000/svg"


def _local(tag: str) -> str:
    """Strip the `{namespace}` prefix ElementTree prepends, so `{...}text` -> `text`."""
    return tag.rsplit("}", 1)[-1]


def _parse_style_font_sizes(root: ET.Element) -> dict[str, tuple[float, bool]]:
    """Map each CSS class in a `<style>` block to (font_size_px, is_bold).

    Figures declare font sizing two ways: a `font-size` attribute on the `<text>`, or a CSS class whose
    rule lives in an SVG `<style>` block (e.g. `.btitle { font-size:32px; font-weight:700; }`). Parse the
    class rules so a class-styled label resolves its size the same as an attribute-styled one.
    """
    classes: dict[str, tuple[float, bool]] = {}
    for el in root.iter():
        if _local(el.tag) != "style" or not el.text:
            continue
        # Each rule: `.name { ...decls... }`. Pull font-size + font-weight out of the decl block.
        for cls, body in re.findall(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}", el.text):
            m = re.search(r"font-size\s*:\s*([0-9.]+)", body)
            if not m:
                continue
            size = float(m.group(1))
            bold = bool(re.search(r"font-weight\s*:\s*(bold|[6-9]00)", body))
            classes[cls] = (size, bold)
    return classes


def _font_size_and_weight(el: ET.Element, style_classes: dict[str, tuple[float, bool]]) -> tuple[float, bool] | None:
    """Resolve a `<text>` element's (font_size, is_bold) from its attribute or its CSS class; None if
    neither supplies a size (can't estimate width without one)."""
    size: float | None = None
    bold = False
    fs = el.get("font-size")
    if fs:
        m = re.match(r"([0-9.]+)", fs)
        if m:
            size = float(m.group(1))
    fw = el.get("font-weight")
    if fw and re.match(r"(bold|[6-9]00)", fw):
        bold = True
    # A class can supply the size (and boldness) when the attribute doesn't.
    cls_attr = el.get("class")
    if cls_attr:
        for name in cls_attr.split():
            if name in style_classes:
                c_size, c_bold = style_classes[name]
                if size is None:
                    size = c_size
                bold = bold or c_bold
    if size is None:
        return None
    return size, bold


def _text_content(el: ET.Element) -> str:
    """Flatten a `<text>` (and any `<tspan>` children) to its visible string."""
    return "".join(el.itertext()).strip()


def _num(v: str | None) -> float | None:
    if v is None:
        return None
    m = re.match(r"(-?[0-9.]+)", v)
    return float(m.group(1)) if m else None


def _viewbox_width(root: ET.Element) -> float | None:
    vb = root.get("viewBox")
    if vb:
        parts = re.split(r"[\s,]+", vb.strip())
        if len(parts) == 4:
            return float(parts[2])
    return _num(root.get("width"))


class _Rect:
    """A `<rect>` box: outer x/y/width/height plus the inner (padded) x-range a label should stay within."""

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y, self.w, self.h = x, y, w, h
        pad = w * BOX_INNER_PAD_FRAC
        self.inner_left = x + pad
        self.inner_right = x + w - pad
        self.inner_w = self.inner_right - self.inner_left

    def contains_point(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def holds_label(self, px: float, py: float) -> bool:
        """True when the anchor sits in the box's central band — text meant to live INSIDE the box, not a
        caption grazing an edge (which is an annotation beside/below the box, not bounded by it)."""
        if not (self.x <= px <= self.x + self.w):
            return False
        lo, hi = BOX_CENTRAL_BAND
        return self.y + self.h * lo <= py <= self.y + self.h * hi


def _collect_rects(root: ET.Element, vb_w: float | None) -> list[_Rect]:
    """Every `<rect>` that is a plausible label box: has x/y/w/h and is NARROWER than PANEL_WIDTH_FRAC of
    the canvas (a wider rect is a background/panel container, not a per-label box — see PANEL_WIDTH_FRAC)."""
    panel_cap = vb_w * PANEL_WIDTH_FRAC if vb_w else None
    rects: list[_Rect] = []
    for el in root.iter():
        if _local(el.tag) != "rect":
            continue
        x, y = _num(el.get("x")), _num(el.get("y"))
        w, h = _num(el.get("width")), _num(el.get("height"))
        if None in (x, y, w, h) or w <= 0 or h <= 0:
            continue
        if panel_cap is not None and w > panel_cap:
            continue  # background or panel — its contents are checked against the canvas, not this rect
        rects.append(_Rect(x, y, w, h))  # type: ignore[arg-type]
    return rects


def _text_extent(text: str, size: float, bold: bool, anchor: str) -> tuple[float, float]:
    """(left_x_offset, right_x_offset) of the estimated text run relative to the element's x.

    Width ~= len * size * ratio. `text-anchor` decides how the run sits about the x point:
    `start` runs rightward, `middle` centers, `end` runs leftward.
    """
    ratio = GLYPH_RATIO_BOLD if bold else GLYPH_RATIO
    width = len(text) * size * ratio
    if anchor == "middle":
        return -width / 2.0, width / 2.0
    if anchor == "end":
        return -width, 0.0
    return 0.0, width  # start (default)


def _innermost_holding_rect(rects: list[_Rect], px: float, py: float) -> _Rect | None:
    """The tightest box whose central band holds the text anchor — smallest-area wins, so a label inside a
    panel is measured against the panel, not the page-background rect that also contains it."""
    hits = [r for r in rects if r.holds_label(px, py)]
    if not hits:
        return None
    return min(hits, key=lambda r: r.w * r.h)


def _over_threshold(overflow: float, size: float, reference_w: float) -> bool:
    """A candidate counts only if it clears the noise floor: at least MIN_OVERFLOW_EMS font-ems OR
    MIN_OVERFLOW_FRAC of the reference width, whichever is larger."""
    floor = max(MIN_OVERFLOW_EMS * size, MIN_OVERFLOW_FRAC * reference_w)
    return overflow >= floor


def check_svg_text_fit():
    """Scan every `book/assets/*.svg`; flag `<text>` estimated to overflow its box or the canvas.

    AUDIT-ONLY: always returns PASS (exit-neutral). Findings print as guidance, each pointing at the
    runbook. Returns (PASS, issues) — `issues` is the human-readable candidate list.
    """
    assets_dir = os.path.join(ROOT, "book", "assets")
    if not os.path.isdir(assets_dir):
        return PASS, ["no book/assets/ dir — nothing to scan"]

    issues: list[str] = []
    flagged_files: set[str] = set()
    for fn in sorted(os.listdir(assets_dir)):
        if not fn.endswith(".svg"):
            continue
        path = os.path.join(assets_dir, fn)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as e:
            issues.append(f"{rel(path)}: XML parse error ({e}) — cannot scan")
            continue

        vb_w = _viewbox_width(root)
        style_classes = _parse_style_font_sizes(root)
        rects = _collect_rects(root, vb_w)

        for el in root.iter():
            if _local(el.tag) != "text":
                continue
            text = _text_content(el)
            if not text:
                continue
            x, y = _num(el.get("x")), _num(el.get("y"))
            if x is None or y is None:
                continue  # dx/dy-positioned or tspan-driven; skip (can't anchor it cheaply)
            fw = _font_size_and_weight(el, style_classes)
            if fw is None:
                continue
            size, bold = fw
            anchor = (el.get("text-anchor") or "start").strip()
            left_off, right_off = _text_extent(text, size, bold, anchor)
            text_left, text_right = x + left_off, x + right_off
            est_w = right_off - left_off
            label = text if len(text) <= 42 else text[:39] + "..."

            # Canvas overflow: the estimated run runs off the left edge (<0) or past the viewBox width.
            if vb_w is not None:
                over = max(text_right - vb_w, -text_left)
                if over > 0 and _over_threshold(over, size, vb_w):
                    issues.append(
                        f"{rel(path)}: CANVAS overflow — text {label!r} (est width {est_w:.0f}u, "
                        f"font {size:.0f}u) extends to x={text_right:.0f} past viewBox width {vb_w:.0f} "
                        f"(over by ~{over:.0f}u)")
                    flagged_files.add(fn)
                    continue  # a canvas overflow is the more serious of the two; report it and move on

            # Box overflow: the run exceeds the inner width of the tightest box holding it.
            box = _innermost_holding_rect(rects, x, y)
            if box is not None:
                over = est_w - box.inner_w
                if over > 0 and _over_threshold(over, size, box.inner_w):
                    issues.append(
                        f"{rel(path)}: BOX overflow — text {label!r} (est width {est_w:.0f}u, font "
                        f"{size:.0f}u) exceeds box inner width {box.inner_w:.0f}u "
                        f"(rect x={box.x:.0f} w={box.w:.0f}, over by ~{over:.0f}u)")
                    flagged_files.add(fn)

    if issues:
        issues.append("")
        issues.append(f"AUDIT-ONLY (heuristic; false positives expected). Fix guidance -> {RUNBOOK}")
        issues.insert(0, f"{len(flagged_files)} figure(s) with candidate overflow "
                         f"(est. glyph ratio {GLYPH_RATIO}/{GLYPH_RATIO_BOLD} bold):")
    return PASS, issues  # AUDIT-ONLY: never FAIL
