"""Private, resumable response collection with an append-only spending ledger.

This is an experiment runner, not a leaderboard submission format. Keep its
question snapshots and journals private: they may contain licensed survey text.
Errors and interrupted requests retain their entire reservation, since a lost
response does not prove that the upstream request was free. Resume never retries
a task with a final record; intentional retries must use a new task id.
"""

from __future__ import annotations

import argparse
import asyncio
import contextvars
import dataclasses
import datetime as dt
import fcntl
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
import os
import threading
import time
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx


class CampaignStopped(RuntimeError):
    """The deadline or conservative spending limit prevents another request."""


def _usd(value: Any) -> Decimal:
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Costs must be finite and nonnegative")
    return result


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Ledger:
    """Single-writer durable reservations, safe across concurrent samples."""

    def __init__(self, path: Path, max_usd: float, deadline: float):
        self.path = path
        self.max_usd = _usd(max_usd)
        self.deadline = deadline
        self.lock = threading.RLock()
        self.charges: dict[str, Decimal] = {}
        self.completed: dict[str, dict] = {}
        self.task_hashes: dict[str, str] = {}
        self.metadata: dict | None = None
        self.halted = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open("a+", encoding="utf-8")
        os.chmod(path, 0o600)
        try:
            fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.file.seek(0)
            for line in self.file:
                row = json.loads(line)  # A torn record fails closed; do not discard it.
                if row["kind"] == "reservation":
                    self.charges[row["attempt_id"]] = _usd(row["reserved_usd"])
                elif row["kind"] == "attempt":
                    if row["attempt_id"] not in self.charges:
                        raise ValueError("Attempt has no durable reservation")
                    amount = _usd(row["accounted_usd"])
                    self.halted |= (
                        bool(row.get("halted"))
                        or amount > self.charges[row["attempt_id"]]
                    )
                    self.charges[row["attempt_id"]] = amount
                elif row["kind"] == "final":
                    self.completed[row["task_id"]] = row
                elif row["kind"] == "campaign":
                    if self.metadata is not None and self.metadata != row["metadata"]:
                        raise ValueError(
                            "Journal contains inconsistent campaign metadata"
                        )
                    self.metadata = row["metadata"]
                if row.get("task_hash"):
                    old = self.task_hashes.setdefault(row["task_id"], row["task_hash"])
                    if old != row["task_hash"]:
                        raise ValueError(
                            "Journal task id was reused with different inputs"
                        )
            self.file.seek(0, os.SEEK_END)
        except BaseException:
            self.file.close()
            raise

    @property
    def accounted(self) -> Decimal:
        return sum(self.charges.values(), Decimal(0))

    def append(self, row: dict) -> None:
        with self.lock:
            self.file.write(_json({"at": _now(), **row}) + "\n")
            self.file.flush()
            os.fsync(self.file.fileno())

    def reserve(self, task: dict, amount: Decimal, request: dict) -> str:
        with self.lock:
            if self.halted:
                raise CampaignStopped("journal halted; reconcile before new dispatch")
            if time.time() >= self.deadline:
                raise CampaignStopped("deadline")
            if self.accounted + amount > self.max_usd:
                raise CampaignStopped("budget")
            attempt_id = uuid.uuid4().hex
            fingerprint = hashlib.sha256(_json(task).encode()).hexdigest()
            self.append(
                {
                    "kind": "reservation",
                    "attempt_id": attempt_id,
                    "task_id": task["id"],
                    "task_hash": fingerprint,
                    "reserved_usd": str(amount),
                    "request": request,
                }
            )
            self.charges[attempt_id] = amount
            self.task_hashes[task["id"]] = fingerprint
            return attempt_id

    def settle(self, attempt_id: str, amount: Decimal, **details: Any) -> None:
        with self.lock:
            reserved = self.charges[attempt_id]
            halted = (
                amount > reserved or self.accounted - reserved + amount > self.max_usd
            )
            self.append(
                {
                    "kind": "attempt",
                    "attempt_id": attempt_id,
                    "accounted_usd": str(amount),
                    "halted": halted,
                    **details,
                }
            )
            self.charges[attempt_id] = amount
            self.halted |= halted
            if self.halted:
                raise CampaignStopped(
                    "reported cost exceeded reservation; stop and reconcile"
                )

    def final(self, task: dict, **details: Any) -> None:
        row = {
            "kind": "final",
            "task_id": task["id"],
            "task_hash": hashlib.sha256(_json(task).encode()).hexdigest(),
            "task": task,
            **details,
        }
        self.append(row)
        self.completed[task["id"]] = row
        self.task_hashes[task["id"]] = row["task_hash"]

    def close(self) -> None:
        self.file.close()

    def bind_campaign(self, metadata: dict) -> None:
        # Normalize Decimals exactly as persisted JSON before comparing.
        normalized = json.loads(_json(metadata))
        if self.metadata is not None and self.metadata != normalized:
            raise ValueError("Campaign pricing or runtime changed; use a new journal")
        if self.metadata is None:
            if self.charges or self.completed:
                raise ValueError(
                    "Existing journal lacks campaign provenance; use a new journal"
                )
            self.append({"kind": "campaign", "metadata": normalized})
            self.metadata = normalized


