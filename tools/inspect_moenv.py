#!/usr/bin/env python3
"""Check what a downloaded MOENV dataset actually contains, before any modelling.

Usage:
    python tools/inspect_moenv.py data/raw/moenv/<DataID>/<timestamp>     (folder with records.json)
    python tools/inspect_moenv.py path/to/records.json [--zone 嘉南]

Prints, and writes inspect.md next to records.json:
  - number of records, every field and how often it is empty
  - for long tables (itemname + itemvalue, e.g. regional groundwater quality): every monitoring item with its
    unit(s), number of records and sites, values that are not plain numbers (e.g. "<0.001", "ND"), and min/median/max
  - sampling dates by year, groundwater districts (ugwdistname) with their number of sites
  - which of the items needed by the redox ladder and the Water analysis tab are present, overall and in one district
  - fields that could hold well depth (looked for by name), and the most common values of 'note'
Uses the Python standard library only. Reads the data; changes nothing.
"""
import argparse, json, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# items CHemTrace needs (redox ladder, Water analysis tab, As); matched on the Chinese item name or the abbreviation
NEED = [("As", "砷", r"^As$"), ("Fe", "鐵", r"^Fe$"), ("Mn", "錳", r"^Mn$"), ("DO", "溶氧", r"^DO$"),
        ("ORP/Eh", "氧化還原", r"ORP|Eh"), ("NO3-N", "硝酸鹽", r"NO3"), ("NO2-N", "亞硝酸鹽", r"NO2"),
        ("NH3-N", "氨氮", r"NH3|NH4"), ("SO4", "硫酸鹽", r"SO4"), ("TOC", "總有機碳", r"^TOC$"),
        ("pH", "氫離子濃度指數", r"^pH$"), ("Temp", "水溫", r"Temp|WT"), ("EC", "導電度", r"^EC$|Cond"),
        ("Alkalinity", "鹼度", r"Alk"), ("Ca", "鈣", r"^Ca$"), ("Mg", "鎂", r"^Mg$"), ("Na", "鈉", r"^Na$"),
        ("K", "鉀", r"^K$"), ("Cl", "氯鹽", r"^Cl"), ("Hardness", "硬度", r"Hard"), ("TDS", "總溶解固體", r"TDS")]
NUM = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
DEPTH = re.compile(r"depth|deep|井深|深度|screen|篩|layer|層", re.I)


