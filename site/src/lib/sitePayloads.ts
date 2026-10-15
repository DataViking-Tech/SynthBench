// Build-time JSON payloads for the Index pages' client scripts. They used to
// be inlined into every page (~210 KB for the Index data, ~90 KB more on
// /groups); now each is emitted once as a static file under /data/ (see
// src/pages/data/sb-*.json.ts) and fetched by src/scripts/sb/boot.ts, so the
// browser downloads and caches it once per deploy.
//
// These are internal site payloads, not a public API: no stability contract
// (use /data/leaderboard.json for that). The `?v=` content hash in the URL
// busts the 1-hour /data/* browser cache when the data changes.
import { createHash } from "node:crypto";
import groupData from "@/data/group-alignment.json";
import leaderboardRaw from "@/data/leaderboard.json";
import { buildIndexData, systemSlug } from "@/lib/synthIndex";
import type { SynthBenchData } from "@/types/leaderboard";

const rawBase = import.meta.env.BASE_URL || "/";
const base = rawBase.endsWith("/") ? rawBase : `${rawBase}/`;

let indexJson: string | null = null;
let groupsJson: string | null = null;

/** The Index data read back by model.ts `data()`. */
export function indexPayload(): string {
  if (indexJson == null) {
    const index = buildIndexData(leaderboardRaw as unknown as SynthBenchData);
    const slugs = Object.fromEntries(index.systems.map((c) => [c.baseId, systemSlug(c.baseId)]));
    indexJson = JSON.stringify({ ...index, base, slugs });
  }
  return indexJson;
}

/** Per-group match data for src/scripts/sb/pages/groups.ts. */
export function groupsPayload(): string {
  if (groupsJson == null) groupsJson = JSON.stringify(groupData);
  return groupsJson;
}

const version = (json: string) => createHash("sha1").update(json).digest("hex").slice(0, 10);

export const indexPayloadUrl = (): string =>
  `${base}data/sb-index.json?v=${version(indexPayload())}`;
export const groupsPayloadUrl = (): string =>
  `${base}data/sb-groups.json?v=${version(groupsPayload())}`;

export const payloadHeaders = {
  "Content-Type": "application/json; charset=utf-8",
  // Mirrors the /data/* rule in public/_headers, which wins on Cloudflare Pages.
  "Cache-Control": "public, max-age=3600, s-maxage=21600, stale-while-revalidate=86400",
};
