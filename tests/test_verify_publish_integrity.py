"""Tests for scripts/verify-publish-integrity.py's license-gating backstop.

The integrity script must FAIL when any artifact under the local publish
output (run/, config/, question/) belongs to a dataset whose redistribution
policy is not ``full`` — that is the check that would have caught gated
Pew ATP / CC-BY-NC-SA ``human_distribution`` data shipping to the public
static origin.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify-publish-integrity.py"


def _build_clean_tree(root: Path) -> dict[str, Path]:
    """A minimal publish tree that passes every existing integrity check."""
    leaderboard = root / "leaderboard.json"
    leaderboard.write_text(
        json.dumps(
            {"entries": [{"config_id": "cfg-ntia", "provider": "m", "dataset": "ntia"}]}
        )
    )

    runs_index = root / "runs-index.json"
    runs_index.write_text(
        json.dumps(
            {
                "n_configs": 1,
                "runs": [{"config_id": "cfg-ntia", "run_id": "r1", "dataset": "ntia"}],
            }
        )
    )

    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "cfg-ntia.json").write_text(
        json.dumps({"config_id": "cfg-ntia", "dataset": "ntia"})
    )

    run_dir = root / "run"
    run_dir.mkdir()
    (run_dir / "r1.json").write_text(
        json.dumps({"run_id": "r1", "config_id": "cfg-ntia", "dataset": "ntia"})
    )

    question_dir = root / "question"
    (question_dir / "ntia").mkdir(parents=True)
    (question_dir / "ntia" / "Q1.json").write_text(
        json.dumps({"dataset": "ntia", "key": "Q1"})
    )
    (question_dir / "ntia" / "index.json").write_text(
        json.dumps({"dataset": "ntia", "n_questions": 1, "questions": []})
    )

    return {
        "leaderboard": leaderboard,
        "runs_index": runs_index,
        "config_dir": config_dir,
        "run_dir": run_dir,
        "question_dir": question_dir,
    }


def _run_script(paths: dict[str, Path]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--leaderboard",
            str(paths["leaderboard"]),
            "--runs-index",
            str(paths["runs_index"]),
            "--config-dir",
            str(paths["config_dir"]),
            "--run-dir",
            str(paths["run_dir"]),
            "--question-dir",
            str(paths["question_dir"]),
        ],
        capture_output=True,
        text=True,
    )


def test_clean_full_tier_tree_passes(tmp_path: Path):
    paths = _build_clean_tree(tmp_path)
    result = _run_script(paths)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no gated artifacts" in result.stdout


def test_planted_gated_run_artifact_fails(tmp_path: Path):
    """A gated dataset's per-run JSON in the local output must fail the check."""
    paths = _build_clean_tree(tmp_path)
    (paths["run_dir"] / "leak.json").write_text(
        json.dumps(
            {
                "run_id": "leak",
                "dataset": "subpop",
                "per_question": [{"human_distribution": {"A": 0.6, "B": 0.4}}],
            }
        )
    )

    result = _run_script(paths)
    assert result.returncode != 0
    assert "non-'full'" in result.stderr
    assert "subpop" in result.stderr


def test_planted_gated_config_artifact_fails(tmp_path: Path):
    paths = _build_clean_tree(tmp_path)
    (paths["config_dir"] / "cfg-leak.json").write_text(
        json.dumps({"config_id": "cfg-leak", "dataset": "pewtech"})
    )

    result = _run_script(paths)
    assert result.returncode != 0
    assert "non-'full'" in result.stderr


def test_planted_gated_question_dir_fails(tmp_path: Path):
    """A gated dataset directory under question/ must fail the check."""
    paths = _build_clean_tree(tmp_path)
    leak_dir = paths["question_dir"] / "opinionsqa"
    leak_dir.mkdir()
    (leak_dir / "Q9.json").write_text(
        json.dumps(
            {
                "dataset": "opinionsqa",
                "key": "Q9",
                "human_distribution": {"A": 0.6, "B": 0.4},
            }
        )
    )

    result = _run_script(paths)
    assert result.returncode != 0
    assert "non-'full'" in result.stderr
    assert "opinionsqa" in result.stderr


def test_unknown_dataset_artifact_fails_conservatively(tmp_path: Path):
    """Unknown datasets default to aggregates_only — local presence fails."""
    paths = _build_clean_tree(tmp_path)
    (paths["run_dir"] / "mystery.json").write_text(
        json.dumps({"run_id": "mystery", "dataset": "not_a_registered_dataset"})
    )

    result = _run_script(paths)
    assert result.returncode != 0
    assert "non-'full'" in result.stderr
