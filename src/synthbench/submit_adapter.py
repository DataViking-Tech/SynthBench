"""`synthbench submit-adapter` — vendor self-submission entry point (refs #256).

Drives a vendor :class:`~synthbench.adapter.Adapter` through the core
OpinionsQA suite and emits a submission directory (``submission.md`` +
``run.json``) suitable for opening a PR against the leaderboard repo.

The CLI is the contract: exit 2 = bad inputs, exit 3 = missing API env
var, exit 0 = success. Vendor CI keys off these codes.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import inspect
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click

from synthbench import __version__
from synthbench.adapter import Adapter
from synthbench.leaderboard_pr import (
    EXIT_GH_MISSING,
    GhCommandFailed,
    GhUnavailable,
    open_leaderboard_pr,
)
from synthbench.providers.base import PersonaSpec, Provider, Response
from synthbench.run_hash import compute_run_hash
from synthbench.runner import BenchmarkRunner, BenchmarkResult
from synthbench.suites import SUITE_DIR
from synthbench.validation import CURRENT_SCHEMA_VERSION


# Where vendors should open their submission PR. Pinned here so the stubbed
# output and the eventual real output agree on the URL shape.
LEADERBOARD_REPO = "DataViking-Tech/SynthBench"
LEADERBOARD_REPO_URL = f"https://github.com/{LEADERBOARD_REPO}"
LEADERBOARD_PR_URL = f"{LEADERBOARD_REPO_URL}/compare/main...vendor:submission"

# Default samples per question. Matches BenchmarkRunner's default and the
# CLI `synthbench run` default; vendors can tune via --samples.
DEFAULT_SAMPLES_PER_QUESTION = 30

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_ADAPTER_SYSTEM_HINT = (
    "You are answering a survey. Select the single option that best reflects your view."
)

_ADAPTER_PROMPT_TEMPLATE = """\
{system_hint}

Question: {question}

Options:
{options_block}

