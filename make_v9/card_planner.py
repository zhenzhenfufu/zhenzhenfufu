"""v9 project card: UCSD Course Planner, pure illustration.
A journal planner page with three quarter columns (FALL / WINTER / SPRING), blank course blocks joined by thin
prerequisite links. One FALL block breaks a prerequisite (pink X); a curved arrow moves it to SPRING, where it
gets a check and a 検証済 seal. The robot-cat proposes with a pencil, standing in a little rainy-alley corner.
Writes assets/v9/card-planner.svg (1600x900)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "cp-"
W, H = 1600, 900
K = 2.0
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

# planner geometry
COL_X = (112, 432, 752)      # column left edges
COL_W = 280
BW, BH = 236, 100            # course block
ROW_Y = (226, 374, 522)      # block tops
PANEL_Y0, PANEL_Y1 = 190, 656
GOLD_L = "#fdeccc"


def bx(c):
    return COL_X[c] + (COL_W - BW) / 2


def anchor(c, r, side, dy=0):
    """Point on a block edge: side in 'l', 'r', 't', 'b' (dy shifts l/r points)."""
    x, y = bx(c), ROW_Y[r]
    return {"l": (x, y + BH / 2 + dy), "r": (x + BW, y + BH / 2 + dy),
            "t": (x + BW / 2, y), "b": (x + BW / 2, y + BH)}[side]


# ------------------------------------------------------------------ local helpers
def season_icon(kind, x, y):
    if kind == "fall":     # gold leaf with vein
        return (f'<g transform="translate({x} {y}) rotate(-35)">'
                f'<path d="M0,-20 C14,-12 15,8 0,20 C-15,8 -14,-12 0,-20Z" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="3" stroke-linejoin="round"/>'
                f'<path d="M0,-14 V27 M0,-2 l7,-6 M0,8 l-7,-6" stroke="{GOLD_D}" stroke-width="2.6" fill="none" stroke-linecap="round"/></g>')
    if kind == "winter":   # snowflake
        arms = "".join(f'<g transform="rotate({a})"><path d="M0,0 V-19 M0,-11 l-6,-6 M0,-11 l6,-6"/></g>' for a in range(0, 360, 60))
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{BLUE_D}" stroke-width="3.4" '
                f'stroke-linecap="round" stroke-linejoin="round">{arms}</g>')
    return blossom(x, y, 1.45)


def column(c, label, kind):
    x = COL_X[c]
    cx = x + COL_W / 2
    tw = len(label) * 25.5 + 46          # rough tracked-caps width incl. icon gap
    ix = cx - tw / 2 + 12
    return "".join([
        f'<rect x="{x}" y="{PANEL_Y0}" width="{COL_W}" height="{PANEL_Y1 - PANEL_Y0}" rx="26" fill="{WHITE}" fill-opacity=".55" '
        f'stroke="{LAV}" stroke-width="3" stroke-dasharray="2 11" stroke-linecap="round"/>',
        season_icon(kind, ix, 140),
        text(ix + 34, 153, label, 36, INK, 800, ls=6),
        pen(f"M{cx - 54} 172 q18 7 36 0 t36 0 t36 0", 3.4, PINK),
    ])


def dotted_lines(x, y, w, col=PEN, n_=2):
    o = []
    for i in range(n_):
        ww = w if i == 0 else w * 0.62
        o.append(pen(f"M{x:.1f} {y + i*24:.1f} H{x + ww:.1f}", 4.6, col, ' stroke-dasharray="0.1 12" opacity=".75"'))
    return "".join(o)


def block(c, r, fill, tab, ghost=False, extra=""):
    x, y = bx(c), ROW_Y[r]
    if ghost:
        return (f'<g opacity=".9"><rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="20" fill="{PINK_L}" fill-opacity=".7" '
                f'stroke="{PINK_D}" stroke-width="3.6" stroke-dasharray="12 10" stroke-linecap="round"/>'
                + dotted_lines(x + 40, y + 40, 150, PINK) + extra + '</g>')
    return ("<g>"
            f'<rect x="{x + 7}" y="{y + 7}" width="{BW}" height="{BH}" rx="20" fill="{LAV_L}"/>'
            f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="20" fill="{fill}" stroke="{PEN_D}" stroke-width="4"/>'
            f'<circle cx="{x + 30}" cy="{y + BH/2}" r="9" fill="{tab}" stroke="{PEN_D}" stroke-width="3"/>'
            + dotted_lines(x + 56, y + 40, 140) + extra + "</g>")


def arrow_head(x, y, ang, col, size=16, w=4.4):
    """Open chevron arrowhead at (x,y) pointing in direction ang (deg)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})">'
            + pen(f"M{-size} {-size*0.7:.1f} L0 0 L{-size} {size*0.7:.1f}", w, col) + '</g>')


