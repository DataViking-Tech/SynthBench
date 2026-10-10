"""Public-mirror flow: private-holdout answers withheld client-side, scored
server-side on submission (docs/held-out.md)."""

from __future__ import annotations

import json
import random
import string

import pytest

from synthbench import human_distributions
from synthbench.datasets import opinionsqa as oqa
from synthbench.datasets.base import Dataset, Question
from synthbench.private_holdout import is_private_holdout
from synthbench.report import to_json, to_markdown
from synthbench.runner import BenchmarkRunner
from synthbench.validation import validate_submission
from synthbench.withheld import (
    WithheldScoringError,
    has_withheld_rows,
    score_withheld_rows,
)

OPTIONS = ["Yes", "No", "Not sure"]


def _keys(n_public: int, n_private: int) -> tuple[list[str], list[str]]:
    rng = random.Random(1)
    public: list[str] = []
    private: list[str] = []
    while len(public) < n_public or len(private) < n_private:
        k = "".join(rng.choices(string.ascii_uppercase, k=8)) + "_W26"
        bucket = private if is_private_holdout("opinionsqa", k) else public
        if len(bucket) < (n_private if bucket is private else n_public):
            bucket.append(k)
    return public, private


PUBLIC, PRIVATE = _keys(16, 4)


def _answers(i: int) -> dict[str, float]:
    a = 0.2 + 0.05 * (i % 7)
    b = 0.1 + 0.04 * (i % 5)
    return {"Yes": a, "No": b, "Not sure": 1.0 - a - b}


CANONICAL = {k: _answers(i) for i, k in enumerate(PUBLIC + PRIVATE)}


class _OpinionsQA(Dataset):
    def __init__(self, withhold: bool):
        self._withhold = withhold

    @property
    def name(self) -> str:
        return "opinionsqa"

    def load(self, n: int | None = None) -> list[Question]:
        qs = []
        for k in PUBLIC + PRIVATE:
            withheld = self._withhold and k in PRIVATE
            qs.append(
                Question(
                    key=k,
                    text=f"Question {k}?",
                    options=OPTIONS,
                    human_distribution={} if withheld else dict(CANONICAL[k]),
                    survey="ATP W26",
                    answer_withheld=withheld,
                )
            )
        return qs[:n] if n is not None else qs

    def info(self) -> dict:
        return {"name": "opinionsqa"}


async def _run(mock_provider, *, withhold: bool):
    runner = BenchmarkRunner(
        dataset=_OpinionsQA(withhold),
        provider=mock_provider,
        samples_per_question=5,
        concurrency=4,
    )
    return await runner.run()


# --- adapter -----------------------------------------------------------------


def _wave_file(tmp_path, keys):
    wave = tmp_path / "human_resp" / "American_Trends_Panel_W26"
    wave.mkdir(parents=True)
    (wave / "info.csv").write_text(
        ",key,question,references,option_ordinal\n"
        + "".join(
            f'{i},{k},"Q {k}?","[\'Yes\', \'No\']","[1.0, 2.0]"\n'
            for i, k in enumerate(keys)
        ),
        encoding="utf-8",
    )
    (wave / "NONE_data.json").write_text(
        json.dumps({k: {"NONE": {"Yes": 3.0, "No": 1.0}} for k in keys}),
        encoding="utf-8",
    )
    return wave


def test_withhold_private_answers_marks_only_private_keys(tmp_path):
    wave = _wave_file(tmp_path, PUBLIC[:3] + PRIVATE[:2])
    assert oqa.withhold_private_answers(tmp_path / "human_resp") == 2
    data = json.loads((wave / "NONE_data.json").read_text(encoding="utf-8"))
    for k in PRIVATE[:2]:
        assert data[k] == {"withheld": True}
    for k in PUBLIC[:3]:
        assert data[k] == {"NONE": {"Yes": 3.0, "No": 1.0}}


def test_adapter_loads_withheld_questions_and_caches_the_flag(tmp_path):
    _wave_file(tmp_path, PUBLIC[:3] + PRIVATE[:2])
    oqa.withhold_private_answers(tmp_path / "human_resp")
    ds = oqa.OpinionsQADataset(data_dir=tmp_path)
    questions = ds._process_raw_data(tmp_path)
    by_key = {q.key: q for q in questions}
    assert set(by_key) == set(PUBLIC[:3] + PRIVATE[:2])
    for k in PRIVATE[:2]:
        assert by_key[k].answer_withheld
        assert by_key[k].human_distribution == {}
    for k in PUBLIC[:3]:
        assert not by_key[k].answer_withheld
        assert by_key[k].human_distribution == pytest.approx({"Yes": 0.75, "No": 0.25})

    ds._save_cache(questions)
    cached = {q.key: q for q in ds.load()}
    assert {k for k, q in cached.items() if q.answer_withheld} == set(PRIVATE[:2])