Respond with ONLY the letter of your choice (e.g., "A"). Do not explain."""


def _build_prompt(question: str, options: list[str]) -> str:
    """Render the question + options block the adapter receives.

    Mirrors the prompt shape used by the in-tree providers (raw_openai,
    openrouter, ...) so the leaderboard CI's recompute path sees the same
    surface across providers and adapters.
    """
    options_block = "\n".join(f"({_LETTERS[i]}) {opt}" for i, opt in enumerate(options))
    return _ADAPTER_PROMPT_TEMPLATE.format(
        system_hint=_ADAPTER_SYSTEM_HINT,
        question=question,
        options_block=options_block,
    )


def _parse_option(text: str, options: list[str]) -> str | None:
    """Parse a raw adapter response into one of the declared options.

    Tries, in order:
      1. Leading letter (``A``, ``(A)``) → ``options[index]``.
      2. Leading number (``1``, ``1.``) → ``options[index-1]`` (1-indexed).
      3. Substring match against any option text (case-insensitive).

    Returns ``None`` if no rule fires. Callers surface this as a refusal
    so :class:`BenchmarkRunner` parse-failure metrics stay honest.

    Why a local parser and not the per-provider ``_parse_letter``: those
    are private duplicates that only handle the letter rule. The adapter
    surface is more permissive — vendors are told to "return whatever
    feels native" (a token, a phrase, a number) — so we widen the parser
    rather than narrow the contract.
    """
    if not text:
        return None
    stripped = text.strip()

    # 1. Letter form: A-Z (optionally parenthesized) at the start.
    m = re.match(r"^\(?([A-Za-z])\)?[\s\.\):,-]?", stripped)
    if m:
        letter = m.group(1).upper()
        idx = ord(letter) - ord("A")
        if 0 <= idx < len(options):
            return options[idx]

    # 2. Number form: 1-99 at the start (1-indexed).
    m = re.match(r"^\(?(\d{1,2})\)?[\s\.\):,-]?", stripped)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(options):
            return options[idx]

    # 3. Substring match against option text. Use the longest matching
    # option to avoid "yes" winning over "yes, definitely" when both are
    # offered as choices.
    text_lower = stripped.lower()
    best: tuple[int, str] | None = None
    for opt in options:
        opt_lower = opt.lower()
        if not opt_lower:
            continue
        if opt_lower in text_lower:
            if best is None or len(opt_lower) > best[0]:
                best = (len(opt_lower), opt)
    if best is not None:
        return best[1]

    return None


def _persona_to_dict(persona: PersonaSpec | None) -> dict[str, Any]:
    """Project a :class:`PersonaSpec` to the dict shape vendor adapters expect.

    The Adapter contract documents persona as
    ``{"age": "30-44", "party": "Democrat", ...}`` — i.e. a flat
    demographics dict — so we pass exactly that. The PersonaSpec's
    ``attribute``/``group``/``biography`` fields are runner-internal and
    intentionally not forwarded to the vendor.
    """
    if persona is None:
        return {}
    return dict(persona.demographics)


def _persona_id(persona: PersonaSpec | None) -> str:
    """Stable per-persona id for ``raw_responses`` rows used by run_hash.

    Unconditioned runs collapse to a single id so the hash is stable
    across samples (every sample shares the same persona "slot"). When
    demographic conditioning lands we'll switch this to
    ``f"{attribute}:{group}"``.
    """
    if persona is None or not persona.demographics:
        return "unconditioned"
    parts = sorted(f"{k}={v}" for k, v in persona.demographics.items())
    return ",".join(parts)


class AdapterProvider(Provider):
    """Bridge a vendor :class:`Adapter` into the :class:`Provider` surface.

    Drives ``Adapter.respond`` once per sample, parses the raw string into
    one of the declared options, and stashes the raw transcripts so the
    submit pipeline can rebuild the content-addressed ``run_hash``.

    Parse failures surface as ``Response(refusal=True)`` rather than a
    silently-coerced option, so the runner's refusal-calibration and
    parse-failure metrics reflect reality.
    """

    def __init__(self, adapter: Adapter) -> None:
        self._adapter = adapter
        # Raw transcripts collected during the run, indexed by
        # ``question_text`` (the runner doesn't pass question keys through
        # the Provider surface, so we map text -> key in a post-pass).
        self._raw_log: list[dict[str, str]] = []

    @property
    def name(self) -> str:
        return f"adapter/{self._adapter.name}@{self._adapter.version}"

    @property
    def prompt_template_source(self) -> str:
        return _ADAPTER_PROMPT_TEMPLATE.replace("{system_hint}", _ADAPTER_SYSTEM_HINT)

    async def respond(
        self,
        question: str,
        options: list[str],
        *,
        persona: PersonaSpec | None = None,
    ) -> Response:
        prompt = _build_prompt(question, options)
        persona_dict = _persona_to_dict(persona)
        context = {"question_text": question, "options": list(options)}

        try:
            raw = await self._adapter.respond(
                question=prompt, persona=persona_dict, context=context
            )
        except Exception as exc:  # noqa: BLE001 — surface vendor errors as refusals
            # The vendor's adapter raised mid-run. Don't tank the whole
            # suite — count this sample as a refusal so the runner's
            # refusal-calibration metric reflects the failure.
            self._raw_log.append(
                {
                    "question_text": question,
                    "persona_id": _persona_id(persona),
                    "raw_text": f"<adapter exception: {type(exc).__name__}: {exc}>",
                }
            )
            return Response(
                selected_option="",
                raw_text="",
                metadata={"adapter_error": f"{type(exc).__name__}: {exc}"},
                refusal=True,
            )

        raw_text = raw if isinstance(raw, str) else str(raw)
        self._raw_log.append(
            {
                "question_text": question,
                "persona_id": _persona_id(persona),
                "raw_text": raw_text,
            }
        )
        selected = _parse_option(raw_text, options)
        if selected is None:
            return Response(
                selected_option="",
                raw_text=raw_text,
                metadata={"parse_failure": True},
                refusal=True,
            )
        return Response(selected_option=selected, raw_text=raw_text)


def _load_adapter_module(adapter_path: str) -> object:
    """Import the adapter module either by dotted path or by filesystem path.

    Vendors will typically pass a filesystem path (their adapter lives in
    their own repo, not on ``PYTHONPATH``). Dotted paths are supported as a
    convenience for in-tree adapters and tests.

    Raises:
        click.ClickException: with a vendor-readable message on any import
        failure. Exit code 2 is enforced by the CLI layer.
    """
    p = Path(adapter_path)
    if p.exists() and p.suffix == ".py":
        spec = importlib.util.spec_from_file_location(
            f"_synthbench_adapter_{p.stem}", p
        )
        if spec is None or spec.loader is None:
            raise click.ClickException(
                f"could not load adapter from file: {adapter_path}"
            )
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — surface the vendor's error
            raise click.ClickException(
                f"adapter file imported with errors: {adapter_path}\n  {exc}"
            ) from exc
        return module

    # Fall back to dotted import.
    try:
        return importlib.import_module(adapter_path)
    except ImportError as exc:
        raise click.ClickException(
            f"adapter not importable: {adapter_path!r} "
            f"(tried filesystem path and dotted import). {exc}"
        ) from exc


def _find_adapter_class(module: object) -> type[Adapter]:
    """Locate the concrete Adapter subclass exported by the module.

    Convention: exactly one ``Adapter`` subclass per module. If a module
    exports multiple, the vendor should re-export the canonical one as
    ``Adapter`` (i.e. ``Adapter = MyVendorAdapter``).
    """
    candidates: list[type[Adapter]] = []
    for _name, obj in inspect.getmembers(module, inspect.isclass):
        if obj is Adapter:
            continue
        if issubclass(obj, Adapter):
            candidates.append(obj)

    if not candidates:
        raise click.ClickException(
            "adapter module does not export a subclass of synthbench.adapter.Adapter"
        )
    if len(candidates) > 1:
        # Prefer one literally named "Adapter" if the vendor re-exported.
        named = [c for c in candidates if c.__name__ == "Adapter"]
        if len(named) == 1:
            return named[0]
        raise click.ClickException(
            f"adapter module exports {len(candidates)} Adapter subclasses; "
            "re-export the canonical one as `Adapter = MyAdapter`"
        )
    return candidates[0]


def _load_suite_manifest(suite: str) -> dict:
    """Load ``suites/<suite>.json`` for run-hash input.

    Raises a CLI-friendly error if the suite file is missing so vendors
    pointing at a non-existent suite get the same exit-2 treatment as
    other bad inputs."""
    path = SUITE_DIR / f"{suite}.json"
    if not path.exists():
        raise click.ClickException(
            f"suite manifest not found: {path.name} "
            f"(looked in {SUITE_DIR}). known suites: "
            f"{sorted(p.stem for p in SUITE_DIR.glob('*.json'))}"
        )
    return json.loads(path.read_text())


def _build_dataset():
    """Construct the OpinionsQA dataset used by the adapter eval.

    Factored into its own helper so tests can monkeypatch a small in-memory
    fixture in place of the real CodaLab-backed loader (which would
    otherwise require a downloaded cache).
    """
    from synthbench.datasets.opinionsqa import OpinionsQADataset

    return OpinionsQADataset()


async def _run_eval(
    *,
    adapter: Adapter,
    suite_manifest: dict,
    samples_per_question: int,
    concurrency: int,
) -> tuple[BenchmarkResult, AdapterProvider]:
    """Drive ``adapter`` through the suite via :class:`BenchmarkRunner`.

    Returns the populated :class:`BenchmarkResult` plus the
    :class:`AdapterProvider` so the caller can recover the raw transcripts
    for run-hash computation.
    """
    provider = AdapterProvider(adapter)
    dataset = _build_dataset()
    runner = BenchmarkRunner(
        dataset=dataset,
        provider=provider,
        samples_per_question=samples_per_question,
        concurrency=concurrency,
    )
    result = await runner.run(question_keys=list(suite_manifest["keys"]))
    return result, provider


def _question_text_to_key(result: BenchmarkResult) -> dict[str, str]:
    """Map question text → question key from a populated benchmark result.

    Used to attribute the AdapterProvider's text-indexed raw log back to
    the suite key set so :func:`compute_run_hash` sees stable identifiers.
    """
    return {q.text: q.key for q in result.questions}


def _build_raw_responses_for_hash(
    provider: AdapterProvider, text_to_key: dict[str, str]
) -> list[dict[str, str]]:
    """Collect ``{question_key, persona_id, raw_text}`` rows for run_hash.

    Drops log entries whose question text didn't make it into the result
    (e.g. dataset keys absent from the suite filter) — those samples were
    never scored, so they shouldn't contribute to the content hash.
    """
    rows: list[dict[str, str]] = []
    for entry in provider._raw_log:
        key = text_to_key.get(entry["question_text"])
        if key is None:
            continue
        rows.append(
            {
                "question_key": key,
                "persona_id": entry["persona_id"],
                "raw_text": entry["raw_text"],
            }
        )
    return rows


def _build_scores(result: BenchmarkResult) -> dict[str, float]:
    """Flatten SPS components into a JSON-friendly scores dict."""
    scores: dict[str, float] = {
        "sps": round(result.sps, 6),
        "p_dist": round(result.p_dist, 6),
        "p_rank": round(result.p_rank, 6),
        "p_refuse": round(result.p_refuse, 6),
        "mean_jsd": round(result.mean_jsd, 6),
        "mean_kendall_tau": round(result.mean_kendall_tau, 6),
    }
    if result.p_sub is not None:
        scores["p_sub"] = round(result.p_sub, 6)
    if result.p_cond is not None:
        scores["p_cond"] = round(result.p_cond, 6)
    return scores


def _build_per_question(result: BenchmarkResult) -> list[dict[str, Any]]:
    """Project per-question results to the shape vendors / leaderboard CI parse."""
    rows: list[dict[str, Any]] = []
    for q in result.questions:
        row: dict[str, Any] = {
            "key": q.key,
            "options": q.options,
            "human_distribution": {
                k: round(v, 4) for k, v in q.human_distribution.items()
            },
            "model_distribution": {
                k: round(v, 4) for k, v in q.model_distribution.items()
            },
            "jsd": round(q.jsd, 6),
            "kendall_tau": round(q.kendall_tau, 6),
            "parity": round(q.parity, 6),
            "n_samples": q.n_samples,
            "n_parse_failures": q.n_parse_failures,
            "model_refusal_rate": round(q.model_refusal_rate, 6),
            "human_refusal_rate": round(q.human_refusal_rate, 6),
        }
        rows.append(row)
    return rows


def _build_run_payload(
    *,
    adapter: Adapter,
    vendor: str,
    vendor_version: str,
    suite: str,
    suite_manifest: dict,
    api_env_var: str,
    result: BenchmarkResult,
    provider: AdapterProvider,
) -> dict[str, Any]:
    """Assemble the full ``run.json`` payload from the populated result.

    The shape intentionally overlaps with :func:`synthbench.report.to_json`
    so the leaderboard PR template (rendered by
    :mod:`synthbench.leaderboard_pr`) and Tier-3 validators can parse
    either format without branching.
    """
    adapter_identity = {
        "name": adapter.name,
        "version": adapter.version,
        "vendor": vendor,
        "vendor_version": vendor_version,
    }
    text_to_key = _question_text_to_key(result)
    raw_responses = _build_raw_responses_for_hash(provider, text_to_key)

    run_hash = compute_run_hash(
        adapter=adapter_identity,
        suite=suite_manifest,
        persona_seeds=[],
        raw_responses=raw_responses,
    )

    return {
        "benchmark": "synthbench",
        "schema_version": CURRENT_SCHEMA_VERSION,
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "adapter": adapter_identity,
        "suite": suite,
        "api_env_var": api_env_var,
        "run_hash": run_hash,
        "config": {
            "dataset": result.dataset_name,
            "provider": result.provider_name,
            "samples_per_question": result.config.get("samples_per_question"),
            "n_evaluated": result.config.get("n_evaluated"),
            "question_set_hash": result.q_set_hash,
        },
        "reproducibility": {
            "model_revision_hash": result.config.get("model_revision_hash", ""),
            "prompt_template_hash": result.config.get("prompt_template_hash", ""),
            "framework_version": __version__,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
        "scores": _build_scores(result),
        "aggregate": {
            "mean_jsd": round(result.mean_jsd, 6),
            "median_jsd": round(result.median_jsd, 6),
            "mean_kendall_tau": round(result.mean_kendall_tau, 6),
            "composite_parity": round(result.composite_parity, 6),
            "n_questions": len(result.questions),
            "elapsed_seconds": round(result.elapsed_seconds, 2),
            "n_parse_failures": result.total_parse_failures,
        },
        "per_question": _build_per_question(result),
        "raw_responses": raw_responses,
    }


def _render_submission_md(payload: dict[str, Any]) -> str:
    """Render the human-readable submission summary written next to run.json."""
    adapter = payload["adapter"]
    scores = payload["scores"]
    score_lines = "\n".join(f"- **{k}:** {v}" for k, v in sorted(scores.items()))
    return f"""# SynthBench submission — {adapter["vendor"]} ({adapter["vendor_version"]})

