#!/usr/bin/env python3
"""V2 prototype: geogenic arsenic in groundwater of 嘉南平原, by aquifer layer, compared with WRA measurements.

Usage (from the CHemTrace-TW folder; needs Node.js for the Kd check):  python tools/v2_geogenic_as_prototype.py

Model (proposal, same form as the website's background-soil term cwBg in core(), app.js ~line 1147):
    C_w [µg/L] = 1000 * As_sed_reactive [mg/kg] / (Kd_aq [L/kg] + ne / rho_b)
    Kd_aq = kdFn("As", {pH, fe, sp, redox}) exactly as in base app.js 0.13.0 (checked against the original here)
    redox  = class from the extended ladder, flow-path mode (tools/ladder_v2_prototype.py): o2 -> oxic, no3 -> suboxic,
             mn/fe -> anoxic, so4/ch4 -> sulfidic (the website's classes)
    90 % range of C_w from the website's Kd uncertainty for As (KD_SIG = 0.8 in log10 units, app.js ~line 1023):
             factor 10^(1.645*0.8) up and down.

Inputs and sources:
    As_sed_reactive  2, 5, 10 mg/kg: PHH-extractable As (Fe-(hydr)oxide and organic phases), mostly 0-10 mg/kg in cores
                     CN-1 and CN-23 (Chen & Liu 2007 Fig. 8, figure reading); all of it is taken as reactive.
    sp               As(III): Chen & Liu (2007) p. 985, As in this groundwater is largely As(III) (citing Chen et al. 1994).
    pH               median of WRA 161086 records of the layer (not an arsenic value).
    Fe               3 and 15 g/kg (Chen & Liu 2007 Fig. 9d, figure reading; different extraction from oxalate-Fe).
    ne 0.2, rho_b 1.8 kg/L   website defaults (ASSUMED).
    redox inputs     as in tools/ladder_v2_prototype.py; sediment age = groundwater age T; k = Middelburg (1989) eq. 8b,
                     k = 0.16 T^-0.95 per year (p. 1578), and k/10 as sensitivity (aquifer organic matter is less reactive
                     than marine: Jakobsen & Postma 1994, qualitative).
    T                layer 1: 1,000 and 10,000 yr (Chen & Liu 2007 Fig. 7, about 1-11 ka); layers 2-4: 10,000 and 40,000 yr.
Measured: WRA 161086 'aso' (taken to be As, mg/L; unconfirmed), per-well medians by layer.
Output: data/processed/v2_geogenic_as.csv and v2_summary.md
"""
import csv, itertools, json, math, statistics, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "tools"))
import ladder_v2_prototype as LV          # noqa: E402

KD_SIG_AS = 0.8
CLS = {"o2": "oxic", "no3": "suboxic", "mn": "anoxic", "fe": "anoxic", "so4": "sulfidic", "ch4": "sulfidic"}
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def clamp(v, a, b):
    return max(a, min(b, v))


def kd_as(pH, fe, sp="V", redox="oxic", drain=None, pHigh=False):
    """Python copy of kdFn('As', ...) from base app.js 0.13.0 (checked against the original in check_kd())."""
    lg = 2.77 + 0.9 * math.log10(max(fe, 0.05)) - 0.25 * max(0, pH - 7) + 0.1 * max(0, 7 - pH) - (0.3 if pHigh else 0)
    if sp == "III": lg -= 0.7
    if drain == "periodic": lg -= 0.5
    elif drain == "perm": lg -= 1.2
    if redox == "suboxic": lg -= 0.3
    elif redox == "anoxic": lg -= 1.2
    elif redox == "sulfidic": lg -= 0.7
    return 10 ** clamp(lg, 0.3, 4.3)


def check_kd():
    src = (ROOT / "base" / "docs" / "assets" / "js" / "app.js").read_text(encoding="utf-8")
    i = src.index("function kdFn(m, p){"); depth = 0; j = src.index("{", i)
    for j in range(j, len(src)):
        if src[j] == "{": depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0: break
    fn = src[i:j + 1]
    cases = [(pH, fe, sp, rx) for pH in (6.5, 7.3, 8.2) for fe in (0.5, 3, 15) for sp in ("V", "III") for rx in ("oxic", "anoxic", "sulfidic")]
    js = ("const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));" + fn + ";const C=" + json.dumps(cases) +
          ";console.log(JSON.stringify(C.map(c=>kdFn('As',{pH:c[0],fe:c[1],sp:c[2],redox:c[3]}))));")
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8")
    if out.returncode: sys.exit(out.stderr)
    ref = json.loads(out.stdout)
    bad = [(c, r, kd_as(*c)) for c, r in zip(cases, ref) if abs(kd_as(*c) - r) > 1e-9 * r]
    return len(cases), bad


