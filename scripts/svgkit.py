"""Small helpers for building theme-aware, font-free SVGs for a GitHub README.

GitHub serves README images through <img>, where SVGs cannot load web fonts,
so every string is converted to outline paths with HarfBuzz shaping.
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"


def _num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# Glyphs missing from the subset fonts, drawn in font units (y up, 600 advance).
_ARROW = [(40, 245), (455, 245), (300, 90), (346, 44), (580, 275), (346, 506),
          (300, 460), (455, 305), (40, 305)]
_CUSTOM = {"→": _ARROW}


class Font:
    def __init__(self, filename):
        path = str(FONT_DIR / filename)
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))

    def _shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False, "calt": False})
        return buf

    def width(self, text, size, tracking=0.0):
        buf = self._shape(text)
        adv = sum(p.x_advance for p in buf.glyph_positions)
        return adv * size / self.upem + tracking * len(text)

    def path(self, text, x, y, size, tracking=0.0, anchor="start"):
        """Outline path for `text` with its baseline at y. Returns (d, width)."""
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        s = size / self.upem
        buf = self._shape(text)
        pen = SVGPathPen(self.glyphs, ntos=_num)
        cx = x
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            ch = text[info.cluster]
            gx = cx + pos.x_offset * s
            gy = y - pos.y_offset * s
            tpen = TransformPen(pen, (s, 0, 0, -s, gx, gy))
            if info.codepoint == 0 and ch in _CUSTOM:
                pts = _CUSTOM[ch]
                tpen.moveTo(pts[0])
                for p in pts[1:]:
                    tpen.lineTo(p)
                tpen.closePath()
            elif info.codepoint != 0:
                self.glyphs[self.order[info.codepoint]].draw(tpen)
            cx += pos.x_advance * s + tracking
        return pen.getCommands(), w


# Atkinson Hyperlegible (Braille Institute): every glyph is built to be told
# apart from its neighbours (l / I / 1, 0 / O), which keeps small labels legible.
SANS = Font("atkinson-hyperlegible-next-latin-400-normal.ttf")
SANS_BD = Font("atkinson-hyperlegible-next-latin-700-normal.ttf")
MONO = Font("atkinson-hyperlegible-mono-latin-400-normal.ttf")
MONO_MD = Font("atkinson-hyperlegible-mono-latin-500-normal.ttf")


def wrap(font, s, size, max_w):
    """Greedy word wrap by real glyph widths."""
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and font.width(trial, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    # avoid a lone word on the last line when the previous line can spare one
    if len(lines) > 1 and " " not in lines[-1] and " " in lines[-2]:
        head, moved = lines[-2].rsplit(" ", 1)
        if font.width(f"{moved} {lines[-1]}", size) <= max_w:
            lines[-2], lines[-1] = head, f"{moved} {lines[-1]}"
    return lines


# README column width in CSS px: ~795 on desktop (measured on the live profile),
# ~340 on a phone. Sizes below are given in rendered px and converted per canvas.
DISPLAY = {False: 795, True: 340}
MIN_PX = 12.0
_track = {"k": 1.0, "min": None, "min_text": ""}


def canvas(W, mobile):
    """Start a new SVG. Returns r(px): rendered CSS px -> SVG units."""
    k = W / DISPLAY[mobile]
    _track.update(k=k, min=None, min_text="")
    return lambda v: v * k


def smallest():
    return _track["min"], _track["min_text"]


def text(font, s, x, y, size, cls, tracking=0.0, anchor="start", extra=""):
    shown = size / _track["k"]
    if _track["min"] is None or shown < _track["min"]:
        _track.update(min=shown, min_text=s)
    d, w = font.path(s, x, y, size, tracking, anchor)
    return f'<path class="{cls}" d="{d}"{extra}/>', w


THEMES = {
    "dark": dict(
        fg="#e6edf3", mu="#9198a1", fa="#656c76", line="#30363d", panel="#151b23",
        panel2="#0d1117", ac="#4493f8", ac2="#a5d6ff", gr="#3fb950", warn="#d29922",
        hot="#f78166", cool="#4493f8",
        cells=["#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"],
    ),
    "light": dict(
        fg="#1f2328", mu="#59636e", fa="#818b98", line="#d1d9e0", panel="#f6f8fa",
        panel2="#ffffff", ac="#0969da", ac2="#0550ae", gr="#1a7f37", warn="#9a6700",
        hot="#cf222e", cool="#0969da",
        cells=["#eff2f5", "#aceebb", "#4ac26b", "#2da44e", "#116329"],
    ),
}


def base_css(t):
    return (
        f".fg{{fill:{t['fg']}}}.mu{{fill:{t['mu']}}}.fa{{fill:{t['fa']}}}"
        f".ac{{fill:{t['ac']}}}.gr{{fill:{t['gr']}}}.hot{{fill:{t['hot']}}}"
        f".cool{{fill:{t['cool']}}}.warn{{fill:{t['warn']}}}"
        f".ln{{stroke:{t['line']};fill:none}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.probe{display:none}}"
    )


def svg(w, h, title, desc, body, css):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">'
        f'<title id="t">{title}</title><desc id="d">{desc}</desc>'
        f"<style>{css}</style>{body}</svg>"
    )
