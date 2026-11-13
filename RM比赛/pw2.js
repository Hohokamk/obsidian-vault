const { chromium } = require('D:/01_RoboMaster/arm-kinematic-sim/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Users/Hohokam/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1400 } });
  await page.goto('https://bbs.robomaster.com/wiki/77882607', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  for (const label of ['3 项目分析','3.2.3 重装机器人']) {
    try {
      const loc = page.getByText(label, { exact: false }).first();
      await loc.click({ timeout: 8000 });
      await page.waitForTimeout(2500);
    } catch(e) { fs.appendFileSync('plan_click.txt', 'ERR '+label+' '+e.message+'\n', 'utf8'); }
  }
  const txt = await page.evaluate(() => document.body.innerText);
  const links = await page.$$eval('a', as => as.map(a => (a.innerText||'').trim().replace(/\s+/g,' ')+' || '+a.href));
  fs.writeFileSync('plan_tree.txt', txt + '\n\n=== LINKS ===\n' + links.join('\n'), 'utf8');
  await page.screenshot({ path: 'plan_tree.png', fullPage: false });
  await browser.close();
})();
