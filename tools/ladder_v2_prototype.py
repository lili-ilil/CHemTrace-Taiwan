#!/usr/bin/env python3
"""Prototype of an extended redox ladder for old, slowly flowing aquifers (proposal; not part of the website yet).

Usage (from the CHemTrace-TW folder; needs Node.js for the equivalence check):
    python tools/ladder_v2_prototype.py

The website ladder (redoxLadder, base app.js 0.13.0) supplies electron donors only with the inflowing water and
compares the time to use up the Mn and Fe oxides in the first LAD_ZONE metres with the time scale budT.
The extension writes the same idea as one electron budget per litre of pore water in that zone over a time T:

    pore volumes through the zone   N   = max(1, v*T / LAD_ZONE)
    donors                          D   = N*e_DOC + E_sed
    sediment organic carbon         E_sed = OC% * 10 g/kg / 12 g/mol * 4 e-/C * 1000 * (1 - exp(-k*T)) * LAD_RB / ne   [mmol e-/L]
    acceptors used in order         N*e_O2, N*e_NO3, Mn oxide stock, Fe oxide stock, N*e_SO4, then methanogenesis
    TEAP                            the first acceptor the donors do not use up
Two modes: "zone" (as above; the website's view near a source) and "flowpath" (N = 1: one litre of water followed for
its age T, as for natural background far down a regional flow path). The flow velocity matters only in "zone" mode.

With E_sed = 0 this gives the website's oxic and nitrate steps exactly, and its Mn and Fe steps when N = v*T/L >= 1
(D - N*(e_O2 + e_NO3) = N*s2 compared with the oxide stocks is the same as tMn and tEx compared with T). The sulfate
step differs slightly: the website compares s2 with e_SO4 per pore volume after the oxides are used up; here the
oxide stock is subtracted first. The script checks the equivalence against the original function on random inputs.

Scenarios for 嘉南平原 layers 2-4 (sources in 08_氧化還原階梯修改提案.md):
    recharge O2 at saturation; recharge NO3, SO4, DOC = layer-1 medians (WRA 161086)
    T = 10,000 and 40,000 yr (Chen & Liu 2007, p. 986 and Fig. 7)
    K = 3.14e-5 and 1.80e-4 m/s (Lu et al. 2008, Darcy estimates) and the same divided by 10 (their pumping tests are
        about one order of magnitude lower); gradient 5e-4 (plane fitted to WRA mean water levels, layers 2-4)
    ne = 0.2 (website default, ASSUMED); Fe 3 and 15 g/kg (Chen & Liu 2007 Fig. 9d, figure reading); Mn 0.2 g/kg (ASSUMED)
    sediment OC 0.1, 0.3, 0.9 % (Chen & Liu 2007 Fig. 9b, figure reading: about 0-0.9 %)
    k = 1e-6, 1e-5, 1e-4 per year: Burdige (2011, p. 403) estimates about 1e-4 per year for reactive organic matter
        500-1000 years old from the Middelburg (1989) power model; older sediment is less reactive. The exact
        coefficients of Middelburg (1989) still have to be checked in the original.
Output: data/processed/ladder_v2_scenarios.csv and a printed summary.
"""
import csv, itertools, json, math, random, statistics, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
YEAR_S, LAD_ZONE, LAD_RB, DOC_E = 31557600, 10, 1.8, 4 / 12
N_TO_NO3 = 62.004 / 14.007
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def ladder_v2(I):
    ne = max(0.005, I.get("ne", 0.2)); T = I.get("budT", 1)
    e_o2, e_no3, e_so4 = 4 * I["o2In"] / 32, 5 * I["no3In"] / 62, 8 * I["so4In"] / 96
    e_doc = DOC_E * I["docIn"]
    cap_mn = 2 * I.get("aqMn", 0.2) * 1000 / 54.94 * LAD_RB / ne
    cap_fe = I.get("aqFe", 0.5) * 1000 / 55.85 * LAD_RB / ne
    v = I["K"] * YEAR_S * I["grad"] / ne
    # mode "zone": the website's view (first LAD_ZONE metres, water flushes through); mode "flowpath": follow one litre
    # of water along its flow path for its age T (no flushing: N = 1), meeting sediment that has not been flushed
    N = 1.0 if I.get("mode") == "flowpath" else max(1.0, v * T / LAD_ZONE)
    oc, k = I.get("ocSed", 0.0), I.get("kOC", 0.0)
    e_sed = oc * 10 / 12 * 4 * 1000 * (1 - math.exp(-k * T)) * LAD_RB / ne if oc and k else 0.0
    D = N * e_doc + e_sed
    steps = [("o2", N * e_o2), ("no3", N * e_no3), ("mn", cap_mn), ("fe", cap_fe), ("so4", N * e_so4)]
    acc = 0.0
    for name, a in steps:
        acc += a
        if D <= acc:
            return name, {"N": N, "D": D, "E_sed": e_sed, "v": v}
    return "ch4", {"N": N, "D": D, "E_sed": e_sed, "v": v}


