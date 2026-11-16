#!/usr/bin/env python3
"""Summaries for the Chianan preset from the MOENV downloads (tools/fetch_chianan_extra.py) and the MOA detailed soil map.

Usage (from the CHemTrace-TW folder):  python tools/process_chianan_extra.py
Inputs   data/raw/moenv/AQX_P_08/*  (air quality monthly values; stations 朴子, 新港, 嘉義, 新營)
         data/raw/moenv/WQX_P_01/*  (river water quality; 嘉義縣, 嘉義市, 臺南市)
         data/raw/soil/詳測土壤圖20161013/詳測土壤圖20161013.dbf (detailed soil map, attribute table; codes from
         詳測土壤圖屬性資料代碼說明20161013.doc)
Output   data/processed/chianan_extra_summary.md and .csv
Rules
  air    annual mean = mean of 12 monthly values; only years 2023-2025 with all 12 months are used (2024 is
         incomplete in the download); preset = median over stations of the mean of their complete years
  river  samples 2021-01-01 to 2025-12-31; one record per station, sampling time and item (the API lists some
         samples twice, under two townships or two station coordinates, with the same value; 2026-11-15 check);
         "-" = not measured (skipped); "<x" = below detection limit x;
         per-station median of measured values; preset = median over stations; metals reported with the share of
         samples below detection, and no preset value when most samples are below detection
  soil   polygons in 嘉義縣, 嘉義市, 臺南市 with slope class 1 (0-5 %, the plain); class shares weighted by polygon area
"""
import csv, json, statistics, struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
COUNTIES = {"嘉義縣", "嘉義市", "臺南市"}


def full_runs(dataid):
    out = []
    for d in sorted((RAW / "moenv" / dataid).glob("*")):
        m = d / "meta.json"
        if m.exists() and (d / "records.json").exists():
            q = json.loads(m.read_text(encoding="utf-8")).get("query", {})
            if int(q.get("limit", 0)) >= 1000:
                out.append(json.loads((d / "records.json").read_text(encoding="utf-8")))
    return [r for run in out for r in run]


def air(L, rows):
    R = full_runs("AQX_P_08")
    m = defaultdict(dict)
    for r in R:
        if r["itemengname"] in ("PM10", "PM2.5") and r["monitormonth"][:4] in ("2023", "2024", "2025"):
            try: m[(r["sitename"], r["itemengname"], r["monitormonth"][:4])][r["monitormonth"]] = float(r["concentration"])
            except ValueError: pass
    L.append("## Air quality (MOENV AQX_P_08, monthly values)\n")
    L.append("| station | PM10 2023 / 2024 / 2025 (µg/m³) | PM2.5 2023 / 2024 / 2025 (µg/m³) |\n|---|---|---|")
    st = defaultdict(dict)
    for s in sorted({k[0] for k in m}):
        cells = []
        for it in ("PM10", "PM2.5"):
            yr = []
            for y in ("2023", "2024", "2025"):
                v = m.get((s, it, y), {})
                yr.append(statistics.mean(v.values()) if len(v) == 12 else None)
            ok = [x for x in yr if x is not None]
            if ok: st[it][s] = statistics.mean(ok)
            cells.append(" / ".join(f"{x:.1f}" if x is not None else "incomplete" for x in yr))
        L.append(f"| {s} | {cells[0]} | {cells[1]} |")
    for it in ("PM10", "PM2.5"):
        if st[it]:
            v = statistics.median(st[it].values())
            L.append(f"\n{it}: median over {len(st[it])} stations of the means of the complete years 2023-2025 = **{v:.1f} µg/m³**")
            rows.append({"item": it, "value": f"{v:.1f}", "unit": "µg/m³", "n": len(st[it]), "note": "median of station means, complete years of 2023-2025"})
    L.append("")


