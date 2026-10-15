import { indexPayload, payloadHeaders } from "@/lib/sitePayloads";
import type { APIRoute } from "astro";

// Internal payload for the Index pages (see src/lib/sitePayloads.ts). Not a
// public API; use /data/leaderboard.json instead.
export const GET: APIRoute = () => new Response(indexPayload(), { headers: payloadHeaders });
