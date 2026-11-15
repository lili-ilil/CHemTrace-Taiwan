#!/usr/bin/env python3
"""Water Resources Agency groundwater data: observation wells, water quality by aquifer layer, water level statistics.

Usage (from the CHemTrace-TW folder):
    python tools/process_wra.py

Inputs:
    data/raw/wra/well_condition/<newest complete>/records.json   地下水水位觀測井井況 (tools/fetch_wra.py)
    data/raw/wra/level_stats/<newest complete>/records.json      地下水水位年度統計 (tools/fetch_wra.py)
    data/raw/wra/161086.csv                                      水利署地下水水質歷史資料 (data.gov.tw 161086, CSV)
    data/processed/moenv_wells_all.csv (optional)                for the nearest WRA station to each MOENV well

Outputs in data/processed/:
    wra_wells.csv              one row per observation well: station, layer code, confined/unconfined, depths, TWD97
                               coordinates and zone, checks
    wra_quality_clean.csv      one row per water-quality record, joined with its well (depth, layer, district)
    wra_level_wells.csv        per well: years with an annual mean water level, mean of the annual means
    moenv_wells_nearest_wra.csv  each MOENV well with the nearest WRA station and that station's wells by layer
    wra_summary.md             counts, cleaning log, arsenic by district and aquifer layer, measured redox classes

Cleaning rules (counted in the summary):
 - -999999 and -999998 are missing-value codes. Other negative concentrations are treated as missing (no rule in the
   data description says what they mean). pH outside 0-14 is treated as missing.
 - Water-quality records dated YYYY-01-01T00:00:00 are taken as annual records with the year only (the dataset is
   described as annual water-quality statistics); several records can share one well and date, and they are kept
   as separate records because their values differ.
 - 'asotestitems' (aso) is not defined in the data description. Its values (median 0.02 mg/L) fit arsenic in mg/L;
   this script calls it As_aso and the summary tests whether it rises with depth as Chen & Liu (2007) report for
   arsenic. Confirm the meaning with the provider before publishing.
 - Exact zeros are common for trace elements (2,045 of 5,925 aso records in the 2026-11-15 download). They probably
   stand for "below the detection limit" (limit not given); they are kept as 0, which ranks them lowest, and a median
   of 0 is reported as '0 (below detection?)'.
 - EC appears in two scales for some samples (e.g. 46960 and 46.96 for one well and year); EC is not used here.
 - Coordinates: 'locationbytwd97' is 'x y'. Wells in 金門地區 and 連江/馬祖 use the TWD97 TM2 zone at 119°E
   (EPSG:3825; the x values are near 180,000 m); all others zone 121°E (EPSG:3826).
 - County name vs. address: wells whose address does not start with their county name are flagged.
Measured redox class: McMahon & Chapelle (2008) thresholds with the Fe/sulfide mass ratio of Jurgens et al. (2009)
Table 1 (>10 Fe(III), 0.3-10 Fe(III)-SO4, <0.3 SO4). The WRA data have no dissolved oxygen, so oxic and anoxic cannot
be separated where Fe and Mn are low, and every class is 'with O2 unknown' (Jurgens et al. 2009, Table 2, lower half).
Uses the Python standard library only. Data licence: Open Government Data License, version 1.0
(https://data.gov.tw/license); credit 經濟部水利署 and the dataset names when publishing results.
"""
import csv, glob, json, math, re, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "wra"
OUT = ROOT / "data" / "processed"
MISSING_CODES = {-999999.0, -999998.0}
Q = {"As_aso": "asotestitems", "Fe": "fetestitems", "Mn": "mntestitems", "SO4": "so4testitems", "sulfide": "sulfidetestitems",
     "NO3N": "no3_ntestitems", "NO2N": "no2_ntestitems", "NH3N": "nh3_ntestitems", "TOC": "toctestitems", "pH": "phtestitems",
     "Eh": "ehtestitems", "ORP_oxreelevel": "oxreeleveltestitems", "Cl": "cltestitems", "HCO3": "hco3testitems",
     "Alk": "alktestitems", "Ca": "catestitems", "Mg": "mgtestitems", "Na": "natestitems", "K": "ktestitems",
     "temp": "temptestitems", "TDS": "tdstestitems", "Hg": "hgtestitems", "Pb": "pbtestitems", "Cd": "cdtestitems",
     "Cr": "crtestitems", "Cu": "cutestitems", "Zn": "zntestitems"}
