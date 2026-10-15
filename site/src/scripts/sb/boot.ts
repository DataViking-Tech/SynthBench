// Loads the JSON payloads a page points at (`<script type="application/json"
// id="sb-…" data-src="…">`, see components/sb/*Payload.astro), then runs the
// page script. Page scripts read payloads synchronously via `payload(id)`,
// so they are imported only after everything has arrived.

const loaded = new Map<string, unknown>();

/** A payload fetched by `boot()`, or an inline one (no data-src) parsed on demand. */
export function payload<T>(id: string): T {
  if (loaded.has(id)) return loaded.get(id) as T;
  const el = document.getElementById(id);
  if (!el?.textContent) throw new Error(`Page data #${id} missing`);
  const value = JSON.parse(el.textContent) as T;
  loaded.set(id, value);
  return value;
}

export function boot(page: () => Promise<unknown>): void {
  const note = document.querySelector<HTMLElement>(".sb-loadnote");
  // Only say "loading" if it takes long enough to notice (cached loads don't).
  const slow = window.setTimeout(() => {
    if (note) note.textContent = "Loading data…";
  }, 300);
  const sources = [...document.querySelectorAll<HTMLElement>("script[data-src][id]")];
  Promise.all(
    sources.map(async (el) => {
      const res = await fetch(el.dataset.src as string);
      if (!res.ok) throw new Error(`${res.status} for ${el.dataset.src}`);
      loaded.set(el.id, await res.json());
    }),
  )
    .then(page)
    .then(() => {
      window.clearTimeout(slow);
      note?.remove();
    })
    .catch((err) => {
      window.clearTimeout(slow);
      console.error(err);
      if (note) {
        note.textContent = "Couldn't load the data for this page. Reload to try again.";
        note.classList.add("err");
      }
    });
}
