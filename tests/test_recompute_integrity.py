"""Leaderboard-integrity tests: never trust submitter-supplied aggregates.

Covers the P0-4 fix end to end:

* tier-2 validation recomputes ``scores.sps`` / ``scores.p_refuse`` and
  hard-fails on fabricated values, recording which documented composite
  convention matched;
* publish recomputes every score from per-question rows and ranks by the
  recomputed SPS, warning (but not trusting) when the submitted value
  diverges;
* the published SPS confidence interval is a question-resampling bootstrap
  of the SPS composite itself (P2-4) and is null — never ``[0, 0]`` — when
  unavailable;
* ensemble runs publish a real ``n`` (P3 display bug: rank-1 rows showing
  "scored on zero questions").
"""

from __future__ import annotations

import json
import logging
import math

from click.testing import CliRunner

from synthbench.cli import main as cli_main
from synthbench.publish import publish_leaderboard_data, publish_runs
from synthbench.recompute import bootstrap_metric_cis, recompute_aggregates
from synthbench.runner import BenchmarkResult, QuestionResult
from synthbench.stats import question_set_hash
from synthbench.validation import validate_submission


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _pq_row(i: int, jsd: float, tau: float, m_ref: float, h_ref: float) -> dict:
    return {
        "key": f"Q{i:03d}",
        "text": f"question {i}",
        "options": ["A", "B", "C"],
        "human_distribution": {"A": 0.6, "B": 0.3, "C": 0.1},
        "model_distribution": {"A": 0.5, "B": 0.35, "C": 0.15},
        "jsd": jsd,
        "kendall_tau": tau,
        "parity": (1.0 - jsd + (1.0 + tau) / 2.0) / 2.0,
        "n_samples": 10,
        "n_parse_failures": 0,
        "model_refusal_rate": m_ref,
        "human_refusal_rate": h_ref,
        "temporal_year": 2024,
    }


def _varied_rows(n: int) -> list[dict]:
    """Per-question rows with metric spread (so bootstrap CIs have width)."""
    rows = []
    for i in range(n):
        jsd = 0.1 + 0.5 * (i % 7) / 7.0
        tau = -0.2 + 0.9 * (i % 5) / 5.0
        m_ref = 0.05 * (i % 3)
        h_ref = 0.05
        rows.append(_pq_row(i, jsd, tau, m_ref, h_ref))
    return rows


def _consistent_submission(
    n: int = 20, dataset: str = "ntia", provider: str = "test-provider"
) -> dict:
    """Submission whose aggregates all reconcile with its per-question rows.

    Note the per-question ``jsd``/``kendall_tau`` columns here are synthetic
    (not derived from the embedded distributions), so tests that need the
    tier-2 per-question distribution recompute to pass should use
    ``tier2``-targeted assertions on the aggregate codes only. For publish
    (which reads the metric columns, not the distributions) they are exact.
    """
    rows = _varied_rows(n)
    rec = recompute_aggregates(rows)
    assert rec is not None
    return {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "timestamp": "2026-07-01T00:00:00+00:00",
        "config": {
            "dataset": dataset,
            "provider": provider,
            "n_requested": n,
            "n_evaluated": n,
            "question_set_hash": question_set_hash([q["key"] for q in rows]),
            "parse_failure_rate": 0.0,
        },
        "scores": {
            "sps": round(rec.sps, 6),
            "p_dist": round(rec.p_dist, 6),
            "p_rank": round(rec.p_rank, 6),
            "p_refuse": round(rec.p_refuse, 6),
        },
        "aggregate": {
            "mean_jsd": round(rec.mean_jsd, 6),
            "median_jsd": round(rec.median_jsd, 6),
            "mean_kendall_tau": round(rec.mean_kendall_tau, 6),
            "composite_parity": round(rec.parity_two, 6),
            "n_questions": n,
        },
        "per_question": rows,
    }


def _agg_codes(report) -> set[str]:
    """Error codes from the aggregate-recompute layer only.

    The synthetic fixtures carry per-question metric columns that don't
    derive from the embedded distributions, so PER_Q_* codes fire by
    construction and are not what these tests assert on.
    """
    return {
        i.code
        for i in report.errors
        if not i.code.startswith("PER_Q") and i.code != "RECOMPUTE_ERROR"
    }


# ---------------------------------------------------------------------------
# Validation: fabricated aggregates hard-fail
# ---------------------------------------------------------------------------


