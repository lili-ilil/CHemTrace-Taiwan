#!/usr/bin/env python3
"""Hydrogeological boreholes and lithology logs (GSMMA), and the nearest borehole to each MOENV monitoring well.

Usage (from the CHemTrace-TW folder):
    python tools/process_gsmma.py

Inputs in data/raw/gsmma/ (downloaded by hand from data.gov.tw, CSV, UTF-8):
    16799.csv   水文地質鑽探資料庫: borehole basic data (well no., name, county, township, TWD97 TM2 X/Y, well depth,
                top elevation, year built (ROC year), address, groundwater district, river basin)
    162478.csv  平原區鑽井資料: well no., name, TWD97 TM2 X/Y, depth, year (AD); 13 wells from 2022 are only here
    61131.csv   平原區水文地質鑽探-鑽孔岩心紀錄: one row per depth interval (top, bottom, lithology code). The columns
                岩類代碼說明 / 岩類簡稱 / 岩類說明 hold the code legend in their first rows; they do not describe the row.
Optional: data/processed/moenv_wells_all.csv (from tools/process_moenv_wells.py) for the nearest-borehole table.

Outputs in data/processed/:
    gsmma_boreholes.csv           one row per borehole (both lists joined; 16799 values first)
    gsmma_lithology.csv           one row per interval: code, legend name, main constituent, class
    gsmma_borehole_profiles.csv   per borehole and depth window, the share of logged thickness in each class
    moenv_wells_nearest_borehole.csv  each MOENV well with its nearest borehole, distance and that borehole's profile
    gsmma_summary.md              counts, classification checks, coverage by district

Classification of an interval by its main constituent. In the code the main constituent is the last grain token
(e.g. MvfS = 泥質極細砂, muddy very fine sand -> sand; vfSM = 極細砂質泥, very-fine-sandy mud -> mud), which matches the
Chinese name, where the main constituent comes last. Tokens: C clay, M mud, Z silt (class 'fine'); S sand with size
prefix vf/f/m/c/vc ('sand'); G gravel with size prefix ('gravel'). Rock codes from the legend ('rock'), peat and drift
wood ('organic'), fill ('fill'), L = 資料空缺 ('missing'). Codes not in the legend are parsed the same way when they are
grain codes; upper-case variants of legend rock codes (BR, Br, Bs, Ls, Tf) are read as those rocks; the rest
are 'unclassified'. The summary lists every such code with its count.
Uses the Python standard library only. Data licence: Open Government Data License, version 1.0
(https://data.gov.tw/license); credit 經濟部地質調查及礦業管理中心 and the dataset names when publishing results.
"""
import csv, math, re, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "gsmma"
OUT = ROOT / "data" / "processed"
WINDOWS = [(0, 20), (20, 50), (50, 100), (100, 200), (200, 300)]
CLASSES = ["fine", "sand", "gravel", "rock", "organic", "fill", "missing", "unclassified"]
ROCK = {"agl", "and", "br", "bs", "cgl", "ds", "gns", "ls", "mbl", "ms", "MS54", "sch", "sh", "sls", "slt", "spt",
        "ss", "ss/ms", "ss/sh", "SS-SH", "tf", "qtz"}
CASE_VARIANTS = {"BR": "br", "Br": "br", "Bs": "bs", "Ls": "ls", "Tf": "tf"}
TOKEN = re.compile(r"(vf|vc|f|m|c)?([SG])|([MCZ])")
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def rows(name):
    p = RAW / name
    if not p.is_file():
        sys.exit(f"Missing {p}. Download it from data.gov.tw (see tools/README.md).")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(fh)]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_grain(code):
    """Main constituent of a grain-size code, or None if the code is not made only of grain tokens."""
    pos, toks = 0, []
    while pos < len(code):
        m = TOKEN.match(code, pos)
        if not m:
            return None
        toks.append(m.group(0)); pos = m.end()
    if not toks:
        return None
    last = toks[-1]
    if last in ("C", "M", "Z"):
        return {"C": "clay", "M": "mud", "Z": "silt"}[last], "fine"
    size = {"vf": "very fine", "f": "fine", "m": "medium", "c": "coarse", "vc": "very coarse"}.get(last[:-1], "size not given")
    return (f"{size} sand" if last.endswith("S") else f"{size} gravel"), ("sand" if last.endswith("S") else "gravel")


