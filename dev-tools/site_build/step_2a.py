"""Step 2a: Taiwan basics.

- Coordinates: TWD97 / TM2 zone 121 (EPSG:3826) instead of Swiss LV95 (EPSG:2056).
- Base maps: NLSC WMTS instead of swisstopo, with a layer menu: EMAP (colour, default on the site map), EMAP01 (grey,
  default on the spread map) and PHOTO2 (aerial photo). Layer ids checked in the NLSC capabilities document on 15 Nov 2026;
  NLSC FAQ Q3 (maps.nlsc.gov.tw/S09SOA/pro/faq_ajax_list.jsp): open without application, no bulk server caching.
- Swiss services removed: geo.admin height, profile and stream queries; geodienste.ch protection zones; FOEN overlays.
  Taiwan has no free elevation API (05 file, [S19][S20]), so terrain waits for the DEM grid (step 2d).
- Swiss 1 km data grid removed; the map click now gives TWD97 coordinates for the source location.
- NABEL (Swiss air stations) removed; air background for Taiwan comes in phase 3.
- Browser storage keys renamed (cht-tw-*) so the Taiwan and Swiss sites do not overwrite each other on the same github.io origin.
- Name CHemTrace Taiwan, version 0.1.0; CJK fallback fonts.
"""
JS, IDX, CSS = "assets/js/app.js", "index.html", "assets/css/styles.css"

