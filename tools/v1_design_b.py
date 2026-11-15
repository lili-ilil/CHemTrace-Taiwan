#!/usr/bin/env python3
"""V1 design B for 嘉南平原: run the original redox ladder with inputs that do not come from the well being tested,
per aquifer layer, and compare with the redox classes measured in WRA observation wells of that layer.

Usage (from the CHemTrace-TW folder; needs Node.js):  python tools/v1_design_b.py

Inputs and sources (also written to the summary):
  recharge O2       oxygen solubility in fresh water at the layer-1 median water temperature (WRA data), Benson & Krause
                    equation as given in USGS Office of Water Quality Technical Memorandum 2011.03 (2011), eq. 7, at 1 atm.
                    Assumes recharge water enters saturated with air (ASSUMED). Sensitivity: O2 = 0.
  recharge NO3, SO4, DOC   medians over layer-1 wells of 嘉南平原 (WRA 161086: NO3-N converted to NO3, SO4, TOC as DOC).
                    Sensitivity: TOC median of the layer itself.
  time scale budT   14C(DIC) ages read from Chen & Liu (2007) Fig. 7 (p. 987; figure reading): layer 1 about 1-11 ka,
                    layers 2-4 mostly 10-40 ka (text, p. 986). Runs use 10 ka and 40 ka for layers 2-4.
  aquifer Fe        3 and 15 g/kg: range of 3-stage-extractable Fe read from Chen & Liu (2007) Fig. 9d (p. 989); a
                    different extraction from the oxalate-Fe the website assumes.
  aquifer Mn, K, gradient, porosity   website defaults (BASE + plateau preset): ASSUMED; K also x0.01 and x0.001 as sensitivity.
Measured classes: data/processed/wra_quality_clean.csv (tools/process_wra.py), O2 unknown.
Outputs: data/processed/v1b_runs.csv, v1b_summary.md
"""
import csv, itertools, json, math, statistics, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
N_TO_NO3 = 62.004 / 14.007
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def o2_sat(t_c):
    """Benson & Krause, USGS OWQ Tech. Memo. 2011.03 eq. 7: fresh water, 1 atm, mg/L."""
    T = t_c + 273.15
    return math.exp(-139.34411 + 1.575701e5 / T - 6.642308e7 / T**2 + 1.243800e10 / T**3 - 8.621949e11 / T**4)


def main():
    with open(P / "wra_quality_clean.csv", encoding="utf-8-sig", newline="") as fh:
        R = [r for r in csv.DictReader(fh) if r["groundwaterzone"] == "嘉南平原"]

    def layer_median(lc, k):
        per = defaultdict(list)
        for r in R:
            if r["layercode"] == lc and r[k] != "": per[r["wellidentifier"]].append(float(r[k]))
        return statistics.median(statistics.median(v) for v in per.values()), len(per)
    rech = {k: layer_median("1", k) for k in ("TOC", "NO3N", "SO4", "temp")}
    t_rech = rech["temp"][0]
    o2s = o2_sat(t_rech)
    own_toc = {lc: layer_median(lc, "TOC")[0] for lc in ("2", "3", "4")}

    runs, meta = [], []
    grid = itertools.product(("2", "3", "4"), (10000, 40000), (3, 15), (1, 0.01, 0.001), ("saturated", "zero"), ("layer 1", "own layer"))
    for i, (lc, T, fe, kf, o2case, doccase) in enumerate(grid):
        inp = {"o2In": o2s if o2case == "saturated" else 0.0, "no3In": rech["NO3N"][0] * N_TO_NO3, "so4In": rech["SO4"][0],
               "docIn": rech["TOC"][0] if doccase == "layer 1" else own_toc[lc], "orgType": "none",
               "budT": T, "aqFe": fe, "K": 0.002 * kf}
        runs.append({"id": i, "preset": "plateau", "inputs": inp})
        meta.append({"layer": lc, "budT_yr": T, "aqFe_g_per_kg": fe, "K_factor": kf, "recharge_O2": o2case, "DOC_from": doccase})
    res = subprocess.run(["node", str(ROOT / "tools" / "ladder_node.mjs")], input=json.dumps(runs), capture_output=True, text=True, encoding="utf-8")
    if res.returncode:
        sys.exit("ladder_node.mjs failed:\n" + res.stderr)
    out = {o["id"]: o for o in json.loads(res.stdout)}
    rows = []
    for r, m in zip(runs, meta):
        o = out[r["id"]]
        rows.append({**m, "o2In": f"{r['inputs']['o2In']:.2f}", "docIn": f"{r['inputs']['docIn']:.2f}", "teap": o["teap"], "class": o["cls"],
                     "s1": f"{o['s1']:.3g}", "s2": f"{o['s2']:.3g}", "tEx_yr": "" if o["tEx"] is None else f"{o['tEx']:.3g}"})
    with open(P / "v1b_runs.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

    L = []; say = L.append
    say("# V1 design B (嘉南平原): redox ladder with independent inputs vs measured classes by layer\n")
    say(f"Made {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by tools/v1_design_b.py; ladder from base/ app.js 0.13.0.\n")
    say("## Inputs\n\n| input | value | source | status |\n|---|---|---|---|")
    say(f"| recharge O2 | {o2s:.2f} mg/L (saturation at {t_rech:.1f} °C) | Benson & Krause, USGS OWQ Tech. Memo. 2011.03 eq. 7; temperature = layer-1 median, WRA 161086 | saturation ASSUMED |")
    say(f"| recharge NO3 | {rech['NO3N'][0]:.3g} mg/L NO3-N ({rech['NO3N'][0] * N_TO_NO3:.3g} mg/L NO3) | layer-1 median of {rech['NO3N'][1]} wells, WRA 161086 | data |")
    say(f"| recharge SO4 | {rech['SO4'][0]:.3g} mg/L | layer-1 median, WRA 161086 | data |")
    say(f"| DOC | layer 1: {rech['TOC'][0]:.3g} mg/L; own layer: " + ", ".join(f"L{k} {v:.3g}" for k, v in own_toc.items()) + " | TOC medians, WRA 161086 (TOC as DOC) | data |")
    say("| time scale | 10,000 and 40,000 yr | Chen & Liu (2007) p. 986 and Fig. 7 (figure reading) | literature |")
    say("| aquifer Fe | 3 and 15 g/kg | Chen & Liu (2007) Fig. 9d (figure reading; different extraction) | literature |")
    say("| aquifer Mn 0.2 g/kg, K 0.002 m/s (and ×0.01, ×0.001), gradient 0.003, porosity 0.2 | | website defaults | ASSUMED |")
    say("\n## Ladder result by scenario (same for layers 2, 3 and 4 unless the DOC comes from the layer itself)\n")
    agg = defaultdict(Counter)
    for x in rows: agg[(x["recharge_O2"], x["DOC_from"])][x["teap"]] += 1
    say("| recharge O2 | DOC from | ladder TEAP over the 36 runs (3 layers × 2 time scales × 2 Fe × 3 K) |\n|---|---|---|")
    for (o2c, dc), c in sorted(agg.items()):
        say(f"| {o2c} | {dc} | " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + " |")
    say("\n## Measured classes by layer (WRA 161086, O2 unknown)\n")
    for lc in ("2", "3", "4"):
        c = Counter(r["redox_class"] for r in R if r["layercode"] == lc and r["redox_class"] != "incomplete")
        n = sum(c.values())
        say(f"- Layer {lc} ({n} classified records): " + ", ".join(f"{k} {v / n:.0%}" for k, v in c.most_common(5)))
    (P / "v1b_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
