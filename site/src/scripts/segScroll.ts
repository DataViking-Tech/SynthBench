// Segmented controls (`.sb-seg`) stay on one row on phones and scroll
// sideways (see the max-width:639px rules in sb.css). This keeps them usable:
// `data-more="right|left|both"` fades the clipped edge, and the checked option
// is scrolled into view whenever it changes, including when a page rebuilds
// the control. Loaded by the Index pages (ui.ts) and by /explore and /compare.

const last = new WeakMap<Element, Element | null>();
const watched = new WeakSet<Element>();

function edges(seg: HTMLElement): void {
  const max = seg.scrollWidth - seg.clientWidth;
  const left = seg.scrollLeft > 2;
  const right = max > 2 && seg.scrollLeft < max - 2;
  const more = left && right ? "both" : right ? "right" : left ? "left" : "";
  if (more) seg.dataset.more = more;
  else delete seg.dataset.more;
}

function reveal(seg: HTMLElement): void {
  const on = seg.querySelector('[aria-checked="true"], [aria-selected="true"], .on');
  if (on === last.get(seg)) return;
  last.set(seg, on);
  if (!on || seg.scrollWidth <= seg.clientWidth) return;
  const r = on.getBoundingClientRect();
  const w = seg.getBoundingClientRect();
  if (r.left < w.left) seg.scrollLeft -= w.left - r.left + 24;
  else if (r.right > w.right) seg.scrollLeft += r.right - w.right + 24;
}

const ro = new ResizeObserver((entries) => {
  for (const e of entries) edges(e.target as HTMLElement);
});

function sync(): void {
  for (const seg of document.querySelectorAll<HTMLElement>(".sb-seg")) {
    if (!watched.has(seg)) {
      watched.add(seg);
      seg.addEventListener("scroll", () => edges(seg), { passive: true });
      ro.observe(seg);
    }
    reveal(seg);
    edges(seg);
  }
}

sync();
new MutationObserver(sync).observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ["aria-checked", "aria-selected"],
});
