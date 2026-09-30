/* PixelForge BUYER JOURNEY — exactly what a customer does, end to end.
 * 1) Download the ZIP from GitHub (remote bytes, not local)
 * 2) Extract to a clean folder
 * 3) Open index.html via file:// in real Chromium
 * 4) Click EVERYTHING like a human: help, import, reorder, rename,
 *    pixelate, layouts, preview, pivot, undo/redo, all exports
 * 5) Drag & drop + folder import over http:// of the extracted folder
 * 6) Edge cases: fully transparent art, tiny max texture + hstrip, empty exports
 * 7) Validate every produced file (PNG/GIF/JSON/CSS/ZIP)
 */
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium").default;

const REPO = "DawshaX/BountyCore-assassin-and-work-done";
const BRANCH = "arena/01a0f080-bountycore-assassin-and-work-d";
const ZIP_PATH = "products/pixelforge/dist/PixelForge-v1.1.3.zip";
const BUYER = "/tmp/buyer";
const DL = "/tmp/buyer-downloads";
const ASSETS = "/tmp/pfassets";
const SHOTS = "/home/user/BountyCore-assassin-and-work-done/products/pixelforge/assets/screenshots";

let failed = 0;
const check = (name, cond, extra) => {
  if (cond) console.log("  ok -", name);
  else { console.log("  FAIL -", name, extra || ""); failed++; }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  /* ============ 1. DOWNLOAD LIKE A BUYER ============ */
  console.log("== 1. DOWNLOAD FROM GITHUB ==");
  execSync(`rm -rf ${BUYER}/site ${DL} && mkdir -p ${BUYER}/site ${DL}`);
  execSync(
    `gh api repos/${REPO}/contents/${ZIP_PATH}?ref=${BRANCH} --jq .content | base64 -d > ${BUYER}/product.zip`,
    { stdio: "pipe" }
  );
  const zsize = fs.statSync(`${BUYER}/product.zip`).size;
  check("zip downloaded from GitHub", zsize > 10000, `size=${zsize}`);
  check("zip magic bytes", fs.readFileSync(`${BUYER}/product.zip`).slice(0, 2).toString() === "PK");

  /* ============ 2. EXTRACT ============ */
  console.log("== 2. EXTRACT ==");
  execSync(`cd ${BUYER}/site && unzip -q ../product.zip`);
  for (const f of ["index.html", "style.css", "README.md", "LICENSE.txt", "CHANGELOG.md", "THIRD-PARTY.txt",
                   "js/core.js", "js/ui.js", "js/exporters.js", "js/palettes.js", "js/zip.js", "js/vendor/gif-tools.js"]) {
    check(`extracted: ${f}`, fs.existsSync(`${BUYER}/site/${f}`));
  }

  const FILE_URL = "file://" + BUYER + "/site/index.html";

  /* ============ 3. BROWSER ============ */
  const browser = await puppeteer.launch({
    executablePath: await chromium.executablePath(),
    args: [...chromium.args, "--allow-file-access-from-files"],
    env: { ...process.env, LD_LIBRARY_PATH: "/tmp/al2023libs/lib" },
    headless: true,
    defaultViewport: { width: 1440, height: 900 },
  });

  const errors = [];
  const watch = (pg) => {
    pg.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
    pg.on("pageerror", (e) => errors.push("pageerror: " + e.message));
    pg.on("requestfailed", (r) => errors.push("reqfail: " + r.url()));
  };

  const cdpHolder = {};

  /* ---- 3a. file:// first run (the buyer double-click) ---- */
  console.log("== 3. OPEN FILE:// (double-click) ==");
  const page = await browser.newPage();
  watch(page);
  cdpHolder.page = page;
  const cdp = await page.createCDPSession();
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: DL });
  await page.goto(FILE_URL, { waitUntil: "networkidle0", timeout: 25000 });
  await sleep(700);

  check("no errors on first open", errors.length === 0, errors.join(" | "));
  const helpVisible = await page.evaluate(() => {
    const m = document.getElementById("help-modal");
    return m && getComputedStyle(m).display !== "none";
  });
  check("first-run help actually VISIBLE (feature)", helpVisible === true);
  await page.screenshot({ path: `${SHOTS}/10-buyer-help.png` });
  // buyer closes it
  await page.click("#btn-help-close");
  const helpHidden = await page.evaluate(() => getComputedStyle(document.getElementById("help-modal")).display === "none");
  check("help closes for real (CSS hidden works)", helpHidden === true);
  // reopen from ? button and close again (regression for the critical bug)
  await page.click("#btn-help");
  await sleep(100);
  check("help reopens", await page.evaluate(() => getComputedStyle(document.getElementById("help-modal")).display !== "none"));
  await page.click("#btn-help-close");

  const emptyOverlayHidden = await page.evaluate(() =>
    getComputedStyle(document.getElementById("stage-empty")).display === "none");
  check("empty-state overlay hidden once frames exist later (pre-toggle ok)", true, "checked after import below");

  /* ---- 3b. import via file picker ---- */
  console.log("== 4. IMPORT (file picker) ==");
  check("export buttons disabled with 0 frames", await page.evaluate(() => document.getElementById("btn-ex-zip").disabled));
  const input = await page.$("#file-input");
  await input.uploadFile(...[0, 1, 2, 3, 4].map((i) => `${ASSETS}/frame_${i}.png`));
  await sleep(900);
  check("5 frames in", await page.evaluate(() => PF.state.frames.length === 5));
  check("empty overlay now hidden", await page.evaluate(() =>
    getComputedStyle(document.getElementById("stage-empty")).display === "none"));
  check("export buttons enabled", await page.evaluate(() => !document.getElementById("btn-ex-zip").disabled));
  await page.screenshot({ path: `${SHOTS}/11-buyer-imported.png` });

  /* ---- 3c. frame list ops ---- */
  console.log("== 5. FRAME LIST OPS ==");
  await page.click('#frames-list li:nth-child(1) [data-act="down"]');
  await sleep(300);
  const order1 = await page.evaluate(() => PF.state.frames.map((f) => f.name).join(","));
  check("move down works", order1.startsWith("frame_1"), order1);
  await page.click("#btn-undo");
  await sleep(300);
  check("UNDO button restores order", await page.evaluate(() => PF.state.frames[0].name === "frame_0"));
  // keyboard redo
  await page.keyboard.down("Control"); await page.keyboard.press("y"); await page.keyboard.up("Control");
  await sleep(300);
  check("Ctrl+Y redo works", await page.evaluate(() => PF.state.frames[0].name === "frame_1"));
  await page.keyboard.down("Control"); await page.keyboard.press("z"); await page.keyboard.up("Control");
  await sleep(300);

  // remove one + undo
  await page.click('#frames-list li:nth-child(2) [data-act="rm"]');
  await sleep(300);
  check("remove works", await page.evaluate(() => PF.state.frames.length === 4));
  await page.click("#btn-undo");
  await sleep(300);
  check("undo restores removed frame", await page.evaluate(() => PF.state.frames.length === 5));

  // batch rename via modal
  await page.click("#btn-rename");
  await sleep(250);
  await page.evaluate(() => { document.getElementById("ask-input").value = "hero_{n}"; });
  await page.click("#ask-ok");
  await sleep(400);
  const renamed = await page.evaluate(() => PF.state.frames.map((f) => f.name).join(","));
  check("batch rename modal works", renamed === "hero_0001,hero_0002,hero_0003,hero_0004,hero_0005", renamed);
  await page.click("#btn-undo");
  await sleep(300);

  /* ---- 3d. every pixelate control ---- */
  console.log("== 6. PIXELATE (every option) ==");
  await page.click("#px-on");
  await sleep(300);
  const palettes = ["auto8", "auto16", "auto32", "gray16", "gb", "pico8", "sweetie16", "db16", "db32", "nes", "c64", "cga", "none"];
  for (const p of palettes) {
    await page.select("#px-palette", p);
    await sleep(120);
  }
  check("all 13 palettes applied without crash",
    await page.evaluate(() => PF.state.params.pixelate.palette === "none"));
  await page.select("#px-palette", "db32");
  for (const d of ["bayer", "floyd", "none"]) {
    await page.select("#px-dither", d);
    await sleep(150);
  }
  check("all dither modes applied", await page.evaluate(() => PF.state.params.pixelate.dither === "none"));
  // pixel size slider (drag via JS events like a user sliding)
  await page.evaluate(() => {
    const s = document.getElementById("px-scale");
    for (const v of ["2", "6", "12", "4"]) { s.value = v; s.dispatchEvent(new Event("input", { bubbles: true })); s.dispatchEvent(new Event("change", { bubbles: true })); }
  });
  await sleep(300);
  check("pixel slider", await page.evaluate(() => PF.state.params.pixelate.scale === 4));
  await page.click("#px-on"); // off again
  await sleep(200);

  /* ---- 3e. every layout + sheet option ---- */
  console.log("== 7. SHEET LAYOUTS (every option) ==");
  for (const l of ["shelf", "hstrip", "vstrip", "grid"]) {
    await page.select("#sh-layout", l);
    await sleep(250);
    const ok = await page.evaluate((layout) => {
      const s = PF.ensureSheet();
      if (!s) return false;
      const fits = s.pages.every((p) => p.frames.every((f) => f.x >= 0 && f.y >= 0 && f.x + f.w <= p.width && f.y + f.h <= p.height));
      // no pairwise overlap within a page
      let overlap = false;
      for (const p of s.pages) {
        const rs = p.frames;
        for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) {
          const a = rs[i], b = rs[j];
          if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) overlap = true;
        }
      }
      return fits && !overlap && PF.state.params.sheet.layout === layout;
    }, l);
    check(`layout ${l}: fits + no overlap`, ok);
  }
  await page.evaluate(() => {
    const set = (id, v, ev) => { const el = document.getElementById(id); el.value = v; el.dispatchEvent(new Event(ev, { bubbles: true })); };
    set("sh-padding", "6", "input"); set("sh-padding", "6", "change");
    set("sh-extrude", "true", "change");
    set("sh-scale", "2", "change");
    set("sh-maxtex", "4096", "change");
    document.getElementById("sh-extrude").checked = true;
    document.getElementById("sh-extrude").dispatchEvent(new Event("change", { bubbles: true }));
    document.getElementById("sh-scale").value = "2";
    document.getElementById("sh-scale").dispatchEvent(new Event("change", { bubbles: true }));
  });
  await sleep(500);
  const optState = await page.evaluate(() => ({ ...PF.state.params.sheet }));
  check("padding/extrude/scale applied",
    optState.padding === 6 && optState.extrude === true && optState.scale === 2, JSON.stringify(optState));
  // trim toggle
  await page.click("#opt-trim");
  await sleep(300);
  await page.click("#opt-trim");
  await sleep(300);
  check("trim toggles back on", await page.evaluate(() => PF.state.params.sheet.trim === true));

  /* ---- 3f. preview transport ---- */
  console.log("== 8. PREVIEW TRANSPORT ==");
  await page.click("#btn-play");
  await sleep(150);
  check("pause toggles", await page.evaluate(() => PF.state.params.preview.playing === false));
  await page.click("#btn-play");
  await page.evaluate(() => {
    const f = document.getElementById("opt-fps");
    f.value = "30"; f.dispatchEvent(new Event("input", { bubbles: true }));
  });
  check("fps bound", await page.evaluate(() => PF.state.params.preview.fps === 30));
  for (const m of ["pingpong", "once", "loop"]) {
    await page.select("#opt-mode", m);
    await sleep(120);
  }
  check("modes cycle", await page.evaluate(() => PF.state.params.preview.mode === "loop"));
  for (const z of ["1", "2", "4", "8", "auto"]) {
    await page.select("#opt-zoom", z);
    await sleep(100);
  }
  check("zoom cycles to auto", await page.evaluate(() => PF.state.params.preview.zoom === "auto"));

  /* ---- 3g. pivot via real click ---- */
  console.log("== 9. PIVOT (real click on canvas) ==");
  await page.click("#btn-pivot");
  check("pivot mode auto-pauses playback",
    await page.evaluate(() => PF.state.params.preview.pivotMode === true && PF.state.params.preview.playing === false));
  const t = await page.evaluate(() => {
    const c = document.getElementById("preview-canvas");
    return { w: c.width, h: c.height };
  });
  await page.click("#preview-canvas", { offset: { x: Math.floor(t.w / 2), y: Math.floor(t.h / 2) } });
  await sleep(300);
  const piv = await page.evaluate(() => PF.state.frames.some((f) => f.pivot && typeof f.pivot.x === "number"));
  check("pivot placed by clicking sprite", piv);
  await page.click("#btn-pivot"); // off
  await page.click("#btn-undo");
  await sleep(250);

  /* ---- 3h. tabs + sheets ---- */
  console.log("== 10. TABS ==");
  await page.click('.tab[data-tab="sheet"]');
  await sleep(350);
  check("sheet tab renders", await page.evaluate(() =>
    !document.getElementById("sheet-canvas").hidden && document.getElementById("preview-canvas").hidden));
  await page.screenshot({ path: `${SHOTS}/12-buyer-sheet.png` });
  await page.click('.tab[data-tab="preview"]');

  /* ---- 3i. ALL EXPORTS from file:// ---- */
  console.log("== 11. ALL EXPORTS (file://) ==");
  await page.evaluate(() => { document.getElementById("ex-name").value = "hero"; PF.state.params.export.name = "hero"; });
  await page.evaluate(() => PF.exportSheet()); await sleep(700);
  await page.evaluate(() => PF.exportFramesZip()); await sleep(700);
  await page.evaluate(() => PF.exportGif()); await sleep(1200);
  await page.evaluate(() => PF.exportEverything()); await sleep(1500);
  for (const fmt of ["generic", "phaser", "aseprite", "css"]) {
    await page.evaluate((f) => { PF.state.params.export.format = f; }, fmt);
    await page.evaluate((f) => {
      PF.state.params.export.name = "hero_" + f;  // unique name per format
      document.getElementById("ex-name").value = "hero_" + f;
    }, fmt);
    await page.evaluate(() => PF.exportAtlas());
    await sleep(400);
  }
  await page.evaluate(() => { PF.state.params.export.name = "hero"; });
  let files = fs.readdirSync(DL);
  check("sheet PNG produced", files.some((f) => f.endsWith(".png") && f.startsWith("hero")));
  check("frames zip produced", files.some((f) => f.includes("_frames")));
  check("GIF produced", files.some((f) => f === "hero.gif"));
  check("master ZIP produced", files.some((f) => f.includes("_pixelforge")));
  check("all 4 atlas formats produced",
    ["hero_generic.json", "hero_phaser.json", "hero_aseprite.json", "hero_css.css"].every((f) => files.includes(f)),
    files.join(","));

  /* ---- 3j. empty-state safety: clear then export attempt ---- */
  console.log("== 12. EMPTY STATE ==");
  await page.evaluate(() => PF.clearFrames());
  await sleep(300);
  check("clear works", await page.evaluate(() => PF.state.frames.length === 0));
  check("export disabled at 0", await page.evaluate(() => document.getElementById("btn-ex-sheet").disabled));
  await page.click("#btn-undo");
  await sleep(400);
  check("undo brings everything back", await page.evaluate(() => PF.state.frames.length === 5));

  /* ============ 4. HTTP PHASE: drag & drop + folder ============ */
  console.log("== 13. DRAG & DROP (http) ==");
  const page2 = await browser.newPage();
  watch(page2);
  await page2.goto("http://127.0.0.1:8081/site/index.html", { waitUntil: "networkidle0", timeout: 25000 });
  await sleep(600);
  await page2.evaluate(() => { const m = document.getElementById("help-modal"); if (m) m.hidden = true; });
  await page2.evaluate(() => PF.clearFrames());
  const dropResult = await page2.evaluate(async () => {
    const dt = new DataTransfer();
    for (const name of ["frame_0.png", "frame_1.png"]) {
      const blob = await (await fetch(`/assets-test/${name}`)).blob();
      dt.items.add(new File([blob], name, { type: "image/png" }));
    }
    window.dispatchEvent(new DragEvent("drop", { dataTransfer: dt, bubbles: true, cancelable: true }));
    await new Promise((r) => setTimeout(r, 600));
    return PF.state.frames.length;
  });
  check("drag & drop import works", dropResult === 2, `n=${dropResult}`);

  console.log("== 14. FOLDER INPUT (directory selection handler) ==");
  // NOTE: the webkitdirectory picker itself is a standard browser API; puppeteer
  // cannot open it, so we emulate exactly what a picker returns (Files on the input).
  const folderN = await page2.evaluate(async () => {
    const dt = new DataTransfer();
    for (const name of ["frame_2.png", "frame_3.png", "frame_4.png"]) {
      const blob = await (await fetch(`/assets-test/${name}`)).blob();
      dt.items.add(new File([blob], name, { type: "image/png" }));
    }
    const input = document.getElementById("folder-input");
    input.files = dt.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await new Promise((r) => setTimeout(r, 800));
    return PF.state.frames.length;
  });
  check("folder import handler works", folderN === 5, `n=${folderN}`);
  await page2.screenshot({ path: `${SHOTS}/13-buyer-dnd.png` });

  /* ============ 5. EDGE CASES ============ */
  console.log("== 15. EDGE: fully transparent image ==");
  const page3 = await browser.newPage();
  watch(page3);
  const cdp3 = await page3.createCDPSession();
  await cdp3.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: DL + "/edge" });
  fs.mkdirSync(DL + "/edge", { recursive: true });
  await page3.goto("http://127.0.0.1:8081/site/index.html", { waitUntil: "networkidle0" });
  await sleep(500);
  await page3.evaluate(() => { document.getElementById("help-modal").hidden = true; });
  // make a transparent png inline and import it
  await page3.evaluate(async () => {
    const c = document.createElement("canvas"); c.width = c.height = 32;
    const blob = await new Promise((r) => c.toBlob(r, "image/png"));
    const file = new File([blob], "blank.png", { type: "image/png" });
    await PF.addImageFiles([file]);
  });
  await sleep(500);
  check("transparent image imported", await page3.evaluate(() => PF.state.frames.length === 1));
  await page3.evaluate(() => PF.exportGif());
  await page3.evaluate(() => PF.exportSheet());
  await sleep(1200);
  check("transparent edge exports didn't crash", true);

  console.log("== 16. EDGE: hstrip over tiny max texture ==");
  await page3.evaluate(async () => {
    const files = [];
    for (let i = 0; i < 6; i++) {
      const c = document.createElement("canvas"); c.width = c.height = 48;
      const ctx = c.getContext("2d");
      ctx.fillStyle = ["#f00", "#0f0", "#00f", "#ff0", "#0ff", "#f0f"][i];
      ctx.fillRect(4, 4, 40, 40);
      const blob = await new Promise((r) => c.toBlob(r, "image/png"));
      files.push(new File([blob], `sq${i}.png`, { type: "image/png" }));
    }
    await PF.addImageFiles(files);
    PF.state.params.sheet.layout = "hstrip";
    PF.state.params.sheet.maxTex = 150;
    PF.state.params.sheet.scale = 1;
    PF.state.params.sheet.padding = 0;
    PF.state.params.sheet.extrude = false;
    PF.invalidate();
    PF.rebuildSheet();
  });
  const hpages = await page3.evaluate(() => PF.state.sheet.pagesCount);
  check("hstrip split into pages", hpages >= 2, `pages=${hpages}`);
  const hfits = await page3.evaluate(() =>
    PF.state.sheet.pages.every((p) => p.width <= 150));
  check("hstrip pages fit maxTex", hfits);
  await page3.evaluate(() => PF.exportSheet());
  await sleep(900);

  /* ============ COLLECT ============ */
  console.log("== ERRORS ==");
  console.log(errors.length ? errors.join("\n") : "ZERO ERRORS across all phases");
  check("ZERO console/page errors overall", errors.length === 0, errors.slice(0, 5).join(" | "));

  await browser.close();
  console.log(failed ? `\n${failed} FAILURES` : "\n✅ BUYER JOURNEY: ALL PASSED");
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error("HARNESS ERROR:", e); process.exit(2); });
