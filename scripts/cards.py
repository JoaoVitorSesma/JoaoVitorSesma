"""Project cards: research (forest plot), dashboard (cases per year) and monitor (terminal).

Every size is written in rendered CSS px through r(), so text keeps the same
on-screen size whatever the SVG canvas width is (see svgkit.DISPLAY).
"""

import json
import math
from pathlib import Path

from svgkit import MONO, MONO_MD, SERIF, SERIF_IT, THEMES, base_css, canvas, svg, text

DATA = Path(__file__).parent / "data"
HR = json.loads((DATA / "cox_hazard_ratios.json").read_text())
YEARS = json.loads((DATA / "dashboard_cases_by_year.json").read_text())

P = 16.0  # loop period for card animations, seconds

KEYS = (
    "@keyframes gx{0%{transform:scaleX(0)}9%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
    "@keyframes gy{0%{transform:scaleY(0)}8%,92%{transform:scaleY(1)}100%{transform:scaleY(0)}}"
    "@keyframes pop{0%{opacity:0}9%,92%{opacity:1}100%{opacity:0}}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
)

# Rendered sizes (CSS px) per layout.
SIZES = {
    False: dict(pad=32, eyebrow=12.5, title=34, body=14, num=22, label=12.5, small=12.5, cap=17, term=13.5),
    True: dict(pad=18, eyebrow=12.5, title=30, body=13, num=22, label=12.5, small=12, cap=16, term=12),
}

C = {
    "en": dict(
        r_eyebrow="01 — undergraduate research · FOSP",
        r_title=["Who survives colorectal", "cancer — and why?"],
        r_title_m=["Who survives", "colorectal cancer", "— and why?"],
        r_body=["Cox proportional hazards model on", "São Paulo's cancer registry: data",
                "cleaning, encoding, variable", "selection and validation."],
        r_stats=[("0.747", "C-index"), ("37,499", "patients"), ("22,078", "deaths observed"), ("2000–23", "follow-up")],
        r_fig=" Adjusted hazard ratios, 95% CI",
        r_lower="lower risk",
        r_higher="higher risk",
        d_eyebrow="02 — app · Streamlit",
        d_title=["Cervical cancer in", "São Paulo, year by year"],
        d_title_m=["Cervical cancer", "in São Paulo,", "year by year"],
        d_window="DFOSP.py — streamlit run",
        d_filters="filters",
        d_age="age",
        d_stage="stage",
        d_outcome="outcome",
        d_alive="alive",
        d_dead="deceased",
        d_chart="diagnoses per year",
        d_2020="2020 · −20%",
        d_fig=[" 55,647 public FOSP records per diagnosis year · 2023 still incomplete"],
        d_fig_m=[" 55,647 public FOSP records", "per diagnosis year · 2023 incomplete"],
        m_eyebrow="03 — automation · every 15 min",
        m_title=["A watchtower for", "Codex usage resets"],
        m_title_m=["A watchtower", "for Codex", "usage resets"],
        m_body=["Polls public sources, classifies", "reset announcements with",
                "deterministic rules and alerts", "Discord only when it matters."],
        m_facts=[("R$ 0", "monthly cost"), ("0", "LLM calls"), ("4", "sources"), ("2", "schedulers")],
        m_likely="likely",
        m_confirmed="confirmed",
        m_note=["illustrative run, based on the project README"],
        m_note_m=["illustrative run, based on", "the project README"],
    ),
    "pt": dict(
        r_eyebrow="01 — iniciação científica · FOSP",
        r_title=["Quem sobrevive ao câncer", "colorretal — e por quê?"],
        r_title_m=["Quem sobrevive", "ao câncer colorretal", "— e por quê?"],
        r_body=["Modelo de riscos proporcionais de", "Cox no registro de câncer de SP:",
                "limpeza, codificação, seleção de", "variáveis e validação."],
        r_stats=[("0,747", "C-index"), ("37.499", "pacientes"), ("22.078", "óbitos observados"), ("2000–23", "seguimento")],
        r_fig=" Hazard ratios ajustados, IC 95%",
        r_lower="menor risco",
        r_higher="maior risco",
        d_eyebrow="02 — aplicação · Streamlit",
        d_title=["Câncer do colo do útero", "em SP, ano a ano"],
        d_title_m=["Câncer do colo", "do útero em SP,", "ano a ano"],
        d_window="DFOSP.py — streamlit run",
        d_filters="filtros",
        d_age="idade",
        d_stage="estádio",
        d_outcome="desfecho",
        d_alive="vivo",
        d_dead="óbito",
        d_chart="diagnósticos por ano",
        d_2020="2020 · −20%",
        d_fig=[" 55.647 registros públicos da FOSP por ano de diagnóstico · 2023 incompleto"],
        d_fig_m=[" 55.647 registros públicos da", "FOSP por ano · 2023 incompleto"],
        m_eyebrow="03 — automação · a cada 15 min",
        m_title=["Uma sentinela para os", "resets de uso do Codex"],
        m_title_m=["Uma sentinela", "para os resets", "de uso do Codex"],
        m_body=["Consulta fontes públicas, classifica", "anúncios de reset com regras",
                "determinísticas e só avisa no", "Discord quando importa."],
        m_facts=[("R$ 0", "custo mensal"), ("0", "chamadas a LLM"), ("4", "fontes"), ("2", "agendadores")],
        m_likely="provável",
        m_confirmed="confirmado",
        m_note=["execução ilustrativa, baseada no README do projeto"],
        m_note_m=["execução ilustrativa, baseada", "no README do projeto"],
    ),
}


