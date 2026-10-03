# MegaUI — Game UI Design System

**The complete, fully editable game UI kit: 4 themes, 2,672 vector
components, 244 icons, 84 screens in 4K — every file original parametric
artwork.**

## What's in this package

| Folder | Contents |
|---|---|
| `svg/<theme>/<group>/` | **2,672 master SVGs** — buttons (9 shapes × 4 states × 4 kinds), bars, rings, slots, panels, windows, forms, decor, cards, leaderboard, HUD widgets (minimap / compass / currency), **touch controls (joystick, ABXY, crosshairs)**, **meta overlays (nameplate, killfeed, prompts, radial wheel, party frames, ammo, subtitles)**, icons |
| `png4k/<theme>/<group>/` | The same **2,672 PNGs at 4× resolution**, transparent, ready for any engine |
| `screens/<theme>/` | **84 full screens** (Menu, HUD, Inventory, Shop, Settings, Pause, Dialog, Map, Quests, Character, Results, Login, Loading, Character Select, Skill Tree, Defeat, Confirm, **Achievements, Crafting, Chat, Mobile HUD**) as HTML source + **4K PNG (3840×2160)** |
| `tokens/` | `design-tokens.json` + `megaui.css` — every color in one place |
| `fonts/` | Inter + Montserrat TTF with **OFL-1.1** licenses |
| `docs/RECLOUR.md` | One-command recolor guide for designers |
| `manifest.json` | Machine-readable inventory of every component |
| `index.html` | **Offline interactive gallery** — browse themes, screens, components, all icons (double-click to open) |
| `MegaUI-Unity-v1.0.0.unitypackage` *(one level up in `dist/`)* | Full Unity import: 2,672 sprites + UI Toolkit USS/UXML + runtime C# (popup animation, button juice, bar driver, one-click theme switcher) + editor helper |

## Themes

1. **Dark Fantasy** — gold on obsidian, filigree corners
2. **Sci-Fi Neon** — chamfered neon HUD, scanlines, brackets
3. **Clean Royal** — light/navy premium mobile look
4. **Pixel Retro** — 8-bit hard shadows, stair-stepped cuts, banded gloss

## For developers
- Import PNG 4× sprites directly (pixels-per-unit: 100 recommended).
- Unity users: import the `.unitypackage` — sprites arrive as **Sprite**
  (single mode, 16px borders = 9-slice ready), plus:
  - `MegaUI/Runtime/MegaUIThemeSwitcher.cs` — recolor a whole screen with
    one click (palettes = design-tokens.json)
  - `MegaUI/Runtime/MegaUIPopup.cs` — scale/fade modal animation
  - `MegaUI/Runtime/MegaUIButtonFx.cs` — press/hover button juice
  - `MegaUI/Runtime/MegaUIBar.cs` — smooth status bars + segmented mode
  - `MegaUI/UI/*.uxml` — MainMenu / HUD / Inventory / Settings / Sample
  - `MegaUI/UI/MegaUI.uss` — tokens + widget classes + 4 theme classes
- Web/HTML5: use `tokens/megaui.css` or drop SVGs straight into the DOM.

## For designers (full editability)
- Every component is a **parametric SVG** (plain text, version-controllable).
- Change colors with `tools/retheme.py` — recolor a whole theme in one
  command, no vector editor needed (see `docs/RECLOUR.md`).
- Or edit `tools/tokens.py` and regenerate the entire kit from source.

## Quality guarantees
- Original artwork only — no traced/stock/AI-borrowed geometry.
- Valid XML across all SVGs, verified by the automated test suite
  (`tools/verify_kit.py`, 34/34 checks).
- Consistent 24px icon grid, shared stroke weights, one type scale.
