"""Unit tests for :mod:`synthbench.submission_pr` (refs sb-6gw).

Exercises each check function in isolation so the CI runner script can
stay thin. End-to-end runner behavior is covered by
``test_validate_submission_pr_runner`` at the bottom.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from synthbench.submission_pr import (
    CheckResult,
    check_adapter_registry,
    check_run_hash,
    is_adapter_submission,
    lint_submission_md,
    load_accepted_adapters,
    render_sticky_comment,
)


# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------


def test_load_accepted_adapters_missing_file_is_empty(tmp_path: Path) -> None:
    """Missing registry yields []; the registry check then fails every
    submission with a useful message, which is the safer failure mode."""
    assert load_accepted_adapters(tmp_path / "nope.json") == []


def test_load_accepted_adapters_validates_shape(tmp_path: Path) -> None:
    p = tmp_path / "registry.json"
    p.write_text(json.dumps({"adapters": [{"name": "x", "version": 1}]}))
    with pytest.raises(ValueError):
        load_accepted_adapters(p)


def test_check_adapter_registry_pass() -> None:
    run = {"adapter": {"name": "acme/test", "version": "0.1.0"}}
    result = check_adapter_registry(run, [{"name": "acme/test", "version": "0.1.0"}])
    assert result.passed, result


def test_check_adapter_registry_fail_when_not_listed() -> None:
    run = {"adapter": {"name": "acme/test", "version": "0.1.0"}}
    result = check_adapter_registry(run, [{"name": "acme/test", "version": "0.2.0"}])
    assert result.failed
    # The failure message must point the vendor at the registry PR flow,
    # not just say "no".
    assert "data/accepted_adapters.json" in " ".join(result.details)
    assert "separate" in " ".join(result.details).lower()


def test_check_adapter_registry_fail_when_no_adapter_block() -> None:
    """Submissions without an adapter block should never reach this check
    in production (the runner filters them out), but defensive failure
    here protects against bypass."""
    result = check_adapter_registry({"provider": "openrouter/openai/x"}, [])
    assert result.failed
    assert "no `adapter` block" in result.summary


# ---------------------------------------------------------------------------
# Run-hash check
# ---------------------------------------------------------------------------


def test_check_run_hash_skips_when_module_missing(monkeypatch) -> None:
    """Until sb-1ix lands, the check must skip rather than crash."""
    # Force the import probe to return None by removing the module if it
    # somehow got registered.
    monkeypatch.setitem(sys.modules, "synthbench.run_hash", None)
    run = {"run_hash": "deadbeef"}
    result = check_run_hash(run, suite_manifest={"keys": ["A"]}, derive=None)
    assert result.status == "skip"
    assert "sb-1ix" in " ".join(result.details)


def test_check_run_hash_skips_when_declared_null() -> None:
    """Scaffold submissions carry `run_hash: null` — that's not a fail."""
    derive_fn = lambda **kw: "x"  # noqa: E731
    result = check_run_hash({"run_hash": None}, suite_manifest=None, derive=derive_fn)
    assert result.status == "skip"
    assert "null" in result.summary


def test_check_run_hash_pass_when_match() -> None:
    derive_fn = lambda **kw: "abc123def456"  # noqa: E731
    run = {"run_hash": "abc123def456", "adapter": {"name": "x", "version": "1"}}
    result = check_run_hash(run, suite_manifest={"keys": []}, derive=derive_fn)
    assert result.passed, result


def test_check_run_hash_fail_when_mismatch() -> None:
    derive_fn = lambda **kw: "actual_hash_value"  # noqa: E731
    run = {"run_hash": "declared_hash", "adapter": {}, "raw_responses": []}
    result = check_run_hash(run, suite_manifest={"keys": []}, derive=derive_fn)
    assert result.failed
    # Both hashes must appear in the diff so reviewers can spot which
    # input drifted.
    joined = " ".join(result.details)
    assert "declared_hash" in joined
    assert "actual_hash_value" in joined


def test_check_run_hash_fail_when_derive_raises() -> None:
    def bad_derive(**kw):
        raise RuntimeError("missing field")

    result = check_run_hash(
        {"run_hash": "x", "adapter": {}}, suite_manifest=None, derive=bad_derive
    )
    assert result.failed
    assert "missing field" in result.summary


# ---------------------------------------------------------------------------
# submission.md lint
# ---------------------------------------------------------------------------


VALID_MD = """# SynthBench Score Card

**Provider:** acme/test
**Dataset:** core (200 questions)

## SynthBench Parity Score (SPS)

**SPS: 0.7100**

| Metric | Score |
|--------|------:|
| P_dist | 0.65 |
| P_rank | 0.72 |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3 |
"""


def test_lint_submission_md_passes_canonical_format() -> None:
    result = lint_submission_md(VALID_MD)
    assert result.passed, result


def test_lint_submission_md_flags_missing_h1() -> None:
    result = lint_submission_md(VALID_MD.replace("# SynthBench Score Card", ""))
    assert result.failed


def test_lint_submission_md_flags_wrong_h1_prefix() -> None:
    swapped = VALID_MD.replace("# SynthBench Score Card", "# My Awesome Submission")
    result = lint_submission_md(swapped)
    assert result.failed
    assert any("H1 must start with" in d for d in result.details)


def test_lint_submission_md_flags_missing_section() -> None:
    stripped = "\n".join(
        ln for ln in VALID_MD.splitlines() if not ln.startswith("## Raw Metrics")
    )
    result = lint_submission_md(stripped)
    assert result.failed
    assert any("Raw Metrics" in d for d in result.details)


