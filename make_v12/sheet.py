"""v12 README sheet: the panels between the header and the footer.

GitHub cannot colour the README page itself, so the whole README is a stack of images that tile with no
gaps, each section in its own pale tint (BG_* below) (README.md places them as <img align="top"> with no
whitespace between them).  This module writes:

    links-{website,linkedin,email,demo}.svg                  one 1600x124 strip cut in four link buttons
    about.svg                                                 "Now / Before" paragraphs on a cream text panel
    title-work.svg                                            "Selected work" section strip
    tile-siderius.svg, tile-planner.svg,                      800x600 tiles: the card scene inset with its
    tile-majorana.svg, tile-nwa.svg                           caption underneath (two tiles per row)
    toolbox.svg                                               "Toolbox" strip with grouped chips
    title-snake.svg                                           "Contributions, eaten" strip above the snake

Python 3 stdlib only.  Text uses the same system-font stack as the header.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import card_majorana  # noqa: E402
import card_nwa  # noqa: E402
import card_planner  # noqa: E402
import card_siderius  # noqa: E402

OUT_DEFAULT = os.path.join(os.path.dirname(HERE), "assets", "v12")

FONT = "'Hiragino Sans','PingFang SC','Segoe UI',system-ui,-apple-system,'Noto Sans CJK SC',sans-serif"
PAPER = "#f3eefc"        # default sheet colour (Selected work)
# each section gets its own pale tint so the sections read apart while the sheet stays continuous
BG_LINKS = "#fcf0f6"     # pale sakura
BG_WORK = PAPER          # pale lavender
BG_TOOL = "#edf0fd"      # pale periwinkle
BG_SNAKE = "#fdf2ec"     # pale peach (the snake workflow paints the same colour behind snake-sheet.svg)
PAPER_HI = "#faf7ff"     # chip fill (chips sit on a cream text panel)
TEXT_BG = "#fffaf3"      # warm cream: every block of text sits on this, so text reads apart from the scenes
TEXT_EDGE = "#efe2d6"    # hairline round the cream panels
LINE = "#d8cdf6"         # hairlines and button borders
INK = "#2b2768"          # titles (header name colour)
INK_V = "#3b3579"        # body text
MUTE = "#6b5fa8"         # secondary text
PINK = "#d24f86"         # accents (header label colour)
SAK = "#f6a9c6"
GOLD = "#f2c46b"

W = 1600


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def doc(w, h, label, body, defs="", bg=PAPER):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{esc(label)}"><rect width="{w}" height="{h}" fill="{bg}"/>'
            + (f"<defs>{defs}</defs>" if defs else "") + body + "</svg>")


def plum(x, y, r, rot=-12):
    """Small five-petal plum blossom (same glyph family as the footer)."""
    pet = "".join(f'<circle cx="{r * .56 * c:.2f}" cy="{r * .56 * s:.2f}" r="{r * .47:.2f}"/>'
                  for c, s in ((0, -1), (.951, -.309), (.588, .809), (-.588, .809), (-.951, -.309)))
    return (f'<g transform="translate({x} {y}) rotate({rot})"><g fill="{SAK}" stroke="{INK}" stroke-width="1.8">{pet}</g>'
            f'<g fill="{SAK}">{pet}</g><circle r="{r * .24:.2f}" fill="{GOLD}" stroke="{INK}" stroke-width="1.1"/></g>')


def spark(x, y, r, col="#ffffff"):
    k = r * .28
    return (f'<path d="M{x} {y - r} Q{x + k} {y - k} {x + r} {y} Q{x + k} {y + k} {x} {y + r} '
            f'Q{x - k} {y + k} {x - r} {y} Q{x - k} {y - k} {x} {y - r}Z" fill="{col}"/>')


# Rendered widths at 28px semibold, measured in headless Edge on macOS (Hiragino Sans).  Chips use these so
# every chip gets the same inner padding; other strings fall back to the per-glyph estimate below.
CHIP_PX28 = {"Python": 106.1, "PyTorch": 123.7, "R": 21.7, "SQL": 61.5, "Java": 69.5, "C++": 60.6,
             "AI agents": 142.7, "time series": 165.4, "statistical inference": 298.2, "regression": 161.0,
             "Unreal Engine 5": 239.3, "Blender": 116.8, "LaTeX": 93.6, "Git": 41.9}


def chip_w(s, fs):
    """Width of s at font-size fs: measured table when available, else a per-glyph estimate (about +-10%)."""
    if s in CHIP_PX28:
        return CHIP_PX28[s] * fs / 28
    t = 0
    for ch in s:
        if ch in "iljtfr' I":
            t += .34
        elif ch in "MW":
            t += .85
        elif ch.isupper():
            t += .74
        elif ch.isdigit() or ch in "+\u00b7":
            t += .60
        elif ord(ch) > 0x2e80:
            t += 1.0
        else:
            t += .60
    return t * fs


def text_w(s, fs, k=.56):
    """Rough rendered width of s in the system sans at font-size fs (CJK counts double)."""
    return sum((1.9 if ord(ch) > 0x2e80 else (.62 if ch.isupper() else 1)) for ch in s) * fs * k


# ------------------------------------------------------------------ section titles
def title_body(text, h=120, sub=None):
    x0, y = 72, h - 38
    body = [plum(x0 + 14, y - 15, 15),
            f'<text x="{x0 + 44}" y="{y}" font-family="{FONT}" font-size="46" font-weight="800" fill="{INK}" '
            f'letter-spacing="-.4">{esc(text)}</text>']
    tw = text_w(text, 46, .6)
    head_w = max(tw, chip_w(text, 46) * 1.08)
    pw = 44 + head_w + 34 + (chip_w(sub, 26) * 1.08 + 26 if sub else 0)
    body.insert(0, f'<rect x="{x0 - 16}" y="{y - 52}" width="{pw + 16:.0f}" height="78" rx="39" fill="{TEXT_BG}" '
                   f'stroke="{TEXT_EDGE}" stroke-width="2"/>')
    body.append(f'<path d="M{x0 + 44} {y + 12} h{tw:.0f}" stroke="{SAK}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    if sub:
        body.append(f'<text x="{x0 + 44 + head_w + 26:.0f}" y="{y}" font-family="{FONT}" font-size="26" font-weight="500" '
                    f'fill="{MUTE}">{esc(sub)}</text>')
    body += [spark(W - 120, 40, 9, "#ffffff"), spark(W - 92, 70, 5, GOLD), spark(W - 160, 76, 4, "#ffffff")]
    return "".join(body)


def title_strip(text, h=120, sub=None, bg=PAPER):
    return doc(W, h, text + (f" ({sub})" if sub else ""), title_body(text, h, sub), bg=bg)


# ------------------------------------------------------------------ link buttons
LINKS = [
    ("website", "Website"),
    ("linkedin", "LinkedIn"),
    ("email", "Email"),
    ("demo", "Planner demo"),
]
LW = W / len(LINKS)          # each link strip is a quarter of the sheet
PILL_W, PILL_H = 320, 84
PILL_GAP = (W - 2 * 64 - len(LINKS) * PILL_W) / (len(LINKS) - 1)   # pills span the same 64..1536 column as the tiles


def icon(kind, x, y):
    s = f'fill="none" stroke="{PINK}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "website":
        return (f'<g {s}><circle cx="{x}" cy="{y}" r="15"/><ellipse cx="{x}" cy="{y}" rx="6.5" ry="15"/>'
                f'<path d="M{x - 15} {y} H{x + 15}"/></g>')
    if kind == "linkedin":
        return (f'<rect x="{x - 15}" y="{y - 15}" width="30" height="30" rx="7" fill="{PINK}"/>'
                f'<text x="{x}" y="{y + 8}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="800" '
                f'fill="#ffffff">in</text>')
    if kind == "demo":
        return (f'<g {s}><circle cx="{x}" cy="{y}" r="15"/></g>'
                f'<path d="M{x - 4.5} {y - 7.5} L{x + 7.5} {y} L{x - 4.5} {y + 7.5}Z" fill="{PINK}"/>')
    return (f'<g {s}><rect x="{x - 16}" y="{y - 11}" width="32" height="22" rx="4"/>'
            f'<path d="M{x - 14} {y - 8} L{x} {y + 3} L{x + 14} {y - 8}"/></g>')


def link_strip(i, h=124):
    kind, label = LINKS[i]
    bx = 64 + i * (PILL_W + PILL_GAP) - i * LW       # pill position inside this quarter strip
    by = (h - PILL_H) / 2 + 2
    assert 0 <= bx and bx + PILL_W <= LW, (kind, bx)
    tx = bx + 70
    body = (f'<rect x="{bx:.1f}" y="{by + 4:.1f}" width="{PILL_W}" height="{PILL_H}" rx="{PILL_H / 2}" fill="{LINE}" opacity=".7"/>'
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{PILL_W}" height="{PILL_H}" rx="{PILL_H / 2}" fill="{TEXT_BG}" stroke="{TEXT_EDGE}" stroke-width="2"/>'
            + icon(kind, bx + 42, by + PILL_H / 2)
            + f'<text x="{tx:.1f}" y="{by + PILL_H / 2 + 11:.1f}" font-family="{FONT}" font-size="28" font-weight="800" fill="{INK}">{esc(label)}</text>')
    assert 70 + chip_w(label, 28) < PILL_W - 16, (label, chip_w(label, 28))
    return doc(LW, h, label, body, bg=BG_LINKS)


# ------------------------------------------------------------------ project tiles
TILES = [
    # file key, card builder, side, title, line 1, line 2
    ("siderius", lambda: card_siderius.card(), "L", "SIDERIUS",
     "Open-source auto-ML agent for science", "Contributor · orchestration tests on Project 8 data"),
    ("planner", lambda: card_planner.card(), "R", "UCSD Course Planner",
     "The model proposes, a checker decides", "Prerequisite graph from the catalog \u00b7 demo above"),
    ("majorana", lambda: card_majorana.build_svg(), "L", "Signal or Background?",
     "Majorana waveforms · residual 1D CNN", "Self-training on 65k unlabelled waveforms"),
    ("nwa", lambda: card_nwa.card(), "R", "Night Water Academy 夜水书院",
     "UE5 puzzle game · producer, team of 5", "Tsinghua × miHoYo competition (judging in progress)"),
]
TW, TH = 800, 600
OUT_M, GUT = 64, 16              # outer margin of the sheet, half gutter between the two tiles of a row
ART_Y = 10


def inset(card_svg, x, y, w, h):
    """Re-root a standalone 1600x900 card SVG as a nested <svg> placed at (x, y, w, h)."""
    m = re.match(r"<svg\b[^>]*>", card_svg)
    attrs = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}">' + card_svg[m.end():]


CAP_H = 152                      # cream caption band under each scene


def tile(key, build, side, title, l1, l2):
    ax = OUT_M if side == "L" else GUT
    aw = TW - OUT_M - GUT
    ah = round(aw * 9 / 16, 2)
    ch = ah + CAP_H
    defs = (f'<filter id="t{key}-bl" x="-10%" y="-10%" width="120%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>'
            f'<clipPath id="t{key}-cc"><rect x="{ax}" y="{ART_Y}" width="{aw}" height="{ch:.2f}" rx="22"/></clipPath>')
    # one rounded card: soft shadow, cream body, scene on top, caption on the cream
    shadow = (f'<rect x="{ax}" y="{ART_Y + 8}" width="{aw}" height="{ch:.2f}" rx="22" fill="#5d4fb0" opacity=".14" '
              f'filter="url(#t{key}-bl)"/>')
    card = f'<rect x="{ax}" y="{ART_Y}" width="{aw}" height="{ch:.2f}" rx="22" fill="{TEXT_BG}"/>'
    art = f'<g clip-path="url(#t{key}-cc)">' + inset(build(), ax, ART_Y, aw, ah) + "</g>"
    edge = (f'<rect x="{ax}" y="{ART_Y}" width="{aw}" height="{ch:.2f}" rx="22" fill="none" stroke="{TEXT_EDGE}" '
            f'stroke-width="2"/>')
    tx, ty = ax + 26, ART_Y + ah + 50
    body = [shadow, card, art, edge,
            f'<text x="{tx}" y="{ty:.1f}" font-family="{FONT}" font-size="36" font-weight="800" fill="{INK}" '
            f'letter-spacing="-.2">{esc(title)}<tspan dx="12" font-size="27" fill="{PINK}">\u2197</tspan></text>',
            f'<text x="{tx}" y="{ty + 44:.1f}" font-family="{FONT}" font-size="27" font-weight="600" fill="{INK_V}">{esc(l1)}</text>',
            f'<text x="{tx}" y="{ty + 82:.1f}" font-family="{FONT}" font-size="23" font-weight="500" fill="{MUTE}">{esc(l2)}</text>']
    for s, fs in ((title, 36), (l1, 27), (l2, 23)):
        assert chip_w(s, fs) < aw - 2 * 26 - 8, (key, s, round(chip_w(s, fs)))
    assert ART_Y + ch + 24 <= TH
    return doc(TW, TH, f"{title}: {l1}. {l2}.", "".join(body), defs)


# ------------------------------------------------------------------ toolbox
TOOLBOX = [
    ("Languages", ["Python", "PyTorch", "R", "SQL", "Java", "C++"]),
    ("Methods", ["AI agents", "time series", "statistical inference", "regression"]),
    ("Tools", ["Unreal Engine 5", "Blender", "LaTeX", "Git"]),
]


def toolbox():
    h = 376
    x0 = 72
    body = [title_body("Toolbox"),
            f'<rect x="64" y="122" width="{W - 128}" height="{3 * 70 + 18}" rx="26" fill="{TEXT_BG}" stroke="{TEXT_EDGE}" stroke-width="2"/>']
    y = 134
    for gi, (group, items) in enumerate(TOOLBOX):
        body.append(f'<text x="{x0 + 44}" y="{y + 36}" font-family="{FONT}" font-size="24" font-weight="700" '
                    f'fill="{PINK}" letter-spacing="1.5">{esc(group.upper())}</text>')
        x = x0 + 262
        for it in items:
            cw = max(56, chip_w(it, 28) + 2 * 24)
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="52" rx="26" fill="{PAPER_HI}" stroke="{LINE}" stroke-width="2"/>'
                        f'<text x="{x + cw / 2:.1f}" y="{y + 36}" text-anchor="middle" font-family="{FONT}" font-size="28" '
                        f'font-weight="600" fill="{INK_V}">{esc(it)}</text>')
            x += cw + 16
        assert x < W - 60, group
        y += 70
    return doc(W, h, "Toolbox. " + ". ".join(f"{g}: {', '.join(i)}" for g, i in TOOLBOX) + ".", "".join(body), bg=BG_TOOL)


# ------------------------------------------------------------------ about (Now / Before)
ABOUT = [
    ("Now", "In Prof. Aobo Li\u2019s Rare AI Lab at UC San Diego I work on SIDERIUS, an open-source agent that turns "
            "a dataset and a research question into an iterative machine-learning experiment and checks validity "
            "beside the score. I test its orchestration mode and run it end to end on Project 8 physics data. "
            "If you have a dataset and a question, try it and open an issue."),
    ("Before", "AI Agent Development Intern at Pfizer China R&D (summer 2026): a regulatory-filing system where "
               "deterministic code decides and review agents only advise."),
]
ABOUT_FS, ABOUT_LH, ABOUT_WRAP = 27, 42, 1150     # wrap width is conservative: the estimate is about +-10%


def wrap(text, fs, width):
    lines, cur = [], ""
    for word in text.split(" "):
        nxt = (cur + " " + word).strip()
        if cur and chip_w(nxt, fs) > width:
            lines.append(cur)
            cur = word
        else:
            cur = nxt
    return lines + [cur]


def about():
    x0, lab_x, txt_x = 64, 112, 262
    blocks = [(lab, wrap(t, ABOUT_FS, ABOUT_WRAP)) for lab, t in ABOUT]
    y = 34 + 48
    body = []
    for lab, lines in blocks:
        body.append(f'<text x="{lab_x}" y="{y}" font-family="{FONT}" font-size="25" font-weight="800" fill="{PINK}" '
                    f'letter-spacing="1.5">{esc(lab.upper())}</text>')
        for k, ln in enumerate(lines):
            body.append(f'<text x="{txt_x}" y="{y + k * ABOUT_LH}" font-family="{FONT}" font-size="{ABOUT_FS}" '
                        f'font-weight="500" fill="{INK_V}">{esc(ln)}</text>')
        y += len(lines) * ABOUT_LH + 26
    ph = y - 26 - ABOUT_LH + 34 + 18          # panel bottom: last baseline + descent + padding
    h = 34 + ph + 34 - 8
    panel = (f'<rect x="{x0}" y="10" width="{W - 2 * x0}" height="{ph:.0f}" rx="26" fill="{TEXT_BG}" '
             f'stroke="{TEXT_EDGE}" stroke-width="2"/>')
    label = " ".join(f"{lab}: {t}" for lab, t in ABOUT)
    return doc(W, round(h), label, panel + "".join(body), bg=BG_LINKS)


# ------------------------------------------------------------------ build
def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    files = {}
    for i, (kind, _) in enumerate(LINKS):
        files[f"links-{kind}.svg"] = link_strip(i)
    files["about.svg"] = about()
    files["title-work.svg"] = title_strip("Selected work")
    for t in TILES:
        files[f"tile-{t[0]}.svg"] = tile(*t)
    files["toolbox.svg"] = toolbox()
    files["title-snake.svg"] = title_strip("Contributions, eaten", sub="my GitHub graph, one square at a time", bg=BG_SNAKE)
    for name, s in files.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(s)
    return os.path.join(out_dir, "toolbox.svg")


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT))
