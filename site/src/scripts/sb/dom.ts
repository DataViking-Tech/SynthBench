// Small DOM + SVG + scale helpers shared by the Index pages. Text always goes
// in via textContent / text nodes, never innerHTML.

import { signed } from "@/lib/format";

type Attrs = Record<string, unknown>;
type Child = Node | string | number | null | undefined | false | Child[];

const SVG_NS = "http://www.w3.org/2000/svg";

function append(el: Element, kids: Child[]): void {
  for (const kid of kids) {
    if (kid == null || kid === false) continue;
    if (Array.isArray(kid)) append(el, kid);
    else el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
}

export function h<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  attrs: Attrs | null = null,
  ...kids: Child[]
): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs ?? {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = String(v);
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k.startsWith("on") && typeof v === "function")
      el.addEventListener(k.slice(2), v as EventListener);
    else el.setAttribute(k, v === true ? "" : String(v));
  }
  append(el, kids);
  return el;
}

/** Replace an element's children, skipping null / false entries like `h()` does. */
export function fill(el: Element, ...kids: Child[]): void {
  el.replaceChildren();
  append(el, kids);
}

export function s<K extends keyof SVGElementTagNameMap>(
  tag: K,
  attrs: Attrs | null,
  parent?: Element,
): SVGElementTagNameMap[K] {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs ?? {})) {
    if (v == null || v === false) continue;
    if (k === "text") el.textContent = String(v);
    else el.setAttribute(k, String(v));
  }
  // Chart roots are drawn in pixels at their container's width. A matching
  // viewBox lets CSS (`svg.sb-c[viewBox]`) scale them down instead of
  // overflowing when the container is narrower than the last layout.
  if (
    tag === "svg" &&
    attrs &&
    attrs.viewBox == null &&
    typeof attrs.width === "number" &&
    typeof attrs.height === "number"
  )
    el.setAttribute("viewBox", `0 0 ${attrs.width} ${attrs.height}`);
  if (parent) parent.appendChild(el);
  return el;
}

export const css = (name: string): string =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

export type Scale = (v: number) => number;

export const linear =
  (d0: number, d1: number, r0: number, r1: number): Scale =>
  (v) =>
    r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);

export const logScale = (d0: number, d1: number, r0: number, r1: number): Scale => {
  const l0 = Math.log10(d0);
  const l1 = Math.log10(d1);
  return (v) => r0 + ((Math.log10(v) - l0) / (l1 - l0)) * (r1 - r0);
};

export function ticks(a: number, b: number, n = 6): number[] {
  const raw = (b - a) / n;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((x) => (b - a) / x <= n) ?? 10 * mag;
  const out: number[] = [];
  for (let v = Math.ceil(a / step) * step; v <= b + 1e-9; v += step) out.push(+v.toFixed(8));
  return out;
}

const measureCtx = document.createElement("canvas").getContext("2d");
export function textWidth(t: string, size = 12.5, weight = 500, mono = false): number {
  if (!measureCtx) return t.length * size * 0.55;
  measureCtx.font = `${weight} ${size}px ${mono ? '"IBM Plex Mono"' : '"IBM Plex Sans"'}, system-ui, sans-serif`;
  return measureCtx.measureText(t).width;
}

/** Trim text with an ellipsis so it fits in `max` px. */
export function fitText(t: string, max: number, size = 12.5, weight = 500): string {
  if (textWidth(t, size, weight) <= max) return t;
  let out = t;
  while (out.length > 1 && textWidth(`${out}…`, size, weight) > max) out = out.slice(0, -1);
  return `${out.trimEnd()}…`;
}

// ---------- Axis tick density ----------
// Tick labels (.sb-t: 11px mono) need room on narrow charts, where a fixed
// list like -40…100 in steps of 20 ran together ("−806040200"). These keep
// only ticks whose labels clear their neighbours at the chart's actual
// scale, always keeping 0 and, where possible, the two ends.

/** Smallest centre-to-centre distance between two tick labels, in px. */
const MIN_TICK_GAP = 32;
const tickLabelW = (t: string) => textWidth(t, 11, 400, true);
function ticksFit(vals: number[], x: Scale, label: (v: number) => string, pad: number): boolean {
  for (let i = 1; i < vals.length; i++) {
    const room = Math.abs(x(vals[i]) - x(vals[i - 1]));
    const need = (tickLabelW(label(vals[i - 1])) + tickLabelW(label(vals[i]))) / 2 + pad;
    if (room < Math.max(need, MIN_TICK_GAP)) return false;
  }
  return true;
}

