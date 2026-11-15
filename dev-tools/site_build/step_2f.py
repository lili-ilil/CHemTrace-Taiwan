"""Step 2f (part 1): Taiwan site presets, starting with the Chianan plain (嘉南平原).

Decision of 15 Nov 2026: a value without a Taiwan source keeps the model's generic default and is marked ASSUMED in the
form and in the report, so the model still runs and the user sees what to replace.

- PRESETS.chianan: every value has an entry in src, or it is ASSUMED (generic default, taken from the Swiss Plateau preset).
- The four Swiss presets stay in the code, hidden from the menu, because the self-test uses them as numerical fixtures.
- INP.assumed lists the inputs that still carry an ASSUMED preset value ("key" or "key.Metal" for per-metal inputs);
  editing an input removes it from the list. The form shows the source or an ASSUMED badge; the report lists them.
Sources: 05, 06, 08, 10 files and data/processed (see the src texts below). Values derived here from data/processed:
  wt   3.8 m  = median over 63 WRA layer-1 wells of (ground height − mean annual water level), 1994–2025 (wra_level_wells.csv,
              wra_wells.csv); assumes the level field is an elevation (noted in 08)
  elev 6 m    = median ground height of the WRA wells in the plain, 5.9 m over 159 wells (44 wells listed as 0 m left out)
  pH, drain, ssc, bgRiv.As, pm10, pm25 = tools/process_chianan_extra.py (data/processed/chianan_extra_summary.md)
  lakeTau 0  = decision of 15 Nov 2026 (no lake downstream). The lake inputs still feed the Hg methylation index and stay ASSUMED.
  gwpH 7.2, bgGw As 50 µg/L = medians of the per-well medians, WRA 161086, layer 1, 54 wells, 1993–2025
"""
JS, CSS = "assets/js/app.js", "assets/css/styles.css"

CHIANAN = r'''  chianan:{label:"Chianan plain (嘉南平原), coastal", note:"Chianan plain: thick clay, silt and fine-sand deposits; shallow, reducing groundwater with naturally high arsenic in the deeper aquifers.",
    v:{precip:1000, infil:40, pH:7.0, oc:2, fe:4, pstat:"normal", drain:"well", rhob:1.3, theta:0.3, bg:{As:8,Hg:0.1,Pb:30},
       aq:"porous", wt:3.8, K:3.14e-5, grad:5e-4, thick:15, ne:0.25, gwpH:7.2, redox:"anoxic", aqFe:3, aqOC:0.3, bgGw:{As:50,Hg:0.005,Pb:0.3},
       Q:10, ssc:19.6, bgRiv:{As:6.75,Hg:0.002,Pb:0.2}, lakeO2:"seasonal", doc:3, lpH:8.2, so4:"mod", wet:"some", lakeTau:0, troph:"meso", elev:6, pm10:36.2, pm25:16.7},
    src:{precip:"Chen & Liu (2007) TAO 18:975, p. 983: annual rainfall about 1,000 mm",
       aq:"Chen & Liu (2007) p. 977: unconsolidated clay, silt and fine sand",
       wt:"WRA observation wells, layer 1 (data.gov.tw 32717, 32718): median depth 3.8 m over 63 wells, 1994–2025",
       K:"Lu et al. (2008) Hydrogeol. J. 16:139: 3.14×10⁻⁵ to 1.80×10⁻⁴ m/s for the fine-sand aquifer (lower end used; pumping tests about ten times lower)",
       grad:"Plane fit to WRA annual mean water levels, layers 1–4: about 4–6 × 10⁻⁴ towards the west (08 file)",
       ne:"Liu (1995) Radiocarbon 37:531, p. 540: 25 ± 5%, for the neighbouring Choushui fan (borrowed)",
       gwpH:"WRA groundwater quality (data.gov.tw 161086), layer 1: median of 54 wells 7.2, 1993–2025",
       redox:"WRA 161086, layer 1: most complete samples are Fe(III) reducing (06 file)",
       aqFe:"Chen & Liu (2007) Fig. 9d, p. 989: extractable Fe about 3–15 g/kg, read from the figure (lower end used)",
       aqOC:"Chen & Liu (2007) Fig. 9b, p. 989: sediment organic carbon about 0–0.9%, read from the figure",
       bgGw:{As:"WRA 161086, layer 1: median of 54 wells 0.05 mg/L (the deeper layers 0.10–0.12 mg/L)"},
       elev:"WRA observation wells in the plain (data.gov.tw 32718): median ground height 5.9 m",
       pH:"MOA detailed soil map (2016), plain of Chiayi and Tainan (slope 0–5 %): area-weighted median topsoil pH class 6.6–7.3, class midpoint used; classes range from below 5.5 to above 7.9",
       drain:"MOA detailed soil map (2016): 91 % of the plain area well drained",
       ssc:"MOENV river water quality (WQX_P_01), Chiayi and Tainan, 2021–2025: median suspended solids of 69 stations",
       bgRiv:{As:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: median total As of 45 stations (total, so an upper bound for dissolved)"},
       lakeTau:"No lake downstream: the rivers of the plain flow into the Taiwan Strait (decision of 15 Nov 2026)",
       pm10:"MOENV air quality monthly values (AQX_P_08), stations Puzi, Xingang, Chiayi, Xinying: median of the station means of 2023 and 2025 (2024 lacks August)",
       pm25:"MOENV AQX_P_08, same stations and years as PM10"}},
'''

