"""Cut the hero's pipeline icons out of my icon artwork.

    python scripts/cut_icons.py

Light theme: scripts/icons/source.png, a sheet with the three icons on white
cards. Dark theme: scripts/icons/source-<name>-dark.png, one render per icon on
a near-black background, drawn for dark mode.

Each icon is cropped above its label and its background colour is turned into
transparency (colour-to-alpha), so it sits on GitHub's own background.
Outputs scripts/icons/<name>-<theme>.png.
"""

from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent / "icons"
NAMES = ("infra", "models", "ui")

# light sheet: column per icon, and the band above the labels
SHEET_COLS = {"infra": (66, 352), "models": (370, 656), "ui": (675, 973)}
SHEET_ROWS = (18, 220)

# dark renders: the part of each image above its label, as a fraction of height
DARK_TOP = {"infra": 0.78, "models": 0.77, "ui": 0.79}
DARK_MAX_H = 240  # px kept: about 3x the size the icon is shown at


def to_alpha(rgb, bg):
    """Smallest alpha that explains each pixel as a colour over bg."""
    p = rgb.astype(float)
    b = np.array(bg, float)
    up = np.where(p > b, (p - b) / np.maximum(255 - b, 1), 0)
    down = np.where(p < b, (b - p) / np.maximum(b, 1), 0)
    a = np.clip(np.maximum(up, down).max(axis=2), 0, 1)
    # fade the faintest values out instead of cutting them, which drops the
    # compression noise in the background without a hard edge
    a = np.clip((a - 0.05) / 0.95, 0, 1)
    safe = np.maximum(a, 1e-6)[..., None]
    fg = np.clip(b + (p - b) / safe, 0, 255)
    return np.dstack([fg, a * 255]).astype(np.uint8)


def trim(rgba, pad=4, level=6):
    im = Image.fromarray(rgba, "RGBA")
    l, t, r, b = Image.fromarray(rgba[..., 3]).point(lambda v: 255 if v > level else 0).getbbox()
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))


def keep_icon(rgba):
    """Keep the icon and drop isolated specks of render noise in the background,
    which would otherwise stretch the crop."""
    from scipy import ndimage

    solid = ndimage.binary_dilation(rgba[..., 3] > 40, iterations=6)
    labels, n = ndimage.label(solid)
    if n:
        sizes = ndimage.sum(solid, labels, range(1, n + 1))
        solid = np.isin(labels, 1 + np.flatnonzero(sizes > sizes.max() * 0.02))
    out = rgba.copy()
    out[..., 3] = np.where(solid, rgba[..., 3], 0)
    return out


def save(im, name, theme):
    im.save(HERE / f"{name}-{theme}.png", optimize=True)
    print(f"{name}-{theme}.png", im.size)


def main():
    sheet = np.asarray(Image.open(HERE / "source.png").convert("RGB"))
    y0, y1 = SHEET_ROWS
    bg = sheet[y0 + 4, SHEET_COLS["infra"][0] + 4]
    for name, (x0, x1) in SHEET_COLS.items():
        save(trim(to_alpha(sheet[y0:y1, x0:x1], bg)), name, "light")

    for name in NAMES:
        src = np.asarray(Image.open(HERE / f"source-{name}-dark.png").convert("RGB"))
        h = src.shape[0]
        bg = np.median(np.concatenate([src[:8, :8].reshape(-1, 3), src[:8, -8:].reshape(-1, 3)]), axis=0)
        rgba = keep_icon(to_alpha(src[: int(h * DARK_TOP[name])], bg))
        im = trim(rgba, pad=10)
        if im.height > DARK_MAX_H:
            im = im.resize((round(im.width * DARK_MAX_H / im.height), DARK_MAX_H), Image.LANCZOS)
        save(im, name, "dark")


if __name__ == "__main__":
    main()
