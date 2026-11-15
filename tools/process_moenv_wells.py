#!/usr/bin/env python3
"""Clean the MOENV regional groundwater quality data and build per-sample and per-well tables for one district.

Usage (from the CHemTrace-TW folder):
    python tools/process_moenv_wells.py                       # newest complete downloads, all districts
    python tools/process_moenv_wells.py --zone 嘉南平原        # one groundwater district
    python tools/process_moenv_wells.py --quality <folder or records.json> --wells <folder or records.json>

Inputs (from tools/fetch_moenv.py):
    WQX_P_02  regional groundwater quality monitoring data (long table: one row per site, date and item)
    WQX_P_07  basic information on regional groundwater quality monitoring wells

Outputs in data/processed/ (<zone> = district name, or 'all'):
    moenv_samples_<zone>.csv   one row per well and sampling time; for each key item a value column and a qualifier
                               column (_q): '<' = below the detection limit (value = detection limit)
    moenv_wells_<zone>.csv     one row per well: location, status, sampling period, and per key item the number of
                               samples, number below detection, median and maximum
    moenv_long_clean.csv       every item after cleaning (all districts), for later use
    moenv_summary_<zone>.md    cleaning log with counts, units, coverage and a first look at arsenic

Cleaning rules (each one is counted in the summary):
 1. Dates come in three forms: 'YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD' and 'YYYYMMDD'. All are converted to ISO.
 2. Records that repeat the same well, date, time and item are dropped when their values are the same after rule 3
    ('' / 'None' / '-' all mean "not measured"). In the 2026-11-15 download this removes the 'YYYYMMDD' copies of
    2016-2017 samples (they repeat the 'YYYY-MM-DD' records) and an exact second copy of the 2025 records.
    Conflicting repeats are kept once (first seen) and listed in the summary.
 3. Values: HTML entities are decoded ('&lt;' -> '<'); '', '-', 'None' = not measured; a number = measured;
    '<x' = below the detection limit x; 'ND' = below an unknown detection limit.
 4. Redox potential (氧化還原電位, mV): -999 and -555 are treated as missing-value codes (2026-11-15 download: -999 six
    times, -555 five times, all in 2020 and all in samples where no other item was measured). Values written '<x' are
    read as -x (negative).
    Evidence in the 2026-11-15 download: '<x' occurs only in 2016-2019, when no negative numbers occur, and from 2020 on
    negative numbers occur and '<x' does not; samples with '<x' have the chemistry of reducing water (high Fe and NH3-N,
    low NO3-N), like the samples with negative numbers. This is an inference from the data, not a documented rule.
 5. Total alkalinity and total hardness are labelled 'mg/L' from 2020 and 'mg/L as CaCO3' before; the values are on the
    same scale (medians 233.5 and 234 mg/L for alkalinity, 264 and 272 mg/L for hardness, 2026-11-15 download), so both are taken as mg/L as CaCO3.
Medians with values below detection: if at least half of the samples are below detection, the median is reported as
'<' + the highest detection limit; otherwise the median of the measured values with the censored ones ranked lowest.
Uses the Python standard library only. Licence of the data: Open Government Data License, version 1.0
(https://data.gov.tw/license); credit the Ministry of Environment and the dataset names when publishing results.
"""
import argparse, csv, html, json, re, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "moenv"
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# key items: short code, item name in the data, unit after cleaning
KEY = [("As", "砷", "mg/L"), ("Fe", "鐵", "mg/L"), ("Mn", "錳", "mg/L"), ("DO", "溶氧(電極法)", "mg/L"),
       ("ORP", "氧化還原電位", "mV"), ("NO3N", "硝酸鹽氮", "mg/L as N"), ("NH3N", "氨氮", "mg/L as N"),
       ("SO4", "硫酸鹽", "mg/L"), ("TOC", "總有機碳", "mg/L"), ("pH", "酸鹼值", ""), ("WT", "水溫", "°C"),
       ("EC", "導電度", "µmho/cm at 25 °C"), ("Alk", "總鹼度", "mg/L as CaCO3"), ("Ca", "鈣", "mg/L"),
       ("Mg", "鎂", "mg/L"), ("Na", "鈉", "mg/L"), ("K", "鉀", "mg/L"), ("Cl", "氯鹽", "mg/L"),
       ("TH", "總硬度", "mg/L as CaCO3"), ("TDS", "總溶解固體物", "mg/L"), ("GWT", "水面至井口深度", "m"),
       ("Hg", "汞", "mg/L"), ("Pb", "鉛", "mg/L"), ("Cd", "鎘", "mg/L"), ("Cr", "鉻", "mg/L"),
       ("Cu", "銅", "mg/L"), ("Ni", "鎳", "mg/L"), ("Zn", "鋅", "mg/L")]
