"""Night Water Academy -- full-bleed anime background card (1600x900).

Usage:
    python3 gen.py            -> writes scene_nwa.svg next to this file
    from gen import scene_nwa -> scene_nwa(x=0, y=0, s=1.0, uid="nwa", animate=True) returns an SVG <g> string
                                 whose drawing covers (x, y)-(x+1600*s, y+900*s).
Pure stdlib. No text, no scripts, no rasters, no green hues.
Lower-left foreground (x 120-520, y 480-860) is kept calm: a lavender boardwalk for a chibi to stand on.
"""
import math
import os
import random

W, H = 1600, 900
HZ = 560  # water line / horizon

# ---------------------------------------------------------------- palette
INK = "#3d3b7a"
SKY = [(0, "#7f87dc"), (.30, "#a3a2ee"), (.55, "#c7b5f1"), (.80, "#ecc6e9"), (1, "#fcdbe3")]
CL_SH, CL_MID, CL_LT, CL_HI = "#a49be2", "#d2c1f2", "#f6dcef", "#fff7f8"
MT_FAR, MT_FAR_L = "#c3b6ef", "#d6cbf6"
MT_NEAR, MT_NEAR_L = "#a99ce2", "#bdb1ee"
ROOF, ROOF_D, ROOF_U, ROOF_H, ROOF_T = "#6668c4", "#4d4ea1", "#3d3c84", "#8e90e4", "#cfccf7"
GOLD, GOLD_L, GOLD_D = "#f3c46c", "#ffe8ad", "#d39a4c"
PIL, PIL_D, PIL_L = "#e2789c", "#b45a83", "#f7abc3"
BRK, BRK_D = "#86a0ea", "#5d76cf"
CREAM, GLOW, GLOW_L, LAT = "#fbf0e8", "#ffd88c", "#fff2c8", "#c98b7c"
ST_T, ST_F, ST_D = "#e6ddf7", "#bfb2e8", "#9a8fd6"
LAN, LAN_D = "#ef80a2", "#c45a86"
SAK, SAK_D, SAK_DD, SAK_L, SAK_H = "#f6b9d3", "#e392bb", "#c477a7", "#fbd6e6", "#fff0f6"
BARK = "#6a5197"
WOOD_T, WOOD_L, WOOD_F, WOOD_D = "#9384cc", "#ab9bdc", "#6f62ae", "#57508f"


_G = ["nwa"]  # current uid (for shared gradients inside helpers)


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def pts(seq):
    return " ".join(f"{n(a)},{n(b)}" for a, b in seq)


# ---------------------------------------------------------------- small motifs
def sparkle(x, y, r, col="#fffaf0", op=1.0, cls=""):
    k = r * .22
    d = (f"M{n(x)} {n(y-r)} Q{n(x+k)} {n(y-k)} {n(x+r)} {n(y)} Q{n(x+k)} {n(y+k)} {n(x)} {n(y+r)} "
         f"Q{n(x-k)} {n(y+k)} {n(x-r)} {n(y)} Q{n(x-k)} {n(y-k)} {n(x)} {n(y-r)}Z")
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="{col}" opacity="{op}"/>'


def petal_path(s):
    return (f"M0 {n(s)} C{n(-.95*s)} {n(.25*s)} {n(-.7*s)} {n(-.85*s)} {n(-.18*s)} {n(-s)} "
            f"L0 {n(-.72*s)} L{n(.18*s)} {n(-s)} C{n(.7*s)} {n(-.85*s)} {n(.95*s)} {n(.25*s)} 0 {n(s)}Z")


def petal(x, y, s, rot, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<g transform="translate({n(x)},{n(y)}) rotate({n(rot)})"><g{c}>'
            f'<path d="{petal_path(s)}" fill="{SAK}"/>'
            f'<path d="M0 {n(s)} C{n(-.95*s)} {n(.25*s)} {n(-.7*s)} {n(-.85*s)} {n(-.18*s)} {n(-s)} L0 {n(-.72*s)}Z" fill="{SAK_L}"/>'
            f'<path d="M0 {n(s*.85)} L0 {n(-.5*s)}" stroke="{SAK_D}" stroke-width="{n(max(.6, s*.08))}" opacity=".6"/>'
            f'</g></g>')


def blossom(x, y, r, col=SAK_H, mid=GOLD):
    out = []
    for i in range(5):
        a = math.radians(i * 72 - 90)
        out.append(f'<circle cx="{n(x+math.cos(a)*r*.55)}" cy="{n(y+math.sin(a)*r*.55)}" r="{n(r*.5)}" fill="{col}"/>')
    out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r*.28)}" fill="{mid}"/>')
    return "".join(out)


# ---------------------------------------------------------------- cel-shaded puffy mass (clouds, tree crowns)
def cel_mass(u, name, circles, cols, base=None, v=(-.3, -1), b1=10, b2=24, rim=5, **_):
    """Anime cel shading for a puffy mass (cloud lump, tree crown).
    circles: (cx, cy, r) union = silhouette S.  cols = (shadow, mid, light, rim-highlight).
    Each tone is S translated toward the light by a fixed offset, clipped to S, so terminators follow the lumpy
    outline with hard edges; rim highlight = S minus S shifted away from the light (mask).  base -> flat underside."""
    sh, mid, lt, hi = cols
    L = math.hypot(*v)
    vx, vy = v[0] / L, v[1] / L
    cid = f"{u}-{name}"
    circ = "".join(f'<circle cx="{n(a)}" cy="{n(b)}" r="{n(r)}"/>' for a, b, r in circles)
    defs = f'<clipPath id="{cid}">{circ}</clipPath>'
    if base is not None:
        defs += f'<clipPath id="{cid}-b"><rect x="-400" y="-400" width="2400" height="{n(base+400)}"/></clipPath>'

    def shape(fill, ox=0, oy=0):
        g = f'<g fill="{fill}">{circ}</g>'
        if base is not None:
            g = f'<g clip-path="url(#{cid}-b)">{g}</g>'
        if ox or oy:
            g = f'<g transform="translate({n(ox)},{n(oy)})">{g}</g>'
        return g
    defs += (f'<mask id="{cid}-m" maskUnits="userSpaceOnUse" x="-400" y="-400" width="2400" height="1700">'
             f'{shape("#fff")}{shape("#000", -vx*rim, -vy*rim)}</mask>')
    body = [shape(sh), shape(mid, vx * b1, vy * b1), shape(lt, vx * b2, vy * b2),
            f'<g mask="url(#{cid}-m)">{shape(hi)}</g>']
    inner = f'<g clip-path="url(#{cid})">{"".join(body)}</g>'
    if base is not None:
        inner = f'<g clip-path="url(#{cid}-b)">{inner}</g>'
    return defs, inner


def dome(cx, b, w, rnd):
    """Circles for one flat-bottomed cumulus lump of width w sitting on y=b."""
    c = [(cx + rnd.uniform(-.05, .05) * w, b - w * .2, w * .3),
         (cx - w * .27, b - w * .1, w * .21), (cx + w * .28, b - w * .11, w * .22),
         (cx - w * .43, b - w * .02, w * .12), (cx + w * .44, b - w * .03, w * .13),
         (cx + rnd.uniform(-.15, .15) * w, b - w * .4, w * .18)]
    if rnd.random() < .6:
        c.append((cx + rnd.choice([-1, 1]) * w * .17, b - w * .33, w * .15))
    return c


def cumulus(u, name, masses, light_pt, cols=None, seed=1):
    """masses: list of (cx, bottom_y, width), drawn back->front in the given order."""
    cols = cols or (CL_SH, CL_MID, CL_LT, CL_HI)
    rnd = random.Random(seed)
    defs, body = [], []
    bottom = max(m[1] for m in masses)
    for i, (cx, b, w) in enumerate(masses):
        dx, dy = light_pt[0] - cx, light_pt[1] - (b - w * .3)
        d = math.hypot(dx, dy) or 1
        v = (dx / d * .55, dy / d * .55 - .8)
        d_, s_ = cel_mass(u, f"{name}{i}", dome(cx, b, w, rnd), cols, base=b if b >= bottom - 12 else None, v=v,
                          b1=max(8, w * .11), b2=max(16, w * .24), rim=max(3, w * .025))
        defs.append(d_)
        body.append(s_)
    return "".join(defs), "".join(body)


