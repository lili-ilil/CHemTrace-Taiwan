// Numerical regression: runs SMP.run for every metal × medium × land use and writes the results as JSON.
// Usage: node dev-tools/tests/t_regress.js out.json   (server on port 8765, site/ as root)
// Compare two outputs with: node dev-tools/tests/t_regress.js --diff a.json b.json
const fs = require('fs');
if(process.argv[2] === '--diff'){
  const a = JSON.parse(fs.readFileSync(process.argv[3])), b = JSON.parse(fs.readFileSync(process.argv[4]));
  let n = 0, bad = 0;
  for(const k of Object.keys(a)){ n++; if(JSON.stringify(a[k]) !== JSON.stringify(b[k])){ bad++; if(bad <= 5) console.log('DIFF', k); } }
  console.log(`${n} cases, ${bad} differ` + (Object.keys(b).length !== n ? `, case count ${n} vs ${Object.keys(b).length}` : ''));
  process.exit(bad ? 1 : 0);
}
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(600);
  const out = await p.evaluate(() => {
    const o = {};
    for(const m of ["As", "Hg", "Pb"]) for(const medium of ["soil", "air", "road", "gw", "river", "glacier"]) for(const land of ["garden", "agri"]){
      if(medium === "road" && m !== "Pb") continue;
      const r = SMP.run(m, {medium, land});
      o[`${m}|${medium}|${land}`] = r.results.map(x => [x.id, x.value, x.tag, x.p5, x.p95]);
    }
    return o;
  });
  fs.writeFileSync(process.argv[2] || 'regress.json', JSON.stringify(out));
  console.log(Object.keys(out).length, 'cases written'); await b.close();
})();
