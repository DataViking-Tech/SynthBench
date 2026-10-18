import { signedRange } from "@/lib/format";
import { ensembleNames, modelNameFromLabel } from "@/lib/vocab";
import {
  axisTicks,
  axisTitle,
  css,
  fmt,
  h,
  linear,
  mount,
  rowLabel,
  rowLayout,
  s,
  textWidth,
  thinTicks,
  ticks,
} from "../dom";
import {
  CORE,
  type Method,
  data,
  dsLabel,
  dsMeta,
  ensembleLabel,
  pruneCompare,
  systems,
} from "../model";
import { hoverInfo, initShell, marker, methodColor } from "../ui";

pruneCompare();
const d = data();
const F = d.findings;
const idxOf = (id: string, sps: number) => {
  const m = dsMeta(id);
  return m ? (100 * (sps - m.random)) / ((m.ceiling ?? 1) - m.random) : 0;
};

type Mark = (g: SVGElement, x: number, y: number) => void;
const ring: Mark = (g, x, y) => {
  s(
    "circle",
    { cx: x, cy: y, r: 5, fill: css("--sb-panel"), stroke: css("--sb-ink"), "stroke-width": 1.8 },
    g,
  );
};
const solid: Mark = (g, x, y) => {
  s("circle", { cx: x, cy: y, r: 5.5, fill: css("--sb-ink") }, g);
};
const method =
  (m: Method): Mark =>
  (g, x, y) => {
    marker(g, m, x, y, 5);
  };
const none: Mark = () => {};

interface DumbRow {
  name: string;
  a: number;
  b: number;
  label: string;
  markA?: Mark;
  /** Uncertainty around a / b (95% interval or ±1 SD), drawn as a whisker. */
  errA?: [number, number];
  errB?: [number, number];
  tip?: [string, string][];
}
/**
 * One row per item: a line from value a to value b, with a value label on the
 * right. Narrow charts put each row's label on its own line above it.
 */
