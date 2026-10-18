// Stacked answer-distribution bars for the question and run pages, as HTML
// strings (the question page renders them at build time, the run page and
// gated question pages in the browser). Styles: styles/dist-bars.css.
// Behaviour (tap a segment to read it, fit the printed shares):
// scripts/distBars.ts.
//
// - Segments print their share inside when they are wide enough to hold it
//   (distBars.ts hides the ones that don't fit), and carry the option and
//   share in data attributes and a title for hover.
// - A "reference" bar is the thin human bar drawn under each model's bar so
//   every row can be read against people without scrolling back up.
// - Wrap a row's bars and a `distReadout()` in an element with
//   `data-dist-group`: tapping a segment writes the option and its share in
//   each of the group's named bars ("agree: model 41.0% · people 23.5%")
//   into the readout, and highlights that option in the group's bars.

import { optionColor } from "./answerPalette";

const esc = (s: unknown): string =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

export interface DistBarOpts {
  /** Accessible name prefix, e.g. "Distribution: " or "Model distribution: ". */
  aria: string;
  /** Thin reference bar (people) under a model's bar: no printed shares. */
  ref?: boolean;
  /** Short name used in the tap readout ("model", "people"). */
  name?: string;
}

/** Options to draw: `options` when given, else the distribution's own keys. */
export const distKeys = (options: string[] | null | undefined, dist: Record<string, number>) =>
  options?.length ? options : Object.keys(dist);

export function distBarHtml(
  dist: Record<string, number>,
  options: string[],
  o: DistBarOpts,
): string {
  const keys = distKeys(options, dist);
  const segments = keys
    .map((k, i) => {
      const v = Math.max(0, Math.min(1, dist[k] ?? 0));
      const pct = v * 100;
      const shown = `${pct.toFixed(1)}%`;
      const label = !o.ref && pct >= 8 ? `<span class="dist-pct">${Math.round(pct)}%</span>` : "";
      return `<span class="dist-seg" data-o="${esc(k)}" data-p="${shown}" title="${esc(k)}: ${shown}" style="width:${pct}%;background:${optionColor(keys, i)}">${label}</span>`;
    })
    .join("");
  const summary = keys.map((k) => `${k}: ${((dist[k] ?? 0) * 100).toFixed(1)}%`).join(", ");
  const name = o.name ? ` data-name="${esc(o.name)}"` : "";
  return `<span class="dist-bar${o.ref ? " dist-bar--ref" : ""}"${name} role="img" aria-label="${esc(`${o.aria}${summary}`)}">${segments}</span>`;
}

/** Where a tapped segment's option and share are written. */
export const distReadout = (hint = ""): string =>
  `<span class="dist-readout" aria-live="polite" data-hint="${esc(hint)}">${esc(hint)}</span>`;

/** Legend chips for `options`, in bar order and colours. */
export function distLegendHtml(options: string[]): string {
  return options
    .map(
      (k, i) =>
        `<span class="dist-chip"><span class="dist-swatch" style="background:${optionColor(options, i)}"></span>${esc(k)}</span>`,
    )
    .join("");
}
