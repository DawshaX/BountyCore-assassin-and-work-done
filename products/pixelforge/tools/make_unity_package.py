#!/usr/bin/env python3
"""Build PixelForge-Unity-*.unitypackage (tar.gz of GUID folders).

Unity's .unitypackage format:
  <guid>/pathinfo   original path (e.g. Assets/PixelForge/index.html)
  <guid>/asset.meta Unity importer metadata (YAML, carries the GUID)
  <guid>/asset      raw file bytes (files only; folders have no asset)

Usage:  python3 tools/make_unity_package.py
Output: dist/PixelForge-Unity-v1.1.3.unitypackage
"""
import io
import os
import sys
import tarfile
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "1.1.3"
OUT = os.path.join(ROOT, "dist", f"PixelForge-Unity-v{VERSION}.unitypackage")

# (source path relative to products/pixelforge, destination under Assets/)
FILES = [
    # The full offline web app
    ("index.html", "Assets/PixelForge/WebApp/index.html"),
    ("style.css", "Assets/PixelForge/WebApp/style.css"),
    ("js/core.js", "Assets/PixelForge/WebApp/js/core.js"),
    ("js/exporters.js", "Assets/PixelForge/WebApp/js/exporters.js"),
    ("js/palettes.js", "Assets/PixelForge/WebApp/js/palettes.js"),
    ("js/ui.js", "Assets/PixelForge/WebApp/js/ui.js"),
    ("js/zip.js", "Assets/PixelForge/WebApp/js/zip.js"),
    ("js/vendor/gif-tools.js", "Assets/PixelForge/WebApp/js/vendor/gif-tools.js"),
    ("js/vendor/gifenc.LICENSE", "Assets/PixelForge/WebApp/js/vendor/gifenc.LICENSE"),
    ("js/vendor/gifuct-js.LICENSE", "Assets/PixelForge/WebApp/js/vendor/gifuct-js.LICENSE"),
    ("README.md", "Assets/PixelForge/WebApp/README.md"),
    # Unity integration
    ("unity/Editor/PixelForgeLauncher.cs", "Assets/PixelForge/Editor/PixelForgeLauncher.cs"),
    ("unity/README.md", "Assets/PixelForge/README.md"),
    # Docs
    ("LICENSE.txt", "Assets/PixelForge/LICENSE.txt"),
    ("CHANGELOG.md", "Assets/PixelForge/CHANGELOG.md"),
    ("THIRD-PARTY.txt", "Assets/PixelForge/THIRD-PARTY.txt"),
]

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


def importer_for(path):
    if path.endswith(".cs"):
        return MONO_IMPORTER
    return DEFAULT_IMPORTER


def all_paths():
    """Collect every file + every folder directory, preserving order."""
    folders, files = [], []
    seen_folders = set()

    def add_folder(p):
        if p == "Assets" or not p:
            return
        while p not in seen_folders:
            seen_folders.add(p)
            parent = os.path.dirname(p)
            if parent and parent != p:
                add_folder(parent)
            folders.append(p)

    for _, dest in FILES:
        add_folder(os.path.dirname(dest))
        files.append(dest)
    return folders, files


def main():
    folders, file_paths = all_paths()
    guids = {p: uuid.uuid4().hex for p in list(folders) + list(file_paths)}
    if len(set(guids.values())) != len(guids):
        sys.exit("GUID collision")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    src_by_dest = {dest: src for src, dest in FILES}

    with tarfile.open(OUT, "w:gz", format=tarfile.USTAR_FORMAT) as tar:
        def add_bytes(name, data):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))

        for path in list(folders) + list(file_paths):
            g = guids[path]
            is_dir = path in folders
            meta = (FOLDER_META if is_dir else importer_for(path)).format(guid=g)
            add_bytes(f"{g}/pathinfo", path.encode("utf-8"))
            add_bytes(f"{g}/asset.meta", meta.encode("utf-8"))
            if not is_dir:
                with open(os.path.join(ROOT, src_by_dest[path]), "rb") as f:
                    add_bytes(f"{g}/asset", f.read())

    # ---- validate what we wrote ----
    names, paths_found, dup = [], set(), False
    with tarfile.open(OUT, "r:gz") as tar:
        for m in tar.getmembers():
            names.append(m.name)
            if m.name.endswith("/pathinfo"):
                p = tar.extractfile(m).read().decode("utf-8")
                if p in paths_found:
                    dup = True
                paths_found.add(p)
        guid_dirs = {n.split("/")[0] for n in names}
        for g in guid_dirs:
            have = {n.split("/")[1] for n in names if n.startswith(g + "/")}
            if "pathinfo" not in have or "asset.meta" not in have:
                sys.exit(f"incomplete entry {g}: {have}")
    missing_files = [d for _, d in FILES if d not in paths_found]
    missing_asset = []
    for _, dest in FILES:
        g = guids[dest]
        if f"{g}/asset" not in names:
            missing_asset.append(dest)
    if missing_files or missing_asset or dup:
        sys.exit(f"validation failed missing={missing_files} no-asset={missing_asset} dup={dup}")

    size = os.path.getsize(OUT)
    print(f"wrote {OUT} ({size} bytes)")
    print(f"entries: {len(guid_dirs)} guid folders, {len(file_paths)} files, {len(folders)} folders")


if __name__ == "__main__":
    main()
