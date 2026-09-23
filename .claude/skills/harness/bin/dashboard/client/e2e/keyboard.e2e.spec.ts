import { expect, test, type Locator, type Page, type TestInfo } from '@playwright/test';
import { access, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { checkFor, loadManifest, type UiCheck } from '../ui-manifest.js';

const manifest = loadManifest();
const check = checkFor(manifest, 'keyboard focus transitions and restoration match DESIGN');
const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..', '..');
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';
const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';

async function load(page: Page, route: string): Promise<void> {
  await page.addInitScript(() => {
    const fixed = Date.parse('2026-09-17T12:00:00Z');
    class FrozenDate extends Date { constructor(...args: ConstructorParameters<typeof Date>) { super(args.length ? args[0] : fixed); } static now() { return fixed; } }
    Object.defineProperty(window, 'Date', { value: FrozenDate });
  });
  const response = await page.goto(route);
  expect.soft(response, `served bundle must load ${route}`).not.toBeNull();
  await expect.soft(page.locator('body')).toBeVisible();
  await page.waitForLoadState('networkidle');
}

async function capture(page: Page, testInfo: TestInfo, contract: UiCheck): Promise<void> {
  await page.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}' });
  const session = await page.context().newCDPSession(page);
  const shot = await session.send('Page.captureScreenshot', { format: 'webp', captureBeyondViewport: true });
  expect.soft(shot.data, 'screenshot capture produces WebP evidence').toBeTruthy();
  if (!shot.data) return;
  const path = resolve(root, `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${testInfo.project.name}/${contract.check_id}--execution.webp`);
  await mkdir(resolve(path, '..'), { recursive: true });
  try { await access(path); throw new Error(`duplicate screenshot evidence: ${path}`); }
  catch (error) { if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error; }
  const bytes = Buffer.from(shot.data, 'base64');
  expect.soft(bytes.length, 'screenshot evidence is nonempty').toBeGreaterThan(12);
  expect.soft(bytes.subarray(0, 4).toString(), 'screenshot evidence has RIFF header').toBe('RIFF');
  expect.soft(bytes.subarray(8, 12).toString(), 'screenshot evidence has WEBP header').toBe('WEBP');
  await writeFile(path, bytes);
  await testInfo.attach(`evidence:${contract.check_id}:execution`, { path, contentType: 'image/webp' });
}

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.title !== check.spec_title || !check.applicable_projects.includes(testInfo.project.name)) return;
  await capture(page, testInfo, check);
});


async function expectFocused(locator: Locator, ring: 'keyboard' | 'pointer' | 'none', message: string): Promise<void> {
  await expect.soft(locator, `${message}: activeElement`).toBeFocused();
  const width = ring === 'keyboard' ? '2px' : '0px';
  await expect.soft(locator, `${message}: computed outline width`).toHaveCSS('outline-width', width);
  if (ring === 'keyboard') {
    await expect.soft(locator, `${message}: computed outline offset`).toHaveCSS('outline-offset', '2px');
    const colour = await locator.evaluate((element) => getComputedStyle(document.documentElement).getPropertyValue('--color-text-primary').trim());
    await expect.soft(locator, `${message}: computed outline colour`).toHaveCSS('outline-color', colour);
  }
}

async function tabThrough(page: Page, controls: Locator[], clause: string): Promise<void> {
  await page.locator('body').press('Control+Home');
  for (const [index, control] of controls.entries()) {
    await page.keyboard.press('Tab');
    await expectFocused(control, 'keyboard', `${clause} stop ${index + 1}`);
  }
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(0);
}

async function runClause(name: string, action: () => Promise<void>, failures: string[]): Promise<void> {
  await test.step(`C3-KEYBOARD: ${name}`, async () => {
    try { await action(); }
    catch (error) { failures.push(`${name}: ${error instanceof Error ? error.message : String(error)}`); }
  });
}

