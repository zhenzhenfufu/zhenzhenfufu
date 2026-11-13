"""v11 header: full-bleed anime dusk over calm water (1600x600).

Left ~60%: soft lavender->peach sky carrying the plain typeset intro.
Right: official chibi Furina (a Genshin Impact "Paimon's Paintings" emoji, (c) HoYoverse, embedded from
art/ by art.py) rising out of the water, a three-tier cel-shaded cumulus and a low sun with light rays.

    build(out_dir) -> path of the written header.svg
    python3 header.py [out_dir]          (default: <repo>/assets/v11)

Python 3 stdlib only. Scene helpers are imported read-only from scenes/.
"""
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import art as ART  # noqa: E402

OUT_DEFAULT = os.path.join(os.path.dirname(HERE), "assets", "v11")

U = "hd"                 # uid prefix for every id / class in this file
W, H, RX = 1600, 600, 28
HZ = 486                 # horizon / far water line
SUN = (1262, 486)        # low sun sitting on the horizon behind Furina

FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"

# ---- palette (pastel anime dusk; hues kept outside 70-192) ----
INK = "#2b2768"          # deep indigo (name)
INK_V = "#332e72"        # values
INK_T = "#3b3579"        # tagline
MUTE = "#6b5fa8"         # small caps line
PINK = "#d24f86"         # labels
SAKURA = "#e45f93"       # 王臻
CREAM = "#fff6ee"

# Furina placement
FX, FY, FH = 1296, 606, 470   # Furina sticker: bottom-centre anchor and drawn height

# text block
X0 = 72
VX = X0 + 112            # value column
ROW_FS = 24              # ~12.5 px at the README's ~830 px width
TAG_FS = 31
CAPS_FS = 20
Y_CAPS, Y_NAME, Y_TAG = 118, 210, 270
# one entry per text line: (label or "", value, baseline y); the long Now value wraps onto a 2nd line
ROW_LINES = None         # filled below from TEXT

TEXT = {
    "caps": "DATA SCIENCE · UC SAN DIEGO · CLASS OF 2029",
    "name": "Zhen Wang",
    "cn": "王臻",
    "tag": "I build AI agents — and the checks that keep them honest.",
    "rows": [("Now", ("Rare AI Lab (Prof. Aobo Li)", "SIDERIUS, an open-source auto-ML agent for science")),
             ("Before", "AI Agent Development Intern · Pfizer China R&D (2026)"),
             ("Also", "I make games · Night Water Academy 夜水书院 (UE5)")],
}
ROW_LINES = [("Now", TEXT["rows"][0][1][0], 340), ("", TEXT["rows"][0][1][1], 378),
             ("Before", TEXT["rows"][1][1], 420), ("Also", TEXT["rows"][2][1], 462)]


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sparkle(x, y, r, col="#fffaf0", op=1.0, cls=""):
    k = r * .2
    d = (f"M{n(x)} {n(y-r)} Q{n(x+k)} {n(y-k)} {n(x+r)} {n(y)} Q{n(x+k)} {n(y+k)} {n(x)} {n(y+r)} "
         f"Q{n(x-k)} {n(y+k)} {n(x-r)} {n(y)} Q{n(x-k)} {n(y-k)} {n(x)} {n(y-r)}Z")
    c = f' class="{cls}"' if cls else ""
    o = f' opacity="{op}"' if op < 1 else ""
    return f'<path{c} d="{d}" fill="{col}"{o}/>'


