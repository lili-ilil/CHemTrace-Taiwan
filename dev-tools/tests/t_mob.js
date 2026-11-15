const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const [name,w,h,scheme] of [['air-mobile',400,2400,'light'],['air-dark',1400,1200,'dark']]) {
    const ctx = await browser.newContext({viewport:{width:w,height:h}, colorScheme:scheme}); const page = await ctx.newPage();
    const errs=[]; page.on('pageerror',e=>errs.push(e.message));
    await page.goto('http://localhost:8765/index.html'); await page.waitForTimeout(500);
    if (!(await page.isVisible('#adv'))) await page.click('#mAdv');
    await page.waitForTimeout(500);
    await page.selectOption('#metalSel','Hg'); await page.waitForTimeout(300);
    await page.click('#tab-rel'); await page.selectOption('#f-medium','air'); await page.waitForTimeout(500);
    await page.click('#tab-air'); await page.waitForTimeout(300);
    await page.evaluate(() => document.getElementById('advPanels').scrollIntoView());
    await page.screenshot({path:`shots/${name}.png`});
    const ov = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    await page.evaluate(() => document.getElementById('budget').scrollIntoView());
    await page.screenshot({path:`shots/${name}-budget.png`});
    console.log(name, 'overflow', ov, errs);
    await ctx.close();
  }
  await browser.close();
})();
