"""Contamination detection for benchmark results.

Three complementary probes:

1. Cross-model convergence (:func:`convergence_analysis`) — given multiple
   result files, flag questions where every model produces nearly-identical
   distributions (low variance = likely shared memorization).
2. Paraphrase sensitivity (:func:`run_contamination_test`) — for a single
   model, run the 50 original OpinionsQA questions alongside 3 paraphrases
   each and measure how much parity changes. High sensitivity = the model
   behaves very differently on rephrased inputs, consistent with surface-form
   memorization rather than semantic reasoning.
3. De-identification sensitivity (:func:`run_deident_test`) — for a single
   model, run 20 well-known opinion topics at 5 progressively abstracted
   levels (full brand → feature description). A model that reasons from
   features should produce stable distributions across levels; a model that
   recognizes the brand and recalls training-corpus opinions drifts as
   identifying information is stripped.
"""

from __future__ import annotations

import asyncio
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthbench.providers.base import Provider


@dataclass(frozen=True)
class QuestionContamination:
    """Contamination risk assessment for a single question."""

    key: str
    text: str
    options: list[str]
    mean_std: float  # Mean std across all options (lower = more suspicious)
    contamination_risk: float  # 0..1 score; 1 = highest risk (lowest variance)
    per_option_std: dict[str, float]  # std of each option's proportion across models
    n_models: int
    model_distributions: dict[str, dict[str, float]]  # model -> option -> proportion


@dataclass
class ConvergenceAnalysis:
    """Full convergence analysis across all questions and models."""

    questions: list[QuestionContamination]
    n_models: int
    n_questions: int
    model_names: list[str]
    mean_contamination_risk: float
    high_risk_count: int  # questions with contamination_risk >= 0.8
    medium_risk_count: int  # questions with 0.5 <= contamination_risk < 0.8
    low_risk_count: int  # questions with contamination_risk < 0.5


