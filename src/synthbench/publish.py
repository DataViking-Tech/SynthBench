"""Export leaderboard data as JSON for the Astro frontend."""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from synthbench.datasets.policy import DatasetPolicy, all_policies, policy_for
from synthbench.findings import PRODUCT_TO_RAW_DISPLAY as _PRODUCT_TO_RAW_DISPLAY
from synthbench.run_validity import is_invalid_run, run_identity

if TYPE_CHECKING:
    from synthbench.r2_upload import R2Uploader

logger = logging.getLogger(__name__)

# Tolerance for the submitted-vs-recomputed SPS divergence warning. Mirrors
# the tier-2 validator's aggregate tolerance so publish and validate agree
# on what counts as "the submitter's number doesn't reconcile".
_SPS_DIVERGENCE_WARN_TOLERANCE = 1e-2

# Private cache key attached to loaded result dicts so the recomputed view
# is derived once per run per publish pass. Never serialized: every emitted
# artifact is built from explicit field lists.
_RECOMPUTED_KEY = "_synthbench_recomputed_view"


def _effective_n(result: dict) -> int:
    """Number of evaluated questions, derived defensively.

    Prefers ``config.n_evaluated`` when it is a positive int, else falls back
    to the per-question row count. Ensemble results historically shipped
    without ``n_evaluated`` and published as ``n: 0`` — rank-1 rows "scored
    on zero questions" — so the row count is the safety net.
    """
    cfg = result.get("config") or {}
    n = cfg.get("n_evaluated")
    if isinstance(n, int) and not isinstance(n, bool) and n > 0:
        return n
    per_question = result.get("per_question")
    return len(per_question) if isinstance(per_question, list) else 0


def _recomputed_view(result: dict, source: str | None = None) -> dict:
    """Recompute every publishable score from the run's per-question rows.

    The publish pipeline never trusts submitter-supplied aggregates (P0-4):
    ranking, displayed scores, and confidence intervals all come from this
    view. Submitted ``scores`` / ``aggregate`` blocks are only consulted for
    fields that cannot be derived from ``per_question`` (``p_sub`` /
    ``p_cond``, operational metadata like token usage and latency).

    Returns ``{"scores": {...}, "aggregate": {...}, "per_metric_ci": {...}}``.
    ``per_metric_ci`` is ``{}`` when a CI cannot be computed (absence means
    unknown — consumers must never see a degraded ``[0, 0]``). When a run
    carries no usable per-question rows, all recomputed scores are absent and
    the run publishes with zeroed scores rather than the submitted claims.

    Logs a warning when the submitted ``scores.sps`` diverges from the
    recomputed value beyond tolerance; the recomputed number is published
    regardless.
    """
    cached = result.get(_RECOMPUTED_KEY)
    if isinstance(cached, dict):
        return cached

    from synthbench.recompute import bootstrap_metric_cis, recompute_aggregates

    per_question = result.get("per_question") or []
    submitted_scores = result.get("scores") or {}
    rec = recompute_aggregates(per_question, extended_scores=submitted_scores)

    if rec is None:
        view: dict = {"scores": {}, "aggregate": {}, "per_metric_ci": {}}
        result[_RECOMPUTED_KEY] = view
        return view

    scores: dict = {
        "sps": rec.sps,
        "p_dist": rec.p_dist,
        "p_rank": rec.p_rank,
    }
    if rec.p_refuse is not None:
        scores["p_refuse"] = rec.p_refuse
    # p_sub / p_cond are not derivable from per_question rows; pass through
    # the (tier-1 bounds-checked) submitted values that already entered the
    # recomputed composite via recompute_aggregates.
    for key in ("p_sub", "p_cond"):
        if key in rec.components:
            scores[key] = rec.components[key]

    aggregate = {
        "mean_jsd": rec.mean_jsd,
        "median_jsd": rec.median_jsd,
        "mean_kendall_tau": rec.mean_kendall_tau,
        "composite_parity": rec.parity_two,
        "n_questions": rec.n_questions,
    }

    submitted_sps = submitted_scores.get("sps")
    if (
        isinstance(submitted_sps, (int, float))
        and not isinstance(submitted_sps, bool)
        and abs(float(submitted_sps) - rec.sps) > _SPS_DIVERGENCE_WARN_TOLERANCE
    ):
        label = source or (result.get("config") or {}).get("provider", "<unknown>")
        logger.warning(
            "%s: submitted scores.sps=%.6f diverges from recomputed %.6f "
            "(delta=%.6f); publishing the recomputed value",
            label,
            float(submitted_sps),
            rec.sps,
            abs(float(submitted_sps) - rec.sps),
        )

    view = {
        "scores": scores,
        "aggregate": aggregate,
        "per_metric_ci": bootstrap_metric_cis(
            per_question, extended_scores=submitted_scores
        ),
    }
    result[_RECOMPUTED_KEY] = view
    return view


def _partition_valid_runs(
    loaded: list[tuple[str, dict]],
) -> tuple[list[tuple[str, dict]], list[dict]]:
    """Split ``(run_id, data)`` pairs into valid runs + excluded-run records.

    ``loaded`` comes from the publish-time JSON-load pass. An ``excluded``
    record carries the run_id, a human-readable reason, identity fields,
    and the uniformity metrics so downstream consumers (leaderboard.json
    transparency block, operator CLI) can see exactly what was filtered
    and why. See ``run_validity.is_invalid_run`` for the detection rule.
    """
    valid: list[tuple[str, dict]] = []
    excluded: list[dict] = []
    for run_id, data in loaded:
        invalid, reason, metrics = is_invalid_run(data)
        if invalid:
            excluded.append(
                {
                    "run_id": run_id,
                    "reason": reason,
                    **run_identity(data),
                    "metrics": metrics,
                }
            )
            continue
        valid.append((run_id, data))
    return valid, excluded


def _policy_to_dict(policy: DatasetPolicy) -> dict:
    """Serialize a DatasetPolicy for embedding in published JSON artifacts."""
    return {
        "redistribution_policy": policy.redistribution_policy,
        "license_url": policy.license_url,
        "citation": policy.citation,
    }


