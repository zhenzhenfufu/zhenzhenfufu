"""Chibi Keqing (刻晴) fan art as pure SVG, cel-shaded anime style.

    keqing(x, y, scale=1, uid='kq', pose='stand', flip=False, target=None) -> str  (an SVG <g> fragment)

(x, y) is the ground point between her feet.  Bounding box at scale 1 relative to (x, y),
measured from a render (includes blade glow, sparks and the ground shadow; multiply by scale):
    pose='stand' : x in [-141, 141], y in [-268, 8]
    pose='bust'  : x in [-141, 141], y in [-268, -66]  (head + shoulders fading out, for small slots)
    pose='point' : x in [-160, 168], y in [-265, 9]   (default aim; with target= the +x edge is
                   ~142 for a near-vertical blade).  Action pose: 3/4 turn toward +x, leaning into a
                   step, sword arm thrust diagonally up/out, fist at chest, back foot kicked up,
                   twin tails swept toward -x, closed-mouth smile.  target=(px, py) (page coords)
                   aims the blade so its tip line passes through that point.
flip=True mirrors her horizontally about x (stand/bust bboxes are symmetric to within 1 px; the
point bbox mirrors with her).
Twin tails are separate wavy locks (two-tone violet, jagged lilac highlight bands, thin rim light);
she holds a slim glowing lightning stiletto in a gloved hand, the other gloved hand on her hip.
All ids/classes are prefixed with `uid`; give each instance a distinct uid.  CSS animation (tail sway,
blade glow pulse, spark flicker/twinkle) stops under prefers-reduced-motion.
Run as a script to write the 600x600 showcase to the scratchpad (never into the repo).
Original non-commercial fan art; no official art used or traced.
"""
import os

INK = "#3a2766"        # line art: deep indigo ink
INK_SOFT = "#5a4290"
HAIR = "#8a6cdc"
HAIR_SH = "#5e45aa"
HAIR_SH2 = "#4a3492"
HAIR_HI = "#b7a2f6"
HAIR_RIM = "#e6dcff"
HAIR_LILAC = "#ddd0ff"
SKIN = "#fff0e6"
SKIN_SH = "#f6cfc6"
BLUSH = "#ff9fb8"
WHITE = "#fdfbff"
WHITE_SH = "#ddd3f3"
PURP = "#4f49a8"
PURP_SH = "#3c3787"
PURP_HI = "#7f7ad6"
GOLD = "#f1cd78"
GOLD_SH = "#c99a44"
TIGHTS = "#463f86"
TIGHTS_HI = "#7a69b8"
ELEC = "#c8a6ff"
ELEC_CORE = "#f7f0ff"
ELEC_DEEP = "#8b5cf0"


def _p(d, fill, stroke=INK, sw=2.2, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s}{extra}/>'


def _shaded(uid, name, d, base, shadows=(), lights=(), sw=2.2, stroke=INK):
    """Base shape + hard-edged shadow/highlight shapes clipped to it + outline on top."""
    cid = f"{uid}-c-{name}"
    out = [f'<clipPath id="{cid}"><path d="{d}"/></clipPath>', _p(d, base, stroke=None)]
    inner = "".join(_p(sd, sf, stroke=None) for sd, sf in list(shadows) + list(lights))
    if inner:
        out.append(f'<g clip-path="url(#{cid})">{inner}</g>')
    out.append(_p(d, "none", stroke=stroke, sw=sw))
    return "".join(out)


def _mirror(d):
    """Mirror a path of absolute M/L/C/Q/Z commands across x=0."""
    toks = d.replace(",", " ").split()
    out, i, cmd, k = [], 0, None, 0
    for t in toks:
        if t.isalpha():
            out.append(t); cmd = t; k = 0
        else:
            v = float(t)
            if k % 2 == 0:
                v = -v
            out.append(f"{v:g}"); k += 1
    return " ".join(out)


def _shift(d, dx, dy):
    toks = d.replace(",", " ").split()
    out, k = [], 0
    for t in toks:
        if t.isalpha():
            out.append(t); k = 0
        else:
            out.append(f"{float(t) + (dx if k % 2 == 0 else dy):g}"); k += 1
    return " ".join(out)


def _n(v):
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else (s[:-2] if s.endswith(".0") else s)


def _spline(ctrl, n=34):
    """Uniform Catmull-Rom through ctrl points -> n+1 evenly-parametrised samples."""
    import math
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    segs = len(ctrl) - 1
    out = []
    for k in range(n + 1):
        u = k / n * segs
        i = min(int(u), segs - 1)
        t = u - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        t2, t3 = t * t, t * t * t
        out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out


def _normals(pts):
    import math
    out = []
    for i in range(len(pts)):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, len(pts) - 1)]
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
        out.append((-dy / L, dx / L))
    return out


def _smooth_closed(poly):
    """Closed polygon -> smooth path (quadratic through edge midpoints); first/sharp points kept."""
    m = [((poly[i][0] + poly[(i + 1) % len(poly)][0]) / 2, (poly[i][1] + poly[(i + 1) % len(poly)][1]) / 2)
         for i in range(len(poly))]
    d = [f"M {_n(m[-1][0])} {_n(m[-1][1])}"]
    for i in range(len(poly)):
        d.append(f"Q {_n(poly[i][0])} {_n(poly[i][1])} {_n(m[i][0])} {_n(m[i][1])}")
    return " ".join(d) + " Z"


def _band(pts, nrm, lo, hi, t0=0.0, t1=1.0, smooth=True):
    """Ribbon between offsets lo(t)..hi(t) (functions of t in [0,1], along the +normal) for t0..t1."""
    n = len(pts) - 1
    idx = [i for i in range(n + 1) if t0 - 1e-9 <= i / n <= t1 + 1e-9]
    a = [(pts[i][0] + nrm[i][0] * hi(i / n), pts[i][1] + nrm[i][1] * hi(i / n)) for i in idx]
    b = [(pts[i][0] + nrm[i][0] * lo(i / n), pts[i][1] + nrm[i][1] * lo(i / n)) for i in idx]
    poly = a + b[::-1]
    if smooth:
        return _smooth_closed(poly)
    return "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in poly) + " Z"


def _at(pts, nrm, w, t, o):
    """Point at parameter t (0..1 along the lock) and offset o (fraction of the half-width, + = outer)."""
    n = len(pts) - 1
    u = min(max(t, 0), 1) * n
    i = min(int(u), n - 1); f = u - i
    x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
    y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
    nx = nrm[i][0] + (nrm[i + 1][0] - nrm[i][0]) * f
    ny = nrm[i][1] + (nrm[i + 1][1] - nrm[i][1]) * f
    ww = w(t) * o
    return (x + nx * ww, y + ny * ww)


def _jag_band(pts, nrm, w, a, b, olo, ohi, teeth=3):
    """Anime hair highlight: a band across the lock between t=a..b whose two ends are saw-toothed
    (sharp spikes pointing along the hair), outer side longer than the inner side."""
    span = b - a
    poly = []
    # top edge, outer -> inner, teeth pointing up the lock
    for j in range(teeth * 2 + 1):
        o = ohi - (ohi - olo) * j / (teeth * 2)
        lean = 0.12 * span * (1 - j / (teeth * 2))          # outer teeth reach further
        poly.append(_at(pts, nrm, w, a - lean + (0.0 if j % 2 == 0 else 0.3 * span), o))
    for k in range(1, 4):                                     # inner side
        poly.append(_at(pts, nrm, w, a + 0.3 * span + (span * 0.38) * k / 4, olo))
    # bottom edge, inner -> outer, teeth pointing down the lock
    for j in range(teeth * 2 + 1):
        o = olo + (ohi - olo) * j / (teeth * 2)
        lean = 0.1 * span * (j / (teeth * 2))
        poly.append(_at(pts, nrm, w, b + lean - (0.0 if j % 2 == 0 else 0.32 * span), o))
    for k in range(3, 0, -1):                                 # outer side
        poly.append(_at(pts, nrm, w, a + 0.3 * span + (span * 0.4) * k / 4, ohi))
    return "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in poly) + " Z"


