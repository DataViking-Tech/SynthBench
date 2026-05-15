"""Submission-PR validation checks (refs sb-6gw / GH#256).

Pure functions used by ``scripts/validate-submission-pr.py`` and the
``.github/workflows/validate-submission.yml`` workflow. Each check returns
a :class:`CheckResult` so the runner can aggregate them into a sticky PR
comment without re-running anything.

What this module is responsible for (the *adapter* submission flow only —
legacy ``provider``-keyed submissions stay on the existing
``validate-submissions`` job in ``ci.yml``):

1. Adapter identity is in ``data/accepted_adapters.json``.
2. Re-derived run hash matches the ``run_hash`` field in ``run.json``
   (skipped gracefully until ``synthbench.run_hash`` lands — see sb-1ix).
3. ``submission.md`` carries the required headings + scores table shape.

Diff-style mismatch messages name *which* input drifted so a reviewer can
tell adapter-identity drift apart from raw-response drift.
"""

from __future__ import annotations

import dataclasses
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, Optional


CheckStatus = str  # "pass" | "fail" | "skip"


@dataclasses.dataclass(frozen=True)
class CheckResult:
    """One check's outcome. ``status`` drives the runner's exit code:
    any ``fail`` → non-zero. ``skip`` is non-fatal but surfaced in the
    sticky comment so reviewers can see why a check did not run."""

    name: str
    status: CheckStatus
    summary: str
    details: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def failed(self) -> bool:
        return self.status == "fail"


# ---------------------------------------------------------------------------
# Adapter identity registry
# ---------------------------------------------------------------------------


def load_accepted_adapters(registry_path: Path) -> list[dict[str, str]]:
    """Return the list of accepted ``{name, version}`` entries.

    Missing file is treated as an empty registry rather than an error: the
    failure mode is a useful one (no adapters accepted yet → all
    submissions fail the check with a clear message).
    """
    if not registry_path.exists():
        return []
    raw = json.loads(registry_path.read_text())
    adapters = raw.get("adapters", [])
    if not isinstance(adapters, list):
        raise ValueError(
            f"{registry_path}: 'adapters' must be a list, got {type(adapters).__name__}"
        )
    out: list[dict[str, str]] = []
    for i, entry in enumerate(adapters):
        if not isinstance(entry, Mapping):
            raise ValueError(f"{registry_path}: adapters[{i}] must be an object")
        name = entry.get("name")
        version = entry.get("version")
        if not isinstance(name, str) or not isinstance(version, str):
            raise ValueError(
                f"{registry_path}: adapters[{i}] must have string 'name' and 'version'"
            )
        out.append({"name": name, "version": version})
    return out


def check_adapter_registry(
    run: Mapping[str, Any], accepted: Iterable[Mapping[str, str]]
) -> CheckResult:
    """Verify the submission's adapter identity is in the registry."""
    adapter = run.get("adapter")
    if not isinstance(adapter, Mapping):
        return CheckResult(
            name="adapter-registry",
            status="fail",
            summary="run.json has no `adapter` block",
            details=(
                "Submissions produced by `synthbench submit-adapter` must "
                "carry an `adapter` object with at least `name` and `version`. "
                "If this is a legacy provider-keyed submission, this workflow "
                "should have skipped it — file a bug.",
            ),
        )

    name = adapter.get("name")
    version = adapter.get("version")
    if not isinstance(name, str) or not isinstance(version, str):
        return CheckResult(
            name="adapter-registry",
            status="fail",
            summary="`adapter.name` and `adapter.version` must be strings",
            details=(
                f"  got name={name!r} version={version!r}",
                "  Vendors: re-run `synthbench submit-adapter` against the "
                "latest scaffold.",
            ),
        )

    for entry in accepted:
        if entry["name"] == name and entry["version"] == version:
            return CheckResult(
                name="adapter-registry",
                status="pass",
                summary=f"adapter `{name}` v`{version}` is in the registry",
            )

    return CheckResult(
        name="adapter-registry",
        status="fail",
        summary=f"adapter `{name}` v`{version}` is NOT in `data/accepted_adapters.json`",
        details=(
            "New adapters require explicit maintainer approval. Open a "
            '**separate** PR adding `{"name": '
            + json.dumps(name)
            + ', "version": '
            + json.dumps(version)
            + "}` to `data/accepted_adapters.json`, wait for it to merge, "
            "then re-push this submission.",
            "Bundling a registry change with a submission change in one PR "
            "defeats the gate — reviewers cannot tell which approval is for "
            "which artifact.",
        ),
    )


# ---------------------------------------------------------------------------
# Run-hash re-derivation
# ---------------------------------------------------------------------------