- **Adapter:** `{adapter["name"]}` v`{adapter["version"]}`
- **Suite:** `{payload["suite"]}`
- **API env var:** `{payload["api_env_var"]}` (presence checked; value never read by SynthBench)
- **Run hash:** `{payload["run_hash"]}`
- **Questions evaluated:** {payload["aggregate"]["n_questions"]}
- **Samples per question:** {payload["config"]["samples_per_question"]}
- **Elapsed:** {payload["aggregate"]["elapsed_seconds"]}s

## Scores

{score_lines}

## Open the PR

```sh
curl -fsSL {LEADERBOARD_REPO_URL}/raw/main/leaderboard/schema.json | head
```

PR target: {LEADERBOARD_PR_URL}
"""


def _write_artifacts(output_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    """Persist ``submission.md`` + ``run.json`` from a populated payload."""
    output_dir.mkdir(parents=True, exist_ok=True)
    run_path = output_dir / "run.json"
    run_path.write_text(json.dumps(payload, indent=2) + "\n")
    md_path = output_dir / "submission.md"
    md_path.write_text(_render_submission_md(payload))
    return md_path, run_path


@click.command("submit-adapter")
@click.option(
    "--adapter",
    "adapter_path",
    required=True,
    help=(
        "Path or dotted import to a Python module exporting a subclass of "
        "synthbench.adapter.Adapter."
    ),
)
@click.option(
    "--vendor",
    required=True,
    help="Vendor name as it will appear on the leaderboard (e.g. 'acme-ai').",
)
@click.option(
    "--vendor-version",
    required=True,
    help="Vendor-supplied version string for this adapter (semver or date).",
)
@click.option(
    "--api-env-var",
    required=True,
    help=(
        "Name of the env var holding the vendor's API key "
        "(e.g. OPENROUTER_API_KEY). SynthBench checks presence only — the "
        "secret is never read by this process."
    ),
)
@click.option(
    "--suite",
    default="core",
    show_default=True,
    help="Suite to evaluate against. Only 'core' is supported today.",
)
@click.option(
    "--samples",
    type=int,
    default=DEFAULT_SAMPLES_PER_QUESTION,
    show_default=True,
    help="Samples per question.",
)
@click.option(
    "--concurrency",
    type=int,
    default=10,
    show_default=True,
    help="Concurrent adapter calls. Lower if the vendor API rate-limits.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False),
    default="./synthbench-submission/",
    show_default=True,
    help="Directory to write submission.md + run.json into.",
)
@click.option(
    "--open-pr",
    "open_pr",
    is_flag=True,
    default=False,
    help=(
        "After writing artifacts, use the `gh` CLI to fork the leaderboard "
        "repo into your namespace, push a submission branch, and open a "
        "PR. Requires `gh` on PATH (exit 4 if missing). SynthBench never "
        "reads your GitHub credentials — gh uses its own auth context."
    ),
)
@click.option(
    "--leaderboard-repo",
    default=LEADERBOARD_REPO,
    show_default=True,
    help=(
        "Upstream leaderboard repo in owner/name form. Override only when "
        "testing against a fork of the leaderboard itself."
    ),
)
def submit_adapter(
    adapter_path: str,
    vendor: str,
    vendor_version: str,
    api_env_var: str,
    suite: str,
    samples: int,
    concurrency: int,
    output_dir: str,
    open_pr: bool,
    leaderboard_repo: str,
) -> None:
    """Run the SynthBench suite against a vendor adapter and emit a submission.

    Example:

      synthbench submit-adapter \\
          --adapter ./my_adapter.py \\
          --vendor acme-ai \\
          --vendor-version 2026.05.14 \\
          --api-env-var ACME_API_KEY
    """
    # 1. Import the adapter module. Exit 2 == "your inputs are wrong".
    try:
        module = _load_adapter_module(adapter_path)
    except click.ClickException as exc:
        click.echo(f"error: {exc.message}", err=True)
        sys.exit(2)

    try:
        adapter_cls = _find_adapter_class(module)
    except click.ClickException as exc:
        click.echo(f"error: {exc.message}", err=True)
        sys.exit(2)

    # 2. Validate the API env var is set — presence only, never read.
    if os.environ.get(api_env_var) is None:
        click.echo(
            f"error: env var {api_env_var!r} is not set. "
            "SynthBench does not read the value, but it must be present so "
            "your adapter can authenticate when the eval runs.",
            err=True,
        )
        sys.exit(3)

    # 3. Instantiate the adapter. Vendor constructors should be no-arg;
    #    anything else is a contract violation.
    try:
        adapter = adapter_cls()
    except TypeError as exc:
        click.echo(
            f"error: adapter {adapter_cls.__name__} must be constructible "
            f"with no arguments. {exc}",
            err=True,
        )
        sys.exit(2)

    # 4. Load the suite manifest. A missing suite is a bad input, not a
    #    runtime failure → exit 2.
    try:
        suite_manifest = _load_suite_manifest(suite)
    except click.ClickException as exc:
        click.echo(f"error: {exc.message}", err=True)
        sys.exit(2)

    # 5. Drive the adapter through the suite.
    click.echo(f"running suite '{suite}' against {adapter.name}...")
    result, provider = asyncio.run(
        _run_eval(
            adapter=adapter,
            suite_manifest=suite_manifest,
            samples_per_question=samples,
            concurrency=concurrency,
        )
    )

    payload = _build_run_payload(
        adapter=adapter,
        vendor=vendor,
        vendor_version=vendor_version,
        suite=suite,
        suite_manifest=suite_manifest,
        api_env_var=api_env_var,
        result=result,
        provider=provider,
    )

    out = Path(output_dir)
    md_path, run_path = _write_artifacts(out, payload)

    click.echo(f"wrote submission to: {out}")
    click.echo(f"  - {md_path.name}")
    click.echo(f"  - {run_path.name}")
    click.echo(
        f"  SPS={payload['scores']['sps']} "
        f"P_dist={payload['scores']['p_dist']} "
        f"P_rank={payload['scores']['p_rank']}"
    )
    click.echo("")

    if open_pr:
        try:
            pr_url = open_leaderboard_pr(
                submission_dir=out,
                leaderboard_repo=leaderboard_repo,
            )
        except GhUnavailable as exc:
            click.echo(f"error: {exc}", err=True)
            sys.exit(EXIT_GH_MISSING)
        except GhCommandFailed as exc:
            click.echo(f"error: {exc}", err=True)
            sys.exit(1)
        click.echo(f"opened leaderboard PR: {pr_url}")
        return

    click.echo(f"next: open a PR against {LEADERBOARD_PR_URL}")
    click.echo(
        f"verify with: curl -fsSL "
        f"{LEADERBOARD_REPO_URL}/raw/main/leaderboard/schema.json"
    )
