#!/usr/bin/env python3
"""Compact well table for the site auto-fill: data/grid/wells.json (copied to site/data/ by step_wells.py).

Usage (from the CHemTrace-TW folder):  python tools/build_well_table.py
Inputs (made by tools/process_moenv_wells.py and tools/process_wra.py):
  data/processed/moenv_wells_all.csv   MOENV regional groundwater monitoring (WQX_P_02, WQX_P_07), per-well medians 2014-2025
  data/processed/moenv_long_clean.csv  every MOENV value with its qualifier ('<' = below detection; value = detection limit)
  data/processed/wra_quality_clean.csv WRA groundwater quality (data.gov.tw 161086) with the redox class of each sample
  data/processed/wra_wells.csv         WRA observation wells (data.gov.tw 32718): layer, coordinates, ground height
Rules
  MOENV wells give pH, chloride, EC, depth to water (GWT, "水面至井口深度", measured from the well top) and the metal
  backgrounds. A metal counts as below detection when more than half of the samples are below the limit; then the
  background is 0 and the most common detection limit is kept for the note. Metals in µg/L.
  WRA layer-1 wells give the redox class: the most common class among samples with a complete analysis
  ("incomplete" samples are skipped), the median chloride and the ground height of the well (data.gov.tw 32718). WRA metal values are not used (below-detection
  values are stored as 0 without a limit).
"""
import csv, json, statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
OUT = ROOT / "data" / "grid" / "wells.json"
METALS = ["As", "Hg", "Pb", "Cd", "Cr", "Ni"]


def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def main():
    dl = defaultdict(Counter)
    for r in csv.DictReader(open(P / "moenv_long_clean.csv", encoding="utf-8-sig")):
        if r["code"] in METALS and r["qualifier"] == "<":
            dl[(r["siteid"], r["code"])][r["value"]] += 1
    moenv = []
    for w in csv.DictReader(open(P / "moenv_wells_all.csv", encoding="utf-8-sig")):
        x, y = num(w["twd97tm2x"]), num(w["twd97tm2y"])
        if x is None or y is None: continue
        met = {}
        for m in METALS:
            n, nc = int(num(w[f"{m}_n"]) or 0), int(num(w[f"{m}_ncens"]) or 0)
            if n == 0: continue
            d = dl.get((w["siteid"], m))
            dlv = round(float(d.most_common(1)[0][0]) * 1000, 4) if d else None
            if nc > n / 2: met[m] = [0, n, nc, dlv]
            else:
                med = num(w[f"{m}_median"])
                if med is not None: met[m] = [round(med * 1000, 3), n, nc, dlv]
        moenv.append([w["siteid"], w["sitename"], round(x), round(y), w["ugwdistname"], int(num(w["n_samples"]) or 0),
                      w["first_date"][:4], w["last_date"][:4], num(w["pH_median"]), num(w["Cl_median"]), num(w["EC_median"]),
                      num(w["GWT_median"]), met])
    wells = {r["wellidentifier"].upper(): r for r in csv.DictReader(open(P / "wra_wells.csv", encoding="utf-8-sig"))}
    cls, cl, yrs = defaultdict(Counter), defaultdict(list), defaultdict(set)
    for r in csv.DictReader(open(P / "wra_quality_clean.csv", encoding="utf-8-sig")):
        if r["layercode"] != "1": continue
        k = r["wellidentifier"].upper()
        if r["redox_class"] and r["redox_class"] != "incomplete": cls[k][r["redox_class"]] += 1
        c = num(r["Cl"])
        if c is not None and c > 0: cl[k].append(c)
        if r["year"]: yrs[k].add(r["year"])
    wra = []
    for k in sorted(set(cls) | set(cl)):
        w = wells.get(k)
        if not w: continue
        x, y = num(w["x"]), num(w["y"])
        if x is None or y is None: continue
        top = cls[k].most_common(1)[0] if cls[k] else None
        ys = sorted(yrs[k])
        wra.append([k, w["station"], round(x), round(y), w["groundwaterzone"], sum(cls[k].values()),
                    top[0] if top else None, round(top[1] / sum(cls[k].values()), 2) if top else None,
                    round(statistics.median(cl[k]), 1) if cl[k] else None, len(cl[k]), ys[0] if ys else "", ys[-1] if ys else "", num(w["groundheight_m"])])
    doc = {"generated": date.today().isoformat(), "units": "metals µg/L, Cl mg/L, EC µS/cm, GWT m",
           "moenv_fields": ["siteid", "name", "E", "N", "zone", "samples", "first", "last", "pH", "Cl", "EC", "GWT", "metals {m: [median, n, n below DL, DL]}"],
           "wra_fields": ["wellid", "station", "E", "N", "zone", "complete samples", "redox class", "share", "Cl median", "Cl n", "first", "last", "ground height m"],
           "sources": {"moenv": "MOENV regional groundwater monitoring (WQX_P_02, WQX_P_07), Open Government Data License 1.0",
                       "wra": "WRA groundwater quality (data.gov.tw 161086) and observation wells (32718), Open Government Data License 1.0"},
           "moenv": moenv, "wra": wra}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT}: {len(moenv)} MOENV wells, {len(wra)} WRA layer-1 wells, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
