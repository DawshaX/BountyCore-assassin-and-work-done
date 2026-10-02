"""MegaUI SVG component kit v2 — original parametric vector components.

Every function returns a standalone SVG string. All artwork is generated
from geometry rules (no tracing, no external assets). Theme = tokens.THEMES.

v2: depth (shadow + bevel + inner light), style ornament, form controls,
windows, and decorative pieces — modeled against premium UI-kit references.
"""
import math
import uuid

from tokens import THEMES, GEO, state_tint

FAM = "'Verdana','DejaVu Sans',sans-serif"
MONO = "'Courier New','DejaVu Sans Mono',monospace"


def _uid():
    return uuid.uuid4().hex[:8]


def _svg(w, h, body, viewbox=None):
    vb = viewbox or f"0 0 {w} {h}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="{vb}">{body}</svg>')


def _lum(c):
    return (0.2126 * int(c[1:3], 16) + 0.7152 * int(c[3:5], 16)
            + 0.0722 * int(c[5:7], 16)) / 255


def _on(bg_hex, t):
    """Readable ink for text drawn ON bg_hex."""
    return t["bg"] if _lum(bg_hex) > 0.45 else "#FFFFFF"


def _label(w, h, text, fill, style, size=None, x=None, y=None):
    fs = size or min(20, int(h * 0.40))
    fam = MONO if style == "pixel" else FAM
    ls = {"fantasy": 2.4, "sci": 3.2, "royal": 1.6, "pixel": 2.0}[style]
    return (f'<text x="{x if x is not None else w/2}" '
            f'y="{y if y is not None else h/2}" fill="{fill}" font-family="{fam}" '
            f'font-size="{fs}" font-weight="700" letter-spacing="{ls}" '
            f'text-anchor="middle" dominant-baseline="central">{text}</text>')


def _band(stops):
    out = []
    for i, (off, col, op) in enumerate(stops):
        out.append((off, col, op))
        if i < len(stops) - 1:
            mid = (off + stops[i + 1][0]) / 2
            out.append((mid, col, op))
    return out


def _grad(gid, stops, vertical=True):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>'
                for o, c, op in stops)
    return f'<linearGradient id="{gid}" {xy}>{s}</linearGradient>'


def _path_for(style, w, h, r, inset=0, corners="tb"):
    """Outer shape path: rounded / chamfered(TL+BR) / square / pixel."""
    x0, y0, x1, y1 = inset, inset, w - inset, h - inset
    if style in ("fantasy", "royal"):
        rr = max(0, r - inset)
        return (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" '
                f'rx="{rr}" ry="{rr}"/>')
    if style == "sci":
        c = max(0, GEO["sci"]["chamfer"] - inset)
        return (f'<path d="M{x0+c} {y0} L{x1} {y0} L{x1} {y1-c} '
                f'L{x1-c} {y1} L{x0} {y1} L{x0} {y0+c} Z"/>')
    return f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}"/>'


def _shadow(style, w, h, r, dx=0, dy=4, op=0.45, inset=0):
    return (f'<g transform="translate({dx},{dy})" opacity="{op}">'
            f'{_path_for(style, w, h, r, inset=inset, )}</g>').replace(
        "/>", ' fill="#000000"/>', 1)


