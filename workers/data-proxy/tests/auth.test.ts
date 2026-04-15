import { SignJWT, createLocalJWKSet, exportJWK, generateKeyPair } from "jose";
import { beforeAll, describe, expect, it } from "vitest";
import {
  __clearKeySetCacheForTesting,
  __setKeySetForTesting,
  expectedIssuerFor,
  jwksUrlFor,
  parseBearer,
  verifySupabaseJwt,
} from "../src/auth";

const SUPABASE_URL = "https://test-project.supabase.co";
const CONFIG = { supabaseUrl: SUPABASE_URL, expectedAudience: "authenticated" };

type KeyPair = Awaited<ReturnType<typeof generateKeyPair>>;

let validKeys: KeyPair;
let otherKeys: KeyPair;
let jwks: Awaited<ReturnType<typeof createLocalJWKSet>>;

async function signToken(
  opts: { aud?: string; iss?: string; sub?: string; expSeconds?: number; keys?: KeyPair } = {},
): Promise<string> {
  const keys = opts.keys ?? validKeys;
  const builder = new SignJWT({})
    .setProtectedHeader({ alg: "ES256" })
    .setSubject(opts.sub ?? "user-123")
    .setIssuer(opts.iss ?? expectedIssuerFor(SUPABASE_URL))
    .setAudience(opts.aud ?? "authenticated")
    .setIssuedAt();
  const exp = opts.expSeconds ?? 3600;
  builder.setExpirationTime(`${exp}s`);
  return builder.sign(keys.privateKey);
}

beforeAll(async () => {
  validKeys = await generateKeyPair("ES256");
  otherKeys = await generateKeyPair("ES256");

  const jwk = await exportJWK(validKeys.publicKey);
  jwk.alg = "ES256";
  jwk.kid = "test-key-1";
  jwks = createLocalJWKSet({ keys: [jwk] });

  __clearKeySetCacheForTesting();
  __setKeySetForTesting(jwksUrlFor(SUPABASE_URL), jwks);
});

describe("parseBearer", () => {
  it("extracts the token from a well-formed header", () => {
    expect(parseBearer("Bearer abc.def.ghi")).toBe("abc.def.ghi");
    expect(parseBearer("bearer abc.def.ghi")).toBe("abc.def.ghi");
    expect(parseBearer("  Bearer   tok123  ")).toBe("tok123");
  });

  it("returns null for missing or malformed headers", () => {
    expect(parseBearer(null)).toBeNull();
    expect(parseBearer("")).toBeNull();
    expect(parseBearer("Basic dXNlcjpwYXNz")).toBeNull();
    expect(parseBearer("Bearer ")).toBeNull();
    expect(parseBearer("Bearer")).toBeNull();
  });
});

describe("jwksUrlFor / expectedIssuerFor", () => {
  it("derives JWKS + issuer URLs and normalizes trailing slashes", () => {
    expect(jwksUrlFor("https://x.supabase.co")).toBe(
      "https://x.supabase.co/auth/v1/.well-known/jwks.json",
    );
    expect(jwksUrlFor("https://x.supabase.co/")).toBe(
      "https://x.supabase.co/auth/v1/.well-known/jwks.json",
    );
    expect(expectedIssuerFor("https://x.supabase.co/")).toBe("https://x.supabase.co/auth/v1");
  });
});

describe("verifySupabaseJwt", () => {
  it("accepts a valid signed token and returns the claims", async () => {
    const token = await signToken();
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).not.toBeNull();
    expect(claims?.sub).toBe("user-123");
    expect(claims?.aud).toBe("authenticated");
  });

  it("rejects tokens signed by the wrong key", async () => {
    const token = await signToken({ keys: otherKeys });
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).toBeNull();
  });

  it("rejects tokens with the wrong audience", async () => {
    const token = await signToken({ aud: "anon" });
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).toBeNull();
  });

  it("rejects tokens with the wrong issuer", async () => {
    const token = await signToken({ iss: "https://other.supabase.co/auth/v1" });
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).toBeNull();
  });

  it("rejects expired tokens", async () => {
    const token = await signToken({ expSeconds: -60 });
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).toBeNull();
  });

  it("rejects malformed tokens", async () => {
    expect(await verifySupabaseJwt("not-a-jwt", CONFIG, jwks)).toBeNull();
    expect(await verifySupabaseJwt("", CONFIG, jwks)).toBeNull();
    expect(await verifySupabaseJwt("a.b.c", CONFIG, jwks)).toBeNull();
  });

  it("rejects tokens with an empty sub claim", async () => {
    const token = await signToken({ sub: "" });
    const claims = await verifySupabaseJwt(token, CONFIG, jwks);
    expect(claims).toBeNull();
  });
});
