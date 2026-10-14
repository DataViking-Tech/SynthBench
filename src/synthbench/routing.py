"""Build ``routing.json``: the best system per (use-case slice, topic).

Althing reads this file to pick a model (or blend) for a study. See
``docs/routing-json-api.md`` for the contract. In short:

* Slices group datasets by who is being simulated (:data:`SLICES`).
* Topics are the routing taxonomy in :mod:`synthbench.topics`, plus
  ``"all"``.
* Candidates are the current leaderboard rows (same dedup as
  ``publish-data``), singles and ensembles, without baselines or
  template / temperature / persona-pack / harness / effort variants. A
  candidate must cover every dataset in the slice.
* Each candidate's score is the SynthBench Index on the slice's questions
  in that topic. Per dataset: full SPS (p_dist, p_rank, p_refuse) on those
  questions, rescaled as ``100 * (SPS - SPS_random) / (ceiling - SPS_random)``
  with the random baseline scored on the same questions. The slice value is
  the question-weighted mean over datasets.
* ``ci`` and ``confident`` come from a paired bootstrap over questions
  (fixed seed): every candidate and the random baseline are resampled with
  the same question draws.
"""

from __future__ import annotations

import json
import logging
import warnings
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

API_NAME = "synthbench-routing"
API_VERSION = "1.0.0"
CONTRACT_URL = (
    "https://github.com/DataViking-Tech/SynthBench/blob/main/docs/routing-json-api.md"
)

SLICES: tuple[dict, ...] = (
    {
        "id": "us-general",
        "label": "US general public",
        "datasets": ["opinionsqa", "gss"],
    },
    {
        "id": "us-subgroups",
        "label": "US demographic subgroups",
        "datasets": ["subpop"],
    },
    {
        "id": "cross-national",
        "label": "Respondents outside the US",
        "datasets": ["globalopinionqa"],
    },
)

MIN_QUESTIONS = 30
MAX_CANDIDATES = 12
N_BOOTSTRAP = 2000
SEED = 20261014

# Split-half human ceilings (overall SPS). Mirrors site/src/lib/ceilings.ts,
# which the site's Index uses; tests/test_routing.py checks they agree.
DATASET_CEILINGS: dict[str, float] = {
    "opinionsqa": 0.999518,
    "subpop": 0.995346,
    "globalopinionqa": 0.997219,
    "gss": 0.998784,
    "ntia": 0.999973,
}

RANDOM_PROVIDER = "random-baseline"


# ---------------------------------------------------------------------------
# Candidate systems
# ---------------------------------------------------------------------------


def _is_variant(cfg: dict) -> bool:
    """Template / temperature / persona-pack / harness / effort variants."""
    return any(
        cfg.get(k) is not None
        for k in ("prompt_template", "temperature", "persona_pack", "harness", "effort")
    )


def _usable(q: dict) -> bool:
    def num(x: object) -> bool:
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    return num(q.get("jsd")) and num(q.get("kendall_tau"))


def _members(r: dict) -> list[dict]:
    from synthbench.config_id import runnable_ids
    from synthbench.leaderboard import provider_framework

    cfg = r.get("config") or {}
    provider = cfg.get("provider", "")
    sources = cfg.get("ensemble_sources") or []
    if not provider.startswith("ensemble/") or not sources:
        return [
            {
                "model_id": runnable_ids(provider)[1],
                "framework": provider_framework(provider),
                "weight": 1.0,
            }
        ]
    weights = [s.get("weight") for s in sources]
    if all(isinstance(w, (int, float)) and w > 0 for w in weights):
        total = float(sum(weights))
        norm = [float(w) / total for w in weights]
    else:
        norm = [1.0 / len(sources)] * len(sources)
    return [
        {
            "model_id": runnable_ids(s.get("provider", ""))[1],
            "framework": provider_framework(s.get("provider", "")),
            "weight": round(w, 6),
        }
        for s, w in zip(sources, norm)
    ]


