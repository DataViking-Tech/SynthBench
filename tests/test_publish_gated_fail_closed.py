"""Fail-closed gating for gated-tier publish artifacts.

License-restricted (``gated``) datasets — Pew ATP sources, CC-BY-NC-SA
corpora — must only ever ship to the authenticated R2 origin. When no R2
uploader is configured the publish step must SKIP those artifacts, never
write them to the local static output (``site/public/data/`` ships to a
public origin with no auth in front of it). Strict mode
(``strict_gating=True`` / ``--strict-gating`` / ``SYNTHBENCH_PUBLISH_STRICT=1``)
hard-fails instead, which is what CI deploys use so a missing R2
configuration fails the build loudly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from synthbench.cli import main
from synthbench.publish import GatedPublishError, publish_questions, publish_runs


# Env overrides for CLI invocations: guarantee no ambient R2 credentials
# leak into the test (empty string == unset for env_has_r2_config).
_NO_R2_ENV = {
    "R2_ACCOUNT_ID": "",
    "R2_ACCESS_KEY_ID": "",
    "R2_SECRET_ACCESS_KEY": "",
    "R2_BUCKET": "",
    "SYNTHBENCH_PUBLISH_STRICT": "",
}


def _combined_output(result) -> str:
    """stdout + stderr across click versions (mixed or split capture)."""
    out = result.output
    try:
        err = result.stderr
    except (ValueError, AttributeError):
        err = ""
    return out + err


def _make_run_result(provider: str, dataset: str) -> dict:
    return {
        "benchmark": "synthbench",
        "config": {
            "provider": provider,
            "dataset": dataset,
            "n_evaluated": 1,
        },
        "scores": {"sps": 0.5, "p_dist": 0.5, "p_rank": 0.5, "p_refuse": 1.0},
        "aggregate": {"mean_jsd": 0.1, "mean_kendall_tau": 0.5, "n_questions": 1},
        "per_question": [
            {
                "key": "Q1",
                "text": "q?",
                "options": ["A", "B"],
                "human_distribution": {"A": 0.6, "B": 0.4},
                "model_distribution": {"A": 0.5, "B": 0.5},
                "jsd": 0.1,
                "n_samples": 10,
                "model_refusal_rate": 0.0,
                "human_refusal_rate": 0.05,
            }
        ],
    }


def _write_gated_fixture(results_dir: Path) -> None:
    results_dir.mkdir()
    (results_dir / "20260101-gated.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "subpop"))
    )


# -- Library behavior: skip + count, never write locally ---------------------


def test_publish_runs_without_uploader_skips_gated(tmp_path: Path):
    """Gated run/config artifacts are withheld, not written to local disk."""
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    out_dir = tmp_path / "site_data"
    counts = publish_runs(results_dir, out_dir, r2_uploader=None)

    # One per-run + one per-config artifact withheld.
    assert counts["runs"] == 1
    assert counts["configs"] == 1
    assert counts["gated_skipped"] == 2
    assert list((out_dir / "run").glob("*.json")) == []
    assert list((out_dir / "config").glob("*.json")) == []
    # The public catalog still ships — gated rows degrade to no drill-down.
    assert (out_dir / "runs-index.json").exists()


def test_publish_runs_full_tier_datasets_still_publish_locally(tmp_path: Path):
    """gss and ntia are ``full`` — no uploader required, artifacts land locally."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-gss.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "gss"))
    )
    (results_dir / "20260102-ntia.json").write_text(
        json.dumps(_make_run_result("openrouter/openai/gpt-4o-mini", "ntia"))
    )

    out_dir = tmp_path / "site_data"
    counts = publish_runs(results_dir, out_dir, r2_uploader=None)

    assert counts["gated_skipped"] == 0
    run_datasets = {
        json.loads(p.read_text())["dataset"] for p in (out_dir / "run").glob("*.json")
    }
    assert run_datasets == {"gss", "ntia"}
    assert len(list((out_dir / "config").glob("*.json"))) == 2


def test_publish_questions_full_tier_datasets_still_publish_locally(tmp_path: Path):
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-gss.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "gss"))
    )
    (results_dir / "20260102-ntia.json").write_text(
        json.dumps(_make_run_result("openrouter/openai/gpt-4o-mini", "ntia"))
    )

    out_dir = tmp_path / "site_data"
    counts = publish_questions(results_dir, out_dir, r2_uploader=None)

    assert counts["gated_skipped"] == 0
    assert (out_dir / "question" / "gss" / "Q1.json").exists()
    assert (out_dir / "question" / "gss" / "index.json").exists()
    assert (out_dir / "question" / "ntia" / "Q1.json").exists()
    assert (out_dir / "question" / "ntia" / "index.json").exists()


# -- Strict mode: hard failure ------------------------------------------------


def test_publish_runs_strict_gating_raises_without_uploader(tmp_path: Path):
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    with pytest.raises(GatedPublishError, match="strict gating"):
        publish_runs(
            results_dir, tmp_path / "out", r2_uploader=None, strict_gating=True
        )

    # Nothing gated landed locally before the failure either.
    assert list((tmp_path / "out" / "run").glob("*.json")) == []


def test_publish_questions_strict_gating_raises_without_uploader(tmp_path: Path):
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    with pytest.raises(GatedPublishError, match="strict gating"):
        publish_questions(
            results_dir, tmp_path / "out", r2_uploader=None, strict_gating=True
        )

    assert not (tmp_path / "out" / "question" / "subpop").exists()


def test_publish_runs_strict_gating_ok_with_full_tier_only(tmp_path: Path):
    """Strict mode does not fire when nothing routes to R2."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-ntia.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "ntia"))
    )

    counts = publish_runs(
        results_dir, tmp_path / "out", r2_uploader=None, strict_gating=True
    )
    assert counts["gated_skipped"] == 0


# -- CLI: warning summary and strict exit codes -------------------------------


def test_cli_publish_runs_warns_on_skipped_gated(tmp_path: Path):
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "publish-runs",
            "--results-dir",
            str(results_dir),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        env=_NO_R2_ENV,
    )

    assert result.exit_code == 0, _combined_output(result)
    output = _combined_output(result)
    assert "gated artifact(s) skipped" in output
    assert "R2 uploader not configured" in output
    assert list((tmp_path / "out" / "run").glob("*.json")) == []


def test_cli_publish_runs_strict_env_var_fails(tmp_path: Path):
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "publish-runs",
            "--results-dir",
            str(results_dir),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        env={**_NO_R2_ENV, "SYNTHBENCH_PUBLISH_STRICT": "1"},
    )

    assert result.exit_code == 1
    assert "strict gating" in _combined_output(result)
    assert list((tmp_path / "out" / "run").glob("*.json")) == []


def test_cli_publish_questions_strict_flag_fails(tmp_path: Path):
    results_dir = tmp_path / "raw"
    _write_gated_fixture(results_dir)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "publish-questions",
            "--results-dir",
            str(results_dir),
            "--output-dir",
            str(tmp_path / "out"),
            "--strict-gating",
        ],
        env=_NO_R2_ENV,
    )

    assert result.exit_code == 1
    assert "strict gating" in _combined_output(result)
    assert not (tmp_path / "out" / "question" / "subpop").exists()


def test_cli_publish_runs_no_warning_when_nothing_skipped(tmp_path: Path):
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-ntia.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "ntia"))
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "publish-runs",
            "--results-dir",
            str(results_dir),
            "--output-dir",
            str(tmp_path / "out"),
        ],
        env=_NO_R2_ENV,
    )

    assert result.exit_code == 0, _combined_output(result)
    assert "gated artifact(s) skipped" not in _combined_output(result)
