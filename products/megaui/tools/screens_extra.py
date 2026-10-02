"""MegaUI screens — batch 2 (layouts 13–17): loading, character select,
skill tree, defeat, confirm modal.

Injected helpers avoid circular imports: build(COPY, SHAPES, E, wrap, K, THEMES).
"""
from tokens import THEMES  # noqa: F401  (re-exported for clarity)


def build(COPY, SHAPES_BY_THEME, E, wrap, K, THEMES):
    def screen_loading(th):
        c = COPY[th]
        body = (
            E(660, 300, '<div class="sub" style="text-align:center;width:600px">NOW LOADING</div>')
            + E(560, 350, f'<h1 style="text-align:center;width:800px;font-size:64px">{c["game"]}</h1>')
            + E(660, 500, K.divider(600, th))
            + E(560, 570, K.bar(800, 40, th, "xp", 0.72, False, label="LOADING"))
            + E(560, 628,
                '<div class="row" style="width:800px;justify-content:space-between">'
                '<div class="lbl">72%</div><div class="lbl">PREPARING THE REALM</div></div>')
            + E(560, 730,
                '<div class="card" style="width:800px">'
                '<div class="lbl" style="margin-bottom:8px">TIP</div>'
                '<div style="font-size:19px;line-height:1.5">Combine fire resistance before '
                'entering the Ember Vault — potions persist between zones.</div></div>')
            + E(1660, 1010, '<div class="lbl">v1.0</div>')
        )
        return wrap(th, body)

    def screen_charselect(th):
        c, sh = COPY[th], SHAPES_BY_THEME[th]
        heroes = [(c["hero"], "WARRIOR", "sword", True),
                  ("MoonRider", "MAGE", "wand", False),
                  ("IronVow", "GUARDIAN", "shield", False)]
        cards = ""
        accent = THEMES[th]["accent"]
        for i, (nm, cls, ic, sel) in enumerate(heroes):
            x = 330 + i * 470
            border = f"border:3px solid {accent};" if sel else ""
            btn = K.button(240, 60, th, "normal" if sel else "hover",
                           "primary" if sel else "secondary",
                           label="SELECTED" if sel else "SELECT", shape=sh)
            cards += E(x, 260, (
                f'<div class="card" style="width:400px;height:480px;text-align:center;{border}">'
                f'<div style="margin-top:10px">{K.portrait(170, th, "circle", sel)}</div>'
                f'<div style="margin-top:12px">{K.icon(ic, th, 52)}</div>'
                f'<div style="margin-top:12px;font-size:25px;font-weight:700;'
                f'letter-spacing:2px">{nm}</div>'
                f'<div class="lbl" style="margin-top:6px">{cls} · LV 42</div>'
                f'<div style="margin-top:14px">{K.chip(150, 40, th, "9.4K", "gold")}</div>'
                f'<div style="margin-top:16px">{btn}</div>'
                f'</div>'))
        body = (
            E(700, 110, '<div class="sub" style="width:520px;text-align:center">'
                        'CHOOSE YOUR CHAMPION</div>')
            + E(560, 165, '<h2 style="width:800px;text-align:center">CHARACTER SELECT</h2>')
            + cards
            + E(730, 820, K.button(460, 84, th, "normal", "primary",
                                   label="ENTER THE REALM", shape=sh))
            + E(860, 950, '<div class="lbl">3 / 8 UNLOCKS · 5 LOCKED</div>')
        )
        return wrap(th, body)

    def screen_skilltree(th):
        c, sh = COPY[th], SHAPES_BY_THEME[th]
        nodes = [
            (880, 240, "sword", "CLEAVE", True),
            (620, 420, "shield", "BLOCK", True),
            (1140, 420, "bolt", "SHOCK", True),
            (480, 640, "fire", "IGNITE", False),
            (880, 560, "star", "WARRIOR", True),
            (1280, 640, "target", "PIERCE", False),
            (680, 830, "potion", "VIGOR", False),
            (1080, 830, "wand", "ULTIMATE", False),
        ]
        lines = ""
        for (x1, y1, _, _, a), (x2, y2, _, _, b) in zip(nodes, nodes[1:]):
            col = THEMES[th]["accent2"] if (a and b) else THEMES[th]["muted"]
            lines += (f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;'
                      f'pointer-events:none"><line x1="{x1+70}" y1="{y1+70}" x2="{x2+70}" '
                      f'y2="{y2+70}" stroke="{col}" stroke-width="4" opacity="0.7"/></svg>')
        dots = ""
        for x, y, ic, nm, owned in nodes:
            ring_html = K.ring(140, th, 1.0 if owned else 0.12, "", "xp") if owned \
                else K.slot(130, th)
            dots += E(x, y, (
                f'<div style="text-align:center;width:160px">'
                f'<div style="position:relative;width:140px;height:140px;'
                f'margin:0 auto">{ring_html}'
                f'<div style="position:absolute;inset:0;display:flex;align-items:center;'
                f'justify-content:center">{K.icon(ic, th, 56)}</div></div>'
                f'<div class="lbl" style="margin-top:8px;'
                f'{"" if owned else "opacity:.35"}">{nm}</div></div>'))
        body = (
            E(120, 90, K.button(200, 64, th, "normal", "ghost", label="< BACK", shape=sh))
            + E(640, 90, '<h2>SKILL TREE</h2>')
            + E(1500, 96, f'<div class="row">{K.badge(56, th, "3")}'
                          '<div class="lbl" style="margin-left:10px">POINTS LEFT</div></div>')
            + lines + dots
            + E(1480, 300, (
                '<div class="card" style="width:330px">'
                '<div class="lbl">SKILL DETAIL</div>'
                '<div style="margin-top:10px;font-size:22px;font-weight:700">SHOCK</div>'
                '<div style="margin-top:8px;font-size:15px;line-height:1.5;opacity:.75">'
                'Chain lightning hits 3 targets for 140% weapon damage.</div>'
                '<div style="margin-top:14px">'
                + K.bar(290, 26, th, "mana", 0.6, False) + '</div>'
                '<div style="margin-top:14px">'
                + K.button(290, 60, th, "normal", "primary", label="UNLOCK · 1 PT", shape=sh)
                + '</div></div>'))
        )
        return wrap(th, body)

    def screen_defeat(th):
        sh = SHAPES_BY_THEME[th]
        danger = THEMES[th]["danger"]
        body = (
            E(660, 240, f'<h1 style="width:600px;text-align:center;color:{danger};'
                        'font-size:96px">DEFEAT</h1>')
            + E(620, 400, (
                '<div class="card" style="width:680px;text-align:center">'
                '<div class="row" style="justify-content:space-between">'
                '<div><div class="lbl">SURVIVED</div>'
                '<div style="font-size:30px;font-weight:700;margin-top:6px">12:41</div></div>'
                '<div><div class="lbl">KILLS</div>'
                '<div style="font-size:30px;font-weight:700;margin-top:6px">37</div></div>'
                '<div><div class="lbl">GOLD LOST</div>'
                f'<div style="font-size:30px;font-weight:700;margin-top:6px;'
                f'color:{THEMES[th]["accent2"]}">-320</div></div>'
                '</div></div>'))
            + E(660, 610, K.stars(280, 44, th, 2, 5))
            + E(730, 730, K.button(460, 84, th, "normal", "primary",
                                   label="RETRY CHECKPOINT", shape=sh))
            + E(770, 850, K.button(380, 72, th, "normal", "ghost",
                                   label="RETURN TO MENU", shape=sh))
        )
        return wrap(th, body, dim=True)

    def screen_confirm(th):
        c, sh = COPY[th], SHAPES_BY_THEME[th]
        body = E(560, 300, (
            '<div class="card" style="width:800px;padding:0;border:none">'
            + K.dialog(800, 430, th, "Confirm Purchase",
                       f"Buy {c['item']} for 1,250 gold?", f"BUY {c['item'].upper()}", "CANCEL")
            + '</div>'))
        body += E(640, 780, (
            '<div class="lbl" style="width:640px;text-align:center">'
            'BALANCE: 12,450 GOLD — YOU KEEP 11,200</div>'))
        return wrap(th, body, dim=True)

    return [
        ("13-loading", screen_loading),
        ("14-character-select", screen_charselect),
        ("15-skill-tree", screen_skilltree),
        ("16-defeat", screen_defeat),
        ("17-confirm", screen_confirm),
    ]
