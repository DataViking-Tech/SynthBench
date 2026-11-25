"""Preserve OpenRouter billing evidence on Althing's native Messages transport.

This per-instance shim mirrors Althing 1.9.1's ``_send_anthropic`` request,
error handling, and parsing. It changes no prompt or decoding parameter and
does not replace the native message id. Remove it when the upstream adapter
retains response-header generation ids and its raw usage block itself.
"""

from __future__ import annotations

import json
from types import MethodType
from typing import Any, Callable

import httpx


def attach_openrouter_billing(
    client: Any,
    canonical_model: str,
    *,
    post: Callable[..., httpx.Response] | None = None,
) -> dict[str, str]:
    """Annotate responses from one resolved OpenRouter provider instance.

    ``canonical_model`` accepts ``anthropic/...`` or
    ``openrouter/anthropic/...``. Explicit routing prevents credential-based
    fallback to a direct Anthropic provider. The returned metadata contains
    no credentials, request headers, or request body. ``post`` is injectable
    for offline transport-equivalence tests.
    """
    from althing.llm.providers import openrouter as native

    upstream_model = canonical_model.removeprefix("openrouter/")
    if not upstream_model.startswith("anthropic/"):
        raise ValueError(
            "Billing instrumentation requires an explicit Anthropic OpenRouter model"
        )
    provider = client._resolve_provider("openrouter/" + upstream_model)
    if not isinstance(provider, native.OpenRouterProvider):
        raise TypeError("Resolved provider is not Althing's OpenRouter adapter")
    metadata = {
        "transport": "anthropic-messages-passthrough",
        "billing_instrumentation": "generation-header-and-native-usage-v1",
    }
    if getattr(provider, "_synthbench_openrouter_billing_attached", False):
        return metadata
    send_post = post if post is not None else httpx.post

    def send_anthropic(self, request):
        # Keep this wire path equivalent to the installed native method.
        url = f"{self._base_url}/v1/messages"
        body = native.build_anthropic_body(request)
        native._apply_provider_routing(body, request)
        try:
            resp = send_post(
                url,
                headers=self._headers(anthropic_passthrough=True),
                json=body,
                timeout=120.0,
            )
        except httpx.HTTPError as exc:
            raise native.LLMError(
                f"Transport error: {exc}",
                native.LLMErrorCategory.TRANSPORT,
                cause=exc,
            ) from exc
        if resp.status_code != 200:
            raise native._openrouter_error_from_response(resp)
        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise native.LLMError(
                "Failed to parse OpenRouter Anthropic-passthrough response",
                native.LLMErrorCategory.DESERIALIZATION,
                cause=exc,
            ) from exc
        response = native.parse_anthropic_response(data, request.model)

        generation_id = resp.headers.get("x-generation-id")
        if not generation_id:
            request_id = resp.headers.get("request-id") or resp.headers.get(
                "x-request-id"
            )
            if request_id and request_id.startswith("gen-"):
                generation_id = request_id
        response._openrouter_generation_id = generation_id
        usage = data.get("usage")
        response._openrouter_usage = usage if isinstance(usage, dict) else {}
        return response

    provider._send_anthropic = MethodType(send_anthropic, provider)
    provider._synthbench_openrouter_billing_attached = True
    return metadata
