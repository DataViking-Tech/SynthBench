export type TopicCategory =
  | "Politics & Governance"
  | "International Relations & Security"
  | "Economy & Work"
  | "Technology & Digital Life"
  | "Media & Information"
  | "Health & Science"
  | "Social Values & Religion"
  | "Identity & Demographics"
  | "Trust & Wellbeing"
  | "General Attitudes";

export interface LeaderboardEntry {
  rank: number;
  /**
   * Canonical config slug (framework--model--t<temp>--tpl<name>--<hash8>).
   * Used to link rows to /config/<id>/. Emitted by publish.py.
   */
  config_id?: string;
  provider: string;
  model: string;
  /**
   * Machine-runnable execution-layer ID: "raw" | "synthpanel" | "ensemble" |
   * "baseline". Unlike `provider`/`model` (display labels), this is stable and
   * parseable — it tells a consumer whether a score reflects a raw model, the
   * SynthPanel product layer, an ensemble, or a statistical baseline. Emitted
   * by publish.py via synthbench.config_id.runnable_ids (sb-7ly).
   */
  provider_id?: string;
  /**
   * Machine-runnable model identifier — an OpenRouter ``<vendor>/<model>`` slug
   * (e.g. "google/gemini-2.5-flash-lite", "meta-llama/llama-3.3-70b-instruct")
   * a consumer can pipe straight to the gateway without parsing display names.
   * Version dates are preserved. See runnable_ids in config_id.py (sb-7ly).
   */
  model_id?: string;
  dataset: string;
  framework: string;

  sps: number;
  /**
   * Position in the meaningful evaluation range: (SPS - P_unconditioned) /
   * (P_ceiling - P_unconditioned). Expressed in [0, ~1]. Present only when a
   * raw-LLM baseline and dataset ceiling are both available. Raw LLMs resolve
   * to 0 (they ARE the unconditioned reference); baselines are omitted.
   */
  normalized_sps?: number;

  p_dist: number;
  p_rank: number;
  p_refuse: number;
  p_cond?: number;
  p_sub?: number;

  jsd: number;
  tau: number;

  n: number;
  samples_per_question?: number;
  temperature?: number;
  /**
   * Reasoning-effort level ("low" | "medium" | "high") threaded to the
   * provider's native reasoning knob. Absent = provider default reasoning
   * behaviour (all pre-effort rows). Treat absence as unknown/default,
   * never as "low".
   */
  effort?: string;
  template?: string;

  /**
   * 95% bootstrap CI on the recomputed `sps` (questions resampled with
   * replacement, full SPS composite recomputed per resample). `null` when
   * a CI cannot be computed (fewer than 5 scored questions) — treat null
   * as unknown, never zero.
   */
  ci_lower: number | null;
  ci_upper: number | null;

  is_baseline: boolean;
  is_ensemble: boolean;

  /**
   * Number of raw result files aggregated into this row — replicates for
   * this exact (model, framework, dataset, temperature, template) config.
   * Emitted by publish.py so the default view can hide under-replicated
   * configs without re-grouping in JS.
   */
  run_count?: number;
  /**
   * Number of distinct datasets this (model, framework, temperature, template)
   * config has runs on. Used for the default view's coverage filter.
   */
  dataset_coverage_count?: number;

  /**
   * Total USD spent on the LLM calls aggregated into this row, computed by
   * publish.py from token_usage × pricing_snapshot. ``null`` for self-hosted,
   * unknown-provider, or pre-tracking rows. See `_compute_cost_fields` in
   * publish.py.
   */
  cost_usd?: number | null;
  /** Cost normalized per 100 questions answered. ``null`` when cost_usd or n is unavailable. */
  cost_per_100q?: number | null;
  /** USD per 1.0 SPS point — only populated when sps ≥ 0.01 to avoid amplification. */
  cost_per_sps_point?: number | null;
  /** True when pricing was estimated (e.g., fallback table) rather than authoritative. */
  is_cost_estimated?: boolean | null;
  /** Total input tokens across all LLM calls aggregated into this row. */
  input_tokens?: number | null;
  /** Total output tokens across all LLM calls aggregated into this row. */
  output_tokens?: number | null;
  /**
   * USD per API call to the underlying model. ``cost_usd / token_usage.call_count``.
   * ``null`` for ensembles (no single underlying response), rows missing
   * token_usage, or unknown-provider rows. See `_compute_cost_fields` in
   * publish.py (sb-293).
   */
  cost_per_response?: number | null;
  /**
   * Average tokens (input + output) per API call. ``null`` when token_usage
   * is unavailable or for ensemble rows. Used as a model-property proxy in
   * the Pareto leaderboard view.
   */
  tokens_per_response?: number | null;
  /**
   * Median per-question latency in seconds, computed by report.py over the
   * runner's per-question timings. ``null`` for pre-instrumentation rows
   * (sb-293).
   */
  latency_p50_seconds?: number | null;
  /** 95th-percentile per-question latency in seconds; see `latency_p50_seconds`. */
  latency_p95_seconds?: number | null;

