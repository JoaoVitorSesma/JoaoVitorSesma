"""Render SVG assets at chosen animation times for visual checks.

    python scripts/preview.py out.png file.svg[,file2.svg] t1 t2 ...  [--bg dark|light] [--width 900] [--reduced]
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BG = {"dark": "#0d1117", "light": "#ffffff"}


def main():
    args = sys.argv[1:]
    out, files = args[0], args[1].split(",")
    bg, width, reduced, times = "dark", 900, False, []
    i = 2
    while i < len(args):
        a = args[i]
        if a == "--bg":
            bg = args[i + 1]; i += 2; continue
        if a == "--width":
            width = int(args[i + 1]); i += 2; continue
        if a == "--reduced":
            reduced = True; i += 1; continue
        times.append(float(a)); i += 1
    from PIL import Image, ImageDraw
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for t in times:
            for f in files:
                pg = b.new_page(viewport={"width": width, "height": 400},
                                reduced_motion="reduce" if reduced else "no-preference")
                src = Path(f).read_text()
                pg.set_content(
                    f"<html><body style='margin:0;background:{BG[bg]}'>"
                    f"<style>svg{{width:{width}px;height:auto;display:block}}</style>{src}</body></html>"
                )
                pg.wait_for_timeout(150)
                pg.evaluate(
                    """(t) => {
                      const svg = document.querySelector('svg');
                      svg.pauseAnimations(); svg.setCurrentTime(t);
                      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
                    }""",
                    t,
                )
                pg.wait_for_timeout(120)
                tmp = f"/tmp/_pv_{len(shots)}.png"
                pg.locator("svg").screenshot(path=tmp)
                shots.append((f"{Path(f).name} @ {t}s", Image.open(tmp).convert("RGB")))
                pg.close()
        b.close()
    W = max(im.width for _, im in shots)
    H = sum(im.height + 22 for _, im in shots)
    sheet = Image.new("RGB", (W, H), "#6e7681")
    y = 0
    d = ImageDraw.Draw(sheet)
    for lbl, im in shots:
        d.text((4, y + 4), lbl, fill="#ffffff")
        sheet.paste(im, (0, y + 20))
        y += im.height + 22
    sheet.save(out)


if __name__ == "__main__":
    main()