# ---------------------------------------------------------------- buttons ---
def button(w, h, theme_key, state="normal", kind="primary", label="",
           shape="standard"):
    """shape: standard | pill | wide (CTA) — more shapes added in Phase 2."""
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    u = _uid()
    r = h / 2 - 1 if shape == "pill" else g["r"]

    fill_base = {
        "primary": t["accent"],
        "secondary": t["panel2"],
        "danger": t["danger"],
        "ghost": "none",
    }[kind]
    fill = state_tint(t, state, fill_base) if fill_base != "none" else "none"
    stroke = t["accent"] if kind in ("primary", "ghost") else t["stroke"]
    if kind == "danger":
        stroke = state_tint(t, state, "#FF7A6A") if style != "royal" else "#8E2C2C"
    stroke_w = g["stroke"]
    ink = t["bg"] if kind == "primary" and state != "disabled" else t["ink"]
    if kind == "danger":
        ink = "#FFFFFF"

    pressed = state == "pressed"
    lift = 3 if pressed else 0          # pressed content pushes down
    dy = 0 if (pressed or state == "disabled") else 4

    parts = []

    # ---- drop shadow (hard for pixel, soft-ish for others) — opaque faces only
    if dy and fill != "none":
        if style == "pixel":
            parts.append(_shadow(style, w, h, r, dx=5, dy=5, op=1.0))
        else:
            parts.append(_shadow(style, w, h, r, dx=0, dy=dy, op=0.40))

    # ---- outer neon halo (sci)
    if style == "sci" and kind in ("primary", "danger") and state != "disabled":
        parts.append(f'<g fill="none" stroke="{stroke}" stroke-width="7" '
                     f'opacity="0.30">{_path_for(style, w, h, r)}</g>')

    # ---- face
    body = _path_for(style, w, h, r)
    parts.append(f'<g fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}">'
                 f'{body}</g>')

    # ---- gloss + top bevel light + bottom shade (clipped)
    gloss = [(0.0, "#ffffff", 0.30), (0.42, "#ffffff", 0.07),
             (0.52, "#000000", 0.06), (1.0, "#000000", 0.26)]
    if style == "pixel":
        gloss = _band(gloss)
    if fill != "none":
        gid = f"g{u}"
        parts.append(f'<defs>{_grad(gid, gloss)}</defs>')
        parts.append(f'<g transform="translate(0,{lift})"><g transform="translate('
                     f'{stroke_w/2},{stroke_w/2})">'
                     f'<clipPath id="c{u}">{_path_for(style, w - stroke_w, h - stroke_w, r)}</clipPath>'
                     f'<g clip-path="url(#c{u})">'
                     f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>')
        # bright top edge inside face
        parts.append(f'<rect x="1.5" y="1.5" width="{w-3}" height="2" '
                     f'fill="#ffffff" opacity="0.34"/>')
        # bottom inner shade band
        parts.append(f'<rect x="1.5" y="{h-5}" width="{w-3}" height="3.5" '
                     f'fill="#000000" opacity="0.30"/>')
        parts.append("</g></g></g>")

    # ---- inner hairline
    if style != "pixel" and fill != "none":
        ins = stroke_w / 2 + 2
        parts.append(f'<g fill="none" stroke="{t["ink"]}" stroke-opacity="0.20" '
                     f'stroke-width="1" transform="translate(0,{lift})">'
                     f'<g transform="translate({ins},{ins})">'
                     f'{_path_for(style, w - 2 * ins, h - 2 * ins, max(2, r - 2))}'
                     f'</g></g>')

    # ---- state overlays
    if state == "hover":
        parts.append(f'<g opacity="0.14" transform="translate(0,{lift})">'
                     f'<g fill="{t["accent2"]}">{_path_for(style, w, h, r)}</g></g>')
    if state == "pressed":
        parts.append(f'<g opacity="0.24" transform="translate(0,{lift})">'
                     f'<g fill="#000000">{_path_for(style, w, h, r)}</g></g>')
    if state == "disabled":
        parts.append(f'<g opacity="0.38"><g fill="#101018">'
                     f'{_path_for(style, w, h, r)}</g></g>')

    # ---- ornaments per style
    if style == "sci":
        c = GEO["sci"]["chamfer"]
        parts.append(f'<g transform="translate(0,{lift})">')
        parts.append(
            f'<path d="M2 {c+5} L2 2 L{c+5} 2" fill="none" stroke="{t["accent2"]}" '
            f'stroke-width="2.5"/>'
            f'<path d="M{w-2} {h-c-5} L{w-2} {h-2} L{w-c-5} {h-2}" fill="none" '
            f'stroke="{t["accent2"]}" stroke-width="2.5"/>')
        # side chevrons + micro ticks (only when there is a label)
        if label:
            cx0 = w * 0.5 - (len(label) * 6.5 + 18) / 2
            parts.append(f'<path d="M{cx0-10} {h/2-5} L{cx0-15} {h/2} L{cx0-10} {h/2+5}" '
                         f'fill="none" stroke="{t["accent"]}" stroke-width="2" opacity="0.9"/>')
            cx1 = w * 0.5 + (len(label) * 6.5 + 18) / 2
            parts.append(f'<path d="M{cx1+10} {h/2-5} L{cx1+15} {h/2} L{cx1+10} {h/2+5}" '
                         f'fill="none" stroke="{t["accent"]}" stroke-width="2" opacity="0.9"/>')
        for i in range(4):
            tx = w * 0.5 - 21 + i * 14
            parts.append(f'<rect x="{tx}" y="{h-8}" width="7" height="2" '
                         f'fill="{t["ink"]}" opacity="0.35"/>')
        parts.append("</g>")
    if style == "fantasy":
        d = 7
        parts.append(f'<g transform="translate(0,{lift})">')
        for cx, cy in ((d, d), (w - d, d), (d, h - d), (w - d, h - d)):
            parts.append(f'<path d="M{cx} {cy-5.5} L{cx+5.5} {cy} L{cx} {cy+5.5} '
                         f'L{cx-5.5} {cy} Z" fill="{t["accent2"]}" '
                         f'stroke="{t["stroke"]}" stroke-width="1"/>')
        if kind == "primary" and h >= 44:
            gx = w * 0.5 - (len(label) * 7 + 26) / 2
            parts.append(f'<path d="M{gx} {h/2} L{gx+5} {h/2-5} L{gx+10} {h/2} '
                         f'L{gx+5} {h/2+5} Z" fill="{_on(t["accent"], t)}" opacity="0.85"/>')
        parts.append("</g>")
    if style == "royal":
        parts.append(f'<g transform="translate(0,{lift})">'
                     f'<rect x="10" y="{h-7}" width="{w-20}" height="2.5" '
                     f'fill="{t["accent2"]}" opacity="0.9"/>'
                     f'<rect x="10" y="4.5" width="{w-20}" height="1.5" '
                     f'fill="#ffffff" opacity="0.55"/></g>')
    if style == "pixel" and fill != "none":
        parts.append(f'<g transform="translate(0,{lift})">'
                     f'<g clip-path="url(#c{u})">'
                     f'<rect x="0" y="{h-7}" width="{w}" height="3" '
                     f'fill="#000000" opacity="0.35"/></g></g>')

    if label:
        ty = h / 2 + lift + (2 if pressed else 0)
        parts.append(_label(w, h, label, ink, style, y=ty))
    return _svg(w, h, "".join(parts))


# ------------------------------------------------------------------ panels ---
def panel(w, h, theme_key, title=True, label="Inventory", scanlines=False):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    u = _uid()
    parts = [f'<defs>{_grad(f"p{u}", [(0, t["panel2"], 1), (1, t["panel"], 1)])}'
             f'<pattern id="s{u}" width="8" height="5" patternUnits="userSpaceOnUse">'
             f'<rect width="8" height="1.2" fill="#ffffff" opacity="0.05"/>'
             f'</pattern></defs>']
    body_fill = t["panel"] if style == "pixel" else f"url(#p{u})"

    if style == "pixel":
        parts.append(f'<rect x="9" y="9" width="{w-4}" height="{h-4}" fill="#000000" opacity="0.55"/>')
    else:
        parts.append(_shadow(style, w, h, g["r"], dy=5, op=0.38))
    parts.append(f'<g fill="{body_fill}" stroke="{t["stroke"]}" '
                 f'stroke-width="{g["stroke"]}">{_path_for(style, w, h, g["r"])}</g>')

    th = 54 if title else 0
    parts.append(f'<clipPath id="tp{u}">{_path_for(style, w, h, g["r"])}</clipPath>')
    if title:
        band = 0.20 if style != "pixel" else 0.30
        parts.append(f'<g clip-path="url(#tp{u})">'
                     f'<rect x="0" y="0" width="{w}" height="{th}" '
                     f'fill="{t["accent"]}" opacity="{band}"/>'
                     f'<rect x="0" y="0" width="{w}" height="3" fill="#ffffff" opacity="0.14"/>'
                     f'<rect x="0" y="{th}" width="{w}" height="2.5" '
                     f'fill="{t["accent2"]}" opacity="0.95"/></g>')
        if label:
            fam = MONO if style == "pixel" else FAM
            ls = {"fantasy": 2.2, "sci": 3.0, "royal": 1.4, "pixel": 1.8}[style]
            parts.append(f'<text x="26" y="{th/2+1}" fill="{t["ink"]}" '
                         f'font-family="{fam}" font-size="21" font-weight="700" '
                         f'letter-spacing="{ls}" dominant-baseline="central">{label}</text>')
            # right ornament in header
            ox = w - 26
            if style == "fantasy":
                parts.append(f'<path d="M{ox} {th/2} L{ox-7} {th/2-7} L{ox-14} {th/2} '
                             f'L{ox-7} {th/2+7} Z" fill="{t["accent2"]}" opacity="0.9"/>'
                             f'<rect x="{ox-56}" y="{th/2-1}" width="36" height="2" '
                             f'fill="{t["accent2"]}" opacity="0.7"/>')
            elif style == "sci":
                parts.append(f'<circle cx="{ox-4}" cy="{th/2}" r="7" fill="{t["good"]}" opacity="0.9"/>'
                             f'<circle cx="{ox-4}" cy="{th/2}" r="11" fill="none" '
                             f'stroke="{t["good"]}" stroke-width="1.5" opacity="0.5"/>'
                             f'<text x="{ox-24}" y="{th/2}" fill="{t["muted"]}" '
                             f'font-family="{MONO}" font-size="11" text-anchor="end" '
                             f'dominant-baseline="central">ONLINE</text>')
            elif style == "royal":
                parts.append(f'<rect x="{ox-46}" y="{th/2-1.5}" width="46" height="3" '
                             f'fill="{t["accent2"]}"/>')
            else:  # pixel
                parts.append(f'<rect x="{ox-16}" y="{th/2-8}" width="16" height="16" '
                             f'fill="{t["accent2"]}"/><rect x="{ox-12}" y="{th/2-4}" '
                             f'width="8" height="8" fill="{t["panel"]}"/>')

    if scanlines or style == "sci":
        parts.append(f'<g clip-path="url(#tp{u})">'
                     f'<rect x="0" y="{th}" width="{w}" height="{h-th}" '
                     f'fill="url(#s{u})"/></g>')

    if style == "fantasy":
        for cx, cy, sx, sy in ((10, 10, 1, 1), (w - 10, 10, -1, 1),
                               (10, h - 10, 1, -1), (w - 10, h - 10, -1, -1)):
            parts.append(
                f'<path d="M{cx} {cy} l{16*sx} 0 M{cx} {cy} l0 {16*sy} '
                f'M{cx + 5*sx} {cy} q{6*sx} {6*sy} {12*sx} 0" '
                f'fill="none" stroke="{t["accent2"]}" stroke-width="2" opacity="0.8"/>')
            parts.append(f'<path d="M{cx} {cy-4} L{cx+4} {cy} L{cx} {cy+4} '
                         f'L{cx-4} {cy} Z" fill="{t["accent2"]}"/>')
    if style == "sci":
        c = 20
        parts.append(
            f'<path d="M4 {c+4} L4 4 L{c+4} 4 M{w-4} {h-c-4} L{w-4} {h-4} '
            f'L{w-c-4} {h-4} M{w-4} {c+4} L{w-4} 4 L{w-c-4} 4 '
            f'M4 {h-c-4} L4 {h-4} L{c+4} {h-4}" fill="none" '
            f'stroke="{t["accent"]}" stroke-width="3"/>')
        parts.append(f'<text x="14" y="{h-12}" fill="{t["muted"]}" '
                     f'font-family="{MONO}" font-size="11" opacity="0.8">'
                     f'//{u[:4].upper()} · SEC-07</text>')
    if style == "royal":
        parts.append(f'<rect x="14" y="14" width="{w-28}" height="{h-28}" fill="none" '
                     f'stroke="{t["accent2"]}" stroke-width="1.5" opacity="0.75"/>')
    if style == "pixel":
        # dither dots on header
        if title:
            for x in range(8, w - 8, 16):
                parts.append(f'<rect x="{x}" y="{th-10}" width="4" height="4" '
                             f'fill="{t["accent2"]}" opacity="0.9"/>')
    return _svg(w, h, "".join(parts))


# -------------------------------------------------------------------- bars ---
def bar(w, h, theme_key, kind="hp", value=0.68, segmented=True, label=""):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    u = _uid()
    colors = {"hp": t["danger"], "mana": t["mana"], "xp": t["accent"],
              "stamina": t["good"], "gold": t["accent2"]}
    fill_c = colors.get(kind, t["accent"])
    pad = g["stroke"]
    gloss = [(0.0, "#ffffff", 0.40), (0.5, "#ffffff", 0.08),
             (1.0, "#000000", 0.28)]
    if style == "pixel":
        gloss = _band(gloss)
    parts = [f'<defs>{_grad(f"b{u}", gloss)}</defs>']
    if style == "pixel":
        parts.append(f'<rect x="5" y="5" width="{w}" height="{h}" fill="#000000" opacity="0.55"/>')
    else:
        parts.append(_shadow(style, w, h, max(4, g["r"] - 2), dy=3, op=0.35))
    parts.append(f'<g fill="{t["panel"]}" stroke="{t["stroke"]}" '
                 f'stroke-width="{g["stroke"]}">'
                 f'{_path_for(style, w, h, max(4, g["r"] - 2))}</g>')

    ix, iy = pad + 3, pad + 3
    iw, ih = w - 2 * ix, h - 2 * iy
    parts.append(f'<clipPath id="in{u}"><rect x="{ix}" y="{iy}" width="{iw}" '
                 f'height="{ih}" rx="{max(0,(g["r"]-4))}"/></clipPath>')
    parts.append(f'<g clip-path="url(#in{u})">')
    parts.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" '
                 f'fill="#000000" opacity="0.50"/>')
    fw = int(iw * max(0.0, min(1.0, value)))
    if fw > 0:
        if style == "sci":
            # angled fill end
            pts = f'{ix},{iy} {ix+fw-8},{iy} {ix+fw},{iy+ih/2} {ix+fw-8},{iy+ih} {ix},{iy+ih}'
            parts.append(f'<polygon points="{pts}" fill="{fill_c}"/>')
            parts.append(f'<polygon points="{pts}" fill="url(#b{u})"/>')
        else:
            parts.append(f'<rect x="{ix}" y="{iy}" width="{fw}" height="{ih}" fill="{fill_c}"/>')
            parts.append(f'<rect x="{ix}" y="{iy}" width="{fw}" height="{ih}" fill="url(#b{u})"/>')
        # bright leading edge
        parts.append(f'<rect x="{ix+fw-3}" y="{iy}" width="3" height="{ih}" '
                     f'fill="#ffffff" opacity="0.75"/>')
    if segmented:
        step = iw / 10
        parts.append(f'<g stroke="#000000" stroke-opacity="0.40" stroke-width="'
                     f'{3 if style=="pixel" else 2}">')
        for i in range(1, 10):
            x = ix + i * step
            parts.append(f'<line x1="{x}" y1="{iy}" x2="{x}" y2="{iy+ih}"/>')
        parts.append("</g>")
    parts.append("</g>")
    # top inner light
    parts.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="1.5" '
                 f'fill="#ffffff" opacity="0.22"/>')
    if label:
        parts.append(_label(w, h, label, t["ink"], style,
                            size=min(15, int(h * 0.5))))
    return _svg(w, h, "".join(parts))