  topic_scores?: Record<TopicCategory, number>;
  topic_metrics?: Record<TopicCategory, TopicMetricBreakdown>;
  demographic_scores?: DemographicBreakdown[];
  /**
   * Structured per-dimension demographic subgroup scorecard (issue #255,
   * API 1.2.0). Emitted by publish.py on every entry: explicit `null` means
   * the entry has no demographic-conditioned runs (nothing measured); an
   * object means at least one dimension was measured. Prefer this over the
   * flat legacy `demographic_scores` array.
   */
  demographic_scorecard?: DemographicScorecard | null;
  replicates?: ReplicateRun[];

  /**
   * SPS recomputed over the public 80% of the dataset's holdout split.
   * Present only on holdout-enabled datasets with enough per-question rows
   * to compute a subset mean. See `synthbench.private_holdout`.
   */
  sps_public?: number;
  /**
   * SPS recomputed over the private 20% of the dataset's holdout split.
   * The hidden answer key means this score is what our server computes,
   * not what the submitter could fake against public distributions.
   */
  sps_private?: number;
  /** |sps_public − sps_private|. Large values suggest fabrication or contamination. */
  sps_public_private_delta?: number;
  /**
   * Verification badge derived from `sps_public_private_delta` vs
   * `SPS_DIVERGENCE_THRESHOLD` (0.05). "verified" = delta within threshold,
   * "flagged" = delta exceeds threshold (submission warrants review).
   * Absent when the split cannot be computed.
   */
  verification_badge?: "verified" | "flagged";

  /**
   * RESERVED — SPS from a possible future periodic server-side re-eval of
   * this config against the private holdout cut. No pipeline populates
   * this field today; whether the re-eval cron is still wanted is an open
   * design decision (submission-time server-side scoring largely
   * supersedes it — see docs/held-out.md § History). Distinct from
   * `sps_private`, which is computed at publish time for every entry.
   */
  sps_held_out?: number;

  /** |sps − sps_held_out|. Compared against LEADERBOARD_HELD_OUT_DELTA_THRESHOLD. */
  sps_held_out_delta?: number;

  /**
   * RESERVED — ISO 8601 timestamp of the last periodic held-out re-eval
   * for this (config, dataset) pair. No pipeline populates this today.
   */
  held_out_last_run?: string;

  /**
   * RESERVED — trust badge from the periodic held-out re-eval comparison.
   * Distinct from `verification_badge` (publish-time cheat-detector).
   * Derived from `sps_held_out_delta` vs
   * `LEADERBOARD_HELD_OUT_DELTA_THRESHOLD`:
   *   - "verified" — delta within threshold; held-out and public agree
   *   - "flagged"  — delta exceeds threshold; under investigation
   * Absent on every current entry — no re-eval job exists yet.
   */
  held_out_badge?: "verified" | "flagged";
}

export interface TopicMetricBreakdown {
  sps: number;
  n: number;
  p_dist?: number;
  p_rank?: number;
  p_refuse?: number;
}

export interface DemographicBreakdown {
  attribute: string;
  group: string;
  p_dist: number;
  p_cond: number;
  n_questions: number;
}

/** One subgroup cell of the demographic scorecard. */
export interface DemographicScorecardGroup {
  /** Subgroup value, e.g. "Northeast". */
  group: string;
  /** Subgroup p_dist (distributional parity), [0, 1]. */
  score: number;
  /**
   * 95% CI bounds on `score`. Currently always `null` — the source
   * demographic_breakdown blocks carry only point estimates. The keys are
   * stable so consumers can null-check once subgroup bootstrap CIs land.
   * Treat `null` as unknown, never zero.
   */
  ci_lower: number | null;
  ci_upper: number | null;
  /** Questions answered under this subgroup conditioning. */
  n: number;
  /** Conditioning strength vs. the unconditioned baseline (optional). */
  p_cond?: number;
}

/** One measured demographic dimension (attribute) with its subgroup cells. */
export interface DemographicScorecardDimension {
  /** Raw SubPOP attribute code, e.g. "CREGION". */
  attribute: string;
  /** Human-readable dimension name, e.g. "Geography (US Census region)". */
  label: string;
  groups: DemographicScorecardGroup[];
}

/**
 * Structured demographic subgroup scorecard for one leaderboard entry
 * (issue #255). Only dimensions a run actually measured appear — absence of
 * a dimension means "not yet measured", never zero.
 */
export interface DemographicScorecard {
  /** Dataset the subgroup scores came from (e.g. "subpop"). */
  dataset: string;
  dimensions: DemographicScorecardDimension[];
}

export interface ReplicateRun {
  rep: number;
  sps: number;
  p_dist: number;
  p_rank: number;
}

/**
 * Findings block — computed at publish time from leaderboard-results/
 * per-question rows (synthbench.findings, #309). A CI drift guard
 * (tests/test_findings_drift.py) keeps this in lockstep with the artifacts.
 */
