"""Step 4 (part 1): Taiwan geography. Runs after step_cr.py.

- Glacier melt is no longer offered as a release type (Taiwan has no glaciers; decision of 16 Nov 2026). The code stays,
  so the selfTest can still check it, but saved inputs with medium "glacier" fall back to soil (sanitize() keeps only
  menu values).
- Chianan groundwater Hg and Pb background set to 0 (decision of 16 Nov 2026): MOENV regional groundwater monitoring
  (WQX_P_02), 94 wells in the Chianan plain, 2014-2025: Hg 1,805 of 1,809 samples below 0.0003 mg/L, Pb 1,561 of
  1,809 below 0.003 mg/L (data/processed/moenv_long_clean.csv). The value in step_2f.py is 0; the source note says so.
- Every background set to 0 because the samples are below detection now says so in the source note.
Planned in this step: downstream reservoir or sea, coastal effects (see 14_沿海與海洋設計.md).
"""
JS = "assets/js/app.js"

PATCHES = [
    (JS, '[["gw","Groundwater, directly"],["river","River"]].concat(["As","Hg","Pb"].includes(m) ? [["glacier","Glacier melt (old deposition)"]] : [])',
         '[["gw","Groundwater, directly"],["river","River"]]'),
    (JS, '  if(INP.medium === "glacier" && !["As","Hg","Pb"].includes(S.metal)) INP.medium = "soil";', '  if(INP.medium === "glacier") INP.medium = "soil";'),
    # spread map: well layers in the support-layer drawer (drawn by step_wells.py)
    ("index.html", '<p class="mini">Taiwan layers are being added: drinking-water source protection zones, groundwater pollution control sites, the arsenic potential areas and geology (step 2e). The Swiss layers of the original site do not apply here.</p>', '<p class="mini">Wells, air stations and protection zones are available. Still to come: groundwater pollution control sites, the arsenic potential areas and geology (step 2e).</p>\n                <label><input type="checkbox" data-ov="wellsM" autocomplete="off"><span>MOENV groundwater monitoring wells <small>red: median of the selected metal above the drinking-water standard; click a well for its values</small></span></label>\n                <label><input type="checkbox" data-ov="wellsR" autocomplete="off"><span>WRA observation wells, layer 1 <small>colour: redox class; click a well for chloride</small></span></label>\n'
          '                <label><input type="checkbox" data-ov="air" autocomplete="off"><span>MOENV air-quality stations <small>PM10 and PM2.5, mean of complete years 2023–2025; grey: traffic stations</small></span></label>\n'
          '                <label><input type="checkbox" data-ov="pz" autocomplete="off"><span>Drinking-water source protection zones <small>blue: protection zone (groundwater class 1); dashed purple: set distance around an intake</small></span></label>'),
    ("index.html", "<small>Taiwan layers in preparation</small>", "<small>Wells, air stations, protection zones</small>"),
    # salty groundwater: chloride input and the Cd free-ion correction of the aquifer Kd
    (JS, 'const BASE = {preset:"chianan", assumed:[], ', 'const BASE = {preset:"chianan", assumed:[], gwCl:"", '),
    (JS, '  {k:"gwpH", tab:"gw", label:"Groundwater pH", unit:"–", min:3, max:11, src:"MOENV and WRA groundwater monitoring"},',
         '  {k:"gwpH", tab:"gw", label:"Groundwater pH", unit:"–", min:3, max:11, src:"MOENV and WRA groundwater monitoring"},\n'
         '  {k:"gwCl", tab:"gw", label:"Chloride in groundwater", unit:"mg/L", min:0, max:30000, optional:true, help:"Seawater intrusion raises chloride. Cadmium forms chloride complexes and binds less: its aquifer Kd is scaled by the free Cd²⁺ fraction (constants from minteq.v4.dat, checked against PHREEQC). Empty: no correction. Standard seawater holds about 19,350 mg chloride per kg (Pawlowicz 2010, Ocean Sci. 6:361, Table 3).", src:"MOENV and WRA groundwater monitoring"},'),
    (JS, '  o.kdAqCalc = kdFn(m, {pH:I.gwpH, oc:I.aqOC, fe:I.aqFe, sp, redox:I.redox});', '  o.kdAqCalc = kdFn(m, {pH:I.gwpH, oc:I.aqOC, fe:I.aqFe, sp, redox:I.redox, cl:num(I.gwCl) || 0});'),
    (JS, '    lg = clamp(lg, Math.log10(0.44), Math.log10(192000));\n',
         '    lg = clamp(lg, Math.log10(0.44), Math.log10(192000));\n    if(p.cl > 0) lg += Math.log10(cdClFactor(p.cl));   // salty groundwater (step_coast.py)\n'),
    (JS, "function kdFn(m, p){",
         "// free Cd2+ fraction relative to chloride-free water: CdCl+, CdCl2, CdCl3- (minteq.v4.dat), Davies activities at I = 0.01 + [Cl]\n"
         "function cdClFactor(clMg){\n"
         "  const c = clMg / 35453, I = 0.01 + c, dav = z => Math.pow(10, -0.509 * z * z * (Math.sqrt(I) / (1 + Math.sqrt(I)) - 0.3 * I));\n"
         "  const gM = dav(2), gCl = dav(1), B = [[1.98, 1], [2.6, 0], [2.4, 1]];\n"
         "  let s = 0; B.forEach(([lk, z], i) => { s += Math.pow(10, lk) * gM * Math.pow(gCl, i + 1) / dav(z) * Math.pow(c, i + 1); });\n"
         "  return 1 / (1 + s);\n}\nfunction kdFn(m, p){"),
    (JS, '      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",',
         '      ok("Cd aquifer Kd with 12,350 mg/L chloride is about 0.05 of the chloride-free value (PHREEQC check: 0.044)", Math.abs(kdFn("Cd", {pH:7, cl:12350}) / kdFn("Cd", {pH:7}) - 0.051) < 0.002, "free-ion fraction");\n'
         '      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",'),
]

BD = " (below detection, not a measured zero)"


def build(F):
    s = F.get(JS)
    a = 'Cr:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: total Cr 1,714 of 1,809 samples below 0.001 mg/L, so 0 used"},'
    if a not in s:
        raise SystemExit("[step_coast] groundwater source anchor missing")
    s = s.replace(a, a[:-2] + ', Hg:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: 1,805 of 1,809 samples below 0.0003 mg/L, so 0 used", '
                  'Pb:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: 1,561 of 1,809 samples below 0.003 mg/L, so 0 used"},', 1)
    n = s.count(', so 0 used"')
    if n < 7:
        raise SystemExit(f"[step_coast] expected at least 7 'so 0 used' notes, found {n}")
    s = s.replace(', so 0 used"', ', so 0 used' + BD + '"')
    F.put(JS, s)
