// Groups page: how closely each system's default answers match each
// demographic group (or country), plus the effect of naming the group in the
// prompt. Data: #sb-group-data (lib/groupAlignment.ts), joined to the Index
// systems by config id.
//
// Charts summarise the shown systems per row (range, middle half, median, one
// tick per system) so they stay readable as systems are added. Individual
// systems are read from the table or highlighted by letter, using the shared
// compare selection (up to three).

import type {
  ConditionCell,
  ConditionSet,
  GroupAttrScore,
  GroupAttribute,
  GroupData,
  Interval,
} from "@/lib/groupAlignment";
import {
  type Scale,
  axisTitle,
  css,
  fill,
  fmt,
  h,
  linear,
  mount,
  s,
  textWidth,
  ticks,
} from "../dom";
import {
  METHODS,
  type ShownMethod,
  type SystemConfig,
  byKey,
  data,
  dsLabel,
  emit,
  fullName,
  onChange,
  profileHref,
  pruneCompare,
  state,
  systems,
} from "../model";
import {
  METHOD_IDS,
  filterStatus,
  glyph,
  initShell,
  methodChips,
  methodColor,
  methodKey,
  readSet,
  setParam,
  takeaways,
  tip,
  toggleCompare,
  writeParams,
} from "../ui";

pruneCompare();
const G = JSON.parse(
  (document.getElementById("sb-group-data") as HTMLElement).textContent ?? "{}",
) as GroupData;
const $ = (id: string) => document.getElementById(id) as HTMLElement;
const q = new URLSearchParams(location.search);

const DATASETS = ["opinionsqa", "subpop", "globalopinionqa"].filter((d) => G.datasets[d]);
const POPULATION: Record<string, string> = {
  opinionsqa: "US adults, 8 attributes",
  subpop: "US adults, 22 groups",
  globalopinionqa: "Countries",
};
const LETTERS = ["A", "B", "C"];
const TABLE_ROWS = 12;

const st = {
  ds: DATASETS.includes(q.get("ds") ?? "") ? (q.get("ds") as string) : "opinionsqa",
  methods: readSet("methods", METHOD_IDS, METHOD_IDS),
  variants: q.get("variants") === "1",
  split: q.get("split") === "method",
  attr: q.get("attr"),
  mode: (q.get("mode") === "abs" ? "abs" : "rel") as "rel" | "abs",
  cond: q.get("cond"),
  sort: q.get("sort"),
  asc: q.get("dir") === "asc",
  find: "",
  all: false,
};

// ---------- Data access ----------
const scoreOf = (c: SystemConfig, ds = st.ds) => {
  const id = c.ds[ds]?.configId;
  return id ? G.systems[id] : undefined;
};
const eligible = () =>
  systems().filter(
    (c) => c.method !== "baseline" && (st.variants || !c.variant) && scoreOf(c) != null,
  );
const pool = () => eligible().filter((c) => st.methods.has(c.method));
/** Highlighted systems: the shared compare selection, limited to what's shown. */
const picked = (): SystemConfig[] =>
  state.compare
    .map((k) => byKey(k))
    .filter((c): c is SystemConfig => c != null && pool().includes(c));
const letterOf = (c: SystemConfig) => LETTERS[state.compare.indexOf(c.key)] ?? "?";

const ATTR_ORDER = [
  "POLIDEOLOGY",
  "POLPARTY",
  "EDUCATION",
  "INCOME",
  "AGE",
  "RACE",
  "RELIG",
  "CREGION",
  "SEX",
];
const attrRank = (id: string) =>
  ATTR_ORDER.includes(id) ? ATTR_ORDER.indexOf(id) : ATTR_ORDER.length;
const attrsOf = (ds = st.ds): GroupAttribute[] =>
  [...(G.datasets[ds]?.attributes ?? [])].sort((p, r) => attrRank(p.id) - attrRank(r.id));
const currentAttr = (): GroupAttribute => {
  const list = attrsOf();
  return (
    list.find((a) => a.id === st.attr) ??
    list.find((a) => a.id === "POLIDEOLOGY") ??
    list.find((a) => a.id === "COUNTRY") ??
    list[0]
  );
};
const groupLabel = (a: GroupAttribute, id: string) =>
  a.groups.find((g) => g.id === id)?.label ?? id;
const ends = (a: GroupAttribute) => [a.groups[0].label, a.groups[a.groups.length - 1].label];

interface RefRow {
  id: "everyone" | "majority" | "random";
  name: string;
  desc: string;
  score: (attr: string) => GroupAttrScore | undefined;
}
const refScore = (c: SystemConfig | null | undefined) => (attr: string) =>
  c ? scoreOf(c)?.attrs[attr] : undefined;
const REFS: RefRow[] = [
  {
    id: "everyone",
    name: "All respondents",
    desc: "the whole survey sample's real answers, scored against each group",
    score: (attr) => G.reference[st.ds]?.[attr],
  },
  {
    id: "majority",
    name: "Majority answer",
    desc: "always picks the most popular option",
    score: refScore(data().references.majority),
  },
  {
    id: "random",
    name: "Random answers",
    desc: "picks an option uniformly at random",
    score: refScore(data().references.random),
  },
];

const signed = (v: number) =>
  Math.abs(v) < 0.05 ? "0.0" : `${v > 0 ? "+" : "−"}${Math.abs(v).toFixed(1)}`;
const quantile = (xs: number[], p: number) => {
  const a = [...xs].sort((u, v) => u - v);
  if (!a.length) return Number.NaN;
  const i = (a.length - 1) * p;
  const lo = Math.floor(i);
  return a[lo] + (a[Math.ceil(i)] - a[lo]) * (i - lo);
};
const median = (xs: number[]) => quantile(xs, 0.5);
const niceMax = (v: number, step = 2) => Math.max(step * 2, Math.ceil(v / step) * step);

// ---------- URL + change wiring ----------
const isDefault = () =>
  st.ds === "opinionsqa" && setParam(st.methods, METHOD_IDS) == null && !st.variants;
const changed = () => {
  writeParams({
    ds: st.ds === "opinionsqa" ? null : st.ds,
    methods: setParam(st.methods, METHOD_IDS),
    variants: st.variants ? "1" : null,
    split: st.split ? "method" : null,
    attr: st.attr,
    mode: st.mode === "abs" ? "abs" : null,
    cond: st.cond,
    sort: st.sort,
    dir: st.asc ? "asc" : null,
  });
  emit();
};
const reset = () => {
  st.ds = "opinionsqa";
  for (const m of METHOD_IDS) st.methods.add(m);
  st.variants = false;
  changed();
};

function refInfo(node: SVGElement, title: string, rows: [string, string][]): void {
  node.addEventListener("pointerenter", (e) => tip.show(e, title, rows));
  node.addEventListener("pointermove", (e) => tip.move(e));
  node.addEventListener("pointerleave", () => tip.hide());
}

// ---------- Marks ----------
/** Reference glyphs: triangle = all respondents, square = majority, cross = random. */
function refMark(g: Element, id: RefRow["id"], x: number, y: number): SVGElement {
  const col = css("--sb-muted");
  if (id === "everyone")
    return s(
      "path",
      { d: `M${x - 5},${y - 4}L${x + 5},${y - 4}L${x},${y + 4}Z`, fill: col, stroke: "none" },
      g,
    );
  if (id === "majority")
    return s(
      "rect",
      {
        x: x - 4,
        y: y - 4,
        width: 8,
        height: 8,
        fill: css("--sb-panel"),
        stroke: col,
        "stroke-width": 1.6,
      },
      g,
    );
  return s(
    "path",
    {
      d: `M${x - 4},${y - 4}L${x + 4},${y + 4}M${x - 4},${y + 4}L${x + 4},${y - 4}`,
      stroke: col,
      "stroke-width": 1.8,
    },
    g,
  );
}

