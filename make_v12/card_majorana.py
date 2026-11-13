"""Card: "Signal or Background?" - anime underground physics lab / aquarium observation room.

    build(out_dir) -> path      writes card-majorana.svg into out_dir
    build_svg()    -> str       the standalone 1600x900 SVG
    python3 card_majorana.py [out_dir]   (default: ../assets/v12)

A glowing germanium-crystal string in a frosted cryostat (left), a big curved holographic panel
with a faint stack of lavender waveforms and one bold waveform whose sharp rise is picked out in
gold (centre/right), "signal" (ticked) / "background" tabs, and official chibi Furina (a Genshin Impact
"Paimon's Paintings" emoji, (c) HoYoverse, embedded from art/ by art.py) gasping at the find.
Behind: a panoramic aquarium window full of periwinkle water and light rays.

The scene is drawn from scratch; the only raster is the embedded official chibi emoji.
Python 3 stdlib only.  No script / image / foreignObject / external refs.  No hue 70-192.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True     # never leave __pycache__ in the repo
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import art as ART  # noqa: E402

W, H, RX = 1600, 900, 28
U = "mj"                      # uid prefix for every id / class in this card
INK = "#3f3780"
INK2 = "#5b4f9e"
WHITE = "#ffffff"
GOLD, GOLD_SH, GOLD_HI, GOLD_D = "#ffd27a", "#f0ad57", "#fff3c8", "#d98c3e"
PINK, PINK_SH = "#f8bfd6", "#e897bd"
FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"

# holographic panel (local coords 0..PW x 0..PH, warped to look curved)
PX, PY, PW, PH, SAG = 646, 64, 812, 452, 13
# plot area inside the panel (local)
PL0, PL1 = 44, PW - 44
LYB, LYP = 0.815 * PH, 0.31 * PH     # baseline / full-amplitude local y
UR, RW = 0.30, 0.026                 # bold waveform: rise start (fraction of plot) and rise width


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def P(pts):
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)


def lg(gid, x1, y1, x2, y2, stops, units=True):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(st + (None,))[:3] for st in stops])
    gu = ' gradientUnits="userSpaceOnUse"' if units else ""
    return f'<linearGradient id="{gid}"{gu} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(gid, cx, cy, r, stops, units=True):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(st + (None,))[:3] for st in stops])
    gu = ' gradientUnits="userSpaceOnUse"' if units else ""
    return f'<radialGradient id="{gid}"{gu} cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def sparkle(cx, cy, r, fill=WHITE, op=1.0, cls=""):
    k = r * 0.2
    c = f' class="{cls}"' if cls else ""
    o = f' opacity="{op}"' if op < 1 else ""
    return (f'<path{c}{o} fill="{fill}" d="M{f(cx)},{f(cy - r)} Q{f(cx + k)},{f(cy - k)} {f(cx + r)},{f(cy)} '
            f'Q{f(cx + k)},{f(cy + k)} {f(cx)},{f(cy + r)} Q{f(cx - k)},{f(cy + k)} {f(cx - r)},{f(cy)} '
            f'Q{f(cx - k)},{f(cy - k)} {f(cx)},{f(cy - r)}Z"/>')


def ell(cx, cy, rx, ry):
    return (f"M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 "
            f"a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0Z")


# ------------------------------------------------------------------ panel warp
def wp(lx, ly):
    u = lx / PW
    return PX + lx, PY + ly + SAG * (1 - (2 * u - 1) ** 2) * (1 - 2 * ly / PH)


def wpath(pts, close=False):
    return P([wp(x, y) for x, y in pts]) + ("Z" if close else "")


def rrect_local(x0, y0, x1, y1, r, step=24):
    pts = []

    def edge(a, b):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for i in range(n):
            t = i / n
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))

    def arc(cx, cy, a0):
        for i in range(7):
            a = math.radians(a0 + 90 * i / 6)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    arc(x0 + r, y0 + r, 180)
    edge((x0 + r, y0), (x1 - r, y0))
    arc(x1 - r, y0 + r, 270)
    edge((x1, y0 + r), (x1, y1 - r))
    arc(x1 - r, y1 - r, 0)
    edge((x1 - r, y1), (x0 + r, y1))
    arc(x0 + r, y1 - r, 90)
    edge((x0, y1 - r), (x0, y0 + r))
    return pts


def ux(u):
    return PL0 + (PL1 - PL0) * u


def vy(v):
    return LYB - (LYB - LYP) * v


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def wave_v(u, ur, rw, amp, tau, steps=((1.0, 0.0),)):
    """Germanium-detector style charge pulse: flat baseline, sharp rise, slow exponential tail.
    steps = [(fraction, extra delay)] -> multi-step rise (multi-site 'background')."""
    v = 0.0
    for frac, dly in steps:
        a = ur + dly
        if u > a:
            v += frac * smooth((u - a) / rw)
    tail = math.exp(-max(0.0, u - ur - rw) / tau)
    return amp * v * tail


def wave_pts(ur, rw, amp, tau, steps=((1.0, 0.0),), noise=0.0, seed=1, n=70, u0=0.0, u1=1.0):
    rnd = random.Random(seed)
    us = set(u0 + (u1 - u0) * i / n for i in range(n + 1))
    for frac, dly in steps:
        for i in range(13):
            us.add(ur + dly - rw * 0.2 + rw * 1.4 * i / 12)
    us = sorted(u for u in us if u0 <= u <= u1)
    out = []
    for u in us:
        v = wave_v(u, ur, rw, amp, tau, steps) + (rnd.uniform(-noise, noise) if noise else 0)
        out.append((ux(u), vy(v)))
    return out


# ------------------------------------------------------------------ defs / style
def defs():
    d = []
    d.append(f'<clipPath id="{U}-card"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>')
    # window panes (union clip)
    d.append(f'<clipPath id="{U}-pane">' + "".join(
        f'<path d="M{x0},{y1} V{y0 + 46} Q{x0},{y0} {x0 + 46},{y0} H{x1 - 46} Q{x1},{y0} {x1},{y0 + 46} V{y1} Z"/>'
        for x0, x1, y0, y1 in PANES) + "</clipPath>")
    d.append(lg(f"{U}-water", 0, 30, 0, 630, [(0, "#f8e9fa"), (.1, "#dcdcff"), (.26, "#b9c3fb"), (.55, "#a0a8f0"),
                                               (.82, "#a59be6"), (1, "#b7a6e6")]))
    d.append(lg(f"{U}-ray", 0, 30, 0, 640, [(0, WHITE, .75), (.6, WHITE, .22), (1, WHITE, 0)]))
    d.append(lg(f"{U}-wall", 0, 0, 0, 640, [(0, "#b4a8ea"), (1, "#c8bcf2")]))
    d.append(lg(f"{U}-floor", 0, 640, 0, 900, [(0, "#dccff8"), (.35, "#ccbcf1"), (1, "#bca6e6")]))
    d.append(lg(f"{U}-mull", 0, 0, 1, 0, [(0, "#e9e3ff"), (.35, "#cbc0f4"), (.7, "#a99ce2"), (1, "#8f82d2")], units=False))
    d.append(lg(f"{U}-metal", 0, 0, 1, 0, [(0, "#a79ce6"), (.18, "#d9d1fb"), (.32, "#b7abef"),
                                          (.7, "#8d80d6"), (1, "#7568c2")], units=False))
    d.append(lg(f"{U}-cop", 0, 0, 1, 0, [(0, "#f3c7ae"), (.2, "#ffe6d6"), (.36, "#f6cdb6"),
                                        (.72, "#e3a596"), (1, "#c98a8a")], units=False))
    d.append(lg(f"{U}-xtal", 0, 0, 1, 0, [(0, "#c3b2ff"), (.22, "#f1dcff"), (.5, "#ffc7e6"),
                                         (.78, "#c2c9ff"), (1, "#a9b1f6")], units=False))
    d.append(lg(f"{U}-glass", 0, 0, 1, 0, [(0, "#eef0ff", .4), (.2, "#ffffff", .08), (.7, "#dfe2ff", .04),
                                          (1, "#c1c4f6", .38)], units=False))
    d.append(rg(f"{U}-xglow", 262, 430, 210, [(0, "#fff4fb", .95), (.35, "#ffd6ef", .55), (.7, "#d9c9ff", .2),
                                              (1, "#d9c9ff", 0)]))
    d.append(rg(f"{U}-pool", .5, .5, .5, [(0, "#fff3fb", .85), (.5, "#f1c9ef", .35), (1, "#e0c4f4", 0)], units=False))
    d.append(rg(f"{U}-soft", .5, .5, .5, [(0, WHITE, .9), (.6, WHITE, .35), (1, WHITE, 0)], units=False))
    d.append(rg(f"{U}-back", .5, .5, .5, [(0, "#fff6ea", .7), (.35, "#ffe6f0", .42), (.7, "#ffe2ec", .12), (1, "#ffe2ec", 0)], units=False))
    d.append(rg(f"{U}-bokeh", .5, .5, .5, [(0, "#ffffff", .05), (.75, "#f3eaff", .25), (.95, "#ffffff", .7), (1, "#ffffff", 0)], units=False))
    d.append(rg(f"{U}-gsoft", .5, .5, .5, [(0, "#fff1c4", .95), (.45, "#ffd27a", .45), (1, "#ffd27a", 0)], units=False))
    d.append(lg(f"{U}-panel", 0, PY, 0, PY + PH, [(0, "#fbf8ff", .82), (.5, "#f1ebff", .7), (1, "#e6ddff", .68)]))
    d.append(lg(f"{U}-pedge", PX, 0, PX + PW, 0, [(0, WHITE), (.5, "#d8ccff"), (1, WHITE)]))
    d.append(lg(f"{U}-beam", 0, PY + PH, 0, DTOP, [(0, "#f3eaff", .05), (1, "#fff7ff", .55)]))
    d.append(lg(f"{U}-band", 0, PY + LYP - 30, 0, PY + LYB + 20, [(0, "#ffe7a6", .05), (.5, "#ffd98f", .42),
                                                                  (1, "#ffe7a6", .05)]))
    d.append(lg(f"{U}-desk", 0, DTOP + 10, 0, DTOP + 92, [(0, "#cdbdf2"), (1, "#a593dc")]))
    d.append(lg(f"{U}-desktop", 0, 0, 1, 0, [(0, "#f6f2ff"), (.55, "#ece6ff"), (1, "#d9d0fb")], units=False))
    d.append(lg(f"{U}-tab", 0, 0, 0, 1, [(0, "#fff0bf"), (.55, "#ffd986"), (1, "#f7c463")], units=False))
    d.append(lg(f"{U}-mist", 0, 0, 0, 1, [(0, WHITE, 0), (.5, WHITE, .75), (1, "#efe9ff", .2)], units=False))
    d.append(f'<filter id="{U}-blur" x="-20%" y="-20%" width="140%" height="140%">'
             f'<feGaussianBlur stdDeviation="6"/></filter>')
    d.append(f'<filter id="{U}-blur3" x="-50%" y="-50%" width="200%" height="200%">'
             f'<feGaussianBlur stdDeviation="9"/></filter>')
    d.append(f'<filter id="{U}-blur2" x="-30%" y="-30%" width="160%" height="160%">'
             f'<feGaussianBlur stdDeviation="2.4"/></filter>')
    return "<defs>" + "".join(d) + "</defs>"


def style():
    c = U
    return ("<style>"
            f"@keyframes {c}-ray{{0%,100%{{opacity:1}}50%{{opacity:.72}}}}"
            f"@keyframes {c}-up{{0%{{transform:translateY(0);opacity:0}}12%{{opacity:.9}}85%{{opacity:.8}}"
            f"100%{{transform:translateY(-300px);opacity:0}}}}"
            f"@keyframes {c}-pulse{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}"
            f"@keyframes {c}-tw{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(.45);opacity:.35}}}}"
            f"@keyframes {c}-bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}"
            f"@keyframes {c}-scan{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}80%{{opacity:1}}"
            f"100%{{transform:translateX(700px);opacity:0}}}}"
            f".{c}-ray{{animation:{c}-ray 7s ease-in-out infinite}}"
            f".{c}-ray2{{animation:{c}-ray 9s ease-in-out -2.5s infinite}}"
            f".{c}-up{{animation:{c}-up 9s linear infinite}}"
            f".{c}-up2{{animation:{c}-up 12s linear -4s infinite}}"
            f".{c}-up3{{animation:{c}-up 10s linear -7s infinite}}"
            f".{c}-glow{{animation:{c}-pulse 3.4s ease-in-out infinite}}"
            f".{c}-gold{{animation:{c}-pulse 2.2s ease-in-out infinite}}"
            f".{c}-tw,.{c}-tw2,.{c}-tw3{{transform-box:fill-box;transform-origin:50% 50%}}"
            f".{c}-tw{{animation:{c}-tw 2.6s ease-in-out infinite}}"
            f".{c}-tw2{{animation:{c}-tw 3.3s ease-in-out -1.1s infinite}}"
            f".{c}-tw3{{animation:{c}-tw 2.9s ease-in-out -1.9s infinite}}"
            f".{c}-bob{{animation:{c}-bob 6s ease-in-out infinite}}"
            f".{c}-bob2{{animation:{c}-bob 7.5s ease-in-out -2s infinite}}"
            f".{c}-scan{{animation:{c}-scan 6.5s ease-in-out infinite}}"
            f"@media (prefers-reduced-motion: reduce){{.{c}-ray,.{c}-ray2,.{c}-up,.{c}-up2,.{c}-up3,.{c}-glow,"
            f".{c}-gold,.{c}-tw,.{c}-tw2,.{c}-tw3,.{c}-bob,.{c}-bob2,.{c}-scan{{animation:none}}}}"
            "</style>")


# ------------------------------------------------------------------ room: window + water
PANES = [(-20, 524, 22, 628), (548, 1056, 22, 628), (1080, 1620, 22, 628)]


def jelly(x, y, s, cls):
    """Distant pastel jellyfish (soft, low contrast)."""
    bell = f"M{-30},0 C-30,-26 -14,-36 0,-36 C14,-36 30,-26 30,0 C20,-4 10,4 0,0 C-10,4 -20,-4 -30,0Z"
    tent = "".join(f'<path d="M{dx},-1 C{dx + 6},14 {dx - 6},30 {dx + 3},{44 + abs(dx) * .2}" fill="none" '
                   f'stroke="#f2c6e4" stroke-width="2.4" stroke-linecap="round" opacity=".75"/>'
                   for dx in (-18, -6, 6, 18))
    return (f'<g class="{cls}"><g transform="translate({x},{y}) scale({s})" opacity=".8">{tent}'
            f'<path d="{bell}" fill="#f6cfea"/>'
            f'<path d="M8,-35 C22,-31 30,-20 30,0 C24,-2 20,-2 16,-1 C20,-14 16,-26 8,-35Z" fill="#e2a9d6" opacity=".7"/>'
            f'<path d="M-22,-14 C-20,-24 -12,-30 -4,-31" fill="none" stroke="{WHITE}" stroke-width="3.2" '
            f'stroke-linecap="round" opacity=".9"/>'
            f'<path d="{bell}" fill="none" stroke="#c48fcd" stroke-width="1.6" opacity=".7"/></g></g>')


def rocks(rnd):
    """Pastel seabed ridge with cel-lit boulders and pink coral fans."""
    o = []
    # far ridge
    far = [(-20, 560)]
    for x in range(-20, 1640, 60):
        far.append((x, 520 + 22 * math.sin(x * .011) + 12 * math.sin(x * .031 + 1)))
    far += [(1620, 640), (-20, 640)]
    o.append(f'<path d="{P(far)}Z" fill="#b6b2ee" opacity=".75"/>')
    # boulders
    for cx, cy, r in ((70, 590, 70), (180, 610, 52), (380, 600, 64), (470, 615, 40), (640, 605, 58),
                      (760, 616, 44), (980, 600, 66), (1150, 612, 50), (1300, 596, 74), (1450, 612, 54),
                      (1560, 600, 62)):
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{f(r * .62)}" fill="#a59de4"/>')
        o.append(f'<path d="M{f(cx - r * .86)},{f(cy - r * .3)} C{f(cx - r * .6)},{f(cy - r * .62)} '
                 f'{f(cx + r * .1)},{f(cy - r * .7)} {f(cx + r * .55)},{f(cy - r * .46)} '
                 f'C{f(cx + r * .1)},{f(cy - r * .5)} {f(cx - r * .5)},{f(cy - r * .42)} {f(cx - r * .86)},{f(cy - r * .3)}Z" '
                 f'fill="#cdc8f6"/>')
    # coral fans (pink / lilac branching strokes)
    for bx, by, h, col in ((300, 560, 64, "#eeb0d6"), (520, 585, 44, "#d9b2f0"), (870, 570, 58, "#eeb0d6"),
                           (1240, 552, 70, "#f0bcd9"), (1500, 566, 52, "#d9b2f0")):
        br = []
        for k in range(5):
            a = math.radians(-90 + (k - 2) * 22)
            ex, ey = bx + math.cos(a) * h, by + math.sin(a) * h
            mx, my = bx + math.cos(a) * h * .45, by + math.sin(a) * h * .45
            br.append(f"M{bx},{by} Q{f(mx - (k - 2) * 3)},{f(my)} {f(ex)},{f(ey)}")
            a2 = a + (.5 if k >= 2 else -.5)
            br.append(f"M{f(mx)},{f(my)} l{f(math.cos(a2) * h * .35)},{f(math.sin(a2) * h * .35)}")
        o.append(f'<path d="{" ".join(br)}" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" opacity=".85"/>')
    return "".join(o)


def window(rnd):
    o = [f'<rect width="{W}" height="660" fill="url(#{U}-wall)"/>']
    g = [f'<rect x="-20" y="0" width="1660" height="660" fill="url(#{U}-water)"/>']
    # caustic web near the surface
    cau = []
    for row in range(3):
        y0 = 40 + row * 34
        pts = []
        for x in range(-20, 1640, 36):
            pts.append((x, y0 + 9 * math.sin(x * .05 + row * 1.7) + 5 * math.sin(x * .13 + row)))
        cau.append(P(pts))
    g.append(f'<path d="{" ".join(cau)}" fill="none" stroke="{WHITE}" stroke-width="2.4" opacity=".35"/>')
    # light rays slanting from the upper left
    for i, (x0, w0, op, cls) in enumerate(((60, 70, .55, "ray"), (250, 40, .4, "ray2"), (430, 110, .5, "ray"),
                                          (700, 60, .42, "ray2"), (930, 120, .45, "ray"), (1200, 50, .4, "ray2"),
                                          (1380, 90, .5, "ray"))):
        g.append(f'<g class="{U}-{cls}"><path d="M{x0},20 L{x0 + w0},20 L{x0 + w0 + 300},640 L{x0 + 180},640Z" '
                 f'fill="url(#{U}-ray)" opacity="{op}"/></g>')
    g.append(jelly(470, 150, .9, f"{U}-bob"))
    g.append(jelly(1475, 130, .7, f"{U}-bob2"))
    g.append(rocks(rnd))
    # drifting plankton sparkles + rising bubbles
    for i in range(26):
        x, y = rnd.uniform(0, 1600), rnd.uniform(60, 520)
        g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rnd.uniform(1.2, 2.6))}" fill="{WHITE}" opacity="{f(rnd.uniform(.35, .8))}"/>')
    for i, (x, y, r) in enumerate(((520, 600, 7), (536, 640, 4), (1070, 610, 6), (1092, 650, 3.5),
                                   (90, 640, 5), (1590, 630, 6))):
        g.append(f'<g class="{U}-up{"" if i % 3 == 0 else i % 3 + 1}">'
                 f'<circle cx="{x}" cy="{y}" r="{r}" fill="{WHITE}" fill-opacity=".18" stroke="{WHITE}" stroke-width="1.6" opacity=".85"/>'
                 f'<path d="M{f(x - r * .55)},{f(y - r * .1)} A{f(r * .6)},{f(r * .6)} 0 0,1 {f(x - r * .1)},{f(y - r * .55)}" '
                 f'fill="none" stroke="{WHITE}" stroke-width="1.6" stroke-linecap="round"/></g>')
    o.append(f'<g clip-path="url(#{U}-pane)">{"".join(g)}'
             # glass reflections (anime diagonal sheen)
             f'<path d="M80,22 L190,22 L-20,330 L-20,190Z" fill="{WHITE}" opacity=".22"/>'
             f'<path d="M230,22 L262,22 L40,360 L8,360Z" fill="{WHITE}" opacity=".18"/>'
             f'<path d="M700,22 L790,22 L560,380 L548,380 L548,260Z" fill="{WHITE}" opacity=".16"/>'
             f'<path d="M1250,22 L1330,22 L1100,380 L1080,380 L1080,290Z" fill="{WHITE}" opacity=".18"/>'
             f'<path d="M1370,22 L1392,22 L1160,380 L1138,380Z" fill="{WHITE}" opacity=".14"/>'
             "</g>")
    # pane frames: inner rim light + ink line
    for x0, x1, y0, y1 in PANES:
        d = f"M{x0},{y1} V{y0 + 46} Q{x0},{y0} {x0 + 46},{y0} H{x1 - 46} Q{x1},{y0} {x1},{y0 + 46} V{y1}"
        o.append(f'<path d="{d}" fill="none" stroke="#e9e3ff" stroke-width="9"/>'
                 f'<path d="{d}" fill="none" stroke="{INK2}" stroke-width="2.6" opacity=".75"/>')
    # top beam
    o.append(f'<path d="M0,0 H1600 V14 C1200,20 400,20 0,14Z" fill="#9f92dc"/>'
             f'<path d="M0,14 C400,20 1200,20 1600,14" fill="none" stroke="#e9e3ff" stroke-width="2.4"/>')
    # mullions: cel-shaded struts with gold collars
    for x0, x1 in ((524, 548), (1056, 1080)):
        o.append(f'<rect x="{x0 - 3}" y="0" width="{x1 - x0 + 6}" height="640" fill="url(#{U}-mull)"/>'
                 f'<rect x="{x1 - 3}" y="0" width="3" height="640" fill="#7e71c4"/>'
                 f'<path d="M{x0 - 3},0 V640 M{x1 + 3},0 V640" stroke="{INK2}" stroke-width="2" opacity=".8"/>')
        for yy in (120, 590):
            o.append(f'<rect x="{x0 - 7}" y="{yy}" width="{x1 - x0 + 14}" height="14" rx="4" fill="{GOLD}" '
                     f'stroke="{INK2}" stroke-width="1.8"/>'
                     f'<rect x="{x0 - 4}" y="{yy + 2.5}" width="{(x1 - x0) * .5}" height="3" rx="1.5" fill="{GOLD_HI}"/>')
    # cozy string lights draped under the top beam
    wires, bulbs = [], []
    for x0, x1, sag in ((-10, 390, 34), (390, 800, 40), (800, 1210, 36), (1210, 1610, 40)):
        wires.append(f"M{x0},18 Q{(x0 + x1) / 2},{18 + sag * 2} {x1},18")
        for k in range(1, 7):
            t = k / 7
            bx = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * (x0 + x1) / 2 + t * t * x1
            by = 18 + 2 * t * (1 - t) * sag * 2
            col = (GOLD, "#ffc2dc", GOLD_HI)[k % 3]
            bulbs.append((bx, by + 6, col, k % 2))
    o.append(f'<path d="{" ".join(wires)}" fill="none" stroke="{INK2}" stroke-width="2" opacity=".8"/>')
    for i, (bx, by, col, alt) in enumerate(bulbs):
        o.append(f'<g class="{U}-{"glow" if alt else "gold"}"><circle cx="{f(bx)}" cy="{f(by)}" r="20" fill="url(#{U}-gsoft)" opacity=".85"/></g>'
                 f'<path d="M{f(bx - 2.5)},{f(by - 7)} h5 v3 h-5Z" fill="{INK2}"/>'
                 f'<ellipse cx="{f(bx)}" cy="{f(by + 1)}" rx="5.6" ry="7" fill="{col}" stroke="{GOLD_D}" stroke-width="1"/>'
                 f'<circle cx="{f(bx - 1.4)}" cy="{f(by - 1.6)}" r="1.5" fill="{WHITE}"/>')
    # sill
    o.append(f'<path d="M0,622 H1600 V652 H0Z" fill="#cfc4f4"/>'
             f'<path d="M0,622 H1600" stroke="{WHITE}" stroke-width="3"/>'
             f'<path d="M0,638 H1600 V652 H0Z" fill="#ab9fe2"/>'
             f'<path d="M0,652 H1600" stroke="{INK2}" stroke-width="2" opacity=".7"/>')
    return "".join(o)


def floor(rnd):
    o = [f'<rect x="0" y="652" width="{W}" height="{H - 652}" fill="url(#{U}-floor)"/>']
    # perspective tiles
    vx, vy0 = 800, 380
    lines = []
    for x in range(-2000, 3700, 190):
        t = (900 - vy0) / (652 - vy0)
        lines.append(f"M{f(vx + (x - vx) * 1)},652 L{f(vx + (x - vx) * t)},900")
    for y in (668, 694, 730, 780, 850):
        lines.append(f"M0,{y} H1600")
    o.append(f'<path d="{" ".join(lines)}" stroke="#a698e0" stroke-width="1.6" opacity=".45" fill="none"/>')
    # window reflection slices on the polished floor
    for x0, x1, _, _ in PANES:
        for k, (dy, hh, op) in enumerate(((656, 22, .45), (684, 12, .3), (704, 7, .2))):
            o.append(f'<rect x="{max(0, x0 + 30)}" y="{dy}" width="{min(1600, x1 - 30) - max(0, x0 + 30)}" '
                     f'height="{hh}" fill="#eef0ff" opacity="{op}"/>')
    # soft light pools from the window
    for x, y, rx_, ry_ in ((560, 870, 150, 16), (1480, 866, 120, 14), (980, 884, 200, 12)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx_}" ry="{ry_}" fill="url(#{U}-soft)" opacity=".55"/>')
    return "".join(o)


# ------------------------------------------------------------------ cryostat
CX = 262


def cyl(cx, top, bot, rx, ry, fill, shade, ink=INK, sw=2.6, hl=WHITE, hl_op=.75, shade_k=.42, cap=None):
    """Cel-shaded vertical cylinder: body + hard shadow on the right + highlight band + top ellipse."""
    body = f"M{f(cx - rx)},{f(top)} V{f(bot)} A{f(rx)},{f(ry)} 0 0,0 {f(cx + rx)},{f(bot)} V{f(top)}Z"
    k = shade_k
    sy = ry * math.sqrt(1 - k * k)
    sh = (f"M{f(cx + rx * k)},{f(top)} V{f(bot + sy)} A{f(rx)},{f(ry)} 0 0,0 {f(cx + rx)},{f(bot)} V{f(top)}Z")
    hb = f"M{f(cx - rx * .7)},{f(top)} h{f(rx * .16)} V{f(bot + ry * .66)} l{f(-rx * .16)},{f(-ry * .06)}Z"
    o = [f'<path d="{body}" fill="{ink}" transform="translate(1.6,2.2)"/>',
         f'<path d="{body}" fill="{fill}"/>', f'<path d="{sh}" fill="{shade}"/>',
         f'<path d="{hb}" fill="{hl}" opacity="{hl_op}"/>',
         f'<path d="{body}" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>']
    if cap:
        o.append(f'<path d="{ell(cx, top, rx, ry)}" fill="{cap}" stroke="{ink}" stroke-width="{sw}"/>')
    return "".join(o)


def crystal(cx, cy, rx, ry, h):
    """One glowing germanium crystal: octagonal prism with cel-toned facets, bright top face."""
    top, bot = cy - h / 2, cy + h / 2
    ang = [math.radians(-22.5 + 45 * k) for k in range(8)]
    vt = [(cx + rx * math.cos(a), top + ry * math.sin(a)) for a in ang]
    front = [0, 1, 2, 3, 4, 5]                  # front-half vertices, right to left
    tones = ["#8f86ea", "#b4b0ff", "#ffa6d6", "#ffe6f7", "#d6bfff"]
    o = [f'<g class="{U}-glow"><ellipse cx="{f(cx)}" cy="{f(cy + 2)}" rx="{f(rx * 1.55)}" ry="{f(h * 1.0)}" fill="#ff9fd2" '
         f'opacity=".9" filter="url(#{U}-blur3)"/></g>']
    sil = [vt[i % 8] for i in front] + [(x, y + h) for x, y in (vt[i % 8] for i in reversed(front))]
    o.append(f'<path d="{P(sil)}Z" fill="#5a4cae" transform="translate(1.4,2)"/>')
    for k in range(5):
        a, b = vt[front[k] % 8], vt[front[k + 1] % 8]
        q = [a, b, (b[0], b[1] + h), (a[0], a[1] + h)]
        o.append(f'<path d="{P(q)}Z" fill="{tones[k]}"/>')
    # glow seam + highlight stripe on the brightest facet
    a, b = vt[3], vt[4]
    o.append(f'<path d="M{f(a[0] * .7 + b[0] * .3)},{f(a[1] + 8)} V{f(a[1] + h - 8)}" stroke="{WHITE}" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<path d="M{f(cx - rx * .55)},{f(cy + h * .18)} Q{f(cx)},{f(cy + h * .3)} {f(cx + rx * .55)},{f(cy + h * .18)}" '
             f'fill="none" stroke="#fff4fb" stroke-width="3" stroke-linecap="round" opacity=".7"/>')
    edges = " ".join(f"M{f(vt[i % 8][0])},{f(vt[i % 8][1])} v{h}" for i in front[1:-1])
    o.append(f'<path d="{edges}" stroke="#8a7fdc" stroke-width="1.3" opacity=".8"/>')
    o.append(f'<path d="{P(sil)}Z" fill="none" stroke="#5a4cae" stroke-width="2.2" stroke-linejoin="round"/>')
    rimp = [vt[i % 8] for i in front]
    o.append(f'<path d="{P(rimp)}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linejoin="round" opacity=".9"/>')
    # top face
    o.append(f'<path d="{P(vt)}Z" fill="#fff0fa" stroke="#5a4cae" stroke-width="2" stroke-linejoin="round"/>')
    inner = [(cx + (x - cx) * .62, top + (y - top) * .62) for x, y in vt]
    o.append(f'<path d="{P(inner)}Z" fill="#f9d2ec"/>')
    o.append(f'<path d="M{f(cx - rx * .5)},{f(top - ry * .25)} L{f(cx + rx * .1)},{f(top - ry * .62)}" stroke="{WHITE}" '
             f'stroke-width="3.2" stroke-linecap="round"/>')
    return "".join(o)


def cryostat(rnd):
    o = []
    cx = CX
    gt, gb, grx, gry = 270, 606, 104, 20      # glass bell top / bottom
    # big glow behind the glass + soft light spokes
    o.append(f'<g class="{U}-glow"><ellipse cx="{cx}" cy="440" rx="250" ry="280" fill="url(#{U}-xglow)"/>')
    sp = []
    for k in range(10):
        a = math.radians(-160 + k * 36)
        r0, r1 = 120, 250 + (k % 3) * 30
        w = .06
        sp.append(f"M{f(cx + math.cos(a - w) * r0)},{f(440 + math.sin(a - w) * r0)} "
                  f"L{f(cx + math.cos(a) * r1)},{f(440 + math.sin(a) * r1)} "
                  f"L{f(cx + math.cos(a + w) * r0)},{f(440 + math.sin(a + w) * r0)}Z")
    o.append(f'<path d="{" ".join(sp)}" fill="#fff1fa" opacity=".45"/></g>')
    # pipe to the ceiling
    o.append(f'<rect x="{cx - 26}" y="0" width="52" height="214" fill="url(#{U}-metal)"/>'
             f'<rect x="{cx + 12}" y="0" width="14" height="214" fill="#6e62bd" opacity=".55"/>'
             f'<path d="M{cx - 26},0 V214 M{cx + 26},0 V214" stroke="{INK}" stroke-width="2.6"/>')
    for yy in (52, 140):
        o.append(f'<rect x="{cx - 33}" y="{yy}" width="66" height="16" rx="5" fill="{GOLD}" stroke="{INK}" stroke-width="2.2"/>'
                 f'<rect x="{cx + 10}" y="{yy + 2}" width="20" height="12" rx="3" fill="{GOLD_SH}"/>'
                 f'<rect x="{cx - 28}" y="{yy + 3}" width="24" height="4" rx="2" fill="{GOLD_HI}"/>')
    # side feed line
    feed = f"M{cx + 60},214 C{cx + 66},150 {cx + 96},120 {cx + 100},0"
    o.append(f'<path d="{feed}" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round"/>'
             f'<path d="{feed}" fill="none" stroke="#b9aef0" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="{feed}" fill="none" stroke="#ece7ff" stroke-width="2.2" stroke-linecap="round" transform="translate(-2,0)"/>')
    # base pedestal (drawn first; the bell sits on it)
    o.append(cyl(cx, 600, 772, 124, 24, f"url(#{U}-metal)", "#7468c0", hl_op=.55))
    o.append(f'<path d="{ell(cx, 600, 124, 24)}" fill="#d4ccf8" stroke="{INK}" stroke-width="2.6"/>'
             f'<path d="M{cx - 124},738 A124,24 0 0,0 {cx + 124},738" fill="none" stroke="{GOLD}" stroke-width="6"/>'
             f'<path d="M{cx - 124},738 A124,24 0 0,0 {cx + 124},738" fill="none" stroke="{INK}" stroke-width="1.6" opacity=".55"/>')
    for lx, col in ((-58, "#ffb3d4"), (-30, GOLD), (-2, "#c9d2ff")):
        o.append(f'<rect x="{cx + lx}" y="668" width="20" height="10" rx="5" fill="{col}" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{cx + lx + 4}" y="670" width="7" height="3" rx="1.5" fill="{WHITE}"/>')
    o.append(f'<path d="M{cx - 70},700 H{cx + 30}" stroke="{INK2}" stroke-width="2" opacity=".5"/>')
    # gold seat ring under the bell
    o.append(f'<path d="{ell(cx, gb, grx + 9, gry + 3)}" fill="{GOLD}" stroke="{INK}" stroke-width="2.4"/>'
             f'<path d="M{cx + 30},{gb + 19} A{grx + 9},{gry + 3} 0 0,0 {cx + grx + 9},{gb}" fill="none" stroke="{GOLD_SH}" stroke-width="4"/>')
    # glass bell (back half)
    o.append(f'<path d="M{cx - grx},{gt} V{gb} A{grx},{gry} 0 0,0 {cx + grx},{gb} V{gt}Z" fill="#a597e2" opacity=".72"/>')
    o.append(f'<path d="{ell(cx, gb, grx, gry)}" fill="#e7dcff" opacity=".8"/>')
    # support rods + crystal string
    rods = f"M{cx - 72},{gt + 10} V{gb + 4} M{cx + 72},{gt + 10} V{gb + 4}"
    o.append(f'<path d="{rods}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
             f'<path d="{rods}" stroke="#f3c7ae" stroke-width="3.6" stroke-linecap="round"/>')
    for cy in (350, 442, 534):
        o.append(f'<path d="M{cx - 74},{cy + 34} H{cx + 74}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M{cx - 74},{cy + 34} H{cx + 74}" stroke="#ffd9bf" stroke-width="3.6" stroke-linecap="round"/>')
        o.append(crystal(cx, cy, 60, 13, 54))
    # glass front: tint, reflections
    o.append(f'<path d="M{cx - grx},{gt} V{gb} A{grx},{gry} 0 0,0 {cx + grx},{gb} V{gt}Z" fill="url(#{U}-glass)"/>')
    o.append(f'<path d="M{cx - 84},{gt + 30} V{gb - 4}" stroke="{WHITE}" stroke-width="12" stroke-linecap="round" opacity=".55"/>'
             f'<path d="M{cx - 62},{gt + 40} V{gt + 150}" stroke="{WHITE}" stroke-width="4" stroke-linecap="round" opacity=".75"/>'
             f'<path d="M{cx + 92},{gt + 40} V{gb - 16}" stroke="#f7dcff" stroke-width="4" stroke-linecap="round" opacity=".8"/>')
    # frost: scalloped white band under the cap with icicle drips, haze at the bottom
    fr = [(cx - grx, gt)]
    n = 12
    for i in range(n + 1):
        x = cx - grx + 2 * grx * i / n
        base = gt + 14 + gry * .5 * math.sqrt(max(0, 1 - ((x - cx) / grx) ** 2))
        fr.append((x, base + rnd.uniform(0, 5)))
        if i < n:
            xm = x + grx / n
            fr.append((xm, base + rnd.uniform(8, 13)))
    fr.append((cx + grx, gt))
    o.append(f'<path d="{P(fr)}Z" fill="{WHITE}" opacity=".78"/>')
    drips = []
    for x, L in ((cx - 70, 16), (cx - 34, 24), (cx + 8, 12), (cx + 46, 20), (cx + 80, 13)):
        yb = gt + 22 + gry * .5 * math.sqrt(max(0, 1 - ((x - cx) / grx) ** 2))
        drips.append(f"M{f(x - 3.5)},{f(yb)} L{f(x)},{f(yb + L)} L{f(x + 3.5)},{f(yb)}Z")
    o.append(f'<path d="{" ".join(drips)}" fill="{WHITE}" opacity=".85"/>')
    o.append(f'<path d="M{cx - grx},{gb - 30} V{gb} A{grx},{gry} 0 0,0 {cx + grx},{gb} V{gb - 30} '
             f'A{grx},{gry} 0 0,1 {cx - grx},{gb - 30}Z" fill="url(#{U}-mist)" opacity=".8"/>')
    o.append(f'<path d="M{cx - grx},{gt} V{gb} A{grx},{gry} 0 0,0 {cx + grx},{gb} V{gt}" fill="none" stroke="{INK}" stroke-width="2.8"/>')
    # head (copper cap)
    o.append(cyl(cx, 214, 264, 120, 22, f"url(#{U}-cop)", "#d9998e", cap="#ffe3d2", hl_op=.8))
    o.append(f'<path d="{ell(cx, 214, 82, 13)}" fill="#f6cdb6" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{cx - 70},210 A82,13 0 0,1 {cx + 10},201" fill="none" stroke="{WHITE}" stroke-width="3" stroke-linecap="round"/>')
    # pipe flange seated on the cap
    o.append(f'<path d="{ell(cx, 212, 44, 9)}" fill="{GOLD}" stroke="{INK}" stroke-width="2.2"/>'
             f'<path d="M{cx + 6},220.6 A44,9 0 0,0 {cx + 44},212" fill="none" stroke="{GOLD_SH}" stroke-width="3"/>')
    o.append(cyl(cx, 160, 208, 26, 5, f"url(#{U}-metal)", "#6e62bd", sw=2.4, hl_op=.6))
    o.append(f'<path d="M{cx - 120},250 A120,22 0 0,0 {cx + 120},250" fill="none" stroke="{GOLD}" stroke-width="5"/>'
             f'<path d="M{cx - 120},250 A120,22 0 0,0 {cx + 120},250" fill="none" stroke="{INK}" stroke-width="1.6" opacity=".6"/>')
    for k in range(9):
        a = math.pi * (k + .5) / 9
        bx, by = cx - math.cos(a) * 108, 260 + math.sin(a) * 18
        o.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="3.2" fill="{GOLD_HI}" stroke="{INK}" stroke-width="1.3"/>')
    # frost crust on the cap rim
    o.append(f'<path d="M{cx - 120},214 Q{cx - 100},206 {cx - 80},212 Q{cx - 60},204 {cx - 40},210" fill="none" '
             f'stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity=".85"/>')
    # cold mist hugging the floor
    for mx, my, mw, mh, op in ((cx - 150, 772, 150, 28, .85), (cx + 40, 786, 190, 24, .8), (cx - 40, 800, 230, 20, .65),
                               (cx + 170, 806, 130, 16, .55)):
        o.append(f'<ellipse cx="{mx}" cy="{my}" rx="{mw / 2}" ry="{mh / 2}" fill="url(#{U}-soft)" opacity="{op}"/>')
    o.append(f'<path d="M{cx - 190},780 C{cx - 150},760 {cx - 110},790 {cx - 60},770 C{cx - 20},756 {cx + 20},786 {cx + 70},772 '
             f'C{cx + 110},760 {cx + 150},784 {cx + 200},774" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    # frost sparkles
    for (sx, sy, r, cls) in ((cx - 128, 300, 12, "tw"), (cx + 130, 380, 9, "tw2"), (cx - 122, 520, 8, "tw3"),
                             (cx + 120, 560, 13, "tw"), (cx + 74, 196, 8, "tw2"), (cx - 168, 724, 9, "tw3")):
        o.append(sparkle(sx, sy, r, WHITE, 1, f"{U}-{cls}"))
    for (sx, sy) in ((cx - 40, 300), (cx + 30, 312), (cx - 88, 410), (cx + 86, 470), (cx + 40, 588), (cx - 30, 592)):
        o.append(f'<circle cx="{sx}" cy="{sy}" r="2.2" fill="{WHITE}"/>')
    return "".join(o)


def cables():
    d1 = f"M{CX + 118},742 C{CX + 190},770 {CX + 200},822 {CX + 290},826 C{CX + 360},830 {CX + 380},800 676,792"
    d2 = f"M{CX + 112},754 C{CX + 170},800 {CX + 210},852 {CX + 320},852 C{CX + 400},852 {CX + 420},818 686,812"
    o = []
    for d, col in ((d2, "#8a7ed4"), (d1, "#b0a4ec")):
        o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round"/>'
                 f'<path d="{d}" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="{d}" fill="none" stroke="#efeaff" stroke-width="2" stroke-linecap="round" '
                 f'transform="translate(-1,-2.4)" opacity=".85"/>')
    return "".join(o)


# ------------------------------------------------------------------ desk console
DX0, DX1, DTOP = 636, 1436, 746
EM0, EM1 = 930, 1360


def desk():
    o = []
    mid = (DX0 + DX1) / 2
    fb = DTOP + 92
    o.append(f'<ellipse cx="{mid}" cy="{fb + 8}" rx="430" ry="20" fill="#8a7cd0" opacity=".3"/>')
    front = (f"M{DX0},{DTOP + 14} Q{mid},{DTOP + 2} {DX1},{DTOP + 14} V{fb - 20} "
             f"Q{DX1},{fb} {DX1 - 20},{fb} H{DX0 + 20} Q{DX0},{fb} {DX0},{fb - 20}Z")
    o.append(f'<path d="{front}" fill="{INK}" transform="translate(2,3)"/>'
             f'<path d="{front}" fill="url(#{U}-desk)"/>')
    o.append(f'<clipPath id="{U}-dclip"><path d="{front}"/></clipPath><g clip-path="url(#{U}-dclip)">'
             f'<path d="M{DX1 - 200},{DTOP} L{DX1 - 236},{fb + 4} H{DX1 + 10} V{DTOP}Z" fill="#8c7ed0" opacity=".8"/>'
             f'<path d="M{DX0},{fb - 16} H{DX1}" stroke="#8c7ed0" stroke-width="12" opacity=".5"/>'
             f'<path d="M{DX0 + 16},{DTOP + 22} V{fb - 14}" stroke="{WHITE}" stroke-width="6" stroke-linecap="round" opacity=".55"/>'
             '</g>')
    # one long inset strip with soft lights + sliders (no text)
    o.append(f'<rect x="{DX0 + 60}" y="{DTOP + 34}" width="{DX1 - DX0 - 120}" height="36" rx="18" fill="#ab9fe6" stroke="{INK2}" stroke-width="2"/>'
             f'<rect x="{DX0 + 72}" y="{DTOP + 37}" width="{DX1 - DX0 - 144}" height="7" rx="3.5" fill="#d3caf8" opacity=".75"/>')
    for k, col in enumerate(("#ffb3d4", GOLD, "#d3dbff")):
        x = DX0 + 90 + k * 44
        o.append(f'<rect x="{x}" y="{DTOP + 45}" width="32" height="14" rx="7" fill="{col}" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{x + 5}" y="{DTOP + 47.5}" width="11" height="3.5" rx="1.7" fill="{WHITE}"/>')
    for k, col in enumerate((GOLD, "#d3dbff", "#ffb3d4")):
        x = DX1 - 220 + k * 44
        o.append(f'<rect x="{x}" y="{DTOP + 45}" width="32" height="14" rx="7" fill="{col}" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{x + 5}" y="{DTOP + 47.5}" width="11" height="3.5" rx="1.7" fill="{WHITE}"/>')
    for k in range(2):
        y = DTOP + 46 + k * 12
        o.append(f'<path d="M{mid - 150},{y} H{mid + 150}" stroke="#8e81d0" stroke-width="4" stroke-linecap="round"/>'
                 f'<rect x="{mid - 90 + k * 110}" y="{y - 5}" width="18" height="10" rx="4" fill="#fff6fb" stroke="{INK}" stroke-width="1.5"/>')
    o.append(f'<path d="{front}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>')
    top = (f"M{DX0 - 8},{DTOP + 14} Q{mid},{DTOP + 2} {DX1 + 8},{DTOP + 14} L{DX1 - 10},{DTOP - 6} "
           f"Q{mid},{DTOP - 18} {DX0 + 10},{DTOP - 6}Z")
    o.append(f'<path d="{top}" fill="url(#{U}-desktop)" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
    o.append(f'<path d="M{DX0 - 8},{DTOP + 14} Q{mid},{DTOP + 2} {DX1 + 8},{DTOP + 14}" fill="none" stroke="{GOLD}" stroke-width="4.5"/>'
             f'<path d="M{DX0 - 8},{DTOP + 14} Q{mid},{DTOP + 2} {DX1 + 8},{DTOP + 14}" fill="none" stroke="{INK}" stroke-width="1.4" opacity=".6"/>')
    o.append(f'<path d="M{EM0},{DTOP - 2} Q{mid},{DTOP - 12} {EM1},{DTOP - 2}" fill="none" stroke="#c7b9f6" stroke-width="9" stroke-linecap="round"/>'
             f'<path d="M{EM0},{DTOP - 2} Q{mid},{DTOP - 12} {EM1},{DTOP - 2}" fill="none" stroke="{WHITE}" stroke-width="4" stroke-linecap="round" class="{U}-glow"/>')
    return "".join(o)


def beam():
    """Soft projection light from the desk slot up to the bottom of the panel."""
    bl, br = wp(70, PH), wp(PW - 70, PH)
    return (f'<path d="M{EM0},{DTOP - 4} L{f(bl[0])},{f(bl[1])} L{f(br[0])},{f(br[1])} L{EM1},{DTOP - 4}Z" '
            f'fill="url(#{U}-beam)" opacity=".8"/>')


# ------------------------------------------------------------------ holographic panel
def panel():
    o = []
    outline = rrect_local(0, 0, PW, PH, 30)
    # back glow
    o.append(f'<path d="{wpath(rrect_local(-16, -16, PW + 16, PH + 16, 40), True)}" fill="{WHITE}" opacity=".35" filter="url(#{U}-blur)"/>')
    o.append(f'<path d="{wpath(outline, True)}" fill="url(#{U}-panel)"/>')
    # grid
    gl = []
    for i in range(11):
        x = ux(i / 10)
        gl.append(wpath([(x, 104), (x, LYB + 26)]))
    for v in (-0.06, .25, .5, .75, 1.0):
        y = vy(v)
        gl.append(wpath([(PL0 + (PL1 - PL0) * k / 12, y) for k in range(13)]))
    o.append(f'<path d="{" ".join(gl)}" fill="none" stroke="#cbbff4" stroke-width="1.4" opacity=".75"/>')
    # header rule + decorative UI bars (no text)
    o.append(f'<path d="{wpath([(24 + k * (PW - 48) / 16, 92) for k in range(17)])}" fill="none" stroke="#b3a5ec" stroke-width="2"/>')
    # gold highlight band behind the rise
    bx0, bx1 = ux(UR - .03), ux(UR + RW + .03)
    band = [(bx0, LYP - 34), (bx1, LYP - 34), (bx1, LYB + 18), (bx0, LYB + 18)]
    dense = []
    for (ax, ay), (bxx, byy) in zip(band, band[1:] + band[:1]):
        for k in range(6):
            t = k / 6
            dense.append((ax + (bxx - ax) * t, ay + (byy - ay) * t))
    o.append(f'<path d="{wpath(dense, True)}" fill="url(#{U}-band)"/>')
    # faint stack of many waveforms
    rnd = random.Random(7)
    cols = ["#a796ec", "#e4a4d6", "#9ba8f0", "#bb98e8"]
    stack = []
    for i in range(20):
        ur = UR + rnd.uniform(-.045, .08)
        rw = rnd.uniform(.02, .075)
        amp = rnd.uniform(.84, 1.0) if i % 5 else rnd.uniform(.5, .72)
        tau = rnd.uniform(1.8, 4.6)
        steps = ((1.0, 0.0),) if i % 3 else ((.5, 0.0), (.5, rnd.uniform(.035, .08)))
        pts = wave_pts(ur, rw, amp, tau, steps, noise=.004, seed=i + 3, n=40)
        stack.append((cols[i % 4], wpath(pts)))
    for col in cols:
        ds = " ".join(d for c, d in stack if c == col)
        o.append(f'<path d="{ds}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round" opacity=".8"/>')
    # bold waveform
    bold = wpath(wave_pts(UR, RW, 1.0, 3.2, noise=.0035, seed=99, n=80))
    o.append(f'<path d="{bold}" fill="none" stroke="{WHITE}" stroke-width="15" stroke-linejoin="round" stroke-linecap="round" opacity=".85"/>'
             f'<path d="{bold}" fill="none" stroke="{INK}" stroke-width="6.5" stroke-linejoin="round" stroke-linecap="round"/>')
    # gold rise highlight with glow
    rise = wpath(wave_pts(UR, RW, 1.0, 3.2, n=2, u0=UR - .006, u1=UR + RW + .004))
    o.append(f'<g class="{U}-gold"><path d="{rise}" fill="none" stroke="{GOLD}" stroke-width="26" stroke-linecap="round" '
             f'opacity=".75" filter="url(#{U}-blur)"/></g>'
             f'<path d="{rise}" fill="none" stroke="{GOLD_D}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="{rise}" fill="none" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="{rise}" fill="none" stroke="{GOLD_HI}" stroke-width="2.6" stroke-linecap="round" transform="translate(-1.5,0)"/>')
    tx, ty = wp(ux(UR + RW), vy(.99))
    bx_, by_ = wp(ux(UR), vy(0))
    o.append(sparkle(tx + 12, ty - 20, 16, GOLD_HI, 1, f"{U}-tw") + sparkle(tx + 34, ty - 2, 7, WHITE, 1, f"{U}-tw2")
             + sparkle(bx_ - 18, by_ + 18, 9, GOLD, 1, f"{U}-tw3"))
    # scan sweep (animated)
    sx0, sy0 = wp(PL0, 104)
    sx1, sy1 = wp(PL0, LYB + 26)
    o.append(f'<g class="{U}-scan"><rect x="{f(sx0)}" y="{f(sy0 + 6)}" width="10" height="{f(sy1 - sy0 - 6)}" rx="5" '
             f'fill="#ffffff" opacity=".45"/></g>')
    # tabs: "signal" (ticked, active) and "background"
    o.append(tabs())
    # glass sheen + frame
    sh1 = [(130, 0), (230, 0), (60, PH), (-40, PH)]
    o.append(f'<clipPath id="{U}-pclip"><path d="{wpath(outline, True)}"/></clipPath>'
             f'<g clip-path="url(#{U}-pclip)">'
             f'<path d="{wpath(sh1, True)}" fill="{WHITE}" opacity=".22"/>'
             f'<path d="{wpath([(260, 0), (290, 0), (120, PH), (90, PH)], True)}" fill="{WHITE}" opacity=".2"/>'
             f'<path d="{wpath([(PW - 120, 0), (PW - 70, 0), (PW - 260, PH), (PW - 310, PH)], True)}" fill="{WHITE}" opacity=".12"/>'
             "</g>")
    o.append(f'<path d="{wpath(outline, True)}" fill="none" stroke="{INK2}" stroke-width="5" opacity=".5"/>'
             f'<path d="{wpath(outline, True)}" fill="none" stroke="url(#{U}-pedge)" stroke-width="3"/>'
             f'<path d="{wpath(rrect_local(10, 10, PW - 10, PH - 10, 22), True)}" fill="none" stroke="#c2b4f4" stroke-width="1.4"/>')
    # gold corner brackets
    br = []
    for (x, y, dx, dy) in ((14, 14, 1, 1), (PW - 14, 14, -1, 1), (14, PH - 14, 1, -1), (PW - 14, PH - 14, -1, -1)):
        br.append(wpath([(x + dx * 44, y), (x + dx * 10, y), (x, y + dy * 10), (x, y + dy * 44)]))
    o.append(f'<path d="{" ".join(br)}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="{" ".join(br)}" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(o)


def tabs():
    o = []
    y0, h = 30, 52
    # signal tab
    # right end at local x 730: >= 20 px clear of the gold top-right bracket (x 754..798, y 14..58)
    sx0, sw_ = 304, 186
    bx0, bw = sx0 + sw_ + 16, 224
    for x0, w, active in ((sx0, sw_, True), (bx0, bw, False)):
        cx = x0 + w / 2
        _, yoff = wp(cx, y0)
        y = yoff
        X = PX + x0
        if active:
            o.append(f'<rect x="{f(X)}" y="{f(y + 3)}" width="{w}" height="{h}" rx="{h / 2}" fill="{INK}"/>'
                     f'<rect x="{f(X)}" y="{f(y)}" width="{w}" height="{h}" rx="{h / 2}" fill="url(#{U}-tab)" stroke="{INK}" stroke-width="2.6"/>'
                     f'<rect x="{f(X + 16)}" y="{f(y + 6)}" width="{w - 40}" height="7" rx="3.5" fill="{WHITE}" opacity=".7"/>')
            # tick
            tx, ty = X + 24, y + h / 2
            o.append(f'<path d="M{f(tx)},{f(ty + 1)} l9,9 l17,-20" fill="none" stroke="{INK}" stroke-width="6" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
            o.append(f'<text x="{f(X + 60)}" y="{f(y + h / 2 + 9.8)}" font-family="{FONT}" font-size="28" '
                     f'font-weight="800" fill="{INK}">signal</text>')
            o.append(sparkle(X + w - 6, y + 2, 10, WHITE, 1, f"{U}-tw3"))
        else:
            o.append(f'<rect x="{f(X)}" y="{f(y)}" width="{w}" height="{h}" rx="{h / 2}" fill="#ffffff" fill-opacity=".55" '
                     f'stroke="#a898e6" stroke-width="2.4"/>'
                     f'<text x="{f(X + w / 2)}" y="{f(y + h / 2 + 9.5)}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="27" font-weight="700" fill="#9384d6">background</text>')
    return "".join(o)


# ------------------------------------------------------------------ assemble
def build_svg():
    rnd = random.Random(11)
    body = [window(rnd), floor(rnd)]
    # crystal glow pooled on the floor
    body.append(f'<ellipse cx="{CX + 10}" cy="800" rx="230" ry="40" fill="url(#{U}-pool)"/>')
    body.append(cryostat(rnd))
    body.append(cables())
    body.append(beam())
    body.append(panel())
    body.append(desk())
    # chibi Furina (official Genshin Impact emoji, (c) HoYoverse): "!" at the gold pulse
    body.append(f'<ellipse cx="1310" cy="640" rx="230" ry="230" fill="url(#{U}-back)"/>')
    body.append(ART.place("furina_gasp", 1318, H + 16, 470, f"{U}fu", shadow=("#6f5fc8", .35, 10), fade=(H - 40, H + 6)))
    # out-of-focus foreground bubbles (depth)
    for bx, by, r, op in ((70, 860, 64, .5), (1560, 70, 54, .45), (1240, 860, 30, .4)):
        body.append(f'<circle cx="{bx}" cy="{by}" r="{r}" fill="url(#{U}-bokeh)" opacity="{op}"/>'
                    f'<path d="M{bx - r * .62},{by - r * .1} A{r * .64},{r * .64} 0 0,1 {bx - r * .1},{by - r * .62}" fill="none" '
                    f'stroke="{WHITE}" stroke-width="{r * .12:.1f}" stroke-linecap="round" opacity="{op}"/>')
    # foreground sparkle dust
    for (sx, sy, r, col, cls) in ((560, 250, 9, WHITE, "tw"), (1450, 250, 8, GOLD_HI, "tw2"), (1560, 700, 10, WHITE, "tw3"),
                                  (470, 470, 6, GOLD_HI, "tw2"), (1200, 640, 7, WHITE, "tw")):
        body.append(sparkle(sx, sy, r, col, 1, f"{U}-{cls}"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Signal or Background? Anime illustration: an underground aquarium lab with a glowing germanium '
            f'crystal in a frosted cryostat, a holographic panel of detector waveforms with one pulse rise in gold, '
            f'and chibi Furina (official Genshin Impact emoji, © HoYoverse) gasping at the find">'
            f'{defs()}{style()}<g clip-path="url(#{U}-card)">{"".join(body)}</g></svg>')


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "card-majorana.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(build_svg())
    return p


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "assets", "v12")
    p = build(out)
    print(p, os.path.getsize(p) // 1024, "KB")
