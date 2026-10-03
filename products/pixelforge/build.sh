#!/usr/bin/env bash
# PixelForge release builder → dist/PixelForge-vX.Y.Z.zip
set -euo pipefail
cd "$(dirname "$0")"

VER="${1:-1.0.0}"
OUT="dist"
STAGE="$(mktemp -d)"

cp index.html style.css README.md LICENSE.txt CHANGELOG.md "$STAGE/"
cp -r js "$STAGE"/; cp THIRD-PARTY.txt "$STAGE"/

(cd "$STAGE" && zip -qr "PixelForge-v${VER}.zip" .)
mkdir -p "$OUT"
mv "$STAGE/PixelForge-v${VER}.zip" "$OUT/"
rm -rf "$STAGE"

echo "Built $OUT/PixelForge-v${VER}.zip"
unzip -l "$OUT/PixelForge-v${VER}.zip"
