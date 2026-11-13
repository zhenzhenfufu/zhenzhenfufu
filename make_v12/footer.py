"""v12 footer (1600 x 240): a calm full-bleed anime dusk over still water; bottom of the README sheet,
so only the bottom corners are rounded.  Carries the HoYoverse credit line.

Official chibi Hu Tao says thanks at the left and chibi Keqing dozes on a pillow at the right (Genshin Impact
"Paimon's Paintings" emoji, (c) HoYoverse, embedded from art/ by art.py); the low sun sets in the middle under
"thanks for stopping by" + a small plum-blossom glyph.  Pure stdlib, no script / external refs.

    python3 footer.py [out_dir]     -> writes footer.svg (default: ../assets/v12)
    build(out_dir) -> path
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
from scenes import nwa as NWA  # noqa: E402

W, H, RX = 1600, 240, 28
U = "ft"                      # uid prefix for everything this file draws
HZ = 156                      # horizon / far water line
SUN_X = 800
FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"
TXT = "thanks for stopping by"
TXT_SIZE = 44
TXT_LEN = 520                 # fixed with textLength so every font lands the same width
TXT_Y = 92

INK = "#3a3482"               # deep indigo text / ink
INK_SOFT = "#5b4f9e"
SAK, SAK_D, SAK_L = "#f6a9c6", "#e07aa5", "#ffe3ef"
GOLD, GOLD_L = "#ffd48a", "#fff3d2"
CREAM = "#fff8ef"
DEFAULT_OUT = os.path.join(os.path.dirname(HERE), "assets", "v12")


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def star4(x, y, r, col="#ffffff", op=1.0, cls=""):
    """Anime four-point sparkle with concave sides."""
    k = r * .2
    d = (f"M{f(x)} {f(y-r)} Q{f(x+k)} {f(y-k)} {f(x+r)} {f(y)} Q{f(x+k)} {f(y+k)} {f(x)} {f(y+r)} "
         f"Q{f(x-k)} {f(y+k)} {f(x-r)} {f(y)} Q{f(x-k)} {f(y-k)} {f(x)} {f(y-r)}Z")
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="{col}" opacity="{op}"/>'


# ------------------------------------------------------------------ style
def style():
    return (f'<style>'
            f'@keyframes {U}-tw{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.25;transform:scale(.6)}}}}'
            f'@keyframes {U}-dr{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(7px)}}}}'
            f'@keyframes {U}-gl{{0%,100%{{opacity:.95}}50%{{opacity:.45}}}}'
            f'@keyframes {U}-rp{{0%{{transform:scale(.55);opacity:.9}}100%{{transform:scale(1.25);opacity:0}}}}'
            f'.{U}-tw,.{U}-tw2,.{U}-tw3{{transform-box:fill-box;transform-origin:50% 50%}}'
            f'.{U}-tw{{animation:{U}-tw 2.8s ease-in-out infinite}}'
            f'.{U}-tw2{{animation:{U}-tw 3.4s ease-in-out -1.1s infinite}}'
            f'.{U}-tw3{{animation:{U}-tw 4.1s ease-in-out -2s infinite}}'
            f'.{U}-dr{{animation:{U}-dr 7s ease-in-out infinite}}'
            f'.{U}-dr2{{animation:{U}-dr 9s ease-in-out -2.5s infinite reverse}}'
            f'.{U}-gl{{animation:{U}-gl 2.4s ease-in-out infinite}}'
            f'.{U}-gl2{{animation:{U}-gl 3s ease-in-out -1.2s infinite}}'
            f'.{U}-rp{{transform-box:fill-box;transform-origin:50% 50%;animation:{U}-rp 3.6s ease-out infinite}}'
            f'.{U}-rp2{{transform-box:fill-box;transform-origin:50% 50%;animation:{U}-rp 3.6s ease-out -1.8s infinite}}'
            # salon.py gives the pets' second rising bubble a positive 1.6s delay whose 0% keyframe is
            # opacity 0, so the bubble would sit visible for 1.6s and then blink out; a negative delay starts
            # it mid-cycle instead.  g.<cls> outranks the plain .<cls> rule, and only the delay is touched,
            # so the pets' own reduced-motion `animation:none` still wins.
            f'g.{U}cm-up2,g.{U}cr-up2{{animation-delay:-1.6s}}'
            f'@media (prefers-reduced-motion: reduce){{.{U}-tw,.{U}-tw2,.{U}-tw3,.{U}-dr,.{U}-dr2,.{U}-gl,.{U}-gl2,'
            f'.{U}-rp,.{U}-rp2{{animation:none}}}}'
            f'</style>')


# ------------------------------------------------------------------ sky
def sky():
    defs = (f'<linearGradient id="{U}-sky" x1="0" y1="0" x2="0" y2="{HZ}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#9fa6ec"/><stop offset=".38" stop-color="#bdb3f2"/>'
            f'<stop offset=".72" stop-color="#e9c4ea"/><stop offset="1" stop-color="#ffdcdc"/></linearGradient>'
            f'<radialGradient id="{U}-sunglow" cx="{SUN_X}" cy="{HZ}" r="430" gradientUnits="userSpaceOnUse" '
            f'gradientTransform="translate({SUN_X} {HZ}) scale(1 .42) translate({-SUN_X} {-HZ})">'
            f'<stop offset="0" stop-color="#fff4dc" stop-opacity=".95"/><stop offset=".25" stop-color="#ffe0d2" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="#ffd6e4" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{U}-ray" x1="0" y1="{HZ}" x2="0" y2="0" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fffaf0" stop-opacity=".55"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/>'
            f'</linearGradient>'
            f'<radialGradient id="{U}-sun" cx=".5" cy=".38" r=".62">'
            f'<stop offset="0" stop-color="#fffdf6"/><stop offset=".7" stop-color="#fff0cf"/><stop offset="1" stop-color="#ffd9b0"/>'
            f'</radialGradient>')
    o = [f'<rect width="{W}" height="{HZ+2}" fill="url(#{U}-sky)"/>',
         f'<rect width="{W}" height="{HZ+2}" fill="url(#{U}-sunglow)"/>']
    # light rays fanning up from the setting sun
    rays = []
    for ang, wd in ((-62, 5), (-38, 7), (-16, 4), (14, 6), (36, 4), (58, 7)):
        a0, a1 = math.radians(ang - 90 - wd / 2), math.radians(ang - 90 + wd / 2)
        R = 700
        rays.append(f'M{SUN_X} {HZ} L{f(SUN_X + R*math.cos(a0))} {f(HZ + R*math.sin(a0))} '
                    f'L{f(SUN_X + R*math.cos(a1))} {f(HZ + R*math.sin(a1))}Z')
    o.append(f'<path d="{" ".join(rays)}" fill="url(#{U}-ray)"/>')
    return defs, "".join(o)


def far_stratus():
    """Long flat anime dusk streaks low on the horizon (lit pink tops, lavender bellies)."""
    o = []
    for x, y, w, h, top, bot in ((150, 128, 380, 7, "#ffe7ef", "#d9c3ee"), (420, 140, 260, 5, "#fff0f2", "#e2c9ef"),
                                 (1060, 122, 420, 8, "#ffeaf0", "#d6c0ee"), (1290, 138, 300, 5, "#fff1f3", "#e2caef"),
                                 (640, 112, 120, 4, "#fff4f0", "#e6cdef")):
        o.append(f'<path d="M{x} {y} q{w*.12:.0f} {-h*1.4:.0f} {w*.4:.0f} {-h:.0f} t{w*.6:.0f} {h*.4:.0f} '
                 f'q{-w*.2:.0f} {h*.9:.0f} {-w:.0f} {h*.6:.0f}Z" fill="{bot}"/>'
                 f'<path d="M{x+w*.06:.0f} {y-h*.3:.1f} q{w*.12:.0f} {-h*1.2:.0f} {w*.38:.0f} {-h*.8:.0f} '
                 f't{w*.5:.0f} {h*.3:.0f} q{-w*.4:.0f} {-h*.2:.0f} {-w*.88:.0f} {h*.5:.0f}Z" fill="{top}"/>')
    return "".join(o)


def clouds():
    """Two small cel-shaded cumulus with flat shaded undersides (nwa helper), lit by the low sun."""
    cols = ("#a99fe2", "#d3c3f3", "#f8dcec", "#fff6f4")
    d1, b1 = NWA.cumulus(U, "cuA", [(382, 74, 64), (428, 74, 100), (476, 74, 58)], (SUN_X, HZ), cols, seed=4)
    d2, b2 = NWA.cumulus(U, "cuB", [(1178, 64, 56), (1216, 64, 88), (1258, 64, 50)], (SUN_X, HZ), cols, seed=9)
    d3, b3 = NWA.cumulus(U, "cuC", [(120, 60, 50), (156, 60, 76)], (SUN_X, HZ), cols, seed=2)
    return d1 + d2 + d3, (f'<g id="{U}-clA" class="{U}-dr">{b1}</g><g id="{U}-clB" class="{U}-dr2">{b2}</g>'
                          f'<g id="{U}-clC" class="{U}-dr2">{b3}</g>')


def sun():
    return (f'<circle cx="{SUN_X}" cy="{HZ+6}" r="46" fill="#ffe9d6" opacity=".55"/>'
            f'<circle cx="{SUN_X}" cy="{HZ+6}" r="30" fill="url(#{U}-sun)"/>')


def far_isles():
    """Pale distant islets / headlands on the horizon."""
    return (f'<path d="M0 {HZ} V{HZ-14} C30 {HZ-18} 60 {HZ-22} 92 {HZ-16} C120 {HZ-11} 150 {HZ-9} 190 {HZ-4} L230 {HZ}Z" '
            f'fill="#c9b9ef"/><path d="M0 {HZ-14} C30 {HZ-18} 60 {HZ-22} 92 {HZ-16} L92 {HZ-12} C60 {HZ-16} 30 {HZ-12} 0 {HZ-9}Z" '
            f'fill="#ddd0f6"/>'
            f'<path d="M1330 {HZ} C1370 {HZ-10} 1400 {HZ-15} 1438 {HZ-13} C1480 {HZ-11} 1530 {HZ-20} 1600 {HZ-18} V{HZ}Z" '
            f'fill="#cbbbef"/><path d="M1438 {HZ-13} C1480 {HZ-11} 1530 {HZ-20} 1600 {HZ-18} V{HZ-14} '
            f'C1530 {HZ-15} 1480 {HZ-7} 1438 {HZ-9}Z" fill="#ded1f6"/>')


# ------------------------------------------------------------------ water
def water():
    defs = (f'<linearGradient id="{U}-wat" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#f6d3e4"/><stop offset=".35" stop-color="#d6c6f2"/>'
            f'<stop offset="1" stop-color="#a9aced"/></linearGradient>'
            f'<radialGradient id="{U}-shal" cx="210" cy="250" r="330" gradientUnits="userSpaceOnUse" '
            f'gradientTransform="translate(210 250) scale(1 .38) translate(-210 -250)">'
            f'<stop offset="0" stop-color="#fff1e6" stop-opacity=".95"/><stop offset=".55" stop-color="#fbe2ea" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="#f4d8ee" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{U}-rfl" x1="0" y1="{HZ}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity=".1"/>'
            f'</linearGradient>'
            f'<mask id="{U}-rm" maskUnits="userSpaceOnUse" x="0" y="{HZ}" width="{W}" height="{H-HZ}">'
            f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{U}-rfl)"/></mask>'
            f'<clipPath id="{U}-wc"><rect x="0" y="{HZ}" width="{W}" height="{H-HZ}"/></clipPath>')
    o = [f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{U}-wat)"/>']
    # mirrored clouds + isles, sliced (anime broken-mirror reflection)
    refl = (f'<g mask="url(#{U}-rm)"><g transform="translate(0 {2*HZ}) scale(1 -1)">'
            f'<use href="#{U}-far"/></g></g>')
    o.append(f'<g clip-path="url(#{U}-wc)">{refl}</g>')
    # hard-edged cel bands: a deeper periwinkle swell in the foreground, a pale sheen band under the horizon
    o.append(f'<path d="M0 {HZ+6} C300 {HZ+3} 520 {HZ+9} 800 {HZ+6} C1080 {HZ+3} 1300 {HZ+10} 1600 {HZ+6} V{HZ+14} '
             f'C1300 {HZ+18} 1080 {HZ+11} 800 {HZ+15} C520 {HZ+19} 300 {HZ+12} 0 {HZ+16}Z" fill="#fff3f4" opacity=".55"/>')
    o.append(f'<path d="M0 222 C140 214 300 226 470 218 C640 210 760 224 940 218 C1120 212 1300 226 1600 214 V{H} H0Z" '
             f'fill="#9b9fe8" opacity=".5"/>'
             f'<path d="M470 218 C640 210 760 224 940 218 C1120 212 1300 226 1600 214" fill="none" stroke="#ffffff" '
             f'stroke-width="1.6" opacity=".55"/>')
    o.append(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#{U}-shal)"/>')
    # horizon shine line
    o.append(f'<rect x="0" y="{HZ-.6}" width="{W}" height="1.6" fill="#fff6f4" opacity=".9"/>')
    # sun glitter column: short capsules widening toward the viewer
    rnd = random.Random(5)
    gl = []
    y = HZ + 4
    i = 0
    while y < H:
        t = (y - HZ) / (H - HZ)
        for _ in range(2 if t > .3 else 1):
            w = (26 + 120 * t) * rnd.uniform(.35, 1)
            x = SUN_X + rnd.uniform(-1, 1) * (16 + 90 * t) - w / 2
            hgt = 2 + 2.2 * t
            cls = f"{U}-gl" if i % 2 else f"{U}-gl2"
            col = "#fff6dd" if rnd.random() < .6 else "#ffe2b6"
            gl.append(f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(hgt)}" rx="{f(hgt/2)}" fill="{col}"/>')
            i += 1
        y += 4 + 9 * t
    o.append("".join(gl))
    # cel water bands: pale lens lines (lit) with darker periwinkle under-strokes, perspective spacing
    rnd = random.Random(11)
    lines = []
    for k in range(26):
        t = rnd.random() ** 1.6
        y = HZ + 6 + t * (H - HZ - 10)
        L = 30 + 220 * t * rnd.uniform(.5, 1)
        x = rnd.uniform(0, W)
        if abs(x - SUN_X) < 140 + 80 * t:
            continue
        th = 1 + 1.8 * t
        lines.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(L)}" height="{f(th)}" rx="{f(th/2)}" fill="#ffffff" opacity="{f(.35 + .4*t)}"/>'
                     f'<rect x="{f(x + L*.15)}" y="{f(y + th + 1)}" width="{f(L*.7)}" height="{f(th*.8)}" rx="{f(th*.4)}" '
                     f'fill="#8c8ade" opacity="{f(.18 + .2*t)}"/>')
    o.append(f'<g class="{U}-dr">{"".join(lines)}</g>')
    return defs, "".join(o)


def shoal():
    """Pale wet-sand shoal peeking out at the bottom-left: the creatures' shallows."""
    top = "M0 210 C30 212 70 218 100 222 C130 226 170 232 210 {H}".replace("{H}", str(H))
    return (f'<path d="{top} L0 {H}Z" fill="#f7e1dc" opacity=".55"/>'
            f'<path d="M0 220 C30 222 60 226 86 230 C110 234 136 238 150 {H} L0 {H}Z" fill="#f9e4dd"/>'
            f'<path d="M0 220 C30 222 60 226 86 230 C110 234 136 238 150 {H} L138 {H} C120 238 96 234 70 231 '
            f'C46 228 22 226 0 226Z" fill="#fffaf4"/>'
            f'<path d="M0 232 C30 232 56 236 76 {H} L0 {H}Z" fill="#efd0d6"/>')