def link(a, b, col=PEN_D, dash=None, w=4.0, head=True):
    """Thin prerequisite link: S-curve from a to b (horizontal tangents) with dot at start, chevron at end."""
    (x1, y1), (x2, y2) = a, b
    mx = (x1 + x2) / 2
    d = f"M{x1:.1f} {y1:.1f} C{mx:.1f} {y1:.1f} {mx:.1f} {y2:.1f} {x2:.1f} {y2:.1f}"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    ang = 0 if x2 > x1 else 180
    return (pen(d, w, col, da) + f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="6" fill="{CREAM}" stroke="{col}" stroke-width="3"/>'
            + (arrow_head(x2 - (3 if ang == 0 else -3), y2, ang, col, 11, w) if head else ""))


def pencil_mascot(x, y, scale):
    """Robot-cat holding a pencil in its left hand, tip pointing down-left at the planner."""
    pen_g = (f'<g transform="translate(-64 26) rotate(-20)"><g transform="translate(-30 0)">'
             f'<path d="M-30,-8 H34 V8 H-30Z" fill="{GOLD}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M-30,-8 H34 V-2 H-30Z" fill="#ffe2a6"/>'
             f'<path d="M-30,-8 H34 V8 H-30Z" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M34,-8 H44 V8 H34Z" fill="{LAV}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M44,-8 H50 Q56,-8 56,0 Q56,8 50,8 H44Z" fill="{PINK}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M-30,-8 L-54,0 L-30,8Z" fill="#ffe9cf" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M-44,-3.4 L-54,0 L-44,3.4Z" fill="{INK}"/></g></g>'
             f'<circle cx="-64" cy="26" r="8.5" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>')
    return (f'<g transform="translate({x} {y}) scale({scale})"><g class="bob">'
            f'{mascot(0, 0, 1, bob=False)}{pen_g}</g></g>')


