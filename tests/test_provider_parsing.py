"""Tests for shared option parsing, refusal handling, retries, and temperature.

Covers the P1-8 / P1-7 fixes:

* option-text echo no longer parsed by first letter ("Better" != "Worse")
* substring fallback no longer matches across word boundaries
  ("Disagree" != "Agree", "I cannot" != "No")
* refusals detected via detect_refusal, not silently counted as options[0]
* parse failures are parse failures — never fabricated selections
* n_samples == 0 is not coerced back to samples_per_question
* provider exceptions are retried with backoff and classified as infra
  errors, not refusals
* --temperature actually reaches the request payload
* model aliases resolve to real model IDs
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import click
import pytest

from synthbench.providers._parsing import ParsedResponse, parse_option_response
from synthbench.providers._retry import call_with_retries, is_retryable_exception
from synthbench.providers.base import Distribution, Provider, ProviderError, Response
from synthbench.runner import BenchmarkRunner


# ---------------------------------------------------------------------------
# parse_option_response — table-driven
# ---------------------------------------------------------------------------

_OPTS_BETTER = ["Better", "Worse", "About the same"]
_OPTS_AGREE = ["Agree", "Disagree"]
_OPTS_YESNO = ["Yes", "No"]


@pytest.mark.parametrize(
    ("text", "options", "expected"),
    [
        # Option-text echo must match the echoed option, never its first letter.
        ("Better", _OPTS_BETTER, ParsedResponse(option="Better")),
        ("Worse", _OPTS_BETTER, ParsedResponse(option="Worse")),
        ("better", _OPTS_BETTER, ParsedResponse(option="Better")),
        ("  About the same.  ", _OPTS_BETTER, ParsedResponse(option="About the same")),
        # Superstring options must not be shadowed by their substrings.
        ("Disagree", _OPTS_AGREE, ParsedResponse(option="Disagree")),
        ("I'd say Disagree", _OPTS_AGREE, ParsedResponse(option="Disagree")),
        # Refusal text is a refusal — not a substring match into "No".
        ("I cannot answer that as an AI", _OPTS_YESNO, ParsedResponse(refusal=True)),
        ("I'm not able to share opinions.", _OPTS_YESNO, ParsedResponse(refusal=True)),
        ("As an AI, I have no view here.", _OPTS_YESNO, ParsedResponse(refusal=True)),
        # Bare letters, anchored: full-match forms only.
        ("B", _OPTS_BETTER, ParsedResponse(option="Worse")),
        ("b", _OPTS_BETTER, ParsedResponse(option="Worse")),
        ("(C)", _OPTS_BETTER, ParsedResponse(option="About the same")),
        ("A.", _OPTS_BETTER, ParsedResponse(option="Better")),
        (" C) ", _OPTS_BETTER, ParsedResponse(option="About the same")),
        # Letter out of range is a parse failure, not a crash.
        ("Z", _OPTS_YESNO, ParsedResponse()),
        # Containment respects word boundaries: "no" must not match "cannot".
        ("That is simply not knowable", _OPTS_YESNO, ParsedResponse()),
        ("My answer is no.", _OPTS_YESNO, ParsedResponse(option="No")),
        # Garbage and empty responses are parse failures.
        ("The moon is made of cheese", _OPTS_YESNO, ParsedResponse()),
        ("", _OPTS_YESNO, ParsedResponse()),
        ("   ", _OPTS_YESNO, ParsedResponse()),
    ],
)
def test_parse_option_response_table(text, options, expected):
    assert parse_option_response(text, options) == expected


def test_exact_option_echo_wins_over_refusal_patterns():
    """An option worded in the first person is a selection when echoed."""
    options = ["I don't know", "Yes", "No"]
    parsed = parse_option_response("I don't know", options)
    assert parsed == ParsedResponse(option="I don't know")


def test_parse_failure_flag():
    assert ParsedResponse().is_parse_failure
    assert not ParsedResponse(option="Yes").is_parse_failure
    assert not ParsedResponse(refusal=True).is_parse_failure


# ---------------------------------------------------------------------------
# Provider-level parsing (mocked SDK clients)
# ---------------------------------------------------------------------------


def _fake_openai_resp(content: str):
    choice = SimpleNamespace(
        message=SimpleNamespace(content=content),
        finish_reason="stop",
    )
    return SimpleNamespace(
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
    )


def _openai_provider_with(monkeypatch, content: str):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    provider = RawOpenAIProvider(model="gpt-4o-mini")
    provider._client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(return_value=_fake_openai_resp(content))
            )
        ),
        close=AsyncMock(),
    )
    return provider


@pytest.mark.asyncio
async def test_option_text_echo_regression(monkeypatch):
    """'Better' must select 'Better' — the old parser returned 'Worse'."""
    provider = _openai_provider_with(monkeypatch, "Better")
    resp = await provider.respond("Q?", _OPTS_BETTER)
    assert resp.selected_option == "Better"
    assert resp.refusal is False


@pytest.mark.asyncio
async def test_refusal_text_is_refusal_not_no(monkeypatch):
    provider = _openai_provider_with(monkeypatch, "I cannot answer that as an AI")
    resp = await provider.respond("Q?", _OPTS_YESNO)
    assert resp.selected_option is None
    assert resp.refusal is True


@pytest.mark.asyncio
async def test_garbage_is_parse_failure_not_first_option(monkeypatch):
    provider = _openai_provider_with(monkeypatch, "the moon is made of cheese")
    resp = await provider.respond("Q?", _OPTS_YESNO)
    assert resp.selected_option is None
    assert resp.refusal is False


@pytest.mark.asyncio
async def test_raw_anthropic_option_echo(monkeypatch):
    pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    fake_message = SimpleNamespace(
        content=[SimpleNamespace(text="Disagree")],
        stop_reason="end_turn",
        usage=None,
    )
    provider = RawAnthropicProvider(model="claude-haiku-4-5")
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(create=AsyncMock(return_value=fake_message)),
        close=AsyncMock(),
    )
    resp = await provider.respond("Q?", _OPTS_AGREE)
    assert resp.selected_option == "Disagree"


# ---------------------------------------------------------------------------
# Temperature threading + strict constructor kwargs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openai_temperature_reaches_request_payload(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    provider = RawOpenAIProvider(model="gpt-4o-mini", temperature=0.3)
    create = AsyncMock(return_value=_fake_openai_resp("A"))
    provider._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
        close=AsyncMock(),
    )
    await provider.respond("Q?", _OPTS_YESNO)
    assert create.call_args.kwargs["temperature"] == 0.3


@pytest.mark.asyncio
async def test_anthropic_temperature_reaches_request_payload(monkeypatch):
    pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    fake_message = SimpleNamespace(
        content=[SimpleNamespace(text="A")], stop_reason="end_turn", usage=None
    )
    provider = RawAnthropicProvider(model="claude-haiku-4-5", temperature=0.7)
    create = AsyncMock(return_value=fake_message)
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(create=create),
        close=AsyncMock(),
    )
    await provider.respond("Q?", _OPTS_YESNO)
    assert create.call_args.kwargs["temperature"] == 0.7


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "cls", "env"),
    [
        ("synthbench.providers.raw_gemini", "RawGeminiProvider", "GEMINI_API_KEY"),
        ("synthbench.providers.openrouter", "OpenRouterProvider", "OPENROUTER_API_KEY"),
        ("synthbench.providers.ollama", "OllamaProvider", None),
    ],
)
async def test_openai_shaped_providers_thread_temperature(
    monkeypatch, module, cls, env
):
    pytest.importorskip("openai")
    if env:
        monkeypatch.setenv(env, "test-key")
    import importlib

    provider_cls = getattr(importlib.import_module(module), cls)
    provider = provider_cls(temperature=0.25)
    create = AsyncMock(return_value=_fake_openai_resp("A"))
    provider._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
        close=AsyncMock(),
    )
    await provider.respond("Q?", _OPTS_YESNO)
    assert create.call_args.kwargs["temperature"] == 0.25


def test_default_temperature_is_one(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    assert RawOpenAIProvider()._temperature == 1.0


def test_constructors_reject_unknown_kwargs(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.majority_baseline import MajorityBaselineProvider
    from synthbench.providers.random_baseline import RandomBaselineProvider
    from synthbench.providers.raw_openai import RawOpenAIProvider

    with pytest.raises(TypeError):
        RawOpenAIProvider(model="gpt-4o-mini", bogus_option=1)
    with pytest.raises(TypeError):
        RandomBaselineProvider(model="gpt-4o-mini")
    with pytest.raises(TypeError):
        MajorityBaselineProvider(temperature=0.5)


def test_synthpanel_temperature_reaches_cli_command(monkeypatch, tmp_path):
    from synthbench.providers import synthpanel as sp_mod

    monkeypatch.setattr(sp_mod, "_HAS_SYNTH_PANEL_API", False)
    provider = sp_mod.SynthPanelProvider(
        model="haiku", temperature=0.4, synthpanel_path="/bin/echo"
    )
    cmd = provider._build_cmd("inst.yaml", "pers.yaml")
    idx = cmd.index("--temperature")
    assert cmd[idx + 1] == "0.4"


# ---------------------------------------------------------------------------
# CLI kwargs plumbing + alias table
# ---------------------------------------------------------------------------


def test_model_aliases_point_at_real_model_ids():
    from synthbench.cli import MODEL_ALIASES

    assert MODEL_ALIASES["sonnet"] == "claude-sonnet-4-5-20250929"
    assert MODEL_ALIASES["opus"] == "claude-opus-4-20250514"
    assert MODEL_ALIASES["haiku"] == "claude-haiku-4-5-20251001"
    assert MODEL_ALIASES["gemini-flash"] == "gemini-2.5-flash"
    assert MODEL_ALIASES["gemini-pro"] == "gemini-2.5-pro"
    # No alias may point at a retired preview or chimeric snapshot.
    for alias, resolved in MODEL_ALIASES.items():
        assert "preview" not in resolved, (alias, resolved)
        assert resolved != "claude-sonnet-4-5-20241022"
        assert resolved != "claude-opus-4-0-20250514"


def test_provider_kwargs_scopes_options_per_provider():
    from synthbench.cli import _provider_kwargs

    assert _provider_kwargs("raw-openai", model="gpt-4o-mini", temperature=0.5) == {
        "model": "gpt-4o-mini",
        "temperature": 0.5,
    }
    # Baselines take neither model nor temperature.
    assert _provider_kwargs("random", model="gpt-4o-mini") == {}
    # http gets url, not model.
    assert _provider_kwargs("http", model="x", url="http://e/") == {"url": "http://e/"}
    # ollama maps --url to base_url.
    assert _provider_kwargs("ollama", model="llama3", url="http://h:1/v1") == {
        "model": "llama3",
        "base_url": "http://h:1/v1",
    }


def test_provider_kwargs_rejects_unsupported_options():
    from synthbench.cli import _provider_kwargs

    with pytest.raises(click.UsageError):
        _provider_kwargs("random", temperature=0.7)
    with pytest.raises(click.UsageError):
        _provider_kwargs("raw-anthropic", model="m", url="http://e/")
    with pytest.raises(click.UsageError):
        _provider_kwargs("raw-openai", model="m", prompt_template="tpl.txt")


# ---------------------------------------------------------------------------
# Retry / infra-error classification
# ---------------------------------------------------------------------------


class _FakeRateLimitError(Exception):
    status_code = 429


class _FakeServerError(Exception):
    status_code = 503


class _FakeBadRequest(Exception):
    status_code = 400


def test_is_retryable_exception_classification():
    assert is_retryable_exception(_FakeRateLimitError())
    assert is_retryable_exception(_FakeServerError())
    assert is_retryable_exception(TimeoutError())
    assert is_retryable_exception(ConnectionError())
    assert not is_retryable_exception(_FakeBadRequest())
    assert not is_retryable_exception(ValueError("nope"))


@pytest.mark.asyncio
async def test_call_with_retries_retries_transient_then_succeeds():
    attempts = 0
    sleeps: list[float] = []

    async def flaky():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise _FakeRateLimitError("429")
        return "ok"

    async def fake_sleep(delay):
        sleeps.append(delay)

    result = await call_with_retries(flaky, sleep=fake_sleep)
    assert result == "ok"
    assert attempts == 3
    assert len(sleeps) == 2
    # Exponential growth between attempts (with jitter in [0.5, 1.0]).
    assert all(d > 0 for d in sleeps)


@pytest.mark.asyncio
async def test_call_with_retries_does_not_retry_non_transient():
    attempts = 0

    async def broken():
        nonlocal attempts
        attempts += 1
        raise _FakeBadRequest("400")

    async def fake_sleep(delay):  # pragma: no cover — must not be called
        raise AssertionError("should not sleep for non-retryable errors")

    with pytest.raises(_FakeBadRequest):
        await call_with_retries(broken, sleep=fake_sleep)
    assert attempts == 1


@pytest.mark.asyncio
async def test_call_with_retries_exhausts_and_raises():
    attempts = 0

    async def always_429():
        nonlocal attempts
        attempts += 1
        raise _FakeRateLimitError("429")

    async def fake_sleep(delay):
        pass

    with pytest.raises(_FakeRateLimitError):
        await call_with_retries(always_429, max_attempts=3, sleep=fake_sleep)
    assert attempts == 3


@pytest.mark.asyncio
async def test_provider_respond_retries_transient_errors(monkeypatch):
    """A transient 429 is retried inside the provider, not surfaced or
    miscounted as a refusal."""
    pytest.importorskip("openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from synthbench.providers.raw_openai import RawOpenAIProvider

    async def no_sleep(_delay):
        pass

    monkeypatch.setattr(asyncio, "sleep", no_sleep)

    provider = RawOpenAIProvider(model="gpt-4o-mini")
    create = AsyncMock(
        side_effect=[_FakeRateLimitError("429"), _fake_openai_resp("Yes")]
    )
    provider._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
        close=AsyncMock(),
    )
    resp = await provider.respond("Q?", _OPTS_YESNO)
    assert resp.selected_option == "Yes"
    assert resp.refusal is False
    assert create.call_count == 2


# ---------------------------------------------------------------------------
# Runner: n_samples == 0 stays 0; parse failures excluded from distribution
# ---------------------------------------------------------------------------


class _ZeroSampleProvider(Provider):
    """Distribution provider whose batch produced no usable samples."""

    @property
    def name(self) -> str:
        return "mock/zero-samples"

    @property
    def supports_distribution(self) -> bool:
        return True

    async def respond(self, question, options, *, persona=None):  # pragma: no cover
        raise AssertionError("distribution path should be used")

    async def get_distribution(
        self, question, options, *, persona=None, n_samples=None
    ):
        n = len(options)
        return Distribution(
            probabilities=[1.0 / n] * n,
            method="sampling",
            n_samples=0,
            n_parse_failures=n_samples or 0,
        )


@pytest.mark.asyncio
async def test_runner_does_not_coerce_zero_n_samples(mock_dataset):
    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=_ZeroSampleProvider(),
        samples_per_question=30,
    )
    result = await runner.run(n=2)
    for qr in result.questions:
        assert qr.n_samples == 0, "n_samples=0 must not be coerced to 30"
        assert qr.n_parse_failures == 30


class _BatchZeroSampleProvider(_ZeroSampleProvider):
    async def batch_get_distribution(
        self, questions, options_list, *, persona=None, n_samples=None
    ):
        return [
            await self.get_distribution(q, opts, n_samples=n_samples)
            for q, opts in zip(questions, options_list)
        ]


@pytest.mark.asyncio
async def test_batched_runner_does_not_coerce_zero_n_samples(mock_dataset):
    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=_BatchZeroSampleProvider(),
        samples_per_question=30,
    )
    result = await runner.run(n=2)
    for qr in result.questions:
        assert qr.n_samples == 0
        assert qr.n_parse_failures == 30


class _FlakyParseProvider(Provider):
    """Alternates a valid vote, a parse failure, and a refusal."""

    def __init__(self):
        self._n = 0

    @property
    def name(self) -> str:
        return "mock/flaky-parse"

    async def respond(self, question, options, *, persona=None):
        self._n += 1
        if self._n % 3 == 1:
            return Response(selected_option=options[1])
        if self._n % 3 == 2:
            return Response(selected_option=None, raw_text="garbled ###")
        return Response(selected_option=None, refusal=True)


@pytest.mark.asyncio
async def test_parse_failures_excluded_from_distribution(mock_dataset):
    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=_FlakyParseProvider(),
        samples_per_question=9,
        concurrency=1,
    )
    result = await runner.run(n=1)
    qr = result.questions[0]
    # 3 valid + 3 refusals count as samples; 3 parse failures do not.
    assert qr.n_samples == 6
    assert qr.n_parse_failures == 3
    assert qr.model_refusal_rate == pytest.approx(0.5)
    # All valid mass on options[1] after renormalization.
    assert qr.model_distribution[qr.options[1]] == pytest.approx(1.0)


def test_base_get_distribution_reports_parse_failures(mock_dataset):
    provider = _FlakyParseProvider()
    dist = asyncio.run(provider.get_distribution("Q?", ["a", "b"], n_samples=9))
    assert dist.n_samples == 6
    assert dist.n_parse_failures == 3
    assert dist.refusal_probability == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# run_validity: zero-sample questions flag / invalidate
# ---------------------------------------------------------------------------


def _validity_q(key: str, n_samples: int) -> dict:
    return {
        "key": key,
        "model_distribution": {"A": 0.6, "B": 0.3, "C": 0.1},
        "model_refusal_rate": 0.0,
        "n_samples": n_samples,
    }


def test_zero_sample_questions_flag_in_metrics():
    from synthbench.run_validity import compute_uniformity_metrics

    pq = [_validity_q(f"Q{i}", 30) for i in range(19)] + [_validity_q("Z0", 0)]
    metrics = compute_uniformity_metrics({"per_question": pq})
    assert metrics["n_zero_sample_questions"] == 1
    assert metrics["zero_sample_fraction"] == pytest.approx(0.05)


def test_run_with_many_zero_sample_questions_is_invalid():
    from synthbench.run_validity import is_invalid_run

    pq = [_validity_q(f"Q{i}", 30) for i in range(15)] + [
        _validity_q(f"Z{i}", 0) for i in range(5)
    ]
    invalid, reason, metrics = is_invalid_run({"per_question": pq})
    assert invalid
    assert reason.startswith("zero-sample")
    assert metrics["n_zero_sample_questions"] == 5


def test_run_with_isolated_zero_sample_question_stays_valid():
    from synthbench.run_validity import is_invalid_run

    pq = [_validity_q(f"Q{i}", 30) for i in range(19)] + [_validity_q("Z0", 0)]
    invalid, reason, metrics = is_invalid_run({"per_question": pq})
    assert not invalid
    assert metrics["n_zero_sample_questions"] == 1


def test_missing_n_samples_field_not_counted_as_zero():
    from synthbench.run_validity import compute_uniformity_metrics

    pq = [
        {"key": "Q1", "model_distribution": {"A": 0.9, "B": 0.1}},
        _validity_q("Q2", 30),
    ]
    metrics = compute_uniformity_metrics({"per_question": pq})
    assert metrics["n_zero_sample_questions"] == 0


# ---------------------------------------------------------------------------
# synthpanel CLI fallbacks: infra failures raise, never fabricate
# ---------------------------------------------------------------------------


class _FakeProc:
    def __init__(self, returncode: int, stdout: bytes = b"", stderr: bytes = b""):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    async def communicate(self):
        return self._stdout, self._stderr


def _cli_synthpanel_provider(monkeypatch):
    from synthbench.providers import synthpanel as sp_mod

    monkeypatch.setattr(sp_mod, "_HAS_SYNTH_PANEL_API", False)
    return sp_mod.SynthPanelProvider(model="haiku", synthpanel_path="/bin/echo")


def _patch_subprocess(monkeypatch, proc: _FakeProc):
    async def fake_exec(*cmd, **kwargs):
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)


@pytest.mark.asyncio
async def test_synthpanel_subprocess_failure_raises_not_uniform(monkeypatch):
    provider = _cli_synthpanel_provider(monkeypatch)
    _patch_subprocess(monkeypatch, _FakeProc(returncode=1, stderr=b"boom"))
    with pytest.raises(ProviderError):
        await provider.get_distribution("Q?", ["Yes", "No"], n_samples=3)


@pytest.mark.asyncio
async def test_synthpanel_bad_json_raises_not_uniform(monkeypatch):
    provider = _cli_synthpanel_provider(monkeypatch)
    _patch_subprocess(monkeypatch, _FakeProc(returncode=0, stdout=b"not json"))
    with pytest.raises(ProviderError):
        await provider.get_distribution("Q?", ["Yes", "No"], n_samples=3)


@pytest.mark.asyncio
async def test_synthpanel_batch_classifies_responses(monkeypatch):
    import json as _json

    provider = _cli_synthpanel_provider(monkeypatch)
    payload = {
        "rounds": [
            {
                "results": [
                    {"responses": [{"response": "Better"}]},
                    {"responses": [{"response": "I cannot answer that as an AI"}]},
                    {"responses": [{"response": "wibble wobble"}]},
                ]
            }
        ]
    }
    _patch_subprocess(
        monkeypatch, _FakeProc(returncode=0, stdout=_json.dumps(payload).encode())
    )
    dist = await provider.get_distribution(
        "Q?", ["Better", "Worse", "About the same"], n_samples=3
    )
    # 1 valid + 1 refusal are samples; the garbled one is a parse failure.
    assert dist.n_samples == 2
    assert dist.n_parse_failures == 1
    assert dist.refusal_probability == pytest.approx(0.5)
    assert dist.probabilities[0] == pytest.approx(0.5)  # "Better", not "Worse"
    assert dist.probabilities[1] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_synthpanel_respond_failure_raises(monkeypatch):
    provider = _cli_synthpanel_provider(monkeypatch)
    _patch_subprocess(monkeypatch, _FakeProc(returncode=2, stderr=b"crashed"))
    with pytest.raises(ProviderError):
        await provider.respond("Q?", ["Yes", "No"])


# ---------------------------------------------------------------------------
# Adapter parser regression (same first-char bug class)
# ---------------------------------------------------------------------------


def test_adapter_parse_option_no_first_char_bug():
    from synthbench.submit_adapter import _parse_option

    opts = ["Better", "Worse", "About the same"]
    assert _parse_option("Better", opts) == "Better"
    assert _parse_option("B", opts) == "Worse"
    assert _parse_option("B. because reasons", opts) == "Worse"
    assert _parse_option("2", opts) == "Worse"
    assert _parse_option("2024 was a great year", opts) is None
    assert _parse_option("Disagree", ["Agree", "Disagree"]) == "Disagree"