def _strand(uid, name, ctrl, w0, fill, tone=0, bands=(), rim=True, lw=(2.6, 1.4), n=20):
    """One cel-shaded hair lock along a wavy centreline.
    +normal side is the OUTER (rim-lit) edge, -normal side the inner (shadow) edge.
    Ink outline is an underlay ribbon, thicker on the shadow side and tapering to nothing at the tip.
    bands: [(t0, t1, centre_offset_frac, half_width_frac)] lighter lilac highlight bands (spindle shaped)."""
    import math
    pts = _spline(ctrl, n)
    nrm = _normals(pts)

    def w(t):
        return w0 * max(0.0, 1 - t ** 3.2) * (0.84 + 0.26 * math.sin(math.pi * min(t * 1.25, 1)))
    shape = _band(pts, nrm, lambda t: -w(t), lambda t: w(t))
    ink = _band(pts, nrm, lambda t: -w(t) - lw[0] * (1 - t) ** 0.8, lambda t: w(t) + lw[1] * (1 - t) ** 0.8)
    cid = f"{uid}-c-{name}"
    sh_col, sh2_col = (HAIR_SH, HAIR_SH2) if tone == 0 else (HAIR_SH2, "#3f2c80")
    # hard-edged inner shadow with a wavy terminator
    cp = _spline(ctrl, 12); cn = _normals(cp)          # coarser sampling is plenty for the terminators
    shadow = _band(cp, cn, lambda t: -w(t) - 4,
                   lambda t: w(t) * (-0.18 + 0.32 * math.sin(t * 9.0 + 0.6)))
    deep = _band(cp, cn, lambda t: -w(t) - 4, lambda t: -w(t) * 0.62, 0.0, 1.0)
    inner = [_p(shadow, sh_col, stroke=None), _p(deep, sh2_col, stroke=None)]
    for (a, b, c, hw) in bands:
        inner.append(_p(_jag_band(pts, nrm, w, a, b, c - hw, c + hw), HAIR_HI, stroke=None))
        m = (b - a) * 0.2
        inner.append(_p(_jag_band(pts, nrm, w, a + m, b - m, c - hw * 0.1, c + hw * 0.7, teeth=2), HAIR_LILAC, stroke=None))
    for (a, b, c) in ((0.06, 0.5, 0.12), (0.4, 0.88, -0.28)):   # thin strand-flow lines
        q = [_at(pts, nrm, w, a + (b - a) * k / 8, c) for k in range(9)]
        d = f"M {_n(q[0][0])} {_n(q[0][1])} " + " ".join(
            f"Q {_n(q[k][0])} {_n(q[k][1])} {_n((q[k][0] + q[k + 1][0]) / 2)} {_n((q[k][1] + q[k + 1][1]) / 2)}"
            for k in range(1, 8)) + f" L {_n(q[8][0])} {_n(q[8][1])}"
        inner.append(_p(d, "none", stroke=INK_SOFT, sw=1.0, extra=' opacity=".55"'))
    if rim:
        inner.append(_p(_band(pts, nrm, lambda t: w(t) - 1.9 * (1 - t), lambda t: w(t) + 2, 0.04, 0.86),
                        HAIR_RIM, stroke=None))
    return (_p(ink, INK, stroke=None)
            + f'<clipPath id="{cid}"><path d="{shape}"/></clipPath>'
            + _p(shape, fill, stroke=None)
            + f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')


FRONT_HAIR = ("M -64 -168 C -70 -212 -38 -244 0 -244 C 38 -244 70 -212 64 -168 "
              "C 66 -148 62 -126 52 -104 C 50 -124 46 -140 41 -150 "
              "C 40 -158 36 -164 32 -168 Q 30 -160 24 -152 Q 22 -166 16 -176 Q 13 -162 6 -150 "
              "Q 4 -164 -2 -176 Q -6 -160 -14 -152 Q -14 -166 -20 -176 Q -24 -162 -32 -154 "
              "Q -32 -162 -36 -168 C -40 -160 -44 -150 -46 -140 C -48 -128 -50 -118 -52 -104 "
              "C -62 -126 -66 -148 -64 -168 Z")


def _sparkle(cx, cy, r, fill, cls=""):
    k = r * 0.22
    d = (f"M {cx} {cy-r} Q {cx+k} {cy-k} {cx+r} {cy} Q {cx+k} {cy+k} {cx} {cy+r} "
         f"Q {cx-k} {cy+k} {cx-r} {cy} Q {cx-k} {cy-k} {cx} {cy-r} Z")
    c = f' class="{cls}"' if cls else ""
    return f'<path d="{d}" fill="{fill}"{c}/>'


def _bolt(pts, uid, w=3.2, cls=""):
    """Tapered, filled lightning bolt along a zigzag polyline (thick at start, sharp at end)."""
    import math
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        ww = w * (1 - i / (n - 1)) + 0.3
        left.append((x + nx * ww, y + ny * ww)); right.append((x - nx * ww, y - ny * ww))
    poly = left + right[::-1]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in poly) + " Z"
    core = "M " + " L ".join(f"{x} {y}" for x, y in pts[:-1])
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c}><path d="{d}" fill="{ELEC}" stroke="{ELEC}" stroke-width="{w*2.2}" stroke-linejoin="round" '
            f'opacity=".55" filter="url(#{uid}-glow)"/>'
            f'<path d="{d}" fill="{ELEC_DEEP}" stroke="{ELEC_DEEP}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="{core}" fill="none" stroke="{ELEC_CORE}" stroke-width="{w*0.55:.2f}" stroke-linejoin="round" stroke-linecap="round"/></g>')


def _defs(uid):
    return f"""<defs>
<linearGradient id="{uid}-hairg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#7a5dd0"/><stop offset=".6" stop-color="{HAIR}"/><stop offset="1" stop-color="#ab92ee"/></linearGradient>
<linearGradient id="{uid}-tailg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#6c50c0"/><stop offset=".55" stop-color="{HAIR}"/><stop offset="1" stop-color="#c3aef6"/></linearGradient>
<linearGradient id="{uid}-iris" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#3b1f78"/><stop offset=".45" stop-color="#6a3fc0"/><stop offset="1" stop-color="#d2b6ff"/></linearGradient>
<linearGradient id="{uid}-blade" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0" stop-color="#7d4ff0"/><stop offset=".6" stop-color="#c9a8ff"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<radialGradient id="{uid}-blush" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{BLUSH}" stop-opacity=".75"/><stop offset="1" stop-color="{BLUSH}" stop-opacity="0"/></radialGradient>
<radialGradient id="{uid}-aura" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="#e7d8ff" stop-opacity=".95"/><stop offset=".5" stop-color="#c7a6ff" stop-opacity=".45"/><stop offset="1" stop-color="#c7a6ff" stop-opacity="0"/></radialGradient>
<filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4"/></filter>
</defs>"""


def _style(uid):
    return f"""<style>
.{uid}-fl{{animation:{uid}-fl 1.7s steps(1,end) infinite}}
.{uid}-fl2{{animation:{uid}-fl 1.7s steps(1,end) .55s infinite}}
.{uid}-tw{{transform-box:fill-box;transform-origin:center;animation:{uid}-tw 2.6s ease-in-out infinite}}
.{uid}-tw2{{transform-box:fill-box;transform-origin:center;animation:{uid}-tw 2.6s ease-in-out 1.3s infinite}}
.{uid}-swl{{transform-box:fill-box;animation:{uid}-swl 4s ease-in-out infinite}}
.{uid}-swr{{transform-box:fill-box;animation:{uid}-swr 4s ease-in-out -2s infinite}}
@keyframes {uid}-swl{{0%,100%{{transform:rotate(0deg)}}50%{{transform:rotate(1.6deg)}}}}
@keyframes {uid}-swr{{0%,100%{{transform:rotate(0deg)}}50%{{transform:rotate(-1.6deg)}}}}

.{uid}-gl{{animation:{uid}-gl 2.2s ease-in-out infinite}}
@keyframes {uid}-gl{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}
@keyframes {uid}-fl{{0%{{opacity:1}}40%{{opacity:.35}}55%{{opacity:1}}80%{{opacity:.7}}}}
@keyframes {uid}-tw{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(.55);opacity:.55}}}}
@media (prefers-reduced-motion: reduce){{.{uid}-fl,.{uid}-fl2,.{uid}-tw,.{uid}-tw2,.{uid}-swl,.{uid}-swr,.{uid}-gl{{animation:none}}}}
</style>"""


# ---------------------------------------------------------------- parts
# Left twin tail as separate wavy locks: (ctrl points, half-width, tone, highlight bands).
# Drawn back-to-front; the right tail is the mirror image.
TAIL_LOCKS = [
    # back lock (darker tone): peeks out between the body and the middle lock
    ([(-52, -206), (-74, -198), (-90, -172), (-94, -140), (-86, -110), (-80, -84), (-84, -58), (-90, -38), (-91, -20)],
     10, 1, [(0.54, 0.7, 0.25, 0.5)]),
    # middle lock, tip curling back inward
    ([(-54, -212), (-84, -206), (-104, -182), (-110, -148), (-100, -118), (-90, -92), (-94, -64), (-102, -42), (-106, -20)],
     12, 0, [(0.5, 0.68, 0.28, 0.52)]),
    # main outer lock: big S-wave, carries the strongest highlight bands
    ([(-54, -218), (-90, -214), (-114, -192), (-124, -158), (-114, -126), (-102, -100), (-106, -72), (-118, -46), (-123, -22)],
     14.5, 0, [(0.24, 0.42, 0.28, 0.58), (0.6, 0.74, 0.32, 0.48)]),
]


