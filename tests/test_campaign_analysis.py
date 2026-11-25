"""Campaign inference uses complete distributions and question-level units."""

from __future__ import annotations

import json
import stat

import pytest

from synthbench.campaign_analysis import analyze_campaign, main
from synthbench.metrics import jensen_shannon_divergence


def _task(model="good", question="q0", sample=0, n=5, replicate=0):
    return {
        "id": f"{model}-{question}-{replicate}-{n}-{sample}",
        "dataset": "fixture",
        "model": model,
        "provider": "althing",
        "question_key": question,
        "replicate": replicate,
        "sample_index": sample,
        "samples_per_question": n,
    }


def _final(task, option="A", refusal=False, status="completed"):
    return {
        "kind": "final",
        "task_id": task["id"],
        "task": task,
        "status": status,
        "error": "TransportError" if status == "error" else None,
        "response": {
            "selected_option": option,
            "refusal": refusal,
            "raw_text": "PRIVATE RESPONSE",
        },
        "elapsed_seconds": 2.0,
    }


@pytest.fixture
def files(tmp_path):
    questions = [
        {
            "key": f"q{i}",
            "text": "PRIVATE SURVEY TEXT",
            "options": ["A", "B"],
            "human_distribution": {"A": 0.8, "B": 0.2},
        }
        for i in range(6)
    ]
    (tmp_path / "fixture-questions-private.json").write_text(json.dumps(questions))

    def write(rows, name="journal.jsonl"):
        path = tmp_path / name
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
        return path

    return tmp_path, write


def test_known_distribution_and_replicates_remain_separate(files):
    directory, write = files
    rows = []
    for replicate in (0, 1):
        for sample in range(5):
            rows.append(
                _final(
                    _task(sample=sample, replicate=replicate),
                    "A" if sample < (4 if replicate == 0 else 1) else "B",
                )
            )
    result = analyze_campaign([write(rows)], directory)
    config = result["configurations"][0]
    assert config["replicates"]["0"]["scores"] == {
        "sps": 1.0,
        "p_dist": 1.0,
        "p_rank": 1.0,
        "p_refuse": 1.0,
    }
    assert config["replicates"]["1"]["scores"]["p_rank"] == 0.0
    assert len(config["questions"]) == 2
    assert config["summary"]["n_distinct_scored_questions"] == 1
    assert config["summary"]["scores"]["p_rank"] == 0.5
    serialized = json.dumps(result)
    for secret in (
        "PRIVATE SURVEY TEXT",
        "PRIVATE RESPONSE",
        "human_distribution",
        "model_distribution",
    ):
        assert secret not in serialized


def test_incomplete_cell_is_not_scored_but_complete_prefix_is_labeled(files):
    directory, write = files
    rows = [_final(_task(sample=i, n=30), "A" if i < 10 else "B") for i in range(20)]
    rows.append(_final(_task(sample=20, n=30), status="error"))
    result = analyze_campaign([write(list(reversed(rows)))], directory)
    config = result["configurations"][0]
    assert config["summary"]["scores"] is None
    cell = config["questions"][0]
    assert cell["n_completed"] == 20
    assert cell["missing_sample_indices"] == list(range(20, 30))
    assert cell["n_errors"] == 1
    assert [row["prefix_samples"] for row in result["convergence_prefixes"]] == [10, 20]
    assert all(
        not row["source_cell_complete"] for row in result["convergence_prefixes"]
    )
    assert result["convergence_prefixes"][0]["scores"]["p_rank"] == 1.0
    assert result["convergence_prefixes"][1]["scores"]["p_rank"] == 0.5


def test_no_uniform_fallback_for_all_refusals_and_parse_failures(files):
    directory, write = files
    rows = [_final(_task(sample=i), option=None, refusal=i < 3) for i in range(5)]
    cell = analyze_campaign([write(rows)], directory)["configurations"][0]["questions"][
        0
    ]
    assert cell["complete"]
    assert cell["scores"] is None
    assert cell["score_unavailable_reason"] == "no_valid_answers"
    assert cell["refusal_rate"] == 0.6
    assert cell["parse_failure_rate"] == 0.4


