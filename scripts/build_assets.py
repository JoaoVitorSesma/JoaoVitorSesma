"""Build every README asset: hero, walking strip and project cards.

    python scripts/build_assets.py

Outputs go to assets/ in English and Portuguese, light and dark, desktop and
mobile. Data comes from scripts/data (see assets/SOURCES.md).
"""

import json
from pathlib import Path

import cards
import sprite
from svgkit import MONO, MONO_MD, SERIF, SERIF_IT, THEMES, base_css, svg, text

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).parent / "data"
OUT = ROOT / "assets"

KM = json.loads((DATA / "km_curve.json").read_text())

STR = {
    "en": dict(
        cmd="whoami",
        tagline=["health data → survival models → tools people use"],
        tagline_m=["health data → survival models", "→ tools people use"],
        meta="Computer Engineering · Instituto Mauá de Tecnologia · Brazil",
        meta_m=["Computer Engineering", "Instituto Mauá de Tecnologia · Brazil"],
        now_label="now",
        now="recurrence modeling — Cox × ML",
        months="months",
        median="median 44 mo",
        fig1=" Colorectal cancer survival · FOSP · n = 37,621",
        fig1_m=" Colorectal cancer survival",
        fig1_m2="FOSP · n = 37,621 · 2000–2023",
        hero_title="João Vitor Sesma",
        hero_desc="João Vitor Sesma. Health data to survival models to tools people use. "
        "Computer Engineering at Instituto Mauá de Tecnologia, Brazil. Currently modeling "
        "recurrence with Cox and machine learning. Figure: Kaplan–Meier survival curve for "
        "colorectal cancer, FOSP, 37,621 patients, median survival 44 months.",
    ),
    "pt": dict(
        cmd="whoami",
        tagline=["dados de saúde → modelos de sobrevida → ferramentas"],
        tagline_m=["dados de saúde → modelos de sobrevida", "→ ferramentas"],
        meta="Engenharia de Computação · Instituto Mauá de Tecnologia · Brasil",
        meta_m=["Engenharia de Computação", "Instituto Mauá de Tecnologia · Brasil"],
        now_label="agora",
        now="modelando recidiva — Cox × ML",
        months="meses",
        median="mediana 44 meses",
        fig1=" Sobrevida no câncer colorretal · FOSP · n = 37.621",
        fig1_m=" Sobrevida no câncer colorretal",
        fig1_m2="FOSP · n = 37.621 · 2000–2023",
        hero_title="João Vitor Sesma",
        hero_desc="João Vitor Sesma. Dados de saúde para modelos de sobrevida para ferramentas. "
        "Engenharia de Computação no Instituto Mauá de Tecnologia, Brasil. Agora modelando "
        "recidiva com Cox e machine learning. Figura: curva de Kaplan–Meier do câncer "
        "colorretal, FOSP, 37.621 pacientes, sobrevida mediana de 44 meses.",
    ),
}


