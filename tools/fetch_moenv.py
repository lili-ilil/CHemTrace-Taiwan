#!/usr/bin/env python3
"""Download datasets from the Ministry of Environment open data API (data.moenv.gov.tw).

Usage (from the CHemTrace-TW folder):
    python tools/fetch_moenv.py <DataID> [<DataID> ...] [options]

Examples:
    python tools/fetch_moenv.py XXXX_P_01 --sample 1000      # first 1000 records only, to check fields and items
    python tools/fetch_moenv.py XXXX_P_01                    # whole dataset, page by page
    python tools/fetch_moenv.py XXXX_P_01 --param year_month=2024_06

API (https://data.moenv.gov.tw/paradigm):
    https://data.moenv.gov.tw/api/v2/{DataID}?format=json&offset=..&limit=..&api_key=..
Limits (https://data.moenv.gov.tw/api-term): 300 calls per API per day without a key, 5,000 with a member key.

The API key is read from .secret/moenv_api_key.txt (or the MOENV_API_KEY environment variable).
It is never printed or written to any output file.

Output, per DataID, in data/raw/moenv/<DataID>/<UTC timestamp>/:
    page_00000.json ...  every API response exactly as received
    records.json         all records joined into one list
    meta.json            DataID, download time, query (without the key), record count, attribution text

Licence: Open Government Data License, version 1.0 (https://data.gov.tw/license). Any reuse must credit
the providing agency and year, the dataset name and version, and the licence (section 3.2 and Exhibit).
Uses the Python standard library only.
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = os.environ.get("MOENV_API_BASE", "https://data.moenv.gov.tw/api/v2/")   # override only for offline tests
ROOT = Path(__file__).resolve().parent.parent
KEY_FILES = [ROOT / ".secret" / "moenv_api_key.txt", ROOT / ".secrets" / "moenv_api_key.txt"]
UA = "CHemTrace-TW data download (research; contact via ETH Zurich)"

try:
    sys.stdout.reconfigure(errors="replace"); sys.stderr.reconfigure(errors="replace")
except Exception:
    pass


def read_key():
    k = os.environ.get("MOENV_API_KEY", "").strip()
    if k:
        return k
    for p in KEY_FILES:
        if p.is_file():
            k = p.read_text(encoding="utf-8-sig").strip()
            if k:
                return k
    return ""


def redact(text, key):
    return text.replace(key, "***") if key else text


def get(url, key, retries, timeout):
    """GET with retries. Returns (status, bytes). Error messages never contain the key."""
    wait = 5
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                print(f"  HTTP {e.code}, retry in {wait} s", flush=True); time.sleep(wait); wait *= 2; continue
            raise RuntimeError(redact(f"HTTP {e.code}: {body}", key)) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < retries:
                print(f"  {redact(str(e), key)}, retry in {wait} s", flush=True); time.sleep(wait); wait *= 2; continue
            raise RuntimeError(redact(f"network error: {e}", key)) from None


def records_of(obj):
    """The API's JSON layout is not documented on the platform pages: accept a list, or a dict with 'records'."""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("records", "Records", "data", "result"):
            v = obj.get(k)
            if isinstance(v, list):
                return v
            if isinstance(v, dict) and isinstance(v.get("records"), list):
                return v["records"]
    return None


