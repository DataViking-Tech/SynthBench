"""Subgroup consistency metric (P_sub)."""

from __future__ import annotations

import math


def subgroup_consistency(group_scores: dict[str, float]) -> float:
    """Compute subgroup consistency: P_sub = 1 - CV(group_scores).

    CV (coefficient of variation) = std / mean. A provider with equal
    accuracy across all demographic groups gets P_sub close to 1.
    A provider accurate for some groups but poor for others gets P_sub < 1.

    Args:
        group_scores: Mapping of group name to alignment score (e.g., P_dist
            per demographic group). Values should be in [0, 1].

    Returns:
        P_sub in [0, 1]. Higher = more consistent across groups.
        Returns 1.0 if fewer than 2 groups (no dispersion measurable).
    """
    if len(group_scores) < 2:
        return 1.0

    values = list(group_scores.values())
    n = len(values)
    mean = sum(values) / n

    if mean == 0.0:
        return 0.0

    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance)
    cv = std / mean

    return max(0.0, min(1.0, 1.0 - cv))


def p_sub(group_scores: list[float]) -> float:
    """Compute subgroup parity from a list of per-group scores.

    P_sub = 1 - CV(group_scores) where CV = std / mean.

    Convenience wrapper over subgroup_consistency that accepts a list
    instead of a dict.

    Args:
        group_scores: Per-group alignment scores (e.g., P_dist per group).

    Returns:
        P_sub in [0, 1]. Higher = more consistent across groups.
        Returns 1.0 if fewer than 2 scores.
    """
    if len(group_scores) < 2:
        return 1.0
    named = {str(i): v for i, v in enumerate(group_scores)}
    return subgroup_consistency(named)
