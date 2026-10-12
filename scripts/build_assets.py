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
        # Hero: the sidebar already says who I am, so the hero only makes the claim.
        kicker="FULL-STACK AI",
        head=[[("From the cluster", "fg")], [("to ", "fg"), ("the people.", "or")]],
        sub="Infrastructure, models and the interfaces people actually use. I work across all three.",
        loop="user feedback",
        stages=[("Infrastructure", "clusters · data"), ("Models", "LLMs · vision"),
                ("Interfaces", "apps · dashboards")],
        hero_title="From the cluster to the people.",
        hero_desc="From the cluster to the people. Infrastructure, models and the interfaces people "
        "actually use: clusters and data feed models such as LLMs and vision, which feed apps and "
        "dashboards, with user feedback flowing back into the models.",
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
        kicker="IA FULL-STACK",
        head=[[("Do cluster", "fg")], [("às ", "fg"), ("pessoas.", "or")]],
        sub="Infraestrutura, modelos e as interfaces que as pessoas usam de fato. Atuo nas três.",
        loop="feedback de uso",
        stages=[("Infraestrutura", "clusters · dados"), ("Modelos", "LLMs · visão"),
                ("Interfaces", "apps · dashboards")],
        hero_title="Do cluster às pessoas.",
        hero_desc="Do cluster às pessoas. Infraestrutura, modelos e as interfaces que as pessoas usam "
        "de fato: clusters e dados alimentam modelos como LLMs e visão computacional, que alimentam "
        "apps e dashboards, com o feedback de uso voltando para os modelos.",
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


ORANGE = {"light": "#bc4c00", "dark": "#f0883e"}

# The three pipeline icons are cut from my renders in scripts/icons/ by cut_icons.py
# and embedded as PNG: an <img> SVG on GitHub cannot load anything external.
ICON_DIR = Path(__file__).parent / "icons"
ICON_NAMES = ("infra", "models", "ui")
ICON_H = {"infra": 1.24, "models": 0.93, "ui": 1.12}  # height, in units of 0.6 column
ICON_STYLE = {
    "light": dict(arrow="#54758a", top="#a5becb", bottom="#36566a", edge="#36566a", label="#426779", glow=0.0),
    "dark": dict(arrow="#86a5b9", top="#c8dde7", bottom="#3c596f", edge="#3c596f", label="#a0b8c7", glow=0.0),
}


def _icon(name, theme):
    import base64
    from PIL import Image
    path = ICON_DIR / f"{name}-{theme}.png"
    w, h = Image.open(path).size
    return base64.b64encode(path.read_bytes()).decode(), w, h


def _arrow(fill, edge, x1, x2, y, sc):
    h, hl, hw = 3 * sc, 13 * sc, 9 * sc
    return (f'<path d="M{x1:.1f} {y - h:.1f} H{x2 - hl:.1f} V{y - hw:.1f} L{x2:.1f} {y:.1f} '
            f'L{x2 - hl:.1f} {y + hw:.1f} V{y + h:.1f} H{x1:.1f} Z" fill="{fill}" '
            f'stroke="{edge}" stroke-width="{sc * 0.7:.1f}" stroke-linejoin="round"/>')


