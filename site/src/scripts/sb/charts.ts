// Charts for the Overview and Analysis pages. Every chart labels its axes.

import {
  axisTitle,
  css,
  fmt,
  linear,
  logScale,
  s,
  spread,
  textWidth,
  ticks,
  tryPlaceLabel,
} from "./dom";
import {
  CORE,
  METHODS,
  type Ranked,
  type ShownMethod,
  type SystemConfig,
  component,
  data,
  dsLabel,
  ensembleLabel,
  fullCoverage,
  fullName,
  personaPairs,
  scopeName,
  scoreIn,
  shortName,
  state,
} from "./model";
import {
  capRows,
  glyphSvg,
  highlight,
  hoverInfo,
  interactive,
  marker,
  methodColor,
  showAllToggle,
} from "./ui";

const METHOD_ORDER = Object.keys(METHODS) as ShownMethod[];

const svgEl = (
  parent: HTMLElement,
  width: number,
  height: number,
  label: string,
): SVGSVGElement => {
  const svg = s("svg", { class: "sb-c", width, height, role: "img", "aria-label": label });
  parent.append(svg);
  return svg;
};

// ---------- The gap: ranked systems as a sorted dot plot, 0 = random, 100 = people ----------

/** Method tag after a system's name. Keeps "via codex" so same-model runs stay distinct. */
export const methodTag = (c: SystemConfig): string =>
  [
    c.method === "ensemble" ? "" : METHODS[c.method as ShownMethod].short,
    c.harness ? `via ${c.harness}` : "",
  ]
    .filter(Boolean)
    .join(", ");

/** Trim text with an ellipsis so it fits in `max` px. */
function fitText(t: string, max: number, size = 12.5, weight = 500): string {
  if (textWidth(t, size, weight) <= max) return t;
  let out = t;
  while (out.length > 1 && textWidth(`${out}…`, size, weight) > max) out = out.slice(0, -1);
  return `${out.trimEnd()}…`;
}

/**
 * One row per system, sorted by Index (rows arrive sorted), labels in a fixed
 * left gutter. Scores below the -40 edge get an arrow and their value instead
 * of being pinned to the edge.
 */