def ring(size, theme_key, value=0.7, label="", kind="xp"):
    """Circular progress indicator."""
    t = THEMES[theme_key]
    style = t["style"]
    u = _uid()
    colors = {"hp": t["danger"], "mana": t["mana"], "xp": t["accent"],
              "stamina": t["good"], "gold": t["accent2"]}
    c = colors.get(kind, t["accent"])
    r = size / 2 - size * 0.09
    cx = cy = size / 2
    circ = 2 * math.pi * r
    sw = size * 0.10
    dash = circ * max(0.0, min(1.0, value))
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["panel2"]}" '
        f'stroke-width="{sw}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["stroke"]}" '
        f'stroke-width="{sw+3}" stroke-opacity="0.6" stroke-dasharray="2 3"/>',
        f'<g transform="rotate(-90 {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="{r}" '
        f'fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="butt" '
        f'stroke-dasharray="{dash:.1f} {circ-dash:.1f}"/></g>',
        f'<circle cx="{cx}" cy="{cy}" r="{r - sw/2}" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.25" stroke-width="1"/>',
    ]
    if label:
        parts.append(_label(size, size, label, t["ink"], style,
                            size=int(size * 0.20)))
    return _svg(size, size, "".join(parts))


# ------------------------------------------------------------------ ribbon ---
def ribbon(w, h, theme_key, label=""):
    t = THEMES[theme_key]
    style = t["style"]
    svg_parts = []
    if style == "pixel":
        body = f'M0 0 H{w} V{h} H0 Z'
        svg_parts = [f'<rect x="5" y="5" width="{w}" height="{h}" fill="#000000" opacity="0.55"/>',
                     f'<path d="{body}" fill="{t["accent"]}" stroke="{t["stroke"]}" stroke-width="4"/>',
                     f'<rect x="4" y="4" width="{w-8}" height="4" fill="#ffffff" opacity="0.5"/>']
    else:
        body = (f'M0 {h*0.18} L{w*0.06} {h*0.18} L{w*0.06} {h*0.82} L0 {h*0.82} '
                f'L{w*0.12} {h*0.5} Z '
                f'M{w} {h*0.18} L{w*0.94} {h*0.18} L{w*0.94} {h*0.82} L{w} {h*0.82} '
                f'L{w*0.88} {h*0.5} Z '
                f'M{w*0.05} {h*0.1} L{w*0.95} {h*0.1} L{w*0.95} {h*0.9} L{w*0.05} {h*0.9} Z')
        svg_parts = [_shadow(style, w, h, 0, dx=0, dy=4, op=0.4),
                     f'<path d="{body}" fill="{t["accent"]}" stroke="{t["stroke"]}" stroke-width="2"/>',
                     f'<rect x="{w*0.07}" y="{h*0.16}" width="{w*0.86}" height="{h*0.68}" '
                     f'fill="none" stroke="{_on(t["accent"], t)}" stroke-opacity="0.45" '
                     f'stroke-width="1.5"/>',
                     f'<rect x="{w*0.05}" y="{h*0.1}" width="{w*0.9}" height="3" '
                     f'fill="#ffffff" opacity="0.35"/>']
    if label:
        svg_parts.append(_label(w, h, label, _on(t["accent"], t), style,
                                size=min(20, int(h * 0.32))))
    return _svg(w, h, "".join(svg_parts))


