"""Step 2b (part 1): English / Traditional Chinese.

- index.html stays English. index.zh.html is a Chinese copy of it, made in build() below from the HTML pairs in zh_strings.py.
- index.zh.html loads assets/js/i18n-zh.js (window.CHT_ZH, written from zh_strings.T and zh_strings.P) before app.js.
- app.js gets tr(): exact match in CHT_ZH.t, then the regular expressions in CHT_ZH.p, else the English text is kept.
  The data tables (metals, compartments, fields, tabs, chemical forms, data sources) are translated once at start-up,
  and the form, tabs and result cards pass their text through tr().
- A Language switch (EN / 中文) next to Theme. The choice is kept in localStorage (cht-tw-lang); index.html moves to the
  Chinese page when the stored choice is zh.
- The manual, validation and assumptions pages stay English (decision of 15 Nov 2026).
Part 2 will translate the help texts, tab notes, result explanations and the report, after the Explore content has been
rewritten for Taiwan (it is still the Swiss text).
"""
import json
import zh_strings as ZH

JS, IDX = "assets/js/app.js", "index.html"

I18N_CORE = r'''"use strict";
/* ---------- language: English by default; index.zh.html loads assets/js/i18n-zh.js (window.CHT_ZH) first ---------- */
const ZH = window.CHT_ZH || null, LANG = ZH ? "zh" : "en";
const TR_P = ZH ? ZH.p.map(([re, out]) => [new RegExp(re), out]) : [];
function tr(s){
  if(!ZH || typeof s !== "string" || !s) return s;
  const hit = ZH.t[s]; if(hit != null) return hit;
  for(const [re, out] of TR_P) if(re.test(s)) return s.replace(re, out);
  return s;
}
// translate the strings of a data table in place; identifiers (keys such as k, id, tab) and option values stay as they are
const TR_SKIP = new Set(["k", "id", "tab", "type", "sp", "unit", "preset", "c", "base"]);
function trDeep(o){
  if(!ZH || o == null || typeof o !== "object") return o;
  if(Array.isArray(o)){
    if(o.length === 2 && typeof o[0] === "string" && typeof o[1] === "string" && /^[a-z0-9_]+$/i.test(o[0]) && o[0] === o[0].toLowerCase()){ o[1] = tr(o[1]); return o; }
    for(let i = 0; i < o.length; i++){ if(typeof o[i] === "string") o[i] = tr(o[i]); else trDeep(o[i]); }
    return o;
  }
  for(const k of Object.keys(o)){ if(TR_SKIP.has(k)) continue; const v = o[k]; if(typeof v === "string") o[k] = tr(v); else if(v && typeof v === "object") trDeep(v); }
  return o;
}'''

LANG_HTML = '''    <div class="ctl"><span class="ctl-label" id="lblLang">Language</span>
      <div class="seg" role="radiogroup" aria-labelledby="lblLang" id="langSeg">
        <button role="radio" aria-checked="true" data-lang="en" lang="en">EN</button>
        <button role="radio" aria-checked="false" data-lang="zh" lang="zh-Hant">中文</button>
      </div></div>
    <div class="ctl ctl-end"><span class="ctl-label" id="lblTheme">Theme</span>'''

LANG_JS = r'''const themeSeg = $("#themeSeg");
document.querySelectorAll("#langSeg button").forEach(b => b.addEventListener("click", () => {
  const l = b.dataset.lang; if(l === LANG) return;
  try{ localStorage.setItem("cht-tw-lang", l); }catch(e){}
  location.href = (l === "zh" ? "index.zh.html" : "index.html") + location.hash;
}));'''

REDIRECT = '''<script>try{if(localStorage.getItem("cht-tw-lang")==="zh")location.replace("index.zh.html"+location.hash)}catch(e){}</script>
<link rel="alternate" hreflang="zh-Hant" href="index.zh.html">
<script src="assets/vendor/leaflet/leaflet.js" defer></script>'''