# Public so the runner can render the same skip reason in the sticky
# comment without re-importing.
RUN_HASH_SKIP_REASON = (
    "`synthbench.run_hash` not present yet — check will activate once "
    "[sb-1ix](../../issues?q=sb-1ix) lands the content-addressed run-hash "
    "module."
)


def _import_run_hash() -> Optional[Any]:
    """Return the ``derive_run_hash`` callable from ``synthbench.run_hash``,
    or ``None`` if the module/function is not yet implemented (sb-1ix)."""
    try:
        module = __import__("synthbench.run_hash", fromlist=["derive_run_hash"])
    except ImportError:
        return None
    return getattr(module, "derive_run_hash", None)


def check_run_hash(
    run: Mapping[str, Any],
    suite_manifest: Optional[Mapping[str, Any]],
    *,
    derive: Optional[Any] = None,
) -> CheckResult:
    """Re-derive the run hash and compare it to ``run["run_hash"]``.

    ``derive`` is injectable for tests. In production it is resolved via
    :func:`_import_run_hash`, so the check skips gracefully while sb-1ix
    is in flight.
    """
    derive_fn = derive if derive is not None else _import_run_hash()
    if derive_fn is None:
        return CheckResult(
            name="run-hash",
            status="skip",
            summary="run-hash re-derivation skipped",
            details=(RUN_HASH_SKIP_REASON,),
        )

    declared = run.get("run_hash")
    if declared is None:
        # The scaffold writes null; not a fail until the eval pipeline
        # actually populates it. Skip with an explicit note so reviewers
        # see *why* nothing was checked.
        return CheckResult(
            name="run-hash",
            status="skip",
            summary="`run.json` has `run_hash: null`",
            details=(
                "This is the scaffold default. Once the eval pipeline "
                "(sb-bas) and run-hash module (sb-1ix) both land, real "
                "submissions will carry a hex string here and this check "
                "will fail-closed.",
            ),
        )
    if not isinstance(declared, str):
        return CheckResult(
            name="run-hash",
            status="fail",
            summary=f"`run_hash` must be a string, got {type(declared).__name__}",
        )

    adapter = run.get("adapter") or {}
    raw_responses = run.get("raw_responses") or []
    persona_seeds = run.get("persona_seeds")
    try:
        recomputed = derive_fn(
            adapter=adapter,
            suite_manifest=suite_manifest or {},
            persona_seeds=persona_seeds,
            raw_responses=raw_responses,
        )
    except Exception as exc:  # noqa: BLE001 — surface vendor-facing error
        return CheckResult(
            name="run-hash",
            status="fail",
            summary=f"failed to re-derive run hash: {exc}",
        )

    if recomputed == declared:
        return CheckResult(
            name="run-hash",
            status="pass",
            summary=f"run hash re-derives to `{declared[:12]}…`",
        )

    # Mismatch: try to pinpoint which input drifted. The sb-1ix module is
    # expected to expose a ``components()`` helper that hashes each input
    # group independently; if it's not there, we fall back to a generic
    # diff message rather than guessing.
    details = [
        f"  declared:    {declared}",
        f"  re-derived:  {recomputed}",
    ]
    components = getattr(derive_fn, "components", None)
    if components is None:
        try:
            run_hash_mod = __import__("synthbench.run_hash", fromlist=["components"])
        except ImportError:
            run_hash_mod = None
        if run_hash_mod is not None:
            components = getattr(run_hash_mod, "components", None)
    if callable(components):
        try:
            recomputed_parts = components(
                adapter=adapter,
                suite_manifest=suite_manifest or {},
                persona_seeds=persona_seeds,
                raw_responses=raw_responses,
            )
            declared_parts = run.get("run_hash_components") or {}
            drifted: list[str] = []
            for key, value in recomputed_parts.items():
                if declared_parts.get(key) != value:
                    drifted.append(key)
            if drifted:
                details.append("  inputs that drifted: " + ", ".join(sorted(drifted)))
        except Exception as exc:  # noqa: BLE001
            details.append(f"  (component diff unavailable: {exc})")

    return CheckResult(
        name="run-hash",
        status="fail",
        summary="run-hash mismatch — submission inputs do not match declared hash",
        details=tuple(details),
    )


# ---------------------------------------------------------------------------
# submission.md format lint
# ---------------------------------------------------------------------------


REQUIRED_H1_PREFIX = "# SynthBench"
REQUIRED_SECTIONS = ("## SynthBench Parity Score", "## Raw Metrics")
# Scores table is recognized by these column headers (in order). Matches the
# canonical format produced by `synthbench publish-runs` and the
# legacy report.py renderer.
SCORES_TABLE_HEADERS = ("Metric", "Score")


