"""Native wire-equivalence and billing-header retention, without API calls."""

from copy import deepcopy

import httpx
import pytest

from synthbench.campaign_transport import attach_openrouter_billing

native = pytest.importorskip("althing.llm.providers.openrouter")
models = pytest.importorskip("althing.llm.models")


class Client:
    def __init__(self, provider):
        self.provider = provider
        self.resolved = []

    def _resolve_provider(self, model):
        self.resolved.append(model)
        return self.provider


def provider():
    result = native.OpenRouterProvider.__new__(native.OpenRouterProvider)
    result._api_key = "test-key-not-a-secret"
    result._base_url = "https://openrouter.ai/api"
    return result


def request(*, cache=True):
    return models.CompletionRequest(
        model="anthropic/claude-haiku-5.5",
        max_tokens=1024,
        messages=[
            models.InputMessage(
                role="user", content=[models.TextBlock(text="Choose A or B.")]
            )
        ],
        system="Answer as the selected survey respondent.",
        tools=[
            models.ToolDefinition(
                name="answer",
                input_schema={
                    "type": "object",
                    "properties": {"option": {"enum": ["A", "B"]}},
                    "required": ["option"],
                },
            )
        ],
        tool_choice=models.ToolChoice(kind="tool", name="answer"),
        provider_routing={"order": ["Anthropic"], "allow_fallbacks": False},
        cache_enabled=cache,
    )


def payload():
    return {
        "id": "msg_native_id",
        "model": "claude-haiku-5.5",
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "tool_native",
                "name": "answer",
                "input": {"option": "A"},
            }
        ],
        "stop_reason": "tool_use",
        "usage": {
            "input_tokens": 120,
            "output_tokens": 20,
            "cost": 0,
            "cost_details": {"upstream_inference_cost": 0.000022},
            "is_byok": True,
        },
    }


def response(*, headers=None, status=200, body=None):
    return httpx.Response(
        status,
        headers=headers,
        json=payload() if body is None else body,
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/messages"),
    )


@pytest.mark.parametrize("cache", [False, True])
def test_preserves_native_wire_and_message_id_while_retaining_billing(
    monkeypatch, cache
):
    original = provider()
    instrumented = provider()
    sent = []

    def post(url, **kwargs):
        sent.append((url, deepcopy(kwargs)))
        return response(headers={"x-generation-id": "gen-openrouter-id"})

    with monkeypatch.context() as context:
        context.setattr(native.httpx, "post", post)
        baseline = original._send_anthropic(request(cache=cache))
    client = Client(instrumented)
    metadata = attach_openrouter_billing(
        client, "anthropic/claude-haiku-5.5", post=post
    )
    actual = instrumented._send_anthropic(request(cache=cache))

    assert sent[0] == sent[1]
    assert sent[1][1]["timeout"] == 120.0
    assert "temperature" not in sent[1][1]["json"]
    assert sent[1][1]["json"]["provider"] == {
        "order": ["Anthropic"],
        "allow_fallbacks": False,
    }
    assert actual.id == baseline.id == "msg_native_id"
    assert actual.content == baseline.content
    assert actual.usage == baseline.usage
    assert actual._openrouter_generation_id == "gen-openrouter-id"
    assert actual._openrouter_usage == payload()["usage"]
    assert client.resolved == ["openrouter/anthropic/claude-haiku-5.5"]
    assert "test-key" not in str(metadata)
    assert not hasattr(original, "_synthbench_openrouter_billing_attached")


@pytest.mark.parametrize(
    "headers,expected",
    [
        ({"request-id": "gen-fallback"}, "gen-fallback"),
        ({"x-request-id": "gen-x-fallback"}, "gen-x-fallback"),
        ({"request-id": "request-unrelated"}, None),
        (
            {"x-generation-id": "gen-primary", "request-id": "gen-secondary"},
            "gen-primary",
        ),
        ({}, None),
    ],
)
def test_header_fallback_is_generation_specific(headers, expected):
    actual = provider()
    attach_openrouter_billing(
        Client(actual),
        "openrouter/anthropic/claude-haiku-5.5",
        post=lambda *args, **kwargs: response(headers=headers),
    )
    assert actual._send_anthropic(request())._openrouter_generation_id == expected


def test_keeps_native_error_classification():
    actual = provider()
    body = {
        "error": {
            "code": 429,
            "message": "Rate limited",
            "type": "rate_limit_error",
            "metadata": {"provider_name": "Anthropic"},
        }
    }
    error_response = response(status=429, body=body)
    expected = native._openrouter_error_from_response(error_response)
    attach_openrouter_billing(
        Client(actual),
        "anthropic/claude-haiku-5.5",
        post=lambda *args, **kwargs: error_response,
    )
    with pytest.raises(native.LLMError) as caught:
        actual._send_anthropic(request())
    assert caught.value.category == expected.category
    assert caught.value.status_code == expected.status_code
    assert caught.value.downstream_provider == expected.downstream_provider
    assert str(caught.value) == str(expected)


@pytest.mark.parametrize("failure", ["transport", "json"])
def test_transport_and_json_errors_match_native_categories(failure):
    actual = provider()

    def post(*args, **kwargs):
        if failure == "transport":
            raise httpx.ReadTimeout("test timeout")
        return httpx.Response(200, content=b"not json")

    attach_openrouter_billing(Client(actual), "anthropic/claude-haiku-5.5", post=post)
    with pytest.raises(native.LLMError) as caught:
        actual._send_anthropic(request())
    expected = (
        native.LLMErrorCategory.TRANSPORT
        if failure == "transport"
        else native.LLMErrorCategory.DESERIALIZATION
    )
    assert caught.value.category == expected


def test_attachment_is_idempotent_and_rejects_wrong_provider():
    actual = provider()
    client = Client(actual)
    first = attach_openrouter_billing(client, "anthropic/claude-haiku-5.5")
    method = actual._send_anthropic
    assert attach_openrouter_billing(client, "anthropic/claude-haiku-5.5") == first
    assert actual._send_anthropic is method
    with pytest.raises(ValueError, match="explicit Anthropic"):
        attach_openrouter_billing(client, "google/not-eligible")
    with pytest.raises(TypeError, match="not Althing's OpenRouter"):
        attach_openrouter_billing(Client(object()), "anthropic/claude-haiku-5.5")
