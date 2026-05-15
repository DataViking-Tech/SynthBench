"""Tests for `synthbench submit-adapter` scaffold (refs #256).

These exercise the wiring only — the placeholder artifacts written by the
scaffold are not yet shape-compatible with the eventual leaderboard
schema; that's tracked in follow-up issues against #256.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from synthbench import leaderboard_pr
from synthbench.cli import main


RANDOM_ADAPTER_MODULE = "synthbench.adapter"  # exports RandomAdapter


def test_submit_adapter_help_exits_zero():
    """`synthbench submit-adapter --help` is the discovery surface vendors
    hit first; if it breaks, nothing else matters."""
    res = CliRunner().invoke(main, ["submit-adapter", "--help"])
    assert res.exit_code == 0, res.output
    assert "--adapter" in res.output
    assert "--vendor" in res.output
    assert "--api-env-var" in res.output


def test_submit_adapter_missing_module_exits_2(tmp_path, monkeypatch):
    """Non-importable adapter path → exit 2 with a vendor-readable error.

    Exit 2 is reserved for 'your inputs are malformed' so vendor CI can
    distinguish bad-args from runtime failures (which would be exit 1)."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            "does.not.exist.anywhere",
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )
    assert res.exit_code == 2, res.output
    assert "adapter not importable" in res.output


def test_submit_adapter_missing_env_var_exits_3(tmp_path, monkeypatch):
    """Adapter imports cleanly but the API env var is unset → exit 3.

    Distinct from exit 2 so vendor CI can prompt for credential setup
    without re-running the whole import-validation dance."""
    monkeypatch.delenv("SYNTHBENCH_TEST_ENV_VAR_THAT_IS_NOT_SET", raising=False)
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "SYNTHBENCH_TEST_ENV_VAR_THAT_IS_NOT_SET",
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )
    assert res.exit_code == 3, res.output
    assert "is not set" in res.output


def test_submit_adapter_happy_path_writes_artifacts(tmp_path, monkeypatch):
    """End-to-end scaffold: RandomAdapter + dummy env var → exit 0 with
    submission.md + run.json present in --output-dir."""
    monkeypatch.setenv("ACME_API_KEY", "ignored-presence-only")
    out_dir = tmp_path / "submission"
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert res.exit_code == 0, res.output

    md = out_dir / "submission.md"
    rj = out_dir / "run.json"
    assert md.exists(), f"submission.md not written; got: {list(out_dir.iterdir())}"
    assert rj.exists(), f"run.json not written; got: {list(out_dir.iterdir())}"

    # run.json must round-trip and carry the vendor identity + scaffold
    # status, since downstream tooling will key off these.
    payload = json.loads(rj.read_text())
    assert payload["status"] == "scaffold"
    assert payload["adapter"]["vendor"] == "acme"
    assert payload["adapter"]["vendor_version"] == "0.1.0"
    assert payload["adapter"]["name"] == "synthbench/random-adapter"
    assert payload["suite"] == "core"
    assert payload["api_env_var"] == "ACME_API_KEY"

    # run_hash must be present and well-formed even in scaffold mode
    # (sb-1ix). Empty persona_seeds + raw_responses still produce a real
    # sha256 over the adapter identity + suite manifest.
    assert isinstance(payload["run_hash"], str)
    assert len(payload["run_hash"]) == 64
    int(payload["run_hash"], 16)  # valid hex
    assert payload["raw_responses"] == []

    # submission.md should mention vendor + scaffold disclaimer so the PR
    # reviewer doesn't mistake it for a real leaderboard entry.
    md_text = md.read_text()
    assert "acme" in md_text
    assert "Scaffold" in md_text


