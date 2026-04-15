import { describe, expect, it } from "vitest";
import { corsHeadersFor, parseAllowedOrigins, preflightResponse } from "../src/cors";

describe("parseAllowedOrigins", () => {
  it("splits comma-separated values and trims whitespace", () => {
    const set = parseAllowedOrigins("https://a.com, https://b.com ,https://c.com");
    expect(set.has("https://a.com")).toBe(true);
    expect(set.has("https://b.com")).toBe(true);
    expect(set.has("https://c.com")).toBe(true);
    expect(set.size).toBe(3);
  });

  it("returns an empty set for undefined or empty input", () => {
    expect(parseAllowedOrigins(undefined).size).toBe(0);
    expect(parseAllowedOrigins("").size).toBe(0);
    expect(parseAllowedOrigins("   ").size).toBe(0);
  });
});

describe("corsHeadersFor", () => {
  const allowed = parseAllowedOrigins("https://synthbench.org,https://www.synthbench.org");

  it("grants CORS for allowed origins with credentials", () => {
    const headers = corsHeadersFor("https://synthbench.org", allowed);
    expect(headers["Access-Control-Allow-Origin"]).toBe("https://synthbench.org");
    expect(headers["Access-Control-Allow-Credentials"]).toBe("true");
    expect(headers.Vary).toBe("Origin");
    expect(headers["Access-Control-Allow-Methods"]).toContain("GET");
    expect(headers["Access-Control-Allow-Headers"]).toContain("Authorization");
  });

  it("omits CORS grant for unknown origins but keeps Vary header", () => {
    const headers = corsHeadersFor("https://evil.example", allowed);
    expect(headers["Access-Control-Allow-Origin"]).toBeUndefined();
    expect(headers.Vary).toBe("Origin");
  });

  it("omits CORS grant when no Origin header is present", () => {
    const headers = corsHeadersFor(null, allowed);
    expect(headers["Access-Control-Allow-Origin"]).toBeUndefined();
    expect(headers.Vary).toBe("Origin");
  });

  it("never returns wildcard origin", () => {
    // Credentials mode + wildcard is a browser-blocked combo. Guard against
    // future regressions where someone sets ALLOWED_ORIGINS to "*".
    const wildcardSet = parseAllowedOrigins("*");
    const headers = corsHeadersFor("https://synthbench.org", wildcardSet);
    expect(headers["Access-Control-Allow-Origin"]).toBeUndefined();
  });
});

describe("preflightResponse", () => {
  const allowed = parseAllowedOrigins("https://synthbench.org");

  it("returns 204 with CORS + max-age for allowed origin", async () => {
    const res = preflightResponse("https://synthbench.org", allowed);
    expect(res.status).toBe(204);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe("https://synthbench.org");
    expect(res.headers.get("Access-Control-Max-Age")).toBe("86400");
    expect(await res.text()).toBe("");
  });

  it("returns 204 without CORS grant for disallowed origin", () => {
    const res = preflightResponse("https://evil.example", allowed);
    expect(res.status).toBe(204);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBeNull();
  });
});
