#!/usr/bin/env python3
"""MegaUI kit verification suite (tests).

Checks structural integrity, counts, XML validity, render outputs,
tokens, retheme round-trip and the Unity package.

Usage: python3 tools/verify_kit.py
"""
import json
import os
import subprocess
import sys
import tarfile
import xml.dom.minidom as minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "dist", "kit")
SVG = os.path.join(KIT, "svg")
PNG = os.path.join(KIT, "png4k")
SCREENS = os.path.join(KIT, "screens")

FAILED = []
PASSED = 0


def check(name, ok, detail=""):
    global PASSED
    if ok:
        PASSED += 1
        print(f"  ok  {name}")
    else:
        FAILED.append(name)
        print(f"FAIL  {name}  {detail}")


def main():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from tokens import THEMES

    print("== manifest ==")
    mpath = os.path.join(KIT, "manifest.json")
    check("manifest.json exists", os.path.isfile(mpath))
    man = json.load(open(mpath))

    print("== svg tree ==")
    svg_files = []
    for dp, _, fns in os.walk(SVG):
        svg_files += [os.path.join(dp, f) for f in fns if f.endswith(".svg")]
    check("manifest total == fs count", man["total"] == len(svg_files),
          f'{man["total"]} vs {len(svg_files)}')
    check(">= 2600 svg components", len(svg_files) >= 2600, str(len(svg_files)))
    for th in THEMES:
        n = len([f for f in svg_files if f"/{th}/" in f])
        check(f"{th}: >=500 svgs", n >= 500, str(n))

    print("== svg xml validity (sample + icons all) ==")
    bad = []
    icons = [f for f in svg_files if f"/icons/" in f]
    sample = [f for f in svg_files if "/buttons/" in f][:64] + icons
    for f in sample:
        try:
            minidom.parse(f)
        except Exception as e:
            bad.append((f, str(e)[:60]))
    check(f"xml valid ({len(sample)} files)", not bad, str(bad[:3]))

    print("== png4k mirror ==")
    png_files = []
    for dp, _, fns in os.walk(PNG):
        png_files += [os.path.join(dp, f) for f in fns if f.endswith(".png")]
    check("every svg has a 4x png", len(png_files) == len(svg_files),
          f"{len(png_files)} vs {len(svg_files)}")

    print("== icons ==")
    import svgkit as K
    check(">=210 base icons", len(K.ICON_NAMES) >= 210, str(len(K.ICON_NAMES)))
    check("icon names unique", len(set(K.ICON_NAMES)) == len(K.ICON_NAMES))

    print("== buttons matrix ==")
    bdir = os.path.join(SVG, "darkfantasy", "buttons")
    n_btn = len(os.listdir(bdir)) if os.path.isdir(bdir) else 0
    check("buttons/theme >=150", n_btn >= 150, str(n_btn))

    print("== screens ==")
    n_html = n_png = 0
    from PIL import Image
    dims_ok = True
    for th in THEMES:
        d = os.path.join(SCREENS, th)
        hs = [f for f in os.listdir(d) if f.endswith(".html")]
        ps = [f for f in os.listdir(d) if f.endswith(".png")]
        n_html += len(hs)
        n_png += len(ps)
        check(f"{th}: 21 screens", len(hs) == 21 and len(ps) == 21,
              f"{len(hs)} html / {len(ps)} png")
        if ps:
            im = Image.open(os.path.join(d, ps[0]))
            if im.size != (3840, 2160):
                dims_ok = False
    check("screen pngs are 4K (3840x2160)", dims_ok)
    check("84 screens total", n_html == 84 and n_png == 84)

    print("== tokens ==")
    tjson = os.path.join(KIT, "tokens", "design-tokens.json")
    tcss = os.path.join(KIT, "tokens", "megaui.css")
    check("design-tokens.json valid", os.path.isfile(tjson))
    tok = json.load(open(tjson))
    check("tokens cover 4 themes", len(tok.get("themes", {})) == 4)
    css = open(tcss).read()
    check("css tokens cover 4 themes",
          all(f"--mega-{th}-accent" in css for th in THEMES))

    print("== fonts + license ==")
    fdir = os.path.join(KIT, "fonts")
    ttfs = [f for f in os.listdir(fdir) if f.endswith(".ttf")]
    ofls = [f for f in os.listdir(fdir) if f.startswith("OFL")]
    check(">=3 ttf fonts", len(ttfs) >= 3, str(ttfs))
    check("OFL licenses present", len(ofls) >= 2, str(ofls))

    print("== retheme round-trip ==")
    out = os.path.join(ROOT, "build", "_retheme_test")
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "retheme.py"),
         "--theme", "pixel", "--set", "accent=#12AB34",
         "--out", out],
        capture_output=True, text=True)
    ok = r.returncode == 0
    check("retheme runs", ok, r.stderr[-200:])
    if ok:
        f = os.path.join(out, "buttons", "standard-primary-normal.svg")
        check("retheme applied color",
              os.path.isfile(f) and "#12ab34" in open(f).read().lower())

    print("== unity package ==")
    import glob
    ups = glob.glob(os.path.join(ROOT, "dist", "MegaUI-Unity-*.unitypackage"))
    check("unitypackage exists", bool(ups))
    if ups:
        t = tarfile.open(ups[0])
        names = t.getnames()
        check("unitypackage >=2400 groups", len(names) >= 7200, str(len(names)))
        paths = [t.extractfile(n).read().decode(errors="ignore")
                 for n in names if n.endswith("pathname")]
        check("contains Assets/ paths", any(p.startswith("Assets/MegaUI") for p in paths))
        check("contains sprites", sum(1 for p in paths if p.endswith(".png")) >= 2000)
        check("contains .uss + .uxml",
              any(p.endswith("MegaUI.uss") for p in paths) and
              any(p.endswith("Sample.uxml") for p in paths))
        check("contains .cs editor script",
              any(p.endswith(".cs") for p in paths))
        check("contains OFL font licenses",
              any("OFL-" in p for p in paths))

    print("== docs ==")
    for f in ("README.md",):
        check(f"kit/{f}", os.path.isfile(os.path.join(KIT, f)))
    check("docs/RECLOUR.md", os.path.isfile(os.path.join(KIT, "docs", "RECLOUR.md")))

    print()
    print(f"PASSED: {PASSED}   FAILED: {len(FAILED)}")
    if FAILED:
        for f in FAILED:
            print("  -", f)
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
