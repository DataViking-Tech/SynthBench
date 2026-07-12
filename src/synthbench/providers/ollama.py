"""Ollama local model provider — no API key required.

Connects to a local Ollama instance via its OpenAI-compatible endpoint.
Default: http://localhost:11434/v1
"""

from __future__ import annotations

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

_DEFAULT_BASE_URL = "http://localhost:11434/v1"


def _build_prompt(question: str, options: list[str]) -> str:
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _PROMPT_TEMPLATE.format(question=question, options_block=options_block)


class OllamaProvider(Provider):
    """Call a local Ollama model with no persona framing.

    No API key required. Ollama must be running locally (or at a
    custom base_url).
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = _DEFAULT_BASE_URL,
        temperature: float = 1.0,
    ):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: "
                "pip install 'synthbench[openai]'"
            )

        self._model = model
        self._temperature = temperature
        self._client = openai.AsyncOpenAI(
            api_key="ollama",  # Ollama doesn't need a real key
            base_url=base_url,
        )

    @property
    def name(self) -> str:
        return f"ollama/{self._model}"

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

        return Response(
            selected_option=parsed.option,
            raw_text=raw_text,
            refusal=parsed.refusal,
            metadata={
                "model": self._model,
                "finish_reason": resp.choices[0].finish_reason,
                "usage": None,
            },
        )

    async def close(self) -> None:
        await self._client.close()
