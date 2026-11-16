"""Step 2c: Taiwan standards replace the Swiss LIM table.

Values (05_第一階段_資料可行性與試點計畫.md, section 1.3; units converted to µg/L for water):
  飲用水水質標準 (amended 2024-11-25) [S27]: As 0.01, Hg 0.001, Pb 0.01 mg/L
  地下水污染管制標準, values of the 2013-12-18 version [S28], unchanged by the 2025-12-23 amendment [S41]:
      class 1 (inside drinking-water source protection zones) As 0.050, Hg 0.0020, Pb 0.010 mg/L
      class 2 (all other groundwater)                          As 0.50,  Hg 0.020,  Pb 0.10 mg/L
  地下水污染監測標準 (2013-12-18) [S31]: half of the control standard for these metals
  土壤污染管制標準 / 土壤污染監測標準 (2011-01-31) [S32][S33], mg/kg, food-crop farmland in brackets:
      control    As 60, Hg 20 (5), Pb 2000 (500);  monitoring As 30, Hg 10 (2), Pb 1000 (300)
Not checked yet, so no comparison is made (the result says so):
  地面水體分類及水質標準, fully revised 2026-03-27 [S34]: metal values not read
  空氣品質標準 (amended 2024-09-30): values not read; deposition: no Taiwanese limit found
Taiwan has no standard for seepage water; seepage is compared with the groundwater control standard and labelled so.
"""
JS, IDX = "assets/js/app.js", "index.html"

LIM_NEW = r'''// Taiwan standards: water in µg/L, soil in mg/kg (sources in dev-tools/site_build/step_2c.py and the Taiwan standards table)
const LIM = {
  drink:{As:10, Hg:1, Pb:10},                                        // 飲用水水質標準, amended 2024-11-25
  gwCtl:{1:{As:50, Hg:2, Pb:10}, 2:{As:500, Hg:20, Pb:100}},          // 地下水污染管制標準 (2013 values, unchanged 2025-12-23)
  gwMon:{1:{As:25, Hg:1, Pb:5}, 2:{As:250, Hg:10, Pb:50}},            // 地下水污染監測標準: half of the control values
  soilCtl:{As:60, Hg:20, Pb:2000}, soilCtlFarm:{As:60, Hg:5, Pb:500}, // 土壤污染管制標準 (2011-01-31); food-crop farmland
  soilMon:{As:30, Hg:10, Pb:1000}, soilMonFarm:{As:30, Hg:2, Pb:300}, // 土壤污染監測標準 (2011-01-31); food-crop farmland
  surf:{},                                                           // 地面水體分類及水質標準 (revised 2026-03-27): not checked yet
  dep:{}                                                             // no Taiwanese deposition limit found
};
const gwClassOf = I => I.gwClass === "1" ? "1" : "2";'''

SOIL_NEW = r'''function soilStatus(m, Cs, land){
  const farm = land === "agri", ctl = (farm ? LIM.soilCtlFarm : LIM.soilCtl)[m], mon = (farm ? LIM.soilMonFarm : LIM.soilMon)[m];
  const use = farm ? " for food-crop farmland" : "";
  if(ctl && Cs > ctl) return ["crit","Exceeds control standard", `Soil pollution control standard${use}: ${ctl} mg/kg`];
  if(mon && Cs > mon) return ["warn","Above monitoring standard", `Soil pollution monitoring standard${use}: ${mon} mg/kg (control standard ${ctl} mg/kg)`];
  return ["ok","Below Taiwan standards", `Taiwan soil standards${use} (mg/kg): monitoring ${mon}, control ${ctl}`];
}'''

SOILLIM_NEW = r'''function soilLimFor(m, land){ return (land === "agri" ? LIM.soilCtlFarm : LIM.soilCtl)[m] || null; }'''

