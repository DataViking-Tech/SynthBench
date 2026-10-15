// Client-side view of the Index data embedded by the page (see IndexData in
// lib/synthIndex.ts), plus the shared scope / compare state.

import type { DatasetMeta, IndexData, Method, SystemConfig } from "@/lib/synthIndex";
import { METHOD_NAMES, datasetAudience, ensembleNames, harnessTag } from "@/lib/vocab";
import { payload } from "./boot";

export type { DatasetMeta, IndexData, Method, SystemConfig };
export type Scope = "all" | string;

export interface PageData extends IndexData {
  base: string;
  slugs: Record<string, string>;
}

/** The Index data, fetched by boot.ts before the page script runs. */
export const data = (): PageData => payload<PageData>("sb-index-data");

export const CORE = ["opinionsqa", "subpop", "gss", "globalopinionqa"] as const;
export const ALL = [...CORE, "ntia"] as const;
/** True when a system was scored on every core dataset (ranked on the Index). */
export const fullCoverage = (c: SystemConfig): boolean => c.coverage === CORE.length;
/** Footnote mark for datasets shown but kept out of the Index. */
export const dsMark = (id: string): string =>
  (CORE as readonly string[]).includes(id) ? "" : " †";

export const METHODS: Record<
  Exclude<Method, "baseline">,
  { label: string; short: string; desc: string; color: string }
> = {
  raw: { ...METHOD_NAMES.raw, desc: "the model prompted directly", color: "--sb-raw" },
  althing: {
    ...METHOD_NAMES.althing,
    desc: "the same model, conditioned with a demographic persona",
    color: "--sb-althing",
  },
  ensemble: {
    ...METHOD_NAMES.ensemble,
    desc: "equal-weight blend of three or four systems, raw or persona",
    color: "--sb-ensemble",
  },
};
export type ShownMethod = keyof typeof METHODS;

export const LAB_GLYPH: Record<string, string> = {
  Anthropic: "A",
  OpenAI: "O",
  Google: "G",
  Meta: "M",
  DataViking: "Σ",
};

export const dsLabel = (id: string): string =>
  data().datasets.find((d) => d.id === id)?.label ?? id;
/** Secondary population text for a dataset ("US adults"). */
export const dsAudience = (id: string): string => datasetAudience(id);
export const dsMeta = (id: string): DatasetMeta | undefined =>
  data().datasets.find((d) => d.id === id);

// Names come from lib/vocab.ts (computed into SystemConfig at build time), so
// every page and chart uses the same full and short name for a system.
/** "Ensemble: Qwen 3.8 Flash, DeepSeek V4.1 Flash, Gemini 3.5 Flash-Lite (raw)" → "Qwen + DeepSeek + Gemini, raw". */
export const ensembleLabel = (name: string): string => ensembleNames(name).short;
/** Short name without the method: "Haiku 4.5", "GPT-6 Luna via codex", "Qwen + DeepSeek + Gemini, raw". */
export const shortName = (c: SystemConfig): string => c.short;
/** Short name plus the method: "Haiku 4.5, persona". */
export const shortWithMethod = (c: SystemConfig): string =>
  `${c.short}${c.method === "ensemble" ? "" : `, ${METHODS[c.method as ShownMethod].short}`}`;
/** Model (or ensemble) name without method tags, for rows that show the method separately. */
export const baseName = (c: SystemConfig): string => (c.method === "ensemble" ? c.name : c.base);
/** Full name: "Claude Haiku 4.5, persona", "GPT-6 Luna via codex, raw (structured template)". */
export const fullName = (c: SystemConfig): string => c.name;
/** Short method plus the harness tag: "persona via codex". */
export const methodShort = (c: SystemConfig): string =>
  `${METHODS[c.method as ShownMethod].short}${c.harness ? ` ${harnessTag(c.harness)}` : ""}`;
/** Method label plus the harness tag, for pickers: "Althing persona via codex". */
export const methodLabel = (c: SystemConfig): string =>
  `${METHODS[c.method as ShownMethod].label}${c.harness ? ` ${harnessTag(c.harness)}` : ""}`;
export const familyId = (c: SystemConfig): string => c.baseId;
/** Findings data names a few models by older short names; map them to the leaderboard's base names. */
const FINDINGS_NAMES: Record<string, string> = {
  "GPT-4o-mini": "GPT-4o mini",
  "Gemini Flash Lite": "Gemini 2.5 Flash-Lite",
};
export const findingsModel = (name: string): string => FINDINGS_NAMES[name] ?? name;
/** Query that picks this system on its /system page (method, plus harness when set). */
export const profileQuery = (c: SystemConfig): Record<string, string | null> => ({
  method: c.method,
  harness: c.harness ?? null,
});
export const profileHref = (c: SystemConfig): string => {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(profileQuery(c))) if (v != null) q.set(k, v);
  return `${data().base}system/${data().slugs[c.baseId]}/?${q}`;
};

// ---------- Shared state: scope + compare, persisted across pages ----------

const params = new URLSearchParams(location.search);
const stored = (k: string) => {
  try {
    return localStorage.getItem(k);
  } catch {
    return null;
  }
};
export const state = {
  scope: (params.get("scope") ?? stored("sb-scope") ?? "all") as Scope,
  compare: [] as string[],
};
try {
  state.compare = JSON.parse(stored("sb-compare") ?? "[]") as string[];
} catch {
  state.compare = [];
}

