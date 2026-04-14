"""End-to-end integration: token usage lands in report JSON.

Uses a mocked provider so this test does not touch any LLM API.
"""

from __future__ import annotations

import pytest

from synthbench.providers.base import PersonaSpec, Provider, Response
from synthbench.report import to_json
from synthbench.runner import BenchmarkRunner


class UsageReportingProvider(Provider):
    """Provider that returns Response with metadata['usage'] each call."""

    def __init__(self, input_per_call: int = 10, output_per_call: int = 2):
        self._input = input_per_call
        self._output = output_per_call

    @property
    def name(self) -> str:
        return "mock/usage"

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        return Response(
            selected_option=options[0],
            metadata={
                "model": "mock-model",
                "usage": {
                    "input_tokens": self._input,
                    "output_tokens": self._output,
                },
            },
        )


class NoUsageProvider(Provider):
    """Provider that mirrors the ollama path — usage explicitly None."""

    @property
    def name(self) -> str:
        return "mock/no-usage"

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        return Response(
            selected_option=options[0],
            metadata={"model": "mock-model", "usage": None},
        )


@pytest.mark.asyncio
async def test_tokens_present_in_report_json(mock_dataset):
    provider = UsageReportingProvider(input_per_call=10, output_per_call=2)
    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=provider,
        samples_per_question=3,
    )
    result = await runner.run(n=2)

    payload = to_json(result)
    per_q = payload["per_question"]
    assert len(per_q) == 2

    # Per-question token_usage present and matches per-sample math.
    for q in per_q:
        assert q["token_usage"]["input_tokens"] == 30  # 3 samples * 10
        assert q["token_usage"]["output_tokens"] == 6
        assert q["token_usage"]["call_count"] == 3

    # Aggregate sums across questions.
    agg = payload["aggregate"]["token_usage"]
    assert agg["input_tokens"] == sum(q["token_usage"]["input_tokens"] for q in per_q)
    assert agg["output_tokens"] == sum(q["token_usage"]["output_tokens"] for q in per_q)
    assert agg["call_count"] == sum(q["token_usage"]["call_count"] for q in per_q)
    assert agg["source"] == "measured"


@pytest.mark.asyncio
async def test_no_usage_path_omits_token_usage(mock_dataset):
    provider = NoUsageProvider()
    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=provider,
        samples_per_question=3,
    )
    result = await runner.run(n=2)

    payload = to_json(result)
    for q in payload["per_question"]:
        assert "token_usage" not in q
    assert "token_usage" not in payload["aggregate"]


@pytest.mark.asyncio
async def test_partial_usage_marks_source_partial(mock_dataset, monkeypatch):
    """If only some questions have usage, aggregate.source == 'partial'."""

    questions = mock_dataset.load(n=2)
    no_usage_text = questions[0].text  # first question reports no usage

    class FlakyProvider(Provider):
        @property
        def name(self) -> str:
            return "mock/flaky"

        async def respond(self, question, options, *, persona=None):
            if question == no_usage_text:
                return Response(
                    selected_option=options[0],
                    metadata={"model": "mock", "usage": None},
                )
            return Response(
                selected_option=options[0],
                metadata={
                    "model": "mock",
                    "usage": {"input_tokens": 5, "output_tokens": 1},
                },
            )

    runner = BenchmarkRunner(
        dataset=mock_dataset,
        provider=FlakyProvider(),
        samples_per_question=3,
    )
    result = await runner.run(n=2)
    payload = to_json(result)

    per_q = payload["per_question"]
    assert "token_usage" not in per_q[0]
    assert per_q[1]["token_usage"]["input_tokens"] == 15
    agg = payload["aggregate"]["token_usage"]
    assert agg["source"] == "partial"
    assert agg["input_tokens"] == 15
