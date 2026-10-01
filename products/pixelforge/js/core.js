/* PixelForge — core state + processing pipeline (v1.1) */
(function () {
  "use strict";

  const state = {
    frames: [], // {id,name,src,delay,pivot,cacheKey,proc,cell,thumb}
    seq: 0,
    params: {
      pixelate: { on: false, scale: 4, palette: "auto16", dither: "none" },
      sheet: { layout: "grid", columns: 0, padding: 0, extrude: false, maxTex: 2048, scale: 1, trim: true },
      preview: { fps: 12, mode: "loop", zoom: "auto", playing: true, tab: "preview", page: 0, pivotMode: false },
      export: { format: "generic", name: "sprites" },
    },
    sheet: null,
    activeFrame: 0,
    dirty: true,
  };

  const listeners = [];
  function on(evt, fn) { listeners.push([evt, fn]); }
  function emit(evt, arg) {
    for (const [e, fn] of listeners) if (e === evt || e === "*") fn(evt === e ? arg : evt, arg);
  }

  /* ================= history (undo / redo) ================= */

  const history = { stack: [], idx: -1, cap: 50, key: null };
  let gestureKey = null;

  function snapshot() {
    return {
      frames: state.frames.map((f) => ({
        id: f.id, name: f.name, src: f.src, thumb: f.thumb,
        delay: f.delay, pivot: f.pivot ? { ...f.pivot } : null,
      })),
      params: JSON.parse(JSON.stringify(state.params)),
      activeFrame: state.activeFrame,
      seq: state.seq,
    };
  }

  function keyOf(s) {
    return JSON.stringify([
      s.frames.map((f) => [f.id, f.name, f.delay, f.pivot]),
      s.params, s.activeFrame, s.seq,
    ]);
  }

  function restore(snap) {
    state.frames = snap.frames.map((f) => ({ ...f, cacheKey: null, proc: null, cell: null }));
    state.params = JSON.parse(JSON.stringify(snap.params));
    state.activeFrame = Math.min(snap.activeFrame, Math.max(0, state.frames.length - 1));
    state.seq = snap.seq;
    history.key = keyOf(snapshot());
    invalidate();
    emit("frames");
    emit("params");
    emit("rebuild");
    emit("history");
  }

  /** Push current state onto the undo timeline (no-op if nothing changed). */
  function commitHistory() {
    const s = snapshot();
    const k = keyOf(s);
    if (k === history.key && history.idx === history.stack.length - 1) return;
    history.stack = history.stack.slice(0, history.idx + 1);
    history.stack.push(s);
    history.key = k;
    if (history.stack.length > history.cap) { history.stack.shift(); history.idx--; }
    history.idx = history.stack.length - 1;
    emit("history");
  }

  function initHistory() {
    const s = snapshot();
    history.stack = [s];
    history.idx = 0;
    history.key = keyOf(s);
    emit("history");
  }

  /** Slider gesture: commit once BEFORE the first live mutation. */
  function beginParamGesture(key) {
    if (gestureKey === key) return;
    gestureKey = key;
    commitHistory();
  }
  function endParamGesture() { gestureKey = null; }

  function undo() {
    endParamGesture();
    if (history.idx <= 0) return false;
    history.idx--;
    restore(history.stack[history.idx]);
    status("Undo");
    return true;
  }
  function redo() {
    endParamGesture();
    if (history.idx < 0 || history.idx >= history.stack.length - 1) return false;
    history.idx++;
    restore(history.stack[history.idx]);
    status("Redo");
    return true;
  }
  function historyState() {
    return { canUndo: history.idx > 0, canRedo: history.idx >= 0 && history.idx < history.stack.length - 1 };
  }

  /* ================= import ================= */

  function isGif(file) {
    return file.type === "image/gif" || /\.gif$/i.test(file.name || "");
  }

  /**
   * Load a file → array of {canvas, delay(ms|null)}.
   * GIFs are decoded frame-by-frame (composited), everything else is 1 frame.
   */
  async function loadImageFrames(file) {
    if (isGif(file) && window.PFGif) {
      const buf = await file.arrayBuffer();
      const parsed = PFGif.parseGIF(buf);
      const gframes = PFGif.decompressFrames(parsed, true);
      if (!gframes.length) throw new Error("empty gif");
      const W = parsed.lsd.width, H = parsed.lsd.height;
      const main = document.createElement("canvas");
      main.width = W; main.height = H;
      const ctx = main.getContext("2d", { willReadFrequently: true });
      const out = [];
      let prevDisposal = 0, prevDims = null, backup = null;

      for (const gf of gframes) {
        if (prevDisposal === 2 && prevDims) {
          ctx.clearRect(prevDims.left, prevDims.top, prevDims.width, prevDims.height);
        } else if (prevDisposal === 3 && backup) {
          ctx.putImageData(backup, 0, 0);
        }
        if (gf.disposalType === 3) backup = ctx.getImageData(0, 0, W, H);

        const patch = new ImageData(gf.patch, gf.dims.width, gf.dims.height);
        ctx.putImageData(patch, gf.dims.left, gf.dims.top);

        const copy = document.createElement("canvas");
        copy.width = W; copy.height = H;
        const cctx = copy.getContext("2d");
        cctx.drawImage(main, 0, 0);
        out.push({ canvas: copy, delay: gf.delay || null });

        prevDisposal = gf.disposalType;
        prevDims = gf.dims;
      }
      return out;
    }

    const canvas = await decodeImage(file);
    return [{ canvas, delay: null }];
  }

  function decodeImage(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        const c = document.createElement("canvas");
        c.width = img.naturalWidth || img.width;
        c.height = img.naturalHeight || img.height;
        c.getContext("2d").drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
        resolve(c);
      };
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("decode failed")); };
      img.src = url;
    });
  }

  async function addImageFiles(files) {
    const added = [];
    for (const file of files) {
      if (!file.type.startsWith("image/")) continue;
      try {
        const parts = await loadImageFrames(file);
        const base = stripExt(file.name || "frame") || `frame_${state.seq + 1}`;
        const multi = parts.length > 1;
        parts.forEach((p, i) => {
          state.seq++;
          added.push({
            id: state.seq,
            name: multi ? `${base}_${String(i + 1).padStart(4, "0")}` : base,
            src: p.canvas,
            delay: p.delay,
            pivot: null,
            cacheKey: null,
            proc: null,
            cell: null,
            thumb: null,
          });
        });
      } catch (err) {
        console.warn("skip file", file.name, err);
      }
    }
    if (added.length) {
      state.frames.push(...added);
      invalidate();
      commitHistory();
      emit("frames");
      emit("rebuild");
      const gifNote = added.some((f) => f.delay) ? ` (${added.length} GIF frames)` : "";
      status(`Imported ${added.length} image${added.length > 1 ? "s" : ""}${gifNote}.`);
    }
    return added;
  }

  function stripExt(n) { return n.replace(/\.[^.]+$/, ""); }

  /* ================= frame ops ================= */

  function removeFrame(id) {
    const i = state.frames.findIndex((f) => f.id === id);
    if (i < 0) return;
    state.frames.splice(i, 1);
    if (state.activeFrame >= state.frames.length) state.activeFrame = Math.max(0, state.frames.length - 1);
    invalidate();
    commitHistory();
    emit("frames");
    emit("rebuild");
  }

  function clearFrames() {
    if (!state.frames.length) return;
    state.frames = [];
    state.activeFrame = 0;
    invalidate();
    commitHistory();
    emit("frames");
    emit("rebuild");
  }

  function moveFrame(from, to) {
    if (to < 0 || to >= state.frames.length || from === to) return;
    const [f] = state.frames.splice(from, 1);
    state.frames.splice(to, 0, f);
    if (state.activeFrame === from) state.activeFrame = to;
    commitHistory();
    emit("frames");
    emit("rebuild");
  }

  function renameAll(template) {
    state.frames.forEach((f, i) => {
      const pad = String(i + 1).padStart(4, "0");
      let name;
      if (template.includes("{name}")) name = template.replace(/\{name\}/g, f.name);
      else if (template.includes("{n}")) name = template.replace(/\{n\}/g, pad);
      else name = `${template.replace(/\s*$/, "")}_${pad}`;
      f.name = (name || f.name).slice(0, 64);
    });
    commitHistory();
    emit("frames");
    emit("rebuild");
  }

  function setPivot(id, x, y) {
    const f = state.frames.find((f) => f.id === id);
    if (!f) return;
    processFrame(f);
    const cell = f.cell;
    const px = Math.max(0, Math.min(cell.sw, Math.round(x)));
    const py = Math.max(0, Math.min(cell.sh, Math.round(y)));
    if (f.pivot && f.pivot.x === px && f.pivot.y === py) return;
    f.pivot = { x: px, y: py };
    commitHistory();
    emit("rebuild");
  }

  function invalidate() { state.dirty = true; }

  /* ================= processing ================= */

  function frameKey() {
    const p = state.params;
    return JSON.stringify([p.pixelate, p.sheet.trim]);
  }

  function processFrame(f) {
    const key = frameKey();
    if (f.cacheKey === key && f.proc && f.cell) return f;

    const px = state.params.pixelate;
    let base = f.src;
    if (px.on && px.scale > 1) base = PF.pixelate(f.src, px.scale);

    const out = document.createElement("canvas");
    out.width = base.width;
    out.height = base.height;
    const ctx = out.getContext("2d", { willReadFrequently: true });
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(base, 0, 0);

    let imgData = null;
    if (px.on) {
      imgData = ctx.getImageData(0, 0, out.width, out.height);
      if (px.palette === "auto8" || px.palette === "auto16" || px.palette === "auto32") {
        const n = px.palette === "auto8" ? 8 : px.palette === "auto16" ? 16 : 32;
        const pal = PF.autoPalette([imgData], n);
        PF.quantize(imgData, pal, px.dither);
      } else if (px.palette !== "none") {
        const pal = PF.palettes[px.palette];
        if (pal) PF.quantize(imgData, pal, px.dither);
      }
      if (px.palette !== "none") ctx.putImageData(imgData, 0, 0);
    }

    let cell = { sx: 0, sy: 0, sw: out.width, sh: out.height };
    if (state.params.sheet.trim) {
      if (!imgData) imgData = ctx.getImageData(0, 0, out.width, out.height);
      const bbox = findAlphaBBox(imgData);
      if (bbox) cell = bbox;
    }

    // clamp pivot into current cell
    if (f.pivot) {
      f.pivot.x = Math.max(0, Math.min(cell.sw, f.pivot.x));
      f.pivot.y = Math.max(0, Math.min(cell.sh, f.pivot.y));
    }

    f.proc = out;
    f.cell = cell;
    f.cacheKey = key;
    return f;
  }

  function findAlphaBBox(img) {
    const { data, width: w, height: h } = img;
    let minX = w, minY = h, maxX = -1, maxY = -1;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (data[(y * w + x) * 4 + 3] > 8) {
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
        }
      }
    }
    if (maxX < 0) return null;
    return { sx: minX, sy: minY, sw: maxX - minX + 1, sh: maxY - minY + 1 };
  }

  /* ================= packing ================= */

  function rebuildSheet() {
    if (!state.frames.length) { state.sheet = null; state.dirty = false; emit("sheet"); return; }

    const P = state.params.sheet;
    const frames = state.frames.map(processFrame);

    const scale = P.scale;
    const pad = P.extrude ? Math.max(P.padding, scale) : P.padding;
    const items = frames.map((f) => ({ f, w: f.cell.sw * scale, h: f.cell.sh * scale }));
    const maxW = P.maxTex;
    const n = items.length;

    const cw = Math.max(1, ...items.map((i) => i.w));
    const ch = Math.max(1, ...items.map((i) => i.h));

    /* Warn only when a single frame cannot fit inside ONE page
       (multi-page split handles wider grids without data loss). */
    if (cw + pad * 2 > maxW || ch + pad * 2 > maxW) {
      toast(`⚠ Frame too wide for ${maxW}px texture — reduce scale/padding.`);
    }

    let positions = [];
    let sheetW = 0, sheetH = 0;

    if (P.layout === "grid" || P.layout === "hstrip" || P.layout === "vstrip") {
      let cols;
      if (P.layout === "hstrip") cols = n;
      else if (P.layout === "vstrip") cols = 1;
      else {
        cols = P.columns > 0 ? P.columns : Math.ceil(Math.sqrt(n));
        cols = Math.max(1, Math.min(cols, n));
      }
      let rows = Math.ceil(n / cols);

      if (P.layout === "grid") {
        let need = cols * (cw + pad) + pad;
        while (need > maxW && cols < n) {
          cols++;
          rows = Math.ceil(n / cols);
          need = cols * (cw + pad) + pad;
        }
      }

      positions = items.map((_, i) => {
        const cx = i % cols, cy = Math.floor(i / cols);
        return { x: pad + cx * (cw + pad), y: pad + cy * (ch + pad), w: cw, h: ch };
      });
      sheetW = cols * (cw + pad) + pad;
      sheetH = rows * (ch + pad) + pad;
      if (P.layout === "hstrip") { sheetW = n * (cw + pad) + pad; sheetH = ch + pad * 2; }
      if (P.layout === "vstrip") { sheetW = cw + pad * 2; sheetH = n * (ch + pad) + pad; }
    } else {
      // shelf packing (tight, variable sizes)
      const shelfItems = items.slice().sort((a, b) => b.h - a.h || b.w - a.w);
      let x = pad, y = pad, shelfH = 0;
      sheetW = 0;
      const shelfPos = [];
      for (const it of shelfItems) {
        if (x + it.w + pad > maxW && x > pad) {
          x = pad;
          y += shelfH + pad;
          shelfH = 0;
        }
        shelfPos.push({ x, y, w: it.w, h: it.h });
        x += it.w + pad;
        shelfH = Math.max(shelfH, it.h);
        sheetW = Math.max(sheetW, x);
      }
      sheetH = y + shelfH + pad;
      const byId = new Map();
      shelfItems.forEach((it, i) => byId.set(it.f.id, shelfPos[i]));
      positions = frames.map((f) => byId.get(f.id));
    }

    sheetW = Math.max(1, Math.ceil(sheetW));
    sheetH = Math.max(1, Math.ceil(sheetH));

    /* ---- split into pages if it exceeds the max texture size ---- */
    const pageDefs = splitPages(positions, sheetW, sheetH, P.maxTex, pad);

    const extrude = P.extrude && scale >= 1;
    const pages = pageDefs.map((def) => {
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, def.w);
      canvas.height = Math.max(1, def.h);
      const ctx = canvas.getContext("2d");
      ctx.imageSmoothingEnabled = false;
      const placed = [];

      for (const i of def.indices) {
        const f = frames[i];
        const pos = positions[i];
        const cell = f.cell;
        const dw = cell.sw * scale;
        const dh = cell.sh * scale;
        const dx = pos.x - def.x0;
        const dy = pos.y - def.y0;

        if (extrude) {
          const o = scale;
          const offs = [[0, -o], [0, o], [-o, 0], [o, 0], [-o, -o], [o, -o], [-o, o], [o, o]];
          for (const [ox, oy] of offs) {
            ctx.drawImage(f.proc, cell.sx, cell.sy, cell.sw, cell.sh, dx + ox, dy + oy, dw, dh);
          }
        }
        ctx.drawImage(f.proc, cell.sx, cell.sy, cell.sw, cell.sh, dx, dy, dw, dh);

        placed.push({
          id: f.id,
          name: f.name,
          page: def.page,
          x: dx, y: dy, w: dw, h: dh,
          srcW: cell.sw, srcH: cell.sh,
          fullW: f.proc.width, fullH: f.proc.height,
          offX: cell.sx, offY: cell.sy,
          pivot: f.pivot ? { x: f.pivot.x, y: f.pivot.y } : { x: Math.round(cell.sw / 2), y: Math.round(cell.sh / 2) },
        });
      }
      return { ...def, canvas, width: canvas.width, height: canvas.height, frames: placed };
    });

    const all = pages.flatMap((p) => p.frames);
    state.sheet = {
      pages,
      pagesCount: pages.length,
      frames: all,
      canvas: pages[0].canvas,
      width: pages[0].width,
      height: pages[0].height,
      order: state.frames.map((f) => f.name),
    };
    state.dirty = false;
    if (state.params.preview.page >= pages.length) state.params.preview.page = 0;
    emit("sheet");
  }

  function splitPages(positions, sheetW, sheetH, maxTex, pad) {
    const all = positions.map((_, i) => i);
    if (sheetW <= maxTex && sheetH <= maxTex) {
      return [{ page: 0, x0: 0, y0: 0, w: sheetW, h: sheetH, indices: all }];
    }
    const defs = [];
    if (sheetW > maxTex) {
      // split vertically by columns (e.g. oversized horizontal strip)
      const sorted = all.slice().sort((a, b) => positions[a].x - positions[b].x);
      let cur = null;
      for (const i of sorted) {
        const p = positions[i];
        if (!cur || p.x + p.w - cur.x0 > maxTex) {
          cur = { x0: p.x, y0: 0, w: 0, h: sheetH, indices: [] };
          defs.push(cur);
        }
        cur.indices.push(i);
        cur.w = Math.max(cur.w, p.x + p.w - cur.x0);
      }
      defs.forEach((d) => { d.w = Math.min(maxTex, d.w + pad); });
    } else {
      // split horizontally by bands of rows
      const sorted = all.slice().sort((a, b) => positions[a].y - positions[b].y || positions[a].x - positions[b].x);
      let cur = null;
      for (const i of sorted) {
        const p = positions[i];
        if (!cur || p.y + p.h - cur.y0 > maxTex) {
          cur = { x0: 0, y0: p.y, w: sheetW, h: 0, indices: [] };
          defs.push(cur);
        }
        cur.indices.push(i);
        cur.h = Math.max(cur.h, p.y + p.h - cur.y0);
      }
      defs.forEach((d) => { d.h = Math.min(maxTex, d.h + pad); });
    }
    return defs.map((d, i) => ({ ...d, page: i }));
  }

  function ensureSheet() {
    if (state.dirty || !state.sheet) rebuildSheet();
    return state.sheet;
  }

  /* ================= misc ================= */

  function status(msg) { emit("status", msg); }
  function toast(msg) { emit("toast", msg); }

  window.PF = window.PF || {};
  Object.assign(window.PF, {
    state, on, emit,
    addImageFiles, loadImageFrames,
    removeFrame, clearFrames, moveFrame, renameAll, setPivot,
    invalidate, rebuildSheet, ensureSheet, processFrame,
    commitHistory, initHistory, beginParamGesture, endParamGesture,
    undo, redo, historyState,
    status, toast,
  });
})();
