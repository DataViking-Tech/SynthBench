"""Routing tests for the R2 publish path (sb-sjs).

Verifies that ``publish_runs`` and ``publish_questions`` send per-dataset
artifacts to the injected uploader for non-``full`` datasets and continue
to write public-tier datasets to disk. Uses a fake S3 client wrapped by a
real ``R2Uploader`` so the assertions cover end-to-end serialization, not
a mocked boundary inside the publish module.
"""

from __future__ import annotations

import json
from pathlib import Path

from synthbench.publish import publish_questions, publish_runs
from synthbench.r2_upload import R2Config, R2Uploader


# -- Test helpers -----------------------------------------------------------


class _FakeS3Client:
    def __init__(self):
        self.calls: list[dict] = []

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str):
        self.calls.append({"Bucket": Bucket, "Key": Key, "Body": Body})
        return {"ETag": "fake"}


def _uploader() -> tuple[R2Uploader, _FakeS3Client]:
    client = _FakeS3Client()
    cfg = R2Config(
        account_id="acct",
        access_key_id="ak",
        secret_access_key="sk",
        bucket="synthbench-data-test",
    )
    return R2Uploader(cfg, client=client), client


def _make_question_result(provider: str, dataset: str, key: str) -> dict:
    return {
        "benchmark": "synthbench",
        "config": {"provider": provider, "dataset": dataset},
        "per_question": [
            {
                "key": key,
                "text": "q?",
                "options": ["A", "B"],
                "human_distribution": {"A": 0.6, "B": 0.4},
                "model_distribution": {"A": 0.5, "B": 0.5},
                "jsd": 0.05,
                "n_samples": 10,
                "model_refusal_rate": 0.0,
                "human_refusal_rate": 0.05,
            }
        ],
    }


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
            }
        ],
    }


# -- publish_questions routing ---------------------------------------------


def test_publish_questions_routes_gated_dataset_to_r2(tmp_path: Path):
    """opinionsqa is `aggregates_only` → per-question + index land in R2."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "run_one.json").write_text(
        json.dumps(
            _make_question_result(
                "openrouter/anthropic/claude-haiku-4-5", "opinionsqa", "Q1"
            )
        )
    )
    (results_dir / "run_two.json").write_text(
        json.dumps(
            _make_question_result("openrouter/openai/gpt-4o-mini", "opinionsqa", "Q1")
        )
    )

    out_dir = tmp_path / "site_data"
    uploader, client = _uploader()
    counts = publish_questions(results_dir, out_dir, r2_uploader=uploader)

    assert counts == {"questions": 1, "datasets": 1}
    # No per-question file on disk for the gated dataset.
    assert not (out_dir / "question" / "opinionsqa" / "Q1.json").exists()
    assert not (out_dir / "question" / "opinionsqa" / "index.json").exists()

    keys = {c["Key"] for c in client.calls}
    assert "question/opinionsqa/Q1.json" in keys
    assert "question/opinionsqa/index.json" in keys

    # Payload integrity: the body for Q1 still parses and carries the
    # cross-model rollup the site expects.
    q1_body = next(
        c["Body"] for c in client.calls if c["Key"] == "question/opinionsqa/Q1.json"
    )
    payload = json.loads(q1_body)
    assert payload["dataset"] == "opinionsqa"
    assert payload["key"] == "Q1"


def test_publish_questions_keeps_full_dataset_on_disk_with_uploader(tmp_path: Path):
    """NTIA is `full` → per-question lands locally even with uploader present."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "ntia_run.json").write_text(
        json.dumps(
            _make_question_result(
                "openrouter/anthropic/claude-haiku-4-5", "ntia", "NQ1"
            )
        )
    )

    out_dir = tmp_path / "site_data"
    uploader, client = _uploader()
    counts = publish_questions(results_dir, out_dir, r2_uploader=uploader)

    assert counts == {"questions": 1, "datasets": 1}
    assert (out_dir / "question" / "ntia" / "NQ1.json").exists()
    assert (out_dir / "question" / "ntia" / "index.json").exists()
    assert client.calls == []


def test_publish_questions_without_uploader_writes_all_locally(tmp_path: Path):
    """Local-only mode (no uploader) preserves pre-sb-sjs behavior."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "gated_run.json").write_text(
        json.dumps(
            _make_question_result(
                "openrouter/anthropic/claude-haiku-4-5", "opinionsqa", "Q1"
            )
        )
    )

    out_dir = tmp_path / "site_data"
    counts = publish_questions(results_dir, out_dir, r2_uploader=None)

    assert counts == {"questions": 1, "datasets": 1}
    assert (out_dir / "question" / "opinionsqa" / "Q1.json").exists()


# -- publish_runs routing ---------------------------------------------------


def test_publish_runs_routes_gated_run_and_config_to_r2(tmp_path: Path):
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    # Use a deterministic run_id-shaped filename so _run_id_from_path keys work.
    (results_dir / "20260101-aaa.json").write_text(
        json.dumps(
            _make_run_result("openrouter/anthropic/claude-haiku-4-5", "opinionsqa")
        )
    )

    out_dir = tmp_path / "site_data"
    uploader, client = _uploader()
    counts = publish_runs(results_dir, out_dir, r2_uploader=uploader)

    assert counts["runs"] == 1
    assert counts["configs"] == 1
    # runs-index always stays public/local.
    assert (out_dir / "runs-index.json").exists()
    # Per-run + per-config land in R2 for gated datasets.
    keys = {c["Key"] for c in client.calls}
    assert any(k.startswith("run/") and k.endswith(".json") for k in keys)
    assert any(k.startswith("config/") and k.endswith(".json") for k in keys)
    # Local run/ + config/ dirs exist (publish_runs creates them) but contain
    # no JSON for the gated run.
    assert list((out_dir / "run").glob("*.json")) == []
    assert list((out_dir / "config").glob("*.json")) == []


def test_publish_runs_keeps_full_run_local(tmp_path: Path):
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-bbb.json").write_text(
        json.dumps(_make_run_result("openrouter/anthropic/claude-haiku-4-5", "ntia"))
    )

    out_dir = tmp_path / "site_data"
    uploader, client = _uploader()
    counts = publish_runs(results_dir, out_dir, r2_uploader=uploader)

    assert counts["runs"] == 1
    assert client.calls == []
    assert list((out_dir / "run").glob("*.json")) != []
    assert list((out_dir / "config").glob("*.json")) != []


def test_publish_runs_runs_index_always_local_even_with_gated_runs(tmp_path: Path):
    """The cross-dataset catalog stays public so the site can route to it."""
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "20260101-ccc.json").write_text(
        json.dumps(
            _make_run_result("openrouter/anthropic/claude-haiku-4-5", "opinionsqa")
        )
    )

    out_dir = tmp_path / "site_data"
    uploader, _client = _uploader()
    publish_runs(results_dir, out_dir, r2_uploader=uploader)

    index = json.loads((out_dir / "runs-index.json").read_text())
    assert index["n_runs"] == 1
    assert index["runs"][0]["dataset"] == "opinionsqa"
