/* Smoke test for itch-fill.js against a mock of the itch.io create-project form.
 * Run:  NODE_PATH=/tmp/pfjsdom/node_modules node test/itchfill_test.js
 * Needs jsdom (npm i jsdom). Network fetches are expected to FAIL here (sandbox
 * blocks CDNs) — the test asserts graceful degradation + all text fields filled. */
"use strict";
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const MOCK_FORM = `<!doctype html><html><body>
<form id="edit_form">
  <div class="field"><label for="game_title">Title</label>
    <input id="game_title" name="game[title]" type="text"></div>

  <div class="field"><label for="game_url">Project URL</label>
    <span>xdaw.itch.io/</span><input id="game_url" name="game[url]" type="text"></div>

  <div class="field"><label for="game_short">Short description or tagline</label>
    <textarea id="game_short" name="game[short_description]"></textarea></div>

  <fieldset class="field"><legend>What are you uploading?</legend>
    <label><input type="radio" name="classification" value="games"> Games — A piece of software you can play</label>
    <label><input type="radio" name="classification" value="comics"> Comics</label>
  </fieldset>

  <fieldset class="field"><legend>Kind of project</legend>
    <label><input type="radio" name="kind" value="downloadable"> Downloadable — You only have files to be downloaded</label>
    <label><input type="radio" name="kind" value="html"> HTML</label>
  </fieldset>

  <fieldset class="field"><legend>Release status</legend>
    <label><input type="radio" name="release" value="released"> Released — Project is complete, but might receive some updates</label>
    <label><input type="radio" name="release" value="wip"> Unreleased</label>
  </fieldset>

  <fieldset class="field" id="pricing_box"><legend>Pricing</legend>
    <label><input type="radio" name="price_type" value="donate"> $0 or donate</label>
    <label><input type="radio" name="price_type" value="paid"> Paid</label>
    <label><input type="radio" name="price_type" value="nopay"> No payments</label>
    <div class="field price_field"><label for="game_price">Fixed price</label>
      <input id="game_price" name="game[price]" type="text" placeholder="$"></div>
  </fieldset>

  <div class="field" id="uploads_box"><div class="header">Uploads</div>
    <input type="file" name="uploads[]">
    <p>or Choose from Dropbox — Add External file — File size limit: 1 GB</p></div>

  <div class="field"><label for="game_desc">Description</label>
    <p>This will make up the content of your game page.</p>
    <textarea id="game_desc" name="game[description]" rows="10"></textarea></div>

  <div class="field"><label for="game_genre">Genre</label>
    <select id="game_genre" name="game[genre_id]">
      <option value="">No genre</option>
      <option value="1">Action</option></select></div>

  <div class="field"><label>Tags</label>
    <input type="text" placeholder="Click to view options, type to filter or enter custom tag">
    <p>Max of 10.</p></div>

  <fieldset class="field"><legend>AI generation disclosure</legend>
    <label><input type="radio" name="ai" value="yes"> Yes — This project contains the output of Generative AI</label>
    <label><input type="radio" name="ai" value="no"> No — This project does not contain the output of Generative AI</label>
  </fieldset>

  <fieldset class="field"><legend>Community</legend>
    <label><input type="radio" name="community" value="disabled"> Disabled</label>
    <label><input type="radio" name="community" value="comments"> Comments — Add a nested comment thread to the bottom of the project page</label>
    <label><input type="radio" name="community" value="board"> Discussion board</label>
  </fieldset>

  <fieldset class="field"><legend>Visibility &amp; access</legend>
    <label><input type="radio" name="visibility" value="draft"> Draft — Only those who can edit the project can view the page</label>
    <label><input type="radio" name="visibility" value="public"> Public — Anyone can view the page</label>
  </fieldset>

  <div class="field" id="cover_box"><div class="header">Cover image</div>
    <input type="file" name="cover" accept="image/png,image/jpeg">
    <p>The cover image is used whenever itch.io wants to link to your project from another part of the site. Required (Minimum: 315x250, Recommended: 630x500)</p></div>

  <div class="field" id="video_box"><div class="header">Gameplay video or trailer</div>
    <input type="text" placeholder="https://www.youtube.com/watch?v=..."></div>

  <div class="field" id="shots_box"><div class="header">Screenshots</div>
    <input type="file" name="screenshots[]" multiple>
    <p>Screenshots will appear on your game's page. Optional but highly recommended. Upload 3 to 5 for best results.</p></div>
</form>
</body></html>`;

