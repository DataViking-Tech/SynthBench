import { css, fmt, h, heat, linear, s } from "../dom";
import {
  ALL,
  METHODS,
  type Ranked,
  type ShownMethod,
  type SystemConfig,
  type Val,
  component,
  data,
  dsLabel,
  emit,
  onChange,
  pruneCompare,
  scoreIn,
  state,
  systems,
  tiers,
} from "../model";
import {
  METHOD_IDS,
  filterStatus,
  glyph,
  initShell,
  inspect,
  marker,
  methodChips,
  methodColor,
  methodKey,
  readSet,
  scopeControl,
  setParam,
  toggleCompare,
  writeParams,
} from "../ui";

pruneCompare();
const d = data();
const q = new URLSearchParams(location.search);
type Cols = "scores" | "components" | "cost" | "checks";
const COLS: [Cols, string][] = [
  ["scores", "Scores"],
  ["components", "Components"],
  ["cost", "Cost"],
  ["checks", "Checks"],
];
const st = {
  methods: readSet("methods", METHOD_IDS, METHOD_IDS),
  experiments: q.get("experiments") === "1",
  partial: q.get("partial") === "1",
  cols: (COLS.some(([k]) => k === q.get("cols")) ? q.get("cols") : "scores") as Cols,
};
const isDefault = () =>
  state.scope === "all" && st.methods.size === METHOD_IDS.length && !st.experiments && !st.partial;
const changed = () => {
  writeParams({
    methods: setParam(st.methods, METHOD_IDS),
    experiments: st.experiments ? "1" : null,
    partial: st.partial ? "1" : null,
    cols: st.cols === "scores" ? null : st.cols,
  });
  emit();
};
const reset = () => {
  state.scope = "all";
  for (const m of METHOD_IDS) st.methods.add(m);
  st.experiments = false;
  st.partial = false;
  changed();
};

// ---------- Filters ----------
const toggle = (label: string, title: string, key: "experiments" | "partial") => {
  const input = h("input", { type: "checkbox" });
  input.addEventListener("change", () => {
    st[key] = input.checked;
    changed();
  });
  const el = h("label", { class: "sb-toggle", title }, input, label);
  return Object.assign(el, {
    sync: () => {
      input.checked = st[key];
    },
  });
};
const expT = toggle(
  "Experiments",
  "Show runs with non-default settings (temperature, prompt template). They aren't ranked.",
  "experiments",
);
const partT = toggle(
  "Partial coverage",
  "Show systems not run on all three core datasets. They aren't ranked.",
  "partial",
);
const colsSeg = h("div", { class: "sb-seg", role: "radiogroup", "aria-label": "Columns" });
const renderCols = () =>
  colsSeg.replaceChildren(
    ...COLS.map(([k, label]) =>
      h(
        "button",
        {
          type: "button",
          role: "radio",
          "aria-checked": st.cols === k ? "true" : "false",
          class: st.cols === k ? "on" : null,
          onclick: () => {
            st.cols = k;
            changed();
          },
        },
        label,
      ),
    ),
  );
const chips = methodChips(st.methods, changed);
let shownCount = 0;
const status = filterStatus(() => [shownCount, systems().length], isDefault, reset);
document
  .getElementById("lb-filters")
  ?.append(
    scopeControl(),
    chips,
    h("div", { class: "sb-filter" }, h("span", { class: "sb-lbl" }, "Include"), expT, partT),
    h("div", { class: "sb-filter" }, h("span", { class: "sb-lbl" }, "Columns"), colsSeg),
    status,
  );

