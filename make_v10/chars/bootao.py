"""Boo Tao (Hu Tao's little ghost) -- our own chibi fan art, pure-stdlib SVG generator.

    from chars.bootao import bootao
    frag = bootao(x, y, scale=1, pose='float', uid='bt', shadow=True, flower=None,
                  flip=False, face=None, carry_svg=None, edge=16)

(x, y) is the centre of the ghost's round head in every pose.
pose:
  'float'   arms at the sides, plum blossom on the head (flower defaults on)
  'wave'    one nub raised and waving (animated)
  'lantern' holding a little swinging paper lantern out to the left
  'carry'   both nubs raised, holding something above the head.  carry_svg is an SVG
            fragment drawn in a frame whose origin (0, 0) is the grip point midway between
            the hands (head-local (0, -66); hands at x = +-29).  Draw the item on y <= ~+4,
            about 50-80 units wide, so both mittens overlap its lower edge (the mittens are
            drawn in front of it).  Default: a big cel-shaded gold star (r 40, centre (0,-30)).
  'peek'    only the top of the head shows, peeking up from behind an edge.  Everything
            below head-local y = edge (default 16, i.e. y + edge*scale on the page) is
            clipped; two little hands grip the edge (x = -43 and +41) and the tail tip
            curls up beside the head.  The mouth is hidden, only the eyes show.
            Put the ghost so the edge line lies on top of a sill / cloud / card edge.
face: 'happy' (round eyes, open smile), 'wink' (viewer-left eye open, right eye closed ^,
      open smile) or 'smug' (soft curved half-lids over a visible iris, small ':3' mouth).
      None (default) picks FACE_DEFAULT[pose]: float -> wink, lantern -> smug, else happy.
flip: mirror left/right.  shadow: soft floor shadow (float/wave/lantern/carry only).
Each fragment carries its own <defs> + <style>; ids/classes are prefixed by uid, so give
every instance a unique uid.  All CSS animation stops under prefers-reduced-motion.

BBOX[pose] = (min_x, min_y, max_x, max_y) relative to the anchor at scale 1, flip=False,
measured from renders (ink + lantern/item; the faint aura and floor shadow excluded).
With flip=True negate and swap the x values.  BBOX_GLOW includes the faint aura; the bob
animation lifts the ghost by up to BOB=7 units (peek: 3).  shadow=True adds an ellipse at
y=+100 (rx 46).

Running this file writes a showcase to the scratchpad (see SHOWCASE).
"""
import os
import zlib

INK = "#4a2550"      # deep plum outline
INK_SOFT = "#7b5a93"
BODY = "#fbf9ff"
LIT_EDGE = "#ece6fc"
SHADE = "#d8cdf3"
SHADE2 = "#b9a8e6"
RIM = "#ffffff"
BLUSH = "#ff9cbc"
BLUSH_L = "#ee5f8e"
EYE_TOP = "#24112e"
EYE_MID = "#57234f"
EYE_BOT = "#b4436f"
MOUTH = "#7a2853"
TONGUE = "#ff8aac"
GOLD = "#ffd27a"
GOLD_D = "#f2a65a"
GOLD_L = "#fff4cf"
RED = "#f0768c"
RED_D = "#c94a6c"

SHOWCASE = ("/private/tmp/claude-501/-Users-allen-Desktop/a50b0c32-36b9-4f3d-9a23-f8832c6a6de7/"
            "scratchpad/v10final/chars/bootao.svg")

# measured (see module docstring): ink incl. sparkles, lantern, default star (not its glow)
BBOX = {
    "float": (-78, -59, 90, 66),
    "wave": (-66, -59, 93, 63),
    "lantern": (-86, -53, 88, 84),
    "carry": (-68, -140, 90, 66),
    "peek": (-68, -53, 70, 19),      # with the default edge=16; the bottom is edge + 3
}
# the same including the faint aura / lantern glow / star glow (shadow=False)
BBOX_GLOW = {
    "float": (-78, -76, 90, 80),
    "wave": (-71, -76, 93, 79),
    "lantern": (-113, -75, 88, 88),
    "carry": (-76, -154, 90, 80),
    "peek": (-69, -53, 70, 19),
}
BOB = 7          # the float animation lifts everything (except peek) up to BOB units
AURA = 88

# Silhouette: round head (r~52-54 centred at 0,0) tapering at the lower right into a thin
# tail that sweeps right and curls up to a sharp tip at (78, 12).
BODY_D = ("M0,-51 C-30,-51 -54,-29 -54,0 C-54,27 -37,47 -12,55 "
          "C8,62 34,66 54,61 C72,56 86,43 88,27 C89,15 83,6 74,7 "
          "C80,10 83,18 80,28 C76,40 64,48 49,50 C45,50 42,49.6 40,49 "
          "C48,37 54,20 54,0 C54,-29 30,-51 0,-51 Z")
TIP = (74, 7)
# head only (peek pose: the tail is hidden below the edge)
HEAD_D = "M0,-51 C-30,-51 -54,-29 -54,0 C-54,30 -30,56 0,56 C30,56 54,30 54,0 C54,-29 30,-51 0,-51 Z"


