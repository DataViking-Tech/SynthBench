"""Server-side scoring of withheld private-holdout rows.

Clients that load a dataset from SynthBench's public mirror get no human
answers for the private-holdout questions (docs/held-out.md). They still
sample the model on those questions and submit the rows with
``answer_withheld: true`` and null metrics. The submission pipeline calls
:func:`score_withheld_rows` with the canonical answer key (gated R2) before
validation, so the file it validates and publishes is complete.
"""

from __future__ import annotations

from typing import Any, Mapping

from synthbench.metrics import (
    extract_human_refusal_rate,
    jensen_shannon_divergence,
    kendall_tau_b,
    parity_score,
)
from synthbench.recompute import bootstrap_metric_cis, recompute_aggregates


class WithheldScoringError(ValueError):
    """Raised when a withheld row has no canonical answer to score against."""


def has_withheld_rows(data: Mapping[str, Any]) -> bool:
    return any(
        isinstance(q, dict) and q.get("answer_withheld") is True
        for q in data.get("per_question") or []
    )


def score_withheld_rows(
    data: dict, canonical: Mapping[str, Mapping[str, float]]
) -> int:
    """Score every withheld row in place and recompute the file's aggregates.

    Each withheld row gets the canonical ``human_distribution`` and the same
    per-question metrics the runner computes; ``answer_withheld`` is replaced
    by ``scored_server_side: true``. ``scores``, the aggregate means and the
    per-metric CIs are then recomputed from all rows, the same way publish
    recomputes them. Returns the number of rows scored (0 leaves ``data``
    untouched).
    """
    rows = [
        q
        for q in data.get("per_question") or []
        if isinstance(q, dict) and q.get("answer_withheld") is True
    ]
    if not rows:
        return 0
    missing = [q.get("key") for q in rows if not canonical.get(q.get("key"))]
    if missing:
        raise WithheldScoringError(
            f"no canonical answers for {len(missing)} withheld row(s): {missing[:5]}"
        )

    for q in rows:
        human = dict(canonical[q["key"]])
        model = q.get("model_distribution") or {}
        jsd = jensen_shannon_divergence(human, model)
        tau = kendall_tau_b(human, model)
        q["human_distribution"] = {k: round(v, 4) for k, v in human.items()}
        q["jsd"] = round(jsd, 6)
        q["kendall_tau"] = round(tau, 6)
        q["parity"] = round(parity_score(jsd, tau), 6)
        q["human_refusal_rate"] = round(extract_human_refusal_rate(human), 6)
        del q["answer_withheld"]
        q["scored_server_side"] = True

    per_question = data["per_question"]
    scores = data.setdefault("scores", {})
    rec = recompute_aggregates(per_question, extended_scores=scores)
    if rec is not None:
        scores.update(
            {
                "sps": round(rec.sps, 6),
                "p_dist": round(rec.p_dist, 6),
                "p_rank": round(rec.p_rank, 6),
            }
        )
        if rec.p_refuse is not None:
            scores["p_refuse"] = round(rec.p_refuse, 6)
        aggregate = data.setdefault("aggregate", {})
        aggregate.update(
            {
                "mean_jsd": round(rec.mean_jsd, 6),
                "median_jsd": round(rec.median_jsd, 6),
                "mean_kendall_tau": round(rec.mean_kendall_tau, 6),
                "composite_parity": round(rec.parity_two, 6),
                "per_metric_ci": {
                    k: [round(lo, 6), round(hi, 6)]
                    for k, (lo, hi) in bootstrap_metric_cis(
                        per_question, extended_scores=scores
                    ).items()
                },
            }
        )
        aggregate.pop("n_answers_withheld", None)
        aggregate["n_scored_server_side"] = len(rows)
    return len(rows)
