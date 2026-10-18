// Phone layouts for the two Analysis charts that need label columns on both
// sides (charts.ts ladder() and byDataset()). Narrow, those were drawn
// at their minimum width and scrolled sideways, so most of the chart sat off
// screen. These fit the width instead:
//  - ladderNarrow: one row per base model, its name on a line above the row
//    and raw → persona drawn on a shared Index axis; ensembles in a second
//    group below.
//  - byDatasetNarrow: the same four dataset columns, each line ending in a
//    number keyed to a tappable list under the chart.

import { methodTag } from "./charts";
import {
  axisTicks,
  axisTitle,
  css,
  fitText,
  fmt,
  h,
  linear,
  s,
  spread,
  textWidth,
  ticks,
} from "./dom";
import {
  CORE,
  type SystemConfig,
  data,
  dsLabel,
  ensembleLabel,
  fullName,
  scoreIn,
  shortName,
} from "./model";
import {
  capRows,
  glyph,
  glyphSvg,
  highlight,
  hoverInfo,
  inspect,
  interactive,
  marker,
  methodColor,
  methodKey,
  showAllToggle,
} from "./ui";

/** Chart widths below which the Analysis page uses these layouts (the wide ones clip their end labels under ~700px). */
export const LADDER_NARROW = 720;
export const DATASETS_NARROW = 720;

const svgEl = (parent: HTMLElement, width: number, height: number, label: string) => {
  const svg = s("svg", { class: "sb-c", width, height, role: "img", "aria-label": label });
  parent.append(svg);
  return svg;
};

// ---------- Raw, persona, ensemble ----------