def test_submit_adapter_loads_from_filesystem_path(tmp_path, monkeypatch):
    """Vendors will typically point at a .py file in their own repo, not a
    dotted import. Verify that path works too."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    adapter_file = tmp_path / "my_adapter.py"
    adapter_file.write_text(
        "from synthbench.adapter import Adapter\n"
        "class MyAdapter(Adapter):\n"
        "    @property\n"
        "    def name(self): return 'acme/test'\n"
        "    @property\n"
        "    def version(self): return '0.0.1'\n"
        "    async def respond(self, *, question, persona, context=None):\n"
        "        return 'yes'\n"
    )
    out_dir = tmp_path / "out"
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            str(adapter_file),
            "--vendor",
            "acme",
            "--vendor-version",
            "0.0.1",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads((out_dir / "run.json").read_text())
    assert payload["adapter"]["name"] == "acme/test"


def test_submit_adapter_run_hash_is_deterministic(tmp_path, monkeypatch):
    """Two scaffold-mode runs with identical inputs MUST emit the same
    ``run_hash`` — this is the leaderboard's tamper-detection contract
    surfaced at the CLI layer."""
    monkeypatch.setenv("ACME_API_KEY", "x")

    def run_into(subdir: str) -> str:
        out = tmp_path / subdir
        res = CliRunner().invoke(
            main,
            [
                "submit-adapter",
                "--adapter",
                RANDOM_ADAPTER_MODULE,
                "--vendor",
                "acme",
                "--vendor-version",
                "0.1.0",
                "--api-env-var",
                "ACME_API_KEY",
                "--output-dir",
                str(out),
            ],
        )
        assert res.exit_code == 0, res.output
        return json.loads((out / "run.json").read_text())["run_hash"]

    assert run_into("a") == run_into("b")


def test_submit_adapter_unknown_suite_exits_2(tmp_path, monkeypatch):
    """Missing suite manifest is a bad-input error, not a runtime failure
    — mirrors the exit-2 convention for unimportable adapters."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--suite",
            "this-suite-does-not-exist",
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )
    assert res.exit_code == 2, res.output
    assert "suite manifest not found" in res.output


# --- sb-b0v: --open-pr / leaderboard PR auto-generation --------------------


def test_render_pr_body_scaffold_run_marks_scores_pending():
    """Scaffold mode (no scores, no run_hash) must render a valid PR body
    that flags itself as scaffold so reviewers don't treat it as a real
    leaderboard entry."""
    body = leaderboard_pr.render_pr_body(
        {
            "schema_version": "0.0.0-scaffold",
            "status": "scaffold",
            "adapter": {
                "name": "acme/test",
                "version": "0.0.1",
                "vendor": "acme",
                "vendor_version": "0.1.0",
            },
            "suite": "core",
            "run_hash": None,
            "scores": None,
        }
    )
    assert "acme" in body
    assert "scaffold" in body.lower()
    assert "pending" in body  # null run_hash renders as 'pending'


def test_render_pr_body_real_run_emits_scores_table():
    """Once the eval pipeline lands (sb-bas), a populated scores dict must
    render as a markdown table the leaderboard repo can parse."""
    body = leaderboard_pr.render_pr_body(
        {
            "schema_version": "1.0.0",
            "status": "completed",
            "adapter": {
                "name": "acme/prod",
                "version": "1.2.3",
                "vendor": "acme",
                "vendor_version": "2026.05.14",
            },
            "suite": "core",
            "run_hash": "abc1234567890def" + "0" * 48,
            "scores": {"jsd": 0.123, "kendall_tau": 0.456},
        }
    )
    assert "| metric | value |" in body
    assert "| jsd | 0.123 |" in body
    assert "| kendall_tau | 0.456 |" in body
    assert "abc1234567890def" in body


def test_branch_name_uses_run_hash_prefix():
    name = leaderboard_pr.branch_name("acme", "2026.05.14", "abc1234567890deadbeef")
    assert name == "submission/acme-2026.05.14-abc12345"


def test_branch_name_falls_back_to_scaffold_when_no_hash():
    """Scaffold submissions still need a branch so vendors can validate the
    `gh` fork/push flow before the eval pipeline lands."""
    name = leaderboard_pr.branch_name("acme", "0.1.0", None)
    assert name == "submission/acme-0.1.0-scaffold"


def test_branch_name_normalizes_slashes_in_vendor():
    """A vendor like 'acme/research' would produce a malformed branch ref;
    collapse to dashes so `gh api repos/.../git/refs` accepts it."""
    name = leaderboard_pr.branch_name("acme/research", "1.0", "deadbeefcafe")
    assert name == "submission/acme-research-1.0-deadbeef"


