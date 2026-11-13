"""Chibi Furina fan art (non-commercial, original SVG drawing; nothing traced or downloaded).

    furina(x, y, scale=1, uid='fu', pose='present', expr='smile', flip=False) -> SVG <g> string

    (x, y)  ground point between her feet.
    pose    'present'  right arm swept out, palm up under a floating water droplet; other hand on hip
            'judge'    one arm raised high, pointing dramatically; other fist on hip
            'bow'      theatrical curtsy: top hat swept off in one hand, other arm flourished out
            'point'    level courtroom point; other hand on hip
            'laugh'    back of the hand to the mouth ("ohoho~"); other hand on hip
    expr    'smile' | 'smug' | 'laugh'   (also 'wink', 'serene' = closed happy eyes)
            pass None to use the pose's natural expression.
    flip    mirror horizontally.

    Bounding box at scale 1 relative to (x, y): BBOX_BY_POSE[pose] (x mirrored when flip=True),
    BBOX = union of all poses, or call bbox(pose, scale, flip).
    Every id is prefixed with uid -- use a distinct uid per instance.  Python 3 stdlib only.
    Running this file writes a showcase SVG into the scratchpad (never into the repo).
"""
import math
import os

# ---------------------------------------------------------------- palette (no green: hues kept 200-345)
INK = '#363170'          # deep indigo line ink
INK2 = '#5b5aa6'         # softer ink for inner hair strands
HAIR, HAIR_TIP = '#eaedfd', '#d2e0ff'
HAIR_SH, HAIR_SH2 = '#bfc9ef', '#a3b1e5'
INNER, INNER_SH = '#b4c8f6', '#8eaaea'      # light-blue under-layer of her hair
STREAK, STREAK_SH = '#8db4f4', '#6a92df'
SKIN, SKIN_SH, SKIN_SH2 = '#fff3ec', '#f7d3cf', '#eeb9bb'
BLUSH = '#f7a0b6'
NAVY, NAVY_SH, NAVY_HI = '#34428c', '#252f6a', '#6479cf'
WHITE, WHITE_SH = '#ffffff', '#d7dcf5'
GLOVE, GLOVE_SH = '#ffffff', '#d3d9f4'
LB, LB_SH, LB_HI = '#9fc4ff', '#6f99e6', '#e4f0ff'
GOLD, GOLD_SH = '#f4d488', '#d3a256'
MOUTH, TONGUE = '#c24a6a', '#f597ad'

SW = 2.0     # inner line weight
SIL = 6.0    # silhouette stroke (=> ~3 units of outer contour outside every shape)

# bounding box of the drawing relative to (x, y) at scale 1: (min_x, min_y, max_x, max_y)
BBOX_BY_POSE = {   # measured from renders (includes the ~3-unit outer contour), +1 unit margin
    'present': (-110, -287, 110, 5),
    'judge':   (-110, -287, 110, 5),
    'bow':     (-114, -269, 101, 5),
    'point':   (-110, -287, 110, 5),
    'laugh':   (-110, -287, 110, 5),
}
# union over all poses (kept as a 4-tuple for backward compatibility with the old BBOX constant)
BBOX = (-114, -287, 110, 5)

DEFAULT_EXPR = {'present': 'smile', 'judge': 'smug', 'bow': 'serene', 'point': 'smile', 'laugh': 'laugh'}