// ---------- Small inline charts ----------
const AX: [number, number] = [-40, 60];
const BW = 220;
function intervalCell(c: SystemConfig, v: Val): SVGSVGElement {
  const sv = s("svg", { class: "sb-c", width: BW, height: 22, "aria-hidden": "true" });
  const x = linear(AX[0], AX[1], 6, BW - 6);
  s(
    "rect",
    { x: x(AX[0]), y: 4, width: x(0) - x(AX[0]), height: 14, fill: "var(--sb-zone-neg)" },
    sv,
  );
  for (const t of [-20, 20, 40])
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 2, y2: 20 }, sv);
  s("line", { x1: x(0), x2: x(0), y1: 0, y2: 22, stroke: css("--sb-ink-2") }, sv);
  const cl = (n: number) => Math.max(AX[0], Math.min(AX[1], n));
  if (v.lo != null && v.hi != null)
    s(
      "rect",
      {
        x: x(cl(v.lo)),
        y: 9,
        width: Math.max(2, x(cl(v.hi)) - x(cl(v.lo))),
        height: 4,
        rx: 2,
        fill: methodColor(c.method),
        opacity: 0.35,
      },
      sv,
    );
  marker(sv, c.method, x(cl(v.v)), 11, 4.5);
  if (v.v < AX[0])
    s("text", { x: x(AX[0]) + 10, y: 15, class: "sb-neg-t", text: "◀ off scale" }, sv);
  return sv;
}
function axisHead(): HTMLElement {
  const sv = s("svg", { class: "sb-c", width: BW, height: 14, "aria-hidden": "true" });
  const x = linear(AX[0], AX[1], 6, BW - 6);
  for (const t of [-40, -20, 0, 20, 40, 60])
    s(
      "text",
      {
        class: "sb-t",
        x: x(t),
        y: 11,
        "text-anchor": t === -40 ? "start" : t === 60 ? "end" : "middle",
        text: fmt.int(t),
      },
      sv,
    );
  return h("div", { class: "sb-axhead" }, h("span", null, "Index, 95% interval"), sv);
}
function bullet(v: number | null, r: number | null, color: string): SVGSVGElement {
  const W = 84;
  const sv = s("svg", {
    class: "sb-c",
    width: W,
    height: 14,
    "aria-hidden": "true",
    style: "display:inline-block;vertical-align:middle",
  });
  const x = linear(0.4, 1, 0, W);
  s("rect", { x: 0, y: 4, width: W, height: 6, rx: 3, fill: css("--sb-grid") }, sv);
  if (v != null)
    s("rect", { x: 0, y: 4, width: x(Math.max(0.4, v)), height: 6, rx: 3, fill: color }, sv);
  if (r != null)
    s(
      "line",
      { x1: x(r), x2: x(r), y1: 0, y2: 14, stroke: css("--sb-neg-ink"), "stroke-width": 2 },
      sv,
    );
  return sv;
}
function gapBar(g: number | null): SVGSVGElement {
  const W = 110;
  const sv = s("svg", {
    class: "sb-c",
    width: W,
    height: 14,
    "aria-hidden": "true",
    style: "display:inline-block;vertical-align:middle",
  });
  const x = linear(0, 0.12, 0, W);
  s("rect", { x: 0, y: 4, width: W, height: 6, rx: 3, fill: css("--sb-grid") }, sv);
  if (g != null)
    s(
      "rect",
      {
        x: 0,
        y: 4,
        width: x(Math.min(0.12, g)),
        height: 6,
        rx: 3,
        fill: g > 0.05 ? css("--sb-warn") : css("--sb-ink-2"),
      },
      sv,
    );
  s(
    "line",
    { x1: x(0.05), x2: x(0.05), y1: 0, y2: 14, stroke: css("--sb-ink"), "stroke-width": 1.5 },
    sv,
  );
  return sv;
}

// ---------- Table ----------
type Row = {
  c: SystemConfig;
  v: Val;
  tier: number | null;
  tied: number;
  kind: "ranked" | "experiment" | "partial";
};
const th = (label: string | Node, cls?: string | null, title?: string) =>
  h("th", { class: cls ?? null, scope: "col", title: title ?? null }, label);
const scaled = (label: string, scale: string) =>
  h("span", null, label, h("small", { class: "sb-th-scale" }, scale));
const maxGap = (c: SystemConfig) => {
  const gaps = Object.values(c.ds)
    .map((x) => x.holdoutGap)
    .filter((g): g is number => g != null);
  return gaps.length ? Math.max(...gaps) : null;
};
const spq = (c: SystemConfig) =>
  [
    ...new Set(
      Object.values(c.ds)
        .map((x) => x.samplesPerQuestion)
        .filter(Boolean),
    ),
  ].join(" / ") || "—";