def ripple(cx, cy, rx, cls=""):
    """Cel ripple ring on the water surface at a creature's waterline: lit front arc + shadow back arc."""
    ry = rx * .22
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c}><path d="M{f(cx-rx)} {f(cy)} A{f(rx)} {f(ry)} 0 0 1 {f(cx+rx)} {f(cy)}" fill="none" stroke="#8f8fe0" '
            f'stroke-width="1.6" opacity=".55"/>'
            f'<path d="M{f(cx-rx)} {f(cy)} A{f(rx)} {f(ry)} 0 0 0 {f(cx+rx)} {f(cy)}" fill="none" stroke="#ffffff" '
            f'stroke-width="2.2" opacity=".95"/></g>')


# ------------------------------------------------------------------ characters
def pets():
    """Chibi Hu Tao saying thanks on the left (official Genshin Impact emoji, (c) HoYoverse)."""
    o = [f'<ellipse cx="250" cy="182" rx="210" ry="70" fill="url(#{U}-back)"/>']
    o.append(ART.place("hutao_thanks", 250, H + 10, 230, U + "ht", shadow=("#6f5fc8", .35, 8), fade=(H - 26, H + 4)))
    return "".join(o)


def boo():
    """Chibi Keqing dozing on her pillow on the right (official Genshin Impact emoji, (c) HoYoverse)."""
    o = [f'<ellipse cx="1380" cy="182" rx="210" ry="70" fill="url(#{U}-back)"/>']
    o.append(ART.place("keqing_sleep", 1380, H + 10, 230, U + "kq", shadow=("#6f5fc8", .35, 8), fade=(H - 26, H + 4)))
    for px, py, ps, rot in ((1200, 210, 6, 30), (1560, 216, 5.5, -50), (1250, 228, 7, 110)):
        o.append(f'<g transform="translate({px} {py}) scale(1 .5)">{NWA.petal(0, 0, ps, rot)}</g>'
                 f'<ellipse cx="{px}" cy="{py + 3}" rx="{f(ps*1.3)}" ry="1.1" fill="#ffffff" opacity=".7"/>')
    o.append(NWA.petal(1180, 70, 5.5, -35, f"{U}-tw3"))
    return "".join(o)


