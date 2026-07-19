"""Raw OpenAI GPT provider — no persona conditioning."""

from __future__ import annotations

from synthbench.providers._parsing import parse_option_response
from synthbench.providers._retry import call_with_retries
from synthbench.providers.base import (
    PersonaSpec,
    Provider,
    Response,
    build_persona_system_prompt,
    validate_effort,
)

# Completion-token ceilings applied when a reasoning-effort level is set.
#
# OpenAI reasoning models (o-series / gpt-5-class) take the effort level
# verbatim via `reasoning_effort`; the reasoning tokens count against
# `max_completion_tokens` (reasoning models reject the legacy `max_tokens`),
# so higher effort gets a higher ceiling to avoid truncating mid-thought.
_EFFORT_MAX_COMPLETION_TOKENS = {"low": 4096, "medium": 16384, "high": 32768}

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_SYSTEM = (
    "You are answering a survey. Select the single option that best reflects your view."
)

_PROMPT_TEMPLATE = """\
Question: {question}

Options:
{options_block}

Respond with ONLY the letter of your choice (e.g., "A"). Do not explain."""


def _build_prompt(question: str, options: list[str]) -> str:
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _PROMPT_TEMPLATE.format(question=question, options_block=options_block)


class RawOpenAIProvider(Provider):
    """Call OpenAI GPT directly with no persona framing."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 1.0,
        effort: str | None = None,
    ):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: "
                "pip install 'synthbench[openai] @ git+https://github.com/DataViking-Tech/SynthBench.git'"
            )
        self._effort = validate_effort(effort, "raw-openai")
        if self._effort is not None and temperature != 1.0:
            # OpenAI reasoning models reject the temperature parameter
            # (sampling is pinned). Refuse the combination up front rather
            # than tag the run with a temperature that cannot apply.
            raise ValueError(
                "raw-openai: --effort targets reasoning models, which do not "
                "support a custom temperature. Drop --temperature (the "
                f"default is 1.0) or remove --effort (got {temperature})."
            )
        self._model = model
        self._temperature = temperature
        self._client = openai.AsyncOpenAI()

    @property
    def name(self) -> str:
        return f"raw-openai/{self._model}"

    @property
    def prompt_template_source(self) -> str:
        return _SYSTEM + "\n" + _PROMPT_TEMPLATE

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        prompt = _build_prompt(question, options)
        system = build_persona_system_prompt(_SYSTEM, persona)

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        if self._effort is not None:
            # Reasoning models: `reasoning_effort` is sent via extra_body so
            # it reaches the request JSON regardless of openai SDK version.
            # They reject `max_tokens` (use max_completion_tokens) and the
            # temperature parameter (sampling is pinned at the default), so
            # neither is sent. Non-reasoning models reject reasoning_effort
            # with a 400 that surfaces (after bounded retries) as a
            # ProviderError — a loud failure, never silently untrue metadata.
            request_kwargs: dict = {
                "model": self._model,
                "max_completion_tokens": _EFFORT_MAX_COMPLETION_TOKENS[self._effort],
                "messages": messages,
                "extra_body": {"reasoning_effort": self._effort},
            }
        else:
            request_kwargs = {
                "model": self._model,
                "max_tokens": 8,
                "temperature": self._temperature,
                "messages": messages,
            }

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
