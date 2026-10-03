#!/usr/bin/env bash
# rebuild_all.sh — regenerate EVERYTHING after a /tmp or dist wipe.
# One command, atomic: env + tokens + kit + screens + renders + gallery +
# sheets + unity + QA + zips + github sync.
#
# Usage:  bash tools/rebuild_all.sh          (full ~15 min)
set -euo pipefail
MEGA="$(cd "$(dirname "$0")/.." && pwd)"
cd "$MEGA"

echo "== 1/8 environment =="
if [ ! -d /tmp/pffab/node_modules/puppeteer-core ]; then
  mkdir -p /tmp/pffab && (cd /tmp/pffab &&
    npm install --no-audit --no-fund puppeteer-core @sparticuz/chromium >/dev/null 2>&1)
fi
if [ ! -f /tmp/al2023x/lib/libnspr4.so ]; then
  node -e "
const zlib=require('zlib'),fs=require('fs'),path=require('path');
const dir='/tmp/pffab/node_modules/@sparticuz/chromium/bin';
fs.mkdirSync('/tmp/al2023x',{recursive:true});
for(const f of fs.readdirSync(dir)){
  if(f.endsWith('.tar.br'))
    fs.writeFileSync('/tmp/'+f.replace('.br',''),zlib.brotliDecompressSync(fs.readFileSync(path.join(dir,f))));
}"
  for t in /tmp/*.tar; do tar -xf "$t" -C /tmp/al2023x; done
fi
export LD_LIBRARY_PATH=/tmp/al2023x/lib

echo "== 2/8 tokens + fonts =="
python3 tools/make_tokens.py >/dev/null
F=dist/kit/fonts; mkdir -p "$F"
if [ ! -f "$F/Inter_400Regular.ttf" ]; then
  mkdir -p /tmp/fontpkg
  if [ ! -d /tmp/fontpkg/node_modules/@expo-google-fonts/inter ]; then
    (cd /tmp/fontpkg && npm install --no-audit --no-fund \
      @expo-google-fonts/inter @expo-google-fonts/montserrat >/dev/null 2>&1)
  fi
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/inter/400Regular/Inter_400Regular.ttf "$F/"
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/inter/600SemiBold/Inter_600SemiBold.ttf "$F/"
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/inter/700Bold/Inter_700Bold.ttf "$F/"
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/montserrat/700Bold/Montserrat_700Bold.ttf "$F/" 2>/dev/null \
    || cp /tmp/fontpkg/node_modules/@expo-google-fonts/montserrat/600SemiBold/Montserrat_600SemiBold.ttf "$F/"
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/inter/LICENSE_FONT "$F/OFL-Inter.txt"
  cp /tmp/fontpkg/node_modules/@expo-google-fonts/montserrat/LICENSE_FONT "$F/OFL-Montserrat.txt"
fi

echo "== 3/8 docs sync =="
mkdir -p dist/kit/docs
cp listing/README.md dist/kit/README.md
cp listing/RECLOUR.md dist/kit/docs/RECLOUR.md
cp listing/DESCRIPTION-plain.txt listing/TAGS.txt listing/FAB-ANSWERS.txt \
   listing/PRICE-AND-MEDIA.md listing/CONTENTS.txt listing/FAB-SUBMISSION-KIT.txt dist/kit/ 2>/dev/null || true

echo "== 4/8 kit + screens =="
python3 tools/make_kit.py | tail -1
python3 tools/make_screens.py

echo "== 5/8 renders (components + screens) =="
NODE_PATH=/tmp/pffab/node_modules node tools/render4k.js components 2>&1 | grep -E "components done|FATAL" | tail -1
NODE_PATH=/tmp/pffab/node_modules node tools/render4k.js screens 2>&1 | grep -E "screens done|FATAL" | tail -1

echo "== 6/8 gallery + sheets =="
python3 tools/make_gallery.py
python3 tools/make_review.py >/dev/null
NODE_PATH=/tmp/pffab/node_modules node tools/shot.js 2>&1 | grep -E "^done|FATAL" | tail -1

echo "== 7/8 unity + QA =="
python3 tools/make_unity_package.py | tail -1
[ -d /tmp/pfv4 ] || { python3 -m venv /tmp/pfv4 && /tmp/pfv4/bin/pip -q install pillow; }
/tmp/pfv4/bin/python tools/verify_kit.py > dist/kit/docs/TEST-REPORT.txt 2>&1
tail -2 dist/kit/docs/TEST-REPORT.txt

echo "== 8/8 complete zip =="
python3 - <<'EOF'
import zipfile, os
Z = 'dist/MegaUI-complete-v1.0.0.zip'
z = zipfile.ZipFile(Z, 'w', zipfile.ZIP_DEFLATED, compresslevel=6)
z.write('dist/kit/CONTENTS.txt', 'CONTENTS.txt')
for root, dirs, files in os.walk('dist/kit'):
    dirs[:] = [d for d in dirs if d != 'svg-darkfantasy-crimson']
    for f in files:
        p = os.path.join(root, f)
        if p == 'dist/kit/CONTENTS.txt':
            continue
        z.write(p, p)
for th in ('darkfantasy', 'scifi', 'royal', 'pixel'):
    z.write(f'build/review/review-{th}.png', f'sheets/review-{th}.png')
z.close()
size = os.path.getsize(Z)
assert size < 100_000_000, f'zip {size} exceeds GitHub 100MB'
print(f'complete zip: {size/1e6:.1f} MB')
EOF

echo "== done: syncing to GitHub =="
bash tools/sync_github.sh "megaui rebuild_all $(date +%F_%T)"
echo "ALL DONE"