test('keyboard focus transitions and restoration match DESIGN', async ({ page }, testInfo) => {
  test.setTimeout(120_000);
  test.skip(!check.applicable_projects.includes(testInfo.project.name), 'C3-KEYBOARD is not applicable to this project');
  const failures: string[] = [];

  await runClause('overview exact Tab order and noncontrol exclusions', async () => {
    await load(page, overview);
    const tiles = page.locator('[aria-label="Repository KPIs"] a');
    const info = page.getByRole('button', { name: /About/ });
    const statuses = ['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale'].map((name) => page.getByRole('button', { name: new RegExp(name) }));
    await expect.soft(tiles, 'overview has seven KPI tile links').toHaveCount(7);
    await expect.soft(info, 'overview has seven KPI InfoDisclosure triggers').toHaveCount(7);
    await tabThrough(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), ...Array.from({ length: 7 }, (_, index) => tiles.nth(index)).flatMap((tile, index) => [tile, info.nth(index)]), ...statuses, page.getByRole('combobox', { name: 'Station' }), page.getByRole('combobox', { name: 'Status' }), page.getByRole('combobox', { name: 'Kind' }), page.getByRole('button', { name: /Kanban|Table/ })], 'overview Tab order');
    const noncontrols = page.locator('svg, [data-chart], [data-unavailable], [data-status-badge]');
    for (let index = 0; index < await noncontrols.count(); index += 1) {
      const noncontrol = noncontrols.nth(index);
      await expect.soft(noncontrol, 'charts and named noncontrols are aria-hidden').toHaveAttribute('aria-hidden', 'true');
      await expect.soft(noncontrol, 'charts and named noncontrols are not focusable').toHaveJSProperty('tabIndex', -1);
    }
  }, failures);
  await runClause('overview conditional Clear Filters layout headers and row controls remain in Tab order', async () => {
    await load(page, `${overview}&status=needs-you`);
    const clear = page.getByRole('button', { name: 'Clear Filters' });
    const layout = page.getByRole('button', { name: /Kanban|Table/ });
    const sortable = page.locator('th button, [aria-sort] button');
    const rows = page.locator('table a[href*="/work/"], [data-lane] a[href*="/work/"]');
    await expect.soft(clear, 'Clear Filters is conditionally available').toBeVisible();
    await expect.soft(sortable, 'Table layout exposes sortable headers').not.toHaveCount(0);
    await expect.soft(rows, 'Table layout exposes displayed row controls').not.toHaveCount(0);
    await tabThrough(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), ...Array.from({ length: 7 }, (_, index) => [page.locator('[aria-label="Repository KPIs"] a').nth(index), page.getByRole('button', { name: /About/ }).nth(index)]).flat(), ...['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale'].map((name) => page.getByRole('button', { name: new RegExp(name) })), page.getByRole('combobox', { name: 'Station' }), page.getByRole('combobox', { name: 'Status' }), page.getByRole('combobox', { name: 'Kind' }), clear, layout, ...Array.from({ length: await sortable.count() }, (_, index) => sortable.nth(index)), ...Array.from({ length: await rows.count() }, (_, index) => rows.nth(index))], 'overview complete Tab order');
  }, failures);

  await runClause('KPI exact Tab order and displayed row controls', async () => {
    await load(page, '/kpi/4?window=all&repo=all');
    const info = page.getByRole('button', { name: /About/ });
    const rows = page.getByRole('link', { name: /FEAT|BUG/ });
    await tabThrough(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), info, ...Array.from({ length: await rows.count() }, (_, index) => rows.nth(index))], 'KPI Tab order');
  }, failures);

  await runClause('work detail exact Tab order and h1 exclusion', async () => {
    await load(page, '/work/FEAT-53?window=all&repo=all');
    const title = page.locator('[data-route-title]');
    await expect.soft(title, 'fresh work detail h1 is not activeElement').not.toBeFocused();
    await expect.soft(title, 'work detail h1 remains programmatic-only').toHaveAttribute('tabindex', '-1');
    const links = page.getByRole('link', { name: /FEAT|BUG/ });
    await tabThrough(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), ...Array.from({ length: await links.count() }, (_, index) => links.nth(index))], 'work detail Tab order');
  }, failures);

  await runClause('keyboard and pointer focus indicators differ', async () => {
    await load(page, overview);
    const filter = page.getByRole('combobox', { name: 'Station' });
    await filter.focus();
    await expectFocused(filter, 'keyboard', 'keyboard-focused filter');
    await filter.click();
    await expectFocused(filter, 'pointer', 'pointer-focused filter');
  }, failures);

  await runClause('fresh loads leave h1 unfocused', async () => {
    await load(page, '/kpi/1?window=all&repo=all');
    await expect.soft(page.locator('[data-route-title]'), 'fresh KPI load h1 activeElement').not.toBeFocused();
  }, failures);

  await runClause('in-app KPI and work transitions land on unrung h1', async () => {
    await load(page, overview);
    await page.locator('[aria-label="Repository KPIs"] a').first().click();
    await settle(page);
    await expectFocused(page.locator('[data-route-title]'), 'none', 'KPI route h1 after tile activation');
    await load(page, overview);
    await page.getByRole('link', { name: /FEAT|BUG/ }).first().click();
    await settle(page);
    await expectFocused(page.locator('[data-route-title]'), 'none', 'work route h1 after dashboard row activation');
    await load(page, '/kpi/4?window=all&repo=all');
    await page.getByRole('link', { name: /FEAT|BUG/ }).first().click();
    await settle(page);
    await expectFocused(page.locator('[data-route-title]'), 'none', 'work route h1 after KPI row activation');
  }, failures);

  for (const opening of ['pointer', 'keyboard'] as const) for (const close of ['selection', 'Escape'] as const) {
    await runClause(`${opening}-opened Selector ${close} restores trigger with correct ring`, async () => {
      await load(page, overview);
      const selector = page.getByRole('combobox', { name: 'Station' });
      if (opening === 'pointer') await selector.click();
      else { await selector.focus(); await page.keyboard.press('Space'); }
      if (close === 'selection') { await page.keyboard.press('ArrowDown'); await page.keyboard.press('Enter'); }
      else await page.keyboard.press('Escape');
      await settle(page);
      await expectFocused(selector, opening === 'keyboard' ? 'keyboard' : 'pointer', `${opening} Selector ${close} restoration`);
    }, failures);
  }

  await runClause('attention activation lands on selected Status filter', async () => {
    await load(page, overview);
    await page.getByRole('button', { name: /Needs You/ }).click();
    await settle(page);
    const status = page.getByRole('combobox', { name: 'Status' });
    await expectFocused(status, 'pointer', 'Status after attention activation');
    await expect.soft(status, 'Status selected value is exposed').toContainText('Needs You');
    await expect.soft(page.locator('[aria-live="polite"]'), 'Status selection is announced').toContainText('Needs You');
  }, failures);

  await runClause('filter and layout updates retain initiator after results settle', async () => {
    await load(page, overview);
    const status = page.getByRole('combobox', { name: 'Status' });
    await status.focus();
    await page.keyboard.press('Space');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    await settle(page);
    await expectFocused(status, 'keyboard', 'Status after filter update');
    const layout = page.getByRole('button', { name: 'Kanban' });
    await layout.click();
    await settle(page);
    await expectFocused(layout, 'pointer', 'Kanban after layout update');
    await expect.soft(page.locator('[aria-live="polite"]'), 'layout result count is announced').toContainText(/\d+ of \d+ items/);
  }, failures);

  await runClause('grilling and worktree disclosure toggles restore their row buttons', async () => {
    await load(page, overview);
    for (const name of ['Grilling', 'Worktree']) {
      const toggle = page.getByRole('button', { name });
      await toggle.click();
      await settle(page);
      await expectFocused(toggle, 'pointer', `${name} after expand`);
      await toggle.click();
      await settle(page);
      await expectFocused(toggle, 'pointer', `${name} after collapse`);
    }
  }, failures);

  for (const source of ['attention card', 'KPI tile', 'dashboard row'] as const) {
    await runClause(`browser Back restores exact ${source} initiator`, async () => {
      await load(page, overview);
      const initiator = source === 'attention card' ? page.getByRole('button', { name: /Needs You/ }) : source === 'KPI tile' ? page.locator('[aria-label="Repository KPIs"] a').first() : page.getByRole('link', { name: /FEAT|BUG/ }).first();
      await initiator.click();
      await settle(page);
      await page.goBack();
      await settle(page);
      await expectFocused(initiator, 'pointer', `${source} after browser Back`);
    }, failures);
  }

  await runClause('InfoDisclosure keyboard open Escape restores ring', async () => {
    await load(page, '/kpi/4?window=all&repo=all');
    const disclosure = page.getByRole('button', { name: /About/ });
    await disclosure.focus();
    await page.keyboard.press('Enter');
    await settle(page);
    await expectFocused(page.getByRole('dialog').getByRole('button').first(), 'keyboard', 'InfoDisclosure first control');
    await page.keyboard.press('Escape');
    await settle(page);
    await expectFocused(disclosure, 'keyboard', 'InfoDisclosure after Escape');
  }, failures);

  await runClause('InfoDisclosure outside click restores pointer trigger without ring', async () => {
    await load(page, '/kpi/4?window=all&repo=all');
    const disclosure = page.getByRole('button', { name: /About/ });
    await disclosure.click();
    await page.mouse.click(1, 1);
    await settle(page);
    await expectFocused(disclosure, 'pointer', 'InfoDisclosure after outside click');
  }, failures);

  expect.soft(failures, 'all C3 keyboard clauses execute before reporting product divergence').toEqual([]);
});