export function ladderNarrow(el: HTMLElement, W: number, pool: SystemConfig[]): string[] {
  const fams = [...new Set(pool.filter((c) => c.method !== "ensemble").map((c) => c.baseId))];
  const rows = fams
    .map((id) => {
      const a = pool.find((c) => c.baseId === id && c.method === "raw");
      const b = pool.find((c) => c.baseId === id && c.method === "althing");
      const va = a ? (scoreIn(a)?.v ?? null) : null;
      const vb = b ? (scoreIn(b)?.v ?? null) : null;
      const c = (a ?? b) as SystemConfig;
      return { a, b, va, vb, name: shortName(c), lab: c.lab };
    })
    .filter((r) => r.va != null || r.vb != null)
    .sort((p, q) => Math.max(q.va ?? -1e9, q.vb ?? -1e9) - Math.max(p.va ?? -1e9, p.vb ?? -1e9));
  const ens = pool
    .filter((c) => c.method === "ensemble")
    .map((c) => ({ c, v: scoreIn(c)?.v ?? null }))
    .filter((e): e is { c: SystemConfig; v: number } => e.v != null)
    .sort((p, q) => q.v - p.v);

  el.append(
    h(
      "div",
      { class: "sb-legend sb-nlegend-key" },
      h("span", null, methodKey("raw"), "Raw prompt"),
      h("span", null, methodKey("althing"), "Althing persona"),
      h("span", null, methodKey("ensemble"), "Ensemble"),
    ),
  );
  const vals = [
    ...rows.flatMap((r) => [r.va, r.vb]).filter((v): v is number => v != null),
    ...ens.map((e) => e.v),
  ];
  if (!vals.length) {
    const svg = svgEl(el, W, 80, "No systems match the current filters");
    s(
      "text",
      {
        x: W / 2,
        y: 40,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No systems match the current filters.",
      },
      svg,
    );
    return [];
  }
  const lo = Math.min(-10, Math.floor((Math.min(...vals) - 4) / 10) * 10);
  const hi = Math.max(20, Math.ceil((Math.max(...vals) + 4) / 10) * 10);
  const x = linear(lo, hi, 8, W - 40);
  const rowH = 36;
  const headH = 24;
  const groups: { title: string; n: number }[] = [
    { title: "Each model: raw prompt, then with the persona", n: rows.length },
    { title: "Ensembles: equal-weight blends", n: ens.length },
  ].filter((g) => g.n > 0);
  const plotB = groups.reduce((a, g) => a + headH + g.n * rowH, 0);
  const H = plotB + 44;
  const svg = svgEl(
    el,
    W,
    H,
    "Index with a raw prompt, with an Althing persona, and as an ensemble",
  );
  s(
    "rect",
    { x: x(lo), y: 0, width: x(0) - x(lo), height: plotB, fill: "var(--sb-zone-neg)" },
    svg,
  );
  for (const t of axisTicks(lo, hi, x, fmt.int, 5)) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 14, "text-anchor": "middle", text: fmt.int(t) },
      svg,
    );
  }
  s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
  axisTitle(svg, "SynthBench Index", { x: (x(lo) + x(hi)) / 2, y: H - 4 });

  // A row: a background strip carrying the label line (so gridlines stop
  // short of the text), then the marks on the line below.
  const labelLine = (g: Element, y0: number, lab: string | null, name: string, value: string) => {
    s("rect", { x: 0, y: y0, width: W, height: 17, fill: "var(--sb-panel)" }, g);
    const vw = textWidth(value, 12.5, 500, true) + 6;
    const nx = lab ? 19 : 0;
    if (lab) glyphSvg(g, lab, 0, y0 + 13);
    const shown = fitText(name, W - nx - vw, 12.5, 500);
    const t = s("text", { x: nx, y: y0 + 13, class: "sb-lab", text: shown }, g);
    if (shown !== name) s("title", { text: name }, t);
    s("text", { x: W, y: y0 + 13, "text-anchor": "end", class: "sb-val", text: value }, g);
  };
  const heading = (y0: number, text: string) => {
    s("rect", { x: 0, y: y0, width: W, height: headH, fill: "var(--sb-panel)" }, svg);
    s("text", { x: 0, y: y0 + 16, class: "sb-sub", text: fitText(text, W, 11.5, 400) }, svg);
  };

  let y = 0;
  if (rows.length) {
    heading(y, groups[0].title);
    y += headH;
  }
  for (const r of rows) {
    const key = (r.b ?? r.a)?.key ?? r.name;
    const g = s("g", { class: "sb-s", "data-k": key, "data-k2": r.b && r.a ? r.a.key : null }, svg);
    const value =
      r.va != null && r.vb != null ? `${fmt.int(r.va)} → ${fmt.int(r.vb)}` : fmt.int(r.va ?? r.vb);
    labelLine(g, y, r.lab, r.name, value);
    const cy = y + 26;
    if (r.va != null && r.vb != null) {
      const up = r.vb >= r.va;
      s(
        "line",
        {
          x1: x(r.va),
          x2: x(r.vb),
          y1: cy,
          y2: cy,
          stroke: up ? css("--sb-ink-2") : css("--sb-neg-ink"),
          "stroke-width": 2,
          opacity: 0.6,
        },
        g,
      );
      s(
        "text",
        {
          x: W,
          y: cy + 4,
          "text-anchor": "end",
          class: "sb-val",
          style: `fill:${up ? css("--sb-ok") : css("--sb-neg-ink")}`,
          text: fmt.delta(r.vb - r.va),
        },
        g,
      );
    }
    if (r.a && r.va != null) {
      const va = r.va;
      marker(g, "raw", x(va), cy, 5);
      interactive(
        s("circle", { class: "sb-hit", cx: x(va), cy, r: 13 }, g),
        r.a,
        () => [["Index", fmt.one(va)]],
        svg,
      );
    }
    if (r.b && r.vb != null) {
      const vb = r.vb;
      const va = r.va;
      marker(g, "althing", x(vb), cy, 5);
      interactive(
        s("circle", { class: "sb-hit", cx: x(vb), cy, r: 13 }, g),
        r.b,
        () => [
          ["Index", fmt.one(vb)],
          ...(va != null ? ([["Change vs raw", fmt.delta(vb - va)]] as [string, string][]) : []),
        ],
        svg,
      );
    }
    y += rowH;
  }
  if (ens.length) {
    heading(y, groups[groups.length - 1].title);
    y += headH;
  }
  for (const e of ens) {
    const g = s("g", { class: "sb-s", "data-k": e.c.key }, svg);
    labelLine(g, y, null, ensembleLabel(e.c.base), fmt.int(e.v));
    const cy = y + 26;
    marker(g, "ensemble", x(e.v), cy, 6);
    interactive(
      s("circle", { class: "sb-hit", cx: x(e.v), cy, r: 13 }, g),
      e.c,
      () => [["Index", fmt.one(e.v)]],
      svg,
    );
    y += rowH;
  }
  highlight(svg, null);

  const both = rows.filter(
    (r): r is typeof r & { va: number; vb: number } => r.va != null && r.vb != null,
  );
  const notes: string[] = [];
  if (both.length) {
    const best = both.reduce((p, q) => (q.vb - q.va > p.vb - p.va ? q : p));
    const worst = both.reduce((p, q) => (q.vb - q.va < p.vb - p.va ? q : p));
    notes.push(`Largest gain from the persona: ${best.name}, ${fmt.delta(best.vb - best.va)}.`);
    if (worst.vb < worst.va)
      notes.push(
        `${worst.name} scores lower with the persona (${fmt.delta(worst.vb - worst.va)}).`,
      );
    if (ens.length) {
      const top = ens[0];
      const bestSingle = Math.max(...both.flatMap((r) => [r.va, r.vb]));
      notes.push(
        `The best ensemble (${ensembleLabel(top.c.base)}) is ${fmt.delta(top.v - bestSingle)} against the best single system.`,
      );
    }
  }
  return notes;
}