def _std(values: list[float]) -> float:
    """Population standard deviation (no scipy needed)."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def load_result_distributions(
    path: Path,
) -> tuple[str, dict[str, dict[str, float]], dict[str, str]]:
    """Load per-question model distributions from a result JSON file.

    Returns:
        (provider_name, {question_key: {option: proportion}}, {question_key: text})
    """
    with open(path) as f:
        data = json.load(f)

    if data.get("benchmark") != "synthbench":
        raise ValueError(f"Not a synthbench result file: {path}")

    provider = data.get("config", {}).get("provider", str(path))
    distributions: dict[str, dict[str, float]] = {}
    texts: dict[str, str] = {}

    for q in data.get("per_question", []):
        key = q["key"]
        distributions[key] = q["model_distribution"]
        texts[key] = q.get("text", "")

    return provider, distributions, texts


def convergence_analysis(
    result_files: list[Path],
    *,
    min_models: int = 2,
) -> ConvergenceAnalysis:
    """Compute per-question contamination risk from cross-model convergence.

    For each question present in at least ``min_models`` result files, computes
    the standard deviation of each option's proportion across models. Low std
    means all models produce nearly identical distributions — a contamination
    signal.

    The contamination_risk score is 1 - normalized_mean_std, where
    normalized_mean_std is the mean option std divided by the theoretical
    maximum std for that number of models.

    Args:
        result_files: Paths to synthbench result JSON files.
        min_models: Minimum number of models a question must appear in.

    Returns:
        ConvergenceAnalysis with per-question contamination risk scores.
    """
    # Load all results
    model_data: dict[str, dict[str, dict[str, float]]] = {}  # model -> key -> dist
    all_texts: dict[str, str] = {}
    model_names: list[str] = []

    for path in result_files:
        provider, distributions, texts = load_result_distributions(path)
        # Deduplicate provider names by appending a counter if needed
        base_name = provider
        counter = 1
        while provider in model_data:
            counter += 1
            provider = f"{base_name}#{counter}"
        model_data[provider] = distributions
        model_names.append(provider)
        all_texts.update(texts)

    if len(model_names) < 2:
        raise ValueError(f"Need at least 2 model result files, got {len(model_names)}")

    # Collect all question keys that appear in >= min_models files
    key_counts: dict[str, int] = {}
    for distributions in model_data.values():
        for key in distributions:
            key_counts[key] = key_counts.get(key, 0) + 1

    eligible_keys = sorted(k for k, c in key_counts.items() if c >= min_models)

    if not eligible_keys:
        raise ValueError(f"No questions found in >= {min_models} result files")

    # For each eligible question, compute cross-model distribution std
    questions: list[QuestionContamination] = []

    for key in eligible_keys:
        # Collect all option names across models for this question
        all_options: set[str] = set()
        model_dists_for_key: dict[str, dict[str, float]] = {}

        for model, distributions in model_data.items():
            if key in distributions:
                dist = distributions[key]
                all_options.update(dist.keys())
                model_dists_for_key[model] = dist

        sorted_options = sorted(all_options)
        n_models_for_q = len(model_dists_for_key)

        # Compute std of each option's proportion across models
        per_option_std: dict[str, float] = {}
        for option in sorted_options:
            proportions = [
                dist.get(option, 0.0) for dist in model_dists_for_key.values()
            ]
            per_option_std[option] = _std(proportions)

        # Mean std across all options
        mean_std = (
            sum(per_option_std.values()) / len(per_option_std)
            if per_option_std
            else 0.0
        )

        # Theoretical max std for proportions with n models:
        # Max std for a binary proportion (0 or 1 split across models) is 0.5
        # when exactly half the models say 0 and half say 1.
        # For a uniform [0,1] distribution, max population std is 0.5.
        # We normalize mean_std by 0.5 to get a 0..1 scale.
        max_possible_std = 0.5
        normalized = (
            min(mean_std / max_possible_std, 1.0) if max_possible_std > 0 else 0.0
        )
        contamination_risk = round(1.0 - normalized, 6)

        questions.append(
            QuestionContamination(
                key=key,
                text=all_texts.get(key, ""),
                options=sorted_options,
                mean_std=round(mean_std, 6),
                contamination_risk=contamination_risk,
                per_option_std={k: round(v, 6) for k, v in per_option_std.items()},
                n_models=n_models_for_q,
                model_distributions=model_dists_for_key,
            )
        )

    # Aggregate stats
    mean_risk = sum(q.contamination_risk for q in questions) / len(questions)
    high_risk = sum(1 for q in questions if q.contamination_risk >= 0.8)
    medium_risk = sum(1 for q in questions if 0.5 <= q.contamination_risk < 0.8)
    low_risk = sum(1 for q in questions if q.contamination_risk < 0.5)

    return ConvergenceAnalysis(
        questions=questions,
        n_models=len(model_names),
        n_questions=len(questions),
        model_names=model_names,
        mean_contamination_risk=round(mean_risk, 6),
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
    )


def format_convergence_report(analysis: ConvergenceAnalysis) -> str:
    """Format a convergence analysis as a markdown report."""
    lines = [
        "# Cross-Model Convergence Analysis",
        "",
        f"**Models:** {analysis.n_models}",
        f"**Questions analyzed:** {analysis.n_questions}",
        f"**Mean contamination risk:** {analysis.mean_contamination_risk:.4f}",
        "",
        "## Risk Distribution",
        "",
        f"- High risk (>= 0.8): {analysis.high_risk_count} questions",
        f"- Medium risk (0.5-0.8): {analysis.medium_risk_count} questions",
        f"- Low risk (< 0.5): {analysis.low_risk_count} questions",
        "",
        "## Models",
        "",
    ]

    for name in analysis.model_names:
        lines.append(f"- {name}")

    lines.append("")

    # Top contamination risks
    sorted_q = sorted(
        analysis.questions, key=lambda q: q.contamination_risk, reverse=True
    )

    lines.extend(
        [
            "## Highest Contamination Risk (top 20)",
            "",
            "| Rank | Key | Risk | Mean Std | Models | Text |",
            "|------|-----|------|----------|--------|------|",
        ]
    )

    for i, q in enumerate(sorted_q[:20], 1):
        text_trunc = q.text[:60] + "..." if len(q.text) > 60 else q.text
        lines.append(
            f"| {i} | {q.key} | {q.contamination_risk:.4f} | "
            f"{q.mean_std:.4f} | {q.n_models} | {text_trunc} |"
        )

    lines.append("")

    # Lowest risk (genuine reasoning)
    lines.extend(
        [
            "## Lowest Contamination Risk (most divergent, top 20)",
            "",
            "| Rank | Key | Risk | Mean Std | Models | Text |",
            "|------|-----|------|----------|--------|------|",
        ]
    )

    for i, q in enumerate(reversed(sorted_q[-20:]), 1):
        text_trunc = q.text[:60] + "..." if len(q.text) > 60 else q.text
        lines.append(
            f"| {i} | {q.key} | {q.contamination_risk:.4f} | "
            f"{q.mean_std:.4f} | {q.n_models} | {text_trunc} |"
        )

    lines.append("")
    return "\n".join(lines)


@dataclass
class ParaphraseQuestionResult:
    """Paraphrase sensitivity result for a single question."""

    key: str
    original_text: str
    options: list[str]
    human_distribution: dict[str, float]
    original_model_distribution: dict[str, float]
    original_parity: float
    paraphrases: list[str]
    paraphrase_model_distributions: list[dict[str, float]]
    paraphrase_parities: list[float]
    mean_paraphrase_parity: float
    delta: float  # original_parity - mean_paraphrase_parity (signed)
    sensitivity_pct: float  # delta / original_parity * 100


@dataclass
class ContaminationTestResult:
    """Aggregate paraphrase sensitivity result across all questions."""

    provider_name: str
    n_originals: int
    n_paraphrases_per: int
    samples_per_question: int
    per_question: list[ParaphraseQuestionResult]
    original_sps: float  # mean parity on the 50 originals
    adjusted_sps: float  # mean parity on all 150 paraphrases
    sensitivity_pct: float  # (original_sps - adjusted_sps) / original_sps * 100
    elapsed_seconds: float


def _parity_against_human(human: dict[str, float], model: dict[str, float]) -> float:
    """JSD + Kendall's tau composite parity score for one distribution pair."""
    from synthbench.metrics import (
        jensen_shannon_divergence,
        kendall_tau_b,
        parity_score,
    )

    jsd = jensen_shannon_divergence(human, model)
    tau = kendall_tau_b(human, model)
    return parity_score(jsd, tau)