def test_some_parse_failures_use_runner_refusal_denominator(files):
    directory, write = files
    rows = [
        _final(_task(sample=i), option="A" if i < 3 else None, refusal=i == 3)
        for i in range(5)
    ]
    cell = analyze_campaign([write(rows)], directory)["configurations"][0]["questions"][
        0
    ]
    assert cell["scores"]["p_refuse"] == 0.75  # 1 refusal / 4 valid-or-refused outcomes
    assert cell["refusal_rate"] == 0.2  # Display rates include parse failures.
    assert cell["parse_failure_rate"] == 0.2
    assert cell["scores"]["p_dist"] == pytest.approx(
        1 - jensen_shannon_divergence({"A": 0.8, "B": 0.2}, {"A": 1.0, "B": 0.0})
    )


@pytest.mark.asyncio
async def test_scores_match_existing_runner(files, mock_dataset):
    from synthbench.providers.base import Provider, Response
    from synthbench.runner import BenchmarkRunner

    directory, write = files
    question = mock_dataset.load(n=1)[0]
    (directory / "fixture-questions-private.json").write_text(
        json.dumps(
            [
                {
                    "key": question.key,
                    "options": question.options,
                    "human_distribution": question.human_distribution,
                }
            ]
        )
    )
    outcomes = [
        Response(selected_option=question.options[0]),
        Response(selected_option=question.options[0]),
        Response(selected_option=question.options[1]),
        Response(selected_option=None, refusal=True),
        Response(selected_option=None),
    ]

    class SequenceProvider(Provider):
        name = "sequence"

        def __init__(self):
            self.responses = iter(outcomes)

        async def respond(self, question, options, *, persona=None):
            return next(self.responses)

    runner_result = await BenchmarkRunner(
        mock_dataset, SequenceProvider(), samples_per_question=5, concurrency=1
    ).run(n=1)
    rows = [
        _final(
            _task(question=question.key, sample=i),
            response.selected_option,
            response.refusal,
        )
        for i, response in enumerate(outcomes)
    ]
    result = analyze_campaign([write(rows)], directory)
    scores = result["configurations"][0]["summary"]["scores"]
    assert scores == pytest.approx(
        {
            "sps": runner_result.sps,
            "p_dist": runner_result.p_dist,
            "p_rank": runner_result.p_rank,
            "p_refuse": runner_result.p_refuse,
        }
    )


def test_pairs_bootstrap_questions_after_averaging_replicates(files):
    directory, write = files
    rows = []
    for question in range(5):
        for replicate in range(3):
            for model, option in (("good", "A"), ("bad", "B")):
                for i in range(5):
                    rows.append(
                        _final(
                            _task(
                                model=model,
                                question=f"q{question}",
                                sample=i,
                                replicate=replicate,
                            ),
                            option,
                        )
                    )
    result = analyze_campaign([write(rows)], directory, resamples=100)
    contrast = result["paired_contrasts"][0]
    assert contrast["n_questions"] == 5
    assert contrast["n_replicate_cells"] == 15
    assert contrast["bootstrap_unit"] == "question_with_replicates_averaged"
    # Sorted configs put bad before good: positive right-minus-left rank difference.
    assert contrast["metrics"]["p_rank"] == {"delta": 1.0, "ci95": [1.0, 1.0]}


def test_mismatched_question_sets_are_not_compared(files):
    directory, write = files
    rows = [
        _final(_task(model=model, question=q, sample=i))
        for model, q in (("good", "q0"), ("bad", "q1"))
        for i in range(5)
    ]
    result = analyze_campaign([write(rows)], directory)
    assert not result["paired_contrasts"]
    assert len(result["unpaired_configurations"]) == 1


def test_billing_counts_cutoff_attempts_and_unsettled_reservations(files):
    directory, write = files
    task = _task()
    rows = []
    for i in range(3):
        rows.append(
            {
                "kind": "reservation",
                "attempt_id": str(i),
                "task_id": task["id"],
                "reserved_usd": "0.5",
            }
        )
        if i < 2:
            rows.append(
                {
                    "kind": "attempt",
                    "attempt_id": str(i),
                    "task_id": task["id"],
                    "accounted_usd": "0.2",
                    "cost_source": "provider-reported-max-gateway-upstream",
                    "usage": {
                        "cost": 0.0,
                        "cost_details": {"upstream_inference_cost": 0.2},
                    },
                    "elapsed_seconds": 1,
                }
            )
    rows.append(_final(task))
    journal = write(rows)
    result = analyze_campaign([journal, journal], directory)
    cost = result["all_journal_billing"]
    assert cost["accounted_usd"] == 0.9
    assert cost["attempt_count"] == 3
    assert cost["unsettled_attempt_count"] == 1
    assert cost["reported_costs"]["gateway_usd"] == {
        "usd": 0.0,
        "attempts_with_evidence": 2,
    }
    assert cost["reported_costs"]["upstream_usd"]["usd"] == 0.4
    assert cost["reported_costs"]["provider_reported_usd"]["usd"] is None


