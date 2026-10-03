/* Headless sanity tests for PixelForge pure-logic modules */
global.window = global;
require("../js/palettes.js");
require("../js/zip.js");
const fs = require("fs");

let failed = 0;
function check(name, cond) {
  if (cond) console.log("  ok -", name);
  else { console.error("  FAIL -", name); failed++; }
}

/* ---- quantize ---- */
{
  const w = 4, h = 4;
  const data = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    data[i * 4] = 255; data[i * 4 + 1] = 40; data[i * 4 + 2] = 40; data[i * 4 + 3] = 255;
  }
  // one transparent pixel
  data[0 * 4 + 3] = 0;
  const img = { data, width: w, height: h };
  const pal = window.PF.palettes.pico8;
  window.PF.quantize(img, pal, "none");

  const isPalColor = (r, g, b) => pal.some((p) => p[0] === r && p[1] === g && p[2] === b);
  check("quantize maps to palette color", isPalColor(data[4], data[5], data[6]));
  check("quantize preserves transparency", data[3] === 0);
}

/* ---- floyd dither doesn't crash & stays in palette ---- */
{
  const w = 8, h = 8;
  const data = new Uint8ClampedArray(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    const v = (i * 7) % 256;
    data[i * 4] = v; data[i * 4 + 1] = 255 - v; data[i * 4 + 2] = 128; data[i * 4 + 3] = 255;
  }
  const img = { data, width: w, height: h };
  const pal = window.PF.palettes.db32;
  window.PF.quantize(img, pal, "floyd");
  let all = true;
  for (let i = 0; i < w * h; i++) {
    const r = data[i * 4], g = data[i * 4 + 1], b = data[i * 4 + 2];
    if (!pal.some((p) => p[0] === r && p[1] === g && p[2] === b)) all = false;
  }
  check("floyd output stays in palette", all);
}

/* ---- bayer dither doesn't crash ---- */
{
  const w = 8, h = 8;
  const data = new Uint8ClampedArray(w * h * 4).fill(200);
  for (let i = 3; i < data.length; i += 4) data[i] = 255;
  const img = { data, width: w, height: h };
  window.PF.quantize(img, window.PF.palettes.gb, "bayer");
  check("bayer runs", data[0] !== undefined);
}

/* ---- auto palette (median cut) ---- */
{
  const mk = (n, r, g, b) => {
    const d = new Uint8ClampedArray(n * 4);
    for (let i = 0; i < n; i++) {
      d[i * 4] = (r + i * 3) % 256;
      d[i * 4 + 1] = (g + i * 5) % 256;
      d[i * 4 + 2] = (b + i * 7) % 256;
      d[i * 4 + 3] = i % 10 === 0 ? 0 : 255; // some transparent
    }
    return { data: d, width: n, height: 1 };
  };
  const pal = window.PF.autoPalette([mk(500, 10, 60, 120), mk(500, 200, 30, 90)], 8);
  check("autoPalette returns <= 8 colors", pal.length >= 2 && pal.length <= 8, pal.length);
  check("autoPalette entries valid RGB",
    pal.every((c) => c.length === 3 && c.every((v) => Number.isInteger(v) && v >= 0 && v <= 255)));

  // large input path (forces median cut splitting)
  const big = mk(60000, 0, 0, 0);
  const pal2 = window.PF.autoPalette([big], 16);
  check("autoPalette handles large input", pal2.length >= 2 && pal2.length <= 16, pal2.length);
}

/* ---- zip ---- */
{
  const enc = new TextEncoder();
  const entries = [
    { name: "hello.txt", data: enc.encode("Hello PixelForge!\n") },
    { name: "dir/data.bin", data: new Uint8Array([0, 1, 2, 250, 251, 252]) },
    { name: "unicode-إسم.txt", data: enc.encode("unicode name test") },
  ];
  const blob = window.PF.makeZip(entries);
  blob.arrayBuffer().then((buf) => {
    fs.writeFileSync("/tmp/pf_test.zip", Buffer.from(buf));
    console.log("  zip written:", buf.byteLength, "bytes");
    process.exit(failed ? 1 : 0);
  });
}
