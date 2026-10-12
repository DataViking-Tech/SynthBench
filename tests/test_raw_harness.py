"""Raw providers through a subscription agent CLI (claude-code: / codex:)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from synthbench.leaderboard import display_provider_name, provider_framework
from synthbench.providers import _harness
from synthbench.providers._harness import split_harness

pytest.importorskip("althing.llm.client")


class _FakeClient:
    def __init__(self, text: str, served: str):
        self.text, self.served, self.requests = text, served, []

    def send(self, request):
        self.requests.append(request)
        return SimpleNamespace(
            text=self.text,
            model=self.served,
            usage=SimpleNamespace(input_tokens=5, output_tokens=1),
        )


@pytest.fixture
def fake_client(monkeypatch):
    holder = {}

    def make(text="B", served="claude-code:claude-haiku-5-5"):
        client = _FakeClient(text, served)
        monkeypatch.setattr(
            "althing.llm.client.LLMClient", lambda: client, raising=True
        )
        holder["client"] = client
        return client

    return make


def test_split_harness():
    assert split_harness("claude-code:haiku") == ("claude-code", "haiku")
    assert split_harness("codex:gpt-6-luna") == ("codex", "gpt-6-luna")
    assert split_harness("claude-haiku-4-5") == (None, "claude-haiku-4-5")


def test_raw_anthropic_through_claude_code(fake_client):
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    client = fake_client("B")
    p = RawAnthropicProvider(model="claude-code:haiku")
    assert p.harness == "claude-code"
    r = asyncio.run(p.respond("How happy are you?", ["Very", "Pretty", "Not too"]))
    assert r.selected_option == "Pretty"
    # The raw survey prompt, not a persona prompt.
    sent = client.requests[0]
    assert sent.system.startswith("You are answering a survey.")
    assert "Respond with ONLY the letter" in sent.messages[0].content[0].text
    # The alias is recorded as the model the CLI served.
    assert p.name == "raw-anthropic/claude-haiku-5-5 harness=claude-code"
    asyncio.run(p.close())


def test_raw_openai_through_codex(fake_client):
    from synthbench.providers.raw_openai import RawOpenAIProvider

    fake_client("A", served="codex:gpt-6-luna")
    p = RawOpenAIProvider(model="codex:gpt-6-luna")
    r = asyncio.run(p.respond("Favor or oppose?", ["Favor", "Oppose"]))
    assert r.selected_option == "Favor"
    assert p.name == "raw-openai/gpt-6-luna harness=codex"


def test_harness_vendor_must_match_provider(fake_client):
    from synthbench.providers.raw_openai import RawOpenAIProvider

    fake_client()
    with pytest.raises(ValueError, match="runs anthropic models"):
        RawOpenAIProvider(model="claude-code:haiku")


def test_effort_is_rejected_through_a_harness(fake_client):
    from synthbench.providers.raw_anthropic import RawAnthropicProvider

    fake_client()
    with pytest.raises(ValueError, match="--effort"):
        RawAnthropicProvider(model="claude-code:haiku", effort="low")


@pytest.mark.parametrize(
    ("provider", "name"),
    [
        ("raw-anthropic/claude-haiku-5-5 harness=claude-code", "Claude Haiku 5.5"),
        ("raw-anthropic/claude-sonnet-4-6 harness=claude-code", "Claude Sonnet 4.6"),
        ("raw-openai/gpt-6-luna harness=codex", "GPT-6 Luna"),
        (
            "raw-anthropic/claude-haiku-4-5-20251001 harness=claude-code",
            "Claude Haiku 4.5",
        ),
    ],
)
def test_raw_harness_runs_display_as_raw_vendor_models(provider, name):
    assert display_provider_name(provider) == name
    assert provider_framework(provider) == "raw"


def test_module_exports_harness_vendors():
    assert _harness.HARNESS_VENDORS == {"claude-code": "anthropic", "codex": "openai"}