# ------------------------------------------------------------------ text
def plum(x, y, r):
    """Cel-shaded plum blossom glyph."""
    o = [f'<g transform="translate({f(x)} {f(y)}) rotate(-12)">']
    pet = []
    for i in range(5):
        a = math.radians(i * 72 - 90)
        px, py = math.cos(a) * r * .56, math.sin(a) * r * .56
        pet.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(r*.47)}"/>')
    o.append(f'<g fill="{SAK}" stroke="{INK}" stroke-width="2.2">{"".join(pet)}</g>')
    o.append(f'<g fill="{SAK}">{"".join(pet)}</g>')
    # hard cel shadow on lower-right petals + light upper-left
    o.append(f'<path d="M{f(r*.15)} {f(r*.05)} L{f(r*.95)} {f(r*.2)} A{f(r)} {f(r)} 0 0 1 {f(-r*.35)} {f(r*.95)}Z" '
             f'fill="{SAK_D}" opacity=".55"/>')
    o.append(f'<ellipse cx="{f(-r*.42)}" cy="{f(-r*.5)}" rx="{f(r*.2)}" ry="{f(r*.11)}" transform="rotate(-40 {f(-r*.42)} {f(-r*.5)})" fill="#fff"/>')
    o.append(f'<circle r="{f(r*.24)}" fill="{GOLD}" stroke="{INK}" stroke-width="1.3"/>')
    for i in range(5):
        a = math.radians(i * 72 - 54)
        o.append(f'<circle cx="{f(math.cos(a)*r*.38)}" cy="{f(math.sin(a)*r*.38)}" r="1.3" fill="#d9883f"/>')
    o.append('</g>')
    return "".join(o)


