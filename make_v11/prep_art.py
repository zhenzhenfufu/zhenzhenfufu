#!/usr/bin/env python3
"""Crop the official HoYoverse character art to its alpha box and save small WebP cutouts in art/.

The source PNGs are not kept in the repo. All are HoYoverse's official chibi "Paimon's Paintings"
emoji (in-game chat stickers), as mirrored on genshin-impact.fandom.com under
"File:Icon Emoji Paimon's Paintings <set> <character> <n>.png" (renamed PP<set>_<character>_<n>.png).
Run once with the folder holding the downloaded files:  python3 -I prep_art.py <raw_dir>
Needs Pillow (with WebP). build.py itself only reads the .webp files.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "art")

# name: (source file, longest side in px of the saved cutout, webp quality)
JOBS = {
    "furina_scroll": ("PP29_Furina_1.png", 552, 86),   # header
    "keqing_think":  ("PP09_Keqing_1.png", 300, 88),   # SIDERIUS
    "hutao_book":    ("PP05_Hu_Tao_2.png", 640, 84),   # Course Planner
    "furina_gasp":   ("PP28_Furina_1.png", 340, 88),   # Majorana
    "hutao_wink":    ("PP05_Hu_Tao_4.png", 640, 84),   # Night Water Academy
    "hutao_thanks":  ("PP21_Hu_Tao_1.png", 340, 88),   # footer
    "keqing_sleep":  ("PP02_Keqing_2.png", 520, 84),   # footer
}


def main(raw):
    os.makedirs(ART, exist_ok=True)
    sizes = {}
    for name, (src, side, q) in JOBS.items():
        im = Image.open(os.path.join(raw, src)).convert("RGBA")
        im = im.crop(im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox())
        k = side / max(im.size)
        if k < 1:
            im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        sizes[name] = list(im.size)
        out = os.path.join(ART, name + ".webp")
        im.save(out, "WEBP", quality=q, method=6)
        print(f"{name:<12} {im.size[0]}x{im.size[1]}  {os.path.getsize(out) / 1024:.0f} KB")
    with open(os.path.join(ART, "sizes.json"), "w") as fh:
        json.dump(sizes, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