# ---------------------------------------------------------------- architecture
def roof(cx, ey, hw, tip, ry, rhw, u, name, th=13, tiles=True, hl=True):
    """Front elevation of an upturned-eave roof. Returns (defs, svg)."""
    L = (cx - hw - 22, ey - tip)
    R = (cx + hw + 22, ey - tip)
    # roof face (eave line -> hips -> ridge)
    face = (f"M{n(L[0])} {n(L[1])} Q{n(cx-hw+26)} {n(ey+2)} {n(cx-hw+110)} {n(ey)} L{n(cx+hw-110)} {n(ey)} "
            f"Q{n(cx+hw-26)} {n(ey+2)} {n(R[0])} {n(R[1])} "
            f"Q{n(cx+rhw+(hw-rhw)*.42)} {n(ey-tip*.55-6)} {n(cx+rhw)} {n(ry)} L{n(cx-rhw)} {n(ry)} "
            f"Q{n(cx-rhw-(hw-rhw)*.42)} {n(ey-tip*.55-6)} {n(L[0])} {n(L[1])}Z")
    eave = (f"M{n(L[0])} {n(L[1])} Q{n(cx-hw+26)} {n(ey+2)} {n(cx-hw+110)} {n(ey)} L{n(cx+hw-110)} {n(ey)} "
            f"Q{n(cx+hw-26)} {n(ey+2)} {n(R[0])} {n(R[1])} "
            f"L{n(R[0]-6)} {n(R[1]+th*.55)} Q{n(cx+hw-30)} {n(ey+th+2)} {n(cx+hw-110)} {n(ey+th)} "
            f"L{n(cx-hw+110)} {n(ey+th)} Q{n(cx-hw+30)} {n(ey+th+2)} {n(L[0]+6)} {n(L[1]+th*.55)}Z")
    cid = f"{u}-{name}"
    defs = f'<clipPath id="{cid}"><path d="{face}"/></clipPath>'
    o = [f'<path d="{eave}" fill="{ROOF_U}"/>', f'<path d="{face}" fill="{ROOF}"/>']
    g = []
    if tiles:
        span = hw * 2 + 40
        k = int(span / 15)
        for i in range(k + 1):
            x_e = cx - hw - 20 + span * i / k
            f = (x_e - cx) / (hw + 20)
            x_r = cx + f * rhw
            g.append(f"M{n(x_e)} {n(ey+2)} Q{n(x_e + (x_r-x_e)*.15)} {n(ry+(ey-ry)*.45)} {n(x_r)} {n(ry)}")
        o.append(f'<g clip-path="url(#{cid})"><path d="{" ".join(g)}" stroke="{ROOF_D}" stroke-width="3.2" fill="none" opacity=".55"/>')
        if hl:
            # hard-edged moonlight sheen on the upper-left slope
            sh = (f"M{n(cx-rhw-10)} {n(ry-4)} L{n(cx+rhw*.15)} {n(ry-4)} L{n(cx-rhw*.25)} {n(ry+(ey-ry)*.36)} "
                  f"L{n(cx-hw*.55)} {n(ry+(ey-ry)*.62)} L{n(cx-hw-30)} {n(ey-tip*.6)} Z")
            o.append(f'<path d="{sh}" fill="{ROOF_H}" opacity=".55"/>')
            o.append(f'<path d="M{n(cx-rhw)} {n(ry+3)} L{n(cx+rhw*.4)} {n(ry+3)} L{n(cx+rhw*.4-30)} {n(ry+8)} L{n(cx-rhw-14)} {n(ry+8)}Z" fill="#fff" opacity=".3"/>')
        o.append('</g>')
    # tile-end row along the eave (lighter cel band + round tile caps)
    band = (f"M{n(L[0])} {n(L[1])} Q{n(cx-hw+26)} {n(ey+2)} {n(cx-hw+110)} {n(ey)} L{n(cx+hw-110)} {n(ey)} "
            f"Q{n(cx+hw-26)} {n(ey+2)} {n(R[0])} {n(R[1])}")
    o.append(f'<path d="{band}" stroke="{ROOF_T}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    caps = []
    for i in range(int((2 * hw - 220) / 16) + 1):
        caps.append(f'<circle cx="{n(cx-hw+110+i*16)}" cy="{n(ey+3)}" r="2.6"/>')
    o.append(f'<g fill="{ROOF_T}">{"".join(caps)}</g>')
    # ridge + upturned hip ends
    o.append(f'<rect x="{n(cx-rhw-6)}" y="{n(ry-9)}" width="{n(2*rhw+12)}" height="11" rx="3" fill="{ROOF_D}"/>')
    o.append(f'<rect x="{n(cx-rhw-6)}" y="{n(ry-9)}" width="{n(2*rhw+12)}" height="4" rx="2" fill="{ROOF_H}"/>')
    # hip ridges (darker line along the hip edges)
    o.append(f'<path d="M{n(L[0])} {n(L[1])} Q{n(cx-rhw-(hw-rhw)*.42)} {n(ey-tip*.55-6)} {n(cx-rhw)} {n(ry)}" '
             f'stroke="{ROOF_D}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M{n(R[0])} {n(R[1])} Q{n(cx+rhw+(hw-rhw)*.42)} {n(ey-tip*.55-6)} {n(cx+rhw)} {n(ry)}" '
             f'stroke="{ROOF_D}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    # curled tips (gold)
    for sx, P in ((-1, L), (1, R)):
        o.append(f'<path d="M{n(P[0]-sx*8)} {n(P[1]+5)} q{n(sx*10)} -2 {n(sx*12)} -14 q{n(sx*1)} -6 {n(-sx*4)} -6" '
                 f'stroke="{GOLD}" stroke-width="3.4" fill="none" stroke-linecap="round"/>')
    # ridge-end ornaments (chiwen-like curls)
    for sx in (-1, 1):
        x = cx + sx * (rhw + 4)
        o.append(f'<path d="M{n(x)} {n(ry-6)} q{n(sx*2)} -22 {n(sx*-14)} -24 q{n(sx*-10)} 0 {n(sx*-8)} 10 '
                 f'q{n(sx*2)} 6 {n(sx*8)} 3" stroke="{ROOF_D}" stroke-width="7" fill="none" stroke-linecap="round"/>')
        o.append(f'<circle cx="{n(x - sx*13)}" cy="{n(ry-27)}" r="3.2" fill="{GOLD}"/>')
    return defs, "".join(o)


def lattice_panel(x, y, w, h, lit=True, k=3):
    o = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{GLOW if lit else ST_F}"/>']
    if lit:
        o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w*.45)}" height="{n(h)}" fill="{GLOW_L}" opacity=".7"/>')
    g = []
    cols = k
    rows = max(2, int(h / (w / cols)))
    for i in range(1, cols):
        g.append(f"M{n(x + w*i/cols)} {n(y)} V{n(y+h)}")
    for j in range(1, rows):
        g.append(f"M{n(x)} {n(y + h*j/rows)} H{n(x+w)}")
    o.append(f'<path d="{" ".join(g)}" stroke="{LAT}" stroke-width="1.6" opacity=".8"/>')
    o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="none" stroke="{LAT}" stroke-width="2.4"/>')
    return "".join(o)


def pillar(x, y0, y1, w=13):
    return (f'<rect x="{n(x-w/2)}" y="{n(y0)}" width="{n(w)}" height="{n(y1-y0)}" fill="{PIL}"/>'
            f'<rect x="{n(x+w/2-4)}" y="{n(y0)}" width="4" height="{n(y1-y0)}" fill="{PIL_D}"/>'
            f'<rect x="{n(x-w/2+2)}" y="{n(y0)}" width="2.4" height="{n(y1-y0)}" fill="{PIL_L}"/>')