SITE_BLOCK = r'''/* ================= SITE LOOKUP (map + Taiwan coordinates) ================= */
// The Taiwan 1 km data grid (climate, soil, aquifer, land use) is not built yet (step 2d of 07_完整建構流程.md).
// Until then a map click gives the TWD97 coordinates of a place, which can become the source location; site values are typed in.
const GRID = {meta:null, layers:{}, ok:null};
let SITE = null, map = null, mapMarker = null;
// Base maps: NLSC WMTS, Web Mercator tiles in {z}/{y}/{x} order. NLSC FAQ Q3: the WMTS service has been open without
// application since 30 Aug 2013; tiles must not be cached in bulk on a server, so the page loads them straight from NLSC.
// Layer ids from the NLSC capabilities document: EMAP 臺灣通用電子地圖, EMAP01 灰階, PHOTO2 正射影像圖(通用).
// (EMAP5_OPENDATA stops at 1:18,000 and looks blurred when zoomed in.)
const NLSC_URL = id => `https://wmts.nlsc.gov.tw/wmts/${id}/default/GoogleMapsCompatible/{z}/{y}/{x}`;
const NLSC_ATTR = 'Base map © <a href="https://maps.nlsc.gov.tw/" target="_blank" rel="noopener">NLSC 內政部國土測繪中心</a>';
const BASEMAPS = [["EMAP", "Map"], ["EMAP01", "Map, grey"], ["PHOTO2", "Aerial photo"]];
function addBaseLayers(m, def){
  const LF = window.L, layers = {};
  BASEMAPS.forEach(([id, name]) => { layers[name] = LF.tileLayer(NLSC_URL(id), {maxZoom:19, attribution:NLSC_ATTR}); });
  layers[(BASEMAPS.find(b => b[0] === def) || BASEMAPS[0])[1]].addTo(m);
  LF.control.layers(layers, null, {position:"topright", collapsed:true}).addTo(m);
}
const TW_BOUNDS = [[21.3, 117.6], [26.8, 122.6]];      // Taiwan, Penghu, Kinmen and Matsu
async function loadGrid(){
  if(GRID.ok !== null) return GRID.ok;
  try{
    const [m, b] = await Promise.all([fetch("data/grid.json").then(r => { if(!r.ok) throw 0; return r.json(); }), fetch("data/grid.bin").then(r => { if(!r.ok) throw 0; return r.arrayBuffer(); })]);
    const n = m.ncols * m.nrows;
    m.layers.forEach(L0 => { GRID.layers[L0.name] = {spec:L0, arr: L0.type === "u8" ? new Uint8Array(b, L0.byteOffset, n) : L0.type === "u16" ? new Uint16Array(b, L0.byteOffset, n) : new Int16Array(b, L0.byteOffset, n)}; });
    GRID.meta = m; GRID.ok = true;
  }catch(e){ GRID.ok = false; }
  return GRID.ok;
}
function sampleGrid(name, E, N, search){
  const g = GRID.layers[name]; if(!g) return null;
  const m = GRID.meta, s = g.spec, c0 = Math.floor((E - m.x0) / m.res), r0 = Math.floor((m.y1 - N) / m.res);
  for(let d = 0; d <= (search == null ? 2 : search); d++){
    let best = null, bd = 1e9;
    for(let dr = -d; dr <= d; dr++) for(let dc = -d; dc <= d; dc++){
      if(Math.max(Math.abs(dr), Math.abs(dc)) !== d) continue;
      const r = r0 + dr, c = c0 + dc; if(r < 0 || c < 0 || r >= m.nrows || c >= m.ncols) continue;
      const v = g.arr[r * m.ncols + c]; if(v === s.nodata) continue;
      const dd = dr * dr + dc * dc; if(dd < bd){ bd = dd; best = (v - s.offset) / s.scale; }
    }
    if(best !== null) return {v:best, km:d};
  }
  return null;
}
// TWD97 / TM2 zone 121 (EPSG:3826): GRS80 ellipsoid, central meridian 121° E, scale 0.9999, false easting 250,000 m.
// Transverse Mercator by the Krüger series to n⁴ (Karney 2011, J. Geodesy 85:475); TWD97 is treated as identical to WGS84.
// Checked against PROJ 9.8 in selfTest (difference well below 1 mm inside Taiwan).
const TM2 = (() => {
  const a = 6378137, f = 1 / 298.257222101, n = f / (2 - f), n2 = n * n, n3 = n2 * n, n4 = n3 * n;
  return {A: a / (1 + n) * (1 + n2 / 4 + n4 / 64), e: Math.sqrt(f * (2 - f)), k0: 0.9999, lon0: 121, FE: 250000,
    al: [n / 2 - 2 * n2 / 3 + 5 * n3 / 16 + 41 * n4 / 180, 13 * n2 / 48 - 3 * n3 / 5 + 557 * n4 / 1440, 61 * n3 / 240 - 103 * n4 / 140, 49561 * n4 / 161280],
    be: [n / 2 - 2 * n2 / 3 + 37 * n3 / 96 - n4 / 360, n2 / 48 + n3 / 15 - 437 * n4 / 1440, 17 * n3 / 480 - 37 * n4 / 840, 4397 * n4 / 161280],
    de: [2 * n - 2 * n2 / 3 - 2 * n3 + 116 * n4 / 45, 7 * n2 / 3 - 8 * n3 / 5 - 227 * n4 / 45, 56 * n3 / 15 - 136 * n4 / 35, 4279 * n4 / 630]};
})();
function wgsToTwd97(lat, lng){
  const T = TM2, r = Math.PI / 180, phi = lat * r, lam = (lng - T.lon0) * r, sp = Math.sin(phi);
  const t = Math.sinh(Math.atanh(sp) - T.e * Math.atanh(T.e * sp));
  const xi = Math.atan2(t, Math.cos(lam)), eta = Math.atanh(Math.sin(lam) / Math.sqrt(1 + t * t));
  let x = xi, y = eta;
  for(let j = 1; j <= 4; j++){ x += T.al[j - 1] * Math.sin(2 * j * xi) * Math.cosh(2 * j * eta); y += T.al[j - 1] * Math.cos(2 * j * xi) * Math.sinh(2 * j * eta); }
  return {E: T.FE + T.k0 * T.A * y, N: T.k0 * T.A * x};
}
function twd97ToWgs(E, N){
  const T = TM2, xi = N / (T.k0 * T.A), eta = (E - T.FE) / (T.k0 * T.A);
  let x = xi, y = eta;
  for(let j = 1; j <= 4; j++){ x -= T.be[j - 1] * Math.sin(2 * j * xi) * Math.cosh(2 * j * eta); y -= T.be[j - 1] * Math.cos(2 * j * xi) * Math.sinh(2 * j * eta); }
  const chi = Math.asin(Math.sin(x) / Math.cosh(y));
  let phi = chi; for(let j = 1; j <= 4; j++) phi += T.de[j - 1] * Math.sin(2 * j * chi);
  return {lat: phi * 180 / Math.PI, lng: T.lon0 + Math.atan2(Math.sinh(y), Math.cos(x)) * 180 / Math.PI};
}
const inTaiwan = ll => ll.lat > TW_BOUNDS[0][0] && ll.lat < TW_BOUNDS[1][0] && ll.lng > TW_BOUNDS[0][1] && ll.lng < TW_BOUNDS[1][1];
function readSite(E, N){
  const ll = twd97ToWgs(E, N);
  return {E:Math.round(E), N:Math.round(N), lat:ll.lat, lng:ll.lng, inside:inTaiwan(ll)};
}
const r2 = x => x == null ? null : Math.round(x * 100) / 100;
function siteRows(s){
  const rows = [];
  const add = (k, v, src) => rows.push(`<tr><td>${esc(k)}</td><td>${v}</td><td>${esc(src)}</td></tr>`);
  add("Coordinates", `E ${s.E.toLocaleString("en-US")}, N ${s.N.toLocaleString("en-US")}`, "TWD97 / TM2 121° (EPSG:3826)");
  add("Latitude, longitude", `${s.lat.toFixed(5)}° N, ${s.lng.toFixed(5)}° E`, "converted (TWD97 ≈ WGS84)");
  add("Climate, soil, aquifer, land use", "– (enter them in the tabs below)", "Taiwan data grid not built yet");
  return rows.join("");
}
function showSite(s){
  SITE = s;
  const info = $("#spInfo"), btn = $("#spApply");
  if(!s.inside){ info.innerHTML = `<p>This point is outside Taiwan. Pick a place in Taiwan, Penghu, Kinmen or Matsu.</p>`; btn.disabled = true; return; }
  const notes = [];
  if(s.lng < 120) notes.push("Penghu, Kinmen and Matsu officially use TM2 zone 119 (EPSG:3825). This site uses zone 121 everywhere so that distances stay consistent; convert zone-119 coordinates before typing them in.");
  info.innerHTML = `<table class="sp-table"><tbody>${siteRows(s)}</tbody></table>${notes.length ? `<ul class="sp-notes">${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul>` : ""}<p class="mini">The Taiwan data grid (precipitation, soil, aquifer, land use) is planned; until then this point only sets where the source is.</p>`;
  btn.disabled = false;
  $("#spE").value = s.E; $("#spN").value = s.N;
  if(map){
    if(mapMarker) mapMarker.setLatLng([s.lat, s.lng]);
    else mapMarker = window.L.circleMarker([s.lat, s.lng], {radius:8, className:"sp-marker"}).addTo(map);
  }
}
function pickTwd97(E, N){ showSite(readSite(E, N)); }
function applySite(){
  const s = SITE; if(!s || !s.inside) return;
  INP.srcE = s.E; INP.srcN = s.N; INP.siteName = `E ${s.E}, N ${s.N}`; SP.fitKey = "";
  renderForm(); refreshAll(); saveAdv();
  $("#spApply").textContent = "Source location set ✓";
  setTimeout(() => { $("#spApply").textContent = "Use as the source location"; }, 1800);
}
function initMap(){
  if(map || typeof window.L === "undefined" || !document.getElementById("spMap")) return;
  const LF = window.L;
  map = LF.map("spMap", {minZoom:6, maxZoom:19, maxBounds:TW_BOUNDS, maxBoundsViscosity:0.8}).setView([23.7, 120.95], 7);
  addBaseLayers(map, "EMAP");
  map.on("click", e => { const p = wgsToTwd97(e.latlng.lat, e.latlng.lng); pickTwd97(p.E, p.N); });
  if(SITE && SITE.inside) mapMarker = LF.circleMarker([SITE.lat, SITE.lng], {radius:8, className:"sp-marker"}).addTo(map);
}
function initSite(){
  $("#spGo").addEventListener("click", () => {
    const E = Number($("#spE").value), N = Number($("#spN").value);
    const ll = isFinite(E) && isFinite(N) && $("#spE").value !== "" && $("#spN").value !== "" ? twd97ToWgs(E, N) : null;
    if(!ll || !inTaiwan(ll)){ $("#spInfo").innerHTML = "<p>Enter TWD97 / TM2 121° coordinates in metres, for example E 165347, N 2586676 (WRA observation well Budai, Chiayi).</p>"; return; }
    pickTwd97(E, N);
    if(map) map.setView([ll.lat, ll.lng], Math.max(map.getZoom(), 11));
  });
  $("#spApply").addEventListener("click", applySite);
}
'''

