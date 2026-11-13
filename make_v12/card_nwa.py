"""Night Water Academy (夜水书院) card -- 1600x900 full-bleed anime illustration.

    python3 card_nwa.py            -> writes ../assets/v12/card-nwa.svg
    from card_nwa import build     -> build(out_dir) writes <out_dir>/card-nwa.svg, returns the path

A lantern-lit jetty and the academy hall on moonlit water, with official chibi Hu Tao (a Genshin
Impact "Paimon's Paintings" emoji, (c) HoYoverse, embedded from art/ by art.py) winking from the jetty.
Architecture helpers come from scenes/nwa.py (imported read-only); clouds, trees, water and the jetty
are drawn here.  Stdlib only, no text, no green hues; every id/class is prefixed with the uid.
"""
import math
import os
import random
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from scenes import nwa as N  # noqa: E402
import art as ART  # noqa: E402

W, H, RX = 1600, 900, 28
HZ = N.HZ  # 560, water line
n, pts = N.n, N.pts
MX, MY, MR = 600, 190, 86  # moon

# palette additions (all blue-violet / pink / gold; nothing in the 70-192 deg hue band)
DEEP = "#3b3680"      # deep indigo foreground ink
DEEP2 = "#4c4795"
DEEP_L = "#6d66bb"
BARK = "#54407f"
BARK_L = "#7b66ad"
WARM = "#ffcf86"
WARM_L = "#fff1c9"

HT_X, HT_Y, HT_S = 335, 846, 1.6


# ======================================================================= helpers
def circles_path(circles, rect=None):
    """Union of circles (+ optional rect) as ONE nonzero path; every sub-path runs counter-clockwise."""
    d = []
    for cx, cy, r in circles:
        d.append(f"M{n(cx-r)} {n(cy)}a{n(r)} {n(r)} 0 1 0 {n(2*r)} 0a{n(r)} {n(r)} 0 1 0 {n(-2*r)} 0")
    if rect:
        x0, y0, x1, y1 = rect
        d.append(f"M{n(x0)} {n(y1)}H{n(x1)}V{n(y0)}H{n(x0)}Z")
    return "".join(d)


def cel_layer(u, name, d, tones, v, b1, b2, rim, base=None, bounce=None):
    """Hard-edged anime cel shading of an arbitrary silhouette path d.
    tones = (shadow, mid, light, rim highlight); v = unit-ish vector toward the light.
    Tone k = silhouette shifted toward the light, clipped to the silhouette.  base -> flat bottom."""
    sh, mid, lt, hi = tones
    L = math.hypot(*v) or 1
    vx, vy = v[0] / L, v[1] / L
    pid, cid = f"{u}-{name}", f"{u}-{name}c"
    defs = [f'<path id="{pid}" d="{d}"/>', f'<clipPath id="{cid}"><use href="#{pid}"/></clipPath>',
            f'<mask id="{u}-{name}m" maskUnits="userSpaceOnUse" x="-200" y="-200" width="2000" height="1400">'
            f'<use href="#{pid}" fill="#fff"/><use href="#{pid}" fill="#000" transform="translate({n(-vx*rim)},{n(-vy*rim)})"/></mask>']
    body = [f'<use href="#{pid}" fill="{sh}"/>', f'<g clip-path="url(#{cid})">',
            f'<use href="#{pid}" fill="{mid}" transform="translate({n(vx*b1)},{n(vy*b1)})"/>',
            f'<use href="#{pid}" fill="{lt}" transform="translate({n(vx*b2)},{n(vy*b2)})"/>']
    if bounce is not None and base is not None:
        col, hgt = bounce
        body.append(f'<rect x="-50" y="{n(base-hgt)}" width="1700" height="{n(hgt)}" fill="{col}" opacity=".7"/>')
    body.append('</g>')
    body.append(f'<use href="#{pid}" fill="{hi}" mask="url(#{u}-{name}m)"/>')
    g = "".join(body)
    if base is not None:
        defs.append(f'<clipPath id="{cid}b"><rect x="-200" y="-400" width="2000" height="{n(base+400)}"/></clipPath>')
        g = f'<g clip-path="url(#{cid}b)">{g}</g>'
    return "".join(defs), g


def petal_def(u):
    """One cel-shaded petal (size 10) shared by every petal instance."""
    return f'<g id="{u}-pt">{N.petal(0, 0, 10, 0)}</g>'


def petal(u, x, y, s, rot, cls="", flat=1.0):
    c = f' class="{cls}"' if cls else ""
    sy = f" scale(1,{flat})" if flat != 1 else ""
    return f'<g transform="translate({n(x)},{n(y)}){sy} rotate({n(rot)}) scale({s/10:.2f})"><use href="#{u}-pt"{c}/></g>'


# ======================================================================= clouds
# Cumulus routine shared with the SIDERIUS card and the header (copied, not imported, so this card stays
# self-contained): one knobbly silhouette per mass filled with flat cel tones -- pink lit top, a scalloped
# periwinkle mid-shadow band that climbs on the side away from the moon, one flat hard-edged underside band,
# a single crisp rim on the lit top contour, and an occlusion shadow onto the mass behind.
def ni(v):
    return str(int(round(v)))


def ring_path(circles, rect=None):
    """Integer-rounded union-of-circles path (compact)."""
    d = []
    for cx, cy, r in circles:
        r = max(1, r)
        d.append(f"M{ni(cx-r)} {ni(cy)}a{ni(r)} {ni(r)} 0 1 0 {ni(2*r)} 0a{ni(r)} {ni(r)} 0 1 0 {ni(-2*r)} 0")
    if rect:
        x0, y0, x1, y1 = rect
        d.append(f"M{ni(x0)} {ni(y1)}H{ni(x1)}V{ni(y0)}H{ni(x0)}Z")
    return "".join(d)


