import { expect, test } from "@playwright/test";

// sb-3ie — Mirror of sb-ave for /compare. The Metrics tiles render via an
// inner script that injects `.metric-tile` nodes into `#compare-metrics`
// after fetching both subjects' rollups. The tile background uses the
// LIGHT-mode `--color-surface` token, which is not flipped in dark mode and
// produces grey-on-grey for the muted label/value text. This spec asserts
// WCAG AA (4.5:1) for the metric label in both light and dark themes.

const RUN_A = "opinionsqa_ensemble_3blend_20260412_020745";
const RUN_B = "opinionsqa_majority-baseline_20260410_152904";
const ROUTE = `compare/?a=${encodeURIComponent(RUN_A)}&b=${encodeURIComponent(RUN_B)}&mode=run`;

async function measureContrast(page: import("@playwright/test").Page): Promise<number> {
  const firstTile = page.locator("#compare-metrics .metric-tile").first();
  await expect(firstTile).toBeVisible({ timeout: 15000 });

  return await page.evaluate(() => {
    const tile = document.querySelector<HTMLElement>("#compare-metrics .metric-tile");
    const label = tile?.querySelector<HTMLElement>(".metric-label");
    const body = document.body;
    if (!tile || !label) throw new Error("metric-tile or metric-label missing");

    // Paint a single CSS color onto a 1×1 canvas atop an explicit underlay
    // and read the resulting [r,g,b,a] pixel. `paint(color)` returns the
    // color composited over solid white (no underlay); `paint(color, under)`
    // composites over `under` (which itself may be translucent — caller is
    // responsible for layering).
    const paint = (
      color: string,
      under?: [number, number, number],
    ): [number, number, number, number] => {
      const cv = document.createElement("canvas");
      cv.width = cv.height = 1;
      const ctx = cv.getContext("2d");
      if (!ctx) throw new Error("no 2d context");
      if (under) {
        ctx.fillStyle = `rgb(${under[0]}, ${under[1]}, ${under[2]})`;
        ctx.fillRect(0, 0, 1, 1);
      } else {
        ctx.clearRect(0, 0, 1, 1);
      }
      ctx.fillStyle = color;
      ctx.fillRect(0, 0, 1, 1);
      const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
      return [r, g, b, a / 255];
    };

    const lumin = (r: number, g: number, b: number): number => {
      const conv = (c: number) => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
      };
      return 0.2126 * conv(r) + 0.7152 * conv(g) + 0.0722 * conv(b);
    };

    const bodyRgba = paint(getComputedStyle(body).backgroundColor);
    const bodyOpaque: [number, number, number] = [bodyRgba[0], bodyRgba[1], bodyRgba[2]];

    // Tile fill is `color-mix(... transparent)` → translucent. Layer it onto
    // the body background to recover the visible color the user sees.
    const tileOnBody = paint(getComputedStyle(tile).backgroundColor, bodyOpaque);
    const tileOpaque: [number, number, number] = [tileOnBody[0], tileOnBody[1], tileOnBody[2]];

    const labelOnTile = paint(getComputedStyle(label).color, tileOpaque);

    const lf = lumin(labelOnTile[0], labelOnTile[1], labelOnTile[2]);
    const lb = lumin(tileOpaque[0], tileOpaque[1], tileOpaque[2]);
    const [hi, lo] = lf >= lb ? [lf, lb] : [lb, lf];
    return (hi + 0.05) / (lo + 0.05);
  });
}

test.describe("compare: metric-tile label contrast (sb-3ie)", () => {
  test("dark theme — metric-label clears WCAG AA on tile background", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto(ROUTE);
    const ratio = await measureContrast(page);
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  test("light theme — metric-label clears WCAG AA on tile background", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "light" });
    await page.goto(ROUTE);
    const ratio = await measureContrast(page);
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });
});
