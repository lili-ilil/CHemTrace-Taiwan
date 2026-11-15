const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(800);
const r=await p.evaluate(()=>{const t0=performance.now();const r=SMP.selfTest();r.ms=performance.now()-t0;return r;});
console.log(r.version, r.passed+'/'+r.total, 'ms', r.ms.toFixed(0));r.checks.forEach(c=>console.log((c.pass?'PASS ':'FAIL ')+c.check+' — '+c.detail));
console.log(errs);await b.close();})();