def fz(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


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
    m = max(4, int(round(per / (sz * sum(rr) * .78))))
    ring = []
    for i in range(m):
        th = math.pi * (1 - (i + rnd.uniform(-.22, .22)) / (m - 1))
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
    ring.sort(key=lambda q: q[0])  # interior polygon through the lobe centres so the union never has holes
    poly = [(ring[0][0], base)] + ring + [(ring[-1][0], base)]
    return p, "M" + " L".join(f"{fz(a)} {fz(b)}" for a, b in poly) + "Z"


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


def cel_cloud(u, key, masses, pal, light, op=1.0, t1k=.2, t2k=.44):
    """Anime cumulus from masses (back to front); masses = [((puffs, poly), base_y, cool)];
    pal = (shadow, body, lit, rim, underside, base_glow); light = -1 (moon on the left) .. +1 (on the right)."""
    sh, body, lit, rimc, under, glow = pal
    lx = light
    defs, out = [], []
    prev = None

    def C(a, b, r, dx=0, dy=0):
        return f'<circle cx="{round(a + dx)}" cy="{round(b + dy)}" r="{round(r)}"/>'

    for mi, ((puffs, poly), base, cool) in enumerate(masses):
        cid = f"{u}-{key}{mi}"
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
        sil = "".join(f"M{round(a - r)} {round(b)}a{round(r)} {round(r)} 0 1 0 {2 * round(r)} 0a{round(r)} {round(r)} 0 1 0 {-2 * round(r)} 0"
                      for a, b, r in puffs)
        defs.append(f'<path id="{cid}s" d="{sil}"/>')
        defs.append(f'<clipPath id="{cid}"><rect x="{fz(x0)}" y="{fz(top - 4)}" width="{fz(wd)}" height="{fz(hgt + 4)}"/></clipPath>'
                    f'<clipPath id="{cid}c"><use href="#{cid}s"/><path d="{poly}"/></clipPath>')
        g = []
        if prev:   # occlusion shadow cast onto the mass just behind (no rect clip -> no vertical seam)
            g.append(f'<g clip-path="url(#{prev}c)"><g fill="{c_sh}" opacity=".5">'
                     + "".join(C(a, b, r + 8, -lx * 6, -4) for a, b, r in puffs if r > 12) + '</g></g>')
        rnd = random.Random(sum(map(ord, cid)) * 7)
        inner = [f'<rect x="{fz(x0)}" y="{fz(top - 4)}" width="{fz(wd)}" height="{fz(hgt + 4)}" fill="{c_lt}"/>']
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
            return min(lim, contour(x) + hgt * t1k * (1 + .55 * side(x) * lx))

        def t2(x):
            return min(lim, contour(x) + hgt * t2k * (1 + .38 * side(x) * lx))
        d = [f"M{fz(x0)} {fz(base + 2)} L{fz(x0)} {fz(t1(x0))}"] + _scallop(x0, x1, t1, rnd, 34, 80, 14) + [f"L{fz(x1)} {fz(base + 2)}Z"]
        inner.append(f'<path d="{" ".join(d)}" fill="{c_bd}"/>')
        d = [f"M{fz(x0)} {fz(base + 2)} L{fz(x0)} {fz(t2(x0))}"] + _scallop(x0, x1, t2, rnd, 44, 110, 20) + [f"L{fz(x1)} {fz(base + 2)}Z"]
        inner.append(f'<path d="{" ".join(d)}" fill="{c_sh}"/>')
        d = ([f"M{fz(x0)} {fz(base + 2)} L{fz(x0)} {fz(base - band)}"]
             + _scallop(x0, x1, lambda x: base - band, rnd, 40, 90, 8, down=False) + [f"L{fz(x1)} {fz(base + 2)}Z"])
        inner.append(f'<path d="{" ".join(d)}" fill="{_mix(under, tint, cool * .3)}"/>')
        inner.append(f'<rect x="{fz(x0)}" y="{fz(base - 3.5)}" width="{fz(wd)}" height="4" fill="{glow}" opacity=".9"/>')
        # crisp rim light along the lit top contour only (silhouette minus itself shifted down-away)
        inner.append(f'<use href="#{cid}s" fill="{rimc}"/>'
                     f'<g fill="{c_lt}" transform="translate({fz(-lx * 4)} 6)">{"".join(C(a, b, r) for a, b, r in puffs if b - r < top + hgt * .55)}</g>')
        g.append(f'<g clip-path="url(#{cid})"><g clip-path="url(#{cid}c)">{inner[0]}{inner[5]}{"".join(inner[1:5])}</g></g>')
        out.append("".join(g))
        prev = cid
    o = f' opacity="{fz(op)}"' if op < 1 else ""
    return "".join(defs), f'<g{o}>{"".join(out)}</g>'


# pal = (shadow, body, lit, rim, underside, base glow) -- moonlit night: pink-cream tops, periwinkle undersides
PAL_TOW = ("#a597dc", "#cdbbec", "#f6d6ea", "#fff6f4", "#a191d8", "#f6d2e4")
PAL_SUB = ("#9c8ed8", "#bcaee8", "#d9c9f2", "#f4eafa", "#988ad4", "#e8cbe8")
PAL_FAR = ("#bcaae4", "#dcc8f0", "#f8dcec", "#fff6f4", "#b9a6e0", "#fbe0e8")


def clouds(u):
    """Moonlit cumulus banks (moon at MX, MY).  Right of the moon: a three-tier tower behind the academy, lit from
    the left so its shadow plane climbs on the right; left of the moon: a low bank behind Hu Tao lit from the
    right; two small far clouds near the moon."""
    D, B = [], []
    far = [(blob(980, 150, 190, 70, 51), 150, .2)]
    d_, g_ = cel_cloud(u, "cf", far, PAL_FAR, -0.6, op=.95)
    D.append(d_)
    B.append(g_)
    low = [(blob(760, 520, 240, 74, 52), 520, .3)]
    d_, g_ = cel_cloud(u, "cl", low, PAL_FAR, -0.5)
    D.append(d_)
    B.append(g_)
    # right tower: crown, main body, low foot toward the moon
    tower = [(blob(1450, 250, 300, 170, 11, lean=.12), 250, .7),
             (blob(1420, 510, 560, 330, 12, lean=-.08), 510, .25),
             (blob(1170, 510, 230, 130, 14), 510, 0)]
    tower[1][0][0].append((1660, 420, 110))
    d_, g_ = cel_cloud(u, "ct", tower, PAL_TOW, -0.8, t2k=.5)
    D.append(d_)
    sub = [(blob(1560, 510, 230, 160, 31, lean=.1), 510, 0), (blob(1400, 510, 180, 100, 32), 510, 0)]
    d2_, g2_ = cel_cloud(u, "cs", sub, PAL_SUB, -0.8, t2k=.5)
    D.append(d2_)
    B.append(f'{g_}<g clip-path="url(#{u}-ct1c)">{g2_}</g>')
    # left bank behind Hu Tao, lit from the moon on its right
    left = [(blob(180, 350, 370, 176, 21, lean=-.1), 350, .5),
            (blob(300, 500, 700, 166, 22), 500, .15)]
    left[-1][0][0].append((-50, 456, 90))
    d_, g_ = cel_cloud(u, "cb", left, PAL_TOW, 0.8, t1k=.26, t2k=.56)
    D.append(d_)
    B.append(g_)
    return "".join(D), "".join(B)


# ======================================================================= trees
def sakura_tree(u, name, cx, base, w, h, rnd, lean=0):
    """Sakura tree: crooked trunk + branches, crown of scalloped blossom clumps in two cel-shaded layers."""
    o, defs = [], []
    top = base - h
    # trunk + main limbs (deep plum), drawn first so the crown overlaps them
    tr = (f"M{n(cx-8)} {base} C{n(cx-6)} {n(base-h*.18)} {n(cx-14+lean)} {n(base-h*.3)} {n(cx-4+lean)} {n(base-h*.42)} "
          f"L{n(cx+6+lean)} {n(base-h*.42)} C{n(cx+4+lean)} {n(base-h*.3)} {n(cx+8)} {n(base-h*.16)} {n(cx+9)} {base}Z")
    o.append(f'<path d="{tr}" fill="{BARK}"/>')
    o.append(f'<path d="M{n(cx-6)} {base} C{n(cx-4)} {n(base-h*.18)} {n(cx-11+lean)} {n(base-h*.3)} {n(cx-2+lean)} {n(base-h*.42)}" '
             f'stroke="{BARK_L}" stroke-width="2.4" fill="none"/>')
    limbs = []
    for ang, ln in ((-150, .5), (-115, .42), (-62, .44), (-28, .5), (-88, .36)):
        a = math.radians(ang)
        x1_, y1_ = cx + lean + math.cos(a) * w * ln, base - h * .42 + math.sin(a) * h * ln * .9
        limbs.append(f"M{n(cx+lean)} {n(base-h*.4)} Q{n((cx+lean+x1_)/2 + math.sin(a)*8)} {n((base-h*.42+y1_)/2)} {n(x1_)} {n(y1_)}")
    o.append(f'<path d="{" ".join(limbs)}" stroke="{BARK}" stroke-width="{n(max(3, w*.035))}" fill="none" stroke-linecap="round"/>')

    def clumps(k, rscale, yoff):
        cs = []
        for i in range(k):
            a = math.pi * (i + .5) / k + rnd.uniform(-.15, .15)
            ccx = cx + lean + math.cos(a) * w * .36 * rnd.uniform(.75, 1.05)
            ccy = top + h * .36 + yoff - math.sin(a) * h * .22 * rnd.uniform(.7, 1.1)
            R = w * rscale * rnd.uniform(.85, 1.15)
            cs.append((ccx, ccy, R * .78))
            m = 8
            for j in range(m):
                b = 2 * math.pi * j / m + rnd.uniform(-.2, .2)
                cs.append((ccx + math.cos(b) * R * .72, ccy + math.sin(b) * R * .62, R * rnd.uniform(.26, .36)))
        return cs
    back = clumps(5, .2, -h * .02)
    back.append((cx + lean, top + h * .2, w * .2))
    front = clumps(4, .17, h * .1)
    front.append((cx + lean + w * .05, top + h * .27, w * .17))
    v = (-.45, -1)
    d1, g1 = cel_layer(u, name + "b", ring_path(back), (N.SAK_DD, "#d184b3", N.SAK_D, N.SAK), v, w * .05, w * .11, 2.5)
    d2, g2 = cel_layer(u, name + "f", ring_path(front), (N.SAK_D, N.SAK, N.SAK_L, N.SAK_H), v, w * .05, w * .12, 2.5)
    defs += [d1, d2]
    o.append(g1)
    # a couple of limbs visible between the clumps
    o.append(f'<path d="M{n(cx+lean)} {n(base-h*.42)} q{n(w*.1)} {n(-h*.12)} {n(w*.2)} {n(-h*.14)} '
             f'M{n(cx+lean)} {n(base-h*.44)} q{n(-w*.08)} {n(-h*.1)} {n(-w*.22)} {n(-h*.1)}" stroke="{BARK}" '
             f'stroke-width="{n(max(2.4, w*.025))}" fill="none" stroke-linecap="round"/>')
    o.append(g2)
    # individual blossoms on the lit tops + hanging fringe
    fl = []
    for _ in range(int(w / 11)):
        a, b, r = rnd.choice(front + back[:len(back) // 2])
        fl.append(N.flower(a + rnd.uniform(-r, r) * .6, b - rnd.uniform(0, r) * .7, rnd.uniform(3.2, 5), rnd.uniform(0, 72),
                           rnd.choice([0, 0, 1])))
    o.append("".join(fl))
    return "".join(defs), "".join(o)


# ======================================================================= water details
def moon_glitter(u):
    """Bright sliced path of moonlight from the horizon toward the viewer, toward the jetty."""
    r = random.Random(3)
    o = [f'<path d="M{MX-24} {HZ} L{MX+24} {HZ} L{MX+150} {H} L{MX-150} {H}Z" fill="url(#{u}-gcol)" opacity=".45"/>',
         f'<path d="M{MX-10} {HZ} L{MX+10} {HZ} L{MX+70} {H} L{MX-70} {H}Z" fill="url(#{u}-gcol)" opacity=".8"/>']
    dash = []
    y = HZ + 4
    while y < H:
        t = (y - HZ) / (H - HZ)
        hw = 10 + t * 95
        k = 1 + int(t * 3)
        for _ in range(k):
            w = r.uniform(.25, .7) * hw * (1.25 if _ == 0 else .7)
            x = MX + r.gauss(0, .38) * hw
            hgt = 1.4 + t * 3.2
            dash.append(f'<rect x="{ni(x-w/2)}" y="{ni(y)}" width="{ni(w)}" height="{n(hgt)}" rx="{ni(hgt/2)}" '
                        f'opacity="{ni(r.uniform(.6, 1))}"/>')
        y += 4.5 + t * 13
    o.append(f'<g class="{u}-gl" fill="#fffbec">{"".join(dash)}</g>')
    return "".join(o)


def surface_cuts(u):
    """Anime water: thin tapered light streaks (in loose clusters) that slice the reflection, plus darker cuts."""
    r = random.Random(17)
    lt, dk = [], []

    def lens(x, y, w, h):
        return (f"M{ni(x-w/2)} {n(y)}Q{ni(x)} {n(y-h)} {ni(x+w/2)} {n(y)}Q{ni(x)} {n(y+h*.5)} {ni(x-w/2)} {n(y)}Z")
    for _ in range(15):
        t = r.random() ** 1.3
        cy = HZ + 14 + t * (H - HZ - 30)
        cx = r.uniform(800, 1600)
        for j in range(r.randint(1, 3)):
            y = cy + j * (4 + t * 9)
            x = cx + r.uniform(-30, 30) * (1 + t)
            w = (r.uniform(30, 80) + t * 140) * (1 - j * .25)
            lt.append(lens(x, y, w, 1.2 + t * 2.4))
    for _ in range(18):
        t = r.random()
        y = HZ + 14 + t * (H - HZ - 30)
        x = r.uniform(800, 1600)
        dk.append(lens(x, y, r.uniform(30, 80) + t * 120, 1 + t * 1.8))
    # long thin highlight streaks cutting straight through the academy's mirror image
    for (x, y, w, h) in [(1010, 606, 300, 1.4), (1330, 628, 240, 1.5), (930, 662, 260, 1.8), (1240, 704, 340, 2),
                         (1480, 744, 220, 2.2), (1090, 790, 380, 2.6), (1400, 836, 300, 2.8)]:
        lt.append(lens(x, y, w, h))
    return (f'<path d="{"".join(dk)}" fill="#5a5bb8" opacity=".35"/>'
            f'<path d="{"".join(lt)}" fill="#f6f2ff" opacity=".85"/>')

def split_ornaments(svg):
    """Split architecture into (base, ornaments).  The water reflection uses only the base: the small ornaments
    (gold curls, finials, ridge jewel, plaque, bracket studs, chiwen ridge-end curls, eave lanterns) are left out
    so the mirrored copy reads as soft mass, not detail.  Ornaments sit on top of the base, so base + ornaments
    redraws the original."""
    gold = "|".join(re.escape(c) for c in (N.GOLD, N.GOLD_L, N.GOLD_D))
    pat = re.compile(r'<g transform="translate\([^"]*\) scale\([^"]*\)"><circle class="lg".*?</g>'
                     rf'|<(?:path|circle|rect|ellipse)\b[^>]*(?:fill|stroke)="(?:{gold})"[^>]*/>'
                     rf'|<path\b[^>]*stroke="{re.escape(N.ROOF_D)}" stroke-width="7"[^>]*/>')
    orn = pat.findall(svg)
    return pat.sub("", svg), "".join(orn)


def ripple(x, y, w, op=.8):
    """Cel ripple: light lens over a darker lens."""
    h = max(1.6, w * .07)
    return (f'<path d="M{n(x-w)} {n(y)} Q{n(x)} {n(y-h*2)} {n(x+w)} {n(y)} Q{n(x)} {n(y-h*.6)} {n(x-w)} {n(y)}Z" fill="#f4f2ff" opacity="{op}"/>'
            f'<path d="M{n(x-w*.7)} {n(y+h*1.4)} Q{n(x+w*.15)} {n(y+h*3)} {n(x+w)} {n(y+h*1.4)} Q{n(x+w*.15)} {n(y+h*2)} {n(x-w*.7)} {n(y+h*1.4)}Z" '
            f'fill="#5f60bd" opacity=".35"/>')


# ======================================================================= jetty
def post_lamp(u, x, base):
    """Deep-indigo wooden lamp post with a glowing square paper lantern (andon) on top."""
    o = [f'<g transform="translate({x},{base})">']
    o.append(f'<ellipse cx="0" cy="-118" rx="96" ry="84" fill="url(#{u}-glw)" class="{u}-lg"/>')
    o.append(f'<rect x="-8" y="-92" width="16" height="96" rx="2" fill="{DEEP2}"/><rect x="-8" y="-92" width="5" height="96" fill="{DEEP_L}"/>')
    o.append(f'<rect x="-12" y="-4" width="24" height="7" rx="2" fill="{DEEP}"/>')
    o.append(f'<path d="M-24 -92 H24 L20 -98 H-20Z" fill="{DEEP}"/>')
    # lantern box
    o.append(f'<rect x="-19" y="-140" width="38" height="44" rx="3" fill="{WARM}"/>'
             f'<rect x="-19" y="-140" width="15" height="44" rx="3" fill="{WARM_L}"/>'
             f'<path d="M0 -140 V-96 M-19 -118 H19" stroke="{N.LAT}" stroke-width="1.8"/>'
             f'<rect x="-19" y="-140" width="38" height="44" rx="3" fill="none" stroke="{DEEP}" stroke-width="3"/>')
    # little roof cap
    o.append(f'<path d="M-30 -140 Q-12 -146 -8 -158 H8 Q12 -146 30 -140Z" fill="{DEEP}"/>'
             f'<path d="M-30 -140 Q-12 -146 -8 -158 H0 Q-4 -146 -16 -141Z" fill="{DEEP_L}"/>'
             f'<path d="M-30 -140 q-4 -1 -3 -7 M30 -140 q4 -1 3 -7" stroke="{N.GOLD}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
             f'<circle cx="0" cy="-162" r="5" fill="{N.GOLD}"/><circle cx="-1.5" cy="-163.5" r="1.8" fill="{N.GOLD_L}"/>')
    # red tassel
    o.append(f'<path d="M14 -96 v14" stroke="{N.LAN_D}" stroke-width="2.4" stroke-linecap="round"/><circle cx="14" cy="-80" r="3" fill="{N.LAN}"/>')
    o.append('</g>')
    return "".join(o)


def jetty(u):
    """Front-facing jetty (deck y 806-900 on the left) with deep-indigo pilings, wet glints, petals, ripples."""
    o = []
    top, xr0, xr1 = 806, 566, 628
    # shadow on the water behind the far edge
    o.append(f'<path d="M-10 {top-7} H{xr0+22} L{xr0+34} {top+4} H-10Z" fill="#5c5cb8" opacity=".45"/>')
    # side face
    o.append(f'<path d="M{xr0} {top} L{xr0+18} {top+6} L{xr1+26} 910 H{xr1}Z" fill="{DEEP2}"/>')
    o.append(f'<path d="M{xr0} {top} L{xr0+18} {top+6}" stroke="{DEEP_L}" stroke-width="2"/>')
    # deck
    o.append(f'<path d="M-10 {top} H{xr0} L{xr1} 910 H-10Z" fill="{N.WOOD_T}"/>')
    y, k, g, lips = top, 0, [], []
    while y < 900:
        hgt = 11 + k * 6
        xr = xr0 + (xr1 - xr0) * (y - top) / 104
        lips.append(f'<path d="M-10 {n(y+1)} H{n(xr)}" stroke="{N.WOOD_L}" stroke-width="{n(2 + k*.6)}"/>')
        y += hgt
        xr = xr0 + (xr1 - xr0) * (y - top) / 104
        g.append(f"M-10 {n(y)} H{n(xr)}")
        k += 1
    o.append("".join(lips))
    o.append(f'<path d="{" ".join(g)}" stroke="{N.WOOD_F}" stroke-width="2.4"/>')
    rj = random.Random(4)
    y, k, j = top, 0, []
    while y < 900:
        hgt = 11 + k * 6
        x = rj.uniform(20, 160)
        while x < 520:
            j.append(f"M{n(x)} {n(y+2)} V{n(y+hgt)}")
            x += rj.uniform(150, 260)
        y += hgt
        k += 1
    o.append(f'<path d="{" ".join(j)}" stroke="{N.WOOD_F}" stroke-width="2"/>')
    # warm lamp light pooled on the boards (right end) + cool moon glints
    o.append(f'<ellipse cx="520" cy="{top+30}" rx="120" ry="26" fill="url(#{u}-warm)"/>')
    o.append(f'<g fill="#efe6fb" opacity=".6"><rect x="470" y="{top+4}" width="60" height="3" rx="1.5"/>'
             f'<rect x="440" y="{top+19}" width="90" height="3.5" rx="1.7"/><rect x="420" y="{top+40}" width="70" height="4" rx="2"/>'
             f'<rect x="512" y="{top+42}" width="30" height="4" rx="2"/><rect x="400" y="{top+68}" width="110" height="5" rx="2.5"/></g>')
    # front-edge shade (deep indigo) for depth
    o.append(f'<path d="M-10 852 H{n(xr0+(xr1-xr0)*46/104)} L{xr1} 910 H-10Z" fill="{DEEP}" opacity=".26"/>')
    o.append(f'<path d="M-10 {top} H{xr0}" stroke="#f3eefc" stroke-width="3"/>')
    # fallen petals on the boards
    for (px, py, ps, rot) in [(118, 868, 8, 30), (232, 884, 9, -50), (468, 852, 7, 80), (520, 884, 9, 10), (176, 822, 6, -20),
                              (402, 826, 6, 60), (60, 890, 10, -70)]:
        o.append(petal(u, px, py, ps, rot, flat=.5))
    # water lapping along the far edge
    o.append(f'<path d="M20 {top-12} q14 -4 28 0 M150 {top-13} q18 -4 36 0 M330 {top-12} q12 -3 24 0 M470 {top-11} q12 -3 24 0" '
             f'stroke="#f2f0ff" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".85"/>')
    return "".join(o)


# ======================================================================= the scene
def scene(u="nwa"):
    N._G[0] = u
    rnd = random.Random(29)
    defs, out = [], []

    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in N.SKY)
    defs.append(f'<linearGradient id="{u}-sky" x1="0" y1="0" x2="0" y2="{HZ}" gradientUnits="userSpaceOnUse">{stops}</linearGradient>')
    defs.append(f'<radialGradient id="{u}-mglow" cx="{MX}" cy="{MY}" r="420" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fffbef" stop-opacity=".95"/><stop offset=".22" stop-color="#fff1f2" stop-opacity=".55"/>'
                f'<stop offset=".55" stop-color="#f0dcf6" stop-opacity=".18"/><stop offset="1" stop-color="#e8d8f8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-moon" cx="{MX-24}" cy="{MY-26}" r="{MR*1.3}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fffef8"/><stop offset=".7" stop-color="#fff5dc"/><stop offset="1" stop-color="#ffe6c4"/></radialGradient>')
    defs.append(f'<linearGradient id="{u}-water" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#f1cfe9"/><stop offset=".14" stop-color="#c3b2ef"/><stop offset=".5" stop-color="#9693e2"/>'
                f'<stop offset="1" stop-color="#6c6cca"/></linearGradient>')
    # reflection tint: darker + more saturated periwinkle the nearer the viewer
    defs.append(f'<linearGradient id="{u}-tint" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#b8a6ee" stop-opacity=".18"/><stop offset=".35" stop-color="#7f7ad8" stop-opacity=".3"/>'
                f'<stop offset="1" stop-color="#5354b6" stop-opacity=".5"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-gcol" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff8ee" stop-opacity=".55"/><stop offset=".5" stop-color="#fff2e6" stop-opacity=".22"/>'
                f'<stop offset="1" stop-color="#fff2e6" stop-opacity=".05"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-ray" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fffaf0" stop-opacity=".5"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-mist" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fbe4ef" stop-opacity="0"/><stop offset="1" stop-color="#fbe4ef" stop-opacity=".85"/></linearGradient>')
    defs.append(f'<radialGradient id="{u}-vig" cx="800" cy="430" r="980" gradientUnits="userSpaceOnUse">'
                f'<stop offset=".6" stop-color="#5d5cbc" stop-opacity="0"/><stop offset="1" stop-color="#5d5cbc" stop-opacity=".32"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-glw"><stop offset="0" stop-color="#fff4c8" stop-opacity="1"/>'
                f'<stop offset=".3" stop-color="#ffe2a6" stop-opacity=".5"/><stop offset="1" stop-color="#ffd8b0" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-warm"><stop offset="0" stop-color="#ffd9a0" stop-opacity=".6"/>'
                f'<stop offset=".5" stop-color="#ffc6c8" stop-opacity=".25"/><stop offset="1" stop-color="#ffc6c8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-hglow" cx="1030" cy="440" r="330" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#ffe6b8" stop-opacity=".45"/><stop offset="1" stop-color="#ffe6b8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-dpool"><stop offset="0" stop-color="{DEEP}" stop-opacity=".42"/>'
                f'<stop offset=".6" stop-color="{DEEP}" stop-opacity=".2"/><stop offset="1" stop-color="{DEEP}" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-shd"><stop offset="0" stop-color="{DEEP}" stop-opacity=".45"/>'
                f'<stop offset="1" stop-color="{DEEP}" stop-opacity="0"/></radialGradient>')

    defs.append(petal_def(u))
    # ---- sky
    out.append(f'<rect width="{W}" height="{HZ+2}" fill="url(#{u}-sky)"/>')
    out.append(f'<rect width="{W}" height="{HZ+2}" fill="url(#{u}-mglow)"/>')
    st = []
    for _ in range(56):
        sx, sy = rnd.uniform(0, W), rnd.uniform(0, 330)
        if math.hypot(sx - MX, sy - MY) < 200:
            continue
        st.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(rnd.uniform(.8, 2.0))}" opacity="{n(rnd.uniform(.5, .95))}"/>')
    out.append(f'<g fill="#fffaf6">{"".join(st)}</g>')
    for (sx, sy, r) in [(180, 220, 9), (900, 70, 11), (1450, 70, 8), (330, 80, 7), (780, 330, 6), (1240, 140, 7), (60, 300, 6)]:
        out.append(N.sparkle(sx, sy, r, "#fffaf0", .95, f"{u}-tw"))

    # ---- moon
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+70}" fill="#fff8fb" opacity=".16"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+34}" fill="#fff8fb" opacity=".22"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+128}" fill="none" stroke="#fff6fb" stroke-width="2" opacity=".35"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="url(#{u}-moon)"/>')
    out.append(f'<path d="M{MX+MR*.2} {MY-MR*.97} A{MR} {MR} 0 0 1 {MX+MR*.2} {MY+MR*.97} A{MR*.86} {MR*.98} 0 0 0 {MX+MR*.2} {MY-MR*.97}Z" fill="#fbe0cf" opacity=".55"/>')
    out.append(f'<path d="M{MX-46} {MY-30} q18 -14 34 -4 q10 10 -2 20 q-14 6 -22 16 q-12 6 -16 -8 q-6 -14 6 -24Z" fill="#f4dccf" opacity=".45"/>')
    out.append(f'<path d="M{MX+8} {MY+18} q20 -8 30 6 q6 16 -10 22 q-18 4 -24 -8 q-4 -12 4 -20Z" fill="#f4dccf" opacity=".4"/>')
    out.append(f'<path d="M{MX+26} {MY-48} q12 -4 18 4 q2 10 -8 12 q-12 0 -10 -16Z" fill="#f4dccf" opacity=".35"/>')
    out.append(f'<path d="M{MX-62} {MY-34} A70 70 0 0 1 {MX-20} {MY-74}" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" opacity=".8"/>')

    # ---- thin stratus streaks
    ws = []
    for (x0, y0, w, h) in [(-40, 124, 380, 16), (840, 118, 440, 15), (1240, 262, 330, 12), (300, 304, 300, 11), (700, 286, 220, 9)]:
        x1, xm = x0 + w, x0 + w * .45
        ws.append(f'<path d="M{x0} {y0} Q{n(xm)} {y0-h} {x1} {y0} Q{n(xm)} {n(y0+h*.35)} {x0} {y0}Z" fill="{N.CL_MID}" opacity=".85"/>')
        ws.append(f'<path d="M{x0+8} {y0-1} Q{n(xm)} {n(y0-h*.95)} {x1-6} {y0-1} Q{n(xm)} {n(y0-h*.3)} {x0+8} {y0-1}Z" fill="{N.CL_HI}" opacity=".9"/>')
    out.append("".join(ws))

    # ---- reflected group 1: cumulus banks
    cd, cb = clouds(u)
    defs.append(cd)
    defs.append(f'<g id="{u}-R1">{cb}</g>')
    out.append(f'<use href="#{u}-R1"/>')

    # ---- moon rays
    rays = []
    for ang, wdeg, ln, op in [(62, 3.2, 820, .55), (78, 2.0, 760, .45), (96, 3.6, 860, .5), (112, 1.8, 700, .4), (128, 2.6, 760, .38), (45, 1.6, 640, .35)]:
        a0, a1 = math.radians(ang - wdeg / 2), math.radians(ang + wdeg / 2)
        p = [(MX + math.cos(a0) * 70, MY + math.sin(a0) * 70), (MX + math.cos(a0) * ln, MY + math.sin(a0) * ln),
             (MX + math.cos(a1) * ln, MY + math.sin(a1) * ln), (MX + math.cos(a1) * 70, MY + math.sin(a1) * 70)]
        rays.append(f'<polygon points="{pts(p)}" opacity="{op}"/>')
    out.append(f'<g class="{u}-ry" fill="url(#{u}-ray)">{"".join(rays)}</g>')

    # ---- reflected group 2: mountains, trees, academy
    mt = N.mountains(rnd)
    trnd = random.Random(11)
    td1, t1 = sakura_tree(u, "t1", 772, 514, 158, 196, trnd, lean=-6)
    td2, t2 = sakura_tree(u, "t2", 1352, 522, 136, 168, trnd, lean=8)
    td3, t3 = sakura_tree(u, "t3", 1590, 550, 124, 176, trnd, lean=-4)
    hd, hs = N.hall(u)
    pd, ps = N.pavilion(u)
    defs += [td1, td2, td3, hd, pd]
    ps_b, ps_o = split_ornaments(ps)
    hs_b, hs_o = split_ornaments(hs)
    defs.append(f'<g id="{u}-Rmt">{mt}<rect x="0" y="{HZ-70}" width="{W}" height="72" fill="url(#{u}-mist)"/></g>')
    defs.append(f'<g id="{u}-Rbl">{t1}{t3}{t2}{N.bridge()}{ps_b}{hs_b}</g>')
    # R2 = full academy (drawn above the water); R2m = ornament-free copy used only for the mirror image
    defs.append(f'<g id="{u}-R2"><use href="#{u}-Rmt"/><rect x="0" y="0" width="{W}" height="{HZ}" fill="url(#{u}-hglow)"/>'
                f'<use href="#{u}-Rbl"/>{ps_o}{hs_o}</g>'.replace('class="lg"', f'class="{u}-lg"'))
    defs.append(f'<g id="{u}-R2m"><use href="#{u}-Rmt"/><use href="#{u}-Rbl"/></g>')

    # ---- water + sliced mirror reflection
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{u}-water)"/>')
    # the mirror image fades with depth (~.55 at the waterline -> ~.15 at the bottom edge) so the water stays
    # periwinkle and the lotus lanterns / characters remain the brightest things in the lower half
    defs.append(f'<linearGradient id="{u}-rfade" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff" stop-opacity=".58"/><stop offset=".45" stop-color="#fff" stop-opacity=".34"/>'
                f'<stop offset="1" stop-color="#fff" stop-opacity=".14"/></linearGradient>')
    defs.append(f'<mask id="{u}-rmask" maskUnits="userSpaceOnUse" x="0" y="{HZ}" width="{W}" height="{H-HZ}">'
                f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{u}-rfade)"/></mask>')
    yy, i, refl = HZ, 0, []
    while yy < H:
        t = (yy - HZ) / (H - HZ)
        hgt = 3 + t * 13
        gap = .4 + t * 2.6          # water shows through between slices: horizontal ripple breaks
        amp = .6 + t * 9
        dx = amp * math.sin(i * 1.9) + amp * .4 * math.sin(i * 0.7 + 1)
        cid = f"{u}-ws{i}"
        defs.append(f'<clipPath id="{cid}"><rect x="-20" y="{n(yy)}" width="{W+40}" height="{n(max(1.2, hgt - gap))}"/></clipPath>')
        refl.append(f'<g clip-path="url(#{cid})"><g transform="translate({n(dx)},{2*HZ}) scale(1,-1)">'
                    f'<use href="#{u}-R1" opacity=".7"/><use href="#{u}-R2m"/></g></g>')
        yy += hgt
        i += 1
    out.append(f'<g mask="url(#{u}-rmask)">{"".join(refl)}</g>')
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{u}-tint)"/>')
    out.append(surface_cuts(u))
    out.append(moon_glitter(u))
    # warm window light columns under the academy
    wc = []
    for cxw in (838, 915, 992, 1069, 1146, 1223, 1508):
        yy, k = HZ + 6, 0
        while yy < 770:
            wc.append(f'<rect x="{ni(cxw - 9 + (k%3-1)*4)}" y="{ni(yy)}" width="{ni(18 - k*0.6)}" height="2.6" rx="1.3" opacity="{max(.15, .85 - k*.06):.2f}"/>')
            yy += 9 + k * 1.6
            k += 1
    out.append(f'<g class="{u}-gl2" fill="{N.GOLD_L}">{"".join(wc)}</g>')
    # sparse ripples away from the characters
    rp, rr = [], random.Random(5)
    for _ in range(28):
        xx, yy = rr.uniform(0, W), rr.uniform(HZ + 10, H - 10)
        if xx < 700 and yy > 700:
            continue
        if abs(xx - MX) < 90:
            continue
        t = (yy - HZ) / (H - HZ)
        rp.append(ripple(xx, yy, 12 + t * 60 * rr.uniform(.5, 1), .7))
    out.append("".join(rp))
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="2" fill="#fff4f8" opacity=".9"/>')
    ln, lr = [], random.Random(8)
    for _ in range(16):
        yy = HZ + 6 + lr.random() ** 1.6 * 80
        ln.append(f'<rect x="{n(lr.uniform(-50, 1500))}" y="{n(yy)}" width="{n(lr.uniform(80, 260))}" height="1.4" opacity="{n(lr.uniform(.35, .7))}"/>')
    out.append(f'<g fill="#fff6fb">{"".join(ln)}</g>')
    fp = []
    for (px, py, ps_, rot) in [(860, 720, 7, -40), (1180, 840, 10, 70), (1350, 650, 6, 10), (990, 872, 9, -10), (700, 770, 6, 50),
                               (560, 700, 6, 20)]:
        fp.append(petal(u, px, py, ps_, rot, flat=.45))
    out.append("".join(fp))

    # ---- academy complex above the water
    out.append(f'<use href="#{u}-R2"/>')

    # ---- floating lotus lanterns (kept clear of both characters and of the moon path)
    defs.append(N.river_lantern(0, 0, 1, f"{u}-lg").replace('<g transform="translate(0,0) scale(1)">', f'<g id="{u}-rl">', 1))
    for (lx, ly, ls) in [(520, 584, .42), (880, 598, .5), (1180, 594, .48), (1400, 606, .55), (1560, 640, .75),
                         (900, 700, .8), (1290, 676, .9), (1060, 760, 1.05), (1470, 800, 1.35), (900, 858, 1.2)]:
        out.append(f'<use href="#{u}-rl" transform="translate({lx},{ly}) scale({ls})"/>')

    # ---- jetty + stone lantern + lamp post
    out.append(jetty(u))
    sl = N.stone_lantern(64, 822, 1.18).replace('class="lg"', f'class="{u}-lg"')
    for a, b in ((N.ST_F, "#6f68bd"), (N.ST_T, "#9690dc"), (N.ST_D, DEEP2), (f'fill="{N.ROOF}"', f'fill="{DEEP2}"')):
        sl = sl.replace(f'fill="{a}"' if a.startswith("#") else a, f'fill="{b}"' if b.startswith("#") else b)
    out.append(sl)
    out.append(post_lamp(u, 548, 814))

    # ---- framing sakura branch (top-left)
    bd, bs = N.sakura_branch(u, random.Random(13))
    defs.append(bd)
    out.append(bs.replace(f'stroke="{N.BARK}"', f'stroke="{BARK}"'))
    return defs, out


