// Path parsing for /data/<key> requests. Keeps the Worker's request handler
// free of ad-hoc string surgery and makes the traversal-rejection contract
// unit-testable in isolation (sb-io1).

export interface ParsedKey {
  /** R2 object key, no leading slash. */
  bucketKey: string;
  /** Logical dataset label used in audit logs. `null` for non-question paths. */
  dataset: string | null;
}

export type PathError = "bad_method" | "not_data_route" | "bad_path";

export interface PathResult {
  ok: true;
  value: ParsedKey;
}

export interface PathFailure {
  ok: false;
  error: PathError;
}

const PREFIX = "/data/";

// Mirrors the emission paths in src/synthbench/publish.py (sb-sjs):
//   run/<run_id>.json
//   config/<config_id>.json
//   question/<dataset>/<safe_key>.json
//   question/<dataset>/index.json
// Any path outside these prefixes is rejected so we never accidentally proxy
// unrelated bucket contents (e.g. future private fixtures).
const ALLOWED_TOP_DIRS = new Set(["run", "config", "question"]);

export function parseRequestPath(method: string, pathname: string): PathResult | PathFailure {
  if (method !== "GET" && method !== "HEAD") {
    return { ok: false, error: "bad_method" };
  }
  if (!pathname.startsWith(PREFIX)) {
    return { ok: false, error: "not_data_route" };
  }
  const raw = pathname.slice(PREFIX.length);
  if (!raw) return { ok: false, error: "bad_path" };

  // Reject traversal, absolute-ish paths, and empty segments. We do this on
  // the raw input rather than after normalization so ambiguous inputs like
  // `/data//run/foo.json` or `/data/run/../secret.json` never succeed.
  const segments = raw.split("/");
  for (const seg of segments) {
    if (seg === "" || seg === "." || seg === "..") {
      return { ok: false, error: "bad_path" };
    }
    // Defense-in-depth: backslashes, NULs, and control chars have no business
    // in publish-generated keys. Treat them as bad input rather than trying
    // to normalize.
    if (seg.includes("\\")) {
      return { ok: false, error: "bad_path" };
    }
    for (let i = 0; i < seg.length; i++) {
      if (seg.charCodeAt(i) < 0x20) {
        return { ok: false, error: "bad_path" };
      }
    }
  }

  const top = segments[0];
  if (!top || !ALLOWED_TOP_DIRS.has(top)) {
    return { ok: false, error: "bad_path" };
  }

  const dataset = top === "question" && segments.length >= 2 ? (segments[1] ?? null) : null;
  return { ok: true, value: { bucketKey: raw, dataset } };
}
