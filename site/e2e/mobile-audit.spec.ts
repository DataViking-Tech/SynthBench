import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { type APIRequestContext, expect, test } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Layout regression guard: no page may scroll sideways, at phone, tablet and
// small-laptop widths, in light and dark mode. Hard-fails on horizontal
// overflow; small tap targets are reported (findings.json) but don't fail.
//
// Covers every Index page plus one system profile of each kind, a run, a
// question, the question index and the compare page. Dynamic routes are picked from the
// published data at test time so the guard survives data regeneration.

const VIEWPORTS = [
  { label: "390", width: 390, height: 844 },
  { label: "768", width: 768, height: 1024 },
  { label: "1024", width: 1024, height: 800 },
];
const SCHEMES = ["light", "dark"] as const;

const STATIC_ROUTES = [
  { path: "", label: "home" },
  { path: "leaderboard/", label: "leaderboard" },
  { path: "analysis/", label: "analysis" },
  { path: "groups/", label: "groups" },
  { path: "explore/", label: "explore" },
  { path: "findings/", label: "findings" },
  { path: "methodology/", label: "methodology" },
  { path: "datasets/", label: "datasets" },
  { path: "submit/", label: "submit" },
  { path: "compare/", label: "compare" },
];

/** One single-model and one ensemble profile, a full-tier run and question. */
async function dynamicRoutes(request: APIRequestContext) {
  const out: { path: string; label: string }[] = [];
  const idx = await request.get("data/sb-index.json");
  expect(idx.ok(), "data/sb-index.json").toBeTruthy();
  const index = await idx.json();
  const single = index.systems.find((c: { method: string }) => c.method === "althing");
  const ensemble = index.systems.find((c: { method: string }) => c.method === "ensemble");
  for (const [c, label] of [
    [single, "system-single"],
    [ensemble, "system-ensemble"],
  ] as const)
    if (c) out.push({ path: `system/${index.slugs[c.baseId]}/`, label });
  const runsRes = await request.get("data/runs-index.json");
  const run = runsRes.ok()
    ? (await runsRes.json()).runs.find((r: { dataset: string }) => r.dataset === "gss")
    : null;
  if (run) out.push({ path: `run/${encodeURIComponent(run.run_id)}/`, label: "run" });
  const qs = await request.get("data/question/gss/index.json");
  if (qs.ok()) {
    out.push({ path: "question/gss/", label: "question-index" });
    const q = (await qs.json()).questions?.[0];
    if (q) out.push({ path: `question/gss/${encodeURIComponent(q.key)}/`, label: "question" });
  }
  return out;
}

const OUT_DIR = path.join(__dirname, "mobile-audit-out");
fs.mkdirSync(OUT_DIR, { recursive: true });
const findings: { route: string; viewport: string; scheme: string; issues: string[] }[] = [];
test.afterAll(() => {
  fs.writeFileSync(path.join(OUT_DIR, "findings.json"), JSON.stringify(findings, null, 2));
});

test("no page scrolls sideways", async ({ browser, request }) => {
  test.setTimeout(15 * 60_000);
  const routes = [...STATIC_ROUTES, ...(await dynamicRoutes(request))];
  const failures: string[] = [];
  for (const scheme of SCHEMES) {
    for (const vp of VIEWPORTS) {
      const ctx = await browser.newContext({
        baseURL: test.info().project.use.baseURL,
        viewport: { width: vp.width, height: vp.height },
        colorScheme: scheme,
      });
      const page = await ctx.newPage();
      for (const route of routes) {
        await page.goto(route.path, { waitUntil: "networkidle" });
        await page.waitForTimeout(300);
        const m = await page.evaluate(() => {
          const vw = window.innerWidth;
          // Outermost elements that stick out past the right edge.
          const wide: string[] = [];
          for (const el of document.querySelectorAll("body *")) {
            const r = el.getBoundingClientRect();
            if (r.right <= vw + 1 || !r.width) continue;
            const parent = el.parentElement?.getBoundingClientRect();
            if (parent && parent.right > vw + 1) continue;
            wide.push(`${el.tagName.toLowerCase()}.${el.getAttribute("class") ?? ""}`.slice(0, 80));
          }
          let small = 0;
          for (const el of document.querySelectorAll(
            "a, button, input, select, [role=button], [role=radio], [role=checkbox]",
          )) {
            const r = el.getBoundingClientRect();
            if (r.width && r.height && (r.width < 24 || r.height < 24)) small++;
          }
          return { sw: document.documentElement.scrollWidth, vw, wide: wide.slice(0, 5), small };
        });
        const issues: string[] = [];
        if (m.sw > m.vw + 1) {
          const msg = `${route.label} @ ${vp.label} ${scheme}: page ${m.sw}px wide > ${m.vw}px (${m.wide.join(", ")})`;
          issues.push(msg);
          failures.push(msg);
          await page.screenshot({
            path: path.join(OUT_DIR, `${route.label}-${vp.label}-${scheme}.png`),
            fullPage: true,
          });
        }
        if (m.small) issues.push(`${m.small} tap targets under 24px`);
        findings.push({ route: route.label, viewport: vp.label, scheme, issues });
      }
      await ctx.close();
    }
  }
  expect(failures, failures.join("\n")).toEqual([]);
});