class TestValidationRecomputesSps:
    def test_fabricated_sps_rejected(self):
        """A hand-edited scores.sps (the P0-4 attack) is an ERROR."""
        sub = _consistent_submission()
        sub["scores"]["sps"] = 0.99
        report = validate_submission(sub, tier1=False, tier2=True)
        assert "SCORES_SPS" in _agg_codes(report)
        assert "sps_convention" not in report.metadata

    def test_fabricated_p_refuse_rejected(self):
        sub = _consistent_submission()
        sub["scores"]["p_refuse"] = 0.999999
        report = validate_submission(sub, tier1=False, tier2=True)
        errors_on_refuse = [i for i in report.errors if i.path == "scores.p_refuse"]
        assert errors_on_refuse, report.format()

    def test_sps_convention_recorded_full_sps(self):
        sub = _consistent_submission()
        report = validate_submission(sub, tier1=False, tier2=True)
        assert report.metadata.get("sps_convention") == "sps"
        assert "SCORES_SPS" not in _agg_codes(report)
        assert "sps convention: sps" in report.format()

    def test_sps_convention_recorded_parity_two(self):
        sub = _consistent_submission()
        rec = recompute_aggregates(sub["per_question"])
        sub["scores"]["sps"] = round(rec.parity_two, 6)
        report = validate_submission(sub, tier1=False, tier2=True)
        assert report.metadata.get("sps_convention") == "parity-2"
        assert "SCORES_SPS" not in _agg_codes(report)

    def test_composite_parity_cannot_cherry_pick_conventions(self):
        """sps identified as parity-2 ⇒ composite_parity may not claim the
        (different, higher) full-SPS mean — "whichever is higher" is out."""
        sub = _consistent_submission()
        rec = recompute_aggregates(sub["per_question"])
        # Ensure the two conventions are actually distinguishable here.
        assert abs(rec.sps - rec.parity_two) > 0.02
        sub["scores"]["sps"] = round(rec.parity_two, 6)
        sub["aggregate"]["composite_parity"] = round(rec.sps, 6)
        report = validate_submission(sub, tier1=False, tier2=True)
        assert "AGG_COMPOSITE" in _agg_codes(report)

    def test_composite_parity_may_match_identified_sps_convention(self):
        """The `synthbench ensemble` convention: composite_parity == sps
        (full mean) is internally consistent and accepted."""
        sub = _consistent_submission()
        rec = recompute_aggregates(sub["per_question"])
        sub["aggregate"]["composite_parity"] = round(rec.sps, 6)
        report = validate_submission(sub, tier1=False, tier2=True)
        assert "AGG_COMPOSITE" not in _agg_codes(report)

    def test_extended_components_enter_the_composite(self):
        """Conditioned runs: sps == mean(p_dist, p_rank, p_refuse, p_sub,
        p_cond) must be accepted under the full-SPS convention."""
        sub = _consistent_submission()
        rec = recompute_aggregates(sub["per_question"])
        p_sub, p_cond = 0.9, 0.05
        sub["scores"]["p_sub"] = p_sub
        sub["scores"]["p_cond"] = p_cond
        sub["scores"]["sps"] = round(
            (rec.p_dist + rec.p_rank + rec.p_refuse + p_sub + p_cond) / 5.0, 6
        )
        report = validate_submission(sub, tier1=False, tier2=True)
        assert "SCORES_SPS" not in _agg_codes(report)
        assert report.metadata.get("sps_convention") == "sps"


# ---------------------------------------------------------------------------
# Publish: recomputed ranking + divergence warning
# ---------------------------------------------------------------------------


def _write(results_dir, name: str, payload: dict) -> None:
    (results_dir / name).write_text(json.dumps(payload))


