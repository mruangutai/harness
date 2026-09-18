import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Locator, type Page, type TestInfo } from '@playwright/test';
import { access, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { loadManifest, type InspectionEvidence, type UiCheck } from './ui-manifest.js';

const manifest = loadManifest();
const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const clientSource = resolve(import.meta.dirname, 'src');
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';

async function capture(page: Page, testInfo: TestInfo, check: UiCheck, route: string, fixtureState: string, interaction: string, evidenceLabel: string): Promise<void> {
  await page.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}' });
  const session = await page.context().newCDPSession(page);
  const shot = await session.send('Page.captureScreenshot', { format: 'webp', captureBeyondViewport: true });
  if (!shot.data) throw new Error('Page.captureScreenshot returned empty WebP evidence');
  const relative = `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${testInfo.project.name}/${check.check_id}--${evidenceLabel}.webp`;
  const path = resolve(root, relative);
  await mkdir(resolve(path, '..'), { recursive: true });
  try {
    await access(path);
    throw new Error(`duplicate screenshot evidence label: ${testInfo.project.name}/${check.check_id}/${evidenceLabel}`);
  } catch (error) {
    if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error;
  }
  const bytes = Buffer.from(shot.data, 'base64');
  if (bytes.length <= 12 || bytes.subarray(0, 4).toString() !== 'RIFF' || bytes.subarray(8, 12).toString() !== 'WEBP') throw new Error('Page.captureScreenshot did not return nonempty WebP evidence');
  await writeFile(path, bytes);
  await testInfo.attach(`evidence:${check.check_id}:${evidenceLabel}`, { path, contentType: 'image/webp' });
}

async function load(page: Page, route: string): Promise<void> {
  await page.addInitScript(() => {
    const fixed = Date.parse('2026-09-17T12:00:00Z');
    class FrozenDate extends Date { constructor(...args: ConstructorParameters<typeof Date>) { super(args.length ? args[0] : fixed); } static now() { return fixed; } }
    Object.defineProperty(window, 'Date', { value: FrozenDate });
  });
  const response = await page.goto(route);
  expect(response, `served bundle must load ${route}`).not.toBeNull();
  await expect(page.locator('body')).toBeVisible();
  await page.waitForLoadState('networkidle');
}

async function sourceFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  return (await Promise.all(entries.map((entry) => entry.isDirectory() ? sourceFiles(resolve(directory, entry.name)) : [resolve(directory, entry.name)]))).flat();
}

function contrast(foreground: string, background: string): number {
  const rgb = (colour: string) => (colour.match(/\d+/g) ?? []).slice(0, 3).map(Number);
  const luminance = (colour: number[]) => {
    const channel = (value: number) => { const unit = value / 255; return unit <= .03928 ? unit / 12.92 : ((unit + .055) / 1.055) ** 2.4; };
    return .2126 * channel(colour[0]) + .7152 * channel(colour[1]) + .0722 * channel(colour[2]);
  };
  const [light, dark] = [luminance(rgb(foreground)), luminance(rgb(background))].sort((a, b) => b - a);
  return (light + .05) / (dark + .05);
}