GWLIM_NEW = r'''  const gwc = gwClassOf(I), gwCtl = LIM.gwCtl[gwc][m], dwLim = LIM.drink[m], useDw = I.drink === "yes" && dwLim < gwCtl;
  const tbdv = useDw ? dwLim : gwCtl, limTag = useDw ? "drinking-water std" : `class ${gwc} control std`;
  const limRef = (useDw ? `Drinking-water standard ${dwLim} µg/L (the groundwater is used for drinking)` : `Groundwater pollution control standard, class ${gwc}: ${gwCtl} µg/L`) + `. Class ${gwc}: control ${gwCtl}, monitoring ${LIM.gwMon[gwc][m]} µg/L; drinking water ${dwLim} µg/L`;'''

SELFTEST_ADD = r'''
      { // TWD97 / TM2 121° against PROJ 9.8 (pyproj 3.8, EPSG:3826 → EPSG:4326)
        const ref = [[165347.06, 2586675.92, 23.380636543, 120.171896300], [330000, 2780000, 25.126281164, 121.793346557], [180000, 2450000, 22.147097050, 120.321355184]];
        let eF = 0, eI = 0;
        ref.forEach(([E, N, la, lo]) => { const p = wgsToTwd97(la, lo), q = twd97ToWgs(E, N); eF = Math.max(eF, Math.hypot(p.E - E, p.N - N)); eI = Math.max(eI, Math.hypot((q.lat - la) * 110574, (q.lng - lo) * 111320 * Math.cos(la * Math.PI / 180))); });
        ok("TWD97 coordinates match PROJ", eF < 0.01 && eI < 0.01, `largest difference ${(Math.max(eF, eI) * 1000).toFixed(2)} mm at 3 points`);
      }
      { INP = Object.assign(freshInputs("plateau"), {mapLim:"altl", gwClass:"1"}); const c1 = spreadLimit("As").v;
        INP.gwClass = "2"; const c2 = spreadLimit("As").v; INP = keepI;
        const farm = soilStatus("Pb", 600, "agri")[0], gen = soilStatus("Pb", 600, "garden")[0];
        ok("Taiwan standards follow groundwater class and farmland", c1 === 50 && c2 === 500 && farm === "crit" && gen === "ok", `As groundwater control class 1 ${c1}, class 2 ${c2} µg/L; Pb 600 mg/kg: farmland ${farm}, other land ${gen}`);
      }'''