def _anim_css(uid, delay):
    return f"""<style>
.{uid}-bob{{animation:{uid}-bob 3.4s ease-in-out {delay:.2f}s infinite}}
.{uid}-pk{{animation:{uid}-pk 4.2s ease-in-out {delay:.2f}s infinite}}
.{uid}-shd{{transform-box:fill-box;transform-origin:50% 50%;animation:{uid}-shd 3.4s ease-in-out {delay:.2f}s infinite}}
.{uid}-arm{{transform-box:fill-box;transform-origin:12% 88%;animation:{uid}-arm .9s ease-in-out infinite alternate}}
.{uid}-swing{{transform-box:fill-box;transform-origin:50% 0%;animation:{uid}-swing 3.4s ease-in-out {delay:.2f}s infinite}}
.{uid}-tw{{transform-box:fill-box;transform-origin:50% 50%;animation:{uid}-tw 2.6s ease-in-out infinite}}
.{uid}-wsp{{transform-box:fill-box;transform-origin:20% 100%;animation:{uid}-wsp 2.8s ease-in-out {delay:.2f}s infinite alternate}}
@keyframes {uid}-bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@keyframes {uid}-pk{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
@keyframes {uid}-shd{{0%,100%{{transform:scale(1);opacity:.55}}50%{{transform:scale(.86);opacity:.38}}}}
@keyframes {uid}-arm{{from{{transform:rotate(-10deg)}}to{{transform:rotate(14deg)}}}}
@keyframes {uid}-swing{{0%,100%{{transform:rotate(5deg)}}50%{{transform:rotate(-5deg)}}}}
@keyframes {uid}-tw{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(.55);opacity:.5}}}}
@keyframes {uid}-wsp{{from{{transform:rotate(-4deg)}}to{{transform:rotate(6deg)}}}}
@media (prefers-reduced-motion:reduce){{.{uid}-bob,.{uid}-pk,.{uid}-shd,.{uid}-arm,.{uid}-swing,.{uid}-tw,.{uid}-wsp{{animation:none}}}}
</style>"""


def _defs(uid, d=BODY_D):
    tx, ty = TIP
    return f'''<defs>
<clipPath id="{uid}-clip"><path d="{d}"/></clipPath>
<radialGradient id="{uid}-glow"><stop offset="0" stop-color="#ffffff" stop-opacity=".75"/><stop offset=".55" stop-color="#f4ecff" stop-opacity=".35"/><stop offset="1" stop-color="#ece2ff" stop-opacity="0"/></radialGradient>
<radialGradient id="{uid}-lit" cx="-20" cy="-24" r="64" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="{BODY}"/><stop offset="1" stop-color="{LIT_EDGE}"/></radialGradient>
<radialGradient id="{uid}-lglow"><stop offset="0" stop-color="#fff0c2" stop-opacity="1"/><stop offset=".35" stop-color="#ffd7a8" stop-opacity=".6"/><stop offset="1" stop-color="#ffc0cc" stop-opacity="0"/></radialGradient>
<radialGradient id="{uid}-warm" cx="-74" cy="52" r="74" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffc79a" stop-opacity=".95"/><stop offset=".5" stop-color="#ffd3c0" stop-opacity=".5"/><stop offset="1" stop-color="#ffe0e8" stop-opacity="0"/></radialGradient>
<linearGradient id="{uid}-eye" x1="0" y1="0" x2="0" y2="1"><stop offset=".15" stop-color="{EYE_TOP}"/><stop offset=".6" stop-color="{EYE_MID}"/><stop offset="1" stop-color="{EYE_BOT}"/></linearGradient>
<radialGradient id="{uid}-shd"><stop offset="0" stop-color="#8873c4" stop-opacity=".5"/><stop offset="1" stop-color="#8873c4" stop-opacity="0"/></radialGradient>
<linearGradient id="{uid}-tl" x1="44" y1="0" x2="66" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d4d4d4"/></linearGradient>
<radialGradient id="{uid}-tf" cx="{tx}" cy="{ty}" r="26" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#000" stop-opacity=".95"/><stop offset=".35" stop-color="#000" stop-opacity=".6"/><stop offset=".75" stop-color="#000" stop-opacity=".15"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<mask id="{uid}-m" maskUnits="userSpaceOnUse" x="-130" y="-140" width="280" height="260"><rect x="-130" y="-140" width="280" height="260" fill="url(#{uid}-tl)"/><circle cx="{tx}" cy="{ty}" r="26" fill="url(#{uid}-tf)"/></mask>
<linearGradient id="{uid}-lwg" x1="30" y1="0" x2="62" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="{uid}-lw" maskUnits="userSpaceOnUse" x="-80" y="-80" width="160" height="160"><rect x="-80" y="-80" width="160" height="160" fill="url(#{uid}-lwg)"/><circle cx="-5" cy="-6" r="52.5" fill="#000"/></mask>
<linearGradient id="{uid}-pf" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#e4e4e4"/><stop offset=".9" stop-color="#7a7a7a"/><stop offset="1" stop-color="#666"/></linearGradient>
</defs>'''


def sparkle(x, y, r, fill="#fff", cls="", op=1):
    k = r * .22
    d = (f"M{x},{y-r} C{x+k*.4},{y-k} {x+k},{y-k*.4} {x+r},{y} "
         f"C{x+k},{y+k*.4} {x+k*.4},{y+k} {x},{y+r} "
         f"C{x-k*.4},{y+k} {x-k},{y+k*.4} {x-r},{y} "
         f"C{x-k},{y-k*.4} {x-k*.4},{y-k} {x},{y-r}Z")
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="{fill}" opacity="{op}"/>'