class Layout:
    """Sizes in SVG units for one card variant."""

    def __init__(self, mobile):
        self.mobile = mobile
        self.W = 720 if mobile else 1200
        self.r = canvas(self.W, mobile)
        for k, v in SIZES[mobile].items():
            setattr(self, k, self.r(v))


def frame(L, H, t):
    r = L.r
    return (
        f'<rect x="{r(.6):.1f}" y="{r(.6):.1f}" width="{L.W - r(1.2):.1f}" height="{H - r(1.2):.1f}" '
        f'rx="{r(12):.1f}" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="{r(1):.2f}"/>'
    )


def header(L, s, eyebrow_key, title_key):
    """Eyebrow + serif title. Returns (svg, y below the title)."""
    y = L.pad + L.eyebrow
    out = [text(MONO, s[eyebrow_key], L.pad, y, L.eyebrow, "ac")[0]]
    y += L.eyebrow * 1.2
    for line in s[title_key + ("_m" if L.mobile else "")]:
        y += L.title * 1.08
        out.append(text(SERIF, line, L.pad, y, L.title, "fg")[0])
    return "".join(out), y


def body_lines(L, lines, y, x=None):
    x = L.pad if x is None else x
    out = []
    for line in lines:
        y += L.body * 1.6
        out.append(text(MONO, line, x, y, L.body, "mu")[0])
    return "".join(out), y


def stats(L, items, x, y, col_w):
    out = []
    row_h = L.num + L.label * 2.4
    for i, (num, lbl) in enumerate(items):
        cx = x + (i % 2) * col_w
        cy = y + L.num + (i // 2) * row_h
        out.append(text(MONO_MD, num, cx, cy, L.num, "fg")[0])
        out.append(text(MONO, lbl, cx, cy + L.label * 1.5, L.label, "mu")[0])
    end = y + L.num + row_h + L.label * 1.5
    return f'<g class="st">{"".join(out)}</g>', end


def window(L, t, x, y, w, h, title):
    r = L.r
    bar = r(24)
    out = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r(8):.1f}" '
        f'fill="{t["panel2"]}" stroke="{t["line"]}" stroke-width="{r(1):.2f}"/>'
        f'<path class="ln" stroke-width="{r(1):.2f}" d="M{x:.1f} {y + bar:.1f} H{x + w:.1f}"/>'
    ]
    for k in range(3):
        out.append(f'<circle cx="{x + r(13) + k * r(11):.1f}" cy="{y + bar / 2:.1f}" r="{r(3.5):.1f}" fill="{t["line"]}"/>')
    out.append(text(MONO, title, x + w / 2, y + bar / 2 + L.small * 0.35, L.small, "fa", anchor="middle")[0])
    return "".join(out), y + bar


