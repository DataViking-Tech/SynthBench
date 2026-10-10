import { byDataset, costChart, ladder, sharesOrder } from "../charts";
import { h, mount } from "../dom";
import {
  type SystemConfig,
  emit,
  onChange,
  pruneCompare,
  scopeName,
  shortName,
  state,
  systems,
} from "../model";
import {
  METHOD_IDS,
  filterStatus,
  glyph,
  initShell,
  methodChips,
  readSet,
  scopeControl,
  setParam,
  takeaways,
  toggleChips,
  writeParams,
} from "../ui";

pruneCompare();
const q = new URLSearchParams(location.search);

type View = "shares" | "ladder" | "datasets" | "cost";
const VIEWS: { id: View; title: string; desc: string; sub: () => string; howto: string }[] = [
  {
    id: "shares",
    title: "Shares vs. order",
    desc: "Why most systems sit near random",
    sub: () => `${scopeName()}. Up and to the right is better.`,
    howto:
      "Each mark is one system: hollow circles are raw prompts, filled circles are Althing personas, the diamond is the ensemble. Arrows join the same base model before and after adding a persona. Systems in the shaded corner score below random answers, assuming equal refusal match.",
  },
  {
    id: "ladder",
    title: "Raw, persona, ensemble",
    desc: "What each layer adds",
    sub: () => `${scopeName()}. Each line is one base model.`,
    howto:
      "Left column: each base model prompted directly. Middle: the same model with an Althing persona, with the change from the raw prompt next to it. Right: the ensemble, which averages three persona systems; green lines connect it to its members. A red line means the persona lowered the score.",
  },
  {
    id: "datasets",
    title: "By dataset",
    desc: "Where systems break down",
    sub: () =>
      "Index on each core dataset. The Score setting doesn't apply here because every dataset is shown.",
    howto:
      "Each line is one system across the three core datasets, ordered from US adults to cross-national questions. Points in the shaded band score below random answers on that dataset.",
  },
  {
    id: "cost",
    title: "Cost vs. Index",
    desc: "What you get per dollar",
    sub: () =>
      `${scopeName()} against the cost of answering 100 questions. Up and to the left is better.`,
    howto:
      "Each system is placed by what it cost to answer 100 questions and by its score. Vertical bars are 95% intervals. Cost is only recorded for raw LLM runs so far.",
  },
];

// Systems are filtered by base model ("family"); partial-coverage families start hidden.
interface Family {
  id: string;
  c: SystemConfig;
  full: boolean;
}
const families: Family[] = [];
for (const c of systems().filter((x) => !x.variant)) {
  const f = families.find((x) => x.id === c.baseId);
  if (f) f.full ||= c.coverage === 3;
  else families.push({ id: c.baseId, c, full: c.coverage === 3 });
}
const FAMILY_IDS = families.map((f) => f.id);
const DEFAULT_FAMILIES = families.filter((f) => f.full).map((f) => f.id);

const st = {
  view: (VIEWS.some((v) => v.id === q.get("view")) ? q.get("view") : "shares") as View,
  methods: readSet("methods", METHOD_IDS, METHOD_IDS),
  families: readSet("systems", FAMILY_IDS, DEFAULT_FAMILIES),
  withRefs: q.get("refs") === "1",
  log: q.get("scale") !== "linear",
};
const pool = () =>
  systems().filter((c) => !c.variant && st.methods.has(c.method) && st.families.has(c.baseId));
const isDefault = () =>
  state.scope === "all" &&
  setParam(st.methods, METHOD_IDS) == null &&
  setParam(st.families, DEFAULT_FAMILIES) == null;
const changed = () => {
  writeParams({
    view: st.view === "shares" ? null : st.view,
    methods: setParam(st.methods, METHOD_IDS),
    systems: setParam(st.families, DEFAULT_FAMILIES),
    refs: st.withRefs ? "1" : null,
    scale: st.log ? null : "linear",
  });
  emit();
};
const reset = () => {
  state.scope = "all";
  for (const m of METHOD_IDS) st.methods.add(m);
  st.families.clear();
  for (const id of DEFAULT_FAMILIES) st.families.add(id);
  changed();
};