ASSUMED_FN = r'''// inputs whose preset value has no Taiwan source ("key", or "key.Metal" for per-metal inputs)
function assumedOf(pid){
  const p = PRESETS[pid]; if(!p) return [];
  const src = p.src || {}, out = [];
  for(const [k, v] of Object.entries(p.v)){
    if(v && typeof v === "object") Object.keys(v).forEach(mm => { if(!(src[k] && src[k][mm])) out.push(k + "." + mm); });
    else if(!src[k]) out.push(k);
  }
  return out;
}
function presetSrc(k){
  const p = PRESETS[INP.preset]; if(!p || !p.src) return "";
  const s = p.src[k]; return s && typeof s === "object" ? (s[S.metal] || "") : (s || "");
}
const isAssumed = k => Array.isArray(INP.assumed) && (INP.assumed.includes(k) || INP.assumed.includes(k + "." + S.metal));
function freshInputs(pid){ return Object.assign(clone(BASE), clone(PRESETS[pid].v), {preset:pid, assumed:assumedOf(pid)}); }'''

PATCHES = [
    # the Chianan preset first; the Swiss presets stay as hidden test fixtures
    (JS, "const PRESETS = {\n", "const PRESETS = {\n" + CHIANAN),
    (JS, '  visp:{label:"Visp, Rhone valley (VS)",', '  visp:{hidden:true, label:"Visp, Rhone valley (VS)",'),
    (JS, '  plateau:{label:"Swiss Plateau gravel plain",', '  plateau:{hidden:true, label:"Swiss Plateau gravel plain",'),
    (JS, '  jura:{label:"Jura karst",', '  jura:{hidden:true, label:"Jura karst",'),
    (JS, '  ticino:{label:"Ticino crystalline valley",', '  ticino:{hidden:true, label:"Ticino crystalline valley",'),
    (JS, 'const BASE = {preset:"plateau",', 'const BASE = {preset:"chianan", assumed:[],'),
    (JS, "function freshInputs(pid){ return Object.assign(clone(BASE), clone(PRESETS[pid].v), {preset:pid}); }", ASSUMED_FN),
    (JS, 'const out = freshInputs(src && PRESETS[src.preset] ? src.preset : "plateau");', 'const out = freshInputs(src && PRESETS[src.preset] ? src.preset : "chianan");'),
    (JS, '  if(src.preset === "custom") out.preset = "custom";\n',
     '  if(src.preset === "custom") out.preset = "custom";\n'
     '  if(Array.isArray(src.assumed)) out.assumed = src.assumed.filter(k => typeof k === "string").slice(0, 80);\n'),
    # examples: Taiwan preset; the Swiss place name dropped
    (JS, 'As:{short:"mine-dump seepage", preset:"ticino",', 'As:{short:"mine-dump seepage", preset:"chianan",'),
    (JS, 'Hg:{short:"Visp garden", preset:"visp",', 'Hg:{short:"garden on Hg-rich sediment", preset:"chianan",'),
    (JS, 'Pb:{short:"shooting range", preset:"plateau",', 'Pb:{short:"shooting range", preset:"chianan",'),
    # preset menu without the hidden presets; applying a preset resets the ASSUMED list; editing removes an input from it
    (JS, '$("#presetSel").innerHTML = Object.entries(PRESETS).map(', '$("#presetSel").innerHTML = Object.entries(PRESETS).filter(([, p]) => !p.hidden).map('),
    (JS, '`<option value="${id}">${esc(p.label)}</option>`).join("") + `<option value="custom">Custom values</option>`;',
     '`<option value="${id}">${esc(tr(p.label))}</option>`).join("") + `<option value="custom">${tr("Custom values")}</option>`;'),
    (JS, 'Object.assign(INP, clone(PRESETS[id].v), {preset:id, siteName:"", srcE:"", srcN:""}); renderForm();',
     'Object.assign(INP, clone(PRESETS[id].v), {preset:id, siteName:"", srcE:"", srcN:"", assumed:assumedOf(id)}); renderForm();'),
    (JS, 'function markCustom(k){\n  if(!SITE_KEYS.has(k) || INP.preset === "custom") return;',
     'function markCustom(k){\n  if(Array.isArray(INP.assumed)) INP.assumed = INP.assumed.filter(a => a !== k && a !== k + "." + S.metal);\n'
     '  const box = document.getElementById("f-" + k); const fl = box && box.closest(".fld"); if(fl) fl.querySelectorAll(".asm, .psrc").forEach(e => e.remove());\n'
     '  if(!SITE_KEYS.has(k) || INP.preset === "custom") return;'),
    # the form shows the preset source or an ASSUMED badge
    (JS, '${f.src ? `<span class="src">${esc(f.src)}</span>` : ""}',
     '${isAssumed(f.k) ? `<span class="asm" title="${esc(tr("No Taiwan source: a generic default. Replace it with site data."))}">${tr("ASSUMED · no Taiwan source")}</span>` : (presetSrc(f.k) && INP.preset !== "custom" ? `<span class="src psrc">${tr("Preset source")}: ${esc(presetSrc(f.k))}</span>` : "")}'
     '${f.src ? `<span class="src">${esc(f.src)}</span>` : ""}'),
    # site tab note and report
    (JS, 'PRESETS[I.preset].note + " Illustrative defaults: replace with MeteoSwiss station normals and site data."',
     'tr(PRESETS[I.preset].note) + " " + (Array.isArray(I.assumed) && I.assumed.length ? tr("Inputs marked ASSUMED have no Taiwan source yet; replace them with site data.") : tr("Every preset value has a Taiwan source; check it against your site."))'),
    (JS, "· land use ${I.land}`);", "· land use ${I.land}`);\n  if(Array.isArray(I.assumed) && I.assumed.length) L.push(`Inputs without a Taiwan source (ASSUMED generic defaults): ${I.assumed.join(\", \")}`);"),
    # field source notes that pointed to Swiss services
    (JS, 'help:"Sets how long snow covers the ground.", src:"swisstopo height service (filled from the map)"', 'help:"Sets how long snow covers the ground."'),
    (JS, 'help:"Background air quality. LRV limit 20 µg/m³.", src:"FOEN annual maps 2023–2025 (filled from the map); NABEL or cantonal stations"', 'help:"Background air quality at the site.", src:"MOENV air quality monitoring stations"'),
    (JS, 'help:"LRV limit 10 µg/m³.", src:"FOEN annual maps 2023–2025"', 'src:"MOENV air quality monitoring stations"'),
    # style of the badge
    (CSS, ".leaflet-container{font-family:var(--f-body); background:var(--chip)}",
     ".leaflet-container{font-family:var(--f-body); background:var(--chip)}\n"
     ".fld .asm{display:inline-block; align-self:flex-start; margin-top:4px; font-family:var(--f-mono); font-size:10px; letter-spacing:.06em; color:var(--warn); border:1px dashed currentColor; border-radius:2px; padding:1px 5px}"),
]

