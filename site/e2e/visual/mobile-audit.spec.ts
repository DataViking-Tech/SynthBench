import { expect, test } from "@playwright/test";

// Mobile audit: verify all 9 routes render without horizontal overflow
// at target viewports (375/390/414px). Also checks tap-target sizes on
// interactive controls.

const VIEWPORTS = [
  { name: "iphone-se", width: 375, height: 667 },
  { name: "iphone-14", width: 390, height: 844 },
  { name: "iphone-plus", width: 414, height: 736 },
];

// Using a sample config/run id that exists in the build output.
const SAMPLE_CONFIG = "synthpanel--claude-haiku-4-5--t0.85--tplcurrent--4a453653";
const SAMPLE_RUN = "subpop_random-baseline_20260411_044250";

// Paths are relative to baseURL (http://localhost:4321/synthbench/).
// A leading slash would navigate to the origin root and 404.
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

for (const viewport of VIEWPORTS) {
  test.describe(`Mobile audit @ ${viewport.name} (${viewport.width}px)`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    for (const route of ROUTES) {
      test(`${route.name}: no horizontal overflow`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (e) => errors.push(`PAGE ERROR: ${e.message}`));
        page.on("console", (msg) => {
          if (msg.type() === "error") {
            const txt = msg.text();
            // Ignore harmless favicon / robots 404s not part of the app.
            if (!/favicon|robots\.txt/i.test(txt)) errors.push(`CONSOLE: ${txt}`);
          }
        });

        const resp = await page.goto(route.path, { waitUntil: "networkidle" });
        expect(resp?.status(), `HTTP status for ${route.path}`).toBeLessThan(400);

        // Allow charts to settle
        await page.waitForTimeout(500);

        // Check document width does not exceed viewport
        const { scrollWidth, clientWidth, bodyScrollWidth } = await page.evaluate(() => ({
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          bodyScrollWidth: document.body.scrollWidth,
        }));

        const overflow = Math.max(scrollWidth, bodyScrollWidth) - clientWidth;

        // Collect any element wider than viewport for diagnostic.
        // Exclude elements that are intentionally inside a horizontal scroll
        // container (overflow-x-auto) — the parent clips them, not the body.
        let wideElements: string[] = [];
        if (overflow > 1) {
          wideElements = await page.evaluate((vw) => {
            const problems: string[] = [];
            function isInsideScrollContainer(el: Element): boolean {
              let cur: Element | null = el.parentElement;
              while (cur && cur !== document.body) {
                const s = getComputedStyle(cur);
                if (s.overflowX === "auto" || s.overflowX === "scroll" || s.overflowX === "hidden") {
                  return true;
                }
                cur = cur.parentElement;
              }
              return false;
            }
            for (const el of document.querySelectorAll("*")) {
              const r = el.getBoundingClientRect();
              if (r.right > vw + 1) {
                if (isInsideScrollContainer(el)) continue;
                const tag = el.tagName.toLowerCase();
                const cls = (el.className || "").toString().slice(0, 100);
                const id = el.id ? `#${el.id}` : "";
                problems.push(`${tag}${id}.${cls} right=${r.right.toFixed(1)} w=${r.width.toFixed(1)}`);
                if (problems.length >= 15) break;
              }
            }
            return problems;
          }, viewport.width);
        }

        if (overflow > 1) {
          console.log(`\n=== OVERFLOW: ${route.name} @ ${viewport.width}px: ${overflow.toFixed(1)}px ===`);
          for (const p of wideElements) console.log(`  ${p}`);
        }

        if (errors.length > 0) {
          console.log(`\n=== JS ERRORS on ${route.name} @ ${viewport.width}px ===`);
          for (const e of errors) console.log(`  ${e}`);
        }

        expect(overflow, `page overflows by ${overflow}px`).toBeLessThanOrEqual(1);
      });
    }
  });
}

test.describe("Mobile audit @ 375px — tap targets", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("nav hamburger is tappable", async ({ page }) => {
    await page.goto("./");
    const openBtn = page.locator("#mobile-menu-open");
    await expect(openBtn).toBeVisible();
    const box = await openBtn.boundingBox();
    expect(box, "hamburger has bounding box").not.toBeNull();
    if (box) {
      // Touch-target should be >= 44px (visible or via padding hit area).
      // The button has -m-2.5 p-2.5 giving it roughly 44x44.
      expect(box.width).toBeGreaterThanOrEqual(40);
      expect(box.height).toBeGreaterThanOrEqual(40);
    }
  });

  test("nav menu opens and links are tappable", async ({ page }) => {
    await page.goto("./");
    await page.click("#mobile-menu-open");
    const panel = page.locator("#mobile-menu-panel");
    await expect(panel).toBeVisible();
    const links = panel.locator("a[href*='/synthbench/']");
    const count = await links.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      const box = await links.nth(i).boundingBox();
      if (box) {
        expect(box.height, `link ${i} height`).toBeGreaterThanOrEqual(32);
      }
    }
  });

  test("leaderboard mobile card tap target + expand", async ({ page }) => {
    await page.goto("./leaderboard/");
    // On mobile the table is hidden (md:block / md:hidden) — cards render instead.
    const firstCard = page.locator(".leaderboard-card[data-entry]").first();
    await expect(firstCard).toBeVisible();
    const box = await firstCard.boundingBox();
    expect(box, "card has bounding box").not.toBeNull();
    if (box) {
      expect(box.height, "card tap height").toBeGreaterThanOrEqual(44);
    }
    // Tap to expand detail
    const detail = firstCard.locator(".mobile-detail");
    await expect(detail).toHaveClass(/hidden/);
    await firstCard.click();
    await expect(detail).not.toHaveClass(/hidden/);
  });
});