export interface FindingsData {
  /** Composite convention every SPS value in this block uses ("sps"). */
  sps_convention: string;
  /** Provenance note for the whole block. */
  generated_from: string;
  temperature_sweep: TemperatureSweepPoint[];
  ensemble_comparison: EnsembleComparison[];
  conditioning_results: ConditioningResult[];
  /** Measured attributes beyond the charted POLPARTY/INCOME/EDUCATION set. */
  conditioning_extended?: ConditioningResult[];
  template_comparison?: TemplateComparisonRow[];
  lever_hierarchy: Lever[];
  /** Human-readable definition of each finding's comparison set. */
  comparison_sets?: Record<string, string>;
  /** Numbers not derivable from committed artifacts, with provenance. */
  asserted_constants?: AssertedConstant[];
  /** Data-quality caveats (e.g. ensembles blending excluded constituents). */
  caveats?: string[];
}

export interface TemperatureSweepPoint {
  model: string;
  temperature: number;
  sps: number;
  std?: number;
  /** Replications aggregated into this cell. */
  n_runs?: number;
  dataset?: string;
}

export interface EnsembleComparison {
  dataset: string;
  best_single_model: string;
  /** Framework of the best single row ("raw" or "product"). */
  best_single_framework?: string;
  best_single_sps: number;
  ensemble_sps: number;
  improvement: number;
  /** Question count the ensemble (and comparison set) was evaluated on. */
  n_questions?: number;
  /** Random-baseline SPS on the same dataset/scale, for anchoring. */
  random_baseline_sps?: number;
  random_baseline_n?: number;
}

export interface ConditioningResult {
  attribute: string;
  group: string;
  /** Original SubPOP group label when `group` is a shortened display form. */
  group_raw?: string;
  p_dist: number;
  p_cond: number;
  p_cond_std?: number;
  n_replications: number;
}

export interface TemplateComparisonRow {
  template: string;
  sps: number;
  std?: number;
  n_runs: number;
}

export interface AssertedConstant {
  name: string;
  value: string;
  source: string;
}

export interface Lever {
  name: string;
  effect_min: number;
  effect_max: number;
  cost: "zero" | "low" | "moderate" | "high";
  status: "done" | "actionable" | "scientific";
  /** Optional qualifier (e.g. why a zero-range lever is still "done"). */
  note?: string;
}

export interface ConvergencePoint {
  model: string;
  dataset: string;
  rep_count: number;
  sps: number;
}

export interface TemporalDriftByYearGap {
  mean_jsd: number;
  n_pairs: number;
}

export interface TemporalDriftFloor {
  mean_drift: number;
  ci_low: number;
  ci_high: number;
  n_pairs: number;
  n_stems: number;
  by_year_gap: Record<string, TemporalDriftByYearGap>;
  method?: string;
}

export interface Baselines {
  temporal_drift?: TemporalDriftFloor;
}

/**
 * Runtime pricing manifest captured by publish.py at publish time (sb-tbm
 * Slice 3). Documents which synthpanel pricing rates were applied to cost
 * fields in this leaderboard build.
 */
export interface PricingSnapshot {
  generated_at: string;
  synth_panel_version: string;
  snapshot_date: string;
  rates: Record<string, number | Record<string, number>>;
}

/**
 * Per-dataset cross-provider JSD matrix. Operationalizes HBR's "trendslop"
 * hypothesis (cross-model consensus without ground truth): the 2-D matrix is
 * pairwise mean JSD between raw-LLM model distributions, symmetric with a
 * zero diagonal; ``mean_cross_model_jsd`` / ``mean_human_jsd`` give the 1-D
 * quadrant summary pair (cross-model agreement vs. ground-truth accuracy).
 */
export interface CrossProviderConcordanceBlock {
  models: string[];
  matrix: (number | null)[][];
  mean_cross_model_jsd: number | null;
  mean_human_jsd: number | null;
}

export type RedistributionPolicy = "full" | "gated" | "aggregates_only" | "citation_only";

/** One row of the dataset policy manifest emitted by publish.py. */
export interface DatasetPolicyEntry {
  name: string;
  redistribution_policy: RedistributionPolicy;
  license_url: string | null;
  citation: string | null;
}

export interface SynthBenchData {
  generated_at: string;
  synthbench_version: string;
  datasets: string[];
  entries: LeaderboardEntry[];
  convergence: ConvergencePoint[];
  findings: FindingsData;
  baselines?: Baselines;
  pricing_snapshot?: PricingSnapshot;
  cross_provider_concordance?: Record<string, CrossProviderConcordanceBlock>;
  /** Per-dataset redistribution policy + provenance. */
  dataset_policies?: DatasetPolicyEntry[];
  /** Runs filtered at publish time as invalid (uniform-garbage etc.). */
  excluded_runs?: ExcludedRun[];
}

/** A run filtered by publish.py's run-validity detector. */
export interface ExcludedRun {
  run_id: string;
  reason: string;
  provider: string | null;
  dataset: string | null;
  samples_per_question: number | null;
  n_evaluated: number | null;
  timestamp: string | null;
  metrics: {
    n_questions: number;
    n_uniform_questions: number;
    uniform_fraction: number;
    refusal_rate: number;
  };
}

/** @deprecated Use SynthBenchData — alias kept for existing component imports */
export type LeaderboardData = SynthBenchData;
