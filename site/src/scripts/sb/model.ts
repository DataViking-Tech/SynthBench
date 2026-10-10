// Client-side view of the Index data embedded by the page (see IndexData in
// lib/synthIndex.ts), plus the shared scope / compare state.

import type { DatasetMeta, IndexData, Method, SystemConfig } from "@/lib/synthIndex";

export type { DatasetMeta, IndexData, Method, SystemConfig };
export type Scope = "all" | string;

export interface PageData extends IndexData {
  base: string;
  slugs: Record<string, string>;
}

let cached: PageData | null = null;
export function data(): PageData {
  if (cached) return cached;
  const el = document.getElementById("sb-index-data");
  if (!el?.textContent) throw new Error("Index data missing from page");
  cached = JSON.parse(el.textContent) as PageData;
  return cached;
}

export const CORE = ["opinionsqa", "subpop", "globalopinionqa"] as const;
export const ALL = [...CORE, "gss"] as const;

export const METHODS: Record<
  Exclude<Method, "baseline">,
  { label: string; short: string; desc: string; color: string }
> = {
  raw: { label: "Raw LLM", short: "raw", desc: "the model prompted directly", color: "--sb-raw" },
  althing: {
    label: "Althing persona",
    short: "persona",
    desc: "the same model, conditioned with a demographic persona",
    color: "--sb-althing",
  },
  ensemble: {
    label: "Ensemble",
    short: "ensemble",
    desc: "average of three persona systems",
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
export const dsMeta = (id: string): DatasetMeta | undefined =>
  data().datasets.find((d) => d.id === id);

export const shortName = (c: SystemConfig): string =>
  c.method === "ensemble" ? "Ensemble" : c.base.replace("Gemini 2.5 ", "").replace("Claude ", "");
export const fullName = (c: SystemConfig): string =>
  `${c.base}${c.method === "ensemble" ? "" : `, ${METHODS[c.method as ShownMethod].short}`}${c.variant ? ` (${c.variant})` : ""}`;
export const familyId = (c: SystemConfig): string => c.baseId;
export const profileHref = (c: SystemConfig): string =>
  `${data().base}system/${data().slugs[c.baseId]}/`;

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
    return c.coverage === 3 && c.index != null
      ? { v: c.index, lo: c.indexLo, hi: c.indexHi }
      : null;
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
export const scopeName = (scope: Scope = state.scope): string =>
  scope === "all" ? "Index, average of 3 core datasets" : `${dsLabel(scope)} only`;

export interface Ranked {
  c: SystemConfig;
  v: Val;
  tier: number | null;
  tied: number;
}
/** Tier = 1 + number of systems whose interval sits entirely above this one. */
export function tiers(pool: SystemConfig[], scope: Scope = state.scope): Ranked[] {
  const rows: Ranked[] = [];
  for (const c of pool) {
    const v = scoreIn(c, scope);
    if (v) rows.push({ c, v, tier: null, tied: 1 });
  }
  for (const r of rows) {
    const hi = r.v.hi;
    r.tier =
      hi == null ? null : 1 + rows.filter((o) => o !== r && o.v.lo != null && o.v.lo > hi).length;
  }
  const counts = new Map<number | null, number>();
  for (const r of rows) counts.set(r.tier, (counts.get(r.tier) ?? 0) + 1);
  for (const r of rows) r.tied = counts.get(r.tier) ?? 1;
  return rows.sort((a, b) => b.v.v - a.v.v);
}
export const rankedPool = (): SystemConfig[] => systems().filter((c) => !c.variant);
export const tierOf = (c: SystemConfig, scope: Scope = state.scope): Ranked | undefined =>
  tiers(rankedPool(), scope).find((r) => r.c === c);

/** The same base model under the other single-model method, if any. */
export function counterpart(c: SystemConfig): SystemConfig | undefined {
  if (c.variant || c.method === "ensemble") return undefined;
  return systems().find(
    (o) => !o.variant && o.baseId === c.baseId && o.method !== c.method && o.method !== "ensemble",
  );
}

export const ENSEMBLE_MEMBERS = [
  "anthropic/claude-haiku-4-5",
  "google/gemini-2.5-flash-lite",
  "openai/gpt-4o-mini",
];
