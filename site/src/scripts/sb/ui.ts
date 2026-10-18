// Shared interactive pieces: tooltip, marks, filter controls, the inspector
// drawer and the compare tray.

import { PROVIDER_ICONS } from "@/lib/providerIcons";
import "@/scripts/segScroll";
import { harnessTag } from "@/lib/vocab";
import { axisTitle, css, fill, fmt, h, linear, s, thinTicks } from "./dom";
import {
  ALL,
  CORE,
  LAB_GLYPH,
  METHODS,
  type Scope,
  type ShownMethod,
  type SystemConfig,
  baseName,
  byKey,
  component,
  counterpart,
  data,
  dsLabel,
  dsMark,
  emit,
  fullName,
  onChange,
  profileHref,
  scopeName,
  scoreIn,
  shortName,
  shortWithMethod,
  state,
  tierOf,
} from "./model";

// ---------- Tooltip ----------
// Mouse: shows on hover, follows the pointer, hides on leave. Touch and pen
// have no hover (a tap fires enter and leave back to back), so a tap opens
// the tip and pins it until the next tap elsewhere, a scroll or Escape.
// Keyboard focus shows it only when the focus ring does (:focus-visible), so
// focus moved back to a mark by script doesn't leave a stray tip behind.
const tipEl = h("div", { class: "sb-tip", role: "tooltip" });
document.body.append(tipEl);
let pinned: Element | null = null;
/** True while restoreFocus() moves focus back to a mark: no tip for that. */
let quietFocus = false;
const isTouch = (e: Event): boolean =>
  "pointerType" in e && (e as PointerEvent).pointerType !== "mouse";
/** Focus that should show a tip: keyboard focus, not a click or a script. */
const showsFocus = (e: FocusEvent): boolean => {
  if (quietFocus) return false;
  try {
    return (e.target as Element).matches(":focus-visible");
  } catch {
    return true;
  }
};
export const tip = {
  show(e: MouseEvent | FocusEvent, title: string, rows: [string, string][]): void {
    tipEl.replaceChildren(
      h("div", { class: "sb-tip-t" }, title),
      ...rows.map(([k, v]) => h("div", { class: "sb-tip-r" }, h("span", null, k), h("b", null, v))),
    );
    tipEl.classList.add("on");
    tip.move(e);
  },
  move(e: MouseEvent | FocusEvent): void {
    let cx: number;
    let cy: number;
    if ("clientX" in e) {
      cx = e.clientX;
      cy = e.clientY;
    } else {
      const r = (e.target as Element).getBoundingClientRect();
      cx = r.right;
      cy = r.top;
    }
    const w = tipEl.offsetWidth;
    const hh = tipEl.offsetHeight;
    let x = cx + 14;
    let y = cy + 14;
    // A finger covers the spot below the tap: put the tip above it when it fits.
    if (pinned && cy - hh - 18 > 8) y = cy - hh - 18;
    if (x + w > innerWidth - 8) x = cx - w - 14;
    if (y + hh > innerHeight - 8) y = cy - hh - 12;
    tipEl.style.left = `${Math.max(8, x)}px`;
    tipEl.style.top = `${Math.max(8, y)}px`;
  },
  hide(): void {
    pinned = null;
    tipEl.classList.remove("on");
  },
  /** Open (or, on a second tap, close) a tip pinned to `node`. */
  pin(node: Element, e: MouseEvent, title: string, rows: [string, string][]): void {
    if (pinned === node) {
      tip.hide();
      return;
    }
    pinned = node;
    tip.show(e, title, rows);
  },
};
document.addEventListener(
  "pointerdown",
  (e) => {
    if (pinned && !pinned.contains(e.target as Node)) tip.hide();
  },
  true,
);
addEventListener(
  "scroll",
  () => {
    if (pinned) tip.hide();
  },
  { capture: true, passive: true },
);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && tipEl.classList.contains("on")) tip.hide();
});
/** Remembers whether the press that leads to a click was a finger or pen. */
let lastPress = "mouse";
document.addEventListener("pointerdown", (e) => {
  lastPress = e.pointerType;
});
const tapped = () => lastPress !== "mouse";

// ---------- Keyboard access to chart marks ----------
// A chart with clickable marks is one tab stop (role="group", so assistive
// tech can reach the marks inside, which role="img" hides). Arrow keys move
// between marks in rank order (highest score first), Home/End jump to the
// ends, Enter/Space open the details drawer.
const roving = new WeakMap<SVGSVGElement, { node: SVGElement; rank: number }[]>();
function addRover(svg: SVGSVGElement, node: SVGElement, rank: number): void {
  let marks = roving.get(svg);
  if (!marks) {
    const list: { node: SVGElement; rank: number }[] = [];
    marks = list;
    roving.set(svg, list);
    svg.setAttribute("role", "group");
    svg.addEventListener("keydown", (e) => {
      const i = list.findIndex((m) => m.node === e.target);
      if (i < 0) return;
      const j =
        e.key === "ArrowRight" || e.key === "ArrowDown"
          ? Math.min(list.length - 1, i + 1)
          : e.key === "ArrowLeft" || e.key === "ArrowUp"
            ? Math.max(0, i - 1)
            : e.key === "Home"
              ? 0
              : e.key === "End"
                ? list.length - 1
                : -1;
      if (j < 0) return;
      e.preventDefault();
      list[i].node.setAttribute("tabindex", "-1");
      list[j].node.setAttribute("tabindex", "0");
      (list[j].node as SVGElement & HTMLOrSVGElement).focus();
    });
    // Charts draw synchronously; order the marks once drawing is done.
    queueMicrotask(() => {
      list.sort((a, b) => b.rank - a.rank);
      list.forEach((m, k) => m.node.setAttribute("tabindex", k ? "-1" : "0"));
      const label = (svg.getAttribute("aria-label") ?? "Chart").replace(/\.\s*$/, "");
      svg.setAttribute(
        "aria-label",
        `${label}. ${list.length} marks, highest score first; use the arrow keys to move between them.`,
      );
    });
  }
  marks.push({ node, rank });
}

