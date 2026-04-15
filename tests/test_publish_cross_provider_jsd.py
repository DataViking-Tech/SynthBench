"""Tests for cross-provider JSD matrix in publish.py (HBR Part 1)."""

from __future__ import annotations

import math

from synthbench.metrics.distributional import jensen_shannon_divergence
from synthbench.publish import _compute_cross_provider_concordance


def _result(
    provider: str,
    dataset: str,
    *,
    per_question: list[dict],
    mean_jsd: float = 0.0,
) -> dict:
    """Build a minimal deduped-result shape used by the publish pipeline."""
    return {
        "config": {"provider": provider, "dataset": dataset},
        "aggregate": {"mean_jsd": mean_jsd},
        "per_question": per_question,
    }


def _pq(key: str, dist: dict[str, float]) -> dict:
    return {"key": key, "model_distribution": dist}


def test_empty_input_returns_empty():
    assert _compute_cross_provider_concordance([]) == {}


def test_single_model_dataset_skipped():
    # With only one model per dataset, no pairwise matrix is meaningful.
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", {"A": 0.5, "B": 0.5})],
        )
    ]
    out = _compute_cross_provider_concordance(results)
    assert out == {}


def test_matrix_symmetry_and_diagonal_zero():
    # Two raw models, two shared questions.
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[
                _pq("q1", {"A": 1.0, "B": 0.0}),
                _pq("q2", {"A": 0.5, "B": 0.5}),
            ],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[
                _pq("q1", {"A": 0.5, "B": 0.5}),
                _pq("q2", {"A": 0.5, "B": 0.5}),
            ],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    assert "opinionsqa" in out
    block = out["opinionsqa"]
    models = block["models"]
    matrix = block["matrix"]
    n = len(models)
    assert n == 2
    # Diagonal is zero by definition.
    for i in range(n):
        assert matrix[i][i] == 0.0
    # Symmetric.
    for i in range(n):
        for j in range(n):
            assert matrix[i][j] == matrix[j][i]


def test_per_pair_jsd_correctness():
    # Build distributions where the pairwise JSD is analytically known and
    # reproduce it by invoking jensen_shannon_divergence directly.
    a = {"A": 1.0, "B": 0.0}
    b = {"A": 0.0, "B": 1.0}
    c = {"A": 0.5, "B": 0.5}

    # Haiku gives (a, c); GPT-4o-mini gives (b, c).
    # Pairwise JSD across two questions:
    #   JSD(a, b) at q1, JSD(c, c) == 0 at q2
    expected_pair = (jensen_shannon_divergence(a, b) + 0.0) / 2
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", a), _pq("q2", c)],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q1", b), _pq("q2", c)],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    matrix = out["opinionsqa"]["matrix"]
    assert math.isclose(matrix[0][1], round(expected_pair, 6), rel_tol=1e-6)


def test_missing_shared_questions_returns_none():
    # Two models whose question sets do not overlap produce a None cell.
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q_a", {"A": 1.0, "B": 0.0})],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q_b", {"A": 1.0, "B": 0.0})],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    matrix = out["opinionsqa"]["matrix"]
    assert matrix[0][1] is None
    assert matrix[1][0] is None
    # mean_cross_model_jsd falls back to None when every pair is missing.
    assert out["opinionsqa"]["mean_cross_model_jsd"] is None


def test_partial_missing_averages_over_shared_only():
    # Haiku has q1,q2; GPT has q1,q3. Shared set is {q1}.
    a = {"A": 1.0, "B": 0.0}
    b = {"A": 0.0, "B": 1.0}
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", a), _pq("q2", a)],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q1", b), _pq("q3", b)],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    matrix = out["opinionsqa"]["matrix"]
    # Only q1 is shared → pair JSD collapses to JSD(a, b).
    assert math.isclose(
        matrix[0][1], round(jensen_shannon_divergence(a, b), 6), rel_tol=1e-6
    )


def test_non_raw_frameworks_excluded():
    # Baselines and products should not appear in the matrix.
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", {"A": 1.0, "B": 0.0})],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q1", {"A": 0.0, "B": 1.0})],
        ),
        _result(
            "random-baseline",
            "opinionsqa",
            per_question=[_pq("q1", {"A": 0.5, "B": 0.5})],
        ),
        _result(
            "synthpanel/claude-haiku-4-5-20251001",
            "opinionsqa",
            per_question=[_pq("q1", {"A": 0.9, "B": 0.1})],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    models = out["opinionsqa"]["models"]
    # Only the two raw LLMs survive the framework filter.
    assert len(models) == 2
    assert all("SynthPanel" not in m for m in models)
    assert all("baseline" not in m.lower() for m in models)


def test_quadrant_summary_fields():
    # Verify the HBR "trendslop quadrant" 1-D summary pair.
    a = {"A": 1.0, "B": 0.0}
    b = {"A": 0.0, "B": 1.0}
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", a)],
            mean_jsd=0.10,
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q1", b)],
            mean_jsd=0.20,
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    block = out["opinionsqa"]
    # Mean off-diagonal across the single pair.
    expected_cross = round(jensen_shannon_divergence(a, b), 6)
    assert block["mean_cross_model_jsd"] == expected_cross
    # Mean of per-run mean_jsd vs human.
    assert block["mean_human_jsd"] == 0.15


def test_multiple_datasets_isolated():
    # Keep dataset blocks independent of each other.
    d1 = {"A": 1.0, "B": 0.0}
    d2 = {"A": 0.0, "B": 1.0}
    results = [
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "opinionsqa",
            per_question=[_pq("q1", d1)],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "opinionsqa",
            per_question=[_pq("q1", d2)],
        ),
        _result(
            "openrouter/anthropic/claude-haiku-4-5",
            "subpop",
            per_question=[_pq("q1", d1)],
        ),
        _result(
            "openrouter/openai/gpt-4o-mini",
            "subpop",
            per_question=[_pq("q1", d1)],
        ),
    ]
    out = _compute_cross_provider_concordance(results)
    assert set(out.keys()) == {"opinionsqa", "subpop"}
    # opinionsqa pair diverges; subpop pair agrees → lower off-diagonal.
    assert out["opinionsqa"]["matrix"][0][1] > out["subpop"]["matrix"][0][1]
    assert out["subpop"]["matrix"][0][1] == 0.0
