// sb-xsite: PostHog ⇄ Supabase identity bootstrap.
//
// Loaded lazily (and only for visitors who already have a stored Supabase
// session — see BaseLayout) so supabase-js stays out of the bundle for the
// anonymous common case, keeping the Lighthouse budget intact.
//
// Responsibilities:
//   1. On load, if a session exists, identify the current PostHog person.
//   2. Keep identity in sync with future auth-state changes (sign-in/out).
//
// PostHog persists the identified distinct_id itself, so we do not need to
// re-identify on every page — but doing so on load is cheap and self-heals
// cases where PostHog's storage was cleared while the Supabase session lived
// on (the two use independent storage with independent lifetimes).

import {
  getSession,
  getSupabaseClient,
  identifyToAnalytics,
  isAuthConfigured,
  resetAnalyticsIdentity,
} from "@/lib/auth";

let started = false;

export async function initAnalyticsIdentity(): Promise<void> {
  if (started || !isAuthConfigured()) return;
  started = true;

  try {
    const session = await getSession();
    if (session) identifyToAnalytics(session.user);
  } catch (err) {
    console.warn("[analytics] initial identify failed", err);
  }

  // Future sign-in / sign-out transitions. signOut() in auth.ts also resets
  // directly; this covers token refreshes and cross-tab changes.
  getSupabaseClient().auth.onAuthStateChange((_event, session) => {
    if (session) identifyToAnalytics(session.user);
    else resetAnalyticsIdentity();
  });
}
