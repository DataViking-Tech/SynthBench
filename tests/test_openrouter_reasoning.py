"""OpenRouter raw provider: models that reason before answering by default."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

openai = pytest.importorskip("openai")

from synthbench.providers.openrouter import OpenRouterProvider  # noqa: E402

OPTIONS = ["favor", "oppose", "don't know"]


def _resp(text: str, finish: str = "stop"):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=text), finish_reason=finish)
        ],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=1),
    )


class _FakeCompletions:
    """Answers per reasoning setting; records every request."""

    def __init__(self, default, off=None, minimal=None):
        self.answers = {"default": default, "off": off, "minimal": minimal}
        self.calls: list[str] = []

    async def create(self, **kw):
        reasoning = (kw.get("extra_body") or {}).get("reasoning")
        mode = (
            "default"
            if reasoning is None
            else "off"
            if reasoning.get("enabled") is False
            else "minimal"
        )
        self.calls.append(mode)
        answer = self.answers[mode]
        if answer == "mandatory":
            raise openai.BadRequestError(
                "Reasoning is mandatory for this endpoint",
                response=SimpleNamespace(
                    request=None, status_code=400, headers={}, json=lambda: {}
                ),
                body=None,
            )
        return answer


def _provider(monkeypatch, completions):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    p = OpenRouterProvider(model="test/model")
    p._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return p


def _ask(p, n=1):
    async def run():
        return await asyncio.gather(
            *(p.respond("Death penalty?", OPTIONS) for _ in range(n))
        )

    return asyncio.run(run())


def test_model_answering_by_default_is_left_alone(monkeypatch):
    fake = _FakeCompletions(default=_resp("A"))
    p = _provider(monkeypatch, fake)
    out = _ask(p, n=4)
    assert [r.selected_option for r in out] == ["favor"] * 4
    assert p.reasoning is None
    assert fake.calls == ["default"] * 4


def test_reasoning_turned_off_when_the_default_answer_is_empty(monkeypatch):
    fake = _FakeCompletions(default=_resp("", "length"), off=_resp("B"))
    p = _provider(monkeypatch, fake)
    out = _ask(p, n=5)
    assert all(r.selected_option == "oppose" for r in out)
    assert p.reasoning == "off"
    # One probe at default settings; every answer is from reasoning off.
    assert fake.calls.count("default") == 1
    assert fake.calls.count("off") == 5


def test_minimal_reasoning_when_it_cannot_be_turned_off(monkeypatch):
    fake = _FakeCompletions(
        default=_resp("(", "length"), off="mandatory", minimal=_resp("(C)")
    )
    p = _provider(monkeypatch, fake)
    out = _ask(p, n=3)
    assert all(r.selected_option == "don't know" for r in out)
    assert p.reasoning == "minimal"
    assert fake.calls.count("minimal") == 3


def test_truncated_but_parseable_answer_needs_no_switch(monkeypatch):
    fake = _FakeCompletions(default=_resp("C", "length"))
    p = _provider(monkeypatch, fake)
    assert _ask(p)[0].selected_option == "don't know"
    assert p.reasoning is None


def test_explicit_effort_skips_the_probe(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    p = OpenRouterProvider(model="test/model", effort="low")
    assert p._probed is True