/**
 * Thin a list of tick values (sorted ascending) until their labels fit at
 * scale `x`: every k-th tick counting from 0 (or the first), plus the two
 * ends when they fit, dropping the tick next to an end to make room for it.
 * Returns the list unchanged when it already fits, so wide charts keep
 * every tick.
 */
export function thinTicks(
  values: number[],
  x: Scale,
  label: (v: number) => string = String,
  pad = 8,
): number[] {
  if (values.length < 3 || ticksFit(values, x, label, pad)) return values;
  const anchor = Math.max(0, values.indexOf(0));
  const fixed = values[anchor];
  for (let k = 2; k < values.length; k++) {
    let keep = values.filter((_, i) => (i - anchor) % k === 0);
    for (const end of [values[0], values[values.length - 1]]) {
      if (keep.includes(end)) continue;
      const trial = [...keep, end].sort((a, b) => a - b);
      // Make room by dropping the end's neighbour (never 0 / the anchor).
      while (!ticksFit(trial, x, label, pad) && trial.length > 2) {
        const i = trial.indexOf(end);
        const j = i === 0 ? 1 : i - 1;
        if (trial[j] === fixed) break;
        trial.splice(j, 1);
      }
      if (ticksFit(trial, x, label, pad)) keep = trial;
    }
    if (ticksFit(keep, x, label, pad)) return keep;
  }
  return [fixed];
}

/**
 * Nice ticks between a and b for a horizontal axis at scale `x`: up to `n`
 * of them, fewer (with a rounder step) when the labels wouldn't fit.
 */
export function axisTicks(
  a: number,
  b: number,
  x: Scale,
  label: (v: number) => string = String,
  n = 6,
): number[] {
  for (let k = n; k >= 2; k--) {
    const t = ticks(a, b, k);
    if (ticksFit(t, x, label, 8)) return t;
  }
  return thinTicks(ticks(a, b, 2), x, label);
}

const minus = (s: string) => s.replace("-", "−");
export const fmt = {
  int: (v: number | null | undefined) => (v == null ? "—" : minus(Math.round(v).toString())),
  one: (v: number | null | undefined) => (v == null ? "—" : minus(v.toFixed(1))),
  delta: (v: number | null | undefined) => signed(v),
  deltaOne: (v: number | null | undefined) => signed(v, 1),
  three: (v: number | null | undefined) => (v == null ? "—" : v.toFixed(3)),
  usd: (v: number | null | undefined) =>
    v == null ? "—" : v < 0.01 ? "<$0.01" : `$${v.toFixed(2)}`,
  date: (iso: string) =>
    new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
};

/**
 * Re-render `draw` whenever the element's width changes or `subscribe` fires.
 * Resizes are debounced; in between, the previous SVG scales via its viewBox.
 */
export function mount(
  el: HTMLElement,
  draw: (width: number) => void,
  subscribe?: (fn: () => void) => void,
): () => void {
  let last = 0;
  let timer: number | undefined;
  const run = () => {
    window.clearTimeout(timer);
    const w = Math.floor(el.clientWidth);
    if (!w) return;
    last = w;
    el.replaceChildren();
    draw(w);
  };
  new ResizeObserver(() => {
    if (Math.floor(el.clientWidth) === last) return;
    window.clearTimeout(timer);
    // First layout (or coming back from display:none) draws at once.
    if (!last) run();
    else timer = window.setTimeout(run, 120);
  }).observe(el);
  subscribe?.(run);
  run();
  // Label widths are measured with the webfont; redraw once it has loaded.
  document.fonts?.ready.then(() => {
    if (last) run();
  });
  return run;
}

