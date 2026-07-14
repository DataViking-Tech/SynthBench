// Unit tests for the gated-data edge guard Pages Function
// (site/public/_worker.js). Uses Node's built-in test runner — no extra deps.
//   Run: npm run test:functions   (node --test tests/)
//
// These exercise handleRequest() with a stubbed asset fetcher standing in for
// env.ASSETS.fetch, covering the two invariants that must never regress:
//   1. ABSENT gated question/run/config artifact  -> fresh 403, no-store.
//   2. PRESENT full-tier artifact (gss/ntia/index) -> served unchanged (200).

import assert from "node:assert/strict";
import { test } from "node:test";
import { handleRequest, isGatedRiskPath } from "../public/_worker.js";

/** Build a stub env.ASSETS.fetch that returns a canned Response. */
function assetStub(status, body = "", headers = {}) {
  return async () => new Response(body, { status, headers });
}

const req = (path) => new Request(`https://synthbench.org${path}`);

test("isGatedRiskPath matches only question/run/config artifact roots", () => {
  assert.ok(isGatedRiskPath("/data/question/opinionsqa/REPRSNTREP_W92.json"));
  assert.ok(isGatedRiskPath("/data/run/some-run-id.json"));
  assert.ok(isGatedRiskPath("/data/config/some-config-id.json"));
  // Not gated-risk: top-level public catalogs and non-data routes.
  assert.ok(!isGatedRiskPath("/data/leaderboard.json"));
  assert.ok(!isGatedRiskPath("/data/runs-index.json"));
  assert.ok(!isGatedRiskPath("/index.html"));
  assert.ok(!isGatedRiskPath("/data/question")); // needs trailing slash + child
});

test("absent gated question artifact -> 403 no-store (evicts stale edge copy)", async () => {
  const res = await handleRequest(
    req("/data/question/opinionsqa/REPRSNTREP_W92.json"),
    assetStub(404),
  );
  assert.equal(res.status, 403);
  assert.equal(res.headers.get("Cache-Control"), "no-store");
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
  assert.match(res.headers.get("Content-Type"), /application\/json/);
  const body = await res.json();
  assert.equal(body.gated, true);
  assert.equal(body.error, "gated — sign in via the API");
});

test("absent gated run and config artifacts -> 403", async () => {
  for (const path of ["/data/run/r1.json", "/data/config/c1.json"]) {
    const res = await handleRequest(req(path), assetStub(404));
    assert.equal(res.status, 403, `expected 403 for ${path}`);
    assert.equal(res.headers.get("Cache-Control"), "no-store");
  }
});

test("present full-tier artifact (gss) -> 200 passthrough with data cache policy", async () => {
  const payload = JSON.stringify({ dataset: "gss", human_distribution: [0.5, 0.5] });
  const res = await handleRequest(
    req("/data/question/gss/ABANY.json"),
    assetStub(200, payload, { "Content-Type": "application/json" }),
  );
  assert.equal(res.status, 200);
  assert.equal(await res.text(), payload);
  assert.match(res.headers.get("Cache-Control"), /stale-while-revalidate/);
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
});

test("present full-tier run/config artifacts -> 200 passthrough", async () => {
  for (const path of ["/data/run/gss-run.json", "/data/config/gss-config.json"]) {
    const res = await handleRequest(req(path), assetStub(200, "{}"));
    assert.equal(res.status, 200, `expected 200 for ${path}`);
  }
});

test("present question index.json -> 200 passthrough (not treated as gated)", async () => {
  const res = await handleRequest(req("/data/question/gss/index.json"), assetStub(200, "[]"));
  assert.equal(res.status, 200);
});

test("non-gated-risk 404 is passed through unchanged (defense-in-depth)", async () => {
  // _routes.json scopes the Worker to the three artifact roots, so this path
  // should never reach the Worker in production — but if it does, a 404 for a
  // non-gated path must NOT be rewritten to 403.
  const res = await handleRequest(req("/data/leaderboard.json"), assetStub(404));
  assert.equal(res.status, 404);
});