# ------------------------------------------------------------------ style
def style():
    a = U
    return (f'<style>'
            f'.{a}-f{{font-family:{FONT}}}'
            f'.{a}-anim{{transform-box:fill-box;transform-origin:center}}'
            f'@keyframes {a}-tw{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.3;transform:scale(.6)}}}}'
            f'@keyframes {a}-ray{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}'
            f'@keyframes {a}-dr{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(-10px)}}}}'
            f'@keyframes {a}-bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}'
            f'@keyframes {a}-gl{{0%,100%{{opacity:.95}}50%{{opacity:.35}}}}'
            f'@keyframes {a}-rp{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.6;transform:scale(1.05)}}}}'
            f'.{a}-tw{{animation:{a}-tw 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}'
            f'.{a}-tw2{{animation:{a}-tw 4.1s ease-in-out 1.3s infinite;transform-box:fill-box;transform-origin:center}}'
            f'.{a}-ray{{animation:{a}-ray 7s ease-in-out infinite}}'
            f'.{a}-dr{{animation:{a}-dr 26s ease-in-out infinite}}'
            f'.{a}-bob{{animation:{a}-bob 3.6s ease-in-out infinite}}'
            f'.{a}-bob2{{animation:{a}-bob 4.4s ease-in-out .9s infinite}}'
            f'.{a}-gl{{animation:{a}-gl 2.8s ease-in-out infinite}}'
            f'.{a}-gl2{{animation:{a}-gl 3.5s ease-in-out 1.1s infinite}}'
            f'.{a}-rp{{animation:{a}-rp 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}'
            f'@media (prefers-reduced-motion: reduce){{.{a}-tw,.{a}-tw2,.{a}-ray,.{a}-dr,.{a}-bob,.{a}-bob2,'
            f'.{a}-gl,.{a}-gl2,.{a}-rp{{animation:none}}}}'
            # the Salon emitters' second bubble starts with a +1.6s delay and a 0%-opacity keyframe, so it
            # would sit visible for 1.6s, blink out and restart: run it pre-advanced instead (selector is
            # more specific than the module's own rule; reduced-motion 'animation:none' still wins)
            + "".join(f'svg .{a}-{k}-up2{{animation-delay:-1.6s}}' for k in ("cm", "us", "cr"))
            + f'</style>')


# ------------------------------------------------------------------ defs
def defs():
    a = U
    sx, sy = SUN
    return (
        f'<clipPath id="{a}-card"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>'
        f'<clipPath id="{a}-sky"><rect width="{W}" height="{HZ}"/></clipPath>'
        f'<clipPath id="{a}-wat"><rect y="{HZ}" width="{W}" height="{H - HZ}"/></clipPath>'
        # dusk sky: periwinkle top -> lavender -> sakura -> peach at the horizon
        f'<linearGradient id="{a}-skyg" x1="0" y1="0" x2="0" y2="{HZ}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#a6a8ee"/><stop offset=".3" stop-color="#bdb2f1"/>'
        f'<stop offset=".58" stop-color="#e2bfec"/><stop offset=".8" stop-color="#f8cbdc"/>'
        f'<stop offset=".93" stop-color="#ffd9cf"/><stop offset="1" stop-color="#ffe6d2"/></linearGradient>'
        # warm sun bloom
        f'<radialGradient id="{a}-sun" cx="{sx}" cy="{sy}" r="560" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fffaf0" stop-opacity="1"/><stop offset=".08" stop-color="#fff0dc" stop-opacity=".95"/>'
        f'<stop offset=".3" stop-color="#ffd8cc" stop-opacity=".55"/><stop offset=".65" stop-color="#f6c6e0" stop-opacity=".18"/>'
        f'<stop offset="1" stop-color="#f6c6e0" stop-opacity="0"/></radialGradient>'
        # cool lavender in the top-left corner (keeps the text side calm and cool)
        f'<radialGradient id="{a}-cool" cx="0" cy="0" r="900" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#9aa0ea" stop-opacity=".55"/><stop offset="1" stop-color="#9aa0ea" stop-opacity="0"/></radialGradient>'
        # light rays
        f'<radialGradient id="{a}-rayg" cx="{sx}" cy="{sy}" r="1250" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fffbf2" stop-opacity=".95"/><stop offset=".45" stop-color="#fff4ec" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
        # water: reflected peach at the horizon, deepening to periwinkle at the bottom
        f'<linearGradient id="{a}-watg" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#ffdcd6"/><stop offset=".18" stop-color="#efc8e4"/>'
        f'<stop offset=".55" stop-color="#c8bdf0"/><stop offset="1" stop-color="#a5a9ea"/></linearGradient>'
        f'<radialGradient id="{a}-wsun" cx="{sx}" cy="{HZ}" r="420" gradientTransform="translate(0 {HZ}) scale(1 .45) translate(0 {-HZ})" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff4e2" stop-opacity=".95"/><stop offset=".4" stop-color="#ffe0d6" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="#ffe0d6" stop-opacity="0"/></radialGradient>'
        # soft veil behind the text (no edge)
        f'<radialGradient id="{a}-veil" cx="470" cy="300" r="560" gradientTransform="translate(470 300) scale(1 .5) translate(-470 -300)" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fffaf8" stop-opacity=".62"/><stop offset=".55" stop-color="#fff6f6" stop-opacity=".4"/>'
        f'<stop offset="1" stop-color="#fff6f6" stop-opacity="0"/></radialGradient>'
        # backlight halo behind Furina
        f'<radialGradient id="{a}-halo" cx="{FX - 6}" cy="{FY - 190}" r="230" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fffaf2" stop-opacity=".85"/><stop offset=".5" stop-color="#ffe9ec" stop-opacity=".4"/>'
        f'<stop offset="1" stop-color="#ffe9ec" stop-opacity="0"/></radialGradient>'
        # fade for reflections
        f'<linearGradient id="{a}-rfade" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity=".35"/></linearGradient>'
        f'<radialGradient id="{a}-core"><stop offset="0" stop-color="#ffffff"/><stop offset=".3" stop-color="#fff6e4" stop-opacity=".95"/>'
        f'<stop offset=".6" stop-color="#ffe6d6" stop-opacity=".45"/><stop offset="1" stop-color="#ffe6d6" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="{a}-flare" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff8ee" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".95"/>'
        f'<stop offset="1" stop-color="#fff8ee" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="{a}-glow"><stop offset="0" stop-color="#fff8f0" stop-opacity=".75"/>'
        f'<stop offset=".55" stop-color="#ffeef2" stop-opacity=".35"/><stop offset="1" stop-color="#ffeef2" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="{a}-drop" cx=".35" cy=".35" r=".8">'
        f'<stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="#cfe0ff"/><stop offset="1" stop-color="#8fb2f2"/></radialGradient>'
    )


