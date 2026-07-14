"""Strip script behavior + committed-repo guard (issue #308).

The guard test is the CI tripwire: it FAILS whenever any committed
``leaderboard-results/*.json`` file carries per-question
``human_distribution`` data for a gated dataset, so the license-restricted
payload cannot creep back in via new submissions or manual edits.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from synthbench.datasets.policy import policy_for

REPO_ROOT = Path(__file__).resolve().parent.parent
STRIP_SCRIPT = REPO_ROOT / "scripts" / "strip-gated-distributions.py"
RESULTS_DIR = REPO_ROOT / "leaderboard-results"


def _make_result(dataset: str) -> dict:
    return {
        "benchmark": "synthbench",
        "config": {"provider": "p", "dataset": dataset},
        "scores": {"sps": 0.9},
        "aggregate": {"mean_jsd": 0.1, "mean_kendall_tau": 0.5, "n_questions": 1},
        "per_question": [
            {
                "key": "Q1",
                "human_distribution": {"A": 0.6, "B": 0.4},
                "model_distribution": {"A": 0.5, "B": 0.5},
                "jsd": 0.1,
                "kendall_tau": 0.5,
                "human_refusal_rate": 0.05,
            }
        ],
    }


def _run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(STRIP_SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_strip_removes_gated_distribution_and_stamps_marker(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps(_make_result("opinionsqa"), indent=2))
    assert _run_script(str(path)).returncode == 0

    data = json.loads(path.read_text())
    row = data["per_question"][0]
    assert "human_distribution" not in row
    # Everything else survives — including derived scalars.
    assert row["model_distribution"] == {"A": 0.5, "B": 0.5}
    assert row["jsd"] == 0.1
    assert row["human_refusal_rate"] == 0.05
    assert data["stripped_fields"] == ["human_distribution"]


def test_strip_is_idempotent(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps(_make_result("subpop"), indent=2))
    assert _run_script(str(path)).returncode == 0
    first = path.read_text()
    assert _run_script(str(path)).returncode == 0
    assert path.read_text() == first


def test_strip_leaves_full_tier_datasets_intact(tmp_path):
    path = tmp_path / "run.json"
    original = json.dumps(_make_result("gss"), indent=2)
    path.write_text(original)
    assert _run_script(str(path)).returncode == 0
    assert path.read_text() == original


def test_check_mode_flags_gated_distribution(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps(_make_result("globalopinionqa"), indent=2))
    assert _run_script("--check", str(path)).returncode == 1
    assert _run_script(str(path)).returncode == 0
    assert _run_script("--check", str(path)).returncode == 0


def test_committed_results_carry_no_gated_human_distribution():
    """CI guard: the public repo must never redistribute gated distributions."""
    violations = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or data.get("benchmark") != "synthbench":
            continue
        dataset = (data.get("config") or {}).get("dataset") or ""
        if policy_for(dataset).redistribution_policy != "gated":
            continue
        n = sum(
            1
            for q in data.get("per_question") or []
            if isinstance(q, dict) and "human_distribution" in q
        )
        if n:
            violations.append(f"{path.name} ({n} rows)")
    assert not violations, (
        "Committed result files carry gated human_distribution data; run "
        f"scripts/strip-gated-distributions.py. Offenders: {violations[:5]}"
    )
