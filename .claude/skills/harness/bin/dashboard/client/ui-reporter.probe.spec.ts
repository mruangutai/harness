import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import test from 'node:test';

const client = resolve(import.meta.dirname);
const root = resolve(client, '..', '..', '..', '..', '..', '..');
const feature = 'FEAT-53-metrics-dashboard';
const design = resolve(root, `.harness/harness/features/${feature}/DESIGN.md`);
const gate = resolve(root, '.claude/skills/harness/bin/ui_contract.py');
const packageDir = client;
const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();

type Defect = 'missing record' | 'duplicate' | 'mismatched title' | 'empty WebP' | 'parser error' | 'reporter error' | 'incomplete accounting';
type Reporter = { onBegin(config: object): void; onTestEnd(test: object, result: object): void; onEnd(result: object): Promise<void>; checks: Array<Record<string, unknown>>; reporterErrors: string[]; manifest?: { checks: Array<Record<string, unknown>> } };

async function reporterFor(runId: string): Promise<Reporter> {
  process.env.HARNESS_UI_RUN_ID = runId;
  process.env.HARNESS_UI_FEATURE = feature;
  const module = await import(`./ui-reporter.ts?${runId}`);
  return new module.default() as unknown as Reporter;
}

async function parserFailureReporter(runId: string): Promise<{ reporter: Reporter; results: string; cleanup: () => Promise<void> }> {
  const fixtureRoot = await mkdtemp(resolve(tmpdir(), 'ui-reporter-parser-'));
  const fixtureClient = resolve(fixtureRoot, '.claude/skills/harness/bin/dashboard/client');
  const fixtureBin = resolve(fixtureRoot, '.claude/skills/harness/bin');
  const fixtureGit = resolve(fixtureRoot, 'bin/git');
  await mkdir(dirname(fixtureGit), { recursive: true });
  await mkdir(fixtureClient, { recursive: true });
  await copyFile(resolve(client, 'ui-reporter.ts'), resolve(fixtureClient, 'ui-reporter.ts'));
  await copyFile(resolve(client, 'ui-manifest.ts'), resolve(fixtureClient, 'ui-manifest.ts'));
  await copyFile(gate, resolve(fixtureBin, 'ui_contract.py'));
  await writeFile(fixtureGit, `#!/bin/sh\necho ${commit}\n`, { mode: 0o755 });
  const oldPath = process.env.PATH;
  process.env.PATH = `${dirname(fixtureGit)}:${oldPath}`;
  process.env.HARNESS_UI_RUN_ID = runId;
  process.env.HARNESS_UI_FEATURE = feature;
  // The fixture root is runtime-selected so this import exercises the copied reporter against its absent design.
  const module = await import(`${new URL(`file://${fixtureClient}/ui-reporter.ts`).href}?${runId}`);
  return {
    reporter: new module.default() as unknown as Reporter,
    results: resolve(fixtureRoot, `.harness/harness/features/${feature}/runs/${runId}/ui/results.json`),
    cleanup: async () => {
      process.env.PATH = oldPath;
      await rm(fixtureRoot, { recursive: true, force: true });
    },
  };
}

function resultPath(runId: string): string {
  return resolve(root, `.harness/harness/features/${feature}/runs/${runId}/ui/results.json`);
}

async function normalRecord(reporter: Reporter, webp = true): Promise<void> {
  reporter.onBegin({});
  const contract = reporter.manifest!.checks[0];
  const evidence = resolve(tmpdir(), `ui-reporter-${Date.now()}-${Math.random()}.webp`);
  await writeFile(evidence, webp ? Buffer.from('RIFF0000WEBPpayload') : Buffer.alloc(0));
  reporter.onTestEnd(
    { title: contract.spec_title, parent: { project: () => ({ name: 'desktop-1440' }) } },
    { status: 'passed', attachments: [{ name: `evidence:${contract.check_id}:execution`, path: evidence }], errors: [] },
  );
}

async function inspectionSetupFailure(reporter: Reporter): Promise<void> {
  reporter.onBegin({});
  const contract = reporter.manifest!.checks.find((check) => String(check.method).startsWith('inspection'))!;
  const attachments = await Promise.all(
    Array.from({ length: 7 }, async (_, index) => {
      const evidence = resolve(tmpdir(), `ui-reporter-inspection-${Date.now()}-${index}.webp`);
      await writeFile(evidence, Buffer.from('RIFF0000WEBPpayload'));
      return { name: `evidence:${contract.check_id}:${['overview-default', 'kpi-unavailable', 'work-detail-long-content', 'filtered-zero', 'source-error-with-valid-rows', 'initial-request-error', 'table-overflow'][index]}`, path: evidence };
    }),
  );
  reporter.onTestEnd(
    { title: contract.spec_title, parent: { project: () => ({ name: 'desktop-1440' }) } },
    { status: 'passed', attachments, errors: [{ message: 'inspection setup failure' }] },
  );
}

async function assertInspectionSetupFailure(): Promise<void> {
  const runId = `probe-inspection-setup-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const reporter = await reporterFor(runId);
  await inspectionSetupFailure(reporter);
  await reporter.onEnd({ status: 'passed' });
  const results = resultPath(runId);
  const emitted = JSON.parse(await readFile(results, 'utf8'));
  assert.equal(emitted.summary.status, 'failed');
  assert.equal(emitted.checks[0].status, 'evidence');
  assert.match(emitted.checks[0].errors.join('\n'), /inspection setup failure/);
  assert.match(runGate(results, runId), /inspection setup failure/);
  await rm(dirname(dirname(results)), { recursive: true, force: true });
}

function runGate(results: string, runId: string): string {
  try {
    execFileSync('python3', [gate, 'gate', '--design', design, '--results', results, '--feature', feature, '--run-id', runId, '--served-bundle-commit', commit, '--repo-root', root, '--client-package', packageDir], { cwd: root, encoding: 'utf8', stdio: 'pipe' });
    assert.fail('ui_contract.py gate accepted the defective bundle');
  } catch (error) {
    const failure = error as { status?: number; stdout?: string; stderr?: string };
    assert.notEqual(failure.status, 0, 'ui_contract.py gate must refuse the defective bundle');
    return `${failure.stdout ?? ''}${failure.stderr ?? ''}`;
  }
}

async function assertDefect(name: Defect, prepare: (reporter: Reporter) => Promise<void>, gateError: RegExp): Promise<void> {
  const runId = `probe-${name.replaceAll(' ', '-')}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const reporter = await reporterFor(runId);
  await prepare(reporter);
  await reporter.onEnd({ status: 'passed' });
  const results = resultPath(runId);
  const emitted = JSON.parse(await readFile(results, 'utf8'));
  assert.equal(emitted.summary.status, 'failed');
  assert.match(emitted.summary.errors.join('\n'), new RegExp(name));
  assert.match(runGate(results, runId), gateError);
  await rm(dirname(dirname(results)), { recursive: true, force: true });
}

test('missing record', async () => {
  await assertDefect('missing record', async (reporter) => { reporter.onBegin({}); }, /missing_check_ids is not empty/);
});

test('duplicate', async () => {
  await assertDefect('duplicate', async (reporter) => { await normalRecord(reporter); await normalRecord(reporter); }, /duplicate record/);
});

test('mismatched title', async () => {
  await assertDefect('mismatched title', async (reporter) => { await normalRecord(reporter); reporter.checks[0].spec_title = 'wrong title'; }, /spec_title/);
});

test('empty WebP', async () => {
  await assertDefect('empty WebP', async (reporter) => { await normalRecord(reporter, false); }, /no screenshot evidence/);
});

test('parser error', async () => {
  const runId = `probe-parser-error-${Date.now()}`;
  const fixture = await parserFailureReporter(runId);
  fixture.reporter.onBegin({});
  await fixture.reporter.onEnd({ status: 'passed' });
  const emitted = JSON.parse(await readFile(fixture.results, 'utf8'));
  assert.equal(emitted.summary.status, 'failed');
  assert.match(emitted.summary.errors.join('\n'), /parser error/);
  assert.match(runGate(fixture.results, runId), /observed_check_ids do not account/);
  await fixture.cleanup();
});
test('reporter error', async () => {
  await assertDefect('reporter error', async (reporter) => { reporter.onBegin({}); reporter.onTestEnd({ title: 'unknown', parent: { project: () => ({ name: 'desktop-1440' }) } }, { status: 'passed', attachments: [], errors: [] }); }, /missing_check_ids is not empty/);
});

test('incomplete accounting', async () => {
  await assertDefect('incomplete accounting', async (reporter) => { await normalRecord(reporter); reporter.checks[0].screenshots = []; }, /no screenshot evidence/);
  await assertInspectionSetupFailure();
});
