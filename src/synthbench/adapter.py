"""Vendor-adapter interface for `synthbench submit-adapter` (refs #256).

The adapter is the contract between SynthBench and a third-party synthetic-
respondent vendor. Vendors implement a subclass of :class:`Adapter` in their
own Python module, then point `synthbench submit-adapter --adapter` at the
module path. The submit pipeline imports the module, instantiates the
adapter, runs the standard suite against it, and produces a submission
artifact suitable for opening a PR against the leaderboard repo.

Adapters are intentionally narrow: vendors expose **one** async method
(:meth:`Adapter.respond`) that returns a string answer to a single question
under a single persona condition. Everything upstream of that — distribution
estimation, scoring, run-hash content addressing — is owned by SynthBench so
that vendor implementations stay simple and the evaluation surface stays
honest.

NOTE (refs #256): the full evaluation pipeline that drives `Adapter.respond`
through the `core` suite is still scaffold-only as of this PR. The interface
is frozen here so vendors can start writing adapters in parallel with the
pipeline build-out tracked in follow-up issues.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Any


class Adapter(ABC):
    """Base class every vendor adapter must subclass.

    Implementations should be:
      * **Stateless across questions** — the harness may call ``respond``
        from many coroutines concurrently. Any per-instance state must be
        safe under ``asyncio.gather``.
      * **Side-effect free** — no writing to disk, no global mutation. The
        harness is responsible for persistence.
      * **Deterministic given the same inputs**, where possible. Sampling
        randomness is expected (models are stochastic); orchestration
        randomness is not.

    Two metadata properties are required so the harness can stamp the run
    artifact with vendor identity without re-reading CLI flags:
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable vendor/model identifier (e.g. ``"acme/gpt-4o"``).

        This appears in the leaderboard row and the submission filename, so
        prefer short, stable strings. Avoid embedding timestamps or git
        SHAs here — use :attr:`version` for that.
        """

    @property
    @abstractmethod
    def version(self) -> str:
        """Adapter version string (e.g. ``"2026.05.14"`` or a semver tag).

        Bumped whenever the prompt, sampling parameters, or model snapshot
        materially changes. Two runs with the same ``(name, version)`` are
        expected to be comparable; differing versions are not.
        """

    @abstractmethod
    async def respond(
        self,
        *,
        question: str,
        persona: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        """Answer a single question under a single persona condition.

        Args:
            question: The prompt the harness wants a respondent answer to.
                Already includes options where applicable; the adapter
                should not re-format it.
            persona: Demographic + attitudinal conditioning for this
                respondent. Keys follow the
                :class:`synthbench.providers.base.PersonaSpec` shape (e.g.
                ``{"age": "30-44", "party": "Democrat", ...}``). May be
                empty if the suite calls for unconditioned answers.
            context: Optional suite-specific metadata (e.g. question id,
                survey wave). Adapters should ignore unknown keys.

        Returns:
            The raw answer string. The harness handles parsing this into
            an option index or Likert number, so adapters should return
            whatever shape feels native to their model (a single token, a
            short phrase, or a number).
        """


class RandomAdapter(Adapter):
    """Reference adapter that emits trivial answers, for wiring up tests.

    Returns ``"yes"`` / ``"no"`` for boolean-flavored questions and a
    uniformly random Likert integer (1-5) otherwise. Seeded so the test
    suite stays deterministic.

    This adapter exists so vendors (and SynthBench CI) have a known-good
    target to point ``synthbench submit-adapter --adapter`` at while
    debugging their setup. It is **not** a baseline — its scores are
    expected to be terrible.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return "synthbench/random-adapter"

    @property
    def version(self) -> str:
        return "0.1.0"

    async def respond(
        self,
        *,
        question: str,
        persona: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        q = question.lower()
        if "yes or no" in q or q.strip().endswith("?") and "agree" not in q:
            return self._rng.choice(["yes", "no"])
        return str(self._rng.randint(1, 5))
