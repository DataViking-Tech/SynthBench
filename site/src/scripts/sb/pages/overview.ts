import { gapChart, liftMini, whyMini } from "../charts";
import { fmt, h, heat, mount } from "../dom";
import {
  CORE,
  type SystemConfig,
  data,
  dsLabel,
  emit,
  fullName,
  onChange,
  pruneCompare,
  rankedPool,
  scopeName,
  scoreIn,
  shortName,
  state,
  tiers,
} from "../model";
import {
  METHOD_IDS,
  filterStatus,
  initShell,
  methodChips,
  methodKey,
  readSet,
  scopeControl,
  setParam,
  takeaways,
  writeParams,
} from "../ui";

pruneCompare();
const d = data();
const methods = readSet("methods", METHOD_IDS, METHOD_IDS);
const visible = (c: SystemConfig) => methods.has(c.method);
const $ = (id: string) => document.getElementById(id) as HTMLElement;

// ---------- Filters ----------
const changed = () => {
  writeParams({ methods: setParam(methods, METHOD_IDS) });
  emit();
};
const reset = () => {
  state.scope = "all";
  for (const m of METHOD_IDS) methods.add(m);
  changed();
};
const chips = methodChips(methods, changed);
const status = filterStatus(
  () => [tiers(rankedPool().filter(visible)).length, tiers(rankedPool()).length],
  () => state.scope === "all" && methods.size === METHOD_IDS.length,
  reset,
);
$("ov-filters").append(scopeControl(), chips, status);
onChange(() => {
  chips.rerender();
  status.rerender();
});

// ---------- Lede (fixed: all methods, headline Index) ----------
{
  const ranked = tiers(rankedPool(), "all");
  const best = ranked[0];
  const raws = ranked
    .filter((r) => r.c.method === "raw")
    .map((r) => r.v.v)
    .sort((a, b) => a - b);
  const median = raws.length ? raws[Math.floor(raws.length / 2)] : null;
  const goqa = rankedPool().filter((c) => c.method === "raw" && c.ds.globalopinionqa);
  const below = goqa.filter((c) => c.ds.globalopinionqa.idx < 0).length;
  $("ov-lede").replaceChildren(
    "The ",
    h("b", null, "SynthBench Index"),
    " puts every system on one scale. 0 is what random answers score. 100 is how closely a second sample of real people matches the first. The top system, ",
    best ? fullName(best.c) : "—",
    ", scores ",
    h("span", { class: "n" }, fmt.int(best?.v.v)),
    ". The median raw LLM scores ",
    h("span", { class: "n" }, fmt.int(median)),
    `. On cross-national questions, ${below} of ${goqa.length} raw LLMs score below random.`,
  );
}

// ---------- The gap ----------
const gapEl = $("ov-gap");
mount(
  gapEl,
  (W) => {
    const rows = tiers(rankedPool().filter(visible));
    $("gap-q").textContent = `${scopeName()}. Every ranked system on one scale.`;
    if (!rows.length) {
      gapEl.append(
        h(
          "p",
          { class: "sb-empty" },
          "No systems match these filters. ",
          h("button", { type: "button", class: "sb-linkbtn", onclick: reset }, "Reset filters"),
        ),
      );
      takeaways($("ov-notice"), []);
      return;
    }
    gapChart(gapEl, W, rows);
    const tier1 = rows.filter((r) => r.tier === 1);
    const tier2 = rows.filter((r) => r.tier === 2);
    const raw = rows.filter((r) => r.c.method === "raw");
    const nearZero = raw.filter(
      (r) => r.v.lo != null && r.v.hi != null && r.v.lo <= 0 && r.v.hi >= 0,
    ).length;
    const top = rows[0].v.v;
    const spread = top - rows[rows.length - 1].v.v;
    const items: (string | Node)[][] = [];
    items.push(
      tier1.length === 1
        ? [
            h("b", null, fullName(tier1[0].c)),
            ` is the only system in tier 1.${tier2.length ? ` The next ${tier2.length} are tied in tier 2.` : ""}`,
          ]
        : [`${tier1.length} systems share tier 1.`],
    );
    if (raw.length)
      items.push([
        `${nearZero} of ${raw.length} raw LLMs have a 95% interval that includes 0, so they can't be told apart from random answers.`,
      ]);
    items.push([
      `The top score is ${fmt.int(top)}. The gap to real people (${fmt.int(100 - top)} points) is larger than the spread between all systems shown (${fmt.int(spread)} points).`,
    ]);
    takeaways($("ov-notice"), items);
  },
  onChange,
);

// ---------- By dataset (mini heat table) ----------
function miniHeat(): void {
  const rows = tiers(rankedPool().filter(visible), "all").slice(0, 6);
  const heads: Record<string, string> = {
    opinionsqa: "US adults",
    subpop: "US groups",
    globalopinionqa: "Global",
  };
  $("ov-heat").replaceChildren(
    h("caption", null, "SynthBench Index per dataset, top systems"),
    h(
      "thead",
      null,
      h(
        "tr",
        null,
        h("th", { scope: "col" }, "System"),
        CORE.map((id) => h("th", { scope: "col", title: dsLabel(id) }, heads[id])),
      ),
    ),
    h(
      "tbody",
      null,
      rows.map((r) =>
        h(
          "tr",
          null,
          h("td", { class: "n" }, methodKey(r.c.method), shortName(r.c)),
          CORE.map((id) => {
            const v = r.c.ds[id]?.idx;
            const { bg, fg } = heat(v);
            return h("td", { class: "c", style: { background: bg, color: fg } }, fmt.int(v));
          }),
        ),
      ),
    ),
  );
  const avg = (id: string) => {
    const v = rows.map((r) => r.c.ds[id]?.idx).filter((x): x is number => x != null);
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
  };
  $("ov-heat-take").textContent = rows.length
    ? `Average of these ${rows.length}: ${fmt.int(avg("opinionsqa"))} on US adults, ${fmt.int(avg("globalopinionqa"))} on cross-national questions.`
    : "No systems match these filters.";
}
onChange(miniHeat);
miniHeat();