TERRAIN_STUB = r'''// Taiwan has no free elevation or stream query service (NLSC offers no height API without application), so the terrain
// window (slope, runoff path, terrain direction) waits for the DEM grid of step 2d. deriveTerrain() is kept for that.
async function loadTerrain(E, N){
  const key = `${Math.round(E / 25) * 25},${Math.round(N / 25) * 25}`;
  if(SP.tKey === key) return;
  SP.tKey = key; SP.terrain = null; SP.tState = "none";
  SP.tMsg = "Terrain is not available yet in the Taiwan version (the elevation grid is planned), so slope, runoff path and terrain direction are missing. Set the groundwater direction yourself.";
  if(INP.slopeSrc === "terrain"){ INP.slope = ""; INP.slopeSrc = ""; }
}
function gwDirection(){'''

LAYERS_HTML = r'''<fieldset class="sp-layers" id="spLayers"><legend class="sr-only">Support layers</legend>
                <p class="mini">Taiwan layers are being added: drinking-water source protection zones, groundwater pollution control sites, the arsenic potential areas and geology (step 2e). The Swiss layers of the original site do not apply here.</p>
                <label><input type="checkbox" id="spTerrDir" checked autocomplete="off"><span>Terrain direction arrow <small>a stand-in, not a measurement; needs the elevation grid (planned)</small></span></label>
              </fieldset>'''

