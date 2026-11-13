"""Chibi fan art of Furina's Salon Members (Salon Solitaire summons) - original SVG drawings,
non-commercial, drawn from scratch (no official art traced or embedded).

  usher(x, y, scale=1, uid='us', flip=False, shadow=True)        Gentilhomme Usher, the round octopus in a top hat
  chevalmarin(x, y, scale=1, uid='cm', flip=False, shadow=True)  Surintendante Chevalmarin, the bubble seahorse
  crabaletta(x, y, scale=1, uid='cr', flip=False, shadow=True)   Mademoiselle Crabaletta, the armoured crab
  salon_trio(x, y, scale=1, uid='st', flip=False, shadow=True)   all three in a row (x, y under the seahorse)

Extra keyword arguments (pose=..., etc.) are accepted and ignored, so older callers keep working.
Each returns an SVG <g> string carrying its own <defs>/<style>; every id/class is prefixed by uid.
(x, y) is the ground point under the creature's centre.  Bounding boxes relative to (x, y) at
scale 1 (un-flipped; mirror min/max x when flip=True) are in BBOX.

Style: anime cel shading to match furina.py - ink #363170 outline (2.2 base, heavier on the
lower-right via an offset ink under-layer), hard multiply-style shadow crescents, rim light,
glossy water sheen, inner glow + tiny internal bubbles for a translucent water-creature feel.
No green/teal: every blue sits at hue >= 205.  Python 3 stdlib only.
Running this file writes a showcase SVG into the scratchpad (never into the repo).
"""
import math
import os

INK = '#363170'
WHITE = '#ffffff'
BLUSH = '#f6a2b6'
GOLD, GOLD_SH, GOLD_HI = '#f4d488', '#d6a656', '#fff3c8'
PINK, PINK_SH, PINK_HI = '#f8bfd6', '#e894b6', '#ffe6f1'
SHADE = '#4636ad'      # multiply-style cel shadow colour (used with opacity)
RIM = '#f3d6ff'        # lavender-pink back/rim light

# min_x, min_y, max_x, max_y relative to (x, y) at scale 1 - measured from renders,
# incl. ground shadow and the little bubbles / sparkles around each creature
BBOX = {  # static pose; the idle bob lifts each creature up to 7 px higher while animating
    'usher': (-76, -174, 76, 8),
    'chevalmarin': (-86, -202, 92, 7),
    'crabaletta': (-93, -126, 93, 11),
    'salon_trio': (-267, -200, 283, 11),
}

FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"


# ------------------------------------------------------------------------------------------
# drawing helpers
# ------------------------------------------------------------------------------------------
def _f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.') if abs(v - round(v)) > 1e-6 else str(int(round(v)))


def _cut(cid, d, dx, dy, fill, op=1.0):
    """Crescent = shape minus the same shape shifted by (-dx, -dy): a hard-edged form shadow /
    rim light hugging the (+dx, +dy) side.  Must be placed inside the shape's own clip."""
    return (f'<clipPath id="{cid}"><path clip-rule="evenodd" transform="translate({_f(-dx)},{_f(-dy)})" '
            f'd="M-3000,-3000 H3000 V3000 H-3000 Z {d}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><path d="{d}" fill="{fill}" opacity="{op}"/></g>')


def _cel(uid, name, d, base, shadows=(), highlights=(), sw=2.2, extra='', heavy=1.0,
         form=None, rim=None, sheen=None, post=''):
    """Filled shape + hard-edged cel layers clipped inside + ink outline.

    shadows / highlights: (path, colour[, opacity]) shapes drawn inside the clip.
    form  = (dx, dy, opacity)        automatic shadow crescent on the (+dx, +dy) side
    rim   = (dx, dy, colour, opacity) thin rim-light crescent
    sheen = (dx, dy, opacity)        thin white sheen crescent (usually top-left: negative dx, dy)
    heavy: offset ink under-layer -> thicker line on the lower-right (line-weight variation).
    """
    cid = f'{uid}-k-{name}'
    out = [f'<clipPath id="{cid}"><path d="{d}"/></clipPath>']
    if heavy:
        out.append(f'<path d="{d}" fill="{INK}" transform="translate({_f(.8 * heavy)},{_f(1.3 * heavy)})"/>')
    out.append(f'<path d="{d}" fill="{base}"/>')
    out.append(f'<g clip-path="url(#{cid})">')
    out.append(extra)
    for item in shadows:
        sd, c = item[0], item[1]
        op = f' opacity="{item[2]}"' if len(item) > 2 else ''
        out.append(f'<path d="{sd}" fill="{c}"{op}/>')
    if form:
        out.append(_cut(cid + 'f', d, form[0], form[1], SHADE, form[2]))
    if rim:
        out.append(_cut(cid + 'r', d, rim[0], rim[1], rim[2], rim[3]))
    if sheen:
        out.append(_cut(cid + 's', d, sheen[0], sheen[1], WHITE, sheen[2]))
    for item in highlights:
        hd, c = item[0], item[1]
        op = f' opacity="{item[2]}"' if len(item) > 2 else ''
        out.append(f'<path d="{hd}" fill="{c}"{op}/>')
    out.append(post + '</g>')
    out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{sw}" '
               f'stroke-linejoin="round" stroke-linecap="round"/>')
    return ''.join(out)


def _circ(cx, cy, r):
    return f'M{_f(cx - r)},{_f(cy)} a{_f(r)},{_f(r)} 0 1,0 {_f(2 * r)},0 a{_f(r)},{_f(r)} 0 1,0 {_f(-2 * r)},0 Z'


def _ell(cx, cy, rx, ry):
    return f'M{_f(cx - rx)},{_f(cy)} a{_f(rx)},{_f(ry)} 0 1,0 {_f(2 * rx)},0 a{_f(rx)},{_f(ry)} 0 1,0 {_f(-2 * rx)},0 Z'


def _lg(gid, x1, y1, x2, y2, stops):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>'
                for o, c, a in [(st + (None,))[:3] for st in stops])
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'{s}</linearGradient>')


def _rg(gid, cx, cy, r, stops, fx=None, fy=None):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>'
                for o, c, a in [(st + (None,))[:3] for st in stops])
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ''
    return f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


