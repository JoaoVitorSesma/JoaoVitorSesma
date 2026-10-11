"""The JVM.Sesma signature, written in contribution-graph squares.

Each glyph is 7 rows tall, like a week column of the GitHub graph. Letters
light up column by column, so the signature appears to be written left to
right. The resting state is fully drawn, so reduced motion shows it at once.
"""

GLYPHS = {
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "e": ["....", "....", ".##.", "#..#", "####", "#...", ".###"],
    "s": ["....", "....", ".###", "#...", ".##.", "...#", "###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    "a": ["....", "....", ".##.", "...#", ".###", "#..#", ".###"],
}

TEXT = "JVM.Sesma"


def grid(word=TEXT):
    """7 rows of 0/1, one blank column around every glyph."""
    cols = [[0] * 7]
    for ch in word:
        g = GLYPHS[ch]
        for cx in range(len(g[0])):
            cols.append([1 if g[ry][cx] == "#" else 0 for ry in range(7)])
        cols.append([0] * 7)
    return [[c[ry] for c in cols] for ry in range(7)]


def draw(theme, x0, y0, pitch, start=0.3, step=0.035, dark=True):
    """Return (svg, css, width, height) for the signature at the given pitch."""
    g = grid()
    rows, cols = len(g), len(g[0])
    cell = pitch * 0.8
    seed, out, css = 11, [], []
    quiet = 80 if dark else 97  # share of empty background cells; light mode needs fewer
    for ry in range(rows):
        for cx in range(cols):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            lv = 0 if seed % 100 < quiet else 1
            x, y = x0 + cx * pitch, y0 + ry * pitch
            rect = f'x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{cell * .2:.1f}"'
            out.append(f'<rect {rect} fill="{theme["cells"][lv]}"/>')
            if g[ry][cx]:
                out.append(f'<rect class="sg{cx}" {rect} fill="{theme["cells"][4]}"/>')
    for cx in range(cols):
        css.append(f".sg{cx}{{animation:fade .25s ease {start + cx * step:.2f}s both}}")
    body = f'<g shape-rendering="crispEdges">{"".join(out)}</g>'
    return body, "".join(css), cols * pitch, rows * pitch