export function gapChart(el: HTMLElement, width: number, rows: Ranked[]): void {
  const D0 = -40;
  const D1 = 100;
  // Narrow screens put each label on its own line above the dots.
  const narrow = width < 560;
  const rowH = narrow ? 40 : 26;
  const top = 42;
  const rankW = 26;
  const valW = 34;
  const flagW = 13;
  const tagOf = (r: Ranked) => methodTag(r.c);
  const labelW = (r: Ranked) =>
    textWidth(shortName(r.c)) +
    (tagOf(r) ? 6 + textWidth(tagOf(r), 11.5, 400) : 0) +
    (r.c.flagged ? flagW : 0);
  const gutter = narrow
    ? 0
    : Math.min(
        Math.round(width * 0.4),
        Math.ceil(rankW + 20 + Math.max(0, ...rows.map(labelW)) + 14 + valW),
      );
  const nameMax = narrow ? width - rankW - 20 - valW - 18 : gutter - rankW - 20 - valW - 14;
  const x = linear(D0, D1, narrow ? 10 : gutter + 16, width - 12);
  const plotB = top + rows.length * rowH;
  const H = plotB + 50;
  const svg = svgEl(
    el,
    width,
    H,
    `SynthBench Index of the ${rows.length} systems shown, highest first. 0 is random answers, 100 is real people.`,
  );

  // Frame: below-random zone, grid, axis.
  s(
    "rect",
    {
      x: x(D0),
      y: top - 6,
      width: x(0) - x(D0),
      height: plotB - top + 6,
      fill: "var(--sb-zone-neg)",
    },
    svg,
  );
  for (const t of [-40, -20, 0, 20, 40, 60, 80, 100]) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: top - 6, y2: plotB }, svg);
    s(
      "text",
      {
        class: "sb-t",
        x: x(t),
        y: plotB + 17,
        "text-anchor": t === D0 ? "start" : t === D1 ? "end" : "middle",
        text: fmt.int(t),
      },
      svg,
    );
  }
  s("line", { x1: x(D0), x2: x(D1), y1: plotB, y2: plotB, stroke: css("--sb-line-2") }, svg);
  axisTitle(
    svg,
    narrow
      ? "SynthBench Index"
      : "SynthBench Index (0 = random answers, 100 = a second sample of real people)",
    { x: (x(D0) + x(D1)) / 2, y: plotB + 38 },
  );

  // Reference lines, labelled in the header band.
  const vline = (v: number, y1: number, stroke: string, w: number, opacity = 1) =>
    s("line", { x1: x(v), x2: x(v), y1, y2: plotB + 6, stroke, "stroke-width": w, opacity }, svg);
  vline(0, 4, css("--sb-ink"), 1.5);
  vline(D1, 4, css("--sb-ink"), 2.5);
  // Long labels when both fit between the 0 and 100 lines, short ones otherwise.
  const refLbls = [
    ["0: random answers", "100: real people"],
    ["0: random", "100: people"],
  ].find(([a, b]) => textWidth(a) + textWidth(b) + 24 < x(D1) - x(0)) ?? ["0", "100"];
  s("text", { x: x(0) + 6, y: 14, class: "sb-lab", text: refLbls[0] }, svg);
  s("text", { x: x(D1) - 8, y: 14, "text-anchor": "end", class: "sb-lab", text: refLbls[1] }, svg);
  if (!narrow)
    s(
      "text",
      {
        x: x(D1) - 8,
        y: 30,
        "text-anchor": "end",
        class: "sb-sub",
        text: "a second sample of the survey panel",
      },
      svg,
    );
  const zoneLbl = ["Worse than random", "Below random"].find(
    (t) => textWidth(t, 11.5, 400) < x(0) - x(D0) - 12,
  );
  if (zoneLbl) s("text", { x: x(D0) + 5, y: 14, class: "sb-neg-t", text: zoneLbl }, svg);
  const maj = data().references.majority;
  const majV = maj ? scoreIn(maj)?.v : null;
  if (majV != null && majV > D0 && majV < 0) {
    // Label sits above the line's top end, so the line never runs through it.
    vline(majV, top - 4, css("--sb-ink-2"), 1, 0.7);
    const room = x(0) - x(D0) - 8;
    const lbl =
      [`Majority answer ${fmt.int(majV)}`, `Majority ${fmt.int(majV)}`].find(
        (t) => textWidth(t, 11.5, 400) < room,
      ) ?? fmt.int(majV);
    const w = textWidth(lbl, 11.5, 400);
    const lx = Math.max(x(D0) + 4, Math.min(x(0) - 6 - w, x(majV) - w / 2));
    s("text", { x: lx, y: 31, class: "sb-sub", text: lbl }, svg);
  }

  // Rows.
  rows.forEach((r, i) => {
    const y0 = top + i * rowH;
    const cy = narrow ? y0 + 28 : y0 + rowH / 2;
    const ty = narrow ? y0 + 14 : cy + 4.5;
    const col = methodColor(r.c.method);
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
    s("line", { class: "sb-gl", x1: x(D0), x2: x(D1), y1: cy, y2: cy }, g);
    const { v, lo, hi } = r.v;
    if (lo != null && hi != null && hi >= D0) {
      const a = Math.max(D0, lo);
      const b = Math.min(D1, hi);
      const stroke = { stroke: col, "stroke-width": 2, opacity: 0.55 };
      s("line", { x1: x(a), x2: x(b), y1: cy, y2: cy, ...stroke }, g);
      for (const [end, edge] of [
        [lo, D0],
        [hi, D1],
      ] as const)
        if ((end === lo && end >= D0) || (end === hi && end <= D1))
          s("line", { x1: x(end), x2: x(end), y1: cy - 4, y2: cy + 4, ...stroke }, g);
        else {
          const dir = edge === D0 ? 1 : -1;
          s(
            "path",
            {
              d: `M${x(edge) + dir * 5},${cy - 4}L${x(edge)},${cy}L${x(edge) + dir * 5},${cy + 4}`,
              fill: "none",
              ...stroke,
            },
            g,
          );
        }
    }
    if (v >= D0) marker(g, r.c.method, x(v), cy, 5);
    else {
      // Off the left edge: an arrow at the edge, with the value beside it.
      const ax = x(D0);
      s("path", { d: `M${ax},${cy}L${ax + 9},${cy - 5.5}L${ax + 9},${cy + 5.5}Z`, fill: col }, g);
      s(
        "text",
        { x: ax + 14, y: cy + 4, class: "sb-neg-t sb-halo", text: `${fmt.int(v)}, off scale` },
        g,
      );
    }
    // Label: rank, lab logo, name, method tag, holdout flag; value right-aligned.
    s("text", { x: rankW - 8, y: ty, "text-anchor": "end", class: "sb-t", text: String(i + 1) }, g);
    glyphSvg(g, r.c.lab, rankW, ty);
    const tag = tagOf(r);
    const extra = (tag ? 6 + textWidth(tag, 11.5, 400) : 0) + (r.c.flagged ? flagW : 0);
    const label = s("text", { x: rankW + 20, y: ty, class: "sb-lab sb-halo" }, g);
    s("tspan", { text: fitText(shortName(r.c), Math.max(60, nameMax - extra)) }, label);
    if (tag) s("tspan", { dx: 6, class: "sb-sub", text: tag }, label);
    if (r.c.flagged) s("tspan", { dx: 5, class: "sb-warn-t", text: "!" }, label);
    s(
      "text",
      {
        x: narrow ? x(D1) - 8 : gutter,
        y: ty,
        "text-anchor": "end",
        class: "sb-val sb-halo",
        text: fmt.int(v),
      },
      g,
    );
    interactive(
      s("rect", { class: "sb-hit", x: 0, y: y0, width, height: rowH }, g),
      r.c,
      () => [
        ["Index", fmt.one(v)],
        ["95% interval", lo != null ? `${fmt.int(lo)} to ${fmt.int(hi)}` : "—"],
        ["Tier", r.tier == null ? "—" : `${r.tier}${r.tied > 1 ? ` (${r.tied} tied)` : ""}`],
        ...(r.c.flagged
          ? ([
              [
                "Holdout check",
                `! gap above the review threshold on ${r.c.flagged} dataset${r.c.flagged > 1 ? "s" : ""}`,
              ],
            ] as [string, string][])
          : []),
      ],
      svg,
    );
  });

  // The headline gap, drawn on the top row between its interval and 100.
  const best = rows[0];
  if (best) {
    const cy = narrow ? top + 28 : top + rowH / 2;
    const a = x(Math.min(D1, Math.max(D0, best.v.hi ?? best.v.v))) + 12;
    const b = x(D1) - 6;
    const gap = fmt.int(D1 - best.v.v);
    const lbl = [
      `${gap} points between the top system and real people`,
      `${gap} points to real people`,
      `${gap} pts`,
    ].find((t) => textWidth(t, 11.5, 400) + 28 < b - a);
    if (lbl) {
      const ink = css("--sb-ink-2");
      // Annotation only: let pointer events reach the row underneath.
      const ann = s("g", { "pointer-events": "none" }, svg);
      s("line", { x1: a, x2: b, y1: cy, y2: cy, stroke: ink }, ann);
      for (const xx of [a, b])
        s("line", { x1: xx, x2: xx, y1: cy - 4, y2: cy + 4, stroke: ink }, ann);
      const lw = textWidth(lbl, 11.5, 400);
      s(
        "rect",
        {
          x: (a + b) / 2 - lw / 2 - 6,
          y: cy - 9,
          width: lw + 12,
          height: 18,
          fill: css("--sb-panel"),
        },
        ann,
      );
      s(
        "text",
        { x: (a + b) / 2, y: cy + 4, "text-anchor": "middle", class: "sb-sub", text: lbl },
        ann,
      );
    }
  }
  highlight(svg, null);
}

// ---------- Raw prompt vs persona, same base model (compact) ----------
export function liftMini(el: HTMLElement, width: number): { up: number; total: number } {
  const rows = personaPairs()
    .map((p) => ({ a: p.raw, b: p.persona, va: p.va, vb: p.vb }))
    .sort((p, q) => q.vb - q.va - (p.vb - p.va));
  const rowH = 26;
  const labelW = 92;
  const H = rows.length * rowH + 44;
  const vals = rows.flatMap((r) => [r.va, r.vb]);
  const d0 = Math.min(-10, Math.floor((Math.min(...vals, 0) - 4) / 10) * 10);
  const d1 = Math.max(20, Math.ceil((Math.max(...vals, 0) + 4) / 10) * 10);
  const x = linear(d0, d1, labelW + 8, width - 36);
  const svg = svgEl(
    el,
    width,
    H,
    "Index with a raw prompt and with an Althing persona, per base model",
  );
  const plotB = rows.length * rowH;
  for (const t of ticks(d0, d1, 4)) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 14, "text-anchor": "middle", text: fmt.int(t) },
      svg,
    );
  }
  s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
  axisTitle(svg, "SynthBench Index", { x: (x(d0) + x(d1)) / 2, y: H - 4 });
  rows.forEach((r, i) => {
    const cy = i * rowH + rowH / 2;
    const g = s("g", { class: "sb-s", "data-k": r.b.key }, svg);
    s(
      "text",
      { x: labelW, y: cy + 4, "text-anchor": "end", class: "sb-lab", text: shortName(r.a) },
      g,
    );
    s(
      "line",
      {
        x1: x(r.va),
        x2: x(r.vb),
        y1: cy,
        y2: cy,
        stroke: css("--sb-ink-2"),
        "stroke-width": 1.5,
        opacity: 0.5,
      },
      g,
    );
    marker(g, "raw", x(r.va), cy, 4.5);
    marker(g, "althing", x(r.vb), cy, 4.5);
    s(
      "text",
      { x: width, y: cy + 4, "text-anchor": "end", class: "sb-val", text: fmt.delta(r.vb - r.va) },
      g,
    );
    interactive(
      s("rect", { class: "sb-hit", x: 0, y: cy - rowH / 2, width, height: rowH }, g),
      r.b,
      () => [
        ["Raw prompt", fmt.one(r.va)],
        ["Althing persona", fmt.one(r.vb)],
        ["Change", fmt.delta(r.vb - r.va)],
      ],
      svg,
    );
  });
  return { up: rows.filter((r) => r.vb > r.va).length, total: rows.length };
}

