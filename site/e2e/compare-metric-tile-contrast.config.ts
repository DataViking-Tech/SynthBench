import { defineConfig, devices } from "@playwright/test";

// sb-3ie — functional test for /compare metric-tile label contrast in dark
// mode. Mirrors run-aggregate-scores-contrast.config.ts (one config per spec).
export default defineConfig({
  testDir: ".",
  testMatch: "compare-metric-tile-contrast.spec.ts",
  outputDir: "./test-results-compare-metric-tile-contrast",
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://localhost:4321/synthbench/",
  },
  projects: [
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"], colorScheme: "dark" },
    },
  ],
  webServer: {
    command: "npm run preview",
    port: 4321,
    reuseExistingServer: !process.env.CI,
    cwd: "..",
  },
});
