// Shared helpers for the exploration pages (/explore, /compare, /run,
// /config, /question): human labels for the settings that tell same-model
// configs apart, small-sample confidence intervals, and question-page keys.
//
// Everything here works on the public runs-index catalog or on values the
// caller already has; nothing fetches gated per-question data.

import type { RunIndexEntry } from "@/types/runs";
import { METHOD_NAMES, datasetName, runSystem } from "./vocab";

/** "opinionsqa" → "OpinionsQA"; "ntia (Nov 2023)" → "NTIA (Nov 2023)". Names from lib/vocab.ts. */
export function datasetLabel(id: string | null | undefined): string {
  if (!id) return "—";
  const [head, ...rest] = id.split(" ");
  const label = datasetName(head);
  return rest.length ? `${label} ${rest.join(" ")}` : label;
}

type NameFields = Parameters<typeof runSystem>[0];
/**
 * Canonical system name of a run or config ("GPT-6 Luna via codex, persona"),
 * the same one the leaderboard and charts use. Includes the harness tag.
 */
export const systemName = (e: NameFields): string => runSystem(e).full;
/** Method label ("Raw LLM", "Althing persona", "Ensemble", "Baseline"). */
export const methodName = (e: NameFields): string => METHOD_NAMES[runSystem(e).method].label;

/** Bare adapter name of a dataset id ("ntia (Nov 2023)" → "ntia"). */
export const datasetBase = (id: string): string => id.split(" ", 1)[0] ?? id;

/** Sampling temperature; null means the provider default. */
export const tempLabel = (t: number | null | undefined): string =>
  t == null ? "default" : String(t);

/** Prompt template; null and "current" are both the default template. */
export const templateLabel = (tpl: string | null | undefined): string =>
  !tpl || tpl === "current" ? "default" : tpl;

type SettingsLike = Pick<
  RunIndexEntry,
  "temperature" | "template" | "effort" | "persona_pack" | "n_questions"
>;

/**
 * One-line description of the settings that distinguish configs of the same
 * model, in words: "temperature 0.85 · default template · 100 questions",
 * or "default settings · 100 questions" when temperature and template are
 * both the defaults (the same wording as /explore). Optional parts (effort,
 * persona pack) only appear when set. The harness is part of the system name
 * (systemName), so it is not repeated here.
 */
export function settingsLabel(e: SettingsLike, opts: { n?: boolean } = {}): string {
  const tempDefault = e.temperature == null;
  const tplDefault = templateLabel(e.template) === "default";
  const parts =
    tempDefault && tplDefault
      ? ["default settings"]
      : [
          tempDefault ? "default temperature" : `temperature ${tempLabel(e.temperature)}`,
          `${templateLabel(e.template)} template`,
        ];
  if (e.effort) parts.push(`${e.effort} effort`);
  if (e.persona_pack) parts.push(`${e.persona_pack} personas`);
  if (opts.n !== false) parts.push(`${e.n_questions} questions`);
  return parts.join(" · ");
}

/** Two-sided 97.5% Student-t quantiles for df = 1..30; df > 30 uses 1.96. */
const T975 = [
  12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.16, 2.145,
  2.131, 2.12, 2.11, 2.101, 2.093, 2.086, 2.08, 2.074, 2.069, 2.064, 2.06, 2.056, 2.052, 2.048,
  2.045, 2.042,
];
export const tQuantile975 = (df: number): number => (df >= 1 && df <= 30 ? T975[df - 1] : 1.96);

/** Fewest replicates for which a replicate-spread interval is shown. */
export const MIN_CI_REPLICATES = 3;

export interface ReplicateStats {
  mean: number | null;
  /** Sample standard deviation (n − 1); null with fewer than two values. */
  std: number | null;
  n: number;
  /** 95% t-interval of the mean; null when n < MIN_CI_REPLICATES. */
  ci: { low: number; high: number } | null;
}

/** Mean, sample std and a t-based 95% interval over replicate values. */
export function replicateStats(values: (number | null | undefined)[]): ReplicateStats {
  const xs = values.filter((v): v is number => typeof v === "number" && !Number.isNaN(v));
  const n = xs.length;
  if (n === 0) return { mean: null, std: null, n: 0, ci: null };
  const mean = xs.reduce((a, b) => a + b, 0) / n;
  if (n < 2) return { mean, std: null, n, ci: null };
  const std = Math.sqrt(xs.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1));
  if (n < MIN_CI_REPLICATES) return { mean, std, n, ci: null };
  const half = (tQuantile975(n - 1) * std) / Math.sqrt(n);
  return { mean, std, n, ci: { low: mean - half, high: mean + half } };
}

/** Mirror publish._safe_question_key: anything but [A-Za-z0-9_-] → "_". */
export const safeQuestionKey = (key: string): string => key.replace(/[^A-Za-z0-9_-]/g, "_");

/** Numeric-aware key comparison ("Q2" before "Q10"). */
export const compareKeys = (a: string, b: string): number =>
  a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" });

/**
 * Sanitized keys that have a /question/<dataset>/<key>/ page, or null when
 * that can't be determined. Gated datasets list theirs in the public
 * gated-routes.json manifest (keys only, no data); full-tier datasets in their
 * public question index. Private-holdout keys have no page, so links are only
 * drawn for keys in this set.
 */
export async function questionPageKeys(base: string, dataset: string): Promise<Set<string> | null> {
  try {
    const res = await fetch(`${base}/data/gated-routes.json`);
    if (res.ok) {
      const manifest = (await res.json()) as { datasets?: Record<string, string[]> };
      const keys = manifest.datasets?.[dataset];
      if (keys) return new Set(keys);
    }
  } catch {
    // fall through to the full-tier index
  }
  try {
    const res = await fetch(`${base}/data/question/${encodeURIComponent(dataset)}/index.json`);
    if (!res.ok) return null;
    const idx = (await res.json()) as { questions?: { key: string }[] };
    return new Set((idx.questions ?? []).map((q) => safeQuestionKey(q.key)));
  } catch {
    return null;
  }
}

/** Modal (highest-share) option of a distribution, or "—". */
export function modalOption(dist: Record<string, number> | undefined | null): string {
  if (!dist) return "—";
  let best: string | null = null;
  let bestVal = Number.NEGATIVE_INFINITY;
  for (const [k, v] of Object.entries(dist)) {
    if (v > bestVal) {
      bestVal = v;
      best = k;
    }
  }
  return best ?? "—";
}
