import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
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
  const bytes = Buffer.from(shot.data, 'base64');
  if (bytes.subarray(0, 4).toString() !== 'RIFF' || bytes.subarray(8, 12).toString() !== 'WEBP') throw new Error('Page.captureScreenshot did not return WebP evidence');
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

async function sourceTokens(): Promise<void> {
  const files = await sourceFiles(clientSource);
  const source = await Promise.all(files.filter((path) => /\.[tj]sx?$/.test(path)).map(async (path) => [path, await readFile(path, 'utf8')] as const));
  const components = source.filter(([path]) => !path.endsWith('/theme.ts'));
  expect(components, 'client source must be inspected, not manifest metadata').not.toEqual([]);
  for (const [path, text] of components) {
    expect(text, `${path} must not add raw hex colours`).not.toMatch(/#[0-9a-f]{3,8}\b/i);
    expect(text, `${path} must not add colour-scheme branches`).not.toMatch(/prefers-color-scheme|isDark/);
  }
  const chartFiles = components.filter(([, text]) => text.includes("from './charts'"));
  expect(chartFiles, 'chart mount source must be present').not.toEqual([]);
}

async function objective(page: Page, check: UiCheck): Promise<void> {
  if (check.check_id === 'SRC-TOKENS') return sourceTokens();
  await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
  if (check.check_id === 'C1-HEADER-GEOMETRY') {
    const header = page.getByRole('heading', { name: 'Operations Dashboard' });
    const repository = page.getByRole('combobox', { name: 'Repository' });
    await expect(header).toBeVisible(); await expect(repository).toBeVisible();
    const box = await header.boundingBox(); expect(box?.height ?? 0).toBeGreaterThan(0);
    await expect(page.getByRole('radio', { name: '30d' })).toBeVisible();
    await expect(page.getByRole('radio', { name: '90d' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'All' })).toBeVisible();
  }
  if (check.check_id === 'KPI-R1') {
    const tiles = page.locator('[aria-label="Repository KPIs"] a');
    await expect(tiles).toHaveCount(7);
    const boxes = await tiles.evaluateAll((links) => links.map((link) => { const box = link.closest('[class]')?.getBoundingClientRect() ?? link.getBoundingClientRect(); return { x: box.x, y: box.y, width: box.width }; }));
    expect(new Set(boxes.slice(0, 4).map((box) => box.y)).size).toBe(1);
    expect(new Set(boxes.slice(4).map((box) => box.y)).size).toBe(1);
    expect(boxes[0].y).toBeLessThan(boxes[4].y);
  }
  if (check.check_id === 'C3-KEYBOARD') {
    await page.locator('body').press('Control+Home');
    await page.keyboard.press('Tab');
    await expect(page.getByRole('radio', { name: '30d' })).toBeFocused();
    await expect(page.getByRole('radio', { name: '30d' })).toHaveCSS('outline-width', '2px');
    const tile = page.getByRole('link', { name: 'Throughput' });
    await tile.click();
    await expect(page.locator('[data-route-title]')).toBeFocused();
    await page.goBack();
    await expect(tile).toBeFocused();
  }
  if (check.check_id === 'C3-CONTRAST') {
    const ratio = await page.locator('body').evaluate((element) => {
      const rgb = getComputedStyle(element).backgroundColor.match(/\d+/g)?.map(Number) ?? [27, 27, 27];
      const channel = (value: number) => { const unit = value / 255; return unit <= .03928 ? unit / 12.92 : ((unit + .055) / 1.055) ** 2.4; };
      const light = .2126 * channel(rgb[0]) + .7152 * channel(rgb[1]) + .0722 * channel(rgb[2]); return (1.05) / (light + .05);
    });
    expect(ratio).toBeGreaterThanOrEqual(3);
  }
  if (check.check_id === 'C4-HATCH') await expect(page.locator('[style*="repeating-linear-gradient"], [class*="unavailable"]')).not.toHaveCount(0);
  if (check.check_id === 'TBL-DESKTOP') {
    const table = page.locator('table').first(); await expect(table).toBeVisible();
    await expect(table.locator('th')).not.toHaveCount(0); await expect(table.locator('td')).not.toHaveCount(0);
  }
  if (check.check_id === 'A11Y-AXE') expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()).violations).toEqual([]);
}

async function interact(page: Page, evidence: InspectionEvidence): Promise<void> {
  if (evidence.evidence_label === 'kpi-unavailable' || evidence.evidence_label === 'disclosure-open') {
    await page.getByRole('button', { name: /About/ }).first().press('Enter');
    await expect(page.getByRole('dialog')).toBeVisible();
  } else if (evidence.evidence_label === 'kpi-drill') {
    await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    await page.getByRole('link', { name: 'Throughput' }).click();
    await expect(page.locator('[data-route-title]')).toBeFocused();
  } else if (evidence.evidence_label === 'work-drill') {
    await load(page, '/?window=all&repo=all&station=all&status=all&kind=all&layout=table');
    await page.getByRole('link', { name: 'FEAT-53' }).click();
    await expect(page.locator('[data-route-title]')).toBeFocused();
  } else if (evidence.evidence_label === 'table-overflow') {
    const table = page.locator('table').first(); await table.evaluate((element) => element.parentElement?.scrollTo({ left: element.parentElement.scrollWidth }));
  } else if (evidence.evidence_label === 'initial-request-error') {
    await page.getByRole('button', { name: 'Retry' }).focus();
    await expect(page.getByRole('button', { name: 'Retry' })).toBeFocused();
  }
}

async function inspection(page: Page, testInfo: TestInfo, check: UiCheck, evidence: InspectionEvidence): Promise<void> {
  await load(page, evidence.route);
  await interact(page, evidence);
  await capture(page, testInfo, check, page.url(), evidence.fixture_state, evidence.setup, evidence.evidence_label);
}

for (const check of manifest.checks) {
  test(check.spec_title, async ({ page }, testInfo) => {
    test.skip(!check.applicable_projects.includes(testInfo.project.name), `${check.check_id} is not applicable to ${testInfo.project.name}`);
    const rows = manifest.inspection_evidence.filter((entry) => entry.check_id === check.check_id && entry.project === testInfo.project.name);
    if (rows.length > 0) { for (const row of rows) await inspection(page, testInfo, check, row); return; }
    await objective(page, check);
    await capture(page, testInfo, check, page.url(), 'default loaded dashboard', 'automated predicate execution', 'execution');
  });
}