// ---------- Persona effect ----------
$("ov-lift-legend").append(
  h("span", null, methodKey("raw"), "Raw prompt"),
  h("span", null, methodKey("althing"), "Althing persona"),
  h("span", { class: "sb-legend-r" }, "Change"),
);
// Raw and persona runs don't always use the same number of samples per question.
const samplesNote = (): string | null => {
  const pairs = rankedPool()
    .filter((c) => c.method === "althing")
    .map((p) => [rankedPool().find((r) => r.method === "raw" && r.baseId === p.baseId), p] as const)
    // Same pairs the chart draws: both scored in the current scope.
    .filter(
      (pair): pair is readonly [SystemConfig, SystemConfig] =>
        pair[0] != null && scoreIn(pair[0]) != null && scoreIn(pair[1]) != null,
    );
  const fewer = pairs.filter(([raw, persona]) =>
    CORE.some((id) => {
      const a = raw.ds[id]?.samplesPerQuestion;
      const b = persona.ds[id]?.samplesPerQuestion;
      return a != null && b != null && a < b;
    }),
  ).length;
  return fewer
    ? `For ${fewer} of these ${pairs.length} models, the raw runs used fewer samples per question than the persona runs on at least one dataset, which may overstate the gain.`
    : null;
};
const liftEl = $("ov-lift");
mount(
  liftEl,
  (W) => {
    const { up, total } = liftMini(liftEl, W);
    $("ov-lift-take").textContent = [
      `In this score, the persona raises ${up} of ${total} models.`,
      samplesNote(),
    ]
      .filter(Boolean)
      .join(" ");
  },
  onChange,
);

// ---------- Shares vs. order ----------
const whyEl = $("ov-why");
mount(whyEl, (W) => whyMini(whyEl, W), onChange);

// ---------- Findings ----------
{
  const idxOf = (id: string, sps: number) => {
    const m = d.datasets.find((x) => x.id === id);
    return m ? (100 * (sps - m.random)) / ((m.ceiling ?? 1) - m.random) : 0;
  };
  const items: [string, string, string][] = [];
  const ec = d.findings.ensemble_comparison ?? [];
  if (ec.length) {
    const lifts = ec.map(
      (e) => idxOf(e.dataset, e.ensemble_sps) - idxOf(e.dataset, e.best_single_sps),
    );
    items.push([
      `An ensemble of three persona systems beats the best single system on all ${ec.length} datasets tested`,
      `+${Math.round(Math.min(...lifts))} to +${Math.round(Math.max(...lifts))}`,
      "Index points over the best single system",
    ]);
  }
  const tpl = d.systems
    .filter((c) => c.variant?.startsWith("temperature 0.85") && c.ds.subpop)
    .map((c) => c.ds.subpop.idx);
  if (tpl.length > 1)
    items.push([
      "Changing only the persona prompt template can drop a system far below random",
      `${fmt.int(Math.max(...tpl) - Math.min(...tpl))} pts`,
      "range on SubPOP, same model and temperature",
    ]);
  const conc = Object.entries(d.concordance ?? {}).filter(
    ([, b]) => b.mean_cross_model_jsd != null && b.mean_human_jsd,
  );
  if (conc.length) {
    const [id, b] = conc.reduce((p, q) =>
      1 - (q[1].mean_cross_model_jsd as number) / (q[1].mean_human_jsd as number) >
      1 - (p[1].mean_cross_model_jsd as number) / (p[1].mean_human_jsd as number)
        ? q
        : p,
    );
    const pct = Math.round(
      (1 - (b.mean_cross_model_jsd as number) / (b.mean_human_jsd as number)) * 100,
    );
    items.push([
      "Models agree with each other more than they agree with people",
      `${pct}%`,
      `lower divergence between models than from people, on ${dsLabel(id)}`,
    ]);
  }
  $("ov-findings").replaceChildren(
    ...items.map(([claim, value, sub], i) =>
      h(
        "a",
        { class: "sb-fl-row", href: `${d.base}findings/` },
        h("span", { class: "i" }, String(i + 1).padStart(2, "0")),
        h("span", { class: "c" }, claim),
        h("span", { class: "v" }, value),
        h("span", { class: "s" }, sub),
      ),
    ),
  );
}

// ---------- Trust strip ----------
{
  const flagged = d.systems.reduce((a, c) => a + c.flagged, 0);
  $("ov-trust").replaceChildren(
    h(
      "div",
      null,
      h("b", null, "Recomputed from raw data"),
      "Every score is recomputed from the published per-question results with open-source code.",
    ),
    h(
      "div",
      null,
      h("b", null, "Private holdout"),
      `20 to 40% of each dataset is scored against an answer key we don't publish. ${flagged} result${flagged === 1 ? "" : "s"} with a public/private gap above 0.05 ${flagged === 1 ? "is" : "are"} flagged.`,
    ),
    h(
      "div",
      null,
      h("b", null, "Failed runs listed"),
      `${d.excludedRuns} runs failed validity checks. They are listed on the methodology page.`,
    ),
    h(
      "div",
      null,
      h("b", null, "Operator disclosure"),
      "SynthBench is run by DataViking, which also builds Althing. Every system goes through the same pipeline.",
    ),
  );
}

initShell();
