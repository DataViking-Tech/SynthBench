// Split-half human ceilings (overall SPS), pinned from the last `synthbench
// publish-data` run that had the raw survey data on disk (leaderboard generated
// 2026-07-20). publish-data omits `baselines.ceiling` when that data is absent,
// which is the case in CI and the Pages build, so synthIndex.ts falls back to
// these. Refresh from `baselines.ceiling[ds].overall` of a full local publish run.

export interface PinnedCeiling {
  mean: number;
  ciLow: number;
  ciHigh: number;
  qualityFlag: string;
}

export const PINNED_CEILINGS: Record<string, PinnedCeiling> = {
  opinionsqa: { mean: 0.999518, ciLow: 0.998559, ciHigh: 0.999953, qualityFlag: "high" },
  subpop: { mean: 0.995346, ciLow: 0.986315, ciHigh: 0.999546, qualityFlag: "medium" },
  globalopinionqa: { mean: 0.997219, ciLow: 0.992431, ciHigh: 0.999536, qualityFlag: "medium" },
};
