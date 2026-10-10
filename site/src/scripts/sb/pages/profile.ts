import { axisTitle, css, fmt, h, linear, mount, s, ticks } from "../dom";
import {
  ALL,
  CORE,
  ENSEMBLE_MEMBERS,
  METHODS,
  type ShownMethod,
  type SystemConfig,
  counterpart,
  data,
  dsLabel,
  dsMeta,
  emit,
  onChange,
  pruneCompare,
  scopeName,
  scoreIn,
  state,
  systems,
  tierOf,
} from "../model";
import {
  initShell,
  marker,
  methodColor,
  methodKey,
  scopeControl,
  toggleCompare,
  writeParams,
} from "../ui";

pruneCompare();
const d = data();
const root = document.getElementById("profile") as HTMLElement;
const baseId = root.dataset.baseId ?? "";
const $ = (id: string) => document.getElementById(id) as HTMLElement;

const mine = systems().filter((c) => c.baseId === baseId && !c.variant);
const variants = systems().filter((c) => c.baseId === baseId && c.variant);
const ens = systems().find((c) => c.method === "ensemble" && !c.variant);
const inEnsemble = ENSEMBLE_MEMBERS.includes(baseId);
const options: [SystemConfig, string][] = [
  ...mine.map((c): [SystemConfig, string] => [c, METHODS[c.method as ShownMethod].label]),
  ...(inEnsemble && ens ? [[ens, "As part of the ensemble"] as [SystemConfig, string]] : []),
];
const fromUrl = new URLSearchParams(location.search).get("method");
let cur: SystemConfig =
  options.find(([c]) => c.method === fromUrl)?.[0] ??
  mine.find((c) => c.method === "althing") ??
  mine[0];

const median = (a: number[]) => {
  const q = [...a].sort((x, y) => x - y);
  const m = q.length >> 1;
  return q.length % 2 ? q[m] : (q[m - 1] + q[m]) / 2;
};
const others = (id: string, me: SystemConfig | null) =>
  systems().filter((c) => !c.variant && c.ds[id] && c !== me);
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

$("pf-filters").append(scopeControl());

// ---------- Method switch ----------
function renderMethod(): void {
  $("pf-method").replaceChildren(
    h("span", { class: "sb-lbl" }, "Method"),
    h(
      "div",
      { class: "sb-seg", role: "radiogroup", "aria-label": "Method" },
      options.map(([c, label]) =>
        h(
          "button",
          {
            type: "button",
            role: "radio",
            "aria-checked": c === cur ? "true" : "false",
            class: c === cur ? "on" : null,
            onclick: () => {
              cur = c;
              writeParams({ method: c.method });
              emit();
            },
          },
          h("span", { class: "sb-inl" }, methodKey(c.method), label),
        ),
      ),
    ),
    h(
      "button",
      { type: "button", class: "sb-btn sb-btn-sm", onclick: () => toggleCompare(cur.key) },
      state.compare.includes(cur.key) ? "Remove from compare" : "Add to compare",
    ),
  );
}

