"""SIDERIUS scene: anime twilight over a rooftop observatory (full-bleed 1600x900).

    scene_siderius(x=0, y=0, s=1.0, uid="sd") -> str   # an SVG <g> fragment (defs inline)
    build_svg() -> str                                   # standalone SVG document
Drawing occupies (x, y) .. (x + 1600*s, y + 900*s). Empty character spot: x 560-1040, y 520-860.
Python 3 stdlib only. No text, no raster, no script. Palette avoids hue 70-192.
"""
import math
import os
import random

W, H = 1600, 900

# ---- palette (pastel anime twilight; no greens) ----
INK = "#3b3470"        # deep indigo ink (outline accents)
INK2 = "#5a4f9a"
SKY = ["#6f6cc0", "#8a82d2", "#a99be0", "#c9a9e2", "#eab3d2", "#f9c3c2", "#ffd6b8", "#ffe7c8"]
GOLD = "#ffd27a"
GOLD_L = "#fff1c4"
CREAM = "#fff7ea"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def sparkle(cx, cy, r, fill, op=1.0, cls=""):
    """4-point anime sparkle."""
    k = r * 0.22
    d = (f"M{f(cx)} {f(cy - r)} Q{f(cx + k)} {f(cy - k)} {f(cx + r)} {f(cy)} "
         f"Q{f(cx + k)} {f(cy + k)} {f(cx)} {f(cy + r)} Q{f(cx - k)} {f(cy + k)} {f(cx - r)} {f(cy)} "
         f"Q{f(cx - k)} {f(cy - k)} {f(cx)} {f(cy - r)}Z")
    c = f' class="{cls}"' if cls else ""
    o = f' opacity="{op}"' if op < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}{c}/>'


# ------------------------------------------------------------------ clouds
def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def cloud(uid, key, puffs, base_y, pal, light=(0.55, -0.8), drift=None, rim=None, belly=None):
    """Cel-shaded cumulus. puffs = [(cx, cy, r)], flat underside at base_y.
    Each puff is shaded on its own (back to front) so every bump gets a crisp
    cel edge.  pal = (shadow, mid, lit, highlight, underside)."""
    sh, mid, lit, hi, under = pal
    cid = f"{uid}cl{key}"
    lx, ly = light
    nrm = math.hypot(lx, ly)
    lx, ly = lx / nrm, ly / nrm
    minx = min(a - r for a, b, r in puffs) - 10
    maxx = max(a + r for a, b, r in puffs) + 10
    miny = min(b - r for a, b, r in puffs) - 10
    out = [f'<clipPath id="{cid}"><rect x="{f(minx)}" y="{f(miny)}" width="{f(maxx - minx)}" height="{f(base_y - miny)}"/></clipPath>']
    circ = "".join(f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r)}"/>' for a, b, r in puffs)
    out.append(f'<clipPath id="{cid}u">{circ}</clipPath>')
    layers = []
    order = sorted(puffs, key=lambda q: q[1] + q[2] * 0.3)  # higher puffs are further back
    top = min(b - r for a, b, r in puffs)
    span = max(1, base_y - top)
    mx_ = sum(a for a, b, r in puffs) / len(puffs)
    my_ = sum(b for a, b, r in puffs) / len(puffs)
    wid = max(1, (maxx - minx) / 2)
    # silhouette base: lit body; puffs are 2-tone (shade crescent + lit) with tones by height
    for i, (a, b, r) in enumerate(order):
        pid = f"{cid}p{i}"
        t = min(1, max(0, (base_y - b) / span))          # 0 bottom .. 1 top
        q = 0 if t < .3 else (.5 if t < .62 else 1)        # quantised = cel steps
        body = _mix(mid, lit, q)
        shade = _mix(body, _mix(under, sh, q), .7)
        side = ((a - mx_) * lx + (b - my_) * ly) / wid      # >0 faces the light
        if side < -0.28:                                     # big-form shadow side (hard step)
            body = _mix(body, shade, .5)
        jr = random.Random(int(a * 7 + b * 13))
        off, kk = jr.uniform(.06, .16), jr.uniform(.95, .99)
        out.append(f'<clipPath id="{pid}"><circle cx="{f(a)}" cy="{f(b)}" r="{f(r)}"/></clipPath>')
        g = [f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r)}" fill="{shade}"/>']
        if rim or t > .3:  # rim light crescent on the sun-facing edge
            rimc = hi if rim else _mix(lit, hi, min(1, t * 1.2))
            g.append(f'<circle cx="{f(a + lx * r * (off + .1))}" cy="{f(b + ly * r * (off + .1))}" r="{f(r * kk)}" fill="{rimc}"/>')
            g.append(f'<circle cx="{f(a + lx * r * off)}" cy="{f(b + ly * r * off)}" r="{f(r * kk)}" fill="{body}"/>')
        else:
            g.append(f'<circle cx="{f(a + lx * r * .22)}" cy="{f(b + ly * r * .22)}" r="{f(r * .95)}" fill="{body}"/>')
        layers.append(f'<g clip-path="url(#{pid})">{"".join(g)}</g>')
    # flat, darker underside band with a gently waving top edge
    rnd = random.Random(sum(map(ord, key)))
    band = 16 + (maxx - minx) * 0.025
    pts = [f"M{f(minx)} {f(base_y + 2)}", f"L{f(minx)} {f(base_y - band)}"]
    xx = minx
    while xx < maxx:
        w = rnd.uniform(60, 120)
        pts.append(f"Q{f(xx + w / 2)} {f(base_y - band * rnd.uniform(1.2, 1.7))} {f(min(xx + w, maxx))} {f(base_y - band)}")
        xx += w
    pts.append(f"L{f(maxx)} {f(base_y + 2)}Z")
    layers.append(f'<path d="{" ".join(pts)}" fill="{belly or under}" opacity=".9"/>')
    anim = f' class="{drift}"' if drift else ""
    out.append(f'<g{anim}><g clip-path="url(#{cid})"><g clip-path="url(#{cid}u)">{"".join(layers)}</g></g></g>')
    return "".join(out)


