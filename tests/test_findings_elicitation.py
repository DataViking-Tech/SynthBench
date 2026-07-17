"""Unit tests for the elicitation-mode (natural vs schema-forced) finding."""

from __future__ import annotations

import pytest

from synthbench.findings import _build_elicitation_comparison, _parse_failure_rate

_QHASH = "a" * 40
_PROVIDER = "synthpanel/openrouter/anthropic/claude-haiku-4-5"


def _q(key: str, jsd: float, tau: float, refusal: float = 0.0) -> dict:
    return {
        "key": key,
        "jsd": jsd,
        "kendall_tau": tau,
        "model_refusal_rate": refusal,
        "human_refusal_rate": 0.02,
    }


def _result(
    provider: str,
    per_question: list[dict],
    *,
    elicitation: str | None = None,
    prompt_template: str | None = None,
    parse_failure_rate: float | None = None,
    question_set_hash: str = _QHASH,
    samples: int = 30,
) -> dict:
    config = {
        "provider": provider,
        "dataset": "gss",
        "samples_per_question": samples,
        "n_evaluated": len(per_question),
        "question_set_hash": question_set_hash,
        "temperature": None,
        "refusal_detector_version": 2,
    }
    if elicitation is not None:
        config["elicitation"] = elicitation
        config["prompt_template"] = prompt_template or elicitation
    if parse_failure_rate is not None:
        config["parse_failure_rate"] = parse_failure_rate
    return {
        "benchmark": "synthbench",
        "config": config,
        "scores": {},
        "aggregate": {"n_questions": len(per_question)},
        "per_question": per_question,
    }


def _fixture_pair() -> tuple[dict, dict]:
    natural = _result(
        _PROVIDER,
        [_q("GSS_A", 0.2, 0.5), _q("GSS_B", 0.3, 0.4)],
        parse_failure_rate=0.016,
    )
    structured = _result(
        f"{_PROVIDER} tpl=structured",
        [_q("GSS_A", 0.3, 0.6), _q("GSS_B", 0.4, 0.5)],
        elicitation="structured",
        parse_failure_rate=0.0,
    )
    return natural, structured


def test_matched_pair_emits_arms_and_deltas():
    natural, structured = _fixture_pair()
    rows = _build_elicitation_comparison([natural, structured])
    assert len(rows) == 1
    row = rows[0]
    assert row["model"] == "SynthPanel (Haiku 4.5)"
    assert row["framework"] == "product"
    assert row["dataset"] == "gss"
    assert row["elicitation"] == "structured"
    assert row["template"] == "structured"
    assert row["n_questions"] == 2
    assert row["samples_per_question"] == 30
    assert row["refusal_detector_version"] == 2

    # Recomputed from the fixture rows: p_dist = 1 - mean_jsd,
    # p_rank = (1 + mean_tau) / 2, p_refuse = 1 - mean |refusal diff|.
    assert row["natural"]["p_dist"] == pytest.approx(0.75)
    assert row["structured"]["p_dist"] == pytest.approx(0.65)
    assert row["natural"]["p_rank"] == pytest.approx(0.725)
    assert row["structured"]["p_rank"] == pytest.approx(0.775)
    assert row["natural"]["p_refuse"] == pytest.approx(0.98)
    assert row["natural"]["parse_failure_rate"] == pytest.approx(0.016)
    assert row["structured"]["parse_failure_rate"] == 0.0

    # Deltas (structured - natural) are exact over the rounded arm values.
    for metric, delta in row["delta"].items():
        assert delta == pytest.approx(
            round(row["structured"][metric] - row["natural"][metric], 6)
        )
    assert row["delta"]["p_dist"] == pytest.approx(-0.1)
    assert row["delta"]["parse_failure_rate"] == pytest.approx(-0.016)


def test_unmatched_variant_emits_nothing():
    _, structured = _fixture_pair()
    assert _build_elicitation_comparison([structured]) == []
    natural, _ = _fixture_pair()
    assert _build_elicitation_comparison([natural]) == []
    assert _build_elicitation_comparison([]) == []


def test_identity_mismatch_is_not_a_pair():
    natural, structured = _fixture_pair()
    # Different question set: not the same measured configuration.
    other = _result(
        f"{_PROVIDER} tpl=structured",
        [_q("GSS_A", 0.3, 0.6), _q("GSS_B", 0.4, 0.5)],
        elicitation="structured",
        question_set_hash="b" * 40,
    )
    assert _build_elicitation_comparison([natural, other]) == []
    # Different question count under the same hash: skipped defensively.
    shorter = _result(
        f"{_PROVIDER} tpl=structured",
        [_q("GSS_A", 0.3, 0.6)],
        elicitation="structured",
    )
    assert _build_elicitation_comparison([natural, shorter]) == []
    # Sanity: the true counterpart still pairs.
    assert len(_build_elicitation_comparison([natural, structured, other])) == 1


def test_parse_failure_rate_fallback_from_aggregate():
    result = _result(_PROVIDER, [_q("GSS_A", 0.2, 0.5)], samples=10)
    assert _parse_failure_rate(result) is None
    result["aggregate"]["n_parse_failures"] = 2
    assert _parse_failure_rate(result) == pytest.approx(0.2)
    # Recorded config value wins over the aggregate-derived fallback.
    result["config"]["parse_failure_rate"] = 0.05
    assert _parse_failure_rate(result) == pytest.approx(0.05)
