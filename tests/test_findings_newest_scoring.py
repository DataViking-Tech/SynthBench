"""Pooled findings use only runs scored with the newest code."""

from __future__ import annotations

from synthbench.findings import (
    _build_conditioning,
    _build_template_comparison,
    _build_temperature_sweep,
    _newest_scoring,
)


def _run(
    provider, dataset, sps, *, rdv=None, opv=None, temperature=None, tpl=None, demo=None
):
    cfg = {"provider": provider, "dataset": dataset, "n_evaluated": 1}
    if rdv is not None:
        cfg["refusal_detector_version"] = rdv
    if opv is not None:
        cfg["option_parser_version"] = opv
    if temperature is not None:
        cfg["temperature"] = temperature
    if tpl is not None:
        cfg["prompt_template"] = f"templates/{tpl}.txt"
    jsd = 1 - sps
    run = {
        "config": cfg,
        "scores": {"sps": sps},
        "per_question": [{"key": "q", "jsd": jsd, "kendall_tau": 2 * sps - 1}],
    }
    if demo is not None:
        run["demographic_breakdown"] = demo
    return run


def test_newest_scoring_keeps_only_the_top_rank():
    old, new = _run("p", "d", 0.5), _run("p", "d", 0.6, rdv=5, opv=3)
    assert _newest_scoring([old, new]) == [new]
    assert _newest_scoring([old]) == [old]
    assert _newest_scoring([]) == []


def test_temperature_sweep_drops_old_runs_of_the_same_model():
    old = _run(
        "althing/openrouter/openai/gpt-4o-mini t=0.3",
        "opinionsqa",
        0.9,
        temperature=0.3,
    )
    new = _run(
        "althing/openrouter/openai/gpt-4o-mini t=0.3",
        "opinionsqa",
        0.7,
        temperature=0.3,
        rdv=5,
        opv=3,
    )
    points = _build_temperature_sweep([old, new])
    assert len(points) == 1
    assert points[0]["n_runs"] == 1


def test_template_comparison_and_conditioning_use_newest_runs():
    p = "althing/openrouter/anthropic/claude-haiku-4.5 t=0.85"
    rows = _build_template_comparison(
        [
            _run(p, "subpop", 0.5, tpl="minimal"),
            _run(p, "subpop", 0.7, tpl="minimal", rdv=5, opv=3),
        ]
    )
    assert [r["n_runs"] for r in rows] == [1]

    def group(pc):
        return {"POLPARTY": [{"group": "Democrat", "p_dist": 0.6, "p_cond": pc}]}

    site, _ = _build_conditioning(
        [
            _run("openrouter/openai/gpt-4o-mini", "subpop", 0.6, demo=group(0.01)),
            _run(
                "openrouter/openai/gpt-4o-mini",
                "subpop",
                0.6,
                rdv=5,
                opv=3,
                demo=group(0.05),
            ),
        ]
    )
    assert [(r["p_cond"], r["n_replications"]) for r in site] == [(0.05, 1)]
