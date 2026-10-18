import { topicLabel } from "@/lib/topics";
import { harnessTag, modelNameFromLabel } from "@/lib/vocab";
import { axisTicks, axisTitle, css, fmt, h, linear, mount, s, thinTicks, ticks } from "../dom";
import {
  ALL,
  CORE,
  METHODS,
  type ShownMethod,
  type SystemConfig,
  counterpart,
  data,
  dsLabel,
  dsMark,
  dsMeta,
  emit,
  ensembleLabel,
  ensembles,
  fullCoverage,
  methodLabel,
  methodShort,
  onChange,
  profileQuery,
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
const options: [SystemConfig, string][] = [
  ...mine.map((c): [SystemConfig, string] => [c, methodLabel(c)]),
  ...ensembles()
    .filter((e) => e.baseId !== baseId && e.members.some((m) => m.id === baseId))
    .map((e): [SystemConfig, string] => [e, `In the ensemble ${ensembleLabel(e.base)}`]),
];
/** URL state for an option: the method and harness, or which ensemble it is on a member's page. */
const optionParams = (c: SystemConfig): Record<string, string | null> => ({
  ...profileQuery(c),
  ensemble: c.baseId !== baseId ? c.baseId : null,
});
const fromUrl = new URLSearchParams(location.search);
const matchesUrl = (c: SystemConfig) =>
  Object.entries(optionParams(c)).every(([k, v]) => (fromUrl.get(k) ?? null) === v);
let cur: SystemConfig =
  options.find(([c]) => matchesUrl(c))?.[0] ??
  mine.find((c) => c.method === fromUrl.get("method") && !c.harness) ??
  mine.find((c) => c.method === "althing" && !c.harness) ??
  mine[0];

const median = (a: number[]) => {
  const q = [...a].sort((x, y) => x - y);
  const m = q.length >> 1;
  return q.length % 2 ? q[m] : (q[m - 1] + q[m]) / 2;
};
const others = (id: string, me: SystemConfig | null) =>
  systems().filter((c) => !c.variant && c.ds[id] && c !== me);
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
/** Below this chart width, row labels sit above their bars instead of beside them. */
const NARROW = 480;
/** Topics with fewer questions than this are marked "low n". */
const LOW_N = 10;

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
              writeParams(optionParams(c));
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
  // Same state as the headline tile: the score in the current scope, against
  // the other systems scored in that scope.
  const field = systems()
    .filter((c) => !c.variant)
    .map((c) => scoreIn(c)?.v)
    .filter((x): x is number => x != null);
  const m = field.length ? median(field) : 0;
  const who =
    cur.method === "ensemble"
      ? `The ensemble ${cur.short}`
      : `${cur.base}${cur.harness ? ` ${harnessTag(cur.harness)}` : ""} with ${cur.method === "raw" ? "a raw prompt" : "an Althing persona"}`;
  const parts: string[] = [];
  const where = state.scope === "all" ? "the Index" : dsLabel(state.scope);
  if (v)
    parts.push(
      `${who} scores ${fmt.int(v.v)} on ${where}, ${v.v > m + 5 ? "above" : v.v < m - 5 ? "below" : "close to"} the median system (${fmt.int(m)}).`,
    );
  else if (state.scope === "all") {
    const missing = CORE.filter((id) => !cur.ds[id]).map(dsLabel);
    parts.push(
      `${who} wasn't run on every core dataset${missing.length ? ` (no ${missing.join(" or ")} run)` : ""}, so it isn't ranked on the Index.`,
    );
  } else parts.push(`${who} wasn't run on ${dsLabel(state.scope)}.`);
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
    for (const t of thinTicks([-40, -20, 0, 20, 40, 60], x, fmt.int)) {
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
          text: `${dsLabel(id)}${dsMark(id)}`,
        },
        svg,
      );
      // Questions this system was actually run on (as in the runs table), out
      // of the dataset's full size.
      const ran = (cur.ds[id] ?? cp?.ds[id])?.n;
      const total = dsMeta(id)?.questions;
      s(
        "text",
        {
          x: labelW,
          y: cy + 13,
          "text-anchor": "end",
          class: "sb-sub",
          text:
            ran != null && total != null && ran < total
              ? `${ran} of ${total} questions`
              : `${ran ?? total ?? "?"} questions`,
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
      `Index per topic on ${dsLabel(topicDs)}. Dark tick: median of other systems. Rows marked “low n” have fewer than 10 questions.`;
    const ds = cur.ds[topicDs];
    const topics = Object.keys(ds.topicIdx).sort((a, b) => ds.topicIdx[b] - ds.topicIdx[a]);
    // Narrow screens: topic names go on their own line above each bar.
    const narrow = W < NARROW;
    const rowH = narrow ? 38 : 26;
    const labelW = narrow ? -10 : Math.min(240, W * 0.3);
    const plotB = topics.length * rowH;
    const H = plotB + 44;
    const x = linear(-100, 60, labelW + 10, W - (narrow ? 34 : 70));
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
    for (const t of thinTicks([-100, -50, 0, 50], x, fmt.int)) {
      s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
      s(
        "text",
        { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: fmt.int(t) },
        svg,
      );
    }
    s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
    axisTitle(
      svg,
      narrow
        ? "Index on this topic (0 = random)"
        : "SynthBench Index on this topic (0 = random answers)",
      { x: (x(-100) + x(60)) / 2, y: H - 4 },
    );
    axisTitle(svg, narrow ? "Qs" : "Questions", { x: W - 2, y: plotB + 15, anchor: "end" });
    topics.forEach((t, i) => {
      const cy = narrow ? i * rowH + 26 : i * rowH + rowH / 2;
      const n = ds.topicN[t];
      const val = ds.topicIdx[t];
      const g = s("g", null, svg);
      s(
        "text",
        {
          x: narrow ? 0 : labelW,
          y: narrow ? cy - 10 : cy + 4,
          "text-anchor": narrow ? "start" : "end",
          class: n < LOW_N ? "sb-lab sb-light sb-lown" : "sb-lab sb-light",
          text: n < LOW_N ? `${topicLabel(t)} (low n)` : topicLabel(t),
        },
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

// ---------- Experiments (persona only, backed by this model's own runs) ----------
// The temperature sweep and template runs are Althing persona experiments, so
// they only show while the persona is selected, and only on a dataset this
// system was itself run on.
const SWEEP_DS = "opinionsqa";
const sweep = (d.findings.temperature_sweep ?? [])
  .filter(
    (p) => modelNameFromLabel(p.model) === mine[0]?.base && (p.dataset ?? SWEEP_DS) === SWEEP_DS,
  )
  .sort((a, b) => a.temperature - b.temperature);
const templates = variants.filter(
  (c) => c.variant?.startsWith("temperature 0.85") && c.ds.subpop && !c.harness,
);
const isPersona = () => cur.method === "althing" && !cur.harness && cur.baseId === baseId;
const showTemp = () => isPersona() && sweep.length > 1 && cur.ds[SWEEP_DS] != null;
const showTpl = () => isPersona() && templates.length > 1 && cur.ds.subpop != null;
const runsText = (runs: number[], what: string) => {
  const lo = Math.min(...runs);
  const hi = Math.max(...runs);
  return lo === hi
    ? `${lo === 1 ? "One run" : `${lo} runs`} per ${what}`
    : `${lo} to ${hi} runs per ${what}`;
};
const hasBand = sweep.some((p) => (p.n_runs ?? 1) > 1 && (p.std ?? 0) > 0);
function renderExperiments(): void {
  const t = showTemp();
  const p = showTpl();
  $("pf-exp").style.display = t || p ? "" : "none";
  $("pf-temp-panel").style.display = t ? "" : "none";
  $("pf-tpl-panel").style.display = p ? "" : "none";
  // A lone panel takes the full row instead of leaving an empty column.
  $("pf-temp-panel").style.gridColumn = t && !p ? "1 / -1" : "";
  $("pf-tpl-panel").style.gridColumn = p && !t ? "1 / -1" : "";
  if (t)
    $("pf-temp-q").textContent = [
      `${dsLabel(SWEEP_DS)}, Althing persona.`,
      `${runsText(
        sweep.map((q) => q.n_runs ?? 1),
        "temperature",
      )}${hasBand ? "; band: ±1 standard deviation across repeat runs." : ", so there is no error band. Differences of a few points may be noise."}`,
      `These sweep runs are separate from the published run, which scores ${fmt.int(cur.ds[SWEEP_DS].idx)} at the default temperature.`,
    ].join(" ");
  if (p) {
    const def = templates.find((c) => !/template/.test(c.variant ?? ""));
    $("pf-tpl-q").textContent = [
      `${dsLabel("subpop")}, Althing persona, temperature 0.85.`,
      `${runsText(
        templates.map((c) => c.ds.subpop.runs ?? 1),
        "template",
      )}.`,
      def
        ? `At temperature 0.85 the default template scores ${fmt.int(def.ds.subpop.idx)}; the published run at the default temperature scores ${fmt.int(cur.ds.subpop.idx)}.`
        : "",
    ]
      .filter(Boolean)
      .join(" ");
  }
}
// Registered before the charts so they draw into visible panels.
onChange(renderExperiments);
renderExperiments();
{
  const oq = dsMeta(SWEEP_DS);
  const toIdx = (sps: number) =>
    oq ? (100 * (sps - oq.random)) / ((oq.ceiling ?? 1) - oq.random) : 0;
  const tempEl = $("pf-temp");
  mount(
    tempEl,
    (W) => {
      if (!showTemp()) return;
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
      const pts = sweep.map((q) => ({
        x: q.temperature,
        y: toIdx(q.sps),
        sd: hasBand ? toIdx(q.sps + (q.std ?? 0)) - toIdx(q.sps) : 0,
      }));
      const xs = pts.map((q) => q.x);
      const lo = Math.floor((Math.min(...pts.map((q) => q.y - q.sd)) - 3) / 5) * 5;
      const hi = Math.ceil((Math.max(...pts.map((q) => q.y + q.sd)) + 3) / 5) * 5;
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
      const shown = thinTicks(
        pts.map((q) => q.x),
        X,
        String,
      );
      for (const q of pts.filter((p) => shown.includes(p.x)))
        s(
          "text",
          {
            class: "sb-t",
            x: X(q.x),
            y: H - m.b + 16,
            "text-anchor": "middle",
            text: String(q.x),
          },
          svg,
        );
      axisTitle(svg, "Sampling temperature", { x: (m.l + W - m.r) / 2, y: H - 6 });
      axisTitle(svg, `Index (${dsLabel(SWEEP_DS)})`, {
        x: 14,
        y: (m.t + H - m.b) / 2,
        vertical: true,
      });
      if (hasBand) {
        const band = `${pts.map((q, i) => `${i ? "L" : "M"}${X(q.x)},${Y(q.y + q.sd)}`).join("")}${[
          ...pts,
        ]
          .reverse()
          .map((q) => `L${X(q.x)},${Y(q.y - q.sd)}`)
          .join("")}Z`;
        s("path", { d: band, fill: methodColor("althing"), opacity: 0.14 }, svg);
      }
      s(
        "path",
        {
          d: pts.map((q, i) => `${i ? "L" : "M"}${X(q.x)},${Y(q.y)}`).join(""),
          fill: "none",
          stroke: methodColor("althing"),
          "stroke-width": 2,
        },
        svg,
      );
      for (const q of pts) marker(svg, "althing", X(q.x), Y(q.y), 3.5);
    },
    onChange,
  );
  const tplEl = $("pf-tpl");
  mount(
    tplEl,
    (W) => {
      if (!showTpl()) return;
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
      const lo = Math.min(-20, Math.floor(Math.min(...rows.map((c) => c.ds.subpop.idx)) / 20) * 20);
      const hi = Math.max(20, Math.ceil(Math.max(...rows.map((c) => c.ds.subpop.idx)) / 20) * 20);
      const x = linear(lo, hi, labelW + 10, W - 40);
      for (const t of axisTicks(lo, hi, x, fmt.int, 5)) {
        s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
        s(
          "text",
          { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: fmt.int(t) },
          svg,
        );
      }
      s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
      axisTitle(svg, "Index on SubPOP (0 = random answers)", {
        x: (x(lo) + x(hi)) / 2,
        y: H - 4,
      });
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
    },
    onChange,
  );
}

// ---------- Holdout check ----------
const trustEl = $("pf-trust");
mount(trustEl, (W) => {
  const items: { c: SystemConfig; id: string; gap: number; limit: number }[] = [];
  for (const c of mine)
    for (const [id, v] of Object.entries(c.ds))
      if (v.holdoutGap != null) items.push({ c, id, gap: v.holdoutGap, limit: v.holdoutLimit });
  const narrow = W < NARROW;
  const rowH = narrow ? 38 : 26;
  const labelW = narrow ? -10 : 170;
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
  for (const t of thinTicks(narrow ? [0, 0.08, 0.16] : [0, 0.04, 0.08, 0.12, 0.16], x, (v) =>
    v.toFixed(2),
  )) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: t.toFixed(2) },
      svg,
    );
  }
  axisTitle(
    svg,
    narrow
      ? "Public − private SPS (tick = threshold)"
      : "Public minus private SPS, absolute (tick = review threshold)",
    { x: (x(0) + x(0.16)) / 2, y: H - 4 },
  );
  items.forEach((it, i) => {
    const cy = narrow ? i * rowH + 26 : i * rowH + rowH / 2;
    const over = it.gap > it.limit;
    s(
      "text",
      {
        x: narrow ? 0 : labelW,
        y: narrow ? cy - 10 : cy + 4,
        "text-anchor": narrow ? "start" : "end",
        class: "sb-lab sb-light",
        text: `${methodShort(it.c)}, ${dsLabel(it.id)}`,
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
      ["Method", "Dataset", "Questions run", "Samples per question", "Runs", "Configuration"].map(
        (t) => h("th", { scope: "col" }, t),
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
          h("td", null, h("span", { class: "sb-inl" }, methodKey(c.method), methodShort(c))),
          h("td", null, dsLabel(id)),
          h(
            "td",
            { class: "sb-mono" },
            (dsMeta(id)?.questions ?? v.n) > v.n
              ? `${v.n} of ${dsMeta(id)?.questions}`
              : String(v.n),
          ),
          h(
            "td",
            { class: "sb-mono" },
            v.samplesPerQuestion == null ? "—" : String(v.samplesPerQuestion),
          ),
          h("td", { class: "sb-mono" }, v.runs == null ? "—" : String(v.runs)),
          h(
            "td",
            null,
            v.configId
              ? h(
                  "a",
                  {
                    href: `${d.base}config/${v.configId}/`,
                    title: `${dsLabel(id)}, ${c.variant ?? "default temperature, default template"}: replicates, metrics and per-topic scores`,
                    style: { whiteSpace: "nowrap" },
                  },
                  `${c.variant ?? "t default · default template"} →`,
                )
              : null,
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