export interface SpreadItem {
  y: number;
}
/** Nudge labels apart vertically (keeping order) so none overlap. */
export function spread<T extends SpreadItem>(
  items: T[],
  gap: number,
  top: number,
  bottom: number,
): T[] {
  const a = [...items].sort((p, q) => p.y - q.y);
  for (let i = 1; i < a.length; i++) if (a[i].y - a[i - 1].y < gap) a[i].y = a[i - 1].y + gap;
  const over = a.length ? a[a.length - 1].y - bottom : 0;
  if (over > 0) for (const it of a) it.y -= over;
  for (let i = a.length - 2; i >= 0; i--) if (a[i + 1].y - a[i].y < gap) a[i].y = a[i + 1].y - gap;
  if (a.length && a[0].y < top) {
    const d = top - a[0].y;
    for (const it of a) it.y += d;
  }
  return a;
}

export interface Placed {
  x: number;
  y: number;
  anchor: "start" | "middle" | "end";
}
type Box = [number, number, number, number];
/** Put a point label at the first candidate spot clear of labels, points and edges. */
export function placeLabel(
  px: number,
  py: number,
  w: number,
  placed: Box[],
  points: [number, number][],
  bounds: Box,
): Placed {
  return (
    tryPlaceLabel(px, py, w, placed, points, bounds) ??
    leastBadPlace(px, py, w, placed, points, bounds)
  );
}
const CANDS: [number, number, Placed["anchor"]][] = [
  [10, 4, "start"],
  [-10, 4, "end"],
  [0, -11, "middle"],
  [0, 19, "middle"],
  [9, -9, "start"],
  [-9, -9, "end"],
  [9, 17, "start"],
  [-9, 17, "end"],
];
const candBox = (px: number, py: number, w: number, [dx, dy, anchor]: (typeof CANDS)[number]) => {
  const x = px + dx;
  const y = py + dy;
  const x0 = anchor === "start" ? x : anchor === "end" ? x - w : x - w / 2;
  return { p: { x, y, anchor }, b: [x0 - 2, y - 11, x0 + w + 2, y + 3] as Box };
};
/**
 * When no spot is clear, take the candidate with the fewest collisions that
 * stays inside the plot (a label running off the edge is worse than an
 * overlap), instead of always putting it to the right of the point.
 */
function leastBadPlace(
  px: number,
  py: number,
  w: number,
  placed: Box[],
  points: [number, number][],
  bounds: Box,
): Placed {
  const cost = (b: Box) =>
    placed.filter((o) => !(b[2] < o[0] || b[0] > o[2] || b[3] < o[1] || b[1] > o[3])).length +
    points.filter(([qx, qy]) => qx > b[0] - 5 && qx < b[2] + 5 && qy > b[1] - 5 && qy < b[3] + 5)
      .length +
    (b[0] < bounds[0] || b[2] > bounds[2] || b[1] < bounds[1] || b[3] > bounds[3] ? 1000 : 0);
  let best = candBox(px, py, w, CANDS[0]);
  let bestCost = Number.POSITIVE_INFINITY;
  for (const c of CANDS) {
    const o = candBox(px, py, w, c);
    const k = cost(o.b);
    if (k < bestCost) {
      best = o;
      bestCost = k;
    }
  }
  placed.push(best.b);
  return best.p;
}
/** Like placeLabel, but returns null (and reserves nothing) when no spot is clear. */
export function tryPlaceLabel(
  px: number,
  py: number,
  w: number,
  placed: Box[],
  points: [number, number][],
  bounds: Box,
): Placed | null {
  const hits = (b: Box) =>
    placed.some((o) => !(b[2] < o[0] || b[0] > o[2] || b[3] < o[1] || b[1] > o[3])) ||
    points.some(([qx, qy]) => qx > b[0] - 5 && qx < b[2] + 5 && qy > b[1] - 5 && qy < b[3] + 5) ||
    b[0] < bounds[0] ||
    b[2] > bounds[2] ||
    b[1] < bounds[1] ||
    b[3] > bounds[3];
  for (const c of CANDS) {
    const o = candBox(px, py, w, c);
    if (!hits(o.b)) {
      placed.push(o.b);
      return o.p;
    }
  }
  return null;
}