/** Letter badge for a highlighted system, with an optional interval line. */
function letterMark(
  g: Element,
  c: SystemConfig,
  x: number,
  y: number,
  rows: [string, string][],
  ci?: [number, number],
): void {
  if (ci)
    s(
      "line",
      {
        x1: ci[0],
        x2: ci[1],
        y1: y,
        y2: y,
        stroke: css("--sb-ink"),
        "stroke-width": 1.6,
        opacity: 0.55,
      },
      g,
    );
  const grp = s("g", { tabindex: "0", role: "img", "aria-label": `${fullName(c)}` }, g);
  s(
    "circle",
    { cx: x, cy: y, r: 7, fill: css("--sb-ink"), stroke: css("--sb-panel"), "stroke-width": 1.5 },
    grp,
  );
  s(
    "text",
    { x, y: y + 3.5, "text-anchor": "middle", class: "sb-letter-t", text: letterOf(c) },
    grp,
  );
  refInfo(grp as unknown as SVGElement, `${letterOf(c)}: ${fullName(c)}`, rows);
}

interface BandSet {
  key: string;
  label: string;
  color: string;
  list: SystemConfig[];
}
/** One band for all shown systems, or one per method when split. */
function bandSets(list: SystemConfig[]): BandSet[] {
  if (!st.split) return [{ key: "all", label: "Shown systems", color: css("--sb-ink-2"), list }];
  return METHOD_IDS.filter((m) => st.methods.has(m))
    .map((m) => ({
      key: m,
      label: METHODS[m].label,
      color: methodColor(m),
      list: list.filter((c) => c.method === m),
    }))
    .filter((b) => b.list.length);
}
const bandSetOf = (sets: BandSet[], c: SystemConfig) =>
  sets.findIndex((b) => b.key === "all" || b.key === c.method);

/**
 * Summary band: thin line = full range, box = middle half, short ticks = one
 * per system, black bar = median. Hover shows the numbers.
 */
function band(
  g: Element,
  x: Scale,
  cy: number,
  vals: number[],
  half: number,
  color: string,
  title: string,
  show: (v: number) => string,
): void {
  if (!vals.length) return;
  const mn = Math.min(...vals);
  const mx = Math.max(...vals);
  const q1 = quantile(vals, 0.25);
  const q3 = quantile(vals, 0.75);
  const md = median(vals);
  s(
    "line",
    { x1: x(mn), x2: x(mx), y1: cy, y2: cy, stroke: color, "stroke-width": 1.5, opacity: 0.5 },
    g,
  );
  s(
    "rect",
    {
      x: x(q1),
      y: cy - half,
      width: Math.max(3, x(q3) - x(q1)),
      height: half * 2,
      rx: 3,
      fill: color,
      opacity: 0.2,
    },
    g,
  );
  for (const v of vals)
    s(
      "line",
      {
        x1: x(v),
        x2: x(v),
        y1: cy - half + 2,
        y2: cy + half - 2,
        stroke: color,
        "stroke-width": 1.3,
        opacity: 0.55,
      },
      g,
    );
  s(
    "line",
    {
      x1: x(md),
      x2: x(md),
      y1: cy - half - 3,
      y2: cy + half + 3,
      stroke: css("--sb-ink"),
      "stroke-width": 2.2,
    },
    g,
  );
  const hit = s(
    "rect",
    {
      x: x(mn) - 5,
      y: cy - half - 4,
      width: x(mx) - x(mn) + 10,
      height: half * 2 + 8,
      class: "sb-hit",
    },
    g,
  );
  refInfo(hit, title, [
    ["Systems", String(vals.length)],
    ["Median", show(md)],
    ["Middle half", `${show(q1)} to ${show(q3)}`],
    ["Range", `${show(mn)} to ${show(mx)}`],
  ]);
}

function legendSvg(draw: (g: SVGSVGElement) => void, w = 16): SVGSVGElement {
  const svg = s("svg", { width: w, height: 14, "aria-hidden": "true", class: "sb-c" });
  draw(svg);
  return svg;
}
const bandLegend = () => {
  const items: HTMLElement[] = [];
  if (st.split)
    items.push(
      ...METHOD_IDS.filter((m) => st.methods.has(m)).map((m) =>
        h("span", null, methodKey(m), METHODS[m].label),
      ),
    );
  items.push(
    h(
      "span",
      null,
      legendSvg((g) => {
        const c = css("--sb-ink-2");
        s("line", { x1: 1, x2: 33, y1: 7, y2: 7, stroke: c, "stroke-width": 1.5, opacity: 0.5 }, g);
        s("rect", { x: 9, y: 2, width: 16, height: 10, rx: 2, fill: c, opacity: 0.2 }, g);
        for (const v of [4, 11, 14, 20, 30])
          s("line", { x1: v, x2: v, y1: 4, y2: 10, stroke: c, opacity: 0.55 }, g);
        s("line", { x1: 17, x2: 17, y1: 0, y2: 14, stroke: css("--sb-ink"), "stroke-width": 2 }, g);
      }, 34),
      "Shown systems",
    ),
  );
  return items;
};
const pickedLegend = () =>
  picked().length
    ? [
        h(
          "span",
          null,
          legendSvg((g) => {
            s("circle", { cx: 8, cy: 7, r: 6.5, fill: css("--sb-ink") }, g);
          }),
          "Highlighted (bar: 95% interval)",
        ),
      ]
    : [];
const refLegend = (ids: RefRow["id"][]) =>
  REFS.filter((r) => ids.includes(r.id)).map((r) =>
    h(
      "span",
      { title: r.desc },
      legendSvg((g) => refMark(g, r.id, 8, 7)),
      r.name,
    ),
  );

function xAxis(
  svg: SVGSVGElement,
  x: (v: number) => number,
  dom: [number, number],
  top: number,
  bottom: number,
  title: string,
  signedTicks: boolean,
): void {
  for (const t of ticks(dom[0], dom[1], 12)) {
    s(
      "line",
      {
        class: t === 0 && signedTicks ? "sb-zero" : "sb-gl",
        x1: x(t),
        x2: x(t),
        y1: top,
        y2: bottom,
      },
      svg,
    );
    s(
      "text",
      {
        class: "sb-t",
        x: x(t),
        y: bottom + 16,
        "text-anchor": "middle",
        text: signedTicks
          ? t === 0
            ? "0"
            : `${t > 0 ? "+" : "−"}${Math.abs(t)}`
          : Number.isInteger(t)
            ? String(t)
            : t.toFixed(1),
      },
      svg,
    );
  }
  axisTitle(svg, title, { x: (x(dom[0]) + x(dom[1])) / 2, y: bottom + 38 });
}

/** Vertical offsets for stacked bands and highlighted letters within a row. */
const subRow = (n: number, i: number, gap: number) => (i - (n - 1) / 2) * gap;