function currentRows(): { rows: Row[]; partial: Row[] } {
  const pool = systems().filter((c) => st.methods.has(c.method));
  const ranked: Row[] = tiers(pool.filter((c) => !c.variant)).map((r: Ranked) => ({
    ...r,
    kind: "ranked",
  }));
  const extra: Row[] = [];
  if (st.experiments)
    for (const c of pool.filter((x) => x.variant)) {
      const v = scoreIn(c);
      if (v) extra.push({ c, v, tier: null, tied: 1, kind: "experiment" });
    }
  const partial: Row[] =
    st.partial && state.scope === "all"
      ? pool
          .filter((c) => !c.variant && c.coverage > 0 && c.coverage < 3 && c.index != null)
          .map((c) => ({
            c,
            v: { v: c.index as number, lo: c.indexLo, hi: c.indexHi },
            tier: null,
            tied: 1,
            kind: "partial" as const,
          }))
      : [];
  return { rows: [...ranked, ...extra].sort((a, b) => b.v.v - a.v.v), partial };
}

function header(): HTMLElement[] {
  const head = [th("Tier"), th(h("span", { class: "sr-only" }, "Compare")), th("System")];
  const idxLabel = state.scope === "all" ? "Index" : dsLabel(state.scope);
  if (st.cols === "scores")
    head.push(
      th(axisHead()),
      th(idxLabel, "r", "SynthBench Index with its 95% interval"),
      ...ALL.map((id) =>
        th(`${dsLabel(id)}${id === "gss" ? " †" : ""}`, "c", `Index on ${dsLabel(id)}`),
      ),
      th("Holdout", "c", "Public and private questions agree within 0.05"),
    );
  else if (st.cols === "components")
    head.push(
      th(idxLabel, "r"),
      th("SPS", "r", "Survey Parity Score, 0 to 1"),
      th(
        scaled("Shares match", "bar 0.4 to 1, red tick = random"),
        null,
        "1 − Jensen-Shannon divergence. Red tick = random answers.",
      ),
      th(
        scaled("Order match", "bar 0.4 to 1, red tick = random"),
        null,
        "(1 + Kendall τ) ÷ 2. Red tick = random answers.",
      ),
      th(
        scaled("Refusal match", "bar 0.4 to 1, red tick = random"),
        null,
        "How closely refusal and don't-know rates match people. Red tick = random answers.",
      ),
    );
  else if (st.cols === "cost")
    head.push(
      th(idxLabel, "r"),
      th("USD per 100 questions", "r"),
      th("Index points per USD", "r"),
      th("Median latency", "r"),
      th("Samples per question", "r"),
      th("Runs", "r"),
    );
  else
    head.push(
      th(idxLabel, "r"),
      th(
        scaled("Public vs. private SPS gap", "bar 0 to 0.12, line = 0.05 limit"),
        null,
        "Largest gap across datasets. Line = 0.05 review threshold.",
      ),
      th("Status"),
      th("Runs", "r"),
      th("Questions", "r"),
    );
  return head;
}

