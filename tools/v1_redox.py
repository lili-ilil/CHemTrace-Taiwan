#!/usr/bin/env python3
"""V1: compare the CHemTrace redox ladder with the redox process inferred from measured groundwater chemistry.

Usage (from the CHemTrace-TW folder; needs Node.js for the ladder):
    python tools/v1_redox.py --design A

Design A (consistency check): the ladder gets the measured dissolved O2, nitrate, sulfate and TOC of the same sample
(TOC stands in for DOC). Everything else is the website default (BASE + the 'plateau' preset of the Swiss site 0.13.0,
read from base/docs/assets/js/app.js by tools/ladder_node.mjs). The result is compared with the process inferred from
the same sample's Mn and Fe (not ladder inputs) together with O2, nitrate and sulfate, using the framework below.
This is partly circular (low measured O2 and nitrate push both towards reducing); see 06_V1_氧化還原驗證設計.md.

Measured redox process: McMahon & Chapelle (2008), Ground Water 46(2): 259-271, Table 1 (p. 262): thresholds in mg/L,
O2 0.5, NO3-N 0.5, Mn 0.05, Fe 0.1, SO4 0.5; mixed classes as in Jurgens et al. (2009), USGS OFR 2009-1004, Table 2.
Without sulfide data, Fe(III) and sulfate reduction stay one class (Fe(III)/SO4), as in McMahon & Chapelle (2008).
The MOENV data do not say whether Fe and Mn were filtered; Jurgens et al. (2009, p. 3) note that total dissolved Mn and
Fe estimate Mn2+ and Fe2+ well in filtered, acidified samples.
A value below its detection limit counts as below a threshold only if the detection limit is at or below the
threshold; otherwise that indicator is undetermined.

Inputs: data/processed/moenv_samples_all.csv (tools/process_moenv_wells.py).
Outputs: data/processed/v1<design>_samples.csv and v1<design>_summary.md.
"""
import argparse, csv, json, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
TH = {"DO": 0.5, "NO3N": 0.5, "Mn": 0.05, "Fe": 0.1, "SO4": 0.5}     # McMahon & Chapelle (2008) Table 1, mg/L
N_TO_NO3 = 62.004 / 14.007                                           # mg NO3 per mg NO3-N
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def flag(row, c):
    """True if >= threshold, False if below, None if missing or undetermined."""
    v, q = row.get(c, ""), row.get(c + "_q", "")
    if v == "":
        return None
    x = float(v)
    if q == "<":
        return False if x <= TH[c] else None
    return x >= TH[c]


def measured_process(row):
    """Return (category, process, processes set) following McMahon & Chapelle (2008) / Jurgens et al. (2009)."""
    O, N, M, F, S = (flag(row, c) for c in ("DO", "NO3N", "Mn", "Fe", "SO4"))
    if None in (O, N, M, F):
        return "incomplete", "", set()
    if F:
        anox = "Fe(III)/SO4" if S else ("CH4gen" if S is False else "Fe(III)/SO4 or CH4gen")
        procs = {"Fe(III)/SO4"} if S else ({"CH4gen"} if S is False else {"Fe(III)/SO4", "CH4gen"})
        if O and N:
            return "mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2)", f"O2-NO3-{anox}", {"O2", "NO3"} | procs
        if O:
            return "mixed(oxic-anoxic)", f"O2-{anox}", {"O2"} | procs
        if N:
            return "mixed(anoxic)", f"NO3-{anox}", {"NO3"} | procs
        return "anoxic", anox, procs
    if M:
        if O:
            return "mixed(oxic-anoxic)", "O2-Mn(IV)", {"O2", "Mn(IV)"}
        if N:
            return "mixed(anoxic)", "NO3-Mn(IV)", {"NO3", "Mn(IV)"}
        return "anoxic", "Mn(IV)", {"Mn(IV)"}
    if O:
        return "oxic", "O2", {"O2"}
    if N:
        return "anoxic", "NO3", {"NO3"}
    return "suboxic", "suboxic", {"suboxic"}


