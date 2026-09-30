/* PixelForge — UI wiring, preview renderer, interactions (v1.1) */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = PF.state;

  /* ---------------- helpers ---------------- */

  let toastTimer = null;
  function showToast(msg) {
    const t = $("toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (t.hidden = true), 3200);
  }

  function askText(title, value) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "modal";
      overlay.innerHTML = `
        <div class="modal-card">
          <div class="modal-head"><h2>${title}</h2></div>
          <div style="padding:14px 16px; display:grid; gap:10px;">
            <input type="text" id="ask-input" spellcheck="false" />
            <div style="display:flex; gap:8px; justify-content:flex-end;">
              <button class="btn" id="ask-cancel">Cancel</button>
              <button class="btn btn-accent" id="ask-ok">OK</button>
            </div>
          </div>
        </div>`;
      document.body.appendChild(overlay);
      const input = overlay.querySelector("#ask-input");
      input.value = value;
      input.focus();
      input.select();
      const done = (v) => { overlay.remove(); resolve(v); };
      overlay.querySelector("#ask-ok").onclick = () => done(input.value);
      overlay.querySelector("#ask-cancel").onclick = () => done(null);
      input.onkeydown = (e) => {
        if (e.key === "Enter") done(input.value);
        if (e.key === "Escape") done(null);
      };
    });
  }

  /* ---------------- frames list ---------------- */

  function thumbFor(f) {
    if (!f.thumb) {
      try { f.thumb = f.src.toDataURL("image/png"); } catch { f.thumb = ""; }
    }
    return f.thumb;
  }

  function renderFrames() {
    const list = $("frames-list");
    list.innerHTML = "";
    $("frames-count").textContent = state.frames.length;
    $("stage-empty").hidden = state.frames.length > 0;
    toggleExport(state.frames.length > 0);

    state.frames.forEach((f, i) => {
      const li = document.createElement("li");
      li.draggable = true;
      li.dataset.id = f.id;
      if (i === state.activeFrame) li.classList.add("active");

      const img = document.createElement("img");
      img.src = thumbFor(f);
      img.alt = "";

      const meta = document.createElement("div");
      meta.className = "frame-meta";
      meta.innerHTML = `<div class="frame-name"></div><div class="frame-size">${f.src.width}×${f.src.height}${f.delay ? ` · ${f.delay}ms` : ""}</div>`;
      meta.querySelector(".frame-name").textContent = f.name;

      const actions = document.createElement("div");
      actions.className = "frame-actions";
      actions.innerHTML = `
        <button title="Move up" data-act="up">▲</button>
        <button title="Move down" data-act="down">▼</button>
        <button title="Remove" data-act="rm" class="rm">✕</button>`;
      actions.onclick = (e) => {
        const act = e.target.dataset.act;
        if (!act) return;
        e.stopPropagation();
        if (act === "up") PF.moveFrame(i, i - 1);
        if (act === "down") PF.moveFrame(i, i + 1);
        if (act === "rm") PF.removeFrame(f.id);
      };

      li.onclick = () => {
        state.activeFrame = i;
        renderFrames();
      };

      li.ondragstart = (e) => {
        li.classList.add("dragging");
        e.dataTransfer.setData("text/plain", String(i));
        e.dataTransfer.effectAllowed = "move";
      };
      li.ondragend = () => li.classList.remove("dragging");
      li.ondragover = (e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; };
      li.ondrop = (e) => {
        e.preventDefault();
        const from = parseInt(e.dataTransfer.getData("text/plain"), 10);
        if (!Number.isNaN(from)) PF.moveFrame(from, i);
      };

      li.append(img, meta, actions);
      list.appendChild(li);
    });
  }

  function toggleExport(on) {
    ["btn-export-sheet", "btn-export-json", "btn-export-zip",
     "btn-ex-sheet", "btn-ex-atlas", "btn-ex-frames", "btn-ex-gif", "btn-ex-zip",
     "btn-clear"].forEach((id) => { const el = $(id); if (el) el.disabled = !on; });
  }

  /* ---------------- preview ---------------- */

  const preview = { frame: 0, dir: 1, last: 0, acc: 0 };

  function fitCanvas(canvas) {
    const body = canvas.parentElement;
    const w = Math.max(160, Math.floor(body.clientWidth - 24));
    const h = Math.max(120, Math.floor(body.clientHeight - 24));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
  }

  function drawChecker(ctx, w, h, size) {
    ctx.fillStyle = "#171a22";
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = "#20242f";
    for (let y = 0; y < h; y += size) {
      for (let x = 0; x < w; x += size) {
        if (((x / size) + (y / size)) % 2 === 0) ctx.fillRect(x, y, size, size);
      }
    }
  }

  function activeProcessed() {
    if (!state.frames.length) return null;
    const f = state.frames[Math.min(state.activeFrame, state.frames.length - 1)];
    return f ? PF.processFrame(f) : null;
  }

  /** Compute sprite placement on the preview canvas. */
  function previewTransform(canvas) {
    const f = activeProcessed();
    if (!f || !f.cell) return null;
    const cell = f.cell;
    let zoom = state.params.preview.zoom;
    if (zoom === "auto") {
      const z = Math.min(
        Math.floor((canvas.width - 40) / cell.sw),
        Math.floor((canvas.height - 40) / cell.sh)
      );
      zoom = Math.max(1, Math.min(z, 16));
    } else zoom = parseInt(zoom, 10);
    const dw = cell.sw * zoom, dh = cell.sh * zoom;
    const dx = Math.floor((canvas.width - dw) / 2);
    const dy = Math.floor((canvas.height - dh) / 2);
    return { f, cell, zoom, dw, dh, dx, dy };
  }

  function renderPreview() {
    const canvas = $("preview-canvas");
    fitCanvas(canvas);
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    drawChecker(ctx, canvas.width, canvas.height, 12);

    const t = previewTransform(canvas);
    if (!t) return;

    ctx.fillStyle = "rgba(0,0,0,.35)";
    ctx.fillRect(t.dx + 4, t.dy + 4, t.dw, t.dh);
    ctx.drawImage(t.f.proc, t.cell.sx, t.cell.sy, t.cell.sw, t.cell.sh, t.dx, t.dy, t.dw, t.dh);

    // pivot crosshair
    if (state.params.preview.pivotMode) {
      const p = t.f.pivot || { x: t.cell.sw / 2, y: t.cell.sh / 2 };
      const px = t.dx + p.x * t.zoom;
      const py = t.dy + p.y * t.zoom;
      ctx.save();
      ctx.strokeStyle = "#41d6c3";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(px - 14, py); ctx.lineTo(px + 14, py);
      ctx.moveTo(px, py - 14); ctx.lineTo(px, py + 14);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(px, py, 6, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = "rgba(65,214,195,.9)";
      ctx.font = "12px monospace";
      ctx.fillText(`pivot ${Math.round(p.x)},${Math.round(p.y)}`, px + 12, py - 10);
      ctx.restore();
    }
  }

  function renderSheetView() {
    const canvas = $("sheet-canvas");
    fitCanvas(canvas);
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    drawChecker(ctx, canvas.width, canvas.height, 12);

    const sheet = PF.ensureSheet();
    if (!sheet) return;
    const pageIdx = Math.min(state.params.preview.page, sheet.pages.length - 1);
    const page = sheet.pages[pageIdx];
    const z = Math.max(0.05, Math.min(
      (canvas.width - 24) / page.width,
      (canvas.height - 24) / page.height,
      4
    ));
    const dw = Math.floor(page.width * z);
    const dh = Math.floor(page.height * z);
    ctx.drawImage(page.canvas, 0, 0, page.width, page.height,
      Math.floor((canvas.width - dw) / 2), Math.floor((canvas.height - dh) / 2), dw, dh);
  }

  function tick(ts) {
    const p = state.params.preview;
    if (state.frames.length > 1 && p.playing && p.tab === "preview") {
      const interval = 1000 / p.fps;
      if (!preview.last) preview.last = ts;
      preview.acc += ts - preview.last;
      preview.last = ts;
      while (preview.acc >= interval) {
        preview.acc -= interval;
        advance();
      }
    } else {
      preview.last = ts;
    }

    if (state.params.preview.tab === "preview") renderPreview();
    else renderSheetView();
    requestAnimationFrame(tick);
  }

  function advance() {
    const n = state.frames.length;
    if (n <= 1) return;
    const mode = state.params.preview.mode;
    if (mode === "loop") {
      preview.frame = (preview.frame + 1) % n;
    } else if (mode === "pingpong") {
      if (n === 2) preview.frame = 1 - preview.frame;
      else {
        preview.frame += preview.dir;
        if (preview.frame >= n - 1) { preview.frame = n - 1; preview.dir = -1; }
        if (preview.frame <= 0) { preview.frame = 0; preview.dir = 1; }
      }
    } else {
      if (preview.frame < n - 1) preview.frame++;
      else { state.params.preview.playing = false; syncPlayBtn(); }
    }
    state.activeFrame = preview.frame;
    updateInfo();
  }

  function syncPlayBtn() {
    $("btn-play").textContent = state.params.preview.playing ? "II" : "▶";
  }

  function updateInfo() {
    const sheet = state.sheet;
    const n = state.frames.length;
    const cur = n ? Math.min(preview.frame + 1, n) : 0;
    $("stage-info").textContent = n ? `${cur}/${n} · frame ${preview.frame + 1}` : "";
    $("status-sheet").textContent = sheet
      ? `sheet ${sheet.width}×${sheet.height}${sheet.pagesCount > 1 ? ` · ${sheet.pagesCount} pages` : ""} · ${state.frames.length} frames · ${state.params.sheet.scale}×`
      : "";
    updatePageNav();
  }

  function updatePageNav() {
    const sheet = state.sheet;
    const nav = $("page-nav");
    const multi = sheet && sheet.pagesCount > 1;
    nav.hidden = !multi;
    if (multi) {
      const i = Math.min(state.params.preview.page, sheet.pagesCount - 1);
      $("page-label").textContent = `page ${i + 1}/${sheet.pagesCount}`;
      $("page-prev").disabled = i <= 0;
      $("page-next").disabled = i >= sheet.pagesCount - 1;
    }
  }

  /* ---------------- rebuild ---------------- */

  let rebuildTimer = null;
  function rebuild(debounced) {
    clearTimeout(rebuildTimer);
    const run = () => {
      if (!state.frames.length) { state.sheet = null; PF.emit("sheet"); updateInfo(); return; }
      try {
        PF.rebuildSheet();
        updateInfo();
        PF.status(`Sheet built: ${state.sheet.width}×${state.sheet.height}${state.sheet.pagesCount > 1 ? ` (${state.sheet.pagesCount} pages)` : ""}`);
      } catch (err) {
        console.error(err);
        showToast("Build error: " + err.message);
      }
    };
    if (debounced) rebuildTimer = setTimeout(run, 90);
    else run();
  }

  /* ---------------- control sync (after undo) ---------------- */

  function syncControls() {
    const px = state.params.pixelate;
    $("px-on").checked = px.on;
    $("px-controls").classList.toggle("disabled", !px.on);
    $("px-scale").value = px.scale;
    $("px-scale-val").textContent = px.scale;
    $("px-palette").value = px.palette;
    $("px-dither").value = px.dither;

    const sh = state.params.sheet;
    $("sh-layout").value = sh.layout;
    $("sh-cols-row").style.display = sh.layout === "grid" ? "" : "none";
    $("sh-columns").value = sh.columns;
    $("sh-padding").value = sh.padding;
    $("sh-padding-val").textContent = sh.padding;
    $("sh-extrude").checked = sh.extrude;
    $("sh-maxtex").value = String(sh.maxTex);
    $("sh-scale").value = String(sh.scale);
    $("opt-trim").checked = sh.trim;

    const ex = state.params.export;
    $("ex-format").value = ex.format;
    $("ex-name").value = ex.name;

    syncHistoryButtons();
  }

  function syncHistoryButtons() {
    const h = PF.historyState();
    $("btn-undo").disabled = !h.canUndo;
    $("btn-redo").disabled = !h.canRedo;
  }

  /* ---------------- wiring ---------------- */

  function bind() {
    /* import */
    const fileInput = $("file-input");
    const folderInput = $("folder-input");
    $("btn-import").onclick = $("btn-add").onclick = $("btn-empty-import").onclick = () => fileInput.click();
    $("btn-folder").onclick = () => folderInput.click();
    fileInput.onchange = async () => {
      await PF.addImageFiles([...fileInput.files]);
      fileInput.value = "";
    };
    folderInput.onchange = async () => {
      const imgs = [...folderInput.files].filter((f) => f.type.startsWith("image/"));
      if (imgs.length) await PF.addImageFiles(imgs);
      else showToast("No images found in that folder.");
      folderInput.value = "";
    };

    /* drag & drop */
    const dz = $("drop-zone");
    let dragDepth = 0;
    window.addEventListener("dragenter", (e) => { e.preventDefault(); dragDepth++; dz.classList.add("over"); });
    window.addEventListener("dragleave", () => { if (--dragDepth <= 0) { dragDepth = 0; dz.classList.remove("over"); } });
    window.addEventListener("dragover", (e) => e.preventDefault());
    window.addEventListener("drop", async (e) => {
      e.preventDefault();
      dragDepth = 0;
      dz.classList.remove("over");
      const files = [...(e.dataTransfer?.files || [])];
      if (files.length) await PF.addImageFiles(files);
    });

    $("btn-clear").onclick = () => {
      if (state.frames.length && confirm(`Remove all ${state.frames.length} frames?`)) PF.clearFrames();
    };

    $("btn-rename").onclick = async () => {
      const tpl = await askText("BATCH RENAME", "{name}");
      if (tpl === null) return;
      const final = tpl.includes("{name}") || tpl.includes("{n}") ? tpl : tpl.replace(/\s*$/, "") + "_{n}";
      PF.renameAll(final);
      renderFrames();
      rebuild(true);
    };

    /* undo / redo */
    $("btn-undo").onclick = () => { PF.undo(); };
    $("btn-redo").onclick = () => { PF.redo(); };
    document.addEventListener("keydown", (e) => {
      const t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "SELECT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === "z" && !e.shiftKey) { e.preventDefault(); PF.undo(); }
      else if (mod && (e.key.toLowerCase() === "y" || (e.key.toLowerCase() === "z" && e.shiftKey))) { e.preventDefault(); PF.redo(); }
    });

    /* tabs */
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.onclick = () => {
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const name = tab.dataset.tab;
        state.params.preview.tab = name;
        $("preview-canvas").hidden = name !== "preview";
        $("sheet-canvas").hidden = name !== "sheet";
        $("transport").style.opacity = name === "preview" ? "1" : ".45";
        updatePageNav();
      };
    });

    /* page nav */
    $("page-prev").onclick = () => { state.params.preview.page = Math.max(0, state.params.preview.page - 1); updatePageNav(); };
    $("page-next").onclick = () => {
      const max = (state.sheet ? state.sheet.pagesCount : 1) - 1;
      state.params.preview.page = Math.min(max, state.params.preview.page + 1);
      updatePageNav();
    };

    /* transport */
    $("btn-play").onclick = () => {
      state.params.preview.playing = !state.params.preview.playing;
      syncPlayBtn();
    };
    $("opt-fps").oninput = (e) => {
      state.params.preview.fps = +e.target.value;
      $("fps-val").textContent = e.target.value;
    };
    $("opt-mode").onchange = (e) => { state.params.preview.mode = e.target.value; preview.dir = 1; };
    $("opt-zoom").onchange = (e) => { state.params.preview.zoom = e.target.value; };

    /* pivot mode */
    $("btn-pivot").onclick = () => {
      state.params.preview.pivotMode = !state.params.preview.pivotMode;
      $("btn-pivot").classList.toggle("toggled", state.params.preview.pivotMode);
      showToast(state.params.preview.pivotMode
        ? "Pivot mode ON — click on the sprite to place the pivot point"
        : "Pivot mode OFF");
    };
    $("preview-canvas").addEventListener("click", (e) => {
      if (!state.params.preview.pivotMode || !state.frames.length) return;
      const canvas = $("preview-canvas");
      const t = previewTransform(canvas);
      if (!t) return;
      const rect = canvas.getBoundingClientRect();
      const sx = canvas.width / rect.width;
      const sy = canvas.height / rect.height;
      const mx = (e.clientX - rect.left) * sx;
      const my = (e.clientY - rect.top) * sy;
      const localX = (mx - t.dx) / t.zoom;
      const localY = (my - t.dy) / t.zoom;
      const f = t.f;
      PF.setPivot(f.id, localX, localY);
      showToast(`Pivot set: ${Math.round(f.pivot ? f.pivot.x : localX)}, ${Math.round(f.pivot ? f.pivot.y : localY)}`);
    });

    /* pixelate controls (with undo gestures) */
    const pxOn = $("px-on"), pxBox = $("px-controls");
    pxOn.onchange = () => {
      state.params.pixelate.on = pxOn.checked;
      pxBox.classList.toggle("disabled", !pxOn.checked);
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("px-scale").oninput = (e) => {
      PF.beginParamGesture("px-scale");
      state.params.pixelate.scale = +e.target.value;
      $("px-scale-val").textContent = e.target.value;
      PF.invalidate();
      rebuild(true);
    };
    $("px-scale").onchange = () => { PF.endParamGesture(); PF.commitHistory(); };
    $("px-palette").onchange = (e) => {
      state.params.pixelate.palette = e.target.value;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("px-dither").onchange = (e) => {
      state.params.pixelate.dither = e.target.value;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };

    /* sheet controls */
    $("sh-layout").onchange = (e) => {
      state.params.sheet.layout = e.target.value;
      $("sh-cols-row").style.display = e.target.value === "grid" ? "" : "none";
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("sh-columns").onchange = (e) => {
      state.params.sheet.columns = Math.max(0, +e.target.value || 0);
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("sh-padding").oninput = (e) => {
      PF.beginParamGesture("sh-padding");
      state.params.sheet.padding = +e.target.value;
      $("sh-padding-val").textContent = e.target.value;
      PF.invalidate();
      rebuild(true);
    };
    $("sh-padding").onchange = () => { PF.endParamGesture(); PF.commitHistory(); };
    $("sh-extrude").onchange = (e) => {
      state.params.sheet.extrude = e.target.checked;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("sh-maxtex").onchange = (e) => {
      state.params.sheet.maxTex = +e.target.value;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("sh-scale").onchange = (e) => {
      state.params.sheet.scale = +e.target.value;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };
    $("opt-trim").onchange = (e) => {
      state.params.sheet.trim = e.target.checked;
      PF.invalidate();
      PF.commitHistory();
      rebuild();
    };

    /* export controls */
    $("ex-format").onchange = (e) => {
      state.params.export.format = e.target.value;
      PF.commitHistory();
    };
    $("ex-name").oninput = (e) => {
      PF.beginParamGesture("ex-name");
      state.params.export.name = (e.target.value || "sprites").replace(/[^\w\-.]/g, "_");
    };
    $("ex-name").onchange = () => { PF.endParamGesture(); PF.commitHistory(); };

    $("btn-export-sheet").onclick = $("btn-ex-sheet").onclick = () => PF.exportSheet();
    $("btn-export-json").onclick = $("btn-ex-atlas").onclick = () => PF.exportAtlas();
    $("btn-export-zip").onclick = $("btn-ex-zip").onclick = () => PF.exportEverything();
    $("btn-ex-frames").onclick = () => PF.exportFramesZip();
    $("btn-ex-gif").onclick = () => PF.exportGif();

    /* help modal */
    $("btn-help").onclick = () => ($("help-modal").hidden = false);
    $("btn-help-close").onclick = () => ($("help-modal").hidden = true);
    $("help-modal").onclick = (e) => { if (e.target === $("help-modal")) $("help-modal").hidden = true; };

    /* PF events */
    PF.on("frames", renderFrames);
    PF.on("rebuild", () => rebuild());
    PF.on("status", (msg) => ($("status-msg").textContent = msg));
    PF.on("toast", showToast);
    PF.on("history", syncHistoryButtons);
    PF.on("params", syncControls);
    PF.on("sheet", updatePageNav);
  }

  /* ---------------- init ---------------- */

  function init() {
    bind();
    PF.initHistory();
    renderFrames();
    syncControls();
    syncPlayBtn();
    requestAnimationFrame(tick);
    PF.status("Ready — import images to begin.");
    try {
      if (!localStorage.getItem("pf_seen_help")) {
        $("help-modal").hidden = false;
        localStorage.setItem("pf_seen_help", "1");
      }
    } catch { /* private mode */ }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
