const { chromium } = require('C:/Users/tianhuo/Documents/codex第一个项目/.codex_tmp/expense_reconcile_20260910/node_modules/playwright');
const fs = require('fs');
const crypto = require('crypto');

const source = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/team_package_20260928/sources/WO2021116933A1.html';
const output = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/contest_report_20260928/search_screenshots/archived_also_published_as_readable_20260928.png';
const log = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/contest_report_20260928/search_screenshots/capture_readable_family_run_20260928.json';

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const context = await browser.newContext({ viewport: { width: 1280, height: 1100 }, deviceScaleFactor: 1 });
  await context.route(/^https?:/, route => route.abort());
  const page = await context.newPage();
  try {
    await page.goto('file:///' + source.replace(/\\/g, '/'), { waitUntil: 'domcontentloaded', timeout: 30000 });
    const title = await page.title();
    const section = page.locator('h2', { hasText: 'Also Published As' });
    if (await section.count() !== 1 || !title.includes('WO2021116933A1')) throw new Error('Expected archived Google Patents page/section unavailable');
    await page.evaluate(() => { document.documentElement.style.zoom = '1.8'; });
    await section.scrollIntoViewIfNeeded();
    await page.evaluate(() => window.scrollBy(0, -80));
    const visible = await page.locator('body').innerText();
    if (!visible.includes('CN115087774A')) throw new Error('CN115087774A is not present in replayed page');
    await page.screenshot({ path: output, fullPage: false });
    const bytes = fs.readFileSync(output);
    fs.writeFileSync(log, JSON.stringify({
      capturedAt: new Date().toISOString(),
      sourceHtml: source,
      finalUrl: page.url(),
      title,
      network: 'http/https requests aborted; local archived HTML replay only',
      runtimeView: 'document.documentElement.style.zoom=1.8; scrolled to Also Published As; no source HTML write and no image editing/cropping',
      visibleTextChecks: ['Also Published As', 'CN115087774A', '2022-09-20'].filter(value => visible.includes(value)),
      output,
      sha256: crypto.createHash('sha256').update(bytes).digest('hex').toUpperCase(),
      byteLength: bytes.length
    }, null, 2) + '\n');
  } catch (err) {
    fs.writeFileSync(log, JSON.stringify({ capturedAt: new Date().toISOString(), sourceHtml: source, finalUrl: page.url(), message: String(err) }, null, 2) + '\n');
    process.exitCode = 1;
  } finally {
    await context.close();
    await browser.close();
  }
})();