def _swept(ctrl, dx, dy):
    """Bend a lock's centreline as if blown: control point i moves by (dx, dy) * (i/(n-1))**1.5
    (the root stays pinned to the bun, the tip moves most)."""
    n = len(ctrl) - 1
    return [(x + dx * (i / n) ** 1.5, y + dy * (i / n) ** 1.5) for i, (x, y) in enumerate(ctrl)]


def _tail_locks(side, sweep):
    """TAIL_LOCKS for one side in left-side coordinates (the right side is mirrored after drawing).
    sweep > 0 swings both tails toward local -x (left tail flares out and lifts, right tail swings
    in behind her back); outer locks swing the most."""
    if not sweep:
        return TAIL_LOCKS
    out = []
    for k, (ctrl, w0, tone, bands) in enumerate(TAIL_LOCKS):
        f = 0.7 + 0.15 * k
        if side < 0:
            ctrl = _swept(ctrl, -38 * sweep * f, -26 * sweep * f)
        else:
            ctrl = _swept(ctrl, 34 * sweep * f, -8 * sweep * f)
        out.append((ctrl, w0, tone, bands))
    return out


def _tail_side(uid, side, sweep=0.0):
    out = []
    for k, (ctrl, w0, tone, bands) in enumerate(_tail_locks(side, sweep)):
        fn = _strand if side < 0 else _strand_m
        out.append(fn(uid, f"t{side}{k}", ctrl, w0, f"url(#{uid}-tailg)", tone, bands))
    return "".join(out)


def _strand_m(uid, name, ctrl, w0, fill, tone, bands):
    """Mirror image (across x=0) of the lock built on the left-side centreline `ctrl`."""
    import re
    frag = _strand(uid, name, ctrl, w0, fill, tone, bands)
    return re.sub(r' d="([^"]+)"', lambda m: f' d="{_mirror(m.group(1))}"', frag)


def _tails(uid, sweep=0.0):
    # pivot ~ the tail root next to the bun (fill-box percentages of each tail group's bbox)
    def origin(locks):
        xs = [x for c, *_ in locks for x, _ in c]
        ys = [y for c, *_ in locks for _, y in c]
        x0, x1, y0, y1 = min(xs) - 16, max(xs) + 6, min(ys) - 16, max(ys)
        return (-54 - x0) / (x1 - x0) * 100, (-214 - y0) / (y1 - y0) * 100
    lx, ly = origin(_tail_locks(-1, sweep))
    rx, ry = origin(_tail_locks(1, sweep))
    return (f'<g class="{uid}-swl" style="transform-origin:{lx:.0f}% {ly:.0f}%">' + _tail_side(uid, -1, sweep) + "</g>"
            + f'<g class="{uid}-swr" style="transform-origin:{100-rx:.0f}% {ry:.0f}%">' + _tail_side(uid, 1, sweep) + "</g>")


def _back_hair(uid):
    d = ("M -64 -160 C -70 -206 -40 -238 0 -238 C 40 -238 70 -206 64 -160 "
         "C 66 -136 62 -116 54 -98 C 30 -92 -30 -92 -54 -98 C -62 -116 -66 -136 -64 -160 Z")
    return _shaded(uid, "bh", d, HAIR_SH, [("M -70 -130 L 70 -130 L 70 -80 L -70 -80 Z", HAIR_SH2)], sw=2.4)


BUN = "M -16 -228 C -20 -244 -34 -256 -50 -263 C -60 -250 -64 -232 -58 -214 C -44 -212 -26 -216 -16 -228 Z"


def _bun_ornament(uid, sgn):
    """Gold hair cuff wrapped round the bun with a violet gem and a tiny two-drop tassel (left bun coords)."""
    band = "M -64 -232 Q -46 -239 -24 -245"
    gem_f = "M -43 -246 L -38.5 -239.5 L -43 -233 L -47.5 -239.5 Z"
    gem = "M -43 -243.6 L -40.6 -239.5 L -43 -235.4 L -45.4 -239.5 Z"
    glint = "M -43.6 -242 L -42.2 -240.6 L -43.8 -239.6 Z"
    wing = "M -47 -239.5 L -52 -243 L -50.2 -238.4 Z M -39 -239.5 L -34 -242.2 L -36 -237.6 Z"
    chain = "M -61 -232.5 C -63 -228 -64 -224 -63.5 -220"
    drop = "M -63.5 -221 C -61.2 -219 -61 -216 -63.5 -213.6 C -66 -216 -65.8 -219 -63.5 -221 Z"
    chain2 = "M -58.5 -233.5 C -59 -229 -58.6 -226 -57.6 -223.5"
    drop2 = "M -57.6 -224.4 L -55.8 -221.6 L -57.6 -218.8 L -59.4 -221.6 Z"
    parts = [(chain, "none", GOLD_SH, 1.3), (chain2, "none", GOLD_SH, 1.2)]
    cid = f"{uid}-c-bunc{sgn}"
    out = []
    if sgn == 1:
        band, gem_f, gem, glint, wing, chain, drop, chain2, drop2 = map(
            _mirror, (band, gem_f, gem, glint, wing, chain, drop, chain2, drop2))
    out.append(_p(chain, "none", stroke=GOLD_SH, sw=1.3))
    out.append(_p(chain2, "none", stroke=GOLD_SH, sw=1.2))
    out.append(_p(drop, "#9b6bf2", stroke=INK, sw=1.0))
    out.append(_p(drop2, GOLD, stroke=INK, sw=0.9))
    bun = BUN if sgn == -1 else _mirror(BUN)
    out.append(f'<clipPath id="{cid}"><path d="{bun}"/></clipPath><g clip-path="url(#{cid})">'
               + _p(band, "none", stroke=INK, sw=6.6) + _p(band, "none", stroke=GOLD, sw=4.2)
               + _p(band, "none", stroke="#fff1c4", sw=1.1, extra=' transform="translate(0 -1.2)" opacity=".9"')
               + "</g>")
    out.append(_p(wing, GOLD, stroke=INK, sw=0.9))
    out.append(_p(gem_f, GOLD, stroke=INK, sw=1.2))
    out.append(_p(gem, "#8f5ff0", stroke=None))
    out.append(_p(glint, "#f3ebff", stroke=None))
    return "".join(out)


def _buns(uid):
    out = []
    for sgn in (-1, 1):
        d = BUN
        sh = [("M -50 -263 C -60 -250 -64 -232 -58 -214 C -50 -213 -44 -214 -40 -215 C -48 -228 -50 -246 -50 -263 Z", HAIR_SH),
              ("M -16 -228 C -26 -218 -42 -213 -58 -214 L -58 -206 L -12 -222 Z", HAIR_SH2)]
        hi = [("M -41 -253 C -33 -248 -27 -241 -24 -234 C -30 -239 -36 -243 -44 -246 Z", HAIR_HI),
              ("M -40 -251 C -35 -248 -31 -244 -29 -240 C -32 -243 -36 -246 -41 -248.5 Z", HAIR_LILAC),
              # thin rim light on the outer silhouette
              ("M -50 -266 C -60 -252 -66 -234 -60 -214 L -57.6 -214 C -62 -232 -58.6 -250 -49.4 -260 Z", HAIR_RIM)]
        strands = ["M -48 -258 C -45 -246 -41 -236 -31 -225", "M -54 -246 C -53 -236 -50 -226 -44 -218"]
        if sgn == 1:
            d = _mirror(d); sh = [(_mirror(a), b) for a, b in sh]; hi = [(_mirror(a), b) for a, b in hi]
            strands = [_mirror(a) for a in strands]
        out.append(_shaded(uid, f"bun{sgn}", d, HAIR, sh, hi, sw=2.4))
        for a in strands:
            out.append(_p(a, "none", stroke=INK_SOFT, sw=1.1, extra=' opacity=".7"'))
        out.append(_bun_ornament(uid, sgn))
    return "".join(out)


def _face(uid):
    d = ("M -54 -176 C -56 -150 -50 -130 -36 -118 C -24 -108 -10 -103 0 -103 "
         "C 10 -103 24 -108 36 -118 C 50 -130 56 -150 54 -176 Z")
    # hair shadow cast on forehead (hard anime shadow under the bangs)
    sh = [(_shift(FRONT_HAIR, 1.5, 5), SKIN_SH),
          ("M -56 -160 C -52 -140 -48 -128 -44 -122 C -50 -124 -56 -136 -58 -150 Z", SKIN_SH),
          ("M 56 -160 C 52 -140 48 -128 44 -122 C 50 -124 56 -136 58 -150 Z", SKIN_SH)]
    return _shaded(uid, "face", d, SKIN, sh, sw=2.3)


