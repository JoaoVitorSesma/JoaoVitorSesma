"""Cut the hero's pipeline icons out of scripts/icons/source.png.

    python scripts/cut_icons.py

The sheet has the three icons on white cards (light) and on dark cards (dark).
Each icon is cropped above its label and its card colour is turned into
transparency (colour-to-alpha), so it sits on GitHub's own background and the
dark icons keep their soft glow. Outputs scripts/icons/<name>-<theme>.png.
"""

from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent / "icons"
COLS = {"infra": (66, 352), "models": (370, 656), "ui": (675, 973)}
ROWS = {"light": (18, 220), "dark": (295, 500)}


def to_alpha(rgb, bg):
    """Smallest alpha that explains each pixel as a colour over bg."""
    p = rgb.astype(float)
    b = np.array(bg, float)
    up = np.where(p > b, (p - b) / np.maximum(255 - b, 1), 0)
    down = np.where(p < b, (b - p) / np.maximum(b, 1), 0)
    a = np.clip(np.maximum(up, down).max(axis=2), 0, 1)
    # fade the faintest values out instead of cutting them, which drops the
    # compression noise in the background without a hard edge round the glow
    a = np.clip((a - 0.05) / 0.95, 0, 1)
    safe = np.maximum(a, 1e-6)[..., None]
    fg = np.clip(b + (p - b) / safe, 0, 255)
    return np.dstack([fg, a * 255]).astype(np.uint8)


def main():
    sheet = np.asarray(Image.open(HERE / "source.png").convert("RGB"))
    for theme, (y0, y1) in ROWS.items():
        bg = sheet[y0 + 4, COLS["infra"][0] + 4]
        for name, (x0, x1) in COLS.items():
            rgba = to_alpha(sheet[y0:y1, x0:x1], bg)
            im = Image.fromarray(rgba, "RGBA")
            l, t, r, b = Image.fromarray(rgba[..., 3]).point(lambda v: 255 if v > 6 else 0).getbbox()
            pad = 4
            im = im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))
            im.save(HERE / f"{name}-{theme}.png", optimize=True)
            print(f"{name}-{theme}.png", im.size)


if __name__ == "__main__":
    main()