def _dedup_results(results: list[dict]) -> list[dict]:
    """De-duplicate results: keep the run with the most n_evaluated per (display_name, framework, dataset).

    Also merges demographic_breakdown data from all runs sharing the same key
    into the winning entry, since conditioned runs may have fewer n_evaluated
    but carry unique demographic data.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework

    best: dict[tuple[str, str, str], dict] = {}
    all_demographics: dict[tuple[str, str, str], dict[str, list]] = {}
    for r in results:
        cfg = r.get("config", {})
        provider = cfg.get("provider", "unknown")
        dataset = cfg.get("dataset", "unknown")
        n_eval = _effective_n(r)
        name = display_provider_name(provider)
        fw = provider_framework(provider)
        key = (name, fw, dataset)
        existing = best.get(key)
        if existing is None or n_eval > _effective_n(existing):
            best[key] = r
        # Collect demographic data from all runs
        demo = r.get("demographic_breakdown", {})
        if demo:
            merged = all_demographics.setdefault(key, {})
            for attr, groups in demo.items():
                if isinstance(groups, list) and attr not in merged:
                    merged[attr] = groups

    # Merge collected demographics into winning entries
    for key, r in best.items():
        if key in all_demographics:
            existing_demo = r.get("demographic_breakdown", {})
            if not existing_demo:
                r["demographic_breakdown"] = all_demographics[key]
            else:
                for attr, groups in all_demographics[key].items():
                    if attr not in existing_demo:
                        existing_demo[attr] = groups

    return list(best.values())


def _compute_topic_scores(per_question: list[dict]) -> dict[str, float]:
    """Compute per-topic aggregate SPS from per-question data using keyword categorization."""
    from synthbench.topics import categorize_question

    topic_parities: dict[str, list[float]] = {}
    for q in per_question:
        text = q.get("text", "")
        if not text:
            continue
        category = categorize_question(text)
        parity = q.get("parity")
        if parity is not None:
            topic_parities.setdefault(category, []).append(parity)

    topic_scores: dict[str, float] = {}
    for category, parities in sorted(topic_parities.items()):
        if parities:
            topic_scores[category] = round(sum(parities) / len(parities), 6)
    return topic_scores


def _compute_topic_metrics(per_question: list[dict]) -> dict[str, dict[str, float]]:
    """Per-topic breakdown of SPS components (p_dist, p_rank, p_refuse, sps).

    Mirrors the aggregate-level formulas in ``runner.ParityResult``:
        p_dist   = 1 - mean(JSD)
        p_rank   = (1 + mean(tau)) / 2
        p_refuse = 1 - mean(|R_model - R_human|)
        sps      = mean(parity)  (per-question composite score)

    Used by the leaderboard expansion to render full topic-score metrics
    instead of a single SPS value per topic.
    """
    from synthbench.topics import categorize_question

    buckets: dict[str, dict[str, list[float]]] = {}
    for q in per_question:
        text = q.get("text", "")
        if not text:
            continue
        category = categorize_question(text)
        bucket = buckets.setdefault(
            category, {"jsd": [], "tau": [], "refuse_diff": [], "parity": []}
        )
        parity = q.get("parity")
        if parity is not None:
            bucket["parity"].append(float(parity))
        jsd = q.get("jsd")
        if jsd is not None:
            bucket["jsd"].append(float(jsd))
        tau = q.get("kendall_tau")
        if tau is not None:
            bucket["tau"].append(float(tau))
        model_r = q.get("model_refusal_rate")
        human_r = q.get("human_refusal_rate")
        if model_r is not None and human_r is not None:
            bucket["refuse_diff"].append(abs(float(model_r) - float(human_r)))

    metrics: dict[str, dict[str, float]] = {}
    for category, b in sorted(buckets.items()):
        if not b["parity"]:
            continue
        entry: dict[str, float] = {
            "sps": round(sum(b["parity"]) / len(b["parity"]), 6),
            "n": len(b["parity"]),
        }
        if b["jsd"]:
            entry["p_dist"] = round(1.0 - sum(b["jsd"]) / len(b["jsd"]), 6)
        if b["tau"]:
            entry["p_rank"] = round((1.0 + sum(b["tau"]) / len(b["tau"])) / 2.0, 6)
        if b["refuse_diff"]:
            entry["p_refuse"] = round(
                max(0.0, 1.0 - sum(b["refuse_diff"]) / len(b["refuse_diff"])), 6
            )
        metrics[category] = entry
    return metrics


_COST_FIELD_KEYS = (
    "cost_usd",
    "cost_per_100q",
    "cost_per_sps_point",
    "cost_per_response",
    "tokens_per_response",
    "is_cost_estimated",
)

_NULL_COST_FIELDS: dict = {k: None for k in _COST_FIELD_KEYS}

_LATENCY_FIELD_KEYS = ("latency_p50_seconds", "latency_p95_seconds")
_NULL_LATENCY_FIELDS: dict = {k: None for k in _LATENCY_FIELD_KEYS}


def _compute_latency_fields(aggregate: dict) -> dict:
    """Derive latency_p50_seconds / latency_p95_seconds from the run aggregate.

    The runner records per-question latency and report.py rolls it up into
    ``aggregate.latency_seconds = {p50, p95, mean, n, source}`` (sb-293).
    Pre-instrumentation rows (no ``latency_seconds`` block) get nulls so the
    leaderboard renders ``"—"`` instead of misleading zeros.
    """
    block = (aggregate or {}).get("latency_seconds")
    if not isinstance(block, dict):
        return dict(_NULL_LATENCY_FIELDS)
    p50 = block.get("p50")
    p95 = block.get("p95")
    return {
        "latency_p50_seconds": round(float(p50), 4) if p50 is not None else None,
        "latency_p95_seconds": round(float(p95), 4) if p95 is not None else None,
    }


def _compute_cost_fields(aggregate: dict, config: dict, entry: dict) -> dict:
    """Derive cost_usd, cost_per_100q, cost_per_sps_point, is_cost_estimated.

    Returns a dict with all four keys; values are ``None`` whenever token usage
    or pricing is unavailable. ``cost_per_sps_point`` is also ``None`` when SPS
    is below 0.01 (avoid divide-by-near-zero amplification).

    Self-hosted (``ollama/*``) and unknown-provider rows produce nulls.
    Rows whose token_usage records zero tokens emit ``$0.00`` even when the
    provider has no priced equivalent (baselines): zero × any rate is zero,
    so we report measured-zero rather than missing-data.
    """
    token_usage = (aggregate or {}).get("token_usage")
    if not isinstance(token_usage, dict):
        return dict(_NULL_COST_FIELDS)

    input_tokens = int(token_usage.get("input_tokens") or 0)
    output_tokens = int(token_usage.get("output_tokens") or 0)
    call_count = int(token_usage.get("call_count") or 0)

    n = entry.get("n") or aggregate.get("n_questions") or 0
    sps = entry.get("sps") or 0

    if input_tokens == 0 and output_tokens == 0:
        cost_usd = 0.0
    else:
        provider = (config or {}).get("provider")
        if not provider:
            return dict(_NULL_COST_FIELDS)
        try:
            from synth_panel.cost import lookup_pricing_by_provider
        except ImportError:
            return dict(_NULL_COST_FIELDS)
        pricing, _is_estimated = lookup_pricing_by_provider(provider)
        if pricing is None:
            return dict(_NULL_COST_FIELDS)
        cost_usd = (
            input_tokens * pricing.input_cost_per_million
            + output_tokens * pricing.output_cost_per_million
        ) / 1_000_000

    cost_per_100q = (cost_usd / n * 100) if n > 0 else None
    cost_per_sps_point = (cost_usd / sps) if sps >= 0.01 else None
    # "Response" here is one API call to the underlying model. For native
    # distribution providers (1 call → distribution over options) that's 1
    # response per question; for sampling providers it's samples_per_question.
    # call_count is the canonical denominator because it absorbs both shapes.
    cost_per_response = (cost_usd / call_count) if call_count > 0 else None
    tokens_per_response = (
        (input_tokens + output_tokens) / call_count if call_count > 0 else None
    )

    return {
        "cost_usd": round(cost_usd, 6),
        "cost_per_100q": round(cost_per_100q, 6) if cost_per_100q is not None else None,
        "cost_per_sps_point": (
            round(cost_per_sps_point, 6) if cost_per_sps_point is not None else None
        ),
        "cost_per_response": (
            round(cost_per_response, 6) if cost_per_response is not None else None
        ),
        "tokens_per_response": (
            round(tokens_per_response, 2) if tokens_per_response is not None else None
        ),
        "is_cost_estimated": False,
    }


def _compute_ensemble_cost(
    config: dict,
    results_by_provider_ds: dict[tuple[str, str], dict],
) -> float | None:
    """Sum cost_usd across constituent runs listed in ``config.ensemble_sources``.

    Returns ``None`` if any constituent has no token_usage or unresolved pricing.
    """
    sources = (config or {}).get("ensemble_sources")
    if not sources:
        return None

    try:
        from synth_panel.cost import lookup_pricing_by_provider
    except ImportError:
        return None

    dataset = (config or {}).get("dataset", "unknown")
    total = 0.0
    for src in sources:
        provider = src.get("provider")
        if not provider:
            return None
        constituent = results_by_provider_ds.get((provider, dataset))
        if constituent is None:
            return None
        usage = constituent.get("aggregate", {}).get("token_usage")
        if not isinstance(usage, dict):
            return None
        pricing, _ = lookup_pricing_by_provider(provider)
        if pricing is None:
            return None
        in_tok = int(usage.get("input_tokens") or 0)
        out_tok = int(usage.get("output_tokens") or 0)
        total += (
            in_tok * pricing.input_cost_per_million
            + out_tok * pricing.output_cost_per_million
        ) / 1_000_000
    return round(total, 6)


def _build_pricing_snapshot() -> dict:
    """Emit the rates table used for this publish run.

    Reads the named pricing constants from ``synth_panel.cost`` plus the
    ``# pricing snapshot_date: YYYY-MM-DD`` anchor comment, and stamps the
    installed synthpanel version. Designed to be lossless under ``json.dump``.
    """
    rates: dict[str, dict] = {}
    snapshot_date: str | None = None
    synth_panel_version: str | None = None

    try:
        from synth_panel import cost as _spc
    except ImportError:
        _spc = None  # type: ignore[assignment]

    if _spc is not None:
        named_constants = (
            ("haiku", "HAIKU_PRICING"),
            ("sonnet", "SONNET_PRICING"),
            ("opus", "OPUS_PRICING"),
            ("gemini-2.5-pro", "GEMINI_PRO_PRICING"),
            ("gemini-flash", "GEMINI_FLASH_PRICING"),
        )
        for label, attr in named_constants:
            pricing = getattr(_spc, attr, None)
            if pricing is None:
                continue
            rates[label] = {
                "input_cost_per_million": pricing.input_cost_per_million,
                "output_cost_per_million": pricing.output_cost_per_million,
                "cache_creation_cost_per_million": pricing.cache_creation_cost_per_million,
                "cache_read_cost_per_million": pricing.cache_read_cost_per_million,
            }

        try:
            import inspect

            source = inspect.getsource(_spc)
            m = re.search(r"pricing snapshot_date:\s*(\d{4}-\d{2}-\d{2})", source)
            if m:
                snapshot_date = m.group(1)
        except (OSError, TypeError):
            snapshot_date = None

    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            synth_panel_version = version("synthpanel")
        except PackageNotFoundError:
            synth_panel_version = None
    except ImportError:
        synth_panel_version = None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synth_panel_version": synth_panel_version,
        "snapshot_date": snapshot_date,
        "rates": rates,
    }


# Human-readable labels for SubPOP demographic attribute codes. Fallback for
# unknown codes is title-casing the raw attribute so new dimensions degrade
# gracefully instead of erroring or hiding data.
_DEMOGRAPHIC_DIMENSION_LABELS: dict[str, str] = {
    "AGE": "Age",
    "CREGION": "Geography (US Census region)",
    "EDUCATION": "Education",
    "SEX": "Sex",
    "RACE": "Race / ethnicity",
    "INCOME": "Income",
    "POLPARTY": "Political party",
    "POLIDEOLOGY": "Political ideology",
    "RELIG": "Religion",
    "RELIGATTEND": "Religious attendance",
    "CITIZEN": "Citizenship",
    "MARITAL": "Marital status",
}


def _demographic_dimension_label(attribute: str) -> str:
    return _DEMOGRAPHIC_DIMENSION_LABELS.get(
        attribute, attribute.replace("_", " ").title()
    )


def _build_demographic_scorecard(r: dict) -> dict | None:
    """Build the structured ``demographic_scorecard`` block for one entry.

    Groups the run's ``demographic_breakdown`` (SubPOP conditioned runs) by
    attribute and exposes, per subgroup: the score (subgroup ``p_dist``),
    a CI when computable, the question count, and the source dataset.

    Returns ``None`` when the run carries no demographic breakdown — the
    entry publishes ``"demographic_scorecard": null`` so API consumers can
    distinguish "not measured" from "field not supported" (issue #255).

    CI note: today's ``demographic_breakdown`` blocks carry only point
    estimates (no per-question subgroup rows), so ``ci_lower`` /
    ``ci_upper`` are ``null``. The keys are emitted anyway so the shape is
    stable once subgroup-level bootstrap CIs land; consumers must treat
    ``null`` as unknown, never zero.
    """
    demo_breakdown = r.get("demographic_breakdown") or {}
    if not isinstance(demo_breakdown, dict):
        return None

    dataset = (r.get("config") or {}).get("dataset", "unknown")
    dimensions: list[dict] = []
    for attr in sorted(demo_breakdown):
        groups = demo_breakdown[attr]
        if not isinstance(groups, list) or not groups:
            continue
        rows: list[dict] = []
        for g in groups:
            if not isinstance(g, dict):
                continue
            score = g.get("p_dist")
            if score is None:
                continue
            row: dict = {
                "group": g.get("group", ""),
                "score": round(float(score), 6),
                "ci_lower": None,
                "ci_upper": None,
                "n": g.get("n_questions", 0),
            }
            p_cond = g.get("p_cond")
            if p_cond is not None:
                row["p_cond"] = round(float(p_cond), 6)
            rows.append(row)
        if rows:
            dimensions.append(
                {
                    "attribute": attr,
                    "label": _demographic_dimension_label(attr),
                    "groups": rows,
                }
            )

    if not dimensions:
        return None
    return {"dataset": dataset, "dimensions": dimensions}


def _build_entry(
    r: dict,
    rank: int,
    results_by_provider_ds: dict[tuple[str, str], dict] | None = None,
) -> dict:
    """Build a leaderboard entry from a result dict."""
    from synthbench.config_id import build_config_id, runnable_ids
    from synthbench.leaderboard import display_provider_name, provider_framework

    cfg = r.get("config", {})
    provider_raw = cfg.get("provider", "unknown")
    provider_name = display_provider_name(provider_raw)
    framework = provider_framework(provider_raw)
    provider_id, model_id = runnable_ids(provider_raw)
    # Never trust submitter-supplied aggregates (P0-4): every score below is
    # recomputed from the per-question rows. The submitted `aggregate` block
    # is only read for operational metadata (token usage, latency).
    view = _recomputed_view(r)
    scores = view["scores"]
    rec_agg = view["aggregate"]
    agg = r.get("aggregate", {})

    is_baseline = framework == "baseline"
    is_ensemble = "ensemble" in provider_raw.lower()

    tpl_stem = _tpl_name(cfg.get("prompt_template"))
    config_id, _ = build_config_id(
        provider_raw,
        dataset=cfg.get("dataset", "unknown"),
        temperature=cfg.get("temperature"),
        template=tpl_stem,
        samples_per_question=cfg.get("samples_per_question"),
        question_set_hash=cfg.get("question_set_hash"),
    )

    # CI on SPS, recomputed at publish time: resample questions, recompute
    # the full composite per resample (P2-4 fix — the stored per_metric_ci
    # of legacy files is the CI of the 2-metric parity, a different metric).
    # None (JSON null) when unavailable: absence means unknown, never [0, 0].
    sps_ci = view["per_metric_ci"].get("sps")
    ci_lower = sps_ci[0] if sps_ci else None
    ci_upper = sps_ci[1] if sps_ci else None

    entry: dict = {
        "rank": rank,
        "config_id": config_id,
        "provider": provider_name,
        "model": provider_name,
        # Runnable IDs (sb-7ly): machine-parseable counterparts to the display
        # labels above. provider_id = framework/runner; model_id = OpenRouter-
        # runnable <vendor>/<model> slug so consumers can pipe to the gateway
        # without parsing display names. See config_id.runnable_ids.
        "provider_id": provider_id,
        "model_id": model_id,
        "dataset": cfg.get("dataset", "unknown"),
        "framework": framework,
        "sps": round(scores.get("sps", 0), 6),
        "p_dist": round(scores.get("p_dist", 0), 6),
        "p_rank": round(scores.get("p_rank", 0), 6),
        "p_refuse": round(scores.get("p_refuse", 0), 6),
        "jsd": round(rec_agg.get("mean_jsd", 0), 6),
        "tau": round(rec_agg.get("mean_kendall_tau", 0), 6),
        "n": _effective_n(r),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "is_baseline": is_baseline,
        "is_ensemble": is_ensemble,
    }

    # Optional sub-metrics (conditioned runs only)
    p_cond = scores.get("p_cond")
    if p_cond is not None and p_cond > 0:
        entry["p_cond"] = round(p_cond, 6)
    p_sub = scores.get("p_sub")
    if p_sub is not None:
        entry["p_sub"] = round(p_sub, 6)

    # Run metadata
    spq = cfg.get("samples_per_question")
    if spq is not None:
        entry["samples_per_question"] = spq
    temp = cfg.get("temperature")
    if temp is not None:
        entry["temperature"] = temp
    tpl = cfg.get("prompt_template")
    if tpl:
        entry["template"] = Path(tpl).stem

    # Topic scores from per-question keyword categorization
    per_question = r.get("per_question", [])
    if per_question:
        topic_scores = _compute_topic_scores(per_question)
        if topic_scores:
            entry["topic_scores"] = topic_scores
        topic_metrics = _compute_topic_metrics(per_question)
        if topic_metrics:
            entry["topic_metrics"] = topic_metrics

    # Demographic scores (real SubPOP data)
    demo_breakdown = r.get("demographic_breakdown", {})
    if demo_breakdown:
        flat_demographics: list[dict] = []
        for _attr, groups in demo_breakdown.items():
            if isinstance(groups, list):
                for g in groups:
                    flat_demographics.append(
                        {
                            "attribute": g.get("attribute", ""),
                            "group": g.get("group", ""),
                            "p_dist": round(g.get("p_dist", 0), 6),
                            "p_cond": round(g.get("p_cond", 0), 6),
                            "n_questions": g.get("n_questions", 0),
                        }
                    )
        if flat_demographics:
            entry["demographic_scores"] = flat_demographics

    # Structured per-dimension scorecard (issue #255). Explicit null (never
    # absent) so API consumers can rely on the key: null = this entry has no
    # demographic-conditioned runs, object = at least one dimension measured.
    entry["demographic_scorecard"] = _build_demographic_scorecard(r)

    cost_fields = _compute_cost_fields(agg, cfg, entry)
    if is_ensemble:
        ens_cost = _compute_ensemble_cost(cfg, results_by_provider_ds or {})
        if ens_cost is None:
            cost_fields = dict(_NULL_COST_FIELDS)
        else:
            n = entry.get("n") or 0
            sps = entry.get("sps") or 0
            # Ensembles don't have a single token_usage block, so per-response
            # cost/tokens stay null — they have no single underlying response.
            cost_fields = {
                "cost_usd": round(ens_cost, 6),
                "cost_per_100q": round(ens_cost / n * 100, 6) if n > 0 else None,
                "cost_per_sps_point": round(ens_cost / sps, 6) if sps >= 0.01 else None,
                "cost_per_response": None,
                "tokens_per_response": None,
                "is_cost_estimated": False,
            }
    entry.update(cost_fields)
    entry.update(_compute_latency_fields(agg))

    # Private-holdout verification fields: sps_public / sps_private /
    # delta + a "verified" | "flagged" badge computed off the delta vs. the
    # divergence threshold. Only surfaced for holdout-enabled datasets; on
    # others the keys stay absent so the site renders nothing.
    from synthbench.private_holdout import compute_split_sps, is_holdout_enabled

    dataset_name = cfg.get("dataset", "unknown")
    if per_question and is_holdout_enabled(dataset_name):
        split = compute_split_sps(dataset_name, per_question)
        sps_public = split.get("sps_public")
        sps_private = split.get("sps_private")
        delta = split.get("delta")
        if sps_public is not None:
            entry["sps_public"] = round(float(sps_public), 6)
        if sps_private is not None:
            entry["sps_private"] = round(float(sps_private), 6)
        if delta is not None:
            entry["sps_public_private_delta"] = round(float(delta), 6)
        if sps_public is not None and sps_private is not None:
            entry["verification_badge"] = (
                "flagged" if split.get("flagged") else "verified"
            )

    return entry


def _build_findings(results: list[dict], excluded_runs: list[dict]) -> dict:
    """Compute the findings block from the loaded run pool (#309).

    Delegates to :mod:`synthbench.findings` — every number is derived from
    the recomputed per-question rows of the valid runs, with non-derivable
    numbers carried as documented asserted constants. ``excluded_runs`` are
    the validity-filtered records so ensemble caveats can flag blends built
    on excluded constituents.
    """
    from synthbench.findings import build_findings

    return build_findings(results, {e["run_id"] for e in excluded_runs})


def _load_opinionsqa_human_distributions() -> list[dict]:
    """Load human distributions for all OpinionsQA questions (all waves).

    Used for temporal drift computation: groups by question stem across
    waves, so we need every wave's cached distribution — not just the
    subsets evaluated by models.

    Returns an empty list if the cache is unavailable.
    """
    from synthbench.datasets.opinionsqa import OpinionsQADataset, wave_year

    try:
        ds = OpinionsQADataset()
        questions = ds.load()
    except Exception:
        return []

    out = []
    for q in questions:
        year = wave_year(q.survey) if q.survey else 0
        out.append(
            {
                "key": q.key,
                "human_distribution": q.human_distribution,
                "temporal_year": year,
                "survey": q.survey,
            }
        )
    return out


def _build_baselines(results: list[dict], datasets: list[str]) -> dict:
    """Compute Human Ceiling (per dataset) and Temporal Drift (OpinionsQA).

    Best-effort: if raw data is not available on disk, the corresponding
    ceiling entry is omitted rather than failing the publish step.
    """
    from synthbench.baselines import (
        compute_globalopinionqa_ceiling,
        compute_opinionsqa_ceiling,
        compute_opinionsqa_subgroup_ceilings,
        compute_subpop_ceiling,
        compute_temporal_drift,
    )

    out: dict = {
        "ceiling": {},
        "temporal_drift": None,
        "citations": [
            {
                "key": "santurkar2023",
                "text": "Santurkar et al. 2023, OpinionsQA.",
                "arxiv": "2303.17548",
            },
            {
                "key": "durmus2023",
                "text": "Durmus et al. 2023, GlobalOpinionQA.",
                "arxiv": "2306.16388",
            },
            {
                "key": "suh2025",
                "text": "Suh et al. 2025, SubPOP.",
                "arxiv": "2502.16761",
            },
            {
                "key": "pew_methods",
                "text": "Pew Research Center, Survey Methodology 101.",
            },
            {
                "key": "spearman1910",
                "text": "Spearman, C. (1910); Brown, W. (1910). Spearman-Brown prophecy formula.",
            },
            {"key": "efron1979", "text": "Efron, B. (1979). Bootstrap methods."},
            {
                "key": "lin1991",
                "text": "Lin, J. (1991). Jensen-Shannon divergence properties.",
            },
            {
                "key": "cochran1977",
                "text": "Cochran, W. (1977). Sampling Techniques (n=400 rule-of-thumb).",
            },
        ],
        "survey_weight_caveat": (
            "Ceiling computed from raw category counts; ignoring survey "
            "weights could shift the ceiling by 1-3% on demographically "
            "skewed subgroups."
        ),
    }

    if "opinionsqa" in datasets:
        # B=1000 published across all ceiling wrappers. The vectorized
        # multinomial + JSD path in compute_ceiling makes this feasible at
        # publish time (sb-dkz); earlier Finding-A B=200 tradeoff retired.
        oqa = compute_opinionsqa_ceiling(n_bootstrap=1000)
        if oqa is not None:
            sub = compute_opinionsqa_subgroup_ceilings(n_bootstrap=1000)
            if sub is not None:
                oqa["per_subgroup"] = sub
            out["ceiling"]["opinionsqa"] = oqa

        # Temporal drift floor (OpinionsQA only) — computed from the full
        # dataset so coverage reflects all waves, not just evaluated subsets.
        human_qs = _load_opinionsqa_human_distributions()
        if human_qs:
            out["temporal_drift"] = compute_temporal_drift(human_qs)

    if "subpop" in datasets:
        sp = compute_subpop_ceiling()
        if sp is not None:
            out["ceiling"]["subpop"] = sp

    if "globalopinionqa" in datasets:
        goqa = compute_globalopinionqa_ceiling()
        if goqa is not None:
            out["ceiling"]["globalopinionqa"] = goqa

    return out


# Display-name map for product->raw rows lives in synthbench.findings
# (shared with the findings block computation); imported at module top as
# _PRODUCT_TO_RAW_DISPLAY for _annotate_normalized_sps below.


def _annotate_normalized_sps(entries: list[dict], baselines: dict) -> None:
    """Add normalized_sps = (SPS - P_unconditioned) / (P_ceiling - P_unconditioned).

    P_unconditioned is the raw-LLM baseline SPS for the same underlying model on
    the same dataset (the "just prompt the model" reference). Raw-LLM rows use
    their own SPS, yielding normalized_sps == 0. Product rows look up their
    underlying raw model via _PRODUCT_TO_RAW_DISPLAY. Baseline rows and rows
    without a resolvable reference are left without the field, so the frontend
    can fall back to the raw SPS for display.

    P_ceiling comes from baselines.ceiling[dataset].overall.mean. If no ceiling
    is present for a dataset (e.g., ceiling computation was skipped), no entry
    for that dataset receives normalized_sps.

    Values are clamped to [0, 1.05] — a small margin above the ceiling keeps
    the (rare) case where SPS exceeds the bootstrap mean from producing a
    confusing 120% display.
    """
    ceilings: dict[str, float] = {}
    for ds, block in (baselines.get("ceiling") or {}).items():
        overall = (block or {}).get("overall") or {}
        mean = overall.get("mean")
        if isinstance(mean, (int, float)):
            ceilings[ds] = float(mean)

    raw_sps_lookup: dict[tuple[str, str], float] = {}
    for e in entries:
        if e.get("framework") != "raw":
            continue
        sps = e.get("sps")
        if not isinstance(sps, (int, float)) or sps <= 0:
            continue
        raw_sps_lookup[(e.get("dataset"), e.get("model"))] = float(sps)

    for e in entries:
        ds = e.get("dataset")
        sps = e.get("sps")
        if ds not in ceilings or not isinstance(sps, (int, float)):
            continue
        fw = e.get("framework")
        model = e.get("model")
        if fw == "raw":
            p_unc: float | None = raw_sps_lookup.get((ds, model))
        elif fw == "product":
            raw_model = _PRODUCT_TO_RAW_DISPLAY.get(model)
            p_unc = raw_sps_lookup.get((ds, raw_model)) if raw_model else None
        else:
            p_unc = None
        if p_unc is None:
            continue
        p_ceiling = ceilings[ds]
        denom = p_ceiling - p_unc
        if denom <= 0:
            continue
        normalized = (float(sps) - p_unc) / denom
        # Clamp to avoid visually confusing negative or very-out-of-range values
        # while still surfacing entries that edge past the ceiling.
        normalized = max(0.0, min(1.05, normalized))
        e["normalized_sps"] = round(normalized, 6)


def _compute_cross_provider_concordance(deduped: list[dict]) -> dict[str, dict]:
    """Per-dataset cross-provider JSD matrix between raw-LLM model runs.

    Operationalizes HBR Romasanta/Thomas/Levina (2026) "trendslop": cross-model
    consensus without ground truth. Low off-diagonal cells = providers agree
    with each other (potentially on shared error modes). High off-diagonal =
    providers genuinely diverge.

    For each dataset, build ``M[i][j] = mean JSD(dist_i(q), dist_j(q))`` over
    the set of questions both models answered. Matrix is symmetric with a zero
    diagonal. Pairs with no shared questions emit ``None``. Only raw-framework
    runs are included — products and baselines conflate architecture with
    prompting, which muddies the cross-model interpretation.

    Also emits the 1-D summary pair used for the concordance-vs-correctness
    quadrant view: ``mean_cross_model_jsd`` (mean of the off-diagonal) and
    ``mean_human_jsd`` (mean across models of their per-run mean_jsd vs human).
    """
    from synthbench.leaderboard import display_provider_name, provider_framework
    from synthbench.metrics.distributional import jensen_shannon_divergence

    # dataset -> model_display -> {question_key: model_distribution}
    by_dataset: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    # dataset -> model_display -> aggregate mean_jsd vs human
    human_jsd_by_dataset: dict[str, dict[str, float]] = {}

    for r in deduped:
        cfg = r.get("config", {})
        provider_raw = cfg.get("provider", "")
        if not provider_raw:
            continue
        if provider_framework(provider_raw) != "raw":
            continue
        dataset = cfg.get("dataset", "unknown")
        display = display_provider_name(provider_raw)

        q_map = by_dataset.setdefault(dataset, {}).setdefault(display, {})
        for q in r.get("per_question", []):
            key = q.get("key")
            dist = q.get("model_distribution")
            if key and isinstance(dist, dict) and dist:
                q_map[key] = dist

        mean_jsd = r.get("aggregate", {}).get("mean_jsd")
        if isinstance(mean_jsd, (int, float)):
            human_jsd_by_dataset.setdefault(dataset, {})[display] = float(mean_jsd)

    out: dict[str, dict] = {}
    for dataset, model_map in by_dataset.items():
        models = sorted(model_map.keys())
        if len(models) < 2:
            continue
        n = len(models)
        matrix: list[list[float | None]] = [[0.0] * n for _ in range(n)]
        off_diag_vals: list[float] = []

        for i in range(n):
            for j in range(i + 1, n):
                dists_i = model_map[models[i]]
                dists_j = model_map[models[j]]
                shared = set(dists_i) & set(dists_j)
                if not shared:
                    matrix[i][j] = None
                    matrix[j][i] = None
                    continue
                jsd_sum = 0.0
                for k in shared:
                    jsd_sum += jensen_shannon_divergence(dists_i[k], dists_j[k])
                mean_pair = round(jsd_sum / len(shared), 6)
                matrix[i][j] = mean_pair
                matrix[j][i] = mean_pair
                off_diag_vals.append(mean_pair)

        mean_cross = (
            round(sum(off_diag_vals) / len(off_diag_vals), 6) if off_diag_vals else None
        )
        human_vals = [
            human_jsd_by_dataset.get(dataset, {})[m]
            for m in models
            if m in human_jsd_by_dataset.get(dataset, {})
        ]
        mean_human = round(sum(human_vals) / len(human_vals), 6) if human_vals else None

        out[dataset] = {
            "models": models,
            "matrix": matrix,
            "mean_cross_model_jsd": mean_cross,
            "mean_human_jsd": mean_human,
        }

    return out


def _annotate_run_counts(entries: list[dict], all_results: list[dict]) -> None:
    """Add ``run_count`` and ``dataset_coverage_count`` to leaderboard entries.

    ``run_count`` is the number of raw result files whose config matches this
    entry's (model, framework, dataset, temperature, template) tuple — i.e.
    replicates aggregated into the winning row.

    ``dataset_coverage_count`` is the number of distinct datasets this entry's
    (model, framework, temperature, template) config has runs on. Together
    these let the site's default view hide under-replicated configs without
    re-grouping in JS.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework

    run_counts: dict[tuple, int] = {}
    datasets_per_config: dict[tuple, set[str]] = {}

    for r in all_results:
        cfg = r.get("config", {})
        provider_raw = cfg.get("provider", "unknown")
        name = display_provider_name(provider_raw)
        fw = provider_framework(provider_raw)
        dataset = cfg.get("dataset", "unknown")
        temp = cfg.get("temperature")
        tpl_stem = _tpl_name(cfg.get("prompt_template"))

        run_key = (name, fw, dataset, temp, tpl_stem)
        run_counts[run_key] = run_counts.get(run_key, 0) + 1
        cov_key = (name, fw, temp, tpl_stem)
        datasets_per_config.setdefault(cov_key, set()).add(dataset)

    for e in entries:
        run_key = (
            e.get("model"),
            e.get("framework"),
            e.get("dataset"),
            e.get("temperature"),
            e.get("template"),
        )
        cov_key = (
            e.get("model"),
            e.get("framework"),
            e.get("temperature"),
            e.get("template"),
        )
        e["run_count"] = run_counts.get(run_key, 0)
        e["dataset_coverage_count"] = len(datasets_per_config.get(cov_key, set()))


def publish_leaderboard_data(
    results_dir: Path, output_path: Path, version: str = "0.1.0"
) -> Path:
    """Export leaderboard data as JSON for the Astro frontend.

    Reads all result JSON files from results_dir, deduplicates and ranks them,
    then writes a single JSON file conforming to the SynthBenchData TypeScript
    interface.

    Returns the path to the generated JSON file.
    """
    json_files = sorted(results_dir.glob("*.json"))
    loaded: list[tuple[str, dict]] = []
    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
            if data.get("benchmark") == "synthbench":
                loaded.append((_run_id_from_path(jf), data))
        except (json.JSONDecodeError, KeyError):
            continue

    if not loaded:
        raise ValueError(f"No valid SynthBench result files found in {results_dir}")

    valid_pairs, excluded_runs = _partition_valid_runs(loaded)
    results = [data for _, data in valid_pairs]

    if not results:
        raise ValueError(
            f"All {len(loaded)} result files in {results_dir} were filtered as "
            f"invalid runs (uniform-distribution garbage). Refusing to emit "
            f"an empty leaderboard."
        )

    # Recompute all scores up front (P0-4): warms the per-run cache with the
    # run_id attached so submitted-vs-recomputed SPS divergence warnings name
    # the offending file, and guarantees ranking below uses recomputed values.
    for run_id, data in valid_pairs:
        _recomputed_view(data, source=run_id)

    deduped = _dedup_results(results)

    # Index by (provider_string, dataset) so ensemble cost can resolve its
    # constituent runs. Built off the deduped pool — ensemble_sources reference
    # canonical provider strings (e.g., "synthpanel/claude-haiku-4-5-...") that
    # match the constituent runs surviving dedup.
    results_by_provider_ds: dict[tuple[str, str], dict] = {}
    for r in deduped:
        cfg_r = r.get("config", {})
        key = (cfg_r.get("provider", ""), cfg_r.get("dataset", "unknown"))
        results_by_provider_ds[key] = r

    # Collect all datasets
    datasets_set: set[str] = set()
    for r in deduped:
        ds = r.get("config", {}).get("dataset", "unknown")
        datasets_set.add(ds)
    datasets = sorted(datasets_set)

    # Build ranked entries per dataset
    entries = []
    for ds in datasets:
        ds_results = [
            r for r in deduped if r.get("config", {}).get("dataset", "unknown") == ds
        ]
        # Rank by the RECOMPUTED SPS — submitted aggregates are ignored
        # entirely (P0-4: a hand-edited scores.sps must not buy a rank).
        ds_results.sort(
            key=lambda r: _recomputed_view(r)["scores"].get("sps", 0.0),
            reverse=True,
        )
        for rank, r in enumerate(ds_results, 1):
            entries.append(_build_entry(r, rank, results_by_provider_ds))

    # Build convergence data
    from synthbench.leaderboard import build_convergence_data

    convergence_raw = build_convergence_data(results)
    convergence: list[dict] = []
    for provider, sweeps in convergence_raw.items():
        for sweep in sweeps:
            for sps_val in sweep.get("runs", []):
                convergence.append(
                    {
                        "model": provider,
                        "dataset": "opinionsqa",
                        "rep_count": sweep.get("samples", 0),
                        "sps": sps_val,
                    }
                )

    baselines = _build_baselines(results, datasets)
    _annotate_normalized_sps(entries, baselines)
    _annotate_run_counts(entries, results)

    cross_provider_concordance = _compute_cross_provider_concordance(deduped)

    synthbench_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthbench_version": version,
        "datasets": datasets,
        "entries": entries,
        "convergence": convergence,
        "findings": _build_findings(results, excluded_runs),
        "baselines": baselines,
        "cross_provider_concordance": cross_provider_concordance,
        "pricing_snapshot": _build_pricing_snapshot(),
        "dataset_policies": [
            {
                "name": p.name,
                **_policy_to_dict(p),
            }
            for p in all_policies()
        ],
        "excluded_runs": excluded_runs,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(synthbench_data, f, indent=2)
        f.write("\n")
    return output_path


# ---------------------------------------------------------------------------
# Run explorer artifacts (Slice 8.1 — runs-index + per-config + per-run)
# ---------------------------------------------------------------------------


def _round_or_none(value: float | int | None, places: int = 6) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, places)


def _safe_mean(values: list[float]) -> float | None:
    nums = [float(v) for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def _safe_stddev(values: list[float]) -> float | None:
    nums = [float(v) for v in values if v is not None]
    n = len(nums)
    if n < 2:
        return 0.0 if n == 1 else None
    mean = sum(nums) / n
    variance = sum((x - mean) ** 2 for x in nums) / (n - 1)
    return math.sqrt(variance)


def _tpl_name(raw: str | None) -> str | None:
    if not raw:
        return None
    return Path(raw).stem if ("/" in raw or raw.endswith(".md")) else raw


def _parse_run_timestamp(stem: str, fallback: str | None = None) -> str | None:
    """Extract a YYYY-MM-DDTHH:MM:SSZ timestamp from a run_id stem.

    Run files end in ``_YYYYMMDD_HHMMSS``. Falls back to the result's own
    ``timestamp`` field when the stem cannot be parsed.
    """
    m = re.search(r"_(\d{8})_(\d{6})$", stem)
    if m:
        d, t = m.group(1), m.group(2)
        return f"{d[0:4]}-{d[4:6]}-{d[6:8]}T{t[0:2]}:{t[2:4]}:{t[4:6]}Z"
    return fallback


def _run_id_from_path(path: Path) -> str:
    """Raw filename stem — stable and filesystem-greppable."""
    return path.stem


def _augment_per_question(
    per_question: list[dict],
    policy: DatasetPolicy | None = None,
    dataset: str | None = None,
) -> list[dict]:
    """Return per-question rows with a lightweight ``topic`` label attached.

    If ``policy`` restricts redistribution of per-question human data, the
    ``human_distribution`` and ``human_refusal_rate`` fields are stripped
    before emission. Aggregate metrics (jsd, kendall_tau, parity) stay — they
    are derived, not raw upstream data.

    On holdout-enabled datasets, the private split also has its
    ``human_distribution`` / ``human_refusal_rate`` suppressed regardless of
    redistribution policy: the point of the private set is that the public
    JSON can't be used to reverse-engineer the answer key. Rows get an
    ``is_holdout`` flag so the site can badge them as private.
    """
    from synthbench.private_holdout import is_holdout_enabled, is_private_holdout
    from synthbench.topics import categorize_question

    suppress_human_by_policy = bool(policy and policy.suppress_human_distribution)
    holdout_enabled = bool(dataset) and is_holdout_enabled(dataset)

    out: list[dict] = []
    for q in per_question:
        text = q.get("text", "")
        topic = categorize_question(text) if text else None
        row = dict(q)
        if topic:
            row["topic"] = topic

        is_holdout = False
        if holdout_enabled:
            key = row.get("key")
            if isinstance(key, str) and is_private_holdout(dataset or "", key):
                is_holdout = True
                row["is_holdout"] = True

        if suppress_human_by_policy or is_holdout:
            row.pop("human_distribution", None)
            row.pop("human_refusal_rate", None)
        out.append(row)
    return out


_QUESTION_TEXT_REGISTRY_CACHE: dict[Path, dict[str, dict[str, str]]] = {}


def _load_question_text_registry(repo_root: Path) -> dict[str, dict[str, str]]:
    """Load ``{dataset: {key: full_text}}`` from ``data/question-text-registries``.

    The registries are small JSON fixtures committed under the repo root. They
    carry the full question text for every ``(dataset, key)`` pair and exist to
    rehydrate the per-question ``text`` field in historical
    ``leaderboard-results/*.json`` files. Those files were written before the
    report-writer stopped slicing question text at 120 chars (sb-5o1 /
    PR #115), so roughly half the rows stored on disk end mid-word. Because the
    benchmark runs themselves are expensive, we repair the data at publish time
    from these fixtures instead of re-running every benchmark.

    Returns an empty dict when the registry directory is missing so callers
    degrade gracefully back to the (potentially truncated) text in the source
    JSON.
    """
    cached = _QUESTION_TEXT_REGISTRY_CACHE.get(repo_root)
    if cached is not None:
        return cached
    registry_dir = repo_root / "data" / "question-text-registries"
    out: dict[str, dict[str, str]] = {}
    if not registry_dir.exists():
        _QUESTION_TEXT_REGISTRY_CACHE[repo_root] = out
        return out
    for path in sorted(registry_dir.glob("*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        dataset = data.get("dataset") or path.stem
        questions = data.get("questions") or {}
        if isinstance(questions, dict):
            out[dataset] = {str(k): str(v) for k, v in questions.items() if v}
    _QUESTION_TEXT_REGISTRY_CACHE[repo_root] = out
    return out


def _rehydrate_question_text(result: dict, registry: dict[str, dict[str, str]]) -> None:
    """Replace truncated per-question ``text`` from the registry, in place.

    Only overwrites when the registry has a *longer* string for the key — a
    belt-and-suspenders check that keeps us from clobbering a full-length row
    because a stale registry happened to carry a shorter value.
    """
    cfg = result.get("config") or {}
    dataset = cfg.get("dataset") or ""
    texts = registry.get(dataset)
    if not texts:
        return
    for q in result.get("per_question") or []:
        key = q.get("key")
        if not key:
            continue
        full = texts.get(key)
        if full and len(full) > len(q.get("text") or ""):
            q["text"] = full


def _rehydrate_human_distributions(
    result: dict,
    *,
    strict: bool,
    warned_datasets: set[str],
) -> None:
    """Rehydrate stripped ``human_distribution`` rows from the canonical source.

    Committed ``leaderboard-results/*.json`` files carry no
    ``human_distribution`` for gated datasets (issue #308) — the field is
    stripped before commit and restored here, at publish time, from the
    canonical registry (:mod:`synthbench.human_distributions`). This is the
    distribution analogue of :func:`_rehydrate_question_text`, with one
    upgrade: the values come from the canonical dataset artifact, never from
    a submitter's copy.

    Only called on the gated emission path (an R2 uploader is configured —
    without one the gated artifacts are skipped entirely and there is
    nothing to rehydrate for). No-op when every row already carries a
    distribution or when the dataset is not gated.

    When rows remain without a distribution (no canonical source available,
    or keys missing from it): ``strict=True`` raises
    :class:`GatedPublishError` so CI deploys fail loudly instead of shipping
    gated artifacts with silently-absent human data; otherwise a warning is
    logged once per dataset.
    """
    from synthbench.human_distributions import (
        load_canonical_distributions,
        rehydrate_per_question,
    )

    cfg = result.get("config") or {}
    dataset = cfg.get("dataset") or ""
    if not dataset or not policy_for(dataset).serves_from_r2:
        return
    per_question = result.get("per_question") or []
    if not any(
        isinstance(q, dict) and not q.get("human_distribution") for q in per_question
    ):
        return

    canonical = load_canonical_distributions(dataset)
    missing = (
        rehydrate_per_question(per_question, canonical)
        if canonical is not None
        else sum(
            1
            for q in per_question
            if isinstance(q, dict) and not q.get("human_distribution")
        )
    )
    if not missing:
        return
    if strict:
        raise GatedPublishError(
            f"{missing} per-question row(s) for gated dataset {dataset!r} have "
            "no human_distribution and the canonical registry could not supply "
            "them. Provide a canonical source — a local artifact under "
            "$SYNTHBENCH_HUMAN_DISTRIBUTIONS_DIR / ~/.synthbench/human-distributions, "
            "the R2 object human-distributions/<dataset>.json, or the dataset "
            "adapter's cache (see scripts/generate-canonical-distributions.py) — "
            "or drop strict gating to publish these artifacts without human "
            "distributions."
        )
    if dataset not in warned_datasets:
        warned_datasets.add(dataset)
        logger.warning(
            "gated dataset %s: %d per-question row(s) missing human_distribution "
            "and no canonical source available — gated artifacts will ship "
            "without human distributions",
            dataset,
            missing,
        )


def _compute_variance_summary(sps_values: list[float]) -> dict:
    nums = [float(v) for v in sps_values if v is not None]
    if not nums:
        return {"n_replicates": 0}
    lo, hi = min(nums), max(nums)
    mean = sum(nums) / len(nums)
    std = _safe_stddev(nums) or 0.0
    cv = (std / mean) if mean else 0.0
    return {
        "n_replicates": len(nums),
        "sps_mean": _round_or_none(mean),
        "sps_std": _round_or_none(std),
        "sps_range": [_round_or_none(lo), _round_or_none(hi)],
        "sps_cv": _round_or_none(cv),
    }


def _topic_aggregate(per_run_topics: list[dict[str, float]]) -> dict[str, dict]:
    """Mean/std per topic across a list of per-run topic_scores dicts."""
    from collections import defaultdict

    buckets: dict[str, list[float]] = defaultdict(list)
    for scores in per_run_topics:
        for topic, val in scores.items():
            if val is None:
                continue
            buckets[topic].append(float(val))
    out: dict[str, dict] = {}
    for topic, vals in sorted(buckets.items()):
        out[topic] = {
            "mean": _round_or_none(_safe_mean(vals)),
            "std": _round_or_none(_safe_stddev(vals) or 0.0),
            "n_replicates": len(vals),
        }
    return out


def _build_index_entry(
    run_id: str,
    config_id: str,
    parsed,
    cfg: dict,
    scores: dict,
    agg: dict,
    timestamp: str | None,
    display_name: str,
    is_baseline: bool,
    is_ensemble: bool,
    n_topics: int,
) -> dict:
    return {
        "run_id": run_id,
        "config_id": config_id,
        "framework": parsed.framework,
        "base_provider": parsed.base_provider,
        "model": parsed.model,
        "display_name": display_name,
        "dataset": cfg.get("dataset", "unknown"),
        "temperature": cfg.get("temperature"),
        "template": _tpl_name(cfg.get("prompt_template")),
        "samples_per_question": cfg.get("samples_per_question"),
        # `or` (not dict-default) so ensemble rows whose config never carried
        # n_evaluated fall through to the recomputed per-question count
        # instead of publishing n=0.
        "n_questions": cfg.get("n_evaluated") or agg.get("n_questions", 0),
        "n_topics": n_topics,
        "sps": _round_or_none(scores.get("sps")),
        "p_dist": _round_or_none(scores.get("p_dist")),
        "p_rank": _round_or_none(scores.get("p_rank")),
        "p_refuse": _round_or_none(scores.get("p_refuse")),
        "jsd": _round_or_none(agg.get("mean_jsd")),
        "tau": _round_or_none(agg.get("mean_kendall_tau")),
        "timestamp": timestamp,
        "is_baseline": is_baseline,
        "is_ensemble": is_ensemble,
    }


def _build_run_detail(
    run_id: str,
    config_id: str,
    parsed,
    result: dict,
    display_name: str,
    is_baseline: bool,
    is_ensemble: bool,
    timestamp: str | None,
) -> dict:
    cfg = result.get("config", {}) or {}
    # Recomputed from per-question rows (P0-4) — submitted scores/aggregate
    # metrics are never republished. The submitted aggregate block is only
    # read for operational metadata (elapsed_seconds, n_parse_failures).
    view = _recomputed_view(result, source=run_id)
    scores = view["scores"]
    rec_agg = view["aggregate"]
    agg = result.get("aggregate", {}) or {}
    per_question = result.get("per_question", []) or []
    demo = result.get("demographic_breakdown", {}) or {}
    temporal = result.get("temporal_breakdown", {}) or {}
    dataset_name = cfg.get("dataset", "unknown")
    policy = policy_for(dataset_name)

    # Question-resampling bootstrap CIs, recomputed at publish time (P2-4:
    # the stored per_metric_ci of legacy files labelled a 2-metric parity
    # CI as the SPS CI). None when unavailable — never a degraded [0, 0].
    per_metric_ci = {
        metric: list(bounds) for metric, bounds in view["per_metric_ci"].items()
    } or None

    detail = {
        "run_id": run_id,
        "config_id": config_id,
        "benchmark": result.get("benchmark", "synthbench"),
        "version": result.get("version"),
        "timestamp": timestamp,
        "framework": parsed.framework,
        "base_provider": parsed.base_provider,
        "model": parsed.model,
        "display_name": display_name,
        "is_baseline": is_baseline,
        "is_ensemble": is_ensemble,
        "dataset": dataset_name,
        "dataset_policy": _policy_to_dict(policy),
        "temperature": cfg.get("temperature"),
        "template": _tpl_name(cfg.get("prompt_template")),
        "samples_per_question": cfg.get("samples_per_question"),
        "n_requested": cfg.get("n_requested"),
        "n_evaluated": cfg.get("n_evaluated") or rec_agg.get("n_questions"),
        "question_set_hash": cfg.get("question_set_hash"),
        "topic_filter": cfg.get("topic_filter"),
        "parse_failure_rate": cfg.get("parse_failure_rate"),
        "scores": {
            "sps": _round_or_none(scores.get("sps")),
            "p_dist": _round_or_none(scores.get("p_dist")),
            "p_rank": _round_or_none(scores.get("p_rank")),
            "p_refuse": _round_or_none(scores.get("p_refuse")),
        },
        "aggregate": {
            "mean_jsd": _round_or_none(rec_agg.get("mean_jsd")),
            "median_jsd": _round_or_none(rec_agg.get("median_jsd")),
            "mean_kendall_tau": _round_or_none(rec_agg.get("mean_kendall_tau")),
            "composite_parity": _round_or_none(rec_agg.get("composite_parity")),
            "n_questions": rec_agg.get("n_questions"),
            "elapsed_seconds": _round_or_none(agg.get("elapsed_seconds"), places=3),
            "per_metric_ci": per_metric_ci,
            "n_parse_failures": agg.get("n_parse_failures"),
        },
        "per_question": _augment_per_question(
            per_question, policy=policy, dataset=dataset_name
        ),
    }

    if scores.get("p_cond") is not None:
        detail["scores"]["p_cond"] = _round_or_none(scores.get("p_cond"))
    if scores.get("p_sub") is not None:
        detail["scores"]["p_sub"] = _round_or_none(scores.get("p_sub"))

    # Holdout split report: compute SPS on the public/private partitions so
    # the site can show both numbers and flag divergent submissions. Only
    # emitted for datasets that actually participate in the split.
    from synthbench.private_holdout import compute_split_sps, is_holdout_enabled

    if is_holdout_enabled(dataset_name):
        split = compute_split_sps(dataset_name, per_question)
        detail["holdout_split"] = {
            "sps_public": _round_or_none(split.get("sps_public")),
            "sps_private": _round_or_none(split.get("sps_private")),
            "delta": _round_or_none(split.get("delta")),
            "n_public": split.get("n_public", 0),
            "n_private": split.get("n_private", 0),
            "flagged": bool(split.get("flagged", False)),
        }

    if demo:
        detail["demographic_breakdown"] = demo
    if temporal:
        detail["temporal_breakdown"] = temporal

    return detail


def _build_config_rollup(
    config_id: str,
    parsed,
    runs: list[dict],
    dataset: str,
    display_name: str,
    is_baseline: bool,
    is_ensemble: bool,
) -> dict:
    """Aggregate a set of replicate run records into a per-config rollup.

    Each ``runs`` entry is a dict with keys: run_id, timestamp, scores,
    aggregate, topic_scores, config.
    """
    replicates = []
    sps_values: list[float] = []
    jsd_values: list[float] = []
    tau_values: list[float] = []
    per_run_topics: list[dict[str, float]] = []

    for r in runs:
        scores = r["scores"]
        agg = r["aggregate"]
        replicates.append(
            {
                "run_id": r["run_id"],
                "timestamp": r["timestamp"],
                "sps": _round_or_none(scores.get("sps")),
                "p_dist": _round_or_none(scores.get("p_dist")),
                "p_rank": _round_or_none(scores.get("p_rank")),
                "p_refuse": _round_or_none(scores.get("p_refuse")),
                "jsd": _round_or_none(agg.get("mean_jsd")),
                "tau": _round_or_none(agg.get("mean_kendall_tau")),
                "n_questions": r["config"].get("n_evaluated")
                or agg.get("n_questions", 0),
            }
        )
        if scores.get("sps") is not None:
            sps_values.append(float(scores["sps"]))
        if agg.get("mean_jsd") is not None:
            jsd_values.append(float(agg["mean_jsd"]))
        if agg.get("mean_kendall_tau") is not None:
            tau_values.append(float(agg["mean_kendall_tau"]))
        if r.get("topic_scores"):
            per_run_topics.append(r["topic_scores"])

    sample_cfg = runs[0]["config"] if runs else {}

    rollup = {
        "config_id": config_id,
        "framework": parsed.framework,
        "base_provider": parsed.base_provider,
        "model": parsed.model,
        "display_name": display_name,
        "dataset": dataset,
        "temperature": sample_cfg.get("temperature"),
        "template": _tpl_name(sample_cfg.get("prompt_template")),
        "samples_per_question": sample_cfg.get("samples_per_question"),
        "is_baseline": is_baseline,
        "is_ensemble": is_ensemble,
        "n_replicates": len(replicates),
        "replicates": replicates,
        "aggregate": {
            "sps": {
                "mean": _round_or_none(_safe_mean(sps_values)),
                "std": _round_or_none(_safe_stddev(sps_values) or 0.0),
            },
            "jsd": {
                "mean": _round_or_none(_safe_mean(jsd_values)),
                "std": _round_or_none(_safe_stddev(jsd_values) or 0.0),
            },
            "tau": {
                "mean": _round_or_none(_safe_mean(tau_values)),
                "std": _round_or_none(_safe_stddev(tau_values) or 0.0),
            },
        },
        "variance_summary": _compute_variance_summary(sps_values),
        "topic_breakdown": _topic_aggregate(per_run_topics),
    }
    return rollup


def _write_minified(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, separators=(",", ":"), sort_keys=False)


def _routes_to_r2(dataset: str | None) -> bool:
    """Whether a per-dataset artifact must ship to R2 instead of local disk.

    Only the ``gated`` tier (sb-sj6) serves from R2. ``full`` continues to
    land in ``site/public/data/`` for the static-site Pages origin;
    ``aggregates_only`` and ``citation_only`` emit no per-question/run/
    config artifact at all — callers must short-circuit on
    :attr:`DatasetPolicy.suppress_per_question` before reaching this
    helper. Returns False when the dataset is unknown.

    Routing is a property of the dataset's license policy alone — it does
    NOT depend on whether an uploader happens to be configured. A gated
    artifact with no uploader is skipped (fail closed), never written to
    the local static output.
    """
    if dataset is None:
        return False
    return policy_for(dataset).serves_from_r2


class GatedPublishError(ValueError):
    """A gated-tier artifact could not be published in strict mode.

    Raised when strict gating is enabled and a dataset whose
    ``redistribution_policy`` routes to R2 has no uploader configured.
    Subclasses :class:`ValueError` so the publish CLI's existing error
    handling surfaces the message and exits non-zero.
    """


@dataclass
class GatedSkipLog:
    """Tracks gated artifacts that were skipped because R2 is unconfigured.

    License-restricted (``gated``) artifacts must never land in the local
    static output — that origin is served publicly without auth. When no
    R2 uploader is available the publish step either skips the artifact
    (default: degrade gracefully, gated data is unavailable until
    credentials are provided and the publish re-runs) or hard-fails
    (``strict=True``, used by CI deploys so a missing R2 configuration
    fails the build loudly instead of silently shipping without gated
    data).
    """

    strict: bool = False
    keys: list[str] = field(default_factory=list)

    def record(self, relative_key: str, dataset: str) -> None:
        if self.strict:
            raise GatedPublishError(
                f"Gated artifact {relative_key!r} (dataset {dataset!r}) has no "
                "R2 uploader configured and strict gating is enabled. Gated "
                "artifacts are never written to the local static output. "
                "Configure R2_ACCOUNT_ID/R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY/"
                "R2_BUCKET, or drop --strict-gating / SYNTHBENCH_PUBLISH_STRICT "
                "to skip gated artifacts instead."
            )
        self.keys.append(relative_key)

    @property
    def count(self) -> int:
        return len(self.keys)


def _emit_artifact(
    output_dir: Path,
    relative_key: str,
    payload: dict,
    *,
    dataset: str | None,
    r2_uploader: "R2Uploader | None",
    gated_skips: GatedSkipLog | None = None,
) -> None:
    """Route a single publish artifact to R2 or local disk per dataset policy.

    ``relative_key`` is interpreted both as a path under ``output_dir`` for
    local writes and as the R2 object key for uploads, so the two surfaces
    stay in lock-step (the Worker proxy looks up the same path).

    Gated-tier artifacts are fail-closed: when no uploader is configured
    they are recorded on ``gated_skips`` (or silently dropped if no log is
    supplied) and NEVER written under ``output_dir`` — the local output is
    the public static origin, and writing license-restricted data there is
    exactly the leak this routing exists to prevent.
    """
    if _routes_to_r2(dataset):
        if r2_uploader is None:
            if gated_skips is not None:
                # Raises GatedPublishError in strict mode.
                gated_skips.record(relative_key, dataset or "unknown")
            return
        r2_uploader.put_json(relative_key, payload)
        return
    _write_minified(output_dir / relative_key, payload)


def publish_runs(
    results_dir: Path,
    output_dir: Path,
    version: str = "0.1.0",
    *,
    r2_uploader: "R2Uploader | None" = None,
    strict_gating: bool = False,
) -> dict[str, int]:
    """Emit the three run-explorer artifact families.

    Per-run and per-config artifacts are routed by the dataset's
    :class:`DatasetPolicy` (sb-sj6):

    - ``full`` — artifacts land on disk under ``output_dir`` for the static
      site; the Pages origin serves them without auth.
    - ``gated`` — artifacts ship to Cloudflare R2 (requires
      ``r2_uploader``); the Worker proxy fronts the bucket with Supabase
      JWT validation so only signed-in visitors can reach them. When no
      uploader is configured these artifacts are SKIPPED, never written
      locally (fail closed — the local output is the public static
      origin). With ``strict_gating=True`` the first such artifact raises
      :class:`GatedPublishError` instead.
    - ``aggregates_only`` / ``citation_only`` — no per-run / per-config
      artifact emitted. The catalog row in ``runs-index.json`` still
      appears so the leaderboard renders, but drill-down pages have no
      payload to fetch (the frontend suppresses the link via
      ``leaderboard.dataset_policies``).

    The catalog (``runs-index.json``) always lands locally — it spans
    every dataset and carries only aggregate fields, so it stays public
    alongside ``leaderboard.json``.

    Artifacts written:
        ``<output_dir>/runs-index.json`` — public catalog (always local)
        ``full`` datasets:
            ``<output_dir>/config/<config-id>.json`` — per-config rollup
            ``<output_dir>/run/<run-id>.json`` — full per-question detail
        ``gated`` datasets (when ``r2_uploader`` is set):
            ``r2://<bucket>/config/<config-id>.json``
            ``r2://<bucket>/run/<run-id>.json``

    Returns a dict of counts: {"runs": N, "configs": M, "gated_skipped": K}.
    ``runs``/``configs`` reflect the index entries, not the number of
    per-run/per-config artifacts actually emitted (suppressed datasets
    still contribute to the index). ``gated_skipped`` counts gated
    artifacts dropped because no R2 uploader was configured — callers
    should surface a prominent warning when it is non-zero.
    """
    from synthbench.config_id import build_config_id
    from synthbench.leaderboard import display_provider_name, provider_framework

    import shutil

    results_dir = Path(results_dir)
    output_dir = Path(output_dir)
    run_dir = output_dir / "run"
    config_dir = output_dir / "config"
    # Clean stale local artifacts so removed/migrated source runs don't
    # linger. R2 objects are not pruned here — the uploader overwrites by
    # key on republish, and bucket versioning preserves prior versions for
    # operator-driven rollback.
    if run_dir.exists():
        shutil.rmtree(run_dir)
    if config_dir.exists():
        shutil.rmtree(config_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    gated_skips = GatedSkipLog(strict=strict_gating)

    json_files = sorted(results_dir.glob("*.json"))
    if not json_files:
        raise ValueError(f"No result files found in {results_dir}")

    # Historical per_question.text was truncated at 120 chars by report.py
    # (removed in sb-5o1 / PR #115). Re-running benchmarks to regenerate the
    # on-disk JSONs is prohibitively expensive, so we repair the text at
    # publish time from committed fixtures.
    text_registry = _load_question_text_registry(results_dir.parent)

    # Two passes: first build per-run detail + collect replicate records by
    # config_id; second pass writes config rollups.
    index_entries: list[dict] = []
    grouped: dict[str, list[dict]] = {}
    group_meta: dict[str, dict] = {}

    pre_loaded: list[tuple[Path, str, dict]] = []
    for jf in json_files:
        try:
            with open(jf) as f:
                result = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if result.get("benchmark") != "synthbench":
            continue
        pre_loaded.append((jf, _run_id_from_path(jf), result))

    valid_triples = [
        (jf, rid, data) for (jf, rid, data) in pre_loaded if not is_invalid_run(data)[0]
    ]

    # Committed result files carry no human_distribution for gated datasets
    # (issue #308). Rehydrate from the canonical registry before emitting
    # gated artifacts — only relevant when an uploader is configured, since
    # gated artifacts are otherwise skipped entirely (fail closed).
    rehydrate_warned: set[str] = set()

    for jf, _run_id_early, result in valid_triples:
        _rehydrate_question_text(result, text_registry)
        if r2_uploader is not None:
            _rehydrate_human_distributions(
                result, strict=strict_gating, warned_datasets=rehydrate_warned
            )

        cfg = result.get("config", {}) or {}
        provider_raw = cfg.get("provider", "unknown")
        dataset = cfg.get("dataset", "unknown")
        temperature = cfg.get("temperature")
        template = _tpl_name(cfg.get("prompt_template"))
        samples = cfg.get("samples_per_question")
        qset = cfg.get("question_set_hash")

        config_id, parsed = build_config_id(
            provider_raw,
            dataset=dataset,
            temperature=temperature,
            template=template,
            samples_per_question=samples,
            question_set_hash=qset,
        )

        display_name = display_provider_name(provider_raw)
        framework_taxonomy = provider_framework(provider_raw)
        is_baseline = framework_taxonomy == "baseline" or parsed.framework == "baseline"
        is_ensemble = (
            parsed.framework == "ensemble" or "ensemble" in provider_raw.lower()
        )

        run_id = _run_id_from_path(jf)
        timestamp = _parse_run_timestamp(run_id, fallback=result.get("timestamp"))

        # Derive topic scores once (also used in rollup aggregation).
        per_question = result.get("per_question", []) or []
        topic_scores = _compute_topic_scores(per_question) if per_question else {}

        # Under ``aggregates_only`` / ``citation_only`` the dataset gets no
        # per-run artifact at all — the catalog row in ``runs-index.json``
        # carries only aggregate fields, so the leaderboard still renders
        # without exposing per-question distributions through the drill-down
        # detail. ``full`` lands locally; ``gated`` ships to R2 via the
        # routing helper.
        run_policy = policy_for(dataset)
        if not run_policy.suppress_per_question:
            run_detail = _build_run_detail(
                run_id=run_id,
                config_id=config_id,
                parsed=parsed,
                result=result,
                display_name=display_name,
                is_baseline=is_baseline,
                is_ensemble=is_ensemble,
                timestamp=timestamp,
            )
            if topic_scores:
                run_detail["topic_scores"] = {
                    k: _round_or_none(v) for k, v in topic_scores.items()
                }

            _emit_artifact(
                output_dir,
                f"run/{run_id}.json",
                run_detail,
                dataset=dataset,
                r2_uploader=r2_uploader,
                gated_skips=gated_skips,
            )

        # Recomputed metrics (P0-4) override the submitted aggregate block;
        # the submitted block still contributes operational metadata only
        # (elapsed_seconds, token_usage, latency).
        view = _recomputed_view(result, source=run_id)
        agg = {**(result.get("aggregate", {}) or {}), **view["aggregate"]}
        scores = view["scores"]

        index_entries.append(
            _build_index_entry(
                run_id=run_id,
                config_id=config_id,
                parsed=parsed,
                cfg=cfg,
                scores=scores,
                agg=agg,
                timestamp=timestamp,
                display_name=display_name,
                is_baseline=is_baseline,
                is_ensemble=is_ensemble,
                n_topics=len(topic_scores),
            )
        )

        grouped.setdefault(config_id, []).append(
            {
                "run_id": run_id,
                "timestamp": timestamp,
                "config": cfg,
                "scores": scores,
                "aggregate": agg,
                "topic_scores": topic_scores,
            }
        )
        if config_id not in group_meta:
            group_meta[config_id] = {
                "parsed": parsed,
                "dataset": dataset,
                "display_name": display_name,
                "is_baseline": is_baseline,
                "is_ensemble": is_ensemble,
            }

    # Write per-config rollups. Skipped for ``aggregates_only`` /
    # ``citation_only`` datasets so no per-question surface ships outside
    # the aggregate leaderboard row; ``gated`` lands in R2, ``full`` local.
    for config_id, runs in grouped.items():
        meta = group_meta[config_id]
        config_policy = policy_for(meta["dataset"])
        if config_policy.suppress_per_question:
            continue
        # Sort replicates by timestamp for stable, chronological display.
        runs_sorted = sorted(runs, key=lambda r: r.get("timestamp") or "")
        rollup = _build_config_rollup(
            config_id=config_id,
            parsed=meta["parsed"],
            runs=runs_sorted,
            dataset=meta["dataset"],
            display_name=meta["display_name"],
            is_baseline=meta["is_baseline"],
            is_ensemble=meta["is_ensemble"],
        )
        _emit_artifact(
            output_dir,
            f"config/{config_id}.json",
            rollup,
            dataset=meta["dataset"],
            r2_uploader=r2_uploader,
            gated_skips=gated_skips,
        )

    # Sort index for stable output: dataset, then SPS desc, then timestamp.
    index_entries.sort(
        key=lambda e: (
            e.get("dataset") or "",
            -(e.get("sps") or 0.0),
            e.get("timestamp") or "",
        )
    )

    index_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthbench_version": version,
        "n_runs": len(index_entries),
        "n_configs": len(grouped),
        "runs": index_entries,
    }
    _write_minified(output_dir / "runs-index.json", index_payload)

    return {
        "runs": len(index_entries),
        "configs": len(grouped),
        "gated_skipped": gated_skips.count,
    }


# ---------------------------------------------------------------------------
# Per-question question-explorer artifacts (sb-eiv)
# ---------------------------------------------------------------------------


# Filename-safe sanitization for question keys. Keys observed across the
# three datasets (``GOQA_0_adeba4f8``, ``PREDICTA_W27``, ``AAPERSADV_W125``)
# are alphanumeric + underscore, but we guard against future datasets whose
# keys might contain slashes, spaces, or other shell/URL-hostile chars.
_QUESTION_KEY_SAFE_RE = re.compile(r"[^A-Za-z0-9_\-]")


def _safe_question_key(key: str) -> str:
    """Return a filesystem- and URL-safe rendering of ``key``.

    Non-safe characters are replaced with ``_``; the transform is stable,
    so the same source key always maps to the same on-disk filename. This
    mirrors the ``run_id`` strategy — keep the real key in JSON payloads
    and index entries so the site can display it unaltered, while using
    the sanitized form only for paths.
    """
    return _QUESTION_KEY_SAFE_RE.sub("_", key)


def _pairwise_mean_and_max_jsd(
    dists: list[dict[str, float]],
) -> tuple[float | None, float | None]:
    """Return (mean, max) pairwise JSD across a list of distributions.

    Returns ``(None, None)`` when fewer than two distributions are provided.
    """
    from synthbench.metrics.distributional import jensen_shannon_divergence

    if len(dists) < 2:
        return (None, None)
    values: list[float] = []
    for i in range(len(dists)):
        for j in range(i + 1, len(dists)):
            values.append(jensen_shannon_divergence(dists[i], dists[j]))
    if not values:
        return (None, None)
    return (sum(values) / len(values), max(values))


def _top_option(dist: dict[str, float] | None) -> str | None:
    """Return the option with highest mass, or ``None`` for empty / tied-zero."""
    if not dist:
        return None
    best_key: str | None = None
    best_val = -1.0
    for k, v in dist.items():
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv > best_val:
            best_val = fv
            best_key = k
    if best_val <= 0.0:
        return None
    return best_key


def _collect_question_rollups(
    results: list[tuple[str, dict]],
) -> dict[tuple[str, str], dict]:
    """Group per-question rows across all result files by (dataset, key).

    Input: list of ``(run_id, raw_result_json)`` tuples. Deduplicates each
    ``(dataset, key, framework, display_name)`` by keeping the row with the
    largest ``n_samples`` — this mirrors the leaderboard dedup policy so a
    model with multiple replicates contributes its best-sampled run.

    Output: ``{(dataset, key): {question, options, human_*, model_responses,
    aggregated_responses}}``. ``model_responses`` is the cross-model sample
    that feeds the trendslop summary (raw + single-model product, no
    baselines, no ensembles). ``aggregated_responses`` is a parallel bucket
    for ensemble entries — shown on the per-question page for comparison
    but deliberately excluded from the summary stats.
    """
    from synthbench.config_id import build_config_id
    from synthbench.leaderboard import display_provider_name, provider_framework

    # (dataset, key) → rollup skeleton (question text, options, human dist)
    rollups: dict[tuple[str, str], dict] = {}
    # (dataset, key, framework, display_name) → best response candidate
    # (cross-model trendslop bucket).
    best_by_key: dict[tuple[str, str, str, str], dict] = {}
    # Parallel bucket for ensemble entries, keyed the same way so replicates
    # dedup on n_samples.
    best_aggregated_by_key: dict[tuple[str, str, str, str], dict] = {}

    for run_id, data in results:
        cfg = data.get("config", {}) or {}
        provider_raw = cfg.get("provider", "") or ""
        if not provider_raw:
            continue
        framework = provider_framework(provider_raw)
        # Baselines (majority/random) are dropped entirely — they're not
        # "models answering the question" in any sense the per-question
        # view surfaces.
        if framework == "baseline":
            continue
        # Ensembles are partitioned into the aggregated bucket so they
        # don't muddy the cross-model trendslop summary but remain visible
        # on the per-question page.
        is_ensemble = "ensemble" in provider_raw.lower()

        dataset = cfg.get("dataset", "unknown")
        display_name = display_provider_name(provider_raw)
        base_provider = (
            provider_raw.split("/")[1] if "/" in provider_raw else provider_raw
        )

        tpl_stem = _tpl_name(cfg.get("prompt_template"))
        config_id, _ = build_config_id(
            provider_raw,
            dataset=dataset,
            temperature=cfg.get("temperature"),
            template=tpl_stem,
            samples_per_question=cfg.get("samples_per_question"),
            question_set_hash=cfg.get("question_set_hash"),
        )

        for q in data.get("per_question", []) or []:
            key = q.get("key")
            if not key:
                continue
            model_dist = q.get("model_distribution")
            if not isinstance(model_dist, dict) or not model_dist:
                continue

            rollup = rollups.get((dataset, key))
            if rollup is None:
                rollup = {
                    "dataset": dataset,
                    "key": key,
                    "question": q.get("text", ""),
                    "options": list(q.get("options") or []),
                    "human_distribution": dict(q.get("human_distribution") or {}),
                    "human_refusal_rate": q.get("human_refusal_rate"),
                    "temporal_year": q.get("temporal_year"),
                    "topic": q.get("topic"),
                }
                rollups[(dataset, key)] = rollup

            n_samples = q.get("n_samples") or 0
            candidate = {
                "config_id": config_id,
                "model": display_name,
                "framework": framework,
                "base_provider": base_provider,
                "distribution": dict(model_dist),
                "n_samples": int(n_samples) if n_samples is not None else 0,
                "jsd_to_human": _round_or_none(q.get("jsd")),
                "refusal_rate": _round_or_none(q.get("model_refusal_rate")),
                "run_id": run_id,
                "temperature": cfg.get("temperature"),
                "template": tpl_stem,
            }
            bucket_key = (dataset, key, framework, display_name)
            target = best_aggregated_by_key if is_ensemble else best_by_key
            prev = target.get(bucket_key)
            if prev is None or candidate["n_samples"] > prev["n_samples"]:
                target[bucket_key] = candidate

    for (dataset, key, _framework, _display), response in best_by_key.items():
        rollup = rollups.get((dataset, key))
        if rollup is None:
            continue
        rollup.setdefault("model_responses", []).append(response)

    for (
        dataset,
        key,
        _framework,
        _display,
    ), response in best_aggregated_by_key.items():
        rollup = rollups.get((dataset, key))
        if rollup is None:
            continue
        rollup.setdefault("aggregated_responses", []).append(response)

    return rollups


def _emit_response(r: dict) -> dict:
    """Shape a single response for emission (drops bookkeeping fields)."""
    return {
        "config_id": r["config_id"],
        "model": r["model"],
        "framework": r["framework"],
        "base_provider": r["base_provider"],
        "distribution": r["distribution"],
        "n_samples": r["n_samples"],
        "jsd_to_human": r["jsd_to_human"],
        "refusal_rate": r["refusal_rate"],
        "run_id": r["run_id"],
        "temperature": r.get("temperature"),
        "template": r.get("template"),
    }


def _finalize_question_payload(rollup: dict) -> dict:
    """Build the emitted per-question JSON from a raw rollup dict.

    Sorts ``model_responses`` by ``jsd_to_human`` ascending (null → end) so
    the top row is the closest-to-human model. Computes the summary block
    used by the trendslop indicators (mean/max pairwise JSD, consensus
    option, refusal-rate spread) from ``model_responses`` ONLY —
    ``aggregated_responses`` (ensembles) are emitted for display but
    excluded from summary math to avoid double-counting.
    """
    responses = rollup.get("model_responses", []) or []
    # Sort stably: lowest jsd_to_human first, then model name for ties.
    responses.sort(
        key=lambda r: (
            r.get("jsd_to_human")
            if r.get("jsd_to_human") is not None
            else float("inf"),
            r.get("model") or "",
        )
    )

    dists = [
        r["distribution"] for r in responses if isinstance(r.get("distribution"), dict)
    ]
    cross_mean, cross_max = _pairwise_mean_and_max_jsd(dists)

    # Consensus option: most common model-modal pick. Ties broken by alphabetic
    # order so output is deterministic across publishes.
    modal_counts: dict[str, int] = {}
    for r in responses:
        modal = _top_option(r.get("distribution"))
        if modal is not None:
            modal_counts[modal] = modal_counts.get(modal, 0) + 1
    consensus: str | None = None
    if modal_counts:
        best_count = max(modal_counts.values())
        tied = sorted([k for k, v in modal_counts.items() if v == best_count])
        consensus = tied[0] if tied else None

    refusals = [
        r["refusal_rate"] for r in responses if r.get("refusal_rate") is not None
    ]
    refusal_spread = (
        round(max(refusals) - min(refusals), 6) if len(refusals) >= 2 else None
    )

    jsd_to_human_values = [
        r["jsd_to_human"] for r in responses if r.get("jsd_to_human") is not None
    ]
    jsd_to_human_mean = (
        _round_or_none(sum(jsd_to_human_values) / len(jsd_to_human_values))
        if jsd_to_human_values
        else None
    )

    # Shape model_responses for emission (drop bookkeeping fields the
    # frontend doesn't need; keep temperature/template for the drill-down
    # breadcrumb on the question page).
    emitted_responses = [_emit_response(r) for r in responses]

    aggregated = rollup.get("aggregated_responses", []) or []
    aggregated.sort(
        key=lambda r: (
            r.get("jsd_to_human")
            if r.get("jsd_to_human") is not None
            else float("inf"),
            r.get("model") or "",
        )
    )
    emitted_aggregated = [_emit_response(r) for r in aggregated]

    human_dist = rollup.get("human_distribution") or {}
    policy = policy_for(rollup["dataset"])
    # Pre-compute human_top_option before potentially clearing the raw
    # distribution — the modal pick itself is an aggregate label, not the
    # full distribution, and is safe to keep under aggregates_only.
    human_top = _top_option(human_dist)
    suppress_human = policy.suppress_human_distribution
    emitted_human_dist: dict[str, float] | None = {} if suppress_human else human_dist
    emitted_human_refusal: float | None = (
        None if suppress_human else _round_or_none(rollup.get("human_refusal_rate"))
    )

    payload: dict = {
        "dataset": rollup["dataset"],
        "key": rollup["key"],
        "question": rollup.get("question", ""),
        "options": rollup.get("options", []),
        "human_distribution": emitted_human_dist,
        "human_refusal_rate": emitted_human_refusal,
        "model_responses": emitted_responses,
        "aggregated_responses": emitted_aggregated,
        "summary": {
            "n_models": len(emitted_responses),
            "cross_model_jsd_mean": _round_or_none(cross_mean),
            "cross_model_jsd_max": _round_or_none(cross_max),
            "consensus_option": consensus,
            "human_top_option": human_top,
            "refusal_rate_spread": refusal_spread,
            "jsd_to_human_mean": jsd_to_human_mean,
        },
        "dataset_policy": _policy_to_dict(policy),
    }
    topic = rollup.get("topic")
    if topic:
        payload["topic"] = topic
    year = rollup.get("temporal_year")
    if year:
        payload["temporal_year"] = year
    return payload


def _build_question_index_entry(payload: dict) -> dict:
    """Build a row for ``question/<dataset>/index.json`` from a per-question payload."""
    text: str = payload.get("question", "") or ""
    excerpt = text if len(text) <= 160 else text[:157] + "…"
    summary = payload.get("summary", {}) or {}
    entry = {
        "key": payload["key"],
        "question_excerpt": excerpt,
        "n_models": summary.get("n_models", 0),
        "cross_model_jsd_mean": summary.get("cross_model_jsd_mean"),
        "cross_model_jsd_max": summary.get("cross_model_jsd_max"),
        "jsd_to_human_mean": summary.get("jsd_to_human_mean"),
        "consensus_option": summary.get("consensus_option"),
        "human_top_option": summary.get("human_top_option"),
        "refusal_rate_spread": summary.get("refusal_rate_spread"),
    }
    topic = payload.get("topic")
    if topic:
        entry["topic"] = topic
    return entry


def publish_questions(
    results_dir: Path,
    output_dir: Path,
    version: str = "0.1.0",
    *,
    r2_uploader: "R2Uploader | None" = None,
    strict_gating: bool = False,
) -> dict[str, int]:
    """Emit per-question rollups for the question-explorer view.

    Inverts the per-run pivot: for every ``(dataset, question_key)`` pair
    across all result files, aggregate every model's response into a single
    JSON file. Also emits a per-dataset index so the site can iterate keys
    at build time.

    Per-question files and the dataset index are routed by the dataset's
    :class:`DatasetPolicy` (sb-sj6): ``full`` lands on disk for the static
    site, ``gated`` ships to Cloudflare R2 (requires ``r2_uploader``), and
    ``aggregates_only`` / ``citation_only`` emit no per-question artifact
    at all. Gated artifacts with no uploader configured are SKIPPED, never
    written locally (fail closed — the local output is the public static
    origin); with ``strict_gating=True`` the first such artifact raises
    :class:`GatedPublishError` instead.

    Artifacts written:
        ``full`` datasets:
            ``<output_dir>/question/<dataset>/<sanitized-key>.json``
            ``<output_dir>/question/<dataset>/index.json``
        ``gated`` datasets (when ``r2_uploader`` is set):
            ``r2://<bucket>/question/<dataset>/<sanitized-key>.json``
            ``r2://<bucket>/question/<dataset>/index.json``

    Returns counts: ``{"questions": N, "datasets": M, "gated_skipped": K}``.
    ``gated_skipped`` counts gated artifacts dropped because no R2
    uploader was configured — callers should surface a prominent warning
    when it is non-zero.
    """
    import shutil

    results_dir = Path(results_dir)
    output_dir = Path(output_dir)
    question_root = output_dir / "question"
    # Clean stale local rollups; R2 objects are overwritten by key on
    # republish (versioning preserves history server-side).
    if question_root.exists():
        shutil.rmtree(question_root)
    question_root.mkdir(parents=True, exist_ok=True)

    gated_skips = GatedSkipLog(strict=strict_gating)

    text_registry = _load_question_text_registry(results_dir.parent)
    rehydrate_warned: set[str] = set()

    json_files = sorted(results_dir.glob("*.json"))
    loaded: list[tuple[str, dict]] = []
    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("benchmark") != "synthbench":
            continue
        _rehydrate_question_text(data, text_registry)
        if r2_uploader is not None:
            _rehydrate_human_distributions(
                data, strict=strict_gating, warned_datasets=rehydrate_warned
            )
        loaded.append((_run_id_from_path(jf), data))

    if not loaded:
        raise ValueError(f"No valid SynthBench result files found in {results_dir}")

    # Drop invalid runs (uniform-distribution garbage) before inverting the
    # per-run → per-question pivot, so bogus model_distributions don't
    # pollute the cross-model rollups used by the question-explorer view.
    valid_loaded, _excluded = _partition_valid_runs(loaded)

    rollups = _collect_question_rollups(valid_loaded)

    by_dataset_index: dict[str, list[dict]] = {}
    n_questions = 0

    from synthbench.private_holdout import is_private_holdout

    # Track sanitized keys per gated dataset so we can emit a local routes
    # manifest that the Astro static build enumerates for shell pages (the
    # payload itself lives behind the gate in R2 and is fetched client-side
    # once a JWT is available). Full-tier datasets don't need a routes
    # manifest — Astro walks their local on-disk directory directly.
    gated_routes: dict[str, list[str]] = {}

    for (dataset, key), rollup in rollups.items():
        if not rollup.get("model_responses"):
            continue
        policy = policy_for(dataset)
        if policy.suppress_per_question:
            # aggregates_only / citation_only: no per-question artifact, no
            # index entry.
            continue
        # Private holdout keys ship no per-question page at all: the page
        # would otherwise reveal the hidden human_distribution through its
        # summary fields (``human_top_option`` in particular). We also skip
        # the dataset index entry so the key isn't listed as "missing" —
        # from the public site's perspective the holdout keys simply do
        # not exist.
        if is_private_holdout(dataset, key):
            continue
        payload = _finalize_question_payload(rollup)
        safe_key = _safe_question_key(key)
        _emit_artifact(
            output_dir,
            f"question/{dataset}/{safe_key}.json",
            payload,
            dataset=dataset,
            r2_uploader=r2_uploader,
            gated_skips=gated_skips,
        )
        by_dataset_index.setdefault(dataset, []).append(
            _build_question_index_entry(payload)
        )
        if policy.serves_from_r2:
            gated_routes.setdefault(dataset, []).append(safe_key)
        n_questions += 1

    for dataset, entries in by_dataset_index.items():
        # Sort by descending cross-model JSD spread — divergent questions
        # (most interesting for trendslop vetting) bubble to the top of the
        # dataset index. Null spreads sort last.
        entries.sort(
            key=lambda e: (
                -(e.get("cross_model_jsd_mean") or -1.0),
                e.get("key") or "",
            )
        )
        index_payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthbench_version": version,
            "dataset": dataset,
            "n_questions": len(entries),
            "questions": entries,
        }
        _emit_artifact(
            output_dir,
            f"question/{dataset}/index.json",
            index_payload,
            dataset=dataset,
            r2_uploader=r2_uploader,
            gated_skips=gated_skips,
        )

    # Always emit a gated-routes manifest locally so the Astro SSG build can
    # prerender shell pages for gated-tier questions even when the rich
    # payload lives behind the Worker proxy. Empty mapping is fine; the file
    # just encodes "no gated datasets need shell pages".
    gated_routes_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthbench_version": version,
        "datasets": {
            dataset: sorted(set(keys)) for dataset, keys in gated_routes.items()
        },
    }
    _write_minified(output_dir / "gated-routes.json", gated_routes_payload)

    return {
        "questions": n_questions,
        "datasets": len(by_dataset_index),
        "gated_skipped": gated_skips.count,
    }