function row(r: Row, rows: Row[], i: number): HTMLElement {
  const { c, v } = r;
  const sel = state.compare.includes(c.key);
  const first = r.tier != null && rows.findIndex((x) => x.tier === r.tier) === i;
  const last = r.tier != null && rows.map((x) => x.tier).lastIndexOf(r.tier) === i;
  const tr = h("tr", {
    class: ["sys", sel ? "sel" : null, first ? "tier-start" : null, last ? "tier-end" : null]
      .filter(Boolean)
      .join(" "),
    tabindex: "0",
    "aria-label": `${c.base}, ${METHODS[c.method as ShownMethod].label}: open details`,
    onclick: () => inspect(c.key),
    onkeydown: (e: KeyboardEvent) => {
      if (e.key === "Enter") inspect(c.key);
    },
  });
  const tierCell = h(
    "td",
    { class: "tier" },
    r.tier != null
      ? [
          h("span", { class: "tb" }),
          first
            ? h(
                "div",
                { class: "tl" },
                `Tier ${r.tier}`,
                h("small", null, r.tied > 1 ? `${r.tied} tied` : "alone"),
              )
            : null,
        ]
      : h("div", { class: "tl sb-muted" }, r.kind === "experiment" ? "exp." : "—"),
  );
  const cb = h(
    "td",
    { class: "cb" },
    h("button", {
      type: "button",
      class: `sb-cbox${sel ? " on" : ""}`,
      role: "checkbox",
      "aria-checked": sel ? "true" : "false",
      "aria-label": `Compare ${c.base}`,
      title: "Add to compare",
      onclick: (e: Event) => {
        e.stopPropagation();
        toggleCompare(c.key);
      },
    }),
  );
  const name = h(
    "td",
    null,
    h(
      "div",
      { class: "sb-sysname" },
      h("span", { class: "n" }, glyph(c.lab), c.base),
      h(
        "span",
        { class: "m" },
        methodKey(c.method),
        METHODS[c.method as ShownMethod].label,
        c.variant ? h("span", { class: "sb-tag" }, c.variant) : null,
        c.harness
          ? h(
              "span",
              { class: "sb-tag", title: `Run through the ${c.harness} CLI` },
              `via ${c.harness}`,
            )
          : null,
        c.flagged
          ? h("span", { class: "sb-warn", title: "Public vs. private gap above 0.05" }, "⚠")
          : null,
      ),
    ),
  );
  const cells: HTMLElement[] = [tierCell, cb, name];
  const random = d.references.random;
  if (st.cols === "scores") {
    cells.push(
      h("td", null, intervalCell(c, v)),
      h(
        "td",
        { class: "v" },
        fmt.int(v.v),
        h("small", null, v.lo != null ? `${fmt.int(v.lo)} to ${fmt.int(v.hi)}` : ""),
      ),
    );
    for (const id of ALL) {
      const x = c.ds[id];
      const { bg, fg } = heat(x?.idx);
      cells.push(
        h(
          "td",
          { class: `hc${state.scope === id ? " cur" : ""}` },
          h("span", { style: { background: bg, color: fg } }, x ? fmt.int(x.idx) : "·"),
        ),
      );
    }
    const g = maxGap(c);
    cells.push(
      h(
        "td",
        { class: "c" },
        g == null
          ? h("span", { class: "sb-muted" }, "—")
          : g > 0.05
            ? h("span", { class: "sb-warn" }, "⚠")
            : h("span", { class: "sb-ok" }, "✓"),
      ),
    );
  } else if (st.cols === "components") {
    cells.push(
      h("td", { class: "v" }, fmt.int(v.v)),
      h("td", { class: "v plain" }, fmt.three(component(c, "sps"))),
    );
    for (const k of ["pDist", "pRank", "pRefuse"] as const) {
      const val = component(c, k);
      cells.push(
        h(
          "td",
          { class: "nowrap" },
          bullet(val, component(random, k), methodColor(c.method)),
          h("span", { class: "sb-mono sb-cellnum" }, fmt.three(val)),
        ),
      );
    }
  } else if (st.cols === "cost") {
    cells.push(
      h("td", { class: "v" }, fmt.int(v.v)),
      h(
        "td",
        { class: "v plain" },
        c.cost100 == null ? h("span", { class: "sb-muted" }, "not recorded") : fmt.usd(c.cost100),
      ),
      h("td", { class: "v plain" }, c.cost100 ? fmt.int(v.v / c.cost100) : "—"),
      h("td", { class: "v plain" }, c.latencyP50 == null ? "—" : `${c.latencyP50.toFixed(1)} s`),
      h("td", { class: "v plain" }, spq(c)),
      h("td", { class: "v plain" }, String(c.runs)),
    );
  } else {
    const g = maxGap(c);
    cells.push(
      h("td", { class: "v" }, fmt.int(v.v)),
      h(
        "td",
        { class: "nowrap" },
        gapBar(g),
        h("span", { class: "sb-mono sb-cellnum" }, g == null ? "—" : g.toFixed(3)),
      ),
      h(
        "td",
        null,
        g == null
          ? h("span", { class: "sb-muted" }, "no holdout")
          : g > 0.05
            ? h("span", { class: "sb-warn" }, "⚠ under review")
            : h("span", { class: "sb-ok" }, "✓ within 0.05"),
      ),
      h("td", { class: "v plain" }, String(c.runs)),
      h(
        "td",
        { class: "v plain" },
        Object.values(c.ds)
          .reduce((a, x) => a + x.n, 0)
          .toLocaleString("en-US"),
      ),
    );
  }
  tr.append(...cells);
  return tr;
}

