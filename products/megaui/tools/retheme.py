"""MegaUI re-theme tool — recolor any theme's whole SVG tree in one command.

Designers can restyle the entire kit without opening a vector editor:

  python3 tools/retheme.py --theme darkfantasy --set accent=#FF3B30 \\
      --set accent2=#FFD166 --out dist/kit/svg-darkfantasy-crimson

Only hex colors change; geometry, states and naming stay intact.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import THEMES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "dist", "kit", "svg")
COLOR_KEYS = ["bg", "panel", "panel2", "ink", "muted", "accent", "accent2",
              "stroke", "danger", "good", "mana"]


def parse_hex(v):
    v = v.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise SystemExit(f"bad color: #{v}")
    return "#" + v.lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True, choices=list(THEMES))
    ap.add_argument("--set", action="append", default=[],
                    metavar="KEY=#HEX",
                    help=f"one or more of: {', '.join(COLOR_KEYS)}")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--also-css", action="store_true",
                    help="write a patched megaui.css into the output dir")
    args = ap.parse_args()

    t = THEMES[args.theme]
    mapping = {}
    for kv in args.set:
        k, _, v = kv.partition("=")
        k = k.strip()
        if k not in COLOR_KEYS:
            raise SystemExit(f"unknown color key '{k}' (valid: {COLOR_KEYS})")
        mapping[t[k].lower()] = parse_hex(v)
        if len(t[k]) == 7:  # also swap #ABC shorthand if present
            mapping[t[k].lower()] = parse_hex(v)
    if not mapping:
        raise SystemExit("no --set given; nothing to do")

    src = os.path.join(SVG, args.theme)
    if not os.path.isdir(src):
        raise SystemExit(f"kit not found: {src} (run make_kit.py first)")
    n = 0
    for dirpath, _, files in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        dst = os.path.join(args.out, rel)
        os.makedirs(dst, exist_ok=True)
        for fn in files:
            if not fn.endswith(".svg"):
                continue
            p = os.path.join(dirpath, fn)
            s = open(p).read()
            for old, new in mapping.items():
                s = re.sub(re.escape(old), new, s, flags=re.I)
            open(os.path.join(dst, fn), "w").write(s)
            n += 1

    if args.also_css:
        css = [":root{"]
        for c in COLOR_KEYS:
            val = mapping.get(t[c].lower(), t[c])
            css.append(f"  --mega-{args.theme}-{c}: {val};")
        css.append("}")
        with open(os.path.join(args.out, "megaui.css"), "w") as f:
            f.write("\n".join(css) + "\n")

    print(f"re-themed {n} SVGs -> {args.out}")
    print("changed:", ", ".join(f"{k}=>{v}" for k, v in mapping.items()))


if __name__ == "__main__":
    main()
