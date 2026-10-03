/* PixelForge — minimal ZIP writer (store method, no compression) */
(function () {
  "use strict";

  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(buf) {
    let c = 0xffffffff;
    for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  }

  /**
   * Build a ZIP blob from entries.
   * @param {{name:string, data:Uint8Array}[]} entries
   * @returns {Blob}
   */
  function makeZip(entries) {
    const encoder = new TextEncoder();
    const parts = [];
    const central = [];
    let offset = 0;

    for (const e of entries) {
      const nameBytes = encoder.encode(e.name);
      const data = e.data;
      const crc = crc32(data);

      const local = new Uint8Array(30 + nameBytes.length);
      const lv = new DataView(local.buffer);
      lv.setUint32(0, 0x04034b50, true); // local file header signature
      lv.setUint16(4, 20, true);         // version needed
      lv.setUint16(6, 0x0800, true);     // flags: UTF-8 names
      lv.setUint16(8, 0, true);          // method: store
      lv.setUint16(10, 0, true);         // mod time
      lv.setUint16(12, 0x21, true);      // mod date (1980-01-01)
      lv.setUint32(14, crc, true);
      lv.setUint32(18, data.length, true); // compressed size
      lv.setUint32(22, data.length, true); // uncompressed size
      lv.setUint16(26, nameBytes.length, true);
      lv.setUint16(28, 0, true);         // extra len
      local.set(nameBytes, 30);

      parts.push(local, data);

      const cd = new Uint8Array(46 + nameBytes.length);
      const cv = new DataView(cd.buffer);
      cv.setUint32(0, 0x02014b50, true); // central dir signature
      cv.setUint16(4, 20, true);         // version made by
      cv.setUint16(6, 20, true);         // version needed
      cv.setUint16(8, 0x0800, true);     // flags
      cv.setUint16(10, 0, true);         // method
      cv.setUint16(12, 0, true);         // time
      cv.setUint16(14, 0x21, true);      // date
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, nameBytes.length, true);
      cv.setUint16(30, 0, true);         // extra
      cv.setUint16(32, 0, true);         // comment
      cv.setUint16(34, 0, true);         // disk
      cv.setUint16(36, 0, true);         // internal attrs
      cv.setUint32(38, 0, true);         // external attrs
      cv.setUint32(42, offset, true);    // local header offset
      cd.set(nameBytes, 46);
      central.push(cd);

      offset += local.length + data.length;
    }

    const centralSize = central.reduce((s, c) => s + c.length, 0);
    const eocd = new Uint8Array(22);
    const ev = new DataView(eocd.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(4, 0, true);
    ev.setUint16(6, 0, true);
    ev.setUint16(8, entries.length, true);
    ev.setUint16(10, entries.length, true);
    ev.setUint32(12, centralSize, true);
    ev.setUint32(16, offset, true);
    ev.setUint16(20, 0, true);

    return new Blob([...parts, ...central, eocd], { type: "application/zip" });
  }

  window.PF = window.PF || {};
  window.PF.makeZip = makeZip;
  window.PF.crc32 = crc32;
})();