// ---------- Headline numbers ----------
function renderStats(): void {
  const v = scoreIn(cur);
  const tr = tierOf(cur);
  const cp = counterpart(cur);
  const vals = CORE.filter((id) => cur.ds[id]).map((id): [string, number] => [id, cur.ds[id].idx]);
  const best = vals.length ? vals.reduce((a, b) => (b[1] > a[1] ? b : a)) : null;
  const worst = vals.length ? vals.reduce((a, b) => (b[1] < a[1] ? b : a)) : null;
  const vsRandom =
    v?.lo == null || v.hi == null ? "—" : v.lo > 0 ? "Above" : v.hi < 0 ? "Below" : "Tied";
  let lift: number | null = null;
  if (cp) {
    const a = scoreIn(cur.method === "raw" ? cur : cp);
    const b = scoreIn(cur.method === "raw" ? cp : cur);
    if (a && b) lift = b.v - a.v;
  }
  const bestPersona = Math.max(
    ...systems()
      .filter((c) => c.method === "althing" && !c.variant)
      .map((c) => scoreIn(c)?.v ?? Number.NEGATIVE_INFINITY),
  );
  const effect =
    cur.method === "ensemble"
      ? v && Number.isFinite(bestPersona)
        ? v.v - bestPersona
        : null
      : lift;
  const stat = (k: string, val: string, sub: string, color?: string) =>
    h(
      "div",
      null,
      h("div", { class: "k" }, k),
      h("div", { class: "v", style: color ? { color } : null }, val),
      h("div", { class: "d" }, sub),
    );
  $("pf-stats").replaceChildren(
    stat(
      scopeName(),
      v ? fmt.int(v.v) : "—",
      tr?.tier != null
        ? `Tier ${tr.tier}${tr.tied > 1 ? `, tied with ${tr.tied - 1} other${tr.tied > 2 ? "s" : ""}` : ", alone"}`
        : "Not ranked on this score",
    ),
    stat(
      "Compared with random answers",
      vsRandom,
      v?.lo != null ? `95% interval ${fmt.int(v.lo)} to ${fmt.int(v.hi)}` : "",
    ),
    stat(
      cur.method === "ensemble" ? "Ensemble vs. best single persona" : "Persona effect",
      fmt.delta(effect),
      cur.method === "ensemble" ? "Index points" : "Althing persona minus raw prompt",
      effect == null ? undefined : effect >= 0 ? css("--sb-ok") : css("--sb-neg-ink"),
    ),
    stat(
      "Range across core datasets",
      worst && best ? `${fmt.int(worst[1])} to ${fmt.int(best[1])}` : "—",
      worst ? `Lowest on ${dsLabel(worst[0])}` : "",
    ),
  );
  const field = systems()
    .filter((c) => !c.variant && c.coverage === 3 && c.index != null)
    .map((c) => c.index as number);
  const m = field.length ? median(field) : 0;
  const who =
    cur.method === "ensemble"
      ? "The Althing Ensemble"
      : `${cur.base} with ${cur.method === "raw" ? "a raw prompt" : "an Althing persona"}`;
  const parts: string[] = [];
  if (cur.index != null)
    parts.push(
      `${who} has an Index of ${fmt.int(cur.index)}, ${cur.index > m + 5 ? "above" : cur.index < m - 5 ? "below" : "close to"} the median system (${fmt.int(m)}).`,
    );
  else parts.push(`${who} wasn't run on all three core datasets, so it has no headline Index.`);
  if (best && worst && best[0] !== worst[0])
    parts.push(
      `It does best on ${dsLabel(best[0])} (${fmt.int(best[1])}) and worst on ${dsLabel(worst[0])} (${fmt.int(worst[1])}${worst[1] < 0 ? ", below random answers" : ""}).`,
    );
  if (lift != null && cur.method !== "ensemble")
    parts.push(
      `On this score, the persona ${lift >= 0 ? "adds" : "subtracts"} ${Math.abs(Math.round(lift))} points.`,
    );
  $("pf-summary").textContent = parts.join(" ");
}