# ------------------------------------------------------------------ scene
def body():
    o = [card_frame(W, H, UID, K)]

    # --- columns
    for c, (lab, kind) in enumerate([("FALL", "fall"), ("WINTER", "winter"), ("SPRING", "spring")]):
        o.append(column(c, lab, kind))

    # --- prerequisite links (behind blocks)
    o.append(link(anchor(0, 0, "r"), anchor(1, 0, "l")))
    o.append(link(anchor(0, 1, "r", -18), anchor(1, 1, "l", -18)))
    o.append(link(anchor(1, 0, "r"), anchor(2, 0, "l")))
    o.append(link(anchor(1, 1, "r"), anchor(2, 2, "l"), BLUE_D, w=4.4))
    # the broken one: FALL block needs a WINTER course first (backward link, pink dashed)
    o.append(link(anchor(1, 1, "l", 26), anchor(0, 2, "r"), PINK_D, dash="2 11", w=5))

    # --- blocks
    o.append(block(0, 0, BLUE_L, BLUE))
    o.append(block(0, 1, LAV_L, LAV))
    xg, yg = bx(0), ROW_Y[2]
    xmark = pen(f"M{xg + BW - 62} {yg + 22} l40 48 M{xg + BW - 22} {yg + 22} l-40 48", 9, PINK_D)
    o.append(block(0, 2, None, None, ghost=True, extra=xmark))
    o.append(block(1, 0, GOLD_L, GOLD))
    o.append(block(1, 1, BLUE_L, BLUE))
    o.append(block(1, 2, LAV_L, LAV))
    o.append(block(2, 0, LAV_L, LAV))
    o.append(block(2, 1, GOLD_L, GOLD))
    xs, ys = bx(2), ROW_Y[2]
    check = pen(f"M{xs + BW - 66} {ys + 46} l16 18 l32 -36", 9, PINK_D)
    o.append(block(2, 2, PINK_L, PINK, extra=check))

    # --- the move: swooping arrow under WINTER, from the X block to its SPRING slot
    (ax, ay), (bx_, by) = anchor(0, 2, "b"), anchor(2, 2, "b")
    d = f"M{ax:.1f} {ay + 10:.1f} C{ax + 40:.1f} {ay + 210:.1f} {bx_ - 40:.1f} {by + 210:.1f} {bx_:.1f} {by + 18:.1f}"
    o.append(pen(d, 12, CREAM))
    o.append(pen(d, 5, BLUE_D, ' stroke-dasharray="14 12"'))
    o.append(arrow_head(bx_, by + 14, -90, BLUE_D, 22, 6))
    o.append(sparkle(ax + 320, ay + 160, 15, GOLD, 1, "tw"))

    # --- 検証済 seal on the moved block
    o.append(hanko(bx(2) + BW + 86, ROW_Y[2] + BH + 82, 60, -12))

    # --- right side: little rainy-alley corner with the mascot
    o.append(f'<clipPath id="{UID}rc"><rect x="1088" y="96" width="456" height="590"/></clipPath>')
    o.append(f'<g clip-path="url(#{UID}rc)">{rain(1080, 96, 470, 580, 24, 7, 2.0, .42, (16, 30), LAV)}</g>')
    w0, wc, w1 = (1104, 104), (1290, 170), (1530, 112)

    def wire_y(xq):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            t = (lo + hi) / 2
            if (1-t)**2*w0[0] + 2*(1-t)*t*wc[0] + t*t*w1[0] < xq:
                lo = t
            else:
                hi = t
        return (1-t)**2*w0[1] + 2*(1-t)*t*wc[1] + t*t*w1[1]
    o.append(pen(f"M{w0[0]} {w0[1]} Q{wc[0]} {wc[1]} {w1[0]} {w1[1]}", 3.4, EDGE))
    o.append(lantern(1206, wire_y(1206) - 2, UID, 1.4))
    sgs = 1.55
    sw, sh_ = vsign_size("雨宿り", 28, 11)
    sx = 1440
    hook = wire_y(sx + sw * sgs / 2)
    o.append(vsign(sx, hook + 14 * sgs - 2, "雨宿り", sgs, INK, LAV))
    o.append(puddle(1296, 612, 0.95))
    o.append(pencil_mascot(1300, 482, 1.95))

    # --- sparse sprinkles
    o.append(star(1262, 760, 15, GOLD, PEN_D, 2.4, cls="tw2"))
    o.append(sparkle(404, 112, 13, PEN, .9))
    o.append(sparkle(1458, 760, 16, GOLD, 1, "tw"))
    o.append(petal(1050, 152, 25, 1.4))
    o.append(petal(120, 760, -30, 1.3, .8))
    o.append(petal(1500, 470, 60, 1.2, .8))
    return "\n".join(o)


def svg():
    title = "Course planner illustration"
    desc = ("Journal planner page with three quarter columns labelled FALL, WINTER and SPRING holding blank course "
            "blocks joined by prerequisite links. A FALL block marked with a pink X is moved by a curved arrow to "
            "SPRING, where it gets a check and a 検証済 seal. The robot-cat mascot holds a pencil beside it.")
    return svg_doc(W, H, UID, title, desc, body(), k=K)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "card-planner.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


def main():
    for p in build():
        print(p)


if __name__ == "__main__":
    main()