PATCHES = [
    # ---------- app.js ----------
    (JS, "/* CHemTrace (formerly Swiss Metal Pathways) – app */", "/* CHemTrace Taiwan – app. Built from CHemTrace 0.13.0 (Swiss version, base/docs) by dev-tools/site_build. */"),
    (JS, '"smp-metal"', '"cht-tw-metal"', {"count": 2}),
    (JS, '"smp-theme"', '"cht-tw-theme"', {"count": 2}),
    (JS, '"smp-adv"', '"cht-tw-adv"', {"count": 2}),
    (JS, 'const APP_VERSION = "0.13.0", APP_DATE = "2026-11-03";', 'const APP_VERSION = "0.1.0", APP_DATE = "2026-11-15";'),
    (JS, "`CHemTrace – screening report · version", "`CHemTrace Taiwan – screening report · version"),
    (JS, 'L.push("CHemTrace · © 2026 Li-Ling T. ETH Zürich', 'L.push("CHemTrace Taiwan · © 2026 Li-Ling T. ETH Zürich'),
    (JS, "tag:`CHemTrace ${APP_VERSION}`", "tag:`CHemTrace Taiwan ${APP_VERSION}`"),
    (JS, '{app:"chemtrace", appVersion:APP_VERSION', '{app:"chemtrace-tw", appVersion:APP_VERSION'),
    # NABEL and the Swiss/German Hg wet deposition
    (JS, r"/\* NABEL background \(BAFU/Empa.*?\nconst HG_WETDEP = 5 / 365;[^\n]*\n",
     "// Air background for Taiwan (metals in PM10, dust deposition, gaseous Hg) is planned for phase 3; until then enter your own values.\n"
     "const NABEL = [];\n", {"regex": True}),
    (JS, ' : m === "Hg" ? {v:HG_WETDEP, src:"wet deposition about 5 µg/m²/yr (Schauinsland and German background stations)"} : null;', " : null;"),
    (JS, ' (no Swiss background value)', ' (no background value for Taiwan yet)'),
    # site lookup block
    (JS, r"/\* ================= SITE LOOKUP \(map \+ Swiss data grid\) ================= \*/\n.*?\nfunction showMapIfNeeded\(\)\{",
     SITE_BLOCK + "function showMapIfNeeded(){", {"regex": True}),
    # spread map: default place, conversion, terrain
    (JS, 'const SRC_DEF = {visp:[2634000, 1127500, "Visp"], plateau:[2612900, 1214950, "Kirchberg (BE)"], jura:[2553000, 1217000, "La Chaux-de-Fonds"], ticino:[2706350, 1096670, "Astano (TI)"]};',
     '// default place for the spread map until Taiwan presets carry their own: WRA groundwater observation well 布袋(1), Chiayi (data.gov.tw 32718)\n'
     'const SRC_DEF = {}, SRC_HOME = [165347, 2586676, "Budai, Chiayi (WRA well)"];'),
    (JS, "const d = SRC_DEF[INP.preset] || SRC_DEF.plateau;", "const d = SRC_DEF[INP.preset] || SRC_HOME;"),
    (JS, "const toLL = (E, N) => { const w = lv95ToWgs(E, N);", "const toLL = (E, N) => { const w = twd97ToWgs(E, N);"),
    (JS, r"async function loadTerrain\(E, N\)\{\n.*?\nfunction gwDirection\(\)\{", TERRAIN_STUB, {"regex": True}),
    # spread map: remove the geodienste.ch layer, NLSC tiles, Taiwan extent
    (JS, r"// geodienste\.ch fair use.*?\nfunction initSpreadMap\(\)\{", "function initSpreadMap(){", {"regex": True}),
    (JS, 'SP.map = LF.map("spMap2", {minZoom:8, maxZoom:18, maxBounds:[[45.4, 5.4], [48.2, 11.0]], maxBoundsViscosity:0.8, preferCanvas:true, zoomSnap:0.5}).setView([46.82, 8.23], 8);',
     'SP.map = LF.map("spMap2", {minZoom:7, maxZoom:19, maxBounds:TW_BOUNDS, maxBoundsViscosity:0.8, preferCanvas:true, zoomSnap:0.5}).setView([23.7, 120.95], 8);'),
    (JS, '''LF.tileLayer("https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg", {maxZoom:19, attribution:'© <a href="https://www.swisstopo.admin.ch/" target="_blank" rel="noopener">swisstopo</a>'}).addTo(SP.map);''',
     'addBaseLayers(SP.map, "EMAP01");   // grey by default so the red and amber zones stand out; colour and aerial photo in the layer menu'),
    (JS, r"  SP\.ov\.cant = null;[^\n]*\n  SP\.ov\.hk100 = [^\n]*\n  SP\.ov\.tracer = [^\n]*\n",
     "  // Taiwan support layers (protection zones, pollution control sites, arsenic potential areas, geology) come in step 2e\n", {"regex": True}),
    (JS, "const p = wgsToLv95(e.latlng.lat, e.latlng.lng), s = srcOf();", "const p = wgsToTwd97(e.latlng.lat, e.latlng.lng), s = srcOf();"),
    (JS, '    if(cb.dataset.ov === "cant"){ cantWms(cb.checked); return; }\n', ""),
    (JS, '  SP.map.on("moveend", () => { if(CW.on) cantSchedule(); });\n', ""),
    (JS, 'E ${Math.round(s.E).toLocaleString("de-CH")}, N ${Math.round(s.N).toLocaleString("de-CH")}', 'E ${Math.round(s.E).toLocaleString("en-US")}, N ${Math.round(s.N).toLocaleString("en-US")}'),
    (JS, "Set the real direction from the cantonal groundwater map or your wells.", "Set the real direction from groundwater-level contours of nearby WRA observation wells or from your own wells."),
    (JS, '>Use preset place</button>', '>Use default place</button>'),
    (JS, r'  const a = \$\("#spGeoLink"\); if\(a\) a\.href = `https://map\.geo\.admin\.ch[^\n]*\n', "", {"regex": True}),
    # ---------- index.html ----------
    (IDX, "<title>CHemTrace</title>", "<title>CHemTrace Taiwan</title>", {"count": 2}),   # page title and the logo's SVG title
    (IDX, 'aria-label="CHemTrace"', 'aria-label="CHemTrace Taiwan"'),
    (IDX, "</svg></h1>", '</svg><span class="logo-tw">Taiwan</span></h1>'),
    (IDX, '<meta name="description" content="CHemTrace follows contaminants through Swiss landscapes: what forms they take, where they go, how they reach people and where to trap them, with a screening calculator for Swiss sites. Arsenic, mercury and lead now; more contaminants are being added.">',
     '<meta name="description" content="CHemTrace Taiwan follows contaminants through Taiwanese landscapes: what forms they take, where they go, how they reach people and where to trap them, with a screening calculator. Arsenic, mercury and lead now; in development.">'),
    (IDX, '<span class="kicker">Contaminants in Swiss landscapes · now As · Hg · Pb, more in progress</span>',
     '<span class="kicker">Taiwan · contaminants in soil, air, groundwater, rivers and lakes · now As · Hg · Pb · in development</span>'),
    (IDX, "Trace contaminants through glacier, rock, soil, air, river, lake and groundwater in Switzerland:",
     "Trace contaminants through rock, soil, air, river, lake and groundwater in Taiwan:"),
    (IDX, '<label class="mini" for="presetSel">Swiss site preset</label>', '<label class="mini" for="presetSel">Site preset</label>'),
    (IDX, '<div class="sp-head"><h3>Pick a site in Switzerland</h3><p>Click the map or enter LV95 coordinates. The site\'s climate, soil, aquifer and background values can then fill the inputs below.</p></div>',
     '<div class="sp-head"><h3>Pick a site in Taiwan</h3><p>Click the map or enter TWD97 coordinates (TM2 121°, EPSG:3826). The point becomes the source location on the spread map. Site values (climate, soil, aquifer) are typed in below until the Taiwan data grid is built.</p></div>'),
    (IDX, '<div class="sp-map" id="spMap" aria-label="Map of Switzerland: click to choose a site"></div>', '<div class="sp-map" id="spMap" aria-label="Map of Taiwan: click to choose a site"></div>'),
    (IDX, '<label class="mini" for="spE">E (LV95)</label><input id="spE" type="number" step="any" inputmode="decimal" placeholder="2634000">',
     '<label class="mini" for="spE">E (TWD97)</label><input id="spE" type="number" step="any" inputmode="decimal" placeholder="165347">'),
    (IDX, '<label class="mini" for="spN">N (LV95)</label><input id="spN" type="number" step="any" inputmode="decimal" placeholder="1127500">',
     '<label class="mini" for="spN">N (TWD97)</label><input id="spN" type="number" step="any" inputmode="decimal" placeholder="2586676">'),
    (IDX, '<div class="sp-info" id="spInfo"><p>No site chosen yet. Values come from a 1 km grid built from MeteoSwiss, KOBO soil maps, the geochemical soil atlas, the hydrogeological map 1:500,000 and BFS land-use statistics.</p></div>',
     '<div class="sp-info" id="spInfo"><p>No site chosen yet.</p></div>'),
    (IDX, '<button class="btn" id="spApply" disabled>Fill inputs from this site</button>', '<button class="btn" id="spApply" disabled>Use as the source location</button>'),
    (IDX, r'<fieldset class="sp-layers" id="spLayers">.*?</fieldset>', LAYERS_HTML, {"regex": True}),
    (IDX, "<span>Support layers<small>Protection zones, hydrogeology, tracer tests</small></span>", "<span>Support layers<small>Taiwan layers in preparation</small></span>"),
    (IDX, "Version 0.13.0, 3 November 2026", "CHemTrace Taiwan 0.1.0 (in development), 15 November 2026", {"count": 2}),
    (IDX, "Built from literature and Swiss federal sources, checked October 2026.",
     "Taiwan version in development, built from the Swiss CHemTrace 0.13.0; Taiwan standards checked November 2026, other content is still partly Swiss."),
    (IDX, "Map data © swisstopo; climate data: Source MeteoSwiss; soil maps © KOBO (CC BY 4.0); soil atlas © FOEN/Agroscope; land use © BFS.",
     "Base map © NLSC (內政部國土測繪中心); groundwater data © MOENV and WRA; boreholes © GSMMA; open government data under OGDL-Taiwan-1.0."),
    # ---------- styles.css: CJK fallback fonts; muted colours on the NLSC base map so plume colours stand out ----------
    (CSS, '--f-display:"Archivo", "Helvetica Neue", Arial, sans-serif;', '--f-display:"Archivo", "Helvetica Neue", Arial, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;'),
    (CSS, '--f-body:"Archivo", "Helvetica Neue", Arial, sans-serif;', '--f-body:"Archivo", "Helvetica Neue", Arial, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;'),
    (CSS, '--f-mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;', '--f-mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, "Noto Sans Mono CJK TC", "Microsoft JhengHei", monospace;'),
    (CSS, "h1.logo .logo-svg{display:block; height:clamp(28px, 3.3vw, 38px); width:auto; overflow:visible}",
     "h1.logo .logo-svg{display:block; height:clamp(28px, 3.3vw, 38px); width:auto; overflow:visible}\n"
     "h1.logo{display:flex; align-items:flex-end; gap:10px}\n"
     "h1.logo .logo-tw{font-family:var(--f-mono); font-size:clamp(13px, 1.4vw, 16px); line-height:1; letter-spacing:.12em; text-transform:uppercase; color:var(--ink-2); padding-bottom:2px}"),
]