# -------------------------------------------------------------------- slot ---
def slot(size, theme_key, icon_name=None, rarity=None):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    u = _uid()
    parts = []
    if style == "pixel":
        parts.append(f'<rect x="5" y="5" width="{size}" height="{size}" fill="#000000" opacity="0.55"/>')
    else:
        parts.append(_shadow(style, size, size, g["r"], dy=3, op=0.4))
    if rarity:
        rc = {"common": t["muted"], "rare": t["mana"], "epic": "#B455E6",
              "legendary": t["accent2"]}.get(rarity, t["muted"])
        parts.append(f'<g fill="{rc}" opacity="0.30">'
                     f'{_path_for(style, size, size, g["r"])}</g>')
    parts.append(f'<g fill="{t["panel"]}" stroke="{t["stroke"]}" '
                 f'stroke-width="{g["stroke"]}">{_path_for(style, size, size, g["r"])}</g>')
    parts.append(f'<g fill="none" stroke="{t["accent"]}" stroke-opacity="0.60" '
                 f'stroke-width="2" transform="translate(6,6)">'
                 f'{_path_for(style, size-12, size-12, max(2, g["r"]-3))}</g>')
    # top light
    parts.append(f'<rect x="8" y="7" width="{size-16}" height="2" fill="#ffffff" opacity="0.25"/>')
    if style == "sci":
        c = 10
        parts.append(f'<path d="M4 {c+4} L4 4 L{c+4} 4 M{size-4} {size-c-4} '
                     f'L{size-4} {size-4} L{size-c-4} {size-4}" fill="none" '
                     f'stroke="{t["accent2"]}" stroke-width="3"/>')
    if style == "fantasy":
        cx = cy = size // 2
        parts.append(f'<path d="M{cx} {cy-7} L{cx+7} {cy} L{cx} {cy+7} L{cx-7} {cy} Z" '
                     f'fill="{t["accent"]}" opacity="0.25"/>')
    if icon_name:
        s = size * 0.5
        parts.append(f'<g transform="translate({(size-s)/2},{(size-s)/2}) scale({s/24})">'
                     f'{icon_body(icon_name, t["accent"])}</g>')
    return _svg(size, size, "".join(parts))


# ------------------------------------------------------------------ chips ---
def chip(w, h, theme_key, amount="1,250", kind="gold"):
    """Currency/status pill: icon + amount."""
    t = THEMES[theme_key]
    style = t["style"]
    u = _uid()
    col_map = {"gold": "#F5C542", "gem": t["mana"], "gem2": "#B455E6",
               "energy": t["good"]}
    if kind == "gold":
        col_map["gold"] = t["accent2"] if style in ("fantasy", "royal") else "#F5C542"
    col = col_map.get(kind, t["accent2"])
    ico = {"gold": "coin", "gem": "gem", "gem2": "star", "energy": "bolt"}.get(kind, "coin")
    r = h / 2 - 1 if style != "pixel" else 0
    parts = [_shadow(style, w, h, r, dy=3, op=0.35)]
    parts.append(f'<g fill="{t["panel"]}" stroke="{col}" stroke-width="2.5">'
                 f'{_path_for(style, w, h, r)}</g>')
    parts.append(f'<g transform="translate({h*0.20},{h*0.20}) scale({h*0.60/24})">'
                 f'{icon_body(ico, col)}</g>')
    parts.append(_label(w, h, amount, t["ink"], style,
                        size=min(17, int(h * 0.44)),
                        x=h * 0.20 + h * 0.60 + 10 + (w - (h * 0.8 + 10)) / 2 - 4))
    return _svg(w, h, "".join(parts))


def badge(size, theme_key, text="3"):
    """Notification badge."""
    t = THEMES[theme_key]
    u = _uid()
    parts = [f'<circle cx="{size/2}" cy="{size/2}" r="{size/2-2}" fill="{t["danger"]}" '
             f'stroke="#ffffff" stroke-width="2"/>',
             _label(size, size, text, "#FFFFFF", "sci", size=int(size * 0.52))]
    return _svg(size, size, "".join(parts))


# ------------------------------------------------------------ form widgets ---
def toggle(w, h, theme_key, on=True):
    t = THEMES[theme_key]
    style = t["style"]
    u = _uid()
    r = h / 2 if style != "pixel" else 0
    track = t["good"] if on else t["panel2"]
    parts = [_shadow(style, w, h, r, dy=3, op=0.3)]
    parts.append(f'<g fill="{track}" stroke="{t["stroke"]}" stroke-width="2">'
                 f'{_path_for(style, w, h, r)}</g>')
    if style == "pixel":
        kw = h - 8
        kx = (w - kw - 4) if on else 4
        parts.append(f'<rect x="{kx}" y="4" width="{kw}" height="{kw}" '
                     f'fill="{t["ink"]}" stroke="{t["stroke"]}" stroke-width="3"/>')
        if on:
            parts.append(f'<rect x="{kx+3}" y="7" width="{kw-6}" height="4" '
                         f'fill="{t["accent"]}" opacity="0.001"/>')
    else:
        kw = h - 8
        kx = (w - kw - 4) if on else 4
        parts.append(f'<circle cx="{kx+kw/2}" cy="{h/2}" r="{kw/2}" fill="#ffffff" '
                     f'stroke="{t["stroke"]}" stroke-width="1.5"/>')
        if on:
            parts.append(f'<circle cx="{kx+kw/2}" cy="{h/2}" r="{kw/2+3.5}" fill="none" '
                         f'stroke="{t["good"]}" stroke-width="2" opacity="0.7"/>')
    if style == "sci" and on:
        parts.append(f'<text x="{w-14}" y="{h/2}" fill="#ffffff" font-family="{MONO}" '
                     f'font-size="11" text-anchor="end" dominant-baseline="central" '
                     f'opacity="0.85">ON</text>')
    return _svg(w, h, "".join(parts))


