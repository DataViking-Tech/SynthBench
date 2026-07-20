"""Unit tests for the nonresponse-fidelity findings computation."""

from __future__ import annotations

from synthbench.findings import (
    _build_nonresponse_fidelity,
    _build_sensitive_topic_sidestepping,
    _nonresponse_mass,
)


def _result(provider: str, per_question: list[dict], dataset: str = "gss") -> dict:
    return {
        "benchmark": "synthbench",
        "config": {
            "provider": provider,
            "dataset": dataset,
            "samples_per_question": 30,
            "n_evaluated": len(per_question),
        },
        "scores": {"sps": 0.5},
        "aggregate": {"n_questions": len(per_question)},
        "per_question": per_question,
    }


def _q(key: str, model_dk: float, human_dk: float, refusal: float = 0.0) -> dict:
    return {
        "key": key,
        "model_distribution": {"yes": 1 - model_dk, "don't know": model_dk},
        "human_distribution": {"yes": 1 - human_dk, "don't know": human_dk},
        "model_refusal_rate": refusal,
        "human_refusal_rate": 0.0,
    }


def test_nonresponse_mass_counts_dk_options_and_refusals():
    dist = {"yes": 0.5, "don't know": 0.2, "No answer": 0.1, "Refused": 0.1}
    assert _nonresponse_mass(dist, 0.05) == 0.45
    assert _nonresponse_mass(None, 0.0) == 0.0
    # Substantive-but-DK-worded options count as explicit nonresponse mass.
    assert _nonresponse_mass({"don't know, no way to find out": 0.3}, 0.0) == 0.3


def test_build_nonresponse_fidelity_rows_and_top_items():
    r = _result(
        "openrouter/google/gemini-2.5-flash",
        [
            _q("GSS_POSTLIFE", 1.0, 0.135),
            _q("GSS_NATRACE", 0.8, 0.044),
            _q("GSS_HEALTH", 0.0, 0.01),
        ],
    )
    baseline = _result("random-baseline", [_q("GSS_POSTLIFE", 0.5, 0.135)])
    rows = _build_nonresponse_fidelity([r, baseline])
    assert len(rows) == 1  # baselines excluded
    row = rows[0]
    assert row["dataset"] == "gss"
    assert row["n_questions"] == 3
    assert row["top_overselected"][0]["key"] == "GSS_POSTLIFE"
    assert all(i["gap"] > 0 for i in row["top_overselected"])
    assert 0 < row["mean_abs_nonresponse_gap"] < 1


def test_build_nonresponse_fidelity_skips_stripped_runs():
    stripped_q = _q("Q1", 0.5, 0.1)
    stripped_q.pop("human_distribution")
    rows = _build_nonresponse_fidelity(
        [_result("openrouter/google/gemini-2.5-flash", [stripped_q])]
    )
    assert rows == []


def test_sensitive_topic_note_derived_from_worst_raw_row():
    rows = [
        {
            "provider": "Althing (Haiku 4.5)",
            "framework": "product",
            "dataset": "gss",
            "n_questions": 75,
            "mean_abs_nonresponse_gap": 0.9,
            "mean_model_nonresponse_mass": 0.9,
            "mean_human_nonresponse_mass": 0.05,
            "top_overselected": [],
        },
        {
            "provider": "Gemini 2.5 Flash",
            "framework": "raw",
            "dataset": "gss",
            "n_questions": 75,
            "mean_abs_nonresponse_gap": 0.126,
            "mean_model_nonresponse_mass": 0.15,
            "mean_human_nonresponse_mass": 0.05,
            "top_overselected": [
                {
                    "key": "GSS_FEPRESCH",
                    "model_mass": 0.97,
                    "human_mass": 0.02,
                    "gap": 0.95,
                }
            ],
        },
    ]
    note = _build_sensitive_topic_sidestepping(rows)
    assert note is not None
    assert note["provider"] == "Gemini 2.5 Flash"  # raw rows only
    assert note["items"][0]["key"] == "GSS_FEPRESCH"
    assert _build_sensitive_topic_sidestepping([]) is None
