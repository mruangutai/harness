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

type PaintProperty = 'color' | 'stroke' | 'fill' | 'backgroundColor' | 'borderTopColor' | 'borderRightColor' | 'borderBottomColor' | 'borderLeftColor';

type TokenRole = {
  selector: string;
  property: PaintProperty;
  name: string;
  token: string;
  fillOpacity?: string;
};

type AuthoredPaint = {
  node: string;
  property: PaintProperty;
  value: string;
  tokens: string[];
};

const kpiRoles = (kpi: number): TokenRole[] => {
  const token = `--color-metrics-kpi-${kpi}`;
  return [
    { selector: `[data-kpi-identity-dot="${kpi}"]`, property: 'backgroundColor', name: '8px label dot', token },
    { selector: `[data-kpi-sparkline-stroke="${kpi}"]`, property: 'stroke', name: 'sparkline stroke', token },
    { selector: `[data-kpi-sparkline-fill="${kpi}"]`, property: 'fill', name: '12%-alpha sparkline fill', token, fillOpacity: '0.12' },
    { selector: `[data-kpi-sparkline-end-dot="${kpi}"]`, property: 'fill', name: 'sparkline end dot', token },
    { selector: `[data-kpi-panel-accent="${kpi}"]`, property: 'borderTopColor', name: 'panel accent', token },
    { selector: `[data-kpi-shape-b-line="${kpi}"]`, property: 'stroke', name: 'Shape B line', token },
    { selector: `[data-kpi-shape-b-y-title="${kpi}"]`, property: 'fill', name: 'Shape B y-title', token },
    { selector: `[data-kpi-column-dot="${kpi}"]`, property: 'backgroundColor', name: 'column-header dot', token },
  ];
};

const statusNeutralRoles = (status: string): TokenRole[] => [
  { selector: `[data-status-icon="${status}"]`, property: 'color', name: 'icon', token: '--color-neutral' },
  { selector: `[data-status-count="${status}"]`, property: 'color', name: 'count', token: '--color-neutral' },
  { selector: `[data-status-background="${status}"]`, property: 'backgroundColor', name: 'background', token: '--color-neutral' },
  { selector: `[data-status-border="${status}"]`, property: 'borderTopColor', name: 'border', token: '--color-neutral' },
  { selector: `[data-status-top-line="${status}"]`, property: 'borderTopColor', name: 'top line', token: '--color-neutral' },
  { selector: `[data-status-selection="${status}"]`, property: 'backgroundColor', name: 'selected treatment', token: '--color-neutral' },
];

function cssProperty(property: PaintProperty): string {
  return property.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
}

