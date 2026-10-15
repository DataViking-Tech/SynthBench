import { defineConfig, devices } from "@playwright/test";

// Horizontal-overflow regression guard (mobile-audit.spec.ts). Runs against
// `npm run preview` of a default build (base /synthbench/). Point it at
// another server with E2E_BASE_URL, e.g. a dev server started with
// BASE_PATH=/:  E2E_BASE_URL=http://localhost:4321/ npx playwright test -c e2e/mobile-audit.config.ts
const baseURL = process.env.E2E_BASE_URL ?? "http://localhost:4321/synthbench/";

export default defineConfig({
  testDir: ".",
  testMatch: "mobile-audit.spec.ts",
  outputDir: "./test-results-mobile-audit",
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: { baseURL },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: "npm run preview",
        port: 4321,
        reuseExistingServer: !process.env.CI,
        cwd: "..",
      },
});