function render(): void {
  expT.sync();
  partT.sync();
  renderCols();
  chips.rerender();
  const { rows, partial } = currentRows();
  shownCount = rows.length + partial.length;
  status.rerender();
  const head = header();
  const ncol = head.length;
  const body: HTMLElement[] = [];
  const majV = d.references.majority ? scoreIn(d.references.majority)?.v : null;
  const refs = [
    { v: 0, label: "0", text: "Random answers: a uniformly random option on every question" },
    ...(majV != null
      ? [{ v: majV, label: fmt.int(majV), text: "Majority answer: always the most popular option" }]
      : []),
  ];
  const done = new Set<(typeof refs)[number]>();
  const refRow = (r: (typeof refs)[number]) => {
    done.add(r);
    body.push(
      h(
        "tr",
        { class: "refrow" },
        h("td", { colspan: String(ncol) }, h("b", null, r.label), r.text),
      ),
    );
  };
  if (!rows.length && !partial.length)
    body.push(
      h(
        "tr",
        null,
        h(
          "td",
          { colspan: String(ncol), class: "sb-empty" },
          "No systems match these filters. ",
          h("button", { type: "button", class: "sb-linkbtn", onclick: reset }, "Reset filters"),
        ),
      ),
    );
  rows.forEach((r, i) => {
    for (const rf of refs) if (!done.has(rf) && r.v.v < rf.v) refRow(rf);
    body.push(row(r, rows, i));
  });
  if (rows.length) for (const rf of refs) if (!done.has(rf)) refRow(rf);
  if (partial.length) {
    body.push(
      h(
        "tr",
        { class: "refrow" },
        h(
          "td",
          { colspan: String(ncol) },
          h("b", null, "—"),
          "Partial coverage, not ranked. Index averages only the datasets each system was run on.",
        ),
      ),
    );
    partial.forEach((r, i) => body.push(row(r, partial, i)));
  }
  document
    .getElementById("leaderboard")
    ?.replaceChildren(h("thead", null, h("tr", null, head)), h("tbody", null, body));
}
onChange(render);
render();

// ---------- CSV of the current view ----------
document.getElementById("lb-csv")?.addEventListener("click", () => {
  const { rows, partial } = currentRows();
  const esc = (x: unknown) => {
    const t = x == null ? "" : String(x);
    return /[",\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t;
  };
  const lines = [
    [
      "system",
      "method",
      "variant",
      "harness",
      "tier",
      "index",
      "index_lo",
      "index_hi",
      ...ALL.map((id) => `${id}_index`),
      "cost_per_100_usd",
      "flagged_datasets",
    ].join(","),
    ...[...rows, ...partial].map((r) =>
      [
        r.c.base,
        r.c.method,
        r.c.variant,
        r.c.harness,
        r.tier,
        r.v.v,
        r.v.lo,
        r.v.hi,
        ...ALL.map((id) => r.c.ds[id]?.idx),
        r.c.cost100,
        r.c.flagged,
      ]
        .map(esc)
        .join(","),
    ),
  ];
  const url = URL.createObjectURL(new Blob([`${lines.join("\n")}\n`], { type: "text/csv" }));
  const a = h("a", { href: url, download: `synthbench-index-${state.scope}.csv` });
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

initShell();
