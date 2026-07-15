"""Base provider interface for SynthBench."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass

# Reasoning-effort levels accepted by --effort. Kept deliberately small:
# every supported provider maps these three tiers onto its own native
# reasoning knob (see each provider's _EFFORT_* table), so a leaderboard
# row tagged "high" means the same qualitative thing across vendors.
EFFORT_LEVELS = ("low", "medium", "high")


def validate_effort(effort: str | None, provider_label: str) -> str | None:
    """Validate a reasoning-effort level at provider construction time.

    Returns the value unchanged when valid (or None). Raises ``ValueError``
    for unknown levels — never silently coerce, or the run's config would
    claim an effort that was not actually applied.
    """
    if effort is not None and effort not in EFFORT_LEVELS:
        raise ValueError(
            f"{provider_label}: unknown effort level {effort!r} "
            f"(expected one of {', '.join(EFFORT_LEVELS)})"
        )
    return effort


@dataclass
class PersonaSpec:
    """Specification for persona conditioning."""

    demographics: dict[str, str]
    attribute: str = ""
    group: str = ""
    biography: str | None = None
    conditioning_style: str = "default"


@dataclass
class Distribution:
    """A probability distribution over options."""

    probabilities: list[float]
    refusal_probability: float = 0.0
    method: str = "sampling"
    n_samples: int | None = None
    metadata: dict | None = None
    n_parse_failures: int = 0
    """Samples whose response could not be mapped to any option.

    Parse failures are excluded from ``probabilities`` and from
    ``n_samples`` — they are reported here so the runner can surface a
    real ``n_parse_failures`` instead of silently folding failures into
    the distribution.
    """


class ProviderError(RuntimeError):
    """Infrastructure failure while querying a provider.

    Raised (after bounded retries) instead of fabricating a response or
    publishing a uniform distribution. Distinct from a refusal, which is a
    legitimate model behaviour tracked via ``Response.refusal``.
    """


@dataclass
class Response:
    """A single response from a provider.

    ``selected_option`` is ``None`` when the raw response could not be
    parsed into any of the offered options (a parse failure). Providers
    must NOT substitute a default option — the runner counts these as
    parse failures and excludes them from the distribution.
    """

    selected_option: str | None
    raw_text: str = ""
    metadata: dict | None = None
    refusal: bool = False


class Provider(ABC):
    """Interface that all synthetic respondent providers implement.

    Providers answer survey questions by selecting from given options.
    The harness calls respond() multiple times per question to build
    an empirical distribution, or get_distribution() for providers that
    return distributions natively.
    """

    @abstractmethod
    async def respond(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
    ) -> Response:
        """Answer a survey question by selecting one option.

        Args:
            question: The survey question text.
            options: List of answer choices.
            persona: Optional persona conditioning.

        Returns:
            Response with the selected option text.
        """
        ...

    async def get_distribution(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
        n_samples: int | None = None,
    ) -> Distribution:
        """Get a probability distribution over options.

        Default implementation calls respond() n_samples times and builds
        an empirical distribution. Override for providers that return
        distributions natively (e.g., via logprobs or direct probability output).

        Args:
            n_samples: Number of samples. Defaults to 30 for sampling providers.
                Logprob providers ignore this parameter.
        """
        effective_samples = n_samples if n_samples is not None else 30
        tasks = [
            self.respond(question, options, persona=persona)
            for _ in range(effective_samples)
        ]
        results = await asyncio.gather(*tasks)

        valid_options = set(options)
        refusals = sum(1 for r in results if r.refusal)
        responses = [
            r.selected_option
            for r in results
            if not r.refusal and r.selected_option in valid_options
        ]
        parse_failures = sum(
            1
            for r in results
            if not r.refusal and r.selected_option not in valid_options
        )

        # Parse failures carry no signal about the answer distribution —
        # exclude them from both the numerator and the denominator.
        total = len(responses) + refusals
        counts = Counter(responses)
        probs = [counts.get(opt, 0) / max(total, 1) for opt in options]
        refusal_prob = refusals / max(total, 1)

        return Distribution(
            probabilities=probs,
            refusal_probability=refusal_prob,
            method="sampling",
            n_samples=total,
            n_parse_failures=parse_failures,
        )

    @property
    def supports_distribution(self) -> bool:
        """Whether this provider natively supports distribution output.

        Override to return True if get_distribution() has a native
        implementation (not just repeated sampling).
        """
        return False

    @property
    def prompt_template_source(self) -> str:
        """Deterministic representation of the prompt surface this provider uses.

        Used by the harness to derive ``reproducibility.prompt_template_hash``
        so Tier-3 validation can detect prompt drift between submissions.
        Providers that send text to a model should override this to return
        the literal system + user template strings. Providers that don't
        send a prompt (baselines) can leave it empty.
        """
        return ""

    async def close(self) -> None:
        """Clean up resources (HTTP clients, etc.)."""
        pass

    @property
    @abstractmethod
    def name(self) -> str: ...


def build_persona_system_prompt(base_system: str, persona: PersonaSpec | None) -> str:
    """Build system prompt with optional persona conditioning.

    When persona is provided, replaces the base system prompt with a
    demographics-aware framing that instructs the model to respond
    as a person with those demographic characteristics.
    """
    if persona is None:
        return base_system
    demo_parts = [f"{k}: {v}" for k, v in persona.demographics.items()]
    return (
        f"You are a survey respondent. Demographics: {', '.join(demo_parts)}. "
        "Answer as this person would."
    )
