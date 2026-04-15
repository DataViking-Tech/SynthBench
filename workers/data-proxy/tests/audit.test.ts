import { describe, expect, it, vi } from "vitest";
import { clientIpFor, writeAuditLog } from "../src/audit";

function makeRequest(headers: Record<string, string>): Request {
  return new Request("https://api.synthbench.org/data/run/abc.json", { headers });
}

describe("clientIpFor", () => {
  it("prefers CF-Connecting-IP", () => {
    const req = makeRequest({
      "CF-Connecting-IP": "203.0.113.7",
      "x-forwarded-for": "203.0.113.9, 10.0.0.1",
    });
    expect(clientIpFor(req)).toBe("203.0.113.7");
  });

  it("falls back to the first x-forwarded-for entry", () => {
    const req = makeRequest({ "x-forwarded-for": "198.51.100.5, 10.0.0.1" });
    expect(clientIpFor(req)).toBe("198.51.100.5");
  });

  it("returns null when neither header is present", () => {
    const req = makeRequest({});
    expect(clientIpFor(req)).toBeNull();
  });
});

describe("writeAuditLog", () => {
  const config = {
    supabaseUrl: "https://test.supabase.co",
    serviceRoleKey: "service-role-secret",
  };

  it("POSTs to the PostgREST endpoint with service-role auth", async () => {
    const fetchImpl = vi.fn<typeof fetch>(async () => new Response(null, { status: 201 }));

    await writeAuditLog(
      {
        userId: "u-1",
        dataset: "opinions_qa",
        artifactPath: "run/abc.json",
        requestIp: "203.0.113.7",
        userAgent: "vitest/1.0",
      },
      { ...config, fetchImpl },
    );

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const firstCall = fetchImpl.mock.calls[0];
    if (!firstCall) throw new Error("expected fetch to be called");
    const [url, init] = firstCall;
    expect(url).toBe("https://test.supabase.co/rest/v1/data_access_log");
    expect(init?.method).toBe("POST");
    const headers = init?.headers as Record<string, string>;
    expect(headers.apikey).toBe("service-role-secret");
    expect(headers.Authorization).toBe("Bearer service-role-secret");
    expect(headers.Prefer).toBe("return=minimal");
    expect(JSON.parse(init?.body as string)).toEqual({
      user_id: "u-1",
      dataset: "opinions_qa",
      artifact_path: "run/abc.json",
      request_ip: "203.0.113.7",
      user_agent: "vitest/1.0",
    });
  });

  it("sends null dataset for non-question paths", async () => {
    const fetchImpl = vi.fn<typeof fetch>(async () => new Response(null, { status: 201 }));
    await writeAuditLog(
      {
        userId: "u-1",
        dataset: null,
        artifactPath: "run/abc.json",
        requestIp: null,
        userAgent: null,
      },
      { ...config, fetchImpl },
    );
    const call = fetchImpl.mock.calls[0];
    if (!call) throw new Error("expected fetch to be called");
    const body = JSON.parse(call[1]?.body as string);
    expect(body.dataset).toBeNull();
    expect(body.request_ip).toBeNull();
    expect(body.user_agent).toBeNull();
  });

  it("swallows transport errors so the data response is never blocked", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const fetchImpl = vi.fn<typeof fetch>(async () => {
      throw new Error("network down");
    });
    await expect(
      writeAuditLog(
        { userId: "u", dataset: null, artifactPath: "x", requestIp: null, userAgent: null },
        { ...config, fetchImpl },
      ),
    ).resolves.toBeUndefined();
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });

  it("logs a warning for non-2xx Supabase responses", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const fetchImpl = vi.fn<typeof fetch>(
      async () => new Response("rls violation", { status: 403, statusText: "Forbidden" }),
    );
    await writeAuditLog(
      { userId: "u", dataset: null, artifactPath: "x", requestIp: null, userAgent: null },
      { ...config, fetchImpl },
    );
    expect(warn).toHaveBeenCalledWith(expect.stringContaining("403"));
    warn.mockRestore();
  });
});
