import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { captureHardFailureEvidence } from '../ui-evidence.js';
import { loadManifest } from '../ui-manifest.js';

const manifest = loadManifest();
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



test.afterEach(async ({ page }, testInfo) => {
  const check = manifest.checks.find((candidate) => candidate.spec_title === testInfo.title);
  if (!check || !check.applicable_projects.includes(testInfo.project.name)) return;
  await captureHardFailureEvidence(page, testInfo, check, 'execution');
});


async function headerGeometry(page: Page): Promise<void> {
  for (const route of ['/?window=all&repo=all', '/kpi/7?window=all&repo=all', '/work/FEAT-53?window=all&repo=all']) {
    await test.step(`C1-HEADER-GEOMETRY: ${route} header is at least 72px high`, async () => {
      await load(page, route);
      expect.soft((await page.locator('header').boundingBox())?.height ?? 0).toBeGreaterThanOrEqual(72);
    });
    await test.step(`C1-HEADER-GEOMETRY: ${route} product name and breadcrumb compose the left group`, async () => {
      const header = page.locator('header');
      await expect.soft(header.getByText('Operations Dashboard')).toBeVisible({ timeout: 1_000 });
      await expect.soft(header.getByRole('link', { name: 'Overview' })).toBeVisible({ timeout: 1_000 });
    });
    await test.step(`C1-HEADER-GEOMETRY: ${route} window controls precede the 180px Repository selector in the right group`, async () => {
      const header = page.locator('header');
      const controls = header.getByRole('radio');
      const repository = header.getByRole('combobox', { name: 'Repository' });
      await expect.soft(controls).toHaveCount(3, { timeout: 1_000 });
      await expect.soft(controls.nth(0)).toHaveAccessibleName('30d', { timeout: 1_000 });
      await expect.soft(controls.nth(1)).toHaveAccessibleName('90d', { timeout: 1_000 });
      await expect.soft(controls.nth(2)).toHaveAccessibleName('All', { timeout: 1_000 });
      expect.soft((await repository.boundingBox())?.width ?? 0).toBeGreaterThanOrEqual(180);
      if (await controls.count() === 3 && await repository.count() === 1) expect.soft(await controls.last().evaluate((control, selector) => Boolean(control.compareDocumentPosition(selector as Node) & Node.DOCUMENT_POSITION_FOLLOWING), await repository.elementHandle())).toBe(true);
    });
    await test.step(`C1-HEADER-GEOMETRY: ${route} header main and footer container edges align`, async () => {
      const boxes = await Promise.all(['header', 'main', 'footer'].map((selector) => page.locator(selector).boundingBox()));
      const [header, main, footer] = boxes;
      expect.soft(header).not.toBeNull();
      expect.soft(main).not.toBeNull();
      expect.soft(footer).not.toBeNull();
      if (header && main && footer) {
        expect.soft([main.x, footer.x]).toEqual([header.x, header.x]);
        expect.soft([main.x + main.width, footer.x + footer.width]).toEqual([header.x + header.width, header.x + header.width]);
      }
    });
  }
}

async function kpiGrid(page: Page): Promise<void> {
  await load(page, overview);
  const tiles = page.locator('[aria-label="Repository KPIs"] a');
  await test.step('KPI-R1: seven KPI tiles exist in DOM order 1 through 7', async () => {
    await expect.soft(tiles).toHaveCount(7);
    expect.soft(await tiles.evaluateAll((links) => links.map((link) => link.getAttribute('href')))).toEqual(Array.from({ length: 7 }, (_, index) => `/kpi/${index + 1}`));
  });
  await test.step('KPI-R1: tiles 1 through 4 form the equal-width first row', async () => {
    const boxes = await tiles.evaluateAll((links) => links.slice(0, 4).map((link) => link.getBoundingClientRect().toJSON()));
    expect.soft(new Set(boxes.map((box) => box.y)).size).toBe(1);
    expect.soft(new Set(boxes.map((box) => box.width)).size).toBe(1);
  });
  await test.step('KPI-R1: tiles 5 through 7 form the equal-width second row', async () => {
    const boxes = await tiles.evaluateAll((links) => links.slice(4).map((link) => link.getBoundingClientRect().toJSON()));
    expect.soft(new Set(boxes.map((box) => box.y)).size).toBe(1);
    expect.soft(new Set(boxes.map((box) => box.width)).size).toBe(1);
  });
  await test.step('KPI-R1: the two rows are ordered 4 plus 3 with no spans or empty slots', async () => {
    const boxes = await tiles.evaluateAll((links) => links.map((link) => link.getBoundingClientRect().toJSON()));
    expect.soft(boxes[0]?.y).toBeLessThan(boxes[4]?.y ?? Number.NEGATIVE_INFINITY);
    expect.soft(boxes.slice(0, 4).every((box) => box.y === boxes[0]?.y)).toBe(true);
    expect.soft(boxes.slice(4).every((box) => box.y === boxes[4]?.y)).toBe(true);
  });
}

for (const check of manifest.checks.filter((candidate) => candidate.check_id === 'C1-HEADER-GEOMETRY' || candidate.check_id === 'KPI-R1')) {
  test(check.spec_title, async ({ page }, testInfo) => {
    test.skip(!check.applicable_projects.includes(testInfo.project.name), `${check.check_id} is not applicable to ${testInfo.project.name}`);
      if (check.check_id === 'C1-HEADER-GEOMETRY') await headerGeometry(page);
      else await kpiGrid(page);
  });
}