async def run_contamination_test(
    *,
    provider: Provider,
    samples_per_question: int,
    concurrency: int = 10,
    suite_path: Path,
) -> ContaminationTestResult:
    """Run the paraphrase sensitivity test against a single provider.

    Loads a paraphrase suite (see ``suites/paraphrase_test.json``), queries
    the provider for a distribution on every original and paraphrased
    question, and measures the parity delta. Lower delta = the model is
    robust to surface-form changes (less likely to be memorizing).

    Args:
        provider: Provider to evaluate.
        samples_per_question: Samples used to estimate each distribution.
        concurrency: Max concurrent in-flight distribution requests.
        suite_path: Path to the paraphrase suite JSON.

    Returns:
        ContaminationTestResult with per-question and aggregate metrics.
    """
    with open(suite_path) as f:
        suite = json.load(f)

    items: list[dict] = suite["items"]
    if not items:
        raise ValueError(f"Paraphrase suite is empty: {suite_path}")

    sem = asyncio.Semaphore(max(1, concurrency))

    async def _query(text: str, options: list[str]) -> dict[str, float]:
        async with sem:
            dist = await provider.get_distribution(
                text, options, n_samples=samples_per_question
            )
        return dict(zip(options, dist.probabilities))

    tasks: list[asyncio.Task] = []
    for item in items:
        options = item["options"]
        tasks.append(asyncio.create_task(_query(item["original_text"], options)))
        for paraphrase in item["paraphrases"]:
            tasks.append(asyncio.create_task(_query(paraphrase, options)))

    t0 = time.monotonic()
    all_dists = await asyncio.gather(*tasks)
    elapsed = time.monotonic() - t0

    per_question: list[ParaphraseQuestionResult] = []
    original_parities: list[float] = []
    paraphrase_parities_flat: list[float] = []
    idx = 0

    for item in items:
        options = item["options"]
        human = item["human_distribution"]
        paraphrases: list[str] = item["paraphrases"]

        original_dist = all_dists[idx]
        idx += 1
        original_parity = _parity_against_human(human, original_dist)

        paraphrase_dists: list[dict[str, float]] = []
        paraphrase_parities: list[float] = []
        for _ in paraphrases:
            pd = all_dists[idx]
            idx += 1
            paraphrase_dists.append(pd)
            paraphrase_parities.append(_parity_against_human(human, pd))

        mean_para = (
            sum(paraphrase_parities) / len(paraphrase_parities)
            if paraphrase_parities
            else 0.0
        )
        delta = original_parity - mean_para
        sensitivity_pct = (
            (delta / original_parity * 100.0) if original_parity > 0 else 0.0
        )

        per_question.append(
            ParaphraseQuestionResult(
                key=item["key"],
                original_text=item["original_text"],
                options=options,
                human_distribution=human,
                original_model_distribution=original_dist,
                original_parity=original_parity,
                paraphrases=paraphrases,
                paraphrase_model_distributions=paraphrase_dists,
                paraphrase_parities=paraphrase_parities,
                mean_paraphrase_parity=mean_para,
                delta=delta,
                sensitivity_pct=sensitivity_pct,
            )
        )
        original_parities.append(original_parity)
        paraphrase_parities_flat.extend(paraphrase_parities)

    original_sps = (
        sum(original_parities) / len(original_parities) if original_parities else 0.0
    )
    adjusted_sps = (
        sum(paraphrase_parities_flat) / len(paraphrase_parities_flat)
        if paraphrase_parities_flat
        else 0.0
    )
    overall_sensitivity_pct = (
        (original_sps - adjusted_sps) / original_sps * 100.0
        if original_sps > 0
        else 0.0
    )

    return ContaminationTestResult(
        provider_name=provider.name,
        n_originals=len(items),
        n_paraphrases_per=len(items[0]["paraphrases"]) if items else 0,
        samples_per_question=samples_per_question,
        per_question=per_question,
        original_sps=original_sps,
        adjusted_sps=adjusted_sps,
        sensitivity_pct=overall_sensitivity_pct,
        elapsed_seconds=elapsed,
    )


