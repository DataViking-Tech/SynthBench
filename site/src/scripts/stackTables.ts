// Responsive tables: under 640px, `table.sb-stack` rows render as stacked
// cards (see global.css). Each cell is labelled with its column header via
// `data-label`, kept up to date as client scripts render or re-render tables
// (including tables inserted after load, e.g. gated pages and /explore).

function label(table: HTMLTableElement): void {
  // Skip header cells hidden with display:none (optional columns not rendered).
  const heads = [...table.querySelectorAll<HTMLElement>("thead th")]
    .filter((th) => getComputedStyle(th).display !== "none")
    .map((th) => (th.textContent ?? "").replace(/[▲▼]/g, "").replace(/\s+/g, " ").trim());
  for (const body of table.tBodies) {
    for (const tr of body.rows) {
      let col = 0;
      for (const td of tr.cells) {
        const span = td.colSpan || 1;
        if (span === 1 && heads[col] && td.getAttribute("data-label") !== heads[col])
          td.setAttribute("data-label", heads[col]);
        col += span;
      }
    }
  }
}

const labelAll = () => {
  for (const t of document.querySelectorAll<HTMLTableElement>("table.sb-stack")) label(t);
};
labelAll();
new MutationObserver(labelAll).observe(document.body, { childList: true, subtree: true });
