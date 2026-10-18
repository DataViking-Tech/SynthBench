// Behaviour for the stacked distribution bars built by lib/distBar.ts.
//
// - Tap (or click) a segment: the option and its share in each of the
//   group's named bars (model, people) go into the group's readout, and the
//   option is highlighted in the group's bars. Tap it again to clear.
//   Hover titles stay for mouse users; the bar's accessible name lists
//   every share for screen readers.
// - Printed shares that don't fit their segment are hidden (re-checked on
//   resize and when bars are added, e.g. expanded rows on the run page).

function readout(group: Element, seg: HTMLElement | null): void {
  const out = group.querySelector<HTMLElement>(".dist-readout");
  for (const s of group.querySelectorAll(".dist-seg.is-sel")) s.classList.remove("is-sel");
  group.classList.toggle("has-sel", !!seg);
  if (!seg) {
    if (out) out.textContent = out.dataset.hint ?? "";
    return;
  }
  const opt = seg.dataset.o ?? "";
  for (const s of group.querySelectorAll<HTMLElement>(".dist-seg")) {
    if (s.dataset.o === opt) s.classList.add("is-sel");
  }
  if (!out) return;
  // Every named bar in the group (model and people), else just this one.
  const named = [...group.querySelectorAll<HTMLElement>(".dist-bar[data-name]")];
  const shares = named
    .map((bar) => {
      const s = [...bar.querySelectorAll<HTMLElement>(".dist-seg")].find(
        (x) => x.dataset.o === opt,
      );
      return s ? `${bar.dataset.name} ${s.dataset.p}` : null;
    })
    .filter(Boolean);
  out.textContent = `${opt}: ${shares.length > 1 ? shares.join(" · ") : (seg.dataset.p ?? "")}`;
}

document.addEventListener("click", (e) => {
  const seg = (e.target as Element | null)?.closest<HTMLElement>(".dist-seg");
  if (!seg) return;
  const group = seg.closest("[data-dist-group]");
  if (!group) return;
  const again = seg.classList.contains("is-sel") && group.classList.contains("has-sel");
  readout(group, again ? null : seg);
});

/** Hide printed shares wider than their segment. */
function fit(root: ParentNode = document): void {
  for (const pct of root.querySelectorAll<HTMLElement>(".dist-pct")) {
    const seg = pct.parentElement;
    if (!seg) continue;
    pct.hidden = false;
    pct.hidden = pct.offsetWidth + 6 > seg.clientWidth;
  }
}

let queued = false;
const refit = () => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(() => {
    queued = false;
    fit();
  });
};
fit();
addEventListener("resize", refit);
new MutationObserver(refit).observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  // Not "hidden": fit() sets it, and would re-trigger itself.
  attributeFilter: ["class"],
});
