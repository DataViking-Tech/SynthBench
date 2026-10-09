import { axisTitle, css, fmt, h, linear, mount, s } from "../dom";
import { type SystemConfig, data, fullName, pruneCompare, systems } from "../model";
import { hoverInfo, initShell, marker, methodColor } from "../ui";

pruneCompare();
const d = data();
const $ = (id: string) => document.getElementById(id) as HTMLElement;

// ---------- Worked example: one question ----------
const OPTIONS = ["A great deal", "A fair amount", "Not too much", "None at all", "Refused"];
const PEOPLE = [0.07, 0.29, 0.38, 0.23, 0.03];
const UNIFORM = OPTIONS.map(() => 1 / OPTIONS.length);
const mode = PEOPLE.indexOf(Math.max(...PEOPLE));
const ONE_HOT = OPTIONS.map((_, i) => (i === mode ? 1 : 0));
const lerp = (a: number[], b: number[], t: number) => a.map((v, i) => v + (b[i] - v) * t);
// Slider 0 → uniform, 0.5 → matches people, 1 → everything on the most common answer.
const panel = (t: number) =>
  t <= 0.5 ? lerp(UNIFORM, PEOPLE, t / 0.5) : lerp(PEOPLE, ONE_HOT, (t - 0.5) / 0.5);
const log2 = (x: number) => Math.log(x) / Math.LN2;
const kl = (p: number[], q: number[]) =>
  p.reduce((a, pi, i) => (pi > 0 ? a + pi * log2(pi / q[i]) : a), 0);
const jsd = (p: number[], q: number[]) => {
  const m = p.map((v, i) => (v + q[i]) / 2);
  return (kl(p, m) + kl(q, m)) / 2;
};
const tauB = (x: number[], y: number[]) => {
  let c = 0;
  let dd = 0;
  let tx = 0;
  let ty = 0;
  for (let i = 0; i < x.length; i++)
    for (let j = i + 1; j < x.length; j++) {
      const a = Math.sign(x[i] - x[j]);
      const b = Math.sign(y[i] - y[j]);
      if (!a && !b) continue;
      if (!a) tx++;
      else if (!b) ty++;
      else if (a === b) c++;
      else dd++;
    }
  const den = Math.sqrt((c + dd + tx) * (c + dd + ty));
  return den ? (c - dd) / den : 0;
};
const score = (p: number[]) => {
  const pd = 1 - jsd(p, PEOPLE);
  const pr = (1 + tauB(p.slice(0, 4), PEOPLE.slice(0, 4))) / 2;
  const pf = 1 - Math.abs(p[4] - PEOPLE[4]);
  return { pd, pr, pf, sps: (pd + pr + pf) / 3 };
};
const RANDOM = score(UNIFORM);
let current = panel(0.8);

const swatchBar = h("span", { class: "sb-sw-bar", style: { background: methodColor("althing") } });
$("mt-legend").append(
  h("span", { class: "sb-sw-tick" }),
  " real people   ",
  swatchBar,
  " synthetic panel",
);

const distEl = $("mt-dist");
const drawDist = mount(distEl, (W) => {
  const rowH = 30;
  const labelW = 112;
  const plotB = OPTIONS.length * rowH;
  const H = plotB + 40;
  const x = linear(0, 1, labelW + 10, W - 44);
  const svg = s("svg", {
    class: "sb-c",
    width: W,
    height: H,
    role: "img",
    "aria-label": "Answer shares: real people vs. synthetic panel",
  });
  distEl.append(svg);
  for (const t of [0, 0.25, 0.5, 0.75, 1]) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 14, "text-anchor": "middle", text: `${t * 100}%` },
      svg,
    );
  }
  axisTitle(svg, "Share of respondents choosing each answer", { x: (x(0) + x(1)) / 2, y: H - 4 });
  OPTIONS.forEach((o, i) => {
    const cy = i * rowH + rowH / 2;
    s(
      "text",
      { x: labelW, y: cy + 4, "text-anchor": "end", class: "sb-lab sb-light", text: o },
      svg,
    );
    s(
      "rect",
      {
        x: x(0),
        y: cy - 6,
        width: Math.max(1, x(current[i]) - x(0)),
        height: 12,
        rx: 2,
        fill: methodColor("althing"),
      },
      svg,
    );
    s(
      "line",
      {
        x1: x(PEOPLE[i]),
        x2: x(PEOPLE[i]),
        y1: cy - 10,
        y2: cy + 10,
        stroke: css("--sb-ink"),
        "stroke-width": 2.5,
      },
      svg,
    );
    s(
      "text",
      {
        x: Math.max(x(current[i]), x(PEOPLE[i])) + 6,
        y: cy + 4,
        class: "sb-val",
        text: `${Math.round(current[i] * 100)}%`,
      },
      svg,
    );
  });
});

const slider = $("mt-slider") as HTMLInputElement;
function update(): void {
  const t = Number(slider.value) / 100;
  current = panel(t);
  drawDist();
  const sc = score(current);
  const row = (k: string, sub: string, v: number, r: number) => [
    h("div", { class: "k" }, k, h("small", null, sub)),
    h("div", { class: "v" }, v.toFixed(3), h("small", null, `random ${r.toFixed(3)}`)),
  ];
  $("mt-scores").replaceChildren(
    ...row("Shares match", "1 − Jensen-Shannon divergence", sc.pd, RANDOM.pd),
    ...row("Order match", "(1 + Kendall τ) ÷ 2", sc.pr, RANDOM.pr),
    ...row("Refusal match", "1 − |refusal rate gap|", sc.pf, RANDOM.pf),
    h("div", { class: "k tot" }, "SPS (mean of the three)"),
    h("div", { class: "v tot" }, sc.sps.toFixed(3)),
  );
  $("mt-big").textContent = fmt.int((100 * (sc.sps - RANDOM.sps)) / (1 - RANDOM.sps));
  $("mt-note").textContent =
    t < 0.12
      ? "Random answers score 0 by definition."
      : t < 0.42
        ? "The shares lean the right way but are still too even."
        : t <= 0.58
          ? "The panel matches people: shares, order and refusals all line up."
          : "Over-confident: the order is still right but too many answers go to the most common option. Most raw LLMs fail this way.";
}
slider.addEventListener("input", update);
update();

