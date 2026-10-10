// Charts for the Overview and Analysis pages. Every chart labels its axes.

import {
  axisTitle,
  css,
  fmt,
  linear,
  logScale,
  placeLabel,
  s,
  spread,
  textWidth,
  ticks,
} from "./dom";
import {
  CORE,
  ENSEMBLE_MEMBERS,
  METHODS,
  type Ranked,
  type ShownMethod,
  type SystemConfig,
  component,
  data,
  dsLabel,
  fullName,
  scopeName,
  scoreIn,
  shortName,
} from "./model";
import { glyphSvg, highlight, hoverInfo, interactive, marker, methodColor } from "./ui";

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

// ---------- The gap: every ranked system on one 0–100 scale ----------
export function gapChart(el: HTMLElement, width: number, rows: Ranked[]): void {
  const x = linear(-40, 100, 10, width - 10);
  const laneH = 24;
  const lanes: number[] = [];
  const placed = [...rows]
    .sort((a, b) => a.v.v - b.v.v)
    .map((r) => {
      const name = `${shortName(r.c)}${r.c.method === "ensemble" ? "" : `, ${METHODS[r.c.method as ShownMethod].short}`}`;
      const px = x(Math.max(-40, r.v.v));
      const w = 22 + textWidth(name) + 8 + textWidth(fmt.int(r.v.v), 11.5, 500, true) + 10;
      let lane = 0;
      while (lanes[lane] != null && lanes[lane] > px - 8) lane++;
      lanes[lane] = px + w;
      return { ...r, name, px, lane };
    });
  const axisY = 30 + Math.max(1, lanes.length) * laneH + 18;
  const H = axisY + 92;
  const svg = svgEl(
    el,
    width,
    H,
    "Every system on the SynthBench Index scale, from random answers (0) to real people (100)",
  );
  s(
    "rect",
    { x: x(-40), y: 0, width: x(0) - x(-40), height: axisY, fill: "var(--sb-zone-neg)" },
    svg,
  );
  s("text", { x: x(-40) + 8, y: 16, class: "sb-neg-t", text: "Worse than random" }, svg);
  for (const t of [-40, -20, 0, 20, 40, 60, 80, 100]) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: axisY }, svg);
    s(
      "text",
      {
        class: "sb-t",
        x: x(t),
        y: axisY + 18,
        "text-anchor": t === -40 ? "start" : t === 100 ? "end" : "middle",
        text: fmt.int(t),
      },
      svg,
    );
  }
  s("line", { x1: x(-40), x2: x(100), y1: axisY, y2: axisY, stroke: css("--sb-line-2") }, svg);
  axisTitle(svg, "SynthBench Index (0 = random answers, 100 = a second sample of real people)", {
    x: (x(-40) + x(100)) / 2,
    y: axisY + 38,
  });
  s(
    "line",
    { x1: x(0), x2: x(0), y1: 0, y2: axisY + 6, stroke: css("--sb-ink"), "stroke-width": 1.5 },
    svg,
  );
  s(
    "line",
    { x1: x(100), x2: x(100), y1: 0, y2: axisY + 6, stroke: css("--sb-ink"), "stroke-width": 2.5 },
    svg,
  );
  s("text", { x: x(0) + 6, y: 16, class: "sb-lab", text: "0: random answers" }, svg);
  s(
    "text",
    { x: x(100) - 8, y: 16, "text-anchor": "end", class: "sb-lab", text: "100: real people" },
    svg,
  );
  s(
    "text",
    {
      x: x(100) - 8,
      y: 31,
      "text-anchor": "end",
      class: "sb-sub",
      text: "second half of the survey panel",
    },
    svg,
  );
  const maj = data().references.majority;
  const majV = maj ? scoreIn(maj)?.v : null;
  if (majV != null && majV >= -40) {
    s(
      "line",
      {
        x1: x(majV),
        x2: x(majV),
        y1: axisY - 6,
        y2: axisY + 6,
        stroke: css("--sb-ink-2"),
        "stroke-width": 1.5,
      },
      svg,
    );
    s(
      "text",
      {
        x: x(majV),
        y: axisY - 10,
        "text-anchor": "middle",
        class: "sb-sub",
        text: `Majority answer ${fmt.int(majV)}`,
      },
      svg,
    );
  }
  const best = rows[0];
  if (best) {
    const y = axisY + 68;
    const a = x(best.v.v);
    const b = x(100);
    s("line", { x1: a, x2: b, y1: y, y2: y, stroke: css("--sb-ink-2") }, svg);
    for (const xx of [a, b])
      s("line", { x1: xx, x2: xx, y1: y - 5, y2: y + 5, stroke: css("--sb-ink-2") }, svg);
    const lbl = `${fmt.int(100 - best.v.v)} points between the top system and real people`;
    const lw = textWidth(lbl, 11.5, 400);
    s(
      "rect",
      {
        x: (a + b) / 2 - lw / 2 - 6,
        y: y - 9,
        width: lw + 12,
        height: 18,
        fill: css("--sb-panel"),
      },
      svg,
    );
    s(
      "text",
      { x: (a + b) / 2, y: y + 4, "text-anchor": "middle", class: "sb-sub", text: lbl },
      svg,
    );
  }
  for (const r of placed) {
    const cy = axisY - 22 - r.lane * laneH;
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
    s(
      "line",
      { x1: r.px, x2: r.px, y1: cy + 6, y2: axisY, stroke: css("--sb-line-2"), opacity: 0.7 },
      g,
    );
    if (r.v.lo != null && r.v.hi != null)
      s(
        "rect",
        {
          x: x(Math.max(-40, r.v.lo)),
          y: cy - 2,
          width: x(Math.min(100, r.v.hi)) - x(Math.max(-40, r.v.lo)),
          height: 4,
          rx: 2,
          fill: methodColor(r.c.method),
          opacity: 0.22,
        },
        g,
      );
    marker(g, r.c.method, r.px, cy, 5);
    glyphSvg(g, r.c.lab, r.px + 10, cy + 4.5);
    s("text", { x: r.px + 30, y: cy + 4.5, class: "sb-lab sb-halo", text: r.name }, g);
    s(
      "text",
      {
        x: r.px + 30 + textWidth(r.name) + 7,
        y: cy + 4.5,
        class: "sb-val sb-halo",
        text: fmt.int(r.v.v),
      },
      g,
    );
    const hit = s(
      "rect",
      { class: "sb-hit", x: r.px - 8, y: cy - 11, width: 40 + textWidth(r.name) + 30, height: 22 },
      g,
    );
    interactive(
      hit,
      r.c,
      () => [
        ["Index", fmt.one(r.v.v)],
        ["95% interval", r.v.lo != null ? `${fmt.int(r.v.lo)} to ${fmt.int(r.v.hi)}` : "—"],
        ["Tier", r.tier == null ? "—" : `${r.tier}${r.tied > 1 ? ` (${r.tied} tied)` : ""}`],
      ],
      svg,
    );
  }
  highlight(svg, null);
}

