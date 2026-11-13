const { chromium } = require('D:/01_RoboMaster/arm-kinematic-sim/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Users/Hohokam/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1200 } });
  const logs = [];
  page.on('request', r => { const u=r.url(); if (u.includes('developers-server')) logs.push({m:r.method(), u, p:r.postData()}); });
  await page.goto('https://bbs.robomaster.com/wiki/77882607', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  const txt = await page.evaluate(() => document.body.innerText);
  fs.writeFileSync('plan_wiki.txt', txt, 'utf8');
  fs.writeFileSync('plan_reqs.txt', JSON.stringify(logs,null,1), 'utf8');
  await browser.close();
})();