// ---------- By dataset, against the field ----------
const dsEl = $("pf-ds");
mount(
  dsEl,
  (W) => {
    const cp = counterpart(cur);
    const ids = ALL.filter((id) => cur.ds[id] || cp?.ds[id]);
    const rowH = 48;
    const labelW = 128;
    const H = ids.length * rowH + 44;
    const plotB = ids.length * rowH;
    const x = linear(-40, 60, labelW + 10, W - 36);
    const svg = s("svg", {
      class: "sb-c",
      width: W,
      height: H,
      role: "img",
      "aria-label": "Index by dataset compared with all other systems",
    });
    dsEl.append(svg);
    s(
      "rect",
      { x: x(-40), y: 0, width: x(0) - x(-40), height: plotB, fill: "var(--sb-zone-neg)" },
      svg,
    );
    for (const t of [-40, -20, 0, 20, 40, 60]) {
      s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
      s(
        "text",
        { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: fmt.int(t) },
        svg,
      );
    }
    s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
    axisTitle(svg, "SynthBench Index (0 = random answers)", { x: (x(-40) + x(60)) / 2, y: H - 4 });
    ids.forEach((id, i) => {
      const cy = i * rowH + rowH / 2;
      s(
        "text",
        {
          x: labelW,
          y: cy - 1,
          "text-anchor": "end",
          class: "sb-lab",
          text: `${dsLabel(id)}${id === "gss" ? " †" : ""}`,
        },
        svg,
      );
      s(
        "text",
        {
          x: labelW,
          y: cy + 13,
          "text-anchor": "end",
          class: "sb-sub",
          text: `${dsMeta(id)?.questions ?? "?"} questions`,
        },
        svg,
      );
      const f = others(id, null).map((o) => o.ds[id].idx);
      if (f.length) {
        const lo = clamp(Math.min(...f), -40, 60);
        const hi = clamp(Math.max(...f), -40, 60);
        s(
          "rect",
          {
            x: x(lo),
            y: cy - 12,
            width: Math.max(2, x(hi) - x(lo)),
            height: 24,
            rx: 3,
            fill: css("--sb-grid"),
          },
          svg,
        );
        const md = clamp(median(f), -40, 60);
        s(
          "line",
          {
            x1: x(md),
            x2: x(md),
            y1: cy - 12,
            y2: cy + 12,
            stroke: css("--sb-ink-2"),
            "stroke-width": 1.5,
          },
          svg,
        );
      }
      const pairs: [SystemConfig, number, boolean][] = [
        [cur, cp ? -5 : 0, true],
        ...(cp ? [[cp, 6, false] as [SystemConfig, number, boolean]] : []),
      ];
      for (const [c, off, isCur] of pairs) {
        const v = c.ds[id];
        if (!v) continue;
        const g = s("g", { opacity: isCur ? 1 : 0.45 }, svg);
        if (v.lo != null && v.hi != null)
          s(
            "line",
            {
              x1: x(clamp(v.lo, -40, 60)),
              x2: x(clamp(v.hi, -40, 60)),
              y1: cy + off,
              y2: cy + off,
              stroke: methodColor(c.method),
              "stroke-width": 2,
            },
            g,
          );
        marker(g, c.method, x(clamp(v.idx, -40, 60)), cy + off, isCur ? 5.5 : 4.5);
      }
      if (cur.ds[id])
        s(
          "text",
          {
            x: W - 2,
            y: cy + 4,
            "text-anchor": "end",
            class: "sb-val",
            text: fmt.int(cur.ds[id].idx),
          },
          svg,
        );
    });
    if (cp)
      dsEl.prepend(
        h(
          "div",
          { class: "sb-legend" },
          h("span", null, methodKey(cur.method), METHODS[cur.method as ShownMethod].label),
          h(
            "span",
            { style: { opacity: "0.5" } },
            methodKey(cp.method),
            `${METHODS[cp.method as ShownMethod].label} (same model)`,
          ),
        ),
      );
  },
  onChange,
);

// ---------- Components ----------
function renderComponents(): void {
  const ids = CORE.filter((id) => cur.ds[id]);
  const random = d.references.random;
  const bullet = (val: number, r: number) => {
    const W = 88;
    const b = s("svg", {
      class: "sb-c",
      width: W,
      height: 14,
      "aria-hidden": "true",
      style: "display:inline-block;vertical-align:middle",
    });
    const x = linear(0.4, 1, 0, W);
    s("rect", { x: 0, y: 4, width: W, height: 6, rx: 3, fill: css("--sb-grid") }, b);
    s(
      "rect",
      { x: 0, y: 4, width: x(Math.max(0.4, val)), height: 6, rx: 3, fill: methodColor(cur.method) },
      b,
    );
    s(
      "line",
      { x1: x(r), x2: x(r), y1: 0, y2: 14, stroke: css("--sb-neg-ink"), "stroke-width": 2 },
      b,
    );
    return b;
  };
  const rows: ["pDist" | "pRank" | "pRefuse", string][] = [
    ["pDist", "Shares match"],
    ["pRank", "Order match"],
    ["pRefuse", "Refusal match"],
  ];
  $("pf-comp").replaceChildren(
    h(
      "thead",
      null,
      h(
        "tr",
        null,
        h("th", { scope: "col" }, "Component"),
        ids.map((id) => h("th", { scope: "col" }, dsLabel(id))),
      ),
    ),
    h(
      "tbody",
      null,
      rows.map(([k, label]) =>
        h(
          "tr",
          null,
          h("td", { class: "sb-strong" }, label),
          ids.map((id) => {
            const val = cur.ds[id][k];
            const r = random.ds[id]?.[k] ?? 0;
            return h(
              "td",
              { class: "nowrap" },
              bullet(val, r),
              h("span", { class: "sb-mono sb-cellnum" }, val.toFixed(2)),
              h(
                "div",
                { class: val >= r ? "sb-ok sb-small" : "sb-down sb-small" },
                `${val >= r ? "+" : "−"}${Math.abs(val - r).toFixed(2)} vs. random`,
              ),
            );
          }),
        ),
      ),
    ),
  );
}

