#!/usr/bin/env python3
"""Build dist/kit/index.html — dependency-free offline gallery.

Browse every theme: screens (4K thumbs), component groups, and the full
icon set. Plain HTML/CSS/JS with relative paths so it works from a zip
extract, GitHub Pages, or double-click locally.

Usage: python3 tools/make_gallery.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "dist", "kit")
SVG = os.path.join(KIT, "svg")
SCREENS = os.path.join(KIT, "screens")
OUT = os.path.join(KIT, "index.html")

GROUP_TITLES = {
    "buttons": "Buttons (9 shapes × 4 states × 4 kinds)",
    "iconbuttons": "Icon buttons", "bars": "Status bars", "rings": "Rings",
    "slots": "Slots & rarities", "panels": "Panels", "windows": "Windows",
    "forms": "Form widgets", "decor": "Decor & chips", "cards": "Cards",
    "leaderboard": "Leaderboard", "icons": "Icons (24px grid)",
    "hud": "HUD widgets", "touch": "Touch controls",
    "overlays": "Meta overlays",
}


def rel(*p):
    return "/".join(p)


def main():
    man = json.load(open(os.path.join(KIT, "manifest.json")))
    themes = list(man["themes"].keys())
    total = man["total"]

    parts = ["""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MegaUI — Game UI Design System</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0e0c09;color:#ece2cc;font:15px/1.5 Verdana,'DejaVu Sans',sans-serif}
header{padding:34px 40px 10px;background:
 linear-gradient(180deg,rgba(212,169,78,.14),transparent)}
h1{font-size:34px;letter-spacing:5px;color:#e9c26a}
.sub{opacity:.6;letter-spacing:2px;font-size:12px;margin-top:6px;text-transform:uppercase}
nav{display:flex;gap:8px;padding:18px 40px;position:sticky;top:0;background:#0e0c09e6;
 backdrop-filter:blur(6px);z-index:9;border-bottom:1px solid #2a2317;flex-wrap:wrap}
nav button{background:#1b1611;color:#d8cbaa;border:1px solid #3a3020;padding:9px 22px;
 border-radius:999px;cursor:pointer;letter-spacing:1.5px;font-size:13px}
nav button.on{background:#d4a94e;color:#14100c;border-color:#d4a94e;font-weight:700}
nav .count{margin-left:auto;opacity:.45;align-self:center;font-size:12px}
section{display:none;padding:26px 40px 60px}
section.on{display:block}
h2{font-size:15px;letter-spacing:3px;color:#e9c26a;margin:34px 0 14px;text-transform:uppercase}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.card{background:#171310;border:1px solid #2c2418;border-radius:10px;padding:10px;
 transition:border-color .15s}
.card:hover{border-color:#d4a94e}
.card img{width:100%;display:block;border-radius:6px;background:
 repeating-conic-gradient(#15120e 0 25%,#1a1612 0 50%) 0 0/16px 16px}
.card .cap{font-size:11px;opacity:.65;margin-top:8px;word-break:break-all;text-align:center}
.screens{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.screens .card img{aspect-ratio:16/9;object-fit:cover}
a{color:#e9c26a}
.note{opacity:.55;font-size:12px;margin-top:6px}
</style></head><body>
<header>
<h1>MEGAUI</h1>
<div class="sub">Game UI Design System · __TOTAL__ files · 4 themes · offline gallery</div>
</header>
<nav id="nav">
""".replace("__TOTAL__", str(total))]

    for i, th in enumerate(themes):
        cls = " class='on'" if i == 0 else ""
        parts.append(f"<button data-th='{th}'{cls}>{th}</button>")
    parts.append(f"<span class='count'>svg → png4k mirror · 4× resolution</span>")
    parts.append("</nav>")

    for th in themes:
        cls = " class='on'" if th == themes[0] else ""
        parts.append(f"<section id='s-{th}'{cls}>")

        # screens
        sdir = os.path.join(SCREENS, th)
        shots = sorted(f for f in os.listdir(sdir) if f.endswith(".png"))
        parts.append("<h2>Screens — 4K (3840×2160)</h2><div class='screens'>")
        for f in shots:
            name = f[:-4]
            parts.append(
                f"<a class='card' href='{rel('screens', th, f)}' target='_blank'>"
                f"<img loading='lazy' src='{rel('screens', th, f)}' alt='{name}'>"
                f"<div class='cap'>{name}</div></a>")
        parts.append("</div>")

        # component groups
        groups = sorted(os.listdir(os.path.join(SVG, th)))
        parts.append("<h2>Components</h2><div class='grid'>")
        for g in groups:
            gdir = os.path.join(SVG, th, g)
            files = sorted(os.listdir(gdir))
            cap = GROUP_TITLES.get(g, g)
            if g == "icons":
                # dedicated icon section below; show only 24 samples here
                files = files[:24]
            elif len(files) > 16:
                step = len(files) // 16 or 1
                files = files[::step][:16]
            for f in files:
                if not f.endswith(".svg"):
                    continue
                label = f[:-4]
                parts.append(
                    f"<div class='card'><img loading='lazy' "
                    f"src='{rel('svg', th, g, f)}'>"
                    f"<div class='cap'>{label}</div></div>")
        parts.append("</div>")
        parts.append("<div class='note'>Sampled grid — every file lives in "
                     f"<code>/svg/{th}/&lt;group&gt;/</code> "
                     "with a mirrored <code>/png4k/</code> export.</div>")

        # full icons
        icons = sorted(f for f in os.listdir(os.path.join(SVG, th, "icons"))
                       if f.endswith(".svg"))
        parts.append(f"<h2>Icons — {len(icons)} per theme</h2><div class='grid'>")
        for f in icons:
            parts.append(
                f"<div class='card'><img loading='lazy' style='padding:14px' "
                f"src='{rel('svg', th, 'icons', f)}'>"
                f"<div class='cap'>{f[:-4]}</div></div>")
        parts.append("</div>")
        parts.append("</section>")

    parts.append("""
<script>
const nav=document.getElementById('nav');
nav.addEventListener('click',e=>{
 const b=e.target.closest('button'); if(!b)return;
 nav.querySelectorAll('button').forEach(x=>x.classList.remove('on'));
 b.classList.add('on');
 document.querySelectorAll('section').forEach(s=>s.classList.remove('on'));
 document.getElementById('s-'+b.dataset.th).classList.add('on');
});
</script>
</body></html>""")
    with open(OUT, "w") as f:
        f.write("".join(parts))
    print(f"gallery -> {OUT}  ({os.path.getsize(OUT)//1024} KB)")


if __name__ == "__main__":
    main()