def check_equivalence(n=400):
    random.seed(1)
    runs = []
    for i in range(n):
        inp = {"o2In": random.choice([0, 0.5, 2, 8]), "no3In": random.choice([0, 1, 15]), "so4In": random.choice([0, 5, 30, 300]),
               "docIn": random.choice([0.5, 1, 3, 10, 30]), "aqFe": random.choice([0.2, 0.5, 5]), "aqMn": 0.2,
               "K": random.choice([1e-3, 1e-4, 1e-5]), "grad": random.choice([0.003, 0.0005]), "ne": 0.2,
               "budT": random.choice([1, 10, 100, 1e4]), "orgType": "none"}
        runs.append({"id": i, "preset": "plateau", "inputs": inp})
    res = subprocess.run(["node", str(ROOT / "tools" / "ladder_node.mjs")], input=json.dumps(runs), capture_output=True, text=True, encoding="utf-8")
    if res.returncode:
        sys.exit(res.stderr)
    orig = {o["id"]: o["teap"] for o in json.loads(res.stdout)}
    same = Counter(); diff = []
    for r in runs:
        new, info = ladder_v2(r["inputs"])
        o = orig[r["id"]]
        v_ok = info["v"] * r["inputs"]["budT"] / LAD_ZONE >= 1
        key = "same" if new == o else ("differs (N<1: zone not flushed)" if not v_ok else "differs")
        same[key] += 1
        if key == "differs" and len(diff) < 5: diff.append((r["inputs"], o, new))
    return same, diff


def main():
    same, diff = check_equivalence()
    print("Equivalence with the website ladder (sediment OC off, 400 random cases):", dict(same))
    for d in diff: print("  differs:", d)

    with open(P / "wra_quality_clean.csv", encoding="utf-8-sig", newline="") as fh:
        R = [r for r in csv.DictReader(fh) if r["groundwaterzone"] == "嘉南平原"]
    def med(lc, k):
        per = defaultdict(list)
        for r in R:
            if r["layercode"] == lc and r[k] != "": per[r["wellidentifier"]].append(float(r[k]))
        return statistics.median(statistics.median(v) for v in per.values())
    t = med("1", "temp"); Tk = t + 273.15
    o2s = math.exp(-139.34411 + 1.575701e5 / Tk - 6.642308e7 / Tk**2 + 1.243800e10 / Tk**3 - 8.621949e11 / Tk**4)
    base = {"o2In": o2s, "no3In": med("1", "NO3N") * N_TO_NO3, "so4In": med("1", "SO4"), "docIn": med("1", "TOC"),
            "grad": 5e-4, "ne": 0.2, "aqMn": 0.2}
    rows = []
    for mode, T, K, fe, oc, k in itertools.product(("zone", "flowpath"), (1e4, 4e4), (3.14e-6, 1.8e-5, 3.14e-5, 1.8e-4), (3, 15), (0.1, 0.3, 0.9), (1e-6, 1e-5, 1e-4)):
        I = dict(base, budT=T, K=K, aqFe=fe, ocSed=oc, kOC=k, mode=mode)
        teap, info = ladder_v2(I)
        rows.append({"mode": mode, "budT_yr": T, "K_m_s": K, "aqFe_g_kg": fe, "ocSed_pct": oc, "kOC_per_yr": k, "teap": teap,
                     "v_m_yr": f"{info['v']:.3g}", "pore_volumes": f"{info['N']:.3g}", "E_sed_mmol_e_L": f"{info['E_sed']:.4g}", "D_mmol_e_L": f"{info['D']:.4g}"})
    for I0, lab in ((dict(base, budT=1e4, K=1.8e-4, aqFe=3), "same scenario without sediment OC"),):
        print(f"Without sediment OC ({lab}):", ladder_v2(I0)[0])
    with open(P / "ladder_v2_scenarios.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    print(f"\nInputs: recharge O2 {o2s:.2f} mg/L (saturation at {t:.1f} °C), NO3 {base['no3In']:.3g} mg/L, SO4 {base['so4In']:.3g} mg/L, DOC {base['docIn']:.3g} mg/L")
    for mode in ("zone", "flowpath"):
        rs = [r for r in rows if r["mode"] == mode]
        print(f"\nMode {mode}: {len(rs)} scenarios. TEAP overall:", dict(Counter(r["teap"] for r in rs)))
        for k in (1e-6, 1e-5, 1e-4):
            print(f"  k = {k:g}/yr:", dict(Counter(r["teap"] for r in rs if r["kOC_per_yr"] == k)))
        for oc in (0.1, 0.3, 0.9):
            print(f"  OC = {oc}%:", dict(Counter(r["teap"] for r in rs if r["ocSed_pct"] == oc)))
        for fe in (3, 15):
            print(f"  Fe = {fe} g/kg:", dict(Counter(r["teap"] for r in rs if r["aqFe_g_kg"] == fe)))
        if mode == "zone":
            for K in (3.14e-6, 1.8e-5, 3.14e-5, 1.8e-4):
                print(f"  K = {K:g} m/s:", dict(Counter(r["teap"] for r in rs if r["K_m_s"] == K)))


if __name__ == "__main__":
    main()