def load_tasks(path: Path) -> list[dict]:
    tasks = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ids = set()
    for task in tasks:
        for field in ("id", "dataset", "question_key", "model", "provider"):
            if not isinstance(task.get(field), str) or not task[field]:
                raise ValueError(f"Task needs a nonempty {field}")
        if task["id"] in ids:
            raise ValueError(f"Duplicate task id: {task['id']}")
        ids.add(task["id"])
        if task["provider"] not in ("openrouter", "althing"):
            raise ValueError("Only OpenRouter-backed providers are permitted")
        if not task["model"].startswith("anthropic/"):
            raise ValueError("Campaign is restricted to explicit anthropic/* model ids")
        if task.get("elicitation", "natural") not in ("natural", "structured"):
            raise ValueError("Unknown elicitation mode")
        if task["provider"] == "openrouter" and (
            task.get("persona_pack") or task.get("elicitation", "natural") != "natural"
        ):
            raise ValueError(
                "Raw provider does not support packs or structured capture"
            )
        for key, default in (
            ("replicate", 0),
            ("sample_index", 0),
            ("samples_per_question", 30),
        ):
            value = task.get(key, default)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid {key}")
        if task.get("sample_index", 0) >= task.get("samples_per_question", 30):
            raise ValueError("sample_index must be below samples_per_question")
    return tasks


def load_pricing(path: Path) -> dict[str, tuple[Decimal, Decimal]]:
    data = json.loads(path.read_text())
    if "data" in data and isinstance(data["data"], list):
        data = {
            row["id"]: {
                "input_per_million": _usd(row["pricing"]["prompt"]) * 1_000_000,
                "output_per_million": _usd(row["pricing"]["completion"]) * 1_000_000,
            }
            for row in data["data"]
            if row["id"].startswith("anthropic/")
        }
    return {
        model: (_usd(rates["input_per_million"]), _usd(rates["output_per_million"]))
        for model, rates in data.items()
    }


def load_questions(
    tasks: list[dict], directory: Path | None
) -> dict[tuple[str, str], dict]:
    from synthbench.datasets import DATASETS

    questions = {}
    for dataset in sorted({task["dataset"] for task in tasks}):
        if directory:
            rows = json.loads(
                (directory / f"{dataset}-questions-private.json").read_text()
            )
            if isinstance(rows, dict):
                rows = rows["questions"]
        else:
            rows = [dataclasses.asdict(q) for q in DATASETS[dataset]().load()]
        for q in rows:
            # Deliberately keep only request-side fields; never answer keys.
            questions[dataset, q["key"]] = {
                key: q.get(key)
                for key in ("key", "text", "options", "respondent_population")
            }
    for task in tasks:
        q = questions[task["dataset"], task["question_key"]]
        if not q["text"] or not q["options"]:
            raise ValueError("Question lacks text or options")
    return questions


class _SingleAttempt:
    def run(self, fn, **kwargs):
        return fn()


_task_context: contextvars.ContextVar[dict] = contextvars.ContextVar("campaign_task")