async function authoredPaints(page: Page, roles: TokenRole[] = [], selector = 'body *'): Promise<AuthoredPaint[]> {
  return page.locator(selector).evaluateAll((nodes, allowedRoles) => {
    const properties = ['color', 'stroke', 'fill', 'backgroundColor', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor'] as const;
    const cssName = (property: string) => property.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
    const specificity = (selector: string) => (selector.match(/#[\w-]+/g)?.length ?? 0) * 10_000
      + (selector.match(/(?:\.[\w-]+|\[[^\]]+\]|:(?!:)[\w-]+)/g)?.length ?? 0) * 100
      + (selector.match(/(?:^|[\s>+~])([a-z][\w-]*)/gi)?.length ?? 0);
    const valueFor = (node: Element, property: string) => {
      const name = cssName(property);
      const candidates: Array<{ value: string; important: boolean; specificity: number; order: number }> = [];
      const add = (value: string, important: boolean, selectorSpecificity: number, order: number) => {
        if (value) candidates.push({ value: value.trim(), important, specificity: selectorSpecificity, order });
      };
      add(node.getAttribute(name) ?? '', false, 0, -1);
      let order = 0;
      const visit = (rules: CSSRuleList) => {
        for (const rule of rules) {
          if (rule instanceof CSSStyleRule) {
            for (const ruleSelector of rule.selectorText.split(',')) {
              if (node.matches(ruleSelector)) add(rule.style.getPropertyValue(name), rule.style.getPropertyPriority(name) === 'important', specificity(ruleSelector), order);
            }
            order += 1;
          } else if ('cssRules' in rule) {
            visit((rule as CSSGroupingRule).cssRules);
          }
        }
      };
      for (const sheet of document.styleSheets) {
        try {
          visit(sheet.cssRules);
        } catch {
          // Cross-origin stylesheets cannot author the dashboard's local semantic tokens.
        }
      }
      const style = (node as HTMLElement).style;
      add(style.getPropertyValue(name), style.getPropertyPriority(name) === 'important', 1_000_000, order + 1);
      return candidates.sort((left, right) => Number(right.important) - Number(left.important) || right.specificity - left.specificity || right.order - left.order)[0]?.value ?? '';
    };
    return nodes.flatMap((node) => properties.map((property) => ({
      node: node.outerHTML.slice(0, 200),
      property,
      value: valueFor(node, property),
      tokens: allowedRoles.filter((role) => role.property === property && node.matches(role.selector)).map((role) => role.token),
    })).filter((declaration) => declaration.value));
  }, roles);
}

async function expectPaint(page: Page, selector: string, property: PaintProperty, colour: string, name: string): Promise<void> {
  const locator = page.locator(selector);
  const count = await locator.count();
  expect.soft(count, `${name} must be rendered`).toBeGreaterThan(0);
  if (count) {
    const paints = await locator.evaluateAll((nodes, key) => nodes.map((node) => getComputedStyle(node)[key as keyof CSSStyleDeclaration]), property);
    for (const paint of paints) expect.soft(paint, `${name} must use its signed token`).toBe(colour);
  }
}

async function expectOwnedPaint(page: Page, role: TokenRole, token: string, colour: string, name: string): Promise<void> {
  const locator = page.locator(role.selector);
  const count = await locator.count();
  expect.soft(count, `${name} must be rendered`).toBeGreaterThan(0);
  const declarations = await authoredPaints(page, [role], role.selector);
  const property = cssProperty(role.property);
  for (const node of await locator.elementHandles()) {
    const html = await node.evaluate((element) => element.outerHTML.slice(0, 200));
    const declaration = declarations.find((candidate) => candidate.node === html && cssProperty(candidate.property) === property);
    expect.soft(declaration?.value, `${name} must own ${token} before substitution`).toBe(`var(${token})`);
  }
  await expectPaint(page, role.selector, role.property, colour, name);
  if (role.fillOpacity) {
    const opacity = await locator.evaluateAll((nodes) => nodes.map((node) => getComputedStyle(node).fillOpacity));
    for (const value of opacity) expect.soft(value, `${name} must compute fill-opacity ${role.fillOpacity}`).toBe(role.fillOpacity);
  }
}

async function expectNoOtherToken(page: Page, token: string, name: string, declarations?: AuthoredPaint[]): Promise<void> {
  const offenders = (declarations ?? await authoredPaints(page)).filter((declaration) => declaration.value.includes(token) && !declaration.tokens.includes(token));
  expect.soft(offenders, `${name} must not be authored on another selector or property`).toEqual([]);
}



test.afterEach(async ({ page }, testInfo) => {
  const check = manifest.checks.find((candidate) => candidate.spec_title === testInfo.title);
  if (!check || !check.applicable_projects.includes(testInfo.project.name)) return;
  await captureHardFailureEvidence(page, testInfo, check, 'execution');
});


async function kpiIdentity(page: Page): Promise<void> {
  const allRoles = Array.from({ length: 7 }, (_, index) => kpiRoles(index + 1)).flat();
  const declarations = await authoredPaints(page, allRoles);
  for (let kpi = 1; kpi <= 7; kpi += 1) {
    const token = `--color-metrics-kpi-${kpi}`;
    const roles = kpiRoles(kpi);
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} resolves identity token`, async () => expect.soft(await tokenColour(page, token), `${token} resolves`).not.toBe(''));
    const colour = await tokenColour(page, token);
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} label dot uses identity token`, async () => expectOwnedPaint(page, roles[0], token, colour, `KPI ${kpi} 8px label dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline stroke uses identity token`, async () => expectOwnedPaint(page, roles[1], token, colour, `KPI ${kpi} sparkline stroke`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline fill uses 12 percent identity token`, async () => expectOwnedPaint(page, roles[2], token, colour, `KPI ${kpi} 12%-alpha sparkline fill`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} sparkline end dot uses identity token`, async () => expectOwnedPaint(page, roles[3], token, colour, `KPI ${kpi} sparkline end dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} panel accent uses identity token`, async () => expectOwnedPaint(page, roles[4], token, colour, `KPI ${kpi} panel accent`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} Shape B line uses identity token`, async () => expectOwnedPaint(page, roles[5], token, colour, `KPI ${kpi} Shape B line`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} Shape B y-title uses identity token`, async () => expectOwnedPaint(page, roles[6], token, colour, `KPI ${kpi} Shape B y-title`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} column-header dot uses identity token`, async () => expectOwnedPaint(page, roles[7], token, colour, `KPI ${kpi} column-header dot`));
    await test.step(`DIR-KPI-IDENTITY: KPI ${kpi} excludes delta grade status text border background gap and other elements`, async () => expectNoOtherToken(page, token, `KPI ${kpi} identity token`, declarations));
  }
}

async function statusLabels(page: Page): Promise<void> {
  const allKpiRoles = Array.from({ length: 7 }, (_, index) => kpiRoles(index + 1)).flat();
  const statusRoles = statuses.map((status) => {
    const name = slug(status);
    return { selector: `[data-status-label="${name}"]`, property: 'color' as const, name: 'attention-label text', token: `--color-metrics-status-${name}` };
  });
  const declarations = await authoredPaints(page, [...allKpiRoles, ...statusRoles]);
  for (let kpi = 1; kpi <= 7; kpi += 1) {
    const token = `--color-metrics-kpi-${kpi}`;
    await expectNoOtherToken(page, token, `KPI ${kpi} identity token`, declarations);
  }
  for (const status of statuses) {
    const name = slug(status);
    const token = `--color-metrics-status-${name}`;
    const colour = await tokenColour(page, token);
    const label = { selector: `[data-status-label="${name}"]`, property: 'color' as const, name: 'attention-label text', token };
    const card = page.getByRole('button', { name: new RegExp(`^${status}`) });
    await test.step(`DIR-STATUS-LABEL: ${status} status token resolves`, async () => expect.soft(colour, `${status} status token resolves`).not.toBe(''));
    await test.step(`DIR-STATUS-LABEL: ${status} matching attention-label text uses status token`, async () => expectOwnedPaint(page, label, token, colour, `${status} attention-label text`));
    await test.step(`DIR-STATUS-LABEL: ${status} token occurs on no other element`, async () => expectNoOtherToken(page, token, `${status} status token`, declarations));
    for (const role of statusNeutralRoles(name)) {
      await test.step(`DIR-STATUS-LABEL: ${status} ${role.name} remains neutral before selection`, async () => {
        const neutral = await tokenColour(page, role.token);
        await expectPaint(page, role.selector, role.property, neutral, `${status} ${role.name}`);
      });
    }
    await test.step(`DIR-STATUS-LABEL: ${status} selection remains neutral after selection`, async () => {
      await expect.soft(card, `${status} attention card exists`).toHaveCount(1);
      if (await card.count()) await card.click();
      for (const role of statusNeutralRoles(name)) {
        const neutral = await tokenColour(page, role.token);
        await expectPaint(page, role.selector, role.property, neutral, `${status} ${role.name}`);
      }
      const selectedDeclarations = await authoredPaints(page, [...allKpiRoles, ...statusRoles]);
      for (let kpi = 1; kpi <= 7; kpi += 1) {
        const kpiToken = `--color-metrics-kpi-${kpi}`;
        await expectNoOtherToken(page, kpiToken, `KPI ${kpi} identity token`, selectedDeclarations);
      }
      for (const statusRole of statusRoles) {
        const statusColour = await tokenColour(page, statusRole.token);
        await expectOwnedPaint(page, statusRole, statusRole.token, statusColour, `${statusRole.name} after selection`);
        await expectNoOtherToken(page, statusRole.token, `${statusRole.name} status token after selection`, selectedDeclarations);
      }
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
