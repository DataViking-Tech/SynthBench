import { defineConfig, devices } from "@playwright/test";

// sb-u74 Pass 4.1 — VRT for Storybook stories.
// Runs Playwright against a pre-built storybook-static/ served by http-server.
// Shares the route-VRT snapshot-path convention so macOS dev vs Linux CI baselines
// coexist without collision.

export default defineConfig({
  testDir: "./visual",
  testMatch: "storybook.visual.spec.ts",
  outputDir: "./test-results-storybook",
  snapshotPathTemplate:
    "{testDir}/__screenshots__/{testFilePath}/{platform}/{projectName}/{arg}{ext}",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:6007",
    screenshot: "only-on-failure",
  },
  expect: {
    toHaveScreenshot: {
      animations: "disabled",
      maxDiffPixelRatio: 0.01,
    },
  },
  projects: [
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npx http-server storybook-static -p 6007 --silent",
    port: 6007,
    reuseExistingServer: !process.env.CI,
    cwd: "..",
    timeout: 30000,
  },
});
