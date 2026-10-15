// One vocabulary for the whole site: display names of datasets, models,
// methods, systems and metrics, plus the SPS -> Index transform. Pure (no data
// imports), so both build-time Astro code and client scripts can use it.
//
// Naming rules:
//   * A single-model system is "<model>[ via <harness>], <method short>
//     [(<variant>)]", e.g. "Claude Haiku 4.5, persona", "GPT-6 Luna via codex, raw".
//     Its short name is the model's short name plus the harness tag
//     ("Haiku 4.5", "GPT-6 Luna via codex"); the method is shown beside it.
//   * An ensemble is "Ensemble of A (persona), B (raw), ..." (or "(all raw)"
//     when every member shares a method); short "A + B + C[, raw]" using each
//     member's family word. Ensembles get no lab logo.
//   * Model short names only drop the "Claude " prefix, so versions stay
//     visible ("Gemini 2.5 Flash-Lite" vs "Gemini 3.5 Flash-Lite").
//   * Datasets have one name (OpinionsQA, SubPOP, GSS, GlobalOpinionQA, NTIA)
//     and a population subtitle ("US adults") used only as secondary text.
//   * Scores lead with the SynthBench Index (0 = random answers, 100 = real
//     people); SPS (0 to 1) is secondary.

export const SITE_NAME = "SynthBench";
/** Every page title is "<page> · SynthBench" (the homepage passes its own). */
export const pageTitle = (title: string): string =>
  title === SITE_NAME || title.startsWith(`${SITE_NAME}:`) ? title : `${title} · ${SITE_NAME}`;

// ---------- Datasets ----------

export interface DatasetName {
  name: string;
  /** Short population subtitle, secondary to the name. */
  audience: string;
  /** Longer source description. */
  population: string;
}

export const DATASET_NAMES: Record<string, DatasetName> = {
  opinionsqa: {
    name: "OpinionsQA",
    audience: "US adults",
    population: "US adults (Pew American Trends Panel)",
  },
  subpop: { name: "SubPOP", audience: "22 US groups", population: "22 US subpopulations" },
  gss: { name: "GSS", audience: "US adults", population: "US adults (General Social Survey)" },
  globalopinionqa: {
    name: "GlobalOpinionQA",
    audience: "Cross-national",
    population: "Cross-national (Pew Global Attitudes, WVS)",
  },
  ntia: { name: "NTIA", audience: "US adults", population: "US adults (NTIA Internet Use Survey)" },
};

/** "globalopinionqa", "ntia (Nov 2023)" -> dataset id without wave suffix. */
export const datasetId = (id: string): string => id.split(" ", 1)[0].toLowerCase();
export const datasetName = (id: string): string => DATASET_NAMES[datasetId(id)]?.name ?? id;
export const datasetAudience = (id: string): string => DATASET_NAMES[datasetId(id)]?.audience ?? "";
export const datasetPopulation = (id: string): string =>
  DATASET_NAMES[datasetId(id)]?.population ?? "";

// ---------- Methods ----------

export type MethodId = "raw" | "althing" | "ensemble" | "baseline";

export const METHOD_NAMES: Record<MethodId, { label: string; short: string }> = {
  raw: { label: "Raw LLM", short: "raw" },
  althing: { label: "Althing persona", short: "persona" },
  ensemble: { label: "Ensemble", short: "ensemble" },
  baseline: { label: "Baseline", short: "baseline" },
};

/**
 * Method of a run from its framework string. "synthpanel" is Althing's name
 * before the rename, "product" its leaderboard framework tag; "openrouter" is a
 * raw call routed through OpenRouter.
 */
export function methodOf(
  framework: string | null | undefined,
  opts: { ensemble?: boolean; baseline?: boolean; label?: string } = {},
): MethodId {
  if (opts.baseline || framework === "baseline") return "baseline";
  if (opts.ensemble || framework === "ensemble" || /^Ensemble\b/.test(opts.label ?? ""))
    return "ensemble";
  if (framework === "althing" || framework === "synthpanel" || framework === "product")
    return "althing";
  return "raw";
}

// ---------- Models ----------

