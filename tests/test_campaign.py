"""No-network checks for campaign billing and durable response collection."""

import asyncio
import hashlib
import json
import time
from decimal import Decimal
from types import SimpleNamespace

import pytest
import httpx

from synthbench.campaign import (
    CampaignStopped,
    Collector,
    Ledger,
    load_pricing,
    load_questions,
    load_tasks,
)


def task(index=0):
    return {
        "id": f"task-{index}",
        "dataset": "gss",
        "question_key": "q",
        "provider": "openrouter",
        "model": "anthropic/test",
        "sample_index": index,
    }


def test_concurrent_reservations_cannot_oversubscribe(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)

    async def reserve(i):
        try:
            return await asyncio.to_thread(ledger.reserve, task(i), Decimal("0.4"), {})
        except CampaignStopped:
            return None

    async def run():
        return await asyncio.gather(*(reserve(i) for i in range(10)))

    try:
        reservations = asyncio.run(run())
        assert sum(x is not None for x in reservations) == 2
        assert ledger.accounted == Decimal("0.8")
    finally:
        ledger.close()


def test_resume_keeps_unsettled_and_failed_reservations(tmp_path):
    path = tmp_path / "journal.jsonl"
    ledger = Ledger(path, 1, time.time() + 60)
    abandoned = ledger.reserve(task(), Decimal("0.4"), {})
    failed = ledger.reserve(task(1), Decimal("0.4"), {})
    ledger.settle(failed, Decimal("0.4"), cost_source="reservation-retained")
    ledger.final(task(1), status="error")
    ledger.close()
    ledger = Ledger(path, 1, time.time() + 60)
    try:
        assert ledger.charges[abandoned] == Decimal("0.4")
        assert ledger.accounted == Decimal("0.8")
        assert ledger.completed["task-1"]["status"] == "error"
        with pytest.raises(CampaignStopped):
            ledger.reserve(task(2), Decimal("0.3"), {})
    finally:
        ledger.close()


