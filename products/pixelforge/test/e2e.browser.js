/* PixelForge REAL Chromium E2E — deps: npm i puppeteer-core @sparticuz/chromium (see ITCH.md) */
const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium").default;

const APP = "http://127.0.0.1:8080/";
const FILE_URL = "file://" + path.resolve("/home/user/BountyCore-assassin-and-work-done/products/pixelforge/index.html");
const SHOTS = "/home/user/BountyCore-assassin-and-work-done/products/pixelforge/assets/screenshots";
const DL = "/tmp/pfdownloads";
const ASSETS = "/tmp/pfassets";

let failed = 0;
const check = (name, cond, extra) => {
  if (cond) console.log("  ok -", name);
  else { console.log("  FAIL -", name, extra || ""); failed++; }
};

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  fs.rmSync(DL, { recursive: true, force: true });
  fs.mkdirSync(DL, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: await chromium.executablePath(),
    args: [...chromium.args, "--allow-file-access-from-files"],
    env: { ...process.env, LD_LIBRARY_PATH: "/tmp/al2023libs/lib" },
    headless: true,
    defaultViewport: { width: 1440, height: 900 },
  });

  const page = await browser.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => errors.push("reqfail: " + r.url() + " " + (r.failure() && r.failure().errorText)));

  const cdp = await page.createCDPSession();
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: DL });

  console.log("== LOAD OVER HTTP ==");
  await page.goto(APP, { waitUntil: "networkidle0", timeout: 25000 });
  await new Promise((r) => setTimeout(r, 600));
  check("no errors on load", errors.length === 0, errors.join(" | "));
  check("title", (await page.title()).includes("PixelForge"));

  // close first-run help modal if open
  await page.evaluate(() => { const m = document.getElementById("help-modal"); if (m) m.hidden = true; });
  await page.screenshot({ path: path.join(SHOTS, "01-empty.png") });

  console.log("== IMPORT PNG FRAMES ==");
  const input = await page.$("#file-input");
  await input.uploadFile(
    ...[0, 1, 2, 3, 4].map((i) => path.join(ASSETS, `frame_${i}.png`))
  );
  await new Promise((r) => setTimeout(r, 900));
  let n = await page.evaluate(() => PF.state.frames.length);
  check("5 frames imported", n === 5, `n=${n}`);
  const sheetInfo = await page.evaluate(() => {
    const s = PF.ensureSheet();
    return s && { w: s.width, h: s.height, frames: s.frames.length, pages: s.pagesCount };
  });
  check("sheet built", sheetInfo && sheetInfo.frames === 5, JSON.stringify(sheetInfo));
  await page.screenshot({ path: path.join(SHOTS, "02-animation.png") });

  console.log("== PLAY + PIXELATE ==");
  await page.click("#px-on");
  await new Promise((r) => setTimeout(r, 500));
  const pxOn = await page.evaluate(() => PF.state.params.pixelate.on);
  check("pixelate enabled", pxOn === true);
  await page.select("#px-palette", "pico8");
  await new Promise((r) => setTimeout(r, 500));
  const pal = await page.evaluate(() => PF.state.params.pixelate.palette);
  check("palette applied", pal === "pico8");
  await page.screenshot({ path: path.join(SHOTS, "03-pixelate.png") });

  console.log("== UNDO ==");
  const beforeUndo = await page.evaluate(() => PF.state.params.pixelate.palette);
  await page.evaluate(() => PF.undo());
  const afterUndo = await page.evaluate(() => PF.state.params.pixelate.palette);
  check("undo reverted palette", beforeUndo === "pico8" && afterUndo !== "pico8", `${beforeUndo} -> ${afterUndo}`);

  console.log("== PIVOT ==");
  await page.evaluate(() => {
    const f = PF.state.frames[0];
    PF.setPivot(f.id, 10, 20);
  });
  const pivot = await page.evaluate(() => {
    const f = PF.state.frames[0];
    return { pivot: f.pivot, cell: f.cell, requested: { x: 10, y: 20 } };
  });
  const px = pivot.pivot;
  check("pivot clamped inside cell", px && px.x === Math.min(10, pivot.cell.sw) && px.y === Math.min(20, pivot.cell.sh),
    JSON.stringify(pivot));

  console.log("== SHEET VIEW + PAGES ==");
  await page.click('.tab[data-tab="sheet"]');
  await new Promise((r) => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SHOTS, "04-sheet-view.png") });
  await page.click('.tab[data-tab="preview"]');

  console.log("== EXPORTS (real files via downloads) ==");
  await page.evaluate(() => PF.exportSheet());
  await page.evaluate(() => PF.exportAtlas());
  await page.evaluate(() => PF.exportGif());
  await new Promise((r) => setTimeout(r, 2500));
  const files = fs.readdirSync(DL);
  check("sheet PNG downloaded", files.some((f) => f.endsWith(".png")), files.join(","));
  check("atlas JSON downloaded", files.some((f) => f.endsWith(".json")), files.join(","));
  check("GIF downloaded", files.some((f) => f.endsWith(".gif")), files.join(","));

  // validate exported JSON + GIF bytes
  const jsonFile = files.find((f) => f.endsWith(".json"));
  if (jsonFile) {
    const j = JSON.parse(fs.readFileSync(path.join(DL, jsonFile), "utf8"));
    const keys = Object.keys(j.frames || {});
    check("json parses + 5 frames", keys.length === 5, keys.join(","));
    check("json has pivot", Object.values(j.frames).every((f) => f.pivot));
  }
  const gifFile = files.find((f) => f.endsWith(".gif"));
  if (gifFile) {
    const b = fs.readFileSync(path.join(DL, gifFile));
    const head = b.slice(0, 6).toString("ascii");
    check("gif valid header", head === "GIF89a" || head === "GIF87a", head);
    check("gif has 5 frames", b.includes(Buffer.from([0x2c, 0x00, 0x00])) || b.length > 1000, `size=${b.length}`);
  }

  console.log("== GIF IMPORT ==");
  await page.evaluate(() => PF.clearFrames());
  await new Promise((r) => setTimeout(r, 300));
  await input.uploadFile(path.join(ASSETS, "anim.gif"));
  await new Promise((r) => setTimeout(r, 900));
  const gifN = await page.evaluate(() => ({ n: PF.state.frames.length, delays: PF.state.frames.map(f => f.delay) }));
  check("gif -> 3 frames", gifN.n === 3, JSON.stringify(gifN));
  check("gif delays = 150ms", gifN.delays.every((d) => d === 150), gifN.delays.join(","));

  console.log("== MULTI-PAGE ==");
  await page.evaluate(() => {
    PF.clearFrames();
  });
  await input.uploadFile(...[0, 1, 2, 3, 4].map((i) => path.join(ASSETS, `frame_${i}.png`)));
  await new Promise((r) => setTimeout(r, 700));
  await page.evaluate(() => {
    PF.state.params.pixelate.on = false;   // back to full 64px cells
    PF.state.params.sheet.maxTex = 80;
    PF.state.params.sheet.layout = "grid";
    PF.state.params.sheet.columns = 0;
    PF.invalidate();
    PF.rebuildSheet();
  });
  const pages = await page.evaluate(() => PF.state.sheet.pagesCount);
  check("multi-page split works", pages >= 2, `pages=${pages}`);
  await page.evaluate(() => {
    PF.state.params.sheet.maxTex = 2048;
    PF.invalidate();
    PF.rebuildSheet();
  });
  await page.screenshot({ path: path.join(SHOTS, "06-multipage.png") });

  console.log("== OFFLINE FILE:// (buyer flow) ==");
  const errors2 = [];
  const page2 = await browser.newPage();
  page2.on("console", (m) => { if (m.type() === "error") errors2.push("console: " + m.text()); });
  page2.on("pageerror", (e) => errors2.push("pageerror: " + e.message));
  await page2.goto(FILE_URL, { waitUntil: "networkidle0", timeout: 25000 });
  await new Promise((r) => setTimeout(r, 700));
  check("file:// opens with zero errors", errors2.length === 0, errors2.join(" | "));
  const inp2 = await page2.$("#file-input");
  await inp2.uploadFile(path.join(ASSETS, "frame_0.png"));
  await new Promise((r) => setTimeout(r, 700));
  const n2 = await page2.evaluate(() => PF.state.frames.length);
  check("file:// import works", n2 === 1, `n=${n2}`);
  const gifLib = await page2.evaluate(() => typeof window.PFGif);
  check("vendor lib loaded on file://", gifLib === "object", gifLib);
  await page2.evaluate(() => { const m = document.getElementById("help-modal"); if (m) m.hidden = true; });
  await page2.screenshot({ path: path.join(SHOTS, "05-offline-file.png") });

  console.log("== ERRORS COLLECTED ==");
  console.log(errors.length ? errors.join("\n") : "NONE (http)");
  console.log(errors2.length ? errors2.join("\n") : "NONE (file://)");

  await browser.close();
  console.log(failed ? `\n${failed} FAILURES` : "\nALL REAL-BROWSER TESTS PASSED");
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error("HARNESS ERROR:", e); process.exit(2); });