/** Canonical display name per model id (vendor/model, undated). */
export const MODEL_NAMES: Record<string, string> = {
  "anthropic/claude-haiku-4-5": "Claude Haiku 4.5",
  "anthropic/claude-haiku-5-5": "Claude Haiku 5.5",
  "anthropic/claude-sonnet-4": "Claude Sonnet 4",
  "anthropic/claude-sonnet-4-6": "Claude Sonnet 4.6",
  "anthropic/claude-sonnet-5-5": "Claude Sonnet 5.5",
  "openai/gpt-6-luna": "GPT-6 Luna",
  "openai/gpt-4o-mini": "GPT-4o mini",
  "openai/gpt-4o": "GPT-4o",
  "google/gemini-2.5-flash": "Gemini 2.5 Flash",
  "google/gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite",
  "google/gemini-3.8-flash": "Gemini 3.8 Flash",
  "google/gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite",
  "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
  "meta/muse-glimmer-30b": "Muse Glimmer 30B",
  "deepseek/deepseek-v4.1-flash": "DeepSeek V4.1 Flash",
  "qwen/qwen3.8-flash": "Qwen 3.8 Flash",
  "random-baseline": "Random answers",
  "majority-baseline": "Majority answer",
};

/**
 * Older display names that name the same model (run files keep the name
 * they were published under).
 */
const MODEL_ALIASES: Record<string, string> = {
  "gemini flash lite": "Gemini 2.5 Flash-Lite",
  "gpt-4o-mini": "GPT-4o mini",
  "random baseline": "Random answers",
  "majority baseline": "Majority answer",
};

/**
 * model_id keeps vendor version dates (claude-haiku-4-5-20251001) so it stays
 * runnable; dated and undated ids are the same model here, as are
 * OpenRouter's dotted Anthropic versions (claude-sonnet-4.6).
 */
export function normalizeModelId(id: string): string {
  const undated = id.replace(/-\d{8}$/, "");
  return undated.startsWith("anthropic/") ? undated.replace(/\./g, "-") : undated;
}

/** Vendor-less, dot-free key: "anthropic/claude-haiku-4.5" -> "claude-haiku-4-5". */
const slugKey = (id: string): string =>
  (id.split("/").pop() ?? id)
    .toLowerCase()
    .replace(/-\d{8}$/, "")
    .replace(/\./g, "-");
const BY_SLUG = new Map<string, string>(
  Object.keys(MODEL_NAMES).map((id) => [slugKey(id), id] as [string, string]),
);

/**
 * Canonical model id for display and grouping. Accepts vendor-prefixed or bare
 * ids, dated or dotted versions ("claude-haiku-4.5", "claude-haiku-4-5",
 * "anthropic/claude-haiku-4-5-20251001" all give "anthropic/claude-haiku-4-5").
 * Display only: config ids are never rewritten.
 */
export function canonicalModelId(id: string): string {
  return BY_SLUG.get(slugKey(id)) ?? normalizeModelId(id);
}