def test_cost_settlement_releases_only_unused_reserve(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    try:
        attempt = ledger.reserve(task(), Decimal("0.8"), {})
        ledger.settle(attempt, Decimal("0.2"), cost_source="provider-reported")
        ledger.reserve(task(1), Decimal("0.8"), {})
        assert ledger.accounted == Decimal(1)
    finally:
        ledger.close()


def test_deadline_and_single_writer_fail_closed(tmp_path):
    path = tmp_path / "journal.jsonl"
    ledger = Ledger(path, 1, time.time() - 1)
    try:
        with pytest.raises(CampaignStopped, match="deadline"):
            ledger.reserve(task(), Decimal("0.1"), {})
        with pytest.raises(BlockingIOError):
            Ledger(path, 1, time.time() + 60)
        assert path.read_text() == ""
    finally:
        ledger.close()


def test_torn_record_is_not_silently_discarded(tmp_path):
    path = tmp_path / "journal.jsonl"
    path.write_text('{"kind":"reservation"')
    with pytest.raises(json.JSONDecodeError):
        Ledger(path, 1, time.time() + 60)


def test_task_validation_and_question_answer_key_exclusion(tmp_path):
    tasks_path = tmp_path / "tasks.jsonl"
    tasks_path.write_text(json.dumps(task()) + "\n")
    tasks = load_tasks(tasks_path)
    (tmp_path / "gss-questions-private.json").write_text(
        json.dumps(
            [
                {
                    "key": "q",
                    "text": "Question?",
                    "options": ["Yes", "No"],
                    "human_distribution": {"Yes": 0.5, "No": 0.5},
                }
            ]
        )
    )
    questions = load_questions(tasks, tmp_path)
    assert "human_distribution" not in questions["gss", "q"]
    tasks_path.write_text((json.dumps(task()) + "\n") * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        load_tasks(tasks_path)


def test_catalog_ignores_unrelated_prices_but_rejects_invalid_claude_rate(tmp_path):
    path = tmp_path / "pricing.json"
    catalog = {
        "data": [
            {"id": "unrelated/credit", "pricing": {"prompt": "-1", "completion": "-1"}},
            {
                "id": "anthropic/test",
                "pricing": {"prompt": "0.000002", "completion": "0.00001"},
            },
        ]
    }
    path.write_text(json.dumps(catalog))
    assert load_pricing(path) == {"anthropic/test": (Decimal(2), Decimal(10))}
    catalog["data"][1]["pricing"]["prompt"] = "-1"
    path.write_text(json.dumps(catalog))
    with pytest.raises(ValueError, match="finite and nonnegative"):
        load_pricing(path)


@pytest.mark.asyncio
async def test_completed_task_not_dispatched_and_inputs_cannot_change(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    collector = Collector(ledger, {}, {("gss", "q"): {}}, 2)
    ledger.final(
        {**task(), "_question_hash": hashlib.sha256(b"{}").hexdigest()},
        status="completed",
    )
    try:
        await collector._one(task())
        assert not collector.providers
        with pytest.raises(ValueError, match="different inputs"):
            await collector._one({**task(), "replicate": 9})
        collector.questions["gss", "q"] = {"text": "Changed snapshot"}
        with pytest.raises(ValueError, match="different inputs"):
            await collector._one(task())
    finally:
        await collector.cost_client.aclose()
        ledger.close()


@pytest.mark.asyncio
async def test_raw_attempts_are_individually_billed_and_response_retained(
    tmp_path, monkeypatch
):
    import synthbench.providers.openrouter as raw_module
    from synthbench.providers.base import Response

    class FakeRaw:
        def __init__(self, **kwargs):
            self._client = SimpleNamespace()
            self.reasoning = None

        async def _request(self, kwargs):
            return SimpleNamespace(
                id="gen-test",
                usage=SimpleNamespace(model_dump=lambda: {"cost": 0.1}),
                model_dump=lambda: {"id": "gen-test", "raw": "A"},
            )

        async def respond(self, question, options):
            await self._request({"max_tokens": 64, "messages": [{"content": question}]})
            await self._request({"max_tokens": 64, "messages": [{"content": question}]})
            return Response("Yes", "A")

        async def close(self):
            pass

    monkeypatch.setattr(raw_module, "OpenRouterProvider", FakeRaw)
    ledger = Ledger(tmp_path / "journal.jsonl", 2, time.time() + 60)
    collector = Collector(
        ledger,
        {"anthropic/test": (Decimal(100), Decimal(100))},
        {("gss", "q"): {"text": "Question?", "options": ["Yes", "No"]}},
    )
    try:
        summary = await collector.run([task()])
        assert summary["completed"] == 1
        assert ledger.accounted == Decimal("0.2")
        rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
        assert [row["kind"] for row in rows] == [
            "campaign",
            "reservation",
            "received",
            "attempt",
            "reservation",
            "received",
            "attempt",
            "final",
        ]
        assert rows[-1]["response"]["raw_text"] == "A"
        assert rows[-1]["response"]["metadata"]["generation_id"] == "gen-test"
        assert rows[-1]["response"]["metadata"]["attempt_id"]
        assert rows[-1]["settings"]["reasoning_request"] is None
    finally:
        ledger.close()


@pytest.mark.asyncio
async def test_transport_failure_retains_reservation(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    collector = Collector(
        ledger, {}, {("gss", "q"): {"text": "Q", "options": ["A", "B"]}}
    )

    async def fail(task_arg, question):
        ledger.reserve(task_arg, Decimal("0.25"), {})
        raise ConnectionError("Do not persist arbitrary exception strings")

    collector._one_althing = fail
    current = {**task(), "provider": "althing"}
    try:
        summary = await collector.run([current])
        assert summary["errors"] == 1
        assert ledger.accounted == Decimal("0.25")
        assert "Do not persist" not in ledger.path.read_text()
    finally:
        ledger.close()


@pytest.mark.asyncio
async def test_byok_zero_gateway_cost_accounts_upstream_credits(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    collector = Collector(ledger, {"anthropic/test": (Decimal(2), Decimal(10))}, {})
    try:
        cost, source = await collector._cost(
            "anthropic/test",
            None,
            {
                "cost": 0,
                "is_byok": True,
                "cost_details": {"upstream_inference_cost": 0.0123},
                "prompt_tokens": 100,
                "completion_tokens": 10,
            },
        )
        assert cost == Decimal("0.0123")
        assert "upstream" in source
        cost, source = await collector._cost(
            "anthropic/test",
            None,
            {
                "cost": 0,
                "prompt_tokens": 100,
                "completion_tokens": 10,
            },
        )
        assert cost == Decimal("0.0003")
        assert source == "catalog-token-estimate"
        cost, _ = await collector._cost(
            "anthropic/test",
            None,
            {
                "cost": 0.02,
                "cost_details": {"upstream_inference_cost": 0.01},
            },
        )
        assert cost == Decimal("0.02")
    finally:
        await collector.cost_client.aclose()
        ledger.close()


def test_underestimated_reservation_stops_even_before_total_budget(tmp_path):
    ledger = Ledger(tmp_path / "journal.jsonl", 100, time.time() + 60)
    try:
        attempt = ledger.reserve(task(), Decimal("0.001"), {})
        with pytest.raises(CampaignStopped, match="exceeded reservation"):
            ledger.settle(attempt, Decimal("0.002"))
        assert ledger.accounted == Decimal("0.002")
    finally:
        ledger.close()


def test_campaign_provenance_rejects_pricing_edits_on_resume(tmp_path):
    path = tmp_path / "journal.jsonl"
    ledger = Ledger(path, 100, time.time() + 60)
    ledger.bind_campaign({"pricing": {"anthropic/test": ["2", "10"]}})
    ledger.close()
    ledger = Ledger(path, 100, time.time() + 60)
    try:
        ledger.bind_campaign({"pricing": {"anthropic/test": ["2", "10"]}})
        with pytest.raises(ValueError, match="pricing or runtime changed"):
            ledger.bind_campaign({"pricing": {"anthropic/test": ["4", "20"]}})
    finally:
        ledger.close()


def test_overrun_halt_survives_resume_with_larger_cap(tmp_path):
    path = tmp_path / "journal.jsonl"
    ledger = Ledger(path, 1, time.time() + 60)
    attempt = ledger.reserve(task(), Decimal("0.01"), {})
    with pytest.raises(CampaignStopped):
        ledger.settle(attempt, Decimal("0.02"))
    ledger.close()
    resumed = Ledger(path, 10, time.time() + 60)
    try:
        with pytest.raises(CampaignStopped, match="journal halted"):
            resumed.reserve(task(1), Decimal("0.01"), {})
    finally:
        resumed.close()


@pytest.mark.asyncio
async def test_received_answer_survives_billing_failure(tmp_path, monkeypatch):
    import synthbench.providers.openrouter as raw_module

    class FakeRaw:
        def __init__(self, **kwargs):
            self._client = SimpleNamespace()

        async def _request(self, kwargs):
            return SimpleNamespace(
                id="gen-recoverable",
                usage=SimpleNamespace(model_dump=lambda: {"cost": "invalid"}),
                model_dump=lambda: {"id": "gen-recoverable", "answer": "A"},
            )

        async def respond(self, question, options):
            await self._request({"max_tokens": 64, "messages": []})

    monkeypatch.setattr(raw_module, "OpenRouterProvider", FakeRaw)
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    collector = Collector(
        ledger,
        {"anthropic/test": (Decimal(2), Decimal(10))},
        {("gss", "q"): {"text": "Q", "options": ["Yes", "No"]}},
    )
    try:
        result = await collector.run([task()])
        assert result["errors"] == 1
        rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
        received = next(row for row in rows if row["kind"] == "received")
        assert received["generation_id"] == "gen-recoverable"
        assert received["response"]["answer"] == "A"
        assert ledger.accounted > 0
    finally:
        ledger.close()


@pytest.mark.asyncio
async def test_generation_lookup_uses_upstream_cost_when_gateway_is_zero(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-not-a-secret")
    ledger = Ledger(tmp_path / "journal.jsonl", 1, time.time() + 60)
    collector = Collector(ledger, {"anthropic/test": (Decimal(2), Decimal(10))}, {})
    await collector.cost_client.aclose()

    calls = []

    def respond(request):
        assert request.url.params["id"] == "gen-example"
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(404, json={"error": "not indexed yet"})
        return httpx.Response(
            200,
            json={
                "data": {
                    "total_cost": 0,
                    "is_byok": True,
                    "upstream_inference_cost": 0.0000068,
                }
            },
        )

    collector.cost_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    try:
        cost, source = await collector._cost(
            "anthropic/test", "gen-example", {"cost": 0}
        )
        assert cost == Decimal("0.0000068")
        assert source == "generation-api-max-gateway-upstream"
        assert len(calls) == 2
    finally:
        await collector.cost_client.aclose()
        ledger.close()
