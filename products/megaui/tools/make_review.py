"""Generate build/review/review.html — one themed section per theme.

v2 contact sheet: buttons / form controls / windows / bars / loot / icons
plus a composed HUD mockup per theme to prove real-world assembly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import THEMES, STATES  # noqa: E402
import svgkit as K  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "build", "review")

MOCK = {
    "darkfantasy": {
        "ribbon": "THE DARK KEEP",
        "quest": [("Slay 10 Ghouls", True), ("Find the Relic", False),
                  ("Return to Elder", False)],
        "cta": "ENTER DUNGEON",
        "chat": "The raid begins at dusk...",
        "tip": "Deals 120% shadow damage",
        "lv": "LV 27",
        "icons": ["sword", "potion", "fire", "bolt", "bag", "wand"],
    },
    "scifi": {
        "ribbon": "SECTOR 07 // RAID",
        "quest": [("Calibrate warp core", True), ("Defend the station", False),
                  ("Scan anomaly K-9", False)],
        "cta": "LAUNCH MISSION",
        "chat": "Shields at 98%, commander.",
        "tip": "Overcharge: +40% output",
        "lv": "LVL 42",
        "icons": ["bolt", "target", "eye", "shield", "bag", "gear"],
    },
    "royal": {
        "ribbon": "KINGDOM CAMPAIGN",
        "quest": [("Escort the merchant", True), ("Clear the wolves", False),
                  ("Deliver the decree", False)],
        "cta": "CONTINUE",
        "chat": "Your grace, the army awaits.",
        "tip": "Restores 30 HP over 5s",
        "lv": "LVL 12",
        "icons": ["sword", "potion", "crown", "flag", "bag", "shield"],
    },
    "pixel": {
        "ribbon": "LEVEL 1-4",
        "quest": [("Get the key card", True), ("Beat stage boss", False),
                  ("Find 3 secrets", False)],
        "cta": "START GAME",
        "chat": "press START to play!",
        "tip": "x2 damage for 10s",
        "lv": "LV 08",
        "icons": ["play", "potion", "bolt", "key", "bag", "star"],
    },
}


def _fig(svg, cap, cls=""):
    return f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'


def section(key):
    t = THEMES[key]
    m = MOCK[key]
    c = []

    # ---------------- buttons ----------------
    for st in STATES:
        c.append(_fig(K.button(240, 60, key, st, "primary", label="PLAY"),
                      f"primary · {st}"))
    for kind, word in (("secondary", "OPTIONS"), ("danger", "DELETE"),
                       ("ghost", "CANCEL")):
        c.append(_fig(K.button(240, 60, key, "normal", kind, label=word), kind))
    c.append(_fig(K.button(260, 54, key, "normal", "primary", label="CLAIM",
                           shape="pill"), "pill · claim"))
    c.append(_fig(K.button(260, 54, key, "normal", "secondary", label="BACK",
                           shape="pill"), "pill · back"))

    buttons = f'<div class="band"><h3>Buttons · 4 states × 4 kinds + pill</h3>' \
              f'<div class="grid">{"".join(c)}</div></div>'

    # ---------------- form controls ----------------
    f = []
    f.append(_fig(K.tabs(430, 46, key, ("GENERAL", "VIDEO", "AUDIO"), 1), "tabs"))
    f.append(_fig(K.toggle(76, 38, key, True), "toggle · on"))
    f.append(_fig(K.toggle(76, 38, key, False), "toggle · off"))
    f.append(_fig(K.checkbox(40, key, True), "check · on"))
    f.append(_fig(K.checkbox(40, key, False), "check · off"))
    f.append(_fig(K.slider(280, 40, key, 0.55), "slider"))
    f.append(_fig(K.input(300, 50, key, "Player name", True), "input · focus"))
    f.append(_fig(K.input(300, 50, key, "Email address", False), "input"))
    f.append(_fig(K.dropdown(220, 46, key, "Normal"), "dropdown"))
    kc = "".join(_fig(K.keycap(54, key, k), k, "tight") for k in ("W", "A", "S", "D"))
    f.append(f'<figure><div class="row">{kc}</div><figcaption>keycaps</figcaption></figure>')
    f.append(_fig(K.chip(160, 42, key, "1,250", "gold"), "chip · gold"))
    f.append(_fig(K.chip(160, 42, key, "88", "gem"), "chip · gem"))
    form = f'<div class="band"><h3>Form controls &amp; inputs</h3>' \
           f'<div class="grid">{"".join(f)}</div></div>'

    # ---------------- windows ----------------
    w = []
    w.append(_fig(K.dialog(500, 310, key), "dialog", "wide"))
    w.append(_fig(K.panel(460, 310, key, label="Inventory"), "panel", "wide"))
    w.append(_fig(K.tooltip(320, 58, key, m["tip"]), "tooltip", "wide"))
    w.append(_fig(K.bubble(300, 66, key, m["chat"], "left"), "chat · left"))
    w.append(_fig(K.bubble(300, 66, key, "Ready when you are!", "right"),
                  "chat · right", "wide"))
    windows = f'<div class="band"><h3>Windows, dialogs &amp; chat</h3>' \
              f'<div class="grid">{"".join(w)}</div></div>'

    # ---------------- bars & status ----------------
    b = []
    for kind in ("hp", "mana", "xp", "stamina"):
        b.append(_fig(K.bar(430, 36, key, kind, 0.68), f"bar · {kind}", "wide"))
    b.append(_fig(K.ring(150, key, 0.72, label="72%", kind="xp"), "ring · xp"))
    b.append(_fig(K.ring(150, key, 0.35, label="35%", kind="hp"), "ring · hp"))
    b.append(_fig(K.stars(340, 48, key, 4, 5), "stars · 4/5", "wide"))
    b.append(f'<figure><div class="row">{K.icon("bell", key, 44)}'
             f'<div class="rel">{K.icon("cart", key, 44)}'
             f'<div class="bdg2">{K.badge(34, key, "3")}</div></div></div>'
             f'<figcaption>icon + badge</figcaption></figure>')
    bars = f'<div class="band"><h3>Bars, progress &amp; status</h3>' \
           f'<div class="grid">{"".join(b)}</div></div>'

    # ---------------- loot & decor ----------------
    d = []
    d.append(_fig(K.slot(96, key), "slot · empty"))
    d.append(_fig(K.slot(96, key, icon_name="sword", rarity="rare"),
                  "slot · rare"))
    d.append(_fig(K.slot(96, key, icon_name="gem", rarity="legendary"),
                  "slot · legendary"))
    d.append(_fig(K.slot(96, key, icon_name="potion", rarity="epic"),
                  "slot · epic"))
    d.append(_fig(K.item_card(360, 128, key), "item card", "wide"))
    d.append(_fig(K.ribbon(340, 78, key, label=m["ribbon"]), "ribbon", "wide"))
    d.append(_fig(K.divider(380, key), "divider", "wide"))
    decor = f'<div class="band"><h3>Loot slots, item cards &amp; decoration</h3>' \
            f'<div class="grid">{"".join(d)}</div></div>'

    # ---------------- icons ----------------
    igs = "".join(_fig(K.icon(n, key, 54), n, "tight") for n in K.ICON_NAMES)
    icons = f'<div class="band"><h3>Icon library · {len(K.ICON_NAMES)} icons</h3>' \
            f'<div class="icons">{igs}</div></div>'

    # ---------------- HUD mockup ----------------
    quest_rows = []
    for text, done in m["quest"]:
        mark = K.icon("check" if done else "question", key, 26,
                      color=(t["good"] if done else t["muted"]))
        state = "done" if done else ""
        quest_rows.append(
            f'<div class="qrow {state}">{mark}'
            f'<span><b>{text}</b><i>{"Completed" if done else "In progress"}</i></span>'
            f'</div>')
    slots = "".join(
        f'<div class="act">{K.slot(70, key, icon_name=ic)}'
        + (f'<div class="bdg">{K.badge(28, key, "2")}</div>' if ic == "bag" else "")
        + '</div>' for ic in m["icons"])
    chips = (f'<div class="chiprow">{K.chip(150, 42, key, "12,450", "gold")}'
             f'{K.chip(130, 42, key, "386", "gem")}</div>')
    menu_icons = "".join(
        f'<div class="act sm">{K.slot(56, key, icon_name=ic)}</div>'
        for ic in ("gear", "search", "user"))
    hud = f'''
<div class="mock" data-mock="{key}">
  {chips}
  <div class="menurow">{menu_icons}</div>
  <div class="lvwrap"><div class="lv">{m["lv"]}</div>
    {K.bar(340, 30, key, "hp", 0.72)}
    {K.bar(340, 30, key, "mana", 0.46)}
    {K.bar(340, 30, key, "stamina", 0.88)}
  </div>
  <div class="ribwrap">{K.ribbon(380, 74, key, label=m["ribbon"])}</div>
  <div class="quest">{K.panel(400, 300, key, label="QUESTS")}
    <div class="qbody">{"".join(quest_rows)}</div>
  </div>
  <div class="bubblewrap">{K.bubble(300, 64, key, m["chat"], "left")}</div>
  <div class="tipwrap">{K.tooltip(300, 56, key, m["tip"])}</div>
  <div class="actionbar">{slots}</div>
  <div class="ctarow">{K.button(300, 58, key, "normal", "primary", label=m["cta"])}
    {K.button(180, 58, key, "normal", "ghost", label="MENU")}</div>
  <div class="stats">{K.ring(110, key, 0.62, label="62%", kind="xp")}
    {K.stars(230, 36, key, 3, 5)}</div>
</div>'''
    screen = (f'<div class="band"><h3>In-context HUD mockup · real assembly</h3>'
              f'{hud}</div>')

    return f'''
<section data-theme="{key}" style="background:{t['bg']};color:{t['ink']}">
  <h2>{t["label"]} <small>{key}</small></h2>
  {buttons}{form}{windows}{bars}{decor}{icons}{screen}
</section>'''


HTML = """<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{font:14px/1.4 system-ui,sans-serif;background:#0a0a0f}
section{padding:40px 46px;border-bottom:4px solid #000}
h2{font-size:24px;letter-spacing:.5px;margin-bottom:26px;text-transform:uppercase}
h2 small{opacity:.45;font-weight:400;text-transform:none;font-size:16px}
.band{margin-bottom:38px}
.band h3{font-size:13px;letter-spacing:2.5px;text-transform:uppercase;
  opacity:.55;margin-bottom:16px;font-weight:700}
.grid{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}
figure{display:flex;flex-direction:column;gap:7px;align-items:center;width:262px}
figure.wide{width:470px}
figure.tight{width:78px;gap:5px}
figcaption{font-size:11px;opacity:.55;letter-spacing:.6px;text-align:center}
.row{display:flex;gap:10px;align-items:center}
.icons{display:flex;flex-wrap:wrap;gap:18px}
.rel{position:relative;display:inline-block}
.bdg2{position:absolute;top:-8px;right:-10px}
.mock{position:relative;width:1400px;height:640px;overflow:hidden;
  border:2px solid rgba(128,128,128,.35);border-radius:6px;
  background:radial-gradient(120% 90% at 50% 0%,rgba(255,255,255,.05),transparent 60%),
    linear-gradient(180deg,rgba(0,0,0,.25),rgba(0,0,0,.5));}
.mock [data-theme]{all:initial}
.chiprow{position:absolute;left:24px;top:20px;display:flex;gap:12px}
.menurow{position:absolute;right:24px;top:18px;display:flex;gap:12px}
.act{position:relative;display:inline-block}
.bdg{position:absolute;top:-6px;right:-8px}
.lvwrap{position:absolute;left:24px;top:96px;display:flex;flex-direction:column;
  gap:14px;align-items:flex-start}
.lv{font:700 13px system-ui;letter-spacing:3px;padding:5px 14px;border-radius:3px;
  background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.25);margin-bottom:4px}
[data-mock="royal"]{background:
    radial-gradient(120% 90% at 50% 0%,rgba(31,58,110,.10),transparent 60%),
    linear-gradient(180deg,#F7F3EA,#EAE3D2);border-color:#C9C0A8}
[data-mock="royal"] .lv{background:rgba(31,58,110,.85)}
[data-mock="royal"] .actionbar{background:rgba(255,255,255,.65);
    border-color:rgba(31,58,110,.35)}
.ribwrap{position:absolute;left:50%;top:22px;transform:translateX(-50%)}
.quest{position:absolute;right:24px;top:96px;width:400px}
.qbody{position:absolute;top:66px;left:8px;right:8px;
  display:flex;flex-direction:column;gap:12px}
.qrow{display:flex;gap:12px;align-items:center;padding:8px 10px;border-radius:4px;
  background:rgba(128,128,128,.12)}
.qrow b{display:block;font-size:14px;font-weight:700}
.qrow i{display:block;font-size:11px;font-style:normal;opacity:.55;margin-top:2px}
.qrow.done b{opacity:.55;text-decoration:line-through}
.bubblewrap{position:absolute;left:24px;bottom:210px}
.tipwrap{position:absolute;left:430px;top:300px}
.actionbar{position:absolute;left:50%;bottom:96px;transform:translateX(-50%);
  display:flex;gap:12px;padding:12px 16px;border-radius:6px;
  background:rgba(0,0,0,.35);border:1px solid rgba(128,128,128,.3)}
.ctarow{position:absolute;left:50%;bottom:22px;transform:translateX(-50%);
  display:flex;gap:16px;align-items:center}
.stats{position:absolute;left:24px;bottom:22px;display:flex;gap:16px;
  align-items:center}
</style>
""" + "".join(section(k) for k in THEMES)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "review.html")
    with open(path, "w") as f:
        f.write(HTML)
    print("wrote", path)