def _common_defs(uid):
    """Shared per-creature gradients: anime eye iris, bubble body, iridescent bubble rim."""
    return (f'<linearGradient id="{uid}-iris" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#262c78"/><stop offset=".42" stop-color="#3d5ccc"/>'
            f'<stop offset=".78" stop-color="#7fa6ff"/><stop offset="1" stop-color="#c4d8ff"/></linearGradient>'
            f'<radialGradient id="{uid}-bub" cx=".5" cy=".5" r=".5">'
            f'<stop offset=".55" stop-color="#e8eeff" stop-opacity=".08"/>'
            f'<stop offset=".9" stop-color="#c9d4ff" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="#b6c4ff" stop-opacity=".7"/></radialGradient>'
            f'<linearGradient id="{uid}-iri" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="#9fb4ff"/><stop offset=".35" stop-color="#c3b2ff"/>'
            f'<stop offset=".65" stop-color="#ffbfe0"/><stop offset="1" stop-color="#9fc4ff"/></linearGradient>')


def _eye(uid, cx, cy, r=10.0, look=(0.0, 0.0), side=1):
    """Glossy anime creature eye: dark almond, gradient iris, pupil, lower glow, two highlights,
    a tiny sparkle and a thick upper lash line with a small outer flick (side = outer direction)."""
    lx, ly = look
    rx, ry = r * .8, r
    ic, icy = cx + lx, cy + ly
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx + .6)}" ry="{_f(ry + .6)}" fill="{INK}"/>'
            f'<ellipse cx="{_f(ic)}" cy="{_f(icy + r * .1)}" rx="{_f(rx * .8)}" ry="{_f(ry * .84)}" fill="url(#{uid}-iris)"/>'
            f'<ellipse cx="{_f(ic)}" cy="{_f(icy + r * .05)}" rx="{_f(rx * .38)}" ry="{_f(ry * .46)}" fill="#1d2160" opacity=".75"/>'
            f'<path d="M{_f(ic - rx * .62)},{_f(icy + r * .48)} Q{_f(ic)},{_f(icy + r * .98)} {_f(ic + rx * .62)},{_f(icy + r * .48)} '
            f'Q{_f(ic)},{_f(icy + r * .7)} {_f(ic - rx * .62)},{_f(icy + r * .48)} Z" fill="#e6f0ff" opacity=".85"/>'
            f'<ellipse cx="{_f(ic - rx * .34 * side)}" cy="{_f(icy - r * .34)}" rx="{_f(r * .3)}" ry="{_f(r * .38)}" '
            f'transform="rotate({-18 * side} {_f(ic - rx * .34 * side)} {_f(icy - r * .34)})" fill="{WHITE}"/>'
            f'<circle cx="{_f(ic + rx * .4 * side)}" cy="{_f(icy + r * .36)}" r="{_f(r * .14)}" fill="{WHITE}"/>'
            f'<circle cx="{_f(ic + rx * .1 * side)}" cy="{_f(icy - r * .52)}" r="{_f(r * .07)}" fill="{WHITE}" opacity=".9"/>'
            f'<path d="M{_f(cx - rx * 1.05 * side)},{_f(cy - r * .32)} Q{_f(cx - rx * .3 * side)},{_f(cy - r * 1.28)} {_f(cx + rx * .95 * side)},{_f(cy - r * .52)} '
            f'L{_f(cx + rx * 1.35 * side)},{_f(cy - r * .78)} L{_f(cx + rx * 1.02 * side)},{_f(cy - r * .2)} '
            f'Q{_f(cx - rx * .2 * side)},{_f(cy - r * .98)} {_f(cx - rx * 1.05 * side)},{_f(cy - r * .32)} Z" fill="{INK}"/>')


def _blush(cx, cy, w=7.0):
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(w)}" ry="{_f(w * .5)}" fill="{BLUSH}" opacity=".6"/>'
            + ''.join(f'<path d="M{_f(cx - w * .55 + i * w * .45)},{_f(cy + w * .22)} l{_f(w * .26)},{_f(-w * .44)}" '
                      f'stroke="#e57f9b" stroke-width="1.1" stroke-linecap="round" opacity=".8"/>' for i in range(3)))


def _bubble(cx, cy, r, uid, sw=1.4):
    """Translucent anime water bubble: soft rim body, iridescent outline, white crescent + dot."""
    return (f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="url(#{uid}-bub)" stroke="url(#{uid}-iri)" stroke-width="{sw}"/>'
            f'<path d="M{_f(cx - r * .64)},{_f(cy - r * .02)} A{_f(r * .64)},{_f(r * .64)} 0 0,1 {_f(cx - r * .02)},{_f(cy - r * .64)}" '
            f'fill="none" stroke="{WHITE}" stroke-width="{_f(max(1.0, r * .2))}" stroke-linecap="round"/>'
            f'<circle cx="{_f(cx + r * .42)}" cy="{_f(cy + r * .4)}" r="{_f(max(.7, r * .11))}" fill="{WHITE}"/>')


def _sparkle(cx, cy, r, fill=WHITE, op=1.0, cls=''):
    k = r * .2
    c = f' class="{cls}"' if cls else ''
    return (f'<path{c} d="M{_f(cx)},{_f(cy - r)} Q{_f(cx + k)},{_f(cy - k)} {_f(cx + r)},{_f(cy)} Q{_f(cx + k)},{_f(cy + k)} '
            f'{_f(cx)},{_f(cy + r)} Q{_f(cx - k)},{_f(cy + k)} {_f(cx - r)},{_f(cy)} Q{_f(cx - k)},{_f(cy - k)} {_f(cx)},{_f(cy - r)} Z" '
            f'fill="{fill}" opacity="{op}"/>')


def _drop(cx, cy, s=1.0, rot=0, uid=''):
    """Small water droplet with cel shadow, ink outline and highlight."""
    d = 'M0,-9 C3,-4 6,-1 6,3 C6,7 3,9 0,9 C-3,9 -6,7 -6,3 C-6,-1 -3,-4 0,-9 Z'
    return (f'<g transform="translate({_f(cx)},{_f(cy)}) rotate({rot}) scale({s})">'
            f'<path d="{d}" fill="#a9c2ff" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M-5.2,4 C-2,6.5 2,6.5 5.6,2 C5.4,6.4 3,8.3 0,8.3 C-3,8.3 -5,6.6 -5.2,4 Z" fill="#7e9ef0"/>'
            f'<path d="M-3,2 C-3,0 -2,-2 -1,-3" stroke="{WHITE}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>')


