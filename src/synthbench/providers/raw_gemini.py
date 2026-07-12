"""Raw Google Gemini provider — no persona conditioning.

Uses Gemini's OpenAI-compatible endpoint so we can reuse the openai SDK.
Requires GEMINI_API_KEY environment variable.
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

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _build_prompt(question: str, options: list[str]) -> str:
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _PROMPT_TEMPLATE.format(question=question, options_block=options_block)


class RawGeminiProvider(Provider):
    """Call Google Gemini directly with no persona framing.

    Uses the OpenAI-compatible endpoint so we need only the openai SDK.
    """

    def __init__(self, model: str = "gemini-2.5-flash-lite", temperature: float = 1.0):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: "
                "pip install 'synthbench[openai]'"
            )

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is required. "
                "Get one at https://aistudio.google.com/apikey"
            )

        self._model = model
        self._temperature = temperature
        self._client = openai.AsyncOpenAI(
            api_key=gemini_key,
            base_url=_GEMINI_BASE_URL,
        )

    @property
    def name(self) -> str:
        return f"raw-gemini/{self._model}"

    @property
    def prompt_template_source(self) -> str:
        return _SYSTEM + "\n" + _PROMPT_TEMPLATE

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        prompt = _build_prompt(question, options)
        system = build_persona_system_prompt(_SYSTEM, persona)

        resp = await call_with_retries(
            lambda: self._client.chat.completions.create(
                model=self._model,
                max_tokens=8,
                temperature=self._temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
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
