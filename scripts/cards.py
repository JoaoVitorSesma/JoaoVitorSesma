"""Project cards: research (forest plot), dashboard (cases per year) and monitor (terminal)."""

import json
import math
from pathlib import Path

from svgkit import MONO, MONO_MD, SERIF, SERIF_IT, THEMES, base_css, svg, text

DATA = Path(__file__).parent / "data"
HR = json.loads((DATA / "cox_hazard_ratios.json").read_text())
YEARS = json.loads((DATA / "dashboard_cases_by_year.json").read_text())

P = 16.0  # loop period for card animations, seconds

KEYS = (
    "@keyframes gx{0%{transform:scaleX(0)}9%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
    "@keyframes gy{0%{transform:scaleY(0)}8%,92%{transform:scaleY(1)}100%{transform:scaleY(0)}}"
    "@keyframes pop{0%{opacity:0}9%,92%{opacity:1}100%{opacity:0}}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    "@keyframes ring{0%{r:5;opacity:.6}60%,100%{r:16;opacity:0}}"
)

C = {
    "en": dict(
        r_eyebrow="01 — undergraduate research · FOSP",
        r_title=["Who survives colorectal", "cancer — and why?"],
        r_title_m=["Who survives", "colorectal cancer", "— and why?"],
        r_stats=[("0.747", "C-index"), ("37,499", "patients"), ("22,078", "deaths observed"), ("2000–23", "follow-up")],
        r_body=["Cox proportional hazards on São Paulo's", "cancer registry: cleaning, encoding,", "variable selection and validation."],
        r_fig=" Adjusted hazard ratios, 95% CI",
        r_axis="hazard ratio (log)",
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
        d_lag="registry lag",
        d_fig=" 55,647 public FOSP records per diagnosis year · 2023 still incomplete",
        d_fig_m=[" 55,647 public FOSP records", "per diagnosis year · 2023 incomplete"],
        m_eyebrow="03 — automation · every 15 min",
        m_title=["A watchtower for", "Codex usage resets"],
        m_title_m=["A watchtower", "for Codex", "usage resets"],
        m_body=["Polls public sources, classifies reset", "announcements with deterministic rules", "and alerts Discord only when it matters."],
        m_facts=[("R$ 0", "monthly cost"), ("0", "LLM calls"), ("4", "sources"), ("2", "independent clocks")],
        m_note="illustrative run, based on the project README",
    ),
    "pt": dict(
        r_eyebrow="01 — iniciação científica · FOSP",
        r_title=["Quem sobrevive ao câncer", "colorretal — e por quê?"],
        r_title_m=["Quem sobrevive", "ao câncer colorretal", "— e por quê?"],
        r_stats=[("0,747", "C-index"), ("37.499", "pacientes"), ("22.078", "óbitos observados"), ("2000–23", "seguimento")],
        r_body=["Modelo de riscos proporcionais de Cox", "no registro de câncer de SP: limpeza,", "codificação, seleção e validação."],
        r_fig=" Hazard ratios ajustados, IC 95%",
        r_axis="hazard ratio (log)",
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
        d_lag="atraso do registro",
        d_fig=" 55.647 registros públicos da FOSP por ano de diagnóstico · 2023 incompleto",
        d_fig_m=[" 55.647 registros públicos da", "FOSP por ano · 2023 incompleto"],
        m_eyebrow="03 — automação · a cada 15 min",
        m_title=["Uma sentinela para os", "resets de uso do Codex"],
        m_title_m=["Uma sentinela", "para os resets", "de uso do Codex"],
        m_body=["Consulta fontes públicas, classifica", "anúncios de reset com regras", "determinísticas e só avisa quando importa."],
        m_facts=[("R$ 0", "custo mensal"), ("0", "chamadas a LLM"), ("4", "fontes"), ("2", "relógios independentes")],
        m_note="execução ilustrativa, baseada no README do projeto",
    ),
}


def frame(W, H, t):
    return (
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t["panel"]}" '
        f'stroke="{t["line"]}" stroke-width="1.5"/>'
    )


def title_block(lang, key, x, y, size, cls="fg"):
    out = []
    for line in C[lang][key]:
        out.append(text(SERIF, line, x, y, size, cls)[0])
        y += size * 1.08
    return "".join(out), y


