// Reusable browser regression suite. Uses only the documented CUA browser APIs supplied by the caller.
// In cua_repl: const suite = await import('file:///.../_build/tools/check_search_browser.mjs');
// await suite.checkSearchBrowser(tab, viewportCapability, 'http://127.0.0.1:8012');
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
export async function checkSearchBrowser(tab, viewport, origin) {
  const passed = [];
  const input = () => tab.playwright.getByRole('searchbox', { name: 'Search this site' });
  async function loaded(query, de = false) {
    await tab.playwright.getByRole('heading', { name: de ? `Suche: „${query}“` : `Search: “${query}”`, exact: true }).waitFor({ state: 'visible' });
    await tab.playwright.locator('.global-search-status').filter({ hasText: /\d+ (?:result|Treffer)|No matches|Keine Treffer/ }).waitFor({ state: 'visible' });
  }
  async function query(value) { await input().fill(value); await input().press('Enter'); await loaded(value); }
  try {
    await viewport.reset();
    await tab.goto(`${origin}/research-ai4se.html?q=harness`); await loaded('harness');
    assert.equal(await tab.playwright.locator('.global-result-children a[href="research-ai4se.html#ai-f12"]').count(), 1);
    const related = tab.playwright.locator('.global-result-related').first();
    await related.locator('summary', {}).click();
    assert.ok(await related.locator('a[href="research-ai4se.html#ai-summary"]', {}).isVisible());
    passed.push('Page/section/figure grouping and expandable direct links');
    await query('harnses');
    assert.ok((await tab.playwright.locator('.global-result-reason').first().innerText({})).includes('harness'));
    passed.push('Typo fallback and explanation');
    await query('wrapping effect');
    const paper = tab.playwright.locator('.global-search-list > li').filter({ has: tab.playwright.locator('a[href="research.html#pub-Net15"]') });
    assert.ok((await paper.locator('.global-result-source', {}).innerText({})).includes('Abstract'));
    assert.ok((await paper.locator('p', {}).innerText({})).toLowerCase().includes('wrapping'));
    await tab.playwright.locator('.global-search-list a[href="research.html#pub-Net15"]').click();
    await tab.playwright.locator('#pub-Net15 .pub-abstract').waitFor({ state: 'visible' });
    assert.equal(await tab.playwright.locator('#pub-Net15 .pub-abstract').getAttribute('open', {}), '');
    await tab.playwright.getByRole('searchbox', { name: 'Search publications', exact: true }).fill('wrapping effect');
    assert.ok(await tab.playwright.locator('#pub-Net15').isVisible());
    assert.equal(await tab.playwright.locator('.pubs > li:not([hidden])').count(), 1);
    await tab.back(); await loaded('wrapping effect');
    passed.push('Own abstract hit, source label, paper destination and browser Back');
    await query('qzxv-nonexistent-937451');
    assert.ok((await tab.playwright.locator('.global-search-status').innerText({})).startsWith('No matches'));
    await tab.playwright.getByRole('button', { name: 'Back to page ×' }).click();
    assert.equal(await tab.playwright.locator('#global-results').isVisible(), false);
    passed.push('Empty state and page restoration');
    await viewport.set({ width: 390, height: 844 });
    await tab.playwright.getByRole('button', { name: 'Open search', exact: true }).click();
    assert.equal(await tab.playwright.evaluate(() => document.activeElement.id), 'global-query');
    await query('ai-f12');
    assert.equal(await tab.playwright.evaluate(() => document.getElementById('index').classList.contains('open')), false);
    assert.equal(await tab.playwright.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert.equal(await tab.playwright.locator('.global-search-list > li').count(), 1);
    passed.push('Phone shortcut, focus, submit, exact reference and overflow');
    await viewport.set({ width: 768, height: 1024 });
    await tab.playwright.getByRole('button', { name: 'Open search', exact: true }).click();
    assert.equal(await tab.playwright.evaluate(() => document.activeElement.id), 'global-query');
    await input().press('Escape');
    await tab.playwright.getByRole('button', { name: 'close', exact: true }).click();
    passed.push('Tablet shortcut and keyboard escape');
    await tab.goto(`${origin}/de/research.html?q=barrierefreiheit`); await loaded('barrierefreiheit', true);
    assert.ok(await tab.playwright.locator('.global-search-list a[href="research.html#pub-BKM+25"]').isVisible());
    passed.push('German concept synonym finds own English abstract');

    // Recovery fixture: the same site UI, with an initially missing local index.
    await viewport.reset();
    const suffix = Date.now(), htmlName = `search-error-${suffix}.html`, jsonName = `search-retry-${suffix}.json`;
    const directory = new URL('_build/search-work/', root);
    await fs.mkdir(directory, { recursive: true });
    const fixture = new URL(htmlName, directory), index = new URL(jsonName, directory);
    try {
      let html = await fs.readFile(new URL('index.html', root), 'utf8');
      html = html.replace('<head>', `<head><base href="${origin}/">`)
        .replace('data-index="assets/search-en.json"', `data-index="_build/search-work/${jsonName}"`);
      await fs.writeFile(fixture, html);
      await tab.goto(`${origin}/_build/search-work/${htmlName}?q=harness`);
      await tab.playwright.getByRole('button', { name: 'Try again', exact: true }).waitFor({ state: 'visible' });
      await fs.copyFile(new URL('assets/search-en.json', root), index);
      await tab.playwright.getByRole('button', { name: 'Try again', exact: true }).click(); await loaded('harness');
      passed.push('Index failure and successful retry');
    } finally { await fs.rm(fixture, { force: true }); await fs.rm(index, { force: true }); }
    await tab.goto(`${origin}/research-ai4se.html?q=harness`); await loaded('harness');
    return passed;
  } finally { await viewport.reset(); }
}