def checkbox(size, theme_key, checked=True):
    t = THEMES[theme_key]
    style = t["style"]
    parts = []
    if style == "pixel":
        parts.append(f'<rect x="4" y="4" width="{size}" height="{size}" fill="#000000" opacity="0.5"/>')
    inner = (f'<g fill="{t["accent"] if checked else t["panel"]}" '
             f'stroke="{t["stroke"]}" stroke-width="2.5">'
             f'{_path_for(style, size, size, max(2, size*0.18))}</g>')
    parts.append(inner)
    if checked:
        m = size * 0.24
        col = _on(t["accent"], t) if style != "royal" else "#FFFFFF"
        parts.append(f'<path d="M{m} {size*0.52} L{size*0.44} {size*0.76} '
                     f'L{size*0.78} {size*0.26}" fill="none" stroke="{col}" '
                     f'stroke-width="{max(3, size*0.14)}" stroke-linecap="round" '
                     f'stroke-linejoin="round"/>')
    return _svg(size, size, "".join(parts))


def slider(w, h, theme_key, value=0.6):
    t = THEMES[theme_key]
    style = t["style"]
    u = _uid()
    th = max(6, int(h * 0.30))
    ty = (h - th) / 2
    kw = h
    kx = max(kw / 2, (w - kw) * value)
    parts = []
    parts.append(f'<rect x="{kw/2}" y="{ty}" width="{w-kw}" height="{th}" '
                 f'fill="{t["panel2"]}" stroke="{t["stroke"]}" stroke-width="2" '
                 f'rx="{th/2 if style!="pixel" else 0}"/>')
    fw = kx - kw / 2
    parts.append(f'<rect x="{kw/2}" y="{ty}" width="{max(0,fw)}" height="{th}" '
                 f'fill="{t["accent"]}" rx="{th/2 if style!="pixel" else 0}"/>')
    # knurled knob
    if style == "pixel":
        parts.append(f'<rect x="{kx-kw/2}" y="2" width="{kw}" height="{h-4}" '
                     f'fill="{t["ink"]}" stroke="{t["stroke"]}" stroke-width="3"/>')
        parts.append(f'<rect x="{kx-3}" y="{h*0.3}" width="6" height="{h*0.4}" '
                     f'fill="{t["stroke"]}"/>')
    else:
        parts.append(f'<circle cx="{kx}" cy="{h/2}" r="{kw/2}" fill="{t["ink"]}" '
                     f'stroke="{t["accent"]}" stroke-width="3"/>')
        parts.append(f'<circle cx="{kx}" cy="{h/2}" r="{kw/2-5}" fill="{t["panel2"]}"/>')
        parts.append(f'<circle cx="{kx}" cy="{h/2}" r="3" fill="{t["accent"]}"/>')
    return _svg(w, h, "".join(parts))


def input(w, h, theme_key, placeholder="Player name", focused=False):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    parts = []
    st = t["accent"] if focused else t["stroke"]
    sw = 3 if focused else 2
    parts.append(f'<g fill="{t["panel"]}" stroke="{st}" stroke-width="{sw}">'
                 f'{_path_for(style, w, h, g["r"])}</g>')
    if focused:
        parts.append(f'<g fill="none" stroke="{t["accent"]}" stroke-width="6" '
                     f'opacity="0.25">{_path_for(style, w, h, g["r"])}</g>')
    fam = MONO if style == "pixel" else FAM
    parts.append(f'<text x="16" y="{h/2}" fill="{t["muted"]}" font-family="{fam}" '
                 f'font-size="{min(17, int(h*0.40))}" dominant-baseline="central">'
                 f'{placeholder}</text>')
    if focused:
        tw = len(placeholder) * (9 if style != "pixel" else 9.5) + 20
        if tw < w - 24:
            parts.append(f'<rect x="{tw}" y="{h*0.26}" width="2.5" height="{h*0.48}" '
                         f'fill="{t["accent"]}"/>')
    if style == "sci":
        c = 12
        parts.append(f'<path d="M4 {c+4} L4 4 L{c+4} 4" fill="none" '
                     f'stroke="{t["accent2"]}" stroke-width="2.5"/>')
    return _svg(w, h, "".join(parts))


def dropdown(w, h, theme_key, value="Normal"):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    parts = []
    parts.append(f'<g fill="{t["panel2"]}" stroke="{t["stroke"]}" stroke-width="2">'
                 f'{_path_for(style, w, h, g["r"])}</g>')
    fam = MONO if style == "pixel" else FAM
    parts.append(f'<text x="16" y="{h/2}" fill="{t["ink"]}" font-family="{fam}" '
                 f'font-size="{min(16, int(h*0.38))}" dominant-baseline="central">{value}</text>')
    bx = w - h * 0.7
    by = h / 2
    parts.append(f'<path d="M{bx-6} {by-3} L{bx} {by+4} L{bx+6} {by-3}" fill="none" '
                 f'stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append(f'<rect x="{w-h*0.95}" y="6" width="1.5" height="{h-12}" '
                 f'fill="{t["stroke"]}"/>')
    return _svg(w, h, "".join(parts))


def tabs(w, h, theme_key, items, active=0):
    t = THEMES[theme_key]
    style = t["style"]
    n = len(items)
    tw = w / n
    parts = []
    parts.append(f'<rect x="0" y="{h-3}" width="{w}" height="3" fill="{t["stroke"]}"/>')
    for i, it in enumerate(items):
        x0 = i * tw
        on = i == active
        if on:
            fill = t["accent"] if style != "royal" else t["accent"]
            parts.append(f'<rect x="{x0}" y="0" width="{tw}" height="{h}" '
                         f'fill="{fill}" opacity="{0.18 if style!="pixel" else 0.30}"/>')
            parts.append(f'<rect x="{x0}" y="{h-4}" width="{tw}" height="4" '
                         f'fill="{fill}"/>')
        col = t["ink"] if on else t["muted"]
        parts.append(f'<text x="{x0+tw/2}" y="{h/2-1}" fill="{col}" '
                     f'font-family="{MONO if style=="pixel" else FAM}" '
                     f'font-size="{min(15, int(h*0.36))}" font-weight="'
                     f'{"700" if on else "400"}" text-anchor="middle" '
                     f'dominant-baseline="central">{it}</text>')
        if i:
            parts.append(f'<rect x="{x0}" y="{h*0.22}" width="1.5" height="{h*0.56}" '
                         f'fill="{t["stroke"]}"/>')
    return _svg(w, h, "".join(parts))


def keycap(size, theme_key, label="A"):
    t = THEMES[theme_key]
    style = t["style"]
    parts = []
    if style != "pixel":
        parts.append(_shadow(style, size, size, size * 0.18, dy=4, op=0.4))
    else:
        parts.append(f'<rect x="4" y="4" width="{size}" height="{size}" fill="#000000" opacity="0.55"/>')
    parts.append(f'<g fill="{t["panel2"]}" stroke="{t["stroke"]}" stroke-width="2.5">'
                 f'{_path_for(style, size, size, size*0.18)}</g>')
    parts.append(f'<rect x="4" y="4" width="{size-8}" height="3" fill="#ffffff" opacity="0.3"/>')
    parts.append(_label(size, size, label, t["ink"], style, size=int(size * 0.46)))
    return _svg(size, size, "".join(parts))