// ---------- Topics ----------
let topicDs = "opinionsqa";
const topicsEl = $("pf-topics");
function renderTopicTabs(): string[] {
  const avail = ALL.filter((id) => cur.ds[id] && Object.keys(cur.ds[id].topicIdx).length);
  if (!avail.includes(topicDs as (typeof ALL)[number])) topicDs = avail[0] ?? "";
  $("pf-topic-ds").replaceChildren(
    h("span", { class: "sb-lbl" }, "Dataset"),
    h(
      "div",
      { class: "sb-seg", role: "radiogroup", "aria-label": "Topic dataset" },
      avail.map((id) =>
        h(
          "button",
          {
            type: "button",
            role: "radio",
            "aria-checked": id === topicDs ? "true" : "false",
            class: id === topicDs ? "on" : null,
            onclick: () => {
              topicDs = id;
              emit();
            },
          },
          dsLabel(id),
        ),
      ),
    ),
  );
  return avail;
}
mount(
  topicsEl,
  (W) => {
    const avail = renderTopicTabs();
    if (!avail.length) {
      $("pf-topic-q").textContent = "No per-topic scores for this system.";
      return;
    }
    $("pf-topic-q").textContent =
      `Index per topic on ${dsLabel(topicDs)}. Dark tick: median of other systems. Faded rows have fewer than 10 questions.`;
    const ds = cur.ds[topicDs];
    const topics = Object.keys(ds.topicIdx).sort((a, b) => ds.topicIdx[b] - ds.topicIdx[a]);
    const rowH = 26;
    const labelW = Math.min(240, W * 0.3);
    const plotB = topics.length * rowH;
    const H = plotB + 44;
    const x = linear(-100, 60, labelW + 10, W - 70);
    const svg = s("svg", {
      class: "sb-c",
      width: W,
      height: H,
      role: "img",
      "aria-label": "Index per topic",
    });
    topicsEl.append(svg);
    s(
      "rect",
      { x: x(-100), y: 0, width: x(0) - x(-100), height: plotB, fill: "var(--sb-zone-neg)" },
      svg,
    );
    for (const t of [-100, -50, 0, 50]) {
      s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
      s(
        "text",
        { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: fmt.int(t) },
        svg,
      );
    }
    s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
    axisTitle(svg, "SynthBench Index on this topic (0 = random answers)", {
      x: (x(-100) + x(60)) / 2,
      y: H - 4,
    });
    axisTitle(svg, "Questions", { x: W - 2, y: plotB + 15, anchor: "end" });
    topics.forEach((t, i) => {
      const cy = i * rowH + rowH / 2;
      const n = ds.topicN[t];
      const val = ds.topicIdx[t];
      const g = s("g", { opacity: n < 10 ? 0.4 : 1 }, svg);
      s(
        "text",
        { x: labelW, y: cy + 4, "text-anchor": "end", class: "sb-lab sb-light", text: t },
        g,
      );
      const peer = others(topicDs, cur)
        .map((o) => o.ds[topicDs].topicIdx[t])
        .filter((p): p is number => p != null);
      s(
        "line",
        {
          x1: x(0),
          x2: x(clamp(val, -100, 60)),
          y1: cy,
          y2: cy,
          stroke: methodColor(cur.method),
          "stroke-width": 2,
          opacity: 0.5,
        },
        g,
      );
      if (peer.length) {
        const md = clamp(median(peer), -100, 60);
        s(
          "line",
          {
            x1: x(md),
            x2: x(md),
            y1: cy - 7,
            y2: cy + 7,
            stroke: css("--sb-ink"),
            "stroke-width": 2,
          },
          g,
        );
      }
      marker(g, cur.method, x(clamp(val, -100, 60)), cy, 4.5);
      if (val < -100)
        s("text", { x: x(-100) + 4, y: cy + 4, class: "sb-neg-t", text: `◀ ${fmt.int(val)}` }, g);
      s("text", { class: "sb-t", x: W - 2, y: cy + 4, "text-anchor": "end", text: String(n) }, g);
    });
  },
  onChange,
);

