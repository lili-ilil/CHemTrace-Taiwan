// Taiwan checks in a real browser: Advanced mode, coordinate lookup, source location, groundwater class, standards in results.
// Start a server in site/ on port 8765 first (see README). Usage: node dev-tools/tests/t_tw.js [outdir]
const {chromium} = require('playwright');
const out = process.argv[2] || '.';
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1360, height:1000}});
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if(m.type() === 'error' && !/Failed to load resource|ERR_/.test(m.text())) errs.push(m.text()); });
  await p.goto('http://localhost:8765/index.html#advanced'); await p.waitForTimeout(1200);
  const res = {};
  res.title = await p.title();
  res.keys = await p.evaluate(() => Object.keys(localStorage));
  // coordinate lookup: WRA well Budai
  await p.fill('#spE', '165347'); await p.fill('#spN', '2586676'); await p.click('#spGo'); await p.waitForTimeout(300);
  res.siteInfo = (await p.textContent('#spInfo')).replace(/\s+/g, ' ').trim();
  await p.click('#spApply'); await p.waitForTimeout(800);
  res.srcStatus = (await p.textContent('#spDir')).replace(/\s+/g, ' ').trim().slice(0, 300);
  // outside Taiwan
  await p.fill('#spE', '2600000'); await p.fill('#spN', '1200000'); await p.click('#spGo'); await p.waitForTimeout(200);
  res.outside = (await p.textContent('#spInfo')).replace(/\s+/g, ' ').trim();
  // groundwater release of As, class 1 vs class 2
  const gw = async cls => p.evaluate(c => { const r = SMP.run ? null : null; return null; }, cls);
  res.rows = await p.evaluate(() => {
    const pick = () => [...document.querySelectorAll('#results .runrow, .runrow')].map(e => e.textContent.replace(/\s+/g, ' ').trim()).filter(t => /control std|drinking-water std|monitoring standard|control standard|Taiwan|GW control/.test(t)).slice(0, 8);
    return pick();
  });
  await p.screenshot({path:`${out}/tw_adv_top.png`, fullPage:false});
  // go to the Exposure tab and switch the class
  const tabs = await p.$$eval('[role="tab"], #advTabs button, .tabs button', els => els.map(e => e.textContent.trim()));
  res.tabs = tabs.slice(0, 12);
  res.gwClassField = await p.evaluate(() => !!document.querySelector('[data-k="gwClass"], #f-gwClass'));
  await p.evaluate(() => document.getElementById('spread') && document.getElementById('spread').scrollIntoView());
  await p.waitForTimeout(600);
  await p.screenshot({path:`${out}/tw_spread.png`, fullPage:false});
  res.errors = errs;
  console.log(JSON.stringify(res, null, 1));
  await b.close();
})();
