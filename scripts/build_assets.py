"""Build every README asset: hero, walking strip and project cards.

    python scripts/build_assets.py

Outputs go to assets/ in English and Portuguese, light and dark, desktop and
mobile. Data comes from scripts/data (see assets/SOURCES.md).
"""

import json
from pathlib import Path

import cards
import creatures
from svgkit import MIN_PX, MONO, MONO_MD, SANS, SANS_BD, THEMES, base_css, canvas, scale, smallest, svg, text, wrap

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).parent / "data"
OUT = ROOT / "assets"

KM = json.loads((DATA / "km_curve.json").read_text())

STR = {
    "en": dict(
        cmd="whoami",
        tagline="Health data, survival models and the tools people use.",
        meta_m=["Computer Engineering", "Instituto Mauá de Tecnologia · Brazil"],
        now_label="now",
        now="modeling recurrence with Cox and machine learning",
        months="months",
        median="median 44 months",
        fig1_a=" Colorectal cancer survival",
        fig1_b="FOSP · n = 37,621 · 2000–2023",
        hero_title="João Vitor Sesma",
        hero_desc="João Vitor Sesma. Health data, survival models and the tools people use. "
        "Computer Engineering at Instituto Mauá de Tecnologia, Brazil. Currently modeling "
        "recurrence with Cox and machine learning. Figure: Kaplan–Meier survival curve for "
        "colorectal cancer, FOSP, 37,621 patients, median survival 44 months.",
    ),
    "pt": dict(
        cmd="whoami",
        tagline="Dados de saúde, modelos de sobrevida e as ferramentas que as pessoas usam.",
        meta_m=["Engenharia de Computação", "Instituto Mauá de Tecnologia · Brasil"],
        now_label="agora",
        now="modelando recidiva com Cox e machine learning",
        months="meses",
        median="mediana 44 meses",
        fig1_a=" Sobrevida no câncer colorretal",
        fig1_b="FOSP · n = 37.621 · 2000–2023",
        hero_title="João Vitor Sesma",
        hero_desc="João Vitor Sesma. Dados de saúde, modelos de sobrevida e as ferramentas que as pessoas usam. "
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
    name_size = min(r(52), col_w / SANS_BD.width("João Vitor Sesma", 1) * 0.98)
    y += name_size * 1.05
    n1, _ = text(SANS_BD, "João Vitor Sesma", x, y, name_size, "fg", tracking=-name_size * 0.01)
    parts.append(f'<g class="name">{n1}</g>')
    css.append(f".name{{animation:rise .9s cubic-bezier(.2,.8,.2,1) {t_end + .15:.2f}s both}}")

    start = t_end + 0.5
    y += tag * 1.9
    tl = []
    for line in wrap(SANS, s["tagline"], tag, col_w):
        tl.append(text(SANS, line, x, y, tag, "fg")[0])
        y += tag * 1.4
    parts.append(f'<g class="tag">{"".join(tl)}</g>')
    css.append(f".tag{{animation:rise .8s cubic-bezier(.2,.8,.2,1) {start:.2f}s both}}")
    start += 0.6
    y += meta * 0.5
    g = []
    for line in s["meta_m"]:
        g.append(text(SANS, line, x, y, meta, "mu")[0])
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
    nx = lx + wl + meta * 0.6
    for i, line in enumerate(wrap(SANS, s["now"], meta, x + col_w - nx)):
        if i:
            y += meta * 1.4
        g.append(text(SANS, line, nx, y, meta, "fg")[0])
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
    f2, _ = text(SANS, s["fig1_a"].strip(), cap_x + indent, cap_y, cap, "mu")
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


MASCOT = "hedgehog"  # one of creatures.CREATURES: silver, egg, mecha, blob, hedgehog


# Each trip across the strip: direction (+1 right, -1 left) and whether it rolls.
# The first trip always rolls; later ones mix plain walks in.
TRIPS = [(+1, True), (-1, False), (+1, False), (-1, True)]
# Roll trip: (phase, share of the trip's duration, speed relative to walking)
ROLL_PLAN = [("walk", 0.30, 1.0), ("crouch", 0.03, 0.3), ("curl", 0.03, 0.3), ("ball", 0.26, 3.0),
             ("curl", 0.03, 0.3), ("crouch", 0.03, 0.3), ("walk", 0.32, 1.0)]


def _motion(travel, walk_time, roll):
    """Keyframes for a full cycle at a constant walking speed.

    walk_time is how long a plain walking trip takes. Returns
    (period, stops [(t, x)], spans {phase: [(t0, t1)]}, trips [(t0, direction)]).
    """
    trips = TRIPS if roll else [(+1, False), (-1, False)]
    speed = travel / walk_time
    roll_time = travel / (speed * sum(f * v for _, f, v in ROLL_PLAN))
    t, stops, spans, starts = 0.0, [(0.0, 0.0)], {"walk": [], "crouch": [], "curl": [], "ball": []}, []
    for direction, rolls in trips:
        starts.append((t, direction))
        x_from = 0.0 if direction > 0 else travel
        plan = ROLL_PLAN if rolls else [("walk", 1.0, 1.0)]
        dur = roll_time if rolls else walk_time
        x = x_from
        for phase, f, v in plan:
            dt = f * dur
            spans[phase].append((t, t + dt))
            t += dt
            x += direction * speed * v * dt
            stops.append((t, min(max(x, 0.0), travel)))
        stops[-1] = (t, travel if direction > 0 else 0.0)
    return t, stops, spans, starts


def strip(theme, mobile, mascot=None):
    """A thin band where the mascot crosses a row of contribution-style cells
    that light up under it, turning round at each end."""
    t = THEMES[theme]
    canvas(720 if mobile else 1200, mobile)
    name = mascot or MASCOT
    pal, frames, gw, gh = creatures.get(name)
    roll = creatures.CREATURES[name].get("roll")
    W, walk_time = (720, 14.0) if mobile else (1200, 20.0)
    px, cell, pitch = 3, 10, 14
    sw, sh = gw * px, gh * px
    top = 8
    cells_y = top + sh + 4
    H = cells_y + cell + 4
    travel = W - sw
    fade = 2.6
    period, stops, spans, trips = _motion(travel, walk_time, roll)

    def pass_times(cx):
        """Moments when the mascot's centre crosses x = cx."""
        target, out = cx - sw / 2, []
        for (t0, x0), (t1, x1) in zip(stops, stops[1:]):
            lo, hi = min(x0, x1), max(x0, x1)
            if lo <= target <= hi and x1 != x0:
                out.append(round(t0 + (target - x0) / (x1 - x0) * (t1 - t0), 3) % period)
        out = sorted(set(out))
        return [v for i, v in enumerate(out) if i == 0 or v - out[i - 1] > 0.05] or [0.0]

    seed, levels = 7, []
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
        flashes = pass_times(min(max(cx, sw / 2), W - sw / 2))
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
        steps = "".join(
            f"{m / period * 100:.2f}%{{fill:{col(m if m < period else 0)}}}" for m in sorted(marks)
        )
        css.append(f"@keyframes c{i}{{{steps}}}.c{i}{{animation:c{i} {period}s linear infinite}}")
        rects.append(
            f'<rect class="c{i}" x="{x0 + i * pitch:.1f}" y="{cells_y}" width="{cell}" '
            f'height="{cell}" rx="2" fill="{base}"/>'
        )

    rest_x = round(travel * 0.42)
    walk_kf = "".join(f"{tt / period * 100:.3f}%{{transform:translate({xx:.1f}px,{top}px)}}" for tt, xx in stops)
    css.append(
        f".walk{{transform:translate({rest_x}px,{top}px);animation:walk {period}s linear infinite}}"
        f"@keyframes walk{{{walk_kf}}}"
        ".flip{transform-box:fill-box;transform-origin:center;"
        f"animation:flip {period}s steps(1) infinite}}"
        "@keyframes flip{"
        + "".join(f"{t0 / period * 100:.3f}%{{transform:scaleX({d})}}" for t0, d in trips)
        + f"100%{{transform:scaleX({trips[-1][1]})}}}}"
        ".fa{animation:fa .44s steps(1) infinite}.fb{opacity:0;animation:fb .44s steps(1) infinite}"
        "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
    )
    rf = lambda k: creatures.frame_rects(pal, frames[k], px)
    if not roll:
        body = f'<g class="fa">{rf(0)}</g><g class="fb">{rf(1)}</g>'
    else:
        # which pose is visible when: crouch/curl split their phases in two
        groups = spans

        def vis(cls, spans, base_on):
            merged = []
            for a_, b_ in sorted(spans):
                if merged and a_ <= merged[-1][1] + 1e-6:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], b_))
                else:
                    merged.append((a_, b_))
            kf = [] if merged and merged[0][0] <= 0 else ["0%{opacity:0}"]
            for a_, b_ in merged:
                pa, pb = a_ / period * 100, b_ / period * 100
                if pa > 0:
                    kf.append(f"{pa - .001:.3f}%{{opacity:0}}")
                kf.append(f"{pa:.3f}%{{opacity:1}}{pb:.3f}%{{opacity:1}}")
                if pb < 100:
                    kf.append(f"{pb + .001:.3f}%{{opacity:0}}")
            if not (merged and merged[-1][1] >= period):
                kf.append("100%{opacity:0}")
            return (f".{cls}{{opacity:{1 if base_on else 0};animation:{cls} {period}s linear infinite}}"
                    f"@keyframes {cls}{{{''.join(kf)}}}")

        css.append(vis("gw", groups["walk"], True))
        css.append(vis("gc", groups["crouch"], False))
        css.append(vis("gu", groups["curl"], False))
        css.append(vis("gb", groups["ball"], False))
        css.append(".spin{transform-box:fill-box;transform-origin:center;animation:spin .5s steps(4) infinite}"
                   "@keyframes spin{to{transform:rotate(360deg)}}")
        w0, w1 = roll["walk"]
        c0, c1 = roll["curl"]
        body = (
            f'<g class="gw"><g class="fa">{rf(w0)}</g><g class="fb">{rf(w1)}</g></g>'
            f'<g class="gc">{rf(c0)}</g><g class="gu">{rf(c1)}</g>'
            f'<g class="gb"><g class="spin">{rf(roll["ball"])}</g></g>'
        )
    return svg(
        W, H, "Walking mascot",
        "A small pixel-art hedgehog walking across a row of contribution squares, curling up and rolling along part of the way."
        if roll else "A small pixel-art creature walking across a row of contribution squares.",
        "".join(rects) + f'<g class="walk" shape-rendering="crispEdges"><g class="flip">{body}</g></g>', "".join(css),
    )