/** Fallback display name for model ids not in MODEL_NAMES. */
function prettyModel(id: string): string {
  const tail = id.split("/").pop() ?? id;
  return tail.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Canonical display name of a model id. */
export const modelName = (id: string): string =>
  MODEL_NAMES[canonicalModelId(id)] ?? prettyModel(id);

/** Canonical display name from a free-form name ("Haiku 4.5", "Gemini Flash Lite"). */
export function modelNameFromLabel(label: string): string {
  const t = label.trim();
  const alias = MODEL_ALIASES[t.toLowerCase()];
  if (alias) return alias;
  const names = Object.values(MODEL_NAMES);
  return (
    names.find((n) => n === t) ??
    names.find((n) => n === `Claude ${t}`) ??
    names.find((n) => n.toLowerCase() === t.toLowerCase()) ??
    t
  );
}

/** Short model name: drops only the "Claude " prefix, so versions stay visible. */
export const modelShortName = (name: string): string => name.replace(/^Claude /, "");

/** One word per model for ensemble short names ("Haiku", "Gemini", "GPT-4o mini"). */
function familyWord(name: string): string {
  const short = modelShortName(name);
  return /^GPT-/.test(short) ? short : short.split(" ")[0];
}

// ---------- Ensembles ----------

export interface EnsembleMember {
  name: string;
  method: MethodId;
}

/**
 * Members of an ensemble from its published label:
 *   "Ensemble: A (Althing), B, C"   mixed (untagged members are raw)
 *   "Ensemble: A, B, C (raw)"       one method for all members
 */
export function parseEnsemble(label: string): EnsembleMember[] | null {
  const m = label.match(/^Ensemble:\s*(.*)$/);
  if (!m) return null;
  let body = m[1].trim();
  let all: MethodId | null = null;
  const tail = body.match(/^(.*\S)\s+\((raw|Althing|althing|persona)\)$/);
  const parts0 = body.split(", ");
  // A trailing tag applies to everyone only when no other member is tagged.
  if (tail && !parts0.slice(0, -1).some((p) => /\(\w+\)$/.test(p))) {
    body = tail[1];
    all = tail[2] === "raw" ? "raw" : "althing";
  }
  return body.split(", ").map((p) => {
    const t = p.match(/^(.*?)\s+\((raw|Althing|althing|persona)\)$/);
    const name = modelNameFromLabel(t ? t[1] : p);
    const method: MethodId = t ? (t[2] === "raw" ? "raw" : "althing") : (all ?? "raw");
    return { name, method };
  });
}

/** Canonical full and short names of an ensemble from its published label. */
export function ensembleNames(label: string): { full: string; short: string } {
  const members = parseEnsemble(label);
  if (!members?.length) return { full: label, short: label };
  const methods = new Set(members.map((m) => m.method));
  const uniform = methods.size === 1 ? members[0].method : null;
  const list = members
    .map((m) => `${modelShortName(m.name)}${uniform ? "" : ` (${METHOD_NAMES[m.method].short})`}`)
    .join(", ");
  const full = `Ensemble of ${list}${uniform ? ` (all ${METHOD_NAMES[uniform].short})` : ""}`;
  const short = `${members.map((m) => familyWord(m.name)).join(" + ")}${uniform ? `, ${METHOD_NAMES[uniform].short}` : ""}`;
  return { full, short };
}

// ---------- Systems ----------

/** Non-default settings of a run, or null. Same wording on every page. */
export function variantLabel(v: {
  temperature?: number | null;
  template?: string | null;
  effort?: string | null;
  persona_pack?: string | null;
}): string | null {
  const parts: string[] = [];
  if (v.temperature != null) parts.push(`temperature ${v.temperature}`);
  if (v.template && v.template !== "current") parts.push(`${v.template} template`);
  if (v.effort) parts.push(`${v.effort} effort`);
  if (v.persona_pack) parts.push(`${v.persona_pack} personas`);
  return parts.length ? parts.join(", ") : null;
}

/** "via codex": the agent CLI a run went through, or "" for direct API calls. */
export const harnessTag = (harness: string | null | undefined): string =>
  harness ? `via ${harness}` : "";

export interface SystemNameParts {
  /** Canonical model name, or the ensemble's published label. */
  base: string;
  method: MethodId;
  harness?: string | null;
  variant?: string | null;
}

export function systemFullName(p: SystemNameParts): string {
  if (p.method === "ensemble") return ensembleNames(p.base).full;
  const via = p.harness ? ` ${harnessTag(p.harness)}` : "";
  const method = p.method === "baseline" ? "" : `, ${METHOD_NAMES[p.method].short}`;
  return `${p.base}${via}${method}${p.variant ? ` (${p.variant})` : ""}`;
}

/** Short name without the method (charts show the method by colour). */
export function systemShortName(p: SystemNameParts): string {
  if (p.method === "ensemble") return ensembleNames(p.base).short;
  return `${modelShortName(p.base)}${p.harness ? ` ${harnessTag(p.harness)}` : ""}`;
}

/** Harness from an explicit field or the "harness=<name>" token in a run or provider id. */
export function harnessOf(...sources: (string | null | undefined)[]): string | null {
  for (const s of sources) {
    if (!s) continue;
    const m = s.match(/harness=([A-Za-z][A-Za-z-]*)/);
    if (m) return m[1];
  }
  return null;
}

/**
 * Canonical name of a published run, config or per-question row. Works from
 * the fields every run artifact carries (display name, model, framework).
 */
export function runSystem(r: {
  display_name?: string | null;
  model?: string | null;
  framework?: string | null;
  base_provider?: string | null;
  config_id?: string | null;
  run_id?: string | null;
  harness?: string | null;
  is_ensemble?: boolean;
  is_baseline?: boolean;
  temperature?: number | null;
  template?: string | null;
  effort?: string | null;
  persona_pack?: string | null;
}): SystemNameParts & { full: string; short: string; modelKey: string } {
  const label = r.display_name || r.model || "";
  const method = methodOf(r.framework, {
    ensemble: r.is_ensemble || r.config_id?.startsWith("ensemble--"),
    baseline: r.is_baseline || r.config_id?.startsWith("baseline--"),
    label,
  });
  let base: string;
  let modelKey: string;
  if (method === "ensemble") {
    base = /^Ensemble\b/.test(label) ? label : (r.model ?? label);
    modelKey = `ensemble:${r.model ?? label}`;
  } else {
    // config ids are "<method>--<model slug>--...", the most reliable model key.
    const slug = r.config_id?.split("--")[1];
    const fromModel = r.model && !/^Althing \(|^Ensemble/.test(r.model) ? r.model : null;
    const id = slug ?? fromModel;
    if (id && BY_SLUG.has(slugKey(id))) {
      modelKey = canonicalModelId(id);
      base = modelName(id);
    } else {
      const inner = label.match(/^Althing \((.*)\)$/)?.[1] ?? label;
      base = modelNameFromLabel(inner);
      modelKey = id ? canonicalModelId(id) : base;
    }
  }
  const harness = r.harness ?? harnessOf(r.run_id, r.base_provider);
  const parts: SystemNameParts = { base, method, harness, variant: variantLabel(r) };
  return {
    ...parts,
    full: systemFullName(parts),
    short: systemShortName(parts),
    modelKey,
  };
}

// ---------- Metrics ----------

export interface MetricName {
  /** Plain-English label, shown first. */
  label: string;
  /** Technical name, shown second (never upper-cased: it may contain τ). */
  tech: string;
  /** One-line explanation for tooltips. */
  desc: string;
}

export const METRIC_NAMES = {
  index: {
    label: "SynthBench Index",
    tech: "0 = random answers, 100 = real people",
    desc: "SPS rescaled per dataset: 0 matches uniform random answers, 100 matches a second half of the real survey panel.",
  },
  sps: {
    label: "Survey Parity Score",
    tech: "SPS, 0 to 1",
    desc: "Mean of shares, order and refusal match, from 0 to 1. The Index rescales it so random answers score 0 and real people 100.",
  },
  pDist: {
    label: "Shares match",
    tech: "p_dist = 1 − mean JSD",
    desc: "How closely answer shares match people's: 1 minus the mean Jensen-Shannon divergence.",
  },
  pRank: {
    label: "Order match",
    tech: "p_rank = (1 + Kendall τ) ÷ 2",
    desc: "Whether the options are ranked in the same order as people rank them.",
  },
  pRefuse: {
    label: "Refusal match",
    tech: "p_refuse",
    desc: "How closely refusal and don't-know rates match people.",
  },
  pCond: {
    label: "Persona effect",
    tech: "p_cond",
    desc: "How far naming a group in the prompt moves answers toward that group.",
  },
  pSub: {
    label: "Group evenness",
    tech: "p_sub",
    desc: "How evenly the match holds across demographic groups.",
  },
  jsd: {
    label: "Distribution gap",
    tech: "mean JSD, lower is better",
    desc: "Mean Jensen-Shannon divergence between the system's and people's answer shares. 0 means identical.",
  },
  tau: {
    label: "Rank agreement",
    tech: "Kendall τ, −1 to 1",
    desc: "Mean Kendall τ between the system's and people's option rankings.",
  },
} satisfies Record<string, MetricName>;

// ---------- SPS -> Index ----------

/** Per-dataset anchors of the Index: SPS of random answers and the human ceiling. */
export interface IndexScale {
  random: number;
  ceiling: number;
}

/** Index_d = 100 * (SPS - SPS_random) / (ceiling - SPS_random). */
export function spsToIndex(sps: number | null | undefined, scale: IndexScale | undefined) {
  if (sps == null || Number.isNaN(sps) || !scale) return null;
  return (100 * (sps - scale.random)) / (scale.ceiling - scale.random);
}

/** An SPS difference or standard deviation in Index points. */
export function spsSpanToIndex(span: number | null | undefined, scale: IndexScale | undefined) {
  if (span == null || Number.isNaN(span) || !scale) return null;
  return (100 * span) / (scale.ceiling - scale.random);
}

/** Client side: the anchors embedded by components/sb/IndexScales.astro. */
export function readIndexScales(): Record<string, IndexScale> {
  try {
    return JSON.parse(document.getElementById("sb-index-scales")?.textContent ?? "{}");
  } catch {
    return {};
  }
}

/** Index in whole points, like the rest of the site; "—" when missing. */
export const fmtIndex = (v: number | null | undefined): string =>
  v == null || Number.isNaN(v) ? "—" : String(Math.round(v));

export const INDEX_EXPLAINER =
  "SynthBench Index: 0 = random answers, 100 = real people. SPS is the raw 0 to 1 score it is computed from.";
