import type { FullConfig, FullResult, Reporter, TestCase, TestResult } from '@playwright/test/reporter';
import { execFileSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { loadManifest, type UiManifest } from './ui-manifest.js';

const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const output = resolve(root, `.harness/harness/features/${feature}/runs/${runId}/ui/results.json`);

type CheckResult = { check_id: string; spec_title: string; method: string; surface: string; project: string; status: 'passed' | 'failed' | 'evidence'; screenshot_evidence: unknown[]; errors: string[] };

export default class UiReporter implements Reporter {
  private manifest!: UiManifest;
  private checks: CheckResult[] = [];
  private reporterErrors: string[] = [];
  onBegin(_config: FullConfig): void { this.manifest = loadManifest(); }

  onTestEnd(test: TestCase, result: TestResult): void {
    const project = test.parent.project()?.name;
    const specTitle = test.title;
    const contract = this.manifest.checks.find((check) => check.spec_title === specTitle);
    if (!contract || !project) {
      this.reporterErrors.push(`unlisted test result: ${project ?? 'unknown project'} / ${specTitle}`);
      return;
    }
    const screenshots = result.attachments.filter((attachment) => attachment.name.startsWith('evidence:')).map((attachment) => {
      const evidenceLabel = attachment.name.split(':').at(-1) ?? 'execution';
      const evidence = this.manifest.inspection_evidence.find((entry) => entry.check_id === contract.check_id && entry.project === project && entry.evidence_label === evidenceLabel);
      return evidence ? { path: `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${project}/${contract.check_id}--${evidenceLabel}.webp`, route: evidence.route, fixture_state: evidence.fixture_state, interaction: evidence.setup, evidence_label: evidenceLabel } : { path: `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${project}/${contract.check_id}--${evidenceLabel}.webp`, route: '/', fixture_state: 'default loaded dashboard', interaction: 'automated predicate execution', evidence_label: evidenceLabel };
    });
    this.checks.push({ check_id: contract.check_id, spec_title: contract.spec_title, method: contract.method, surface: contract.surface, project, status: result.status === 'passed' ? (contract.method.startsWith('inspection') ? 'evidence' : 'passed') : 'failed', screenshot_evidence: screenshots, errors: result.errors.map((error) => error.message) });
  }

  async onEnd(result: FullResult): Promise<void> {
    const observed = Object.fromEntries(this.manifest.projects.map((project) => [project, this.checks.filter((check) => check.project === project).map((check) => check.check_id)]));
    const missing = Object.fromEntries(this.manifest.projects.map((project) => [project, this.manifest.applicable[project].filter((id) => !observed[project].includes(id))]));
    const invalidEvidence = this.checks.some((check) => check.screenshot_evidence.length === 0);
    const duplicate = this.checks.some((check, index) => this.checks.findIndex((other) => other.check_id === check.check_id && other.project === check.project) !== index);
    const titleMismatch = this.checks.some((check) => this.manifest.checks.find((contract) => contract.check_id === check.check_id)?.spec_title !== check.spec_title);
    const failed = result.status !== 'passed' || this.reporterErrors.length > 0 || invalidEvidence || duplicate || titleMismatch || Object.values(missing).some((ids) => ids.length > 0);
    await mkdir(resolve(output, '..'), { recursive: true });
    await writeFile(output, JSON.stringify({ schema: 'harness-ui-results/1', feature, run_id: runId, design: '.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md', served_bundle_commit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(), projects: { 'desktop-1440': { viewport: { width: 1440, height: 1100 } }, 'desktop-1920': { viewport: { width: 1920, height: 1100 } } }, listed_check_ids: this.manifest.listed_check_ids, applicable_check_ids: this.manifest.applicable, observed_check_ids: observed, missing_check_ids: missing, checks: this.checks, summary: { status: failed ? 'failed' : 'passed', check_count: this.checks.length, errors: this.reporterErrors } }, null, 2));
  }
}
