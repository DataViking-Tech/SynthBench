import { expect, test } from "@playwright/test";

test.describe("Chart Visual Regression", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Wait for ECharts to render
    await page.waitForSelector(".echarts-container canvas, .echarts-container svg", {
      timeout: 10000,
    });
    // Extra time for chart animations to settle
    await page.waitForTimeout(500);
  });

  test("hero chart renders", async ({ page }) => {
    const hero = page.locator("section").filter({ hasText: "Best Model vs Random Baseline" });
    await expect(hero).toBeVisible();
    await expect(hero).toHaveScreenshot("hero-chart.png");
  });

  test("SPS dot plot renders", async ({ page }) => {
    const chart = page.locator("section").filter({ hasText: "SPS by Model" });
    await expect(chart).toBeVisible();
    await expect(chart).toHaveScreenshot("dot-plot.png");
  });

  test("per-metric breakdown renders", async ({ page }) => {
    const chart = page.locator("section").filter({ hasText: "Per-Metric Breakdown" });
    await expect(chart).toBeVisible();
    await expect(chart).toHaveScreenshot("per-metric-dot.png");
  });

  test("convergence line chart renders", async ({ page }) => {
    const chart = page.locator("section").filter({ hasText: "SPS Convergence" });
    await expect(chart).toBeVisible();
    await expect(chart).toHaveScreenshot("convergence-line.png");
  });

  test("topic grouped bar chart renders", async ({ page }) => {
    const chart = page.locator("section").filter({ hasText: "SPS by Topic" });
    await expect(chart).toBeVisible();
    await expect(chart).toHaveScreenshot("topic-grouped-bar.png");
  });

  test("CI whisker plot renders", async ({ page }) => {
    const chart = page.locator("section").filter({ hasText: "Confidence Intervals" });
    await expect(chart).toBeVisible();
    await expect(chart).toHaveScreenshot("whisker-plot.png");
  });
});

test.describe("Leaderboard Table Visual Regression", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector("#leaderboard");
  });

  test("leaderboard table default view", async ({ page }) => {
    const table = page.locator("#leaderboard");
    await expect(table).toBeVisible();
    await expect(table).toHaveScreenshot("leaderboard-default.png");
  });

  test("leaderboard table expanded row", async ({ page }) => {
    // Click first data row to expand
    const firstRow = page.locator("#leaderboard-table tbody tr[data-entry]").first();
    await firstRow.click();
    await page.waitForTimeout(200);
    const table = page.locator("#leaderboard");
    await expect(table).toHaveScreenshot("leaderboard-expanded.png");
  });
});

test.describe("Full Page Visual Regression", () => {
  test("full page light theme", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "light" });
    await page.goto("/");
    await page.waitForSelector(".echarts-container canvas, .echarts-container svg", {
      timeout: 10000,
    });
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot("full-page-light.png", {
      fullPage: true,
    });
  });

  test("full page dark theme", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto("/");
    await page.waitForSelector(".echarts-container canvas, .echarts-container svg", {
      timeout: 10000,
    });
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot("full-page-dark.png", {
      fullPage: true,
    });
  });
});
