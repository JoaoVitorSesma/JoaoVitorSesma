"""The README mascot: an original pixel-art hedgehog drawn by João.

Every pose is a grid of characters; each character maps to a colour in the
palette and '.' is transparent. Poses face right; the strip mirrors them on
the way back. Spines have an outer rim (r) and interior quills (q).
"""

PALETTE = {
    "o": "#0b1024",  # outline
    "B": "#0096fd",  # spines
    "S": "#22657a",  # spine shadow where it meets the body
    "Y": "#ffde11",  # body
    "y": "#c9a400",  # body shade
    "f": "#c9a400",  # raised paw
    "r": "#0b1024",  # outer spine rim
    "q": "#0b1024",  # interior quill, dark in both themes
    "n": "#0b1024",  # nose
    "h": "#0b1024",  # nose highlight
}

# The dark theme lightens the exposed spine rim and the nose so they stay
# visible on GitHub's dark background; shapes stay identical.
DARK = {"r": "#245674", "n": "#29384c", "h": "#53677e"}

# 27 x 20, facing right: four walking poses, crouch, curl and the ball.
FRAMES = [
    [
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBooBBBBr....",
        "..rrBBqqqBBqBBBoYYYoBBr....",
        "rrBBBBqBBBBBBBoYyyYYYYy....",
        ".rBBBBBqBBqBBBBoYYYYYYYro..",
        "..rBBBBBBqBBBBBBYYYYooYYo..",
        ".rrBqqBBBBqBBSYYYYYYooYYYnh",
        "rrBBqBBBBSSSSYYYYYYYooYYYnn",
        ".rBBBBBSYYYYYYYYYYYYYYYYYYo",
        "..rBBBYYYYYYYYYYYYYYYYYYYo.",
        ".rrBBYYYYYYYYYYYYYYYYYYYo..",
        "...oYYYYYYYYYYYYYYYYYYYo...",
        "....oYYYYYYYYYYYYYYyooo....",
        "......oYYofffoYYYffo.......",
        "......oYYoooo.oYYfo........",
        ".......oo......ooo.........",
    ],
    [
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBooBBBBr....",
        "..rrBBqqqBBqBBBoYYYoBBr....",
        "rrBBBBqBBBBBBBoYyyYYYYy....",
        ".rBBBBBqBBqBBBBoYYYYYYYro..",
        "..rBBBBBBqBBBBBBYYYYooYYo..",
        ".rrBqqBBBBqBBSYYYYYYooYYYnh",
        "rrBBqBBBBSSSSYYYYYYYooYYYnn",
        ".rBBBBBSYYYYYYYYYYYYYYYYYYo",
        "..rBBBYYYYYYYYYYYYYYYYYYYo.",
        ".rrBBYYYYYYYYYYYYYYYYYYYo..",
        "...oYYYYYYYYYYYYYYYYYYYo...",
        "....oYYYYYYYYYYYYYYyooo....",
        ".....oYYYofffoYYofffo......",
        ".....oYYo.offoYYoooo.......",
        "......oo...oo.oo...........",
    ],
    [
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBooBBBBr....",
        "..rrBBqqqBBqBBBoYYYoBBr....",
        "rrBBBBqBBBBBBBoYyyYYYYy....",
        ".rBBBBBqBBqBBBBoYYYYYYYro..",
        "..rBBBBBBqBBBBBBYYYYooYYo..",
        ".rrBqqBBBBqBBSYYYYYYooYYYnh",
        "rrBBqBBBBSSSSYYYYYYYooYYYnn",
        ".rBBBBBSYYYYYYYYYYYYYYYYYYo",
        "..rBBBYYYYYYYYYYYYYYYYYYYo.",
        ".rrBBYYYYYYYYYYYYYYYYYYYo..",
        "...oYYYYYYYYYYYYYYYYYYYo...",
        "....oYYYYYYYYYYYYYYyooo....",
        "......oYYYffoYYYofffo......",
        ".......oooffoYYo.offo......",
        "..........oo.oo...oo.......",
    ],
    [
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBooBBBBr....",
        "..rrBBqqqBBqBBBoYYYoBBr....",
        "rrBBBBqBBBBBBBoYyyYYYYy....",
        ".rBBBBBqBBqBBBBoYYYYYYYro..",
        "..rBBBBBBqBBBBBBYYYYooYYo..",
        ".rrBqqBBBBqBBSYYYYYYooYYYnh",
        "rrBBqBBBBSSSSYYYYYYYooYYYnn",
        ".rBBBBBSYYYYYYYYYYYYYYYYYYo",
        "..rBBBYYYYYYYYYYYYYYYYYYYo.",
        ".rrBBYYYYYYYYYYYYYYYYYYYo..",
        "...oYYYYYYYYYYYYYYYYYYYo...",
        "....oYYYYYYYYYYYYYYyooo....",
        "......oYYYffooYYYffo.......",
        ".......oYYfo..oooffo.......",
        "........ooo......oo........",
    ],
    [
        "...........................",
        "...........................",
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBBBBBBBr....",
        ".orrrBqqBBBBBBBBBBooBBBr...",
        ".rBBBBBqBBBBBBBBBoYYYoBr...",
        ".orBBBBBBBBBBBBBoYyyYYBr...",
        "..rBBBBBBBBBBBYYBoYYYYYo...",
        "orBqqBBBBBBBYYYYYYYYYYYo...",
        "rBBBqBBBBYYYYYYYYYYYYoYYo..",
        ".rrBBBBBYYYYYYYYYYYYYYYYnh.",
        "..BBBBYYYYYYYYYYYYYYYYYYyo.",
        "..rrBYYYYYYYYYYYYYYYYYYYyo.",
        ".....oYYYofffoYYofffo......",
        ".....oYYo.offoYYoooo.......",
        "......oo...oo.oo...........",
    ],
    [
        "...........................",
        "...........................",
        ".........rrr...............",
        ".........rBBrr.rrr.........",
        ".....rrrrrBBBrrBBrr........",
        ".....rBBBBrrBBBrBBr.r......",
        "..rrrrBBBBBqqBBBBBBrBr.....",
        "...rBBBBBBBqBqBBBBBBBBr....",
        "..orrrqqBBBBBBBBBBBBBBrBr..",
        "..rBBBBqBBBBBBBBBBBBBBBBr..",
        "..orBBBBBBBBBBBBoYyBBBBBr..",
        "...rBBBBBBBBBBBBoYYoBBBro..",
        ".orBBBBBBBBBBBBBBYYYYBBBr..",
        ".rBBqqBBBBBBBBBBBYYYYYBro..",
        "..rrBqBBBBBBBBBBYYYoYYYo...",
        "...orBBBBBBBBYYYYYYooYYo...",
        "...rBBBBBBYYYYYYYYYYYYyo...",
        "....rrrBYooYYYYYYyYYYYoo...",
        "......oYYYYyYYYyYYoyYyo....",
        "......ooyYYoyyyyoYoonho....",
    ],
    [
        "...........................",
        "............r..ro..........",
        "...........rBrrBro.........",
        "........rBBrBBrBBror.......",
        ".......rrBBBBBBBBBrBr......",
        "......rBBBBqqBBBBBBBB......",
        ".......BBBBqBBBBBBBBr......",
        ".......rBBBBBBBBBBBBro.....",
        ".....orBBBBBBBBBBBBBBro....",
        ".....rBBqqBBBBBBBBBBBBr....",
        ".....orBBqBBBBBBBBBBBro....",
        "....orBBBBBBBBBBqBBBBBr....",
        "....rBBBBBBBBBBqBBBBBBr....",
        "....orBBBBBBBBBBqBBBBBr....",
        "......rBBBqqBBBBBBBBBr.....",
        "......rBBBqBBBBBBBBBro.....",
        "......rBBBBBBBBBBBBBB......",
        ".......rrBBBBBBBBBBrr......",
        "........rBBrBrrBrrBr.......",
        "........ooooooooooo........",
    ],
]