# ---------------------------------------------------------------- windows ---
def tooltip(w, h, theme_key, text="Deals 120% damage"):
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    parts = []
    parts.append(_shadow(style, w, h, g["r"], dy=4, op=0.45))
    parts.append(f'<g fill="{t["panel2"]}" stroke="{t["accent"]}" stroke-width="2">'
                 f'{_path_for(style, w, h, g["r"])}</g>')
    # pointer
    px = w * 0.5
    parts.append(f'<path d="M{px-10} {h-1} L{px} {h+13} L{px+10} {h-1} Z" '
                 f'fill="{t["panel2"]}" stroke="{t["accent"]}" stroke-width="2" '
                 f'stroke-linejoin="round"/>')
    parts.append(f'<rect x="{px-8}" y="{h-1}" width="16" height="3" '
                 f'fill="{t["panel2"]}"/>')
    parts.append(f'<rect x="12" y="{h/2-9}" width="3" height="18" fill="{t["accent"]}"/>')
    parts.append(f'<text x="26" y="{h/2}" fill="{t["ink"]}" '
                 f'font-family="{MONO if style=="pixel" else FAM}" '
                 f'font-size="{min(15, int(h*0.36))}" dominant-baseline="central">{text}</text>')
    return _svg(w, h + 14, "".join(parts))


def dialog(w, h, theme_key, title="Confirm", message="Proceed with the quest?",
           primary="ACCEPT", secondary="DECLINE"):
    """Modal window composed from panel + text + buttons."""
    t = THEMES[theme_key]
    inner = []
    inner.append(panel(w, h, theme_key, title=True, label=title))
    fam = MONO if t["style"] == "pixel" else FAM
    inner.append(f'<text x="{w/2}" y="{h*0.44}" fill="{t["ink"]}" font-family="{fam}" '
                 f'font-size="17" text-anchor="middle" dominant-baseline="central">'
                 f'{message}</text>')
    bw, bh = int(w * 0.36), 46
    gap = 18
    x0 = (w - 2 * bw - gap) / 2
    y0 = h - bh - 26
    inner.append(f'<g transform="translate({x0},{y0})">'
                 + button(bw, bh, theme_key, "normal", "ghost", label=secondary)
                 + '</g>')
    inner.append(f'<g transform="translate({x0+bw+gap},{y0})">'
                 + button(bw, bh, theme_key, "normal", "primary", label=primary)
                 + '</g>')
    return _svg(w, h, "".join(inner))


def bubble(w, h, theme_key, text="Ready when you are!", side="left"):
    """Chat message bubble."""
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    parts = []
    r = min(g["r"], 14)
    parts.append(_shadow(style, w, h, r, dy=3, op=0.3))
    fill = t["panel2"] if side == "left" else t["accent"]
    ink = t["ink"] if side == "left" else _on(t["accent"], t)
    st = t["stroke"] if side == "left" else t["accent"]
    parts.append(f'<g fill="{fill}" stroke="{st}" stroke-width="2">'
                 f'{_path_for(style, w, h, r)}</g>')
    if side == "left":
        parts.append(f'<path d="M2 {h*0.35} L2 {h*0.75} L16 {h*0.62} Z" '
                     f'fill="{fill}" stroke="{st}" stroke-width="2"/>')
    else:
        parts.append(f'<path d="M{w-2} {h*0.35} L{w-2} {h*0.75} L{w-16} {h*0.62} Z" '
                     f'fill="{fill}" stroke="{st}" stroke-width="2"/>')
    fam = MONO if style == "pixel" else FAM
    parts.append(f'<text x="{w/2}" y="{h/2}" fill="{ink}" font-family="{fam}" '
                 f'font-size="14" text-anchor="middle" dominant-baseline="central">'
                 f'{text}</text>')
    return _svg(w, h, "".join(parts))


def stars(w, h, theme_key, rating=4, total=5):
    """Star rating row."""
    t = THEMES[theme_key]
    style = t["style"]
    parts = []
    s = h
    gap = h * 0.18
    for i in range(total):
        x = i * (s + gap)
        on = i < rating
        gold = t["accent"] if style == "pixel" else t["accent2"]
        col = gold if on else t["panel2"]
        op = 1 if on else 1
        parts.append(f'<g transform="translate({x},0) scale({s/24})" fill="{col}" '
                     f'opacity="{op}" stroke="{t["stroke"]}" stroke-width="{0.8 if not on else 0}">'
                     f'{ICONS["star"]}</g>')
        if not on:
            parts.append(f'<g transform="translate({x},0) scale({s/24})" fill="none" '
                         f'stroke="{t["muted"]}" stroke-width="1.4">{ICONS["star"]}</g>')
    return _svg(int(total * (s + gap) - gap), h, "".join(parts))


def divider(w, theme_key, ornament=True):
    """Ornamental horizontal rule."""
    t = THEMES[theme_key]
    y = 8
    parts = [f'<rect x="0" y="{y-1}" width="{w*0.42}" height="2" fill="{t["stroke"]}"/>',
             f'<rect x="{w*0.58}" y="{y-1}" width="{w*0.42}" height="2" fill="{t["stroke"]}"/>']
    if ornament:
        cx = w / 2
        if t["style"] == "pixel":
            parts.append(f'<rect x="{cx-6}" y="{y-6}" width="12" height="12" '
                         f'fill="{t["accent"]}"/>')
        else:
            parts.append(f'<path d="M{cx} {y-8} L{cx+8} {y} L{cx} {y+8} L{cx-8} {y} Z" '
                         f'fill="{t["accent"]}"/>')
            parts.append(f'<rect x="{w*0.42}" y="{y-1}" width="{w*0.16}" height="2" '
                         f'fill="{t["accent"]}" opacity="0.8"/>')
    return _svg(w, 16, "".join(parts))


def item_card(w, h, theme_key, name="Iron Sword", sub="DMG 12-18",
              price="150", rarity="rare", icon_name="sword"):
    """Shop/inventory item card: slot + text + buy button."""
    t = THEMES[theme_key]
    style = t["style"]
    g = GEO[style]
    parts = []
    if style == "pixel":
        parts.append(f'<rect x="6" y="6" width="{w}" height="{h}" fill="#000000" opacity="0.5"/>')
    else:
        parts.append(_shadow(style, w, h, g["r"], dy=4, op=0.38))
    parts.append(f'<g fill="{t["panel"]}" stroke="{t["stroke"]}" stroke-width="2">'
                 f'{_path_for(style, w, h, g["r"])}</g>')
    s = h - 24
    parts.append(f'<g transform="translate(12,12)">'
                 + slot(s, theme_key, icon_name=icon_name, rarity=rarity)
                 + '</g>')
    tx = 12 + s + 14
    fam = MONO if style == "pixel" else FAM
    parts.append(f'<text x="{tx}" y="30" fill="{t["ink"]}" font-family="{fam}" '
                 f'font-size="16" font-weight="700" dominant-baseline="central">{name}</text>')
    parts.append(f'<text x="{tx}" y="54" fill="{t["muted"]}" font-family="{fam}" '
                 f'font-size="13" dominant-baseline="central">{sub}</text>')
    bw, bh = 92, 34
    parts.append(f'<g transform="translate({w-bw-12},{h-bh-12})">'
                 + button(bw, bh, theme_key, "normal", "primary", label=price,
                          shape="standard")
                 + '</g>')
    return _svg(w, h, "".join(parts))