PATCHES = [
    (JS, '(function(){\n"use strict";', "(function(){\n" + I18N_CORE),
    # translate data tables once, before anything is drawn from them (DATA is drawn where it is defined)
    (JS, '\n$("#dataGrid").innerHTML = DATA.map(', '\ntrDeep(DATA);\n$("#dataGrid").innerHTML = DATA.map('),
    (JS, "\nconst TABNOTES = {", "\nif(ZH) [METALS, C, FIELDS, TABS, FORMS].forEach(trDeep);\nconst TABNOTES = {"),
    # form
    (JS, "const lab = typeof f.label === \"function\" ? f.label(INP) : f.label;", "const lab = tr(typeof f.label === \"function\" ? f.label(INP) : f.label);"),
    (JS, '${String(v) === String(val) ? " selected" : ""}>${esc(l)}</option>', '${String(v) === String(val) ? " selected" : ""}>${esc(tr(l))}</option>'),
    (JS, '` placeholder="${esc(f.ph || "calculated")}"`', '` placeholder="${esc(tr(f.ph || "calculated"))}"`'),
    (JS, '`<span class="help">${esc(typeof f.help === "function" ? f.help(INP) : f.help)}</span>`', '`<span class="help">${esc(tr(typeof f.help === "function" ? f.help(INP) : f.help))}</span>`'),
    (JS, '${note ? `<p class="tabnote">${esc(note)}</p>` : ""}', '${note ? `<p class="tabnote">${esc(tr(note))}</p>` : ""}'),
    # result cards and the short result rows
    (JS, '<div class="rl"><span>${esc(r.label)}</span><span class="pill ${r.status}">${esc(r.tag)}</span></div>', '<div class="rl"><span>${esc(tr(r.label))}</span><span class="pill ${r.status}">${esc(tr(r.tag))}</span></div>'),
    (JS, '<div class="rr">${esc(r.ref)}</div><div class="rh">${esc(r.how)}</div>${r.bench ? `<div class="bench"><b>Measured</b>${esc(r.bench)}</div>` : ""}',
     '<div class="rr">${esc(tr(r.ref))}</div><div class="rh">${esc(tr(r.how))}</div>${r.bench ? `<div class="bench"><b>${tr("Measured")}</b>${esc(tr(r.bench))}</div>` : ""}'),
    (JS, 'const runRow = r => `<div class="runrow"><span>${esc(r.label)}<b>', 'const runRow = r => `<div class="runrow"><span>${esc(tr(r.label))}<b>'),
    (JS, '`<small class="rr90">90% range ${fmt(r.mc.p5)}–${fmt(r.mc.p95)}</small>` : ""}</span><span class="pill ${r.status}">${esc(r.tag)}</span></div>`;',
     '`<small class="rr90">${tr("90% range")} ${fmt(r.mc.p5)}–${fmt(r.mc.p95)}</small>` : ""}</span><span class="pill ${r.status}">${esc(tr(r.tag))}</span></div>`;'),
    # site picker table and button texts
    (JS, 'const add = (k, v, src) => rows.push(`<tr><td>${esc(k)}</td><td>${v}</td><td>${esc(src)}</td></tr>`);\n  add("Coordinates"',
     'const add = (k, v, src) => rows.push(`<tr><td>${esc(tr(k))}</td><td>${tr(v)}</td><td>${esc(tr(src))}</td></tr>`);\n  add("Coordinates"'),
    (JS, '<p class="mini">The Taiwan data grid (precipitation, soil, aquifer, land use) is planned; until then this point only sets where the source is.</p>`;',
     '<p class="mini">${tr("The Taiwan data grid (precipitation, soil, aquifer, land use) is planned; until then this point only sets where the source is.")}</p>`;'),
    (JS, 'info.innerHTML = `<p>This point is outside Taiwan. Pick a place in Taiwan, Penghu, Kinmen or Matsu.</p>`;', 'info.innerHTML = `<p>${tr("This point is outside Taiwan. Pick a place in Taiwan, Penghu, Kinmen or Matsu.")}</p>`;'),
    (JS, '$("#spApply").textContent = "Source location set ✓";\n  setTimeout(() => { $("#spApply").textContent = "Use as the source location"; }, 1800);',
     '$("#spApply").textContent = tr("Source location set ✓");\n  setTimeout(() => { $("#spApply").textContent = tr("Use as the source location"); }, 1800);'),
    (JS, 'BASEMAPS.forEach(([id, name]) => { layers[name] = LF.tileLayer(', 'BASEMAPS.forEach(([id, name0]) => { const name = tr(name0); layers[name] = LF.tileLayer('),
    (JS, "layers[(BASEMAPS.find(b => b[0] === def) || BASEMAPS[0])[1]].addTo(m);", "layers[tr((BASEMAPS.find(b => b[0] === def) || BASEMAPS[0])[1])].addTo(m);"),
    (JS, '$("#playTxt").textContent = on ? "Pause" : "Play";', '$("#playTxt").textContent = tr(on ? "Pause" : "Play");'),
    (JS, '$("#loadExample").textContent = "Load example: " + EXAMPLES[S.metal].short;', '$("#loadExample").textContent = tr("Load example: " + EXAMPLES[S.metal].short);'),
    (JS, '$("#spPlay").innerHTML = on ? "❚❚ Pause" : "▶ Play";', '$("#spPlay").innerHTML = tr(on ? "❚❚ Pause" : "▶ Play");'),
    # language switch
    (JS, 'const themeSeg = $("#themeSeg");', LANG_JS),
    (IDX, '    <div class="ctl ctl-end"><span class="ctl-label" id="lblTheme">Theme</span>', LANG_HTML),
    (IDX, '<script src="assets/vendor/leaflet/leaflet.js" defer></script>', REDIRECT),
]


def build(F):
    """Write index.zh.html and assets/js/i18n-zh.js after the patches above."""
    s = F.get(IDX)
    s = s.replace('<html lang="en">', '<html lang="zh-Hant">', 1)
    s = s.replace('<script>try{if(localStorage.getItem("cht-tw-lang")==="zh")location.replace("index.zh.html"+location.hash)}catch(e){}</script>\n'
                  '<link rel="alternate" hreflang="zh-Hant" href="index.zh.html">',
                  '<link rel="alternate" hreflang="en" href="index.html">', 1)
    s = s.replace('<script src="assets/js/app.js" defer></script>', '<script src="assets/js/i18n-zh.js" defer></script>\n<script src="assets/js/app.js" defer></script>', 1)
    s = s.replace('aria-checked="true" data-lang="en"', 'aria-checked="false" data-lang="en"', 1).replace('aria-checked="false" data-lang="zh"', 'aria-checked="true" data-lang="zh"', 1)
    missing = []
    for en, zh in ZH.HTML:
        if en not in s:
            missing.append(en)
        s = s.replace(en, zh)
    if missing:
        raise SystemExit("[step_2b] index.zh.html: English text not found:\n  " + "\n  ".join(m[:90] for m in missing))
    F.put("index.zh.html", s)
    F.put("assets/js/i18n-zh.js", "/* CHemTrace Taiwan: Traditional Chinese strings, generated from dev-tools/site_build/zh_strings.py. Do not edit here. */\n"
          "window.CHT_ZH = " + json.dumps({"t": ZH.T, "p": ZH.P}, ensure_ascii=False, indent=0) + ";\n")
