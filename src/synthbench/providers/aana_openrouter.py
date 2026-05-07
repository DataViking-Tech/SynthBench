"""AANA-constrained OpenRouter provider.

This provider uses OpenRouter as the base generator and applies a minimal
AANA-style runtime contract around survey responses: answer only from the
provided option set, preserve persona/question constraints, and emit a single
choice for downstream parsing.
"""

from __future__ import annotations

import os
import re

from synthbench.providers.base import (
    PersonaSpec,
    Provider,
    Response,
    build_persona_system_prompt,
)

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_SYSTEM = (
    "You are the base generator inside an Alignment-Aware Neural Architecture "
    "(AANA) survey respondent. Preserve the user's survey question and persona "
    "constraints, select exactly one listed option, and do not add explanation. "
    "If the options are imperfect, choose the closest listed option rather than "
    "inventing a new answer."
)

_PROMPT_TEMPLATE = """\
Question: {question}

Options:
{options_block}

AANA gate constraints:
- Return exactly one option letter.
- The selected letter must map to one listed option.
- Do not explain the choice.

Respond with ONLY the letter of your choice (e.g., "A")."""

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _build_prompt(question: str, options: list[str]) -> str:
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _PROMPT_TEMPLATE.format(question=question, options_block=options_block)


def _parse_letter(text: str, options: list[str]) -> str | None:
    text = text.strip()
    match = re.match(r"^\(?([A-Z])\)?", text.upper())
    if match:
        idx = ord(match.group(1)) - ord("A")
        if 0 <= idx < len(options):
            return options[idx]

    text_lower = text.lower()
    for opt in options:
        if opt.lower() in text_lower:
            return opt
    return None


class AANAOpenRouterProvider(Provider):
    """Call an OpenRouter model under an AANA response contract."""

    def __init__(self, model: str = "openai/gpt-4o-mini", **kwargs):
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "openai package required. Install with: pip install 'synthbench[openai]'"
            ) from exc

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Get one at https://openrouter.ai/keys"
            )

        self._model = model
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=_OPENROUTER_BASE_URL,
        )

    @property
    def name(self) -> str:
        return f"aana/openrouter/{self._model}"

    @property
    def prompt_template_source(self) -> str:
        return _SYSTEM + "\n" + _PROMPT_TEMPLATE

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        prompt = _build_prompt(question, options)
        system = build_persona_system_prompt(_SYSTEM, persona)

        resp = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=8,
            temperature=1.0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )

        raw_text = resp.choices[0].message.content or ""
        selected = _parse_letter(raw_text, options)
        if selected is None:
            selected = options[0]

        usage = None
        if getattr(resp, "usage", None) is not None:
            usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            }

        return Response(
            selected_option=selected,
            raw_text=raw_text,
            metadata={
                "model": self._model,
                "architecture": "AANA",
                "gate_contract": "single listed option",
                "finish_reason": resp.choices[0].finish_reason,
                "usage": usage,
            },
        )

    async def close(self) -> None:
        await self._client.close()