// ---------- Chart 1: which end of each ordered scale ----------
function leanChart(el: HTMLElement, W: number): string[] {
  const attrs = attrsOf().filter((a) => a.ordered);
  if (!attrs.length) {
    el.append(
      h(
        "p",
        { class: "sb-empty" },
        `${dsLabel(st.ds)} groups are countries, which have no natural order. See the country chart below.`,
      ),
    );
    return [];
  }
  const list = pool();
  const sets = bandSets(list);
  const hl = picked();
  const endsOf = (c: SystemConfig, a: GroupAttribute) => scoreOf(c)?.attrs[a.id]?.ends;
  const rows = attrs.map((a) => ({
    a,
    vals: list.map((c) => endsOf(c, a)).filter((v): v is Interval => v != null),
    refs: REFS.map((r) => ({ r, v: r.score(a.id)?.ends })).filter(
      (x): x is { r: RefRow; v: Interval } => x.v != null,
    ),
  }));
  const all = rows.flatMap((r) => [...r.vals.map((v) => v[0]), ...r.refs.map((x) => x.v[0])]);
  for (const c of hl)
    for (const a of attrs) {
      const v = endsOf(c, a);
      if (v) all.push(v[1], v[2]);
    }
  const D = niceMax(Math.max(...all.map(Math.abs), 4));
  const labelW = Math.max(...attrs.map((a) => textWidth(a.label, 12.5, 600))) + 28;
  const padR = 92;
  const x = linear(-D, D, labelW, W - padR);
  const bandH = st.split ? 20 : 26;
  const rowH = 44 + sets.length * bandH;
  const top = 26;
  const bottom = top + rows.length * rowH;
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: bottom + 48,
    role: "img",
    "aria-label": `Difference in match between the two ends of each ordered attribute, ${dsLabel(st.ds)}`,
  });
  el.append(svg);
  xAxis(
    svg,
    x,
    [-D, D],
    top - 8,
    bottom,
    "Match to the right-hand group minus match to the left-hand group (points)",
    true,
  );
  s("text", { class: "sb-t", x: W - 6, y: top - 12, "text-anchor": "end", text: "MEDIAN" }, svg);

  rows.forEach((row, i) => {
    const y0 = top + i * rowH;
    const mid = y0 + 26 + (sets.length * bandH) / 2;
    const [first, last] = ends(row.a);
    if (i) s("line", { x1: 0, x2: W, y1: y0, y2: y0, stroke: css("--sb-line") }, svg);
    s("text", { class: "sb-lab", x: 0, y: mid + 4, text: row.a.label }, svg);
    s("text", { class: "sb-sub", x: x(-D) + 2, y: y0 + 16, text: `← closer to ${first}` }, svg);
    s(
      "text",
      {
        class: "sb-sub",
        x: x(D) - 2,
        y: y0 + 16,
        "text-anchor": "end",
        text: `closer to ${last} →`,
      },
      svg,
    );
    sets.forEach((b, j) => {
      const cy = mid + subRow(sets.length, j, bandH);
      const vals = b.list.map((c) => endsOf(c, row.a)?.[0]).filter((v): v is number => v != null);
      band(
        svg,
        x,
        cy,
        vals,
        st.split ? 6 : 8,
        b.color,
        `${row.a.label}: ${b.label}`,
        (v) => `${signed(v)} points`,
      );
      if (st.split)
        s(
          "text",
          {
            class: "sb-val",
            x: W - 6,
            y: cy + 4,
            "text-anchor": "end",
            text: signed(median(vals)),
          },
          svg,
        );
    });
    if (!st.split)
      s(
        "text",
        {
          class: "sb-val",
          x: W - 6,
          y: mid + 4,
          "text-anchor": "end",
          text: signed(median(row.vals.map((v) => v[0]))),
        },
        svg,
      );
    for (const { r, v } of row.refs) {
      const m = refMark(svg, r.id, x(v[0]), r.id === "everyone" ? y0 + 26 : mid);
      refInfo(m, r.name, [
        [`${last} minus ${first}`, `${signed(v[0])} points`],
        ["95% interval", `${signed(v[1])} to ${signed(v[2])}`],
        ["What it is", r.desc],
      ]);
    }
    hl.forEach((c, k) => {
      const v = endsOf(c, row.a);
      if (!v) return;
      const j = bandSetOf(sets, c);
      const cy = mid + subRow(sets.length, Math.max(0, j), bandH) + subRow(hl.length, k, 5);
      letterMark(
        svg,
        c,
        x(v[0]),
        cy,
        [
          [`${last} minus ${first}`, `${signed(v[0])} points`],
          ["95% interval", `${signed(v[1])} to ${signed(v[2])}`],
        ],
        [x(v[1]), x(v[2])],
      );
    });
  });

  const notes: string[] = [];
  for (const row of rows) {
    if (!row.vals.length) continue;
    const [first, last] = ends(row.a);
    const toLast = row.vals.filter((v) => v[1] > 0).length;
    const toFirst = row.vals.filter((v) => v[2] < 0).length;
    const n = row.vals.length;
    const med = median(row.vals.map((v) => v[0]));
    if (toLast >= toFirst && toLast > 0)
      notes.push(
        `${row.a.label}: ${toLast} of ${n} systems are closer to ${last} than to ${first}, beyond their 95% interval. Median gap ${signed(med)} points.`,
      );
    else if (toFirst > 0)
      notes.push(
        `${row.a.label}: ${toFirst} of ${n} systems are closer to ${first} than to ${last}, beyond their 95% interval. Median gap ${signed(med)} points.`,
      );
    const maj = row.refs.find((x) => x.r.id === "majority")?.v;
    if (
      maj &&
      maj[1] > 0 === med > 0 &&
      (maj[1] > 0 || maj[2] < 0) &&
      Math.abs(maj[0]) >= Math.abs(med) / 3
    )
      notes.push(
        `The majority answer also scores ${signed(maj[0])} on ${row.a.label.toLowerCase()}, so part of that gap comes from how much each group agrees internally, not from the systems.`,
      );
  }
  return notes.slice(0, 6);
}

// ---------- Table: one row per system ----------
interface Col {
  id: string;
  label: string;
  sub: string;
  signed: boolean;
  get: (c: SystemConfig) => Interval | undefined;
}
const SHORT: Record<string, string> = {
  POLIDEOLOGY: "Ideology",
  RACE: "Race",
  RELIG: "Religion",
};
function tableCols(): Col[] {
  return attrsOf().map((a) => {
    if (a.ordered) {
      const [first, last] = ends(a);
      return {
        id: a.id,
        label: SHORT[a.id] ?? a.label,
        sub: `+ = ${last}`,
        signed: true,
        get: (c: SystemConfig) => scoreOf(c)?.attrs[a.id]?.ends,
      };
    }
    return {
      id: a.id,
      label: SHORT[a.id] ?? a.label,
      sub: "spread",
      signed: false,
      get: (c: SystemConfig) => scoreOf(c)?.attrs[a.id]?.gap,
    };
  });
}

