// Cloudflare Pages advanced-mode Worker — gated-data edge guard (sb-edge-guard).
//
// WHY advanced mode (a single _worker.js at the deploy root) instead of a
// file-based `functions/` directory:
//   The deploy step runs `wrangler pages deploy site/dist` from the repo root
//   (see .github/workflows/cf-pages.yml). Wrangler resolves a file-based
//   `functions/` directory relative to its current working directory (the repo
//   root) — NOT inside the uploaded `site/dist` — so a `site/functions/` dir
//   would be silently ignored and never deployed. A `_worker.js` at the ROOT
//   of the uploaded directory is detected unconditionally, independent of CWD.
//   Astro copies everything under `site/public/` to `site/dist/` verbatim (the
//   same mechanism that already ships `site/public/_headers`), so this file
//   lands at `site/dist/_worker.js` and is guaranteed to be the deployed Pages
//   Function. `site/dist/_routes.json` (from `site/public/_routes.json`) scopes
//   it to /data/(question|run|config)/* only.
//
// WHAT it does:
//   License-restricted "gated" per-question survey data (Pew ATP, OpinionsQA,
//   …) must never be served from the public static origin. Publish now skips
//   gated artifacts (they upload to the authenticated R2 origin instead), so a
//   gated /data/(question|run|config)/… path is ABSENT from the static assets
//   and the origin 404s it. But a handful of gated URLs are stuck in
//   Cloudflare's Always-Online / stale-while-revalidate cache tier, still
//   returning a stale HTTP 200 with the full `human_distribution`. This Worker:
//     (a) permanently blocks gated data at the edge — an absent
//         question/run/config artifact returns a fresh 403, and
//     (b) EVICTS the stuck stale copies — when Cloudflare revalidates the
//         SWR-cached entry, the origin now returns a definitive
//         `403 Cache-Control: no-store` (not a 404 that Always-Online
//         "rescues"), so the archived 200 is replaced and never re-stored.
//
//   Full-tier artifacts (gss, ntia, per-question index.json, and — because
//   they are never routed here — runs-index.json / leaderboard.json) DO exist
//   as static assets and are served unchanged.

// Per-question / per-run / per-config artifact roots. Gated datasets emit
// artifacts ONLY under these three prefixes (see src/synthbench/publish.py);
// an asset that is absent here was withheld for licensing, i.e. it is gated.
const GATED_RISK_RE = /^\/data\/(question|run|config)\//;

// Mirror of the `/data/*` policy in site/public/_headers so full-tier
// artifacts that pass through this Worker keep the same public
// stale-while-revalidate cache contract that directly-served /data/* assets
// get (env.ASSETS.fetch does not reliably re-apply _headers).
const DATA_CACHE_CONTROL = "public, max-age=3600, s-maxage=21600, stale-while-revalidate=86400";

const GATED_BODY = JSON.stringify({
  error: "gated — sign in via the API",
  gated: true,
});

/**
 * True when `pathname` addresses a per-question/run/config artifact whose
 * absence from static assets means it was withheld as gated data.
 * @param {string} pathname
 * @returns {boolean}
 */
export function isGatedRiskPath(pathname) {
  return GATED_RISK_RE.test(pathname);
}

/**
 * Core request logic, split out from the default export so it is unit-testable
 * with a stubbed asset fetcher.
 * @param {Request} request
 * @param {(request: Request) => Promise<Response>} assetFetch  env.ASSETS.fetch
 * @returns {Promise<Response>}
 */
export async function handleRequest(request, assetFetch) {
  const { pathname } = new URL(request.url);
  const assetRes = await assetFetch(request);

  // Gated backstop: an absent per-question/run/config artifact is withheld
  // license-restricted data. Return a fresh, uncacheable 403 that evicts any
  // stale edge copy when Cloudflare revalidates.
  if (assetRes.status === 404 && isGatedRiskPath(pathname)) {
    return new Response(GATED_BODY, {
      status: 403,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  // Everything else (full-tier gss/ntia artifacts, per-question index.json, any
  // 2xx /data asset) passes through. Re-assert the public /data/* cache + CORS
  // contract so the pass-through matches direct static-asset serving.
  const res = new Response(assetRes.body, assetRes);
  if (assetRes.ok) {
    res.headers.set("Cache-Control", DATA_CACHE_CONTROL);
    res.headers.set("Access-Control-Allow-Origin", "*");
  }
  return res;
}

export default {
  /**
   * @param {Request} request
   * @param {{ ASSETS: { fetch: (request: Request) => Promise<Response> } }} env
   * @returns {Promise<Response>}
   */
  async fetch(request, env) {
    return handleRequest(request, (req) => env.ASSETS.fetch(req));
  },
};
