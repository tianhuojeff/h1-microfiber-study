const { chromium } = require('C:/Users/tianhuo/Documents/codex第一个项目/.codex_tmp/expense_reconcile_20260910/node_modules/playwright');
const fs = require('fs');
const crypto = require('crypto');

const output = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/contest_report_20260928/search_screenshots/google_patents_archived_public_record_WO2021116933A1_20260928.png';
const familyOutput = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/contest_report_20260928/search_screenshots/google_patents_archived_also_published_as_WO2021116933A1_20260928.png';
const log = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/contest_report_20260928/search_screenshots/capture_archived_google_patents_run_20260928.json';
const source = 'C:/Users/tianhuo/Documents/codex第一个项目/h1-study/team_package_20260928/sources/WO2021116933A1.html';
const url = 'file:///' + source.replace(/:/g, ':').replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
  await context.route(/^https?:/, route => route.abort());
  const page = await context.newPage();
  let navigation = null;
  let error = null;
  try {
    navigation = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1500);
    const title = await page.title();
    const finalUrl = page.url();
    const pageText = await page.locator('body').innerText({ timeout: 5000 }).catch(() => '');
    const isArchivedPublicPage = finalUrl.startsWith('file:///') && title.includes('WO2021116933A1') && pageText.includes('Google Patents');
    if (!isArchivedPublicPage) throw new Error(`Unexpected page: title=${title}; url=${finalUrl}`);
    await page.screenshot({ path: output, fullPage: false });
    const section = page.locator('h2', { hasText: 'Also Published As' });
    if (await section.count() !== 1) throw new Error('Archived HTML has no unique Also Published As section');
    await section.scrollIntoViewIfNeeded();
    await page.screenshot({ path: familyOutput, fullPage: false });
    const bytes = fs.readFileSync(output);
    const familyBytes = fs.readFileSync(familyOutput);
    fs.writeFileSync(log, JSON.stringify({
      capturedAt: new Date().toISOString(),
      requestedUrl: url,
      finalUrl,
      httpStatus: navigation ? navigation.status() : null,
      title,
      sourceHtml: source,
      visibleTextChecks: ['WO2021116933A1', 'Microplastic compactor', 'Google Patents'].filter(value => pageText.includes(value)),
      screenshots: [
        { file: output, sha256: crypto.createHash('sha256').update(bytes).digest('hex').toUpperCase(), byteLength: bytes.length, scope: 'archived-page header and bibliographic area' },
        { file: familyOutput, sha256: crypto.createHash('sha256').update(familyBytes).digest('hex').toUpperCase(), byteLength: familyBytes.length, scope: 'archived-page Also Published As section including CN115087774A' }
      ]
    }, null, 2) + '\n');
  } catch (err) {
    error = { capturedAt: new Date().toISOString(), requestedUrl: url, finalUrl: page.url(), message: String(err) };
    fs.writeFileSync(log, JSON.stringify(error, null, 2) + '\n');
    process.exitCode = 1;
  } finally {
    await context.close();
    await browser.close();
  }
})();
