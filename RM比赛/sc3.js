const { chromium } = require('D:/01_RoboMaster/arm-kinematic-sim/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Users/Hohokam/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1200 } });
  const logs = [];
  page.on('request', r => { if (r.url().includes('page-posts-es-search')) logs.push({url:r.url(), post:r.postData()}); });
  await page.goto('https://bbs.robomaster.com/search?keyword=' + encodeURIComponent('重装'), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  fs.writeFileSync('searchpost.txt', JSON.stringify(logs, null, 1), 'utf8');
  // bilibili
  const p2 = await browser.newPage();
  for (const kw of ['RMUC 2027 重装','2027 机甲大师 重装机器人','重装机器人 装配']) {
    try {
      const u = 'https://search.bilibili.com/all?keyword=' + encodeURIComponent(kw);
      await p2.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p2.waitForTimeout(5000);
      const t = await p2.evaluate(() => document.body.innerText);
      fs.appendFileSync('bili.txt', '\n==== '+kw+' ====\n'+t.slice(0,4000), 'utf8');
    } catch(e) { fs.appendFileSync('bili.txt','ERR '+kw+' '+e.message+'\n','utf8'); }
  }
  await browser.close();
})();
