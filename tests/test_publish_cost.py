"""Tests for cost field derivation in publish.py (Slice 3)."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

from synthbench.publish import (
    _build_pricing_snapshot,
    _compute_cost_fields,
    _compute_ensemble_cost,
    _compute_latency_fields,
    publish_leaderboard_data,
)

# Imported lazily by the helpers under test, but the test file needs the
# pricing constants for assertion math. Tests skip cleanly if synthpanel
# (a dep added in this slice) is not installed.
synth_panel_cost = pytest.importorskip("synth_panel.cost")
HAIKU = synth_panel_cost.HAIKU_PRICING
SONNET = synth_panel_cost.SONNET_PRICING


# Dynamic read: extract the pricing snapshot_date from the installed
# synth_panel.cost source the same way `_build_pricing_snapshot` does.
# Previously this test hard-coded "2026-04-14", which broke every time
# the upstream cost.py snapshot comment rolled (observed 2026-04-21 when
# synth_panel released v0.9.7 — refinery escalation hq-wisp-ll8ti4).
# Assertions now pin against whatever the installed synth_panel reports,
# so the test no longer requires per-release maintenance.
_SNAPSHOT_PATTERN = re.compile(r"pricing snapshot_date:\s*(\d{4}-\d{2}-\d{2})")


def _current_snapshot_date() -> str:
    """Return the snapshot_date reported by the installed synth_panel.

    Reads the same `# pricing snapshot_date: YYYY-MM-DD` anchor comment
    `_build_pricing_snapshot` parses, from the installed package source.
    Skips the test (via pytest.skip) if the anchor is missing, which
    matches the library's own fallback behavior.
    """
    source = inspect.getsource(synth_panel_cost)
    m = _SNAPSHOT_PATTERN.search(source)
    if not m:
        pytest.skip(
            "synth_panel.cost does not expose a `pricing snapshot_date:` anchor comment"
        )
    return m.group(1)


CURRENT_SNAPSHOT_DATE = _current_snapshot_date()


def _agg(input_tokens: int | None = None, output_tokens: int | None = None) -> dict:
    if input_tokens is None and output_tokens is None:
        return {"n_questions": 100}
    return {
        "n_questions": 100,
        "token_usage": {
            "input_tokens": input_tokens or 0,
            "output_tokens": output_tokens or 0,
            "call_count": 1,
            "source": "measured",
        },
    }


# ---------------------------------------------------------------------------
# _compute_cost_fields
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, aggregate, config, entry, expected",
    [
        (
            "haiku_measured",
            _agg(1_000_000, 1_000_000),
            {"provider": "raw-anthropic/claude-haiku-4-5"},
            {"n": 100, "sps": 0.85},
            {
                "cost_usd": HAIKU.input_cost_per_million
                + HAIKU.output_cost_per_million,
                # cost / n * 100 = cost (n=100)
                "cost_per_100q": HAIKU.input_cost_per_million
                + HAIKU.output_cost_per_million,
                "cost_per_sps_point": (
                    HAIKU.input_cost_per_million + HAIKU.output_cost_per_million
                )
                / 0.85,
                "is_cost_estimated": False,
            },
        ),
        (
            "sonnet_measured",
            _agg(2_000_000, 1_000_000),
            {"provider": "raw-anthropic/claude-sonnet-4"},
            {"n": 200, "sps": 0.9},
            {
                "cost_usd": (
                    2 * SONNET.input_cost_per_million + SONNET.output_cost_per_million
                ),
                "cost_per_100q": (
                    2 * SONNET.input_cost_per_million + SONNET.output_cost_per_million
                )
                / 200
                * 100,
                "cost_per_sps_point": (
                    (2 * SONNET.input_cost_per_million + SONNET.output_cost_per_million)
                    / 0.9
                ),
                "is_cost_estimated": False,
            },
        ),
        (
            "unknown_provider_nulls",
            _agg(1_000_000, 1_000_000),
            {"provider": "raw-openai/gpt-5"},
            {"n": 100, "sps": 0.85},
            {
                "cost_usd": None,
                "cost_per_100q": None,
                "cost_per_sps_point": None,
                "is_cost_estimated": None,
            },
        ),
        (
            # #316: rows without token_usage fall back to the documented
            # samples×questions×per-call-constant estimate, marked estimated.
            "absent_token_usage_estimates",
            _agg(),  # no token_usage key
            {
                "provider": "raw-anthropic/claude-haiku-4-5",
                "samples_per_question": 5,
                "n_evaluated": 100,
            },
            {"n": 100, "sps": 0.85},
            {
                "cost_usd": 500
                * (
                    124 * HAIKU.input_cost_per_million
                    + 4 * HAIKU.output_cost_per_million
                )
                / 1_000_000,
                "cost_per_100q": 500
                * (
                    124 * HAIKU.input_cost_per_million
                    + 4 * HAIKU.output_cost_per_million
                )
                / 1_000_000,
                "tokens_per_response": None,
                "is_cost_estimated": True,
            },
        ),
        (
            # #316: no token_usage AND no samples_per_question/n_evaluated —
            # nothing to estimate from, stays null.
            "absent_token_usage_and_config_nulls",
            _agg(),  # no token_usage key
            {"provider": "raw-anthropic/claude-haiku-4-5"},
            {"n": 100, "sps": 0.85},
            {
                "cost_usd": None,
                "cost_per_100q": None,
                "cost_per_sps_point": None,
                "is_cost_estimated": None,
            },
        ),
        (
            # #316: baselines make zero model calls — true $0.00, not an
            # estimate, even without token_usage.
            "baseline_no_token_usage_zero_cost",
            _agg(),  # no token_usage key
            {"provider": "random-baseline"},
            {"n": 100, "sps": 0.5, "is_baseline": True},
            {
                "cost_usd": 0.0,
                "cost_per_100q": 0.0,
                "cost_per_sps_point": 0.0,
                "is_cost_estimated": False,
            },
        ),
        (
            "zero_tokens_baseline_zero_cost",
            _agg(0, 0),
            {"provider": "random-baseline"},
            {"n": 100, "sps": 0.5},
            {
                "cost_usd": 0.0,
                "cost_per_100q": 0.0,
                "cost_per_sps_point": 0.0,
                "is_cost_estimated": False,
            },
        ),
        (
            "low_sps_cost_per_sps_null",
            _agg(1_000_000, 1_000_000),
            {"provider": "raw-anthropic/claude-haiku-4-5"},
            {"n": 100, "sps": 0.001},  # < 0.01 → null cps
            {
                "cost_usd": HAIKU.input_cost_per_million
                + HAIKU.output_cost_per_million,
                "cost_per_100q": HAIKU.input_cost_per_million
                + HAIKU.output_cost_per_million,
                "cost_per_sps_point": None,
                "is_cost_estimated": False,
            },
        ),
    ],
)
def test_compute_cost_fields(name, aggregate, config, entry, expected):
    result = _compute_cost_fields(aggregate, config, entry)
    assert set(result.keys()) == {
        "cost_usd",
        "cost_per_100q",
        "cost_per_sps_point",
        "cost_per_response",
        "tokens_per_response",
        "is_cost_estimated",
    }
    for k, want in expected.items():
        got = result[k]
        if want is None or got is None:
            assert got == want, f"{name}/{k}: got {got!r}, expected {want!r}"
        else:
            assert got == pytest.approx(want, rel=1e-5), (
                f"{name}/{k}: got {got!r}, expected {want!r}"
            )


# ---------------------------------------------------------------------------
# _compute_ensemble_cost
# ---------------------------------------------------------------------------


def _constituent(provider: str, dataset: str, in_tok: int, out_tok: int) -> dict:
    return {
        "config": {"provider": provider, "dataset": dataset},
        "aggregate": {
            "token_usage": {
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "call_count": 1,
                "source": "measured",
            },
        },
    }


def test_compute_ensemble_cost_sums_all_constituents():
    haiku = _constituent("synthpanel/claude-haiku-4-5", "subpop", 1_000_000, 500_000)
    sonnet = _constituent("synthpanel/claude-sonnet-4", "subpop", 1_000_000, 500_000)
    opus = _constituent("raw-anthropic/claude-opus-4-6", "subpop", 1_000_000, 500_000)
    results_by_pds = {
        ("synthpanel/claude-haiku-4-5", "subpop"): haiku,
        ("synthpanel/claude-sonnet-4", "subpop"): sonnet,
        ("raw-anthropic/claude-opus-4-6", "subpop"): opus,
    }
    config = {
        "dataset": "subpop",
        "ensemble_sources": [
            {"provider": "synthpanel/claude-haiku-4-5", "weight": 1 / 3},
            {"provider": "synthpanel/claude-sonnet-4", "weight": 1 / 3},
            {"provider": "raw-anthropic/claude-opus-4-6", "weight": 1 / 3},
        ],
    }
    result = _compute_ensemble_cost(config, results_by_pds)
    assert result is not None
    cost, is_estimated = result
    assert is_estimated is False  # every constituent had measured usage
    expected = (
        (HAIKU.input_cost_per_million + 0.5 * HAIKU.output_cost_per_million)
        + (SONNET.input_cost_per_million + 0.5 * SONNET.output_cost_per_million)
        + (
            synth_panel_cost.OPUS_PRICING.input_cost_per_million
            + 0.5 * synth_panel_cost.OPUS_PRICING.output_cost_per_million
        )
    )
    assert cost == pytest.approx(expected, rel=1e-5)


def test_compute_ensemble_cost_missing_constituent_returns_none():
    haiku = _constituent("synthpanel/claude-haiku-4-5", "subpop", 1_000_000, 500_000)
    # opus exists, but sonnet's token_usage is missing AND its config lacks
    # samples_per_question/n_evaluated, so the #316 estimate can't run either.
    sonnet_no_usage = {
        "config": {"provider": "synthpanel/claude-sonnet-4", "dataset": "subpop"},
        "aggregate": {"n_questions": 100},  # no token_usage
    }
    opus = _constituent("raw-anthropic/claude-opus-4-6", "subpop", 1_000_000, 500_000)
    results_by_pds = {
        ("synthpanel/claude-haiku-4-5", "subpop"): haiku,
        ("synthpanel/claude-sonnet-4", "subpop"): sonnet_no_usage,
        ("raw-anthropic/claude-opus-4-6", "subpop"): opus,
    }
    config = {
        "dataset": "subpop",
        "ensemble_sources": [
            {"provider": "synthpanel/claude-haiku-4-5", "weight": 1 / 3},
            {"provider": "synthpanel/claude-sonnet-4", "weight": 1 / 3},
            {"provider": "raw-anthropic/claude-opus-4-6", "weight": 1 / 3},
        ],
    }
    assert _compute_ensemble_cost(config, results_by_pds) is None


def test_compute_ensemble_cost_no_sources_returns_none():
    assert _compute_ensemble_cost({"dataset": "subpop"}, {}) is None


def test_compute_ensemble_cost_estimates_unmeasured_constituent():
    """#316: a constituent without token_usage contributes the documented
    samples×questions×per-call-constant estimate and flips is_estimated."""
    haiku = _constituent("synthpanel/claude-haiku-4-5", "subpop", 1_000_000, 500_000)
    sonnet_estimable = {
        "config": {
            "provider": "synthpanel/claude-sonnet-4",
            "dataset": "subpop",
            "samples_per_question": 5,
            "n_evaluated": 100,
        },
        "aggregate": {"n_questions": 100},  # no token_usage
    }
    results_by_pds = {
        ("synthpanel/claude-haiku-4-5", "subpop"): haiku,
        ("synthpanel/claude-sonnet-4", "subpop"): sonnet_estimable,
    }
    config = {
        "dataset": "subpop",
        "ensemble_sources": [
            {"provider": "synthpanel/claude-haiku-4-5", "weight": 0.5},
            {"provider": "synthpanel/claude-sonnet-4", "weight": 0.5},
        ],
    }
    result = _compute_ensemble_cost(config, results_by_pds)
    assert result is not None
    cost, is_estimated = result
    assert is_estimated is True
    expected = (
        HAIKU.input_cost_per_million + 0.5 * HAIKU.output_cost_per_million
    ) + 500 * (
        124 * SONNET.input_cost_per_million + 4 * SONNET.output_cost_per_million
    ) / 1_000_000
    assert cost == pytest.approx(expected, rel=1e-5)


# ---------------------------------------------------------------------------
# _build_pricing_snapshot
# ---------------------------------------------------------------------------


def test_build_pricing_snapshot_shape_and_rates():
    snap = _build_pricing_snapshot()
    assert set(snap.keys()) == {
        "generated_at",
        "synth_panel_version",
        "snapshot_date",
        "rates",
    }
    rates = snap["rates"]
    for label in ("haiku", "sonnet", "opus", "gemini-2.5-pro", "gemini-flash"):
        assert label in rates, f"missing rate label: {label}"
        for k in (
            "input_cost_per_million",
            "output_cost_per_million",
            "cache_creation_cost_per_million",
            "cache_read_cost_per_million",
        ):
            assert k in rates[label], f"{label} missing {k}"
    assert rates["haiku"]["input_cost_per_million"] == HAIKU.input_cost_per_million
    assert rates["haiku"]["output_cost_per_million"] == HAIKU.output_cost_per_million
    assert rates["sonnet"]["input_cost_per_million"] == SONNET.input_cost_per_million
    # snapshot_date is read from the installed cost.py anchor comment;
    # pin against whatever synth_panel reports today so future releases
    # don't break this test (see module-level _current_snapshot_date).
    assert snap["snapshot_date"] == CURRENT_SNAPSHOT_DATE
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", snap["snapshot_date"]), (
        f"snapshot_date must be ISO YYYY-MM-DD, got {snap['snapshot_date']!r}"
    )


# ---------------------------------------------------------------------------
# Golden-file: 3-entry leaderboard fragment
# ---------------------------------------------------------------------------


def _pq_rows(n: int, sps: float) -> list[dict]:
    """Constant-metric per-question rows whose recomputed composite == sps.

    publish no longer trusts submitted aggregates (P0-4): the leaderboard
    sps is recomputed from per-question rows, so this golden fixture must
    carry rows that actually reconcile to the target score (the pre-fix
    fixture shipped ``per_question: []`` and relied on the submitted
    ``scores.sps`` being republished verbatim). With tau=0.5 and a zero
    refusal diff, the 3-metric composite reduces to (2.75 - jsd) / 3, so
    jsd = 2.75 - 3·sps hits the target exactly.
    """
    jsd = 2.75 - 3.0 * sps
    assert 0.0 <= jsd <= 1.0, "target sps out of range for constant-row fixture"
    return [
        {
            "key": f"Q{i:03d}",
            "text": f"question {i}",
            "options": ["A", "B", "C"],
            "human_distribution": {"A": 0.6, "B": 0.3, "C": 0.1},
            "model_distribution": {"A": 0.5, "B": 0.35, "C": 0.15},
            "jsd": jsd,
            "kendall_tau": 0.5,
            "parity": (1.0 - jsd + 0.75) / 2.0,
            "n_samples": 5,
            "model_refusal_rate": 0.02,
            "human_refusal_rate": 0.02,
        }
        for i in range(n)
    ]


def _make_run(
    *,
    provider: str,
    dataset: str,
    sps: float,
    n_questions: int,
    timestamp: str,
    token_usage: dict | None = None,
    ensemble_sources: list | None = None,
) -> dict:
    config: dict = {
        "provider": provider,
        "dataset": dataset,
        "n_evaluated": n_questions,
        "samples_per_question": 5,
    }
    if ensemble_sources:
        config["ensemble_sources"] = ensemble_sources
    jsd = 2.75 - 3.0 * sps
    aggregate: dict = {
        "mean_jsd": jsd,
        "median_jsd": jsd,
        "mean_kendall_tau": 0.5,
        "composite_parity": sps,
        "n_questions": n_questions,
        "elapsed_seconds": 1.0,
        "per_metric_ci": {"sps": [sps - 0.01, sps + 0.01]},
        "n_parse_failures": 0,
    }
    if token_usage is not None:
        aggregate["token_usage"] = token_usage
    return {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "timestamp": timestamp,
        "config": config,
        "scores": {
            "sps": sps,
            "p_dist": 1.0 - jsd,
            "p_rank": 0.75,
            "p_refuse": 1.0,
        },
        "aggregate": aggregate,
        "per_question": _pq_rows(n_questions, sps),
        "demographic_breakdown": {},
    }


def test_golden_three_entry_leaderboard(tmp_path: Path):
    """Feed 3 raw artifacts (measured / no-tokens / ensemble) through publish_leaderboard_data
    and assert the cost-related shape and values."""
    haiku_with_tokens = _make_run(
        provider="synthpanel/claude-haiku-4-5",
        dataset="subpop",
        sps=0.83,
        n_questions=200,
        timestamp="2026-04-14T10:00:00Z",
        token_usage={
            "input_tokens": 2_000_000,
            "output_tokens": 500_000,
            "call_count": 200,
            "source": "measured",
        },
    )
    gemini_no_tokens = _make_run(
        provider="synthpanel/gemini-2.5-flash-lite",
        dataset="subpop",
        sps=0.78,
        n_questions=200,
        timestamp="2026-04-14T10:05:00Z",
        # no token_usage — pre-Slice-2 row
    )
    ensemble_blend = _make_run(
        provider="ensemble/3-model-blend",
        dataset="subpop",
        sps=0.85,
        n_questions=200,
        timestamp="2026-04-14T10:10:00Z",
        ensemble_sources=[
            {
                "file": "h.json",
                "provider": "synthpanel/claude-haiku-4-5",
                "weight": 0.5,
            },
            {
                "file": "g.json",
                "provider": "synthpanel/gemini-2.5-flash-lite",
                "weight": 0.5,
            },
        ],
    )

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    (results_dir / "haiku.json").write_text(json.dumps(haiku_with_tokens))
    (results_dir / "gemini.json").write_text(json.dumps(gemini_no_tokens))
    (results_dir / "ensemble.json").write_text(json.dumps(ensemble_blend))

    out_path = tmp_path / "leaderboard.json"
    publish_leaderboard_data(results_dir, out_path)
    data = json.loads(out_path.read_text())

    # Top-level shape
    assert "pricing_snapshot" in data
    assert data["pricing_snapshot"]["snapshot_date"] == CURRENT_SNAPSHOT_DATE

    by_provider = {e["provider"]: e for e in data["entries"]}

    # Haiku row carries all four cost fields with measured cost > 0.
    haiku_entry = next(e for e in data["entries"] if "haiku" in e["model"].lower())
    expected_haiku_cost = (
        2_000_000 * HAIKU.input_cost_per_million
        + 500_000 * HAIKU.output_cost_per_million
    ) / 1_000_000
    assert haiku_entry["cost_usd"] == pytest.approx(expected_haiku_cost, rel=1e-5)
    assert haiku_entry["cost_per_100q"] == pytest.approx(
        expected_haiku_cost / 200 * 100, rel=1e-5
    )
    assert haiku_entry["cost_per_sps_point"] == pytest.approx(
        expected_haiku_cost / 0.83, rel=1e-5
    )
    assert haiku_entry["is_cost_estimated"] is False

    # Gemini row (no token_usage) — #316 estimate from config
    # (samples_per_question=5 × n_evaluated=200 = 1000 calls at the
    # documented per-call token constants), clearly marked estimated.
    FLASH_LITE = synth_panel_cost.GEMINI_FLASH_LITE_PRICING
    expected_gemini_cost = (
        1000
        * (
            124 * FLASH_LITE.input_cost_per_million
            + 4 * FLASH_LITE.output_cost_per_million
        )
        / 1_000_000
    )
    gemini_entry = next(e for e in data["entries"] if "gemini" in e["model"].lower())
    assert gemini_entry["cost_usd"] == pytest.approx(expected_gemini_cost, rel=1e-5)
    assert gemini_entry["cost_per_100q"] == pytest.approx(
        expected_gemini_cost / 200 * 100, rel=1e-5
    )
    assert gemini_entry["is_cost_estimated"] is True
    # The estimation constant must never masquerade as a measurement.
    assert gemini_entry["tokens_per_response"] is None

    # Ensemble row — haiku constituent measured + gemini constituent
    # estimated → summed cost, marked estimated.
    ensemble_entry = next(e for e in data["entries"] if e["is_ensemble"])
    assert ensemble_entry["cost_usd"] == pytest.approx(
        expected_haiku_cost + expected_gemini_cost, rel=1e-5
    )
    assert ensemble_entry["is_cost_estimated"] is True
    assert ensemble_entry["cost_per_response"] is None

    # Sanity: not ranking these entries away
    assert {e["dataset"] for e in data["entries"]} == {"subpop"}
    assert by_provider  # at least one entry indexed by display name


# ---------------------------------------------------------------------------
# Per-response economics + latency (sb-293)
# ---------------------------------------------------------------------------


def test_cost_per_response_and_tokens_per_response_from_call_count():
    """call_count drives both per-response cost and tokens/response."""
    aggregate = {
        "n_questions": 100,
        "token_usage": {
            "input_tokens": 600_000,
            "output_tokens": 300_000,
            "call_count": 300,  # 3 samples/question × 100 q
            "source": "measured",
        },
    }
    result = _compute_cost_fields(
        aggregate,
        {"provider": "raw-anthropic/claude-haiku-4-5"},
        {"n": 100, "sps": 0.8},
    )
    expected_cost = (
        600_000 * HAIKU.input_cost_per_million + 300_000 * HAIKU.output_cost_per_million
    ) / 1_000_000
    assert result["cost_per_response"] == pytest.approx(expected_cost / 300, rel=1e-5)
    assert result["tokens_per_response"] == pytest.approx(900_000 / 300, rel=1e-5)


def test_cost_per_response_null_when_call_count_missing():
    """No call_count → per-response cost/tokens stay null (denominator unknown)."""
    aggregate = {
        "n_questions": 100,
        "token_usage": {
            "input_tokens": 600_000,
            "output_tokens": 300_000,
            # call_count omitted
            "source": "measured",
        },
    }
    result = _compute_cost_fields(
        aggregate,
        {"provider": "raw-anthropic/claude-haiku-4-5"},
        {"n": 100, "sps": 0.8},
    )
    assert result["cost_per_response"] is None
    assert result["tokens_per_response"] is None
    # The aggregate-level cost_usd / cost_per_100q still populate.
    assert result["cost_usd"] is not None


def test_compute_latency_fields_from_aggregate():
    """latency_seconds block in aggregate flows into p50/p95 entry fields."""
    aggregate = {
        "latency_seconds": {
            "mean": 1.2,
            "p50": 1.1,
            "p95": 2.4,
            "n": 100,
            "source": "measured",
        }
    }
    result = _compute_latency_fields(aggregate)
    assert result == {
        "latency_p50_seconds": pytest.approx(1.1),
        "latency_p95_seconds": pytest.approx(2.4),
    }


def test_compute_latency_fields_absent_block_returns_nulls():
    """Pre-instrumentation rows (no latency_seconds block) get nulls, not zeros."""
    assert _compute_latency_fields({}) == {
        "latency_p50_seconds": None,
        "latency_p95_seconds": None,
    }
    assert _compute_latency_fields({"latency_seconds": None}) == {
        "latency_p50_seconds": None,
        "latency_p95_seconds": None,
    }


def test_publish_surfaces_latency_and_per_response_columns(tmp_path: Path):
    """End-to-end: a run with token_usage + latency block → entry has all sb-293 fields."""
    instrumented = _make_run(
        provider="synthpanel/claude-haiku-4-5",
        dataset="subpop",
        sps=0.83,
        n_questions=200,
        timestamp="2026-05-14T10:00:00Z",
        token_usage={
            "input_tokens": 1_000_000,
            "output_tokens": 200_000,
            "call_count": 200,
            "source": "measured",
        },
    )
    # Splice in the latency aggregate that report.py would emit.
    instrumented["aggregate"]["latency_seconds"] = {
        "mean": 0.9,
        "p50": 0.8,
        "p95": 1.7,
        "n": 200,
        "source": "measured",
    }

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    (results_dir / "haiku.json").write_text(json.dumps(instrumented))

    out_path = tmp_path / "leaderboard.json"
    publish_leaderboard_data(results_dir, out_path)
    data = json.loads(out_path.read_text())

    entry = next(e for e in data["entries"] if "haiku" in e["model"].lower())
    assert entry["cost_per_response"] is not None
    assert entry["cost_per_response"] > 0
    assert entry["tokens_per_response"] == pytest.approx(1_200_000 / 200, rel=1e-5)
    assert entry["latency_p50_seconds"] == pytest.approx(0.8)
    assert entry["latency_p95_seconds"] == pytest.approx(1.7)
