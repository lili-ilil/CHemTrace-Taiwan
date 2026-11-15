#!/usr/bin/env python3
"""Extend the V1/V2 prototypes from 嘉南平原 to the other arsenic-potential districts (濁水溪沖積扇, 屏東平原, 蘭陽平原).

Usage (from the CHemTrace-TW folder):  python tools/v2_districts.py

For each district and aquifer layer (WRA 161086 joined with the well list, tools/process_wra.py):
  measured    per-well medians of aso (taken to be As), share of records above 10 µg/L, measured redox classes (O2 unknown)
  model       extended ladder in flow-path mode (tools/ladder_v2_prototype.py) + geogenic As term
              (tools/v2_geogenic_as_prototype.py), with district-specific measured inputs:
                recharge O2 = saturation at the layer-1 median temperature; recharge NO3, SO4, DOC = layer-1 medians;
                pH = median of the layer
              and literature inputs TRANSFERRED FROM 嘉南平原 (Chen & Liu 2007), because no district values were found
              in the abstracts read so far: sediment reactive As 2, 5, 10 mg/kg; Fe 3 and 15 g/kg; sediment OC 0.1, 0.3,
              0.9 %.
              Organic-matter reactivity follows the SEDIMENT age, not the water age: k = Middelburg (1989) 0.16 a^-0.95 per
              year (and k/10), with a = 10,000 yr for layer 1 (嘉南平原: the upper ~100 m deposited in the last 10,000
              years, Chen & Liu 2007 p. 977) and 30,000 yr for layers 2-4 (嘉南平原北區: intermediate aquifer deposited
              30,000-10,000 years ago, Lu et al. 2008 p. 148); transferred to the other districts (ASSUMED).
              Groundwater age (the exposure time T) is not known for these districts, so the model is run for
              T = 100, 1,000, 10,000 and 40,000 years and the results are reported per T.
Second part ("local runs"): district literature values replace the borrowed ones where a full text gives them
  濁水溪沖積扇  groundwater age T: layer 1 (unconfined, above the Huchi aquitard) 40 yr = span of the bomb-tritium front
                (Liu 1995 p. 539; the shallow water is a mixture of <40 yr and older water, p. 534); layers 2-4 (confined,
                below the aquitard) 4,150 and 18,000 yr = youngest and oldest conventional 14C ages in Liu (1995) Table 1
                (p. 534). Sediment age: the Huchi aquitard (30-60 m depth) was deposited 20-6 ka BP (Liu 1995 p. 534),
                so layer 1 sediments are younger than 6 ka and layers 2-4 older than 20 ka; the bounds 6,000 and 20,000 yr
                are used. Sediment As: total As in sand cores, log10 mean 0.69 ± 0.29 (Liu et al. 2006 J. Environ.
                Qual. 35:68-75, p. 70), i.e. 2.5 / 4.9 / 9.5 mg/kg; total As, so predictions are an upper bound.
                Liu et al. (2006, p. 72) found groundwater As correlated with aquitard cores, not aquifer cores.
                WRA layer 1 is mostly 'U' (median depth 45 m) and layers 2-4 'C' (median 119-280 m), which is how the
                WRA layers are matched to the paper's unconfined / confined aquifers (ASSUMED mapping).
  蘭陽平原      sediment As: total As by XRF in 9 well-screen core samples, 6.7 / 17.1 / 22.4 mg/kg (min / median / max,
                Liu & Wu 2019 Table 5 p. 11). This is TOTAL As, so predictions are an upper bound; the script also
                back-calculates the reactive As needed to reproduce the measured medians (WRA 161086 and Liu & Wu 2019
                Table 1 p. 4: aquifer 1, 13-70 m, and aquifer 2, 70-250 m). Groundwater and sediment ages: not found
                (the 18 ka sequence boundary in Liu & Wu 2019 p. 2 has no depth in the text), so the grid T and the
                assumed sediment ages are kept.
  屏東平原      no district literature found; not rerun.
Outputs: data/processed/v2_districts.csv, v2_districts_summary.md, v2_districts_local.csv"""
import csv, itertools, math, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "tools"))
import ladder_v2_prototype as LV                 # noqa: E402
from v2_geogenic_as_prototype import kd_as, CLS  # noqa: E402
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass
ZONES = ["嘉南平原", "濁水溪沖積扇", "屏東平原", "蘭陽平原"]
AGES = [1e2, 1e3, 1e4, 4e4]