TEAP2PROC = {"o2": "O2", "no3": "NO3", "mn": "Mn(IV)", "fe": "Fe(III)/SO4", "so4": "Fe(III)/SO4", "ch4": "CH4gen"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default="A", choices=["A"])
    ap.add_argument("--samples", default=str(P / "moenv_samples_all.csv"))
    ap.add_argument("--budT", type=float, default=None, help="sensitivity run: ladder time horizon in years (website default 1)")
    a = ap.parse_args()
    with open(a.samples, encoding="utf-8-sig", newline="") as fh:
        S = list(csv.DictReader(fh))
    # ---- ladder inputs (design A): measured values of the same sample
    runs, keep = [], []
    for i, r in enumerate(S):
        if not all(r[c] != "" for c in ("DO", "NO3N", "SO4", "TOC")):
            continue
        val = lambda c: 0.0 if r[c + "_q"] == "<" else float(r[c])   # below detection -> 0 for the electron balance
        runs.append({"id": i, "preset": "plateau", "inputs": {"o2In": val("DO"), "no3In": val("NO3N") * N_TO_NO3,
                                                              "so4In": val("SO4"), "docIn": val("TOC"), "orgType": "none",
                                                              **({"budT": a.budT} if a.budT else {})}})
        keep.append(i)
    res = subprocess.run(["node", str(ROOT / "tools" / "ladder_node.mjs")], input=json.dumps(runs), capture_output=True,
                         text=True, encoding="utf-8")
    if res.returncode:
        sys.exit("ladder_node.mjs failed:\n" + res.stderr)
    out = {o["id"]: o for o in json.loads(res.stdout)}
    used = next(iter(out.values()))["used"] if out else {}

    # ---- compare
    rows = []
    for i in keep:
        r, o = S[i], out[i]
        cat, proc, procs = measured_process(r)
        mp = TEAP2PROC[o["teap"]]
        if cat == "incomplete":
            agree = ""
        elif procs == {"suboxic"}:
            agree = "n/a (measured suboxic)"
        else:
            agree = "yes" if mp in procs else "no"
        rows.append({"siteid": r["siteid"], "sitename": r["sitename"], "ugwdistname": r["ugwdistname"], "date": r["date"],
                     "DO": r["DO"], "NO3N": r["NO3N"] + r["NO3N_q"], "Mn": r["Mn"] + r["Mn_q"], "Fe": r["Fe"] + r["Fe_q"],
                     "SO4": r["SO4"] + r["SO4_q"], "TOC": r["TOC"] + r["TOC_q"], "ORP": r["ORP"], "NH3N": r["NH3N"] + r["NH3N_q"],
                     "As": r["As"] + r["As_q"], "measured_category": cat, "measured_process": proc,
                     "ladder_teap": o["teap"], "ladder_class": o["cls"], "ladder_process": mp, "agree": agree,
                     "s1_mmol_e_per_L": f"{o['s1']:.3g}", "s2_mmol_e_per_L": f"{o['s2']:.3g}"})
    tag = a.design.lower() + (f"_budT{a.budT:g}" if a.budT else "")
    with open(P / f"v1{tag}_samples.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

    # ---- summary
    L = []; say = L.append
    say(f"# V1 design {a.design}{f' (sensitivity: budT = {a.budT:g} years)' if a.budT else ''}: redox ladder vs measured redox process\n")
    say(f"Made {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by tools/v1_redox.py. Ladder: redoxLadder from "
        f"base/docs/assets/js/app.js (CHemTrace 0.13.0), run by tools/ladder_node.mjs.\n")
    say(f"Samples with DO, NO3-N, SO4 and TOC: {len(rows)} (of {len(S)}). Website defaults used for the other ladder inputs: "
        + ", ".join(f"{k} {v}" for k, v in used.items()) + " (BASE + preset 'plateau').\n")
    def table(sel, title):
        rs = [x for x in rows if sel(x)]
        say(f"\n## {title} ({len(rs)} samples, {len({x['siteid'] for x in rs})} wells)\n")
        mc = Counter(x["measured_category"] for x in rs)
        say("Measured category: " + ", ".join(f"{k} {v} ({v / len(rs):.0%})" for k, v in mc.most_common()))
        lc = Counter(x["ladder_teap"] for x in rs)
        say("\nLadder TEAP: " + ", ".join(f"{k} {v} ({v / len(rs):.0%})" for k, v in lc.most_common()))
        cmp_ = [x for x in rs if x["agree"] in ("yes", "no")]
        if cmp_:
            ya = sum(1 for x in cmp_ if x["agree"] == "yes")
            say(f"\nAgreement (ladder process is one of the measured processes): {ya} of {len(cmp_)} ({ya / len(cmp_):.0%}); "
                f"not compared: {len(rs) - len(cmp_)} (measured suboxic or incomplete)")
        ct = defaultdict(Counter)
        for x in rs: ct[x["measured_process"]][x["ladder_process"]] += 1
        cols = ["O2", "NO3", "Mn(IV)", "Fe(III)/SO4", "CH4gen"]
        say("\n| measured process \\ ladder | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols))
        for k, c in sorted(ct.items(), key=lambda kv: -sum(kv[1].values())):
            say(f"| {k or '(incomplete)'} | " + " | ".join(str(c.get(cc, 0)) for cc in cols) + " |")
    table(lambda x: True, "All districts")
    table(lambda x: x["ugwdistname"] == "嘉南平原", "嘉南平原")
    for z in ("濁水溪沖積扇", "屏東平原", "蘭陽平原"):
        table(lambda x, z=z: x["ugwdistname"] == z, z)
    say("\n## Notes\n")
    say("- Ladder processes are mapped as o2→O2, no3→NO3, mn→Mn(IV), fe and so4→Fe(III)/SO4, ch4→CH4gen, because the measured "
        "framework cannot separate Fe(III) and sulfate reduction without sulfide.")
    say("- 'suboxic' means different things: in McMahon & Chapelle (2008) low O2 and low nitrate with Mn and Fe below "
        "threshold (process not defined); in the ladder, nitrate reduction. Measured suboxic samples are not scored.")
    say("- Values below detection enter the ladder as 0.")
    (P / f"v1{tag}_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