/** Hover/focus shows a tooltip and highlights the mark; click opens the inspector. */
export function interactive(
  node: SVGElement,
  c: SystemConfig,
  rows: () => [string, string][],
  svg?: SVGSVGElement,
): void {
  node.setAttribute("tabindex", "0");
  node.setAttribute("role", "button");
  // Name carries the numbers so screen-reader users get what the tooltip shows.
  node.setAttribute(
    "aria-label",
    `${fullName(c)}: ${rows()
      .map(([k, v]) => `${k} ${v}`)
      .join(", ")}. Open details.`,
  );
  if (svg) addRover(svg, node, scoreIn(c)?.v ?? Number.NEGATIVE_INFINITY);
  const enter = (e: MouseEvent | FocusEvent) => {
    tip.show(e, fullName(c), rows());
    if (svg) highlight(svg, c.key);
  };
  // Touch: no hover tip at all. A tap selects the mark and opens the details
  // drawer, which shows everything the tip would, so nothing is left over it.
  node.addEventListener("pointerenter", (e) => {
    if (!isTouch(e)) enter(e);
  });
  node.addEventListener("focus", (e) => {
    if (showsFocus(e)) enter(e);
  });
  node.addEventListener("pointermove", (e) => {
    if (!isTouch(e)) tip.move(e);
  });
  const leave = () => {
    tip.hide();
    if (svg) highlight(svg, null);
  };
  node.addEventListener("pointerleave", (e) => {
    if (!isTouch(e)) leave();
  });
  node.addEventListener("blur", leave);
  node.addEventListener("click", () => {
    tip.hide();
    inspect(c.key);
  });
  node.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      inspect(c.key);
    }
  });
}

/**
 * Plain tooltip for marks that aren't systems (reference points, findings):
 * hover or keyboard focus, or a tap on touch screens (pinned until the next
 * tap elsewhere).
 */
export function hoverInfo(node: SVGElement, title: string, rows: [string, string][]): void {
  node.addEventListener("pointerenter", (e) => {
    if (!isTouch(e)) tip.show(e, title, rows);
  });
  node.addEventListener("pointermove", (e) => {
    if (!isTouch(e) && !pinned) tip.move(e);
  });
  node.addEventListener("pointerleave", (e) => {
    if (!isTouch(e) && !pinned) tip.hide();
  });
  node.addEventListener("click", (e) => {
    if (tapped()) tip.pin(node, e, title, rows);
  });
  node.addEventListener("focus", (e) => {
    if (showsFocus(e)) tip.show(e, title, rows);
  });
  node.addEventListener("blur", () => {
    if (!pinned) tip.hide();
  });
}

let focused: string | null = null;
export function highlight(svg: SVGSVGElement, key: string | null): void {
  const keys = [key, focused].filter(Boolean);
  svg.classList.toggle("sb-dim", keys.length > 0);
  // data-k2: a second system the mark belongs to (e.g. an ensemble-to-member link).
  for (const n of svg.querySelectorAll<SVGElement>(".sb-s"))
    n.classList.toggle(
      "hl",
      keys.includes(n.dataset.k ?? "") || (!!n.dataset.k2 && keys.includes(n.dataset.k2)),
    );
}

// ---------- Marks ----------
export const methodColor = (m: SystemConfig["method"]): string =>
  css(METHODS[m as ShownMethod]?.color ?? "--sb-muted");

/** Raw = hollow circle, persona = filled circle, ensemble = diamond. */
export function marker(
  g: Element,
  method: SystemConfig["method"],
  x: number,
  y: number,
  r = 4.5,
): SVGElement {
  const col = methodColor(method);
  const ring = css("--sb-panel");
  if (method === "ensemble") {
    const d = r * 1.35;
    return s(
      "path",
      {
        d: `M${x},${y - d}L${x + d},${y}L${x},${y + d}L${x - d},${y}Z`,
        fill: col,
        stroke: ring,
        "stroke-width": 1.5,
      },
      g,
    );
  }
  if (method === "raw")
    return s("circle", { cx: x, cy: y, r, fill: ring, stroke: col, "stroke-width": 2 }, g);
  return s("circle", { cx: x, cy: y, r: r + 0.5, fill: col, stroke: ring, "stroke-width": 1.5 }, g);
}

/** Lab logo drawn into an SVG chart, 14px, top-left at (x, y - 11). */
export function glyphSvg(g: Element, lab: string, x: number, y: number): void {
  const paths = PROVIDER_ICONS[lab];
  if (!paths) {
    s(
      "rect",
      { x, y: y - 11, width: 14, height: 14, rx: 3, fill: "none", stroke: css("--sb-line-2") },
      g,
    );
    s(
      "text",
      {
        x: x + 7,
        y: y - 0.5,
        "text-anchor": "middle",
        class: "sb-glyph-t",
        text: LAB_GLYPH[lab] ?? "·",
      },
      g,
    );
    return;
  }
  const icon = s(
    "svg",
    { x, y: y - 11, width: 14, height: 14, viewBox: "0 0 24 24", class: "sb-logo" },
    g,
  );
  s("title", { text: lab }, icon);
  for (const p of paths) s("path", { d: p.d, fill: p.fill ?? "currentColor" }, icon);
}
/** "via codex" tag for systems run through an agent CLI, or null. */
export function harnessChip(c: SystemConfig): HTMLElement | null {
  return c.harness
    ? h(
        "span",
        { class: "sb-tag", title: `Run through the ${c.harness} CLI` },
        harnessTag(c.harness),
      )
    : null;
}
/** Lab logo for HTML (tables, chips, drawer); falls back to a lettered box. */
export function glyph(lab: string): HTMLElement {
  const paths = PROVIDER_ICONS[lab];
  if (!paths)
    return h(
      "span",
      { class: "sb-glyph", title: lab, "aria-hidden": "true" },
      LAB_GLYPH[lab] ?? "·",
    );
  const icon = s(
    "svg",
    { viewBox: "0 0 24 24", width: 15, height: 15, "aria-hidden": "true" },
    undefined,
  );
  for (const p of paths) s("path", { d: p.d, fill: p.fill ?? "currentColor" }, icon);
  return h("span", { class: "sb-logo-h", title: lab }, icon);
}
export const methodKey = (m: SystemConfig["method"]): HTMLElement =>
  h("span", { class: `sb-mk ${m}`, "aria-hidden": "true" });

