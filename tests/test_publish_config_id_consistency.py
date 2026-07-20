"""Lock in the config_id invariant across publish-data and publish-runs (sb-2iz).

Both pipelines must emit the same ``config_id`` for the same result, otherwise
leaderboard rows link to ``/config/<id>/`` pages that don't exist (404).

The bug this guards against:

- ``publish-data`` (``_build_entry``) and ``publish-runs`` both call
  ``build_config_id(provider, ...)`` which reads ``parsed.framework`` from
  ``parse_provider``. If either path ever switches to ``provider_framework``
  (the human-facing taxonomy: ``raw`` / ``product`` / ``baseline``) for the
  slug while the other keeps ``parsed.framework`` (the path-derived label:
  ``raw`` / ``althing`` / ``ensemble`` / ``baseline``), the prefix
  diverges — e.g. an OpenRouter raw call becomes ``openrouter--gpt-4o-mini``
  on one side and ``raw--gpt-4o-mini`` on the other.
"""

from __future__ import annotations

import json
from pathlib import Path

from synthbench.config_id import build_config_id
from synthbench.publish import (
    _build_entry,
    publish_leaderboard_data,
    publish_runs,
)

# Provider strings spanning every shape that hits production.
PROVIDER_FIXTURES = [
    "openrouter/openai/gpt-4o-mini",
    "openrouter/anthropic/claude-haiku-4-5",
    "openrouter/meta-llama/llama-3.3-70b-instruct",
    "openrouter/google/gemini-2.5-flash-lite",
    "raw-anthropic/claude-haiku-4-5-20251001",
    "raw-gemini/gemini-2.5-flash-lite",
    "althing/openrouter/openai/gpt-4o-mini",
    "althing/openrouter/anthropic/claude-haiku-4-5",
    "althing/claude-haiku-4-5-20251001",
    "althing/gemini-2.5-flash-lite",
    "ensemble/3-model-blend",
    "random-baseline",
    "majority-baseline",
]


def _result(provider: str, dataset: str = "globalopinionqa") -> dict:
    """Minimal SynthBench result dict with the fields publish.py reads."""
    return {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "timestamp": "2026-04-14T00:00:00Z",
        "config": {
            "provider": provider,
            "dataset": dataset,
            "temperature": None,
            "prompt_template": None,
            "samples_per_question": 10,
            "n_evaluated": 100,
            "n_requested": 100,
        },
        "scores": {
            "sps": 0.5,
            "p_dist": 0.5,
            "p_rank": 0.5,
            "p_refuse": 0.5,
        },
        "aggregate": {
            "mean_jsd": 0.1,
            "mean_kendall_tau": 0.5,
            "n_questions": 100,
            "per_metric_ci": {"sps": [0.45, 0.55]},
        },
        "per_question": [],
    }


def _runs_path_config_id(result: dict) -> str:
    """Mirror the publish-runs config_id derivation in publish.py:1131."""
    cfg = result["config"]
    template = cfg.get("prompt_template")
    if template:
        stem = (
            Path(template).stem
            if ("/" in template or template.endswith(".md"))
            else template
        )
    else:
        stem = None
    slug, _ = build_config_id(
        cfg["provider"],
        dataset=cfg.get("dataset"),
        temperature=cfg.get("temperature"),
        template=stem,
        samples_per_question=cfg.get("samples_per_question"),
        question_set_hash=cfg.get("question_set_hash"),
    )
    return slug


def test_build_entry_matches_publish_runs_config_id():
    """Per-provider: leaderboard entry config_id == publish-runs config_id.

    Surgical guard: catches divergence at the function level even if the
    end-to-end pipeline is fine for the current fixture set.
    """
    for provider in PROVIDER_FIXTURES:
        result = _result(provider)
        entry_cid = _build_entry(result, rank=1)["config_id"]
        runs_cid = _runs_path_config_id(result)
        assert entry_cid == runs_cid, (
            f"config_id divergence for provider={provider!r}: "
            f"_build_entry={entry_cid!r} vs publish_runs={runs_cid!r}. "
            f"Leaderboard links to /config/{entry_cid}/ would 404."
        )


