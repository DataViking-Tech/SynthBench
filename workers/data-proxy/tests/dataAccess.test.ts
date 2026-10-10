// /data access with `sb_` API keys (read scope) and dataset archives under
// datasets/. Complements index.test.ts, which covers the JWT browser path.

import { describe, expect, it, vi } from "vitest";
import { sha256Hex } from "../src/apiKey";
import worker from "../src/index";
import { parseRequestPath } from "../src/path";

const SUPABASE_URL = "https://test-project.supabase.co";
const WORKER_ORIGIN = "https://api.synthbench.org";
const READ_KEY = `sb_${"r".repeat(32)}`;
const READ_PREFIX = "sb_rrrrr";
const ARCHIVE_KEY = "datasets/opinionsqa/human_resp-canonical-v1.tar.gz";

interface StoredObject {
  body: string;
  contentType?: string;
}

function makeBucket(store: Map<string, StoredObject>): R2Bucket {
  return {
    async get(key: string) {
      const value = store.get(key);
      if (value === undefined) return null;
      return {
        body: new Response(value.body).body,
        httpMetadata: value.contentType ? { contentType: value.contentType } : {},
      } as unknown as R2ObjectBody;
    },
  } as unknown as R2Bucket;
}

function harness(scope: "read" | "submit" | "both") {
  const waitUntil: Promise<unknown>[] = [];
  const ctx = {
    waitUntil(p: Promise<unknown>) {
      waitUntil.push(p);
    },
    passThroughOnException() {},
  } as unknown as ExecutionContext;

  const auditBodies: unknown[] = [];
  const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
    const u = String(url);
    if (u.includes("/rest/v1/api_keys") && u.includes(`key_prefix=eq.${READ_PREFIX}`)) {
      return new Response(
        JSON.stringify([
          {
            id: 21,
            user_id: "user-reader",
            scope,
            expires_at: null,
            revoked_at: null,
            key_hash: await sha256Hex(READ_KEY),
          },
        ]),
        { status: 200 },
      );
    }
    if (u.includes("/rest/v1/api_keys") && init?.method === "PATCH") {
      return new Response(null, { status: 204 });
    }
    if (u.includes("/rest/v1/data_access_log")) {
      auditBodies.push(JSON.parse(String(init?.body ?? "{}")));
      return new Response(null, { status: 201 });
    }
    return new Response("unexpected", { status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);

  const store = new Map<string, StoredObject>([
    [ARCHIVE_KEY, { body: "gzip-bytes", contentType: "application/gzip" }],
    ["run/abc.json", { body: '{"ok":true}' }],
  ]);
  const env = {
    DATA_BUCKET: makeBucket(store),
    SUBMISSIONS_BUCKET: makeBucket(new Map()),
    SUPABASE_URL,
    SUPABASE_JWT_AUD: "authenticated",
    SUPABASE_SERVICE_ROLE_KEY: "service-role-secret",
    ALLOWED_ORIGINS: "https://synthbench.org",
    GITHUB_DISPATCH_TOKEN: "ghp-test",
    GITHUB_DISPATCH_REPO: "DataViking-Tech/synthbench",
    GITHUB_DISPATCH_WORKFLOW: "process-submission.yml",
    GITHUB_DISPATCH_REF: "main",
  } as Parameters<typeof worker.fetch>[1];
  return { env, ctx, waitUntil, auditBodies };
}

function get(path: string, token?: string): Request {
  return new Request(`${WORKER_ORIGIN}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

describe("parseRequestPath datasets/", () => {
  it("accepts dataset archives and labels the dataset", () => {
    const result = parseRequestPath("GET", `/data/${ARCHIVE_KEY}`);
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.value).toEqual({ bucketKey: ARCHIVE_KEY, dataset: "opinionsqa" });
  });

  it("never serves provenance/ (raw microdata)", () => {
    const result = parseRequestPath("GET", "/data/provenance/opinionsqa/raw.tar.gz");
    expect(result.ok).toBe(false);
  });
});

describe("/data with sb_ API keys", () => {
  it("serves a dataset archive to a read-scope key with its stored content type", async () => {
    const { env, ctx, waitUntil, auditBodies } = harness("read");
    const res = await worker.fetch(get(`/data/${ARCHIVE_KEY}`, READ_KEY), env, ctx);
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("application/gzip");
    expect(await res.text()).toBe("gzip-bytes");
    await Promise.all(waitUntil);
    expect(auditBodies).toContainEqual(
      expect.objectContaining({
        user_id: "user-reader",
        dataset: "opinionsqa",
        artifact_path: ARCHIVE_KEY,
      }),
    );
  });

  it("accepts a key with both scopes", async () => {
    const { env, ctx } = harness("both");
    const res = await worker.fetch(get(`/data/${ARCHIVE_KEY}`, READ_KEY), env, ctx);
    expect(res.status).toBe(200);
  });

  it("rejects a submit-only key with 403", async () => {
    const { env, ctx } = harness("submit");
    const res = await worker.fetch(get(`/data/${ARCHIVE_KEY}`, READ_KEY), env, ctx);
    expect(res.status).toBe(403);
    expect(((await res.json()) as { error: string }).error).toContain("read scope");
  });

  it("keeps JSON content type for publish artifacts", async () => {
    const { env, ctx } = harness("read");
    const res = await worker.fetch(get("/data/run/abc.json", READ_KEY), env, ctx);
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("application/json; charset=utf-8");
  });

  it("still requires a token", async () => {
    const { env, ctx } = harness("read");
    const res = await worker.fetch(get(`/data/${ARCHIVE_KEY}`), env, ctx);
    expect(res.status).toBe(401);
  });
});