def corner_spray(u, rnd):
    """Foreground sakura spray dipping in from the top-right corner, in deeper backlit tones (depth accent)."""
    o = [f'<path d="M1620 -6 Q1540 30 1470 34 Q1420 36 1388 70 M1540 22 Q1528 60 1546 96 M1470 34 Q1452 14 1424 8" '
         f'stroke="{DEEP}" stroke-width="8" fill="none" stroke-linecap="round"/>',
         f'<path d="M1620 -10 Q1540 26 1470 30 Q1422 32 1392 64" stroke="{DEEP_L}" stroke-width="2.2" fill="none" stroke-linecap="round"/>']
    back, front = [], []
    for (cx, cy, rr) in [(1600, 12, 30), (1530, 30, 26), (1468, 38, 24), (1404, 66, 20), (1546, 92, 18), (1430, 12, 16)]:
        for _ in range(7):
            a, d = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, rr)
            fx, fy = cx + math.cos(a) * d, cy + math.sin(a) * d * .8
            t = rnd.random()
            (back if t < .55 else front).append(N.flower(fx, fy, rnd.uniform(8, 12.5), rnd.uniform(0, 72), 2 if t < .55 else 1))
        bx, by = cx + rnd.uniform(-rr, rr), cy + rr * .9
        front.append(f'<ellipse cx="{n(bx)}" cy="{n(by)}" rx="3.4" ry="4.8" fill="{N.SAK_DD}"/>')
    return "".join(o + back + front)


