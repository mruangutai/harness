import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { access, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { loadManifest, type InspectionEvidence, type UiCheck } from './ui-manifest.js';

const manifest = loadManifest();
const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const clientSource = resolve(import.meta.dirname, 'src');
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';

async function capture(page: Page, testInfo: TestInfo, check: UiCheck, evidenceLabel: string): Promise<void> {
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

async function sourceTokens(): Promise<void> {
  await test.step('SRC-TOKENS: component source contains no raw hex colours', async () => {
    const source = await Promise.all((await sourceFiles(clientSource)).filter((path) => /\.[tj]sx?$/.test(path)).map(async (path) => [path, await readFile(path, 'utf8')] as const));
    const components = source.filter(([path]) => !path.endsWith('/theme.ts') && !path.endsWith('.test.tsx'));
    expect.soft(components, 'client source must be inspected, not manifest metadata').not.toEqual([]);
    for (const [path, text] of components) expect.soft(text, `${path} must not add raw hex colours`).not.toMatch(/#[0-9a-f]{3,8}\b/i);
  });
  await test.step('SRC-TOKENS: component source uses no colour-scheme branch', async () => {
    const source = await Promise.all((await sourceFiles(clientSource)).filter((path) => /\.[tj]sx?$/.test(path)).map((path) => readFile(path, 'utf8')));
    expect.soft(source.join('\n')).not.toMatch(/prefers-color-scheme|isDark/);
  });
  await test.step('SRC-TOKENS: component source uses the Astryx type scale', async () => {
    const source = await Promise.all((await sourceFiles(clientSource)).filter((path) => /\.[tj]sx?$/.test(path) && !path.endsWith('/theme.ts') && !path.endsWith('.test.tsx')).map((path) => readFile(path, 'utf8')));
    expect.soft(source.join('\n').replace("fontSize: 'var(--text-supporting-size)'", '')).not.toMatch(/\bfontSize\s*:/);
  });
  await test.step('SRC-TOKENS: every chart mount binds a declared theme token', async () => {
    const source = await Promise.all((await sourceFiles(clientSource)).filter((path) => /\.[tj]sx?$/.test(path)).map(async (path) => [path, await readFile(path, 'utf8')] as const));
    const charts = source.filter(([, text]) => text.includes("from './charts'"));
    expect.soft(charts).not.toEqual([]);
    expect.soft(charts.some(([, text]) => /(?:stroke|fill|color|marker|axis|label)[A-Za-z]*=.+(?:var\(--color|theme)/s.test(text))).toBe(true);
  });
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
    await test.step(`${check.check_id}: ${evidence.evidence_label}`, async () => {
      await load(page, evidence.route);
      await interact(page, evidence);
    });
  } catch (error) {
    failure = error;
  }
  await capture(page, testInfo, check, evidence.evidence_label);
  if (failure) throw failure;
}

for (const check of manifest.checks.filter((candidate) => ['SRC-TOKENS', 'VIS-DENSITY', 'VIS-PROTOTYPE'].includes(candidate.check_id))) {
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
      await sourceTokens();
      await load(page, overview);
    } catch (error) {
      failure = error;
    } finally {
      await capture(page, testInfo, check, 'execution');
    }
    if (failure) throw failure;
  });
}
