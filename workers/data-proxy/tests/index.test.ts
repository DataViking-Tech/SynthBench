// End-to-end unit test for the Worker fetch handler. We supply a fake R2
// bucket + a test-only key resolver so the handler runs through the real
// auth/path/CORS/audit wiring without touching the network.

import { SignJWT, createLocalJWKSet, exportJWK, generateKeyPair } from "jose";
import { beforeAll, describe, expect, it, vi } from "vitest";
import {
  __clearKeySetCacheForTesting,
  __setKeySetForTesting,
  expectedIssuerFor,
  jwksUrlFor,
} from "../src/auth";
import worker from "../src/index";

const SUPABASE_URL = "https://test-project.supabase.co";
const WORKER_ORIGIN = "https://api.synthbench.org";
const SITE_ORIGIN = "https://synthbench.org";

type KeyPair = Awaited<ReturnType<typeof generateKeyPair>>;
let validKeys: KeyPair;
let jwks: Awaited<ReturnType<typeof createLocalJWKSet>>;

beforeAll(async () => {
  validKeys = await generateKeyPair("ES256");
  const jwk = await exportJWK(validKeys.publicKey);
  jwk.alg = "ES256";
  jwk.kid = "test-key-e2e";
  jwks = createLocalJWKSet({ keys: [jwk] });
  __clearKeySetCacheForTesting();
  __setKeySetForTesting(jwksUrlFor(SUPABASE_URL), jwks);
});

async function signToken(overrides: Partial<{ sub: string; aud: string; exp: number }> = {}) {
  return new SignJWT({})
    .setProtectedHeader({ alg: "ES256" })
    .setSubject(overrides.sub ?? "user-abc")
    .setIssuer(expectedIssuerFor(SUPABASE_URL))
    .setAudience(overrides.aud ?? "authenticated")
    .setIssuedAt()
    .setExpirationTime(`${overrides.exp ?? 3600}s`)
    .sign(validKeys.privateKey);
}

// Minimal R2Bucket double with the shape the Worker actually uses. Only
// `get()` is exercised; other methods throw so accidental usage fails loudly.
function makeBucket(store: Map<string, string>): R2Bucket {
  return {
    async get(key: string) {
      const value = store.get(key);
      if (value === undefined) return null;
      return {
        body: new Response(value).body,
      } as unknown as R2ObjectBody;
    },
  } as unknown as R2Bucket;
}

interface Harness {
  env: Parameters<typeof worker.fetch>[1];
  ctx: ExecutionContext;
  waitUntilPromises: Promise<unknown>[];
  fetchMock: ReturnType<typeof vi.fn>;
}

function makeHarness(
  store: Map<string, string> = new Map([["run/abc.json", '{"ok":true}']]),
): Harness {
  const waitUntilPromises: Promise<unknown>[] = [];
  const ctx = {
    waitUntil(p: Promise<unknown>) {
      waitUntilPromises.push(p);
    },
    passThroughOnException() {},
  } as unknown as ExecutionContext;

  // The Worker's audit writer calls global fetch; route through a vitest
  // spy so we can assert on audit emissions without a live network.
  const fetchMock = vi.fn(async () => new Response(null, { status: 201 }));
  vi.stubGlobal("fetch", fetchMock);

  const env = {
    DATA_BUCKET: makeBucket(store),
    SUPABASE_URL,
    SUPABASE_JWT_AUD: "authenticated",
    SUPABASE_SERVICE_ROLE_KEY: "service-role-secret",
    ALLOWED_ORIGINS: `${SITE_ORIGIN},https://www.synthbench.org`,
  } as Parameters<typeof worker.fetch>[1];

  return { env, ctx, waitUntilPromises, fetchMock };
}

