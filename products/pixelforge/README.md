# PixelForge — Sprite Sheet Maker & Pixel Art Studio

**Turn any images into pixel art, pack them into sprite sheets, preview the animation, and export engine-ready atlas files — 100% offline, right in your browser.**

No installs. No accounts. No watermarks. No uploads — everything runs locally on your machine.

---

## Quick start

1. Open `index.html` in any modern browser (Chrome, Edge, Firefox, Safari).
2. **Drop images** anywhere on the window (PNG / JPG / WEBP / GIF first frame).
3. Tweak **Pixelate** (pixel size, retro palettes, dithering) if you want.
4. Pick a **sheet layout** and hit **play** to preview the animation.
5. Export **PNG + atlas JSON**, or grab everything as a **ZIP**.

## Features

| Area | What you get |
|---|---|
| Import | Multi-file drag & drop, **whole folder import**, **animated GIF import (every frame + delays)**, reorder frames (drag or ▲▼), batch rename, remove |
| Pixelate | 1–16 px pixel size, **Auto palette from your art (8/16/32)** + 9 built-in palettes (Game Boy, PICO-8, Sweetie-16, DB16, DB32, NES, C64, CGA, Grayscale), Bayer & Floyd–Steinberg dithering |
| Packing | Grid (uniform cells), Compact shelf (tight pack), Horizontal / Vertical strip · **multi-page split when exceeding max texture** |
| Sheet options | Trim transparent edges, padding, edge extrusion (no texture bleeding), 1024–8192 max texture, 1×/2×/4×/8× nearest-neighbour output |
| Preview | Animation player with 1–60 FPS, Loop / Ping-pong / Once modes, zoom, live sheet view with **page navigation**, **pivot point editor (click to place)** |
| Editing | **Undo / Redo everywhere (Ctrl+Z / Ctrl+Y)** |
| Export | PNG sheet(s) · Atlas JSON (**Generic**, **Phaser 3**, **Aseprite**) with **pivot points** · **CSS sprite** · individual frames · **animated GIF** · one-click **ZIP** (includes GIF) |

## Atlas formats

- **Generic JSON** — `frames: { name: { frame, trimmed, spriteSourceSize, sourceSize } }` (works with most engines & pipelines)
- **Phaser 3** — `textures[0].frames[]` format, drop straight into `this.load.atlas()`
- **Aseprite** — JSON-array format with per-frame `duration` (File → Import Sprite Sheet)
- **CSS** — ready-made classes with `background-position` for web games

## Browser support

Any browser with ES2020 + Canvas support (Chrome/Edge 90+, Firefox 90+, Safari 15+). Works offline from a local file — no server required.

## License

Free to use in personal and commercial games and projects. The tool itself is single-user and may not be redistributed or resold. See `LICENSE.txt`.

---

### For developers

Source is plain HTML/CSS/JS — no build step, no dependencies:

```
index.html      UI shell
style.css       theme
js/palettes.js  palettes + quantization + dithering + pixelate
js/zip.js       tiny store-only ZIP writer
js/core.js      state + processing + packing pipeline
js/exporters.js PNG/atlas/CSS/ZIP exporters
js/ui.js        DOM wiring + animation preview
```

Run tests: `node test/node_test.js`