def test_publish_pipeline_config_ids_match_runs_index(tmp_path):
    """End-to-end: every config_id in leaderboard.json must exist in runs-index.json.

    This is the live invariant the founder bug relied on. If it ever breaks,
    the Explore page and leaderboard row links 404.
    """
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    for i, provider in enumerate(PROVIDER_FIXTURES):
        result = _result(provider)
        # Vary timestamp so run_id stems are unique and parseable.
        slug = provider.replace("/", "_").replace(" ", "_")
        path = results_dir / f"globalopinionqa_{slug}_20260414_{i:06d}.json"
        with open(path, "w") as f:
            json.dump(result, f)

    leaderboard_path = tmp_path / "leaderboard.json"
    publish_leaderboard_data(results_dir, leaderboard_path)

    runs_out = tmp_path / "runs-out"
    publish_runs(results_dir, runs_out)

    with open(leaderboard_path) as f:
        leaderboard = json.load(f)
    with open(runs_out / "runs-index.json") as f:
        runs_index = json.load(f)

    leaderboard_cids = {e["config_id"] for e in leaderboard["entries"]}
    runs_cids = {r["config_id"] for r in runs_index["runs"]}

    missing = leaderboard_cids - runs_cids
    assert not missing, (
        f"Leaderboard config_ids missing from runs-index.json — these would "
        f"404 on /config/<id>/: {sorted(missing)}"
    )


# Canonical framework prefix per provider shape. Locks in the post-fix
# decision that ``openrouter/...`` is a gateway, not a framework — the slug
# uses the underlying ``raw`` framework so direct vs gateway calls dedupe.
# If anyone ever reverts this, the founder bug returns: leaderboard rows
# link to ``/config/openrouter--.../`` pages that don't exist.
EXPECTED_FRAMEWORK_PREFIX = {
    "openrouter/openai/gpt-4o-mini": "raw",
    "openrouter/anthropic/claude-haiku-4-5": "raw",
    "openrouter/meta-llama/llama-3.3-70b-instruct": "raw",
    "openrouter/google/gemini-2.5-flash-lite": "raw",
    "raw-anthropic/claude-haiku-4-5-20251001": "raw",
    "raw-gemini/gemini-2.5-flash-lite": "raw",
    "althing/openrouter/openai/gpt-4o-mini": "althing",
    "althing/openrouter/anthropic/claude-haiku-4-5": "althing",
    "althing/claude-haiku-4-5-20251001": "althing",
    "althing/gemini-2.5-flash-lite": "althing",
    "ensemble/3-model-blend": "ensemble",
    "random-baseline": "baseline",
    "majority-baseline": "baseline",
}


def test_canonical_framework_prefix_in_config_id():
    """Both publish paths must emit the canonical framework prefix.

    The original founder bug was a leaderboard config_id of
    ``openrouter--gpt-4o-mini--...`` while runs-index used ``raw--...`` —
    same model, different prefix, dead link. This test pins down the
    expected prefix per provider shape so a regression in ``_parse_path``
    (or anyone replacing ``parsed.framework`` with the human-facing
    ``provider_framework(...)`` taxonomy in the slug) trips immediately.
    """
    for provider, expected_prefix in EXPECTED_FRAMEWORK_PREFIX.items():
        result = _result(provider)
        entry_cid = _build_entry(result, rank=1)["config_id"]
        assert entry_cid.startswith(f"{expected_prefix}--"), (
            f"Expected leaderboard config_id for {provider!r} to start with "
            f"{expected_prefix!r}--, got {entry_cid!r}"
        )


def test_refusal_detector_version_stamp_never_changes_config_id():
    """The v2 detector stamp is metadata-only: config_ids must be stable.

    ``config.refusal_detector_version`` (absent = v1 on historical runs)
    must never feed ``build_config_id`` — otherwise every rebaselined run
    would mint a new /config/<id>/ URL and orphan its history. Mirrors the
    additive-knob guarantee #325 established for ``effort``.
    """
    for provider in PROVIDER_FIXTURES:
        base = _result(provider)
        stamped = _result(provider)
        stamped["config"]["refusal_detector_version"] = 2
        base_cid = _build_entry(base, rank=1)["config_id"]
        stamped_cid = _build_entry(stamped, rank=1)["config_id"]
        assert base_cid == stamped_cid, (
            f"config_id changed under refusal_detector_version stamp for "
            f"{provider!r}: {base_cid!r} vs {stamped_cid!r}"
        )


def test_all_committed_config_ids_unchanged_by_detector_stamp():
    """Recompute every committed run's config_id with and without the stamp.

    The #325-style regression sweep: 0 changes across the entire committed
    corpus.
    """
    results_dir = Path(__file__).resolve().parent.parent / "leaderboard-results"
    checked = 0
    for jf in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("benchmark") != "synthbench":
            continue
        cfg = data.get("config") or {}
        if not cfg.get("provider"):
            continue
        original = _runs_path_config_id(data)
        stamped = json.loads(json.dumps(data))
        stamped["config"]["refusal_detector_version"] = 2
        assert _runs_path_config_id(stamped) == original, jf.name
        checked += 1
    assert checked > 50  # the corpus is really there
