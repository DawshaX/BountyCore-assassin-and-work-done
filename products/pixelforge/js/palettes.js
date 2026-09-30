/* PixelForge — palettes, quantization, dithering, pixelation */
(function () {
  "use strict";

  const hex = (s) => [
    parseInt(s.slice(0, 2), 16),
    parseInt(s.slice(2, 4), 16),
    parseInt(s.slice(4, 6), 16),
  ];

  const PALETTES = {
    none: null,
    gray16: Array.from({ length: 16 }, (_, i) => {
      const v = Math.round((i / 15) * 255);
      return [v, v, v];
    }),
    gb: ["9bbc0f", "8bac0f", "306230", "0f380f"].map(hex),
    pico8: [
      "000000", "1d2b53", "7e2553", "008751", "ab5236", "5f574f", "c2c3c7", "fff1e8",
      "ff004d", "ffa300", "ffec27", "00e436", "29adff", "83769c", "ff77a8", "ffccaa",
    ].map(hex),
    sweetie16: [
      "1a1c2c", "5d275d", "b13e53", "ef7d57", "ffcd75", "a7f070", "38b764", "257179",
      "29366f", "3b5dc9", "41a6f6", "73eff7", "f4f4f4", "94b0c2", "566c86", "333c57",
    ].map(hex),
    db16: [
      "140c1c", "442434", "30346d", "4e4a4e", "854c30", "346524", "d04648", "757161",
      "597dce", "d27d2c", "8595a1", "6daa2c", "d2aa99", "6dc2ca", "dad45e", "deeed6",
    ].map(hex),
    db32: [
      "000000", "222034", "45283c", "66365d", "8b5685", "a76b69", "a9a1a1", "727b81",
      "5a7585", "5f6d7a", "6d8189", "7d8b7a", "687848", "4e6342", "32432c", "4f6b47",
      "71906d", "98a96c", "a5ad7e", "c1cf9b", "d5d89d", "d5d89d" /* placeholder replaced below */
    ].map(hex),
    nes: [
      "7c7c7c", "0000fc", "0000bc", "4428bc", "940084", "a80020", "a81000", "881400",
      "503000", "007800", "006800", "005800", "004058", "000000", "000000", "000000",
      "bcbcbc", "0078f8", "0058f8", "6844fc", "d800cc", "e40058", "f83800", "e45c10",
      "ac7c00", "00b800", "00a800", "00a844", "008888", "000000", "000000", "000000",
      "f8f8f8", "3cbcfc", "6888fc", "9878f8", "f878f8", "f85898", "f87858", "fca044",
      "f8b800", "b8f818", "58d854", "58f898", "00e8d8", "787878", "000000", "000000",
      "fcfcfc", "a4e4fc", "b8b8f8", "d8b8f8", "f8b8f8", "f8a4c0", "f0d0b0", "fce0a8",
      "f8d878", "d8f878", "b8f8b8", "b8f8d8", "00fcfc", "f8d8f8", "000000", "000000",
    ].map(hex),
    c64: [
      "000000", "ffffff", "880000", "aaee77", "dd4488", "00cc55", "0000aa", "eedd66",
      "dd8844", "664400", "aa5555", "333333", "777777", "aaff66", "0088ff", "bbbbbb",
    ].map(hex),
    cga: [
      "000000", "55ffff", "ff55ff", "ffffff", // mode 4 palette 1 high
    ].map(hex),
  };

  // fix db32 duplicate placeholder: real DB32 tail
  PALETTES.db32 = [
    "000000", "222034", "45283c", "66365d", "8b5685", "a76b69", "a9a1a1", "727b81",
    "5a7585", "5f6d7a", "6d8189", "7d8b7a", "687848", "4e6342", "32432c", "4f6b47",
    "71906d", "98a96c", "a5ad7e", "c1cf9b", "d5d89d", "b8b8d8", "6d59b4", "b53120",
    "73174d", "3b004f", "000000", "1b0326", "3a0440", "5b0045", "75003d", "8c002d",
  ].map(hex);

  const BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
  ];

  function nearest(pal, r, g, b) {
    let best = 0;
    let bestD = Infinity;
    for (let i = 0; i < pal.length; i++) {
      const p = pal[i];
      const dr = r - p[0], dg = g - p[1], db = b - p[2];
      // weighted RGB distance (perceptual-ish)
      const rm = (r + p[0]) / 2;
      const d = (2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db;
      if (d < bestD) { bestD = d; best = i; }
    }
    return pal[best];
  }

  /**
   * Quantize + dither an ImageData in place.
   * @param {ImageData} img
   * @param {number[][]} pal array of [r,g,b]
   * @param {string} dither 'none' | 'bayer' | 'floyd'
   */
  function quantize(img, pal, dither) {
    const { data, width: w, height: h } = img;

    if (dither === "floyd") {
      // work on float buffer for error diffusion
    const buf = new Float32Array(w * h * 3);
      for (let i = 0, j = 0; i < data.length; i += 4, j += 3) {
        buf[j] = data[i]; buf[j + 1] = data[i + 1]; buf[j + 2] = data[i + 2];
      }
      const idx = (x, y) => (y * w + x) * 3;
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const ai = (y * w + x) * 4;
          if (data[ai + 3] < 8) continue; // leave transparent pixels alone
          const i3 = idx(x, y);
          const r = buf[i3], g = buf[i3 + 1], b = buf[i3 + 2];
          const c = nearest(pal, r, g, b);
          const er = r - c[0], eg = g - c[1], eb = b - c[2];
          data[ai] = c[0]; data[ai + 1] = c[1]; data[ai + 2] = c[2];
          // distribute error: 7/16 right, 3/16 down-left, 5/16 down, 1/16 down-right
          const spread = (nx, ny, f) => {
            if (nx < 0 || nx >= w || ny < 0 || ny >= h) return;
            const ni = idx(nx, ny);
            buf[ni] += er * f; buf[ni + 1] += eg * f; buf[ni + 2] += eb * f;
          };
          spread(x + 1, y, 7 / 16);
          spread(x - 1, y + 1, 3 / 16);
          spread(x, y + 1, 5 / 16);
          spread(x + 1, y + 1, 1 / 16);
        }
      }
      return;
    }

    const useBayer = dither === "bayer";
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        if (data[i + 3] < 8) continue;
        let r = data[i], g = data[i + 1], b = data[i + 2];
        if (useBayer) {
          const t = (BAYER4[y & 3][x & 3] / 16 - 0.47) * 56;
          r = Math.max(0, Math.min(255, r + t));
          g = Math.max(0, Math.min(255, g + t));
          b = Math.max(0, Math.min(255, b + t));
        }
        const c = nearest(pal, r, g, b);
        data[i] = c[0]; data[i + 1] = c[1]; data[i + 2] = c[2];
      }
    }
  }

  /**
   * Pixelate: downscale by `scale` (box average) then upscale nearest.
   * Returns a new canvas.
   */
  function pixelate(srcCanvas, scale) {
    const w = srcCanvas.width, h = srcCanvas.height;
    if (scale <= 1) return srcCanvas;
    const sw = Math.max(1, Math.round(w / scale));
    const sh = Math.max(1, Math.round(h / scale));

    const small = document.createElement("canvas");
    small.width = sw; small.height = sh;
    const sctx = small.getContext("2d", { willReadFrequently: true });
    sctx.imageSmoothingEnabled = true;
    sctx.imageSmoothingQuality = "high";
    // draw full image into small canvas (box filter via browser downscale)
    sctx.drawImage(srcCanvas, 0, 0, sw, sh);

    const out = document.createElement("canvas");
    out.width = sw; out.height = sh; // keep logical (small) size; upscale happens at pack time
    const octx = out.getContext("2d", { willReadFrequently: true });
    octx.imageSmoothingEnabled = false;
    octx.drawImage(small, 0, 0);
    return out;
  }

  /* ---------------- auto palette (median cut) ---------------- */

  /**
   * Build an N-color palette from a set of ImageData-like objects
   * using the median-cut algorithm. Opaque pixels only (alpha > 128).
   * Subsamples large inputs for speed.
   */
  function autoPalette(imgs, maxColors) {
    const samples = [];
    for (const img of imgs) {
      const d = img.data;
      const stride = Math.max(1, Math.floor(d.length / 4 / 40000)) * 4; // cap ~40k/frame
      for (let i = 0; i < d.length; i += stride) {
        if (d[i + 3] > 128) samples.push([d[i], d[i + 1], d[i + 2]]);
      }
    }
    if (samples.length === 0) return PALETTES.db16.slice();
    if (samples.length <= maxColors) {
      // dedupe then return as-is
      const seen = new Set();
      const out = [];
      for (const s of samples) {
        const k = s.join(",");
        if (!seen.has(k)) { seen.add(k); out.push(s); }
      }
      while (out.length < Math.min(maxColors, 8) && out.length < samples.length) out.push([0, 0, 0]);
      return out;
    }

    let boxes = [samples];
    while (boxes.length < maxColors) {
      // pick the box with the largest channel range
      let bi = -1, bestRange = -1;
      for (let i = 0; i < boxes.length; i++) {
        const b = boxes[i];
        if (b.length < 2) continue;
        const r = boxRange(b);
        if (r.range > bestRange) { bestRange = r.range; bi = i; }
      }
      if (bi < 0 || bestRange <= 0) break;
      const box = boxes[bi];
      const { ch } = boxRange(box);
      box.sort((a, b) => a[ch] - b[ch]);
      const mid = box.length >> 1;
      boxes.splice(bi, 1, box.slice(0, mid), box.slice(mid));
    }

    return boxes
      .filter((b) => b.length)
      .map((b) => {
        let r = 0, g = 0, bl = 0;
        for (const p of b) { r += p[0]; g += p[1]; bl += p[2]; }
        return [Math.round(r / b.length), Math.round(g / b.length), Math.round(bl / b.length)];
      });
  }

  function boxRange(box) {
    let min = [255, 255, 255], max = [0, 0, 0];
    for (const p of box) {
      for (let c = 0; c < 3; c++) {
        if (p[c] < min[c]) min[c] = p[c];
        if (p[c] > max[c]) max[c] = p[c];
      }
    }
    const ranges = [max[0] - min[0], max[1] - min[1], max[2] - min[2]];
    let ch = 0;
    if (ranges[1] >= ranges[ch]) ch = 1;
    if (ranges[2] >= ranges[ch]) ch = 2;
    return { ch, range: ranges[ch] };
  }

  window.PF = window.PF || {};
  window.PF.palettes = PALETTES;
  window.PF.quantize = quantize;
  window.PF.pixelate = pixelate;
  window.PF.autoPalette = autoPalette;
})();