# ------------------------------------------------------------------ sky
def wisp(x, y, w, h, body, glow, op=1.0):
    """Long thin anime dusk streak with a sun-lit underside."""
    def sp(x0, y0, ww, hh):
        return (f"M{n(x0)} {n(y0 + hh * .6)} C{n(x0 + ww * .3)} {n(y0 + hh * .05)} {n(x0 + ww * .75)} {n(y0)} "
                f"{n(x0 + ww)} {n(y0 + hh * .55)} C{n(x0 + ww * .7)} {n(y0 + hh * .95)} {n(x0 + ww * .3)} "
                f"{n(y0 + hh)} {n(x0)} {n(y0 + hh * .6)}Z")
    return (f'<g opacity="{op}"><path d="{sp(x, y, w, h)}" fill="{body}"/>'
            f'<path d="{sp(x + w * .1, y + h * .55, w * .82, h * .45)}" fill="{glow}"/></g>')


def rays():
    sx, sy = SUN
    o = []
    for ang, wd, ln, op in [(-170, 2.6, 1300, .5), (-158, 4.2, 1300, .42), (-146, 2.0, 1200, .5),
                            (-133, 5.0, 1100, .32), (-118, 2.2, 900, .4), (-104, 3.4, 800, .3),
                            (-88, 1.8, 700, .32), (-70, 3.0, 700, .28), (-52, 2.0, 600, .3)]:
        a0, a1 = math.radians(ang - wd / 2), math.radians(ang + wd / 2)
        p = [(sx + math.cos(a0) * 40, sy + math.sin(a0) * 40), (sx + math.cos(a0) * ln, sy + math.sin(a0) * ln),
             (sx + math.cos(a1) * ln, sy + math.sin(a1) * ln), (sx + math.cos(a1) * 40, sy + math.sin(a1) * 40)]
        o.append(f'<polygon points="{" ".join(f"{n(x)},{n(y)}" for x, y in p)}" fill="url(#{U}-rayg)" opacity="{op}"/>')
    return f'<g class="{U}-ray">{"".join(o)}</g>'


def far_hills():
    """Very faint distant islands on the horizon (depth cue that runs under the text side)."""
    rnd = random.Random(4)
    o = []
    for x0, x1, hmax, col, top in [(-20, 520, 22, "#d3c3ef", "#e6d8f6"), (380, 900, 14, "#dccbf1", "#ecdff7"),
                                   (1460, 1640, 26, "#cdbcec", "#e2d4f5")]:
        pts = [(x0, HZ + 1)]
        k = 9
        for i in range(k + 1):
            t = i / k
            bump = math.sin(t * math.pi) ** .7
            pts.append((x0 + (x1 - x0) * t, HZ - hmax * bump * rnd.uniform(.7, 1.05)))
        pts.append((x1, HZ + 1))
        d = "M" + " L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z"
        o.append(f'<path d="{d}" fill="{col}"/>')
        # lit top edge
        d2 = "M" + " L".join(f"{n(x)} {n(y)}" for x, y in pts[1:-1])
        o.append(f'<path d="{d2}" fill="none" stroke="{top}" stroke-width="2" stroke-linejoin="round" opacity=".9"/>')
    return "".join(o)


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