def test_canonical_artifact_refuses_public_mirror_data(monkeypatch):
    from synthbench import datasets

    monkeypatch.setitem(datasets.DATASETS, "opinionsqa", lambda: _OpinionsQA(True))
    with pytest.raises(ValueError, match="withheld"):
        human_distributions.build_artifact("opinionsqa")


# --- runner / report ---------------------------------------------------------


@pytest.mark.asyncio
async def test_withheld_rows_are_sampled_but_not_scored(mock_provider):
    result = await _run(mock_provider, withhold=True)
    assert len(result.questions) == 20
    assert result.n_withheld == 4
    assert {q.key for q in result.scored} == set(PUBLIC)

    withheld = [q for q in result.questions if q.answer_withheld]
    assert all(q.model_distribution for q in withheld)
    assert all(q.jsd is None and q.kendall_tau is None for q in withheld)

    data = to_json(result)
    rows = {q["key"]: q for q in data["per_question"]}
    for k in PRIVATE:
        assert rows[k]["answer_withheld"] is True
        assert rows[k]["jsd"] is None
        assert "human_distribution" not in rows[k]
    assert data["aggregate"]["n_answers_withheld"] == 4
    assert "**Scored locally:** 16 questions" in to_markdown(result)


# --- validation --------------------------------------------------------------


def _codes(report) -> set[str]:
    return {i.code for i in report.issues}


@pytest.mark.asyncio
async def test_client_side_validation_accepts_withheld_rows(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    assert not {
        c for c in _codes(validate_submission(data)) if c.startswith("WITHHELD")
    }


@pytest.mark.asyncio
async def test_withheld_row_on_public_question_is_rejected(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    row = next(q for q in data["per_question"] if q["key"] == PUBLIC[0])
    row.update(answer_withheld=True, jsd=None, kendall_tau=None)
    row.pop("human_distribution", None)
    assert "WITHHELD_NOT_PRIVATE" in _codes(validate_submission(data))


@pytest.mark.asyncio
async def test_withheld_row_with_metrics_is_rejected(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    row = next(q for q in data["per_question"] if q["key"] == PRIVATE[0])
    row["jsd"] = 0.01
    assert "WITHHELD_HAS_METRICS" in _codes(validate_submission(data))


@pytest.mark.asyncio
async def test_pipeline_rejects_unscored_rows(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    assert "WITHHELD_UNSCORED" in _codes(validate_submission(data, require_scored=True))
    assert "WITHHELD_UNSCORED" in _codes(
        validate_submission(data, canonical_distributions=CANONICAL)
    )


# --- server-side scoring -----------------------------------------------------


@pytest.mark.asyncio
async def test_server_side_scoring_matches_a_full_local_run(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    full = to_json(await _run(mock_provider, withhold=False))

    assert has_withheld_rows(data)
    assert score_withheld_rows(data, CANONICAL) == 4
    assert not has_withheld_rows(data)

    rows = {q["key"]: q for q in data["per_question"]}
    full_rows = {q["key"]: q for q in full["per_question"]}
    for k in PRIVATE:
        assert rows[k]["scored_server_side"] is True
        for metric in ("jsd", "kendall_tau", "parity", "human_refusal_rate"):
            assert rows[k][metric] == pytest.approx(full_rows[k][metric], abs=1e-5)
    for metric in ("sps", "p_dist", "p_rank"):
        assert data["scores"][metric] == pytest.approx(full["scores"][metric], abs=1e-5)
    assert data["aggregate"]["mean_jsd"] == pytest.approx(
        full["aggregate"]["mean_jsd"], abs=1e-5
    )
    assert data["aggregate"]["n_scored_server_side"] == 4
    assert "n_answers_withheld" not in data["aggregate"]

    report = validate_submission(
        data, canonical_distributions=CANONICAL, require_scored=True
    )
    assert not {c for c in _codes(report) if c.startswith("WITHHELD")}


@pytest.mark.asyncio
async def test_scoring_needs_an_answer_for_every_withheld_row(mock_provider):
    data = to_json(await _run(mock_provider, withhold=True))
    partial = {k: v for k, v in CANONICAL.items() if k != PRIVATE[0]}
    with pytest.raises(WithheldScoringError, match=PRIVATE[0]):
        score_withheld_rows(data, partial)


def test_scoring_a_complete_file_is_a_no_op():
    data = {"per_question": [{"key": "A", "jsd": 0.1}], "scores": {"sps": 0.5}}
    before = json.dumps(data)
    assert score_withheld_rows(data, CANONICAL) == 0
    assert json.dumps(data) == before
