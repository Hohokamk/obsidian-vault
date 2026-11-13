const { chromium } = require('D:/01_RoboMaster/arm-kinematic-sim/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Users/Hohokam/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1200 } });
  const reqs = [];
  page.on('request', r => { const u = r.url(); if (/api|search|wiki|posts|graphql/i.test(u)) reqs.push(r.method() + ' ' + u); });
  await page.goto('https://bbs.robomaster.com/wiki/20204847/1969149', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(6000);
  const links = await page.$$eval('a', as => as.map(a => (a.innerText||'').trim().replace(/\s+/g,' ') + ' || ' + a.href).filter(x => x.length > 6));
  fs.writeFileSync('links.txt', links.join('\n'), 'utf8');
  await page.goto('https://bbs.robomaster.com/search?keyword=' + encodeURIComponent('重装'), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(12000);
  const txt = await page.evaluate(() => document.body.innerText);
  fs.writeFileSync('search.txt', txt, 'utf8');
  fs.writeFileSync('reqs.txt', reqs.join('\n'), 'utf8');
  await browser.close();
})();
