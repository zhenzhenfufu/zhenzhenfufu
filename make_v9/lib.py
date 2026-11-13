"""v9 shared style module: washi journal page + icon wallpaper margin + rainy-alley accents.

Every helper returns an SVG fragment string. Helpers that reference <defs> take `uid`
(the per-document id prefix used by `defs(uid, k)` / `svg_doc`) so several SVGs never clash.
`scale` multiplies geometry AND stroke widths; for 1600x900 cards shown at ~420px wide,
use scale ~2 so strokes stay bold. Python 3 stdlib only.
"""
import math
import random

# ------------------------------------------------------------------ palette (light pastel only, no hue 70-192)
FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"
INK = "#2b2557"      # main text / ink outlines (deep indigo)
INK2 = "#4a4570"     # secondary text (tagline)
MUTE = "#6f68a8"     # small tracked caps, muted lavender-indigo
PEN = "#8f8bd0"      # ink-pen doodle stroke
PEN_D = "#7670bd"    # darker pen
LAV = "#b9b0f0"
LAV_L = "#e6e0fb"
PINK = "#f7b6cf"     # sakura
PINK_D = "#d9608e"   # labels, hanko
PINK_L = "#ffe3ee"
BLUE = "#a9c4ff"     # sky blue
BLUE_D = "#6f8bff"   # periwinkle
BLUE_L = "#e3ebff"
GOLD = "#f2c46d"
GOLD_D = "#e0a640"
CREAM = "#fff7ec"    # paper
WHITE = "#ffffff"
SKY1, SKY2, SKY3 = "#ebe4fb", "#ddd6f6", "#f7e9f2"   # lavender margin gradient
DOT = "#e2daf2"      # paper dot grid
B1, B2, B3 = "#d9d0f4", "#cfc5f0", "#c4b9ea"         # watercolour alley buildings
EDGE = "#b3a8e2"     # building edges / wires
WIN = "#f3eefc"      # windows
FAR = "#d2c9f0"      # far skyline
BRANCH = "#9c86b8"   # sakura branch

PALETTE = dict(INK=INK, INK2=INK2, MUTE=MUTE, PEN=PEN, PEN_D=PEN_D, LAV=LAV, LAV_L=LAV_L, PINK=PINK,
               PINK_D=PINK_D, PINK_L=PINK_L, BLUE=BLUE, BLUE_D=BLUE_D, BLUE_L=BLUE_L, GOLD=GOLD,
               GOLD_D=GOLD_D, CREAM=CREAM, WHITE=WHITE, SKY1=SKY1, SKY2=SKY2, SKY3=SKY3, DOT=DOT,
               B1=B1, B2=B2, B3=B3, EDGE=EDGE, WIN=WIN, FAR=FAR, BRANCH=BRANCH)

# ------------------------------------------------------------------ base style (all motion off under reduced-motion)
BASE_STYLE = """<style>
  .f{font-family:%s}
  .tw{animation:tw 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
  .tw2{animation:tw 3.2s ease-in-out 1.6s infinite;transform-box:fill-box;transform-origin:center}
  @keyframes tw{0%%,100%%{opacity:1;transform:scale(1)}50%%{opacity:.45;transform:scale(.8)}}
  .bob{animation:bob 3.6s ease-in-out infinite}
  @keyframes bob{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-5px)}}
  .rain{animation:fall 1.6s linear infinite}
  @keyframes fall{from{transform:translate(0,-60px)}to{transform:translate(-11px,0)}}
  .sway{transform-box:fill-box;transform-origin:50%% 0;animation:sway 4s ease-in-out infinite alternate}
  @keyframes sway{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}
  .rip{animation:rip 2.8s ease-in-out infinite}
  @keyframes rip{0%%,100%%{opacity:1}50%%{opacity:.25}}
  .drift{animation:drift 9s ease-in-out infinite alternate}
  @keyframes drift{from{transform:translate(0,0)}to{transform:translate(-12px,9px)}}
  @media (prefers-reduced-motion: reduce){.tw,.tw2,.bob,.rain,.sway,.rip,.drift{animation:none}}
</style>""" % FONT


