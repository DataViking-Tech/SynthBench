"""`synthbench submit-adapter` — vendor self-submission entry point (refs #256).

This is the **scaffold** implementation. The CLI surface, validation, and
artifact layout are pinned here so vendors can start integrating; the
heavy lifting (running the suite, computing the run hash, opening the
leaderboard PR) is stubbed and tracked in follow-up issues against #256.

Naming note: the existing `synthbench submit` posts a pre-computed
``result.json`` to the hosted API. The new adapter-driven flow is a
different verb shape (vendor brings code, harness drives evaluation), so
it lives under ``submit-adapter`` for this scaffold. Final naming is a
Wesley call — see the PR body for the open question.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import os
import sys
from pathlib import Path

import click

from synthbench.adapter import Adapter


# Follow-up issue numbers — replace once filed against #256.
TODO_EVAL_ISSUE = "TBD (eval pipeline)"
TODO_HASH_ISSUE = "TBD (run-hash content addressing)"
TODO_PR_ISSUE = "TBD (leaderboard PR generation)"

# Where vendors should open their submission PR. Pinned here so the stubbed
# output and the eventual real output agree on the URL shape.
LEADERBOARD_REPO_URL = "https://github.com/DataViking-Tech/SynthBench"
LEADERBOARD_PR_URL = f"{LEADERBOARD_REPO_URL}/compare/main...vendor:submission"


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
            "adapter module does not export a subclass of "
            "synthbench.adapter.Adapter"
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


def _write_placeholder_artifacts(
    output_dir: Path,
    *,
    adapter: Adapter,
    vendor: str,
    vendor_version: str,
    suite: str,
    api_env_var: str,
) -> tuple[Path, Path]:
    """Emit the stubbed ``submission.md`` + ``run.json`` for the scaffold path.

    Returns (submission_md_path, run_json_path). The real pipeline (refs
    #256 follow-ups) replaces both writes with content from an actual
    suite run.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stub = {
        "schema_version": "0.0.0-scaffold",
        "status": "scaffold",
        "adapter": {
            "name": adapter.name,
            "version": adapter.version,
            "vendor": vendor,
            "vendor_version": vendor_version,
        },
        "suite": suite,
        "api_env_var": api_env_var,
        "run_hash": None,
        "scores": None,
        "per_question": [],
        "todo": {
            "eval_pipeline": TODO_EVAL_ISSUE,
            "run_hash": TODO_HASH_ISSUE,
            "leaderboard_pr": TODO_PR_ISSUE,
        },
    }
    run_path = output_dir / "run.json"
    run_path.write_text(json.dumps(run_stub, indent=2) + "\n")

    md = f"""# SynthBench submission — {vendor} ({vendor_version})

> **Scaffold output.** This submission was produced by `synthbench
> submit-adapter` in scaffold mode (refs #256). The full evaluation
> pipeline is not yet wired up.

- **Adapter:** `{adapter.name}` v`{adapter.version}`
- **Suite:** `{suite}`
- **API env var:** `{api_env_var}` (presence checked; value never read by SynthBench)
- **Run hash:** _pending (see {TODO_HASH_ISSUE})_

## What to do with this file

Once the follow-up issues land, this file will contain the leaderboard
row + scoring summary. For now, you can open a PR to verify the path
shape works end-to-end:

```sh
# Stubbed verification — real curl command emitted by the full pipeline.
curl -fsSL {LEADERBOARD_REPO_URL}/raw/main/leaderboard/schema.json | head
```

PR target: {LEADERBOARD_PR_URL}

## TODOs tracked against #256

- [ ] Run the `{suite}` suite against the adapter ({TODO_EVAL_ISSUE})
- [ ] Compute content-addressed run hash ({TODO_HASH_ISSUE})
- [ ] Auto-generate leaderboard PR body ({TODO_PR_ISSUE})
"""
    md_path = output_dir / "submission.md"
    md_path.write_text(md)
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
    "--output-dir",
    type=click.Path(file_okay=False),
    default="./synthbench-submission/",
    show_default=True,
    help="Directory to write submission.md + run.json into.",
)
def submit_adapter(
    adapter_path: str,
    vendor: str,
    vendor_version: str,
    api_env_var: str,
    suite: str,
    output_dir: str,
) -> None:
    """Run the SynthBench suite against a vendor adapter and emit a submission.

    Scaffold-only: this command currently validates inputs and writes
    placeholder artifacts. The full evaluation + leaderboard PR pipeline
    is tracked in follow-ups to #256.

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

    # 4. Write placeholder artifacts. Real eval lands in a follow-up.
    out = Path(output_dir)
    md_path, run_path = _write_placeholder_artifacts(
        out,
        adapter=adapter,
        vendor=vendor,
        vendor_version=vendor_version,
        suite=suite,
        api_env_var=api_env_var,
    )

    click.echo(f"wrote scaffold submission to: {out}")
    click.echo(f"  - {md_path.name}")
    click.echo(f"  - {run_path.name}")
    click.echo("")
    click.echo("next steps (scaffold mode — full pipeline pending):")
    click.echo(f"  open a PR against: {LEADERBOARD_PR_URL}")
    click.echo(
        f"  verify with:        curl -fsSL "
        f"{LEADERBOARD_REPO_URL}/raw/main/leaderboard/schema.json"
    )
    click.echo("")
    click.echo(
        f"TODO (refs #256): eval={TODO_EVAL_ISSUE}, "
        f"hash={TODO_HASH_ISSUE}, pr={TODO_PR_ISSUE}"
    )
