"""Offline analysis of private campaign journals; never emits survey answers/text.

Only fully observed question cells enter headline scores. Prefix estimates are
separate, explicitly labeled views, never replacements for missing full cells.
Question-level paired inference averages replicates before bootstrapping.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
import math
import os
from pathlib import Path
from statistics import mean, median

from synthbench.datasets.base import Question
from synthbench.metrics import synthbench_parity_score
from synthbench.runner import _score_question
from synthbench.stats import bootstrap_ci

METRICS = ("sps", "p_dist", "p_rank", "p_refuse")
PREFIXES = (10, 20, 30, 60, 100, 150)
CONFIG_FIELDS = ("dataset", "model", "provider", "elicitation", "persona_pack")


def _configuration(task):
    return {
        **{key: task.get(key) for key in CONFIG_FIELDS},
        "elicitation": task.get("elicitation", "natural"),
        "samples_per_question": task.get("samples_per_question", 30),
    }


def _config_key(task):
    return json.dumps(_configuration(task), sort_keys=True)


def _number(value):
    if value is None:
        return None
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("Journal has invalid cost or latency")
    return result


def _latencies(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return {
            "count": 0,
            "mean_seconds": None,
            "p50_seconds": None,
            "p95_seconds": None,
        }
    return {
        "count": len(values),
        "mean_seconds": mean(values),
        "p50_seconds": median(values),
        "p95_seconds": values[max(0, math.ceil(0.95 * len(values)) - 1)],
    }


def _billing(reservations, attempts):
    accounted = 0.0
    reported = {"gateway_usd": [], "upstream_usd": [], "provider_reported_usd": []}
    sources = Counter()
    elapsed = []
    for attempt_id, reservation in reservations.items():
        row = attempts.get(attempt_id)
        if row is None:
            accounted += _number(reservation["reserved_usd"])
            sources["unsettled-reservation"] += 1
            continue
        accounted += _number(row["accounted_usd"])
        sources[row.get("cost_source", "unknown")] += 1
        elapsed.append(_number(row.get("elapsed_seconds")))
        usage = row.get("usage") or {}
        gateway = usage.get("cost", usage.get("total_cost"))
        upstream = (usage.get("cost_details") or {}).get(
            "upstream_inference_cost", usage.get("upstream_inference_cost")
        )
        for key, value in (
            ("gateway_usd", gateway),
            ("upstream_usd", upstream),
            ("provider_reported_usd", usage.get("provider_reported_cost")),
        ):
            if value is not None:
                reported[key].append(_number(value))
    return {
        "attempt_count": len(reservations),
        "unsettled_attempt_count": len(reservations.keys() - attempts.keys()),
        "accounted_usd": accounted,
        "reported_costs": {
            key: {
                "usd": sum(values) if values else None,
                "attempts_with_evidence": len(values),
            }
            for key, values in reported.items()
        },
        "cost_sources": dict(sources),
        "attempt_latency": _latencies(elapsed),
    }


def _cell_score(question, rows):
    n = len(rows)
    responses = [row["response"] for row in rows]
    refused = sum(bool(row.get("refusal")) for row in responses)
    selected = [
        row.get("selected_option")
        for row in responses
        if not row.get("refusal") and row.get("selected_option") in question.options
    ]
    invalid = n - refused - len(selected)
    result = {
        "n_completed": n,
        "n_valid_answers": len(selected),
        "n_refusals": refused,
        "n_parse_failures": invalid,
        "refusal_rate": refused / n,
        "parse_failure_rate": invalid / n,
        "scores": None,
        "score_unavailable_reason": None,
    }
    if not selected:
        result["score_unavailable_reason"] = "no_valid_answers"
        return result
    if question.answer_withheld or not question.human_distribution:
        result["score_unavailable_reason"] = "answer_key_unavailable"
        return result
    counts = Counter(selected)
    model = {option: counts[option] / len(selected) for option in question.options}
    human_refusal, jsd, tau, _parity = _score_question(question, model)
    # Runner denominator excludes parse failures but includes refusals.
    refusal_denominator = len(selected) + refused
    scores = {
        "p_dist": 1 - jsd,
        "p_rank": (1 + tau) / 2,
        "p_refuse": 1 - abs(refused / refusal_denominator - human_refusal),
    }
    result["scores"] = {"sps": synthbench_parity_score(scores), **scores}
    return result


def _summary(cells):
    scored = [cell for cell in cells if cell.get("scores") is not None]
    complete = [cell for cell in cells if cell["complete"]]
    return {
        "n_question_cells": len(cells),
        "n_complete_cells": len(complete),
        "n_scored_cells": len(scored),
        "n_distinct_scored_questions": len({cell["question_key"] for cell in scored}),
        "scores": {
            metric: mean(cell["scores"][metric] for cell in scored)
            for metric in METRICS
        }
        if scored
        else None,
        "refusal_rate": sum(cell.get("n_refusals", 0) for cell in complete)
        / sum(cell["n_completed"] for cell in complete)
        if complete
        else None,
        "parse_failure_rate": sum(cell.get("n_parse_failures", 0) for cell in complete)
        / sum(cell["n_completed"] for cell in complete)
        if complete
        else None,
    }


def _paired(configurations, resamples):
    contrasts, skipped = [], []
    for left, right in combinations(configurations, 2):
        a, b = left["config"], right["config"]
        if a["dataset"] != b["dataset"]:
            continue
        cells_a = {(c["question_key"], c["replicate"]): c for c in left["questions"]}
        cells_b = {(c["question_key"], c["replicate"]): c for c in right["questions"]}
        pair = {
            "left": left["id"],
            "right": right["id"],
            "direction": "right-minus-left",
        }
        if (
            a["samples_per_question"] != b["samples_per_question"]
            or cells_a.keys() != cells_b.keys()
            or not cells_a
            or any(not c["complete"] for c in [*cells_a.values(), *cells_b.values()])
        ):
            skipped.append(
                {
                    **pair,
                    "reason": "question_replicate_sample_coverage_not_identical_and_complete",
                }
            )
            continue
        if any(c.get("scores") is None for c in [*cells_a.values(), *cells_b.values()]):
            skipped.append(
                {
                    **pair,
                    "reason": "unscorable_cells_no_paired_estimate",
                    "unscorable_cells_left": sum(
                        c.get("scores") is None for c in cells_a.values()
                    ),
                    "unscorable_cells_right": sum(
                        c.get("scores") is None for c in cells_b.values()
                    ),
                }
            )
            continue
        question_diffs = defaultdict(lambda: defaultdict(list))
        for key in sorted(cells_a):
            for metric in METRICS:
                question_diffs[key[0]][metric].append(
                    cells_b[key]["scores"][metric] - cells_a[key]["scores"][metric]
                )
        metrics = {}
        for metric in METRICS:
            values = [mean(diffs[metric]) for diffs in question_diffs.values()]
            estimate = mean(values)
            ci = None
            if len(values) >= 5:
                interval = bootstrap_ci(values, mean, n_resamples=resamples, seed=42)
                ci = [interval.ci_lower, interval.ci_upper]
            metrics[metric] = {"delta": estimate, "ci95": ci}
        contrasts.append(
            {
                **pair,
                "n_questions": len(question_diffs),
                "n_replicate_cells": len(cells_a),
                "bootstrap_unit": "question_with_replicates_averaged",
                "confidence": 0.95,
                "bootstrap_method": "BCa",
                "bootstrap_resamples": resamples,
                "multiple_comparison_adjustment": "none; exploratory contrasts",
                "metrics": metrics,
            }
        )
    return contrasts, skipped


def analyze_campaign(
    journals,
    questions_dir,
    *,
    task_files=(),
    selection=None,
    split=None,
    resamples=2000,
):
    """Return private numeric analysis; no network or upstream data access."""
    if resamples < 1:
        raise ValueError("resamples must be positive")
    finals, tasks, reservations, attempts = {}, {}, {}, {}
    for path in dict.fromkeys(Path(p).resolve() for p in journals):
        with path.open() as source:
            for line in source:
                if not line.strip():
                    continue
                row = json.loads(line)
                kind = row["kind"]
                if kind == "final":
                    task = row["task"]
                    compact = {
                        key: row.get(key)
                        for key in ("status", "elapsed_seconds", "error", "settings")
                    }
                    compact["response"] = {
                        key: (row.get("response") or {}).get(key)
                        for key in ("selected_option", "refusal")
                    }
                    if task["id"] in tasks and tasks[task["id"]] != task:
                        raise ValueError("Task id has conflicting inputs")
                    if task["id"] in finals and finals[task["id"]] != compact:
                        raise ValueError("Task has conflicting final records")
                    tasks[task["id"]], finals[task["id"]] = task, compact
                elif kind in ("reservation", "attempt"):
                    target = reservations if kind == "reservation" else attempts
                    key = row["attempt_id"]
                    fields = (
                        ("task_id", "reserved_usd")
                        if kind == "reservation"
                        else (
                            "task_id",
                            "accounted_usd",
                            "usage",
                            "cost_source",
                            "elapsed_seconds",
                        )
                    )
                    compact = {field: row.get(field) for field in fields}
                    if key in target and target[key] != compact:
                        raise ValueError("Attempt id has conflicting records")
                    target[key] = compact
    for path in task_files:
        for line in Path(path).read_text().splitlines():
            if line.strip():
                task = json.loads(line)
                existing = {
                    key: value
                    for key, value in tasks.get(task["id"], {}).items()
                    if key != "_question_hash"
                }
                if existing and existing != task:
                    raise ValueError("Task manifest conflicts with journal")
                tasks[task["id"]] = task
    if attempts.keys() - reservations.keys():
        raise ValueError("Attempt has no reservation")
    if split is not None and selection is None:
        raise ValueError("--split requires --selection")
    if selection:
        for groups in selection.values():
            if isinstance(groups, dict) and set(groups.get("development", [])) & set(
                groups.get("evaluation", [])
            ):
                raise ValueError("Development and evaluation keys overlap")
    groups = defaultdict(list)
    for task_id, task in tasks.items():
        if selection is not None:
            keys = selection.get(task["dataset"], [])
            if isinstance(keys, dict):
                keys = (
                    keys.get(split, [])
                    if split
                    else [key for values in keys.values() for key in values]
                )
            elif split:
                raise ValueError(
                    "Named split requires dataset -> split -> keys selection"
                )
            if task["question_key"] not in keys:
                continue
        groups[_config_key(task)].append((task, finals.get(task_id)))
    configurations, prefix_rows = [], []
    for index, (config_key, members) in enumerate(sorted(groups.items())):
        config = json.loads(config_key)
        dataset = config["dataset"]
        raw = json.loads(
            (Path(questions_dir) / f"{dataset}-questions-private.json").read_text()
        )
        lookup = {
            row["key"]: row
            for row in (raw["questions"] if isinstance(raw, dict) else raw)
        }
        cells = defaultdict(dict)
        for task, final in members:
            key = (task["question_key"], task.get("replicate", 0))
            sample = task.get("sample_index", 0)
            expected = config["samples_per_question"]
            if (
                isinstance(sample, bool)
                or not isinstance(sample, int)
                or not isinstance(expected, int)
                or expected <= 0
                or not 0 <= sample < expected
            ):
                raise ValueError("Invalid sample index or expected sample count")
            if sample in cells[key]:
                raise ValueError("Duplicate logical sample across task ids")
            cells[key][sample] = final
        output_cells = []
        for (question_key, replicate), by_sample in sorted(cells.items()):
            q = lookup[question_key]
            question = Question(
                key=question_key,
                text="",
                options=q["options"],
                human_distribution=q.get("human_distribution") or {},
                answer_withheld=q.get("answer_withheld", False),
            )
            complete_rows = {
                i: row
                for i, row in by_sample.items()
                if row is not None and row["status"] == "completed"
            }
            missing = sorted(set(range(expected)) - complete_rows.keys())
            cell = {
                "question_key": question_key,
                "replicate": replicate,
                "complete": not missing,
                "expected_samples": expected,
                "n_completed": len(complete_rows),
                "missing_sample_indices": missing,
                "n_errors": sum(
                    row is not None and row["status"] == "error"
                    for row in by_sample.values()
                ),
                "scores": None,
            }
            if not missing:
                cell.update(
                    _cell_score(question, [complete_rows[i] for i in range(expected)])
                )
            output_cells.append(cell)
            for prefix in PREFIXES:
                if prefix <= expected and all(
                    i in complete_rows for i in range(prefix)
                ):
                    prefix_rows.append(
                        {
                            "config_id": f"config-{index}",
                            "question_key": question_key,
                            "replicate": replicate,
                            "prefix_samples": prefix,
                            "source_cell_complete": not missing,
                            **_cell_score(
                                question, [complete_rows[i] for i in range(prefix)]
                            ),
                        }
                    )
        member_ids = {task["id"] for task, _ in members}
        relevant_reservations = {
            key: row
            for key, row in reservations.items()
            if row["task_id"] in member_ids
        }
        relevant_attempts = {
            key: row for key, row in attempts.items() if key in relevant_reservations
        }
        configurations.append(
            {
                "id": f"config-{index}",
                "config": config,
                "summary": _summary(output_cells),
                "replicates": {
                    str(rep): _summary(
                        [cell for cell in output_cells if cell["replicate"] == rep]
                    )
                    for rep in sorted({cell["replicate"] for cell in output_cells})
                },
                "questions": output_cells,
                "billing": _billing(relevant_reservations, relevant_attempts),
                "response_latency": _latencies(
                    [
                        _number(row.get("elapsed_seconds"))
                        for _, row in members
                        if row is not None
                    ]
                ),
                "settings_counts": dict(
                    Counter(
                        json.dumps(row.get("settings"), sort_keys=True)
                        for _, row in members
                        if row is not None
                    )
                ),
                "errors": dict(
                    Counter(
                        row.get("error") or "unknown"
                        for _, row in members
                        if row is not None and row["status"] == "error"
                    )
                ),
            }
        )
    contrasts, skipped = _paired(configurations, resamples)
    return {
        "schema_version": 1,
        "scope": "private campaign analysis; distributional survey fidelity only",
        "split": split,
        "coverage_scope": "task manifests plus observed journal tasks"
        if task_files
        else "observed final tasks only; undispatched tasks require --tasks",
        "configuration_count": len(configurations),
        "configurations": configurations,
        "convergence_prefixes": prefix_rows,
        "paired_contrasts": contrasts,
        "unpaired_configurations": skipped,
        "all_journal_billing": _billing(reservations, attempts),
        "unattributed_attempt_tasks": len(
            {row["task_id"] for row in reservations.values()} - tasks.keys()
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", nargs="+", required=True, type=Path)
    parser.add_argument("--questions-dir", required=True, type=Path)
    parser.add_argument("--tasks", nargs="*", default=[], type=Path)
    parser.add_argument(
        "--selection",
        type=Path,
        help="JSON dataset -> keys, or dataset -> {development: keys, evaluation: keys}",
    )
    parser.add_argument("--split", choices=("development", "evaluation"))
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    result = analyze_campaign(
        args.journal,
        args.questions_dir,
        task_files=args.tasks,
        selection=json.loads(args.selection.read_text()) if args.selection else None,
        split=args.split,
        resamples=args.resamples,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as target:
        os.fchmod(target.fileno(), 0o600)
        json.dump(result, target, indent=2, allow_nan=False)
        target.write("\n")
    os.replace(temporary, args.output)
    return 0
