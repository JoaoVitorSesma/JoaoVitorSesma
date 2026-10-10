"""Original pixel-art dragon used in the walking strip.

Each frame is a grid of characters; every character maps to a colour in
PALETTE ('.' is transparent). Frames face right; the strip mirrors them
when the dragon walks back.
"""

PALETTE = {
    "o": "#1e2633",  # outline
    "w": "#eef2f7",  # body
    "s": "#c3ccd8",  # shade
    "d": "#8f9bad",  # deep shade / feet
    "b": "#6aaef5",  # wing membrane
    "B": "#2f6fc4",  # wing bone
    "g": "#dfe5ee",  # horn
    "e": "#141a24",  # eye
    "h": "#ffffff",  # eye highlight
    "c": "#f4a9b8",  # cheek
}

# 28 x 18, facing right
WALK_A = [
    "................oo..........",
    ".................go.........",
    "...........oo.....go.oooo...",
    "..........obbo....owwwwwwo..",
    ".........obbBo...owwwwwwwwo.",
    "........obbbBo..owwwwwwheewo",
    ".......obbbbBo..owwwwwwweewo",
    "......obbbbBBo.owwwwwwwwwwwo",
    ".....obbbbbBo.owwwwwwwwwwcwo",
    "..o..oooobBoowwwwwwwwwwoooo.",
    ".ogo.....oowwwwssowwwwo.....",
    ".ogo....owwwwwwwwwwwwwwo....",
    "..owo..owwwwwwwwwwwwwwwo....",
    "...owoowwwwwwwwwwwwwwwwo....",
    "....owwwwwsssssssssswwo.....",
    ".....oowsssssssssssoo.......",
    "......owwo.odo....owwo.odo..",
    "......oddo.ooo....oddo.ooo..",
]

WALK_B = [
    "................oo..........",
    "........oooo.....go.........",
    ".......obbbbo.....go.oooo...",
    "......obbbBBo.....owwwwwwo..",
    ".......obbbBo....owwwwwwwwo.",
    "........obbBo...owwwwwwheewo",
    ".........obBo...owwwwwwweewo",
    "..........oBo..owwwwwwwwwwwo",
    "..........oBo.owwwwwwwwwwcwo",
    "..o.....oooBoowwwwwwwwwoooo.",
    ".ogo.....oowwwwssowwwwo.....",
    ".ogo....owwwwwwwwwwwwwwo....",
    "..owo..owwwwwwwwwwwwwwwo....",
    "...owoowwwwwwwwwwwwwwwwo....",
    "....owwwwwsssssssssswwo.....",
    ".....oowsssssssssssoo.......",
    ".....odo.owwo....odo.owwo...",
    ".....ooo.oddo....ooo.oddo...",
]

FRAMES = [WALK_A, WALK_B]
W = len(WALK_A[0])
H = len(WALK_A)

for _f in FRAMES:
    assert len(_f) == H and all(len(r) == W for r in _f), "ragged sprite"


def frame_rects(frame, px, ox=0.0, oy=0.0):
    """Return SVG <rect>s for one frame, merging horizontal runs of a colour."""
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
                f'height="{px:g}" fill="{PALETTE[ch]}"/>'
            )
            x += run
    return "".join(out)