def drift(u):
    """Drifting petals + sparkles drawn over the characters (foreground layer)."""
    prnd = random.Random(21)
    pts_ = [(260, 260), (700, 420), (860, 180), (1180, 330), (1380, 240), (1500, 420), (980, 520),
            (1100, 820), (1520, 560), (640, 300), (1280, 470), (40, 560), (860, 640), (1560, 180), (560, 470)]
    o = []
    for k, (px, py) in enumerate(pts_):
        o.append(petal(u, px, py, prnd.uniform(6, 12) * (1.4 if py > 600 else 1), prnd.uniform(0, 360), f"{u}-pf {u}-pf{k%4}"))
    for (sx, sy, r) in [(1000, 640, 7), (1240, 560, 6), (1360, 740, 6), (1580, 760, 7), (612, 640, 6)]:
        o.append(N.sparkle(sx, sy, r, "#fffaf0", .95, f"{u}-tw"))
    sp, srnd = [], random.Random(41)
    for _ in range(16):
        sx, sy = srnd.uniform(700, 1560), srnd.uniform(240, 560)
        sp.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(srnd.uniform(1.2, 2.6))}" opacity="{n(srnd.uniform(.6, 1))}"/>')
    o.append(f'<g class="{u}-tw2" fill="{N.GOLD_L}">{"".join(sp)}</g>')
    return "".join(o)


