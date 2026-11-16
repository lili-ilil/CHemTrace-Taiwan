#!/usr/bin/env python3
"""Rainfall normals for the site auto-fill: data/grid/rain.json (copied to site/data/ by step_wells.py).

Usage (from the CHemTrace-TW folder):  python tools/build_rain_table.py
Inputs: data/raw/C-B0027-001.json (CWA 月平均-地面測站資料, 1991-2020 monthly normals of 27 staffed stations) and
data/raw/cwa/stations_codis.csv (coordinates and altitude from CODiS, see data/raw/cwa/README.md).
Annual rainfall = sum of the 12 monthly "Accumulation" normals (mm).
"""
import csv, json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "grid" / "rain.json"


def main():
    d = json.loads((ROOT / "data" / "raw" / "C-B0027-001.json").read_text(encoding="utf-8-sig"))
    loc = d["cwaopendata"]["resources"]["resource"]["data"]["surfaceObs"]["location"]
    st = {r["stationID"]: r for r in csv.DictReader(open(ROOT / "data" / "raw" / "cwa" / "stations_codis.csv", encoding="utf-8"))}
    rows = []
    for l in loc:
        sid = l["station"]["StationID"]; P = l["stationObsStatistics"].get("Precipitation")
        s = st.get(sid)
        if not P or not s: continue
        rows.append([sid, l["station"]["StationName"], float(s["lat_wgs84"]), float(s["lon_wgs84"]), float(s["altitude_m"]),
                     round(sum(float(m["Accumulation"]) for m in P["monthly"]), 1), f'{P["StationStartYear"]}–{P["StationEndYear"]}'])
    doc = {"generated": date.today().isoformat(), "fields": ["stationID", "name", "lat", "lon", "altitude m", "annual rainfall mm", "period"],
           "source": "CWA C-B0027-001 (1991–2020 monthly normals, sum of the 12 months); coordinates from CODiS station list (16 Nov 2026)",
           "stations": rows}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT}: {len(rows)} stations")


if __name__ == "__main__":
    main()