def load(p):
    p = Path(p)
    f = p / "records.json" if p.is_dir() else p
    data = json.loads(f.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        data = data.get("records", [])
    return f, [r for r in data if isinstance(r, dict)]


def g(r, k):
    v = r.get(k)
    return "" if v is None else str(v).strip()


def num(s):
    s = s.replace(",", "")
    return float(s) if NUM.match(s) else None


def measured(v):
    """A real measurement: a number, or a value below the detection limit such as '<0.0003' or 'ND'."""
    return num(v) is not None or v.startswith("<") or v.upper() in ("ND", "N.D.")


def which_need(name, abbr):
    out = []
    for lab, zh, rx in NEED:
        if (zh and zh in name and not (lab == "NO3-N" and "亞" in name)) or (abbr and re.search(rx, abbr)):
            out.append(lab)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--zone", default="嘉南", help="text to look for in ugwdistname (default 嘉南)")
    a = ap.parse_args()
    f, R = load(a.path)
    L = []
    say = lambda s="": (print(s), L.append(s))
    say(f"# Inspection of {f}")
    say(f"\nRecords: {len(R)}")
    fields = Counter(k for r in R for k in r)
    say("\n## Fields (share of records where the value is empty)\n")
    say("| field | empty |\n|---|---|")
    for k, _ in sorted(fields.items()):
        empty = sum(1 for r in R if g(r, k) == "")
        say(f"| {k} | {empty / len(R):.0%} |" if R else f"| {k} | – |")
    dep = [k for k in fields if DEPTH.search(k)]
    say(f"\nFields whose name suggests depth or layer: {', '.join(dep) if dep else 'none'}")

    site_key = next((k for k in ("sitename", "siteid", "SITE_NAME", "site_name") if k in fields), None)
    if "ugwdistname" in fields and site_key:
        z = defaultdict(set)
        for r in R: z[g(r, "ugwdistname")].add(g(r, site_key))
        say("\n## Groundwater districts (ugwdistname)\n")
        say("| district | sites |\n|---|---|")
        for k, v in sorted(z.items(), key=lambda kv: -len(kv[1])): say(f"| {k or '(empty)'} | {len(v)} |")

    if "note" in fields:
        c = Counter(g(r, "note") for r in R if g(r, "note"))
        say(f"\n## Most common values of 'note' ({len(c)} distinct)\n")
        for k, n in c.most_common(15): say(f"- {k} ({n})")

    if "statusofuse" in fields:
        say("\n## statusofuse\n")
        for k, n in Counter(g(r, "statusofuse") for r in R).most_common(): say(f"- {k or '(empty)'}: {n}")

    if {"itemname", "itemvalue"} <= set(fields):
        abbr_key = "itemengabbreviation" if "itemengabbreviation" in fields else None
        it = defaultdict(lambda: {"abbr": Counter(), "unit": Counter(), "n": 0, "sites": set(), "vals": [], "odd": Counter()})
        years = Counter()
        for r in R:
            d = it[g(r, "itemname")]
            d["n"] += 1
            if abbr_key: d["abbr"][g(r, abbr_key)] += 1
            d["unit"][g(r, "itemunit")] += 1
            if site_key: d["sites"].add(g(r, site_key))
            v = g(r, "itemvalue"); x = num(v)
            if x is None: d["odd"][v] += 1
            else: d["vals"].append(x)
            m = re.match(r"(\d{4})", g(r, "sampledate"))
            if m: years[m.group(1)] += 1
        if years:
            say("\n## Records by sampling year\n")
            say(" · ".join(f"{y}: {n}" for y, n in sorted(years.items())))
        say("\n## Monitoring items\n")
        say("| item | abbreviation | unit | records | sites | not a plain number (examples) | min | median | max |\n|---|---|---|---|---|---|---|---|---|")
        for name, d in sorted(it.items(), key=lambda kv: -kv[1]["n"]):
            v = d["vals"]
            odd = ", ".join(f"{k!r}×{n}" for k, n in d["odd"].most_common(3))
            st = (f"{min(v):g} | {statistics.median(v):g} | {max(v):g}") if v else "– | – | –"
            say(f"| {name} | {'/'.join(k for k in d['abbr'] if k)} | {'/'.join(k for k in d['unit'] if k)} | {d['n']} | {len(d['sites'])} | {odd} | {st} |")

        def coverage(rows):
            have = defaultdict(set)
            for r in rows:
                if not measured(g(r, "itemvalue")): continue      # '-' or empty means not measured
                for lab in which_need(g(r, "itemname"), g(r, abbr_key) if abbr_key else ""):
                    have[lab].add(g(r, site_key) if site_key else "")
            return have
        allc = coverage(R)
        zr = [r for r in R if a.zone in g(r, "ugwdistname")] if "ugwdistname" in fields else []
        zc = coverage(zr)
        nz = len({g(r, site_key) for r in zr}) if site_key else 0
        say(f"\n## Items CHemTrace needs: number of sites with at least one measurement (a number or below detection; '-' does not count) (all / districts containing '{a.zone}', {nz} sites)\n")
        yrs = defaultdict(set)
        for r in zr:
            if not measured(g(r, "itemvalue")): continue
            m = re.match(r"(\d{4})", g(r, "sampledate"))
            if m:
                for lab in which_need(g(r, "itemname"), g(r, abbr_key) if abbr_key else ""): yrs[lab].add(m.group(1))
        say(f"| item | all sites | {a.zone} | years measured in {a.zone} |\n|---|---|---|---|")
        for lab, _, _ in NEED:
            y = sorted(yrs.get(lab, ()))
            say(f"| {lab} | {len(allc.get(lab, ()))} | {len(zc.get(lab, ()))} | {f'{y[0]}–{y[-1]} ({len(y)} yrs)' if y else '–'} |")
        say("\nMatching is by item name and abbreviation; check the item table above for anything missed or matched wrongly.")

    out = f.parent / "inspect.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nWritten: {out}")


if __name__ == "__main__":
    main()
