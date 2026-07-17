"""CI drift guard for the research narrative (#309).

The findings block in ``site/src/data/leaderboard.json`` and the generated
sections of ``FINDINGS.md`` are both rendered from the per-question rows in
``leaderboard-results/``. These tests recompute both from the artifacts and
fail on any difference from what is committed, so the narrative can never
silently diverge from the leaderboard again.

To refresh after changing artifacts or the findings computation:
    python scripts/generate-findings-md.py
    synthbench publish-data --results-dir leaderboard-results \
        --output site/src/data/leaderboard.json   # or patch just .findings
"""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path

import pytest

from synthbench.findings import (
    ASSERTED_CONSTANTS,
    build_findings,
    load_valid_results,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "leaderboard-results"
LEADERBOARD_JSON = REPO_ROOT / "site" / "src" / "data" / "leaderboard.json"
FINDINGS_MD = REPO_ROOT / "FINDINGS.md"


@pytest.fixture(scope="module")
def computed_findings() -> dict:
    logging.disable(logging.WARNING)  # expected recompute-divergence warnings
    try:
        results, excluded = load_valid_results(RESULTS_DIR)
    finally:
        logging.disable(logging.NOTSET)
    return build_findings(results, excluded, results_dir=RESULTS_DIR)


def test_findings_block_matches_committed_leaderboard(computed_findings):
    """leaderboard.json's findings block must equal a fresh recompute."""
    with open(LEADERBOARD_JSON) as f:
        committed = json.load(f)["findings"]
    assert committed == computed_findings, (
        "site/src/data/leaderboard.json 'findings' block has drifted from "
        "leaderboard-results/. Regenerate it (synthbench publish-data, or "
        "patch the findings key) and commit."
    )


def test_findings_md_generated_sections_match_artifacts(computed_findings):
    """FINDINGS.md's generated sections must equal a fresh render."""
    spec = importlib.util.spec_from_file_location(
        "generate_findings_md", REPO_ROOT / "scripts" / "generate-findings-md.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    original = FINDINGS_MD.read_text()
    regenerated = mod.regenerate(original, computed_findings)
    assert original == regenerated, (
        "FINDINGS.md generated sections are stale — run "
        "`python scripts/generate-findings-md.py` and commit the result."
    )


def test_asserted_constants_carry_sources(computed_findings):
    """Every non-derivable number must name its provenance."""
    assert computed_findings["asserted_constants"] == ASSERTED_CONSTANTS
    for constant in ASSERTED_CONSTANTS:
        for key in ("name", "value", "source"):
            assert constant.get(key), f"asserted constant missing {key}: {constant}"


def test_findings_block_shape(computed_findings):
    """Minimal structural contract the site components rely on."""
    f = computed_findings
    assert f["sps_convention"] == "sps"
    assert len(f["ensemble_comparison"]) >= 3
    for row in f["ensemble_comparison"]:
        assert row["improvement"] == pytest.approx(
            row["ensemble_sps"] - row["best_single_sps"], abs=1e-6
        )
        assert "random_baseline_sps" in row
    # Every published ensemble carries an error-correlation matrix (3
    # constituents -> 3 pairwise r's), recomputed from the committed
    # constituents' per-question JSD vectors.
    assert len(f["ensemble_error_correlation"]) == len(f["ensemble_comparison"])
    for row in f["ensemble_error_correlation"]:
        assert (
            len(row["pairs"])
            == len(row["constituents"]) * (len(row["constituents"]) - 1) // 2
        )
        for pair in row["pairs"]:
            assert -1.0 <= pair["pearson_r"] <= 1.0
            assert pair["n"] > 0
    # KeyFindings.astro looks these groups up by exact display string.
    groups = {(r["attribute"], r["group"]) for r in f["conditioning_results"]}
    for needed in (
        ("POLPARTY", "Republican"),
        ("POLPARTY", "Democrat"),
        ("INCOME", "$100K+"),
        ("INCOME", "<$30K"),
    ):
        assert needed in groups
    # TemperatureCurve.astro keys its palette on these model names.
    sweep_models = {p["model"] for p in f["temperature_sweep"]}
    assert sweep_models == {"Claude Haiku 4.5", "Gemini Flash Lite", "GPT-4o-mini"}
