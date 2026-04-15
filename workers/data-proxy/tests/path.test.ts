import { describe, expect, it } from "vitest";
import { parseRequestPath } from "../src/path";

describe("parseRequestPath", () => {
  it("accepts a run artifact path", () => {
    const result = parseRequestPath("GET", "/data/run/abc123.json");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value).toEqual({ bucketKey: "run/abc123.json", dataset: null });
    }
  });

  it("accepts a config artifact path", () => {
    const result = parseRequestPath("GET", "/data/config/haiku-t0.3.json");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.bucketKey).toBe("config/haiku-t0.3.json");
      expect(result.value.dataset).toBeNull();
    }
  });

  it("extracts the dataset label for question paths", () => {
    const result = parseRequestPath("GET", "/data/question/opinions_qa/q_abortion_1.json");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value).toEqual({
        bucketKey: "question/opinions_qa/q_abortion_1.json",
        dataset: "opinions_qa",
      });
    }
  });

  it("accepts the dataset index", () => {
    const result = parseRequestPath("GET", "/data/question/globalopinionqa/index.json");
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.value.dataset).toBe("globalopinionqa");
  });

  it("accepts HEAD requests", () => {
    const result = parseRequestPath("HEAD", "/data/run/abc.json");
    expect(result.ok).toBe(true);
  });

  it("rejects non-GET/HEAD methods with bad_method", () => {
    for (const method of ["POST", "PUT", "DELETE", "PATCH"]) {
      const result = parseRequestPath(method, "/data/run/abc.json");
      expect(result).toEqual({ ok: false, error: "bad_method" });
    }
  });

  it("rejects paths outside /data/", () => {
    expect(parseRequestPath("GET", "/")).toEqual({ ok: false, error: "not_data_route" });
    expect(parseRequestPath("GET", "/other/run/x.json")).toEqual({
      ok: false,
      error: "not_data_route",
    });
  });

  it("rejects traversal and empty segments", () => {
    for (const path of [
      "/data/",
      "/data/run/",
      "/data/run//abc.json",
      "/data/../secret",
      "/data/run/../config/abc.json",
      "/data/./run/abc.json",
    ]) {
      const result = parseRequestPath("GET", path);
      expect(result.ok).toBe(false);
      if (!result.ok) expect(result.error).toBe("bad_path");
    }
  });

  it("rejects unknown top-level directories", () => {
    const result = parseRequestPath("GET", "/data/secret/thing.json");
    expect(result).toEqual({ ok: false, error: "bad_path" });
  });

  it("rejects backslashes and control characters", () => {
    expect(parseRequestPath("GET", "/data/run/abc\\evil.json").ok).toBe(false);
    expect(parseRequestPath("GET", "/data/run/abc\u0001.json").ok).toBe(false);
  });
});