def _collect_systems(
    deduped: list[dict],
    datasets: set[str],
    results_by_provider_ds: dict[tuple[str, str], dict],
) -> tuple[dict[str, dict], dict[str, dict[str, dict]]]:
    """Group deduped rows into cross-dataset systems.

    Returns ``(systems, random_rows)``: ``systems[group]`` carries the
    candidate metadata and ``rows[dataset] = {key: per_question_row}``;
    ``random_rows[dataset]`` is the random baseline's rows.
    """
    from synthbench.config_id import build_config_id
    from synthbench.leaderboard import display_provider_name, provider_framework
    from synthbench.publish import _build_entry

    systems: dict[str, dict] = {}
    random_rows: dict[str, dict[str, dict]] = {}
    for r in sorted(
        deduped,
        key=lambda x: (
            (x.get("config") or {}).get("dataset", ""),
            (x.get("config") or {}).get("provider", ""),
        ),
    ):
        cfg = r.get("config") or {}
        ds = cfg.get("dataset", "")
        if ds not in datasets:
            continue
        provider = cfg.get("provider", "")
        rows = {
            q["key"]: q
            for q in r.get("per_question") or []
            if isinstance(q, dict) and q.get("key") and _usable(q)
        }
        if provider == RANDOM_PROVIDER:
            random_rows[ds] = rows
            continue
        framework = provider_framework(provider)
        if framework == "baseline" or _is_variant(cfg):
            continue
        label = display_provider_name(provider)
        group = f"{label}|{framework}"
        system = systems.get(group)
        if system is None:
            members = _members(r)
            system = {
                "config_id": build_config_id(provider)[0],
                "label": label,
                "kind": "blend" if provider.startswith("ensemble/") else "single",
                "members": members,
                "althing_native": all(m["framework"] == "product" for m in members),
                "rows": {},
                "cost_per_100q": {},
            }
            systems[group] = system
        system["rows"][ds] = rows
        cost = _build_entry(r, 0, results_by_provider_ds).get("cost_per_100q")
        system["cost_per_100q"][ds] = cost
    return systems, random_rows


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _sps_matrix(jsd: np.ndarray, tau: np.ndarray, rdiff: np.ndarray) -> np.ndarray:
    """Full SPS over the last axis (questions); rdiff NaN = no refusal data.

    Matches :func:`synthbench.recompute.recompute_aggregates`: p_refuse is
    averaged over rows that carry both refusal rates, and drops out of the
    composite when none do.
    """
    p_dist = 1.0 - jsd.mean(axis=-1)
    p_rank = (1.0 + tau.mean(axis=-1)) / 2.0
    with warnings.catch_warnings():
        # All-NaN rows (no refusal data) are expected; they fall back below.
        warnings.simplefilter("ignore", RuntimeWarning)
        mean_rdiff = np.nanmean(rdiff, axis=-1)
    p_refuse = np.clip(1.0 - mean_rdiff, 0.0, 1.0)
    has = np.isfinite(p_refuse)
    return np.where(
        has,
        (p_dist + p_rank + np.nan_to_num(p_refuse)) / 3.0,
        (p_dist + p_rank) / 2.0,
    )


def _arrays(
    rows_list: list[dict[str, dict]], keys: list[str]
) -> tuple[np.ndarray, ...]:
    jsd = np.array([[rows[k]["jsd"] for k in keys] for rows in rows_list], dtype=float)
    tau = np.array(
        [[rows[k]["kendall_tau"] for k in keys] for rows in rows_list], dtype=float
    )

    def rdiff(q: dict) -> float:
        m, h = q.get("model_refusal_rate"), q.get("human_refusal_rate")
        if isinstance(m, (int, float)) and isinstance(h, (int, float)):
            return abs(float(m) - float(h))
        return float("nan")

    rd = np.array([[rdiff(rows[k]) for k in keys] for rows in rows_list], dtype=float)
    return jsd, tau, rd


