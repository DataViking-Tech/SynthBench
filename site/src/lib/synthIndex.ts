// SynthBench Index v1: re-expresses each published SPS on a scale anchored to
// two reference points, per dataset:
//
//   Index_d = 100 * (SPS - SPS_random) / (ceiling - SPS_random)
//
// 0 means the system matches the human answer distribution no better than
// uniform random answers; 100 means it matches as well as a second, independent
// half of the human panel (split-half ceiling). The headline Index averages the
// core datasets. Computed at build time from leaderboard.json, so the site never
// disagrees with the published SPS values it is derived from.

import type { LeaderboardEntry, SynthBenchData } from "@/types/leaderboard";
import { PINNED_CEILINGS } from "./ceilings";

export const CORE_DATASETS = ["opinionsqa", "subpop", "globalopinionqa"] as const;
export const ALL_DATASETS = [...CORE_DATASETS, "gss"] as const;

export type Method = "raw" | "althing" | "ensemble" | "baseline";

export interface DatasetMeta {
  id: string;
  label: string;
  population: string;
  core: boolean;
  questions: number;
  random: number;
  majority: number | null;
  majorityIdx: number | null;
  ceiling: number | null;
  /** True when no split-half ceiling is published and 1.0 is assumed. */
  ceilingAssumed: boolean;
  /** Quality flag of the published ceiling ("high", "medium", ...). */
  ceilingQuality: string | null;
}

export interface DatasetScore {
  sps: number;
  idx: number;
  lo: number | null;
  hi: number | null;
  pDist: number;
  pRank: number;
  pRefuse: number;
  n: number;
  runs: number | null;
  samplesPerQuestion: number | null;
  cost100: number | null;
  latencyP50: number | null;
  badge: "verified" | "flagged" | null;
  /** |public - private| SPS on the holdout split. */
  holdoutGap: number | null;
  topicIdx: Record<string, number>;
  topicN: Record<string, number>;
  configId: string | null;
}

export interface SystemConfig {
  key: string;
  /** Display name of the base model ("Claude Haiku 4.5"), or "Althing Ensemble". */
  base: string;
  /** Machine id of the base model, or "ensemble" / the baseline id. */
  baseId: string;
  lab: string;
  method: Method;
  /** Non-default settings (temperature, prompt template), or null. */
  variant: string | null;
  /**
   * Agent CLI the runs went through ("claude-code", "codex"), or null for
   * direct API calls. A tag on the row, not a variant: harness runs are
   * still ranked, under the vendor's model and lab.
   */
  harness: string | null;
  ds: Record<string, DatasetScore>;
  coverage: number;
  index: number | null;
  indexLo: number | null;
  indexHi: number | null;
  cost100: number | null;
  latencyP50: number | null;
  flagged: number;
  runs: number;
}

export interface IndexData {
  generated: string;
  version: string;
  excludedRuns: number;
  datasets: DatasetMeta[];
  systems: SystemConfig[];
  references: { random: SystemConfig; majority: SystemConfig | null };
  findings: SynthBenchData["findings"];
  concordance: SynthBenchData["cross_provider_concordance"] | null;
}

const LABELS: Record<string, [string, string]> = {
  opinionsqa: ["OpinionsQA", "US adults (Pew American Trends Panel)"],
  subpop: ["SubPOP", "22 US subpopulations"],
  globalopinionqa: ["GlobalOpinionQA", "Cross-national (Pew Global Attitudes, WVS)"],
  gss: ["GSS", "US adults (General Social Survey)"],
};

const LAB_BY_PREFIX: Record<string, string> = {
  anthropic: "Anthropic",
  openai: "OpenAI",
  google: "Google",
  "meta-llama": "Meta",
};

const BASE_NAMES: Record<string, string> = {
  "anthropic/claude-haiku-4-5": "Claude Haiku 4.5",
  "anthropic/claude-haiku-5-5": "Claude Haiku 5.5",
  "openai/gpt-6-luna": "GPT-6 Luna",
  "anthropic/claude-sonnet-4": "Claude Sonnet 4",
  "anthropic/claude-sonnet-4.6": "Claude Sonnet 4.6",
  "openai/gpt-4o-mini": "GPT-4o mini",
  "openai/gpt-4o": "GPT-4o",
  "google/gemini-2.5-flash": "Gemini 2.5 Flash",
  "google/gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite",
  "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
};