def css(u):
    r = f"#{u}-root "
    return (f'<style>'
            f'{r}.{u}-tw{{animation:{u}tw 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}'
            f'{r}.{u}-tw:nth-of-type(3n){{animation-delay:-1.1s}}{r}.{u}-tw:nth-of-type(3n+1){{animation-delay:-2.2s}}'
            f'{r}.{u}-lg{{animation:{u}lg 2.6s ease-in-out infinite}}{r}.{u}-tw2{{animation:{u}gl 2.2s ease-in-out infinite}}'
            f'{r}.{u}-gl{{animation:{u}gl 3.4s ease-in-out infinite}}{r}.{u}-gl2{{animation:{u}gl 2.8s ease-in-out infinite -1s}}'
            f'{r}.{u}-pf{{animation:{u}pf 9s linear infinite;transform-box:fill-box;transform-origin:center}}'
            f'{r}.{u}-pf1{{animation-delay:-2.3s;animation-duration:11s}}{r}.{u}-pf2{{animation-delay:-4.6s;animation-duration:10s}}'
            f'{r}.{u}-pf3{{animation-delay:-6.9s;animation-duration:12s}}'
            f'@keyframes {u}tw{{0%,100%{{opacity:.95;transform:scale(1)}}50%{{opacity:.35;transform:scale(.6)}}}}'
            f'@keyframes {u}lg{{0%,100%{{opacity:1}}50%{{opacity:.62}}}}'
            f'@keyframes {u}gl{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}'
            f'@keyframes {u}pf{{0%{{transform:translate(0,0) rotate(0deg);opacity:1}}80%{{opacity:1}}'
            f'100%{{transform:translate(-70px,120px) rotate(300deg);opacity:0}}}}'
            f'@media (prefers-reduced-motion: reduce){{{r}*{{animation:none!important}}}}'
            f'</style>')


