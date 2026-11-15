const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(process.argv[2] || 'http://localhost:8765/index.html'); await p.waitForTimeout(800);
  const cases = { soilAs_off: ['As', {preset:'plateau', medium:'soil'}], soilAs_lad: ['As', {preset:'plateau', medium:'soil', rlOn:'on'}], soilAs_fuel: ['As', {preset:'plateau', medium:'soil', rlOn:'on', orgType:'fuel', orgHc:20}], soilPb_fuel: ['Pb', {preset:'plateau', medium:'soil', rlOn:'on', orgType:'fuel', orgHc:20}] };
  fs.mkdirSync(process.argv[3] || 'pq_var', {recursive:true});
  for(const [k,[m,inp]] of Object.entries(cases)){
    const f = await p.evaluate(([m,inp]) => window.CHemTrace.exportFile('phreeqc', m, inp), [m,inp]);
    fs.writeFileSync((process.argv[3] || 'pq_var') + '/' + k + '.pqi', f.text);
  }
  await b.close();
})();