def main():
    n, bad = check_kd()
    print(f"kdFn check against app.js: {n - len(bad)} of {n} cases identical")
    with open(P / "wra_quality_clean.csv", encoding="utf-8-sig", newline="") as fh:
        R = [r for r in csv.DictReader(fh) if r["groundwaterzone"] == "嘉南平原"]
    def per_well(lc, k):
        per = defaultdict(list)
        for r in R:
            if r["layercode"] == lc and r[k] != "": per[r["wellidentifier"]].append(float(r[k]))
        return [statistics.median(v) for v in per.values()]
    med = lambda lc, k: statistics.median(per_well(lc, k))
    t = med("1", "temp"); Tk = t + 273.15
    o2 = math.exp(-139.34411 + 1.575701e5 / Tk - 6.642308e7 / Tk**2 + 1.243800e10 / Tk**3 - 8.621949e11 / Tk**4)
    base = {"o2In": o2, "no3In": med("1", "NO3N") * LV.N_TO_NO3, "so4In": med("1", "SO4"), "docIn": med("1", "TOC"),
            "grad": 5e-4, "ne": 0.2, "aqMn": 0.2, "K": 3.14e-5, "mode": "flowpath"}
    ages = {"1": (1e3, 1e4), "2": (1e4, 4e4), "3": (1e4, 4e4), "4": (1e4, 4e4)}
    rows = []
    for lc in ("1", "2", "3", "4"):
        pH = med(lc, "pH")
        for T, fe, oc, kf, asd in itertools.product(ages[lc], (3, 15), (0.1, 0.3, 0.9), (1, 0.1), (2, 5, 10)):
            teap, _ = LV.ladder_v2(dict(base, budT=T, aqFe=fe, ocSed=oc, kOC=0.16 * T**-0.95 * kf))
            kd = kd_as(pH, fe, "III", CLS[teap])
            cw = 1000 * asd / (kd + 0.2 / 1.8)
            f = 10 ** (1.645 * KD_SIG_AS)
            rows.append({"layer": lc, "T_yr": T, "aqFe_g_kg": fe, "ocSed_pct": oc, "k_factor": kf, "As_sed_mg_kg": asd, "pH": f"{pH:.2f}",
                         "teap": teap, "redox_class": CLS[teap], "Kd_L_kg": f"{kd:.3g}", "As_pred_ug_L": f"{cw:.3g}",
                         "As_pred_p5_ug_L": f"{1000 * asd / (kd * f + 0.2 / 1.8):.3g}", "As_pred_p95_ug_L": f"{1000 * asd / (kd / f + 0.2 / 1.8):.3g}"})
    with open(P / "v2_geogenic_as.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

    L = []; say = L.append
    say("# V2 prototype: geogenic arsenic in 嘉南平原 by aquifer layer\n")
    say(f"Made {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by tools/v2_geogenic_as_prototype.py. kdFn check: {n - len(bad)} of {n} identical.\n")
    say("| layer | measured As, per-well medians: median (25th–75th pct), µg/L [wells] | predicted, median over scenarios (range of central values) µg/L | redox classes in the scenarios |\n|---|---|---|---|")
    for lc in ("1", "2", "3", "4"):
        m = sorted(x * 1000 for x in per_well(lc, "As_aso"))
        q = lambda p: m[min(len(m) - 1, max(0, round(p * (len(m) - 1))))]
        rs = [r for r in rows if r["layer"] == lc]
        pv = sorted(float(r["As_pred_ug_L"]) for r in rs)
        say(f"| {lc} | {statistics.median(m):.3g} ({q(0.25):.3g}–{q(0.75):.3g}) [{len(m)}] | {statistics.median(pv):.3g} ({pv[0]:.3g}–{pv[-1]:.3g}) | "
            + ", ".join(f"{k} {v}" for k, v in Counter(r['redox_class'] for r in rs).most_common()) + " |")
    say("\nBy redox class and sediment As (layers 2–4, central values, µg/L):\n")
    say("| redox class | As_sed 2 mg/kg | 5 mg/kg | 10 mg/kg |\n|---|---|---|---|")
    for c in ("anoxic", "sulfidic"):
        vals = []
        for asd in (2, 5, 10):
            v = [float(r["As_pred_ug_L"]) for r in rows if r["layer"] != "1" and r["redox_class"] == c and r["As_sed_mg_kg"] == asd]
            vals.append(f"{min(v):.3g}–{max(v):.3g}" if v else "–")
        say(f"| {c} | " + " | ".join(vals) + " |")
    say("\nThe 90 % range from the Kd uncertainty is a factor of about 20 up and down around each central value (v2_geogenic_as.csv).")
    (P / "v2_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