SIGNED = {"Eh", "ORP_oxreelevel", "temp"}            # may be negative
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def newest(name):
    best = None
    for d in sorted((RAW / name).glob("*/")):
        m = d / "meta.json"
        if m.is_file() and not json.loads(m.read_text(encoding="utf-8")).get("sample"):
            best = d
    if not best:
        sys.exit(f"No complete download in {RAW / name}; run tools/fetch_wra.py {name}")
    return best


def f(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if x in MISSING_CODES else x


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    wdir, ldir = newest("well_condition"), newest("level_stats")
    W = json.loads((wdir / "records.json").read_text(encoding="utf-8"))
    LV = json.loads((ldir / "records.json").read_text(encoding="utf-8"))
    qpath = RAW / "161086.csv"
    with open(qpath, encoding="utf-8-sig", newline="") as fh:
        QR = list(csv.DictReader(fh))
    log = Counter()

    # ---- wells
    wells = {}
    for w in W:
        wid = (w.get("wellidentifier") or "").upper()
        xy = (w.get("locationbytwd97") or "").split()
        x, y = (f(xy[0]), f(xy[1])) if len(xy) == 2 else (None, None)
        zone = w.get("groundwaterzone", "")
        epsg = "3825" if re.search(r"金門|連江|馬祖", zone + w.get("locationaddress", "")[:3]) else "3826"
        addr, county = w.get("locationaddress", ""), w.get("countyname", "")
        mism = bool(county and addr and not addr.startswith(county.replace("台", "臺")) and not addr.startswith(county))
        if mism: log["wells: county name and address disagree"] += 1
        station = re.sub(r"\s*\(\d+\)\s*$", "", w.get("wellname", "")).strip()
        wells[wid] = {"wellidentifier": wid, "wellname": w.get("wellname", ""), "station": station, "wellnumber": w.get("wellnumber", ""),
                      "groundwaterzone": zone, "layercode": w.get("groundwaterlayercode", ""), "layerattribute": w.get("layerattribute", ""),
                      "welldepth_m": w.get("welldepth", ""), "finishdepth_m": w.get("finishdepth", ""), "groundheight_m": w.get("groundheight", ""),
                      "x": "" if x is None else f"{x:.2f}", "y": "" if y is None else f"{y:.2f}", "epsg": epsg,
                      "establishdate": w.get("establishdate", ""), "disusedate": "" if w.get("disusedate") in ("99999999", "") else w.get("disusedate"),
                      "countyname": county, "townname": w.get("townname", ""), "address": addr,
                      "county_address_mismatch": "yes" if mism else "", "remarks": w.get("remarks", "")}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "wra_wells.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(next(iter(wells.values())))); wr.writeheader()
        for k in sorted(wells): wr.writerow(wells[k])

    # ---- water quality
    rows = []; unmatched = Counter()
    for r in QR:
        wid = (r.get("wellidentifier") or "").upper()
        t = r.get("samplingtime", "")
        prec = "year" if t.endswith("-01-01T00:00:00") else "day"
        rec = {"wellidentifier": wid, "date": t[:10], "date_precision": prec, "year": t[:4]}
        for k, col in Q.items():
            raw = r.get(col, "")
            try:
                if float(raw) in MISSING_CODES: log[f"{k}: missing code"] += 1
            except (TypeError, ValueError):
                pass
            x = f(raw)
            if x is not None and x < 0 and k not in SIGNED:
                log[f"{k}: negative value treated as missing"] += 1; x = None
            if k == "pH" and x is not None and not (0 <= x <= 14):
                log["pH outside 0-14 treated as missing"] += 1; x = None
            rec[k] = "" if x is None else f"{x:g}"
        w = wells.get(wid)
        if not w: unmatched[wid] += 1
        for k in ("station", "groundwaterzone", "layercode", "layerattribute", "welldepth_m", "x", "y", "epsg"):
            rec[k] = w[k] if w else ""
        rows.append(rec)
    log["quality records"] = len(QR); log["quality records whose well is not in the well list"] = sum(unmatched.values())

    # measured redox class without O2 (Jurgens et al. 2009 Table 2, lower half; Fe/sulfide ratio from Table 1)
    def cls(r):
        g = lambda k: float(r[k]) if r[k] != "" else None
        N, M, F, S, H = g("NO3N"), g("Mn"), g("Fe"), g("SO4"), g("sulfide")
        if None in (N, M, F, S):
            return "incomplete"
        n, m, fe, s = N >= 0.5, M >= 0.05, F >= 0.1, S >= 0.5
        if fe:
            if s:
                if H is not None and H > 0:
                    ratio = F / H
                    proc = "Fe(III)" if ratio > 10 else ("Fe(III)-SO4" if ratio >= 0.3 else "SO4")
                else:
                    proc = "Fe(III)/SO4 (no sulfide)"
            else:
                proc = "CH4gen"
            return ("NO3 and " if n else "") + proc + ", O2 unknown"
        if m:
            return ("NO3 and " if n else "") + "Mn(IV), O2 unknown"
        return "O2 or NO3 (O2 unknown)" if n else "O2 or suboxic (O2 unknown)"
    for r in rows: r["redox_class"] = cls(r)
    cols = list(rows[0])
    with open(OUT / "wra_quality_clean.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader(); wr.writerows(rows)

    # ---- water level statistics
    lv = defaultdict(list)
    for r in LV:
        x = f(r.get("annualaveragewaterlevel"))
        if x is not None: lv[(r.get("wellidentifier") or "").upper()].append((r.get("year"), x))
    with open(OUT / "wra_level_wells.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh); wr.writerow(["wellidentifier", "station", "groundwaterzone", "layercode", "years", "first_year", "last_year", "mean_of_annual_means_m"])
        for wid, v in sorted(lv.items()):
            w = wells.get(wid, {})
            ys = sorted(y for y, _ in v)
            wr.writerow([wid, w.get("station", ""), w.get("groundwaterzone", ""), w.get("layercode", ""), len(v), ys[0], ys[-1], f"{statistics.mean(x for _, x in v):.3f}"])

    # ---- nearest WRA station to each MOENV well (zone 121 only)
    near = False; mw = OUT / "moenv_wells_all.csv"
    if mw.is_file():
        st = defaultdict(list)
        for w in wells.values():
            if w["x"] and w["epsg"] == "3826": st[w["station"] + "|" + w["groundwaterzone"]].append(w)
        cen = {k: (statistics.mean(float(w["x"]) for w in v), statistics.mean(float(w["y"]) for w in v)) for k, v in st.items()}
        with open(mw, encoding="utf-8-sig", newline="") as fh:
            M = list(csv.DictReader(fh))
        with open(OUT / "moenv_wells_nearest_wra.csv", "w", newline="", encoding="utf-8-sig") as fh:
            wr = csv.writer(fh); wr.writerow(["siteid", "sitename", "ugwdistname", "wra_station", "wra_zone", "distance_m", "wra_wells (layer:depth m)"])
            for m in M:
                x, y = f(m.get("twd97tm2x")), f(m.get("twd97tm2y"))
                if x is None or y is None or m["ugwdistname"] in ("金門", "連江", "澎湖地區"): continue
                k, d = min(((k, math.hypot(c[0] - x, c[1] - y)) for k, c in cen.items()), key=lambda t: t[1])
                ws = sorted(st[k], key=lambda w: f(w["welldepth_m"]) or 0)
                wr.writerow([m["siteid"], m["sitename"], m["ugwdistname"], k.split("|")[0], k.split("|")[1], f"{d:.0f}",
                             "; ".join(f"{w['layercode']}:{w['welldepth_m']}" for w in ws)])
        near = True

    # ---- summary
    L = []; say = L.append
    say(f"# WRA groundwater data: wells, water quality by layer, levels\n\nMade {stamp} by tools/process_wra.py.\n")
    say("Data: 經濟部水利署, 地下水水位觀測井井況 (data.gov.tw 32718), 地下水水位年度統計 (32717), 水利署地下水水質歷史資料 "
        "(161086); Open Government Data License, version 1.0, https://data.gov.tw/license\n")
    say(f"## Wells\n\n- Observation wells: {len(wells)}; stations (well name without '(n)'): {len({w['station'] + w['groundwaterzone'] for w in wells.values()})}; disused: {sum(1 for w in wells.values() if w['disusedate'])}")
    say(f"- Layer codes: {dict(Counter(w['layercode'] for w in wells.values()).most_common())}")
    say(f"- Confined (C) / unconfined (U): {dict(Counter(w['layerattribute'] for w in wells.values()).most_common())}")
    say(f"- County name and address disagree: {log['wells: county name and address disagree']} wells (flagged in wra_wells.csv)")
    say("\n## Cleaning log (water quality)\n\n| step | count |\n|---|---|")
    for k, v in sorted(log.items()):
        if not k.startswith("wells:") and v: say(f"| {k} | {v} |")
    say(f"\nRecords dated YYYY-01-01 (year only): {sum(1 for r in rows if r['date_precision'] == 'year')} of {len(rows)}; years {min(r['year'] for r in rows)}–{max(r['year'] for r in rows)}")

    def wellmed(sel, k):
        per = defaultdict(list)
        for r in rows:
            if sel(r) and r[k] != "": per[r["wellidentifier"]].append(float(r[k]))
        return {w: statistics.median(v) for w, v in per.items()}, sum(len(v) for v in per.values())
    say("\n## Arsenic (aso) by district and aquifer layer\n")
    say("Median over wells of each well's median; share of records above 0.01, 0.05 and 0.1 mg/L. aso is taken to be arsenic in mg/L (unconfirmed).\n")
    say("| district | layer | wells | records | median of well medians | >0.01 | >0.05 | >0.1 |\n|---|---|---|---|---|---|---|---|")
    for z in ("嘉南平原", "濁水溪沖積扇", "屏東平原", "蘭陽平原"):
        for lc in ("1", "2", "3", "4"):
            sel = lambda r, z=z, lc=lc: r["groundwaterzone"] == z and r["layercode"] == lc
            med, n = wellmed(sel, "As_aso")
            vals = [float(r["As_aso"]) for r in rows if sel(r) and r["As_aso"] != ""]
            if not vals: continue
            share = lambda t: f"{sum(1 for v in vals if v > t) / len(vals):.0%}"
            mm = statistics.median(med.values())
            say(f"| {z} | {lc} | {len(med)} | {n} | {'0 (below detection?)' if mm == 0 else f'{mm:.3g}'} | {share(0.01)} | {share(0.05)} | {share(0.1)} |")
    say("\n## Measured redox class (O2 unknown) in 嘉南平原 by layer\n")
    for lc in ("1", "2", "3", "4"):
        c = Counter(r["redox_class"] for r in rows if r["groundwaterzone"] == "嘉南平原" and r["layercode"] == lc)
        n = sum(c.values())
        if n: say(f"- Layer {lc} ({n} records): " + ", ".join(f"{k} {v / n:.0%}" for k, v in c.most_common(6)))
    if near:
        with open(OUT / "moenv_wells_nearest_wra.csv", encoding="utf-8-sig", newline="") as fh:
            N_ = list(csv.DictReader(fh))
        g = defaultdict(list)
        for r in N_: g[r["ugwdistname"]].append(float(r["distance_m"]) / 1000)
        say("\n## Nearest WRA station to each MOENV well\n\n| MOENV district | wells | median distance (km) |\n|---|---|---|")
        for z, d in sorted(g.items(), key=lambda kv: -len(kv[1])):
            say(f"| {z} | {len(d)} | {statistics.median(d):.1f} |")
    (OUT / "wra_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