def thanks():
    glyph = 34
    x0 = 800 - (TXT_LEN + glyph) / 2
    rnd = random.Random(3)
    rot = " ".join(f(rnd.uniform(-5.5, 5.5)) for _ in TXT)
    dy = [0] * len(TXT)
    prev = 0
    for i in range(len(TXT)):
        cur = rnd.uniform(-2.2, 2.2)
        dy[i] = f(cur - prev)
        prev = cur
    attrs = (f'x="{f(x0)}" y="{TXT_Y}" textLength="{TXT_LEN}" lengthAdjust="spacing" font-family="{FONT}" '
             f'font-size="{TXT_SIZE}" font-weight="600" rotate="{rot}" dy="{" ".join(dy)}"')
    o = [f'<g transform="translate({f(x0)} {TXT_Y}) skewX(-9) translate({f(-x0)} {-TXT_Y})">',
         # soft cream halo so the ink reads on sky and rays
         f'<text {attrs} fill="{CREAM}" stroke="{CREAM}" stroke-width="8" stroke-linejoin="round" opacity=".6">{TXT}</text>',
         f'<text {attrs} fill="{INK}">{TXT}</text>',
         '</g>']
    # tapered brush swash under the words (sakura pink, darker lower edge like a cel brush stroke)
    ux0, ux1, uy = x0 + 4, x0 + TXT_LEN - 14, TXT_Y + 17
    L = ux1 - ux0
    o.append(f'<path d="M{f(ux0)} {f(uy)} C{f(ux0+L*.3)} {f(uy-4)} {f(ux0+L*.7)} {f(uy-2)} {f(ux1)} {f(uy-7)} '
             f'C{f(ux0+L*.72)} {f(uy+7)} {f(ux0+L*.3)} {f(uy+10)} {f(ux0)} {f(uy)}Z" fill="{SAK}"/>')
    o.append(f'<path d="M{f(ux0+L*.08)} {f(uy+2.4)} C{f(ux0+L*.35)} {f(uy+5.5)} {f(ux0+L*.7)} {f(uy+3.4)} {f(ux1-6)} {f(uy-5)} '
             f'C{f(ux0+L*.7)} {f(uy+7.4)} {f(ux0+L*.35)} {f(uy+9.6)} {f(ux0+L*.08)} {f(uy+2.4)}Z" fill="{SAK_D}"/>')
    o.append(f'<path d="M{f(ux0+L*.12)} {f(uy-.6)} C{f(ux0+L*.3)} {f(uy-2.6)} {f(ux0+L*.5)} {f(uy-2.4)} {f(ux0+L*.62)} {f(uy-2.8)}" '
             f'fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" opacity=".85"/>')
    o.append(plum(x0 + TXT_LEN + glyph / 2 + 8, TXT_Y - 17, 17))
    return "".join(o)


