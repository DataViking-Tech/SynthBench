"""Tests for per-topic SPS component breakdown in publish.py."""

from __future__ import annotations

from synthbench.publish import _compute_topic_metrics


def _q(
    text: str,
    *,
    parity: float,
    jsd: float,
    tau: float,
    m_ref: float = 0.0,
    h_ref: float = 0.0,
) -> dict:
    return {
        "text": text,
        "parity": parity,
        "jsd": jsd,
        "kendall_tau": tau,
        "model_refusal_rate": m_ref,
        "human_refusal_rate": h_ref,
    }


def test_empty_input_returns_empty():
    assert _compute_topic_metrics([]) == {}


def test_metrics_match_aggregate_formulas():
    # Two "Politics & Governance" questions (keyword: vote / election).
    pq = [
        _q(
            "Did you vote in the last election?",
            parity=0.8,
            jsd=0.10,
            tau=0.5,
            m_ref=0.1,
            h_ref=0.2,
        ),
        _q(
            "How often do you vote in elections?",
            parity=0.6,
            jsd=0.30,
            tau=0.1,
            m_ref=0.0,
            h_ref=0.0,
        ),
    ]
    metrics = _compute_topic_metrics(pq)
    assert "Politics & Governance" in metrics
    m = metrics["Politics & Governance"]

    assert m["n"] == 2
    assert m["sps"] == 0.7  # mean of 0.8, 0.6
    # p_dist = 1 - mean(jsd) = 1 - 0.2
    assert m["p_dist"] == 0.8
    # p_rank = (1 + mean(tau)) / 2 = (1 + 0.3) / 2
    assert m["p_rank"] == 0.65
    # p_refuse = 1 - mean(|0.1 - 0.2|, |0 - 0|) = 1 - 0.05
    assert m["p_refuse"] == 0.95


def test_missing_text_skipped():
    # First row has no text; should be ignored.
    pq = [
        {"text": "", "parity": 1.0, "jsd": 0.0, "kendall_tau": 1.0},
        _q("Did you vote?", parity=0.5, jsd=0.2, tau=0.0),
    ]
    metrics = _compute_topic_metrics(pq)
    assert len(metrics) == 1
    topic = next(iter(metrics))
    assert metrics[topic]["n"] == 1
    assert metrics[topic]["sps"] == 0.5


def test_topics_are_separated():
    pq = [
        _q("Did you vote?", parity=0.9, jsd=0.05, tau=0.9),
        _q("How is your health?", parity=0.3, jsd=0.4, tau=-0.2),
    ]
    metrics = _compute_topic_metrics(pq)
    assert metrics["Politics & Governance"]["sps"] == 0.9
    assert metrics["Health & Science"]["sps"] == 0.3
    assert metrics["Politics & Governance"]["n"] == 1
    assert metrics["Health & Science"]["n"] == 1


def test_p_refuse_clamped_nonnegative():
    # Large refusal divergence should floor at 0.0.
    pq = [
        _q("Did you vote?", parity=0.5, jsd=0.0, tau=0.0, m_ref=1.0, h_ref=0.0),
    ]
    metrics = _compute_topic_metrics(pq)
    m = metrics["Politics & Governance"]
    assert m["p_refuse"] == 0.0


def test_missing_optional_fields_produces_sps_only():
    # A topic with only parity (no jsd/tau/refusal) still gets SPS + n.
    pq = [{"text": "Did you vote?", "parity": 0.7}]
    metrics = _compute_topic_metrics(pq)
    m = metrics["Politics & Governance"]
    assert m["sps"] == 0.7
    assert m["n"] == 1
    assert "p_dist" not in m
    assert "p_rank" not in m
    assert "p_refuse" not in m
