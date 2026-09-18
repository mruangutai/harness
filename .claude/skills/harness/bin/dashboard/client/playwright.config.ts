import { defineConfig } from '@playwright/test';
import { prepareFixtureSync } from './fixture.js';

const fixture = prepareFixtureSync();

export default defineConfig({
  testMatch: 'feat-53.e2e.spec.ts',
  outputDir: 'test-results/playwright-artifacts',
  reporter: [['list'], ['./ui-reporter.ts']],
  use: {
    baseURL: 'http://127.0.0.1:8972',
    locale: 'en-US',
    timezoneId: 'UTC',
    colorScheme: 'dark',
    reducedMotion: 'reduce',
    deviceScaleFactor: 1,
  },
  projects: [
    { name: 'desktop-1440', use: { viewport: { width: 1440, height: 1100 } } },
    { name: 'desktop-1920', grepInvert: /component source uses only theme tokens/, use: { viewport: { width: 1920, height: 1100 } } },
  ],
  webServer: {
    command: `python3 ../serve.py --root ${fixture} --port 8972`,
    port: 8972,
    reuseExistingServer: false,
  },
});
