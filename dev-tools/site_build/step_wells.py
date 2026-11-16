"""Step 2d (part 2): groundwater auto-fill from the nearest monitoring wells. Runs after step_grid.py.

Data: data/grid/wells.json from tools/build_well_table.py (MOENV regional groundwater monitoring wells and WRA
layer-1 observation wells; rules in that script). Copied to site/data/wells.json.
On a site pick the page looks for the nearest MOENV well and the nearest WRA layer-1 well with a redox class.
A well is used only within WELL_KM = 5 km (assumption: a screening choice, shown with the distance in every note).
Filled: groundwater pH, depth to water (MOENV GWT, measured from the well top), background of every metal
(0 when more than half the samples are below detection, with the limit in the note), and the redox class.
The WRA redox classes are mapped to the site's four classes (assumption, CHemTrace mapping):
  CH4 generation, SO4 reduction or Fe(III)-SO4 with sulfide -> sulfidic; Fe(III) (also "Fe(III)/SO4, no sulfide") ->
  anoxic; Mn(IV), "O2 or NO3" and "O2 or suboxic" -> suboxic (oxygen was not measured, so oxic is never assigned).
Chloride is shown (it signals seawater influence) but not yet used in the calculation.
Elevation: ground height of the nearest WRA observation well within 5 km (data.gov.tw 32718), until an elevation grid exists.
Air: data/grid/air.json from tools/build_air_table.py (MOENV AQX_P_07 and AQX_P_08). PM10 and PM2.5 come from the
nearest station within AIR_KM = 10 km (assumption, shown with the distance); traffic stations (交通站) are skipped
because they measure roadside air, not the background.
Protection zones: data/grid/protection.geojson from tools/build_protection_layer.py (MOENV, data.gov.tw 6377). A site
inside a protection zone (PRO_TYPE 保護區) gets groundwater class 1, otherwise class 2 (Groundwater Pollution Control
Standards, see the 05 file); the point test uses the outlines simplified to about 20 m. Areas within the set distance
of an intake are shown but do not set the class.
Rainfall: data/grid/rain.json from tools/build_rain_table.py (CWA C-B0027-001, 1991-2020 normals of 27 staffed
stations; coordinates from the CODiS station list). The nearest station within RAIN_KM = 30 km whose altitude is within
RAIN_DZ = 300 m of the site's ground height (from the nearest WRA well); when the site height is unknown, only
stations below 300 m are used (assumptions: rainfall rises steeply with height, e.g. Alishan 3,941 mm vs Chiayi 1,822 mm).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = "assets/js/app.js"

WELLS_JS = r'''
// ---- groundwater wells for the site auto-fill (tools/build_well_table.py; rules in dev-tools/site_build/step_wells.py)
const WELLS = {d:null, ok:null}, WELL_KM = 5;
async function loadWells(){
  if(WELLS.ok !== null) return WELLS.ok;
  try{ WELLS.d = await fetch("data/wells.json").then(r => { if(!r.ok) throw 0; return r.json(); }); WELLS.ok = true; }catch(e){ WELLS.ok = false; }
  return WELLS.ok;
}
function redoxOfClass(c){
  if(!c) return null;
  const p = c.replace(/^NO3 and /, "");
  if(/^CH4gen|^SO4|^Fe\(III\)-SO4/.test(p)) return "sulfidic";
  if(/^Fe\(III\)/.test(p)) return "anoxic";
  if(/^Mn\(IV\)|^O2 or/.test(p)) return "suboxic";
  return null;
}
function nearWells(E, N){
  if(!WELLS.ok) return null;
  const near = (list, ok) => { let b = null, bd = Infinity; for(const w of list){ if(ok && !ok(w)) continue; const d = Math.hypot(w[2] - E, w[3] - N); if(d < bd){ bd = d; b = w; } } return b ? {w:b, km:bd / 1000} : null; };
  const m = near(WELLS.d.moenv), r = near(WELLS.d.wra, w => !!redoxOfClass(w[6])), h = near(WELLS.d.wra, w => w[12] != null);
  return {m, r, h, useM:!!(m && m.km <= WELL_KM), useR:!!(r && r.km <= WELL_KM), useH:!!(h && h.km <= WELL_KM)};
}
const kmTxt = km => `${km < 10 ? km.toFixed(1) : Math.round(km)} km`;
function moenvNote(g){ const w = g.m.w; return `MOENV groundwater well ${w[1]} (${w[0]}), ${kmTxt(g.m.km)} away, ${w[5]} samples ${w[6]}–${w[7]}`; }
function wraNote(g){ const w = g.r.w; return `WRA layer-1 well ${w[1]} (${w[0]}), ${kmTxt(g.r.km)} away`; }
function metalNote(v){ return v[0] === 0 && v[2] > v[1] / 2 ? `${v[2]} of ${v[1]} samples below ${v[3] != null ? v[3] + " µg/L" : "detection"}, so 0 used (below detection, not a measured zero)` : `median ${v[0]} µg/L (${v[2]} of ${v[1]} samples below detection)`; }
function wellRows(s, add){
  const g = s.gw;
  if(!g || !g.m){ add("Groundwater", "– (well table not loaded)", "MOENV, WRA"); return; }
  const SRC_M = "MOENV regional groundwater monitoring", SRC_R = "WRA groundwater quality, layer 1";
  if(g.useM){
    const w = g.m.w;
    add("Nearest MOENV well", `${esc(w[1])}, ${kmTxt(g.m.km)} <span class="mini">(${w[5]} ${tr("samples")}, ${w[6]}–${w[7]})</span>`, SRC_M);
    if(w[8] != null) add("Groundwater pH", `${w[8]}`, SRC_M);
    if(w[11] != null) add("Depth to water", `${r2(w[11])} m <span class="mini">(${tr("from the well top")})</span>`, SRC_M);
    if(w[12][S.metal]) add(`Background ${S.metal} in groundwater`, esc(tr(metalNote(w[12][S.metal]))), SRC_M);
    if(w[9] != null) add("Chloride", `${w[9]} mg/L`, SRC_M);
  } else add("Groundwater", `– (${tr("nearest MOENV well")} ${esc(g.m.w[1])} ${tr("is")} ${kmTxt(g.m.km)} ${tr("away; more than 5 km, not used")})`, SRC_M);
  if(g.useR){
    const w = g.r.w;
    add("Redox class", `${esc(tr(w[6]))} → ${tr(redoxOfClass(w[6]))} <span class="mini">(${Math.round(w[7] * 100)}% ${tr("of")} ${w[5]} ${tr("complete samples")}, ${esc(w[1])}, ${kmTxt(g.r.km)})</span>`, SRC_R);
    if(w[8] != null) add("Chloride, WRA well", `${w[8]} mg/L <span class="mini">(${w[9]} ${tr("samples")})</span>`, SRC_R);
  } else if(g.r) add("Redox class", `– (${tr("nearest WRA well with a redox class is")} ${kmTxt(g.r.km)} ${tr("away; not used")})`, SRC_R);
  if(g.useH) add("Ground height", `${g.h.w[12]} m <span class="mini">(${esc(g.h.w[1])}, ${kmTxt(g.h.km)})</span>`, "WRA observation wells (32718)");
}
function applyWells(s, src){
  const g = s.gw; if(!g) return;
  // drop well notes left from an earlier pick that this point does not refill
  if(!g.useM) Object.keys(src).forEach(k => { if(k === "gwpH" || k === "wt" || k === "gwCl" || k.startsWith("bgGw.")) delete src[k]; });
  if(!g.useR) delete src.redox;
  if(!g.useH) delete src.elev;
  if(g.useH){ const w = g.h.w; INP.elev = Math.round(w[12]); src.elev = `WRA observation well ${w[1]} (${w[0]}), ${kmTxt(g.h.km)} away: ground height ${w[12]} m (data.gov.tw 32718); no elevation grid yet`; }
  if(g.useM){
    const w = g.m.w, here = moenvNote(g);
    if(w[8] != null){ INP.gwpH = w[8]; src.gwpH = `${here}: median pH ${w[8]}`; }
    if(w[9] != null){ INP.gwCl = w[9]; src.gwCl = `${here}: median chloride ${w[9]} mg/L`; }
    if(w[11] != null && w[11] > 0){ INP.wt = r2(w[11]); src.wt = `${here}: median depth to water ${r2(w[11])} m, measured from the well top`; }
    for(const [m, v] of Object.entries(w[12])){ if(!METALS[m]) continue; INP.bgGw[m] = v[0]; src["bgGw." + m] = `${here}: ${metalNote(v)}`; }
  }
  if(g.useR){
    const w = g.r.w, rx = redoxOfClass(w[6]);
    if(rx){ INP.redox = rx; src.redox = `${wraNote(g)}: most common class "${w[6]}" in ${Math.round(w[7] * 100)}% of ${w[5]} complete samples (${w[10]}–${w[11]}); mapped by CHemTrace to ${rx}`; }
  }
}
// ---- air-quality stations for the site auto-fill (tools/build_air_table.py)
const AIR = {d:null, ok:null}, AIR_KM = 10;
async function loadAir(){
  if(AIR.ok !== null) return AIR.ok;
  try{ AIR.d = await fetch("data/air.json").then(r => { if(!r.ok) throw 0; return r.json(); }); AIR.d.stations.forEach(s => { const p = wgsToTwd97(s[4], s[5]); s.E = p.E; s.N = p.N; }); AIR.ok = true; }catch(e){ AIR.ok = false; }
  return AIR.ok;
}
function nearAir(E, N){
  if(!AIR.ok) return null;
  let b = null, bd = Infinity;
  for(const s of AIR.d.stations){ if(s[3] === "交通站" || s[6] == null) continue; const d = Math.hypot(s.E - E, s.N - N); if(d < bd){ bd = d; b = s; } }
  return b ? {s:b, km:bd / 1000, use:bd / 1000 <= AIR_KM} : null;
}
function airRows(s, add){
  const a = s.air, SRC = "MOENV air quality monitoring (AQX_P_07, AQX_P_08)";
  if(!a){ add("Background air", "– (station table not loaded)", SRC); return; }
  const t = a.s;
  if(a.use){
    add("Nearest air station", `${esc(t[1])} <span class="mini">(${esc(t[3])}, ${esc(t[2])})</span>, ${kmTxt(a.km)}`, SRC);
    add("PM10, PM2.5 (annual mean)", `${t[6]}, ${t[7] != null ? t[7] : "–"} µg/m³ <span class="mini">(${t[8].replace("/", ", ")})</span>`, SRC);
  } else add("Background air", `– (${tr("nearest air station")} ${esc(t[1])} ${tr("is")} ${kmTxt(a.km)} ${tr("away; more than 10 km, not used")})`, SRC);
}
function applyAir(s, src){
  const a = s.air; if(!a) return;
  if(!a.use){ delete src.pm10; delete src.pm25; return; }
  const t = a.s, here = `MOENV air station ${t[1]} (${t[0]}, ${t[3]}), ${kmTxt(a.km)} away: mean of the complete years ${t[8].replace("/", " and ")} of monthly values (AQX_P_08)`;
  INP.pm10 = t[6]; src.pm10 = `${here}, PM10 ${t[6]} µg/m³`;
  if(t[7] != null){ INP.pm25 = t[7]; src.pm25 = `${here}, PM2.5 ${t[7]} µg/m³`; }
}
function airPopup(t){
  return `<b>${esc(t[1])}</b> <span class="mini">(MOENV ${esc(t[0])}, ${esc(t[3])}, ${esc(t[2])})</span>`
    + (t[6] != null ? `<br>PM10 ${t[6]} µg/m³ · PM2.5 ${t[7] != null ? t[7] : "–"} µg/m³ <span class="mini">(${tr("mean of complete years")} ${t[8].replace("/", ", ")})</span>` : `<br>${tr("no complete year 2023–2025")}`)
    + (t[3] === "交通站" ? `<br><span class="mini">${tr("traffic station: roadside air, not used as background")}</span>` : "");
}
// ---- drinking-water source protection zones (tools/build_protection_layer.py): map layer and groundwater class
const PZ = {d:null, ok:null};
async function loadPz(){
  if(PZ.ok !== null) return PZ.ok;
  try{ PZ.d = await fetch("data/protection.geojson").then(r => { if(!r.ok) throw 0; return r.json(); }); PZ.ok = true; }catch(e){ PZ.ok = false; }
  return PZ.ok;
}
function inRing(x, y, ring){ let ins = false; for(let i = 0, j = ring.length - 1; i < ring.length; j = i++){ const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1]; if(((yi > y) !== (yj > y)) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) ins = !ins; } return ins; }
function inGeom(x, y, g){ const polys = g.type === "MultiPolygon" ? g.coordinates : [g.coordinates]; return polys.some(p => inRing(x, y, p[0]) && !p.slice(1).some(h => inRing(x, y, h))); }
function zonesAt(lat, lng){ return PZ.ok ? PZ.d.features.filter(f => inGeom(lng, lat, f.geometry)).map(f => f.properties) : null; }
function pzRows(s, add){
  const z = s.pz, SRC = "MOENV drinking-water source protection zones (data.gov.tw 6377)";
  if(!z){ add("Protection zone", "– (layer not loaded)", SRC); return; }
  const pzs = z.filter(p => p.type === "保護區"), ds = z.filter(p => p.type !== "保護區");
  add("Protection zone", pzs.length ? `${pzs.map(p => esc(p.name)).join("; ")} → ${tr("groundwater class 1")}` : `${tr("outside all protection zones")} → ${tr("groundwater class 2")}`, SRC);
  if(ds.length) add("Near a drinking-water intake", ds.map(p => esc(p.name)).join("; "), SRC);
}
function applyPz(s, src){
  const z = s.pz; if(!z) return;
  const pzs = z.filter(p => p.type === "保護區");
  INP.gwClass = pzs.length ? "1" : "2";
  src.gwClass = pzs.length ? `Inside ${pzs.map(p => p.name).join("; ")} (MOENV protection zones, data.gov.tw 6377, file of 2026-07-20; outlines simplified to about 20 m): class 1, groundwater within a drinking-water source protection zone`
    : "Outside all drinking-water source protection zones (MOENV, data.gov.tw 6377, file of 2026-07-20; outlines simplified to about 20 m): class 2";
}
function pzPopup(p){ return `<b>${esc(p.name)}</b><br>${esc(p.type === "保護區" ? tr("Drinking-water source protection zone") : tr("Within the set distance of a drinking-water intake"))}<br><span class="mini">${esc(p.county)} · ${esc(p.basin)}${p.intake ? " · " + esc(p.intake) : ""}<br>${esc(p.desc)}</span>`; }
async function pzLayer(){
  if(!(await loadPz()) || !SP.map) return null;
  if(!SP.ov.pz) SP.ov.pz = window.L.geoJSON(PZ.d, {style:f => f.properties.type === "保護區" ? {color:"#1F6F9F", weight:1.2, fillColor:"#5AA9D6", fillOpacity:0.18} : {color:"#7A5C9E", weight:1, dashArray:"4 3", fillColor:"#B79BD6", fillOpacity:0.12},
    onEachFeature:(f, l) => l.bindPopup(() => pzPopup(f.properties))});
  return SP.ov.pz;
}
// ---- rainfall normals (tools/build_rain_table.py): CWA 1991-2020, 27 staffed stations
const RAIN = {d:null, ok:null}, RAIN_KM = 30, RAIN_DZ = 300;
async function loadRain(){
  if(RAIN.ok !== null) return RAIN.ok;
  try{ RAIN.d = await fetch("data/rain.json").then(r => { if(!r.ok) throw 0; return r.json(); }); RAIN.d.stations.forEach(s => { const p = wgsToTwd97(s[2], s[3]); s.E = p.E; s.N = p.N; }); RAIN.ok = true; }catch(e){ RAIN.ok = false; }
  return RAIN.ok;
}
function nearRain(E, N, elev){
  if(!RAIN.ok) return null;
  const ok = s => elev != null ? Math.abs(s[4] - elev) <= RAIN_DZ : s[4] <= RAIN_DZ;
  let b = null, bd = Infinity;
  for(const s of RAIN.d.stations){ if(!ok(s)) continue; const d = Math.hypot(s.E - E, s.N - N); if(d < bd){ bd = d; b = s; } }
  return b ? {s:b, km:bd / 1000, use:bd / 1000 <= RAIN_KM, elevKnown:elev != null} : null;
}
function rainRows(s, add){
  const a = s.rain, SRC = "CWA 1991–2020 normals (C-B0027-001)";
  if(!a){ add("Rainfall", "– (station table not loaded)", SRC); return; }
  const t = a.s;
  if(a.use) add("Rainfall, nearest CWA station", `${Math.round(t[5]).toLocaleString("en-US")} mm/yr <span class="mini">(${esc(t[1])}, ${kmTxt(a.km)}, ${t[4]} m, ${t[6]})</span>`, SRC);
  else add("Rainfall", `– (${tr("nearest suitable CWA station")} ${esc(t[1])} ${tr("is")} ${kmTxt(a.km)} ${tr("away; more than 30 km, not used")})`, SRC);
}
function applyRain(s, src){
  const a = s.rain; if(!a) return;
  if(!a.use){ delete src.precip; return; }
  const t = a.s;
  INP.precip = Math.round(t[5]);
  src.precip = `CWA station ${t[1]} (${t[0]}), ${kmTxt(a.km)} away, ${t[4]} m: 1991–2020 normal ${t[5]} mm/yr (C-B0027-001; ${t[6]}); ${a.elevKnown ? "station within 300 m of the site's height" : "site height unknown, lowland stations only"}`;
}
'''

LAYER_JS = r'''
// ---- spread map: well layers (support-layer drawer)
const REDOX_COL = {oxic:"#2F7D9E", suboxic:"#7FA35A", anoxic:"#C08A2E", sulfidic:"#7A4E8F"};
function moenvPopup(w){
  const m = S.metal, v = w[12][m], lim = LIM.drink[m];
  return `<b>${esc(w[1])}</b> <span class="mini">(MOENV ${esc(w[0])}, ${esc(tr(w[4]))})</span><br>${w[5]} ${tr("samples")}, ${w[6]}–${w[7]}`
    + (v ? `<br>${esc(tr(`Background ${m} in groundwater`))}: ${esc(tr(metalNote(v)))}${lim != null ? ` <span class="mini">(${tr("drinking-water standard")} ${lim} µg/L)</span>` : ""}` : "")
    + (w[8] != null ? `<br>pH ${w[8]}` : "") + (w[9] != null ? ` · ${tr("Chloride")} ${w[9]} mg/L` : "") + (w[11] != null ? `<br>${tr("Depth to water")} ${r2(w[11])} m (${tr("from the well top")})` : "");
}
function wraPopup(w){
  const rx = redoxOfClass(w[6]);
  return `<b>${esc(w[1])}</b> <span class="mini">(WRA ${esc(w[0])}, ${esc(tr(w[4]))})</span>`
    + (w[6] ? `<br>${tr("Redox class")}: ${esc(tr(w[6]))}${rx ? ` → ${tr(rx)}` : ""} <span class="mini">(${Math.round(w[7] * 100)}% ${tr("of")} ${w[5]} ${tr("complete samples")}, ${w[10]}–${w[11]})</span>` : "")
    + (w[8] != null ? `<br>${tr("Chloride")} ${w[8]} mg/L <span class="mini">(${w[9]} ${tr("samples")})</span>` : "");
}
async function wellLayer(key){
  if(!(await loadWells()) || !SP.map) return null;
  const LF = window.L;
  if(key === "wellsM" && (!SP.ov.wellsM || SP.wellMetal !== S.metal)){
    if(SP.ov.wellsM && SP.map.hasLayer(SP.ov.wellsM)) SP.map.removeLayer(SP.ov.wellsM);
    const m = S.metal, lim = LIM.drink[m], g = LF.layerGroup();
    WELLS.d.moenv.forEach(w => {
      const v = w[12][m], over = v && lim != null && v[0] > lim, ll = twd97ToWgs(w[2], w[3]);
      LF.circleMarker([ll.lat, ll.lng], {renderer:SP.canvas, radius:over ? 6 : 4.5, weight:1, color:"#fff", fillColor:over ? "#C0392B" : "#4A5A6A", fillOpacity:0.9})
        .bindPopup(() => moenvPopup(w)).addTo(g);
    });
    SP.ov.wellsM = g; SP.wellMetal = m;
  }
  if(key === "wellsR" && !SP.ov.wellsR){
    const g = LF.layerGroup();
    WELLS.d.wra.forEach(w => {
      const ll = twd97ToWgs(w[2], w[3]), rx = redoxOfClass(w[6]);
      LF.circleMarker([ll.lat, ll.lng], {renderer:SP.canvas, radius:4.5, weight:1.5, color:rx ? REDOX_COL[rx] : "#888", fillColor:"#fff", fillOpacity:0.85})
        .bindPopup(() => wraPopup(w)).addTo(g);
    });
    SP.ov.wellsR = g;
  }
  return SP.ov[key];
}
async function airLayer(){
  if(!(await loadAir()) || !SP.map) return null;
  if(!SP.ov.air){
    const LF = window.L, g = LF.layerGroup();
    AIR.d.stations.forEach(t => { const tra = t[3] === "交通站";
      LF.circleMarker([t[4], t[5]], {renderer:SP.canvas, radius:5, weight:1.5, color:tra ? "#999" : "#2F6FB0", fillColor:tra ? "#fff" : "#9CC3E6", fillOpacity:0.9}).bindPopup(() => airPopup(t)).addTo(g); });
    SP.ov.air = g;
  }
  return SP.ov.air;
}
function refreshWellLayer(){
  const cb = document.querySelector('#spLayers input[data-ov="wellsM"]');
  if(cb && cb.checked && SP.wellMetal !== S.metal) wellLayer("wellsM").then(l => { if(l && cb.checked) l.addTo(SP.map); });
}
'''

PATCHES = [
    (JS, "async function pickTwd97(E, N){ await loadGrid(); showSite(readSite(E, N)); }",
     WELLS_JS.lstrip("\n") + "async function pickTwd97(E, N){ await Promise.all([loadGrid(), loadWells(), loadAir(), loadPz(), loadRain()]); showSite(readSite(E, N)); }"),
    (JS, "  return {E:Math.round(E), N:Math.round(N), lat:ll.lat, lng:ll.lng, inside:inTaiwan(ll), soil: soil && soil.ph ? soil : null};",
         "  const gw = nearWells(E, N);\n  return {E:Math.round(E), N:Math.round(N), lat:ll.lat, lng:ll.lng, inside:inTaiwan(ll), soil: soil && soil.ph ? soil : null, gw, air:nearAir(E, N), pz:zonesAt(ll.lat, ll.lng), rain:nearRain(E, N, gw && gw.useH ? gw.h.w[12] : null)};"),
    (JS, '  add("Climate, aquifer, land use", "– (enter them in the tabs below)", "Taiwan data grid: only the soil map so far");',
         '  wellRows(s, add); airRows(s, add); rainRows(s, add); pzRows(s, add);\n  add("Wind, land use", "– (enter them in the tabs below)", "not yet in the Taiwan data grid");'),
    (JS, '${tr(s.soil ? "Soil values come from the soil map polygon at this point or within 250 m of it; check them against a site sample." : "The Taiwan data grid has only the soil map so far; this point sets where the source is.")}',
         '${tr("Soil values come from the soil map polygon at this point or within 250 m; groundwater values from the nearest monitoring wells within 5 km, background air from the nearest air station within 10 km, rainfall from the nearest CWA station within 30 km and 300 m of height. Check them against site samples.")}'),
    (JS, 'btn.textContent = tr(s.soil ? "Fill soil values and set the source location" : "Use as the source location");',
         'btn.textContent = tr(s.soil || (s.gw && (s.gw.useM || s.gw.useR)) || (s.air && s.air.use) || (s.rain && s.rain.use) || !!s.pz ? "Fill site values and set the source location" : "Use as the source location");'),
    (JS, "    if(Array.isArray(INP.assumed)) INP.assumed = INP.assumed.filter(k => !(k in src));\n  }\n  renderForm();",
         "  }\n  { const src = INP.siteSrc = Object.assign({}, INP.siteSrc); applyWells(s, src); applyAir(s, src); applyRain(s, src); applyPz(s, src);\n"
         "    if(Array.isArray(INP.assumed)) INP.assumed = INP.assumed.filter(k => !(k in src)); }\n  renderForm();"),
    # per-metal site sources ("bgGw.As") in the form and when a value is edited
    (JS, '(INP.siteSrc && INP.siteSrc[f.k] ? `<span class="src psrc">${tr("Site source")}: ${esc(INP.siteSrc[f.k])}</span>`',
         '(INP.siteSrc && (INP.siteSrc[f.k + "." + S.metal] || INP.siteSrc[f.k]) ? `<span class="src psrc">${tr("Site source")}: ${esc(INP.siteSrc[f.k + "." + S.metal] || INP.siteSrc[f.k])}</span>`'),
    (JS, '  if(INP.siteSrc && INP.siteSrc[k]){ INP.siteSrc = Object.assign({}, INP.siteSrc); delete INP.siteSrc[k]; }',
         '  if(INP.siteSrc && (INP.siteSrc[k] || INP.siteSrc[k + "." + S.metal])){ INP.siteSrc = Object.assign({}, INP.siteSrc); delete INP.siteSrc[k]; delete INP.siteSrc[k + "." + S.metal]; }'),
    (JS, 'filter(([k, v]) => typeof v === "string").slice(0, 20)', 'filter(([k, v]) => typeof v === "string").slice(0, 40)'),
    # spread map: well layers
    (JS, "function drawSpread(){", LAYER_JS.lstrip("\n") + "function drawSpread(){\n  refreshWellLayer();", {"count": 1}),
    (JS, "    const l = SP.ov[cb.dataset.ov]; if(l){ if(cb.checked) l.addTo(SP.map); else SP.map.removeLayer(l); }",
         "    const go = l => { if(l){ if(cb.checked) l.addTo(SP.map); else SP.map.removeLayer(l); } };\n"
         "    if(cb.dataset.ov.startsWith(\"wells\")) wellLayer(cb.dataset.ov).then(go); else if(cb.dataset.ov === \"air\") airLayer().then(go); else if(cb.dataset.ov === \"pz\") pzLayer().then(go); else go(SP.ov[cb.dataset.ov]);"),
]


def build(F):
    p = ROOT / "data" / "grid" / "wells.json"
    if not p.exists():
        raise SystemExit(f"[step_wells] {p} missing: run python tools/build_well_table.py first")
    F.raw["data/wells.json"] = p.read_bytes()
    a = ROOT / "data" / "grid" / "air.json"
    if not a.exists():
        raise SystemExit(f"[step_wells] {a} missing: run python tools/build_air_table.py first")
    F.raw["data/air.json"] = a.read_bytes()
    z = ROOT / "data" / "grid" / "protection.geojson"
    if not z.exists():
        raise SystemExit(f"[step_wells] {z} missing: run python tools/build_protection_layer.py first")
    F.raw["data/protection.geojson"] = z.read_bytes()
    r = ROOT / "data" / "grid" / "rain.json"
    if not r.exists():
        raise SystemExit(f"[step_wells] {r} missing: run python tools/build_rain_table.py first")
    F.raw["data/rain.json"] = r.read_bytes()
