"""Generic HTTP endpoint provider."""

from __future__ import annotations

from dataclasses import asdict

import httpx

from synthbench.providers.base import Distribution, PersonaSpec, Provider, Response


class HttpProvider(Provider):
    """Call an arbitrary HTTP endpoint that accepts survey questions.

    The endpoint receives a POST with JSON body:
        {"question": str, "options": [str, ...], "persona": {...} | null}

    And returns JSON in one of two modes:
        Single response: {"selected_option": str}
        Distribution:    {"probabilities": [float, ...]}
    """

    def __init__(self, url: str, headers: dict[str, str] | None = None, **kwargs):
        self._url = url
        self._client = httpx.AsyncClient(
            headers=headers or {},
            timeout=30,
        )

    @property
    def name(self) -> str:
        return f"http/{self._url}"

    def _build_body(
        self,
        question: str,
        options: list[str],
        persona: PersonaSpec | None = None,
    ) -> dict:
        body: dict = {"question": question, "options": options}
        if persona is not None:
            body["persona"] = asdict(persona)
        return body

    async def respond(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
    ) -> Response:
        body = self._build_body(question, options, persona)
        resp = await self._client.post(self._url, json=body)
        resp.raise_for_status()
        data = resp.json()

        selected = data.get("selected_option", "")
        if selected not in options:
            # Try to match
            for opt in options:
                if opt.lower() == selected.lower():
                    selected = opt
                    break
            else:
                selected = options[0]

        return Response(
            selected_option=selected,
            raw_text=str(data),
            metadata=data.get("metadata"),
            refusal=data.get("refusal", False),
        )

    async def get_distribution(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
        n_samples: int = 30,
    ) -> Distribution:
        body = self._build_body(question, options, persona)
        resp = await self._client.post(self._url, json=body)
        resp.raise_for_status()
        data = resp.json()

        if "probabilities" in data:
            return Distribution(
                probabilities=data["probabilities"],
                refusal_probability=data.get("refusal_probability", 0.0),
                method="reported",
                n_samples=data.get("n_samples"),
            )

        # Endpoint returns individual responses — fall back to sampling
        return await super().get_distribution(
            question, options, persona=persona, n_samples=n_samples
        )

    async def close(self) -> None:
        await self._client.aclose()