class Collector:
    def __init__(
        self, ledger: Ledger, pricing: dict, questions: dict, concurrency: int = 8
    ):
        if concurrency < 1:
            raise ValueError("concurrency must be positive")
        self.ledger = ledger
        self.pricing = pricing
        self.questions = questions
        self.concurrency = concurrency
        packages = {}
        for package in ("synthbench-eval", "althing", "openai"):
            try:
                packages[package] = version(package)
            except PackageNotFoundError:
                packages[package] = "unavailable"
        ledger.bind_campaign(
            {
                "pricing": pricing,
                "packages": packages,
                "max_usd": str(ledger.max_usd),
                "deadline": ledger.deadline,
                "collector_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest(),
            }
        )
        self.providers: dict[tuple, Any] = {}
        self.last_attempts: dict[str, dict] = {}
        self.cost_client = httpx.AsyncClient(timeout=10, follow_redirects=False)
        self.stopped: str | None = None

    def _reserve(self, task: dict, request: dict) -> tuple[str, Decimal]:
        input_rate, output_rate = self.pricing[task["model"]]
        # UTF8 bytes are a conservative text-token bound. Add 4096 tokens
        # for chat/tool framing, and 25% input premium for cache creation.
        # This is explicitly an estimate, not a provider token-count proof.
        input_bound = len(_json(request).encode("utf-8")) + 4096
        output_bound = int(request["max_tokens"])
        amount = (
            Decimal(input_bound) * input_rate * Decimal("1.25")
            + Decimal(output_bound) * output_rate
        ) / 1_000_000
        return self.ledger.reserve(task, amount, request), amount

    async def _cost(
        self, model: str, generation_id: str | None, usage: dict
    ) -> tuple[Decimal, str]:
        def reported(data: dict) -> Decimal:
            # BYOK Claude promotions can debit upstream credits while
            # OpenRouter's own cost is zero. Never interpret gateway $0 as
            # a free inference, nor add overlapping billing measures.
            costs = [
                _usd(data[key])
                for key in (
                    "cost",
                    "total_cost",
                    "provider_reported_cost",
                    "upstream_inference_cost",
                )
                if data.get(key) is not None
            ]
            details = data.get("cost_details")
            if (
                isinstance(details, dict)
                and details.get("upstream_inference_cost") is not None
            ):
                costs.append(_usd(details["upstream_inference_cost"]))
            return max(costs, default=Decimal(0))

        native = reported(usage)
        if native > 0:
            return native, "provider-reported-max-gateway-upstream"
        if generation_id:
            for delay in (0, 0.5, 1, 2):
                if delay:
                    await asyncio.sleep(delay)
                try:
                    response = await self.cost_client.get(
                        "https://openrouter.ai/api/v1/generation",
                        params={"id": generation_id},
                        headers={
                            "Authorization": "Bearer "
                            + os.environ["OPENROUTER_API_KEY"]
                        },
                    )
                    if response.status_code == 200:
                        billing = response.json().get("data", {})
                        cost = reported(billing)
                        if cost > 0:
                            # Preserve gateway/upstream evidence lost by the
                            # Althing typed usage parser, without response text.
                            for field in (
                                "total_cost",
                                "upstream_inference_cost",
                                "is_byok",
                            ):
                                if billing.get(field) is not None:
                                    usage[field] = billing[field]
                            return cost, "generation-api-max-gateway-upstream"
                    elif response.status_code != 404:
                        break
                except (httpx.HTTPError, ValueError, KeyError):
                    break
        input_rate, output_rate = self.pricing[model]
        inputs = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)))
        outputs = int(usage.get("output_tokens", usage.get("completion_tokens", 0)))
        details = usage.get("prompt_tokens_details") or {}
        writes = int(
            usage.get("cache_write_tokens", details.get("cache_write_tokens", 0))
        )
        reads = int(usage.get("cache_read_tokens", 0))
        if not usage or inputs + outputs + writes + reads == 0:
            raise ValueError("No usable billing evidence")
        cost = (
            Decimal(inputs + reads) * input_rate
            + Decimal(writes) * input_rate * Decimal("1.25")
            + Decimal(outputs) * output_rate
        ) / 1_000_000
        return cost, "catalog-token-estimate"

    def _raw_provider(self, task: dict):
        from synthbench.providers.openrouter import OpenRouterProvider

        key = ("openrouter", task["model"])
        if key not in self.providers:
            provider = OpenRouterProvider(model=task["model"], temperature=None)
            provider._client.max_retries = 0
            provider._client.timeout = httpx.Timeout(120)
            original = provider._request

            async def request(kwargs):
                active = _task_context.get()
                attempt_id, reserved = self._reserve(active, kwargs)
                started = time.monotonic()
                try:
                    response = await original(kwargs)
                    usage = response.usage.model_dump() if response.usage else {}
                    self.ledger.append(
                        {
                            "kind": "received",
                            "attempt_id": attempt_id,
                            "task_id": active["id"],
                            "generation_id": response.id,
                            "usage": usage,
                            "response": response.model_dump(),
                        }
                    )
                    self.last_attempts[active["id"]] = {
                        "attempt_id": attempt_id,
                        "generation_id": response.id,
                        "reasoning_request": kwargs.get("extra_body", {}).get(
                            "reasoning"
                        ),
                    }
                    cost, source = await self._cost(active["model"], response.id, usage)
                    self.ledger.settle(
                        attempt_id,
                        cost,
                        task_id=active["id"],
                        generation_id=response.id,
                        usage=usage,
                        response=response.model_dump(),
                        cost_source=source,
                        elapsed_seconds=time.monotonic() - started,
                    )
                    return response
                except BaseException as exc:
                    # Budget exceptions raised before dispatch are outside this
                    # try. All dispatched failures conservatively stay charged.
                    if (
                        attempt_id in self.ledger.charges
                        and self.ledger.charges[attempt_id] == reserved
                    ):
                        self.ledger.settle(
                            attempt_id,
                            reserved,
                            task_id=active["id"],
                            error=type(exc).__name__,
                            cost_source="reservation-retained",
                            elapsed_seconds=time.monotonic() - started,
                        )
                    raise

            provider._request = request
            self.providers[key] = provider
        return self.providers[key]

    def _althing_provider(self, task: dict):
        from synthbench.providers.althing import AlthingProvider

        key = (
            "althing",
            task["model"],
            task.get("elicitation", "natural"),
            task.get("persona_pack"),
        )
        if key not in self.providers:
            provider = AlthingProvider(
                model="openrouter/" + task["model"],
                elicitation=task.get("elicitation", "natural"),
                persona_pack=task.get("persona_pack"),
            )
            if not provider._use_api:
                raise ValueError("Campaign requires the direct Althing Python API")
            provider._client._retry_policy = _SingleAttempt()
            self.providers[key] = provider
        return self.providers[key]

    def _population_system(
        self, task: dict, question: dict, provider: Any
    ) -> str | None:
        if not task.get("persona_pack"):
            return None
        from althing.population import allocate_population
        from althing.prompts import persona_system_prompt

        population = question.get("respondent_population")
        if not population or len(population) != 1:
            raise ValueError(
                "Population task needs exactly one respondent-population attribute"
            )
        ((key, members),) = population.items()
        allocation = allocate_population(
            provider._pack_personas,
            key=key,
            members=members,
            n_samples=task.get("samples_per_question", 30),
            seed=f"{question['key']}:{task.get('replicate', 0)}",
        )
        personas = [persona for persona, count in allocation for _ in range(count)]
        return persona_system_prompt(personas[task.get("sample_index", 0)])

    async def _one_althing(self, task: dict, question: dict):
        from synthbench.providers.base import Response

        provider = self._althing_provider(task)
        system = self._population_system(task, question, provider)
        request = provider._build_api_request(
            question["text"], question["options"], None, system=system
        )
        request_dict = dataclasses.asdict(request)
        attempt_id, reserved = self._reserve(task, request_dict)
        started = time.monotonic()
        try:
            response = await asyncio.to_thread(provider._client.send, request)
            usage = dataclasses.asdict(response.usage)
            self.ledger.append(
                {
                    "kind": "received",
                    "attempt_id": attempt_id,
                    "task_id": task["id"],
                    "generation_id": response.id,
                    "usage": usage,
                    "response": dataclasses.asdict(response),
                }
            )
            cost, source = await self._cost(task["model"], response.id, usage)
            self.ledger.settle(
                attempt_id,
                cost,
                task_id=task["id"],
                generation_id=response.id,
                usage=usage,
                response=dataclasses.asdict(response),
                cost_source=source,
                elapsed_seconds=time.monotonic() - started,
            )
            raw, parsed = provider._parse_api_response(response, question["options"])
            return Response(
                selected_option=parsed.option,
                raw_text=raw,
                refusal=parsed.refusal,
                metadata={
                    "model": response.model,
                    "usage": usage,
                    "generation_id": response.id,
                    "transport": "anthropic-messages-passthrough",
                },
            )
        except BaseException as exc:
            if self.ledger.charges.get(attempt_id) == reserved:
                self.ledger.settle(
                    attempt_id,
                    reserved,
                    task_id=task["id"],
                    error=type(exc).__name__,
                    cost_source="reservation-retained",
                    elapsed_seconds=time.monotonic() - started,
                )
            raise

    async def _one(self, task: dict) -> None:
        question = self.questions[task["dataset"], task["question_key"]]
        task = {
            **task,
            "_question_hash": hashlib.sha256(_json(question).encode()).hexdigest(),
        }
        fingerprint = hashlib.sha256(_json(task).encode()).hexdigest()
        if (
            task["id"] in self.ledger.task_hashes
            and self.ledger.task_hashes[task["id"]] != fingerprint
        ):
            raise ValueError("Task id reused with different inputs")
        if task["id"] in self.ledger.completed:
            return
        if self.stopped:
            return
        context = _task_context.set(task)
        started = time.monotonic()
        try:
            if task["provider"] == "openrouter":
                provider = self._raw_provider(task)
                response = await provider.respond(question["text"], question["options"])
                evidence = self.last_attempts.pop(task["id"], {})
                response.metadata = {**(response.metadata or {}), **evidence}
                settings = {
                    "reasoning_request": evidence.get("reasoning_request"),
                    "transport": "openai-chat-completions",
                }
            else:
                response = await self._one_althing(task, question)
                settings = {
                    "transport": "anthropic-messages-passthrough",
                    "internal_retries": 0,
                }
            self.ledger.final(
                task,
                status="completed",
                response=dataclasses.asdict(response),
                settings=settings,
                elapsed_seconds=time.monotonic() - started,
            )
        except CampaignStopped as exc:
            self.stopped = str(exc)
        except Exception as exc:  # noqa: BLE001 — persist task failure without secret-bearing exception text
            self.ledger.final(
                task,
                status="error",
                error=type(exc).__name__,
                elapsed_seconds=time.monotonic() - started,
            )
        finally:
            _task_context.reset(context)

    async def run(self, tasks: list[dict]) -> dict:
        iterator = iter(tasks)

        async def worker():
            for task in iterator:
                if self.stopped:
                    break
                await self._one(task)

        try:
            await asyncio.gather(*(worker() for _ in range(self.concurrency)))
        finally:
            for provider in self.providers.values():
                if hasattr(provider, "close"):
                    result = provider.close()
                    if asyncio.iscoroutine(result):
                        await result
                executor = getattr(provider, "_executor", None)
                if executor:
                    executor.shutdown(wait=True)
            await self.cost_client.aclose()
        requested_ids = {task["id"] for task in tasks}
        finals = [
            row for key, row in self.ledger.completed.items() if key in requested_ids
        ]
        return {
            "requested": len(tasks),
            "completed": sum(r["status"] == "completed" for r in finals),
            "errors": sum(r["status"] == "error" for r in finals),
            "accounted_usd": str(self.ledger.accounted),
            "max_usd": str(self.ledger.max_usd),
            "stopped": self.stopped,
            "at": _now(),
            "billing_note": "Includes conservative retained reservations; reconcile against provider billing.",
        }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--questions-dir", type=Path)
    parser.add_argument("--pricing", required=True, type=Path)
    parser.add_argument("--max-usd", required=True, type=float)
    parser.add_argument(
        "--deadline", required=True, help="Timezone-aware ISO timestamp"
    )
    parser.add_argument("--concurrency", default=8, type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    deadline = dt.datetime.fromisoformat(args.deadline.replace("Z", "+00:00"))
    if deadline.tzinfo is None or not math.isfinite(args.max_usd) or args.max_usd < 0:
        parser.error("Deadline needs timezone; budget must be finite and nonnegative")
    tasks = load_tasks(args.tasks)
    pricing = load_pricing(args.pricing)
    if any(task["model"] not in pricing for task in tasks):
        parser.error("Missing model pricing")
    questions = load_questions(tasks, args.questions_dir)
    if args.dry_run:
        print(
            _json({"tasks": len(tasks), "questions": len(questions), "paid_calls": 0})
        )
        return 0
    ledger = Ledger(args.journal, args.max_usd, deadline.timestamp())
    try:
        summary = asyncio.run(
            Collector(ledger, pricing, questions, args.concurrency).run(tasks)
        )
        summary_path = args.journal.with_suffix(".summary.json")
        summary_path.write_text(_json(summary) + "\n")
        os.chmod(summary_path, 0o600)
        print(_json(summary))
        return 0 if summary["completed"] == len(tasks) else 2
    finally:
        ledger.close()


if __name__ == "__main__":
    raise SystemExit(main())