// ---------- Why an Index: SPS vs. Index on OpinionsQA ----------
const oq = d.datasets.find((x) => x.id === "opinionsqa");
const pool = systems().filter((c) => !c.variant && c.ds.opinionsqa);
const whyEl = $("mt-why");
if (oq && pool.length) {
  mount(whyEl, (W) => {
    const H = 210;
    const labelW = 150;
    const svg = s("svg", {
      class: "sb-c",
      width: W,
      height: H,
      role: "img",
      "aria-label": "Systems on the raw SPS scale and on the Index scale",
    });
    whyEl.append(svg);
    const scales = [
      {
        cy: 46,
        title: "Raw SPS",
        sub: "0 to 1",
        x: linear(0, 1, labelW, W - 16),
        get: (c: SystemConfig) => c.ds.opinionsqa.sps,
        ticks: [0, 0.25, 0.5, 0.75, 1],
        tf: (v: number) => v.toFixed(2),
        random: oq.random,
      },
      {
        cy: 146,
        title: "SynthBench Index",
        sub: "0 = random, 100 = people",
        x: linear(-40, 100, labelW, W - 16),
        get: (c: SystemConfig) => c.ds.opinionsqa.idx,
        ticks: [-40, -20, 0, 20, 40, 60, 80, 100],
        tf: fmt.int,
        random: 0,
      },
    ];
    for (const sc of scales) {
      s(
        "text",
        { x: labelW - 14, y: sc.cy, "text-anchor": "end", class: "sb-lab", text: sc.title },
        svg,
      );
      s(
        "text",
        { x: labelW - 14, y: sc.cy + 15, "text-anchor": "end", class: "sb-sub", text: sc.sub },
        svg,
      );
      s(
        "line",
        {
          x1: sc.x(sc.ticks[0]),
          x2: sc.x(sc.ticks[sc.ticks.length - 1]),
          y1: sc.cy,
          y2: sc.cy,
          stroke: css("--sb-line-2"),
        },
        svg,
      );
      for (const v of sc.ticks)
        s(
          "text",
          { class: "sb-t", x: sc.x(v), y: sc.cy + 30, "text-anchor": "middle", text: sc.tf(v) },
          svg,
        );
      s(
        "line",
        {
          x1: sc.x(sc.random),
          x2: sc.x(sc.random),
          y1: sc.cy - 16,
          y2: sc.cy + 16,
          stroke: css("--sb-ink"),
          "stroke-width": 1.5,
        },
        svg,
      );
      s(
        "text",
        {
          class: "sb-sub",
          x: sc.x(sc.random),
          y: sc.cy - 20,
          "text-anchor": "middle",
          text: "random answers",
        },
        svg,
      );
      for (const c of pool) {
        const v = sc.get(c);
        const g = s("g", null, svg);
        marker(g, c.method, sc.x(v), sc.cy, 5);
        hoverInfo(s("circle", { class: "sb-hit", cx: sc.x(v), cy: sc.cy, r: 9 }, g), fullName(c), [
          ["Raw SPS", c.ds.opinionsqa.sps.toFixed(3)],
          ["Index", fmt.one(c.ds.opinionsqa.idx)],
        ]);
      }
    }
  });
  const sps = pool.map((c) => c.ds.opinionsqa.sps);
  $("mt-why-note").textContent =
    `On raw SPS, every system lands between ${Math.min(...sps).toFixed(2)} and ${Math.max(...sps).toFixed(2)}, and random answers score ${oq.random.toFixed(2)}. A score like 0.81 looks like "81% of the way to human". The Index shows how little most systems beat random answers by, and how far all of them are from real people.`;
}

// ---------- Reference points ----------
$("mt-anchors").replaceChildren(
  h(
    "thead",
    null,
    h(
      "tr",
      null,
      [
        "Dataset",
        "Population",
        "Questions",
        "0 = random SPS",
        "Majority answer SPS (Index)",
        "100 = ceiling SPS",
        "Ceiling quality",
      ].map((t, i) => h("th", { scope: "col", class: i >= 2 && i <= 5 ? "r" : null }, t)),
    ),
  ),
  h(
    "tbody",
    null,
    d.datasets.map((x) =>
      h(
        "tr",
        null,
        h("td", { class: "sb-strong" }, `${x.label}${x.ceilingAssumed ? " †" : ""}`),
        h("td", { class: "sb-muted" }, x.population),
        h("td", { class: "r sb-mono" }, x.questions.toLocaleString("en-US")),
        h("td", { class: "r sb-mono" }, x.random.toFixed(3)),
        h(
          "td",
          { class: "r sb-mono" },
          x.majority != null ? `${x.majority.toFixed(3)} (${fmt.int(x.majorityIdx)})` : "—",
        ),
        h("td", { class: "r sb-mono" }, x.ceiling != null ? x.ceiling.toFixed(4) : "1.0, assumed"),
        h(
          "td",
          null,
          x.ceilingAssumed
            ? h("span", { class: "sb-warn" }, "Not computed yet; left out of the Index")
            : (x.ceilingQuality ?? "—"),
        ),
      ),
    ),
  ),
);

initShell();
