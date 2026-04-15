// Audit log writer. Every authenticated R2 fetch gets a row in
// `public.data_access_log` on Supabase (table + RLS provisioned by sb-8o4).
// We use the service-role REST API so writes succeed under the table's
// RLS policy ("INSERT-only by service role").
//
// The writer is fire-and-forget from the caller's perspective (wrapped in
// ctx.waitUntil). Failures are logged via `console.warn` but never block the
// data response — an unavailable Supabase would otherwise take the gated
// dataset offline, which is worse than missing audit coverage for a few
// minutes of logs.

export interface AuditEntry {
  userId: string;
  dataset: string | null;
  artifactPath: string;
  requestIp: string | null;
  userAgent: string | null;
}

export interface AuditConfig {
  supabaseUrl: string;
  serviceRoleKey: string;
  /** Injection seam for tests. Defaults to global fetch. */
  fetchImpl?: typeof fetch;
}

/** Extracts the best-effort client IP for an inbound Worker request. */
export function clientIpFor(request: Request): string | null {
  // CF-Connecting-IP is the canonical client IP on Workers, populated by the
  // Cloudflare edge. `x-forwarded-for` is a fallback for local dev where
  // there's no edge in front. Neither is guaranteed — fall through to null.
  const cfIp = request.headers.get("CF-Connecting-IP");
  if (cfIp) return cfIp;
  const xff = request.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0]?.trim() || null;
  return null;
}

export async function writeAuditLog(entry: AuditEntry, config: AuditConfig): Promise<void> {
  const url = `${config.supabaseUrl.replace(/\/+$/, "")}/rest/v1/data_access_log`;
  const body = JSON.stringify({
    user_id: entry.userId,
    dataset: entry.dataset,
    artifact_path: entry.artifactPath,
    request_ip: entry.requestIp,
    user_agent: entry.userAgent,
  });
  const doFetch = config.fetchImpl ?? fetch;
  try {
    const res = await doFetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: config.serviceRoleKey,
        Authorization: `Bearer ${config.serviceRoleKey}`,
        // Tell PostgREST we don't need the inserted row echoed back — saves
        // both a round trip on our side and RLS overhead on Supabase's.
        Prefer: "return=minimal",
      },
      body,
    });
    if (!res.ok) {
      console.warn(`[data-proxy] audit log write failed: ${res.status} ${res.statusText}`);
    }
  } catch (err) {
    console.warn(`[data-proxy] audit log write error: ${(err as Error).message}`);
  }
}