// ---------- Random answers vs raw LLMs on shares and order (compact) ----------
export function whyMini(el: HTMLElement, width: number): void {
  const raws = data().systems.filter((c) => c.method === "raw" && !c.variant && fullCoverage(c));
  const avg = (k: "pDist" | "pRank") =>
    raws.reduce((a, c) => a + (component(c, k) ?? 0), 0) / raws.length;
  const random = data().references.random;
  const rows: [string, number, number][] = [
    ["Shares match", component(random, "pDist") ?? 0, avg("pDist")],
    ["Order match", component(random, "pRank") ?? 0, avg("pRank")],
  ];
  const labelW = 92;
  const H = rows.length * 46 + 44;
  const x = linear(0.4, 1, labelW + 8, width - 10);
  const svg = svgEl(
    el,
    width,
    H,
    "Random answers and raw LLMs compared on shares match and order match",
  );
  const plotB = rows.length * 46 + 6;
  for (const t of [0.4, 0.6, 0.8, 1]) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 14, "text-anchor": "middle", text: t.toFixed(1) },
      svg,
    );
  }
  axisTitle(svg, "Score, 0 to 1 (higher matches people better)", {
    x: (x(0.4) + x(1)) / 2,
    y: H - 4,
  });
  rows.forEach(([label, r, m], i) => {
    const cy = i * 46 + 24;
    s("text", { x: labelW, y: cy + 4, "text-anchor": "end", class: "sb-lab", text: label }, svg);
    s(
      "line",
      { x1: x(r), x2: x(m), y1: cy, y2: cy, stroke: css("--sb-line-2"), "stroke-width": 2 },
      svg,
    );
    s(
      "circle",
      { cx: x(r), cy, r: 5, fill: css("--sb-panel"), stroke: css("--sb-ink"), "stroke-width": 1.8 },
      svg,
    );
    marker(svg, "raw", x(m), cy, 5);
    s(
      "text",
      {
        x: x(r),
        y: cy - 10,
        "text-anchor": "middle",
        class: "sb-sub",
        text: `random ${r.toFixed(2)}`,
      },
      svg,
    );
    s(
      "text",
      {
        x: x(m),
        y: cy + 19,
        "text-anchor": "middle",
        class: "sb-sub",
        text: `raw LLMs ${m.toFixed(2)}`,
      },
      svg,
    );
  });
}