// ---------- Experiments (only for models that have them) ----------
const sweep = (d.findings.temperature_sweep ?? []).filter(
  (p) => p.model === mine[0]?.base && (p.dataset ?? "opinionsqa") === "opinionsqa",
);
const templates = variants.filter((c) => c.variant?.startsWith("temperature 0.85") && c.ds.subpop);
if (!sweep.length && !templates.length) $("pf-exp").remove();
else {
  const oq = dsMeta("opinionsqa");
  const toIdx = (sps: number) =>
    oq ? (100 * (sps - oq.random)) / ((oq.ceiling ?? 1) - oq.random) : 0;
  const tempEl = $("pf-temp");
  mount(tempEl, (W) => {
    const H = 220;
    const m = { l: 56, r: 12, t: 12, b: 46 };
    const svg = s("svg", {
      class: "sb-c",
      width: W,
      height: H,
      role: "img",
      "aria-label": "Index by sampling temperature",
    });
    tempEl.append(svg);
    if (!sweep.length) {
      s(
        "text",
        {
          x: W / 2,
          y: H / 2,
          "text-anchor": "middle",
          class: "sb-sub",
          text: "No temperature sweep for this model yet.",
        },
        svg,
      );
      return;
    }
    const pts = sweep.map((p) => ({
      x: p.temperature,
      y: toIdx(p.sps),
      sd: toIdx(p.sps + (p.std ?? 0)) - toIdx(p.sps),
    }));
    const xs = pts.map((p) => p.x);
    const lo = Math.floor((Math.min(...pts.map((p) => p.y - p.sd)) - 3) / 5) * 5;
    const hi = Math.ceil((Math.max(...pts.map((p) => p.y + p.sd)) + 3) / 5) * 5;
    const X = linear(Math.min(...xs) - 0.05, Math.max(...xs) + 0.05, m.l, W - m.r);
    const Y = linear(lo, hi, H - m.b, m.t);
    for (const t of ticks(lo, hi, 4)) {
      s("line", { class: "sb-gl", x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) }, svg);
      s(
        "text",
        { class: "sb-t", x: m.l - 6, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
        svg,
      );
    }
    for (const p of pts)
      s(
        "text",
        { class: "sb-t", x: X(p.x), y: H - m.b + 16, "text-anchor": "middle", text: String(p.x) },
        svg,
      );
    axisTitle(svg, "Sampling temperature", { x: (m.l + W - m.r) / 2, y: H - 6 });
    axisTitle(svg, "Index (OpinionsQA)", { x: 14, y: (m.t + H - m.b) / 2, vertical: true });
    const band = `${pts.map((p, i) => `${i ? "L" : "M"}${X(p.x)},${Y(p.y + p.sd)}`).join("")}${[
      ...pts,
    ]
      .reverse()
      .map((p) => `L${X(p.x)},${Y(p.y - p.sd)}`)
      .join("")}Z`;
    s("path", { d: band, fill: methodColor("althing"), opacity: 0.14 }, svg);
    s(
      "path",
      {
        d: pts.map((p, i) => `${i ? "L" : "M"}${X(p.x)},${Y(p.y)}`).join(""),
        fill: "none",
        stroke: methodColor("althing"),
        "stroke-width": 2,
      },
      svg,
    );
    for (const p of pts) marker(svg, "althing", X(p.x), Y(p.y), 3.5);
  });
  const tplEl = $("pf-tpl");
  mount(tplEl, (W) => {
    const rows = [...templates].sort((a, b) => b.ds.subpop.idx - a.ds.subpop.idx);
    const rowH = 32;
    const labelW = 150;
    const plotB = rows.length * rowH;
    const H = plotB + 44;
    const svg = s("svg", {
      class: "sb-c",
      width: W,
      height: H,
      role: "img",
      "aria-label": "Index by persona prompt template",
    });
    tplEl.append(svg);
    if (!rows.length) {
      s(
        "text",
        {
          x: W / 2,
          y: H / 2 + 20,
          "text-anchor": "middle",
          class: "sb-sub",
          text: "No template comparison for this model yet.",
        },
        svg,
      );
      return;
    }
    const lo = Math.min(-20, Math.floor(Math.min(...rows.map((c) => c.ds.subpop.idx)) / 20) * 20);
    const hi = Math.max(20, Math.ceil(Math.max(...rows.map((c) => c.ds.subpop.idx)) / 20) * 20);
    const x = linear(lo, hi, labelW + 10, W - 40);
    for (const t of ticks(lo, hi, 5)) {
      s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
      s(
        "text",
        { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: fmt.int(t) },
        svg,
      );
    }
    s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
    axisTitle(svg, "Index on SubPOP (0 = random answers)", { x: (x(lo) + x(hi)) / 2, y: H - 4 });
    rows.forEach((c, i) => {
      const cy = i * rowH + rowH / 2;
      const v = c.ds.subpop.idx;
      const tpl = c.variant?.match(/(\w+) template/)?.[1];
      s(
        "text",
        {
          x: labelW,
          y: cy + 4,
          "text-anchor": "end",
          class: "sb-lab sb-light",
          text: tpl ? `${tpl} template` : "default template",
        },
        svg,
      );
      s(
        "rect",
        {
          x: x(Math.min(0, v)),
          y: cy - 7,
          width: Math.abs(x(v) - x(0)),
          height: 14,
          rx: 2,
          fill: methodColor("althing"),
          opacity: v < 0 ? 0.55 : 1,
        },
        svg,
      );
      s(
        "text",
        { x: v < 0 ? x(0) + 6 : x(v) + 6, y: cy + 4, class: "sb-val", text: fmt.int(v) },
        svg,
      );
    });
  });
}