// ---------- Raw prompt vs persona, same base model (compact) ----------
export function liftMini(el: HTMLElement, width: number): { up: number; total: number } {
  const bases = [
    ...new Set(
      data()
        .systems.filter((c) => c.method === "althing" && !c.variant)
        .map((c) => c.baseId),
    ),
  ];
  const rows = bases
    .map((id) => {
      const a = data().systems.find((c) => c.baseId === id && c.method === "raw" && !c.variant);
      const b = data().systems.find((c) => c.baseId === id && c.method === "althing" && !c.variant);
      const va = a ? scoreIn(a) : null;
      const vb = b ? scoreIn(b) : null;
      return a && b && va && vb ? { a, b, va: va.v, vb: vb.v } : null;
    })
    .filter((r): r is NonNullable<typeof r> => r != null)
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
  const raws = data().systems.filter((c) => c.method === "raw" && !c.variant && c.coverage === 3);
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
  axisTitle(svg, "Shares match: 1 − Jensen-Shannon divergence (0 to 1)", {
    x: (m.l + width - m.r) / 2,
    y: H - 8,
  });
  axisTitle(svg, "Order match: (1 + Kendall τ) ÷ 2 (0 to 1)", {
    x: 16,
    y: (m.t + H - m.b) / 2,
    vertical: true,
  });
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
    const right = cx < width - m.r - textWidth(nm) - 20;
    s(
      "text",
      {
        x: right ? cx + 11 : cx - 11,
        y: cy + (cy > H - m.b - 24 ? -10 : 4),
        "text-anchor": right ? "start" : "end",
        class: "sb-lab sb-halo",
        text: nm,
      },
      g,
    );
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
  const ens = rows.find((r) => r.c.method === "ensemble");
  if (ens)
    for (const id of ENSEMBLE_MEMBERS) {
      const p = rows.find((r) => r.c.baseId === id && r.c.method === "althing");
      if (p)
        s(
          "line",
          {
            x1: X(p.x),
            y1: Y(p.y),
            x2: X(ens.x),
            y2: Y(ens.y),
            stroke: methodColor("ensemble"),
            opacity: 0.3,
          },
          svg,
        );
    }
  const placedBoxes: [number, number, number, number][] = [];
  const points = rows.map((r): [number, number] => [X(r.x), Y(r.y)]);
  for (const r of [...rows].sort(
    (a, b) => Number(a.c.method === "raw") - Number(b.c.method === "raw"),
  )) {
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
    const cx = X(r.x);
    const cy = Y(r.y);
    marker(g, r.c.method, cx, cy, 5);
    const nm = shortName(r.c);
    const weight = r.c.method === "raw" ? 400 : 500;
    const lp = placeLabel(
      cx,
      cy,
      textWidth(nm, 12, weight),
      placedBoxes,
      points.filter(([a, b]) => a !== cx || b !== cy),
      [m.l, m.t, width - m.r, H - m.b],
    );
    s(
      "text",
      {
        x: lp.x,
        y: lp.y,
        "text-anchor": lp.anchor,
        class: `sb-halo ${r.c.method === "raw" ? "sb-lab sb-light" : "sb-lab"}`,
        style: "font-size:12px",
        text: nm,
      },
      g,
    );
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
  if (ens)
    notes.push(
      "The ensemble improves shares the most, because averaging three models evens out over-confident answers.",
    );
  return notes;
}

// ---------- Analysis: raw → persona → ensemble ----------
export function ladder(el: HTMLElement, width: number, pool: SystemConfig[]): string[] {
  const H = Math.max(420, Math.min(560, innerHeight - 320));
  const m = { l: 210, r: 210, t: 46, b: 20 };
  const cols = { raw: m.l + 20, althing: width / 2, ensemble: width - m.r - 20 };
  const fams = [...new Set(pool.filter((c) => c.method !== "ensemble").map((c) => c.baseId))];
  const ens = pool.find((c) => c.method === "ensemble");
  const ensV = ens ? scoreIn(ens) : null;
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
  if (ensV) vals.push(ensV.v);
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
      width: cols.ensemble - cols.raw + 60,
      height: Y(lo) - Y(0),
      fill: "var(--sb-zone-neg)",
    },
    svg,
  );
  for (const t of ticks(lo, hi, 6)) {
    s(
      "line",
      { class: "sb-gl", x1: cols.raw - 30, x2: cols.ensemble + 30, y1: Y(t), y2: Y(t) },
      svg,
    );
    s("text", { class: "sb-t", x: cols.ensemble + 36, y: Y(t) + 4, text: fmt.int(t) }, svg);
  }
  axisTitle(svg, "SynthBench Index", {
    x: cols.ensemble + 70,
    y: (m.t + H - m.b) / 2,
    vertical: true,
  });
  s(
    "line",
    { x1: cols.raw - 30, x2: cols.ensemble + 30, y1: Y(0), y2: Y(0), stroke: css("--sb-ink-2") },
    svg,
  );
  s(
    "text",
    {
      x: cols.ensemble + 26,
      y: Y(0) + 15,
      "text-anchor": "end",
      class: "sb-neg-t",
      text: "Below random answers",
    },
    svg,
  );
  const heads: [keyof typeof cols, string, string][] = [
    ["raw", "Raw prompt", "model as-is"],
    ["althing", "Althing persona", "same model, conditioned"],
    ["ensemble", "Ensemble", "three persona systems averaged"],
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
  for (const r of rows) {
    const key = (r.b ?? r.a)?.key ?? r.id;
    const g = s("g", { class: "sb-s", "data-k": key }, svg);
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
      if (ens && ensV && ENSEMBLE_MEMBERS.includes(r.id))
        s(
          "line",
          {
            x1: cols.althing,
            x2: cols.ensemble,
            y1: Y(vb),
            y2: Y(ensV.v),
            stroke: methodColor("ensemble"),
            "stroke-width": 1.5,
            opacity: 0.45,
          },
          g,
        );
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
    s("text", { x: cols.althing + 84, y: R.y + 4, class: "sb-sub sb-halo", text: R.r.name }, R.g);
  }
  if (ens && ensV) {
    const g = s("g", { class: "sb-s", "data-k": ens.key }, svg);
    marker(g, "ensemble", cols.ensemble, Y(ensV.v), 6);
    s(
      "text",
      {
        x: cols.ensemble + 14,
        y: Y(ensV.v) + 4,
        class: "sb-lab sb-halo",
        text: `Althing Ensemble ${fmt.int(ensV.v)}`,
      },
      g,
    );
    interactive(
      s("circle", { class: "sb-hit", cx: cols.ensemble, cy: Y(ensV.v), r: 13 }, g),
      ens,
      () => [["Index", fmt.one(ensV.v)]],
      svg,
    );
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
    if (ensV)
      notes.push(
        `The ensemble is ${fmt.delta(ensV.v - Math.max(...both.map((r) => r.vb)))} above the best single persona system.`,
      );
  }
  return notes;
}

