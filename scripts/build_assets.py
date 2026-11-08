"""Build every README asset: hero, numbers, walking strip, project cards, toolbox and buttons.

    python scripts/build_assets.py

Outputs go to assets/ in English and Portuguese, light and dark, desktop and
mobile. Data comes from scripts/data (see assets/SOURCES.md).
"""

from functools import partial
from math import pi
from pathlib import Path
from typing import NamedTuple

import cards
import hedgehog
from svgkit import MIN_PX, MONO, MONO_MD, SANS, SANS_BD, THEMES, base_css, canvas, scale, smallest, svg, text, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"


STR = {
    "en": dict(
        # One number per project card below, in the same order, matching the card's own figures.
        stats=[("Research", "37,499", "patients modeled"), ("Dashboard", "55,647", "records visualized"),
               ("Monitor", "96", "automated checks a day")],
        # The Toolbox panel. Every tool in a project's stack line in the README must be here
        # (test_assets checks it), so the two never drift apart.
        toolbox_title="Toolbox",
        toolbox=[("Data & research", ["Python", "pandas", "NumPy", "lifelines", "Jupyter"]),
                 ("Apps & visualization", ["Streamlit", "Plotly", "GeoPandas", "Folium"]),
                 ("Automation", ["GitHub Actions", "Cloudflare Workers", "Discord webhooks", "pytest"]),
                 ("Coursework", ["Flutter", "Dart"])],
        cta_main="Get in touch",
        cta_alt="See projects",
        contact_mail="Email app",
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
        stats=[("Pesquisa", "37.499", "pacientes modelados"), ("Dashboard", "55.647", "registros visualizados"),
               ("Monitor", "96", "verificações automáticas por dia")],
        toolbox_title="Ferramentas",
        toolbox=[("Dados e pesquisa", ["Python", "pandas", "NumPy", "lifelines", "Jupyter"]),
                 ("Aplicações e visualização", ["Streamlit", "Plotly", "GeoPandas", "Folium"]),
                 ("Automação", ["GitHub Actions", "Cloudflare Workers", "webhooks do Discord", "pytest"]),
                 ("Disciplina", ["Flutter", "Dart"])],
        cta_main="Fale comigo",
        cta_alt="Ver projetos",
        contact_mail="App de e-mail",
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
    # The small arrowhead needs a bright fill against the dark background.
    tip_fill = st["top"] if theme == "dark" else "url(#arrow-metal)"
    tip_edge = st["arrow"] if theme == "dark" else st["edge"]
    arc = (
        f'<path d="{d}" fill="none" stroke="{st["edge"]}" stroke-width="{r(3.6):.1f}" '
        f'stroke-linecap="round"/>'
        f'<path d="{d}" fill="none" stroke="url(#arrow-metal)" stroke-width="{r(2.6):.1f}" '
        f'stroke-linecap="round"/>'
        f'<path d="M{ex:.1f} {tip:.1f} L{ex - aw:.1f} {ey:.1f} Q{ex:.1f} {ey + ah * 0.28:.1f} {ex + aw:.1f} {ey:.1f} Z" '
        f'fill="{tip_fill}" stroke="{tip_edge}" stroke-width="{r(0.6):.1f}" stroke-linejoin="round"/>'
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
    tag = f'<g class="tag">{"".join(sl)}</g>'
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
        # Align the paragraph's last baseline with the diagram captions.
        caption_baseline = y0 + ph - r(12) * 0.4
        text_baseline = y - sub * 1.42
        tag = f'<g transform="translate(0 {caption_baseline - text_baseline:.1f})">{tag}</g>'
        H = max(caption_baseline + sub * 0.4, y0 + ph) + r(10)
    parts.append(tag)
    parts += pp
    css += pc
    # README spacing lives in the SVG because GitHub strips custom margins.
    # Leave air below the language buttons and above the padded status rows.
    top_pad = r(8 if mobile else 16)
    body = f'<g transform="translate(0 {top_pad:.1f})">{"".join(parts)}</g>'
    return svg(W, int(H + top_pad + r(14)), s["hero_title"], s["hero_desc"], body, "".join(css))


def numbers(lang, theme, mobile):
    """The three project numbers, static, opening the Selected work section.

    A panel like the cards', one column per card in the cards' order, each named
    after its project so the number reads as a preview of that card."""
    t, s = THEMES[theme], STR[lang]
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    pad, gap = (r(12), r(10)) if mobile else (r(22), r(20))
    eyebrow, num, lab = r(12), r(22), r(12.5)
    colw = (W - 2 * pad) / 3
    sw = r(1)
    top = pad + eyebrow
    y = top + eyebrow * 0.9 + num * 1.15
    parts, rows = [], 1
    for i, (project, v, label) in enumerate(s["stats"]):
        x = pad + i * colw + (gap if i else 0)
        inner = colw - (gap if i else 0) - gap
        parts.append(text(MONO_MD, project.upper(), x, top, eyebrow, "ac", tracking=r(0.6))[0])
        parts.append(text(MONO_MD, v, x, y, num, "fg")[0])
        lines = wrap(SANS, label, lab, inner)
        rows = max(rows, len(lines))
        for j, line in enumerate(lines):
            parts.append(text(SANS, line, x, y + lab * (1.6 + 1.3 * j), lab, "mu")[0])
    box_h = y + lab * (1.6 + 1.3 * (rows - 1)) + lab * 0.4 + pad
    for i in (1, 2):
        dx = pad + i * colw
        parts.append(f'<path class="ln" stroke-width="{sw:.2f}" d="M{dx:.1f} {pad:.1f} V{box_h - pad:.1f}"/>')
    frame = (f'<rect x="{sw * .6:.1f}" y="{sw * .6:.1f}" width="{W - sw * 1.2:.1f}" height="{box_h - sw * 1.2:.1f}" '
             f'rx="{r(12):.1f}" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="{sw:.2f}"/>')
    # Air below the panel, before the first card: GitHub strips margins.
    H = int(box_h + r(6))
    alt = ", ".join(f"{v} {label}" for _, v, label in s["stats"])
    return svg(W, H, alt, alt, frame + "".join(parts), base_css(t))


def toolbox(lang, theme, mobile):
    """The tools, grouped by area: a panel like the numbers strip, each group an
    accent label over a row of chips. Two groups per row on desktop, one on mobile."""
    t, s = THEMES[theme], STR[lang]
    W = 720 if mobile else 1200
    r = canvas(W, mobile)
    pad, gap = (r(14), r(14)) if mobile else (r(22), r(28))
    eyebrow, fs = r(12), r(13)
    chip_h, chip_px, chip_gap = fs * 2.0, r(10), r(6)
    sw = r(1)
    per_row = 1 if mobile else 2
    colw = (W - 2 * pad - gap * (per_row - 1)) / per_row
    groups = s["toolbox"]
    parts, y = [], pad
    for row in range(0, len(groups), per_row):
        bottom = y
        for k, (area, tools) in enumerate(groups[row:row + per_row]):
            x0 = pad + k * (colw + gap)
            parts.append(text(MONO_MD, area.upper(), x0, y + eyebrow, eyebrow, "ac", tracking=r(0.6))[0])
            cx, cy = x0, y + eyebrow + r(10)
            for tool in tools:
                w = SANS.width(tool, fs) + 2 * chip_px
                if cx > x0 and cx + w > x0 + colw:
                    cx, cy = x0, cy + chip_h + chip_gap
                parts.append(
                    f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{w:.1f}" height="{chip_h:.1f}" rx="{chip_h / 2:.1f}" '
                    f'fill="{t["panel2"]}" stroke="{t["line"]}" stroke-width="{sw:.2f}"/>'
                    + text(SANS, tool, cx + w / 2, cy + chip_h / 2 + fs * 0.35, fs, "fg", anchor="middle")[0]
                )
                cx += w + chip_gap
            bottom = max(bottom, cy + chip_h)
        y = bottom + (r(18) if mobile else r(22))
    box_h = y - (r(18) if mobile else r(22)) + pad
    frame = (f'<rect x="{sw * .6:.1f}" y="{sw * .6:.1f}" width="{W - sw * 1.2:.1f}" height="{box_h - sw * 1.2:.1f}" '
             f'rx="{r(12):.1f}" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="{sw:.2f}"/>')
    desc = ". ".join(f"{area}: {', '.join(tools)}" for area, tools in groups) + "."
    return svg(W, int(box_h + r(6)), s["toolbox_title"], desc, frame + "".join(parts), base_css(t))


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, k):
    a, b = _hex(a), _hex(b)
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(a, b))


# The hedgehog's routine is a script: a list of trips, each a leg that crosses
# the strip (or stops part way) followed by what happens where it stops.
# _motion() only plays it back, so a new behaviour is a new entry here, not new
# code. Each phase name is drawn by one entry of POSES.


class Leg(NamedTuple):
    """Cross to the edge: [(phase, share of the leg's time, speed relative to walking)]."""
    phases: tuple

    @property
    def rolls(self):
        return any(phase.startswith("ball") for phase, _, _ in self.phases)


class Hold(NamedTuple):
    """Stay put in one pose for a few seconds."""
    phase: str
    seconds: float


class Recoil(NamedTuple):
    """Move back, against the direction of travel, while holding one pose."""
    phase: str
    seconds: float
    distance: float


class Look(NamedTuple):
    """Turn to look back without moving, then face the way of travel again."""
    seconds: float
    phase: str = "rest"


class Edge(NamedTuple):
    """What happens where the leg stops. touch="ball" stops where the ball
    itself, not the sprite's box, meets the edge."""
    beats: tuple
    touch: str = "body"

    @property
    def bumps(self):
        return any(isinstance(beat, Recoil) for beat in self.beats)


class Trip(NamedTuple):
    direction: int  # +1 right, -1 left
    leg: Leg
    edge: Edge
    to: float = None  # stop part way, as a share of the strip from the left; None goes to the edge


WALK = Leg((("walk", 1.0, 1.0),))
# Curls up a third of the way in and reaches the edge at full speed.
ROLL = Leg((("walk", 0.30, 1.0), ("crouch", 0.05, 0.3),
            ("curl", 0.05, 0.3), ("ball", 0.60, 3.0)))
# Brakes to walking pace first, so the ball comes to rest without hitting anything.
ROLL_STOP = Leg((("walk", 0.30, 1.0), ("crouch", 0.05, 0.3), ("curl", 0.05, 0.3),
                 ("ball", 0.42, 3.0), ("ball_slow", 0.18, 1.0)))

UNCURL = (Hold("ball_rest", .25), Hold("curl", .25), Hold("crouch", .25))
TURN = (Hold("rest", .35), Hold("blink", .15), Hold("rest", .25))
RECOVER = (Hold("rest", .55), Hold("shake", .75), Hold("rest", .15),
           Hold("blink", .15), Hold("rest", .20))

BALL_BUMP = Edge((Hold("ball_impact", .20), Recoil("ball_recoil", .70, 90),
                  *UNCURL, *RECOVER), touch="ball")
WALK_BUMP = Edge((Hold("walk_impact", .25), Recoil("walk_recoil", .50, 24), *RECOVER))
# Out of breath after a roll: a longer rest and two blinks before turning.
TIRED = (Hold("rest", .6), Hold("blink", .15), Hold("rest", .25),
         Hold("blink", .15), Hold("rest", .4))

BALL_TURN = Edge((*UNCURL, *TIRED))
WALK_TURN = Edge(TURN)
# Halfway across: blink, glance back over the shoulder, blink, carry on.
LOOK_BACK = Edge((Hold("rest", .4), Hold("blink", .15), Look(.9),
                  Hold("rest", .3), Hold("blink", .15), Hold("rest", .3)))

# Every edge sees one bump and one quiet turn, and both gaits do each once.
SCRIPT = (
    Trip(+1, ROLL, BALL_BUMP),
    Trip(-1, WALK, WALK_BUMP),
    Trip(+1, WALK, LOOK_BACK, to=.55),
    Trip(+1, WALK, WALK_TURN),
    Trip(-1, ROLL_STOP, BALL_TURN),
)
# The trips that reach an edge, as (direction, rolls, bumps).
TRIPS = [(trip.direction, trip.leg.rolls, trip.edge.bumps) for trip in SCRIPT if trip.to is None]


class Pose(NamedTuple):
    """How strip() draws the script's phases.

    cls is the CSS class of the pose's group, shown only during its phases.
    art names a drawing that strip() builds. ground says what touches the
    floor and lights cells: "gait" (the walking poses in turn), "stand" (the
    first walking pose), "crouch", "curl", "ball" (one centred tangent while
    the square sprite rotates) or None (airborne). shown is the pose visible
    without animation, under reduced motion.
    """
    cls: str
    phases: tuple
    art: str
    ground: object
    shown: bool = False


# Order matters: it is the stacking and CSS order of the generated SVG.
POSES = (
    Pose("gw", ("walk",), "walking", "gait", shown=True),
    Pose("gc", ("crouch",), "crouch", "crouch"),
    Pose("gu", ("curl",), "curl", "curl"),
    Pose("gb", ("ball",), "ball_spin", "ball"),
    Pose("gbs", ("ball_slow",), "ball_slow", "ball"),
    Pose("idle", ("rest",), "stand", "stand"),
    Pose("closed", ("blink", "walk_recoil"), "closed", "stand"),
    Pose("whit", ("walk_impact",), "walk_hit", "stand"),
    Pose("bhit", ("ball_impact",), "ball_hit", "ball"),
    Pose("bback", ("ball_recoil",), "ball_hop", None),
    Pose("bstop", ("ball_rest",), "ball", "ball"),
    Pose("shake", ("shake",), "shake", "stand"),
)


def _pose(phase):
    """The pose that draws a phase; every phase in the script needs one."""
    for pose in POSES:
        if phase in pose.phases:
            return pose
    raise ValueError(f"phase {phase!r} has no pose in POSES")


def _edge_x(trip, travel, ball_margin):
    """Where the trip's leg stops."""
    if trip.to is not None:
        return travel * trip.to
    edge = travel if trip.direction > 0 else 0.0
    if trip.edge.touch == "ball":
        edge += trip.direction * ball_margin
    return edge


def _trip_end(trip, travel, ball_margin):
    """Where the trip's edge beats leave the hedgehog."""
    x = _edge_x(trip, travel, ball_margin)
    for beat in trip.edge.beats:
        if isinstance(beat, Recoil):
            x = x - trip.direction * beat.distance
    return x


def _motion(travel, walk_time, ball_margin=0, script=SCRIPT):
    """Play the script back as keyframes for one cycle at a constant walking speed.

    walk_time is how long a plain walking trip takes. Returns
    (period, stops [(t, x)], spans {phase: [(t0, t1)]}, trips [(t0, direction)]).
    """
    speed = travel / walk_time
    # Start where the last trip leaves the hedgehog, so the loop never teleports.
    x = _trip_end(script[-1], travel, ball_margin)
    t, stops, spans, starts = 0.0, [(0.0, x)], {"walk": [], "crouch": [], "curl": [], "ball": []}, []

    def advance(phase, duration, target):
        nonlocal t, x
        spans.setdefault(phase, []).append((t, t + duration))
        t += duration
        x = target
        stops.append((t, x))

    for trip in script:
        direction = trip.direction
        starts.append((t, direction))
        end = _edge_x(trip, travel, ball_margin)
        plan = trip.leg.phases
        dur = abs(end - x) / (speed * sum(f * v for _, f, v in plan))
        for phase, f, v in plan:
            dt = f * dur
            advance(phase, dt, x + direction * speed * v * dt)
        # Land exactly on the edge, whatever rounding the leg accumulated.
        x = end
        stops[-1] = (t, x)
        for beat in trip.edge.beats:
            if isinstance(beat, Recoil):
                advance(beat.phase, beat.seconds, x - direction * beat.distance)
            elif isinstance(beat, Look):
                starts.append((t, -direction))
                advance(beat.phase, beat.seconds, x)
                starts.append((t, direction))
            else:
                advance(beat.phase, beat.seconds, x)
    return t, stops, spans, starts


def _ground_runs(frame):
    """Horizontal supports in the bottom row (including the pixel outline)."""
    runs = []
    for x, ch in enumerate(frame[-1]):
        if ch != ".":
            if runs and runs[-1][0] + runs[-1][1] == x:
                runs[-1] = (runs[-1][0], runs[-1][1] + 1)
            else:
                runs.append((x, 1))
    return runs


def _contact_tracks(frames, roll, step, px, stops, spans, trips):
    """Time and horizontal bounds of each planted foot, mirrored on return."""
    tracks = []
    width = len(frames[0][0]) * px
    footprints = [_ground_runs(frame) for frame in frames]
    still = {"stand": roll["walk"][0], "crouch": roll["curl"][0], "curl": roll["curl"][1],
             "ball": roll["ball"]}
    for (a, xa), (b, xb) in zip(stops, stops[1:]):
        mid = (a + b) / 2
        phase = next(p for p, intervals in spans.items() if any(lo <= mid < hi for lo, hi in intervals))
        ground = _pose(phase).ground
        if ground is None:
            continue  # airborne: cells light again on landing, not during the hop
        direction = next(d for t, d in reversed(trips) if t <= mid)
        ticks = [a, b]
        if ground == "gait":
            ticks += [i * step for i in range(int(a / step) + 1, int(b / step) + 1) if i * step < b]
        ticks.sort()
        for start, end in zip(ticks, ticks[1:]):
            if ground == "gait":
                index = roll["walk"][int(((start + end) / 2) / step) % len(roll["walk"])]
            else:
                index = still[ground]
            supports = footprints[index]
            if ground == "ball":
                # The tangent remains centered as the square sprite rotates.
                supports = [(len(frames[index][0]) / 2 - .5, 1)]
            for x, size in supports:
                offset = x * px if direction > 0 else width - (x + size) * px
                left = lambda tt: xa + (xb - xa) * (tt - a) / (b - a) + offset
                tracks.append((start, end, left(start), left(end), size * px))
    return tracks


def _cell_contacts(cx, cell, tracks):
    """Intervals when a planted support overlaps the cell, in either direction."""
    contacts = []
    for a, b, xa, xb, width in tracks:
        low, high = cx - cell / 2 - width, cx + cell / 2
        if xa == xb:
            if low <= xa <= high:
                contacts.append((a, b))
            continue
        enter = a + (low - xa) / (xb - xa) * (b - a)
        leave = a + (high - xa) / (xb - xa) * (b - a)
        start, end = max(a, min(enter, leave)), min(b, max(enter, leave))
        if start < end:
            contacts.append((start, end))
    merged = []
    for start, end in sorted(contacts):
        if merged and start <= merged[-1][1] + 1e-8:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def strip(theme, mobile):
    """A thin band where the hedgehog crosses a row of contribution-style cells
    that light up under it. The edges are invisible: at each one it either
    bumps and recovers or simply turns round."""
    t = THEMES[theme]
    r_px = canvas(720 if mobile else 1200, mobile)
    pal, frames, gw, gh = hedgehog.palette(theme), hedgehog.FRAMES, hedgehog.W, hedgehog.H
    roll, step = hedgehog.ROLL, hedgehog.STEP
    W, walk_time = (720, 14.0) if mobile else (1200, 20.0)
    px, cell, pitch = 3, 10, 14
    sw, sh = gw * px, gh * px
    top = 8
    cells_y = top + sh
    H = cells_y + cell + 4
    travel = W - sw
    fade = 2.6
    ball = frames[roll["ball"]]
    ball_margin = min(x for row in ball for x, ch in enumerate(row) if ch != ".") * px
    period, stops, spans, trips = _motion(travel, walk_time, ball_margin)
    for phase in spans:
        _pose(phase)  # fail early on a scripted phase nothing draws
    # Keep the pose clock aligned with the repeating contact/position clock.
    gait = step * len(roll["walk"])
    step = period / (round(period / gait) * len(roll["walk"]))
    tracks = _contact_tracks(frames, roll, step, px, stops, spans, trips)

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
        contacts = _cell_contacts(cx, cell, tracks)
        base, hot = t["cells"][lv], t["cells"][4]

        def col(tt):
            best = 0.0
            for start, end in contacts:
                if start <= tt <= end:
                    return hot
                dt = (tt - end) % period
                if dt < fade:
                    best = max(best, 1 - dt / fade)
            return _mix(base, hot, best)

        marks = {0.0, period}
        for start, end in contacts:
            for mark in (start - .01, start, end, end + fade):
                marks.add(mark % period)
        steps = "".join(
            f"{m / period * 100:.6f}%{{fill:{col(m if m < period else 0)}}}" for m in sorted(marks)
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
        f".flip{{transform-origin:{sw / 2}px {sh / 2}px;"
        f"animation:flip {period}s steps(1) infinite}}"
        "@keyframes flip{"
        + "".join(f"{t0 / period * 100:.3f}%{{transform:scaleX({d})}}" for t0, d in trips)
        + f"100%{{transform:scaleX({trips[-1][1]})}}}}"
    )
    rf = lambda k: hedgehog.frame_rects(pal, frames[k], px)
    walk_frames = roll["walk"]
    walking = []
    for i, frame in enumerate(walk_frames):
        keyframes = "".join(f"{j / len(walk_frames) * 100:g}%{{opacity:{int(i == j)}}}"
                            for j in range(len(walk_frames)))
        css.append(f".wf{i}{{opacity:{int(i == 0)};animation:wf{i} {step * len(walk_frames):.12g}s steps(1) infinite}}"
                   f"@keyframes wf{i}{{{keyframes}100%{{opacity:{int(i == 0)}}}}}")
        walking.append(f'<g class="wf{i}">{rf(frame)}</g>')
    walking = "".join(walking)
    # Each pose group is visible only during its phases of the cycle.
    groups = spans

    def vis(cls, intervals, base_on):
        merged = []
        for a_, b_ in sorted(intervals):
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

    for pose in POSES:
        css.append(vis(pose.cls, [span for phase in pose.phases for span in groups.get(phase, [])],
                       pose.shown))
    diameter = sum(any(ch != "." for ch in row) for row in ball) * px
    spin_time = pi * diameter / (travel / walk_time * 3)
    css.append(f".spin{{transform-box:fill-box;transform-origin:center;animation:spin {spin_time:g}s steps(4) infinite}}"
               "@keyframes spin{to{transform:rotate(360deg)}}")
    css.append(f".backspin{{transform-box:fill-box;transform-origin:center;animation:spin {spin_time:g}s steps(4) infinite reverse}}")
    # While braking the ball turns at walking pace, a third of its rolling spin.
    css.append(f".slowspin{{transform-box:fill-box;transform-origin:center;animation:spin {spin_time * 3:g}s steps(4) infinite}}")

    def reaction(cls, intervals, transforms, origin=""):
        marks = {0.0: transforms[0][1], period: transforms[0][1]}
        for a_, b_ in intervals:
            for share, transform in transforms:
                marks[a_ + (b_ - a_) * share] = transform
        keys = "".join(f"{tt / period * 100:.6f}%{{transform:{value}}}" for tt, value in sorted(marks.items()))
        css.append(f".{cls}{{{origin}animation:{cls} {period}s linear infinite}}@keyframes {cls}{{{keys}}}")

    reaction("walkhit", groups["walk_impact"],
             [(0, "scaleX(1)"), (.5, "scaleX(.93)"), (1, "scaleX(1)")],
             f"transform-origin:{sw}px {sh}px;")
    ball_right = sw - ball_margin
    reaction("ballhit", groups["ball_impact"],
             [(0, "scale(1,1)"), (.5, "scale(.8,1.1)"), (1, "scale(1,1)")],
             f"transform-origin:{ball_right}px {sh}px;")
    reaction("hop", groups["ball_recoil"],
             [(0, "translateY(0px)"), (.25, "translateY(-12px)"),
              (.5, "translateY(-17px)"), (.75, "translateY(-12px)"), (1, "translateY(0px)")])
    recovery = hedgehog.recovery()
    closed = hedgehog.frame_rects(pal, recovery["blink"], px)
    heads = []
    for cls, pose, slots in (("sl", "left", (0,)), ("sm", "blink", (1, 3)), ("sr", "right", (2,))):
        keys = "".join(f"{j * 25}%{{opacity:{int(j in slots)}}}" for j in range(4))
        keys += f"100%{{opacity:{int(0 in slots)}}}"
        css.append(f".{cls}{{opacity:0;animation:{cls} .25s steps(1) infinite}}@keyframes {cls}{{{keys}}}")
        offset = -px if pose != "blink" else 0
        heads.append(f'<g class="{cls}">{hedgehog.frame_rects(pal, recovery[pose], px, offset)}</g>')
    c0, c1 = roll["curl"]
    rolled = rf(roll["ball"])
    # The drawings POSES refers to by name.
    art = {
        "walking": walking,
        "crouch": rf(c0),
        "curl": rf(c1),
        "ball_spin": f'<g class="spin">{rolled}</g>',
        "ball_slow": f'<g class="slowspin">{rolled}</g>',
        "stand": rf(walk_frames[0]),
        "closed": closed,
        "walk_hit": f'<g class="walkhit">{closed}</g>',
        "ball_hit": f'<g class="ballhit">{rolled}</g>',
        "ball_hop": f'<g class="hop"><g class="backspin">{rolled}</g></g>',
        "ball": rolled,
        "shake": "".join(heads),
    }
    body = "".join(f'<g class="{pose.cls}">{art[pose.art]}</g>' for pose in POSES)
    # A larger pause separates contact actions from the project divider.
    top_pad = r_px(12)
    content = "".join(rects) + f'<g class="walk" shape-rendering="crispEdges"><g class="flip">{body}</g></g>'
    content = f'<g transform="translate(0 {top_pad:.1f})">{content}</g>'
    return svg(
        W, int(H + top_pad), "Walking mascot",
        "A pixel-art hedgehog alternates walking and rolling; sometimes it bumps into the edge, recoils and shakes its head, other times it just turns around, and once it stops halfway to glance back.",
        content, "".join(css),
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

STATUS_COPY = {
    "en": {
        "now": "Building ML and deep learning models on ECG data, with medical validation in the loop.",
        "exploring": "LLM internals, computer vision and compute clusters.",
    },
    "pt": {
        "now": "Construindo modelos de ML e deep learning com dados de ECG, com validação médica no processo.",
        "exploring": "Funcionamento interno de LLMs, visão computacional e clusters de computação.",
    },
}
STATUS_COLORS = {
    "dark": dict(now="#77cdbb", exploring="#e5b57a", frame="#8a9baa", divider="#303d49"),
    "light": dict(now="#197462", exploring="#89571b", frame="#617586", divider="#d1d9e0"),
}


def _status_instrument(kind, colors):
    """A processor and a compass share an open instrument frame."""
    accent = colors[kind]
    body = (f'<path d="M3 8V3H8M16 3H21V8M21 16V21H16M8 21H3V16" '
            f'fill="none" stroke="{colors["frame"]}" stroke-width="1.4" stroke-linecap="round"/>')
    if kind == "now":
        body += (f'<rect x="8" y="8" width="8" height="8" rx="1.5" fill="none" '
                 f'stroke="{accent}" stroke-width="1.5"/>'
                 f'<path d="M10 5V8M14 5V8M10 16V19M14 16V19M5 10H8M5 14H8M16 10H19M16 14H19" '
                 f'stroke="{accent}" stroke-width="1.2" stroke-linecap="round"/>'
                 f'<circle cx="12" cy="12" r="1.5" fill="{accent}"/>')
    else:
        body += (f'<circle cx="12" cy="12" r="5.3" fill="none" stroke="{accent}" stroke-width="1.3"/>'
                 f'<path d="M9 15L10.5 10.5L15 9L13.5 13.5Z" fill="{accent}"/>')
    return body


def status_notes(lang, theme, mobile):
    """Open laboratory notes: side by side on desktop, stacked on phones.

    Keep the approved desktop geometry in rendered pixels. Shared frames and
    neutral copy connect the two markers; only the instruments and labels differ.
    Padding is part of the SVG because GitHub strips custom README margins.
    """
    t, colors = THEMES[theme], STATUS_COLORS[theme]
    width = 340 if mobile else 795
    scale(1)
    col = width if mobile else (width - 48) / 2
    parts, bottoms = [], []
    top = 10
    for i, kind in enumerate(STATUS[lang]):
        x = 0 if mobile else i * (col + 48)
        y = top if mobile or i == 0 else 10
        parts.append(f'<g transform="translate({x} {y + 4})">{_status_instrument(kind, colors)}</g>')
        parts.append(text(MONO_MD, STATUS[lang][kind], x + 35, y + 21, 12, "",
                          tracking=0.7, extra=f' fill="{colors[kind]}"')[0])
        lines = wrap(SANS, STATUS_COPY[lang][kind], 15, col - 35)
        for j, line in enumerate(lines):
            parts.append(text(SANS, line, x + 35, y + 52 + j * 23, 15, "fg")[0])
        bottom = y + 52 + (len(lines) - 1) * 23 + 10
        bottoms.append(bottom)
        if mobile and i == 0:
            parts.append(f'<path d="M35 {bottom + 16}H{width}" stroke="{colors["divider"]}"/>')
            top = bottom + 32
    if not mobile:
        parts.insert(0, f'<path d="M{col + 24} 16V{max(bottoms) - 8}" stroke="{colors["divider"]}"/>')
    title = "Now and Exploring" if lang == "en" else "Agora e Explorando"
    desc = " ".join(f"{STATUS[lang][kind]}: {STATUS_COPY[lang][kind]}" for kind in STATUS[lang])
    return svg(width, max(bottoms) + 8, title, desc, "".join(parts), base_css(t))


CTA_GREEN = {"dark": "#238636", "light": "#1f883d"}


def _contact_icon(name):
    """[(path, fill)] in a 24-unit box. fill None means the text colour."""
    import re
    if name == "outlook":
        # Microsoft's four squares, drawn here: Outlook and LinkedIn have no logo in Simple Icons.
        return [(f"M{x} {y}h10.5v10.5H{x}z", c) for x, y, c in
                ((1, 1, "#F25022"), (12.5, 1, "#7FBA00"), (1, 12.5, "#00A4EF"), (12.5, 12.5, "#FFB900"))]
    src = (Path(__file__).parent / "icons" / "contact" / f"{name}.svg").read_text(encoding="utf-8")
    d = re.search(r' d="([^"]+)"', src)[1]
    if 'viewBox="0 0 16 16"' in src:  # Bootstrap Icons draw in 16 units
        d = f'<g transform="scale(1.5)"><path d="{d}"/></g>'
    return [(d, CONTACT_COLOURS.get(name))]


# Gmail from Simple Icons 16.36.0 (CC0); LinkedIn and envelope from Bootstrap Icons 1.13.2 (MIT).
# Licences in scripts/icons/contact/. Brand colours: Gmail and LinkedIn; the envelope uses the text colour.
CONTACT_COLOURS = {"gmail": "#EA4335", "linkedin": "#0A66C2"}


def cta_pill(label, primary, theme, icon=None):
    """Call-to-action button: solid green for the main action, outline for the second.
    icon names a logo drawn left of the label (see _contact_icon)."""
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
    if icon:
        size = 16 * k
        g = []
        for d, fill in _contact_icon(icon):
            fill = fill or t["fg"]
            g.append(d.replace("<path ", f'<path fill="{fill}" ') if d.startswith("<g")
                     else f'<path fill="{fill}" d="{d}"/>')
        dot = (f'<g transform="translate({pad - 2 * k:.1f} {(h - size) / 2:.1f}) scale({size / 24:.4f})">'
               f'{"".join(g)}</g>')
        lx = pad - 2 * k + size + 7 * k
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


CONTACTS = {"gmail": "Gmail", "outlook": "Outlook", "linkedin": "LinkedIn"}


def lang_globe(theme):
    t, k = THEMES[theme], 2
    scale(k)  # no text, but start a fresh smallest-text record
    s, r = 30 * k, 7.5 * k
    c = s / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="30" viewBox="{c - 11 * k} 0 {22 * k} {s}" '
            f'role="img" aria-label="Language"><title>Language</title>'
            f'<g fill="none" stroke="{t["mu"]}" stroke-width="{1.4 * k}">'
            f'<circle cx="{c}" cy="{c}" r="{r}"/><ellipse cx="{c}" cy="{c}" rx="{r * 0.45}" ry="{r}"/>'
            f'<path d="M{c - r} {c} H{c + r}"/></g></svg>')


def outputs():
    """Every generated asset as (path, build), in build order. build() returns the SVG."""
    for theme in THEMES:
        for mobile in (False, True):
            yield OUT / "strip" / f"walk-{theme}{'-mobile' if mobile else ''}.svg", partial(strip, theme, mobile)
    for lang in STR:
        for theme in THEMES:
            for mobile in (False, True):
                sfx = f"{lang}-{theme}{'-mobile' if mobile else ''}.svg"
                for kind, build in cards.BUILDERS.items():
                    yield OUT / "work" / f"{kind}-{sfx}", partial(build, lang, theme, mobile)
                yield OUT / "hero" / f"hero-{sfx}", partial(hero, lang, theme, mobile)
                yield OUT / "work" / f"numbers-{sfx}", partial(numbers, lang, theme, mobile)
                yield OUT / "work" / f"toolbox-{sfx}", partial(toolbox, lang, theme, mobile)

    for theme in THEMES:
        yield OUT / "lang" / f"globe-{theme}.svg", partial(lang_globe, theme)
        for name, label in CONTACTS.items():
            yield OUT / "contact" / f"{name}-{theme}.svg", partial(cta_pill, label, False, theme, name)
        for lang in LANGS:
            for active in (True, False):
                yield (OUT / "lang" / f"{lang}-{'active' if active else 'idle'}-{theme}.svg",
                       partial(lang_pill, lang, active, theme))

    for lang in STR:
        for theme in THEMES:
            yield OUT / "cta" / f"main-{lang}-{theme}.svg", partial(cta_pill, STR[lang]["cta_main"], True, theme)
            yield OUT / "cta" / f"alt-{lang}-{theme}.svg", partial(cta_pill, STR[lang]["cta_alt"], False, theme)
            # Contact buttons in Let's talk; brand names read the same in both languages.
            yield OUT / "contact" / f"mail-{lang}-{theme}.svg", partial(cta_pill, STR[lang]["contact_mail"], False, theme, "envelope")
            for mobile in (False, True):
                suffix = "-mobile" if mobile else ""
                yield OUT / "status" / f"notes-{lang}-{theme}{suffix}.svg", partial(status_notes, lang, theme, mobile)


def main():
    report, failures = [], []
    for path, build in outputs():
        content = build()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        size, sample = smallest()
        if size is not None:
            report.append((size, path.name, sample))
            if size < MIN_PX - 0.01:
                failures.append(path.name)

    print("smallest text as rendered on GitHub (px):")
    for size, name, sample in sorted(report)[:6]:
        print(f"  {size:5.1f}  {name:32} {sample!r}")
    if failures:
        raise SystemExit(f"{len(failures)} assets have text under {MIN_PX}px: {failures[:4]}")


if __name__ == "__main__":
    main()
