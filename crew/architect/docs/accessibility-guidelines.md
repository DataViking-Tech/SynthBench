# SynthBench Accessibility Guidelines

Target standard: **WCAG 2.1 AA**. Lighthouse accessibility gate: **≥ 0.90** on every route (enforced in CI via `site/lighthouserc.json`).

This doc codifies the patterns that came out of the site-wide accessibility audits. If you're writing a new component or page, match these patterns — don't invent a new one. If you genuinely need something new, update this doc in the same PR.

---

## Core principles

1. **Every interactive element is keyboard-reachable.** If you can click it with a mouse, you must be able to reach it with Tab and activate it with Enter or Space.
2. **Every interactive element has an accessible name and a role.** Icon-only buttons need `aria-label`. Custom widgets need the right ARIA pattern (or don't use a custom widget — use a native `<button>`, `<a>`, `<select>`, `<details>`).
3. **Color is never the only carrier of information.** Status badges, chart segments, validation state — always pair color with text, icon, pattern, or shape.
4. **Focus order matches visual order.** If you see a "tab jumps to the wrong place" bug, it's usually because JS injected an element mid-tree without updating the DOM order.
5. **Don't strip focus rings without replacing them.** `focus:outline-none` without a `focus:ring-*` replacement is a WCAG 2.4.7 failure. See the global `:focus-visible` fallback in `site/src/styles/global.css`.

---

## Required site-wide patterns

### Skip link (WCAG 2.4.1)

Every page gets a skip link as the first child of `<body>`, rendered via `BaseLayout.astro`. Don't remove it. If you add a new layout, copy the pattern:

```astro
<a
  href="#main-content"
  class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 ..."
  >Skip to main content</a
>
<main id="main-content" tabindex="-1">…</main>
```

The `tabindex="-1"` on `<main>` makes it a script-targetable focus destination without adding it to the tab order.

### Page titles

Every page sets a descriptive `<title>` via `<BaseLayout title="…">`. Avoid generic titles like "Loading…" while data fetches — server-render a fallback (id, slug, or "Loading: specific thing") so a deep-linked screen-reader user doesn't land on a naked "Loading".

### Heading hierarchy

One `<h1>` per page. `<h2>` sections. Don't skip levels for visual size — use Tailwind classes on the right semantic tag. If a card inside a section needs big prominent text, it's an `<h3>` (or `<p class="text-2xl font-bold">` if it isn't structurally a heading).

### External links

Links with `target="_blank"` get `rel="noopener noreferrer"` **and** a visually-hidden "opens in a new tab" cue:

```astro
<a href="https://..." target="_blank" rel="noopener noreferrer">
  GitHub<span class="sr-only"> (opens in a new tab)</span>
</a>
```

### Icons

- Decorative SVG: `aria-hidden="true"` on the `<svg>`.
- Icon-only buttons/links: `aria-label` on the **button/link**, not the svg.
- Informational SVG (rare): first child is `<title>` with text that describes what it conveys.

---

## Component patterns

### 1. Charts (ECharts) — `Chart.astro` contract

Every chart MUST supply a `title` (required) and SHOULD supply a `description` and/or `dataTable`. The wrapper renders a `<figure>` + visually-hidden `<figcaption>`, sets `role="img"` with an accessible name on the inner container, and optionally exposes a `<details>`-wrapped real `<table>` equivalent.

```astro
<Chart
  title="SPS by Model with 95% confidence intervals"
  description="Dot plot of Survey Parity Score per model; whiskers are 95% CIs."
  dataTable={{
    headers: ["Model", "SPS", "CI low", "CI high"],
    rows: entries.map((e) => [e.model, e.sps, e.ci_lower, e.ci_upper]),
  }}
  option={chartOption}
/>
```

**Why:** ECharts SVG output has no accessible name — a screen-reader user reading 12 charts with no titles gets 12 "group" announcements and nothing else. The data table gives keyboard/screen-reader users an equivalent way to reach the numbers.

**Reduced motion:** `Chart.astro` already injects `animation: false` into the option when `prefers-reduced-motion: reduce` is set. If you init ECharts directly (don't — use the wrapper), match that behavior.

**Inline ECharts exceptions:** `config/[id].astro` and `DemographicHeatmap.astro` initialize charts inline because they need to refetch/reselect data client-side. They follow the same contract manually: an outer `<figure aria-labelledby>`, inner `<div role="img" aria-labelledby aria-describedby>`, and a sibling `<details>`/`<table>` data alternative rendered from the same data. If you need the same pattern, copy-paste from there rather than bypassing `Chart.astro`.

### 2. Sortable table headers

Sort state MUST live on the `<th>` as `aria-sort="ascending|descending|none"`. The click target MUST be a `<button>` inside the `<th>` — not the `<th>` itself, not a `<div>` with a click handler. The visual sort direction indicator (▲/▼) is `aria-hidden="true"` and paired with a screen-reader status message.

```astro
<th scope="col" aria-sort="none">
  <button type="button" data-sort="sps">
    SPS <span class="sort-indicator" aria-hidden="true"></span>
  </button>
</th>
```

```ts
// On click: flip the direction, update aria-sort on the th, update indicator,
// and announce the new sort via a live region.
activeTh.setAttribute("aria-sort", ascending ? "ascending" : "descending");
announce(`Sorted by ${colLabel} ${ascending ? "ascending" : "descending"}.`);
```

Sort announcements go into a visually-hidden `role="status" aria-live="polite"` region that persists on the page (create it once; update `textContent`).

### 3. Expandable table rows

The expand affordance is a `<button>` inside the first `<td>` — not a click handler on the `<tr>`. The button carries `aria-expanded` + `aria-controls={detailId}`. The detail row has an `id` matching `aria-controls`, starts `hidden`, and toggles via `.classList.toggle("hidden", !expanded)`.

```astro
<tr>
  <td>
    <button type="button" class="expand-row"
            aria-expanded="false" aria-controls="detail-3"
            aria-label="Show details for Claude on OpinionsQA">
      <span class="expand-caret" aria-hidden="true">▸</span>
    </button>
  </td>
  …other cells…
</tr>
<tr id="detail-3" class="detail-row hidden">…</tr>
```

### 4. Row-as-link (LeaderboardTable, SummaryLeaderboard)

If a whole row should navigate to a detail page, the row itself carries `role="link"`, `tabindex="0"`, and `aria-label`; a hidden anchor inside the first data cell receives the click-forwarding for native navigation. Pair with in-cell controls (chevron buttons, real `<a>` links) that `event.stopPropagation()` so their interactions are not hijacked by the row handler.

### 5. Tab-like UI (DatasetTabs, ViewToggle)

If the buttons *swap which content is visible* and you want to treat the group as tabs, you commit to the full ARIA Tabs pattern: `role="tablist"`, `role="tab"`, `role="tabpanel"`, roving tabindex, arrow-key navigation, Home/End. That's a lot of code.

**Default: don't use tab semantics.** Use toggle buttons with `aria-pressed`, wrapped in `<div role="group" aria-label="…">`. That's what SynthBench does for dataset filter and view toggle. No arrow-key keyboard model required — each button is reachable via Tab.

**Do not** wrap toggle button groups in `<nav>` — `<nav>` is for navigation landmarks, and a group of filter buttons is not site navigation.

### 6. Disclosure list (e.g., `/explore`)

The runs hierarchy at `/explore` looks like a tree but is a disclosure list. **This is intentional.** A real ARIA `role="tree"` requires arrow-key navigation, roving tabindex, `role="treeitem"` on every descendant, and `aria-level` / `aria-setsize` / `aria-posinset` — which we don't implement.

For nested expand/collapse sections without keyboard tree navigation:
- Each header is a native `<button aria-expanded aria-controls>`.
- The body it controls has a matching `id` and uses the native `hidden` attribute when collapsed.
- **Never** slap `role="tree"` on the container unless you're also going to implement the keyboard model. `role="tree"` without keyboard support is a worse lie than having no role at all.

### 7. Preserving focus across re-renders

When a JS interaction (filter change, expand toggle, selection change) triggers a full DOM rebuild, focus is lost to `<body>`. To preserve it:

1. Before the re-render, capture the currently-focused element's stable key: `document.activeElement.dataset.focusKey`.
2. When rebuilding, apply the same `data-focus-key` to the element that represents "the same thing" in the new DOM.
3. After the re-render, `document.querySelector('[data-focus-key="…"]')?.focus()`.

See `renderTree()` in `site/src/pages/explore.astro` for the reference implementation.

**Better when possible:** surgical DOM updates that don't destroy focusable nodes. Only re-render what changed.

### 8. Dialog / modal (mobile menu)

Any `role="dialog" aria-modal="true"` MUST:

1. Save `document.activeElement` before opening.
2. Move focus inside the dialog on open (typically the close button or first focusable).
3. Trap Tab / Shift-Tab within the dialog.
4. Close on Escape.
5. Restore focus to the saved trigger on close.

The trigger (e.g., hamburger button) carries `aria-expanded` + `aria-controls={dialogId}` and mirrors the dialog's open state.

Reference implementation: the mobile menu in `site/src/components/shared/Nav.astro`. Reuse that logic — don't roll another one.

### 9. Forms

- Every `<input>` / `<select>` has a programmatic label. Preferred: `<label for="id">` + matching `id`. Acceptable fallbacks: implicit label wrapping, or `aria-label`.
- Grouped controls (range min/max pair, related checkboxes) go inside `<fieldset><legend>…</legend></fieldset>` or `<div role="group" aria-labelledby>`.
- Custom placeholder text is not a label substitute.
- Error messages: render them near the input with `aria-describedby` pointing at the error id, and use `role="alert"` for dynamic error display.

### 10. "Disabled link" anti-pattern

A link is **not** disabled via `aria-disabled` + `href="#"`. Keyboard users can still Tab to it and press Enter, which navigates to `#` and scrolls to top — a bad surprise.

**Fix:** either (a) toggle between `<button disabled>` (when disabled) and `<a>` (when enabled), or (b) keep the anchor but set `tabindex="-1"` while disabled **and** install a click/keydown guard that calls `preventDefault()` when `aria-disabled="true"`. See `#compare-go` in `site/src/pages/explore.astro` + `guardDisabledLink()` helper.

### 11. Live regions & status messages

For dynamic text that should be announced (filter result counts, "copied to clipboard", loading→loaded transitions, error messages):

- Create the live region **on mount**, not on demand. Appending a new live region dynamically doesn't reliably trigger announcements on all screen readers.
- Use `role="status" aria-live="polite"` for non-urgent updates, `role="alert"` (implies `aria-live="assertive"`) for errors that need immediate attention.
- Update via `textContent = "…"`; don't swap the whole element.

```astro
<p id="explore-live" class="sr-only" role="status" aria-live="polite"></p>
```

```ts
const live = document.getElementById("explore-live");
if (live) live.textContent = `${nConfigs} configs · ${nRuns} runs`;
```

### 12. Distribution bars / custom visualizations

Color-only encoding fails for ~8% of male users (colorblindness). For small stacked bars (see `compare.astro`, `run/[id].astro`):

- The bar container gets `role="img"` and `aria-label` with a readable summary of the data.
- The text label beside the bar stays `aria-hidden="true"` (it's already in the aria-label).
- A `<details>` + real `<table>` data equivalent is ideal when the data density warrants it.

---

## Color contrast

### Tokens (defined in `site/src/styles/global.css`)

- `--color-text` on `--color-surface`: high contrast. No action needed.
- `--color-muted`: darkened to `oklch(0.45 0.01 264)` in light mode; auto-brightens to `oklch(0.72 0.01 264)` in dark mode. Targets ≥4.5:1 for body text. If you need softer, call it out and verify with a contrast checker.
- `--color-baseline`, `--color-accent`: darkened from the original values so badges like `text-baseline` on `bg-baseline/20` meet AA (normal text requires 4.5:1, large text 3:1). **Verify in browser after any token change** — oklch lightness changes affect blend with alpha.

### Rules of thumb

- Body text: 4.5:1 minimum.
- Large text (18pt / 14pt bold): 3:1 minimum.
- UI component boundaries, focus indicators, chart data points: 3:1 minimum (WCAG 1.4.11).
- **Tinted background + same-hue text is a trap.** `bg-accent/10 text-accent` often falls to 2–3:1. Use `/15` or `/20` tint + a darker text shade, OR a solid bg with white text. Always re-check after changing alpha.
- **Dark-mode and light-mode must both pass.** The dark-mode override on `--color-muted` is there because the same lightness that works against `--color-surface` (light) does not work against `--color-surface-dark`.

### Badges

- `bg-accent/15 text-accent` — acceptable with the darker accent token (verify per-instance).
- Provider tags (`bg-provider-synthpanel/10 text-provider-synthpanel`) — provider colors are hex literals; check each one against the surfaces they sit on.

---

## Keyboard / focus checklist

Before merging a visual change, run:

1. Load the page. Tab through every interactive element. Focus indicator visible at every stop?
2. Activate every interactive element with Enter (links, buttons) and Space (buttons, checkboxes). Expected result?
3. Close dialogs with Escape. Focus returns to the trigger?
4. Sort a table, expand a row, change a filter, submit a form. Focus stays in a sensible place after the state change?
5. Test `prefers-reduced-motion`. Animations short-circuit?
6. Emulate `prefers-color-scheme: dark`. All contrast still passes?

The automated Lighthouse a11y score (enforced at ≥0.90 in CI) catches a small subset of issues — mostly the obvious missing-label / missing-landmark ones. It does not catch: keyboard traps, missing focus rings, broken dialogs, color-only information, sort announcements, reduced motion, or any live-region behavior. Run the checklist above yourself.

---

## Testing references

- WCAG 2.1 Quick Reference: https://www.w3.org/WAI/WCAG21/quickref/
- APG (ARIA Authoring Practices Guide): https://www.w3.org/WAI/ARIA/apg/ — has working examples for every pattern above.
- Manual testing: macOS VoiceOver (Cmd+F5 to toggle), NVDA (Windows), Firefox / Chrome devtools' "Accessibility tree" inspector.
- Automated: `npm run build` in `site/`, then the CI Lighthouse job.