// ---------- Analysis: Index by dataset ----------
export function byDataset(el: HTMLElement, width: number, pool: SystemConfig[]): string[] {
  const H = Math.max(420, Math.min(560, innerHeight - 320));
  const m = { l: 64, r: 230, t: 20, b: 64 };
  const cols = [...CORE];
  const sub: Record<string, string> = {
    opinionsqa: "US adults",
    subpop: "22 US subgroups",
    globalopinionqa: "cross-national",
  };
  const rows = pool.filter((c) => cols.filter((id) => c.ds[id]).length >= 2);
  const vals = rows.flatMap((c) =>
    cols.map((id) => c.ds[id]?.idx).filter((v): v is number => v != null),
  );
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
  const x = (i: number) => m.l + 50 + (i / 2) * (width - m.l - m.r - 100);
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
  axisTitle(svg, "Dataset", { x: (x(0) + x(2)) / 2, y: H - 6 });
  type Lbl = { c: SystemConfig; g: SVGGElement; x0: number; y0: number; y: number };
  const labels: Lbl[] = [];
  for (const c of rows) {
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
    glyphSvg(L.g, L.c.lab, lx, L.y + 4.5);
    const label = s(
      "text",
      { x: lx + 19, y: L.y + 4.5, class: "sb-lab", text: shortName(L.c) },
      L.g,
    );
    if (L.c.method !== "ensemble")
      s("tspan", { dx: 5, class: "sb-sub", text: METHODS[L.c.method as ShownMethod].short }, label);
  }
  highlight(svg, null);
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
      `Above random answers on all three datasets: ${allAbove.map((c) => fullName(c)).join(", ")}.`,
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
  const m = { l: 64, r: 170, t: 18, b: 52 };
  const rows = pool
    .map((c) => ({ c, x: c.cost100, v: scoreIn(c) }))
    .filter(
      (r): r is { c: SystemConfig; x: number; v: NonNullable<ReturnType<typeof scoreIn>> } =>
        r.x != null && r.x > 0 && r.v != null,
    );
  const svg = svgEl(el, width, H, "SynthBench Index versus cost per 100 questions");
  const missing = pool.filter((c) => c.cost100 == null && scoreIn(c)).length;
  if (!rows.length) {
    s(
      "text",
      {
        x: width / 2,
        y: H / 2,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No cost data for the systems shown. Cost is only recorded for raw LLM runs.",
      },
      svg,
    );
    return [];
  }
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
    ? [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2].filter((t) => t <= xmax)
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
      stroke: css("--sb-ink"),
      "stroke-width": 1.2,
      opacity: 0.5,
    },
    svg,
  );
  type Lbl = { c: SystemConfig; g: SVGGElement; x0: number; y0: number; y: number };
  const labels: Lbl[] = [];
  for (const r of rows) {
    const g = s("g", { class: "sb-s", "data-k": r.c.key }, svg);
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
    labels.push({ c: r.c, g, x0: X(r.x), y0: Y(r.v.v), y: Y(r.v.v) });
    interactive(
      s("circle", { class: "sb-hit", cx: X(r.x), cy: Y(r.v.v), r: 13 }, g),
      r.c,
      () => [
        ["Cost per 100 questions", fmt.usd(r.x)],
        ["Index", fmt.one(r.v.v)],
      ],
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
    glyphSvg(L.g, L.c.lab, lx, L.y + 4.5);
    s("text", { x: lx + 19, y: L.y + 4.5, class: "sb-lab", text: shortName(L.c) }, L.g);
  }
  if (missing)
    s(
      "text",
      {
        x: m.l + 8,
        y: m.t + 14,
        class: "sb-sub",
        text: `${missing} system${missing > 1 ? "s" : ""} not plotted: token cost isn't recorded for persona and ensemble runs yet.`,
      },
      svg,
    );
  highlight(svg, null);
  const value = rows.reduce((p, q) => (q.v.v / q.x > p.v.v / p.x ? q : p));
  const priciest = rows.reduce((p, q) => (q.x > p.x ? q : p));
  return [
    `Most Index per dollar: ${shortName(value.c)}, ${fmt.int(value.v.v)} at ${fmt.usd(value.x)} per 100 questions.`,
    `The most expensive model shown, ${shortName(priciest.c)}, scores ${fmt.int(priciest.v.v)}.`,
    "The line connects systems that no cheaper system beats.",
  ];
}