def classify(code, legend):
    """Return (main constituent, class, note)."""
    c = CASE_VARIANTS.get(code, code)
    if c == "L":
        return "data gap (資料空缺)", "missing", ""
    if c in ROCK:
        return legend.get(c, (c,))[0], "rock", "case variant of a legend code" if c != code else ""
    if c in ("pt", "dwd"):
        return legend[c][0], "organic", ""
    if c == "tsh":
        return legend[c][0], "fill", ""
    g = parse_grain(c)
    if g:
        return g[0], g[1], "" if c in legend else "parsed, not in legend"
    return code, "unclassified", "not in legend" if c not in legend else "legend code not classified"


def legend_class(name):
    """Class implied by the Chinese legend name (for checking the code parser): the main constituent comes last
    ('粉砂質細砂'), or first in the form 'X含Y' (X containing Y)."""
    if "含" in name:
        name = name.split("含")[0]
    if re.search(r"(粘土|黏土|泥|粉砂)$", name) and not name.endswith("岩"):
        return "fine"
    if name.endswith("砂"):
        return "sand"
    if name.endswith("礫"):
        return "gravel"
    return None


def main():
    A, B, C = rows("16799.csv"), rows("162478.csv"), rows("61131.csv")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = []; say = L.append

    # ---- legend (side table in the first rows of 61131)
    legend = {r["岩類代碼說明"]: (r["岩類簡稱"], r["岩類說明"]) for r in C if r.get("岩類簡稱") not in ("", "-", None)}

    # ---- boreholes
    bh = {}
    for r in A:
        y = fnum(r.get("建置年分"))
        bh[r["井號"]] = {"well_no": r["井號"], "name": r["井名"], "county": r.get("縣市", ""), "township": r.get("鄉鎮", ""),
                         "x": r.get("TWD97二度分帶X", ""), "y": r.get("TWD97二度分帶Y", ""), "depth_m": r.get("井深", ""),
                         "top_elev_m": r.get("井頂高程", ""), "year_built": str(int(y) + 1911) if y else "",
                         "address": r.get("井址", ""), "district": r.get("地下水分區", ""), "basin": r.get("流域", ""),
                         "source": "16799"}
    for r in B:
        if r["井號"] in bh:
            bh[r["井號"]]["source"] += "+162478"; continue
        bh[r["井號"]] = {"well_no": r["井號"], "name": r["井名"], "county": "", "township": "", "x": r.get("TWD97二度分帶X", ""),
                         "y": r.get("TWD97二度分帶Y", ""), "depth_m": r.get("深度", ""), "top_elev_m": "", "year_built": r.get("年份", ""),
                         "address": "", "district": "", "basin": "", "source": "162478"}

    # ---- lithology intervals
    iv = []; notes = Counter(); unk = Counter(); bad = 0
    for r in C:
        top, bot = fnum(r.get("深度上限")), fnum(r.get("深度下限"))
        if top is None or bot is None or bot < top:
            bad += 1; continue
        code = r.get("岩性代碼", "")
        main_, cls, note = classify(code, legend)
        if note:
            notes[(code, note, cls)] += 1
        iv.append({"well_no": r["井號"], "well_name": r.get("井名", ""), "top_m": top, "bottom_m": bot, "code": code,
                   "legend_name": legend.get(CASE_VARIANTS.get(code, code), ("",))[0], "main": main_, "class": cls, "note": note})
    by = defaultdict(list)
    for x in iv:
        by[x["well_no"]].append(x)
    for w in by.values():
        w.sort(key=lambda x: (x["top_m"], x["bottom_m"]))

    # parser check against legend names
    check = Counter(); mism = []
    for code, (name, _) in legend.items():
        g = parse_grain(code); lc = legend_class(name)
        if g and lc:
            ok = g[1] == lc; check["agree" if ok else "disagree"] += 1
            if not ok: mism.append((code, name, g[1], lc))

    # ---- profiles per borehole
    prof = {}
    for wn, ivs in by.items():
        p = {"logged_m": sum(x["bottom_m"] - x["top_m"] for x in ivs), "max_depth_m": max(x["bottom_m"] for x in ivs)}
        gaps = sum(max(0, b["top_m"] - a["bottom_m"]) for a, b in zip(ivs, ivs[1:]))
        p["gap_m"] = gaps
        for lo, hi in WINDOWS + [(0, 1e9)]:
            tot = Counter()
            for x in ivs:
                t = max(0.0, min(hi, x["bottom_m"]) - max(lo, x["top_m"]))
                if t > 0: tot[x["class"]] += t
            s = sum(tot.values())
            key = f"{lo}-{int(hi)}m" if hi < 1e9 else "all"
            p[key] = {c: (tot[c] / s if s else None) for c in CLASSES}
            p[key + "_m"] = s
        prof[wn] = p

    # ---- write tables
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "gsmma_boreholes.csv", "w", newline="", encoding="utf-8-sig") as fh:
        cols = ["well_no", "name", "county", "township", "district", "basin", "x", "y", "depth_m", "top_elev_m",
                "year_built", "address", "source", "has_log", "log_max_depth_m"]
        wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader()
        for k in sorted(bh):
            d = dict(bh[k]); d["has_log"] = "yes" if k in prof else "no"
            d["log_max_depth_m"] = f"{prof[k]['max_depth_m']:g}" if k in prof else ""
            wr.writerow(d)
    with open(OUT / "gsmma_lithology.csv", "w", newline="", encoding="utf-8-sig") as fh:
        cols = ["well_no", "well_name", "top_m", "bottom_m", "code", "legend_name", "main", "class", "note"]
        wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader()
        for k in sorted(by):
            for x in by[k]:
                wr.writerow({**x, "top_m": f"{x['top_m']:g}", "bottom_m": f"{x['bottom_m']:g}"})
    wkeys = [f"{lo}-{hi}m" for lo, hi in WINDOWS] + ["all"]
    with open(OUT / "gsmma_borehole_profiles.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(["well_no", "name", "district", "logged_m", "max_depth_m", "gap_m"] +
                    [f"{w}_{c}" for w in wkeys for c in ["logged_m"] + CLASSES])
        for k in sorted(prof):
            p = prof[k]; b = bh.get(k, {})
            row = [k, b.get("name", ""), b.get("district", ""), f"{p['logged_m']:g}", f"{p['max_depth_m']:g}", f"{p['gap_m']:g}"]
            for w in wkeys:
                row.append(f"{p[w + '_m']:g}")
                row += ["" if p[w][c] is None else f"{p[w][c]:.3f}" for c in CLASSES]
            wr.writerow(row)

    # ---- nearest borehole to each MOENV well
    near_ok = False
    mw = OUT / "moenv_wells_all.csv"
    if mw.is_file():
        with open(mw, encoding="utf-8-sig", newline="") as fh:
            M = list(csv.DictReader(fh))
        pts = [(k, float(b["x"]), float(b["y"])) for k, b in bh.items() if fnum(b["x"]) and fnum(b["y"])]
        with open(OUT / "moenv_wells_nearest_borehole.csv", "w", newline="", encoding="utf-8-sig") as fh:
            wr = csv.writer(fh)
            wr.writerow(["siteid", "sitename", "ugwdistname", "borehole", "borehole_name", "borehole_district", "distance_m",
                         "same_district", "borehole_depth_m", "has_log"] +
                        [f"{w}_{c}" for w in wkeys[:4] for c in ("fine", "sand", "gravel")])
            dists = defaultdict(list)
            for m in M:
                x, y = fnum(m.get("twd97tm2x")), fnum(m.get("twd97tm2y"))
                if x is None or y is None:
                    continue
                k, d = min(((k, math.hypot(px - x, py - y)) for k, px, py in pts), key=lambda t: t[1])
                b = bh[k]; p = prof.get(k)
                same = "yes" if b["district"] and b["district"] == m["ugwdistname"] else ("unknown" if not b["district"] else "no")
                dists[m["ugwdistname"]].append(d)
                row = [m["siteid"], m["sitename"], m["ugwdistname"], k, b["name"], b["district"], f"{d:.0f}", same,
                       b["depth_m"], "yes" if p else "no"]
                for w in wkeys[:4]:
                    row += ["" if not p or p[w]["fine"] is None else f"{p[w][c]:.2f}" for c in ("fine", "sand", "gravel")]
                wr.writerow(row)
        near_ok = True

    # ---- summary
    say(f"# GSMMA hydrogeological boreholes and lithology logs\n\nMade {stamp} by tools/process_gsmma.py.\n")
    say("Data: 經濟部地質調查及礦業管理中心, 水文地質鑽探資料庫 (data.gov.tw 16799), 平原區鑽井資料 (162478), "
        "平原區水文地質鑽探-鑽孔岩心紀錄 (61131); Open Government Data License, version 1.0, https://data.gov.tw/license\n")
    say("## Boreholes\n")
    say(f"- In 16799: {len(A)}; in 162478: {len(B)}; joined: {len(bh)} (only in 162478: {sum(1 for b in bh.values() if b['source'] == '162478')}, all without district)")
    say(f"- With a lithology log: {len(prof)}; log wells not in either list: {len(set(by) - set(bh))}")
    say("\n| district | boreholes | with log | well depth median (m) | depth range (m) |\n|---|---|---|---|---|")
    dd = defaultdict(list)
    for k, b in bh.items(): dd[b["district"] or "(none given)"].append(k)
    for z, ks in sorted(dd.items(), key=lambda kv: -len(kv[1])):
        dep = [fnum(bh[k]["depth_m"]) for k in ks if fnum(bh[k]["depth_m"])]
        say(f"| {z} | {len(ks)} | {sum(1 for k in ks if k in prof)} | {statistics.median(dep):g} | {min(dep):g}–{max(dep):g} |" if dep else f"| {z} | {len(ks)} | {sum(1 for k in ks if k in prof)} | – | – |")
    say("\n## Lithology intervals\n")
    say(f"- Intervals: {len(iv)} (dropped with missing or reversed depths: {bad}); boreholes: {len(by)}")
    say(f"- Gaps between consecutive intervals: {sum(1 for w in by.values() for a, b in zip(w, w[1:]) if b['top_m'] > a['bottom_m'] + 1e-6)}; "
        f"overlaps: {sum(1 for w in by.values() for a, b in zip(w, w[1:]) if b['top_m'] < a['bottom_m'] - 1e-6)}")
    tot = Counter()
    for x in iv: tot[x["class"]] += x["bottom_m"] - x["top_m"]
    s = sum(tot.values())
    say("\n| class | logged thickness (m) | share |\n|---|---|---|")
    for c in CLASSES: say(f"| {c} | {tot[c]:.0f} | {tot[c] / s:.1%} |")
    say(f"\nParser check against the legend names (grain codes whose name ends in a grain word): agree {check['agree']}, disagree {check['disagree']}")
    for m_ in mism: say(f"- {m_}")
    say("\nCodes classified with a note (code, note, class: intervals):\n")
    for (code, note, cls), n in sorted(notes.items(), key=lambda kv: -kv[1]): say(f"- {code}: {note}, {cls}: {n}")
    if near_ok:
        say("\n## Nearest borehole to each MOENV monitoring well\n")
        say("| MOENV district | wells | median distance (km) | 90th percentile (km) | nearest borehole in the same district |\n|---|---|---|---|---|")
        with open(OUT / "moenv_wells_nearest_borehole.csv", encoding="utf-8-sig", newline="") as fh:
            N = list(csv.DictReader(fh))
        g = defaultdict(list)
        for r in N: g[r["ugwdistname"]].append(r)
        for z, rs in sorted(g.items(), key=lambda kv: -len(kv[1])):
            d = sorted(float(r["distance_m"]) / 1000 for r in rs)
            say(f"| {z} | {len(rs)} | {statistics.median(d):.1f} | {d[min(len(d) - 1, max(0, math.ceil(0.9 * len(d)) - 1))]:.1f} | {sum(1 for r in rs if r['same_district'] == 'yes')} |")
        say("\nThe MOENV wells have no depth in the open data, so the borehole profile shows the layers near the well, not the layer the well draws from.")
    (OUT / "gsmma_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
