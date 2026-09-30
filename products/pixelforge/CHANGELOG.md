# Changelog

## 1.1.2 — 2026-09-30

### Added
- Defensive guards: empty GIF palette (fully-transparent edge case),
  empty batch-rename pattern ignored with toast.

## 1.1.1 — 2026-09-30

### Fixed
- **CRITICAL: UI blocked by always-visible overlays** — author CSS rules
  (`.modal{display:grid}`, `#stage-empty{display:grid}`, `.page-nav{display:flex}`)
  were beating the browser's `[hidden]{display:none}`, so the help dialog and
  the empty-state layer covered the whole app. Added a global
  `[hidden]{display:none !important}` guard. (Found via real-Chromium E2E;
  attribute-only tests could not catch it.)
- **Platform-dependent glyphs** — replaced `⤓ ⏸ 📁 ↶ ↷ ＋` with universally
  supported symbols/text (`↓`, `II`, `FOLDER`, `UNDO`, `REDO`, `+`) so no
  buyer sees tofu boxes □ in the UI or in store screenshots.

### Verified
- Full end-to-end run in real Chromium (HTTP + offline `file://`):
  import, pixelate, undo, pivot, multi-page, PNG/JSON/GIF exports,
  GIF import with delays — **zero console errors**.

## 1.1.0 — 2026-09-30

### Added
- **Animated GIF import** — drop a GIF, get every frame (with original delays, disposal handled)
- **Animated GIF export** — one-click `.gif` of your animation (respects FPS + once/loop mode), also included in the ZIP
- **Folder import** — import an entire folder of images at once
- **Pivot points** — click the preview to set each sprite's rotation pivot; exported to Generic/Phaser JSON
- **Multi-page sheets** — sheets that exceed the max texture size are split into multiple pages (page nav in Sheet View; per-page PNGs + `textureIndex` in atlas)
- **Auto palette** — median-cut palette extracted from your own art (8/16/32 colors)
- **Undo / Redo** — buttons + Ctrl+Z / Ctrl+Y across imports, renames, reorders, parameter changes
- First-run quick help modal
- Per-frame delay display in the frame list

### Changed
- Default palette is now `Auto · image 16`
- ZIP export now includes the animated preview GIF
- CSS sprite export supports multi-page (per-frame background image)
- Help modal documents the new workflow

### Fixed
- GIF encoder pixel buffers are copied to plain `Uint8Array` before quantization (guards against cross-realm / view edge cases)

## 1.0.0 — 2026-09-30

- Initial release: import → pixelate (9 retro palettes, Bayer/Floyd dithering) → pack (grid/shelf/strips, trim, extrude, 1–8×) → preview (1–60 FPS) → export (PNG + Generic/Phaser 3/Aseprite/CSS atlas + ZIP)
- 100% offline, no dependencies, no watermarks