const listeners: (() => void)[] = [];
export const onChange = (fn: () => void): void => {
  listeners.push(fn);
};
export function emit(): void {
  try {
    localStorage.setItem("sb-scope", state.scope);
    localStorage.setItem("sb-compare", JSON.stringify(state.compare));
  } catch {
    // storage unavailable: state just won't persist across pages
  }
  for (const fn of listeners) fn();
}

export const systems = (): SystemConfig[] => data().systems;
export const byKey = (k: string): SystemConfig | undefined => systems().find((c) => c.key === k);

/** Validate stored compare keys against this build's data. */
export function pruneCompare(): void {
  state.compare = state.compare.filter((k) => byKey(k)).slice(0, 3);
  if (state.scope !== "all" && !dsMeta(state.scope)) state.scope = "all";
}

export interface Val {
  v: number;
  lo: number | null;
  hi: number | null;
}
export function scoreIn(c: SystemConfig, scope: Scope = state.scope): Val | null {
  if (scope === "all")
    return fullCoverage(c) && c.index != null ? { v: c.index, lo: c.indexLo, hi: c.indexHi } : null;
  const d = c.ds[scope];
  return d ? { v: d.idx, lo: d.lo, hi: d.hi } : null;
}
export function component(
  c: SystemConfig,
  k: "pDist" | "pRank" | "pRefuse" | "sps",
  scope: Scope = state.scope,
): number | null {
  const ids = (scope === "all" ? [...CORE] : [scope]).filter((id) => c.ds[id]);
  return ids.length ? ids.reduce((a, id) => a + c.ds[id][k], 0) / ids.length : null;
}
/** Holdout gap of the dataset closest to (or furthest over) its review threshold. */
export function worstHoldout(c: SystemConfig): { gap: number; limit: number } | null {
  let worst: { gap: number; limit: number } | null = null;
  for (const x of Object.values(c.ds)) {
    if (x.holdoutGap == null) continue;
    if (!worst || x.holdoutGap / x.holdoutLimit > worst.gap / worst.limit)
      worst = { gap: x.holdoutGap, limit: x.holdoutLimit };
  }
  return worst;
}
export const scopeName = (scope: Scope = state.scope): string =>
  scope === "all" ? `Index, average of ${CORE.length} core datasets` : `${dsLabel(scope)} only`;

export interface Ranked {
  c: SystemConfig;
  v: Val;
  tier: number | null;
  tied: number;
}
/**
 * Dense tiers over the rows sorted by score. Walking down the list, the first
 * system not yet placed opens a tier (its "leader"); every following system
 * whose 95% interval still reaches the leader's interval (upper bound ≥ the
 * leader's lower bound) joins it. The first system whose interval sits
 * entirely below the leader's opens the next tier. Tiers are numbered 1..k with
 * no gaps and always group adjacent rows. Rows without an interval get no tier.
 */
export function tiers(pool: SystemConfig[], scope: Scope = state.scope): Ranked[] {
  const rows: Ranked[] = [];
  for (const c of pool) {
    const v = scoreIn(c, scope);
    if (v) rows.push({ c, v, tier: null, tied: 1 });
  }
  rows.sort((a, b) => b.v.v - a.v.v);
  let tier = 0;
  let leaderLo: number | null = null;
  for (const r of rows) {
    const { lo, hi } = r.v;
    if (lo == null || hi == null) continue;
    if (leaderLo == null || hi < leaderLo) {
      tier += 1;
      leaderLo = lo;
    }
    r.tier = tier;
  }
  const counts = new Map<number | null, number>();
  for (const r of rows) counts.set(r.tier, (counts.get(r.tier) ?? 0) + 1);
  for (const r of rows) r.tied = r.tier == null ? 1 : (counts.get(r.tier) ?? 1);
  return rows;
}
export const rankedPool = (): SystemConfig[] => systems().filter((c) => !c.variant);
export const tierOf = (c: SystemConfig, scope: Scope = state.scope): Ranked | undefined =>
  tiers(rankedPool(), scope).find((r) => r.c === c);

/** The same base model under the other single-model method and the same harness, if any. */
export function counterpart(c: SystemConfig): SystemConfig | undefined {
  if (c.variant || c.method === "ensemble") return undefined;
  return systems().find(
    (o) =>
      !o.variant &&
      o.baseId === c.baseId &&
      o.method !== c.method &&
      o.method !== "ensemble" &&
      (o.harness ?? null) === (c.harness ?? null),
  );
}

export interface PersonaPair {
  raw: SystemConfig;
  persona: SystemConfig;
  va: number;
  vb: number;
}
/**
 * One raw-vs-persona pair per base model, both scored in `scope`. Raw and
 * persona run through the same harness; the direct API pair is preferred
 * when a model was also run through a CLI harness.
 */
export function personaPairs(scope: Scope = state.scope): PersonaPair[] {
  const out = new Map<string, PersonaPair>();
  const personas = systems()
    .filter((c) => c.method === "althing" && !c.variant)
    .sort((a, b) => Number(a.harness != null) - Number(b.harness != null));
  for (const persona of personas) {
    if (out.has(persona.baseId)) continue;
    const raw = counterpart(persona);
    const va = raw ? scoreIn(raw, scope) : null;
    const vb = scoreIn(persona, scope);
    if (raw && va && vb) out.set(persona.baseId, { raw, persona, va: va.v, vb: vb.v });
  }
  return [...out.values()];
}

/** Ensemble rows (not variants), each with its own members. */
export const ensembles = (): SystemConfig[] =>
  systems().filter((c) => c.method === "ensemble" && !c.variant);
