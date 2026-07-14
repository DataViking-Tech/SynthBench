"""Tests for the per-entry demographic_scorecard block (issue #255).

The scorecard restructures a run's ``demographic_breakdown`` (SubPOP
conditioned runs) into a stable per-dimension API shape: per subgroup a
score (subgroup p_dist), CI slots (null until subgroup bootstrap CIs land),
n, and the source dataset. Entries without demographic data publish an
explicit ``null``.
"""

from __future__ import annotations

from synthbench.publish import (
    _build_demographic_scorecard,
    _build_entry,
    _demographic_dimension_label,
)


def _group(attr: str, group: str, p_dist: float, p_cond: float, n: int) -> dict:
    return {
        "attribute": attr,
        "group": group,
        "p_dist": p_dist,
        "p_cond": p_cond,
        "n_questions": n,
    }


def _run(demographic_breakdown: dict | None) -> dict:
    """Minimal publishable run: per_question rows so recompute succeeds."""
    r = {
        "benchmark": "synthbench",
        "config": {
            "dataset": "subpop",
            "provider": "synthpanel/openrouter/anthropic/claude-haiku-4-5",
            "n_evaluated": 2,
        },
        "scores": {},
        "aggregate": {},
        "per_question": [
            {"text": "Did you vote?", "parity": 0.8, "jsd": 0.1, "kendall_tau": 0.5},
            {
                "text": "How is your health?",
                "parity": 0.6,
                "jsd": 0.3,
                "kendall_tau": 0.1,
            },
        ],
    }
    if demographic_breakdown is not None:
        r["demographic_breakdown"] = demographic_breakdown
    return r


def test_scorecard_none_when_no_breakdown():
    assert _build_demographic_scorecard(_run(None)) is None
    assert _build_demographic_scorecard(_run({})) is None


def test_scorecard_none_when_breakdown_has_no_usable_rows():
    # Attribute present but empty list / malformed rows → no fabricated cells.
    assert _build_demographic_scorecard(_run({"CREGION": []})) is None
    assert _build_demographic_scorecard(_run({"CREGION": "oops"})) is None
    assert (
        _build_demographic_scorecard(
            _run({"CREGION": [{"attribute": "CREGION", "group": "West"}]})
        )
        is None
    )


def test_scorecard_shape_with_real_style_breakdown():
    breakdown = {
        "CREGION": [
            _group("CREGION", "Northeast", 0.622784, 0.018402, 100),
            _group("CREGION", "South", 0.640679, 0.035833, 100),
        ],
        "EDUCATION": [
            _group("EDUCATION", "College graduate/some postgrad", 0.61, 0.02, 100),
        ],
    }
    card = _build_demographic_scorecard(_run(breakdown))
    assert card is not None
    assert card["dataset"] == "subpop"
    # Dimensions sorted by attribute for deterministic output.
    assert [d["attribute"] for d in card["dimensions"]] == ["CREGION", "EDUCATION"]

    cregion = card["dimensions"][0]
    assert cregion["label"] == "Geography (US Census region)"
    assert len(cregion["groups"]) == 2
    ne = cregion["groups"][0]
    assert ne == {
        "group": "Northeast",
        "score": 0.622784,
        "ci_lower": None,
        "ci_upper": None,
        "n": 100,
        "p_cond": 0.018402,
    }


def test_scorecard_ci_slots_are_explicit_nulls():
    card = _build_demographic_scorecard(
        _run({"SEX": [_group("SEX", "Female", 0.7, 0.01, 42)]})
    )
    assert card is not None
    row = card["dimensions"][0]["groups"][0]
    # Keys must exist (stable shape) and be None (unknown, never zero).
    assert "ci_lower" in row and row["ci_lower"] is None
    assert "ci_upper" in row and row["ci_upper"] is None
    assert row["n"] == 42


def test_dimension_labels():
    assert _demographic_dimension_label("CREGION") == "Geography (US Census region)"
    assert _demographic_dimension_label("EDUCATION") == "Education"
    assert _demographic_dimension_label("AGE") == "Age"
    # Unknown codes degrade to title-case, never error.
    assert _demographic_dimension_label("SOME_NEW_DIM") == "Some New Dim"


def test_build_entry_emits_explicit_null_without_data():
    entry = _build_entry(_run(None), rank=1)
    assert "demographic_scorecard" in entry
    assert entry["demographic_scorecard"] is None


def test_build_entry_emits_scorecard_with_data():
    breakdown = {"CREGION": [_group("CREGION", "West", 0.65, 0.03, 100)]}
    entry = _build_entry(_run(breakdown), rank=1)
    card = entry["demographic_scorecard"]
    assert card is not None
    assert card["dataset"] == "subpop"
    assert card["dimensions"][0]["attribute"] == "CREGION"
    assert card["dimensions"][0]["groups"][0]["score"] == 0.65
    # The legacy flat list stays alongside the structured block.
    assert entry["demographic_scores"][0]["group"] == "West"