def fetch(dataid, key, a):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.out) / dataid / stamp
    n = 2
    while out.exists():                             # two runs within the same second get separate folders
        out = Path(a.out) / dataid / f"{stamp}_{n}"; n += 1
    out.mkdir(parents=True)
    extra = dict(p.split("=", 1) for p in a.param)
    limit = min(a.limit, a.sample) if a.sample else a.limit
    offset, page, calls, allrec, total, prev_first = a.offset, 0, 0, [], None, None
    print(f"{dataid}: writing to {out}", flush=True)
    while True:
        q = {"format": "json", "offset": offset, "limit": limit, **extra}
        url = API + urllib.parse.quote(dataid) + "?" + urllib.parse.urlencode(q)
        status, body = get(url + "&api_key=" + urllib.parse.quote(key), key, a.retries, a.timeout)
        calls += 1
        (out / f"page_{page:05d}.json").write_bytes(body)
        try:
            obj = json.loads(body.decode("utf-8-sig"))
        except ValueError:
            raise RuntimeError(f"page {page}: response is not JSON; first bytes: {body[:200]!r}")
        recs = records_of(obj)
        if recs is None:
            raise RuntimeError(f"page {page}: no record list found; top-level keys: {list(obj)[:20] if isinstance(obj, dict) else type(obj)}")
        if total is None and isinstance(obj, dict) and obj.get("total") not in (None, ""):
            try: total = int(obj["total"])
            except (TypeError, ValueError): pass
        if page > 0 and recs and recs == prev_first:
            raise RuntimeError(f"page {page} repeats the previous page: the API seems to ignore 'offset'; stopped to avoid a loop")
        prev_first = recs[:]
        allrec.extend(recs)
        print(f"  page {page}: {len(recs)} records (total so far {a.offset + len(allrec)}{f' of {total}' if total else ''})", flush=True)
        page += 1; offset += len(recs)
        if not recs: break
        if total:                                   # the server may return fewer than 'limit' per page: trust the total
            if a.offset + len(allrec) >= total: break
        elif len(recs) < limit: break
        if a.sample and len(allrec) >= a.sample: break
        if a.max_pages and page >= a.max_pages: print("  stopped: --max-pages reached"); break
        if calls >= a.max_calls: print(f"  stopped: {a.max_calls} calls (--max-calls); tomorrow, continue with --offset {offset}"); break
        time.sleep(a.pause)
    if a.sample: allrec = allrec[:a.sample]
    (out / "records.json").write_text(json.dumps(allrec, ensure_ascii=False, indent=1), encoding="utf-8")
    meta = {"dataid": dataid, "downloaded_utc": stamp, "api": API + dataid, "query": {"format": "json", "limit": limit, **extra},
            "start_offset": a.offset, "next_offset": a.offset + len(allrec),
            "pages": page, "calls": calls, "records": len(allrec), "total_reported": total,
            "complete": a.offset == 0 and (total is None or len(allrec) >= total) and not a.sample,
            "sample": a.sample or None,
            "fields": sorted({k for r in allrec if isinstance(r, dict) for k in r}),
            "licence": "Open Government Data License, version 1.0 (https://data.gov.tw/license)",
            "attribution": "Ministry of Environment (Taiwan), <dataset name>, <version/year>, data.moenv.gov.tw, "
                           "Open Government Data License, version 1.0, https://data.gov.tw/license"}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{dataid}: {len(allrec)} records in {page} page(s), {calls} call(s)" + (" (sample)" if a.sample else ""), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Download MOENV open data (data.moenv.gov.tw) as JSON.")
    ap.add_argument("dataid", nargs="+", help="DataID, e.g. the code in https://data.moenv.gov.tw/dataset/detail/<DataID>")
    ap.add_argument("--sample", type=int, default=0, help="download only the first N records")
    ap.add_argument("--limit", type=int, default=1000, help="records per call (default 1000)")
    ap.add_argument("--param", action="append", default=[], help="extra query parameter key=value, e.g. year_month=2024_06")
    ap.add_argument("--offset", type=int, default=0, help="start at this record (to continue a download stopped by --max-calls)")
    ap.add_argument("--max-pages", type=int, default=0, help="stop after this many pages (0 = no limit)")
    ap.add_argument("--max-calls", type=int, default=4500, help="stop after this many calls per DataID (member limit is 5,000 per API per day)")
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between calls (default 1)")
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--out", default=str(ROOT / "data" / "raw" / "moenv"))
    a = ap.parse_args()
    bad = [p for p in a.param if "=" not in p or p.split("=", 1)[0] in ("api_key", "offset", "limit", "format")]
    if bad: ap.error(f"--param must be key=value and must not set api_key, offset, limit or format: {bad}")
    key = read_key()
    if not key:
        sys.exit("No API key: put it in .secret/moenv_api_key.txt or set MOENV_API_KEY.")
    ok = True
    for d in a.dataid:
        try:
            fetch(d, key, a)
        except RuntimeError as e:
            ok = False; print(f"{d}: FAILED: {redact(str(e), key)}", file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