# ---------------------------------------------------------------- geometry helpers
def _f(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def _pt(p):
    return f'{_f(p[0])},{_f(p[1])}'


def _segs(P, closed=False, k=1 / 6, nd=1):
    """Catmull-Rom through P -> cubic segments (no leading M); joins are smooth, so 'S' after the first."""
    n = len(P)
    q = (lambda p: f'{round(p[0])},{round(p[1])}') if nd == 0 else _pt
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[0]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        if i == 0 or (not closed and i == 1 and False):
            out.append(f'C{q(c1)} {q(c2)} {q(p2)}')
        else:
            out.append(f'S{q(c2)} {q(p2)}')
    return out


def _thin(P):
    """Keep every other point (always keeping both ends) for inner fills."""
    return P if len(P) < 7 else P[:-1:2] + [P[-1]]


def _smooth(P, closed=False, nd=1):
    q = (lambda p: f'{round(p[0])},{round(p[1])}') if nd == 0 else _pt
    return f'M{q(P[0])}' + ''.join(_segs(P, closed, nd=nd)) + ('Z' if closed else '')


def _cr(P, per=7):
    """Sample a Catmull-Rom spline through P (open)."""
    n = len(P)
    out = []
    for i in range(n - 1):
        p0 = P[i - 1] if i > 0 else P[0]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < n else P[-1]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                   + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    out.append(P[-1])
    return out


def _frame(C):
    """Arc-length fractions and unit normals for a sampled centre line."""
    L = [0.0]
    for a, b in zip(C, C[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = L[-1] or 1
    T = [l / tot for l in L]
    N = []
    for i in range(len(C)):
        a = C[max(0, i - 1)]
        b = C[min(len(C) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        N.append((-dy / d, dx / d))
    return T, N


def _prof(t, kind='lock'):
    if kind == 'long':      # keeps its width, then curls to a point
        return (1 - t ** 3.2) * (1 + .15 * math.sin(math.pi * t))
    if kind == 'flick':     # fluffy lock: bulges, then a sharp outward point
        return (1 - t) ** .85 * (1 + .45 * math.sin(math.pi * t))
    return (1 - t) ** .9 * (1 + .3 * math.sin(math.pi * t))


def _edge(C, T, N, W, f):
    """Points at signed width fraction f (-.5 .. .5) across the lock."""
    return [(c[0] + n[0] * w * f, c[1] + n[1] * w * f) for c, n, w in zip(C, N, W)]


# ---------------------------------------------------------------- builder with a silhouette pass
class _Fig:
    def __init__(self, uid):
        self.uid = uid
        self.o = []
        self.sil = []
        self.n = 0
        self.defs = []

    def nid(self, tag):
        self.n += 1
        return f'{self.uid}-{tag}{self.n}'

    def push(self, tf):
        self.o.append(f'<g transform="{tf}">')
        self.sil.append(f'<g transform="{tf}">')

    def pop(self):
        self.o.append('</g>')
        self.sil.append('</g>')

    def add(self, s):
        self.o.append(s)

    def cel(self, d, base, shadows=(), highlights=(), sw=SW, extra='', sil=True, outline=True, clip=True):
        """Filled shape + clipped hard-edged shade/highlight shapes + ink outline (geometry stored once)."""
        pid = self.nid('p')
        self.defs.append(f'<path id="{pid}" d="{d}"/>')
        ref = f'href="#{pid}"'
        inner = ''.join(f'<path d="{sd}" fill="{col}"/>' for sd, col in list(shadows) + list(highlights)) + extra
        s = f'<use {ref} fill="{base}"/>'
        if inner and not clip:
            s += inner
        elif inner:
            cid = self.nid('c')
            s = (f'<clipPath id="{cid}"><use {ref}/></clipPath>' + s
                 + f'<g clip-path="url(#{cid})">{inner}</g>')
        if outline:
            s += f'<use {ref} fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'
        self.o.append(s)
        if sil:
            self.sil.append(f'<use {ref}/>')

    def tube(self, d, col, sh, w, sw=SW, shade_off=(.26, .2)):
        self.o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{_f(w + 2 * sw)}" stroke-linecap="round"/>'
                      f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{_f(w)}" stroke-linecap="round"/>'
                      f'<path d="{d}" fill="none" stroke="{sh}" stroke-width="{_f(w * .36)}" stroke-linecap="round" '
                      f'transform="translate({_f(w * shade_off[0])},{_f(w * shade_off[1])})"/>')
        self.sil.append(f'<path d="{d}" fill="none" stroke-width="{_f(w + SIL)}"/>')

    def lock(self, pts, w, base, shade=HAIR_SH, side=1, kind='lock', shade_f=.42, shade_t0=.18,
             streak=None, streak_f=(-.05, .2), streak_t=(.12, .92), hl=True, hl_col='#ffffff',
             sw=SW, strands=0, per=3, ink=INK):
        """A tapered hair lock along a spline through pts. side=+1 shades the left-hand edge (in travel dir)."""
        C = _cr(pts, per)
        T, N = _frame(C)
        W = [w * _prof(t, kind) for t in T]
        Ledge = _edge(C, T, N, W, .5)
        Redge = _edge(C, T, N, W, -.5)
        d = (f'M{_pt(Ledge[0])}' + ''.join(_segs(Ledge)) + f'L{_pt(Redge[-1])}'
             + ''.join(_segs(Redge[::-1])) + 'Z')
        inner = []
        # hard-edged cel shadow hugging one edge, starting from a point
        se = .5 * side
        idx = [i for i, t in enumerate(T) if t >= shade_t0]
        if idx and shade:
            def sf(t):
                r = min(1, (t - shade_t0) / .16)
                return se - side * shade_f * r
            a = [(C[i][0] + N[i][0] * W[i] * sf(T[i]), C[i][1] + N[i][1] * W[i] * sf(T[i])) for i in idx]
            b = [(C[i][0] + N[i][0] * W[i] * se, C[i][1] + N[i][1] * W[i] * se) for i in idx]
            inner.append(f'<path d="{_smooth(_thin(a) + _thin(b)[::-1], True, nd=0)}" fill="{shade}"/>')
        if streak:
            t0, t1 = streak_t
            ids = [i for i, t in enumerate(T) if t0 <= t <= t1]
            if len(ids) > 2:
                def taper(t):
                    u = (t - t0) / (t1 - t0)
                    return math.sin(math.pi * min(1, max(0, u))) ** .6
                c0, hw = streak_f
                a = [(C[i][0] + N[i][0] * W[i] * (c0 + hw * taper(T[i])), C[i][1] + N[i][1] * W[i] * (c0 + hw * taper(T[i]))) for i in ids]
                b = [(C[i][0] + N[i][0] * W[i] * (c0 - hw * taper(T[i])), C[i][1] + N[i][1] * W[i] * (c0 - hw * taper(T[i]))) for i in ids]
                inner.append(f'<path d="{_smooth(_thin(a) + _thin(b)[::-1], True, nd=0)}" fill="{streak}"/>')
        if hl:
            ids = [i for i, t in enumerate(T) if .06 <= t <= .5]
            if len(ids) > 2:
                le = -.5 * side
                def hf(t):
                    u = (t - .06) / .44
                    return .2 * math.sin(math.pi * u) ** .7
                a = [(C[i][0] + N[i][0] * W[i] * (le + side * .07), C[i][1] + N[i][1] * W[i] * (le + side * .07)) for i in ids]
                b = [(C[i][0] + N[i][0] * W[i] * (le + side * (.07 + hf(T[i]))), C[i][1] + N[i][1] * W[i] * (le + side * (.07 + hf(T[i])))) for i in ids]
                inner.append(f'<path d="{_smooth(_thin(a) + _thin(b)[::-1], True, nd=0)}" fill="{hl_col}" opacity=".9"/>')
        for k in range(strands):
            fr = -.15 + .3 * k / max(1, strands - 1) if strands > 1 else .05
            ids = [i for i, t in enumerate(T) if .2 <= t <= .75]
            pts2 = [(C[i][0] + N[i][0] * W[i] * fr, C[i][1] + N[i][1] * W[i] * fr) for i in ids]
            if len(pts2) > 2:
                inner.append(f'<path d="{_smooth(pts2)}" fill="none" stroke="{INK2}" stroke-width="1.1" stroke-linecap="round" opacity=".6"/>')
        self.cel(d, base, extra=''.join(inner), sw=sw, clip=False)
        return d

    def render(self):
        return ('<defs>' + ''.join(self.defs) + '</defs>'
                + f'<g fill="{INK}" stroke="{INK}" stroke-width="{SIL}" stroke-linejoin="round" stroke-linecap="round">'
                + ''.join(self.sil) + '</g>' + ''.join(self.o))


# ---------------------------------------------------------------- hands
def _hand(F, cx, cy, rot, kind='open', flipy=False, scale=1.0):
    """Small white-gloved hand. Local frame: wrist at origin, fingers toward +x, thumb toward -y."""
    fy = ' scale(1,-1)' if flipy else ''
    sc = f' scale({scale})' if scale != 1 else ''
    F.push(f'translate({_f(cx)},{_f(cy)}) rotate({_f(rot)}){fy}{sc}')
    palm = 'M1,-6 C5,-8.2 10.5,-7.8 13,-5 C15,-2.5 15,2.5 13,5 C10.5,7.6 5,8 1,6 C-.5,3 -.5,-3 1,-6 Z'
    if kind == 'open':
        fingers = [((11, -4.4), (19.5, -8.2), 3.7), ((12, -1.4), (22, -3), 3.9), ((12, 1.5), (21.2, 2.2), 3.8),
                   ((10.5, 4.2), (17.6, 6.6), 3.3)]
        thumb = ((4.5, -5), (9.5, -11.5), 4.1)
    elif kind == 'point':
        fingers = [((11.5, 4.4), (14.4, 5.4), 3.8), ((12.4, 1.8), (15.4, 2.4), 4.0), ((12.6, -.8), (15.6, -.6), 4.0),
                   ((11, -3.7), (24.5, -5.2), 3.9)]
        thumb = ((4.5, -5.2), (12, -1.6), 4.1)
    elif kind == 'flat':
        fingers = [((10.5, 3.8), (18.6, 4.8), 3.4), ((11.5, 1.3), (21, 1.7), 3.6), ((11.5, -1.3), (21.6, -1.5), 3.6),
                   ((11, -3.8), (20, -4.8), 3.4)]
        thumb = ((4.5, -5), (11, -8.6), 4.0)
    elif kind == 'grip':     # curled round something (hat brim)
        fingers = [((11, 4.6), (12.8, 7.6), 3.8), ((12, 2), (14.4, 5.2), 4.0), ((12.4, -.6), (15, 2.6), 4.0),
                   ((11.8, -3.2), (14.6, .2), 3.9)]
        thumb = ((4.5, -5.6), (13.5, -6.6), 4.1)
    else:                    # 'fist' seen from the back, knuckles out
        fingers = [((11.4, 4.2), (13.6, 4.8), 4.0), ((12.4, 1.5), (14.8, 1.8), 4.2), ((12.4, -1.3), (14.8, -1.4), 4.2),
                   ((11.4, -4), (13.8, -4.6), 4.0)]
        thumb = ((4.5, -5.4), (11.6, -6.6), 4.0)
    fl = lambda a, b: f'M{_pt(a)} L{_pt(b)}'
    hs = 1.5
    o = []
    # cuff (light-blue ruffled glove cuff) behind the hand
    cuff = 'M-5,-8.4 C-2,-9.6 1,-9.2 2.4,-8 C3.6,-3 3.6,3 2.4,8 C1,9.4 -2,9.6 -5,8.4 C-3.6,3 -3.6,-3 -5,-8.4 Z'
    o.append(f'<path d="{cuff}" fill="{LB}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
             f'<path d="M-.4,-8.6 C.8,-3 .8,3 -.4,8.6 L2.4,8 C3.6,3 3.6,-3 2.4,-8 Z" fill="{LB_SH}"/>')
    # union: all ink first, then all fills -> no seams between palm and fingers
    o.append(f'<path d="{palm}" fill="{INK}" stroke="{INK}" stroke-width="{2 * hs}" stroke-linejoin="round"/>')
    for a, b, w in fingers:
        o.append(f'<path d="{fl(a, b)}" stroke="{INK}" stroke-width="{_f(w + 2 * hs)}" stroke-linecap="round"/>')
    o.append(f'<path d="{palm}" fill="{GLOVE}"/>')
    o.append(f'<path d="M1,2.2 C5,4.4 10,4.4 14.6,2 C14.4,4 13.6,5 13,5 C10.5,7.6 5,8 1,6 C.4,4.6 .4,3.4 1,2.2 Z" fill="{GLOVE_SH}"/>')
    for a, b, w in fingers:
        o.append(f'<path d="{fl(a, b)}" stroke="{GLOVE}" stroke-width="{_f(w)}" stroke-linecap="round"/>')
        o.append(f'<path d="{fl(a, b)}" stroke="{GLOVE_SH}" stroke-width="{_f(w * .34)}" stroke-linecap="round" '
                 f'transform="translate(0,{_f(w * .24)})"/>')
    # finger separations: short ink lines between neighbouring fingers, from the gap toward the knuckles
    for (a1, b1, w1), (a2, b2, w2) in zip(fingers, fingers[1:]):
        L1 = math.hypot(b1[0] - a1[0], b1[1] - a1[1])
        L2 = math.hypot(b2[0] - a2[0], b2[1] - a2[1])
        if min(L1, L2) < 5:
            # knuckle bumps: a short notch
            m = ((b1[0] + b2[0]) / 2 + 1, (b1[1] + b2[1]) / 2)
            o.append(f'<path d="M{_pt(m)} l-3.2,0" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>')
            continue
        L = min(L1, L2)
        e = ((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2)
        s = ((a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2)
        p = (s[0] + (e[0] - s[0]) * .35, s[1] + (e[1] - s[1]) * .35)
        q = (s[0] + (e[0] - s[0]) * .97, s[1] + (e[1] - s[1]) * .97)
        o.append(f'<path d="M{_pt(p)} L{_pt(q)}" stroke="{INK}" stroke-width="1.15" stroke-linecap="round"/>')
    # thumb on top with its own outline
    a, b, w = thumb
    o.append(f'<path d="{fl(a, b)}" stroke="{INK}" stroke-width="{_f(w + 2 * hs)}" stroke-linecap="round"/>'
             f'<path d="{fl(a, b)}" stroke="{GLOVE}" stroke-width="{_f(w)}" stroke-linecap="round"/>'
             f'<path d="{fl(a, b)}" stroke="{GLOVE_SH}" stroke-width="{_f(w * .32)}" stroke-linecap="round" transform="translate(.8,.6)"/>')
    # glove seam
    o.append(f'<path d="M3.5,-2.5 C6,-1 6.5,1.5 5.5,3.5" fill="none" stroke="{WHITE_SH}" stroke-width="1" stroke-linecap="round"/>')
    F.add(''.join(o))
    # silhouette
    F.sil.append(f'<path d="{palm}"/>' + ''.join(
        f'<path d="{fl(a, b)}" fill="none" stroke-width="{_f(w + SIL)}"/>' for a, b, w in fingers + [thumb]))
    F.pop()


# ---------------------------------------------------------------- eyes / face
def _eye(F, cx, cy, side, top, mid, bot, expr):
    """side = -1 for the viewer-left eye, +1 for viewer-right. Outer corner is toward `side`."""
    s = side
    if expr in ('laugh', 'serene') or (expr == 'wink' and side > 0):
        # happy closed eye: thick arch + lash flick
        F.add(f'<path d="M{_f(cx - 12)},{_f(cy + 3)} Q{_f(cx)},{_f(cy - 11)} {_f(cx + 12)},{_f(cy + 3)}" fill="none" stroke="{INK}" '
              f'stroke-width="3.6" stroke-linecap="round"/>'
              f'<path d="M{_f(cx + 10 * s)},{_f(cy - 1.5)} l{_f(5 * s)},-3.4" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
        return
    gid = F.nid('ig')
    F.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{top}"/><stop offset=".55" stop-color="{mid}"/>'
                  f'<stop offset="1" stop-color="{bot}"/></linearGradient>')
    w, h = 12, 15.5
    sclera = (f'M{_f(cx - 14)},{_f(cy - 5)} C{_f(cx - 13)},{_f(cy - 20)} {_f(cx + 13)},{_f(cy - 20)} {_f(cx + 14)},{_f(cy - 5)} '
              f'C{_f(cx + 15)},{_f(cy + 9)} {_f(cx + 8)},{_f(cy + 16)} {_f(cx)},{_f(cy + 16)} '
              f'C{_f(cx - 8)},{_f(cy + 16)} {_f(cx - 15)},{_f(cy + 9)} {_f(cx - 14)},{_f(cy - 5)} Z')
    iris = (f'M{_f(cx - w)},{_f(cy)} C{_f(cx - w)},{_f(cy - h * 1.3)} {_f(cx + w)},{_f(cy - h * 1.3)} {_f(cx + w)},{_f(cy)} '
            f'C{_f(cx + w)},{_f(cy + h * 1.32)} {_f(cx - w)},{_f(cy + h * 1.32)} {_f(cx - w)},{_f(cy)} Z')
    cid = F.nid('ec')
    o = [f'<clipPath id="{cid}"><path d="{sclera}"/></clipPath>',
         f'<path d="{sclera}" fill="#ffffff"/>',
         f'<g clip-path="url(#{cid})">',
         f'<path d="{sclera}" fill="none" stroke="#c9cdf0" stroke-width="5" transform="translate(0,-3)"/>',
         f'<path d="{iris}" fill="url(#{gid})" stroke="{INK}" stroke-width="1.3"/>',
         # iris ring detail
         f'<ellipse cx="{_f(cx)}" cy="{_f(cy + 1.5)}" rx="{_f(w * .66)}" ry="{_f(h * .78)}" fill="none" stroke="{top}" stroke-width="1" opacity=".55"/>',
         # upper-lid cast shadow
         f'<path d="M{_f(cx - 15)},{_f(cy - 22)} L{_f(cx + 15)},{_f(cy - 22)} L{_f(cx + 15)},{_f(cy - 6)} '
         f'C{_f(cx + 6)},{_f(cy - 11)} {_f(cx - 6)},{_f(cy - 11)} {_f(cx - 15)},{_f(cy - 6)} Z" fill="{INK}" opacity=".42"/>',
         # pupil (soft deep oval)
         f'<ellipse cx="{_f(cx)}" cy="{_f(cy + 1)}" rx="4.6" ry="6.6" fill="{INK}" opacity=".78"/>',
         # light catch: crescent of pale blue at the bottom of the iris
         f'<path d="M{_f(cx - 8.5)},{_f(cy + 7)} C{_f(cx - 4)},{_f(cy + 14)} {_f(cx + 4)},{_f(cy + 14)} {_f(cx + 8.5)},{_f(cy + 7)} '
         f'C{_f(cx + 4)},{_f(cy + 9.5)} {_f(cx - 4)},{_f(cy + 9.5)} {_f(cx - 8.5)},{_f(cy + 7)} Z" fill="#ffffff" opacity=".75"/>',
         # signature water-drop highlight (point up), plus a small round catch-light
         f'<path d="M{_f(cx - 4 * s)},{_f(cy - 13)} C{_f(cx - 1.6 * s)},{_f(cy - 9.5)} {_f(cx - .2 * s)},{_f(cy - 7)} {_f(cx - .2 * s)},{_f(cy - 4.6)} '
         f'C{_f(cx - .2 * s)},{_f(cy - 1.2)} {_f(cx - 7.8 * s)},{_f(cy - 1.2)} {_f(cx - 7.8 * s)},{_f(cy - 4.6)} '
         f'C{_f(cx - 7.8 * s)},{_f(cy - 7)} {_f(cx - 6.4 * s)},{_f(cy - 9.5)} {_f(cx - 4 * s)},{_f(cy - 13)} Z" fill="#ffffff"/>',
         f'<circle cx="{_f(cx + 4.6 * s)}" cy="{_f(cy + 5)}" r="1.9" fill="#ffffff"/>',
         f'<circle cx="{_f(cx + 2 * s)}" cy="{_f(cy - 8)}" r="1" fill="#ffffff" opacity=".9"/>']
    if expr == 'smug':
        # heavy half-lid: skin cover + flat lash line
        o.append(f'<path d="M{_f(cx - 18)},{_f(cy - 24)} L{_f(cx + 18)},{_f(cy - 24)} L{_f(cx + 18)},{_f(cy - 4 - 2 * s)} '
                 f'C{_f(cx + 6)},{_f(cy - 6.5)} {_f(cx - 6)},{_f(cy - 6.5)} {_f(cx - 18)},{_f(cy - 4 + 2 * s)} Z" fill="{SKIN}"/>')
    o.append('</g>')
    if expr == 'smug':
        o.append(f'<path d="M{_f(cx - 15 * s)},{_f(cy - 2 + 2 * s * s)} C{_f(cx - 8 * s)},{_f(cy - 7.5)} {_f(cx + 8 * s)},{_f(cy - 7.5)} {_f(cx + 16 * s)},{_f(cy - 5)} '
                 f'L{_f(cx + 20 * s)},{_f(cy - 8)} L{_f(cx + 16.5 * s)},{_f(cy - 1.5)} C{_f(cx + 8 * s)},{_f(cy - 4.5)} {_f(cx - 8 * s)},{_f(cy - 4)} {_f(cx - 15 * s)},{_f(cy - 2 + 2 * s * s)} Z" '
                 f'fill="{INK}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<path d="M{_f(cx - 10 * s)},{_f(cy - 11)} C{_f(cx - 2 * s)},{_f(cy - 14)} {_f(cx + 8 * s)},{_f(cy - 13)} {_f(cx + 13 * s)},{_f(cy - 9)}" '
                 f'fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" opacity=".7"/>')
    else:
        # thick upper lash with a winged outer corner + crease line
        o.append(f'<path d="M{_f(cx - 15 * s)},{_f(cy - 3)} C{_f(cx - 12 * s)},{_f(cy - 19)} {_f(cx + 10 * s)},{_f(cy - 21.5)} {_f(cx + 16 * s)},{_f(cy - 7)} '
                 f'L{_f(cx + 20.5 * s)},{_f(cy - 9.5)} L{_f(cx + 16.5 * s)},{_f(cy - 2)} '
                 f'C{_f(cx + 9 * s)},{_f(cy - 16)} {_f(cx - 10 * s)},{_f(cy - 15.5)} {_f(cx - 15 * s)},{_f(cy - 3)} Z" '
                 f'fill="{INK}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    # lower lash
    o.append(f'<path d="M{_f(cx - 2 * s)},{_f(cy + 16.2)} Q{_f(cx + 5 * s)},{_f(cy + 16.4)} {_f(cx + 10 * s)},{_f(cy + 12)}" '
             f'fill="none" stroke="#7d64a8" stroke-width="1.5" stroke-linecap="round"/>')
    F.add(''.join(o))


def _face(F, expr):
    face = ('M-47,-178 C-49,-150 -45,-132 -31,-120 C-19,-111 -9,-106 0,-105 C9,-106 19,-111 31,-120 '
            'C45,-132 49,-150 47,-178 C40,-214 -40,-214 -47,-178 Z')
    F.cel(face, SKIN,
          [('M-60,-166 C-40,-158 -24,-162 -10,-170 C6,-160 30,-156 60,-168 L60,-220 L-60,-220 Z', SKIN_SH),
           ('M38,-162 C42,-142 32,-124 12,-111 L60,-100 L60,-162 Z', SKIN_SH)])
    # blush + hatch
    for bx in (-30, 30):
        F.add(f'<ellipse cx="{bx}" cy="-125" rx="9.5" ry="4.6" fill="{BLUSH}" opacity=".5"/>'
              + ''.join(f'<path d="M{bx - 6.5 + i * 4},-122.5 l3,-5" stroke="#e57d9b" stroke-width="1.15" stroke-linecap="round" opacity=".75"/>'
                        for i in range(4)))
    # heterochromia: viewer-left eye deep blue, viewer-right eye pale blue
    _eye(F, -21, -140, -1, '#21307f', '#3f6ad6', '#9cc9ff', expr)
    _eye(F, 21, -140, 1, '#3554b8', '#7eb0f4', '#dbeeff', expr)
    # nose
    F.add(f'<path d="M.6,-126.5 l-1.4,2.2" stroke="#d99a9a" stroke-width="1.5" stroke-linecap="round"/>')
    # mouth
    if expr == 'laugh':
        F.add(f'<path d="M-10,-119 C-9,-106 9,-106 10,-119 C4,-117 -4,-117 -10,-119 Z" fill="{MOUTH}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
              f'<path d="M-6,-111.6 C-3,-108.4 3,-108.4 6,-111.6 C3,-114 -3,-114 -6,-111.6 Z" fill="{TONGUE}"/>'
              f'<path d="M-8.4,-118.4 C-4,-117 4,-117 8.4,-118.4 L7.6,-116.4 C3,-115.4 -3,-115.4 -7.6,-116.4 Z" fill="#ffffff"/>')
    elif expr == 'smug':
        # closed cat-like smirk, one corner hitched up
        F.add(f'<path d="M-7,-117 C-4,-114.6 -1.5,-114.6 0,-116.6 C1.6,-114.4 5,-114.4 8.6,-119.6" fill="none" stroke="{INK}" stroke-width="1.9" '
              f'stroke-linecap="round" stroke-linejoin="round"/>'
              f'<path d="M8.6,-119.6 l1.6,-1.4" stroke="{INK}" stroke-width="1.4" stroke-linecap="round"/>')
    elif expr == 'serene':
        F.add(f'<path d="M-5.5,-118.6 C-3,-113.8 3,-113.8 5.5,-118.6 C2,-117.4 -2,-117.4 -5.5,-118.6 Z" fill="{MOUTH}" stroke="{INK}" '
              f'stroke-width="1.6" stroke-linejoin="round"/>')
    else:  # smile / wink
        F.add(f'<path d="M-7,-119 C-5,-110.4 5,-110.4 7,-119 C2.4,-117.2 -2.4,-117.2 -7,-119 Z" fill="{MOUTH}" stroke="{INK}" stroke-width="1.7" stroke-linejoin="round"/>'
              f'<path d="M-3.4,-114.2 C-1.2,-112.4 1.2,-112.4 3.4,-114.2 C1.2,-115.4 -1.2,-115.4 -3.4,-114.2 Z" fill="{TONGUE}"/>')


def _brows(F, expr):
    if expr == 'smug':
        d = ('M-32,-162 Q-24,-167 -13,-164', 'M13,-167 Q23,-174 33,-170')
    elif expr in ('laugh', 'serene'):
        d = ('M-32,-165 Q-23,-171 -13,-168', 'M13,-168 Q23,-171 32,-165')
    else:
        d = ('M-32,-164 Q-23,-169 -13,-167', 'M13,-167 Q23,-169 32,-164')
    F.add(''.join(f'<path d="{x}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity=".85"/>' for x in d))


# ---------------------------------------------------------------- hair
def _hair_grad(F):
    g = F.nid('hg')
    F.defs.append(f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="0" y1="-236" x2="0" y2="-120">'
                  f'<stop offset="0" stop-color="{HAIR}"/><stop offset=".5" stop-color="{HAIR}"/>'
                  f'<stop offset="1" stop-color="{HAIR_TIP}"/></linearGradient>')
    t = F.nid('tg')
    F.defs.append(f'<linearGradient id="{t}" gradientUnits="userSpaceOnUse" x1="0" y1="-262" x2="0" y2="-205">'
                  f'<stop offset="0" stop-color="#dde3fb"/><stop offset="1" stop-color="{HAIR}"/></linearGradient>')
    F.top = f'url(#{t})'
    b = F.nid('bg')
    F.defs.append(f'<linearGradient id="{b}" gradientUnits="userSpaceOnUse" x1="0" y1="-200" x2="0" y2="-80">'
                  f'<stop offset="0" stop-color="{HAIR_SH}"/><stop offset="1" stop-color="{INNER}"/></linearGradient>')
    return f'url(#{g})', f'url(#{b})'


def _back_hair(F, hg, bg):
    # under-mass behind the head (in shadow, fading to the light-blue under-layer)
    mass = ('M-72,-186 C-80,-240 -34,-262 0,-262 C34,-262 80,-240 72,-186 C76,-160 82,-138 86,-122 '
            'L74,-98 L62,-106 L50,-94 L38,-100 L-38,-100 L-50,-94 L-62,-106 L-74,-98 L-86,-122 '
            'C-82,-138 -76,-160 -72,-186 Z')
    F.cel(mass, bg, sil=True, outline=True)
    # fluffy shoulder-length layers fanning out to pointed, outward-flicked tips
    for m in (-1, 1):
        F.lock([(m * 60, -206), (m * 78, -174), (m * 82, -150), (m * 92, -128), (m * 106, -116)], 30, hg,
               shade=HAIR_SH, side=-m, kind='lock', hl=False, shade_f=.44, shade_t0=.12)
        F.lock([(m * 54, -178), (m * 68, -146), (m * 70, -124), (m * 80, -106), (m * 94, -98)], 26, INNER,
               shade=INNER_SH, side=-m, kind='lock', hl=False, shade_t0=.15)
        F.lock([(m * 46, -150), (m * 54, -124), (m * 60, -104), (m * 72, -92)], 20, INNER,
               shade=INNER_SH, side=-m, kind='lock', hl=False)


def _side_lock_left(F, hg):
    # viewer-left cheek lock: frames the face and curls outward at the jaw
    F.lock([(-54, -214), (-62, -180), (-64, -146), (-66, -122), (-74, -108), (-84, -108)], 26, hg, side=1, kind='flick',
           streak=STREAK, streak_f=(.02, .15), streak_t=(.3, .86), hl=False, shade_t0=.22, sw=1.8)


def _long_lock(F, hg):
    # the signature long side lock: down past the shoulder, ending in a ringlet curl
    pts = [(52, -214), (62, -182), (64, -148), (60, -118), (62, -94), (70, -72), (72, -54), (64, -42), (54, -46), (54, -56), (61, -58)]
    F.lock(pts, 24, hg, side=-1, kind='long', shade_f=.42, streak=STREAK, streak_f=(.06, .16), streak_t=(.14, .78),
           hl=False, sw=1.8)


def _bangs(F, hg):
    # layered, slightly swept bangs: wide pointed locks hanging from the crown (outer first, centre last)
    spec = [
        ([(-50, -224), (-56, -196), (-62, -168), (-67, -158)], 28, 1, None),
        ([(50, -224), (57, -196), (59, -168), (57, -157)], 28, -1, None),
        ([(-30, -230), (-34, -202), (-40, -174), (-46, -162)], 30, 1, None),
        ([(28, -230), (33, -202), (32, -174), (26, -160)], 30, -1, STREAK),
        ([(-8, -232), (-10, -204), (-15, -176), (-22, -163)], 30, 1, None),
        ([(10, -232), (10, -204), (7, -172), (2, -151)], 20, -1, None),
    ]
    for pts, w, side, st in spec:
        F.lock(pts, w, hg, side=side, kind='lock', streak=st, streak_f=(.04, .17), streak_t=(.12, .8), shade_t0=.34,
               shade_f=.36, hl=False, sw=1.7)
    # crown dome covering the lock roots: only its upper arc is inked
    dome = ('M-72,-188 C-80,-240 -34,-262 0,-262 C34,-262 80,-240 72,-188 '
            'C62,-202 46,-210 28,-214 C14,-218 -14,-218 -28,-214 C-46,-210 -62,-202 -72,-188 Z')
    # two little fly-away strands on the crown for fluff
    F.lock([(40, -248), (50, -258), (60, -260), (64, -256)], 8, hg, shade=None, hl=False, sw=1.5)
    ring = ('M-62,-214 C-50,-232 -22,-242 4,-242 C28,-242 48,-234 60,-220 '
            'C55,-222 50,-223 45,-223 L43,-213 C40,-218 36,-222 30,-226 '
            'C20,-229 11,-230 3,-229 L0,-217 C-2,-222 -6,-226 -10,-228 '
            'C-22,-227 -34,-223 -43,-218 L-47,-207 C-48,-211 -51,-214 -55,-216 Z')
    ring_sh = ('M-66,-206 C-54,-226 -24,-236 4,-236 C30,-236 52,-228 64,-212 L64,-204 L-66,-198 Z')
    F.cel(dome, F.top,
          [('M34,-266 C64,-252 82,-228 74,-188 L96,-188 L96,-266 Z', HAIR_SH),
           ('M-80,-200 C-70,-190 -64,-196 -58,-204 L-80,-180 Z', HAIR_SH)],
          highlights=[(ring, HAIR_SH2)],
          extra=f'<path d="{ring}" fill="#ffffff" transform="translate(0,2.6)"/>'
                f'<path d="M14,-260 C20,-246 22,-232 22,-216" fill="none" stroke="{STREAK}" stroke-width="5.5" stroke-linecap="round"/>'
                + ''.join(f'<path d="{d}" fill="none" stroke="{INK2}" stroke-width="1.1" stroke-linecap="round" opacity=".5"/>' for d in (
                    'M-34,-252 C-46,-240 -52,-228 -55,-214', 'M40,-252 C50,-242 56,-230 58,-214', 'M-6,-260 C-9,-250 -11,-240 -11,-228')),
          outline=False)
    F.add(f'<path d="M-72,-188 C-80,-240 -34,-262 0,-262 C34,-262 80,-240 72,-188" fill="none" stroke="{INK}" '
          f'stroke-width="{SW}" stroke-linecap="round"/>')


# ---------------------------------------------------------------- hat
def _hat(F, tf, bow_side=1):
    F.push(tf)
    brim = 'M-31,1 C-31,-7 31,-7 31,1 C31,8.6 -31,8.6 -31,1 Z'
    crown = 'M-17,1 L-19.5,-35 C-19.5,-39.5 19.5,-39.5 19.5,-35 L17,1 C10,5 -10,5 -17,1 Z'
    F.cel(brim, NAVY, [('M-36,1 C-10,8 10,8 36,1 L36,12 L-36,12 Z', NAVY_SH)],
          highlights=[('M-26,-1.6 C-14,-5 14,-5 26,-1.6 C14,-3.4 -14,-3.4 -26,-1.6 Z', NAVY_HI)])
    F.cel(crown, NAVY, [('M7,-42 L26,-42 L26,8 L7,8 Z', NAVY_SH)],
          highlights=[('M-14.5,-32 L-10.5,-32 L-9.6,-15 L-13.6,-15 Z', NAVY_HI),
                      ('M-19.5,-37.4 C-19.5,-41 19.5,-41 19.5,-37.4 C10,-35 -10,-35 -19.5,-37.4 Z', NAVY_HI)])
    # light-blue ribbon band + bow with two trailing tails
    F.cel('M-18.2,-12 L18.2,-12 L17.4,-2.4 C10,1 -10,1 -17.4,-2.4 Z', LB, [('M7,-14 L22,-14 L22,3 L7,3 Z', LB_SH)],
          highlights=[('M-16,-10.4 L4,-10.4 L4,-9 L-16,-9 Z', LB_HI)], sw=1.8)
    b = bow_side
    F.cel(f'M{12 * b},-7 C{18 * b},-17 {29 * b},-15 {27 * b},-7 C{29 * b},0 {18 * b},2 {12 * b},-7 Z', LB,
          [(f'M{12 * b},-7 L{32 * b},-7 L{32 * b},4 L{12 * b},4 Z', LB_SH)], sw=1.7)
    F.cel(f'M{11 * b},-7 C{9 * b},0 {11 * b},9 {16 * b},16 L{19 * b},11 L{22 * b},15 C{18 * b},8 {15 * b},0 {13 * b},-7 Z', LB,
          [(f'M{14 * b},-6 L{24 * b},-6 L{24 * b},18 L{14 * b},18 Z', LB_SH)], sw=1.6)
    F.cel(f'M{8 * b},-7 C{5 * b},-17 {-2 * b},-17 {0 * b},-8 C{-2 * b},0 {5 * b},1 {8 * b},-7 Z', LB,
          [(f'M{-4 * b},-6 L{10 * b},-6 L{10 * b},4 L{-4 * b},4 Z', LB_SH)], sw=1.7)
    # water-drop gem knot
    F.add(f'<path d="M{10 * b},-13.4 C{13 * b},-10 {14 * b},-8 {14 * b},-6.2 C{14 * b},-3 {6 * b},-3 {6 * b},-6.2 C{6 * b},-8 {7 * b},-10 {10 * b},-13.4 Z" '
          f'fill="{LB_HI}" stroke="{INK}" stroke-width="1.4"/>'
          f'<path d="M{8.4 * b},-8.6 C{8.4 * b},-9.6 {9 * b},-10.4 {9.6 * b},-11" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round"/>')
    F.pop()


# ---------------------------------------------------------------- body
def _tails(F, flare=0):
    for m in (-1, 1):
        f = flare
        t = (f'M{m * 6},-60 C{m * (22 + f)},-58 {m * (37 + f)},-44 {m * (48 + f * 1.4)},-14 L{m * (38 + f)},-21 L{m * (31 + f * .6)},-10 '
             f'C{m * (27 + f * .4)},-27 {m * 18},-40 {m * 6},-46 Z')
        F.cel(t, NAVY,
              [(f'M{m * 4},-50 C{m * 18},-42 {m * 27},-30 {m * 32},-10 L{m * 4},-10 Z', NAVY_SH)],
              highlights=[(f'M{m * 14},-58 C{m * 27},-52 {m * 35},-40 {m * (41 + f)},-24 L{m * (44 + f)},-25 '
                           f'C{m * 37},-42 {m * 29},-54 {m * 16},-60 Z', NAVY_HI if m < 0 else NAVY)],
              extra=f'<path d="M{m * (48 + f * 1.4)},-14 L{m * (38 + f)},-21 L{m * (31 + f * .6)},-10" fill="none" stroke="{LB}" '
                    f'stroke-width="3.4" stroke-linejoin="round" transform="translate(0,-2.6)"/>')


def _legs(F, pose):
    if pose == 'bow':
        # curtsy: white-sock leg crossed behind, navy leg in front with a soft knee bend
        F.tube('M9,-42 Q12,-24 -2,-9', WHITE, WHITE_SH, 10)
        F.add(f'<path d="M4.5,-27 L16,-25" stroke="{LB_SH}" stroke-width="3"/>')
        _boot(F, -2, -1, tilt=-12, dy=-2.5)
        F.tube('M-10,-42 Q-16,-26 -13,-10', NAVY, NAVY_SH, 10)
        F.add(f'<path d="M-17,-31 L-9,-30" stroke="{NAVY_HI}" stroke-width="1.6"/>')
        _boot(F, -13, -1)
        return
    F.tube('M10,-42 Q11,-24 11,-10', WHITE, WHITE_SH, 10)
    F.add(f'<path d="M5,-26 L17,-26" stroke="{LB_SH}" stroke-width="3"/>')
    F.tube('M-10,-42 Q-11,-24 -11,-10', NAVY, NAVY_SH, 10)
    F.add(f'<path d="M-15,-30 L-6,-30" stroke="{NAVY_HI}" stroke-width="1.6" opacity=".9"/>')
    _boot(F, -11, -1)
    _boot(F, 11, 1)


def _boot(F, bx, mir, tilt=0, dy=0):
    F.push(f'translate({bx},{dy}) rotate({tilt},0,-8)')
    if mir > 0:
        d = 'M-6,-17 L6,-17 L6,-6 C10,-5 11,-2 10,1 L-9,1 C-10,-3 -8,-6 -6,-6 Z'
    else:
        d = 'M-6,-17 L6,-17 L6,-6 C8,-6 10,-3 9,1 L-10,1 C-11,-2 -10,-5 -6,-6 Z'
    F.cel(d, NAVY, [('M-12,-4 L14,-4 L14,4 L-12,4 Z', NAVY_SH)],
          highlights=[('M-4,-15 L-2,-15 L-2,-8 L-4,-8 Z', NAVY_HI)])
    F.add(f'<path d="M-6,-15 L6,-15" stroke="{GOLD}" stroke-width="2"/>')
    F.pop()


def _torso(F):
    shorts = 'M-20,-54 L20,-54 L22,-38 C14,-36 6,-37 1,-40 C-4,-37 -14,-36 -22,-38 Z'
    F.cel(shorts, NAVY, [('M-30,-46 L30,-46 L30,-30 L-30,-30 Z', NAVY_SH)])
    coat = ('M-12,-100 C-22,-99 -27,-95 -27,-88 C-26,-76 -22,-64 -22,-52 C-14,-50 14,-50 22,-52 '
            'C22,-64 26,-76 27,-88 C27,-95 22,-99 12,-100 Z')
    F.cel(coat, NAVY, [('M8,-100 C20,-90 22,-70 30,-52 L40,-52 L40,-104 Z', NAVY_SH)],
          highlights=[('M-24,-92 C-22,-84 -21,-72 -20,-62 L-17,-62 C-18,-74 -19,-84 -20,-93 Z', NAVY_HI)])
    F.cel('M-11,-99 L11,-99 L9,-60 L0,-53 L-9,-60 Z', WHITE, [('M2,-100 L14,-100 L14,-50 L2,-50 Z', WHITE_SH)], sw=1.8, sil=False)
    F.add(''.join(f'<circle cx="0" cy="{by}" r="1.9" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>' for by in (-72, -64)))
    F.add(f'<path d="M-11,-99 L-16,-84 L-9,-60" fill="none" stroke="{LB}" stroke-width="2.6" stroke-linejoin="round"/>'
          f'<path d="M11,-99 L16,-84 L9,-60" fill="none" stroke="{LB}" stroke-width="2.6" stroke-linejoin="round"/>'
          f'<path d="M-22,-53 C-14,-51 14,-51 22,-53" fill="none" stroke="{GOLD}" stroke-width="2"/>')
    jabot = ('M-8,-100 L8,-100 C11,-96 9,-92 6,-91 C10,-88 9,-83 5,-82 C8,-79 6,-74 0,-73 '
             'C-6,-74 -8,-79 -5,-82 C-9,-83 -10,-88 -6,-91 C-9,-92 -11,-96 -8,-100 Z')
    F.cel(jabot, LB, [('M0,-102 L14,-102 L14,-70 L0,-70 Z', LB_SH)],
          highlights=[('M-6,-96 C-4,-93 -4,-90 -6,-88 L-7,-89 C-6,-91 -6,-93 -7,-95 Z', LB_HI)], sw=1.8, sil=False)


def _collar(F):
    F.add(f'<path d="M-6,-109 L6,-109 L6,-100 L-6,-100 Z" fill="{SKIN_SH}" stroke="{INK}" stroke-width="1.6"/>'
          f'<path d="M-7,-103 L-14,-97 L-6,-96 Z M7,-103 L14,-97 L6,-96 Z" fill="{WHITE}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
          f'<path d="M0,-101 C3,-98 4,-96 4,-94 C4,-91 -4,-91 -4,-94 C-4,-96 -3,-98 0,-101 Z" fill="{LB_HI}" stroke="{INK}" stroke-width="1.4"/>'
          f'<circle cx="-1.3" cy="-94.5" r="1" fill="#ffffff"/>')


def _puffs(F):
    for px in (-1, 1):
        d = f'M{px * 12},-101 C{px * 24},-104 {px * 31},-98 {px * 30},-88 C{px * 25},-86 {px * 18},-88 {px * 14},-92 Z'
        F.cel(d, NAVY, [(f'M{px * 10},-92 L{px * 34},-92 L{px * 34},-80 L{px * 10},-80 Z', NAVY_SH)],
              highlights=[(f'M{px * 18},-101 C{px * 24},-101 {px * 27},-98 {px * 28},-95 L{px * 24},-97 Z', NAVY_HI)])


def _arm(F, sh, ctrl, wr, kind, flipy=False, extra_rot=0, hand_scale=1.0):
    F.tube(f'M{_pt(sh)} Q{_pt(ctrl)} {_pt(wr)}', NAVY, NAVY_SH, 11)
    ang = math.degrees(math.atan2(wr[1] - ctrl[1], wr[0] - ctrl[0])) + extra_rot
    _hand(F, wr[0], wr[1], ang, kind, flipy=flipy, scale=hand_scale)


def _droplet(F, cx, cy, r, op=1):
    d = (f'M{_f(cx)},{_f(cy - r * 1.7)} C{_f(cx + r * .55)},{_f(cy - r * .8)} {_f(cx + r)},{_f(cy - r * .3)} {_f(cx + r)},{_f(cy + r * .2)} '
         f'C{_f(cx + r)},{_f(cy + r * .8)} {_f(cx + r * .5)},{_f(cy + r)} {_f(cx)},{_f(cy + r)} C{_f(cx - r * .5)},{_f(cy + r)} {_f(cx - r)},{_f(cy + r * .8)} {_f(cx - r)},{_f(cy + r * .2)} '
         f'C{_f(cx - r)},{_f(cy - r * .3)} {_f(cx - r * .55)},{_f(cy - r * .8)} {_f(cx)},{_f(cy - r * 1.7)} Z')
    F.cel(d, LB, [(f'M{_f(cx - r)},{_f(cy + r * .1)} C{_f(cx)},{_f(cy + r * .5)} {_f(cx + r * .4)},{_f(cy)} {_f(cx + r * 1.2)},{_f(cy - r * .6)} '
                   f'L{_f(cx + r * 1.2)},{_f(cy + r * 1.2)} L{_f(cx - r)},{_f(cy + r * 1.2)} Z', LB_SH)],
          sw=max(1.2, r * .17), sil=False,
          extra=f'<path d="M{_f(cx - r * .5)},{_f(cy - r * .1)} C{_f(cx - r * .5)},{_f(cy - r * .6)} {_f(cx - r * .25)},{_f(cy - r * .95)} {_f(cx - r * .05)},{_f(cy - r * 1.15)}" '
                f'fill="none" stroke="#ffffff" stroke-width="{_f(r * .28)}" stroke-linecap="round"/>'
                f'<circle cx="{_f(cx + r * .35)}" cy="{_f(cy + r * .45)}" r="{_f(r * .15)}" fill="#ffffff"/>')


def _sparkle4(cx, cy, r, col='#ffffff', op=1):
    k = r * .2
    return (f'<path d="M{_f(cx)},{_f(cy - r)} Q{_f(cx + k)},{_f(cy - k)} {_f(cx + r)},{_f(cy)} Q{_f(cx + k)},{_f(cy + k)} {_f(cx)},{_f(cy + r)} '
            f'Q{_f(cx - k)},{_f(cy + k)} {_f(cx - r)},{_f(cy)} Q{_f(cx - k)},{_f(cy - k)} {_f(cx)},{_f(cy - r)} Z" fill="{col}" opacity="{op}"/>')


# ---------------------------------------------------------------- main entry
def furina(x, y, scale=1, uid='fu', pose='present', expr=None, flip=False, **_ignored):
    if pose not in BBOX_BY_POSE:
        pose = 'present'
    if expr is None:
        expr = DEFAULT_EXPR[pose]
    sx = -scale if flip else scale
    F = _Fig(uid)
    hg, bg = _hair_grad(F)
    SH_R, SH_L = (-22, -93), (22, -93)     # viewer-left / viewer-right shoulders

    def hip(side):
        m = side
        _arm(F, (m * 22, -92), (m * 43, -79), (m * 27, -62), 'fist', flipy=(m > 0))

    _tails(F, flare=6 if pose == 'bow' else 0)
    _legs(F, pose)
    up = None
    if pose == 'bow':
        up = 'translate(0,5) rotate(-5,0,-52)'
        F.push(up)
    if pose == 'bow':
        F.push('rotate(-7,0,-108)')
    _back_hair(F, hg, bg)
    if pose == 'bow':
        F.pop()
    _torso(F)
    front = []          # callables drawn after the head
    if pose == 'present':
        _arm(F, SH_R, (-44, -82), (-60, -94), 'open', flipy=True, extra_rot=-22)
        hip(1)
        front.append(lambda: _droplet(F, -76, -122, 7.5))
    elif pose == 'judge':
        hip(1)
        front.append(lambda: _arm(F, SH_R, (-46, -104), (-70, -130), 'point', flipy=True))
        # dramatic accent lines off the fingertip
        front.append(lambda: F.add(''.join(
            f'<path d="M{_f(-83 + 7 * math.cos(a))},{_f(-154 + 7 * math.sin(a))} L{_f(-83 + 14 * math.cos(a))},{_f(-154 + 14 * math.sin(a))}" '
            f'stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>' for a in (math.radians(-165), math.radians(-125), math.radians(-85)))))
    elif pose == 'point':
        hip(1)
        front.append(lambda: _arm(F, SH_R, (-44, -92), (-62, -104), 'point', flipy=True))
    elif pose == 'laugh':
        hip(-1)
        front.append(lambda: _arm(F, SH_L, (46, -96), (32, -114), 'flat', flipy=False, extra_rot=0))
    elif pose == 'bow':
        # viewer-left hand sweeps the hat out low; viewer-right arm flourishes outward
        _arm(F, SH_R, (-42, -78), (-58, -70), 'grip', flipy=True)
        front.append(lambda: _arm(F, SH_L, (46, -90), (70, -100), 'open', flipy=False))
    _puffs(F)
    _collar(F)
    if pose == 'bow':
        F.push('rotate(-7,0,-108)')
    _face(F, expr)
    _side_lock_left(F, hg)
    _long_lock(F, hg)
    _bangs(F, hg)
    _brows(F, expr)
    if pose != 'bow':
        _hat(F, 'translate(-34,-242) rotate(-22)')
    else:
        F.pop()
    for fn in front:
        fn()
    if up:
        # the hat, held by its brim (drawn last so the gripping hand's fingers read over it)
        _hat(F, 'translate(-71,-56) rotate(-112) scale(.95)', bow_side=-1)
        _hand(F, -58, -70, 180 + 23, 'grip', flipy=True)
        F.pop()
    return f'<g transform="translate({_f(x)},{_f(y)}) scale({sx},{scale})">' + F.render() + '</g>'


def bbox(pose='present', scale=1, flip=False):
    """Bounding box (min_x, min_y, max_x, max_y) relative to the anchor for a pose/scale/flip."""
    x0, y0, x1, y1 = BBOX_BY_POSE.get(pose, BBOX_BY_POSE['present'])
    if flip:
        x0, x1 = -x1, -x0
    return (x0 * scale, y0 * scale, x1 * scale, y1 * scale)


# ======================================================================== showcase (debug only)
def _cloud(cx, cy, s, cid):
    """Anime cumulus: rounded top, flat shaded underside, hard-edged mid shade."""
    bumps = [(-70, 0, 22), (-44, -16, 30), (-8, -36, 40), (32, -24, 34), (64, -6, 24), (86, 4, 14)]
    top = ''.join(f'<circle cx="{_f(cx + bx * s)}" cy="{_f(cy + by * s)}" r="{_f(r * s)}"/>' for bx, by, r in bumps)
    flat = f'<rect x="{_f(cx - 92 * s)}" y="{_f(cy - 6 * s)}" width="{_f(192 * s)}" height="{_f(16 * s)}" rx="{_f(8 * s)}"/>'
    return (f'<clipPath id="{cid}">{top}{flat}</clipPath><g clip-path="url(#{cid})">'
            f'<rect x="{_f(cx - 100 * s)}" y="{_f(cy - 80 * s)}" width="{_f(200 * s)}" height="{_f(100 * s)}" fill="#d6d3f6"/>'
            + ''.join(f'<circle cx="{_f(cx + (bx - 6) * s)}" cy="{_f(cy + (by - 9) * s)}" r="{_f(r * s)}" fill="#efeefe"/>' for bx, by, r in bumps)
            + ''.join(f'<circle cx="{_f(cx + (bx - 12) * s)}" cy="{_f(cy + (by - 17) * s)}" r="{_f(r * s * .96)}" fill="#ffffff"/>' for bx, by, r in bumps)
            + '</g>')


def showcase():
    W, H = 1500, 640
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Chibi fan art of Furina in five poses">',
         '<style>.fs-tw{animation:fs-tw 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}'
         '.fs-tw2{animation:fs-tw 3.2s ease-in-out -1.6s infinite;transform-box:fill-box;transform-origin:center}'
         '@keyframes fs-tw{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.6)}}'
         '@media (prefers-reduced-motion: reduce){.fs-tw,.fs-tw2{animation:none}}</style>',
         '<defs><linearGradient id="fs-sky" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#a7b3ef"/><stop offset=".5" stop-color="#c9cff7"/><stop offset=".8" stop-color="#ecdcf3"/>'
         '<stop offset="1" stop-color="#fbe4ee"/></linearGradient>'
         '<linearGradient id="fs-sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c6cff6"/><stop offset="1" stop-color="#a3b1e8"/></linearGradient>'
         '<radialGradient id="fs-glow" cx=".8" cy=".02" r=".6"><stop offset="0" stop-color="#fffaf0" stop-opacity=".95"/>'
         '<stop offset=".4" stop-color="#fff2f6" stop-opacity=".3"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="fs-frame"><rect width="{W}" height="{H}" rx="28"/></clipPath></defs>',
         '<g clip-path="url(#fs-frame)">',
         f'<rect width="{W}" height="{H}" fill="url(#fs-sky)"/><rect width="{W}" height="{H}" fill="url(#fs-glow)"/>']
    for a0, a1, op in ((100, 106, .3), (112, 120, .22), (126, 131, .28), (138, 146, .18)):
        r = 1400
        p0 = (1200 + r * math.cos(math.radians(a0)), r * math.sin(math.radians(a0)))
        p1 = (1200 + r * math.cos(math.radians(a1)), r * math.sin(math.radians(a1)))
        s.append(f'<path d="M1200,0 L{p0[0]:.0f},{p0[1]:.0f} L{p1[0]:.0f},{p1[1]:.0f} Z" fill="#ffffff" opacity="{op}"/>')
    s.append(_cloud(160, 120, 1.1, 'fs-c1') + _cloud(760, 80, .8, 'fs-c2') + _cloud(1380, 200, 1.2, 'fs-c3'))
    s.append(f'<rect x="0" y="470" width="{W}" height="{H - 470}" fill="url(#fs-sea)"/>'
             f'<path d="M0,470 L{W},470" stroke="#ffffff" stroke-width="2.5" opacity=".9"/>')
    poses = [('present', 'smile', 150, False), ('judge', 'smug', 450, False), ('bow', None, 750, False),
             ('point', 'wink', 1050, True), ('laugh', 'laugh', 1340, False)]
    sc = 1.55
    gy = 600
    for i, (p, e, cx, fl) in enumerate(poses):
        s.append(f'<ellipse cx="{cx}" cy="{gy + 2}" rx="{70 * sc / 1.4:.0f}" ry="{11 * sc / 1.4:.0f}" fill="none" stroke="#ffffff" stroke-width="2" opacity=".8"/>')
        s.append(f'<ellipse cx="{cx}" cy="{gy + 2}" rx="{48 * sc / 1.4:.0f}" ry="{6 * sc / 1.4:.0f}" fill="#7f6cc0" opacity=".2"/>')
        s.append(furina(cx, gy, sc, uid=f'fs{i}', pose=p, expr=e, flip=fl))
        s.append(f'<text x="{cx}" y="{H - 10}" text-anchor="middle" font-size="16" fill="#4a4590" '
                 f'font-family="\'Hiragino Sans\',\'PingFang SC\',\'Segoe UI\',system-ui,-apple-system,\'Noto Sans CJK SC\',sans-serif">'
                 f'{p} / {e or DEFAULT_EXPR[p]}</text>')
    for i, (cx, cy, r) in enumerate(((300, 140, 10), (620, 210, 8), (900, 160, 9), (1210, 120, 7), (60, 300, 6), (1460, 330, 7))):
        s.append(_sparkle4(cx, cy, r).replace('<path ', f'<path class="fs-tw{"2" if i % 2 else ""}" ', 1))
    s.append('</g></svg>')
    return ''.join(s)


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, 'furina.svg')
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(showcase())
    return p


if __name__ == '__main__':
    print('wrote', build('/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/scratchpad/v10final/chars'))
