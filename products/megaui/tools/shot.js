/* Screenshot each themed section of build/review/review.html */
"use strict";
const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium").default;

const ROOT = path.join(__dirname, "..");
const OUT = path.join(ROOT, "build", "review");

(async () => {
  const browser = await puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
    defaultViewport: { width: 1500, height: 1000, deviceScaleFactor: 2 },
  });
  const page = await browser.newPage();
  const errs = [];
  page.on("pageerror", (e) => errs.push(String(e)));
  await page.goto("file://" + path.join(OUT, "review.html"), { waitUntil: "load" });
  const themes = await page.$$eval("section[data-theme]", (els) =>
    els.map((e) => e.getAttribute("data-theme")));
  for (const th of themes) {
    const el = await page.$(`section[data-theme="${th}"]`);
    await el.screenshot({ path: path.join(OUT, `review-${th}.png`) });
    console.log("shot", th);
  }
  if (errs.length) console.log("PAGE ERRORS:", errs.join(" | "));
  await browser.close();
  console.log("done");
})().catch((e) => { console.error("FATAL", e); process.exit(1); });
