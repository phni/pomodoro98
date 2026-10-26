#!/usr/bin/env python3
"""Render the Pomodoro98 icons from the pixel art in scripts/icon_art.py.

Writes the scalable SVG and the 64/128/256/512 px PNGs used for the launcher
and Flathub, plus the three 64 px window icons (focus, rest, and a grey idle
variant). PNG output needs Pillow: ``python3 -m pip install Pillow``.

The icon is drawn on a grid SCALE times finer than the art: each tomato pixel
becomes a SCALE x SCALE block, while the title-bar buttons use the finer grid
so they are exactly square with their glyphs centred.

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
SCALE = 4  # fine grid units per art pixel
MARGIN = 2  # transparent art pixels around the window on each side
LAUNCHER_SIZES = (64, 128, 256, 512)

# Title-bar buttons on the fine grid, measured from the original artwork:
# square 24x24 boxes, 3 units apart, vertically centred in the title bar.
BUTTON_SIZE = 24
BUTTON_BEVEL = 3  # white top/left highlight and grey bottom/right shadow
BUTTON_TOP = 14
BUTTONS = ((147, "minimize"), (174, "maximize"), (201, "close"))


class Canvas:
    def __init__(self):
        self.w, self.h = WIDTH * SCALE, HEIGHT * SCALE
        self.px = [["l"] * self.w for _ in range(self.h)]

    def fine(self, x0, y0, x1, y1, key):
        """Fill fine-grid cells x0..x1, y0..y1 (inclusive)."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px[y][x] = key

    def art(self, x0, y0, x1, y1, key):
        """Fill art pixels x0..x1, y0..y1 (inclusive)."""
        self.fine(x0 * SCALE, y0 * SCALE, (x1 + 1) * SCALE - 1, (y1 + 1) * SCALE - 1, key)


def draw_button(c, x0, glyph):
    """Win98 button: mitred white/grey bevel and a black glyph centred in the box."""
    n, bevel, y0 = BUTTON_SIZE, BUTTON_BEVEL, BUTTON_TOP
    for dy in range(n):
        for dx in range(n):
            right, bottom = n - 1 - dx, n - 1 - dy
            if min(dx, dy, right, bottom) >= bevel:
                key = "l"  # face
            elif dx < bevel and bottom < bevel:  # bottom-left corner: split on the diagonal
                key = "w" if dx < bottom else "g"
            elif dy < bevel and right < bevel:  # top-right corner: split on the diagonal
                key = "w" if dy < right else "g"
            elif dx < bevel or dy < bevel:
                key = "w"
            else:
                key = "g"
            c.px[y0 + dy][x0 + dx] = key
    # Every glyph fills the same 12x12 box with 6 units of face on each side.
    gx, gy = x0 + 6, y0 + 6
    if glyph == "minimize":
        c.fine(gx, gy + 9, gx + 11, gy + 11, "k")  # bar along the bottom of the box
    elif glyph == "maximize":
        c.fine(gx, gy, gx + 11, gy + 11, "k")
        c.fine(gx + 2, gy + 2, gx + 9, gy + 9, "l")
    else:  # close: four corner squares and a centre square
        for cx, cy in ((0, 0), (8, 0), (4, 4), (0, 8), (8, 8)):
            c.fine(gx + cx, gy + cy, gx + cx + 3, gy + cy + 3, "k")


def window():
    """Return the icon as rows of palette keys on the fine grid."""
    c = Canvas()
    w, h = WIDTH - 1, HEIGHT - 1
    # Outer frame: black edge, then light top/left and grey bottom/right bevels.
    c.art(0, 0, w, 0, "k")
    c.art(0, h, w, h, "k")
    c.art(0, 0, 0, h, "k")
    c.art(w, 0, w, h, "k")
    c.art(1, 1, w - 1, 1, "s")
    c.art(1, 1, 1, h - 1, "s")
    c.art(1, h - 1, w - 1, h - 1, "g")
    c.art(w - 1, 1, w - 1, h - 1, "g")
    # Title bar and its buttons.
    c.art(3, 3, w - 3, 9, "n")
    for x0, glyph in BUTTONS:
        draw_button(c, x0, glyph)
    # Sunken client area holding the tomato.
    c.art(3, 11, w - 3, 11, "g")
    c.art(3, 11, 3, h - 3, "g")
    c.art(3, h - 3, w - 3, h - 3, "s")
    c.art(w - 3, 11, w - 3, h - 3, "s")
    for dy, row in enumerate(TOMATO):
        for dx, key in enumerate(row):
            c.art(4 + dx, 12 + dy, 4 + dx, 12 + dy, "l" if key == "." else key)
    return ["".join(r) for r in c.px]


def svg(rows):
    size = (max(WIDTH, HEIGHT) + 2 * MARGIN) * SCALE
    ox = (size - WIDTH * SCALE) // 2
    oy = (size - HEIGHT * SCALE) // 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        'width="512" height="512" shape-rendering="crispEdges">'
    ]
    # Merge horizontal runs, then stack identical runs from consecutive rows.
    runs = {}
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            key, start = row[x], x
            while x < len(row) and row[x] == key:
                x += 1
            span = (start, x, key)
            if (span, y - 1) in runs:
                runs[(span, y)] = runs.pop((span, y - 1))
                runs[(span, y)][1] += 1
            else:
                runs[(span, y)] = [y, 1]
    for ((start, end, key), _), (top, height) in sorted(runs.items(), key=lambda r: r[1]):
        out.append(
            f'<rect x="{ox + start}" y="{oy + top}" width="{end - start}" '
            f'height="{height}" fill="{PALETTE[key]}"/>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def png(rows, size, grey=False):
    from PIL import Image

    canvas = (max(WIDTH, HEIGHT) + 2 * MARGIN) * SCALE
    ox = (canvas - WIDTH * SCALE) // 2
    oy = (canvas - HEIGHT * SCALE) // 2
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            r, g, b = (int(PALETTE[key][i : i + 2], 16) for i in (1, 3, 5))
            if grey:
                r = g = b = round(0.299 * r + 0.587 * g + 0.114 * b)
            img.putpixel((ox + x, oy + y), (r, g, b, 255))
    # Scale up with crisp pixels, then down smoothly to the exact size.
    big = img.resize((canvas * 4, canvas * 4), Image.NEAREST)
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
