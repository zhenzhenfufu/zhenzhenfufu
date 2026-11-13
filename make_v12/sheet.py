"""v12 README sheet: the panels between the header and the footer.

GitHub cannot colour the README page itself, so the whole README is a stack of images that share one
pale-lavender paper colour and tile with no gaps (README.md places them as <img align="top"> with no
whitespace between them).  This module writes:

    links-website.svg, links-linkedin.svg, links-email.svg   one 1600x124 strip cut in three link buttons
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
PAPER = "#f3eefc"        # the sheet colour every panel shares
PAPER_HI = "#faf7ff"     # button / chip fill
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


def doc(w, h, label, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{esc(label)}"><rect width="{w}" height="{h}" fill="{PAPER}"/>'
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
    body.append(f'<path d="M{x0 + 44} {y + 14} h{tw:.0f}" stroke="{SAK}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    if sub:
        body.append(f'<text x="{x0 + 44 + tw + 26:.0f}" y="{y}" font-family="{FONT}" font-size="26" font-weight="500" '
                    f'fill="{MUTE}">{esc(sub)}</text>')
    body += [spark(W - 120, 40, 9, "#ffffff"), spark(W - 92, 70, 5, GOLD), spark(W - 160, 76, 4, "#ffffff")]
    return "".join(body)


def title_strip(text, h=120, sub=None):
    return doc(W, h, text + (f" ({sub})" if sub else ""), title_body(text, h, sub))


# ------------------------------------------------------------------ link buttons
LINKS = [
    ("website", "Website", "zhenzhenfufu.github.io"),
    ("linkedin", "LinkedIn", "Zhen Wang"),
    ("email", "Email", "zhw124@ucsd.edu"),
]


def icon(kind, x, y):
    s = f'fill="none" stroke="{PINK}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "website":
        return (f'<g {s}><circle cx="{x}" cy="{y}" r="15"/><ellipse cx="{x}" cy="{y}" rx="6.5" ry="15"/>'
                f'<path d="M{x - 15} {y} H{x + 15}"/></g>')
    if kind == "linkedin":
        return (f'<rect x="{x - 15}" y="{y - 15}" width="30" height="30" rx="7" fill="{PINK}"/>'
                f'<text x="{x}" y="{y + 8}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="800" '
                f'fill="#ffffff">in</text>')
    return (f'<g {s}><rect x="{x - 16}" y="{y - 11}" width="32" height="22" rx="4"/>'
            f'<path d="M{x - 14} {y - 8} L{x} {y + 3} L{x + 14} {y - 8}"/></g>')


def link_strip(i, h=124):
    w = W / 3
    kind, label, sub = LINKS[i]
    bw, bh = 440, 84
    bx, by = (w - bw) / 2, (h - bh) / 2 + 2
    body = (f'<rect x="{bx:.1f}" y="{by + 4:.1f}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{LINE}" opacity=".7"/>'
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{PAPER_HI}" stroke="{LINE}" stroke-width="2"/>'
            + icon(kind, bx + 54, by + bh / 2)
            + f'<text x="{bx + 88:.1f}" y="{by + 38:.1f}" font-family="{FONT}" font-size="30" font-weight="800" fill="{INK}">{esc(label)}</text>'
            f'<text x="{bx + 88:.1f}" y="{by + 68:.1f}" font-family="{FONT}" font-size="22" font-weight="500" fill="{MUTE}">{esc(sub)}</text>')
    return doc(round(w, 2), h, f"{label}: {sub}", body)


# ------------------------------------------------------------------ project tiles
TILES = [
    # file key, card builder, side, title, line 1, line 2
    ("siderius", lambda: card_siderius.card(), "L", "SIDERIUS",
     "Open-source auto-ML agent for science", "Contributor · orchestration testing on Project 8 data"),
    ("planner", lambda: card_planner.card(), "R", "UCSD Course Planner",
     "The model proposes, a checker decides", "Catalog prerequisite graph · live demo in the repo"),
    ("majorana", lambda: card_majorana.build_svg(), "L", "Signal or Background?",
     "Majorana detector waveforms · residual 1D CNN", "Self-training on 65k unlabelled waveforms"),
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


def tile(key, build, side, title, l1, l2):
    ax = OUT_M if side == "L" else GUT
    aw = TW - OUT_M - GUT
    ah = round(aw * 9 / 16, 2)
    # soft drop shadow: a blurred rounded rect in the shadow colour
    shadow = (f'<rect x="{ax}" y="{ART_Y + 8}" width="{aw}" height="{ah}" rx="22" fill="#5d4fb0" opacity=".16" '
              f'filter="url(#t{key}-bl)"/>')
    defs = f'<filter id="t{key}-bl" x="-10%" y="-10%" width="120%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>'
    art = inset(build(), ax, ART_Y, aw, ah)
    ty = ART_Y + ah + 60
    body = [shadow, art,
            f'<text x="{ax + 6}" y="{ty:.1f}" font-family="{FONT}" font-size="36" font-weight="800" fill="{INK}" '
            f'letter-spacing="-.2">{esc(title)}<tspan dx="12" font-size="26" fill="{PINK}">↗</tspan></text>',
            f'<text x="{ax + 6}" y="{ty + 44:.1f}" font-family="{FONT}" font-size="27" font-weight="600" fill="{INK_V}">{esc(l1)}</text>',
            f'<text x="{ax + 6}" y="{ty + 82:.1f}" font-family="{FONT}" font-size="23" font-weight="500" fill="{MUTE}">{esc(l2)}</text>']
    for s, fs in ((title, 36), (l1, 27), (l2, 23)):
        assert text_w(s, fs) < aw - 40, (key, s)
    return doc(TW, TH, f"{title}: {l1}. {l2}.", "".join(body), defs)


# ------------------------------------------------------------------ toolbox
TOOLBOX = [
    ("Languages", ["Python", "PyTorch", "R", "SQL", "Java", "C++"]),
    ("Methods", ["AI agents", "time series", "statistical inference", "regression"]),
    ("Tools", ["Unreal Engine 5", "Blender", "LaTeX", "Git"]),
]


def toolbox():
    h = 330
    x0 = 72
    body = [title_body("Toolbox")]
    y = 128
    for gi, (group, items) in enumerate(TOOLBOX):
        body.append(f'<text x="{x0 + 44}" y="{y + 32}" font-family="{FONT}" font-size="22" font-weight="700" '
                    f'fill="{PINK}" letter-spacing="1.5">{esc(group.upper())}</text>')
        x = x0 + 240
        for it in items:
            cw = text_w(it, 26, .54) + 44
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="48" rx="24" fill="{PAPER_HI}" stroke="{LINE}" stroke-width="2"/>'
                        f'<text x="{x + cw / 2:.1f}" y="{y + 33}" text-anchor="middle" font-family="{FONT}" font-size="26" '
                        f'font-weight="600" fill="{INK_V}">{esc(it)}</text>')
            x += cw + 16
        assert x < W - 60, group
        y += 66
    return doc(W, h, "Toolbox. " + ". ".join(f"{g}: {', '.join(i)}" for g, i in TOOLBOX) + ".", "".join(body))


# ------------------------------------------------------------------ build
def build(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    files = {}
    for i, (kind, _, _) in enumerate(LINKS):
        files[f"links-{kind}.svg"] = link_strip(i)
    files["title-work.svg"] = title_strip("Selected work")
    for t in TILES:
        files[f"tile-{t[0]}.svg"] = tile(*t)
    files["toolbox.svg"] = toolbox()
    files["title-snake.svg"] = title_strip("Contributions, eaten", sub="my GitHub graph, one square at a time")
    for name, s in files.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(s)
    return os.path.join(out_dir, "title-work.svg")


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT))