function cellBar(v: Interval | undefined, col: Col, max: number): HTMLElement {
  if (!v) return h("td", { class: "r sb-muted" }, "—");
  const unclear = col.signed && v[1] <= 0 && v[2] >= 0;
  const w = 40;
  const svg = s("svg", { width: w, height: 10, "aria-hidden": "true", class: "sb-c" });
  const x = col.signed ? linear(-max, max, 0, w) : linear(0, max, 0, w);
  const x0 = col.signed ? x(0) : 0;
  s(
    "rect",
    {
      x: Math.min(x0, x(v[0])),
      y: 1,
      width: Math.max(1.5, Math.abs(x(v[0]) - x0)),
      height: 8,
      rx: 2,
      fill: css("--sb-ink-2"),
      opacity: unclear ? 0.25 : 0.7,
    },
    svg,
  );
  if (col.signed) s("line", { x1: x0, x2: x0, y1: 0, y2: 10, stroke: css("--sb-line-2") }, svg);
  return h(
    "td",
    {
      class: `r sb-gr-cell${unclear ? " unclear" : ""}`,
      title: `95% interval ${signed(v[1])} to ${signed(v[2])}${unclear ? ". Includes 0, so the direction is unclear." : ""}`,
    },
    h("span", { class: "sb-gr-num" }, col.signed ? signed(v[0]) : fmt.one(v[0])),
    svg,
  );
}

function systemsTable(): HTMLElement {
  const cols = tableCols();
  const sortCol = cols.find((c) => c.id === st.sort) ?? cols[0];
  const needle = st.find.trim().toLowerCase();
  const list = pool().filter((c) => !needle || fullName(c).toLowerCase().includes(needle));
  const val = (c: SystemConfig) => sortCol?.get(c)?.[0];
  list.sort((p, r) => {
    const a = val(p);
    const b = val(r);
    if (a == null) return 1;
    if (b == null) return -1;
    return st.asc ? a - b : b - a;
  });
  const shown = st.all || needle ? list : list.slice(0, TABLE_ROWS);
  const max = (col: Col) =>
    Math.max(
      1,
      ...pool().map((c) => Math.abs(col.get(c)?.[0] ?? 0)),
      ...REFS.map((r) =>
        Math.abs((col.signed ? r.score(col.id)?.ends : r.score(col.id)?.gap)?.[0] ?? 0),
      ),
    );
  const maxes = cols.map(max);
  const head = h(
    "tr",
    null,
    h("th", { class: "cb" }, h("span", { class: "sr-only" }, "Highlight")),
    h("th", null, "System"),
    cols.map((col) => {
      const on = col === sortCol;
      return h(
        "th",
        { class: "r", "aria-sort": on ? (st.asc ? "ascending" : "descending") : null },
        h(
          "button",
          {
            type: "button",
            class: `sb-gr-sort${on ? " on" : ""}`,
            title: `Sort by ${col.label}`,
            onclick: () => {
              if (st.sort === col.id || (!st.sort && col === cols[0])) st.asc = !st.asc;
              else {
                st.sort = col.id;
                st.asc = false;
              }
              changed();
            },
          },
          col.label,
          on ? (st.asc ? " ↑" : " ↓") : "",
        ),
        h("small", null, col.sub),
      );
    }),
  );
  const rows = shown.map((c) => {
    const sel = state.compare.includes(c.key);
    const i = state.compare.indexOf(c.key);
    return h(
      "tr",
      {
        class: `sys${sel ? " sel" : ""}`,
        tabindex: "0",
        "aria-label": `${fullName(c)}: ${sel ? "remove highlight" : "highlight on the charts"}`,
        onclick: () => toggleCompare(c.key),
        onkeydown: (e: KeyboardEvent) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggleCompare(c.key);
          }
        },
      },
      h(
        "td",
        { class: "cb" },
        sel && i < 3
          ? h("span", { class: "sb-letter" }, LETTERS[i])
          : h("span", { class: "sb-cbox", "aria-hidden": "true" }),
      ),
      h(
        "td",
        null,
        h(
          "div",
          { class: "sb-sysname" },
          h("div", { class: "n" }, glyph(c.lab), c.base),
          h(
            "div",
            { class: "m" },
            methodKey(c.method),
            c.method === "ensemble" ? "Ensemble" : METHODS[c.method as ShownMethod].label,
            c.variant ? ` · ${c.variant}` : null,
          ),
        ),
      ),
      cols.map((col, k) => cellBar(col.get(c), col, maxes[k])),
    );
  });
  const refRows = REFS.map((r) =>
    h(
      "tr",
      { class: "refrow" },
      h("td", null),
      h("td", null, h("b", null, r.name)),
      cols.map((col, k) =>
        cellBar(col.signed ? r.score(col.id)?.ends : r.score(col.id)?.gap, col, maxes[k]),
      ),
    ),
  );
  const more =
    !needle && list.length > TABLE_ROWS
      ? h(
          "button",
          {
            type: "button",
            class: "sb-linkbtn",
            onclick: () => {
              st.all = !st.all;
              emit();
            },
          },
          st.all ? `Show the first ${TABLE_ROWS}` : `Show all ${list.length} systems`,
        )
      : null;
  return h(
    "div",
    null,
    h(
      "table",
      { class: "sb-lb sb-gr-sys" },
      h("thead", null, head),
      h(
        "tbody",
        null,
        rows.length
          ? rows
          : h(
              "tr",
              null,
              h("td", { colspan: String(cols.length + 2), class: "sb-empty" }, "No systems match."),
            ),
        refRows,
      ),
    ),
    h(
      "div",
      { class: "sb-gr-tablefoot" },
      h("span", null, `${shown.length} of ${list.length} systems`),
      more,
    ),
  );
}

