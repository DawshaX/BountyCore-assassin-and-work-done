/* ============================================================================
 * PixelForge — itch.io auto-fill script (EN)
 * ----------------------------------------------------------------------------
 * WHERE:  open https://xdaw.itch.io/game/new  (the create-project form)
 * HOW:    F12 → Console → paste this ENTIRE file → press Enter
 * WHAT:   fills Title, URL, descriptions, pricing, radios, tags, genre,
 *         AI disclosure, community, visibility — then downloads cover,
 *         screenshots and the product ZIP from GitHub and attaches them.
 * DOES NOT: submit the form, change anything on itch side except the fields
 *         you see. Review everything, then press Save yourself.
 * Retry: if some files fail (CDN blocked), re-run — it tries 4 mirrors.
 * ==========================================================================*/
(async () => {
  "use strict";

  /* ---------- config ---------- */
  const OWNER = "DawshaX", REPO = "BountyCore-assassin-and-work-done", REF = "itchkit";
  const BASE = `products/pixelforge`;

  const TITLE = "PixelForge — Sprite Sheet Maker & Pixel Art Studio";
  const SLUG  = "pixelforge";
  const TAGLINE = "Turn any images into pixel art, pack sprite sheets, preview animations and export engine-ready JSON/GIF — 100% offline.";
  const PRICE = "5.99";
  const TAGS = ["pixel art","sprite sheet","tool","game development","editor","animation","2d","utility","sprites","assets"];

  const DESCRIPTION = `**PixelForge is the fastest way to go from a folder of images to an animated, engine-ready sprite sheet.**

Built for indie devs who ship. No subscriptions, no cloud, no telemetry — the app runs entirely in your browser, even offline.

### The workflow

1. **Import** — drag & drop a batch of PNG/JPG/WEBP, a whole **folder**, or even an **animated GIF** (every frame + timing imported). Reorder frames by dragging, batch-rename in one click. Undo/Redo anywhere (Ctrl+Z / Ctrl+Y).
2. **Pixelate** (optional) — shrink any art to 1–16 px pixels and quantize it to a palette **extracted from your own art** (auto 8/16/32) or legendary retro palettes: Game Boy, PICO-8, Sweetie-16, DawnBringer, NES, C64, CGA… with Bayer or Floyd–Steinberg dithering.
3. **Pack** — Grid, tight shelf, or strip layouts. Trim transparent edges, add padding, extrude edges (bye-bye texture bleeding), cap at 1024–8192 px (oversized sheets auto-split into **multiple pages**), export at 1×–8× nearest-neighbour scale.
4. **Preview** — hit play and watch your animation at 1–60 FPS, loop / ping-pong / once. Click **PIVOT** and click the sprite to place its rotation point — exported to your JSON.
5. **Export** — one click for:
   - \`sprites.png\` — the sheet (one file per page)
   - atlas JSON — **Generic**, **Phaser 3** or **Aseprite** format, with pivot points
   - **CSS sprite** classes for web games
   - **animated GIF** of your preview (respects FPS & imported timing)
   - individual trimmed frames
   - everything in one ZIP (GIF included)

### Why PixelForge?

- **Everything offline** — your art never leaves your machine.
- **Zero setup** — open \`index.html\`, done. Works from a USB stick.
- **Pixel-perfect** — nearest-neighbour everywhere, integer output scales, optional edge extrusion.
- **Engine-ready** — imports cleanly into Phaser, Aseprite, Godot, Unity (via generic JSON), Construct, GameMaker and plain CSS.
- **Free updates** — pay once, get the 1.x line.

### FAQ

**Q: Do I need to install anything?**
No. It's a single folder — open the HTML file in any modern browser.

**Q: Can I use the sprites in commercial games?**
Yes. Outputs are yours, royalty-free, forever. See the EULA.

**Q: Does it work with Aseprite / Phaser / Godot?**
Yes — export the matching atlas format (Aseprite JSON, Phaser 3 JSON, or Generic JSON which most engines accept).

**Q: GIF support?**
Animated GIF imports bring in every frame with its timing. You can also export an animated GIF of your packed sheet directly.

**Q: Refunds?**
Digital goods — if it doesn't open or you're unhappy, message me and I'll sort it out.`;

  /* files: [repo-relative, display-name] per target input */
  const FILES = {
    cover:  [`${BASE}/assets/cover.png`, "cover.png"],
    shots:  [
      [`${BASE}/assets/screenshots/02-animation.png`, "01-animation.png"],
      [`${BASE}/assets/screenshots/03-pixelate.png`, "02-pixelate.png"],
      [`${BASE}/assets/screenshots/04-sheet-view.png`, "03-sheet-view.png"],
      [`${BASE}/assets/screenshots/06-multipage.png`, "04-multipage.png"],
      [`${BASE}/assets/screenshots/05-offline-file.png`, "05-offline.png"],
    ],
    upload: [`${BASE}/dist/PixelForge-v1.1.3.zip`, "PixelForge-v1.1.3.zip"],
  };

  /* ---------- results ---------- */
  const R = { ok: [], fail: [], warn: [] };
  const ok  = m => { R.ok.push(m);  console.log("%c[OK] " + m, "color:#2ecc71"); };
  const bad = m => { R.fail.push(m); console.warn("[FAIL] " + m); };
  const wrn = m => { R.warn.push(m); console.warn("[?] " + m); };

  const norm = s => (s || "").replace(/\s+/g, " ").trim().toLowerCase();
  const fire = (el, types) => types.forEach(t => el.dispatchEvent(new Event(t, { bubbles: true })));

  /* set value the way frameworks notice */
  function setNative(el, v) {
    const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype
                : el instanceof HTMLSelectElement  ? HTMLSelectElement.prototype
                : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, "value").set.call(el, v);
    fire(el, ["input", "change", "blur"]);
  }

  /* find a control by its visible label / header text (shortest match wins) */
  function byLabel(text, sel = "input, textarea, select") {
    const t = norm(text);
    let best = null, bestLen = 1e9;
    const cands = document.querySelectorAll("label, legend, .header, .subheader, [class*='header'], [class*='label'], dt");
    for (const c of cands) {
      const ct = norm(c.textContent);
      if (ct !== t && !ct.startsWith(t + " ") && !ct.startsWith(t + "—") && !ct.startsWith(t + " -")) continue;
      if (ct.length >= bestLen) continue;
      let ctl = null;
      if (c.control && c.control.matches && c.control.matches(sel)) ctl = c.control;
      else if (c.htmlFor && document.getElementById(c.htmlFor)) ctl = document.getElementById(c.htmlFor);
      else {
        const box = c.closest(".field, .form-group, .input-group, li, dd, section") || c.parentElement;
        ctl = box && box.querySelector(sel);
      }
      if (ctl && ctl.matches(sel)) { best = ctl; bestLen = ct.length; }
    }
    if (best) return best;
    /* fallback: by name/placeholder/id */
    return document.querySelector(
      `${sel}[name*='${t.replace(/'/g, "")}'], ${sel}[id*='${t.replace(/'/g, "")}'], ${sel}[placeholder*='${t.replace(/'/g, "")}']`
    );
  }

  /* find a radio/checkbox whose OWN label text contains/equals text */
  function byChoice(text, type = "radio") {
    const t = norm(text);
    let best = null, bestLen = 1e9;
    for (const r of document.querySelectorAll(`input[type=${type}]`)) {
      let lt = "";
      if (r.labels && r.labels.length) lt = norm(r.labels[0].textContent);
      if (!lt) lt = norm(r.parentElement && r.parentElement.textContent);
      if (!lt || lt.length > 300) continue;
      const hit = lt === t || lt.startsWith(t + " ") || lt.startsWith(t + "—") || lt.startsWith(t + " -") ||
                  lt.includes(" " + t + " —") || lt.includes(" " + t + " -");
      if (hit && lt.length < bestLen) { best = r; bestLen = lt.length; }
    }
    return best;
  }

  function clickIt(el, label) {
    if (!el) return bad(label + " — control not found");
    if (el.type === "checkbox" || el.type === "radio") {
      if (el.checked) return ok(label + " (already set)");
      el.click();
      if (el.checked || el.type === "checkbox") return ok(label);
      /* radio might have been blocked — force it */
      el.checked = true; fire(el, ["input", "change"]);
      return ok(label + " (forced)");
    }
    return ok(label + " (found)");
  }

  function setField(el, value, label) {
    if (!el) return bad(label + " — control not found");
    setNative(el, value);
    if (el.value !== String(value) && el.value.replace(/\s/g, "") !== String(value).replace(/\s/g, ""))
      return bad(label + ` — value not accepted (got "${el.value}")`);
    return ok(label);
  }

  /* ---------- CDN fetch with 4 mirrors ---------- */
  async function getBlob(rel) {
    const url = [
      `https://cdn.jsdelivr.net/gh/${OWNER}/${REPO}@${REF}/${rel}`,
      `https://raw.githubusercontent.com/${OWNER}/${REPO}/${REF}/${rel}`,
      `https://raw.githack.com/${OWNER}/${REPO}/${REF}/${rel}`,
      `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://raw.githubusercontent.com/${OWNER}/${REPO}/${REF}/${rel}`)}`,
    ];
    for (const u of url) {
      try {
        const res = await fetch(u, { mode: "cors" });
        if (res.ok) {
          const b = await res.blob();
          if (b.size > 0) { console.log(`  fetched ${rel} (${b.size} B) via ${new URL(u).host}`); return b; }
        }
      } catch (e) { /* try next mirror */ }
    }
    throw new Error("all mirrors failed for " + rel);
  }

  /* classify a file input by the text around it (innermost-first, length-guarded
     so the giant form container never matches everything) */
  function classify(fi) {
    let node = fi.parentElement, depth = 0;
    while (node && depth < 8) {
      const t = norm(node.textContent);
      if (t.length < 2500) {
        if (t.includes("cover image is used")) return "cover";
        if (t.includes("screenshots will appear")) return "shots";
        if (t.includes("file size limit") || t.includes("use butler") || t.includes("add external file")) return "upload";
        if (t.includes("gameplay video or trailer")) return "video";
      }
      node = node.parentElement; depth++;
    }
    const hint = norm(fi.name + " " + fi.accept + " " + fi.className + " " + fi.id);
    if (hint.includes("cover")) return "cover";
    if (hint.includes("shot")) return "shots";
    if (hint.includes("upload")) return "upload";
    return "other";
  }

  async function attach(kind, fi) {
    const spec = FILES[kind];
    if (!spec) return;
    try {
      const list = kind === "shots" ? spec : [spec];
      const dt = new DataTransfer();
      for (const [rel, name] of list) {
        const blob = await getBlob(rel);
        dt.items.add(new File([blob], name, { type: blob.type || (name.endsWith(".zip") ? "application/zip" : "image/png") }));
      }
      if (fi.files && fi.files.length) { try { fi.value = ""; } catch (e) {} }
      fi.files = dt.files;
      fire(fi, ["input", "change"]);
      ok(`${kind}: attached ${list.length} file(s) → "${fi.name || fi.id || "file input"}"`);
    } catch (e) {
      bad(`${kind} — ${e.message}. UPLOAD IT MANUALLY (drag from the kit zip).`);
    }
  }

  /* ============================ FILL ============================ */
  console.log("%c>>> PixelForge auto-fill starting…", "color:#f1c40f;font-weight:bold");

  /* text fields */
  setField(byLabel("Title"), TITLE, "Title");
  setField(byLabel("Short description or tagline"), TAGLINE, "Short description");
  setField(byLabel("Description"), DESCRIPTION, "Description (markdown)");

  /* classification / kind / release / pricing / visibility / AI / community */
  clickIt(byChoice("Games"), "Classification = Games");
  clickIt(byChoice("Downloadable"), "Kind of project = Downloadable");
  clickIt(byChoice("Released"), "Release status = Released");
  clickIt(byChoice("Paid"), "Pricing = Paid");

  /* price input: try several strategies */
  (() => {
    const tries = [
      () => document.querySelector("input[name*='price'][type='text'], input[name*='price'][type='number']"),
      () => { const r = byChoice("Paid"); const box = r && r.closest(".field, section, li"); return box && box.querySelector("input[type=text]"); },
      () => byLabel("Fixed price"),
      () => document.querySelector("input[placeholder='$'], input[placeholder*='price']")
    ];
    for (const t of tries) {
      let el = null;
      try { el = t(); } catch (e) {}
      if (el && el.tagName === "INPUT") { setNative(el, PRICE); if (el.value) return ok("Price = $" + PRICE); }
    }
    bad("Price input not found — set $5.99 manually");
  })();

  clickIt(byChoice("Yes — This project contains"), "AI disclosure = Yes");
  clickIt(byChoice("Draft"), "Visibility = Draft (change to Public after review)");
  /* community: Comments = on (may be radio or checkbox) */
  (() => {
    let c = byChoice("Comments", "radio") || byChoice("Comments", "checkbox");
    if (!c) {
      /* fallback: checkbox whose label mentions comment thread */
      for (const x of document.querySelectorAll("input[type=checkbox]")) {
        const lt = norm(x.labels && x.labels[0] ? x.labels[0].textContent : x.parentElement.textContent);
        if (lt.startsWith("comments")) { c = x; break; }
      }
    }
    clickIt(c, "Comments = enabled");
  })();

  /* genre select */
  (() => {
    const sels = [...document.querySelectorAll("select")];
    for (const s of sels) {
      const opts = [...s.options].map(o => o.text);
      if (opts.some(o => norm(o) === "no genre")) {
        const opt = [...s.options].find(o => norm(o.text) === "no genre" || norm(o.text).startsWith("no genre"));
        setNative(s, opt.value); return ok("Genre = No genre");
      }
    }
    wrn("Genre select not found (may not exist) — skip if so");
  })();

  /* tags (token input): type + Enter each */
  (async () => {
    const input = document.querySelector(
      "input[placeholder*='custom tag'], input[placeholder*='type to filter'], input[name*='tag']"
    );
    if (!input) return bad("Tags input not found — add the 10 tags manually from ANSWERS.txt");
    let done = 0;
    for (const tag of TAGS) {
      setNative(input, tag);
      ["keydown", "keypress", "keyup"].forEach(t =>
        input.dispatchEvent(new KeyboardEvent(t, { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }))
      );
      await new Promise(r => setTimeout(r, 180));
      if (input.value === "") done++;
      setNative(input, "");
    }
    if (done >= 8) ok(`Tags: ${done}/10 added (verify visually)`);
    else wrn(`Tags: only ${done}/10 registered — type the rest manually: ${TAGS.join(", ")}`);
  })();

  /* file inputs (async — runs after the sync fill above) */
  (async () => {
    const fis = [...document.querySelectorAll("input[type=file]")];
    console.log("file inputs found:", fis.length);
    const buckets = {};
    for (const fi of fis) {
      const k = classify(fi);
      (buckets[k] = buckets[k] || []).push(fi);
      console.log("  •", k, "←", (fi.name || fi.id || fi.className || "?"));
    }
    if (buckets.cover) await attach("cover", buckets.cover[0]); else bad("cover input not found");
    if (buckets.shots) await attach("shots", buckets.shots[0]); else bad("screenshots input not found");
    if (buckets.upload) await attach("upload", buckets.upload[0]); else bad("uploads input not found");

    /* slug LAST (title blur may regenerate it) */
    await new Promise(r => setTimeout(r, 700));
    setField(byLabel("Project URL"), SLUG, "Project URL = /" + SLUG);

    /* ---------- summary ---------- */
    console.log("%c========== SUMMARY ==========", "color:#f1c40f;font-weight:bold");
    R.ok.forEach(m => console.log("%c✓ " + m, "color:#2ecc71"));
    R.warn.forEach(m => console.log("%c▲ " + m, "color:#f1c40f"));
    R.fail.forEach(m => console.log("%c✗ " + m, "color:#e74c3c;font-weight:bold"));
    console.log(`%c${R.ok.length} ok · ${R.warn.length} warnings · ${R.fail.length} FAILED — now SCROLL the form, verify every field, fix any ✗ manually (answers in ANSWERS.txt), then Save.`, "color:#f1c40f;font-weight:bold");
  })();
})();