def rdp(points, eps):
    """Ramer–Douglas–Peucker simplification."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = (dx * dx + dy * dy) ** 0.5 or 1
    idx, dmax = 0, 0.0
    for i, (x, y) in enumerate(points[1:-1], 1):
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            idx, dmax = i, d
    if dmax > eps:
        return rdp(points[: idx + 1], eps)[:-1] + rdp(points[idx:], eps)
    return [points[0], points[-1]]


def km_figure(lang, t, x0, y0, w, h, delay, stroke=2.25, tick=12):
    """Kaplan–Meier plot drawn in place. Returns (body, css)."""
    s = STR[lang]
    sx = lambda m: x0 + m / 300 * w
    sy = lambda p: y0 + (1 - p) * h
    pts = [(sx(max(m, 0)), sy(p)) for m, p in KM]
    pts = rdp(pts, 0.35)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    parts = [
        f'<g class="axes"><path class="ln" stroke-width="1" d="M{x0} {y0 - 6} V{y0 + h} H{x0 + w}"/>',
    ]
    for p in (1.0, 0.5, 0.0):
        parts.append(text(MONO, f"{p:.1f}", x0 - 10, sy(p) + 4, tick, "fa", anchor="end")[0])
        if p != 0.0:
            parts.append(f'<path class="ln" stroke-dasharray="2 4" stroke-width="1" d="M{x0} {sy(p):.1f} H{x0 + w}"/>')
    for m in (0, 60, 120, 180, 240):
        parts.append(text(MONO, str(m), sx(m), y0 + h + 20, tick, "fa", anchor="middle")[0])
    parts.append(text(MONO, s["months"], x0 + w, y0 + h + 20, tick, "fa", anchor="end")[0] + "</g>")
    # median guide
    mx, my = sx(44), sy(0.5)
    parts.append(
        f'<g class="med"><path stroke="{t["ac"]}" stroke-width="1.25" stroke-dasharray="3 3" fill="none" '
        f'd="M{x0} {my:.1f} H{mx:.1f} V{y0 + h}"/>'
        f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4" fill="{t["ac"]}"/>'
        + text(MONO_MD, s["median"], mx + 10, my - 9, tick + 1, "ac")[0]
        + "</g>"
    )
    parts.append(
        f'<path class="km" pathLength="1" d="{d}" fill="none" stroke="{t["fg"]}" '
        f'stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    parts.append(
        f'<circle class="probe" r="4.5" fill="{t["ac"]}" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{delay + 4.2}s"/>'
        f'<animateMotion dur="11s" begin="{delay + 4.2}s" repeatCount="indefinite" path="{d}"/></circle>'
    )
    css = (
        f".km{{stroke-dasharray:1;animation:draw 3.4s cubic-bezier(.3,.7,.2,1) {delay}s both}}"
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        f".med{{animation:fade .8s ease {delay + 3.3}s both}}"
        f".axes{{animation:fade .6s ease {delay - .5:.2f}s both}}"
    )
    return "".join(parts), css


def type_line(font, s, x, y, size, cls, start, cps, uid):
    """A line that types itself in via a stepped clip. Returns (body, css, width, end)."""
    el, w = text(font, s, x, y, size, cls)
    n = len(s)
    dur = n / cps
    body = (
        f'<clipPath id="{uid}"><rect class="{uid}" x="{x - 2}" y="{y - size * 1.2:.1f}" '
        f'width="{w + 4:.1f}" height="{size * 1.6:.1f}"/></clipPath>'
        f'<g clip-path="url(#{uid})">{el}</g>'
    )
    css = (
        f".{uid}{{transform-box:fill-box;transform-origin:0 50%;"
        f"animation:type {dur:.2f}s steps({n}) {start:.2f}s both}}"
    )
    return body, css, w, start + dur


COMMON_KEYS = (
    "@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    "@keyframes pulse{0%{r:5;opacity:.55}70%,100%{r:14;opacity:0}}"
)


def hero(lang, theme, mobile):
    t, s = THEMES[theme], STR[lang]
    parts, css = [], [base_css(t), COMMON_KEYS]
    if mobile:
        W, H, x = 720, 900, 24
        prompt_y, name_y, name_size = 64, 168, 92
        tag_size, tag_y = 24, 236
    else:
        W, H, x = 1200, 400, 6
        prompt_y, name_y, name_size = 58, 160, 92
        tag_size, tag_y = 19, 214

    # prompt: ~/joao $ whoami
    p1, w1 = text(MONO, "~/joao $ ", x, prompt_y, tag_size - 2, "mu")
    parts.append(p1)
    b, c, _, t_end = type_line(MONO, s["cmd"], x + w1, prompt_y, tag_size - 2, "gr", 0.4, 9, "ty0")
    parts.append(b)
    css.append(c)

    # name
    n1, wn1 = text(SERIF, "João Vitor ", x, name_y, name_size, "fg")
    n2, _ = text(SERIF_IT, "Sesma", x + wn1, name_y, name_size, "ac")
    parts.append(f'<g class="name">{n1}{n2}</g>')
    css.append(f".name{{animation:rise .9s cubic-bezier(.2,.8,.2,1) {t_end + .15:.2f}s both}}")

    # tagline types in, cursor blinks after it
    lines = s["tagline_m"] if mobile else s["tagline"]
    start = t_end + 0.7
    y = tag_y
    for i, line in enumerate(lines):
        b, c, wl, start = type_line(MONO, line, x, y, tag_size, "fg", start, 26, f"ty{i + 1}")
        parts.append(b)
        css.append(c)
        last_w, last_y = wl, y
        y += tag_size * 1.55
    cw = tag_size * 0.6
    parts.append(
        f'<rect class="cur" x="{x + last_w + 4:.1f}" y="{last_y - tag_size * 0.82:.1f}" '
        f'width="{cw:.1f}" height="{tag_size * 1.05:.1f}" fill="{t["ac"]}"/>'
    )
    css.append(f".cur{{animation:fade .01s {start:.2f}s both,blink 1.1s steps(1) {start:.2f}s infinite}}")

    # meta + now
    meta_size = 15 if not mobile else 19
    y += 8 if not mobile else 6
    meta_lines = s["meta_m"] if mobile else [s["meta"]]
    g = []
    for line in meta_lines:
        g.append(text(MONO, line, x, y, meta_size, "mu")[0])
        y += meta_size * 1.6
    y += 14
    cx = x + 6
    g.append(
        f'<circle cx="{cx}" cy="{y - meta_size * 0.33:.1f}" r="5" fill="{t["gr"]}"/>'
        f'<circle class="pl" cx="{cx}" cy="{y - meta_size * 0.33:.1f}" r="5" fill="{t["gr"]}"/>'
    )
    lbl, wl = text(MONO_MD, s["now_label"], x + 22, y, meta_size, "gr")
    g.append(lbl)
    g.append(text(MONO, s["now"], x + 22 + wl + meta_size * 0.6, y, meta_size, "fg")[0])
    parts.append(f'<g class="meta">{"".join(g)}</g>')
    css.append(f".meta{{animation:fade .8s ease {start + .1:.2f}s both}}")
    css.append(f".pl{{animation:pulse 2.4s ease-out {start + .5:.2f}s infinite}}")

    # figure
    fig_delay = start + 0.2
    if mobile:
        fx, fy, fw, fh = x + 50, y + 70, W - x * 2 - 62, 300
        body, c = km_figure(lang, t, fx, fy, fw, fh, fig_delay, stroke=3, tick=16)
        cap_y = fy + fh + 66
        f1, wf = text(SERIF_IT, "Fig. 1", x, cap_y, 26, "fg")
        f2, _ = text(SERIF, s["fig1_m"], x + wf, cap_y, 26, "mu")
        f3, _ = text(MONO, s["fig1_m2"], x, cap_y + 32, 16, "fa")
        cap = f1 + f2 + f3
    else:
        fx, fy, fw, fh = 735, 44, 445, 262
        body, c = km_figure(lang, t, fx, fy, fw, fh, fig_delay)
        cap_y = fy + fh + 62
        f1, wf = text(SERIF_IT, "Fig. 1", fx - 34, cap_y, 23, "fg")
        f2, _ = text(SERIF, s["fig1"], fx - 34 + wf, cap_y, 23, "mu")
        cap = f1 + f2
    parts.append(body)
    parts.append(f'<g class="cap">{cap}</g>')
    css.append(c)
    css.append(f".cap{{animation:fade 1s ease {fig_delay + .4:.2f}s both}}")

    return svg(W, H, s["hero_title"], s["hero_desc"], "".join(parts), "".join(css))


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, k):
    a, b = _hex(a), _hex(b)
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(a, b))


def strip(theme, mobile):
    """A thin band where the pixel dragon walks back and forth over a row of
    contribution-style cells that light up under its feet."""
    t = THEMES[theme]
    W, period = (720, 22.0) if mobile else (1200, 32.0)
    px, cell, pitch = 3, 10, 14
    sw, sh = sprite.W * px, sprite.H * px
    top = 8
    cells_y = top + sh + 4
    H = cells_y + cell + 4
    travel = W - sw
    half = period / 2
    fade = 2.6

    # deterministic pseudo-random base levels (decorative, not real activity)
    seed = 7
    levels = []
    n = (W + pitch - cell) // pitch
    for _ in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        r = seed % 100
        levels.append(0 if r < 52 else 1 if r < 80 else 2 if r < 94 else 3)

    css = [base_css(t)]
    rects = []
    x0 = (W - (n * pitch - (pitch - cell))) / 2
    for i, lv in enumerate(levels):
        cx = x0 + i * pitch + cell / 2
        frac = min(max((cx - sw / 2) / travel, 0), 1)
        flashes = sorted({round(frac * half, 3), round(period - frac * half, 3) % period})
        base, hot = t["cells"][lv], t["cells"][4]

        def col(tt):
            best = 0.0
            for f in flashes:
                dt = (tt - f) % period
                if dt < fade:
                    best = max(best, 1 - dt / fade)
            return _mix(base, hot, best)

        marks = {0.0, period}
        for f in flashes:
            for d in (-0.05, 0.0, fade):
                marks.add(round((f + d) % period, 3))
        frames = "".join(
            f"{m / period * 100:.2f}%{{fill:{col(m if m < period else 0)}}}" for m in sorted(marks)
        )
        css.append(f"@keyframes c{i}{{{frames}}}.c{i}{{animation:c{i} {period}s linear infinite}}")
        rects.append(
            f'<rect class="c{i}" x="{x0 + i * pitch:.1f}" y="{cells_y}" width="{cell}" '
            f'height="{cell}" rx="2" fill="{base}"/>'
        )

    rest_x = round(travel * 0.42)
    fa = sprite.frame_rects(sprite.WALK_A, px)
    fb = sprite.frame_rects(sprite.WALK_B, px)
    css.append(
        f".walk{{transform:translate({rest_x}px,{top}px);animation:walk {period}s linear infinite}}"
        f"@keyframes walk{{0%{{transform:translate(0,{top}px)}}50%{{transform:translate({travel}px,{top}px)}}"
        f"100%{{transform:translate(0,{top}px)}}}}"
        ".flip{transform-box:fill-box;transform-origin:center;"
        f"animation:flip {period}s steps(1) infinite}}"
        "@keyframes flip{0%{transform:scaleX(1)}50%{transform:scaleX(-1)}100%{transform:scaleX(-1)}}"
        ".fa{animation:fa .44s steps(1) infinite}.fb{opacity:0;animation:fb .44s steps(1) infinite}"
        "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
    )
    body = (
        "".join(rects)
        + f'<g class="walk"><g class="flip"><g class="fa">{fa}</g><g class="fb">{fb}</g></g></g>'
    )
    return svg(
        W, H, "Walking dragon", "A small pixel-art dragon walking across a row of contribution squares.",
        body, "".join(css),
    )


def main():
    (OUT / "strip").mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            name = f"walk-{theme}{'-mobile' if mobile else ''}.svg"
            (OUT / "strip" / name).write_text(strip(theme, mobile))
    (OUT / "work").mkdir(parents=True, exist_ok=True)
    for kind, build in cards.BUILDERS.items():
        for lang in STR:
            for theme in THEMES:
                for mobile in (False, True):
                    name = f"{kind}-{lang}-{theme}{'-mobile' if mobile else ''}.svg"
                    (OUT / "work" / name).write_text(build(lang, theme, mobile))
    (OUT / "hero").mkdir(parents=True, exist_ok=True)
    for lang in STR:
        for theme in THEMES:
            for mobile in (False, True):
                name = f"hero-{lang}-{theme}{'-mobile' if mobile else ''}.svg"
                (OUT / "hero" / name).write_text(hero(lang, theme, mobile))


if __name__ == "__main__":
    main()