def caption(L, label, lines, x, y):
    out = []
    f1, wf = text(SERIF_IT, label, x, y, L.cap, "fg")
    out.append(f1)
    for i, line in enumerate(lines):
        out.append(text(SERIF, line, x + (wf if i == 0 else 0), y + i * L.cap * 1.2, L.cap, "mu")[0])
    return "".join(out), y + (len(lines) - 1) * L.cap * 1.2


# ---------------------------------------------------------------- research

def forest(L, lang, t, x, y, w):
    s, r = C[lang], L.r
    size = L.small
    row_h = r(36) if not L.mobile else r(32)
    label_w = max(MONO.width(row[lang], size) for row in HR["rows"]) + r(12)
    val_w = MONO_MD.width("2,18", size) + r(10)
    pw = w - label_w - val_w
    lo_d, hi_d = 0.45, 2.5
    px = lambda v: x + label_w + (math.log(v) - math.log(lo_d)) / (math.log(hi_d) - math.log(lo_d)) * pw
    rows = HR["rows"]
    top = y + size * 1.9
    bottom = top + row_h * len(rows)
    ref = px(1)
    sw = r(1)
    out, css = [], []
    out.append(text(MONO, s["r_lower"], ref - r(6), y + size, size, "cool", anchor="end")[0])
    out.append(text(MONO, s["r_higher"], ref + r(6), y + size, size, "hot")[0])
    out.append(f'<path class="ln" stroke-width="{sw:.2f}" d="M{x + label_w:.1f} {bottom + r(4):.1f} H{x + label_w + pw:.1f}"/>')
    out.append(
        f'<path stroke="{t["fa"]}" stroke-width="{sw:.2f}" stroke-dasharray="{r(3):.1f} {r(3):.1f}" '
        f'd="M{ref:.1f} {top - r(6):.1f} V{bottom + r(4):.1f}"/>'
    )
    for v in (0.5, 1, 2):
        lab = f"{v:g}".replace(".", "," if lang == "pt" else ".")
        out.append(text(MONO, lab, px(v), bottom + r(4) + size * 1.4, size, "fa", anchor="middle")[0])
    for i, row in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        out.append(text(MONO, row[lang], x + label_w - r(12), cy + size * 0.35, size, "mu", anchor="end")[0])
        up = row["hr"] > 1
        col = t["hot"] if up else t["cool"]
        hx = px(row["hr"])
        x1, x2 = (ref, hx) if up else (hx, ref)
        out.append(
            f'<rect class="s{i}" x="{x1:.1f}" y="{cy - r(1.2):.1f}" width="{x2 - x1:.1f}" height="{r(2.4):.1f}" fill="{col}" opacity=".55"/>'
            f'<g class="p{i}"><rect x="{px(row["lo"]):.1f}" y="{cy - r(4.5):.1f}" width="{max(px(row["hi"]) - px(row["lo"]), r(1.5)):.1f}" '
            f'height="{r(9):.1f}" rx="{r(1.5):.1f}" fill="{col}" opacity=".35"/>'
            f'<circle cx="{hx:.1f}" cy="{cy:.1f}" r="{r(4.2):.1f}" fill="{col}"/>'
        )
        val = f"{row['hr']:.2f}".replace(".", "," if lang == "pt" else ".")
        out.append(text(MONO_MD, val, x + w, cy + size * 0.35, size, "fg", anchor="end")[0] + "</g>")
        d = 0.35 + i * 0.13
        origin = "0 50%" if up else "100% 50%"
        css.append(
            f".s{i}{{transform-box:fill-box;transform-origin:{origin};animation:gx {P}s cubic-bezier(.2,.8,.2,1) {d:.2f}s infinite both}}"
            f".p{i}{{animation:pop {P}s ease {d + .35:.2f}s infinite both}}"
        )
    return "".join(out), "".join(css), bottom + r(4) + size * 1.4


