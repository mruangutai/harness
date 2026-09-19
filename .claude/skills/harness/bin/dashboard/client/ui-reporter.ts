import type { FullConfig, FullResult, Reporter, TestCase, TestResult } from '@playwright/test/reporter';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { copyFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { loadManifest, type InspectionEvidence, type UiManifest, type UiResultRecord } from './ui-manifest.ts';

const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const output = resolve(root, `.harness/harness/features/${feature}/runs/${runId}/ui/results.json`);
type Evidence = { path: string; route: string; fixture_state: string; interaction: string; evidence_label: string };
type TracePublication = { source: string; destination: string };

function evidenceRows(manifest: UiManifest, checkId: string, project: string): InspectionEvidence[] {
  return manifest.inspection_evidence.filter((entry) => entry.check_id === checkId && entry.project === project);
}

function expectedLabels(manifest: UiManifest, checkId: string, project: string): string[] {
  const rows = evidenceRows(manifest, checkId, project);
  return rows.length === 0 ? ['execution'] : rows.map((row) => row.evidence_label);
}

function webp(path: string): boolean {
  try {
    const bytes = readFileSync(path);
    return bytes.length > 12 && bytes.subarray(0, 4).toString() === 'RIFF' && bytes.subarray(8, 12).toString() === 'WEBP';
  } catch {
    return false;
  }
}

function traceProblem(path: string | undefined): 'empty' | 'non-ZIP' | null {
  if (!path) return 'empty';
  try {
    const bytes = readFileSync(path);
    if (bytes.length === 0) return 'empty';
    const firstEocd = Math.max(0, bytes.length - 65_557);
    for (let index = bytes.length - 22; index >= firstEocd; index -= 1) {
      if (bytes.subarray(index, index + 4).toString() === 'PK\u0005\u0006' && index + 22 + bytes.readUInt16LE(index + 20) === bytes.length) return null;
    }
    return 'non-ZIP';
  } catch {
    return 'empty';
  }
}

function traceDestination(checkId: string, project: string): string {
  return `.harness/harness/features/${feature}/runs/${runId}/ui/traces/${checkId}--${project}.zip`;
}

export default class UiReporter implements Reporter {
  private manifest?: UiManifest;
  private checks: UiResultRecord[] = [];
  private reporterErrors: string[] = [];
  private tracePublications: TracePublication[] = [];

  onBegin(_config: FullConfig): void {
    try { this.manifest = loadManifest(); }
    catch (error) { this.reporterErrors.push(`parser error: ${error instanceof Error ? error.message : String(error)}`); }
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    const project = test.parent.project()?.name;
    if (!this.manifest || !project) {
      this.reporterErrors.push(`reporter error: cannot map test result: ${project ?? 'unknown project'} / ${test.title}`);
      return;
    }
    const contract = this.manifest.checks.find((check) => check.spec_title === test.title);
    if (!contract) {
      this.reporterErrors.push(`reporter error: unlisted test result: ${project} / ${test.title}`);
      return;
    }
    if (!contract.applicable_projects.includes(project)) {
      this.reporterErrors.push(`mismatched project result for ${project}/${contract.check_id}`);
      return;
    }
    const expected = expectedLabels(this.manifest, contract.check_id, project);
    const attachments = result.attachments.filter((attachment) => attachment.name.startsWith(`evidence:${contract.check_id}:`));
    const labels = attachments.map((attachment) => attachment.name.slice(`evidence:${contract.check_id}:`.length));
    const exact = labels.length === expected.length && new Set(labels).size === labels.length && expected.every((label) => labels.includes(label));
    if (!exact) this.reporterErrors.push(`evidence labels mismatch for ${project}/${contract.check_id}: expected ${expected.join(',')} observed ${labels.join(',')}`);
    const screenshots = attachments.map((attachment): Evidence | null => {
      const label = attachment.name.slice(`evidence:${contract.check_id}:`.length);
      const row = evidenceRows(this.manifest!, contract.check_id, project).find((entry) => entry.evidence_label === label);
      if (!attachment.path || !webp(attachment.path) || !expected.includes(label)) {
        this.reporterErrors.push(`empty WebP evidence for ${project}/${contract.check_id}/${label}`);
        return null;
      }
      return {
        path: `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${project}/${contract.check_id}--${label}.webp`,
        route: row?.route ?? '/',
        fixture_state: row?.fixture_state ?? 'default loaded dashboard',
        interaction: row?.setup ?? 'automated predicate execution',
        evidence_label: label,
      };
    }).filter((evidence): evidence is Evidence => evidence !== null);
    const traceAttachments = result.attachments.filter((attachment) => attachment.name === 'trace');
    const namedTraceAttachments = result.attachments.filter((attachment) => attachment.name.startsWith('trace:'));
    let trace: string | undefined;
    if (this.manifest.traced_check_ids.includes(contract.check_id)) {
      for (const attachment of namedTraceAttachments) {
        const [, attachedCheck, attachedProject] = attachment.name.split(':');
        if (attachedCheck !== contract.check_id) this.reporterErrors.push(`mismatched trace check for ${project}/${contract.check_id}: ${attachment.name}`);
        else if (attachedProject !== project) this.reporterErrors.push(`mismatched trace project for ${project}/${contract.check_id}: ${attachment.name}`);
        else this.reporterErrors.push(`named trace attachment is not Playwright trace for ${project}/${contract.check_id}: ${attachment.name}`);
      }
      if (traceAttachments.length === 0) this.reporterErrors.push(`missing trace for ${project}/${contract.check_id}`);
      else if (traceAttachments.length !== 1) this.reporterErrors.push(`duplicate trace for ${project}/${contract.check_id}`);
      else {
        const path = traceAttachments[0].path;
        const problem = traceProblem(path);
        if (problem) this.reporterErrors.push(`${problem} trace for ${project}/${contract.check_id}`);
        else {
          trace = traceDestination(contract.check_id, project);
          this.tracePublications.push({ source: path!, destination: trace });
        }
      }
    }
    this.checks.push({ check_id: contract.check_id, spec_title: contract.spec_title, method: contract.method, surface: contract.surface, project, status: contract.method.startsWith('inspection') ? 'evidence' : result.status === 'passed' ? 'passed' : 'failed', screenshots, errors: result.errors.map((error) => error.message), ...(trace ? { trace } : {}) });
  }

  async onEnd(result: FullResult): Promise<void> {
    const manifest = this.manifest;
    const projects = manifest?.projects ?? ['desktop-1440', 'desktop-1920'];
    const applicable = manifest?.applicable ?? Object.fromEntries(projects.map((project) => [project, []]));
    const observed = [...new Set(this.checks.map((check) => check.check_id))];
    const missing = manifest?.listed_check_ids.filter((id) => !observed.includes(id)) ?? [];
    const duplicate = this.checks.some((check, index) => this.checks.findIndex((other) => other.check_id === check.check_id && other.project === check.project) !== index);
    const titleMismatch = this.checks.some((check) => manifest?.checks.find((contract) => contract.check_id === check.check_id)?.spec_title !== check.spec_title);
    const incomplete = missing.length > 0 || this.checks.some((check) => !check.screenshots.length || (manifest?.traced_check_ids.includes(check.check_id) && !check.trace));
    if (missing.length) this.reporterErrors.push(`missing record: ${missing.join(',')}`);
    if (duplicate) this.reporterErrors.push('duplicate record');
    if (titleMismatch) this.reporterErrors.push('mismatched title');
    if (incomplete) this.reporterErrors.push('incomplete accounting');
    if (this.reporterErrors.length === 0) {
      await Promise.all(this.tracePublications.map(async ({ source, destination }) => {
        const path = resolve(root, destination);
        await mkdir(resolve(path, '..'), { recursive: true });
        await copyFile(source, path);
      }));
    }
    const failed = result.status !== 'passed' || this.reporterErrors.length > 0 || this.checks.some((check) => check.status === 'failed' || check.errors.length > 0);
    await mkdir(resolve(output, '..'), { recursive: true });
    await writeFile(output, JSON.stringify({ schema: 'harness-ui-results/1', feature, run_id: runId, design: '.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md', served_bundle_commit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(), projects: { 'desktop-1440': { viewport: { width: 1440, height: 1100 } }, 'desktop-1920': { viewport: { width: 1920, height: 1100 } } }, listed_check_ids: manifest?.listed_check_ids ?? [], applicable_check_ids: applicable, observed_check_ids: observed, missing_check_ids: missing, checks: this.checks, summary: { status: failed ? 'failed' : 'passed', check_count: this.checks.length, errors: this.reporterErrors } }, null, 2));
  }
}
