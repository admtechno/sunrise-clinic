// Sessions 12 and 13: the browser tests. Playwright starts the API (settings
// config.settings.e2e and the database m9_e2e) and the Vite server, opens
// Chromium, and runs the tests in e2e/ one after the other.
import { defineConfig, devices } from "@playwright/test";

// where the Django API is, from this folder
export const API_DIR = process.env.API_DIR ?? "../api";

export default defineConfig({
  testDir: "e2e",
  workers: 1, // one database for every test: never two tests at once
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI), // a test.only left behind fails the run in CI
  retries: process.env.CI ? 2 : 0, // Session 13: a second chance in CI only
  // the list in the terminal, and an HTML report (npx playwright show-report)
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "retain-on-failure", // a trace of each failed test (Session 13)
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "python manage.py runserver 127.0.0.1:8000 --noreload",
      cwd: API_DIR,
      env: {
        DJANGO_SETTINGS_MODULE: "config.settings.e2e",
        // Session 13: a short token life for the expiry test (else 300 s)
        JWT_ACCESS_SECONDS: process.env.JWT_ACCESS_SECONDS ?? "300",
      },
      url: "http://127.0.0.1:8000/api/v1/",
      stderr: "ignore", // Django's request log; "pipe" shows it in the report
      reuseExistingServer: false, // an API you started yourself uses YOUR database
      timeout: 60_000,
    },
    {
      // Session 14: E2E_PREVIEW=1 runs every test against the BUILT app
      command: process.env.E2E_PREVIEW
        ? "npm run build && npm run preview -- --port 5173"
        : "npm run dev -- --host 127.0.0.1 --port 5173 --strictPort",
      url: "http://127.0.0.1:5173/",
      reuseExistingServer: false,
      timeout: 120_000, // a build first takes longer
    },
  ],
});
