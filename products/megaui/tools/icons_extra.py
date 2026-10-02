"""MegaUI icons batch 2 — original artwork on the shared 24x24 grid.

Every entry is hand-built geometry (no tracing). Helpers generate the
repetitive polygon families so counts grow without losing consistency.
"""
import math


def _star(points=5, r_out=10.0, r_in=4.6, cx=12, cy=12, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append(f"{cx + r*math.cos(a):.2f} {cy + r*math.sin(a):.2f}")
    return '<path d="M' + ' L'.join(pts) + ' Z"/>'


def _poly(n, r, cx=12, cy=12, rot=-90):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        pts.append(f"{cx + r*math.cos(a):.2f} {cy + r*math.sin(a):.2f}")
    return '<path d="M' + ' L'.join(pts) + ' Z"/>'


def _arrow(rot):
    return (f'<g transform="rotate({rot} 12 12)">'
            '<path d="M4 12 H17"/><path d="M13 7.5 L17.5 12 L13 16.5"/></g>')


_BASE_ARROW = ('<path d="M4 12 H17"/><path d="M13 7.5 L17.5 12 L13 16.5"/>')

ICONS_EXTRA = {
    # ---- directional arrows (8) ----
    "arrow_ur": _arrow(-45),
    "arrow_u": _arrow(-90),
    "arrow_ul": _arrow(-135),
    "arrow_l": _arrow(180),
    "arrow_dl": _arrow(135),
    "arrow_d": _arrow(90),
    "arrow_dr": _arrow(45),
    "chevron_u": '<path d="M5 15 L12 8 L19 15"/>',
    "chevron_d": '<path d="M5 9 L12 16 L19 9"/>',
    "chevron_l": '<path d="M15 5 L8 12 L15 19"/>',
    "chevron_r": '<path d="M9 5 L16 12 L9 19"/>',

    # ---- star family (procedural) ----
    "star4": _star(4, 10.5, 3.4),
    "star6": _star(6, 10.5, 5.2),
    "star8": _star(8, 10.5, 6.0),
    "sparkle": ('<path d="M12 3 Q13.5 10.5 21 12 Q13.5 13.5 12 21 '
                'Q10.5 13.5 3 12 Q10.5 10.5 12 3 Z"/>'),

    # ---- media ----
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1"/>',
    "skip_f": '<path d="M6 5.5 L15 12 L6 18.5 Z"/><path d="M17.5 5.5 V18.5"/>',
    "skip_b": '<path d="M18 5.5 L9 12 L18 18.5 Z"/><path d="M6.5 5.5 V18.5"/>',
    "repeat": ('<path d="M6 8 h10 a3 3 0 0 1 3 3 v1"/><path d="M9 5.5 L6 8 l3 2.5"/>'
               '<path d="M18 16 H8 a3 3 0 0 1 -3 -3 v-1"/><path d="M15 18.5 L18 16 l-3 -2.5"/>'),
    "shuffle": ('<path d="M4 7 h3 l10 10 h3"/><path d="M17 4.5 L20 7 L17 9.5"/>'
                '<path d="M4 17 h3 l3 -3"/><path d="M14 10 l3 -3"/><path d="M17 14.5 L20 17 L17 19.5"/>'),
    "record": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4" fill="HOLE"/>',
    "mic": ('<rect x="9" y="3" width="6" height="11" rx="3"/>'
            '<path d="M5.5 11.5 a6.5 6.5 0 0 0 13 0"/><path d="M12 18 v3 M8.5 21 h7"/>'),
    "camera": ('<path d="M3 8 h4 l2 -2.5 h6 L17 8 h4 v11 H3 Z"/><circle cx="12" cy="13" r="3.6"/>'),
    "image": ('<rect x="3.5" y="5" width="17" height="14" rx="2"/>'
              '<circle cx="9" cy="10" r="1.7"/><path d="M4.5 17.5 L10 12.5 l3.5 3 3 -2.5 3.5 3.5"/>'),
    "video": ('<rect x="3" y="6" width="12.5" height="12" rx="2"/>'
              '<path d="M15.5 10.5 L21 7.5 v9 L15.5 13.5 Z"/>'),

    # ---- system / files ----
    "save": ('<path d="M4 4 h13 l3 3 v13 H4 Z"/><path d="M7.5 4 v5 h8 V4"/>'
             '<rect x="7.5" y="13" width="9" height="7"/>'),
    "folder": '<path d="M3.5 6 h6 l2 2.5 h9 V19 H3.5 Z"/>',
    "file": ('<path d="M6 3.5 h8 l4 4 V20.5 H6 Z"/><path d="M14 3.5 v4 h4"/>'),
    "download": ('<path d="M12 4 V15"/><path d="M7.5 10.5 L12 15 L16.5 10.5"/>'
                 '<path d="M4.5 19.5 H19.5"/>'),
    "upload": ('<path d="M12 16 V5"/><path d="M7.5 9.5 L12 5 L16.5 9.5"/>'
               '<path d="M4.5 19.5 H19.5"/>'),
    "link": ('<path d="M9.5 14.5 L14.5 9.5"/><path d="M8 11 L5.5 13.5 a3.5 3.5 0 0 0 5 5 L13 16"/>'
             '<path d="M16 13 L18.5 10.5 a3.5 3.5 0 0 0 -5 -5 L11 8"/>'),
    "filter": '<path d="M3.5 5.5 H20.5 L14 13 V19.5 L10 17.5 V13 Z"/>',
    "layers": ('<path d="M12 3.5 L21 8.5 L12 13.5 L3 8.5 Z"/>'
               '<path d="M4.5 12.5 L12 16.8 L19.5 12.5" stroke-opacity="0.8"/>'
               '<path d="M4.5 16.5 L12 20.8 L19.5 16.5" stroke-opacity="0.6"/>'),
    "copy": ('<rect x="8" y="8" width="12" height="12" rx="2"/>'
             '<path d="M16 8 V6 a2 2 0 0 0 -2 -2 H6 a2 2 0 0 0 -2 2 v8 a2 2 0 0 0 2 2 h2"/>'),
    "grid": ('<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/>'
             '<rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/>'),
    "list": ('<path d="M8.5 6 H20 M8.5 12 H20 M8.5 18 H20"/>'
             '<circle cx="4.6" cy="6" r="1.3" fill="HOLE"/>'
             '<circle cx="4.6" cy="12" r="1.3" fill="HOLE"/>'
             '<circle cx="4.6" cy="18" r="1.3" fill="HOLE"/>'),
    "menu": '<path d="M4 6.5 H20 M4 12 H20 M4 17.5 H20" stroke-width="2.4"/>',
    "more": ('<circle cx="5.5" cy="12" r="1.7" fill="HOLE"/>'
             '<circle cx="12" cy="12" r="1.7" fill="HOLE"/>'
             '<circle cx="18.5" cy="12" r="1.7" fill="HOLE"/>'),
    "expand": ('<path d="M4 9.5 V4 h5.5 M14.5 4 H20 v5.5 M20 14.5 V20 h-5.5 M9.5 20 H4 v-5.5"/>'),
    "collapse": ('<path d="M9.5 4 V9.5 H4 M20 9.5 H14.5 V4 M14.5 20 V14.5 H20 M4 14.5 H9.5 V20"/>'),

    # ---- status / security ----
    "alert": ('<path d="M12 3.5 L21.5 20 H2.5 Z"/><path d="M12 9.5 V14.5"/>'
              '<circle cx="12" cy="17.3" r="1.3" fill="HOLE"/>'),
    "info": ('<circle cx="12" cy="12" r="8.6"/><path d="M12 11 V16.5"/>'
             '<circle cx="12" cy="7.8" r="1.3" fill="HOLE"/>'),
    "check_circle": ('<circle cx="12" cy="12" r="8.6"/><path d="M8 12.4 L10.9 15.3 L16.2 9.4"/>'),
    "x_circle": ('<circle cx="12" cy="12" r="8.6"/><path d="M9 9 L15 15 M15 9 L9 15"/>'),
    "unlock": ('<rect x="5" y="10.5" width="14" height="9.5" rx="2"/>'
               '<path d="M8 10.5 V7.6 a4 4 0 0 1 7.6 -1.8"/>'),
    "eye_off": ('<path d="M4 12 C6.5 8 9.2 6.2 12 6.2 s5.5 1.8 8 5.8 c-1 1.8 -2.3 3.1 -3.7 4"/>'
                '<path d="M6.5 15.6 C5.4 14.6 4.6 13.4 4 12"/>'
                '<circle cx="12" cy="12" r="2.6"/><path d="M4.5 4.5 L19.5 19.5"/>'),
    "wifi": ('<path d="M3.5 9 a12.5 12.5 0 0 1 17 0"/><path d="M6.5 12.4 a8.5 8.5 0 0 1 11 0"/>'
             '<path d="M9.5 15.8 a4.5 4.5 0 0 1 5 0"/>'
             '<circle cx="12" cy="19" r="1.5" fill="HOLE"/>'),
    "battery": ('<rect x="3" y="8" width="16" height="8" rx="1.6"/>'
                '<path d="M20.5 10.5 v3"/>'
                '<rect x="5" y="10" width="6" height="4" fill="HOLE" stroke="none"/>'),
    "cloud": ('<path d="M7.5 18 a4.4 4.4 0 0 1 .6 -8.7 a5.6 5.6 0 0 1 10.7 1.6 '
              'a3.6 3.6 0 0 1 -.8 7.1 Z"/>'),
    "cloud_rain": ('<path d="M7.5 15.5 a4.4 4.4 0 0 1 .6 -8.7 a5.6 5.6 0 0 1 10.7 1.6 '
                   'a3.6 3.6 0 0 1 -.8 7.1 Z"/><path d="M8.5 18 L7.5 21 M12.5 18 L11.5 21 M16.5 18 L15.5 21"/>'),

    # ---- RPG gear ----
    "helmet": ('<path d="M5 14 a7 7 0 0 1 14 0 v5 h-4 v-3 h-6 v3 H5 Z"/>'
               '<path d="M12 7.4 V14" stroke-opacity="0.7"/>'),
    "armor": ('<path d="M7 4.5 L12 6.5 L17 4.5 L20 8 v6.5 c0 3 -3.5 5 -8 6 '
              'c-4.5 -1 -8 -3 -8 -6 V8 Z"/><path d="M12 6.5 V19" stroke-opacity="0.6"/>'),
    "boots": ('<path d="M7 4 h5 v9 c0 2 1 3 3.5 3.6 l2.5 .9 v2.5 H7 Z"/>'
              '<path d="M7 17.5 h11" stroke-opacity="0.6"/>'),
    "gauntlet": ('<path d="M6.5 8.5 h11 v5.5 a5.5 5.5 0 0 1 -11 0 Z"/>'
                 '<path d="M6.5 8.5 L5 5.5 M9.5 8.5 L8.8 4.8 M12.5 8.5 V4.2 M15.5 8.5 L16.2 4.8"/>'),
    "ring_item": ('<circle cx="12" cy="14.5" r="5.5"/><path d="M9.5 9.5 L12 4.5 L14.5 9.5"/>'
                  '<path d="M9.5 9.5 H14.5"/>'),
    "amulet": ('<path d="M7 4 a7 7 0 0 0 10 0"/><path d="M12 10.5 L15.5 14 L12 19 L8.5 14 Z"/>'),
    "bow": ('<path d="M7 3.5 C16 7 16 17 7 20.5"/><path d="M7 3.5 L7 20.5"/>'
            '<path d="M5 12 H19"/><path d="M15.5 8.8 L19 12 L15.5 15.2"/>'),
    "dagger": ('<path d="M12 2.5 L14 6 V13.5 H10 V6 Z"/><path d="M8.5 13.5 h7"/>'
               '<path d="M12 13.5 v5"/><circle cx="12" cy="20" r="1.5"/>'),
    "greatsword": ('<path d="M11 1.8 h2 l2.4 4 V15 h-6.8 V5.8 Z"/>'
                   '<path d="M6.5 15 h11"/><path d="M12 15 v4.5"/>'
                   '<path d="M9 19.5 h6"/>'),
    "mace": ('<circle cx="12" cy="7" r="4.4"/>'
             '<path d="M12 7 l0 -3.6 M12 7 l3.1 -1.8 M12 7 l3.1 1.8 M12 7 l0 3.6 '
             'M12 7 l-3.1 1.8 M12 7 l-3.1 -1.8" stroke-opacity="0.9"/>'
             '<path d="M12 11.4 V20.5"/>'),
    "spear": ('<path d="M12 2 L14 6.5 L12 9 L10 6.5 Z"/><path d="M12 9 V21"/>'
              '<path d="M9.8 14 h4.4"/>'),
    "staff": ('<path d="M12 7.5 V21"/><circle cx="12" cy="5" r="3.4"/>'
              '<path d="M8.8 5 H4.5 M15.2 5 H19.5" stroke-opacity="0.7"/>'),
    "orb": ('<circle cx="12" cy="12" r="7.5"/><path d="M7.5 10.5 C9 8.5 11 7.8 13 8.4" '
            'stroke-opacity="0.8"/>'),
    "scroll": ('<path d="M6 4.5 h12 a2 2 0 0 1 2 2 v11 a2 2 0 0 1 -2 2 H6 Z"/>'
               '<path d="M6 4.5 a2 2 0 0 0 0 15"/><path d="M9 9 h6 M9 12.5 h6 M9 16 h4"/>'),
    "tome": ('<path d="M5 4.5 h10 a3 3 0 0 1 3 3 V19.5 H8 a3 3 0 0 1 -3 -3 Z"/>'
             '<path d="M8 4.5 V19.5" stroke-opacity="0.7"/><path d="M11 9 h4 M11 12.5 h4"/>'),
    "rune": ('<path d="M12 2.5 L19.5 7 v10 L12 21.5 L4.5 17 V7 Z"/>'
             '<path d="M12 7 L15.5 12 L12 17 L8.5 12 Z"/>'),

    # ---- resources ----
    "ore": ('<path d="M8.5 4.5 L15.5 4.5 L20 10 L17 19 H7 L4 10 Z"/>'
            '<path d="M8.5 4.5 L11 10 L7 19 M15.5 4.5 L13 10 L17 19 M4 10 H20" stroke-opacity="0.65"/>'),
    "ingot": ('<path d="M5.5 15 L8 9.5 H16 L18.5 15 Z"/><path d="M8 9.5 L9.5 6 H14.5 L16 9.5"/>'),
    "herb": ('<path d="M12 21 V9"/><path d="M12 12 C7 12 5.5 8.5 6 5.5 c3.5 .3 6 3 6 6.5"/>'
             '<path d="M12 15 c5 0 6.5 -3.5 6 -6.5 c-3.5 .3 -6 3 -6 6.5"/>'),
    "flower": ('<circle cx="12" cy="9" r="2.4"/>'
               '<path d="M12 6.6 a3.4 3.4 0 1 1 0 .1 M12 11.4 a3.4 3.4 0 1 1 0 -.1" stroke-opacity="0"/>'
               '<circle cx="12" cy="5.2" r="2.3"/><circle cx="15.8" cy="9" r="2.3"/>'
               '<circle cx="12" cy="12.8" r="2.3"/><circle cx="8.2" cy="9" r="2.3"/>'
               '<path d="M12 15 V21"/>'),
    "mushroom": ('<path d="M4.5 11.5 a7.5 6 0 0 1 15 0 Z"/>'
                 '<path d="M9.5 11.5 c0 4 -.8 6 -1.5 8.5 h8 c-.7 -2.5 -1.5 -4.5 -1.5 -8.5"/>'
                 '<circle cx="9.5" cy="8" r="1.4" fill="HOLE"/>'
                 '<circle cx="14.5" cy="7" r="1.4" fill="HOLE"/>'),
    "meat": ('<path d="M6 16.5 c-2.5 -2.5 -1.5 -7 2.5 -9.5 s8.5 -2.5 10.5 .5 '
             'c1.8 2.7 .3 6 -2.5 7.8 c-2.8 1.8 -8 1 -10.5 1.2 Z"/>'
             '<path d="M6 16.5 L3.5 19 a1.8 1.8 0 0 0 2.5 2.5 L8.5 19" />'),
    "bread": ('<path d="M4.5 12 a7.5 5.5 0 0 1 15 0 v6.5 H4.5 Z"/>'
              '<path d="M8.5 8.5 L7 12 M12 7.4 L12 12 M15.5 8.5 L17 12" stroke-opacity="0.7"/>'),
    "fish": ('<path d="M3.5 12 C6 7.5 10.5 6 14 7.5 c3 1.3 4.6 3.3 6.5 4.5 '
             'c-1.9 1.2 -3.5 3.2 -6.5 4.5 C10.5 18 6 16.5 3.5 12 Z"/>'
             '<path d="M3.5 12 L1.8 9 M3.5 12 L1.8 15"/>'
             '<circle cx="15.5" cy="11" r="1.2" fill="HOLE"/>'),
    "log": ('<ellipse cx="6.5" cy="12" rx="2.5" ry="6.5"/><path d="M6.5 5.5 H17.5 a2.5 6.5 0 0 1 0 13 H6.5"/>'
            '<ellipse cx="6.5" cy="12" rx="1.2" ry="3"/>'),
    "stone": ('<path d="M6.5 8.5 L11 4.5 L17 6 L19.5 12 L16 18.5 L9 19.5 L4.5 14 Z"/>'
              '<path d="M11 4.5 L12.5 11 L9 19.5 M17 6 L12.5 11 L19.5 12 M4.5 14 L12.5 11" '
              'stroke-opacity="0.6"/>'),
    "rope": ('<path d="M7 4 c4 2 4 4 0 6 s-4 4 0 6 s4 4 0 4"/>'
             '<path d="M17 4 c-4 2 -4 4 0 6 s4 4 0 6 s-4 4 0 4"/>'),
    "bone": ('<path d="M7.5 4.5 a2.5 2.5 0 1 1 2 3.6 L14.5 15 a2.5 2.5 0 1 1 -3.6 2 '
             'L5.8 10.5 a2.5 2.5 0 1 1 3.6 -2 L7.5 4.5 Z" transform="rotate(8 12 12)"/>'),
    "feather": ('<path d="M18.5 4.5 C10 6 5.5 11 5 19 c8 -.5 13 -5 14.5 -13.5 Z"/>'
                '<path d="M5 19 L14 9" stroke-opacity="0.8"/>'),
    "claw": ('<path d="M5 4 c1 6 4 10 9 12"/><path d="M9 3 c.6 5 3 9 7 11"/>'
             '<path d="M13 3.5 c.3 4 2 7.5 5 9.5"/>'),
    "fang": '<path d="M6 4.5 C7 11 9.5 16 12 19.5 C14.5 16 17 11 18 4.5 Z"/>',

    # ---- nature / world ----
    "tree": ('<path d="M12 3 L17.5 11 H14.5 L19 17.5 H5 L9.5 11 H6.5 Z"/>'
             '<path d="M12 17.5 V21"/>'),
    "mountain": ('<path d="M2.5 19 L9 6.5 L13 13 L15.5 8.5 L21.5 19 Z"/>'
                 '<path d="M9 6.5 L11 10.5 L7 10.5 Z" stroke-opacity="0.7"/>'),
    "wave": ('<path d="M3 10 c3 -3.5 6 -3.5 9 0 s6 3.5 9 0"/>'
             '<path d="M3 15 c3 -3.5 6 -3.5 9 0 s6 3.5 9 0"/>'),
    "tornado": ('<path d="M4 5.5 H20 M6 9.5 H18 M8 13.5 H16 M10 17.5 H14 M11.5 21 H12.5"/>'),
    "anchor": ('<circle cx="12" cy="5.5" r="2.5"/><path d="M12 8 V20.5"/>'
               '<path d="M7 12.5 H17"/><path d="M4.5 15.5 c1 4 4 5 7.5 5 s6.5 -1 7.5 -5"/>'),
    "tent": ('<path d="M12 4 L21 19.5 H3 Z"/><path d="M12 4 V19.5"/>'
             '<path d="M9 19.5 L12 13 L15 19.5"/>'),
    "campfire": ('<path d="M12 12.5 c-2.5 -2 -2 -5 1 -7.5 c.3 2 1.5 2.8 2.4 4 '
                 'c1.5 -1.2 1.8 -3 1.4 -4.5 c2 2.3 3 5 3 7.5 a5.8 5.8 0 0 1 -11.6 0 c0 -1.6 .7 -3 3.8 -5"/>'
                 '<path d="M5 20.5 L19 17.5 M5 17.5 L19 20.5"/>'),
    "castle": ('<path d="M4 20.5 V9 h3 V6 h3 v3 h4 V6 h3 v3 h3 v11.5 Z"/>'
               '<path d="M10 20.5 v-5 h4 v5"/>'),
    "tower": ('<path d="M8 20.5 V8.5 L12 4 l4 4.5 V20.5 Z"/><path d="M10.5 12 h3 M10.5 15.5 h3"/>'),
    "door": ('<path d="M6 20.5 V5.5 a1.5 1.5 0 0 1 1.5 -1.5 h9 a1.5 1.5 0 0 1 1.5 1.5 V20.5"/>'
             '<circle cx="15.5" cy="12.5" r="1.3" fill="HOLE"/>'),
    "bridge": ('<path d="M3 15 c4.5 -7 13.5 -7 18 0"/><path d="M3 15 H21"/>'
               '<path d="M7 15 V11 M12 15 V9.4 M17 15 V11"/><path d="M3 19 H21" stroke-opacity="0.6"/>'),

    # ---- rewards / meta ----
    "trophy": ('<path d="M7.5 4.5 h9 v5 a4.5 4.5 0 0 1 -9 0 Z"/>'
               '<path d="M7.5 6 H4.5 a3.5 3.5 0 0 0 3.5 4 M16.5 6 h3 a3.5 3.5 0 0 1 -3.5 4"/>'
               '<path d="M12 14 v3.5 M9 20.5 h6 M10 17.5 h4"/>'),
    "medal": ('<circle cx="12" cy="15" r="5"/><path d="M8.5 10.5 L6 3.5 h4 l2 4.5 2 -4.5 h4 L15.5 10.5"/>'
              + _star(5, 3.4, 1.5, 12, 15, -90)),
    "gift": ('<rect x="4" y="10" width="16" height="4"/><path d="M5.5 14 v6.5 h13 V14"/>'
             '<path d="M12 10 v10.5"/><path d="M12 10 c-4.5 0 -5.5 -5.5 -1.5 -5.5 c2.5 0 1.5 3.5 1.5 5.5 Z '
             'M12 10 c4.5 0 5.5 -5.5 1.5 -5.5 c-2.5 0 -1.5 3.5 -1.5 5.5 Z"/>'),
    "dice": ('<rect x="4.5" y="4.5" width="15" height="15" rx="3"/>'
             '<circle cx="9" cy="9" r="1.4" fill="HOLE"/>'
             '<circle cx="15" cy="9" r="1.4" fill="HOLE"/>'
             '<circle cx="12" cy="12" r="1.4" fill="HOLE"/>'
             '<circle cx="9" cy="15" r="1.4" fill="HOLE"/>'
             '<circle cx="15" cy="15" r="1.4" fill="HOLE"/>'),
    "ghost": ('<path d="M5 20.5 V11 a7 7 0 0 1 14 0 v9.5 l-2.5 -2.2 L14 20.5 '
              'l-2.5 -2.2 L9 20.5 L6.5 18.3 Z"/><circle cx="9.5" cy="10.5" r="1.3" fill="HOLE"/>'
              '<circle cx="14.5" cy="10.5" r="1.3" fill="HOLE"/>'),
    "crystal": ('<path d="M12 2.5 L18 8 L15.5 21 H8.5 L6 8 Z"/>'
                '<path d="M6 8 H18 M12 2.5 L9.5 8 L12 21 L14.5 8 Z" stroke-opacity="0.65"/>'),
    "heartbreak": ('<path d="M12 20.5 C5.5 15 3 10.5 5.5 7.5 C7.4 5.2 10.4 5.6 12 7.8 '
                   'C11.6 5.6 14.6 5.2 18.5 7.5 C21 10.5 18.5 15 12 20.5 Z"/>'
                   '<path d="M12 7.8 L10 12 l2.5 2 -1.5 4.5" stroke-opacity="0.9"/>'),
    "wings": ('<path d="M12 16 C9 10 5.5 6.5 2.5 5.5 c1 5 3.5 9 9.5 11 Z"/>'
              '<path d="M12 16 C15 10 18.5 6.5 21.5 5.5 c-1 5 -3.5 9 -9.5 11 Z"/>'
              '<path d="M12 8.5 V19" stroke-opacity="0.7"/>'),
    "mask": ('<path d="M4 8.5 c2.7 -1.5 5.3 -1.5 8 0 c2.7 -1.5 5.3 -1.5 8 0 c0 5.5 -3 9.5 '
             '-8 10.5 c-5 -1 -8 -5 -8 -10.5 Z"/><path d="M8 12.5 c1.2 1 2.4 1 3.5 0 '
             'M12.5 12.5 c1.2 1 2.4 1 3.5 0" stroke-opacity="0.8"/>'),
    "puzzle": ('<path d="M9.5 4.5 h5 v2 a2 2 0 1 0 0 4 v2 h2 a2 2 0 1 1 0 4 h-2 v3 h-5 '
               'v-2 a2 2 0 1 0 0 -4 v-2 h-2 a2 2 0 1 1 0 -4 h2 Z" transform="translate(0.5 0)"/>'),
    "hourglass": ('<path d="M6 3.5 H18 M6 20.5 H18"/>'
                  '<path d="M7 3.5 c0 5 5 6.5 5 8.5 s-5 3.5 -5 8.5"/>'
                  '<path d="M17 3.5 c0 5 -5 6.5 -5 8.5 s5 3.5 5 8.5"/>'),
    "compass": ('<circle cx="12" cy="12" r="8.6"/><path d="M15.5 8.5 L13.5 13.5 L8.5 15.5 '
                'L10.5 10.5 Z"/>'),
    "crown2": ('<path d="M4 16.5 L4 7.5 l4.5 4 L12 5 l3.5 6.5 4.5 -4 v9 Z"/>'
               '<path d="M4 16.5 H20" stroke-opacity="0.7"/>'),
    "scepter": ('<circle cx="12" cy="5" r="3"/><path d="M12 8 V21"/>'
                '<path d="M9 12.5 L12 10.5 L15 12.5" stroke-opacity="0.7"/>'),
    "scale": ('<path d="M12 4 V20 M7 20 H17"/><path d="M5 8 H19"/>'
              '<path d="M5 8 L2.8 13 a2.6 2.6 0 0 0 4.4 0 Z"/>'
              '<path d="M19 8 L16.8 13 a2.6 2.6 0 0 0 4.4 0 Z"/>'),
    "search_loc": ('<circle cx="12" cy="10" r="5.5"/><path d="M12 4.5 V2.8 M17.5 10 h1.7 '
                   'M6.8 10 H5.1"/><path d="M12 15.5 L9.5 21 h5 Z"/>'),
    "pin": ('<path d="M12 21 C7 15.5 5.5 12 5.5 9.5 a6.5 6.5 0 0 1 13 0 C18.5 12 17 15.5 12 21 Z"/>'
            '<circle cx="12" cy="9.5" r="2.4"/>'),
    "tag": ('<path d="M4 4.5 h7.5 L20.5 13.5 L13.5 20.5 L4.5 11.5 Z"/>'
            '<circle cx="8.8" cy="9.2" r="1.6"/>'),
    "wallet": ('<rect x="3.5" y="6.5" width="17" height="13" rx="2.5"/>'
               '<path d="M3.5 10 H16.5 a1.5 1.5 0 0 0 0 0"/>'
               '<circle cx="16.5" cy="13" r="1.4" fill="HOLE"/>'),
    "bank": ('<path d="M3.5 9 L12 4 L20.5 9 Z"/><path d="M5.5 9.5 V17 M9.8 9.5 V17 '
             'M14.2 9.5 V17 M18.5 9.5 V17"/><path d="M3.5 20.5 H20.5"/>'),
    "chart": ('<path d="M4 4 V20 H20"/><path d="M7.5 16.5 V12 M11.5 16.5 V8 M15.5 16.5 V11 '
              'M19 16.5 V6"/>'),
    "trending": ('<path d="M4 17 L9.5 11.5 L13 15 L20 8"/>'
                 '<path d="M15.5 8 H20 V12.5"/>'),
    "speech": ('<path d="M4.5 5.5 h15 v10.5 h-8.5 L7 20 v-4 H4.5 Z"/>'
               '<path d="M8 9.5 h8 M8 12.5 h5" stroke-opacity="0.8"/>'),
    "speech_dots": ('<path d="M4.5 5.5 h15 v10.5 h-8.5 L7 20 v-4 H4.5 Z"/>'
                    '<circle cx="9" cy="11" r="1.2" fill="HOLE"/>'
                    '<circle cx="12" cy="11" r="1.2" fill="HOLE"/>'
                    '<circle cx="15" cy="11" r="1.2" fill="HOLE"/>'),
    "mail": ('<rect x="3.5" y="5.5" width="17" height="13" rx="2"/>'
             '<path d="M4 7 L12 13 L20 7"/>'),
    "bell_off": ('<path d="M6.5 9.5 a5.5 5.5 0 0 1 8 -4.9 M17.5 10.5 v3 l1.5 2.5 H8"/>'
                 '<path d="M10 18.6 a2 2 0 0 0 4 0"/><path d="M4.5 4.5 L19.5 19.5"/>'),
    "power": ('<path d="M12 3.5 V11"/><path d="M7.2 6.5 a7.5 7.5 0 1 0 9.6 0"/>'),
    "terminal": ('<rect x="3.5" y="5" width="17" height="14" rx="2"/>'
                 '<path d="M7 10 L10 12.5 L7 15 M12.5 15.5 H17"/>'),
    "code": '<path d="M8.5 7.5 L3.5 12 L8.5 16.5 M15.5 7.5 L20.5 12 L15.5 16.5 M13.5 5 L10.5 19"/>',
    "palette": ('<path d="M12 3.5 a8.5 8.5 0 0 0 0 17 c1.7 0 2.2 -1.2 1.5 -2.2 '
                'c-.8 -1.2 0 -2.3 1.4 -2.3 H17 a4 4 0 0 0 4 -4 c0 -4.5 -4.1 -8.5 -9 -8.5 Z"/>'
                '<circle cx="8" cy="10" r="1.3" fill="HOLE"/>'
                '<circle cx="12" cy="7.5" r="1.3" fill="HOLE"/>'
                '<circle cx="16" cy="10" r="1.3" fill="HOLE"/>'),
    "brush": ('<path d="M14.5 4.5 l5 5 -7.5 7.5 -5 -5 Z"/><path d="M7 12 L4.5 16.5 '
              'c-1.2 2.2 .8 4.2 3 3 L12 17"/>'),
    "ruler": ('<rect x="3" y="8.5" width="18" height="7" rx="1.2" transform="rotate(-25 12 12)"/>'
              '<path d="M7.5 10.7 L8.5 13.2 M11 8.8 L12 11.3 M14.5 7 L15.5 9.5 '
              'M18 5.2 L19 7.7" stroke-opacity="0.85"/>'),
    "cog2": ('<path d="M12 8.2 a3.8 3.8 0 1 0 0 7.6 a3.8 3.8 0 0 0 0 -7.6 Z"/>'
             '<path d="M12 2.8 l1 2.6 2.7 -.6 .6 2.7 2.6 1 -1.4 2.4 1.4 2.4 -2.6 1 '
             '-.6 2.7 -2.7 -.6 -1 2.6 -1 -2.6 -2.7 .6 -.6 -2.7 -2.6 -1 1.4 -2.4 -1.4 -2.4 '
             '2.6 -1 .6 -2.7 2.7 .6 Z"/>'),
    "bug": ('<ellipse cx="12" cy="13.5" rx="5" ry="6"/><path d="M12 7.5 V19.5" stroke-opacity="0.7"/>'
            '<path d="M7 11 L3.5 9 M7 14 H3.5 M7 17 L4 19 M17 11 L20.5 9 M17 14 H20.5 M17 17 L20 19"/>'
            '<path d="M10 6.5 L8.5 4.5 M14 6.5 L15.5 4.5"/>'),
    "magic_wand2": ('<path d="M4.5 19.5 L14 10"/><path d="M16.5 3 l1.2 3 3 1.2 -3 1.2 '
                    '-1.2 3 -1.2 -3 -3 -1.2 3 -1.2 Z"/>'
                    '<path d="M20 13 l.7 1.7 1.7 .7 -1.7 .7 -.7 1.7 -.7 -1.7 -1.7 -.7 '
                    '1.7 -.7 Z"/>'),
    "portal": ('<ellipse cx="12" cy="12" rx="6.5" ry="9"/>'
               '<ellipse cx="12" cy="12" rx="3.2" ry="5.2" stroke-opacity="0.8"/>'
               '<path d="M12 3 V1.5 M12 21 V22.5" stroke-opacity="0.6"/>'),
    "ladder": ('<path d="M8 3.5 V20.5 M16 3.5 V20.5"/>'
               '<path d="M8 7 H16 M8 11 H16 M8 15 H16 M8 19 H16" stroke-opacity="0.85"/>'),
    "hammer_wrench": ('<path d="M14.5 6.5 a4 4 0 0 0 -5.4 5.2 L3.5 17.3 a2 2 0 0 0 2.8 2.8 '
                      'l5.6 -5.6 a4 4 0 0 0 5.2 -5.4 L14.5 11 13 10.8 12.8 9.3 Z"/>'),
    "paint_bucket": ('<path d="M5.5 10 L12 3.5 L18.5 10 a7.5 7.5 0 0 1 -13 0 Z"/>'
                     '<path d="M15.5 17 c1.5 2 2.5 3.4 2.5 4.5 a2.4 2.4 0 0 1 -4.8 0 '
                     'c0 -1.1 1 -2.5 2.3 -4.5" fill="none"/>'),
    "crop": ('<path d="M6.5 2.5 V17.5 H21.5"/><path d="M2.5 6.5 H17.5 V21.5"/>'),
    "eyedropper": ('<path d="M15.5 3.5 a2.8 2.8 0 0 1 4 4 L13 14 l-3 -3 Z"/>'
                   '<path d="M10 11 L4 17 v3 h3 l6 -6"/>'),
    "hash_tag": '<path d="M9 3.5 L7.5 20.5 M16.5 3.5 L15 20.5 M4 8.5 H20 M3.5 15.5 H19.5"/>',
    "at_sign": ('<circle cx="12" cy="12" r="4"/><path d="M16 8 v5 a2.8 2.8 0 0 0 5.5 0 V12 '
                'a9.5 9.5 0 1 0 -3.8 7.6"/>'),
    "globe": ('<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12 H20.6"/>'
              '<path d="M12 3.4 c2.6 2.4 4 5.4 4 8.6 s-1.4 6.2 -4 8.6 c-2.6 -2.4 -4 -5.4 -4 -8.6 '
              's1.4 -6.2 4 -8.6 Z"/>'),
    "send": '<path d="M20.5 3.5 L3.5 10.5 L10.5 13.5 L13.5 20.5 Z"/><path d="M10.5 13.5 L20.5 3.5"/>',
    "print": ('<path d="M7 8.5 V3.5 h10 v5"/><rect x="3.5" y="8.5" width="17" height="8" rx="2"/>'
              '<path d="M7 13.5 h10 V20.5 H7 Z"/><circle cx="16.5" cy="11.5" r="1.2" fill="HOLE"/>'),
    "monitor": ('<rect x="3" y="4.5" width="18" height="12" rx="2"/>'
                '<path d="M9 20.5 h6 M12 16.5 v4"/>'),
    "phone": ('<rect x="7" y="3" width="10" height="18" rx="2.5"/>'
              '<path d="M10.5 6 h3 M10.5 18 h3" stroke-opacity="0.8"/>'),
    "gamepad": ('<path d="M7.5 8.5 h9 a5.5 5.5 0 0 1 5.4 6.5 l-.5 2.6 a2.6 2.6 0 0 1 -4.7 1 '
                'L15 16 H9 l-1.7 2.1 a2.6 2.6 0 0 1 -4.7 -1 l-.5 -2.6 a5.5 5.5 0 0 1 5.4 -6.5 Z"/>'
                '<path d="M7 11.5 V14 M5.7 12.7 H8.3" stroke-width="1.8"/>'
                '<circle cx="15.8" cy="12" r="1.1" fill="HOLE"/>'
                '<circle cx="17.8" cy="14" r="1.1" fill="HOLE"/>'),
    "lightbulb": ('<path d="M8.5 14.5 a6 6 0 1 1 7 0 c-.9 .7 -1.2 1.6 -1.3 2.7 H9.8 '
                  'c-.1 -1.1 -.4 -2 -1.3 -2.7 Z"/><path d="M9.8 19.5 h4.4 M10.5 21.5 h3"/>'),
    "flash_drive": ('<rect x="8" y="8" width="8" height="12.5" rx="1.5"/>'
                    '<path d="M9.5 8 V4.5 a1 1 0 0 1 1 -1 h3 a1 1 0 0 1 1 1 V8"/>'
                    '<path d="M10.5 12 h3 M10.5 15 h3" stroke-opacity="0.8"/>'),
    "sd_card": ('<path d="M7 3.5 h7.5 L18 7.5 v13 H7 Z"/><path d="M9.5 4.5 v4 M12 4.5 v4 '
                'M14.5 4.5 v4" stroke-opacity="0.85"/>'),
    "cpu": ('<rect x="6.5" y="6.5" width="11" height="11" rx="1.5"/>'
            '<rect x="10" y="10" width="4" height="4"/>'
            '<path d="M9 3.5 V6.5 M15 3.5 V6.5 M9 17.5 V20.5 M15 17.5 V20.5 '
            'M3.5 9 H6.5 M3.5 15 H6.5 M17.5 9 H20.5 M17.5 15 H20.5"/>'),
    "memory": ('<rect x="4" y="7" width="16" height="10" rx="1.5"/>'
               '<path d="M7 17 v2.5 M11 17 v2.5 M15 17 v2.5 M7 10 v4 M11 10 v4 M15 10 v4" '
               'stroke-opacity="0.85"/>'),
    "keycard": ('<rect x="3.5" y="6.5" width="17" height="11" rx="2"/>'
                '<rect x="6" y="9.5" width="5" height="5"/>'
                '<path d="M13.5 10 H18 M13.5 13 H18" stroke-opacity="0.85"/>'),
    "coins_stack": ('<ellipse cx="12" cy="7" rx="7" ry="3"/>'
                    '<path d="M5 7 v4 c0 1.7 3.1 3 7 3 s7 -1.3 7 -3 V7"/>'
                    '<path d="M5 11 v4 c0 1.7 3.1 3 7 3 s7 -1.3 7 -3 v-4"/>'),
    "chest": ('<path d="M4 10.5 a8 4.5 0 0 1 16 0 V19.5 H4 Z"/><path d="M4 13 H20"/>'
              '<rect x="10.5" y="11.5" width="3" height="4.5"/>'),
    "book_open": ('<path d="M12 6.5 C10 4.5 7 4 4 5.5 V18.5 c3 -1.5 6 -1 8 1 '
                  'c2 -2 5 -2.5 8 -1 V5.5 c-3 -1.5 -6 -1 -8 1 Z"/>'
                  '<path d="M12 6.5 V20.5" stroke-opacity="0.7"/>'),
    "card_flip": ('<rect x="4.5" y="3.5" width="15" height="17" rx="2"/>'
                  '<path d="M12 7 l3.5 4 -3.5 4 -3.5 -4 Z"/>'),
    "helmet_visor": ('<path d="M4.5 12.5 a7.5 7.5 0 0 1 15 0 v4.5 H4.5 Z"/>'
                     '<path d="M7 13 h10" stroke-opacity="0.8"/>'
                     '<path d="M9.5 16 h5" stroke-opacity="0.6"/>'),
}

# procedural extras that need helpers at import time
ICONS_EXTRA["medal"] = ('<circle cx="12" cy="15" r="5"/>'
                        '<path d="M8.5 10.5 L6 3.5 h4 l2 4.5 2 -4.5 h4 L15.5 10.5"/>'
                        + _star(5, 3.4, 1.5, 12, 15, -90))

EXTRA_NAMES = list(ICONS_EXTRA.keys())
