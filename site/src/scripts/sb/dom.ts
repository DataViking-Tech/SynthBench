// Small DOM + SVG + scale helpers shared by the Index pages. Text always goes
// in via textContent / text nodes, never innerHTML.

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

const minus = (s: string) => s.replace("-", "−");
export const fmt = {
  int: (v: number | null | undefined) => (v == null ? "—" : minus(Math.round(v).toString())),
  one: (v: number | null | undefined) => (v == null ? "—" : minus(v.toFixed(1))),
  delta: (v: number | null | undefined) =>
    v == null ? "—" : `${v > 0 ? "+" : v < 0 ? "−" : "±"}${Math.abs(Math.round(v))}`,
  three: (v: number | null | undefined) => (v == null ? "—" : v.toFixed(3)),
  usd: (v: number | null | undefined) =>
    v == null ? "—" : v < 0.01 ? "<$0.01" : `$${v.toFixed(2)}`,
  date: (iso: string) =>
    new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
};

/** Re-render `draw` whenever the element's width changes or `subscribe` fires. */
export function mount(
  el: HTMLElement,
  draw: (width: number) => void,
  subscribe?: (fn: () => void) => void,
): () => void {
  let last = 0;
  const run = () => {
    const w = Math.floor(el.clientWidth);
    if (!w) return;
    last = w;
    el.replaceChildren();
    draw(w);
  };
  new ResizeObserver(() => {
    if (Math.floor(el.clientWidth) !== last) run();
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
  const cands: [number, number, Placed["anchor"]][] = [
    [10, 4, "start"],
    [-10, 4, "end"],
    [0, -11, "middle"],
    [0, 19, "middle"],
    [9, -9, "start"],
    [-9, -9, "end"],
    [9, 17, "start"],
    [-9, 17, "end"],
  ];
  const boxOf = ([dx, dy, anchor]: (typeof cands)[number]) => {
    const x = px + dx;
    const y = py + dy;
    const x0 = anchor === "start" ? x : anchor === "end" ? x - w : x - w / 2;
    return { p: { x, y, anchor }, b: [x0 - 2, y - 11, x0 + w + 2, y + 3] as Box };
  };
  const hits = (b: Box) =>
    placed.some((o) => !(b[2] < o[0] || b[0] > o[2] || b[3] < o[1] || b[1] > o[3])) ||
    points.some(([qx, qy]) => qx > b[0] - 5 && qx < b[2] + 5 && qy > b[1] - 5 && qy < b[3] + 5) ||
    b[0] < bounds[0] ||
    b[2] > bounds[2] ||
    b[1] < bounds[1] ||
    b[3] > bounds[3];
  for (const c of cands) {
    const o = boxOf(c);
    if (!hits(o.b)) {
      placed.push(o.b);
      return o.p;
    }
  }
  const o = boxOf(cands[0]);
  placed.push(o.b);
  return o.p;
}

/** Diverging fill around 0: blue above random, red below, neutral at 0. */
export function heat(v: number | null | undefined, max = 50): { bg: string; fg: string } {
  if (v == null) return { bg: "transparent", fg: css("--sb-muted") };
  const parse = (c: string) => [1, 3, 5].map((i) => Number.parseInt(c.slice(i, i + 2), 16));
  const mid = parse(css("--sb-heat-mid"));
  const end = parse(v >= 0 ? css("--sb-heat-pos") : css("--sb-heat-neg"));
  const t = Math.min(1, Math.abs(v) / max) ** 0.85 * 0.9;
  const rgb = mid.map((x, i) => Math.round(x + (end[i] - x) * t));
  const lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  return { bg: `rgb(${rgb.join(",")})`, fg: lum < 145 ? "#ffffff" : "#15171a" };
}

/** Axis title: horizontal under the axis, or rotated along a vertical axis. */
export function axisTitle(
  svg: SVGSVGElement,
  text: string,
  opts: { x: number; y: number; vertical?: boolean; anchor?: "start" | "middle" | "end" },
): void {
  s(
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
}