def _nub(cx, cy, ang, L=15, w=8, cls=""):
    """little mitten-shaped arm, drawn BEHIND the body so the body outline makes the join.
    base at (cx, cy) pointing ang degrees; L = reach beyond the base."""
    c = f' class="{cls}"' if cls else ""
    d = (f"M-8,{-w} C{L*.4:.1f},{-w-.3} {L-5:.1f},{-w-1.4} {L:.1f},{-w*.6:.1f} "
         f"C{L+4.4:.1f},{-w*.2:.1f} {L+4.2:.1f},{w*.55:.1f} {L-.5:.1f},{w*.9:.1f} "
         f"C{L-4:.1f},{w+.8} {L*.4:.1f},{w+.2} -8,{w} Z")
    shade = (f"M{L*.15:.1f},{w*.45:.1f} C{L*.5:.1f},{w*.62:.1f} {L-1:.1f},{w*.55:.1f} {L+2.8:.1f},{w*.05:.1f} "
             f"C{L+2.2:.1f},{w*.62:.1f} {L-2:.1f},{w*.95:.1f} {L-5:.1f},{w*.97:.1f} "
             f"C{L*.5:.1f},{w*1.02:.1f} {L*.2:.1f},{w*.9:.1f} {L*.15:.1f},{w*.45:.1f}Z")
    return (f'<g{c}><g transform="translate({cx},{cy}) rotate({ang})">'
            f'<path d="{d}" fill="{BODY}" stroke="{INK}" stroke-width="3.4" stroke-linejoin="round"/>'
            f'<path d="{shade}" fill="{SHADE}"/>'
            f'<ellipse cx="{L-3:.1f}" cy="{-w*.42:.1f}" rx="2.6" ry="1.5" fill="#ffffff"/>'
            f'</g></g>')


def _noodle_arm(k):
    """carry pose: a tapered noodle arm rooted at the upper SIDE of the body (about a third
    of the way down, behind the outline), bowing out into an elbow beside the head and bending
    up past it to a mitten under the carried item at (k*29, -66).  k = -1 left, +1 right.
    Returns (arm, hand): the arm goes behind the body, the hand in front of the item."""
    import math
    p0, p1, p2 = (k * 44, -6), (k * 74, -32), (k * 33, -64)
    L, R = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        m = math.hypot(dx, dy)
        nx, ny = -dy / m, dx / m
        w = 8.6 - 2.4 * t
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    outer = L if k < 0 else R
    pl = lambda pts: " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    hx, hy = k * 29, -66
    arm = (f'<path d="M{pl(L + R[::-1])}Z" fill="{BODY}" stroke="{INK}" stroke-width="3.3" stroke-linejoin="round"/>'
           f'<path d="M{pl(outer[5:14])}" fill="none" stroke="{SHADE}" stroke-width="4" stroke-linecap="round" '
           f'transform="translate({-k*1.8},0)"/>')
    hand = (f'<ellipse cx="{hx}" cy="{hy}" rx="9.4" ry="8.4" transform="rotate({k*-20} {hx} {hy})" fill="{BODY}" '
            f'stroke="{INK}" stroke-width="3.3"/>'
            f'<path d="M{hx-k*2},{hy+7.4} C{hx+k*5},{hy+7} {hx+k*9},{hy+3} {hx+k*9.2},{hy-1.6} '
            f'C{hx+k*5.6},{hy+2.4} {hx+k*2},{hy+4.6} {hx-k*2},{hy+7.4}Z" fill="{SHADE}"/>'
            f'<path d="M{hx-k*4.6},{hy-6.2} L{hx-k*6.4},{hy-1.8}" stroke="{INK_SOFT}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<ellipse cx="{hx+k*1.5}" cy="{hy-4.4}" rx="2.6" ry="1.5" fill="#ffffff"/>')
    return arm, hand


def _hand(cx, cy, k=1):
    """a little mitten gripping an edge at (cx, cy) (dome above the edge line)"""
    s = (f'<g transform="translate({cx},{cy}) scale({k})">'
         f'<path d="M-10,1 C-11,-8 -5,-12 0,-12 C6,-12 11,-8 10,1" fill="{BODY}" stroke="{INK}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="M3,-10.5 C8,-9 9.6,-5 9,0 L3,0 C5,-3 5,-7 3,-10.5Z" fill="{SHADE}"/>'
         f'<path d="M-2.5,1 L-2.5,-3.6 M2.8,1 L2.8,-3.2" stroke="{INK_SOFT}" stroke-width="1.8" stroke-linecap="round"/>'
         f'<ellipse cx="-4.6" cy="-8" rx="2.4" ry="1.4" fill="#ffffff" transform="rotate(-25 -4.6 -8)"/>'
         f'</g>')
    return s


