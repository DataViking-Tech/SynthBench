"""Validation behavior for gated-stripped result files (issue #308).

Committed ``leaderboard-results/*.json`` files carry no per-question
``human_distribution`` for gated datasets. The validator must:

* accept the stripped shape (marker + gated policy) at tier 1,
* WARN — never silently pass — when distribution-dependent recompute is
  skipped for lack of a canonical source,
* run the full recompute against canonical distributions when supplied,
  overriding any submitter-supplied copies (integrity upgrade).
"""

from __future__ import annotations

import copy

import pytest

from synthbench.metrics.distributional import jensen_shannon_divergence
from synthbench.metrics.ranking import kendall_tau_b
from synthbench.stats import question_set_hash
from synthbench.validation import (
    STRIPPED_FIELDS_KEY,
    is_stripped_gated,
    validate_submission,
)

_HUMAN = {
    "Q_A": {"A": 0.5, "B": 0.3, "C": 0.2},
    "Q_B": {"A": 0.7, "B": 0.2, "C": 0.1},
}
_MODEL = {
    "Q_A": {"A": 0.4, "B": 0.4, "C": 0.2},
    "Q_B": {"A": 0.6, "B": 0.3, "C": 0.1},
}


def _make_submission(dataset: str = "opinionsqa") -> dict:
    """A self-consistent submission WITH human distributions embedded."""
    per_question = []
    jsds, taus = [], []
    for key in ("Q_A", "Q_B"):
        jsd = jensen_shannon_divergence(_HUMAN[key], _MODEL[key])
        tau = kendall_tau_b(_HUMAN[key], _MODEL[key])
        jsds.append(jsd)
        taus.append(tau)
        per_question.append(
            {
                "key": key,
                "text": "q?",
                "options": ["A", "B", "C"],
                "human_distribution": dict(_HUMAN[key]),
                "model_distribution": dict(_MODEL[key]),
                "jsd": jsd,
                "kendall_tau": tau,
                "parity": (1.0 - jsd + (1.0 + tau) / 2.0) / 2.0,
                "n_samples": 10,
            }
        )
    mean_jsd = sum(jsds) / len(jsds)
    mean_tau = sum(taus) / len(taus)
    p_dist = 1.0 - mean_jsd
    p_rank = (1.0 + mean_tau) / 2.0
    return {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "config": {
            "dataset": dataset,
            "provider": "test-provider",
            "question_set_hash": question_set_hash(["Q_A", "Q_B"]),
        },
        "scores": {"sps": (p_dist + p_rank) / 2.0},
        "aggregate": {
            "mean_jsd": mean_jsd,
            "median_jsd": mean_jsd,
            "mean_kendall_tau": mean_tau,
            "composite_parity": 0.5 * p_dist + 0.5 * p_rank,
            "n_questions": 2,
        },
        "per_question": per_question,
    }


def _strip(data: dict) -> dict:
    stripped = copy.deepcopy(data)
    for q in stripped["per_question"]:
        q.pop("human_distribution", None)
    stripped[STRIPPED_FIELDS_KEY] = ["human_distribution"]
    return stripped


def test_is_stripped_gated_requires_marker_and_gated_policy():
    data = _make_submission("opinionsqa")
    assert not is_stripped_gated(data)  # no marker
    stripped = _strip(data)
    assert is_stripped_gated(stripped)
    # Full-tier dataset: marker is NOT honored.
    full = _strip(_make_submission("gss"))
    assert not is_stripped_gated(full)


def test_stripped_gated_file_validates_with_explicit_warning():
    report = validate_submission(_strip(_make_submission()))
    assert report.ok
    codes = [i.code for i in report.warnings]
    assert "RECOMPUTE_SKIPPED_NO_DISTRIBUTION" in codes
    # The aggregate recompute (scalar-based) still ran and identified the
    # composite convention.
    assert report.metadata.get("sps_convention") is not None


def test_missing_human_distribution_without_marker_is_schema_error():
    data = _make_submission()
    for q in data["per_question"]:
        q.pop("human_distribution")
    report = validate_submission(data)
    assert not report.ok
    assert any(i.code == "SCHEMA_MISSING" for i in report.errors)


def test_marker_on_full_tier_dataset_does_not_waive_schema():
    report = validate_submission(_strip(_make_submission("gss")))
    assert not report.ok
    assert any(i.code == "SCHEMA_MISSING" for i in report.errors)


def test_canonical_rehydration_restores_full_recompute():
    report = validate_submission(
        _strip(_make_submission()), canonical_distributions=_HUMAN
    )
    assert report.ok
    assert not report.warnings
    assert report.metadata.get("recompute_source") == "canonical"


def test_canonical_rehydration_catches_fabricated_metrics():
    stripped = _strip(_make_submission())
    stripped["per_question"][0]["jsd"] = 0.9  # fabricated
    report = validate_submission(stripped, canonical_distributions=_HUMAN)
    assert not report.ok
    assert any(i.code == "PER_Q_JSD" for i in report.errors)


def test_canonical_overrides_submitter_supplied_distributions():
    """Tampered human_distribution consistent with fabricated metrics is
    still caught: the canonical copy wins in trusted contexts."""
    data = _make_submission()
    row = data["per_question"][0]
    # Attacker sets human == model so recompute-from-submitted yields jsd 0.
    row["human_distribution"] = dict(row["model_distribution"])
    row["jsd"] = 0.0
    row["kendall_tau"] = 1.0
    # A competent attacker keeps the aggregates internally consistent too.
    jsds = [q["jsd"] for q in data["per_question"]]
    taus = [q["kendall_tau"] for q in data["per_question"]]
    mean_jsd = sum(jsds) / len(jsds)
    mean_tau = sum(taus) / len(taus)
    p_dist, p_rank = 1.0 - mean_jsd, (1.0 + mean_tau) / 2.0
    data["aggregate"].update(
        mean_jsd=mean_jsd,
        median_jsd=mean_jsd,
        mean_kendall_tau=mean_tau,
        composite_parity=0.5 * p_dist + 0.5 * p_rank,
    )
    data["scores"]["sps"] = (p_dist + p_rank) / 2.0
    report_untrusted = validate_submission(data)
    # Self-consistent per-question metrics — only aggregate checks can
    # complain here; the per-question fabrication passes without canonical.
    assert not any(
        i.code in ("PER_Q_JSD", "PER_Q_TAU") for i in report_untrusted.errors
    )
    report_trusted = validate_submission(data, canonical_distributions=_HUMAN)
    assert any(i.code in ("PER_Q_JSD", "PER_Q_TAU") for i in report_trusted.errors)


def test_canonical_rehydration_does_not_mutate_input():
    stripped = _strip(_make_submission())
    validate_submission(stripped, canonical_distributions=_HUMAN)
    assert all("human_distribution" not in q for q in stripped["per_question"])


@pytest.mark.parametrize("dataset", ["opinionsqa", "subpop", "globalopinionqa"])
def test_gated_datasets_recognized(dataset):
    assert is_stripped_gated(_strip(_make_submission(dataset)))
