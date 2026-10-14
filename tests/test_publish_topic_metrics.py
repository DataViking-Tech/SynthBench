"""Per-topic SPS breakdown in publish.py: routing taxonomy, full SPS."""

from __future__ import annotations

import pytest

from synthbench.publish import (
    _build_entry,
    _compute_topic_metrics,
    _compute_topic_scores,
)
from synthbench.recompute import recompute_aggregates


def _q(
    text: str,
    *,
    jsd: float,
    tau: float,
    m_ref: float | None = 0.0,
    h_ref: float | None = 0.0,
    key: str | None = None,
    parity: float = 0.5,
) -> dict:
    row = {
        "text": text,
        "parity": parity,
        "jsd": jsd,
        "kendall_tau": tau,
        "model_refusal_rate": m_ref,
        "human_refusal_rate": h_ref,
    }
    if key:
        row["key"] = key
    return row


def test_empty_input_returns_empty():
    assert _compute_topic_metrics([]) == {}


def test_full_sps_includes_p_refuse():
    pq = [
        _q(
            "Did you vote in the last election?",
            jsd=0.10,
            tau=0.5,
            m_ref=0.1,
            h_ref=0.2,
        ),
        _q("How often do you vote in elections?", jsd=0.30, tau=0.1),
    ]
    m = _compute_topic_metrics(pq)["politics"]
    assert m["n"] == 2
    assert m["p_dist"] == pytest.approx(0.8)
    assert m["p_rank"] == pytest.approx(0.65)
    assert m["p_refuse"] == pytest.approx(0.95)
    # Full SPS = mean of the three components, not the stored 2-metric parity.
    assert m["sps"] == pytest.approx((0.8 + 0.65 + 0.95) / 3, abs=1e-6)


def test_sps_matches_headline_on_same_questions():
    """A single-topic run's topic SPS equals its recomputed headline SPS."""
    pq = [
        _q("Did you vote?", jsd=0.12, tau=0.4, m_ref=0.0, h_ref=0.05),
        _q("Who should be president?", jsd=0.2, tau=0.6, m_ref=0.1, h_ref=0.02),
        _q("Do you support Congress?", jsd=0.05, tau=-0.2, m_ref=None, h_ref=None),
    ]
    scores = {"p_cond": 0.7}
    headline = recompute_aggregates(pq, extended_scores=scores)
    m = _compute_topic_metrics(pq, extended_scores=scores)["politics"]
    assert m["sps"] == pytest.approx(headline.sps, abs=1e-6)


def test_topics_are_separated_and_ordered():
    pq = [
        _q("How is your health?", jsd=0.4, tau=-0.2),
        _q("Did you vote?", jsd=0.05, tau=0.9),
    ]
    metrics = _compute_topic_metrics(pq)
    assert list(metrics) == ["politics", "science-health"]
    assert metrics["politics"]["n"] == 1
    assert metrics["science-health"]["n"] == 1


def test_committed_label_used_over_text():
    # GSS_ABANY is labeled in the committed GSS file; the text here would
    # otherwise classify as science-health.
    from synthbench.topics import label_for

    topic = label_for("gss", "GSS_ABANY")
    pq = [_q("How is your health?", jsd=0.1, tau=0.1, key="GSS_ABANY")]
    assert list(_compute_topic_metrics(pq, dataset="gss")) == [topic]


def test_unclassifiable_rows_skipped():
    pq = [
        {"text": "", "jsd": 0.0, "kendall_tau": 1.0},
        _q("Did you vote?", jsd=0.2, tau=0.0),
    ]
    metrics = _compute_topic_metrics(pq)
    assert list(metrics) == ["politics"]
    assert metrics["politics"]["n"] == 1


def test_rows_without_metrics_skipped():
    pq = [{"text": "Did you vote?", "parity": 0.7}]
    assert _compute_topic_metrics(pq) == {}


def test_p_refuse_absent_without_refusal_data():
    pq = [_q("Did you vote?", jsd=0.2, tau=0.2, m_ref=None, h_ref=None)]
    m = _compute_topic_metrics(pq)["politics"]
    assert "p_refuse" not in m
    assert m["sps"] == pytest.approx((0.8 + 0.6) / 2)


def test_p_refuse_clamped_nonnegative():
    pq = [_q("Did you vote?", jsd=0.0, tau=0.0, m_ref=1.0, h_ref=0.0)]
    assert _compute_topic_metrics(pq)["politics"]["p_refuse"] == 0.0


def test_topic_scores_mirror_metrics():
    pq = [
        _q("Did you vote?", jsd=0.1, tau=0.3, m_ref=0.2, h_ref=0.0),
        _q("How is your health?", jsd=0.3, tau=0.1),
    ]
    metrics = _compute_topic_metrics(pq)
    assert _compute_topic_scores(pq) == {t: m["sps"] for t, m in metrics.items()}


def test_build_entry_topic_fields_use_ids():
    pq = [
        _q("Did you vote?", jsd=0.1, tau=0.3, key="K1"),
        _q("How is your health?", jsd=0.3, tau=0.1, key="K2"),
    ]
    r = {
        "config": {"provider": "openrouter/openai/gpt-4o-mini", "dataset": "custom"},
        "per_question": pq,
    }
    entry = _build_entry(r, 1)
    assert set(entry["topic_metrics"]) == {"politics", "science-health"}
    assert (
        entry["topic_scores"]["politics"] == entry["topic_metrics"]["politics"]["sps"]
    )
