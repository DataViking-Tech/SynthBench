import { expect, test } from "@playwright/test";

// sb-u74 Pass 4.1 — VRT for the 5 representative stories (Chart has 3 variants).
// Each story renders in the Storybook preview iframe at:
//   /iframe.html?id=<story-id>&viewMode=story&globals=theme:<light|dark>
// The theme toggle comes from withThemeByDataAttribute in .storybook/preview.ts,
// which sets data-theme on the preview document; we also emulate the OS color
// scheme so Tailwind's prefers-color-scheme queries match.
//
// KNOWN LIMITATION — static render mode: Astro's inline <script> blocks are
// hoisted to the page level during build and do NOT execute inside
// storybook-astro's static-rendered story frames. Chart/chart-like stories
// render the container + data-option attribute but the echarts init script
// never runs, so canvases are blank. VRT still protects against HTML/CSS
// regressions in the container, legend, heading, and wrapping chrome.
// See follow-up bead sb-v8j for tracking full script-hoisting support.

type Story = {
  id: string;
  label: string;
  settleMs?: number;
  readySelector?: string;
};

const STORIES: Story[] = [
  {
    id: "shared-chart--bar",
    label: "chart-bar",
    readySelector: ".echarts-container",
    settleMs: 500,
  },
  {
    id: "shared-chart--line",
    label: "chart-line",
    readySelector: ".echarts-container",
    settleMs: 500,
  },
  {
    id: "shared-chart--short-height",
    label: "chart-short-height",
    readySelector: ".echarts-container",
    settleMs: 500,
  },
  {
    id: "leaderboard-leaderboardtable--default",
    label: "leaderboard-table",
    readySelector: "#leaderboard-table",
    settleMs: 300,
  },
  {
    id: "home-keyfindings--default",
    label: "home-key-findings",
    settleMs: 300,
  },
  {
    id: "home-herosection--default",
    label: "home-hero",
    settleMs: 300,
  },
  {
    id: "findings-convergenceline--default",
    label: "findings-convergence-line",
    readySelector: ".echarts-container",
    settleMs: 500,
  },
];

const THEMES = [
  { label: "light", colorScheme: "light" as const, global: "theme:light" },
  { label: "dark", colorScheme: "dark" as const, global: "theme:dark" },
];

for (const story of STORIES) {
  for (const theme of THEMES) {
    test(`${story.label} — ${theme.label}`, async ({ page }) => {
      test.setTimeout(45000);
      await page.emulateMedia({ colorScheme: theme.colorScheme });
      const url = `/iframe.html?id=${story.id}&viewMode=story&globals=${encodeURIComponent(theme.global)}`;
      await page.goto(url, { waitUntil: "networkidle" });
      if (story.readySelector) {
        await page.waitForSelector(story.readySelector, { timeout: 10000 });
      }
      if (story.settleMs) {
        await page.waitForTimeout(story.settleMs);
      }
      await page.waitForLoadState("networkidle");
      await expect(page).toHaveScreenshot(`${story.label}-${theme.label}.png`, {
        fullPage: true,
        timeout: 20000,
      });
    });
  }
}
