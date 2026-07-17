"""Research-findings block computed from committed run artifacts (#309).

Every quantitative claim in the published findings block (and the generated
sections of ``FINDINGS.md``) is derived here, at publish time, from the
per-question rows in ``leaderboard-results/`` via the same recompute path
that ranks the leaderboard (#305). Numbers that genuinely cannot be derived
from committed artifacts live in :data:`ASSERTED_CONSTANTS` with an explicit
source, and the CI drift guard (``tests/test_findings_drift.py``) fails when
either side rots.

Metric convention: all SPS values here are the **full composite** ("sps"
convention per SUBMISSIONS.md — the equal-weighted mean of every available
component), recomputed from per-question rows. The retired 2-metric
``parity-2`` composite is never used.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

SPS_CONVENTION = "sps"
"""Composite convention every number in the findings block uses.

``"sps"`` = full composite (equal-weighted mean of all available components,
recomputed from per-question rows; see SUBMISSIONS.md). The legacy
``parity-2`` (0.5*P_dist + 0.5*P_rank) convention is not used anywhere in
the findings block.
"""

# Display-name map: product entries -> underlying raw-LLM display name.
# Also used by publish._annotate_normalized_sps so a SynthPanel row can look
# up its corresponding "just prompt the model" baseline SPS for the same
# dataset. Kept as a small explicit map (rather than string parsing) because
# the product display names omit the vendor prefix ("Haiku 4.5" vs "Claude
# Haiku 4.5") and a typo-tolerant match would silently bind the wrong row.
PRODUCT_TO_RAW_DISPLAY: dict[str, str] = {
    "SynthPanel (Haiku 4.5)": "Claude Haiku 4.5",
    "SynthPanel (Sonnet 4)": "Claude Sonnet 4",
    "SynthPanel (GPT-4o-mini)": "GPT-4o-mini",
    "SynthPanel (GPT-4o)": "GPT-4o",
    "SynthPanel (Gemini Flash Lite)": "Gemini Flash Lite",
    "SynthPanel (Llama 3.3 70B)": "Llama 3.3 70B",
}

# Short display labels for demographic groups whose raw SubPOP labels are
# long. The raw label is preserved in ``group_raw``. The short forms are
# load-bearing for the site: KeyFindings.astro looks up "$100K+" / "<$30K"
# and "Republican" / "Democrat" by exact string.
_GROUP_DISPLAY: dict[str, str] = {
    "$100,000 or more": "$100K+",
    "Less than $30,000": "<$30K",
    "College graduate/some postgrad": "College graduate",
    "Less than high school": "Less than HS",
}

# Attributes surfaced in the site-facing conditioning_results block (chart
# colors and headline-ratio lookups exist for exactly these). Everything
# else a run measured lands in conditioning_extended.
_CONDITIONING_SITE_ATTRIBUTES = ("POLPARTY", "INCOME", "EDUCATION")

# Numbers the artifacts cannot reproduce. Each entry names its source; the
# drift guard asserts the published block carries exactly this list, so a
# hand-edit in one place without the other fails CI.
ASSERTED_CONSTANTS: list[dict] = [
    {
        "name": "blend_weighting_equivalence",
        "value": "equal-weight ~= score-proportional ~= inverse-JSD (to 3 decimals)",
        "source": (
            "Session-1 ensemble weighting comparison (2026-04-12); the "
            "alternative-weighting blend files were not committed to "
            "leaderboard-results/, so this is not reproducible from artifacts."
        ),
    },
    {
        "name": "per_question_improvement_share",
        "value": "72-81% of individual questions improve under blending",
        "source": (
            "Session-1 per-question blend analysis (2026-04-12), computed "
            "under the retired parity-2 convention; not recomputed since."
        ),
    },
    {
        "name": "oracle_ceiling_gap",
        "value": "per-question oracle model selection barely exceeds the equal blend",
        "source": (
            "Session-1 oracle analysis (2026-04-12); oracle blend files were "
            "not committed to leaderboard-results/."
        ),
    },
    {
        "name": "base_entropy_h5",
        "value": (
            "base output entropy (bits, default temperature): "
            "GPT-4o-mini 0.22, Claude Haiku 4.5 0.36, Gemini Flash Lite 0.56"
        ),
        "source": (
            "Experiment H5 notebook analysis (2026-04-12) of "
            "default-temperature model_distribution rows; the notebook "
            "output was not committed, so the exact values are asserted."
        ),
    },
    {
        "name": "ensemble_signed_error_correlation",
        "value": (
            "pairwise Pearson r of constituents' per-option signed residuals "
            "(model probability − human probability) on the ensemble common "
            "question sets: globalopinionqa 0.27–0.44, opinionsqa 0.36–0.38, "
            "subpop 0.36–0.42 — all pairs moderately positively correlated"
        ),
        "source": (
            "Computed 2026-07-16 from the committed constituents' "
            "per-question model_distribution rows plus canonical "
            "human-distribution rehydration (synthbench.human_distributions); "
            "committed gated artifacts strip human_distribution (#308), so "
            "the signed residuals are not derivable from public artifacts "
            "alone. The JSD-based correlations in ensemble_error_correlation "
            "ARE derivable and are recomputed by the drift guard."
        ),
    },
    {
        "name": "template_refusal_collapse",
        "value": (
            "P_refuse collapses from ~0.80 to 0.40-0.50 on templates with "
            "unfilled format-string placeholders"
        ),
        "source": (
            "Session-1 template-variant analysis (2026-04-12); per-component "
            "P_refuse for the template runs is derivable in principle but the "
            "published block only tracks composite SPS for templates."
        ),
    },
]


def _run_sps(result: dict) -> float | None:
    """Recomputed full-composite SPS for one run, without bootstrap CIs.

    Uses the cached publish-time view when present (so publish never pays
    twice), else calls ``recompute_aggregates`` directly — the identical
    scoring path, minus the expensive CI bootstrap.
    """
    from synthbench.publish import _RECOMPUTED_KEY

    cached = result.get(_RECOMPUTED_KEY)
    if isinstance(cached, dict):
        sps = cached.get("scores", {}).get("sps")
        return float(sps) if isinstance(sps, (int, float)) else None

    from synthbench.recompute import recompute_aggregates

    rec = recompute_aggregates(
        result.get("per_question") or [],
        extended_scores=result.get("scores") or {},
    )
    return None if rec is None else rec.sps


def _effective_n(result: dict) -> int:
    from synthbench.publish import _effective_n as impl

    return impl(result)


def _run_components(result: dict) -> dict[str, float] | None:
    """Recomputed score components (sps/p_dist/p_rank/p_refuse) for one run.

    Same scoring path as :func:`_run_sps` but returns every component the
    elicitation comparison publishes, not just the composite. ``p_refuse``
    is omitted when the run carries no refusal data.
    """
    from synthbench.publish import _RECOMPUTED_KEY

    cached = result.get(_RECOMPUTED_KEY)
    if isinstance(cached, dict):
        scores = cached.get("scores") or {}
    else:
        from synthbench.recompute import recompute_aggregates

        rec = recompute_aggregates(
            result.get("per_question") or [],
            extended_scores=result.get("scores") or {},
        )
        if rec is None:
            return None
        scores = {"sps": rec.sps, "p_dist": rec.p_dist, "p_rank": rec.p_rank}
        if rec.p_refuse is not None:
            scores["p_refuse"] = rec.p_refuse
    out = {
        k: float(v)
        for k, v in scores.items()
        if k in ("sps", "p_dist", "p_rank", "p_refuse") and isinstance(v, (int, float))
    }
    return out if "sps" in out else None


def load_valid_results(results_dir: Path) -> tuple[list[dict], set[str]]:
    """Load SynthBench result files, split into (valid_results, excluded_run_ids).

    Mirrors the publish-time load: non-SynthBench / unparseable files are
    skipped, uniform-garbage runs are excluded (run_validity), and the
    excluded run ids are returned so callers can flag ensembles whose
    constituents were filtered.
    """
    from synthbench.publish import _partition_valid_runs, _run_id_from_path

    loaded: list[tuple[str, dict]] = []
    for jf in sorted(results_dir.glob("*.json")):
        try:
            with open(jf) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("benchmark") == "synthbench":
            loaded.append((_run_id_from_path(jf), data))
    valid_pairs, excluded = _partition_valid_runs(loaded)
    return [d for _, d in valid_pairs], {e["run_id"] for e in excluded}


def _mean_std(values: list[float]) -> tuple[float, float | None]:
    mean = round(statistics.mean(values), 6)
    std = round(statistics.stdev(values), 6) if len(values) > 1 else None
    return mean, std


def _build_temperature_sweep(results: list[dict]) -> list[dict]:
    """Per-(model, temperature) recomputed SPS over the OpinionsQA sweep runs.

    Sweep runs are identified by the explicit `` t=`` provider suffix the
    sweep sessions used, so default-temperature leaderboard runs (different
    question counts) never mix into a sweep cell.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework

    cells: dict[tuple[str, float], list[float]] = {}
    for r in results:
        cfg = r.get("config") or {}
        provider = cfg.get("provider", "")
        temperature = cfg.get("temperature")
        if (
            cfg.get("dataset") != "opinionsqa"
            or " t=" not in provider
            or " tpl=" in provider
            or provider_framework(provider) != "product"
            or not isinstance(temperature, (int, float))
        ):
            continue
        sps = _run_sps(r)
        if sps is None:
            continue
        display = display_provider_name(provider)
        model = PRODUCT_TO_RAW_DISPLAY.get(display, display)
        cells.setdefault((model, float(temperature)), []).append(sps)

    out = []
    for (model, temperature), values in sorted(cells.items()):
        mean, std = _mean_std(values)
        point = {
            "model": model,
            "temperature": temperature,
            "sps": mean,
            "n_runs": len(values),
            "dataset": "opinionsqa",
        }
        if std is not None:
            point["std"] = std
        out.append(point)
    return out


