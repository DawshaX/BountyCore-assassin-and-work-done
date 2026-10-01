/* ============================================================================
 * Fab evidence shoot — real images through PixelForge, 1920x1080 screenshots,
 * exported files validated. Produces assets/fab/fab-gallery-*.png + TEST-REPORT.
 * Run:
 *   cd products/pixelforge
 *   NODE_PATH=/tmp/pffab/node_modules node test/fab_shoot.js
 * Needs: puppeteer-core + @sparticuz/chromium installed under NODE_PATH.
 * ==========================================================================*/
"use strict";
const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium").default;

const ROOT = path.join(__dirname, "..");
const FAB = path.join(ROOT, "assets", "fab");
const SHOTS = path.join(FAB, "shoot");
const DL = "/tmp/fab-dl";
const LOG = [];
const t0 = Date.now();
let failures = 0;
const log = (m) => { console.log(m); LOG.push(m); };
const ok = (m) => log(`  ok - ${m}`);
const bad = (m) => { failures++; log(`  FAIL - ${m}`); };
const assert = (c, m) => (c ? ok(m) : bad(m));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const setNative = (page, sel, value, ev) =>
  page.evaluate((s, v, e) => {
    const el = document.querySelector(s);
    if (!el) return false;
    const proto = el.tagName === "SELECT" ? HTMLSelectElement : HTMLInputElement;
    Object.getOwnPropertyDescriptor(proto.prototype, "value").set.call(el, v);
    el.dispatchEvent(new Event(e || "input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }, sel, value, ev);

const click = (page, sel) => page.evaluate((s) => {
  const el = document.querySelector(s);
  if (!el) return false;
  el.click();
  return true;
}, sel);

const clickByText = (page, selector, text) => page.evaluate((s, t) => {
  const el = [...document.querySelectorAll(s)].find(e => e.textContent.trim().includes(t));
  if (!el) return false;
  el.click();
  return true;
}, selector, text);

const shot = async (page, name) => {
  const p = path.join(SHOTS, name);
  await page.screenshot({ path: p });
  ok(`screenshot ${name}`);
  return p;
};

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  fs.rmSync(DL, { recursive: true, force: true });
  fs.mkdirSync(DL, { recursive: true });

  log("== PIXELFORGE FAB EVIDENCE SHOOT ==");
  log("date: " + new Date().toISOString());
  log("viewport: 1920x1080 (Fab min for media: 1920x1080)");

  const browser = await puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: chromium.headless,
    defaultViewport: { width: 1920, height: 1080 },
  });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
  const cdp = await page.createCDPSession();
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: DL });

  /* ---- 1. first open (file:// = offline proof) ---- */
  const app = "file://" + path.join(ROOT, "index.html");
  await page.goto(app, { waitUntil: "load", timeout: 30000 });
  await sleep(400);
  log("opened: " + app);
  assert((await page.url()).startsWith("file://"), "runs from file:// (fully offline)");
  if (!(await click(page, "#btn-help-close"))) log("  (help modal was not open)");
  await sleep(200);
  const emptyVisible = await page.evaluate(() => {
    const el = document.querySelector("#stage-empty");
    return el && !el.hasAttribute("hidden") && getComputedStyle(el).display !== "none";
  });
  assert(emptyVisible, "first-open empty state visible");
  await shot(page, "s0-empty-state.png");

  /* ---- 2. import REAL generated images (castle + cat) ---- */
  const [fi] = await page.$$("#file-input");
  assert(!!fi, "file input found");
  await fi.uploadFile(path.join(FAB, "input-castle.png"), path.join(FAB, "input-cat.png"));
  await page.waitForFunction(
    () => (document.querySelector("#frames-count") || {}).textContent?.trim() === "2",
    { timeout: 15000 }
  ).catch(() => {});
  const count = await page.evaluate(() => (document.querySelector("#frames-count") || {}).textContent);
  assert((count || "").trim() === "2", `2 real frames imported (got "${count}")`);
  const status = await page.evaluate(() => (document.querySelector("#status-msg") || {}).textContent || "");
  log("status: " + status.trim());
  await shot(page, "s1-imported-2-photos.png");

  /* ---- 3. pixelate the photos ---- */
  await click(page, "#px-on");
  await sleep(300);
  await page.evaluate(() => {
    const sel = document.querySelector("#px-palette");
    const opt = [...sel.options].find(o => /DawnBringer/i.test(o.text)) || sel.options[1];
    Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set.call(sel, opt.value);
    sel.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await sleep(700); // allow canvas repaint
  const paletteUsed = await page.evaluate(() => (document.querySelector("#px-palette") || {}).selectedOptions?.[0]?.text || "");
  assert(/DawnBringer/i.test(paletteUsed), `palette applied: ${paletteUsed}`);
  const pxOn = await page.evaluate(() => document.querySelector("#px-on").checked);
  assert(pxOn, "Convert to pixel art enabled on real photo");
  await shot(page, "s2-pixelated-dawnbringer.png");

  /* ---- 4. packing: padding + extrude, sheet view ---- */
  await setNative(page, "#sh-padding", "6");
  const extrude = await page.evaluate(() => {
    const el = document.querySelector("#sh-extrude");
    if (!el.checked) el.click();
    return el.checked;
  });
  assert(extrude, "edge extrusion enabled");
  await clickByText(page, "button, .tab, [role=tab]", "SHEET VIEW");
  await sleep(500);
  await shot(page, "s3-sheet-packed.png");
  const sheetInfo = await page.evaluate(() => (document.querySelector("#status-sheet") || {}).textContent || "");
  log("sheet: " + sheetInfo.trim());

  /* ---- 5. animation preview (play) ---- */
  await clickByText(page, "button, .tab, [role=tab]", "ANIMATION PREVIEW");
  await sleep(300);
  const playing = await page.evaluate(() => {
    const b = document.querySelector("#btn-play");
    if (b && /II/.test(b.textContent)) return true;
    if (b) { b.click(); return true; }
    return false;
  });
  await sleep(600);
  assert(playing, "animation playing with real pixelated frames");
  await shot(page, "s4-animation-preview.png");

  /* ---- 6. exports (validated later in this run) ---- */
  const seen = () => new Set(fs.readdirSync(DL));
  const grab = async (btnSel, label) => {
    const n0 = seen();
    await click(page, btnSel);
    let fresh = [];
    for (let i = 0; i < 50 && fresh.length === 0; i++) {
      await sleep(150);
      fresh = [...seen()].filter(f => !n0.has(f));
    }
    await sleep(400);
    /* Chrome may overwrite same-name downloads in place — also detect mtime bumps */
    if (fresh.length === 0) {
      const now = Date.now();
      fresh = [...seen()].filter(f => now - fs.statSync(path.join(DL, f)).mtimeMs < 4000);
    }
    if (fresh.length) { ok(`export ${label}: ${fresh.join(", ")}`); return fresh; }
    bad(`export ${label}: no file appeared`);
    return [];
  };
  const png = await grab("#btn-ex-sheet", "PNG sheet");
  const gif = await grab("#btn-ex-gif", "GIF");
  const atlas = await grab("#btn-ex-atlas", "atlas JSON");
  const zip = await grab("#btn-ex-zip", "master ZIP");

  /* ---- 7. multipage: pixelate OFF (full-res photos => big sheet) ---- */
  const pxStillOn = await page.evaluate(() => document.querySelector("#px-on").checked);
  if (pxStillOn) await click(page, "#px-on");
  await sleep(700);
  const setMaxTex = (v) => page.evaluate((val) => {
    const sel = document.querySelector("#sh-maxtex");
    Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set.call(sel, val);
    sel.dispatchEvent(new Event("change", { bubbles: true }));
  }, v);

  /* 7a. max texture smaller than a single frame => honest warning must fire */
  await setMaxTex("1024");
  await sleep(500);
  const warn = await page.evaluate(() => {
    const t = document.querySelector("#toast");
    return { hidden: !t || t.hidden, text: (t && t.textContent) || "" };
  });
  assert(!warn.hidden && /too wide/i.test(warn.text),
    `warning fires when frame exceeds texture (got: ${JSON.stringify(warn.text)})`);
  const warnSheet = await page.evaluate(() => {
    const s = PF.ensureSheet();
    return { pages: s.pagesCount, maxTex: PF.state.params.sheet.maxTex };
  });
  log("at maxTex=1024: " + JSON.stringify(warnSheet));

  /* 7b. 2048: cell fits -> lossless split, no false warning */
  await setMaxTex("2048");
  await sleep(3700); /* toast auto-hides after 3200ms */
  const toastGone = await page.evaluate(() => (document.querySelector("#toast") || {}).hidden);
  assert(toastGone === true, "no false warning at maxTex=2048 (toast cleared)");
  const maxTexUsed = await page.evaluate(() => (document.querySelector("#sh-maxtex") || {}).selectedOptions?.[0]?.text || "");
  log("maxTex: " + maxTexUsed);
  await clickByText(page, "button, .tab, [role=tab]", "SHEET VIEW");
  await sleep(400);
  await shot(page, "s5-multipage-split.png");

  /* telemetry: sheet internals + Chrome download events + export status */
  const mpSheetInfo = await page.evaluate(() => {
    const s = PF.ensureSheet();
    const allFit = s.frames.every(f => {
      const p = s.pages[f.page];
      return p && f.x + f.w <= p.width + 0.5 && f.y + f.h <= p.height + 0.5;
    });
    return { pages: s.pages.length, pagesCount: s.pagesCount,
      dims: s.pages.map(p => p.width + "x" + p.height),
      allFramesFit: allFit,
      dirty: !!PF.state.dirty, maxTex: PF.state.params.sheet.maxTex };
  });
  log("sheet before export: " + JSON.stringify(mpSheetInfo));
  assert(mpSheetInfo.pagesCount >= 2, `split into ${mpSheetInfo.pagesCount} pages`);
  assert(mpSheetInfo.allFramesFit, "every frame fits inside its page (no clipping)");
  await page.evaluate(() => {
    window.__rej = "";
    window.addEventListener("unhandledrejection", e => {
      window.__rej = String((e.reason && e.reason.stack) || e.reason);
    });
  });
  const dlEvents = [];
  try {
    const cdp2 = await page.createCDPSession();
    await cdp2.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: DL, eventsEnabled: true });
    cdp2.on("Browser.downloadWillBegin", e => dlEvents.push("begin:" + e.suggestedFilename));
    cdp2.on("Browser.downloadProgress", e => dlEvents.push(e.state));
  } catch (e) { log("cdp dl events unavailable: " + e.message); }

  const n0m = seen();
  await click(page, "#btn-ex-sheet");
  for (let i = 0; i < 30; i++) await sleep(200);
  const allNew = [...seen()].filter(f => !n0m.has(f));
  const statusAfter = await page.evaluate(() => ((document.querySelector("#status-msg") || {}).textContent || "").trim());
  const rejAfter = await page.evaluate(() => window.__rej || "");
  log("status after multipage export: " + JSON.stringify(statusAfter));
  log("download events: " + (dlEvents.join(" | ") || "(none)"));
  if (rejAfter) log("UNHANDLED REJECTION: " + rejAfter);
  if (allNew.length) ok(`export multi-page PNGs: ${allNew.join(", ")}`);
  else bad("export multi-page PNGs: no file appeared");

  /* ---- 8. wrap up ---- */
  const errCount = errors.length;
  assert(errCount === 0, `zero console/page errors (got ${errCount}: ${errors.slice(0, 3).join(" | ")})`);

  /* promote key shots to gallery names (1920x1080) */
  const promote = [
    ["s0-empty-state.png", "fab-gallery-01-first-open.png"],
    ["s1-imported-2-photos.png", "fab-gallery-02-import-real-photos.png"],
    ["s2-pixelated-dawnbringer.png", "fab-gallery-03-pixelated.png"],
    ["s3-sheet-packed.png", "fab-gallery-04-sheet-packed.png"],
    ["s4-animation-preview.png", "fab-gallery-05-animation-preview.png"],
    ["s5-multipage-split.png", "fab-gallery-06-multipage.png"],
  ];
  for (const [a, b] of promote) {
    if (fs.existsSync(path.join(SHOTS, a))) {
      fs.copyFileSync(path.join(SHOTS, a), path.join(FAB, b));
      ok(`gallery ${b}`);
    }
  }

  await browser.close();

  const passed = LOG.filter(l => l.startsWith("  ok -")).length;
  log(`== SUMMARY: ${passed} ok, ${failures} FAIL, ${Date.now() - t0}ms ==`);
  const report = path.join(FAB, "TEST-REPORT.txt");
  fs.writeFileSync(report,
    "PixelForge — Fab evidence shoot (real-browser, real images)\n" +
    "===========================================================\n" +
    LOG.join("\n") + "\n\nDownloaded exports: " + fs.readdirSync(DL).join(", ") + "\n");
  console.log("report: " + report);
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.error("FATAL", e); process.exit(2); });
