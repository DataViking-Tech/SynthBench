#!/usr/bin/env python3
"""CI runner for `.github/workflows/validate-submission.yml` (refs sb-6gw).

Walks a NUL-delimited list of changed files (the same format ci.yml's
`validate-submissions` job uses), filters down to adapter-based
submissions, runs the checks in :mod:`synthbench.submission_pr`, writes a
sticky PR comment body to ``--comment-out``, and exits non-zero if any
required check failed.

Adapter submissions are detected by the presence of an ``adapter`` block
in ``run.json``; legacy provider-keyed submissions are silently skipped
(they are covered by ``ci.yml :: validate-submissions``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make ``src/`` importable when this script is invoked from a checkout
# without `pip install -e .` (the workflow installs the package, but the
# script should also work in `python scripts/validate-submission-pr.py`).
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from synthbench.submission_pr import (  # noqa: E402  (sys.path tweak above)
    CheckResult,
    check_adapter_registry,
    check_run_hash,
    is_adapter_submission,
    lint_submission_md,
    load_accepted_adapters,
    load_suite_manifest,
    render_sticky_comment,
)


def _read_changed_files(list_path: Path) -> list[Path]:
    """Read the NUL-delimited file list produced by ``git diff -z``."""
    if not list_path.exists():
        return []
    raw = list_path.read_bytes()
    if not raw:
        return []
    # Trailing NUL is normal from git diff -z; drop empty strings.
    return [Path(p.decode()) for p in raw.split(b"\x00") if p]


def _validate_one(
    json_path: Path,
    *,
    repo_root: Path,
    accepted: list[dict[str, str]],
) -> list[CheckResult]:
    """Run all checks for one adapter-submission JSON. The sibling
    ``submission.md``, if present, gets linted; absence is itself a fail."""
    try:
        run = json.loads(json_path.read_text())
    except json.JSONDecodeError as exc:
        return [
            CheckResult(
                name="parse",
                status="fail",
                summary=f"{json_path.name} is not valid JSON: {exc}",
            )
        ]
    if not isinstance(run, dict):
        return [
            CheckResult(
                name="parse",
                status="fail",
                summary=f"{json_path.name} top-level must be a JSON object",
            )
        ]

    results: list[CheckResult] = []
    results.append(check_adapter_registry(run, accepted))

    suite_name = run.get("suite") if isinstance(run.get("suite"), str) else "core"
    suite_manifest = load_suite_manifest(
        suite_name, repo_root / "src" / "synthbench" / "suites"
    )
    results.append(check_run_hash(run, suite_manifest))

    md_path = json_path.with_suffix(".md")
    if md_path.exists():
        results.append(lint_submission_md(md_path.read_text()))
    else:
        results.append(
            CheckResult(
                name="submission-md",
                status="fail",
                summary=f"missing companion `{md_path.name}` next to run.json",
                details=(
                    "  Adapter submissions must ship a markdown score card "
                    "alongside the JSON so the leaderboard can render a "
                    "human-readable summary.",
                ),
            )
        )
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--changed-files",
        type=Path,
        required=True,
        help="Path to NUL-delimited list of changed file paths (git diff -z).",
    )
    p.add_argument(
        "--comment-out",
        type=Path,
        required=True,
        help="Path to write the sticky PR comment markdown body.",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd).",
    )
    p.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="Override path to accepted_adapters.json (default: <root>/data/...).",
    )
    args = p.parse_args(argv)

    repo_root: Path = args.repo_root.resolve()
    registry_path: Path = (
        args.registry
        if args.registry
        else repo_root / "data" / "accepted_adapters.json"
    )

    try:
        accepted = load_accepted_adapters(registry_path)
    except ValueError as exc:
        # A broken registry file is a hard fail — better to block the PR
        # than silently accept everything.
        body = render_sticky_comment(
            submissions=[
                (
                    str(registry_path.relative_to(repo_root)),
                    [
                        CheckResult(
                            name="registry-load",
                            status="fail",
                            summary=f"{exc}",
                        )
                    ],
                )
            ]
        )
        args.comment_out.write_text(body)
        print(body)
        return 1

    changed = _read_changed_files(args.changed_files)
    submissions: list[tuple[str, list[CheckResult]]] = []
    for rel in changed:
        path = repo_root / rel if not rel.is_absolute() else rel
        if path.suffix != ".json":
            continue
        if "leaderboard-results" not in path.parts:
            continue
        if not path.exists():
            # File was deleted in the PR; nothing for this workflow to check.
            continue
        try:
            run = json.loads(path.read_text())
        except json.JSONDecodeError:
            # Defer the malformed-JSON message into the per-file check
            # output so the sticky comment is the only surface a reviewer
            # has to look at.
            submissions.append(
                (
                    str(rel),
                    [
                        CheckResult(
                            name="parse",
                            status="fail",
                            summary=f"{path.name} is not valid JSON",
                        )
                    ],
                )
            )
            continue
        if not isinstance(run, dict) or not is_adapter_submission(run):
            # Legacy provider-keyed submission — out of scope for this
            # workflow. Don't add to submissions list at all so the
            # sticky comment stays focused.
            continue
        submissions.append(
            (str(rel), _validate_one(path, repo_root=repo_root, accepted=accepted))
        )

    body = render_sticky_comment(submissions=submissions)
    args.comment_out.parent.mkdir(parents=True, exist_ok=True)
    args.comment_out.write_text(body)
    print(body)

    any_fail = any(r.failed for _, results in submissions for r in results)
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