def esc(s):
    """XML-escape text content (&, <, >)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def n(v):
    """Compact number formatting for coordinates."""
    return f"{v:.1f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def text(x, y, s, size, fill=INK, weight=400, anchor="start", ls=0, extra=""):
    """Plain <text> in the shared font (s is escaped)."""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{n(x)}" y="{n(y)}" class="f" font-size="{n(size)}" font-weight="{weight}" '
            f'fill="{fill}"{a}{l}{extra}>{esc(s)}</text>')


def pen(d, w=3.2, col=PEN, extra=""):
    """Round-capped ink-pen stroke path."""
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" stroke-linecap="round" '
            f'stroke-linejoin="round"{extra}/>')


# ------------------------------------------------------------------ tiny shapes
def drop_d(cx, cy, r):
    """Path data for a raindrop with round bottom centred at (cx,cy)."""
    return (f"M{cx:.1f} {cy-2.3*r:.1f} C{cx+0.35*r:.1f} {cy-1.4*r:.1f} {cx+r:.1f} {cy-0.7*r:.1f} {cx+r:.1f} {cy:.1f} "
            f"A{r:.1f} {r:.1f} 0 0 1 {cx-r:.1f} {cy:.1f} C{cx-r:.1f} {cy-0.7*r:.1f} {cx-0.35*r:.1f} {cy-1.4*r:.1f} {cx:.1f} {cy-2.3*r:.1f} Z")


def sparkle_d(cx, cy, r):
    """Path data for a 4-point sparkle."""
    k = r * 0.22
    return (f"M{cx:.1f},{cy-r:.1f} Q{cx+k:.1f},{cy-k:.1f} {cx+r:.1f},{cy:.1f} Q{cx+k:.1f},{cy+k:.1f} {cx:.1f},{cy+r:.1f} "
            f"Q{cx-k:.1f},{cy+k:.1f} {cx-r:.1f},{cy:.1f} Q{cx-k:.1f},{cy-k:.1f} {cx:.1f},{cy-r:.1f}Z")


def sparkle(cx, cy, r, fill=GOLD, op=1.0, cls=""):
    """4-point sparkle; cls='tw' to twinkle."""
    c = f' class="{cls}"' if cls else ""
    return f'<g{c}><path d="{sparkle_d(cx, cy, r)}" fill="{fill}" opacity="{op}"/></g>'


def star(cx, cy, r, fill=GOLD, stroke=PEN_D, sw=1.6, rot=0, cls=""):
    """5-point star with ink outline; cls='tw' to twinkle."""
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36 + rot)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}")
    c = f' class="{cls}"' if cls else ""
    st = f' stroke="{stroke}" stroke-width="{n(sw)}"' if stroke else ""
    return f'<g{c}><polygon points="{" ".join(pts)}" fill="{fill}" stroke-linejoin="round"{st}/></g>'


def petal(x, y, rot=0, scale=1.0, op=0.9):
    """Sakura petal (notched tip) at (x,y)."""
    t = f'transform="translate({n(x)} {n(y)}) rotate({n(rot)}) scale({n(scale)})"'
    return (f'<g {t} opacity="{op}"><path d="M0,-14 C10,-12 13,2 0,14 C-13,2 -10,-12 0,-14Z" fill="{PINK}"/>'
            f'<path d="M0,-14 L0,-7" stroke="{WHITE}" stroke-width="2" stroke-linecap="round"/></g>')


def blossom(x, y, scale=1.0, op=1.0):
    """Five-petal sakura blossom."""
    p = "".join(f'<ellipse cx="0" cy="-8" rx="6" ry="9" transform="rotate({i*72})"/>' for i in range(5))
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})" opacity="{op}"><g fill="{PINK}">{p}</g>'
            f'<circle r="3" fill="{PINK_D}"/><circle r="1.4" fill="{GOLD}"/></g>')


def _flower(cx, cy, r, fill=WHITE, op=0.9):
    o = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        ex, ey = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        o.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r*0.42:.1f}" ry="{r*0.5:.1f}" transform="rotate({i*72} {ex:.1f} {ey:.1f})"/>')
    return f'<g fill="{fill}" fill-opacity="{op}">' + "".join(o) + f'<circle cx="{cx}" cy="{cy}" r="{r*0.22:.1f}" fill="{GOLD}" fill-opacity="1"/></g>'


# ------------------------------------------------------------------ icon wallpaper glyphs (option 3), centred at 0,0, ~20px
def _ic_drop(c=BLUE_D):
    return f'<path d="M0,-10 C4,-3 7,1 7,5 A7,7 0 0 1 -7,5 C-7,1 -4,-3 0,-10Z" fill="{c}"/>'


def _ic_sakura(c=PINK_D):
    p = "".join(f'<ellipse cx="0" cy="-5.5" rx="3.6" ry="5.6" transform="rotate({a})"/>' for a in range(0, 360, 72))
    return f'<g fill="{c}">{p}</g><circle r="2" fill="{WHITE}"/>'


def _ic_check(c=PINK_D, w=3.4):
    return f'<path d="M-8,0 L-2.5,6 L9,-7" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def _ic_spark(c=GOLD_D, r=10):
    return f'<path d="{sparkle_d(0, 0, r)}" fill="{c}"/>'


def _ic_umbrella(c=BLUE_D):
    return (f'<g fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round">'
            f'<path d="M-10,-1 A10,9 0 0 1 10,-1 Q5,-3.5 0,-1 Q-5,-3.5 -10,-1Z" fill="{c}" fill-opacity=".35"/>'
            f'<path d="M0,-1 V8 a3,3 0 0 1 -6,0"/></g>')


def _ic_wave(c=PEN_D):
    return (f'<path d="M-13,1 H-6 L-3,-7 L1,9 L4,-3 L6,1 H13" fill="none" stroke="{c}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def _ic_heart(c=PINK_D):
    rows = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    cells = "".join(f'<rect x="{(i-3.5)*2.8:.1f}" y="{(j-3)*2.8:.1f}" width="2.8" height="2.8"/>'
                    for j, r in enumerate(rows) for i, ch in enumerate(r) if ch == "1")
    return f'<g fill="{c}">{cells}</g>'


def _place(x, y, glyph, rot=0, s=1.0):
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{glyph}</g>'


def wallpaper_pattern(pid, k=1.0, op=0.22):
    """<pattern> def: half-drop tile of tiny trait icons (raindrop, check, sparkle, umbrella, waveform,
    sakura, pixel heart). Use as fill on the lavender margin only; op keeps it subtle."""
    items = [(22, 26, _ic_drop(), 0), (95, 22, _ic_check(), -6), (165, 30, _ic_spark(), 0),
             (58, 70, _ic_umbrella(), -10), (130, 68, _ic_wave(), 0), (200, 76, _ic_sakura(), 20),
             (24, 118, _ic_heart(), 0), (94, 122, _ic_sakura(), -12), (162, 116, _ic_drop(), 0),
             (60, 156, _ic_spark(PEN_D, 8), 0), (128, 158, _ic_umbrella(PINK_D), 8), (196, 150, _ic_check(BLUE_D, 3), 4)]
    g = "".join(_place(x, y, gl, r) for x, y, gl, r in items)
    return (f'<pattern id="{pid}" width="220" height="168" patternUnits="userSpaceOnUse" '
            f'patternTransform="scale({n(k)})"><g opacity="{op}">{g}</g></pattern>')


# ------------------------------------------------------------------ defs
def defs(uid, k=1.0, wall_op=0.22):
    """All shared <defs> for one document, ids prefixed with uid: {uid}sky, {uid}wall, {uid}grid,
    {uid}tapeRain, {uid}tapeRainLav, {uid}tapeSakura, {uid}sh, {uid}shs, {uid}photo, {uid}road,
    {uid}bldL, {uid}bldR, {uid}lamp, {uid}halo, {uid}soft. k scales pattern tiles (1 = header, 2 = 1600px card)."""
    p = uid
    return f"""<defs>
  <linearGradient id="{p}sky" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{SKY1}"/><stop offset=".55" stop-color="{SKY2}"/><stop offset="1" stop-color="{SKY3}"/>
  </linearGradient>
  {wallpaper_pattern(p + "wall", k, wall_op)}
  <pattern id="{p}grid" width="30" height="30" patternUnits="userSpaceOnUse" patternTransform="scale({n(k)})">
    <circle cx="15" cy="15" r="1.9" fill="{DOT}"/>
  </pattern>
  <pattern id="{p}tapeRain" width="30" height="30" patternUnits="userSpaceOnUse" patternTransform="scale({n(k)})">
    <rect width="30" height="30" fill="{BLUE}" fill-opacity=".72"/>
    <path d="{drop_d(8, 11, 3.6)}" fill="{WHITE}" fill-opacity=".85"/>
    <path d="{drop_d(23, 25, 2.8)}" fill="{WHITE}" fill-opacity=".65"/>
  </pattern>
  <pattern id="{p}tapeRainLav" width="30" height="30" patternUnits="userSpaceOnUse" patternTransform="scale({n(k)})">
    <rect width="30" height="30" fill="{LAV}" fill-opacity=".78"/>
    <path d="{drop_d(8, 11, 3.6)}" fill="{WHITE}" fill-opacity=".85"/>
    <path d="{drop_d(23, 25, 2.8)}" fill="{WHITE}" fill-opacity=".65"/>
  </pattern>
  <pattern id="{p}tapeSakura" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="scale({n(k)})">
    <rect width="36" height="36" fill="{PINK}" fill-opacity=".8"/>
    {_flower(10, 10, 7)}
    {_flower(27, 27, 5.4, WHITE, .75)}
  </pattern>
  <filter id="{p}sh" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="{n(6*k)}" stdDeviation="{n(8*k)}" flood-color="#4a3f8f" flood-opacity=".18"/>
  </filter>
  <filter id="{p}shs" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="{n(3*k)}" stdDeviation="{n(3*k)}" flood-color="#4a3f8f" flood-opacity=".2"/>
  </filter>
  <linearGradient id="{p}photo" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c6baf0"/><stop offset=".6" stop-color="#ddd3f7"/><stop offset="1" stop-color="#f7dbe9"/>
  </linearGradient>
  <linearGradient id="{p}road" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e3dbf7"/><stop offset="1" stop-color="#f3e6f3"/>
  </linearGradient>
  <linearGradient id="{p}bldL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{B2}"/><stop offset="1" stop-color="{B1}"/></linearGradient>
  <linearGradient id="{p}bldR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{B1}"/><stop offset="1" stop-color="#e2dbf7"/></linearGradient>
  <radialGradient id="{p}lamp"><stop offset="0" stop-color="#ffe9c2" stop-opacity=".85"/><stop offset="1" stop-color="#ffe9c2" stop-opacity="0"/></radialGradient>
  <radialGradient id="{p}halo"><stop offset="0" stop-color="#fffaf0" stop-opacity=".9"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/></radialGradient>
  <filter id="{p}soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.4"/></filter>
