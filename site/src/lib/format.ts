// Shared number formatting for signed changes. Use these instead of
// hand-written `+${x}` templates, which render negative values as "+-3".

/**
 * A signed change: "+3", "−3" (true minus sign) or "±0" when it rounds to
 * zero. `places` is the number of decimals.
 */
export function signed(v: number | null | undefined, places = 0): string {
  if (v == null || Number.isNaN(v)) return "—";
  const r = Number(v.toFixed(places));
  const body = Math.abs(r).toFixed(places);
  return r > 0 ? `+${body}` : r < 0 ? `−${body}` : `±${body}`;
}

/** A range of signed changes, low to high: "+7 to +22", "−0.2 to +7.1". */
export function signedRange(lo: number, hi: number, places = 0): string {
  const a = signed(Math.min(lo, hi), places);
  const b = signed(Math.max(lo, hi), places);
  return a === b ? a : `${a} to ${b}`;
}
