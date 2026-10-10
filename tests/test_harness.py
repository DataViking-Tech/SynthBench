"""Harness runs (althing claude-code: / codex: models) are named after the vendor model."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from synthbench.config_id import parse_provider, runnable_ids
from synthbench.leaderboard import display_provider_name, provider_framework
from synthbench.providers.althing import AlthingProvider, _split_harness
from synthbench.publish import _annotate_run_counts, _dedup_results


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("claude-code:haiku", ("claude-code", "haiku")),
        ("codex:gpt-6-luna", ("codex", "gpt-6-luna")),
        ("haiku", (None, "haiku")),
        ("claude-haiku-4-5", (None, "claude-haiku-4-5")),
    ],
)
def test_split_harness(model, expected):
    assert _split_harness(model) == expected


def test_provider_name_uses_vendor_and_served_model():
    prov = AlthingProvider(model="claude-code:haiku", elicitation="structured")
    assert prov.harness == "claude-code"
    # Before any response the alias stands in for the model.
    assert prov.name == "althing/anthropic/haiku harness=claude-code tpl=structured"
    prov._note_served_model(SimpleNamespace(model="claude-code:claude-haiku-5-5"))
    assert (
        prov.name
        == "althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured"
    )


def test_codex_provider_name():
    prov = AlthingProvider(model="codex:gpt-6-luna")
    prov._note_served_model(SimpleNamespace(model="codex:gpt-6-luna"))
    assert prov.name == "althing/openai/gpt-6-luna harness=codex"


def test_api_provider_name_unchanged():
    prov = AlthingProvider(model="haiku")
    assert prov.harness is None
    assert prov.name == "althing/haiku"


def test_harness_provider_parses_to_vendor_model():
    provider = "althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured"
    parsed = parse_provider(provider)
    assert parsed.base_provider == "anthropic"
    assert parsed.model == "claude-haiku-5-5"
    assert parsed.knobs["harness"] == "claude-code"
    assert runnable_ids(provider) == ("althing", "anthropic/claude-haiku-5-5")
    assert display_provider_name(provider) == "Althing (Haiku 5.5)"
    assert provider_framework(provider) == "product"


def test_harness_runs_keep_their_own_row():
    api = {
        "config": {
            "provider": "althing/anthropic/claude-haiku-5-5",
            "dataset": "opinionsqa",
            "n_evaluated": 100,
        }
    }
    cli = {
        "config": {
            "provider": "althing/anthropic/claude-haiku-5-5 harness=claude-code",
            "dataset": "opinionsqa",
            "n_evaluated": 100,
            "harness": "claude-code",
        }
    }
    assert len(_dedup_results([api, cli])) == 2

    entries = [
        {
            "model": "Althing (Haiku 5.5)",
            "framework": "product",
            "dataset": "opinionsqa",
        },
        {
            "model": "Althing (Haiku 5.5)",
            "framework": "product",
            "dataset": "opinionsqa",
            "harness": "claude-code",
        },
    ]
    _annotate_run_counts(entries, [api, cli, cli])
    assert [e["run_count"] for e in entries] == [1, 2]