# ---- cumulus routine ported verbatim from card_siderius.py so the set shares one cloud look
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


def sd_cloud(u, key, masses, pal, light, drift=None, op=1.0, t1k=.2, t2k=.44):
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
            # (header change: no bounding-rect clip here, so the shadow never ends in a vertical seam)
            g.append(f'<g clip-path="url(#{prev}c)"><g fill="{c_sh}" opacity=".5">'
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
            return min(lim, contour(x) + hgt * t1k * (1 + .55 * side(x) * lx))

        def t2(x):
            return min(lim, contour(x) + hgt * t2k * (1 + .38 * side(x) * lx))
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



# pal = (shadow, body, lit, rim, underside, base glow)
PAL_TOW = ("#9d88d8", "#d7b8ea", "#ffd3e3", "#fff6ee", "#a68bd6", "#ffd3c4")   # a notch richer than SIDERIUS: paler sky here
PAL_SUB = ("#9580d4", "#bba3e6", "#d9bfef", "#f6e4f6", "#9c84d2", "#efc6dc")
PAL_FAR = ("#c3a7e0", "#e6c2ea", "#fdd3e2", "#fff3ee", "#cfa3d6", "#ffe0cf")


def clouds():
    """Cel-shaded cumulus (same routine as the SIDERIUS card). Returns (defs, body).
    Right of the sun: one wide cumulus in three tiers (crown, shoulder, low foot), lit from the
    low sun on its left so the shadow plane climbs on the right.  Left of the sun: a low,
    distant bank under the text side's horizon."""
    u = f"{U}-c"
    D, B = [], []
    base = HZ - 8
    far = [(blob(850, base, 250, 56, 41, lean=.2), base, .5),
           (blob(990, base, 230, 84, 42), base, .35)]
    d_, g_ = sd_cloud(u, "f", far, PAL_FAR, 0.6, drift=f"{U}-dr", op=.95)
    D.append(d_)
    B.append(g_)
    # lower step left of the sun (lit from the sun on its right), between the text and Furina
    shoulder = [(blob(1112, base, 300, 140, 61), base, .2)]
    d_, g_ = sd_cloud(u, "h", shoulder, PAL_TOW, 0.8, t1k=.24, t2k=.6)
    D.append(d_)
    hsub = [(blob(1060, base, 150, 74, 62), base, 0), (blob(1170, base, 120, 52, 63), base, 0)]
    d2_, g2_ = sd_cloud(u, "i", hsub, PAL_SUB, 0.8, t1k=.24, t2k=.6)
    D.append(d2_)
    B.append(f'{g_}<g clip-path="url(#{u}h0c)">{g2_}</g>')
    tower = [(blob(1476, 292, 270, 178, 11, lean=.1), 292, .8),
             (blob(1470, base, 480, 300, 12, lean=-.08), base, .3),
             (blob(1330, base, 200, 126, 14), base, 0)]
    tower[1][0][0].append((1650, 400, 110))
    d_, g_ = sd_cloud(u, "t", tower, PAL_TOW, -0.8, t2k=.52)
    D.append(d_)
    sub = [(blob(1560, base, 230, 150, 31, lean=.1), base, 0), (blob(1420, base, 170, 96, 32), base, 0)]
    d2_, g2_ = sd_cloud(u, "s", sub, PAL_SUB, -0.8, t2k=.52)
    D.append(d2_)
    B.append(f'{g_}<g clip-path="url(#{u}t1c)">{g2_}</g>')
    return "".join(D), f'<g id="{U}-cl">{"".join(B)}</g>'


def sky_layer():
    o = [f'<rect width="{W}" height="{HZ + 2}" fill="url(#{U}-skyg)"/>',
         f'<rect width="{W}" height="{HZ + 2}" fill="url(#{U}-cool)"/>',
         f'<rect width="{W}" height="{HZ + 2}" fill="url(#{U}-sun)"/>']
    # thin dusk streaks (upper sky, above the text block)
    for x, y, w, h, op in [(-40, 64, 420, 9, .9), (330, 102, 380, 7, .75), (690, 52, 300, 7, .7)]:
        o.append(wisp(x, y, w, h, "#d8c8f4", "#ffe6e6", op))
    o.append(rays())
    # first stars
    for x, y, r, cls in [(58, 40, 5, "tw"), (262, 30, 3.5, "tw2"), (590, 26, 4.5, "tw"), (930, 70, 4, "tw2"),
                         (1060, 34, 5.5, "tw"), (760, 140, 3, "tw2")]:
        o.append(sparkle(x, y, r, "#fffaf2", .95, f"{U}-{cls}"))
    return "".join(o)


# ------------------------------------------------------------------ water
def water(refl_ids):
    """Water plane: gradient, broken-mirror reflection of the sky group, sun glitter, ripple lines."""
    o = [f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#{U}-watg)"/>']
    # broken mirror reflection slices of the clouds / hills
    yy, i = HZ, 0
    sl, dfs = [], []
    while yy < H:
        hgt = 3.5 + (yy - HZ) / (H - HZ) * 14
        amp = .5 + (yy - HZ) / (H - HZ) * 7
        dx = amp * math.sin(i * 1.9) + amp * .4 * math.sin(i * .7 + 1)
        cid = f"{U}-ws{i}"
        dfs.append(f'<clipPath id="{cid}"><rect x="-20" y="{n(yy)}" width="{W + 40}" height="{n(hgt + .5)}"/></clipPath>')
        uses = f'<use href="#{U}-refl"/>'
        sl.append(f'<g clip-path="url(#{cid})"><g transform="translate({n(dx)},{2 * HZ}) scale(1,-1)">{uses}</g></g>')
        yy += hgt
        i += 1
    o.append(f'<g opacity=".42">{"".join(sl)}</g>')
    o.append(f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#{U}-wsun)"/>')
    # horizon shine
    o.append(f'<rect x="0" y="{HZ - .8}" width="{W}" height="1.8" fill="#fff4ee" opacity=".9"/>')
    o.append(f'<rect x="{SUN[0] - 420}" y="{HZ - 2}" width="840" height="4" rx="2" fill="url(#{U}-flare)"/>')
    # ripple lines: short pale strokes, denser near the horizon
    rnd = random.Random(21)
    rl = []
    for k in range(58):
        t = rnd.random() ** 1.6
        y = HZ + 4 + t * (H - HZ - 8)
        x = rnd.uniform(-20, W)
        w = 14 + t * 70 * rnd.uniform(.5, 1.2)
        th = .9 + t * 1.6
        rl.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(th)}" rx="{n(th / 2)}" fill="#fffaf6" opacity="{n(.35 + .3 * (1 - t))}"/>')
    o.append("".join(rl))
    # darker periwinkle ripple shadows (cel underside of each wavelet)
    sh = []
    for k in range(26):
        t = rnd.random() ** 1.3
        y = HZ + 8 + t * (H - HZ - 10)
        x = rnd.uniform(-20, W)
        w = 20 + t * 90 * rnd.uniform(.5, 1.1)
        sh.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(1 + t * 1.6)}" rx="1" fill="#8f91dc" opacity=".22"/>')
    o.append("".join(sh))
    # sun glitter column under the sun (broken gold/cream slices)
    sx = SUN[0]
    gl = []
    yy, i = HZ + 3, 0
    while yy < H:
        t = (yy - HZ) / (H - HZ)
        w = 18 + t * 120 * (.55 + .45 * math.sin(i * 2.3) ** 2)
        x = sx - w / 2 + 14 * math.sin(i * 1.7)
        hh = 1.6 + t * 3
        col = "#fff6dc" if i % 3 else "#ffe2a8"
        cls = f' class="{U}-gl"' if i % 2 else f' class="{U}-gl2"'
        gl.append(f'<rect{cls} x="{n(x)}" y="{n(yy)}" width="{n(w)}" height="{n(hh)}" rx="{n(hh / 2)}" fill="{col}"/>')
        yy += hh + 3 + t * 6
        i += 1
    o.append("".join(gl))
    # a few calm glints on the open water under the text side
    for x, y, r, cls in [(150, 534, 5, "tw"), (402, 512, 4, "tw2"), (640, 556, 5.5, "tw2"), (868, 526, 4, "tw"),
                         (1010, 586, 4.5, "tw")]:
        o.append(sparkle(x, y, r, "#ffffff", .9, f"{U}-{cls}"))
    dfs.append(f'<g id="{U}-refl">' + "".join(f'<use href="#{r}"/>' for r in refl_ids) + '</g>')
    return "".join(dfs), "".join(o)


def ripple_rings(cx, cy, rx, k=3, op=1.0):
    """Cel ripple rings on the water around a standing / landing figure."""
    o = []
    for i in range(k):
        r = rx * (1 + i * .55)
        ry = r * .15
        o.append(f'<ellipse cx="{n(cx)}" cy="{n(cy + 1.5)}" rx="{n(r)}" ry="{n(ry)}" fill="none" stroke="#7f7fd0" '
                 f'stroke-width="{n(2.2 - i * .4)}" opacity="{n((.32 - i * .07) * op)}"/>')
        o.append(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r)}" ry="{n(ry)}" fill="none" stroke="#ffffff" '
                 f'stroke-width="{n(2.4 - i * .5)}" opacity="{n((.9 - i * .25) * op)}"/>')
    return f'<g class="{U}-rp">{"".join(o)}</g>'


