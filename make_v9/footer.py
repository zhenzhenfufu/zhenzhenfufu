"""v9 footer: the torn bottom edge of the washi journal page lying on the icon-wallpaper margin.
Pen-ink 上海 -> San Diego flight route with pale skylines at each end (option 3), a dashed arc with a
paper plane framing a handwritten "thanks for stopping by" + umbrella doodle, washi tape bits, and the
robot-cat waving under its clear umbrella near the right. Writes assets/v9/footer.svg (1600x220)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "ft-"
W, H = 1600, 220
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

PX0, PX1 = 34, W - 34      # paper sides, same as the header page
EDGE_Y = 160               # mean y of the torn bottom edge
GROUND = 114               # skyline ground line on the paper
SKY_COL = B2               # pale lavender silhouettes
SKY_COL2 = B3
TXT = "thanks for stopping by"
TXT_SIZE = 31
TXT_W = 384                # measured: Hiragino Sans W6 @31px
TXT_Y = 104
MX, MY, MS = 1450, 140, 0.7   # mascot head centre + scale


# ------------------------------------------------------------------ torn paper
def torn_points(seed=7):
    """Irregular torn edge from right to left (so it closes the paper path)."""
    rnd = random.Random(seed)
    pts, x = [], PX1
    while x > PX0:
        y = EDGE_Y + 4 * math.sin(x / 97) + 3 * math.sin(x / 41 + 1) + rnd.uniform(-3.2, 3.2)
        pts.append((x, y))
        x -= rnd.uniform(9, 19)
    pts.append((PX0, EDGE_Y + 2))
    return pts


def edge_y_at(pts, x):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x2 <= x <= x1:
            t = (x1 - x) / (x1 - x2)
            return y1 + t * (y2 - y1)
    return EDGE_Y


def page(pts):
    edge = " ".join(f"L{x:.1f} {y:.1f}" for x, y in pts)
    d = f"M{PX0} -40 H{PX1} {edge} Z"
    fibres = "M" + " L".join(f"{x:.1f} {y - 1.6:.1f}" for x, y in pts)
    o = [margin_bg(W, H, UID),
         f'<clipPath id="{UID}pg"><path d="{d}"/></clipPath>',
         f'<path d="{d}" fill="{CREAM}" filter="url(#{UID}sh)"/>',
         f'<path d="{d}" fill="url(#{UID}grid)"/>',
         # white paper fibres along the tear
         pen(fibres, 3.2, WHITE, ' opacity=".95"'),
         # journal margin rule + punched holes, continuing the header page
         f'<g clip-path="url(#{UID}pg)"><line x1="92" y1="0" x2="92" y2="{H}" stroke="{PINK}" stroke-width="2.4" opacity=".7"/></g>']
    for y in (34, 92):
        o.append(f'<circle cx="62" cy="{y}" r="9" fill="#ddd6f6"/>'
                 f'<path d="M54 {y-4} a9 9 0 0 1 16 0" fill="none" stroke="#c4bbe8" stroke-width="2"/>')
    return "\n".join(o)


# ------------------------------------------------------------------ route: skylines + dashed arc (option 3)
def shanghai(x0, b):
    """Pale Shanghai-ish block silhouette with a generic two-sphere tower; spans x0..x0+232."""
    def X(v):
        return x0 + v
    d = (f"M{X(0)} {b} V{b-30} H{X(24)} V{b-46} H{X(44)} V{b-36} H{X(62)} V{b-60} L{X(71)} {b-71} L{X(80)} {b-60} "
         f"V{b-40} H{X(100)} V{b-52} H{X(118)} V{b-26} H{X(140)} V{b-42} H{X(160)} V{b-22} H{X(232)} V{b}Z")
    tx = X(196)
    o = [f'<path d="{d}" fill="{SKY_COL}"/>',
         f'<g fill="{SKY_COL2}"><rect x="{tx-3}" y="{b-82}" width="6" height="82"/>'
         f'<path d="M{tx-13} {b} L{tx-3} {b-38} H{tx+3} L{tx+13} {b}Z"/>'
         f'<rect x="{tx-1.2}" y="{b-96}" width="2.4" height="16"/></g>',
         f'<circle cx="{tx}" cy="{b-60}" r="10" fill="{PINK}" stroke="{SKY_COL2}" stroke-width="2.5"/>',
         f'<circle cx="{tx}" cy="{b-33}" r="6.5" fill="{PINK}" stroke="{SKY_COL2}" stroke-width="2.5"/>']
    # a few lit windows
    for wx, wy in [(8, 22), (8, 14), (30, 36), (30, 26), (68, 48), (68, 38), (106, 42), (106, 32), (146, 32)]:
        o.append(f'<rect x="{X(wx)}" y="{b-wy}" width="5" height="5" rx="1" fill="{WIN}"/>')
    o.append(pen(f"M{x0-10} {b} H{x0+246}", 2.6, PEN))
    return "".join(o)


def san_diego(x0, b):
    """Pale San Diego low-rise + three palms + a wave; spans x0..x0+246."""
    def X(v):
        return x0 + v
    d = (f"M{X(10)} {b} V{b-24} H{X(38)} V{b-40} H{X(62)} V{b-28} H{X(90)} V{b-48} H{X(110)} V{b-26} H{X(138)} "
         f"V{b-36} H{X(162)} V{b-20} H{X(200)} V{b}Z")
    o = [f'<path d="{d}" fill="{SKY_COL}"/>']
    for wx, wy in [(18, 16), (46, 30), (46, 20), (96, 38), (96, 28), (96, 18), (146, 26)]:
        o.append(f'<rect x="{X(wx)}" y="{b-wy}" width="5" height="5" rx="1" fill="{WIN}"/>')
    for px, ph, lean in [(X(2), 66, -5), (X(196), 76, 6), (X(224), 54, -3)]:
        tx_, ty_ = px + lean, b - ph
        fr = "".join(
            f'<path d="M{tx_} {ty_} Q{tx_ + 12*math.cos(math.radians(a)):.1f} {ty_-8} '
            f'{tx_ + 22*math.cos(math.radians(a)):.1f} {ty_ + 9 + 22*math.sin(math.radians(a))*0.4:.1f}"/>'
            for a in (-165, -125, -55, -15))
        o.append(f'<g stroke="{SKY_COL2}" stroke-width="4" fill="none" stroke-linecap="round">'
                 f'<path d="M{px} {b} Q{px + lean*0.3:.1f} {b - ph*0.5:.1f} {tx_} {ty_}"/>{fr}</g>')
    o.append(pen(f"M{x0-8} {b} H{x0+250}", 2.6, PEN))
    return "".join(o)


def route():
    sh_x, sd_x = 124, 1056
    o = [shanghai(sh_x, GROUND), san_diego(sd_x, GROUND),
         text(sh_x + 116, GROUND + 28, "上海", 21, PEN_D, 700, "middle", 3),
         text(sd_x + 118, GROUND + 28, "San Diego", 21, PEN_D, 700, "middle", 1)]
    a0, a1, cy = (sh_x + 252, 70), (sd_x - 26, 70), -10
    (x0, y0), (x1, y1) = a0, a1
    mid = (x0 + x1) / 2
    o.append(pen(f"M{x0} {y0} Q{mid} {cy} {x1} {y1}", 2.6, PEN, ' stroke-dasharray="3 10"'))
    o.append(f'<path d="{sparkle_d(x0, y0, 8)}" fill="{PINK_D}"/>')
    o.append(f'<circle cx="{x1}" cy="{y1}" r="5.5" fill="{PINK_D}"/>')
    peak = 0.5 * y0 + 0.5 * cy
    o.append(doodle_plane(mid, peak, 1.0, 0))
    return "\n".join(o)


# ------------------------------------------------------------------ handwritten thanks + umbrella doodle
def umbrella_doodle(x, y, s=1.0):
    """Tiny ink umbrella (stands in for ☂), (x,y) = canopy top centre."""
    canopy = (f"M{x-17*s:.1f} {y+14*s:.1f} C{x-16*s:.1f} {y+2*s:.1f} {x-8*s:.1f} {y:.1f} {x:.1f} {y:.1f} "
              f"C{x+8*s:.1f} {y:.1f} {x+16*s:.1f} {y+2*s:.1f} {x+17*s:.1f} {y+14*s:.1f} "
              f"Q{x+11.5*s:.1f} {y+10*s:.1f} {x+5.7*s:.1f} {y+14*s:.1f} Q{x:.1f} {y+10*s:.1f} {x-5.7*s:.1f} {y+14*s:.1f} "
              f"Q{x-11.5*s:.1f} {y+10*s:.1f} {x-17*s:.1f} {y+14*s:.1f}Z")
    return (f'<g><path d="{canopy}" fill="{BLUE}" fill-opacity=".7" stroke="{PEN_D}" stroke-width="{2.4*s:.1f}" stroke-linejoin="round"/>'
            + pen(f"M{x:.1f} {y+13*s:.1f} V{y+30*s:.1f} q0 {5*s:.1f} {-5*s:.1f} {5*s:.1f} q{-4*s:.1f} 0 {-4*s:.1f} {-4*s:.1f}", 2.4 * s, PEN_D)
            + f'<circle cx="{x:.1f}" cy="{y-2*s:.1f}" r="{2.4*s:.1f}" fill="{PINK_D}"/></g>')


def thanks():
    total = TXT_W + 30 + 34
    tx = 800 - total / 2
    o = [f'<g transform="translate({tx:.1f} {TXT_Y}) skewX(-8) rotate(-1.5)">',
         f'<text x="0" y="0" class="f" font-size="{TXT_SIZE}" font-weight="600" fill="{PEN_D}" letter-spacing="0.5">{esc(TXT)}</text>',
         pen(f"M4 14 q{TXT_W*0.12:.0f} 6 {TXT_W*0.25:.0f} 0 t{TXT_W*0.25:.0f} 0 t{TXT_W*0.25:.0f} 0 t{TXT_W*0.2:.0f} -1", 3, PINK),
         '</g>',
         umbrella_doodle(tx + TXT_W + 30 + 17, TXT_Y - 30, 1.0)]
    return "\n".join(o)


# ------------------------------------------------------------------ mascot waving under the umbrella
WAVE_STYLE = """<style>
  .wave{transform-box:fill-box;transform-origin:100% 100%;animation:wave 1.4s ease-in-out infinite alternate}
  @keyframes wave{from{transform:rotate(-14deg)}to{transform:rotate(12deg)}}
  @media (prefers-reduced-motion: reduce){.wave{animation:none}}