/** Diverging fill around 0: blue above random, red below, neutral at 0. */
export function heat(v: number | null | undefined, max = 50): { bg: string; fg: string } {
  if (v == null) return { bg: "transparent", fg: css("--sb-muted") };
  const parse = (c: string) => [1, 3, 5].map((i) => Number.parseInt(c.slice(i, i + 2), 16));
  const mid = parse(css("--sb-heat-mid"));
  const end = parse(v >= 0 ? css("--sb-heat-pos") : css("--sb-heat-neg"));
  const t = Math.min(1, Math.abs(v) / max) ** 0.85 * 0.9;
  const rgb = mid.map((x, i) => Math.round(x + (end[i] - x) * t));
  // Pick whichever text colour contrasts more (WCAG relative luminance).
  // White on the mid-blue cells was only 3.1-3.6:1. Black rather than the ink
  // colour keeps even the worst-case cell (where the two are closest) at 4.5:1.
  const L = luminance(rgb);
  const dark = (L + 0.05) / 0.05;
  const light = 1.05 / (L + 0.05);
  return { bg: `rgb(${rgb.join(",")})`, fg: light > dark ? "#ffffff" : "#000000" };
}

/** WCAG 2 relative luminance of an sRGB colour given as 0-255 channels. */
export function luminance(rgb: number[]): number {
  const [r, g, b] = rgb.map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Make room below the chart: grow the SVG (and its viewBox) by `dy` px. */
function growSvg(svg: SVGSVGElement, dy: number): void {
  const w = Number(svg.getAttribute("width"));
  const hh = Number(svg.getAttribute("height")) + dy;
  svg.setAttribute("height", String(hh));
  if (svg.hasAttribute("viewBox")) svg.setAttribute("viewBox", `0 0 ${w} ${hh}`);
}

/**
 * Axis title: horizontal under the axis, or rotated along a vertical axis.
 * `sub` is a secondary note in muted text after the title, dropped when there
 * is no room for it. A centred horizontal title is kept inside the SVG: moved
 * in from the edge if it would run over, or wrapped onto a second line (the
 * SVG grows to fit) when it is wider than the chart.
 */
export function axisTitle(
  svg: SVGSVGElement,
  text: string,
  opts: {
    x: number;
    y: number;
    vertical?: boolean;
    anchor?: "start" | "middle" | "end";
    sub?: string;
  },
): SVGTextElement {
  const el = s(
    "text",
    {
      class: "sb-axis-title",
      x: opts.x,
      y: opts.y,
      "text-anchor": opts.anchor ?? "middle",
      transform: opts.vertical ? `rotate(-90 ${opts.x} ${opts.y})` : null,
      text,
    },
    svg,
  );
  const W = Number(svg.getAttribute("width"));
  const tw = (t: string) => textWidth(t, 12, 500);
  const subW = opts.sub ? 8 + textWidth(opts.sub, 11.5, 400) : 0;
  if (opts.vertical) {
    const room = Number(svg.getAttribute("height")) - 8;
    if (opts.sub && tw(text) + subW <= room)
      s("tspan", { dx: 8, class: "sb-sub", text: opts.sub }, el);
    return el;
  }
  if ((opts.anchor ?? "middle") !== "middle" || !W) {
    if (opts.sub) s("tspan", { dx: 8, class: "sb-sub", text: opts.sub }, el);
    return el;
  }
  const pad = 4;
  const room = W - 2 * pad;
  const w = tw(text) + (opts.sub && tw(text) + subW <= room ? subW : 0);
  if (w > tw(text)) s("tspan", { dx: 8, class: "sb-sub", text: opts.sub }, el);
  if (w <= room) {
    el.setAttribute("x", String(Math.min(W - pad - w / 2, Math.max(pad + w / 2, opts.x))));
    return el;
  }
  // Too wide for the chart: two lines, split where they come out most even.
  const words = text.split(" ");
  let best = 1;
  let bestW = Number.POSITIVE_INFINITY;
  for (let i = 1; i < words.length; i++) {
    const m = Math.max(tw(words.slice(0, i).join(" ")), tw(words.slice(i).join(" ")));
    if (m < bestW) {
      best = i;
      bestW = m;
    }
  }
  el.textContent = "";
  el.setAttribute("x", String(W / 2));
  s("tspan", { x: W / 2, text: fitText(words.slice(0, best).join(" "), room, 12) }, el);
  s("tspan", { x: W / 2, dy: 15, text: fitText(words.slice(best).join(" "), room, 12) }, el);
  growSvg(svg, 15);
  return el;
}
