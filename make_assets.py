"""Generate the animated SVGs for the GitHub profile README.

Palette: anime pastel. Sakura-milk -> lavender -> sky gradient backgrounds,
violet ink, a sakura / lavender accent pair. Light backgrounds on purpose:
the cards look the same in GitHub's light and dark themes.

    python3 make_assets.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent / "assets"

PASTEL = dict(
    g1="#fff0f6", g2="#f3edff", g3="#e6f4ff",      # background gradient: sakura milk, lavender, sky
    bg="#ffffffb8", card="#fffafd", tint="#f1ecff",  # bands sit on the gradient as frosted white
    ink="#2b2440", soft="#574f6e", muted="#857a9c", line="#efd3e2",
    iris="#6a5ae0", iris_hi="#8f80ff", iris_line="#e2dafc",
    sakura="#d93b74", sakura_soft="#ffe1ec", sky="#4b9fe0", ok="#1f9c78")

SANS = "'Hiragino Sans','Segoe UI',system-ui,-apple-system,'PingFang SC','Noto Sans CJK SC',sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def pulse(x0, x1, base, height, t_rise, n=140, seed=1, noise=1.4, second=None):
    """Charge-pulse shape: baseline, fast rise, slow exponential tail.
    `second` = (t, frac) adds a second step, the multi-site background look."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + t * (x1 - x0)
        def step(t0):
            return 0.0 if t <= t0 else (1 - math.exp(-(t - t0) / 0.012)) * math.exp(-(t - t0) / 1.6)
        if second:
            v = (1 - second[1]) * step(t_rise) + second[1] * step(second[0])
        else:
            v = step(t_rise)
        y = base - v * height + rnd.uniform(-noise, noise)
        out.append((x, y))
    return out


def petals(c, w, h, n=7, seed=3):
    rnd = random.Random(seed)
    groups, css = [], []
    for i in range(n):
        x = rnd.uniform(0.05, 0.95) * w
        dur = rnd.uniform(11, 17)
        delay = -rnd.uniform(0, dur)
        drift = rnd.uniform(30, 90)
        s = rnd.uniform(0.7, 1.15)
        css.append(f".p{i}{{animation:fall{i} {dur:.1f}s linear {delay:.1f}s infinite}}"
                   f"@keyframes fall{i}{{from{{transform:translate({x:.0f}px,-20px)}}"
                   f"to{{transform:translate({x + drift:.0f}px,{h + 20}px)}}}}")
        groups.append(f'<g class="p{i}"><path class="spin" transform="scale({s:.2f})" '
                      f'd="M0,-5 C4,-5 7,-1 6,3 C4,6 1,5 0,3 C-1,5 -4,6 -6,3 C-7,-1 -4,-5 0,-5Z" '
                      f'fill="{'#ffb3cd' if i % 2 else '#ffc8db'}" opacity="0.85"/></g>')
    css.append(".spin{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}"
               "@keyframes spin{to{transform:rotate(360deg)}}")
    return "".join(groups), "".join(css)


def frame(c, w, h, body, css="", r=14):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f"<style>text{{font-family:{SANS}}} .mono{{font-family:{MONO}}}"
            f"@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}{css}</style>"
            f'<defs><linearGradient id="bgg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c["g1"]}"/><stop offset=".55" stop-color="{c["g2"]}"/>'
            f'<stop offset="1" stop-color="{c["g3"]}"/></linearGradient></defs>'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="url(#bgg)" stroke="{c["line"]}"/>'
            f"{body}</svg>")


