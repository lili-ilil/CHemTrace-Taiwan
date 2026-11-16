#!/usr/bin/env python3
"""Download nationwide MOENV air-quality data for the site auto-fill (nearest station PM10 and PM2.5).

Usage (from the CHemTrace-TW folder, with your key in .secret/moenv_api_key.txt as for fetch_moenv.py):
    python tools/fetch_air_all.py            # test the filters, then download
    python tools/fetch_air_all.py --test     # only the 50-record tests

Datasets (checked on data.moenv.gov.tw/dataset/detail/<DataID>, 16 Nov 2026):
    AQX_P_07 空氣品質監測站基本資料: station name, county, TWD97Lon, TWD97Lat, SiteType, SiteId (all stations, small)
    AQX_P_08 空氣品質監測月值: monthly values; only PM10 and PM2.5 are downloaded (filter itemengname,EQ,<item>)
The key is handled only by fetch_moenv.py and is never printed. Each filter is first tested with 50 records; if the
API ignores the filter the script stops instead of downloading every pollutant.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "moenv"


def newest(dataid):
    runs = sorted((OUT / dataid).glob("*/records.json"), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None


def fetch(dataid, extra, sample):
    cmd = [sys.executable, str(ROOT / "tools" / "fetch_moenv.py"), dataid] + extra
    if sample:
        cmd += ["--sample", str(sample)]
    print(">>", dataid, " ".join(extra), "(test)" if sample else "(full)", flush=True)
    if subprocess.run(cmd).returncode:
        sys.exit("fetch_moenv.py stopped; see the message above")
    p = newest(dataid)
    return (json.loads(p.read_text(encoding="utf-8")) if p else []), p


def main():
    test_only = "--test" in sys.argv
    recs, p = fetch("AQX_P_07", [], 50)
    print(f"   stations test: {len(recs)} records; fields {sorted(recs[0].keys()) if recs else '-'}")
    if not test_only:
        recs, p = fetch("AQX_P_07", [], 0)
        print(f"   saved {len(recs)} stations in {p.parent}")
    for item in ("PM10", "PM2.5"):
        recs, p = fetch("AQX_P_08", ["--param", f"filters=itemengname,EQ,{item}"], 50)
        got = {r.get("itemengname") for r in recs}
        if not recs:
            sys.exit(f"   no records for itemengname = {item}; tell Claude")
        if got != {item}:
            sys.exit(f"   the filter was ignored (items {sorted(got)[:5]}). Stopped; tell Claude.")
        print(f"   filter works: {len(recs)} test records, all {item}")
        if not test_only:
            recs, p = fetch("AQX_P_08", ["--param", f"filters=itemengname,EQ,{item}"], 0)
            print(f"   saved {len(recs)} records in {p.parent}")


if __name__ == "__main__":
    main()
