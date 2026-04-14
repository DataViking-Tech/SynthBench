"""Tests for contamination detection (convergence + paraphrase sensitivity)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from synthbench.contamination import (
    convergence_analysis,
    convergence_to_json,
    deident_result_to_json,
    format_convergence_report,
    load_result_distributions,
    result_to_json,
    run_contamination_test,
    run_deident_test,
)
from synthbench.providers.base import Distribution, PersonaSpec, Provider, Response


def _write_result(tmp_path, name: str, provider: str, per_question: list[dict]) -> str:
    """Write a minimal synthbench result JSON file and return the path."""
    data = {
        "benchmark": "synthbench",
        "version": "0.1.0",
        "config": {
            "dataset": "opinionsqa",
            "provider": provider,
            "n_evaluated": len(per_question),
        },
        "scores": {"sps": 0.5},
        "aggregate": {},
        "per_question": per_question,
    }
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(data))
    return path


def _make_question(key: str, text: str, dist: dict[str, float]) -> dict:
    return {
        "key": key,
        "text": text,
        "options": list(dist.keys()),
        "human_distribution": {k: 0.25 for k in dist},
        "model_distribution": dist,
        "jsd": 0.1,
        "kendall_tau": 0.5,
        "parity": 0.6,
        "n_samples": 30,
    }


class TestLoadResultDistributions:
    def test_loads_valid_file(self, tmp_path):
        q = _make_question("Q1", "Test?", {"A": 0.5, "B": 0.5})
        path = _write_result(tmp_path, "r1", "model-a", [q])
        provider, dists, texts = load_result_distributions(path)
        assert provider == "model-a"
        assert "Q1" in dists
        assert dists["Q1"] == {"A": 0.5, "B": 0.5}
        assert texts["Q1"] == "Test?"

    def test_rejects_non_synthbench(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"benchmark": "other"}))
        with pytest.raises(ValueError, match="Not a synthbench"):
            load_result_distributions(path)


class TestConvergenceAnalysis:
    def test_identical_distributions_high_risk(self, tmp_path):
        """When all models produce identical distributions, contamination_risk = 1.0."""
        dist = {"A": 0.6, "B": 0.3, "C": 0.1}
        q = _make_question("Q1", "Same?", dist)

        f1 = _write_result(tmp_path, "r1", "model-a", [q])
        f2 = _write_result(tmp_path, "r2", "model-b", [q])
        f3 = _write_result(tmp_path, "r3", "model-c", [q])

        analysis = convergence_analysis([f1, f2, f3])

        assert analysis.n_models == 3
        assert analysis.n_questions == 1
        assert analysis.questions[0].contamination_risk == pytest.approx(1.0)
        assert analysis.questions[0].mean_std == pytest.approx(0.0)

    def test_divergent_distributions_low_risk(self, tmp_path):
        """When models produce very different distributions, risk is low."""
        q1 = _make_question("Q1", "Div?", {"A": 1.0, "B": 0.0})
        q2 = _make_question("Q1", "Div?", {"A": 0.0, "B": 1.0})

        f1 = _write_result(tmp_path, "r1", "model-a", [q1])
        f2 = _write_result(tmp_path, "r2", "model-b", [q2])

        analysis = convergence_analysis([f1, f2])

        assert analysis.n_questions == 1
        q = analysis.questions[0]
        # std of [1.0, 0.0] = 0.5, std of [0.0, 1.0] = 0.5
        # mean_std = 0.5, contamination_risk = 1 - (0.5/0.5) = 0.0
        assert q.contamination_risk == pytest.approx(0.0)
        assert q.mean_std == pytest.approx(0.5)

    def test_min_models_filter(self, tmp_path):
        """Questions appearing in fewer than min_models files are excluded."""
        q_shared = _make_question("Q1", "Shared", {"A": 0.5, "B": 0.5})
        q_unique = _make_question("Q2", "Unique", {"A": 0.8, "B": 0.2})

        f1 = _write_result(tmp_path, "r1", "model-a", [q_shared, q_unique])
        f2 = _write_result(tmp_path, "r2", "model-b", [q_shared])
        f3 = _write_result(tmp_path, "r3", "model-c", [q_shared])

        analysis = convergence_analysis([f1, f2, f3], min_models=3)

        assert analysis.n_questions == 1
        assert analysis.questions[0].key == "Q1"

    def test_needs_at_least_2_files(self, tmp_path):
        q = _make_question("Q1", "Solo", {"A": 1.0})
        f1 = _write_result(tmp_path, "r1", "model-a", [q])

        with pytest.raises(ValueError, match="at least 2"):
            convergence_analysis([f1])

    def test_risk_categories(self, tmp_path):
        """Verify high/medium/low risk bucketing."""
        # High risk: identical
        q_same = _make_question("Q_HIGH", "Same", {"A": 0.8, "B": 0.2})
        # Medium risk: moderate divergence
        q_med_a = _make_question("Q_MED", "Med", {"A": 0.7, "B": 0.3})
        q_med_b = _make_question("Q_MED", "Med", {"A": 0.5, "B": 0.5})
        # Low risk: strong divergence
        q_low_a = _make_question("Q_LOW", "Low", {"A": 1.0, "B": 0.0})
        q_low_b = _make_question("Q_LOW", "Low", {"A": 0.0, "B": 1.0})

        f1 = _write_result(tmp_path, "r1", "model-a", [q_same, q_med_a, q_low_a])
        f2 = _write_result(tmp_path, "r2", "model-b", [q_same, q_med_b, q_low_b])

        analysis = convergence_analysis([f1, f2])

        assert analysis.n_questions == 3
        assert analysis.high_risk_count >= 1
        assert analysis.low_risk_count >= 1

    def test_duplicate_provider_names(self, tmp_path):
        """Multiple files from same provider get deduplicated names."""
        q = _make_question("Q1", "Dup", {"A": 0.5, "B": 0.5})
        f1 = _write_result(tmp_path, "r1", "model-a", [q])
        f2 = _write_result(tmp_path, "r2", "model-a", [q])

        analysis = convergence_analysis([f1, f2])
        assert analysis.n_models == 2
        assert len(set(analysis.model_names)) == 2

    def test_partial_overlap(self, tmp_path):
        """Questions not in all files still get analyzed if >= min_models."""
        q1 = _make_question("Q1", "Both", {"A": 0.5, "B": 0.5})
        q2 = _make_question("Q2", "Only A", {"A": 0.9, "B": 0.1})
        q3 = _make_question("Q3", "Only B", {"A": 0.1, "B": 0.9})

        f1 = _write_result(tmp_path, "r1", "model-a", [q1, q2])
        f2 = _write_result(tmp_path, "r2", "model-b", [q1, q3])

        analysis = convergence_analysis([f1, f2], min_models=2)
        # Only Q1 is in both
        assert analysis.n_questions == 1
        assert analysis.questions[0].key == "Q1"


class TestFormatAndSerialize:
    def test_format_report_contains_key_sections(self, tmp_path):
        dist = {"A": 0.5, "B": 0.5}
        q = _make_question("Q1", "Test question text", dist)
        f1 = _write_result(tmp_path, "r1", "model-a", [q])
        f2 = _write_result(tmp_path, "r2", "model-b", [q])

        analysis = convergence_analysis([f1, f2])
        report = format_convergence_report(analysis)

        assert "Cross-Model Convergence Analysis" in report
        assert "Risk Distribution" in report
        assert "model-a" in report
        assert "model-b" in report
        assert "Highest Contamination Risk" in report

    def test_json_serialization_roundtrip(self, tmp_path):
        dist = {"A": 0.5, "B": 0.5}
        q = _make_question("Q1", "Test?", dist)
        f1 = _write_result(tmp_path, "r1", "model-a", [q])
        f2 = _write_result(tmp_path, "r2", "model-b", [q])

        analysis = convergence_analysis([f1, f2])
        data = convergence_to_json(analysis)

        assert data["type"] == "contamination_convergence"
        assert data["n_models"] == 2
        assert data["n_questions"] == 1
        assert len(data["per_question"]) == 1
        assert "contamination_risk" in data["per_question"][0]
        # Verify it's JSON-serializable
        json.dumps(data)


# ---------------------------------------------------------------------------
# Paraphrase sensitivity
# ---------------------------------------------------------------------------


class _StaticDistributionProvider(Provider):
    """Provider that returns caller-controlled distributions per prompt.

    ``distributions_by_text`` maps prompt text to a list of probabilities in
    option order. Unknown prompts return uniform.
    """

    def __init__(self, distributions_by_text: dict[str, list[float]]):
        self._by_text = distributions_by_text

    @property
    def name(self) -> str:
        return "stub/paraphrase"

    @property
    def supports_distribution(self) -> bool:
        return True

    async def respond(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
    ) -> Response:  # pragma: no cover - not used by the test path
        return Response(selected_option=options[0])

    async def get_distribution(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
        n_samples: int | None = None,
    ) -> Distribution:
        probs = self._by_text.get(question)
        if probs is None:
            probs = [1.0 / len(options)] * len(options)
        return Distribution(
            probabilities=list(probs),
            method="stub",
            n_samples=n_samples or 1,
        )


def _write_paraphrase_suite(tmp_path: Path, items: list[dict]) -> Path:
    suite = {
        "suite": "paraphrase_test",
        "version": "test",
        "n_originals": len(items),
        "n_paraphrases_per": len(items[0]["paraphrases"]) if items else 0,
        "n_total": sum(1 + len(it["paraphrases"]) for it in items),
        "items": items,
    }
    path = tmp_path / "paraphrase_test.json"
    path.write_text(json.dumps(suite))
    return path


class TestRunContaminationTest:
    def test_identical_paraphrase_distributions_zero_sensitivity(self, tmp_path):
        """When paraphrase distributions match the original, sensitivity = 0."""
        options = ["Yes", "No"]
        human = {"Yes": 0.6, "No": 0.4}
        item = {
            "key": "Q1",
            "original_text": "Are you happy?",
            "paraphrases": ["Do you feel happy?", "Would you say you are happy?"],
            "options": options,
            "human_distribution": human,
        }
        suite_path = _write_paraphrase_suite(tmp_path, [item])

        # Every prompt returns [0.6, 0.4] — same as the human dist.
        same = [0.6, 0.4]
        provider = _StaticDistributionProvider(
            {
                "Are you happy?": same,
                "Do you feel happy?": same,
                "Would you say you are happy?": same,
            }
        )

        result = asyncio.run(
            run_contamination_test(
                provider=provider,
                samples_per_question=1,
                concurrency=4,
                suite_path=suite_path,
            )
        )

        assert result.n_originals == 1
        assert result.n_paraphrases_per == 2
        assert len(result.per_question) == 1
        q = result.per_question[0]
        assert q.original_parity == pytest.approx(q.mean_paraphrase_parity)
        assert q.delta == pytest.approx(0.0)
        assert q.sensitivity_pct == pytest.approx(0.0)
        assert result.sensitivity_pct == pytest.approx(0.0)
        # Original and adjusted SPS agree when everything is identical.
        assert result.original_sps == pytest.approx(result.adjusted_sps)

    def test_paraphrase_degrades_parity_positive_sensitivity(self, tmp_path):
        """When paraphrases degrade parity, sensitivity_pct is positive."""
        options = ["A", "B"]
        human = {"A": 1.0, "B": 0.0}
        item = {
            "key": "Q1",
            "original_text": "original",
            "paraphrases": ["p1", "p2", "p3"],
            "options": options,
            "human_distribution": human,
        }
        suite_path = _write_paraphrase_suite(tmp_path, [item])

        provider = _StaticDistributionProvider(
            {
                "original": [1.0, 0.0],  # perfect match
                "p1": [0.5, 0.5],
                "p2": [0.5, 0.5],
                "p3": [0.5, 0.5],
            }
        )

        result = asyncio.run(
            run_contamination_test(
                provider=provider,
                samples_per_question=1,
                concurrency=4,
                suite_path=suite_path,
            )
        )

        q = result.per_question[0]
        assert q.original_parity > q.mean_paraphrase_parity
        assert q.delta > 0
        assert q.sensitivity_pct > 0
        assert result.sensitivity_pct == pytest.approx(q.sensitivity_pct)

    def test_result_to_json_structure(self, tmp_path):
        options = ["A", "B"]
        human = {"A": 0.5, "B": 0.5}
        item = {
            "key": "Q1",
            "original_text": "text",
            "paraphrases": ["p1"],
            "options": options,
            "human_distribution": human,
        }
        suite_path = _write_paraphrase_suite(tmp_path, [item])

        provider = _StaticDistributionProvider({})
        result = asyncio.run(
            run_contamination_test(
                provider=provider,
                samples_per_question=1,
                concurrency=2,
                suite_path=suite_path,
            )
        )

        data = result_to_json(result)

        assert data["benchmark"] == "synthbench"
        assert data["type"] == "contamination_paraphrase"
        assert data["provider"] == "stub/paraphrase"
        assert data["config"]["n_originals"] == 1
        assert data["config"]["n_paraphrases_per"] == 1
        assert "contamination_sensitivity" in data["aggregate"]
        assert "original_sps" in data["aggregate"]
        assert "adjusted_sps" in data["aggregate"]
        assert len(data["per_question"]) == 1
        pq = data["per_question"][0]
        assert pq["key"] == "Q1"
        assert pq["paraphrases"] == ["p1"]
        # Result must be JSON-serializable end-to-end.
        json.dumps(data)

    def test_empty_suite_raises(self, tmp_path):
        suite_path = _write_paraphrase_suite(tmp_path, [])
        provider = _StaticDistributionProvider({})
        with pytest.raises(ValueError, match="empty"):
            asyncio.run(
                run_contamination_test(
                    provider=provider,
                    samples_per_question=1,
                    concurrency=2,
                    suite_path=suite_path,
                )
            )

    def test_bundled_deident_suite_matches_header(self):
        """The shipped de-identification suite has consistent header counts."""
        suite_path = (
            Path(__file__).parent.parent
            / "src"
            / "synthbench"
            / "suites"
            / "deident_test.json"
        )
        with open(suite_path) as f:
            suite = json.load(f)
        items = suite["items"]
        assert len(items) == suite["n_topics"] == 20
        assert suite["n_levels"] == 5
        assert len(suite["level_labels"]) == 5
        for item in items:
            assert len(item["levels"]) == 5, item["key"]
            assert "key" in item and "topic" in item
        assert suite["n_total"] == 20 * 5

    def test_handles_zero_original_parity(self, tmp_path):
        """Guard against division-by-zero in the sensitivity ratio."""
        options = ["A", "B"]
        # Human says A=1.0, model says B=1.0 → parity = 0 (worst case).
        human = {"A": 1.0, "B": 0.0}
        item = {
            "key": "Q1",
            "original_text": "original",
            "paraphrases": ["p1"],
            "options": options,
            "human_distribution": human,
        }
        suite_path = _write_paraphrase_suite(tmp_path, [item])

        provider = _StaticDistributionProvider(
            {"original": [0.0, 1.0], "p1": [0.0, 1.0]}
        )

        result = asyncio.run(
            run_contamination_test(
                provider=provider,
                samples_per_question=1,
                concurrency=2,
                suite_path=suite_path,
            )
        )

        q = result.per_question[0]
        # With parity=0, sensitivity_pct must be 0 (not NaN/inf).
        assert q.original_parity == pytest.approx(0.0)
        assert q.sensitivity_pct == 0.0
        assert result.sensitivity_pct == 0.0


# ---------------------------------------------------------------------------
# De-identification sensitivity
# ---------------------------------------------------------------------------


def _write_deident_suite(
    tmp_path: Path,
    items: list[dict],
    *,
    options: list[str] | None = None,
    level_labels: list[str] | None = None,
) -> Path:
    n_levels = len(items[0]["levels"]) if items else 0
    suite = {
        "suite": "deident_test",
        "version": "test",
        "n_topics": len(items),
        "n_levels": n_levels,
        "n_total": len(items) * n_levels,
        "level_labels": level_labels or [f"level_{i + 1}" for i in range(n_levels)],
        "items": items,
    }
    if options is not None:
        suite["options"] = options
    path = tmp_path / "deident_test.json"
    path.write_text(json.dumps(suite))
    return path


class TestRunDeidentTest:
    def test_identical_level_distributions_zero_variance(self, tmp_path):
        """All five levels return the same dist -> pairwise JSD = 0."""
        options = ["Yes", "No"]
        item = {
            "key": "topic1",
            "topic": "A shared topic",
            "levels": [f"L{i} text" for i in range(1, 6)],
        }
        suite_path = _write_deident_suite(tmp_path, [item], options=options)

        same = [0.7, 0.3]
        provider = _StaticDistributionProvider(
            {f"L{i} text": same for i in range(1, 6)}
        )

        result = asyncio.run(
            run_deident_test(
                provider=provider,
                samples_per_question=1,
                concurrency=4,
                suite_path=suite_path,
            )
        )

        assert result.n_topics == 1
        assert result.n_levels == 5
        assert result.mean_pairwise_jsd == pytest.approx(0.0)
        assert result.mean_option_std == pytest.approx(0.0)
        assert result.mean_drift_l1_to_l5 == pytest.approx(0.0)

        t = result.per_topic[0]
        # pairwise_jsd matrix is 5x5, zero everywhere
        assert len(t.pairwise_jsd) == 5
        for row in t.pairwise_jsd:
            assert all(cell == pytest.approx(0.0) for cell in row)

    def test_divergent_levels_positive_variance(self, tmp_path):
        """Distinct distributions across levels yield positive JSD."""
        options = ["A", "B"]
        item = {
            "key": "topic1",
            "topic": "Topic",
            "levels": ["L1", "L2", "L3", "L4", "L5"],
        }
        suite_path = _write_deident_suite(tmp_path, [item], options=options)

        provider = _StaticDistributionProvider(
            {
                "L1": [1.0, 0.0],  # strongly A (brand known)
                "L2": [0.9, 0.1],
                "L3": [0.5, 0.5],
                "L4": [0.2, 0.8],
                "L5": [0.0, 1.0],  # strongly B (brand stripped)
            }
        )

        result = asyncio.run(
            run_deident_test(
                provider=provider,
                samples_per_question=1,
                concurrency=4,
                suite_path=suite_path,
            )
        )

        t = result.per_topic[0]
        assert t.mean_pairwise_jsd > 0.0
        assert t.drift_l1_to_l5 > t.mean_pairwise_jsd * 0.5
        assert t.mean_option_std > 0.0
        assert result.mean_pairwise_jsd == pytest.approx(t.mean_pairwise_jsd)

    def test_per_item_options_override_suite_options(self, tmp_path):
        """Item-level options take precedence over suite-level options."""
        item = {
            "key": "t1",
            "topic": "Topic",
            "levels": ["L1", "L2", "L3", "L4", "L5"],
            "options": ["X", "Y", "Z"],
        }
        # Suite-level options should be ignored in favor of item-level.
        suite_path = _write_deident_suite(
            tmp_path, [item], options=["Ignored1", "Ignored2"]
        )

        uniform = [1.0 / 3] * 3
        provider = _StaticDistributionProvider({f"L{i}": uniform for i in range(1, 6)})
        result = asyncio.run(
            run_deident_test(
                provider=provider,
                samples_per_question=1,
                concurrency=2,
                suite_path=suite_path,
            )
        )
        assert result.per_topic[0].options == ["X", "Y", "Z"]

    def test_empty_suite_raises(self, tmp_path):
        path = tmp_path / "empty.json"
        path.write_text(
            json.dumps(
                {
                    "suite": "deident_test",
                    "version": "test",
                    "n_topics": 0,
                    "n_levels": 0,
                    "n_total": 0,
                    "items": [],
                }
            )
        )
        provider = _StaticDistributionProvider({})
        with pytest.raises(ValueError, match="empty"):
            asyncio.run(
                run_deident_test(
                    provider=provider,
                    samples_per_question=1,
                    concurrency=2,
                    suite_path=path,
                )
            )

    def test_inconsistent_level_count_raises(self, tmp_path):
        """All topics must have the same number of levels."""
        items = [
            {"key": "t1", "topic": "A", "levels": ["a", "b", "c", "d", "e"]},
            {"key": "t2", "topic": "B", "levels": ["a", "b", "c"]},
        ]
        suite_path = _write_deident_suite(tmp_path, items, options=["X", "Y"])
        provider = _StaticDistributionProvider({})
        with pytest.raises(ValueError, match="levels"):
            asyncio.run(
                run_deident_test(
                    provider=provider,
                    samples_per_question=1,
                    concurrency=2,
                    suite_path=suite_path,
                )
            )

    def test_missing_options_raises(self, tmp_path):
        """Topic with no options at either level raises a clear error."""
        item = {
            "key": "t1",
            "topic": "Topic",
            "levels": ["L1", "L2", "L3", "L4", "L5"],
        }
        suite_path = _write_deident_suite(tmp_path, [item], options=None)
        provider = _StaticDistributionProvider({})
        with pytest.raises(ValueError, match="options"):
            asyncio.run(
                run_deident_test(
                    provider=provider,
                    samples_per_question=1,
                    concurrency=2,
                    suite_path=suite_path,
                )
            )

    def test_deident_result_to_json_structure(self, tmp_path):
        options = ["A", "B"]
        item = {
            "key": "t1",
            "topic": "Topic label",
            "levels": ["L1", "L2", "L3", "L4", "L5"],
        }
        suite_path = _write_deident_suite(
            tmp_path,
            [item],
            options=options,
            level_labels=["l1", "l2", "l3", "l4", "l5"],
        )

        provider = _StaticDistributionProvider(
            {f"L{i}": [0.5, 0.5] for i in range(1, 6)}
        )
        result = asyncio.run(
            run_deident_test(
                provider=provider,
                samples_per_question=1,
                concurrency=2,
                suite_path=suite_path,
            )
        )

        data = deident_result_to_json(result)
        assert data["benchmark"] == "synthbench"
        assert data["type"] == "contamination_deident"
        assert data["provider"] == "stub/paraphrase"
        assert data["config"]["n_topics"] == 1
        assert data["config"]["n_levels"] == 5
        assert data["config"]["level_labels"] == ["l1", "l2", "l3", "l4", "l5"]
        assert "mean_pairwise_jsd" in data["aggregate"]
        assert "mean_option_std" in data["aggregate"]
        assert "mean_drift_l1_to_l5" in data["aggregate"]
        topic = data["per_topic"][0]
        assert topic["key"] == "t1"
        assert topic["topic"] == "Topic label"
        assert len(topic["level_distributions"]) == 5
        assert len(topic["pairwise_jsd"]) == 5
        matrix = topic["pairwise_jsd"]
        for i in range(len(matrix)):
            assert matrix[i][i] == pytest.approx(0.0)
            for j in range(len(matrix)):
                assert matrix[i][j] == pytest.approx(matrix[j][i])
        # End-to-end JSON serializable.
        json.dumps(data)