// ---------- Analysis: shares vs order ----------
export function sharesOrder(
  el: HTMLElement,
  width: number,
  pool: SystemConfig[],
  zoom: boolean,
): string[] {
  const H = Math.max(440, Math.min(580, innerHeight - 300));
  const m = { l: 64, r: 24, t: 16, b: 52 };
  const rows = pool
    .map((c) => ({ c, x: component(c, "pDist"), y: component(c, "pRank") }))
    .filter((r): r is { c: SystemConfig; x: number; y: number } => r.x != null && r.y != null);
  const random = data().references.random;
  const majority = data().references.majority;
  const refs = [
    {
      name: "Random answers",
      x: component(random, "pDist") ?? 0,
      y: component(random, "pRank") ?? 0,
    },
    ...(majority
      ? [
          {
            name: "Majority answer",
            x: component(majority, "pDist") ?? 0,
            y: component(majority, "pRank") ?? 0,
          },
        ]
      : []),
  ];
  const svg = svgEl(el, width, H, "Shares match versus order match for each system");
  if (!rows.length) {
    s(
      "text",
      {
        x: width / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No systems match the current filters.",
      },
      svg,
    );
    return [];
  }
  const fit = zoom ? rows : [...rows, ...refs];
  const xs = fit.map((r) => r.x);
  const ys = fit.map((r) => r.y);
  const px = Math.max(0.02, (Math.max(...xs) - Math.min(...xs)) * 0.12);
  const py = Math.max(0.02, (Math.max(...ys) - Math.min(...ys)) * 0.16);
  const x0 = Math.min(...xs) - px;
  const x1 = Math.max(...xs) + px * 1.4;
  const y0 = Math.min(...ys) - py;
  const y1 = Math.max(...ys) + py;
  const X = linear(x0, x1, m.l, width - m.r);
  const Y = linear(y0, y1, H - m.b, m.t);
  // Region scoring below random answers (shares + order below random's sum; refusal held equal).
  const c0 = refs[0].x + refs[0].y;
  const corners: [number, number][] = (
    [
      [x0, y0],
      [x1, y0],
      [x1, y1],
      [x0, y1],
    ] as [number, number][]
  ).filter(([a, b]) => a + b < c0);
  const cut = (
    [
      [x0, c0 - x0],
      [x1, c0 - x1],
      [c0 - y0, y0],
      [c0 - y1, y1],
    ] as [number, number][]
  ).filter(([a, b]) => a >= x0 - 1e-9 && a <= x1 + 1e-9 && b >= y0 - 1e-9 && b <= y1 + 1e-9);
  if (cut.length >= 2) {
    const pts = [...corners, ...cut].sort(
      (p, q) => Math.atan2(p[1] - y0, p[0] - x0) - Math.atan2(q[1] - y0, q[0] - x0),
    );
    s(
      "path",
      {
        d: `${pts.map((p, i) => `${i ? "L" : "M"}${X(p[0])},${Y(p[1])}`).join("")}Z`,
        fill: "var(--sb-zone-neg)",
      },
      svg,
    );
    cut.sort((a, b) => a[0] - b[0]);
    s(
      "line",
      {
        x1: X(cut[0][0]),
        y1: Y(cut[0][1]),
        x2: X(cut[cut.length - 1][0]),
        y2: Y(cut[cut.length - 1][1]),
        stroke: css("--sb-neg-ink"),
        opacity: 0.6,
      },
      svg,
    );
  }
  for (const t of ticks(y0, y1, 6)) {
    s("line", { class: "sb-gl", x1: m.l, x2: width - m.r, y1: Y(t), y2: Y(t) }, svg);
    s(
      "text",
      { class: "sb-t", x: m.l - 8, y: Y(t) + 4, "text-anchor": "end", text: t.toFixed(2) },
      svg,
    );
  }
  for (const t of ticks(x0, x1, 7)) {
    s("line", { class: "sb-gl", x1: X(t), x2: X(t), y1: m.t, y2: H - m.b }, svg);
    s(
      "text",
      { class: "sb-t", x: X(t), y: H - m.b + 17, "text-anchor": "middle", text: t.toFixed(2) },
      svg,
    );
  }
  // Plain axis names first; the formula is secondary.
  const xt = axisTitle(svg, "Shares match", { x: (m.l + width - m.r) / 2, y: H - 8 });
  s("tspan", { dx: 8, class: "sb-sub", text: "1 − Jensen-Shannon divergence, 0 to 1" }, xt);
  const yt = axisTitle(svg, "Order match", { x: 16, y: (m.t + H - m.b) / 2, vertical: true });
  s("tspan", { dx: 8, class: "sb-sub", text: "(1 + Kendall τ) ÷ 2, 0 to 1" }, yt);
  const placedBoxes: [number, number, number, number][] = [];
  for (const r of refs) {
    const inside = r.x >= x0 && r.x <= x1 && r.y >= y0 && r.y <= y1;
    const cx = Math.max(m.l + 8, Math.min(width - m.r - 8, X(r.x)));
    const cy = Math.max(m.t + 8, Math.min(H - m.b - 8, Y(r.y)));
    const g = s("g", null, svg);
    s(
      "rect",
      {
        x: cx - 5,
        y: cy - 5,
        width: 10,
        height: 10,
        fill: css("--sb-panel"),
        stroke: css("--sb-ink"),
        "stroke-width": 1.5,
        transform: `rotate(45 ${cx} ${cy})`,
      },
      g,
    );
    const nm = `${r.name}${inside ? "" : `, off chart at (${r.x.toFixed(2)}, ${r.y.toFixed(2)})`}`;
    const tw = textWidth(nm);
    const right = cx < width - m.r - tw - 20;
    const tx = right ? cx + 11 : cx - 11;
    const ty = cy + (cy > H - m.b - 24 ? -10 : 4);
    s(
      "text",
      {
        x: tx,
        y: ty,
        "text-anchor": right ? "start" : "end",
        class: "sb-lab sb-halo",
        text: nm,
      },
      g,
    );
    const bx = right ? tx : tx - tw;
    placedBoxes.push([bx - 2, ty - 11, bx + tw + 2, ty + 3]);
    hoverInfo(s("circle", { class: "sb-hit", cx, cy, r: 12 }, g), r.name, [
      ["Shares match", r.x.toFixed(3)],
      ["Order match", r.y.toFixed(3)],
    ]);
  }
  const defs = s("defs", null, svg);
  const ah = s(
    "marker",
    {
      id: "sb-arrow",
      viewBox: "0 0 10 10",
      refX: 8,
      refY: 5,
      markerWidth: 7,
      markerHeight: 7,
      orient: "auto",
    },
    defs,
  );
  s(
    "path",
    { d: "M1,1L9,5L1,9", fill: "none", stroke: css("--sb-ink-2"), "stroke-width": 1.6 },
    ah,
  );
  const moves: { name: string; dx: number; dy: number }[] = [];
  for (const id of new Set(rows.map((r) => r.c.baseId))) {
    const a = rows.find((r) => r.c.baseId === id && r.c.method === "raw");
    const b = rows.find((r) => r.c.baseId === id && r.c.method === "althing");
    if (!a || !b) continue;
    moves.push({ name: shortName(a.c), dx: b.x - a.x, dy: b.y - a.y });
    const dx = X(b.x) - X(a.x);
    const dy = Y(b.y) - Y(a.y);
    const L = Math.hypot(dx, dy);
    if (L > 18)
      s(
        "line",
        {
          class: "sb-s",
          "data-k": b.c.key,
          "data-k2": a.c.key,
          x1: X(a.x) + (dx / L) * 8,
          y1: Y(a.y) + (dy / L) * 8,
          x2: X(b.x) - (dx / L) * 9,
          y2: Y(b.y) - (dy / L) * 9,
          stroke: css("--sb-ink-2"),
          "stroke-width": 1.4,
          opacity: 0.7,
          "marker-end": "url(#sb-arrow)",
        },
        svg,
      );
  }
  // Ensemble-to-member links appear only while either end is hovered or inspected.
  for (const ens of rows.filter((r) => r.c.method === "ensemble"))
    for (const mem of ens.c.members) {
      const p = rows.find((r) => r.c.baseId === mem.id && r.c.method === mem.method);
      if (p)
        s(
          "line",
          {
            class: "sb-s sb-onhl",
            "data-k": ens.c.key,
            "data-k2": p.c.key,
            x1: X(p.x),
            y1: Y(p.y),
            x2: X(ens.x),
            y2: Y(ens.y),
            stroke: methodColor("ensemble"),
            "stroke-width": 1.5,
            opacity: 0.7,
          },
          svg,
        );
    }
  const points = rows.map((r): [number, number] => [X(r.x), Y(r.y)]);
  const groups = new Map<SystemConfig, SVGGElement>();
  for (const r of [...rows].sort(
    (a, b) => Number(a.c.method === "raw") - Number(b.c.method === "raw"),
  )) {
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
    groups.set(r.c, g);
    const cx = X(r.x);
    const cy = Y(r.y);
    marker(g, r.c.method, cx, cy, 5);
    interactive(
      s("circle", { class: "sb-hit", cx, cy, r: 13 }, g),
      r.c,
      () => [
        ["Shares match", r.x.toFixed(3)],
        ["Order match", r.y.toFixed(3)],
        ["Refusal match", fmt.three(component(r.c, "pRefuse"))],
        ["Index", fmt.one(scoreIn(r.c)?.v)],
      ],
      svg,
    );
  }
  // Labels: the top systems, every ensemble, the best of each method and any
  // system in the compare tray. The rest get their label on hover or focus.
  const idx = (c: SystemConfig) => scoreIn(c)?.v ?? Number.NEGATIVE_INFINITY;
  const ranked = [...rows].sort((a, b) => idx(b.c) - idx(a.c));
  const labelled = new Set<SystemConfig>(ranked.slice(0, 5).map((r) => r.c));
  for (const r of ranked) {
    if (r.c.method === "ensemble" || state.compare.includes(r.c.key)) labelled.add(r.c);
  }
  for (const meth of METHOD_ORDER) {
    const best = ranked.find((r) => r.c.method === meth);
    if (best) labelled.add(best.c);
  }
  const bounds: [number, number, number, number] = [m.l, m.t, width - m.r, H - m.b];
  const labelAt = (r: (typeof rows)[number], strict: boolean) => {
    const cx = X(r.x);
    const cy = Y(r.y);
    const nm = shortName(r.c);
    const tag = methodTag(r.c);
    const text = tag ? `${nm}, ${tag}` : nm;
    const weight = r.c.method === "raw" ? 400 : 500;
    const others = points.filter(([a, b]) => a !== cx || b !== cy);
    const w = textWidth(text, 12, weight);
    // A label with no clear spot is shown on hover only, never drawn over another.
    const fixed = strict ? tryPlaceLabel(cx, cy, w, placedBoxes, others, bounds) : null;
    const lp = fixed ??
      tryPlaceLabel(cx, cy, w, [...placedBoxes], others, bounds) ?? {
        x: cx + 10,
        y: cy + 4,
        anchor: "start" as const,
      };
    s(
      "text",
      {
        x: lp.x,
        y: lp.y,
        "text-anchor": lp.anchor,
        class: `sb-halo sb-lab${r.c.method === "raw" ? " sb-light" : ""}${fixed ? "" : " sb-onhl"}`,
        style: "font-size:12px",
        text,
      },
      groups.get(r.c),
    );
  };
  for (const r of ranked) if (labelled.has(r.c)) labelAt(r, true);
  for (const r of ranked) if (!labelled.has(r.c)) labelAt(r, false);
  highlight(svg, null);
  const raws = rows.filter((r) => r.c.method === "raw");
  const up = moves.filter((mv) => mv.dx > 0 && mv.dy > 0).length;
  const lostOrder = moves.filter((mv) => mv.dy < 0).map((mv) => mv.name);
  const notes: string[] = [];
  if (raws.length)
    notes.push(
      `Random answers score ${refs[0].x.toFixed(2)} on shares. The best raw LLM scores ${Math.max(...raws.map((r) => r.x)).toFixed(2)}. On order it is the other way round.`,
    );
  if (moves.length)
    notes.push(
      `The persona moves ${up} of ${moves.length} models up and to the right.${lostOrder.length ? ` ${lostOrder.join(", ")} loses order match.` : ""}`,
    );
  if (rows.some((r) => r.c.method === "ensemble"))
    notes.push(
      "The ensembles improve shares the most, because averaging several models evens out over-confident answers.",
    );
  return notes;
}

