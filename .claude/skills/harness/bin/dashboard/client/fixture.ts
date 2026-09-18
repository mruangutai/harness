import { cpSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const client = resolve(fileURLToPath(new URL('.', import.meta.url)));
const dashboard = resolve(client, '..');
const fixtureRoot = resolve(client, 'test-results', 'fixture-project-a');
const fixtureFeatures = resolve(fixtureRoot, '.harness', 'harness', 'features');
const sourceFeature = resolve(dashboard, 'fixtures', 'project-a', '.harness', 'demo', 'features', 'FIX-SHIPPED');
const states = [
  ['FEAT-53', 'default loaded dashboard', 'feature'], ['FEAT-53-ATTENTION', 'attention', 'feature'], ['FEAT-53-GRILLING', 'grilling', 'grilling'], ['FEAT-53-WORKTREE', 'worktree', 'worktree'], ['FEAT-53-UNAVAILABLE', 'unavailable-kpis', 'feature'], ['FEAT-53-FILTERED-ZERO', 'filtered-zero', 'bug'], ['FEAT-53-SOURCE-ERROR', 'source-errors', 'feature'], ['FEAT-53-INITIAL-ERROR', 'initial-error', 'feature'], ['FEAT-53-REFRESH-ERROR', 'refresh-error', 'feature'], ['FEAT-53-OVERFLOW', 'overflow', 'feature'], ['FEAT-53-LONG-CONTENT', 'long-content', 'feature'],
] as const;

export function prepareFixtureSync(): string {
  rmSync(fixtureRoot, { force: true, recursive: true });
  cpSync(resolve(dashboard, 'fixtures', 'project-a'), fixtureRoot, { recursive: true });
  mkdirSync(resolve(fixtureRoot, '.harness'), { recursive: true });
  cpSync(resolve(client, '..', '..', '..', '..', '..', '..', '.harness', 'harness.json'), resolve(fixtureRoot, '.harness', 'harness.json'));
  mkdirSync(fixtureFeatures, { recursive: true });
  for (const [id, state, kind] of states) {
    const destination = resolve(fixtureFeatures, id);
    cpSync(sourceFeature, destination, { recursive: true });
    writeFileSync(resolve(destination, 'feature.json'), JSON.stringify({ feature_id: id, branch: `fixture/${state}`, runs: [{ id: `fixture-${state}`, squad: kind, verdict: state === 'initial-error' || state === 'refresh-error' ? 'FAIL' : 'PASS' }], fixture_state: state, source_path: `.harness/harness/features/${id}` }, null, 2));
    writeFileSync(resolve(destination, 'fixture-state.json'), JSON.stringify({ state, deterministic_clock: '2026-09-17T12:00:00Z', unavailable: state === 'unavailable-kpis', zero_match_filter: state === 'filtered-zero', source_error: state === 'source-errors', request_error: state.endsWith('error'), overflow: state === 'overflow', long_content: state === 'long-content' }, null, 2));
  }
  writeFileSync(resolve(fixtureRoot, '.harness', 'metrics', 'fixture-states.json'), JSON.stringify(Object.fromEntries(states.map(([id, state]) => [id, state])), null, 2));
  return fixtureRoot;
}