def main():
    with open(P / "wra_quality_clean.csv", encoding="utf-8-sig", newline="") as fh:
        Q = list(csv.DictReader(fh))
    rows, L = [], []
    MEAS = {}
    say = L.append
    say("# V1/V2 prototypes in the four arsenic-potential districts\n")
    say(f"Made {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by tools/v2_districts.py. Literature inputs other than "
        "groundwater age are transferred from 嘉南平原 (Chen & Liu 2007); see the script header.\n")
    for z in ZONES:
        R = [r for r in Q if r["groundwaterzone"] == z]
        def per_well(lc, k):
            per = defaultdict(list)
            for r in R:
                if r["layercode"] == lc and r[k] != "": per[r["wellidentifier"]].append(float(r[k]))
            return [statistics.median(v) for v in per.values()]
        def med(lc, k):
            v = per_well(lc, k)
            return statistics.median(v) if v else None
        t = med("1", "temp"); Tk = t + 273.15
        o2 = math.exp(-139.34411 + 1.575701e5 / Tk - 6.642308e7 / Tk**2 + 1.243800e10 / Tk**3 - 8.621949e11 / Tk**4)
        rech = {"NO3N": med("1", "NO3N"), "SO4": med("1", "SO4"), "TOC": med("1", "TOC")}
        base = {"o2In": o2, "no3In": rech["NO3N"] * LV.N_TO_NO3, "so4In": rech["SO4"], "docIn": rech["TOC"],
                "grad": 5e-4, "ne": 0.2, "aqMn": 0.2, "K": 3.14e-5, "mode": "flowpath"}
        say(f"\n## {z}\n")
        say(f"Recharge (layer-1 medians): O2 {o2:.2f} mg/L (saturation at {t:.1f} °C), NO3-N {rech['NO3N']:.3g}, SO4 {rech['SO4']:.3g}, TOC {rech['TOC']:.3g} mg/L\n")
        say("| layer | wells | measured As median of well medians (µg/L) | records > 10 µg/L | main measured redox classes | predicted As median (µg/L) by age: 100 / 1,000 / 10,000 / 40,000 yr | predicted redox at 100 yr / 40,000 yr |")
        say("|---|---|---|---|---|---|---|")
        for lc in ("1", "2", "3", "4"):
            m = per_well(lc, "As_aso")
            if not m: continue
            vals = [float(r["As_aso"]) for r in R if r["layercode"] == lc and r["As_aso"] != ""]
            pH = med(lc, "pH")
            cls_meas = Counter(r["redox_class"].replace(", O2 unknown", "").replace(" (O2 unknown)", "") for r in R if r["layercode"] == lc and r["redox_class"] != "incomplete")
            nm = sum(cls_meas.values())
            preds, redox = {}, {}
            for T in AGES:
                pv, rx = [], Counter()
                for fe, oc, kf, asd in itertools.product((3, 15), (0.1, 0.3, 0.9), (1, 0.1), (2, 5, 10)):
                    sed_age = 1e4 if lc == "1" else 3e4
                    teap, _ = LV.ladder_v2(dict(base, budT=T, aqFe=fe, ocSed=oc, kOC=0.16 * sed_age**-0.95 * kf))
                    kd = kd_as(pH, fe, "III", CLS[teap])
                    cw = 1000 * asd / (kd + 0.2 / 1.8)
                    pv.append(cw); rx[teap] += 1
                    rows.append({"zone": z, "layer": lc, "T_yr": T, "aqFe": fe, "ocSed": oc, "k_factor": kf, "As_sed": asd,
                                 "pH": f"{pH:.2f}", "teap": teap, "Kd": f"{kd:.3g}", "As_pred_ug_L": f"{cw:.3g}"})
                preds[T] = statistics.median(pv); redox[T] = rx
            mm = statistics.median(m) * 1000
            MEAS[(z, lc)] = {"base": base, "pH": pH, "meas": mm, "wells": len(m)}
            say(f"| {lc} | {len(m)} | {'0 (below detection?)' if mm == 0 else f'{mm:.3g}'} | {sum(1 for v in vals if v > 0.01) / len(vals):.0%} | "
                + (", ".join(f"{k} {v / nm:.0%}" for k, v in cls_meas.most_common(3)) if nm else "–") + " | "
                + " / ".join(f"{preds[T]:.3g}" for T in AGES) + " | "
                + ", ".join(f"{k} {v}" for k, v in redox[1e2].most_common(2)) + " / " + ", ".join(f"{k} {v}" for k, v in redox[4e4].most_common(2)) + " |")
    with open(P / "v2_districts.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    local(MEAS, say)
    (P / "v2_districts_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


LIT = ROOT / "data" / "literature"
NE_RHO = 0.2 / 1.8


def lanyang_paper_medians():
    """Median As (µg/L) of Liu & Wu (2019) Table 1 per aquifer; ND counted as 0; the all-ND sample w14-2 is skipped."""
    with open(LIT / "liu_wu_2019_lanyang_table1.csv", encoding="utf-8-sig", newline="") as fh:
        R = [r for r in csv.DictReader(fh) if r["pH"] != "ND"]
    out = {}
    for name, sel in (("aquifer 1 (<=70 m)", lambda d: d <= 70), ("aquifer 2 (>70 m)", lambda d: d > 70)):
        v = [0.0 if r["As_mg_L"] == "ND" else float(r["As_mg_L"]) for r in R if sel(float(r["depth_m"]))]
        out[name] = (statistics.median(v) * 1000, len(v), sum(1 for r in R if sel(float(r["depth_m"])) and r["As_mg_L"] == "ND"))
    return out


def local(MEAS, say):
    with open(LIT / "liu_wu_2019_lanyang_table5_sediment_As.csv", encoding="utf-8-sig", newline="") as fh:
        t5 = sorted(float(r["As_total_XRF_mg_kg"]) for r in csv.DictReader(fh))
    lan_as = (t5[0], statistics.median(t5), t5[-1])
    paper = lanyang_paper_medians()
    spec = {
        "濁水溪沖積扇": {"As": tuple(round(10 ** x, 2) for x in (0.69 - 0.29, 0.69, 0.69 + 0.29)),
                     "As_label": "total As in sand cores (H2O2 + HCl digestion), Liu et al. 2006 p. 70: 10^(0.69 ± 0.29) = 2.5 / 4.9 / 9.5 mg/kg (upper bound)",
                     "layers": {"1": ([40], 6e3), "2": ([4150, 18000], 2e4), "3": ([4150, 18000], 2e4), "4": ([4150, 18000], 2e4)}},
        "蘭陽平原": {"As": lan_as, "As_label": "total As, Liu & Wu 2019 Table 5: " + " / ".join(f"{a:g}" for a in lan_as) + " mg/kg (upper bound)",
                  "layers": {lc: (AGES, 1e4 if lc == "1" else 3e4) for lc in "1234"}},
    }
    out = []
    say("\n# Local runs with district literature values\n")
    say("See the script header for the sources. Predicted = median over Fe 3/15 g/kg, sediment OC 0.1/0.3/0.9 %, k factor 1/0.1 and the "
        "three sediment As values; 'reactive As needed' = measured median × (Kd + n_e/ρ_b), median over the same grid without As.\n")
    for z, sp in spec.items():
        say(f"\n## {z}\n\nSediment As: {sp['As_label']}\n")
        if z == "蘭陽平原":
            say("Liu & Wu (2019) Table 1 (p. 4), ND counted as 0: " + "; ".join(f"{k}: median {v[0]:.3g} µg/L (n = {v[1]}, {v[2]} ND)" for k, v in paper.items()) + "\n")
        say("| layer | T (yr) | sediment age (yr) | measured WRA median (µg/L) | predicted median (min–max) (µg/L) | predicted redox | reactive As needed to match WRA (mg/kg) |")
        say("|---|---|---|---|---|---|---|")
        for lc, (Ts, sed_age) in sp["layers"].items():
            if (z, lc) not in MEAS: continue
            M = MEAS[(z, lc)]
            for T in Ts:
                cw, kds, rx = [], [], Counter()
                for fe, oc, kf in itertools.product((3, 15), (0.1, 0.3, 0.9), (1, 0.1)):
                    teap, _ = LV.ladder_v2(dict(M["base"], budT=T, aqFe=fe, ocSed=oc, kOC=0.16 * sed_age**-0.95 * kf))
                    kd = kd_as(M["pH"], fe, "III", CLS[teap])
                    kds.append(kd); rx[teap] += 1
                    for asd in sp["As"]:
                        c = 1000 * asd / (kd + NE_RHO); cw.append(c)
                        out.append({"zone": z, "layer": lc, "T_yr": T, "sed_age_yr": sed_age, "aqFe": fe, "ocSed": oc, "k_factor": kf,
                                    "As_sed": f"{asd:g}", "teap": teap, "Kd": f"{kd:.3g}", "As_pred_ug_L": f"{c:.3g}"})
                need = statistics.median([M["meas"] / 1000 * (k + NE_RHO) for k in kds]) if M["meas"] > 0 else None
                meas_txt = "0 (below detection?)" if M["meas"] == 0 else f"{M['meas']:.3g}"
                say(f"| {lc} | {T:,.0f} | {sed_age:,.0f} | {meas_txt} | "
                    f"{statistics.median(cw):.3g} ({min(cw):.3g}–{max(cw):.3g}) | " + ", ".join(f"{k} {v}" for k, v in rx.most_common(2)) + " | "
                    + ("–" if need is None else f"{need:.2g} ({need / sp['As'][1]:.0%} of {sp['As'][1]:g})") + " |")
        if z == "蘭陽平原":
            say("")
            for name, lcs, (pm, n, nd) in (("aquifer 1", ["1"], paper["aquifer 1 (<=70 m)"]), ("aquifer 2", ["2", "3", "4"], paper["aquifer 2 (>70 m)"])):
                for lc in lcs:
                    if (z, lc) not in MEAS: continue
                    M = MEAS[(z, lc)]
                    for T in (1e3, 1e4):
                        kds = []
                        for fe, oc, kf in itertools.product((3, 15), (0.1, 0.3, 0.9), (1, 0.1)):
                            teap, _ = LV.ladder_v2(dict(M["base"], budT=T, aqFe=fe, ocSed=oc, kOC=0.16 * (1e4 if lc == "1" else 3e4)**-0.95 * kf))
                            kds.append(kd_as(M["pH"], fe, "III", CLS[teap]))
                        need = statistics.median([pm / 1000 * (k + NE_RHO) for k in kds])
                        say(f"- layer {lc}, T {T:,.0f} yr: reactive As needed to match Liu & Wu {name} median {pm:.3g} µg/L = {need:.2g} mg/kg "
                            f"({need / lan_as[1]:.0%} of the median total As {lan_as[1]:g} mg/kg)")
    with open(P / "v2_districts_local.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0])); wr.writeheader(); wr.writerows(out)


if __name__ == "__main__":
    main()
