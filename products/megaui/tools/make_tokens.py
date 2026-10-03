"""Emit design tokens (JSON + CSS) from tokens.py — single source of truth."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import THEMES, GEO, STATES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "kit", "tokens")
os.makedirs(OUT, exist_ok=True)

COLOR_KEYS = ["bg", "panel", "panel2", "ink", "muted", "accent", "accent2",
              "stroke", "danger", "good", "mana"]

doc = {
    "$schema": "https://design-tokens.github.io/community-group/format/",
    "name": "MegaUI - Game UI Design System",
    "version": "1.0.0",
    "themes": {},
    "geometry": GEO,
    "states": STATES,
    "typography": {
        "ui": "Verdana, 'DejaVu Sans', sans-serif",
        "mono": "'Courier New', 'DejaVu Sans Mono', monospace",
        "letterSpacing": {"fantasy": 2.4, "sci": 3.2, "royal": 1.6, "pixel": 2.0},
    },
}
css = ["/* MegaUI design tokens — drop-in CSS custom properties */",
       ":root{"]
for key, t in THEMES.items():
    doc["themes"][key] = {"label": t["label"], "style": t["style"],
                          "colors": {c: t[c] for c in COLOR_KEYS}}
    css.append(f"  /* {t['label']} */")
    for c in COLOR_KEYS:
        css.append(f"  --mega-{key}-{c}: {t[c]};")
    css.append(f"  --mega-{key}-radius: {GEO[t['style']]['r']}px;")
    css.append(f"  --mega-{key}-stroke: {GEO[t['style']]['stroke']}px;")
css.append("}")

# ready-to-use component classes
css.append("""
/* quick component classes (theme = darkfantasy by default) */
.mega-btn{padding:14px 34px;border:var(--mega-darkfantasy-stroke) solid var(--mega-darkfantasy-accent);
  background:var(--mega-darkfantasy-accent);color:var(--mega-darkfantasy-bg);
  border-radius:var(--mega-darkfantasy-radius);font-weight:700;letter-spacing:2.4px;cursor:pointer}
.mega-btn--ghost{background:transparent;color:var(--mega-darkfantasy-ink)}
.mega-panel{background:var(--mega-darkfantasy-panel);border:var(--mega-darkfantasy-stroke) solid var(--mega-darkfantasy-stroke);
  border-radius:var(--mega-darkfantasy-radius);color:var(--mega-darkfantasy-ink)}
.mega-chip{display:inline-flex;gap:8px;align-items:center;padding:8px 18px;border-radius:999px;
  background:var(--mega-darkfantasy-panel);border:2px solid var(--mega-darkfantasy-accent2);
  color:var(--mega-darkfantasy-ink);font-weight:700}
""")
css.append("}")

with open(os.path.join(OUT, "design-tokens.json"), "w") as f:
    json.dump(doc, f, indent=2)
with open(os.path.join(OUT, "megaui.css"), "w") as f:
    f.write("\n".join(css) + "\n")
print("tokens ->", OUT)
