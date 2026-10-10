"""Build every README asset: hero, walking strip and project cards.

    python scripts/build_assets.py

Outputs go to assets/ in English and Portuguese, light and dark, desktop and
mobile. Data comes from scripts/data (see assets/SOURCES.md).
"""

import json
from pathlib import Path

import cards
import sprite
from svgkit import MIN_PX, MONO, MONO_MD, SERIF, SERIF_IT, THEMES, base_css, canvas, smallest, svg, text

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).parent / "data"
OUT = ROOT / "assets"

KM = json.loads((DATA / "km_curve.json").read_text())

STR = {
    "en": dict(
        cmd="whoami",
        tagline_m=["health data → survival models", "→ tools people use"],
        tagline_m3=["health data →", "survival models →", "tools people use"],
        meta_m=["Computer Engineering", "Instituto Mauá de Tecnologia · Brazil"],
        now_label="now",
        now="recurrence modeling — Cox × ML",
        months="months",
        median="median 44 months",
        fig1_a=" Colorectal cancer survival",
        fig1_b="FOSP · n = 37,621 · 2000–2023",
        hero_title="João Vitor Sesma",
        hero_desc="João Vitor Sesma. Health data to survival models to tools people use. "
        "Computer Engineering at Instituto Mauá de Tecnologia, Brazil. Currently modeling "
        "recurrence with Cox and machine learning. Figure: Kaplan–Meier survival curve for "
        "colorectal cancer, FOSP, 37,621 patients, median survival 44 months.",
    ),
    "pt": dict(
        cmd="whoami",
        tagline_m=["dados de saúde → modelos de sobrevida", "→ ferramentas"],
        tagline_m3=["dados de saúde →", "modelos de sobrevida →", "ferramentas"],
        meta_m=["Engenharia de Computação", "Instituto Mauá de Tecnologia · Brasil"],
        now_label="agora",
        now="modelando recidiva — Cox × ML",
        months="meses",
        median="mediana 44 meses",
        fig1_a=" Sobrevida no câncer colorretal",
        fig1_b="FOSP · n = 37.621 · 2000–2023",
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


def km_figure(lang, t, x0, y0, w, h, delay, r, tick):
    """Kaplan–Meier plot drawn in place. `tick` is the label size in SVG units."""
    s = STR[lang]
    sx = lambda m: x0 + m / 300 * w
    sy = lambda p: y0 + (1 - p) * h
    pts = [(sx(max(m, 0)), sy(p)) for m, p in KM]
    pts = rdp(pts, 0.35)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    sw = r(1)
    parts = [f'<g class="axes"><path class="ln" stroke-width="{sw:.2f}" d="M{x0} {y0 - r(4):.1f} V{y0 + h} H{x0 + w}"/>']
    for p in (1.0, 0.5, 0.0):
        parts.append(text(MONO, f"{p:.1f}", x0 - r(7), sy(p) + tick * 0.35, tick, "fa", anchor="end")[0])
        if p != 0.0:
            parts.append(
                f'<path class="ln" stroke-dasharray="{r(1.5):.1f} {r(3):.1f}" stroke-width="{sw:.2f}" '
                f'd="M{x0} {sy(p):.1f} H{x0 + w}"/>'
            )
    ty = y0 + h + tick * 1.45
    for m in (0, 60, 120, 180):
        parts.append(text(MONO, str(m), sx(m), ty, tick, "fa", anchor="middle")[0])
    parts.append(text(MONO, s["months"], x0 + w, ty, tick, "fa", anchor="end")[0] + "</g>")
    mx, my = sx(44), sy(0.5)
    parts.append(
        f'<g class="med"><path stroke="{t["ac"]}" stroke-width="{r(1.1):.2f}" stroke-dasharray="{r(2.5):.1f} {r(2.5):.1f}" '
        f'fill="none" d="M{x0} {my:.1f} H{mx:.1f} V{y0 + h}"/>'
        f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r(3.5):.1f}" fill="{t["ac"]}"/>'
        + text(MONO_MD, s["median"], mx + r(8), my - r(8), tick, "ac")[0]
        + "</g>"
    )
    parts.append(
        f'<path class="km" pathLength="1" d="{d}" fill="none" stroke="{t["fg"]}" '
        f'stroke-width="{r(2):.2f}" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    parts.append(
        f'<circle class="probe" r="{r(3.8):.1f}" fill="{t["ac"]}" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{delay + 4.2:.2f}s"/>'
        f'<animateMotion dur="11s" begin="{delay + 4.2:.2f}s" repeatCount="indefinite" path="{d}"/></circle>'
    )
    css = (
        f".km{{stroke-dasharray:1;animation:draw 3.4s cubic-bezier(.3,.7,.2,1) {delay:.2f}s both}}"
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        f".med{{animation:fade .8s ease {delay + 3.3:.2f}s both}}"
        f".axes{{animation:fade .6s ease {delay - .5:.2f}s both}}"
    )
    return "".join(parts), css, ty


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
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    x = r(10) if mobile else r(4)
    # sizes in rendered px
    prompt, tag, meta, tick, cap = (13, 15, 13, 12.5, 13) if mobile else (13, 16, 13.5, 12.5, 13.5)
    prompt, tag, meta, tick, cap = r(prompt), r(tag), r(meta), r(tick), r(cap)
    col_w = (W - 2 * x) if mobile else r(440)

    y = r(30)
    p1, w1 = text(MONO, "~/joao $ ", x, y, prompt, "mu")
    parts.append(p1)
    b, c, _, t_end = type_line(MONO, s["cmd"], x + w1, y, prompt, "gr", 0.4, 9, "ty0")
    parts.append(b)
    css.append(c)

    # name: as large as the column allows, capped
    name_size = min(r(64), col_w / (SERIF.width("João Vitor ", 1) + SERIF_IT.width("Sesma", 1)) * 0.98)
    y += name_size * 1.0
    n1, wn1 = text(SERIF, "João Vitor ", x, y, name_size, "fg")
    n2, _ = text(SERIF_IT, "Sesma", x + wn1, y, name_size, "ac")
    parts.append(f'<g class="name">{n1}{n2}</g>')
    css.append(f".name{{animation:rise .9s cubic-bezier(.2,.8,.2,1) {t_end + .15:.2f}s both}}")

    lines = s["tagline_m3"] if mobile else s["tagline_m"]
    start = t_end + 0.7
    y += tag * 2.0
    for i, line in enumerate(lines):
        b, c, wl, start = type_line(MONO, line, x, y, tag, "fg", start, 26, f"ty{i + 1}")
        parts.append(b)
        css.append(c)
        last_w, last_y = wl, y
        y += tag * 1.5
    parts.append(
        f'<rect class="cur" x="{x + last_w + tag * 0.25:.1f}" y="{last_y - tag * 0.82:.1f}" '
        f'width="{tag * 0.6:.1f}" height="{tag * 1.05:.1f}" fill="{t["ac"]}"/>'
    )
    css.append(f".cur{{animation:fade .01s {start:.2f}s both,blink 1.1s steps(1) {start:.2f}s infinite}}")

    y += meta * 0.5
    g = []
    for line in s["meta_m"]:
        g.append(text(MONO, line, x, y, meta, "mu")[0])
        y += meta * 1.5
    y += meta * 0.6
    cy = y - meta * 0.33
    dot = r(4)
    g.append(
        f'<circle cx="{x + dot:.1f}" cy="{cy:.1f}" r="{dot:.1f}" fill="{t["gr"]}"/>'
        f'<circle class="pl" cx="{x + dot:.1f}" cy="{cy:.1f}" r="{dot:.1f}" fill="{t["gr"]}"/>'
    )
    lx = x + dot * 2 + meta * 0.6
    lbl, wl = text(MONO_MD, s["now_label"], lx, y, meta, "gr")
    g.append(lbl)
    g.append(text(MONO, s["now"], lx + wl + meta * 0.6, y, meta, "fg")[0])
    parts.append(f'<g class="meta">{"".join(g)}</g>')
    css.append(f".meta{{animation:fade .8s ease {start + .1:.2f}s both}}")
    css.append(f".pl{{animation:pulse 2.4s ease-out {start + .5:.2f}s infinite}}")
    left_bottom = y

    fig_delay = start + 0.2
    if mobile:
        fx = x + tick * 2.4
        fy = y + r(40)
        fw, fh = W - x - fx, r(150)
        cap_x = x
    else:
        fx, fy = r(500), r(34)
        fw, fh = W - x - fx, r(165)
        cap_x = fx - tick * 2.4
    body, c, ty = km_figure(lang, t, fx, fy, fw, fh, fig_delay, r, tick)
    cap_y = ty + cap * 2.6
    f1, wf = text(MONO_MD, "FIG. 1", cap_x, cap_y, tick, "ac")
    indent = wf + cap * 0.8
    f2, _ = text(MONO, s["fig1_a"].strip(), cap_x + indent, cap_y, cap, "mu")
    f3, _ = text(MONO, s["fig1_b"], cap_x + indent, cap_y + cap * 1.5, tick, "fa")
    parts.append(body)
    parts.append(f'<g class="cap">{f1}{f2}{f3}</g>')
    css.append(c)
    css.append(f".cap{{animation:fade 1s ease {fig_delay + .4:.2f}s both}}")
    H = int(max(cap_y + cap * 1.5, left_bottom) + r(14))
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
    canvas(W, mobile)
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
    report, failures = [], []

    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        size, sample = smallest()
        if size is not None:
            report.append((size, path.name, sample))
            if size < MIN_PX - 0.01:
                failures.append(path.name)

    for theme in THEMES:
        for mobile in (False, True):
            write(OUT / "strip" / f"walk-{theme}{'-mobile' if mobile else ''}.svg", strip(theme, mobile))
    for lang in STR:
        for theme in THEMES:
            for mobile in (False, True):
                sfx = f"{lang}-{theme}{'-mobile' if mobile else ''}.svg"
                for kind, build in cards.BUILDERS.items():
                    write(OUT / "work" / f"{kind}-{sfx}", build(lang, theme, mobile))
                write(OUT / "hero" / f"hero-{sfx}", hero(lang, theme, mobile))

    print("smallest text as rendered on GitHub (px):")
    for size, name, sample in sorted(report)[:6]:
        print(f"  {size:5.1f}  {name:32} {sample!r}")
    if failures:
        raise SystemExit(f"{len(failures)} assets have text under {MIN_PX}px: {failures[:4]}")


if __name__ == "__main__":
    main()