class TestPublishRecomputedRanking:
    def test_ranking_ignores_submitted_sps(self, tmp_path, caplog):
        """A run claiming sps=0.99 over weak rows must NOT outrank a run
        whose rows genuinely score higher; the published sps is the
        recomputed one and the divergence is logged."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()

        weak = _consistent_submission(
            n=20, provider="openrouter/anthropic/claude-haiku-4-5"
        )
        weak_recomputed = weak["scores"]["sps"]
        weak["scores"]["sps"] = 0.99  # fabricated — must be ignored

        strong_rows = [
            _pq_row(i, jsd=0.05, tau=0.8, m_ref=0.05, h_ref=0.05) for i in range(20)
        ]
        strong = _consistent_submission(n=20, provider="openrouter/openai/gpt-4o-mini")
        strong["per_question"] = strong_rows
        strong_rec = recompute_aggregates(strong_rows)
        strong["scores"] = {"sps": round(strong_rec.sps, 6)}

        _write(results_dir, "weak_fabricated.json", weak)
        _write(results_dir, "strong_honest.json", strong)

        out = tmp_path / "leaderboard.json"
        with caplog.at_level(logging.WARNING, logger="synthbench.publish"):
            publish_leaderboard_data(results_dir, out)
        payload = json.loads(out.read_text())

        entries = sorted(payload["entries"], key=lambda e: e["rank"])
        assert len(entries) == 2
        # The honest run ranks first despite the lower *submitted* number.
        assert "GPT-4o-mini" in entries[0]["model"]
        assert entries[0]["sps"] == round(strong_rec.sps, 6)
        # The fabricated 0.99 is nowhere; the recomputed value is published.
        assert entries[1]["sps"] == round(weak_recomputed, 6)
        assert all(e["sps"] != 0.99 for e in entries)

        # Divergence warning names the offending run.
        warned = [
            rec.message
            for rec in caplog.records
            if "diverges from recomputed" in rec.getMessage()
        ]
        assert any("weak_fabricated" in m for m in warned), caplog.text

    def test_sps_ci_contains_recomputed_point_estimate(self, tmp_path):
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        sub = _consistent_submission(n=40)
        _write(results_dir, "run.json", sub)

        out = tmp_path / "leaderboard.json"
        publish_leaderboard_data(results_dir, out)
        entry = json.loads(out.read_text())["entries"][0]

        assert entry["ci_lower"] is not None and entry["ci_upper"] is not None
        assert entry["ci_lower"] < entry["ci_upper"]
        assert entry["ci_lower"] <= entry["sps"] <= entry["ci_upper"], entry

    def test_unavailable_ci_publishes_null_not_zero(self, tmp_path):
        """Fewer than 5 scored questions ⇒ no CI ⇒ null, never [0, 0]."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        sub = _consistent_submission(n=3)
        _write(results_dir, "tiny.json", sub)

        out = tmp_path / "leaderboard.json"
        publish_leaderboard_data(results_dir, out)
        entry = json.loads(out.read_text())["entries"][0]

        assert entry["ci_lower"] is None
        assert entry["ci_upper"] is None

    def test_run_detail_per_metric_ci_recomputed_on_sps(self, tmp_path):
        """The run-detail per_metric_ci is recomputed at publish time and its
        sps interval contains the recomputed sps (P2-4: legacy files stored a
        2-metric parity CI under the 'sps' key)."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        sub = _consistent_submission(n=40, dataset="ntia")
        # Poison the stored CI the way legacy files are: an interval that
        # does not contain the sps point estimate.
        sub["aggregate"]["per_metric_ci"] = {"sps": [0.1, 0.2]}
        _write(results_dir, "run.json", sub)

        out_dir = tmp_path / "site"
        publish_runs(results_dir, out_dir)
        detail = json.loads((out_dir / "run" / "run.json").read_text())

        lo, hi = detail["aggregate"]["per_metric_ci"]["sps"]
        assert lo <= detail["scores"]["sps"] <= hi
        assert (lo, hi) != (0.1, 0.2)


# ---------------------------------------------------------------------------
# Ensemble n (source + defensive publish)
# ---------------------------------------------------------------------------


class TestEnsembleN:
    def _source_run(self, provider: str, shift: float) -> dict:
        rows = []
        for i in range(12):
            base = {"A": 0.5 + shift, "B": 0.35 - shift, "C": 0.15}
            rows.append(
                {
                    "key": f"Q{i:03d}",
                    "text": f"question {i}",
                    "options": ["A", "B", "C"],
                    "human_distribution": {"A": 0.6, "B": 0.3, "C": 0.1},
                    "model_distribution": base,
                    "jsd": 0.1,
                    "kendall_tau": 0.5,
                    "parity": 0.825,
                    "n_samples": 10,
                    "model_refusal_rate": 0.02,
                    "human_refusal_rate": 0.05,
                }
            )
        return {
            "benchmark": "synthbench",
            "version": "0.1.0",
            "config": {"dataset": "ntia", "provider": provider},
            "scores": {},
            "aggregate": {"n_questions": len(rows)},
            "per_question": rows,
        }

    def test_ensemble_command_populates_n_evaluated(self, tmp_path):
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        a.write_text(json.dumps(self._source_run("prov/a", 0.0)))
        b.write_text(json.dumps(self._source_run("prov/b", 0.05)))
        out_dir = tmp_path / "out"

        runner = CliRunner()
        result = runner.invoke(
            cli_main, ["ensemble", str(a), str(b), "--output", str(out_dir)]
        )
        assert result.exit_code == 0, result.output

        produced = list(out_dir.glob("*.json"))
        assert len(produced) == 1
        blend = json.loads(produced[0].read_text())
        assert blend["config"]["n_evaluated"] == 12
        assert blend["aggregate"]["n_questions"] == 12

        # The blend must also survive its own validator: aggregates are
        # recomputed from the blended per-question rows.
        report = validate_submission(blend)
        assert report.ok, report.format()
        assert report.metadata.get("sps_convention") == "sps"

    def test_publish_defends_against_legacy_ensemble_without_n(self, tmp_path):
        """Legacy ensemble rows (config.n_evaluated never written) must
        publish n from the per-question row count, not 0."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        legacy = _consistent_submission(
            n=20, dataset="ntia", provider="ensemble/3-model-blend"
        )
        del legacy["config"]["n_evaluated"]
        del legacy["config"]["n_requested"]
        _write(results_dir, "legacy_ensemble.json", legacy)

        out = tmp_path / "leaderboard.json"
        publish_leaderboard_data(results_dir, out)
        entry = json.loads(out.read_text())["entries"][0]
        assert entry["is_ensemble"] is True
        assert entry["n"] == 20

        out_dir = tmp_path / "site"
        publish_runs(results_dir, out_dir)
        index = json.loads((out_dir / "runs-index.json").read_text())
        assert index["runs"][0]["n_questions"] == 20
        detail = json.loads((out_dir / "run" / "legacy_ensemble.json").read_text())
        assert detail["n_evaluated"] == 20