CODE = {zh: c for c, zh, _ in KEY}
NUM = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
MISSING = {"", "-", "None", "none", "NULL", "null"}


def newest(dataid):
    """Newest download folder of a DataID that is complete (meta.json says complete) or not a sample."""
    best = None
    for d in sorted((RAW / dataid).glob("*/")):
        m = d / "meta.json"
        if not m.is_file():
            continue
        meta = json.loads(m.read_text(encoding="utf-8"))
        if meta.get("sample"):
            continue
        best = d
    if not best:
        sys.exit(f"No complete download of {dataid} in {RAW / dataid}. Run tools/fetch_moenv.py {dataid} first.")
    return best


def load(p):
    p = Path(p)
    f = p / "records.json" if p.is_dir() else p
    data = json.loads(f.read_text(encoding="utf-8-sig"))
    return f, [r for r in (data.get("records", []) if isinstance(data, dict) else data) if isinstance(r, dict)]


def s(r, k):
    v = r.get(k)
    return "" if v is None else str(v).strip()


def iso(d):
    """Return (YYYY-MM-DD, HH:MM:SS or '') or None."""
    d = d.strip()
    m = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?$", d)
    if not m:
        return None
    y, mo, da, hh, mi, ss = m.groups()
    return f"{y}-{mo}-{da}", (f"{hh}:{mi}:{ss or '00'}" if hh else "")


def parse(item, raw, log):
    """Return (value, qualifier, status). qualifier '<' = below detection limit (value = limit, None if unknown)."""
    v = html.unescape(raw).strip()
    if v != raw.strip():
        log["html entity decoded"] += 1
    if v in MISSING:
        return None, "", "not measured"
    if item == "氧化還原電位":
        if v in ("-999", "-999.0", "-555", "-555.0"):
            log["ORP -999 or -555 treated as missing"] += 1
            return None, "", "missing code"
        if v.startswith("<") and NUM.match(v[1:].strip()):
            log["ORP '<x' read as -x"] += 1
            return -float(v[1:]), "", "measured"
    if NUM.match(v):
        return float(v), "", "measured"
    if v.startswith("<") and NUM.match(v[1:].strip()):
        return float(v[1:]), "<", "below detection"
    if v.upper() in ("ND", "N.D."):
        return None, "<", "below detection"
    log[f"unreadable value in {item}: {v!r}"] += 1
    return None, "", "unreadable"