// ---------- Holdout check ----------
const trustEl = $("pf-trust");
mount(trustEl, (W) => {
  const items: { c: SystemConfig; id: string; gap: number; limit: number }[] = [];
  for (const c of mine)
    for (const [id, v] of Object.entries(c.ds))
      if (v.holdoutGap != null) items.push({ c, id, gap: v.holdoutGap, limit: v.holdoutLimit });
  const rowH = 26;
  const labelW = 170;
  const plotB = Math.max(1, items.length) * rowH;
  const H = plotB + 44;
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: H,
    role: "img",
    "aria-label": "Public versus private score gap",
  });
  trustEl.append(svg);
  if (!items.length) {
    s(
      "text",
      {
        x: W / 2,
        y: rowH / 2 + 4,
        "text-anchor": "middle",
        class: "sb-sub",
        text: "No holdout results for this system.",
      },
      svg,
    );
    return;
  }
  const x = linear(0, 0.16, labelW + 10, W - 74);
  for (const t of [0, 0.04, 0.08, 0.12, 0.16]) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: t.toFixed(2) },
      svg,
    );
  }
  axisTitle(svg, "Public minus private SPS, absolute (tick = review threshold)", {
    x: (x(0) + x(0.16)) / 2,
    y: H - 4,
  });
  items.forEach((it, i) => {
    const cy = i * rowH + rowH / 2;
    const over = it.gap > it.limit;
    s(
      "text",
      {
        x: labelW,
        y: cy + 4,
        "text-anchor": "end",
        class: "sb-lab sb-light",
        text: `${METHODS[it.c.method as ShownMethod].short}, ${dsLabel(it.id)}`,
      },
      svg,
    );
    s(
      "rect",
      {
        x: x(0),
        y: cy - 4,
        width: x(Math.min(0.16, it.gap)) - x(0),
        height: 8,
        rx: 2,
        fill: over ? css("--sb-warn") : css("--sb-ink-2"),
        opacity: over ? 1 : 0.5,
      },
      svg,
    );
    s(
      "line",
      {
        x1: x(it.limit),
        x2: x(it.limit),
        y1: cy - 8,
        y2: cy + 8,
        stroke: css("--sb-ink"),
        "stroke-width": 1.5,
      },
      svg,
    );
    s(
      "text",
      {
        x: W - 2,
        y: cy + 4,
        "text-anchor": "end",
        class: over ? "sb-warn-t" : "sb-ok-t",
        text: `${over ? "⚠" : "✓"} ${it.gap.toFixed(3)}`,
      },
      svg,
    );
  });
});

// ---------- Runs ----------
$("pf-runs").replaceChildren(
  h(
    "thead",
    null,
    h(
      "tr",
      null,
      ["Method", "Dataset", "Questions", "Samples per question", "Runs", ""].map((t) =>
        h("th", { scope: "col" }, t),
      ),
    ),
  ),
  h(
    "tbody",
    null,
    mine.flatMap((c) =>
      Object.entries(c.ds).map(([id, v]) =>
        h(
          "tr",
          null,
          h(
            "td",
            null,
            h(
              "span",
              { class: "sb-inl" },
              methodKey(c.method),
              METHODS[c.method as ShownMethod].short,
            ),
          ),
          h("td", null, dsLabel(id)),
          h("td", { class: "sb-mono" }, String(v.n)),
          h(
            "td",
            { class: "sb-mono" },
            v.samplesPerQuestion == null ? "—" : String(v.samplesPerQuestion),
          ),
          h("td", { class: "sb-mono" }, v.runs == null ? "—" : String(v.runs)),
          h(
            "td",
            null,
            v.configId ? h("a", { href: `${d.base}config/${v.configId}/` }, "Run details") : null,
          ),
        ),
      ),
    ),
  ),
);

function render(): void {
  renderMethod();
  renderStats();
  renderComponents();
}
onChange(render);
render();
initShell();
