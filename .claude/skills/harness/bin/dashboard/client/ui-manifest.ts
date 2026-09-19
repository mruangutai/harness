import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';

export type UiCheck = { check_id: string; spec_title: string; surface: string; method: string; applicable_projects: string[] };
export type InspectionEvidence = { check_id: string; evidence_label: string; route: string; fixture_state: string; setup: string; project: string };
export type UiManifest = { schema: 'harness-ui-manifest/1'; design: string; projects: string[]; checks: UiCheck[]; inspection_evidence: InspectionEvidence[]; traced_check_ids: string[]; listed_check_ids: string[]; applicable: Record<string, string[]> };
export type UiResultRecord = { check_id: string; spec_title: string; method: string; surface: string; project: string; status: 'passed' | 'failed' | 'evidence'; screenshots: { path: string; route: string; fixture_state: string; interaction: string; evidence_label: string }[]; errors: string[]; trace?: string };

const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const design = resolve(root, '.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md');
const parser = resolve(root, '.claude/skills/harness/bin/ui_contract.py');

export function loadManifest(): UiManifest {
  const output = execFileSync('python3', [parser, 'check', '--design', design, '--require-predicates', '--require-inspection-evidence'], { encoding: 'utf8' });
  const manifest = JSON.parse(output) as UiManifest;
  if (manifest.schema !== 'harness-ui-manifest/1' || manifest.checks.length !== 12) throw new Error('ui_contract.py returned an invalid normalized manifest');
  return manifest;
}

export function checkFor(manifest: UiManifest, title: string): UiCheck {
  const check = manifest.checks.find((candidate) => candidate.spec_title === title);
  if (!check) throw new Error(`missing manifest check: ${title}`);
  return check;
}
