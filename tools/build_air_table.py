#!/usr/bin/env python3
"""Air-quality station table for the site auto-fill: data/grid/air.json (copied to site/data/ by step_wells.py).

Usage (from the CHemTrace-TW folder, after tools/fetch_air_all.py):  python tools/build_air_table.py
Inputs: newest full downloads of MOENV AQX_P_07 (stations: name, type, TWD97 longitude and latitude) and AQX_P_08
(monthly values, PM10 and PM2.5) in data/raw/moenv/.
Rules (as for the Chianan preset, tools/process_chianan_extra.py):
  - one value per station and month (the download repeats some months; repeats with different values are reported)
  - annual mean = mean of the 12 monthly values; only the years 2023-2025 with all 12 months are used
  - station value = mean of its complete years; "x" and empty values are skipped (that month is then missing)
  - traffic stations (交通站) are kept in the table but marked, and the site does not use them for background air
"""
import json, statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "moenv"
OUT = ROOT / "data" / "grid" / "air.json"
YEARS = ("2023", "2024", "2025")


def newest_full(dataid, item=None):
    best = None
    for d in sorted((RAW / dataid).glob("*")):
        m = d / "meta.json"
        if not m.exists() or not (d / "records.json").exists(): continue
        q = json.loads(m.read_text(encoding="utf-8")).get("query", {})
        if int(q.get("limit", 0)) < 1000: continue
        if item and q.get("filters") != f"itemengname,EQ,{item}": continue
        best = d
    if not best: raise SystemExit(f"no full download of {dataid} {item or ''}: run tools/fetch_air_all.py")
    return json.loads((best / "records.json").read_text(encoding="utf-8")), best.name


def main():
    st, run7 = newest_full("AQX_P_07")
    vals, runs, conflicts = {}, {}, 0
    for item in ("PM10", "PM2.5"):
        recs, runs[item] = newest_full("AQX_P_08", item)
        mon = {}
        for r in recs:
            try: v = float(r["concentration"])
            except ValueError: continue
            k = (r["siteid"], r["monitormonth"])
            if k in mon and mon[k] != v: conflicts += 1
            mon.setdefault(k, v)
        by = defaultdict(lambda: defaultdict(dict))
        for (sid, m), v in mon.items():
            if m[:4] in YEARS: by[sid][m[:4]][m] = v
        vals[item] = {}
        for sid, ys in by.items():
            full = {y: statistics.mean(d.values()) for y, d in ys.items() if len(d) == 12}
            if full: vals[item][sid] = (round(statistics.mean(full.values()), 1), sorted(full))
    rows = []
    for s in st:
        sid = s["siteid"]
        p10, p25 = vals["PM10"].get(sid), vals["PM2.5"].get(sid)
        rows.append([sid, s["sitename"], s["county"], s["sitetype"], float(s["twd97lat"]), float(s["twd97lon"]),
                     p10[0] if p10 else None, p25[0] if p25 else None, "/".join(p10[1]) if p10 else ""])
    doc = {"generated": date.today().isoformat(), "rule": "mean of the complete years among 2023-2025 (12 monthly values each)",
           "fields": ["siteid", "name", "county", "type", "lat", "lon", "PM10 µg/m³", "PM2.5 µg/m³", "complete years (PM10)"],
           "source": f"MOENV AQX_P_07 ({run7}) and AQX_P_08 ({runs['PM10']}, {runs['PM2.5']}), Open Government Data License 1.0",
           "stations": rows}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = sum(1 for r in rows if r[6] is not None)
    print(f"{OUT}: {len(rows)} stations, {n} with PM10 for complete years; {conflicts} repeated months with different values")


if __name__ == "__main__":
    main()
