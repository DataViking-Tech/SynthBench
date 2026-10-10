import { axisTitle, css, fmt, h, linear, mount, s, ticks } from "../dom";
import { CORE, type Method, data, dsLabel, dsMeta, pruneCompare, systems } from "../model";
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
  tip?: [string, string][];
}
/** One row per item: a line from value a to value b, with a value label on the right. */
function dumbbell(
  el: HTMLElement,
  rows: DumbRow[],
  o: {
    domain: [number, number];
    axis: string;
    tick?: (v: number) => string;
    labelW?: number;
    zero?: number;
    a: Mark;
    b: Mark;
  },
): void {
  mount(el, (W) => {
    const rowH = 34;
    const labelW = Math.min(o.labelW ?? 130, W * 0.46);
    const plotB = rows.length * rowH;
    const H = plotB + 44;
    const tick = o.tick ?? fmt.int;
    const x = linear(o.domain[0], o.domain[1], labelW + 12, W - 82);
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
    for (const t of ticks(o.domain[0], o.domain[1], 5)) {
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
    rows.forEach((r, i) => {
      const cy = i * rowH + rowH / 2;
      s(
        "text",
        { x: labelW, y: cy + 4, "text-anchor": "end", class: "sb-lab sb-light", text: r.name },
        svg,
      );
      s(
        "line",
        { x1: x(r.a), x2: x(r.b), y1: cy, y2: cy, stroke: css("--sb-line-2"), "stroke-width": 2 },
        svg,
      );
      (r.markA ?? o.a)(svg, x(r.a), cy);
      o.b(svg, x(r.b), cy);
      s("text", { x: W - 2, y: cy + 4, "text-anchor": "end", class: "sb-val", text: r.label }, svg);
      if (r.tip)
        hoverInfo(
          s("rect", { class: "sb-hit", x: 0, y: cy - rowH / 2, width: W, height: rowH }, svg),
          r.name,
          r.tip,
        );
    });
  });
}
const legend = (...items: (string | Node)[]) => h("div", { class: "sb-note sb-legend" }, ...items);
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

// 1. Raw LLMs vs. random answers
const raws = systems().filter((c) => c.method === "raw" && !c.variant);
const goqa = raws.filter((c) => c.ds.globalopinionqa);
items.push({
  id: "random",
  short: "Raw LLMs vs. random",
  claim:
    "A directly prompted LLM scores close to random answers, and below random on cross-national questions",
  confidence: [3, "Strong"],
  number: `${goqa.filter((c) => c.ds.globalopinionqa.idx < 0).length} of ${goqa.length}`,
  numberLabel: "raw LLMs score below random on GlobalOpinionQA",
  meaning:
    "A plain prompt is not a substitute for a survey panel. Check results against real data before using them for a new population.",
  evidence:
    "Random answers spread probability evenly across the options, which matches questions where people are split. LLMs do worse than random at matching answer shares and better at matching answer order (see Analysis, Shares vs. order).",
  viz(el) {
    const rows = CORE.map((id): DumbRow => {
      const v = raws
        .filter((c) => c.ds[id])
        .map((c) => c.ds[id].idx)
        .sort((p, q) => p - q);
      return {
        name: dsLabel(id),
        a: v[0],
        b: v[v.length - 1],
        label: `median ${fmt.int(v[v.length >> 1])}`,
        tip: [
          ["Lowest raw LLM", fmt.one(v[0])],
          ["Highest raw LLM", fmt.one(v[v.length - 1])],
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
const ec = (F.ensemble_comparison ?? []).map((e) => ({
  ...e,
  a: idxOf(e.dataset, e.best_single_sps),
  b: idxOf(e.dataset, e.ensemble_sps),
}));
if (ec.length) {
  const corr = (F.ensemble_error_correlation ?? []).map((c) => c.mean_pearson_r);
  items.push({
    id: "ensemble",
    short: "Ensembles",
    claim: "Averaging three systems beats the best single system on every dataset tested",
    confidence: [3, "Strong"],
    number: `+${Math.round(Math.min(...ec.map((e) => e.b - e.a)))} to +${Math.round(Math.max(...ec.map((e) => e.b - e.a)))}`,
    numberLabel: "Index points over the best single system",
    meaning:
      "If you can pay for three calls per respondent, average models from different labs. The gain comes from the errors they don't share.",
    evidence: `Equal-weight average of the members' per-question answer distributions.${corr.length ? ` The members' errors correlate at r = ${Math.min(...corr).toFixed(2)} to ${Math.max(...corr).toFixed(2)}.` : ""} It costs about three times as much as a single run.`,
    viz(el) {
      dumbbell(
        el,
        ec.map((e) => ({
          name: dsLabel(e.dataset),
          a: e.a,
          b: e.b,
          label: fmt.delta(e.b - e.a),
          markA: method(e.best_single_framework === "raw" ? "raw" : "althing"),
          tip: [
            ["Best single system", `${e.best_single_model}, ${fmt.one(e.a)}`],
            ["Ensemble", fmt.one(e.b)],
          ],
        })),
        {
          domain: [-10, 60],
          axis: "SynthBench Index (0 = random answers)",
          zero: 0,
          a: method("althing"),
          b: method("ensemble"),
        },
      );
      el.after(
        legend(
          swatch(method("althing")),
          " best single system (hollow if a raw prompt)   ",
          swatch(method("ensemble")),
          " ensemble",
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
  items.push({
    id: "template",
    short: "Prompt template",
    claim: "The wording of the persona prompt alone can drop a system below random answers",
    confidence: [2, "Moderate"],
    number: fmt.delta(bottom.ds.subpop.idx - top.ds.subpop.idx),
    numberLabel: `Index change from the template alone (SubPOP, ${top.base})`,
    meaning:
      "Treat the persona template like a model version: track every change and re-run the benchmark after each one.",
    evidence: `Same model, temperature 0.85, ${top.ds.subpop.n} SubPOP questions, one or two runs per template. Most of the drop comes from refusal match, which falls from ${top.ds.subpop.pRefuse.toFixed(2)} with the ${tplName(top.variant)} template to ${bottom.ds.subpop.pRefuse.toFixed(2)} with the ${tplName(bottom.variant)} template. The other templates made the model decline far more often than people do.`,
    viz(el) {
      dumbbell(
        el,
        tpls.map((c) => ({
          name: `${tplName(c.variant)} template`,
          a: 0,
          b: c.ds.subpop.idx,
          label: fmt.int(c.ds.subpop.idx),
          tip: [["Refusal match", c.ds.subpop.pRefuse.toFixed(3)]],
        })),
        {
          domain: [-100, 20],
          axis: "Index on SubPOP (0 = random answers)",
          zero: 0,
          a: none,
          b: method("althing"),
        },
      );
    },
  });
}

// 4. Temperature
const sweep = (F.temperature_sweep ?? []).filter(
  (p) => (p.dataset ?? "opinionsqa") === "opinionsqa",
);
const models = [...new Set(sweep.map((p) => p.model))];
if (models.length) {
  const gains = models.map((m) => {
    const p = sweep.filter((q) => q.model === m);
    return idxOf("opinionsqa", Math.max(...p.map((q) => q.sps))) - idxOf("opinionsqa", p[0].sps);
  });
  const runs = sweep.map((p) => p.n_runs).filter((n): n is number => n != null);
  items.push({
    id: "temperature",
    short: "Temperature",
    claim: "Higher temperature helps some models and makes little difference for others",
    confidence: [2, "Moderate"],
    number: fmt.delta(Math.max(...gains)),
    numberLabel: "largest gain from changing temperature (OpinionsQA)",
    meaning:
      "Test a few temperatures for each model before running a study. A setting that works for one model doesn't carry over to another.",
    evidence: `Althing persona runs on OpinionsQA${runs.length ? `, ${Math.min(...runs)} to ${Math.max(...runs)} repeat runs per point` : ""}. The band shows ±1 standard deviation.`,
    viz(el) {
      const grid = h("div", { class: "sb-sm3" });
      el.append(grid);
      const all = sweep.map((p) => idxOf("opinionsqa", p.sps));
      const lo = Math.floor((Math.min(...all) - 5) / 5) * 5;
      const hi = Math.ceil((Math.max(...all) + 5) / 5) * 5;
      const tMin = Math.min(...sweep.map((p) => p.temperature));
      const tMax = Math.max(...sweep.map((p) => p.temperature));
      for (const m of models) {
        const pts = sweep
          .filter((p) => p.model === m)
          .map((p) => ({
            x: p.temperature,
            y: idxOf("opinionsqa", p.sps),
            sd: idxOf("opinionsqa", p.sps + (p.std ?? 0)) - idxOf("opinionsqa", p.sps),
          }));
        const chart = h("div");
        grid.append(
          h(
            "div",
            null,
            h(
              "h4",
              null,
              m
                .replace("GPT-4o-mini", "GPT-4o mini")
                .replace("Gemini Flash Lite", "Gemini 2.5 Flash-Lite"),
            ),
            h(
              "div",
              { class: "sb-note" },
              `${fmt.delta(pts[pts.length - 1].y - pts[0].y)} from ${pts[0].x} to ${pts[pts.length - 1].x}`,
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
            "aria-label": `${m}: Index by temperature`,
          });
          chart.append(svg);
          for (const t of ticks(lo, hi, 3)) {
            s("line", { class: "sb-gl", x1: mg.l, x2: W - mg.r, y1: Y(t), y2: Y(t) }, svg);
            s(
              "text",
              { class: "sb-t", x: mg.l - 4, y: Y(t) + 4, "text-anchor": "end", text: fmt.int(t) },
              svg,
            );
          }
          for (const t of ticks(tMin, tMax, 4))
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
        });
      }
    },
  });
}

// 5. Model consensus
const conc = Object.entries(d.concordance ?? {}).filter(
  (
    e,
  ): e is [
    string,
    {
      models: string[];
      matrix: (number | null)[][];
      mean_cross_model_jsd: number;
      mean_human_jsd: number;
    },
  ] => e[1].mean_cross_model_jsd != null && e[1].mean_human_jsd != null,
);
if (conc.length) {
  const pct = (b: { mean_cross_model_jsd: number; mean_human_jsd: number }) =>
    Math.round((1 - b.mean_cross_model_jsd / b.mean_human_jsd) * 100);
  const best = conc.reduce((p, q) => (pct(q[1]) > pct(p[1]) ? q : p));
  items.push({
    id: "consensus",
    short: "Model agreement",
    claim: "Models agree with each other more than they agree with people",
    confidence: [2, "Moderate"],
    number: `${pct(best[1])}%`,
    numberLabel: `lower divergence between models than between models and people (${dsLabel(best[0])})`,
    meaning:
      "Several models giving the same answer is not evidence that the answer is right. They share training data and make the same mistakes.",
    evidence:
      "Mean pairwise Jensen-Shannon divergence between raw LLM answer distributions, compared with the mean divergence between each model and people.",
    viz(el) {
      const vals = conc.flatMap(([, b]) => [b.mean_cross_model_jsd, b.mean_human_jsd]);
      dumbbell(
        el,
        conc.map(([id, b]) => ({
          name: dsLabel(id),
          a: b.mean_human_jsd,
          b: b.mean_cross_model_jsd,
          label: `${pct(b)}% lower`,
          tip: [
            ["Model vs. people", b.mean_human_jsd.toFixed(3)],
            ["Model vs. model", b.mean_cross_model_jsd.toFixed(3)],
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
      el.after(legend(swatch(ring), " model vs. people   ", swatch(solid), " model vs. model"));
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
  items.push({
    id: "voice",
    short: "Default voice",
    claim: "A model's default answers already resemble some groups more than others",
    confidence: [2, "Moderate"],
    number: `${(hiP.p_cond / loP.p_cond).toFixed(1)}×`,
    numberLabel: `as much adjustment needed to answer like a ${hiP.group} as like a ${loP.group}`,
    meaning:
      "Synthetic samples lean toward the model's default respondent. Check accuracy for each subgroup before reporting splits.",
    evidence: `Althing persona on SubPOP. The party gap is larger than run-to-run noise (${hiP.n_replications} runs). Education points the same way but with fewer runs. The income gap is within noise.`,
    viz(el) {
      const rows = attrs
        .map((a) => {
          const pair = cr.filter((r) => r.attribute === a).sort((p, q) => q.p_cond - p.p_cond);
          if (pair.length !== 2) return null;
          const [p, q] = pair;
          return {
            name: `${ATTR[a] ?? a}: ${q.group} vs. ${p.group}`,
            a: q.p_cond,
            b: p.p_cond,
            label: `${(p.p_cond / q.p_cond).toFixed(1)}×`,
            tip: [
              [q.group, `${q.p_cond.toFixed(3)} (${q.n_replications} runs)`],
              [p.group, `${p.p_cond.toFixed(3)} (${p.n_replications} runs)`],
            ] as [string, string][],
          };
        })
        .filter((r): r is NonNullable<typeof r> => r != null);
      dumbbell(el, rows, {
        domain: [0, Math.ceil(Math.max(...rows.map((r) => r.b)) * 50) / 50],
        axis: "How far the persona must shift answers toward the group (P_cond)",
        tick: (v) => v.toFixed(2),
        labelW: 230,
        a: ring,
        b: solid,
      });
      el.after(legend("Higher means the group is further from the model's default answers."));
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
  };
  items.push({
    id: "dont-know",
    short: "“Don't know”",
    claim:
      "On sensitive questions, a safety-tuned model picks “don't know” far more often than people do",
    confidence: [1, "Early"],
    number: `${(stt.mean_model_nonresponse_mass / stt.mean_human_nonresponse_mass).toFixed(1)}×`,
    numberLabel: `the human rate of nonresponse answers (${stt.provider}, ${dsLabel(stt.dataset)})`,
    meaning:
      "Report nonresponse separately for questions on religion, race, gender roles and welfare.",
    evidence:
      "The extra nonresponse is concentrated on religion, gender-role, race and welfare questions. The model picks a legitimate “don't know” option instead of refusing, so refusal-rate metrics miss it. This is one model on one dataset, so treat it as early evidence.",
    viz(el) {
      dumbbell(
        el,
        stt.items.map((it) => ({
          name: Q[it.key] ?? it.key,
          a: it.human_mass,
          b: it.model_mass,
          label: `${Math.round(it.model_mass * 100)}%`,
          tip: [
            ["People", `${Math.round(it.human_mass * 100)}%`],
            ["Model", `${Math.round(it.model_mass * 100)}%`],
          ],
        })),
        {
          domain: [0, 1],
          axis: "Share of answers that are a nonresponse option",
          tick: (v) => `${Math.round(v * 100)}%`,
          labelW: 250,
          a: ring,
          b: method("raw"),
        },
      );
      el.after(legend(swatch(ring), " people   ", swatch(method("raw")), " model"));
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
