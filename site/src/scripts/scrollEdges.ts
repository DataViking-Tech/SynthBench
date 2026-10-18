// Sideways scrollers that aren't tables: segmented controls (`.sb-seg`,
// which stay on one row on phones, see sb.css) and code samples or anything
// else marked `.sb-scrollx`. `data-more="right|left|both"` fades the clipped
// edge while there is more to scroll to. Segmented controls also scroll
// their checked option into view whenever it changes, including when a page
// rebuilds the control. Loaded by the Index pages (ui.ts), /explore,
// /compare and CodeBlock.astro.

const SEL = ".sb-seg, .sb-scrollx";
const last = new WeakMap<Element, Element | null>();
const watched = new WeakSet<Element>();

function edges(el: HTMLElement): void {
  const max = el.scrollWidth - el.clientWidth;
  const left = el.scrollLeft > 2;
  const right = max > 2 && el.scrollLeft < max - 2;
  const more = left && right ? "both" : right ? "right" : left ? "left" : "";
  if (more) el.dataset.more = more;
  else delete el.dataset.more;
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
  for (const el of document.querySelectorAll<HTMLElement>(SEL)) {
    if (!watched.has(el)) {
      watched.add(el);
      el.addEventListener("scroll", () => edges(el), { passive: true });
      ro.observe(el);
    }
    if (el.classList.contains("sb-seg")) reveal(el);
    edges(el);
  }
}

sync();
new MutationObserver(sync).observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ["aria-checked", "aria-selected"],
});