def droplet(x, y, r, rot=0, cls=""):
    """Anime water droplet: teardrop with cel shadow, outline and a hard white glint."""
    c = f' class="{cls}"' if cls else ""
    d = (f"M0 {n(-r * 1.9)} C{n(r * .35)} {n(-r * 1.2)} {n(r)} {n(-r * .55)} {n(r)} 0 "
         f"A{n(r)} {n(r)} 0 0 1 {n(-r)} 0 C{n(-r)} {n(-r * .55)} {n(-r * .35)} {n(-r * 1.2)} 0 {n(-r * 1.9)}Z")
    return (f'<g transform="translate({n(x)},{n(y)}) rotate({rot})"><g{c}>'
            f'<path d="{d}" fill="url(#{U}-drop)" stroke="#4a54a8" stroke-width="{n(max(1, r * .16))}"/>'
            f'<path d="M{n(r * .15)} {n(r * .2)} A{n(r * .78)} {n(r * .78)} 0 0 1 {n(-r * .7)} {n(r * .05)} '
            f'A{n(r * .9)} {n(r * .9)} 0 0 0 {n(r * .15)} {n(r * .2)}Z" fill="#7fa1ec" opacity=".55"/>'
            f'<ellipse cx="{n(-r * .38)}" cy="{n(-r * .35)}" rx="{n(r * .2)}" ry="{n(r * .36)}" transform="rotate(25 {n(-r * .38)} {n(-r * .35)})" fill="#fff"/>'
            f'<circle cx="{n(r * .4)}" cy="{n(r * .25)}" r="{n(r * .1)}" fill="#fff"/>'
            f'</g></g>')


