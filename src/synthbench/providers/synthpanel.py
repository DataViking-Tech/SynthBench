"""SynthPanel full-pipeline provider.

Benchmarks the complete SynthPanel pipeline by shelling out to the
``synthpanel`` CLI.  For each respond() call, builds temporary persona
and instrument YAML files, runs ``synthpanel panel run``, and parses
the JSON output.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from synthbench.providers.base import Distribution, PersonaSpec, Provider, Response

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


def _yaml_escape(text: str) -> str:
    """Escape a string for embedding in double-quoted YAML."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _build_instrument_yaml(question: str, options: list[str]) -> str:
    """Build a single-question instrument YAML with natural presentation.

    Embeds the options in the question text so synthpanel sees a natural
    survey question rather than a forced-choice letter prompt.
    """
    opts_lines = "\\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    full_text = _yaml_escape(question) + "\\n\\n" + opts_lines
    opts_str = ", ".join(f'"{_yaml_escape(o)}"' for o in options)
    return (
        "version: 3\n"
        "rounds:\n"
        '  - name: "q"\n'
        "    questions:\n"
        f'    - text: "{full_text}"\n'
        f"      options: [{opts_str}]\n"
        "      type: multiple_choice\n"
    )


def _build_persona_yaml(persona: PersonaSpec | None, count: int = 1) -> str:
    """Build persona YAML with full conditioning context.

    When *count* > 1, replicates the persona to enable batch runs
    through a single synthpanel invocation.
    """
    if persona is None:
        block = (
            '  - name: "Survey Respondent"\n'
            '    occupation: "survey respondent"\n'
            '    background: "A general survey respondent."\n'
            '    personality_traits: "Responds thoughtfully and authentically."\n'
        )
        return "personas:\n" + block * count

    # Build descriptive name from demographics
    demo_parts = [f"{k}: {v}" for k, v in persona.demographics.items()]
    demo_summary = ", ".join(demo_parts)
    name_base = f"Respondent ({demo_summary})"

    # Build background from biography or demographics
    background = persona.biography or f"A person with {demo_summary.lower()}."

    entries: list[str] = []
    for i in range(count):
        suffix = f" {i + 1}" if count > 1 else ""
        lines = [f'  - name: "{_yaml_escape(name_base)}{suffix}"\n']
        for k, v in persona.demographics.items():
            lines.append(f'    {k.lower()}: "{_yaml_escape(v)}"\n')
        lines.append('    occupation: "survey respondent"\n')
        lines.append(f'    background: "{_yaml_escape(background)}"\n')
        lines.append(
            '    personality_traits: "Responds authentically based on their'
            ' demographic background."\n'
        )
        entries.append("".join(lines))

    return "personas:\n" + "".join(entries)


