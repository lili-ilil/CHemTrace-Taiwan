#!/usr/bin/env python3
"""Download datasets from the Water Resources Agency open data API (opendata.wra.gov.tw).

Usage (from the CHemTrace-TW folder):
    python tools/fetch_wra.py well_condition                 # 地下水水位觀測井井況
    python tools/fetch_wra.py level_stats                    # 地下水水位年度統計
    python tools/fetch_wra.py <dataset-uuid> --name <short-name>
    python tools/fetch_wra.py well_condition --sample 50     # first 50 records only

Dataset paths as shown in the API documentation (https://opendata.wra.gov.tw/openapi/swagger/index.html,
read 2026-11-15): GET /api/v2/<uuid> with query parameters page (1..N, default 1) and size (records per page,
at most 1000). No API key is listed in the documentation.

Output in data/raw/wra/<name>/<UTC timestamp>/: page_00001.json ... (responses as received), records.json, meta.json.
If the server address differs from --base, open the dataset in the documentation, press "Try it out" and
"Execute", and copy the start of the "Request URL" into --base.
Licence: Open Government Data License, version 1.0 (https://data.gov.tw/license); credit 經濟部水利署 and the
dataset name when publishing results. Uses the Python standard library only.
"""
import argparse, json, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWN = {
    "well_condition": ("3e86faea-e94a-4a91-a870-852d73e83c3d", "地下水水位觀測井井況 (data.gov.tw 32718)"),
    "level_stats": ("f3ae2889-ccaf-45a3-a546-0edd8d9fd2da", "地下水水位年度統計 (data.gov.tw 32717)"),
}
UA = "CHemTrace-TW data download (research; ETH Zurich)"
try:
    sys.stdout.reconfigure(errors="replace"); sys.stderr.reconfigure(errors="replace")
except Exception:
    pass


def get(url, retries, timeout):
    wait = 5
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                print(f"  HTTP {e.code}, retry in {wait} s", flush=True); time.sleep(wait); wait *= 2; continue
            raise RuntimeError(f"HTTP {e.code} for {url}: {body}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < retries:
                print(f"  {e}, retry in {wait} s", flush=True); time.sleep(wait); wait *= 2; continue
            raise RuntimeError(f"network error for {url}: {e}") from None


def records_of(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("records", "Records", "data", "Data", "result", "items", "value"):
            v = obj.get(k)
            if isinstance(v, list):
                return v
            if isinstance(v, dict):
                r = records_of(v)
                if r is not None:
                    return r
    return None


def main():
    ap = argparse.ArgumentParser(description="Download WRA open data (opendata.wra.gov.tw) as JSON.")
    ap.add_argument("dataset", help="well_condition, level_stats, or a dataset uuid from the API documentation")
    ap.add_argument("--name", help="folder name for a uuid (default: the uuid)")
    ap.add_argument("--base", default="https://opendata.wra.gov.tw", help="server address (default https://opendata.wra.gov.tw)")
    ap.add_argument("--size", type=int, default=1000, help="records per page, at most 1000")
    ap.add_argument("--sample", type=int, default=0, help="download only the first N records")
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--max-pages", type=int, default=2000)
    a = ap.parse_args()
    uuid, label = KNOWN.get(a.dataset, (a.dataset, a.name or a.dataset))
    name = a.dataset if a.dataset in KNOWN else (a.name or a.dataset)
    size = min(a.size, a.sample) if a.sample else min(a.size, 1000)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "data" / "raw" / "wra" / name / stamp
    n = 2
    while out.exists():                             # two runs within the same second get separate folders
        out = ROOT / "data" / "raw" / "wra" / name / f"{stamp}_{n}"; n += 1
    out.mkdir(parents=True)
    print(f"{label}: writing to {out}", flush=True)
    allrec, page, prev = [], 1, None
    try:
        while page <= a.max_pages:
            url = f"{a.base.rstrip('/')}/api/v2/{urllib.parse.quote(uuid)}?" + urllib.parse.urlencode({"page": page, "size": size})
            body = get(url, a.retries, a.timeout)
            (out / f"page_{page:05d}.json").write_bytes(body)
            try:
                obj = json.loads(body.decode("utf-8-sig"))
            except ValueError:
                raise RuntimeError(f"page {page}: response is not JSON; first bytes: {body[:200]!r}")
            recs = records_of(obj)
            if recs is None:
                raise RuntimeError(f"page {page}: no record list found; top-level keys: {list(obj)[:20] if isinstance(obj, dict) else type(obj)}")
            if recs and recs == prev:
                raise RuntimeError(f"page {page} repeats the previous page: 'page' seems to be ignored; stopped")
            prev = recs[:]
            allrec.extend(recs)
            print(f"  page {page}: {len(recs)} records (total so far {len(allrec)})", flush=True)
            if len(recs) < size or not recs or (a.sample and len(allrec) >= a.sample):
                break
            page += 1; time.sleep(a.pause)
    except RuntimeError as e:
        sys.exit(f"FAILED: {e}")
    if a.sample:
        allrec = allrec[:a.sample]
    (out / "records.json").write_text(json.dumps(allrec, ensure_ascii=False, indent=1), encoding="utf-8")
    meta = {"dataset": label, "uuid": uuid, "base": a.base, "downloaded_utc": stamp, "size": size, "pages": page,
            "records": len(allrec), "sample": a.sample or None, "complete": not a.sample,
            "fields": sorted({k for r in allrec if isinstance(r, dict) for k in r}),
            "licence": "Open Government Data License, version 1.0 (https://data.gov.tw/license)",
            "attribution": f"經濟部水利署, {label}, opendata.wra.gov.tw, Open Government Data License, version 1.0"}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{label}: {len(allrec)} records in {page} page(s)" + (" (sample)" if a.sample else ""))


if __name__ == "__main__":
    main()