def splash(cx, cy, s=1.0):
    """Little crown splash at a boot: a few droplets kicked up plus a bright crescent."""
    o = [f'<path d="M{n(cx - 26 * s)} {n(cy)} Q{n(cx - 20 * s)} {n(cy - 12 * s)} {n(cx - 12 * s)} {n(cy - 4 * s)} '
         f'Q{n(cx - 6 * s)} {n(cy - 16 * s)} {n(cx)} {n(cy - 5 * s)} Q{n(cx + 7 * s)} {n(cy - 15 * s)} {n(cx + 13 * s)} {n(cy - 4 * s)} '
         f'Q{n(cx + 21 * s)} {n(cy - 12 * s)} {n(cx + 27 * s)} {n(cy)} Z" fill="#f4f1ff" stroke="#5b62b8" stroke-width="1.3" '
         f'stroke-linejoin="round" opacity=".92"/>']
    return "".join(o)


# ------------------------------------------------------------------ text
def text_block():
    rows = []
    for lab, val, y in ROW_LINES:
        if lab:
            rows.append(f'<text x="{X0}" y="{y}" font-size="{ROW_FS}" font-weight="700" fill="{PINK}" letter-spacing=".3">{esc(lab)}</text>')
        rows.append(f'<text x="{VX}" y="{y}" font-size="{ROW_FS}" font-weight="500" fill="{INK_V}">{esc(val)}</text>')
    return (f'<g class="{U}-f" font-family="{FONT}">'
            f'<text x="{X0 + 2}" y="{Y_CAPS}" font-size="{CAPS_FS}" font-weight="700" letter-spacing="3" fill="{MUTE}">{esc(TEXT["caps"])}</text>'
            f'<text x="{X0 - 4}" y="{Y_NAME}" font-size="88" font-weight="800" letter-spacing="-1.5" fill="{INK}">{esc(TEXT["name"])}'
            f'<tspan dx="26" font-size="54" font-weight="700" letter-spacing="3" fill="{SAKURA}">{esc(TEXT["cn"])}</tspan></text>'
            f'<text x="{X0}" y="{Y_TAG}" font-size="{TAG_FS}" font-weight="500" fill="{INK_T}">{esc(TEXT["tag"])}</text>'
            + "".join(rows) + '</g>')


