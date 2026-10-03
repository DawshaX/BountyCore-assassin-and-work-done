# MegaUI — Recolor & Customization Guide

MegaUI is **fully editable** without Photoshop or Figma. Every component is an
original parametric SVG, and every color comes from one token table.

## 1. Design tokens (single source of truth)

| File | Use |
|---|---|
| `tokens/design-tokens.json` | Import into Figma plugins, build scripts, engines |
| `tokens/megaui.css` | CSS custom properties, drop into any web UI |
| `tools/tokens.py` | Python source — regenerate everything after editing |

Color keys per theme: `bg panel panel2 ink muted accent accent2 stroke danger good mana`

## 2. One-command re-theme (no vector editor needed)

```bash
# Recolor the whole Dark Fantasy tree
python3 tools/retheme.py --theme darkfantasy \
  --set accent=#FF3B30 --set accent2=#FFD166 \
  --out dist/kit/svg-darkfantasy-crimson
```

* Only hex values change — geometry, states, and file names stay identical.
* Chain multiple `--set` flags; add `--also-css` to emit a matching CSS file.
* Output is a complete, ready-to-zip alternate theme.

## 3. Regenerate the kit from source

```bash
python3 tools/make_tokens.py          # tokens json + css
python3 tools/make_kit.py             # full SVG tree from the token table
python3 tools/make_screens.py         # 68 screens
node tools/render4k.js all            # PNG 4x + 4K screens
```

Edit `tools/tokens.py` (colors) or `tools/svgkit.py` (geometry rules), rerun —
the whole kit updates consistently. Nothing is traced or hand-duplicated.

## 4. Engine notes

* **SVG** = master format (edit in any vector tool, or a text editor).
* **PNG @4x** = transparent, ready for Unity/Unreal import (100 px/unit).
* **Unity**: `MegaUIThemeSwitcher` recolors assigned graphics from the same
  palette; USS classes carry `--mega-*` variables per theme class.
* Components share a 1x baseline grid — scale to any resolution without
  redesign (9-slice friendly: panels, slots, buttons all have generous
  borders).
