/* MegaUI render pipeline: SVG kit -> PNG4K, screens HTML -> 4K PNG.
 * Usage: node render4k.js components | screens | all
 */
"use strict";
const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium").default;

const ROOT = path.join(__dirname, "..");
const KIT = path.join(ROOT, "dist", "kit");
const SVG = path.join(KIT, "svg");
const PNG = path.join(KIT, "png4k");
const SCREENS = path.join(KIT, "screens");

function walk(dir, base = dir, out = []) {
  for (const n of fs.readdirSync(dir)) {
    const p = path.join(dir, n);
    if (fs.statSync(p).isDirectory()) walk(p, base, out);
    else out.push(path.relative(base, p));
  }
  return out;
}

async function launch(dsf, width, height) {
  return puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
    defaultViewport: { width, height, deviceScaleFactor: dsf },
  });
}

async function renderComponents() {
  const filter = process.argv[3] || "";
  const files = walk(SVG).filter((f) => f.endsWith(".svg") && f.includes(filter));
  console.log("components:", files.length);
  const browser = await launch(4, 3200, 1200);
  const page = await browser.newPage();
  let done = 0;
  const BATCH = 36;
  for (let i = 0; i < files.length; i += BATCH) {
    const batch = files.slice(i, i + BATCH);
    const html = `<!doctype html><style>
      *{box-sizing:border-box;margin:0;padding:0}
      body{background:transparent;display:flex;flex-wrap:wrap;gap:0;width:3160px}
      .slot{display:inline-block;margin:6px;background:transparent}
      .slot svg{display:block}
    </style><body>` +
      batch.map((f) => {
        const svg = fs.readFileSync(path.join(SVG, f), "utf8");
        return `<div class="slot" data-f="${f}">${svg}</div>`;
      }).join("") + `</body>`;
    await page.setContent(html, { waitUntil: "load" });
    const slots = await page.$$(".slot");
    for (const s of slots) {
      const rel = await s.evaluate((el) => el.dataset.f);
      const svgEl = await s.$("svg");
      const out = path.join(PNG, rel.replace(/\.svg$/, ".png"));
      fs.mkdirSync(path.dirname(out), { recursive: true });
      try {
        await svgEl.screenshot({ path: out, omitBackground: true });
      } catch (e) {
        console.log("skip", rel, String(e).slice(0, 80));
      }
      done++;
    }
    process.stdout.write(`\r${done}/${files.length}`);
  }
  console.log("\ncomponents done:", done);
  await browser.close();
}

async function renderScreens() {
  const browser = await launch(2, 1920, 1080);
  const page = await browser.newPage();
  const errs = [];
  page.on("pageerror", (e) => errs.push(String(e)));
  let done = 0;
  for (const th of fs.readdirSync(SCREENS)) {
    const dir = path.join(SCREENS, th);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".html"))) {
      await page.goto("file://" + path.join(dir, f), { waitUntil: "load" });
      await new Promise((r) => setTimeout(r, 80));
      const out = path.join(dir, f.replace(/\.html$/, ".png"));
      await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
      done++;
      process.stdout.write(`\r${done} screens`);
    }
  }
  console.log("\nscreens done:", done);
  if (errs.length) console.log("PAGE ERRORS:", errs.slice(0, 5).join(" | "));
  await browser.close();
}

(async () => {
  const mode = process.argv[2] || "all";
  if (mode === "components" || mode === "all") await renderComponents();
  if (mode === "screens" || mode === "all") await renderScreens();
  console.log("RENDER COMPLETE");
})().catch((e) => { console.error("FATAL", e); process.exit(1); });
