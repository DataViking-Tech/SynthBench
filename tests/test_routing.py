"""routing.json: shape, candidate selection, Index math and the confidence rule."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthbench.routing import (
    API_NAME,
    DATASET_CEILINGS,
    MAX_CANDIDATES,
    MIN_QUESTIONS,
    SLICES,
    build_routing,
)
from synthbench.topics import TOPIC_IDS

REPO = Path(__file__).resolve().parent.parent

POLITICS = "Did you vote in the last election?"
HEALTH = "How would you rate your own health?"


def _rows(
    dataset: str, n: int, *, jsd: float, tau: float, m_ref: float = 0.0
) -> list[dict]:
    """``n`` questions, the first half politics, the second half health."""
    rows = []
    for i in range(n):
        # Small per-question spread so bootstrap intervals are not degenerate.
        wobble = ((i * 37) % 11 - 5) / 500
        rows.append(
            {
                "key": f"{dataset.upper()}_Q{i:03d}",
                "text": POLITICS if i < n // 2 else HEALTH,
                "jsd": max(0.0, jsd + wobble),
                "kendall_tau": tau,
                "parity": 0.5,
                "model_refusal_rate": m_ref,
                "human_refusal_rate": 0.0,
            }
        )
    return rows


def _result(provider: str, dataset: str, rows: list[dict], **cfg) -> dict:
    return {
        "benchmark": "synthbench",
        "config": {
            "provider": provider,
            "dataset": dataset,
            "n_evaluated": len(rows),
            "samples_per_question": 10,
            **cfg,
        },
        "per_question": rows,
    }


N = {"opinionsqa": 40, "gss": 20, "subpop": 40, "globalopinionqa": 40}


def _pool(
    *, best_jsd: float = 0.05, best_tau: float = 0.6, n: dict | None = None
) -> list[dict]:
    n = n or N
    results = []
    for ds, k in n.items():
        results.append(_result("random-baseline", ds, _rows(ds, k, jsd=0.30, tau=0.0)))
        results.append(
            _result("majority-baseline", ds, _rows(ds, k, jsd=0.25, tau=0.2))
        )
        results.append(
            _result(
                "althing/openrouter/qwen/qwen3.8-flash",
                ds,
                _rows(ds, k, jsd=0.15, tau=0.4),
            )
        )
        results.append(
            _result(
                "openrouter/deepseek/deepseek-v4.1-flash",
                ds,
                _rows(ds, k, jsd=best_jsd + 0.001, tau=best_tau),
            )
        )
        results.append(
            _result(
                "ensemble/mixed",
                ds,
                _rows(ds, k, jsd=0.10, tau=0.5),
                ensemble_sources=[
                    {
                        "provider": "althing/openrouter/qwen/qwen3.8-flash",
                        "weight": 0.6,
                    },
                    {
                        "provider": "openrouter/deepseek/deepseek-v4.1-flash",
                        "weight": 0.2,
                    },
                ],
            )
        )
        results.append(
            _result(
                "ensemble/native",
                ds,
                _rows(ds, k, jsd=0.12, tau=0.45),
                ensemble_sources=[
                    {"provider": "althing/openrouter/qwen/qwen3.8-flash"},
                    {"provider": "althing/openrouter/anthropic/claude-haiku-5.5"},
                ],
            )
        )
        # Variants never become candidates, however well they score.
        results.append(
            _result(
                "althing/openrouter/qwen/qwen3.8-flash t=0.3",
                ds,
                _rows(ds, k, jsd=0.0, tau=1.0),
                temperature=0.3,
            )
        )
        results.append(
            _result(
                "althing/openrouter/qwen/qwen3.8-flash tpl=structured",
                ds,
                _rows(ds, k, jsd=0.0, tau=1.0),
                prompt_template="templates/structured.md",
            )
        )
    # Covers only opinionsqa: never a us-general candidate.
    results.append(
        _result(
            "openrouter/openai/gpt-4o",
            "opinionsqa",
            _rows("opinionsqa", 40, jsd=0.0, tau=1.0),
        )
    )
    return results


@pytest.fixture(scope="module")
def routing() -> dict:
    return build_routing(
        _pool(), generated_at="2026-10-14T00:00:00+00:00", n_bootstrap=400
    )


def _route(payload: dict, slice_id: str, topic: str) -> dict:
    return next(
        r for r in payload["routes"] if r["slice"] == slice_id and r["topic"] == topic
    )


def test_top_level_shape(routing):
    assert routing["api"]["name"] == API_NAME
    assert re.fullmatch(r"\d+\.\d+\.\d+", routing["api"]["version"])
    assert routing["generated_at"] == "2026-10-14T00:00:00+00:00"
    assert routing["taxonomy"]["version"] == 1
    assert [t["id"] for t in routing["taxonomy"]["topics"]] == list(TOPIC_IDS)
    assert [s["id"] for s in routing["slices"]] == [
        "us-general",
        "us-subgroups",
        "cross-national",
    ]
    assert routing["slices"][0]["datasets"] == ["opinionsqa", "gss"]
    assert routing["min_questions"] == MIN_QUESTIONS == 30
    json.dumps(routing)  # serializable


def test_one_route_per_slice_topic_with_questions(routing):
    pairs = [(r["slice"], r["topic"]) for r in routing["routes"]]
    assert len(pairs) == len(set(pairs))
    for s in SLICES:
        topics = {t for sl, t in pairs if sl == s["id"]}
        # Synthetic questions are politics or health only.
        assert topics == {"all", "politics", "science-health"}
    us = _route(routing, "us-general", "all")
    assert us["n_questions"] == 60
    assert us["n_by_dataset"] == {"opinionsqa": 40, "gss": 20}
    assert _route(routing, "us-general", "politics")["n_questions"] == 30


def test_route_fields(routing):
    for r in routing["routes"]:
        assert set(r) >= {
            "slice",
            "topic",
            "n_questions",
            "confident",
            "best",
            "best_althing",
            "best_single_althing",
            "candidates",
        }
        assert 0 < len(r["candidates"]) <= MAX_CANDIDATES
        idx = [c["index"] for c in r["candidates"]]
        assert idx == sorted(idx, reverse=True)
        assert r["best"] == r["candidates"][0]["config_id"]
        for c in r["candidates"]:
            assert c["kind"] in ("single", "blend")
            assert c["n"] == r["n_questions"]
            lo, hi = c["ci"]
            assert lo <= hi
            assert c["members"]


def test_candidates_exclude_baselines_variants_and_partial_coverage(routing):
    for r in routing["routes"]:
        labels = {c["label"] for c in r["candidates"]}
        ids = {c["config_id"] for c in r["candidates"]}
        assert not any("Baseline" in lbl for lbl in labels)
        assert not any("--t0.3--" in i or "tplstructured" in i for i in ids)
        # GPT-4o only ran opinionsqa: not a candidate for any slice here.
        assert "GPT-4o" not in labels
    assert len(_route(routing, "us-general", "all")["candidates"]) == 4


def test_best_althing_rules(routing):
    for r in routing["routes"]:
        by_id = {c["config_id"]: c for c in r["candidates"]}
        assert by_id[r["best_althing"]]["althing_native"] is True
        single = by_id[r["best_single_althing"]]
        assert single["althing_native"] is True
        assert single["kind"] == "single"
    us = _route(routing, "us-general", "all")
    by_id = {c["config_id"]: c for c in us["candidates"]}
    # The raw DeepSeek row is best overall but never best_althing.
    assert by_id[us["best"]]["label"] == "DeepSeek V4.1 Flash"
    assert by_id[us["best"]]["althing_native"] is False
    assert by_id[us["best_althing"]]["kind"] == "blend"  # ensemble/native
    assert by_id[us["best_single_althing"]]["label"] == "Althing (Qwen 3.8 Flash)"


def test_members_and_weights(routing):
    us = _route(routing, "us-general", "all")
    by_label = {c["label"]: c for c in us["candidates"]}
    mixed = next(
        c for c in us["candidates"] if c["config_id"].startswith("ensemble--mixed")
    )
    assert mixed["althing_native"] is False
    assert [m["framework"] for m in mixed["members"]] == ["product", "raw"]
    assert [m["weight"] for m in mixed["members"]] == [0.75, 0.25]
    native = next(
        c for c in us["candidates"] if c["config_id"].startswith("ensemble--native")
    )
    assert [m["weight"] for m in native["members"]] == [0.5, 0.5]
    single = by_label["Althing (Qwen 3.8 Flash)"]
    assert single["members"] == [
        {"model_id": "qwen/qwen3.8-flash", "framework": "product", "weight": 1.0}
    ]


def test_index_matches_formula():
    """Index = 100*(SPS - SPS_random)/(ceiling - SPS_random), question-weighted."""
    payload = build_routing(_pool(), n_bootstrap=50)
    us = _route(payload, "us-general", "all")
    deepseek = next(c for c in us["candidates"] if c["label"] == "DeepSeek V4.1 Flash")

    def sps(rows):
        p_dist = 1 - sum(r["jsd"] for r in rows) / len(rows)
        p_rank = (1 + sum(r["kendall_tau"] for r in rows) / len(rows)) / 2
        return (p_dist + p_rank + 1.0) / 3  # refusal rates match: p_refuse = 1

    expected = 0.0
    for ds, n in (("opinionsqa", 40), ("gss", 20)):
        s = sps(_rows(ds, n, jsd=0.051, tau=0.6))
        r = sps(_rows(ds, n, jsd=0.30, tau=0.0))
        expected += n * 100 * (s - r) / (DATASET_CEILINGS[ds] - r)
    assert deepseek["index"] == pytest.approx(expected / 60, abs=0.05)


def test_confident_when_best_clearly_ahead(routing):
    assert _route(routing, "us-general", "all")["confident"] is True


def test_not_confident_below_min_questions(routing):
    route = _route(routing, "us-general", "politics")  # 30 questions: at the bar
    assert route["n_questions"] == 30
    small = build_routing(
        _pool(n={"opinionsqa": 20, "gss": 8, "subpop": 20, "globalopinionqa": 20}),
        n_bootstrap=200,
    )
    for r in small["routes"]:
        assert r["n_questions"] < MIN_QUESTIONS
        assert r["confident"] is False


def test_not_confident_when_close():
    # DeepSeek and the mixed blend score almost the same: the paired
    # difference interval includes 0.
    payload = build_routing(_pool(best_jsd=0.099, best_tau=0.5), n_bootstrap=400)
    us = _route(payload, "us-general", "all")
    assert us["confident"] is False


def test_deterministic():
    a = build_routing(_pool(), generated_at="x", n_bootstrap=200)
    b = build_routing(_pool(), generated_at="x", n_bootstrap=200)
    assert a == b


def test_slice_skipped_without_random_baseline():
    pool = [
        r
        for r in _pool()
        if not (
            r["config"]["provider"] == "random-baseline"
            and r["config"]["dataset"] == "gss"
        )
    ]
    payload = build_routing(pool, n_bootstrap=50)
    assert {r["slice"] for r in payload["routes"]} == {"us-subgroups", "cross-national"}


def test_ceilings_match_site_pins():
    ts = (REPO / "site" / "src" / "lib" / "ceilings.ts").read_text(encoding="utf-8")
    pinned = dict(re.findall(r"(\w+): \{ mean: ([0-9.]+)", ts))
    assert {k: float(v) for k, v in pinned.items()} == DATASET_CEILINGS


def test_publish_data_writes_routing(tmp_path):
    from synthbench.publish import publish_leaderboard_data

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    for i, r in enumerate(_pool()):
        (results_dir / f"run_{i:03d}.json").write_text(json.dumps(r), encoding="utf-8")
    routing_path = tmp_path / "routing.json"
    publish_leaderboard_data(
        results_dir, tmp_path / "leaderboard.json", routing_output=routing_path
    )
    payload = json.loads(routing_path.read_text(encoding="utf-8"))
    leaderboard = json.loads(
        (tmp_path / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert payload["generated_at"] == leaderboard["generated_at"]
    assert payload["routes"]
    assert leaderboard["topic_taxonomy"]["version"] == 1


def test_equal_coverage_excludes_nobody(routing):
    assert all(r["excluded_for_coverage"] == 0 for r in routing["routes"])


def test_short_runs_do_not_shrink_a_larger_question_set():
    """Systems on the larger --suite routing set keep their questions.

    The random baseline and Qwen ran 80 SubPOP questions; everything else
    ran the first 40. The 40-question systems leave the route instead of
    cutting it to 40 questions.
    """
    results = []
    for r in _pool():
        cfg = r["config"]
        if cfg["dataset"] == "subpop" and cfg["provider"] in (
            "random-baseline",
            "althing/openrouter/qwen/qwen3.8-flash",
        ):
            continue
        results.append(r)
    results.append(
        _result("random-baseline", "subpop", _rows("subpop", 80, jsd=0.30, tau=0.0))
    )
    results.append(
        _result(
            "althing/openrouter/qwen/qwen3.8-flash",
            "subpop",
            _rows("subpop", 80, jsd=0.15, tau=0.4),
        )
    )
    payload = build_routing(
        results, generated_at="2026-10-14T00:00:00+00:00", n_bootstrap=200
    )
    route = _route(payload, "us-subgroups", "all")
    assert route["n_questions"] == 80
    assert [c["label"] for c in route["candidates"]] == ["Althing (Qwen 3.8 Flash)"]
    assert route["excluded_for_coverage"] == 3
    assert route["confident"] is False  # one candidate is never confident
    # Slices where everyone ran the same questions are unchanged.
    assert _route(payload, "us-general", "all")["excluded_for_coverage"] == 0


def test_routing_suite_runs_feed_routing_only():
    """A --suite routing run joins routing.json but not the leaderboard dedup."""
    from synthbench.publish import _dedup_results, is_routing_suite_run

    big = _result(
        "althing/openrouter/qwen/qwen3.8-flash",
        "subpop",
        _rows("subpop", 80, jsd=0.15, tau=0.4),
        suite="routing",
    )
    rand = _result(
        "random-baseline",
        "subpop",
        _rows("subpop", 80, jsd=0.30, tau=0.0),
        suite="routing",
    )
    results = [*_pool(), big, rand]
    assert is_routing_suite_run(big) and not is_routing_suite_run(_pool()[0])

    def subpop_n(rows, provider):
        return next(
            r["config"]["n_evaluated"]
            for r in rows
            if r["config"]["provider"] == provider
            and r["config"]["dataset"] == "subpop"
        )

    leaderboard = _dedup_results(results)
    assert subpop_n(leaderboard, "althing/openrouter/qwen/qwen3.8-flash") == 40
    assert subpop_n(leaderboard, "random-baseline") == 40
    routing_rows = _dedup_results(results, include_routing_suite=True)
    assert subpop_n(routing_rows, "althing/openrouter/qwen/qwen3.8-flash") == 80

    payload = build_routing(
        results, generated_at="2026-10-14T00:00:00+00:00", n_bootstrap=200
    )
    assert _route(payload, "us-subgroups", "all")["n_questions"] == 80
