// Stable URL slug for vendor (provider) names on /leaderboard/<vendor>/ pages.
// Provider strings in leaderboard.json contain spaces, dots, and parentheses
// (e.g. "SynthPanel (Haiku 4.5)") — none safe in a path segment. We normalize
// by lowercasing, stripping anything outside [a-z0-9], and collapsing runs of
// dashes so the slug round-trips cleanly through static-path generation.

export function vendorSlug(provider: string): string {
  return provider
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function vendorSlugMap(providers: Iterable<string>): Map<string, string> {
  const out = new Map<string, string>();
  for (const p of providers) {
    const slug = vendorSlug(p);
    if (!slug) continue;
    if (!out.has(slug)) out.set(slug, p);
  }
  return out;
}
