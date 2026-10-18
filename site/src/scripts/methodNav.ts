// Method page (/methodology) navigation. The page is long, so on phones:
// - long secondary sections start folded under their lede ([data-mfold],
//   components/methodology/MethodSection.astro) behind a "Read more" button;
// - the sticky "On this page" bar names the current section and closes after
//   a jump (components/methodology/MethodJump.astro);
// - a back-to-top button appears after two screens (all widths).
// Any link, hash or find-in-page match that lands inside a folded body opens
// it first, so anchors never point at hidden text. Without JavaScript the
// whole page stays open and the menu is a plain <details>.

const phone = matchMedia("(max-width: 639px)");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");

// ---------- Folds ----------
interface Fold {
  body: HTMLElement;
  btn: HTMLButtonElement;
  /** The button's visible words ("Read more" / "Show less"). */
  word: HTMLElement;
  /** Opened by the reader (or a link into it); stays open across resizes. */
  open: boolean;
}
const folds: Fold[] = [];

function render(f: Fold): void {
  const folded = phone.matches && !f.open;
  if (folded) f.body.setAttribute("hidden", "until-found");
  else f.body.removeAttribute("hidden");
  f.btn.hidden = !phone.matches;
  f.btn.setAttribute("aria-expanded", String(!folded));
  f.word.textContent = folded ? "Read more" : "Show less";
}

for (const body of document.querySelectorAll<HTMLElement>("[data-mfold]")) {
  const section = body.closest("section");
  const title = section?.querySelector("h2")?.textContent?.trim() ?? "";
  body.id ||= `${section?.id ?? "sec"}-more`;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "sb-mfold-btn";
  btn.setAttribute("aria-controls", body.id);
  const word = document.createElement("span");
  btn.append(word);
  // Screen readers hear which section the button opens.
  if (title) {
    const t = document.createElement("span");
    t.className = "sr-only";
    t.textContent = `: ${title}`;
    btn.append(t);
  }
  const f: Fold = { body, btn, word, open: false };
  btn.addEventListener("click", () => {
    f.open = !f.open;
    render(f);
    // Closing a long section from below would leave the reader far past it;
    // bring its heading back into view.
    if (!f.open && section && section.getBoundingClientRect().top < 0)
      section.scrollIntoView({ block: "start" });
  });
  // Chrome's find-in-page reveals hidden="until-found" text by itself.
  body.addEventListener("beforematch", () => {
    f.open = true;
    render(f);
  });
  body.before(btn);
  folds.push(f);
  render(f);
}
phone.addEventListener("change", () => {
  for (const f of folds) render(f);
});

/** Open the fold that holds `el`, if it is folded. */
function reveal(el: Element | null): void {
  if (!el) return;
  for (const f of folds)
    if (!f.open && f.body.contains(el)) {
      f.open = true;
      render(f);
    }
}

function targetOf(hash: string): HTMLElement | null {
  if (hash.length < 2) return null;
  try {
    return document.getElementById(decodeURIComponent(hash.slice(1)));
  } catch {
    return null;
  }
}

// A link to somewhere on this page: open the target's fold before the
// browser scrolls to it.
document.addEventListener("click", (e) => {
  const a = (e.target as Element | null)?.closest?.<HTMLAnchorElement>("a[href*='#']");
  if (!a) return;
  const url = new URL(a.href, location.href);
  if (url.pathname !== location.pathname || url.search !== location.search) return;
  reveal(targetOf(url.hash));
});
addEventListener("hashchange", () => reveal(targetOf(location.hash)));

// Arrived with a hash: the browser scrolled there before the folds above it
// closed and before the charts and tables above it were drawn, so the target
// drifts. Open its fold and land on it again whenever the content above
// changes height, for a few seconds or until the reader scrolls themselves.
const landing = targetOf(location.hash);
if (landing) {
  reveal(landing);
  const land = () => landing.scrollIntoView({ block: "start", behavior: "instant" });
  const page = document.querySelector(".sb-meth");
  const ro = new ResizeObserver(() => requestAnimationFrame(land));
  const stop = () => {
    ro.disconnect();
    for (const t of ["wheel", "touchstart", "keydown", "pointerdown"]) removeEventListener(t, stop);
  };
  for (const t of ["wheel", "touchstart", "keydown", "pointerdown"])
    addEventListener(t, stop, { passive: true });
  if (page) ro.observe(page);
  requestAnimationFrame(land);
  setTimeout(stop, 4000);
}

// ---------- "On this page" ----------
const allJump = [...document.querySelectorAll<HTMLAnchorElement>("a[data-jump]")];
for (const a of allJump)
  if (!document.getElementById(a.dataset.jump ?? "")) (a.closest("li") ?? a).remove();
const jumpLinks = allJump.filter((a) => a.isConnected);

const menu = document.querySelector<HTMLDetailsElement>(".sb-jump-d");
const cur = document.querySelector<HTMLElement>("[data-jump-cur]");
if (menu) {
  menu.addEventListener("click", (e) => {
    if ((e.target as Element).closest("a[data-jump]")) menu.open = false;
  });
  document.addEventListener("pointerdown", (e) => {
    if (menu.open && !menu.contains(e.target as Node)) menu.open = false;
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary")?.focus();
    }
  });
}

// ---------- Back to top ----------
const totop = document.createElement("button");
totop.type = "button";
totop.className = "sb-totop";
totop.hidden = true;
totop.setAttribute("aria-label", "Back to top");
totop.innerHTML = '<span aria-hidden="true">↑</span> Top';
totop.addEventListener("click", () => {
  if (menu) menu.open = false;
  scrollTo({ top: 0, behavior: reduceMotion.matches ? "instant" : "smooth" });
  document.querySelector<HTMLElement>(".sb-meth h1")?.focus({ preventScroll: true });
});
(document.querySelector(".sb-meth") ?? document.body).append(totop);

// ---------- Current section ----------
// The last section whose top has passed under the bar.
const sections = jumpLinks
  .map((a) => document.getElementById(a.dataset.jump ?? ""))
  .filter((el, i, all): el is HTMLElement => el != null && all.indexOf(el) === i);
const labels = new Map(jumpLinks.map((a) => [a.dataset.jump ?? "", a.textContent?.trim() ?? ""]));
let current = "";
let ticking = false;
function spy(): void {
  ticking = false;
  const line = phone.matches ? 72 : 24;
  let id = sections[0]?.id ?? "";
  for (const s of sections) if (s.getBoundingClientRect().top <= line) id = s.id;
  if (id !== current) {
    current = id;
    if (cur) cur.textContent = labels.get(id) ?? "";
    for (const a of jumpLinks)
      if (a.dataset.jump === id) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
  }
  totop.hidden = scrollY < 2 * innerHeight;
}
const onScroll = () => {
  if (!ticking) {
    ticking = true;
    requestAnimationFrame(spy);
  }
};
addEventListener("scroll", onScroll, { passive: true });
addEventListener("resize", onScroll, { passive: true });
spy();

// A module, so its names stay out of the global scope.
export {};