type CeilingBlock = Record<string, { overall?: { mean?: number; quality_flag?: string } }>;

function methodOf(e: LeaderboardEntry): Method {
  if (e.is_baseline) return "baseline";
  if (e.is_ensemble) return "ensemble";
  return e.provider_id === "synthpanel" || e.provider_id === "althing" || e.framework === "product"
    ? "althing"
    : "raw";
}

function round(v: number, digits = 1): number {
  const f = 10 ** digits;
  return Math.round(v * f) / f;
}

function mean(xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

/** Fallback display name for model ids not in BASE_NAMES. */
function prettyModel(id: string): string {
  const tail = id.split("/").pop() ?? id;
  return tail.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function buildIndexData(raw: SynthBenchData): IndexData {
  const entries = raw.entries;
  const ceilings = ((raw.baselines as unknown as { ceiling?: CeilingBlock })?.ceiling ??
    {}) as CeilingBlock;
  const randomSps: Record<string, number> = {};
  const majoritySps: Record<string, number> = {};
  const questions: Record<string, number> = {};
  for (const e of entries) {
    if (e.model_id === "random-baseline") randomSps[e.dataset] = e.sps;
    if (e.model_id === "majority-baseline") majoritySps[e.dataset] = e.sps;
    questions[e.dataset] = Math.max(questions[e.dataset] ?? 0, e.n);
  }
  // publish-data omits ceilings when the raw survey data isn't on disk (CI,
  // Pages builds), so fall back to the pinned values in lib/ceilings.ts.
  const pinned = PINNED_CEILINGS;
  const ceilingOf = (ds: string): number | null =>
    ceilings[ds]?.overall?.mean ?? pinned[ds]?.mean ?? null;
  const qualityOf = (ds: string): string | null =>
    ceilings[ds]?.overall?.quality_flag ?? pinned[ds]?.qualityFlag ?? null;
  const toIdx = (ds: string, v: number | null | undefined): number | null => {
    if (v == null || randomSps[ds] == null) return null;
    const c = ceilingOf(ds) ?? 1;
    return round((100 * (v - randomSps[ds])) / (c - randomSps[ds]));
  };

  const byKey = new Map<string, SystemConfig>();
  for (const e of entries) {
    if (randomSps[e.dataset] == null) continue;
    const method = methodOf(e);
    const variantParts: string[] = [];
    if (e.temperature != null) variantParts.push(`temperature ${e.temperature}`);
    if (e.template && e.template !== "current") variantParts.push(`${e.template} template`);
    if (e.effort) variantParts.push(`${e.effort} effort`);
    if (e.persona_pack) variantParts.push(`${e.persona_pack} personas`);
    const modelId = e.model_id ?? e.model;
    const key = [
      method,
      modelId,
      e.temperature ?? "default",
      e.template ?? "current",
      e.effort ?? "",
      e.persona_pack ?? "",
      e.harness ?? "",
    ].join("|");
    const prefix = modelId.includes("/") ? modelId.split("/")[0] : "";
    let base: string;
    if (method === "ensemble") base = "Althing Ensemble";
    else if (method === "baseline")
      base = modelId === "random-baseline" ? "Random answers" : "Majority answer";
    else base = BASE_NAMES[modelId] ?? prettyModel(modelId);
    let cfg = byKey.get(key);
    if (!cfg) {
      cfg = {
        key,
        base,
        baseId: method === "ensemble" ? "ensemble" : modelId,
        lab: method === "ensemble" ? "DataViking" : (LAB_BY_PREFIX[prefix] ?? "Other"),
        method,
        variant: variantParts.length ? variantParts.join(", ") : null,
        harness: e.harness ?? null,
        ds: {},
        coverage: 0,
        index: null,
        indexLo: null,
        indexHi: null,
        cost100: null,
        latencyP50: null,
        flagged: 0,
        runs: 0,
      };
      byKey.set(key, cfg);
    }
    const ds = e.dataset;
    const topicIdx: Record<string, number> = {};
    const topicN: Record<string, number> = {};
    for (const [topic, m] of Object.entries(e.topic_metrics ?? {})) {
      const v = toIdx(ds, m.sps);
      if (v != null) {
        topicIdx[topic] = v;
        topicN[topic] = m.n;
      }
    }
    cfg.ds[ds] = {
      sps: e.sps,
      idx: toIdx(ds, e.sps) ?? 0,
      lo: toIdx(ds, e.ci_lower),
      hi: toIdx(ds, e.ci_upper),
      pDist: e.p_dist,
      pRank: e.p_rank,
      pRefuse: e.p_refuse,
      n: e.n,
      runs: e.run_count ?? null,
      samplesPerQuestion: e.samples_per_question ?? null,
      cost100: e.cost_per_100q ?? null,
      latencyP50: e.latency_p50_seconds ?? null,
      badge: e.verification_badge ?? null,
      holdoutGap: e.sps_public_private_delta ?? null,
      topicIdx,
      topicN,
      configId: e.config_id ?? null,
    };
  }

  for (const c of byKey.values()) {
    const core = CORE_DATASETS.filter((d) => c.ds[d]);
    c.coverage = core.length;
    if (core.length) {
      c.index = round(mean(core.map((d) => c.ds[d].idx)));
      // Interval: datasets treated as independent; per-dataset bootstrap
      // half-widths combine as sqrt(sum w^2) / k.
      const widths = core.map((d) => {
        const s = c.ds[d];
        return s.lo != null && s.hi != null ? (s.hi - s.lo) / 2 : null;
      });
      if (widths.every((w) => w != null)) {
        const half = Math.sqrt((widths as number[]).reduce((a, w) => a + w * w, 0)) / core.length;
        c.indexLo = round(c.index - half);
        c.indexHi = round(c.index + half);
      }
    }
    const scores = Object.values(c.ds);
    const costs = scores.map((s) => s.cost100).filter((v): v is number => v != null);
    c.cost100 = costs.length ? round(mean(costs), 4) : null;
    const lats = scores.map((s) => s.latencyP50).filter((v): v is number => v != null);
    c.latencyP50 = lats.length ? round(mean(lats), 2) : null;
    c.flagged = scores.filter((s) => s.badge === "flagged").length;
    c.runs = scores.reduce((a, s) => a + (s.runs ?? 0), 0);
  }

  const all = [...byKey.values()];
  const random = all.find((c) => c.baseId === "random-baseline");
  if (!random) throw new Error("synthIndex: leaderboard.json has no random-baseline entries");
  const majority = all.find((c) => c.baseId === "majority-baseline") ?? null;

  const datasets: DatasetMeta[] = ALL_DATASETS.filter((d) => randomSps[d] != null).map((d) => ({
    id: d,
    label: LABELS[d]?.[0] ?? d,
    population: LABELS[d]?.[1] ?? "",
    core: (CORE_DATASETS as readonly string[]).includes(d),
    questions: questions[d] ?? 0,
    random: randomSps[d],
    majority: majoritySps[d] ?? null,
    majorityIdx: toIdx(d, majoritySps[d]),
    ceiling: ceilingOf(d),
    ceilingAssumed: ceilingOf(d) == null,
    ceilingQuality: qualityOf(d),
  }));

  return {
    generated: raw.generated_at,
    version: raw.synthbench_version,
    excludedRuns: raw.excluded_runs?.length ?? 0,
    datasets,
    systems: all
      .filter((c) => c.method !== "baseline")
      .sort((a, b) => (b.index ?? -999) - (a.index ?? -999)),
    references: { random, majority },
    findings: raw.findings,
    concordance: raw.cross_provider_concordance ?? null,
  };
}

/** URL slug for a base model's profile page. */
export function systemSlug(baseId: string): string {
  return baseId
    .replace(/[^a-z0-9]+/gi, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase();
}
