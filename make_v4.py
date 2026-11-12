"""Build assets/v4/*.svg: the profile header, four project cards and a footer
strip, drawn as plain SVG. The palette and motifs (lavender sky, mint glass HUD
panels with chamfered corners, a glowing check, waveforms, node graphs, sakura
petals) are taken from the ChatGPT HUD explorations, but nothing here is a
generated image.

    python3 make_v4.py
"""
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "assets/v4"
OUT.mkdir(parents=True, exist_ok=True)

SANS = "'Hiragino Sans','Segoe UI',system-ui,-apple-system,'PingFang SC','Noto Sans CJK SC',sans-serif"

# palette sampled from the chosen illustrations
SKY_TOP, SKY_MID, SKY_LOW = "#ebe4fb", "#ddd6f6", "#f7e9f2"
LAV, LAV_DEEP = "#b6b5e9", "#8f8bd0"
INK, INK_SOFT = "#34305e", "#625f92"
MINT, MINT_DEEP, MINT_SOFT = "#6fdcae", "#2fae7c", "#c9f3e1"
PINK, PINK_DEEP, PINK_SOFT = "#f4a9c4", "#d9608e", "#fbdbe8"
WHITE = "#ffffff"

STYLE = f"""<style>
text{{font-family:{SANS}}}
.petal{{animation:drift 14s ease-in-out infinite}}
@keyframes drift{{0%,100%{{transform:translate(0,0) rotate(0deg)}}50%{{transform:translate(-14px,10px) rotate(24deg)}}}}
.glow{{animation:glow 3.6s ease-in-out infinite}}
@keyframes glow{{0%,100%{{opacity:.35}}50%{{opacity:.9}}}}
.kira{{transform-box:fill-box;transform-origin:center;animation:kira 3.2s ease-in-out infinite}}
@keyframes kira{{0%,100%{{opacity:.25;transform:scale(.55)}}50%{{opacity:1;transform:scale(1)}}}}
@media (prefers-reduced-motion: reduce){{.petal,.glow,.kira{{animation:none}}}}
</style>"""


def defs(uid):
    return f"""<defs>
  <linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY_TOP}"/><stop offset=".6" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_LOW}"/>
  </linearGradient>
  <linearGradient id="glass{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{WHITE}" stop-opacity=".72"/><stop offset="1" stop-color="{WHITE}" stop-opacity=".32"/>
  </linearGradient>
  <linearGradient id="bar{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{MINT_SOFT}" stop-opacity=".5"/>
  </linearGradient>
  <filter id="blur{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="cloud{uid}" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>"""


def chamfer(x, y, w, h, c=16):
    """Glass panel outline with the top-left and bottom-right corners cut."""
    return (f"M{x+c},{y} H{x+w} V{y+h-c} L{x+w-c},{y+h} H{x} V{y+c} Z")


def panel(uid, x, y, w, h, c=16, accent=MINT):
    d = chamfer(x, y, w, h, c)
    return (f'<path d="{d}" fill="url(#glass{uid})" stroke="{accent}" stroke-width="2" stroke-opacity=".85"/>'
            f'<path d="M{x+c+10},{y+7} H{x+c+64}" stroke="{accent}" stroke-width="4" stroke-linecap="round" opacity=".8"/>'
            f'<circle cx="{x+w-16}" cy="{y+14}" r="3.5" fill="{PINK}"/>')


def petal(x, y, s, rot, delay, op=.9):
    return (f'<g class="petal" style="animation-delay:-{delay}s;transform-origin:{x}px {y}px">'
            f'<path transform="translate({x},{y}) rotate({rot}) scale({s})" fill="{PINK_SOFT}" stroke="{PINK}" '
            f'stroke-width=".8" opacity="{op}" d="M0,-10 C7,-10 10,-2 7,5 C5,9 2,11 0,8 C-2,11 -5,9 -7,5 C-10,-2 -7,-10 0,-10Z"/></g>')


def kira(x, y, k, col, delay):
    return (f'<path class="kira" style="animation-delay:-{delay}s" fill="{col}" '
            f'd="M{x},{y-k} Q{x+k*.18},{y-k*.18} {x+k},{y} Q{x+k*.18},{y+k*.18} {x},{y+k} '
            f'Q{x-k*.18},{y+k*.18} {x-k},{y} Q{x-k*.18},{y-k*.18} {x},{y-k}Z"/>')