def _eye(uid, cx, side, look=(0, 0)):
    """side=-1 for viewer-left eye, +1 viewer-right. Outer corner is toward the side.
    look shifts the iris/pupil/highlights inside the eye white (gaze direction)."""
    o = side  # outward
    ex, ey = cx, -134
    out = []
    # eye white
    white = (f"M {ex-13*o} {ey-6} C {ex-12*o} {ey-16} {ex+10*o} {ey-17} {ex+14*o} {ey-8} "
             f"C {ex+15*o} {ey+6} {ex+8*o} {ey+14} {ex} {ey+14} C {ex-9*o} {ey+14} {ex-14*o} {ey+6} {ex-13*o} {ey-6} Z")
    cid = f"{uid}-eye{side}"
    out.append(f'<clipPath id="{cid}"><path d="{white}"/></clipPath>')
    out.append(_p(white, "#ffffff", stroke=None))
    g = []
    g.append(f'<ellipse cx="{ex+1*o}" cy="{ey+1}" rx="11" ry="14" fill="url(#{uid}-iris)" stroke="#33206a" stroke-width="1.1"/>')
    # lid shadow on the eyeball
    g.append(_p(f"M {ex-16} {ey-20} L {ex+16} {ey-20} L {ex+16} {ey-7} C {ex+6} {ey-10} {ex-6} {ey-10} {ex-16} {ey-6} Z",
                "#3a2270", stroke=None, extra=' opacity=".45"'))
    # pupil: tall diamond, Keqing-ish
    g.append(_p(f"M {ex+1*o} {ey-6} L {ex+5*o} {ey+2} L {ex+1*o} {ey+9} L {ex-3*o} {ey+2} Z", "#2a165c", stroke=None))
    # lower iris glow
    g.append(f'<ellipse cx="{ex+1*o}" cy="{ey+9}" rx="7" ry="3.6" fill="#efe2ff" opacity=".55"/>')
    # highlights
    g.append(f'<ellipse cx="{ex-4*o}" cy="{ey-5}" rx="4.6" ry="5.6" fill="#ffffff"/>')
    g.append(f'<circle cx="{ex+6*o}" cy="{ey+6}" r="2" fill="#ffffff"/>')
    g.append(f'<circle cx="{ex+4.5*o}" cy="{ey-7}" r="1.3" fill="#ffffff" opacity=".9"/>')
    if look != (0, 0):      # move iris/pupil/highlights; the lid shadow stays put (same layer order)
        t = f'<g transform="translate({look[0]} {look[1]})">'
        g = [t + g[0] + "</g>", g[1], t + "".join(g[2:]) + "</g>"]
    out.append(f'<g clip-path="url(#{cid})">{"".join(g)}</g>')
    # upper lash line: thick, with outer flick
    lash = (f"M {ex-15*o} {ey-4} C {ex-12*o} {ey-16} {ex+8*o} {ey-20} {ex+15*o} {ey-9} "
            f"L {ex+19*o} {ey-12} L {ex+16*o} {ey-5} "
            f"C {ex+10*o} {ey-15} {ex-8*o} {ey-14} {ex-13*o} {ey-2} Z")
    out.append(_p(lash, "#2e1b5c", stroke="#2e1b5c", sw=1.2))
    # small lash tick at outer corner
    # double-eyelid crease
    out.append(_p(f"M {ex-6*o} {ey-20} C {ex+2*o} {ey-23} {ex+10*o} {ey-21} {ex+15*o} {ey-15}", "none", stroke=INK_SOFT, sw=1.0, extra=' opacity=".5"'))
    # lower lash: short soft stroke
    out.append(_p(f"M {ex-4*o} {ey+14.5} C {ex+3*o} {ey+15} {ex+9*o} {ey+12} {ex+12*o} {ey+7}", "none", stroke=INK_SOFT, sw=1.3))
    return "".join(out)


def _face_details(uid, turn=0.0, closed=False):
    """turn in [0, 1]: 3/4 turn toward +x -- features slide toward +x and the far (+x) eye narrows."""
    if not turn:
        out = [_eye(uid, -22, -1), _eye(uid, 22, 1)]
    else:
        dn, df, k = 5 * turn, 8 * turn, 1 - .2 * turn
        lk = (round(3.2 * turn, 1), round(-2.0 * turn, 1))    # glance up toward the raised blade
        out = [f'<g transform="translate({dn:.1f} 0)">{_eye(uid, -22, -1, lk)}</g>',
               f'<g transform="translate({22 + df:.1f} 0) scale({k:.2f} 1) translate(-22 0)">{_eye(uid, 22, 1, lk)}</g>']
    body = _face_lower(uid, closed)
    if turn:
        body = f'<g transform="translate({7 * turn:.1f} 0)">{body}</g>'
    out.append(body)
    return "".join(out)


def _face_lower(uid, closed=False):
    out = []
    # blush + hatch
    for sx in (-1, 1):
        cx = 31 * sx
        out.append(f'<ellipse cx="{cx}" cy="-114" rx="12" ry="6" fill="url(#{uid}-blush)"/>')
        for k in (-5, 0, 5):
            out.append(_p(f"M {cx+k-1.5} -112 L {cx+k+1.5} -117", "none", stroke="#f07f9d", sw=1.1))
    # nose
    out.append(_p("M 1 -120 L 2.2 -118.6", "none", stroke="#d99a9a", sw=1.4))
    if closed:
        # closed-mouth determined smile: one lopsided stroke, the far corner tucked up in a smirk
        out.append(_p("M -6.5 -110.6 C -3 -108.2 2.6 -108 7.4 -111.8", "none", stroke=INK, sw=1.7))
        out.append(_p("M 7.4 -111.8 L 9 -113.6", "none", stroke=INK, sw=1.3))
        out.append(_p("M -1.6 -106.2 C 0.4 -105.6 2 -105.8 3.2 -106.6", "none", stroke="#e79aa8", sw=1.1))
    else:
        # determined confident smile: open, slightly lopsided
        out.append(_p("M -7 -112 C -3 -109 4 -109 8 -113 C 6 -106 -3 -104 -7 -112 Z", "#d45a7a", stroke=INK, sw=1.5))
        out.append(_p("M -3 -107.6 C 0 -106 3 -106.5 5 -108.2 C 3 -109.2 -1 -109.2 -3 -107.6 Z", "#ff9bb2", stroke=None))
        out.append(_p("M -9 -111 L -7 -112", "none", stroke=INK, sw=1.3))
    # determined brows, drawn over the bangs (see-through hair convention)
    out.append(_p("M -33 -158 C -27 -160 -19 -159 -12 -155", "none", stroke="#4a2f8a", sw=2.2, extra=' opacity=".9"'))
    out.append(_p("M 33 -158 C 27 -160 19 -159 12 -155", "none", stroke="#4a2f8a", sw=2.2, extra=' opacity=".9"'))
    return "".join(out)


def _front_hair(uid):
    d = FRONT_HAIR
    sh = [
        ("M 24 -152 Q 22 -166 16 -176 L 18 -190 Q 24 -172 30 -160 Z", HAIR_SH),
        ("M 6 -150 Q 4 -164 -2 -176 L 0 -192 Q 6 -170 12 -158 Z", HAIR_SH),
        ("M -14 -152 Q -14 -166 -20 -176 L -18 -190 Q -12 -170 -8 -160 Z", HAIR_SH),
        ("M -32 -154 Q -32 -162 -36 -168 L -36 -184 Q -32 -170 -26 -160 Z", HAIR_SH),
        ("M 52 -104 C 50 -124 46 -140 41 -150 C 44 -160 50 -172 58 -182 C 60 -156 58 -128 52 -104 Z", HAIR_SH),
        ("M -52 -104 C -50 -122 -48 -134 -46 -144 C -50 -156 -54 -170 -58 -182 C -62 -156 -60 -126 -52 -104 Z", HAIR_SH),
        ("M -70 -200 C -64 -170 -60 -150 -56 -110 L -72 -110 Z", HAIR_SH2),
        ("M 70 -200 C 64 -170 60 -150 56 -110 L 72 -110 Z", HAIR_SH2),
    ]
    # angel-ring highlight following the skull curve, with a jagged lower edge
    top, bot = [], []
    n = 22
    for k in range(n + 1):
        x = -55 + 110 * k / n
        yt = -214 + 0.0062 * x * x            # arc
        top.append((x, yt))
        bot.append((x, yt + (11 if k % 2 else 5)))
    ring = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in top + bot[::-1]) + " Z"
    rim = ("M -52 -104 C -62 -126 -66 -148 -64 -168 C -70 -212 -38 -244 0 -244 C 38 -244 70 -212 64 -168 "
           "C 66 -148 62 -126 52 -104 L 49.6 -108 C 59 -128 62.6 -148 61.4 -168 C 61.6 -209 36.6 -241.4 0 -241.4 "
           "C -36.6 -241.4 -61.6 -209 -61.4 -168 C -62.6 -148 -59 -128 -49.6 -108 Z")
    hi = [(ring, HAIR_HI), (rim, "#c4b2fb")]
    out = [_shaded(uid, "fh", d, f"url(#{uid}-hairg)", sh, hi, sw=2.5)]
    for ln in ("M -14 -153 C -13 -160 -12 -166 -10 -172", "M 6 -151 C 7 -158 8 -164 10 -170",
               "M 24 -153 C 25 -160 26 -165 28 -170", "M -32 -155 C -31 -160 -30 -164 -29 -168",
               "M 50 -112 C 48 -124 47 -136 47 -148", "M -50 -112 C -48 -124 -47 -136 -47 -148",
               "M -40 -186 C -36 -200 -28 -210 -18 -218", "M 40 -186 C 36 -200 28 -210 18 -218"):
        out.append(_p(ln, "none", stroke=INK_SOFT, sw=1.2, extra=' opacity=".75"'))
    # tiny star glint on the hair gloss
    out.append(_sparkle(-30, -219, 4.5, "#ffffff"))
    return "".join(out)