LANGS = {"en": "English", "pt": "Português"}


def lang_pill(lang, active, theme):
    """Language button: filled pill for the current language, outline for the other."""
    t, k = THEMES[theme], 2
    scale(k)
    fs, h, pad = 13.5 * k, 30 * k, 13 * k
    font = SANS_BD if active else SANS
    label = LANGS[lang]
    w = pad * 2 + font.width(label, fs)
    if active:
        frame = (f'<rect x="{k / 2}" y="{k / 2}" width="{w - k:.1f}" height="{h - k}" rx="{(h - k) / 2}" '
                 f'fill="{t["ac"]}" fill-opacity=".14" stroke="{t["ac"]}" stroke-width="{k}"/>')
    else:
        frame = (f'<rect x="{k / 2}" y="{k / 2}" width="{w - k:.1f}" height="{h - k}" rx="{(h - k) / 2}" '
                 f'fill="none" stroke="{t["line"]}" stroke-width="{k}"/>')
    el, _ = text(font, label, pad, h / 2 + fs * 0.36, fs, "fg" if active else "mu")
    title = f"{label} (current)" if active else label
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / k:.0f}" height="{h / k:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{title}"><title>{title}</title>'
            f'<style>{base_css(t)}</style>{frame}{el}</svg>')


def lang_globe(theme):
    t, k = THEMES[theme], 2
    s, r = 30 * k, 7.5 * k
    c = s / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="30" viewBox="{c - 11 * k} 0 {22 * k} {s}" '
            f'role="img" aria-label="Language"><title>Language</title>'
            f'<g fill="none" stroke="{t["mu"]}" stroke-width="{1.4 * k}">'
            f'<circle cx="{c}" cy="{c}" r="{r}"/><ellipse cx="{c}" cy="{c}" rx="{r * 0.45}" ry="{r}"/>'
            f'<path d="M{c - r} {c} H{c + r}"/></g></svg>')


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

    for theme in THEMES:
        write(OUT / "lang" / f"globe-{theme}.svg", lang_globe(theme))
        for lang in LANGS:
            for active in (True, False):
                write(OUT / "lang" / f"{lang}-{'active' if active else 'idle'}-{theme}.svg", lang_pill(lang, active, theme))

    print("smallest text as rendered on GitHub (px):")
    for size, name, sample in sorted(report)[:6]:
        print(f"  {size:5.1f}  {name:32} {sample!r}")
    if failures:
        raise SystemExit(f"{len(failures)} assets have text under {MIN_PX}px: {failures[:4]}")


if __name__ == "__main__":
    main()
