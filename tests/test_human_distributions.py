"""Tests for the canonical human-distribution registry (issue #308)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthbench import human_distributions as hd


@pytest.fixture(autouse=True)
def _isolated_registry(monkeypatch, tmp_path):
    """Point the registry at an empty tmp dir and block R2/adapter fallbacks."""
    monkeypatch.setenv("SYNTHBENCH_HUMAN_DISTRIBUTIONS_DIR", str(tmp_path))
    monkeypatch.setattr(hd, "_load_from_r2", lambda base, local_dir: None)
    monkeypatch.setattr(hd, "_load_from_adapter", lambda base: None)
    hd.clear_cache()
    yield tmp_path
    hd.clear_cache()


def _write_artifact(local_dir: Path, dataset: str, dists: dict) -> None:
    (local_dir / f"{dataset}.json").write_text(
        json.dumps(
            {
                "dataset": dataset,
                "n_questions": len(dists),
                "distributions": dists,
            }
        )
    )


def test_load_from_local_artifact(_isolated_registry):
    _write_artifact(_isolated_registry, "opinionsqa", {"Q1": {"A": 0.6, "B": 0.4}})
    dists = hd.load_canonical_distributions("opinionsqa")
    assert dists == {"Q1": {"A": 0.6, "B": 0.4}}


def test_missing_source_returns_none_and_is_memoized(_isolated_registry):
    assert hd.load_canonical_distributions("opinionsqa") is None
    # Miss is cached: writing the artifact afterwards does not change the
    # in-process answer until the cache is cleared.
    _write_artifact(_isolated_registry, "opinionsqa", {"Q1": {"A": 1.0}})
    assert hd.load_canonical_distributions("opinionsqa") is None
    hd.clear_cache()
    assert hd.load_canonical_distributions("opinionsqa") == {"Q1": {"A": 1.0}}


def test_malformed_artifact_returns_none(_isolated_registry):
    (_isolated_registry / "subpop.json").write_text("{not json")
    assert hd.load_canonical_distributions("subpop") is None


def test_filtered_dataset_name_uses_base(_isolated_registry):
    _write_artifact(_isolated_registry, "opinionsqa", {"Q1": {"A": 1.0}})
    assert hd.load_canonical_distributions("opinionsqa (W82)") == {"Q1": {"A": 1.0}}


def test_rehydrate_fills_missing_rows():
    rows = [
        {"key": "Q1"},
        {"key": "Q2", "human_distribution": {"A": 0.9, "B": 0.1}},
        {"key": "Q_UNKNOWN"},
    ]
    missing = hd.rehydrate_per_question(rows, {"Q1": {"A": 0.5, "B": 0.5}})
    assert rows[0]["human_distribution"] == {"A": 0.5, "B": 0.5}
    # Existing distribution untouched without replace_existing.
    assert rows[1]["human_distribution"] == {"A": 0.9, "B": 0.1}
    assert "human_distribution" not in rows[2]
    assert missing == 1


def test_rehydrate_replace_existing_overwrites_submitted_copy():
    rows = [{"key": "Q1", "human_distribution": {"A": 0.9, "B": 0.1}}]
    missing = hd.rehydrate_per_question(
        rows, {"Q1": {"A": 0.5, "B": 0.5}}, replace_existing=True
    )
    assert rows[0]["human_distribution"] == {"A": 0.5, "B": 0.5}
    assert missing == 0


def test_build_artifact_unknown_dataset_raises():
    with pytest.raises(KeyError):
        hd.build_artifact("definitely-not-a-dataset")
