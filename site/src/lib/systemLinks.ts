// Build-time only: map a run/config from runs-index.json to the /system/
// profile of its base model, so run and config pages can link back up.
// Imports the full leaderboard, so keep it out of client scripts.

import leaderboardRaw from "@/data/leaderboard.json";
import { buildIndexData, normalizeModelId, systemSlug } from "@/lib/synthIndex";
import type { SynthBenchData } from "@/types/leaderboard";
import type { RunIndexEntry } from "@/types/runs";

export interface SystemLink {
  slug: string;
  name: string;
}

type Entry = Pick<RunIndexEntry, "config_id" | "framework" | "base_provider" | "model">;

let resolver: ((e: Entry) => SystemLink | null) | null = null;

/**
 * Profile of the system a config belongs to: exact config match against the
 * leaderboard first, else the base model (provider/model) for single-model
 * runs. Baselines and unranked ensembles have no profile.
 */
export function systemLinkFor(e: Entry): SystemLink | null {
  if (!resolver) {
    const index = buildIndexData(leaderboardRaw as unknown as SynthBenchData);
    const byConfig = new Map<string, SystemLink>();
    const byBase = new Map<string, SystemLink>();
    for (const c of index.systems) {
      const link = { slug: systemSlug(c.baseId), name: c.base };
      if (c.method !== "baseline" && !byBase.has(c.baseId)) byBase.set(c.baseId, link);
      for (const d of Object.values(c.ds)) {
        if (d.configId && c.method !== "baseline") byConfig.set(d.configId, link);
      }
    }
    resolver = (x) => {
      const hit = byConfig.get(x.config_id);
      if (hit) return hit;
      if (x.framework === "ensemble" || x.framework === "baseline" || !x.base_provider) return null;
      return byBase.get(normalizeModelId(`${x.base_provider}/${x.model}`)) ?? null;
    };
  }
  return resolver(e);
}