// ---------- Analysis: raw → persona → ensemble ----------
export function ladder(el: HTMLElement, width: number, pool: SystemConfig[]): string[] {
  const H = Math.max(420, Math.min(560, innerHeight - 320));
  const fams = [...new Set(pool.filter((c) => c.method !== "ensemble").map((c) => c.baseId))];
  const ensList = pool
    .filter((c) => c.method === "ensemble")
    .map((c) => ({ c, v: scoreIn(c)?.v ?? null }))
    .filter((e): e is { c: SystemConfig; v: number } => e.v != null);
  const ensText = (e: { c: SystemConfig; v: number }) =>
    `${ensembleLabel(e.c.base)} ${fmt.int(e.v)}`;
  // Right margin: ensemble labels, then the Index ticks and axis title at the edge.
  const ensW = Math.max(120, ...ensList.map((e) => textWidth(ensText(e))));
  const m = { l: 210, r: Math.min(width * 0.3, ensW + 90), t: 46, b: 20 };
  const cols = { raw: m.l + 20, althing: 0, ensemble: width - m.r };
  cols.althing = (cols.raw + cols.ensemble) / 2;
  const tickX = width - 26;
  const rows = fams
    .map((id) => {
      const a = pool.find((c) => c.baseId === id && c.method === "raw");
      const b = pool.find((c) => c.baseId === id && c.method === "althing");
      const va = a ? (scoreIn(a)?.v ?? null) : null;
      const vb = b ? (scoreIn(b)?.v ?? null) : null;
      return {
        id,
        a,
        b,
        va,
        vb,
        name: shortName((a ?? b) as SystemConfig),
        lab: (a ?? b)?.lab ?? "",
      };
    })
    .filter((r) => r.va != null || r.vb != null);
  const svg = svgEl(
    el,
    width,
    H,
    "Index with a raw prompt, with an Althing persona, and as an ensemble",
  );
  const vals = rows.flatMap((r) => [r.va, r.vb]).filter((v): v is number => v != null);
  for (const e of ensList) vals.push(e.v);
  if (!vals.length) {
    s(
      "text",
      {
        x: width / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No systems match the current filters.",
      },
      svg,
    );
    return [];
  }
  const lo = Math.min(-15, Math.floor((Math.min(...vals) - 5) / 10) * 10);
  const hi = Math.max(30, Math.ceil((Math.max(...vals) + 5) / 10) * 10);
  const Y = linear(lo, hi, H - m.b, m.t);
  s(
    "rect",
    {
      x: cols.raw - 30,
      y: Y(0),
      width: tickX - 26 - (cols.raw - 30),
      height: Y(lo) - Y(0),
      fill: "var(--sb-zone-neg)",
    },
    svg,
  );
  for (const t of ticks(lo, hi, 6)) {
    s("line", { class: "sb-gl", x1: cols.raw - 30, x2: tickX - 26, y1: Y(t), y2: Y(t) }, svg);
    s(
      "text",
      { class: "sb-t", x: tickX, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
      svg,
    );
  }
  axisTitle(svg, "SynthBench Index", {
    x: width - 6,
    y: (m.t + H - m.b) / 2,
    vertical: true,
  });
  s(
    "line",
    { x1: cols.raw - 30, x2: tickX - 26, y1: Y(0), y2: Y(0), stroke: css("--sb-ink-2") },
    svg,
  );
  s(
    "text",
    {
      x: tickX - 30,
      y: Y(0) + 15,
      "text-anchor": "end",
      class: "sb-neg-t",
      text: "Below random answers",
    },
    svg,
  );
  const sizes = [...new Set(ensList.map((e) => e.c.members.length))].sort((a, b) => a - b);
  const heads: [keyof typeof cols, string, string][] = [
    ["raw", "Raw prompt", "model as-is"],
    ["althing", "Althing persona", "same model, conditioned"],
    [
      "ensemble",
      "Ensemble",
      sizes.length ? `${sizes.join(" or ")} systems averaged` : "several systems averaged",
    ],
  ];
  for (const [k, l, d] of heads) {
    s(
      "line",
      { x1: cols[k], x2: cols[k], y1: m.t - 6, y2: H - m.b, stroke: css("--sb-line-2") },
      svg,
    );
    s("text", { x: cols[k], y: 16, "text-anchor": "middle", class: "sb-lab", text: l }, svg);
    s("text", { x: cols[k], y: 31, "text-anchor": "middle", class: "sb-sub", text: d }, svg);
  }
  type Lbl = { y: number; y0: number; r: (typeof rows)[number]; g: SVGGElement };
  const left: Lbl[] = [];
  const right: Lbl[] = [];
  // Links to an ensemble appear only while it or its member is hovered or inspected.
  const ensLink = (e: { c: SystemConfig; v: number }, mem: SystemConfig, x1: number, y1: number) =>
    s(
      "line",
      {
        class: "sb-s sb-onhl",
        "data-k": e.c.key,
        "data-k2": mem.key,
        x1,
        x2: cols.ensemble,
        y1,
        y2: Y(e.v),
        stroke: methodColor("ensemble"),
        "stroke-width": 1.5,
        opacity: 0.8,
      },
      svg,
    );
  for (const r of rows) {
    const key = (r.b ?? r.a)?.key ?? r.id;
    const g = s("g", { class: "sb-s", "data-k": key, "data-k2": r.b && r.a ? r.a.key : null }, svg);
    if (r.va != null && r.vb != null)
      s(
        "line",
        {
          x1: cols.raw,
          x2: cols.althing,
          y1: Y(r.va),
          y2: Y(r.vb),
          stroke: r.vb >= r.va ? css("--sb-ink-2") : css("--sb-neg-ink"),
          "stroke-width": 2,
          opacity: 0.6,
        },
        g,
      );
    for (const e of ensList)
      if (r.a && r.va != null && e.c.members.some((m) => m.id === r.id && m.method === "raw"))
        ensLink(e, r.a, cols.raw, Y(r.va));
    if (r.a && r.va != null) {
      const va = r.va;
      marker(g, "raw", cols.raw, Y(va), 5);
      interactive(
        s("circle", { class: "sb-hit", cx: cols.raw, cy: Y(va), r: 12 }, g),
        r.a,
        () => [["Index", fmt.one(va)]],
        svg,
      );
      left.push({ y: Y(va), y0: Y(va), r, g });
    }
    if (r.b && r.vb != null) {
      const vb = r.vb;
      const va = r.va;
      marker(g, "althing", cols.althing, Y(vb), 5);
      interactive(
        s("circle", { class: "sb-hit", cx: cols.althing, cy: Y(vb), r: 12 }, g),
        r.b,
        () => [
          ["Index", fmt.one(vb)],
          ...(va != null ? ([["Change vs raw", fmt.delta(vb - va)]] as [string, string][]) : []),
        ],
        svg,
      );
      right.push({ y: Y(vb), y0: Y(vb), r, g });
      for (const e of ensList.filter((e) =>
        e.c.members.some((m) => m.id === r.id && m.method === "althing"),
      ))
        ensLink(e, r.b, cols.althing, Y(vb));
    }
  }
  for (const L of spread(left, 18, m.t, H - m.b)) {
    s(
      "path",
      {
        d: `M${cols.raw - 8},${L.y0}L${cols.raw - 22},${L.y}`,
        stroke: css("--sb-line-2"),
        fill: "none",
      },
      L.g,
    );
    s(
      "text",
      {
        x: cols.raw - 26,
        y: L.y + 4,
        "text-anchor": "end",
        class: "sb-val",
        text: fmt.int(L.r.va),
      },
      L.g,
    );
    s(
      "text",
      {
        x: cols.raw - 50,
        y: L.y + 4,
        "text-anchor": "end",
        class: "sb-lab sb-halo",
        text: L.r.name,
      },
      L.g,
    );
    glyphSvg(L.g, L.r.lab, cols.raw - 70 - textWidth(L.r.name), L.y + 4.5);
  }
  for (const R of spread(right, 18, m.t, H - m.b)) {
    const d = R.r.va != null && R.r.vb != null ? R.r.vb - R.r.va : null;
    s(
      "path",
      {
        d: `M${cols.althing + 8},${R.y0}L${cols.althing + 22},${R.y}`,
        stroke: css("--sb-line-2"),
        fill: "none",
      },
      R.g,
    );
    s(
      "text",
      { x: cols.althing + 26, y: R.y + 4, class: "sb-val sb-halo", text: fmt.int(R.r.vb) },
      R.g,
    );
    if (d != null)
      s(
        "text",
        {
          x: cols.althing + 50,
          y: R.y + 4,
          class: `sb-val sb-halo ${d >= 0 ? "sb-up-t" : "sb-down-t"}`,
          style: `fill:${d >= 0 ? css("--sb-ok") : css("--sb-neg-ink")}`,
          text: fmt.delta(d),
        },
        R.g,
      );
    s(
      "text",
      { x: cols.althing + 84, y: R.y + 4, class: "sb-lab sb-light sb-halo", text: R.r.name },
      R.g,
    );
  }
  const ensLabels = ensList.map((e) => {
    const g = s("g", { class: "sb-s", "data-k": e.c.key }, svg);
    marker(g, "ensemble", cols.ensemble, Y(e.v), 6);
    interactive(
      s("circle", { class: "sb-hit", cx: cols.ensemble, cy: Y(e.v), r: 13 }, g),
      e.c,
      () => [["Index", fmt.one(e.v)]],
      svg,
    );
    return { y: Y(e.v), y0: Y(e.v), e, g };
  });
  for (const L of spread(ensLabels, 18, m.t, H - m.b))
    s(
      "text",
      {
        x: cols.ensemble + 14,
        y: L.y + 4,
        class: "sb-lab sb-halo",
        text: ensText(L.e),
      },
      L.g,
    );
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
    if (ensList.length) {
      const top = ensList.reduce((p, q) => (q.v > p.v ? q : p));
      const bestSingle = Math.max(...both.flatMap((r) => [r.va, r.vb]));
      notes.push(
        `The best ensemble (${ensembleLabel(top.c.base)}) is ${fmt.delta(top.v - bestSingle)} against the best single system.`,
      );
    }
  }
  return notes;
}