// ---------- Filter controls ----------

// Every single-select segmented control on these pages is a
// role="radiogroup" of role="radio" buttons (or a role="tablist" of tabs).
// Implement the APG keyboard pattern once for all of them: one tab stop per
// group (the checked option), arrows move and select, Home/End jump. Pages
// rebuild these controls on every state change, so the tab stops are kept in
// step by a MutationObserver rather than at each call site.
const GROUP = '[role="radiogroup"], [role="tablist"]';
const OPTION = '[role="radio"], [role="tab"]';
const isOn = (b: Element) =>
  b.getAttribute("aria-checked") === "true" || b.getAttribute("aria-selected") === "true";
function syncGroup(g: Element): void {
  const opts = [...g.querySelectorAll<HTMLElement>(OPTION)];
  const on = opts.find(isOn) ?? opts[0];
  for (const o of opts) {
    const t = o === on ? "0" : "-1";
    if (o.getAttribute("tabindex") !== t) o.setAttribute("tabindex", t);
  }
}
const syncAll = () => {
  for (const g of document.querySelectorAll(GROUP)) syncGroup(g);
};
new MutationObserver(syncAll).observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ["aria-checked", "aria-selected"],
});
document.addEventListener("keydown", (e) => {
  const opt = (e.target as Element | null)?.closest?.(OPTION);
  const g = opt?.closest(GROUP);
  if (!opt || !g) return;
  const opts = [...g.querySelectorAll<HTMLElement>(OPTION)];
  const i = opts.indexOf(opt as HTMLElement);
  const j =
    e.key === "ArrowRight" || e.key === "ArrowDown"
      ? (i + 1) % opts.length
      : e.key === "ArrowLeft" || e.key === "ArrowUp"
        ? (i - 1 + opts.length) % opts.length
        : e.key === "Home"
          ? 0
          : e.key === "End"
            ? opts.length - 1
            : -1;
  if (j < 0) return;
  e.preventDefault();
  // Selection follows focus. The click usually re-renders the group, so find
  // it again by position and focus the newly checked option.
  const gi = [...document.querySelectorAll(GROUP)].indexOf(g);
  opts[j].click();
  const again = document.querySelectorAll(GROUP)[gi];
  const next = again ? [...again.querySelectorAll<HTMLElement>(OPTION)][j] : opts[j];
  if (again) syncGroup(again);
  next?.focus();
});

/** Segmented scope control: Index or a single dataset. */
export function scopeControl(): HTMLElement {
  const wrap = h("div", { class: "sb-seg", role: "radiogroup", "aria-label": "Score shown" });
  // Datasets no system has results on yet (e.g. NTIA) get no tab until they do.
  const scored = (id: string) => id === state.scope || data().systems.some((c) => c.ds[id]);
  const opts: [Scope, string][] = [
    ["all", "Index"],
    ...data()
      .datasets.filter((d) => scored(d.id))
      .map((d): [Scope, string] => [d.id, `${d.label}${d.ceilingAssumed ? " †" : ""}`]),
  ];
  const render = () =>
    wrap.replaceChildren(
      ...opts.map(([id, label]) =>
        h(
          "button",
          {
            type: "button",
            role: "radio",
            "aria-checked": state.scope === id ? "true" : "false",
            class: state.scope === id ? "on" : null,
            title: id === "all" ? `Average of ${CORE.map(dsLabel).join(", ")}` : dsLabel(id),
            onclick: () => {
              state.scope = id;
              emit();
            },
          },
          label,
        ),
      ),
    );
  onChange(render);
  render();
  return h("div", { class: "sb-filter" }, h("span", { class: "sb-lbl" }, "Score"), wrap);
}

export interface ToggleSet {
  all: string[];
  on: Set<string>;
  label: (id: string) => string;
  icon?: (id: string) => Node | null;
  note?: (id: string) => string | null;
}
/**
 * Toggle chips with explicit on/off state. Click toggles one; double-click
 * shows only that one; "All" restores everything.
 */
export type Rerenderable = HTMLElement & { rerender: () => void };
export function toggleChips(title: string, set: ToggleSet, changed: () => void): Rerenderable {
  const wrap = h("div", { class: "sb-filter" });
  const render = () => {
    const allOn = set.all.every((id) => set.on.has(id));
    wrap.replaceChildren(
      h("span", { class: "sb-lbl" }, title),
      h(
        "div",
        { class: "sb-chips" },
        ...set.all.map((id) => {
          const on = set.on.has(id);
          const chip = h(
            "button",
            {
              type: "button",
              class: `sb-chip${on ? " on" : ""}`,
              "aria-pressed": on ? "true" : "false",
              title: `Click to ${on ? "hide" : "show"}. Double-click to show only this.`,
            },
            h("span", { class: "sb-check", "aria-hidden": "true" }),
            set.icon?.(id) ?? null,
            set.label(id),
            set.note?.(id) ? h("span", { class: "sb-chip-note" }, set.note(id)) : null,
          );
          let timer: number | undefined;
          chip.addEventListener("click", () => {
            window.clearTimeout(timer);
            timer = window.setTimeout(() => {
              if (on) set.on.delete(id);
              else set.on.add(id);
              changed();
            }, 180);
          });
          chip.addEventListener("dblclick", () => {
            window.clearTimeout(timer);
            set.on.clear();
            set.on.add(id);
            changed();
          });
          return chip;
        }),
        allOn
          ? null
          : h(
              "button",
              {
                type: "button",
                class: "sb-linkbtn",
                onclick: () => {
                  for (const id of set.all) set.on.add(id);
                  changed();
                },
              },
              "Show all",
            ),
      ),
    );
  };
  render();
  return Object.assign(wrap, { rerender: render });
}

