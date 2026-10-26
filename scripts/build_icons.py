#!/usr/bin/env python3
"""Render the Pomodoro98 icons from the pixel art in scripts/icon_art.py.

Writes the scalable SVG and the 64/128/256/512 px PNGs used for the launcher
and Flathub, plus the three 64 px window icons (focus, rest, and a grey idle
variant). PNG output needs Pillow: ``python3 -m pip install Pillow``.

Run from anywhere: ``python3 scripts/build_icons.py``
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icon_art import HEIGHT, PALETTE, TOMATO, WIDTH  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HICOLOR = ROOT / "flatpak" / "icons" / "hicolor"
WINDOW_ICONS = ROOT / "src" / "pomodoro98" / "icons"
APP_ID = "io.github.phni.Pomodoro98"
MARGIN = 2  # transparent pixels around the window on each side
LAUNCHER_SIZES = (64, 128, 256, 512)


def button(glyph):
    """A 6x5 title-bar button: light top-left edge, grey bottom-right, black glyph."""
    rows = ["wwwwwg", "wllllg", "wllllg", "wllllg", "gggggg"]
    rows = [list(r) for r in rows]
    marks = {
        "minimize": [(3, 1), (3, 2), (3, 3)],
        "maximize": [
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 1),
            (2, 4),
            (3, 1),
            (3, 2),
            (3, 3),
            (3, 4),
        ],
        "close": [(1, 1), (1, 3), (2, 2), (3, 1), (3, 3)],
    }[glyph]
    for y, x in marks:
        rows[y][x] = "k"
    return rows


def window():
    """Return the icon as rows of palette keys ("." in TOMATO becomes window grey)."""
    px = [["l"] * WIDTH for _ in range(HEIGHT)]

    def rect(x0, y0, x1, y1, key):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px[y][x] = key

    # Outer frame: black edge, then light top/left and grey bottom/right bevels.
    rect(0, 0, WIDTH - 1, 0, "k")
    rect(0, HEIGHT - 1, WIDTH - 1, HEIGHT - 1, "k")
    rect(0, 0, 0, HEIGHT - 1, "k")
    rect(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1, "k")
    rect(1, 1, WIDTH - 2, 1, "s")
    rect(1, 1, 1, HEIGHT - 2, "s")
    rect(1, HEIGHT - 2, WIDTH - 2, HEIGHT - 2, "g")
    rect(WIDTH - 2, 1, WIDTH - 2, HEIGHT - 2, "g")
    # Title bar with minimize, maximize, and close buttons.
    rect(3, 3, WIDTH - 4, 9, "n")
    for x0, glyph in ((36, "minimize"), (43, "maximize"), (50, "close")):
        for dy, row in enumerate(button(glyph)):
            for dx, key in enumerate(row):
                px[4 + dy][x0 + dx] = key
    # Sunken client area holding the tomato.
    rect(3, 11, WIDTH - 4, 11, "g")
    rect(3, 11, 3, HEIGHT - 4, "g")
    rect(3, HEIGHT - 4, WIDTH - 4, HEIGHT - 4, "s")
    rect(WIDTH - 4, 11, WIDTH - 4, HEIGHT - 4, "s")
    for dy, row in enumerate(TOMATO):
        for dx, key in enumerate(row):
            px[12 + dy][4 + dx] = "l" if key == "." else key
    return ["".join(r) for r in px]


def svg(rows):
    size = max(WIDTH, HEIGHT) + 2 * MARGIN
    ox, oy = (size - WIDTH) // 2, (size - HEIGHT) // 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        'width="512" height="512" shape-rendering="crispEdges">'
    ]
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            key, start = row[x], x
            while x < len(row) and row[x] == key:
                x += 1
            out.append(
                f'<rect x="{ox + start}" y="{oy + y}" width="{x - start}" height="1" '
                f'fill="{PALETTE[key]}"/>'
            )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def png(rows, size, grey=False):
    from PIL import Image

    canvas = max(WIDTH, HEIGHT) + 2 * MARGIN
    ox, oy = (canvas - WIDTH) // 2, (canvas - HEIGHT) // 2
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            r, g, b = (int(PALETTE[key][i : i + 2], 16) for i in (1, 3, 5))
            if grey:
                r = g = b = round(0.299 * r + 0.587 * g + 0.114 * b)
            img.putpixel((ox + x, oy + y), (r, g, b, 255))
    # Scale up with crisp pixels, then down smoothly to the exact size.
    big = img.resize((canvas * 16, canvas * 16), Image.NEAREST)
    return big.resize((size, size), Image.LANCZOS)


def main():
    rows = window()
    scalable = HICOLOR / "scalable" / "apps"
    scalable.mkdir(parents=True, exist_ok=True)
    (scalable / f"{APP_ID}.svg").write_text(svg(rows))
    for size in LAUNCHER_SIZES:
        out = HICOLOR / f"{size}x{size}" / "apps"
        out.mkdir(parents=True, exist_ok=True)
        png(rows, size).save(out / f"{APP_ID}.png", optimize=True)
    png(rows, 64).save(WINDOW_ICONS / "icon.png", optimize=True)
    png(rows, 64).save(WINDOW_ICONS / "icon_rest.png", optimize=True)
    png(rows, 64, grey=True).save(WINDOW_ICONS / "icon_idle.png", optimize=True)
    print("Icons written to", HICOLOR.relative_to(ROOT), "and", WINDOW_ICONS.relative_to(ROOT))


if __name__ == "__main__":
    main()
