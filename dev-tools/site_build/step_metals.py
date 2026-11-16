"""Step 3 (part 0): metal list made generic, so that Cd, Ni and Cr can be added (13_新增金屬計畫_Cd_Cr_Ni.md).
Also: the PHREEQC batch export picks the added compound from a per-metal table (it used H3AsO3 for any other metal).

The two places that listed As, Hg and Pb by hand now use the keys of METALS; the English pages accept any element
symbol for their colour. Results for As, Hg and Pb must stay identical: dev-tools/tests/t_regress.js compares them.
"""
JS = "assets/js/app.js"

PATCHES = [
    (JS, 'if(v && typeof v === "object") ["As","Hg","Pb"].forEach(mm => {', 'if(v && typeof v === "object") Object.keys(METALS).forEach(mm => {'),
    (JS, 'for(const m of ["As", "Hg", "Pb"]) for(const medium of ["soil", "air", "gw", "river"])', 'for(const m of Object.keys(METALS)) for(const medium of ["soil", "air", "gw", "river"])'),
    # PHREEQC batch export: the added compound fell through to H3AsO3 for any metal other than Pb and Hg.
    # New metals are added as a neutral salt, as Pb is added as PbCO3 (a modelling choice, not a measured value).
    (JS, '  const salt = m === "Pb" ? "PbCO3" : m === "Hg" ? "Hg(OH)2" : !asV ? "H3AsO3" : "sodium arsenate (NaH2AsO4 and Na2HAsO4 in the ratio of their species at this pH)";',
         '  const RX = {Pb:"PbCO3", Hg:"Hg(OH)2", Cd:"CdCO3", Ni:"NiCO3", Cr:c.form.sp === "VI" ? "Na2CrO4" : "Cr(OH)3"}, rx = RX[m] || "H3AsO3";\n'
         '  const salt = !asV ? rx : "sodium arsenate (NaH2AsO4 and Na2HAsO4 in the ratio of their species at this pH)";'),
    (JS, '  else L.push(`    ${m === "Pb" ? "PbCO3" : m === "Hg" ? "Hg(OH)2" : "H3AsO3"}   1`);', '  else L.push(`    ${rx}   1`);'),
]
for _p in ("manual.html", "validation.html", "assumptions.html"):
    PATCHES.append((_p, 'if(m === "Hg" || m === "Pb" || m === "As") document.documentElement.setAttribute("data-metal", m);',
                    'if(/^[A-Z][a-z]?$/.test(m || "")) document.documentElement.setAttribute("data-metal", m);'))