def check(uid, cx, cy, r, glow=True):
    k = r * .5
    path = f"M{cx-k*.95},{cy+k*.02} L{cx-k*.25},{cy+k*.7} L{cx+k*1.0},{cy-k*.65}"
    g = (f'<circle class="glow" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MINT}" stroke-width="{r*.22:.1f}" filter="url(#blur{uid})"/>'
         if glow else "")
    return (g + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}" fill-opacity=".55" stroke="{MINT}" stroke-width="{r*.1:.1f}"/>'
            f'<path d="{path}" fill="none" stroke="{MINT_DEEP}" stroke-width="{r*.2:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def cross(cx, cy, r):
    k = r * .38
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}" fill-opacity=".6" stroke="{PINK}" stroke-width="{r*.1:.1f}"/>'
            f'<path d="M{cx-k},{cy-k} L{cx+k},{cy+k} M{cx+k},{cy-k} L{cx-k},{cy+k}" stroke="{PINK_DEEP}" '
            f'stroke-width="{r*.18:.1f}" stroke-linecap="round"/>')


def wave(x0, y0, w, amp, seed, peak=None, n=90):
    """Deterministic detector-like trace: small noise plus an optional pulse."""
    pts = []
    for i in range(n + 1):
        t = i / n
        noise = ((i * 7919 + seed * 104729) % 97) / 97 - .5
        v = noise * amp * .5
        if peak is not None:
            d = (t - peak) / .022
            v -= amp * 2.2 * (2.718 ** (-d * d))
        pts.append(f"{x0 + t * w:.1f},{y0 + v:.1f}")
    return " ".join(pts)


def clouds(uid, W, H):
    return (f'<g filter="url(#cloud{uid})" fill="{WHITE}" opacity=".85">'
            f'<ellipse cx="{W*.12}" cy="{H*.98}" rx="{W*.22}" ry="{H*.16}"/>'
            f'<ellipse cx="{W*.45}" cy="{H*1.02}" rx="{W*.25}" ry="{H*.14}"/>'
            f'<ellipse cx="{W*.85}" cy="{H*.99}" rx="{W*.25}" ry="{H*.15}"/></g>')


def brackets(W, H, m=22, L=34):
    s = f'stroke="{LAV_DEEP}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity=".55"'
    return (f'<path {s} d="M{m},{m+L} V{m} H{m+L} M{W-m-L},{m} H{W-m} V{m+L} '
            f'M{W-m},{H-m-L} V{H-m} H{W-m-L} M{m+L},{H-m} H{m} V{H-m-L}"/>')


