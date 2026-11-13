"""v9 project card: Night Water Academy (UE5 puzzle game). Pure illustration on the shared card frame:
a taped game-screen window showing a pastel-dusk academy hall over calm moonlit water (reflection,
floating lanterns, crescent moon, gentle rain), with a controller doodle, puzzle pieces, pixel
PRESS START and the robot-cat peeking out from behind the screen under its umbrella.
Writes assets/v9/card-nwa.svg."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "nw-"
W, H = 1600, 900
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

# game-screen window (page coords, before its small tilt)
SX, SY, SW, SH = 112, 106, 904, 640
ROT = -1.6
MASCOT = (1064, 642, 1.22)           # head centre + scale of the peeking robot-cat
BEZ, BAR = 16, 42                     # white bezel, title-bar height
VW, VH = SW - 2 * BEZ, SH - 2 * BEZ - BAR   # scene viewport (868 x 526)
WL = 356                              # waterline in scene coords

# extra local colours (all lavender / pink / gold / blue hues, no green)
SKY_T, SKY_M, SKY_B = "#b3a7ec", "#cdc1f4", "#f6d9e8"
MTN1, MTN2 = "#c8bcef", "#d9cdf4"
WAT_T, WAT_B = "#e9d8f1", "#c3c4f2"
ROOF, ROOF_L = "#7d74c8", "#9c95dc"
COL = "#e58db1"                       # hall columns (soft vermilion-pink)
GLOW = "#ffe3a6"                      # lit windows


def local_defs():
    p = UID
    return f"""<defs>
  <linearGradient id="{p}nsky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY_T}"/><stop offset=".55" stop-color="{SKY_M}"/><stop offset="1" stop-color="{SKY_B}"/>
  </linearGradient>
  <linearGradient id="{p}nwat" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{WAT_T}"/><stop offset="1" stop-color="{WAT_B}"/>
  </linearGradient>
  <radialGradient id="{p}glow"><stop offset="0" stop-color="#ffe2a8" stop-opacity=".95"/><stop offset="1" stop-color="#ffe2a8" stop-opacity="0"/></radialGradient>
  <filter id="{p}blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.4"/></filter>
</defs>
<style>
  .blink{{animation:blink 1.4s steps(2,start) infinite}}
  @keyframes blink{{to{{visibility:hidden}}}}
  .rise{{animation:rise 7s ease-in-out infinite alternate}}
  @keyframes rise{{from{{transform:translate(0,0)}}to{{transform:translate(4px,-14px)}}}}
  .bobw{{animation:bobw 3.4s ease-in-out infinite alternate}}
  @keyframes bobw{{from{{transform:translate(0,0)}}to{{transform:translate(0,3px)}}}}
  @media (prefers-reduced-motion: reduce){{.blink,.rise,.bobw{{animation:none}}}}
