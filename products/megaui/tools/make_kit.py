"""MegaUI mass-production generator — builds the full kit tree.

Output: dist/kit/svg/<theme>/<group>/<name>.svg  +  dist/kit/manifest.json
Every file is an original parametric SVG produced by svgkit.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import THEMES, STATES  # noqa: E402
import svgkit as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "dist", "kit")
SVG = os.path.join(KIT, "svg")

SHAPES = ["standard", "pill", "square", "chamfer", "bracket",
          "bevel", "tab", "arrow", "notch"]
KINDS = ["primary", "secondary", "danger", "ghost"]
BAR_KINDS = ["hp", "mana", "xp", "stamina", "gold"]
BAR_SIZES = [("sm", 200, 24), ("md", 320, 32), ("lg", 480, 44)]
RARITIES = ["common", "rare", "epic", "legendary"]
SLOT_SIZES = [48, 64, 96, 128]
PANEL_SIZES = [("sm", 360, 200), ("md", 520, 320), ("lg", 720, 460)]
KEYS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [str(d) for d in range(10)] + \
       ["UP", "DOWN", "LEFT", "RIGHT", "ESC", "SPC"]
CARD_ICONS = ["sword", "shield", "bolt", "potion", "fire", "gem", "crown", "wand"]


def w(path, svg):
    with open(path, "w") as f:
        f.write(svg)


def build_theme(theme):
    counts = {}

    def put(group, name, svg):
        d = os.path.join(SVG, theme, group)
        os.makedirs(d, exist_ok=True)
        w(os.path.join(d, name + ".svg"), svg)
        counts[group] = counts.get(group, 0) + 1

    # ---- buttons: 9 shapes x 4 states x 4 kinds = 144
    for shape in SHAPES:
        for st in STATES:
            for kind in KINDS:
                lbl = {"primary": "PLAY", "secondary": "OPTIONS",
                       "danger": "DELETE", "ghost": "CANCEL"}[kind]
                put("buttons", f"{shape}-{kind}-{st}",
                    K.button(240, 60, theme, st, kind, label=lbl, shape=shape))

    # ---- pill CTAs + icon buttons
    for shape in SHAPES:
        put("buttons", f"{shape}-cta-normal",
            K.button(300, 56, theme, "normal", "primary", label="CONTINUE",
                     shape=shape))
        put("iconbuttons", f"{shape}-play",
            K.button(64, 64, theme, "normal", "secondary", shape=shape))

    # ---- bars: 5 kinds x 3 sizes x 2 styles
    for kind in BAR_KINDS:
        for sn, bw, bh in BAR_SIZES:
            put("bars", f"{kind}-{sn}-segmented",
                K.bar(bw, bh, theme, kind, 0.68, segmented=True))
            put("bars", f"{kind}-{sn}-plain",
                K.bar(bw, bh, theme, kind, 0.68, segmented=False))
            put("bars", f"{kind}-{sn}-empty",
                K.bar(bw, bh, theme, kind, 0.0, segmented=True))

    # ---- rings
    for kind in BAR_KINDS:
        put("rings", f"{kind}-128", K.ring(128, theme, 0.72, label="72%", kind=kind))
        put("rings", f"{kind}-96", K.ring(96, theme, 0.45, kind=kind))

    # ---- slots
    for sz in SLOT_SIZES:
        put("slots", f"empty-{sz}", K.slot(sz, theme))
        for rar in RARITIES:
            put("slots", f"{rar}-{sz}",
                K.slot(sz, theme, rarity=rar))
        for ic in ("sword", "potion", "gem", "coin"):
            put("slots", f"{ic}-{sz}",
                K.slot(sz, theme, icon_name=ic, rarity="rare"))

    # ---- panels / windows
    for pn, pw, ph in PANEL_SIZES:
        put("panels", f"window-{pn}",
            K.panel(pw, ph, theme, title=True, label="Inventory"))
        put("panels", f"bare-{pn}",
            K.panel(pw, ph, theme, title=False))
    put("windows", "dialog-confirm",
        K.dialog(500, 310, theme, "Confirm", "Proceed with the quest?",
                 "ACCEPT", "DECLINE"))
    put("windows", "dialog-alert",
        K.dialog(500, 310, theme, "Warning", "This action cannot be undone!",
                 "CONFIRM", "GO BACK"))
    for tw in (240, 320, 420):
        put("windows", f"tooltip-{tw}",
            K.tooltip(tw, 58, theme, "Deals 120% damage"))
    put("windows", "chat-left", K.bubble(300, 66, theme, "Ready when you are!", "left"))
    put("windows", "chat-right", K.bubble(300, 66, theme, "On my way!", "right"))
    for kind in ("info", "success", "warning", "error"):
        put("windows", f"toast-{kind}",
            K.toast(340, 56, theme, "Achievement unlocked!", kind))

    # ---- forms
    put("forms", "tabs-general", K.tabs(430, 46, theme, ("GENERAL", "VIDEO", "AUDIO"), 0))
    put("forms", "tabs-video", K.tabs(430, 46, theme, ("GENERAL", "VIDEO", "AUDIO"), 1))
    for szn, tw, th in (("md", 76, 38), ("sm", 56, 28)):
        put("forms", f"toggle-on-{szn}", K.toggle(tw, th, theme, True))
        put("forms", f"toggle-off-{szn}", K.toggle(tw, th, theme, False))
        put("forms", f"checkbox-on-{szn}", K.checkbox(int(th * 0.95), theme, True))
        put("forms", f"checkbox-off-{szn}", K.checkbox(int(th * 0.95), theme, False))
        put("forms", f"radio-on-{szn}", K.radio(int(th * 0.95), theme, True))
        put("forms", f"radio-off-{szn}", K.radio(int(th * 0.95), theme, False))
    for val in (0.25, 0.55, 0.85):
        put("forms", f"slider-{int(val*100)}", K.slider(280, 40, theme, val))
    put("forms", "input-focus", K.input(300, 50, theme, "Player name", True))
    put("forms", "input-normal", K.input(300, 50, theme, "Email address", False))
    put("forms", "dropdown", K.dropdown(220, 46, theme, "Normal"))
    for k in KEYS:
        put("forms", f"keycap-{k}", K.keycap(56, theme, k))

    # ---- decor
    for rw in (240, 320, 380, 460):
        put("decor", f"ribbon-{rw}", K.ribbon(rw, 74, theme, label="QUEST COMPLETE"))
    put("decor", "divider-420", K.divider(420, theme))
    put("decor", "divider-240", K.divider(240, theme))
    for shp in ("circle", "square"):
        for sz in (64, 96, 128):
            put("decor", f"portrait-{shp}-{sz}", K.portrait(sz, theme, shp))
    for rar in RARITIES:
        for ci, icn in enumerate(CARD_ICONS[:4]):
            cd = (0.0, 0.45, 0.75)[ci % 3]
            put("decor", f"skill-{rar}-{icn}",
                K.skillcard(96, 96, theme, icn, cd, rar))
    for pos in (0.3, 0.55, 0.8):
        put("decor", f"scrollbar-{int(pos*100)}", K.scrollbar(28, 240, theme, pos))
    for kn in ("gold", "gem", "gem2", "energy"):
        put("decor", f"chip-{kn}-lg", K.chip(170, 44, theme, "12,450", kn))
        put("decor", f"chip-{kn}-sm", K.chip(120, 34, theme, "88", kn))
    for rating in range(6):
        put("decor", f"stars-{rating}", K.stars(340, 44, theme, rating, 5))
    for d in range(1, 10):
        put("decor", f"badge-{d}", K.badge(40, theme, str(d)))

    # ---- item cards + leaderboard
    for rar in RARITIES:
        put("cards", f"item-{rar}",
            K.item_card(360, 128, theme, rarity=rar))
    for rk in range(1, 6):
        nm = ("ShadowKing", "Nova", "PixelKnight", "Raven", "Blade")[rk - 1]
        put("leaderboard", f"row-{rk}",
            K.leaderboard(440, 64, theme, rk, nm, f"{20000 - rk*1731:,}"))

    # ---- HUD overlay widgets (minimap / compass / currency)
    put("hud", "minimap-220", K.minimap(220, theme, "MINIMAP"))
    put("hud", "minimap-180", K.minimap(180, theme, "ZONE 4"))
    for ww in (240, 320, 420):
        put("hud", f"compass-{ww}", K.compass(ww, 54, theme))
    for kn in ("gold", "gem", "gem2", "energy"):
        put("hud", f"currency-{kn}-plus", K.currency(theme, kn, "12,450", with_plus=True))
        put("hud", f"currency-{kn}", K.currency(theme, kn, "386", h=44, with_plus=False))

    # ---- touch controls + meta overlays (batch 3 widgets)
    put("touch", "joystick-engaged", K.joystick(150, theme, engaged=True))
    put("touch", "joystick-idle", K.joystick(150, theme, engaged=False))
    put("touch", "buttons-abxy", K.touch_buttons(theme))
    for ck in ("cross", "circle", "brackets"):
        put("touch", f"crosshair-{ck}", K.crosshair(96, theme, ck))
    put("overlays", "nameplate", K.nameplate(240, 64, theme, "ShadowKing", 42, "", 0.78, 0.55))
    put("overlays", "nameplate-clan", K.nameplate(280, 64, theme, "Nova", 7, "[VOID]", 0.62))
    put("overlays", "killfeed", K.killfeed(300, theme,
        (("Nova", "Blade", "sword"), ("Raven", "Nova", "bolt"))))
    put("overlays", "prompt-e", K.prompt(250, 56, theme, "E", "Open door"))
    put("overlays", "prompt-f", K.prompt(230, 56, theme, "F", "Talk"))
    put("overlays", "radial", K.radial(320, theme))
    put("overlays", "party", K.party(300, 200, theme))
    put("overlays", "ammo-bolt", K.ammo(270, 64, theme, "bolt", 24, 30))
    put("overlays", "ammo-arrow", K.ammo(250, 60, theme, "arrow", 7, 12))
    put("overlays", "subtitle", K.subtitle(560, theme))

    # ---- icons (theme-tinted)
    for name in K.ICON_NAMES:
        put("icons", name, K.icon(name, theme, 96))

    return counts


def main():
    os.makedirs(SVG, exist_ok=True)
    manifest = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "themes": {}, "shapes": SHAPES, "states": STATES,
                "kinds": KINDS, "total": 0}
    for th in THEMES:
        counts = build_theme(th)
        manifest["themes"][th] = counts
        manifest["total"] += sum(counts.values())
        print(f"{th}: {sum(counts.values())} files")
    with open(os.path.join(KIT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("TOTAL:", manifest["total"], "->", KIT)


if __name__ == "__main__":
    main()