def sparkles():
    pts = [(300, 34, 7, GOLD_L, "tw"), (690, 34, 5, "#ffffff", "tw2"), (936, 28, 6, "#ffffff", "tw3"),
           (1036, 70, 4.5, GOLD, "tw"), (1330, 38, 6, "#ffffff", "tw2"), (1536, 66, 5, GOLD_L, "tw3"),
           (52, 98, 4, "#ffffff", "tw"), (760, 180, 4, "#fffaf0", "tw2"), (900, 204, 5, "#fffaf0", "tw3"),
           (1180, 214, 4, "#ffffff", "tw"), (560, 222, 3.5, "#ffffff", "tw2")]
    return "".join(star4(x, y, r, c, 1, f"{U}-{k}") for x, y, r, c, k in pts)


CREDIT = ("Chibi characters: official Genshin Impact \u201cPaimon\u2019s Paintings\u201d emoji",
          "Genshin Impact \u00a9 HoYoverse \u00b7 non-commercial \u00b7 scenes are my own")


def credit():
    # cream pill behind the two credit lines (same TEXT_BG as the README sheet panels)
    o = [f'<rect x="{W // 2 - 420}" y="{H - 72}" width="840" height="66" rx="22" fill="#fffaf3" fill-opacity=".9" '
         f'stroke="#efe2d6" stroke-width="1.5"/>']
    for line, y in zip(CREDIT, (H - 44, H - 16)):
        a = (f'x="{W // 2}" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="600" '
             f'letter-spacing=".2"')
        o.append(f'<text {a} fill="{CREAM}" stroke="{CREAM}" stroke-width="5" stroke-linejoin="round" opacity=".6">{line}</text>'
                 f'<text {a} fill="{INK_SOFT}">{line}</text>')
    return "".join(o)


