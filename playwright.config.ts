import { defineConfig } from '@playwright/test';

const hasBaseUrl = Boolean(process.env.BASE_URL);

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:8000',
    trace: 'on-first-retry',
  },
  webServer: hasBaseUrl
    ? undefined
    : {
        command: 'cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000',
        url: 'http://127.0.0.1:8000/api/v1/health',
        reuseExistingServer: true,
        timeout: 120000,
      },
});