/** "Showing 7 of 10 systems · Reset filters" readout. */
export function filterStatus(
  count: () => [number, number],
  isDefault: () => boolean,
  reset: () => void,
): Rerenderable {
  const el = h("div", { class: "sb-status", "aria-live": "polite" });
  const render = () => {
    const [shown, total] = count();
    fill(
      el,
      h("span", null, `Showing ${shown} of ${total} systems`),
      isDefault()
        ? null
        : h("button", { type: "button", class: "sb-linkbtn", onclick: reset }, "Reset filters"),
    );
  };
  render();
  return Object.assign(el, { rerender: render });
}

// ---------- Compare tray ----------
const LETTERS = ["A", "B", "C"];
export const letter = (i: number): HTMLElement => h("span", { class: "sb-letter" }, LETTERS[i]);
const tray = h("div", { class: "sb-tray", role: "region", "aria-label": "Compare selection" });
document.body.append(tray);
export function toggleCompare(key: string): void {
  state.compare = state.compare.includes(key)
    ? state.compare.filter((k) => k !== key)
    : [...state.compare, key].slice(-3);
  emit();
}
function renderTray(): void {
  tray.classList.toggle("on", state.compare.length > 0);
  fill(
    tray,
    h("span", { class: "sb-lbl" }, "Compare"),
    ...state.compare.map((k, i) => {
      const c = byKey(k);
      if (!c) return null;
      return h(
        "span",
        { class: "sb-tray-chip" },
        letter(i),
        shortWithMethod(c),
        h(
          "button",
          {
            type: "button",
            "aria-label": `Remove ${shortName(c)}`,
            onclick: () => toggleCompare(k),
          },
          "×",
        ),
      );
    }),
    state.compare.length > 1
      ? h(
          "button",
          { type: "button", class: "sb-tray-go", onclick: () => openCompare() },
          "Compare",
        )
      : h("span", { class: "sb-tray-hint" }, "Select one more system"),
    h(
      "button",
      {
        type: "button",
        class: "sb-tray-clear",
        onclick: () => {
          state.compare = [];
          emit();
        },
      },
      "Clear",
    ),
  );
}
onChange(renderTray);

// ---------- Inspector drawer ----------
// A modal dialog: focus moves in on open, Tab cycles inside, Escape or the
// close button closes it and focus returns to whatever opened it.
const drawer = h("aside", {
  class: "sb-drawer",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "sb-drawer-title",
  tabindex: "-1",
});
document.body.append(drawer);
tray.before(drawer);
let mode: "one" | "compare" | null = null;
// The opener is often re-rendered while the drawer is open (charts and table
// rows redraw on every state change), so remember how to find it again.
let opener: { el: HTMLElement | SVGElement; label: string | null; id: string } | null = null;
function rememberOpener(): void {
  if (drawer.classList.contains("on")) return;
  const el = document.activeElement as HTMLElement | SVGElement | null;
  opener =
    el && el !== document.body && !drawer.contains(el)
      ? { el, label: el.getAttribute("aria-label"), id: el.id }
      : null;
}
function restoreFocus(): void {
  if (!opener) return;
  const { el, label, id } = opener;
  opener = null;
  const byId = id ? document.getElementById(id) : null;
  const byLabel = label
    ? [...document.querySelectorAll<HTMLElement>("[aria-label]")].find(
        (n) => n.getAttribute("aria-label") === label,
      )
    : undefined;
  const target = el.isConnected ? el : (byId ?? byLabel);
  // Focus goes back for keyboard users; it shouldn't reopen the mark's tooltip.
  quietFocus = true;
  target?.focus();
  quietFocus = false;
}
const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';
function close(): void {
  focused = null;
  mode = null;
  drawer.classList.remove("on");
  emit();
  restoreFocus();
}
document.addEventListener("keydown", (e) => {
  if (!drawer.classList.contains("on")) return;
  if (e.key === "Escape") {
    e.preventDefault();
    close();
    return;
  }
  if (e.key !== "Tab") return;
  const items = [...drawer.querySelectorAll<HTMLElement>(FOCUSABLE)].filter(
    (n) => n.getClientRects().length > 0,
  );
  if (!items.length) {
    e.preventDefault();
    drawer.focus();
    return;
  }
  const first = items[0];
  const last = items[items.length - 1];
  const active = document.activeElement;
  if (!drawer.contains(active)) {
    e.preventDefault();
    first.focus();
  } else if (e.shiftKey && (active === first || active === drawer)) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && active === last) {
    e.preventDefault();
    first.focus();
  }
});
export function inspect(key: string): void {
  rememberOpener();
  focused = key;
  mode = "one";
  renderDrawer();
  drawer.classList.add("on");
  drawer.focus();
  emit();
}
export function openCompare(): void {
  rememberOpener();
  focused = null;
  mode = "compare";
  renderDrawer();
  drawer.classList.add("on");
  drawer.focus();
  emit();
}
onChange(() => {
  if (drawer.classList.contains("on")) renderDrawer();
});