def test_open_pr_exits_4_when_gh_missing(tmp_path, monkeypatch):
    """`gh` absent from PATH must produce exit 4 — distinct from exit 1
    (runtime failure) and exit 2 (bad inputs) so vendor CI can detect a
    missing-tooling state and prompt for install."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    monkeypatch.setattr(leaderboard_pr.shutil, "which", lambda _name: None)
    out_dir = tmp_path / "out"
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(out_dir),
            "--open-pr",
        ],
    )
    assert res.exit_code == 4, res.output
    assert "gh" in res.output.lower()
    # Artifacts must still have been written before the PR step failed —
    # otherwise the vendor loses their scaffold output on a missing-gh.
    assert (out_dir / "run.json").exists()
    assert (out_dir / "submission.md").exists()


def test_open_pr_happy_path_calls_gh_and_prints_pr_url(tmp_path, monkeypatch):
    """End-to-end with `gh` mocked: the CLI should call gh in the right
    sequence (fork → resolve user → create ref → upload files → open PR)
    and surface the resulting PR URL to the vendor."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    monkeypatch.setattr(leaderboard_pr.shutil, "which", lambda _name: "/usr/bin/gh")

    calls: list[list[str]] = []

    class _StubCompleted:
        returncode = 0
        stderr = ""

        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    def fake_run(argv, *_args, **_kwargs):
        calls.append(argv)
        sub = argv[1] if len(argv) > 1 else ""
        if sub == "repo" and argv[2] == "fork":
            return _StubCompleted("forked\n")
        if sub == "api" and argv[2] == "user":
            return _StubCompleted("vendor-user\n")
        if sub == "api" and "git/ref/heads/" in argv[2]:
            return _StubCompleted("base-sha-xyz\n")
        if sub == "api" and "git/refs" in argv[2]:
            return _StubCompleted('{"ref":"refs/heads/submission/..."}\n')
        if sub == "api" and "contents/" in argv[2]:
            return _StubCompleted('{"commit": {"sha": "deadbeef"}}\n')
        if sub == "pr" and argv[2] == "create":
            return _StubCompleted(
                "https://github.com/DataViking-Tech/SynthBench/pull/999\n"
            )
        raise AssertionError(f"unexpected gh call: {argv}")

    monkeypatch.setattr(leaderboard_pr.subprocess, "run", fake_run)

    out_dir = tmp_path / "out"
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(out_dir),
            "--open-pr",
        ],
    )
    assert res.exit_code == 0, res.output
    assert "pull/999" in res.output

    sub_argv = [c[1:] for c in calls]  # strip leading "gh"
    assert any(
        a[:2] == ["repo", "fork"] and "DataViking-Tech/SynthBench" in a
        for a in sub_argv
    )
    assert any(a[:2] == ["api", "user"] for a in sub_argv)
    assert any(a[0] == "api" and "git/refs" in a[1] for a in sub_argv)
    contents_calls = [a for a in sub_argv if a[0] == "api" and "contents/" in a[1]]
    assert len(contents_calls) == 2  # submission.md + run.json
    pr_create = [a for a in sub_argv if a[:2] == ["pr", "create"]]
    assert len(pr_create) == 1
    head_idx = pr_create[0].index("--head") + 1
    assert pr_create[0][head_idx].startswith("vendor-user:submission/acme-0.1.0-")


def test_open_pr_surfaces_gh_failure_as_exit_1(tmp_path, monkeypatch):
    """A non-zero `gh` exit (e.g. fork blocked by org policy) maps to exit
    1 with stderr surfaced — separate from the missing-binary exit 4 so
    vendors can tell 'install gh' apart from 'gh ran but failed'."""
    monkeypatch.setenv("ACME_API_KEY", "x")
    monkeypatch.setattr(leaderboard_pr.shutil, "which", lambda _name: "/usr/bin/gh")

    class _Failed:
        returncode = 1
        stdout = ""
        stderr = "fork blocked by SSO policy\n"

    monkeypatch.setattr(leaderboard_pr.subprocess, "run", lambda *a, **k: _Failed())

    out_dir = tmp_path / "out"
    res = CliRunner().invoke(
        main,
        [
            "submit-adapter",
            "--adapter",
            RANDOM_ADAPTER_MODULE,
            "--vendor",
            "acme",
            "--vendor-version",
            "0.1.0",
            "--api-env-var",
            "ACME_API_KEY",
            "--output-dir",
            str(out_dir),
            "--open-pr",
        ],
    )
    assert res.exit_code == 1, res.output
    assert "fork blocked" in res.output