def card(u="nwa"):
    defs, out = scene(u)
    # chibi Hu Tao (official Genshin Impact emoji, (c) HoYoverse) winking from the jetty
    out.append(ART.place("hutao_wink", HT_X, H + 16, 480, f"{u}ht", shadow=("#6f5fc8", .35, 10), fade=(H - 40, H + 6)))
    out.append(corner_spray(u, random.Random(7)))
    out.append(drift(u))
    out.append(f'<rect width="{W}" height="{H}" fill="url(#{u}-vig)"/>')
    body = f'<g id="{u}-root">{css(u)}<defs>{"".join(defs)}</defs>{"".join(out)}</g>'
    body = re.sub(r'(?<=[ ,"(A-Za-z])(-?)0\.(\d)', r'\1.\2', body)  # 0.5 -> .5
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Anime illustration: chibi Hu Tao (official Genshin Impact emoji, © HoYoverse) winks from a lantern-lit jetty '
            f'over moonlit water, an academy hall glowing behind">'
            f'<defs><clipPath id="{u}-card"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath></defs>'
            f'<g clip-path="url(#{u}-card)">{body}</g></svg>')


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "card-nwa.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(card())
    return p


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "assets", "v12")
    p = build(out)
    print(p, os.path.getsize(p) // 1024, "KB")