/** Per-dataset dot + interval rows, on a shared Index axis. */
export function datasetDots(list: SystemConfig[], width = 392, letters = false): SVGSVGElement {
  const ids = ALL.filter((id) => list.some((c) => c.ds[id]));
  const rowH = letters ? 16 + list.length * 12 : 26;
  const labelW = 112;
  const H = ids.length * rowH + 40;
  const x = linear(-40, 60, labelW + 8, width - 30);
  const svg = s("svg", {
    class: "sb-c",
    width,
    height: H,
    role: "img",
    "aria-label": "Index by dataset",
  });
  const plotB = H - 40;
  s(
    "rect",
    { x: x(-40), y: 0, width: x(0) - x(-40), height: plotB, fill: "var(--sb-zone-neg)" },
    svg,
  );
  for (const t of thinTicks([-40, -20, 0, 20, 40, 60], x, fmt.int)) {
    s("line", { class: "sb-gl", x1: x(t), x2: x(t), y1: 0, y2: plotB }, svg);
    s(
      "text",
      { class: "sb-t", x: x(t), y: plotB + 14, "text-anchor": "middle", text: fmt.int(t) },
      svg,
    );
  }
  s("line", { x1: x(0), x2: x(0), y1: 0, y2: plotB, stroke: css("--sb-ink-2") }, svg);
  axisTitle(svg, "SynthBench Index (0 = random answers)", { x: (x(-40) + x(60)) / 2, y: H - 4 });
  ids.forEach((id, r) => {
    const y0 = r * rowH;
    s(
      "text",
      {
        x: labelW,
        y: y0 + rowH / 2 + 4,
        "text-anchor": "end",
        class: "sb-lab sb-light",
        text: `${dsLabel(id)}${dsMark(id)}`,
      },
      svg,
    );
    list.forEach((c, i) => {
      const d = c.ds[id];
      if (!d) return;
      const cy = letters ? y0 + 10 + i * 12 : y0 + rowH / 2;
      const cl = (v: number) => Math.max(-40, Math.min(60, v));
      if (d.lo != null && d.hi != null)
        s(
          "line",
          {
            x1: x(cl(d.lo)),
            x2: x(cl(d.hi)),
            y1: cy,
            y2: cy,
            stroke: letters ? css("--sb-ink-2") : methodColor(c.method),
            "stroke-width": 1.6,
            opacity: 0.6,
          },
          svg,
        );
      if (letters) {
        s("circle", { cx: x(cl(d.idx)), cy, r: 6, fill: css("--sb-ink") }, svg);
        s(
          "text",
          {
            x: x(cl(d.idx)),
            y: cy + 3.5,
            "text-anchor": "middle",
            class: "sb-letter-t",
            text: LETTERS[i],
          },
          svg,
        );
      } else {
        marker(svg, c.method, x(cl(d.idx)), cy, 4.5);
        s(
          "text",
          { x: width - 2, y: cy + 4, "text-anchor": "end", class: "sb-val", text: fmt.int(d.idx) },
          svg,
        );
      }
    });
  });
  return svg;
}

/** Shares / order / refusal bars against the random-answers tick. */
export function componentBars(c: SystemConfig, width = 392): SVGSVGElement {
  const rows: ["pDist" | "pRank" | "pRefuse", string][] = [
    ["pDist", "Shares match"],
    ["pRank", "Order match"],
    ["pRefuse", "Refusal match"],
  ];
  const random = data().references.random;
  const H = rows.length * 26 + 36;
  const x = linear(0.4, 1, 112, width - 50);
  const svg = s("svg", {
    class: "sb-c",
    width,
    height: H,
    role: "img",
    "aria-label": "Score components",
  });
  rows.forEach(([k, label], i) => {
    const cy = i * 26 + 13;
    const v = component(c, k);
    const r = component(random, k);
    s(
      "text",
      { x: 104, y: cy + 4, "text-anchor": "end", class: "sb-lab sb-light", text: label },
      svg,
    );
    s(
      "rect",
      { x: x(0.4), y: cy - 3, width: x(1) - x(0.4), height: 6, rx: 3, fill: css("--sb-grid") },
      svg,
    );
    if (v != null)
      s(
        "rect",
        {
          x: x(0.4),
          y: cy - 3,
          width: x(Math.max(0.4, v)) - x(0.4),
          height: 6,
          rx: 3,
          fill: methodColor(c.method),
        },
        svg,
      );
    if (r != null)
      s(
        "line",
        {
          x1: x(r),
          x2: x(r),
          y1: cy - 8,
          y2: cy + 8,
          stroke: css("--sb-neg-ink"),
          "stroke-width": 2,
        },
        svg,
      );
    s(
      "text",
      { x: width - 2, y: cy + 4, "text-anchor": "end", class: "sb-val", text: fmt.three(v) },
      svg,
    );
  });
  const axisY = rows.length * 26 + 2;
  for (const t of thinTicks([0.4, 0.6, 0.8, 1], x, (v) => v.toFixed(1)))
    s(
      "text",
      { class: "sb-t", x: x(t), y: axisY + 10, "text-anchor": "middle", text: t.toFixed(1) },
      svg,
    );
  axisTitle(svg, "Component score, 0 to 1, not Index points (red tick = random answers)", {
    x: (x(0.4) + x(1)) / 2,
    y: H - 2,
  });
  return svg;
}

/** Where a value sits between random (0) and people (100). */
function positionStrip(
  v: { v: number; lo: number | null; hi: number | null },
  width = 392,
): SVGSVGElement {
  const x = linear(-40, 100, 6, width - 6);
  const svg = s("svg", {
    class: "sb-c",
    width,
    height: 36,
    role: "img",
    "aria-label": "Position between random answers and people",
  });
  s("rect", { x: x(-40), y: 8, width: x(0) - x(-40), height: 8, fill: "var(--sb-zone-neg)" }, svg);
  s("rect", { x: x(0), y: 8, width: x(100) - x(0), height: 8, fill: css("--sb-grid") }, svg);
  if (v.lo != null && v.hi != null)
    s(
      "rect",
      {
        x: x(Math.max(-40, v.lo)),
        y: 8,
        width: x(Math.min(100, v.hi)) - x(Math.max(-40, v.lo)),
        height: 8,
        fill: css("--sb-ink-2"),
        opacity: 0.35,
      },
      svg,
    );
  s(
    "line",
    { x1: x(v.v), x2: x(v.v), y1: 3, y2: 21, stroke: css("--sb-ink"), "stroke-width": 2.5 },
    svg,
  );
  s("text", { class: "sb-t", x: x(0), y: 33, "text-anchor": "middle", text: "0 random" }, svg);
  s("text", { class: "sb-t", x: x(100), y: 33, "text-anchor": "end", text: "100 people" }, svg);
  return svg;
}

