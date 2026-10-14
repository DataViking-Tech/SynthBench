"""OpenRouter provider — access many models through a single gateway.

Requires OPENROUTER_API_KEY environment variable.
Uses the openai SDK against the OpenRouter-compatible endpoint.
"""

from __future__ import annotations

import asyncio
import os

from synthbench.providers._parsing import parse_option_response
from synthbench.providers._retry import call_with_retries
from synthbench.providers.base import (
    RAW_ANSWER_MAX_TOKENS,
    PersonaSpec,
    Provider,
    Response,
    build_persona_system_prompt,
    validate_effort,
)

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Request settings for models that reason before answering by default. Such a
# model spends the 8-token answer budget thinking and returns nothing or a
# cut-off answer. The first cut-off, unreadable answer in a run switches the
# run to reasoning off, or, where a model won't allow that, minimal reasoning
# with room for it (reasoning text excluded from the answer); that request is
# re-sent and every later one uses the mode. Some models (Sonnet 5.5) decide
# per question whether to think, so the first request alone can't tell.
_REASONING_MODES = {
    "off": {
        "max_tokens": RAW_ANSWER_MAX_TOKENS,
        "extra_body": {"reasoning": {"enabled": False}},
    },
    "minimal": {
        "max_tokens": 1024,
        "extra_body": {"reasoning": {"effort": "minimal", "exclude": True}},
    },
}

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
                "pip install 'synthbench-eval[openai] @ git+https://github.com/DataViking-Tech/SynthBench.git'"
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
        # None while the model answers within the default budget; "off" /
        # "minimal" once a cut-off answer forced a switch (see
        # _REASONING_MODES). Stamped into the run config.
        self.reasoning: str | None = None
        self._switch_lock = asyncio.Lock()
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
            "max_tokens": RAW_ANSWER_MAX_TOKENS,
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

        resp = await self._create(request_kwargs)
        if self._effort is None and self._cut_off(resp, options):
            resp = await self._switch_reasoning(request_kwargs)

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

    async def _create(self, request_kwargs: dict):
        if self.reasoning is not None:
            request_kwargs = {**request_kwargs, **_REASONING_MODES[self.reasoning]}
        return await call_with_retries(lambda: self._request(request_kwargs))

    async def _request(self, request_kwargs: dict):
        """One chat completion; an answer-less reply is raised as retryable.

        OpenRouter occasionally returns HTTP 200 with ``choices`` missing
        (an upstream provider error passed through), which would otherwise
        crash the run on ``resp.choices[0]``.
        """
        resp = await self._client.chat.completions.create(**request_kwargs)
        if not getattr(resp, "choices", None):
            raise ConnectionError(f"OpenRouter returned no choices for {self._model}")
        return resp

    @staticmethod
    def _cut_off(resp, options: list[str]) -> bool:
        """True when reasoning used up the budget before an option was named.

        A long visible answer that runs out of tokens (prose a model writes
        despite the instruction) is not a reasoning problem and keeps the
        run's mode; only an empty answer or one that spent tokens reasoning
        counts.
        """
        choice = resp.choices[0]
        content = choice.message.content or ""
        details = getattr(
            getattr(resp, "usage", None), "completion_tokens_details", None
        )
        reasoned = bool(getattr(details, "reasoning_tokens", 0) or 0)
        return (
            choice.finish_reason == "length"
            and (reasoned or not content.strip())
            and parse_option_response(content, options).is_parse_failure
        )

    async def _switch_reasoning(self, request_kwargs: dict):
        """Re-send a cut-off request with reasoning controlled; set the run's mode."""
        import openai

        async with self._switch_lock:
            if self.reasoning is not None:
                return await self._create(request_kwargs)
            return await self._pick_mode(request_kwargs, openai)

    async def _pick_mode(self, request_kwargs: dict, openai):
        for mode in ("off", "minimal"):
            try:
                resp = await call_with_retries(
                    lambda: self._request({**request_kwargs, **_REASONING_MODES[mode]})
                )
            except openai.BadRequestError as exc:
                if mode == "off" and "mandatory" in str(exc).lower():
                    continue
                raise
            self.reasoning = mode
            return resp
        raise AssertionError("unreachable")

    async def close(self) -> None:
        await self._client.close()
