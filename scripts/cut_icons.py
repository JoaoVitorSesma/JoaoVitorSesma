"""Cut the hero's pipeline icons out of my icon renders.

    python scripts/cut_icons.py

One render per icon and theme, scripts/icons/source-<name>-<theme>.png, each on
a plain background with its label underneath. Each icon is cropped above its
label and its background is turned into transparency (colour-to-alpha), so it
sits on GitHub's own background. Outputs scripts/icons/<name>-<theme>.png.
"""

from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent / "icons"
NAMES = ("infra", "models", "ui")

# the part of each render above its label, as a fraction of its height
TOP = {"infra": 0.78, "models": 0.77, "ui": 0.79}
MAX_H = 240  # px kept: about 3x the size the icon is shown at


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
    for theme in ("light", "dark"):
        for name in NAMES:
            src = np.asarray(Image.open(HERE / f"source-{name}-{theme}.png").convert("RGB"))
            h = src.shape[0]
            if theme == "light":
                # the light renders sit on a soft off-white wash, brighter in the
                # middle; keying against pure white keeps only what is darker
                bg = np.array([255, 255, 255])
            else:
                corners = [src[:8, :8], src[:8, -8:], src[-8:, :8], src[-8:, -8:]]
                bg = np.median(np.concatenate([c.reshape(-1, 3) for c in corners]), axis=0)
            rgba = keep_icon(to_alpha(src[: int(h * TOP[name])], bg))
            im = trim(rgba, pad=10)
            if im.height > MAX_H:
                im = im.resize((round(im.width * MAX_H / im.height), MAX_H), Image.LANCZOS)
            save(im, name, theme)


if __name__ == "__main__":
    main()
