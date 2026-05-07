import sentry from "@sentry/astro";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";

// Defaults preserve GH Pages behavior so existing builds keep working.
// CF Pages overrides via build env: SITE_URL=https://synthbench.org BASE_PATH=/
const site = process.env.SITE_URL || "https://dataviking-tech.github.io";
const base = process.env.BASE_PATH || "/synthbench";

// sb-xjf: Sentry config. All env vars are optional so local `npm run build`
// still works without Doppler — the integration only emits events when
// PUBLIC_SENTRY_DSN is set, and only uploads source maps when SENTRY_AUTH_TOKEN
// is set. CI populates all four from synthbench/prd Doppler.
const sentryDsn = process.env.PUBLIC_SENTRY_DSN || "";
const sentryAuthToken = process.env.SENTRY_AUTH_TOKEN || "";
const sentryOrg = process.env.SENTRY_ORG_SLUG || "dataviking-llc";
const sentryProject = process.env.SENTRY_PROJECT_SLUG || "synthbench";

const integrations = [];
if (sentryDsn) {
  integrations.push(
    sentry({
      dsn: sentryDsn,
      // server_name distinguishes site events from worker events (which set
      // server_name="synthbench-data-proxy" in withSentry init) — both surfaces
      // share the `synthbench` Sentry project per the bead description.
      sourceMapsUploadOptions: {
        org: sentryOrg,
        project: sentryProject,
        authToken: sentryAuthToken,
        // Skip the upload step entirely when no auth token is present so
        // preview builds (e.g. fork PRs without secrets) don't fail.
        enabled: Boolean(sentryAuthToken),
      },
    }),
  );
}

export default defineConfig({
  site,
  base,
  integrations,
  vite: {
    plugins: [tailwindcss()],
  },
});