function dumbbell(
  el: HTMLElement,
  rows: DumbRow[],
  o: {
    domain: [number, number];
    axis: string;
    tick?: (v: number) => string;
    /** Explicit tick positions, instead of the automatic ones. */
    tickValues?: number[];
    labelW?: number;
    zero?: number;
    a: Mark;
    b: Mark;
  },
): void {
  mount(el, (W) => {
    // Gutter: at least `labelW`, wider for a longer label, never over 46%.
    const longest = Math.max(0, ...rows.map((r) => textWidth(r.name, 12.5, 400) + 4));
    const L = rowLayout(W, Math.min(Math.max(o.labelW ?? 130, longest), W * 0.46), 34);
    const { rowH } = L;
    const plotB = rows.length * rowH;
    const H = plotB + 44;
    const tick = o.tick ?? fmt.int;
    const x = linear(o.domain[0], o.domain[1], L.narrow ? 8 : L.labelW + 12, W - 82);
    const clampX = (v: number) => x(Math.max(o.domain[0], Math.min(o.domain[1], v)));
    const svg = s("svg", { class: "sb-c", width: W, height: H, role: "img", "aria-label": o.axis });
    el.append(svg);
    if (o.zero != null && o.zero > o.domain[0])
      s(
        "rect",
        {
          x: x(o.domain[0]),
          y: 0,
          width: x(o.zero) - x(o.domain[0]),
          height: plotB,
          fill: "var(--sb-zone-neg)",
        },
        svg,
      );
    const tv = o.tickValues
      ? thinTicks(o.tickValues, x, tick)
      : axisTicks(o.domain[0], o.domain[1], x, tick, 5);
    for (const t of tv) {
      s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
      s(
        "text",
        { class: "sb-t", x: x(t), y: plotB + 15, "text-anchor": "middle", text: tick(t) },
        svg,
      );
    }
    if (o.zero != null)
      s("line", { x1: x(o.zero), x2: x(o.zero), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
    axisTitle(svg, o.axis, { x: (x(o.domain[0]) + x(o.domain[1])) / 2, y: H - 4 });
    const whisker = (err: [number, number] | undefined, cy: number) => {
      if (!err) return;
      const [x1, x2] = [clampX(err[0]), clampX(err[1])];
      s("line", { x1, x2, y1: cy, y2: cy, stroke: css("--sb-ink-2"), "stroke-width": 1.5 }, svg);
      for (const xe of [x1, x2])
        s(
          "line",
          {
            x1: xe,
            x2: xe,
            y1: cy - 4,
            y2: cy + 4,
            stroke: css("--sb-ink-2"),
            "stroke-width": 1.5,
          },
          svg,
        );
    };
    rows.forEach((r, i) => {
      const y0 = i * rowH;
      const cy = y0 + L.markY;
      rowLabel(svg, L, W, y0, r.name);
      s(
        "line",
        { x1: x(r.a), x2: x(r.b), y1: cy, y2: cy, stroke: css("--sb-line-2"), "stroke-width": 2 },
        svg,
      );
      whisker(r.errA, cy);
      whisker(r.errB, cy);
      (r.markA ?? o.a)(svg, x(r.a), cy);
      o.b(svg, x(r.b), cy);
      s(
        "text",
        { x: W - 2, y: cy + 4, "text-anchor": "end", class: "sb-val sb-halo", text: r.label },
        svg,
      );
      if (r.tip)
        hoverInfo(
          s("rect", { class: "sb-hit", x: 0, y: y0, width: W, height: rowH }, svg),
          r.name,
          r.tip,
        );
    });
  });
}
const legend = (...items: (string | Node | null)[]) =>
  h("div", { class: "sb-note sb-legend" }, ...items);
const swatch = (draw: Mark) => {
  const sv = s("svg", {
    width: 14,
    height: 14,
    "aria-hidden": "true",
    style: "vertical-align:-2px",
  });
  draw(sv, 7, 7);
  return sv;
};
/** One legend entry: a marker and its label, kept together when the legend wraps. */
const key = (draw: Mark, label: string) => h("span", null, swatch(draw), label);

interface Finding {
  id: string;
  short: string;
  claim: string;
  confidence: [number, string];
  number: string;
  numberLabel: string;
  meaning: string;
  evidence: string;
  viz: (el: HTMLElement) => void;
}
const items: Finding[] = [];

/**
 * Evidence rating from the runs behind each plotted point: one run per point
 * is early evidence whatever the effect size; repeat runs earn `otherwise`.
 */
const rate = (minRuns: number, otherwise: [number, string] = [2, "Moderate"]): [number, string] =>
  minRuns <= 1 ? [1, "Early"] : otherwise;
const runsText = (runs: number[], what: string): string => {
  const lo = Math.min(...runs);
  const hi = Math.max(...runs);
  if (lo !== hi) return `${lo} to ${hi} runs per ${what}`;
  return lo === 1 ? `one run per ${what}` : `${lo} runs per ${what}`;
};
const pctText = (v: number) => `${v < 0.1 ? (v * 100).toFixed(1) : Math.round(v * 100)}%`;

// 1. Raw LLMs vs. random answers
const raws = systems().filter((c) => c.method === "raw" && !c.variant);
const goqa = raws.filter((c) => c.ds.globalopinionqa);
const goqaBelow = goqa.filter((c) => c.ds.globalopinionqa.idx < 0).length;
const goqaSure = goqa.filter((c) => (c.ds.globalopinionqa.hi ?? 0) < 0).length;
items.push({
  id: "random",
  short: "Raw LLMs vs. random",
  claim:
    "A directly prompted LLM scores close to random answers, and below random on cross-national questions",
  confidence: [3, "Strong"],
  number: `${goqaBelow} of ${goqa.length}`,
  numberLabel: `raw LLMs score below random on GlobalOpinionQA. For ${goqaSure} of them the whole 95% interval is below 0.`,
  meaning:
    "A plain prompt is not a substitute for a survey panel. Check results against real data before using them for a new population.",
  evidence:
    "Random answers spread probability evenly across the options, which matches questions where people are split. LLMs do worse than random at matching answer shares and better at matching answer order (see Analysis, Shares vs. order). Each system has a bootstrap 95% interval; tap or hover a row for how many raw LLMs sit clearly above or below 0.",
  viz(el) {
    const rows = CORE.map((id): DumbRow => {
      const sys = raws.filter((c) => c.ds[id]).sort((p, q) => p.ds[id].idx - q.ds[id].idx);
      const v = sys.map((c) => c.ds[id].idx);
      const lo = sys[0].ds[id];
      const hi = sys[sys.length - 1].ds[id];
      return {
        name: dsLabel(id),
        a: v[0],
        b: v[v.length - 1],
        label: `median ${fmt.int(v[v.length >> 1])}`,
        tip: [
          [
            "Lowest raw LLM",
            `${fmt.one(lo.idx)} (95% interval ${fmt.int(lo.lo)} to ${fmt.int(lo.hi)})`,
          ],
          [
            "Highest raw LLM",
            `${fmt.one(hi.idx)} (95% interval ${fmt.int(hi.lo)} to ${fmt.int(hi.hi)})`,
          ],
          [
            "Interval entirely below 0",
            `${sys.filter((c) => (c.ds[id].hi ?? 0) < 0).length} of ${sys.length}`,
          ],
          [
            "Interval entirely above 0",
            `${sys.filter((c) => (c.ds[id].lo ?? 0) > 0).length} of ${sys.length}`,
          ],
        ],
      };
    });
    const lo = Math.min(-30, Math.floor(Math.min(...rows.map((r) => r.a)) / 10) * 10);
    const hi = Math.max(40, Math.ceil(Math.max(...rows.map((r) => r.b)) / 10) * 10);
    dumbbell(el, rows, {
      domain: [lo, hi],
      axis: "SynthBench Index (0 = random answers)",
      zero: 0,
      a: method("raw"),
      b: method("raw"),
    });
    el.after(
      legend("Each row runs from the lowest to the highest raw LLM. Shaded: below random answers."),
    );
  },
});

// 2. Ensembles
const ec = (F.ensemble_comparison ?? [])
  .filter((e) => e.best_member_sps != null)
  .map((e) => ({
    ...e,
    a: idxOf(e.dataset, e.best_member_sps as number),
    b: idxOf(e.dataset, e.ensemble_sps),
    top: idxOf(e.dataset, e.best_single_sps),
    label: ensembleLabel(e.ensemble_model ?? "Ensemble"),
  }));
if (ec.length) {
  const corr = (F.ensemble_error_correlation ?? []).map((c) => c.mean_pearson_r);
  const gains = ec.map((e) => e.b - e.a);
  const vsTop = ec.map((e) => e.b - e.top);
  const winsMember = gains.filter((g) => g > 0).length;
  const winsTop = vsTop.filter((g) => g > 0).length;
  // One row per ensemble: its average Index against its best member's,
  // over the datasets it was scored on.
  const byEns = new Map<string, typeof ec>();
  for (const e of ec) byEns.set(e.label, [...(byEns.get(e.label) ?? []), e]);
  const avg = (xs: number[]) => xs.reduce((p, q) => p + q, 0) / xs.length;
  const ens = [...byEns].map(([label, rows]) => {
    const raw = rows[0].ensemble_model ?? label;
    // The ensemble's own leaderboard row carries its 95% interval; it matches
    // the dataset average only when the ensemble was scored on every core dataset.
    const sys = systems().find((c) => c.method === "ensemble" && !c.variant && c.base === raw);
    const ci: [number, number] | undefined =
      sys && rows.length === CORE.length && sys.indexLo != null && sys.indexHi != null
        ? [sys.indexLo, sys.indexHi]
        : undefined;
    return {
      label,
      name: rows[0].ensemble_model ? ensembleNames(raw).full : label,
      a: avg(rows.map((r) => r.a)),
      b: avg(rows.map((r) => r.b)),
      top: avg(rows.map((r) => r.top)),
      ci,
    };
  });
  const best = ens.reduce((p, q) => (q.b > p.b ? q : p));
  items.push({
    id: "ensemble",
    short: "Ensembles",
    claim:
      winsMember === ec.length
        ? "Blending models whose errors differ beats the blend's own best member on every dataset tested"
        : `Blending models whose errors differ beats the blend's own best member in ${winsMember} of ${ec.length} ensemble–dataset comparisons`,
    confidence: [2, "Moderate"],
    number: signedRange(
      Math.min(...ens.map((e) => e.b - e.a)),
      Math.max(...ens.map((e) => e.b - e.a)),
    ),
    numberLabel:
      "Index points over the ensemble's own best member (not the best system overall), averaged over datasets",
    meaning:
      "Pick members whose errors point in different directions, not just the top scorers. Three mid-table models can match a blend of the strongest. The same model with and without a persona errs alike, so it adds little.",
    evidence: `Equal-weight average of the members' per-question answer distributions.${corr.length ? ` Members' error sizes correlate at r = ${Math.min(...corr).toFixed(2)} to ${Math.max(...corr).toFixed(2)}.` : ""} Against the best single system on each dataset, rather than the blend's own members, an ensemble wins ${winsTop} of ${ec.length} comparisons (${signedRange(Math.min(...vsTop), Math.max(...vsTop))} Index points). The complementary blends were chosen from about 64,000 combinations using only the public questions, and they keep their lead on the private questions that played no part in choosing them. The best blend here, ${best.label}, averages ${fmt.int(best.b)} against ${fmt.int(best.top)} for the best single system. Each ensemble has one run per dataset; the whisker on each ensemble is the 95% interval of its Index. It costs three or four times as much as a single run.`,
    viz(el) {
      const lo = Math.min(-10, Math.floor(Math.min(...ens.map((e) => e.a)) / 10) * 10);
      const hi = Math.max(60, Math.ceil(Math.max(...ens.map((e) => e.ci?.[1] ?? e.b)) / 10) * 10);
      dumbbell(
        el,
        ens.map((e) => ({
          name: e.label,
          a: e.a,
          b: e.b,
          errB: e.ci,
          label: fmt.delta(e.b - e.a),
          tip: [
            ["Ensemble", e.name],
            ["Best member, average Index", fmt.one(e.a)],
            ["Ensemble, average Index", fmt.one(e.b)],
            ...(e.ci
              ? ([
                  ["Ensemble Index, 95% interval", `${fmt.int(e.ci[0])} to ${fmt.int(e.ci[1])}`],
                ] as [string, string][])
              : []),
            ["Best single system, average", fmt.one(e.top)],
          ],
        })),
        {
          domain: [lo, hi],
          axis: "SynthBench Index, averaged over datasets (0 = random answers)",
          labelW: 210,
          zero: 0,
          a: method("althing"),
          b: method("ensemble"),
        },
      );
      el.after(
        legend(
          key(method("althing"), "best member"),
          key(method("ensemble"), "ensemble, with its 95% interval"),
        ),
      );
    },
  });
}

// 3. Persona template
const tpls = systems()
  .filter((c) => c.variant?.startsWith("temperature 0.85") && c.ds.subpop)
  .sort((a, b) => b.ds.subpop.idx - a.ds.subpop.idx);
if (tpls.length > 1) {
  const tplName = (v: string | null) => v?.match(/(\w+) template/)?.[1] ?? "default";
  const top = tpls[0];
  const bottom = tpls[tpls.length - 1];
  const range = top.ds.subpop.idx - bottom.ds.subpop.idx;
  const allBelow = top.ds.subpop.idx < 0;
  const tplRuns = tpls.map((c) => c.ds.subpop.runs ?? 1);
  const published = systems().find(
    (c) => c.baseId === top.baseId && c.method === "althing" && !c.variant && !c.harness,
  )?.ds.subpop;
  const def = tpls.find((c) => tplName(c.variant) === "default");
  items.push({
    id: "template",
    short: "Prompt template",
    claim: `The wording of the persona prompt alone moved the score by ${fmt.int(range)} points${allBelow ? "; even the best template scored below random here" : ""}`,
    confidence: rate(Math.min(...tplRuns)),
    number: `${fmt.int(range)} pts`,
    numberLabel: `between the best and worst of ${tpls.length} templates (SubPOP, ${top.base}, temperature 0.85)`,
    meaning:
      "Treat the persona template like a model version: track every change and re-run the benchmark after each one.",
    evidence: `Same model, temperature 0.85, ${top.ds.subpop.n} SubPOP questions, ${runsText(tplRuns, "template")}, so differences of a few points may be noise.${def && published ? ` At temperature 0.85 even the default template scores ${fmt.int(def.ds.subpop.idx)}, against ${fmt.int(published.idx)} for the published persona run at the default temperature.` : ""} Most of the drop comes from refusal match, which falls from ${top.ds.subpop.pRefuse.toFixed(2)} with the ${tplName(top.variant)} template to ${bottom.ds.subpop.pRefuse.toFixed(2)} with the ${tplName(bottom.variant)} template. The other templates made the model decline far more often than people do.`,
    viz(el) {
      const lo = Math.min(
        -60,
        Math.floor(Math.min(...tpls.map((c) => c.ds.subpop.lo ?? 0)) / 20) * 20,
      );
      dumbbell(
        el,
        tpls.map((c) => ({
          name: `${tplName(c.variant)} template`,
          a: 0,
          b: c.ds.subpop.idx,
          errB:
            c.ds.subpop.lo != null && c.ds.subpop.hi != null
              ? [c.ds.subpop.lo, c.ds.subpop.hi]
              : undefined,
          label: fmt.int(c.ds.subpop.idx),
          tip: [
            ["Index", fmt.one(c.ds.subpop.idx)],
            ["95% interval", `${fmt.int(c.ds.subpop.lo)} to ${fmt.int(c.ds.subpop.hi)}`],
            ["Refusal match", c.ds.subpop.pRefuse.toFixed(3)],
            ["Runs", String(c.ds.subpop.runs ?? 1)],
          ],
        })),
        {
          domain: [lo, 20],
          axis: "Index on SubPOP (0 = random answers)",
          zero: 0,
          a: none,
          b: method("althing"),
        },
      );
      el.after(legend("Whiskers: 95% interval over questions, from one run per template."));
    },
  });
}

// 4. Temperature
const sweep = (F.temperature_sweep ?? [])
  .filter((p) => (p.dataset ?? "opinionsqa") === "opinionsqa")
  .sort((a, b) => a.temperature - b.temperature);
const models = [...new Set(sweep.map((p) => p.model))];
if (models.length) {
  const per = models.map((m) => sweep.filter((q) => q.model === m));
  // Compare every model over the temperature range they were all run on.
  const tLo = Math.max(...per.map((p) => p[0].temperature));
  const tHi = Math.min(...per.map((p) => p[p.length - 1].temperature));
  const at = (p: typeof sweep, t: number) => p.find((q) => q.temperature === t);
  const shared = per
    .map((p, i) => {
      const a = at(p, tLo);
      const b = at(p, tHi);
      return a && b
        ? { model: models[i], gain: idxOf("opinionsqa", b.sps) - idxOf("opinionsqa", a.sps) }
        : null;
    })
    .filter((g): g is NonNullable<typeof g> => g != null);
  const up = shared.filter((g) => g.gain > 0).length;
  const runs = sweep.map((p) => p.n_runs ?? 1);
  const hasBand = sweep.some((p) => (p.n_runs ?? 1) > 1 && (p.std ?? 0) > 0);
  const longer = per.filter((p) => p[p.length - 1].temperature > tHi);
  const name = (m: string) => modelNameFromLabel(m);
  items.push({
    id: "temperature",
    short: "Temperature",
    claim:
      up === shared.length
        ? `Raising temperature from ${tLo} to ${tHi} improved all ${shared.length} models tested, by different amounts`
        : `Raising temperature from ${tLo} to ${tHi} improved ${up} of ${shared.length} models tested`,
    confidence: rate(Math.min(...runs)),
    number: shared.length
      ? signedRange(Math.min(...shared.map((g) => g.gain)), Math.max(...shared.map((g) => g.gain)))
      : "—",
    numberLabel: `Index change from temperature ${tLo} to ${tHi} (OpinionsQA, Althing persona)`,
    meaning:
      "Test a few temperatures for each model before running a study. The size of the gain differs between models, so a setting tuned on one doesn't carry over.",
    evidence: `Althing persona runs on OpinionsQA, ${runsText(runs, "temperature")}.${hasBand ? " The band shows ±1 standard deviation across repeat runs." : " With a single run per point there is no error band, so differences of a few points may be noise."} The models were swept over different ranges, so the headline compares them on the range they share (${tLo} to ${tHi}, shaded).${longer.length ? ` ${longer.map((p) => `${name(p[0].model)} was also run up to ${p[p.length - 1].temperature}`).join("; ")}.` : ""}`,
    viz(el) {
      const grid = h("div", { class: "sb-sm3" });
      el.append(grid);
      const all = sweep.map((p) => idxOf("opinionsqa", p.sps));
      const lo = Math.floor((Math.min(...all) - 5) / 5) * 5;
      const hi = Math.ceil((Math.max(...all) + 5) / 5) * 5;
      const tMin = Math.min(...sweep.map((p) => p.temperature));
      const tMax = Math.max(...sweep.map((p) => p.temperature));
      for (const [i, m] of models.entries()) {
        const pts = per[i].map((p) => ({
          x: p.temperature,
          y: idxOf("opinionsqa", p.sps),
          sd: hasBand ? idxOf("opinionsqa", p.sps + (p.std ?? 0)) - idxOf("opinionsqa", p.sps) : 0,
        }));
        const g = shared.find((x) => x.model === m);
        const last = pts[pts.length - 1];
        const chart = h("div");
        grid.append(
          h(
            "div",
            null,
            h("h3", null, name(m)),
            h(
              "div",
              { class: "sb-note" },
              [
                g ? `${fmt.delta(g.gain)} from ${tLo} to ${tHi}` : null,
                last.x > tHi ? `${fmt.delta(last.y - pts[0].y)} up to ${last.x}` : null,
              ]
                .filter(Boolean)
                .join("; "),
            ),
            chart,
          ),
        );
        mount(chart, (W) => {
          const H = 170;
          const mg = { l: 44, r: 6, t: 8, b: 40 };
          const X = linear(tMin - 0.05, tMax + 0.05, mg.l, W - mg.r);
          const Y = linear(lo, hi, H - mg.b, mg.t);
          const svg = s("svg", {
            class: "sb-c",
            width: W,
            height: H,
            role: "img",
            "aria-label": `${name(m)}: Index by temperature`,
          });
          chart.append(svg);
          s(
            "rect",
            {
              x: X(tLo),
              y: mg.t,
              width: X(tHi) - X(tLo),
              height: H - mg.b - mg.t,
              fill: css("--sb-grid"),
              opacity: 0.6,
            },
            svg,
          );
          for (const t of ticks(lo, hi, 3)) {
            s("line", { class: "sb-gl", x1: mg.l, x2: W - mg.r, y1: Y(t), y2: Y(t) }, svg);
            s(
              "text",
              { class: "sb-t", x: mg.l - 4, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
              svg,
            );
          }
          for (const t of axisTicks(tMin, tMax, X, String, 4))
            s(
              "text",
              {
                class: "sb-t",
                x: X(t),
                y: H - mg.b + 14,
                "text-anchor": "middle",
                text: String(t),
              },
              svg,
            );
          axisTitle(svg, "Temperature", { x: (mg.l + W - mg.r) / 2, y: H - 4 });
          axisTitle(svg, "Index", { x: 12, y: (mg.t + H - mg.b) / 2, vertical: true });
          if (hasBand) {
            const band = `${pts.map((p, j) => `${j ? "L" : "M"}${X(p.x)},${Y(p.y + p.sd)}`).join("")}${[
              ...pts,
            ]
              .reverse()
              .map((p) => `L${X(p.x)},${Y(p.y - p.sd)}`)
              .join("")}Z`;
            s("path", { d: band, fill: methodColor("althing"), opacity: 0.14 }, svg);
          }
          s(
            "path",
            {
              d: pts.map((p, j) => `${j ? "L" : "M"}${X(p.x)},${Y(p.y)}`).join(""),
              fill: "none",
              stroke: methodColor("althing"),
              "stroke-width": 2,
            },
            svg,
          );
          for (const p of pts) marker(svg, "althing", X(p.x), Y(p.y), 3);
        });
      }
      el.after(
        legend(
          `Shaded: the range all ${models.length} models were run on. Each dot is ${hasBand ? "the mean of repeat runs" : "a single run"}.`,
        ),
      );
    },
  });
}

// 5. Model consensus
const conc = Object.entries(d.concordance ?? {}).flatMap(([id, b]) =>
  b.mean_cross_model_jsd != null && b.mean_human_jsd != null
    ? [{ id, cross: b.mean_cross_model_jsd, human: b.mean_human_jsd }]
    : [],
);
if (conc.length) {
  const pct = (b: { cross: number; human: number }) => Math.round((1 - b.cross / b.human) * 100);
  const pctLabel = (b: { cross: number; human: number }) =>
    pct(b) >= 0 ? `${pct(b)}% lower` : `${-pct(b)}% higher`;
  const best = conc.reduce((p, q) => (pct(q) > pct(p) ? q : p));
  const agree = conc.filter((b) => pct(b) > 0);
  const against = conc.filter((b) => pct(b) <= 0);
  items.push({
    id: "consensus",
    short: "Model agreement",
    claim:
      agree.length === conc.length
        ? "Models agree with each other more than they agree with people"
        : `On ${agree.length} of ${conc.length} datasets, models agree with each other more than they agree with people`,
    confidence: [2, "Moderate"],
    number: `${agree.length} of ${conc.length}`,
    numberLabel: `datasets where models are closer to each other than to people (up to ${pct(best)}% lower divergence, ${dsLabel(best.id)})`,
    meaning:
      "Several models giving the same answer is not evidence that the answer is right. They share training data and often make the same mistakes.",
    evidence: `Mean pairwise Jensen-Shannon divergence between raw LLM answer distributions, compared with the mean divergence between each model and people.${against.length ? ` On ${against.map((b) => dsLabel(b.id)).join(" and ")} it goes the other way: models differ from each other ${against.map((b) => `${-pct(b)}%`).join(" and ")} more than they differ from people.` : ""} These are single averages over all raw LLMs, with no interval.`,
    viz(el) {
      const vals = conc.flatMap((b) => [b.cross, b.human]);
      dumbbell(
        el,
        conc.map((b) => ({
          name: dsLabel(b.id),
          a: b.human,
          b: b.cross,
          label: pctLabel(b),
          tip: [
            ["Model vs. people", b.human.toFixed(3)],
            ["Model vs. model", b.cross.toFixed(3)],
          ],
        })),
        {
          domain: [Math.floor(Math.min(...vals) * 20) / 20, Math.ceil(Math.max(...vals) * 20) / 20],
          axis: "Mean Jensen-Shannon divergence (lower = more alike)",
          tick: (v) => v.toFixed(2),
          a: ring,
          b: solid,
        },
      );
      el.after(
        legend(
          key(ring, "model vs. people"),
          key(solid, "model vs. model"),
          h("span", null, "Right: how much lower (or higher) model vs. model is"),
        ),
      );
    },
  });
}

// 6. Default voice
const cr = F.conditioning_results ?? [];
const attrs = [...new Set(cr.map((r) => r.attribute))];
const party = cr.filter((r) => r.attribute === "POLPARTY");
if (party.length === 2) {
  const ATTR: Record<string, string> = {
    POLPARTY: "Party",
    INCOME: "Income",
    EDUCATION: "Education",
  };
  const [hiP, loP] = [...party].sort((a, b) => b.p_cond - a.p_cond);
  // "Per-group conditioned SubPOP evaluations (Haiku 4.5, t=0.85); ..."
  const setup = F.comparison_sets?.conditioning_results?.match(/\(([^,()]+), t=([\d.]+)\)/);
  const baseModel = setup
    ? (systems().find((c) => c.base.endsWith(setup[1]))?.base ?? setup[1])
    : null;
  const pairs = attrs
    .map((a) => {
      const pair = cr.filter((r) => r.attribute === a).sort((p, q) => q.p_cond - p.p_cond);
      if (pair.length !== 2) return null;
      const [far, near] = pair;
      // Standard error of the difference between the two group means.
      const se = Math.sqrt(
        (far.p_cond_std ?? 0) ** 2 / far.n_replications +
          (near.p_cond_std ?? 0) ** 2 / near.n_replications,
      );
      return { a, far, near, clear: se > 0 && far.p_cond - near.p_cond > 2 * se };
    })
    .filter((r): r is NonNullable<typeof r> => r != null);
  const clear = pairs.filter((p) => p.clear).map((p) => (ATTR[p.a] ?? p.a).toLowerCase());
  const noisy = pairs.filter((p) => !p.clear).map((p) => (ATTR[p.a] ?? p.a).toLowerCase());
  const reps = cr.map((r) => r.n_replications);
  const hasSd = cr.every((r) => r.p_cond_std != null);
  const list = (xs: string[]) =>
    xs.length > 1 ? `${xs.slice(0, -1).join(", ")} and ${xs[xs.length - 1]}` : xs[0];
  items.push({
    id: "voice",
    short: "Default voice",
    claim: "A model's default answers already resemble some groups more than others",
    confidence: rate(Math.min(...reps)),
    number: `${(hiP.p_cond / loP.p_cond).toFixed(1)}×`,
    numberLabel: `as much adjustment needed to answer like a ${hiP.group} as like a ${loP.group}${baseModel ? ` (${baseModel})` : ""}`,
    meaning:
      "Synthetic samples lean toward the model's default respondent. Check accuracy for each subgroup before reporting splits.",
    evidence: `Althing persona on ${baseModel ?? "one base model"}, SubPOP${setup ? `, temperature ${setup[2]}` : ""}, ${runsText(reps, "group")}. One model only, so this shows how that model's default leans, not every model's.${clear.length ? ` The ${list(clear)} gap${clear.length > 1 ? "s are" : " is"} more than twice ${clear.length > 1 ? "their" : "its"} standard error.` : ""}${noisy.length ? ` The ${list(noisy)} gap${noisy.length > 1 ? "s are" : " is"} within run-to-run noise.` : ""}`,
    viz(el) {
      const sd = (r: (typeof cr)[number]): [number, number] | undefined =>
        r.p_cond_std != null
          ? [Math.max(0, r.p_cond - r.p_cond_std), r.p_cond + r.p_cond_std]
          : undefined;
      const rows = pairs.map(({ a, far, near }) => ({
        name: `${ATTR[a] ?? a}: ${near.group} vs. ${far.group}`,
        a: near.p_cond,
        b: far.p_cond,
        errA: sd(near),
        errB: sd(far),
        label: `${(far.p_cond / near.p_cond).toFixed(1)}×`,
        tip: [
          [
            near.group,
            `${near.p_cond.toFixed(3)} ± ${(near.p_cond_std ?? 0).toFixed(3)} (${near.n_replications} runs)`,
          ],
          [
            far.group,
            `${far.p_cond.toFixed(3)} ± ${(far.p_cond_std ?? 0).toFixed(3)} (${far.n_replications} runs)`,
          ],
        ] as [string, string][],
      }));
      const top = Math.max(...rows.map((r) => r.errB?.[1] ?? r.b));
      // Ticks every 0.02, so labels like 0.025 never round to "0.03". The axis
      // ends on a multiple of 0.04 so that when a narrow chart keeps every
      // other tick, they stay evenly spaced up to the end.
      const steps = 2 * Math.ceil(top / 0.04 - 1e-9);
      const tickValues = Array.from({ length: steps + 1 }, (_, k) => +(k * 0.02).toFixed(2));
      const hi = tickValues[tickValues.length - 1];
      dumbbell(el, rows, {
        domain: [0, hi],
        axis: "How far the persona must shift answers toward the group (P_cond)",
        tick: (v) => v.toFixed(2),
        tickValues,
        labelW: 230,
        a: ring,
        b: solid,
      });
      el.after(
        legend(
          key(ring, "group closer to the model's default answers"),
          key(solid, "group further from them"),
          hasSd
            ? h("span", null, `Whiskers: ±1 standard deviation across ${runsText(reps, "group")}`)
            : null,
        ),
      );
    },
  });
}

// 7. "Don't know" on sensitive questions
const stt = F.sensitive_topic_sidestepping;
if (stt?.items?.length) {
  const Q: Record<string, string> = {
    GSS_FEPRESCH: "Preschooler suffers if mother works",
    GSS_NATRACE: "Spending on conditions of Black Americans",
    GSS_POSTLIFE: "Life after death",
    GSS_NATHEAL: "Spending on health",
    GSS_NATFARE: "Spending on welfare",
    GSS_NATEDUC: "Spending on education",
    GSS_NATCRIME: "Spending on crime",
    GSS_FINRELA: "Family income vs. the average",
    GSS_CLASS: "Own social class",
    GSS_GUNLAW: "Permits to buy a gun",
    GSS_HEALTH: "Own health",
    GSS_SATFIN: "Satisfaction with finances",
    GSS_TAX: "Own federal income tax",
    GSS_OWNGUN: "Gun in the home",
    GSS_GOD: "Belief in God",
    GSS_BIBLE: "View of the Bible",
    GSS_POLVIEWS: "Own political views",
    GSS_ABANY: "Abortion for any reason",
    GSS_ABSINGLE: "Abortion if not married",
    GSS_LETDIE1: "End of life for incurable disease",
    GSS_SUICIDE1: "Suicide if incurable disease",
    GSS_CONFINAN: "Confidence in banks",
    GSS_CONJUDGE: "Confidence in the Supreme Court",
    GSS_CONPRESS: "Confidence in the press",
    GSS_CONMEDIC: "Confidence in medicine",
    GSS_CONSCI: "Confidence in science",
    GSS_CONFED: "Confidence in the federal government",
    GSS_CONBUS: "Confidence in major companies",
    GSS_CONEDUC: "Confidence in education",
    GSS_XMARSEX: "Extramarital sex",
    GSS_HOMOSEX: "Same-sex relations",
    GSS_PREMARSX: "Sex before marriage",
    GSS_PORNLAW: "Pornography laws",
    GSS_GRASS: "Legalizing marijuana",
    GSS_CAPPUN: "Death penalty for murder",
  };
  // Unknown keys: the question's last sentence (GSS items start with a shared
  // preamble), cut at a word boundary from the front.
  const label = (key: string, t: string | undefined) => {
    if (Q[key]) return Q[key];
    if (!t) return key;
    const last =
      t
        .split(/(?<=[.?])\s+/)
        .filter(Boolean)
        .pop() ?? t;
    if (last.length <= 44) return last;
    return `${last.slice(0, 42).replace(/\s+\S*$/, "")}…`;
  };
  const optionShare = (r: {
    mean_model_option_mass?: number;
    mean_model_nonresponse_mass: number;
  }) => r.mean_model_option_mass ?? r.mean_model_nonresponse_mass;
  const runs = (F.nonresponse_fidelity ?? []).filter((r) => r.dataset === stt.dataset);
  const humanOpt = stt.mean_human_nonresponse_mass;
  const worstRun = runs.find((r) => r.provider === stt.provider && r.framework === "raw");
  const humanAll = worstRun?.mean_human_nonresponse_mass;
  const ratios = runs.map((r) => optionShare(r) / humanOpt).sort((a, b) => a - b);
  const medianRatio = ratios.length
    ? ratios.length % 2
      ? ratios[ratios.length >> 1]
      : (ratios[ratios.length / 2 - 1] + ratios[ratios.length / 2]) / 2
    : null;
  const far = ratios.filter((x) => x > 10).length;
  const worst = stt.mean_model_nonresponse_mass / humanOpt;
  items.push({
    id: "dont-know",
    short: "“Don't know”",
    claim:
      "A few models pick “don't know” far more often than people do, a failure that refusal metrics miss",
    confidence: rate(1),
    number: runs.length ? `${far} of ${runs.length}` : `${worst.toFixed(0)}×`,
    numberLabel: runs.length
      ? `runs on ${dsLabel(stt.dataset)} pick “don't know” more than 10× as often as people. Worst: ${stt.provider} (raw), ${worst.toFixed(0)}×. Median run: ${medianRatio?.toFixed(1)}×.`
      : `the human rate of “don't know” answers (${stt.provider}, ${dsLabel(stt.dataset)})`,
    meaning:
      "Report “don't know” answers separately, and check which questions a model declines before trusting its averages. Most models don't do this, so it's a per-model check, not a rule.",
    evidence: `The model picks a listed “don't know” option instead of refusing, so refusal-rate metrics miss it. People pick a listed “don't know” option on ${pctText(humanOpt)} of answers to these ${stt.n_questions} questions${humanAll != null ? `; counting people who skipped or refused the question as well, the human nonresponse rate is ${pctText(humanAll)}` : ""}. This finding compares listed options only. The first chart shows every run on ${dsLabel(stt.dataset)}, one run each; the second shows the questions with the largest gap for the worst run.`,
    viz(el) {
      if (runs.length) {
        const strip = h("div");
        el.append(h("h3", null, `Every run on ${dsLabel(stt.dataset)}`), strip);
        const groups: [string, Method, typeof runs][] = [
          ["Raw LLM", "raw", runs.filter((r) => r.framework === "raw")],
          ["Althing persona", "althing", runs.filter((r) => r.framework !== "raw")],
        ];
        mount(strip, (W) => {
          const L = rowLayout(W, 120, 30);
          const { rowH } = L;
          const plotB = groups.length * rowH;
          const H = plotB + 44;
          const hi = Math.max(0.2, Math.ceil(Math.max(...runs.map(optionShare)) * 10) / 10);
          const x = linear(0, hi, L.narrow ? 8 : L.labelW + 12, W - 16);
          const svg = s("svg", {
            class: "sb-c",
            width: W,
            height: H,
            role: "img",
            "aria-label": "Share of answers that pick “don't know”, per run",
          });
          strip.append(svg);
          for (const t of axisTicks(0, hi, x, (v) => `${Math.round(v * 100)}%`, 5)) {
            s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
            s(
              "text",
              {
                class: "sb-t",
                x: x(t),
                y: plotB + 15,
                "text-anchor": "middle",
                text: `${Math.round(t * 100)}%`,
              },
              svg,
            );
          }
          // Narrow rows put their label above the dots, so the people line is
          // drawn through each row's dots only, never through a label.
          const spans: [number, number][] = L.narrow
            ? groups.map((_, i) => [i * rowH + L.markY - 10, i * rowH + L.markY + 10])
            : [[0, plotB]];
          for (const [y1, y2] of spans)
            s(
              "line",
              {
                x1: x(humanOpt),
                x2: x(humanOpt),
                y1,
                y2,
                stroke: css("--sb-ink"),
                "stroke-width": 1.5,
              },
              svg,
            );
          axisTitle(svg, "Share of answers that pick “don't know” (line = people)", {
            x: (x(0) + x(hi)) / 2,
            y: H - 4,
          });
          groups.forEach(([name, m, rs], i) => {
            const cy = i * rowH + L.markY;
            rowLabel(svg, L, W, i * rowH, name);
            for (const r of rs) {
              const g = s("g", { opacity: 0.8 }, svg);
              marker(g, m, x(optionShare(r)), cy, 4);
              hoverInfo(
                s(
                  "rect",
                  { class: "sb-hit", x: x(optionShare(r)) - 5, y: cy - 8, width: 10, height: 16 },
                  svg,
                ),
                r.provider,
                [
                  ["Picks “don't know”", pctText(optionShare(r))],
                  ["People", pctText(humanOpt)],
                  ["Ratio", `${(optionShare(r) / humanOpt).toFixed(1)}×`],
                ],
              );
            }
          });
        });
      }
      const qs = h("div");
      el.append(h("h3", null, `Worst run: ${stt.provider} (raw), largest gaps`), qs);
      dumbbell(
        qs,
        stt.items.map((it) => ({
          name: label(it.key, it.text),
          a: it.human_mass,
          b: it.model_mass,
          label: `${Math.round(it.model_mass * 100)}%`,
          tip: [
            ["Question", it.text ?? it.key],
            ["People", pctText(it.human_mass)],
            ["Model", pctText(it.model_mass)],
          ],
        })),
        {
          domain: [0, 1],
          axis: "Share of answers that pick “don't know”",
          tick: (v) => `${Math.round(v * 100)}%`,
          labelW: 250,
          a: ring,
          b: method("raw"),
        },
      );
      qs.after(legend(key(ring, "people"), key(method("raw"), "model")));
    },
  });
}

// ---------- Render ----------
const meter = (n: number, label: string) =>
  h(
    "span",
    { class: "sb-conf", title: "How strong the evidence is" },
    h(
      "i",
      null,
      [0, 1, 2].map((i) => h("b", { class: i < n ? "on" : null })),
    ),
    `Evidence: ${label}`,
  );
document
  .getElementById("fd-toc")
  ?.replaceChildren(
    ...items.map((it, i) =>
      h(
        "a",
        { href: `#${it.id}` },
        h("span", { class: "i" }, String(i + 1).padStart(2, "0")),
        h("span", null, h("b", null, it.short), `${it.confidence[1]} · ${it.number}`),
      ),
    ),
  );
const list = document.getElementById("fd-list");
items.forEach((it, i) => {
  const viz = h("div");
  list?.append(
    h(
      "section",
      { class: "sb-block sb-panel sb-finding", id: it.id },
      h(
        "div",
        { class: "txt" },
        h(
          "div",
          { class: "top" },
          h("span", { class: "sb-kicker" }, `Finding ${String(i + 1).padStart(2, "0")}`),
          meter(...it.confidence),
        ),
        h("h2", { class: "claim" }, it.claim),
        h(
          "div",
          null,
          h("div", { class: "num" }, it.number),
          h("div", { class: "numl" }, it.numberLabel),
        ),
        h("div", { class: "so" }, h("b", null, "What it means: "), it.meaning),
        h("details", null, h("summary", null, "Evidence and caveats"), h("p", null, it.evidence)),
      ),
      h("div", { class: "viz" }, viz),
    ),
  );
  it.viz(viz);
});
if (location.hash) setTimeout(() => document.querySelector(location.hash)?.scrollIntoView(), 100);

initShell();