LIMITS_HTML = r'''<section class="sec" id="limits">
    <div class="sec-head">
      <h2>Taiwan standards</h2>
      <p>Benchmarks a result is compared with. Check the current text on the Laws &amp; Regulations Database (law.moj.gov.tw) or the MOENV regulation system before using them in a report.</p>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Medium</th><th class="m-as">Arsenic</th><th class="m-hg">Mercury</th><th class="m-pb">Lead</th><th>Basis</th></tr></thead>
        <tbody>
          <tr><td>Drinking water, maximum</td><td class="num">0.01 mg/L</td><td class="num">0.001 mg/L</td><td class="num">0.01 mg/L</td><td class="basis"><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?PCODE=O0040019" target="_blank" rel="noopener">飲用水水質標準</a> (Drinking Water Quality Standards), amended 25 Nov 2024</td></tr>
          <tr><td>Groundwater, control standard, class 1<br><span class="note">inside drinking-water source protection zones</span></td><td class="num">0.050 mg/L</td><td class="num">0.0020 mg/L</td><td class="num">0.010 mg/L</td><td class="basis" rowspan="2"><a href="https://oaout.moenv.gov.tw/law/LawContent.aspx?id=FL015529" target="_blank" rel="noopener">地下水污染管制標準</a> (Groundwater Pollution Control Standards); values of the 18 Dec 2013 version, unchanged by the 23 Dec 2025 amendment</td></tr>
          <tr><td>Groundwater, control standard, class 2<br><span class="note">all other groundwater</span></td><td class="num">0.50 mg/L</td><td class="num">0.020 mg/L</td><td class="num">0.10 mg/L</td></tr>
          <tr><td>Groundwater, monitoring standard</td><td colspan="3">Half of the control standard for the same class (class 1: As 0.025, Hg 0.0010, Pb 0.005 mg/L)</td><td class="basis"><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=O0110013" target="_blank" rel="noopener">地下水污染監測標準</a> (Groundwater Pollution Monitoring Standards), 18 Dec 2013</td></tr>
          <tr><td>Soil, control standard</td><td class="num">60 mg/kg</td><td class="num">20 mg/kg<br><span class="note">food-crop farmland 5</span></td><td class="num">2000 mg/kg<br><span class="note">food-crop farmland 500</span></td><td class="basis"><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?PCODE=O0110005" target="_blank" rel="noopener">土壤污染管制標準</a> (Soil Pollution Control Standards), 31 Jan 2011</td></tr>
          <tr><td>Soil, monitoring standard</td><td class="num">30 mg/kg</td><td class="num">10 mg/kg<br><span class="note">food-crop farmland 2</span></td><td class="num">1000 mg/kg<br><span class="note">food-crop farmland 300</span></td><td class="basis"><a href="https://www.epb.taichung.gov.tw/media/520975/土壤污染監測標準.pdf" target="_blank" rel="noopener">土壤污染監測標準</a> (Soil Pollution Monitoring Standards), 31 Jan 2011</td></tr>
          <tr><td>Surface water</td><td colspan="3">Not yet checked here: the standard was fully revised on 27 Mar 2026 and its metal values have not been read</td><td class="basis"><a href="https://www.6laws.net/6law/law3/地面水體分類及水質標準.htm" target="_blank" rel="noopener">地面水體分類及水質標準</a></td></tr>
          <tr><td>Air</td><td colspan="3">Not yet checked here (Air Quality Standards, amended 30 Sep 2024). Results use the WHO guideline for Pb and Hg and the EU target value for As, labelled as such</td><td class="basis">空氣品質標準</td></tr>
          <tr><td>WHO drinking-water guideline</td><td class="num">10 µg/L</td><td class="num">6 µg/L<br><span class="note">inorganic Hg</span></td><td class="num">10 µg/L</td><td class="basis">WHO guidelines</td></tr>
          <tr><td>Dietary reference</td><td>No safe intake identified; margin-of-exposure approach</td><td>MeHg 1.3 µg/kg bw per week; inorganic Hg 4 µg/kg bw per week</td><td>No threshold; BMDL₀₁ 12 µg/L blood (child IQ)</td><td class="basis">EFSA (As 2024, Hg 2012, Pb 2010)</td></tr>
          <tr><td>Cancer classification</td><td>Group 1 (inorganic As)</td><td>Group 2B (methylmercury)</td><td>Group 2A (inorganic Pb)</td><td class="basis">IARC</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">Class 1 groundwater lies inside a drinking-water source protection zone; set the class in the Exposure tab. Taiwan has no standard for seepage water, so seepage leaving the topsoil is compared with the groundwater control standard as a screening reference. Taiwan also lists Cd, Cr, Cu, Ni and Zn; they will be added with those metals.</p>
  </section>'''

DATA_NEW = r'''const DATA = [
 ["MOENV regional groundwater quality","Quarterly samples from the regional monitoring wells (about 500 wells), with arsenic, metals, iron, manganese and the main ions. Also through the MOENV open-data API (data.moenv.gov.tw).","Aquifer chemistry","https://data.gov.tw/en/datasets/6348"],
 ["WRA groundwater quality by aquifer layer","Water Resources Agency samples from the layered observation wells, including As, Fe, Mn, sulfate, nitrate and organic carbon.","Redox and arsenic by depth","https://data.gov.tw/en/datasets/161086"],
 ["WRA groundwater observation wells","Well list with aquifer layer, depth and TWD97 coordinates; water-level statistics in dataset 32717.","Wells, layers, levels","https://data.gov.tw/en/datasets/32718"],
 ["GSMMA hydrogeological boreholes","Geological Survey and Mining Management Agency boreholes with lithology logs.","Aquifer material","https://data.gov.tw/en/datasets/16799"],
 ["Soil and groundwater pollution sites","Listed control and remediation sites with location and pollutants.","Known hotspots","https://data.gov.tw/en/datasets/6351"],
 ["Groundwater pollution control areas","Areas where groundwater use is restricted because of pollution.","Restricted groundwater","https://data.gov.tw/en/datasets/35092"],
 ["Detailed soil map","Ministry of Agriculture soil survey of agricultural land.","Soil properties","https://data.gov.tw/en/datasets/55747"],
 ["Tap water quality sampling","Monthly sampling of tap water quality.","Drinking water","https://data.gov.tw/en/datasets/139648"],
 ["NLSC map services","Base maps, orthophotos and national land-use tiles (WMTS), open data without application.","Base map, land use","https://maps.nlsc.gov.tw/S09SOA/pro/Wmts_ajax_main.jsp"]
];'''

