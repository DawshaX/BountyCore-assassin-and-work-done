#!/usr/bin/env python
"""Fab-compliant store graphics: cover + features at 1920x1080 (Fab minimum).
Also writes thumbnail copy to assets/fab/.  Run: python3 tools/make_fab_graphics.py"""
from PIL import Image, ImageDraw, ImageFont
import os

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BG = os.path.join(ASSETS, "cover_bg.png")
FAB = os.path.join(ASSETS, "fab")

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

AMBER = (255, 181, 69)
CYAN = (65, 214, 195)
WHITE = (232, 236, 246)
DIM = (139, 147, 168)


def cover_bg(w, h):
    im = Image.open(BG).convert("RGBA")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def gradient_overlay(im, top_alpha=210, mid_alpha=90):
    w, h = im.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(h):
        t = y / h
        if t < 0.42:
            a = top_alpha + (mid_alpha - top_alpha) * (t / 0.42)
        else:
            a = mid_alpha * max(0.0, 1 - (t - 0.42) / 0.5) + 40
        d.line([(0, y), (w, y)], fill=(8, 9, 14, int(a)))
    return Image.alpha_composite(im, ov)


def sp_text(d, xy, text, font, fill, spacing=0, anchor_center_x=None):
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor_center_x is not None:
        x = anchor_center_x - total / 2
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += cw + spacing
    return total


def chip(d, x, y, text, font, border, text_fill, pad=18):
    tw = d.textlength(text, font=font)
    fh = font.size
    w = tw + pad * 2
    h = fh + pad * 1.4
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, outline=border, width=2,
                        fill=(10, 12, 18, 200))
    d.text((x + pad, y + pad * 0.62), text, font=font, fill=text_fill)
    return w, h


def make_cover_1920():
    W, H = 1920, 1080
    im = gradient_overlay(cover_bg(W, H))
    d = ImageDraw.Draw(im)

    f_title = ImageFont.truetype(SANS_B, 208)
    f_sub = ImageFont.truetype(MONO_B, 44)
    f_chip = ImageFont.truetype(MONO_B, 31)
    f_badge = ImageFont.truetype(MONO_B, 28)

    d.rectangle([0, 0, W, 10], fill=AMBER)

    title = "PIXELFORGE"
    widths = [d.textlength(c, font=f_title) for c in title]
    spacing = 8
    total = sum(widths) + spacing * (len(title) - 1)
    x = (W - total) / 2
    y = 118
    for i, (c, cw) in enumerate(zip(title, widths)):
        t = i / max(1, len(title) - 1)
        col = tuple(round(AMBER[j] + (CYAN[j] - AMBER[j]) * t) for j in range(3))
        d.text((x + 6, y + 8), c, font=f_title, fill=(0, 0, 0, 160))
        d.text((x, y), c, font=f_title, fill=col + (255,))
        x += cw + spacing

    sp_text(d, (0, 372), "SPRITE  SHEET  MAKER  &  PIXEL  ART  STUDIO",
            f_sub, WHITE, spacing=6, anchor_center_x=W / 2)

    d.rectangle([W / 2 - 400, 448, W / 2 + 400, 453], fill=CYAN)

    rows = [
        ["100% OFFLINE", "NO WATERMARKS", "GIF IN + OUT"],
        ["PHASER · ASEPRITE", "UNDO / REDO", "MULTI-PAGE PNG"],
    ]
    cy = 496
    for row in rows:
        widths2 = [d.textlength(txt, font=f_chip) + 36 * 2 for txt in row]
        gap = 24
        total_w = sum(widths2) + gap * (len(row) - 1)
        cx = (W - total_w) / 2
        for txt, tw in zip(row, widths2):
            chip(d, cx, cy, txt, f_chip, CYAN, WHITE)
            cx += tw + gap
        cy += 76

    chip(d, 48, H - 96, "v1.1", f_badge, AMBER, AMBER, pad=15)
    d.rectangle([0, H - 10, W, H], fill=CYAN)

    out = os.path.join(FAB, "fab-thumbnail-1920x1080.png")
    im.convert("RGB").save(out, optimize=True)
    # also refresh main cover (same art, keeps itch at its ratio)
    print("wrote", out, im.size)


def make_features_1920():
    W, H = 1920, 1080
    im = Image.new("RGBA", (W, H), (11, 13, 18, 255))
    d = ImageDraw.Draw(im)

    for y in range(0, H, 48):
        for x in range(0, W, 48):
            if ((x // 48) + (y // 48)) % 2 == 0:
                d.rectangle([x, y, x + 47, y + 47], fill=(15, 18, 26, 255))

    f_h = ImageFont.truetype(SANS_B, 80)
    f_ic = ImageFont.truetype(SANS_B, 68)
    f_t = ImageFont.truetype(SANS_B, 40)
    f_d = ImageFont.truetype(MONO_B, 28)

    sp_text(d, (0, 62), "EVERYTHING IN ONE TOOL", f_h, AMBER, spacing=9, anchor_center_x=W / 2)
    d.rectangle([W / 2 - 300, 176, W / 2 + 300, 181], fill=CYAN)

    tiles = [
        ("▦", "DROP & PACK", "Batch, folder & GIF\nimport, reorder, trim"),
        ("◈", "PIXELATE", "Auto palette + 12 retro\nBayer / Floyd dithering"),
        ("▶", "LIVE PREVIEW", "1–60 FPS + pivot editor\nloop / ping-pong / once"),
        ("▣", "ATLAS EXPORT", "Generic · Phaser 3\nAseprite · CSS · GIF"),
        ("⊞", "EXTRUDE + SCALE", "Multi-page, no bleeding\n1–8× nearest-neighbour"),
        ("⌁", "100% OFFLINE", "No cloud, no watermark\nUndo / Redo built-in"),
    ]

    cols = 3
    mx, my = 66, 236
    tw = (W - mx * 2 - 36 * (cols - 1)) / cols
    th = 326

    accents = [AMBER, CYAN, (255, 107, 107), (122, 92, 255), CYAN, AMBER]
    for i, (icon, title, desc) in enumerate(tiles):
        cx = mx + (i % cols) * (tw + 36)
        cy = my + (i // cols) * (th + 36)
        acc = accents[i]
        d.rounded_rectangle([cx, cy, cx + tw, cy + th], radius=14,
                            fill=(18, 22, 32, 255), outline=(38, 44, 61, 255), width=2)
        d.rectangle([cx, cy, cx + tw, cy + 7], fill=acc)
        d.text((cx + 32, cy + 32), icon, font=f_ic, fill=acc)
        d.text((cx + 132, cy + 46), title, font=f_t, fill=WHITE)
        d.multiline_text((cx + 36, cy + 156), desc, font=f_d, fill=DIM, spacing=12)

    f_f = ImageFont.truetype(MONO_B, 30)
    sp_text(d, (0, H - 78), "PIXELFORGE  ·  SPRITE SHEET MAKER & PIXEL ART STUDIO  ·  v1.1",
            f_f, (90, 99, 120), spacing=3, anchor_center_x=W / 2)

    out = os.path.join(FAB, "fab-features-1920x1080.png")
    im.convert("RGB").save(out, optimize=True)
    print("wrote", out, im.size)


if __name__ == "__main__":
    os.makedirs(FAB, exist_ok=True)
    make_cover_1920()
    make_features_1920()