# ------------------------------------------------------------------- icons ---
def _gear_path(cx, cy, teeth=8, r_out=9.5, r_in=7.2):
    pts = []
    step = math.pi * 2 / teeth
    for i in range(teeth):
        a0 = i * step
        for da, r in ((0.0, r_in), (step * 0.18, r_out),
                      (step * 0.42, r_out), (step * 0.60, r_in)):
            a = a0 + da
            pts.append(f"{cx + r*math.cos(a):.2f} {cy + r*math.sin(a):.2f}")
    return "M" + " L".join(pts) + " Z"


ICONS = {
    "sword": ('<path d="M12 2 l2.2 3.2 V14 h-4.4 V5.2 Z"/>'
              '<path d="M7.5 14 h9"/><path d="M12 14 v5.5"/>'
              '<circle cx="12" cy="21" r="1.6"/>'),
    "shield": ('<path d="M12 2 l8 3 v6 c0 5.2 -4 8.4 -8 9.4 '
               'c-4 -1 -8 -4.2 -8 -9.4 v-6 Z"/>'
               '<path d="M12 6.5 v11" stroke-opacity="0.6"/>'),
    "heart": ('<path d="M12 20.5 C5.5 15 3 10.5 5.5 7.5 C7.4 5.2 10.4 5.6 12 7.8 '
              'C11.6 5.6 14.6 5.2 18.5 7.5 C21 10.5 18.5 15 12 20.5 Z"/>'),
    "coin": ('<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="4.6"/>'
             '<path d="M12 8.8 v6.4 M9.8 10.6 h4.4 M9.8 13.4 h4.4"/>'),
    "gem": ('<path d="M12 3 l7.2 5.8 L12 21 L4.8 8.8 Z"/>'
            '<path d="M4.8 8.8 H19.2 M12 3 L9.4 8.8 12 21 14.6 8.8 Z" stroke-opacity="0.65"/>'),
    "potion": ('<path d="M9.6 2.5 h4.8 v4.6 l3.1 5.2 c2.1 4 -1.1 8.2 -5.5 8.2 '
               's-7.6 -4.2 -5.5 -8.2 l3.1 -5.2 Z"/>'
               '<path d="M8.4 14.5 h7.2" stroke-opacity="0.7"/>'),
    "key": ('<circle cx="8.5" cy="8.5" r="4.6"/><path d="M11.9 11.9 L19.5 19.5"/>'
            '<path d="M16.6 16.4 l2 -2 M14.4 18.6 l2 -2"/>'),
    "star": ('<path d="M12 2.8 l2.7 5.7 6.3 .8 -4.6 4.4 1.2 6.3 -5.6 -3 -5.6 3 '
             '1.2 -6.3 -4.6 -4.4 6.3 -.8 Z"/>'),
    "gear": None,
    "skull": ('<path d="M5.5 12 a6.5 6.5 0 0 1 13 0 v3.2 h-2.2 v2.4 h-2.2 v2.4 '
              'h-4.2 v-2.4 h-2.2 v-2.4 H5.5 Z"/>'
              '<circle cx="9.3" cy="12" r="1.7" fill="HOLE"/>'
              '<circle cx="14.7" cy="12" r="1.7" fill="HOLE"/>'),
    "flag": ('<path d="M6 3 v18"/><path d="M8 4.5 h10 l-2.2 3.2 2.2 3.2 h-10 Z"/>'),
    "book": ('<path d="M12 6.4 C10 4.4 7 4 4.5 5.4 V18.6 C7 17.2 10 17.6 12 19.6 '
             'C14 17.6 17 17.2 19.5 18.6 V5.4 C17 4 14 4.4 12 6.4 Z"/>'
             '<path d="M12 6.4 V19.6" stroke-opacity="0.7"/>'),
    "crown": ('<path d="M4 8.5 L8.2 12.5 L12 5 L15.8 12.5 L20 8.5 L18.2 19 H5.8 Z"/>'
              '<path d="M5.8 16 h12.4" stroke-opacity="0.6"/>'),
    "map": ('<path d="M3.5 6.5 L9 4 L15 6.5 L20.5 4 V17.5 L15 20 L9 17.5 L3.5 20 Z"/>'
            '<path d="M9 4 V17.5 M15 6.5 V20" stroke-opacity="0.7"/>'),
    "arrow": ('<path d="M4 12 H17.5"/><path d="M13.5 7.5 L18.5 12 L13.5 16.5"/>'),
    # ---- v2 batch (27 more) ----
    "play": ('<path d="M8 5 L19 12 L8 19 Z"/>'),
    "pause": ('<path d="M8 5 V19 M16 5 V19" stroke-width="3.4"/>'),
    "volume": ('<path d="M4 9.5 H7.5 L12.5 5.5 V18.5 L7.5 14.5 H4 Z"/>'
               '<path d="M15.5 9 a4.4 4.4 0 0 1 0 6" stroke-opacity="0.85"/>'
               '<path d="M18 6.6 a8 8 0 0 1 0 10.8" stroke-opacity="0.6"/>'),
    "music": ('<circle cx="8" cy="17" r="2.8"/><circle cx="17" cy="15" r="2.8"/>'
              '<path d="M10.8 17 V7 L19.8 5 V15"/>'),
    "bell": ('<path d="M12 3 a6.4 6.4 0 0 1 6.4 6.4 v3.4 l1.6 2.7 H4 l1.6 -2.7 '
             'V9.4 A6.4 6.4 0 0 1 12 3 Z"/><path d="M10 18.6 a2 2 0 0 0 4 0"/>'),
    "moon": ('<path d="M15.8 3.6 A8.6 8.6 0 1 0 20.4 15.5 A7.4 7.4 0 0 1 15.8 3.6 Z"/>'),
    "sun": ('<circle cx="12" cy="12" r="4.4"/>'
            '<path d="M12 2.5 V5 M12 19 V21.5 M2.5 12 H5 M19 12 H21.5 '
            'M5.3 5.3 L7 7 M17 17 L18.7 18.7 M18.7 5.3 L17 7 M7 17 L5.3 18.7"/>'),
    "fire": ('<path d="M12 21 c-3.9 0 -6.5 -2.5 -6.5 -6 0 -3.4 2.6 -5.2 3.7 -8.4 '
             'c.4 1.7 1.5 2.7 2.4 3.2 C11 7.4 10.6 4.6 12.6 2.2 c.4 2.8 5.9 4.7 5.9 12.8 '
             'c0 3.5 -2.6 6 -6.5 6 Z"/>'),
    "bolt": ('<path d="M13.4 2 L4.8 13.4 H10.4 L9.6 22 L19.2 10.2 H13.2 Z"/>'),
    "droplet": ('<path d="M12 2.8 C12 2.8 5.4 10.2 5.4 14.6 a6.6 6.6 0 0 0 13.2 0 '
                'C18.6 10.2 12 2.8 12 2.8 Z"/>'),
    "snow": ('<path d="M12 2.5 V21.5 M3.8 7.2 L20.2 16.8 M20.2 7.2 L3.8 16.8"/>'),
    "leaf": ('<path d="M19.5 4.5 C10 4.5 4.5 9 4.5 15.5 c0 1.4 .4 2.7 1.1 3.9 '
             'C7 13 11 9.5 16.5 7.8 c-4.4 2.6 -7.6 6.4 -9 12.2 c1 -.4 2 -.6 3.1 -.6 '
             '6.5 0 10.4 -6 9.9 -14.9 Z"/>'),
    "home": ('<path d="M4 11.4 L12 4 L20 11.4 V20 H14.4 V14.5 H9.6 V20 H4 Z"/>'),
    "lock": ('<rect x="5" y="10.5" width="14" height="9.5" rx="2"/>'
             '<path d="M8 10.5 V7.6 a4 4 0 0 1 8 0 v2.9"/><circle cx="12" cy="15" r="1.6"/>'),
    "search": ('<circle cx="10.5" cy="10.5" r="6.2"/><path d="M15.2 15.2 L20.5 20.5"/>'),
    "trash": ('<path d="M4.8 6.8 H19.2 M9.5 6.8 V4.6 h5 V6.8"/>'
              '<path d="M6.6 6.8 L7.5 19.4 h9 L17.4 6.8"/>'
              '<path d="M10 10 v6 M14 10 v6" stroke-opacity="0.7"/>'),
    "edit": ('<path d="M4.5 19.5 L5.3 15.7 L15.9 5.1 L18.9 8.1 L8.3 18.7 Z"/>'
             '<path d="M14.2 6.8 L17.2 9.8"/>'),
    "cart": ('<path d="M3.5 4.5 H6.2 L8.6 14.6 H17.6 L19.8 7 H7.1"/>'
             '<circle cx="9.4" cy="18.6" r="1.8"/><circle cx="16.6" cy="18.6" r="1.8"/>'),
    "user": ('<circle cx="12" cy="8" r="4.2"/><path d="M4.5 20.5 c1 -4.2 4 -6.2 7.5 -6.2 '
             's6.5 2 7.5 6.2"/>'),
    "refresh": ('<path d="M19.4 12 a7.4 7.4 0 1 1 -2.2 -5.3"/>'
                '<path d="M17.6 3.6 L17.6 7.4 L13.8 7.4"/>'),
    "target": ('<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="4.8"/>'
               '<circle cx="12" cy="12" r="1.4"/>'),
    "clock": ('<circle cx="12" cy="12" r="8.6"/><path d="M12 6.8 V12 l3.6 2.4"/>'),
    "calendar": ('<rect x="4" y="5.5" width="16" height="14.5" rx="2"/>'
                 '<path d="M4 10 H20 M8.5 3.5 V7 M15.5 3.5 V7"/>'
                 '<path d="M8 13.6 h2 M14 13.6 h2 M8 17 h2 M14 17 h2" stroke-opacity="0.8"/>'),
    "eye": ('<path d="M2.8 12 C5.5 7.6 8.6 5.4 12 5.4 s6.5 2.2 9.2 6.6 '
            'C18.5 16.4 15.4 18.6 12 18.6 s-6.5 -2.2 -9.2 -6.6 Z"/>'
            '<circle cx="12" cy="12" r="2.8"/>'),
    "hammer": ('<path d="M6.4 17.6 L14.6 9.4"/><path d="M12.6 4.6 L19.4 4.6 '
               'L19.4 9.2 L16 12.4 L11.4 11 Z"/>'),
    "axe": ('<path d="M7 20 L15.4 6.4"/><path d="M13.4 3.6 c3.4 .4 5.8 2.4 6.6 5.6 '
            'l-4.4 1.2 -3.6 -3.6 Z"/>'),
    "wand": ('<path d="M4.5 19.5 L13.5 10.5"/><path d="M16 3.4 l1.3 3 3 1.3 -3 1.3 '
             '-1.3 3 -1.3 -3 -3 -1.3 3 -1.3 Z"/>'),
    "bag": ('<path d="M6.5 8.5 h11 l1.3 11.5 H5.2 Z"/><path d="M8.8 8.5 V6.4 '
            'a3.2 3.2 0 0 1 6.4 0 v2.1"/>'),
    "arrow_up": ('<path d="M12 19.5 V5 M6.8 10.2 L12 5 L17.2 10.2"/>'),
    "arrow_down": ('<path d="M12 4.5 V19 M6.8 13.8 L12 19 L17.2 13.8"/>'),
    "arrow_left": ('<path d="M19.5 12 H5 M10.2 6.8 L5 12 L10.2 17.2"/>'),
    "close": ('<path d="M6 6 L18 18 M18 6 L6 18" stroke-width="2.6"/>'),
    "check": ('<path d="M4.5 12.8 L9.6 18 L19.5 6.6" stroke-width="2.8"/>'),
    "plus": ('<path d="M12 5 V19 M5 12 H19" stroke-width="2.8"/>'),
    "minus": ('<path d="M5 12 H19" stroke-width="2.8"/>'),
    "question": ('<path d="M8.4 9 a3.8 3.8 0 1 1 5 3.6 c-1 .4 -1.4 1 -1.4 2.2 '
                 'v1"/><circle cx="12" cy="18.6" r="1.4"/>'),
    "lightning": None,  # alias handled below
}
ICONS["lightning"] = ICONS["bolt"]


