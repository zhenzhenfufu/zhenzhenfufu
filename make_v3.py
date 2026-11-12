"""Build assets/v3/header.svg: the GPT-generated banner (anime HUD set) with
crisp SVG text on the calm left side, plus a few twinkles. The banner art was
generated with ChatGPT; the text is real SVG so it stays sharp at any width.

    python3 make_v3.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).parent
bg = base64.b64encode((ROOT / "assets/v3/header-bg.jpg").read_bytes()).decode()

W, H = 1760, 587
SANS = "'Hiragino Sans','Segoe UI',system-ui,-apple-system,'PingFang SC','Noto Sans CJK SC',sans-serif"

def kira(x, y, k, col, delay):
    return (f'<path class="kira" style="animation-delay:-{delay}s" fill="{col}" '
            f'd="M{x},{y-k} Q{x+k*.18},{y-k*.18} {x+k},{y} Q{x+k*.18},{y+k*.18} {x},{y+k} '
            f'Q{x-k*.18},{y+k*.18} {x-k},{y} Q{x-k*.18},{y-k*.18} {x},{y-k}Z"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
text{{font-family:{SANS}}}
.kira{{transform-box:fill-box;transform-origin:center;animation:kira 3.2s ease-in-out infinite}}
@keyframes kira{{0%,100%{{opacity:.2;transform:scale(.55)}}50%{{opacity:1;transform:scale(1)}}}}
@media (prefers-reduced-motion: reduce){{.kira{{animation:none}}}}
</style>
<defs>
  <clipPath id="r"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="38"/></filter>
</defs>
<g clip-path="url(#r)">
  <image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{bg}" xlink:href="data:image/jpeg;base64,{bg}"/>
  <ellipse cx="470" cy="300" rx="520" ry="210" fill="#ffffff" opacity=".55" filter="url(#soft)"/>
  <text x="96" y="196" font-size="30" font-weight="700" letter-spacing="5" fill="#c0295a">DATA SCIENCE @ UC SAN DIEGO</text>
  <text x="90" y="318" font-size="112" font-weight="800" letter-spacing="-2" fill="#2b2440">Zhen Wang<tspan dx="26" font-size="60" font-weight="700" letter-spacing="4" fill="#c0295a">王臻</tspan></text>
  <text x="96" y="392" font-size="38" fill="#4a4266">I build AI agents — and the checks</text>
  <text x="96" y="442" font-size="38" fill="#4a4266">that keep them honest.</text>
  {kira(1010, 120, 18, "#ffffff", 0)}{kira(1060, 170, 9, "#8fe3c4", 1.1)}{kira(120, 110, 11, "#b9a8ff", 2.0)}{kira(860, 470, 12, "#ffffff", .6)}
</g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="none" stroke="#e7dcf5" stroke-width="2"/>
</svg>'''
(ROOT / "assets/v3/header.svg").write_text(svg, encoding="utf-8")
print("header.svg", len(svg) // 1024, "KB")