W = len(FRAMES[0][0])
H = len(FRAMES[0])
for _f in FRAMES:
    assert len(_f) == H and all(len(r) == W for r in _f), "ragged hedgehog pose"

# Seconds per walking pose, and which poses make up each movement.
STEP = 0.11
ROLL = dict(walk=[0, 1, 2, 3], curl=[4, 5], ball=6)


def palette(theme="light"):
    """Colours for the theme; only the rim and nose change in dark mode."""
    return {**PALETTE, **DARK} if theme == "dark" else dict(PALETTE)


def recovery():
    """Blink and shake the existing side-profile head; keep the feet planted."""
    blink = [list(row) for row in FRAMES[0]]
    for y in range(9, 12):
        blink[y][20:22] = "YY"
    blink[10][20:23] = "ooo"
    poses = {"blink": ["".join(row) for row in blink]}
    for name, offset in (("left", -1), ("right", 1)):
        body = [["."] + row[:] + ["."] for row in blink]
        for y in range(6, 16):
            body[y][18:28] = "." * 10
            if y >= 9:
                body[y][18:22] = "YYYY"
            for x in range(17, 27):
                if blink[y][x] != ".":
                    body[y][x + 1 + offset] = blink[y][x]
        poses[name] = ["".join(row) for row in body]
    return poses


def frame_rects(palette, frame, px, ox=0.0, oy=0.0):
    """SVG <rect>s for one pose, merging horizontal runs of a colour."""
    out = []
    for y, row in enumerate(frame):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == ch:
                run += 1
            out.append(
                f'<rect x="{ox + x * px:g}" y="{oy + y * px:g}" width="{run * px:g}" '
                f'height="{px:g}" fill="{palette[ch]}"/>'
            )
            x += run
    return "".join(out)