def test_manifest_reveals_fully_undispatched_cells(files):
    directory, write = files
    tasks = [_task(question=q, sample=i) for q in ("q0", "q1") for i in range(5)]
    manifest = write(tasks, "tasks.jsonl")
    finals = [
        _final({**t, "_question_hash": "actual-collector-input-hash"})
        for t in tasks[:5]
    ]
    result = analyze_campaign([write(finals)], directory, task_files=[manifest])
    config = result["configurations"][0]
    assert config["summary"]["n_question_cells"] == 2
    assert config["summary"]["n_complete_cells"] == 1
    assert config["questions"][1]["missing_sample_indices"] == list(range(5))


def test_selection_filters_frozen_evaluation_and_cli_writes_private_file(files):
    directory, write = files
    journal = write(
        [_final(_task(question=q, sample=i)) for q in ("q0", "q1") for i in range(5)]
    )
    selection = directory / "selection.json"
    selection.write_text(
        json.dumps({"fixture": {"development": ["q0"], "evaluation": ["q1"]}})
    )
    output = directory / "analysis.json"
    assert (
        main(
            [
                "--journal",
                str(journal),
                "--questions-dir",
                str(directory),
                "--selection",
                str(selection),
                "--split",
                "evaluation",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    result = json.loads(output.read_text())
    assert [
        cell["question_key"] for cell in result["configurations"][0]["questions"]
    ] == ["q1"]
    assert stat.S_IMODE(output.stat().st_mode) == 0o600


def test_conflicting_logical_samples_and_split_overlap_fail_closed(files):
    directory, write = files
    task = _task()
    duplicate = {**task, "id": "different-id"}
    journal = write([_final(task), _final(duplicate)])
    with pytest.raises(ValueError, match="Duplicate logical sample"):
        analyze_campaign([journal], directory)
    with pytest.raises(ValueError, match="overlap"):
        analyze_campaign(
            [journal],
            directory,
            selection={"fixture": {"development": ["q0"], "evaluation": ["q0"]}},
        )


def _repair(task, suffix="repair", **overrides):
    return {**task, "id": f"{task['id']}-{suffix}", "retry_of": task["id"], **overrides}


def _charge(task, amount, elapsed):
    return [
        {
            "kind": "reservation",
            "attempt_id": task["id"],
            "task_id": task["id"],
            "reserved_usd": amount,
        },
        {
            "kind": "attempt",
            "attempt_id": task["id"],
            "task_id": task["id"],
            "accounted_usd": amount,
            "cost_source": "provider-reported-max-gateway-upstream",
            "usage": {"cost": amount},
            "elapsed_seconds": elapsed,
        },
    ]


def test_explicit_repair_fills_one_slot_and_retains_error_cost_and_history(files):
    directory, write = files
    original = {**_task(n=1), "_question_hash": "snapshot-v1"}
    repair = _repair(original)
    failed = {**_final(original, status="error"), "elapsed_seconds": 10}
    completed = _final(repair)
    original_path = write([*_charge(original, "0.1", 10), failed], "original.jsonl")
    repair_path = write([*_charge(repair, "0.2", 2), completed], "repair.jsonl")
    # Ordering input files does not change the declared causal lineage.
    result = analyze_campaign([repair_path, original_path], directory)
    config = result["configurations"][0]
    cell = config["questions"][0]
    assert cell["complete"] and cell["n_completed"] == 1
    assert cell["n_errors"] == 1
    assert cell["n_unresolved_error_samples"] == 0
    assert cell["retry_history"] == [
        {
            "sample_index": 0,
            "root_task_id": original["id"],
            "task_ids": [original["id"], repair["id"]],
            "statuses": ["error", "completed"],
            "errors": ["TransportError", None],
            "selected_task_id": repair["id"],
            "recovered": True,
        }
    ]
    assert config["retry_coverage"] == {
        "retried_samples": 1,
        "retry_tasks": 1,
        "recovered_samples": 1,
        "unresolved_retried_samples": 0,
    }
    assert config["billing"]["accounted_usd"] == pytest.approx(0.3)
    assert result["all_journal_billing"]["accounted_usd"] == pytest.approx(0.3)
    assert config["billing"]["attempt_latency"]["mean_seconds"] == 6
    assert config["response_latency"]["count"] == 1
    assert config["response_latency"]["mean_seconds"] == 2
    assert config["errors"] == {"TransportError": 1}


@pytest.mark.parametrize(
    ("option", "refusal"), [("A", False), (None, False), (None, True)]
)
def test_retry_of_completed_answer_parse_failure_or_refusal_is_rejected(
    files, option, refusal
):
    directory, write = files
    original = _task(n=1)
    repair = _repair(original)
    path = write([_final(original, option=option, refusal=refusal), _final(repair)])
    with pytest.raises(ValueError, match="final error"):
        analyze_campaign([path], directory)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dataset", "other"),
        ("question_key", "q1"),
        ("model", "other"),
        ("provider", "openrouter"),
        ("elicitation", "structured"),
        ("persona_pack", "global-respondents"),
        ("replicate", 1),
        ("sample_index", 1),
        ("samples_per_question", 6),
        ("_question_hash", "changed-snapshot"),
    ],
)
def test_retry_cannot_change_sample_scope_or_question_snapshot(files, field, value):
    directory, write = files
    original = {**_task(), "_question_hash": "original-snapshot"}
    repair = _repair(original, **{field: value})
    path = write([_final(original, status="error"), _final(repair)])
    with pytest.raises(ValueError, match="same sample"):
        analyze_campaign([path], directory)


def test_retry_unknown_parent_cycle_and_branch_fail_closed(files):
    directory, write = files
    original = _task(n=1)
    repair = _repair(original)
    with pytest.raises(ValueError, match="unknown parent"):
        analyze_campaign([write([_final(repair)])], directory)
    cyclic_original = {**original, "retry_of": repair["id"]}
    with pytest.raises(ValueError, match="cycle"):
        analyze_campaign(
            [
                write(
                    [
                        _final(cyclic_original, status="error"),
                        _final(repair, status="error"),
                    ]
                )
            ],
            directory,
        )
    alternate = _repair(original, suffix="alternate")
    with pytest.raises(ValueError, match="branching"):
        analyze_campaign(
            [
                write(
                    [
                        _final(original, status="error"),
                        _final(repair),
                        _final(alternate),
                    ]
                )
            ],
            directory,
        )


def test_failed_to_failed_to_completed_retry_chain_and_pending_terminal(files):
    directory, write = files
    original = _task(n=1)
    first = _repair(original)
    second = _repair(first)
    rows = [
        _final(original, status="error"),
        _final(first, status="error"),
        _final(second),
    ]
    result = analyze_campaign([write(rows)], directory)
    cell = result["configurations"][0]["questions"][0]
    assert cell["n_completed"] == 1 and cell["n_errors"] == 2
    assert cell["retry_history"][0]["task_ids"] == [
        original["id"],
        first["id"],
        second["id"],
    ]
    assert cell["retry_history"][0]["statuses"] == ["error", "error", "completed"]
    manifest = write([original, first, second], "tasks.jsonl")
    result = analyze_campaign([write(rows[:2])], directory, task_files=[manifest])
    config = result["configurations"][0]
    assert config["questions"][0]["missing_sample_indices"] == [0]
    assert config["questions"][0]["retry_history"][0]["statuses"] == [
        "error",
        "error",
        "pending",
    ]
    assert config["retry_coverage"]["unresolved_retried_samples"] == 1


def test_retry_parent_requires_observed_error_final_and_preserves_journal_hash(files):
    directory, write = files
    original = _task(n=1)
    repair = _repair(original)
    manifest = write([original, repair], "tasks.jsonl")
    with pytest.raises(ValueError, match="final error"):
        analyze_campaign([write([_final(repair)])], directory, task_files=[manifest])
    original_row = _final({**original, "_question_hash": "old"}, status="error")
    repair_row = _final({**repair, "_question_hash": "new"})
    with pytest.raises(ValueError, match="same sample"):
        analyze_campaign(
            [write([original_row, repair_row])], directory, task_files=[manifest]
        )