// ---------- Chart 2: every group ----------
function detailChart(el: HTMLElement, W: number): string[] {
  const a = currentAttr();
  if (!a) return [];
  const list = pool();
  const sets = bandSets(list);
  const hl = picked();
  const rel = st.mode === "rel";
  const isCountry = a.id === "COUNTRY";
  const cellOf = (c: SystemConfig, g: string) => scoreOf(c)?.attrs[a.id]?.groups[g];
  const valOf = (cell: number[] | undefined) => (cell ? (rel ? cell[1] : cell[0]) : null);

  type Row = {
    id: string;
    label: string;
    vals: number[];
    refs: { r: RefRow; v: number }[];
    n: number;
  };
  let rows: Row[] = a.groups.map((g) => {
    const cells = list
      .map((c) => cellOf(c, g.id))
      .filter((x): x is NonNullable<typeof x> => x != null);
    return {
      id: g.id,
      label: g.label,
      vals: cells.map((x) => (rel ? x[1] : x[0])),
      refs: REFS.filter((r) => rel || r.id !== "everyone")
        .map((r) => ({ r, v: valOf(r.score(a.id)?.groups[g.id]) }))
        .filter((x): x is { r: RefRow; v: number } => x.v != null),
      n: Math.round(median(cells.map((x) => x[4]))),
    };
  });
  rows = rows.filter((r) => r.vals.length);
  if (!a.ordered) rows.sort((p, r) => median(r.vals) - median(p.vals));
  if (!rows.length) {
    el.append(h("p", { class: "sb-empty" }, "No system shown has scores for these groups."));
    return [];
  }

  const vals = rows.flatMap((r) => [...r.vals, ...r.refs.map((x) => x.v)]);
  for (const c of hl)
    for (const r of rows) {
      const cell = cellOf(c, r.id);
      if (cell) vals.push(...(rel ? [cell[2], cell[3]] : [cell[0]]));
    }
  const dom: [number, number] = rel
    ? (() => {
        const D = niceMax(Math.max(...vals.map(Math.abs)));
        return [-D, D];
      })()
    : [Math.floor((Math.min(...vals) - 1) / 5) * 5, Math.ceil((Math.max(...vals) + 1) / 5) * 5];
  const labelW = Math.max(...rows.map((r) => textWidth(r.label, isCountry ? 12 : 12.5, 500))) + 22;
  const colW = 52;
  const padR = 64 + hl.length * colW;
  const x = linear(dom[0], dom[1], labelW, W - padR);
  const bandH = st.split ? 16 : isCountry ? 22 : 30;
  const rowH = st.split ? 8 + sets.length * bandH : bandH + (isCountry ? 4 : 6);
  const top = 22;
  const bottom = top + rows.length * rowH;
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: bottom + 48,
    role: "img",
    "aria-label": `Match to each ${a.label.toLowerCase()} group, ${dsLabel(st.ds)}`,
  });
  el.append(svg);
  xAxis(
    svg,
    x,
    dom,
    top - 6,
    bottom,
    rel
      ? "Match to the group's real answers minus the system's own average over these groups (points)"
      : "Match to the group's real answers (100 = identical answer shares)",
    rel,
  );
  s("text", { class: "sb-t", x: W - 6, y: top - 8, "text-anchor": "end", text: "QUESTIONS" }, svg);
  hl.forEach((c, k) =>
    s(
      "text",
      {
        class: "sb-t",
        x: W - 64 - (hl.length - 1 - k) * colW - 8,
        y: top - 8,
        "text-anchor": "end",
        text: letterOf(c),
      },
      svg,
    ),
  );

  const paths: [number, number][][] = hl.map(() => []);
  rows.forEach((row, i) => {
    const mid = top + i * rowH + rowH / 2;
    if (i % 2 === 0)
      s(
        "rect",
        { x: 0, y: mid - rowH / 2, width: W, height: rowH, fill: css("--sb-panel-2") },
        svg,
      );
    s(
      "text",
      { class: isCountry ? "sb-lab sb-light" : "sb-lab", x: 6, y: mid + 4, text: row.label },
      svg,
    );
    s(
      "text",
      { class: "sb-t", x: W - 6, y: mid + 4, "text-anchor": "end", text: String(row.n) },
      svg,
    );
    sets.forEach((b, j) => {
      const cy = mid + subRow(sets.length, j, bandH);
      const v = b.list.map((c) => valOf(cellOf(c, row.id))).filter((x): x is number => x != null);
      band(
        svg,
        x,
        cy,
        v,
        st.split ? 5 : isCountry ? 6 : 8,
        b.color,
        `${row.label}: ${b.label}`,
        (u) => (rel ? `${signed(u)} points` : fmt.one(u)),
      );
    });
    for (const { r, v } of row.refs) {
      const m = refMark(svg, r.id, x(v), mid);
      refInfo(m, `${r.name}: ${row.label}`, [
        [rel ? "Versus its average" : "Match", rel ? `${signed(v)} points` : fmt.one(v)],
        ["What it is", r.desc],
      ]);
    }
    hl.forEach((c, k) => {
      const cell = cellOf(c, row.id);
      const v = valOf(cell);
      if (cell == null || v == null) return;
      const j = Math.max(0, bandSetOf(sets, c));
      const cy = mid + subRow(sets.length, j, bandH) + subRow(hl.length, k, 4);
      paths[k].push([x(v), cy]);
      s(
        "text",
        {
          class: "sb-val",
          x: W - 64 - (hl.length - 1 - k) * colW - 8,
          y: mid + 4,
          "text-anchor": "end",
          text: rel ? signed(v) : fmt.one(v),
        },
        svg,
      );
      letterMark(
        svg,
        c,
        x(v),
        cy,
        [
          [row.label, `match ${fmt.one(cell[0])}`],
          ["Versus its average", `${signed(cell[1])} (${signed(cell[2])} to ${signed(cell[3])})`],
          ["Questions", String(cell[4])],
        ],
        rel ? [x(cell[2]), x(cell[3])] : undefined,
      );
    });
  });
  if (a.ordered)
    for (const p of paths) {
      if (p.length > 1) {
        const line = s(
          "polyline",
          {
            points: p.map((pt) => pt.join(",")).join(" "),
            fill: "none",
            stroke: css("--sb-ink"),
            "stroke-width": 1.2,
            "stroke-dasharray": "3 3",
            opacity: 0.6,
          },
          svg,
        );
        svg.insertBefore(line, svg.querySelector("g[role=img]"));
      }
    }

  const notes: string[] = [];
  const scores = list
    .map((c) => scoreOf(c)?.attrs[a.id])
    .filter((x): x is GroupAttrScore => x != null);
  const tally = (key: "best" | "worst") => {
    const t = new Map<string, number>();
    for (const sc of scores) t.set(sc[key], (t.get(sc[key]) ?? 0) + 1);
    return [...t.entries()].sort((p, r) => r[1] - p[1])[0];
  };
  const best = tally("best");
  const worst = tally("worst");
  if (best)
    notes.push(
      `Closest group for ${best[1]} of ${scores.length} systems: ${groupLabel(a, best[0])}.`,
    );
  if (worst)
    notes.push(
      `Furthest group for ${worst[1]} of ${scores.length} systems: ${groupLabel(a, worst[0])}.`,
    );
  const everyone = G.reference[st.ds]?.[a.id];
  if (scores.length)
    notes.push(
      `Median gap between a system's closest and furthest group: ${fmt.one(median(scores.map((sc) => sc.gap[0])))} points${everyone ? `. For all respondents' real answers it is ${fmt.one(everyone.gap[0])}` : ""}.`,
    );
  for (const c of hl) {
    const sc = scoreOf(c)?.attrs[a.id];
    if (sc)
      notes.push(
        `${letterOf(c)}, ${fullName(c)}: closest to ${groupLabel(a, sc.best)}, furthest from ${groupLabel(a, sc.worst)}, a gap of ${fmt.one(sc.gap[0])} points (95% interval ${fmt.one(sc.gap[1])} to ${fmt.one(sc.gap[2])}).`,
      );
  }
  if (isCountry)
    notes.push(
      "Countries with fewer than 20 of the questions are left out. Each country was asked a different set of questions.",
    );
  return notes;
}

function detailTable(): HTMLElement {
  const a = currentAttr();
  const list = pool();
  const hl = picked();
  const rel = st.mode === "rel";
  const head = [
    "Group",
    "Median",
    "Middle half",
    "All respondents",
    "Majority answer",
    "Random answers",
  ];
  for (const c of hl) head.push(`${letterOf(c)}: ${fullName(c)}`);
  const show = (v: number) => (rel ? signed(v) : fmt.one(v));
  const cellVal = (cell: number[] | undefined) => (cell ? show(rel ? cell[1] : cell[0]) : "—");
  const body = a.groups
    .map((g) => {
      const vals = list
        .map((c) => scoreOf(c)?.attrs[a.id]?.groups[g.id])
        .filter((c): c is [number, number, number, number, number] => c != null)
        .map((c) => (rel ? c[1] : c[0]));
      if (!vals.length) return null;
      const tds = [
        g.label,
        show(median(vals)),
        `${show(quantile(vals, 0.25))} to ${show(quantile(vals, 0.75))}`,
        ...REFS.map((r) => cellVal(r.score(a.id)?.groups[g.id])),
        ...hl.map((c) => cellVal(scoreOf(c)?.attrs[a.id]?.groups[g.id])),
      ];
      return h(
        "tr",
        null,
        tds.map((t, i) => h(i ? "td" : "th", { scope: i ? null : "row" }, t)),
      );
    })
    .filter(Boolean);
  return h(
    "table",
    { class: "sb-lb sb-gr-tbl" },
    h(
      "caption",
      null,
      `${a.label}, ${dsLabel(st.ds)}, ${list.length} systems. ${rel ? "Points relative to each system's average over these groups." : "Match, 0 to 100."}`,
    ),
    h(
      "thead",
      null,
      h(
        "tr",
        null,
        head.map((t) => h("th", { scope: "col" }, t)),
      ),
    ),
    h("tbody", null, body),
  );
}

