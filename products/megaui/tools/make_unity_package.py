#!/usr/bin/env python3
"""Build MegaUI-Unity-v1.0.0.unitypackage (tar.gz of GUID folders).

Unity .unitypackage layout:
  <guid>/pathinfo   original path (Assets/...)
  <guid>/asset.meta Unity importer YAML
  <guid>/asset      raw bytes (files only)

Contents: full 4x PNG sprite library (imported as Sprite), OFL fonts,
UI Toolkit USS/UXML starter, design tokens, docs, editor helper.

Usage:  python3 tools/make_unity_package.py
Output: dist/MegaUI-Unity-v1.0.0.unitypackage
"""
import hashlib
import os
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "dist", "kit")
VERSION = "1.0.0"
OUT = os.path.join(ROOT, "dist", f"MegaUI-Unity-v{VERSION}.unitypackage")

DEFAULT_IMPORTER = """fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

MONO_IMPORTER = """fileFormatVersion: 2
guid: {guid}
MonoImporter:
  externalObjects: {{}}
  serializedVersion: 2
  defaultReferences: []
  executionOrder: 0
  icon: {{instanceID: 0}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

FOLDER_META = """fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

SPRITE_IMPORTER = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMasterTextureLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 4096
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 16, y: 16, z: 16, w: 16}}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  shape: 0
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 4096
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: 
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  spritePackingTag: 
  pSDRemoveMatte: 0
  pSDShowRemoveMatteOption: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

USS = """/* MegaUI design tokens — UI Toolkit USS (variables + starter classes) */
:root {
    --mega-bg: #14100c;
    --mega-panel: #1e1813;
    --mega-panel2: #271f17;
    --mega-ink: #f0e6d2;
    --mega-muted: #a8987c;
    --mega-accent: #d4a94e;
    --mega-accent2: #f2cc7a;
    --mega-stroke: #7a5c2c;
    --mega-danger: #c0392b;
    --mega-good: #4e9a51;
    --mega-mana: #4f7bd8;
    --mega-radius: 8px;
    --mega-stroke-width: 2px;
}

.mega-root {
    background-color: var(--mega-bg);
    color: var(--mega-ink);
    font-size: 16px;
}

.mega-btn {
    background-color: var(--mega-accent);
    color: var(--mega-bg);
    border-width: var(--mega-stroke-width);
    border-color: var(--mega-accent);
    border-radius: var(--mega-radius);
    padding: 10px 28px;
    -unity-font-style: bold;
    letter-spacing: 2.4px;
    transition-property: background-color;
    transition-duration: 0.1s;
}

.mega-btn:hover { background-color: var(--mega-accent2); }
.mega-btn:active { background-color: var(--mega-stroke); }
.mega-btn:disabled { opacity: 0.45; }

.mega-btn--ghost {
    background-color: rgba(0, 0, 0, 0);
    color: var(--mega-ink);
    border-color: var(--mega-accent);
}

.mega-panel {
    background-color: var(--mega-panel);
    border-width: var(--mega-stroke-width);
    border-color: var(--mega-stroke);
    border-radius: var(--mega-radius);
    padding: 18px;
}

.mega-title {
    font-size: 22px;
    -unity-font-style: bold;
    letter-spacing: 2px;
    color: var(--mega-accent);
    margin-bottom: 8px;
}

.mega-chip {
    background-color: var(--mega-panel);
    border-width: 2px;
    border-color: var(--mega-accent2);
    border-radius: 999px;
    padding: 6px 16px;
    -unity-font-style: bold;
}

.mega-bar-track {
    background-color: var(--mega-panel2);
    border-radius: 4px;
    height: 24px;
}
.mega-bar-fill {
    background-color: var(--mega-danger);
    border-radius: 4px;
    height: 24px;
}
"""

UXML = """<ui:UXML xmlns:ui="UnityEngine.UIElements">
    <ui:VisualElement name="mega-root" class="mega-root mega-panel" style="padding:40px;">
        <ui:Label text="MEGAUI" class="mega-title"/>
        <ui:Label text="Game UI Design System — sample screen" style="margin-bottom:18px;"/>
        <ui:VisualElement style="flex-direction:row;">
            <ui:Button text="PLAY" class="mega-btn" style="margin-right:12px;"/>
            <ui:Button text="OPTIONS" class="mega-btn" style="margin-right:12px;"/>
            <ui:Button text="CANCEL" class="mega-btn mega-btn--ghost"/>
        </ui:VisualElement>
        <ui:VisualElement class="mega-bar-track" style="margin-top:20px;width:320px;">
            <ui:VisualElement class="mega-bar-fill" style="width:68%;"/>
        </ui:VisualElement>
        <ui:VisualElement style="flex-direction:row;margin-top:16px;">
            <ui:Label text="12,450" class="mega-chip" style="margin-right:10px;"/>
            <ui:Label text="386" class="mega-chip"/>
        </ui:VisualElement>
    </ui:VisualElement>
</ui:UXML>
"""

EDITOR_CS = """using UnityEditor;
using UnityEngine;

namespace MegaUI
{
    public static class MegaUIWindow
    {
        [MenuItem("Window/MegaUI/About")]
        public static void About()
        {
            EditorUtility.DisplayDialog("MegaUI",
                "MegaUI - Game UI Design System v%s\\n\\n" +
                "Sprites: Assets/MegaUI/Sprites/<theme>/<group>\\n" +
                "Styles: Assets/MegaUI/UI/MegaUI.uss (UI Toolkit)\\n" +
                "Sample: Assets/MegaUI/UI/Sample.uxml\\n" +
                "Fonts:  Assets/MegaUI/Fonts (Inter/Montserrat, OFL)\\n\\n" +
                "All artwork is original vector -> 4x PNG sprites, " +
                "imported as Sprite (single mode, 16px borders).",
                "OK");
        }
    }
}
""" % VERSION

README = """# MegaUI - Game UI Design System (Unity package)

## What's inside
- `Assets/MegaUI/Sprites/<theme>/<group>/*.png`
  Full 4x sprite library for 4 themes (darkfantasy, scifi, royal, pixel):
  buttons (9 shapes x 4 states x 4 kinds), bars, rings, slots, panels,
  windows, forms, decor, cards, leaderboard rows and 203 icons.
  All imported as **Sprite** (single mode, 16px sprite border for 9-slice).
- `Assets/MegaUI/UI/MegaUI.uss` + `Sample.uxml` — UI Toolkit starter with
  design-token variables and ready classes (.mega-btn, .mega-panel...).
- `Assets/MegaUI/Fonts/` — Inter + Montserrat TTF with **OFL-1.1** licenses.
- `Assets/MegaUI/design-tokens.json` — same tokens for tooling/web.
- `Assets/MegaUI/RECLOUR.md` — one-command recolor workflow.

## Quick start
1. Import this .unitypackage (Unity 2021.3+ recommended).
2. Drag any sprite from `Assets/MegaUI/Sprites/...` into a Canvas (uGUI)
   or reference it from UI Toolkit USS with `-unity-background-image`.
3. For UI Toolkit: open `Assets/MegaUI/UI/Sample.uxml`.
4. Recolor workflow: see `RECLOUR.md`.

## Notes
- Sprites use a shared 100 px/unit baseline; scale freely.
- 9-slice: sprite borders are pre-set to 16px — resize panels without
  redrawing art.
- Every file is original parametric vector art (no traced stock).
"""


def guid_for(path):
    return hashlib.md5(("MegaUI:" + path).encode()).hexdigest()


def importer_for(rel_dest):
    if rel_dest.endswith(".cs"):
        return MONO_IMPORTER
    if rel_dest.lower().endswith(".png"):
        return SPRITE_IMPORTER
    return DEFAULT_IMPORTER


def collect():
    """Yield (source_or_None, dest_under_Assets, inline_text_or_None)."""
    files = []
    # sprites
    png_root = os.path.join(KIT, "png4k")
    for dp, _, fns in os.walk(png_root):
        for fn in sorted(fns):
            if not fn.endswith(".png"):
                continue
            src = os.path.join(dp, fn)
            rel = os.path.relpath(src, png_root).replace(os.sep, "/")
            files.append((src, f"Assets/MegaUI/Sprites/{rel}", None))
    # fonts
    fdir = os.path.join(KIT, "fonts")
    if os.path.isdir(fdir):
        for fn in sorted(os.listdir(fdir)):
            ext = os.path.splitext(fn)[1].lower()
            if ext in (".ttf", ".txt"):
                files.append((os.path.join(fdir, fn),
                              f"Assets/MegaUI/Fonts/{fn}", None))
    # ui toolkit + tokens + docs
    files.append((None, "Assets/MegaUI/UI/MegaUI.uss", USS))
    files.append((None, "Assets/MegaUI/UI/Sample.uxml", UXML))
    files.append((None, "Assets/MegaUI/Editor/MegaUIWindow.cs", EDITOR_CS))
    tok = os.path.join(KIT, "tokens", "design-tokens.json")
    if os.path.isfile(tok):
        files.append((tok, "Assets/MegaUI/design-tokens.json", None))
    rec = os.path.join(KIT, "docs", "RECLOUR.md")
    if os.path.isfile(rec):
        files.append((rec, "Assets/MegaUI/RECLOUR.md", None))
    files.append((None, "Assets/MegaUI/README.md", README))
    return files


def main():
    items = collect()
    folders = set()
    for _, dest, _ in items:
        d = os.path.dirname(dest)
        while d and d != "Assets":
            folders.add(d)
            d = os.path.dirname(d)

    n_files = n_folders = 0
    with tarfile.open(OUT, "w:gz") as tar:
        def add_bytes(name, data):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            import io
            tar.addfile(info, io.BytesIO(data.encode() if isinstance(data, str) else data))

        for folder in sorted(folders):
            g = guid_for("folder:" + folder)
            add_bytes(f"{g}/pathname", folder)
            add_bytes(f"{g}/asset.meta", FOLDER_META.format(guid=g))
            n_folders += 1

        for src, dest, inline in items:
            g = guid_for(dest)
            data = inline.encode() if inline is not None else open(src, "rb").read()
            add_bytes(f"{g}/pathname", dest)
            add_bytes(f"{g}/asset.meta", importer_for(dest).format(guid=g))
            add_bytes(f"{g}/asset", data)
            n_files += 1

    size = os.path.getsize(OUT)
    print(f"folders: {n_folders}  files: {n_files}")
    print(f"-> {OUT}  ({size/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