def _ornaments(uid):
    """Kept for compatibility: the hair ornaments are now drawn on the buns (see _bun_ornament)."""
    return ""


def _body(uid, turn=0.0, step=False):
    """step=True: she has just stepped toward +x -- the back (-x) foot lifts behind her, the front
    foot plants a little forward and the coat tails trail toward -x."""
    out = []
    tx = 5 * turn          # chest centre-line shift for a 3/4 turn toward +x
    # back coat tails (white with purple lining, gold edge)
    for sgn in (-1, 1):
        d = "M -22 -62 C -40 -50 -58 -26 -66 -4 C -54 -10 -44 -12 -34 -10 C -30 -26 -24 -42 -16 -56 Z"
        sh = [("M -66 -4 C -54 -10 -44 -12 -34 -10 C -32 -16 -30 -20 -28 -24 C -40 -22 -54 -16 -66 -4 Z", WHITE_SH)]
        if sgn == 1:
            d = _mirror(d); sh = [(_mirror(a), b) for a, b in sh]
        coat = _shaded(uid, f"coat{sgn}", d, WHITE, sh, sw=2.2)
        if step:      # trail behind the step: both tails swing toward -x and lift a little
            px = -22 if sgn == -1 else 22
            coat = f'<g transform="rotate({11 if sgn == -1 else 8} {px} -62)">{coat}</g>'
        out.append(coat)
    # legs (tights) and heels
    for sgn in ((1, -1) if step else (-1, 1)):    # step: the lifted back leg is drawn over the planted one
        leg = "M -20 -30 L -19 -10 C -19 -7 -9 -7 -9 -10 L -8 -30 Z"
        hi = [("M -17 -26 L -16 -12 L -14.5 -12 L -15.5 -26 Z", TIGHTS_HI)]
        shoe = "M -22 -10 C -23 -2 -21 1 -14 1 C -7 1 -6 -3 -7 -10 C -12 -12 -18 -12 -22 -10 Z"
        if sgn == 1:
            leg = _mirror(leg); hi = [(_mirror(a), b) for a, b in hi]; shoe = _mirror(shoe)
        lg = [_shaded(uid, f"leg{sgn}", leg, TIGHTS, [], hi, sw=2.1)]
        shine = "M -19 -8 C -18 -6 -15 -5.5 -12 -6 L -12 -4.5 C -15 -4 -18 -4.5 -19.5 -6 Z"
        if sgn == 1:
            shine = _mirror(shine)
        lg.append(_shaded(uid, f"shoe{sgn}", shoe, PURP, [(_shift(shoe, 2 * sgn, 4), PURP_SH)], [(shine, PURP_HI)], sw=2.1))
        strap = "M -21 -9 Q -14 -11 -8 -9"
        lg.append(_p(strap if sgn == -1 else _mirror(strap), "none", stroke=GOLD, sw=2))
        lg = "".join(lg)
        if step:
            # back leg: swung back from the hip and lifted (heel up, toe pointing down);
            # front leg: planted slightly forward
            lg = (f'<g transform="translate(-3 -1) rotate(42 -14 -30)">{lg}</g>' if sgn == -1
                  else f'<g transform="translate(3 0) rotate(-7 14 -30)">{lg}</g>')
        out.append(lg)
    # skirt: purple with white under-layer + gold hem
    under = "M -32 -60 C -44 -46 -52 -32 -54 -22 Q 0 -10 54 -22 C 52 -32 44 -46 32 -60 Z"
    out.append(_shaded(uid, "under", under, WHITE, [("M -60 -30 Q 0 -18 60 -30 L 60 -10 L -60 -10 Z", WHITE_SH)], sw=2.1))
    sk = ("M -30 -62 C -40 -50 -46 -38 -50 -28 Q -38 -22 -26 -26 Q -14 -20 0 -24 Q 14 -20 26 -26 "
          "Q 38 -22 50 -28 C 46 -38 40 -50 30 -62 Z")
    sksh = [("M -30 -62 C -38 -52 -44 -40 -50 -28 Q -44 -25 -38 -25 C -36 -38 -32 -50 -24 -62 Z", PURP_SH),
            ("M 6 -62 C 4 -48 2 -36 0 -24 Q 8 -22 14 -23 C 12 -36 12 -50 14 -62 Z", PURP_SH),
            ("M 30 -62 C 38 -52 44 -40 50 -28 Q 46 -26 42 -25 C 40 -38 36 -50 24 -62 Z", PURP_SH)]
    skhi = [("M -16 -60 C -18 -48 -20 -38 -22 -28 L -18 -27 C -16 -38 -14 -50 -12 -60 Z", PURP_HI)]
    out.append(_shaded(uid, "skirt", sk, PURP, sksh, skhi, sw=2.2))
    out.append(_p("M -48 -31 Q -38 -25 -26 -29 Q -14 -23 0 -27 Q 14 -23 26 -29 Q 38 -25 48 -31",
                  "none", stroke=GOLD, sw=2.2))
    # torso / bodice
    tor = "M -24 -98 C -30 -84 -31 -70 -30 -58 L 30 -58 C 31 -70 30 -84 24 -98 Z"
    out.append(_shaded(uid, "torso", tor, PURP,
                       [("M -32 -100 L -14 -100 C -20 -86 -22 -72 -20 -56 L -32 -56 Z", PURP_SH)],
                       [("M 14 -92 C 18 -84 20 -74 20 -62 L 23 -62 C 23 -74 21 -84 17 -92 Z", PURP_HI)], sw=2.2))
    # white chest panel / high collar (V) with gold trim
    col = "M -18 -100 C -10 -94 -4 -88 0 -76 C 4 -88 10 -94 18 -100 L 8 -104 L 0 -98 L -8 -104 Z"
    colsh = "M -18 -100 C -10 -94 -4 -88 0 -76 L 0 -98 L -8 -104 Z"
    coll = "M -19 -99 C -11 -93 -5 -87 0 -75 C 5 -87 11 -93 19 -99"
    if tx:
        col, colsh, coll = (_shift(d, tx, 0) for d in (col, colsh, coll))
    out.append(_shaded(uid, "col", col, WHITE, [(colsh, WHITE_SH)], sw=1.8))
    out.append(_p(coll, "none", stroke=GOLD, sw=2))
    # waist sash (gold) + Electro vision at the hip
    out.append(_p("M -30 -62 Q 0 -56 30 -62 L 30 -57 Q 0 -51 -30 -57 Z", GOLD, sw=1.5))
    vis = [("M 24 -64 L 31 -58 L 24 -52 L 17 -58 Z", GOLD, INK), ("M 24 -61.5 L 28 -58 L 24 -54.5 L 20 -58 Z", "#a074ff", None),
           ("M 23 -60 L 24.5 -59 L 23 -58 Z", "#ffffff", None)]
    for d, fill, stroke in vis:
        d = _shift(d, -1.6 * tx, 0) if tx else d
        out.append(_p(d, fill, stroke=stroke, sw=1.5) if stroke else _p(d, fill, stroke=None))
    # chest emblem: gold diamond with violet gem
    em = [("M 0 -80 L 5 -73 L 0 -66 L -5 -73 Z", GOLD, INK), ("M 0 -77 L 2.6 -73 L 0 -69 L -2.6 -73 Z", "#8f5ff0", None)]
    for d, fill, stroke in em:
        d = _shift(d, tx, 0) if tx else d
        out.append(_p(d, fill, stroke=stroke, sw=1.4) if stroke else _p(d, fill, stroke=None))
    # neck + chin shadow
    out.append(_shaded(uid, "neck", "M -8 -110 L -8 -98 L 0 -96 L 8 -98 L 8 -110 Z", SKIN,
                       [("M -10 -112 L 10 -112 L 10 -103 Q 0 -98 -10 -103 Z", SKIN_SH)], sw=1.8))
    # shoulder puffs (purple w/ gold edge), Keqing's sleeve caps
    for sgn in (-1, 1):
        d = "M -22 -100 C -32 -102 -40 -94 -38 -84 C -32 -80 -26 -84 -22 -90 Z"
        if sgn == 1:
            d = _mirror(d)
        out.append(_shaded(uid, f"pu{sgn}", d, PURP_HI, [(_shift(d, 3 * -sgn, 6), PURP)], sw=2))
        g = "M -37 -86 C -32 -82 -27 -85 -23 -90"
        out.append(_p(g if sgn == -1 else _mirror(g), "none", stroke=GOLD, sw=2))
    return "".join(out)


