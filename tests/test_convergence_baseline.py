"""Tests for ``synthbench.load_convergence_baseline`` (sb-ham8).

Contract defined in ``docs/convergence-analysis.md`` §"Integration:
synthpanel --calibrate-against". synthpanel (>= 0.9) probes six attribute
paths to find a baseline loader; the top-of-list path is
``synthbench.load_convergence_baseline(dataset=..., question_key=...)``.

These tests pin the behavior synthpanel expects:

* The export is visible both at ``synthbench.*`` and
  ``synthbench.convergence.*`` (it probes both namespaces).
* ``full``-tier datasets return the documented payload with
  ``human_distribution`` populated.
* ``gated``-tier datasets raise ``BaselineGatedError`` — a subclass of
  ``BaselineUnavailable`` so callers can catch either.
* Question-key resolution accepts both bare and prefixed forms.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

import synthbench
from synthbench import (
    BaselineGatedError,
    BaselineUnavailable,
    load_convergence_baseline,
)
from synthbench.convergence import load_convergence_baseline as lcb_convergence
from synthbench.datasets.gss import GSSDataset


# ---------------------------------------------------------------------------
# synthpanel attribute probe — the export must resolve at both paths
# ---------------------------------------------------------------------------


def test_export_visible_at_module_root():
    """synthpanel's first probe hits ``synthbench.load_convergence_baseline``."""
    assert hasattr(synthbench, "load_convergence_baseline")
    assert callable(synthbench.load_convergence_baseline)


def test_export_visible_under_convergence():
    """synthpanel's fallback probe hits ``synthbench.convergence.*``."""
    assert lcb_convergence is load_convergence_baseline


def test_gated_error_is_unavailable_subclass():
    """Callers that only catch ``BaselineUnavailable`` still see gated errors."""
    assert issubclass(BaselineGatedError, BaselineUnavailable)


# ---------------------------------------------------------------------------
# Success path — full-tier datasets
# ---------------------------------------------------------------------------


def _seed_gss_cache(tmp_path: Path) -> Path:
    """Write a minimal GSS aggregated CSV + prime the cached questions.json.

    Returns the data dir. Using the raw-CSV pathway rather than dropping a
    pre-built questions.json keeps the test close to how a real setup runs.
    """
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    csv_path = raw_dir / "gss_aggregated.csv"
    cols = ["question_id", "question_text", "year", "option", "count"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(
            [
                {
                    "question_id": "SPKATH",
                    "question_text": "Allow atheist to speak?",
                    "year": "2022",
                    "option": "Yes",
                    "count": 700,
                },
                {
                    "question_id": "SPKATH",
                    "question_text": "Allow atheist to speak?",
                    "year": "2022",
                    "option": "No",
                    "count": 300,
                },
            ]
        )
    return tmp_path


@pytest.fixture
def gss_with_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Patch GSSDataset's default cache dir to a seeded tmp_path."""
    data_dir = _seed_gss_cache(tmp_path)
    monkeypatch.setattr("synthbench.datasets.gss._default_cache_dir", lambda: data_dir)
    # Sanity: the adapter resolves the seeded data.
    q = GSSDataset().load()
    assert q, "seeded GSS fixture did not materialize any questions"
    return data_dir


def test_full_tier_gss_returns_documented_payload(gss_with_data):
    """Success path: GSS (tier=full) returns the docs-specified shape."""
    payload = load_convergence_baseline(dataset="gss", question_key="GSS_SPKATH")
    assert payload["dataset"] == "gss"
    assert payload["question_key"] == "GSS_SPKATH"
    assert payload["redistribution_policy"] == "full"
    # human_distribution is the only load-bearing field — synthpanel attaches
    # it verbatim to each matching question's `calibration` sub-object.
    assert payload["human_distribution"] == pytest.approx({"Yes": 0.7, "No": 0.3})
    # Provenance passes through for synthpanel's run-metadata block.
    assert payload["license_url"]
    assert payload["citation"]


def test_full_tier_accepts_bare_question_id(gss_with_data):
    """synthpanel may pass the upstream id (``SPKATH``) without the
    ``GSS_`` prefix — the loader resolves either form."""
    payload = load_convergence_baseline(dataset="gss", question_key="SPKATH")
    assert payload["question_key"] == "GSS_SPKATH"
    assert payload["human_distribution"]["Yes"] == pytest.approx(0.7)


def test_full_tier_accepts_filter_suffix(gss_with_data):
    """``gss (2022)`` resolves to the same ``gss`` adapter / policy."""
    payload = load_convergence_baseline(dataset="gss (2022)", question_key="SPKATH")
    assert payload["dataset"] == "gss"
    assert payload["redistribution_policy"] == "full"


def test_unknown_question_raises_unavailable(gss_with_data):
    with pytest.raises(BaselineUnavailable):
        load_convergence_baseline(dataset="gss", question_key="NOT_A_QUESTION")


# ---------------------------------------------------------------------------
# Gated failure path — synthpanel must see a distinct, catchable error
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "gated_dataset",
    [
        "opinionsqa",
        "globalopinionqa",
        "subpop",
        "pewtech",
        "eurobarometer",
        "michigan",
        "wvs",
    ],
)
def test_gated_tier_raises_gated_error(gated_dataset: str):
    """Gated datasets raise BaselineGatedError before touching the adapter.

    This runs without any on-disk data: the policy check must short-circuit
    before any ``dataset.load()`` is attempted, otherwise gated adapters
    would fail with download / auth errors instead of the documented
    gated-tier signal.
    """
    with pytest.raises(BaselineGatedError):
        load_convergence_baseline(dataset=gated_dataset, question_key="ANY_KEY")


def test_gated_error_is_caught_by_unavailable():
    """Callers that don't care about the distinction can catch the parent."""
    with pytest.raises(BaselineUnavailable):
        load_convergence_baseline(dataset="opinionsqa", question_key="ABANY")


# ---------------------------------------------------------------------------
# Input-validation edge cases
# ---------------------------------------------------------------------------


def test_missing_question_key_raises_value_error():
    with pytest.raises(ValueError):
        load_convergence_baseline(dataset="gss")


def test_unknown_dataset_raises_unavailable():
    """Unknown dataset names fall through to ``aggregates_only`` policy —
    the loader surfaces that as ``BaselineUnavailable`` (not ``Gated``)."""
    with pytest.raises(BaselineUnavailable) as exc_info:
        load_convergence_baseline(dataset="not-a-real-dataset", question_key="FOO")
    assert not isinstance(exc_info.value, BaselineGatedError)
