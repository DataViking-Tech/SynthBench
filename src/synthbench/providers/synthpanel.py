"""SynthPanel full-pipeline provider.

Shells out to the ``synthpanel`` CLI to benchmark the complete pipeline:
persona conditioning, survey instruments, response extraction, synthesis.

Supports synthpanel v0.6.0+ flags: --models, --temperature, --profile.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

from synthbench.providers.base import PersonaSpec, Provider, Response

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _parse_letter(text: str, options: list[str]) -> str | None:
    """Extract the selected option from response text."""
    text = text.strip()

    match = re.match(r"^\(?([A-Z])\)?", text.upper())
    if match:
        idx = ord(match.group(1)) - ord("A")
        if 0 <= idx < len(options):
            return options[idx]

    text_lower = text.lower()
    for opt in options:
        if opt.lower() in text_lower:
            return opt

    return None


def _build_instrument_yaml(question: str, options: list[str]) -> str:
    """Build a minimal v3 instrument YAML for a single question."""
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    instrument = {
        "instrument": {
            "version": 3,
            "rounds": [
                {
                    "name": "benchmark",
                    "questions": [
                        {
                            "text": (
                                f"{question}\n\n{options_block}\n\n"
                                "Respond with ONLY the letter of your choice "
                                '(e.g., "A"). Do not explain.'
                            ),
                        }
                    ],
                    "route_when": [{"else": "__end__"}],
                }
            ],
        }
    }
    return yaml.dump(instrument, default_flow_style=False)


def _build_persona_yaml(persona: PersonaSpec | None) -> str:
    """Build a persona YAML from PersonaSpec or a generic respondent."""
    if persona and persona.demographics:
        demo = persona.demographics
        name = f"Respondent ({', '.join(f'{k}={v}' for k, v in demo.items())})"
        persona_dict = {"name": name, **demo}
        if persona.biography:
            persona_dict["background"] = persona.biography
    else:
        persona_dict = {"name": "Survey Respondent", "background": "Average adult."}

    return yaml.dump({"personas": [persona_dict]}, default_flow_style=False)


class SynthPanelProvider(Provider):
    """Benchmark the full SynthPanel pipeline via CLI.

    Supports synthpanel v0.6.0+ with --models, --temperature, --profile.
    """

    def __init__(
        self,
        model: str = "haiku",
        temperature: float | None = None,
        profile: str | None = None,
        synthpanel_path: str | None = None,
        **kwargs,
    ):
        self._model = model
        self._temperature = temperature
        self._profile = profile
        self._synthpanel = synthpanel_path or shutil.which("synthpanel")

        if self._synthpanel is None:
            raise ImportError(
                "synthpanel CLI not found on PATH. Install with: pip install synthpanel"
            )

    @property
    def name(self) -> str:
        parts = [f"synthpanel/{self._model}"]
        if self._temperature is not None:
            parts.append(f"t={self._temperature}")
        if self._profile:
            parts.append(f"profile={self._profile}")
        return " ".join(parts)

    async def respond(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
    ) -> Response:
        with tempfile.TemporaryDirectory() as tmpdir:
            inst_path = Path(tmpdir) / "instrument.yaml"
            pers_path = Path(tmpdir) / "personas.yaml"

            inst_path.write_text(_build_instrument_yaml(question, options))
            pers_path.write_text(_build_persona_yaml(persona))

            cmd = [
                self._synthpanel,
                "--output-format",
                "json",
            ]

            if self._profile:
                cmd.extend(["--profile", self._profile])

            cmd.extend(
                [
                    "panel",
                    "run",
                    "--personas",
                    str(pers_path),
                    "--instrument",
                    str(inst_path),
                    "--models",
                    f"{self._model}:1.0",
                    "--no-synthesis",
                ]
            )

            if self._temperature is not None:
                cmd.extend(["--temperature", str(self._temperature)])

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode().strip()
                raise RuntimeError(
                    f"synthpanel exited with code {proc.returncode}: {err}"
                )

            raw_text = stdout.decode().strip()

            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                return Response(
                    selected_option=options[0],
                    raw_text=raw_text,
                    metadata={"error": "json_parse_failure"},
                )

            # Extract the panelist response from the nested structure
            answer_text = ""
            metadata = data.get("metadata", {})

            rounds = data.get("rounds", [])
            if rounds:
                results = rounds[0].get("results", [])
                if results:
                    responses = results[0].get("responses", [])
                    if responses:
                        answer_text = responses[0].get("response", "")

            selected = _parse_letter(answer_text, options)
            if selected is None:
                selected = options[0]

            return Response(
                selected_option=selected,
                raw_text=answer_text,
                metadata=metadata,
            )

    async def close(self) -> None:
        pass