def test_lint_submission_md_flags_missing_scores_table() -> None:
    # Replace the first table's header with one missing the canonical
    # "Metric | Score" columns.
    bad = VALID_MD.replace("| Metric | Score |", "| Foo | Bar |").replace(
        "| Metric | Value |", "| Foo | Bar |"
    )
    result = lint_submission_md(bad)
    assert result.failed
    assert any("scores table" in d for d in result.details)


# ---------------------------------------------------------------------------
# is_adapter_submission
# ---------------------------------------------------------------------------


def test_is_adapter_submission_true_for_adapter_block() -> None:
    assert is_adapter_submission({"adapter": {"name": "x", "version": "1"}})


def test_is_adapter_submission_false_for_legacy() -> None:
    assert not is_adapter_submission({"config": {"provider": "openrouter/x"}})


# ---------------------------------------------------------------------------
# Sticky-comment rendering
# ---------------------------------------------------------------------------


def test_render_sticky_comment_marker_present() -> None:
    """The marker is what lets the sticky-comment action find and
    overwrite the previous comment — losing it would stack comments on
    every push."""
    body = render_sticky_comment(submissions=[])
    assert body.splitlines()[0].startswith("<!-- synthbench:")


def test_render_sticky_comment_no_submissions() -> None:
    body = render_sticky_comment(submissions=[])
    assert "No adapter-based submissions" in body


def test_render_sticky_comment_includes_each_result() -> None:
    submissions = [
        (
            "leaderboard-results/acme.json",
            [
                CheckResult(name="adapter-registry", status="pass", summary="ok"),
                CheckResult(
                    name="run-hash",
                    status="fail",
                    summary="mismatch",
                    details=("  declared: aaa", "  re-derived: bbb"),
                ),
            ],
        )
    ]
    body = render_sticky_comment(submissions=submissions)
    assert "❌" in body
    assert "leaderboard-results/acme.json" in body
    assert "adapter-registry" in body
    assert "mismatch" in body
    assert "declared: aaa" in body


def test_render_sticky_comment_all_pass_shows_green() -> None:
    submissions = [
        (
            "leaderboard-results/x.json",
            [CheckResult(name="adapter-registry", status="pass", summary="ok")],
        )
    ]
    body = render_sticky_comment(submissions=submissions)
    assert "✅ All checks passed" in body
    assert "❌" not in body.split("\n", 4)[2]  # status line is green


# ---------------------------------------------------------------------------
# End-to-end runner script
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parent.parent


def _make_changed_files(tmp_path: Path, paths: list[str]) -> Path:
    """Build the NUL-delimited file list `scripts/validate-submission-pr.py`
    expects (same format `git diff -z` produces)."""
    out = tmp_path / "changed.txt"
    out.write_bytes(b"\x00".join(p.encode() for p in paths) + b"\x00")
    return out


def _run_runner(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate-submission-pr.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_runner_passes_when_no_submissions_changed(tmp_path: Path) -> None:
    """No leaderboard changes → exit 0, comment says "no submissions"."""
    changed = _make_changed_files(tmp_path, ["README.md"])
    comment = tmp_path / "comment.md"
    proc = _run_runner(
        [
            "--changed-files",
            str(changed),
            "--comment-out",
            str(comment),
            "--repo-root",
            str(REPO_ROOT),
        ]
    )
    assert proc.returncode == 0, proc.stderr
    assert "No adapter-based submissions" in comment.read_text()


def test_runner_skips_legacy_submissions(tmp_path: Path) -> None:
    """A legacy (no `adapter` block) submission is silently skipped so
    the sticky comment stays focused on adapter submissions."""
    sub = tmp_path / "fake-leaderboard-results"
    sub.mkdir()
    # Symlinking under the actual repo would be intrusive — instead use
    # --repo-root to point at tmp_path and stage a fake submission there.
    legacy = {
        "benchmark": "globalopinionqa",
        "config": {"provider": "openrouter/x", "dataset": "d"},
    }
    (sub / "legacy.json").write_text(json.dumps(legacy))
    # The runner filters by `"leaderboard-results" in path.parts`, so we
    # rename to that conventional folder name under tmp_path.
    real = tmp_path / "leaderboard-results"
    sub.rename(real)
    changed = _make_changed_files(tmp_path, ["leaderboard-results/legacy.json"])
    comment = tmp_path / "comment.md"
    proc = _run_runner(
        [
            "--changed-files",
            str(changed),
            "--comment-out",
            str(comment),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "No adapter-based submissions" in comment.read_text()


def test_runner_fails_when_adapter_not_registered(tmp_path: Path) -> None:
    """An adapter submission whose identity is not in the registry must
    fail the workflow with exit code 1 and a clear sticky-comment
    explanation."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "accepted_adapters.json").write_text(
        json.dumps({"adapters": []})
    )
    (tmp_path / "leaderboard-results").mkdir()
    run = {
        "schema_version": "0.0.0-scaffold",
        "adapter": {"name": "unknown/adapter", "version": "9.9.9"},
        "suite": "core",
        "run_hash": None,
    }
    (tmp_path / "leaderboard-results" / "x.json").write_text(json.dumps(run))
    (tmp_path / "leaderboard-results" / "x.md").write_text(VALID_MD)

    changed = _make_changed_files(tmp_path, ["leaderboard-results/x.json"])
    comment = tmp_path / "comment.md"
    proc = _run_runner(
        [
            "--changed-files",
            str(changed),
            "--comment-out",
            str(comment),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert proc.returncode == 1, proc.stderr + proc.stdout
    body = comment.read_text()
    assert "unknown/adapter" in body
    assert "NOT in" in body
