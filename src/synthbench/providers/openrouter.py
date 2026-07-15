"""OpenRouter provider — access many models through a single gateway.

Requires OPENROUTER_API_KEY environment variable.
Uses the openai SDK against the OpenRouter-compatible endpoint.
"""

from __future__ import annotations

import os

from synthbench.providers._parsing import parse_option_response
from synthbench.providers._retry import call_with_retries
from synthbench.providers.base import (
    PersonaSpec,
    Provider,
    Response,
    build_persona_system_prompt,
    validate_effort,
)

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_SYSTEM = (
    "You are answering a survey. Select the single option that best reflects your view."
)

_PROMPT_TEMPLATE = """\
Question: {question}

Options:
{options_block}

Respond with ONLY the letter of your choice (e.g., "A"). Do not explain."""

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# max_tokens ceilings used when a reasoning-effort level is requested.
#
# OpenRouter's unified `reasoning: {"effort": ...}` parameter forwards the
# effort level verbatim to models with a native effort knob (OpenAI o-series /
# gpt-5-class) and, for Anthropic-style budget models, converts it to
# `budget_tokens = max(min(max_tokens * ratio, 128000), 1024)` where the
# ratio is low=0.2 / medium=0.5 / high=0.8. These ceilings are chosen so the
# derived budgets land exactly on SynthBench's raw-anthropic tiers
# (low=2048, medium=8192, high=24576), keeping "high" comparable whether a
# Claude model is reached directly or through the gateway.
_EFFORT_MAX_TOKENS = {"low": 10240, "medium": 16384, "high": 30720}


def _build_prompt(question: str, options: list[str]) -> str:
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _PROMPT_TEMPLATE.format(question=question, options_block=options_block)


class OpenRouterProvider(Provider):
    """Call models via OpenRouter with no persona framing."""

    def __init__(
        self,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 1.0,
        effort: str | None = None,
    ):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: "
                "pip install 'synthbench[openai]'"
            )

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Get one at https://openrouter.ai/keys"
            )

        self._model = model
        self._temperature = temperature
        self._effort = validate_effort(effort, "openrouter")
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=_OPENROUTER_BASE_URL,
        )

    @property
    def name(self) -> str:
        return f"openrouter/{self._model}"

    @property
    def prompt_template_source(self) -> str:
        return _SYSTEM + "\n" + _PROMPT_TEMPLATE

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        prompt = _build_prompt(question, options)
        system = build_persona_system_prompt(_SYSTEM, persona)

        request_kwargs: dict = {
            "model": self._model,
            "max_tokens": 8,
            "temperature": self._temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        if self._effort is not None:
            # OpenRouter's unified reasoning parameter (sent via extra_body so
            # it reaches the request JSON regardless of openai SDK version).
            # Reasoning tokens count against max_tokens, so the 8-token answer
            # ceiling is replaced by the per-tier ceiling documented above.
            request_kwargs["max_tokens"] = _EFFORT_MAX_TOKENS[self._effort]
            request_kwargs["extra_body"] = {"reasoning": {"effort": self._effort}}

        resp = await call_with_retries(
            lambda: self._client.chat.completions.create(**request_kwargs)
        )

        raw_text = resp.choices[0].message.content or ""
        parsed = parse_option_response(raw_text, options)

        usage = None
        if getattr(resp, "usage", None) is not None:
            usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            }

        return Response(
            selected_option=parsed.option,
            raw_text=raw_text,
            refusal=parsed.refusal,
            metadata={
                "model": self._model,
                "finish_reason": resp.choices[0].finish_reason,
                "usage": usage,
            },
        )

    async def close(self) -> None:
        await self._client.close()
