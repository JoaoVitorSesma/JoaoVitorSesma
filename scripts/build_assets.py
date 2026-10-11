"""Build every README asset: hero, numbers, walking strip, project cards and buttons.

    python scripts/build_assets.py

Outputs go to assets/ in English and Portuguese, light and dark, desktop and
mobile. Data comes from scripts/data (see assets/SOURCES.md).
"""

from pathlib import Path

import cards
import creatures
from svgkit import MIN_PX, MONO, MONO_MD, SANS, SANS_BD, THEMES, base_css, canvas, scale, smallest, svg, text, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"


STR = {
    "en": dict(
        cmd="whoami",
        name="João Vitor Morimoto Sesma",
        name_lines=["João Vitor", "Morimoto Sesma"],
        tagline="Health data, survival models and the tools people use.",
        # Only what the profile sidebar does not already show (name aside).
        rows=[("drawn to", "AI for healthcare, data analysis and automation"),
              ("now", "building ML and deep learning models for medical diagnosis"),
              ("learning", "LLMs (building and using them) and computer vision")],
        stats=[("37,621", "patients modeled"), ("55,647", "records visualized"), ("96", "automated checks a day")],
        cta_main="Get in touch · Email me",
        cta_alt="See projects",
        hero_title="João Vitor Morimoto Sesma",
        hero_desc="João Vitor Morimoto Sesma. "
        "Health data, survival models and the tools people use. Drawn to AI for healthcare, data "
        "analysis and automation. Now building ML and deep learning models for medical diagnosis. "
        "Learning LLMs, building and using them, and computer vision.",
    ),
    "pt": dict(
        cmd="whoami",
        name="João Vitor Morimoto Sesma",
        name_lines=["João Vitor", "Morimoto Sesma"],
        tagline="Dados de saúde, modelos de sobrevida e as ferramentas que as pessoas usam.",
        rows=[("interesses", "IA para saúde, análise de dados e automação"),
              ("agora", "construindo modelos de ML e deep learning para diagnóstico médico"),
              ("aprendendo", "LLMs (construindo e usando) e visão computacional")],
        stats=[("37.621", "pacientes modelados"), ("55.647", "registros visualizados"), ("96", "verificações automáticas por dia")],
        cta_main="Fale comigo · E-mail",
        cta_alt="Ver projetos",
        hero_title="João Vitor Morimoto Sesma",
        hero_desc="João Vitor Morimoto Sesma. "
        "Dados de saúde, modelos de sobrevida e as ferramentas que as pessoas usam. Interesses: IA para "
        "saúde, análise de dados e automação. Agora construindo modelos de ML e deep learning para "
        "diagnóstico médico. Aprendendo LLMs, construindo e usando, e visão computacional.",
    ),
}


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
    """Who I am in a few seconds: name, one line, and the whoami
    answers the profile sidebar does not already show."""
    t, s = THEMES[theme], STR[lang]
    parts, css = [], [base_css(t), COMMON_KEYS]
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    x = r(10) if mobile else r(4)
    full = W - 2 * x

    y = r(18)

    # 0.1 s: prompt types, name rises right away
    p1, w1 = text(MONO, "~/joao $ ", x, y, r(13), "mu")
    parts.append(p1)
    b_, c_, _, _ = type_line(MONO, s["cmd"], x + w1, y, r(13), "gr", 0.1, 12, "ty0")
    parts.append(b_)
    css.append(c_)
    lines = s["name_lines"] if mobile else [s["name"]]
    size = min(r(46), min(full / SANS_BD.width(l, 1) for l in lines) * 0.98)
    g = []
    for i, line in enumerate(lines):
        y += size * (1.12 if i == 0 else 1.08)
        g.append(text(SANS_BD, line, x, y, size, "fg", tracking=-size * 0.01)[0])
    parts.append(f'<g class="name">{"".join(g)}</g>')
    css.append(".name{animation:rise .7s cubic-bezier(.2,.8,.2,1) .15s both}")

    # 0.4 s: one line on what I do
    tag = r(15 if mobile else 16)
    y += tag * 1.8
    tl = []
    for line in wrap(SANS, s["tagline"], tag, full):
        tl.append(text(SANS, line, x, y, tag, "fg")[0])
        y += tag * 1.4
    parts.append(f'<g class="tag">{"".join(tl)}</g>')
    css.append(".tag{animation:rise .7s cubic-bezier(.2,.8,.2,1) .4s both}")

    # 0.7 s on: whoami answers, one by one
    fs = r(13 if mobile else 13.5)
    y += fs * 0.8
    rows = s["rows"]
    cols = 1 if mobile or len(rows) <= 3 else 2  # a short list reads best as one column
    gap = r(28)
    col_w = (full - gap * (cols - 1)) / cols
    keyw = max(MONO.width(k, fs) for k, _ in rows) + r(16)
    per_col = -(-len(rows) // cols)
    # rows are laid out as a grid: entry k sits in column k // per_col, line k % per_col,
    # and every grid line is as tall as its tallest entry, so the columns stay aligned
    wrapped = [wrap(SANS, v, fs, col_w - keyw) for _, v in rows]
    cy = y + fs * 1.2
    for line_i in range(per_col):
        members = [ci * per_col + line_i for ci in range(cols) if ci * per_col + line_i < len(rows)]
        for idx in members:
            k, _ = rows[idx]
            cx = x + (idx // per_col) * (col_w + gap)
            is_now = idx == 1
            row = [text(MONO, k, cx, cy, fs, "gr" if is_now else "ac")[0]]
            if is_now:
                dx = cx + MONO.width(k, fs) + r(8)
                dy = cy - fs * 0.33
                row.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{r(3):.1f}" fill="{t["gr"]}"/>'
                           f'<circle class="pl" cx="{dx:.1f}" cy="{dy:.1f}" r="{r(3):.1f}" fill="{t["gr"]}"/>')
            for j, line in enumerate(wrapped[idx]):
                row.append(text(SANS, line, cx + keyw, cy + j * fs * 1.35, fs, "fg")[0])
            parts.append(f'<g class="r{idx}">{"".join(row)}</g>')
            css.append(f".r{idx}{{animation:rise .45s ease {0.7 + idx * 0.2:.2f}s both}}")
        tallest = max(len(wrapped[idx]) for idx in members)
        cy += fs * 1.35 * (tallest - 1) + fs * 1.8
    bottoms = [cy - fs * 0.8]
    css.append(".pl{animation:pulse 2.4s ease-out 1.6s infinite}")
    H = int(max(bottoms) + r(12))
    return svg(W, H, s["hero_title"], s["hero_desc"], "".join(parts), "".join(css))


def numbers(lang, theme, mobile):
    """The three project numbers, static, opening the Selected work section."""
    t, s = THEMES[theme], STR[lang]
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    x = r(4)
    colw = (W - 2 * x) / 3
    num, lab = r(22), r(12.5)
    parts = []
    y = num * 1.1
    rows = 1
    for i, (v, label) in enumerate(s["stats"]):
        parts.append(text(MONO_MD, v, x + i * colw, y, num, "fg")[0])
        lines = wrap(SANS, label, lab, colw - r(10))
        rows = max(rows, len(lines))
        for j, line in enumerate(lines):
            parts.append(text(SANS, line, x + i * colw, y + lab * (1.6 + 1.3 * j), lab, "mu")[0])
    H = int(y + lab * (1.6 + 1.3 * (rows - 1)) + r(8))
    alt = ", ".join(f"{v} {label}" for v, label in s["stats"])
    return svg(W, H, alt, alt, "".join(parts), base_css(t))


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


CTA_GREEN = {"dark": "#238636", "light": "#1f883d"}


def cta_pill(label, primary, theme):
    """Call-to-action button: solid green for the main action, outline for the second."""
    t, k = THEMES[theme], 2
    scale(k)
    fs, h, pad = 14 * k, 34 * k, 15 * k
    font = SANS_BD
    lx = pad
    dot = ""
    if primary:
        r_ = 3.5 * k
        dot = f'<circle cx="{pad + r_:.1f}" cy="{h / 2:.1f}" r="{r_:.1f}" fill="#ffffff"/>'
        lx = pad + r_ * 2 + 8 * k
    w = lx + font.width(label, fs) + pad
    if primary:
        frame = f'<rect width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{CTA_GREEN[theme]}"/>'
        el, _ = text(font, label, lx, h / 2 + fs * 0.36, fs, "fg")
        el = el.replace('class="fg"', 'fill="#ffffff"')
    else:
        frame = (f'<rect x="{k / 2}" y="{k / 2}" width="{w - k:.1f}" height="{h - k}" rx="{(h - k) / 2}" '
                 f'fill="none" stroke="{t["line"]}" stroke-width="{k}"/>')
        el, _ = text(font, label, lx, h / 2 + fs * 0.36, fs, "fg")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / k:.0f}" height="{h / k:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{label}"><title>{label}</title>'
            f'<style>{base_css(t)}</style>{frame}{dot}{el}</svg>')


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
                write(OUT / "work" / f"numbers-{sfx}", numbers(lang, theme, mobile))

    for theme in THEMES:
        write(OUT / "lang" / f"globe-{theme}.svg", lang_globe(theme))
        for lang in LANGS:
            for active in (True, False):
                write(OUT / "lang" / f"{lang}-{'active' if active else 'idle'}-{theme}.svg", lang_pill(lang, active, theme))

    for lang in STR:
        for theme in THEMES:
            write(OUT / "cta" / f"main-{lang}-{theme}.svg", cta_pill(STR[lang]["cta_main"], True, theme))
            write(OUT / "cta" / f"alt-{lang}-{theme}.svg", cta_pill(STR[lang]["cta_alt"], False, theme))

    print("smallest text as rendered on GitHub (px):")
    for size, name, sample in sorted(report)[:6]:
        print(f"  {size:5.1f}  {name:32} {sample!r}")
    if failures:
        raise SystemExit(f"{len(failures)} assets have text under {MIN_PX}px: {failures[:4]}")


if __name__ == "__main__":
    main()