# ------------------------------------------------------------------ document
def svg():
    sd, sb = sky()
    cd, cb = clouds()
    wd, wb = water()
    defs = (f'<clipPath id="{U}-clip"><path d="M0 0 H{W} V{H - RX} A{RX} {RX} 0 0 1 {W - RX} {H} H{RX} A{RX} {RX} 0 0 1 0 {H - RX} Z"/></clipPath>'
            f'<radialGradient id="{U}-back"><stop offset="0" stop-color="#fff6ee" stop-opacity=".8"/>'
            f'<stop offset=".5" stop-color="#ffe6ef" stop-opacity=".4"/><stop offset="1" stop-color="#ffe6ef" stop-opacity="0"/>'
            f'</radialGradient>'
            f'<radialGradient id="{U}-pool"><stop offset="0" stop-color="#ffffff" stop-opacity=".85"/>'
            f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>' + sd + cd + wd)
    body = [sb, f'<g id="{U}-far">{far_stratus()}{far_isles()}</g>', cb, sun(), wb, shoal(), sparkles(), thanks(), pets(), boo(),
            credit()]
    label = ("Footer: an anime dusk over calm water. Chibi Hu Tao says thanks on the left and chibi Keqing dozes on a pillow "
             "on the right (official Genshin Impact emoji, © HoYoverse); the words thanks for stopping by sit above the setting sun.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{label}"><title>thanks for stopping by</title>{style()}<defs>{defs}</defs>'
            f'<g clip-path="url(#{U}-clip)">{"".join(body)}</g></svg>')


def build(out_dir=DEFAULT_OUT):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "footer.svg")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(svg())
    return p


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT))