// ---------- Index by dataset ----------

/** Short population notes that fit under a ~70px column. */
const AUDIENCE: Record<string, string> = {
  opinionsqa: "US adults",
  subpop: "US groups",
  gss: "US adults",
  globalopinionqa: "global",
};

export function byDatasetNarrow(
  el: HTMLElement,
  W: number,
  pool: SystemConfig[],
  cap: { limit: number; all: boolean; onToggle: () => void },
): string[] {
  const cols = [...CORE];
  const idx = (c: SystemConfig) => scoreIn(c, "all")?.v ?? Number.NEGATIVE_INFINITY;
  const rows = pool
    .filter((c) => cols.filter((id) => c.ds[id]).length >= 2)
    .sort((a, b) => idx(b) - idx(a));
  const drawn = capRows(rows, cap.limit, cap.all);
  const maj = data().references.majority;
  const majPts = maj
    ? cols
        .map((id, i) => ({ i, v: maj.ds[id]?.idx }))
        .filter((p): p is { i: number; v: number } => p.v != null)
    : [];
  const m = { l: 44, r: 30, t: 10, b: 52 };
  const H = Math.max(320, drawn.length * 14 + 120) + m.t + m.b;
  const svg = svgEl(el, W, H, "Index on each core dataset, one line per system");
  if (!rows.length) {
    s(
      "text",
      {
        x: W / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No systems match the current filters.",
      },
      svg,
    );
    return [];
  }
  const vals = [
    ...drawn.flatMap((c) => cols.map((id) => c.ds[id]?.idx).filter((v): v is number => v != null)),
    ...majPts.map((p) => p.v),
  ];
  const lo = Math.min(-30, ...vals.map((v) => v - 5));
  const hi = Math.max(50, ...vals.map((v) => v + 5));
  const step = (W - m.l - m.r - 36) / Math.max(1, cols.length - 1);
  const x = (i: number) => m.l + 18 + i * step;
  const Y = linear(lo, hi, H - m.b, m.t);
  s(
    "rect",
    { x: m.l, y: Y(0), width: W - m.l - m.r, height: Y(lo) - Y(0), fill: "var(--sb-zone-neg)" },
    svg,
  );
  for (const t of ticks(lo, hi, 5)) {
    s("line", { class: "sb-gl", x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) }, svg);
    s(
      "text",
      { class: "sb-t", x: m.l - 6, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
      svg,
    );
  }
  axisTitle(svg, "SynthBench Index", { x: 10, y: (m.t + H - m.b) / 2, vertical: true });
  s("line", { x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0), stroke: css("--sb-ink-2") }, svg);
  cols.forEach((id, i) => {
    s("line", { x1: x(i), x2: x(i), y1: m.t, y2: H - m.b, stroke: css("--sb-line-2") }, svg);
    // Names too wide for the column break at their last word boundary:
    // "GlobalOpinionQA" → "Global" / "OpinionQA".
    const name = dsLabel(id);
    const lines =
      textWidth(name) > step - 6
        ? name.replace(/^([A-Z][a-z]+)(?=[A-Z])/, "$1\n").split("\n")
        : [name];
    lines.forEach((ln, k) =>
      s(
        "text",
        { x: x(i), y: H - m.b + 16 + k * 14, "text-anchor": "middle", class: "sb-lab", text: ln },
        svg,
      ),
    );
    s(
      "text",
      {
        x: x(i),
        y: H - m.b + 16 + lines.length * 14,
        "text-anchor": "middle",
        class: "sb-sub",
        text: AUDIENCE[id] ?? "",
      },
      svg,
    );
  });

  type Lbl = { tag: string; g: SVGGElement; x0: number; y0: number; y: number };
  const labels: Lbl[] = [];
  if (majPts.length >= 2) {
    const g = s("g", null, svg);
    const pts = majPts.map((p): [number, number] => [x(p.i), Y(p.v)]);
    const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join("");
    s("path", { d, fill: "none", stroke: css("--sb-ink-2"), "stroke-width": 1.5, opacity: 0.7 }, g);
    for (const [px, py] of pts)
      s(
        "rect",
        {
          x: px - 4,
          y: py - 4,
          width: 8,
          height: 8,
          fill: css("--sb-panel"),
          stroke: css("--sb-ink-2"),
          "stroke-width": 1.5,
          transform: `rotate(45 ${px} ${py})`,
        },
        g,
      );
    const last = pts[pts.length - 1];
    labels.push({ tag: "M", g, x0: last[0], y0: last[1], y: last[1] });
    hoverInfo(
      s("path", { class: "sb-hit", d, fill: "none", stroke: "transparent", "stroke-width": 14 }, g),
      "Majority answer (reference)",
      majPts.map((p): [string, string] => [dsLabel(cols[p.i]), fmt.one(p.v)]),
    );
  }
  drawn.forEach((c, n) => {
    const g = s("g", { class: "sb-s", "data-k": c.key }, svg);
    const pts = cols
      .map((id, i): [number, number] | null => (c.ds[id] ? [x(i), Y(c.ds[id].idx)] : null))
      .filter((p): p is [number, number] => p != null);
    const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join("");
    s(
      "path",
      { d, fill: "none", stroke: methodColor(c.method), "stroke-width": 2, opacity: 0.85 },
      g,
    );
    for (const p of pts) marker(g, c.method, p[0], p[1], 4);
    const last = pts[pts.length - 1];
    labels.push({ tag: String(n + 1), g, x0: last[0], y0: last[1], y: last[1] });
    interactive(
      s("path", { class: "sb-hit", d, fill: "none", stroke: "transparent", "stroke-width": 16 }, g),
      c,
      () => cols.map((id): [string, string] => [dsLabel(id), fmt.one(c.ds[id]?.idx)]),
      svg,
    );
  });
  const lx = W - m.r + 8;
  for (const L of spread(labels, 13, m.t + 4, H - m.b)) {
    s(
      "path",
      { d: `M${L.x0 + 6},${L.y0}L${lx - 3},${L.y}`, stroke: css("--sb-line-2"), fill: "none" },
      L.g,
    );
    s("text", { x: lx, y: L.y + 4, class: "sb-val", text: L.tag }, L.g);
  }
  highlight(svg, null);

  // The key: one button per numbered line, opening its details.
  el.append(
    h(
      "ol",
      { class: "sb-nkey" },
      drawn.map((c, n) =>
        h(
          "li",
          null,
          h(
            "button",
            {
              type: "button",
              class: "sb-tap",
              "aria-label": `${n + 1}: ${fullName(c)}. Open details.`,
              onclick: () => inspect(c.key),
            },
            h("span", { class: "sb-nkey-n" }, String(n + 1)),
            methodKey(c.method),
            glyph(c.lab),
            h(
              "span",
              { class: "sb-nkey-t" },
              shortName(c),
              methodTag(c) ? h("small", null, ` ${methodTag(c)}`) : null,
            ),
            h("span", { class: "sb-nkey-v" }, fmt.int(scoreIn(c, "all")?.v)),
          ),
        ),
      ),
      majPts.length >= 2
        ? h(
            "li",
            { class: "sb-nkey-ref" },
            h("span", { class: "sb-nkey-n" }, "M"),
            h(
              "span",
              { class: "sb-nkey-t" },
              "Majority answer, a reference: always the most popular option",
            ),
          )
        : null,
    ),
  );
  const more = showAllToggle({ total: rows.length, ...cap });
  if (more) el.append(more);

  const drops = rows
    .map((c) =>
      c.ds.opinionsqa && c.ds.globalopinionqa
        ? c.ds.opinionsqa.idx - c.ds.globalopinionqa.idx
        : null,
    )
    .filter((v): v is number => v != null);
  const below = rows.filter((c) => c.ds.globalopinionqa && c.ds.globalopinionqa.idx < 0).length;
  const notes = [
    `${below} of ${rows.length} systems score below random answers on GlobalOpinionQA.`,
  ];
  if (drops.length)
    notes.unshift(
      `From OpinionsQA to GlobalOpinionQA, systems drop ${fmt.int(drops.reduce((a, b) => a + b, 0) / drops.length)} points on average.`,
    );
  const allAbove = rows.filter((c) => CORE.every((id) => (c.ds[id]?.idx ?? -1) > 0));
  if (allAbove.length && allAbove.length <= 2)
    notes.push(
      `Above random answers on every core dataset: ${allAbove.map((c) => fullName(c)).join(", ")}.`,
    );
  return notes;
}
