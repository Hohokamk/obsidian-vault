const { chromium } = require('D:/01_RoboMaster/arm-kinematic-sim/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Users/Hohokam/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const out = [];
  async function dump(url, name, wait=6000) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(wait);
      const text = await page.evaluate(() => document.body.innerText);
      out.push('===== ' + name + ' | ' + url + ' =====\n' + text);
      console.log(name, text.length);
    } catch (e) { console.log('ERR', name, e.message); }
  }
  await dump('https://bbs.robomaster.com/wiki/20204847/1969149', 'wiki-rmuc-rules', 8000);
  await dump('https://bbs.robomaster.com/search?keyword=' + encodeURIComponent('重装'), 'bbs-search', 8000);
  fs.writeFileSync('web1.txt', out.join('\n\n'), 'utf8');
  await browser.close();
})();