def result_to_json(result: ContaminationTestResult) -> dict:
    """Serialize a :class:`ContaminationTestResult` to a JSON-ready dict.

    The ``aggregate.contamination_sensitivity`` field is the canonical
    number to surface in leaderboard aggregates when available.
    """
    return {
        "benchmark": "synthbench",
        "type": "contamination_paraphrase",
        "provider": result.provider_name,
        "config": {
            "samples_per_question": result.samples_per_question,
            "n_originals": result.n_originals,
            "n_paraphrases_per": result.n_paraphrases_per,
        },
        "aggregate": {
            "original_sps": round(result.original_sps, 6),
            "adjusted_sps": round(result.adjusted_sps, 6),
            "contamination_sensitivity": round(result.sensitivity_pct, 6),
        },
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "per_question": [
            {
                "key": q.key,
                "original_text": q.original_text,
                "options": q.options,
                "human_distribution": q.human_distribution,
                "original_model_distribution": q.original_model_distribution,
                "original_parity": round(q.original_parity, 6),
                "paraphrases": q.paraphrases,
                "paraphrase_model_distributions": q.paraphrase_model_distributions,
                "paraphrase_parities": [round(x, 6) for x in q.paraphrase_parities],
                "mean_paraphrase_parity": round(q.mean_paraphrase_parity, 6),
                "delta": round(q.delta, 6),
                "sensitivity_pct": round(q.sensitivity_pct, 6),
            }
            for q in result.per_question
        ],
    }


# ---------------------------------------------------------------------------
# De-identification sensitivity
# ---------------------------------------------------------------------------


@dataclass
class DeidentTopicResult:
    """De-identification sensitivity result for a single topic."""

    key: str
    topic: str
    options: list[str]
    level_texts: list[str]
    level_labels: list[str]
    level_distributions: list[dict[str, float]]
    pairwise_jsd: list[list[float]]  # symmetric n_levels x n_levels matrix
    mean_pairwise_jsd: float  # mean of upper triangle (diagonal excluded)
    per_option_std: dict[str, float]  # std of each option's prob across levels
    mean_option_std: float  # mean across options
    drift_l1_to_l5: float  # JSD between level 1 and level 5 distributions


