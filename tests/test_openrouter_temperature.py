"""An omitted decoding knob stays omitted on the wire and in CLI metadata."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from click.testing import CliRunner

openai = pytest.importorskip("openai")

from synthbench.cli import main  # noqa: E402
from synthbench.providers.openrouter import OpenRouterProvider  # noqa: E402


@pytest.fixture
def completions(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="A"), finish_reason="stop"
                )
            ],
            usage=None,
        )
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
        close=AsyncMock(),
    )
    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **_kwargs: client)
    return create


@pytest.mark.asyncio
@pytest.mark.parametrize("temperature", [None, 0.0, 0.85, 1.0])
async def test_request_preserves_explicit_temperature_only(completions, temperature):
    kwargs = {} if temperature is None else {"temperature": temperature}
    provider = OpenRouterProvider(model="anthropic/claude-sonnet-5.5", **kwargs)

    response = await provider.respond("Favor or oppose?", ["Favor", "Oppose"])

    assert response.selected_option == "Favor"
    sent = completions.call_args.kwargs
    if temperature is None:
        assert "temperature" not in sent
    else:
        assert sent["temperature"] == temperature


@pytest.mark.parametrize("temperature", [None, 0.0, 0.85])
def test_cli_temperature_metadata_matches_request(
    completions, monkeypatch, mock_dataset, tmp_path, temperature
):
    from synthbench.datasets import DATASETS

    monkeypatch.setitem(DATASETS, "mock", type(mock_dataset))
    args = [
        "run",
        "--provider",
        "openrouter",
        "--model",
        "anthropic/claude-sonnet-5.5",
        "--dataset",
        "mock",
        "--n",
        "1",
        "--samples",
        "1",
        "--output",
        str(tmp_path),
    ]
    if temperature is not None:
        args += ["--temperature", str(temperature)]

    result = CliRunner().invoke(main, args)

    assert result.exit_code == 0, result.output
    artifact = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert artifact["config"].get("temperature") == temperature
    sent = completions.call_args.kwargs
    if temperature is None:
        assert "temperature" not in sent
    else:
        assert sent["temperature"] == temperature
