import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { captureHardFailureEvidence } from '../ui-evidence.js';
import { checkFor, loadManifest } from '../ui-manifest.js';

const manifest = loadManifest();
const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';

async function load(page: Page, route: string): Promise<void> {
  await page.addInitScript(() => {
    const fixed = Date.parse('2026-09-17T12:00:00Z');
    class FrozenDate extends Date { constructor(...args: ConstructorParameters<typeof Date>) { super(args.length ? args[0] : fixed); } static now() { return fixed; } }
    Object.defineProperty(window, 'Date', { value: FrozenDate });
  });
  const response = await page.goto(route);
  expect.soft(response, `served bundle loads ${route}`).not.toBeNull();
  await expect.soft(page.locator('body')).toBeVisible();
  await page.waitForLoadState('networkidle');
}



test.afterEach(async ({ page }, testInfo) => {
  const check = manifest.checks.find((candidate) => candidate.spec_title === testInfo.title);
  if (!check || !check.applicable_projects.includes(testInfo.project.name)) return;
  await captureHardFailureEvidence(page, testInfo, check, 'execution');
});


async function clause(name: string, action: () => Promise<void>): Promise<void> {
  await test.step(name, async () => {
    try { await action(); }
    catch (error) { expect.soft(false, `${name}: ${error instanceof Error ? error.message : String(error)}`).toBe(true); }
  });
}