describe("Worker fetch handler", () => {
  it("handles CORS preflight for allowed origins", async () => {
    const { env, ctx } = makeHarness();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`, {
        method: "OPTIONS",
        headers: { Origin: SITE_ORIGIN },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(204);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe(SITE_ORIGIN);
    expect(res.headers.get("Access-Control-Allow-Credentials")).toBe("true");
  });

  it("returns 401 when Authorization is missing", async () => {
    const { env, ctx } = makeHarness();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`, { headers: { Origin: SITE_ORIGIN } }),
      env,
      ctx,
    );
    expect(res.status).toBe(401);
    expect(await res.json()).toEqual({ error: "sign in to view" });
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe(SITE_ORIGIN);
  });

  it("returns 401 for invalid JWTs", async () => {
    const { env, ctx } = makeHarness();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`, {
        headers: { Authorization: "Bearer nope.not.jwt" },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(401);
    expect(await res.json()).toEqual({ error: "invalid token" });
  });

  it("returns 400 for bad paths (unknown top-level dir)", async () => {
    const { env, ctx } = makeHarness();
    const token = await signToken();
    // Note: URL-level traversal like `/data/../x` gets normalized by the URL
    // parser before it reaches the Worker, so we exercise the allowlist path
    // instead — a syntactically valid /data/ request with a forbidden prefix.
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/secret/thing.json`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(400);
  });

  it("returns 404 for unknown R2 keys", async () => {
    const { env, ctx } = makeHarness(new Map());
    const token = await signToken();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/missing.json`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(404);
  });

  it("returns 200 + JSON body + audit log for authenticated hits", async () => {
    const { env, ctx, waitUntilPromises, fetchMock } = makeHarness(
      new Map([["question/opinions_qa/q1.json", '{"key":"q1"}']]),
    );
    const token = await signToken({ sub: "user-xyz" });
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/question/opinions_qa/q1.json`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Origin: SITE_ORIGIN,
          "CF-Connecting-IP": "203.0.113.7",
          "User-Agent": "vitest-harness",
        },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toContain("application/json");
    expect(res.headers.get("Cache-Control")).toBe("private, max-age=60");
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe(SITE_ORIGIN);
    expect(await res.json()).toEqual({ key: "q1" });

    // Flush the fire-and-forget audit write and assert on its payload.
    await Promise.all(waitUntilPromises);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const auditCall = fetchMock.mock.calls[0];
    if (!auditCall) throw new Error("expected audit fetch to be called");
    const [url, init] = auditCall;
    expect(url).toBe(`${SUPABASE_URL}/rest/v1/data_access_log`);
    const body = JSON.parse((init as RequestInit).body as string);
    expect(body).toEqual({
      user_id: "user-xyz",
      dataset: "opinions_qa",
      artifact_path: "question/opinions_qa/q1.json",
      request_ip: "203.0.113.7",
      user_agent: "vitest-harness",
    });
  });

  it("returns HEAD with no body on authenticated hits", async () => {
    const { env, ctx, waitUntilPromises, fetchMock } = makeHarness();
    const token = await signToken();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`, {
        method: "HEAD",
        headers: { Authorization: `Bearer ${token}` },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("");
    // HEAD intentionally does not audit (no body read) — keeps the audit log
    // focused on actual data retrievals.
    await Promise.all(waitUntilPromises);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns 500 when required env is missing", async () => {
    const { env, ctx } = makeHarness();
    const brokenEnv = { ...env, SUPABASE_URL: "" };
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`),
      brokenEnv,
      ctx,
    );
    expect(res.status).toBe(500);
  });

  it("does not leak CORS headers to disallowed origins on success", async () => {
    const { env, ctx } = makeHarness();
    const token = await signToken();
    const res = await worker.fetch(
      new Request(`${WORKER_ORIGIN}/data/run/abc.json`, {
        headers: { Authorization: `Bearer ${token}`, Origin: "https://evil.example" },
      }),
      env,
      ctx,
    );
    expect(res.status).toBe(200);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBeNull();
    expect(res.headers.get("Vary")).toBe("Origin");
  });
});