def pipeline(t, theme, s, x0, y0, w, r, mobile):
    """Infrastructure -> models -> interfaces, with user feedback flowing back."""
    st = ICON_STYLE[theme]
    col = w / 3
    cxs = [x0 + col * (i + 0.5) for i in range(3)]
    icons = [_icon(n, theme) for n in ICON_NAMES]
    # displayed heights, the same in both themes so they share one layout
    body_h = [col * 0.60 * ICON_H[n] for n in ICON_NAMES]
    fs_arc, fs_name, fs_cap = r(12), r(14), r(12)
    parts, css = [], []
    # A shared cool metal finish ties the connectors to the rendered icons.
    parts.append('<defs><linearGradient id="arrow-metal" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{st["top"]}"/>'
                 f'<stop offset=".45" stop-color="{st["arrow"]}"/>'
                 f'<stop offset="1" stop-color="{st["bottom"]}"/>'
                 '</linearGradient></defs>')

    # vertical rhythm: label, arc, icons, names
    yl = y0 + fs_arc
    apex = yl + r(9)
    gap = r(5)  # air between the arc's ends and the icons
    cy = apex + r(20) + max(body_h) / 2
    tops = [cy - h / 2 for h in body_h]

    # feedback arc: leaves the top of interfaces, lands on top of models.
    # Both control points sit straight above the ends, so the curve leaves and
    # arrives vertically and runs straight into the arrowhead.
    ah, aw = r(7), r(4.5)
    sx, sy = cxs[2], tops[2] - gap
    ex, tip = cxs[1], tops[1] - gap
    ey = tip - ah
    ya = (apex - 0.125 * (sy + ey)) / 0.75
    d = f"M{sx:.1f} {sy:.1f} C{sx:.1f} {ya:.1f} {ex:.1f} {ya:.1f} {ex:.1f} {ey:.1f}"
    arc = (
        f'<path d="{d}" fill="none" stroke="{st["edge"]}" stroke-width="{r(3.6):.1f}" '
        f'stroke-linecap="round"/>'
        f'<path d="{d}" fill="none" stroke="url(#arrow-metal)" stroke-width="{r(2.6):.1f}" '
        f'stroke-linecap="round"/>'
        f'<path d="M{ex:.1f} {tip:.1f} L{ex - aw:.1f} {ey:.1f} Q{ex:.1f} {ey + ah * 0.28:.1f} {ex + aw:.1f} {ey:.1f} Z" '
        f'fill="url(#arrow-metal)" stroke="{st["edge"]}" stroke-width="{r(0.6):.1f}" stroke-linejoin="round"/>'
    )
    lab = text(MONO, s["loop"], (sx + ex) / 2, yl, fs_arc, "feedback-label", anchor="middle")[0]
    parts.append(f'<g class="lp">{arc}{lab}</g>')
    css.append(".lp{animation:fade .6s ease 1.3s both}"
               f".feedback-label{{fill:{st['label']}}}")

    # soft glow behind every icon
    parts.append(f'<radialGradient id="hglow"><stop offset="0" stop-color="{t["gr"]}" stop-opacity="{st["glow"]}"/>'
                 f'<stop offset=".55" stop-color="{t["gr"]}" stop-opacity="{st["glow"] * 0.45:.3f}"/>'
                 f'<stop offset="1" stop-color="{t["gr"]}" stop-opacity="0"/></radialGradient>')
    for i, (b64, pw, ph) in enumerate(icons):
        # height fixed per icon, width from the render's own proportions
        ih = body_h[i]
        iw = ih * pw / ph
        glow = (f'<circle cx="{cxs[i]:.1f}" cy="{cy:.1f}" r="{col * 0.44:.1f}" fill="url(#hglow)"/>'
                if st["glow"] else "")
        img = (f'<image x="{cxs[i] - iw / 2:.1f}" y="{cy - ih / 2:.1f}" width="{iw:.1f}" height="{ih:.1f}" '
               f'href="data:image/png;base64,{b64}"/>')
        parts.append(f'<g class="ic{i}">{glow}{img}</g>')
        css.append(f".ic{i}{{animation:rise .6s cubic-bezier(.2,.8,.2,1) {0.5 + 0.2 * i:.1f}s both}}")

    for i in range(2):
        a = _arrow("url(#arrow-metal)", st["edge"], cxs[i] + col * 0.36, cxs[i + 1] - col * 0.36, cy, col * 0.0055)
        parts.append(f'<g class="aw{i}">{a}</g>')
        css.append(f".aw{i}{{animation:fade .4s ease {0.8 + 0.2 * i:.1f}s both}}")

    # names and captions; a caption too wide for its column splits at the dot
    yn = cy + max(body_h) / 2 + fs_name * 1.5
    bottom = yn
    for i, (name, cap) in enumerate(s["stages"]):
        g = [text(SANS, name, cxs[i], yn, fs_name, "fg", anchor="middle")[0]]
        lines = [cap] if MONO.width(cap, fs_cap) <= col * 0.94 else cap.split(" · ")
        yc = yn
        for line in lines:
            yc += fs_cap * 1.5
            g.append(text(MONO, line, cxs[i], yc, fs_cap, "mu", anchor="middle")[0])
        bottom = max(bottom, yc)
        parts.append(f'<g class="ic{i}">{"".join(g)}</g>')
    return parts, css, bottom + fs_cap * 0.4 - y0


