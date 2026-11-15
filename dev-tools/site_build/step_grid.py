"""Step 2d (part 1): Taiwan data grid with the MOA detailed soil map; picking a site fills the soil inputs.

- data/grid/grid.bin + grid.json (made by tools/build_soil_grid.py, 250 m cells, TWD97) are copied to site/data/.
- A map click or coordinate look-up reads topsoil pH class, drainage, texture and lime at that point.
- "Fill soil values and set the source location" sets pH (class midpoint; the class limit for the open classes
  <4.5 and >9.1) and the water regime (good -> well drained; imperfect or poor -> periodically waterlogged;
  very poor or flooded -> permanently waterlogged: a CHemTrace mapping, stated in the source note), removes them from
  the ASSUMED list and shows the source under the field. The rest of the preset stays as it is.
- The detailed soil map covers mainly farmland; elsewhere the page says there is no soil map at that point.
"""
from pathlib import Path

JS = "assets/js/app.js"
ROOT = Path(__file__).resolve().parents[2]

SOIL_CONST = r'''// MOA detailed soil map (詳測土壤圖 2016-10-13) code book, as rasterised by tools/build_soil_grid.py
const SOIL_PH = [null, [null, 4.5, "below 4.5"], [4.6, 5.0], [5.1, 5.5], [5.6, 6.0], [6.1, 6.5], [6.6, 7.3], [7.4, 7.8], [7.9, 8.4], [8.5, 9.0], [9.1, null, "above 9.1"]];
const SOIL_DRAIN = [null, ["good", "well"], ["imperfect", "periodic"], ["poor", "periodic"], ["very poor", "perm"], ["flooded", "perm"]];
const SOIL_TEX = [null, "sand, coarse sand", "fine sand, loamy sand", "sandy loam", "very fine sand, very fine sandy loam", "silt, silt loam", "loam", "sandy clay loam", "clay loam, silty clay loam", "silty clay", "clay", "gravel"];
const SOIL_LIME = [null, "not calcareous", "calcareous", "lime nodules"];
const phTxt = c => SOIL_PH[c] ? (SOIL_PH[c][2] || `${SOIL_PH[c][0].toFixed(1)}–${SOIL_PH[c][1].toFixed(1)}`) : "";
const phMid = c => { const p = SOIL_PH[c]; if(!p) return null; return p[0] == null ? p[1] : p[1] == null ? p[0] : Math.round((p[0] + p[1]) * 5) / 10; };
function readSite(E, N){
  const ll = twd97ToWgs(E, N);
  const v = k => { const s = GRID.ok ? sampleGrid(k, E, N, 1) : null; return s ? s.v : null; };
  const soil = GRID.ok ? {ph:v("soil_ph"), drain:v("soil_drain"), tex:v("soil_tex"), lime:v("soil_lime")} : null;
  return {E:Math.round(E), N:Math.round(N), lat:ll.lat, lng:ll.lng, inside:inTaiwan(ll), soil: soil && soil.ph ? soil : null};
}'''

ROWS_OLD = '''  add("Climate, soil, aquifer, land use", "– (enter them in the tabs below)", "Taiwan data grid not built yet");'''
ROWS_NEW = '''  const so = s.soil, SRC = "MOA detailed soil map (2016)";
  if(so){
    add("Topsoil pH", `${phTxt(so.ph)} <span class="mini">(${tr("class")})</span>`, SRC);
    if(so.drain) add("Drainage", tr(SOIL_DRAIN[so.drain][0]), SRC);
    if(so.tex) add("Texture, 0–30 cm", tr(SOIL_TEX[so.tex]), SRC);
    if(so.lime) add("Lime", tr(SOIL_LIME[so.lime]), SRC);
  } else add("Soil", "– (no detailed soil map at this point; it covers mainly farmland)", SRC);
  add("Climate, aquifer, land use", "– (enter them in the tabs below)", "Taiwan data grid: only the soil map so far");'''

