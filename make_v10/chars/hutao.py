"""Chibi Hu Tao (non-commercial fan art, our own drawing) as standalone SVG fragments.

    hutao(x, y, scale=1, uid='ht', pose='peace', boo=True, flip=False, boo_pose=None) -> str
        (x, y) = ground point between her feet.  pose: 'peace' (wink + V sign) or 'grin'
        (both eyes open, fist on hip).  boo=True adds Boo Tao (drawn by chars/bootao.py)
        floating at her side; boo_pose overrides his pose ('float' | 'wave' | 'lantern').
        flip=True mirrors x.  Bounding box at scale 1 (measured): x [-132, 100] with Boo Tao,
        x [-109, 100] without, y [-250, 8]; multiply by scale, use [-x1, -x0] when flipped.
    boo_tao(x, y, scale=1, uid='bt', standalone_defs=True, pose='float', shadow=False) -> str
        thin wrapper around chars/bootao.bootao, sized like the old built-in ghost
        ((x, y) = head centre, head radius ~24*scale).
    BBOX[(pose, boo)] = (x0, y0, x1, y1) at scale 1 relative to the anchor; Boo Tao's soft
        white glow can reach ~10 units past x0 (invisible on light backgrounds).

Every fragment carries its own <defs>/<style>; ids and classes are prefixed by uid, so give
each instance a distinct uid.  CSS animation stops under prefers-reduced-motion.
Run as a script to write a 600x600 showcase into the scratchpad (never into the repo).
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWCASE = ("/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/"
            "scratchpad/v10final/chars/hutao.svg")

# Bounding boxes at scale 1, relative to the anchor (x0, y0, x1, y1); measured from renders.
BBOX = {
    ("peace", True): (-132, -250, 100, 8),
    ("peace", False): (-109, -250, 100, 8),
    ("grin", True): (-132, -250, 100, 8),
    ("grin", False): (-109, -250, 100, 8),
}

# ---- palette (warm plum-browns, no green) ----
INK = "#3a1d2a"        # plum-brown line ink (never black)
HAIR = "#4f2b35"
HAIR_SH = "#381d28"
HAIR_HI = "#7d4852"
HAIR_TIP = "#8e3a48"
SKIN = "#fff0e6"
SKIN_SH = "#f5c9bf"
BLUSH = "#ff9fae"
COAT = "#5a323d"
COAT_SH = "#40222f"
COAT_DEEP = "#311a26"
COAT_HI = "#7e4c57"
COAT_GLINT = "#a06a72"
COAT_LIT = "#683b47"
RIM = "#c9b8f0"        # lavender sky rim light
RED = "#c8364a"
RED_SH = "#982638"
RED_HI = "#ea6274"
GOLD = "#f0c46a"
GOLD_SH = "#c9924a"
WHITE = "#fffaf6"
PLUM_PINK = "#ffd0da"

LIFT = 14   # upper body sits LIFT units lower than the old long-legged version (shorter legs)

_bt_mod = None


def _bootao_mod():
    """Load chars/bootao.py whether we are imported as a package, by path, or run as a script."""
    global _bt_mod
    if _bt_mod is None:
        try:
            from . import bootao as m          # package import (make_v10.chars.hutao)
        except Exception:
            spec = importlib.util.spec_from_file_location("_v10_chars_bootao", os.path.join(HERE, "bootao.py"))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        _bt_mod = m
    return _bt_mod


BOO_K = 0.44   # bootao.py draws a head of radius 54; the old built-in ghost was ~24 at scale 1


def boo_tao(x, y, scale=1, uid="bt", standalone_defs=True, pose="float", shadow=False, **kw):
    """Boo Tao drawn by chars/bootao.py, sized like the old built-in ghost: (x, y) = head centre,
    head radius ~24*scale.  standalone_defs is accepted for backward compatibility (bootao.py
    always emits its own defs)."""
    return _bootao_mod().bootao(x, y, scale=scale * BOO_K, pose=pose, uid=uid, shadow=shadow, **kw)


# ------------------------------------------------------------------ geometry helpers
def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-9 else str(int(round(v)))


def _smooth(pts, closed=True):
    """Catmull-Rom spline through pts -> SVG path data (cubic Beziers)."""
    n = len(pts)
    d = [f"M{_f(pts[0][0])},{_f(pts[0][1])}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_f(c1[0])},{_f(c1[1])} {_f(c2[0])},{_f(c2[1])} {_f(p2[0])},{_f(p2[1])}")
    if closed:
        d.append("Z")
    return " ".join(d)


def _bez(segs, t):
    """Point on a chain of cubic segments [(p0,p1,p2,p3), ...] at global t in [0,1]."""
    k = min(int(t * len(segs)), len(segs) - 1)
    u = t * len(segs) - k
    p0, p1, p2, p3 = segs[k]
    a, b, c, e = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1])


def _lerp_tab(tab, t):
    for (t0, v0), (t1, v1) in zip(tab, tab[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0
            u = u * u * (3 - 2 * u)
            return v0 + (v1 - v0) * u
    return tab[-1][1]


class _Ribbon:
    """A tapered hair/cloth strip around a Bezier centreline. side a in [-1, 1] across the width
    (a=+1 is the left of the direction of travel)."""

    def __init__(self, segs, widths):
        self.segs, self.widths = segs, widths

    def frame(self, t):
        p = _bez(self.segs, t)
        q = _bez(self.segs, min(1, t + 1e-3))
        r = _bez(self.segs, max(0, t - 1e-3))
        tx, ty = q[0] - r[0], q[1] - r[1]
        L = math.hypot(tx, ty) or 1
        return p, (ty / L, -tx / L), _lerp_tab(self.widths, t)   # normal = tangent rotated -90deg

    def pt(self, t, a):
        p, n, w = self.frame(t)
        return (p[0] + n[0] * w * a, p[1] + n[1] * w * a)

    def band(self, t0, t1, a0, a1, n=18):
        """closed outline of the region t in [t0,t1], side in [a0(t), a1(t)] (numbers or callables)."""
        f0 = a0 if callable(a0) else (lambda t, v=a0: v)
        f1 = a1 if callable(a1) else (lambda t, v=a1: v)
        ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
        return _smooth([self.pt(t, f0(t)) for t in ts] + [self.pt(t, f1(t)) for t in reversed(ts)])

    def line(self, t0, t1, a, n=12):
        return _smooth([self.pt(t0 + (t1 - t0) * i / n, a) for i in range(n + 1)], closed=False)


# ------------------------------------------------------------------ defs
def _defs(uid):
    return f"""
