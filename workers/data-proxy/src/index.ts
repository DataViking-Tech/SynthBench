// Cloudflare Worker entrypoint for sb-io1 — the gated-tier data proxy.
//
// Flow per request:
//   1. Preflight? → return CORS headers and bail.
//   2. Parse /data/<key>; reject bad paths (including `..` traversal) with 400.
//   3. Parse Authorization: Bearer <jwt>; missing → 401.
//   4. Verify JWT against Supabase JWKS; invalid/expired → 401.
//   5. Fetch from R2; miss → 404.
//   6. Fire-and-forget audit log via ctx.waitUntil.
//   7. Return JSON with `Cache-Control: private, max-age=60` so CDN shared
//      caches never hold user-specific data.
//
// Every branch has a matching unit test in tests/.

import { type AuditConfig, clientIpFor, writeAuditLog } from "./audit";
import { parseBearer, verifySupabaseJwt } from "./auth";
import { corsHeadersFor, parseAllowedOrigins, preflightResponse } from "./cors";
import { parseRequestPath } from "./path";

export interface Env {
  DATA_BUCKET: R2Bucket;
  SUPABASE_URL: string;
  SUPABASE_JWT_AUD: string;
  SUPABASE_SERVICE_ROLE_KEY: string;
  ALLOWED_ORIGINS: string;
}

function jsonResponse(
  body: unknown,
  status: number,
  extraHeaders: Record<string, string>,
): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...extraHeaders,
    },
  });
}

function envConfigOk(env: Env): boolean {
  // The Worker is useless without these — fail loudly with a 500 so operators
  // catch misconfiguration immediately rather than silently serving 401s.
  return Boolean(env.SUPABASE_URL && env.SUPABASE_JWT_AUD && env.SUPABASE_SERVICE_ROLE_KEY);
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const origin = request.headers.get("Origin");
    const allowed = parseAllowedOrigins(env.ALLOWED_ORIGINS);

    if (request.method === "OPTIONS") {
      return preflightResponse(origin, allowed);
    }

    const cors = corsHeadersFor(origin, allowed);

    if (!envConfigOk(env)) {
      return jsonResponse({ error: "server misconfigured" }, 500, cors);
    }

    const url = new URL(request.url);
    const parsed = parseRequestPath(request.method, url.pathname);
    if (!parsed.ok) {
      const status = parsed.error === "bad_method" ? 405 : parsed.error === "bad_path" ? 400 : 404;
      const message =
        parsed.error === "bad_method"
          ? "method not allowed"
          : parsed.error === "bad_path"
            ? "bad path"
            : "not found";
      return jsonResponse({ error: message }, status, cors);
    }

    const token = parseBearer(request.headers.get("Authorization"));
    if (!token) {
      return jsonResponse({ error: "sign in to view" }, 401, cors);
    }

    const claims = await verifySupabaseJwt(token, {
      supabaseUrl: env.SUPABASE_URL,
      expectedAudience: env.SUPABASE_JWT_AUD,
    });
    if (!claims) {
      return jsonResponse({ error: "invalid token" }, 401, cors);
    }

    const { bucketKey, dataset } = parsed.value;

    const obj = await env.DATA_BUCKET.get(bucketKey);
    if (!obj) {
      return jsonResponse({ error: "not found" }, 404, cors);
    }

    // HEAD must not return a body — match R2's metadata-only response shape.
    if (request.method === "HEAD") {
      return new Response(null, {
        status: 200,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "private, max-age=60",
          ...cors,
        },
      });
    }

    const auditConfig: AuditConfig = {
      supabaseUrl: env.SUPABASE_URL,
      serviceRoleKey: env.SUPABASE_SERVICE_ROLE_KEY,
    };
    ctx.waitUntil(
      writeAuditLog(
        {
          userId: claims.sub,
          dataset,
          artifactPath: bucketKey,
          requestIp: clientIpFor(request),
          userAgent: request.headers.get("User-Agent"),
        },
        auditConfig,
      ),
    );

    return new Response(obj.body, {
      status: 200,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "private, max-age=60",
        ...cors,
      },
    });
  },
};