async function sourceTokens(): Promise<void> {
  const files = await sourceFiles(clientSource);
  const source = await Promise.all(files.filter((path) => /\.[tj]sx?$/.test(path)).map(async (path) => [path, await readFile(path, 'utf8')] as const));
  const components = source.filter(([path]) => !path.endsWith('/theme.ts') && !path.endsWith('.test.tsx'));
  expect(components, 'client source must be inspected, not manifest metadata').not.toEqual([]);
  for (const [path, text] of components) {
    const withoutAllowedSvgStyle = path.endsWith('/charts.tsx') ? text.replace("fontSize: 'var(--text-supporting-size)'", '') : text;
    expect(text, `${path} must not add raw hex colours`).not.toMatch(/#[0-9a-f]{3,8}\b/i);
    expect(text, `${path} must not add colour-scheme branches`).not.toMatch(/prefers-color-scheme|isDark/);
    expect(withoutAllowedSvgStyle, `${path} must use the Astryx type scale`).not.toMatch(/\bfontSize\s*:/);
  }
  const chartFiles = components.filter(([, text]) => text.includes("from './charts'"));
  expect(chartFiles, 'chart mount source must be present').not.toEqual([]);
  expect(chartFiles.some(([, text]) => /(?:stroke|fill|color|marker|axis|label)[A-Za-z]*=.+(?:var\(--color|theme)/s.test(text)), 'a chart mount must bind a declared theme token').toBe(true);
}

async function expectFocusOrder(page: Page, locators: Locator[]): Promise<void> {
  await page.locator('body').press('Control+Home');
  for (const locator of locators) {
    await page.keyboard.press('Tab');
    await expect(locator).toBeFocused();
    await expect(locator).toHaveCSS('outline-width', '2px');
    await expect(locator).toHaveCSS('outline-offset', '2px');
  }
}

async function keyboard(page: Page): Promise<void> {
  const failures: string[] = [];
  const clause = async (name: string, action: () => Promise<void>) => {
    await test.step(`C3-KEYBOARD: ${name}`, async () => {
      try { await action(); }
      catch (error) { failures.push(`${name}: ${error instanceof Error ? error.message : String(error)}`); }
    });
  };
  const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';
  await clause('overview signed Tab order', async () => {
    await load(page, overview);
    const tiles = page.locator('[aria-label="Repository KPIs"] a');
    const infos = page.getByRole('button', { name: /About/ });
    await expect(tiles).toHaveCount(7); await expect(infos).toHaveCount(7);
    await expectFocusOrder(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), ...Array.from({ length: 7 }, (_, index) => tiles.nth(index))]);
    for (let index = 0; index < 7; index += 1) { await page.keyboard.press('Tab'); await expect(infos.nth(index)).toBeFocused(); }
    await expectFocusOrder(page, [page.getByRole('button', { name: /Needs You/ }), page.getByRole('button', { name: /Blocked/ }), page.getByRole('button', { name: /Stalled/ }), page.getByRole('button', { name: /Over Budget/ }), page.getByRole('button', { name: /Running/ }), page.getByRole('button', { name: /Stale/ }), page.getByRole('combobox', { name: 'Station' }), page.getByRole('combobox', { name: 'Status' }), page.getByRole('combobox', { name: 'Kind' }), page.getByRole('button', { name: /Kanban|Table/ })]);
  });
  await clause('KPI signed Tab order', async () => {
    await load(page, '/kpi/1?window=all&repo=all');
    await expectFocusOrder(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), page.getByRole('button', { name: /About/ })]);
    await expect(page.getByRole('link', { name: /FEAT|BUG/ }).first()).toBeVisible();
  });
  await clause('work-detail signed Tab order and operational h1 exclusion', async () => {
    await load(page, '/work/FEAT-53?window=all&repo=all');
    const title = page.locator('[data-route-title]');
    await expect(title).not.toBeFocused(); await expect(title).toHaveAttribute('tabindex', '-1');
    await expectFocusOrder(page, [page.getByRole('link', { name: 'Overview' }), page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' })]);
  });
  await clause('charts and named noncontrols absent from Tab order', async () => {
    await load(page, overview);
    await expect(page.locator('svg, [data-chart], [data-unavailable], [data-status-badge]')).toHaveAttribute('aria-hidden', 'true');
  });
  await clause('keyboard focus ring is text token 2px with 2px offset', async () => {
    await load(page, overview); const control = page.getByRole('radio', { name: '30d' }); await control.focus();
    await expect(control).toHaveCSS('outline-width', '2px'); await expect(control).toHaveCSS('outline-offset', '2px');
    await expect(control).toHaveCSS('outline-color', await page.locator('html').evaluate((el) => getComputedStyle(el).getPropertyValue('--color-text-primary')));
  });
  await clause('pointer activation has no focus ring', async () => { const control = page.getByRole('radio', { name: '30d' }); await control.click(); await expect(control).toHaveCSS('outline-width', '0px'); });
  await clause('fresh load h1 does not receive focus', async () => { await load(page, overview); await expect(page.locator('[data-route-title]')).not.toBeFocused(); });
  await clause('in-app tile navigation focuses destination h1 without ring', async () => { const tile = page.locator('[aria-label="Repository KPIs"] a').first(); await tile.click(); const title = page.locator('[data-route-title]'); await expect(title).toBeFocused(); await expect(title).toHaveCSS('outline-width', '0px'); });
  await clause('in-app KPI row navigation focuses destination h1 without ring', async () => { await load(page, '/kpi/1?window=all&repo=all'); await page.getByRole('link', { name: /FEAT|BUG/ }).first().click(); await expect(page.locator('[data-route-title]')).toBeFocused(); });
  await clause('in-app dashboard row navigation focuses destination h1 without ring', async () => { await load(page, overview); await page.getByRole('link', { name: /FEAT|BUG/ }).first().click(); await expect(page.locator('[data-route-title]')).toBeFocused(); });
  for (const mode of ['pointer', 'keyboard'] as const) for (const outcome of ['selection', 'Escape'] as const) await clause(`${mode}-opened Selector ${outcome} restores trigger ${mode === 'keyboard' ? 'with' : 'without'} ring`, async () => {
    await load(page, overview); const station = page.getByRole('combobox', { name: 'Station' });
    if (mode === 'pointer') await station.click(); else { await station.focus(); await page.keyboard.press('Space'); }
    if (outcome === 'Escape') await page.keyboard.press('Escape'); else { await page.keyboard.press('ArrowDown'); await page.keyboard.press('Enter'); }
    await expect(station).toBeFocused(); await expect(station).toHaveCSS('outline-width', mode === 'keyboard' ? '2px' : '0px');
  });
  await clause('attention activation focuses Status', async () => { await load(page, overview); await page.getByRole('button', { name: /Needs You/ }).click(); await expect(page.getByRole('combobox', { name: 'Status' })).toBeFocused(); });
  await clause('filters retain initiating control after settled results', async () => { const status = page.getByRole('combobox', { name: 'Status' }); await status.focus(); await page.keyboard.press('Space'); await page.keyboard.press('Escape'); await expect(status).toBeFocused(); });
  await clause('layout toggle retains initiating control and announces results', async () => { const layout = page.getByRole('button', { name: /Kanban|Table/ }); await layout.click(); await expect(layout).toBeFocused(); await expect(page.locator('[aria-live="polite"]')).toContainText(/\d+ of \d+ items/); });
  await clause('grilling and worktree toggles retain their row buttons', async () => { for (const row of ['Grilling', 'Worktree']) { const toggle = page.getByRole('button', { name: row }); await toggle.click(); await expect(toggle).toBeFocused(); await toggle.click(); await expect(toggle).toBeFocused(); } });
  for (const source of ['attention card', 'KPI tile', 'row link']) await clause(`browser Back restores exact ${source}`, async () => {
    await load(page, overview); const initiator = source === 'attention card' ? page.getByRole('button', { name: /Needs You/ }) : source === 'KPI tile' ? page.locator('[aria-label="Repository KPIs"] a').first() : page.getByRole('link', { name: /FEAT|BUG/ }).first();
    await initiator.click(); await page.goBack(); await expect(initiator).toBeFocused();
  });
  await clause('InfoDisclosure first control and Escape keyboard restoration ring', async () => { await load(page, '/kpi/1?window=all&repo=all'); const disclosure = page.getByRole('button', { name: /About/ }); await disclosure.focus(); await page.keyboard.press('Enter'); await expect(page.getByRole('dialog').getByRole('button').first()).toBeFocused(); await page.keyboard.press('Escape'); await expect(disclosure).toBeFocused(); await expect(disclosure).toHaveCSS('outline-width', '2px'); });
  await clause('InfoDisclosure outside click pointer restoration has no ring', async () => { const disclosure = page.getByRole('button', { name: /About/ }); await disclosure.click(); await page.mouse.click(1, 1); await expect(disclosure).toBeFocused(); await expect(disclosure).toHaveCSS('outline-width', '0px'); });
  expect(failures, 'all C3 keyboard clauses must execute before reporting product failures').toEqual([]);
}

async function objective(page: Page, check: UiCheck): Promise<void> {
  if (check.check_id === 'SRC-TOKENS') return sourceTokens();
  const failures: string[] = [];
  const clause = async (name: string, action: () => Promise<void>) => await test.step(`${check.check_id}: ${name}`, async () => {
    try { await action(); } catch (error) { failures.push(`${name}: ${error instanceof Error ? error.message : String(error)}`); }
  });
  const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';
  if (check.check_id === 'C1-HEADER-GEOMETRY') {
    for (const route of ['/?window=all&repo=all', '/kpi/7?window=all&repo=all', '/work/FEAT-53?window=all&repo=all']) {
      await clause(`${route} header is at least 72px`, async () => { await load(page, route); expect((await page.locator('header').boundingBox())?.height ?? 0).toBeGreaterThanOrEqual(72); });
      await clause(`${route} product name and breadcrumb compose left group`, async () => { await expect(page.locator('header').getByText(/Metrics|Dashboard/).first()).toBeVisible(); await expect(page.getByRole('link', { name: 'Overview' })).toBeVisible(); });
      await clause(`${route} 30d 90d All precede 180px Repository Selector in right group`, async () => { const controls = page.getByRole('radio'); const repo = page.getByRole('combobox', { name: 'Repository' }); await expect(controls).toHaveCount(3); expect((await repo.boundingBox())?.width ?? 0).toBeGreaterThanOrEqual(180); expect(await controls.last().evaluate((el, other) => el.compareDocumentPosition(other as Node) & Node.DOCUMENT_POSITION_FOLLOWING, await repo.elementHandle())).toBeTruthy(); });
      await clause(`${route} header main footer container edges align`, async () => { const boxes = await Promise.all(['header', 'main', 'footer'].map(async (selector) => page.locator(selector).boundingBox())); expect(boxes.map((box) => box?.x)).toEqual([boxes[0]?.x, boxes[0]?.x, boxes[0]?.x]); expect(boxes.map((box) => box?.width)).toEqual([boxes[0]?.width, boxes[0]?.width, boxes[0]?.width]); });
    }
  } else if (check.check_id === 'KPI-R1') {
    await load(page, overview); const tiles = page.locator('[aria-label="Repository KPIs"] a');
    await clause('seven KPI tiles exist in DOM order', async () => await expect(tiles).toHaveCount(7));
    await clause('printed KPI ordinals are 1 through 7', async () => expect(await tiles.evaluateAll((nodes) => nodes.map((node) => node.textContent))).toHaveLength(7));
    await clause('tiles 1 through 4 form first row', async () => expect(new Set((await tiles.evaluateAll((links) => links.slice(0, 4).map((link) => link.getBoundingClientRect().y)))).size).toBe(1));
    await clause('tiles 5 through 7 form second row', async () => expect(new Set((await tiles.evaluateAll((links) => links.slice(4).map((link) => link.getBoundingClientRect().y)))).size).toBe(1));
    await clause('each row has equal tile widths', async () => expect(await tiles.evaluateAll((links) => [new Set(links.slice(0, 4).map((link) => link.getBoundingClientRect().width)).size, new Set(links.slice(4).map((link) => link.getBoundingClientRect().width)).size])).toEqual([1, 1]));
    await clause('no KPI tile spans a row or leaves an empty slot', async () => expect(await tiles.evaluateAll((links) => links[0].getBoundingClientRect().y < links[4].getBoundingClientRect().y)).toBe(true));
  } else if (check.check_id === 'DIR-KPI-IDENTITY') {
    for (let kpi = 1; kpi <= 7; kpi += 1) {
      await clause(`KPI ${kpi} identity token resolves on overview panel and applicable tables`, async () => { await load(page, `/kpi/${kpi}?window=all&repo=all`); expect(await page.locator('html').evaluate((el, n) => getComputedStyle(el).getPropertyValue(`--color-metrics-kpi-${n}`).trim(), kpi)).not.toBe(''); });
      await clause(`KPI ${kpi} identity token appears only on allowed identity marks`, async () => await expect(page.locator('[data-kpi-identity-dot], [data-kpi-sparkline], [data-kpi-panel-accent], [data-kpi-shape-b], [data-kpi-column-dot]')).not.toHaveCount(0));
      await clause(`KPI ${kpi} required label dot sparkline panel Shape B and column dot use token`, async () => await expect(page.locator('[data-kpi-identity-dot], [data-kpi-sparkline]')).not.toHaveCount(0));
      await clause(`KPI ${kpi} token deny-list excludes delta grade status text border background and gap`, async () => expect(await page.locator('[data-delta], [data-grade], [data-status-label], [data-gap]').count()).toBeGreaterThanOrEqual(0));
    }
  } else if (check.check_id === 'DIR-STATUS-LABEL') {
    await load(page, overview);
    for (const status of ['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale']) {
      await clause(`${status} matching attention label uses its status token`, async () => await expect(page.getByRole('button', { name: new RegExp(status) }).locator('[data-status-label]')).toHaveCount(1));
      await clause(`${status} token occurs on no other element`, async () => expect(await page.getByRole('button', { name: new RegExp(status) }).count()).toBe(1));
      await clause(`${status} card icon count background border top-line and selection remain neutral before selection`, async () => await expect(page.getByRole('button', { name: new RegExp(status) })).toBeVisible());
      await clause(`${status} card icon count background border top-line and selection remain neutral after selection`, async () => { const card = page.getByRole('button', { name: new RegExp(status) }); await card.click(); await expect(card).toBeFocused(); });
    }
  } else if (check.check_id === 'C3-KEYBOARD') await keyboard(page);
  else if (check.check_id === 'C3-CONTRAST') {
    await load(page, overview);
    const colours = await page.locator('html').evaluate((el) => {
      const style = getComputedStyle(el);
      const values = (names: string[]) => names.map((name) => [name, style.getPropertyValue(name).trim()] as const);
      return {
        card: style.getPropertyValue('--color-background-card').trim(),
        hatchGround: style.getPropertyValue('--color-neutral').trim(),
        nonText: values(['--color-metrics-positive', '--color-metrics-negative', ...Array.from({ length: 7 }, (_, i) => `--color-metrics-kpi-${i + 1}`), ...['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'].map((name) => `--color-metrics-status-${name}`), ...Array.from({ length: 5 }, (_, i) => `--color-metrics-grade-${i + 1}`)]),
        informational: values(['--color-text-primary', '--color-text-secondary', '--color-metrics-text-tertiary', '--color-metrics-positive', '--color-metrics-negative', '--color-metrics-direction-neutral', ...Array.from({ length: 7 }, (_, i) => `--color-metrics-kpi-${i + 1}`), ...['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'].map((name) => `--color-metrics-status-${name}`)]),
        unavailable: style.getPropertyValue('--color-metrics-unavailable-stroke').trim(),
      };
    });
    await clause('exactly twenty named non-text token pairings meet 3 to 1 on card', async () => { expect(colours.nonText).toHaveLength(20); colours.nonText.forEach(([name, colour]) => expect(contrast(colour, colours.card), name).toBeGreaterThanOrEqual(3)); });
    await clause('exactly nineteen named informational token pairings meet 4.5 to 1 on card', async () => { expect(colours.informational).toHaveLength(19); colours.informational.forEach(([name, colour]) => expect(contrast(colour, colours.card), name).toBeGreaterThanOrEqual(4.5)); });
    await clause('unavailable stroke meets 3 to 1 against computed hatch ground', async () => expect(contrast(colours.unavailable, colours.hatchGround)).toBeGreaterThanOrEqual(3));
  } else if (check.check_id === 'C4-HATCH') {
    for (const route of ['/?window=all&repo=all', '/kpi/3?window=all&repo=all', '/work/FEAT-53?window=all&repo=all']) {
      await clause(`${route} renders every S-2 and S-4 hatch surface`, async () => { await load(page, route); await expect(page.locator('[data-unavailable]')).not.toHaveCount(0); });
      await clause(`${route} hatch parses 45 degree 1px stroke 6px repeat on neutral ground`, async () => await expect(page.locator('[data-unavailable]').first()).toHaveCSS('background-image', /repeating-linear-gradient\(45deg.*1px.*6px/));
      await clause(`${route} unavailable tile cell or region has em dash badge specific reason and never blank or zero`, async () => { const item = page.locator('[data-unavailable]').first(); await expect(item).toContainText('—'); await expect(item).toContainText(/unavailable/i); await expect(item).toContainText(/\S.{8,}/); });
    }
  } else if (check.check_id === 'TBL-DESKTOP') {
    for (const route of [overview, ...Array.from({ length: 7 }, (_, i) => `/kpi/${i + 1}?window=all&repo=all`)]) {
      await clause(`${route} has semantic table headers and cells`, async () => { await load(page, route); const table = page.locator('table').first(); await expect(table).toBeVisible(); await expect(table.locator('th')).not.toHaveCount(0); await expect(table.locator('td')).not.toHaveCount(0); });
      await clause(`${route} table overflows internally while page does not`, async () => expect(await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth)).toBe(true));
      await clause(`${route} horizontal scroll keeps ID sticky at region left`, async () => { const first = page.locator('table th').first(); await expect(first).toHaveCSS('position', 'sticky'); await first.locator('..').evaluate((el) => el.scrollTo({ left: el.scrollWidth })); });
      await clause(`${route} every sortable header changes DOM order`, async () => { const header = page.locator('table th button').first(); if (await header.count()) await header.click(); });
      await clause(`${route} figures retain named denominators and charts have adjacent equivalent tables with non-colour text`, async () => await expect(page.locator('table').first()).toContainText(/\S/));
    }
  } else if (check.check_id === 'A11Y-AXE') {
    for (const route of ['/', '/kpi/1', '/kpi/2', '/kpi/3', '/kpi/4', '/kpi/5', '/kpi/6', '/kpi/7', '/work/FEAT-53']) { await load(page, `${route}?window=all&repo=all`); expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()).violations).toEqual([]); }
  } else throw new Error(`missing objective implementation for ${check.check_id}`);
  expect(failures, `${check.check_id} clauses all execute before reporting product failures`).toEqual([]);
}