def _score_route(
    candidates: list[dict],
    random_rows: dict[str, dict[str, dict]],
    keys_by_ds: dict[str, list[str]],
    seed: int,
    n_bootstrap: int = N_BOOTSTRAP,
) -> tuple[np.ndarray, np.ndarray]:
    """Index per candidate: ``(point[C], bootstrap[C, B])``."""
    rng = np.random.default_rng(seed)
    total = sum(len(k) for k in keys_by_ds.values())
    point = np.zeros(len(candidates))
    boot = np.zeros((len(candidates), n_bootstrap))
    for ds, keys in keys_by_ds.items():
        if not keys:
            continue
        rows_list = [c["rows"][ds] for c in candidates] + [random_rows[ds]]
        jsd, tau, rd = _arrays(rows_list, keys)
        ceiling = DATASET_CEILINGS.get(ds, 1.0)

        sps = _sps_matrix(jsd, tau, rd)  # [C+1]
        rand = sps[-1]
        point += len(keys) * 100.0 * (sps[:-1] - rand) / (ceiling - rand)

        idx = rng.integers(0, len(keys), size=(n_bootstrap, len(keys)))
        sps_b = _sps_matrix(jsd[:, idx], tau[:, idx], rd[:, idx])  # [C+1, B]
        rand_b = sps_b[-1]
        boot += len(keys) * 100.0 * (sps_b[:-1] - rand_b) / (ceiling - rand_b)
    return point / total, boot / total


def _route_keys(
    slice_datasets: list[str],
    candidates: list[dict],
    random_rows: dict[str, dict[str, dict]],
    topic_of: dict[tuple[str, str], str | None],
    topic: str,
) -> dict[str, list[str]]:
    """Questions every candidate and the random baseline answered, per dataset."""
    out: dict[str, list[str]] = {}
    for ds in slice_datasets:
        common = set(random_rows.get(ds, {}))
        for c in candidates:
            common &= set(c["rows"][ds])
        out[ds] = sorted(
            k for k in common if topic == "all" or topic_of.get((ds, k)) == topic
        )
    return out


def _round_ci(lo: float, hi: float) -> list[float]:
    return [round(float(lo), 1), round(float(hi), 1)]


def _cost(system: dict, keys_by_ds: dict[str, list[str]]) -> float | None:
    total = 0.0
    weight = 0
    for ds, keys in keys_by_ds.items():
        cost = system["cost_per_100q"].get(ds)
        if cost is None:
            return None
        total += len(keys) * float(cost)
        weight += len(keys)
    return round(total / weight, 4) if weight else None


def _build_route(
    slice_def: dict,
    topic: str,
    candidates: list[dict],
    random_rows: dict[str, dict[str, dict]],
    topic_of: dict[tuple[str, str], str | None],
    n_bootstrap: int,
    min_questions: int,
) -> dict | None:
    datasets = slice_def["datasets"]
    keys_by_ds = _route_keys(datasets, candidates, random_rows, topic_of, topic)
    n_questions = sum(len(k) for k in keys_by_ds.values())
    if n_questions == 0 or not candidates:
        return None
    seed = SEED + zlib.crc32(f"{slice_def['id']}|{topic}".encode())
    point, boot = _score_route(candidates, random_rows, keys_by_ds, seed, n_bootstrap)

    order = sorted(
        range(len(candidates)),
        key=lambda i: (-point[i], candidates[i]["config_id"]),
    )
    best = order[0]
    runner_up = order[1] if len(order) > 1 else None
    confident = False
    if runner_up is not None and n_questions >= min_questions:
        diff = boot[best] - boot[runner_up]
        lo, hi = np.percentile(diff, [2.5, 97.5])
        confident = bool(lo > 0 or hi < 0)

    best_althing = next((i for i in order if candidates[i]["althing_native"]), None)
    best_single_althing = next(
        (
            i
            for i in order
            if candidates[i]["althing_native"] and candidates[i]["kind"] == "single"
        ),
        None,
    )

    # At most MAX_CANDIDATES, but always list the systems the best_* fields
    # point at so a consumer can resolve them.
    top = order[:MAX_CANDIDATES]
    musts = [
        i
        for i in dict.fromkeys((best_althing, best_single_althing))
        if i is not None and i not in top
    ]
    shown = sorted(order[: MAX_CANDIDATES - len(musts)] + musts, key=order.index)

    def cid(i: int | None) -> str | None:
        return candidates[i]["config_id"] if i is not None else None

    out_candidates = []
    for i in shown:
        c = candidates[i]
        lo, hi = np.percentile(boot[i], [2.5, 97.5])
        out_candidates.append(
            {
                "config_id": c["config_id"],
                "label": c["label"],
                "kind": c["kind"],
                "althing_native": c["althing_native"],
                "members": c["members"],
                "index": round(float(point[i]), 1),
                "ci": _round_ci(lo, hi),
                "n": n_questions,
                "cost_per_100q": _cost(c, keys_by_ds),
            }
        )

    return {
        "slice": slice_def["id"],
        "topic": topic,
        "n_questions": n_questions,
        "n_by_dataset": {ds: len(k) for ds, k in keys_by_ds.items()},
        "confident": confident,
        "best": cid(best),
        "best_althing": cid(best_althing),
        "best_single_althing": cid(best_single_althing),
        "candidates": out_candidates,
    }


