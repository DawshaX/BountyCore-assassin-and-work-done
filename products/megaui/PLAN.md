# MegaUI — Game UI Design System (products/megaui)

Approved direction: build THE most complete, premium, sellable UI system on Fab.
User delegated final design/product decisions to me; every phase still gets
sample review + user sign-off before mass production (PLAN.md §5 rule).

## Decisions (made 2026-10-01, approved by direction "اعمل اللي انت شايفه صح")

- **Name/title:** `MegaUI - Game UI Design System` (30 chars, brand + keyword)
- **Price tiers (dual):** Personal **$49.99** (volume) / Professional **$199.99**
  (4x studio margin — Fab presets allow any split; both tiers mandatory)
- **Themes (4):** Dark Fantasy · Sci-Fi Neon · Clean Royal · Pixel Retro
- **Sources:** original parametric **SVG** (never Image Trace) + PNG 4K exports
  + layered HTML/CSS screen mocks; fonts = OFL only, bundled with licenses
- **Engine gate:** primary format = **Unity package** (UI Toolkit UXML/USS +
  sprites + fonts + Editor utilities) — Additional files: SVG/PNG/docs zip
  (lessons from PixelForge's promotion error)
- **AI policy:** `Created With AI = YES` (mandatory, honest) + `NoAI` tag on
  Standard license; differentiation = completeness, consistency, docs,
  working engine package — not AI volume
- **Category:** UI → UI Kits / HUDs; Unity path (Asset Store guidelines;
  UE widget-blueprint minimums deferred)

## Scope targets ("اكمل 100% وكل اللي يحتاجه المشتري")

| Family | Target |
|---|---|
| Full screens (1920x1080) | 12 per theme = 48 |
| Buttons (9 shapes x 4 states) | 36 per theme = 144 |
| Bars (hp/mana/xp/stamina/dots…) | 10 per theme = 40 |
| Icons (24px grid, consistent) | 200+ base, tinted per theme |
| Panels/frames/slots/ribbons/tabs/toggles | 60+ per theme |
| Sources | every element as SVG + 4K PNG (9-slice ready) |
| Fonts | OFL bundles + LICENSE files |
| Extras | CSS/JSON design tokens, recolor guide, Unity package, docs |

## Phases (checkpoint = user sign-off)

0. ✅ direction approved (this file)
1. ✅ Core generator + first samples — **user approved samples (v1 ZIP)**
2. Mass production [IN PROGRESS]:
   - ✅ 9 button shapes × 4 states × 4 kinds × 4 themes
   - ✅ full kit tree: **1,784 SVGs** (manifest.json) + **1,784 PNG @4x**
   - ✅ new families: portrait, skillcard+cooldown, toast, scrollbar, radio, leaderboard
   - ✅ tokens (JSON+CSS) + retheme.py + RECLOUR.md (designer-editable)
   - ✅ 48 screens (12 layouts × 4 themes) rendered **4K 3840×2160**
   - ⬜ icons 51 → 200+ base (batch 2 next)
   - ⬜ sample sheets update + user review
3. (merged into 2) screens -> review together
4. Unity package (gate) + fonts + docs -> review
5. Listing kit (answers/media/test-report like PixelForge) -> submit by user
6. Post-live: tags/price fast edits, 14-day review