# field source notes: Taiwan data instead of Swiss monitoring programmes
for _old, _new, _n in [
    ('src:"FOEN hydrological data"', 'src:"WRA hydrological yearbook and discharge stations"', 1),
    ('src:"MeteoSwiss climate normals (opendata.swiss)"', 'src:"Central Weather Administration climate statistics"', 1),
    ('src:"MeteoSwiss station climatology"', 'src:"Central Weather Administration station climatology"', 1),
    ('src:"MeteoSwiss wind roses"', 'src:"Central Weather Administration wind records"', 1),
    ('src:"NABO, cantonal data"', 'src:"No national soil background data found for Taiwan; sample reference soil"', 1),
    ('src:"NABO, cantonal soil surveys"', 'src:"Soil surveys (no national Taiwan dataset found yet)"', 1),
    ('src:"NADUF"', 'src:"MOENV river water quality monitoring"', 1),
    ('src:"NAQUA"', 'src:"MOENV and WRA groundwater monitoring"', 2),
    ('src:"O₂, NO₃⁻, Fe²⁺, H₂S from NAQUA or site wells"', 'src:"O₂, NO₃⁻, Fe²⁺, H₂S from MOENV or WRA monitoring wells, or site wells"', 1),
    ('src:"Recharge or upstream groundwater (NAQUA, site wells)"', 'src:"Recharge or upstream groundwater (MOENV or WRA wells, site wells)"', 1),
]:
    PATCHES.append((JS, _old, _new, {"count": _n}))