let passed = 0, failed = 0;
const check = (cond, msg) => {
  if (cond) { passed++; console.log("  ok - " + msg); }
  else { failed++; console.log("  FAIL - " + msg); }
};

(async () => {
  const logs = [];
  const vc = new VirtualConsole();
  vc.on("log", (...a) => logs.push(a.join(" ")));
  vc.on("warn", (...a) => logs.push(a.join(" ")));
  vc.on("error", (...a) => logs.push("ERROR " + a.join(" ")));
  vc.on("jsdomError", (e) => logs.push("JSDOM_ERROR " + e.message));

  const dom = new JSDOM(MOCK_FORM, { runScripts: "outside-only", virtualConsole: vc, url: "https://xdaw.itch.io/game/new" });
  const { window } = dom;
  const doc = window.document;

  const script = fs.readFileSync(path.join(__dirname, "..", "itch-fill.js"), "utf8");
  try {
    window.eval(script);
  } catch (e) {
    console.log("FAIL - script threw synchronously: " + e.message);
    process.exit(1);
  }

  // wait for async fill (tags loop ~2s + files + 700ms slug + summary)
  await new Promise(r => setTimeout(r, 6000));

  const v = sel => (doc.querySelector(sel) || {}).value;
  const checked = name => { const el = doc.querySelector(`input[name="${name}"]:checked`); return el && el.value; };

  console.log("== TEXT FIELDS ==");
  check(v("#game_title").includes("PixelForge"), "Title filled");
  check(v("#game_short").includes("100% offline"), "Short description filled");
  check(v("#game_desc").includes("fastest way") && v("#game_desc").includes("FAQ"), "Description filled (full markdown)");
  check(v("#game_url") === "pixelforge", "Project URL = pixelforge (got: " + v("#game_url") + ")");
  check(v("#game_price") === "5.99", "Price = 5.99 (got: " + JSON.stringify(v("#game_price")) + ")");

  console.log("== RADIOS / SELECTS ==");
  check(checked("classification") === "games", "Classification = Games");
  check(checked("kind") === "downloadable", "Kind = Downloadable");
  check(checked("release") === "released", "Release = Released");
  check(checked("price_type") === "paid", "Pricing = Paid");
  check(checked("ai") === "yes", "AI disclosure = Yes");
  check(checked("community") === "comments", "Community = Comments");
  check(checked("visibility") === "draft", "Visibility = Draft");
  check(v("#game_genre") === "", "Genre = No genre");

  console.log("== TAGS (widget not implemented in mock → warn expected) ==");
  check(logs.some(l => l.includes("Tags:")) || logs.some(l => l.includes("Tags input not found")), "Tags path executed without crash");

  console.log("== FILES (CDN blocked in sandbox → graceful FAIL expected) ==");
  check(logs.some(l => l.includes("cover") && l.includes("FAIL")), "cover fetch failed gracefully (expected here)");
  check(!logs.some(l => l.startsWith("ERROR") || l.startsWith("JSDOM_ERROR")), "no uncaught jsdom errors");
  check(logs.some(l => l.includes("SUMMARY")), "summary printed");

  console.log("== GRACEFUL ==");
  const failCount = logs.filter(l => l.includes("[FAIL]")).length;
  check(failCount >= 1 && failCount <= 6, "reported failures only for blocked fetches (got " + failCount + ")");

  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
