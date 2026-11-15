const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(800);
  const cases = {};
  for(const m of ['As','Hg','Pb']) for(const pre of ['plateau','ticino','jura','visp']) for(const med of ['soil','gw']) for(const alk of [null, 250]) cases[`${m}_${pre}_${med}_${alk?'alk':'noalk'}`] = [m, Object.assign({preset:pre, medium:med}, alk ? {wcAlk:alk, wcCa:80} : {})];
  fs.mkdirSync('pq_more', {recursive:true});
  for(const [k,[m,inp]] of Object.entries(cases)){
    const f = await p.evaluate(([m,inp]) => window.CHemTrace.exportFile('phreeqc', m, inp), [m,inp]);
    fs.writeFileSync('pq_more/' + k + '.pqi', f.text);
  }
  await b.close();
})();