def _strip(pts, w0, w1, a=-.5, b=.5, cap=True, t0=0.0, t1=1.0):
    """Closed outline of a tube along polyline pts: width w0 -> w1 (by arc length), left edge at
    a*w and right edge at b*w along the normal (a<0 = left of travel), round tip cap.
    t0..t1 restricts the strip to part of the length."""
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    tot = L[-1] or 1.0
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = L[i] / tot
        if t < t0 - 1e-9 or t > t1 + 1e-9:
            continue
        j0, j1 = max(0, i - 1), min(n - 1, i + 1)
        dx, dy = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        w = w0 + (w1 - w0) * t
        left.append((x + nx * w * a, y + ny * w * a))
        right.append((x + nx * w * b, y + ny * w * b))
    d = 'M' + ' L'.join(f'{_f(x)},{_f(y)}' for x, y in left)
    we = w0 + (w1 - w0) * min(t1, 1.0)
    if cap:
        rr = we * (b - a) / 2
        d += f' A{_f(rr)},{_f(rr)} 0 0,1 {_f(right[-1][0])},{_f(right[-1][1])}'
    d += ' L' + ' L'.join(f'{_f(x)},{_f(y)}' for x, y in reversed(right)) + ' Z'
    return d


def _quad(p0, p1, p2, n):
    return [((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def _style(uid, dur=3.4, amp=6, delay=0.0):
    return (f'<style>@keyframes {uid}-b{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-{amp}px)}}}}'
            f'@keyframes {uid}-u{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:1}}100%{{transform:translateY(-34px);opacity:0}}}}'
            f'@keyframes {uid}-t{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}'
            f'.{uid}-bob{{animation:{uid}-b {dur}s ease-in-out {delay}s infinite}}'
            f'.{uid}-up{{animation:{uid}-u 3.6s ease-out infinite}}'
            f'.{uid}-up2{{animation:{uid}-u 4.4s ease-out 1.6s infinite}}'
            f'.{uid}-tw{{animation:{uid}-t 2.6s ease-in-out infinite}}'
            f'.{uid}-tw2{{animation:{uid}-t 3.1s ease-in-out 1.2s infinite}}'
            f'@media (prefers-reduced-motion: reduce){{.{uid}-bob,.{uid}-up,.{uid}-up2,.{uid}-tw,.{uid}-tw2'
            f'{{animation:none}}}}</style>')


def _ground(rx, uid):
    return (f'<ellipse cx="0" cy="0" rx="{rx}" ry="{_f(rx * .15)}" fill="#7d78d0" opacity=".2"/>'
            f'<ellipse cx="0" cy="-.5" rx="{_f(rx * .62)}" ry="{_f(rx * .09)}" fill="#6f68c4" opacity=".16"/>')


def _open(x, y, scale, flip):
    sx = -scale if flip else scale
    return f'<g transform="translate({_f(x)},{_f(y)}) scale({sx},{scale})">'


# ------------------------------------------------------------------------------------------
# Gentilhomme Usher - round octopus in a gentleman's top hat with a monocle
# ------------------------------------------------------------------------------------------
def usher(x, y, scale=1, uid='us', flip=False, shadow=True, **_kw):
    B_TOP, B_MID, B_BOT = '#a3b5ff', '#889cf8', '#7c8ef2'
    T_HI, SUCK = '#a9b9ff', '#c9d3ff'
    o = [_open(x, y, scale, flip), _style(uid, 3.2, 6),
         '<defs>' + _common_defs(uid)
         + _lg(f'{uid}-body', 0, -128, 0, -34, [(0, B_TOP), (.55, B_MID), (1, B_BOT)])
         + _lg(f'{uid}-tent', 0, -50, 0, 0, [(0, '#6175de'), (.6, '#7b8aee'), (1, '#9c95f4')])
         + _lg(f'{uid}-tentb', 0, -50, 0, 0, [(0, '#4756be'), (1, '#6c6ad8')])
         + _rg(f'{uid}-core', -6, -56, 44, [(0, '#e4ebff', .5), (.6, '#c2ceff', .16), (1, '#c2ceff', 0)])
         + _lg(f'{uid}-crown', -22, 0, 22, 0, [(0, '#4b519e'), (.5, '#3a3f8c'), (1, '#2f3378')])
         + '</defs>']
    if shadow:
        o.append(_ground(52, uid))
    o.append(f'<g class="{uid}-bob">')

    # ---- tentacles: tapered tubes sweeping down and curling outward (back row first) ----
    specs = [(-10, -1, 7, True), (10, 1, 7, True),
             (-44, -1, 8.5, False), (44, 1, 8.5, False), (-24, -1, 7.5, False), (24, 1, 7.5, False)]
    for k, (bx, dx, cr, back) in enumerate(specs):
        cxp, cyp = bx + dx * (9 + abs(bx) * .3), -12 if not back else -16
        x0, y0, x1, y1 = bx * .8, -46, cxp - dx * cr, cyp
        mx, my = x0 + (x1 - x0) * .2 - dx * 4, -28
        pts = _quad((x0, y0), (mx, my), (x1, y1), 10)
        for i in range(1, 17):
            a = (math.pi - (i / 16) * 1.35 * math.pi) if dx > 0 else ((i / 16) * 1.35 * math.pi)
            r = cr * (1 - .5 * i / 16)
            pts.append((cxp + r * math.cos(a), cyp + r * math.sin(a)))
        w0 = 15 if back else 16.5
        d = _strip(pts, w0, 3.2)
        o.append(_cel(uid, f't{k}', d, f'url(#{uid}-tentb)' if back else f'url(#{uid}-tent)',
                      shadows=[(_strip(pts, w0, 3.2, -.7, -.06), SHADE, .3)],
                      highlights=[(_strip(pts, w0, 3.2, .18, .36, cap=False, t0=.04, t1=.5), T_HI, .9)],
                      sw=2.1, heavy=.8))
        # suckers along the curl
        for t in (11, 14, 18) if not back else (12, 16):
            if t < len(pts):
                px, py = pts[t]
                o.append(f'<ellipse cx="{_f(px)}" cy="{_f(py)}" rx="1.9" ry="1.5" fill="{SUCK}" opacity=".9"/>')

    # ---- body: squishy translucent ball ----
    body = 'M0,-128 C34,-128 58,-104 58,-74 C58,-50 40,-34 0,-34 C-40,-34 -58,-50 -58,-74 C-58,-104 -34,-128 0,-128 Z'
    inner = (f'<path d="M-58,-34 H58 V-128 H-58 Z" fill="url(#{uid}-core)"/>'
             # faint caustic ripples (water sheen)
             f'<path d="M-50,-104 q7,-4 14,0 t14,0 t14,0" fill="none" stroke="{WHITE}" stroke-width="1.5" opacity=".3"/>'
             f'<path d="M14,-46 q7,3 14,0 t14,0" fill="none" stroke="{WHITE}" stroke-width="1.3" opacity=".22"/>'
             # tiny bubbles inside the jelly
             f'<circle cx="-40" cy="-66" r="3.4" fill="none" stroke="{WHITE}" stroke-width="1.1" opacity=".55"/>'
             f'<circle cx="-46" cy="-56" r="1.8" fill="{WHITE}" opacity=".45"/>'
             f'<circle cx="44" cy="-92" r="2.6" fill="none" stroke="{WHITE}" stroke-width="1" opacity=".5"/>'
             # freckle spots
             f'<circle cx="-44" cy="-84" r="4.2" fill="#a7b7ff" opacity=".7"/><circle cx="-34" cy="-96" r="2.6" fill="#a7b7ff" opacity=".7"/>'
             f'<circle cx="47" cy="-78" r="3.6" fill="#a7b7ff" opacity=".55"/>'
             # hard cast shadow of the top hat brim on the head
             f'<ellipse cx="0" cy="0" rx="34" ry="7.5" transform="translate(13,-119.5) rotate(12)" fill="{SHADE}" opacity=".32"/>')
    o.append(_cel(uid, 'body', body, f'url(#{uid}-body)', extra=inner, sw=2.4, heavy=1.1,
                  form=(18, 22, .42), rim=(4, 1.5, RIM, .9), sheen=(-3, -3.5, .5),
                  highlights=[('M-44,-100 C-38,-116 -22,-124 -6,-124 C-20,-120 -32,-112 -38,-98 C-40,-94 -46,-94 -44,-100 Z', WHITE, .92),
                              ('M28,-118 C36,-114 42,-108 46,-100 C42,-102 36,-108 28,-118 Z', WHITE, .6),
                              # reflected light from the water below
                              ('M-44,-46 C-24,-37 18,-37 34,-42 C20,-33 -26,-33 -44,-46 Z', '#cdd6ff', .85)],
                  post=_sparkle(-26, -114, 5, WHITE, 1, f'{uid}-tw') + f'<circle cx="-12" cy="-121" r="1.8" fill="{WHITE}"/>'))
    # ---- face ----
    o.append(_eye(uid, -18, -74, 11, (.5, .5), -1) + _eye(uid, 18, -74, 11, (.5, .5), 1))
    o.append(_blush(-33, -58) + _blush(33, -58))
    o.append(f'<path d="M-6,-57 Q-3,-53 0,-57 Q3,-53 6,-57" fill="none" stroke="{INK}" stroke-width="1.9" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    # monocle: gold rim, glass glint, chain
    o.append(f'<circle cx="18" cy="-74" r="15" fill="#eef2ff" fill-opacity=".14"/>'
             f'<path d="M8,-80 L14,-86 M10,-74 L20,-84" stroke="{WHITE}" stroke-width="1.6" stroke-linecap="round" opacity=".75"/>'
             f'<circle cx="18" cy="-74" r="15" fill="none" stroke="{INK}" stroke-width="4.6"/>'
             f'<circle cx="18" cy="-74" r="15" fill="none" stroke="{GOLD}" stroke-width="2.4"/>'
             f'<path d="M5.5,-81.5 A15,15 0 0,1 18,-89" fill="none" stroke="{GOLD_HI}" stroke-width="1.4" stroke-linecap="round"/>'
             f'<path d="M30,-82 A15,15 0 0,1 31,-66" fill="none" stroke="{GOLD_SH}" stroke-width="1.4"/>'
             f'<path d="M31,-66 C40,-58 44,-50 40,-40" fill="none" stroke="{GOLD_SH}" stroke-width="1.5" stroke-dasharray="2.2 1.8"/>')
    # ---- top hat, tilted ----
    o.append('<g transform="translate(10,-124) rotate(12)">'
             + _cel(uid, 'brim', 'M-34,0 C-30,-7 30,-7 34,0 C30,7 -30,7 -34,0 Z', '#343884',
                    shadows=[('M-40,1 C-14,5 14,5 40,1 L40,10 L-40,10 Z', '#1f2258')],
                    highlights=[('M-28,-1.5 C-14,-4.5 10,-4.8 26,-2 C10,-3.4 -12,-3 -28,-1.5 Z', '#7b84d8')], sw=2.3)
             + _cel(uid, 'crown', 'M-20,-2 L-22,-44 C-10,-48 10,-48 22,-44 L20,-2 C8,1 -8,1 -20,-2 Z', f'url(#{uid}-crown)',
                    shadows=[('M8,-50 L30,-50 L30,4 L7,4 Z', SHADE, .35)],
                    highlights=[('M-16,-40 L-11,-41 L-10,-18 L-15,-18 Z', '#7078c9'),
                                ('M-16,-6 L-11,-6 L-11,-4 L-15.5,-4 Z', '#7078c9')],
                    rim=(2.5, 0, RIM, .7), sw=2.3)
             + _cel(uid, 'band', 'M-21,-16 C-8,-13 8,-13 21,-16 L20.5,-6 C8,-3 -8,-3 -20.5,-6 Z', GOLD,
                    shadows=[('M6,-20 L26,-20 L26,0 L6,0 Z', GOLD_SH)],
                    highlights=[('M-18,-13.5 C-8,-11.5 2,-11.5 4,-11.8 L4,-10.4 C-4,-10 -12,-10.4 -18,-12 Z', GOLD_HI)],
                    sw=1.7, heavy=0)
             + f'<path d="M-22,-44 C-10,-40 10,-40 22,-44" fill="none" stroke="{INK}" stroke-width="1.8"/>'
             + f'<path d="M-18,-43.5 C-8,-41.5 6,-41.5 14,-42.5" fill="none" stroke="#7078c9" stroke-width="1.2"/>'
             + '</g>')
    o.append('</g>')  # bob
    o.append(f'<g class="{uid}-up">{_bubble(-62, -40, 5, uid)}</g><g class="{uid}-up2">{_bubble(60, -70, 4, uid)}</g>'
             + _sparkle(-62, -132, 4.5, '#ffe9a8', 1, f'{uid}-tw2'))
    o.append('</g>')
    return ''.join(o)


# ------------------------------------------------------------------------------------------
# Surintendante Chevalmarin - bubble seahorse: pale azure, curled tail, pink fins, lady's hat
# ------------------------------------------------------------------------------------------
BCX, BCY, BR = 2, -110, 86     # Chevalmarin's bubble (centre, radius) at scale 1


def chevalmarin(x, y, scale=1, uid='cm', flip=False, shadow=True, strong_rim=False, **_kw):
    """strong_rim=True adds a bolder periwinkle + pink double rim (behind her) and a white
    lower sheen (in front), for pale backgrounds where the default rim washes out.  The bubble
    is a circle of radius BR centred at (BCX, BCY) in her local frame (scale 1, before flip)."""
    S_TOP, S_BOT = '#cfe2ff', '#80a3f6'
    BELLY, BELLY_SH = '#fff5f8', '#e6dcf6'
    o = [_open(x, y, scale, flip), _style(uid, 3.6, 7, .6),
         '<defs>' + _common_defs(uid)
         + _lg(f'{uid}-body', 0, -160, 0, -4, [(0, S_TOP), (.5, '#a8c6ff'), (1, '#8eaefa')])
         + _lg(f'{uid}-fin', -44, -92, -24, -52, [(0, '#ffd3e6'), (1, '#e7a8d6')])
         + _rg(f'{uid}-core', 18, -70, 38, [(0, WHITE, .6), (1, WHITE, 0)])
         + _rg(f'{uid}-big', BCX, BCY, BR, [(0, '#eef2ff', .04), (.8, '#dfe6ff', .14), (.96, '#c8d3ff', .48), (1, '#b9c6ff', .7)])
         + '</defs>']
    if shadow:
        o.append(_ground(40, uid))
    o.append(f'<g class="{uid}-bob">')
    # big bubble she floats in: the body of the bubble sits behind her, sized and centred so her
    # head, hat and feather are all inside it (only the tail curl pokes out of the bottom); the
    # rim sheen is drawn in front of her afterwards so she reads as *inside* the bubble.
    def arc(r, a0, a1):
        p0 = (BCX + r * math.cos(math.radians(a0)), BCY + r * math.sin(math.radians(a0)))
        p1 = (BCX + r * math.cos(math.radians(a1)), BCY + r * math.sin(math.radians(a1)))
        return f'M{_f(p0[0])},{_f(p0[1])} A{_f(r)},{_f(r)} 0 0,1 {_f(p1[0])},{_f(p1[1])}'
    o.append(f'<circle cx="{BCX}" cy="{BCY}" r="{BR}" fill="url(#{uid}-big)" stroke="url(#{uid}-iri)" stroke-width="2.4"/>')
    if strong_rim:
        o.append(f'<circle cx="{BCX}" cy="{BCY}" r="{BR}" fill="none" stroke="#8c96ec" stroke-width="2.6" opacity=".8"/>'
                 f'<circle cx="{BCX}" cy="{BCY}" r="{BR - 3.6}" fill="none" stroke="#ffd3ea" stroke-width="2.6" opacity=".75"/>')
    front_sheen = (f'<path d="{arc(BR * .84, 198, 238)}" fill="none" stroke="{WHITE}" stroke-width="5.5" stroke-linecap="round" opacity=".9"/>'
                   f'<path d="{arc(BR * .84, 184, 191)}" fill="none" stroke="{WHITE}" stroke-width="3.2" stroke-linecap="round" opacity=".85"/>'
                   f'<path d="{arc(BR * .9, 22, 48)}" fill="none" stroke="#ffd6ec" stroke-width="2.8" stroke-linecap="round" opacity=".9"/>'
                   + _sparkle(BCX - BR * .5, BCY - BR * .74, 6.5, WHITE, 1, f'{uid}-tw'))
    if strong_rim:
        front_sheen += f'<path d="{arc(BR * .93, 52, 74)}" fill="none" stroke="{WHITE}" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
    # dorsal fin (behind body), translucent sakura pink with ribs
    fin = ('M-24,-95 C-31,-98 -38,-94 -38,-88 C-45,-86 -47,-78 -43,-74 C-48,-70 -46,-61 -40,-60 '
           'C-40,-54 -32,-50 -24,-50 C-28,-64 -28,-80 -24,-95 Z')
    o.append(f'<g opacity=".86">' + _cel(
        uid, 'fin', fin, f'url(#{uid}-fin)', sw=2.0, heavy=.6,
        shadows=[('M-60,-66 C-44,-62 -34,-58 -24,-58 L-20,-40 L-60,-40 Z', PINK_SH, .55)],
        extra=f'<path d="M-26,-88 L-40,-84 M-26,-78 L-43,-74 M-26,-68 L-42,-63 M-25,-59 L-36,-56" '
              f'stroke="{WHITE}" stroke-width="1.5" stroke-linecap="round" opacity=".85"/>',
        sheen=(-2, -2, .6)) + '</g>')
    # tail: stem down from the body, then a spiral curling forward under the belly
    cx0, cy0, r0 = 12, -17, 15
    stem = _quad((-9, -50), (-6, -30), (cx0 - r0, cy0), 8)
    curl = []
    for i in range(1, 25):
        t = i / 24
        a = math.pi - t * 1.25 * 2 * math.pi
        r = r0 * (1 - .66 * t)
        curl.append((cx0 + r * math.cos(a), cy0 + r * math.sin(a)))
    pts = stem + curl
    tail = _strip(pts, 18, 4)
    rings = []
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    for i in range(2, len(pts) - 3, 2):
        (xa, ya), (xb, yb) = pts[i - 1], pts[i + 1]
        ln = math.hypot(xb - xa, yb - ya) or 1
        nx, ny = -(yb - ya) / ln, (xb - xa) / ln
        w = (18 + (4 - 18) * L[i] / L[-1]) * .42
        px, py = pts[i]
        rings.append(f'M{_f(px - nx * w)},{_f(py - ny * w)} L{_f(px + nx * w)},{_f(py + ny * w)}')
    o.append(_cel(uid, 'tail', tail, f'url(#{uid}-body)', sw=2.2, heavy=1,
                  shadows=[(_strip(pts, 18, 4, -.8, -.05), SHADE, .26)],
                  highlights=[(_strip(pts, 18, 4, .14, .3, cap=False, t0=.02, t1=.55), WHITE, .55)],
                  extra=f'<path d="{" ".join(rings)}" stroke="#6f8fe0" stroke-width="1.3" stroke-linecap="round" opacity=".6"/>'))
    # body / belly: S-curve, round belly bulging forward (+x)
    body = ('M-20,-110 C-4,-114 14,-106 18,-96 C38,-88 46,-70 40,-54 C34,-40 20,-34 4,-36 '
            'C-8,-36 -16,-42 -18,-50 C-24,-66 -30,-92 -20,-110 Z')
    belly = (f'<path d="{_ell(30, -68, 18, 32)}" fill="{BELLY}"/>'
             f'<path d="M20,-42 C32,-44 42,-52 47,-66 L50,-30 L14,-30 Z" fill="{BELLY_SH}"/>'
             f'<path d="M14,-90 Q26,-85 41,-84 M13,-80 Q26,-75 46,-74 M13,-70 Q26,-65 48,-64 M14,-60 Q26,-55 46,-54 M16,-50 Q24,-46 40,-46" '
             f'fill="none" stroke="#d9cdef" stroke-width="1.5" stroke-linecap="round"/>'
             f'<path d="{_ell(30, -68, 18, 32)}" fill="none" stroke="#8f9fe6" stroke-width="1.3"/>'
             f'<path d="M-20,-34 H50 V-112 H-20 Z" fill="url(#{uid}-core)"/>'
             f'<circle cx="-8" cy="-70" r="2.6" fill="none" stroke="{WHITE}" stroke-width="1" opacity=".6"/>'
             f'<circle cx="-12" cy="-60" r="1.5" fill="{WHITE}" opacity=".5"/>')
    o.append(_cel(uid, 'body', body, f'url(#{uid}-body)', sw=2.4, heavy=1.1, extra=belly,
                  form=(8, 9, .3), rim=(3, 1, RIM, .9), sheen=(-2.5, -2.5, .55),
                  highlights=[('M-17,-100 C-15,-107 -8,-109 -3,-108 C-9,-104 -12,-96 -13,-86 C-15,-88 -17,-94 -17,-100 Z', WHITE, .85)]))
    # snout first so the head overlaps it
    snout = 'M14,-130 C24,-129 36,-128 44,-128.5 C47,-129.6 51,-129 51,-123 C51,-117.4 47,-117 44,-118.2 C36,-119 24,-116 14,-113 Z'
    o.append(_cel(uid, 'snout', snout, f'url(#{uid}-body)', sw=2.2,
                  shadows=[('M10,-121 C24,-118 36,-119 60,-120 L60,-108 L10,-108 Z', SHADE, .26)],
                  highlights=[('M22,-127 C30,-126.4 38,-125.6 44,-127.6 C40,-125 30,-124.6 22,-125.4 Z', WHITE, .8)]))
    o.append(f'<path d="M50,-125.6 Q48.7,-123 50,-120.4" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    head = 'M-26,-128 C-26,-150 -8,-162 8,-158 C24,-154 32,-140 28,-124 C24,-108 8,-102 -6,-104 C-20,-106 -26,-114 -26,-128 Z'
    o.append(_cel(uid, 'head', head, f'url(#{uid}-body)', sw=2.4, heavy=1.1,
                  form=(8, 11, .34), rim=(3, 1, RIM, .9), sheen=(-2.5, -3, .55),
                  highlights=[('M-19,-140 C-15,-151 -5,-156 3,-155 C-7,-151 -13,-145 -15,-135 C-17,-135 -19,-137 -19,-140 Z', WHITE, .9)],
                  post=f'<circle cx="-4" cy="-152" r="1.6" fill="{WHITE}"/>'))
    # coronet crest on the back of the head
    o.append(_cel(uid, 'crest', 'M-24,-136 L-35,-141 L-27,-129 L-37,-126 L-26,-118 L-22,-120 Z', BELLY,
                  shadows=[('M-40,-125 L-20,-125 L-20,-110 L-40,-110 Z', BELLY_SH)], sw=1.9, heavy=.6))
    o.append(_eye(uid, 4, -130, 11, (1.6, .5), 1))
    o.append(f'<path d="M-7,-145 Q-1,-149 6,-148" fill="none" stroke="{INK}" stroke-width="1.9" stroke-linecap="round"/>')
    o.append(_blush(18, -114, 6))
    o.append(f'<path d="M8,-111 Q11,-107 14,-110" fill="none" stroke="{INK}" stroke-width="1.7" stroke-linecap="round"/>')
    # lady's hat: small tilted navy disc with white feather and pink ribbon
    o.append('<g transform="translate(-4,-158) rotate(-14)">'
             + _cel(uid, 'hbrim', 'M-22,0 C-18,-6 18,-6 22,0 C18,5 -18,5 -22,0 Z', '#3a438f',
                    shadows=[('M-30,1 C-10,4 10,4 30,1 L30,8 L-30,8 Z', '#262d6a')],
                    highlights=[('M-17,-1.5 C-6,-3.6 6,-3.6 16,-2 C6,-2.6 -6,-2.6 -17,-1.5 Z', '#8790e0')], sw=2.1)
             + _cel(uid, 'hcrown', 'M-12,-1 C-12,-14 12,-14 12,-1 Z', '#46509f',
                    shadows=[('M3,-16 L16,-16 L16,2 L3,2 Z', '#333b82')],
                    highlights=[('M-9,-6 C-9,-10 -5,-12.5 -2,-12.5 C-5,-10 -6.5,-8 -7,-5 Z', '#7f89da')], sw=2.1)
             + _cel(uid, 'ribbon', 'M-11.5,-6 C-4,-4 4,-4 11.5,-6 L12,-1 C4,1 -4,1 -12,-1 Z', PINK,
                    shadows=[('M2,-8 L14,-8 L14,2 L2,2 Z', PINK_SH)], sw=1.5, heavy=0)
             + _cel(uid, 'feather', 'M8,-8 C14,-26 28,-30 34,-26 C28,-22 20,-14 12,-4 Z', WHITE,
                    shadows=[('M13,-11 C20,-18 27,-23 36,-27 L40,0 L13,0 Z', '#d6dcf4')],
                    extra=f'<path d="M11,-6 C17,-16 24,-23 32,-26.5" fill="none" stroke="#a9b8ea" stroke-width="1.1"/>', sw=1.7, heavy=.5)
             + f'<circle cx="9" cy="-5" r="2.8" fill="{GOLD}" stroke="{INK}" stroke-width="1.2"/>'
             + f'<circle cx="8.2" cy="-5.8" r=".9" fill="{WHITE}"/>'
             + '</g>')
    o.append(front_sheen)
    o.append('</g>')  # bob
    o.append(f'<g class="{uid}-up">{_bubble(BCX + BR * .7, BCY - BR * .78, 6, uid)}{_bubble(BCX + BR * .56, BCY - BR * .98, 3.5, uid)}</g>'
             f'<g class="{uid}-up2">{_bubble(BCX + BR * .98, BCY - BR * .3, 4, uid)}</g>')
    o.append('</g>')
    return ''.join(o)


# ------------------------------------------------------------------------------------------
# Mademoiselle Crabaletta - heavy-armoured crab: navy lacquer shell, gold trim, maid bow
# ------------------------------------------------------------------------------------------
def crabaletta(x, y, scale=1, uid='cr', flip=False, shadow=True, **_kw):
    C_HI = '#cfdaff'
    o = [_open(x, y, scale, flip), _style(uid, 3.0, 5, 1.1),
         '<defs>' + _common_defs(uid)
         + _lg(f'{uid}-shell', 0, -90, 0, -22, [(0, '#788ff0'), (.5, '#5f76e0'), (1, '#5265d2')])
         + _lg(f'{uid}-limb', 0, -110, 0, 0, [(0, '#a5baff'), (1, '#7891ea')])
         + _lg(f'{uid}-limbb', 0, -110, 0, 0, [(0, '#8aa0f2'), (1, '#6479d8')])
         + _lg(f'{uid}-claw', 0, -32, 0, 14, [(0, '#b2c4ff'), (.55, '#91a9f6'), (1, '#7189e6')])
         + _rg(f'{uid}-core', 0, -40, 44, [(0, '#c6d2ff', .4), (1, '#c6d2ff', 0)])
         + '</defs>']
    if shadow:
        o.append(_ground(68, uid))
    o.append(f'<g class="{uid}-bob">')
    # legs (behind): three per side, two segments each - thick upper leg, pointed lower leg
    for sgn in (-1, 1):
        for i, bx in enumerate((22, 36, 48)):
            kx, ky = sgn * (bx + 19), -38 + i * 3                      # knee
            up = _quad((sgn * bx, -36), (sgn * (bx + 10), -50 + i * 3), (kx, ky), 6)
            lo = _quad((kx, ky), (sgn * (bx + 26), -24), (sgn * (bx + 23 - i * 2), -1), 7)
            fill = f'url(#{uid}-limbb)' if i == 1 else f'url(#{uid}-limb)'
            sh = (-.9, -.05) if sgn > 0 else (.05, .9)
            hl = (.12, .32) if sgn > 0 else (-.32, -.12)
            o.append(_cel(uid, f'lgl{sgn}{i}', _strip(lo, 10.5, 2, cap=False), fill,
                          shadows=[(_strip(lo, 10.5, 2, *sh, cap=False), SHADE, .3)],
                          highlights=[(_strip(lo, 10.5, 2, *hl, cap=False, t0=.1, t1=.5), WHITE, .5)], sw=1.9, heavy=.6))
            o.append(_cel(uid, f'lgu{sgn}{i}', _strip(up, 12, 11), fill,
                          shadows=[(_strip(up, 12, 11, *sh), SHADE, .3)],
                          highlights=[(_strip(up, 12, 11, *hl, cap=False, t0=.15, t1=.8), WHITE, .55)], sw=1.9, heavy=.6))
    # claw arms
    for sgn in (-1, 1):
        pts = _quad((sgn * 44, -52), (sgn * 62, -60), (sgn * 64, -78), 8)
        o.append(_cel(uid, f'arm{sgn}', _strip(pts, 14, 11, cap=False), f'url(#{uid}-limb)',
                      shadows=[(_strip(pts, 14, 11, -.9, 0) if sgn > 0 else _strip(pts, 14, 11, 0, .9), SHADE, .25)],
                      sw=2.1, heavy=.7))
    # pincers, raised
    for sgn, nm in ((-1, 'cl'), (1, 'cr')):
        big = ('M-12,12 C-24,4 -25,-16 -12,-25 C-2,-32 14,-31 22,-21 C25,-17 25,-12 22,-11 C16,-15 9,-15 3,-11 '
               'C9,-9 15,-7 19,-3 C21,0 19,3 16,3 C10,9 0,15 -12,12 Z')
        g = f'<g transform="translate({sgn * 66},-92) scale({sgn},1)">'
        g += _cel(uid, nm + 'b', big, f'url(#{uid}-claw)', sw=2.4, heavy=1,
                  form=(6, 7, .3), rim=(2.5, 1, RIM, .9) if sgn > 0 else None,
                  highlights=[('M-17,-4 C-18,-15 -11,-23 -3,-25 C-9,-19 -12,-12 -13,-3 C-14,-1 -17,-1 -17,-4 Z', WHITE, .85),
                              ('M8,-27 C13,-26 18,-23 21,-19 L18,-18 C16,-21 12,-24 8,-27 Z', C_HI)],
                  post=_sparkle(-12, -17, 3.6, WHITE, 1))
        g += f'<path d="M-1,-25 C2,-20 3,-15 3,-11" fill="none" stroke="{INK}" stroke-width="1.4" stroke-linecap="round" opacity=".7"/>'
        g += f'<path d="M-2,4 C2,2 6,0 9,-3" fill="none" stroke="#6077d6" stroke-width="1.2" stroke-linecap="round" opacity=".7"/>'
        g += f'<circle cx="-6" cy="-4" r="2.6" fill="{GOLD}" stroke="{INK}" stroke-width="1.1"/><circle cx="-6.8" cy="-4.8" r=".8" fill="{WHITE}"/>'
        g += '</g>'
        o.append(g)
    # eye stalks + eyeballs
    for sgn in (-1, 1):
        pts = _quad((sgn * 20, -80), (sgn * 26, -94), (sgn * 28, -104), 6)
        o.append(_cel(uid, f'stalk{sgn}', _strip(pts, 9, 7.5, cap=False), f'url(#{uid}-limb)',
                      shadows=[(_strip(pts, 9, 7.5, -.9, 0) if sgn > 0 else _strip(pts, 9, 7.5, 0, .9), SHADE, .25)],
                      sw=1.9, heavy=.5))
    for sgn in (-1, 1):
        o.append(_cel(uid, f'eb{sgn}', _circ(sgn * 29, -110, 13.5), WHITE,
                      shadows=[(_ell(sgn * 29 + 5, -101, 15, 6.5), '#d9e0fb')], sw=2.3, heavy=.9,
                      rim=(2.5, 1, '#ffe2f2', 1) if sgn > 0 else None))
        o.append(_eye(uid, sgn * 29 + sgn * 1, -109, 9.6, (0, 1), sgn))
    # shell / armour body: wide lacquered dome
    shell = 'M-58,-46 C-60,-74 -34,-90 0,-90 C34,-90 60,-74 58,-46 C56,-30 36,-22 0,-22 C-36,-22 -56,-30 -58,-46 Z'
    plates = (f'<path d="M-58,-22 H58 V-90 H-58 Z" fill="url(#{uid}-core)"/>'
              f'<path d="M-30,-86 C-26,-62 -24,-44 -22,-22 M30,-86 C26,-62 24,-44 22,-22" fill="none" stroke="{INK}" stroke-width="1.8"/>'
              f'<path d="M-27,-86 C-23,-62 -21,-44 -19,-22 M27,-86 C23,-62 21,-44 19,-22" fill="none" stroke="{GOLD}" stroke-width="2.2"/>'
              f'<path d="M-25.6,-80 C-23,-64 -22,-56 -21.4,-50" fill="none" stroke="{GOLD_HI}" stroke-width="1" stroke-linecap="round"/>')
    trims = (f'<path d="M-58,-50 C-30,-40 30,-40 58,-50" fill="none" stroke="{GOLD}" stroke-width="3.2"/>'
             f'<path d="M-50,-49.5 C-30,-42.4 -10,-41 6,-41.2" fill="none" stroke="{GOLD_HI}" stroke-width="1" stroke-linecap="round"/>'
             f'<path d="M-58,-46.6 C-30,-36.6 30,-36.6 58,-46.6" fill="none" stroke="{INK}" stroke-width="1.4"/>'
             f'<path d="M20,-42 C36,-44 50,-48 58,-51" fill="none" stroke="{GOLD_SH}" stroke-width="3.2"/>'
             + ''.join(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="{GOLD}" stroke="{INK}" stroke-width=".9"/>'
                       f'<circle cx="{cx - .7}" cy="{cy - .7}" r=".7" fill="{WHITE}"/>'
                       for cx, cy in [(-44, -62), (44, -62), (-40, -76), (40, -76)]))
    o.append(_cel(uid, 'shell', shell, f'url(#{uid}-shell)', sw=2.6, heavy=1.2, extra=plates,
                  form=(14, 15, .42), rim=(4, 1.5, RIM, .85), sheen=(-3, -3.5, .45),
                  highlights=[('M-46,-62 C-40,-78 -22,-86 -4,-87 C-20,-82 -34,-74 -40,-60 C-42,-56 -47,-57 -46,-62 Z', WHITE, .9),
                              ('M8,-86 C14,-86 20,-85 24,-84 C20,-83.5 14,-84 8,-84.6 Z', WHITE, .7),
                              ('M-40,-28 C-20,-24 20,-24 40,-28 C24,-22 -24,-22 -40,-28 Z', '#93a6f6', .7)],
                  post=trims + _sparkle(-30, -80, 4.5, WHITE, 1, f'{uid}-tw')))
    # face on the front plate
    o.append(f'<path d="M-7,-59 Q-3.5,-54 0,-59 Q3.5,-54 7,-59" fill="none" stroke="{INK}" stroke-width="1.9" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(_blush(-15, -63, 6) + _blush(15, -63, 6))
    # maid headdress: white frilled band + pink bow on top of the shell
    frill = 'M-16,-88 C-15,-95 -10,-97 -7,-93 C-5,-98 5,-98 7,-93 C10,-97 15,-95 16,-88 C6,-91 -6,-91 -16,-88 Z'
    o.append(_cel(uid, 'frill', frill, WHITE, shadows=[('M-30,-91 C-10,-92 10,-92 30,-91 L30,-80 L-30,-80 Z', '#d6dcf4')],
                  sw=1.9, heavy=.5))
    bow = 'M0,-97 C-5,-105 -15,-108 -15,-100 C-15,-93 -6,-93 0,-97 Z M0,-97 C5,-105 15,-108 15,-100 C15,-93 6,-93 0,-97 Z'
    o.append(_cel(uid, 'bow', bow, PINK, shadows=[('M-24,-99 C-10,-97 10,-97 24,-99 L24,-90 L-24,-90 Z', PINK_SH)],
                  highlights=[('M-12.5,-102 C-12,-104.6 -9,-105 -6,-102.6 C-9,-103 -11,-102.8 -12.5,-102 Z', PINK_HI),
                              ('M6,-102.6 C9,-105 12,-104.6 12.5,-102 C11,-102.8 9,-103 6,-102.6 Z', PINK_HI)], sw=1.9, heavy=.5))
    o.append(f'<circle cx="0" cy="-97" r="3" fill="{GOLD}" stroke="{INK}" stroke-width="1.5"/><circle cx="-.8" cy="-97.8" r=".9" fill="{WHITE}"/>')
    o.append('</g>')  # bob
    o.append(f'<g class="{uid}-up">{_drop(-80, -40, .7, -15)}</g><g class="{uid}-up2">{_bubble(82, -50, 4.5, uid)}</g>'
             + _sparkle(78, -112, 4.5, '#ffe9a8', 1, f'{uid}-tw2'))
    o.append('</g>')
    return ''.join(o)


def salon_trio(x, y, scale=1, uid='st', flip=False, shadow=True, gap=190, **_kw):
    """Usher - Chevalmarin - Crabaletta in a row; (x, y) under the seahorse."""
    return (_open(x, y, scale, flip)
            + usher(-gap, 0, 1, uid + 'u', shadow=shadow) + crabaletta(gap, 0, 1, uid + 'c', shadow=shadow)
            + chevalmarin(0, -6, 1, uid + 'm', shadow=shadow)
            + '</g>')


def showcase():
    W, H = 900, 600
    uid = 'sc'
    rays = ''.join(f'<path d="M{x0},0 L{x0 + w},0 L{x0 + w + 140},{H} L{x0 + 120},{H} Z" fill="#ffffff" opacity="{op}"/>'
                   for x0, w, op in ((150, 60, .16), (330, 34, .12), (560, 80, .14), (760, 30, .1)))
    bubbles = ''.join(_bubble(bx, by, r, uid) for bx, by, r in
                      [(70, 90, 14), (110, 140, 6), (820, 110, 18), (780, 170, 7), (450, 70, 9), (300, 540, 6), (640, 548, 10)])
    drops = _drop(240, 120, 1.0, 10) + _drop(690, 90, .8, -12) + _drop(884, 240, .7) + _drop(40, 330, .8)
    sparks = _sparkle(200, 220, 7, WHITE) + _sparkle(700, 240, 6, '#ffe9a8') + _sparkle(520, 120, 5, WHITE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Chibi fan art: an octopus in a top hat, a seahorse in a bubble and an armoured crab">'
            '<defs><linearGradient id="sc-bg" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#e9ecff"/><stop offset=".55" stop-color="#dde4ff"/><stop offset="1" stop-color="#fbe6f1"/>'
            '</linearGradient><radialGradient id="sc-glow" cx=".5" cy=".55" r=".5">'
            '<stop offset="0" stop-color="#ffffff" stop-opacity=".8"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
            + _common_defs(uid) + '</defs>'
            f'<rect width="{W}" height="{H}" fill="url(#sc-bg)"/>{rays}<ellipse cx="450" cy="340" rx="430" ry="230" fill="url(#sc-glow)"/>'
            '<path d="M0,470 C150,450 300,488 450,470 C600,452 750,488 900,468 L900,600 L0,600 Z" fill="#d3dbff" opacity=".7"/>'
            '<path d="M0,500 C160,486 310,514 460,500 C610,486 760,512 900,498" fill="none" stroke="#ffffff" stroke-width="3" opacity=".8"/>'
            + bubbles + drops + sparks
            + salon_trio(450, 488, 1.52)
            + '</svg>')


def build(out_dir):
    """Write the showcase as salon.svg into out_dir (returns the path)."""
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, 'salon.svg')
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(showcase())
    return p


if __name__ == '__main__':
    print('wrote', build('/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/scratchpad/v10final/chars'))