def svg(W, H, uid, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{STYLE}{defs(uid)}<defs><clipPath id="clip{uid}"><rect width="{W}" height="{H}" rx="26"/></clipPath></defs>'
            f'<g clip-path="url(#clip{uid})"><rect width="{W}" height="{H}" fill="url(#sky{uid})"/>{clouds(uid, W, H)}{body}</g>'
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="none" stroke="{LAV}" stroke-width="2"/></svg>')


# ---------------------------------------------------------------- header
def header():
    W, H, u = 1760, 560, "h"
    b = [brackets(W, H)]
    # left: text
    b.append(f'<text x="96" y="178" font-size="26" font-weight="700" letter-spacing="6" fill="{MINT_DEEP}">DATA SCIENCE @ UC SAN DIEGO</text>')
    b.append(f'<text x="90" y="300" font-size="112" font-weight="800" letter-spacing="-2" fill="{INK}">Zhen Wang'
             f'<tspan dx="26" font-size="58" font-weight="700" letter-spacing="4" fill="{PINK_DEEP}">王臻</tspan></text>')
    b.append(f'<text x="96" y="376" font-size="36" fill="{INK_SOFT}">I build AI agents — and the checks</text>')
    b.append(f'<text x="96" y="424" font-size="36" fill="{INK_SOFT}">that keep them honest.</text>')
    # status chips
    chips = [("agent", LAV_DEEP), ("checker", MINT_DEEP), ("verified", PINK_DEEP)]
    x = 96
    for label, col in chips:
        w = 26 + len(label) * 13
        b.append(f'<rect x="{x}" y="456" width="{w}" height="34" rx="17" fill="{WHITE}" fill-opacity=".6" stroke="{col}" stroke-width="1.6"/>'
                 f'<text x="{x + w/2}" y="479" font-size="18" text-anchor="middle" fill="{col}" font-weight="600">{label}</text>')
        x += w + 12
    # right: HUD cluster
    b.append(panel(u, 1000, 84, 440, 196))
    b.append(f'<g stroke="{LAV}" stroke-width="1" opacity=".6">' +
             "".join(f'<path d="M1020,{y} H1420"/>' for y in (140, 180, 220, 260)) + "</g>")
    b.append(f'<polyline points="{wave(1022, 196, 396, 26, 3, peak=.58)}" fill="none" stroke="{MINT}" stroke-width="5" opacity=".35" filter="url(#blur{u})"/>')
    b.append(f'<polyline points="{wave(1022, 196, 396, 26, 3, peak=.58)}" fill="none" stroke="{MINT_DEEP}" stroke-width="2.4" stroke-linejoin="round"/>')
    b.append(panel(u, 1468, 84, 220, 196))
    b.append(check(u, 1578, 188, 64))
    b.append(panel(u, 1000, 308, 270, 176))
    nodes = [(1050, 420), (1110, 360), (1170, 440), (1230, 372), (1130, 452)]
    edges = [(0, 1), (1, 2), (1, 3), (2, 3), (0, 4), (4, 2)]
    b.append("".join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[c][0]}" y2="{nodes[c][1]}" stroke="{LAV_DEEP}" stroke-width="2" opacity=".7"/>' for a, c in edges))
    b.append("".join(f'<circle cx="{x}" cy="{y}" r="{11 if i != 3 else 14}" fill="{MINT_SOFT if i != 3 else MINT}" stroke="{MINT_DEEP if i == 3 else LAV_DEEP}" stroke-width="2"/>' for i, (x, y) in enumerate(nodes)))
    b.append(panel(u, 1298, 308, 390, 176))
    heights = [34, 52, 46, 70, 64, 92, 108]
    for i, h in enumerate(heights):
        bx = 1330 + i * 48
        b.append(f'<rect x="{bx}" y="{462 - h}" width="28" height="{h}" rx="5" fill="url(#bar{u})"/>')
    trend = " ".join(f"{1344 + i*48},{462 - h - 16}" for i, h in enumerate(heights))
    b.append(f'<polyline points="{trend}" fill="none" stroke="{PINK_DEEP}" stroke-width="2.4" stroke-dasharray="6 6"/>')
    # petals and sparkles, sparse
    for args in [(930, 120, 1.6, 20, 0), (1720, 300, 1.3, -30, 4), (960, 500, 1.1, 60, 7), (740, 90, 1.0, 10, 2), (1450, 520, 1.2, -50, 9)]:
        b.append(petal(*args))
    b.append(kira(1460, 60, 12, WHITE, 0) + kira(960, 280, 9, MINT, 1.3) + kira(80, 96, 10, LAV_DEEP, 2.1))
    return svg(W, H, u, "".join(b))


# ---------------------------------------------------------------- cards
CW, CH = 640, 360


def card_siderius():
    u = "s"
    b = [panel(u, 40, 40, 370, 280)]
    b.append(f'<g stroke="{LAV}" stroke-width="1" opacity=".6">' + "".join(f'<path d="M64,{y} H386"/>' for y in (120, 170, 220, 270)) + "</g>")
    hs = [40, 62, 56, 88, 104, 140, 172]
    for i, h in enumerate(hs):
        b.append(f'<rect x="{72 + i*44}" y="{290 - h}" width="26" height="{h}" rx="5" fill="url(#bar{u})"/>')
    b.append(f'<polyline points="{" ".join(f"{85 + i*44},{274 - h}" for i, h in enumerate(hs))}" fill="none" stroke="{MINT_DEEP}" stroke-width="3" stroke-linejoin="round"/>')
    # shield inspector
    sx, sy = 510, 170
    b.append(f'<path class="glow" d="M{sx},{sy-92} L{sx+74},{sy-64} V{sy+4} C{sx+74},{sy+54} {sx+36},{sy+84} {sx},{sy+100} C{sx-36},{sy+84} {sx-74},{sy+54} {sx-74},{sy+4} V{sy-64}Z" fill="none" stroke="{MINT}" stroke-width="14" filter="url(#blur{u})"/>')
    b.append(f'<path d="M{sx},{sy-92} L{sx+74},{sy-64} V{sy+4} C{sx+74},{sy+54} {sx+36},{sy+84} {sx},{sy+100} C{sx-36},{sy+84} {sx-74},{sy+54} {sx-74},{sy+4} V{sy-64}Z" fill="{WHITE}" fill-opacity=".7" stroke="{MINT}" stroke-width="5"/>')
    b.append(f'<path d="M{sx-34},{sy+6} L{sx-8},{sy+32} L{sx+38},{sy-22}" fill="none" stroke="{MINT_DEEP}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
    # magnifier over the chart
    b.append(f'<circle cx="330" cy="150" r="40" fill="{WHITE}" fill-opacity=".35" stroke="{LAV_DEEP}" stroke-width="6"/>'
             f'<path d="M358,178 L392,212" stroke="{LAV_DEEP}" stroke-width="10" stroke-linecap="round"/>')
    b.append(petal(600, 50, 1.3, 30, 1) + petal(440, 320, 1.1, -20, 5) + kira(450, 70, 10, WHITE, .4))
    return svg(CW, CH, u, "".join(b))


def card_planner():
    u = "p"
    b = [panel(u, 36, 36, 568, 288, c=18)]
    cols = ["FA", "WI", "SP"]
    for ci, name in enumerate(cols):
        x = 66 + ci * 182
        b.append(f'<text x="{x + 80}" y="86" font-size="20" font-weight="700" text-anchor="middle" letter-spacing="3" fill="{INK_SOFT}">{name}</text>')
        for ri in range(3):
            y = 104 + ri * 70
            bad = (ci, ri) == (1, 1)
            fixed = (ci, ri) == (2, 1)
            stroke = PINK if bad else MINT
            fill = PINK_SOFT if bad else (MINT_SOFT if fixed else WHITE)
            b.append(f'<rect x="{x}" y="{y}" width="160" height="54" rx="10" fill="{fill}" fill-opacity="{.9 if bad or fixed else .7}" stroke="{stroke}" stroke-width="{2.5 if bad or fixed else 1.5}"/>')
            b.append(f'<rect x="{x+16}" y="{y+16}" width="70" height="8" rx="4" fill="{LAV}"/><rect x="{x+16}" y="{y+31}" width="44" height="7" rx="3.5" fill="{LAV}" opacity=".6"/>')
            if bad:
                b.append(cross(x + 132, y + 27, 15))
            else:
                b.append(check(u, x + 132, y + 27, 15, glow=fixed))
    # arrow from the failing tile to its fix
    b.append(f'<path d="M402,231 L424,231" stroke="{MINT_DEEP}" stroke-width="3.5" stroke-linecap="round"/>'
             f'<path d="M416,224 L425,231 L416,238" fill="none" stroke="{MINT_DEEP}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(petal(600, 330, 1.2, 40, 2) + petal(30, 340, 1.0, -10, 6) + kira(590, 30, 10, WHITE, 1))
    return svg(CW, CH, u, "".join(b))


def card_majorana():
    u = "m"
    b = [panel(u, 36, 36, 568, 288, c=18)]
    b.append(f'<g stroke="{LAV}" stroke-width="1" opacity=".6">' + "".join(f'<path d="M60,{y} H580"/>' for y in (110, 160, 210, 260)) + "</g>")
    b.append(f'<rect x="300" y="72" width="54" height="226" rx="6" fill="{MINT_SOFT}" fill-opacity=".7" stroke="{MINT}" stroke-width="2"/>')
    pts = wave(64, 236, 512, 22, 11, peak=.5, n=140)
    b.append(f'<polyline points="{pts}" fill="none" stroke="{MINT}" stroke-width="6" opacity=".35" filter="url(#blur{u})"/>'
             f'<polyline points="{pts}" fill="none" stroke="{LAV_DEEP}" stroke-width="2.2" stroke-linejoin="round"/>')
    # verdict tags
    b.append(f'<rect x="384" y="84" width="200" height="48" rx="24" fill="{WHITE}" fill-opacity=".8" stroke="{MINT}" stroke-width="2"/>' + check(u, 410, 108, 15, glow=False) +
             f'<text x="434" y="116" font-size="21" font-weight="700" fill="{MINT_DEEP}">signal</text>')
    b.append(f'<rect x="384" y="144" width="200" height="48" rx="24" fill="{WHITE}" fill-opacity=".8" stroke="{PINK}" stroke-width="2"/>' + cross(410, 168, 15) +
             f'<text x="434" y="176" font-size="21" font-weight="700" fill="{PINK_DEEP}">background</text>')
    b.append(petal(30, 40, 1.2, 20, 3) + petal(612, 330, 1.1, -40, 8) + kira(380, 60, 9, WHITE, .8))
    return svg(CW, CH, u, "".join(b))


def card_nwa():
    u = "n"
    b = []
    # moonlit academy hall over water, in the same palette
    b.append(f'<circle class="glow" cx="500" cy="104" r="60" fill="{WHITE}" filter="url(#blur{u})"/>'
             f'<circle cx="500" cy="104" r="50" fill="{WHITE}" stroke="{PINK_SOFT}" stroke-width="3"/>')
    hall = (f'<path d="M178,150 Q200,152 214,128 H346 Q360,152 382,150 Q370,158 350,158 H210 Q190,158 178,150Z" fill="{LAV_DEEP}"/>'
            f'<rect x="222" y="158" width="116" height="22" fill="{LAV}"/>'
            f'<path d="M140,192 Q170,196 192,178 H368 Q390,196 420,192 Q404,204 380,204 H180 Q156,204 140,192Z" fill="{LAV_DEEP}"/>'
            f'<rect x="176" y="204" width="208" height="34" fill="{LAV}"/>'
            + "".join(f'<path d="M{x},204 V238" stroke="{LAV_DEEP}" stroke-width="3"/>' for x in range(190, 384, 32))
            + f'<rect x="262" y="214" width="36" height="24" rx="3" fill="{PINK_SOFT}" opacity=".9"/>'
            f'<rect x="150" y="238" width="260" height="10" fill="{LAV_DEEP}"/>')
    b.append(hall)
    b.append(f'<rect x="0" y="248" width="640" height="112" fill="{LAV}" opacity=".45"/>')
    b.append(f'<g transform="translate(0,496) scale(1,-1)" opacity=".22">{hall}</g>')
    for i, (y, w) in enumerate([(266, 200), (286, 150), (306, 110), (326, 70)]):
        b.append(f'<path d="M{500 - w/2},{y} H{500 + w/2}" stroke="{WHITE}" stroke-width="{4 - i*.6:.1f}" stroke-linecap="round" opacity=".85"/>')
    for i in range(4):
        b.append(f'<path d="M{60 + i*90},{300 + (i % 2)*24} H{120 + i*90}" stroke="{WHITE}" stroke-width="2" opacity=".55" stroke-linecap="round"/>')
    b.append(panel(u, 40, 40, 116, 48, c=12) +
             f'<text x="98" y="73" font-size="19" font-weight="700" text-anchor="middle" letter-spacing="2" fill="{INK_SOFT}">UE5</text>')
    b.append(petal(420, 60, 1.3, 20, 2) + petal(600, 200, 1.0, -30, 6) + petal(110, 140, 1.1, 50, 4))
    b.append(kira(600, 50, 10, WHITE, .2) + kira(250, 80, 8, WHITE, 1.8))
    return svg(CW, CH, u, "".join(b))


def footer():
    W, H, u = 1760, 120, "f"
    b = [f'<path d="M80,60 H800" stroke="{LAV_DEEP}" stroke-width="2" opacity=".5"/>',
         f'<path d="M960,60 H1680" stroke="{LAV_DEEP}" stroke-width="2" opacity=".5"/>']
    b.append("".join(f'<path d="M{x},54 V66" stroke="{LAV_DEEP}" stroke-width="2" opacity=".5"/>' for x in range(120, 800, 80)))
    b.append("".join(f'<path d="M{x},54 V66" stroke="{LAV_DEEP}" stroke-width="2" opacity=".5"/>' for x in range(1000, 1680, 80)))
    b.append(check(u, 880, 60, 30))
    b.append(petal(420, 34, 1.3, 20, 1) + petal(1300, 88, 1.2, -40, 5) + petal(1600, 30, 1.0, 60, 3))
    b.append(kira(700, 92, 9, WHITE, .5) + kira(1080, 30, 10, MINT, 2))
    return svg(W, H, u, "".join(b))


for name, fn in [("header", header), ("card-siderius", card_siderius), ("card-planner", card_planner),
                 ("card-majorana", card_majorana), ("card-nwa", card_nwa), ("footer", footer)]:
    s = fn()
    (OUT / f"{name}.svg").write_text(s, encoding="utf-8")
    print(f"{name}.svg {len(s)//1024} KB")
