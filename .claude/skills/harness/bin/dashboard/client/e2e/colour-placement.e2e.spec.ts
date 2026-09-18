import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { captureHardFailureEvidence } from '../ui-evidence.js';
import { loadManifest } from '../ui-manifest.js';

const manifest = loadManifest();
const overview = '/?window=all&repo=all&station=all&status=all&kind=all&layout=table';
const statuses = ['Needs You', 'Blocked', 'Stalled', 'Over Budget', 'Running', 'Stale'] as const;

function slug(value: string): string {
  return value.toLowerCase().replaceAll(' ', '-');
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

async function tokenColour(page: Page, token: string): Promise<string> {
  return page.locator('html').evaluate((element, name) => {
    const probe = document.createElement('span');
    probe.style.color = `var(${name})`;
    element.append(probe);
    const colour = getComputedStyle(probe).color;
    probe.remove();
    return colour;
  }, token);
}

async function expectPaint(page: Page, selector: string, property: 'color' | 'stroke' | 'fill' | 'backgroundColor' | 'borderTopColor', colour: string, name: string): Promise<void> {
  const locator = page.locator(selector);
  const count = await locator.count();
  expect.soft(count, `${name} must be rendered`).toBeGreaterThan(0);
  if (count) {
    const paints = await locator.evaluateAll((nodes, key) => nodes.map((node) => getComputedStyle(node)[key as keyof CSSStyleDeclaration]), property);
    for (const paint of paints) expect.soft(paint, `${name} must use its signed token`).toBe(colour);
  }
}

async function expectNoOtherPaint(page: Page, colour: string, allowed: string, name: string): Promise<void> {
  const offenders = await page.locator(`body *:not(${allowed})`).evaluateAll((nodes, identity) => nodes.filter((node) => {
    const style = getComputedStyle(node);
    return [style.color, style.backgroundColor, style.borderTopColor, style.borderRightColor, style.borderBottomColor, style.borderLeftColor, style.fill, style.stroke].includes(identity);
  }).map((node) => node.outerHTML.slice(0, 200)), colour);
  expect.soft(offenders, `${name} must not colour a non-identity element`).toEqual([]);
}



test.afterEach(async ({ page }, testInfo) => {
  const check = manifest.checks.find((candidate) => candidate.spec_title === testInfo.title);
  if (!check || !check.applicable_projects.includes(testInfo.project.name)) return;
  await captureHardFailureEvidence(page, testInfo, check, 'execution');
});


async function kpiIdentity(page: Page): Promise<void> {
  for (let kpi = 1; kpi <= 7; kpi += 1) {
    const token = `--color-metrics-kpi-${kpi}`;
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} resolves identity token`, async () => expect.soft(await tokenColour(page, token), `${token} resolves`).not.toBe(''));
    const colour = await tokenColour(page, token);
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} label dot uses identity token`, async () => expectPaint(page, `[data-kpi-identity-dot="${kpi}"]`, 'backgroundColor', colour, `KPI ${kpi} 8px label dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline stroke uses identity token`, async () => expectPaint(page, `[data-kpi-sparkline-stroke="${kpi}"]`, 'stroke', colour, `KPI ${kpi} sparkline stroke`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline fill uses 12 percent identity token`, async () => expectPaint(page, `[data-kpi-sparkline-fill="${kpi}"]`, 'fill', colour, `KPI ${kpi} 12%-alpha sparkline fill`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline end dot uses identity token`, async () => expectPaint(page, `[data-kpi-sparkline-end-dot="${kpi}"]`, 'fill', colour, `KPI ${kpi} sparkline end dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} panel accent uses identity token`, async () => expectPaint(page, `[data-kpi-panel-accent="${kpi}"]`, 'borderTopColor', colour, `KPI ${kpi} panel accent`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} Shape B line uses identity token`, async () => expectPaint(page, `[data-kpi-shape-b-line="${kpi}"]`, 'stroke', colour, `KPI ${kpi} Shape B line`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} Shape B y-title uses identity token`, async () => expectPaint(page, `[data-kpi-shape-b-y-title="${kpi}"]`, 'fill', colour, `KPI ${kpi} Shape B y-title`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} column-header dot uses identity token`, async () => expectPaint(page, `[data-kpi-column-dot="${kpi}"]`, 'backgroundColor', colour, `KPI ${kpi} column-header dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} excludes delta grade status text border background gap and other elements`, async () => expectNoOtherPaint(page, colour, `[data-kpi-identity-mark="${kpi}"]`, `KPI ${kpi} identity token`));
  }
}

async function statusLabels(page: Page): Promise<void> {
  for (const status of statuses) {
    const name = slug(status);
    const colour = await tokenColour(page, `--color-metrics-status-${name}`);
    const label = `[data-status-label="${name}"]`;
    const card = page.getByRole('button', { name: new RegExp(`^${status}`) });
    await test.step(`DIR-STATUS-LABEL: ${status} status token resolves`, async () => expect.soft(colour, `${status} status token resolves`).not.toBe(''));
    await test.step(`DIR-STATUS-LABEL: ${status} matching attention-label text uses status token`, async () => expectPaint(page, label, 'color', colour, `${status} attention-label text`));
    await test.step(`DIR-STATUS-LABEL: ${status} token occurs on no other element`, async () => expectNoOtherPaint(page, colour, label, `${status} status token`));
    for (const [part, selector, property] of [
      ['icon', `[data-status-icon="${name}"]`, 'color'], ['count', `[data-status-count="${name}"]`, 'color'], ['background', `[data-status-background="${name}"]`, 'backgroundColor'], ['border', `[data-status-border="${name}"]`, 'borderTopColor'], ['top line', `[data-status-top-line="${name}"]`, 'borderTopColor'],
    ] as const) {
      await test.step(`DIR-STATUS-LABEL: ${status} ${part} remains neutral before selection`, async () => {
        const neutral = await tokenColour(page, '--color-neutral');
        await expectPaint(page, selector, property, neutral, `${status} ${part}`);
      });
    }
    await test.step(`DIR-STATUS-LABEL: ${status} selection remains neutral after selection`, async () => {
      await expect.soft(card, `${status} attention card exists`).toHaveCount(1);
      if (await card.count()) await card.click();
      const neutral = await tokenColour(page, '--color-neutral');
      await expectPaint(page, `[data-status-selection="${name}"]`, 'backgroundColor', neutral, `${status} selected treatment`);
    });
  }
}

for (const check of manifest.checks.filter((entry) => entry.check_id === 'DIR-KPI-IDENTITY' || entry.check_id === 'DIR-STATUS-LABEL')) {
  test(check.spec_title, async ({ page }, testInfo) => {
    test.skip(!check.applicable_projects.includes(testInfo.project.name), `${check.check_id} is not applicable to ${testInfo.project.name}`);
      await load(page, overview);
      if (check.check_id === 'DIR-KPI-IDENTITY') await kpiIdentity(page);
      else await statusLabels(page);
  });
}
