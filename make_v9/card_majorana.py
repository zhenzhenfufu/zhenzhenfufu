"""v9 project card: Majorana waveforms, signal or background? (pure illustration, 1600x900).

A pastel germanium crystal feeds one bold detector pulse drawn on a taped sheet of graph paper; its
rise is swiped with a marker and inspected through the robot-cat's magnifier. Behind it sits a faint
stack of many unlabelled waveforms and two more sheets; index tabs "signal" (ticked) and "background"
stick out of the sheet. Writes assets/v9/card-majorana.svg."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "mj-"
W, H = 1600, 900
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

# graph sheet
GX, GY, GW, GH = 420, 132, 760, 590
# waveform frame inside the sheet
X0, X1 = 452, 1150      # waveform x range
YB = 600                # baseline
XR = 640                # rise centre
AMP = 300               # pulse height of the bold waveform
# magnifier lens
LX, LY, LR = 640, 452, 86
MAG = 2.0

GRID_MINOR = "#e4e9fb"
GRID_MAJOR = "#cdd6f6"
SHEET = "#fffdf8"
FAINT = "#b4acd6"


# ------------------------------------------------------------------ waveform maths
def pulse_y(x, xr, amp, wr=9.0, tau=520.0, yb=YB, two=None):
    """Detector-like pulse: flat baseline, smooth fast rise at xr, slow exponential tail.
    two=(dx, frac) adds a second step (multi-site look) dx after the first carrying frac of the height."""
    def step(c):
        s = 1 / (1 + math.exp(-(x - c) / wr))
        return s * math.exp(-max(0.0, x - c) / tau)
    if two:
        dx, frac = two
        v = (1 - frac) * step(xr) + frac * step(xr + dx)
    else:
        v = step(xr)
    return yb - amp * v


def wave_path(xr, amp, wr=9.0, tau=520.0, yb=YB, two=None, noise=0.0, seed=0, x0=X0, x1=X1, step=4):
    rnd = random.Random(seed)
    pts = []
    x = x0
    while x <= x1:
        y = pulse_y(x, xr, amp, wr, tau, yb, two) + (rnd.uniform(-noise, noise) if noise else 0)
        pts.append(f"{x:.0f} {y:.1f}")
        # finer sampling through the rise so it stays smooth
        x += 1.5 if abs(x - xr) < 40 or (two and abs(x - xr - two[0]) < 40) else step
    return "M" + " L".join(pts)


# ------------------------------------------------------------------ pieces
def sheet_rect(x, y, w, h, rot, fill=SHEET, op=1.0, shadow="shs"):
    cx, cy = x + w / 2, y + h / 2
    return (f'<g transform="rotate({rot} {cx:.0f} {cy:.0f})" opacity="{op}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" filter="url(#{UID}{shadow})"/>'
            f'</g>')


def grid(x, y, w, h, minor=30, major=150):
    o = []
    v = x + minor
    while v < x + w - 1:
        major_line = (v - x) % major == 0
        o.append(f'<path d="M{v} {y} V{y+h}" stroke="{GRID_MAJOR if major_line else GRID_MINOR}" '
                 f'stroke-width="{2.2 if major_line else 1.6}"/>')
        v += minor
    v = y + minor
    while v < y + h - 1:
        major_line = (v - y) % major == 0
        o.append(f'<path d="M{x} {v} H{x+w}" stroke="{GRID_MAJOR if major_line else GRID_MINOR}" '
                 f'stroke-width="{2.2 if major_line else 1.6}"/>')
        v += minor
    return "".join(o)


def faint_stack():
    """Many unlabelled waveforms: varied rise position, height, rise time, some multi-site."""
    rnd = random.Random(29)
    o = [f'<g fill="none" stroke="{FAINT}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity=".5">']
    for i in range(16):
        xr = XR + rnd.uniform(-70, 120)
        amp = rnd.uniform(120, 330)
        wr = rnd.uniform(6, 16)
        tau = rnd.uniform(380, 900)
        two = (rnd.uniform(26, 60), rnd.uniform(.3, .55)) if i % 4 == 1 else None
        o.append(f'<path d="{wave_path(xr, amp, wr, tau, YB, two, noise=2.2, seed=i + 3, step=6)}"/>')
    o.append('</g>')
    return "".join(o)


def bold_wave():
    return wave_path(XR, AMP, 8.5, 640, YB, noise=1.4, seed=7)


def marker_swipe():
    """Gold highlighter swipe along the rise (drawn under the ink)."""
    y0, y1 = YB + 18, YB - AMP - 14
    return (f'<path d="M{XR-6} {y0} L{XR+10} {y1}" stroke="{GOLD}" stroke-width="54" stroke-linecap="round" opacity=".5"/>'
            f'<path d="M{XR-2} {y0-6} L{XR+12} {y1+8}" stroke="{GOLD}" stroke-width="30" stroke-linecap="round" opacity=".35"/>')


def graph_sheet():
    o = [
        # two more sheets underneath: the unlabelled pile
        sheet_rect(GX + 30, GY + 18, GW, GH, 3.6, "#efe9fc"),
        sheet_rect(GX + 8, GY + 10, GW, GH, -2.6, "#f8f3fe"),
        f'<rect x="{GX}" y="{GY}" width="{GW}" height="{GH}" rx="8" fill="{SHEET}" filter="url(#{UID}shs)"/>',
        f'<clipPath id="{UID}gc"><rect x="{GX}" y="{GY}" width="{GW}" height="{GH}" rx="8"/></clipPath>',
        f'<g clip-path="url(#{UID}gc)">',
        grid(GX, GY, GW, GH),
        faint_stack(),
        marker_swipe(),
        # time axis + baseline tick marks
        pen(f"M{X0-6} {YB+52} H{X1+4}", 3.4, PEN, ' opacity=".9"'),
        pen(f"M{X1-8} {YB+42} l14 10 l-14 10", 3.4, PEN, ' opacity=".9"'),
        f'<path d="{bold_wave()}" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>',
        '</g>',
        # red margin line of the sheet
        f'<path d="M{GX+44} {GY} V{GY+GH}" stroke="{PINK}" stroke-width="2.4" opacity=".7"/>',
        tape(GX + GW / 2, GY + 2, 170, 44, -3, UID, "rainlav"),
        # dashed pen arrow: this pulse -> the "signal" tab
        pen(f"M{XR+150} {YB-AMP-34} Q{XR+300} {GY+66} {GX+GW-58} {GY+102}", 5, PINK_D, ' stroke-dasharray="2 13"'),
        pen(f"M{GX+GW-78} {GY+86} L{GX+GW-56} {GY+102} L{GX+GW-80} {GY+114}", 5, PINK_D),
        # plug where the detector cable enters the sheet; ink lead into the waveform
        pen(f"M{GX+10} {YB} H{X0+2}", 7, INK),
        f'<rect x="{GX-12}" y="{YB-13}" width="26" height="26" rx="7" fill="{PINK}" stroke="{PEN_D}" stroke-width="4"/>',
    ]
    return "\n".join(o)


def index_tabs():
    """Two sticky index tabs poking out of the right edge of the sheet."""
    o = []
    tabs = [(196, "signal", PINK_L, PINK, PINK_D, True), (318, "background", LAV_L, LAV, PEN_D, False)]
    for y, label, fill, edge, ink, ticked in tabs:
        x0 = GX + GW - 40
        w = 372 if label == "background" else 258
        h = 82
        o.append(f'<g filter="url(#{UID}shs)"><path d="M{x0} {y} H{x0+w-18} Q{x0+w} {y} {x0+w} {y+18} V{y+h-18} '
                 f'Q{x0+w} {y+h} {x0+w-18} {y+h} H{x0}Z" fill="{fill}"/></g>')
        o.append(f'<path d="M{x0+40} {y} H{x0+w-18} Q{x0+w} {y} {x0+w} {y+18} V{y+h-18} Q{x0+w} {y+h} {x0+w-18} {y+h} '
                 f'H{x0+40}" fill="none" stroke="{edge}" stroke-width="3.5"/>')
        # sticky glue strip on the part that sits on the sheet
        o.append(f'<rect x="{x0}" y="{y}" width="40" height="{h}" fill="{edge}" opacity=".45"/>')
        bx, by = x0 + 62, y + h / 2 - 17
        o.append(f'<rect x="{bx}" y="{by}" width="34" height="34" rx="7" fill="{WHITE}" stroke="{ink}" stroke-width="4"/>')
        if ticked:
            o.append(pen(f"M{bx+3} {by+14} l11 13 l24 -30", 7, PINK_D))
        o.append(text(bx + 50, y + h / 2 + 12, label, 34, ink, 700))
    return "\n".join(o)


def detector():
    """Stylised p-type point-contact germanium crystal: pastel cylinder on a small cradle, an incoming
    gamma track with a burst inside, and a cable from the point contact to the sheet."""
    cx, top, bot, rx, ry = 236, 360, 560, 92, 24
    o = [f'<defs><linearGradient id="{UID}ge" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="#c9d7ff"/><stop offset=".45" stop-color="#e9e6fd"/>'
         f'<stop offset="1" stop-color="#c3b8f0"/></linearGradient>'
         f'<radialGradient id="{UID}burst"><stop offset="0" stop-color="#fff3d6" stop-opacity=".95"/>'
         f'<stop offset="1" stop-color="#fff3d6" stop-opacity="0"/></radialGradient></defs>']
    # cable: from point contact, down and across to the sheet's baseline
    cab = f"M{cx} {bot+ry+34} C{cx} {bot+120} {cx+90} {YB+2} {GX+4} {YB}"
    o.append(pen(cab, 7, PEN_D))
    o.append(pen(cab, 2.2, WHITE, ' opacity=".8"'))
    # cradle
    o.append(f'<path d="M{cx-rx-14} {bot+6} H{cx+rx+14} L{cx+rx-4} {bot+ry+34} H{cx-rx+4}Z" fill="{LAV}" '
             f'stroke="{PEN_D}" stroke-width="4" stroke-linejoin="round"/>')
    o.append(f'<rect x="{cx-14}" y="{bot+ry+20}" width="28" height="16" rx="5" fill="{PINK}" stroke="{PEN_D}" stroke-width="3.5"/>')
    # crystal body
    body = f"M{cx-rx} {top} V{bot} A{rx} {ry} 0 0 0 {cx+rx} {bot} V{top}"
    o.append(f'<path d="{body} A{rx} {ry} 0 0 0 {cx-rx} {top}Z" fill="url(#{UID}ge)" stroke="{PEN_D}" stroke-width="4.5" stroke-linejoin="round"/>')
    o.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="#f4f1fe" stroke="{PEN_D}" stroke-width="4.5"/>')
    o.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx-26}" ry="{ry-9}" fill="none" stroke="{LAV}" stroke-width="3"/>')
    # facet highlight
    o.append(pen(f"M{cx-rx+22} {top+40} V{bot-30}", 9, WHITE, ' opacity=".85"'))
    o.append(pen(f"M{cx-rx+42} {top+60} V{top+110}", 5, WHITE, ' opacity=".7"'))
    # interaction burst + wavy gamma track coming in from upper left, ending inside the crystal
    bx, by = cx + 14, top + 92
    o.append(f'<circle cx="{bx}" cy="{by}" r="48" fill="url(#{UID}burst)"/>')
    sx, sy = cx - 150, top - 170
    L = math.hypot(bx - sx, by - sy)
    ux, uy = (bx - sx) / L, (by - sy) / L
    pts = []
    for i in range(0, 161):
        t = i / 160 * (L - 34)
        off = 10 * math.sin(t * 2 * math.pi / 34) * min(1, max(0, (L - 34 - t) / 40))
        pts.append(f"{sx + ux*t - uy*off:.1f} {sy + uy*t + ux*off:.1f}")
    o.append(pen("M" + " L".join(pts), 4.4, GOLD_D))
    ex, ey = sx + ux * (L - 22), sy + uy * (L - 22)
    a = math.atan2(uy, ux)
    o.append(pen(f"M{ex - 18*math.cos(a-0.5):.1f} {ey - 18*math.sin(a-0.5):.1f} L{ex:.1f} {ey:.1f} "
                 f"L{ex - 18*math.cos(a+0.5):.1f} {ey - 18*math.sin(a+0.5):.1f}", 4.4, GOLD_D))
    o.append(sparkle(bx, by, 26, GOLD, 1, "tw"))
    o.append(text(cx, bot - 22, "Ge", 36, PEN_D, 800, "middle"))
    return "\n".join(o)


def magnifier_and_mascot():
    """Mascot holding a big magnifier over the rise; lens shows the rise at MAG x."""
    o = []
    # mascot placement: hand at the end of the handle
    ang = math.radians(48)
    hx0, hy0 = LX + (LR + 8) * math.cos(ang), LY + (LR + 8) * math.sin(ang)
    hand_x, hand_y = LX + (LR + 92) * math.cos(ang), LY + (LR + 92) * math.sin(ang)
    s = 1.5
    mx, my = hand_x + 59 * s, hand_y - 25 * s
    o.append(mascot(mx, my, s, bob=False))
    # handle
    o.append(pen(f"M{hx0:.1f} {hy0:.1f} L{hand_x:.1f} {hand_y:.1f}", 15, INK))
    o.append(pen(f"M{hx0 + 22*math.cos(ang):.1f} {hy0 + 22*math.sin(ang):.1f} L{hand_x - 14*math.cos(ang):.1f} {hand_y - 14*math.sin(ang):.1f}",
                 5, PINK, ' opacity=".9"'))
    o.append(f'<circle cx="{hand_x:.1f}" cy="{hand_y:.1f}" r="{8*s:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="{4*s:.1f}"/>')
    # lens content: magnified copy of grid + swipe + bold wave
    t = f"translate({LX} {LY}) scale({MAG}) translate({-LX} {-LY})"
    o.append(f'<clipPath id="{UID}lens"><circle cx="{LX}" cy="{LY}" r="{LR}"/></clipPath>')
    o.append(f'<g clip-path="url(#{UID}lens)"><circle cx="{LX}" cy="{LY}" r="{LR}" fill="{SHEET}"/>'
             f'<g transform="{t}">{grid(GX, GY, GW, GH)}{marker_swipe()}'
             f'<path d="{bold_wave()}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>'
             f'<path d="M{LX-LR+18} {LY-24} A{LR-18} {LR-18} 0 0 1 {LX-20} {LY-LR+18}" fill="none" stroke="{WHITE}" stroke-width="9" stroke-linecap="round" opacity=".9"/>'
             f'</g>')
    o.append(f'<circle cx="{LX}" cy="{LY}" r="{LR}" fill="{BLUE_L}" fill-opacity=".14" stroke="{INK}" stroke-width="10"/>')
    o.append(f'<circle cx="{LX}" cy="{LY}" r="{LR+7}" fill="none" stroke="{WHITE}" stroke-width="3" opacity=".7"/>')
    return "\n".join(o)


def accents():
    px, py, pw, ph = card_paper_rect(W, H)
    o = [
        # small lantern hanging from a string near the top left, soft rain over the detector corner
        pen("M196 96 Q290 134 392 88", 3.2, EDGE),
        f'<circle cx="196" cy="96" r="6" fill="{PINK}" stroke="{PEN_D}" stroke-width="2.4"/>',
        f'<circle cx="392" cy="88" r="6" fill="{PINK}" stroke="{PEN_D}" stroke-width="2.4"/>',
        lantern(292, 111, UID, 1.15),
        f'<clipPath id="{UID}rc"><rect x="{px+40}" y="{py+40}" width="320" height="300"/></clipPath>',
        f'<g clip-path="url(#{UID}rc)">{rain(px + 40, py + 40, 320, 300, 20, 5, 1.6, .7, (20, 34), BLUE)}</g>',
        # puddle under the detector cradle
        puddle(236, 640, .9),
        # bottom-right hanko + sparkles + petals
        hanko(1400, 712, 74, -12),
        star(1300, 520, 20, GOLD, PEN_D, 2.6, cls="tw"),
        sparkle(1436, 480, 14, BLUE_D, .7, "tw2"),
        sparkle(372, 760, 12, GOLD, .9),
        petal(1270, 790, 30, 1.6, .85),
        petal(1494, 590, -30, 1.4, .8),
        petal(340, 120, 60, 1.3, .8),
        star(118, 760, 15, GOLD, PEN_D, 2.2, rot=12),
    ]
    return "\n".join(o)


def svg():
    title = "Signal or background? Majorana detector waveforms"
    desc = ("Illustration: a pastel germanium crystal feeds one bold detector pulse drawn on taped graph paper; "
            "the pulse rise is highlighted with a marker and inspected through a magnifier held by a small "
            "cat-eared robot. A faint stack of many unlabelled waveforms sits behind it, and index tabs "
            "'signal' (ticked) and 'background' stick out of the sheet. Stamped 検証済.")
    body = "\n".join([card_frame(W, H, UID), accents(), detector(), graph_sheet(), index_tabs(),
                      magnifier_and_mascot()])
    return svg_doc(W, H, UID, title, desc, body, k=2.0)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "card-majorana.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


if __name__ == "__main__":
    print("\n".join(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)))