def wisp(x, y, w, h, body, glow, top=None):
    """Long thin twilight streak: tapered band lighter than the sky, with a bright
    sun-lit underside line (sun is below the horizon)."""
    def sp(x0, y0, ww, hh):
        return (f"M{f(x0)} {f(y0 + hh * .6)} C{f(x0 + ww * .3)} {f(y0 + hh * .05)} {f(x0 + ww * .75)} {f(y0)} {f(x0 + ww)} {f(y0 + hh * .55)} "
                f"C{f(x0 + ww * .7)} {f(y0 + hh * .95)} {f(x0 + ww * .3)} {f(y0 + hh * 1.0)} {f(x0)} {f(y0 + hh * .6)}Z")
    h *= 2.2
    return (f'<path d="{sp(x, y, w, h)}" fill="{body}"/>'
            f'<path d="{sp(x + w * .12, y + h * .62, w * .8, h * .42)}" fill="{glow}"/>')


def gen_puffs(cx, base_y, width, height, n, seed):
    """Low cumulus bank: a row of base puffs plus a few upper puffs."""
    rnd = random.Random(seed)
    p = []
    k = max(3, int(width / 70))
    for i in range(k):
        t = i / (k - 1)
        x = cx - width / 2 + t * width
        bump = math.sin(t * math.pi)
        r = rnd.uniform(0.45, 0.7) * height * (0.55 + 0.45 * bump) * 0.6
        p.append((x + rnd.uniform(-12, 12), base_y - r * 0.55, r))
    for i in range(n):
        t = rnd.uniform(0.15, 0.85)
        bump = math.sin(t * math.pi)
        x = cx - width / 2 + t * width
        r = rnd.uniform(0.28, 0.48) * height * (0.6 + 0.4 * bump)
        y = base_y - r * 0.6 - bump * height * rnd.uniform(0.35, 0.75)
        p.append((x, y, r))
    return p