def _arm_hip(uid):
    arm = "M 32 -90 C 44 -84 48 -74 44 -64 L 35 -67 C 38 -72 36 -78 28 -83 Z"
    out = [_shaded(uid, "armR", arm, WHITE, [("M 44 -64 L 35 -67 C 38 -72 38 -76 36 -80 L 48 -74 Z", WHITE_SH)], sw=2)]
    # gloved hand resting on the hip: back of the hand, fingers tucked toward the waist
    hand = ("M 35 -65 C 40 -67.5 45.5 -64.5 44.6 -59.5 C 44 -56 41.6 -52.6 38.6 -50.6 "
            "Q 36 -48.6 34.2 -50.6 Q 31.6 -50.2 31.4 -52.8 Q 29.2 -53.4 30 -56 Q 28.8 -58.6 31 -60.4 "
            "C 31.6 -62.6 33 -64.2 35 -65 Z")
    out.append(_shaded(uid, "handR", hand, PURP,
                       [("M 44.6 -59.5 C 44 -56 41.6 -52.6 38.6 -50.6 Q 36 -48.6 34.2 -50.6 L 37 -54 L 42 -60 Z", PURP_SH)],
                       [("M 34 -63.2 C 37.4 -64.8 41 -64.2 42.4 -62.4 C 39.6 -62.4 36.6 -61.6 34.4 -60.2 Z", PURP_HI)], sw=1.8))
    for ln in ("M 35.6 -57.6 L 32.2 -54.6", "M 37.6 -56.4 L 34.6 -52.4", "M 39.8 -55.2 L 37.4 -51.6"):
        out.append(_p(ln, "none", stroke=INK, sw=1.0, extra=' opacity=".8"'))
    out.append(_p("M 46.5 -68 L 35 -72 L 33 -65.5 L 44.6 -61.5 Z", GOLD, sw=1.6))
    out.append(_p("M 45 -66.4 L 35.4 -69.8", "none", stroke="#fff1c4", sw=1, extra=' opacity=".9"'))
    return "".join(out)


def _stiletto(uid):
    """Slim lightning stiletto, drawn pointing up (-y) with the grip centre at the origin.
    The fist (drawn over it) covers y in [-8.6, 8]; the gold cross-guard sits just above the
    fist and the dark hilt end + gold pommel just below, so the weapon reads as a sword."""
    blade = "M -3.8 -15 C -3.7 -42 -2.9 -70 0 -104 C 2.9 -70 3.7 -42 3.8 -15 Z"
    out = [f'<g class="{uid}-gl">'
           f'<path d="{blade}" fill="{ELEC}" stroke="{ELEC}" stroke-width="9" stroke-linejoin="round" '
           f'opacity=".85" filter="url(#{uid}-glow)"/>'
           f'<path d="{blade}" fill="none" stroke="#e4d4ff" stroke-width="3.2" stroke-linejoin="round" opacity=".55"/></g>',
           _p(blade, f"url(#{uid}-blade)", stroke="#4f28a8", sw=1.4),
           # hard cel split along the ridge: darker plane on one side ...
           _p("M 0 -101 C -2.4 -70 -3.2 -42 -3.3 -15.5 L 0 -15.5 Z", "#7448de", stroke=None, extra=' opacity=".62"'),
           # ... and a hard white light edge on the other
           _p("M 0.6 -98 C 2.4 -70 3.0 -42 3.1 -16 L 1.5 -16 C 1.5 -42 1.2 -70 0.6 -98 Z", "#ffffff", stroke=None),
           _p("M 0 -100 L 0 -17", "none", stroke="#f3ecff", sw=.8, extra=' opacity=".8"'),
           _sparkle(0, -102, 4.6, "#ffffff")]
    # cross-guard: gold, swept like a little lightning wing, hard shadow underneath, violet gem
    guard = ("M -15.5 -11.5 L -9.5 -16.6 L -3.6 -15.6 L 0 -20 L 3.6 -15.6 L 9.5 -16.6 L 15.5 -11.5 "
             "L 11.5 -8.4 L 4.4 -9.8 L 0 -7.6 L -4.4 -9.8 L -11.5 -8.4 Z")
    out.append(_shaded(uid, "guard", guard, GOLD,
                       [("M -16 -11.6 L 16 -11.6 L 16 -6 L -16 -6 Z", GOLD_SH)],
                       [("M -13.4 -12.4 L -9.2 -15.4 L -3.8 -14.4 L -3.4 -13.2 L -9 -14.1 Z", "#fff3cf")], sw=1.3))
    out.append(_p("M 0 -17.6 L 2.6 -13.6 L 0 -10.4 L -2.6 -13.6 Z", "#9b6bf2", stroke=INK, sw=.8))
    out.append(_p("M -.5 -16 L .8 -14.4 L -.6 -13.6 Z", "#ffffff", stroke=None))
    # dark hilt end + gold pommel showing below the fist
    out.append(_p("M -2.6 -4 L 2.6 -4 L 2.8 13 L -2.8 13 Z", "#2c2768", sw=1.2))
    out.append(_p("M -2.2 10.2 L 2.2 10.2", "none", stroke="#6c64c4", sw=1))
    out.append(_shaded(uid, "pom", "M 0 11.6 L 4.6 16.4 L 0 21.4 L -4.6 16.4 Z", GOLD,
                       [("M 0 16.4 L 6 16.4 L 0 23 Z", GOLD_SH)], sw=1.2))
    out.append(_p("M 0 14 L 1.7 16.4 L 0 18.8 L -1.7 16.4 Z", "#9b6bf2", stroke=None))
    return "".join(out)


def _fist(uid):
    """Small gloved fist gripping a hilt that runs vertically through the origin (wrist below)."""
    fist = ("M -6.4 -5.4 C -3 -8.6 2.6 -8.6 5 -7 Q 8.6 -5.8 7.2 -3.1 Q 9.2 -0.9 7.2 1.2 Q 9 3.4 6.8 5.4 "
            "Q 6.4 8 3 8 L -3.8 8 C -6.6 8 -7.4 5.6 -7 2.6 Z")
    out = [_shaded(uid, "fistL", fist, PURP,
                   [("M -7.4 -6 L -2.4 -6 C -3.6 -1 -3.4 4 -2 9 L -7.6 9 Z", PURP_SH)],
                   [("M 1 -6.6 Q 6.2 -6.6 6.4 -4 L 1.6 -4.4 Z M 2 -2.2 Q 7 -2 7 0 L 2.2 -0.4 Z", PURP_HI)], sw=1.6)]
    for ln in ("M 1.4 -3.6 L 7.6 -3.3", "M 1.6 0.4 L 7.8 0.6", "M 1.6 4.2 L 7.4 4.6"):
        out.append(_p(ln, "none", stroke=INK, sw=0.9))
    # thumb wrapping over the front of the fingers
    thumb = "M -6.6 -3.4 C -3.6 -5.8 1.6 -6.2 4.6 -4.6 C 3.4 -2.6 -0.6 -1.6 -6.2 -0.6 Z"
    out.append(_shaded(uid, "thumbL", thumb, PURP_HI, [("M -7 -1.8 L 4.6 -4.6 L 5 -2 L -7 1 Z", PURP)], sw=1.2))
    return "".join(out)


HAND_L = (-54.5, -133.5)   # grip centre of the raised hand
SWORD_ROT = -20


def _arm_raised(uid):
    out = []
    hx, hy = HAND_L
    out.append(f'<ellipse cx="-74" cy="-172" rx="12" ry="40" transform="rotate(-20 -74 -172)" fill="url(#{uid}-aura)" opacity=".7"/>')
    out.append(f'<g transform="translate({hx} {hy}) rotate({SWORD_ROT})">{_stiletto(uid)}</g>')
    arm = "M -30 -96 C -42 -100 -50 -110 -53 -120 L -44 -124 C -41 -114 -35 -106 -26 -102 Z"
    out.append(_shaded(uid, "armL", arm, WHITE, [("M -30 -96 C -42 -100 -50 -110 -53 -120 L -49 -122 C -46 -112 -40 -104 -28 -98 Z", WHITE_SH)], sw=2))
    out.append(_p("M -55.5 -119 L -43 -125 L -45.4 -130.6 L -57.8 -124.6 Z", GOLD, sw=1.6))
    out.append(_p("M -55.4 -121.6 L -44.4 -127", "none", stroke="#fff1c4", sw=1, extra=' opacity=".9"'))
    out.append(f'<g transform="translate({hx} {hy}) rotate({SWORD_ROT})">{_fist(uid)}</g>')
    return "".join(out)


