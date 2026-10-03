# PixelForge for Unity

**Offline sprite sheet maker & pixel art studio — bundled with your Unity project.**

## Open the tool

Menu: **Tools → PixelForge → Open Sprite Sheet Maker**

This launches `WebApp/index.html` in your default browser. The tool is a
standalone HTML5 application:

- 100% offline — no internet, no account, no telemetry, no AI at runtime
- Works from a local file (`file://`) — no server required
- Import PNG/JPG/WEBP/GIF by drag & drop
- One-click pixel-art conversion (13 palettes incl. DawnBringer 16),
  dithering, edge extrusion, transparent trim
- Sheet layouts (shelf / horizontal / vertical / uniform grid),
  padding, output scale 1x–8x, max texture 1024–8192 with automatic
  multi-page split
- Live animation preview with FPS control, loop/ping-pong/once, pivots
- Exports: **PNG sprite sheet** (multi-page), **animated GIF**,
  **atlas JSON** (Generic / Phaser 3 / Aseprite / CSS), **frames ZIP**,
  **all-in-one ZIP**

## Getting the output into Unity

1. Export from PixelForge (PNG sheet + optional atlas JSON).
2. Drag the PNG into your `Assets` folder — it imports as a Texture2D.
3. Slice it with Unity's Sprite Editor (or use the atlas JSON rectangles
   as your slicing guide) and assign sprites to animations as usual.

## Files

- `WebApp/` — the complete PixelForge application (open `index.html`)
- `Editor/PixelForgeLauncher.cs` — the Tools/PixelForge menu
- `README.md` — this file
- `LICENSE.txt` — proprietary EULA (personal + commercial use in your
  projects; no redistribution of the source itself)
- `CHANGELOG.md`, `THIRD-PARTY.txt`

## Requirements

- Unity 2021.3 or newer (any render pipeline — the tool is editor/user
  space only, it does not modify your scenes or assets)
- A modern web browser (Chrome, Edge, Firefox, Safari)

## Support

https://github.com/DawshaX/BountyCore-assassin-and-work-done
