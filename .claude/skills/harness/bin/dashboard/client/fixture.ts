import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const client = resolve(fileURLToPath(new URL('.', import.meta.url)));
const dashboard = resolve(client, '..');
const fixtureBase = resolve(client, 'test-results', 'fixtures');
const sourceFeature = resolve(dashboard, 'fixtures', 'project-a', '.harness', 'demo', 'features', 'FIX-SHIPPED');
const states = [
  ['FEAT-53', 'default loaded dashboard', 'feature'],
  ['FEAT-53-ATTENTION', 'attention', 'feature'],
  ['FEAT-53-GRILLING', 'grilling', 'grilling'],
  ['FEAT-53-WORKTREE', 'worktree', 'worktree'],
  ['FEAT-53-UNAVAILABLE', 'unavailable-kpis', 'feature'],
  ['FEAT-53-FILTERED-ZERO', 'filtered-zero', 'bug'],
  ['FEAT-53-SOURCE-ERROR', 'source-errors', 'feature'],
  ['FEAT-53-INITIAL-ERROR', 'initial-error', 'feature'],
  ['FEAT-53-REFRESH-ERROR', 'refresh-error', 'feature'],
  ['FEAT-53-OVERFLOW', 'overflow', 'feature'],
  ['FEAT-53-LONG-CONTENT', 'long-content', 'feature'],
] as const;

export function fixturePath(runId = process.env.HARNESS_UI_RUN_ID ?? 'local'): string {
  if (!/^[A-Za-z0-9_-]+$/.test(runId)) throw new Error(`invalid UI fixture run id: ${runId}`);
  return resolve(fixtureBase, runId);
}

function materializeState(destination: string, id: string, state: string, kind: string): void {
  const unavailable = state === 'unavailable-kpis';
  const requestError = state === 'initial-error' || state === 'refresh-error';
  const source = JSON.parse(readFileSync(resolve(destination, 'feature.json'), 'utf8')) as Record<string, unknown>;
  writeFileSync(resolve(destination, 'feature.json'), JSON.stringify({
    ...source,
    feature_id: id,
    branch: `fixture/${state}`,
    fixture_state: state,
    fixture: {
      deterministic_clock: '2026-09-17T12:00:00Z',
      unavailable,
      unavailable_reason: unavailable ? 'KPI 3 has no measurement for the selected window.' : null,
      zero_match_filter: state === 'filtered-zero',
      source_error: state === 'source-errors' ? 'fixture source failed while valid rows remain' : null,
      request_error: requestError ? `${state} fixture request failure` : null,
      overflow: state === 'overflow',
      long_content: state === 'long-content',
    },
    runs: [{ id: `fixture-${state}`, squad: kind, verdict: requestError ? 'FAIL' : 'PASS' }],
  }, null, 2));
  writeFileSync(resolve(destination, 'plan.yaml'), `fixture_state: ${state}\n`);
  if (state === 'attention') writeFileSync(resolve(destination, 'STATE.md'), '## Open Questions\n- operator decision required\n');
  writeFileSync(resolve(destination, 'touchpoints.jsonl'), JSON.stringify({
    feature_id: id, state, kind, reason: state === 'long-content' ? 'A deliberately long operational fixture record that must wrap without page overflow.' : `${state} deterministic fixture`,
  }) + '\n');
}

export function prepareFixtureSync(runId = process.env.HARNESS_UI_RUN_ID ?? 'local'): string {
  const fixtureRoot = fixturePath(runId);
  const fixtureFeatures = resolve(fixtureRoot, '.harness', 'harness', 'features');
  rmSync(fixtureRoot, { force: true, recursive: true });
  cpSync(resolve(dashboard, 'fixtures', 'project-a'), fixtureRoot, { recursive: true });
  mkdirSync(resolve(fixtureRoot, '.harness', 'metrics'), { recursive: true });
  cpSync(resolve(client, '..', '..', '..', '..', '..', '..', '.harness', 'harness.json'), resolve(fixtureRoot, '.harness', 'harness.json'));
  mkdirSync(fixtureFeatures, { recursive: true });
  for (const [id, state, kind] of states) {
    const destination = resolve(fixtureFeatures, id);
    cpSync(sourceFeature, destination, { recursive: true });
    materializeState(destination, id, state, kind);
  }
  const notes = resolve(fixtureRoot, '.harness', 'notes');
  mkdirSync(notes, { recursive: true });
  writeFileSync(resolve(notes, 'grilling-Grilling.md'), '---\nstatus: open\nbecame: null\n---\n# Grilling\n');
  initializeFixtureRepository(fixtureRoot);
  return fixtureRoot;
}

function initializeFixtureRepository(fixtureRoot: string): void {
  const environment = {
    ...process.env,
    GIT_AUTHOR_NAME: 'Harness Fixture',
    GIT_AUTHOR_EMAIL: 'fixture@harness.test',
    GIT_AUTHOR_DATE: '2026-09-17T12:00:00Z',
    GIT_COMMITTER_NAME: 'Harness Fixture',
    GIT_COMMITTER_EMAIL: 'fixture@harness.test',
    GIT_COMMITTER_DATE: '2026-09-17T12:00:00Z',
  };
  execFileSync('git', ['init', '--quiet'], { cwd: fixtureRoot, env: environment });
  execFileSync('git', ['add', '.'], { cwd: fixtureRoot, env: environment });
  execFileSync('git', ['commit', '--quiet', '--message', 'fixture'], { cwd: fixtureRoot, env: environment });
  execFileSync('git', ['worktree', 'add', '--detach', resolve(fixtureRoot, 'Worktree')], { cwd: fixtureRoot, env: environment });
}

export default function globalSetup(): void {
  prepareFixtureSync();
}