@dataclass
class DeidentTestResult:
    """Aggregate de-identification sensitivity result across all topics."""

    provider_name: str
    n_topics: int
    n_levels: int
    samples_per_question: int
    level_labels: list[str]
    per_topic: list[DeidentTopicResult]
    mean_pairwise_jsd: float  # avg across topics — primary recognition score
    mean_option_std: float  # avg across topics
    mean_drift_l1_to_l5: float  # avg across topics
    elapsed_seconds: float


def _pairwise_jsd_matrix(distributions: list[dict[str, float]]) -> list[list[float]]:
    """Compute the full symmetric pairwise JSD matrix."""
    from synthbench.metrics import jensen_shannon_divergence

    n = len(distributions)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            jsd = jensen_shannon_divergence(distributions[i], distributions[j])
            matrix[i][j] = jsd
            matrix[j][i] = jsd
    return matrix


def _mean_upper_triangle(matrix: list[list[float]]) -> float:
    n = len(matrix)
    if n < 2:
        return 0.0
    values = [matrix[i][j] for i in range(n) for j in range(i + 1, n)]
    return sum(values) / len(values) if values else 0.0


async def run_deident_test(
    *,
    provider: Provider,
    samples_per_question: int,
    concurrency: int = 10,
    suite_path: Path,
) -> DeidentTestResult:
    """Run the de-identification sensitivity test against a single provider.

    Loads a de-identification suite (see ``suites/deident_test.json``) with
    20 well-known opinion topics, each presented at 5 progressively abstracted
    levels (full brand → abstract feature description). For every level the
    provider returns a response distribution; we then compute the pairwise
    Jensen-Shannon divergence across the 5 distributions. Larger divergence
    means the provider's opinion shifts substantially as identifying
    information is stripped — a signature of brand recognition rather than
    feature-driven reasoning.

    Args:
        provider: Provider to evaluate.
        samples_per_question: Samples used to estimate each distribution.
        concurrency: Max concurrent in-flight distribution requests.
        suite_path: Path to the de-identification suite JSON.

    Returns:
        DeidentTestResult with per-topic and aggregate metrics.
    """
    with open(suite_path) as f:
        suite = json.load(f)

    items: list[dict] = suite["items"]
    if not items:
        raise ValueError(f"De-identification suite is empty: {suite_path}")

    suite_options: list[str] | None = suite.get("options")
    level_labels: list[str] = list(
        suite.get(
            "level_labels",
            [f"level_{i + 1}" for i in range(len(items[0]["levels"]))],
        )
    )
    n_levels = len(items[0]["levels"])
    for item in items:
        if len(item["levels"]) != n_levels:
            raise ValueError(
                f"Topic {item.get('key')} has {len(item['levels'])} levels; "
                f"expected {n_levels} for consistency."
            )

    sem = asyncio.Semaphore(max(1, concurrency))

    async def _query(text: str, options: list[str]) -> dict[str, float]:
        async with sem:
            dist = await provider.get_distribution(
                text, options, n_samples=samples_per_question
            )
        return dict(zip(options, dist.probabilities))

    tasks: list[asyncio.Task] = []
    item_options: list[list[str]] = []
    for item in items:
        options = list(item.get("options") or suite_options or [])
        if not options:
            raise ValueError(
                f"Topic {item.get('key')} has no options (neither item-level "
                "nor suite-level) — cannot query provider."
            )
        item_options.append(options)
        for text in item["levels"]:
            tasks.append(asyncio.create_task(_query(text, options)))

    t0 = time.monotonic()
    all_dists = await asyncio.gather(*tasks)
    elapsed = time.monotonic() - t0

    per_topic: list[DeidentTopicResult] = []
    idx = 0
    for item, options in zip(items, item_options):
        dists: list[dict[str, float]] = []
        for _ in range(n_levels):
            dists.append(all_dists[idx])
            idx += 1

        matrix = _pairwise_jsd_matrix(dists)
        mean_pairwise = _mean_upper_triangle(matrix)

        per_option_std: dict[str, float] = {}
        for option in options:
            proportions = [d.get(option, 0.0) for d in dists]
            per_option_std[option] = _std(proportions)
        mean_option_std = (
            sum(per_option_std.values()) / len(per_option_std)
            if per_option_std
            else 0.0
        )

        from synthbench.metrics import jensen_shannon_divergence

        drift = jensen_shannon_divergence(dists[0], dists[-1])

        per_topic.append(
            DeidentTopicResult(
                key=item["key"],
                topic=item.get("topic", item["key"]),
                options=options,
                level_texts=list(item["levels"]),
                level_labels=level_labels,
                level_distributions=dists,
                pairwise_jsd=[[round(x, 6) for x in row] for row in matrix],
                mean_pairwise_jsd=round(mean_pairwise, 6),
                per_option_std={k: round(v, 6) for k, v in per_option_std.items()},
                mean_option_std=round(mean_option_std, 6),
                drift_l1_to_l5=round(drift, 6),
            )
        )

    mean_pairwise_agg = (
        sum(t.mean_pairwise_jsd for t in per_topic) / len(per_topic)
        if per_topic
        else 0.0
    )
    mean_option_std_agg = (
        sum(t.mean_option_std for t in per_topic) / len(per_topic) if per_topic else 0.0
    )
    mean_drift_agg = (
        sum(t.drift_l1_to_l5 for t in per_topic) / len(per_topic) if per_topic else 0.0
    )

    return DeidentTestResult(
        provider_name=provider.name,
        n_topics=len(items),
        n_levels=n_levels,
        samples_per_question=samples_per_question,
        level_labels=level_labels,
        per_topic=per_topic,
        mean_pairwise_jsd=round(mean_pairwise_agg, 6),
        mean_option_std=round(mean_option_std_agg, 6),
        mean_drift_l1_to_l5=round(mean_drift_agg, 6),
        elapsed_seconds=elapsed,
    )