def river(L, rows):
    R0 = [r for r in full_runs("WQX_P_01") if r["county"] in COUNTIES and "2021-01-01" <= r["sampledate"][:10] <= "2025-12-31"]
    seen = {}
    for r in R0: seen.setdefault((r["siteid"], r["sampledate"], r["itemengabbreviation"]), r)
    R = list(seen.values())
    L.append("## River water quality (MOENV WQX_P_01), 2021-2025, 嘉義縣, 嘉義市, 臺南市\n")
    basins = defaultdict(set)
    for r in R: basins[r["basin"] or "(no basin)"].add(r["siteid"])
    L.append(f"Records in 2021-2025: {len(R0)}; after removing repeated station-time-item records: {len(R)}\n")
    L.append("Stations per basin: " + ", ".join(f"{b} {len(s)}" for b, s in sorted(basins.items(), key=lambda x: -len(x[1]))) + "\n")
    L.append("| item | samples measured | below detection | detection limits seen (mg/L) | median of station medians | stations |\n|---|---|---|---|---|---|")
    for it, unit, f in (("SS", "mg/L", 1), ("pH", "", 1), ("As", "µg/L", 1000), ("Hg", "µg/L", 1000), ("Pb", "µg/L", 1000),
                         ("Cd", "µg/L", 1000), ("Ni", "µg/L", 1000), ("Cr6", "µg/L", 1000), ("Cr", "µg/L", 1000)):
        per, nd, dls, n = defaultdict(list), 0, set(), 0
        for r in R:
            if r["itemengabbreviation"] != it: continue
            v = r["itemvalue"].strip()
            if v in ("-", ""): continue
            n += 1
            if v.startswith("<"):
                nd += 1; dls.add(v[1:]); continue
            try: per[r["siteid"]].append(float(v) * f)
            except ValueError: pass
        vals = [statistics.median(x) for x in per.values() if x]
        med = statistics.median(vals) if vals else None
        share = nd / n if n else 0
        use = med is not None and share < 0.5
        L.append(f"| {it} | {n} | {nd} ({share:.0%}) | {', '.join(sorted(dls)[:4]) or '–'} | {f'{med:.3g} {unit}' if med is not None else '–'}{'' if use else ' (not used: mostly below detection)' if med is not None else ''} | {len(per)} |")
        rows.append({"item": "river " + it, "value": f"{med:.3g}" if use else "", "unit": unit, "n": len(per), "note": f"{nd} of {n} samples below detection ({share:.0%})"})
    L.append("\nMetals are MOENV river monitoring values (total, not filtered), so as a 'dissolved background' they are an upper bound.\n")


def soil(L, rows):
    p = RAW / "soil" / "詳測土壤圖20161013" / "詳測土壤圖20161013.dbf"
    if not p.exists():
        L.append("## Soil\n\nSoil map not found.\n"); return
    f = p.open("rb"); h = f.read(32); n, hl, rl = struct.unpack("<IHH", h[4:12]); fields = []
    while True:
        d = f.read(32)
        if d[0] == 0x0D: break
        fields.append((d[:11].split(b"\0")[0].decode("big5", "replace"), d[16]))
    f.seek(hl)
    names = [x[0] for x in fields]
    PH = {1: "< 4.5", 2: "4.6-5.0", 3: "5.1-5.5", 4: "5.6-6.0", 5: "6.1-6.5", 6: "6.6-7.3", 7: "7.4-7.8", 8: "7.9-8.4", 9: "8.5-9.0", 10: "> 9.1"}
    DR = {1: "good", 2: "imperfect", 3: "poor", 4: "very poor", 23: "flooded"}
    ph, dr, tot = defaultdict(float), defaultdict(float), 0.0
    for _ in range(n):
        rec = f.read(rl); pos = 1; v = {}
        for name, l in fields:
            v[name] = rec[pos:pos + l].decode("big5", "replace").strip(); pos += l
        if v[names[0]] not in COUNTIES: continue
        try:
            slope, a = int(float(v["坡度"] or 0)), float(v["面積"] or 0)
            c_ph, c_dr = int(float(v["表土酸鹼性"] or 0)), int(float(v["排水等級"] or 0))
        except (KeyError, ValueError):
            continue
        if slope != 1: continue
        tot += a
        if c_ph: ph[c_ph] += a
        if c_dr: dr[c_dr] += a
    L.append("## Soil (MOA detailed soil map, 2016-10-13), 嘉義縣, 嘉義市, 臺南市, slope class 1 (0-5 %)\n")
    L.append(f"Mapped area {tot / 1e6:.0f} km². Shares of the area with data:\n")
    def share(d, lab):
        s = sum(d.values()); out = sorted(d.items(), key=lambda x: -x[1])
        return ", ".join(f"{lab.get(k, k)} {a / s:.0%}" for k, a in out)
    L.append("- topsoil pH class: " + share(ph, PH))
    L.append("- drainage class: " + share(dr, DR))
    s = sum(ph.values()); cum = 0
    for k in sorted(ph):
        cum += ph[k]
        if cum >= s / 2:
            L.append(f"- area-weighted median topsoil pH class: {PH[k]}"); rows.append({"item": "soil pH class (median)", "value": PH[k], "unit": "", "n": "", "note": "area-weighted"}); break
    top = max(dr.items(), key=lambda x: x[1])[0]
    rows.append({"item": "soil drainage class (largest share)", "value": DR.get(top, top), "unit": "", "n": "", "note": f"{dr[top] / sum(dr.values()):.0%} of area"})
    L.append("")


def main():
    L, rows = ["# Chianan preset: air, river and soil summaries\n", "Made by tools/process_chianan_extra.py; rules in the script header.\n"], []
    air(L, rows); river(L, rows); soil(L, rows)
    (OUT / "chianan_extra_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(OUT / "chianan_extra_summary.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "value", "unit", "n", "note"]); w.writeheader(); w.writerows(rows)
    print("\n".join(L))


if __name__ == "__main__":
    main()