def hanging_lantern(x, y, s=1.0, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<g transform="translate({n(x)},{n(y)}) scale({s})">'
            f'<circle{c} cx="0" cy="14" r="34" fill="url(#{_G[0]}-glw)"/>'
            f'<path d="M0 -10 V2" stroke="{ROOF_U}" stroke-width="1.6"/>'
            f'<rect x="-6" y="0" width="12" height="4" rx="1" fill="{GOLD_D}"/>'
            f'<ellipse cx="0" cy="14" rx="11" ry="12" fill="{LAN}"/>'
            f'<path d="M4 3 Q12 9 9 22 Q6 26 3 25 Q8 14 4 3Z" fill="{LAN_D}"/>'
            f'<ellipse cx="-4" cy="11" rx="3" ry="6" fill="#ffd0dd"/>'
            f'<rect x="-6" y="24" width="12" height="4" rx="1" fill="{GOLD_D}"/>'
            f'<path d="M-2 28 V36 M2 28 V35" stroke="{GOLD}" stroke-width="1.4"/>'
            f'</g>')


def hall(u):
    cx = 1030
    defs, o = [], []
    # --- stilts & deck
    posts = "".join(f'<rect x="{n(x)}" y="532" width="7" height="30" fill="{ROOF_U}"/>' for x in range(770, 1300, 34))
    o.append(posts)
    o.append(f'<rect x="756" y="530" width="552" height="6" fill="{ST_D}"/>')
    o.append(f'<path d="M748 516 H1316 L1310 532 H754Z" fill="{ST_F}"/>')
    o.append(f'<rect x="746" y="510" width="572" height="8" rx="2" fill="{ST_T}"/>')
    o.append('<path d="M754 532 H1310" stroke="#fff" stroke-width="1.5" opacity=".5"/>')
    # steps down to the water at the centre
    for i in range(4):
        o.append(f'<rect x="{n(cx-52-i*8)}" y="{n(532+i*7)}" width="{n(104+i*16)}" height="7" fill="{ST_T if i%2==0 else ST_F}"/>')
    # --- lower storey
    xs = [800 + i * 77 for i in range(7)]  # 800..1262
    o.append(f'<rect x="792" y="418" width="478" height="94" fill="{CREAM}"/>')
    for i in range(6):
        xa, xb = xs[i] + 8, xs[i + 1] - 8
        if i in (2, 3):
            # open doors: warm interior with bookshelves
            o.append(f'<rect x="{n(xa)}" y="436" width="{n(xb-xa)}" height="74" fill="{GLOW}"/>')
            o.append(f'<rect x="{n(xa)}" y="436" width="{n((xb-xa)*.5)}" height="74" fill="{GLOW_L}" opacity=".6"/>')
            for sh in range(3):
                yy = 448 + sh * 20
                o.append(f'<rect x="{n(xa+4)}" y="{n(yy+14)}" width="{n(xb-xa-8)}" height="3" fill="{LAT}"/>')
                bx = xa + 6
                rnd = random.Random(i * 10 + sh)
                while bx < xb - 10:
                    bw = rnd.choice([3, 4, 5])
                    bh = rnd.choice([10, 12, 13])
                    col = rnd.choice(["#c98aa8", "#9a8ad6", "#e0a37f", "#b6a3e0", "#d77d93"])
                    o.append(f'<rect x="{n(bx)}" y="{n(yy+14-bh)}" width="{bw}" height="{bh}" fill="{col}"/>')
                    bx += bw + 1
            o.append(f'<rect x="{n(xa)}" y="436" width="{n(xb-xa)}" height="74" fill="none" stroke="{LAT}" stroke-width="2.4"/>')
        else:
            o.append(lattice_panel(xa, 438, xb - xa, 54, True, 4))
            o.append(f'<rect x="{n(xa)}" y="492" width="{n(xb-xa)}" height="18" fill="{ST_F}"/>')
    # door curtain glow spill on deck
    o.append(f'<ellipse cx="{cx}" cy="512" rx="110" ry="8" fill="{GLOW_L}" opacity=".7"/>')
    for x in xs:
        o.append(pillar(x, 418, 512))
    # balustrade
    rail = [f'<rect x="746" y="494" width="{n(cx-60-746)}" height="4" fill="{CREAM}"/>',
            f'<rect x="{n(cx+60)}" y="494" width="{n(1318-cx-60)}" height="4" fill="{CREAM}"/>']
    for x in range(750, 1318, 18):
        if abs(x - cx) < 64:
            continue
        rail.append(f'<rect x="{x}" y="497" width="4" height="13" fill="#f4ecfb"/><rect x="{x+3}" y="497" width="1.5" height="13" fill="{ST_F}"/>')
    o.append("".join(rail))
    # beam + bracket band
    o.append(f'<rect x="784" y="404" width="494" height="16" fill="{BRK}"/>')
    o.append(f'<rect x="784" y="404" width="494" height="4" fill="#aabdf4"/>')
    o.append("".join(f'<circle cx="{x}" cy="413" r="2.3" fill="{GOLD}"/>' for x in range(796, 1272, 22)))
    o.append(f'<rect x="784" y="396" width="494" height="8" fill="{BRK_D}"/>')
    # lower roof (double eave)
    d, s = roof(cx, 396, 300, 26, 352, 200, u, "r1", th=12, hl=True)
    defs.append(d)
    o.append(s)
    # --- upper storey
    o.append(f'<rect x="880" y="300" width="300" height="56" fill="{CREAM}"/>')
    for i in range(4):
        xa = 892 + i * 72
        if i in (1, 2):
            continue
        o.append(lattice_panel(xa, 312, 60, 38, True, 4))
    # plaque (no text: abstract gold strokes)
    o.append(f'<rect x="964" y="306" width="132" height="44" rx="3" fill="{ROOF_U}" stroke="{GOLD}" stroke-width="3"/>')
    o.append(f'<rect x="970" y="312" width="120" height="32" rx="2" fill="none" stroke="{GOLD_D}" stroke-width="1.2"/>')
    o.append(f'<path d="M1030 316 l8 12 -8 12 -8 -12z" fill="{GOLD}"/><circle cx="1030" cy="328" r="3" fill="{GOLD_L}"/>')
    for sx in (-1, 1):
        o.append(f'<path d="M{1030+sx*14} 328 h{sx*12} q{sx*14} 0 {sx*14} -7 q0 -6 {sx*-6} -6 q{sx*-5} 0 {sx*-5} 5 '
                 f'M{1030+sx*40} 328 h{sx*14} q{sx*12} 0 {sx*12} 7 q0 6 {sx*-6} 6 q{sx*-5} 0 {sx*-5} -5" '
                 f'stroke="{GOLD_L}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    for x in (880, 952, 1108, 1180):
        o.append(pillar(x, 300, 356, 11))
    o.append(f'<rect x="866" y="288" width="328" height="13" fill="{BRK}"/>')
    o.append("".join(f'<circle cx="{x}" cy="295" r="2" fill="{GOLD}"/>' for x in range(876, 1190, 20)))
    o.append(f'<rect x="866" y="282" width="328" height="6" fill="{BRK_D}"/>')
    d, s = roof(cx, 282, 214, 30, 222, 112, u, "r2", th=12, hl=True)
    defs.append(d)
    o.append(s)
    # ridge jewel
    o.append(f'<path d="M{cx} 190 q10 12 0 24 q-10 -12 0 -24Z" fill="{GOLD}"/><circle cx="{cx}" cy="205" r="4" fill="{GOLD_L}"/>')
    o.append(f'<rect x="{cx-14}" y="210" width="28" height="6" rx="2" fill="{GOLD_D}"/>')
    # hanging lanterns at eave corners
    o.append(hanging_lantern(752, 384, 1.0, "lg"))
    o.append(hanging_lantern(1308, 384, 1.0, "lg"))
    o.append(hanging_lantern(842, 272, .8, "lg"))
    o.append(hanging_lantern(1218, 272, .8, "lg"))
    return "".join(defs), "".join(o)


def pavilion(u, cx=1508, base=548):
    o, defs = [], []
    o.append(f'<path d="M{cx-74} {base} H{cx+74} L{cx+68} {base+12} H{cx-68}Z" fill="{ST_F}"/>')
    o.append(f'<rect x="{cx-78}" y="{base-6}" width="156" height="8" rx="2" fill="{ST_T}"/>')
    o.append("".join(f'<rect x="{x}" y="{base+12}" width="6" height="{HZ-base-10}" fill="{ROOF_U}"/>' for x in range(cx - 64, cx + 66, 30)))
    # interior glow
    o.append(f'<rect x="{cx-52}" y="{base-70}" width="104" height="64" fill="{GLOW}" opacity=".9"/>')
    o.append(f'<rect x="{cx-52}" y="{base-70}" width="40" height="64" fill="{GLOW_L}" opacity=".6"/>')
    o.append(f'<path d="M{cx-60} {base-18} H{cx+60}" stroke="{CREAM}" stroke-width="4"/>')
    o.append("".join(f'<rect x="{x}" y="{base-16}" width="3" height="10" fill="{CREAM}"/>' for x in range(cx - 56, cx + 58, 12)))
    for x in (cx - 58, cx, cx + 58):
        o.append(pillar(x, base - 78, base - 4, 10))
    o.append(f'<rect x="{cx-72}" y="{base-86}" width="144" height="10" fill="{BRK}"/>')
    o.append(f'<rect x="{cx-72}" y="{base-90}" width="144" height="5" fill="{BRK_D}"/>')
    d, s = roof(cx, base - 90, 76, 22, base - 168, 4, u, "pv", th=10, hl=True)
    defs.append(d)
    o.append(s)
    o.append(f'<path d="M{cx} {base-206} q8 10 0 22 q-8 -10 0 -22Z" fill="{GOLD}"/>'
             f'<rect x="{cx-3}" y="{base-186}" width="6" height="18" fill="{GOLD_D}"/>'
             f'<circle cx="{cx}" cy="{base-176}" r="6" fill="{GOLD}"/>')
    o.append(hanging_lantern(cx - 92, base - 102, .75, "lg"))
    o.append(hanging_lantern(cx + 92, base - 102, .75, "lg"))
    return "".join(defs), "".join(o)


def bridge():
    # humped stone arch bridge between hall deck and pavilion
    x0, x1, top = 1312, 1438, 494
    cxb = (x0 + x1) / 2
    o = []
    o.append(f'<path d="M{x0} 536 Q{n(cxb)} {top-14} {x1} 536 L{x1} {HZ} L{n(cxb+34)} {HZ} A34 34 0 0 0 {n(cxb-34)} {HZ} L{x0} {HZ}Z" fill="{ST_F}"/>')
    o.append(f'<path d="M{x0} 536 Q{n(cxb)} {top-14} {x1} 536" stroke="{ST_T}" stroke-width="7" fill="none"/>')
    o.append(f'<path d="M{n(cxb+34)} {HZ} A34 34 0 0 0 {n(cxb-34)} {HZ}" stroke="{ST_D}" stroke-width="5" fill="none"/>')
    # railing posts following the hump
    for i in range(9):
        t = i / 8
        x = x0 + (x1 - x0) * t
        y = (1 - t) ** 2 * 536 + 2 * (1 - t) * t * (top - 14) + t ** 2 * 536
        o.append(f'<rect x="{n(x-2)}" y="{n(y-17)}" width="4" height="15" fill="#f4ecfb"/>')
    o.append(f'<path d="M{x0} 522 Q{n(cxb)} {top-28} {x1} 522" stroke="#f4ecfb" stroke-width="3" fill="none"/>')
    return "".join(o)


def tree(u, name, cx, base, w, h, rnd, trunk=True):
    """Sakura tree crown, cel shaded."""
    c = []
    for i in range(14):
        a = rnd.uniform(0, math.pi)
        rr = rnd.uniform(.55, 1)
        x = cx + math.cos(a) * w * .42 * rr
        y = base - h * .45 - math.sin(a) * h * .38 * rr
        c.append((x, y, rnd.uniform(.18, .27) * w))
    c.append((cx, base - h * .35, w * .32))
    defs, body = cel_mass(u, name, c, (SAK_DD, SAK_D, SAK, SAK_H), v=(-.5, -1), b1=w*.06, b2=w*.13, rim=3)
    o = []
    if trunk:
        o.append(f'<path d="M{n(cx-7)} {base} Q{n(cx-4)} {n(base-h*.25)} {n(cx-22)} {n(base-h*.45)} M{n(cx+2)} {base} '
                 f'Q{n(cx+4)} {n(base-h*.3)} {n(cx+26)} {n(base-h*.5)}" stroke="{BARK}" stroke-width="9" fill="none" stroke-linecap="round"/>')
        o.append(f'<rect x="{n(cx-8)}" y="{n(base-h*.22)}" width="14" height="{n(h*.22)}" fill="{BARK}"/>')
    o.append(body)
    fl = []
    for _ in range(int(w / 5)):
        a, b, r = rnd.choice(c)
        fl.append(flower(a + rnd.uniform(-r, r) * .7, b + rnd.uniform(-r, r) * .6, rnd.uniform(3.5, 5.5), rnd.uniform(0, 72), rnd.choice([0, 0, 1])))
    o.append("".join(fl))
    return defs, "".join(o)


def mountains(rnd):
    o = []
    # far range (left and right of the academy), hard-edged lit faces
    def ridge(x0, x1, peaks, ybase, col, lcol):
        p = [(x0, ybase)]
        lit = []
        for (px, py, wl, wr) in peaks:
            p += [(px - wl, ybase - 6), (px - wl * .45, py + (ybase - py) * .35), (px, py), (px + wr * .5, py + (ybase - py) * .45), (px + wr, ybase - 4)]
            lit.append([(px, py), (px - wl * .45, py + (ybase - py) * .35), (px - wl * .7, ybase - 3), (px - wl * .1, ybase - 3), (px + wr * .05, py + (ybase - py) * .5)])
        p.append((x1, ybase))
        s = f'<polygon points="{pts(p)}" fill="{col}"/>'
        s += "".join(f'<polygon points="{pts(l)}" fill="{lcol}"/>' for l in lit)
        return s
    o.append(ridge(-20, 820, [(140, 400, 150, 130), (330, 430, 120, 140), (520, 452, 110, 120), (690, 470, 90, 100)], HZ, MT_FAR, MT_FAR_L))
    o.append(ridge(1180, 1640, [(1380, 430, 160, 120), (1560, 410, 120, 120)], HZ, MT_FAR, MT_FAR_L))
    # tiny distant pagoda on the left ridge
    px, py = 140, 404
    pg = []
    for i in range(4):
        w = 22 - i * 4
        y = py - i * 11
        pg.append(f'<rect x="{n(px-w/2+3)}" y="{n(y-6)}" width="{n(w-6)}" height="6" fill="{MT_NEAR}"/>')
        pg.append(f'<path d="M{n(px-w/2-3)} {n(y-6)} Q{px} {n(y-11)} {n(px+w/2+3)} {n(y-6)}Z" fill="{ROOF}" opacity=".55"/>')
    pg.append(f'<rect x="{px-1}" y="{py-54}" width="2" height="10" fill="{ROOF}" opacity=".55"/>')
    pg.append(f'<circle cx="{px}" cy="{py-17}" r="2" fill="{GLOW}"/>')
    o.append("".join(pg))
    o.append(ridge(-20, 700, [(60, 470, 120, 110), (250, 492, 120, 130), (470, 505, 110, 120)], HZ, MT_NEAR, MT_NEAR_L))
    # low lavender treeline / far bank
    bank = [(-20, HZ)]
    x = -20
    while x < 1640:
        bank.append((x, HZ - rnd.uniform(6, 16)))
        x += rnd.uniform(18, 30)
    bank.append((1640, HZ))
    o.append(f'<polygon points="{pts(bank)}" fill="#9d90da"/>')
    return "".join(o)


def river_lantern(x, y, s, glowcls="lg"):
    """Lotus floating lantern with cel-shaded petals + glow + water reflection."""
    o = [f'<g transform="translate({n(x)},{n(y)}) scale({n(s)})">']
    o.append(f'<ellipse class="{glowcls}" cx="0" cy="-10" rx="58" ry="44" fill="url(#{_G[0]}-glw)"/>')
    # reflection streaks
    o.append(f'<g fill="{GOLD_L}" opacity=".75"><rect x="-10" y="8" width="20" height="3" rx="1.5"/><rect x="-7" y="15" width="14" height="2.6" rx="1.3"/>'
             f'<rect x="-12" y="22" width="9" height="2.2" rx="1.1"/><rect x="2" y="27" width="8" height="2" rx="1"/></g>')
    # cel ripple ring
    o.append(f'<ellipse cx="0" cy="4" rx="30" ry="6" fill="none" stroke="#eef0ff" stroke-width="2" opacity=".6"/>')
    # back petals
    o.append(f'<path d="M-22 0 Q-24 -16 -12 -20 Q-10 -8 -4 0Z M22 0 Q24 -16 12 -20 Q10 -8 4 0Z" fill="{SAK_D}"/>')
    # base
    o.append(f'<path d="M-24 0 Q0 9 24 0 Q0 4 -24 0Z" fill="{SAK_DD}"/>')
    # candle + flame
    o.append(f'<rect x="-4" y="-16" width="8" height="10" rx="1.5" fill="{CREAM}"/>')
    o.append(f'<path d="M0 -30 Q5 -22 0 -16 Q-5 -22 0 -30Z" fill="{GOLD}"/><path d="M0 -26 Q2 -21 0 -18 Q-2 -21 0 -26Z" fill="#fffbe6"/>')
    # front petals (cel: light left halves)
    o.append(f'<path d="M-18 1 Q-20 -12 -9 -16 Q-4 -6 -2 2Z" fill="{SAK}"/><path d="M-18 1 Q-20 -12 -9 -16 Q-12 -6 -10 2Z" fill="{SAK_L}"/>')
    o.append(f'<path d="M18 1 Q20 -12 9 -16 Q4 -6 2 2Z" fill="{SAK_D}"/>')
    o.append(f'<path d="M-7 3 Q-9 -12 0 -18 Q9 -12 7 3Z" fill="{SAK}"/><path d="M-7 3 Q-9 -12 0 -18 Q-2 -8 -1 3Z" fill="{SAK_H}"/>')
    o.append(f'<path d="M-20 2 Q0 8 20 2" stroke="{SAK_H}" stroke-width="1.6" fill="none" opacity=".8"/>')
    o.append('</g>')
    return "".join(o)


def stone_lantern(x, base, sc=1.0):
    """Stone lantern at the far-left edge of the boardwalk (frames the chibi area, stays at x<110)."""
    o = [f'<g transform="translate({x},{base}) scale({sc})">']
    o.append(f'<ellipse cx="0" cy="-114" rx="90" ry="80" fill="url(#{_G[0]}-glw)" class="lg"/>')
    o.append(f'<rect x="-26" y="-14" width="52" height="14" rx="2" fill="{ST_F}"/><rect x="-26" y="-14" width="20" height="14" fill="{ST_T}"/>')
    o.append(f'<rect x="-10" y="-80" width="20" height="66" fill="{ST_F}"/><rect x="-10" y="-80" width="8" height="66" fill="{ST_T}"/>')
    o.append(f'<rect x="-28" y="-92" width="56" height="12" rx="2" fill="{ST_D}"/><rect x="-28" y="-92" width="22" height="12" fill="{ST_F}"/>')
    o.append(f'<rect x="-22" y="-136" width="44" height="44" fill="{ST_F}"/><rect x="-22" y="-136" width="10" height="44" fill="{ST_T}"/>')
    o.append(f'<rect x="-13" y="-128" width="26" height="28" fill="{GLOW}"/><rect x="-13" y="-128" width="11" height="28" fill="{GLOW_L}"/>')
    o.append(f'<path d="M0 -128 V-100 M-13 -114 H13" stroke="{ST_D}" stroke-width="2"/>')
    o.append(f'<path d="M-44 -134 Q-20 -142 -14 -160 H14 Q20 -142 44 -134 Q0 -128 -44 -134Z" fill="{ROOF}"/>')
    o.append(f'<path d="M-44 -134 Q-20 -142 -14 -160 H0 Q-6 -142 -22 -133Z" fill="{ROOF_H}"/>')
    o.append(f'<path d="M-44 -134 q-4 -2 -2 -8 M44 -134 q4 -2 2 -8" stroke="{GOLD}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    o.append(f'<circle cx="0" cy="-166" r="7" fill="{ROOF_D}"/><circle cx="-2" cy="-168" r="2.5" fill="{ROOF_H}"/>')
    o.append('</g>')
    return "".join(o)


def boardwalk():
    """Front-facing lavender jetty; top surface y 806-900 on the left, right edge recedes (side face visible)."""
    o = []
    top, xr0, xr1 = 806, 566, 628
    # shadow on the water just past the far edge
    o.append(f'<path d="M-10 {top-6} H{xr0+20} L{xr0+30} {top+4} H-10Z" fill="#7f7fcf" opacity=".55"/>')
    o.append(f'<path d="M{xr0} {top} L{xr0+16} {top+6} L{xr1+22} 910 H{xr1}Z" fill="{WOOD_D}"/>')
    o.append(f'<path d="M-10 {top} H{xr0} L{xr1} 910 H-10Z" fill="{WOOD_T}"/>')
    # planks parallel to the far edge, widening toward the viewer, each with a lit top lip
    y, k, g, lips = top, 0, [], []
    while y < 900:
        hgt = 11 + k * 6
        xr = xr0 + (xr1 - xr0) * (y - top) / 104
        lips.append(f'<path d="M-10 {n(y+1)} H{n(xr)}" stroke="{WOOD_L}" stroke-width="{n(2 + k*.6)}"/>')
        y += hgt
        xr = xr0 + (xr1 - xr0) * (y - top) / 104
        g.append(f"M-10 {n(y)} H{n(xr)}")
        k += 1
    o.append("".join(lips))
    o.append(f'<path d="{" ".join(g)}" stroke="{WOOD_F}" stroke-width="2.4"/>')
    # staggered butt joints + nail dots
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
    o.append(f'<path d="{" ".join(j)}" stroke="{WOOD_F}" stroke-width="2"/>')
    # wet moonlight glints on the boards (toward the moon)
    o.append(f'<g fill="#efe6fb" opacity=".55"><rect x="470" y="{top+4}" width="60" height="3" rx="1.5"/>'
             f'<rect x="440" y="{top+19}" width="90" height="3.5" rx="1.7"/><rect x="420" y="{top+40}" width="70" height="4" rx="2"/>'
             f'<rect x="510" y="{top+42}" width="30" height="4" rx="2"/><rect x="400" y="{top+68}" width="110" height="5" rx="2.5"/></g>')
    # foreground shade toward the bottom edge
    o.append(f'<path d="M-10 860 H{n(xr0+(xr1-xr0)*54/104)} L{xr1} 910 H-10Z" fill="#4a4486" opacity=".25"/>')
    o.append(f'<path d="M-10 {top} H{xr0}" stroke="#f3eefc" stroke-width="3"/>')
    # mooring post with rope
    o.append(f'<rect x="544" y="{top-50}" width="18" height="60" rx="3" fill="{WOOD_F}"/><rect x="544" y="{top-50}" width="7" height="60" fill="{WOOD_L}"/>')
    o.append(f'<ellipse cx="553" cy="{top-50}" rx="9" ry="3.5" fill="#ded2f2"/>')
    o.append(f'<path d="M544 {top-32} q-4 6 0 10 h18 q4 -4 0 -10" stroke="{GOLD_D}" stroke-width="2.6" fill="none"/>')
    # water lap highlights along the far edge
    o.append(f'<path d="M20 {top-12} q14 -4 28 0 M150 {top-13} q18 -4 36 0 M330 {top-12} q12 -3 24 0 M600 {top-8} q10 -3 20 0" '
             f'stroke="#f2f0ff" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".8"/>')
    return "".join(o)


def flower_def(u, tone):
    """Five-petal sakura blossom (radius 10), cel shaded. tone 0 = front/lit, 1 = mid, 2 = back/shadow."""
    r = 10
    pc = [(SAK_L, SAK, SAK_H), (SAK, SAK_D, SAK_L), (SAK_D, SAK_DD, SAK)][tone]
    o = [f'<g id="{u}-fl{tone}">']
    pp = f"M0 0 C{n(-r*.55)} {n(-r*.25)} {n(-r*.6)} {n(-r*.9)} {n(-r*.2)} {n(-r)} L0 {n(-r*.82)} L{n(r*.2)} {n(-r)} C{n(r*.6)} {n(-r*.9)} {n(r*.55)} {n(-r*.25)} 0 0Z"
    sh = f"M0 0 C{n(-r*.55)} {n(-r*.25)} {n(-r*.6)} {n(-r*.9)} {n(-r*.2)} {n(-r)} L0 {n(-r*.82)}Z"
    o.append(f'<g id="{u}-pt{tone}"><path d="{pp}" fill="{pc[0]}"/><path d="{sh}" fill="{pc[1]}" opacity=".55"/></g>')
    for i in range(1, 5):
        o.append(f'<use href="#{u}-pt{tone}" transform="rotate({i*72})"/>')
    o.append(f'<circle r="{n(r*.34)}" fill="{pc[1]}"/>')
    if tone < 2:
        st = " ".join(f"M0 0 L{n(math.cos(math.radians(a))*r*.5)} {n(math.sin(math.radians(a))*r*.5)}" for a in range(-90, 270, 72))
        o.append(f'<path d="{st}" stroke="{SAK_DD}" stroke-width=".7"/>')
        o.append("".join(f'<circle cx="{n(math.cos(math.radians(a))*r*.5)}" cy="{n(math.sin(math.radians(a))*r*.5)}" r=".8" fill="{GOLD}"/>'
                         for a in range(-90, 270, 72)))
        o.append(f'<path d="M-7.5 -3.5 q1.5 -3.5 4.5 -4.2" stroke="#fff" stroke-width="1" fill="none" stroke-linecap="round" opacity=".8"/>')
    o.append('</g>')
    return "".join(o)


def flower(x, y, r, rot, tone=0):
    return f'<use href="#{_G[0]}-fl{tone}" transform="translate({n(x)},{n(y)}) rotate({n(rot)}) scale({r/10:.2f})"/>'


def sakura_branch(u, rnd):
    """Foreground framing branch from the top-left corner (stays at x<430, y<190): individual cel blossoms."""
    o = []
    o.append(f'<path d="M-20 30 Q120 50 230 30 Q300 18 392 48 M118 44 Q168 86 156 146 M236 30 Q262 66 304 90 M56 38 Q72 8 112 -12 '
             f'M330 30 Q350 8 380 4" stroke="{BARK}" stroke-width="9" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M-20 26 Q120 45 230 25 Q300 13 392 44" stroke="#8d76bd" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    nodes = [(26, 26, 36), (100, 14, 30), (164, 44, 38), (150, 132, 28), (236, 26, 30), (306, 88, 28), (384, 46, 26), (64, 66, 26), (360, 10, 20)]
    back, mid, front = [], [], []
    for (cx, cy, rr) in nodes:
        for _ in range(9):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, rr)
            fx, fy = cx + math.cos(a) * d, cy + math.sin(a) * d * .8
            r = rnd.uniform(8, 13)
            t = rnd.random()
            (back if t < .3 else mid if t < .62 else front).append(flower(fx, fy, r, rnd.uniform(0, 72), 2 if t < .3 else 1 if t < .62 else 0))
        # buds
        for _ in range(2):
            bx, by = cx + rnd.uniform(-rr, rr), cy + rnd.uniform(-rr, rr) * .8
            front.append(f'<ellipse cx="{n(bx)}" cy="{n(by)}" rx="3.6" ry="5" fill="{SAK_D}"/><ellipse cx="{n(bx-1)}" cy="{n(by-1.5)}" rx="1.6" ry="2.4" fill="{SAK_L}"/>')
    o += back + mid + front
    return "".join(flower_def(u, t) for t in range(3)), "".join(o)


# ---------------------------------------------------------------- the scene
def scene_nwa(x=0, y=0, s=1.0, uid="nwa", animate=True):
    u = uid
    _G[0] = uid
    rnd = random.Random(29)
    defs, out = [], []
    MX, MY, MR = 600, 190, 86  # moon

    # gradients
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in SKY)
    defs.append(f'<linearGradient id="{u}-sky" x1="0" y1="0" x2="0" y2="{HZ}" gradientUnits="userSpaceOnUse">{stops}</linearGradient>')
    defs.append(f'<radialGradient id="{u}-mglow" cx="{MX}" cy="{MY}" r="420" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fffbef" stop-opacity=".95"/><stop offset=".22" stop-color="#fff1f2" stop-opacity=".55"/>'
                f'<stop offset=".55" stop-color="#f0dcf6" stop-opacity=".18"/><stop offset="1" stop-color="#e8d8f8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-moon" cx="{MX-24}" cy="{MY-26}" r="{MR*1.3}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fffef8"/><stop offset=".7" stop-color="#fff5dc"/><stop offset="1" stop-color="#ffe6c4"/></radialGradient>')
    defs.append(f'<linearGradient id="{u}-water" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#f3d2e8"/><stop offset=".18" stop-color="#cdb9f0"/><stop offset=".55" stop-color="#a6a3e8"/>'
                f'<stop offset="1" stop-color="#7a7ed2"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-tint" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#e9d3f2" stop-opacity=".15"/><stop offset=".5" stop-color="#a9a5ea" stop-opacity=".35"/>'
                f'<stop offset="1" stop-color="#8a8cdb" stop-opacity=".55"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-ray" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fffaf0" stop-opacity=".5"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/></linearGradient>')
    defs.append(f'<linearGradient id="{u}-mist" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fbe4ef" stop-opacity="0"/><stop offset="1" stop-color="#fbe4ef" stop-opacity=".85"/></linearGradient>')
    defs.append(f'<radialGradient id="{u}-vig" cx="800" cy="430" r="980" gradientUnits="userSpaceOnUse">'
                f'<stop offset=".62" stop-color="#6f6fc8" stop-opacity="0"/><stop offset="1" stop-color="#6f6fc8" stop-opacity=".28"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-glw"><stop offset="0" stop-color="#fff4c8" stop-opacity="1"/>'
                f'<stop offset=".3" stop-color="#ffe2a6" stop-opacity=".5"/><stop offset="1" stop-color="#ffd8b0" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-b1"><stop offset="0" stop-color="#ffd6e8" stop-opacity=".16"/><stop offset=".8" stop-color="#ffd6e8" stop-opacity=".2"/>'
                f'<stop offset=".95" stop-color="#fff0f6" stop-opacity=".26"/><stop offset="1" stop-color="#fff0f6" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-b2"><stop offset="0" stop-color="#ffeec4" stop-opacity=".16"/><stop offset=".8" stop-color="#ffe6b8" stop-opacity=".2"/>'
                f'<stop offset=".95" stop-color="#fff6dc" stop-opacity=".26"/><stop offset="1" stop-color="#fff6dc" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-hglow" cx="1030" cy="440" r="330" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#ffe6b8" stop-opacity=".45"/><stop offset="1" stop-color="#ffe6b8" stop-opacity="0"/></radialGradient>')

    # ---- sky
    out.append(f'<rect width="{W}" height="{HZ+2}" fill="url(#{u}-sky)"/>')
    out.append(f'<rect width="{W}" height="{HZ+2}" fill="url(#{u}-mglow)"/>')
    st = []
    for _ in range(90):
        sx, sy = rnd.uniform(0, W), rnd.uniform(0, 330)
        if math.hypot(sx - MX, sy - MY) < 200:
            continue
        st.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(rnd.uniform(.8, 2.0))}" fill="#fffaf6" opacity="{n(rnd.uniform(.5, .95))}"/>')
    out.append(f'<g>{"".join(st)}</g>')
    for (sx, sy, r) in [(180, 220, 9), (900, 70, 11), (1450, 70, 8), (330, 80, 7), (780, 330, 6), (1240, 140, 7), (60, 300, 6)]:
        out.append(sparkle(sx, sy, r, "#fffaf0", .95, "tw"))

    # ---- moon with halo rings (cel-style: crisp rings, flat crater shapes)
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+70}" fill="#fff8fb" opacity=".16"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+34}" fill="#fff8fb" opacity=".22"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR+128}" fill="none" stroke="#fff6fb" stroke-width="2" opacity=".35"/>')
    out.append(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="url(#{u}-moon)"/>')
    out.append(f'<path d="M{MX+MR*.2} {MY-MR*.97} A{MR} {MR} 0 0 1 {MX+MR*.2} {MY+MR*.97} A{MR*.86} {MR*.98} 0 0 0 {MX+MR*.2} {MY-MR*.97}Z" fill="#fbe0cf" opacity=".55"/>')
    out.append(f'<path d="M{MX-46} {MY-30} q18 -14 34 -4 q10 10 -2 20 q-14 6 -22 16 q-12 6 -16 -8 q-6 -14 6 -24Z" fill="#f4dccf" opacity=".45"/>')
    out.append(f'<path d="M{MX+8} {MY+18} q20 -8 30 6 q6 16 -10 22 q-18 4 -24 -8 q-4 -12 4 -20Z" fill="#f4dccf" opacity=".4"/>')
    out.append(f'<path d="M{MX+26} {MY-48} q12 -4 18 4 q2 10 -8 12 q-12 0 -10 -16Z" fill="#f4dccf" opacity=".35"/>')
    out.append(f'<path d="M{MX-62} {MY-34} A70 70 0 0 1 {MX-20} {MY-74}" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" opacity=".8"/>')

    # ---- wispy stratus streaks (flat anime bands)
    ws = []
    for (x0, y0, w, h) in [(-40, 124, 380, 16), (840, 118, 440, 15), (1240, 262, 330, 12), (300, 304, 300, 11), (700, 286, 220, 9)]:
        x1, xm = x0 + w, x0 + w * .45
        ws.append(f'<path d="M{x0} {y0} Q{n(xm)} {y0-h} {x1} {y0} Q{n(xm)} {n(y0+h*.35)} {x0} {y0}Z" fill="{CL_MID}" opacity=".85"/>')
        ws.append(f'<path d="M{x0+8} {y0-1} Q{n(xm)} {n(y0-h*.95)} {x1-6} {y0-1} Q{n(xm)} {n(y0-h*.3)} {x0+8} {y0-1}Z" fill="{CL_HI}" opacity=".9"/>')
    out.append("".join(ws))

    # ---- reflected group 1: big cumulus clouds
    cdefs, cl = [], []
    M = (600, 190)
    for nm, masses, sd in [
        ("cuR", [(1430, 200, 190), (1330, 236, 170), (1540, 236, 210), (1260, 330, 190), (1400, 318, 250), (1580, 332, 230),
                 (1200, 420, 200), (1330, 412, 240), (1500, 420, 300), (1620, 440, 200), (1160, 492, 220), (1330, 496, 330),
                 (1520, 496, 300)], 7),
        ("cuL", [(150, 360, 210), (300, 392, 230), (40, 400, 200), (420, 440, 200), (200, 446, 290), (60, 500, 300),
                 (330, 506, 330), (500, 506, 180)], 8),
        ("cuM", [(760, 476, 150), (690, 508, 170), (850, 510, 190)], 9),
        ("cuS", [(1040, 160, 120), (985, 170, 70)], 10)]:
        d, b = cumulus(u, nm, masses, M, seed=sd)
        cdefs.append(d); cl.append(b)
    defs.extend(cdefs)
    defs.append(f'<g id="{u}-R1">{"".join(cl)}</g>')
    out.append(f'<use href="#{u}-R1"/>')

    # ---- light rays from the moon
    rays = []
    for ang, wdeg, ln, op in [(62, 3.2, 820, .55), (78, 2.0, 760, .45), (96, 3.6, 860, .5), (112, 1.8, 700, .4), (128, 2.6, 760, .38), (45, 1.6, 640, .35)]:
        a0, a1 = math.radians(ang - wdeg / 2), math.radians(ang + wdeg / 2)
        p = [(MX + math.cos(a0) * 70, MY + math.sin(a0) * 70), (MX + math.cos(a0) * ln, MY + math.sin(a0) * ln),
             (MX + math.cos(a1) * ln, MY + math.sin(a1) * ln), (MX + math.cos(a1) * 70, MY + math.sin(a1) * 70)]
        rays.append(f'<polygon points="{pts(p)}" fill="url(#{u}-ray)" opacity="{op}"/>')
    out.append(f'<g class="ry">{"".join(rays)}</g>')

    # ---- reflected group 2: mountains, trees, academy
    mt = mountains(rnd)
    trnd = random.Random(11)
    td1, t1 = tree(u, "t1", 774, 512, 150, 190, trnd)
    td2, t2 = tree(u, "t2", 1350, 520, 130, 160, trnd)
    td3, t3 = tree(u, "t3", 1590, 548, 120, 170, trnd)
    hd, hs = hall(u)
    pd, ps = pavilion(u)
    defs += [td1, td2, td3, hd, pd]
    defs.append(f'<g id="{u}-R2">{mt}<rect x="0" y="{HZ-70}" width="{W}" height="72" fill="url(#{u}-mist)"/>'
                f'<rect x="0" y="0" width="{W}" height="{HZ}" fill="url(#{u}-hglow)"/>'
                f'{t1}{t3}{t2}{bridge()}{ps}{hs}</g>')

    # ---- water
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{u}-water)"/>')
    # broken mirror reflection: horizontal slices, each shifted a little (classic anime water)
    yy, i = HZ, 0
    refl = []
    while yy < H:
        hgt = 3 + (yy - HZ) / (H - HZ) * 20
        amp = .6 + (yy - HZ) / (H - HZ) * 9
        dx = amp * math.sin(i * 1.9) + amp * .4 * math.sin(i * 0.7 + 1)
        cid = f"{u}-ws{i}"
        defs.append(f'<clipPath id="{cid}"><rect x="-20" y="{n(yy)}" width="{W+40}" height="{n(hgt+.6)}"/></clipPath>')
        refl.append(f'<g clip-path="url(#{cid})"><g transform="translate({n(dx)},{2*HZ}) scale(1,-1)">'
                    f'<use href="#{u}-R1" opacity=".75"/><use href="#{u}-R2"/></g></g>')
        yy += hgt
        i += 1
    out.append(f'<g opacity=".62">{"".join(refl)}</g>')
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{u}-tint)"/>')

    # moon glitter path on the water
    gl = []
    grnd = random.Random(3)
    yy = HZ + 6
    while yy < H:
        t = (yy - HZ) / (H - HZ)
        w = 8 + t * 70 * grnd.uniform(.5, 1.1)
        xx = MX + grnd.uniform(-1, 1) * (10 + t * 40)
        gl.append(f'<ellipse cx="{n(xx)}" cy="{n(yy)}" rx="{n(w)}" ry="{n(1.2 + t*2.4)}" fill="#fff8e6" opacity="{n(grnd.uniform(.55, .95))}"/>')
        if grnd.random() < .5:
            gl.append(f'<ellipse cx="{n(xx + grnd.uniform(-1,1)*w*1.6)}" cy="{n(yy+3)}" rx="{n(w*.4)}" ry="{n(1 + t*1.5)}" fill="#fff8e6" opacity=".55"/>')
        yy += 6 + t * 18
    out.append(f'<g class="gl">{"".join(gl)}</g>')
    # warm window light columns under the academy
    wc = []
    for cxw in (838, 915, 992, 1069, 1146, 1223, 1508):
        yy = HZ + 6
        k = 0
        while yy < 760:
            wc.append(f'<rect x="{n(cxw - 9 + (k%3-1)*4)}" y="{n(yy)}" width="{n(18 - k*0.6)}" height="2.6" rx="1.3" fill="{GOLD_L}" opacity="{n(max(.15, .8 - k*.06))}"/>')
            yy += 9 + k * 1.6
            k += 1
    out.append(f'<g class="gl2">{"".join(wc)}</g>')
    # cel-shaded ripples: light lens over dark lens
    rp = []
    rr = random.Random(5)
    for _ in range(70):
        xx = rr.uniform(0, W)
        yy = rr.uniform(HZ + 10, H - 10)
        if xx < 600 and yy > 780:
            continue
        t = (yy - HZ) / (H - HZ)
        w = 12 + t * 70 * rr.uniform(.5, 1)
        h = 1.6 + t * 3
        rp.append(f'<path d="M{n(xx-w)} {n(yy)} Q{n(xx)} {n(yy-h*2)} {n(xx+w)} {n(yy)} Q{n(xx)} {n(yy-h*.6)} {n(xx-w)} {n(yy)}Z" fill="#f4f2ff" opacity=".75"/>')
        rp.append(f'<path d="M{n(xx-w*.8+w*.3)} {n(yy+h*1.6)} Q{n(xx+w*.3)} {n(yy+h*3.4)} {n(xx+w*.8+w*.3)} {n(yy+h*1.6)} Q{n(xx+w*.3)} {n(yy+h*2.2)} {n(xx-w*.8+w*.3)} {n(yy+h*1.6)}Z" fill="#7c7fd2" opacity=".35"/>')
    out.append("".join(rp))
    # horizon shine line
    out.append(f'<rect x="0" y="{HZ}" width="{W}" height="2" fill="#fff4f8" opacity=".85"/>')
    # long thin distance shimmer lines near the horizon
    ln = []
    lr = random.Random(8)
    for _ in range(16):
        yy = HZ + 6 + lr.random() ** 1.6 * 80
        x0 = lr.uniform(-50, 1500)
        ln.append(f'<rect x="{n(x0)}" y="{n(yy)}" width="{n(lr.uniform(80, 260))}" height="1.4" fill="#fff6fb" opacity="{n(lr.uniform(.35, .7))}"/>')
    out.append("".join(ln))
    # petals resting on the water (flattened)
    fp = []
    for (px, py, ps, rot) in [(640, 790, 9, 20), (860, 700, 7, -40), (1180, 830, 10, 70), (1350, 640, 6, 10), (980, 860, 9, -10), (560, 700, 6, 50)]:
        fp.append(f'<g transform="translate({px},{py}) scale(1,.45)">{petal(0, 0, ps, rot)}</g>')
    out.append("".join(fp))

    # ---- academy complex (above the water)
    out.append(f'<use href="#{u}-R2"/>')

    # ---- floating lotus lanterns (kept out of the chibi zone)
    for (lx, ly, ls) in [(560, 586, .45), (700, 610, .6), (880, 598, .5), (1180, 594, .48), (1400, 606, .55),
                         (1560, 640, .75), (790, 680, .85), (1290, 676, .9), (1010, 744, 1.1), (1470, 800, 1.4), (735, 832, 1.25)]:
        out.append(river_lantern(lx, ly, ls))

    # ---- foreground boardwalk (chibi stands here) + stone lantern at far left
    out.append(boardwalk())
    out.append(stone_lantern(64, 822, 1.18))

    # ---- framing sakura branch
    bd, bs = sakura_branch(u, random.Random(13))
    defs.append(bd)
    out.append(bs)

    # ---- drifting petals + sparkles
    prnd = random.Random(21)
    pts_ = [(260, 260), (420, 380), (700, 420), (860, 180), (1180, 330), (1380, 240), (1500, 420), (980, 520), (560, 520),
            (330, 620), (1100, 820), (1520, 560), (180, 470), (640, 300), (1280, 470), (40, 560), (900, 640), (1560, 180)]
    pet = []
    for k, (px, py) in enumerate(pts_):
        pet.append(petal(px, py, prnd.uniform(6, 12) * (1.4 if py > 600 else 1), prnd.uniform(0, 360), f"pf pf{k%4}"))
    out.append("".join(pet))
    for (sx, sy, r) in [(1000, 640, 7), (1240, 560, 6), (640, 700, 8), (1360, 740, 6), (860, 760, 5), (1580, 760, 7)]:
        out.append(sparkle(sx, sy, r, "#fffaf0", .95, "tw"))

    sp = []
    srnd = random.Random(41)
    for _ in range(26):
        sx, sy = srnd.uniform(700, 1560), srnd.uniform(240, 560)
        sp.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(srnd.uniform(1.2, 2.6))}" fill="{GOLD_L}" opacity="{n(srnd.uniform(.6, 1))}"/>')
    out.append(f'<g class="tw2">{"".join(sp)}</g>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#{u}-vig)"/>')

    css = ""
    if animate:
        css = (f'<style>'
               f'#{u}-root .tw{{animation:{u}tw 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}'
               f'#{u}-root .tw:nth-of-type(3n){{animation-delay:-1.1s}}#{u}-root .tw:nth-of-type(3n+1){{animation-delay:-2.2s}}'
               f'#{u}-root .lg{{animation:{u}lg 2.6s ease-in-out infinite}}#{u}-root .tw2{{animation:{u}gl 2.2s ease-in-out infinite}}'
               f'#{u}-root .gl{{animation:{u}gl 4s ease-in-out infinite}}#{u}-root .gl2{{animation:{u}gl 3s ease-in-out infinite -1s}}'
               f'#{u}-root .pf{{animation:{u}pf 9s linear infinite;transform-box:fill-box;transform-origin:center}}'
               f'#{u}-root .pf1{{animation-delay:-2.3s;animation-duration:11s}}#{u}-root .pf2{{animation-delay:-4.6s;animation-duration:10s}}'
               f'#{u}-root .pf3{{animation-delay:-6.9s;animation-duration:12s}}'
               f'@keyframes {u}tw{{0%,100%{{opacity:.95;transform:scale(1)}}50%{{opacity:.35;transform:scale(.6)}}}}'
               f'@keyframes {u}lg{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}'
               f'@keyframes {u}gl{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}'
               f'@keyframes {u}pf{{0%{{transform:translate(0,0) rotate(0deg);opacity:1}}80%{{opacity:1}}'
               f'100%{{transform:translate(-70px,120px) rotate(300deg);opacity:0}}}}'
               f'@media (prefers-reduced-motion: reduce){{#{u}-root *{{animation:none!important}}}}'
               f'</style>')
    tr = f' transform="translate({n(x)},{n(y)}) scale({s})"' if (x or y or s != 1) else ""
    return (f'<g id="{u}-root"{tr}>{css}<defs>{"".join(defs)}</defs>{"".join(out)}</g>')


def build_svg(uid="nwa", rx=28):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Anime illustration: a lantern-lit Chinese academy hall on still water under a big moon">'
            f'<defs><clipPath id="{uid}-card"><rect width="{W}" height="{H}" rx="{rx}"/></clipPath></defs>'
            f'<rect width="{W}" height="{H}" rx="{rx}" fill="#a3a2ee"/>'
            f'<g clip-path="url(#{uid}-card)">{scene_nwa(uid=uid)}</g></svg>')


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "scene_nwa.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(p, os.path.getsize(p) // 1024, "KB")
