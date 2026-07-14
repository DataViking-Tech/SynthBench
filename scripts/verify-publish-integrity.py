#!/usr/bin/env python3
"""Fail-fast post-publish integrity check.

Run after `synthbench publish-data` and `synthbench publish-runs`, before the
Astro build. Guards against stale / path-polluted publish artifacts (sb-4zy)
by asserting every entry carries a `config_id` and every referenced config
has a matching rollup file on disk.

Also acts as the license-gating backstop: FAILS if any artifact under the
local publish output (run/, config/, question/) belongs to a dataset whose
redistribution policy is not ``full``. Gated-tier data (Pew ATP,
CC-BY-NC-SA sources, …) must only ever ship to the authenticated R2 origin;
its presence in the local static output means the build would publish
license-restricted per-question ``human_distribution`` data to a public,
unauthenticated origin.

Exits non-zero on first violation. Paths are CLI flags so this can be reused
from CI and local dev.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_json(path: Path) -> object:
    try:
        with path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"FAIL: {path} not found — publish step did not produce it")
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: {path} is not valid JSON: {e}")


def check_leaderboard(path: Path) -> set[str]:
    data = _load_json(path)
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        sys.exit(f"FAIL: {path} has no 'entries' list or it is empty")

    missing = [i for i, e in enumerate(entries) if not e.get("config_id")]
    if missing:
        sample = entries[missing[0]]
        sys.exit(
            f"FAIL: {len(missing)}/{len(entries)} leaderboard entries missing "
            f"config_id. First offender (idx {missing[0]}): "
            f"provider={sample.get('provider')!r} dataset={sample.get('dataset')!r}"
        )
    return {e["config_id"] for e in entries}


def check_runs_index(path: Path) -> tuple[set[str], dict[str, str]]:
    """Validate runs-index.json and return ``(config_ids, config_to_dataset)``.

    The dataset map lets the config-file check skip configs whose dataset
    rolls up to R2 instead of local disk under the gated tier (sb-sjs).
    """
    data = _load_json(path)
    if not isinstance(data, dict):
        sys.exit(f"FAIL: {path} is not a dict")

    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        sys.exit(f"FAIL: {path} has no 'runs' list or it is empty")

    missing = [i for i, r in enumerate(runs) if not r.get("config_id")]
    if missing:
        sample = runs[missing[0]]
        sys.exit(
            f"FAIL: {len(missing)}/{len(runs)} runs-index entries missing "
            f"config_id. First offender: run_id={sample.get('run_id')!r}"
        )

    declared = data.get("n_configs")
    config_ids = {r["config_id"] for r in runs}
    if isinstance(declared, int) and declared != len(config_ids):
        sys.exit(
            f"FAIL: {path} n_configs={declared} but runs reference "
            f"{len(config_ids)} distinct config_ids"
        )
    config_to_dataset = {
        r["config_id"]: r.get("dataset", "") for r in runs if r.get("config_id")
    }
    return config_ids, config_to_dataset


def _policy_by_name() -> dict[str, str] | None:
    """Map dataset base name → redistribution policy, or None if unresolvable.

    Prefers the installed synthbench package; falls back to importing from
    the repo's ``src/`` tree so the gating backstop still runs from a bare
    checkout. Returns None only when neither import path works.
    """
    try:
        from synthbench.datasets.policy import all_policies
    except ImportError:
        src = Path(__file__).resolve().parent.parent / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        try:
            from synthbench.datasets.policy import all_policies
        except ImportError:
            return None
    return {p.name: p.redistribution_policy for p in all_policies()}


def _gated_datasets() -> set[str]:
    """Names of datasets whose rollups ship to R2 instead of local disk.

    Falls back to an empty set if the synthbench package isn't importable
    from this script's runtime — in that case all configs are checked
    locally, which matches the legacy behavior.
    """
    policies = _policy_by_name()
    if policies is None:
        return set()
    return {name for name, policy in policies.items() if policy != "full"}


def _dataset_base(dataset_name: str) -> str:
    """Strip ``(filter)`` suffixes, mirroring synthbench.datasets.policy."""
    return dataset_name.split(" ", 1)[0].strip()


def check_no_gated_artifacts_local(
    run_dir: Path,
    config_dir: Path,
    question_dir: Path,
) -> None:
    """FAIL if any local publish artifact belongs to a non-``full`` dataset.

    This is the backstop against shipping license-restricted per-question
    data (``human_distribution``) from the public static origin: only
    ``full``-tier datasets may have per-run/per-config/per-question JSON in
    the local output. ``gated`` artifacts belong in R2 behind the Worker
    proxy; ``aggregates_only``/``citation_only`` artifacts must not exist
    anywhere.
    """
    policies = _policy_by_name()
    if policies is None:
        sys.exit(
            "FAIL: cannot resolve dataset redistribution policies (synthbench "
            "not importable) — the gated-artifact backstop cannot run. Install "
            "the package (`pip install -e .`) and re-run."
        )

    def _is_full(dataset_name: str) -> bool:
        # Unknown datasets default to aggregates_only in the policy module,
        # so treat anything unregistered as a violation too (conservative).
        return policies.get(_dataset_base(dataset_name)) == "full"

    violations: list[str] = []

    for artifact_dir in (run_dir, config_dir):
        if not artifact_dir.is_dir():
            continue
        for path in sorted(artifact_dir.glob("*.json")):
            try:
                with path.open() as f:
                    payload = json.load(f)
            except (OSError, json.JSONDecodeError):
                violations.append(f"{path} (unreadable/invalid JSON)")
                continue
            dataset = ""
            if isinstance(payload, dict):
                dataset = payload.get("dataset") or ""
            if not dataset or not _is_full(dataset):
                violations.append(f"{path} (dataset={dataset or 'unknown'!r})")

    if question_dir.is_dir():
        for sub in sorted(question_dir.iterdir()):
            if not sub.is_dir():
                continue
            if not _is_full(sub.name):
                n = len(list(sub.glob("*.json")))
                violations.append(f"{sub}/ ({n} file(s), dataset={sub.name!r})")

    if violations:
        sample = violations[:5]
        sys.exit(
            f"FAIL: {len(violations)} artifact(s) from non-'full' "
            "(gated/suppressed) datasets found in the LOCAL publish output. "
            "These must ship to the authenticated R2 origin, never the public "
            "static site — deploying them leaks license-restricted "
            "human_distribution data. Re-run publish with R2 credentials "
            f"configured. Examples: {sample}"
        )


def check_no_gated_distributions_committed(results_dir: Path) -> None:
    """FAIL if committed result files carry gated ``human_distribution`` data.

    Source-of-truth guard for issue #308: committed
    ``leaderboard-results/*.json`` files must be stripped of per-question
    ``human_distribution`` for every gated dataset (Pew ATP / CC-BY-NC-SA
    sources) — the publish pipeline rehydrates from the canonical registry
    instead. This backstop keeps the data from creeping back in via new
    submissions or manual edits.
    """
    if not results_dir.is_dir():
        return  # nothing committed to guard (e.g. bespoke invocations)

    policies = _policy_by_name()
    if policies is None:
        sys.exit(
            "FAIL: cannot resolve dataset redistribution policies (synthbench "
            "not importable) — the committed-results gating guard cannot run. "
            "Install the package (`pip install -e .`) and re-run."
        )

    violations: list[str] = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            with path.open() as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or data.get("benchmark") != "synthbench":
            continue
        dataset = (data.get("config") or {}).get("dataset") or ""
        if policies.get(_dataset_base(dataset)) != "gated":
            continue
        n = sum(
            1
            for q in data.get("per_question") or []
            if isinstance(q, dict) and "human_distribution" in q
        )
        if n:
            violations.append(f"{path} ({n} row(s), dataset={dataset!r})")

    if violations:
        sample = violations[:5]
        sys.exit(
            f"FAIL: {len(violations)} committed result file(s) in {results_dir} "
            "carry per-question human_distribution for a gated dataset. Run "
            "scripts/strip-gated-distributions.py and re-commit. "
            f"Examples: {sample}"
        )


def check_config_files(
    config_dir: Path,
    referenced: set[str],
    config_to_dataset: dict[str, str],
) -> None:
    if not config_dir.is_dir():
        sys.exit(f"FAIL: config rollup directory {config_dir} does not exist")

    gated = _gated_datasets()
    # Configs whose dataset is gated land in R2; their absence from the
    # local rollup directory is expected, not a regression.
    locally_required = {
        cid
        for cid in referenced
        if config_to_dataset.get(cid, "").split(" ", 1)[0] not in gated
    }

    on_disk = {p.stem for p in config_dir.glob("*.json")}
    missing_files = locally_required - on_disk
    if missing_files:
        sample = sorted(missing_files)[:3]
        sys.exit(
            f"FAIL: {len(missing_files)} config_ids referenced by runs-index "
            f"have no rollup file in {config_dir}. Examples: {sample}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--leaderboard",
        type=Path,
        default=Path("site/src/data/leaderboard.json"),
    )
    parser.add_argument(
        "--runs-index",
        type=Path,
        default=Path("site/public/data/runs-index.json"),
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("site/public/data/config"),
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=Path("site/public/data/run"),
    )
    parser.add_argument(
        "--question-dir",
        type=Path,
        default=Path("site/public/data/question"),
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("leaderboard-results"),
        help="Committed source result files to check for gated distributions.",
    )
    args = parser.parse_args()

    leaderboard_ids = check_leaderboard(args.leaderboard)
    runs_ids, config_to_dataset = check_runs_index(args.runs_index)
    check_config_files(args.config_dir, runs_ids, config_to_dataset)
    check_no_gated_artifacts_local(args.run_dir, args.config_dir, args.question_dir)
    check_no_gated_distributions_committed(args.results_dir)

    # Every config_id appearing on the leaderboard must also have a rollup
    # file — this is what the /run/[id] and /config/[id] routes hydrate from.
    orphan_on_leaderboard = leaderboard_ids - runs_ids
    if orphan_on_leaderboard:
        sample = sorted(orphan_on_leaderboard)[:3]
        sys.exit(
            f"FAIL: {len(orphan_on_leaderboard)} leaderboard config_ids are "
            f"not represented in runs-index. Examples: {sample}"
        )

    print(
        f"OK: leaderboard={len(leaderboard_ids)} configs, "
        f"runs-index={len(runs_ids)} configs, all config_ids present, "
        "no gated artifacts in the local publish output, no gated "
        "human_distribution in committed results."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