def _lantern(x, y):
    """small hanging lantern; (x,y) is the top of the string"""
    s = []
    s.append(f'<path d="M{x},{y} L{x},{y+16}" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    cy = y + 34
    s.append(f'<ellipse cx="{x}" cy="{cy}" rx="15" ry="14" fill="{RED}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{x+4},{cy-13} C{x+13},{cy-9} {x+15},{cy+6} {x+6},{cy+13} C{x+15},{cy+10} {x+14.5},{cy-8} {x+4},{cy-13}Z" fill="{RED_D}"/>')
    s.append(f'<path d="M{x},{cy-14} C{x-6},{cy-6} {x-6},{cy+6} {x},{cy+14}" fill="none" stroke="{RED_D}" stroke-width="1.6"/>')
    s.append(f'<path d="M{x},{cy-14} C{x+6},{cy-6} {x+6},{cy+6} {x},{cy+14}" fill="none" stroke="{RED_D}" stroke-width="1.6"/>')
    s.append(f'<ellipse cx="{x-2}" cy="{cy}" rx="5" ry="7" fill="{GOLD}"/>')
    s.append(f'<ellipse cx="{x-3.5}" cy="{cy-3}" rx="1.8" ry="3" fill="#fffbe8"/>')
    s.append(f'<path d="M{x-8},{cy-8} C{x-10},{cy-4} {x-10},{cy+2} {x-9},{cy+5}" fill="none" stroke="#ffd4de" stroke-width="2" stroke-linecap="round"/>')
    s.append(f'<rect x="{x-8}" y="{cy-19}" width="16" height="6" rx="2" fill="{INK}"/>')
    s.append(f'<rect x="{x-7}" y="{cy+13}" width="14" height="5" rx="2" fill="{INK}"/>')
    s.append(f'<rect x="{x-5}" y="{cy-17.5}" width="6" height="1.6" rx=".8" fill="#9a6aa0"/>')
    s.append(f'<path d="M{x},{cy+18} L{x},{cy+23} M{x-2.5},{cy+23} L{x-2.5},{cy+31} M{x},{cy+23} L{x},{cy+33} M{x+2.5},{cy+23} L{x+2.5},{cy+31}" stroke="{RED_D}" stroke-width="2" stroke-linecap="round"/>')
    s.append(f'<circle cx="{x}" cy="{cy+23}" r="2.4" fill="{GOLD_D}" stroke="{INK}" stroke-width="1.2"/>')
    return "".join(s)


def _plum(x, y, r, rot=0):
    """tiny five-petal plum blossom (Hu Tao hat motif)"""
    s = [f'<g transform="translate({x},{y}) rotate({rot})">']
    for i in range(5):
        s.append(f'<ellipse cx="0" cy="{-r*.62:.2f}" rx="{r*.5:.2f}" ry="{r*.56:.2f}" transform="rotate({i*72})" '
                 f'fill="{RED}" stroke="{INK}" stroke-width="1.6"/>')
    for i in range(5):
        s.append(f'<ellipse cx="{r*.12:.2f}" cy="{-r*.5:.2f}" rx="{r*.2:.2f}" ry="{r*.3:.2f}" transform="rotate({i*72})" fill="#ffc2d1"/>')
    s.append(f'<circle r="{r*.28:.2f}" fill="{GOLD}" stroke="{INK}" stroke-width="1.2"/>')
    s.append('</g>')
    return "".join(s)


def _star(cx, cy, r, uid):
    """cel-shaded soft-gold five-point star (default carry item)"""
    import math
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * .5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    # rounded star: quadratic corners
    d = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        a = (p1[0] + (p0[0] - p1[0]) * .16, p1[1] + (p0[1] - p1[1]) * .16)
        b = (p1[0] + (p2[0] - p1[0]) * .16, p1[1] + (p2[1] - p1[1]) * .16)
        d.append(("M" if i == 0 else "L") + f"{a[0]:.1f},{a[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {b[0]:.1f},{b[1]:.1f}")
    d = " ".join(d) + "Z"
    # shadow half: right side triangles from centre
    sh = []
    for i in (1, 2, 3, 4):
        p, q = pts[i], pts[i + 1]
        sh.append(f"M{cx:.1f},{cy:.1f} L{p[0]:.1f},{p[1]:.1f} L{q[0]:.1f},{q[1]:.1f}Z")
    return (f'<defs><clipPath id="{uid}-st"><path d="{d}"/></clipPath>'
            f'<radialGradient id="{uid}-sg"><stop offset="0" stop-color="#fff6d8" stop-opacity=".95"/>'
            f'<stop offset=".5" stop-color="#ffe4b0" stop-opacity=".35"/><stop offset="1" stop-color="#ffd9c8" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*1.7:.1f}" fill="url(#{uid}-sg)"/>'
            f'<path d="{d}" fill="{GOLD}"/>'
            f'<g clip-path="url(#{uid}-st)"><path d="{"".join(sh)}" fill="{GOLD_D}" opacity=".8"/>'
            f'<path d="M{cx-r*.62:.1f},{cy-r*.28:.1f} L{cx-r*.1:.1f},{cy-r*.32:.1f} L{cx-r*.02:.1f},{cy-r*.9:.1f}" fill="none" stroke="{GOLD_L}" stroke-width="{r*.12:.1f}" stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            + sparkle(round(cx + r * .9, 1), round(cy - r * .78, 1), r * .32, "#ffffff", f"{uid}-tw"))


def _round_eye(uid, ex, ey, look=0.0, s=1):
    """big round anime eye: plum-to-rose iris, dark upper lash arc with an outer flick,
    a large highlight + a small bounce dot.  s = outer side (-1 viewer-left eye, +1 right)."""
    return [
        f'<ellipse cx="{ex}" cy="{ey}" rx="7.6" ry="10.4" fill="url(#{uid}-eye)"/>',
        # pupil (darker core) for depth
        f'<ellipse cx="{ex+look*.6:.1f}" cy="{ey+1.2}" rx="3.6" ry="5.4" fill="{EYE_TOP}" opacity=".55"/>',
        # upper lash: thicker in the middle, flicks out at the outer corner
        f'<path d="M{ex-s*5.6},{ey-7.6} Q{ex+s*.6},{ey-13.4} {ex+s*6.8},{ey-5.6} Q{ex+s*8.6},{ey-4.6} {ex+s*9.8},{ey-2.6}" '
        f'fill="none" stroke="{INK}" stroke-width="3.1" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<ellipse cx="{ex-2.2+look}" cy="{ey-3.8}" rx="3.3" ry="4.1" fill="#ffffff"/>',
        f'<circle cx="{ex+2.9+look}" cy="{ey+4.9}" r="1.6" fill="#ffffff" opacity=".92"/>',
        f'<path d="M{ex-3.6},{ey+8.6} Q{ex},{ey+10.4} {ex+3.6},{ey+8.6}" fill="none" stroke="#ff9cbc" stroke-width="1.3" '
        f'stroke-linecap="round" opacity=".9"/>',
    ]


def _closed_eye(ex, ey, s=1):
    """happy closed eye (^ arc) with a tiny outer lash flick"""
    return [f'<path d="M{ex-8.4},{ey+3.4} Q{ex-.6},{ey-7.4} {ex+8.4},{ey+3.4}" fill="none" stroke="{INK}" '
            f'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="M{ex+s*7.6},{ey+1.8} L{ex+s*10.6},{ey-.4}" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>']


def _open_smile(mx, my, w=8.2, h=11.4):
    """open 'D' smile with a tongue"""
    return [f'<path d="M{mx-w},{my} Q{mx},{my+2.2} {mx+w},{my} Q{mx+w*.86:.1f},{my+h} {mx},{my+h} '
            f'Q{mx-w*.86:.1f},{my+h} {mx-w},{my} Z" fill="{MOUTH}" stroke="{INK}" stroke-width="2.3" stroke-linejoin="round"/>',
            f'<path d="M{mx-w*.56:.1f},{my+h*.78:.1f} Q{mx},{my+h*.42:.1f} {mx+w*.56:.1f},{my+h*.78:.1f} '
            f'Q{mx},{my+h+.2:.1f} {mx-w*.56:.1f},{my+h*.78:.1f}Z" fill="{TONGUE}"/>']


def _face(uid, kind, ex1, ex2, ey, mx, my, look=0.0, mouth=True):
    """kind: 'happy' (round eyes, open smile), 'wink' (viewer-left eye open, right eye a
    closed ^ arc, open smile) or 'smug' (soft, curved half-lids over a visible iris with
    highlight, small closed ':3' cat mouth -- mischievous but still cute)."""
    o = []
    if kind in ("happy", "wink"):
        o.extend(_round_eye(uid, ex1, ey, look, -1))
        if kind == "wink":
            o.extend(_closed_eye(ex2, ey + 1, 1))
        else:
            o.extend(_round_eye(uid, ex2, ey, look, 1))
        if mouth:
            o.extend(_open_smile(mx, my))
        return o
    # --- smug (softened): curved upper lid covering the top ~30% of a round iris
    for i, ex in enumerate((ex1, ex2)):
        s = -1 if i == 0 else 1          # outer side direction
        cid = f"{uid}-lid{i}"
        # region below the lid curve (convex upward, a touch lower at the outer corner)
        lid = f"M{ex-10.4},{ey-1.4} Q{ex},{ey-8.8} {ex+10.4},{ey-1.4}"
        # mouthless (peek): the cheeks push the lower lids up into a grin-squint, so the teasing
        # reads from the eyes alone instead of looking half-asleep
        grin = not mouth
        bottom = (f"L{ex+10.4},{ey+9.5} Q{ex},{ey+1.5} {ex-10.4},{ey+9.5}Z" if grin
                  else f"L{ex+10.4},{ey+14} L{ex-10.4},{ey+14}Z")
        o.append(f'<clipPath id="{cid}"><path d="{lid} {bottom}"/></clipPath>')
        o.append(f'<g clip-path="url(#{cid})">'
                 f'<ellipse cx="{ex}" cy="{ey+1}" rx="7.6" ry="10" fill="url(#{uid}-eye)"/>'
                 f'<ellipse cx="{ex+look*.6:.1f}" cy="{ey+2.4}" rx="3.6" ry="5" fill="{EYE_TOP}" opacity=".55"/>'
                 f'<ellipse cx="{ex-2.3+look}" cy="{ey-.6}" rx="3.1" ry="3.5" fill="#ffffff"/>'
                 f'<circle cx="{ex+2.9+look}" cy="{ey+(3.4 if grin else 6)}" r="1.6" fill="#ffffff" opacity=".92"/></g>')
        if grin:
            o.append(f'<path d="M{ex-7.6},{ey+8} Q{ex},{ey+1.8} {ex+7.6},{ey+8}" fill="none" stroke="{INK}" '
                     f'stroke-width="2" stroke-linecap="round"/>')
        # the lid line itself, with a lash flick at the outer corner
        lo_y = ey - 1.4
        ox = ex + s * 10.4
        o.append(f'<path d="{lid}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>')
        o.append(f'<path d="M{ox-s*1.2},{lo_y} L{ox+s*2.4},{lo_y+2.4}" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    if not mouth:
        return o
    # small closed ':3' cat mouth
    o.append(f'<path d="M{mx-7.2},{my+.6} Q{mx-6.4},{my+5.6} {mx-3},{my+5} Q{mx-.6},{my+4.4} {mx},{my+1.6} '
             f'Q{mx+.6},{my+4.4} {mx+3},{my+5} Q{mx+6.4},{my+5.6} {mx+7.2},{my+.6}" fill="none" stroke="{INK}" '
             f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return o


def _body(uid, pose, warm=False, d=BODY_D):
    """head + tail silhouette with cel shading, gloss and the fading tail tip"""
    o = [f'<g mask="url(#{uid}-m)">']
    o.append(f'<path d="{d}" fill="{SHADE}"/>')
    o.append(f'<g clip-path="url(#{uid}-clip)">')
    # lit cel (hard edge), airbrushed inside
    o.append(f'<circle cx="-8" cy="-10" r="56" fill="url(#{uid}-lit)"/>')
    # core shadow where the head overhangs the tail root
    o.append(f'<path d="M39,48 C30,56 14,60 -4,60 L-4,70 L60,70 C58,62 50,54 39,48Z" fill="{SHADE2}" opacity=".55"/>')
    o.append(f'<path d="M54,6 C52,26 46,40 39,48 C47,47 55,46 62,43 C58,36 57,22 54,6Z" fill="{SHADE2}" opacity=".5"/>')
    # bounce light hugging the lower rim
    o.append(f'<path d="M-49,18 C-44,38 -28,52 -6,57 C14,62 36,61 52,56" fill="none" stroke="{RIM}" '
             f'stroke-width="3" stroke-linecap="round" opacity=".9" transform="translate(1.5,-4.5)"/>')
    # inner glow running up the tail (ghostly translucency)
    o.append(f'<path d="M46,56 C64,53 79,42 83,26" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity=".8"/>')
    if warm:
        o.append(f'<rect x="-80" y="-80" width="180" height="160" fill="url(#{uid}-warm)"/>')
    o.append('</g>')
    o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linejoin="round"/>')
    # line-weight variation: heavier ink on the shadow side (lower right), tapering out
    o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="6.2" stroke-linejoin="round" mask="url(#{uid}-lw)"/>')
    o.append('</g>')
    # gloss: bold crescent + dash + dot (upper-left), pale periwinkle under-edge so it reads on white
    o.append('<path d="M-44,-15 C-41,-32 -28,-44 -12,-47" fill="none" stroke="#d4d0ff" stroke-width="9.5" stroke-linecap="round" opacity=".55" transform="translate(2.2,2.2)"/>')
    o.append('<path d="M-44,-15 C-41,-32 -28,-44 -12,-47" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/>')
    o.append('<path d="M-46.5,-4 L-46.6,-2" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>')
    o.append('<circle cx="-2" cy="-46.6" r="2.4" fill="#ffffff"/>')
    return o


# default expression per pose (face=None): cheerful everywhere; the telescope / float pose
# winks (its viewer-left eye stays open), the lantern pose is the one gently mischievous look.
FACE_DEFAULT = {"float": "wink", "wave": "happy", "carry": "happy", "peek": "happy", "lantern": "smug"}


def bootao(x, y, scale=1, pose="float", uid="bt", shadow=True, flower=None, flip=False,
           face=None, carry_svg=None, edge=16):
    """Boo Tao chibi. (x,y) = head centre. See module docstring / BBOX for extents."""
    if flower is None:
        flower = pose == "float"
    if face is None:
        face = FACE_DEFAULT.get(pose, "happy")
    delay = (zlib.crc32(uid.encode()) % 17) / 10
    sx = -scale if flip else scale
    o = [f'<g transform="translate({x},{y}) scale({sx},{scale})">', _anim_css(uid, delay),
         _defs(uid, HEAD_D if pose == 'peek' else BODY_D)]

    if pose == "peek":
        o.append(f'<defs><clipPath id="{uid}-pc"><rect x="-140" y="-160" width="280" height="{160+edge}"/></clipPath>'
                 f'<mask id="{uid}-pm" maskUnits="userSpaceOnUse" x="30" y="-50" width="46" height="{50+edge+12}">'
                 f'<rect x="30" y="-50" width="46" height="{50+edge+12}" fill="url(#{uid}-pf)"/></mask></defs>')
        o.append(f'<g clip-path="url(#{uid}-pc)">')
        o.append(f'<ellipse cx="0" cy="{edge}" rx="78" ry="60" fill="url(#{uid}-glow)"/>')
        # tail tip curling up beside the head (the rest of the ghost is hidden below the edge)
        e = edge
        tail = (f"M52,{e+8} C60,{e-6} 64,-8 67,-20 C70,-33 65,-43 55,-44 "
                f"C49,-44.5 45,-40 47,-36 C50,-39 54,-39 57,-35 C60,-30 58,-20 55,-10 "
                f"C52,-1 47,{e-4} 40,{e+8}Z")
        o.append(f'<g mask="url(#{uid}-pm)"><path d="{tail}" fill="{SHADE}" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>'
                 f'<path d="M57,{e-4} C61,-2 64,-12 64,-24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round"/></g>')
        o.append(f'<g class="{uid}-pk">')
        o.extend(_body(uid, pose, d=HEAD_D))
        o.extend(_face(uid, face, -21, 11, -6, -5, 13, look=-1.2, mouth=False))
        for bx in (-36, 26):
            o.append(f'<ellipse cx="{bx}" cy="7" rx="8.4" ry="4.4" fill="{BLUSH}" opacity=".75"/>')
            o.append(f'<path d="M{bx-4.5},9.2 l2.6,-4.6 M{bx-.5},9.2 l2.6,-4.6 M{bx+3.5},9.2 l2.6,-4.6" '
                     f'stroke="{BLUSH_L}" stroke-width="1.3" stroke-linecap="round" opacity=".8"/>')
        if flower:
            o.append(_plum(-30, -46, 10, -12))
        o.append('</g></g>')
        o.append(_hand(-43, edge, 1))
        o.append(_hand(41, edge, 1))
        o.append(sparkle(-62, -30, 6, GOLD, f"{uid}-tw"))
        o.append('</g>')
        return "\n".join(o)

    if shadow:
        o.append(f'<ellipse class="{uid}-shd" cx="10" cy="100" rx="46" ry="7.5" fill="url(#{uid}-shd)"/>')
    tilt = {"wave": -6, "lantern": 5, "carry": 0}.get(pose, 0)
    o.append(f'<g class="{uid}-bob"><g transform="rotate({tilt})">')
    o.append(f'<circle cx="6" cy="2" r="{AURA}" fill="url(#{uid}-glow)"/>')

    lantern = ""
    if pose == "lantern":
        o.append(f'<circle cx="-68" cy="54" r="46" fill="url(#{uid}-lglow)"/>')
        o.append(_nub(-48, 20, 176, L=16, w=8.5))
        o.append(_nub(48, 14, 12))
        lantern = (f'<g transform="rotate(-5 -68 22)"><g class="{uid}-swing">' + _lantern(-68, 22) + '</g></g>')
    elif pose == "wave":
        o.append(_nub(-49, 22, 158))
        o.append(_nub(45, -16, -48, L=20, w=8.5, cls=f"{uid}-arm"))
    elif pose == "carry":
        item = carry_svg if carry_svg is not None else _star(0, -30, 40, uid)
        arms = [_noodle_arm(k) for k in (-1, 1)]
        o.extend(a for a, _ in arms)
        lantern = f'<g transform="translate(0,-66)">{item}</g>' + "".join(h for _, h in arms)
    else:
        o.append(_nub(-50, 21, 160))
        o.append(_nub(49, 12, 14))

    o.extend(_body(uid, pose, warm=(pose == "lantern")))
    o.append(lantern)

    # face, shifted left (3/4 turn away from the tail); looks up when carrying
    if pose == "carry":
        o.extend(_face(uid, face, -20, 12, -5, -4, 11, look=.6))
    else:
        o.extend(_face(uid, face, -21, 11, 0, -5, 14, look=-1.0))
    by = 13 if pose != "carry" else 9
    for bx in (-37, 27):
        o.append(f'<ellipse cx="{bx}" cy="{by}" rx="8.8" ry="4.8" fill="{BLUSH}" opacity=".75"/>')
        o.append(f'<path d="M{bx-4.5},{by+2.2} l2.6,-4.6 M{bx-.5},{by+2.2} l2.6,-4.6 M{bx+3.5},{by+2.2} l2.6,-4.6" '
                 f'stroke="{BLUSH_L}" stroke-width="1.3" stroke-linecap="round" opacity=".8"/>')

    if flower:
        o.append(_plum(-30, -46, 10, -12))
    if pose == "wave":
        o.append(f'<path d="M80,-40 q5,6 3.5,13 M88,-49 q9,10 6.5,23" fill="none" stroke="{INK}" '
                 f'stroke-width="2.6" stroke-linecap="round" opacity=".6"/>')
    if pose == "float":
        o.append(sparkle(-70, -40, 8, GOLD, f"{uid}-tw"))
        o.append(sparkle(70, -38, 5.5, "#ffb3cb", f"{uid}-tw"))
    o.append('</g></g></g>')
    return "\n".join(o)


# ---------------------------------------------------------------- showcase
_cn = [0]


def cloud(x, y, s, uid, puffs=None):
    """anime cumulus: cauliflower puffs lit from upper-left with a hard-edged lavender core
    shadow; flat shaded underside clipped to the cloud's own silhouette."""
    if puffs is None:
        puffs = [(-104, 6, 20), (-74, -6, 30), (-38, -24, 38), (6, -40, 46), (50, -22, 38),
                 (86, -4, 28), (112, 8, 18), (-10, -8, 34), (30, -2, 30)]
    _cn[0] += 1
    cid = f"{uid}-c{_cn[0]}"
    shape = "".join(f'<circle cx="{px}" cy="{py}" r="{r}"/>' for px, py, r in puffs)
    o = [f'<g transform="translate({x},{y}) scale({s})">',
         f'<defs><clipPath id="{cid}b"><rect x="-200" y="-200" width="400" height="214"/></clipPath>'
         f'<clipPath id="{cid}s">{shape}</clipPath></defs>',
         f'<g clip-path="url(#{cid}b)"><g clip-path="url(#{cid}s)">',
         '<rect x="-200" y="-200" width="400" height="400" fill="#e2d6f8"/>']
    for px, py, r in sorted(puffs, key=lambda q: q[1] - q[2]):
        o.append(f'<circle cx="{px}" cy="{py}" r="{r}" fill="#ddd0f6"/>')
        o.append(f'<circle cx="{px-r*.16:.1f}" cy="{py-r*.22:.1f}" r="{r*.84:.1f}" fill="#fcfaff"/>')
    for px, py, r in puffs:
        if r > 30:
            o.append(f'<ellipse cx="{px-r*.42:.1f}" cy="{py-r*.5:.1f}" rx="{r*.22:.1f}" ry="{r*.12:.1f}" '
                     f'transform="rotate(-35 {px-r*.42:.1f} {py-r*.5:.1f})" fill="#ffffff"/>')
    wave = "".join(f" Q{-200+i*40+20},{-5 if i%2 else -2} {-200+i*40+40},1" for i in range(10))
    o.append(f'<path d="M-200,1{wave} L200,40 L-200,40Z" fill="#d3c5f3"/>')
    o.append('<path d="M-200,9 C-60,6 40,11 200,8 L200,40 L-200,40Z" fill="#bfaee9"/>')
    o.append('</g></g></g>')
    return "".join(o)


def wisp(x, y, s=1, uid="w"):
    """little ghost-fire (pastel will-o'-wisp); needs a radialGradient id f"{uid}-wg" in scope"""
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<circle cy="2" r="22" fill="url(#{uid}-wg)"/>'
            f'<path d="M4,-21 C1,-12 11,-7 11,3 C11,11 6,15 0,15 C-6,15 -11,11 -11,3 C-11,-6 -1,-9 4,-21Z" '
            f'fill="#ffb3cf" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M0,-2 C3,2 6,4 6,8 C6,11 3,12.5 0,12.5 C-3,12.5 -6,11 -6,8 C-6,4 -2,3 0,-2Z" fill="#fff4f8"/>'
            f'<path d="M5.5,0 C9,3 9.5,9 5,12.5" fill="none" stroke="#f27aa6" stroke-width="2.2" stroke-linecap="round"/>'
            '</g>')


def showcase(path):
    W, H = 900, 600
    u = "bts"
    b = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'''<defs>
<clipPath id="{u}-r"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<linearGradient id="{u}-sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#9aaaf0"/><stop offset=".4" stop-color="#c6c1f6"/><stop offset=".75" stop-color="#f4d2ec"/><stop offset="1" stop-color="#ffe5ec"/></linearGradient>
<radialGradient id="{u}-sun" cx=".8" cy=".12" r=".55"><stop offset="0" stop-color="#fff8e8" stop-opacity=".95"/><stop offset=".4" stop-color="#ffeef2" stop-opacity=".35"/><stop offset="1" stop-color="#fff0f4" stop-opacity="0"/></radialGradient>
</defs>''',
         f'<g clip-path="url(#{u}-r)">',
         f'<rect width="{W}" height="{H}" fill="url(#{u}-sky)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#{u}-sun)"/>']
    for x0, w, x1, op in [(690, 30, 330, .16), (730, 18, 480, .12), (770, 46, 600, .10)]:
        b.append(f'<path d="M{x0},-20 L{x0+w},-20 L{x1+w*3},620 L{x1},620Z" fill="#ffffff" opacity="{op}"/>')
    b.append(f'<g opacity=".7">{cloud(820, 250, .7, u)}{cloud(70, 220, .6, u)}</g>')
    for (sx, sy, r, c) in [(60, 70, 7, "#fff"), (840, 110, 9, "#fff6d6"), (380, 40, 4, "#fff"), (560, 60, 5, "#fff")]:
        b.append(sparkle(sx, sy, r, c))
    b.append(bootao(150, 170, 1.2, "float", "bta", shadow=False))
    b.append(bootao(450, 205, 1.2, "carry", "btb", shadow=False))
    b.append(bootao(750, 170, 1.2, "wave", "btc", shadow=False))
    b.append(bootao(170, 420, 1.1, "lantern", "btd", shadow=False))
    # peek over a cloud edge
    # a little pastel stone parapet for the peek pose to hide behind (edge line at y = 470 + 16*1.2)
    ey = 470 + 16 * 1.2
    b.append(f'<path d="M330,{ey} L610,{ey} L610,620 L330,620Z" fill="#c9bff2"/>'
             f'<path d="M330,{ey} L610,{ey} L610,{ey+9} L330,{ey+9}Z" fill="#ece6ff"/>'
             f'<path d="M330,{ey+9} L610,{ey+9} L610,{ey+16} L330,{ey+16}Z" fill="#a99ae0"/>'
             f'<path d="M330,{ey} L610,{ey} M330,{ey+16} L610,{ey+16}" stroke="{INK}" stroke-width="3"/>'
             f'<path d="M330,{ey} L330,620 M610,{ey} L610,620" stroke="{INK}" stroke-width="3"/>')
    b.append(bootao(470, 470, 1.2, "peek", "bte"))
    b.append(cloud(470, 600, 1.3, u, puffs=[(-150, 8, 26), (-100, -10, 40), (-40, -22, 48), (20, -24, 50),
                                             (80, -16, 44), (140, 0, 30), (180, 10, 20), (-170, 12, 20)]))
    b.append(bootao(760, 430, 1.1, "float", "btf", shadow=False, face="happy", flip=True, flower=False))
    b.append(cloud(150, 640, 1.3, u))
    b.append(cloud(800, 650, 1.3, u))
    b.append('</g></svg>')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(b))


if __name__ == "__main__":
    showcase(SHOWCASE)
    print("wrote", SHOWCASE)