// ---------- Controls ----------
const $ = (id: string) => document.getElementById(id) as HTMLElement;
const famChips = toggleChips(
  "Systems",
  {
    all: FAMILY_IDS,
    on: st.families,
    label: (id) => {
      const f = families.find((x) => x.id === id) as Family;
      return f.id === "ensemble" ? "Ensemble" : shortName(f.c);
    },
    icon: (id) => glyph((families.find((x) => x.id === id) as Family).c.lab),
    note: (id) => ((families.find((x) => x.id === id) as Family).full ? null : "partial"),
  },
  changed,
);
const mChips = methodChips(st.methods, changed);
const status = filterStatus(
  () => [pool().length, systems().filter((c) => !c.variant).length],
  isDefault,
  reset,
);
$("an-filters").append(scopeControl(), mChips, famChips, status);

function renderViews(): void {
  $("an-views").replaceChildren(
    ...VIEWS.map((v) =>
      h(
        "button",
        {
          type: "button",
          role: "tab",
          "aria-selected": st.view === v.id ? "true" : "false",
          class: st.view === v.id ? "on" : null,
          onclick: () => {
            st.view = v.id;
            changed();
          },
        },
        h("b", null, v.title),
        h("span", null, v.desc),
      ),
    ),
  );
  const seg = (
    opts: [boolean, string][],
    get: () => boolean,
    set: (b: boolean) => void,
    label: string,
  ) =>
    h(
      "div",
      { class: "sb-filter" },
      h("span", { class: "sb-lbl" }, label),
      h(
        "div",
        { class: "sb-seg", role: "radiogroup", "aria-label": label },
        opts.map(([val, text]) =>
          h(
            "button",
            {
              type: "button",
              role: "radio",
              "aria-checked": get() === val ? "true" : "false",
              class: get() === val ? "on" : null,
              onclick: () => {
                set(val);
                changed();
              },
            },
            text,
          ),
        ),
      ),
    );
  $("an-opts").replaceChildren(
    ...(st.view === "shares"
      ? [
          seg(
            [
              [false, "Systems only"],
              [true, "Include references"],
            ],
            () => st.withRefs,
            (b) => {
              st.withRefs = b;
            },
            "Zoom",
          ),
        ]
      : st.view === "cost"
        ? [
            seg(
              [
                [true, "Log"],
                [false, "Linear"],
              ],
              () => st.log,
              (b) => {
                st.log = b;
              },
              "Cost axis",
            ),
          ]
        : []),
  );
  const v = VIEWS.find((x) => x.id === st.view) ?? VIEWS[0];
  $("an-title").textContent = v.title;
  $("an-sub").textContent = v.sub();
  $("an-howto").textContent = v.howto;
}
onChange(() => {
  renderViews();
  mChips.rerender();
  famChips.rerender();
  status.rerender();
});
renderViews();

// ---------- Chart ----------
const chartEl = $("an-chart");
mount(
  chartEl,
  (W) => {
    const list = pool();
    let notes: string[] = [];
    if (st.view === "shares") notes = sharesOrder(chartEl, W, list, !st.withRefs);
    else if (st.view === "ladder") notes = ladder(chartEl, W, list);
    else if (st.view === "datasets") notes = byDataset(chartEl, W, list);
    else notes = costChart(chartEl, W, list, st.log);
    if (!list.length)
      chartEl.append(
        h(
          "p",
          { class: "sb-empty" },
          h("button", { type: "button", class: "sb-linkbtn", onclick: reset }, "Reset filters"),
        ),
      );
    takeaways($("an-notice"), notes);
  },
  onChange,
);

initShell();