// ---------- Chart 3: naming the group in the prompt ----------
const METHOD_OF: Record<string, SystemConfig["method"]> = {
  raw: "raw",
  synthpanel: "althing",
  althing: "althing",
  ensemble: "ensemble",
};
const condKey = (c: ConditionSet) => `${c.method}|${c.model}|${c.temperature ?? ""}`;
const condMethod = (c: ConditionSet) => METHOD_OF[c.method] ?? "raw";
const condName = (c: ConditionSet) => {
  const m = condMethod(c);
  const sys = systems().find((x) => x.baseId === c.model && x.method === m);
  const base = sys ? sys.base : c.model;
  const short = m === "baseline" ? "" : `, ${METHODS[m as ShownMethod].short}`;
  return `${base}${short}${c.temperature != null ? ` (temperature ${c.temperature})` : ""}`;
};
const condSets = () => G.conditioning.filter((c) => st.methods.has(condMethod(c)));
const condCurrent = (): ConditionSet | null =>
  st.cond ? (condSets().find((c) => condKey(c) === st.cond) ?? null) : null;
/** Conditioning runs of a highlighted system's base model and method, if any. */
const condFor = (c: SystemConfig) =>
  condSets().find((x) => x.model === c.baseId && condMethod(x) === c.method);

interface CondRow {
  a: GroupAttribute;
  id: string;
  label: string;
}
type CondLine = CondRow | { head: string };
function condRows(sets: ConditionSet[]): CondLine[] {
  const rows: CondLine[] = [];
  for (const a of attrsOf("subpop")) {
    const gs = a.groups.filter((g) => sets.some((c) => c.attrs[a.id]?.[g.id]));
    if (!gs.length) continue;
    rows.push({ head: a.label });
    for (const g of gs) rows.push({ a, id: g.id, label: g.label });
  }
  return rows;
}
function rowLayout(rows: CondLine[], top: number, rowH = 28, headH = 26) {
  let y = top;
  const ys = rows.map((r) => {
    const h0 = "head" in r ? headH : rowH;
    const cy = y + h0 / 2;
    y += h0;
    return cy;
  });
  return { ys, bottom: y };
}
const condLabelW = (rows: CondLine[]) =>
  Math.max(...rows.map((r) => ("head" in r ? 0 : textWidth(r.label, 12.5)))) + 34;
const change = (v: ConditionCell) => v[1] - v[0];

/** All conditioning runs: spread of the change in match when the group is named. */
function condAll(el: HTMLElement, W: number): string[] {
  const sets = condSets();
  if (!sets.length) {
    el.append(h("p", { class: "sb-empty" }, "No runs of this test for the selected methods."));
    return [];
  }
  const rows = condRows(sets);
  const vals = sets.flatMap((c) =>
    Object.values(c.attrs).flatMap((g) => Object.values(g).map(change)),
  );
  const D = niceMax(Math.max(...vals.map(Math.abs)), 5);
  const x = linear(-D, D, condLabelW(rows), W - 96);
  const top = 26;
  const { ys, bottom } = rowLayout(rows, top, 30);
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: bottom + 48,
    role: "img",
    "aria-label": "Change in match to each group when the prompt names the group",
  });
  el.append(svg);
  xAxis(
    svg,
    x,
    [-D, D],
    top - 6,
    bottom,
    "Change in match when the prompt names the group (points)",
    true,
  );
  s("text", { class: "sb-sub", x: x(-D) + 2, y: top - 12, text: "← further from the group" }, svg);
  s(
    "text",
    {
      class: "sb-sub",
      x: x(D) - 2,
      y: top - 12,
      "text-anchor": "end",
      text: "closer to the group →",
    },
    svg,
  );
  s("text", { class: "sb-t", x: W - 6, y: top - 12, "text-anchor": "end", text: "MEDIAN" }, svg);
  const hl = picked()
    .map((c) => ({ c, set: condFor(c) }))
    .filter((p): p is { c: SystemConfig; set: ConditionSet } => p.set != null);
  const changes: { row: CondRow; d: number }[] = [];
  rows.forEach((r, i) => {
    const cy = ys[i];
    if ("head" in r) {
      s("text", { class: "sb-t", x: 0, y: cy + 6, text: r.head.toUpperCase() }, svg);
      return;
    }
    s("text", { class: "sb-lab", x: 14, y: cy + 4, text: r.label }, svg);
    const ds = sets
      .map((c) => c.attrs[r.a.id]?.[r.id])
      .filter((v): v is ConditionCell => v != null)
      .map(change);
    for (const d of ds) changes.push({ row: r, d });
    band(
      svg,
      x,
      cy,
      ds,
      7,
      css("--sb-ink-2"),
      `${r.label}: systems tested`,
      (v) => `${signed(v)} points`,
    );
    s(
      "text",
      {
        class: "sb-val",
        x: W - 6,
        y: cy + 4,
        "text-anchor": "end",
        text: ds.length > 1 ? `${signed(median(ds))}  (${ds.length})` : `${signed(ds[0])}  (1)`,
      },
      svg,
    );
    hl.forEach(({ c, set }, k) => {
      const v = set.attrs[r.a.id]?.[r.id];
      if (!v) return;
      letterMark(svg, c, x(change(v)), cy + subRow(hl.length, k, 5), [
        ["No group named", fmt.one(v[0])],
        ["Group named", fmt.one(v[1])],
        ["Change", `${signed(change(v))} points`],
      ]);
    });
  });

  const notes: string[] = [];
  const worse = changes.filter((c) => c.d < -0.5).length;
  notes.push(
    `Naming the group made a system's answers less like that group's real answers in ${worse} of ${changes.length} cases, across ${sets.length} systems.`,
  );
  const byGroup = new Map<string, number[]>();
  for (const c of changes) byGroup.set(c.row.label, [...(byGroup.get(c.row.label) ?? []), c.d]);
  const meds = [...byGroup.entries()]
    .filter(([, v]) => v.length >= 3)
    .map(([g, v]): [string, number] => [g, median(v)])
    .sort((p, r) => r[1] - p[1]);
  if (meds.length >= 2)
    notes.push(
      `Largest median gain: ${meds[0][0]} (${signed(meds[0][1])}). Largest median loss: ${meds[meds.length - 1][0]} (${signed(meds[meds.length - 1][1])}).`,
    );
  const thin = [...byGroup.values()].filter((v) => v.length === 1).length;
  if (thin)
    notes.push(
      `${thin} groups were tested on one system only. The number in brackets is the count.`,
    );
  return notes;
}