/**
 * Hand-off from the Index-level compare to /compare's question-level diff:
 * one link per pair and dataset where both systems have a published config
 * (only the current dataset when the scope is one dataset).
 */
function questionDiffLinks(list: SystemConfig[], pairs: [number, number][]): HTMLElement | null {
  const ids = state.scope === "all" ? [...ALL] : [state.scope];
  const rows = pairs
    .filter(([a, b]) => list[a] && list[b])
    .map(([a, b]) => {
      const links = ids.flatMap((id) => {
        const ca = list[a].ds[id]?.configId;
        const cb = list[b].ds[id]?.configId;
        if (!ca || !cb) return [];
        const href = `${data().base}compare/?a=${encodeURIComponent(ca)}&b=${encodeURIComponent(cb)}&mode=config`;
        return [h("a", { href, style: { textDecoration: "underline" } }, dsLabel(id))];
      });
      if (!links.length) return null;
      return h(
        "div",
        { class: "sb-pair" },
        h("div", { class: "sb-pair-h" }, letter(a), "vs", letter(b)),
        h(
          "p",
          { class: "sb-note", style: { display: "flex", flexWrap: "wrap", gap: "4px 12px" } },
          ...links,
        ),
      );
    })
    .filter((r): r is HTMLDivElement => r != null);
  if (!rows.length) return null;
  return h(
    "div",
    { class: "sb-ds" },
    h("h3", null, "Per-question diff →"),
    h("p", { class: "sb-note" }, "Where the answers differ, question by question, on one dataset."),
    ...rows,
  );
}

function verdicts(a: SystemConfig, b: SystemConfig, ia: number, ib: number): HTMLElement[] {
  const out: HTMLElement[] = [];
  for (const id of ALL) {
    const x = a.ds[id];
    const y = b.ds[id];
    if (!x || !y || x.lo == null || x.hi == null || y.lo == null || y.hi == null) continue;
    if (x.lo > y.hi)
      out.push(
        h(
          "li",
          null,
          h("b", null, `${LETTERS[ia]} is higher`),
          ` on ${dsLabel(id)} by ${Math.round(x.idx - y.idx)}`,
        ),
      );
    else if (y.lo > x.hi)
      out.push(
        h(
          "li",
          null,
          h("b", null, `${LETTERS[ib]} is higher`),
          ` on ${dsLabel(id)} by ${Math.round(y.idx - x.idx)}`,
        ),
      );
    else
      out.push(
        h(
          "li",
          null,
          h("b", null, "No clear difference"),
          ` on ${dsLabel(id)} (intervals overlap)`,
        ),
      );
  }
  return out;
}

