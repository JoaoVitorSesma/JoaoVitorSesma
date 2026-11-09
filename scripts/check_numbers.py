"""Recompute the README's numbers from the projects themselves and compare.

    python scripts/check_numbers.py

Every figure the cards and the numbers strip show is documented in
assets/SOURCES.md. This script fetches those sources from GitHub (the Cox
notebook, the dashboard's CSV and app, the monitor's README and code), derives
each number again and checks it against scripts/data/*.json and the copy in
STR / cards.C. Exits 1 on any mismatch, so a change in a project shows up here
instead of leaving the profile quietly out of date.
"""

import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter

import build_assets
import cards

RAW = "https://raw.githubusercontent.com/JoaoVitorSesma/{repo}/main/{path}"
COX = ("Predicao-da-Sobrevida-em-Pacientes-com-Cancer-Colorretal-IC",
       "Predição_da_Sobrevida_em_Pacientes_com_Câncer_Colorretal_COX.ipynb")
CSV = ("Dashboard", "colo_utero1.csv")
APP = ("Dashboard", "DFOSP.py")
MONITOR_README = ("codex-reset-monitor", "README.md")
MONITOR_CODE = ("codex-reset-monitor", "src/monitor.py")

results = []


def fetch(repo, path):
    url = RAW.format(repo=repo, path=urllib.parse.quote(path))
    request = urllib.request.Request(url, headers={"User-Agent": "readme number check"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def check(name, shown, source):
    results.append((shown == source, name, shown, source))


def num(value, lang, decimals=0):
    """A number as each README writes it: 37,499 / 0.747 in English, 37.499 / 0,747 in Portuguese."""
    text = f"{value:,.{decimals}f}"
    return text if lang == "en" else text.translate(str.maketrans(",.", ".,"))


def research():
    data = json.loads((build_assets.ROOT / "scripts/data/cox_hazard_ratios.json").read_text(encoding="utf-8"))
    nb = json.loads(fetch(*COX))
    outputs = ["".join(o.get("data", {}).get("text/plain", [])) + "".join(o.get("text", []))
               for cell in nb["cells"] for o in cell.get("outputs", [])]
    # The last fitted model whose summary lists the covariates the card shows (cell 41;
    # an earlier spline model in cell 29 prints a similar table).
    summary = [t for t in outputs if "exp(coef)" in t and "PRESENCA_META" in t][-1]
    check("Cox observations", data["n_obs"], int(re.search(r"number of observations = (\d+)", summary)[1]))
    check("Cox events", data["events"], int(re.search(r"number of events observed = (\d+)", summary)[1]))
    printed = [float(v) for t in outputs for v in re.findall(r"(?:Concordance Index|C-index)[^:\n]*:\s*([0-9.]+)", t)]
    check("C-index printed in the notebook", data["c_index"], round(printed[0], 3) if printed else None)
    check("C-index in the summary (2 decimals)", round(data["c_index"], 2),
          float(re.search(r"Concordance = ([0-9.]+)", summary)[1]))
    table = {m[1]: m for m in re.finditer(
        r"^(\w+)\s+(-?[\d.]+)\s+([\d.]+)\s+[\d.]+\s+-?[\d.]+\s+-?[\d.]+\s+([\d.]+)\s+([\d.]+)\s*$", summary, re.M)}
    for row in data["rows"]:
        m = table.get(row["var"])
        check(f"hazard ratio {row['var']}", (row["hr"], row["lo"], row["hi"]),
              (float(m[3]), float(m[4]), float(m[5])) if m else None)
    for lang in ("en", "pt"):
        c_index, patients, deaths, _ = (v for v, _ in cards.C[lang]["r_stats"])
        check(f"[{lang}] research card C-index", c_index, num(data["c_index"], lang, 3))
        check(f"[{lang}] research card patients", patients, num(data["n_obs"], lang))
        check(f"[{lang}] research card deaths", deaths, num(data["events"], lang))
        check(f"[{lang}] numbers strip patients", build_assets.STR[lang]["stats"][0][1], num(data["n_obs"], lang))


def dashboard():
    data = json.loads((build_assets.ROOT / "scripts/data/dashboard_cases_by_year.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(io.StringIO(fetch(*CSV), newline="")))
    years = Counter(row["ANODIAG"] for row in rows)
    check("dashboard records", data["total"], len(rows))
    check("dashboard records per year", data["years"], {y: years[y] for y in data["years"]})
    drop = round((data["years"]["2020"] / data["years"]["2019"] - 1) * 100)
    app = fetch(*APP)
    regions = re.search(r"NOME_DRS\s*=\s*\[(.*?)\]", app, re.S)[1]
    n_regions = len(re.findall(r'"[^"]+"', regions))
    n_filters = len(re.findall(r"st\.sidebar\.(?:slider|segmented_control|selectbox|multiselect|radio|checkbox)\(", app))
    check("dashboard computes 36-month survival", True, "loc[36]" in app)
    for lang in ("en", "pt"):
        s = cards.C[lang]
        check(f"[{lang}] 2020 drop label", s["d_2020"], f"2020 · −{-drop}%")
        check(f"[{lang}] Fig. 2 record count", True, num(data["total"], lang) in s["d_fig"])
        check(f"[{lang}] numbers strip records", build_assets.STR[lang]["stats"][1][1], num(data["total"], lang))
        check(f"[{lang}] dashboard health regions", s["d_stats"][0][0], str(n_regions))
        check(f"[{lang}] dashboard filters", s["d_stats"][2][0], str(n_filters))


def monitor():
    readme, code = fetch(*MONITOR_README), fetch(*MONITOR_CODE)
    minutes = re.search(r"Cloudflare Cron \(([^)]*)\)", readme)[1].split(",")
    fetchers = re.search(r"SOURCE_FETCHERS\s*=\s*\{(.*?)\}", code, re.S)[1]
    n_sources = len(re.findall(r'^\s*"[^"]+"\s*:', fetchers, re.M))
    check("terminal fetches every source", sum(line.startswith("fetch ") for _, line, _ in cards.LOG), n_sources)
    for lang in ("en", "pt"):
        check(f"[{lang}] numbers strip checks a day", build_assets.STR[lang]["stats"][2][1], str(len(minutes) * 24))
        check(f"[{lang}] monitor sources", cards.C[lang]["m_facts"][2][0], str(n_sources))


def main():
    for part in (research, dashboard, monitor):
        try:
            part()
        except Exception as error:  # a source moved or changed shape: report it, keep checking
            results.append((False, f"{part.__name__}: could not read the source", "", repr(error)))
    for ok, name, shown, source in results:
        print(f"  {'ok ' if ok else 'BAD'} {name}" + ("" if ok else f": README shows {shown!r}, source gives {source!r}"))
    failed = sum(not ok for ok, *_ in results)
    print(f"{len(results) - failed} of {len(results)} numbers match their sources.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
