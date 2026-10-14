"""Dedup and run counts prefer runs scored with the newest code."""

from __future__ import annotations

from synthbench.publish import _annotate_run_counts, _dedup_results, _scoring_rank


def _run(n: int, rdv: int | None = None, opv: int | None = None) -> dict:
    cfg = {
        "provider": "openrouter/openai/gpt-4o-mini",
        "dataset": "opinionsqa",
        "n_evaluated": n,
    }
    if rdv is not None:
        cfg["refusal_detector_version"] = rdv
    if opv is not None:
        cfg["option_parser_version"] = opv
    return {"config": cfg, "per_question": []}


def test_scoring_rank_defaults_to_v1():
    assert _scoring_rank(_run(10)) == (1, 1)
    assert _scoring_rank(_run(10, 4, 3)) == (4, 3)


def test_newer_scoring_beats_more_questions():
    old = _run(684)
    new = _run(100, 4, 3)
    assert _dedup_results([old, new]) == [new]
    assert _dedup_results([new, old]) == [new]


def test_question_count_breaks_ties_within_a_scoring_version():
    small, large = _run(100, 4, 3), _run(200, 4, 3)
    assert _dedup_results([small, large]) == [large]


def test_run_count_counts_only_the_winning_scoring_version():
    runs = [_run(684), _run(684), _run(684), _run(100, 4, 3)]
    entry = {
        "model": "GPT-4o-mini",
        "framework": "raw",
        "dataset": "opinionsqa",
        "temperature": None,
        "template": None,
        "effort": None,
        "persona_pack": None,
        "harness": None,
    }
    _annotate_run_counts([entry], runs)
    assert entry["run_count"] == 1
