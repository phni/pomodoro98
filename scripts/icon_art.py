"""Pixel art for the Pomodoro98 app icon.

The icon is a 60x56 pixel-art Windows 98-style window with a tomato inside.
`scripts/build_icons.py` draws the window frame in code and fills its client
area with TOMATO, then writes the SVG and every PNG size. Edit this file and
rerun the script to change the icon.

Each character in TOMATO is one pixel; see PALETTE for the colours; "." is the
window's grey background.
"""

WIDTH = 60
HEIGHT = 56

PALETTE = {
    "k": "#000000",  # outline
    "n": "#02108f",  # title bar navy
    "w": "#ffffff",  # highlight
    "s": "#f0f0f0",  # frame light edge
    "l": "#c8c8c8",  # window grey
    "g": "#808080",  # frame shadow
    "d": "#303030",  # tomato shadow
    "R": "#fc1b17",  # tomato red
    "r": "#c90308",  # tomato mid red
    "m": "#810305",  # tomato dark red
    "p": "#fd6d6a",  # tomato pink highlight
    "G": "#81d223",  # leaf light green
    "e": "#41ab1a",  # leaf green
    "f": "#218a1c",  # leaf mid green
    "h": "#165b1e",  # leaf dark green
}

# Client area, 52x40 pixels, placed at x=4, y=12 inside the window frame.
TOMATO = [
    "....................................................",
    ".......................kkk..........................",
    "......................ghhhd.........................",
    "......................kGffk.........................",
    "......................kGeehk........................",
    "..............kkkkk....kGehk.....kkkk...............",
    "..............kGGeekkk..kGfk..kkkGffk...............",
    "................kkeGefkkkGfkkkGGGfkk................",
    "...............gkkhGeffhkefkkkeGGfkk................",
    "..............dkkkkGefehkffkhfeefkkkkkkk............",
    "............kkrRRRkkGGefkhhhffkkkRRRRRkkk...........",
    "..........kkRRRRRkGGffffehhffGGGGkkRRRRRmkk.........",
    "..........krRRRmkGeffkkkGGefkkfeeeGkkRRRrkk.........",
    ".........kRRRppkkGefkkkkGGGfkkheeeefkRRRrkkd........",
    "........kRRRRwwkkekkrRRkkGGfkRkkkffffkRRrrrk........",
    "........kRRRpwwkkkRRRRRRkGGfkRRRRkkffkRRrrrk........",
    "......kkRRRRwwRRRRRRRRRRkeekRRRRRRRkkkRRrrrmkk......",
    "......kkRRswwwRswwpRRRRRRkkkRRRRRRRRRkRRrrrmkk......",
    "......kkRRwwwwRwwwppRRRRRkkmRRRRRRRRRkRrrrrmkk......",
    ".....krRRRwwRRwwwwppRRRRRkkRRRRRRRRRRRRrrrmmddk.....",
    ".....krRRpppRRwwwpppRRRRRRRRRRRRRRRrrrRrrmmmddk.....",
    ".....krRRpppRRppppRRRRRRRRRRRRRRRRrrrrRrrmmmddk.....",
    ".....krRRpppRRRpppRRRRRRRRRRRRRRRRrrrrRrrmmmddk.....",
    ".....krRRpppRRRRppRRRRRRRRRRRRRrrrrrrrrrmmmmddk.....",
    ".....krRRRppRRRRRRRRRRRRRRRRRrrrrrrrrrrrmmmmddk.....",
    ".....krRrRRRRRRRRRRRRRRRRRRRRrrrrrrrrrrmmmmdddk.....",
    "......kkrRrrrRRRRRRRRRRRRrrrrrrrrrrrrmmmmdddkk......",
    "......kkrrrrrrRRRRRRrrrrrrrrrrrrrrrrmmmmmdddkk......",
    "......kkrrrrrrRRrrrrrrrrrrrrrrrrrrrrmmmmddddkk......",
    ".......dmrrrrrrrrrrrrrrrrrrrrrrrrrrmmmmmdddk........",
    "........krrrrrrrrrrrrrrrrrrrrrrrmmmmmmmddddk........",
    "........krrrrrrrrrrrrrrrrrrrrmmmmmmmmmdddddk........",
    ".........krrmrrrrrrrrrrrrrmmmmmmmmmmdddddkk.........",
    "..........kkmmrrrrrrrrrrrrmmmmmmmdddddddk...........",
    "..........gkmmmrrrrrmmmmmmmmmmmmmdddddddk...........",
    "............kkmmmmmmmmmmmmmmmdddddddddkk............",
    "..............kkmmmmmmmmdddddddddddddk..............",
    "...............dkkmmmmmdddddddddddkkk...............",
    "..................kkkkkkkkkkkkkkkk..................",
    "....................................................",
]