function renderDrawer(): void {
  drawer.replaceChildren();
  const x = h(
    "button",
    { type: "button", class: "sb-x", "aria-label": "Close", onclick: close },
    "×",
  );
  if (mode === "compare") {
    const list = state.compare.map(byKey).filter((c): c is SystemConfig => !!c);
    type Row = [
      string,
      (c: SystemConfig) => number | null,
      (v: number | null) => string,
      "high" | "low" | null,
    ];
    const rows: Row[] = [
      ["Index", (c) => scoreIn(c)?.v ?? null, fmt.one, "high"],
      ["Tier", (c) => tierOf(c)?.tier ?? null, (v) => (v == null ? "—" : String(v)), "low"],
      ...ALL.map((id): Row => [dsLabel(id), (c) => c.ds[id]?.idx ?? null, fmt.int, "high"]),
      ["Shares match", (c) => component(c, "pDist"), fmt.three, "high"],
      ["Order match", (c) => component(c, "pRank"), fmt.three, "high"],
      ["Refusal match", (c) => component(c, "pRefuse"), fmt.three, "high"],
      ["Cost per 100 questions", (c) => c.cost100, fmt.usd, "low"],
      ["Holdout flags", (c) => c.flagged, (v) => (v ? `⚠ ${v}` : "none"), null],
    ];
    const table = h(
      "table",
      { class: "sb-cmpt" },
      h(
        "tr",
        null,
        h("th", null, ""),
        list.map((_, i) => h("th", null, letter(i))),
      ),
    );
    for (const [k, get, f, better] of rows) {
      const vals = list.map(get);
      const nums = vals.filter((v): v is number => typeof v === "number");
      const best =
        better && nums.length > 1
          ? better === "high"
            ? Math.max(...nums)
            : Math.min(...nums)
          : null;
      table.append(
        h(
          "tr",
          null,
          h("td", null, k),
          vals.map((v) => h("td", { class: best != null && v === best ? "best" : null }, f(v))),
        ),
      );
    }
    const pairs: [number, number][] = [
      [0, 1],
      [0, 2],
      [1, 2],
    ];
    drawer.append(
      h(
        "div",
        { class: "sb-dh" },
        h(
          "div",
          null,
          h("div", { class: "sb-kicker" }, `Comparing ${list.length} · ${scopeName()}`),
          h("h2", { class: "sb-dttl", id: "sb-drawer-title" }, "Side by side"),
        ),
        x,
      ),
      h(
        "div",
        { class: "sb-ds" },
        list.map((c, i) =>
          h(
            "div",
            { class: "sb-cmp-who" },
            letter(i),
            glyph(c.lab),
            h("b", null, baseName(c)),
            h("span", { class: "sb-tag" }, METHODS[c.method as ShownMethod].short),
            harnessChip(c),
          ),
        ),
      ),
      h(
        "div",
        { class: "sb-ds" },
        h("h3", null, "Scores"),
        table,
        h("p", { class: "sb-note" }, "▲ marks the best value in each row."),
      ),
      h("div", { class: "sb-ds" }, h("h3", null, "Index by dataset"), datasetDots(list, 392, true)),
      h(
        "div",
        { class: "sb-ds" },
        h("h3", null, "Are the differences real?"),
        h("p", { class: "sb-note" }, "Based on whether the 95% intervals overlap."),
        ...pairs
          .filter(([a, b]) => list[a] && list[b])
          .map(([a, b]) =>
            h(
              "div",
              { class: "sb-pair" },
              h("div", { class: "sb-pair-h" }, letter(a), "vs", letter(b)),
              h("ul", null, verdicts(list[a], list[b], a, b)),
            ),
          ),
      ),
      ...[questionDiffLinks(list, pairs)].filter((el): el is HTMLElement => el != null),
    );
    return;
  }
  const c = focused ? byKey(focused) : undefined;
  if (!c) return;
  const v = scoreIn(c);
  const tr = tierOf(c);
  const cp = counterpart(c);
  const inCmp = state.compare.includes(c.key);
  const spq = [
    ...new Set(
      Object.values(c.ds)
        .map((d) => d.samplesPerQuestion)
        .filter(Boolean),
    ),
  ].join(" / ");
  let personaRow: HTMLElement | null = null;
  if (cp) {
    const rawC = c.method === "raw" ? c : cp;
    const altC = c.method === "raw" ? cp : c;
    const a = scoreIn(rawC);
    const b = scoreIn(altC);
    personaRow = h(
      "div",
      { class: "sb-ds" },
      h("h3", null, "Raw prompt vs. Althing persona"),
      a && b
        ? h(
            "div",
            { class: "sb-persona" },
            h("span", { class: "sb-mono" }, `raw ${fmt.int(a.v)} → persona ${fmt.int(b.v)}`),
            h("b", { class: `sb-mono ${b.v >= a.v ? "sb-up" : "sb-down"}` }, fmt.delta(b.v - a.v)),
            h(
              "button",
              { type: "button", class: "sb-btn sb-btn-sm", onclick: () => inspect(cp.key) },
              `View ${METHODS[cp.method as ShownMethod].short}`,
            ),
          )
        : h("p", { class: "sb-note" }, "Not available for this score."),
    );
  }
  fill(
    drawer,
    h(
      "div",
      { class: "sb-dh" },
      glyph(c.lab),
      h(
        "div",
        null,
        h("h2", { class: "sb-dttl", id: "sb-drawer-title" }, baseName(c)),
        h(
          "div",
          { class: "sb-dsub" },
          methodKey(c.method),
          `${METHODS[c.method as ShownMethod].label}: ${METHODS[c.method as ShownMethod].desc}`,
          c.variant ? h("span", { class: "sb-tag" }, c.variant) : null,
          harnessChip(c),
        ),
      ),
      x,
    ),
    h(
      "div",
      { class: "sb-ds" },
      h("h3", null, scopeName()),
      h(
        "div",
        { class: "sb-big-row" },
        h("div", { class: "sb-big" }, v ? fmt.int(v.v) : "—"),
        h(
          "div",
          { class: "sb-note" },
          v?.lo != null
            ? `95% interval ${fmt.int(v.lo)} to ${fmt.int(v.hi)}`
            : "Not scored on every core dataset",
          h("br"),
          tr?.tier != null
            ? `Tier ${tr.tier}${tr.tied > 1 ? `, tied with ${tr.tied - 1} other${tr.tied > 2 ? "s" : ""}` : ", alone"}`
            : "",
        ),
      ),
      v ? positionStrip(v) : null,
    ),
    h("div", { class: "sb-ds" }, h("h3", null, "By dataset"), datasetDots([c])),
    h("div", { class: "sb-ds" }, h("h3", null, "Score components"), componentBars(c)),
    personaRow,
    h(
      "div",
      { class: "sb-ds" },
      h("h3", null, "Checks and provenance"),
      h(
        "dl",
        { class: "sb-kv" },
        h("dt", null, "Holdout check"),
        h(
          "dd",
          null,
          c.flagged
            ? h(
                "span",
                { class: "sb-warn" },
                `⚠ Gap above the review threshold on ${c.flagged} dataset${c.flagged > 1 ? "s" : ""}`,
              )
            : h("span", { class: "sb-ok" }, "✓ Within the review threshold everywhere"),
        ),
        h("dt", null, "Replicate runs"),
        h("dd", null, String(c.runs)),
        h("dt", null, "Samples per question"),
        h("dd", null, spq || "—"),
        h("dt", null, "Cost per 100 questions"),
        h("dd", null, c.cost100 == null ? "not recorded" : fmt.usd(c.cost100)),
      ),
    ),
    h(
      "div",
      { class: "sb-ds sb-actions" },
      h(
        "button",
        {
          type: "button",
          class: `sb-btn${inCmp ? "" : " sb-btn-dark"}`,
          onclick: () => {
            toggleCompare(c.key);
            renderDrawer();
          },
        },
        inCmp ? "Remove from compare" : "Add to compare",
      ),
      h("a", { class: "sb-btn", href: profileHref(c) }, "Full profile"),
    ),
  );
}

// ---------- Horizontal scroll affordance ----------
/**
 * Marks a horizontal scroller with `data-more="right|left|both"` (CSS fades
 * the clipped edge) and shows a "scroll for more" hint above it while
 * there are columns out of view. Safe to call more than once.
 */
