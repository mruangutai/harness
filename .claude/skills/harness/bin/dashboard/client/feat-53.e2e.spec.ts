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
    try { await action(); }
    catch (error) { failures.push(`${name}: ${error instanceof Error ? error.message : String(error)}`); }
  };
  await clause('overview tab order and noncontrols', async () => {
    await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    const tiles = page.locator('[aria-label="Repository KPIs"] a');
    const infos = page.getByRole('button', { name: /About/ });
    await expect(tiles).toHaveCount(7);
    await expect(infos).toHaveCount(7);
    await expectFocusOrder(page, [page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), ...Array.from({ length: 7 }, (_, index) => tiles.nth(index))]);
    for (let index = 0; index < 7; index += 1) { await page.keyboard.press('Tab'); await expect(infos.nth(index)).toBeFocused(); }
    await expect(page.locator('svg, [data-chart], [data-unavailable], [data-status-badge]')).toHaveAttribute('aria-hidden', 'true');
  });
  await clause('selector pointer and keyboard restoration', async () => {
    const station = page.getByRole('combobox', { name: 'Station' });
    await station.click(); await page.keyboard.press('Escape'); await expect(station).toBeFocused(); await expect(station).toHaveCSS('outline-width', '0px');
    await station.focus(); await page.keyboard.press('Space'); await page.keyboard.press('Escape'); await expect(station).toBeFocused(); await expect(station).toHaveCSS('outline-width', '2px');
  });
  await clause('tile route and Back restoration', async () => {
    const tile = page.locator('[aria-label="Repository KPIs"] a').first();
    await tile.click(); await expect(page.locator('[data-route-title]')).toBeFocused(); await page.goBack(); await expect(tile).toBeFocused();
  });
  await clause('attention filters layout and announcements', async () => {
    await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    const attentionCard = page.getByRole('button', { name: /Needs You/ });
    await attentionCard.click();
    const status = page.getByRole('combobox', { name: 'Status' });
    await expect(status).toBeFocused();
    await status.focus(); await page.keyboard.press('Space'); await page.keyboard.press('ArrowDown'); await page.keyboard.press('Enter'); await expect(status).toBeFocused();
    const layout = page.getByRole('button', { name: 'Kanban' });
    await layout.click(); await expect(layout).toBeFocused(); await expect(page.locator('[aria-live="polite"]')).toContainText(/\d+ of \d+ items/);
  });
  await clause('grilling and worktree restoration', async () => {
    for (const row of ['Grilling', 'Worktree']) {
      const toggle = page.getByRole('button', { name: row });
      await toggle.click(); await expect(toggle).toBeFocused(); await toggle.click(); await expect(toggle).toBeFocused();
    }
  });
  await clause('KPI tab order and disclosure close variants', async () => {
    await load(page, '/kpi/1?window=all&repo=all');
    const disclosure = page.getByRole('button', { name: /About/ });
    await expectFocusOrder(page, [page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' }), disclosure]);
    await disclosure.focus(); await page.keyboard.press('Enter'); await expect(page.getByRole('dialog').getByRole('button').first()).toBeFocused(); await page.keyboard.press('Escape'); await expect(disclosure).toBeFocused();
    await disclosure.click(); await page.mouse.click(1, 1); await expect(disclosure).toBeFocused();
  });
  await clause('work detail fresh load and tab order', async () => {
    await load(page, '/work/FEAT-53?window=all&repo=all');
    const title = page.locator('[data-route-title]');
    await expect(title).not.toBeFocused(); await expect(title).toHaveAttribute('tabindex', '-1'); await expect(title).toHaveCSS('outline-width', '0px');
    await expectFocusOrder(page, [page.getByRole('radio', { name: '30d' }), page.getByRole('radio', { name: '90d' }), page.getByRole('radio', { name: 'All' }), page.getByRole('combobox', { name: 'Repository' })]);
  });
  expect(failures, 'all C3 keyboard clauses must execute before reporting product failures').toEqual([]);
}

async function objective(page: Page, check: UiCheck): Promise<void> {
  if (check.check_id === 'SRC-TOKENS') return sourceTokens();
  await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
  if (check.check_id === 'C1-HEADER-GEOMETRY') {
    for (const route of ['/?window=all&repo=all', '/kpi/7?window=all&repo=all', '/work/FEAT-53?window=all&repo=all']) {
      await load(page, route);
      const header = page.locator('header');
      const main = page.locator('main');
      const repository = page.getByRole('combobox', { name: 'Repository' });
      await expect(header, `${route} must expose a shared header`).toBeVisible();
      const [headerBox, mainBox, repositoryBox] = await Promise.all([header.boundingBox(), main.boundingBox(), repository.boundingBox()]);
      expect(headerBox?.height ?? 0).toBeGreaterThanOrEqual(72);
      expect(repositoryBox?.width ?? 0).toBeGreaterThanOrEqual(180);
      expect(headerBox?.x).toBe(mainBox?.x);
      await expect(page.getByRole('radio', { name: '30d' })).toBeVisible();
      await expect(page.getByRole('radio', { name: '90d' })).toBeVisible();
      await expect(page.getByRole('radio', { name: 'All' })).toBeVisible();
    }
  } else if (check.check_id === 'KPI-R1') {
    const tiles = page.locator('[aria-label="Repository KPIs"] a');
    await expect(tiles).toHaveCount(7);
    await expect(tiles).toHaveText(['Throughput', 'Rework', 'Blocking Human Touchpoints', 'Escaped Defects', 'Code Grading', 'Usage by Agent / Model Tier', 'Merged PRs Over Time']);
    const boxes = await tiles.evaluateAll((links) => links.map((link) => { const box = link.closest('[data-elevation]')?.getBoundingClientRect() ?? link.getBoundingClientRect(); return { x: box.x, y: box.y, width: box.width }; }));
    expect(new Set(boxes.slice(0, 4).map((box) => box.y)).size).toBe(1);
    expect(new Set(boxes.slice(4).map((box) => box.y)).size).toBe(1);
    expect(boxes[0].y).toBeLessThan(boxes[4].y);
    expect(new Set(boxes.slice(0, 4).map((box) => box.width)).size).toBe(1);
    expect(new Set(boxes.slice(4).map((box) => box.width)).size).toBe(1);
  } else if (check.check_id === 'DIR-KPI-IDENTITY') {
    const tokenColours = await page.locator('html').evaluate((element) => Array.from({ length: 7 }, (_, index) => getComputedStyle(element).getPropertyValue(`--color-metrics-kpi-${index + 1}`).trim()));
    expect(tokenColours.every(Boolean), 'all seven KPI identity tokens must resolve').toBe(true);
    await expect(page.locator('[aria-label="Repository KPIs"] [data-kpi-identity-dot]'), 'each tile must expose its identity dot').toHaveCount(7);
    await expect(page.locator('[aria-label="Repository KPIs"] [data-kpi-sparkline]'), 'each tile must expose its sparkline identity mark').toHaveCount(7);
  } else if (check.check_id === 'DIR-STATUS-LABEL') {
    for (const status of ['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale']) {
      const card = page.getByRole('button', { name: new RegExp(status) });
      await expect(card).toBeVisible();
      await card.click();
      await expect(card).toBeFocused();
      await expect(card.locator('[data-status-label]'), `${status} must mark the only status-coloured label`).toHaveCount(1);
    }
  } else if (check.check_id === 'C3-KEYBOARD') await keyboard(page);
  else if (check.check_id === 'C3-CONTRAST') {
    const colours = await page.locator('html').evaluate((element) => {
      const style = getComputedStyle(element);
      return ['--color-text-primary', '--color-text-secondary', '--color-metrics-text-tertiary', '--color-metrics-positive', '--color-metrics-negative', '--color-metrics-direction-neutral', ...Array.from({ length: 7 }, (_, index) => `--color-metrics-kpi-${index + 1}`), ...Array.from({ length: 6 }, (_, index) => ['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'][index]).map((status) => `--color-metrics-status-${status}`), ...Array.from({ length: 5 }, (_, index) => `--color-metrics-grade-${index + 1}`), '--color-metrics-unavailable-stroke'].map((name) => style.getPropertyValue(name));
    });
    const background = await page.locator('body').evaluate((element) => getComputedStyle(element).backgroundColor);
    expect(colours).toHaveLength(22);
    for (const colour of colours) expect(contrast(colour, background)).toBeGreaterThanOrEqual(3);
    expect(colours.slice(0, 19)).toHaveLength(19);
    for (const colour of colours.slice(0, 19)) expect(contrast(colour, background)).toBeGreaterThanOrEqual(4.5);
  } else if (check.check_id === 'C4-HATCH') {
    await load(page, '/kpi/3?window=all&repo=all');
    const unavailable = page.locator('[data-unavailable]');
    await expect(unavailable, 'unavailable state must be rendered from fixture data').not.toHaveCount(0);
    await expect(unavailable).toContainText('—');
    await expect(unavailable).toContainText(/unavailable/i);
    await expect(unavailable).toContainText(/\S.{8,}/);
    await expect(unavailable).toHaveCSS('background-image', /repeating-linear-gradient\(45deg/);
  } else if (check.check_id === 'TBL-DESKTOP') {
    const tables = page.locator('table');
    await expect(tables).not.toHaveCount(0);
    for (let index = 0; index < await tables.count(); index += 1) {
      const table = tables.nth(index);
      await expect(table.locator('th')).not.toHaveCount(0);
      await expect(table.locator('td')).not.toHaveCount(0);
      const first = table.locator('th').first();
      await expect(first).toHaveCSS('position', 'sticky');
      await first.click();
    }
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= window.innerWidth)).toBe(true);
  } else if (check.check_id === 'A11Y-AXE') {
    for (const route of ['/', '/kpi/1', '/kpi/2', '/kpi/3', '/kpi/4', '/kpi/5', '/kpi/6', '/kpi/7', '/work/FEAT-53']) {
      await load(page, `${route}?window=all&repo=all`);
      expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()).violations).toEqual([]);
    }
  } else throw new Error(`missing objective implementation for ${check.check_id}`);
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
    await objective(page, check);
    if (check.check_id === 'SRC-TOKENS') await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    await capture(page, testInfo, check, page.url(), 'default loaded dashboard', 'automated predicate execution', 'execution');
  });
}

