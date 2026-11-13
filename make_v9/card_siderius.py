"""v9 SIDERIUS card (pure illustration, 1600x900): the agent loop around the robot-cat on a washi
journal page. question star -> experiment bars -> score curve -> magnifier check, dashed arrows
closing the loop, a waveform (the data) feeding the question, 検証済 hanko, and a small rainy-alley
accent (hanging エージェント sign, paper lantern, light rain). Writes assets/v9/card-siderius.svg."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *  # noqa: E402,F401,F403

UID = "sd-"
W, H = 1600, 900
OUT_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "v9")

CX, CY = 800, 452          # loop centre
S = 2.1                    # icon scale (icons are drawn at node radius 36, as in the v8 sketch)
R = 36 * S                 # node radius on the page
NODES = {"question": (430, CY), "experiment": (CX, 222), "score": (1170, CY), "check": (CX, 682)}
ORDER = ["question", "experiment", "score", "check", "question"]
FILL = {"question": GOLD, "experiment": PINK_L, "score": BLUE_L, "check": LAV_L}


def arrowhead(x, y, ang, s=S, col=PINK_D):
    return (f'<path d="M-7 -7 L5 0 L-7 7" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({n(s)})" '
            f'fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


def ring():
    """Faint dotted star-chart ring through the four nodes."""
    rx, ry = 370, 230
    return (f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{PEN}" stroke-width="2.6" '
            f'stroke-dasharray="2 14" stroke-linecap="round" opacity=".55"/>')


def edges():
    """Dashed edges bowing outward, pink arrowhead at each midpoint (clockwise)."""
    o = []
    for a, b in zip(ORDER, ORDER[1:]):
        (x1, y1), (x2, y2) = NODES[a], NODES[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ox, oy = mx - CX, my - CY
        L = math.hypot(ox, oy) or 1
        qx, qy = mx + ox / L * 78, my + oy / L * 78
        o.append(pen(f"M{x1} {y1} Q{qx:.0f} {qy:.0f} {x2} {y2}", 5.2, PEN_D, ' stroke-dasharray="6 17"'))
        ax, ay = 0.25 * x1 + 0.5 * qx + 0.25 * x2, 0.25 * y1 + 0.5 * qy + 0.25 * y2
        o.append(arrowhead(ax, ay, math.degrees(math.atan2(y2 - y1, x2 - x1))))
    return "\n".join(o)


def node_disc(x, y, fill):
    return (f'<circle cx="{x}" cy="{y}" r="{R + 10:.1f}" fill="{CREAM}"/>'
            f'<circle cx="{x + 4*S:.1f}" cy="{y + 4*S:.1f}" r="{R:.1f}" fill="{fill}" fill-opacity=".9"/>'
            f'<circle cx="{x}" cy="{y}" r="{R:.1f}" fill="none" stroke="{PEN_D}" stroke-width="{2.8*S:.1f}"/>')


def icon(kind):
    """Node icons in local coords (node centre = 0,0, radius 36), scaled by S."""
    x, y = NODES[kind]
    if kind == "question":       # the research question: a white star that twinkles
        g = f'<g class="tw">{star(0, 0, 20, WHITE, PEN_D, 2.6)}</g>'
    elif kind == "experiment":   # an experiment run: bar chart
        g = "".join(f'<rect x="{-20 + i*14}" y="{16 - hh}" width="10" height="{hh}" rx="2" fill="{c}" '
                    f'stroke="{PEN_D}" stroke-width="1.9"/>' for i, (hh, c) in enumerate([(14, BLUE), (24, LAV), (32, PINK)]))
        g += pen("M-24 17 H24", 2.3)
    elif kind == "score":        # the score: a falling loss curve on tiny axes
        g = pen("M-20 -20 V18 H22", 2.4) + pen("M-16 -14 C-8 8 2 10 20 10", 3.4, BLUE_D)
    else:                        # validity check: magnifier with a pink tick
        g = (f'<circle cx="-4" cy="-4" r="14" fill="{WHITE}" stroke="{PEN_D}" stroke-width="3"/>'
             + pen("M6 6 l11 11", 5, PEN_D) + pen("M-10 -4 l4 5 l9 -10", 3.2, PINK_D))
    return f'<g transform="translate({x} {y}) scale({n(S)})">{g}</g>'


def nodes():
    return "\n".join(node_disc(*NODES[k], FILL[k]) + icon(k) for k in ["question", "experiment", "score", "check"])


def centre():
    """Mascot in the middle of the loop, standing on a small puddle, a couple of sparkles."""
    return "\n".join([
        puddle(CX, 556, 0.74),
        mascot(CX, 456, 1.6),
        sparkle(CX + 124, 366, 17, GOLD, 1, "tw"),
        sparkle(CX - 128, 516, 11, BLUE_D, .7, "tw2"),
    ])


def data_feed():
    """Chirp waveform (the dataset) at bottom-left, dashed arrow feeding it up into the question node."""
    qx, qy = NODES["question"]
    a = math.radians(108)
    ex, ey = qx + math.cos(a) * (R + 16), qy + math.sin(a) * (R + 16)   # just below the node
    c2x, c2y = ex + 4, ey + 92
    ang = math.degrees(math.atan2(ey - c2y, ex - c2x))
    return "\n".join([
        doodle_wave(104, 742, 250, amp=17, scale=2.0, col=BLUE_D, op=.85, cycles=(2.4, 5)),
        pen(f"M370 742 C424 742 {c2x:.0f} {c2y:.0f} {ex:.0f} {ey:.0f}", 5.2, PEN_D, ' stroke-dasharray="6 17"'),
        arrowhead(ex, ey, ang),
    ])


def vsign_tate(x, y, chars, scale, ink, edge):
    """Vertical sign; lib.vsign already turns the long-vowel mark ー upright (tategaki)."""
    return vsign(x, y, chars, scale, ink, edge, size=28, pad=11)


def alley_accent():
    """Right column: a pen-drawn wire with a hanging エージェント sign and a paper lantern, light rain."""
    cid = f"{UID}rainclip"
    sw, sh_ = vsign_size("エージェント", 28, 11)
    ss = 1.36
    sx = 1394
    o = [f'<clipPath id="{cid}"><rect x="1262" y="132" width="270" height="440" rx="20"/></clipPath>',
         f'<g clip-path="url(#{cid})">{rain(1262, 132, 270, 440, 22, 7, 2.0, .32, (16, 28), PEN)}</g>',
         pen("M1268 168 Q1372 206 1516 158", 3.2, EDGE),
         f'<circle cx="1268" cy="168" r="6" fill="{PINK}" stroke="{PEN_D}" stroke-width="2.4"/>',
         f'<circle cx="1516" cy="158" r="6" fill="{PINK}" stroke="{PEN_D}" stroke-width="2.4"/>',
         lantern(1314, 178, UID, 1.45),
         vsign_tate(sx, 198, "エージェント", ss, INK, BLUE_D)]
    return "\n".join(o)


def scatter():
    """Small stars, petals; kept to the quiet corners."""
    return "\n".join([
        star(232, 214, 20, GOLD, PEN_D, 3.2),
        star(612, 120, 12, GOLD, PEN_D, 2.6, cls="tw2"),
        star(1062, 122, 14, GOLD, PEN_D, 2.6),
        star(1236, 640, 11, GOLD, PEN_D, 2.4),
        sparkle(176, 440, 12, BLUE_D, .6),
        petal(262, 584, 30, 2.0, .9),
        petal(1182, 786, -24, 1.7, .85),
        petal(1012, 126, 40, 1.4, .75),
    ])


def svg():
    title = "SIDERIUS — agent loop illustration"
    desc = ("Illustration on a dotted journal page: a small cat-eared robot stands at the centre of a loop of four "
            "inked circles — a star for the question, a bar chart for the experiment, a falling curve for the score "
            "and a magnifier with a tick for the validity check — joined by dashed arrows. A waveform feeds the loop "
            "from the lower left; a hanging エージェント sign and a paper lantern sit in light rain on the right, "
            "and a round 検証済 stamp marks the lower right corner.")
    body = "\n".join([card_frame(W, H, UID), alley_accent(), ring(), edges(), nodes(), centre(), data_feed(),
                      scatter(), hanko(1398, 724, 76, -14)])
    return svg_doc(W, H, UID, title, desc, body, k=2.0)


def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "card-siderius.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    return [path]


def main():
    print("\n".join(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT)))


if __name__ == "__main__":
    main()