# ------------------------------------------------------------------ main scene
def scene_siderius(x=0, y=0, s=1.0, uid="sd"):
    u = uid
    rnd = random.Random(29)
    defs, sky, mid, fg = [], [], [], []

    # ---------------- sky gradient + sun glow
    stops = "".join(f'<stop offset="{f(o)}" stop-color="{c}"/>'
                    for o, c in zip((0, .16, .3, .43, .55, .66, .76, .84), SKY))
    defs.append(f'<linearGradient id="{u}sky" x1="0" y1="0" x2="0" y2="1">{stops}'
                f'<stop offset="1" stop-color="{SKY[-1]}"/></linearGradient>')
    defs.append(f'<radialGradient id="{u}sun" cx="1160" cy="610" r="560" gradientUnits="userSpaceOnUse">'
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

    # ---------------- faint milky way band above the constellation
    defs.append(f'<filter id="{u}mw" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>')
    sky.append(f'<g transform="rotate(-14 820 150)" opacity=".5">'
               f'<ellipse cx="820" cy="150" rx="720" ry="46" fill="#d9c8f4" filter="url(#{u}mw)"/>'
               f'<ellipse cx="900" cy="146" rx="420" ry="20" fill="#f3e2f6" filter="url(#{u}mw)"/></g>')
    mw = []
    for i in range(140):
        tt = rnd.uniform(-1, 1)
        px = 820 + tt * 700
        py = 150 + rnd.gauss(0, 20)
        ang = math.radians(-14)
        qx = 820 + (px - 820) * math.cos(ang) - (py - 150) * math.sin(ang)
        qy = 150 + (px - 820) * math.sin(ang) + (py - 150) * math.cos(ang)
        mw.append(f'<circle cx="{f(qx)}" cy="{f(qy)}" r="{rnd.choice((0.7, 0.9, 1.1, 1.4))}" fill="#fffaf0" opacity="{f(rnd.uniform(.3, .8))}"/>')
    sky.append(f'<g>{"".join(mw)}</g>')

    # ---------------- background stars (upper sky only)
    st = []
    for i in range(120):
        sx, sy = rnd.uniform(10, 1590), rnd.uniform(8, 380) ** 1.0
        if sy > 120 + 280 * (sx / 1600) and sx > 1000:  # keep off the tall cloud
            continue
        fade = max(0.0, 1 - sy / 400)
        r = rnd.choice((0.9, 1.1, 1.3, 1.6, 2.1))
        cls = f' class="{u}tw{i % 3}"' if i % 4 == 0 else ""
        st.append(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{r}" fill="#fffaf0" opacity="{f(0.35 + 0.6 * fade)}"{cls}/>')
    sky.append(f'<g>{"".join(st)}</g>')
    for i, (sx, sy, r) in enumerate(((95, 260, 9), (420, 64, 8), (760, 40, 7), (1010, 150, 6), (1530, 70, 9), (590, 210, 6))):
        sky.append(sparkle(sx, sy, r, "#fffaf0", .9, f"{u}tw{i % 3}"))

    # ---------------- light rays from the low sun
    rays = []
    for i, (a, w, op) in enumerate(((-170, 5, .12), (-152, 4, .09), (-136, 6, .13), (-117, 4, .09),
                                    (-100, 5, .12), (-84, 3, .08))):
        a1, a2 = math.radians(a - w / 2), math.radians(a + w / 2)
        R = 1300
        sx0, sy0 = 1160, 610
        rays.append(f'<path d="M{sx0} {sy0} L{f(sx0 + R * math.cos(a1))} {f(sy0 + R * math.sin(a1))} '
                    f'L{f(sx0 + R * math.cos(a2))} {f(sy0 + R * math.sin(a2))}Z" fill="url(#{u}ray)" opacity="{op}"/>')
    defs.append(f'<radialGradient id="{u}ray" cx="1160" cy="610" r="1150" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff8e6"/><stop offset=".55" stop-color="#fff0dc" stop-opacity=".6"/>'
                f'<stop offset="1" stop-color="#fff0dc" stop-opacity="0"/></radialGradient>')
    sky.append(f'<g class="{u}rays">{"".join(rays)}</g>')

    # ---------------- constellation = rising chart curve
    pts = []
    n = 9
    for i in range(n):
        t = i / (n - 1)
        px = 470 + t * 600
        py = 360 - 270 * (1 - math.exp(-3.0 * t)) / (1 - math.exp(-3.0)) + (8 if i % 2 else -6) * (1 - t)
        pts.append((px, py))
    # faint "axis" stars
    ax = "".join(f'<circle cx="{f(470 + i * 75)}" cy="392" r="1.6" fill="#fffaf0" opacity=".45"/>' for i in range(9))
    ax += "".join(f'<circle cx="440" cy="{f(390 - i * 40)}" r="1.6" fill="#fffaf0" opacity=".45"/>' for i in range(8))
    sky.append(f'<g>{ax}</g>')
    line = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts)
    defs.append(f'<filter id="{u}glow" x="-20%" y="-20%" width="140%" height="140%">'
                f'<feGaussianBlur stdDeviation="5"/></filter>')
    sky.append(f'<path d="{line}" fill="none" stroke="#fff3c8" stroke-width="9" opacity=".35" filter="url(#{u}glow)"/>')
    sky.append(f'<path d="{line}" fill="none" stroke="#fffaf0" stroke-width="3" stroke-linejoin="round" '
               f'stroke-dasharray="1 0" opacity=".85" class="{u}draw"/>')
    for i, (a, b) in enumerate(pts):
        big = i in (0, 3, 6, 8)
        r = 15 if i == n - 1 else (11 if big else 7)
        sky.append(f'<circle cx="{f(a)}" cy="{f(b)}" r="{r * 1.6}" fill="#fff3c8" opacity=".35" filter="url(#{u}glow)"/>')
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
    PAL_FAR = ("#c3a2d8", "#ffd2cc", "#f6cfe2", "#fff4e6", "#d3a6d6")
    PAL = ("#9f8ad6", "#f4c6dc", "#d9c0ee", "#fff2ea", "#b394d6")
    PAL_WARM = ("#a48ed8", "#ffcdd0", "#e8c4ea", "#fff4e2", "#c69ad4")
    # far horizon cloud bank
    far = [(560, 528, 34), (615, 515, 48), (690, 506, 60), (780, 500, 66), (875, 503, 60), (960, 510, 52), (1035, 518, 42), (1090, 526, 30),
           (670, 462, 44), (750, 440, 60), (845, 446, 56), (925, 470, 42), (720, 392, 36), (790, 378, 42), (860, 402, 32)]
    sky.append(cloud(u, "far", far, 532, PAL_FAR, light=(0.5, 0.4), drift=f"{u}dr1", rim=True, belly="#f9cad2"))
    # tall cumulus tower on the right (hand-placed silhouette)
    tower = [(1170, 566, 56), (1250, 548, 84), (1360, 540, 110), (1490, 540, 100), (1600, 545, 90),
             (1240, 470, 62), (1330, 440, 104), (1470, 430, 118), (1600, 440, 86),
             (1300, 345, 66), (1395, 320, 96), (1520, 330, 86),
             (1360, 236, 64), (1450, 205, 90), (1560, 240, 64),
             (1420, 130, 54), (1490, 118, 46)]
    sky.append(cloud(u, "tow", tower, 596, PAL_WARM, light=(-0.9, 0.15), drift=f"{u}dr2", rim=True))
    # mid-left cloud behind observatory
    left = [(-20, 548, 80), (90, 530, 92), (215, 528, 84), (330, 540, 70), (420, 556, 48),
            (30, 440, 82), (150, 420, 86), (265, 452, 64),
            (90, 335, 60), (175, 340, 50)]
    sky.append(cloud(u, "lft", left, 580, PAL, light=(0.9, 0.1), drift=f"{u}dr1", rim=True))
    # thin twilight streaks
    sky.append(f'<g class="{u}dr2" opacity=".9">'
               + wisp(430, 446, 520, 20, "#f8c8d6", "#fff0de")
               + wisp(780, 478, 330, 14, "#fbcfd6", "#fff4e2")
               + wisp(560, 420, 220, 11, "#f2c2da", "#ffe8dc")
               + wisp(840, 300, 380, 16, "#c6aee8", "#efcde4")
               + wisp(1000, 330, 200, 11, "#cbb2ea", "#f2d0e2")
               + wisp(-60, 226, 360, 16, "#a998de", "#cdb6ea")
               + '</g>')

    # ---------------- distant town silhouette (two layers, lavender haze)
    def skyline(seed, y0, hmin, hmax, col, win, x0=-10, x1=1610):
        r2 = random.Random(seed)
        d = [f"M{x0} 700 L{x0} {y0}"]
        wins = []
        xx = x0
        while xx < x1:
            w = r2.uniform(30, 90)
            h = r2.uniform(hmin, hmax)
            top = y0 - h
            if r2.random() < 0.25:  # pitched roof
                d.append(f"L{f(xx)} {f(top + 10)} L{f(xx + w / 2)} {f(top - 8)} L{f(xx + w)} {f(top + 10)}")
            else:
                d.append(f"L{f(xx)} {f(top)} L{f(xx + w)} {f(top)}")
                if r2.random() < 0.18:
                    d.append(f"L{f(xx + w - 8)} {f(top)} L{f(xx + w - 8)} {f(top - 26)} L{f(xx + w - 10)} {f(top - 26)} L{f(xx + w - 10)} {f(top)}")
            if win:
                for _ in range(int(w * h / 900)):
                    if r2.random() < 0.55:
                        wx, wy = xx + r2.uniform(5, w - 9), top + r2.uniform(10, h - 4)
                        wins.append(f'<rect x="{f(wx)}" y="{f(wy)}" width="3.6" height="4.6" fill="{win}" opacity="{f(r2.uniform(.55, 1))}"/>')
            xx += w
        d.append(f"L{x1} 700Z")
        return f'<path d="{" ".join(d)}" fill="{col}"/>' + "".join(wins)

    mid.append(skyline(4, 600, 20, 60, "#c2b0e0", None))
    mid.append(skyline(9, 640, 30, 90, "#a593d4", "#ffe2a6"))
    for (wx, wy) in ((610, 548), (1236, 538)):
        mid.append(f'<g fill="#9585cd"><rect x="{wx - 14}" y="{wy}" width="28" height="22" rx="3"/>'
                   f'<path d="M{wx - 16} {wy} L{wx} {wy - 9} L{wx + 16} {wy}Z"/>'
                   f'<rect x="{wx - 11}" y="{wy + 22}" width="3" height="16"/><rect x="{wx + 8}" y="{wy + 22}" width="3" height="16"/></g>'
                   f'<rect x="{wx + 4}" y="{wy + 2}" width="6" height="18" fill="#b2a2dc" opacity=".6"/>')
    # tower crane / radio mast for depth
    mid.append(f'<path d="M1470 660 L1478 520 L1486 660Z" fill="#8f7fc6"/><circle cx="1478" cy="518" r="3.5" fill="#ff9fb8" class="{u}tw1"/>')
    # haze strip
    defs.append(f'<linearGradient id="{u}haze" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffe7d6" stop-opacity="0"/><stop offset="1" stop-color="#f6d3e4" stop-opacity=".7"/></linearGradient>')
    mid.append(f'<rect x="0" y="560" width="{W}" height="110" fill="url(#{u}haze)"/>')

    # ---------------- rooftop: parapet, railing, floor
    VPX, VPY = 800, 560
    defs.append(f'<linearGradient id="{u}floor" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#cdbbea"/><stop offset=".45" stop-color="#b9a5e0"/>'
                f'<stop offset="1" stop-color="#9c88d0"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}wall" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#a996d8"/><stop offset="1" stop-color="#8d7bc6"/></linearGradient>')
    floor_y = 712
    # parapet wall
    mid.append(f'<rect x="0" y="664" width="{W}" height="{floor_y - 664}" fill="url(#{u}wall)"/>')
    mid.append(f'<rect x="0" y="658" width="{W}" height="9" fill="#e9dcf6"/>')
    mid.append(f'<rect x="0" y="667" width="{W}" height="5" fill="#7d6cbc" opacity=".55"/>')
    # railing (thin, behind character spot; posts + two rails)
    rail = [f'<rect x="0" y="584" width="{W}" height="5" rx="2.5" fill="#f3e9fb"/>',
            f'<rect x="0" y="589" width="{W}" height="3" fill="#8e7cc8"/>',
            f'<rect x="0" y="622" width="{W}" height="3.5" rx="1.7" fill="#e6d8f4"/>']
    for px in range(20, 1600, 56):
        rail.append(f'<rect x="{px}" y="588" width="5" height="72" fill="#d9c9ef"/>'
                    f'<rect x="{px + 3}" y="588" width="2" height="72" fill="#8e7cc8" opacity=".6"/>')
    mid.append(f'<g>{"".join(rail)}</g>')
    # floor
    fg.append(f'<rect x="0" y="{floor_y}" width="{W}" height="{H - floor_y}" fill="url(#{u}floor)"/>')
    tiles = []
    for i in range(-14, 15):
        bx = VPX + i * 150
        # line from parapet line toward the bottom, aimed away from the vanishing point
        t0 = (floor_y - VPY) / (H - VPY)
        tiles.append(f'<path d="M{f(VPX + (bx - VPX) * t0)} {floor_y} L{f(bx)} {H}"/>')
    yy = floor_y
    gap = 16
    while yy < H:
        tiles.append(f'<path d="M0 {f(yy)} L{W} {f(yy)}"/>')
        yy += gap
        gap *= 1.32
    fg.append(f'<g stroke="#8b77c4" stroke-width="1.6" opacity=".45" fill="none">{"".join(tiles)}</g>')
    # parapet shadow on floor (hard cel shadow)
    fg.append(f'<path d="M0 {floor_y} L{W} {floor_y} L{W} {floor_y + 14} L0 {floor_y + 20}Z" fill="#8d7ac6" opacity=".45"/>')
    # sky-reflecting puddles (anime wet-rooftop look)
    defs.append(f'<linearGradient id="{u}pud" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffd6bf"/><stop offset=".5" stop-color="#eab3d2"/>'
                f'<stop offset="1" stop-color="#a99be0"/></linearGradient>')
    for (cx, cy, rx, ry) in ((1180, 842, 150, 22), (330, 812, 110, 14), (1460, 760, 70, 8)):
        fg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{u}pud)" opacity=".9"/>'
                  f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#fff3f2" stroke-width="2" opacity=".6"/>'
                  f'<path d="M{cx - rx * .55} {cy - ry * .25} L{cx + rx * .1} {cy - ry * .25}" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>'
                  f'<path d="M{cx + rx * .2} {cy + ry * .2} L{cx + rx * .45} {cy + ry * .2}" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".6"/>')
    # ground highlight for the character spot
    defs.append(f'<radialGradient id="{u}spot" cx="800" cy="800" r="300" gradientUnits="userSpaceOnUse" '
                f'gradientTransform="translate(0 600) scale(1 .25)">'
                f'<stop offset="0" stop-color="#fff6e0" stop-opacity=".95"/>'
                f'<stop offset=".45" stop-color="#ffe6d8" stop-opacity=".55"/>'
                f'<stop offset="1" stop-color="#ffe6d8" stop-opacity="0"/></radialGradient>')
    fg.append(f'<ellipse cx="800" cy="800" rx="320" ry="80" fill="url(#{u}spot)"/>')
    fg.append(f'<ellipse cx="800" cy="806" rx="150" ry="22" fill="#fffaf0" opacity=".35"/>')

    # ---------------- observatory dome (left)
    obs = []
    ox, oy = 245, 470     # dome centre
    R = 168
    wall_top, wall_bot = oy, 760
    # drum (cylinder) with cel shading: curved base, hard terminator bands, panel seams
    L, Rr = ox - R - 6, ox + R + 6
    drum = f"M{L} {wall_top} L{L} {wall_bot} A{R + 6} 22 0 0 0 {Rr} {wall_bot} L{Rr} {wall_top}Z"
    defs.append(f'<clipPath id="{u}drum"><path d="{drum}"/></clipPath>')
    seams = "".join(f'<rect x="{f(ox + (R + 6) * math.sin(math.radians(v)) - 1)}" y="{wall_top}" width="2.2" height="{wall_bot - wall_top + 30}" fill="#9a86d0" opacity=".35"/>'
                    for v in (-62, -38, -14, 14, 38, 62))
    obs.append(f'<g clip-path="url(#{u}drum)">'
               f'<rect x="{L}" y="{wall_top}" width="{Rr - L}" height="{wall_bot - wall_top + 30}" fill="#dccdf1"/>'
               f'<rect x="{L}" y="{wall_top}" width="{R * .62}" height="{wall_bot - wall_top + 30}" fill="#ae9adb"/>'
               f'<rect x="{L}" y="{wall_top}" width="{R * .22}" height="{wall_bot - wall_top + 30}" fill="#9d88d2"/>'
               f'<rect x="{ox + R * .5}" y="{wall_top}" width="{R * .5 + 6}" height="{wall_bot - wall_top + 30}" fill="#f3eafb"/>'
               f'<rect x="{ox + R * .74}" y="{wall_top}" width="12" height="{wall_bot - wall_top + 30}" fill="#fffaf2"/>'
               f'{seams}'
               # overhang shadow under the dome rim (hard, curved)
               f'<path d="M{L} {wall_top} L{Rr} {wall_top} L{Rr} {wall_top + 18} A{R + 6} 20 0 0 1 {L} {wall_top + 18}Z" fill="#8f7cc8" opacity=".55"/>'
               # base band
               f'<path d="M{L} {wall_bot - 26} A{R + 6} 22 0 0 0 {Rr} {wall_bot - 26} L{Rr} {wall_bot + 40} L{L} {wall_bot + 40}Z" fill="#8d7bc6" opacity=".45"/>'
               f'</g>')
    obs.append(f'<path d="M{ox - 40} {wall_bot} L{ox - 40} 600 Q{ox} 560 {ox + 40} 600 L{ox + 40} {wall_bot}Z" fill="#7d6bbd"/>'
               f'<path d="M{ox - 30} {wall_bot} L{ox - 30} 606 Q{ox} 574 {ox + 30} 606 L{ox + 30} {wall_bot}Z" fill="#ffe2a6"/>'
               f'<path d="M{ox - 30} {wall_bot} L{ox - 30} 606 Q{ox - 8} 584 {ox + 4} 588 L{ox + 4} {wall_bot}Z" fill="#ffd27a" opacity=".7"/>'
               f'<rect x="{ox - 32}" y="680" width="64" height="4" fill="#7d6bbd"/>')
    # round window
    obs.append(f'<circle cx="{ox + 110}" cy="560" r="24" fill="#7d6bbd"/><circle cx="{ox + 110}" cy="560" r="18" fill="#ffe2a6"/>'
               f'<path d="M{ox + 92} 560 L{ox + 128} 560 M{ox + 110} 542 L{ox + 110} 578" stroke="#7d6bbd" stroke-width="3"/>')
    # dome
    dome = f"M{ox - R} {oy} A{R} {R} 0 0 1 {ox + R} {oy}Z"
    defs.append(f'<clipPath id="{u}dome"><path d="{dome}"/></clipPath>')
    obs.append(f'<path d="{dome}" fill="#b6a2de"/>')
    obs.append(f'<g clip-path="url(#{u}dome)">'
               f'<ellipse cx="{ox + 70}" cy="{oy + 10}" rx="{R * 1.0}" ry="{R * 1.08}" fill="#e7dbf6"/>'
               f'<ellipse cx="{ox + 120}" cy="{oy - 10}" rx="{R * .62}" ry="{R * .9}" fill="#fbf4ff"/>'
               f'<path d="M{ox + 60} {oy - R + 30} Q{ox + 120} {oy - R + 40} {ox + 150} {oy - 60}" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" opacity=".9"/>'
               # ribs
               + "".join(f'<path d="M{ox + R * math.sin(a) * 1.0} {oy} Q{ox + R * math.sin(a) * 0.55} {oy - R * .95} {ox} {oy - R}" '
                         f'stroke="#9a86d0" stroke-width="2.5" fill="none" opacity=".55"/>'
                         for a in (math.radians(v) for v in (-70, -45, 45, 70)))
               + '</g>')
    # open slit with telescope
    slit_w = 54
    obs.append(f'<g clip-path="url(#{u}dome)"><rect x="{ox - slit_w / 2 + 10}" y="{oy - R - 4}" width="{slit_w}" height="{R + 4}" fill="#4d4290" '
               f'transform="rotate(18 {ox} {oy})"/>'
               f'<rect x="{ox - slit_w / 2 + 10}" y="{oy - R - 4}" width="{slit_w * .3}" height="{R + 4}" fill="#665aa8" '
               f'transform="rotate(18 {ox} {oy})"/>'
               f'<rect x="{ox - slit_w / 2 + 10 + slit_w * .55}" y="{oy - R * .55}" width="{slit_w * .22}" height="{R * .6}" fill="#ffd9a0" opacity=".9" '
               f'transform="rotate(18 {ox} {oy})"/></g>')
    # big telescope tube poking out toward the constellation
    tx, ty = ox + 40, oy - 80
    obs.append(f'<g transform="rotate(-38 {tx} {ty})">'
               f'<rect x="{tx}" y="{ty - 20}" width="190" height="40" rx="8" fill="#e6d8f6"/>'
               f'<rect x="{tx}" y="{ty + 4}" width="190" height="16" rx="6" fill="#a995da"/>'
               f'<rect x="{tx}" y="{ty - 16}" width="190" height="7" rx="3.5" fill="#fffaf3"/>'
               f'<rect x="{tx + 172}" y="{ty - 25}" width="30" height="50" rx="7" fill="#ffd27a"/>'
               f'<rect x="{tx + 172}" y="{ty + 6}" width="30" height="19" rx="5" fill="#e9ad5c"/>'
               f'<rect x="{tx + 178}" y="{ty - 21}" width="7" height="42" rx="3" fill="#fff1c4"/>'
               f'<rect x="{tx + 60}" y="{ty - 23}" width="14" height="46" rx="4" fill="#ffd27a"/>'
               f'<rect x="{tx + 60}" y="{ty + 6}" width="14" height="17" rx="4" fill="#e9ad5c"/>'
               f'</g>')
    # dome rim + finial
    obs.append(f'<path d="M{ox - R - 12} {oy - 8} A{R + 12} 14 0 0 0 {ox + R + 12} {oy - 8} L{ox + R + 12} {oy + 4} A{R + 12} 16 0 0 1 {ox - R - 12} {oy + 4}Z" fill="#ffd27a"/>'
               f'<path d="M{ox - R - 12} {oy + 1} A{R + 12} 16 0 0 0 {ox + R + 12} {oy + 1} L{ox + R + 12} {oy + 4} A{R + 12} 16 0 0 1 {ox - R - 12} {oy + 4}Z" fill="#e9ad5c"/>'
               f'<path d="M{ox - R - 12} {oy - 8} L{ox - R * .2} {oy + 6} L{ox - R * .2} {oy + 20} L{ox - R - 12} {oy + 4}Z" fill="#e9ad5c" opacity=".6"/>')
    # cast shadow of the building on the floor (hard cel shape, toward the left/away from sun)
    fg.append(f'<path d="M{ox - R - 10} {wall_bot} L{ox + R + 10} {wall_bot} L{ox + R - 60} {wall_bot + 40} L{ox - R - 120} {wall_bot + 40}Z" fill="#8a76c4" opacity=".5"/>')
    fg.append(f'<g>{"".join(obs)}</g>')

    # ---------------- small telescope on tripod (right)
    tsx, tsy = 1330, 690   # mount head
    tel = []
    leg = "#7d6bbd"
    tel.append(f'<ellipse cx="{tsx}" cy="815" rx="105" ry="12" fill="#8a76c4" opacity=".45"/>')
    for (lx, ly) in ((tsx - 78, 812), (tsx + 70, 815), (tsx + 6, 822)):
        tel.append(f'<path d="M{tsx} {tsy} L{lx} {ly}" stroke="{leg}" stroke-width="8" stroke-linecap="round"/>'
                   f'<path d="M{tsx - 1} {tsy} L{lx - 2} {ly}" stroke="#b9a6e4" stroke-width="2.5" stroke-linecap="round"/>')
    tel.append(f'<circle cx="{tsx}" cy="{tsy}" r="13" fill="{leg}"/><circle cx="{tsx + 3}" cy="{tsy - 3}" r="6" fill="#d8c8f2"/>')
    tel.append(f'<g transform="rotate(-32 {tsx} {tsy - 10})">'
               f'<rect x="{tsx - 70}" y="{tsy - 26}" width="170" height="30" rx="9" fill="#fbf2ff"/>'
               f'<rect x="{tsx - 70}" y="{tsy - 8}" width="170" height="12" rx="5" fill="#bfaae6"/>'
               f'<rect x="{tsx - 66}" y="{tsy - 22}" width="160" height="5" rx="2.5" fill="#fff"/>'
               f'<rect x="{tsx + 86}" y="{tsy - 31}" width="26" height="40" rx="6" fill="#f2a9c4"/>'
               f'<rect x="{tsx + 86}" y="{tsy - 6}" width="26" height="15" rx="5" fill="#d9849f"/>'
               f'<rect x="{tsx + 91}" y="{tsy - 27}" width="6" height="30" rx="3" fill="#ffe0ea"/>'
               f'<rect x="{tsx - 86}" y="{tsy - 20}" width="18" height="18" rx="4" fill="#7d6bbd"/>'
               f'<rect x="{tsx - 10}" y="{tsy - 30}" width="12" height="38" rx="3" fill="#ffd27a"/>'
               f'</g>')
    fg.append(f'<g>{"".join(tel)}</g>')

    # ---------------- string lights along the railing (catenaries)
    lights = []
    anchors = [(440, 560), (720, 600), (1000, 596), (1240, 580), (1600, 610)]
    k = 0
    bulbs = []
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        sag = 34
        mxp, myp = (x0 + x1) / 2, max(y0, y1) + sag
        lights.append(f'<path d="M{x0} {y0} Q{mxp} {myp + sag * .6} {x1} {y1}" stroke="#6e5fb0" stroke-width="2" fill="none"/>')
        for j in range(1, 6):
            t = j / 6
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mxp + t * t * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (myp + sag * .6) + t * t * y1
            col = (GOLD, "#ffb9cf", "#fff1c4")[k % 3]
            lights.append(f'<circle cx="{f(bx)}" cy="{f(by + 8)}" r="14" fill="{col}" opacity=".28" filter="url(#{u}glow)" class="{u}tw{k % 3}"/>'
                          f'<rect x="{f(bx - 1.5)}" y="{f(by - 1)}" width="3" height="5" fill="#6e5fb0"/>'
                          f'<circle cx="{f(bx)}" cy="{f(by + 8)}" r="5.5" fill="{col}"/>'
                          f'<circle cx="{f(bx - 1.6)}" cy="{f(by + 6.4)}" r="1.8" fill="#fff"/>')
            bulbs.append((bx, col))
            k += 1
    # wet-floor reflections of the bulbs (stretched vertical glints just below the parapet)
    refl = "".join(f'<rect x="{f(bx - 2.5)}" y="{floor_y + 6}" width="5" height="{26 + (j % 3) * 8}" rx="2.5" fill="{col}" opacity=".35"/>'
                   for j, (bx, col) in enumerate(bulbs))
    # long wet sheen streaks reflecting the sky glow
    refl += (f'<path d="M430 {floor_y + 28} H1180" stroke="#f6d2e2" stroke-width="5" stroke-linecap="round" opacity=".35"/>'
             f'<path d="M520 {floor_y + 40} H900" stroke="#ffe6d8" stroke-width="3" stroke-linecap="round" opacity=".35"/>'
             f'<path d="M960 {floor_y + 46} H1300" stroke="#f6d2e2" stroke-width="3" stroke-linecap="round" opacity=".3"/>')
    # sun reflection column on the wet floor
    defs.append(f'<linearGradient id="{u}sref" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#ffe9d2" stop-opacity=".75"/>'
                f'<stop offset="1" stop-color="#ffe0e6" stop-opacity="0"/></linearGradient>')
    refl += (f'<path d="M1135 {floor_y} L1185 {floor_y} L1215 {H} L1105 {H}Z" fill="url(#{u}sref)" opacity=".28"/>'
             + "".join(f'<path d="M{f(1160 - w)} {f(yy)} H{f(1160 + w)}" stroke="#fff4e4" stroke-width="{f(sw)}" stroke-linecap="round" opacity=".55"/>'
                       for yy, w, sw in ((724, 30, 3), (740, 46, 3), (762, 24, 2.5), (786, 56, 3.5), (818, 34, 3), (850, 70, 4))))
    fg.append(f'<g>{refl}</g>')
    fg.append(f'<g>{"".join(lights)}</g>')

    # ---------------- drifting sakura petals (cel: base + lighter half + notch)
    def petal(px, py, sz, rot, cls):
        d = (f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} "
             f"C{f(-sz * .75)} {f(sz * .3)} {f(-sz * .7)} {f(-sz * .8)} 0 {f(-sz)}Z")
        hl = f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} C{f(sz * .25)} {f(sz * .2)} {f(sz * .25)} {f(-sz * .5)} 0 {f(-sz)}Z"
        return (f'<g class="{cls}"><g transform="translate({f(px)} {f(py)}) rotate({rot})">'
                f'<path d="{d}" fill="#f7a9c4"/><path d="{hl}" fill="#ffd6e4"/>'
                f'<path d="M{f(-sz * .18)} {f(-sz * 1.02)} L0 {f(-sz * .72)} L{f(sz * .18)} {f(-sz * 1.02)}Z" fill="#f2b6dc"/>'
                f'</g></g>')
    pet = []
    for i, (px, py, sz, rot) in enumerate(((380, 205, 9, 30), (1120, 420, 11, -40), (470, 620, 8, 70), (1500, 640, 12, 15),
                                           (1220, 760, 10, -60), (470, 830, 13, 40), (1040, 880, 9, 100), (150, 860, 11, -20),
                                           (1560, 860, 10, 60), (660, 610, 7, -30))):
        pet.append(petal(px, py, sz * 1.7, rot, f"{u}pf{i % 3}"))
    fg.append("".join(pet))

    # ---------------- foreground sparkles / floating light motes
    motes = []
    for i, (mx2, my2, r) in enumerate(((560, 520, 6), (1080, 540, 8), (640, 700, 4), (1000, 690, 5),
                                       (500, 760, 5), (1120, 760, 4), (900, 470, 5), (700, 470, 4))):
        motes.append(sparkle(mx2, my2, r, GOLD_L, .9, f"{u}tw{i % 3}"))
    fg.append("".join(motes))

    # ---------------- soft vignette to keep focus centre
    defs.append(f'<radialGradient id="{u}vig" cx="800" cy="520" r="980" gradientUnits="userSpaceOnUse">'
                f'<stop offset=".62" stop-color="#5a4f9a" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="#5a4f9a" stop-opacity=".28"/></radialGradient>')
    fg.append(f'<rect width="{W}" height="{H}" fill="url(#{u}vig)"/>')

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
           f"@media (prefers-reduced-motion: reduce){{[class^='{u}'],[class*=' {u}']{{animation:none!important}}"
           f".{u}ss0,.{u}ss1,.{u}ss2{{opacity:1}}}}")
    clip = f'<clipPath id="{u}card"><rect width="{W}" height="{H}" rx="28"/></clipPath>'
    body = "".join(sky) + "".join(mid) + "".join(fg)
    tr = f' transform="translate({f(x)} {f(y)}) scale({s})"' if (x or y or s != 1) else ""
    return (f'<g{tr}><style>{css}</style><defs>{clip}{"".join(defs)}</defs>'
            f'<g clip-path="url(#{u}card)">{body}</g></g>')


def build_svg():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="Anime twilight sky over a rooftop observatory">'
            f'{scene_siderius()}</svg>')


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "scene_siderius.svg"), "w", encoding="utf-8") as fh:
        fh.write(build_svg())
    print("wrote scene_siderius.svg")
