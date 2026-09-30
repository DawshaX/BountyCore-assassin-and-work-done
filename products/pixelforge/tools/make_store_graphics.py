#!/usr/bin/env python
"""Compose PixelForge store graphics: cover.png (1260x1000) + features.png (1280x720)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BG = os.path.join(ASSETS, "cover_bg.png")

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

AMBER = (255, 181, 69)
CYAN = (65, 214, 195)
WHITE = (232, 236, 246)
DIM = (139, 147, 168)
PANEL = (16, 19, 27, 225)


def cover_bg(w, h):
    im = Image.open(BG).convert("RGBA")
    # cover-crop to target
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def gradient_overlay(im, top_alpha=210, mid_alpha=90):
    """Dark gradient from top (readable text area) to transparent."""
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
    """Text with letter spacing; returns width. If anchor_center_x given, centers."""
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor_center_x is not None:
        x = anchor_center_x - total / 2
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += cw + spacing
    return total


def chip(d, x, y, text, font, border, text_fill, pad=14):
    tw = d.textlength(text, font=font)
    fh = font.size
    w = tw + pad * 2
    h = fh + pad * 1.4
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, outline=border, width=2,
                        fill=(10, 12, 18, 200))
    d.text((x + pad, y + pad * 0.62), text, font=font, fill=text_fill)
    return w, h


def make_cover():
    W, H = 1260, 1000
    im = gradient_overlay(cover_bg(W, H))
    d = ImageDraw.Draw(im)

    f_title = ImageFont.truetype(SANS_B, 150)
    f_sub = ImageFont.truetype(MONO_B, 34)
    f_chip = ImageFont.truetype(MONO_B, 24)
    f_badge = ImageFont.truetype(MONO_B, 22)

    # top hairline
    d.rectangle([0, 0, W, 8], fill=AMBER)

    # title with amber→cyan gradient per letter
    title = "PIXELFORGE"
    widths = [d.textlength(c, font=f_title) for c in title]
    spacing = 6
    total = sum(widths) + spacing * (len(title) - 1)
    x = (W - total) / 2
    y = 92
    for i, (c, cw) in enumerate(zip(title, widths)):
        t = i / max(1, len(title) - 1)
        col = tuple(round(AMBER[j] + (CYAN[j] - AMBER[j]) * t) for j in range(3))
        # soft shadow
        d.text((x + 5, y + 6), c, font=f_title, fill=(0, 0, 0, 160))
        d.text((x, y), c, font=f_title, fill=col + (255,))
        x += cw + spacing

    # subtitle
    sp_text(d, (0, 285), "SPRITE  SHEET  MAKER  &  PIXEL  ART  STUDIO",
            f_sub, WHITE, spacing=4, anchor_center_x=W / 2)

    # divider
    d.rectangle([W / 2 - 260, 355, W / 2 + 260, 359], fill=CYAN)

    # feature chips (centered rows)
    rows = [
        ["100% OFFLINE", "NO WATERMARKS", "GIF IN + OUT"],
        ["PHASER · ASEPRITE", "UNDO / REDO", "MULTI-PAGE PNG"],
    ]
    cy = 392
    for row in rows:
        widths2 = []
        fonts = [f_chip] * len(row)
        for txt, f in zip(row, fonts):
            widths2.append(d.textlength(txt, font=f) + 28 * 2)
        gap = 18
        total_w = sum(widths2) + gap * (len(row) - 1)
        cx = (W - total_w) / 2
        for txt, f, tw in zip(row, fonts, widths2):
            chip(d, cx, cy, txt, f, CYAN, WHITE)
            cx += tw + gap
        cy += 58

    # version badge
    chip(d, 36, H - 74, "v1.1", f_badge, AMBER, AMBER, pad=12)

    # bottom hairline
    d.rectangle([0, H - 8, W, H], fill=CYAN)

    out = os.path.join(ASSETS, "cover.png")
    im.convert("RGB").save(out, quality=95)
    print("wrote", out, im.size)


def make_features():
    W, H = 1280, 720
    im = Image.new("RGBA", (W, H), (11, 13, 18, 255))
    d = ImageDraw.Draw(im)

    # subtle checker
    for y in range(0, H, 32):
        for x in range(0, W, 32):
            if ((x // 32) + (y // 32)) % 2 == 0:
                d.rectangle([x, y, x + 31, y + 31], fill=(15, 18, 26, 255))

    f_h = ImageFont.truetype(SANS_B, 54)
    f_ic = ImageFont.truetype(SANS_B, 46)
    f_t = ImageFont.truetype(SANS_B, 27)
    f_d = ImageFont.truetype(MONO_B, 19)

    sp_text(d, (0, 44), "EVERYTHING IN ONE TOOL", f_h, AMBER, spacing=6, anchor_center_x=W / 2)
    d.rectangle([W / 2 - 200, 118, W / 2 + 200, 122], fill=CYAN)

    tiles = [
        ("▦", "DROP & PACK", "Batch, folder & GIF\nimport, reorder, trim"),
        ("◈", "PIXELATE", "Auto palette + 12 retro\nBayer / Floyd dithering"),
        ("▶", "LIVE PREVIEW", "1–60 FPS + pivot editor\nloop / ping-pong / once"),
        ("▣", "ATLAS EXPORT", "Generic · Phaser 3\nAseprite · CSS · GIF"),
        ("⊞", "EXTRUDE + SCALE", "Multi-page, no bleeding\n1–8× nearest-neighbour"),
        ("⌁", "100% OFFLINE", "No cloud, no watermark\nUndo / Redo built-in"),
    ]

    cols, rows_n = 3, 2
    mx, my = 44, 160
    tw = (W - mx * 2 - 24 * (cols - 1)) / cols
    th = 218

    accents = [AMBER, CYAN, (255, 107, 107), (122, 92, 255), CYAN, AMBER]
    for i, (icon, title, desc) in enumerate(tiles):
        cx = mx + (i % cols) * (tw + 24)
        cy = my + (i // cols) * (th + 24)
        acc = accents[i]
        d.rounded_rectangle([cx, cy, cx + tw, cy + th], radius=12,
                            fill=(18, 22, 32, 255), outline=(38, 44, 61, 255), width=2)
        d.rectangle([cx, cy, cx + tw, cy + 5], fill=acc)
        d.text((cx + 22, cy + 22), icon, font=f_ic, fill=acc)
        d.text((cx + 90, cy + 32), title, font=f_t, fill=WHITE)
        d.multiline_text((cx + 24, cy + 104), desc, font=f_d, fill=DIM, spacing=8)

    # footer
    f_f = ImageFont.truetype(MONO_B, 22)
    sp_text(d, (0, H - 58), "PIXELFORGE  ·  SPRITE SHEET MAKER & PIXEL ART STUDIO  ·  v1.0",
            f_f, (90, 99, 120), spacing=2, anchor_center_x=W / 2)

    out = os.path.join(ASSETS, "features.png")
    im.convert("RGB").save(out, quality=95)
    print("wrote", out, im.size)


if __name__ == "__main__":
    make_cover()
    make_features()
