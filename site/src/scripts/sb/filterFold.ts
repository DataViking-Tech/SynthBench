// Phones: secondary filters (method chips, toggles, system pickers) fold
// behind one "Filters (n)" button so the chart or table starts near the top
// of the screen. Wide screens show them as before and never see the button
// (sb-pages.css, "Filters fold"). `n` counts filters changed from their
// defaults, so a folded bar still says when something is hidden.

import { h } from "./dom";

export interface FilterFold {
  /** Re-read the changed-filter count; call on every state change. */
  rerender: () => void;
}

let uid = 0;

/**
 * Insert the fold button into `bar` before `items[0]` and fold `items` on
 * phones. `changed()` is the number of filters that differ from their
 * defaults.
 */
export function filterFold(
  bar: HTMLElement,
  items: HTMLElement[],
  changed: () => number,
): FilterFold {
  const first = items[0];
  if (first && !first.id) first.id = `sb-ffold-${++uid}`;
  const count = h("span", { class: "sb-ffold-n" });
  const btn = h(
    "button",
    {
      type: "button",
      class: "sb-ffold-btn",
      "aria-expanded": "false",
      "aria-controls": first?.id ?? null,
    },
    "Filters",
    count,
  );
  for (const el of items) el.classList.add("sb-ffold-item");
  btn.addEventListener("click", () => {
    const open = !bar.classList.contains("sb-ffold-open");
    bar.classList.toggle("sb-ffold-open", open);
    btn.setAttribute("aria-expanded", String(open));
  });
  if (first) first.before(btn);
  else bar.append(btn);
  const rerender = () => {
    const n = changed();
    count.textContent = n ? ` (${n})` : "";
    btn.setAttribute("aria-label", n ? `Filters, ${n} changed` : "Filters");
  };
  rerender();
  return { rerender };
}