</defs>"""


def svg_doc(w, h, uid, title, desc, body, k=2.0, rx=None):
    """Complete standalone SVG: root + <title>/<desc> + BASE_STYLE + defs(uid,k) + rounded clip around body
    + soft white rim. Text args are escaped. rx defaults to 12*k (24 for a k=2 card)."""
    r = rx if rx is not None else 12 * k
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
        f'aria-labelledby="{uid}t {uid}d" font-family="{FONT}">',
        f'<title id="{uid}t">{esc(title)}</title>',
        f'<desc id="{uid}d">{esc(desc)}</desc>',
        BASE_STYLE,
        defs(uid, k),
        f'<clipPath id="{uid}clip"><rect width="{w}" height="{h}" rx="{n(r)}"/></clipPath>',
        f'<g clip-path="url(#{uid}clip)">',
        body,
        '</g>',
        f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="{n(r-1)}" fill="none" stroke="{WHITE}" stroke-opacity=".7" stroke-width="3"/>',
        '</svg>'])


# ------------------------------------------------------------------ page pieces
def margin_bg(w, h, uid):
    """Lavender margin: gradient + low-opacity icon wallpaper over the whole canvas (paper goes on top)."""
    return (f'<rect width="{w}" height="{h}" fill="url(#{uid}sky)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#{uid}wall)"/>')


def paper(x, y, w, h, uid, rx=16, shadow=True):
    """Cream journal paper with soft drop shadow and dotted grid."""
    f = f' filter="url(#{uid}sh)"' if shadow else ""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="{CREAM}"{f}/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="url(#{uid}grid)"/>')


def tape(cx, cy, w, h, rot, uid, kind="rain", op=1.0):
    """Washi tape strip with zig-zag torn ends centred at (cx,cy); kind = 'rain' (blue raindrops),
    'rainlav' (lavender raindrops) or 'sakura' (pink blossoms)."""
    pat = {"rain": "tapeRain", "rainlav": "tapeRainLav", "sakura": "tapeSakura"}[kind]
    x, y = cx - w / 2, cy - h / 2
    zz, m = max(4, h * 0.13), max(2, int(h // 10))
    pts = [(x, y), (x + w, y)]
    for i in range(1, 2 * m + 1):
        pts.append((x + w - (zz if i % 2 else 0), y + i * h / (2 * m)))
    pts.append((x, y + h))
    for i in range(1, 2 * m):
        pts.append((x + (zz if i % 2 else 0), y + h - i * h / (2 * m)))
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    return (f'<g transform="rotate({n(rot)} {n(cx)} {n(cy)})" opacity="{op}">'
            f'<polygon points="{poly}" fill="url(#{uid}{pat})"/>'
            f'<polygon points="{poly}" fill="{WHITE}" fill-opacity=".12"/></g>')


def card_paper_rect(w, h, k=2.0):
    """(x, y, w, h) of the paper panel that card_frame draws. For 1600x900, k=2: (52, 48, 1496, 804)."""
    mx, my = 26 * k, 24 * k
    return (mx, my, w - 2 * mx, h - 2 * my)


def card_frame(w, h, uid, k=2.0):
    """Standard card background so all cards match: lavender margin + icon wallpaper, dotted cream paper
    (see card_paper_rect), blue raindrop tape top-left and sakura tape top-right. Needs svg_doc(..., k=k)."""
    px, py, pw, ph = card_paper_rect(w, h, k)
    return "\n".join([
        margin_bg(w, h, uid),
        paper(px, py, pw, ph, uid, rx=12 * k),
        tape(px + 34 * k, py + 4 * k, 118 * k, 32 * k, -32, uid, "rain"),
        tape(px + pw - 34 * k, py + 4 * k, 118 * k, 32 * k, 32, uid, "sakura"),
    ])


# ------------------------------------------------------------------ stamps, mascot
def hanko(cx, cy, r=46, rot=-12, text_="検証済", fs=None):
    """Pink-red round seal (default 検証済) with worn specks; fs defaults to r*0.5."""
    fs = fs or r * 0.5
    specks = "".join(f'<circle cx="{cx + r*a:.1f}" cy="{cy + r*b:.1f}" r="{q*r/50:.1f}" fill="{CREAM}"/>'
                     for a, b, q in [(.92, -.3, 2.4), (-.6, .76, 2), (.2, -.97, 1.8), (-.95, -.15, 1.6), (.66, .7, 1.6)])
    return (f'<g transform="rotate({n(rot)} {n(cx)} {n(cy)})" opacity=".92">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{WHITE}" fill-opacity=".35" stroke="{PINK_D}" stroke-width="{r*0.09:.1f}"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r*0.86:.1f}" fill="none" stroke="{PINK_D}" stroke-width="{r*0.035:.1f}"/>'
            f'<text x="{n(cx)}" y="{cy + fs*0.36:.1f}" text-anchor="middle" class="f" font-size="{fs:.1f}" font-weight="800" '
            f'fill="{PINK_D}">{esc(text_)}</text>{specks}</g>')


def raindrop_glyph(x, y, scale=1.0, op=.9):
    """White droplet sitting on an umbrella / surface."""
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})" opacity="{op}">'
            f'<path d="M0 -8 C4 -2 6 2 6 5 A6 6 0 0 1 -6 5 C-6 2 -4 -2 0 -8Z" fill="{WHITE}"/>'
            f'<circle cx="-2" cy="4" r="1.5" fill="{BLUE}"/></g>')


def mascot(x, y, scale=1.0, umbrella=False, magnifier=False, bob=True, face="happy"):
    """Recurring white robot-cat: lavender ears, dark visor face with sky-blue eyes, pink cheeks, lavender
    feet. (x,y) is the head centre; local extents ~x -46..46, y -62 (ear tips) .. 58 (feet).
    umbrella=True adds a clear umbrella in the right hand (canopy reaches y -173, x -66..150);
    magnifier=True adds a magnifier with a pink check in the left hand. face: 'happy' or 'dot'."""
    eyes = (f'<path d="M-20,0 q6,-9 12,0" stroke="{BLUE}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M8,0 q6,-9 12,0" stroke="{BLUE}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
    if face == "dot":
        eyes = f'<circle cx="-14" cy="-2" r="5" fill="{BLUE}"/><circle cx="14" cy="-2" r="5" fill="{BLUE}"/>'
    mag = ""
    if magnifier:
        mag = (f'<g transform="translate(-62 20) rotate(-28)">'
               f'<line x1="0" y1="0" x2="0" y2="30" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
               f'<circle cx="0" cy="-16" r="16" fill="{WHITE}" fill-opacity=".7" stroke="{INK}" stroke-width="4.5"/>'
               f'<path d="M-7 -21 q4 -5 10 -4" stroke="{WHITE}" stroke-width="3" fill="none" stroke-linecap="round"/>'
               f'<path d="M-6 -16 l4 5 l9 -10" stroke="{PINK_D}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
               f'<circle cx="-59" cy="25" r="8" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>')
    umb = ""
    if umbrella:
        umb = (f'<g transform="rotate(-10 48 14)">'
               f'<line x1="48" y1="34" x2="48" y2="-150" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
               f'<path d="M48,34 v8 a9,9 0 0 1 -18,0" stroke="{PINK_D}" stroke-width="5" fill="none" stroke-linecap="round"/>'
               f'<path d="M-50,-96 C-46,-152 -4,-170 48,-170 C100,-170 142,-152 146,-96 Q122,-106 97,-96 Q72,-106 48,-96 '
               f'Q24,-106 -1,-96 Q-26,-106 -50,-96Z" fill="{WHITE}" fill-opacity=".45" stroke="{WHITE}" stroke-width="4" stroke-linejoin="round"/>'
               f'<path d="M-50,-96 C-46,-152 -4,-170 48,-170 C100,-170 142,-152 146,-96" fill="none" stroke="{PEN}" stroke-width="3"/>'
               f'<path d="M48,-170 Q22,-140 -1,-96 M48,-170 Q74,-140 97,-96" fill="none" stroke="{PEN}" stroke-width="2.2" opacity=".7"/>'
               f'<circle cx="48" cy="-173" r="5.5" fill="{PINK_D}"/>'
               f'<path d="M-34,-122 C-28,-142 -8,-154 14,-158" fill="none" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round" opacity=".95"/>'
               f'{raindrop_glyph(-8, -128, .8)}{raindrop_glyph(90, -150, .7)}{raindrop_glyph(118, -118, .6)}</g>'
               f'<circle cx="48" cy="14" r="8" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>')
    cls = ' class="bob"' if bob else ""
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})"><g{cls}>'
            f'<path d="M-38,-30 L-30,-62 L-10,-40Z" fill="{LAV}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M38,-30 L30,-62 L10,-40Z" fill="{LAV}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M-33,-36 L-29,-52 L-19,-41Z" fill="{PINK}"/><path d="M33,-36 L29,-52 L19,-41Z" fill="{PINK}"/>'
            f'<rect x="-24" y="38" width="48" height="20" rx="9" fill="{LAV}" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="-46" y="-42" width="92" height="84" rx="40" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="-32" y="-22" width="64" height="40" rx="18" fill="{INK}"/>{eyes}'
            f'<ellipse cx="-34" cy="26" rx="7" ry="4" fill="{PINK}"/><ellipse cx="34" cy="26" rx="7" ry="4" fill="{PINK}"/>'
            f'{mag}{umb}</g></g>')


# ------------------------------------------------------------------ rainy-alley accents (option 2)
def rain(x, y, w, h, count=40, seed=1, scale=1.0, op=0.5, length=(18, 34), col=WHITE):
    """Animated rain streaks covering box (x,y,w,h) (+60*scale above it for the fall loop). Clip it yourself."""
    rnd = random.Random(seed)
    segs = []
    for _ in range(count):
        sx = x + rnd.uniform(0, w + 20 * scale)
        sy = y + rnd.uniform(-60, h)
        L = rnd.uniform(*length) * scale
        segs.append(f"M{sx:.0f} {sy:.0f}l{-L*.18:.1f} {L:.1f}")
    return (f'<g class="rain"><path d="{"".join(segs)}" stroke="{col}" stroke-width="{2.2*scale:.1f}" '
            f'stroke-linecap="round" opacity="{op}"/></g>')


def _tube(d, col, w=4.0, op=1.0):
    return (f'<g opacity="{op}"><path d="{d}" fill="none" stroke="{col}" stroke-width="{w*2.3:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity=".18"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{WHITE}" stroke-width="{w*0.3:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/></g>')


def vsign_size(chars, size=28, pad=11):
    """(w, h) of vsign() at scale 1."""
    return size + pad * 2, len(chars) * (size + 6) + pad * 2 - 2


def vsign(x, y, chars, scale=1.0, ink=INK, edge=BLUE_D, size=28, pad=11, bracket=True):
    """Vertical shop sign (縦看板) with pastel neon-tube rim; (x,y) = top-left. Size via vsign_size()*scale."""
    w, h = vsign_size(chars, size, pad)
    step = size + 6
    o = [f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})">']
    if bracket:
        o.append(f'<path d="M{w/2} -14 V0" stroke="{EDGE}" stroke-width="4"/>')
    o.append(f'<rect x="4" y="5" width="{w}" height="{h}" rx="9" fill="{INK}" opacity=".08"/>')
    o.append(f'<rect width="{w}" height="{h}" rx="9" fill="{CREAM}" fill-opacity=".95"/>')
    o.append(_tube(f"M10 5 H{w-10} Q{w-5} 5 {w-5} 10 V{h-10} Q{w-5} {h-5} {w-10} {h-5} H10 Q5 {h-5} 5 {h-10} V10 Q5 5 10 5Z", edge, 3.2))
    for i, c in enumerate(chars):
        by = pad + size * 0.9 + i * step
        # tategaki: the long-vowel mark stands upright in vertical text
        rot = f' transform="rotate(90 {w/2} {by - size*0.36:.1f})"' if c == "ー" else ""
        o.append(f'<text x="{w/2}" y="{by:.1f}" text-anchor="middle"{rot} class="f" font-size="{size}" '
                 f'font-weight="700" fill="{ink}">{esc(c)}</text>')
    o.append('</g>')
    return "".join(o)


def lantern(x, y, uid, scale=1.0, glow=True, sway=True):
    """Paper lantern (chōchin) hanging from (x,y) = hook point; ~ 26w x 96h at scale 1. Gently sways."""
    g = f'<circle cx="0" cy="46" r="54" fill="url(#{uid}lamp)"/>' if glow else ""
    cls = ' class="sway"' if sway else ""
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})"><g{cls}>'
            f'<path d="M0 0 V10" stroke="{EDGE}" stroke-width="2.4"/>{g}'
            f'<rect x="-14" y="8" width="28" height="7" rx="2" fill="{INK}" opacity=".55"/>'
            f'<ellipse cx="0" cy="46" rx="24" ry="32" fill="#ffe4ea"/>'
            f'<ellipse cx="0" cy="46" rx="24" ry="32" fill="none" stroke="{PINK_D}" stroke-width="2.6" opacity=".75"/>'
            f'<path d="M-20 34 H20 M-23 48 H23 M-20 62 H20" stroke="{PINK_D}" stroke-width="1.8" opacity=".45"/>'
            f'<rect x="-14" y="76" width="28" height="7" rx="2" fill="{INK}" opacity=".55"/>'
            f'<path d="M0 83 V96" stroke="{PINK_D}" stroke-width="3" stroke-linecap="round"/></g></g>')


def puddle(cx, cy, scale=1.0, ripple=True):
    """Pale blue puddle with white ripple rings (outer ring pulses)."""
    r = f'<g class="rip"><ellipse rx="150" ry="27" fill="none" stroke="{WHITE}" stroke-width="1.8" opacity=".5"/></g>' if ripple else ""
    return (f'<g transform="translate({n(cx)} {n(cy)}) scale({n(scale)})">'
            f'<ellipse rx="132" ry="22" fill="{BLUE}" opacity=".32"/>'
            f'<ellipse rx="100" ry="15" fill="none" stroke="{WHITE}" stroke-width="2.6" opacity=".8"/>{r}</g>')


PHOTO_W, PHOTO_H = 258, 236        # alley_scene / polaroid photo window (local units)
POL_W, POL_H, POL_B = 286, 334, 14  # polaroid frame size and border (local units)


def alley_scene(x, y, uid, scale=1.0, name="al", signs=("雨宿り", "エージェント", "検証済"), with_mascot=True,
                rain_on=True):
    """Mini rainy Tokyo alley in a PHOTO_W x PHOTO_H box at (x,y): lavender watercolour sky with moon,
    soft far skyline, two building edges, vertical signs (left hanging sign = signs[0], right facade =
    signs[1], signs[2]), wires + lantern, rain, mascot under a clear umbrella on a puddle with reflection.
    Clipped to its box. `name` keeps clip ids unique if used twice in one document."""
    W, H = PHOTO_W, PHOTO_H
    cid, pid = f"{uid}{name}c", f"{uid}{name}p"
    mx, my, ms = 124, 176, .56  # mascot head centre + scale
    pcx, pcy = 124, 213          # puddle centre
    axis = my + 58 * ms         # reflection axis = feet line
    o = [f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)})">',
         f'<clipPath id="{cid}"><rect width="{W}" height="{H}" rx="3"/></clipPath>',
         f'<clipPath id="{pid}"><ellipse cx="{pcx}" cy="{pcy}" rx="76" ry="15"/></clipPath>',
         f'<g clip-path="url(#{cid})">',
         f'<rect width="{W}" height="{H}" fill="url(#{uid}photo)"/>',
         # moon
         f'<circle cx="150" cy="34" r="30" fill="url(#{uid}halo)"/><circle cx="150" cy="34" r="11" fill="#fffaf0"/>',
         f'<circle cx="88" cy="22" r="1.8" fill="{WHITE}"/><circle cx="178" cy="62" r="1.6" fill="{WHITE}"/>',
         # far skyline (soft)
         f'<g fill="{FAR}" filter="url(#{uid}soft)"><path d="M56 176 V128 H74 V112 H90 V138 H104 V120 H118 V176Z"/>'
         f'<path d="M132 176 V118 H146 V104 H160 V130 H176 V114 H192 V176Z"/>'
         f'<rect x="111" y="78" width="4" height="60"/><circle cx="113" cy="100" r="7"/></g>',
         # road + perspective
         f'<path d="M0 176 H{W} V{H} H0Z" fill="url(#{uid}road)"/>',
         f'<path d="M124 176 L40 {H} M124 176 L208 {H} M124 176 L-20 214 M124 176 L270 214" stroke="#d4caf1" stroke-width="2" opacity=".8"/>',
         # left building: front face + receding side face
         f'<path d="M0 0 H40 V{H} H0Z" fill="url(#{uid}bldL)"/>',
         f'<path d="M40 0 L62 26 V188 L40 {H}Z" fill="{B3}"/>',
         f'<path d="M40 0 V{H} M62 26 V188" stroke="{EDGE}" stroke-width="2.5"/>',
         f'<rect x="8" y="104" width="24" height="22" rx="3" fill="{WIN}" stroke="{EDGE}" stroke-width="2"/>',
         f'<rect x="10" y="106" width="20" height="18" rx="2" fill="{GOLD}" opacity=".35"/>',
         # little shop: glowing window under a scalloped pink awning
         f'<rect x="5" y="156" width="30" height="40" rx="3" fill="#fff4e3" stroke="{EDGE}" stroke-width="2"/>',
         f'<circle cx="20" cy="176" r="22" fill="url(#{uid}lamp)"/>',
         f'<path d="M1 142 H39 V152 q-3.2 6 -6.3 0 q-3.2 6 -6.3 0 q-3.2 6 -6.3 0 q-3.2 6 -6.3 0 q-3.2 6 -6.3 0 q-3.2 6 -6.3 0Z" '
         f'fill="{PINK}" stroke="{PINK_D}" stroke-width="1.4" stroke-opacity=".5"/>',
         # right building
         f'<path d="M{W} 0 H212 V{H} H{W}Z" fill="url(#{uid}bldR)"/>',
         f'<path d="M212 0 L194 22 V190 L212 {H}Z" fill="{B3}"/>',
         f'<path d="M212 0 V{H} M194 22 V190" stroke="{EDGE}" stroke-width="2.5"/>',
         f'<rect x="221" y="160" width="28" height="22" rx="3" fill="{WIN}" stroke="{EDGE}" stroke-width="2"/>',
         f'<rect x="223" y="162" width="24" height="18" rx="2" fill="{GOLD}" opacity=".35"/>',
         f'<path d="M235 160 V182" stroke="{EDGE}" stroke-width="1.6"/>',
         # wires + lantern
         f'<path d="M62 30 Q124 62 194 26" fill="none" stroke="{EDGE}" stroke-width="2"/>',
         f'<path d="M62 44 Q124 80 194 40" fill="none" stroke="{EDGE}" stroke-width="1.6" opacity=".7"/>',
         lantern(86, 36, uid, 0.48),
         ]
    if signs:
        if len(signs) > 0:   # hanging sign off the left building's side wall
            o.append(vsign(6, 16, signs[0], 0.62, INK, LAV, size=26, pad=10))
        if len(signs) > 1:   # tall facade sign, right building
            o.append(vsign(217, 10, signs[1], 0.62, INK, BLUE_D, size=26, pad=10))
        if len(signs) > 2:   # small sign on the right side wall, lower
            o.append(vsign(190, 150, signs[2], 0.5, PINK_D, PINK, size=26, pad=10, bracket=False))
    # puddle + reflection
    o.append(f'<ellipse cx="{pcx}" cy="{pcy}" rx="80" ry="16" fill="{BLUE}" opacity=".35"/>')
    if with_mascot:
        o.append(f'<g clip-path="url(#{pid})" opacity=".28"><g transform="translate(0 {2*axis}) scale(1 -1)">'
                 f'{mascot(mx, my, ms, umbrella=False, bob=False)}</g></g>')
    o.append(f'<ellipse cx="{pcx}" cy="{pcy}" rx="62" ry="10" fill="none" stroke="{WHITE}" stroke-width="2" opacity=".85"/>'
             f'<g class="rip"><ellipse cx="{pcx}" cy="{pcy}" rx="88" ry="17" fill="none" stroke="{WHITE}" stroke-width="1.6" opacity=".55"/></g>')
    if with_mascot:
        o.append(mascot(mx, my, ms, umbrella=True))
    if rain_on:
        o.append(rain(0, 0, W, H, 34, 11, 0.8, .6))
    o.append(petal(30, 206, 30, .7))
    o.append(petal(236, 222, -40, .65))
    o.append('</g></g>')
    return "\n".join(o)


def polaroid(cx, cy, uid, inner="", caption="", scale=1.0, rot=3.0, name="pol", tape_kind="sakura", caption_size=26):
    """Tilted white polaroid centred at (cx,cy), frame POL_W x POL_H local units, held by a washi tape on top.
    `inner` is drawn in photo-local coords (0..PHOTO_W, 0..PHOTO_H) and clipped; caption sits in the
    bottom strip in a slanted pen style. Use polaroid_point() to find frame corners in page coords."""
    x, y = -POL_W / 2, -POL_H / 2
    px, py = x + POL_B, y + POL_B
    cid = f"{uid}{name}"
    o = [f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(rot)}) scale({n(scale)})">',
         f'<rect x="{x}" y="{y}" width="{POL_W}" height="{POL_H}" rx="5" fill="{WHITE}" filter="url(#{uid}sh)"/>',
         f'<clipPath id="{cid}"><rect x="{px}" y="{py}" width="{PHOTO_W}" height="{PHOTO_H}" rx="3"/></clipPath>',
         f'<g clip-path="url(#{cid})"><g transform="translate({px} {py})">{inner}</g></g>',
         f'<rect x="{px}" y="{py}" width="{PHOTO_W}" height="{PHOTO_H}" rx="3" fill="none" stroke="{INK}" stroke-opacity=".08" stroke-width="2"/>']
    if caption:
        ty = py + PHOTO_H + (POL_H - POL_B - PHOTO_H) * 0.62 + caption_size * 0.35
        o.append(f'<g transform="translate({px + 14} {ty:.1f}) skewX(-8) rotate(-2)">'
                 f'<text x="0" y="0" class="f" font-size="{caption_size}" font-weight="600" fill="{PEN_D}" letter-spacing="4">{esc(caption)}</text>'
                 f'<path d="M2 10 q20 5 40 0 t40 0 t20 -1" fill="none" stroke="{PINK}" stroke-width="3" stroke-linecap="round"/></g>')
    o.append(tape(0, y + 2, 132, 34, -5, uid, tape_kind))
    o.append('</g>')
    return "\n".join(o)


def polaroid_point(cx, cy, lx, ly, scale=1.0, rot=3.0):
    """Page coords of polaroid-local point (lx,ly) (frame centre = 0,0; corners at +-POL_W/2, +-POL_H/2)."""
    a = math.radians(rot)
    X, Y = lx * scale, ly * scale
    return cx + X * math.cos(a) - Y * math.sin(a), cy + X * math.sin(a) + Y * math.cos(a)


# ------------------------------------------------------------------ ink doodles (stroke widths scale with `scale`)
def doodle_wave(x, y, w, amp=14, scale=1.0, col=BLUE_D, op=.8, cycles=(3, 7)):
    """Rising chirp waveform from (x,y) to (x+w,y) with tapered envelope and lead-in/out ticks."""
    pts = []
    a, b = cycles
    for i in range(0, 241):
        t = i / 240
        ph = 2 * math.pi * (a * t + b * t * t)
        env = math.sin(math.pi * min(1, t * 1.15)) ** 0.6 if t < .87 else max(0, 1 - (t - .87) * 7)
        pts.append(f"{x + w*t:.1f} {y + amp*scale*env*math.sin(ph):.1f}")
    return pen("M" + " L".join(pts), 2.6 * scale, col, f' opacity="{op}"')


def doodle_bars(x, y, scale=1.0, heights=(18, 30, 24, 42)):
    """Small hand-inked bar chart; (x,y) = left end of baseline."""
    cols = [BLUE, LAV, PINK, GOLD]
    s = scale
    o = [f'<rect x="{x + i*18*s:.1f}" y="{y - hh*s:.1f}" width="{12*s:.1f}" height="{hh*s:.1f}" rx="{2*s:.1f}" '
         f'fill="{cols[i % 4]}" fill-opacity=".85" stroke="{PEN_D}" stroke-width="{2*s:.1f}"/>' for i, hh in enumerate(heights)]
    o.append(pen(f"M{x-6*s:.1f} {y+1*s:.1f} H{x + (len(heights)*18+4)*s:.1f}", 2.4 * s))
    return "<g>" + "".join(o) + "</g>"


def doodle_nodes(x, y, scale=1.0):
    """Agent-step node graph (5 coloured nodes); (x,y) = first node, spans ~126 x 36 at scale 1."""
    s = scale
    rel = [(0, 10), (40, -14), (82, 6), (126, -12), (64, 22)]
    P = [(x + a * s, y + b * s - 10 * s) for a, b in rel]
    edges = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 2), (1, 3)]
    o = [pen(" ".join(f"M{P[a][0]:.1f} {P[a][1]:.1f} L{P[b][0]:.1f} {P[b][1]:.1f}" for a, b in edges), 2.2 * s)]
    for i, (nx, ny) in enumerate(P):
        o.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{7.5*s:.1f}" fill="{[PINK, LAV, BLUE, GOLD, WHITE][i]}" '
                 f'stroke="{PEN_D}" stroke-width="{2.2*s:.1f}"/>')
    return "<g>" + "".join(o) + "</g>"


def doodle_controller(x, y, scale=1.0):
    """Game controller doodle with marker-offset fill; (x,y) = top-left of body, ~156 x 72 at scale 1."""
    def P(a, b):
        return f"{x + a*scale:.1f} {y + b*scale:.1f}"
    body = (f"M{P(18,0)} H{x+102*scale:.1f} C{P(128,0)} {P(136,24)} {P(138,46)} C{P(140,66)} {P(124,72)} {P(110,58)} "
            f"L{P(98,46)} H{x+22*scale:.1f} L{P(10,58)} C{P(-4,72)} {P(-20,66)} {P(-18,46)} C{P(-16,24)} {P(-8,0)} {P(18,0)}Z")
    s = scale
    return ("<g>" + f'<path d="{body}" transform="translate({5*s:.1f} {5*s:.1f})" fill="{LAV_L}"/>' + pen(body, 3.2 * s)
            + pen(f"M{P(12,22)} v{16*s:.1f} M{P(4,30)} h{16*s:.1f}", 4.2 * s, PEN_D)
            + f'<circle cx="{x+100*s:.1f}" cy="{y+22*s:.1f}" r="{6.5*s:.1f}" fill="{PINK}" stroke="{PEN_D}" stroke-width="{2*s:.1f}"/>'
            + f'<circle cx="{x+114*s:.1f}" cy="{y+36*s:.1f}" r="{6.5*s:.1f}" fill="{BLUE}" stroke="{PEN_D}" stroke-width="{2*s:.1f}"/>'
            + pen(f"M{P(48,20)} h{8*s:.1f} M{P(66,20)} h{8*s:.1f}", 3 * s, PEN) + "</g>")


def doodle_moon(x, y, scale=1.0, water=False, fill=GOLD):
    """Inked crescent moon centred near (x,y) (r=26*scale); water=True adds ripple lines below (夜水)."""
    s = scale
    r = 26 * s
    moon = f"M{x:.1f} {y-r:.1f} A{r:.1f} {r:.1f} 0 1 0 {x+22*s:.1f} {y+14*s:.1f} A{20*s:.1f} {20*s:.1f} 0 1 1 {x:.1f} {y-r:.1f}Z"
    o = f'<path d="{moon}" fill="{fill}" fill-opacity=".8"/>' + pen(moon, 2.6 * s, PEN_D)
    if water:
        o += pen(f"M{x-36*s:.1f} {y+48*s:.1f} q{10*s:.1f} {-6*s:.1f} {20*s:.1f} 0 t{20*s:.1f} 0 t{20*s:.1f} 0 t{20*s:.1f} 0 "
                 f"M{x-22*s:.1f} {y+62*s:.1f} q{10*s:.1f} {-6*s:.1f} {20*s:.1f} 0 t{20*s:.1f} 0 t{20*s:.1f} 0", 2.6 * s, BLUE_D, ' opacity=".7"')
    return "<g>" + o + "</g>"


def doodle_constellation(x, y, scale=1.0, twinkle=True):
    """Pen-drawn constellation (7 points, 3 gold stars) centred at (x,y), spans ~ 110 x 90 at scale 1."""
    s = scale
    pts = [(-52, -30), (-18, -46), (12, -16), (46, -36), (30, 22), (-8, 40), (-44, 18)]
    P = [(x + a * s, y + b * s) for a, b in pts]
    o = [pen("M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in P), 2.2 * s, PEN, ' stroke-dasharray="1 0"')]
    for i, (a, b) in enumerate(P):
        if i in (1, 3, 4):
            cls = ("tw" if i == 3 else "tw2" if i == 1 else "") if twinkle else ""
            o.append(star(a, b, 11 * s, GOLD, PEN_D, 1.6 * s, cls=cls))
        else:
            o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{4.4*s:.1f}" fill="{WHITE}" stroke="{PEN_D}" stroke-width="{2*s:.1f}"/>')
    return "<g>" + "".join(o) + "</g>"


def doodle_magnifier(x, y, scale=1.0):
    """Magnifier with a pink check inside; (x,y) = lens centre, lens r=20*scale."""
    s = scale
    return (f'<g><circle cx="{x}" cy="{y}" r="{20*s:.1f}" fill="{WHITE}" fill-opacity=".8" stroke="{PEN_D}" stroke-width="{3.2*s:.1f}"/>'
            + pen(f"M{x+14*s:.1f} {y+14*s:.1f} l{16*s:.1f} {16*s:.1f}", 6 * s, PEN_D)
            + pen(f"M{x-9*s:.1f} {y:.1f} l{6*s:.1f} {7*s:.1f} l{12*s:.1f} {-14*s:.1f}", 3.6 * s, PINK_D) + "</g>")


def doodle_plane(x, y, scale=1.0, rot=6, fill=WHITE, stroke=PEN_D):
    """Small paper-white plane centred at (x,y), pointing right."""
    d = ("M-16 0 L14 -2 Q22 -2 22 1 Q22 4 14 4 L-16 2 Z M-2 1 L-10 -14 L-4 -14 L8 0 Z M-2 3 L-8 16 L-2 16 L8 3 Z "
         "M-14 1 L-20 -8 L-16 -8 L-8 1 Z")
    return (f'<path d="{d}" transform="translate({n(x)} {n(y)}) rotate({n(rot)}) scale({1.5*scale:.2f})" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>')


def route_strip(x, y, w, scale=1.0, col=PEN, label_col=PEN_D):
    """上海 ✈ San Diego strip on ground line y from x to x+w: left Shanghai skyline sketch (two-sphere tower +
    blocks) labelled 上海, right San Diego palm + low blocks + wave labelled San Diego, dashed arc with a
    plane between. Height ~ 110*scale above y, labels ~30*scale below."""
    s = scale
    sx, ex = x, x + w
    o = ['<g>']
    # Shanghai (left), ink-pen
    o.append(f'<rect x="{sx+4*s:.1f}" y="{y-30*s:.1f}" width="{16*s:.1f}" height="{30*s:.1f}" transform="translate({4*s:.1f} {4*s:.1f})" fill="{LAV_L}"/>')
    o.append(pen(f"M{sx-10*s:.1f} {y:.1f} H{sx+86*s:.1f} M{sx+4*s:.1f} {y:.1f} V{y-30*s:.1f} H{sx+20*s:.1f} V{y:.1f} "
                 f"M{sx+56*s:.1f} {y:.1f} V{y-24*s:.1f} H{sx+72*s:.1f} V{y-14*s:.1f} H{sx+80*s:.1f} V{y:.1f}", 2.6 * s, col))
    tx = sx + 38 * s
    o.append(pen(f"M{tx:.1f} {y:.1f} V{y-88*s:.1f} M{tx-7*s:.1f} {y:.1f} L{tx:.1f} {y-38*s:.1f} L{tx+7*s:.1f} {y:.1f}", 2.6 * s, col))
    o.append(f'<circle cx="{tx:.1f}" cy="{y-38*s:.1f}" r="{8*s:.1f}" fill="{PINK}" stroke="{col}" stroke-width="{2.6*s:.1f}"/>')
    o.append(f'<circle cx="{tx:.1f}" cy="{y-66*s:.1f}" r="{5.5*s:.1f}" fill="{PINK}" stroke="{col}" stroke-width="{2.4*s:.1f}"/>')
    o.append(f'<text x="{tx:.1f}" y="{y+30*s:.1f}" text-anchor="middle" class="f" font-size="{22*s:.1f}" font-weight="700" '
             f'letter-spacing="{2*s:.1f}" fill="{label_col}">上海</text>')
    # San Diego (right): palm + low blocks + wave
    dx = ex - 40 * s
    o.append(f'<rect x="{dx-78*s:.1f}" y="{y-20*s:.1f}" width="{26*s:.1f}" height="{20*s:.1f}" transform="translate({4*s:.1f} {4*s:.1f})" fill="{LAV_L}"/>')
    o.append(pen(f"M{dx-86*s:.1f} {y:.1f} H{ex+6*s:.1f} M{dx-78*s:.1f} {y:.1f} V{y-20*s:.1f} H{dx-52*s:.1f} V{y:.1f} "
                 f"M{dx-48*s:.1f} {y:.1f} V{y-32*s:.1f} H{dx-30*s:.1f} V{y:.1f}", 2.6 * s, col))
    o.append(pen(f"M{dx:.1f} {y:.1f} q{4*s:.1f} {-30*s:.1f} {-2*s:.1f} {-62*s:.1f}", 3 * s, col))
    px_, py_ = dx - 2 * s, y - 62 * s
    leaf = (f"M{px_:.1f} {py_:.1f} q{-20*s:.1f} {-6*s:.1f} {-30*s:.1f} {8*s:.1f} q{14*s:.1f} {-14*s:.1f} {30*s:.1f} {-8*s:.1f} "
            f"q{-6*s:.1f} {-20*s:.1f} {-26*s:.1f} {-20*s:.1f} q{20*s:.1f} {-2*s:.1f} {26*s:.1f} {20*s:.1f} "
            f"q{8*s:.1f} {-18*s:.1f} {28*s:.1f} {-14*s:.1f} q{-20*s:.1f} {2*s:.1f} {-28*s:.1f} {14*s:.1f} "
            f"q{22*s:.1f} {-2*s:.1f} {30*s:.1f} {14*s:.1f} q{-14*s:.1f} {-10*s:.1f} {-30*s:.1f} {-14*s:.1f}Z")
    o.append(f'<path d="{leaf}" fill="{PINK}" fill-opacity=".55" stroke="{col}" stroke-width="{2.4*s:.1f}" stroke-linejoin="round"/>')
    o.append(pen(f"M{dx+8*s:.1f} {y-10*s:.1f} q{8*s:.1f} {-8*s:.1f} {16*s:.1f} 0 t{16*s:.1f} 0", 2.4 * s, BLUE_D, ' opacity=".8"'))
    o.append(f'<text x="{dx-30*s:.1f}" y="{y+30*s:.1f}" text-anchor="middle" class="f" font-size="{22*s:.1f}" font-weight="700" '
             f'letter-spacing="{1*s:.1f}" fill="{label_col}">San Diego</text>')
    # dashed route + plane
    a0, a1 = sx + 60 * s, dx - 40 * s
    mid = (a0 + a1) / 2
    top = y - 100 * s
    o.append(pen(f"M{a0:.1f} {y-50*s:.1f} Q{mid:.1f} {top-40*s:.1f} {a1:.1f} {y-50*s:.1f}", 2.6 * s, col, f' stroke-dasharray="{3*s:.1f} {9*s:.1f}"'))
    o.append(doodle_plane(mid, 0.5 * (y - 50 * s) + 0.5 * (top - 40 * s), scale, 0))
    o.append('</g>')
    return "\n".join(o)


def sakura_branch(x, y, scale=1.0, flip=False):
    """Short sakura sprig hanging from (x,y) (a page corner), blossoms along it; flip mirrors horizontally."""
    s = scale * (-1 if flip else 1)
    o = [f'<g transform="translate({n(x)} {n(y)}) scale({n(s)} {n(abs(s))})">',
         f'<path d="M0 0 C-44 14 -70 10 -100 34 M-56 12 C-60 32 -70 42 -84 52 M-30 6 C-20 26 -24 44 -16 62" '
         f'fill="none" stroke="{BRANCH}" stroke-width="5" stroke-linecap="round"/>']
    for bx, by, bs in [(-100, 34, 1.1), (-84, 54, .9), (-60, 16, 1.0), (-16, 62, 1.0), (-32, 36, .8), (-70, -2, .8)]:
        o.append(blossom(bx, by, bs))
    o.append('</g>')
    return "".join(o)
