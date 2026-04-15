// Supabase JWT validation. Supabase issues JWTs whose public verification
// keys are published as a JWKS at <SUPABASE_URL>/auth/v1/.well-known/jwks.json.
// `jose`'s createRemoteJWKSet handles fetch + cache + key rotation and works
// in Workers without node APIs.
//
// We keep one `getKeySet` per distinct JWKS URL cached in module scope so
// every request reuses the same fetch/cache state rather than paying the
// refresh cost on every invocation.

import { type JWTPayload, type JWTVerifyGetKey, createRemoteJWKSet, jwtVerify } from "jose";

export interface SupabaseClaims extends JWTPayload {
  /** Supabase user id. Always set on authenticated tokens. */
  sub: string;
  /** Expected to be "authenticated" for signed-in users; configurable via env. */
  aud: string | string[];
  /** Supabase project issuer, e.g. https://<ref>.supabase.co/auth/v1. */
  iss: string;
}

export interface VerifyConfig {
  /** Base Supabase project URL, e.g. https://<ref>.supabase.co. */
  supabaseUrl: string;
  /** Expected `aud` claim value (Supabase default: "authenticated"). */
  expectedAudience: string;
}

const keySetCache = new Map<string, JWTVerifyGetKey>();

function getKeySet(jwksUrl: string): JWTVerifyGetKey {
  let set = keySetCache.get(jwksUrl);
  if (!set) {
    set = createRemoteJWKSet(new URL(jwksUrl));
    keySetCache.set(jwksUrl, set);
  }
  return set;
}

export function parseBearer(authorization: string | null): string | null {
  if (!authorization) return null;
  const match = /^Bearer\s+(.+)$/i.exec(authorization.trim());
  return match?.[1]?.trim() || null;
}

export function jwksUrlFor(supabaseUrl: string): string {
  const trimmed = supabaseUrl.replace(/\/+$/, "");
  return `${trimmed}/auth/v1/.well-known/jwks.json`;
}

export function expectedIssuerFor(supabaseUrl: string): string {
  const trimmed = supabaseUrl.replace(/\/+$/, "");
  return `${trimmed}/auth/v1`;
}

/**
 * Verify a Supabase-issued JWT. Returns the decoded claims on success or
 * `null` if the signature, `iss`, `aud`, or `exp` fails validation. Uses
 * `keyResolver` as an injection seam so tests can supply an in-memory JWKS
 * rather than hitting the network.
 */
export async function verifySupabaseJwt(
  token: string,
  config: VerifyConfig,
  keyResolver: JWTVerifyGetKey = getKeySet(jwksUrlFor(config.supabaseUrl)),
): Promise<SupabaseClaims | null> {
  try {
    const { payload } = await jwtVerify(token, keyResolver, {
      issuer: expectedIssuerFor(config.supabaseUrl),
      audience: config.expectedAudience,
    });
    if (typeof payload.sub !== "string" || payload.sub.length === 0) return null;
    return payload as SupabaseClaims;
  } catch {
    // Any verification failure (signature, iss, aud, exp, malformed token)
    // collapses to a single 401 at the caller — we never leak the specific
    // reason to untrusted clients.
    return null;
  }
}

// Test-only escape hatch: lets the test suite prime the module-scoped cache
// with an in-memory key resolver so the Worker handler's default path still
// goes through `createRemoteJWKSet` in production.
export function __setKeySetForTesting(jwksUrl: string, resolver: JWTVerifyGetKey): void {
  keySetCache.set(jwksUrl, resolver);
}

export function __clearKeySetCacheForTesting(): void {
  keySetCache.clear();
}