APPLY_OLD = '''  INP.srcE = s.E; INP.srcN = s.N; INP.siteName = `E ${s.E}, N ${s.N}`; SP.fitKey = "";'''
APPLY_NEW = '''  INP.srcE = s.E; INP.srcN = s.N; INP.siteName = `E ${s.E}, N ${s.N}`; SP.fitKey = "";
  if(s.soil){
    const so = s.soil, here = `MOA detailed soil map (2016) at E ${s.E}, N ${s.N}`, src = INP.siteSrc = Object.assign({}, INP.siteSrc);
    const mid = phMid(so.ph);
    if(mid != null){ INP.pH = mid; src.pH = `${here}: topsoil pH class ${phTxt(so.ph)}, ${SOIL_PH[so.ph][0] == null || SOIL_PH[so.ph][1] == null ? "class limit" : "class midpoint"} used`; }
    if(so.drain){ INP.drain = SOIL_DRAIN[so.drain][1]; src.drain = `${here}: drainage ${SOIL_DRAIN[so.drain][0]} (mapped by CHemTrace to the water regime)`; }
    if(Array.isArray(INP.assumed)) INP.assumed = INP.assumed.filter(k => !(k in src));
  }'''

PATCHES = [
    (JS, '''function readSite(E, N){
  const ll = twd97ToWgs(E, N);
  return {E:Math.round(E), N:Math.round(N), lat:ll.lat, lng:ll.lng, inside:inTaiwan(ll)};
}''', SOIL_CONST),
    (JS, ROWS_OLD, ROWS_NEW),
    (JS, "function pickTwd97(E, N){ showSite(readSite(E, N)); }", "async function pickTwd97(E, N){ await loadGrid(); showSite(readSite(E, N)); }"),
    (JS, APPLY_OLD, APPLY_NEW),
    (JS, "  btn.disabled = false;\n  $(\"#spE\").value = s.E; $(\"#spN\").value = s.N;",
     "  btn.disabled = false; btn.textContent = tr(s.soil ? \"Fill soil values and set the source location\" : \"Use as the source location\");\n  $(\"#spE\").value = s.E; $(\"#spN\").value = s.N;"),
    (JS, '<p class="mini">${tr("The Taiwan data grid (precipitation, soil, aquifer, land use) is planned; until then this point only sets where the source is.")}</p>`;',
     '<p class="mini">${tr(s.soil ? "Soil values come from the soil map polygon at this point or within 250 m of it; check them against a site sample." : "The Taiwan data grid has only the soil map so far; this point sets where the source is.")}</p>`;'),
    # the form shows the site source before the preset source; editing a field removes it; inputs keep it
    (JS, ': (presetSrc(f.k) && INP.preset !== "custom" ?',
     ': (INP.siteSrc && INP.siteSrc[f.k] ? `<span class="src psrc">${tr("Site source")}: ${esc(INP.siteSrc[f.k])}</span>` : presetSrc(f.k) && INP.preset !== "custom" ?'),
    (JS, 'function markCustom(k){\n', 'function markCustom(k){\n  if(INP.siteSrc && INP.siteSrc[k]){ INP.siteSrc = Object.assign({}, INP.siteSrc); delete INP.siteSrc[k]; }\n'),
    (JS, '  if(Array.isArray(src.assumed)) out.assumed = src.assumed.filter(k => typeof k === "string").slice(0, 80);\n',
     '  if(Array.isArray(src.assumed)) out.assumed = src.assumed.filter(k => typeof k === "string").slice(0, 80);\n'
     '  if(src.siteSrc && typeof src.siteSrc === "object") out.siteSrc = Object.fromEntries(Object.entries(src.siteSrc).filter(([k, v]) => typeof v === "string").slice(0, 20).map(([k, v]) => [k, v.slice(0, 200)]));\n'),
    (JS, 'Object.assign(INP, clone(PRESETS[id].v), {preset:id, siteName:"", srcE:"", srcN:"", assumed:assumedOf(id)}); renderForm();',
     'Object.assign(INP, clone(PRESETS[id].v), {preset:id, siteName:"", srcE:"", srcN:"", assumed:assumedOf(id), siteSrc:{}}); renderForm();'),
]


def build(F):
    for name in ("grid.bin", "grid.json"):
        p = ROOT / "data" / "grid" / name
        if not p.exists():
            raise SystemExit(f"[step_grid] {p} missing: run python tools/build_soil_grid.py first")
        F.raw["data/" + name] = p.read_bytes()