def deident_result_to_json(result: DeidentTestResult) -> dict:
    """Serialize a :class:`DeidentTestResult` to a JSON-ready dict.

    The ``aggregate.mean_pairwise_jsd`` field is the primary recognition
    score: higher values indicate the provider's opinion varies substantially
    across de-identification levels, consistent with brand-recognition-driven
    memorization rather than feature-driven reasoning.
    """
    return {
        "benchmark": "synthbench",
        "type": "contamination_deident",
        "provider": result.provider_name,
        "config": {
            "samples_per_question": result.samples_per_question,
            "n_topics": result.n_topics,
            "n_levels": result.n_levels,
            "level_labels": result.level_labels,
        },
        "aggregate": {
            "mean_pairwise_jsd": round(result.mean_pairwise_jsd, 6),
            "mean_option_std": round(result.mean_option_std, 6),
            "mean_drift_l1_to_l5": round(result.mean_drift_l1_to_l5, 6),
        },
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "per_topic": [
            {
                "key": t.key,
                "topic": t.topic,
                "options": t.options,
                "level_labels": t.level_labels,
                "level_texts": t.level_texts,
                "level_distributions": t.level_distributions,
                "pairwise_jsd": t.pairwise_jsd,
                "mean_pairwise_jsd": t.mean_pairwise_jsd,
                "per_option_std": t.per_option_std,
                "mean_option_std": t.mean_option_std,
                "drift_l1_to_l5": t.drift_l1_to_l5,
            }
            for t in result.per_topic
        ],
    }


def convergence_to_json(analysis: ConvergenceAnalysis) -> dict:
    """Serialize a convergence analysis to a JSON-compatible dict."""
    return {
        "benchmark": "synthbench",
        "type": "contamination_convergence",
        "n_models": analysis.n_models,
        "n_questions": analysis.n_questions,
        "model_names": analysis.model_names,
        "mean_contamination_risk": analysis.mean_contamination_risk,
        "high_risk_count": analysis.high_risk_count,
        "medium_risk_count": analysis.medium_risk_count,
        "low_risk_count": analysis.low_risk_count,
        "per_question": [
            {
                "key": q.key,
                "text": q.text,
                "options": q.options,
                "mean_std": q.mean_std,
                "contamination_risk": q.contamination_risk,
                "per_option_std": q.per_option_std,
                "n_models": q.n_models,
                "model_distributions": q.model_distributions,
            }
            for q in sorted(
                analysis.questions,
                key=lambda q: q.contamination_risk,
                reverse=True,
            )
        ],
    }
