"""Runnable provider/model IDs in leaderboard.json entries (sb-7ly / #297).

``/data/leaderboard.json`` historically put display labels (e.g.
``Althing (Gemini Flash Lite)``) in both ``provider`` and ``model``.
Consumers (Althing #519) need *runnable* IDs so they can pipe a row's model
straight to OpenRouter without parsing display names. ``_build_entry`` now also
emits:

- ``provider_id`` — framework/runner (raw / althing / ensemble / baseline)
- ``model_id``    — an OpenRouter ``<vendor>/<model>`` slug

This locks the exact ID per production provider shape. The key correctness
guard: gateway routes preserve the on-path vendor verbatim (``meta-llama`` does
NOT collapse to ``meta``), and model version-dates are preserved, so the slug
stays a valid OpenRouter model id.
"""

from __future__ import annotations

from synthbench.config_id import runnable_ids
from synthbench.publish import _build_entry

# (provider string, expected provider_id, expected model_id) spanning every
# shape that hits production. Mirrors PROVIDER_FIXTURES in
# test_publish_config_id_consistency.py.
RUNNABLE_ID_FIXTURES = [
    ("openrouter/openai/gpt-4o-mini", "raw", "openai/gpt-4o-mini"),
    ("openrouter/openai/gpt-4o", "raw", "openai/gpt-4o"),
    ("openrouter/anthropic/claude-haiku-4-5", "raw", "anthropic/claude-haiku-4-5"),
    ("openrouter/anthropic/claude-sonnet-4", "raw", "anthropic/claude-sonnet-4"),
    ("openrouter/anthropic/claude-sonnet-4.6", "raw", "anthropic/claude-sonnet-4.6"),
    ("openrouter/google/gemini-2.5-flash", "raw", "google/gemini-2.5-flash"),
    ("openrouter/google/gemini-2.5-flash-lite", "raw", "google/gemini-2.5-flash-lite"),
    # Meta routes via OpenRouter keep the verbatim 'meta-llama' author — NOT the
    # dedup-canonical 'meta' from parse_provider.base_provider.
    (
        "openrouter/meta-llama/llama-3.3-70b-instruct",
        "raw",
        "meta-llama/llama-3.3-70b-instruct",
    ),
    # Direct vendor APIs map to the OpenRouter author; version dates preserved.
    (
        "raw-anthropic/claude-haiku-4-5-20251001",
        "raw",
        "anthropic/claude-haiku-4-5-20251001",
    ),
    ("raw-gemini/gemini-2.5-flash-lite", "raw", "google/gemini-2.5-flash-lite"),
    # Althing product layer over an OpenRouter-routed model.
    (
        "althing/openrouter/openai/gpt-4o-mini",
        "althing",
        "openai/gpt-4o-mini",
    ),
    (
        "althing/openrouter/anthropic/claude-haiku-4-5",
        "althing",
        "anthropic/claude-haiku-4-5",
    ),
    (
        "althing/openrouter/anthropic/claude-sonnet-4",
        "althing",
        "anthropic/claude-sonnet-4",
    ),
    (
        "althing/openrouter/google/gemini-2.5-flash-lite",
        "althing",
        "google/gemini-2.5-flash-lite",
    ),
    # Althing over a direct (bare) model — vendor inferred so the slug is
    # still OpenRouter-pipeable.
    (
        "althing/claude-haiku-4-5-20251001",
        "althing",
        "anthropic/claude-haiku-4-5-20251001",
    ),
    ("althing/gemini-2.5-flash-lite", "althing", "google/gemini-2.5-flash-lite"),
    ("althing/gpt-4o-mini", "althing", "openai/gpt-4o-mini"),
    # Ensemble + baselines have no OpenRouter equivalent — keep the native id.
    ("ensemble/3-model-blend", "ensemble", "3-model-blend"),
    ("random-baseline", "baseline", "random-baseline"),
    ("majority-baseline", "baseline", "majority-baseline"),
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
        "scores": {"sps": 0.5, "p_dist": 0.5, "p_rank": 0.5, "p_refuse": 0.5},
        "aggregate": {
            "mean_jsd": 0.1,
            "mean_kendall_tau": 0.5,
            "n_questions": 100,
            "per_metric_ci": {"sps": [0.45, 0.55]},
        },
        "per_question": [],
    }


def test_runnable_ids_per_provider_shape():
    """runnable_ids returns the canonical (provider_id, model_id) per shape."""
    for provider, exp_provider_id, exp_model_id in RUNNABLE_ID_FIXTURES:
        provider_id, model_id = runnable_ids(provider)
        assert (provider_id, model_id) == (exp_provider_id, exp_model_id), (
            f"runnable_ids({provider!r}) = {(provider_id, model_id)!r}, "
            f"expected {(exp_provider_id, exp_model_id)!r}"
        )


def test_runnable_ids_ignore_hyperparameter_knobs():
    """t=/tpl=/profile= suffixes don't change the runnable IDs."""
    base = "althing/openrouter/anthropic/claude-haiku-4-5"
    expected = ("althing", "anthropic/claude-haiku-4-5")
    assert runnable_ids(base) == expected
    assert runnable_ids(f"{base} t=0.85") == expected
    assert runnable_ids(f"{base} t=0.85 tpl=current") == expected
    assert runnable_ids(f"{base} t=0.85 tpl=current profile=fast") == expected


def test_build_entry_emits_runnable_ids():
    """_build_entry surfaces provider_id/model_id alongside display labels."""
    for provider, exp_provider_id, exp_model_id in RUNNABLE_ID_FIXTURES:
        entry = _build_entry(_result(provider), rank=1)
        assert entry["provider_id"] == exp_provider_id, provider
        assert entry["model_id"] == exp_model_id, provider
        # Display labels remain (backward compat); runnable IDs are separate.
        assert "provider" in entry and "model" in entry


def test_runnable_model_id_is_openrouter_pipeable_for_gateway_rows():
    """Every gateway/raw row's model_id is a '<vendor>/<model>' slug.

    Baselines and the ensemble have no OpenRouter equivalent and are exempt.
    """
    exempt = {"ensemble", "baseline"}
    for provider, provider_id, model_id in RUNNABLE_ID_FIXTURES:
        if provider_id in exempt:
            continue
        assert "/" in model_id, (
            f"{provider!r} → model_id={model_id!r} is not a pipeable "
            f"'<vendor>/<model>' slug"
        )