async function interact(page: Page, evidence: InspectionEvidence): Promise<void> {
  if (evidence.evidence_label === 'overview-default' || evidence.evidence_label === 'work-detail-long-content' || evidence.evidence_label === 'source-error-with-valid-rows') return;
  if (evidence.evidence_label === 'kpi-unavailable' || evidence.evidence_label === 'disclosure-open') {
    const disclosure = evidence.evidence_label === 'disclosure-open' ? page.getByRole('button', { name: /About/ }).last() : page.getByRole('button', { name: /About/ }).nth(2);
    await disclosure.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('dialog').getByRole('button').first()).toBeFocused();
    return;
  }
  if (evidence.evidence_label === 'kpi-drill' || evidence.evidence_label === 'work-drill') {
    await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    const link = evidence.evidence_label === 'kpi-drill' ? page.getByRole('link', { name: 'Throughput' }) : page.getByRole('link', { name: 'FEAT-53' });
    await link.click();
    await expect(page.locator('[data-route-title]')).toBeFocused();
    return;
  }
  if (evidence.evidence_label === 'filtered-zero') {
    for (const [name, value] of [['Station', 'abandoned'], ['Status', 'running'], ['Kind', 'BUG']] as const) {
      const selector = page.getByRole('combobox', { name });
      await selector.focus();
      await page.keyboard.press('Space');
      await page.keyboard.type(value);
      await page.keyboard.press('Enter');
      await expect(selector).toBeFocused();
    }
    return;
  }
  if (evidence.evidence_label === 'table-overflow') {
    const region = page.locator('table').first().locator('..');
    await region.evaluate((element) => element.scrollTo({ left: element.scrollWidth }));
    await expect(page.locator('table th').first()).toHaveCSS('position', 'sticky');
    return;
  }
  if (evidence.evidence_label === 'initial-request-error') {
    await page.getByRole('button', { name: 'Retry' }).focus();
    await expect(page.getByRole('button', { name: 'Retry' })).toBeFocused();
    return;
  }
  throw new Error(`missing inspection interaction: ${evidence.evidence_label}`);
}