def hero(lang, theme, mobile):
    """The hook in a few seconds: one claim on the left, the pipeline that backs it on the right.
    Who I am stays in the profile sidebar; what I do now and next follows as text."""
    t, s = THEMES[theme], STR[lang]
    parts, css = [], [base_css(t), COMMON_KEYS, f".or{{fill:{ORANGE[theme]}}}"]
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    x = r(10) if mobile else r(4)
    full = W - 2 * x
    left_w = full if mobile else r(330)

    y = r(16)
    k_el, _ = text(MONO, s["kicker"], x, y, r(12), "mu", tracking=r(1.0))
    parts.append(f'<g class="kk">{k_el}<rect x="{x:.1f}" y="{y + r(9):.1f}" width="{r(34):.1f}" '
                 f'height="{r(1.5):.1f}" fill="{t["fg"]}"/></g>')
    css.append(".kk{animation:fade .5s ease .05s both}")

    head = s["head"]
    size = min(r(46 if mobile else 44),
               min(left_w / sum(SANS_BD.width(seg, 1, -0.012) for seg, _ in line) for line in head) * 0.98)
    y += r(22)
    g = []
    for line in head:
        y += size * 1.04
        cx = x
        for seg, cls in line:
            el, w_ = text(SANS_BD, seg, cx, y, size, cls, tracking=-size * 0.012)
            g.append(el)
            cx += w_
    parts.append(f'<g class="name">{"".join(g)}</g>')
    css.append(".name{animation:rise .7s cubic-bezier(.2,.8,.2,1) .15s both}")

    sub = r(15.5 if mobile else 16)
    y += sub * 1.9
    sl = []
    for line in wrap(SANS, s["sub"], sub, left_w):
        sl.append(text(SANS, line, x, y, sub, "mu")[0])
        y += sub * 1.42
    parts.append(f'<g class="tag">{"".join(sl)}</g>')
    css.append(".tag{animation:rise .7s cubic-bezier(.2,.8,.2,1) .35s both}")
    left_bottom = y - sub * 1.42 + sub * 0.4

    if mobile:
        pp, pc, ph = pipeline(t, theme, s, x, left_bottom + r(26), full, r, mobile)
        H = left_bottom + r(26) + ph + r(8)
    else:
        dx = x + left_w + r(18)
        dw = W - x - dx
        _, _, ph = pipeline(t, theme, s, dx, 0, dw, r, mobile)
        y0 = max(r(2), (left_bottom - ph) / 2 + r(6))
        pp, pc, ph = pipeline(t, theme, s, dx, y0, dw, r, mobile)
        H = max(left_bottom, y0 + ph) + r(10)
    parts += pp
    css += pc
    return svg(W, int(H), s["hero_title"], s["hero_desc"], "".join(parts), "".join(css))


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


STATUS = {"en": {"now": "NOW", "exploring": "EXPLORING"},
          "pt": {"now": "AGORA", "exploring": "EXPLORANDO"}}


def status_tag(kind, lang, theme):
    """Coloured label that opens the Now / Exploring lines under the hero. Markdown
    text cannot be coloured on GitHub, so the label is an image and the line stays text.
    Both tags of a language share one width, so the text after them lines up."""
    t, k = THEMES[theme], 2
    scale(k)
    fs, h, pad, r_ = 12 * k, 24 * k, 10 * k, 3.5 * k
    col = t["gr"] if kind == "now" else t["ac"]
    lx = pad + r_ * 2 + 7 * k
    w = lx + max(MONO_MD.width(v, fs, 0.6 * k) for v in STATUS[lang].values()) + pad
    label = STATUS[lang][kind]
    frame = (f'<rect x="{k / 2}" y="{k / 2}" width="{w - k:.1f}" height="{h - k}" rx="{(h - k) / 2}" '
             f'fill="{col}" fill-opacity=".13" stroke="{col}" stroke-opacity=".55" stroke-width="{k}"/>')
    cx, cy = pad + r_, h / 2
    if kind == "now":  # a live dot, like a status light
        dot = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_:.1f}" fill="{col}"/>'
               f'<circle class="pl" cx="{cx:.1f}" cy="{cy:.1f}" r="{r_:.1f}" fill="{col}"/>')
        anim = ("@keyframes pulse{0%{r:7;opacity:.55}70%,100%{r:20;opacity:0}}"
                ".pl{animation:pulse 2.4s ease-out .6s infinite}")
    else:  # an open ring: still forming
        dot = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_ - k * 0.6:.1f}" fill="none" '
               f'stroke="{col}" stroke-width="{k * 1.2:.1f}"/>')
        anim = ""
    el, _ = text(MONO_MD, label, lx, h / 2 + fs * 0.36, fs, "fg", tracking=0.6 * k)
    el = el.replace('class="fg"', f'fill="{col}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / k:.0f}" height="{h / k:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{label}"><title>{label}</title>'
            f'<style>{base_css(t)}{anim}</style>{frame}{dot}{el}</svg>')


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
            for kind in STATUS[lang]:
                write(OUT / "status" / f"{kind}-{lang}-{theme}.svg", status_tag(kind, lang, theme))

    print("smallest text as rendered on GitHub (px):")
    for size, name, sample in sorted(report)[:6]:
        print(f"  {size:5.1f}  {name:32} {sample!r}")
    if failures:
        raise SystemExit(f"{len(failures)} assets have text under {MIN_PX}px: {failures[:4]}")


if __name__ == "__main__":
    main()