class SynthPanelProvider(Provider):
    """Benchmark the full SynthPanel pipeline via the CLI.

    Shells out to ``synthpanel panel run`` for each respond() call,
    using temporary instrument and persona YAML files.

    Supports synthpanel v0.6.0+ flags: --models, --temperature, --profile.
    """

    def __init__(
        self,
        model: str = "haiku",
        temperature: float | None = None,
        profile: str | None = None,
        synthpanel_path: str | None = None,
        **kwargs,
    ):
        if synthpanel_path:
            self._synthpanel_bin = synthpanel_path
        else:
            found = shutil.which("synthpanel")
            if found is None:
                raise ImportError(
                    "synthpanel is not installed or not on PATH. "
                    "Install synthpanel or pass synthpanel_path= explicitly."
                )
            self._synthpanel_bin = found
        self._model = model
        self._temperature = temperature
        self._profile = profile

    @property
    def name(self) -> str:
        parts = [f"synthpanel/{self._model}"]
        if self._temperature is not None:
            parts.append(f"t={self._temperature}")
        if self._profile:
            parts.append(f"profile={self._profile}")
        return " ".join(parts)

    def _build_cmd(self, inst_path: str, pers_path: str) -> list[str]:
        """Build the synthpanel CLI command (no --no-synthesis)."""
        cmd = [
            self._synthpanel_bin,
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
                pers_path,
                "--instrument",
                inst_path,
                "--models",
                f"{self._model}:1.0",
            ]
        )
        if self._temperature is not None:
            cmd.extend(["--temperature", str(self._temperature)])
        return cmd

    async def respond(
        self, question: str, options: list[str], *, persona: PersonaSpec | None = None
    ) -> Response:
        instrument_yaml = _build_instrument_yaml(question, options)
        persona_yaml = _build_persona_yaml(persona)

        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", prefix="sb_inst_", delete=False
            ) as inst_f,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", prefix="sb_pers_", delete=False
            ) as pers_f,
        ):
            inst_f.write(instrument_yaml)
            inst_path = inst_f.name
            pers_f.write(persona_yaml)
            pers_path = pers_f.name

        try:
            return await self._run_cli(inst_path, pers_path, options)
        finally:
            Path(inst_path).unlink(missing_ok=True)
            Path(pers_path).unlink(missing_ok=True)

    async def get_distribution(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
        n_samples: int | None = None,
    ) -> Distribution:
        """Batch N identical personas into one synthpanel invocation."""
        effective_samples = n_samples if n_samples is not None else 30
        instrument_yaml = _build_instrument_yaml(question, options)
        persona_yaml = _build_persona_yaml(persona, count=effective_samples)

        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", prefix="sb_inst_", delete=False
            ) as inst_f,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", prefix="sb_pers_", delete=False
            ) as pers_f,
        ):
            inst_f.write(instrument_yaml)
            inst_path = inst_f.name
            pers_f.write(persona_yaml)
            pers_path = pers_f.name

        try:
            return await self._run_batch(
                inst_path, pers_path, options, effective_samples
            )
        finally:
            Path(inst_path).unlink(missing_ok=True)
            Path(pers_path).unlink(missing_ok=True)

    async def _run_cli(
        self, inst_path: str, pers_path: str, options: list[str]
    ) -> Response:
        """Execute synthpanel CLI and parse the JSON output."""
        cmd = self._build_cmd(inst_path, pers_path)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        raw_stdout = stdout.decode().strip()
        raw_stderr = stderr.decode().strip()

        if proc.returncode != 0:
            return Response(
                selected_option=options[0],
                raw_text="",
                metadata={
                    "error": f"synthpanel exited {proc.returncode}: {raw_stderr}",
                    "model": self._model,
                },
            )

        try:
            data = json.loads(raw_stdout)
        except json.JSONDecodeError:
            return Response(
                selected_option=options[0],
                raw_text=raw_stdout,
                metadata={
                    "error": "failed to parse synthpanel JSON output",
                    "model": self._model,
                },
            )

        # Extract the panelist response text
        raw_text = ""
        try:
            raw_text = data["rounds"][0]["results"][0]["responses"][0]["response"]
        except (KeyError, IndexError):
            pass

        selected = _parse_letter(raw_text, options)
        if selected is None:
            selected = options[0]

        # Gather metadata from synthpanel output
        panelist_result = {}
        try:
            panelist_result = data["rounds"][0]["results"][0]
        except (KeyError, IndexError):
            pass

        metadata: dict = {
            "model": data.get("model", self._model),
            "total_cost": data.get("total_cost"),
            "panelist_cost": data.get("panelist_cost"),
            "total_usage": data.get("total_usage"),
            "panelist_usage": panelist_result.get("usage"),
        }
        if panelist_result.get("error"):
            metadata["panelist_error"] = panelist_result["error"]

        return Response(
            selected_option=selected,
            raw_text=raw_text,
            metadata=metadata,
        )

    async def _run_batch(
        self,
        inst_path: str,
        pers_path: str,
        options: list[str],
        n_samples: int,
    ) -> Distribution:
        """Run a batch of personas and build a distribution."""
        cmd = self._build_cmd(inst_path, pers_path)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        raw_stdout = stdout.decode().strip()

        if proc.returncode != 0:
            n = len(options)
            return Distribution(
                probabilities=[1.0 / n] * n,
                method="sampling",
                n_samples=0,
            )

        try:
            data = json.loads(raw_stdout)
        except json.JSONDecodeError:
            n = len(options)
            return Distribution(
                probabilities=[1.0 / n] * n,
                method="sampling",
                n_samples=0,
            )

        # Extract all panelist responses from the batch
        responses: list[str] = []
        refusals = 0
        try:
            results = data["rounds"][0]["results"]
            for result in results:
                for resp in result.get("responses", []):
                    raw_text = resp.get("response", "")
                    selected = _parse_letter(raw_text, options)
                    if selected is None:
                        refusals += 1
                    else:
                        responses.append(selected)
        except (KeyError, IndexError):
            pass

        total = len(responses) + refusals
        counts = Counter(responses)
        probs = [counts.get(opt, 0) / max(total, 1) for opt in options]
        refusal_prob = refusals / max(total, 1)

        return Distribution(
            probabilities=probs,
            refusal_probability=refusal_prob,
            method="sampling",
            n_samples=total,
        )

    async def close(self) -> None:
        pass
