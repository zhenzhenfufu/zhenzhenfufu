"""Embed the official character cutouts (art/*.webp) into an SVG as base64 <image> elements.

    place(name, x, y, h, uid, anchor="bottom", flip=False, glow=None) -> svg string

(x, y) is the anchor point in SVG units: "bottom" = bottom-centre of the art, "center" = centre.
h is the drawn height; width follows the cutout's aspect ratio. Every call with the same name
inside one SVG reuses a single <image> through <symbol>/<use>, so the bytes are embedded once.
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "art")

with open(os.path.join(ART, "sizes.json")) as _fh:
    SIZES = json.load(_fh)

_B64 = {}


def _data(name):
    if name not in _B64:
        with open(os.path.join(ART, name + ".webp"), "rb") as fh:
            _B64[name] = "data:image/webp;base64," + base64.b64encode(fh.read()).decode("ascii")
    return _B64[name]


def size(name, h):
    w0, h0 = SIZES[name]
    return h * w0 / h0, h


def box(name, x, y, h, anchor="bottom"):
    w, h = size(name, h)
    if anchor == "bottom":
        return x - w / 2, y - h, w, h
    return x - w / 2, y - h / 2, w, h


def place(name, x, y, h, uid, anchor="bottom", flip=False, shadow=None, fade=None, extra=""):
    """shadow: optional (colour, opacity, blur) soft silhouette glow drawn behind the art.
    fade: optional (y_solid, y_clear) in SVG units: the art fades out downward between them."""
    x0, y0, w, h = box(name, x, y, h, anchor)
    tf = f' transform="translate({2 * x:.1f},0) scale(-1,1)"' if flip else ""
    img = (f'<image href="{_data(name)}" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" '
           f'preserveAspectRatio="xMidYMid meet"/>')
    out = [f'<defs><g id="{uid}">{img}</g>']
    if shadow:
        col, op, blur = shadow
        out.append(f'<filter id="{uid}-sh" x="-20%" y="-20%" width="140%" height="140%">'
                   f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}" result="b"/>'
                   f'<feFlood flood-color="{col}" flood-opacity="{op}"/><feComposite operator="in" in2="b"/>'
                   f'</filter>')
    if fade:
        a, b = fade
        out.append(f'<linearGradient id="{uid}-fg" gradientUnits="userSpaceOnUse" x1="0" y1="{a}" x2="0" y2="{b}">'
                   f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                   f'<mask id="{uid}-fm" maskUnits="userSpaceOnUse" x="{x0 - 40:.0f}" y="{y0 - 40:.0f}" width="{w + 80:.0f}" height="{h + 80:.0f}">'
                   f'<rect x="{x0 - 40:.0f}" y="{y0 - 40:.0f}" width="{w + 80:.0f}" height="{h + 80:.0f}" fill="url(#{uid}-fg)"/></mask>')
        extra += f' mask="url(#{uid}-fm)"'
    out.append("</defs>")
    g = f'<g{tf}{extra}>'
    if shadow:
        g += f'<use href="#{uid}" filter="url(#{uid}-sh)"/>'
    g += f'<use href="#{uid}"/></g>'
    out.append(g)
    return "".join(out)
