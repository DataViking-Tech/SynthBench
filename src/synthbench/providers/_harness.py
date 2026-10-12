"""Send raw-provider prompts through a subscription agent CLI.

``raw-anthropic`` and ``raw-openai`` call the vendor API with an API key.
Given a harness model (``claude-code:<model>`` / ``codex:<model>``) they
instead send the same plain survey prompt through althing's subscription CLI
providers, which run the signed-in ``claude`` / ``codex`` CLI with tools and
the CLI's own system prompt disabled. The run stays a raw run of the vendor's
model; the harness is recorded as a ``harness=`` knob, as for althing runs.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from synthbench.providers._retry import call_with_retries

#: Harness prefix -> vendor whose model the harness runs.
HARNESS_VENDORS = {"claude-code": "anthropic", "codex": "openai"}


def split_harness(model: str) -> tuple[str | None, str]:
    """Split ``claude-code:haiku`` into ``("claude-code", "haiku")``."""
    for harness in HARNESS_VENDORS:
        prefix = f"{harness}:"
        if model.startswith(prefix):
            return harness, model[len(prefix) :]
    return None, model


class HarnessChat:
    """One-turn completions through a subscription CLI, via althing's client."""

    def __init__(self, model: str, *, vendor: str, provider: str):
        harness, bare = split_harness(model)
        if harness is None:
            raise ValueError(f"{model!r} has no harness prefix")
        if HARNESS_VENDORS[harness] != vendor:
            raise ValueError(
                f"{provider}: the {harness} harness runs {HARNESS_VENDORS[harness]} "
                f"models, not {vendor} ones (got {model!r})"
            )
        try:
            from althing.llm.client import LLMClient
        except ImportError as exc:
            raise ImportError(
                f"{provider} with a {harness}: model needs althing>=1.8.0 "
                "(the subscription CLI providers)."
            ) from exc
        self.harness = harness
        self._model = model
        self._bare = bare
        self._served: str | None = None
        self._client = LLMClient()
        self._executor = ThreadPoolExecutor(max_workers=16)

    def provider_name(self, prefix: str) -> str:
        """``raw-anthropic/claude-haiku-5-5 harness=claude-code``.

        Uses the model the CLI reported serving once known, so an alias such
        as ``haiku`` is recorded as the model it resolved to.
        """
        return f"{prefix}/{self._served or self._bare} harness={self.harness}"

    async def complete(self, system: str, prompt: str) -> tuple[str, dict | None]:
        """Return ``(text, usage)`` for one system + user turn."""
        from althing.llm.models import CompletionRequest, InputMessage, TextBlock

        request = CompletionRequest(
            model=self._model,
            max_tokens=64,
            messages=[InputMessage(role="user", content=[TextBlock(text=prompt)])],
            system=system,
        )
        loop = asyncio.get_running_loop()
        response: Any = await call_with_retries(
            lambda: loop.run_in_executor(self._executor, self._client.send, request)
        )
        _, served = split_harness(str(getattr(response, "model", "") or ""))
        if served and served != self._bare and self._served is None:
            self._served = served
        usage = getattr(response, "usage", None)
        usage_dict = (
            {
                "input_tokens": getattr(usage, "input_tokens", 0) or 0,
                "output_tokens": getattr(usage, "output_tokens", 0) or 0,
            }
            if usage is not None
            else None
        )
        return response.text or "", usage_dict

    def close(self) -> None:
        self._executor.shutdown(wait=False)
