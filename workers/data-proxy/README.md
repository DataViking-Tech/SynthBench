# synthbench data-proxy (Cloudflare Worker)

Worker that enforces the gated-tier access contract introduced in the `cf-gate`
epic. It sits on `api.synthbench.org/data/*`, validates a Supabase-issued JWT,
streams the requested artifact out of the private R2 bucket
(`synthbench-data-prod`, created by sb-sjs), and writes an audit row to
Supabase via a fire-and-forget `ctx.waitUntil`.

Bead: **sb-io1** — [cf-gate] Cloudflare Worker proxy.

## Responsibilities

1. Parse `Authorization: Bearer <jwt>`; reject missing/invalid tokens with 401.
2. Validate JWTs against Supabase's JWKS (cached via `jose`'s
   `createRemoteJWKSet`, which respects the `Cache-Control` headers Supabase
   returns). Checks signature, `iss`, `aud`, and `exp`.
3. Translate `/data/<key>` to an R2 object key, reject traversal.
4. Fetch from the `DATA_BUCKET` R2 binding; 404 on miss.
5. Log access to Supabase `data_access_log` via the REST API using the
   service-role secret — best-effort, errors never block the user response.
6. Return the JSON object with `Cache-Control: private, max-age=60` plus CORS
   headers for the configured synthbench origins.

Rate limiting is enforced by a Cloudflare Rulesets rate-limit rule on the
route (e.g. 100 req/min per JWT `sub`). That is configured out-of-band in the
Cloudflare dashboard, not in this Worker — see *Rate limiting* below.

## Environment

Bindings and vars are declared in `wrangler.toml`; secrets are set with
`wrangler secret put`.

| Name                         | Kind    | Purpose                                                               |
| ---------------------------- | ------- | --------------------------------------------------------------------- |
| `DATA_BUCKET`                | R2      | Private bucket created by sb-sjs (`synthbench-data-prod`).            |
| `SUPABASE_URL`               | var     | e.g. `https://<project>.supabase.co`. Used for JWKS + REST endpoints. |
| `SUPABASE_JWT_AUD`           | var     | Expected `aud` claim. Supabase issues `authenticated`.                |
| `ALLOWED_ORIGINS`            | var     | Comma-separated list of allowed browser origins for CORS.             |
| `SUPABASE_SERVICE_ROLE_KEY`  | secret  | Server-only key used to INSERT audit rows. **Never expose to client.**|

### Local dev

```bash
npm install
cp .dev.vars.example .dev.vars   # fill in SUPABASE_SERVICE_ROLE_KEY
npm run dev                      # wrangler dev, uses preview R2 bucket
```

### Deploy

```bash
npm run deploy                   # prod
npm run deploy -- --env preview  # preview (matches sb-sjs preview bucket)
```

## Path contract

The Worker mirrors the key layout emitted by `publish.py` (sb-sjs):

| Request path                         | R2 key                          |
| ------------------------------------ | ------------------------------- |
| `/data/run/<run_id>.json`            | `run/<run_id>.json`             |
| `/data/config/<config_id>.json`      | `config/<config_id>.json`       |
| `/data/question/<dataset>/<key>.json`| `question/<dataset>/<key>.json` |
| `/data/question/<dataset>/index.json`| `question/<dataset>/index.json` |

Traversal (`..`) and absolute keys are rejected with 400.

## Tests

```bash
npm test
```

Unit coverage includes CORS handling, path parsing, JWT validation happy/sad
paths against an in-process JWKS (signed with a locally-generated ES256 key),
and the audit-log fire-and-forget semantics. An integration test against a
live preview Worker is intentionally left as a manual verification step —
`wrangler dev` + a real Supabase JWT.

## Rate limiting

Configure a **Cloudflare Rulesets** rate-limit rule on the
`api.synthbench.org/data/*` route:

- **Match**: `http.request.uri.path starts_with "/data/"`
- **Counting**: `http.request.headers["authorization"][0]` (or JA3 fingerprint
  if unauthenticated)
- **Threshold**: 100 requests / 60 seconds
- **Action**: Managed Challenge or Block

This stays out of the Worker so we can tune aggressiveness without redeploys
and so the rule is visible alongside the rest of our WAF config.

## Out of scope

- Frontend integration — sb-sj6 wires the Astro UI to call this Worker.
- Audit dashboard — a separate bead reads `data_access_log` for ops visibility.
- Billing/quota enforcement — the audit log is the source of truth if we add
  per-user limits later.
