import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { access, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { loadManifest, type UiCheck } from '../ui-manifest.js';

const manifest = loadManifest();
const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..', '..');
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';
const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';

function contrast(foreground: string, background: string): number {
  const rgb = (colour: string) => (colour.match(/\d+/g) ?? []).slice(0, 3).map(Number);
  const luminance = (colour: number[]) => {
    const channel = (value: number) => {
      const unit = value / 255;
      return unit <= 0.03928 ? unit / 12.92 : ((unit + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * channel(colour[0]) + 0.7152 * channel(colour[1]) + 0.0722 * channel(colour[2]);
  };
  const [light, dark] = [luminance(rgb(foreground)), luminance(rgb(background))].sort((a, b) => b - a);
  return (light + 0.05) / (dark + 0.05);
}

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

async function capture(page: Page, testInfo: TestInfo, check: UiCheck): Promise<void> {
  await page.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}' });
  const session = await page.context().newCDPSession(page);
  const shot = await session.send('Page.captureScreenshot', { format: 'webp', captureBeyondViewport: true });
  if (!shot.data) throw new Error('Page.captureScreenshot returned empty WebP evidence');
  const relative = `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${testInfo.project.name}/${check.check_id}--execution.webp`;
  const path = resolve(root, relative);
  await mkdir(resolve(path, '..'), { recursive: true });
  try {
    await access(path);
    throw new Error(`duplicate screenshot evidence label: ${testInfo.project.name}/${check.check_id}/execution`);
  } catch (error) {
    if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error;
  }
  const bytes = Buffer.from(shot.data, 'base64');
  if (bytes.length <= 12 || bytes.subarray(0, 4).toString() !== 'RIFF' || bytes.subarray(8, 12).toString() !== 'WEBP') throw new Error('Page.captureScreenshot did not return nonempty WebP evidence');
  await writeFile(path, bytes);
  await testInfo.attach(`evidence:${check.check_id}:execution`, { path, contentType: 'image/webp' });
}

test.afterEach(async ({ page }, testInfo) => {
  const check = manifest.checks.find((candidate) => candidate.spec_title === testInfo.title);
  if (!check || !check.applicable_projects.includes(testInfo.project.name)) return;
  await capture(page, testInfo, check);
});


async function clause(failures: string[], name: string, action: () => Promise<void>): Promise<void> {
  await test.step(name, async () => {
    try { await action(); }
    catch (error) { failures.push(`${name}: ${error instanceof Error ? error.message : String(error)}`); }
  });
}

const nonTextTokens = [
  '--color-metrics-positive', '--color-metrics-negative',
  ...Array.from({ length: 7 }, (_, index) => `--color-metrics-kpi-${index + 1}`),
  ...['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'].map((name) => `--color-metrics-status-${name}`),
  ...Array.from({ length: 5 }, (_, index) => `--color-metrics-grade-${index + 1}`),
];
const informationalTokens = [
  '--color-text-primary', '--color-text-secondary', '--color-metrics-text-tertiary',
  '--color-metrics-positive', '--color-metrics-negative', '--color-metrics-direction-neutral',
  ...Array.from({ length: 7 }, (_, index) => `--color-metrics-kpi-${index + 1}`),
  ...['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'].map((name) => `--color-metrics-status-${name}`),
];

const contrastCheck = manifest.checks.find((check) => check.check_id === 'C3-CONTRAST');
const hatchCheck = manifest.checks.find((check) => check.check_id === 'C4-HATCH');
if (!contrastCheck || !hatchCheck) throw new Error('C3-CONTRAST and C4-HATCH must be present in the UI contract');

test(contrastCheck.spec_title, async ({ page }, testInfo) => {
  const failures: string[] = [];
    await load(page, overview);
    await clause(failures, 'C3-CONTRAST: exactly twenty non-text token pairings are evaluated', async () => {
      expect.soft(nonTextTokens).toHaveLength(20);
    });
    for (const token of nonTextTokens) {
      await clause(failures, `C3-CONTRAST: ${token} meets 3:1 non-text floor on computed card`, async () => {
        const [colour, card] = await page.locator('html').evaluate((element, name) => {
          const style = getComputedStyle(element);
          return [style.getPropertyValue(name).trim(), style.getPropertyValue('--color-background-card').trim()];
        }, token);
        expect.soft(colour, `${token} resolves on the rendered surface`).not.toBe('');
        expect.soft(contrast(colour, card), token).toBeGreaterThanOrEqual(3);
      });
    }
    await clause(failures, 'C3-CONTRAST: exactly nineteen informational token pairings are evaluated', async () => {
      expect.soft(informationalTokens).toHaveLength(19);
    });
    for (const token of informationalTokens) {
      await clause(failures, `C3-CONTRAST: ${token} meets 4.5:1 informational floor on computed card`, async () => {
        const [colour, card] = await page.locator('html').evaluate((element, name) => {
          const style = getComputedStyle(element);
          return [style.getPropertyValue(name).trim(), style.getPropertyValue('--color-background-card').trim()];
        }, token);
        expect.soft(colour, `${token} resolves on the rendered surface`).not.toBe('');
        expect.soft(contrast(colour, card), token).toBeGreaterThanOrEqual(4.5);
      });
    }
    await clause(failures, 'C3-CONTRAST: unavailable stroke meets 3:1 on computed hatch ground', async () => {
      const [stroke, ground] = await page.locator('html').evaluate((element) => {
        const style = getComputedStyle(element);
        return [style.getPropertyValue('--color-metrics-unavailable-stroke').trim(), style.getPropertyValue('--color-neutral').trim()];
      });
      expect.soft(stroke).not.toBe('');
      expect.soft(ground).not.toBe('');
      expect.soft(contrast(stroke, ground)).toBeGreaterThanOrEqual(3);
    });
    expect(failures, 'all C3-CONTRAST clauses execute before reporting product failures').toEqual([]);
});

test(hatchCheck.spec_title, async ({ page }, testInfo) => {
  const failures: string[] = [];
    for (const route of [overview, '/kpi/3?window=all&repo=all', '/work/FEAT-53?window=all&repo=all']) {
      await load(page, route);
      await clause(failures, `C4-HATCH: ${route} renders every S-2 and S-4 hatch use`, async () => {
        expect.soft(page.locator('[data-unavailable]'), `${route} unavailable surfaces`).not.toHaveCount(0);
      });
      await clause(failures, `C4-HATCH: ${route} computes a 45 degree unavailable-stroke band`, async () => {
        const image = await page.locator('[data-unavailable]').first().evaluate((element) => getComputedStyle(element).backgroundImage);
        expect.soft(image).toMatch(/repeating-linear-gradient\(45deg/i);
        expect.soft(image).toMatch(/var\(--color-metrics-unavailable-stroke\)|rgb\(/i);
      });
      await clause(failures, `C4-HATCH: ${route} computes a 1px unavailable-stroke band`, async () => {
        const image = await page.locator('[data-unavailable]').first().evaluate((element) => getComputedStyle(element).backgroundImage);
        expect.soft(image).toMatch(/(?:\s|,)1px(?:\s|,|\))/);
      });
      await clause(failures, `C4-HATCH: ${route} computes 6px repeat stops on neutral ground`, async () => {
        const [image, ground] = await page.locator('[data-unavailable]').first().evaluate((element) => [getComputedStyle(element).backgroundImage, getComputedStyle(element).getPropertyValue('--color-neutral').trim()]);
        expect.soft(image).toMatch(/6px/);
        expect.soft(ground).not.toBe('');
      });
      await clause(failures, `C4-HATCH: ${route} unavailable treatment has visible em dash`, async () => {
        await expect.soft(page.locator('[data-unavailable]').first()).toContainText('—');
      });
      await clause(failures, `C4-HATCH: ${route} unavailable treatment has visible unavailable badge`, async () => {
        await expect.soft(page.locator('[data-unavailable]').first()).toContainText(/unavailable/i);
      });
      await clause(failures, `C4-HATCH: ${route} unavailable treatment has specific visible reason and is neither blank nor zero`, async () => {
        const text = await page.locator('[data-unavailable]').first().innerText();
        expect.soft(text.trim()).not.toBe('');
        expect.soft(text).not.toMatch(/^\s*0(?:\.0+)?\s*$/);
        expect.soft(text).toMatch(/\S.{8,}/);
      });
    }
    expect(failures, 'all C4-HATCH clauses execute before reporting product failures').toEqual([]);
});