export function scrollHint(wrap: HTMLElement, what = "columns"): void {
  if (wrap.dataset.hint) return;
  wrap.dataset.hint = "1";
  const hint = h(
    "div",
    { class: "sb-scrollhint", "aria-hidden": "true", hidden: true },
    `Scroll sideways for more ${what}`,
    h("span", null, " →"),
  );
  wrap.before(hint);
  const update = () => {
    const max = wrap.scrollWidth - wrap.clientWidth;
    const left = wrap.scrollLeft > 2;
    const right = max > 2 && wrap.scrollLeft < max - 2;
    const more = left && right ? "both" : right ? "right" : left ? "left" : "";
    if (more) wrap.dataset.more = more;
    else delete wrap.dataset.more;
    hint.hidden = max <= 2;
    // Keyboard users need a tab stop to scroll a region with nothing focusable in it.
    if (max > 2 && !wrap.querySelector("a[href],button,input,select,[tabindex]")) {
      wrap.tabIndex = 0;
      wrap.setAttribute("role", "region");
      if (!wrap.hasAttribute("aria-label"))
        wrap.setAttribute(
          "aria-label",
          wrap.querySelector("caption")?.textContent?.trim() || "Scrollable table",
        );
    }
  };
  wrap.addEventListener("scroll", update, { passive: true });
  const ro = new ResizeObserver(update);
  ro.observe(wrap);
  new MutationObserver(() => {
    for (const kid of wrap.children) ro.observe(kid);
    update();
  }).observe(wrap, { childList: true, subtree: true });
  for (const kid of wrap.children) ro.observe(kid);
  update();
}

/** Wire up shared chrome once per page. Call after page controls exist. */
export function initShell(): void {
  for (const w of document.querySelectorAll<HTMLElement>(".sb-tablewrap")) scrollHint(w);
  renderTray();
  const p = new URLSearchParams(location.search);
  const cmp = p.get("compare");
  const insp = p.get("inspect");
  if (cmp) {
    state.compare = cmp
      .split(",")
      .filter((k) => byKey(k))
      .slice(0, 3);
    emit();
    if (state.compare.length > 1) {
      drawer.style.transition = "none";
      openCompare();
      requestAnimationFrame(() => {
        drawer.style.transition = "";
      });
    }
  } else if (insp && byKey(insp)) {
    drawer.style.transition = "none";
    inspect(insp);
    requestAnimationFrame(() => {
      drawer.style.transition = "";
    });
  }
}

export const CORE_IDS = CORE;

// ---------- URL-backed filter state ----------

/** Read a comma-separated set from the query string, keeping only known ids. */
export function readSet(param: string, known: string[], fallback: string[]): Set<string> {
  const raw = new URLSearchParams(location.search).get(param);
  if (raw == null) return new Set(fallback);
  return new Set(raw.split(",").filter((id) => known.includes(id)));
}

/** Update query params in place (null removes one) without adding history entries. */
export function writeParams(values: Record<string, string | null>): void {
  const u = new URL(location.href);
  for (const [k, v] of Object.entries(values)) {
    if (v == null) u.searchParams.delete(k);
    else u.searchParams.set(k, v);
  }
  history.replaceState(null, "", u);
}

/** Query value for a set: null when it equals the default, so clean URLs stay clean. */
export function setParam(on: Set<string>, defaults: string[]): string | null {
  const same = on.size === defaults.length && defaults.every((id) => on.has(id));
  return same ? null : [...on].join(",");
}

export const METHOD_IDS = Object.keys(METHODS) as ShownMethod[];

/** Method chips (raw / persona / ensemble) bound to `on`. */
export function methodChips(on: Set<string>, changed: () => void): Rerenderable {
  return toggleChips(
    "Method",
    {
      all: METHOD_IDS,
      on,
      label: (m) => METHODS[m as ShownMethod].label,
      icon: (m) => methodKey(m as ShownMethod),
    },
    changed,
  );
}

/** Keep the scope param in the URL in step with state.scope. */
onChange(() => writeParams({ scope: state.scope === "all" ? null : state.scope }));

// ---------- Default density: top N with a "Show all" toggle ----------

/** Capping that would hide only a few rows isn't worth a click: show them all. */
const capWorthIt = (total: number, limit: number): boolean => total > limit + 3;
/** The first `limit` rows unless `all` is set or capping would hide three or fewer. */
export const capRows = <T>(rows: T[], limit: number, all: boolean): T[] =>
  all || !capWorthIt(rows.length, limit) ? rows : rows.slice(0, limit);
/**
 * "Showing the top 10 of 33 · Show all 33" under a capped chart or list.
 * Returns null when nothing would be hidden.
 */
export function showAllToggle(o: {
  total: number;
  limit: number;
  all: boolean;
  onToggle: () => void;
  noun?: string;
  shownText?: string;
  lessText?: string;
}): HTMLElement | null {
  if (!capWorthIt(o.total, o.limit)) return null;
  const noun = o.noun ?? "systems";
  return h(
    "div",
    { class: "sb-showall" },
    h(
      "span",
      null,
      o.all
        ? `Showing all ${o.total} ${noun}`
        : (o.shownText ?? `Showing the top ${o.limit} of ${o.total} ${noun}`),
    ),
    h(
      "button",
      {
        type: "button",
        class: "sb-linkbtn",
        "aria-expanded": o.all ? "true" : "false",
        onclick: o.onToggle,
      },
      o.all ? (o.lessText ?? `Show the top ${o.limit} only`) : `Show all ${o.total}`,
    ),
  );
}

// ---------- Takeaways ----------
const openTakes = new Set<string>();
type TakeKid = Node | string | null | undefined | false;
/**
 * Chart findings: the first one in full, the rest folded behind a toggle that
 * stays open across re-renders.
 */
export function takeaways(el: HTMLElement, items: (string | TakeKid[])[]): void {
  const kids = items.map((it) => (Array.isArray(it) ? it : [it]));
  if (!kids.length) {
    fill(el);
    return;
  }
  const more = kids.slice(1);
  const det = more.length
    ? h(
        "details",
        { class: "sb-more", open: openTakes.has(el.id) ? true : null },
        h("summary", null, `${more.length} more finding${more.length === 1 ? "" : "s"}`),
        h(
          "ul",
          null,
          more.map((k) => h("li", null, ...k)),
        ),
      )
    : null;
  det?.addEventListener("toggle", () => {
    if ((det as HTMLDetailsElement).open) openTakes.add(el.id);
    else openTakes.delete(el.id);
  });
  fill(el, h("p", { class: "sb-take1" }, ...kids[0]), det);
}
