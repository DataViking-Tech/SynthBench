"""Reasoning-effort as a first-class config dimension.

Covers the whole thread: CLI kwarg gating → provider request payloads →
config_id identity (CRITICAL: effort-absent runs must hash identically to
pre-effort SynthBench, so no existing leaderboard config_id shifts) →
leaderboard grouping/display → tier-1 validation enum.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import click
import pytest

from synthbench.cli import _provider_kwargs
from synthbench.config_id import build_config_id
from synthbench.validation import Severity, validate_submission


# ---------------------------------------------------------------------------
# CLI kwarg gating
# ---------------------------------------------------------------------------


class TestProviderKwargsEffort:
    @pytest.mark.parametrize(
        "provider", ["raw-anthropic", "raw-openai", "raw-gemini", "openrouter"]
    )
    def test_effort_threaded_to_supported_providers(self, provider):
        kwargs = _provider_kwargs(provider, model="m", effort="high")
        assert kwargs["effort"] == "high"

    @pytest.mark.parametrize(
        "provider", ["ollama", "http", "random", "majority", "population-average"]
    )
    def test_effort_rejected_for_unsupported_providers(self, provider):
        """No reasoning control to thread to → loud error, never a silently
        tagged run (mirrors the --temperature strictness from #304)."""
        with pytest.raises(click.UsageError, match="--effort is not supported"):
            _provider_kwargs(provider, model="m", effort="low")

    def test_effort_rejected_for_synthpanel_with_pointer(self):
        with pytest.raises(click.UsageError, match="synthpanel"):
            _provider_kwargs("synthpanel", model="haiku", effort="medium")

    def test_absent_effort_adds_no_kwarg(self):
        kwargs = _provider_kwargs("raw-anthropic", model="m")
        assert "effort" not in kwargs


# ---------------------------------------------------------------------------
# Provider payload threading (mocked SDK clients asserting the request)
# ---------------------------------------------------------------------------


def _fake_chat_client(content: str = "A"):
    choice = SimpleNamespace(
        message=SimpleNamespace(content=content), finish_reason="stop"
    )
    resp = SimpleNamespace(choices=[choice], usage=None)
    create = AsyncMock(return_value=resp)
    return (
        SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
            close=AsyncMock(),
        ),
        create,
    )


@pytest.mark.asyncio
async def test_openrouter_threads_reasoning_effort(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    from synthbench.providers.openrouter import OpenRouterProvider

    provider = OpenRouterProvider(model="anthropic/claude-sonnet-4.6", effort="high")
    client, create = _fake_chat_client()
    provider._client = client

    resp = await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert kwargs["extra_body"] == {"reasoning": {"effort": "high"}}
    # 8-token cap replaced by the per-tier ceiling (reasoning tokens count
    # against max_tokens on OpenRouter): 0.8 * 30720 = 24576 budget for
    # Anthropic-routed models — same as the raw-anthropic "high" tier.
    assert kwargs["max_tokens"] == 30720
    assert resp.selected_option == "alpha"


@pytest.mark.asyncio
async def test_openrouter_without_effort_sends_no_reasoning(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    from synthbench.providers.openrouter import OpenRouterProvider

    provider = OpenRouterProvider(model="openai/gpt-4o-mini")
    client, create = _fake_chat_client()
    provider._client = client

    await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert "extra_body" not in kwargs
    assert kwargs["max_tokens"] == 8


@pytest.mark.asyncio
async def test_raw_anthropic_threads_thinking_budget(monkeypatch):
    pytest.importorskip("anthropic")
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    provider = RawAnthropicProvider(model="claude-sonnet-4-5", effort="medium")
    # Thinking responses lead with a thinking block; the answer is the
    # first text block.
    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking="…deliberation…"),
            SimpleNamespace(type="text", text="B"),
        ],
        stop_reason="end_turn",
        usage=None,
    )
    create = AsyncMock(return_value=fake_message)
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(create=create), close=AsyncMock()
    )

    resp = await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert kwargs["thinking"] == {"type": "enabled", "budget_tokens": 8192}
    assert kwargs["max_tokens"] > 8192  # ceiling must exceed the budget
    assert kwargs["temperature"] == 1.0
    assert resp.selected_option == "beta"


@pytest.mark.asyncio
async def test_raw_anthropic_without_effort_unchanged(monkeypatch):
    pytest.importorskip("anthropic")
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    provider = RawAnthropicProvider(model="claude-haiku-4-5")
    fake_message = SimpleNamespace(
        content=[SimpleNamespace(text="A")], stop_reason="end_turn", usage=None
    )
    create = AsyncMock(return_value=fake_message)
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(create=create), close=AsyncMock()
    )

    resp = await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert "thinking" not in kwargs
    assert kwargs["max_tokens"] == 8
    assert resp.selected_option == "alpha"


def test_raw_anthropic_effort_rejects_custom_temperature():
    pytest.importorskip("anthropic")
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    with pytest.raises(ValueError, match="temperature=1"):
        RawAnthropicProvider(model="claude-sonnet-4-5", temperature=0.7, effort="high")