def _find_scores_table(lines: list[str]) -> Optional[tuple[int, int]]:
    """Return (header_line_idx, separator_line_idx) for the first table
    whose first two pipe-delimited columns match :data:`SCORES_TABLE_HEADERS`,
    or ``None`` if no such table exists."""
    for i in range(len(lines) - 1):
        header = lines[i].strip()
        sep = lines[i + 1].strip()
        if not header.startswith("|") or not sep.startswith("|"):
            continue
        # Separator row: each cell must be dashes/colons/spaces only.
        sep_cells = [c.strip() for c in sep.strip("|").split("|")]
        if not all(re.fullmatch(r":?-+:?", c) for c in sep_cells if c):
            continue
        header_cells = [c.strip() for c in header.strip("|").split("|")]
        if (
            len(header_cells) >= 2
            and header_cells[0] == SCORES_TABLE_HEADERS[0]
            and header_cells[1] == SCORES_TABLE_HEADERS[1]
        ):
            return (i, i + 1)
    return None


def lint_submission_md(md_text: str) -> CheckResult:
    """Lint the format of an adapter submission's ``submission.md``."""
    issues: list[str] = []
    lines = md_text.splitlines()
    stripped = [ln.strip() for ln in lines]

    h1s = [ln for ln in stripped if ln.startswith("# ")]
    if not h1s:
        issues.append("missing top-level `# ` heading")
    elif not h1s[0].startswith(REQUIRED_H1_PREFIX):
        issues.append(f"H1 must start with `{REQUIRED_H1_PREFIX}` (got `{h1s[0]}`)")

    for section in REQUIRED_SECTIONS:
        if not any(ln.startswith(section) for ln in stripped):
            issues.append(f"missing required section `{section}`")

    if _find_scores_table(lines) is None:
        issues.append(
            "missing scores table — expected a markdown table whose first "
            f"two column headers are `{SCORES_TABLE_HEADERS[0]}` and "
            f"`{SCORES_TABLE_HEADERS[1]}`"
        )

    if issues:
        return CheckResult(
            name="submission-md",
            status="fail",
            summary=f"{len(issues)} format issue(s) in submission.md",
            details=tuple(f"  - {msg}" for msg in issues),
        )
    return CheckResult(
        name="submission-md",
        status="pass",
        summary="submission.md format OK",
    )


# ---------------------------------------------------------------------------
# Submission detection
# ---------------------------------------------------------------------------


def is_adapter_submission(run: Mapping[str, Any]) -> bool:
    """True iff ``run.json`` looks like output of ``synthbench submit-adapter``.

    Detection key is the presence of an ``adapter`` block — legacy
    ``provider``-keyed submissions don't carry one, so they bypass this
    workflow and go through ``ci.yml::validate-submissions`` instead.
    """
    return isinstance(run.get("adapter"), Mapping)


def load_suite_manifest(suite: str, suites_dir: Path) -> Optional[dict[str, Any]]:
    """Load ``suites/<suite>.json`` for run-hash re-derivation.

    Returns ``None`` if the manifest is missing — the run-hash check then
    fails with a clear message rather than crashing.
    """
    candidate = suites_dir / f"{suite}.json"
    if not candidate.exists():
        return None
    return json.loads(candidate.read_text())


# ---------------------------------------------------------------------------
# Sticky-comment rendering
# ---------------------------------------------------------------------------


STICKY_MARKER = "<!-- synthbench: validate-submission v1 -->"


def render_sticky_comment(
    *,
    submissions: list[tuple[str, list[CheckResult]]],
    pr_number: Optional[int] = None,
) -> str:
    """Render the per-submission check matrix as the sticky PR comment body.

    The marker on the first line lets the workflow's sticky-comment
    action find and overwrite the previous comment instead of stacking.
    """
    out = [STICKY_MARKER, "", "## SynthBench submission validation", ""]
    if not submissions:
        out.append(
            "_No adapter-based submissions detected in this PR_ — legacy "
            "provider-keyed submissions are validated by the `ci.yml :: "
            "validate-submissions` job."
        )
        return "\n".join(out) + "\n"

    any_fail = any(r.failed for _, results in submissions for r in results)
    status_line = (
        "❌ One or more checks failed." if any_fail else "✅ All checks passed."
    )
    out.append(status_line)
    out.append("")

    for path, results in submissions:
        out.append(f"### `{path}`")
        out.append("")
        out.append("| Check | Result | Summary |")
        out.append("|-------|--------|---------|")
        for r in results:
            emoji = {"pass": "✅", "fail": "❌", "skip": "⏭️"}[r.status]
            summary = r.summary.replace("|", "\\|")
            out.append(f"| `{r.name}` | {emoji} {r.status} | {summary} |")
        out.append("")
        for r in results:
            if r.details:
                out.append(f"<details><summary>`{r.name}` details</summary>")
                out.append("")
                out.append("```")
                out.extend(r.details)
                out.append("```")
                out.append("")
                out.append("</details>")
                out.append("")

    return "\n".join(out) + "\n"
