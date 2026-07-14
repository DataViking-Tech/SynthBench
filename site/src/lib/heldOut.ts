/**
 * Held-out re-eval client helpers — RESERVED plumbing (issue #259).
 *
 * These fields (`sps_held_out`, `sps_held_out_delta`, `held_out_badge`,
 * `held_out_last_run`) were sketched for a periodic server-side re-eval
 * cron. No pipeline currently populates them, and no leaderboard entry
 * carries them today: submission-time server-side scoring against the
 * canonical private-holdout answer key (`synthbench.private_holdout` +
 * `verification_badge`) largely supersedes the cron for the fabrication
 * threat model. Whether a periodic re-eval is still wanted (it would only
 * add value against post-submission drift/contamination) is an open design
 * decision — see the #259 close-out audit. The badge renders nothing while
 * the fields are absent, so keeping the plumbing is harmless.
 *
 * The threshold is borrowed from
 * `synthbench.private_holdout.SPS_DIVERGENCE_THRESHOLD` — the publish-time
 * cheat-detector uses the same magnitude.
 */

import type { LeaderboardEntry } from "@/types/leaderboard";

/** Δ above which the held-out re-eval flags a row for review. */
export const LEADERBOARD_HELD_OUT_DELTA_THRESHOLD = 0.05;

export type HeldOutBadgeState = "verified" | "flagged" | "none";

/**
 * Derive the badge state from `entry.held_out_badge` with a fallback to
 * `sps_held_out_delta` so the UI is correct even if a publisher emits the
 * delta but forgets the explicit badge field.
 */
export function heldOutBadgeState(entry: LeaderboardEntry): HeldOutBadgeState {
  if (entry.held_out_badge === "verified" || entry.held_out_badge === "flagged") {
    return entry.held_out_badge;
  }
  const delta = entry.sps_held_out_delta;
  if (delta == null || Number.isNaN(delta)) return "none";
  return delta > LEADERBOARD_HELD_OUT_DELTA_THRESHOLD ? "flagged" : "verified";
}

/** Human-readable tooltip body for the badge. */
export function heldOutBadgeTitle(entry: LeaderboardEntry): string {
  const state = heldOutBadgeState(entry);
  if (state === "none") return "Held-out re-eval has not run for this row yet";
  const parts: string[] = [];
  if (entry.sps_held_out != null) {
    parts.push(`Held-out SPS ${entry.sps_held_out.toFixed(3)}`);
  }
  if (entry.sps_held_out_delta != null) {
    parts.push(`Δ ${entry.sps_held_out_delta.toFixed(3)}`);
  }
  parts.push(`threshold ${LEADERBOARD_HELD_OUT_DELTA_THRESHOLD.toFixed(2)}`);
  if (entry.held_out_last_run) {
    parts.push(`last run ${entry.held_out_last_run}`);
  }
  const verdict =
    state === "verified"
      ? "Public/held-out scores agree"
      : "Public and held-out scores diverge — under investigation";
  return `${verdict}. ${parts.join(" · ")}.`;
}