def sparkles(c, spots):
    """Four-point twinkle stars, the anime 'kira' accent."""
    out, css = [], [".kira{transform-box:fill-box;transform-origin:center;animation:kira 2.8s ease-in-out infinite}"
                    "@keyframes kira{0%,100%{opacity:.25;transform:scale(.6)}50%{opacity:1;transform:scale(1)}}"]
    for i, (x, y, size, col, delay) in enumerate(spots):
        k = size
        out.append(f'<path class="kira" style="animation-delay:-{delay}s" fill="{col}" '
                   f'd="M{x},{y - k} Q{x + k * .18},{y - k * .18} {x + k},{y} Q{x + k * .18},{y + k * .18} {x},{y + k} '
                   f'Q{x - k * .18},{y + k * .18} {x - k},{y} Q{x - k * .18},{y - k * .18} {x},{y - k}Z"/>')
    return "".join(out), "".join(css)


# --------------------------------------------------------------------------- header
def header(c):
    W, H = 880, 250
    petal_svg, petal_css = petals(c, W, H)
    kira_svg, kira_css = sparkles(c, [(486, 64, 9, c["iris_hi"], 0), (512, 92, 5, c["sakura"], 1.1),
                                      (470, 112, 4, c["sky"], 2.0), (858, 24, 6, c["sakura"], .6),
                                      (30, 30, 5, c["iris_hi"], 1.7)])
    petal_css += kira_css

    # right panel: a pulse traced like a scope, then a validity check lands on it
    px, py, pw, ph = 548, 40, 300, 170
    wave = pulse(px + 18, px + pw - 18, py + 128, 92, 0.32, seed=7)
    css = petal_css + (
        ".trace{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 6s ease-in-out infinite}"
        "@keyframes draw{0%{stroke-dashoffset:1;opacity:1}45%{stroke-dashoffset:0}85%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}"
        ".chk{opacity:0;animation:chk 6s ease-in-out infinite}"
        "@keyframes chk{0%,46%{opacity:0;transform:translateY(4px)}54%,85%{opacity:1;transform:none}100%{opacity:0}}"
        ".type{animation:type 3.2s steps(56) .4s both}"
        "@keyframes type{from{width:0}to{width:505px}}"
        ".caret{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )
    grid = "".join(f'<line x1="{px + 18}" x2="{px + pw - 18}" y1="{py + 30 + i * 28}" y2="{py + 30 + i * 28}" '
                   f'stroke="{c["iris_line"]}" stroke-width="1"/>' for i in range(4))
    body = f"""
<g>{petal_svg}</g>{kira_svg}
<text x="40" y="58" font-size="13" font-weight="700" letter-spacing="2.4" fill="{c['sakura']}">DATA SCIENCE @ UC SAN DIEGO</text>
<text x="38" y="112" font-size="52" font-weight="800" fill="{c['ink']}" letter-spacing="-1">Zhen Wang<tspan dx="16" font-size="30" font-weight="700" letter-spacing="2" fill="{c['sakura']}">王臻</tspan></text>
<clipPath id="tc"><rect class="type" x="40" y="132" height="34" width="505"/></clipPath>
<g clip-path="url(#tc)"><text x="40" y="156" font-size="16.5" fill="{c['soft']}">I build AI agents — and the checks that keep them honest.</text></g>
<g font-size="12.5">
  <rect x="40" y="186" width="262" height="28" rx="14" fill="{c['tint']}" stroke="{c['iris_line']}"/>
  <text x="56" y="205" fill="{c['iris']}" font-weight="600">SIDERIUS contributor · Rare AI Lab</text>
  <rect x="312" y="186" width="168" height="28" rx="14" fill="{c['card']}" stroke="{c['line']}"/>
  <text x="328" y="205" fill="{c['muted']}">San Diego / Shanghai</text>
</g>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{c['bg']}" stroke="{c['line']}"/>
<text class="mono" x="{px + 18}" y="{py + 22}" font-size="11" fill="{c['muted']}">waveform · model output</text>
{grid}
<polyline class="trace" pathLength="1" points="{pts(wave)}" fill="none" stroke="{c['iris_hi']}" stroke-width="2.2" stroke-linejoin="round"/>
<g class="chk">
  <rect x="{px + pw - 132}" y="{py + 132}" width="114" height="26" rx="13" fill="{c['sakura_soft']}" stroke="{c['sakura']}"/>
  <path d="M{px + pw - 118},{py + 145} l5,5 l9,-10" fill="none" stroke="{c['sakura']}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <text class="mono" x="{px + pw - 98}" y="{py + 149}" font-size="11.5" font-weight="700" fill="{c['sakura']}">checked</text>
</g>"""
    return frame(c, W, H, body, css, r=18)


# --------------------------------------------------------------------------- cards
CW, CH = 430, 236


def card_text(c, title, sub, meta, title_extra=""):
    return f"""
<text x="24" y="160" font-size="21" font-weight="800" fill="{c['ink']}">{esc(title)}{title_extra}</text>
<text x="24" y="183" font-size="13" fill="{c['soft']}">{esc(sub)}</text>
<text x="24" y="211" font-size="12" fill="{c['iris']}" font-weight="600">{esc(meta)}</text>"""


def band(c, h=118):
    return f'<rect x="12" y="12" width="{CW - 24}" height="{h}" rx="10" fill="{c["bg"]}" stroke="{c["line"]}"/>'


def card_siderius(c):
    cx, cy, rx, ry = 215, 72, 150, 40
    loop = f"M{cx - rx},{cy} a{rx},{ry} 0 1,1 {2 * rx},0 a{rx},{ry} 0 1,1 {-2 * rx},0"
    steps = ["propose", "write", "train", "evaluate", "check"]
    nodes = []
    # nodes placed at fractions of the loop; the dot travels 0 -> 1 in 7s, starting at the left
    for name, f in zip(steps, [0, 0.18, 0.34, 0.56, 0.78]):
        y = cy - ry * math.sin(2 * math.pi * f)
        x = cx - rx * math.cos(2 * math.pi * f)
        is_chk = name == "check"
        col = c["sakura"] if is_chk else c["iris"]
        fill = c["sakura_soft"] if is_chk else c["tint"]
        tw = 7.2 * len(name) + 18
        anim = f' class="ping"' if is_chk else ""
        nodes.append(f'<g{anim}><rect x="{x - tw / 2:.1f}" y="{y - 11:.1f}" width="{tw:.1f}" height="22" rx="11" '
                     f'fill="{fill}" stroke="{col}"/><text class="mono" x="{x:.1f}" y="{y + 4:.1f}" font-size="11.5" '
                     f'text-anchor="middle" fill="{col}" font-weight="600">{name}</text></g>')
    css = (".ping{transform-box:fill-box;transform-origin:center;animation:ping 7s linear infinite}"
           "@keyframes ping{0%,72%{transform:scale(1)}78%{transform:scale(1.16)}86%,100%{transform:scale(1)}}")
    body = f"""{band(c)}
<path d="{loop}" fill="none" stroke="{c['iris_line']}" stroke-width="2" stroke-dasharray="4 5"/>
<circle r="5" fill="{c['iris_hi']}"><animateMotion dur="7s" repeatCount="indefinite" path="{loop}"/></circle>
{''.join(nodes)}
{card_text(c, 'SIDERIUS', 'open-source auto-ML agent for science', 'Contributor · Rare AI Lab — orchestration, Project 8 tests')}"""
    return frame(c, CW, CH, body, css)


def card_planner(c):
    cols = [(90, "FALL"), (215, "WINTER"), (340, "SPRING")]
    head = "".join(f'<text class="mono" x="{x}" y="34" font-size="10.5" text-anchor="middle" '
                   f'letter-spacing="1.5" fill="{c["muted"]}">{t}</text>' for x, t in cols)

    def node(x, y, label, cls, col, fill, dash=""):
        return (f'<g class="{cls}"><rect x="{x - 44}" y="{y - 14}" width="88" height="28" rx="8" fill="{fill}" '
                f'stroke="{col}" {dash}/><text class="mono" x="{x}" y="{y + 4}" font-size="12" text-anchor="middle" '
                f'font-weight="600" fill="{col}">{label}</text></g>')

    y = 72
    body = f"""{band(c)}{head}
<line x1="134" x2="171" y1="{y}" y2="{y}" stroke="{c['iris']}" stroke-width="1.8" class="e1"/>
<line x1="259" x2="296" y1="{y}" y2="{y}" stroke="{c['iris']}" stroke-width="1.8" class="e2"/>
{node(90, y, 'DSC 10', 'n1', c['iris'], c['tint'])}
{node(215, y + 0, 'DSC 30', 'bad', c['sakura'], c['sakura_soft'], 'stroke-dasharray="4 3"')}
<g class="bad"><text class="mono" x="215" y="{y + 36}" font-size="10.5" text-anchor="middle" fill="{c['sakura']}">✗ needs DSC 20</text></g>
{node(215, y, 'DSC 20', 'n2', c['iris'], c['tint'])}
{node(340, y, 'DSC 30', 'n3', c['iris'], c['tint'])}
<g class="ok"><text class="mono" x="340" y="{y + 36}" font-size="10.5" text-anchor="middle" fill="{c['ok']}">✓ checker passed</text></g>
{card_text(c, 'UCSD Course Planner', 'the model proposes; a deterministic checker decides', 'Legal first-pass plans 40% → 100% on 20 tasks')}"""
    # 8s cycle: DSC 10 in, a premature DSC 30 is rejected, DSC 20 placed, DSC 30 lands in spring
    css = ("g,line{animation-duration:8s;animation-iteration-count:infinite}"
           ".n1{animation-name:a1}.bad{animation-name:ab}.n2,.e1{animation-name:a2}.n3,.e2{animation-name:a3}.ok{animation-name:a4}"
           "@keyframes a1{0%{opacity:0}6%,92%{opacity:1}100%{opacity:0}}"
           "@keyframes ab{0%,12%{opacity:0}18%,34%{opacity:1}40%,100%{opacity:0}}"
           "@keyframes a2{0%,42%{opacity:0}50%,92%{opacity:1}100%{opacity:0}}"
           "@keyframes a3{0%,56%{opacity:0}64%,92%{opacity:1}100%{opacity:0}}"
           "@keyframes a4{0%,66%{opacity:0}72%,92%{opacity:1}100%{opacity:0}}")
    return frame(c, CW, CH, body, css)


def card_majorana(c):
    sig = pulse(40, 390, 108, 70, 0.3, seed=11, noise=1.2)
    bkg = pulse(40, 390, 108, 70, 0.3, seed=12, noise=1.2, second=(0.42, 0.45))
    css = ("polyline{stroke-dasharray:1;stroke-dashoffset:1}"
           ".s{animation:ds 8s ease-in-out infinite}.b{animation:db 8s ease-in-out infinite}"
           ".ls{animation:ls 8s infinite}.lb{animation:lb 8s infinite}"
           "@keyframes ds{0%{stroke-dashoffset:1;opacity:1}25%{stroke-dashoffset:0}45%{stroke-dashoffset:0;opacity:1}50%,100%{opacity:0;stroke-dashoffset:0}}"
           "@keyframes db{0%,50%{stroke-dashoffset:1;opacity:1}75%{stroke-dashoffset:0}95%{stroke-dashoffset:0;opacity:1}100%{opacity:0}}"
           "@keyframes ls{0%,20%{opacity:0}26%,45%{opacity:1}50%,100%{opacity:0}}"
           "@keyframes lb{0%,70%{opacity:0}76%,95%{opacity:1}100%{opacity:0}}")
    body = f"""{band(c)}
<line x1="40" x2="390" y1="108" y2="108" stroke="{c['iris_line']}"/>
<polyline class="s" pathLength="1" points="{pts(sig)}" fill="none" stroke="{c['iris_hi']}" stroke-width="2"/>
<polyline class="b" pathLength="1" points="{pts(bkg)}" fill="none" stroke="{c['sakura']}" stroke-width="2"/>
<text class="mono ls" x="390" y="34" font-size="11" text-anchor="end" font-weight="700" fill="{c['iris']}">single-site · signal</text>
<text class="mono lb" x="390" y="34" font-size="11" text-anchor="end" font-weight="700" fill="{c['sakura']}">multi-site · background</text>
{card_text(c, 'Signal or Background?', 'Majorana Demonstrator germanium-detector waveforms', 'Residual 1D CNN · self-training on 65k unlabelled')}"""
    return frame(c, CW, CH, body, css)


def card_nwa(c):
    # the band is always night, in either theme
    night, moon, water = "#b9b0f2", "#fffaf0", "#ffffff"
    rings = "".join(f'<ellipse class="r{i}" cx="300" cy="104" rx="10" ry="3" fill="none" stroke="{water}" stroke-width="1.3"/>'
                    for i in range(3))
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="1.1" fill="#ffffff" class="tw" style="animation-delay:-{d}s"/>'
                    for x, y, d in [(48, 30, 0.3), (92, 52, 1.1), (150, 26, 2.0), (205, 44, 0.8), (380, 30, 1.6), (250, 22, 2.4)])
    css = ("".join(f".r{i}{{transform-box:fill-box;transform-origin:center;animation:rip 4.5s ease-out {-i * 1.5}s infinite}}" for i in range(3))
           + "@keyframes rip{from{transform:scale(.3);opacity:.9}to{transform:scale(6);opacity:0}}"
           ".tw{animation:tw 3s ease-in-out infinite}@keyframes tw{50%{opacity:.25}}"
           ".lan{animation:lan 2.6s ease-in-out infinite}@keyframes lan{50%{opacity:.55}}")
    body = f"""<defs><linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a99ef0"/>
<stop offset=".55" stop-color="#f3b8d6"/><stop offset="1" stop-color="#ffd9c7"/></linearGradient>
<linearGradient id="lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9b8f0"/><stop offset="1" stop-color="#9ec5f0"/></linearGradient></defs>
<rect x="12" y="12" width="{CW - 24}" height="118" rx="10" fill="url(#dusk)"/>
<clipPath id="nb"><rect x="12" y="12" width="{CW - 24}" height="118" rx="10"/></clipPath>
<g clip-path="url(#nb)">
{stars}
<circle cx="300" cy="44" r="15" fill="{moon}" opacity=".95"/>
<path d="M12,86 L70,86 L70,66 L60,66 L82,52 L104,66 L94,66 L94,86 L150,86" fill="#6f62b8" stroke="#5a4ea6" stroke-width="1"/>
<rect class="lan" x="78" y="72" width="8" height="10" rx="2" fill="#ffe08a"/>
<rect x="12" y="86" width="{CW - 24}" height="44" fill="url(#lake)"/>
{rings}
<line x1="20" x2="410" y1="86" y2="86" stroke="#ffffff" stroke-opacity=".7"/>
</g>
{card_text(c, 'Night Water Academy', 'first-person puzzle game · Unreal Engine 5', 'Producer · team of 5 · Tsinghua × miHoYo competition', title_extra=f'<tspan fill="{c["sakura"]}" font-size="16" dx="8">夜水书院</tspan>')}"""
    return frame(c, CW, CH, body, css)


def main():
    OUT.mkdir(exist_ok=True)
    makers = {"header": header, "siderius": card_siderius, "planner": card_planner,
              "majorana": card_majorana, "nwa": card_nwa}
    for name, fn in makers.items():
        (OUT / f"{name}.svg").write_text(fn(PASTEL), encoding="utf-8")
    print("wrote", len(makers), "files to", OUT)


if __name__ == "__main__":
    main()