</style>"""


# ------------------------------------------------------------------ scene pieces (scene coords 0..VW, 0..VH)
def hall():
    """Two-storey academy hall with upturned eaves, local coords: centre x=0, waterline y=0."""
    o = []
    # stilts into the water
    for x in range(-150, 151, 30):
        o.append(f'<rect x="{x-3}" y="-18" width="6" height="20" fill="{EDGE}"/>')
    # deck + balustrade
    o.append(f'<rect x="-172" y="-32" width="344" height="15" rx="3" fill="#efe9fb" stroke="{INK}" stroke-width="3"/>')
    o.append(pen("M-162 -48 H162", 3, PEN_D))
    o.append(pen(" ".join(f"M{x} -48 V-32" for x in range(-160, 161, 20)), 2.4, PEN_D))
    # ground-floor body
    o.append(f'<rect x="-112" y="-114" width="224" height="82" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>')
    # windows (left / right bays) + glowing doors (centre)
    for x0 in (-98, 64):
        o.append(f'<rect x="{x0}" y="-98" width="34" height="38" rx="2" fill="{GLOW}" stroke="{PEN_D}" stroke-width="2.4"/>')
        o.append(pen(f"M{x0+17} -98 V-60 M{x0} -79 H{x0+34}", 1.8, PEN_D, ' opacity=".7"'))
    o.append(f'<rect x="-44" y="-104" width="88" height="72" fill="{GLOW}" stroke="{PEN_D}" stroke-width="2.4"/>')
    o.append(pen("M0 -104 V-32 M-22 -104 V-32 M22 -104 V-32 M-44 -80 H44 M-44 -56 H44", 1.8, PEN_D, ' opacity=".6"'))
    o.append(f'<ellipse cx="0" cy="-66" rx="70" ry="40" fill="url(#{UID}glow)" opacity=".7"/>')
    # columns
    for x in (-112, -58, 58, 112):
        o.append(f'<rect x="{x-6}" y="-114" width="12" height="82" fill="{COL}" stroke="{INK}" stroke-width="2.6"/>')
    # lower roof with flared eaves
    lower = ("M-196 -142 Q-170 -114 -122 -114 H122 Q170 -114 196 -142 Q160 -132 134 -146 L100 -168 H-100 "
             "L-134 -146 Q-160 -132 -196 -142Z")
    o.append(f'<path d="{lower}" fill="{ROOF}" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    o.append(pen("M-150 -128 Q-130 -124 -116 -124 H116 Q130 -124 150 -128", 2.6, ROOF_L))
    o.append(pen("M-196 -142 q-4 -10 6 -14 M196 -142 q4 -10 -6 -14", 3.2, INK))
    # upper storey
    o.append(f'<rect x="-70" y="-206" width="140" height="40" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>')
    for x0 in (-56, -14, 28):
        o.append(f'<rect x="{x0}" y="-198" width="28" height="24" rx="2" fill="{GLOW}" stroke="{PEN_D}" stroke-width="2.2"/>')
    for x in (-70, 70):
        o.append(f'<rect x="{x-5}" y="-206" width="10" height="40" fill="{COL}" stroke="{INK}" stroke-width="2.4"/>')
    # upper roof
    upper = ("M-140 -218 Q-118 -196 -82 -196 H82 Q118 -196 140 -218 Q110 -210 92 -222 L60 -250 H-60 L-92 -222 "
             "Q-110 -210 -140 -218Z")
    o.append(f'<path d="{upper}" fill="{ROOF}" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    o.append(pen("M-104 -206 Q-92 -204 -80 -204 H80 Q92 -204 104 -206", 2.4, ROOF_L))
    o.append(pen("M-140 -218 q-4 -10 6 -14 M140 -218 q4 -10 -6 -14", 3.2, INK))
    # ridge + curled ridge ends + gold finial
    o.append(pen("M-64 -251 H64", 5, INK))
    o.append(pen("M-64 -251 q-10 -4 -6 -16 q4 -6 10 -2 M64 -251 q10 -4 6 -16 q-4 -6 -10 -2", 3.2, INK))
    o.append(f'<circle cx="0" cy="-258" r="6" fill="{GOLD}" stroke="{INK}" stroke-width="2.4"/>')
    # blank gold plaque between the roofs
    o.append(f'<rect x="-22" y="-164" width="44" height="14" rx="2" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>')
    return "".join(o)


def eave_lanterns():
    """Small lanterns hanging from the lower eave tips (hall-local coords)."""
    return lantern(-186, -136, UID, 0.42, glow=True) + lantern(186, -136, UID, 0.42, glow=True)


def water_lantern(x, y, s=1.0, cls=""):
    """Floating river lantern (paper box on a little boat) with glow; (x,y) = waterline centre."""
    c = f' class="{cls}"' if cls else ""
    return (f'<g transform="translate({x} {y}) scale({s})"><g{c}>'
            f'<ellipse cx="0" cy="-12" rx="40" ry="26" fill="url(#{UID}glow)"/>'
            f'<path d="M-16 -2 H16 L11 6 H-11Z" fill="{PINK}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<rect x="-10" y="-24" width="20" height="22" rx="3" fill="#fff1d2" stroke="{INK}" stroke-width="2.4"/>'
            f'<path d="M-10 -14 H10" stroke="{GOLD_D}" stroke-width="1.8"/>'
            f'<path d="M-13 -24 H13" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>'
            # reflection streak
            f'<path d="M-8 10 H8 M-5 17 H5" stroke="{GOLD}" stroke-width="3" stroke-linecap="round" opacity=".7"/></g>')


def sky_lantern(x, y, s=1.0, cls="rise"):
    return (f'<g transform="translate({x} {y}) scale({s})"><g class="{cls}">'
            f'<circle cx="0" cy="0" r="30" fill="url(#{UID}glow)"/>'
            f'<path d="M-10 -14 H10 L13 12 H-13Z" fill="#fff1d2" stroke="{PEN_D}" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<path d="M-6 12 H6" stroke="{GOLD_D}" stroke-width="3" stroke-linecap="round"/></g></g>')


def pixel_hearts(x, y, c=4.6, count=3):
    rows = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    o = []
    for k in range(count):
        hx = x + k * (8 * c + 6)
        cells = "".join(f'<rect x="{hx + i*c:.1f}" y="{y + j*c:.1f}" width="{c:.1f}" height="{c:.1f}"/>'
                        for j, r in enumerate(rows) for i, ch in enumerate(r) if ch == "1")
        fill = PINK if k < count - 1 else WHITE
        o.append(f'<g fill="{fill}" stroke="{PINK_D}" stroke-width="1.2">{cells}</g>')
    return "".join(o)


def scene():
    o = [f'<rect width="{VW}" height="{VH}" fill="url(#{UID}nsky)"/>']
    # moon with halo + a few stars
    mx, my = 690, 104
    o.append(f'<circle cx="{mx}" cy="{my}" r="92" fill="url(#{UID}halo)"/>')
    moon = f"M{mx} {my-40} A40 40 0 1 0 {mx+34} {my+21} A31 31 0 1 1 {mx} {my-40}Z"
    o.append(f'<path d="{moon}" fill="#fff6dc" stroke="{GOLD_D}" stroke-width="2.4" stroke-opacity=".6"/>')
    for sx, sy, r, cls in [(120, 66, 9, "tw"), (232, 140, 6, ""), (548, 54, 7, "tw2"), (800, 190, 6, ""), (420, 40, 5, "")]:
        o.append(sparkle(sx, sy, r, WHITE, .95, cls))
    # soft far mountains
    o.append(f'<g filter="url(#{UID}blur)">'
             f'<path d="M0 {WL} V230 Q60 196 120 214 Q190 160 270 206 Q320 228 360 {WL}Z" fill="{MTN1}"/>'
             f'<path d="M500 {WL} Q560 230 640 236 Q720 196 790 224 Q840 240 {VW} 228 V{WL}Z" fill="{MTN1}"/>'
             f'<path d="M0 {WL} V276 Q90 250 180 270 Q260 284 300 {WL}Z M560 {WL} Q640 272 720 270 Q800 262 {VW} 280 V{WL}Z" fill="{MTN2}"/></g>')
    # sky lanterns drifting up
    o.append(sky_lantern(612, 236, 0.95))
    o.append(sky_lantern(806, 292, 0.7))
    o.append(sky_lantern(64, 214, 0.75))
    # water
    o.append(f'<rect y="{WL}" width="{VW}" height="{VH-WL}" fill="url(#{UID}nwat)"/>')
    hx, hs = 340, 1.12
    hall_g = f'<g transform="translate({hx} {WL}) scale({hs})">{hall()}</g>'
    # reflection (mirrored about the waterline, clipped to water)
    o.append(f'<clipPath id="{UID}wclip"><rect y="{WL}" width="{VW}" height="{VH-WL}"/></clipPath>')
    o.append(f'<g clip-path="url(#{UID}wclip)" opacity=".17"><g transform="translate(0 {2*WL}) scale(1 -1)">{hall_g}</g></g>')
    # moon reflection
    o.append(pen(" ".join(f"M{mx-w/2:.0f} {y} h{w}" for y, w in [(WL+20, 54), (WL+44, 40), (WL+68, 46), (WL+94, 28), (WL+120, 34), (WL+148, 18)]),
                 4, "#fff3d0", ' opacity=".9"'))
    # ripple lines across the reflection
    o.append(pen(" ".join(f"M{a} {y} h{b}" for a, y, b in [(150, WL+38, 90), (290, WL+60, 120), (430, WL+26, 60),
                                                           (200, WL+100, 70), (360, WL+128, 110), (36, WL+120, 60),
                                                           (740, WL+86, 70), (600, WL+176, 90), (330, WL+186, 70)]),
                 3, WHITE, ' opacity=".7"'))
    # the hall itself + eave lanterns
    o.append(hall_g)
    o.append(f'<g transform="translate({hx} {WL}) scale({hs})">{eave_lanterns()}</g>')
    # floating lanterns on the water
    for x, y, s, cls in [(84, 420, 1.25, "bobw"), (626, 404, 1.1, ""), (514, 500, 1.35, "bobw"), (792, 482, 1.2, ""),
                         (214, 528, 1.3, "")]:
        o.append(water_lantern(x, y, s, cls))
    # gentle rain
    o.append(rain(0, 0, VW, VH, 36, 7, 1.2, .42, (22, 40)))
    # HUD: pixel hearts
    o.append(pixel_hearts(22, 20))
    return "\n".join(o)


# ------------------------------------------------------------------ screen window
def screen():
    cx, cy = SX + SW / 2, SY + SH / 2
    vx, vy = SX + BEZ, SY + BEZ + BAR
    o = [f'<g transform="rotate({ROT} {cx} {cy})">',
         f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="20" fill="{WHITE}" filter="url(#{UID}sh)"/>',
         # title bar: lavender strip with three window dots
         f'<rect x="{SX+BEZ}" y="{SY+BEZ}" width="{VW}" height="{BAR-8}" rx="8" fill="{LAV_L}"/>']
    for i, c in enumerate((PINK, GOLD, BLUE)):
        o.append(f'<circle cx="{SX+BEZ+24+i*28}" cy="{SY+BEZ+17}" r="8" fill="{c}" stroke="{PEN_D}" stroke-width="2"/>')
    o.append(pen(f"M{SX+SW-BEZ-150} {SY+BEZ+17} h56 M{SX+SW-BEZ-80} {SY+BEZ+17} h56", 5, LAV))
    o.append(f'<clipPath id="{UID}vclip"><rect x="{vx}" y="{vy}" width="{VW}" height="{VH}" rx="8"/></clipPath>')
    o.append(f'<g clip-path="url(#{UID}vclip)"><g transform="translate({vx} {vy})">{scene()}</g></g>')
    o.append(f'<rect x="{vx}" y="{vy}" width="{VW}" height="{VH}" rx="8" fill="none" stroke="{INK}" stroke-opacity=".12" stroke-width="2"/>')
    # washi tape on the two top corners
    o.append(tape(SX + SW - 30, SY + 6, 150, 40, 36, UID, "sakura"))
    o.append(tape(SX + 26, SY + SH - 8, 150, 40, 36, UID, "rainlav"))
    o.append('</g>')
    return "\n".join(o)


# ------------------------------------------------------------------ side doodles
PIX = {
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    ">": ["1000", "1100", "1110", "1111", "1110", "1100", "1000"],
}


def pixel_text(x, y, s, c, fill, shadow=LAV):
    """Hand-built 5x7 pixel caps (font-independent); (x,y) = top-left, c = cell size."""
    o, sh, cx = [], [], x
    for ch in s:
        if ch == " ":
            cx += 4 * c
            continue
        rows = PIX[ch]
        cells = "".join(f'<rect x="{cx + i*c:.1f}" y="{y + j*c:.1f}" width="{c:.1f}" height="{c:.1f}"/>'
                        for j, r in enumerate(rows) for i, b in enumerate(r) if b == "1")
        o.append(cells)
        cx += (len(rows[0]) + 1) * c
    body = "".join(o)
    return (f'<g fill="{shadow}" transform="translate({c*0.6:.1f} {c*0.6:.1f})">{body}</g>'
            f'<g fill="{fill}">{body}</g>'), cx - x


def puzzle_piece(x, y, s=1.0, rot=0, fill=PINK, under=PINK_L):
    """Jigsaw piece (knobs top + right, socket bottom); (x,y) = centre of the square body (100x100 local)."""
    d = ("M-50 -50 H-15 C-15 -56 -20 -60 -20 -66 C-20 -76 -10 -80 0 -80 C10 -80 20 -76 20 -66 C20 -60 15 -56 15 -50 "
         "H50 V-15 C56 -15 60 -20 66 -20 C76 -20 80 -10 80 0 C80 10 76 20 66 20 C60 20 56 15 50 15 V50 H15 "
         "C15 44 20 40 20 34 C20 24 10 20 0 20 C-10 20 -20 24 -20 34 C-20 40 -15 44 -15 50 H-50Z")
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="{d}" transform="translate(7 7)" fill="{under}"/>'
            f'<path d="{d}" fill="{fill}" stroke="{PEN_D}" stroke-width="{3.6/1:.1f}" stroke-linejoin="round"/>'
            f'<path d="M-36 -36 q10 -4 18 -2" fill="none" stroke="{WHITE}" stroke-width="4" stroke-linecap="round" opacity=".8"/></g>')


def side():
    o = []
    # controller + sparkles
    o.append(doodle_controller(1160, 142, 1.72))
    o.append(sparkle(1452, 124, 14, GOLD, 1, "tw"))
    o.append(sparkle(1100, 112, 9, BLUE_D, .6))
    # PRESS START in pixel caps, arrow blinks
    arrow, aw = pixel_text(1072, 330, ">", 6, PINK_D, PINK_L)
    words, ww = pixel_text(1072 + aw + 10, 330, "PRESS START", 6, PINK_D, PINK_L)
    o.append(f'<g class="blink">{arrow}</g>{words}')
    # puzzle pieces (pink + blue, about to click together)
    o.append(puzzle_piece(1330, 566, 0.8, -8, PINK, PINK_L))
    o.append(puzzle_piece(1468, 520, 0.68, 14, BLUE, BLUE_L))
    o.append(pen("M1408 500 q8 -8 18 -6 M1412 520 q10 -3 16 2", 3, PEN, ' opacity=".8"'))
    return "\n".join(o)


# umbrella canopy outline copied from lib.mascot (local coords) so we can back it with a pale tint on cream paper
CANOPY = ("M-50,-96 C-46,-152 -4,-170 48,-170 C100,-170 142,-152 146,-96 Q122,-106 97,-96 Q72,-106 48,-96 "
          "Q24,-106 -1,-96 Q-26,-106 -50,-96Z")


def peeking_mascot():
    """Robot-cat with umbrella peeking out from behind the screen's right edge, on a little puddle.
    Drawn BEFORE the screen so the screen overlaps its left rim; a paw grips the screen edge (drawn after)."""
    mx, my, ms = MASCOT
    tint = (f'<g transform="translate({mx} {my}) scale({ms})"><g class="bob"><g transform="rotate(-10 48 14)">'
            f'<path d="{CANOPY}" fill="{BLUE_L}" fill-opacity=".9"/></g></g></g>')
    drops = pen(" ".join(f"M{mx+dx} {my+dy} l-3 16" for dx, dy in [(-26, -230), (86, -240), (160, -204)]),
                3, BLUE_D, ' opacity=".55"')
    return "\n".join([puddle(mx + 30, my + 76, 0.6), drops, tint, mascot(mx, my, ms, umbrella=True, face="happy")])


def accents():
    return "\n".join([
        hanko(1336, 752, 66, -14),
        petal(1506, 300, 30, 1.1, .85),
        petal(1470, 790, -20, 1.0, .8),
        petal(640, 806, 60, 1.0, .8),
        petal(82, 470, -30, .9, .7),
        sparkle(1206, 800, 9, GOLD, .9, "tw2"),
        pen("M300 806 q14 -8 28 0 t28 0 t28 0 M318 822 q14 -8 28 0 t28 0", 3, BLUE_D, ' opacity=".5"'),
    ])


def svg():
    title = "Night Water Academy 夜水书院 — illustration"
    desc = ("A taped game-screen window on a dotted journal page: a Chinese academy hall with upturned eaves stands "
            "over calm moonlit water at a pastel dusk, with its soft reflection, floating lanterns, a crescent moon "
            "and gentle rain. Beside it: a game controller doodle, two puzzle pieces and PRESS START in pixel caps; "
            "the small robot-cat peeks out from behind the screen under a clear umbrella. Stamped 検証済.")
    body = "\n".join([local_defs(), card_frame(W, H, UID), peeking_mascot(), screen(), side(), accents()])
    return svg_doc(W, H, UID, title, desc, body, k=2.0)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "card-nwa.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


if __name__ == "__main__":
    print("\n".join(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)))
