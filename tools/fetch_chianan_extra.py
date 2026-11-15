#!/usr/bin/env python3
"""Download the MOENV data needed for the Chianan preset (river and reservoir water quality, monthly air quality).

Usage (from the CHemTrace-TW folder, with your key in .secret/moenv_api_key.txt as for fetch_moenv.py):
    python tools/fetch_chianan_extra.py            # test the filters, then download
    python tools/fetch_chianan_extra.py --test     # only the 50-record tests

It calls tools/fetch_moenv.py once per filter value, with the API parameter filters=<field>,EQ,<value>
(MOENV API v2). Before each full download it fetches 50 records and checks that every record has the requested
value; if the API ignored the filter, it stops instead of downloading the whole country.
The key is handled only by fetch_moenv.py and is never printed.

DataIDs (checked on data.moenv.gov.tw/dataset/detail/<DataID>, 15 Nov 2026):
    WQX_P_01 河川水質監測資料, WQX_P_03 水庫水質監測資料, AQX_P_08 空氣品質監測月值
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "moenv"
JOBS = [
    ("WQX_P_01", "county", ["嘉義縣", "嘉義市", "臺南市"]),
    ("WQX_P_03", "county", ["嘉義縣", "嘉義市", "臺南市"]),
    ("AQX_P_08", "sitename", ["朴子", "新港", "嘉義", "新營"]),
]


def newest(dataid):
    runs = sorted((OUT / dataid).glob("*/records.json"), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None


def run(dataid, field, value, sample):
    cmd = [sys.executable, str(ROOT / "tools" / "fetch_moenv.py"), dataid, "--param", f"filters={field},EQ,{value}"]
    if sample:
        cmd += ["--sample", str(sample)]
    print(">>", dataid, field, "=", value, "(test)" if sample else "(full)", flush=True)
    r = subprocess.run(cmd)
    if r.returncode:
        sys.exit(f"fetch_moenv.py stopped with code {r.returncode}")
    p = newest(dataid)
    recs = json.loads(p.read_text(encoding="utf-8")) if p else []
    return recs, p


def main():
    test_only = "--test" in sys.argv
    for dataid, field, values in JOBS:
        for v in values:
            recs, p = run(dataid, field, v, 50)
            got = {str(r.get(field, "")) for r in recs}
            if not recs:
                print(f"   no records for {field} = {v}; check the spelling on the dataset page. Skipped.")
                continue
            if got != {v}:
                sys.exit(f"   the filter was ignored ({field} values {sorted(got)[:5]}). Stopped; tell Claude.")
            print(f"   filter works: {len(recs)} test records, all {field} = {v}")
            if not test_only:
                recs, p = run(dataid, field, v, 0)
                print(f"   saved {len(recs)} records in {p.parent}")


if __name__ == "__main__":
    main()
