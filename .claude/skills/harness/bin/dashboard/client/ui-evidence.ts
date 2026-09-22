import { type Page, type TestInfo } from '@playwright/test';
import { access, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { UiCheck } from './ui-manifest.js';

const root = resolve(import.meta.dirname, '..', '..', '..', '..', '..', '..');
const feature = process.env.HARNESS_UI_FEATURE ?? 'FEAT-53-metrics-dashboard';
const runId = process.env.HARNESS_UI_RUN_ID ?? 'local';

export async function captureHardFailureEvidence(page: Page, testInfo: TestInfo, check: UiCheck, evidenceLabel: string): Promise<void> {
  await page.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}' });
  const session = await page.context().newCDPSession(page);
  const shot = await session.send('Page.captureScreenshot', { format: 'webp', captureBeyondViewport: true });
  if (!shot.data) throw new Error('Page.captureScreenshot returned empty WebP evidence');
  const relative = `.harness/harness/features/${feature}/runs/${runId}/ui/evidence/${testInfo.project.name}/${check.check_id}--${evidenceLabel}.webp`;
  const path = resolve(root, relative);
  await mkdir(resolve(path, '..'), { recursive: true });
  try {
    await access(path);
    throw new Error(`duplicate screenshot evidence label: ${testInfo.project.name}/${check.check_id}/${evidenceLabel}`);
  } catch (error) {
    if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error;
  }
  const bytes = Buffer.from(shot.data, 'base64');
  if (bytes.length <= 12 || bytes.subarray(0, 4).toString() !== 'RIFF' || bytes.subarray(8, 12).toString() !== 'WEBP') throw new Error('Page.captureScreenshot did not return nonempty WebP evidence');
  await writeFile(path, bytes);
  await testInfo.attach(`evidence:${check.check_id}:${evidenceLabel}`, { path, contentType: 'image/webp' });
}
