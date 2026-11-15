const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(800);
  const cases = {
    default_gw: ['As', {preset:'plateau', medium:'gw'}],
    measured_gw: ['As', {preset:'plateau', medium:'gw', rlOn:'on', orgType:'leachate', orgCod:300, wcT:11, o2In:0.5, no3In:2, so4In:45, wcCa:95, wcMg:18, wcNa:25, wcK:4, wcCl:40, wcAlk:380, wcFe:2.5, wcMn:0.6, wcH2S:0.05, wcEh:-50}],
    partial_soil: ['Pb', {preset:'plateau', medium:'soil', wcCa:80, wcAlk:250}],
    acid_soil: ['Pb', {preset:'ticino', medium:'soil', wcCl:12, wcNa:6}],
    fuel_ladder: ['As', {preset:'plateau', medium:'soil', rlOn:'on', orgType:'fuel', orgHc:20}],
  };
  const out = {};
  for(const [k,[m,inp]] of Object.entries(cases)){
    const f = await p.evaluate(([m,inp]) => window.CHemTrace.exportFile('phreeqc', m, inp), [m,inp]);
    fs.writeFileSync('pq_new/'+k+'.pqi', f.text); out[k] = f.text.split('\n').filter(l=>/^ {4}(temp|pe|Ca|Mg|Na|K|Cl|S\(6\)|N\(5\)|Alkalinity|C\(4\)|Fe\(2\)|Mn\(2\)|S\(-2\)|O\(0\))\b|all major|come from|ASSUMED\. Enter|Species distrib|predominant/.test(l)).slice(0,22);
  }
  const lad = await p.evaluate(() => { const r = window.CHemTrace.run('As', {preset:'plateau', medium:'soil', rlOn:'on', orgType:'fuel', orgHc:20}); return {row:r.results.find(x=>x.id==='ladder'), ladder:r.ladder}; });
  console.log(JSON.stringify(out, null, 1)); console.log(JSON.stringify(lad, null, 1)); console.log(errs);
  await b.close();
})();
