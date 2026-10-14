"""Findings and publish with more than one named ensemble."""

from __future__ import annotations

from synthbench.findings import _ensembles_by_dataset
from synthbench.leaderboard import display_provider_name


def _ens(slug, dataset):
    return {"config": {"provider": f"ensemble/{slug}", "dataset": dataset}}


def test_every_ensemble_is_compared_not_only_the_first():
    runs = [
        _ens("flash3-raw", "gss"),
        _ens("3-model-blend", "gss"),
        _ens("flash3-raw", "subpop"),
    ]
    got = [(ds, r["config"]["provider"]) for ds, r in _ensembles_by_dataset(runs)]
    assert got == [
        ("gss", "ensemble/3-model-blend"),
        ("gss", "ensemble/flash3-raw"),
        ("subpop", "ensemble/flash3-raw"),
    ]


def test_named_ensembles_have_distinct_display_names():
    names = {
        display_provider_name(f"ensemble/{s}")
        for s in ("3-model-blend", "flash3-raw", "flash3-althing")
    }
    assert len(names) == 3