# ------------------------------------------------------------------ cast
def cast():
    """Official chibi Furina emoji (HoYoverse) rising out of the dusk water on the right, with sparkles and droplets."""
    o = []
    # backlight halo so the navy coat separates from the warm sky
    o.append(f'<ellipse cx="{FX}" cy="{FY - 250}" rx="300" ry="280" fill="url(#{U}-halo)"/>')
    o.append(ART.place("furina_scroll", FX, FY, FH, f"{U}-fu", shadow=("#6f5fc8", .35, 10), fade=(FY - 70, FY - 4)))
    for x, y, r, rot, cls in [(1030, 300, 6.5, -14, "bob"), (1060, 220, 4.5, 10, "bob2"), (1018, 450, 5, -20, "bob2"),
                              (1560, 270, 5.5, 18, "bob"), (1540, 400, 4.2, 8, "bob2")]:
        o.append(droplet(x, y, r, rot, f"{U}-{cls}"))
    for x, y, r, col, cls in [(1050, 160, 7, "#ffffff", "tw"), (1560, 150, 8, "#ffe6a8", "tw2"), (1470, 60, 6, "#ffffff", "tw"),
                              (1580, 480, 6, "#ffd0e0", "tw2"), (1010, 400, 5, "#ffffff", "tw2")]:
        o.append(sparkle(x, y, r, col, 1, f"{U}-{cls}"))
    return "".join(o)


def reflections():
    return ""


# ------------------------------------------------------------------ document
def svg():
    cd, cb = clouds()
    sky_art = f'<g id="{U}-hills">{far_hills()}</g>{cb}'
    wd, wb = water([f"{U}-hills", f"{U}-cl"])
    title = "Zhen Wang 王臻 — Data Science · UC San Diego · Class of 2029"
    desc = ("I build AI agents — and the checks that keep them honest. "
            "Now: Rare AI Lab (Prof. Aobo Li) · SIDERIUS, an open-source auto-ML agent for science. "
            "Before: AI Agent Development Intern · Pfizer China R&D (2026). "
            "Also: I make games · Night Water Academy 夜水书院 (UE5). "
            "Illustration: chibi Furina (an official Genshin Impact emoji, © HoYoverse) rising out of calm dusk water under cel-shaded clouds.")
    body = [
        # the low sun: its bloom bleeds over the cloud bases on the horizon behind Furina
        f'<g clip-path="url(#{U}-sky)">{sky_layer()}{sky_art}'
        f'<ellipse cx="{SUN[0]}" cy="{SUN[1]}" rx="160" ry="120" fill="url(#{U}-core)" opacity=".9"/></g>',
        f'<g clip-path="url(#{U}-wat)">{wb}{reflections()}</g>',
        f'<rect width="{W}" height="{H}" fill="url(#{U}-veil)"/>',
        cast(),
        text_block(),
    ]
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-labelledby="{U}-title {U}-desc">'
            f'<title id="{U}-title">{esc(title)}</title><desc id="{U}-desc">{esc(desc)}</desc>'
            f'{style()}<defs>{defs()}{cd}{wd}</defs>'
            f'<g clip-path="url(#{U}-card)">{"".join(body)}</g></svg>')
    return re.sub(r">\s+<", "><", doc)          # drop inter-tag whitespace from the imported modules


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "header.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(svg())
    return p


if __name__ == "__main__":
    out = build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)
    print(out, os.path.getsize(out) // 1024, "KB")
