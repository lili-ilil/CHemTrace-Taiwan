// Writes 12_地區預設_嘉南平原.md from the built site (site/assets/js/app.js and i18n-zh.js), so the list always matches the code.
// Usage (from the CHemTrace-TW folder, after build_site.py):  node dev-tools/site_build/make_preset_doc.js
// The PRESETS and FIELDS literals and the Chinese strings are evaluated in a Node VM; nothing is fetched.
const fs = require("fs"), path = require("path"), vm = require("vm");
const ROOT = path.resolve(__dirname, "..", ".."), JS = fs.readFileSync(path.join(ROOT, "site/assets/js/app.js"), "utf8");
const ctx = {window:{}, S:{metal:"As"}, Math}; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(ROOT, "site/assets/js/i18n-zh.js"), "utf8"), ctx);
const ZH = ctx.window.CHT_ZH, TRP = ZH.p.map(([re, out]) => [new RegExp(re), out]);
const tr = s => { if(ZH.t[s] != null) return ZH.t[s]; for(const [re, out] of TRP) if(re.test(s)) return s.replace(re, out); return s; };

function literal(start){                      // text of the {...} or [...] literal that begins at index start
  const open = JS[start], close = open === "{" ? "}" : "]"; let d = 0, q = null;
  for(let i = start; i < JS.length; i++){
    const c = JS[i];
    if(q){ if(c === "\\") i++; else if(c === q) q = null; continue; }
    if(c === '"' || c === "'" || c === "`") q = c;
    else if(c === open) d++;
    else if(c === close && --d === 0) return JS.slice(start, i + 1);
  }
  throw new Error("literal not closed");
}
function evalLit(src){                       // helper functions the literal refers to are stubbed; only labels and keys are read
  for(let i = 0; i < 50; i++){
    try{ return vm.runInContext("(" + src + ")", ctx); }
    catch(e){ const m = /^(\w+) is not defined/.exec(e.message); if(!(e instanceof ReferenceError || e.name === "ReferenceError") || !m) throw e; ctx[m[1]] = () => ""; }
  }
  throw new Error("too many unknown names");
}
const PRESETS = evalLit(literal(JS.indexOf("{", JS.indexOf("const PRESETS = {"))));
const FIELDS = evalLit(literal(JS.indexOf("[", JS.indexOf("const FIELDS = ["))));
const METALS = Object.keys(evalLit(literal(JS.indexOf("{", JS.indexOf("const METALS = {")))));

const P = PRESETS.chianan, src = P.src || {}, rows = [], asm = [];
const label = (k, m) => { const f = FIELDS.find(x => x.k === k); if(!f) return k; ctx.S.metal = m || "As"; const l = typeof f.label === "function" ? f.label() : f.label; return `${tr(l)}（\`${m ? k + "." + m : k}\`）`; };
for(const [k, v] of Object.entries(P.v)){
  if(v && typeof v === "object"){
    for(const m of METALS.filter(mm => mm in v)){ const s = src[k] && src[k][m]; (s ? rows : asm).push([label(k, m), v[m], s]); }
  } else { const s = src[k]; (s ? rows : asm).push([label(k), v, s]); }
}
const fmt = x => typeof x === "number" ? (x !== 0 && Math.abs(x) < 1e-3 ? x.toExponential() : String(x)) : x;
const L = [];
L.push("# 地區預設：嘉南平原（2f）", "");
L.push(`整理日期：${new Date().toISOString().slice(0, 10)}。網站預設在 \`dev-tools/site_build/step_2f.py\`（\`PRESETS.chianan\`），鎘、鎳的背景值在 \`step_cd.py\`、\`step_ni.py\`。這份清單由 \`dev-tools/site_build/make_preset_doc.js\` 從建構好的網站程式產生，兩邊一致；要改數值請改程式，再重新產生。`, "");
L.push("依你的決定：查不到台灣出處的數值，保留模型的通用預設值（取自原本的瑞士高原預設），在表單上標「ASSUMED · 無台灣出處」。", "");
L.push(`共 ${rows.length + asm.length} 個數值：${rows.length} 個有台灣出處或依決定設定，${asm.length} 個是 ASSUMED。`, "");
L.push("## 有出處的數值", "", "| 參數 | 數值 | 出處 |", "|---|---|---|");
rows.forEach(([l, v, s]) => L.push(`| ${l} | ${fmt(v)} | ${s} |`));
L.push("", "## ASSUMED（沒有台灣出處，沿用通用預設值）", "", "| 參數 | 預設值 |", "|---|---|");
asm.forEach(([l, v]) => L.push(`| ${l} | ${fmt(v)} |`));
L.push("", fs.readFileSync(path.join(__dirname, "preset_doc_notes.md"), "utf8").trim(), "");
fs.writeFileSync(path.join(ROOT, "12_地區預設_嘉南平原.md"), L.join("\n"));
console.log(`12_地區預設_嘉南平原.md: ${rows.length} sourced, ${asm.length} ASSUMED`);