# ---------------------------------------------------------------------------
# Runner: the stored SPS CI is a CI on SPS
# ---------------------------------------------------------------------------


def _question_result(i: int, jsd: float, tau: float, m_ref: float) -> QuestionResult:
    return QuestionResult(
        key=f"Q{i:03d}",
        text=f"question {i}",
        options=["A", "B"],
        human_distribution={"A": 0.6, "B": 0.4},
        model_distribution={"A": 0.55, "B": 0.45},
        jsd=jsd,
        kendall_tau=tau,
        parity=(1.0 - jsd + (1.0 + tau) / 2.0) / 2.0,
        n_samples=10,
        model_refusal_rate=m_ref,
        human_refusal_rate=0.05,
    )


class TestRunnerSpsCi:
    def _result(self, **kwargs) -> BenchmarkResult:
        questions = [
            _question_result(
                i,
                jsd=0.1 + 0.06 * (i % 5),
                tau=0.2 + 0.1 * (i % 4),
                m_ref=0.02 * (i % 3),
            )
            for i in range(24)
        ]
        return BenchmarkResult(
            provider_name="test-provider",
            dataset_name="ntia",
            questions=questions,
            **kwargs,
        )

    def test_sps_ci_contains_point_estimate(self):
        result = self._result()
        cis = result.per_metric_ci
        lo, hi = cis["sps"]
        assert lo < hi
        assert lo <= result.sps <= hi, (lo, result.sps, hi)
        # And it is NOT the legacy 2-metric parity interval: the parity mean
        # differs from sps here because p_refuse pulls the composite up.
        parity_mean = sum(q.parity for q in result.questions) / len(result.questions)
        assert not (lo <= parity_mean <= hi) or math.isclose(
            parity_mean, result.sps, abs_tol=0.02
        )

    def test_sps_ci_contains_point_estimate_with_fixed_components(self):
        """p_sub / p_cond shift the composite; the interval must follow."""
        result = self._result(group_scores={"grp:a": 0.8, "grp:b": 0.85})
        assert result.p_sub is not None
        cis = result.per_metric_ci
        lo, hi = cis["sps"]
        assert lo <= result.sps <= hi, (lo, result.sps, hi)


# ---------------------------------------------------------------------------
# recompute module unit coverage
# ---------------------------------------------------------------------------


class TestRecomputeModule:
    def test_returns_none_without_usable_rows(self):
        assert recompute_aggregates([]) is None
        assert recompute_aggregates([{"key": "Q1"}]) is None
        assert recompute_aggregates(None) is None

    def test_refusal_component_optional(self):
        rows = [{"key": f"Q{i}", "jsd": 0.2, "kendall_tau": 0.4} for i in range(6)]
        rec = recompute_aggregates(rows)
        assert rec.p_refuse is None
        assert set(rec.components) == {"p_dist", "p_rank"}
        # 2-component mean == parity_two when refusal data is absent.
        assert math.isclose(rec.sps, rec.parity_two)

    def test_bootstrap_needs_five_rows(self):
        rows = _varied_rows(4)
        assert bootstrap_metric_cis(rows) == {}

    def test_bootstrap_cis_contain_point_estimates(self):
        rows = _varied_rows(60)
        rec = recompute_aggregates(rows)
        cis = bootstrap_metric_cis(rows)
        for metric, value in (
            ("p_dist", rec.p_dist),
            ("p_rank", rec.p_rank),
            ("p_refuse", rec.p_refuse),
            ("sps", rec.sps),
        ):
            lo, hi = cis[metric]
            assert lo <= value <= hi, (metric, lo, value, hi)

    def test_bootstrap_deterministic(self):
        rows = _varied_rows(30)
        assert bootstrap_metric_cis(rows) == bootstrap_metric_cis(rows)