def median_cens(vals):
    """vals: list of (value, qualifier). Returns (median as text, max measured or None, n, n_censored)."""
    n = len(vals)
    cens = [v for v, q in vals if q == "<"]
    det = sorted(v for v, q in vals if q != "<" and v is not None)
    mx = max(det) if det else None
    if n == 0:
        return "", None, 0, 0
    if 2 * len(cens) >= n:
        lim = max((v for v in cens if v is not None), default=None)
        return (f"<{lim:g}" if lim is not None else "<DL"), mx, n, len(cens)
    ranked = [float("-inf")] * len(cens) + det           # censored values rank lowest
    k = len(ranked)
    med = ranked[k // 2] if k % 2 else (ranked[k // 2 - 1] + ranked[k // 2]) / 2
    return f"{med:.6g}", mx, n, len(cens)


def main():
    ap = argparse.ArgumentParser(description="Clean MOENV groundwater quality data and build well tables.")
    ap.add_argument("--quality", help="folder or records.json of WQX_P_02 (default: newest complete download)")
    ap.add_argument("--wells", help="folder or records.json of WQX_P_07 (default: newest complete download)")
    ap.add_argument("--zone", default="all", help="groundwater district (ugwdistname, e.g. 嘉南平原), or 'all' (default)")
    ap.add_argument("--out", default=str(ROOT / "data" / "processed"))
    a = ap.parse_args()
    qf, Q = load(a.quality or newest("WQX_P_02"))
    wf, Wl = load(a.wells or newest("WQX_P_07"))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tag = "all" if a.zone == "all" else a.zone
    log = Counter(); conflicts = []; units = defaultdict(Counter)

    # ---- rules 1-3: dates, values, duplicates
    seen = {}
    clean = []                                            # (siteid, date, time, item, value, qualifier)
    for r in Q:
        t = iso(s(r, "sampledate"))
        if not t:
            log["unreadable date (record dropped)"] += 1; continue
        if len(s(r, "sampledate")) == 8:
            log["date written YYYYMMDD"] += 1
        item = s(r, "itemname")
        units[item][s(r, "itemunit")] += 1
        val, q, status = parse(item, s(r, "itemvalue"), log)
        key = (s(r, "siteid"), t[0], t[1], item)
        if key in seen:
            if seen[key] == (val, q):
                log["repeated record dropped (same value)"] += 1
            else:
                log["repeated record with a different value (first kept)"] += 1
                if len(conflicts) < 30: conflicts.append((key, seen[key], (val, q)))
            continue
        seen[key] = (val, q)
        log[f"value: {status}"] += 1
        clean.append((key[0], t[0], t[1], item, val, q, r))
    log["records read"] = len(Q); log["records kept"] = len(clean)

    # ---- well information: wells file first, quality records as fallback for names and coordinates
    W = {s(w, "siteid"): w for w in Wl}
    names = defaultdict(Counter); coords = defaultdict(Counter); dist = {}
    for sid, d, tm, item, val, q, r in clean:
        names[sid][s(r, "sitename")] += 1
        if s(r, "twd97tm2x") and s(r, "twd97tm2y"):
            coords[sid][(s(r, "twd97tm2x"), s(r, "twd97tm2y"), s(r, "twd97lon"), s(r, "twd97lat"))] += 1
        dist[sid] = s(r, "ugwdistname")
        W.setdefault(sid, {"siteid": sid, "county": s(r, "county"), "township": s(r, "township"), "ugwdistname": s(r, "ugwdistname")})

    def info(sid):
        w = W.get(sid, {})
        x, y, lon, lat = s(w, "twd97tm2x"), s(w, "twd97tm2y"), s(w, "twd97lon"), s(w, "twd97lat")
        src = "wells file"
        if not (x and y) and coords.get(sid):
            x, y, lon, lat = coords[sid].most_common(1)[0][0]; src = "quality records"
        if not (x and y):
            src = "none"
        nm = names[sid].most_common(1)[0][0] if names.get(sid) else s(w, "sitename")
        return {"siteid": sid, "sitename": nm, "other_names": "; ".join(n for n in names.get(sid, {}) if n != nm),
                "county": s(w, "county"), "township": s(w, "township"), "ugwdistname": s(w, "ugwdistname") or dist.get(sid, ""),
                "twd97tm2x": x, "twd97tm2y": y, "twd97lon": lon, "twd97lat": lat, "coord_source": src,
                "statusofuse": s(w, "statusofuse"), "siteaddress": s(w, "siteaddress")}

    INFO = {sid: info(sid) for sid in set(W) | set(names)}
    info = INFO.__getitem__                                # computed once per well
    inzone = lambda sid: a.zone == "all" or INFO[sid]["ugwdistname"] == a.zone

    # ---- long clean table (all districts)
    with open(out / "moenv_long_clean.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(["siteid", "ugwdistname", "date", "time", "item", "code", "value", "qualifier"])
        for sid, d, tm, item, val, q, r in clean:
            if val is None and q == "": continue
            wr.writerow([sid, dist.get(sid, ""), d, tm, item, CODE.get(item, ""), "" if val is None else f"{val:g}", q])

    # ---- samples (wide)
    samp = defaultdict(dict)
    for sid, d, tm, item, val, q, r in clean:
        if item in CODE and inzone(sid) and not (val is None and q == ""):
            samp[(sid, d, tm)][CODE[item]] = (val, q)
    cols = [c for c, _, _ in KEY]
    head = ["siteid", "sitename", "ugwdistname", "twd97tm2x", "twd97tm2y", "date", "time"]
    with open(out / f"moenv_samples_{tag}.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(head + [h for c in cols for h in (c, c + "_q")])
        for (sid, d, tm) in sorted(samp):
            I = info(sid); row = [sid, I["sitename"], I["ugwdistname"], I["twd97tm2x"], I["twd97tm2y"], d, tm]
            for c in cols:
                v = samp[(sid, d, tm)].get(c)
                row += ["" if not v or v[0] is None else f"{v[0]:g}", v[1] if v else ""]
            wr.writerow(row)

    # ---- wells
    per = defaultdict(lambda: defaultdict(list)); dates = defaultdict(list)
    for (sid, d, tm), v in samp.items():
        dates[sid].append(d)
        for c, vq in v.items(): per[sid][c].append(vq)
    wells = sorted(per)
    stats = {}
    with open(out / f"moenv_wells_{tag}.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        base = ["siteid", "sitename", "other_names", "county", "township", "ugwdistname", "twd97tm2x", "twd97tm2y",
                "twd97lon", "twd97lat", "coord_source", "statusofuse", "siteaddress", "n_samples", "first_date", "last_date"]
        wr.writerow(base + [h for c in cols for h in (c + "_n", c + "_ncens", c + "_median", c + "_max")])
        for sid in wells:
            I = info(sid); ds = sorted(dates[sid])
            row = [I[k] for k in base[:13]] + [len(set(ds)), ds[0], ds[-1]]
            for c in cols:
                med, mx, n, nc = median_cens(per[sid].get(c, []))
                stats[(sid, c)] = (med, mx, n, nc)
                row += [n, nc, med, "" if mx is None else f"{mx:g}"]
            wr.writerow(row)

    # ---- summary
    L = []; say = L.append
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    say(f"# MOENV regional groundwater quality: cleaning and well summary ({tag})\n")
    say(f"Made {stamp} by tools/process_moenv_wells.py from `{qf.relative_to(ROOT) if ROOT in qf.parents else qf}` "
        f"and `{wf.relative_to(ROOT) if ROOT in wf.parents else wf}`.\n")
    say("Data: Ministry of Environment (Taiwan), Regional groundwater quality monitoring data (WQX_P_02) and Basic "
        "information on regional groundwater quality monitoring wells (WQX_P_07), data.moenv.gov.tw, Open Government "
        "Data License, version 1.0, https://data.gov.tw/license\n")
    say("## Cleaning log\n\n| step | records |\n|---|---|")
    for k in ["records read", "date written YYYYMMDD", "repeated record dropped (same value)",
              "repeated record with a different value (first kept)", "records kept", "value: measured",
              "value: below detection", "value: not measured", "value: missing code", "value: unreadable",
              "html entity decoded", "ORP '<x' read as -x", "ORP -999 or -555 treated as missing", "unreadable date (record dropped)"]:
        if log.get(k): say(f"| {k} | {log[k]} |")
    for k, n in sorted(log.items()):
        if k.startswith("unreadable value"): say(f"| {k} | {n} |")
    if conflicts:
        say("\nRepeated records with different values (first 30):\n")
        for key, a1, a2 in conflicts: say(f"- {key}: kept {a1}, dropped {a2}")
    say("\n## Units in the raw data (key items)\n\n| code | item | units as written (records) | unit used |\n|---|---|---|---|")
    for c, zh, u in KEY:
        say(f"| {c} | {zh} | {', '.join(f'{k!r} ({n})' for k, n in units[zh].most_common())} | {u} |")
    zs = [sid for sid in wells]
    yrs = Counter(d[:4] for (sid, d, tm) in samp)
    say(f"\n## Wells and samples in {tag}\n")
    say(f"- Wells with at least one key item measured: {len(zs)}")
    say(f"- Wells in the wells file for this district: {sum(1 for w in Wl if a.zone == 'all' or s(w, 'ugwdistname') == a.zone)}")
    say(f"- Wells without coordinates: {sum(1 for sid in zs if info(sid)['coord_source'] == 'none')}; "
        f"coordinates taken from the quality records: {sum(1 for sid in zs if info(sid)['coord_source'] == 'quality records')}")
    say(f"- Status of use: {dict(Counter(info(sid)['statusofuse'] or '(not in wells file)' for sid in zs))}")
    say(f"- Samples (well and sampling time): {len(samp)}; by year: " + " · ".join(f"{y}: {n}" for y, n in sorted(yrs.items())))
    say("\n## Coverage of key items\n\n| code | wells | samples | below detection | median of well medians* |\n|---|---|---|---|---|")
    for c, zh, u in KEY:
        n_w = sum(1 for sid in zs if stats[(sid, c)][2] > 0)
        n_s = sum(stats[(sid, c)][2] for sid in zs); n_c = sum(stats[(sid, c)][3] for sid in zs)
        meds = [float(stats[(sid, c)][0]) for sid in zs if stats[(sid, c)][2] and not stats[(sid, c)][0].startswith("<")]
        say(f"| {c} | {n_w} | {n_s} | {n_c} | {statistics.median(meds):.3g} {u} |" if meds else f"| {c} | {n_w} | {n_s} | {n_c} | – |")
    say("\n*Only wells whose median is a measured value; wells with a median below detection are left out of this column.")
    asw = [(sid, stats[(sid, 'As')]) for sid in zs if stats[(sid, 'As')][2] > 0]
    def above(t):
        return sum(1 for sid, (med, mx, n, nc) in asw if not med.startswith("<") and float(med) > t)
    def anyabove(t):
        return sum(1 for sid, (med, mx, n, nc) in asw if mx is not None and mx > t)
    say(f"\n## Arsenic: first look ({len(asw)} wells)\n")
    say("| threshold (mg/L) | meaning | wells with median above | wells with at least one sample above |\n|---|---|---|---|")
    for t, m in [(0.01, "drinking water standard (飲用水水質標準)"),
                 (0.025, "groundwater monitoring standard, class 1 (地下水污染監測標準)"),
                 (0.05, "groundwater control standard, class 1 (地下水污染管制標準)"),
                 (0.25, "groundwater monitoring standard, class 2"), (0.5, "groundwater control standard, class 2")]:
        say(f"| {t} | {m} | {above(t)} | {anyabove(t)} |")
    say("\nStandards: see 05_第一階段_資料可行性與試點計畫.md, section 1.3, for sources. Medians and maxima are per well "
        "over all samples; they say nothing yet about depth, because the MOENV data have no well depth.")
    orp = sorted((v[0], sid, d) for (sid, d, tm), x in samp.items() for c, v in x.items() if c == "ORP" and v[0] is not None)
    if orp:
        say("\n## Redox potential: extreme values to check by hand\n")
        say("Lowest: " + ", ".join(f"{v:g} mV ({sid}, {d})" for v, sid, d in orp[:8]))
        say("\nHighest: " + ", ".join(f"{v:g} mV ({sid}, {d})" for v, sid, d in orp[-8:]))
    (out / f"moenv_summary_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nWritten to {out}: moenv_samples_{tag}.csv, moenv_wells_{tag}.csv, moenv_long_clean.csv, moenv_summary_{tag}.md")


if __name__ == "__main__":
    main()