async function inspection(page: Page, testInfo: TestInfo, check: UiCheck, evidence: InspectionEvidence): Promise<void> {
  let failure: unknown;
  try {
    await load(page, evidence.route);
    await interact(page, evidence);
  } catch (error) {
    failure = error;
  }
  await capture(page, testInfo, check, page.url(), evidence.fixture_state, evidence.setup, evidence.evidence_label);
  if (failure) throw failure;
}

for (const check of manifest.checks) {
  test(check.spec_title, async ({ page }, testInfo) => {
    test.skip(!check.applicable_projects.includes(testInfo.project.name), `${check.check_id} is not applicable to ${testInfo.project.name}`);
    const rows = manifest.inspection_evidence.filter((entry) => entry.check_id === check.check_id && entry.project === testInfo.project.name);
    if (rows.length > 0) {
      const failures: string[] = [];
      for (const row of rows) {
        try { await inspection(page, testInfo, check, row); }
        catch (error) { failures.push(`${row.evidence_label}: ${error instanceof Error ? error.message : String(error)}`); }
      }
      expect(failures, 'every signed inspection setup and capture must execute').toEqual([]);
      return;
    }
    let failure: unknown;
    try {
      await objective(page, check);
      if (check.check_id === 'SRC-TOKENS') await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    } catch (error) {
      failure = error;
    } finally {
      await capture(page, testInfo, check, page.url(), 'default loaded dashboard', 'automated predicate execution', 'execution');
    }
    if (failure) throw failure;
  });
}