</style>"""


def mascot_waving(x, y, s):
    hand = (f'<g transform="translate({n(x)} {n(y)}) scale({n(s)})"><g class="wave">'
            f'<path d="M-74 -30 q-8 8 -6 20 M-86 -36 q-12 14 -8 30" fill="none" stroke="{PEN}" stroke-width="3.4" '
            f'stroke-linecap="round" opacity=".85"/>'
            f'<circle cx="-60" cy="-18" r="8.5" fill="{WHITE}" stroke="{INK}" stroke-width="4"/></g></g>')
    return f'<g class="bob">{mascot(x, y, s, umbrella=True, bob=False)}{hand}</g>'


def accents(pts):
    clip_rain = f'<clipPath id="{UID}rc"><rect x="1330" y="0" width="236" height="{H}"/></clipPath>'
    return "\n".join([
        # washi tape bits: raindrop tape across the tear at left, sakura tape on the right side edge
        tape(118, edge_y_at(pts, 118) - 2, 122, 32, -22, UID, "rain"),
        tape(1000, edge_y_at(pts, 1000) - 1, 104, 30, 16, UID, "sakura"),
        # puddle + mascot (stands on the margin in front of the torn page)
        puddle(MX + 6, MY + 58 * MS + 4, 0.36),
        clip_rain,
        f'<g clip-path="url(#{UID}rc)">{rain(1330, 0, 236, 200, 14, 5, 1.0, .38, (16, 28), BLUE_D)}</g>',
        mascot_waving(MX, MY, MS),
        # sakura petals + a couple of small sparkles
        petal(522, 122, 25, .85, .85),
        petal(1286, 150, -30, .8, .8),
        petal(214, 186, 40, .75, .7),
        petal(930, 194, -15, .7, .65),
        sparkle(1010, 30, 7, GOLD, .95, "tw"),
        sparkle(452, 30, 6, BLUE_D, .55, "tw2"),
    ])


def svg():
    pts = torn_points()
    title = "thanks for stopping by ☂"
    desc = ("Footer: the torn bottom edge of a dotted journal page on a lavender icon wallpaper. "
            "A dashed flight route with a paper plane links small Shanghai (上海) and San Diego skylines, "
            "framing the handwritten words 'thanks for stopping by' and a tiny umbrella; "
            "the small cat-eared robot waves from under a clear umbrella in the rain.")
    body = "\n".join([WAVE_STYLE, page(pts), route(), thanks(), accents(pts)])
    return svg_doc(W, H, UID, title, desc, body, k=1.0, rx=24)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "footer.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


if __name__ == "__main__":
    print("\n".join(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)))
