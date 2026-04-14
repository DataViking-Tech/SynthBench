import { test } from "@playwright/test";

// Captures full-page screenshots at 375px for visual review.
// Not a regression suite — intentionally not using toHaveScreenshot.

const SAMPLE_CONFIG = "synthpanel--claude-haiku-4-5--t0.85--tplcurrent--4a453653";
const SAMPLE_RUN = "subpop_random-baseline_20260411_044250";

const ROUTES = [
  { path: "./", name: "index" },
  { path: "./leaderboard/", name: "leaderboard" },
  { path: "./explore/", name: "explore" },
  { path: "./compare/", name: "compare" },
  { path: "./findings/", name: "findings" },
  { path: "./methodology/", name: "methodology" },
  { path: "./submit/", name: "submit" },
  { path: `./config/${SAMPLE_CONFIG}/`, name: "config-detail" },
  { path: `./run/${encodeURIComponent(SAMPLE_RUN)}/`, name: "run-detail" },
];

test.describe("Mobile screenshots @ 375px", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  for (const route of ROUTES) {
    test(`${route.name}`, async ({ page }) => {
      await page.goto(route.path, { waitUntil: "networkidle" });
      await page.waitForTimeout(800);
      await page.screenshot({
        path: `e2e/mobile-screenshots/${route.name}-375.png`,
        fullPage: true,
      });
    });
  }

  test("compare-populated", async ({ page }) => {
    // With comparison pre-populated via query param
    await page.goto(
      `./compare/?a=${SAMPLE_CONFIG}&b=synthpanel--claude-haiku-4-5--t0.3--tplcurrent--b530ccc6`,
      { waitUntil: "networkidle" },
    );
    await page.waitForTimeout(800);
    await page.screenshot({
      path: "e2e/mobile-screenshots/compare-populated-375.png",
      fullPage: true,
    });
  });

  test("leaderboard-expanded", async ({ page }) => {
    await page.goto("./leaderboard/");
    await page.waitForTimeout(400);
    const card = page.locator(".leaderboard-card[data-entry]").first();
    await card.click();
    await page.waitForTimeout(300);
    await page.screenshot({
      path: "e2e/mobile-screenshots/leaderboard-expanded-375.png",
      fullPage: true,
    });
  });

  test("nav-menu-open", async ({ page }) => {
    await page.goto("./");
    await page.waitForTimeout(200);
    await page.click("#mobile-menu-open");
    await page.waitForTimeout(200);
    await page.screenshot({
      path: "e2e/mobile-screenshots/nav-menu-open-375.png",
    });
  });
});