def research(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    L = Layout(mobile)
    r = L.r
    css = [base_css(t), KEYS, f".st{{animation:pop {P}s ease .1s infinite both}}"]
    head, y = header(L, s, "r_eyebrow", "r_title")
    parts = [head]
    if mobile:
        st, y = stats(L, s["r_stats"], L.pad, y + r(18), (L.W - 2 * L.pad) / 2)
        parts.append(st)
        fb, fc, end = forest(L, lang, t, L.pad, y + r(22), L.W - 2 * L.pad)
        cap, cy = caption(L, "Fig. 2", [s["r_fig"]], L.pad, end + L.cap * 2.2)
    else:
        bl, y = body_lines(L, s["r_body"], y + r(14))
        parts.append(bl)
        st, y = stats(L, s["r_stats"], L.pad, y + r(22), r(165))
        parts.append(st)
        fx = r(400)
        fb, fc, end = forest(L, lang, t, fx, L.pad + r(4), L.W - L.pad - fx)
        cap, cy = caption(L, "Fig. 2", [s["r_fig"]], fx + r(40), end + L.cap * 2.2)
        cy = max(cy, y)
    parts += [fb, cap]
    css.append(fc)
    H = int(cy + L.pad)
    desc = (
        "Cox model on the FOSP registry: C-index 0.747, 37,499 patients, 22,078 deaths. "
        "Adjusted hazard ratios: metastasis 2.18, no treatment 1.73, recurrence 1.20, stage 1.12 per level, "
        "hormone therapy 0.66, chemotherapy 0.59, surgery 0.55."
    )
    return svg(L.W, H, "Colorectal cancer survival research", desc, frame(L, H, t) + "".join(parts), "".join(css))


# --------------------------------------------------------------- dashboard

def chips(L, t, labels, x, y, on=None):
    r = L.r
    out = []
    h = L.small * 1.8
    for i, lab in enumerate(labels):
        w = MONO.width(lab, L.small) + r(12)
        sel = i == on
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r(4):.1f}" '
            f'fill="{t["ac"] if sel else "none"}" fill-opacity="{.15 if sel else 0}" '
            f'stroke="{t["ac"] if sel else t["line"]}" stroke-width="{r(1):.2f}"/>'
        )
        out.append(text(MONO, lab, x + w / 2, y + h / 2 + L.small * 0.35, L.small, "ac" if sel else "mu", anchor="middle")[0])
        x += w + r(4)
    return "".join(out), y + h


