"""Publish-time rehydration of stripped gated human distributions (#308)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthbench import human_distributions as hd
from synthbench.publish import GatedPublishError, publish_questions, publish_runs
from synthbench.r2_upload import R2Config, R2Uploader


class _FakeS3Client:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str):
        self.objects[Key] = Body
        return {"ETag": "fake"}


def _uploader() -> tuple[R2Uploader, _FakeS3Client]:
    client = _FakeS3Client()
    cfg = R2Config("acct", "ak", "sk", "synthbench-data-test")
    return R2Uploader(cfg, client=client), client


def _stripped_result(dataset: str = "opinionsqa") -> dict:
    return {
        "benchmark": "synthbench",
        "config": {
            "provider": "openrouter/openai/gpt-4o-mini",
            "dataset": dataset,
            "n_evaluated": 1,
        },
        "scores": {"sps": 0.9},
        "aggregate": {"mean_jsd": 0.1, "mean_kendall_tau": 0.5, "n_questions": 1},
        "stripped_fields": ["human_distribution"],
        "per_question": [
            {
                "key": "Q1",
                "text": "q?",
                "options": ["A", "B"],
                "model_distribution": {"A": 0.5, "B": 0.5},
                "jsd": 0.1,
                "kendall_tau": 0.5,
                "parity": 0.8,
                "n_samples": 10,
                "model_refusal_rate": 0.0,
                "human_refusal_rate": 0.05,
            }
        ],
    }


@pytest.fixture(autouse=True)
def _isolated_registry(monkeypatch, tmp_path):
    canon_dir = tmp_path / "canon"
    canon_dir.mkdir()
    monkeypatch.setenv("SYNTHBENCH_HUMAN_DISTRIBUTIONS_DIR", str(canon_dir))
    monkeypatch.setattr(hd, "_load_from_r2", lambda base, local_dir: None)
    monkeypatch.setattr(hd, "_load_from_adapter", lambda base: None)
    hd.clear_cache()
    yield canon_dir
    hd.clear_cache()


def _write_canonical(canon_dir: Path, dataset: str) -> None:
    (canon_dir / f"{dataset}.json").write_text(
        json.dumps({"dataset": dataset, "distributions": {"Q1": {"A": 0.6, "B": 0.4}}})
    )


def _write_result(tmp_path: Path) -> Path:
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "run_one.json").write_text(json.dumps(_stripped_result()))
    return results_dir


def test_publish_runs_rehydrates_stripped_gated_rows(tmp_path, _isolated_registry):
    _write_canonical(_isolated_registry, "opinionsqa")
    results_dir = _write_result(tmp_path)
    uploader, client = _uploader()

    counts = publish_runs(
        results_dir, tmp_path / "out", r2_uploader=uploader, strict_gating=True
    )
    assert counts["gated_skipped"] == 0
    run_keys = [k for k in client.objects if k.startswith("run/")]
    assert run_keys
    payload = json.loads(client.objects[run_keys[0]])
    assert payload["per_question"][0]["human_distribution"] == {
        "A": 0.6,
        "B": 0.4,
    }


def test_publish_questions_rehydrates_stripped_gated_rows(tmp_path, _isolated_registry):
    _write_canonical(_isolated_registry, "opinionsqa")
    results_dir = _write_result(tmp_path)
    uploader, client = _uploader()

    publish_questions(
        results_dir, tmp_path / "out", r2_uploader=uploader, strict_gating=True
    )
    key = "question/opinionsqa/Q1.json"
    assert key in client.objects
    payload = json.loads(client.objects[key])
    assert payload["human_distribution"] == {"A": 0.6, "B": 0.4}


def test_publish_runs_strict_fails_loudly_without_canonical_source(tmp_path):
    results_dir = _write_result(tmp_path)
    uploader, _client = _uploader()
    with pytest.raises(GatedPublishError, match="canonical"):
        publish_runs(
            results_dir,
            tmp_path / "out",
            r2_uploader=uploader,
            strict_gating=True,
        )


def test_publish_runs_non_strict_warns_and_ships_without_distribution(tmp_path, caplog):
    results_dir = _write_result(tmp_path)
    uploader, client = _uploader()
    with caplog.at_level("WARNING"):
        counts = publish_runs(results_dir, tmp_path / "out", r2_uploader=uploader)
    assert counts["gated_skipped"] == 0
    assert any("no canonical source" in r.message for r in caplog.records)
    run_keys = [k for k in client.objects if k.startswith("run/")]
    payload = json.loads(client.objects[run_keys[0]])
    assert "human_distribution" not in payload["per_question"][0]


def test_publish_runs_no_uploader_skips_rehydration(tmp_path):
    """Fail-closed path unchanged: without an uploader, gated artifacts are
    skipped and no canonical lookup happens (no error, no artifact)."""
    results_dir = _write_result(tmp_path)
    counts = publish_runs(results_dir, tmp_path / "out", r2_uploader=None)
    assert counts["gated_skipped"] > 0


def test_publish_runs_leaves_embedded_distributions_alone(tmp_path, _isolated_registry):
    """Unstripped rows (fresh submissions) never trigger a canonical lookup."""
    result = _stripped_result()
    result["per_question"][0]["human_distribution"] = {"A": 0.7, "B": 0.3}
    del result["stripped_fields"]
    results_dir = tmp_path / "raw"
    results_dir.mkdir()
    (results_dir / "run_one.json").write_text(json.dumps(result))
    uploader, client = _uploader()
    # No canonical artifact exists — would raise under strict if consulted.
    publish_runs(
        results_dir, tmp_path / "out", r2_uploader=uploader, strict_gating=True
    )
    run_keys = [k for k in client.objects if k.startswith("run/")]
    payload = json.loads(client.objects[run_keys[0]])
    assert payload["per_question"][0]["human_distribution"] == {
        "A": 0.7,
        "B": 0.3,
    }