PATCHES += [
    (JS, '["Release point","Coordinates in LV95, height or depth, stack exit velocity and temperature.","swisstopo, user"],',
         '["Release point","Coordinates in TWD97 (EPSG:3826), height or depth, stack exit velocity and temperature.","user"],'),
    (JS, '["Coordinates and elevation","EPSG:2056 (LV95); elevation drives temperature, snow cover and runoff.","swissALTI3D"],',
         '["Coordinates and elevation","TWD97 / TM2 121° (EPSG:3826); elevation drives temperature, snow cover and runoff.","elevation grid planned (DEM)"],'),
    (JS, 'help:"Filled from swisstopo terrain when the spread map loads.', 'help:"Will be filled from terrain once the Taiwan elevation grid exists; type it in until then.'),
    (JS, 'help:"Recommended: read it from the cantonal groundwater map or your own wells, or click Set direction on the spread map. Empty: the terrain direction stands in, as support only.", src:"Cantonal groundwater maps; FOEN hydrogeological map 1:100,000"',
         'help:"Recommended: read it from groundwater-level contours of nearby WRA observation wells or from your own wells, or click Set direction on the spread map.", src:"WRA groundwater observation wells and water levels (data.gov.tw 32718, 32717)"'),
    (JS, '{k:"srcE", tab:"rel", label:"Source location E (LV95)", unit:"m", min:2480000, max:2840000, optional:true, help:"Set it on the spread map with Move source. Empty: the preset\'s place, or the site you filled from the map."}',
         '{k:"srcE", tab:"rel", label:"Source location E (TWD97)", unit:"m", min:-60000, max:380000, optional:true, help:"TM2 121° (EPSG:3826). Set it on the spread map with Move source, or pick a site on the map above. Empty: the default place."}'),
    (JS, '{k:"srcN", tab:"rel", label:"Source location N (LV95)", unit:"m", min:1070000, max:1300000, optional:true}',
         '{k:"srcN", tab:"rel", label:"Source location N (TWD97)", unit:"m", min:2350000, max:2950000, optional:true}'),
    (JS, '"map location LV95 " + I.siteName', '"map location TWD97 " + I.siteName', {"count": 2}),
    (JS, 'L.push("Turn on <b>Cantonal protection zones</b> to see whether S1–S3 zones of drinking-water wells or springs lie in the coloured area.");',
         'L.push("Check whether drinking-water source protection zones or water intakes lie in the coloured area; the Taiwan protection-zone layer is planned.");'),
    (JS, "<li><b>Spread map.</b> Terrain comes from the swisstopo profile service on a 50 m grid over a 2.4 km window.",
         "<li><b>Spread map.</b> In the Taiwan version the terrain window is not available yet; it needs the planned elevation grid. The method is kept for it: a 50 m grid over a 2.4 km window."),
    (JS, "until it meets a stream of the swisstopo VECTOR25 river network,", "until it meets a stream of the river network,"),
    (IDX, "Terrain and streams: swisstopo, 2.4 km window at 50 m.", "Terrain and streams: not yet available for Taiwan (elevation grid planned)."),
]

# the English pages keep their content until step 2g, but use the new storage keys
for _p in ("manual.html", "validation.html", "assumptions.html"):
    PATCHES += [(_p, 'localStorage.getItem("smp-theme")', 'localStorage.getItem("cht-tw-theme")'),
                (_p, 'localStorage.getItem("smp-metal")', 'localStorage.getItem("cht-tw-metal")')]