/** One conditioning run set: arrow from default answers to answers with the group named. */
function condOne(el: HTMLElement, W: number, c: ConditionSet): string[] {
  const rows = condRows([c]);
  const random = data().references.random;
  const randomScore = random ? scoreOf(random, "subpop") : undefined;
  const rnd = (r: CondRow) => randomScore?.attrs[r.a.id]?.groups[r.id]?.[0] ?? null;
  const vals = rows.flatMap((r) => {
    if ("head" in r) return [];
    const v = c.attrs[r.a.id][r.id];
    return [v[0], v[1], rnd(r)].filter((x): x is number => x != null);
  });
  const dom: [number, number] = [
    Math.floor((Math.min(...vals) - 1) / 5) * 5,
    Math.ceil((Math.max(...vals) + 1) / 5) * 5,
  ];
  const x = linear(dom[0], dom[1], condLabelW(rows), W - 64);
  const top = 22;
  const { ys, bottom } = rowLayout(rows, top);
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: bottom + 48,
    role: "img",
    "aria-label": `${condName(c)}: match to each group before and after naming the group in the prompt`,
  });
  el.append(svg);
  xAxis(
    svg,
    x,
    dom,
    top - 6,
    bottom,
    "Match to the group's real answers (100 = identical answer shares)",
    false,
  );
  s("text", { class: "sb-t", x: W - 6, y: top - 10, "text-anchor": "end", text: "CHANGE" }, svg);
  const col = methodColor(condMethod(c));
  const defs = s("defs", null, svg);
  const mkr = s(
    "marker",
    {
      id: "gr-arrow",
      viewBox: "0 0 10 10",
      refX: 6,
      refY: 5,
      markerWidth: 6,
      markerHeight: 6,
      orient: "auto-start-reverse",
    },
    defs,
  );
  s("path", { d: "M0,0L10,5L0,10Z", fill: col }, mkr);
  const lifts: {
    label: string;
    a: GroupAttribute;
    d: number;
    after: number;
    rnd: number | null;
  }[] = [];
  rows.forEach((r, i) => {
    const cy = ys[i];
    if ("head" in r) {
      s("text", { class: "sb-t", x: 0, y: cy + 6, text: r.head.toUpperCase() }, svg);
      return;
    }
    s("text", { class: "sb-lab", x: 14, y: cy + 4, text: r.label }, svg);
    const rv = rnd(r);
    if (rv != null) {
      const m = refMark(svg, "random", x(rv), cy);
      refInfo(m, `Random answers: ${r.label}`, [["Match", fmt.one(rv)]]);
    }
    const [before, after, , n, runs] = c.attrs[r.a.id][r.id];
    const d = after - before;
    lifts.push({ label: r.label, a: r.a, d, after, rnd: rv });
    const x0 = x(before);
    const x1 = x(after);
    if (Math.abs(x1 - x0) > 12)
      s(
        "line",
        {
          x1: x0 + (x1 > x0 ? 5 : -5),
          x2: x1 + (x1 > x0 ? -8 : 8),
          y1: cy,
          y2: cy,
          stroke: col,
          "stroke-width": 2,
          "marker-end": "url(#gr-arrow)",
        },
        svg,
      );
    const info: [string, string][] = [
      ["No group named", fmt.one(before)],
      ["Group named", fmt.one(after)],
      ["Change", `${signed(d)} points`],
      ["Questions", String(n)],
      ["Runs", String(runs)],
    ];
    refInfo(
      s(
        "circle",
        { cx: x0, cy, r: 4.5, fill: css("--sb-panel"), stroke: col, "stroke-width": 2 },
        svg,
      ),
      r.label,
      info,
    );
    refInfo(
      s(
        "circle",
        { cx: x1, cy, r: 5, fill: col, stroke: css("--sb-panel"), "stroke-width": 1.5 },
        svg,
      ),
      r.label,
      info,
    );
    s(
      "text",
      {
        class: d < -0.5 ? "sb-val sb-neg-v" : "sb-val",
        x: W - 6,
        y: cy + 4,
        "text-anchor": "end",
        text: signed(d),
      },
      svg,
    );
  });

  const notes: string[] = [];
  const ups = lifts.filter((l) => l.d > 0.5).length;
  const downs = lifts.filter((l) => l.d < -0.5).length;
  notes.push(
    `Naming the group moved ${condName(c)} closer to ${ups} of ${lifts.length} groups and further from ${downs}.`,
  );
  for (const a of attrsOf("subpop")) {
    const ls = lifts.filter((l) => l.a === a).sort((p, r) => r.d - p.d);
    if (ls.length === 2 && Math.abs(ls[0].d - ls[1].d) >= 2)
      notes.push(
        `${a.label}: ${ls[0].label} ${signed(ls[0].d)}, ${ls[1].label} ${signed(ls[1].d)}.`,
      );
  }
  const below = lifts.filter((l) => l.rnd != null && l.after < l.rnd).length;
  if (below)
    notes.push(
      `With the group named, ${below} of ${lifts.length} groups are still matched worse than random answers match them.`,
    );
  return notes.slice(0, 6);
}

function condChart(el: HTMLElement, W: number): string[] {
  const c = condCurrent();
  return c ? condOne(el, W, c) : condAll(el, W);
}

// ---------- Controls ----------
function seg<T extends string>(
  label: string,
  opts: [T, string][],
  get: () => T,
  set: (v: T) => void,
): HTMLElement {
  return h(
    "div",
    { class: "sb-filter" },
    h("span", { class: "sb-lbl" }, label),
    h(
      "div",
      { class: "sb-seg", role: "radiogroup", "aria-label": label },
      opts.map(([v, text]) =>
        h(
          "button",
          {
            type: "button",
            role: "radio",
            "aria-checked": get() === v ? "true" : "false",
            class: get() === v ? "on" : null,
            onclick: () => {
              set(v);
              changed();
            },
          },
          text,
        ),
      ),
    ),
  );
}

/** Highlighted systems as removable chips, plus a type-to-search picker. */
function highlightBar(id: string): HTMLElement {
  const hl = picked();
  const listId = `${id}-systems`;
  const options = pool()
    .filter((c) => !state.compare.includes(c.key))
    .sort((p, r) => fullName(p).localeCompare(fullName(r)));
  const input = h("input", {
    type: "text",
    class: "sb-select",
    list: listId,
    placeholder: hl.length >= 3 ? "Remove one to add another" : "Type a system name",
    disabled: hl.length >= 3 ? true : null,
    "aria-label": "Highlight a system",
  });
  const pick = () => {
    const c = options.find((x) => fullName(x) === input.value);
    if (c) toggleCompare(c.key);
  };
  input.addEventListener("change", pick);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") pick();
  });
  return h(
    "div",
    { class: "sb-filter sb-gr-hl" },
    h("span", { class: "sb-lbl" }, "Highlight"),
    hl.map((c) =>
      h(
        "span",
        { class: "sb-gr-chip" },
        h("span", { class: "sb-letter" }, letterOf(c)),
        fullName(c),
        h("a", { href: profileHref(c), class: "sb-gr-prof" }, "profile"),
        h(
          "button",
          {
            type: "button",
            "aria-label": `Remove ${fullName(c)}`,
            onclick: () => toggleCompare(c.key),
          },
          "×",
        ),
      ),
    ),
    hl.length < 3 ? input : null,
    h(
      "datalist",
      { id: listId },
      options.map((c) => h("option", { value: fullName(c) })),
    ),
  );
}

const mChips = methodChips(st.methods, changed);
const status = filterStatus(() => [pool().length, eligible().length], isDefault, reset);
const dsSeg = h("div");
const variantBox = h("label", { class: "sb-toggle" });
const splitSeg = h("div");
$("gr-filters").append(dsSeg, mChips, variantBox, splitSeg, status);

