"""LINT `figure-label-collision` — a connector stroke must not run THROUGH a free-floating text label.

PROVENANCE. Distilled from a figure-QA pilot (260807) that rendered every hand-authored figure and
looked. The pilot validated a pure-geometry collision detector against one ground-truth defect — a
dashed feedback edge drawn straight through a rotated "the theory changed" label — and found the raw
detector had ~4% precision: it flagged 24 of 87 figures, nearly all false. This file is the pilot's
prototype PLUS four precision filters — the two the pilot's report prescribed (free-floating-label,
faint-stroke) and two more found while adjudicating the survivors against the rendered figures
(dock-vs-through, glyph-core) — tuned so the corpus reads clean while the reintroduced ground-truth
defect still flags with margin (7 core hits vs a survivor ceiling of 2).

THE DEFECT CLASS. The overflow sensor catches text that overruns its own box; the font-band sensor catches
text too small or too big to read. Neither sees a *third* class: a line, arrow, or curve that crosses the
glyphs of a nearby label so the reader parses stroke and text as one smear. That is a legibility defect the
geometry CAN see — a stroke sample lands inside a text's core box — but only after the check discards the
patterns that look identical to geometry yet read fine:

  * **Free-floating-label filter (the precision lever).** A stroke that passes UNDER an opaque box does not
    touch the label painted ON the box — the box border, the gridline behind a step, the arrowhead docking
    at a node title, the decorative check-glyph inside a pill all cross a label's box only because the label
    sits on a filled shape that hides the stroke. So a label is a candidate ONLY when it is *free-floating*:
    its center lies in no filled shape (rect / rounded-rect / circle / ellipse / filled path) other than the
    full-canvas background. A label riding a canvas-coloured halo counts as enclosed — the halo is exactly
    the fix for this defect, and a fixed label must not re-flag.
  * **Faint-stroke gating.** A pale, low-contrast connector web (a many-to-many guide at ~0.2 luminance
    contrast against a near-white canvas) crosses labels yet stays legible because the eye reads it as
    background. A stroke is gated out when its effective opacity is low OR its colour sits within a small
    luminance contrast of the canvas. A dark, saturated edge (the research-arc feedback edge) clears the
    gate and still flags.
  * **Dock-vs-through.** An arrow that POINTS AT a label ends inside it — its interior samples run to a
    stroke endpoint, by design (a node arrowhead docking at its title). A genuine smear PASSES THROUGH:
    the stroke has samples outside the label on both sides of the interior run. Only entered-and-exited
    crossings count, so docking arrows over box-less node labels (the survivors' dominant class) drop.
  * **Glyph-core box.** The hit-box is the readable core (about cap-height above the baseline, a hair
    below, no padding), not the full em. A stroke skimming the ascender tuft above a cap or curving just
    beneath the baseline never smears the letters a reader parses, so it does not count.

What geometry CANNOT catch, and this lint deliberately does not pretend to: TEXT-ON-TEXT crowding, where two
labels or a text-glyph arrow crowd each other (there is no stroke element to test). That class is caught only
by a vision pass over the rendered figure. This lint is the cheap, deterministic COMPLEMENT to that pass, not
a replacement — it guards the exact stroke-through-a-free-label class and nothing wider.

LANDING: AUDIT-ONLY. It prints any finding and returns 0 from the shared validator; it does not gate. A new
geometric sensor over a hand-authored corpus earns its blocking flip only after a clean run proves it stays
at (or near) zero, so it lands audit-only first per the repo's blocking-lint discipline.

  python3 book-models/lint_figure_label_collision.py            # print findings (audit-only, exits 0)
  python3 book-models/lint_figure_label_collision.py --strict   # exit 1 on any finding (the blocking flip)
  python3 book-models/lint_figure_label_collision.py <file.svg> # check specific figure(s)
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "book" / "assets"

# Figures out of scope: decorative cover art + data charts (axis lines legitimately meet tick labels) — the
# same out-of-scope set the overflow / font-band sibling sensors carry.
EXCLUDE_PREFIXES = ("cover", "velocity-")

# --- tunables -------------------------------------------------------------
# The hit-box models the READABLE GLYPH CORE, not the full em: a stroke grazing the ascender tuft above a
# cap or passing just below the baseline does not smear the letters a reader parses, so the box stops at
# roughly cap-height above the baseline and a hair below it, with no slack. This is the second precision
# lever after the free-floating filter — it drops top-graze and under-run false positives (an arc curving
# over a node title, a return edge skimming beneath a label) while a stroke crossing the letter bodies
# still lands many interior samples. Validated: the reintroduced research-arc defect scores 7 core hits,
# every current-tree graze scores <=2, so MIN_HITS=3 separates them with margin.
CHAR_W = 0.52          # mean glyph advance as fraction of font-size
ASC = 0.60             # core height above baseline (font-size fraction) — cap/x-height body, not ascender tuft
DESC = 0.08            # core depth below baseline — excludes descender fringe
MARGIN = 0.0           # no slack: a hit must land in the readable core, not a padded halo around it
BEZIER_STEPS = 24      # samples per cubic/quadratic segment
MIN_HITS = 3           # core samples needed to flag (a genuine pass-through, not a tangent/graze)
BG_AREA_FRAC = 0.85    # a filled shape covering >= this fraction of the canvas is the background, not a box
OPACITY_MIN = 0.45     # a stroke fainter than this (effective opacity) is background, not a connector
CONTRAST_MIN = 0.30    # a stroke within this luminance distance of the canvas is too pale to smear a label
SVG_NS = "{http://www.w3.org/2000/svg}"


# --- 2x3 affine matrix (a b c d e f): x'=a*x+c*y+e, y'=b*x+d*y+f ----------
def mat_mul(m1: tuple, m2: tuple) -> tuple:
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2,
            b1 * c2 + d1 * d2, a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def apply(m: tuple, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def parse_transform(s: str | None) -> tuple:
    if not s:
        return IDENT
    m = IDENT
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s):
        nums = [float(v) for v in re.split(r"[\s,]+", args.strip()) if v]
        if name == "translate":
            t = (1, 0, 0, 1, nums[0], nums[1] if len(nums) > 1 else 0.0)
        elif name == "scale":
            sx = nums[0]
            t = (sx, 0, 0, nums[1] if len(nums) > 1 else sx, 0, 0)
        elif name == "rotate":
            ang = math.radians(nums[0])
            cos, sin = math.cos(ang), math.sin(ang)
            r = (cos, sin, -sin, cos, 0, 0)
            if len(nums) == 3:
                cx, cy = nums[1], nums[2]
                t = mat_mul((1, 0, 0, 1, cx, cy), mat_mul(r, (1, 0, 0, 1, -cx, -cy)))
            else:
                t = r
        elif name == "matrix" and len(nums) == 6:
            t = tuple(nums)
        else:
            t = IDENT
        m = mat_mul(m, t)
    return m


# --- path flattening ------------------------------------------------------
def _tokenize_path(d: str) -> list[str]:
    return re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d)


def _cubic(p0, p1, p2, p3, steps=BEZIER_STEPS):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        out.append((mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                    mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]))
    return out


def _quad(p0, p1, p2, steps=BEZIER_STEPS):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        out.append((mt**2 * p0[0] + 2 * mt * t * p1[0] + t**2 * p2[0],
                    mt**2 * p0[1] + 2 * mt * t * p1[1] + t**2 * p2[1]))
    return out


def flatten_path(d: str) -> list[tuple[float, float]]:
    """Return sample points along a path d-string (user space)."""
    toks = _tokenize_path(d)
    i = 0
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    prev_ctrl = None
    pts: list[tuple[float, float]] = []
    cmd = None

    def nxt() -> float:
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
        rel = cmd.islower()
        C = cmd.upper()
        if C == "M":
            x, y = nxt(), nxt()
            if rel:
                x, y = cur[0] + x, cur[1] + y
            cur = (x, y)
            start = cur
            pts.append(cur)
            cmd = "l" if rel else "L"
        elif C == "L":
            x, y = nxt(), nxt()
            if rel:
                x, y = cur[0] + x, cur[1] + y
            cur = (x, y)
            pts.append(cur)
        elif C == "H":
            x = nxt()
            cur = (cur[0] + x if rel else x, cur[1])
            pts.append(cur)
        elif C == "V":
            y = nxt()
            cur = (cur[0], cur[1] + y if rel else y)
            pts.append(cur)
        elif C == "C":
            c1 = (nxt(), nxt())
            c2 = (nxt(), nxt())
            e = (nxt(), nxt())
            if rel:
                c1 = (cur[0] + c1[0], cur[1] + c1[1])
                c2 = (cur[0] + c2[0], cur[1] + c2[1])
                e = (cur[0] + e[0], cur[1] + e[1])
            pts.extend(_cubic(cur, c1, c2, e))
            prev_ctrl = c2
            cur = e
        elif C == "S":
            c2 = (nxt(), nxt())
            e = (nxt(), nxt())
            if rel:
                c2 = (cur[0] + c2[0], cur[1] + c2[1])
                e = (cur[0] + e[0], cur[1] + e[1])
            c1 = cur if prev_ctrl is None else (2 * cur[0] - prev_ctrl[0], 2 * cur[1] - prev_ctrl[1])
            pts.extend(_cubic(cur, c1, c2, e))
            prev_ctrl = c2
            cur = e
        elif C == "Q":
            c1 = (nxt(), nxt())
            e = (nxt(), nxt())
            if rel:
                c1 = (cur[0] + c1[0], cur[1] + c1[1])
                e = (cur[0] + e[0], cur[1] + e[1])
            pts.extend(_quad(cur, c1, e))
            prev_ctrl = c1
            cur = e
        elif C == "T":
            e = (nxt(), nxt())
            if rel:
                e = (cur[0] + e[0], cur[1] + e[1])
            c1 = cur if prev_ctrl is None else (2 * cur[0] - prev_ctrl[0], 2 * cur[1] - prev_ctrl[1])
            pts.extend(_quad(cur, c1, e))
            prev_ctrl = c1
            cur = e
        elif C == "A":
            nxt(); nxt(); nxt(); nxt(); nxt()
            e = (nxt(), nxt())
            if rel:
                e = (cur[0] + e[0], cur[1] + e[1])
            cur = e
            pts.append(cur)
        elif C == "Z":
            cur = start
            pts.append(cur)
        else:
            i += 1
        if C not in ("C", "S", "Q", "T"):
            prev_ctrl = None
    return pts


# --- colour / luminance ---------------------------------------------------
_NAMED = {"black": (0, 0, 0), "white": (255, 255, 255), "none": None}


def parse_color(c: str | None) -> tuple[int, int, int] | None:
    if not c:
        return None
    c = c.strip().lower()
    if c in _NAMED:
        return _NAMED[c]
    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            return tuple(int(ch * 2, 16) for ch in h)  # type: ignore[return-value]
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    m = re.match(r"rgb\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)", c)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (v / 255.0 for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# --- text OBB (rotated bounding polygon) ----------------------------------
class TextBox:
    def __init__(self, text: str, x: float, y: float, font_size: float, anchor: str, matrix: tuple):
        self.text = text
        n = len(text)
        w = max(n * font_size * CHAR_W, font_size * 0.6)
        if anchor == "middle":
            x0, x1 = x - w / 2, x + w / 2
        elif anchor == "end":
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        y0, y1 = y - font_size * ASC, y + font_size * DESC
        x0 -= MARGIN; x1 += MARGIN; y0 -= MARGIN; y1 += MARGIN
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.poly = [apply(matrix, cx, cy) for cx, cy in corners]
        self.center = apply(matrix, (x0 + x1) / 2, (y0 + y1) / 2)

    def contains(self, px: float, py: float) -> bool:
        poly = self.poly
        inside = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
                inside = not inside
            j = i
        return inside


@dataclass
class Stroke:
    sid: str
    kind: str
    pts: list[tuple[float, float]]
    faint: bool


@dataclass
class Enclosure:
    x0: float
    y0: float
    x1: float
    y1: float

    def area(self) -> float:
        return abs(self.x1 - self.x0) * abs(self.y1 - self.y0)

    def contains(self, px: float, py: float) -> bool:
        return self.x0 <= px <= self.x1 and self.y0 <= py <= self.y1


@dataclass
class Scene:
    texts: list[TextBox] = field(default_factory=list)
    strokes: list[Stroke] = field(default_factory=list)
    enclosures: list[Enclosure] = field(default_factory=list)
    bg_lum: float = 0.988  # near-white canvas default


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _id(elem) -> str:
    return elem.get("id") or elem.get("class") or _local(elem.tag)


def _num(elem, attr: str, default: float = 0.0) -> float:
    v = elem.get(attr)
    if v is None:
        return default
    m = re.match(r"-?\d*\.?\d+", v.strip())
    return float(m.group()) if m else default


def _bbox_of(pts: list[tuple[float, float]]) -> Enclosure:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return Enclosure(min(xs), min(ys), max(xs), max(ys))


@dataclass
class Style:
    matrix: tuple = IDENT
    font_size: float = 16.0
    opacity: float = 1.0        # product of ancestor opacity
    stroke: str | None = None   # inherited stroke colour
    stroke_opacity: float = 1.0
    fill: str | None = "black"  # SVG default fill is black


def collect(elem, st: Style, scene: Scene) -> None:
    m = mat_mul(st.matrix, parse_transform(elem.get("transform")))
    fs = elem.get("font-size")
    font_size = float(re.sub(r"[a-z%]+$", "", fs)) if fs else st.font_size
    op = st.opacity * (_num(elem, "opacity", 1.0))
    stroke = elem.get("stroke", st.stroke)
    stroke_op = st.stroke_opacity * _num(elem, "stroke-opacity", 1.0)
    fill = elem.get("fill", st.fill)
    child_st = Style(m, font_size, op, stroke, stroke_op, fill)
    tag = _local(elem.tag)

    def _has_stroke() -> bool:
        return bool(stroke) and stroke.strip().lower() != "none"

    def _has_fill() -> bool:
        return bool(fill) and fill.strip().lower() != "none"

    def _faint() -> bool:
        eff = op * stroke_op
        if eff < OPACITY_MIN:
            return True
        rgb = parse_color(stroke) if _has_stroke() else None
        if rgb is None:
            return False
        return abs(luminance(rgb) - scene.bg_lum) < CONTRAST_MIN

    if tag == "text":
        txt = "".join(elem.itertext()).strip()
        if txt:
            anchor = elem.get("text-anchor", "start")
            scene.texts.append(TextBox(txt, _num(elem, "x"), _num(elem, "y"), font_size, anchor, m))
        return  # a <tspan> child is part of this label, never a separate one
    elif tag in ("rect",):
        x, y = _num(elem, "x"), _num(elem, "y")
        w, h = _num(elem, "width"), _num(elem, "height")
        corners = [apply(m, x, y), apply(m, x + w, y), apply(m, x + w, y + h), apply(m, x, y + h)]
        if _has_fill():
            scene.enclosures.append(_bbox_of(corners))
    elif tag in ("circle", "ellipse"):
        cx, cy = _num(elem, "cx"), _num(elem, "cy")
        rx = _num(elem, "r") or _num(elem, "rx")
        ry = _num(elem, "r") or _num(elem, "ry")
        corners = [apply(m, cx - rx, cy - ry), apply(m, cx + rx, cy - ry),
                   apply(m, cx + rx, cy + ry), apply(m, cx - rx, cy + ry)]
        if _has_fill():
            scene.enclosures.append(_bbox_of(corners))
    elif tag == "path":
        d = elem.get("d")
        if d:
            pts = [apply(m, px, py) for px, py in flatten_path(d)]
            if _has_fill():
                scene.enclosures.append(_bbox_of(pts))  # a filled path is a shape (blob/wedge), an enclosure
            else:
                scene.strokes.append(Stroke(_id(elem), "path", pts, _faint()))
    elif tag == "line":
        x1, y1, x2, y2 = _num(elem, "x1"), _num(elem, "y1"), _num(elem, "x2"), _num(elem, "y2")
        pts = [apply(m, x1 + (x2 - x1) * t / 12, y1 + (y2 - y1) * t / 12) for t in range(13)]
        scene.strokes.append(Stroke(_id(elem), "line", pts, _faint()))
    elif tag in ("polyline", "polygon"):
        raw = elem.get("points", "")
        nums = [float(v) for v in re.split(r"[\s,]+", raw.strip()) if v]
        raw_pts = list(zip(nums[0::2], nums[1::2]))
        dense = []
        for k in range(len(raw_pts) - 1):
            (ax, ay), (bx, by) = raw_pts[k], raw_pts[k + 1]
            for t in range(13):
                dense.append((ax + (bx - ax) * t / 12, ay + (by - ay) * t / 12))
        pts = [apply(m, px, py) for px, py in dense]
        if tag == "polygon" and _has_fill():
            scene.enclosures.append(_bbox_of(pts))
        else:
            scene.strokes.append(Stroke(_id(elem), tag, pts, _faint()))

    for child in elem:
        collect(child, child_st, scene)


@dataclass
class Finding:
    svg: str
    label: str
    stroke_kind: str
    samples: int
    frac: float


def _canvas_area(root) -> float:
    vb = root.get("viewBox")
    if vb:
        parts = [float(v) for v in re.split(r"[\s,]+", vb.strip()) if v]
        if len(parts) == 4:
            return parts[2] * parts[3]
    return _num(root, "width", 1000.0) * _num(root, "height", 1000.0)


def _bg_luminance(root, scene: Scene, canvas_area: float) -> float:
    # The canvas background is the first big filled rect; its fill sets the contrast reference.
    for elem in root.iter():
        if _local(elem.tag) == "rect":
            w, h = _num(elem, "width"), _num(elem, "height")
            fill = elem.get("fill")
            if w * h >= BG_AREA_FRAC * canvas_area and fill and fill.lower() != "none":
                rgb = parse_color(fill)
                if rgb is not None:
                    return luminance(rgb)
            break  # only the first rect can be the backdrop
    return 0.988


def analyze(path: pathlib.Path) -> list[Finding]:
    tree = ET.parse(path)
    root = tree.getroot()
    canvas_area = _canvas_area(root)
    scene = Scene()
    scene.bg_lum = _bg_luminance(root, scene, canvas_area)
    root_fs = root.get("font-size")
    st = Style(IDENT, float(re.sub(r"[a-z%]+$", "", root_fs)) if root_fs else 16.0,
               1.0, root.get("stroke"), 1.0, root.get("fill", "black"))
    collect(root, st, scene)

    # Drop the full-canvas background from the enclosure set: everything sits "inside" it, so keeping it
    # would enclose every label and the check would flag nothing.
    boxes = [e for e in scene.enclosures if e.area() < BG_AREA_FRAC * canvas_area]

    def enclosed(tb: TextBox) -> bool:
        cx, cy = tb.center
        return any(b.contains(cx, cy) for b in boxes)

    findings: list[Finding] = []
    for stroke in scene.strokes:
        if stroke.faint:
            continue
        n = len(stroke.pts)
        for tb in scene.texts:
            if enclosed(tb):
                continue  # a label riding a filled shape (box / chip / pill / halo) hides the stroke
            idxs = [i for i, (px, py) in enumerate(stroke.pts) if tb.contains(px, py)]
            if len(idxs) < MIN_HITS:
                continue
            # DOCK vs THROUGH. An arrow that POINTS AT a label ends inside it — its interior samples run to
            # a stroke endpoint (a node arrowhead docking at its title, by design). A genuine smear PASSES
            # THROUGH: the stroke has samples OUTSIDE the label on both sides of the interior run. Require
            # entered-and-exited so docking arrows (the pilot's dominant false-positive class over box-less
            # node labels) drop while a feedback edge crossing a free label's core stays flagged.
            entered = idxs[0] >= 1
            exited = idxs[-1] <= n - 2
            if entered and exited:
                frac = len(idxs) / max(n, 1)
                findings.append(Finding(path.name, tb.text, stroke.kind, len(idxs), round(frac, 2)))
    return findings


def _in_scope(name: str) -> bool:
    return not name.startswith(EXCLUDE_PREFIXES)


def findings() -> list[Finding]:
    out: list[Finding] = []
    for svg in sorted(ASSETS.glob("*.svg")):
        if _in_scope(svg.name):
            try:
                out.extend(analyze(svg))
            except ET.ParseError:
                continue
    return out


def summary_line(fs: list[Finding]) -> str:
    figs = len({f.svg for f in fs})
    return f"{len(fs)} stroke-through-label collision(s) across {figs} figure(s)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="specific .svg files (default: all book/assets/*.svg in scope)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding (the blocking flip)")
    args = ap.parse_args(argv)
    if args.paths:
        fs: list[Finding] = []
        for p in args.paths:
            try:
                fs.extend(analyze(pathlib.Path(p)))
            except ET.ParseError as e:
                print(f"  [ERROR] {p}: {e}")
    else:
        fs = findings()
    mode = "STRICT (exit 1 on any finding)" if args.strict else "AUDIT-ONLY (prints, exits 0)"
    print(f"== figure-label-collision — stroke-through-free-label sensor over book/assets/*.svg [{mode}] ==")
    print(f"  excluded: {', '.join(EXCLUDE_PREFIXES)}* · gate: free-floating label + non-faint stroke + "
          f">={MIN_HITS} interior samples")
    if not fs:
        print("  clean — no connector stroke runs through a free-floating label")
        return 0
    print(f"  {summary_line(fs)}:")
    by: dict[str, list[Finding]] = {}
    for f in fs:
        by.setdefault(f.svg, []).append(f)
    for svg in sorted(by):
        print(f"    {svg}:")
        for f in sorted(by[svg], key=lambda x: -x.samples):
            label = f.label if len(f.label) <= 44 else f.label[:41] + "..."
            print(f"      {f.stroke_kind:8s} through '{label}'  ({f.samples} samples, frac={f.frac})")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