def build_routing(
    results: list[dict],
    *,
    extra_results: list[dict] | None = None,
    generated_at: str | None = None,
    n_bootstrap: int = N_BOOTSTRAP,
    min_questions: int = MIN_QUESTIONS,
) -> dict:
    """Build the ``routing.json`` payload from validity-filtered results.

    ``results`` are the valid runs ``publish-data`` ranks (dedup happens
    here, with the same rule). ``extra_results`` (all loaded runs, including
    validity-excluded ones) only fill ensemble cost lookups, as in
    ``publish-data``.
    """
    from synthbench.publish import _dedup_results
    from synthbench.topics import TOPIC_IDS, taxonomy_dict, topic_for

    deduped = _dedup_results(results)
    results_by_provider_ds: dict[tuple[str, str], dict] = {}
    for r in deduped:
        cfg = r.get("config") or {}
        results_by_provider_ds[(cfg.get("provider", ""), cfg.get("dataset", ""))] = r
    for r in extra_results or []:
        cfg = r.get("config") or {}
        results_by_provider_ds.setdefault(
            (cfg.get("provider", ""), cfg.get("dataset", "")), r
        )

    all_datasets = {ds for s in SLICES for ds in s["datasets"]}
    systems, random_rows = _collect_systems(
        deduped, all_datasets, results_by_provider_ds
    )

    topic_of: dict[tuple[str, str], str | None] = {}
    for system in [*systems.values(), {"rows": random_rows}]:
        for ds, rows in system["rows"].items():
            for key, q in rows.items():
                if (ds, key) not in topic_of:
                    topic_of[(ds, key)] = topic_for(ds, key, q.get("text"))

    routes: list[dict] = []
    for slice_def in SLICES:
        datasets = slice_def["datasets"]
        if any(ds not in random_rows for ds in datasets):
            logger.warning(
                "routing: slice %s skipped, no random baseline for %s",
                slice_def["id"],
                [ds for ds in datasets if ds not in random_rows],
            )
            continue
        candidates = sorted(
            (s for s in systems.values() if all(ds in s["rows"] for ds in datasets)),
            key=lambda s: s["config_id"],
        )
        for topic in ("all", *TOPIC_IDS):
            route = _build_route(
                slice_def,
                topic,
                candidates,
                random_rows,
                topic_of,
                n_bootstrap,
                min_questions,
            )
            if route is not None:
                routes.append(route)

    return {
        "api": {
            "name": API_NAME,
            "version": API_VERSION,
            "contract_url": CONTRACT_URL,
        },
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "taxonomy": taxonomy_dict(),
        "slices": [dict(s) for s in SLICES],
        "min_questions": min_questions,
        "routes": routes,
    }


def load_results(results_dir: Path) -> tuple[list[dict], list[dict]]:
    """``(valid_results, all_loaded)`` from a results directory, as publish loads them."""
    from synthbench.publish import _partition_valid_runs, _run_id_from_path

    loaded: list[tuple[str, dict]] = []
    for jf in sorted(Path(results_dir).glob("*.json")):
        try:
            with open(jf, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("benchmark") == "synthbench":
            loaded.append((_run_id_from_path(jf), data))
    valid, _excluded = _partition_valid_runs(loaded)
    return [d for _, d in valid], [d for _, d in loaded]


def write_routing(payload: dict, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return output_path


def publish_routing(results_dir: Path, output_path: Path) -> Path:
    """Load ``results_dir``, build ``routing.json`` and write it to ``output_path``."""
    results, loaded = load_results(results_dir)
    if not results:
        raise ValueError(f"No valid SynthBench result files found in {results_dir}")
    return write_routing(build_routing(results, extra_results=loaded), output_path)
