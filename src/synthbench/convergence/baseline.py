"""Stable baseline-loader export for synthpanel's ``--calibrate-against`` flag.

synthpanel (>= 0.9) probes ``synthbench`` at runtime for a
``load_convergence_baseline`` callable when a user passes
``--calibrate-against DATASET:QUESTION``. This module is the single
owner of that export.

Policy:

* ``full``-tier datasets (currently ``gss`` and ``ntia``) return the
  aggregate ``human_distribution`` directly — the underlying license is
  unambiguously public.
* ``gated``-tier datasets raise :class:`BaselineGatedError`. Serving
  those payloads requires hitting the authenticated R2 origin with
  credentials, which is out of scope for the in-process loader.
* ``aggregates_only`` / ``citation_only`` datasets raise
  :class:`BaselineUnavailable` — synthbench has no per-question
  redistribution rights for them at all.
* Unknown datasets raise :class:`BaselineUnavailable`; the policy
  lookup is conservative (defaults to ``aggregates_only``) and a typo
  should not silently leak or crash downstream.

The return shape is fixed by ``docs/convergence-analysis.md`` — synthpanel
attaches ``human_distribution`` to every matching question's
``calibration`` sub-object and computes JSD with its own local metric.
"""

from __future__ import annotations

from typing import Any

from synthbench.datasets import DATASETS
from synthbench.datasets.policy import policy_for


class BaselineUnavailable(LookupError):
    """Raised when no per-question baseline can be returned for this dataset.

    Covers unknown datasets and the ``aggregates_only`` / ``citation_only``
    tiers where synthbench ships no per-question artifact at all.
    """


class BaselineGatedError(BaselineUnavailable):
    """Raised when the dataset is ``gated`` and requires authenticated access.

    The in-process loader cannot vend gated-tier baselines — those payloads
    live behind the JWT-authenticated R2 origin. synthpanel can surface this
    to the user as an "authenticate to calibrate against <dataset>" hint.
    """


def load_convergence_baseline(
    dataset: str,
    question_key: str | None = None,
) -> dict[str, Any]:
    """Return the aggregate baseline payload for one question.

    Args:
        dataset: Adapter name as registered in
            :data:`synthbench.datasets.DATASETS` (e.g. ``"gss"``, ``"ntia"``).
            A filter suffix like ``"gss (2018)"`` is accepted and resolves
            to the base-name adapter.
        question_key: Question identifier. Accepts both the canonical
            :attr:`Question.key` (e.g. ``"GSS_SPKATH"``) and the bare
            upstream id (``"SPKATH"``). Required.

    Returns:
        Dict shaped per ``docs/convergence-analysis.md`` with keys:
        ``dataset``, ``question_key``, ``human_distribution``,
        ``redistribution_policy``, ``license_url``, ``citation``.

    Raises:
        BaselineGatedError: dataset tier is ``gated`` — authenticated
            access required.
        BaselineUnavailable: dataset is unknown or its tier is
            ``aggregates_only`` / ``citation_only``; or the requested
            question key does not resolve in the adapter.
        ValueError: ``question_key`` was not provided.
    """
    if not question_key:
        raise ValueError(
            "question_key is required: load_convergence_baseline needs a "
            "specific question to return human_distribution for"
        )

    policy = policy_for(dataset)

    if policy.redistribution_policy == "gated":
        raise BaselineGatedError(
            f"dataset {policy.name!r} is gated-tier; baseline requires "
            "authenticated access to the R2 origin and cannot be loaded "
            "from the in-process synthbench API"
        )

    if policy.redistribution_policy != "full":
        raise BaselineUnavailable(
            f"dataset {dataset!r} has no per-question baseline available "
            f"(tier={policy.redistribution_policy!r})"
        )

    adapter_cls = DATASETS.get(policy.name)
    if adapter_cls is None:
        # policy_for() falls back to "aggregates_only" for unknown names,
        # so we'd have bailed above. This is defensive: a future adapter
        # whose policy is declared elsewhere could theoretically skip
        # registration.
        raise BaselineUnavailable(f"no registered adapter for dataset {dataset!r}")

    question = _resolve_question(adapter_cls(), question_key)

    return {
        "dataset": policy.name,
        "question_key": question.key,
        "human_distribution": dict(question.human_distribution),
        "redistribution_policy": policy.redistribution_policy,
        "license_url": policy.license_url,
        "citation": policy.citation,
    }


def _resolve_question(dataset, question_key: str):
    """Locate a Question by key; accept bare or adapter-prefixed forms.

    Mirrors the CLI's :func:`convergence.cli_report._resolve_question`
    behavior so synthpanel callers can pass either the canonical
    ``Question.key`` or the bare upstream id.
    """
    questions = dataset.load()
    for q in questions:
        if q.key == question_key:
            return q
    suffixed = [q for q in questions if q.key.endswith(f"_{question_key}")]
    if len(suffixed) == 1:
        return suffixed[0]
    raise BaselineUnavailable(
        f"no question with key {question_key!r} in dataset {dataset.name!r}"
    )


__all__ = [
    "load_convergence_baseline",
    "BaselineUnavailable",
    "BaselineGatedError",
]
