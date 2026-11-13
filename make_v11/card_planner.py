"""Course-planner card: a sunny pastel study corner at golden hour (1600x900, full bleed).

"The model proposes, a checker decides": a periwinkle chalkboard holds a three-term plan
(FALL / WINTER / SPRING) of paper course notes joined by thin prerequisite lines.  One
FALL placement is crossed out in pink and a dotted chalk arc leads to SPRING, where the slot
glows with a gold check.  Official chibi Hu Tao (a Genshin Impact "Paimon's Paintings" emoji,
(c) HoYoverse, embedded from art/ by art.py) studies a book by the window.  Board tasks are hand-pinned paper notes with squiggle "writing".

    build(out_dir) -> path      writes card-planner.svg into out_dir
    card(uid="pl") -> str       the standalone SVG document
Running this file writes a debug copy to the scratchpad (never into the repo).
Python 3 stdlib only.  No text other than the three term labels, no script.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import art as ART  # noqa: E402

W, H, RX = 1600, 900, 28
FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"
DEBUG_OUT = ("/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/"
             "scratchpad/v11/planner/card-planner.svg")

INK = "#3b3470"        # deep indigo ink
PLUM = "#4a2550"       # plum ink
CREAM = "#fff7ea"
GOLD = "#ffd27a"
GOLD_D = "#f2a65a"
GOLD_L = "#fff1c4"
PINK = "#ff7aa8"
PINK_D = "#d9487c"
SAKURA = "#f7a9c4"
SAKURA_L = "#ffd6e4"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def sparkle(cx, cy, r, fill, op=1.0, cls=""):
    k = r * 0.2
    d = (f"M{f(cx)} {f(cy - r)} Q{f(cx + k)} {f(cy - k)} {f(cx + r)} {f(cy)} "
         f"Q{f(cx + k)} {f(cy + k)} {f(cx)} {f(cy + r)} Q{f(cx - k)} {f(cy + k)} {f(cx - r)} {f(cy)} "
         f"Q{f(cx - k)} {f(cy - k)} {f(cx)} {f(cy - r)}Z")
    c = f' class="{cls}"' if cls else ""
    o = f' opacity="{op}"' if op < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}{c}/>'


def rrect(x, y, w, h, r):
    return f"M{f(x + r)} {f(y)} H{f(x + w - r)} Q{f(x + w)} {f(y)} {f(x + w)} {f(y + r)} V{f(y + h - r)} " \
           f"Q{f(x + w)} {f(y + h)} {f(x + w - r)} {f(y + h)} H{f(x + r)} Q{f(x)} {f(y + h)} {f(x)} {f(y + h - r)} " \
           f"V{f(y + r)} Q{f(x)} {f(y)} {f(x + r)} {f(y)}Z"


# ------------------------------------------------------------------ cumulus
def cumulus(u, key, lobes, base_y, shade_d, pal, light=(-0.95, -0.3), rim_w=6, hi=None, back=None, back_w=3):
    """Anime cumulus, shaded the siderius way: one silhouette (union of lobes) with a flat base,
    a flat lit cream top, a warm sun rim along the light-facing contour, ONE flat lavender shadow
    plane (shade_d, a hand-drawn region on the far side, clipped to the silhouette), a flat
    underside band and a deep base line.  No per-lobe crescents.
    pal = (lit, rim, shadow, under, deep); hi = optional path of a small hard white highlight;
    back = optional pale colour for a thin bounce-light edge on the shadow-side contour."""
    lit, rim, shadow, under, deep = pal
    lx, ly = light
    n = math.hypot(lx, ly)
    lx, ly = lx / n, ly / n
    cid = f"{u}-{key}"
    sil = "".join(f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r)}"/>' for a, b, r in lobes)
    minx = min(a - r for a, b, r in lobes) - 4
    maxx = max(a + r for a, b, r in lobes) + 4
    top = min(b - r for a, b, r in lobes) - 4
    o = [f'<clipPath id="{cid}s">{sil}</clipPath>',
         f'<clipPath id="{cid}b"><rect x="{f(minx)}" y="{f(top)}" width="{f(maxx - minx)}" height="{f(base_y - top)}"/></clipPath>']
    bb = f'x="{f(minx)}" y="{f(top)}" width="{f(maxx - minx)}" height="{f(base_y - top + 4)}"'
    # rim colour everywhere, then the lit body nudged away from the light -> rim only on the sun side
    g = [f'<rect {bb} fill="{rim}"/>',
         "".join(f'<circle cx="{f(a - lx * rim_w)}" cy="{f(b - ly * rim_w)}" r="{f(r)}" fill="{lit}"/>' for a, b, r in lobes)]
    if hi:
        g.append(f'<path d="{hi}" fill="#fffdf8"/>')
    g.append(f'<path d="{shade_d}" fill="{shadow}"/>')
    if back:   # thin pale edge where the shadow side meets the sky (silhouette minus itself shifted to the light)
        o.append(f'<mask id="{cid}m" maskUnits="userSpaceOnUse" {bb}><rect {bb} fill="#fff"/>'
                 + "".join(f'<circle cx="{f(a + lx * back_w)}" cy="{f(b + ly * back_w)}" r="{f(r)}" fill="#000"/>' for a, b, r in lobes)
                 + '</mask>')
        g.append(f'<path d="{shade_d}" fill="{back}" mask="url(#{cid}m)"/>')
    # flat underside: broad, shallow scallops (bottom ~22%), then a thin deep base line
    rnd = random.Random(sum(map(ord, key)))
    band = (base_y - top) * .11
    pts = [f"M{f(minx)} {f(base_y + 2)}", f"L{f(minx)} {f(base_y - band)}"]
    xx = minx
    while xx < maxx:
        w = rnd.uniform(56, 84)
        pts.append(f"Q{f(xx + w / 2)} {f(base_y - band * rnd.uniform(1.3, 1.6))} {f(min(xx + w, maxx))} {f(base_y - band)}")
        xx += w
    pts.append(f"L{f(maxx)} {f(base_y + 2)}Z")
    g.append(f'<path d="{" ".join(pts)}" fill="{under}"/>')
    g.append(f'<rect x="{f(minx)}" y="{f(base_y - 4)}" width="{f(maxx - minx)}" height="6" fill="{deep}"/>')
    o.append(f'<g clip-path="url(#{cid}b)"><g clip-path="url(#{cid}s)">{"".join(g)}</g></g>')
    return "".join(o)


# ------------------------------------------------------------------ sakura
def blossom(x, y, r, rot=0, shade=False):
    """five-petal cel sakura with notched petals"""
    s = [f'<g transform="translate({f(x)} {f(y)}) rotate({rot})">']
    pet = (f"M0 0 C{f(-r * .55)} {f(-r * .25)} {f(-r * .6)} {f(-r * .85)} {f(-r * .18)} {f(-r * 1.02)} "
           f"L0 {f(-r * .84)} L{f(r * .18)} {f(-r * 1.02)} C{f(r * .6)} {f(-r * .85)} {f(r * .55)} {f(-r * .25)} 0 0Z")
    base = "#f6a2c0" if shade else "#ffc4d8"
    for i in range(5):
        s.append(f'<path d="{pet}" transform="rotate({i * 72})" fill="{base}" stroke="#c75d8c" stroke-width="{f(max(.8, r * .07))}" stroke-linejoin="round"/>')
    for i in range(5):
        s.append(f'<path d="M0 {f(-r * .2)} C{f(r * .3)} {f(-r * .4)} {f(r * .32)} {f(-r * .75)} {f(r * .12)} {f(-r * .92)} '
                 f'C{f(r * .05)} {f(-r * .6)} {f(r * .05)} {f(-r * .4)} 0 {f(-r * .2)}Z" transform="rotate({i * 72})" '
                 f'fill="{"#ffd9e6" if shade else "#fff0f5"}"/>')
    s.append(f'<circle r="{f(r * .3)}" fill="#ff6f9a"/>')
    for i in range(5):
        a = math.radians(i * 72 + 36)
        s.append(f'<circle cx="{f(math.cos(a) * r * .42)}" cy="{f(math.sin(a) * r * .42)}" r="{f(r * .07)}" fill="{GOLD}"/>')
    s.append('</g>')
    return "".join(s)


def bud(x, y, r, rot):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({rot})">'
            f'<path d="M0 {f(r)} C{f(-r)} {f(r * .2)} {f(-r * .6)} {f(-r)} 0 {f(-r * 1.2)} C{f(r * .6)} {f(-r)} {f(r)} {f(r * .2)} 0 {f(r)}Z" '
            f'fill="#ff9fc0" stroke="#c75d8c" stroke-width="1"/>'
            f'<path d="M0 {f(r * .6)} C{f(r * .5)} 0 {f(r * .4)} {f(-r * .6)} 0 {f(-r)}" fill="none" stroke="#ffe0ea" stroke-width="1.4"/></g>')


def petal(px, py, sz, rot, cls):
    d = (f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} "
         f"C{f(-sz * .75)} {f(sz * .3)} {f(-sz * .7)} {f(-sz * .8)} 0 {f(-sz)}Z")
    hl = (f"M0 {f(-sz)} C{f(sz * .7)} {f(-sz * .8)} {f(sz * .75)} {f(sz * .3)} 0 {f(sz)} "
          f"C{f(sz * .25)} {f(sz * .2)} {f(sz * .25)} {f(-sz * .5)} 0 {f(-sz)}Z")
    return (f'<g class="{cls}"><g transform="translate({f(px)} {f(py)}) rotate({rot})">'
            f'<path d="{d}" fill="{SAKURA}"/><path d="{hl}" fill="{SAKURA_L}"/>'
            f'<path d="M{f(-sz * .18)} {f(-sz * 1.02)} L0 {f(-sz * .7)} L{f(sz * .18)} {f(-sz * 1.02)}Z" fill="#e98bb2"/>'
            f'</g></g>')


# ------------------------------------------------------------------ board pieces
def squiggle(x, y, length, amp, seed, col, w=4.2, op=1.0):
    """A handwritten-looking chalk-pen scribble (no real letters): word-sized runs of small
    uneven humps and loops with tiny gaps between 'words'."""
    rnd = random.Random(seed)
    d = []
    xx = x
    end = x + length
    while xx < end - 14:
        wl = min(rnd.uniform(26, 52), end - xx)
        d.append(f"M{f(xx)} {f(y + rnd.uniform(-1, 1))}")
        cx = xx
        while cx < xx + wl - 4:
            st = rnd.uniform(6.5, 10)
            up = amp * rnd.uniform(.55, 1.25)
            if rnd.random() < .16:   # a little loop (like an 'l' or 'e')
                d.append(f"C{f(cx + st * 1.1)} {f(y - up * 1.6)} {f(cx - st * .3)} {f(y - up * 1.6)} {f(cx + st * .7)} {f(y + .5)}")
            else:
                d.append(f"Q{f(cx + st / 2)} {f(y - up)} {f(cx + st)} {f(y + rnd.uniform(-.6, 1.2))}")
            cx += st
        xx = cx + rnd.uniform(9, 14)
    o = f' opacity="{op}"' if op < 1 else ""
    return (f'<path d="{" ".join(d)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" '
            f'stroke-linejoin="round"{o}/>')


def course_block(x, y, w, h, col, seed, u, pin="#ff8fb4", rot=0.0):
    """A pastel paper note held to the board by a round magnet: a slightly uneven hand-cut
    outline, a folded corner, a small cast shadow on the board and two handwritten squiggle
    lines (no real text).  (x, y) = top-left of the unrotated note; rot = degrees about its centre."""
    rnd = random.Random(seed)
    body, shade, line = col
    F = 17                      # dog-ear size (bottom-right corner)

    def j(v, k=1.3):
        return v + rnd.uniform(-k, k)
    # hand-cut outline: corners and edge midpoints jittered by about a pixel
    pts = [(j(x), j(y)), (x + w * .5, j(y, 1.6)), (j(x + w), j(y)), (j(x + w, 1.6), y + (h - F) * .5),
           (x + w, y + h - F), (x + w - F, y + h), (x + w * .45, j(y + h, 1.6)), (j(x), j(y + h)),
           (j(x, 1.6), y + h * .5)]
    paper = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts) + "Z"
    cx, cy = x + w / 2, y + h / 2
    o = [f'<g transform="rotate({rot} {f(cx)} {f(cy)})">',
         # cast shadow on the board (offset down-right, away from the window light)
         f'<path d="{paper}" transform="translate(5 8)" fill="#2f2a63" opacity=".3"/>',
         f'<path d="{paper}" fill="{body}"/>']
    # flat cel shade along the bottom edge of the paper (hard edge)
    o.append(f'<path d="M{f(x)} {f(y + h - 11)} L{f(x + w - F + 4)} {f(y + h - 13)} L{f(x + w - F)} {f(y + h)} '
             f'L{f(x + w * .45)} {f(y + h)} L{f(x)} {f(y + h)}Z" fill="{shade}" opacity=".7"/>')
    # top-left light catch
    o.append(f'<path d="M{f(x + 7)} {f(y + h - 20)} L{f(x + 7)} {f(y + 8)} L{f(x + w * .5)} {f(y + 7)}" '
             f'fill="none" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>')
    o.append(f'<path d="{paper}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    # folded corner: the flap, its shade, and the crease
    fx0, fy0 = x + w, y + h - F
    fx1, fy1 = x + w - F, y + h
    o.append(f'<path d="M{f(fx0)} {f(fy0)} L{f(fx1 + 2)} {f(fy0 + 2)} L{f(fx1)} {f(fy1)}Z" fill="{shade}" '
             f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
             f'<path d="M{f(fx0 - 4)} {f(fy0 + 3)} L{f(fx1 + 4)} {f(fy0 + 4)}" stroke="#ffffff" stroke-width="2" '
             f'stroke-linecap="round" opacity=".8"/>')
    # handwriting: a bullet tick + two scribbled lines of different length
    l1 = w * rnd.uniform(.56, .66)
    l2 = w * rnd.uniform(.32, .46)
    by = y + h * .42
    o.append(f'<path d="M{f(x + 16)} {f(by - 1)} q4 6 8 0" fill="none" stroke="{line}" stroke-width="4" stroke-linecap="round"/>')
    o.append(squiggle(x + 34, by, l1, 6.5, seed * 7 + 1, line, 3.8))
    o.append(squiggle(x + 34, by + 21, l2, 5.5, seed * 7 + 2, line, 3.4, .7))
    # round magnet holding it to the board
    mx = x + w - 30
    o.append(f'<circle cx="{f(mx + 2)}" cy="{f(y + 6)}" r="9" fill="#2f2a63" opacity=".25"/>'
             f'<circle cx="{f(mx)}" cy="{f(y + 3)}" r="9" fill="{pin}" stroke="{INK}" stroke-width="2.2"/>'
             f'<circle cx="{f(mx - 2.5)}" cy="{f(y)}" r="3" fill="#ffffff" opacity=".9"/>')
    o.append('</g>')
    return "".join(o)


def chalk_line(d, col="#fff8ee", w=3.2, op=.9, dash=None, cls=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w + 4)}" stroke-linecap="round" opacity="{f(op * .16)}"{da}/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round" opacity="{f(op)}"{da}{c}/>')


def arrow_head(x, y, ang, col, s=11):
    a = math.radians(ang)
    p1 = (x - s * math.cos(a - .5), y - s * math.sin(a - .5))
    p2 = (x - s * math.cos(a + .5), y - s * math.sin(a + .5))
    return (f'<path d="M{f(p1[0])} {f(p1[1])} L{f(x)} {f(y)} L{f(p2[0])} {f(p2[1])}" fill="none" stroke="{col}" '
            f'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')


def maple(x, y, r):
    pts = []
    for i in range(11):
        a = math.radians(-90 + i * 360 / 11)
        rr = r if i % 2 == 0 else r * .5
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts) + "Z"
    return (f'<path d="{d}" fill="#ffab8a" stroke="#fff8ee" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<path d="M{f(x)} {f(y - r * .4)} L{f(x)} {f(y + r * 1.1)}" stroke="#fff8ee" stroke-width="2.4" stroke-linecap="round"/>')


def snowflake(x, y, r):
    o = []
    for i in range(3):
        a = math.radians(i * 60 + 90)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        o.append(f'M{f(x - dx)} {f(y - dy)} L{f(x + dx)} {f(y + dy)}')
        for sgn in (1, -1):
            bx, by = x + sgn * dx * .6, y + sgn * dy * .6
            for t in (.5, -.5):
                b = a + (math.pi if sgn < 0 else 0)
                o.append(f'M{f(bx)} {f(by)} L{f(bx + math.cos(b + t * 1.6) * r * .3)} {f(by + math.sin(b + t * 1.6) * r * .3)}')
    return f'<path d="{" ".join(o)}" stroke="#d8e6ff" stroke-width="3" stroke-linecap="round" fill="none"/>'


def header(cx, y, label, icon, u):
    tw = len(label) * 33
    ix = cx - tw / 2 - 30
    o = [icon(ix, y - 15, 17)]
    o.append(f'<text x="{f(cx + 12)}" y="{f(y)}" text-anchor="middle" font-family="{FONT}" font-size="44" '
             f'font-weight="800" letter-spacing="5" fill="#fffaf2">{label}</text>')
    # chalk underline squiggle
    x0, x1 = cx - tw / 2 - 6, cx + tw / 2 + 30
    d = f"M{f(x0)} {f(y + 16)}"
    n = 6
    for i in range(n):
        xa = x0 + (x1 - x0) * (i + .5) / n
        xb = x0 + (x1 - x0) * (i + 1) / n
        d += f" Q{f(xa)} {f(y + (11 if i % 2 else 21))} {f(xb)} {f(y + 16)}"
    o.append(f'<path d="{d}" fill="none" stroke="#ffc0d6" stroke-width="3.4" stroke-linecap="round" opacity=".9"/>')
    return "".join(o)


def x_mark(cx, cy, s=26):
    d = f"M{f(cx - s)} {f(cy - s)} L{f(cx + s)} {f(cy + s)} M{f(cx + s)} {f(cy - s)} L{f(cx - s)} {f(cy + s)}"
    return (f'<path d="{d}" stroke="{INK}" stroke-width="17" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{PINK}" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="M{f(cx - s + 2)} {f(cy - s - 2)} L{f(cx - 3)} {f(cy - 7)} M{f(cx + s - 2)} {f(cy - s - 2)} L{f(cx + 7)} {f(cy - 13)}" '
            f'stroke="#ffd2e2" stroke-width="3.2" stroke-linecap="round"/>')


def check_mark(cx, cy, s, u):
    d = f"M{f(cx - s)} {f(cy)} L{f(cx - s * .3)} {f(cy + s * .65)} L{f(cx + s * 1.05)} {f(cy - s * .8)}"
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="19" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M{f(cx - s * .35)} {f(cy + s * .48)} L{f(cx + s * .95)} {f(cy - s * .85)}" fill="none" stroke="{GOLD_D}" '
            f'stroke-width="5" stroke-linecap="round" opacity=".7" transform="translate(2 4)"/>'
            f'<path d="M{f(cx - s * .92)} {f(cy - 3)} L{f(cx - s * .5)} {f(cy + s * .32)}" fill="none" stroke="#fffbe8" '
            f'stroke-width="3.4" stroke-linecap="round"/>')


# ------------------------------------------------------------------ the card
def card(uid="pl"):
    u = uid
    defs, back, room, board, front = [], [], [], [], []
    rnd = random.Random(7)

    # ============ wall
    defs.append(f'<linearGradient id="{u}-wall" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="#fbe4e6"/><stop offset=".35" stop-color="#f5e2ef"/>'
                f'<stop offset=".7" stop-color="#e9def6"/><stop offset="1" stop-color="#ddd5f3"/></linearGradient>')
    back.append(f'<rect width="{W}" height="{H}" fill="url(#{u}-wall)"/>')
    # ceiling cornice band
    back.append(f'<rect width="{W}" height="26" fill="#efe2f4"/><rect y="26" width="{W}" height="6" fill="#d9c9ec"/>')
    # wainscot (lower wall panelling)
    back.append(f'<rect y="690" width="{W}" height="210" fill="#e3d6f2"/>'
                f'<rect y="690" width="{W}" height="10" fill="#f6eefb"/><rect y="700" width="{W}" height="4" fill="#cdbde6"/>')
    for i, px in enumerate(range(540, 1600, 210)):
        back.append(f'<path d="{rrect(px, 724, 180, 120, 8)}" fill="none" stroke="#d2c3ea" stroke-width="3"/>'
                    f'<path d="M{px + 4} {722} H{px + 176}" stroke="#f7f0fc" stroke-width="2"/>')

    # ============ window (left)
    WX0, WY0, WX1, WY1 = 52, 64, 470, 600
    gx0, gy0, gx1, gy1 = WX0 + 22, WY0 + 22, WX1 - 22, WY1 - 22
    defs.append(f'<clipPath id="{u}-glass"><rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}"/></clipPath>')
    defs.append(f'<linearGradient id="{u}-sky" x1="0" y1="{gy0}" x2="0" y2="{gy1}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#84a0ee"/><stop offset=".38" stop-color="#a7b0f2"/>'
                f'<stop offset=".6" stop-color="#cbb7ee"/><stop offset=".8" stop-color="#f3c2da"/>'
                f'<stop offset="1" stop-color="#ffd4c2"/></linearGradient>')
    SUNX, SUNY = 150, 452
    defs.append(f'<radialGradient id="{u}-sun" cx="{SUNX}" cy="{SUNY}" r="230" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fffdf4"/><stop offset=".1" stop-color="#fff4d2"/>'
                f'<stop offset=".32" stop-color="#ffe0b6" stop-opacity=".75"/><stop offset="1" stop-color="#ffd6c8" stop-opacity="0"/></radialGradient>')
    sky = [f'<rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}" fill="url(#{u}-sky)"/>',
           f'<circle cx="{SUNX}" cy="{SUNY}" r="230" fill="url(#{u}-sun)"/>']
    # faint sun-ray spokes inside the sky
    spokes = []
    for i, a in enumerate(range(-170, 10, 20)):
        a1, a2 = math.radians(a - 2.4), math.radians(a + 2.4)
        R = 460
        spokes.append(f'M{SUNX} {SUNY} L{f(SUNX + R * math.cos(a1))} {f(SUNY + R * math.sin(a1))} '
                      f'L{f(SUNX + R * math.cos(a2))} {f(SUNY + R * math.sin(a2))}Z')
    # the spokes keep their opacity on a child, so the 1 -> .65 ray keyframes multiply it and the
    # reduced-motion (static) frame matches the animated look
    sky.append(f'<g class="{u}-ry"><path d="{" ".join(spokes)}" fill="#fff6dc" opacity=".72"/></g>')
    # clouds: one golden-hour cumulus in the lower-right pane (sun-lit from the left), a small
    # puff in the upper-left pane behind the sakura branch, stratus streaks by the sun
    PAL = ("#fff4ea", "#ffd58a", "#dcc0ee", "#c2a3de", "#ad8fd6")
    tower = [(292, 506, 26), (330, 494, 36), (382, 490, 40), (432, 498, 34),
             (322, 454, 28), (366, 434, 38), (414, 446, 30),
             (362, 390, 28), (396, 384, 25), (382, 358, 21)]
    # one shadow plane on the far (right / lower) side; its edge follows the big masses only
    tshade = ("M480 330 L394 330 Q410 352 400 374 Q432 388 420 418 Q394 424 388 450 "
              "Q354 452 346 478 Q312 480 296 506 L280 524 L480 524Z")
    thi = "M344 382 Q348 362 370 352 Q364 364 364 374 Q352 374 344 382Z"
    sky.append(f'<g class="{u}-dr2">' + cumulus(u, "ct", tower, 522, tshade, PAL, rim_w=6, hi=thi, back="#f8dcef") + '</g>')
    small = [(100, 226, 18), (130, 212, 26), (164, 218, 21), (188, 228, 12)]
    sshade = "M210 180 L150 180 Q166 200 158 216 Q136 220 124 238 L210 238Z"
    sky.append(f'<g class="{u}-dr1">' + cumulus(u, "cs", small, 238, sshade, PAL, rim_w=4, back="#f8dcef", back_w=2.5) + '</g>')
    for (x0, y0, w, h, c1, c2) in ((gx0 - 20, 404, 200, 9, "#ffd9cf", "#fff3dc"), (176, 432, 96, 6, "#f9c8d6", "#ffeedd"),
                                   (gx0 - 10, 478, 170, 8, "#f7c2d4", "#fff0dc")):
        sky.append(f'<path d="M{f(x0)} {f(y0 + h)} Q{f(x0 + w * .3)} {f(y0 - h * .6)} {f(x0 + w * .6)} {f(y0)} T{f(x0 + w)} {f(y0 + h * .7)} '
                   f'Q{f(x0 + w * .5)} {f(y0 + h * 1.9)} {f(x0)} {f(y0 + h)}Z" fill="{c1}"/>'
                   f'<path d="M{f(x0 + w * .15)} {f(y0 + h * 1.2)} Q{f(x0 + w * .5)} {f(y0 + h * 1.7)} {f(x0 + w * .85)} {f(y0 + h * 1.0)}" '
                   f'fill="none" stroke="{c2}" stroke-width="3" stroke-linecap="round"/>')
    # distant campus rooftops on the horizon
    roof = (f"M{gx0} {gy1} L{gx0} 548 L118 548 L118 536 L176 536 L176 552 L214 552 L222 540 L262 540 L270 552 "
            f"L300 552 L300 530 L314 516 L328 530 L328 556 L380 556 L380 544 L{gx1} 544 L{gx1} {gy1}Z")
    sky.append(f'<path d="{roof}" fill="#c9b4e2"/><path d="M{gx0} 560 H{gx1}" stroke="#e8cce4" stroke-width="3"/>'
               f'<rect x="{gx0}" y="562" width="{gx1 - gx0}" height="{gy1 - 562}" fill="#bfa8dc"/>')
    for wx in range(130, 170, 12):
        sky.append(f'<rect x="{wx}" y="542" width="5" height="5" fill="#ffe4b0"/>')
    # sakura branch outside (enters from top-left of the glass)
    br = ("M60 120 C120 150 170 160 230 150 C270 143 300 132 340 140 C380 148 410 170 470 168 "
          "L470 176 C410 180 376 160 338 152 C300 146 272 156 232 162 C170 172 120 166 60 134Z")
    sk = [f'<path d="{br}" fill="#8a5679" stroke="#5c2f55" stroke-width="2"/>',
          '<path d="M230 156 C250 185 262 210 258 240" fill="none" stroke="#7a4a6c" stroke-width="6" stroke-linecap="round"/>',
          '<path d="M150 158 C140 190 150 210 170 228" fill="none" stroke="#7a4a6c" stroke-width="5" stroke-linecap="round"/>',
          '<path d="M340 146 C356 120 372 104 400 98" fill="none" stroke="#7a4a6c" stroke-width="5" stroke-linecap="round"/>',
          '<path d="M80 140 C120 152 170 158 228 150" fill="none" stroke="#b07a9c" stroke-width="2" stroke-linecap="round"/>']
    for (bx, by, r, rot, sh) in ((96, 128, 15, 10, True), (128, 150, 18, 40, False), (176, 146, 14, -20, True),
                                 (206, 168, 19, 15, False), (256, 140, 16, 50, False), (262, 236, 15, 5, False),
                                 (246, 206, 13, -30, True), (170, 226, 16, 30, False), (148, 196, 12, 0, True),
                                 (300, 128, 13, 20, True), (316, 156, 17, -10, False), (366, 132, 15, 35, False),
                                 (398, 98, 14, 10, True), (380, 104, 12, -40, False), (420, 162, 17, 60, False),
                                 (452, 176, 14, 10, True), (444, 150, 12, -15, False)):
        sk.append(blossom(bx, by, r, rot, sh))
    for (bx, by, r, rot) in ((272, 252, 6, 20), (186, 238, 5, -30), (412, 92, 5, 60), (110, 120, 5, -10), (340, 168, 5, 30)):
        sk.append(bud(bx, by, r, rot))
    sky.append(f'<g class="{u}-sway">{"".join(sk)}</g>')
    # glass reflections (diagonal anime glints)
    for (x0, w, op) in ((96, 34, .2), (146, 12, .22), (290, 46, .14), (356, 10, .18)):
        sky.append(f'<path d="M{x0} {gy1} L{x0 + w} {gy1} L{x0 + w + 160} {gy0} L{x0 + 160} {gy0}Z" fill="#ffffff" opacity="{op}"/>')
    room.append(f'<g clip-path="url(#{u}-glass)">{"".join(sky)}</g>')
    # frame + mullions
    fr = "#fffaf4"
    frs = "#e6d6f0"
    mx = (gx0 + gx1) / 2
    my = 300
    room.append(f'<path d="M{WX0} {WY0} H{WX1} V{WY1} H{WX0}Z M{gx0} {gy0} V{gy1} H{gx1} V{gy0}Z" fill="{fr}" fill-rule="evenodd" '
                f'stroke="{INK}" stroke-width="3"/>')
    room.append(f'<path d="M{gx0} {gy0} H{gx1} L{gx1 - 8} {gy0 + 8} H{gx0 + 8} V{gy1 - 8} L{gx0} {gy1}Z" fill="{frs}"/>')
    room.append(f'<rect x="{f(mx - 8)}" y="{gy0}" width="16" height="{gy1 - gy0}" fill="{fr}" stroke="{INK}" stroke-width="2.4"/>'
                f'<rect x="{f(mx + 2)}" y="{gy0}" width="6" height="{gy1 - gy0}" fill="{frs}"/>'
                f'<rect x="{gx0}" y="{my - 8}" width="{gx1 - gx0}" height="16" fill="{fr}" stroke="{INK}" stroke-width="2.4"/>'
                f'<rect x="{gx0}" y="{my + 2}" width="{gx1 - gx0}" height="6" fill="{frs}"/>'
                f'<circle cx="{f(mx)}" cy="{my}" r="5" fill="{GOLD}" stroke="{INK}" stroke-width="1.6"/>')
    # sill
    room.append(f'<path d="M{WX0 - 26} {WY1} H{WX1 + 26} L{WX1 + 18} {WY1 + 22} H{WX0 - 18}Z" fill="{fr}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
                f'<path d="M{WX0 - 18} {WY1 + 22} H{WX1 + 18} V{WY1 + 30} H{WX0 - 18}Z" fill="#d9c6ec" stroke="{INK}" stroke-width="2.4"/>'
                f'<path d="M{WX0 - 18} {WY1 + 6} H{WX1 + 12}" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>')
    # small sakura bud vase on the sill
    vx = 400
    room.append(f'<path d="M{vx - 16} {WY1} C{vx - 22} {WY1 - 20} {vx - 14} {WY1 - 40} {vx - 6} {WY1 - 48} H{vx + 6} '
                f'C{vx + 14} {WY1 - 40} {vx + 22} {WY1 - 20} {vx + 16} {WY1}Z" fill="#b9c8ff" stroke="{INK}" stroke-width="2.4"/>'
                f'<path d="M{vx + 4} {WY1 - 44} C{vx + 14} {WY1 - 34} {vx + 16} {WY1 - 16} {vx + 12} {WY1 - 2}" fill="none" stroke="#8fa0e6" stroke-width="5" opacity=".7"/>'
                f'<path d="M{vx - 8} {WY1 - 38} C{vx - 12} {WY1 - 28} {vx - 12} {WY1 - 18} {vx - 9} {WY1 - 10}" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>'
                f'<path d="M{vx} {WY1 - 48} C{vx - 6} {WY1 - 80} {vx - 22} {WY1 - 96} {vx - 30} {WY1 - 104} M{vx} {WY1 - 48} C{vx + 6} {WY1 - 74} {vx + 18} {WY1 - 90} {vx + 26} {WY1 - 96}" '
                f'fill="none" stroke="#7a4a6c" stroke-width="3" stroke-linecap="round"/>'
                + blossom(vx - 30, WY1 - 106, 11, 10) + blossom(vx + 27, WY1 - 98, 10, -20, True) + blossom(vx - 12, WY1 - 82, 8, 40)
                + bud(vx + 12, WY1 - 78, 4, 30))

    # curtains: left (full edge) and right (tied back)
    def curtain(x0, x1, y0, y1, tie_y, side):
        cid = f"{u}-cur{side}"
        n = 5
        folds = []
        for i in range(n + 1):
            folds.append(x0 + (x1 - x0) * i / n)
        # silhouette: top straight, pinched at tie, flares to bottom
        pinch = (x0 + x1) / 2 + (-(x1 - x0) * .15 if side == "r" else (x1 - x0) * .15)
        if side == "l":
            d = (f"M{x0} {y0} H{x1} C{x1 + 4} {tie_y - 120} {pinch + 18} {tie_y - 30} {pinch + 14} {tie_y} "
                 f"C{pinch + 12} {tie_y + 50} {x1 + 30} {y1 - 60} {x1 + 46} {y1} H{x0}Z")
        else:
            d = (f"M{x0} {y0} H{x1} V{y1} H{x0 - 40} C{x0 - 26} {y1 - 70} {pinch - 12} {tie_y + 50} {pinch - 14} {tie_y} "
                 f"C{pinch - 18} {tie_y - 30} {x0 - 4} {tie_y - 120} {x0} {y0}Z")
        o = [f'<clipPath id="{cid}"><path d="{d}"/></clipPath>',
             f'<path d="{d}" fill="#fff3f7" opacity=".93"/>']
        g = []
        for i in range(1, n):
            fx = folds[i]
            g.append(f'<path d="M{f(fx)} {y0} C{f(fx + 6)} {tie_y - 80} {f(pinch + (fx - pinch) * .2)} {tie_y - 10} {f(pinch + (fx - pinch) * .2)} {tie_y} '
                     f'C{f(pinch + (fx - pinch) * .3)} {tie_y + 40} {f(fx + (fx - pinch) * .5)} {y1 - 80} {f(fx + (fx - pinch) * .7)} {y1}" '
                     f'fill="none" stroke="#efc6dc" stroke-width="{f(8 + (i % 2) * 6)}" opacity=".85"/>')
            g.append(f'<path d="M{f(fx + 9)} {y0} C{f(fx + 14)} {tie_y - 80} {f(pinch + (fx - pinch) * .2 + 3)} {tie_y - 10} {f(pinch + (fx - pinch) * .2 + 3)} {tie_y}" '
                     f'fill="none" stroke="#ffffff" stroke-width="3" opacity=".9"/>')
        o.append(f'<g clip-path="url(#{cid})">{"".join(g)}</g>')
        o.append(f'<path d="{d}" fill="none" stroke="#c99ac0" stroke-width="2.4" stroke-linejoin="round"/>')
        # tie ribbon
        o.append(f'<path d="M{f(pinch - 30)} {tie_y - 6} Q{f(pinch)} {tie_y + 10} {f(pinch + 30)} {tie_y - 6} L{f(pinch + 30)} {tie_y + 6} '
                 f'Q{f(pinch)} {tie_y + 22} {f(pinch - 30)} {tie_y + 6}Z" fill="{SAKURA}" stroke="{INK}" stroke-width="2.2"/>'
                 f'<circle cx="{f(pinch)}" cy="{tie_y + 8}" r="6" fill="{GOLD}" stroke="{INK}" stroke-width="1.8"/>')
        return "".join(o)

    room.append(f'<rect x="20" y="34" width="490" height="10" rx="5" fill="#d8c3e8" stroke="{INK}" stroke-width="2"/>'
                f'<circle cx="20" cy="39" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
                f'<circle cx="510" cy="39" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>')
    room.append(f'<g class="{u}-cl">' + curtain(-10, 70, 40, 690, 400, "l") + '</g>')
    room.append(f'<g class="{u}-cr">' + curtain(452, 520, 40, 690, 400, "r") + '</g>')

    # ============ chalkboard
    BX0, BY0, BX1, BY1 = 580, 62, 1562, 646
    IX0, IY0, IX1, IY1 = BX0 + 22, BY0 + 22, BX1 - 22, BY1 - 22
    defs.append(f'<linearGradient id="{u}-bd" x1="{IX0}" y1="{IY0}" x2="{IX1}" y2="{IY1}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#7d7ac6"/><stop offset=".55" stop-color="#6f6bb8"/>'
                f'<stop offset="1" stop-color="#6460ac"/></linearGradient>')
    defs.append(f'<clipPath id="{u}-bclip"><rect x="{IX0}" y="{IY0}" width="{IX1 - IX0}" height="{IY1 - IY0}"/></clipPath>')
    # wooden frame (honey wood, cel shaded)
    board.append(f'<path d="{rrect(BX0 + 6, BY0 + 12, BX1 - BX0, BY1 - BY0, 14)}" fill="#3b3470" opacity=".22"/>')
    board.append(f'<path d="{rrect(BX0, BY0, BX1 - BX0, BY1 - BY0, 14)}" fill="#e9b98d" stroke="{INK}" stroke-width="3"/>')
    board.append(f'<path d="M{BX0 + 8} {BY0 + 8} H{BX1 - 8}" stroke="#ffe2c2" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M{BX1 - 8} {BY0 + 14} V{BY1 - 10}" stroke="#d29a6e" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M{BX0 + 8} {BY1 - 8} H{BX1 - 8}" stroke="#d29a6e" stroke-width="5" stroke-linecap="round"/>')
    board.append(f'<rect x="{IX0}" y="{IY0}" width="{IX1 - IX0}" height="{IY1 - IY0}" fill="url(#{u}-bd)" stroke="{INK}" stroke-width="2.6"/>')
    bi = []
    # inner frame shadow (top/left) -> depth
    bi.append(f'<path d="M{IX0} {IY0} H{IX1} V{IY0 + 10} H{IX0 + 10} V{IY1} H{IX0}Z" fill="#4f4a96" opacity=".55"/>')
    # eraser smudges
    for (sx, sy, rx, ry, rot, op) in ((760, 560, 150, 26, -8, .1), (1250, 120, 180, 24, 4, .09), (1100, 600, 120, 18, -3, .08),
                                      (680, 240, 60, 90, 0, .05), (1460, 400, 70, 120, 10, .06)):
        bi.append(f'<ellipse cx="{sx}" cy="{sy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {sx} {sy})" fill="#e8e4ff" opacity="{op}"/>')
    # window-light projection: four skewed warm panes falling across the board
    sk = .42
    panes = []
    for (px, py, pw, ph) in ((640, 96, 190, 205), (846, 96, 190, 205), (640, 318, 190, 205), (846, 318, 190, 205)):
        x0 = px + (py - 96) * sk
        panes.append(f'M{f(x0)} {py} L{f(x0 + pw)} {py} L{f(x0 + pw + ph * sk)} {py + ph} L{f(x0 + ph * sk)} {py + ph}Z')
    defs.append(f'<linearGradient id="{u}-pane" x1="600" y1="0" x2="1300" y2="0" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#ffe9c6" stop-opacity=".34"/><stop offset="1" stop-color="#ffd8d2" stop-opacity=".06"/></linearGradient>')
    bi.append(f'<path d="{" ".join(panes)}" fill="url(#{u}-pane)" class="{u}-ry"/>')
    board.append(f'<g clip-path="url(#{u}-bclip)">{"".join(bi)}</g>')

    # columns
    CX = [IX0 + (IX1 - IX0) * (i + .5) / 3 for i in range(3)]   # 761, 1071, 1381
    for i in (1, 2):
        xx = IX0 + (IX1 - IX0) * i / 3
        board.append(chalk_line(f"M{f(xx)} {IY0 + 34} V{IY1 - 120}", w=2.6, op=.45, dash="2 12"))
    board.append(header(CX[0], 160, "FALL", maple, u))
    board.append(header(CX[1], 160, "WINTER", snowflake, u))
    board.append(header(CX[2], 160, "SPRING", lambda x, y, r: blossom(x, y, r * 1.05, 10), u))

    BW, BH = 214, 76
    ROWS = [240, 354, 468]   # block top y
    C_AZ = ("#dfe8ff", "#b9c8f6", "#8fa0e6")
    C_LV = ("#ece3ff", "#cbbcf2", "#a08ad8")
    C_CR = ("#fff1d6", "#f4d4a6", "#e8a96c")

    def bx(c):
        return CX[c] - BW / 2

    # prerequisite lines (chalk, behind blocks)
    def link(c0, r0, c1, r1, col="#fff8ee", op=.8, dash=None, bend=0):
        x0, y0 = bx(c0) + BW, ROWS[r0] + BH / 2 - 3
        x1, y1 = bx(c1), ROWS[r1] + BH / 2 - 3
        mxp = (x0 + x1) / 2
        d = f"M{f(x0 + 4)} {f(y0)} C{f(mxp + bend)} {f(y0)} {f(mxp - bend)} {f(y1)} {f(x1 - 6)} {f(y1)}"
        return chalk_line(d, col=col, w=3, op=op, dash=dash) + arrow_head(x1 - 6, y1, 0, col)

    lines = [link(0, 0, 1, 0), link(1, 0, 2, 0), link(0, 1, 1, 1), link(0, 0, 1, 1), link(1, 1, 2, 1)]
    # the WINTER-row-2 prerequisite feeding the moved course (gold, satisfied in SPRING)
    gx_0, gy_0 = bx(1) + BW, ROWS[1] + BH / 2 + 8
    gx_1, gy_1 = bx(2) - 4, ROWS[2] + BH / 2 - 6
    gd = f"M{f(gx_0 + 4)} {f(gy_0)} C{f(gx_0 + 60)} {f(gy_0 + 6)} {f(gx_1 - 60)} {f(gy_1)} {f(gx_1)} {f(gy_1)}"
    lines.append(chalk_line(gd, col=GOLD, w=3.6, op=1) + arrow_head(gx_1, gy_1, 2, GOLD))
    # the same prerequisite pointing BACK to FALL = the conflict (pink dashed)
    px0, py0 = bx(1), ROWS[1] + BH / 2 + 10
    px1, py1 = bx(0) + BW + 6, ROWS[2] + BH / 2 - 4
    pd = f"M{f(px0 - 4)} {f(py0)} C{f(px0 - 50)} {f(py0 + 10)} {f(px1 + 50)} {f(py1)} {f(px1)} {f(py1)}"
    lines.append(chalk_line(pd, col="#ff9cc0", w=3.2, op=.95, dash="9 8") + arrow_head(px1, py1, 180, "#ff9cc0"))
    board.append("".join(lines))

    # blocks
    board.append(course_block(bx(0), ROWS[0], BW, BH, C_AZ, 1, u, pin="#8fb0ff", rot=-2.5))
    board.append(course_block(bx(0), ROWS[1], BW, BH, C_CR, 2, u, pin=PINK, rot=3))
    board.append(course_block(bx(1), ROWS[0], BW, BH, C_LV, 3, u, pin=GOLD, rot=2))
    board.append(course_block(bx(1), ROWS[1], BW, BH, C_AZ, 4, u, pin="#c7a8ff", rot=-3.5))
    board.append(course_block(bx(2), ROWS[0], BW, BH, C_CR, 5, u, pin="#8fb0ff", rot=-2))
    board.append(course_block(bx(2), ROWS[1], BW, BH, C_LV, 6, u, pin=PINK, rot=3.5))

    # FALL slot that the checker rejected: dashed ghost outline + pink X
    fx, fy = bx(0), ROWS[2]
    board.append(f'<path d="{rrect(fx, fy, BW, BH, 13)}" fill="#ff9cc0" fill-opacity=".14" stroke="#ffb3cf" stroke-width="3.2" stroke-dasharray="12 9"/>')
    board.append(x_mark(fx + BW / 2, fy + BH / 2, 22))

    # SPRING target slot: gold glow + dashed gold outline + check
    tx, ty = bx(2), ROWS[2]
    defs.append(f'<radialGradient id="{u}-gl"><stop offset="0" stop-color="#fff3c4" stop-opacity=".95"/>'
                f'<stop offset=".45" stop-color="#ffdca0" stop-opacity=".45"/><stop offset="1" stop-color="#ffc9a8" stop-opacity="0"/></radialGradient>')
    board.append(f'<ellipse cx="{f(tx + BW / 2)}" cy="{f(ty + BH / 2)}" rx="{BW * .82}" ry="{BH * 1.35}" fill="url(#{u}-gl)" class="{u}-pulse"/>')
    board.append(f'<path d="{rrect(tx, ty, BW, BH, 13)}" fill="#fff4d0" fill-opacity=".3" stroke="{GOLD}" stroke-width="3.6" stroke-dasharray="12 9"/>')
    board.append(check_mark(tx + BW / 2 + 4, ty + BH / 2 - 2, 24, u))
    for (sx, sy, r, i) in ((tx - 10, ty - 8, 11, 0), (tx + BW + 8, ty + 10, 9, 1), (tx + BW - 20, ty + BH + 12, 7, 2), (tx + 30, ty + BH + 16, 6, 0)):
        board.append(sparkle(sx, sy, r, GOLD_L, 1, f"{u}-tw{i}"))

    # dotted chalk arc FALL slot -> (carried) -> SPRING slot
    a0 = (fx + BW / 2 + 20, fy + BH + 8)
    a1 = (tx + BW / 2 - 30, ty + BH + 8)
    arc = f"M{f(a0[0])} {f(a0[1])} C{f(a0[0] + 60)} {f(a0[1] + 66)} {f(a1[0] - 60)} {f(a1[1] + 66)} {f(a1[0])} {f(a1[1])}"
    board.append(chalk_line(arc, col="#ffffff", w=6.4, op=.95, dash="0.1 15", cls=f"{u}-march"))
    ang = math.atan2(-66, 60)
    ax, ay = a1[0] + 4 * math.cos(ang), a1[1] + 4 * math.sin(ang)
    tri = [(ax + 16 * math.cos(ang), ay + 16 * math.sin(ang)),
           (ax + 11 * math.cos(ang + 2.2), ay + 11 * math.sin(ang + 2.2)),
           (ax + 11 * math.cos(ang - 2.2), ay + 11 * math.sin(ang - 2.2))]
    board.append(f'<path d="M{" L".join(f"{f(a)} {f(b)}" for a, b in tri)}Z" fill="#ffffff" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>')

    # chalk tray + chalk + eraser
    board.append(f'<path d="M{BX0 + 30} {BY1 - 4} H{BX1 - 30} L{BX1 - 40} {BY1 + 14} H{BX0 + 40}Z" fill="#e9b98d" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'
                 f'<path d="M{BX0 + 44} {BY1 + 13} H{BX1 - 44}" stroke="#c98d62" stroke-width="3"/>')
    for (cx0, ln, col, rot) in ((660, 46, "#fffaf2", -4), (716, 36, "#ffc2d6", 3), (1440, 40, GOLD_L, -2), (1490, 30, "#cfe0ff", 6)):
        board.append(f'<g transform="rotate({rot} {cx0} {BY1 - 6})"><rect x="{cx0}" y="{BY1 - 13}" width="{ln}" height="10" rx="5" fill="{col}" stroke="{INK}" stroke-width="1.8"/>'
                     f'<rect x="{cx0 + 4}" y="{BY1 - 11}" width="{ln * .5}" height="3" rx="1.5" fill="#ffffff"/></g>')
    board.append(f'<rect x="1290" y="{BY1 - 26}" width="92" height="24" rx="5" fill="#f6b3cb" stroke="{INK}" stroke-width="2.4"/>'
                 f'<rect x="1290" y="{BY1 - 12}" width="92" height="10" rx="3" fill="#8f7fd0" stroke="{INK}" stroke-width="2"/>'
                 f'<path d="M1298 {BY1 - 21} H1352" stroke="#ffe0ea" stroke-width="3" stroke-linecap="round"/>')

    # ============ light rays from the window sweeping across the room
    defs.append(f'<linearGradient id="{u}-ray" x1="{SUNX}" y1="{SUNY}" x2="1500" y2="760" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff6dc" stop-opacity=".95"/><stop offset=".55" stop-color="#ffefd8" stop-opacity=".45"/>'
                f'<stop offset="1" stop-color="#ffe6e6" stop-opacity="0"/></linearGradient>')
    rays = []
    for (ang, wdt, op) in ((-4, 2.6, .34), (3, 3.6, .4), (10, 2.2, .3), (17, 4.2, .34), (26, 2.4, .26), (33, 3.4, .22)):
        a1, a2 = math.radians(ang - wdt / 2), math.radians(ang + wdt / 2)
        R = 1600
        sx0, sy0 = 470, SUNY + (470 - SUNX) * math.tan(math.radians(ang))
        rays.append(f'<path d="M{f(sx0)} {f(sy0 - 30)} L{f(SUNX + R * math.cos(a1))} {f(SUNY + R * math.sin(a1))} '
                    f'L{f(SUNX + R * math.cos(a2))} {f(SUNY + R * math.sin(a2))} L{f(sx0)} {f(sy0 + 30)}Z" fill="url(#{u}-ray)" opacity="{op}"/>')
    front.append(f'<g class="{u}-ry">{"".join(rays)}</g>')

    # ============ desk (foreground)
    defs.append(f'<linearGradient id="{u}-desk" x1="0" y1="790" x2="0" y2="900" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#f3caa4"/><stop offset="1" stop-color="#e2a982"/></linearGradient>')
    front.append(f'<path d="M0 792 H{W} V{H} H0Z" fill="url(#{u}-desk)"/>'
                 f'<path d="M0 792 H{W}" stroke="{INK}" stroke-width="3"/>'
                 f'<path d="M0 798 H{W}" stroke="#ffe6cc" stroke-width="4"/>'
                 f'<path d="M0 860 H{W}" stroke="#d4966f" stroke-width="2" opacity=".6"/>')
    # warm light pools on the desk (window light)
    front.append(f'<path d="M120 802 L520 802 L700 900 L240 900Z" fill="#fff1d6" opacity=".35"/>'
                 f'<path d="M560 802 L700 802 L860 900 L700 900Z" fill="#fff1d6" opacity=".22"/>')
    # soft footprint of the window light on the wainscot (fades at both ends)
    defs.append(f'<linearGradient id="{u}-foot" x1="520" y1="0" x2="1060" y2="0" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff2d6" stop-opacity="0"/><stop offset=".3" stop-color="#fff2d6" stop-opacity=".55"/>'
                f'<stop offset=".7" stop-color="#ffe9e0" stop-opacity=".3"/><stop offset="1" stop-color="#ffe9e0" stop-opacity="0"/></linearGradient>')
    front.append(f'<path d="M520 704 L860 704 L1060 792 L640 792Z" fill="url(#{u}-foot)" class="{u}-ry"/>')
    front.append(f'<path d="M0 878 H{W} V{H} H0Z" fill="#d49572" opacity=".55"/>')
    # stack of books (left), partly behind Hu Tao
    books = [(70, 742, 250, 50, "#b9c8ff", "#8fa0e6"), (88, 700, 214, 42, SAKURA_L, "#f2a3c2"), (78, 664, 228, 36, "#fff1d6", "#f0c99a")]
    for (bx0, by0, bw, bh, c1, c2) in books:
        front.append(f'<path d="{rrect(bx0, by0, bw, bh, 6)}" fill="{c1}" stroke="{INK}" stroke-width="2.6"/>'
                     f'<rect x="{bx0 + 4}" y="{by0 + bh * .55}" width="{bw - 8}" height="{bh * .4}" rx="3" fill="{c2}"/>'
                     f'<rect x="{bx0 + bw - 44}" y="{by0 + 4}" width="12" height="{bh - 8}" fill="#ffffff" opacity=".75"/>'
                     f'<path d="M{bx0 + 10} {by0 + 8} H{bx0 + bw * .55}" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>')
    # pencil cup (right) with pencils
    pcx = 1478
    front.append(f'<path d="M{pcx + 4} 690 L{pcx + 14} 640 M{pcx + 20} 690 L{pcx + 34} 628 M{pcx + 38} 690 L{pcx + 60} 644" '
                 f'stroke="{INK}" stroke-width="13" stroke-linecap="round"/>'
                 f'<path d="M{pcx + 4} 690 L{pcx + 14} 640" stroke="{GOLD}" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="M{pcx + 20} 690 L{pcx + 34} 628" stroke="{SAKURA}" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="M{pcx + 38} 690 L{pcx + 60} 644" stroke="#a8b8ff" stroke-width="8" stroke-linecap="round"/>')
    front.append(f'<path d="M{pcx - 14} 680 H{pcx + 74} L{pcx + 66} 796 H{pcx - 6}Z" fill="#d6c8f6" stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>'
                 f'<path d="M{pcx + 40} 684 H{pcx + 72} L{pcx + 64} 794 H{pcx + 40}Z" fill="#b3a2e6"/>'
                 f'<path d="M{pcx - 4} 692 L{pcx + 2} 784" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>'
                 + blossom(pcx + 24, 740, 12, 15))
    # open notebook on desk (centre-right, partly cut off by bottom)
    nb = (f'<g transform="rotate(-4 1120 850)">'
          f'<path d="M940 812 Q1030 800 1120 822 Q1210 800 1300 812 L1306 912 H934Z" fill="#fffaf2" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'
          f'<path d="M1120 822 V912" stroke="#d9c6ec" stroke-width="3"/>'
          + "".join(f'<path d="M{960 + (0 if k < 3 else 180)} {840 + (k % 3) * 18} h{110 - (k % 2) * 30}" stroke="#c9bdf0" stroke-width="5" stroke-linecap="round"/>' for k in range(6))
          + f'<path d="M1150 830 h40" stroke="{PINK}" stroke-width="5" stroke-linecap="round"/>'
          f'<g transform="rotate(-18 1080 872)"><rect x="1000" y="866" width="150" height="13" rx="3" fill="#a8b8ff" stroke="{INK}" stroke-width="2.2"/>'
          f'<rect x="1004" y="868" width="100" height="4" rx="2" fill="#e4eaff"/>'
          f'<path d="M1150 866 L1176 872.5 L1150 879Z" fill="#ffe2c4" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
          f'<path d="M1168 870.5 L1176 872.5 L1168 874.5Z" fill="{INK}"/>'
          f'<rect x="990" y="866" width="14" height="13" rx="3" fill="{SAKURA}" stroke="{INK}" stroke-width="2.2"/></g></g>')
    front.append(nb)

    # ============ characters
    # chibi Hu Tao (official Genshin Impact emoji, (c) HoYoverse) studying with a book in front of the window
    front.append(ART.place("hutao_book", 318, H + 16, 450, f"{u}ht", shadow=("#6f5fc8", .35, 10), fade=(H - 40, H + 6)))

    # ============ petals drifting in + dust motes in the rays
    pets = []
    for i, (px, py, sz, rot) in enumerate(((530, 250, 10, 30), (610, 700, 9, -40), (880, 760, 11, 70), (1220, 735, 10, 15),
                                           (520, 470, 8, -60), (1540, 210, 9, 40), (360, 760, 10, 100), (980, 40, 8, -20))):
        pets.append(petal(px, py, sz * 1.5, rot, f"{u}-pf{i % 3}"))
    front.append("".join(pets))
    motes = []
    for i, (mx2, my2, r) in enumerate(((560, 360, 5), (720, 420, 4), (900, 520, 6), (600, 560, 4), (1180, 600, 5),
                                       (980, 330, 3), (660, 300, 3), (1320, 700, 4))):
        motes.append(sparkle(mx2, my2, r, "#fffaf0", 1, f"{u}-tw{i % 3}"))
    front.append("".join(motes))

    # soft warm bloom near window + gentle vignette
    defs.append(f'<radialGradient id="{u}-bloom" cx="{SUNX}" cy="{SUNY}" r="700" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="#fff2d8" stop-opacity=".3"/><stop offset="1" stop-color="#fff2d8" stop-opacity="0"/></radialGradient>')
    defs.append(f'<radialGradient id="{u}-vig" cx="900" cy="420" r="1000" gradientUnits="userSpaceOnUse">'
                f'<stop offset=".7" stop-color="#7a6cc0" stop-opacity="0"/><stop offset="1" stop-color="#7a6cc0" stop-opacity=".22"/></radialGradient>')
    front.append(f'<rect width="{W}" height="{H}" fill="url(#{u}-bloom)"/><rect width="{W}" height="{H}" fill="url(#{u}-vig)"/>')

    css = (f"@keyframes {u}-tw{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.6)}}}}"
           f".{u}-tw0,.{u}-tw1,.{u}-tw2{{transform-box:fill-box;transform-origin:50% 50%}}"
           f".{u}-tw0{{animation:{u}-tw 3.2s ease-in-out infinite}}"
           f".{u}-tw1{{animation:{u}-tw 4.1s ease-in-out -1.3s infinite}}"
           f".{u}-tw2{{animation:{u}-tw 2.7s ease-in-out -.6s infinite}}"
           f"@keyframes {u}-dr{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(10px)}}}}"
           f".{u}-dr1{{animation:{u}-dr 20s ease-in-out infinite}}"
           f".{u}-dr2{{animation:{u}-dr 26s ease-in-out -9s infinite}}"
           f"@keyframes {u}-pf{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(12px,9px)}}}}"
           f".{u}-pf0{{animation:{u}-pf 6s ease-in-out infinite}}"
           f".{u}-pf1{{animation:{u}-pf 7.5s ease-in-out -2s infinite}}"
           f".{u}-pf2{{animation:{u}-pf 9s ease-in-out -4s infinite}}"
           f"@keyframes {u}-ry{{0%,100%{{opacity:1}}50%{{opacity:.65}}}}"
           f".{u}-ry{{animation:{u}-ry 7s ease-in-out infinite}}"
           f"@keyframes {u}-pu{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}"
           f".{u}-pulse{{animation:{u}-pu 2.4s ease-in-out infinite}}"
           f"@keyframes {u}-mr{{to{{stroke-dashoffset:-30.2}}}}"
           f".{u}-march{{animation:{u}-mr 1.4s linear infinite}}"
           f"@keyframes {u}-sw{{0%,100%{{transform:rotate(0deg)}}50%{{transform:rotate(1.2deg)}}}}"
           f".{u}-sway{{transform-box:fill-box;transform-origin:0% 20%;animation:{u}-sw 6s ease-in-out infinite}}"
           f"@keyframes {u}-cu{{0%,100%{{transform:skewX(0deg)}}50%{{transform:skewX(1.4deg)}}}}"
           f".{u}-cl,.{u}-cr{{transform-box:fill-box;transform-origin:50% 0%;animation:{u}-cu 5s ease-in-out infinite}}"
           f".{u}-cr{{animation-delay:-2s}}"
           f"@media (prefers-reduced-motion: reduce){{[class^='{u}-'],[class*=' {u}-']{{animation:none!important}}}}")

    body = "".join(back) + "".join(room) + "".join(board) + "".join(front)
    label = ("Anime study corner at golden hour: a pastel chalkboard plans FALL, WINTER and SPRING courses; "
             "a crossed-out FALL note moves along a dotted arc to a gold-checked SPRING slot while chibi Hu Tao "
             "(official Genshin Impact emoji, © HoYoverse) studies a book by the window")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">'
            f'<style>{css}</style>'
            f'<defs><clipPath id="{u}-card"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>{"".join(defs)}</defs>'
            f'<g clip-path="url(#{u}-card)">{body}</g></svg>')


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "card-planner.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(card())
    return p


if __name__ == "__main__":
    out = build(os.path.dirname(DEBUG_OUT))
    print(out, os.path.getsize(out) // 1024, "KB")
