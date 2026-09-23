const { chromium } = require('playwright');
const path = require('path');
const fx = require('./fixture.js');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 950 } });
  p.on('pageerror', e => console.log('PAGE ERROR:', e.message));
  await p.route('**/zyntern.com/api/jobs**', r => r.fulfill({ status:200, contentType:'application/json',
    body: JSON.stringify({ data: fx, meta:{ current_page:1, last_page:1 } }) }));
  await p.route('**/uploads/avatar/**', r => r.abort());
  await p.goto('file://' + path.resolve(__dirname, '..', 'internship_finder.html'));
  await p.waitForTimeout(1500);

  console.log('title    :', await p.title());
  console.log('count    :', (await p.textContent('#count')).trim());
  console.log('status Z :', (await p.textContent('#statZ')).trim());
  console.log('status P :', (await p.textContent('#statP')).trim());
  console.log('pills    :', (await p.locator('.pillrow .pill').allTextContents()).map(s=>s.replace(/\s+/g,' ').trim()).join(' | '));

  // bilingual search
  for (const term of ['controlling', 'kontrolling', 'finance', 'könyvelő', 'marketing']) {
    await p.fill('#q', term); await p.waitForTimeout(350);
    console.log(`search "${term}":`, (await p.textContent('#count')).trim());
  }
  await p.fill('#q', ''); await p.waitForTimeout(350);

  // field facet reads in English
  await p.locator('.pillrow .pill', { hasText: 'Field' }).click();
  const opts = (await p.locator('.panel .opt .label').allTextContents()).slice(0, 8);
  console.log('field facet:', opts.join(' | '));
  await p.keyboard.press('Escape');

  // detail pane
  await p.click('.card'); await p.waitForTimeout(300);
  console.log('facts    :', (await p.locator('.facts dt').allTextContents()).join(' | '));
  console.log('values   :', (await p.locator('.facts dd').allTextContents()).slice(0,4).join(' | '));
  console.log('sections :', (await p.locator('.sec h4').allTextContents()).join(' | '));
  console.log('apply    :', (await p.textContent('.apply')).trim());
  await p.screenshot({ path: path.resolve(__dirname, 'screenshot.png') });

  const m = await b.newPage({ viewport: { width: 400, height: 820 } });
  await m.route('**/zyntern.com/api/jobs**', r => r.fulfill({ status:200, contentType:'application/json',
    body: JSON.stringify({ data: fx, meta:{ current_page:1, last_page:1 } }) }));
  await m.route('**/uploads/avatar/**', r => r.abort());
  await m.goto('file://' + path.resolve(__dirname, '..', 'internship_finder.html'));
  await m.waitForTimeout(1200);
  console.log('mobile scrollWidth:', await m.evaluate(() => document.documentElement.scrollWidth));
  await b.close();
})();