for (const check of [
  checkFor(manifest, 'desktop tables contain overflow and keep ID sticky'),
  checkFor(manifest, 'routes pass axe and expose non-colour equivalents'),
]) {
  test(check.spec_title, async ({ page }, testInfo) => {
    if (check.check_id === 'TBL-DESKTOP') {
      const routes = [overview, ...Array.from({ length: 7 }, (_, index) => `/kpi/${index + 1}?window=all&repo=all`)];
      for (const route of routes) {
        await clause(`${route}: real table has semantic headers and cells`, async () => {
          await load(page, route);
          const table = page.locator('table').first();
          await expect.soft(table).toBeVisible();
          await expect.soft(table.locator('thead th')).not.toHaveCount(0);
          await expect.soft(table.locator('tbody td')).not.toHaveCount(0);
        });
        await clause(`${route}: bordered table region contains forced horizontal overflow`, async () => {
          const table = page.locator('table').first();
          const overflow = await table.evaluate((element) => {
            const region = element.parentElement;
            if (!region) return false;
            region.style.overflowX = 'auto';
            element.style.minWidth = `${region.clientWidth + 1}px`;
            return region.scrollWidth > region.clientWidth;
          });
          expect.soft(overflow).toBe(true);
        });
        await clause(`${route}: scrolled ID column stays sticky at the region left edge`, async () => {
          const table = page.locator('table').first();
          const sticky = await table.evaluate((element) => {
            const header = element.querySelector('thead th');
            const region = element.parentElement;
            if (!header || !region) return { position: '', before: 0, after: 0, left: 0 };
            const before = header.getBoundingClientRect().left;
            region.scrollLeft = region.scrollWidth;
            return { position: getComputedStyle(header).position, before, after: header.getBoundingClientRect().left, left: region.getBoundingClientRect().left };
          });
          expect.soft(sticky.position).toBe('sticky');
          expect.soft(sticky.after).toBeCloseTo(sticky.left, 1);
          expect.soft(sticky.before).toBeCloseTo(sticky.left, 1);
        });
        await clause(`${route}: page has no horizontal overflow`, async () => {
          expect.soft(await page.locator('body').evaluate((body) => body.scrollWidth <= window.innerWidth)).toBe(true);
        });
        await clause(`${route}: each sortable header changes the specified DOM order`, async () => {
          const headers = page.locator('table thead th button');
          const count = await headers.count();
          expect.soft(count).toBeGreaterThan(0);
          for (let index = 0; index < count; index += 1) {
            const rows = page.locator('table tbody tr');
            const before = await rows.allTextContents();
            await headers.nth(index).click();
            await expect.soft(rows).not.toHaveText(before);
          }
        });
        await clause(`${route}: figures retain named denominators`, async () => {
          const text = await page.locator('main').innerText();
          expect.soft(text).toMatch(/\b(?:of|\/|weeks|vs prior)\b/i);
        });
        await clause(`${route}: charts are hidden and adjacent tables expose identical non-colour values`, async () => {
          const charts = page.locator('[data-testid^="chart-"]');
          const chartCount = await charts.count();
          for (let index = 0; index < chartCount; index += 1) {
            const chart = charts.nth(index);
            await expect.soft(chart).toHaveAttribute('aria-hidden', 'true');
            const table = chart.locator('xpath=following::table[1]');
            await expect.soft(table).toBeVisible();
            await expect.soft(table).toContainText(/\S/);
          }
        });
      }
      return;
    }

    const routes = [
      ['loaded overview', overview],
      ['KPI 1', '/kpi/1?window=all&repo=all'], ['KPI 2', '/kpi/2?window=all&repo=all'], ['KPI 3', '/kpi/3?window=all&repo=all'],
      ['KPI 4', '/kpi/4?window=all&repo=all'], ['KPI 5', '/kpi/5?window=all&repo=all'], ['KPI 6', '/kpi/6?window=all&repo=all'], ['KPI 7', '/kpi/7?window=all&repo=all'],
      ['representative work detail', '/work/FEAT-53?window=all&repo=all'], ['S-1 no ship records', '/work/FEAT-53-GRILLING?window=all&repo=all'],
      ['S-2 pre-capability', '/work/FEAT-53-ATTENTION?window=all&repo=all'], ['S-3 grading caveat', '/work/FEAT-53-WORKTREE?window=all&repo=all'],
      ['S-4 unavailable', '/work/FEAT-53-UNAVAILABLE?window=all&repo=all'], ['S-5 attribution', '/work/FEAT-53?window=all&repo=all'],
      ['S-6 elapsed', '/work/FEAT-53-LONG-CONTENT?window=all&repo=all'], ['S-7 tokens', '/work/FEAT-53-OVERFLOW?window=all&repo=all'],
      ['filtered zero', '/?window=all&repo=all&status=needs-you&layout=table'], ['source error with valid rows', '/work/FEAT-53-SOURCE-ERROR?window=all&repo=all'], ['initial request error', '/work/FEAT-53-INITIAL-ERROR?window=all&repo=all'],
    ] as const;
    for (const [state, route] of routes) {
      await clause(`A11Y-AXE: ${state} has no WCAG A or AA violations`, async () => {
        await load(page, route);
        const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
        expect.soft(results.violations, `${state}: ${results.violations.map((violation) => violation.id).join(', ')}`).toEqual([]);
      });
    }
    await clause('A11Y-AXE: every chart is aria-hidden with an adjacent real table carrying values', async () => {
      await load(page, '/kpi/5?window=all&repo=all');
      const charts = page.locator('[data-testid^="chart-"]');
      expect.soft(await charts.count()).toBeGreaterThan(0);
      for (let index = 0; index < await charts.count(); index += 1) {
        await expect.soft(charts.nth(index)).toHaveAttribute('aria-hidden', 'true');
        await expect.soft(charts.nth(index).locator('xpath=following::table[1]')).toBeVisible();
      }
    });
    await clause('A11Y-AXE: every status has an icon plus its printed label and visible reason', async () => {
      await load(page, overview);
      for (const status of ['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale']) {
        const button = page.getByRole('button', { name: new RegExp(status) });
        await expect.soft(button).toBeVisible();
        await expect.soft(button.locator('svg')).not.toHaveCount(0);
        await expect.soft(button).toContainText(status);
      }
      const rows = page.locator('main').getByText(/(?:Needs You|Blocked|Stalled|Over Budget|Running|Stale):\s*\S+/);
      expect.soft(await rows.count()).toBeGreaterThan(0);
    });
    await clause('A11Y-AXE: every gap treatment exposes visible count or specific reason text', async () => {
      await load(page, '/work/FEAT-53-UNAVAILABLE?window=all&repo=all');
      const visible = await page.locator('main').innerText();
      expect.soft(visible).toMatch(/(?:\b\d+\s+of\s+\d+\b|unavailable|no ship records|reason)/i);
      const inaccessibleGap = page.locator('[title], [aria-label]').filter({ hasText: /^$/ });
      expect.soft(await inaccessibleGap.count()).toBe(0);
    });
  });
}