function renderControls(): void {
  fill(
    dsSeg,
    seg(
      "Survey",
      DATASETS.map((d): [string, string] => [d, dsLabel(d)]),
      () => st.ds,
      (v) => {
        st.ds = v;
        st.sort = null;
        if (!attrsOf().some((a) => a.id === st.attr)) st.attr = null;
      },
    ),
  );
  fill(
    variantBox,
    h("input", {
      type: "checkbox",
      checked: st.variants ? true : null,
      onchange: (e: Event) => {
        st.variants = (e.target as HTMLInputElement).checked;
        changed();
      },
    }),
    " Experiments",
  );
  fill(
    splitSeg,
    seg(
      "Bands",
      [
        ["all", "All systems"],
        ["method", "By method"],
      ],
      () => (st.split ? "method" : "all"),
      (v) => {
        st.split = v === "method";
      },
    ),
  );
  mChips.rerender();
  status.rerender();
  fill($("gr-hl"), highlightBar("gr-hl"));
  fill($("gr-detail-hl"), highlightBar("gr-detail-hl"));

  const lean = attrsOf().some((x) => x.ordered);
  $("gr-lean").closest("section")?.classList.toggle("sb-gr-nolean", !lean);
  $("gr-lean-sub").textContent = `${dsLabel(st.ds)} · ${POPULATION[st.ds]}`;
  fill(
    $("gr-lean-legend"),
    ...bandLegend(),
    ...pickedLegend(),
    ...refLegend(["everyone", "majority", "random"]),
  );
  $("gr-lean-howto").textContent =
    "Each row is an attribute with a natural order. Right of 0 means the systems match the right-hand group better than the left-hand group. Box: middle half of the shown systems. Thin line: all of them. Short ticks: one per system. Grey marks are reference points. Hover any mark for numbers.";
  $("gr-sys-howto").textContent =
    "Ordered attributes show the gap between the two ends (+ means closer to the group named under the column). Other attributes show the gap between the closest and furthest group. Faded values have a 95% interval that includes 0. Click a row to highlight that system on the charts.";

  $("gr-sys-sub").textContent = `${dsLabel(st.ds)} · gap in points per attribute`;

  const a = currentAttr();
  $("gr-detail-title").textContent = a?.id === "COUNTRY" ? "Every country" : "Every group";
  $("gr-detail-sub").textContent =
    st.mode === "rel"
      ? `${a?.label ?? ""} · ${dsLabel(st.ds)} · versus each system's own average`
      : `${a?.label ?? ""} · ${dsLabel(st.ds)} · match score`;
  fill(
    $("gr-detail-filters"),
    seg(
      "Groups",
      attrsOf().map((x): [string, string] => [x.id, x.label]),
      () => currentAttr()?.id ?? "",
      (v) => {
        st.attr = v;
      },
    ),
  );
  fill(
    $("gr-detail-opts"),
    seg(
      "Position",
      [
        ["rel", "Versus own average"],
        ["abs", "Match score"],
      ],
      () => st.mode,
      (v) => {
        st.mode = v;
      },
    ),
  );
  fill(
    $("gr-detail-legend"),
    ...bandLegend(),
    ...pickedLegend(),
    ...refLegend(st.mode === "rel" ? ["everyone", "majority", "random"] : ["majority", "random"]),
  );
  $("gr-detail-howto").textContent =
    a?.id === "COUNTRY"
      ? 'Each row is a country, sorted by the median of the shown systems. "Versus own average" lines up systems with different overall scores. The question column is the median number of that country\'s questions each system answered.'
      : 'Each row is a group. "Versus own average" subtracts each system\'s average over these groups, so systems with different overall scores line up. Highlighted systems are joined across groups, with 95% intervals. Grey marks are reference points.';

  const sets = condSets();
  const cur = condCurrent();
  const sel = h(
    "select",
    {
      class: "sb-select",
      "aria-label": "Show before and after for one system",
      onchange: (e: Event) => {
        const v = (e.target as HTMLSelectElement).value;
        st.cond = v || null;
        changed();
      },
    },
    h("option", { value: "" }, "All systems tested"),
    sets
      .map((c): [string, string] => [condKey(c), condName(c)])
      .sort((p, r) => p[1].localeCompare(r[1]))
      .map(([k, n]) =>
        h("option", { value: k, selected: cur && condKey(cur) === k ? true : null }, n),
      ),
  );
  fill(
    $("gr-cond-filters"),
    h("div", { class: "sb-filter" }, h("span", { class: "sb-lbl" }, "Show"), sel),
  );
  $("gr-cond-sub").textContent = cur
    ? `${condName(cur)} · SubPOP`
    : `SubPOP · ${sets.length} systems tested`;
  if (!cur)
    fill(
      $("gr-cond-legend"),
      h(
        "span",
        null,
        legendSvg((g) => {
          const c = css("--sb-ink-2");
          s(
            "line",
            { x1: 1, x2: 33, y1: 7, y2: 7, stroke: c, "stroke-width": 1.5, opacity: 0.5 },
            g,
          );
          s("rect", { x: 9, y: 2, width: 16, height: 10, rx: 2, fill: c, opacity: 0.2 }, g);
          s(
            "line",
            { x1: 17, x2: 17, y1: 0, y2: 14, stroke: css("--sb-ink"), "stroke-width": 2 },
            g,
          );
        }, 34),
        "Systems tested",
      ),
      ...pickedLegend(),
    );
  else
    fill(
      $("gr-cond-legend"),
      h(
        "span",
        null,
        legendSvg((g) => {
          s(
            "circle",
            {
              cx: 8,
              cy: 7,
              r: 4.5,
              fill: css("--sb-panel"),
              stroke: css("--sb-ink-2"),
              "stroke-width": 2,
            },
            g,
          );
        }),
        "No group named",
      ),
      h(
        "span",
        null,
        legendSvg((g) => {
          s("circle", { cx: 8, cy: 7, r: 5, fill: css("--sb-ink-2") }, g);
        }),
        "Told it belongs to the group",
      ),
      ...refLegend(["random"]),
    );
  $("gr-cond-howto").textContent = cur
    ? "In the same run, the system answered each question once with no group named and once told it belongs to the group. The arrow runs from the first to the second; the change column is the difference in points."
    : "In each run, the system answered every question once with no group named and once told it belongs to the group. Right of 0 means naming the group brought the answers closer to that group's real answers. The number in brackets is how many systems were tested on that group. These are separate experiments, not the leaderboard runs.";
  $("gr-boot").textContent = String(G.bootstrap);
}

const findBox = h("input", {
  type: "search",
  class: "sb-select",
  placeholder: "Find a system",
  "aria-label": "Find a system in the table",
});
findBox.addEventListener("input", () => {
  st.find = findBox.value;
  fill($("gr-sys"), systemsTable());
});
$("gr-sys-find").append(findBox);

onChange(renderControls);
renderControls();

const leanEl = $("gr-lean");
mount(
  leanEl,
  (W) => {
    takeaways($("gr-lean-notice"), leanChart(leanEl, W));
  },
  onChange,
);
const sysEl = $("gr-sys");
const drawTable = () => fill(sysEl, systemsTable());
onChange(drawTable);
drawTable();
const detail = $("gr-detail");
mount(
  detail,
  (W) => {
    takeaways($("gr-detail-notice"), detailChart(detail, W));
    fill($("gr-table"), detailTable());
  },
  onChange,
);
const condEl = $("gr-cond");
mount(
  condEl,
  (W) => {
    takeaways($("gr-cond-notice"), condChart(condEl, W));
  },
  onChange,
);

initShell();