SHOULDER_P = (29, -94)     # point pose: shoulder pivot of the extended (+x side) sword arm
ARM_DEG_P = 54             # point pose: arm direction, degrees from vertical toward +x
ARM_LEN_P = 66
BLADE_DEG_P = 36           # point pose default blade direction (degrees from vertical toward +x)


def _point_hand(arm_deg=None):
    import math
    a = math.radians(ARM_DEG_P if arm_deg is None else arm_deg)
    return (SHOULDER_P[0] + ARM_LEN_P * math.sin(a), SHOULDER_P[1] - ARM_LEN_P * math.cos(a))


def _arm_point(uid, blade_deg, arm_deg=None):
    """Sword arm reaching out and up on the +x side (drawn over the side lock, under the
    shoulder puff), gloved fist at the end, blade at blade_deg from vertical (toward +x)."""
    import math
    arm_deg = ARM_DEG_P if arm_deg is None else arm_deg
    sx, sy = SHOULDER_P
    hx, hy = _point_hand(arm_deg)
    a = math.radians(arm_deg)
    ux, uy = math.sin(a), -math.cos(a)          # along the arm
    nx, ny = -uy, ux                              # +normal = lower/outer side of the arm
    def P(t, w):
        return (sx + ux * ARM_LEN_P * t + nx * w, sy + uy * ARM_LEN_P * t + ny * w)
    # white sleeve: tapers from the shoulder to the cuff (t = .78)
    up = [P(t / 10 * .8, -(8.6 - 2.4 * t / 10)) for t in range(11)]
    lo = [P(t / 10 * .8, 8.6 - 2.4 * t / 10) for t in range(11)]
    sleeve = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in up + lo[::-1]) + " Z"
    shade = ("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in [P(t / 10 * .8, 1.2 + .8 * (t % 2)) for t in range(11)]
                                + lo[::-1]) + " Z")
    lit = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in [P(t / 10 * .8, -5.8 + 1.6 * t / 10) for t in range(1, 10)]
                            + [P(t / 10 * .8, -3.6 + 1.6 * t / 10) for t in range(9, 0, -1)]) + " Z"
    out = [f'<ellipse cx="{hx + 30 * math.sin(math.radians(blade_deg)):.1f}" cy="{hy - 52 * math.cos(math.radians(blade_deg)):.1f}" '
           f'rx="13" ry="46" transform="rotate({blade_deg:.1f} {hx + 30 * math.sin(math.radians(blade_deg)):.1f} '
           f'{hy - 52 * math.cos(math.radians(blade_deg)):.1f})" fill="url(#{uid}-aura)" opacity=".7"/>',
           f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({blade_deg:.1f})">{_stiletto(uid)}</g>',
           _shaded(uid, "armP", sleeve, WHITE, [(shade, WHITE_SH)], [(lit, "#ffffff")], sw=2)]
    # gold cuff band
    c0, c1 = P(.76, -8), P(.76, 8)
    c2, c3 = P(.9, 7.4), P(.9, -7.4)
    out.append(_p(f"M {c0[0]:.1f} {c0[1]:.1f} L {c1[0]:.1f} {c1[1]:.1f} L {c2[0]:.1f} {c2[1]:.1f} L {c3[0]:.1f} {c3[1]:.1f} Z",
                  GOLD, sw=1.6))
    g0, g1 = P(.8, -6.6), P(.8, 6.4)
    out.append(_p(f"M {g0[0]:.1f} {g0[1]:.1f} L {g1[0]:.1f} {g1[1]:.1f}", "none", stroke="#fff1c4", sw=1, extra=' opacity=".9"'))
    out.append(f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({blade_deg:.1f})">{_fist(uid)}</g>')
    # the +x shoulder puff again, on top of the sleeve root
    d = _mirror("M -22 -100 C -32 -102 -40 -94 -38 -84 C -32 -80 -26 -84 -22 -90 Z")
    out.append(_shaded(uid, "puP", d, PURP_HI, [(_shift(d, -3, 6), PURP)], sw=2))
    out.append(_p(_mirror("M -37 -86 C -32 -82 -27 -85 -23 -90"), "none", stroke=GOLD, sw=2))
    return "".join(out)


def _arm_chest(uid):
    """Near (-x) arm folded in front of her chest: white sleeve from the shoulder down to the
    elbow and back across the bodice, small gloved fist held at the heart (resolute, not posing)."""
    sleeve = ("M -33 -95 C -40 -86 -42 -74 -38 -66 C -34 -60 -26 -60 -16 -66 L -9 -71 "
              "L -13 -80 L -22 -75 C -26 -73 -29 -74 -29 -78 C -28 -84 -26 -89 -22 -95 Z")
    shade = ("M -38 -66 C -34 -60 -26 -60 -16 -66 L -9 -71 L -11 -75 L -18 -71 C -26 -66 -33 -66 -37 -72 "
             "C -40 -80 -38 -88 -33 -95 L -45 -95 L -45 -60 Z")
    lit = "M -31 -91 C -35 -84 -36 -77 -34 -71 L -32 -72 C -33 -78 -32 -84 -29 -90 Z"
    out = [_shaded(uid, "armC", sleeve, WHITE, [(shade, WHITE_SH)], [(lit, "#ffffff")], sw=2)]
    # gold cuff at the wrist
    out.append(_p("M -16.4 -64.2 L -9.6 -68.6 L -14.6 -81.4 L -21.4 -77 Z", GOLD, sw=1.6))
    out.append(_p("M -15.6 -66.4 L -19.8 -77.6", "none", stroke="#fff1c4", sw=1, extra=' opacity=".9"'))
    # gloved fist, knuckles up, wrist toward -x
    out.append(f'<g transform="translate(-6.5 -76.5) rotate(78)">{_fist(uid + "c")}</g>')
    return "".join(out)


def _arm_hip_m(uid):
    """_arm_hip mirrored to the -x side (point pose: the sword arm is on +x)."""
    import re
    return re.sub(r' d="([^"]+)"', lambda m: f' d="{_mirror(m.group(1))}"', _arm_hip(uid))


def _electro(uid, bust=False, point=False):
    out = []
    if point:
        # crackle trails behind the step (-x) and round the sword hand side, clear of the blade
        bolts = [([(-112, -200), (-106, -209), (-112, -213), (-104, -224), (-110, -227), (-102, -240)], 3.6, "fl"),
                 ([(-132, -150), (-140, -145), (-136, -140), (-146, -136), (-143, -131), (-156, -126)], 3.0, "fl2"),
                 ([(-64, -40), (-72, -46), (-69, -51), (-79, -56), (-76, -61), (-88, -70)], 3.0, "fl"),
                 ([(116, -110), (124, -116), (120, -121), (130, -126), (126, -131), (138, -140)], 3.0, "fl2")]
        sparks = [(-120, -214, 7, ELEC_CORE, "tw"), (-80, -254, 4.5, ELEC, "tw2"), (-150, -160, 3.6, ELEC, "tw"),
                  (122, -88, 5, ELEC_CORE, "tw2"), (-96, -80, 4, ELEC, "tw"), (112, -196, 3.6, ELEC_CORE, "tw")]
        for pts, w, c in bolts:
            out.append(_bolt(pts, uid, w, f"{uid}-{c}"))
        for cx, cy, r, c, cls in sparks:
            out.append(f'<g filter="url(#{uid}-glow)" opacity=".7">{_sparkle(cx, cy, r*1.4, ELEC)}</g>')
            out.append(_sparkle(cx, cy, r, c, f"{uid}-{cls}"))
        return "".join(out)
    out.append(_bolt([(-108, -206), (-102, -215), (-108, -219), (-100, -230), (-106, -233), (-98, -246)], uid, 3.6, f"{uid}-fl"))
    out.append(_bolt([(-104, -178), (-112, -173), (-108, -168), (-118, -164), (-115, -159), (-128, -154)], uid, 3.0, f"{uid}-fl2"))
    out.append(_bolt([(80, -234), (90, -239), (87, -245), (98, -249), (95, -255), (108, -264)], uid, 3.2, f"{uid}-fl2"))
    if not bust:
        out.append(_bolt([(62, -36), (70, -42), (67, -47), (77, -52), (74, -57), (86, -66)], uid, 3.0, f"{uid}-fl"))
    for cx, cy, r, c, cls in [(-114, -216, 7, ELEC_CORE, f"{uid}-tw"), (-78, -250, 4.5, ELEC, f"{uid}-tw2"),
                              (114, -222, 6, ELEC, f"{uid}-tw"), (98, -196, 3.6, ELEC_CORE, f"{uid}-tw2"),
                              (-96, -146, 3.6, ELEC, f"{uid}-tw")] + ([] if bust else
                             [(92, -84, 5, ELEC_CORE, f"{uid}-tw2"), (-94, -72, 4, ELEC, f"{uid}-tw")]):
        out.append(f'<g filter="url(#{uid}-glow)" opacity=".7">{_sparkle(cx, cy, r*1.4, ELEC)}</g>')
        out.append(_sparkle(cx, cy, r, c, cls))
    return "".join(out)


LEAN_P = (5.0, 8, 0)       # point pose: whole-figure forward lean (deg, pivot x, pivot y), toward +x
HEAD_TILT_P = -5.0         # point pose: chin lifted toward the target (deg about the neck)
NECK = (0, -104)


def _rot(px, py, deg, cx, cy):
    import math
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))


