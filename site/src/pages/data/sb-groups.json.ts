import { groupsPayload, payloadHeaders } from "@/lib/sitePayloads";
import type { APIRoute } from "astro";

// Internal payload for /groups (see src/lib/sitePayloads.ts). Not a public API.
export const GET: APIRoute = () => new Response(groupsPayload(), { headers: payloadHeaders });
