"""Tests for `synthbench submit-adapter` scaffold (refs #256).

These exercise the wiring only — the placeholder artifacts written by the
scaffold are not yet shape-compatible with the eventual leaderboard
schema; that's tracked in follow-up issues against #256.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

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