def _aim(lx, ly):
    """Arm + blade angles (deg from vertical toward +x) that point the stiletto tip line at the
    local, un-leaned point (lx, ly).  The arm is kept diagonal (>= 40 deg) so the fist clears her
    face; the wrist cocks the blade the rest of the way onto the target."""
    import math
    arm = ARM_DEG_P
    blade = BLADE_DEG_P
    for _ in range(4):
        hx, hy = _point_hand(arm)
        blade = math.degrees(math.atan2(lx - hx, -(ly - hy)))
        blade = max(-10.0, min(70.0, blade))
        arm = max(40.0, min(62.0, 0.6 * blade + 40.0))
    return arm, blade


def keqing(x, y, scale=1, uid="kq", pose="stand", flip=False, target=None):
    """pose: 'stand' (sword raised by her face, other hand on hip), 'bust', or 'point' (action pose:
    body turned 3/4 toward local +x -- page-left when flip=True -- leaning into a step, sword arm
    thrust diagonally up and out on that side with the blade aimed, near fist held at her chest,
    back foot lifted behind her, both twin tails swept back, closed-mouth determined smile).
    target=(px, py) in PAGE coordinates aims the point-pose blade at that spot (the tip line passes
    through it; blade angle clamped to [-10, 70] deg from vertical); default 36 deg."""
    sx = -scale if flip else scale
    parts = [_style(uid), _defs(uid)]
    bust = pose == "bust"
    point = pose == "point"
    arm_deg, blade_deg = ARM_DEG_P, BLADE_DEG_P
    if point and target is not None:
        lx = (target[0] - x) / sx          # target in local (unflipped, unscaled) coordinates
        ly = (target[1] - y) / scale
        lx, ly = _rot(lx, ly, -LEAN_P[0], LEAN_P[1], LEAN_P[2])     # undo the lean
        arm_deg, blade_deg = _aim(lx, ly)
    clip = ""
    if bust:
        parts.append(f'<linearGradient id="{uid}-fade" gradientUnits="userSpaceOnUse" x1="0" y1="-112" x2="0" y2="-64">'
                     f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                     f'<mask id="{uid}-bm" maskUnits="userSpaceOnUse" x="-150" y="-300" width="300" height="250">'
                     f'<rect x="-150" y="-300" width="300" height="250" fill="url(#{uid}-fade)"/></mask>')
        clip = f' mask="url(#{uid}-bm)"'
        parts.append(f"<g{clip}>")
    elif point:
        # shadow: planted front foot + a fainter one under the lifted heel
        parts.append(f'<ellipse cx="8" cy="1" rx="56" ry="7" fill="#7a63c8" opacity=".22"/>'
                     f'<ellipse cx="-38" cy="1.5" rx="12" ry="2.6" fill="#7a63c8" opacity=".13"/>')
        parts.append(f'<g transform="rotate({LEAN_P[0]} {LEAN_P[1]} {LEAN_P[2]})">')
    else:
        parts.append(f'<ellipse cx="0" cy="1" rx="62" ry="7" fill="#7a63c8" opacity=".22"/>')
        parts.append("<g>")
    if point:
        head = f'<g transform="rotate({HEAD_TILT_P} {NECK[0]} {NECK[1]})">'
        parts.append(head + _tails(uid, 1.0) + _back_hair(uid) + "</g>")
        parts.append(_body(uid, .8, step=True))
        parts.append(head + _face(uid) + _face_details(uid, .8, closed=True) + _buns(uid)
                     + _front_hair(uid) + _ornaments(uid) + "</g>")
        parts.append(_arm_chest(uid))
        parts.append(_arm_point(uid, blade_deg, arm_deg))
    else:
        parts.append(_tails(uid))
        parts.append(_back_hair(uid))
        parts.append(_body(uid, 0))
        parts.append(_arm_hip(uid))
        parts.append(_face(uid))
        parts.append(_face_details(uid, 0))
        parts.append(_buns(uid))
        parts.append(_front_hair(uid))
        parts.append(_ornaments(uid))
        parts.append(_arm_raised(uid))
    parts.append("</g>")
    parts.append(_electro(uid, bust, point))
    return f'<g transform="translate({x} {y}) scale({sx} {scale})">' + "".join(parts) + "</g>"


def _cloud(cid, cx, cy, s, puffs, base="#ffffff", shade="#ddd4fa", deep="#cbbff3"):
    """Anime cumulus: union of puffs, flat bottom, hard-edged lavender underside and a deeper base strip."""
    circ = "".join(f'<circle cx="{cx+dx*s:.1f}" cy="{cy+dy*s:.1f}" r="{r*s:.1f}"/>' for dx, dy, r in puffs)
    lit = "".join(f'<circle cx="{cx+(dx-6)*s:.1f}" cy="{cy+(dy-13)*s:.1f}" r="{r*s*0.96:.1f}"/>' for dx, dy, r in puffs)
    cut = cy + 14 * s
    return (f'<clipPath id="{cid}-u">{circ}</clipPath>'
            f'<clipPath id="{cid}-b"><rect x="{cx-400}" y="{cut-400}" width="800" height="400"/></clipPath>'
            f'<g clip-path="url(#{cid}-b)"><g clip-path="url(#{cid}-u)">'
            f'<rect x="{cx-400}" y="{cut-400}" width="800" height="400" fill="{shade}"/>'
            f'<rect x="{cx-400}" y="{cut-5*s:.1f}" width="800" height="{6*s:.1f}" fill="{deep}"/>'
            f'<g fill="{base}">{lit}</g></g></g>')


def showcase():
    W = H = 600
    defs = f"""<defs>
<linearGradient id="sc-sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#a9b6f2"/><stop offset=".4" stop-color="#cfc9f8"/><stop offset=".75" stop-color="#f1d9f1"/><stop offset="1" stop-color="#fde6ee"/></linearGradient>
<radialGradient id="sc-sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fffaf0" stop-opacity="1"/><stop offset=".25" stop-color="#fff6ec" stop-opacity=".7"/><stop offset="1" stop-color="#fff6ec" stop-opacity="0"/></radialGradient>
<linearGradient id="sc-ray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
<clipPath id="sc-r"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>"""
    rays = "".join(f'<path d="M 560 -10 L {x0} 640 L {x0+w} 640 Z" fill="url(#sc-ray)" opacity="{o}"/>'
                   for x0, w, o in [(120, 40, .5), (250, 70, .35), (380, 30, .45), (470, 60, .3)])
    puffs_a = [(-90, 0, 40), (-50, -22, 50), (0, -38, 62), (52, -18, 50), (96, 0, 38), (130, 6, 28)]
    puffs_b = [(-60, 0, 30), (-24, -18, 38), (18, -10, 34), (52, 0, 26)]
    stars = "".join(_sparkle(x, y, r, "#ffffff") for x, y, r in [(60, 70, 6), (110, 40, 3.5), (330, 60, 5), (560, 330, 4), (40, 300, 3.5)])
    body = [defs, '<g clip-path="url(#sc-r)">', f'<rect width="{W}" height="{H}" fill="url(#sc-sky)"/>',
            '<circle cx="540" cy="40" r="210" fill="url(#sc-sun)"/>', rays, stars,
            _cloud("scc1", 80, 210, 0.8, puffs_b),
            _cloud("scc2", 330, 600, 1.9, puffs_a),
            _cloud("scc3", 40, 610, 1.3, puffs_b),
            _cloud("scc4", 560, 615, 1.2, puffs_b),
            keqing(232, 572, 1.6, "kqa"),
            keqing(482, 250, 0.8, "kqc", pose="bust"),
            keqing(500, 574, 0.62, "kqb", pose="point", flip=True, target=(330, 300)),
            "</g>"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            + "".join(body) + "</svg>")


SHOWCASE_OUT = ("/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/"
                "scratchpad/v10final/chars/keqing.svg")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(SHOWCASE_OUT), exist_ok=True)
    with open(SHOWCASE_OUT, "w", encoding="utf-8") as f:
        f.write(showcase())
    print("wrote", SHOWCASE_OUT)
