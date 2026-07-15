"""Raw Anthropic Claude provider — no persona conditioning."""

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

# Reasoning-effort → extended-thinking budget (tokens).
#
# Anthropic has no named effort levels; extended thinking takes an explicit
# `budget_tokens`. These tiers are SynthBench's canonical mapping and are
# mirrored by the OpenRouter provider's max_tokens ceilings so a Claude
# model reached via the gateway derives the same budgets (low=0.2*10240,
# medium=0.5*16384, high=0.8*30720). Anthropic's minimum budget is 1024.
_EFFORT_BUDGET_TOKENS = {"low": 2048, "medium": 8192, "high": 24576}

# Headroom on top of the thinking budget for the final visible answer
# (a single option letter). max_tokens must exceed budget_tokens.
_EFFORT_ANSWER_HEADROOM = 64

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


class RawAnthropicProvider(Provider):
    """Call Claude directly with no persona framing."""

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 1.0,  # Sample, don't argmax
        effort: str | None = None,
    ):
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: "
                "pip install 'synthbench[anthropic]'"
            )
        self._effort = validate_effort(effort, "raw-anthropic")
        if self._effort is not None and temperature != 1.0:
            # The Messages API only accepts temperature=1 while extended
            # thinking is enabled. Refuse up front rather than let every
            # request 400 — and never silently drop either knob, or the
            # run's config would claim settings that were not applied.
            raise ValueError(
                "raw-anthropic: --effort enables extended thinking, which "
                "requires temperature=1. Drop --temperature (the default is "
                f"1.0) or remove --effort (got temperature={temperature})."
            )
        self._model = model
        self._temperature = temperature
        self._client = anthropic.AsyncAnthropic()

    @property
    def name(self) -> str:
        return f"raw-anthropic/{self._model}"

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
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self._effort is not None:
            # Extended thinking. Thinking tokens count against max_tokens,
            # so the ceiling is budget + a small answer allowance. Models
            # without extended-thinking support reject the `thinking` block
            # with a 400 that surfaces (after bounded retries) as a
            # ProviderError — a loud failure, never a silently untagged run.
            budget = _EFFORT_BUDGET_TOKENS[self._effort]
            request_kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget,
            }
            request_kwargs["max_tokens"] = budget + _EFFORT_ANSWER_HEADROOM

        message = await call_with_retries(
            lambda: self._client.messages.create(**request_kwargs)
        )

        # With extended thinking the content list leads with thinking
        # block(s); the answer is the first text block. Without thinking the
        # first block IS the text block, so this is a no-op for plain runs.
        raw_text = next(
            (
                block.text
                for block in (message.content or [])
                if getattr(block, "type", "text") == "text"
            ),
            "",
        )
        parsed = parse_option_response(raw_text, options)

        usage = None
        if getattr(message, "usage", None) is not None:
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }

        return Response(
            selected_option=parsed.option,
            raw_text=raw_text,
            refusal=parsed.refusal,
            metadata={
                "model": self._model,
                "stop_reason": message.stop_reason,
                "usage": usage,
            },
        )

    async def close(self) -> None:
        await self._client.close()
