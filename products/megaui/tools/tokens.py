"""MegaUI design tokens: 4 themes, geometry, state matrix."""

THEMES = {
    "darkfantasy": {
        "label": "Dark Fantasy",
        "bg": "#14100C", "panel": "#1E1813", "panel2": "#271F17",
        "ink": "#F0E6D2", "muted": "#A8987C",
        "accent": "#D4A94E", "accent2": "#F2CC7A", "stroke": "#7A5C2C",
        "danger": "#C0392B", "good": "#4E9A51", "mana": "#4F7BD8",
        "style": "fantasy",
    },
    "scifi": {
        "label": "Sci-Fi Neon",
        "bg": "#070B14", "panel": "#0D1526", "panel2": "#12203A",
        "ink": "#E6F4FF", "muted": "#6E8BA8",
        "accent": "#38E8FF", "accent2": "#FF4FD8", "stroke": "#1E3A5F",
        "danger": "#FF4464", "good": "#3DFFB5", "mana": "#7A5CFF",
        "style": "sci",
    },
    "royal": {
        "label": "Clean Royal",
        "bg": "#F4EFE4", "panel": "#FFFFFF", "panel2": "#F7F3EA",
        "ink": "#1C2333", "muted": "#6B7386",
        "accent": "#1F3A6E", "accent2": "#C9A227", "stroke": "#D8D0BE",
        "danger": "#B23A3A", "good": "#2F7D4F", "mana": "#3F6FD8",
        "style": "royal",
    },
    "pixel": {
        "label": "Pixel Retro",
        "bg": "#1A1C2C", "panel": "#2E2E48", "panel2": "#3D3D5C",
        "ink": "#F4F4F4", "muted": "#9B9BB5",
        "accent": "#FFCD75", "accent2": "#41A6F6", "stroke": "#0D0D1A",
        "danger": "#EF7D57", "good": "#4BC95F", "mana": "#41A6F6",
        "style": "pixel",
    },
}

# Geometry per style (px in 1x units)
GEO = {
    "fantasy": {"r": 8, "stroke": 2, "chamfer": 0, "px": 1},
    "sci":     {"r": 0, "stroke": 2, "chamfer": 14, "px": 1},
    "royal":   {"r": 12, "stroke": 2, "chamfer": 0, "px": 1},
    "pixel":   {"r": 0, "stroke": 4, "chamfer": 0, "px": 4},
}

STATES = ["normal", "hover", "pressed", "disabled"]

def state_tint(theme, state, base):
    """Return a color adjusted for the given interaction state."""
    if state == "normal":
        return base
    r, g, b = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
    if state == "hover":
        f = 1.18
    elif state == "pressed":
        f = 0.82
    else:  # disabled
        return "#6A6A72"
    r, g, b = [max(0, min(255, int(c * f))) for c in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"
