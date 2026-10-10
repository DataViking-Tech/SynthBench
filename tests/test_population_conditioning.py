"""Tests for population conditioning via althing persona packs (--persona-pack)."""

from __future__ import annotations

import json
from collections import Counter

import click
import pytest

from synthbench.cli import _provider_kwargs
from synthbench.config_id import build_config_id
from synthbench.datasets.base import Dataset, Question
from synthbench.datasets.globalopinionqa import (
    GlobalOpinionQADataset,
    canonical_country,
)
from synthbench.providers.base import (
    Distribution,
    Provider,
    Response,
    pool_distributions,
)
from synthbench.runner import BenchmarkRunner, PopulationUnsupportedError


def _question(key="GOQA_1", population=None) -> Question:
    return Question(
        key=key,
        text="Do you approve?",
        options=["Approve", "Disapprove"],
        human_distribution={"Approve": 0.6, "Disapprove": 0.4},
        respondent_population=population,
    )


class _Dataset(Dataset):
    def __init__(self, questions):
        self._questions = questions

    @property
    def name(self) -> str:
        return "population-mock"

    def load(self, n=None):
        return list(self._questions)

    def info(self) -> dict:
        return {}


class _PackProvider(Provider):
    """Stands in for AlthingProvider(persona_pack=...)."""

    persona_pack = "global-respondents"

    def __init__(self):
        self.calls = []

    @property
    def name(self) -> str:
        return "althing/mock pack=global-respondents"

    async def respond(self, question, options, *, persona=None) -> Response:
        raise AssertionError("population runs must not use respond()")

    async def get_population_distribution(
        self, question, options, *, population, n_samples, seed
    ):
        self.calls.append((population, n_samples, seed))
        return Distribution(probabilities=[0.25, 0.75], n_samples=n_samples)


# ---------------------------------------------------------------------------
# GlobalOpinionQA populations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Brazil", "Brazil"),
        ("Brazil (Non-national sample)", "Brazil"),
        ("India (Old national sample)", "India"),
        ("S. Korea", "South Korea"),
        ("Britain", "Great Britain"),
        ("Czech Rep.", "Czechia"),
        ("Palest. ter.", "Palestinian territories"),
    ],
)
def test_canonical_country(label, expected):
    assert canonical_country(label) == expected


def _write_cache(tmp_path):
    data = {
        "dataset": "globalopinionqa",
        "questions": [
            {
                "key": "GOQA_1",
                "text": "Do you approve?",
                "options": ["Approve", "Disapprove"],
                "selections": {
                    "Brazil": [0.7, 0.3],
                    "Brazil (Non-national sample)": [0.6, 0.4],
                    "S. Korea": [0.2, 0.8],
                },
                "survey": "",
            }
        ],
    }
    (tmp_path / "questions.json").write_text(json.dumps(data), encoding="utf-8")


def test_globalopinionqa_population_keeps_repeats(tmp_path):
    _write_cache(tmp_path)
    (q,) = GlobalOpinionQADataset(data_dir=tmp_path).load()
    assert q.respondent_population == {"country": ["Brazil", "Brazil", "South Korea"]}


def test_globalopinionqa_population_with_country_filter(tmp_path):
    _write_cache(tmp_path)
    (q,) = GlobalOpinionQADataset(data_dir=tmp_path, country="S. Korea").load()
    assert q.respondent_population == {"country": ["South Korea"]}


def test_population_matches_global_respondents_pack():
    """Every canonical GlobalOpinionQA country must exist in althing's pack."""
    population = pytest.importorskip("althing.population")
    from synthbench.datasets.globalopinionqa import _COUNTRY_ALIASES

    countries = {
        p["country"] for p in population.load_pack_personas("global-respondents")
    }
    assert set(_COUNTRY_ALIASES.values()) <= countries


# ---------------------------------------------------------------------------
# Pooling
# ---------------------------------------------------------------------------


def test_pool_distributions_weights_by_sample_count():
    pooled = pool_distributions(
        [
            Distribution(
                probabilities=[1.0, 0.0],
                n_samples=20,
                metadata={"usage": {"input_tokens": 5}},
            ),
            Distribution(
                probabilities=[0.0, 0.5],
                n_samples=10,
                refusal_probability=0.5,
                n_parse_failures=2,
                metadata={
                    "usage": {"input_tokens": 7},
                    "raw_sample": {"raw_text": "B", "selected_option": "B"},
                },
            ),
        ],
        2,
    )
    assert pooled.n_samples == 30
    assert pooled.probabilities == pytest.approx([20 / 30, 5 / 30])
    assert pooled.refusal_probability == pytest.approx(5 / 30)
    assert pooled.n_parse_failures == 2
    assert pooled.metadata["usage"] == {"input_tokens": 12}
    assert pooled.metadata["raw_sample"]["raw_text"] == "B"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_runner_passes_population_and_stamps_pack():
    population = {"country": ["Brazil", "Japan"]}
    provider = _PackProvider()
    runner = BenchmarkRunner(
        dataset=_Dataset([_question(population=population)]),
        provider=provider,
        samples_per_question=12,
    )
    result = await runner.run()

    assert provider.calls == [(population, 12, "GOQA_1")]
    assert result.questions[0].model_distribution["Disapprove"] == pytest.approx(0.75)
    assert result.config["persona_pack"] == "global-respondents"
    assert result.provider_name.endswith("pack=global-respondents")


@pytest.mark.asyncio
async def test_runner_rejects_dataset_without_population():
    runner = BenchmarkRunner(
        dataset=_Dataset([_question()]),
        provider=_PackProvider(),
        samples_per_question=3,
    )
    with pytest.raises(PopulationUnsupportedError, match="population-mock"):
        await runner.run()


def test_pack_runs_get_their_own_config_id():
    base, _ = build_config_id(
        "althing/claude-code:haiku tpl=structured", dataset="globalopinionqa"
    )
    pack, _ = build_config_id(
        "althing/claude-code:haiku tpl=structured pack=global-respondents",
        dataset="globalopinionqa",
    )
    assert base != pack


def test_persona_pack_rejected_for_non_althing_providers():
    with pytest.raises(click.UsageError, match="althing"):
        _provider_kwargs(
            "raw-anthropic", model="haiku", persona_pack="global-respondents"
        )
    assert _provider_kwargs(
        "althing", model="haiku", persona_pack="global-respondents"
    )["persona_pack"] == ("global-respondents")


# ---------------------------------------------------------------------------
# AlthingProvider.get_population_distribution (needs althing.population)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_althing_provider_samples_each_allocated_persona():
    pytest.importorskip("althing.population")
    from synthbench.providers.althing import AlthingProvider

    prov = AlthingProvider(model="haiku", persona_pack="global-respondents")
    seen: Counter = Counter()

    class _Client:
        def send(self, request):
            country = request.system.split("Country: ")[1].split(".")[0]
            seen[country] += 1
            from althing.llm.models import CompletionResponse, TextBlock

            answer = "A" if country == "Japan" else "B"
            return CompletionResponse(
                id="x", model="haiku", content=[TextBlock(text=answer)]
            )

    prov._client = _Client()
    dist = await prov.get_population_distribution(
        "Do you approve?",
        ["Approve", "Disapprove"],
        population={"country": ["Brazil", "Brazil", "Japan"]},
        n_samples=30,
        seed="GOQA_1",
    )
    assert seen == {"Brazil": 20, "Japan": 10}
    assert dist.n_samples == 30
    assert dist.probabilities == pytest.approx([10 / 30, 20 / 30])
    assert "pack=global-respondents" in prov.name