def stats(items, x, y, col_w, num_size, lbl_size, cols=2, row_h=None):
    row_h = row_h or num_size * 2.3
    out = []
    for i, (num, lbl) in enumerate(items):
        cx = x + (i % cols) * col_w
        cy = y + (i // cols) * row_h
        out.append(text(MONO_MD, num, cx, cy, num_size, "fg")[0])
        out.append(text(MONO, lbl, cx, cy + lbl_size * 1.6, lbl_size, "mu")[0])
    return f'<g class="st">{"".join(out)}</g>'


def forest(lang, t, x, y, w, row_h, label_w, size):
    s = C[lang]
    lo_d, hi_d = 0.45, 2.5
    pw = w - label_w - 70
    px = lambda v: x + label_w + (math.log(v) - math.log(lo_d)) / (math.log(hi_d) - math.log(lo_d)) * pw
    rows = HR["rows"]
    top, bottom = y, y + row_h * len(rows)
    ref = px(1)
    out, css = [], []
    out.append(f'<path class="ln" stroke-width="1" d="M{x + label_w} {bottom + 6} H{x + label_w + pw}"/>')
    out.append(f'<path stroke="{t["fa"]}" stroke-width="1.25" stroke-dasharray="4 4" d="M{ref:.1f} {top - 14} V{bottom + 6}"/>')
    for v in (0.5, 1, 2):
        out.append(text(MONO, f"{v:g}".replace(".", "," if lang == "pt" else "."), px(v), bottom + 6 + size * 1.5, size - 1, "fa", anchor="middle")[0])
    out.append(text(MONO, s["r_lower"], ref - 10, top - 20, size - 1, "cool", anchor="end")[0])
    out.append(text(MONO, s["r_higher"], ref + 10, top - 20, size - 1, "hot")[0])
    for i, r in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        lbl = r[lang]
        out.append(text(MONO, lbl, x + label_w - 16, cy + size * 0.35, size, "mu", anchor="end")[0])
        up = r["hr"] > 1
        col = t["hot"] if up else t["cool"]
        hx = px(r["hr"])
        x1, x2 = (ref, hx) if up else (hx, ref)
        cls = f"s{i}"
        out.append(
            f'<rect class="{cls}" x="{x1:.1f}" y="{cy - 1.5:.1f}" width="{x2 - x1:.1f}" height="3" fill="{col}" opacity=".55"/>'
            f'<g class="p{i}"><rect x="{px(r["lo"]):.1f}" y="{cy - 6:.1f}" width="{max(px(r["hi"]) - px(r["lo"]), 2):.1f}" '
            f'height="12" rx="2" fill="{col}" opacity=".35"/>'
            f'<circle cx="{hx:.1f}" cy="{cy:.1f}" r="5.5" fill="{col}"/>'
        )
        val = f"{r['hr']:.2f}"
        if lang == "pt":
            val = val.replace(".", ",")
        out.append(text(MONO_MD, val, x + w, cy + size * 0.35, size - 1, "fg", anchor="end")[0] + "</g>")
        d = 0.35 + i * 0.13
        origin = "0 50%" if up else "100% 50%"
        css.append(
            f".{cls}{{transform-box:fill-box;transform-origin:{origin};animation:gx {P}s cubic-bezier(.2,.8,.2,1) {d:.2f}s infinite both}}"
            f".p{i}{{animation:pop {P}s ease {d + .35:.2f}s infinite both}}"
        )
    return "".join(out), "".join(css), bottom + 6 + size * 1.5


def research(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    css = [base_css(t), KEYS, f".st{{animation:pop {P}s ease .1s infinite both}}"]
    if mobile:
        W, pad = 720, 40
        parts = [text(MONO, s["r_eyebrow"], pad, 64, 18, "ac")[0]]
        tb, y = title_block(lang, "r_title_m", pad, 128, 54)
        parts.append(tb)
        parts.append(stats(s["r_stats"], pad, y + 30, 320, 34, 17))
        fy = y + 262
        body, c, end = forest(lang, t, pad, fy, W - pad * 2, 52, 250, 18)
        cap_y = end + 58
        f1, wf = text(SERIF_IT, "Fig. 2", pad, cap_y, 28, "fg")
        f2, _ = text(SERIF, s["r_fig"], pad + wf, cap_y, 28, "mu")
        H = int(cap_y + 46)
    else:
        W, H, pad = 1200, 560, 48
        parts = [text(MONO, s["r_eyebrow"], pad, 70, 15, "ac")[0]]
        tb, y = title_block(lang, "r_title", pad, 134, 50)
        parts.append(tb)
        body_lines = []
        yy = y + 14
        for line in s["r_body"]:
            body_lines.append(text(MONO, line, pad, yy, 15, "mu")[0])
            yy += 24
        parts.append("".join(body_lines))
        parts.append(stats(s["r_stats"], pad, yy + 46, 220, 30, 14))
        body, c, end = forest(lang, t, 560, 118, 600, 46, 210, 15)
        cap_y = end + 46
        f1, wf = text(SERIF_IT, "Fig. 2", 560 + 60, cap_y, 23, "fg")
        f2, _ = text(SERIF, s["r_fig"], 560 + 60 + wf, cap_y, 23, "mu")
    parts.append(body)
    parts.append(f1 + f2)
    css.append(c)
    title = "Colorectal cancer survival research"
    desc = (
        "Cox model on the FOSP registry: C-index 0.747, 37,499 patients, 22,078 deaths. "
        "Adjusted hazard ratios: metastasis 2.18, no treatment 1.73, recurrence 1.20, stage 1.12 per level, "
        "hormone therapy 0.66, chemotherapy 0.59, surgery 0.55."
    )
    return svg(W, H, title, desc, frame(W, H, t) + "".join(parts), "".join(css))


def dashboard(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    css = [base_css(t), KEYS]
    years = [(int(k), v) for k, v in YEARS["years"].items() if int(k) <= 2023]
    vmax = max(v for _, v in years)
    if mobile:
        W, pad = 720, 40
        parts = [text(MONO, s["d_eyebrow"], pad, 64, 18, "ac")[0]]
        tb, y = title_block(lang, "d_title_m", pad, 128, 54)
        parts.append(tb)
        win_x, win_y, win_w, win_h = pad, y + 26, W - pad * 2, 470
        side_w = 0
        fs = 17
    else:
        W, H, pad = 1200, 560, 48
        parts = [text(MONO, s["d_eyebrow"], pad, 70, 15, "ac")[0]]
        tb, y = title_block(lang, "d_title", pad, 134, 50)
        parts.append(tb)
        win_x, win_y, win_w, win_h = pad, 222, W - pad * 2, 262
        side_w = 250
        fs = 14
    # app window chrome
    parts.append(
        f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" rx="12" fill="{t["panel2"]}" stroke="{t["line"]}"/>'
        f'<path class="ln" d="M{win_x} {win_y + 34} H{win_x + win_w}"/>'
    )
    for k in range(3):
        parts.append(f'<circle cx="{win_x + 20 + k * 16}" cy="{win_y + 17}" r="5" fill="{t["line"]}"/>')
    parts.append(text(MONO, s["d_window"], win_x + win_w / 2, win_y + 22, fs - 2, "fa", anchor="middle")[0])

    if side_w:
        sx, sy = win_x + 22, win_y + 66
        parts.append(f'<path class="ln" d="M{win_x + side_w} {win_y + 34} V{win_y + win_h}"/>')
        side = [text(MONO_MD, s["d_filters"], sx, sy, fs, "fg")[0]]
        side.append(text(MONO, s["d_age"], sx, sy + 34, fs - 1, "mu")[0])
        side.append(
            f'<path stroke="{t["ac"]}" stroke-width="3" stroke-linecap="round" d="M{sx + 4} {sy + 52} H{sx + 196}"/>'
            f'<circle cx="{sx + 4}" cy="{sy + 52}" r="6" fill="{t["panel2"]}" stroke="{t["ac"]}" stroke-width="2.5"/>'
            f'<circle cx="{sx + 196}" cy="{sy + 52}" r="6" fill="{t["panel2"]}" stroke="{t["ac"]}" stroke-width="2.5"/>'
        )
        side.append(text(MONO, s["d_stage"], sx, sy + 90, fs - 1, "mu")[0])
        cx = sx
        for i, lab in enumerate(["0", "I", "II", "III", "IV"]):
            wch = MONO.width(lab, fs - 2) + 16
            on = i == 0
            side.append(
                f'<rect x="{cx}" y="{sy + 100}" width="{wch:.1f}" height="24" rx="6" '
                f'fill="{t["ac"] if on else "none"}" fill-opacity="{.15 if on else 0}" stroke="{t["ac"] if on else t["line"]}"/>'
            )
            side.append(text(MONO, lab, cx + wch / 2, sy + 117, fs - 2, "ac" if on else "mu", anchor="middle")[0])
            cx += wch + 6
        side.append(text(MONO, s["d_outcome"], sx, sy + 152, fs - 1, "mu")[0])
        cx = sx
        for i, lab in enumerate([s["d_alive"], s["d_dead"]]):
            wch = MONO.width(lab, fs - 2) + 16
            side.append(
                f'<rect x="{cx}" y="{sy + 162}" width="{wch:.1f}" height="24" rx="6" fill="none" stroke="{t["line"]}"/>'
            )
            side.append(text(MONO, lab, cx + wch / 2, sy + 179, fs - 2, "mu", anchor="middle")[0])
            cx += wch + 6
        parts.append("".join(side))

    # bar chart
    cx0 = win_x + side_w + 28
    cw = win_x + win_w - 28 - cx0
    ctop = win_y + 76
    cbot = win_y + win_h - 40
    parts.append(text(MONO_MD, s["d_chart"], cx0, win_y + 62, fs, "fg")[0])
    n = len(years)
    slot = cw / n
    bw = slot * 0.62
    bars = []
    for i, (yr, v) in enumerate(years):
        h = (cbot - ctop) * v / vmax
        bx = cx0 + i * slot + (slot - bw) / 2
        hl = yr == 2020
        lag = yr == 2023
        fill = t["ac"] if hl else t["fa"]
        op = "0.45" if lag else ("1" if hl else "0.7")
        bars.append(
            f'<rect class="b{i}" x="{bx:.1f}" y="{cbot - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{fill}" opacity="{op}"/>'
        )
        css.append(
            f".b{i}{{transform-box:fill-box;transform-origin:50% 100%;animation:gy {P}s cubic-bezier(.2,.8,.2,1) {0.3 + i * 0.045:.2f}s infinite both}}"
        )
        if yr in (2000, 2010, 2020, 2023) or (mobile and yr in (2000, 2010, 2020)):
            if not (mobile and yr == 2023):
                bars.append(text(MONO, str(yr), bx + bw / 2, cbot + 22, fs - 2, "fa", anchor="middle")[0])
        if hl:
            ax, ay = bx + bw / 2, cbot - h
            bars.append(
                f'<g class="ann"><path stroke="{t["ac"]}" stroke-width="1.25" d="M{ax:.1f} {ay - 6:.1f} V{ctop - 2:.1f}"/>'
                + text(MONO_MD, s["d_2020"], ax - 6, ctop - 8, fs - 1, "ac", anchor="end")[0]
                + "</g>"
            )
    parts.append(f'<path class="ln" d="M{cx0} {cbot + 0.5} H{cx0 + cw}"/>')
    parts.append("".join(bars))
    css.append(f".ann{{animation:pop {P}s ease 1.6s infinite both}}")

    if mobile:
        cap_y = win_y + win_h + 56
        f1, wf = text(SERIF_IT, "Fig. 3", pad, cap_y, 28, "fg")
        f2, _ = text(SERIF, s["d_fig_m"][0], pad + wf, cap_y, 28, "mu")
        f3, _ = text(SERIF, s["d_fig_m"][1], pad, cap_y + 32, 28, "mu")
        parts.append(f1 + f2 + f3)
        H = int(cap_y + 60)
    else:
        cap_y = win_y + win_h + 44
        f1, wf = text(SERIF_IT, "Fig. 3", pad, cap_y, 23, "fg")
        f2, _ = text(SERIF, s["d_fig"], pad + wf, cap_y, 23, "mu")
        parts.append(f1 + f2)
    title = "Cervical cancer dashboard"
    desc = (
        "Streamlit dashboard with age, stage and outcome filters. Chart: diagnoses per year in the "
        "public FOSP cervical cancer data, 2000 to 2023, with a 20 percent drop in 2020."
    )
    return svg(W, H, title, desc, frame(W, H, t) + "".join(parts), "".join(css))


LOG = [
    ("$ ", "python src/run_monitor.py", "fg"),
    ("", "cron :07  cloudflare worker → workflow_dispatch", "mu"),
    ("", "fetch  help.openai.com ............. ok", "mu"),
    ("", "fetch  community.openai.com ........ ok", "mu"),
    ("", "fetch  codexreset.org .............. ok", "mu"),
    ("", "classify  type=reset  scope=global  when=09:00 BRT", "fg"),
    ("", "dedupe    3 sources → 1 event", "fg"),
    ("", "notify    discord #codex-alerts", "fg"),
]


def monitor(lang, theme, mobile):
    t, s = THEMES[theme], C[lang]
    css = [base_css(t), KEYS, f".st{{animation:pop {P}s ease .1s infinite both}}"]
    if mobile:
        W, pad = 720, 40
        parts = [text(MONO, s["m_eyebrow"], pad, 64, 18, "ac")[0]]
        tb, y = title_block(lang, "m_title_m", pad, 128, 54)
        parts.append(tb)
        parts.append(stats(s["m_facts"], pad, y + 30, 320, 34, 17))
        tx, ty, tw, fs, lh = pad, y + 226, W - pad * 2, 19, 40
    else:
        W, pad = 1200, 48
        parts = [text(MONO, s["m_eyebrow"], pad, 70, 15, "ac")[0]]
        tb, y = title_block(lang, "m_title", pad, 134, 50)
        parts.append(tb)
        yy = y + 14
        for line in s["m_body"]:
            parts.append(text(MONO, line, pad, yy, 15, "mu")[0])
            yy += 24
        parts.append(stats(s["m_facts"], pad, yy + 46, 220, 30, 14))
        tx, ty, tw, fs, lh = 560, 48, 592, 15, 34
    th = 70 + lh * len(LOG) + 40
    parts.append(
        f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{t["panel2"]}" stroke="{t["line"]}"/>'
        f'<path class="ln" d="M{tx} {ty + 34} H{tx + tw}"/>'
    )
    for k in range(3):
        parts.append(f'<circle cx="{tx + 20 + k * 16}" cy="{ty + 17}" r="5" fill="{t["line"]}"/>')
    parts.append(text(MONO, "codex-reset-monitor", tx + tw / 2, ty + 22, fs - 1, "fa", anchor="middle")[0])

    cps, start = 34.0, 0.4
    y = ty + 72
    x = tx + 22
    for i, (prefix, line, cls) in enumerate(LOG):
        uid = f"l{i}"
        el = ""
        px = x
        if prefix:
            pe, pw = text(MONO, prefix, x, y, fs, "gr")
            el += pe
            px += pw
        le, lw = text(MONO, line, px, y, fs, cls)
        el += le
        n = len(line)
        dur = n / cps if i == 0 else 0.25
        a = start / P * 100
        b = (start + dur) / P * 100
        parts.append(
            f'<clipPath id="{uid}"><rect class="{uid}" x="{x - 2}" y="{y - fs * 1.2:.1f}" width="{px - x + lw + 4:.1f}" height="{fs * 1.7:.1f}"/></clipPath>'
            f'<g clip-path="url(#{uid})">{el}</g>'
        )
        steps = n if i == 0 else 4
        css.append(
            f"@keyframes k{uid}{{0%,{a:.2f}%{{transform:scaleX(0)}}{b:.2f}%,93%{{transform:scaleX(1)}}97%,100%{{transform:scaleX(0)}}}}"
            f".{uid}{{transform-box:fill-box;transform-origin:0 50%;animation:k{uid} {P}s steps({steps}) infinite}}"
        )
        start += dur + (0.9 if i == 0 else 0.55)
        y += lh
    # final status line with likely -> confirmed dots
    a = start / P * 100
    st_y = y + 6
    likely = "likely" if lang == "en" else "provável"
    confirmed = "confirmed" if lang == "en" else "confirmado"
    e1, w1 = text(MONO_MD, likely, x + 18, st_y, fs, "warn")
    arrow, wa = text(MONO, " → ", x + 18 + w1, st_y, fs, "mu")
    e2, _ = text(MONO_MD, confirmed, x + 18 + w1 + wa + 18, st_y, fs, "gr")
    parts.append(
        f'<g class="fin"><circle cx="{x + 6}" cy="{st_y - fs * 0.33:.1f}" r="5" fill="{t["warn"]}"/>{e1}{arrow}'
        f'<circle cx="{x + 18 + w1 + wa + 6:.1f}" cy="{st_y - fs * 0.33:.1f}" r="5" fill="{t["gr"]}"/>{e2}'
        f'<rect class="cur" x="{x + 18 + w1 + wa + 24 + MONO_MD.width(confirmed, fs) + 8:.1f}" y="{st_y - fs * 0.85:.1f}" width="{fs * .6:.1f}" height="{fs * 1.1:.1f}" fill="{t["ac"]}"/></g>'
    )
    css.append(
        f"@keyframes fin{{0%,{a:.2f}%{{opacity:0}}{a + 1:.2f}%,93%{{opacity:1}}97%,100%{{opacity:0}}}}"
        f".fin{{animation:fin {P}s linear infinite}}.cur{{animation:blink 1.1s steps(1) infinite}}"
    )
    note_y = ty + th + (40 if not mobile else 44)
    parts.append(text(SERIF_IT, s["m_note"], tx if not mobile else pad, note_y, 21 if not mobile else 25, "fa")[0])
    H = int(note_y + (36 if mobile else 46))
    title = "Codex reset monitor"
    desc = (
        "Terminal showing an illustrative run: a Cloudflare cron dispatches the workflow, three public "
        "sources are fetched, the announcement is classified, deduplicated into one event and sent to Discord. "
        "Free to run, no LLM calls, four sources, two independent schedulers."
    )
    return svg(W, H, title, desc, frame(W, H, t) + "".join(parts), "".join(css))


BUILDERS = {"research": research, "dashboard": dashboard, "monitor": monitor}
