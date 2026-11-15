// Run the original CHemTrace redox ladder (redoxLadder in base/docs/assets/js/app.js) outside the browser.
// The function and the constants it needs are copied from app.js at run time, unchanged, so the result is what
// the Swiss website 0.13.0 computes. Nothing in base/ is modified.
//
// Usage: node tools/ladder_node.mjs < inputs.json > outputs.json
//   inputs.json: [{id, preset, inputs:{o2In, no3In, so4In, docIn, ...}}, ...]
//   Each run starts from BASE + PRESETS[preset].v (default preset "plateau"), then the given inputs, with rlOn "on".
// Output: [{id, cls, teap, s1, s2, tMn, tEx, v, e, cap}, ...]
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appPath = path.resolve(here, "..", "base", "docs", "assets", "js", "app.js");
const src = fs.readFileSync(appPath, "utf8");

function block(startRe) {
  // returns the source text from the match to the end of its balanced {...} plus a trailing ';' if present
  const m = startRe.exec(src);
  if (!m) throw new Error("not found in app.js: " + startRe);
  let i = src.indexOf("{", m.index), depth = 0, j = i;
  for (; j < src.length; j++) {
    const c = src[j];
    if (c === "{") depth++;
    else if (c === "}") { depth--; if (depth === 0) break; }
  }
  let end = j + 1;
  if (src[end] === ";") end++;
  return src.slice(m.index, end);
}
function line(startRe) {
  const m = startRe.exec(src);
  if (!m) throw new Error("not found in app.js: " + startRe);
  const e = src.indexOf("\n", m.index);
  return src.slice(m.index, e);
}

const parts = [
  line(/^const YEAR_S = .*$/m),
  line(/^const num = .*$/m),
  line(/^const LAD_ZONE = .*$/m),
  line(/^const HC_E = .*$/m),
  block(/^function orgType\(I\)/m),
  block(/^function orgElectrons\(I\)/m),
  block(/^function redoxLadder\(I\)/m),
  block(/^const PRESETS = /m),
  block(/^const BASE = /m),
];
const code = parts.join("\n") + "\n;globalThis.__api = {redoxLadder, PRESETS, BASE};";
const ctx = { Math, Number, Infinity, isFinite, Object, JSON, console };
vm.createContext(ctx);
vm.runInContext(code, ctx);
const { redoxLadder, PRESETS, BASE } = ctx.__api;

const runs = JSON.parse(fs.readFileSync(0, "utf8"));
const out = runs.map(r => {
  const pre = PRESETS[r.preset || "plateau"];
  if (!pre) throw new Error("unknown preset " + r.preset);
  const I = Object.assign(JSON.parse(JSON.stringify(BASE)), JSON.parse(JSON.stringify(pre.v)), r.inputs || {}, { rlOn: "on" });
  const L = redoxLadder(I);
  return { id: r.id, cls: L.cls, teap: L.teap, s1: L.s1, s2: L.s2, tMn: L.tMn, tEx: L.tEx, v: L.v, T: L.T,
           e: L.e, cap: L.cap, used: { K: I.K, grad: I.grad, ne: I.ne, aqFe: I.aqFe, aqMn: I.aqMn, budT: I.budT } };
});
process.stdout.write(JSON.stringify(out));
