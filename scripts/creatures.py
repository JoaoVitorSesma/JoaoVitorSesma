"""Original pixel-art creatures for the walking strip.

Each creature has a palette and two frames drawn as character grids
('.' is transparent). Frames face right; the strip mirrors them on the way
back. Rows are padded to the widest row, so grids can be typed loosely.
"""

OUTLINE = "#1e2633"

CREATURES = {
    # A baby dragon still wearing the bottom half of its eggshell.
    "egg": dict(
        palette={
            "o": OUTLINE, "g": "#5cc47a", "G": "#2f8a4c", "h": "#f2d27a",
            "e": "#141a24", "w": "#ffffff", "c": "#f4a9b8",
            "y": "#f6efdc", "p": "#c9b98f", "b": "#8fdca5", "B": "#2f8a4c",
        },
        frames=[
            [
                "...........o...o........",
                "..........oho.oho.......",
                "...........oho.oho......",
                "........oooooooooooo....",
                ".......oggggggggggggoo..",
                ".o....ogggggggggwegggggo",
                "obo...oggggggggggegggggo",
                "obbo..oggggggggggggggGgo",
                "obbbo.oggggggggggcgoooo.",
                "obBbbooggggggggggggo....",
                ".oBbbbogggggggggggo.....",
                "..ooooyoyoyoyoyoyoyo....",
                "..oyyyyyyyyyyyyyyyyyo...",
                ".oyyypyyyyyyyypyyyyyyo..",
                ".oyyyyyyyyypyyyyyyyyyo..",
                "..oyyypyyyyyyyyyyypyo...",
                "...ooyyyyyyyyyyyyyoo....",
                "....oGGo......oGGo......",
                "....ooo.......ooo.......",
            ],
            [
                "...........o...o........",
                "..........oho.oho.......",
                "...........oho.oho......",
                "oo......oooooooooooo....",
                "obo....oggggggggggggoo..",
                "obbo..ogggggggggwegggggo",
                "obbbo.oggggggggggegggggo",
                "oBbbbooggggggggggggggGgo",
                ".oBbbboggggggggggcgoooo.",
                "..oBbbogggggggggggo.....",
                "...oooogggggggggggo.....",
                "..ooooyoyoyoyoyoyoyo....",
                "..oyyyyyyyyyyyyyyyyyo...",
                ".oyyypyyyyyyyypyyyyyyo..",
                ".oyyyyyyyyypyyyyyyyyyo..",
                "..oyyypyyyyyyyyyyypyo...",
                "...ooyyyyyyyyyyyyyoo....",
                ".....oGGo....oGGo.......",
                ".....ooo.....ooo........",
            ],
        ],
    ),
    # A steel robot dragon with an LED eye and a blinking antenna.
    "mecha": dict(
        palette={
            "o": OUTLINE, "s": "#b7c3d1", "S": "#8794a6", "d": "#56627a",
            "L": "#4fe3ff", "a": "#ffcf4a", "r": "#e8edf3", "j": "#3a4456", "W": "#7fa7d9",
        },
        frames=[
            [
                "....................a.....",
                "....................o.....",
                "................ooooooo...",
                "...............osrrrrrsoo.",
                "...............osssssLLsso",
                "...............ossssssssso",
                "...............ossssjjjjjo",
                "........o.o.o..ossssssoo..",
                ".......ododdodoossssso....",
                "......osrrrrrrrrrsssso....",
                "o....ossWWWWWWWsssssso....",
                "do..osssWWWWWWsssssso.....",
                ".dooossssWWWWsssssso......",
                "..ossSSSSSSSSSSSSSso......",
                "...oSSSSSSSSSSSSSSo.......",
                "....oooooooooooooo........",
                ".....odo.odo..odo.odo.....",
                ".....odo.ooo..odo.ooo.....",
                ".....ooo......ooo.........",
            ],
            [
                "....................o.....",
                "....................o.....",
                "................ooooooo...",
                "...............osrrrrrsoo.",
                "...............osssssLLsso",
                "...............ossssssssso",
                "...............ossssjjjjjo",
                "........o.o.o..ossssssoo..",
                ".......ododdodoossssso....",
                "......osrrrrrrrrrsssso....",
                ".....ossWWWWWWWsssssso....",
                "oo..osssWWWWWWsssssso.....",
                "ddooossssWWWWsssssso......",
                "..ossSSSSSSSSSSSSSso......",
                "...oSSSSSSSSSSSSSSo.......",
                "....oooooooooooooo........",
                "......odo.odo..odo.odo....",
                "......ooo.odo..ooo.odo....",
                "..........ooo......ooo....",
            ],
        ],
    ),
    # A round lilac dragon that hops and flaps tiny wings.
    "blob": dict(
        palette={
            "o": OUTLINE, "m": "#b9a2f2", "M": "#8c72d6", "k": "#e9e0ff",
            "l": "#fff1c2", "w": "#d7ccff", "b": "#a48be8", "e": "#141a24", "h": "#ffffff", "c": "#f4a9b8",
        },
        frames=[
            [
                "......................",
                "..........oo....oo....",
                ".........olo...olo....",
                "..........oooooooo....",
                "..o.o.o.oommmmmmmmoo..",
                ".oMoMoMommmmmmmmmmmmo.",
                "..oMMMommmmmmmmmmhemmo",
                "oooooommmmmmmmmmmeemmo",
                "owbbbbommmmmmmmmmmmcmo",
                "owwbbbommmmmmmmmmmmmmo",
                ".owwbbommmmkkkkkkmmmo.",
                "..owwbommmkkkkkkkkmmo.",
                "...oooommmkkkkkkkkmo..",
                "oMo..ommmmkkkkkkkmmo..",
                ".oMooommmmmkkkkkmmo...",
                "..oooooommmmmmmmoo....",
                ".......omo....omo.....",
                ".......ooo....ooo.....",
            ],
            [
                "..........oo....oo....",
                ".........olo...olo....",
                "..........oooooooo....",
                "oooo.o.o.oommmmmmmmoo.",
                "owbboMoMommmmmmmmmmmmo",
                "owwbbbommmmmmmmmmmhemo",
                ".owwbbommmmmmmmmmmeemo",
                "..owwbommmmmmmmmmmmmco",
                "...oooommmmmmmmmmmmmmo",
                "....ommmmmkkkkkkmmmmo.",
                "...ommmmmkkkkkkkkmmmo.",
                "oMoommmmkkkkkkkkkmmo..",
                ".oMoommmmkkkkkkkmmo...",
                "..oooooommmmmmmmoo....",
                "........oo....oo......",
                "......................",
                "......................",
                "......................",
            ],
        ],
    ),
    # A hedgehog with natural brown spines, trotting on tiny feet.
    "hedgehog": dict(
        palette={
            "o": OUTLINE, "S": "#8a6446", "s": "#5d4030", "f": "#f1dcc0", "F": "#e2c7a1",
            "h": "#ffffff", "e": "#141a24", "n": "#2b2b2b", "c": "#f0a3a8", "k": "#c9977a",
        },
        frames=[
            [
                "...........o..o..o...........",
                "..........osoosooso..........",
                ".......oossSssSssSsoo........",
                ".....oossSssSssSssSssoo......",
                "....ossSssSssSssSssSssSo.....",
                "...osSssSssSssSssSssSssSo....",
                "..oSssSssSssSssSssSssSssoo...",
                ".ossSssSssSssSssSssSssSoffoo.",
                ".oSssSssSssSssSssSssSsoffffo.",
                "ossSssSssSssSssSssSssoffehfo.",
                "oSssSssSssSssSssSssSoffeeffoo",
                "osSssSssSssSssSssSsoffffffffn",
                "ossSssSssSssSssSssofcfffffoo.",
                ".ossSssSssSssSssSsoffffffo...",
                "..ooFFFFFFFFFFFFFFFFFFFoo....",
                "....oFFFFFFFFFFFFFFFFFo......",
                ".....okko.......okko.........",
                ".....ooo........ooo..........",
            ],
            [
                "...........o..o..o...........",
                "..........osoosooso..........",
                ".......oossSssSssSsoo........",
                ".....oossSssSssSssSssoo......",
                "....ossSssSssSssSssSssSo.....",
                "...osSssSssSssSssSssSssSo....",
                "..oSssSssSssSssSssSssSssoo...",
                ".ossSssSssSssSssSssSssSoffoo.",
                ".oSssSssSssSssSssSssSsoffffo.",
                "ossSssSssSssSssSssSssoffehfo.",
                "oSssSssSssSssSssSssSoffeeffoo",
                "osSssSssSssSssSssSsoffffffffn",
                "ossSssSssSssSssSssofcfffffoo.",
                ".ossSssSssSssSssSsoffffffo...",
                "..ooFFFFFFFFFFFFFFFFFFFoo....",
                "....oFFFFFFFFFFFFFFFFFo......",
                ".......okko....okko..........",
                ".......ooo.....ooo...........",
            ],
        ],
    ),
}


# The original silver dragon, kept as an option.
import sprite as _silver  # noqa: E402

CREATURES["silver"] = dict(palette=_silver.PALETTE, frames=[_silver.WALK_A, _silver.WALK_B])


def get(name):
    """Return (palette, frames, width, height) with rows padded to equal width."""
    c = CREATURES[name]
    w = max(len(row) for f in c["frames"] for row in f)
    h = max(len(f) for f in c["frames"])
    frames = [[row.ljust(w, ".") for row in f] + ["." * w] * (h - len(f)) for f in c["frames"]]
    return c["palette"], frames, w, h


def frame_rects(palette, frame, px, ox=0.0, oy=0.0):
    """SVG <rect>s for one frame, merging horizontal runs of a colour."""
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
