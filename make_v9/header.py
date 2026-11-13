"""v9 header: washi journal page on the icon-wallpaper margin, plain typeset intro on the left,
a taped polaroid of a rainy Tokyo alley (雨宿り) on the right. Writes assets/v9/header.svg."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "hd-"
W, H = 1600, 545
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

# paper panel
PX, PY, PW, PH = 34, 30, W - 68, H - 60
X0 = 122            # content left edge
VX = X0 + 108       # value column
FS_ROW = 23         # row font size: the Now line (~960px wide at 23px Hiragino) must end well before the polaroid
POL_CX, POL_CY, POL_ROT = 1396, 262, 3.0


def page():
    o = [margin_bg(W, H, UID),
         paper(PX, PY, PW, PH, UID, rx=16),
         # margin rule + punched holes (journal page)
         f'<line x1="92" y1="{PY}" x2="92" y2="{PY + PH}" stroke="{PINK}" stroke-width="2.4" opacity=".7"/>']
    for i in range(8):
        y = 72 + i * 58
        o.append(f'<circle cx="62" cy="{y}" r="9" fill="#ddd6f6"/>'
                 f'<path d="M54 {y-4} a9 9 0 0 1 16 0" fill="none" stroke="#c4bbe8" stroke-width="2"/>')
    o.append(tape(66, 40, 140, 38, -32, UID, "rain"))
    o.append(tape(70, H - 38, 136, 36, 30, UID, "rainlav"))
    return "\n".join(o)


def content():
    o = ['<g class="f">',
         text(X0, 96, "DATA SCIENCE · UC SAN DIEGO · CLASS OF 2029", 22, MUTE, 600, ls=5),
         f'<text x="{X0 - 4}" y="196" font-size="96" font-weight="800" letter-spacing="-1" fill="{INK}">Zhen Wang'
         f'<tspan dx="24" font-size="50" font-weight="700" letter-spacing="2" fill="{PINK_D}">王臻</tspan></text>',
         text(X0, 258, "I build AI agents — and the checks that keep them honest.", 31, INK2, 400)]
    rows = [("Now", "Rare AI Lab (Prof. Aobo Li) · SIDERIUS, an open-source auto-ML agent for science"),
            ("Before", "AI Agent Development Intern · Pfizer China R&D (2026)"),
            ("Also", "I make games · Night Water Academy 夜水书院 (UE5)")]
    for i, (lab, val) in enumerate(rows):
        y = 342 + i * 48
        o.append(text(X0, y, lab, FS_ROW, PINK_D, 700))
        o.append(text(VX, y, val, FS_ROW, INK, 400))
    o.append('</g>')
    return "\n".join(o)


def doodles():
    """Light ink doodles in the paper margins, all clear of the text block."""
    return "\n".join([
        doodle_constellation(1062, 118, 0.85),
        doodle_moon(1172, 78, 0.62),
        sparkle(1206, 150, 7, BLUE_D, .55),
        doodle_wave(912, 488, 240, amp=10, scale=1.0, op=.7),
        petal(1236, 330, 20, .9),
        petal(1580, 250, 50, .8, .8),
        petal(1192, 500, -30, .8, .75),
        petal(22, 300, 40, .8, .7),
        sparkle(1240, 470, 8, GOLD, .9, "tw"),
    ])


def polaroid_block():
    o = [polaroid(POL_CX, POL_CY, UID, inner=alley_scene(0, 0, UID), caption="雨宿り", rot=POL_ROT)]
    bx, by = polaroid_point(POL_CX, POL_CY, 143, 167, rot=POL_ROT)
    o.append(hanko(bx - 26, by - 16, 44, -14))
    return "\n".join(o)


def svg():
    title = "Zhen Wang 王臻 — Data Science · UC San Diego · Class of 2029"
    desc = ("I build AI agents — and the checks that keep them honest. "
            "Now: Rare AI Lab (Prof. Aobo Li) · SIDERIUS, an open-source auto-ML agent for science. "
            "Before: AI Agent Development Intern · Pfizer China R&D (2026). "
            "Also: I make games · Night Water Academy 夜水书院 (UE5). "
            "Drawn as a dotted journal page with washi tape and a taped polaroid of a rainy alley, "
            "where a small cat-eared robot stands under a clear umbrella; stamped 検証済.")
    body = "\n".join([page(), doodles(), polaroid_block(), content()])
    return svg_doc(W, H, UID, title, desc, body, k=1.0, rx=24)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "header.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


if __name__ == "__main__":
    print("\n".join(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)))