PATCHES = [
    # ---------- LIM and the functions that read it ----------
    (JS, r"const LIM = \{\n  tbdv:.*?\n\};", LIM_NEW, {"regex": True}),
    (JS, r"function soilStatus\(m, Cs, land\)\{\n.*?\n\}", SOIL_NEW, {"regex": True}),
    (JS, r"function soilLimFor\(m, land\)\{\n.*?\n\}", SOILLIM_NEW, {"regex": True}),
    (JS, "  const tbdv = LIM.tbdv[m];\n", GWLIM_NEW + "\n"),
    (JS, '["crit","Exceeds TBDV"]', '["crit","Exceeds " + limTag]', {"count": 2}),
    (JS, '["ok","Below TBDV"]', '["ok","Below " + limTag]', {"count": 2}),
    (JS, "ref:`Drinking-water limit (TBDV) ${tbdv} µg/L · ${drinkTxt}`", "ref:`${limRef} · ${drinkTxt}`", {"count": 2}),
    # seepage water: no Taiwan standard; compared with the groundwater control standard
    (JS, "    const al = LIM.altl1[m];\n", "    const al = LIM.gwCtl[gwClassOf(I)][m];\n"),
    (JS, 'status: o.cw > al ? "crit" : "ok", tag: o.cw > al ? "Exceeds AltlV" : "Below AltlV",', 'status: o.cw > al ? "crit" : "ok", tag: o.cw > al ? "Above GW control std" : "Below GW control std",'),
    (JS, 'ref:`AltlV Annex 1 concentration value: ${al} µg/L` + (m === "As" ? " (10 µg/L proposed in 2024)" : "")',
     'ref:`No Taiwan standard for seepage water; compared with the groundwater pollution control standard, class ${gwClassOf(I)}: ${al} µg/L`'),
    # surface water: not checked yet
    (JS, "const g = LIM.gschv[m];", "const g = LIM.surf[m];", {"count": 2}),
    (JS, 'tag: g ? (o.rivD > g ? "Exceeds GSchV" : "Below GSchV") : "No GSchV value", ref: g ? `GSchV Annex 2: ${g} µg/L dissolved` : "No GSchV value for As"',
     'tag: g ? (o.rivD > g ? "Exceeds standard" : "Below standard") : "Taiwan value not checked", ref: g ? `Surface water standard: ${g} µg/L dissolved` : "Taiwan surface water standard (revised 27 Mar 2026) not yet checked here"'),
    (JS, 'const s = g ? (o.cD > g ? ["crit","Exceeds GSchV"] : ["ok","Below GSchV"]) : (o.cD > 10 ? ["warn","Above 10 µg/L"] : ["info","No GSchV value"]);',
     'const s = g ? (o.cD > g ? ["crit","Exceeds standard"] : ["ok","Below standard"]) : (o.cD > LIM.drink[m] ? ["warn","Above drinking-water std"] : ["info","Taiwan value not checked"]);'),
    (JS, 'ref: g ? `GSchV Annex 2: ${g} µg/L dissolved` : "No GSchV value for As; the drinking-water limit is 10 µg/L"',
     'ref: g ? `Surface water standard: ${g} µg/L dissolved` : `Taiwan surface water standard (revised 27 Mar 2026) not yet checked here; for comparison, the drinking-water standard is ${LIM.drink[m]} µg/L`'),
    # air
    (JS, "const sh = o.air, lv = LIM.lrvDep[m],", "const sh = o.air, lv = LIM.dep[m],"),
    (JS, ': "No LRV value",', ': "No deposition limit",'),
    (JS, "`The LRV sets no deposition limit for ${METALS[m].name.toLowerCase()}`", "`No Taiwanese deposition limit was found for ${METALS[m].name.toLowerCase()}`"),
    (JS, "how:`Single event; the LRV limit applies to annual means. ${within}`", "how:`Single event; air limits apply to annual means. ${within}`"),
    (JS, r"// air limits for comparison: LRV Pb in PM10;[^\n]*\nconst AIR_LIM = [^\n]*\n",
     "// air references until the Taiwan air quality standard is checked: WHO guidelines for Pb and inorganic Hg vapour, EU target value for As\n"
     'const AIR_LIM = {Pb:{v:500, txt:"WHO air quality guideline for Pb: 0.5 µg/m³, annual mean (WHO 2000); the Taiwan air quality standard is not yet checked here"}, '
     'As:{v:6, txt:"EU target value for As in PM10: 6 ng/m³; the Taiwan value is not yet checked here"}, '
     'Hg:{v:1000, txt:"WHO guideline for inorganic Hg vapour: 1 µg/m³, annual mean; the Taiwan value is not yet checked here"}};\n', {"regex": True}),
    (JS, '(m === "Pb" ? "Exceeds LRV" : "Above guideline")', '"Above guideline"'),
    (JS, '(m === "Pb" ? "Below LRV" : "Below guideline")', '"Below guideline"'),
    (JS, 'status: over ? "warn" : "ok", tag: over ? "Above LRV (background)" : "Below LRV",', 'status: "info", tag: "Info",'),
    (JS, "ref:`PM2.5 ${fmt(num(I.pm25))} µg/m³. LRV annual limits: PM10 20, PM2.5 10 µg/m³`, how:\"Annual mean 2023–2025 from the FOEN maps (map sites) before this release; it shows how much dust people here already breathe\"",
     "ref:`PM2.5 ${fmt(num(I.pm25))} µg/m³. The Taiwan air quality standard (amended 30 Sep 2024) is not yet checked here`, how:\"Annual mean at the site before this release; it shows how much dust people here already breathe\""),
    # spread map and soil deposition map
    (JS, 'function spreadLimit(m){ return INP.mapLim === "altl" ? {v:LIM.altl1[m], name:"AltlV concentration value"} : {v:LIM.tbdv[m], name:"drinking-water limit (TBDV)"}; }',
     'function spreadLimit(m){ return INP.mapLim === "altl" ? {v:LIM.gwCtl[gwClassOf(INP)][m], name:`groundwater pollution control standard (class ${gwClassOf(INP)})`} : {v:LIM.drink[m], name:"drinking-water standard"}; }'),
    (JS, r"  // the lowest Swiss soil value for this land use:[^\n]*\n  const g = LIM\.guide\[m\][^\n]*\n  const lim = g \|\| tr \|\| rv \|\| null, limName = [^\n]*?, forest = I\.land === \"forest\";",
     '  // the lowest Taiwan soil value for this land use: the soil pollution monitoring standard (food-crop farmland values for agriculture)\n'
     '  const lim = (I.land === "agri" ? LIM.soilMonFarm : LIM.soilMon)[m] || null, limName = I.land === "agri" ? "soil monitoring standard for food-crop farmland" : "soil monitoring standard", forest = I.land === "forest";',
     {"regex": True}),
    (JS, 'exceeds"} a Swiss limit or health reference point.`', 'exceeds"} a Taiwan standard or health reference point.`'),
    # suggestions
    (JS, '"Excavate and dispose of soil above the AltlV remediation value, or restrict its use for gardens, playgrounds and crops."',
     '"Excavate or contain soil above the soil pollution control standard, or restrict its use for gardens, playgrounds and crops."'),
    (JS, '"Stop further input and check use restrictions: the soil is above a VBBo guide or trigger value."',
     '"Stop further input and check use restrictions: the soil is above the soil pollution monitoring standard."'),
    # exports
    (JS, 'const lim = (I.drink === "yes" ? LIM.tbdv : LIM.altl1)[m];', 'const lim = I.drink === "yes" ? LIM.drink[m] : LIM.gwCtl[gwClassOf(I)][m];'),
    (JS, '${I.drink === "yes" ? "drinking-water limit (TBDV)" : "AltlV Annex 1 concentration value"}',
     '${I.drink === "yes" ? "Taiwan drinking-water standard" : "Taiwan groundwater pollution control standard, class " + gwClassOf(I)}'),
    # new input: groundwater class
    (JS, '  {k:"drink", tab:"exp", label:"Groundwater used for drinking", type:"select", opts:[["yes","Yes"],["no","No"]]},\n',
     '  {k:"drink", tab:"exp", label:"Groundwater used for drinking", type:"select", opts:[["yes","Yes"],["no","No"]]},\n'
     '  {k:"gwClass", tab:"exp", label:"Groundwater class (Taiwan)", type:"select", opts:[["2","Class 2: outside drinking-water source protection zones"],["1","Class 1: inside a drinking-water source protection zone"]], src:"Groundwater Pollution Control Standards"},\n'),
    (JS, 'land:"garden", drink:"yes", bw:10,', 'land:"garden", drink:"yes", gwClass:"2", bw:10,'),
    # self-test
    (JS, 'ok("Error function matches reference values", e < 2e-7, `largest error ${e.toExponential(1)} (method limit 1.5e-7)`);',
     'ok("Error function matches reference values", e < 2e-7, `largest error ${e.toExponential(1)} (method limit 1.5e-7)`);' + SELFTEST_ADD),
    # data sources shown on the page
    (JS, r"const DATA = \[\n.*?\n\];", DATA_NEW, {"regex": True}),
    # ---------- index.html ----------
    (IDX, '<a href="#limits">Swiss reference values</a><a href="#data">Swiss data to connect</a>', '<a href="#limits">Taiwan standards</a><a href="#data">Taiwan data to connect</a>'),
    (IDX, r'<section class="sec" id="limits">.*?</section>', LIMITS_HTML, {"regex": True}),
    (IDX, "<h2>Swiss data to connect</h2>", "<h2>Taiwan data to connect</h2>"),
    (IDX, "<p>Open federal datasets that can fill inputs from a coordinate in LV95 (EPSG:2056). The map in Advanced mode already uses MeteoSwiss climate normals, KOBO soil maps, the geochemical soil atlas, the hydrogeological map and BFS land-use statistics.</p>",
     "<p>Open government datasets (Open Government Data License, version 1.0) that the Taiwan version uses or will use. Coordinates are TWD97 (EPSG:3826).</p>"),
    (IDX, "exposure checks against Swiss values", "exposure checks against Taiwan standards"),
    (IDX, '<li class="now"><b>Automatic site lookup</b><span>Map click fills precipitation, soil pH, organic carbon, aquifer type, land use and background values from Swiss national datasets (1 km grid).</span></li>',
     '<li class="now"><b>Taiwan data grid</b><span>Map click to fill precipitation, soil, aquifer layers, land use and background values from Taiwan open data (planned 1 km grid; for now the map sets the source location).</span></li>'),
    (IDX, "Red marks where the metal is above the Swiss standard", "Red marks where the metal is above the chosen Taiwan standard"),
    (IDX, "Source area: red or amber if the topsoil is above a Swiss value", "Source area: red or amber if the topsoil is above a Taiwan soil standard"),
    (IDX, '<option value="tbdv">Drinking-water limit (TBDV)</option><option value="altl">AltlV concentration value (Annex 1)</option>',
     '<option value="tbdv">Drinking-water standard</option><option value="altl">Groundwater control standard (class from the Exposure tab)</option>'),
    # leftover Swiss wording in the summary
    (JS, 'mg/kg over ${area}, below Swiss soil values.`', 'mg/kg over ${area}, below the Taiwan soil standards.`'),
]
