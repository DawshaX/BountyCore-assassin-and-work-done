"""MegaUI screens generator — 12 screen layouts x 4 themes = 48 screens.

Writes dist/kit/screens/<theme>/<name>.html (1920x1080), rendered to 4K PNG
by tools/render4k.js.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import THEMES  # noqa: E402
import svgkit as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "kit", "screens")

COPY = {
    "darkfantasy": dict(
        game="REALM OF SHADOWS", cta="ENTER DUNGEON", ribbon="THE DARK KEEP",
        quests=[("Slay 10 Ghouls", True), ("Find the Relic", False),
                ("Return to Elder", False)],
        chat="The raid begins at dusk...", item="Iron Sword", item_sub="DMG 12-18",
        hero="ShadowKing", score="99,120",
        inv=[("sword", "Iron Sword"), ("potion", "Health Flask"), ("shield", "Oak Shield"),
             ("key", "Crypt Key"), ("gem", "Soul Gem"), ("coin", "Gold Pouch")],
        skills=["sword", "fire", "potion", "bolt", "bag", "wand"],
        stats=[("HEALTH", 0.82, "hp"), ("MANA", 0.54, "mana"), ("STAMINA", 0.66, "stamina")]),
    "scifi": dict(
        game="NEON PROTOCOL", cta="LAUNCH MISSION", ribbon="SECTOR 07 // RAID",
        quests=[("Calibrate warp core", True), ("Defend the station", False),
                ("Scan anomaly K-9", False)],
        chat="Shields at 98%, commander.", item="Pulse Rifle", item_sub="DMG 24-31",
        hero="Nova", score="148,900",
        inv=[("bolt", "Pulse Rifle"), ("shield", "Aegis Module"), ("eye", "Optic Cam"),
             ("target", "Target Chip"), ("gear", "Servo Kit"), ("gem", "Flux Crystal")],
        skills=["bolt", "target", "eye", "shield", "bag", "gear"],
        stats=[("SHIELD", 0.91, "hp"), ("ENERGY", 0.47, "mana"), ("OXYGEN", 0.78, "stamina")]),
    "royal": dict(
        game="KINGDOM CHRONICLES", cta="CONTINUE", ribbon="KINGDOM CAMPAIGN",
        quests=[("Escort the merchant", True), ("Clear the wolves", False),
                ("Deliver the decree", False)],
        chat="Your grace, the army awaits.", item="Longsword", item_sub="DMG 10-16",
        hero="Aurelia", score="56,780",
        inv=[("sword", "Longsword"), ("crown", "Gold Crown"), ("shield", "Tower Shield"),
             ("potion", "Elixir"), ("gem", "Royal Ruby"), ("flag", "Banner")],
        skills=["sword", "crown", "potion", "flag", "bag", "shield"],
        stats=[("HEALTH", 0.75, "hp"), ("MANA", 0.62, "mana"), ("STAMINA", 0.58, "stamina")]),
    "pixel": dict(
        game="PIXEL QUEST 64", cta="START GAME", ribbon="LEVEL 1-4",
        quests=[("Get the key card", True), ("Beat stage boss", False),
                ("Find 3 secrets", False)],
        chat="press START to play!", item="Steel Blade", item_sub="DMG 08-14",
        hero="PixelKnight", score="31,400",
        inv=[("sword", "Steel Blade"), ("key", "Key Card"), ("potion", "Juice Box"),
             ("star", "Power Star"), ("coin", "Coin Stack"), ("shield", "Buckler")],
        skills=["play", "potion", "bolt", "key", "bag", "star"],
        stats=[("HEALTH", 0.88, "hp"), ("MANA", 0.40, "mana"), ("STAMINA", 0.70, "stamina")]),
}

SHAPES_BY_THEME = {"darkfantasy": "standard", "scifi": "bevel",
                   "royal": "standard", "pixel": "standard"}


def wrap(theme, body, dim=False):
    t = THEMES[theme]
    dim_css = ("background:rgba(0,0,0,.55);" if dim else "")
    return f'''<!doctype html><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:Verdana,'DejaVu Sans',sans-serif}}
body{{width:1920px;height:1080px;overflow:hidden;background:{t["bg"]};color:{t["ink"]};position:relative}}
.bg{{position:absolute;inset:0;background:
  radial-gradient(90% 70% at 20% 0%, {t["panel2"]}88, transparent 60%),
  radial-gradient(70% 60% at 90% 100%, {t["accent"]}22, transparent 55%),
  linear-gradient(180deg, {t["panel"]}55, {t["bg"]})}}
.wm{{position:absolute;right:-60px;bottom:-80px;opacity:.05;transform:rotate(-12deg)}}
.el{{position:absolute}}
.dim{{position:absolute;inset:0;{dim_css}}}
h1{{font-size:76px;letter-spacing:6px;color:{t["accent"]};text-shadow:0 4px 0 rgba(0,0,0,.5)}}
h2{{font-size:34px;letter-spacing:3px}}
.sub{{font-size:16px;letter-spacing:4px;opacity:.6}}
.lbl{{font-size:13px;letter-spacing:2px;opacity:.55;text-transform:uppercase}}
.card{{background:{t["panel"]}cc;border:1px solid {t["stroke"]};border-radius:8px;padding:18px 22px}}
.row{{display:flex;gap:16px;align-items:center}}
.col{{display:flex;flex-direction:column;gap:14px}}
</style>
<div class="bg"></div>
<div class="wm">{K.icon("crown" if theme in ("royal", "darkfantasy") else "gear", theme, 900)}</div>
{body}
'''


def E(x, y, html):
    return f'<div class="el" style="left:{x}px;top:{y}px">{html}</div>'


def screen_mainmenu(th):
    c, sh = COPY[th], SHAPES_BY_THEME[th]
    btns = "".join(
        E(180, 340 + i * 110, K.button(460, 84, th, "normal", k, label=l, shape=sh))
        for i, (k, l) in enumerate(
            [("primary", c["cta"]), ("secondary", "CONTINUE"),
             ("secondary", "OPTIONS"), ("ghost", "QUIT")]))
    return wrap(th, f'''
{E(170, 140, f'<h1>{c["game"]}</h1>')}
{E(174, 235, f'<div class="sub">A MEGAUI DEMO BUILD</div>')}
{E(176, 270, K.divider(460, th))}
{btns}
{E(180, 960, '<div class="lbl">v1.0 · 4 themes · 1784 components</div>')}
{E(1500, 60, f'<div class="row">{K.chip(180,48,th,"12,450","gold")}{K.chip(150,48,th,"386","gem")}</div>')}
{E(1520, 860, K.stars(300, 40, th, 5, 5))}
''')


def screen_hud(th):
    c = COPY[th]
    slots = "".join(
        f'<div class="el">{K.skillcard(110, 110, th, ic, (0, .45, .7, 0, .25, 0)[i], ["rare","epic","rare","legendary","rare","common"][i], label=str(i+1))}</div>'
        for i, ic in enumerate(c["skills"]))
    quests = "".join(
        f'<div class="card row" style="gap:12px">{K.icon("check" if d else "question", th, 30, color=(THEMES[th]["good"] if d else THEMES[th]["muted"]))}<div><b style="font-size:18px">{q}</b><div class="lbl">{"Completed" if d else "In progress"}</div></div></div>'
        for q, d in c["quests"])
    bars = "".join(
        f'<div class="col" style="gap:6px"><div class="lbl">{n}</div>{K.bar(360, 30, th, k, v)}</div>'
        for n, v, k in c["stats"])
    return wrap(th, f'''
{E(50, 40, f'<div class="row" style="gap:14px">{K.chip(190,50,th,"12,450","gold")}{K.chip(150,50,th,"386","gem")}</div>')}
{E(50, 130, bars)}
{E(810, 36, K.ribbon(420, 80, th, label=c["ribbon"]))}
{E(940, 150, f'<div class="lbl" style="text-align:center">BOSS · VOID TITAN</div>{K.bar(760, 40, th, "hp", 0.62, True)}')}
{E(1450, 40, "".join(f'<div class="el" style="left:{i*74}px">{K.slot(64, th, icon_name=n)}</div>' for i, n in enumerate(("gear", "search", "user"))))}
{E(1460, 140, f'<div style="position:relative;width:400px">{K.panel(400, 320, th, label="QUESTS")}<div style="position:absolute;top:64px;left:14px;right:14px;display:flex;flex-direction:column;gap:10px">{quests}</div></div>')}
{E(600, 700, f'<div class="row" style="gap:12px;padding:14px 18px;background:rgba(0,0,0,.4);border:1px solid {THEMES[th]["stroke"]};border-radius:8px">{slots}</div>')}
{E(700, 880, f'<div class="row" style="gap:18px">{K.button(340,72,th,"normal","primary",label=c["cta"],shape=SHAPES_BY_THEME[th])}{K.button(220,72,th,"normal","ghost",label="MENU")}</div>')}
{E(60, 760, K.toast(380, 56, th, c["chat"], "info"))}
''')


def screen_inventory(th):
    c = COPY[th]
    grid = "".join(
        f'<div class="el">{K.slot(104, th, icon_name=(c["inv"][i % 6][0] if i < 12 else None), rarity=("rare" if i % 3 == 0 else "epic" if i % 3 == 1 else None))}</div>'
        for i in range(24))
    eq = "".join(
        f'<div class="el" style="left:{(i%2)*130}px;top:{(i//2)*130}px">{K.slot(110, th, icon_name=ic, rarity="legendary")}</div>'
        for i, ic in enumerate(("crown", "sword", "shield", "potion")))
    stats = "".join(
        f'<div class="col" style="gap:6px"><div class="lbl">{n}</div>{K.bar(300, 26, th, k, v, False)}</div>'
        for n, v, k in c["stats"])
    return wrap(th, f'''
{E(60, 40, f'<h2>INVENTORY</h2>')}
{E(60, 110, K.tabs(500, 50, th, ("ITEMS", "GEAR", "MISC"), 0))}
{E(60, 210, '<div class="lbl">Equipment</div>')}
{E(60, 250, f'<div style="position:relative;width:250px;height:270px">{eq}</div>')}
{E(60, 560, '<div class="lbl">Hero</div>')}
{E(60, 595, K.portrait(150, th, "circle"))}
{E(230, 620, f'<div><b style="font-size:26px">{c["hero"]}</b><div class="lbl">Level 42</div></div>')}
{E(60, 790, f'<div class="col">{stats}</div>')}
{E(400, 210, '<div class="lbl">Backpack · 24 slots</div>')}
{E(400, 250, f'<div style="position:relative;width:680px;height:560px">{grid}</div>')}
{E(1140, 110, f'<div style="position:relative;width:720px;height:900px">{K.panel(720, 900, th, label="ITEM DETAIL")}')}
{E(1190, 220, K.slot(160, th, icon_name=c["inv"][0][0], rarity="legendary"))}
{E(1390, 240, f'<div class="col" style="gap:8px"><b style="font-size:34px">{c["item"]}</b><div class="lbl">{c["item_sub"]}</div>{K.stars(260,36,th,4,5)}</div>')}
{E(1190, 430, f'<div class="card" style="width:600px"><div class="lbl">Description</div><p style="margin-top:10px;font-size:17px;line-height:1.6;opacity:.85">A blade forged in the old ways. Balanced, dependable, and ready for whatever waits beyond the gate.</p></div>')}
{E(1190, 640, f'<div class="col">{stats.replace("300","560")}</div>')}
{E(1190, 880, f'<div class="row">{K.button(300,64,th,"normal","primary",label="EQUIP")}{K.button(220,64,th,"normal","ghost",label="DROP")}</div>')}
''')


def screen_shop(th):
    c = COPY[th]
    cards = "".join(
        f'<div class="el" style="left:{(i%3)*400}px;top:{(i//3)*250}px">{K.item_card(370, 210, th, name=nm, sub=f"DMG {10+i}-{18+i}", price=str(150+i*40), rarity=("rare", "epic", "legendary")[i%3], icon_name=ic)}</div>'
        for i, (ic, nm) in enumerate(c["inv"]))
    return wrap(th, f'''
{E(60, 40, '<h2>ROYAL MARKET</h2>')}
{E(60, 110, K.tabs(520, 50, th, ("BUY", "SELL", "TRADE"), 0))}
{E(1400, 46, f'<div class="row" style="gap:14px">{K.chip(200,52,th,"12,450","gold")}{K.chip(160,52,th,"386","gem")}</div>')}
{E(60, 210, f'<div style="position:relative;width:1230px;height:530px">{cards}</div>')}
{E(1360, 210, f'<div style="position:relative;width:500px;height:640px">{K.panel(500, 640, th, label="FEATURED")}')}
{E(1410, 300, K.slot(180, th, icon_name=c["inv"][2][0], rarity="legendary"))}
{E(1410, 510, f'<div class="col" style="gap:8px"><b style="font-size:28px">{c["item"]}</b><div class="lbl">Legendary · limited stock</div></div>')}
{E(1410, 640, K.button(400, 64, th, "normal", "primary", label="BUY · 950", shape=SHAPES_BY_THEME[th]))}
{E(60, 900, f'<div class="row" style="gap:16px">{K.button(240,64,th,"normal","ghost",label="BACK")}{K.button(280,64,th,"normal","secondary",label="REFRESH")}</div>')}
''')


def screen_settings(th):
    def toggle_row(y, label, on):
        inner = '<div class="lbl">' + label + '</div>'
        return (E(160, y, inner)
                + E(760, y - 8, K.toggle(96, 44, th, on)))

    def slider_row(y, label, v):
        inner = '<div class="lbl">' + label + '</div>'
        return (E(160, y, inner)
                + E(560, y - 12, K.slider(480, 44, th, v)))
    return wrap(th, f'''
{E(160, 60, '<h2>SETTINGS</h2>')}
{E(160, 140, K.tabs(640, 54, th, ("AUDIO", "VIDEO", "GAMEPLAY"), 0))}
{toggle_row(260, "Music", True)}
{toggle_row(350, "Sound effects", True)}
{toggle_row(440, "Subtitles", False)}
{slider_row(560, "Master volume", 0.75)}
{slider_row(660, "Brightness", 0.55)}
{E(160, 780, '<div class="lbl">Graphics quality</div>')}
{E(560, 765, K.dropdown(300, 52, th, "High"))}
{E(160, 880, '<div class="lbl">Control preset</div>')}
{E(560, 870, "".join(K.radio(40, th, i == 1) for i in range(3)) +
  f'<span style="position:absolute;left:150px;top:8px" class="lbl">WASD</span>')}
{E(1300, 140, f'<div style="position:relative;width:480px;height:780px">{K.panel(480, 780, th, label="KEY BINDINGS")}')}
{E(1340, 240, "".join(
    f'<div class="el" style="left:0;top:{i*90}px;width:400px" class="row">{K.keycap(56, th, k)}<span class="lbl" style="margin-left:18px">{a}</span></div>'
    for i, (k, a) in enumerate([("W", "Jump"), ("A", "Move left"), ("S", "Duck"),
                                 ("D", "Move right"), ("E", "Interact"),
                                 ("ESC", "Pause"), ("SPC", "Attack")])) )}
''')


def screen_pause(th):
    c = COPY[th]
    menu = "".join(
        f'<div class="el" style="left:110px;top:{150+i*110}px">{K.button(420, 80, th, "normal", k, label=l, shape=SHAPES_BY_THEME[th])}</div>'
        for i, (k, l) in enumerate([("primary", "RESUME"), ("secondary", "RESTART"),
                                    ("secondary", "SETTINGS"), ("danger", "QUIT TO MENU")]))
    return wrap(th, f'''
<div class="dim"></div>
{E(560, 130, f'<div style="position:relative;width:640px;height:820px">{K.panel(640, 820, th, label="PAUSED")}')}
{E(700, 200, K.divider(360, th))}
{menu}
{E(700, 700, f'<div class="lbl" style="text-align:center">{c["hero"]} · Level 42 · {c["ribbon"]}</div>')}
''')


def screen_dialog(th):
    c = COPY[th]
    return wrap(th, f'''
{E(140, 160, K.portrait(220, th, "circle"))}
{E(140, 410, f'<b style="font-size:32px;letter-spacing:3px">ELDER MORATH</b>')}
{E(140, 460, '<div class="lbl">Quest giver</div>')}
{E(560, 160, f'<div style="position:relative;width:1220px;height:760px">{K.panel(1220, 760, th, label="DIALOG")}')}
{E(640, 300, f'<div style="font-size:26px;line-height:1.7;opacity:.92;max-width:1020px">"The keep has fallen silent, traveler. Whatever stirs in its depths waits for <b style="color:{THEMES[th]["accent"]}">you</b>. Take this boon — and do not fall like the others."</div>')}
{E(640, 520, K.bubble(420, 70, th, c["chat"], "left"))}
{E(640, 640, f'<div class="row" style="gap:20px">{K.button(360,76,th,"normal","primary",label="ACCEPT QUEST")}{K.button(260,76,th,"normal","ghost",label="NOT NOW")}</div>')}
{E(640, 780, f'<div class="row" style="gap:14px"><div class="lbl">Reward</div>{K.chip(170,48,th,"2,500","gold")}{K.chip(150,48,th,"120","gem")}{K.slot(64,th,icon_name="sword",rarity="epic")}</div>')}
''')


def screen_map(th):
    c = COPY[th]
    regions = "".join(
        f'<div class="el" style="left:{(i%3)*300+40}px;top:{(i//3)*230+40}px">{K.panel(260, 190, th, title=False)}</div>'
        for i in range(6))
    marks = "".join(
        f'<div class="el" style="left:{(i%4)*260+90}px;top:{(i//4)*200+90}px">{K.slot(64, th, icon_name=ic, rarity="rare")}</div>'
        for i, ic in enumerate(("flag", "castle" if False else "crown", "skull", "coin",
                                "gem", "potion", "star", "key")))
    return wrap(th, f'''
{E(60, 40, '<h2>WORLD MAP</h2>')}
{E(60, 120, f'<div style="position:relative;width:1120px;height:860px">{K.panel(1120, 860, th, label="THE KNOWN REALMS")}{regions}{marks}</div>')}
{E(1240, 120, f'<div style="position:relative;width:620px;height:420px">{K.panel(620, 420, th, label="REGION")}')}
{E(1290, 210, f'<b style="font-size:30px">Ashen Vale</b>')}
{E(1290, 260, f'<div class="lbl">Recommended level 30+</div>')}
{E(1290, 320, K.bar(500, 30, th, "xp", 0.42))}
{E(1290, 380, '<div class="lbl">Discovery 42%</div>')}
{E(1240, 590, f'<div style="position:relative;width:620px;height:390px">{K.panel(620, 390, th, label="FAST TRAVEL")}')}
{E(1290, 670, "".join(f'<div class="el" style="left:{i*100}px">{K.slot(80, th, icon_name=ic)}</div>' for i, ic in enumerate(("home", "flag", "map", "star"))))}
{E(1290, 800, K.button(500, 64, th, "normal", "primary", label="TRAVEL", shape=SHAPES_BY_THEME[th]))}
''')


def screen_quests(th):
    c = COPY[th]
    rows = "".join(
        f'<div class="el" style="left:0;top:{i*110}px">{K.leaderboard(480, 90, th, i+1, q, "ACTIVE" if d else "DONE", icon_name="flag")}</div>'
        for i, (q, d) in enumerate(c["quests"] + [("Hidden trial", False)] * 3))
    objs = "".join(
        f'<div class="card row" style="gap:14px">{K.checkbox(36, th, d)}<span style="font-size:19px">{o}</span></div>'
        for o, d in (("Defeat the gatekeeper", True), ("Open the sealed door", True),
                     ("Recover the relic", False), ("Escape the crypt", False)))
    return wrap(th, f'''
{E(60, 40, '<h2>QUEST LOG</h2>')}
{E(60, 120, K.tabs(560, 50, th, ("ACTIVE", "DONE", "FAILED"), 0))}
{E(60, 210, f'<div style="position:relative;width:480px;height:700px">{rows}</div>')}
{E(620, 120, f'<div style="position:relative;width:1240px;height:790px">{K.panel(1240, 790, th, label=c["quests"][0][0].upper())}')}
{E(680, 230, f'<div class="lbl">Objectives</div>')}
{E(680, 270, f'<div class="col" style="gap:12px;width:700px">{objs}</div>')}
{E(680, 640, f'<div class="lbl">Progress</div>')}
{E(680, 680, K.bar(700, 36, th, "xp", 0.5))}
{E(1440, 230, f'<div class="lbl">Rewards</div>')}
{E(1440, 270, f'<div class="row" style="gap:16px">{K.chip(180,48,th,"5,000","gold")}{K.chip(150,48,th,"250","gem")}</div>')}
{E(1440, 350, f'<div class="row" style="gap:14px">{K.slot(80,th,icon_name="sword",rarity="epic")}{K.slot(80,th,icon_name="potion",rarity="rare")}</div>')}
{E(1440, 500, f'<div class="card" style="width:360px"><div class="lbl">Story</div><p style="margin-top:8px;font-size:16px;line-height:1.6;opacity:.85">The old warning was clear: what sleeps below must stay sleeping.</p></div>')}
{E(680, 820, K.button(460, 72, th, "normal", "primary", label="TRACK QUEST", shape=SHAPES_BY_THEME[th]))}
''')


def screen_character(th):
    c = COPY[th]
    bars = "".join(
        f'<div class="col" style="gap:6px"><div class="lbl">{n}</div>{K.bar(340, 30, th, k, v, False)}</div>'
        for n, v, k in c["stats"])
    gear = "".join(
        f'<div class="el" style="left:{(i%3)*140}px;top:{(i//3)*140}px">{K.slot(120, th, icon_name=ic, rarity=("legendary","epic","rare","rare","epic","common")[i])}</div>'
        for i, (ic, _nm) in enumerate(c["inv"]))
    skills = "".join(
        f'<div class="el" style="left:{i*130}px">{K.skillcard(110, 110, th, ic, (0,.3,.6,0,.45,0)[i], "rare", label=str(i+1))}</div>'
        for i, ic in enumerate(c["skills"]))
    return wrap(th, f'''
{E(60, 40, '<h2>CHARACTER</h2>')}
{E(60, 130, K.tabs(560, 50, th, ("GEAR", "SKILLS", "STATS"), 0))}
{E(60, 230, K.portrait(280, th, "square"))}
{E(60, 540, f'<div class="col" style="gap:6px"><b style="font-size:38px;letter-spacing:3px">{c["hero"]}</b><div class="lbl">Warrior · Level 42</div></div>')}
{E(60, 650, f'<div class="col">{bars}</div>')}
{E(460, 230, '<div class="lbl">Equipment</div>')}
{E(460, 270, f'<div style="position:relative;width:440px;height:300px">{gear}</div>')}
{E(460, 620, '<div class="lbl">Ability loadout</div>')}
{E(460, 660, f'<div style="position:relative;width:800px;height:130px">{skills}</div>')}
{E(460, 830, f'<div class="row" style="gap:16px">{K.button(300,66,th,"normal","primary",label="UPGRADE")}{K.button(240,66,th,"normal","ghost",label="RESET")}</div>')}
{E(1420, 130, f'<div style="position:relative;width:440px;height:860px">{K.panel(440, 860, th, label="ATTRIBUTES")}')}
{E(1470, 240, "".join(f'<div class="el" style="top:{i*100}px;width:340px" >{K.slider(340, 40, th, v)}</div>'
    for i, v in enumerate((.8, .55, .7, .4, .62))))}
{E(1470, 190, '<div class="lbl">STR</div>')}
{E(1470, 290, '<div class="lbl">DEX</div>')}
{E(1470, 390, '<div class="lbl">INT</div>')}
{E(1470, 490, '<div class="lbl">VIT</div>')}
{E(1470, 590, '<div class="lbl">LUK</div>')}
''')


def screen_results(th):
    c = COPY[th]
    loot = "".join(
        f'<div class="el" style="left:{i*170}px">{K.slot(140, th, icon_name=ic, rarity=("rare","epic","legendary","rare")[i])}</div>'
        for i, ic in enumerate(("sword", "gem", "crown", "potion")))
    return wrap(th, f'''
{E(560, 90, K.ribbon(800, 110, th, label="VICTORY"))}
{E(760, 250, K.stars(540, 90, th, 5, 5))}
{E(700, 390, f'<div style="font-size:74px;font-weight:700;letter-spacing:6px;color:{THEMES[th]["accent"]}">{c["score"]}</div>')}
{E(830, 500, '<div class="lbl">Total score</div>')}
{E(640, 590, f'<div class="card" style="width:640px;text-align:center"><div class="lbl">Time 04:32 · Damage 12,480 · Combo x18</div></div>')}
{E(640, 720, '<div class="lbl">Rewards</div>')}
{E(640, 760, f'<div style="position:relative;width:680px;height:150px">{loot}</div>')}
{E(560, 940, f'<div class="row" style="gap:20px">{K.button(340,74,th,"normal","primary",label="CONTINUE",shape=SHAPES_BY_THEME[th])}{K.button(260,74,th,"normal","ghost",label="RETRY")}</div>')}
''')


def screen_login(th):
    return wrap(th, f'''
{E(660, 90, f'<div style="text-align:center;width:600px"><h1 style="font-size:58px">{COPY[th]["game"]}</h1></div>')}
{E(660, 200, K.divider(600, th))}
{E(560, 270, f'<div style="position:relative;width:800px;height:700px">{K.panel(800, 700, th, label="SIGN IN")}')}
{E(640, 400, f'<div class="lbl">Username</div>')}
{E(640, 435, K.input(640, 58, th, "Enter your name", True))}
{E(640, 540, f'<div class="lbl">Password</div>')}
{E(640, 575, K.input(640, 58, th, "••••••••••", False))}
{E(640, 670, "".join(K.radio(36, th, True) for _ in [0]) +
  f'<span class="lbl" style="margin-left:14px">Remember me</span>')}
{E(640, 740, K.button(640, 64, th, "normal", "primary", label="LOG IN", shape=SHAPES_BY_THEME[th]))}
{E(640, 830, f'<div class="row" style="gap:20px">{K.button(310,56,th,"normal","ghost",label="GUEST")}{K.button(310,56,th,"normal","secondary",label="SIGN UP")}</div>')}
{E(640, 920, '<div class="lbl">Secured with MegaUI auth · v1.0</div>')}
''')


SCREENS = [
    ("01-main-menu", screen_mainmenu),
    ("02-hud", screen_hud),
    ("03-inventory", screen_inventory),
    ("04-shop", screen_shop),
    ("05-settings", screen_settings),
    ("06-pause", screen_pause),
    ("07-dialog", screen_dialog),
    ("08-world-map", screen_map),
    ("09-quests", screen_quests),
    ("10-character", screen_character),
    ("11-results", screen_results),
    ("12-login", screen_login),
]


def main():
    n = 0
    for th in THEMES:
        d = os.path.join(OUT, th)
        os.makedirs(d, exist_ok=True)
        for name, fn in SCREENS:
            html = fn(th)
            with open(os.path.join(d, name + ".html"), "w") as f:
                f.write(html)
            n += 1
    print("screens written:", n, "->", OUT)


if __name__ == "__main__":
    main()