def _build_template_comparison(results: list[dict]) -> list[dict]:
    """Persona-template variant comparison (SubPOP, Haiku, t=0.85)."""
    from synthbench.publish import _tpl_name

    cells: dict[str, list[float]] = {}
    for r in results:
        cfg = r.get("config") or {}
        tpl = _tpl_name(cfg.get("prompt_template"))
        if cfg.get("dataset") != "subpop" or tpl is None:
            continue
        sps = _run_sps(r)
        if sps is not None:
            cells.setdefault(tpl, []).append(sps)

    out = []
    for tpl, values in sorted(cells.items(), key=lambda kv: -statistics.mean(kv[1])):
        mean, std = _mean_std(values)
        row = {"template": tpl, "sps": mean, "n_runs": len(values)}
        if std is not None:
            row["std"] = std
        out.append(row)
    return out


def _build_ensemble_comparison(
    results: list[dict], excluded_run_ids: set[str]
) -> tuple[list[dict], list[str]]:
    """Ensemble vs best single vs random baseline, per dataset.

    Comparison set: the best (recomputed-SPS) non-ensemble, non-baseline
    leaderboard row — raw or product — evaluated on at least as many
    questions as the ensemble. Returns ``(rows, caveats)``; caveats flag
    ensembles blending a constituent that the validity filter excluded.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework
    from synthbench.publish import _dedup_results

    deduped = _dedup_results(results)
    by_dataset: dict[str, list[dict]] = {}
    for r in deduped:
        by_dataset.setdefault(
            (r.get("config") or {}).get("dataset", "unknown"), []
        ).append(r)

    rows: list[dict] = []
    caveats: list[str] = []
    for dataset in sorted(by_dataset):
        ds_results = by_dataset[dataset]
        ensemble = None
        for r in ds_results:
            if (r.get("config") or {}).get("provider", "").startswith("ensemble/"):
                ensemble = r
                break
        if ensemble is None:
            continue
        ensemble_sps = _run_sps(ensemble)
        if ensemble_sps is None:
            continue
        n_questions = _effective_n(ensemble)

        best = None
        best_sps = None
        random_sps = None
        random_n = None
        for r in ds_results:
            provider = (r.get("config") or {}).get("provider", "")
            fw = provider_framework(provider)
            sps = _run_sps(r)
            if sps is None:
                continue
            if provider == "random-baseline":
                random_sps, random_n = sps, _effective_n(r)
                continue
            if fw == "baseline" or provider.startswith("ensemble/"):
                continue
            if _effective_n(r) < n_questions:
                continue
            if best_sps is None or sps > best_sps:
                best, best_sps = r, sps

        if best is None or best_sps is None:
            continue
        best_provider = (best.get("config") or {}).get("provider", "")
        row = {
            "dataset": dataset,
            "best_single_model": display_provider_name(best_provider),
            "best_single_framework": provider_framework(best_provider),
            "best_single_sps": round(best_sps, 6),
            "ensemble_sps": round(ensemble_sps, 6),
            # From the rounded values so improvement == ensemble - best
            # exactly as published (avoids a ±1e-6 rounding mismatch).
            "improvement": round(round(ensemble_sps, 6) - round(best_sps, 6), 6),
            "n_questions": n_questions,
        }
        if random_sps is not None:
            row["random_baseline_sps"] = round(random_sps, 6)
            row["random_baseline_n"] = random_n
        rows.append(row)

        for src in (ensemble.get("config") or {}).get("ensemble_sources", []):
            stem = Path(src.get("file", "")).stem
            if stem in excluded_run_ids:
                caveats.append(
                    f"The {dataset} ensemble blends constituent run '{stem}', "
                    f"which the run-validity filter excludes from the "
                    f"leaderboard as uniform-distribution garbage. The blended "
                    f"per-question rows still include its (uniform) "
                    f"distributions, so the published ensemble score for "
                    f"{dataset} understates a clean re-blend."
                )
    return rows, caveats


def _build_ensemble_error_correlation(
    results: list[dict], results_dir: Path | None
) -> list[dict]:
    """Pairwise error correlation between each ensemble's constituent runs.

    For every dataset with a published ensemble, reads the constituent run
    files named in the ensemble's ``ensemble_sources`` and computes the
    pairwise Pearson r between the constituents' per-question JSD-vs-human
    vectors over the ensemble's common question set. JSD is each run's
    committed per-question error magnitude against the canonical human
    distribution, so r answers "do the constituents err on the same
    questions?" — the published evidence behind (or against) the ensemble
    "uncorrelated errors" framing.

    JSD survives the gated-dataset stripping (#308: ``human_distribution``
    is removed from committed files, derived per-question metrics stay), so
    this block is fully reproducible from public artifacts and the CI drift
    guard recomputes it. The sharper signed per-option residual correlation
    needs the stripped human distributions and is carried as the
    ``ensemble_signed_error_correlation`` asserted constant instead.

    Requires ``results_dir`` to resolve the constituent files; returns
    ``[]`` when it is not supplied or a constituent file is unreadable.
    """
    if results_dir is None:
        return []
    from synthbench.leaderboard import display_provider_name
    from synthbench.publish import _dedup_results

    # Mirror _build_ensemble_comparison's selection: first ensemble per
    # dataset in the deduped pool.
    ensembles: dict[str, dict] = {}
    for r in _dedup_results(results):
        cfg = r.get("config") or {}
        ds = cfg.get("dataset", "unknown")
        if cfg.get("provider", "").startswith("ensemble/") and ds not in ensembles:
            ensembles[ds] = r

    rows: list[dict] = []
    for dataset in sorted(ensembles):
        ensemble = ensembles[dataset]
        common_keys = {
            q.get("key") for q in ensemble.get("per_question") or [] if q.get("key")
        }
        if not common_keys:
            continue

        constituents: list[tuple[str, dict[str, float]]] = []
        for src in (ensemble.get("config") or {}).get("ensemble_sources", []):
            path = results_dir / src.get("file", "")
            try:
                with open(path) as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                constituents = []
                break
            jsd_by_key = {
                q["key"]: float(q["jsd"])
                for q in data.get("per_question") or []
                if q.get("key") in common_keys
                and isinstance(q.get("jsd"), (int, float))
                and not isinstance(q.get("jsd"), bool)
            }
            constituents.append(
                (display_provider_name(src.get("provider", "")), jsd_by_key)
            )
        if len(constituents) < 2:
            continue

        pairs: list[dict] = []
        for i in range(len(constituents)):
            for j in range(i + 1, len(constituents)):
                name_a, jsd_a = constituents[i]
                name_b, jsd_b = constituents[j]
                shared = sorted(set(jsd_a) & set(jsd_b))
                if len(shared) < 3:
                    continue
                try:
                    r_val = statistics.correlation(
                        [jsd_a[k] for k in shared], [jsd_b[k] for k in shared]
                    )
                except statistics.StatisticsError:
                    continue
                pairs.append(
                    {
                        "a": name_a,
                        "b": name_b,
                        "pearson_r": round(r_val, 6),
                        "n": len(shared),
                    }
                )
        if not pairs:
            continue
        rows.append(
            {
                "dataset": dataset,
                "n_questions": _effective_n(ensemble),
                "constituents": [name for name, _ in constituents],
                "pairs": pairs,
                # Mean of the published (rounded) pairwise values so the
                # arithmetic is exactly reproducible from the block itself.
                "mean_pearson_r": round(
                    statistics.mean(p["pearson_r"] for p in pairs), 6
                ),
            }
        )
    return rows


# Score components the elicitation comparison publishes per arm; deltas are
# structured − natural, computed from the rounded per-arm values so the
# published arithmetic is exact.
_ELICITATION_METRICS = ("sps", "p_dist", "p_rank", "p_refuse", "parse_failure_rate")

# Provider-string variant suffix (`` tpl=<stem>``) stripped when matching an
# elicitation-variant run back to its natural-elicitation counterpart.
_TPL_SUFFIX_RE = re.compile(r"\s+tpl=\S+")


def _parse_failure_rate(result: dict) -> float | None:
    """Parse-failure rate for a run, preferring the recorded config value.

    Falls back to ``aggregate.n_parse_failures / (n_questions * samples)``
    when the config predates the recorded rate.
    """
    cfg = result.get("config") or {}
    rate = cfg.get("parse_failure_rate")
    if isinstance(rate, (int, float)) and not isinstance(rate, bool):
        return float(rate)
    agg = result.get("aggregate") or {}
    failures = agg.get("n_parse_failures")
    samples = cfg.get("samples_per_question")
    n = _effective_n(result)
    if isinstance(failures, int) and isinstance(samples, int) and n > 0 and samples > 0:
        return failures / (n * samples)
    return None


def _elicitation_arm(result: dict) -> dict | None:
    """Recomputed per-arm metrics dict for one elicitation-comparison run."""
    components = _run_components(result)
    if components is None:
        return None
    arm = {k: round(v, 6) for k, v in components.items()}
    rate = _parse_failure_rate(result)
    if rate is not None:
        arm["parse_failure_rate"] = round(rate, 6)
    return arm


def _build_elicitation_comparison(results: list[dict]) -> list[dict]:
    """Matched-pair comparison: natural roleplay vs schema-forced elicitation.

    Pairs a run whose config carries an explicit ``elicitation`` mode (the
    ``tpl=structured`` template variant, #328) with the natural-elicitation
    run of the *identical* configuration — same base provider, dataset,
    samples_per_question, question_set_hash, temperature, and effort — so
    the only difference between the arms is the elicitation surface. Pairs
    where either arm is missing (or scored on a different question count)
    are simply not emitted.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework
    from synthbench.publish import _dedup_results, _tpl_name

    def identity(cfg: dict) -> tuple:
        return (
            _TPL_SUFFIX_RE.sub("", cfg.get("provider", "")),
            cfg.get("dataset", "unknown"),
            cfg.get("samples_per_question"),
            cfg.get("question_set_hash"),
            cfg.get("temperature"),
            cfg.get("effort"),
        )

    natural_by_identity: dict[tuple, dict] = {}
    variant_runs: list[dict] = []
    for r in _dedup_results(results):
        cfg = r.get("config") or {}
        elicitation = cfg.get("elicitation")
        if isinstance(elicitation, str) and elicitation != "natural":
            variant_runs.append(r)
        elif _tpl_name(cfg.get("prompt_template")) is None:
            natural_by_identity[identity(cfg)] = r

    rows: list[dict] = []
    for variant in variant_runs:
        v_cfg = variant.get("config") or {}
        natural = natural_by_identity.get(identity(v_cfg))
        if natural is None:
            continue
        if _effective_n(natural) != _effective_n(variant):
            continue
        natural_arm = _elicitation_arm(natural)
        variant_arm = _elicitation_arm(variant)
        if natural_arm is None or variant_arm is None:
            continue

        n_cfg = natural.get("config") or {}
        detector_versions = {
            n_cfg.get("refusal_detector_version"),
            v_cfg.get("refusal_detector_version"),
        }
        provider = n_cfg.get("provider", "")
        rows.append(
            {
                "model": display_provider_name(provider),
                "framework": provider_framework(provider),
                "dataset": v_cfg.get("dataset", "unknown"),
                "elicitation": v_cfg.get("elicitation"),
                "template": _tpl_name(v_cfg.get("prompt_template")),
                "n_questions": _effective_n(variant),
                "samples_per_question": v_cfg.get("samples_per_question"),
                "refusal_detector_version": (
                    detector_versions.pop() if len(detector_versions) == 1 else None
                ),
                "natural": natural_arm,
                "structured": variant_arm,
                # structured − natural, from the rounded per-arm values so
                # the published delta arithmetic is exact.
                "delta": {
                    m: round(variant_arm[m] - natural_arm[m], 6)
                    for m in _ELICITATION_METRICS
                    if m in variant_arm and m in natural_arm
                },
            }
        )
    rows.sort(key=lambda row: (row["dataset"], row["model"]))
    return rows


# Option labels that constitute an EXPLICIT nonresponse when selected —
# "Don't know" variants, refusals, and no-answer/no-opinion buckets. The
# per-question refusal rate (parsed refusal text) is added on top, so the
# metric captures total nonresponse mass regardless of whether the model
# sidestepped via a legitimate option or via refusal prose.
_NONRESPONSE_OPTION_RE = re.compile(
    r"don'?t know|no answer|refused?|not sure|no opinion|cannot choose|"
    r"undecided|prefer not to",
    re.IGNORECASE,
)

# Minimum share of a run's questions that must still carry a
# human_distribution for the nonresponse-fidelity comparison to be
# computable. Gated datasets are committed stripped of human_distribution
# (#308), so this effectively restricts the block to full-tier datasets
# (GSS, NTIA) where the comparison is reproducible from the artifacts.
_NONRESPONSE_MIN_HUMAN_COVERAGE = 0.9


def _nonresponse_mass(dist: dict | None, refusal_rate: float) -> float:
    """Explicit nonresponse-option mass plus parsed-refusal mass."""
    dist = dist or {}
    mass = sum(
        float(v)
        for k, v in dist.items()
        if isinstance(k, str) and _NONRESPONSE_OPTION_RE.search(k)
    )
    return mass + float(refusal_rate or 0.0)


def _build_nonresponse_fidelity(results: list[dict]) -> list[dict]:
    """Per-run nonresponse fidelity: |model DK+refusal mass − human's|.

    For each deduped, non-baseline run whose per-question rows still carry
    ``human_distribution``, computes the mean absolute gap between the
    model's explicit-nonresponse mass (DK-style option mass + parsed
    refusal rate) and the human survey's, plus the items where the model
    most over-selects nonresponse. Rows sort worst-first.
    """
    from synthbench.leaderboard import display_provider_name, provider_framework
    from synthbench.publish import _dedup_results, _tpl_name

    rows: list[dict] = []
    for r in _dedup_results(results):
        cfg = r.get("config") or {}
        provider = cfg.get("provider", "")
        fw = provider_framework(provider)
        if fw == "baseline" or provider.startswith("ensemble/"):
            continue
        per_q = r.get("per_question") or []
        if not per_q:
            continue
        with_human = [q for q in per_q if q.get("human_distribution")]
        if len(with_human) < _NONRESPONSE_MIN_HUMAN_COVERAGE * len(per_q):
            continue

        items = []
        for q in with_human:
            model_mass = _nonresponse_mass(
                q.get("model_distribution"), q.get("model_refusal_rate", 0.0)
            )
            human_mass = _nonresponse_mass(
                q.get("human_distribution"), q.get("human_refusal_rate", 0.0)
            )
            items.append(
                {
                    "key": q.get("key", ""),
                    "model_mass": round(model_mass, 6),
                    "human_mass": round(human_mass, 6),
                    "gap": round(model_mass - human_mass, 6),
                }
            )

        mean_abs_gap = statistics.mean(abs(i["gap"]) for i in items)
        top = sorted(items, key=lambda i: -i["gap"])[:5]
        rows.append(
            {
                "provider": display_provider_name(provider),
                "framework": fw,
                # Template/elicitation variant (None for the default prompt) —
                # distinguishes e.g. natural vs tpl=structured rows.
                "template": _tpl_name(cfg.get("prompt_template")),
                "dataset": cfg.get("dataset", "unknown"),
                "n_questions": len(items),
                "mean_abs_nonresponse_gap": round(mean_abs_gap, 6),
                "mean_model_nonresponse_mass": round(
                    statistics.mean(i["model_mass"] for i in items), 6
                ),
                "mean_human_nonresponse_mass": round(
                    statistics.mean(i["human_mass"] for i in items), 6
                ),
                "top_overselected": [i for i in top if i["gap"] > 0],
            }
        )
    rows.sort(key=lambda row: -row["mean_abs_nonresponse_gap"])
    return rows


def _build_sensitive_topic_sidestepping(nonresponse_rows: list[dict]) -> dict | None:
    """Findings entry: safety-aligned sidestepping via explicit DK options.

    Derived from the worst raw-framework nonresponse row (currently
    Gemini 2.5 Flash on GSS): a model that essentially never refuses in
    prose still concentrates response mass on explicit "don't know"-style
    options for sensitive items — religion (POSTLIFE, GOD), gender roles
    (FEPRESCH), race (NATRACE), welfare (NATFARE) — at rates far above the
    human survey. This is genuine option selection, not a parsing artifact:
    the raw responses ARE the DK option strings.
    """
    raw_rows = [r for r in nonresponse_rows if r["framework"] == "raw"]
    if not raw_rows:
        return None
    worst = raw_rows[0]  # rows are sorted worst-first
    return {
        "headline": (
            "Safety-aligned models over-select explicit nonresponse options "
            "on sensitive items"
        ),
        "provider": worst["provider"],
        "dataset": worst["dataset"],
        "n_questions": worst["n_questions"],
        "mean_model_nonresponse_mass": worst["mean_model_nonresponse_mass"],
        "mean_human_nonresponse_mass": worst["mean_human_nonresponse_mass"],
        "items": worst["top_overselected"],
        "note": (
            "Nonresponse mass concentrates on religion, gender-role, race, "
            "and welfare topics; the model selects a legitimate "
            "'don't know'-style option rather than refusing in prose, so "
            "the sidestepping is invisible to refusal-rate metrics and "
            "only surfaces in the option distribution itself."
        ),
    }


def _build_conditioning(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Aggregate per-group conditioning replications from demographic_breakdown.

    Returns ``(site_rows, extended_rows)`` — site rows cover the attributes
    the findings page charts (POLPARTY / INCOME / EDUCATION); extended rows
    cover every other measured attribute.
    """
    # A cell keys measurements by their exact (p_dist, p_cond) pair: some
    # runs re-publish an identical demographic_breakdown block verbatim, and
    # counting the copy as an independent replication would deflate the std
    # to 0. Genuinely independent replications never collide on both floats.
    cells: dict[tuple[str, str], set[tuple[float, float]]] = {}
    for r in results:
        breakdown = r.get("demographic_breakdown") or {}
        for attribute, groups in breakdown.items():
            if not isinstance(groups, list):
                continue
            for g in groups:
                p_dist, p_cond = g.get("p_dist"), g.get("p_cond")
                if not isinstance(p_dist, (int, float)) or not isinstance(
                    p_cond, (int, float)
                ):
                    continue
                cells.setdefault((attribute, g.get("group", "")), set()).add(
                    (float(p_dist), float(p_cond))
                )

    site_rows: list[dict] = []
    extended_rows: list[dict] = []
    for (attribute, group_raw), pair_set in sorted(
        cells.items(),
        key=lambda kv: (kv[0][0], -statistics.mean(p for _, p in kv[1])),
    ):
        pairs = sorted(pair_set)
        p_dist_mean, _ = _mean_std([d for d, _ in pairs])
        p_cond_mean, p_cond_std = _mean_std([p for _, p in pairs])
        row = {
            "attribute": attribute,
            "group": _GROUP_DISPLAY.get(group_raw, group_raw),
            "group_raw": group_raw,
            "p_dist": p_dist_mean,
            "p_cond": p_cond_mean,
            "n_replications": len(pairs),
        }
        if p_cond_std is not None:
            row["p_cond_std"] = p_cond_std
        if attribute in _CONDITIONING_SITE_ATTRIBUTES:
            site_rows.append(row)
        else:
            extended_rows.append(row)

    order = {a: i for i, a in enumerate(_CONDITIONING_SITE_ATTRIBUTES)}
    site_rows.sort(key=lambda r: (order[r["attribute"]], -r["p_cond"]))
    return site_rows, extended_rows


def _conditioning_ratio(rows: list[dict], attribute: str) -> float | None:
    """max/min mean-p_cond ratio between the two groups of one attribute."""
    vals = [r["p_cond"] for r in rows if r["attribute"] == attribute]
    if len(vals) < 2 or min(vals) <= 0:
        return None
    return round(max(vals) / min(vals), 1)


def _build_lever_hierarchy(
    ensemble_rows: list[dict],
    sweep: list[dict],
    conditioning: list[dict],
    templates: list[dict],
) -> list[dict]:
    """Effect-size ranges (SPS points, x100) computed from the other blocks."""
    levers: list[dict] = []

    improvements = [r["improvement"] * 100 for r in ensemble_rows]
    if improvements:
        levers.append(
            {
                "name": "Ensemble blending",
                "effect_min": round(min(improvements), 1),
                "effect_max": round(max(improvements), 1),
                "cost": "zero",
                "status": "done",
            }
        )

    per_model: dict[str, list[float]] = {}
    for p in sweep:
        per_model.setdefault(p["model"], []).append(p["sps"])
    deltas = [(max(v) - min(v)) * 100 for v in per_model.values() if len(v) > 1]
    if deltas:
        levers.append(
            {
                "name": "Per-model optimal temperature",
                "effect_min": round(min(deltas), 1),
                "effect_max": round(max(deltas), 1),
                "cost": "low",
                "status": "actionable",
            }
        )

    cond_effects = [r["p_cond"] * 100 for r in conditioning]
    if cond_effects:
        levers.append(
            {
                "name": "Demographic conditioning",
                "effect_min": round(min(cond_effects), 1),
                "effect_max": round(max(cond_effects), 1),
                "cost": "moderate",
                "status": "scientific",
            }
        )

    if templates:
        best, rest = templates[0], templates[1:]
        note = None
        if rest:
            advantage = (best["sps"] - max(t["sps"] for t in rest)) * 100
            note = (
                f"'{best['template']}' template already optimal "
                f"(+{advantage:.1f} pts over the best alternative); no "
                f"further gain available from this lever."
            )
        lever = {
            "name": "Persona template",
            "effect_min": 0.0,
            "effect_max": 0.0,
            "cost": "zero",
            "status": "done",
        }
        if note:
            lever["note"] = note
        levers.append(lever)

    return levers


def build_findings(
    results: list[dict],
    excluded_run_ids: set[str] | None = None,
    results_dir: Path | None = None,
) -> dict:
    """Compute the published findings block from loaded (valid) run results.

    ``results`` is the post-validity-filter run pool (pre-dedup — replicate
    runs are required for sweep/conditioning statistics). ``excluded_run_ids``
    lets ensemble caveats detect blends built on filtered constituents.
    ``results_dir`` (the directory the results were loaded from) lets the
    ensemble error-correlation block resolve the exact constituent files
    named in ``ensemble_sources``; without it that block is empty.
    """
    excluded_run_ids = excluded_run_ids or set()

    temperature_sweep = _build_temperature_sweep(results)
    template_comparison = _build_template_comparison(results)
    elicitation_comparison = _build_elicitation_comparison(results)
    ensemble_comparison, caveats = _build_ensemble_comparison(results, excluded_run_ids)
    ensemble_error_correlation = _build_ensemble_error_correlation(results, results_dir)
    conditioning_results, conditioning_extended = _build_conditioning(results)
    nonresponse_fidelity = _build_nonresponse_fidelity(results)
    sensitive_topic_sidestepping = _build_sensitive_topic_sidestepping(
        nonresponse_fidelity
    )
    lever_hierarchy = _build_lever_hierarchy(
        ensemble_comparison,
        temperature_sweep,
        conditioning_results,
        template_comparison,
    )

    comparison_sets = {
        "ensemble_comparison": (
            "best_single = highest recomputed-SPS non-ensemble, non-baseline "
            "leaderboard row (raw or product framework) evaluated on at least "
            "as many questions as the ensemble, after per-(model, framework, "
            "dataset) dedup; random_baseline = recomputed SPS of the "
            "random-baseline run for the same dataset (n in "
            "random_baseline_n)."
        ),
        "ensemble_error_correlation": (
            "For each dataset's published ensemble: pairwise Pearson r "
            "between the constituent runs' committed per-question JSD "
            "vectors (each run's error magnitude vs the canonical human "
            "distribution), over the ensemble's common question set, read "
            "from the exact files named in ensemble_sources. Measures "
            "whether constituents err on the same questions. Signed "
            "per-option residual correlations need the stripped "
            "human_distribution fields (#308) and are carried as the "
            "ensemble_signed_error_correlation asserted constant."
        ),
        "temperature_sweep": (
            "OpinionsQA sweep-tagged SynthPanel runs (' t=' provider suffix); "
            "mean/std of recomputed SPS across the n_runs replications per "
            "(model, temperature) cell."
        ),
        "conditioning_results": (
            "Per-group conditioned SubPOP evaluations (Haiku 4.5, t=0.85); "
            "mean p_dist / p_cond across n_replications runs carrying a "
            "demographic_breakdown for the group."
        ),
        "template_comparison": (
            "SubPOP persona-template variant runs (Haiku 4.5, t=0.85, 100 "
            "questions); mean/std of recomputed SPS across n_runs."
        ),
        "elicitation_comparison": (
            "Matched pairs of deduped runs differing only in elicitation "
            "mode: a run whose config carries an explicit elicitation "
            "template variant (e.g. tpl=structured, schema-forced capture) "
            "vs the natural-elicitation run of the identical configuration "
            "(same base provider, dataset, samples_per_question, "
            "question_set_hash, temperature, effort, and question count). "
            "All scores recomputed from per-question rows; deltas are "
            "structured minus natural."
        ),
        "nonresponse_fidelity": (
            "Per deduped non-baseline run whose committed per-question rows "
            "still carry human_distribution (full-tier datasets; gated files "
            "are stripped per #308): mean |model explicit-nonresponse mass "
            "(DK-style option mass + parsed refusal rate) - human's|, plus "
            "the five items with the largest model over-selection."
        ),
    }

    return {
        "sps_convention": SPS_CONVENTION,
        "generated_from": "leaderboard-results/ (recomputed per-question rows)",
        "temperature_sweep": temperature_sweep,
        "ensemble_comparison": ensemble_comparison,
        "ensemble_error_correlation": ensemble_error_correlation,
        "conditioning_results": conditioning_results,
        "conditioning_extended": conditioning_extended,
        "template_comparison": template_comparison,
        "elicitation_comparison": elicitation_comparison,
        "nonresponse_fidelity": nonresponse_fidelity,
        "sensitive_topic_sidestepping": sensitive_topic_sidestepping,
        "lever_hierarchy": lever_hierarchy,
        "comparison_sets": comparison_sets,
        "asserted_constants": ASSERTED_CONSTANTS,
        "caveats": caveats,
    }