// ---------- Analysis: Index by dataset ----------
export function byDataset(
  el: HTMLElement,
  width: number,
  pool: SystemConfig[],
  cap: { limit: number; all: boolean; onToggle: () => void },
): string[] {
  let H = Math.max(420, Math.min(560, innerHeight - 320));
  const m = { l: 64, r: 230, t: 20, b: 64 };
  const lineLabel = (c: SystemConfig) => {
    const tag = methodTag(c);
    return textWidth(shortName(c)) + (tag ? 5 + textWidth(tag, 11.5, 400) : 0);
  };
  const cols = [...CORE];
  const sub: Record<string, string> = {
    opinionsqa: "US adults",
    subpop: "22 US subgroups",
    gss: "US adults, GSS",
    globalopinionqa: "cross-national",
  };
  const idx = (c: SystemConfig) => scoreIn(c, "all")?.v ?? Number.NEGATIVE_INFINITY;
  const rows = pool
    .filter((c) => cols.filter((id) => c.ds[id]).length >= 2)
    .sort((a, b) => idx(b) - idx(a));
  // The top systems by Index by default; the notes below still cover every row.
  const drawn = capRows(rows, cap.limit, cap.all);
  // Right margin fits the longest line label (lab logo + name + method tag).
  m.r = Math.min(width * 0.36, Math.max(180, ...drawn.map((c) => 22 + 19 + lineLabel(c) + 8)));
  // Tall enough for one 17px label per line plus the majority-answer reference.
  H = Math.max(H, (drawn.length + 1) * 17 + m.t + m.b);
  const maj = data().references.majority;
  const majPts = maj
    ? cols
        .map((id, i) => ({ i, v: maj.ds[id]?.idx }))
        .filter((p): p is { i: number; v: number } => p.v != null)
    : [];
  const vals = [
    ...drawn.flatMap((c) => cols.map((id) => c.ds[id]?.idx).filter((v): v is number => v != null)),
    ...majPts.map((p) => p.v),
  ];
  const svg = svgEl(el, width, H, "Index on each core dataset, one line per system");
  if (!rows.length) {
    s(
      "text",
      {
        x: width / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No systems match the current filters.",
      },
      svg,
    );
    return [];
  }
  const lo = Math.min(-30, ...vals.map((v) => v - 5));
  const hi = Math.max(50, ...vals.map((v) => v + 5));
  const x = (i: number) =>
    m.l + 50 + (i / Math.max(1, cols.length - 1)) * (width - m.l - m.r - 100);
  const Y = linear(lo, hi, H - m.b, m.t);
  s(
    "rect",
    { x: m.l, y: Y(0), width: width - m.l - m.r, height: Y(lo) - Y(0), fill: "var(--sb-zone-neg)" },
    svg,
  );
  for (const t of ticks(lo, hi, 7)) {
    s("line", { class: "sb-gl", x1: m.l, x2: width - m.r, y1: Y(t), y2: Y(t) }, svg);
    s(
      "text",
      { class: "sb-t", x: m.l - 8, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
      svg,
    );
  }
  axisTitle(svg, "SynthBench Index", { x: 16, y: (m.t + H - m.b) / 2, vertical: true });
  s("line", { x1: m.l, x2: width - m.r, y1: Y(0), y2: Y(0), stroke: css("--sb-ink-2") }, svg);
  s("text", { x: m.l + 6, y: Y(0) + 15, class: "sb-neg-t", text: "Below random answers" }, svg);
  cols.forEach((id, i) => {
    s("line", { x1: x(i), x2: x(i), y1: m.t, y2: H - m.b, stroke: css("--sb-line-2") }, svg);
    s(
      "text",
      { x: x(i), y: H - m.b + 18, "text-anchor": "middle", class: "sb-lab", text: dsLabel(id) },
      svg,
    );
    s(
      "text",
      { x: x(i), y: H - m.b + 33, "text-anchor": "middle", class: "sb-sub", text: sub[id] },
      svg,
    );
  });
  axisTitle(svg, "Dataset", { x: (x(0) + x(cols.length - 1)) / 2, y: H - 6 });
  type Lbl = { c: SystemConfig | null; g: SVGGElement; x0: number; y0: number; y: number };
  const labels: Lbl[] = [];
  // Reference: always giving each question's most popular answer.
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
    labels.push({ c: null, g, x0: last[0], y0: last[1], y: last[1] });
    hoverInfo(
      s("path", { class: "sb-hit", d, fill: "none", stroke: "transparent", "stroke-width": 14 }, g),
      "Majority answer (reference)",
      majPts.map((p): [string, string] => [dsLabel(cols[p.i]), fmt.one(p.v)]),
    );
  }
  for (const c of drawn) {
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
    labels.push({ c, g, x0: last[0], y0: last[1], y: last[1] });
    interactive(
      s("path", { class: "sb-hit", d, fill: "none", stroke: "transparent", "stroke-width": 16 }, g),
      c,
      () => cols.map((id): [string, string] => [dsLabel(id), fmt.one(c.ds[id]?.idx)]),
      svg,
    );
  }
  const lx = width - m.r + 22;
  for (const L of spread(labels, 17, m.t, H - m.b)) {
    s(
      "path",
      { d: `M${L.x0 + 7},${L.y0}L${lx - 6},${L.y}`, stroke: css("--sb-line-2"), fill: "none" },
      L.g,
    );
    if (!L.c) {
      s("text", { x: lx + 19, y: L.y + 4.5, class: "sb-sub", text: "Majority answer" }, L.g);
      continue;
    }
    glyphSvg(L.g, L.c.lab, lx, L.y + 4.5);
    const label = s(
      "text",
      { x: lx + 19, y: L.y + 4.5, class: "sb-lab", text: shortName(L.c) },
      L.g,
    );
    const tag = methodTag(L.c);
    if (tag) s("tspan", { dx: 5, class: "sb-sub", text: tag }, label);
  }
  highlight(svg, null);
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

// ---------- Analysis: cost vs Index ----------
export function costChart(
  el: HTMLElement,
  width: number,
  pool: SystemConfig[],
  log: boolean,
): string[] {
  const H = Math.max(420, Math.min(540, innerHeight - 320));
  const m = { l: 64, r: 24, t: 44, b: 52 };
  const rows = pool
    .map((c) => ({ c, x: c.cost100, v: scoreIn(c) }))
    .filter(
      (r): r is { c: SystemConfig; x: number; v: NonNullable<ReturnType<typeof scoreIn>> } =>
        r.x != null && r.x > 0 && r.v != null,
    );
  const svg = svgEl(el, width, H, "SynthBench Index versus cost per 100 questions");
  const missing = pool.filter((c) => c.cost100 == null && scoreIn(c));
  if (!rows.length) {
    s(
      "text",
      {
        x: width / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No cost data for the systems shown: their runs didn't record token cost.",
      },
      svg,
    );
    return [];
  }
  // Legend above the plot (methods shown, the frontier line, what's missing),
  // wrapped to the chart width; the plot starts below it.
  const frontierStroke = { stroke: css("--sb-ink"), "stroke-width": 1.2, opacity: 0.5 };
  type Item = {
    w: number;
    br?: boolean;
    draw: (x: number, y: number) => void;
    x: number;
    y: number;
  };
  const sub = (x: number, y: number, text: string) =>
    s("text", { x, y, class: "sb-sub", text }, svg);
  const legend: Item[] = METHOD_ORDER.filter((mm) => rows.some((r) => r.c.method === mm)).map(
    (meth) => ({
      w: 15 + textWidth(METHODS[meth].label, 11.5, 400),
      draw: (x, y) => {
        marker(svg, meth, x + 5, y - 4, 4.5);
        sub(x + 15, y, METHODS[meth].label);
      },
      x: 0,
      y: 0,
    }),
  );
  const fLong = "Best for the money: no cheaper system scores higher";
  const fText = 24 + textWidth(fLong, 11.5, 400) < width - 16 ? fLong : "Best for the money";
  legend.push({
    w: 24 + textWidth(fText, 11.5, 400),
    draw: (x, y) => {
      s(
        "line",
        { x1: x, x2: x + 18, y1: y - 4, y2: y - 4, ...frontierStroke, "stroke-width": 2 },
        svg,
      );
      sub(x + 24, y, fText);
    },
    x: 0,
    y: 0,
  });
  if (missing.length) {
    const by = METHOD_ORDER.map(
      (mm) => [mm, missing.filter((c) => c.method === mm).length] as const,
    )
      .filter(([, n]) => n)
      .map(([mm, n]) => `${n} ${METHODS[mm].short}`)
      .join(", ");
    const n = `${missing.length} system${missing.length > 1 ? "s" : ""}`;
    const long = `${n} not plotted because their runs didn't record token cost (${by}).`;
    const text =
      textWidth(long, 11.5, 400) < width - 16 ? long : `${n} not plotted: no token cost recorded.`;
    legend.push({
      w: textWidth(text, 11.5, 400),
      br: true,
      draw: (x, y) => sub(x, y, text),
      x: 0,
      y: 0,
    });
  }
  const lx0 = width < 560 ? 8 : m.l;
  let lx = lx0;
  let ly = 18;
  for (const it of legend) {
    if (lx > lx0 && (it.br || lx + it.w > width - 8)) {
      lx = lx0;
      ly += 17;
    }
    it.x = lx;
    it.y = ly;
    lx += it.w + 16;
  }
  m.t = ly + 22;
  const xmax = Math.max(3, ...rows.map((r) => r.x * 1.3));
  const X = log ? logScale(0.01, xmax, m.l, width - m.r) : linear(0, xmax, m.l, width - m.r);
  const lo = Math.min(-20, ...rows.map((r) => r.v.v - 6));
  const hi = Math.max(30, ...rows.map((r) => r.v.v + 6));
  const Y = linear(lo, hi, H - m.b, m.t);
  s(
    "rect",
    { x: m.l, y: Y(0), width: width - m.l - m.r, height: Y(lo) - Y(0), fill: "var(--sb-zone-neg)" },
    svg,
  );
  for (const t of ticks(lo, hi, 6)) {
    s("line", { class: "sb-gl", x1: m.l, x2: width - m.r, y1: Y(t), y2: Y(t) }, svg);
    s(
      "text",
      { class: "sb-t", x: m.l - 8, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
      svg,
    );
  }
  const xt = log
    ? [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50].filter((t) => t <= xmax)
    : ticks(0, xmax, 6);
  for (const t of xt) {
    s("line", { class: "sb-gl", x1: X(t), x2: X(t), y1: m.t, y2: H - m.b }, svg);
    s(
      "text",
      { class: "sb-t", x: X(t), y: H - m.b + 17, "text-anchor": "middle", text: `$${t}` },
      svg,
    );
  }
  s("line", { x1: m.l, x2: width - m.r, y1: Y(0), y2: Y(0), stroke: css("--sb-ink-2") }, svg);
  axisTitle(svg, `Cost per 100 questions in USD${log ? " (log scale)" : ""}`, {
    x: (m.l + width - m.r) / 2,
    y: H - 8,
  });
  axisTitle(svg, scopeName(), { x: 16, y: (m.t + H - m.b) / 2, vertical: true });
  const sorted = [...rows].sort((a, b) => a.x - b.x);
  const frontier: typeof rows = [];
  let best = Number.NEGATIVE_INFINITY;
  for (const r of sorted)
    if (r.v.v > best) {
      frontier.push(r);
      best = r.v.v;
    }
  s(
    "path",
    {
      d: frontier.map((r, i) => `${i ? "L" : "M"}${X(r.x)},${Y(r.v.v)}`).join(""),
      fill: "none",
      ...frontierStroke,
    },
    svg,
  );

  for (const it of legend) it.draw(it.x, it.y);

  // Direct labels for the frontier, the top score, the most expensive system and
  // anything in the compare tray; the rest show their label on hover or focus.
  const groups = new Map<SystemConfig, SVGGElement>();
  for (const r of rows) {
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
    groups.set(r.c, g);
    if (r.v.lo != null && r.v.hi != null)
      s(
        "line",
        {
          x1: X(r.x),
          x2: X(r.x),
          y1: Y(r.v.lo),
          y2: Y(r.v.hi),
          stroke: methodColor(r.c.method),
          opacity: 0.35,
          "stroke-width": 1.5,
        },
        g,
      );
    marker(g, r.c.method, X(r.x), Y(r.v.v), 5);
    interactive(
      s("circle", { class: "sb-hit", cx: X(r.x), cy: Y(r.v.v), r: 13 }, g),
      r.c,
      () => [
        ["Cost per 100 questions", fmt.usd(r.x)],
        ["Index", fmt.one(r.v.v)],
        ["Best for the money", frontier.includes(r) ? "yes" : "no"],
      ],
      svg,
    );
  }
  const top = rows.reduce((p, q) => (q.v.v > p.v.v ? q : p));
  const priciest = rows.reduce((p, q) => (q.x > p.x ? q : p));
  const labelled = [
    ...frontier,
    top,
    priciest,
    ...rows.filter((r) => state.compare.includes(r.c.key)),
  ].filter((r, i, a) => a.indexOf(r) === i);
  const points = rows.map((r): [number, number] => [X(r.x), Y(r.v.v)]);
  const placed: [number, number, number, number][] = [];
  const bounds: [number, number, number, number] = [m.l, m.t, width - m.r, H - m.b];
  const label = (r: (typeof rows)[number], strict: boolean) => {
    const cx = X(r.x);
    const cy = Y(r.v.v);
    const tag = methodTag(r.c);
    const text = `${shortName(r.c)}${tag ? `, ${tag}` : ""}`;
    const others = points.filter(([a, b]) => a !== cx || b !== cy);
    const w = textWidth(text, 12, 500);
    // A label with no clear spot is shown on hover only, never drawn over another.
    const fixed = strict ? tryPlaceLabel(cx, cy, w, placed, others, bounds) : null;
    const lp = fixed ??
      tryPlaceLabel(cx, cy, w, [...placed], others, bounds) ?? {
        x: cx + 10,
        y: cy + 4,
        anchor: "start" as const,
      };
    s(
      "text",
      {
        x: lp.x,
        y: lp.y,
        "text-anchor": lp.anchor,
        class: `sb-lab sb-halo${fixed ? "" : " sb-onhl"}`,
        style: "font-size:12px",
        text,
      },
      groups.get(r.c),
    );
  };
  for (const r of labelled) label(r, true);
  for (const r of rows) if (!labelled.includes(r)) label(r, false);
  highlight(svg, null);
  const value = rows.reduce((p, q) => (q.v.v / q.x > p.v.v / p.x ? q : p));
  return [
    `Most Index per dollar: ${fullName(value.c)}, ${fmt.int(value.v.v)} at ${fmt.usd(value.x)} per 100 questions.`,
    `The most expensive system shown, ${fullName(priciest.c)}, scores ${fmt.int(priciest.v.v)}.`,
    "The line joins the systems that are best for the money: no cheaper system scores higher.",
  ];
}
