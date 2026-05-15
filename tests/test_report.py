"""Tests for score card generation."""

from __future__ import annotations

import json

import pytest

from synthbench.runner import BenchmarkResult, QuestionResult
from synthbench.report import to_json, to_markdown


@pytest.fixture
def sample_result():
    questions = [
        QuestionResult(
            key="Q1",
            text="Do you support X?",
            options=["Yes", "No"],
            human_distribution={"Yes": 0.6, "No": 0.4},
            model_distribution={"Yes": 0.7, "No": 0.3},
            jsd=0.015,
            kendall_tau=1.0,
            parity=0.95,
            n_samples=30,
        ),
        QuestionResult(
            key="Q2",
            text="How do you feel about Y?",
            options=["Good", "Neutral", "Bad"],
            human_distribution={"Good": 0.3, "Neutral": 0.4, "Bad": 0.3},
            model_distribution={"Good": 0.5, "Neutral": 0.3, "Bad": 0.2},
            jsd=0.08,
            kendall_tau=0.67,
            parity=0.78,
            n_samples=30,
        ),
    ]
    return BenchmarkResult(
        provider_name="test/mock",
        dataset_name="test",
        questions=questions,
        config={"samples_per_question": 30, "n_evaluated": 2},
        elapsed_seconds=5.2,
    )


def test_to_json_structure(sample_result):
    data = to_json(sample_result)
    assert data["benchmark"] == "synthbench"
    assert "version" in data
    assert "timestamp" in data
    assert data["config"]["provider"] == "test/mock"
    assert data["aggregate"]["n_questions"] == 2
    assert len(data["per_question"]) == 2


def test_to_json_has_scores(sample_result):
    data = to_json(sample_result)
    assert "scores" in data
    scores = data["scores"]
    assert "sps" in scores
    assert "p_dist" in scores
    assert "p_rank" in scores
    assert "p_refuse" in scores


def test_to_json_per_question_has_refusal(sample_result):
    data = to_json(sample_result)
    for q in data["per_question"]:
        assert "model_refusal_rate" in q
        assert "human_refusal_rate" in q


def test_to_json_round_trip(sample_result):
    data = to_json(sample_result)
    serialized = json.dumps(data)
    parsed = json.loads(serialized)
    assert parsed["aggregate"]["mean_jsd"] == data["aggregate"]["mean_jsd"]


def test_to_markdown_contains_scores(sample_result):
    md = to_markdown(sample_result)
    assert "SynthBench Score Card" in md
    assert "test/mock" in md
    assert "Mean JSD" in md
    assert "SPS" in md
    assert "P_dist" in md
    assert "P_rank" in md
    assert "P_refuse" in md


# ---------------------------------------------------------------------------
# Per-question latency aggregation (sb-293)
# ---------------------------------------------------------------------------


def _latency_result(latencies: list[float | None]) -> BenchmarkResult:
    """Build a minimal BenchmarkResult populated with the given latencies."""
    questions = [
        QuestionResult(
            key=f"Q{i}",
            text=f"q{i}",
            options=["A", "B"],
            human_distribution={"A": 0.5, "B": 0.5},
            model_distribution={"A": 0.5, "B": 0.5},
            jsd=0.0,
            kendall_tau=1.0,
            parity=1.0,
            n_samples=1,
            latency_seconds=lat,
        )
        for i, lat in enumerate(latencies)
    ]
    return BenchmarkResult(
        provider_name="test/mock",
        dataset_name="test",
        questions=questions,
        config={},
        elapsed_seconds=sum(x for x in latencies if x is not None),
    )


def test_latency_aggregate_present_when_all_questions_measured():
    """All-measured runs surface p50/p95/mean and source='measured'."""
    result = _latency_result([0.5, 1.0, 1.5, 2.0, 2.5])
    data = to_json(result)
    block = data["aggregate"].get("latency_seconds")
    assert block is not None
    assert block["source"] == "measured"
    assert block["n"] == 5
    assert block["mean"] == pytest.approx(1.5)
    # Nearest-rank: p50 of 5 ordered samples → index 2 (1.5)
    assert block["p50"] == pytest.approx(1.5)
    # p95 of 5 → index 4 (2.5)
    assert block["p95"] == pytest.approx(2.5)


def test_latency_aggregate_partial_when_only_some_measured():
    """Mixed measurement → source='partial', percentiles over the populated subset."""
    result = _latency_result([0.5, None, 1.5, None, 2.5])
    data = to_json(result)
    block = data["aggregate"]["latency_seconds"]
    assert block["source"] == "partial"
    assert block["n"] == 3
    assert block["p50"] == pytest.approx(1.5)


def test_latency_aggregate_absent_when_no_measurements():
    """Pre-instrumentation runs (no latencies) emit no latency block at all."""
    result = _latency_result([None, None])
    data = to_json(result)
    assert "latency_seconds" not in data["aggregate"]


def test_latency_appears_in_per_question_records():
    """Per-question records carry the latency field when present."""
    result = _latency_result([0.42, None])
    data = to_json(result)
    pq = data["per_question"]
    assert pq[0]["latency_seconds"] == pytest.approx(0.42)
    assert "latency_seconds" not in pq[1]