@pytest.mark.asyncio
async def test_raw_openai_threads_reasoning_effort(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    provider = RawOpenAIProvider(model="o4-mini", effort="low")
    client, create = _fake_chat_client()
    provider._client = client

    await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert kwargs["extra_body"] == {"reasoning_effort": "low"}
    assert kwargs["max_completion_tokens"] == 4096
    # Reasoning models reject max_tokens and pin sampling.
    assert "max_tokens" not in kwargs
    assert "temperature" not in kwargs


def test_raw_openai_effort_rejects_custom_temperature(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    with pytest.raises(ValueError, match="temperature"):
        RawOpenAIProvider(model="o4-mini", temperature=0.3, effort="low")


@pytest.mark.asyncio
async def test_raw_gemini_threads_reasoning_effort(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    from synthbench.providers.raw_gemini import RawGeminiProvider

    provider = RawGeminiProvider(model="gemini-2.5-flash", effort="high")
    client, create = _fake_chat_client()
    provider._client = client

    await provider.respond("Q?", ["alpha", "beta"])

    kwargs = create.call_args.kwargs
    assert kwargs["extra_body"] == {"reasoning_effort": "high"}
    assert kwargs["max_tokens"] > 8


@pytest.mark.parametrize(
    ("provider_env", "module", "cls"),
    [
        ("OPENROUTER_API_KEY", "synthbench.providers.openrouter", "OpenRouterProvider"),
        ("OPENAI_API_KEY", "synthbench.providers.raw_openai", "RawOpenAIProvider"),
        ("GEMINI_API_KEY", "synthbench.providers.raw_gemini", "RawGeminiProvider"),
    ],
)
def test_unknown_effort_level_rejected(monkeypatch, provider_env, module, cls):
    pytest.importorskip("openai")
    monkeypatch.setenv(provider_env, "test-key")
    import importlib

    provider_cls = getattr(importlib.import_module(module), cls)
    with pytest.raises(ValueError, match="unknown effort level"):
        provider_cls(effort="maximum")


# ---------------------------------------------------------------------------
# config_id identity
# ---------------------------------------------------------------------------


class TestConfigIdEffort:
    # Golden slugs computed on main BEFORE the effort dimension landed.
    # If any of these change, every historical /config/<id> URL and every
    # published config_id breaks — this is the backstop.
    GOLDEN_PRE_EFFORT = [
        (
            dict(
                provider="raw-anthropic/claude-haiku-4-5-20251001",
                dataset="opinionsqa",
                temperature=1.0,
                samples_per_question=30,
                question_set_hash="abc123",
            ),
            "raw--claude-haiku-4-5--t1.0--tplcurrent--97a8eea5",
        ),
        (
            dict(
                provider="openrouter/openai/gpt-4o-mini",
                dataset="subpop",
                samples_per_question=30,
            ),
            "raw--gpt-4o-mini--tdefault--tplcurrent--704154ed",
        ),
        (
            dict(
                provider="synthpanel/openrouter/anthropic/claude-haiku-4-5 t=0.85 tpl=current",
                dataset="opinionsqa",
            ),
            "synthpanel--claude-haiku-4-5--t0.85--tplcurrent--9f9ed2bc",
        ),
        (
            dict(
                provider="random-baseline",
                dataset="globalopinionqa",
                samples_per_question=30,
            ),
            "baseline--random-baseline--tdefault--tplcurrent--434f20fe",
        ),
    ]

    @pytest.mark.parametrize(("kwargs", "expected"), GOLDEN_PRE_EFFORT)
    def test_effort_absent_config_ids_are_backward_stable(self, kwargs, expected):
        kwargs = dict(kwargs)
        provider = kwargs.pop("provider")
        slug, _ = build_config_id(provider, **kwargs)
        assert slug == expected

    @pytest.mark.parametrize(("kwargs", "expected"), GOLDEN_PRE_EFFORT)
    def test_explicit_effort_none_matches_omitted(self, kwargs, expected):
        kwargs = dict(kwargs)
        provider = kwargs.pop("provider")
        slug, _ = build_config_id(provider, effort=None, **kwargs)
        assert slug == expected

    def test_effort_levels_hash_distinctly(self):
        base = dict(dataset="opinionsqa", samples_per_question=30)
        slugs = {
            build_config_id(
                "openrouter/anthropic/claude-sonnet-4.6", effort=level, **base
            )[0]
            for level in (None, "low", "medium", "high")
        }
        assert len(slugs) == 4

    def test_effort_appears_in_slug_and_knobs(self):
        slug, parsed = build_config_id(
            "openrouter/anthropic/claude-sonnet-4.6",
            dataset="opinionsqa",
            effort="high",
        )
        assert "--effhigh--" in slug
        assert parsed.knobs["effort"] == "high"

    def test_effort_knob_parsed_from_provider_string(self):
        """A provider string carrying `effort=high` (synthpanel-style knob
        tokens) resolves the same as the explicit kwarg."""
        via_knob, _ = build_config_id(
            "synthpanel/x/y/z effort=high", dataset="opinionsqa"
        )
        via_kwarg, _ = build_config_id(
            "synthpanel/x/y/z", dataset="opinionsqa", effort="high"
        )
        assert via_knob == via_kwarg


# ---------------------------------------------------------------------------
# Leaderboard grouping + display
# ---------------------------------------------------------------------------


def _result(provider: str, sps: float, effort: str | None = None, **cfg_extra):
    cfg = {
        "provider": provider,
        "dataset": "opinionsqa",
        "n_evaluated": 100,
        "samples_per_question": 30,
    }
    if effort is not None:
        cfg["effort"] = effort
    cfg.update(cfg_extra)
    return {
        "benchmark": "synthbench",
        "timestamp": "2026-07-15T00:00:00+00:00",
        "config": cfg,
        "aggregate": {
            "composite_parity": sps,
            "mean_jsd": 0.1,
            "median_jsd": 0.1,
            "mean_kendall_tau": 0.5,
            "n_questions": 100,
        },
        "per_question": [],
    }


class TestLeaderboardEffort:
    def test_config_key_distinguishes_effort_levels(self):
        from synthbench.leaderboard import _config_key

        low = _config_key(_result("openrouter/anthropic/claude-sonnet-4.6", 0.7, "low"))
        high = _config_key(
            _result("openrouter/anthropic/claude-sonnet-4.6", 0.8, "high")
        )
        absent = _config_key(_result("openrouter/anthropic/claude-sonnet-4.6", 0.75))
        assert low != high != absent and low != absent

    def test_entries_carry_effort_and_render_column(self):
        from synthbench.leaderboard import build_leaderboard

        md, lb = build_leaderboard(
            [
                _result("openrouter/anthropic/claude-sonnet-4.6", 0.80, "high"),
                _result("openrouter/anthropic/claude-sonnet-4.6", 0.72, "low"),
                _result("openrouter/anthropic/claude-sonnet-4.6", 0.75),
            ]
        )
        efforts = {e.get("effort") for e in lb["summary"]}
        assert efforts == {"high", "low", None}
        # Three distinct rows — effort variants must never collapse.
        assert len(lb["summary"]) == 3
        assert "Effort" in md
        assert "| high |" in md and "| low |" in md and "| default |" in md

    def test_effort_free_leaderboard_has_no_effort_column(self):
        from synthbench.leaderboard import build_leaderboard

        md, _ = build_leaderboard(
            [_result("openrouter/anthropic/claude-sonnet-4.6", 0.75)]
        )
        assert "Effort" not in md

    def test_publish_dedup_keeps_effort_variants_separate(self):
        from synthbench.publish import _dedup_results

        results = [
            _result("openrouter/anthropic/claude-sonnet-4.6", 0.80, "high"),
            _result("openrouter/anthropic/claude-sonnet-4.6", 0.75),
        ]
        # per_question rows so _effective_n is comparable
        deduped = _dedup_results(results)
        assert len(deduped) == 2


# ---------------------------------------------------------------------------
# Tier-1 validation
# ---------------------------------------------------------------------------


def _minimal_submission(effort=None):
    cfg = {
        "provider": "openrouter/anthropic/claude-sonnet-4.6",
        "dataset": "opinionsqa",
    }
    if effort is not None:
        cfg["effort"] = effort
    return {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "config": cfg,
        "aggregate": {
            "mean_jsd": 0.1,
            "mean_kendall_tau": 0.5,
            "composite_parity": 0.75,
            "n_questions": 1,
        },
        "per_question": [
            {
                "key": "Q1",
                "human_distribution": {"a": 0.6, "b": 0.4},
                "model_distribution": {"a": 0.5, "b": 0.5},
                "jsd": 0.05,
                "kendall_tau": 1.0,
                "n_samples": 30,
            }
        ],
    }


class TestValidationEffortEnum:
    @pytest.mark.parametrize("level", ["low", "medium", "high"])
    def test_known_levels_pass_tier1(self, level):
        report = validate_submission(
            _minimal_submission(effort=level), tier1=True, tier2=False
        )
        assert not [
            i
            for i in report.issues
            if i.path == "config.effort" and i.severity == Severity.ERROR
        ]

    def test_absent_effort_passes_tier1(self):
        report = validate_submission(_minimal_submission(), tier1=True, tier2=False)
        assert not [i for i in report.issues if i.path == "config.effort"]

    @pytest.mark.parametrize("bad", ["maximum", "HIGH", 3, ""])
    def test_unknown_levels_rejected(self, bad):
        report = validate_submission(
            _minimal_submission(effort=bad), tier1=True, tier2=False
        )
        errs = [
            i
            for i in report.issues
            if i.path == "config.effort" and i.severity == Severity.ERROR
        ]
        assert errs, f"effort={bad!r} should be rejected"
        assert errs[0].code == "SCHEMA_ENUM"
