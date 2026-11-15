const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const errs=[];
for(const vw of [1400,400]){const p=await b.newPage({viewport:{width:vw,height:900}});p.on('pageerror',e=>errs.push(e.message));
for(const pg of ['manual.html','validation.html']){await p.goto('http://localhost:8765/'+pg);await p.waitForTimeout(300);
console.log(vw,pg,'ov',await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth),'broken',await p.evaluate(()=>[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.querySelector(a.getAttribute('href'))).map(a=>a.getAttribute('href'))));}
await p.close();}
console.log(errs);await b.close();})();
