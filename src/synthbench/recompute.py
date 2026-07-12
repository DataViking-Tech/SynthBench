"""Recompute aggregate scores from per-question rows.

Single source of truth for the leaderboard-integrity rule that the pipeline
must never trust submitter-supplied aggregates (P0-4): both the tier-2
validator and the publish step derive every score from the per-question
metrics rather than from the submitted ``scores`` / ``aggregate`` blocks.

Two composite conventions exist in the wild (see SUBMISSIONS.md):

* ``parity-2`` — the legacy 2-metric blend ``0.5·P_dist + 0.5·P_rank``.
* ``sps`` — the SynthBench Parity Score: equal-weighted mean of every
  available component (P_dist, P_rank, P_refuse, plus P_cond / P_sub on
  conditioned runs).

P_dist, P_rank, and P_refuse are recomputed here from per-question rows.
P_cond / P_sub cannot be derived from ``per_question`` (they come from
demographic-conditioned sampling that is not serialized per question), so
they are taken from the submitted ``scores`` block when present. They are
bounds-checked upstream by tier-1 validation; recomputing them is tracked
as follow-up work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from synthbench.metrics.composite import synthbench_parity_score

# Convention labels recorded by the validator (see SUBMISSIONS.md).
SPS_CONVENTION_SPS = "sps"
SPS_CONVENTION_PARITY2 = "parity-2"

# Components of the SPS composite that are means of per-question values and
# can therefore be recomputed (and bootstrap-resampled) from ``per_question``.
_EXTENDED_COMPONENTS = ("p_sub", "p_cond")

_BOOTSTRAP_MIN_QUESTIONS = 5


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


@dataclass(frozen=True)
class RecomputedAggregates:
    """Aggregates derived purely from per-question rows (plus passthrough
    extended components for the composite)."""

    n_questions: int
    mean_jsd: float
    median_jsd: float
    mean_kendall_tau: float
    p_dist: float
    p_rank: float
    p_refuse: float | None
    """``None`` when no per-question row carries both refusal rates."""
    parity_two: float
    """Legacy 2-metric composite: ``0.5·P_dist + 0.5·P_rank``."""
    sps: float
    """Full composite: equal-weighted mean of :attr:`components`."""
    components: dict[str, float] = field(default_factory=dict)
    """The components that entered :attr:`sps` (includes any passthrough
    ``p_sub`` / ``p_cond`` from the submitted scores block)."""


def _usable_rows(per_question: Any) -> list[tuple[float, float, float | None]]:
    """Extract ``(jsd, tau, refusal_diff_or_None)`` from per-question rows.

    Rows missing a numeric ``jsd`` or ``kendall_tau`` are skipped entirely —
    they cannot contribute to any recomputed aggregate. The refusal diff is
    ``None`` when either refusal rate is missing on the row.
    """
    if not isinstance(per_question, list):
        return []
    rows: list[tuple[float, float, float | None]] = []
    for q in per_question:
        if not isinstance(q, Mapping):
            continue
        jsd = q.get("jsd")
        tau = q.get("kendall_tau")
        if not _is_number(jsd) or not _is_number(tau):
            continue
        m_ref = q.get("model_refusal_rate")
        h_ref = q.get("human_refusal_rate")
        rdiff = (
            abs(float(m_ref) - float(h_ref))
            if _is_number(m_ref) and _is_number(h_ref)
            else None
        )
        rows.append((float(jsd), float(tau), rdiff))
    return rows


def _extended_from_scores(
    extended_scores: Mapping[str, Any] | None,
) -> dict[str, float]:
    if not extended_scores:
        return {}
    return {
        k: float(extended_scores[k])
        for k in _EXTENDED_COMPONENTS
        if _is_number(extended_scores.get(k))
    }


def recompute_aggregates(
    per_question: Any,
    *,
    extended_scores: Mapping[str, Any] | None = None,
) -> RecomputedAggregates | None:
    """Recompute every derivable aggregate from ``per_question`` rows.

    Args:
        per_question: The submission's ``per_question`` list (raw JSON rows).
        extended_scores: Optional submitted ``scores`` mapping; only its
            ``p_sub`` / ``p_cond`` entries are read (they cannot be derived
            from per-question rows) and folded into the composite.

    Returns:
        :class:`RecomputedAggregates`, or ``None`` when no usable row exists.
    """
    rows = _usable_rows(per_question)
    if not rows:
        return None

    n = len(rows)
    jsds = sorted(r[0] for r in rows)
    mean_jsd = sum(r[0] for r in rows) / n
    mean_tau = sum(r[1] for r in rows) / n
    mid = n // 2
    median_jsd = jsds[mid] if n % 2 else (jsds[mid - 1] + jsds[mid]) / 2.0

    p_dist = 1.0 - mean_jsd
    p_rank = (1.0 + mean_tau) / 2.0

    rdiffs = [r[2] for r in rows if r[2] is not None]
    p_refuse: float | None = None
    if rdiffs:
        p_refuse = max(0.0, min(1.0, 1.0 - sum(rdiffs) / len(rdiffs)))

    components: dict[str, float] = {"p_dist": p_dist, "p_rank": p_rank}
    if p_refuse is not None:
        components["p_refuse"] = p_refuse
    components.update(_extended_from_scores(extended_scores))

    return RecomputedAggregates(
        n_questions=n,
        mean_jsd=mean_jsd,
        median_jsd=median_jsd,
        mean_kendall_tau=mean_tau,
        p_dist=p_dist,
        p_rank=p_rank,
        p_refuse=p_refuse,
        parity_two=0.5 * p_dist + 0.5 * p_rank,
        sps=synthbench_parity_score(components),
        components=components,
    )


def bootstrap_metric_cis(
    per_question: Any,
    *,
    extended_scores: Mapping[str, Any] | None = None,
    n_resamples: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Question-resampling bootstrap CIs for the recomputed metrics.

    Resamples per-question rows with replacement and recomputes the full
    composite per resample — the same convention as the recomputed ``sps``
    (P2-4 fix: the interval is on SPS itself, not on the 2-metric parity).
    Extended components (``p_sub`` / ``p_cond``) do not vary under question
    resampling, so they shift the SPS interval by a constant.

    Returns ``{metric: (ci_lower, ci_upper)}`` with 95% percentile intervals
    for ``p_dist``, ``p_rank``, ``sps`` and — when refusal data is present —
    ``p_refuse``. Returns ``{}`` when fewer than
    :data:`_BOOTSTRAP_MIN_QUESTIONS` usable rows exist: absence means
    *unknown*, never ``[0, 0]``.
    """
    import numpy as np

    rows = _usable_rows(per_question)
    n = len(rows)
    if n < _BOOTSTRAP_MIN_QUESTIONS:
        return {}

    jsd_arr = np.array([r[0] for r in rows], dtype=np.float64)
    tau_arr = np.array([r[1] for r in rows], dtype=np.float64)
    rdiff_arr = np.array(
        [r[2] if r[2] is not None else np.nan for r in rows], dtype=np.float64
    )
    has_refusal = bool(np.isfinite(rdiff_arr).any())

    extended = _extended_from_scores(extended_scores)
    ext_sum = sum(extended.values())
    n_ext = len(extended)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))

    p_dist_b = 1.0 - jsd_arr[idx].mean(axis=1)
    p_rank_b = (1.0 + tau_arr[idx].mean(axis=1)) / 2.0

    def _pct(values: "np.ndarray") -> tuple[float, float]:
        return (
            round(float(np.percentile(values, 2.5)), 6),
            round(float(np.percentile(values, 97.5)), 6),
        )

    cis: dict[str, tuple[float, float]] = {
        "p_dist": _pct(p_dist_b),
        "p_rank": _pct(p_rank_b),
    }

    if has_refusal:
        with np.errstate(invalid="ignore"):
            mean_rdiff_b = np.nanmean(rdiff_arr[idx], axis=1)
        p_refuse_b = np.clip(1.0 - mean_rdiff_b, 0.0, 1.0)
        # Resamples that drew no refusal-bearing rows contribute NaN; the
        # composite for those resamples falls back to the refusal-free form.
        refuse_ok = np.isfinite(p_refuse_b)
        if refuse_ok.any():
            cis["p_refuse"] = _pct(p_refuse_b[refuse_ok])
        sps_b = np.where(
            refuse_ok,
            (p_dist_b + p_rank_b + np.nan_to_num(p_refuse_b) + ext_sum) / (3 + n_ext),
            (p_dist_b + p_rank_b + ext_sum) / (2 + n_ext),
        )
    else:
        sps_b = (p_dist_b + p_rank_b + ext_sum) / (2 + n_ext)

    cis["sps"] = _pct(sps_b)
    return cis
