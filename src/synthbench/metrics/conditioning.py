"""Conditioning fidelity metric (P_cond).

Uses JSD to measure how much persona conditioning improves alignment
with human response distributions.
"""

from __future__ import annotations

from synthbench.metrics.distributional import jensen_shannon_divergence


def conditioning_fidelity(
    conditioned_dist: dict[str, float],
    unconditioned_dist: dict[str, float],
    human_dist: dict[str, float],
) -> float:
    """Compute conditioning fidelity via JSD improvement.

    P_cond = JSD(unconditioned, human) - JSD(conditioned, human), floored at 0.

    Measures how much persona conditioning moves the provider's output
    closer to the human reference distribution compared to the
    unconditioned baseline.

    Args:
        conditioned_dist: Provider response distribution with persona
            conditioning applied.
        unconditioned_dist: Provider response distribution with a generic
            "You are a survey respondent" prompt (no persona conditioning).
        human_dist: Human reference distribution for this question/group.

    Returns:
        P_cond in [0, 1]. Higher = conditioning improved alignment.
        Returns 0.0 if conditioning made things worse or had no effect.
    """
    jsd_unconditioned = jensen_shannon_divergence(unconditioned_dist, human_dist)
    jsd_conditioned = jensen_shannon_divergence(conditioned_dist, human_dist)

    return max(0.0, jsd_unconditioned - jsd_conditioned)