def icon_body(name, color):
    """Return inner markup (paths) for icon name, stroked in `color`."""
    if name == "gear":
        body = f'<path d="{_gear_path(12,12)}"/><circle cx="12" cy="12" r="3.2"/>'
    else:
        body = ICONS[name].replace("HOLE", f'fill="{color}"')
    return (f'<g fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round">{body}</g>')


def icon(name, theme_key, size=48, color=None, stroke_width=2):
    t = THEMES[theme_key]
    c = color or t["accent"]
    if name == "gear":
        body = f'<path d="{_gear_path(12,12)}"/><circle cx="12" cy="12" r="3.2"/>'
    else:
        body = ICONS[name].replace("HOLE", f'fill="{c}"')
    inner = (f'<g fill="none" stroke="{c}" stroke-width="{stroke_width}" '
             f'stroke-linejoin="round" stroke-linecap="round">{body}</g>')
    return _svg(24, 24, inner, viewbox="0 0 24 24").replace(
        'width="24" height="24"', f'width="{size}" height="{size}"')


ICON_NAMES = [
    "sword", "shield", "heart", "coin", "gem", "potion", "key", "star",
    "gear", "skull", "flag", "book", "crown", "map", "arrow",
    "play", "pause", "volume", "music", "bell", "moon", "sun", "fire",
    "bolt", "droplet", "snow", "leaf", "home", "lock", "search", "trash",
    "edit", "cart", "user", "refresh", "target", "clock", "calendar",
    "eye", "hammer", "axe", "wand", "bag", "arrow_up", "arrow_down",
    "arrow_left", "close", "check", "plus", "minus", "question",
]