def dashboard(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    L = Layout(mobile)
    r = L.r
    css = [base_css(t), KEYS]
    years = [(int(k), v) for k, v in YEARS["years"].items() if int(k) <= 2023]
    vmax = max(v for _, v in years)
    head, y = header(L, s, "d_eyebrow", "d_title")
    parts = [head]

    wx, wy, ww = L.pad, y + r(22), L.W - 2 * L.pad
    side_w = 0 if mobile else r(200)
    # sidebar contents decide the window height on desktop
    side = []
    if side_w:
        sx = wx + r(14)
        sy = wy + r(24) + r(14) + L.body
        side.append(text(MONO_MD, s["d_filters"], sx, sy, L.body, "fg")[0])
        yy = sy + r(26)
        side.append(text(MONO, s["d_age"], sx, yy, L.small, "mu")[0])
        yy += r(14)
        x1, x2 = sx + r(5), wx + side_w - r(20)
        side.append(
            f'<path stroke="{t["ac"]}" stroke-width="{r(2.2):.1f}" stroke-linecap="round" d="M{x1:.1f} {yy:.1f} H{x2:.1f}"/>'
            f'<circle cx="{x1:.1f}" cy="{yy:.1f}" r="{r(4.5):.1f}" fill="{t["panel2"]}" stroke="{t["ac"]}" stroke-width="{r(1.8):.1f}"/>'
            f'<circle cx="{x2:.1f}" cy="{yy:.1f}" r="{r(4.5):.1f}" fill="{t["panel2"]}" stroke="{t["ac"]}" stroke-width="{r(1.8):.1f}"/>'
        )
        yy += r(28)
        side.append(text(MONO, s["d_stage"], sx, yy, L.small, "mu")[0])
        c, yy = chips(L, t, ["0", "I", "II", "III", "IV"], sx, yy + r(8), on=0)
        side.append(c)
        yy += r(24)
        side.append(text(MONO, s["d_outcome"], sx, yy, L.small, "mu")[0])
        c, yy = chips(L, t, [s["d_alive"], s["d_dead"]], sx, yy + r(8))
        side.append(c)
        wh = yy + r(16) - wy
    else:
        wh = r(230)
    win, inner_top = window(L, t, wx, wy, ww, wh, s["d_window"])
    parts.append(win)
    if side_w:
        parts.append(f'<path class="ln" stroke-width="{r(1):.2f}" d="M{wx + side_w:.1f} {inner_top:.1f} V{wy + wh:.1f}"/>')
        parts.append("".join(side))

    cx0 = wx + side_w + r(16)
    cw = wx + ww - r(16) - cx0
    title_y = inner_top + r(14) + L.body
    parts.append(text(MONO_MD, s["d_chart"], cx0, title_y, L.body, "fg")[0])
    ctop = title_y + L.small * 2.6
    cbot = wy + wh - L.small * 2.2
    n = len(years)
    slot = cw / n
    bw = slot * 0.64
    bars = []
    for i, (yr, v) in enumerate(years):
        h = (cbot - ctop) * v / vmax
        bx = cx0 + i * slot + (slot - bw) / 2
        hl, lag = yr == 2020, yr == 2023
        fill = t["ac"] if hl else t["fa"]
        op = "0.45" if lag else ("1" if hl else "0.7")
        bars.append(f'<rect class="b{i}" x="{bx:.1f}" y="{cbot - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{r(1.2):.1f}" fill="{fill}" opacity="{op}"/>')
        css.append(
            f".b{i}{{transform-box:fill-box;transform-origin:50% 100%;animation:gy {P}s cubic-bezier(.2,.8,.2,1) {0.3 + i * 0.045:.2f}s infinite both}}"
        )
        if yr in (2000, 2010, 2020):
            bars.append(text(MONO, str(yr), bx + bw / 2, cbot + L.small * 1.5, L.small, "fa", anchor="middle")[0])
        if hl:
            ax, ay = bx + bw / 2, cbot - h
            bars.append(
                f'<g class="ann"><path stroke="{t["ac"]}" stroke-width="{r(1):.2f}" d="M{ax:.1f} {ay - r(4):.1f} V{ctop - L.small * 0.2:.1f}"/>'
                + text(MONO_MD, s["d_2020"], ax - r(5), ctop - L.small * 0.6, L.small, "ac", anchor="end")[0]
                + "</g>"
            )
    parts.append(f'<path class="ln" stroke-width="{r(1):.2f}" d="M{cx0:.1f} {cbot + 0.5:.1f} H{cx0 + cw:.1f}"/>')
    parts.append("".join(bars))
    css.append(f".ann{{animation:pop {P}s ease 1.6s infinite both}}")

    cap, cy = caption(L, "Fig. 3", s["d_fig_m" if mobile else "d_fig"], L.pad, wy + wh + L.cap * 2.2)
    parts.append(cap)
    H = int(cy + L.pad)
    desc = (
        "Streamlit dashboard with age, stage and outcome filters. Chart: diagnoses per year in the "
        "public FOSP cervical cancer data, 2000 to 2023, with a 20 percent drop in 2020."
    )
    return svg(L.W, H, "Cervical cancer dashboard", desc, frame(L, H, t) + "".join(parts), "".join(css))


# ----------------------------------------------------------------- monitor

LOG = [
    ("$ ", "python src/run_monitor.py", "fg"),
    ("", "cron :07 → workflow_dispatch", "mu"),
    ("", "fetch help.openai.com ...... ok", "mu"),
    ("", "fetch community.openai.com . ok", "mu"),
    ("", "fetch codexreset.org ....... ok", "mu"),
    ("", "classify  reset · global · high", "fg"),
    ("", "dedupe    3 sources → 1 event", "fg"),
    ("", "notify    discord #codex-alerts", "fg"),
]


def monitor(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    L = Layout(mobile)
    r = L.r
    css = [base_css(t), KEYS, f".st{{animation:pop {P}s ease .1s infinite both}}"]
    head, y = header(L, s, "m_eyebrow", "m_title")
    parts = [head]
    if mobile:
        st, y = stats(L, s["m_facts"], L.pad, y + r(18), (L.W - 2 * L.pad) / 2)
        parts.append(st)
        tx, ty, tw = L.pad, y + r(22), L.W - 2 * L.pad
        left_end = y
    else:
        bl, y = body_lines(L, s["m_body"], y + r(14))
        parts.append(bl)
        st, left_end = stats(L, s["m_facts"], L.pad, y + r(22), r(165))
        parts.append(st)
        tx, ty = r(400), L.pad
        tw = L.W - L.pad - tx
    fs, lh = L.term, L.term * 1.85
    th = r(24) + r(18) + lh * (len(LOG) + 1) + r(8)
    win, inner_top = window(L, t, tx, ty, tw, th, "codex-reset-monitor")
    parts.append(win)

    cps, start = 34.0, 0.4
    y = inner_top + r(16) + fs
    x = tx + r(14)
    for i, (prefix, line, cls) in enumerate(LOG):
        uid = f"l{i}"
        el, lx = "", x
        if prefix:
            pe, pw = text(MONO, prefix, x, y, fs, "gr")
            el += pe
            lx += pw
        le, lw = text(MONO, line, lx, y, fs, cls)
        el += le
        n = len(line)
        dur = n / cps if i == 0 else 0.25
        a, b = start / P * 100, (start + dur) / P * 100
        parts.append(
            f'<clipPath id="{uid}"><rect class="{uid}" x="{x - r(1):.1f}" y="{y - fs * 1.2:.1f}" '
            f'width="{lx - x + lw + r(2):.1f}" height="{fs * 1.7:.1f}"/></clipPath>'
            f'<g clip-path="url(#{uid})">{el}</g>'
        )
        steps = n if i == 0 else 4
        css.append(
            f"@keyframes k{uid}{{0%,{a:.2f}%{{transform:scaleX(0)}}{b:.2f}%,93%{{transform:scaleX(1)}}97%,100%{{transform:scaleX(0)}}}}"
            f".{uid}{{transform-box:fill-box;transform-origin:0 50%;animation:k{uid} {P}s steps({steps}) infinite}}"
        )
        start += dur + (0.9 if i == 0 else 0.55)
        y += lh
    a = start / P * 100
    dot = r(3.5)
    cy = y - fs * 0.33
    e1, w1 = text(MONO_MD, s["m_likely"], x + dot * 2 + r(6), y, fs, "warn")
    arrow, wa = text(MONO, " → ", x + dot * 2 + r(6) + w1, y, fs, "mu")
    x2 = x + dot * 2 + r(6) + w1 + wa
    e2, w2 = text(MONO_MD, s["m_confirmed"], x2 + dot * 2 + r(6), y, fs, "gr")
    parts.append(
        f'<g class="fin"><circle cx="{x + dot:.1f}" cy="{cy:.1f}" r="{dot:.1f}" fill="{t["warn"]}"/>{e1}{arrow}'
        f'<circle cx="{x2 + dot:.1f}" cy="{cy:.1f}" r="{dot:.1f}" fill="{t["gr"]}"/>{e2}'
        f'<rect class="cur" x="{x2 + dot * 2 + r(6) + w2 + r(5):.1f}" y="{y - fs * 0.85:.1f}" '
        f'width="{fs * .6:.1f}" height="{fs * 1.1:.1f}" fill="{t["ac"]}"/></g>'
    )
    css.append(
        f"@keyframes fin{{0%,{a:.2f}%{{opacity:0}}{a + 1:.2f}%,93%{{opacity:1}}97%,100%{{opacity:0}}}}"
        f".fin{{animation:fin {P}s linear infinite}}.cur{{animation:blink 1.1s steps(1) infinite}}"
    )
    note = []
    ny = ty + th + L.cap * 1.9
    for i, line in enumerate(s["m_note_m" if mobile else "m_note"]):
        note.append(text(SERIF_IT, line, tx, ny + i * L.cap * 1.2, L.cap, "fa")[0])
        last = ny + i * L.cap * 1.2
    parts.append("".join(note))
    H = int(max(last, left_end) + L.pad)
    desc = (
        "Terminal showing an illustrative run: a Cloudflare cron dispatches the workflow, three public "
        "sources are fetched, the announcement is classified, deduplicated into one event and sent to Discord. "
        "Free to run, no LLM calls, four sources, two independent schedulers."
    )
    return svg(L.W, H, "Codex reset monitor", desc, frame(L, H, t) + "".join(parts), "".join(css))


BUILDERS = {"research": research, "dashboard": dashboard, "monitor": monitor}