<defs>
 <linearGradient id="{uid}-iris" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#5a1428"/><stop offset=".45" stop-color="#b02a40"/>
  <stop offset=".8" stop-color="#e8566a"/><stop offset="1" stop-color="#ffb0a8"/>
 </linearGradient>
 <linearGradient id="{uid}-hair" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{HAIR}"/><stop offset=".62" stop-color="{HAIR}"/>
  <stop offset="1" stop-color="{HAIR_TIP}"/>
 </linearGradient>
 <linearGradient id="{uid}-coat" x1="0" y1="0" x2=".35" y2="1">
  <stop offset="0" stop-color="{COAT_HI}"/><stop offset=".38" stop-color="{COAT}"/>
  <stop offset="1" stop-color="{COAT}"/>
 </linearGradient>
 <clipPath id="{uid}-torso"><path d="{_TORSO}"/></clipPath>
 <clipPath id="{uid}-flapL"><path d="{_FLAP_L}"/></clipPath>
 <clipPath id="{uid}-flapR"><path d="{_FLAP_R}"/></clipPath>
 <clipPath id="{uid}-sleeve"><path d="{_SLEEVE}"/></clipPath>
</defs>
<style>
 .{uid}-tw {{ animation: {uid}-tw 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
 .{uid}-sway {{ animation: {uid}-sway 4.6s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 0%; }}
 .{uid}-sway2 {{ animation: {uid}-sway 5.2s ease-in-out -1.7s infinite; transform-box: fill-box; transform-origin: 50% 0%; }}
 @keyframes {uid}-tw {{ 0%,100% {{ opacity: 1; transform: scale(1) }} 50% {{ opacity: .35; transform: scale(.6) }} }}
 @keyframes {uid}-sway {{ 0%,100% {{ transform: rotate(0deg) }} 50% {{ transform: rotate(1.6deg) }} }}
 @media (prefers-reduced-motion: reduce) {{ .{uid}-tw, .{uid}-sway, .{uid}-sway2 {{ animation: none; }} }}
</style>"""


# torso / coat-tail / hanging-sleeve silhouettes (upper-body frame)
_TORSO = ("M-24,-108 C-30,-92 -34,-70 -36,-50 C-24,-46 24,-46 36,-50 C34,-70 30,-92 24,-108Z")
_FLAP_L = ("M-28,-98 C-42,-80 -56,-54 -64,-26 C-60,-29 -56,-30 -52,-28 C-48,-33 -44,-34 -40,-30 "
           "C-36,-33 -32,-32 -28,-28 C-27,-46 -23,-64 -16,-82Z")
_FLAP_R = ("M28,-98 C42,-80 54,-56 60,-30 C56,-33 52,-33 48,-30 C44,-34 40,-34 36,-30 "
           "C33,-33 30,-32 28,-30 C27,-46 23,-64 16,-82Z")
_SLEEVE = ("M-20,-107 C-30,-105 -36,-97 -38,-87 C-40,-79 -43,-71 -47,-63 "
           "C-42,-60 -34,-59 -29,-61 C-29,-70 -27,-80 -24,-89 C-22,-96 -20,-101 -17,-104Z")


# ------------------------------------------------------------------ small parts
def _blossom(cx, cy, r, rot=0, fill=RED, centre=GOLD, shade=RED_SH):
    """Five-petal plum blossom with a cel shadow on the lower petals."""
    petals = "".join(f'<ellipse cx="0" cy="{-r*0.55:.2f}" rx="{r*0.42:.2f}" ry="{r*0.52:.2f}" transform="rotate({rot + i*72})"/>'
                     for i in range(5))
    shade_p = "".join(f'<ellipse cx="0" cy="{-r*0.62:.2f}" rx="{r*0.30:.2f}" ry="{r*0.36:.2f}" transform="rotate({rot + i*72})"/>'
                      for i in (2, 3))
    hi = f'<ellipse cx="{-r*.18:.2f}" cy="{-r*.62:.2f}" rx="{r*.12:.2f}" ry="{r*.2:.2f}" transform="rotate({rot-20})" fill="{PLUM_PINK}"/>'
    return (f'<g transform="translate({cx},{cy})">'
            f'<g fill="{fill}" stroke="{INK}" stroke-width="{max(.6, r*0.09):.2f}" stroke-linejoin="round">{petals}</g>'
            f'<g fill="{shade}">{shade_p}</g>{hi}'
            f'<circle r="{r*0.26:.2f}" fill="{centre}"/>'
            f'<circle r="{r*0.11:.2f}" fill="{RED_SH}"/></g>')


def _flower_pupil(cx, cy, r):
    pts = "".join(f'<circle cx="0" cy="{-r*0.62:.2f}" r="{r*0.48:.2f}" transform="rotate({i*72})"/>' for i in range(5))
    return f'<g transform="translate({cx},{cy})" fill="#3d0a1a">{pts}<circle r="{r*0.6:.2f}"/></g>'


def _eye_open(cx, cy, U, mirror=False):
    s = -1 if mirror else 1
    ew = (f'M{cx-13*s},{cy-6} C{cx-12*s},{cy-17} {cx+12*s},{cy-18} {cx+14*s},{cy-7} '
          f'C{cx+15*s},{cy+8} {cx+8*s},{cy+15} {cx},{cy+15} C{cx-9*s},{cy+15} {cx-14*s},{cy+6} {cx-13*s},{cy-6}Z')
    out = [f'<path d="{ew}" fill="#ffffff"/>',
           f'<ellipse cx="{cx+1*s}" cy="{cy+1}" rx="11" ry="14.5" fill="url(#{U}-iris)"/>',
           f'<path d="M{cx-12*s},{cy-9} C{cx-6*s},{cy-16} {cx+8*s},{cy-16} {cx+13*s},{cy-9} '
           f'C{cx+7*s},{cy-6} {cx-6*s},{cy-5} {cx-12*s},{cy-9}Z" fill="#4a1022" opacity=".55"/>',
           _flower_pupil(cx + 1 * s, cy + 2, 4.2),
           f'<ellipse cx="{cx+1*s}" cy="{cy+1}" rx="11" ry="14.5" fill="none" stroke="#3d0a1a" stroke-width="1"/>',
           f'<ellipse cx="{cx-4}" cy="{cy-5}" rx="4.2" ry="5.2" fill="#ffffff"/>',
           f'<circle cx="{cx+6}" cy="{cy+8}" r="2" fill="#ffffff"/>',
           f'<path d="M{cx-6*s},{cy+10} q4,3 9,0" stroke="#ffd6d0" stroke-width="1.6" fill="none" stroke-linecap="round"/>']
    t = -s   # lash wing / lower tick sit on the OUTER corner
    out.append(f'<path d="M{cx-14*t},{cy-5} C{cx-12*t},{cy-18} {cx+10*t},{cy-21} {cx+16*t},{cy-9} '
               f'L{cx+20*t},{cy-13} L{cx+17*t},{cy-4} C{cx+12*t},{cy-14} {cx-10*t},{cy-14} {cx-14*t},{cy-5}Z" fill="{INK}"/>')
    out.append(f'<path d="M{cx+5*t},{cy+15.5} q{5*t},-1 {8*t},-5" stroke="{INK}" stroke-width="1.3" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def _eye_wink(cx, cy, mirror=False):
    s = -1 if mirror else 1
    return (f'<path d="M{cx-13*s},{cy+1} Q{cx},{cy-13} {cx+13*s},{cy+1}" '
            f'stroke="{INK}" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
            f'<path d="M{cx-13*s},{cy+1} l{-4*s},-3 M{cx-12*s},{cy-3} l{-5*s},-6" stroke="{INK}" stroke-width="2" fill="none" stroke-linecap="round"/>')


# ------------------------------------------------------------------ hair
HAIR_RING = "#a8737c"    # angel-ring sheen (brighter than HAIR_HI, still warm plum)
HAIR_RING_HI = "#d7aab0"


def _lock(U, segs, widths, inner, front=True, rim=False, ring=True, lw0=2.6, lw1=.35):
    """One tapered hair lock (pointed tip) around a Bezier chain.
    inner = side index (+1/-1) facing the head.  Line weight thins from lw0 at the root to lw1 at
    the tip (the ink is a slightly wider ribbon drawn underneath, not a constant stroke)."""
    o = -inner
    rb = _Ribbon(segs, widths)
    ink = _Ribbon(segs, [(t, w + lw1 + (lw0 - lw1) * (1 - t) ** 1.2) for t, w in widths])
    g = [f'<path d="{ink.band(0, 1, -1, 1, 13)}" fill="{INK}"/>',
         f'<path d="{rb.band(0, 1, -1, 1, 13)}" fill="url(#{U}-hair)"/>']
    # hard-edged cel shadow on the head side; a toothy edge where strands break the light
    base = .26 if front else .1
    tri = (lambda t, c, h: max(0.0, 1 - abs(t - c) / h))
    jag = (lambda t: inner * (base - .5 * tri(t, .4, .1) - .36 * tri(t, .72, .08)))
    g.append(f'<path d="{rb.band(.03, .985, inner * 1.0, jag, 20)}" fill="{HAIR_SH}"/>')
    # occlusion just under the tie
    g.append(f'<path d="{rb.band(0, .06, -1, 1, 3)}" fill="{HAIR_SH}"/>')
    # lit streak on the outer side, hard edged, tapering to a point
    if front:
        g.append(f'<path d="{rb.band(.3, .62, o * .2, lambda t: o * (.22 + .4 * math.sin((t - .3) / .32 * math.pi)), 8)}" '
                 f'fill="{HAIR_HI}"/>')
        g.append(f'<path d="{rb.band(.7, .86, o * .3, lambda t: o * (.3 + .26 * math.sin((t - .7) / .16 * math.pi)), 5)}" '
                 f'fill="{HAIR_HI}" opacity=".85"/>')
    # angel ring: a crisp sheen across the lock near the tie, toothy lower edge
    if ring:
        t0, t1, n = .11, .17, 8
        top = [rb.pt(t0 - .012 * math.sin(i / n * math.pi), -.86 + 1.72 * i / n) for i in range(n + 1)]
        bot = [rb.pt(t1 + (.035 if i % 2 else 0) - .012 * math.sin(i / n * math.pi), -.86 + 1.72 * i / n)
               for i in range(n, -1, -1)]
        g.append('<path d="M' + " L".join(f"{_f(x)},{_f(y)}" for x, y in top + bot) + f'Z" fill="{HAIR_RING}"/>')
        c0 = [rb.pt(.125, o * a) for a in (.05, .3, .55)]
        g.append(f'<path d="M{_f(c0[0][0])},{_f(c0[0][1])} L{_f(c0[2][0])},{_f(c0[2][1])}" stroke="{HAIR_RING_HI}" '
                 f'stroke-width="2" stroke-linecap="round"/>')
    # strand line down the middle, fading before the tip
    g.append(f'<path d="{rb.line(.2, .8, o * .05, 7)}" stroke="{HAIR_SH}" stroke-width="1.2" fill="none" stroke-linecap="round"/>')
    if rim:
        g.append(f'<path d="{rb.line(.28, .9, o * .82, 7)}" stroke="{RIM}" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".75"/>')
    return _int_d("".join(g)), rb


def _int_d(frag):
    """Round path coordinates inside d="..." to whole units (keeps the tails' byte size down;
    at the card scales that is a sub-pixel change)."""
    import re
    num = re.compile(r"-?\d+\.\d+")
    return re.sub(r' d="([^"]+)"', lambda m: ' d="' + num.sub(lambda k: str(int(round(float(k.group(0))))), m.group(1)) + '"', frag)


def _tails(U):
    """Low twin tails tied behind the ears, each split into three tapered locks that end in
    pointed tips flicking outward; deliberately not mirror images."""
    out = []
    W_OUT = [(0, 3.5), (.07, 6.5), (.2, 8.6), (.45, 8.2), (.7, 5.6), (.88, 2.8), (1, 0)]
    W_MID = [(0, 4.5), (.07, 7.5), (.2, 10), (.45, 9.2), (.7, 6.2), (.88, 3.2), (1, 0)]
    W_IN = [(0, 3.5), (.1, 6), (.3, 7.4), (.6, 5.6), (.85, 2.6), (1, 0)]
    tails = [
        # viewer-left tail: fuller outward swell; inner side faces +x
        dict(cls="sway", inner=1, locks=[
            ("out", [((-58, -146), (-77, -147), (-100, -133), (-101, -100)),
                     ((-101, -100), (-102, -70), (-95, -50), (-99, -30)),
                     ((-99, -30), (-102, -17), (-107, -8), (-116, -5))], W_OUT),
            ("in", [((-58, -146), (-68, -142), (-82, -128), (-82, -104)),
                    ((-82, -104), (-82, -86), (-74, -72), (-76, -56)),
                    ((-76, -56), (-77, -45), (-80, -37), (-88, -32))], W_IN),
            ("mid", [((-58, -146), (-73, -145), (-92, -131), (-92, -102)),
                     ((-92, -102), (-92, -72), (-81, -56), (-85, -34)),
                     ((-85, -34), (-87, -20), (-89, -9), (-98, -2))], W_MID)]),
        # viewer-right tail: hangs straighter and closer; inner side faces -x
        dict(cls="sway2", inner=-1, locks=[
            ("out", [((58, -148), (75, -148), (95, -136), (95, -106)),
                     ((95, -106), (96, -78), (88, -60), (92, -40)),
                     ((92, -40), (95, -26), (101, -18), (110, -17))], W_OUT),
            ("in", [((58, -148), (68, -145), (79, -132), (78, -108)),
                    ((78, -108), (77, -90), (70, -76), (72, -62)),
                    ((72, -62), (73, -52), (76, -45), (83, -41))], W_IN),
            ("mid", [((58, -148), (72, -147), (86, -134), (86, -108)),
                     ((86, -108), (87, -80), (77, -62), (81, -44)),
                     ((81, -44), (83, -30), (87, -20), (95, -16))], W_MID)]),
    ]
    for tl in tails:
        g = [f'<g class="{U}-{tl["cls"]}">']
        rb_mid = None
        for name, segs, w in tl["locks"]:
            # Ribbon side +1 is +x for these downward locks, so 'inner' is given per tail
            frag, rb = _lock(U, segs, w, tl["inner"], front=(name == "mid"), rim=(name == "out"),
                             ring=True, lw0=2.6 if name == "mid" else 2.3)
            g.append(frag)
            if name == "mid":
                rb_mid = rb
        # hair tie: small red band with a gold bead, where the tail leaves the head
        o = -tl["inner"]
        g.append(f'<path d="{rb_mid.band(0, .035, -1.5, 1.5, 4)}" fill="{RED_SH}" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/>')
        bpt = rb_mid.pt(.018, o * 1.55)
        g.append(f'<circle cx="{_f(bpt[0])}" cy="{_f(bpt[1])}" r="2.2" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
        g.append('</g>')
        out.append("".join(g))
    return "".join(out)


def _bangs():
    """Hu Tao's swept fringe: parted on the viewer-left, clumps sweeping to the viewer-right,
    one long lock falling between the eyes, two short clumps flicking back toward the part."""
    d = ("M-58,-160 C-62,-208 -32,-236 0,-236 C34,-236 64,-208 58,-160 "
         # temple, then clumps whose tips hook to the viewer-right
         "C57,-152 57,-144 56,-134 "
         "C50,-150 44,-168 36,-182 "
         "C34,-170 36,-156 42,-146 "
         "C34,-154 26,-172 18,-188 "
         "C17,-176 18,-164 23,-154 "
         "C15,-162 9,-176 3,-190 "
         # the long lock falling between the eyes
         "C4,-172 2,-150 8,-134 "
         "C-1,-148 -5,-168 -10,-186 "
         "C-12,-176 -15,-166 -12,-158 "
         "C-18,-168 -21,-182 -25,-194 "
         # at the part the clumps flick back toward the viewer-left
         "C-28,-178 -34,-162 -44,-152 "
         "C-40,-162 -38,-174 -38,-186 "
         "C-44,-172 -50,-154 -56,-140 "
         "C-57,-146 -58,-153 -58,-160Z")
    out = [f'<path d="{d}" fill="{HAIR}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>']
    # shadow under the part + clump-separation wedges (hard cel shapes)
    out.append(f'<path d="M-25,-194 C-24,-202 -22,-210 -18,-218 C-20,-208 -21,-200 -20,-190Z '
               f'M3,-190 C4,-198 7,-206 11,-212 C10,-204 9,-198 9,-186Z '
               f'M18,-188 C21,-196 25,-202 30,-206 C28,-198 26,-192 24,-184Z '
               f'M36,-182 C40,-188 44,-192 48,-194 C46,-188 44,-184 42,-178Z '
               f'M-38,-186 C-40,-192 -44,-196 -48,-198 C-46,-192 -44,-188 -42,-182Z" fill="{HAIR_SH}"/>')
    # angel-ring sheen: hard-edged band with a toothy lower edge, broken at the part
    def arc(t, lift):
        x = -46 + 92 * t
        return x, -196 - 20 * (1 - (2 * t - 1) ** 2) - lift
    for t0, t1 in ((0.02, 0.2), (0.28, 0.95)):
        n = 10
        top = [arc(t0 + (t1 - t0) * i / n, 7) for i in range(n + 1)]
        bot = []
        for i in range(2 * n, -1, -1):
            x, y = arc(t0 + (t1 - t0) * i / (2 * n), 0)
            bot.append((x, y + (4 if i % 2 else 0)))
        out.append('<path d="M' + " L".join(f"{_f(x)},{_f(y)}" for x, y in top + bot) + f'Z" fill="{HAIR_HI}"/>')
    out.append('<path d="M-6,-218 C4,-221 14,-220 22,-218" stroke="#b78088" stroke-width="2" fill="none" stroke-linecap="round"/>')
    # strand lines following the sweep
    out.append(f'<path d="M7,-142 C3,-160 1,-176 -2,-196 M-14,-166 C-16,-178 -18,-188 -22,-200 '
               f'M23,-160 C19,-174 15,-186 10,-198 M40,-152 C36,-166 32,-180 27,-192 M-42,-158 C-38,-172 -34,-182 -30,-194" '
               f'stroke="{HAIR_SH}" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def _side_locks():
    out = []
    # viewer-left lock (longer, flicks out) / viewer-right lock (shorter, tucks in): not mirrored
    locks = [
        (-1, "M44,-178 C56,-168 60,-144 58,-122 C57,-108 61,-100 68,-94 C57,-94 51,-100 49,-108 "
             "C47,-102 43,-99 38,-97 C44,-112 46,-132 44,-150 C43,-160 42,-170 44,-178Z",
         "M48,-170 C52,-150 52,-130 50,-112 C48,-126 47,-148 48,-170Z", "M55,-158 C57,-146 57,-132 55,-120"),
        (1, "M44,-178 C56,-170 59,-148 57,-130 C56,-118 58,-110 62,-104 C53,-104 48,-110 47,-117 "
            "C45,-111 42,-108 38,-106 C43,-120 45,-136 44,-152 C43,-162 42,-170 44,-178Z",
         "M48,-170 C51,-152 51,-136 49,-122 C47,-134 47,-152 48,-170Z", "M54,-160 C56,-150 56,-140 54,-130"),
    ]
    for m, body, sh, hi in locks:
        out.append(f'<g transform="scale({m},1)">'
                   f'<path d="{body}" fill="{HAIR}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                   f'<path d="{sh}" fill="{HAIR_SH}"/>'
                   f'<path d="{hi}" stroke="{HAIR_HI}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>')
    return "".join(out)


# ------------------------------------------------------------------ clothes
def _legs():
    """Short chibi legs: thigh band, red garter, dark stockings, round shoes (ground frame)."""
    o = []
    for lx in (-11, 11):
        m = 1 if lx > 0 else -1
        # stocking
        o.append(f'<path d="M{lx-8.4},-36 C{lx-8.8},-26 {lx-7},-16 {lx-5.6},-8 L{lx+5.6},-8 C{lx+7},-16 {lx+8.8},-26 {lx+8.4},-36Z" '
                 f'fill="#58313e" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
        # cel shadow on the side away from the light (always viewer-right half) + shine on the lit side
        o.append(f'<path d="M{lx+1.5},-34 C{lx+1.5},-24 {lx+1.2},-16 {lx+.8},-9 L{lx+5},-9 C{lx+6.4},-16 {lx+7.8},-26 {lx+7.6},-34Z" fill="#3f2230"/>')
        o.append(f'<path d="M{lx-5.4},-21 C{lx-5.4},-17 {lx-5},-14 {lx-4.2},-11" stroke="#8d5d69" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
        # bare thigh + hard shadow under the shorts
        o.append(f'<path d="M{lx-8.6},-36 L{lx+8.6},-36 L{lx+8.4},-23 L{lx-8.4},-23Z" fill="{SKIN}"/>')
        o.append(f'<path d="M{lx-8.6},-31 L{lx+8.6},-31 L{lx+8.5},-27 C{lx+3},-28.6 {lx-3},-26.6 {lx-8.5},-28Z" fill="{SKIN_SH}"/>')
        o.append(f'<path d="M{lx-8.6},-36 L{lx-8.4},-23 M{lx+8.6},-36 L{lx+8.4},-23" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<path d="M{lx-8.5},-23 L{lx+8.5},-23" stroke="{INK}" stroke-width="1.8"/>'
                 f'<path d="M{lx-8.2},-21.2 L{lx+8.2},-21.2" stroke="{RED}" stroke-width="2"/>')
    for m in (-1, 1):
        o.append(f'<g transform="scale({m},1)"><path d="M24,-10 C26,-2 20,2 10,2 C4,2 1,-1 2,-6 C3,-11 8,-12 14,-12 C20,-12 23,-12 24,-10Z" '
                 f'fill="#6b3a3c" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                 f'<path d="M4,-1.5 C8,0.5 16,0.5 22,-3 C21,0 16,1.6 10,1.6 C6,1.6 4,0.6 4,-1.5Z" fill="#4e2a2e"/></g>')
    o.append('<path d="M-20,-8 q4,-3 9,-2" stroke="#a0646a" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
             '<path d="M11,-10 q4,-1 9,2" stroke="#a0646a" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def _coat_tails(U):
    """The long coat flaring behind her legs: lit left flap, shadowed right flap, fold wedges, red hem."""
    o = [f'<path d="{_FLAP_L}" fill="{COAT}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>',
         f'<path d="{_FLAP_R}" fill="{COAT_SH}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>']
    # left flap: highlight along the lit outer edge, two fold valleys running down into hem notches
    o.append(f'<g clip-path="url(#{U}-flapL)">'
             f'<path d="M-30,-98 C-44,-80 -56,-56 -63,-30 L-57,-29 C-52,-52 -42,-74 -27,-92Z" fill="{COAT_HI}"/>'
             f'<path d="M-52,-27 C-49,-44 -42,-62 -32,-80 C-38,-60 -44,-44 -46,-27Z" fill="{COAT_SH}"/>'
             f'<path d="M-40,-29 C-36,-44 -31,-58 -24,-72 C-27,-56 -30,-42 -31,-28Z" fill="{COAT_SH}"/>'
             f'<path d="M-20,-84 C-22,-66 -25,-46 -27,-28 L-34,-28 C-31,-46 -27,-66 -22,-86Z" fill="{COAT_DEEP}"/>'
             f'<path d="M-66,-33 C-60,-38 -56,-38 -52,-35 C-48,-40 -44,-40 -40,-37 C-36,-40 -32,-39 -28,-35 L-27,-20 L-70,-20Z" fill="{RED}"/>'
             f'<path d="M-65,-35.5 C-60,-40 -56,-40 -52,-37.5 C-48,-42 -44,-42 -40,-39.5 C-36,-42 -32,-41 -28,-37.5" stroke="{GOLD}" stroke-width="1.4" fill="none"/>'
             f'</g>')
    # right flap (in shadow): a lighter fold ridge, deep valley, rim light on the outer edge
    o.append(f'<g clip-path="url(#{U}-flapR)">'
             f'<path d="M44,-31 C42,-46 37,-62 29,-78 C35,-62 40,-48 40,-32Z" fill="{COAT}"/>'
             f'<path d="M20,-84 C22,-66 25,-46 27,-28 L33,-28 C30,-46 26,-66 22,-86Z" fill="{COAT_DEEP}"/>'
             f'<path d="M62,-36 C56,-38 52,-38 48,-35 C44,-39 40,-39 36,-35 C33,-38 30,-37 27,-35 L27,-20 L66,-20Z" fill="{RED_SH}"/>'
             f'<path d="M61,-38.5 C56,-40.5 52,-40.5 48,-37.5 C44,-41.5 40,-41.5 36,-37.5 C33,-40 30,-39.5 27,-37.5" stroke="{GOLD_SH}" stroke-width="1.4" fill="none"/>'
             f'</g>')
    o.append(f'<path d="M31,-94 C43,-77 53,-56 58,-37" stroke="{RIM}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".55"/>')
    o.append(f'<path d="{_FLAP_L}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
             f'<path d="{_FLAP_R}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    return "".join(o)


def _torso(U):
    o = [f'<path d="{_TORSO}" fill="url(#{U}-coat)" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>',
         # shorts peeking under the hem
         f'<path d="M-22,-50 L-22,-44 C-10,-41 10,-41 22,-44 L22,-50Z" fill="{COAT_SH}" stroke="{INK}" stroke-width="1.6"/>',
         f'<g clip-path="url(#{U}-torso)">',
         # lit plane on the light side (hard edge broken by the cloth)
         f'<path d="M-40,-104 L-15,-104 C-17,-94 -13,-86 -16,-77 C-18,-68 -14,-60 -17,-46 L-40,-46Z" fill="{COAT_LIT}"/>',
         # big form shadow on the side away from the light (wavy hard edge = cloth)
         f'<path d="M9,-110 C14,-96 13,-86 17,-76 C20,-68 17,-60 21,-50 L40,-50 L40,-110Z" fill="{COAT_SH}"/>',
         # occlusion shadow under the collar and chest
         f'<path d="M-30,-110 L30,-110 L30,-100 C22,-97 16,-101 9,-97 C2,-100 -4,-96 -11,-99 C-18,-96 -24,-100 -30,-97Z" fill="{COAT_SH}"/>',
         # fold valleys rising from the hem (shadow) with a lit ridge beside each
         f'<path d="M-24,-49 C-23,-56 -21,-63 -17,-70 C-18,-62 -18,-55 -17,-49Z" fill="{COAT_SH}"/>',
         f'<path d="M-28,-49 C-27,-57 -25,-64 -21,-70 L-19.5,-68.5 C-23,-62 -25,-56 -25.5,-49Z" fill="{COAT_HI}"/>',
         f'<path d="M12,-49 C11,-56 9,-62 6,-67 C9,-61 11,-55 17,-49Z" fill="{COAT_DEEP}"/>',
         # hard highlight shapes on the lit chest + a glint
         f'<path d="M-27,-100 C-29,-90 -30,-80 -31,-70 L-27.5,-72 C-26.5,-82 -25.5,-91 -23.5,-98Z" fill="{COAT_HI}"/>',
         f'<path d="M-26,-96 C-26.5,-92 -27,-89 -27.5,-86" stroke="{COAT_GLINT}" stroke-width="1.6" stroke-linecap="round" fill="none"/>',
         '</g>',
         # lavender rim light on the shadow edge
         f'<path d="M28,-96 C31,-82 33,-68 34.5,-56" stroke="{RIM}" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".5"/>',
         f'<path d="{_TORSO}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>']
    # coat opening, red collar, gold-piped lapels
    o.append(f'<path d="M-9,-106 L0,-74 L9,-106Z" fill="#2f1822"/>')
    o.append(f'<path d="M-14,-108 C-10,-100 -6,-96 0,-94 C6,-96 10,-100 14,-108 L9,-110 C6,-104 3,-101 0,-100 C-3,-101 -6,-104 -9,-110Z" '
             f'fill="{RED}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(f'<path d="M-9,-104 L-2,-75 M9,-104 L2,-75" stroke="{GOLD}" stroke-width="1.6" stroke-linecap="round"/>')
    for m in (-1, 1):
        fill = COAT_HI if m < 0 else COAT
        o.append(f'<path d="M{8*m},-106 L{27*m},-103 L{19*m},-90 L{10*m},-97Z" fill="{fill}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
                 f'<path d="M{11*m},-103 L{23*m},-101.5 L{18*m},-94" stroke="{GOLD}" stroke-width="1.1" fill="none" stroke-linejoin="round"/>')
    o.append(f'<path d="M-19,-90 L-10,-97 L-12,-93Z" fill="{COAT_SH}"/>')
    for by in (-82, -68):
        for bx in (-7, 7):
            o.append(f'<circle cx="{bx}" cy="{by}" r="2.1" fill="{GOLD}" stroke="{INK}" stroke-width=".8"/>'
                     f'<circle cx="{bx-.6}" cy="{by-.7}" r=".7" fill="#fff6dc"/>')
    # hem band (red, gold trim) with a shadowed right half
    o.append(f'<path d="M-36,-50 C-24,-46 24,-46 36,-50 L35,-56 C24,-52 -24,-52 -35,-56Z" fill="{RED}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(f'<path d="M14,-52.6 C24,-53 30,-54 35,-56 L36,-50 C30,-48 24,-47.4 15,-47Z" fill="{RED_SH}"/>')
    o.append(f'<path d="M-35,-56 C-24,-52 24,-52 35,-56" stroke="{GOLD}" stroke-width="1.3" fill="none"/>')
    # chest pendant: gold ring + red tassel
    o.append(f'<circle cx="0" cy="-90" r="3.6" fill="none" stroke="{GOLD}" stroke-width="2"/>'
             f'<path d="M-2,-86 L-3,-76 L3,-76 L2,-86Z" fill="{RED}" stroke="{INK}" stroke-width=".8"/>')
    return "".join(o)


def _hanging_arm(U):
    """Viewer-left arm hanging relaxed: bell sleeve with folds, red cuff, small curled hand."""
    o = [f'<path d="{_SLEEVE}" fill="{COAT}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>',
         f'<g clip-path="url(#{U}-sleeve)">',
         # shadow along the inner (body-side) edge, wavy
         f'<path d="M-23,-104 C-25,-96 -27,-90 -26,-84 C-29,-78 -28,-72 -31,-66 C-31,-62 -30,-60 -28,-58 L-14,-58 L-14,-106Z" fill="{COAT_SH}"/>',
         # elbow crease: two hard wedges
         f'<path d="M-37,-82 C-34,-81 -31,-79 -28,-78 C-31,-80.5 -33,-82.5 -35,-85Z" fill="{COAT_SH}"/>',
         f'<path d="M-39,-75 C-36,-74 -33,-73 -30,-73.5 C-33,-75 -35,-76.5 -37,-78Z" fill="{COAT_SH}"/>',
         # lit upper arm highlight + rim
         f'<path d="M-24,-104 C-31,-101 -35,-94 -36.5,-87 L-33.5,-88 C-32,-95 -29,-100 -24,-102Z" fill="{COAT_HI}"/>',
         '</g>',
         f'<path d="M-39.5,-84 C-41,-77 -43.5,-71 -46,-65.5" stroke="{RIM}" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".6"/>',
         f'<path d="{_SLEEVE}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>']
    # hand (drawn before the cuff so the cuff overlaps the wrist)
    hand = ("M-42.5,-63 C-44,-58 -44,-54 -42.5,-51 C-41,-48 -37.5,-47.6 -35.8,-50 "
            "C-34.6,-51.8 -35,-54 -35.6,-55.4 C-33.6,-55.6 -32.4,-57.4 -33.2,-59.4 C-33.6,-61 -34.6,-62 -35.4,-63Z")
    o.append(f'<path d="{hand}" fill="{SKIN}" stroke="{INK}" stroke-width="1.7" stroke-linejoin="round"/>')
    o.append(f'<path d="M-42.6,-61 C-40,-59.4 -37,-59.6 -35,-60.6 L-35.2,-63 L-42.6,-63Z" fill="{SKIN_SH}"/>')
    o.append(f'<path d="M-37.2,-58.6 C-36.4,-56.6 -36.6,-53.2 -37.4,-50.4 C-36.4,-50.2 -35.4,-50.8 -35.4,-52 C-35,-53.8 -35.2,-55.2 -35.8,-56.2Z" fill="{SKIN_SH}"/>')
    o.append(f'<path d="M-41.2,-54.4 C-40.2,-52.4 -38.8,-51 -37.2,-50.6 M-39.8,-56.2 C-39.2,-55 -38.4,-54.2 -37.4,-53.8 M-35.6,-55.4 C-36.6,-55.4 -37.4,-56 -37.8,-57" '
             f'stroke="{INK}" stroke-width="1.05" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M-42.4,-56 C-42.6,-54 -42.2,-52.6 -41.4,-51.6" stroke="#ffffff" stroke-width="1.1" fill="none" stroke-linecap="round" opacity=".8"/>')
    # flared red cuff with its dark opening
    o.append(f'<path d="M-48.5,-64.5 C-42,-61.2 -34,-60.4 -28,-62.2 L-28.6,-68 C-34,-66.6 -41,-67.4 -46.2,-70Z" '
             f'fill="{RED}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    o.append(f'<path d="M-34,-61 C-31.6,-61 -29.6,-61.4 -28,-62.2 L-28.6,-68 C-30.4,-67.4 -32.4,-67 -34.4,-66.8Z" fill="{RED_SH}"/>')
    o.append(f'<path d="M-46.8,-67.6 C-41,-64.8 -34,-64.2 -28.4,-65.6" stroke="{GOLD}" stroke-width="1.3" fill="none"/>')
    return "".join(o)


def _peace_arm():
    f = []
    f.append(f'<path d="M20,-104 C32,-104 46,-116 52,-128 L66,-120 C58,-104 40,-90 24,-90Z" '
             f'fill="{COAT}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    f.append(f'<path d="M34,-96 C44,-100 54,-108 60,-118 L66,-120 C58,-104 44,-92 30,-90Z" fill="{COAT_SH}"/>')
    f.append(f'<path d="M24,-102 C34,-104 44,-112 49,-121 L51,-118 C46,-110 36,-102 26,-100Z" fill="{COAT_HI}"/>')
    f.append(f'<path d="M40,-104 C42,-101 44,-99 47,-98 C44,-101 43,-103 43,-106Z" fill="{COAT_DEEP}"/>')
    f.append('<g transform="translate(62,-124) scale(1.25) translate(-62,128)">')
    f.append(f'<g stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" fill="{SKIN}">'
             f'<rect x="-3.4" y="-21" width="6.8" height="23" rx="3.4" transform="translate(57.5,-141) rotate(-17)"/>'
             f'<rect x="-3.4" y="-22" width="6.8" height="24" rx="3.4" transform="translate(65.5,-141) rotate(15)"/>'
             f'<rect x="52" y="-144" width="20" height="18" rx="7"/>'
             f'<path d="M50.5,-136 C51,-131 55,-129.5 60,-130.5 L64,-131.5 C66,-132.5 65.5,-135.5 63,-135.5 L56,-135Z"/>'
             f'</g>')
    f.append(f'<path d="M66,-140 q3.5,0 5,1.5 M66,-134.5 q3.5,0 5.4,1.5" stroke="{INK}" stroke-width="1.1" fill="none" stroke-linecap="round"/>')
    f.append(f'<path d="M54,-128.5 q8,2 16,-.5" stroke="{SKIN_SH}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    f.append(f'<path d="M55,-156 l-.8,4 M67.5,-157 l.8,4" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>')
    f.append('</g>')
    f.append(f'<path d="M47,-130 L71,-118 L68,-111 L44,-123Z" fill="{RED}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    f.append(f'<path d="M46,-126 L69,-114.5" stroke="{GOLD}" stroke-width="1.3"/>')
    return "".join(f)


def _akimbo_arm():
    o = [f'<path d="M18,-104 C30,-104 46,-96 52,-86 C55,-79 47,-72 38,-67 L32,-74 C38,-78 42,-81 41,-85 '
         f'C36,-92 28,-96 20,-96Z" fill="{COAT}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>',
         f'<path d="M30,-99 C40,-96 48,-90 51,-84 C52,-80 48,-76 44,-73 C46,-78 46,-82 42,-86 C38,-91 34,-95 30,-99Z" fill="{COAT_SH}"/>',
         f'<path d="M22,-102 C30,-102 38,-99 44,-94 L42,-92.5 C36,-97 30,-99.5 22,-100Z" fill="{COAT_HI}"/>',
         f'<ellipse cx="30" cy="-68" rx="6" ry="5.5" fill="{SKIN}" stroke="{INK}" stroke-width="1.8"/>',
         f'<path d="M27,-66 q3,2 6,0" stroke="{SKIN_SH}" stroke-width="1.8" fill="none" stroke-linecap="round"/>',
         f'<path d="M40,-64 L31,-75 L36,-79 L45,-68Z" fill="{RED}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>',
         f'<path d="M38.5,-65.5 L30.5,-76" stroke="{GOLD}" stroke-width="1.2"/>']
    return "".join(o)


def _hat():
    o = ['<g transform="rotate(-9 0 -228) translate(0,-226) scale(.86) translate(0,226)">']
    o.append(f'<path d="M-60,-224 C-58,-234 58,-234 62,-222 C56,-212 -54,-212 -60,-224Z" fill="{COAT}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    o.append(f'<path d="M-56,-221 C-40,-215 40,-215 58,-221 C52,-214 -48,-213 -56,-221Z" fill="{COAT_SH}"/>')
    o.append(f'<path d="M-36,-228 L-34,-263 C-20,-269 20,-269 34,-263 L38,-228 C20,-222 -18,-222 -36,-228Z" '
             f'fill="{COAT}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    o.append(f'<path d="M-34,-263 C-20,-267 20,-267 34,-263 C20,-259 -20,-259 -34,-263Z" fill="{COAT_HI}"/>')
    o.append(f'<path d="M18,-265 L22,-226 C30,-227 34,-228 38,-228 L34,-263Z" fill="{COAT_SH}"/>')
    o.append(f'<path d="M-30,-258 L-29,-240 L-25,-240 L-26,-259Z" fill="{COAT_HI}"/>')
    o.append(f'<path d="M-36,-230 L-35.4,-238 C-18,-233 18,-233 36.6,-238 L37.4,-230 C18,-225 -18,-225 -36,-230Z" fill="{RED}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(f'<path d="M-35.6,-236 C-18,-231 18,-231 36.8,-236" stroke="{GOLD}" stroke-width="1.1" fill="none"/>')
    o.append('<path d="M-46,-228 C-30,-231 -10,-232 6,-232" stroke="#8c5a62" stroke-width="2" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M22,-246 C30,-252 40,-263 50,-259" stroke="{INK}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    o.append(_blossom(30, -240, 11, rot=10))
    o.append(_blossom(46, -248, 8.5, rot=40, fill="#e04c62"))
    o.append(_blossom(42, -230, 7, rot=-20, fill="#d8405a"))
    o.append(f'<circle cx="55" cy="-253" r="2.6" fill="{PLUM_PINK}" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<path d="M50,-224 C52,-216 53,-210 52,-204" stroke="{RED}" stroke-width="1.8" fill="none"/>')
    o.append(f'<path d="M47,-206 L57,-206 L55,-192 L49,-192Z" fill="{GOLD}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(f'<path d="M50,-202 L54,-202 M50,-198 L54,-198" stroke="{RED_SH}" stroke-width="1.2"/>')
    o.append(f'<path d="M49,-192 L48,-180 M52,-192 L52,-178 M55,-192 L56,-180" stroke="{RED}" stroke-width="1.8" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


# ------------------------------------------------------------------ the character
def hutao(x, y, scale=1, uid="ht", pose="peace", boo=True, flip=False, boo_pose=None):
    """Chibi Hu Tao. (x, y) = ground point between her feet.
    pose: 'peace' (winks, V sign by her cheek) or 'grin' (both eyes open, fist on hip).
    boo: add Boo Tao (chars/bootao.py) floating by her hanging hand; boo_pose picks his pose.
    Bounding box at scale 1: BBOX[(pose, boo)] = (x0, y0, x1, y1) relative to (x, y);
    multiply by scale, and when flip=True use (-x1, y0, -x0, y1).
    """
    U = uid
    sx = -scale if flip else scale
    o = [_defs(U), f'<g transform="translate({x},{y}) scale({sx},{scale})">']
    o.append('<ellipse cx="0" cy="2" rx="44" ry="6" fill="#7d6aa8" opacity=".22"/>')
    o.append(_legs())
    o.append(f'<g transform="translate(0,{LIFT})">')   # ---- upper body frame
    o.append(f'<path d="M-62,-168 C-66,-214 -34,-238 0,-238 C34,-238 66,-214 62,-168 C60,-140 54,-118 46,-106 '
             f'L-46,-106 C-54,-118 -60,-140 -62,-168Z" fill="{HAIR_SH}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    o.append(_tails(U))
    o.append(_coat_tails(U))
    o.append(_torso(U))
    o.append(_hanging_arm(U))
    front = _peace_arm() if pose == "peace" else ""
    if pose != "peace":
        o.append(_akimbo_arm())
    # neck + face
    o.append(f'<path d="M-8,-114 L-8,-104 C-4,-100 4,-100 8,-104 L8,-114Z" fill="{SKIN_SH}" stroke="{INK}" stroke-width="1.6"/>')
    face = ('M-52,-170 C-53,-142 -42,-122 -24,-114 C-14,-109 -6,-107 0,-107 C6,-107 14,-109 24,-114 '
            'C42,-122 53,-142 52,-170 C50,-206 28,-222 0,-222 C-28,-222 -50,-206 -52,-170Z')
    o.append(f'<path d="{face}" fill="{SKIN}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    # hard-edged cel shadow cast by the fringe (follows the clump tips)
    o.append(f'<path d="M-51,-156 C-49,-148 -46,-144 -42,-145 C-36,-156 -30,-168 -24,-176 C-20,-168 -15,-156 -10,-152 '
             f'C-7,-158 -4,-166 -1,-165 C3,-150 6,-132 10,-131 C14,-142 18,-149 25,-148 C31,-148 37,-141 44,-140 '
             f'C47,-143 50,-146 52,-148 L52,-190 L-52,-190Z" fill="{SKIN_SH}"/>')
    if pose == "peace":
        o.append(_eye_open(-24, -150, U))
        o.append(_eye_wink(24, -150, mirror=True))
    else:
        o.append(_eye_open(-24, -150, U))
        o.append(_eye_open(24, -150, U, mirror=True))
    for bx in (-34, 34):
        o.append(f'<ellipse cx="{bx}" cy="-128" rx="9" ry="4.5" fill="{BLUSH}" opacity=".75"/>'
                 f'<path d="M{bx-5},-126 l3,-5 M{bx-1},-126 l3,-5 M{bx+3},-126 l3,-5" stroke="#e86a82" stroke-width="1.1" stroke-linecap="round"/>')
    o.append('<path d="M1,-134 l1.5,2" stroke="#d99a90" stroke-width="1.5" stroke-linecap="round"/>')
    o.append(f'<path d="M-9,-126 C-6,-125 6,-125 9,-127 C8,-118 3,-114 0,-114 C-4,-114 -8,-118 -9,-126Z" '
             f'fill="#8c2236" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>')
    o.append('<path d="M-5,-118 C-3,-121 3,-121 5,-118 C3,-115 -3,-115 -5,-118Z" fill="#ff8a9a"/>')
    o.append('<path d="M3,-126.2 L4.8,-122.5 L6.6,-126.6Z" fill="#ffffff"/>')
    o.append(_bangs())
    o.append(_side_locks())
    o.append(front)
    o.append(_hat())
    if boo:
        bp = boo_pose or "float"
        o.append(boo_tao(-98, -78 if pose == "peace" else -86, 1, uid=f"{U}-boo", pose=bp))
    o.append('</g></g>')
    return "\n".join(o)


# ------------------------------------------------------------------ showcase
def _sparkle(cx, cy, r, fill="#ffffff", cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<path{c} d="M{cx},{cy-r} Q{cx+r*0.18},{cy-r*0.18} {cx+r},{cy} Q{cx+r*0.18},{cy+r*0.18} {cx},{cy+r} '
            f'Q{cx-r*0.18},{cy+r*0.18} {cx-r},{cy} Q{cx-r*0.18},{cy-r*0.18} {cx},{cy-r}Z" fill="{fill}"/>')


def showcase():
    W = H = 600
    u = "hts"
    bt = _bootao_mod()
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         '<title>Hu Tao chibi fan art</title>',
         f'<defs><linearGradient id="{u}-bg" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#a9b2f0"/><stop offset=".45" stop-color="#d4cdf6"/>'
         '<stop offset=".8" stop-color="#fbd9e6"/><stop offset="1" stop-color="#ffe9e4"/></linearGradient>'
         f'<radialGradient id="{u}-sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6ea" stop-opacity=".95"/>'
         '<stop offset="1" stop-color="#fff6ea" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="{u}-rc"><rect width="600" height="600" rx="22"/></clipPath></defs>',
         f'<g clip-path="url(#{u}-rc)">',
         f'<rect width="600" height="600" fill="url(#{u}-bg)"/>',
         f'<circle cx="300" cy="250" r="260" fill="url(#{u}-sun)"/>']
    for a in (-40, -22, -5, 12, 30, 48):
        s.append(f'<path d="M300,250 L900,190 L900,280Z" fill="#ffffff" opacity=".10" transform="rotate({a-90} 300 250)"/>')
    s.append(f'<g opacity=".9">{bt.cloud(470, 130, .55, u)}</g>')
    s.append(bt.cloud(80, 505, .95, u))
    s.append(bt.cloud(540, 520, 1.05, u))
    s.append('<rect x="0" y="530" width="600" height="70" fill="#fbe2ea"/>')
    s.append('<path d="M0,530 C150,520 450,520 600,530 L600,537 C450,527 150,527 0,537Z" fill="#ffffff" opacity=".7"/>')
    s.append(hutao(285, 552, 1.85, uid="hA", pose="peace", boo=True))
    s.append(hutao(528, 400, 0.66, uid="hB", pose="grin", boo=False, flip=True))
    for (px, py, rot) in [(80, 120, 20), (140, 260, -30), (455, 300, 60), (430, 60, 10), (60, 360, 80), (560, 420, -40)]:
        s.append(f'<ellipse cx="{px}" cy="{py}" rx="7" ry="4" fill="#ff9fb4" transform="rotate({rot} {px} {py})"/>'
                 f'<ellipse cx="{px+1}" cy="{py+1}" rx="4" ry="1.6" fill="#e86a88" transform="rotate({rot} {px} {py})"/>')
    for i, (px, py, r) in enumerate([(110, 70, 10), (200, 150, 6), (470, 210, 8), (560, 330, 6), (40, 240, 7), (380, 40, 6)]):
        s.append(_sparkle(px, py, r, cls="hA-tw" if i % 2 == 0 else ""))
    s.append('</g></svg>')
    return "\n".join(s)


def write_showcase(path=SHOWCASE):
    """Write the 600x600 showcase SVG (scratch output only; never into the repo)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(showcase())
    return path


if __name__ == "__main__":
    print("wrote", write_showcase(sys.argv[1] if len(sys.argv) > 1 else SHOWCASE))
