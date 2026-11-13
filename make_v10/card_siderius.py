"""SIDERIUS card: anime twilight rooftop observatory (full-bleed 1600x900, rounded clip only).

    python3 card_siderius.py          -> writes the card to the scratchpad showcase folder
    build(out_dir) -> path            -> writes card-siderius.svg into out_dir

Keqing stands on the wet rooftop under a constellation whose stars trace a rising curve;
Boo Tao presses one eye to the little tripod telescope that is aimed at that constellation.
Scene art is adapted from scenes/siderius.py (copied here so the clouds, props and floor could
be redrawn); characters come from chars/ unchanged.  Python 3 stdlib only.  No text, no raster,
no script, no external refs.  Palette avoids hue 70-192.  All animation stops under
prefers-reduced-motion.  Original non-commercial fan art.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from chars.keqing import keqing  # noqa: E402
from chars.bootao import bootao  # noqa: E402

W, H, RX = 1600, 900, 28
U = "csd"           # uid prefix for everything this file draws
NAME = "card-siderius.svg"
SHOWCASE_DIR = ("/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/"
                "scratchpad/v10final/cards")

INK = "#3b3470"
SKY = ["#9290cc", "#aaa5da", "#bfb5e5", "#d0b8e4", "#ecb9d6", "#f9c3c2", "#ffd6b8", "#ffe7c8"]
GOLD = "#ffd27a"
GOLD_D = "#e9ad5c"
GOLD_L = "#fff1c4"
CREAM = "#fff7ea"
SUN = (1160, 610)
FLOOR_Y = 712

# layout (world coords)
KQ_X, KQ_Y, KQ_S = 800, 846, 1.68
BT_X, BT_Y, BT_S = 1396, 622, 1.04
TARGET = 3              # constellation star the telescope is aimed at


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def sparkle(cx, cy, r, fill, op=1.0, cls=""):
    """4-point anime sparkle."""
    k = r * 0.22
    d = (f"M{f(cx)} {f(cy - r)} Q{f(cx + k)} {f(cy - k)} {f(cx + r)} {f(cy)} "
         f"Q{f(cx + k)} {f(cy + k)} {f(cx)} {f(cy + r)} Q{f(cx - k)} {f(cy + k)} {f(cx - r)} {f(cy)} "
         f"Q{f(cx - k)} {f(cy - k)} {f(cx)} {f(cy - r)}Z")
    c = f' class="{cls}"' if cls else ""
    o = f' opacity="{f(op)}"' if op < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}{c}/>'


def _smooth(pts):
    """closed Catmull-Rom -> cubic path through pts"""
    n = len(pts)
    pts = [(round(x), round(y, 1)) for x, y in pts]
    d = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{round(c1[0])} {f(c1[1])} {round(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(d) + "Z"


# ------------------------------------------------------------------ clouds
def blob(cx, base, w, h, seed, lean=0.0, rr=(.17, .26)):
    """Puffs for one cumulus mass: a solid core and a dome of cauliflower lobes, each lobe
    carrying 1-3 smaller bumps so the top contour is finely knobbly."""
    rnd = random.Random(seed)
    rc = min(h * 0.42, w * .24)
    p = []
    k = max(1, int(round((w - 2 * rc) / (rc * 1.1))) + 1)
    for i in range(k):
        t = 0.5 if k == 1 else i / (k - 1)
        p.append((cx - w / 2 + rc + t * (w - 2 * rc), base - rc * 0.68, rc))
    sz = min(h, w * .5)
    per = math.pi * math.sqrt(((w / 2) ** 2 + h ** 2) / 2)
    n = max(4, int(round(per / (sz * sum(rr) * .78))))
    ring = []
    for i in range(n):
        th = math.pi * (1 - (i + rnd.uniform(-.22, .22)) / (n - 1))
        th = min(math.pi, max(0, th))
        s = math.sin(th)
        r = sz * rnd.uniform(*rr) * (0.75 + 0.45 * s)
        x = cx + (w / 2 - r) * math.cos(th) + lean * h * s * s
        y = min(base - (h - r) * (s ** 0.8), base - r * 0.5)
        p.append((x, y, r))
        ring.append((x, y))
        for j in range(rnd.choice((1, 2, 2))):
            a = math.radians(rnd.uniform(-155, -25))
            br = r * rnd.uniform(.34, .5)
            p.append((x + math.cos(a) * r * .8, y + math.sin(a) * r * .8, br))
    # interior polygon through the lobe centres so the union never has holes
    ring.sort(key=lambda q: q[0])
    poly = [(ring[0][0], base)] + ring + [(ring[-1][0], base)]
    return p, "M" + " L".join(f"{f(a)} {f(b)}" for a, b in poly) + "Z"


def _scallop(x0, x1, y_at, rnd, wmin, wmax, depth, down=True):
    """open path along y_at(x) made of arcs bulging down (lobe bottoms, cusps pointing up)"""
    d = []
    xx = x0
    while xx < x1:
        w = rnd.uniform(wmin, wmax)
        xb = min(xx + w, x1)
        ym = y_at((xx + xb) / 2) + (1 if down else -1) * depth * rnd.uniform(.6, 1.2) * (xb - xx) / wmax
        d.append(f"Q{round((xx + xb) / 2)} {round(ym)} {round(xb)} {round(y_at(xb))}")
        xx = xb
    return d


def cel_cloud(u, key, masses, pal, light, drift=None, op=1.0):
    """Anime cumulus from masses (back to front).  Each mass is one knobbly silhouette filled
    with flat cel tones: lit body, a scalloped mid-shadow band (lobe bottoms) that climbs on the
    side away from the light, a flat darker underside, a crisp bright rim along the lit top
    contour, and an occlusion shadow where it overlaps the masses behind.
    masses = [(puffs, base_y, cool)]; pal = (shadow, body, lit, rim, underside, base_glow)."""
    sh, body, lit, rimc, under, glow = pal
    lx = light
    defs, out = [], []
    prev = None

    def C(a, b, r, dx=0, dy=0, k=1.0):
        return f'<circle cx="{round(a + dx)}" cy="{round(b + dy)}" r="{round(r * k)}"/>'

    for mi, ((puffs, poly), base, cool) in enumerate(masses):
        cid = f"{u}{key}{mi}"
        top = min(b - r for a, b, r in puffs)
        hgt = base - top
        x0 = min(a - r for a, b, r in puffs) - 6
        x1 = max(a + r for a, b, r in puffs) + 6
        cx = (x0 + x1) / 2
        wd = x1 - x0
        tint = "#c2b0ea"
        c_sh = _mix(sh, tint, cool * .3)
        c_bd = _mix(body, tint, cool * .4)
        c_lt = _mix(lit, tint, cool * .35)
        # the silhouette circles as ONE path (all same winding -> union), defined once, reused
        sil = "".join(f"M{round(a - r)} {round(b)}a{round(r)} {round(r)} 0 1 0 {2 * round(r)} 0a{round(r)} {round(r)} 0 1 0 {-2 * round(r)} 0"
                      for a, b, r in puffs)
        defs.append(f'<path id="{cid}s" d="{sil}"/>')
        circ = f'<use href="#{cid}s"/>'
        defs.append(f'<clipPath id="{cid}"><rect x="{f(x0)}" y="{f(top - 4)}" width="{f(wd)}" height="{f(hgt + 4)}"/></clipPath>'
                    f'<clipPath id="{cid}c">{circ}<path d="{poly}"/></clipPath>')
        g = []
        if prev:   # occlusion shadow cast onto the mass just behind
            g.append(f'<g clip-path="url(#{prev}c)"><g clip-path="url(#{cid})" fill="{c_sh}" opacity=".5">'
                     + "".join(C(a, b, r + 8, -lx * 6, -4) for a, b, r in puffs if r > 12) + '</g></g>')
        rnd = random.Random(sum(map(ord, cid)) * 7)
        inner = [f'<rect x="{f(x0)}" y="{f(top - 4)}" width="{f(wd)}" height="{f(hgt + 4)}" fill="{c_lt}"/>']
        # smoothed top contour of the silhouette -> terminators run roughly parallel to it
        xs = [x0 + i * 8 for i in range(int(wd / 8) + 2)]

        def ctop(x):
            ys = [b - math.sqrt(r * r - (x - a) ** 2) for a, b, r in puffs if abs(x - a) < r]
            return min(ys) if ys else base
        raw = [ctop(x) for x in xs]
        sm = []
        for i in range(len(raw)):
            win = raw[max(0, i - 8):i + 9]
            sm.append(sum(win) / len(win))

        def contour(x):
            i = min(len(xs) - 2, max(0, int((x - x0) / 8)))
            t = (x - xs[i]) / 8
            return sm[i] + (sm[i + 1] - sm[i]) * t

        def side(x):
            return max(-1, min(1, (x - cx) / (wd / 2)))
        band = 8 + hgt * .07
        lim = base - band - 3

        def t1(x):
            return min(lim, contour(x) + hgt * .2 * (1 + .55 * side(x) * lx))

        def t2(x):
            return min(lim, contour(x) + hgt * .44 * (1 + .38 * side(x) * lx))
        d = [f"M{f(x0)} {f(base + 2)} L{f(x0)} {f(t1(x0))}"] + _scallop(x0, x1, t1, rnd, 34, 80, 14) + [f"L{f(x1)} {f(base + 2)}Z"]
        inner.append(f'<path d="{" ".join(d)}" fill="{c_bd}"/>')
        d = [f"M{f(x0)} {f(base + 2)} L{f(x0)} {f(t2(x0))}"] + _scallop(x0, x1, t2, rnd, 44, 110, 20) + [f"L{f(x1)} {f(base + 2)}Z"]
        inner.append(f'<path d="{" ".join(d)}" fill="{c_sh}"/>')
        # flat underside
        d = [f"M{f(x0)} {f(base + 2)} L{f(x0)} {f(base - band)}"] + _scallop(x0, x1, lambda x: base - band, rnd, 40, 90, 8, down=False) + [f"L{f(x1)} {f(base + 2)}Z"]
        inner.append(f'<path d="{" ".join(d)}" fill="{_mix(under, tint, cool * .3)}"/>')
        inner.append(f'<rect x="{f(x0)}" y="{f(base - 3.5)}" width="{f(wd)}" height="4" fill="{glow}" opacity=".9"/>')
        # crisp rim light along the lit top contour (silhouette minus itself shifted down-away)
        inner.append(f'<use href="#{cid}s" fill="{rimc}"/>'
                     f'<g fill="{c_lt}" transform="translate({f(-lx * 4)} 6)">{"".join(C(a, b, r) for a, b, r in puffs if b - r < top + hgt * .55)}</g>')
        g.append(f'<g clip-path="url(#{cid})"><g clip-path="url(#{cid}c)">{inner[0]}{inner[5]}{"".join(inner[1:5])}</g></g>')
        out.append("".join(g))
        prev = cid
    cls = f' class="{drift}"' if drift else ""
    o = f' opacity="{f(op)}"' if op < 1 else ""
    return "".join(defs), f'<g{cls}{o}>{"".join(out)}</g>'


def wisp(x, y, w, h, body, glow):
    def sp(x0, y0, ww, hh):
        return (f"M{f(x0)} {f(y0 + hh * .6)} C{f(x0 + ww * .3)} {f(y0 + hh * .05)} {f(x0 + ww * .75)} {f(y0)} {f(x0 + ww)} {f(y0 + hh * .55)} "
                f"C{f(x0 + ww * .7)} {f(y0 + hh * .95)} {f(x0 + ww * .3)} {f(y0 + hh * 1.0)} {f(x0)} {f(y0 + hh * .6)}Z")
    h *= 2.2
    return (f'<path d="{sp(x, y, w, h)}" fill="{body}"/>'
            f'<path d="{sp(x + w * .12, y + h * .62, w * .8, h * .42)}" fill="{glow}"/>')


def petal(px, py, sz, rot, cls="", flat=1.0, op=1.0):
    d = (f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} "
         f"C{f(-sz * .75)} {f(sz * .3)} {f(-sz * .7)} {f(-sz * .8)} 0 {f(-sz)}Z")
    hl = f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} C{f(sz * .25)} {f(sz * .2)} {f(sz * .25)} {f(-sz * .5)} 0 {f(-sz)}Z"
    c = f' class="{cls}"' if cls else ""
    sc = f" scale(1 {f(flat)})" if flat != 1 else ""
    o = f' opacity="{f(op)}"' if op < 1 else ""
    return (f'<g{c}{o}><g transform="translate({f(px)} {f(py)}){sc} rotate({rot})">'
            f'<path d="{d}" fill="#f7a9c4"/><path d="{hl}" fill="#ffd6e4"/>'
            f'<path d="M{f(-sz * .18)} {f(-sz * 1.02)} L0 {f(-sz * .72)} L{f(sz * .18)} {f(-sz * 1.02)}Z" fill="#f2b6dc"/>'
            f'</g></g>')


# ------------------------------------------------------------------ constellation
def constellation_pts():
    pts = []
    n = 9
    for i in range(n):
        t = i / (n - 1)
        px = 470 + t * 600
        py = 360 - 270 * (1 - math.exp(-3.0 * t)) / (1 - math.exp(-3.0)) + (8 if i % 2 else -6) * (1 - t)
        pts.append((px, py))
    return pts


# ------------------------------------------------------------------ scene
def scene(u):
    """returns dict of layers: defs, sky, mid, floor, props_back, front, top, css"""
    rnd = random.Random(29)
    defs, sky, mid, floor, front = [], [], [], [], []

    # ---------------- sky gradient + sun glow
    stops = "".join(f'<stop offset="{f(o)}" stop-color="{c}"/>'
                    for o, c in zip((0, .16, .3, .43, .55, .66, .76, .84), SKY))
    defs.append(f'<linearGradient id="{u}sky" x1="0" y1="0" x2="0" y2="1">{stops}'
                f'<stop offset="1" stop-color="{SKY[-1]}"/></linearGradient>')
    defs.append(f'<radialGradient id="{u}sun" cx="{SUN[0]}" cy="{SUN[1]}" r="560" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff4d6" stop-opacity=".95"/>'
                f'<stop offset=".25" stop-color="#ffe0b8" stop-opacity=".55"/>'
                f'<stop offset=".6" stop-color="#ffc6c8" stop-opacity=".18"/>'
                f'<stop offset="1" stop-color="#ffc6c8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}moonG" cx=".5" cy=".5" r=".5">'
                f'<stop offset=".35" stop-color="#fff6e4" stop-opacity=".7"/>'
                f'<stop offset="1" stop-color="#fff6e4" stop-opacity="0"/></radialGradient>')
    sky.append(f'<rect width="{W}" height="{H}" fill="url(#{u}sky)"/>')
    sky.append(f'<rect width="{W}" height="{H}" fill="url(#{u}sun)"/>')

    # ---------------- crescent moon (upper left)
    mx, my = 214, 132
    sky.append(f'<circle cx="{mx}" cy="{my}" r="88" fill="url(#{u}moonG)"/>')
    defs.append(f'<mask id="{u}moonM"><circle cx="{mx}" cy="{my}" r="38" fill="#fff"/>'
                f'<circle cx="{mx + 17}" cy="{my - 11}" r="33" fill="#000"/></mask>')
    sky.append(f'<g mask="url(#{u}moonM)"><circle cx="{mx}" cy="{my}" r="38" fill="#fff4dc"/>'
               f'<circle cx="{mx - 6}" cy="{my + 6}" r="36" fill="#ffe7b8"/></g>')

    # ---------------- faint milky way band
    defs.append(f'<filter id="{u}mw" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>')
    sky.append(f'<g transform="rotate(-14 820 150)" opacity=".5">'
               f'<ellipse cx="820" cy="150" rx="720" ry="46" fill="#d9c8f4" filter="url(#{u}mw)"/>'
               f'<ellipse cx="900" cy="146" rx="420" ry="20" fill="#f3e2f6" filter="url(#{u}mw)"/></g>')
    mw = []
    for i in range(90):
        tt = rnd.uniform(-1, 1)
        px = 820 + tt * 700
        py = 150 + rnd.gauss(0, 20)
        ang = math.radians(-14)
        qx = 820 + (px - 820) * math.cos(ang) - (py - 150) * math.sin(ang)
        qy = 150 + (px - 820) * math.sin(ang) + (py - 150) * math.cos(ang)
        mw.append(f'<circle cx="{round(qx)}" cy="{round(qy)}" r="{rnd.choice((0.7, 0.9, 1.1, 1.4))}" opacity="{rnd.uniform(.3, .8):.1f}"/>')
    sky.append(f'<g fill="#fffaf0">{"".join(mw)}</g>')

    # ---------------- background stars
    st = []
    for i in range(95):
        sx, sy = rnd.uniform(10, 1590), rnd.uniform(8, 380)
        if sy > 120 + 280 * (sx / 1600) and sx > 1000:
            continue
        fade = max(0.0, 1 - sy / 400)
        r = rnd.choice((0.9, 1.1, 1.3, 1.6, 2.1))
        cls = f' class="{u}tw{i % 3}"' if i % 4 == 0 else ""
        st.append(f'<circle cx="{round(sx)}" cy="{round(sy)}" r="{r}" opacity="{0.35 + 0.6 * fade:.1f}"{cls}/>')
    sky.append(f'<g fill="#fffaf0">{"".join(st)}</g>')
    for i, (sx, sy, r) in enumerate(((95, 260, 9), (420, 64, 8), (760, 40, 7), (1010, 150, 6), (1530, 70, 9), (590, 210, 6))):
        sky.append(sparkle(sx, sy, r, "#fffaf0", .9, f"{u}tw{i % 3}"))

    # ---------------- light rays from the low sun
    rays = []
    for i, (a, w, op) in enumerate(((-170, 5, .12), (-136, 6, .13), (-117, 4, .09),
                                    (-100, 5, .12), (-84, 3, .08))):
        a1, a2 = math.radians(a - w / 2), math.radians(a + w / 2)
        R = 1300
        sx0, sy0 = SUN
        rays.append(f'<path d="M{sx0} {sy0} L{f(sx0 + R * math.cos(a1))} {f(sy0 + R * math.sin(a1))} '
                    f'L{f(sx0 + R * math.cos(a2))} {f(sy0 + R * math.sin(a2))}Z" opacity="{op}"/>')
    defs.append(f'<radialGradient id="{u}ray" cx="{SUN[0]}" cy="{SUN[1]}" r="1150" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff8e6"/><stop offset=".55" stop-color="#fff0dc" stop-opacity=".6"/>'
                f'<stop offset="1" stop-color="#fff0dc" stop-opacity="0"/></radialGradient>')
    sky.append(f'<g class="{u}rays" fill="url(#{u}ray)">{"".join(rays)}</g>')

    # ---------------- constellation = rising curve
    pts = constellation_pts()
    n = len(pts)
    ax = "".join(f'<circle cx="{f(470 + i * 75)}" cy="392" r="1.6"/>' for i in range(9))
    ax += "".join(f'<circle cx="440" cy="{f(390 - i * 40)}" r="1.6"/>' for i in range(8))
    sky.append(f'<g fill="#fffaf0" opacity=".45">{ax}</g>')
    line = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts)
    defs.append(f'<filter id="{u}glow" x="-20%" y="-20%" width="140%" height="140%">'
                f'<feGaussianBlur stdDeviation="5"/></filter>')
    sky.append(f'<path d="{line}" fill="none" stroke="#fff3c8" stroke-width="9" opacity=".35" filter="url(#{u}glow)"/>')
    sky.append(f'<path d="{line}" fill="none" stroke="#fffaf0" stroke-width="3" stroke-linejoin="round" opacity=".85"/>')
    for i, (a, b) in enumerate(pts):
        big = i in (0, 3, 6, 8)
        r = 15 if i == n - 1 else (11 if big else 7)
        sky.append(f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r * 1.6)}" fill="#fff3c8" opacity=".35" filter="url(#{u}glow)"/>')
        sky.append(sparkle(a, b, r, GOLD_L if big else "#fffaf0", 1, f"{u}tw{i % 3}"))
        sky.append(f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r * .22)}" fill="#fff"/>')

    # ---------------- shooting stars
    defs.append(f'<linearGradient id="{u}tail" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="#fffaf0" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="#fffaf0"/></linearGradient>')
    for i, (sx, sy, L, ang) in enumerate(((1290, 80, 230, -28), (560, 92, 190, -30), (1480, 230, 140, -26))):
        cls = "" if i == 1 else f' class="{u}ss{i}"'
        sky.append(f'<g{cls}><g transform="translate({sx} {sy}) rotate({ang})">'
                   f'<path d="M{-L} -1 L0 -3.2 L0 3.2 L{-L} 1Z" fill="url(#{u}tail)" transform="scale(-1 1)"/>'
                   f'</g>{sparkle(sx, sy, 7, "#fffaf0")}</g>')

    # ---------------- clouds (back to front)
    # pal = (shadow, body, lit, rim, underside, base glow)
    PAL_FAR = ("#d2b3e4", "#ecc9e8", "#fad6e2", "#fff3ee", "#dcaed6", "#ffe0cf")
    PAL_TOW = ("#ab97dc", "#d4bbe9", "#f8d4e4", "#fff4f0", "#b294d8", "#ffd3c4")
    PAL_LFT = ("#a698d9", "#c2b5eb", "#ddd2f4", "#f9f4ff", "#9d8fd2", "#eacbe9")
    far = [(blob(812, 470, 300, 120, 3, lean=.3), 470, .45),
           (blob(700, 532, 360, 104, 5), 532, .1),
           (blob(940, 532, 320, 92, 6), 532, .1)]
    d_, g_ = cel_cloud(u, "f", far, PAL_FAR, 0.4, drift=f"{u}dr1")
    defs.append(d_)
    sky.append(g_)
    tower = [(blob(1500, 300, 260, 190, 11, lean=.15), 300, .9),
             (blob(1455, 598, 520, 360, 12, lean=-.1), 598, .3),
             (blob(1250, 598, 230, 120, 14), 598, 0)]
    tower[1][0][0].append((1650, 520, 120))
    d_, g_ = cel_cloud(u, "t", tower, PAL_TOW, -0.8)
    defs.append(d_)
    # front cauliflower lumps inside the tower's shadow side (breaks up the big flat shadow)
    PAL_SUB = ("#a08cd8", "#c2abe6", "#dcc3ee", "#f3e2f6", "#a58cd6", "#efc6dc")
    sub = [(blob(1545, 598, 250, 175, 31, lean=.1), 598, 0), (blob(1385, 598, 190, 112, 32), 598, 0)]
    d2_, g2_ = cel_cloud(u, "s", sub, PAL_SUB, -0.8)
    defs.append(d2_)
    sky.append(f'<g class="{u}dr2">{g_}<g clip-path="url(#{u}t1c)">{g2_}</g></g>')
    left = [(blob(110, 470, 330, 160, 21, lean=-.2), 470, .5),
            (blob(160, 582, 560, 150, 22), 582, .15)]
    left[-1][0][0].append((-60, 540, 90))
    d_, g_ = cel_cloud(u, "l", left, PAL_LFT, 0.8, drift=f"{u}dr1")
    defs.append(d_)
    sky.append(g_)
    sky.append(f'<g class="{u}dr2" opacity=".9">'
               + wisp(430, 446, 520, 20, "#f8c8d6", "#fff0de")
               + wisp(780, 478, 330, 14, "#fbcfd6", "#fff4e2")
               + wisp(560, 420, 220, 11, "#f2c2da", "#ffe8dc")
               + wisp(840, 300, 380, 16, "#c6aee8", "#efcde4")
               + wisp(1000, 330, 200, 11, "#cbb2ea", "#f2d0e2")
               + wisp(-60, 226, 360, 16, "#a998de", "#cdb6ea")
               + '</g>')

    # ---------------- distant town silhouette
    def skyline(seed, y0, hmin, hmax, col, win, x0=-10, x1=1610):
        r2 = random.Random(seed)
        d = [f"M{x0} 700 L{x0} {y0}"]
        wins = []
        xx = x0
        while xx < x1:
            w = r2.uniform(30, 90)
            h = r2.uniform(hmin, hmax)
            top = y0 - h
            if r2.random() < 0.25:
                d.append(f"L{f(xx)} {f(top + 10)} L{f(xx + w / 2)} {f(top - 8)} L{f(xx + w)} {f(top + 10)}")
            else:
                d.append(f"L{f(xx)} {f(top)} L{f(xx + w)} {f(top)}")
                if r2.random() < 0.18:
                    d.append(f"L{f(xx + w - 8)} {f(top)} L{f(xx + w - 8)} {f(top - 26)} L{f(xx + w - 10)} {f(top - 26)} L{f(xx + w - 10)} {f(top)}")
            if win:
                for _ in range(int(w * h / 900)):
                    if r2.random() < 0.55:
                        wx, wy = xx + r2.uniform(5, w - 9), top + r2.uniform(10, h - 4)
                        wins.append(f'<rect x="{f(wx)}" y="{f(wy)}" width="3.6" height="4.6" opacity="{f(r2.uniform(.55, 1))}"/>')
            xx += w
        d.append(f"L{x1} 700Z")
        return f'<path d="{" ".join(d)}" fill="{col}"/>' + (f'<g fill="{win}">{"".join(wins)}</g>' if wins else "")

    mid.append(skyline(4, 600, 20, 60, "#cfc3e6", None))
    mid.append(skyline(9, 640, 30, 90, "#b3a6da", "#ffe2a6"))
    mid.append(f'<path d="M1470 660 L1478 520 L1486 660Z" fill="#a395cf"/><circle cx="1478" cy="518" r="3.5" fill="#ff9fb8" class="{u}tw1"/>')
    defs.append(f'<linearGradient id="{u}haze" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffe7d6" stop-opacity="0"/><stop offset="1" stop-color="#f6d3e4" stop-opacity=".7"/></linearGradient>')
    mid.append(f'<rect x="0" y="560" width="{W}" height="110" fill="url(#{u}haze)"/>')

    # ---------------- rooftop: parapet, railing, floor
    VPX, VPY = 800, 560
    defs.append(f'<linearGradient id="{u}floor" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ddd2f2"/><stop offset=".45" stop-color="#cbbfe8"/>'
                f'<stop offset="1" stop-color="#b3a5da"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}wall" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#bcaee0"/><stop offset="1" stop-color="#a597d0"/></linearGradient>')
    fy = FLOOR_Y
    mid.append(f'<rect x="0" y="664" width="{W}" height="{fy - 664}" fill="url(#{u}wall)"/>')
    mid.append(f'<rect x="0" y="658" width="{W}" height="9" fill="#e9dcf6"/>')
    mid.append(f'<rect x="0" y="667" width="{W}" height="5" fill="#9081c4" opacity=".55"/>')
    rail = [f'<rect x="0" y="584" width="{W}" height="5" rx="2.5" fill="#f3e9fb"/>',
            f'<rect x="0" y="589" width="{W}" height="3" fill="#9f90cf"/>',
            f'<rect x="0" y="622" width="{W}" height="3.5" rx="1.7" fill="#e6d8f4"/>']
    posts = "".join(f'<rect x="{px}" y="588" width="5" height="72"/>' for px in range(20, 1600, 56))
    posts2 = "".join(f'<rect x="{px + 3}" y="588" width="2" height="72"/>' for px in range(20, 1600, 56))
    rail.append(f'<g fill="#e0d4f1">{posts}</g><g fill="#9f90cf" opacity=".6">{posts2}</g>')
    mid.append(f'<g>{"".join(rail)}</g>')

    floor.append(f'<rect x="0" y="{fy}" width="{W}" height="{H - fy}" fill="url(#{u}floor)"/>')
    tiles = []
    for i in range(-14, 15):
        bx = VPX + i * 150
        t0 = (fy - VPY) / (H - VPY)
        tiles.append(f'M{f(VPX + (bx - VPX) * t0)} {fy} L{f(bx)} {H}')
    yy, gap = fy, 16
    while yy < H:
        tiles.append(f'M0 {f(yy)} L{W} {f(yy)}')
        yy += gap
        gap *= 1.32
    floor.append(f'<path d="{" ".join(tiles)}" stroke="#9c8dcc" stroke-width="1.6" opacity=".42" fill="none"/>')
    floor.append(f'<path d="M0 {fy} L{W} {fy} L{W} {fy + 14} L0 {fy + 20}Z" fill="#a092cc" opacity=".45"/>')

    # wet sheen: sky colour bleeding onto the floor near the parapet
    defs.append(f'<linearGradient id="{u}wet" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffd9e6" stop-opacity=".55"/><stop offset="1" stop-color="#ffd9e6" stop-opacity="0"/></linearGradient>')
    floor.append(f'<rect x="0" y="{fy + 16}" width="{W}" height="60" fill="url(#{u}wet)"/>')

    # ---------------- puddles: irregular, reflecting the sky, with ripples and glints
    defs.append(f'<linearGradient id="{u}pud" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffe2c8"/><stop offset=".3" stop-color="#f7c3d4"/>'
                f'<stop offset=".7" stop-color="#b9a2e2"/><stop offset="1" stop-color="#a39cd9"/></linearGradient>')

    def puddle(key, cx, cy, rx, ry, seed, extra=""):
        r3 = random.Random(seed)
        P = []
        for k in range(14):
            a = 2 * math.pi * k / 14
            j = r3.uniform(.78, 1.12)
            P.append((cx + rx * j * math.cos(a), cy + ry * (j * .9 + .1) * math.sin(a)))
        d = _smooth(P)
        pid = f"{u}pd{key}"
        defs.append(f'<path id="{pid}s" d="{d}"/><clipPath id="{pid}"><use href="#{pid}s"/></clipPath>')
        g = [f'<use href="#{pid}s" fill="#9a86cf" opacity=".55" transform="translate(0 2.5)"/>',
             f'<use href="#{pid}s" fill="url(#{u}pud)"/>',
             f'<g clip-path="url(#{pid})">{extra}'
             f'<path d="M{f(cx - rx * 1.2)} {f(cy - ry * .2)} L{f(cx + rx * 1.2)} {f(cy - ry * .2)} L{f(cx + rx * 1.2)} {f(cy - ry * 1.3)} L{f(cx - rx * 1.2)} {f(cy - ry * 1.3)}Z" fill="#9a86cf" opacity=".5" transform="translate(0 {f(-ry * .5)})"/>'
             f'<path d="M{f(cx - rx * .62)} {f(cy + ry * .25)} H{f(cx + rx * .05)} M{f(cx + rx * .22)} {f(cy + ry * .5)} H{f(cx + rx * .5)}" '
             f'stroke="#fffaf6" stroke-width="2.6" stroke-linecap="round" opacity=".85"/>'
             f'</g>',
             f'<use href="#{pid}s" fill="none" stroke="#f7eefc" stroke-width="2" opacity=".75"/>']
        return "".join(g)

    # reflected crescent moon + bulb glints in the left puddle
    # reflected crescent moon + the observatory door's warm light (door at x 215..275)
    moon_r = ('<g opacity=".85"><circle cx="168" cy="842" r="13" fill="#fff4dc"/>'
              '<circle cx="175" cy="846" r="11" fill="#c2a6e0"/></g>'
              '<path d="M142 856 H188 M152 862 H176" stroke="#fff4dc" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>'
              '<path d="M216 810 H274 V872 H216Z" fill="#ffe2a6" opacity=".55"/>'
              '<path d="M224 810 H262 V872 H224Z" fill="#fff1c4" opacity=".45"/>'
              '<path d="M206 834 H284 M212 850 H270 M220 864 H262" stroke="#ffd27a" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>')
    floor.append(puddle("a", 270, 842, 150, 26, 7, moon_r))
    glints_b = "".join(f'<rect x="{x}" y="{y}" width="3.5" height="{h}" rx="1.7" fill="{c}" opacity=".85"/>'
                       for x, y, h, c in ((1120, 838, 16, GOLD), (1162, 842, 12, "#ffb9cf"), (1206, 836, 18, GOLD_L),
                                          (1252, 840, 14, GOLD), (1290, 846, 10, "#ffb9cf")))
    floor.append(puddle("b", 1205, 852, 160, 24, 3, glints_b))
    floor.append(puddle("c", 1495, 768, 72, 10, 5))
    floor.append(puddle("d", 590, 878, 60, 9, 9))
    # ripple rings (animated) on the puddles
    rip = []
    for i, (cx, cy, rx) in enumerate(((300, 848, 34), (1170, 856, 40), (1500, 770, 18))):
        rip.append(f'<ellipse class="{u}rp{i % 2}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{f(rx * .2)}" fill="none" stroke="#fff6fb" stroke-width="1.6"/>'
                   f'<ellipse cx="{cx}" cy="{cy}" rx="{f(rx * .5)}" ry="{f(rx * .1)}" fill="none" stroke="#fff6fb" stroke-width="1.2" opacity=".55"/>')
    floor.append("".join(rip))

    # ground highlight for the character spot
    defs.append(f'<radialGradient id="{u}spot" cx="800" cy="800" r="300" gradientUnits="userSpaceOnUse" '
                f'gradientTransform="translate(0 600) scale(1 .25)">'
                f'<stop offset="0" stop-color="#fff6e0" stop-opacity=".95"/>'
                f'<stop offset=".45" stop-color="#ffe6d8" stop-opacity=".55"/>'
                f'<stop offset="1" stop-color="#ffe6d8" stop-opacity="0"/></radialGradient>')
    floor.append(f'<ellipse cx="800" cy="800" rx="320" ry="80" fill="url(#{u}spot)"/>')

    # ---------------- observatory dome (left)
    # Key light = the sunset glow on the right (same as the drum, Keqing's rim light and the
    # puddle glints), so the hard cel shadow sits on the dome's left/back third and the moon
    # (upper left) adds a thin warm rim along that shadowed silhouette.  Line art uses the same
    # deep-plum ink as the characters: ~2.8 px on silhouettes, thinner on interior seams.
    OI = "#3a2766"               # character ink (chars/keqing.py INK)
    obs = []
    ox, oy = 245, 470
    R = 168
    wall_top, wall_bot = oy, 760
    L, Rr = ox - R - 6, ox + R + 6
    RW = R + 6
    drum = f"M{L} {wall_top} L{L} {wall_bot} A{RW} 22 0 0 0 {Rr} {wall_bot} L{Rr} {wall_top}Z"
    defs.append(f'<clipPath id="{u}drum"><path d="{drum}"/></clipPath>')
    defs.append(f'<filter id="{u}cs" x="-30%" y="-200%" width="160%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>')
    defs.append(f'<filter id="{u}dg" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>')
    hh = wall_bot - wall_top + 30
    term = ox - R * .34          # drum terminator (light from the right)

    def course(y, ry=20):        # a horizontal course line that follows the drum's curvature
        return f"M{L} {f(y)} A{RW} {ry} 0 0 0 {Rr} {f(y)}"

    def on_drum(v, y0, ry=20):   # point on a course at longitude v (degrees, 0 = facing us)
        a = math.radians(v)
        return ox + RW * math.sin(a), y0 + ry * math.cos(a)
    door_l, door_r, door_top = ox - 42, ox + 42, 556
    # vertical panel seams, spaced by cylinder projection; stop at the door arch
    seams = []
    for v in (-72, -54, -36, -18, 0, 18, 36, 54, 72):
        x = ox + RW * math.sin(math.radians(v))
        y1 = door_top + 6 if door_l - 4 < x < door_r + 4 else wall_bot + 24
        seams.append(f'M{f(x)} {wall_top + 22} V{f(y1)}')
    # rivets along each course (skip the door and the window)
    rivets, rhl = [], []
    for y0 in (556, 650):
        for v in range(-80, 81, 9):
            x, y = on_drum(v, y0)
            if door_l - 6 < x < door_r + 6 or (y0 == 556 and abs(x - (ox + 110)) < 30):
                continue
            rivets.append(f'<circle cx="{f(x)}" cy="{f(y - 6)}" r="2.3"/>')
            if x > term:
                rhl.append(f'<circle cx="{f(x + .8)}" cy="{f(y - 6.8)}" r=".9"/>')
    # soft contact shadow on the floor (cast toward viewer-left, away from the sunset)
    floor.append(f'<ellipse cx="{ox - 40}" cy="{wall_bot + 18}" rx="{RW + 40}" ry="26" fill="#8e7fc4" opacity=".42" filter="url(#{u}cs)"/>')
    # warm door light spilling out across the wet tiles (fans toward the viewer)
    defs.append(f'<linearGradient id="{u}spill" gradientUnits="userSpaceOnUse" x1="0" y1="{wall_bot}" x2="0" y2="{H}">'
                f'<stop offset="0" stop-color="#ffe2a6" stop-opacity=".85"/><stop offset=".55" stop-color="#ffd9b0" stop-opacity=".35"/>'
                f'<stop offset="1" stop-color="#ffd9b0" stop-opacity="0"/></linearGradient>')
    floor.append(f'<path d="M{ox - 31} {wall_bot + 10} L{ox + 31} {wall_bot + 10} L{ox + 112} {H} L{ox - 92} {H}Z" fill="url(#{u}spill)"/>'
                 f'<path d="M{ox - 10} {wall_bot + 18} L{ox + 14} {wall_bot + 18} L{ox + 40} {H} L{ox - 26} {H}Z" fill="#fff3d2" opacity=".28"/>')
    defs.append(f'<radialGradient id="{u}dglo" cx="{ox}" cy="672" r="96" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#ffe7b4" stop-opacity=".95"/><stop offset=".55" stop-color="#ffe0bc" stop-opacity=".45"/>'
                f'<stop offset="1" stop-color="#ffe0bc" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}wglo" cx="{ox + 110}" cy="560" r="52" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#ffe7b4" stop-opacity=".9"/><stop offset="1" stop-color="#ffe0bc" stop-opacity="0"/></radialGradient>')
    obs.append(f'<g clip-path="url(#{u}drum)">'
               # cylinder in hard cel planes: lit / shadow plane (left) / core / reflected rim / highlight
               f'<rect x="{L}" y="{wall_top}" width="{Rr - L}" height="{hh}" fill="#e6ddf6"/>'
               f'<rect x="{L}" y="{wall_top}" width="{f(term - L)}" height="{hh}" fill="#b4a5de"/>'
               f'<rect x="{f(term - 26)}" y="{wall_top}" width="26" height="{hh}" fill="#a594d6"/>'
               f'<rect x="{L}" y="{wall_top}" width="7" height="{hh}" fill="#fff0d8" opacity=".7"/>'
               f'<rect x="{f(ox + R * .48)}" y="{wall_top}" width="{f(R * .52 + 6)}" height="{hh}" fill="#f6effd"/>'
               f'<rect x="{f(ox + R * .72)}" y="{wall_top}" width="12" height="{hh}" fill="#fffaf2"/>'
               # pink sky-bounce from the wet tiles on the lower wall
               f'<path d="M{L} {wall_bot - 70} A{RW} 22 0 0 0 {Rr} {wall_bot - 70} L{Rr} {wall_bot + 40} L{L} {wall_bot + 40}Z" fill="#f4c9df" opacity=".28"/>'
               # warm glow from the door and window washing the wall
               f'<circle cx="{ox}" cy="672" r="96" fill="url(#{u}dglo)"/>'
               f'<circle cx="{ox + 110}" cy="560" r="52" fill="url(#{u}wglo)"/>'
               # panel seams + courses (ink, thin) with a lit lip under each course
               f'<path d="{" ".join(seams)}" stroke="{OI}" stroke-width="1.3" opacity=".32" fill="none"/>'
               + "".join(f'<path d="{course(y)}" stroke="{OI}" stroke-width="1.6" fill="none" opacity=".5"/>'
                         f'<path d="{course(y + 2.5)}" stroke="#fffaf2" stroke-width="1.6" fill="none" opacity=".6"/>'
                         for y in (556, 650))
               + f'<g fill="{OI}" opacity=".5">{"".join(rivets)}</g><g fill="#fffaf2">{"".join(rhl)}</g>'
               # hard cast shadow of the gold eave ring onto the top of the wall (deeper on the shadow side)
               + f'<path d="M{L} {wall_top} L{Rr} {wall_top} L{Rr} {wall_top + 18} A{RW} 22 0 0 1 {L} {wall_top + 26}Z" fill="#8576c0" opacity=".62"/>'
               f'<path d="M{L} {wall_top} L{f(term)} {wall_top} L{f(term)} {wall_top + 44} L{L} {wall_top + 28}Z" fill="#8576c0" opacity=".35"/>'
               # ground bounce + ambient occlusion at the foot
               f'<path d="M{L} {wall_bot - 10} A{RW} 22 0 0 0 {Rr} {wall_bot - 10} L{Rr} {wall_bot + 40} L{L} {wall_bot + 40}Z" fill="#8a7bc4" opacity=".5"/>'
               f'</g>')
    obs.append(f'<path d="{drum}" fill="none" stroke="{OI}" stroke-width="2.8" stroke-linejoin="round"/>')
    # arched doorway: inked stone frame with its own cel shadow, glowing interior, threshold step
    arch_o = f"M{door_l} {wall_bot + 2} L{door_l} 600 Q{ox} {door_top} {door_r} 600 L{door_r} {wall_bot + 2}Z"
    arch_i = f"M{ox - 30} {wall_bot} L{ox - 30} 606 Q{ox} 574 {ox + 30} 606 L{ox + 30} {wall_bot}Z"
    defs.append(f'<clipPath id="{u}arch"><path d="{arch_o}"/></clipPath>')
    defs.append(f'<linearGradient id="{u}door" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fff3d0"/><stop offset=".6" stop-color="#ffe2a6"/><stop offset="1" stop-color="#ffcd84"/></linearGradient>')
    obs.append(f'<path d="{arch_i}" fill="#ffe7b4" opacity=".9" filter="url(#{u}dg)"/>'
               f'<path d="{arch_o}" fill="#a596d6"/>'
               f'<g clip-path="url(#{u}arch)">'
               f'<path d="M{door_l - 4} {wall_bot + 4} L{door_l - 4} 540 L{ox - 8} 540 L{ox - 30} 606 L{ox - 30} {wall_bot}Z" fill="#8a7bc6"/>'
               f'<path d="M{door_r + 4} 540 L{ox + 8} 540 L{ox + 30} 606 L{ox + 30} {wall_bot} L{door_r + 4} {wall_bot + 4}Z" fill="#c4b7ea"/></g>'
               f'<path d="{arch_o}" fill="none" stroke="{OI}" stroke-width="2.6" stroke-linejoin="round"/>'
               f'<path d="{arch_i}" fill="url(#{u}door)" stroke="{OI}" stroke-width="1.6" stroke-linejoin="round"/>'
               # inside: the jamb's hard shadow on the left, a far wall line, the lit floor
               f'<path d="M{ox - 30} {wall_bot} L{ox - 30} 606 Q{ox - 22} 592 {ox - 12} 586 L{ox - 16} 612 L{ox - 16} {wall_bot}Z" fill="#f2b866" opacity=".75"/>'
               f'<path d="M{ox - 30} 724 L{ox + 30} 724 L{ox + 30} {wall_bot} L{ox - 30} {wall_bot}Z" fill="#ffd49a"/>'
               f'<path d="M{ox - 30} 724 H{ox + 30}" stroke="#e9ad5c" stroke-width="1.6"/>'
               f'<path d="M{ox - 4} 590 Q{ox + 12} 592 {ox + 22} 604" stroke="#fffaf0" stroke-width="3" fill="none" stroke-linecap="round"/>'
               # threshold step
               f'<path d="M{door_l - 8} {wall_bot + 2} L{door_r + 8} {wall_bot + 2} L{door_r + 8} {wall_bot + 12} L{door_l - 8} {wall_bot + 12}Z" '
               f'fill="#cfc3ee" stroke="{OI}" stroke-width="2" stroke-linejoin="round"/>'
               f'<path d="M{door_l - 6} {wall_bot + 4} H{door_r + 6}" stroke="#fff6e0" stroke-width="2" opacity=".85"/>')
    # round window: inked frame with cel shadow, glowing pane, mullions, glass glint
    wx, wy = ox + 110, 560
    obs.append(f'<circle cx="{wx}" cy="{wy}" r="25" fill="#a596d6" stroke="{OI}" stroke-width="2.4"/>'
               f'<path d="M{wx - 25} {wy} A25 25 0 0 1 {wx} {wy - 25} A19 19 0 0 0 {wx - 19} {wy}Z" fill="#8a7bc6"/>'
               f'<circle cx="{wx}" cy="{wy}" r="18" fill="url(#{u}door)" stroke="{OI}" stroke-width="1.4"/>'
               f'<path d="M{wx - 18} {wy} H{wx + 18} M{wx} {wy - 18} V{wy + 18}" stroke="{OI}" stroke-width="2.6" opacity=".8"/>'
               f'<path d="M{wx + 5} {wy - 13} A13 13 0 0 1 {wx + 13} {wy - 5}" stroke="#fffaf0" stroke-width="2.6" fill="none" stroke-linecap="round"/>')

    # ----- dome: orthographic hemisphere, point (lat th, lon ph) -> (ox + R cos th sin ph, oy - R sin th)
    def sph(th, ph):
        return ox + R * math.cos(th) * math.sin(ph), oy - R * math.sin(th)
    dome = f"M{ox - R} {oy} A{R} {R} 0 0 1 {ox + R} {oy}Z"
    defs.append(f'<clipPath id="{u}dome"><path d="{dome}"/></clipPath>')
    defs.append(f'<linearGradient id="{u}dsky" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#f3eefc" stop-opacity="0"/><stop offset=".55" stop-color="#f3d4e8" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="#f3d4e8" stop-opacity=".55"/></linearGradient>')
    # flat cel tones: lit body, hard terminator on the left third, deeper core shadow, highlight
    obs.append(f'<path d="{dome}" fill="#e6ddf6"/>')
    ribs = []
    for v in (-70, -48, -24, 40, 62):
        ph = math.radians(v)
        P = [sph(math.radians(t), ph) for t in range(0, 91, 6)]
        ribs.append("M" + " L".join(f"{f(a)} {f(b)}" for a, b in P))
    for t in (34, 62):           # latitude seams (ellipses squashed by the view)
        th = math.radians(t)
        P = [sph(th, math.radians(p)) for p in range(-90, 91, 6)]
        ribs.append("M" + " L".join(f"{f(a)} {f(b)}" for a, b in P))
    obs.append(f'<g clip-path="url(#{u}dome)">'
               f'<rect x="{ox - R}" y="{oy - R}" width="{2 * R}" height="{R}" fill="url(#{u}dsky)"/>'
               f'<path d="M{ox - R - 10} {oy + 4} L{ox - R - 10} {oy - R - 10} L{f(ox - R * .05)} {oy - R - 10} '
               f'C{f(ox - R * .42)} {f(oy - R * .78)} {f(ox - R * .52)} {f(oy - R * .36)} {f(ox - R * .4)} {oy + 4}Z" fill="#b4a5de"/>'
               f'<path d="M{ox - R - 10} {oy + 4} L{ox - R - 10} {oy - R} C{f(ox - R * .8)} {f(oy - R * .62)} {f(ox - R * .82)} {f(oy - R * .28)} {f(ox - R * .76)} {oy + 4}Z" fill="#a594d6"/>'
               # warm moon rim hugging the upper-left silhouette (inside the shadow side)
               f'<path d="M{ox - R} {oy} A{R} {R} 0 0 1 {f(ox - R * .2)} {f(oy - R * .98)} A{R - 7} {R - 5} 0 0 0 {ox - R + 7} {oy}Z" fill="#fff0d8" opacity=".8"/>'
               # lit-side highlight shape + small hard specular
               f'<path d="M{f(ox + R * .25)} {f(oy - R * .9)} C{f(ox + R * .62)} {f(oy - R * .8)} {f(ox + R * .86)} {f(oy - R * .5)} {f(ox + R * .9)} {f(oy - R * .12)} '
               f'C{f(ox + R * .74)} {f(oy - R * .42)} {f(ox + R * .54)} {f(oy - R * .7)} {f(ox + R * .25)} {f(oy - R * .9)}Z" fill="#fffaf2"/>'
               f'<path d="M{f(ox - R * .3)} {f(oy - R * .74)} Q{f(ox - R * .18)} {f(oy - R * .84)} {f(ox - R * .04)} {f(oy - R * .86)}" '
               f'stroke="#fffaf2" stroke-width="5" fill="none" stroke-linecap="round" opacity=".9"/>'
               f'<path d="{" ".join(ribs)}" stroke="{OI}" stroke-width="1.4" fill="none" opacity=".34"/>'
               # band of ground-bounce shade just above the gold ring
               f'<path d="M{ox - R} {oy} A{R} 16 0 0 0 {ox + R} {oy} L{ox + R} {oy - 14} A{R} 16 0 0 1 {ox - R} {oy - 14}Z" fill="#a898d8" opacity=".55"/>'
               '</g>')

    # ----- meridian slit: constant-width shutter opening on longitude ph0; its edges follow
    # x = ox + sin(ph0) * sqrt((R cos th)^2 - w^2) +- w cos(ph0), converging over the crown.
    ph0, w = math.radians(16), 25.0
    lft, rgt = [], []
    th = 0.0
    while True:
        rc = R * math.cos(th)
        if rc <= w + .5:
            break
        cxs = ox + math.sin(ph0) * math.sqrt(rc * rc - w * w)
        y = oy - R * math.sin(th)
        lft.append((cxs - w * math.cos(ph0), y))
        rgt.append((cxs + w * math.cos(ph0), y))
        th += math.radians(4)
    top_y = oy - R - 12
    lft.append((lft[-1][0], top_y))
    rgt.append((rgt[-1][0], top_y))
    slit = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in lft + rgt[::-1]) + "Z"
    # the visible inner jamb (thickness of the shell) along the left edge, lit lip on the right
    jamb = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in lft) + " L" + " L".join(f"{f(a + 9)} {f(b)}" for a, b in lft[::-1]) + "Z"
    lip_r = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in rgt)
    lip_l = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in lft)
    defs.append(f'<clipPath id="{u}slit"><path d="{slit}"/></clipPath>')
    defs.append(f'<linearGradient id="{u}sin" gradientUnits="userSpaceOnUse" x1="0" y1="{oy - R}" x2="0" y2="{oy}">'
                f'<stop offset="0" stop-color="#3f3482"/><stop offset=".7" stop-color="#4a3e90"/><stop offset="1" stop-color="#6a5296"/></linearGradient>')
    # telescope pivot / mount (inside the opening)
    sx_, sy_ = sph(math.radians(26), ph0)
    tx, ty = sx_ - 4, sy_ + 4
    pvx, pvy = tx + 7 * math.cos(math.radians(-40)), ty + 7 * math.sin(math.radians(-40))
    inner = []
    for t in (12, 24, 38, 52, 66):   # inner shell ribs seen through the opening (dimly lit)
        y = oy - R * math.sin(math.radians(t))
        inner.append(f'M{f(ox)} {f(y)} Q{f(ox + 46)} {f(y - 7)} {f(ox + 96)} {f(y)}')
    obs.append(f'<g clip-path="url(#{u}dome)"><g clip-path="url(#{u}slit)">'
               f'<rect x="{ox - 10}" y="{oy - R - 14}" width="120" height="{R + 20}" fill="url(#{u}sin)"/>'
               f'<path d="{" ".join(inner)}" stroke="#6a5cb0" stroke-width="2" fill="none" opacity=".75"/>'
               # warm lamp light from below inside the dome
               f'<ellipse cx="{f(pvx)}" cy="{oy - 4}" rx="34" ry="30" fill="#ffd9a0" opacity=".38" filter="url(#{u}dg)"/>'
               # pier + fork mount
               f'<path d="M{f(pvx - 9)} {oy + 2} L{f(pvx - 6)} {f(pvy + 14)} L{f(pvx + 6)} {f(pvy + 14)} L{f(pvx + 9)} {oy + 2}Z" '
               f'fill="#8c7ed0" stroke="{OI}" stroke-width="1.8" stroke-linejoin="round"/>'
               f'<path d="M{f(pvx - 9)} {oy + 2} L{f(pvx - 6)} {f(pvy + 14)} L{f(pvx - 1)} {f(pvy + 14)} L{f(pvx - 2)} {oy + 2}Z" fill="#6e60b8"/>'
               f'<path d="M{f(pvx - 15)} {f(pvy + 16)} H{f(pvx + 15)}" stroke="{OI}" stroke-width="7" stroke-linecap="round"/>'
               f'<path d="M{f(pvx - 14)} {f(pvy + 16)} H{f(pvx + 14)}" stroke="{GOLD_D}" stroke-width="4" stroke-linecap="round"/>'
               # counterweight rod + weight, pointing back down the polar axis
               f'<path d="M{f(pvx)} {f(pvy)} L{f(pvx - 26)} {f(pvy + 30)}" stroke="{OI}" stroke-width="4.4" stroke-linecap="round"/>'
               f'<path d="M{f(pvx)} {f(pvy)} L{f(pvx - 26)} {f(pvy + 30)}" stroke="#b6a8e6" stroke-width="2" stroke-linecap="round"/>'
               f'<circle cx="{f(pvx - 26)}" cy="{f(pvy + 30)}" r="7" fill="{GOLD}" stroke="{OI}" stroke-width="1.8"/>'
               '</g>'
               f'<path d="{jamb}" fill="#8679c4"/>'
               f'<path d="{lip_l}" stroke="#8c7ec8" stroke-width="5" fill="none"/>'
               f'<path d="{lip_r}" stroke="#fffaf2" stroke-width="4" fill="none"/>'
               f'<path d="{lip_r}" stroke="{OI}" stroke-width="1.6" fill="none" opacity=".7" transform="translate(3 0)"/>'
               f'<path d="{lip_l}" stroke="{OI}" stroke-width="1.6" fill="none" opacity=".7"/>'
               '</g>')
    obs.append(f'<path d="{dome}" fill="none" stroke="{OI}" stroke-width="2.8" stroke-linejoin="round"/>')
    # telescope tube emerging from the slot: its back end starts low inside the dark opening and
    # fades into the slot's shadow, so it reads as coming out of the dome rather than lying on it
    defs.append(f'<linearGradient id="{u}tfade" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="#43388a"/><stop offset=".4" stop-color="#43388a" stop-opacity=".7"/>'
                f'<stop offset="1" stop-color="#43388a" stop-opacity="0"/></linearGradient>')
    sw_ = f'stroke="{OI}" stroke-width="2.2" stroke-linejoin="round"'
    obs.append(f'<g transform="rotate(-40 {f(tx)} {f(ty)})">'
               f'<rect x="{f(tx)}" y="{f(ty - 20)}" width="196" height="40" fill="#e6d8f6" {sw_}/>'
               f'<rect x="{f(tx + 1)}" y="{f(ty + 5)}" width="194" height="14" rx="6" fill="#ab98dc"/>'
               f'<rect x="{f(tx + 8)}" y="{f(ty - 15)}" width="176" height="6" rx="3" fill="#fffaf3"/>'
               f'<rect x="{f(tx - 1)}" y="{f(ty - 21)}" width="56" height="42" fill="url(#{u}tfade)"/>'
               f'<rect x="{f(tx + 176)}" y="{f(ty - 25)}" width="30" height="50" rx="7" fill="{GOLD}" {sw_}/>'
               f'<rect x="{f(tx + 177)}" y="{f(ty + 7)}" width="28" height="17" rx="5" fill="{GOLD_D}"/>'
               f'<rect x="{f(tx + 182)}" y="{f(ty - 21)}" width="7" height="30" rx="3" fill="{GOLD_L}"/>'
               f'<rect x="{f(tx + 66)}" y="{f(ty - 23)}" width="14" height="46" rx="4" fill="{GOLD}" {sw_}/>'
               f'<rect x="{f(tx + 67)}" y="{f(ty + 7)}" width="12" height="15" rx="4" fill="{GOLD_D}"/>'
               f'</g>'
               # front arm of the fork, over the tube
               f'<path d="M{f(pvx - 8)} {f(pvy + 16)} L{f(pvx + 2)} {f(pvy - 2)}" stroke="{OI}" stroke-width="7.4" stroke-linecap="round"/>'
               f'<path d="M{f(pvx - 8)} {f(pvy + 16)} L{f(pvx + 2)} {f(pvy - 2)}" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>'
               f'<circle cx="{f(pvx + 2)}" cy="{f(pvy - 2)}" r="4.6" fill="{GOLD_L}" stroke="{OI}" stroke-width="1.6"/>')
    # gold eave ring at the dome's base (inked, with its own shaded underside)
    ring = (f"M{ox - R - 12} {oy - 8} A{R + 12} 14 0 0 0 {ox + R + 12} {oy - 8} L{ox + R + 12} {oy + 4} "
            f"A{R + 12} 16 0 0 1 {ox - R - 12} {oy + 4}Z")
    obs.append(f'<path d="{ring}" fill="#ffd27a"/>'
               f'<path d="M{ox - R - 12} {oy + 1} A{R + 12} 16 0 0 0 {ox + R + 12} {oy + 1} L{ox + R + 12} {oy + 4} A{R + 12} 16 0 0 1 {ox - R - 12} {oy + 4}Z" fill="#e9ad5c"/>'
               f'<path d="M{ox - R - 12} {oy - 8} L{f(ox - R * .3)} {oy + 6} L{f(ox - R * .3)} {oy + 20} L{ox - R - 12} {oy + 4}Z" fill="#e2a052" opacity=".7"/>'
               f'<path d="M{f(ox + R * .2)} {oy + 8} A{R + 12} 14 0 0 0 {f(ox + R * .85)} {oy}" stroke="#fff1c4" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
               f'<path d="{ring}" fill="none" stroke="{OI}" stroke-width="2.4" stroke-linejoin="round"/>')
    floor.append(f'<g>{"".join(obs)}</g>')

    # ---------------- string lights along the railing (catenaries)
    lights, glows = [], []
    anchors = [(440, 560), (720, 600), (1000, 596), (1240, 580), (1600, 610)]
    k = 0
    bulbs = []
    wires = []
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        sag = 34
        mxp, myp = (x0 + x1) / 2, max(y0, y1) + sag
        wires.append(f'M{x0} {y0} Q{f(mxp)} {f(myp + sag * .6)} {x1} {y1}')
        for j in range(1, 6):
            t = j / 6
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mxp + t * t * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (myp + sag * .6) + t * t * y1
            col = (GOLD, "#ffb9cf", "#fff1c4")[k % 3]
            glows.append(f'<circle cx="{f(bx)}" cy="{f(by + 8)}" r="14" fill="{col}" class="{u}tw{k % 3}"/>')
            lights.append(f'<rect x="{f(bx - 1.5)}" y="{f(by - 1)}" width="3" height="5" fill="#6e5fb0"/>'
                          f'<circle cx="{f(bx)}" cy="{f(by + 8)}" r="5.5" fill="{col}"/>'
                          f'<circle cx="{f(bx - 1.6)}" cy="{f(by + 6.4)}" r="1.8" fill="#fff"/>')
            bulbs.append((bx, col))
            k += 1
    refl = "".join(f'<rect x="{f(bx - 2.5)}" y="{fy + 6}" width="5" height="{26 + (j % 3) * 8}" rx="2.5" fill="{col}" opacity=".35"/>'
                   for j, (bx, col) in enumerate(bulbs))
    refl += (f'<path d="M430 {fy + 28} H1180" stroke="#f6d2e2" stroke-width="5" stroke-linecap="round" opacity=".35"/>'
             f'<path d="M520 {fy + 40} H900" stroke="#ffe6d8" stroke-width="3" stroke-linecap="round" opacity=".35"/>'
             f'<path d="M960 {fy + 46} H1300" stroke="#f6d2e2" stroke-width="3" stroke-linecap="round" opacity=".3"/>')
    defs.append(f'<linearGradient id="{u}sref" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffe9d2" stop-opacity=".75"/>'
                f'<stop offset="1" stop-color="#ffe0e6" stop-opacity="0"/></linearGradient>')
    refl += (f'<path d="M1135 {fy} L1185 {fy} L1215 {H} L1105 {H}Z" fill="url(#{u}sref)" opacity=".28"/>'
             + "".join(f'<path d="M{f(1160 - w)} {f(yy)} H{f(1160 + w)}" stroke="#fff4e4" stroke-width="{f(sw)}" stroke-linecap="round" opacity=".55"/>'
                       for yy, w, sw in ((724, 30, 3), (740, 46, 3), (762, 24, 2.5), (786, 56, 3.5), (818, 34, 3))))
    floor.append(f'<g>{refl}</g>')
    floor.append(f'<path d="{" ".join(wires)}" stroke="#6e5fb0" stroke-width="2" fill="none"/>'
                 f'<g opacity=".28" filter="url(#{u}glow)">{"".join(glows)}</g>{"".join(lights)}')

    # ---------------- floor glints (string-light sparkles on the wet tiles)
    gl = []
    for i, (gx, gy, r) in enumerate(((150, 790, 7), (420, 868, 6), (1040, 820, 6), (1360, 880, 8), (1560, 800, 6), (980, 884, 5))):
        gl.append(sparkle(gx, gy, r, GOLD_L, .95, f"{u}tw{i % 3}"))
    floor.append("".join(gl))

    # ---------------- fallen petals on the floor (flattened by perspective) + floating on puddles
    fp = []
    for i, (px, py, sz, rot) in enumerate(((96, 878, 9, 20), (122, 866, 8, 80), (140, 884, 7, -30), (470, 790, 8, 50),
                                           (520, 860, 9, 110), (1010, 868, 8, -70), (1068, 880, 9, 30), (1420, 836, 8, 60),
                                           (1530, 880, 10, -20), (1572, 858, 8, 100), (322, 852, 8, 40), (1240, 858, 8, -50),
                                           (60, 846, 9, -40), (36, 870, 8, 15), (168, 862, 7, 140), (440, 884, 8, -10))):
        fp.append(petal(px, py, sz * 1.45, rot, flat=.5, op=.95))
    floor.append("".join(fp))

    # ---------------- drifting petals (in front of everything)
    pet = []
    for i, (px, py, sz, rot) in enumerate(((380, 205, 9, 30), (1120, 420, 11, -40), (470, 640, 8, 70), (1560, 640, 12, 15),
                                           (130, 770, 13, 40), (1050, 760, 10, -60), (660, 600, 7, -30), (1000, 250, 8, 120))):
        pet.append(petal(px, py, sz * 1.7, rot, f"{u}pf{i % 3}"))
    front.append("".join(pet))
    motes = []
    for i, (mx2, my2, r) in enumerate(((560, 520, 6), (1080, 540, 8), (640, 700, 4), (1000, 690, 5),
                                       (500, 760, 5), (900, 470, 5), (700, 470, 4))):
        motes.append(sparkle(mx2, my2, r, GOLD_L, .9, f"{u}tw{i % 3}"))
    front.append("".join(motes))

    defs.append(f'<radialGradient id="{u}vig" cx="800" cy="520" r="980" gradientUnits="userSpaceOnUse">'
                f'<stop offset=".62" stop-color="#6a5fa8" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="#6a5fa8" stop-opacity=".15"/></radialGradient>')
    top = [f'<rect width="{W}" height="{H}" fill="url(#{u}vig)"/>']

    css = (f"@keyframes {u}tw{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}"
           f".{u}tw0{{animation:{u}tw 3.2s ease-in-out infinite}}"
           f".{u}tw1{{animation:{u}tw 4.1s ease-in-out -1.3s infinite}}"
           f".{u}tw2{{animation:{u}tw 2.7s ease-in-out -.6s infinite}}"
           f"@keyframes {u}ss{{0%,82%{{opacity:0;transform:translate(0,0)}}86%{{opacity:1}}100%{{opacity:0;transform:translate(-260px,130px)}}}}"
           f".{u}ss0{{animation:{u}ss 7s linear infinite}}"
           f".{u}ss1{{animation:{u}ss 9s linear -3s infinite}}"
           f".{u}ss2{{animation:{u}ss 11s linear -6s infinite}}"
           f"@keyframes {u}dr{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(14px)}}}}"
           f".{u}dr1{{animation:{u}dr 18s ease-in-out infinite}}"
           f".{u}dr2{{animation:{u}dr 24s ease-in-out -8s infinite}}"
           f"@keyframes {u}pf{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-10px,8px)}}}}"
           f".{u}pf0{{animation:{u}pf 6s ease-in-out infinite}}"
           f".{u}pf1{{animation:{u}pf 7.5s ease-in-out -2s infinite}}"
           f".{u}pf2{{animation:{u}pf 9s ease-in-out -4s infinite}}"
           f"@keyframes {u}ry{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}"
           f".{u}rays{{animation:{u}ry 6s ease-in-out infinite}}"
           f"@keyframes {u}rp{{0%{{transform:scale(.4);opacity:.9}}100%{{transform:scale(1.6);opacity:0}}}}"
           f".{u}rp0,.{u}rp1{{transform-box:fill-box;transform-origin:50% 50%}}"
           f".{u}rp0{{animation:{u}rp 3.6s ease-out infinite}}"
           f".{u}rp1{{animation:{u}rp 3.6s ease-out -1.8s infinite}}")
    return dict(defs=defs, sky=sky, mid=mid, floor=floor, front=front, top=top, css=css)


# ------------------------------------------------------------------ telescope + Boo Tao
def _rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


def telescope(u, eye, ang):
    """Little refractor on a wooden tripod.  Local frame: +x points back toward the observer;
    the eyecup's end sits at local (24, 0) = the ghost's eye.  Returns (back, front):
    back = tripod (drawn behind the ghost), front = tube + eyepiece (drawn over his face)."""
    ex, ey = eye
    ox_, oy_ = _rot(24, 0, ang)
    T = (ex - ox_, ey - oy_)
    INKT = "#3a2f6e"
    TUBE, TUBE_SH, TUBE_HI = "#6a5fc0", "#4b4196", "#9d93e6"
    ROSE, ROSE_SH = "#f4a9c6", "#d8799f"
    sw = 2.2
    # mount (tripod head) in world coords
    mx, my = _rot(-92, 26, ang)
    M = (T[0] + mx, T[1] + my)
    back = []
    legs = ((M[0] - 92, 822), (M[0] + 66, 826), (M[0] - 10, 840))
    back.append(f'<ellipse cx="{f(M[0] - 10)}" cy="830" rx="118" ry="13" fill="#8a76c4" opacity=".42"/>')
    for i, (lx, ly) in enumerate(legs):
        w0 = 9 if i < 2 else 8
        back.append(f'<path d="M{f(M[0])} {f(M[1])} L{f(lx)} {ly}" stroke="{INKT}" stroke-width="{w0 + 4}" stroke-linecap="round"/>'
                    f'<path d="M{f(M[0])} {f(M[1])} L{f(lx)} {ly}" stroke="#b07a86" stroke-width="{w0}" stroke-linecap="round"/>'
                    f'<path d="M{f(M[0] - 2)} {f(M[1] + 4)} L{f(lx - 2)} {ly - 4}" stroke="#e9b9b8" stroke-width="2.4" stroke-linecap="round"/>')
    # spreader tray
    sy_ = M[1] + 120
    back.append(f'<path d="M{f(M[0] - 50)} {f(sy_)} L{f(M[0] + 36)} {f(sy_ + 2)}" stroke="{INKT}" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M{f(M[0] - 50)} {f(sy_)} L{f(M[0] + 36)} {f(sy_ + 2)}" stroke="{GOLD}" stroke-width="2.4" stroke-linecap="round"/>')
    back.append(f'<path d="M{f(M[0])} {f(M[1] - 4)} L{f(M[0])} {f(M[1] + 34)}" stroke="{INKT}" stroke-width="12" stroke-linecap="round"/>'
                f'<path d="M{f(M[0])} {f(M[1] - 4)} L{f(M[0])} {f(M[1] + 34)}" stroke="#8f84d8" stroke-width="7" stroke-linecap="round"/>')

    # tube (local frame)
    t = []
    st = f'stroke="{INKT}" stroke-width="{sw}" stroke-linejoin="round"'
    # mount bracket + rings
    t.append(f'<path d="M-104 14 L-80 14 L-84 30 L-100 30Z" fill="{GOLD_D}" {st}/>')
    # main tube (slight taper toward the back)
    t.append(f'<path d="M-200 -17 L-14 -13 L-14 13 L-200 17Z" fill="{TUBE}" {st}/>')
    t.append(f'<path d="M-200 5 L-14 4 L-14 13 L-200 17Z" fill="{TUBE_SH}"/>')
    t.append(f'<path d="M-196 -10 L-18 -7.5" stroke="{TUBE_HI}" stroke-width="4.5" stroke-linecap="round"/>')
    t.append('<path d="M-170 -11 L-60 -9" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity=".85"/>')
    t.append(f'<path d="M-200 -17 L-14 -13 L-14 13 L-200 17Z" fill="none" {st}/>')
    # dew shield (rose) + objective lens
    t.append(f'<path d="M-246 -22 L-198 -20 L-198 20 L-246 22Z" fill="{ROSE}" {st}/>')
    t.append(f'<path d="M-246 8 L-198 7 L-198 20 L-246 22Z" fill="{ROSE_SH}"/>')
    t.append('<path d="M-240 -15 L-204 -14" stroke="#ffe3ee" stroke-width="3.5" stroke-linecap="round"/>')
    t.append('<ellipse cx="-246" cy="0" rx="7" ry="22" fill="#b9b2f0"/>'
             f'<path d="M-249 -14 Q-252 -2 -248 8" stroke="#ffffff" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
             f'<ellipse cx="-246" cy="0" rx="7" ry="22" fill="none" {st}/>')
    # gold rings
    for rx_ in (-200, -120, -64):
        t.append(f'<rect x="{rx_ - 5}" y="-19" width="12" height="38" rx="3" fill="{GOLD}" {st}/>'
                 f'<rect x="{rx_ - 5}" y="5" width="12" height="13" rx="3" fill="{GOLD_D}"/>'
                 f'<rect x="{rx_ - 3}" y="-16" width="3.5" height="20" rx="1.7" fill="{GOLD_L}"/>')
    # finder scope on top
    t.append(f'<path d="M-118 -19 L-112 -27 M-74 -19 L-80 -27" stroke="{INKT}" stroke-width="3"/>'
             f'<rect x="-128" y="-38" width="64" height="13" rx="5" fill="#e8ddfa" {st}/>'
             f'<rect x="-128" y="-31" width="64" height="6" rx="3" fill="#b4a6e6"/>'
             f'<rect x="-136" y="-40" width="12" height="17" rx="3" fill="{ROSE}" {st}/>')
    # focuser + eyepiece barrel (pressed to the ghost's eye)
    t.append(f'<rect x="-16" y="-12" width="18" height="24" rx="3" fill="{TUBE_SH}" {st}/>'
             f'<path d="M-6 12 L-6 20 L4 20 L4 12" fill="{GOLD}" {st}/>'
             f'<rect x="1" y="-7.5" width="15" height="15" rx="2" fill="#4a4380" {st}/>'
             f'<rect x="3" y="-5" width="11" height="3" rx="1.5" fill="#8a80d0"/>'
             f'<path d="M14 -10 L29 -16 Q34 0 29 16 L14 10Z" fill="#2f2860" {st}/>'
             f'<path d="M17 -8.5 L27 -12.5" stroke="#8a80d0" stroke-width="2.2" stroke-linecap="round"/>')
    front = f'<g transform="translate({f(T[0])} {f(T[1])}) rotate({ang})">{"".join(t)}</g>'
    # objective world position (for the sight beam)
    o2 = _rot(-250, 0, ang)
    obj = (T[0] + o2[0], T[1] + o2[1])
    feet = [((M[0] + lx) / 2, (M[1] + ly) / 2, lx, ly) for lx, ly in legs]
    return "".join(back), front, obj, feet


def sight_beam(u, obj, target):
    """dotted sight line from the objective lens toward a constellation star, three sparkles
    along it, and a little 'found it' reticle ring around that star"""
    x0, y0 = obj
    x1, y1 = target
    L = math.hypot(x1 - x0, y1 - y0)
    trail = (f'<path d="M{f(x0 + (x1 - x0) * .04)} {f(y0 + (y1 - y0) * .04)} L{f(x1 - (x1 - x0) * 34 / L)} {f(y1 - (y1 - y0) * 34 / L)}" '
             f'stroke="#fff4d2" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="3 12" class="{u}bm"/>')
    dots = "".join(sparkle(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 10 - t * 5, GOLD_L, 1, f"{u}tw{i % 3}")
                   for i, t in enumerate((0.16, 0.42, 0.68)))
    ring = (f'<g class="{u}rt" stroke="#fff6dc" fill="none" stroke-linecap="round">'
            f'<circle cx="{f(x1)}" cy="{f(y1)}" r="26" stroke-width="2.6" stroke-dasharray="30 11"/>'
            f'<path d="M{f(x1)} {f(y1 - 36)} V{f(y1 - 30)} M{f(x1)} {f(y1 + 30)} V{f(y1 + 36)} '
            f'M{f(x1 - 36)} {f(y1)} H{f(x1 - 30)} M{f(x1 + 30)} {f(y1)} H{f(x1 + 36)}" stroke-width="2.6"/></g>')
    return trail + dots + ring


def keqing_lit(u):
    """Keqing with an anime backlight: a soft Electro-violet aura and a faint warm bloom that
    melt into the sky (no hard outline outside her silhouette), plus a warm rim light just inside
    the ink on the sun-facing (right) edges."""
    flt = (f'<filter id="{u}kqf" x="-18%" y="-12%" width="136%" height="124%" color-interpolation-filters="sRGB">'
           f'<feComponentTransfer in="SourceAlpha" result="a"><feFuncA type="table" tableValues="0 0 1 1"/></feComponentTransfer>'
           f'<feGaussianBlur in="a" stdDeviation="13" result="ab"/>'
           f'<feFlood flood-color="#b8a4ff" flood-opacity=".38"/><feComposite in2="ab" operator="in" result="aura"/>'
           f'<feGaussianBlur in="a" stdDeviation="18" result="bb"/>'
           f'<feFlood flood-color="#fff0f4" flood-opacity=".4"/><feComposite in2="bb" operator="in" result="bloom"/>'
           # rim light from a CLOSED, HARD silhouette: threshold the alpha (drops the soft
           # blade glow / sparkle halos), close the gaps between twin-tail strands (dilate then
           # erode 6), pull it ~3 px further in so the band sits inside the ink, take a thin
           # crescent on the sun-facing (right/top) side, then keep only the part that lies on
           # solid fill (never across a strand gap or outside the line art).
           f'<feComponentTransfer in="SourceAlpha" result="h"><feFuncA type="discrete" tableValues="0 0 0 1"/></feComponentTransfer>'
           f'<feMorphology in="h" operator="dilate" radius="6" result="hd"/>'
           f'<feMorphology in="hd" operator="erode" radius="9" result="e"/>'
           f'<feOffset in="e" dx="-2" dy="1" result="es"/>'
           f'<feComposite in="e" in2="es" operator="out" result="edge0"/>'
           f'<feMorphology in="h" operator="erode" radius="3" result="hi"/>'
           f'<feComposite in="edge0" in2="hi" operator="in" result="edge"/>'
           f'<feFlood flood-color="#ffe9c9" flood-opacity=".6"/><feComposite in2="edge" operator="in" result="rim"/>'
           f'<feMerge><feMergeNode in="bloom"/><feMergeNode in="aura"/><feMergeNode in="SourceGraphic"/><feMergeNode in="rim"/></feMerge>'
           f'</filter>')
    back = (f'<radialGradient id="{u}kqb" cx="{KQ_X}" cy="560" r="330" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fff5ea" stop-opacity=".85"/>'
            f'<stop offset=".45" stop-color="#ffdfee" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="#ffe2ec" stop-opacity="0"/></radialGradient>')
    glow = f'<ellipse cx="{KQ_X}" cy="590" rx="330" ry="300" fill="url(#{u}kqb)"/>'
    fig = f'<g filter="url(#{u}kqf)"><g id="{u}kqfig">{keqing(KQ_X, KQ_Y, scale=KQ_S, uid=u + "kq", pose="stand", flip=True)}</g></g>'
    return flt + back, glow, fig


# ------------------------------------------------------------------ card
def card():
    u = U
    sc = scene(u)
    defs = list(sc["defs"])
    kdefs, kglow, kfig = keqing_lit(u)
    defs.append(kdefs)

    # Boo Tao: eye (the viewer-left one, head-local (-21, +3)) on the eyecup
    eye = (BT_X - 21 * BT_S, BT_Y + 3 * BT_S)
    pts = constellation_pts()
    tgt = pts[TARGET]
    ang = math.degrees(math.atan2(eye[1] - tgt[1], eye[0] - tgt[0]))
    tback, tfront, obj, feet = telescope(u, eye, ang)
    # tripod legs mirrored in the puddle under them
    lrefl = "".join(f'<path d="M{f(lx)} {f(ly)} L{f(2 * lx - mx_)} {f(2 * ly - my_)}" stroke="#b07a86" stroke-width="7" stroke-linecap="round"/>'
                    for mx_, my_, lx, ly in feet)
    lrefl = f'<g clip-path="url(#{u}pdb)" opacity=".35">{lrefl}</g>'
    # Keqing faintly mirrored on the wet floor (re-uses her drawing via <use>, fades out fast)
    kref = (f'<linearGradient id="{u}kfade" gradientUnits="userSpaceOnUse" x1="0" y1="{KQ_Y}" x2="0" y2="{KQ_Y + 60}">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="{u}kmask" maskUnits="userSpaceOnUse" x="500" y="{KQ_Y}" width="600" height="80">'
            f'<rect x="500" y="{KQ_Y}" width="600" height="80" fill="url(#{u}kfade)"/></mask>')
    defs.append(kref)
    kreflect = (f'<g mask="url(#{u}kmask)"><use href="#{u}kqfig" transform="matrix(1 0 0 -1 0 {2 * KQ_Y + 4})"/></g>')
    beam = sight_beam(u, obj, tgt)
    ghost = bootao(BT_X, BT_Y, scale=BT_S, pose="float", uid=u + "bt", shadow=False, flower=True)
    # the ghost holds still while peering (his own bob would pull the eye off the eyepiece)
    hold = f"g.{u}bt-bob{{animation:none!important}}"

    css = sc["css"] + hold + (f"@keyframes {u}bm{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}"
                              f".{u}bm{{animation:{u}bm 4s ease-in-out infinite}}"
                              f"@keyframes {u}rt{{0%,100%{{transform:rotate(0deg) scale(1)}}50%{{transform:rotate(25deg) scale(1.08)}}}}"
                              f".{u}rt{{transform-box:fill-box;transform-origin:50% 50%;animation:{u}rt 5s ease-in-out infinite}}"
                              f"@media (prefers-reduced-motion: reduce){{[class^='{u}'],[class*=' {u}']{{animation:none!important}}"
                              f".{u}ss0,.{u}ss1,.{u}ss2{{opacity:1}}}}")

    body = ("".join(sc["sky"]) + beam + "".join(sc["mid"]) + "".join(sc["floor"])
            + lrefl + kreflect + kglow + kfig
            + tback + ghost + tfront
            + "".join(sc["front"]) + "".join(sc["top"]))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Anime twilight rooftop observatory: a chibi lightning swordswoman under a rising-curve '
            f'constellation while a little ghost peers through a telescope">'
            f'<style>{css}</style>'
            f'<defs><clipPath id="{u}card"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>{"".join(defs)}</defs>'
            f'<g clip-path="url(#{u}card)">{body}</g></svg>')


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, NAME)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(card())
    return p


if __name__ == "__main__":
    p = build(SHOWCASE_DIR)
    print(p, os.path.getsize(p) // 1024, "KB")
